#include <iostream>
#include "BC.h"

BC::BC(const Eigen::VectorXd &arr, const Eigen::VectorXd &brr):Yold(arr), Ynew(brr) {
    // FiberRO a;
    // NumData numData = ParaReader::ReadNumData(a);
    // Timestep = numData.TS;
    // Nodes = numData.NODES;
    // Variables = numData.VARIABLES;
    // TnoV = numData.TNOV;
}

BC::~BC() {}

Eigen::VectorXd BC::process(Eigen::VectorXd &Y)
{
    Eigen::VectorXd temp(TnoV);
    temp.head(10) = Y.head(10);          
    temp.segment(10, TnoV-20) = Y.segment(10, TnoV-20); 
    temp.tail(10) = Y.tail(10);        
    return temp;
}

Eigen::VectorXd BC::yold()
{
    return process(Yold);
}

Eigen::VectorXd BC::ynew()
{
    return process(Ynew);
}
