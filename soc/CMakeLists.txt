# ensure cmake version
cmake_minimum_required(VERSION 3.12 FATAL_ERROR)

set(PROJECT_NAME "soc-component")

# Need to set path to linker script for toolchain file to work
set(LINKER_SCRIPT_PATH "${CMAKE_SOURCE_DIR}/s32k344-mcal/src/Project_Settings/Linker_files/linker_flash_s32k344.ld")

#set(TOOLCHAIN_FILE_PATH "${CMAKE_SOURCE_DIR}/absdef/toolchain_cfg/s32k344_ghs_toolchain.cmake")
#set(CMAKE_TOOLCHAIN_FILE ${TOOLCHAIN_FILE_PATH})

# MCU information
project(${PROJECT_NAME}
        VERSION 0.0.0.1
        LANGUAGES C ASM
)

# Create executable binary and link libraries
set(EXECUTABLE_NAME "${PROJECT_NAME}.elf")

add_executable(${EXECUTABLE_NAME} "")

# Set 'USING_OS_X' to TRUE or FALSE depending on if project is using an OS that integrates into the RTD such as FreeRTOS
set(USING_OS_X TRUE)

# Add necessary libraries to build this component locally
set(SOC_TARGET_LINK_LIBS 
        soc_cfg  
        absdef
        s32k344mcal      
)
set(SOC_CFG_TARGET_LINK_LIBS
        app
)
set(APP_TARGET_LINK_LIBS 
        soc 
        absdef
        s32k344mcal      
)

# Add subdirectories that are configured (i.e., where other CMakeLists.txt files are located)
add_subdirectory(src src)
add_subdirectory(app app)
add_subdirectory(absdef/src absdef)
add_subdirectory(bs_cfg/soc_cfg bs_cfg/soc_cfg)
add_subdirectory(s32k344-mcal/src s32k344-mcal/src)
add_subdirectory(s32k344-freertos/src s32k344-freertos/src)

target_link_options(
        ${EXECUTABLE_NAME}
        PRIVATE
        "-T ${LINKER_SCRIPT_PATH}"
        #-L ${STD_LIB_DIR}
        "-e Reset_Handler"
        "-u VTABLE"
        "-hex=app.hex"
        "-lmath_fp"
        "-lsys"
)

target_link_libraries(
        ${EXECUTABLE_NAME} 
        PRIVATE
        soc
        s32k344mcal
)

target_sources(
        ${EXECUTABLE_NAME}
        PRIVATE
        app/app.c
)

target_include_directories(
    ${EXECUTABLE_NAME}
    PUBLIC
    ${CMAKE_SOURCE_DIR}/app
)

# Eventually use this once we update 'absdef' to enforce strict ISO C99 dialect
#target_compile_options(${EXECUTABLE_NAME} PRIVATE --misra_2012=all)
