#include <sys/mman.h>
#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

struct SharedData {
    int OFFSET_PROGRAM_STARCCM;
    int OFFSET_PROGRAM_CITRINE;
    char data[1024];
};

int main() {
    const char* filename = "ControlDirect_SharedMemory";
    int fd = open(filename, O_RDONLY);
    if (fd == -1) {
        perror("can not open file");
        return 1;
    }

    // 映射文件到内存
    SharedData* sharedData = static_cast<SharedData*>(mmap(
        nullptr, sizeof(SharedData), PROT_READ, MAP_SHARED, fd, 0
    ));
    if (sharedData == MAP_FAILED) {
        perror("can not catch memory");
        close(fd);
        return 1;
    }

    // 打印共享内存中的内容
    std::cout << "STARCCM_turn: " << sharedData->OFFSET_PROGRAM_STARCCM << std::endl;
    std::cout << "CITRINE_turn: " << sharedData->OFFSET_PROGRAM_CITRINE << std::endl;
    std::cout << "data: " << sharedData->data << std::endl;

    // sharedData -> OFFSET_PROGRAM_CITRINE = 0;
    // sharedData -> OFFSET_PROGRAM_STARCCM = 1;

    // 清理资源
    munmap(sharedData, sizeof(SharedData));
    close(fd);

    return 0;
}