set(LIB_NAME s32k344mcal)

add_library(${LIB_NAME} "")

target_compile_definitions(
    ${LIB_NAME}
    PUBLIC
    MCAL_ENABLE_USER_MODE_SUPPORT
    USING_OS_FREERTOS
)

target_link_libraries(${LIB_NAME} PRIVATE os_s32k344)

file(GLOB BOARD_SOURCES "board/*.c")
file(GLOB GENERATE_SOURCES "generate/src/*.c")
file(GLOB RTD_SOURCES "RTD/src/*.c")
file(GLOB STARTUP_SOURCES_C "Project_Settings/Startup_Code/*.c")
file(GLOB STARTUP_SOURCES_S "Project_Settings/Startup_Code/*.s")

target_sources(
    ${LIB_NAME}
    PRIVATE
    ${BOARD_SOURCES}
    ${GENERATE_SOURCES}
    ${RTD_SOURCES}
    ${STARTUP_SOURCES_C}
    ${STARTUP_SOURCES_S}
)

target_include_directories(
    ${LIB_NAME}
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}/mcal-base/header
    ${CMAKE_CURRENT_SOURCE_DIR}/mcal-base/include
    ${CMAKE_CURRENT_SOURCE_DIR}/board
    ${CMAKE_CURRENT_SOURCE_DIR}/generate/include
    ${CMAKE_CURRENT_SOURCE_DIR}/RTD/include
    ${CMAKE_CURRENT_SOURCE_DIR}/Project_Settings/Startup_Code


    $<TARGET_PROPERTY:os_s32k344,INTERFACE_INCLUDE_DIRECTORIES>
)

target_compile_options(${LIB_NAME} PRIVATE -Osize)
