#pragma once
#include <Eigen/Dense>
#include "ReadOut.h"
#include "ParaReader.h"
#include "Nums.h"

class BC
{
private:
    Eigen::VectorXd Yold;
    Eigen::VectorXd Ynew;
    Eigen::VectorXd process(Eigen::VectorXd &Y);

    // int Timestep, Nodes, Variables, TnoV; 

public:
    BC(const Eigen::VectorXd &arr, const Eigen::VectorXd &brr);
    ~BC();

    Eigen::VectorXd yold();
    Eigen::VectorXd ynew();
};
