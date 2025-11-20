#pragma once
#include "MNQ.h"
#include "ParaReader.h"
#include "ReadOut.h"
#include <Eigen/Dense>
#include <cmath>
#include <iostream>
#include <vector>
#include "Nums.h"

class Fx {
private:
  VectorXd Yold;
  VectorXd Ynew;
  VectorXd temp;

  double A, rho, d0, E, I, M, ma, Cdt, Cdn, Cdb, Gx, Gy, Gz, pi, g;
  double Vx, Vy, Vz;
  double Vtx, Vty, Vtz;
  double Vbx, Vby, Vbz;
  double deltaT, deltaS;
  double Gbx, Gby, Gbz;
  double Ax, Ay, Az;

  // int Timestep, Nodes, Variables, TnoV;
  
  int k;

public:
  Fx(const VectorXd &arr, const VectorXd &brr, int index);
  ~Fx();
  VectorXd fx();
};
