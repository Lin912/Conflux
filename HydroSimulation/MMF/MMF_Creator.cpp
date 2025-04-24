#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

using namespace std;

struct ControlDirect {
    int OFFSET_PROGRAM_STARCCM;
    int OFFSET_PROGRAM_CITRINE;
    char data[1024];
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

//   Initializer
    sharedata -> OFFSET_PROGRAM_STARCCM = 1;
    sharedata -> OFFSET_PROGRAM_CITRINE = 0;





    return 0;
}