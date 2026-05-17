#ifndef SOC_CFG_H
#define SOC_CFG_H

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

#define SOC_NUM_OF_CELLS_I32  DUKOSI_NUMBER_OF_CELLS
#define SOC_CELLS_IN_PARALLEL (1u)

#define SOC_GET_CURRENT                  Shunt_getcurrent_ibatt
#define SOC_GET_NVM_IMPORT_STATUS        App_get_soc_nvm_importstatus
#define SOC_GET_CELL_VOLTAGES            Dukosi_get_voltage
#define SOC_GET_CELL_TEMPERATURES        Dukosi_get_temperature
#define SOC_NVM_READ                     App_soc_nvm_read
#define SOC_GET_REST_TIME                App_get_init_batt_resttime
#define SOC_GET_BMS_MODE                 App_get_battstate
#define SOC_GET_MIN_MAX_CELL_TEMPERATURE Dukosi_get_min_max_temperature
#define SOC_GET_CELL_SOHC_LEVELS         Sohc_get_cell_levels
#define SOC_GET_BATT_ASLEEP_TIME         App_get_batt_sleeptime
#define SOC_NVM_WRITE                    App_soc_nvm_write
#define SOC_GET_LOG_FAULT                Dtcmgr_log_fault

#define SOC_BATSM_DT           Battsm_State_t
#define SOC_DUKOSI_VOLT_DT     Dukosi_Voltage_t
#define SOC_DUKOSI_TEMP_DT     Dukosi_Temperature_t
#define SOC_DUKOSI_TEMP_RES_DT Dukosi_Temperature_result_t

#endif /* SOC_CFG_H */
