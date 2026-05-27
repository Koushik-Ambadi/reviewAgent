add_library(soc_cfg INTERFACE)

target_include_directories(
        soc_cfg
        INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}
        
    # Add application dependency components
    $<TARGET_PROPERTY:app,INTERFACE_INCLUDE_DIRECTORIES>
)

# Eventually use this once we update 'absdef' to enforce strict ISO C99 dialect
#target_compile_options(${LIB_NAME} PRIVATE --misra_2012=all)
