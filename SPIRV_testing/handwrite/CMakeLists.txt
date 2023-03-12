cmake_minimum_required(VERSION 3.1)
project(epic_project_name)

cmake_policy(SET CMP0079 NEW)
#set(CMAKE_C_FLAGS "-I${CMAKE_BINARY_DIR}/SPIRVVM/ -lSPIRVVM") doesn't work

#message(STATUS "dir is ${CMAKE_BINARY_DIR}") debug

# setting variables to reuse paths -- links to original repo
set(SPIRVVM_DIR "/home/kris/repos/SPIRV-VM")
set(SPIRVVM_INC_DIR "${SPIRVVM_DIR}/inc")

add_executable(shader_test shader_test.c)

#configure_file("add_vec3_glsl.frag.spv" "add_vec3_glsl.frag.spv" COPYONLY)
#configure_file("add_vec3_hand.spv" "add_vec3_hand.spv" COPYONLY)
# configure_file("out.spv" "out.spv" COPYONLY)

# https://stackoverflow.com/questions/26807329/no-rule-to-make-target-error-in-cmake-when-linking-to-shared-library
add_library(SPIRVVM SHARED IMPORTED)
set_target_properties(SPIRVVM PROPERTIES IMPORTED_LOCATION ${SPIRVVM_DIR}/libSPIRVVM.a)
target_include_directories(shader_test PRIVATE ${SPIRVVM_INC_DIR})
target_link_libraries(shader_test PRIVATE SPIRVVM)
target_link_libraries(shader_test PRIVATE m)
