#include "sample.h"

unsigned system_state;

static unsigned read_state(void)
{
    return system_state;
}

unsigned control_step(unsigned request)
{
    unsigned next = read_state();

    if (request > next) {
        next = request;
    }
    system_state = next;
    return next;
}

unsigned duplicate_step(unsigned request)
{
    unsigned next = read_state();

    if (request > next) {
        next = request;
    }
    system_state = next;
    return next;
}
