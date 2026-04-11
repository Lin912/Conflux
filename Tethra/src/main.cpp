#include "Fiber.h"
#include <chrono>
#include <fstream>
#include <iostream>
#include <spdlog/spdlog.h>
#include <thread>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <mutex>
#include <condition_variable>
#include <cstdint>
#include "Nums.h"

using namespace std;
namespace fs = std::filesystem;

UnifiedControlDirect* g_sharedData = nullptr;

void logMessage(const string &message);

std::mutex mtx;
std::condition_variable cv;

int main(){
    int timeForCitrine = 0;

    Eigen::initParallel();
    Eigen::setNbThreads(THREADS);

    FiberMain fiberInstance;

    const char* filename = "../../../HydroSimulation/ControlDirect_SharedMemory";
    int fd = open(filename, O_RDWR);
    if(fd == -1){
        perror("Can not open ControlDirect file");
        return 1;
    }

    g_sharedData = static_cast<UnifiedControlDirect*>(
        mmap(nullptr, sizeof(UnifiedControlDirect), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
    if(g_sharedData == MAP_FAILED){
        perror("Unable to map file to memory");
        close(fd);
        return 1;
    }

    SPDLOG_INFO("Tethra CABLE Module Successfully Connected to Shared Memory.");

    while(true){
        if(g_sharedData->FLAG_TETHRA == 1){
            SPDLOG_INFO("Data received from STAR-CCM+, starting Tethra calculation...");

            // ==========================================
            // double current_x = g_sharedData->x;
            // ... fiberInstance ...
            // ==========================================

            fiberInstance.Calculation(timeForCitrine);
            logMessage("Processing complete");
            timeForCitrine++;

            // ==========================================
            // g_sharedData->forceX = calculated_force_x;
            // g_sharedData->forceY = calculated_force_y;
            // g_sharedData->forceZ = calculated_force_z;
            // ==========================================

            g_sharedData->FLAG_ROVCTRL = 1;
            g_sharedData->FLAG_TETHRA = 0;
        }

        this_thread::sleep_for(chrono::milliseconds(1));
    }

    munmap(g_sharedData, sizeof(UnifiedControlDirect));
    close(fd);
    return 0;
}

void logMessage(const string &message) { cout << endl << "[LOG]: " << message << endl; }
