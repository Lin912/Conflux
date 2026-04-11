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
#include <cstdint>

#ifdef _WIN32
#include <windows.h>
#endif

#pragma pack(push, 1) 
struct UnifiedControlDirect {
    int32_t FLAG_STARCCM;   
    int32_t FLAG_TETHRA;    
    int32_t FLAG_ROVCTRL;   
    int32_t PADDING_ALIGN;  

    double timestamp;       
    double x, y, z;         
    double roll, pitch, yaw;
    double u, v, w;         
    double p, q, r;         

    double rpm_0, rpm_1, rpm_2, rpm_3, rpm_4, rpm_5; 
    double forceX, forceY, forceZ; 

    char padding[840];
};
#pragma pack(pop)
extern UnifiedControlDirect* g_sharedData;


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
        string outfile;
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
