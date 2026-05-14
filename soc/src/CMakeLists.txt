set(LIB_NAME soc)

add_library(${LIB_NAME} "")

target_sources(
    ${LIB_NAME}
    PRIVATE
    ${LIB_NAME}.c
    soc_model.c
)

# Eventually use this once we update 'absdef' to enforce strict ISO C99 dialect
target_compile_options(
    ${LIB_NAME} 
    PRIVATE 
    --misra_2012=all --diag_warning=1710
)

target_link_libraries(
    ${LIB_NAME} 
    PRIVATE
    ${SOC_TARGET_LINK_LIBS}
)

target_include_directories(
    ${LIB_NAME}
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    
    # This is to expose the component's configuration header file (i.e. ${LIB_NAME}_cfg.h)
    $<TARGET_PROPERTY:${LIB_NAME}_cfg,INTERFACE_INCLUDE_DIRECTORIES>
    $<TARGET_PROPERTY:absdef,INTERFACE_INCLUDE_DIRECTORIES>
)
