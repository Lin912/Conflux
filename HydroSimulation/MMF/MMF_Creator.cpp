#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>
#include <cstdint>

using namespace std;

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

int main()  {
    const char* filename  = "ControlDirect_SharedMemory";

    int fd = open(filename, O_RDWR | O_CREAT, 0600);
    if(fd == -1){
        perror("Can not open ControlDirect file");
        return 1;
    }

    if(ftruncate(fd, sizeof(UnifiedControlDirect)) == -1){
        perror("Can not set the size of ControlDirect file");
        close(fd);
        return 1;
    }

    UnifiedControlDirect* sharedata = static_cast<UnifiedControlDirect*>(
        mmap(nullptr, sizeof(UnifiedControlDirect), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0));

    if(sharedata == MAP_FAILED){
        perror("Unable to map file to memory");
        close(fd);
        return 1;
    }

    memset(sharedata, 0, sizeof(UnifiedControlDirect));

    //Initializer    
    sharedata->FLAG_STARCCM = 1;
    sharedata->FLAG_TETHRA = 0;
    sharedata->FLAG_ROVCTRL = 0;
    sharedata->PADDING_ALIGN = 0; 

    munmap(sharedata, sizeof(UnifiedControlDirect));
    close(fd);

    return 0;
}
