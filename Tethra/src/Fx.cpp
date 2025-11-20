#include "Fx.h"
#include <vector>
#include <thread>
#include <spdlog/spdlog.h>

using namespace std;
using namespace Eigen;

Fx::Fx(const VectorXd &arr, const VectorXd &brr, int index)
    : Yold(arr), Ynew(brr), k(index)
{
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

Fx::~Fx()
{
}

VectorXd Fx::fx() {
    int numSegments = Nodes;
    int segmentSize = Variables;

    MNQ AA(Yold, Ynew, k);

    SparseMatrix<double> BigMold = AA.Mold();
    SparseMatrix<double> BigMnew = AA.Mnew();
    SparseMatrix<double> BigNold = AA.Nold();
    SparseMatrix<double> BigNnew = AA.Nnew();
    
    VectorXd BigQold = AA.Qold();
    VectorXd BigQnew = AA.Qnew();

    std::vector<VectorXd> Yold_segments(numSegments);
    std::vector<VectorXd> Ynew_segments(numSegments);
    std::vector<VectorXd> Qold_vec(numSegments);
    std::vector<VectorXd> Qnew_vec(numSegments);

    for (int i = 0; i < numSegments; i++) {
        int startIdx = i * segmentSize;
        Yold_segments[i] = Yold.segment(startIdx, segmentSize);
        Ynew_segments[i] = Ynew.segment(startIdx, segmentSize);
        Qold_vec[i]      = BigQold.segment(startIdx, segmentSize);
        Qnew_vec[i]      = BigQnew.segment(startIdx, segmentSize);
    }
    
    std::vector<MatrixXd> Mold_vec(numSegments, MatrixXd::Zero(segmentSize, segmentSize));
    std::vector<MatrixXd> Mnew_vec(numSegments, MatrixXd::Zero(segmentSize, segmentSize));
    std::vector<MatrixXd> Nold_vec(numSegments, MatrixXd::Zero(segmentSize, segmentSize));
    std::vector<MatrixXd> Nnew_vec(numSegments, MatrixXd::Zero(segmentSize, segmentSize));

    auto extractBlocks = [&](const SparseMatrix<double>& BigMat, std::vector<MatrixXd>& targetVec) {
        for (int k = 0; k < BigMat.outerSize(); ++k) {
            for (SparseMatrix<double>::InnerIterator it(BigMat, k); it; ++it) {
                int r = it.row();
                int c = it.col();
                
                int blockRow = r / segmentSize;
                int blockCol = c / segmentSize;

                if (blockRow == blockCol && blockRow < numSegments) {
                    targetVec[blockRow](r % segmentSize, c % segmentSize) = it.value();
                }
            }
        }
    };

    extractBlocks(BigMold, Mold_vec);
    extractBlocks(BigMnew, Mnew_vec);
    extractBlocks(BigNold, Nold_vec);
    extractBlocks(BigNnew, Nnew_vec);

    std::vector<VectorXd> temp(numSegments - 1, VectorXd(segmentSize));

    double dT = deltaT;
    double dS = deltaS;
    double dTdS = deltaT * deltaS;

    for (int i = 0; i < numSegments - 1; i++) {
        temp[i] = ((Nnew_vec[i] + Nnew_vec[i+1]) * (Ynew_segments[i+1] - Ynew_segments[i]) * dT)
                + ((Nold_vec[i] + Nold_vec[i+1]) * (Yold_segments[i+1] - Yold_segments[i]) * dT)
                + ((Mnew_vec[i+1] + Mold_vec[i+1]) * (Ynew_segments[i+1] - Yold_segments[i+1]) * dS)
                + ((Mnew_vec[i] + Mold_vec[i]) * (Ynew_segments[i] - Yold_segments[i]) * dS)
                + ((Qold_vec[i] + Qold_vec[i+1] + Qnew_vec[i] + Qnew_vec[i+1]) * dTdS);
    }

    auto calculate_BCtemp = [](const VectorXd& YVec, double Vx_in, double Vy_in, double Vz_in) {
        VectorXd BCtemp(5);
        double cos_theta = cos(YVec(6));
        double sin_theta = sin(YVec(6));
        double cos_phi = cos(YVec(7));
        double sin_phi = sin(YVec(7));

        BCtemp(0) = YVec(0) - (Vx_in * cos_phi * cos_theta + Vy_in * cos_theta * sin_phi - Vz_in * sin_theta);
        BCtemp(1) = YVec(1) - (Vy_in * cos_phi - Vx_in * sin_phi);
        BCtemp(2) = YVec(2) - (Vx_in * cos_phi * sin_theta + Vy_in * sin_theta * sin_phi + Vz_in * cos_theta);
        BCtemp(3) = YVec(8);
        BCtemp(4) = YVec(9);
        return BCtemp;
    };

    VectorXd BCtemp0 = calculate_BCtemp(Ynew_segments[0], Vtx, Vty, Vtz);
    VectorXd BCtemp1 = calculate_BCtemp(Ynew_segments[numSegments-1], Vbx, Vby, Vbz);


    VectorXd ret(numSegments * segmentSize);
    ret.head(5) = BCtemp0;
    
    for (int i = 0; i < numSegments - 1; i++) {
        int startIdx = 5 + i * segmentSize;
        ret.segment(startIdx, segmentSize) = temp[i];
    }

    ret.tail(5) = BCtemp1;

    // SPDLOG_DEBUG("FX Calculation Complete");
    return ret;
}