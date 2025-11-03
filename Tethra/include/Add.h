#pragma once
#include <Eigen/Dense>
#include "ReadOut.h"
#include "ParaReader.h"
#include "Nums.h"

class Add
{
private:
    Eigen::VectorXd Yold, Ynew;

    double Vtx, Vty, Vtz, Vbx, Vby, Vbz;
    //int Timestep, Nodes, Variables, TnoV;
    Eigen::Vector3d calculatePoint00(const Eigen::VectorXd& Y);
    Eigen::Vector3d calculatePoint02(const Eigen::VectorXd& Y);

public:

    Add(const Eigen::VectorXd &arr, const Eigen::VectorXd &brr, int index);
    ~Add();

    Eigen::VectorXd Addyold();
    Eigen::VectorXd Addynew();
};

