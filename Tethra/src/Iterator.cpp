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
  Add bc(Yold, Ynew, k);
  Yold = bc.Addyold();
  Ynew = bc.Addynew();

  Load load(Yold, Ynew);
  fx = load.LF(k);
  jac = load.LJ(k);

  for (int i = 0; i < times; i++) {
    cout << "Iteration " << i + 1 << " times; " << endl;

    //-> Searching Direction Funding//
    // VectorXd p = -jac.fullPivLu().solve(fx); //Calculating the Search Direction(Dense)

    Eigen::SparseLU<SparseMatrix<double>> sparsesolver;  //Calculating the Search Direction(Sparse::SparseLU)
    sparsesolver.compute(jac);
    VectorXd p = sparsesolver.solve(-fx);
    
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
    
    double Lambda = 1.0;  //The Lambda is 1.0
    const double c = 1e-4;  //The Armijo condition constant
    const double minLambda = 1e-6; // Minimum step size

    double fxNorm = fx.norm(); // Norm of the current residual
    double newFxNorm = fxNorm;

    // Backtracking line search to satisfy the Armijo condition(core)
    while(Lambda > minLambda){
        VectorXd trialY = Ynew + Lambda * p;

        // Evaluate the new residual at the proposed step
        Load trialLoad(trialY, trialY);
        VectorXd fx_trial = trialLoad.LF(k);
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
      continue; // Condition satisfiedreak;
    } else {
      updateNextIteration(k);
    }
  }
  SPDLOG_DEBUG("End of iteration for index {}", k);
}

VectorXd Iterator::out() { return Ynew; }

void Iterator::updateY(const VectorXd &deltaY) {
  Yold = Ynew;
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
  for (int i = 10; i < TnoV-11; i++) {
    if (Yold(i) != 0) {
      double a = abs(deltaY(i)) / abs(Yold(i));
      amax = std::max(amax, a);
    }
  }
  return amax;
}

double Iterator::calculateMaxFx() {
  double bmax = 0;
  for (int i = 10; i < TnoV-11; i++) {
    bmax = std::max(bmax, abs(fx(i)));
  }
  return bmax;
}

void Iterator::updateNextIteration(int k) {
  SPDLOG_DEBUG("Updating next iteration");
  Add tempAdd(Yold, Ynew, k);
  Yold = tempAdd.Addyold();
  Ynew = tempAdd.Addynew();

  Load templd(Yold, Ynew);
  fx = templd.LF(k);
  jac = templd.LJ(k);

  BC tempbc(Yold, Ynew);
  Yold = tempbc.yold();
  Ynew = tempbc.ynew();
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