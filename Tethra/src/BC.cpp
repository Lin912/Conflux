#include <iostream>
#include "BC.h"

BC::BC(const Eigen::VectorXd &arr, const Eigen::VectorXd &brr):Yold(arr), Ynew(brr) {}

BC::~BC() {}

Eigen::VectorXd BC::process(Eigen::VectorXd &Y)
{
    Eigen::VectorXd temp(500);
    temp.head(10) = Y.head(10);          
    temp.segment(10, 480) = Y.segment(10, 480); 
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
