# Toolchain File for the PowerPC GCC C/C++ Compiler

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_SYSTEM_PROCESSOR powerpc-eabivle)

# Global Compiler Flags
set(CMAKE_C_FLAGS
    "-Wall \
    -Wextra \
    -Wno-unknown-pragmas \
    -fmessage-length=0 \
    -fstrict-volatile-bitfields \
    -ffunction-sections \
    -fdata-sections \
    -mcpu=e200z4 \
    -mbig \
    -mvle \
    -mregnames \
    -mhard-float \
    -std=c99 \
    -v"
)

# Global Assembler Flags
set(CMAKE_ASM_FLAGS 
      "-x assembler-with-cpp \
      -mcpu=e200z4 \
      -mbig \
      -mvle \
      -mregnames"
)

#Linker file.
add_link_options(
  -Wl,-Map=${PROJECT_BINARY_DIR}/${CMAKE_PROJECT_NAME}.map
  -Xlinker --gc-sections
  -mcpu=e200z4
  -mhard-float
)

# Global Compile-time definitions
add_compile_definitions(
        CPU_MPC5744P
        GCC
)

SET(CMAKE_ASM_FLAGS_DEBUG "-O0 -g3 -DDEBUG -UNDEBUG")
SET(CMAKE_C_FLAGS_DEBUG "-O0 -g3 -DDEBUG -UNDEBUG")
SET(CMAKE_CXX_FLAGS_DEBUG "-O0 -g3 -DDEBUG -UNDEBUG")

# can be set to:
#       "Define DNDEBUG"
#       "Undefine DEBUG"
#       "Define DNDEBUG and Undefine DEBUG"
SET(CUSTOM_RELEASE_TYPE "Define DNDEBUG and Undefine DEBUG")

if(${CUSTOM_RELEASE_TYPE} STREQUAL "Define DNDEBUG")
# This will define NDEBUG - i.e., #define NDEBUG; NDEBUG is a preprocessor symbol that controls if 'assert' is active or not per C 
#  standard
        SET(CMAKE_ASM_FLAGS_RELEASE "-O2 -g3 -DNDEBUG")
        SET(CMAKE_C_FLAGS_RELEASE "-O2 -g3 -DNDEBUG")
        SET(CMAKE_CXX_FLAGS_RELEASE "-O2 -g3 -DNDEBUG")
elseif(${CUSTOM_RELEASE_TYPE} STREQUAL "Undefine DEBUG")
# This will UNdefine DEBUG - i.e. #undefine DEBUG
        SET(CMAKE_ASM_FLAGS_RELEASE "-O2 -g3 -UDEBUG")
        SET(CMAKE_C_FLAGS_RELEASE "-O2 -g3 -UDEBUG")
        SET(CMAKE_CXX_FLAGS_RELEASE "-O2 -g3 -UDEBUG")
elseif(${CUSTOM_RELEASE_TYPE} STREQUAL "Define DNDEBUG and Undefine DEBUG")
        SET(CMAKE_ASM_FLAGS_RELEASE "-O2 -g3 -DNDEBUG -UDEBUG")
        SET(CMAKE_C_FLAGS_RELEASE "-O2 -g3 -DNDEBUG -UDEBUG")
        SET(CMAKE_CXX_FLAGS_RELEASE "-O2 -g3 -DNDEBUG -UDEBUG")
endif()

# CMake requires individual variables for the C Compiler, C++ Compiler and Assembler
set(CMAKE_C_COMPILER    ${CMAKE_SYSTEM_PROCESSOR}-gcc.exe)
set(CMAKE_CXX_COMPILER  ${CMAKE_SYSTEM_PROCESSOR}-g++.exe)
set(CMAKE_ASM_COMPILER  ${CMAKE_SYSTEM_PROCESSOR}-gcc.exe)

# adjust the default behavior of the FIND_XXX() commands:
# search programs in the host environment
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# search headers and libraries in the target environment
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
