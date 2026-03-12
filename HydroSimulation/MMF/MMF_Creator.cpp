#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>
#include <cstdint>

using namespace std;

#pragma pack(push, 1)
struct ControlDirect {
    int32_t OFFSET_PROGRAM_STARCCM;
    int32_t OFFSET_PROGRAM_CITRINE;
    
    double forceX;          // 8-15 
    double forceY;          // 16-23 
    double forceZ;          // 24-31 
    
    double vrx;        		// 32-39 
    double vry;             // 40-47 
    double vrz;             // 48-55 
    double omegarx;         // 56-63 
    double omegary;         // 64-71 
    double omegarz;         // 72-79 
    double rx;              // 80-87 
    double ry;              // 88-95 
    double rz;              // 96-103 
    
    char padding[928];
};

int main()  {
    const char* filename  = "ControlDirect_SharedMemory";

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
	
	memset(sharedata, 0, sizeof(ControlDirect));
	
	// Initializer
    sharedata -> OFFSET_PROGRAM_STARCCM = 1;
    sharedata -> OFFSET_PROGRAM_CITRINE = 0;
    
    cout << "[MMF_Creator] Build and Initialzed :)" << endl;
    cout << "Total: " << sizeof(ControlDirect) << " bit" << endl;

    munmap(sharedata, sizeof(ControlDirect));
    close(fd);

    return 0;
}
