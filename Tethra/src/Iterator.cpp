#include "Iterator.h"
#include <Eigen/Dense>
#include <cmath>
#include <fstream>
#include <iostream>
#include <spdlog/spdlog.h>
#include <Eigen/Sparse>


using namespace std;
using namespace Eigen;

Iterator::Iterator(VectorXd &arr, VectorXd &brr, int a, double b)
    : Yold(arr), Ynew(brr), times(a), Error(b) {
  cout << endl;
  cout << "Now the Maximum Iteration TIMES is " << times << endl;
  cout << "Now the Maximum Allowable Iteration ERROR is " << Error << endl
       << endl;
}

Iterator::~Iterator() {}

void Iterator::begin(int k) {
  SPDLOG_DEBUG("Begin iteration for index {}", k);

  Load load(Yold, Ynew);
  fx = load.LF(k);
  jac = load.LJ(k);

  for (int i = 0; i < times; i++) {
    cout << "Iteration " << i + 1 << " times; " << endl;

    //-> Searching Direction Funding//
    VectorXd p;
    bool solved = false;

    // Try different solvers in order of preference
    Eigen::SparseLU<SparseMatrix<double>> sparsesolver;  //Calculating the Search Direction(Sparse::SparseLU)
    sparsesolver.compute(jac);

    if(sparsesolver.info() == Success) {
      p = sparsesolver.solve(-fx);
      solved = true;
    } else {
        cout << "SparseLU decomposition failed, trying BiCGSTAB solver." << endl;
        
        Eigen::BiCGSTAB<SparseMatrix<double>> bicgstabSolver; //Calculating the Search Direction(Sparse::BiCGSTAB)
        bicgstabSolver.setMaxIterations(200);
        bicgstabSolver.setTolerance(1e-06);

        bicgstabSolver.compute(jac);
      
        if(bicgstabSolver.info() == Eigen::Success) {
          p = bicgstabSolver.solve(-fx);
          if (bicgstabSolver.info() == Eigen::Success){
            cout << "Using BiGCSTAB solver for search Direction. " << endl; 
            solved = true;
          } else{
            cout << "BiCGSTAB solver failed, trying Conjugate Gradient solver." << endl;
            p = VectorXd::Zero(fx.size());
            solved = false;
          }  
        } else {
          cout << "Error: BiCGSTAB solver preconditioning failed. " << endl;
          p = VectorXd::Zero(jac.rows());
          solved = false;
        }
    }

    if(!solved) {
      cerr << "FATAL: All solvers failed to compute search direction. Exiting iteration." << endl;
      
      // savetxt(jac, "../Data/failed_jacobian.txt");
      // savetxt(fx, "../Data/failed_fx.txt");
      break;  
    }


    // Eigen::SimplexLDLT<SparseMatrix<double>> ldltSolver; //Calculating the Search Direction(Sparse::LDLT)
    // ldltSolver.compute(jac);
    // if (solver.info() != Success || ldltSolver.info() != Success) {
    //     cerr << "Decomposition failed!" << endl;
    //     break;
    // }
    // VectorXd p = solver.solve(-fx);

    // Eigen::BiCGSTAB<SparseMatrix<double>> bicgstabSolver; //Calculating the Search Direction(Sparse::BiCGSTAB)
    // bicgstabSolver.setMaxIterations(1000);
    // bicgstabSolver.torerance() = 1e-10;
    // VectorXd p = bicgstabSolver.solveWithGuess(fx, VectorXd::Zero(fx.size()));    
    //<- Searching Direction Funding//

    VectorXd gradF = jac.transpose() * fx;
    double descent_check = gradF.dot(p);

    if(descent_check >= -1e-8) {
        cout << "Warning: Newton direction failed descent check. Falling back to Steepest Descent." << endl;
        // 最速下降方向 p_SD = -J^T * f = -gradF
        p = -gradF; 
        // 关键：由于最速下降方向的长度可能非常大，必须对其进行归一化或限制模长，
        // 否则它可能会导致比牛顿法更严重的震荡和发散。
        // 这里采用简单的归一化，将初始 Lambda 限制在较小值（例如 0.1）。
        // double p_norm = p.norm();
        // if (p_norm > 1e-12) {
            //  归一化 p，并限制其最大步长
            //  p = p / p_norm;
        // } 
      }


    //-> Backtracking Line Search with Armijo Condition//
    double Lambda = 1.0;  //The Lambda is 1.0
    const double c = 1e-08;  //The Armijo condition constant
    const double minLambda = 1e-08; // Minimum step size

    // VectorXd fx_interior = fx.segment(5, TnoV - 10);
    // double fxNorm = fx_interior.norm(); // Norm of the current residual;
    double fxNorm = fx.norm();
    double newFxNorm = fxNorm;

    // Backtracking line search to satisfy the Armijo condition(core)
    while(Lambda > minLambda){
        VectorXd trialY = Ynew + Lambda * p;

        // Add trialBC(Yold, trialY, k); 
        // trialY = trialBC.Addynew();

        // Evaluate the new residual at the proposed step
        Load trialLoad(Yold, trialY);
        VectorXd fx_trial = trialLoad.LF(k);

        // VectorXd fx_trial_interior = fx_trial.segment(5, TnoV - 10);
        // newFxNorm = fx_trial_interior.norm();

        newFxNorm = fx_trial.norm();

        // Check the Armijo condition
        if (newFxNorm <= (1.0 -c * Lambda) * fxNorm) {
            break; // Condition satisfied           
        } else{
            Lambda *= 0.5; // Reduce step size
        }
    }
    
    if(Lambda <= minLambda){
        cout << "Warning: Minimum step size reached in line search." << endl;
    }
    
    // VectorXd deltaY = jac.inverse() * fx * (-1) * Lambda;
    VectorXd deltaY = p * Lambda;

    // VectorXd updatedY = Ynew + deltaY;
    // Add finalBC(Yold, updatedY, k);
    // deltaY = finalBC.Addynew() - Ynew;

    updateY(deltaY);

    saveIterationResults(i);

    double maxIncrementalPercentage = calculateMaxIncrementalPercentage(deltaY);
    double maxFx = calculateMaxFx();

    cout << "Lambda used: " << Lambda << endl;
    cout << "fxNorm before: " << fxNorm << ", fxNorm after: " << newFxNorm << endl;
    cout << "Max incremental percentage: " << maxIncrementalPercentage << endl;
    cout << "Max Fx (abs): " << maxFx << endl << endl;

    if (maxIncrementalPercentage < Error || maxFx < Error) { //The Max Error
      cout << "Iteration converge :)" << endl;
      // continue; // Condition satisfiedreak;
      break;
    } else {
      updateNextIteration(k);
    }
  }
  SPDLOG_DEBUG("End of iteration for index {}", k);
}

VectorXd Iterator::out() { return Ynew; }

void Iterator::updateY(const VectorXd &deltaY) {
  Ynew += deltaY;
  // savetxt(deltaY, "../Data/deltaY.txt");
}

void Iterator::saveIterationResults(int iteration) {
  if (iteration % 20000 ==0) // Only save every 20000 iterations (100 Timesteps)
  {
    // savetxt(jac, "../Data/loadjac.txt");
    // savetxt(fx, "../Data/fx.txt");
    // savetxt(Ynew, "../Data/Ynew.txt");
  }
}

double Iterator::calculateMaxIncrementalPercentage(const VectorXd &deltaY) {
  SPDLOG_DEBUG("Calculating max incremental percentage");
  double amax = 0;

  for (int i = 10; i < TnoV - 10; i++){
    if (Yold(i) != 0){
      double a = abs(deltaY(i)) / abs(Yold(i));
      amax = std::max(amax,a);
    }
  }

  for (int i = 3; i < 8; ++i){
    if (Yold(i) != 0){
      amax = std::max(amax, abs(deltaY(i)) / abs(Yold(i)));
    }
  }

  for (int i = TnoV - 7; i < TnoV - 2; ++i){
    if (Yold(i) != 0){
      amax = std::max(amax, abs(deltaY(i)) / abs(Yold(i)));
    }
  }

 return amax;
}

double Iterator::calculateMaxFx() {
  double bmax = 0;
  for (int i = 5; i < TnoV - 5; i++) {
    bmax = std::max(bmax, abs(fx(i)));
  }
  return bmax;
}

void Iterator::updateNextIteration(int k) {
  SPDLOG_DEBUG("Updating next iteration");

  Load templd(Yold, Ynew);
  fx = templd.LF(k);
  jac = templd.LJ(k);
}

void Iterator::savetxt(const Eigen::MatrixXd &mat,
                       const string &filename) const {
  ofstream outfile(filename, ios::trunc);
  if (outfile.is_open()) {
    outfile << mat;
    outfile.close();
  } else {
    cerr << "Error opening file: " << filename << endl;
  }
}

void Iterator::savetxt(const Eigen::SparseMatrix<double> &mat,
                       const string &filename) const {
  ofstream outfile(filename, ios::trunc);
  if (outfile.is_open()) {
    outfile << mat; 
    outfile.close();
  } else {
    cerr << "Error opening file: " << filename << endl;
  }
}