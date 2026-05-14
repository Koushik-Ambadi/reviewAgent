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

#include "soc_model.h"
#include "Platform_Types.h"
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include "soc.h"
#include <string.h>

/* Named constants for Chart: '<S4>/SOC_StateMachine_Chart' */
#define soc_IN_CORRECTION_ON_WAKE_STATE ((uint8_t)1U)
#define soc_IN_INIT_STATE              ((uint8_t)2U)
#define soc_IN_NORMAL_STATE            ((uint8_t)3U)
#define soc_IN_RESET_STATE             ((uint8_t)4U)

/* Exported block signals */
bool VeSoc_bi_nvmImportStatus;         /* '<Root>/VeSoc_bi_nvmImportStatus'
                                        * NVM import status is successfull or not
                                        */
float32_t VeSoc_A_battCur;             /* '<Root>/VeSoc_A_battCur'
                                        * Battery current input
                                        */
float32_t VaSoc_frc_initialCellSoc[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_frc_initialCellSoc'
                                                      * SOC stored in NVM
                                                      */
float32_t VaSoc_V_cellVolt[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_V_cellVolt'
                                              * Cell voltage input
                                              */
float32_t VaSoc_degC_cellTmp[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_degC_cellTmp'
                                                * Cell temperature
                                                */
float32_t VeSoc_degC_minCellTmp;       /* '<Root>/VeSoc_degC_minCellTmp'
                                        * Minimum cell temperature
                                        */
float32_t VeSoc_degC_maxCellTmp;       /* '<Root>/VeSoc_degC_maxCellTmp'
                                        * Maximum cell temperature
                                        */
uint32_t VeSoc_ms_battAsleepTime;      /* '<Root>/VeSoc_ms_battAsleepTime'
                                        * Battery Asleep time calculated by RTC
                                        */
uint32_t VeSoc_ms_initialBattRestTime; /* '<Root>/VeSoc_ms_initialBattRestTime'
                                        * Battery rest time stored in NVM used for OCV wake on correction
                                        */
float32_t VaSoc_frc_cellSohc[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_frc_cellSohc'
                                                * Cell SOHC
                                                */
Battsm_State_t VeBattsm_nu_battState;  /* '<Root>/VeBattsm_nu_battState' */
Dukosi_Validity_t VaSoc_nu_cellVoltVldt[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_nu_cellVoltVldt' */
Dukosi_Validity_t VaSoc_nu_cellTmpVldt[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_nu_cellTmpVldt' */
bool VeSoc_bi_socReset;                /* '<Root>/VeSoc_bi_socReset' */
uint32_t VeSoc_ms_battRestTime;        /* '<S3>/Switch2'
                                        * Calculated battery rest time output
                                        */
float32_t VaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS];/* '<S3>/Switch9' */
float32_t VaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS];/* '<S3>/Switch8' */
float32_t VaSoc_frc_cellSoc[SOC_NUM_OF_CELLS];/* '<S3>/Switch'
                                               * Calculated cell level SOC
                                               */
float32_t VeSoc_frc_userSoc;           /* '<S22>/Saturation1'
                                        * Calculated user level SOC
                                        */
float32_t VeSoc_frc_packSoc;           /* '<S22>/Saturation2'
                                        * Calculated pack level SOC
                                        */
float32_t VeSoc_frc_minCellSoc;        /* '<S3>/soc_min'
                                        * Minimum cell SOC
                                        */
float32_t VeSoc_frc_maxCellSoc;        /* '<S3>/soc_max'
                                        * Maximum cell SOC
                                        */
float32_t VaSoc_ms_tauDepolar[SOC_NUM_OF_CELLS];/* '<S3>/LaSoc_ms_tauDepolar'
                                                 * Calculated tau depolar values
                                                 */
Soc_State_t VeSoc_nu_socState;         /* '<S3>/LeSoc_nu_socState' */
bool VeSoc_bi_lowSocFault;             /* '<S23>/Switch'
                                        * Low soc fault output
                                        */

/* Exported data definition */

/* Definition for custom storage class: FileScope */
static float32_t KaSoc_Ah_capacityLut[13] =
{
    4.93F, 4.93F, 44.93F, 0.93F, 4.93F, 4.93F, 4.93F, 4.93F, 4.93F, 4.93F, 4.93F,
    4.93F, 4.93F
} ;                                /* Referenced by: '<S11>/1-D Lookup Table' */

static float32_t KaSoc_V_ocvLut[SOC_LUT_SOC_ARRAY_SIZE] =
{
    3.153F, 3.217F, 3.368F, 3.441F, 3.484F, 3.544F, 3.599F, 3.642F, 3.679F,
    3.723F, 3.778F, 3.828F, 3.88F, 3.923F, 3.962F, 4.028F, 4.082F, 4.095F,
    4.102F, 4.117F, 4.146F
} ;                                    /* Referenced by:
                                        * '<S12>/OcvBasedSocLookupTable'
                                        * '<S17>/OcvBasedSocLookupTable'
                                        * '<S20>/OcvBasedSocLookupTable'
                                        */

static float32_t KaSoc_degC_tmpLut[SOC_LUT_TEMP_ARRAY_SIZE] =
{
    -35.0F, -30.0F, -20.0F, -10.0F, 0.0F, 10.0F, 20.0F, 25.0F, 30.0F, 40.0F,
    50.0F, 55.0F, 60.0F
} ;                                    /* Referenced by:
                                        * '<S11>/1-D Lookup Table'
                                        * '<S12>/HystCompensationLookup'
                                        * '<S12>/OcvBasedSocLookupTable'
                                        * '<S15>/Tau_2DLookup_MaxTemp'
                                        * '<S15>/Tau_2DLookup_MinTemp'
                                        * '<S17>/HystCompensationLookup'
                                        * '<S17>/OcvBasedSocLookupTable'
                                        * '<S19>/Tau_2DLookup_MaxTemp'
                                        * '<S19>/Tau_2DLookup_MinTemp'
                                        * '<S20>/HystCompensationLookup'
                                        * '<S20>/OcvBasedSocLookupTable'
                                        */

static float32_t KaSoc_frc_ocvBasedSocLut[273] =
{
    0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F,
    0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F,
    0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F,
    0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F,
    0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F,
    0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F,
    0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F,
    0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F,
    0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F,
    0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F,
    0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F,
    0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F,
    0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F,
    0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F,
    0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F,
    0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F,
    0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F,
    0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F,
    0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F,
    0.9F, 0.95F, 1.0F, 0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F,
    0.45F, 0.5F, 0.55F, 0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F,
    0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F,
    0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F
} ;                                    /* Referenced by:
                                        * '<S12>/OcvBasedSocLookupTable'
                                        * '<S17>/OcvBasedSocLookupTable'
                                        * '<S20>/OcvBasedSocLookupTable'
                                        */

static float32_t KaSoc_frc_socHystVoltLut[(SOC_LUT_SOC_ARRAY_SIZE *
    SOC_LUT_TEMP_ARRAY_SIZE)] =
{
    0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F,
    0.002F, 0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F,
    0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F,
    0.003F, 0.002F, 0.002F, 0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F,
    0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F,
    0.013F, 0.005F, 0.003F, 0.002F, 0.002F, 0.004F, 0.004F, 0.001F, -0.001F,
    -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F,
    0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F, 0.002F, 0.004F, 0.004F,
    0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F,
    0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F, 0.002F,
    0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F,
    0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F,
    0.002F, 0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F,
    0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F,
    0.003F, 0.002F, 0.002F, 0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F,
    0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F,
    0.013F, 0.005F, 0.003F, 0.002F, 0.002F, 0.004F, 0.004F, 0.001F, -0.001F,
    -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F,
    0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F, 0.002F, 0.004F, 0.004F,
    0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F,
    0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F, 0.002F,
    0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F,
    0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F, 0.003F, 0.002F,
    0.002F, 0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F, 0.002F, 0.002F,
    0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F, 0.013F, 0.005F,
    0.003F, 0.002F, 0.002F, 0.004F, 0.004F, 0.001F, -0.001F, -0.004F, 0.001F,
    0.002F, 0.002F, 0.0F, 0.0F, 0.0F, 0.062F, 0.037F, 0.009F, 0.016F, 0.016F,
    0.013F, 0.005F, 0.003F, 0.002F, 0.002F, 0.004F, 0.004F, 0.001F, -0.001F,
    -0.004F, 0.001F, 0.002F, 0.002F, 0.0F, 0.0F
} ;                                    /* Referenced by:
                                        * '<S12>/HystCompensationLookup'
                                        * '<S17>/HystCompensationLookup'
                                        * '<S20>/HystCompensationLookup'
                                        */

static float32_t KaSoc_frc_socLut[SOC_LUT_SOC_ARRAY_SIZE] =
{
    0.0F, 0.05F, 0.1F, 0.15F, 0.2F, 0.25F, 0.3F, 0.35F, 0.4F, 0.45F, 0.5F, 0.55F,
    0.6F, 0.65F, 0.7F, 0.75F, 0.8F, 0.85F, 0.9F, 0.95F, 1.0F
} ;                                    /* Referenced by:
                                        * '<S12>/HystCompensationLookup'
                                        * '<S15>/Tau_2DLookup_MaxTemp'
                                        * '<S15>/Tau_2DLookup_MinTemp'
                                        * '<S17>/HystCompensationLookup'
                                        * '<S19>/Tau_2DLookup_MaxTemp'
                                        * '<S19>/Tau_2DLookup_MinTemp'
                                        * '<S20>/HystCompensationLookup'
                                        */

static float32_t KaSoc_sec_tauDepolarLut[(SOC_LUT_SOC_ARRAY_SIZE *
    SOC_LUT_TEMP_ARRAY_SIZE)] =
{
    991.2F, 119.0F, 111.8F, 143.0F, 147.0F, 202.8F, 168.7F, 122.7F, 112.8F,
    121.2F, 242.8F, 752.8F, 337.7F, 175.2F, 125.5F, 117.8F, 122.3F, 129.0F,
    157.5F, 165.3F, 731.2F, 991.2F, 119.0F, 111.8F, 143.0F, 147.0F, 202.8F,
    168.7F, 122.7F, 112.8F, 121.2F, 242.8F, 752.8F, 337.7F, 175.2F, 125.5F,
    117.8F, 122.3F, 129.0F, 157.5F, 165.3F, 731.2F, 991.2F, 119.0F, 111.8F,
    143.0F, 147.0F, 202.8F, 168.7F, 122.7F, 112.8F, 121.2F, 242.8F, 752.8F,
    337.7F, 175.2F, 125.5F, 117.8F, 122.3F, 129.0F, 157.5F, 165.3F, 731.2F,
    991.2F, 119.0F, 111.8F, 143.0F, 147.0F, 202.8F, 168.7F, 122.7F, 112.8F,
    121.2F, 242.8F, 752.8F, 337.7F, 175.2F, 125.5F, 117.8F, 122.3F, 129.0F,
    157.5F, 165.3F, 731.2F, 991.2F, 119.0F, 111.8F, 143.0F, 147.0F, 202.8F,
    168.7F, 122.7F, 112.8F, 121.2F, 242.8F, 752.8F, 337.7F, 175.2F, 125.5F,
    117.8F, 122.3F, 129.0F, 157.5F, 165.3F, 731.2F, 991.2F, 119.0F, 111.8F,
    143.0F, 147.0F, 202.8F, 168.7F, 122.7F, 112.8F, 121.2F, 242.8F, 752.8F,
    337.7F, 175.2F, 125.5F, 117.8F, 122.3F, 129.0F, 157.5F, 165.3F, 731.2F,
    991.2F, 119.0F, 111.8F, 143.0F, 147.0F, 202.8F, 168.7F, 122.7F, 112.8F,
    121.2F, 242.8F, 752.8F, 337.7F, 175.2F, 125.5F, 117.8F, 122.3F, 129.0F,
    157.5F, 165.3F, 731.2F, 991.2F, 119.0F, 111.8F, 143.0F, 147.0F, 202.8F,
    168.7F, 122.7F, 112.8F, 121.2F, 242.8F, 752.8F, 337.7F, 175.2F, 125.5F,
    117.8F, 122.3F, 129.0F, 157.5F, 165.3F, 731.2F, 1151.2F, 132.2F, 103.2F,
    132.7F, 117.5F, 172.8F, 165.7F, 117.2F, 105.8F, 104.2F, 185.3F, 637.3F,
    254.0F, 123.3F, 105.2F, 108.3F, 114.8F, 122.5F, 154.5F, 184.7F, 451.2F,
    1151.2F, 225.5F, 89.3F, 102.7F, 89.3F, 103.5F, 151.0F, 110.2F, 90.2F, 80.8F,
    109.7F, 453.0F, 137.6F, 87.8F, 88.7F, 95.5F, 105.7F, 113.5F, 150.2F, 161.8F,
    711.2F, 1151.2F, 225.5F, 89.3F, 102.7F, 89.3F, 103.5F, 151.0F, 110.2F, 90.2F,
    80.8F, 109.7F, 453.0F, 137.6F, 87.8F, 88.7F, 95.5F, 105.7F, 113.5F, 150.2F,
    161.8F, 711.2F, 1131.2F, 498.4F, 84.3F, 92.9F, 80.9F, 92.9F, 154.5F, 103.0F,
    82.4F, 73.1F, 92.1F, 371.6F, 114.2F, 81.3F, 83.8F, 92.4F, 102.5F, 109.9F,
    149.3F, 161.8F, 731.2F, 1111.2F, 771.2F, 79.2F, 83.0F, 72.5F, 82.3F, 158.0F,
    95.7F, 74.5F, 65.3F, 74.5F, 290.2F, 90.7F, 74.8F, 78.8F, 89.2F, 99.2F,
    106.2F, 148.3F, 161.8F, 751.2F
} ;                                    /* Referenced by:
                                        * '<S15>/Tau_2DLookup_MaxTemp'
                                        * '<S15>/Tau_2DLookup_MinTemp'
                                        * '<S19>/Tau_2DLookup_MaxTemp'
                                        * '<S19>/Tau_2DLookup_MinTemp'
                                        */

static float32_t KeSoc_A_restingCurThd = 4.0F;
                              /* Referenced by: '<S13>/KeSoc_A_restingCurThd' */
static float32_t KeSoc_V_bodMinCellVolt = 2.993F;
                                /* Referenced by: '<S21>/KeSoc_V_bodMinCellVolt'
                                 * Value TBD
                                 */
static float32_t KeSoc_V_tocAvrgCellVolt = 4.5F;
                               /* Referenced by: '<S24>/KeSoc_V_tocAvrgCellVolt'
                                * Value TBD
                                */
static float32_t KeSoc_V_tocMaxCellVolt = 4.5F;
                                /* Referenced by: '<S24>/KeSoc_V_tocMaxCellVolt'
                                 * Value TBD
                                 */
static bool KeSoc_bi_enableHystComp = true;/* Referenced by:
                                            * '<S12>/KeSoc_bi_enableHystComp'
                                            * '<S17>/KeSoc_bi_enableHystComp'
                                            * '<S20>/KeSoc_bi_enableHystComp'
                                            */
static float32_t KeSoc_frc_BotmOfDchReset = 0.0F;
                               /* Referenced by: '<S3>/KeSoc_frc_BotmOfDchReset'
                                * Value TBD
                                */
static float32_t KeSoc_frc_lowSocResetThd = 0.12F;/* Referenced by: '<S29>/Constant' */
static float32_t KeSoc_frc_lowSocSetThd = 0.1F;/* Referenced by: '<S30>/Constant' */
static float32_t KeSoc_frc_socMaxLim = 1.0F;/* Referenced by:
                                             * '<S22>/Saturation'
                                             * '<S22>/Saturation1'
                                             * '<S22>/Saturation2'
                                             * '<S11>/Saturation'
                                             * '<S28>/KeSoc_frc_socMaxLim'
                                             * SOC_MAX_LIMIT
                                             */
static float32_t KeSoc_frc_socMinLim = 0.0F;/* Referenced by:
                                             * '<S22>/Saturation1'
                                             * '<S22>/Saturation2'
                                             * '<S11>/Saturation'
                                             * '<S27>/Constant'
                                             * SOC_MIN_LIMIT
                                             */
static float32_t KeSoc_frc_topOfChrgReset = 1.0F;
                               /* Referenced by: '<S3>/KeSoc_frc_topOfChrgReset'
                                * Value TBD
                                */
static float32_t KeSoc_frc_userSocMaxLim = 0.99F;
                            /* Referenced by: '<S22>/KeSoc_frc_userSocMaxLim' */
static float32_t KeSoc_frc_userSocMinLim = 0.014F;
                            /* Referenced by: '<S22>/KeSoc_frc_userSocMinLim' */
static float32_t KeSoc_nu_epsValue = 2.22044605E-16F;/* Referenced by: '<S22>/Saturation' */
static float32_t KeSoc_nu_restTauFactor = 3.0F;/* Referenced by:
                                                * '<S15>/KeSoc_nu_restTauFactor'
                                                * '<S19>/KeSoc_nu_restTauFactor'
                                                */
static float32_t KeSoc_sec_sampleTime = 0.01F;/* Referenced by:
                                               * '<S21>/KeSoc_sec_sampleTime'
                                               * '<S24>/KeSoc_sec_sampleTime'
                                               * '<S13>/KeSoc_sec_sampleTime'
                                               * '<S15>/KeSoc_sec_sampleTime'
                                               * '<S19>/KeSoc_sec_sampleTime'
                                               */
static float32_t KeSoc_sec_socBodSetTime = 0.0F;
                               /* Referenced by: '<S21>/KeSoc_sec_socBodSetTime'
                                * Value TBD
                                */
static float32_t KeSoc_sec_socTocSetTime = 0.0F;
                               /* Referenced by: '<S24>/KeSoc_sec_socTocSetTime'
                                * Value TBD
                                */

/* Constant parameters (default storage) */
const ConstP_soc_T soc_ConstP =
{
    /* Pooled Parameter (Expression: )
     * Referenced by:
     *   '<S12>/HystCompensationLookup'
     *   '<S12>/OcvBasedSocLookupTable'
     *   '<S15>/Tau_2DLookup_MaxTemp'
     *   '<S15>/Tau_2DLookup_MinTemp'
     *   '<S17>/HystCompensationLookup'
     *   '<S17>/OcvBasedSocLookupTable'
     *   '<S19>/Tau_2DLookup_MaxTemp'
     *   '<S19>/Tau_2DLookup_MinTemp'
     *   '<S20>/HystCompensationLookup'
     *   '<S20>/OcvBasedSocLookupTable'
     */
    {
        SOC_LUT_SOC_ARRAY_SIZE-1, SOC_LUT_TEMP_ARRAY_SIZE-1
    }
};

/* Block signals (default storage) */
B_soc_T soc_B;

/* Block states (default storage) */
DW_soc_T soc_DW;
static float32_t look2_iflf_binlca(float32_t u0, float32_t u1, const float32_t
    bp0[], const float32_t bp1[], const float32_t table[], const uint32_t
    maxIndex[], uint32_t stride);
static uint32_t plook_u32ff_binca(float32_t u, const float32_t bp[], uint32_t
    maxIndex, float32_t *fraction);
static float32_t intrp2d_fu32fla(const uint32_t bpIndex[], const float32_t frac[],
    const float32_t table[], const uint32_t stride, const uint32_t maxIndex[]);
static uint32_t binsearch_u32f(float32_t u, const float32_t bp[], uint32_t
    startIndex, uint32_t maxIndex);
static float32_t look1_iflf_binlca(float32_t u0, const float32_t bp0[], const
    float32_t table[], uint32_t maxIndex);
static void Soc_ocvBasedSocCalc(const float32_t
    rtu_VaSoc_degC_cellTmp[SOC_NUM_OF_CELLS], const float32_t
    rtu_VaSoc_V_cellVolt[SOC_NUM_OF_CELLS], const float32_t
    rtu_LaSoc_frc_cellSoc[SOC_NUM_OF_CELLS], float32_t
    rty_LaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS]);
static void Soc_socCorrection(const float32_t
    rtu_LaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS], const float32_t
    rtu_LaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS], const float32_t
    rtu_LaSoc_nu_filterWeight[SOC_NUM_OF_CELLS], const uint32_t
    rtu_LaSoc_ms_RequiredRestTime[SOC_NUM_OF_CELLS], uint32_t
    rtu_LeSoc_ms_battRestTime, bool rtu_VeSoc_bi_socReset, float32_t
    rty_LaSoc_frc_cellSoc[SOC_NUM_OF_CELLS], bool *rty_LeSoc_bi_socCorrectedFlag,
    DW_Soc_socCorrection_T *localDW);
static void Soc_filterWeightAndReqRestCalc(float32_t rtu_VeSoc_degC_minCellTmp,
    float32_t rtu_VeSoc_degC_maxCellTmp, const float32_t
    rtu_LaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS], float32_t
    rty_LaSoc_ms_tauDepolar[SOC_NUM_OF_CELLS], uint32_t
    rty_LaSoc_ms_RequiredRestTime[SOC_NUM_OF_CELLS], float32_t
    rty_LaSoc_nu_filterWeight[SOC_NUM_OF_CELLS]);
static void Soc_coulombCountingSocCalc_Init(void);
static void Soc_coulombCountingSocCalc(void);
static void Soc_restTimeCalc(void);
static void Soc_socNormal_Init(void);
static void Soc_socNormal(void);
static void Soc_socCorrectionOnWake(void);
static void Soc_socReset(void);
static void Soc_socOutputs(void);
static float32_t look2_iflf_binlca(float32_t u0, float32_t u1, const float32_t
    bp0[], const float32_t bp1[], const float32_t table[], const uint32_t
    maxIndex[], uint32_t stride)
{
    float32_t fractions[2];
    float32_t frac;
    float32_t y;
    float32_t yL_0d0;
    uint32_t bpIndices[2];
    uint32_t bpIdx;
    uint32_t iLeft;
    uint32_t iRght;

    /* Column-major Lookup 2-D
       Search method: 'binary'
       Use previous index: 'off'
       Interpolation method: 'Linear point-slope'
       Extrapolation method: 'Clip'
       Use last breakpoint for index at or above upper limit: 'on'
       Remove protection against out-of-range input in generated code: 'off'
     */
    /* Prelookup - Index and Fraction
       Index Search method: 'binary'
       Extrapolation method: 'Clip'
       Use previous index: 'off'
       Use last breakpoint for index at or above upper limit: 'on'
       Remove protection against out-of-range input in generated code: 'off'
     */
    if (u0 <= bp0[0U])
    {
        iLeft = 0U;
        frac = 0.0F;
    }
    else if (u0 < bp0[maxIndex[0U]])
    {
        /* Binary Search */
        bpIdx = (maxIndex[0U] >> (uint32_t)1U);
        iLeft = 0U;
        iRght = maxIndex[0U];
        while ((iRght - iLeft) > (uint32_t)1U)
        {
            if (u0 < bp0[bpIdx])
            {
                iRght = bpIdx;
            }
            else
            {
                iLeft = bpIdx;
            }

            bpIdx = ((iRght + iLeft) >> (uint32_t)1U);
        }

        frac = (u0 - bp0[iLeft]) / (bp0[iLeft + 1U] - bp0[iLeft]);
    }
    else
    {
        iLeft = maxIndex[0U];
        frac = 0.0F;
    }

    fractions[0U] = frac;
    bpIndices[0U] = iLeft;

    /* Prelookup - Index and Fraction
       Index Search method: 'binary'
       Extrapolation method: 'Clip'
       Use previous index: 'off'
       Use last breakpoint for index at or above upper limit: 'on'
       Remove protection against out-of-range input in generated code: 'off'
     */
    if (u1 <= bp1[0U])
    {
        iLeft = 0U;
        frac = 0.0F;
    }
    else if (u1 < bp1[maxIndex[1U]])
    {
        /* Binary Search */
        bpIdx = (maxIndex[1U] >> (uint32_t)1U);
        iLeft = 0U;
        iRght = maxIndex[1U];
        while ((iRght - iLeft) > (uint32_t)1U)
        {
            if (u1 < bp1[bpIdx])
            {
                iRght = bpIdx;
            }
            else
            {
                iLeft = bpIdx;
            }

            bpIdx = ((iRght + iLeft) >> (uint32_t)1U);
        }

        frac = (u1 - bp1[iLeft]) / (bp1[iLeft + 1U] - bp1[iLeft]);
    }
    else
    {
        iLeft = maxIndex[1U];
        frac = 0.0F;
    }

    /* Column-major Interpolation 2-D
       Interpolation method: 'Linear point-slope'
       Use last breakpoint for index at or above upper limit: 'on'
       Overflow mode: 'wrapping'
     */
    bpIdx = (iLeft * stride) + bpIndices[0U];
    if (bpIndices[0U] == maxIndex[0U])
    {
        y = table[bpIdx];
    }
    else
    {
        yL_0d0 = table[bpIdx];
        y = ((table[bpIdx + 1U] - yL_0d0) * fractions[0U]) + yL_0d0;
    }

    if (iLeft == maxIndex[1U])
    {
    }
    else
    {
        bpIdx += stride;
        if (bpIndices[0U] == maxIndex[0U])
        {
            yL_0d0 = table[bpIdx];
        }
        else
        {
            yL_0d0 = table[bpIdx];
            yL_0d0 += (table[bpIdx + 1U] - yL_0d0) * fractions[0U];
        }

        y += (yL_0d0 - y) * frac;
    }

    return y;
}

static uint32_t plook_u32ff_binca(float32_t u, const float32_t bp[], uint32_t
    maxIndex, float32_t *fraction)
{
    uint32_t bpIndex;

    /* Prelookup - Index and Fraction
       Index Search method: 'binary'
       Extrapolation method: 'Clip'
       Use previous index: 'off'
       Use last breakpoint for index at or above upper limit: 'on'
       Remove protection against out-of-range input in generated code: 'off'
     */
    if (u <= bp[0U])
    {
        bpIndex = 0U;
        *fraction = 0.0F;
    }
    else if (u < bp[maxIndex])
    {
        bpIndex = binsearch_u32f(u, bp, maxIndex >> (uint32_t)1U, maxIndex);
        *fraction = (u - bp[bpIndex]) / (bp[bpIndex + 1U] - bp[bpIndex]);
    }
    else
    {
        bpIndex = maxIndex;
        *fraction = 0.0F;
    }

    return bpIndex;
}

static float32_t intrp2d_fu32fla(const uint32_t bpIndex[], const float32_t frac[],
    const float32_t table[], const uint32_t stride, const uint32_t maxIndex[])
{
    float32_t y;
    float32_t yL_0d0;
    uint32_t offset_1d;

    /* Column-major Interpolation 2-D
       Interpolation method: 'Linear point-slope'
       Use last breakpoint for index at or above upper limit: 'on'
       Overflow mode: 'wrapping'
     */
    offset_1d = (bpIndex[1U] * stride) + bpIndex[0U];
    if (bpIndex[0U] == maxIndex[0U])
    {
        y = table[offset_1d];
    }
    else
    {
        yL_0d0 = table[offset_1d];
        y = ((table[offset_1d + 1U] - yL_0d0) * frac[0U]) + yL_0d0;
    }

    if (bpIndex[1U] == maxIndex[1U])
    {
    }
    else
    {
        offset_1d += stride;
        if (bpIndex[0U] == maxIndex[0U])
        {
            yL_0d0 = table[offset_1d];
        }
        else
        {
            yL_0d0 = table[offset_1d];
            yL_0d0 += (table[offset_1d + 1U] - yL_0d0) * frac[0U];
        }

        y += (yL_0d0 - y) * frac[1U];
    }

    return y;
}

static uint32_t binsearch_u32f(float32_t u, const float32_t bp[], uint32_t
    startIndex, uint32_t maxIndex)
{
    uint32_t bpIdx;
    uint32_t bpIndex;
    uint32_t iRght;

    /* Binary Search */
    bpIdx = startIndex;
    bpIndex = 0U;
    iRght = maxIndex;
    while ((iRght - bpIndex) > (uint32_t)1U)
    {
        if (u < bp[bpIdx])
        {
            iRght = bpIdx;
        }
        else
        {
            bpIndex = bpIdx;
        }

        bpIdx = ((iRght + bpIndex) >> (uint32_t)1U);
    }

    return bpIndex;
}

static float32_t look1_iflf_binlca(float32_t u0, const float32_t bp0[], const
    float32_t table[], uint32_t maxIndex)
{
    float32_t frac;
    float32_t y;
    uint32_t iLeft;

    /* Column-major Lookup 1-D
       Search method: 'binary'
       Use previous index: 'off'
       Interpolation method: 'Linear point-slope'
       Extrapolation method: 'Clip'
       Use last breakpoint for index at or above upper limit: 'on'
       Remove protection against out-of-range input in generated code: 'off'
     */
    /* Prelookup - Index and Fraction
       Index Search method: 'binary'
       Extrapolation method: 'Clip'
       Use previous index: 'off'
       Use last breakpoint for index at or above upper limit: 'on'
       Remove protection against out-of-range input in generated code: 'off'
     */
    if (u0 <= bp0[0U])
    {
        iLeft = 0U;
        frac = 0.0F;
    }
    else if (u0 < bp0[maxIndex])
    {
        uint32_t bpIdx;
        uint32_t iRght;

        /* Binary Search */
        bpIdx = (maxIndex >> (uint32_t)1U);
        iLeft = 0U;
        iRght = maxIndex;
        while ((iRght - iLeft) > (uint32_t)1U)
        {
            if (u0 < bp0[bpIdx])
            {
                iRght = bpIdx;
            }
            else
            {
                iLeft = bpIdx;
            }

            bpIdx = ((iRght + iLeft) >> (uint32_t)1U);
        }

        frac = (u0 - bp0[iLeft]) / (bp0[iLeft + 1U] - bp0[iLeft]);
    }
    else
    {
        iLeft = maxIndex;
        frac = 0.0F;
    }

    /* Column-major Interpolation 1-D
       Interpolation method: 'Linear point-slope'
       Use last breakpoint for index at or above upper limit: 'on'
       Overflow mode: 'wrapping'
     */
    if (iLeft == maxIndex)
    {
        y = table[iLeft];
    }
    else
    {
        float32_t yL_0d0;
        yL_0d0 = table[iLeft];
        y = ((table[iLeft + 1U] - yL_0d0) * frac) + yL_0d0;
    }

    return y;
}

/* System initialize for atomic system: '<S8>/CoulombCounting_Subsys' */
static void Soc_coulombCountingSocCalc_Init(void)
{
    /* InitializeConditions for DiscreteIntegrator: '<S11>/Integrator' */
    soc_DW.Integrator_PrevResetState = 2;
}

/* Output and update for atomic system: '<S8>/CoulombCounting_Subsys' */
static void Soc_coulombCountingSocCalc(void)
{
    float32_t rtb_Divide;
    float32_t u0;
    int32_t i;

    /* DiscreteIntegrator: '<S11>/Integrator' */
    if (soc_B.LeSoc_bi_ccReset && (soc_DW.Integrator_PrevResetState <= (int8_t)0))
    {
        soc_DW.Integrator_DSTATE = 0.0F;
    }

    /* Sum: '<S11>/Sum of Elements' incorporates:
     *  UnitDelay: '<S1>/Unit Delay1'
     */
    rtb_Divide = -0.0F;
    for (i = 0; i < SOC_NUM_OF_CELLS; i++)
    {
        rtb_Divide += soc_DW.UnitDelay1_DSTATE[i];
    }

    /* Product: '<S11>/Divide' incorporates:
     *  Constant: '<S11>/ABS_AH_TO_COULOMB'
     *  Constant: '<S11>/SOC_CELLS_IN_PARALLEL'
     *  Constant: '<S11>/SOC_NUM_OF_CELLS'
     *  DiscreteIntegrator: '<S11>/Integrator'
     *  Lookup_n-D: '<S11>/1-D Lookup Table'
     *  Product: '<S11>/Divide1'
     *  Product: '<S11>/Product'
     *  Sum: '<S11>/Sum of Elements'
     */
    rtb_Divide = soc_DW.Integrator_DSTATE / ((look1_iflf_binlca(rtb_Divide /
        (float32_t)((int32_t)SOC_NUM_OF_CELLS), &KaSoc_degC_tmpLut[0],
        &KaSoc_Ah_capacityLut[0], 12U) * ABS_AH_TO_COULOMB) * (float32_t)
        SOC_CELLS_IN_PARALLEL);
    for (i = 0; i < SOC_NUM_OF_CELLS; i++)
    {
        /* Saturate: '<S11>/Saturation' incorporates:
         *  Inport: '<Root>/VaSoc_frc_cellSohc'
         *  Product: '<S11>/divide'
         *  Sum: '<S11>/Add'
         *  UnitDelay: '<S8>/Unit Delay3'
         */
        u0 = soc_DW.UnitDelay3_DSTATE[i] + (rtb_Divide / VaSoc_frc_cellSohc[i]);
        if (u0 > KeSoc_frc_socMaxLim)
        {
            /* Saturate: '<S11>/Saturation' */
            soc_B.LaSoc_frc_cellSocCc[i] = KeSoc_frc_socMaxLim;
        }
        else if (u0 < KeSoc_frc_socMinLim)
        {
            /* Saturate: '<S11>/Saturation' */
            soc_B.LaSoc_frc_cellSocCc[i] = KeSoc_frc_socMinLim;
        }
        else
        {
            /* Saturate: '<S11>/Saturation' */
            soc_B.LaSoc_frc_cellSocCc[i] = u0;
        }

        /* End of Saturate: '<S11>/Saturation' */
    }

    /* Update for DiscreteIntegrator: '<S11>/Integrator' incorporates:
     *  Inport: '<Root>/VeSoc_A_battCur'
     */
    soc_DW.Integrator_DSTATE += 0.01F * VeSoc_A_battCur;
    soc_DW.Integrator_PrevResetState = (int8_t)(soc_B.LeSoc_bi_ccReset ? 1 : 0);
}

/*
 * Output and update for atomic system:
 *    '<S8>/OcvBasedSocCalc_Subsys'
 *    '<S9>/OcvBasedSocCalc_Subsys'
 *    '<S10>/OcvBasedSocCalc_Subsys'
 */
static void Soc_ocvBasedSocCalc(const float32_t
    rtu_VaSoc_degC_cellTmp[SOC_NUM_OF_CELLS], const float32_t
    rtu_VaSoc_V_cellVolt[SOC_NUM_OF_CELLS], const float32_t
    rtu_LaSoc_frc_cellSoc[SOC_NUM_OF_CELLS], float32_t
    rty_LaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS])
{
    float32_t rtb_HystCompensationLookup[SOC_NUM_OF_CELLS];
    float32_t rtb_HystCompensationLookup_0;
    int32_t iU;

    /* Switch: '<S12>/Switch' incorporates:
     *  Constant: '<S12>/KeSoc_bi_enableHystComp'
     *  Constant: '<S12>/NoHysteresisIsApplied'
     */
    if (KeSoc_bi_enableHystComp)
    {
        /* Lookup_n-D: '<S12>/HystCompensationLookup' */
        for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
        {
            rtb_HystCompensationLookup[iU] = look2_iflf_binlca
                (rtu_LaSoc_frc_cellSoc[iU], rtu_VaSoc_degC_cellTmp[iU],
                 &KaSoc_frc_socLut[0], &KaSoc_degC_tmpLut[0],
                 &KaSoc_frc_socHystVoltLut[0], soc_ConstP.pooled7, (uint32_t)
                 SOC_LUT_SOC_ARRAY_SIZE);
        }

        /* End of Lookup_n-D: '<S12>/HystCompensationLookup' */
    }
    else
    {
        for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
        {
            rtb_HystCompensationLookup[iU] = 0.0F;
        }
    }

    /* End of Switch: '<S12>/Switch' */
    for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
    {
        /* Sum: '<S12>/Subtract' */
        rtb_HystCompensationLookup_0 = rtu_VaSoc_V_cellVolt[iU] -
            rtb_HystCompensationLookup[iU];
        rtb_HystCompensationLookup[iU] = rtb_HystCompensationLookup_0;

        /* Lookup_n-D: '<S12>/OcvBasedSocLookupTable' */
        rty_LaSoc_frc_cellSocOcv[iU] = look2_iflf_binlca
            (rtb_HystCompensationLookup_0, rtu_VaSoc_degC_cellTmp[iU],
             &KaSoc_V_ocvLut[0], &KaSoc_degC_tmpLut[0],
             &KaSoc_frc_ocvBasedSocLut[0], soc_ConstP.pooled7, 21U);
    }
}

/* Output and update for atomic system: '<S8>/RestTimeAccumulation' */
static void Soc_restTimeCalc(void)
{
    bool rtb_AND;
    bool rtb_OR1;

    /* Logic: '<S13>/AND' incorporates:
     *  Abs: '<S13>/Abs'
     *  Constant: '<S13>/KeSoc_A_restingCurThd'
     *  Constant: '<S13>/StandbyInit'
     *  Constant: '<S13>/StandbyNotReady'
     *  Constant: '<S13>/StandbyReady'
     *  Inport: '<Root>/VeBattsm_nu_battState'
     *  Inport: '<Root>/VeSoc_A_battCur'
     *  Logic: '<S13>/OR'
     *  RelationalOperator: '<S13>/Equal'
     *  RelationalOperator: '<S13>/Equal1'
     *  RelationalOperator: '<S13>/Equal2'
     *  RelationalOperator: '<S13>/LessThanOrEqual'
     */
    rtb_AND = ((fabsf(VeSoc_A_battCur) <= KeSoc_A_restingCurThd) &&
               ((VeBattsm_nu_battState == BATTSM_STATE_STANDBY_INIT) ||
                (VeBattsm_nu_battState == BATTSM_STATE_STANDBY_NOT_READY) ||
                (VeBattsm_nu_battState == BATTSM_STATE_STANDBY_READY)));

    /* Logic: '<S13>/OR1' incorporates:
     *  Logic: '<S13>/NOT'
     */
    rtb_OR1 = (!rtb_AND || soc_B.UnitDelay2);

    /* Switch: '<S16>/Switch' */
    if (rtb_OR1)
    {
        /* Switch: '<S16>/Switch' incorporates:
         *  Constant: '<S16>/Init'
         */
        soc_DW.UnitDelay2_DSTATE = 0.0F;
    }

    /* End of Switch: '<S16>/Switch' */

    /* DataTypeConversion: '<S13>/DatatypeConversion' incorporates:
     *  Constant: '<S13>/ABS_SEC_TO_MILLISEC'
     *  Constant: '<S13>/KeSoc_sec_sampleTime'
     *  Product: '<S13>/Product'
     *  Product: '<S16>/Product'
     */
    soc_B.LeSoc_ms_battRestTime = (uint32_t)((float32_t)
        ((soc_DW.UnitDelay2_DSTATE * KeSoc_sec_sampleTime) * ABS_SEC_TO_MILLISEC));

    /* Switch: '<S16>/Switch1' incorporates:
     *  Logic: '<S16>/LogicalOperator'
     *  Logic: '<S16>/LogicalOperator1'
     */
    if (!rtb_OR1 && rtb_AND)
    {
        /* Switch: '<S16>/Switch' incorporates:
         *  Constant: '<S16>/Increment'
         *  Sum: '<S16>/Sum1'
         *  UnitDelay: '<S16>/UnitDelay2'
         */
        soc_DW.UnitDelay2_DSTATE++;
    }

    /* End of Switch: '<S16>/Switch1' */
}

/*
 * Output and update for atomic system:
 *    '<S8>/SocCorrection_SubSys'
 *    '<S9>/SocCorrection_SubSys'
 */
static void Soc_socCorrection(const float32_t
    rtu_LaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS], const float32_t
    rtu_LaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS], const float32_t
    rtu_LaSoc_nu_filterWeight[SOC_NUM_OF_CELLS], const uint32_t
    rtu_LaSoc_ms_RequiredRestTime[SOC_NUM_OF_CELLS], uint32_t
    rtu_LeSoc_ms_battRestTime, bool rtu_VeSoc_bi_socReset, float32_t
    rty_LaSoc_frc_cellSoc[SOC_NUM_OF_CELLS], bool *rty_LeSoc_bi_socCorrectedFlag,
    DW_Soc_socCorrection_T *localDW)
{
    int32_t k;
    uint32_t maxV;
    bool rtb_AND_d4fo;

    /* Logic: '<S14>/AND' incorporates:
     *  Logic: '<S14>/NOT'
     *  UnitDelay: '<S14>/Unit Delay'
     */
    rtb_AND_d4fo = (rtu_VeSoc_bi_socReset && !localDW->UnitDelay_DSTATE);

    /* Switch: '<S14>/Switch1' incorporates:
     *  RelationalOperator: '<S14>/GreaterThanOrEqual'
     *  Switch: '<S14>/Switch'
     */
    for (k = 0; k < SOC_NUM_OF_CELLS; k++)
    {
        if (rtb_AND_d4fo)
        {
            rty_LaSoc_frc_cellSoc[k] = rtu_LaSoc_frc_cellSocOcv[k];
        }
        else if (rtu_LeSoc_ms_battRestTime >= rtu_LaSoc_ms_RequiredRestTime[k])
        {
            float32_t rtu_LaSoc_nu_filterWeight_0;

            /* Sum: '<S14>/Subtract2' */
            rtu_LaSoc_nu_filterWeight_0 = rtu_LaSoc_nu_filterWeight[k];

            /* Switch: '<S14>/Switch' incorporates:
             *  Constant: '<S14>/Constant'
             *  Product: '<S14>/Product2'
             *  Product: '<S14>/Product3'
             *  Sum: '<S14>/Subtract2'
             *  Sum: '<S14>/Subtract5'
             */
            rty_LaSoc_frc_cellSoc[k] = (rtu_LaSoc_frc_cellSocCc[k] * (1.0F -
                rtu_LaSoc_nu_filterWeight_0)) + (rtu_LaSoc_nu_filterWeight_0 *
                rtu_LaSoc_frc_cellSocOcv[k]);
        }
        else
        {
            rty_LaSoc_frc_cellSoc[k] = rtu_LaSoc_frc_cellSocCc[k];
        }
    }

    /* End of Switch: '<S14>/Switch1' */

    /* MinMax: '<S14>/Max' */
    maxV = rtu_LaSoc_ms_RequiredRestTime[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        uint32_t u1;
        u1 = rtu_LaSoc_ms_RequiredRestTime[k];
        if (maxV < u1)
        {
            maxV = u1;
        }
    }

    /* Logic: '<S14>/OR' incorporates:
     *  MinMax: '<S14>/Max'
     *  RelationalOperator: '<S14>/GreaterThanOrEqual1'
     */
    *rty_LeSoc_bi_socCorrectedFlag = (rtb_AND_d4fo || (rtu_LeSoc_ms_battRestTime
        >= maxV));

    /* Update for UnitDelay: '<S14>/Unit Delay' */
    localDW->UnitDelay_DSTATE = rtu_VeSoc_bi_socReset;
}

/*
 * Output and update for atomic system:
 *    '<S8>/TauDepolarLookup_Subsys'
 *    '<S9>/TauDepolarLookup_Subsys'
 */
static void Soc_filterWeightAndReqRestCalc(float32_t rtu_VeSoc_degC_minCellTmp,
    float32_t rtu_VeSoc_degC_maxCellTmp, const float32_t
    rtu_LaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS], float32_t
    rty_LaSoc_ms_tauDepolar[SOC_NUM_OF_CELLS], uint32_t
    rty_LaSoc_ms_RequiredRestTime[SOC_NUM_OF_CELLS], float32_t
    rty_LaSoc_nu_filterWeight[SOC_NUM_OF_CELLS])
{
    float32_t fractions[2];
    float32_t fractions_0[2];
    float32_t rtb_LaSoc_ms_RequiredRestT_acjj[SOC_NUM_OF_CELLS];
    float32_t rtb_Tau_2DLookup_MinTemp[SOC_NUM_OF_CELLS];
    float32_t rtb_LaSoc_ms_tauDepolar;
    int32_t iU;
    uint32_t bpIndices[2];
    uint32_t bpIndices_0[2];

    /* Lookup_n-D: '<S15>/Tau_2DLookup_MinTemp' */
    bpIndices[1U] = plook_u32ff_binca(rtu_VeSoc_degC_minCellTmp,
        &KaSoc_degC_tmpLut[0], (uint32_t)((int32_t)(SOC_LUT_TEMP_ARRAY_SIZE - 1)),
        &rtb_LaSoc_ms_tauDepolar);
    fractions[1U] = rtb_LaSoc_ms_tauDepolar;
    for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
    {
        bpIndices[0U] = plook_u32ff_binca(rtu_LaSoc_frc_cellSocCc[iU],
            &KaSoc_frc_socLut[0], (uint32_t)((int32_t)(SOC_LUT_SOC_ARRAY_SIZE -
            1)), &rtb_LaSoc_ms_tauDepolar);
        fractions[0U] = rtb_LaSoc_ms_tauDepolar;
        rtb_Tau_2DLookup_MinTemp[iU] = intrp2d_fu32fla(bpIndices, fractions,
            &KaSoc_sec_tauDepolarLut[0], (uint32_t)SOC_LUT_SOC_ARRAY_SIZE,
            soc_ConstP.pooled7);
    }

    /* End of Lookup_n-D: '<S15>/Tau_2DLookup_MinTemp' */

    /* Lookup_n-D: '<S15>/Tau_2DLookup_MaxTemp' */
    bpIndices_0[1U] = plook_u32ff_binca(rtu_VeSoc_degC_maxCellTmp,
        &KaSoc_degC_tmpLut[0], (uint32_t)((int32_t)(SOC_LUT_TEMP_ARRAY_SIZE - 1)),
        &rtb_LaSoc_ms_tauDepolar);
    fractions_0[1U] = rtb_LaSoc_ms_tauDepolar;
    for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
    {
        bpIndices_0[0U] = plook_u32ff_binca(rtu_LaSoc_frc_cellSocCc[iU],
            &KaSoc_frc_socLut[0], (uint32_t)((int32_t)(SOC_LUT_SOC_ARRAY_SIZE -
            1)), &rtb_LaSoc_ms_tauDepolar);
        fractions_0[0U] = rtb_LaSoc_ms_tauDepolar;
        rtb_LaSoc_ms_RequiredRestT_acjj[iU] = intrp2d_fu32fla(bpIndices_0,
            fractions_0, &KaSoc_sec_tauDepolarLut[0], (uint32_t)
            SOC_LUT_SOC_ARRAY_SIZE, soc_ConstP.pooled7);
    }

    /* End of Lookup_n-D: '<S15>/Tau_2DLookup_MaxTemp' */
    for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
    {
        /* Product: '<S15>/Product1' incorporates:
         *  Constant: '<S15>/ABS_SEC_TO_MILLISEC'
         *  MinMax: '<S15>/Max'
         */
        rty_LaSoc_ms_tauDepolar[iU] = fmaxf(rtb_Tau_2DLookup_MinTemp[iU],
            rtb_LaSoc_ms_RequiredRestT_acjj[iU]) * ABS_SEC_TO_MILLISEC;

        /* Product: '<S15>/Product' incorporates:
         *  Constant: '<S15>/KeSoc_nu_restTauFactor'
         */
        rtb_LaSoc_ms_tauDepolar = rty_LaSoc_ms_tauDepolar[iU] *
            KeSoc_nu_restTauFactor;
        rtb_LaSoc_ms_RequiredRestT_acjj[iU] = rtb_LaSoc_ms_tauDepolar;

        /* DataTypeConversion: '<S15>/DataTypeConversion' */
        rty_LaSoc_ms_RequiredRestTime[iU] = (uint32_t)rtb_LaSoc_ms_tauDepolar;
    }

    /* Product: '<S15>/Product2' incorporates:
     *  Constant: '<S15>/ABS_SEC_TO_MILLISEC1'
     *  Constant: '<S15>/KeSoc_sec_sampleTime'
     */
    rtb_LaSoc_ms_tauDepolar = KeSoc_sec_sampleTime * ABS_SEC_TO_MILLISEC;

    /* Product: '<S15>/Divide' incorporates:
     *  Sum: '<S15>/Add'
     */
    for (iU = 0; iU < SOC_NUM_OF_CELLS; iU++)
    {
        rty_LaSoc_nu_filterWeight[iU] = rtb_LaSoc_ms_tauDepolar /
            (rtb_LaSoc_ms_tauDepolar + (float32_t)
             rty_LaSoc_ms_RequiredRestTime[iU]);
    }

    /* End of Product: '<S15>/Divide' */
}

/* System initialize for enable system: '<S2>/NormalState' */
static void Soc_socNormal_Init(void)
{
    /* SystemInitialize for Atomic SubSystem: '<S8>/CoulombCounting_Subsys' */
    Soc_coulombCountingSocCalc_Init();

    /* End of SystemInitialize for SubSystem: '<S8>/CoulombCounting_Subsys' */
}

/* Output and update for enable system: '<S2>/NormalState' */
static void Soc_socNormal(void)
{
    float32_t rtb_LaSoc_nu_filterWeight[SOC_NUM_OF_CELLS];
    int32_t i;
    uint32_t rtb_LaSoc_ms_RequiredRestTime[SOC_NUM_OF_CELLS];
    bool rtb_NOT_he13;

    /* Outputs for Enabled SubSystem: '<S2>/NormalState' incorporates:
     *  EnablePort: '<S8>/Enable'
     */
    if (soc_B.Compare_go2r)
    {
        /* Logic: '<S8>/NOT' */
        rtb_NOT_he13 = !soc_B.LeSoc_bi_socInNormalStateFlg;

        /* Switch: '<S8>/Switch1' incorporates:
         *  Logic: '<S8>/AND'
         *  Logic: '<S8>/AND1'
         *  Switch: '<S8>/Switch2'
         *  Switch: '<S8>/Switch3'
         *  UnitDelay: '<S1>/UnitDelay3'
         *  UnitDelay: '<S1>/UnitDelay4'
         *  UnitDelay: '<S8>/Unit Delay1'
         *  UnitDelay: '<S8>/Unit Delay3'
         */
        if (soc_DW.UnitDelay4_DSTATE_dlsb && rtb_NOT_he13)
        {
            for (i = 0; i < SOC_NUM_OF_CELLS; i++)
            {
                soc_DW.UnitDelay3_DSTATE[i] = soc_B.LaSoc_frc_cellSocOcv[i];
            }
        }
        else if (rtb_NOT_he13 && soc_DW.UnitDelay3_DSTATE_hjte)
        {
            for (i = 0; i < SOC_NUM_OF_CELLS; i++)
            {
                /* UnitDelay: '<S8>/Unit Delay3' incorporates:
                 *  Switch: '<S8>/Switch2'
                 */
                soc_DW.UnitDelay3_DSTATE[i] = soc_B.LaSoc_frc_cellSoc[i];
            }
        }
        else if (soc_DW.UnitDelay1_DSTATE_fjxo)
        {
            for (i = 0; i < SOC_NUM_OF_CELLS; i++)
            {
                /* Switch: '<S8>/Switch3' incorporates:
                 *  Switch: '<S8>/Switch2'
                 *  UnitDelay: '<S8>/Unit Delay'
                 *  UnitDelay: '<S8>/Unit Delay3'
                 */
                soc_DW.UnitDelay3_DSTATE[i] = soc_DW.UnitDelay_DSTATE_fcnr[i];
            }
        }
        else
        {
            /* no actions */
        }

        /* End of Switch: '<S8>/Switch1' */

        /* Outputs for Atomic SubSystem: '<S8>/CoulombCounting_Subsys' */
        Soc_coulombCountingSocCalc();

        /* End of Outputs for SubSystem: '<S8>/CoulombCounting_Subsys' */

        /* Outputs for Atomic SubSystem: '<S8>/TauDepolarLookup_Subsys' */
        /* Inport: '<Root>/VeSoc_degC_minCellTmp' incorporates:
         *  Inport: '<Root>/VeSoc_degC_maxCellTmp'
         */
        Soc_filterWeightAndReqRestCalc(VeSoc_degC_minCellTmp,
            VeSoc_degC_maxCellTmp, soc_B.LaSoc_frc_cellSocCc,
            soc_B.LaSoc_ms_tauDepolar, rtb_LaSoc_ms_RequiredRestTime,
            rtb_LaSoc_nu_filterWeight);

        /* End of Outputs for SubSystem: '<S8>/TauDepolarLookup_Subsys' */

        /* UnitDelay: '<S8>/Unit Delay2' */
        soc_B.UnitDelay2 = soc_DW.UnitDelay2_DSTATE_mulm;

        /* Outputs for Atomic SubSystem: '<S8>/RestTimeAccumulation' */
        Soc_restTimeCalc();

        /* End of Outputs for SubSystem: '<S8>/RestTimeAccumulation' */

        /* Outputs for Atomic SubSystem: '<S8>/OcvBasedSocCalc_Subsys' */
        /* UnitDelay: '<S1>/Unit Delay1' incorporates:
         *  UnitDelay: '<S1>/Unit Delay'
         *  UnitDelay: '<S8>/Unit Delay4'
         */
        Soc_ocvBasedSocCalc(soc_DW.UnitDelay1_DSTATE, soc_DW.UnitDelay_DSTATE,
                            soc_DW.UnitDelay4_DSTATE,
                            soc_B.LaSoc_frc_cellSocOcv_kin5);

        /* End of Outputs for SubSystem: '<S8>/OcvBasedSocCalc_Subsys' */

        /* Outputs for Atomic SubSystem: '<S8>/SocCorrection_SubSys' */
        /* Inport: '<Root>/VeSoc_bi_socReset' incorporates:
         *  UnitDelay: '<S1>/UnitDelay8'
         *  UnitDelay: '<S8>/Unit Delay4'
         */
        Soc_socCorrection(soc_B.LaSoc_frc_cellSocCc,
                          soc_B.LaSoc_frc_cellSocOcv_kin5,
                          rtb_LaSoc_nu_filterWeight,
                          rtb_LaSoc_ms_RequiredRestTime,
                          soc_B.LeSoc_ms_battRestTime, VeSoc_bi_socReset,
                          soc_DW.UnitDelay4_DSTATE, &soc_DW.UnitDelay8_DSTATE,
                          &soc_DW.SocCorrection_SubSys);

        /* End of Outputs for SubSystem: '<S8>/SocCorrection_SubSys' */

        /* Update for UnitDelay: '<S8>/Unit Delay' incorporates:
         *  UnitDelay: '<S8>/Unit Delay4'
         */
        for (i = 0; i < SOC_NUM_OF_CELLS; i++)
        {
            soc_DW.UnitDelay_DSTATE_fcnr[i] = soc_DW.UnitDelay4_DSTATE[i];
        }

        /* End of Update for UnitDelay: '<S8>/Unit Delay' */

        /* Update for UnitDelay: '<S8>/Unit Delay1' incorporates:
         *  UnitDelay: '<S1>/UnitDelay8'
         */
        soc_DW.UnitDelay1_DSTATE_fjxo = soc_DW.UnitDelay8_DSTATE;

        /* Update for UnitDelay: '<S8>/Unit Delay2' incorporates:
         *  UnitDelay: '<S1>/UnitDelay8'
         */
        soc_DW.UnitDelay2_DSTATE_mulm = soc_DW.UnitDelay8_DSTATE;
    }

    /* End of Outputs for SubSystem: '<S2>/NormalState' */
}

/* Output and update for enable system: '<S2>/SocCorrectionOnWakeState' */
static void Soc_socCorrectionOnWake(void)
{
    float32_t rtb_LaSoc_nu_filterWeight[SOC_NUM_OF_CELLS];
    uint32_t rtb_LaSoc_ms_RequiredRestTime[SOC_NUM_OF_CELLS];
    bool rtb_OR_huxg;

    /* Outputs for Enabled SubSystem: '<S2>/SocCorrectionOnWakeState' incorporates:
     *  EnablePort: '<S9>/Enable'
     */
    if (soc_B.Compare_f2dn)
    {
        /* Outputs for Atomic SubSystem: '<S9>/OcvBasedSocCalc_Subsys' */
        /* UnitDelay: '<S1>/Unit Delay1' incorporates:
         *  Inport: '<Root>/VaSoc_frc_initialCellSoc'
         *  UnitDelay: '<S1>/Unit Delay'
         */
        Soc_ocvBasedSocCalc(soc_DW.UnitDelay1_DSTATE, soc_DW.UnitDelay_DSTATE,
                            VaSoc_frc_initialCellSoc,
                            soc_B.LaSoc_frc_cellSocOcv_gyx2);

        /* End of Outputs for SubSystem: '<S9>/OcvBasedSocCalc_Subsys' */

        /* Sum: '<S9>/Add' incorporates:
         *  Inport: '<Root>/VeSoc_ms_battAsleepTime'
         *  Inport: '<Root>/VeSoc_ms_initialBattRestTime'
         */
        soc_B.LeSoc_ms_restTiAfterWakeOnCorrn = VeSoc_ms_battAsleepTime +
            VeSoc_ms_initialBattRestTime;

        /* Outputs for Atomic SubSystem: '<S9>/TauDepolarLookup_Subsys' */
        /* Inport: '<Root>/VeSoc_degC_minCellTmp' incorporates:
         *  Inport: '<Root>/VaSoc_frc_initialCellSoc'
         *  Inport: '<Root>/VeSoc_degC_maxCellTmp'
         */
        Soc_filterWeightAndReqRestCalc(VeSoc_degC_minCellTmp,
            VeSoc_degC_maxCellTmp, VaSoc_frc_initialCellSoc,
            rtb_LaSoc_nu_filterWeight, rtb_LaSoc_ms_RequiredRestTime,
            rtb_LaSoc_nu_filterWeight);

        /* End of Outputs for SubSystem: '<S9>/TauDepolarLookup_Subsys' */

        /* Outputs for Atomic SubSystem: '<S9>/SocCorrection_SubSys' */
        /* Inport: '<Root>/VaSoc_frc_initialCellSoc' incorporates:
         *  Inport: '<Root>/VeSoc_bi_socReset'
         */
        Soc_socCorrection(VaSoc_frc_initialCellSoc,
                          soc_B.LaSoc_frc_cellSocOcv_gyx2,
                          rtb_LaSoc_nu_filterWeight,
                          rtb_LaSoc_ms_RequiredRestTime,
                          soc_B.LeSoc_ms_restTiAfterWakeOnCorrn,
                          VeSoc_bi_socReset, soc_B.LaSoc_frc_cellSoc,
                          &rtb_OR_huxg, &soc_DW.SocCorrection_SubSys_gqbb);

        /* End of Outputs for SubSystem: '<S9>/SocCorrection_SubSys' */

        /* Switch: '<S9>/Switch' */
        if (rtb_OR_huxg)
        {
            /* Sum: '<S9>/Add' incorporates:
             *  Constant: '<S9>/Constant1'
             *  Switch: '<S9>/Switch'
             */
            soc_B.LeSoc_ms_restTiAfterWakeOnCorrn = 0U;
        }

        /* End of Switch: '<S9>/Switch' */

        /* SignalConversion generated from: '<S9>/LeSoc_bi_socCorrnOnWkCmplFlg' incorporates:
         *  Constant: '<S9>/Constant'
         *  UnitDelay: '<S1>/UnitDelay3'
         */
        soc_DW.UnitDelay3_DSTATE_hjte = true;
    }

    /* End of Outputs for SubSystem: '<S2>/SocCorrectionOnWakeState' */
}

/* Output and update for enable system: '<S2>/SocResetState' */
static void Soc_socReset(void)
{
    int32_t i;

    /* Outputs for Enabled SubSystem: '<S2>/SocResetState' incorporates:
     *  EnablePort: '<S10>/Enable'
     */
    if (soc_B.Compare)
    {
        /* Outputs for Atomic SubSystem: '<S10>/OcvBasedSocCalc_Subsys' */
        /* UnitDelay: '<S1>/Unit Delay1' incorporates:
         *  Inport: '<Root>/VaSoc_frc_initialCellSoc'
         *  UnitDelay: '<S1>/Unit Delay'
         */
        Soc_ocvBasedSocCalc(soc_DW.UnitDelay1_DSTATE, soc_DW.UnitDelay_DSTATE,
                            VaSoc_frc_initialCellSoc, soc_B.LaSoc_frc_cellSocOcv);

        /* End of Outputs for SubSystem: '<S10>/OcvBasedSocCalc_Subsys' */
        for (i = 0; i < SOC_NUM_OF_CELLS; i++)
        {
            /* SignalConversion generated from: '<S10>/LaSoc_frc_socOcvAfterReset' */
            soc_B.OutportBufferForLaSoc_frc_socOc[i] =
                soc_B.LaSoc_frc_cellSocOcv[i];
        }

        /* SignalConversion generated from: '<S10>/LeSoc_ms_restTiAfterSocReset' incorporates:
         *  Constant: '<S10>/Constant'
         */
        soc_B.LeSoc_ms_restTiAfterSocReset = 0U;

        /* SignalConversion generated from: '<S10>/LeSoc_bi_socRstCmplFlg' incorporates:
         *  Constant: '<S10>/Constant1'
         *  UnitDelay: '<S1>/UnitDelay4'
         */
        soc_DW.UnitDelay4_DSTATE_dlsb = true;
    }

    /* End of Outputs for SubSystem: '<S2>/SocResetState' */
}

/* Output and update for atomic system: '<S1>/SocOutputs_Subsys' */
static void Soc_socOutputs(void)
{
    float32_t rtb_Product_c0pa[SOC_NUM_OF_CELLS];
    float32_t rtb_Product_dmnf[SOC_NUM_OF_CELLS];
    float32_t VaSoc_frc_cellSohc_0;
    float32_t rtb_Switch_gefl;
    float32_t rtb_Switch_m1yp;
    float32_t tmp;
    int32_t k;
    bool rtb_AND;
    bool rtb_AND_pv5x;
    bool rtb_Equal7;
    bool rtb_RelationalOperator_mlrg;

    /* SignalConversion generated from: '<S3>/LeSoc_nu_socState' */
    VeSoc_nu_socState = soc_B.LeSoc_nu_socState;

    /* Switch: '<S3>/Switch9' incorporates:
     *  Constant: '<S3>/CorrectionOnWake2'
     *  RelationalOperator: '<S3>/Equal6'
     */
    if (VeSoc_nu_socState == SOC_STATE_CORRECTION_ON_WAKE)
    {
        /* Switch: '<S3>/Switch9' */
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            VaSoc_frc_cellSocOcv[k] = soc_B.LaSoc_frc_cellSocOcv_gyx2[k];
        }
    }
    else
    {
        /* RelationalOperator: '<S3>/Equal7' incorporates:
         *  Constant: '<S3>/SocReset2'
         */
        rtb_Equal7 = (VeSoc_nu_socState == SOC_STATE_RESET);

        /* Switch: '<S3>/Switch9' incorporates:
         *  Switch: '<S3>/Switch10'
         */
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            if (rtb_Equal7)
            {
                VaSoc_frc_cellSocOcv[k] =
                    soc_B.OutportBufferForLaSoc_frc_socOc[k];
            }
            else
            {
                VaSoc_frc_cellSocOcv[k] = soc_B.LaSoc_frc_cellSocOcv_kin5[k];
            }
        }
    }

    /* End of Switch: '<S3>/Switch9' */

    /* Logic: '<S3>/AND' incorporates:
     *  Constant: '<S3>/CorrectionOnWake3'
     *  Constant: '<S3>/SocInit1'
     *  Constant: '<S3>/SocReset3'
     *  RelationalOperator: '<S3>/Equal10'
     *  RelationalOperator: '<S3>/Equal8'
     *  RelationalOperator: '<S3>/Equal9'
     */
    rtb_Equal7 = ((VeSoc_nu_socState == SOC_STATE_INIT) || (VeSoc_nu_socState ==
                   SOC_STATE_CORRECTION_ON_WAKE) || (VeSoc_nu_socState ==
                   SOC_STATE_RESET));
    for (k = 0; k < SOC_NUM_OF_CELLS; k++)
    {
        /* Switch: '<S3>/Switch8' */
        if (rtb_Equal7)
        {
            /* Switch: '<S3>/Switch8' incorporates:
             *  Inport: '<Root>/VaSoc_frc_initialCellSoc'
             */
            VaSoc_frc_cellSocCc[k] = VaSoc_frc_initialCellSoc[k];
        }
        else
        {
            /* Switch: '<S3>/Switch8' */
            VaSoc_frc_cellSocCc[k] = soc_B.LaSoc_frc_cellSocCc[k];
        }

        /* End of Switch: '<S3>/Switch8' */
    }

    /* MinMax: '<S21>/MinofElements' */
    tmp = soc_DW.UnitDelay_DSTATE[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        tmp = fminf(tmp, soc_DW.UnitDelay_DSTATE[k]);
    }

    /* Logic: '<S21>/AND' incorporates:
     *  Constant: '<S21>/KeSoc_V_bodMinCellVolt'
     *  Constant: '<S25>/Constant'
     *  Inport: '<Root>/VeSoc_A_battCur'
     *  MinMax: '<S21>/MinofElements'
     *  RelationalOperator: '<S21>/LessThanOrEqual'
     *  RelationalOperator: '<S25>/Compare'
     */
    rtb_AND = ((tmp <= KeSoc_V_bodMinCellVolt) && (VeSoc_A_battCur < 0.0F));

    /* Switch: '<S26>/Switch' incorporates:
     *  Constant: '<S26>/Increment'
     *  Constant: '<S26>/Init'
     *  Sum: '<S26>/Sum1'
     *  UnitDelay: '<S26>/UnitDelay'
     */
    if (rtb_AND)
    {
        rtb_Switch_m1yp = soc_DW.UnitDelay_DSTATE_lxmr + 1.0F;
    }
    else
    {
        rtb_Switch_m1yp = 0.0F;
    }

    /* End of Switch: '<S26>/Switch' */

    /* RelationalOperator: '<S26>/RelationalOperator' incorporates:
     *  Constant: '<S21>/KeSoc_sec_sampleTime'
     *  Constant: '<S21>/KeSoc_sec_socBodSetTime'
     *  Product: '<S26>/Product'
     */
    rtb_Equal7 = ((rtb_Switch_m1yp * KeSoc_sec_sampleTime) >
                  KeSoc_sec_socBodSetTime);

    /* MinMax: '<S24>/MaxofElements' */
    rtb_Switch_gefl = soc_DW.UnitDelay_DSTATE[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        rtb_Switch_gefl = fmaxf(rtb_Switch_gefl, soc_DW.UnitDelay_DSTATE[k]);
    }

    /* Sum: '<S24>/Sum' incorporates:
     *  UnitDelay: '<S1>/Unit Delay'
     */
    tmp = -0.0F;
    for (k = 0; k < SOC_NUM_OF_CELLS; k++)
    {
        tmp += soc_DW.UnitDelay_DSTATE[k];
    }

    /* Logic: '<S24>/AND' incorporates:
     *  Constant: '<S24>/KeSoc_V_tocAvrgCellVolt'
     *  Constant: '<S24>/KeSoc_V_tocMaxCellVolt'
     *  Constant: '<S24>/SOC_NUM_OF_CELLS'
     *  Constant: '<S31>/Constant'
     *  Inport: '<Root>/VeSoc_A_battCur'
     *  MinMax: '<S24>/MaxofElements'
     *  Product: '<S24>/Divide'
     *  RelationalOperator: '<S24>/GreaterThanOrEqual'
     *  RelationalOperator: '<S24>/GreaterThanOrEqual1'
     *  RelationalOperator: '<S31>/Compare'
     *  Sum: '<S24>/Sum'
     */
    rtb_AND_pv5x = ((rtb_Switch_gefl >= KeSoc_V_tocMaxCellVolt) && ((tmp /
                      (float32_t)((int32_t)SOC_NUM_OF_CELLS)) >=
                     KeSoc_V_tocAvrgCellVolt) && (VeSoc_A_battCur > 0.0F));

    /* Switch: '<S32>/Switch' incorporates:
     *  Constant: '<S32>/Increment'
     *  Constant: '<S32>/Init'
     *  Sum: '<S32>/Sum1'
     *  UnitDelay: '<S32>/UnitDelay'
     */
    if (rtb_AND_pv5x)
    {
        rtb_Switch_gefl = soc_DW.UnitDelay_DSTATE_gguj + 1.0F;
    }
    else
    {
        rtb_Switch_gefl = 0.0F;
    }

    /* End of Switch: '<S32>/Switch' */

    /* RelationalOperator: '<S32>/RelationalOperator' incorporates:
     *  Constant: '<S24>/KeSoc_sec_sampleTime'
     *  Constant: '<S24>/KeSoc_sec_socTocSetTime'
     *  Product: '<S32>/Product'
     */
    rtb_RelationalOperator_mlrg = ((rtb_Switch_gefl * KeSoc_sec_sampleTime) >
        KeSoc_sec_socTocSetTime);

    /* Switch: '<S3>/Switch' incorporates:
     *  Constant: '<S3>/CorrectionOnWake'
     *  Constant: '<S3>/SocInit'
     *  Constant: '<S3>/SocReset'
     *  Logic: '<S24>/AND1'
     *  RelationalOperator: '<S3>/Equal'
     *  RelationalOperator: '<S3>/Equal1'
     *  RelationalOperator: '<S3>/Equal2'
     *  Switch: '<S3>/Switch1'
     *  Switch: '<S3>/Switch4'
     *  Switch: '<S3>/Switch5'
     */
    if (VeSoc_nu_socState == SOC_STATE_CORRECTION_ON_WAKE)
    {
        /* Switch: '<S3>/Switch' */
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            VaSoc_frc_cellSoc[k] = soc_B.LaSoc_frc_cellSoc[k];
        }
    }
    else if (VeSoc_nu_socState == SOC_STATE_RESET)
    {
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            /* Switch: '<S3>/Switch' incorporates:
             *  Switch: '<S3>/Switch1'
             */
            VaSoc_frc_cellSoc[k] = soc_B.LaSoc_frc_cellSocOcv[k];
        }
    }
    else if (VeSoc_nu_socState == SOC_STATE_INIT)
    {
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            /* Switch: '<S3>/Switch' incorporates:
             *  Inport: '<Root>/VaSoc_frc_initialCellSoc'
             *  Switch: '<S3>/Switch1'
             *  Switch: '<S3>/Switch4'
             */
            VaSoc_frc_cellSoc[k] = VaSoc_frc_initialCellSoc[k];
        }
    }
    else if (rtb_AND_pv5x && rtb_RelationalOperator_mlrg)
    {
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            /* Switch: '<S3>/Switch' incorporates:
             *  Constant: '<S3>/KeSoc_frc_topOfChrgReset'
             *  Switch: '<S3>/Switch1'
             *  Switch: '<S3>/Switch4'
             *  Switch: '<S3>/Switch5'
             */
            VaSoc_frc_cellSoc[k] = KeSoc_frc_topOfChrgReset;
        }
    }
    else
    {
        /* Logic: '<S21>/AND1' incorporates:
         *  Switch: '<S3>/Switch1'
         *  Switch: '<S3>/Switch4'
         *  Switch: '<S3>/Switch5'
         */
        rtb_AND = (rtb_AND && rtb_Equal7);
        for (k = 0; k < SOC_NUM_OF_CELLS; k++)
        {
            /* Switch: '<S3>/Switch6' incorporates:
             *  Switch: '<S3>/Switch1'
             *  Switch: '<S3>/Switch4'
             *  Switch: '<S3>/Switch5'
             */
            if (rtb_AND)
            {
                /* Switch: '<S3>/Switch' incorporates:
                 *  Constant: '<S3>/KeSoc_frc_BotmOfDchReset'
                 */
                VaSoc_frc_cellSoc[k] = KeSoc_frc_BotmOfDchReset;
            }
            else
            {
                /* Switch: '<S3>/Switch' incorporates:
                 *  UnitDelay: '<S8>/Unit Delay4'
                 */
                VaSoc_frc_cellSoc[k] = soc_DW.UnitDelay4_DSTATE[k];
            }

            /* End of Switch: '<S3>/Switch6' */
        }
    }

    /* End of Switch: '<S3>/Switch' */
    for (k = 0; k < SOC_NUM_OF_CELLS; k++)
    {
        /* Sum: '<S28>/Subtract' */
        tmp = VaSoc_frc_cellSoc[k];

        /* Product: '<S28>/Product' incorporates:
         *  Constant: '<S28>/KeSoc_frc_socMaxLim'
         *  Inport: '<Root>/VaSoc_frc_cellSohc'
         *  Sum: '<S28>/Subtract'
         */
        VaSoc_frc_cellSohc_0 = VaSoc_frc_cellSohc[k];
        rtb_Product_dmnf[k] = (KeSoc_frc_socMaxLim - tmp) * VaSoc_frc_cellSohc_0;

        /* Product: '<S27>/Product' incorporates:
         *  Constant: '<S27>/Constant'
         *  Sum: '<S27>/Subtract'
         */
        rtb_Product_c0pa[k] = (tmp - KeSoc_frc_socMinLim) * VaSoc_frc_cellSohc_0;
    }

    /* MinMax: '<S27>/Min1' */
    tmp = rtb_Product_c0pa[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        tmp = fminf(tmp, rtb_Product_c0pa[k]);
    }

    /* MinMax: '<S28>/Min' */
    VaSoc_frc_cellSohc_0 = rtb_Product_dmnf[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        VaSoc_frc_cellSohc_0 = fminf(VaSoc_frc_cellSohc_0, rtb_Product_dmnf[k]);
    }

    /* Sum: '<S22>/Add' incorporates:
     *  MinMax: '<S27>/Min1'
     *  MinMax: '<S28>/Min'
     */
    VaSoc_frc_cellSohc_0 += tmp;

    /* Saturate: '<S22>/Saturation' */
    if (VaSoc_frc_cellSohc_0 > KeSoc_frc_socMaxLim)
    {
        VaSoc_frc_cellSohc_0 = KeSoc_frc_socMaxLim;
    }
    else if (VaSoc_frc_cellSohc_0 < KeSoc_nu_epsValue)
    {
        VaSoc_frc_cellSohc_0 = KeSoc_nu_epsValue;
    }
    else
    {
        /* no actions */
    }

    /* Product: '<S22>/Divide' incorporates:
     *  MinMax: '<S27>/Min1'
     *  Saturate: '<S22>/Saturation'
     */
    VeSoc_frc_packSoc = tmp / VaSoc_frc_cellSohc_0;

    /* Product: '<S22>/Divide1' incorporates:
     *  Constant: '<S22>/KeSoc_frc_userSocMaxLim'
     *  Constant: '<S22>/KeSoc_frc_userSocMinLim'
     *  Sum: '<S22>/Subtract'
     *  Sum: '<S22>/Subtract1'
     */
    VeSoc_frc_userSoc = (VeSoc_frc_packSoc - KeSoc_frc_userSocMinLim) /
        (KeSoc_frc_userSocMaxLim - KeSoc_frc_userSocMinLim);

    /* Saturate: '<S22>/Saturation1' */
    if (VeSoc_frc_userSoc > KeSoc_frc_socMaxLim)
    {
        /* Product: '<S22>/Divide1' incorporates:
         *  Saturate: '<S22>/Saturation1'
         */
        VeSoc_frc_userSoc = KeSoc_frc_socMaxLim;
    }
    else if (VeSoc_frc_userSoc < KeSoc_frc_socMinLim)
    {
        /* Product: '<S22>/Divide1' incorporates:
         *  Saturate: '<S22>/Saturation1'
         */
        VeSoc_frc_userSoc = KeSoc_frc_socMinLim;
    }
    else
    {
        /* no actions */
    }

    /* End of Saturate: '<S22>/Saturation1' */

    /* Saturate: '<S22>/Saturation2' */
    if (VeSoc_frc_packSoc > KeSoc_frc_socMaxLim)
    {
        /* Product: '<S22>/Divide' incorporates:
         *  Saturate: '<S22>/Saturation2'
         */
        VeSoc_frc_packSoc = KeSoc_frc_socMaxLim;
    }
    else if (VeSoc_frc_packSoc < KeSoc_frc_socMinLim)
    {
        /* Product: '<S22>/Divide' incorporates:
         *  Saturate: '<S22>/Saturation2'
         */
        VeSoc_frc_packSoc = KeSoc_frc_socMinLim;
    }
    else
    {
        /* no actions */
    }

    /* End of Saturate: '<S22>/Saturation2' */

    /* MinMax: '<S3>/soc_min' */
    VeSoc_frc_minCellSoc = VaSoc_frc_cellSoc[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        VeSoc_frc_minCellSoc = fminf(VeSoc_frc_minCellSoc, VaSoc_frc_cellSoc[k]);
    }

    /* End of MinMax: '<S3>/soc_min' */

    /* Logic: '<S23>/NOT' incorporates:
     *  UnitDelay: '<S23>/UnitDelay'
     */
    rtb_AND = !soc_DW.UnitDelay_DSTATE_pzjh;

    /* Switch: '<S23>/Switch' incorporates:
     *  Constant: '<S30>/Constant'
     *  Logic: '<S23>/AND'
     *  Logic: '<S23>/NOT'
     *  RelationalOperator: '<S30>/Compare'
     */
    if ((VeSoc_frc_minCellSoc < KeSoc_frc_lowSocSetThd) && rtb_AND)
    {
        /* Switch: '<S23>/Switch' incorporates:
         *  Constant: '<S23>/Constant'
         */
        VeSoc_bi_lowSocFault = true;
    }
    else
    {
        /* Switch: '<S23>/Switch' incorporates:
         *  Constant: '<S29>/Constant'
         *  Logic: '<S23>/AND1'
         *  RelationalOperator: '<S29>/Compare'
         *  UnitDelay: '<S23>/UnitDelay'
         */
        VeSoc_bi_lowSocFault = ((rtb_AND || (VeSoc_frc_minCellSoc <=
            KeSoc_frc_lowSocResetThd)) && soc_DW.UnitDelay_DSTATE_pzjh);
    }

    /* End of Switch: '<S23>/Switch' */

    /* MinMax: '<S3>/soc_max' */
    VeSoc_frc_maxCellSoc = VaSoc_frc_cellSoc[0];
    for (k = 1; k < SOC_NUM_OF_CELLS; k++)
    {
        VeSoc_frc_maxCellSoc = fmaxf(VeSoc_frc_maxCellSoc, VaSoc_frc_cellSoc[k]);
    }

    /* End of MinMax: '<S3>/soc_max' */

    /* Switch: '<S3>/Switch2' incorporates:
     *  Constant: '<S3>/CorrectionOnWake1'
     *  Constant: '<S3>/SocInit2'
     *  Constant: '<S3>/SocReset1'
     *  RelationalOperator: '<S3>/Equal3'
     *  RelationalOperator: '<S3>/Equal4'
     *  RelationalOperator: '<S3>/Equal5'
     *  Switch: '<S3>/Switch3'
     *  Switch: '<S3>/Switch7'
     */
    if (VeSoc_nu_socState == SOC_STATE_CORRECTION_ON_WAKE)
    {
        /* Switch: '<S3>/Switch2' */
        VeSoc_ms_battRestTime = soc_B.LeSoc_ms_restTiAfterWakeOnCorrn;
    }
    else if (VeSoc_nu_socState == SOC_STATE_RESET)
    {
        /* Switch: '<S3>/Switch3' incorporates:
         *  Switch: '<S3>/Switch2'
         */
        VeSoc_ms_battRestTime = soc_B.LeSoc_ms_restTiAfterSocReset;
    }
    else if (VeSoc_nu_socState == SOC_STATE_INIT)
    {
        /* Switch: '<S3>/Switch7' incorporates:
         *  Inport: '<Root>/VeSoc_ms_initialBattRestTime'
         *  Switch: '<S3>/Switch2'
         *  Switch: '<S3>/Switch3'
         */
        VeSoc_ms_battRestTime = VeSoc_ms_initialBattRestTime;
    }
    else
    {
        /* Switch: '<S3>/Switch2' incorporates:
         *  Switch: '<S3>/Switch3'
         *  Switch: '<S3>/Switch7'
         */
        VeSoc_ms_battRestTime = soc_B.LeSoc_ms_battRestTime;
    }

    /* End of Switch: '<S3>/Switch2' */
    for (k = 0; k < SOC_NUM_OF_CELLS; k++)
    {
        /* SignalConversion generated from: '<S3>/LaSoc_ms_tauDepolar' */
        VaSoc_ms_tauDepolar[k] = soc_B.LaSoc_ms_tauDepolar[k];
    }

    /* Switch: '<S26>/Switch1' incorporates:
     *  Logic: '<S26>/LogicalOperator'
     */
    if (!rtb_Equal7)
    {
        /* Update for UnitDelay: '<S26>/UnitDelay' */
        soc_DW.UnitDelay_DSTATE_lxmr = rtb_Switch_m1yp;
    }

    /* End of Switch: '<S26>/Switch1' */

    /* Switch: '<S32>/Switch1' incorporates:
     *  Logic: '<S32>/LogicalOperator'
     */
    if (!rtb_RelationalOperator_mlrg)
    {
        /* Update for UnitDelay: '<S32>/UnitDelay' */
        soc_DW.UnitDelay_DSTATE_gguj = rtb_Switch_gefl;
    }

    /* End of Switch: '<S32>/Switch1' */

    /* Update for UnitDelay: '<S23>/UnitDelay' */
    soc_DW.UnitDelay_DSTATE_pzjh = VeSoc_bi_lowSocFault;
}

/* Model step function */
void Soc_task(void)
{
    int32_t i;

    /* Outputs for Atomic SubSystem: '<Root>/soc'
     *
     * Block description for '<Root>/soc':
     *  SOC Estimation Algorithm Main/Top level subsystem
     */
    /* Switch: '<S1>/Switch' incorporates:
     *  Constant: '<S1>/Constant'
     *  Inport: '<Root>/VaSoc_V_cellVolt'
     *  Inport: '<Root>/VaSoc_nu_cellVoltVldt'
     *  RelationalOperator: '<S1>/Equal'
     *  UnitDelay: '<S1>/Unit Delay'
     */
    for (i = 0; i < SOC_NUM_OF_CELLS; i++)
    {
        if (VaSoc_nu_cellVoltVldt[i] == DUKOSI_DATA_VALID)
        {
            soc_DW.UnitDelay_DSTATE[i] = VaSoc_V_cellVolt[i];
        }
    }

    /* End of Switch: '<S1>/Switch' */

    /* Outputs for Atomic SubSystem: '<S1>/SocStateMachine_Subsys' */
    /* Chart: '<S4>/SOC_StateMachine_Chart' incorporates:
     *  Inport: '<Root>/VeBattsm_nu_battState'
     *  Inport: '<Root>/VeSoc_bi_nvmImportStatus'
     *  UnitDelay: '<S1>/UnitDelay3'
     *  UnitDelay: '<S1>/UnitDelay4'
     *  UnitDelay: '<S1>/UnitDelay8'
     */
    if (soc_DW.is_active_c3_soc == (uint8_t)0)
    {
        soc_DW.is_active_c3_soc = 1U;
        soc_DW.is_c3_soc = soc_IN_INIT_STATE;
        soc_B.LeSoc_nu_socState = SOC_STATE_INIT;
        soc_B.LeSoc_bi_socInNormalStateFlg = false;
    }
    else
    {
        switch (soc_DW.is_c3_soc)
        {
          case soc_IN_CORRECTION_ON_WAKE_STATE:
            soc_B.LeSoc_nu_socState = SOC_STATE_CORRECTION_ON_WAKE;
            if (soc_DW.UnitDelay3_DSTATE_hjte && ((VeBattsm_nu_battState ==
                    BATTSM_STATE_CHARGE) || (VeBattsm_nu_battState ==
                    BATTSM_STATE_DRIVE)))
            {
                soc_DW.is_c3_soc = soc_IN_NORMAL_STATE;
                soc_B.LeSoc_nu_socState = SOC_STATE_NORMAL;
            }
            break;

          case soc_IN_INIT_STATE:
            soc_B.LeSoc_nu_socState = SOC_STATE_INIT;
            if (VeSoc_bi_nvmImportStatus && ((VeBattsm_nu_battState ==
                    BATTSM_STATE_STANDBY_INIT) || (VeBattsm_nu_battState ==
                    BATTSM_STATE_STANDBY_NOT_READY) || (VeBattsm_nu_battState ==
                  BATTSM_STATE_STANDBY_READY)))
            {
                soc_DW.is_c3_soc = soc_IN_CORRECTION_ON_WAKE_STATE;
                soc_B.LeSoc_nu_socState = SOC_STATE_CORRECTION_ON_WAKE;
            }
            else if (!VeSoc_bi_nvmImportStatus && ((VeBattsm_nu_battState ==
                       BATTSM_STATE_STANDBY_INIT) || (VeBattsm_nu_battState ==
                       BATTSM_STATE_STANDBY_NOT_READY) || (VeBattsm_nu_battState
                       == BATTSM_STATE_STANDBY_READY)))
            {
                soc_DW.is_c3_soc = soc_IN_RESET_STATE;
                soc_B.LeSoc_nu_socState = SOC_STATE_RESET;
            }
            else
            {
                /* no actions */
            }
            break;

          case soc_IN_NORMAL_STATE:
            soc_B.LeSoc_nu_socState = SOC_STATE_NORMAL;
            soc_B.LeSoc_bi_socInNormalStateFlg = true;
            soc_B.LeSoc_bi_ccReset = soc_DW.UnitDelay8_DSTATE;
            break;

          default:
            /* case IN_RESET_STATE: */
            soc_B.LeSoc_nu_socState = SOC_STATE_RESET;
            if (soc_DW.UnitDelay4_DSTATE_dlsb && ((VeBattsm_nu_battState ==
                    BATTSM_STATE_CHARGE) || (VeBattsm_nu_battState ==
                    BATTSM_STATE_DRIVE)))
            {
                soc_DW.is_c3_soc = soc_IN_NORMAL_STATE;
                soc_B.LeSoc_nu_socState = SOC_STATE_NORMAL;
            }
            break;
        }
    }

    /* End of Chart: '<S4>/SOC_StateMachine_Chart' */
    /* End of Outputs for SubSystem: '<S1>/SocStateMachine_Subsys' */

    /* Switch: '<S1>/Switch1' incorporates:
     *  Constant: '<S1>/Constant1'
     *  Inport: '<Root>/VaSoc_degC_cellTmp'
     *  Inport: '<Root>/VaSoc_nu_cellTmpVldt'
     *  RelationalOperator: '<S1>/Equal1'
     *  UnitDelay: '<S1>/Unit Delay1'
     */
    for (i = 0; i < SOC_NUM_OF_CELLS; i++)
    {
        if (VaSoc_nu_cellTmpVldt[i] == DUKOSI_DATA_VALID)
        {
            soc_DW.UnitDelay1_DSTATE[i] = VaSoc_degC_cellTmp[i];
        }
    }

    /* End of Switch: '<S1>/Switch1' */

    /* Outputs for Atomic SubSystem: '<S1>/SocCalculation_Subsys' */
    /* RelationalOperator: '<S6>/Compare' incorporates:
     *  Constant: '<S6>/Constant'
     */
    soc_B.Compare = (soc_B.LeSoc_nu_socState == SOC_STATE_RESET);

    /* Outputs for Enabled SubSystem: '<S2>/SocResetState' */
    Soc_socReset();

    /* End of Outputs for SubSystem: '<S2>/SocResetState' */

    /* RelationalOperator: '<S7>/Compare' incorporates:
     *  Constant: '<S7>/Constant'
     */
    soc_B.Compare_go2r = (soc_B.LeSoc_nu_socState == SOC_STATE_NORMAL);

    /* RelationalOperator: '<S5>/Compare' incorporates:
     *  Constant: '<S5>/Constant'
     */
    soc_B.Compare_f2dn = (soc_B.LeSoc_nu_socState ==
                          SOC_STATE_CORRECTION_ON_WAKE);

    /* Outputs for Enabled SubSystem: '<S2>/SocCorrectionOnWakeState' */
    Soc_socCorrectionOnWake();

    /* End of Outputs for SubSystem: '<S2>/SocCorrectionOnWakeState' */

    /* Outputs for Enabled SubSystem: '<S2>/NormalState' */
    Soc_socNormal();

    /* End of Outputs for SubSystem: '<S2>/NormalState' */
    /* End of Outputs for SubSystem: '<S1>/SocCalculation_Subsys' */

    /* Outputs for Atomic SubSystem: '<S1>/SocOutputs_Subsys' */
    Soc_socOutputs();

    /* End of Outputs for SubSystem: '<S1>/SocOutputs_Subsys' */
    /* End of Outputs for SubSystem: '<Root>/soc' */
}

/* Model initialize function */
void Soc_init(void)
{
    /* Registration code */

    /* block I/O */
    {
        soc_B.LeSoc_nu_socState = SOC_STATE_INIT;
    }

    /* exported global signals */
    VeSoc_ms_battRestTime = 0U;

    {
        int32_t i;
        for (i = 0; i < SOC_NUM_OF_CELLS; i++)
        {
            VaSoc_frc_cellSocOcv[i] = 0.0F;
        }
    }

    {
        int32_t i;
        for (i = 0; i < SOC_NUM_OF_CELLS; i++)
        {
            VaSoc_frc_cellSocCc[i] = 0.0F;
        }
    }

    {
        int32_t i;
        for (i = 0; i < SOC_NUM_OF_CELLS; i++)
        {
            VaSoc_frc_cellSoc[i] = 0.0F;
        }
    }

    VeSoc_frc_userSoc = 0.0F;
    VeSoc_frc_packSoc = 0.0F;
    VeSoc_frc_minCellSoc = 0.0F;
    VeSoc_frc_maxCellSoc = 0.0F;

    {
        int32_t i;
        for (i = 0; i < SOC_NUM_OF_CELLS; i++)
        {
            VaSoc_ms_tauDepolar[i] = 0.0F;
        }
    }

    VeSoc_nu_socState = SOC_STATE_INIT;
    VeSoc_bi_lowSocFault = false;

    /* external inputs */
    (void)memset(&VaSoc_frc_initialCellSoc[0], 0, (uint32_t)SOC_NUM_OF_CELLS *
                 sizeof(float32_t));
    (void)memset(&VaSoc_V_cellVolt[0], 0, (uint32_t)SOC_NUM_OF_CELLS * sizeof
                 (float32_t));
    (void)memset(&VaSoc_degC_cellTmp[0], 0, (uint32_t)SOC_NUM_OF_CELLS * sizeof
                 (float32_t));
    (void)memset(&VaSoc_frc_cellSohc[0], 0, (uint32_t)SOC_NUM_OF_CELLS * sizeof
                 (float32_t));
    (void)memset(&VaSoc_nu_cellVoltVldt[0], 0, (uint32_t)SOC_NUM_OF_CELLS *
                 sizeof(Dukosi_Validity_t));
    (void)memset(&VaSoc_nu_cellTmpVldt[0], 0, (uint32_t)SOC_NUM_OF_CELLS *
                 sizeof(Dukosi_Validity_t));
    VeSoc_bi_nvmImportStatus = false;
    VeSoc_A_battCur = 0.0F;
    VeSoc_degC_minCellTmp = 0.0F;
    VeSoc_degC_maxCellTmp = 0.0F;
    VeSoc_ms_battAsleepTime = 0U;
    VeSoc_ms_initialBattRestTime = 0U;
    VeBattsm_nu_battState = BATTSM_STATE_STANDBY_INIT;
    VeSoc_bi_socReset = false;

    /* SystemInitialize for Atomic SubSystem: '<Root>/soc'
     *
     * Block description for '<Root>/soc':
     *  SOC Estimation Algorithm Main/Top level subsystem
     */
    /* SystemInitialize for Atomic SubSystem: '<S1>/SocStateMachine_Subsys' */
    /* SystemInitialize for Chart: '<S4>/SOC_StateMachine_Chart' */
    soc_B.LeSoc_nu_socState = SOC_STATE_INIT;

    /* End of SystemInitialize for SubSystem: '<S1>/SocStateMachine_Subsys' */

    /* SystemInitialize for Atomic SubSystem: '<S1>/SocCalculation_Subsys' */
    /* SystemInitialize for Enabled SubSystem: '<S2>/NormalState' */
    Soc_socNormal_Init();

    /* End of SystemInitialize for SubSystem: '<S2>/NormalState' */
    /* End of SystemInitialize for SubSystem: '<S1>/SocCalculation_Subsys' */
    /* End of SystemInitialize for SubSystem: '<Root>/soc' */
}
