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

#include "soc.h"
#include "soc_model.h"

#include <string.h>

static float32_t              VaSoc_frc_cellStateOfCharge[SOC_NUM_OF_CELLS];
static float32_t              VaSoc_frc_cellStateOfChargeCc[SOC_NUM_OF_CELLS];
static float32_t              VaSoc_frc_cellStateOfChargeOcv[SOC_NUM_OF_CELLS];
static float32_t              VaSoc_ms_tauDepolarization[SOC_NUM_OF_CELLS];
static float32_t              VaSoc_frc_cellStateOfHealth[SOC_NUM_OF_CELLS];
static uint32_t               VeSoc_ms_batteryAsleepTime;
static float32_t              NaSoc_frc_initialStateOfCharge[SOC_NUM_OF_CELLS];
static SOC_BATSM_DT           VeSoc_nu_batteryState;
static float32_t              VeSoc_A_batteryCurrent;
static bool                   NeSoc_bi_nvmImportStatus;
static uint32_t               VeSoc_ms_batteryRestTime;
static uint32_t               NeSoc_ms_initBatteryRestTime;
static Soc_State_t            VeSoc_nu_stateOfChargeState;
static float32_t              VeSoc_frc_packStateOfCharge;
static float32_t              VeSoc_frc_userStateOfCharge;
static bool                   VeSoc_bi_resetStateOfCharge;
static float32_t              VeSoc_frc_minimumStateOfCharge;
static float32_t              VeSoc_frc_maximumStateOfCharge;
static SOC_DUKOSI_VOLT_DT     VsSoc_V_cellVoltage[SOC_NUM_OF_CELLS];
static SOC_DUKOSI_TEMP_DT     VsSoc_degC_cellTemperature[SOC_NUM_OF_CELLS];
static SOC_DUKOSI_TEMP_RES_DT VsSoc_degC_minMaxCellTemp;
static bool                   VeSoc_bi_lowerStateOfChargeFlt;

/*Model Inputs and Outputs*/
static void Soc_read_inputs (void);
static void Soc_read_outputs (void);

void Soc_initialize (void)
{
    /** Call the Model Initialization task **/
    Soc_init();
}

void Soc_tick (void)
{
    /**Read Inputs **/
    Soc_read_inputs();

    /**Periodic Model Task **/
    Soc_task();

    /**Read Outputs **/
    Soc_read_outputs();
}

static void Soc_read_inputs (void)
{
    int32_t cell_idx = 0;

    if (ABS_OK == SOC_GET_NVM_IMPORT_STATUS(&NeSoc_bi_nvmImportStatus))
    {
        VeSoc_bi_nvmImportStatus = NeSoc_bi_nvmImportStatus;
    }
    else
    {
        VeSoc_bi_nvmImportStatus = FALSE;
    }

    if (ABS_OK == SOC_NVM_READ(&NaSoc_frc_initialStateOfCharge[0]))
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_frc_initialCellSoc[cell_idx] = NaSoc_frc_initialStateOfCharge[cell_idx];
        }
    }
    else
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_frc_initialCellSoc[cell_idx] = 0.0f;
        }
    }

    if (ABS_OK == SOC_GET_CELL_VOLTAGES(&VsSoc_V_cellVoltage[0]))
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_V_cellVolt[cell_idx]      = VsSoc_V_cellVoltage[cell_idx].MeDukosi_V_voltage;
            VaSoc_nu_cellVoltVldt[cell_idx] = VsSoc_V_cellVoltage[cell_idx].MeDukosi_nu_validity;
        }
    }
    else
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_V_cellVolt[cell_idx]      = 0.0f;
            VaSoc_nu_cellVoltVldt[cell_idx] = DUKOSI_DATA_INVALID;
        }
    }

    if (ABS_OK == SOC_GET_CELL_TEMPERATURES(&VsSoc_degC_cellTemperature[0], DUKOSI_TEMP1))
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_degC_cellTmp[cell_idx]   = VsSoc_degC_cellTemperature[cell_idx].MeDukosi_degC_temperature;
            VaSoc_nu_cellTmpVldt[cell_idx] = VsSoc_degC_cellTemperature[cell_idx].MeDukosi_nu_validity;
        }
    }
    else
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_degC_cellTmp[cell_idx]   = 0.0f;
            VaSoc_nu_cellTmpVldt[cell_idx] = DUKOSI_DATA_INVALID;
        }
    }

    if (ABS_OK == SOC_GET_CELL_SOHC_LEVELS(&VaSoc_frc_cellStateOfHealth[0]))
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_frc_cellSohc[cell_idx] = VaSoc_frc_cellStateOfHealth[cell_idx];
        }
    }
    else
    {
        for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
        {
            VaSoc_frc_cellSohc[cell_idx] = 0.0f;
        }
    }

    if (ABS_OK == SOC_GET_REST_TIME(&NeSoc_ms_initBatteryRestTime))
    {
        VeSoc_ms_initialBattRestTime = NeSoc_ms_initBatteryRestTime;
    }
    else
    {
        VeSoc_ms_initialBattRestTime = 0u;
    }

    if (ABS_OK == SOC_GET_CURRENT(&VeSoc_A_batteryCurrent))
    {
        VeSoc_A_battCur = VeSoc_A_batteryCurrent;
    }
    else
    {
        VeSoc_A_battCur = 0.0f;
    }

    if (ABS_OK == SOC_GET_BMS_MODE(&VeSoc_nu_batteryState))
    {
        VeBattsm_nu_battState = VeSoc_nu_batteryState;
    }
    else
    {
        VeBattsm_nu_battState = BATTSM_STATE_STANDBY_INIT;
    }

    if (ABS_OK == SOC_GET_MIN_MAX_CELL_TEMPERATURE(&VsSoc_degC_minMaxCellTemp, DUKOSI_TEMP1))
    {
        VeSoc_degC_minCellTmp = VsSoc_degC_minMaxCellTemp.MeDukosi_degC_min_temperature;
        VeSoc_degC_maxCellTmp = VsSoc_degC_minMaxCellTemp.MeDukosi_degC_max_temperature;
    }
    else
    {
        VeSoc_degC_minCellTmp = 0.0f;
        VeSoc_degC_maxCellTmp = 0.0f;
    }

    if (ABS_OK == SOC_GET_BATT_ASLEEP_TIME(&VeSoc_ms_batteryAsleepTime))
    {
        VeSoc_ms_battAsleepTime = VeSoc_ms_batteryAsleepTime;
    }
    else
    {
        VeSoc_ms_battAsleepTime = 0u;
    }

    VeSoc_bi_socReset = VeSoc_bi_resetStateOfCharge;
}

static void Soc_read_outputs (void)
{
    int32_t cell_idx = 0;

    for (cell_idx = 0; cell_idx < SOC_NUM_OF_CELLS; cell_idx++)
    {
        VaSoc_frc_cellStateOfCharge[cell_idx]    = VaSoc_frc_cellSoc[cell_idx];
        VaSoc_frc_cellStateOfChargeCc[cell_idx]  = VaSoc_frc_cellSocCc[cell_idx];
        VaSoc_frc_cellStateOfChargeOcv[cell_idx] = VaSoc_frc_cellSocOcv[cell_idx];
        VaSoc_ms_tauDepolarization[cell_idx]     = VaSoc_ms_tauDepolar[cell_idx];
    }

    VeSoc_ms_batteryRestTime       = VeSoc_ms_battRestTime;
    VeSoc_nu_stateOfChargeState    = VeSoc_nu_socState;
    VeSoc_frc_packStateOfCharge    = VeSoc_frc_packSoc;
    VeSoc_frc_userStateOfCharge    = VeSoc_frc_userSoc;
    VeSoc_frc_maximumStateOfCharge = VeSoc_frc_maxCellSoc;
    VeSoc_frc_minimumStateOfCharge = VeSoc_frc_minCellSoc;
    VeSoc_bi_lowerStateOfChargeFlt = VeSoc_bi_lowSocFault;

    (void)SOC_NVM_WRITE(&VaSoc_frc_cellStateOfCharge[0]);

    if (FALSE != VeSoc_bi_lowerStateOfChargeFlt)
    {
        (void)SOC_GET_LOG_FAULT(DTCMGR_LOWER_SOC_FAULT, DTCMGR_FAULT_SET);
    }
    else
    {
        (void)SOC_GET_LOG_FAULT(DTCMGR_LOWER_SOC_FAULT, DTCMGR_FAULT_CLR);
    }
}

status_t Soc_get_batt_resttime (uint32_t * battresttime)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != battresttime)
    {
        *battresttime = VeSoc_ms_batteryRestTime;
        status        = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_tau_depolar (float32_t * taudepolar)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != taudepolar)
    {
        (void)memcpy(taudepolar, VaSoc_ms_tauDepolarization, sizeof(VaSoc_ms_tauDepolarization));
        status = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_state (Soc_State_t * socstate)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != socstate)
    {
        *socstate = VeSoc_nu_stateOfChargeState;
        status    = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_pack_level (float32_t * packsoc)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != packsoc)
    {
        *packsoc = VeSoc_frc_packStateOfCharge;
        status   = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_user_level (float32_t * usersoc)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != usersoc)
    {
        *usersoc = VeSoc_frc_userStateOfCharge;
        status   = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_min (float32_t * minsoc)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != minsoc)
    {
        *minsoc = VeSoc_frc_minimumStateOfCharge;
        status  = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_max (float32_t * maxsoc)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != maxsoc)
    {
        *maxsoc = VeSoc_frc_maximumStateOfCharge;
        status  = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_reset (bool resetsoc)
{
    VeSoc_bi_resetStateOfCharge =  resetsoc;
    return ABS_OK;
}

status_t Soc_get_cell_levels (float32_t * cellsoc)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != cellsoc)
    {
        (void)memcpy(cellsoc, VaSoc_frc_cellStateOfCharge, sizeof(VaSoc_frc_cellStateOfCharge));
        status = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_cell_cc_levels (float32_t * cellsoccc)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != cellsoccc)
    {
        (void)memcpy(cellsoccc, VaSoc_frc_cellStateOfChargeCc, sizeof(VaSoc_frc_cellStateOfChargeCc));
        status = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}

status_t Soc_get_cell_ocv_levels (float32_t * cellsococv)
{
    status_t status = ABS_PARAM_ERR;
    if (NULL != cellsococv)
    {
        (void)memcpy(cellsococv, VaSoc_frc_cellStateOfChargeOcv, sizeof(VaSoc_frc_cellStateOfChargeOcv));
        status = ABS_OK;
    }
    else
    {
        status = ABS_PARAM_ERR;
    }
    return status;
}
