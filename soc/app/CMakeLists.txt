set(LIB_NAME app)

add_library(${LIB_NAME} "")

target_sources(
    ${LIB_NAME}
    PRIVATE
    ${LIB_NAME}.c
)

target_link_libraries(
    ${LIB_NAME} 
    PRIVATE
    ${APP_TARGET_LINK_LIBS}
)

target_include_directories(
    ${LIB_NAME}
    PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)
