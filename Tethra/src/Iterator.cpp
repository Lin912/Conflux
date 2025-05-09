#include "Iterator.h"
#include <Eigen/Dense>
#include <cmath>
#include <fstream>
#include <iostream>
#include <spdlog/spdlog.h>


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
  SPDLOG_DEBUG("EXAMPLE LOG 0");
  Yold = bc.Addyold();
  SPDLOG_DEBUG("EXAMPLE LOG 1");
  Ynew = bc.Addynew();
  SPDLOG_DEBUG("EXAMPLE LOG 2");

  Load load(Yold, Ynew);
  fx = load.LF(k);
  jac = load.LJ(k);
  SPDLOG_DEBUG("exmaple log 1");

  for (int i = 0; i < times; i++) {
    cout << "Iteration " << i + 1 << " times; " << endl;

    double Lambda = 0.5;// Lambda is 0.5
    VectorXd deltaY = jac.inverse() * fx * (-1) * Lambda; 
    updateY(deltaY);

    saveIterationResults(i);

    double maxIncrementalPercentage = calculateMaxIncrementalPercentage(deltaY);
    double maxFx = calculateMaxFx();

    cout << "Max incremental percentage: " << maxIncrementalPercentage << endl;
    cout << "Max Fx (abs): " << maxFx << endl << endl;

    if (maxIncrementalPercentage < 1e-16 || maxFx < 1e-16) {
      cout << "Iteration converged!" << endl;
      break;
    } else {
      updateNextIteration(k);
    }
  }
  SPDLOG_DEBUG("exmaple log 2");
}

VectorXd Iterator::out() { return Ynew; }

void Iterator::updateY(const VectorXd &deltaY) {
  Yold = Ynew;
  Ynew += deltaY;
  // savetxt(deltaY, "../Data/deltaY.txt");
}

void Iterator::saveIterationResults(int iteration) {
  if (iteration % 20000 ==
      0) // Only save every 20000 iterations (100 Timesteps)
  {
    // savetxt(jac, "../Data/loadjac.txt");
    // savetxt(fx, "../Data/fx.txt");
    // savetxt(Ynew, "../Data/Ynew.txt");
  }
}

double Iterator::calculateMaxIncrementalPercentage(const VectorXd &deltaY) {
  SPDLOG_DEBUG("Calculating max incremental percentage");
  double amax = 0;
  for (int i = 10; i < 489; i++) {
    if (Yold(i) != 0) {
      double a = abs(deltaY(i)) / abs(Yold(i));
      amax = std::max(amax, a);
    }
  }
  return amax;
}

double Iterator::calculateMaxFx() {
  double bmax = 0;
  for (int i = 10; i < 489; i++) {
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
