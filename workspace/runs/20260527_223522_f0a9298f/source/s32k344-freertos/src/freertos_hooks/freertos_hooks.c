#include "freertos_hooks.h"

/* Only define these if the kernel is NOT going to provide them. */
#if (configSUPPORT_STATIC_ALLOCATION == 1) && ((configKERNEL_PROVIDED_STATIC_MEMORY == 0) || (portUSING_MPU_WRAPPERS != 0))

/* ------- Idle task memory ------- */
static StaticTask_t xIdleTaskTCB;
static StackType_t  xIdleStack[configMINIMAL_STACK_SIZE];

void vApplicationGetIdleTaskMemory (StaticTask_t ** ppxIdleTaskTCBBuffer, StackType_t ** ppxIdleTaskStackBuffer,
                                    uint32_t * pulIdleTaskStackSize)
{
    *ppxIdleTaskTCBBuffer   = &xIdleTaskTCB;
    *ppxIdleTaskStackBuffer = xIdleStack;
    *pulIdleTaskStackSize   = (uint32_t)configMINIMAL_STACK_SIZE;
}

    #if (configUSE_TIMERS == 1)
/* ------- Timer task memory ------- */
static StaticTask_t xTimerTaskTCB;
static StackType_t  xTimerStack[configTIMER_TASK_STACK_DEPTH];

void vApplicationGetTimerTaskMemory (StaticTask_t ** ppxTimerTaskTCBBuffer, StackType_t ** ppxTimerTaskStackBuffer,
                                     uint32_t * pulTimerTaskStackSize)
{
    *ppxTimerTaskTCBBuffer   = &xTimerTaskTCB;
    *ppxTimerTaskStackBuffer = xTimerStack;
    *pulTimerTaskStackSize   = (uint32_t)configTIMER_TASK_STACK_DEPTH;
}
    #endif /* configUSE_TIMERS */

#endif /* guards against kernel-provided definitions */
