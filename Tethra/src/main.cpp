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
#include "Nums.h"

using namespace std;
namespace fs = std::filesystem;

ControlDirect* g_sharedData = nullptr;

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

  g_sharedData = static_cast<ControlDirect*>(mmap(nullptr, sizeof(ControlDirect), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));
  
  if(g_sharedData == MAP_FAILED){
        perror("Unable to map file to memory");
        close(fd);
        return 1;
    }
    
  while(true){
        while(g_sharedData->OFFSET_PROGRAM_CITRINE == 1){
            SPDLOG_INFO("Data in Tethra");
            
            fiberInstance.Calculation(timeForCitrine);
            logMessage("Processing complete");
            timeForCitrine++;

            g_sharedData->OFFSET_PROGRAM_CITRINE = 0;
            g_sharedData->OFFSET_PROGRAM_STARCCM = 1;
        }

        this_thread::sleep_for(chrono::milliseconds(50));
    }
    
  munmap(g_sharedData, sizeof(ControlDirect));
  close(fd);
  return 0;
}
  
void logMessage(const string &message) { cout << endl << "[LOG]: " << message << endl; }  

