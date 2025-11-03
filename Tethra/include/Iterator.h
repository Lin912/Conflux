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
    Eigen::SparseMatrix<double> jac;  // Stores sparse jacobian

    VectorXd Yold;  // Temporary storage for Yold
    VectorXd Ynew;  // Temporary storage for Ynew

    // Save matrix to file
    void savetxt(const Eigen::MatrixXd& mat, const string& filename) const;
    void savetxt(const Eigen::SparseMatrix<double>& mat, const string& filename) const;

    void updateY(const VectorXd& deltaY);
    void saveIterationResults(int iteration);
    double calculateMaxIncrementalPercentage(const VectorXd& deltaY);
    double calculateMaxFx();
    void updateNextIteration(int k);


public:
    // Constructor
    Iterator(VectorXd& arr, VectorXd& brr, int a, double b);
    
    // Destructor
    ~Iterator();

    // Begin iteration process
    void begin(int k);
    // Return the final Ynew
    VectorXd out();

};
