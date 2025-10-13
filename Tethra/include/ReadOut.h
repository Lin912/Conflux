#pragma once
#include <iostream>
#include <vector>
#include <cmath>
#include <string>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <Eigen/Dense>
#include <stdlib.h>
#include <algorithm>
#include <stdexcept>
#include <filesystem>
#include <array>
#include "Nums.h"



#ifdef _WIN32
#include <windows.h>
#endif

using namespace std;
using namespace Eigen;
using Matrix3x3 = std::array<std::array<double, 3>, 3>;


class FiberRO {
    private:
        string fileTopVel;
        string fileWater;
        string fileBottomVelocityRelative;
        string fileBottomomegaRelative;
        string fileBottomEulerAngle;
        string filePhysical;
        string fileObject;
        string fileDelta;
        string fileNums;
        // string outfile;
        string Outfile;
        string Topforceout;
        string Bottomforceout;
        // int Timestep, Nodes, Variables, TnoV;

        vector<double> readLastLineData(const string& filePath);
        Matrix3x3 computeRotationMatrix(const vector<double>& Eulerangle);
        vector<double> ReadCSVLine(const string& filename, int lineIndex = 1);
        vector<double> ParseCSVLine(const char* lineStart);    

        VectorXd ParseCSVLineToVector(const std::string& line);
        double FastStod(const std::string& str);
        size_t CountColumns(const std::string& line);
        void ParseCSVLine(const std::string& line, std::vector<double>& rowData); 
        MatrixXd ConvertToEigenMatrix(const std::vector<std::vector<double>>& data);
        VectorXd ParseCSVLinetoVector(const std::string& line);
        double FastStod(std::string_view str);
        string CreateZeroRow(int cols);

    public:
        FiberRO();
        ~FiberRO();

        vector<double> ReadTopVel(int k);
        vector<double> ReadWater(int k);  
        vector<double> ReadBottomVel();
        VectorXd ReadTheLastRow(int index);
        MatrixXd readCSV(int row);
        void OutTopforce(VectorXd v);
        void OutBottomforce(VectorXd v);

        vector<double> ReadBottomG();
        vector<double> ReadPhysical();
        vector<double> ReadDelta();

        void Output(const MatrixXd &arr, int rr, int ll);
        double flutov(char* filename);
};