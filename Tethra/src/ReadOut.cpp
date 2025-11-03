#include "ReadOut.h"
#include <algorithm>
#include <spdlog/spdlog.h>

FiberRO::FiberRO()
    : fileTopVel("../csv/TopVel4_A0.3_T2.0_Z0.40_20s/velocity_data.csv"), fileObject("../csv/TowedObject.csv"),
      fileBottomVelocityRelative("../../../HydroSimulation/HydroData/VelocityRelative.csv"),
      fileBottomomegaRelative("../../../HydroSimulation/HydroData/omegaRelative.csv"),
      fileBottomEulerAngle("../../../HydroSimulation/HydroData/EulerAngle.csv"),
      fileWater("../csv/Water.csv"), filePhysical("../csv/Parameters.csv"),
      fileDelta("../csv/Delta.csv"), Outfile("../csv/output.csv"){
      std::filesystem::create_directory("../csv");
      // The .txt used to read into computation through udf
      Topforceout = "../../../HydroSimulation/TethraForces/topforce.txt";
      Bottomforceout = "../../../HydroSimulation/TethraForces/bottomforce.txt";
}

FiberRO::~FiberRO() {}

vector<double> FiberRO::ReadTopVel(int k) {
    std::ifstream infile(fileTopVel);
    if (!infile.is_open()) {
        std::cerr << "Error: cannot open file " << fileTopVel << ".csv" << std::endl;
        return {};
    }

    string line;
    for (int i = 0; i <= k; ++i) {
        if (!std::getline(infile, line)) {
            std::cerr << "Error: file has fewer than " << k + 1 << " lines\n";
            return {};
        }
    }

    vector<double> arrdata;
    arrdata.reserve(32);

    const char* ptr = line.c_str();
    const char* end = ptr + line.size();

    while (ptr < end) {
        const char* next = std::find(ptr, end, ',');
        double value = 0.0;
        std::from_chars(ptr, next, value);
        arrdata.push_back(value);
        ptr = (next == end) ? end : next + 1;
    }
    return arrdata;
}

vector<double> FiberRO::ReadWater(int k) {
    std::ifstream infile(fileWater);
    if (!infile.is_open()) {
        std::cerr << "Error: cannot open " << fileWater << ".csv" << std::endl;
        return {};
    }

    std::string line;
    for (int i = 0; i <= k; ++i) {
        if (!std::getline(infile, line)) {
            std::cerr << "Error: file has fewer than " << k + 1 << " lines\n";
            return {};
        }
    }

    std::vector<double> arrdata;
    arrdata.reserve(32);

    const char* ptr = line.c_str();
    const char* end = ptr + line.size();

    while (ptr < end) {
        const char* next = std::find(ptr, end, ',');
        double value = 0.0;
        std::from_chars(ptr, next, value);
        arrdata.push_back(value);
        ptr = (next == end) ? end : next + 1;
    }

    return arrdata;
}

vector<double> FiberRO::readLastLineData(const string& filePath) {
    ifstream file(filePath, ios::binary | ios::ate);
    if (!file.is_open()) {
        cerr << "Error: cannot open file " << filePath << endl;
        return {};
    }

    streampos fileSize = file.tellg();
    if (fileSize <= 0) {
        cerr << "Warning: file is empty: " << filePath << endl;
        return {};
    }

    size_t bufferSize = 1024;
    string lastLine;

    while (true) {
        if (bufferSize > static_cast<size_t>(fileSize))
            bufferSize = static_cast<size_t>(fileSize);

        vector<char> buffer(bufferSize + 1, '\0');
        file.seekg(-static_cast<streamoff>(bufferSize), ios::end);
        file.read(buffer.data(), bufferSize);

        char* lastNewline = strrchr(buffer.data(), '\n');

        if (lastNewline) {
            if (*(lastNewline + 1) == '\0') {
                *lastNewline = '\0';
                lastNewline = strrchr(buffer.data(), '\n');
            }

            if (lastNewline)
                lastLine = string(lastNewline + 1);
            else
                lastLine = string(buffer.data());
            break;
        } else if (bufferSize >= static_cast<size_t>(fileSize)) {
            lastLine = string(buffer.data());
            break;
        } else {
            bufferSize *= 2;
        }
    }

    if (!lastLine.empty() && lastLine.back() == '\r')
        lastLine.pop_back();

    vector<double> result = ParseCSVLine(lastLine.c_str());

    if (result.size() > 3) {
        result.erase(result.begin(), result.end() - 3);
    }

    return result;
}


vector<double> FiberRO::ParseCSVLine(const char* lineStart) {
    vector<double> result;
    const char* ptr = lineStart;
    const char* end = lineStart + strlen(lineStart);
    result.reserve(16);

    while (ptr < end) {
        const char* next = find(ptr, end, ',');
        string token(ptr, next);
        try {
            result.push_back(stod(token));
        } catch (...) {
            
        }
        ptr = (next == end) ? end : next + 1;
    }
    return result;
}

VectorXd FiberRO::ReadTheLastRow(int index) {
    SPDLOG_DEBUG("Reading the last row of the file with index {}", index);
    ifstream infile(Outfile);
    
    if (!infile.is_open()) {
        SPDLOG_ERROR("Failed to open file: {}", Outfile);
        throw std::runtime_error("Cannot open file: " + Outfile);
    }

    string line;

    for (int i = 0; i <= index; ++i) {
        if (!std::getline(infile, line)) {
            SPDLOG_ERROR("Failed to read line {} from file {}", i, Outfile);
            throw std::runtime_error("Insufficient lines in file");
        }
    }
    infile.close();
    return ParseCSVLineToVector(line);
}

VectorXd FiberRO::ParseCSVLineToVector(const string& line) {
    size_t columnCount = 1;
    for (char c : line) {
        if (c == ',') ++columnCount;
    }
    
    VectorXd result(columnCount);
    size_t startPos = 0;
    size_t endPos = 0;
    size_t colIndex = 0;
    
    while (colIndex < columnCount) {
        endPos = line.find(',', startPos);
        
        if (endPos == string::npos) {
            result(colIndex) = FastStod(line.substr(startPos));
            break;
        }
        result(colIndex++) = FastStod(line.substr(startPos, endPos - startPos));
        startPos = endPos + 1;
    }
    return result;
}

double FiberRO::FastStod(const string& str) {
    char* endptr;
    double value = strtod(str.c_str(), &endptr);
    
    if (endptr == str.c_str() || *endptr != '\0') {
        SPDLOG_WARN("Invalid numeric value: '{}', using 0.0", str);
        return 0.0;
    }
    return value;
}

MatrixXd FiberRO::readCSV(int row) {
    SPDLOG_DEBUG("Reading the first {} rows of the file", row);
    ifstream infile(Outfile);
    if (!infile.is_open()) {
        SPDLOG_ERROR("Failed to open file: {}", Outfile);
        throw runtime_error("Cannot open file: " + Outfile);
    }

    vector<vector<double>> data;
    data.reserve(row);
    string line;
    int currentRow = 0;
    size_t expectedCols = 0;
    
    while (currentRow < row && getline(infile, line)) {
        if (line.empty()) continue;
        vector<double> rowData;
        if (currentRow == 0) {
            expectedCols = CountColumns(line);
            rowData.reserve(expectedCols);
        } else {
            rowData.reserve(expectedCols);
        }
        ParseCSVLine(line, rowData);
        if (currentRow > 0 && rowData.size() != expectedCols) {
            SPDLOG_WARN("Row {} has {} columns, expected {}", 
                       currentRow, rowData.size(), expectedCols);
        }
        
        data.push_back(move(rowData));
        ++currentRow;
    }
    
    if (data.empty()) {
        SPDLOG_WARN("No data read from file");
        return MatrixXd(0, 0);
    }
    return ConvertToEigenMatrix(data);
}

size_t FiberRO::CountColumns(const string& line) { return count(line.begin(), line.end(), ',') + 1;}

void FiberRO::ParseCSVLine(const string& line, vector<double>& rowData) {
    size_t start = 0;
    size_t end = 0;
    
    while ((end = line.find(',', start)) != string::npos) {
        string_view field(&line[start], end - start);
        if (!field.empty()) {
            rowData.push_back(FastStod(field));
        } else {
            rowData.push_back(0.0);
        }
        start = end + 1;
    }
    
    if (start < line.length()) {
        string_view field(&line[start], line.length() - start);
        if (!field.empty()) {
            rowData.push_back(FastStod(field));
        } else {
            rowData.push_back(0.0);
        }
    }
}

double FiberRO::FastStod(string_view str) {
    char* endptr;
    double value = strtod(str.data(), &endptr);
    
    if (endptr == str.data() || endptr != str.data() + str.length()) {
        SPDLOG_WARN("Invalid numeric value: '{}', using 0.0", str);
        return 0.0;
    }
    return value;
}

MatrixXd FiberRO::ConvertToEigenMatrix(const vector<vector<double>>& data) {
    if (data.empty()) return MatrixXd(0, 0);
    
    const size_t rows = data.size();
    const size_t cols = data[0].size();
    MatrixXd matrix(rows, cols);
    
    for (size_t i = 0; i < rows; ++i) {
        if (data[i].size() != cols) {
            for (size_t j = 0; j < cols; ++j) {
                matrix(i, j) = (j < data[i].size()) ? data[i][j] : 0.0;
            }
        } else {
            Map<const VectorXd> rowMap(data[i].data(), cols);
            matrix.row(i) = rowMap;
        }
    }
    return matrix;
}

vector<double> FiberRO::ReadCSVLine(const string& filename, int lineIndex) {
        vector<double> arrdata;
  
        ifstream infile(filename);
        if (!infile.is_open()) {
            throw std::runtime_error("Could not open file: " + filename);
        }

        string line;
        for (int i = 0; i <= lineIndex; i++) {
            if (!std::getline(infile, line)) {
                throw std::runtime_error("File does not have line " + std::to_string(lineIndex));
            }
        }

        stringstream sin(line);
        string field;
        
        while (getline(sin, field, ',')) {
            try {
                arrdata.push_back(std::stod(field));
            } catch (const std::exception& e) {
                throw std::runtime_error("Invalid number format in file: " + filename);
            }
        }
        return arrdata;
}

vector<double> FiberRO::ReadBottomG() { return ReadCSVLine(fileObject, 1);}

vector<double> FiberRO::ReadPhysical() { return ReadCSVLine(filePhysical, 1);}

vector<double> FiberRO::ReadDelta() {return ReadCSVLine(fileDelta, 1);}

void FiberRO::Output(const MatrixXd &arr, int rr, int ll) {
    SPDLOG_DEBUG("Outputting matrix({},{}) to file with {} rows and {} columns",
                arr.rows(), arr.cols(), rr, ll);
    
    ofstream datafile(Outfile, std::ios::out | std::ios::trunc);
    if (!datafile.is_open()) {
        SPDLOG_ERROR("Failed to open output file: {}", Outfile);
        throw runtime_error("Cannot open output file: " + Outfile);
    }

    const int outputRows = min(static_cast<int>(arr.rows()), rr);
    const int outputCols = min(static_cast<int>(arr.cols()), ll);
    const string zeroRow = CreateZeroRow(ll);
    
    ostringstream lineBuffer;
    lineBuffer.rdbuf()->pubsetbuf(nullptr, 0);    
    for (int i = 0; i < outputRows; ++i) {
        SPDLOG_TRACE("Writing row {}", i);
        
        lineBuffer.str(""); 
        lineBuffer.clear();
        
        for (int j = 0; j < outputCols; ++j) {
            lineBuffer << arr(i, j);
            if (j < outputCols - 1) {
                lineBuffer << ",";
            }
        }
        
        if (outputCols < ll) {
            if (outputCols > 0) lineBuffer << ",";
            for (int j = outputCols; j < ll; ++j) {
                lineBuffer << "0";
                if (j < ll - 1) {
                    lineBuffer << ",";
                }
            }
        }
        datafile << lineBuffer.str() << "\n";
    }
    
    if (rr > outputRows) {
        for (int i = outputRows; i < rr; ++i) {
            datafile << zeroRow << "\n";
        }
    }
    SPDLOG_DEBUG("Successfully wrote {} rows to file", rr);
}

string FiberRO::CreateZeroRow(int cols) {
    if (cols <= 0) return "";
    
    string zeroRow;
    zeroRow.reserve(cols * 2 - 1); 

    for (int j = 0; j < cols; ++j) {
        zeroRow += '0';
        if (j < cols - 1) {
            zeroRow += ',';
        }
    }
    return zeroRow;
}

double FiberRO::flutov(char *filename) {
  double num;
  string s;
  string lastLine;
  ifstream file(filename);
  if (file.is_open()) {
    while (getline(file, s)) {
      lastLine = s;
    }
    file.close();
  } else {}
  try {
    int pos = lastLine.find(' ');
    num = stod(lastLine.substr(pos + 1));
  } catch (const std::exception &e) {}
  return num;
}

void FiberRO::OutTopforce(VectorXd v) {
  // SPDLOG_DEBUG("Outputting the top force to file");
  ofstream outfileTopforce(Topforceout, ios::trunc);
  
  MatrixXd aa(1, 3);
  aa(0, 0) = v(3); // Forcet
  aa(0, 1) = v(4); // Forcen
  aa(0, 2) = v(5); // Forceb
  //////////////////////////////////////////////////////////////////
  MatrixXd tpmat(3, 3);
  tpmat(0, 0) = cos(v(7)) * cos(v(6));
  tpmat(0, 1) = sin(v(7)) * cos(v(6));
  tpmat(0, 2) = -sin(v(6));
  tpmat(1, 0) = -sin(v(7));
  tpmat(1, 1) = cos(v(7));
  
  tpmat(1, 2) = 0;
  tpmat(2, 0) = sin(v(6)) * cos(v(7));
  tpmat(2, 1) = sin(v(6)) * sin(v(7));
  tpmat(2, 2) = cos(v(6));
  //////////////////////////////////////////////////////////////////
  
  MatrixXd bb(1, 3);
//   bb = aa * tpmat.inverse();
  bb = aa * tpmat;
  outfileTopforce << bb;
  outfileTopforce.close();
}

void FiberRO::OutBottomforce(VectorXd v) {
  // SPDLOG_DEBUG("Outputting the bottom force to file");
  ofstream outfileBottomforce(Bottomforceout, ios::trunc);

  MatrixXd aa(1, 3);
  aa(0, 0) = v(TnoV-7); // Ft
  aa(0, 1) = v(TnoV-6); // Fn
  aa(0, 2) = v(TnoV-5); // Fb
  ///////////////////////////////////////////////////////////////////
  MatrixXd tpmat(3, 3);
  tpmat(0, 0) = cos(v(TnoV-3)) * cos(v(TnoV-4));
  tpmat(0, 1) = sin(v(TnoV-3)) * cos(v(TnoV-4));
  tpmat(0, 2) = -sin(v(TnoV-4));
  tpmat(1, 0) = -sin(v(TnoV-3));
  tpmat(1, 1) = cos(v(TnoV-3));
  tpmat(1, 2) = 0;
  tpmat(2, 0) = sin(v(TnoV-4)) * cos(v(TnoV-3));
  tpmat(2, 1) = sin(v(TnoV-4)) * sin(v(TnoV-3));
  tpmat(2, 2) = cos(v(TnoV-4));
  ///////////////////////////////////////////////////////////////////

  MatrixXd bb(1, 3);
//   bb = aa * tpmat.transpose();
  bb = aa * tpmat;
  outfileBottomforce << bb;
  outfileBottomforce.close();
}

vector<double> FiberRO::ReadBottomVel() {
  vector<double> velocityRelative =
      readLastLineData(fileBottomVelocityRelative);
  vector<double> omegaRelative = readLastLineData(fileBottomomegaRelative);
  vector<double> Eulerangle = readLastLineData(fileBottomEulerAngle);
  ////////////////////////////////////////////////////Towingpoint Position
  vector<double> R = {-0.22, 0.0, -0.00497};
  ////////////////////////////////////////////////////Towingpoint Position

  Matrix3x3 E = computeRotationMatrix(Eulerangle);

  vector<double> crossProduct = {
      omegaRelative[1] * R[2] - omegaRelative[2] * R[1],
      omegaRelative[2] * R[0] - omegaRelative[0] * R[2],
      omegaRelative[0] * R[1] - omegaRelative[1] * R[0]};

  vector<double> brrdata(3, 0.0);
  for (size_t i = 0; i < 3; ++i) {
    if (i == 1) {
      brrdata[i] = velocityRelative[i] + crossProduct[i];
    } else {
      brrdata[i] = velocityRelative[i] + crossProduct[i];
    }
  }

  vector<double> arrdata(3, 0.0);
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      arrdata[i] += E[i][j] * brrdata[j];
    }
  }
  // swap(arrdata[1], arrdata[2]);
  // swap(arrdata[0], arrdata[1]);
  return arrdata;
}

Matrix3x3 FiberRO::computeRotationMatrix(const vector<double> &Eulerangle) { // The Rotation Order is XYZ
  Matrix3x3 Rz = {{{cos(Eulerangle[2]), -sin(Eulerangle[2]), 0},
                   {sin(Eulerangle[2]), cos(Eulerangle[2]), 0},
                   {0, 0, 1}}};

  Matrix3x3 Ry = {{{cos(Eulerangle[1]), 0, sin(Eulerangle[1])},
                   {0, 1, 0},
                   {-sin(Eulerangle[1]), 0, cos(Eulerangle[1])}}};

  Matrix3x3 Rx = {{{1, 0, 0},
                   {0, cos(Eulerangle[0]), -sin(Eulerangle[0])},
                   {0, sin(Eulerangle[0]), cos(Eulerangle[0])}}};

  Matrix3x3 RyRz = {};
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      for (int k = 0; k < 3; ++k) {
        RyRz[i][j] += Ry[i][k] * Rz[k][j];
      }
    }
  }

  Matrix3x3 E = {};
  for (int i = 0; i < 3; ++i) {
    for (int j = 0; j < 3; ++j) {
      for (int k = 0; k < 3; ++k) {
        E[i][j] += Rx[i][k] * RyRz[k][j];
      }
    }
  }
  return E;
}