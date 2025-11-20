#include "MNQ.h"
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include <cmath>
#include <vector>

using namespace Eigen;

MNQ::MNQ(const VectorXd &arr, const VectorXd &brr, int index)
    : Yold(arr), Ynew(brr) {
  FiberRO a;
  PhysicalData physicalData = ParaReader::ReadAllPhysicalData(a, index);
  A = physicalData.A;
  rho = physicalData.rho;
  d0 = physicalData.d0;
  E = physicalData.E;
  I = physicalData.I;
  M = physicalData.M;
  ma = physicalData.ma;
  Cdt = physicalData.Cdt;
  Cdn = physicalData.Cdn;
  Cdb = physicalData.Cdb;
  pi = physicalData.pi;
  g = physicalData.g;
  Gx = physicalData.Gx;
  Gy = physicalData.Gy;
  Gz = physicalData.Gz;

  Vx = physicalData.Vx;
  Vy = physicalData.Vy;
  Vz = physicalData.Vz;

  Vtx = physicalData.Vtx;
  Vty = physicalData.Vty;
  Vtz = physicalData.Vtz;

  Vbx = physicalData.Vbx;
  Vby = physicalData.Vby;
  Vbz = physicalData.Vbz;

  deltaT = physicalData.deltaT;
  deltaS = physicalData.deltaS;

  Gbx = physicalData.Gbx;
  Gby = physicalData.Gby;
  Gbz = physicalData.Gbz;
  Ax = physicalData.Ax;
  Ay = physicalData.Ay;
  Az = physicalData.Az;
}

MNQ::~MNQ() {}

Eigen::SparseMatrix<double> MNQ::CreateSparseMatrix(const Eigen::VectorXd &Y) {
  Eigen::SparseMatrix<double> temp(TnoV, TnoV);
  std::vector<Eigen::Triplet<double>> triplets;

  triplets.reserve(Nodes * 20);

  for (int i = 0; i < Nodes; i++) {
    int idx0 = i * 10 + 0;
    int idx1 = i * 10 + 1;
    int idx2 = i * 10 + 2;
    int idx3 = i * 10 + 3;
    int idx4 = i * 10 + 4;
    int idx5 = i * 10 + 5;
    int idx6 = i * 10 + 6;
    int idx7 = i * 10 + 7;
    int idx8 = i * 10 + 8;
    int idx9 = i * 10 + 9;

    double cos_theta = std::cos(Y(idx6));
    double sin_theta = std::sin(Y(idx6));
    double cos_phi = std::cos(Y(idx7));
    double sin_phi = std::sin(Y(idx7));

    triplets.push_back(Eigen::Triplet<double>(idx0, idx0, M));
    triplets.push_back(Eigen::Triplet<double>(idx0, idx6, M * Y(idx2)));
    triplets.push_back(
        Eigen::Triplet<double>(idx0, idx7, -M * Y(idx1) * cos_theta));

    triplets.push_back(Eigen::Triplet<double>(idx1, idx1, M + ma));
    triplets.push_back(Eigen::Triplet<double>(
        idx1, idx7,
        M * Y(idx0) * cos_theta + M * Y(idx2) * sin_theta + ma * Vy * sin_phi +
            ma * Vx * cos_phi));

    triplets.push_back(Eigen::Triplet<double>(idx2, idx2, M + ma));
    triplets.push_back(Eigen::Triplet<double>(
        idx2, idx6,
        -M * Y(idx0) - ma * Vx * cos_phi * cos_theta -
            ma * Vy * sin_phi * cos_theta + ma * Vz * sin_theta));
    triplets.push_back(Eigen::Triplet<double>(
        idx2, idx7,
        -M * Y(idx1) * sin_theta + ma * Vx * sin_phi * sin_theta -
            ma * Vy * cos_phi * sin_theta));

    triplets.push_back(Eigen::Triplet<double>(idx3, idx3, 1.0 / (A * E)));
    triplets.push_back(Eigen::Triplet<double>(
        idx4, idx7, cos_theta * (Y(idx3) / (A * E) + 1.0)));
    triplets.push_back(
        Eigen::Triplet<double>(idx5, idx6, Y(idx3) / (A * E) + 1.0));
  }

  temp.setFromTriplets(triplets.begin(), triplets.end());
  return temp;
}

Eigen::SparseMatrix<double> MNQ::Mold() { return CreateSparseMatrix(Yold); }
Eigen::SparseMatrix<double> MNQ::Mnew() { return CreateSparseMatrix(Ynew); }

Eigen::SparseMatrix<double> MNQ::CreateSparseNMatrix(const Eigen::VectorXd &Y) {
  Eigen::SparseMatrix<double> temp(TnoV, TnoV);
  std::vector<Eigen::Triplet<double>> triplets;

  triplets.reserve(Nodes * 15);

  for (int i = 0; i < Nodes; i++) {
    int idx0 = i * 10 + 0;
    int idx1 = i * 10 + 1;
    int idx2 = i * 10 + 2;
    int idx3 = i * 10 + 3;
    int idx4 = i * 10 + 4;
    int idx5 = i * 10 + 5;
    int idx6 = i * 10 + 6;
    int idx7 = i * 10 + 7;
    int idx8 = i * 10 + 8;
    int idx9 = i * 10 + 9;

    double cos_theta = std::cos(Y(idx6));

    triplets.push_back(Eigen::Triplet<double>(idx0, idx3, -1.0));
    triplets.push_back(Eigen::Triplet<double>(idx1, idx4, -1.0));
    triplets.push_back(Eigen::Triplet<double>(idx2, idx5, -1.0));
    triplets.push_back(Eigen::Triplet<double>(idx3, idx0, -1.0));
    triplets.push_back(Eigen::Triplet<double>(idx4, idx1, -1.0));
    triplets.push_back(Eigen::Triplet<double>(idx5, idx2, 1.0));
    triplets.push_back(Eigen::Triplet<double>(idx6, idx8, E * I));
    triplets.push_back(Eigen::Triplet<double>(idx7, idx9, E * I));
    triplets.push_back(Eigen::Triplet<double>(idx8, idx6, 1.0));
    triplets.push_back(Eigen::Triplet<double>(idx9, idx7, cos_theta));
  }

  temp.setFromTriplets(triplets.begin(), triplets.end());
  return temp;
}
Eigen::SparseMatrix<double> MNQ::Nold() { return CreateSparseNMatrix(Yold); }
Eigen::SparseMatrix<double> MNQ::Nnew() { return CreateSparseNMatrix(Ynew); }

Eigen::VectorXd MNQ::CreateQVector(const Eigen::VectorXd &Y) {
  Eigen::VectorXd temp(TnoV);

  for (int i = 0; i < Nodes; i++) {
    int idx0 = i * 10 + 0;
    int idx1 = i * 10 + 1;
    int idx2 = i * 10 + 2;
    int idx3 = i * 10 + 3;
    int idx4 = i * 10 + 4;
    int idx5 = i * 10 + 5;
    int idx6 = i * 10 + 6;
    int idx7 = i * 10 + 7;
    int idx8 = i * 10 + 8;
    int idx9 = i * 10 + 9;

    double strain_term = sqrt(Y(idx3) / (A * E) + 1.0);
    double cos_theta = cos(Y(idx6));
    double sin_theta = sin(Y(idx6));
    double cos_phi = cos(Y(idx7));
    double sin_phi = sin(Y(idx7));
    
    double Vr_x = Y(idx0) + Vz * sin_theta - Vx * cos_phi * cos_theta - Vy * cos_theta * sin_phi;
    double Vr_y = Y(idx1) - Vy * cos_phi + Vx * sin_phi;
    double Vr_z = Vz * cos_theta - Y(idx2) + Vx * cos_phi * sin_theta + Vy * sin_phi * sin_theta;
    
    double V_norm_sq = Vr_y*Vr_y + Vr_z*Vr_z;
    double V_norm = sqrt(V_norm_sq);
    
    //double strain_term_cubed = pow(strain_term, 6); 
    double term_pow3 = pow(Y(idx3) / (A * E) + 1.0, 3);

    temp(idx0) =
          Y(idx9) * Y(idx4) - Y(idx8) * Y(idx5) + Gz * sin_theta -
          Gx * cos_phi * cos_theta - Gy * cos_theta * sin_phi +
          0.5 * Cdt * d0 * pi * rho * abs(Vr_x) * strain_term * Vr_x;
          
    temp(idx1) =
          Gx * sin_phi - Gy * cos_phi - Y(idx9) * Y(idx3) -
          Y(idx9) * Y(idx5) * tan(Y(idx6)) +
          0.5 * Cdn * d0 * rho * strain_term * V_norm * Vr_y;
          
    temp(idx2) =
          Y(idx8) * Y(idx3) - Gz * cos_theta -
          Gx * cos_phi * sin_theta - Gy * sin_phi * sin_theta +
          Y(idx9) * Y(idx4) * tan(Y(idx6)) - 
          0.5 * Cdb * d0 * rho * strain_term * V_norm * Vr_z;
          
    temp(idx3) = Y(idx9) * Y(idx1) - Y(idx8) * Y(idx2);
    temp(idx4) = -Y(idx9) * Y(idx0) - Y(idx9) * Y(idx2) * tan(Y(idx6));
    temp(idx5) = -Y(idx8) * Y(idx0) - Y(idx9) * Y(idx1) * tan(Y(idx6));
    
    temp(idx6) = E * I * pow(Y(idx9), 2) * tan(Y(idx6)) - Y(idx5) * term_pow3;
    temp(idx7) = Y(idx4) * term_pow3 - E * I * Y(idx8) * Y(idx9) * tan(Y(idx6));
    temp(idx8) = -Y(idx8);
    temp(idx9) = -Y(idx9);
  }
  return temp;
}
Eigen::VectorXd MNQ::Qold() { return CreateQVector(Yold); }
Eigen::VectorXd MNQ::Qnew() { return CreateQVector(Ynew); }