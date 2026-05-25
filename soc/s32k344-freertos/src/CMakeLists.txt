add_library(os_s32k344 "")

target_link_libraries(
        os_s32k344
        PRIVATE
)

target_sources(
        os_s32k344
        PRIVATE
        croutine.c
        event_groups.c
        list.c
        queue.c
        stream_buffer.c
        tasks.c
        timers.c

        portable/GHS/ARM_CM7/r0p1/port.c

        freertos_hooks/freertos_hooks.c
)

target_include_directories(
        os_s32k344
        PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/config
        ${CMAKE_CURRENT_SOURCE_DIR}/include
        ${CMAKE_CURRENT_SOURCE_DIR}/portable/GHS/ARM_CM7/r0p1
        ${CMAKE_CURRENT_SOURCE_DIR}/freertos_hooks
)
