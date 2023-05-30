cmake_minimum_required(VERSION 3.22.1)
project(template_project VERSION 0.0.1)

set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -std=c++17 -D _DEBUG -Wall")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -std=c++17 -Wall")
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

file(GLOB_RECURSE SRCS src/*.cpp)

# By default, this CMakeLists file recursively searches the 'src' directory for
# source files. To manually specify the locations of source files, uncomment
# the text below and comment out the line above.

# set(SRCS
# 
#     src/main.cpp
#     src/foo.cpp
#     src/bar.cpp
# )

add_executable(${PROJECT_NAME} ${SRCS})
target_link_libraries(${PROJECT_NAME})
