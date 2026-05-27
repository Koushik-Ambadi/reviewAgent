/* ===========================================================================
 *
 *                CONFIDENTIAL AMERICAN BATTERY SOLUTIONS
 *
 *   This is an unpublished work of authorship, which contains
 *   trade secrets, created in 2025.  American Battery Solutions owns
 *   all rights to this work and intends to maintain it in confidence
 *   to preserve its trade secret status.  American Battery Solutions
 *   reserves the right, under the copyright laws of the United
 *   States or those of any other country that may have jurisdiction,
 *   to protect this work as an unpublished work, in the event of
 *   an inadvertent or deliberate unauthorized publication.
 *   American Battery Solutions also reserves its rights under all copyright
 *   laws to protect this work as a published work, when appropriate.
 *   Those having access to this work may not copy it, use it,
 *   modify it, or disclose the information contained in it without
 *   the written authorization of American Battery Solutions.
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Include Files
 *
 * ========================================================================= */
#include "app.h"
#include "soc.h"

/* ===========================================================================
 *
 *   Private Typedefs
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Private Defines
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Public Data Storage
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Private Data Storage
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Private Macros
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Private Function Prototypes
 *
 * ========================================================================= */
static void main_init (void);

static void main_init (void)
{
    Soc_initialize();
}

/* IMPORTANT: Used for testing build only */
static void main_runtime (void)
{
    static uint32_t dummy = 0;

    (void)dummy;
}

/* ===========================================================================
 *
 *   Name: main
 *
 *   Function:
 *
 *   Inputs:
 *
 *   Outputs:
 *
 *   Side Effects:
 *
 *   Remarks:
 *
 *   Requirements Fulfilled:
 *
 *   Function GUID (from detailed design):
 *
 * ========================================================================= */
int32_t main (void)
{
    main_init();

    for (;;)
    {
        main_runtime();
    }
}

status_t Shunt_getcurrent_ibatt (float32_t * current)
{
    status_t status = ABS_OK;
    return status;
}

status_t Dukosi_get_voltage (Dukosi_Voltage_t * VoltageInfo)
{
    status_t status = ABS_OK;
    return status;
}

status_t Dukosi_get_temperature (Dukosi_Temperature_t * TempInfo, Dukosi_Temptype_t temptype)
{
    status_t status = ABS_OK;
    return status;
}

status_t App_soc_nvm_read (float32_t * initsoc)
{
    status_t status = ABS_OK;
    return status;
}

status_t App_get_battstate (Battsm_State_t * battstate)
{
    status_t status = ABS_OK;
    return status;
}

status_t App_get_init_batt_resttime (uint32_t * initbattresttime)
{
    status_t status = ABS_OK;
    return status;
}

status_t App_get_soc_nvm_importstatus (bool * NVMimportstatus)
{
    status_t status = ABS_OK;
    return status;
}

status_t Dukosi_get_min_max_temperature (Dukosi_Temperature_result_t * min_max_temperature, Dukosi_Temptype_t temptype)
{
    status_t status = ABS_OK;
    return status;
}

status_t Sohc_get_cell_levels (float32_t * cellsohc)
{
    status_t status = ABS_OK;
    return status;
}

status_t App_get_batt_sleeptime (uint32_t * battasleeptime)
{
    status_t status = ABS_OK;
    return status;
}

status_t App_soc_nvm_write (float32_t * socnvm)
{
    status_t status = ABS_OK;
    return status;
}

status_t Dtcmgr_log_fault (Dtcmgr_FaultIndex_t idx, Dtcmgr_FaultStatus_t fltStatus)
{
    status_t status = ABS_OK;
    return status;
}
