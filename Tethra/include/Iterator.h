#pragma once
#include <iostream>
#include <fstream>
#include <cmath>
#include <Eigen/Dense>
#include <Eigen/Sparse>
#include "Load.h"
#include "BC.h"
#include "Add.h"
#include "Nums.h"

using namespace std;
using namespace Eigen;

class Iterator
{
private:
    int times;  // Iteration Times
    double Error;  // Convergence Error

    VectorXd fx;  // Stores fx
    // MatrixXd jac;  // Stores Dense jacobian
    SparseMatrix<double> jac;  // Stores sparse jacobian

    VectorXd Yold;  // Temporary storage for Yold
    VectorXd &Ynew;  // Temporary storage for Ynew

    // Save matrix to file
    void savetxt(const Eigen::MatrixXd& mat, const string& filename) const;
    void savetxt(const Eigen::SparseMatrix<double>& mat, const string& filename) const;
    
    void saveIterationResults(int iteration);
    double calculateMaxIncrementalPercentage(const VectorXd& deltaY);
    double calculateMaxFx();
   
public:
    Iterator(VectorXd& arr, VectorXd& brr, int a, double b);
    ~Iterator();

    void begin(int k);
    VectorXd out();
    void updateY(const VectorXd& deltaY);
    void updateNextIteration(int k);
};
