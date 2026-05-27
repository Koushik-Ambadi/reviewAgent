#ifndef APP_H
#define APP_H

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
 *  Include Files
 *
 * ========================================================================= */
#include "Platform_Types.h"
#include "abs_sysdefs.h"
#include "abs_typedefs.h"

/* Global cal/config parameters */
#define DUKOSI_NUMBER_OF_CELLS (195u)
#define ABS_AH_TO_COULOMB      (3600.0f)
#define ABS_SEC_TO_MILLISEC    (1000.0f)

/* ===========================================================================
 *
 *  Extern Support
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *  Public Typedefs
 *
 * ========================================================================= */
typedef enum
{
    DUKOSI_DATA_INIT,
    DUKOSI_DATA_VALID,
    DUKOSI_DATA_INVALID
} Dukosi_Validity_t;

typedef struct
{
    uint16_t          MeDukosi_nu_cell_ID;
    float32_t         MeDukosi_V_voltage;
    Dukosi_Validity_t MeDukosi_nu_validity;
} Dukosi_Voltage_t;

typedef enum
{
    DUKOSI_TEMP1,
    DUKOSI_TEMP2
} Dukosi_Temptype_t;

typedef struct
{
    uint16_t          MeDukosi_nu_cell_ID;
    float32_t         MeDukosi_degC_temperature;
    Dukosi_Validity_t MeDukosi_nu_validity;
} Dukosi_Temperature_t;

typedef struct
{
    uint16_t  MeDukosi_nu_min_cell_ID;
    uint16_t  MeDukosi_nu_max_cell_ID;
    float32_t MeDukosi_degC_min_temperature;
    float32_t MeDukosi_degC_max_temperature;
} Dukosi_Temperature_result_t;

/* BMS State Enum */
typedef enum
{
    BATTSM_STATE_STANDBY_INIT = 0, /* Default value */
    BATTSM_STATE_STANDBY_NOT_READY,
    BATTSM_STATE_STANDBY_READY,
    BATTSM_STATE_PREPARE_BUS_PRECHG,
    BATTSM_STATE_PREPARE_BUS_EXT_ISOLATION_CHK,
    BATTSM_STATE_DRIVE,
    BATTSM_STATE_CHARGE,
    BATTSM_STATE_SUPPORT,
    BATTSM_STATE_DSNG_BUS_WAIT_FOR_CHK,
    BATTSM_STATE_DSNG_BUS_CNTC_WLD_CHK,
    BATTSM_STATE_FASTCHARGE
} Battsm_State_t;

/* List of Faults */
typedef enum
{
    DTCMGR_FAULT_1,
    DTCMGR_FAULT_2,
    DTCMGR_NEG_DC_CON_STUCK_OPEN,
    DTCMGR_POS_DC_CON_STUCK_OPEN,
    DTCMGR_NEG_DC_CON_WELDED,
    DTCMGR_POS_DC_CON_WELDED,
    DTCMGR_PRECHARGE_TIMEOUT,
    DTCMGR_PRECHARGE_OVERCURRENT,
    DTCMGR_PRECHARGE_FAIL_CONTACTOR,
    DTCMGR_PRECHARGE_FAIL_RESISTOR,
    DTCMGR_UNINTENDED_OPEN_CONTACTOR,
    DTCMGR_POWER_LIMIT_FAULT,
    DTCMGR_LOWER_SOE_FAULT,
    DTCMGR_PACK_SOHC_FAULT,
    DTCMGR_PACK_SOHR_FAULT,
    DTCMGR_LOWER_SOC_FAULT,
    /* Total DTC Count - Do not modify */
    DTCMGR_FAULT_TOTAL
} Dtcmgr_FaultIndex_t;

/* Fault Status */
typedef enum
{
    DTCMGR_FAULT_UNKNOWN,
    DTCMGR_FAULT_CLR,
    DTCMGR_FAULT_SET
} Dtcmgr_FaultStatus_t;

/* ===========================================================================
 *
 *   Public Defines
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Public Macros
 *
 * ========================================================================= */

/* ===========================================================================
 *
 *   Public Function Prototypes
 *
 * ========================================================================= */

status_t Dukosi_get_temperature (Dukosi_Temperature_t * TempInfo, Dukosi_Temptype_t temptype);
status_t Dukosi_get_voltage (Dukosi_Voltage_t * Voltage_info);
status_t Shunt_getcurrent_ibatt (float32_t * current);
status_t App_soc_nvm_read (float32_t * initsoc);
status_t App_get_battstate (Battsm_State_t * battstate);
status_t App_get_init_batt_resttime (uint32_t * initbattresttime);
status_t App_get_soc_nvm_importstatus (bool * NVMimportstatus);
status_t Dukosi_get_min_max_temperature (Dukosi_Temperature_result_t * min_max_temperature, Dukosi_Temptype_t temptype);
status_t Sohc_get_cell_levels (float32_t * cellsohc);
status_t App_get_batt_sleeptime (uint32_t * battasleeptime);
status_t App_soc_nvm_write (float32_t * socnvm);
status_t Dtcmgr_log_fault (Dtcmgr_FaultIndex_t idx, Dtcmgr_FaultStatus_t fltStatus);

#endif /* ====== End of file APP_H ====================================== */
