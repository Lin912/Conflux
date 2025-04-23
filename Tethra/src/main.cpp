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

using namespace std;
namespace fs = std::filesystem;

struct ControlDirect
{
  int OFFSET_PROGRAM_STARCCM;
  int OFFSET_PROGRAM_CITRINE;
  char data[1024];
};
void logMessage(const string &message);

std::mutex mtx;
std::condition_variable cv;

int main(){
  int timeForCitrine = 2000;
  FiberMain fiberInstance;

  const char* filename = "../../../HydroSimulation/ControlDirect_SharedMemory";
  
  int fd = open(filename, O_RDWR | O_CREAT, 0600);
  if(fd == -1){
    perror("Can not open ControlDirect file");
    return 1;
  }

  if(ftruncate(fd, sizeof(ControlDirect)) == -1){
    perror("Can not set the sizof ControlDirect file");
    close(fd);
    return 1;
  }

  ControlDirect* sharedata = static_cast<ControlDirect*>(mmap(nullptr, sizeof(ControlDirect), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));

  if(sharedata == MAP_FAILED){
    perror("Unable to map file to memory");
    close(fd);
    return 1;
  }

  //Initializer
  // sharedata -> OFFSET_PROGRAM_STARCCM = 1;
  // sharedata -> OFFSET_PROGRAM_CITRINE = 0;


  while(true){
    // std::unique_lock<std::mutex> lock(mtx);//PorcessLOCK Off

    while(sharedata -> OFFSET_PROGRAM_CITRINE == 0){
      this_thread::sleep_for(chrono::milliseconds(10));

      SPDLOG_INFO("Data in STAR-CCM+");
      // cv.wait(lock);
    }


    SPDLOG_INFO("Data in Tethra");
    fiberInstance.Calculation(timeForCitrine);
    logMessage("Processing complete");
    timeForCitrine++;

    sharedata -> OFFSET_PROGRAM_CITRINE = 0;
    sharedata -> OFFSET_PROGRAM_STARCCM = 1;

    // cv.notify_all();
  }


  munmap(sharedata, sizeof(ControlDirect));
  close(fd);

  return 0;
}


void logMessage(const string &message) { cout << endl << "[LOG]: " << message << endl; }

