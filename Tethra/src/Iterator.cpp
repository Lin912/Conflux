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
    // -> Searching Direction Funding
    VectorXd p;
    bool solved = false;    

    // Try different solvers in order of preference
    //Search Direction(Sparse::SparseLU)
    Eigen::SparseLU<SparseMatrix<double>> sparsesolver; 
    sparsesolver.compute(jac);

    if (sparsesolver.info() == Success) {
      p = sparsesolver.solve(-fx);
      solved = true;  
      cout << "Using Sparse::SparseLU for calculating PDirection ->" << endl;
    } else {
      cout << "SparseLU decomposition Failed :(. Trying the other MatrixMethods" << endl;
      cout << "Falling back to BiCGSTAB." << endl;
    
    
      BiCGSTAB<SparseMatrix<double>> bicgstabsolver;
      bicgstabsolver.setMaxIterations(200);
      bicgstabsolver.setTolerance(1e-06);
      bicgstabsolver.compute(jac);
      
      if (bicgstabsolver.info() == Success) {
          p = bicgstabsolver.solve(-fx);
          if (bicgstabsolver.info() == Success) {
            cout << "BiCGSTAB successfully found search direction." << endl;
            solved = true;
          } else {
            cout << "BiCGSTAB failed to converge :(. Aborting Iteration !!!" << endl;
            p = VectorXd::Zero(fx.rows());
            solved = false;
          }
      } else {
          cout << "BiCGSTAB preconditioning failed. Aborting iteration." << endl;
          p = VectorXd::Zero(fx.rows());
          solved = false;
      }
    }

    if (!solved) {
      cerr << "Failed to compute search direction. Exiting iteration." << endl;
      break;
    }

    //<- Searching Direction Funding//
    VectorXd gradF = jac.transpose() * fx;
    double descent_check = gradF.dot(p);

    if(descent_check >= -1e-8) {
        cout << "[Noting]: Newton direction failed Descent check. Falling back to Steepest Descent." << endl;
        
        // The Steepest Descent Direction(SDD): p_SD = -J^T * f = -gradF
        p = -gradF; 
        
        // <core> :
        // Since the length of the Steepest Descent direction may be very large,
        // it must be normalized or the mode length limited.
        // Otherwise it may lead to More Severe Oscillations and Divergence than Newton's method.
        // Simple normalization is used here to limit the initial Lambda to a small value (such as 0.1).
        double p_norm = p.norm();
        if (p_norm > 1e-12) {
          //  Normalizated p.
          p = p * min(1.0, 1.0 / p_norm);
        } 
      }

    //-> Backtracking Line Search with Armijo Condition//
    double fxNorm = fx.norm();
    double Lambda = 1.000;  //The Lambda is 1.0
    const double c = 1e-01;  //The Armijo condition constant(As c is greater, the condition is more strict)
    const double minLambda = 1e-08; // Minimum step size

    VectorXd Ynew_trial;
    double normFx_trial;

    // Backtracking line search to satisfy the Armijo condition(core01)
    for (int j = 0; j < 20; ++j) { // Max 20 steps for backtracking
        Ynew_trial = Ynew + Lambda * p;
        
        // Load templd(Yold, Ynew_trial);
        Load templd(Yold, Ynew_trial);
        VectorXd Fx_trial = templd.LF(k);
        normFx_trial = Fx_trial.norm();

        // Check the Armijo condition
        if (normFx_trial < (1.0 - c * Lambda) * fxNorm || Lambda < minLambda) {
            break;
        } else{
        Lambda *= 0.5;
        }
    }
        
    // UpDate Ynew
    updateY(p * Lambda);
    
    // Recalculate Fx and Jacobian for next iteration
    updateNextIteration(k);
    
    // Save the TEMP Results in Iteration step
    // saveIterationResults(i);

    // Convergence Check
    double maxIncrementalPercentage = calculateMaxIncrementalPercentage(Lambda * p);
    double maxFx = calculateMaxFx();
    
    if (maxIncrementalPercentage < InpError && maxFx < Error) {
      cout << "Iteration converge [Strict] :)" << endl;
      break;
    }

    cout << "Lambda used: " << Lambda << endl;
    cout << "fxNorm Now: " << fxNorm << endl;
    cout << "Max incremental percentage: " << maxIncrementalPercentage << endl;
    cout << "Max Fx (abs): " << maxFx << endl << endl;
  }
  // SPDLOG_DEBUG("End of iteration for index {}", k);
}

VectorXd Iterator::out() { return Ynew; }

void Iterator::updateY(const VectorXd &deltaY) {
  Ynew += deltaY;
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
  double amax = 0.0;

  for (int i = 10; i < TnoV - 10; i++){
    if (Ynew(i) != 0){
      double a = abs(deltaY(i)) / abs(Ynew(i));
      amax = std::max(amax,a);
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

  // Keep Pure Calculation
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
