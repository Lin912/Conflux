cmake_minimum_required(VERSION 3.10)

# 设置项目名称
project(Tethra5)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin/exe/)
#message(FATAL_ERROR  ${PROJECT_SOURCE_DIR})
# set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fno-var-tracking-assignments")
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-var-tracking-assignments")

# 设置编译器为g++
set(CMAKE_CXX_COMPILER g++)
# 设置编译器标准为C++20
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 设置优化等级为ofast
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Ofast")

# 添加头文件路径
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

# 查找并包含Eigen库
find_package(Eigen3 REQUIRED)
include_directories(${EIGEN3_INCLUDE_DIR})

# 添加源文件
set(SOURCE_FILES
    src/main.cpp
    src/Add.cpp
    src/BC.cpp
    src/Fiber.cpp
    src/Fx.cpp
    src/Iterator.cpp
    src/Jacobian.cpp
    src/Load.cpp
    src/MNQ.cpp
    src/ReadOut.cpp
    src/ParaReader.cpp
)

# 添加可执行文件
add_executable(Tethra5 ${SOURCE_FILES})

target_compile_definitions(Tethra5 PRIVATE SPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_TRACE)
# 链接Eigen库
target_link_libraries(Tethra5 Eigen3::Eigen spdlog::spdlog_header_only)

# 设置构建类型为 Debug
#set(CMAKE_BUILD_TYPE Debug)

# 明确添加调试选项（适用于手动覆盖默认配置）
#set(CMAKE_CXX_FLAGS_DEBUG "-g -O0")
#set(CMAKE_C_FLAGS_DEBUG "-g -O0")

if(NOT TARGET spdlog)
    # Stand-alone build
    find_package(spdlog REQUIRED)
endif()
# target_link_libraries(Tethra5 PRIVATE spdlog::spdlog_header_only)
