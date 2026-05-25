# CMake Toolchain file for Green Hills Software (GHS) Compiler targeting S32K344

# Specify the system name and processor
set(CMAKE_SYSTEM_NAME Generic)

# Prevent CMake from trying to run the compiler for test programs
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(CMAKE_SYSTEM_PROCESSOR cortex-m7)

# Manually set the compiler and mark it as working
set(CMAKE_ASM_COMPILER_ID "GHS")
set(CMAKE_ASM_COMPILER_WORKS TRUE)

set(GHS_PRIMARY_TARGET "arm_standalone.tgt")
set(GHS_TARGET_PLATFORM "standalone")
set(GHS_TOOLSET_ROOT "C:/ghs")

# Specify the target architecture and options
set(GHS_TARGET_TRIPLET "arm")
set(GHS_CPU_OPTION "-cpu=cortex-m7")
set(GHS_DIAB_OPTIONS "-entry=__start -nosdata -non_shared")

# Global Compiler Flags
set(CMAKE_C_FLAGS
    "-cpu=cortexm7 \
    -keeptempfiles \
    -fpu=vfpv5_d16 \
    -fsingle \
    -thumb \
    --no_commons \
    -MD \
    -preprocess_assembly_files \
    -list \
    --no_slash_comment \
    -C99 \
    --no_exceptions \
    --gnu_asm \
    --unsigned_fields \
    --unsigned_chars \
    --no_short_enum \
    --ghstd=last \
    --prototype_errors \
    -Wimplicit-int \
    --incorrect_pragma_warnings \
    -Wshadow \
    -Wtrigraphs \
    -Wundef \
    -G \
    -dual_debug \
    -Onone"
)

# Global Assembler Flags
set(CMAKE_ASM_FLAGS 
      "-cpu=cortexm7 \
      -fpu=vfpv5_d16 \
      -fsingle \
      -preprocess_assembly_files \
      -list \
      -c"
)

set(CMAKE_EXE_LINKER_FLAGS
    "-g \
    -dwarf2 \
    -Wl,-keep=C40_Ip_AccessCode \
    -map \
    -keepmap \
    -Mn \
    -nostartfiles \
    -nostdlib \
    -larch \
    -lstartup \
    -lansi \
    -lind_sd \
    -L\"C:/ghs/comp_202514/lib/thumb2\" \
    -fsingle"
)

# Global Compile-time definitions
add_compile_definitions(
    ENABLE_FPU
    CPU_S32K344 
    CPU_CORTEX_M7
)

set(CMAKE_ASM_FLAGS_DEBUG "-O0 -g3 -DDEBUG -UNDEBUG")
set(CMAKE_C_FLAGS_DEBUG "-O0 -g3 -DDEBUG -UNDEBUG")
set(CMAKE_CXX_FLAGS_DEBUG "-O0 -g3 -DDEBUG -UNDEBUG")

# can be set to:
#       "Define DNDEBUG"
#       "Undefine DEBUG"
#       "Define DNDEBUG and Undefine DEBUG"
set(CUSTOM_RELEASE_TYPE "Define DNDEBUG and Undefine DEBUG")

if(${CUSTOM_RELEASE_TYPE} STREQUAL "Define DNDEBUG")
# This will define NDEBUG - i.e., #define NDEBUG; NDEBUG is a preprocessor symbol that controls if 'assert' is active or not per C 
#  standard
        set(CMAKE_ASM_FLAGS_RELEASE "-O2 -g3 -DNDEBUG")
        set(CMAKE_C_FLAGS_RELEASE "-O2 -g3 -DNDEBUG")
        set(CMAKE_CXX_FLAGS_RELEASE "-O2 -g3 -DNDEBUG")
elseif(${CUSTOM_RELEASE_TYPE} STREQUAL "Undefine DEBUG")
# This will UNdefine DEBUG - i.e. #undefine DEBUG
        set(CMAKE_ASM_FLAGS_RELEASE "-O2 -g3 -UDEBUG")
        set(CMAKE_C_FLAGS_RELEASE "-O2 -g3 -UDEBUG")
        set(CMAKE_CXX_FLAGS_RELEASE "-O2 -g3 -UDEBUG")
elseif(${CUSTOM_RELEASE_TYPE} STREQUAL "Define DNDEBUG and Undefine DEBUG")
        set(CMAKE_ASM_FLAGS_RELEASE "-O2 -g3 -DNDEBUG -UDEBUG")
        set(CMAKE_C_FLAGS_RELEASE "-O2 -g3 -DNDEBUG -UDEBUG")
        set(CMAKE_CXX_FLAGS_RELEASE "-O2 -g3 -DNDEBUG -UDEBUG")
endif()

# Specify the cross compiler executables
set(CMAKE_C_COMPILER ccarm)
set(CMAKE_CXX_COMPILER c++arm)
set(CMAKE_ASM_COMPILER ccarm)

# Set compiler flags
set(CMAKE_C_FLAGS_INIT "${GHS_CPU_OPTION} -Osize -g")
set(CMAKE_CXX_FLAGS_INIT "${GHS_CPU_OPTION} -Osize -g")
set(CMAKE_ASM_FLAGS_INIT "${GHS_CPU_OPTION} -g")

# Set linker flags
set(CMAKE_EXE_LINKER_FLAGS_INIT "${GHS_DIAB_OPTIONS}")

# adjust the default behavior of the FIND_XXX() commands:
# search programs in the host environment
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)

# search headers and libraries in the target environment
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
