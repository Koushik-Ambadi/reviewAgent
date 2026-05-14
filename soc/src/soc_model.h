#ifndef soc_model_h_
#define soc_model_h_

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

#ifndef soc_COMMON_INCLUDES_
#define soc_COMMON_INCLUDES_
#include <stdbool.h>
#include <stdint.h>
#include "Platform_Types.h"
#endif                                 /* soc_COMMON_INCLUDES_ */

/* Exported data define */

/* Definition for custom storage class: Define */
#define SOC_LUT_SOC_ARRAY_SIZE         21                       
#define SOC_LUT_TEMP_ARRAY_SIZE        13                       

/* Includes for objects with custom storage classes */
#include "soc.h"

/*
 * Check that imported macros with storage class "ImportedDefine" are defined
 */
#ifndef SOC_NUM_OF_CELLS
#error The value of parameter "SOC_NUM_OF_CELLS" is not defined
#endif

/*
 * Registered constraints for dimension variants
 */
/* Constraint 'SOC_LUT_TEMP_ARRAY_SIZE == 13' registered by:
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
#if SOC_LUT_TEMP_ARRAY_SIZE != 13
# error "The preprocessor definition 'SOC_LUT_TEMP_ARRAY_SIZE' must be equal to '13'"
#endif

/* Constraint 'SOC_LUT_SOC_ARRAY_SIZE == 21' registered by:
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
#if SOC_LUT_SOC_ARRAY_SIZE != 21
# error "The preprocessor definition 'SOC_LUT_SOC_ARRAY_SIZE' must be equal to '21'"
#endif

/* Block states (default storage) for system '<S8>/SocCorrection_SubSys' */
typedef struct
{
    bool UnitDelay_DSTATE;             /* '<S14>/Unit Delay' */
}
DW_Soc_socCorrection_T;

/* Block signals (default storage) */
typedef struct
{
    uint32_t LeSoc_ms_restTiAfterSocReset;/* '<S10>/Constant' */
    uint32_t LeSoc_ms_restTiAfterWakeOnCorrn;/* '<S9>/Switch' */
    uint32_t LeSoc_ms_battRestTime;    /* '<S13>/DatatypeConversion' */
    float32_t OutportBufferForLaSoc_frc_socOc[SOC_NUM_OF_CELLS];/* '<S10>/OcvBasedSocCalc_Subsys' */
    float32_t LaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS];/* '<S20>/OcvBasedSocLookupTable' */
    float32_t LaSoc_frc_cellSoc[SOC_NUM_OF_CELLS];/* '<S18>/Switch1' */
    float32_t LaSoc_frc_cellSocOcv_gyx2[SOC_NUM_OF_CELLS];/* '<S17>/OcvBasedSocLookupTable' */
    float32_t LaSoc_ms_tauDepolar[SOC_NUM_OF_CELLS];/* '<S15>/Product1' */
    float32_t LaSoc_frc_cellSocOcv_kin5[SOC_NUM_OF_CELLS];/* '<S12>/OcvBasedSocLookupTable' */
    float32_t LaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS];/* '<S11>/Saturation' */
    Soc_State_t LeSoc_nu_socState;     /* '<S4>/SOC_StateMachine_Chart' */
    bool LeSoc_bi_ccReset;             /* '<S4>/SOC_StateMachine_Chart' */
    bool LeSoc_bi_socInNormalStateFlg; /* '<S4>/SOC_StateMachine_Chart' */
    bool Compare;                      /* '<S6>/Compare' */
    bool Compare_go2r;                 /* '<S7>/Compare' */
    bool Compare_f2dn;                 /* '<S5>/Compare' */
    bool UnitDelay2;                   /* '<S8>/Unit Delay2' */
}
B_soc_T;

/* Block states (default storage) for system '<Root>' */
typedef struct
{
    float32_t UnitDelay_DSTATE[SOC_NUM_OF_CELLS];/* '<S1>/Unit Delay' */
    float32_t UnitDelay1_DSTATE[SOC_NUM_OF_CELLS];/* '<S1>/Unit Delay1' */
    float32_t UnitDelay_DSTATE_lxmr;   /* '<S26>/UnitDelay' */
    float32_t UnitDelay_DSTATE_gguj;   /* '<S32>/UnitDelay' */
    float32_t UnitDelay_DSTATE_fcnr[SOC_NUM_OF_CELLS];/* '<S8>/Unit Delay' */
    float32_t UnitDelay3_DSTATE[SOC_NUM_OF_CELLS];/* '<S8>/Unit Delay3' */
    float32_t UnitDelay4_DSTATE[SOC_NUM_OF_CELLS];/* '<S8>/Unit Delay4' */
    float32_t UnitDelay2_DSTATE;       /* '<S16>/UnitDelay2' */
    float32_t Integrator_DSTATE;       /* '<S11>/Integrator' */
    bool UnitDelay3_DSTATE_hjte;       /* '<S1>/UnitDelay3' */
    bool UnitDelay4_DSTATE_dlsb;       /* '<S1>/UnitDelay4' */
    bool UnitDelay8_DSTATE;            /* '<S1>/UnitDelay8' */
    bool UnitDelay_DSTATE_pzjh;        /* '<S23>/UnitDelay' */
    bool UnitDelay1_DSTATE_fjxo;       /* '<S8>/Unit Delay1' */
    bool UnitDelay2_DSTATE_mulm;       /* '<S8>/Unit Delay2' */
    int8_t Integrator_PrevResetState;  /* '<S11>/Integrator' */
    uint8_t is_active_c3_soc;          /* '<S4>/SOC_StateMachine_Chart' */
    uint8_t is_c3_soc;                 /* '<S4>/SOC_StateMachine_Chart' */
    DW_Soc_socCorrection_T SocCorrection_SubSys_gqbb;/* '<S9>/SocCorrection_SubSys' */
    DW_Soc_socCorrection_T SocCorrection_SubSys;/* '<S8>/SocCorrection_SubSys' */
}
DW_soc_T;

/* Constant parameters (default storage) */
typedef struct
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
    uint32_t pooled7[2];
}
ConstP_soc_T;

/* Block signals (default storage) */
extern B_soc_T soc_B;

/* Block states (default storage) */
extern DW_soc_T soc_DW;

/* Constant parameters (default storage) */
extern const ConstP_soc_T soc_ConstP;

/*
 * Exported Global Signals
 *
 * Note: Exported global signals are block signals with an exported global
 * storage class designation.  Code generation will declare the memory for
 * these signals and export their symbols.
 *
 */
extern bool VeSoc_bi_nvmImportStatus;  /* '<Root>/VeSoc_bi_nvmImportStatus'
                                        * NVM import status is successfull or not
                                        */
extern float32_t VeSoc_A_battCur;      /* '<Root>/VeSoc_A_battCur'
                                        * Battery current input
                                        */
extern float32_t VaSoc_frc_initialCellSoc[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_frc_initialCellSoc'
                                                             * SOC stored in NVM
                                                             */
extern float32_t VaSoc_V_cellVolt[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_V_cellVolt'
                                                     * Cell voltage input
                                                     */
extern float32_t VaSoc_degC_cellTmp[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_degC_cellTmp'
                                                       * Cell temperature
                                                       */
extern float32_t VeSoc_degC_minCellTmp;/* '<Root>/VeSoc_degC_minCellTmp'
                                        * Minimum cell temperature
                                        */
extern float32_t VeSoc_degC_maxCellTmp;/* '<Root>/VeSoc_degC_maxCellTmp'
                                        * Maximum cell temperature
                                        */
extern uint32_t VeSoc_ms_battAsleepTime;/* '<Root>/VeSoc_ms_battAsleepTime'
                                         * Battery Asleep time calculated by RTC
                                         */
extern uint32_t VeSoc_ms_initialBattRestTime;/* '<Root>/VeSoc_ms_initialBattRestTime'
                                              * Battery rest time stored in NVM used for OCV wake on correction
                                              */
extern float32_t VaSoc_frc_cellSohc[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_frc_cellSohc'
                                                       * Cell SOHC
                                                       */
extern Battsm_State_t VeBattsm_nu_battState;/* '<Root>/VeBattsm_nu_battState' */
extern Dukosi_Validity_t VaSoc_nu_cellVoltVldt[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_nu_cellVoltVldt' */
extern Dukosi_Validity_t VaSoc_nu_cellTmpVldt[SOC_NUM_OF_CELLS];/* '<Root>/VaSoc_nu_cellTmpVldt' */
extern bool VeSoc_bi_socReset;         /* '<Root>/VeSoc_bi_socReset' */
extern uint32_t VeSoc_ms_battRestTime; /* '<S3>/Switch2'
                                        * Calculated battery rest time output
                                        */
extern float32_t VaSoc_frc_cellSocOcv[SOC_NUM_OF_CELLS];/* '<S3>/Switch9' */
extern float32_t VaSoc_frc_cellSocCc[SOC_NUM_OF_CELLS];/* '<S3>/Switch8' */
extern float32_t VaSoc_frc_cellSoc[SOC_NUM_OF_CELLS];/* '<S3>/Switch'
                                                      * Calculated cell level SOC
                                                      */
extern float32_t VeSoc_frc_userSoc;    /* '<S22>/Saturation1'
                                        * Calculated user level SOC
                                        */
extern float32_t VeSoc_frc_packSoc;    /* '<S22>/Saturation2'
                                        * Calculated pack level SOC
                                        */
extern float32_t VeSoc_frc_minCellSoc; /* '<S3>/soc_min'
                                        * Minimum cell SOC
                                        */
extern float32_t VeSoc_frc_maxCellSoc; /* '<S3>/soc_max'
                                        * Maximum cell SOC
                                        */
extern float32_t VaSoc_ms_tauDepolar[SOC_NUM_OF_CELLS];/* '<S3>/LaSoc_ms_tauDepolar'
                                                        * Calculated tau depolar values
                                                        */
extern Soc_State_t VeSoc_nu_socState;  /* '<S3>/LeSoc_nu_socState' */
extern bool VeSoc_bi_lowSocFault;      /* '<S23>/Switch'
                                        * Low soc fault output
                                        */

/* Model entry point functions */
extern void Soc_init(void);
extern void Soc_task(void);

/*-
 * The generated code includes comments that allow you to trace directly
 * back to the appropriate location in the model.  The basic format
 * is <system>/block_name, where system is the system number (uniquely
 * assigned by Simulink) and block_name is the name of the block.
 *
 * Use the MATLAB hilite_system command to trace the generated code back
 * to the model.  For example,
 *
 * hilite_system('<S3>')    - opens system 3
 * hilite_system('<S3>/Kp') - opens and selects block Kp which resides in S3
 *
 * Here is the system hierarchy for this model
 *
 * '<Root>' : 'soc'
 * '<S1>'   : 'soc/soc'
 * '<S2>'   : 'soc/soc/SocCalculation_Subsys'
 * '<S3>'   : 'soc/soc/SocOutputs_Subsys'
 * '<S4>'   : 'soc/soc/SocStateMachine_Subsys'
 * '<S5>'   : 'soc/soc/SocCalculation_Subsys/CompareToConstant'
 * '<S6>'   : 'soc/soc/SocCalculation_Subsys/CompareToConstant1'
 * '<S7>'   : 'soc/soc/SocCalculation_Subsys/CompareToConstant2'
 * '<S8>'   : 'soc/soc/SocCalculation_Subsys/NormalState'
 * '<S9>'   : 'soc/soc/SocCalculation_Subsys/SocCorrectionOnWakeState'
 * '<S10>'  : 'soc/soc/SocCalculation_Subsys/SocResetState'
 * '<S11>'  : 'soc/soc/SocCalculation_Subsys/NormalState/CoulombCounting_Subsys'
 * '<S12>'  : 'soc/soc/SocCalculation_Subsys/NormalState/OcvBasedSocCalc_Subsys'
 * '<S13>'  : 'soc/soc/SocCalculation_Subsys/NormalState/RestTimeAccumulation'
 * '<S14>'  : 'soc/soc/SocCalculation_Subsys/NormalState/SocCorrection_SubSys'
 * '<S15>'  : 'soc/soc/SocCalculation_Subsys/NormalState/TauDepolarLookup_Subsys'
 * '<S16>'  : 'soc/soc/SocCalculation_Subsys/NormalState/RestTimeAccumulation/RestTimeAccumulation_Timer'
 * '<S17>'  : 'soc/soc/SocCalculation_Subsys/SocCorrectionOnWakeState/OcvBasedSocCalc_Subsys'
 * '<S18>'  : 'soc/soc/SocCalculation_Subsys/SocCorrectionOnWakeState/SocCorrection_SubSys'
 * '<S19>'  : 'soc/soc/SocCalculation_Subsys/SocCorrectionOnWakeState/TauDepolarLookup_Subsys'
 * '<S20>'  : 'soc/soc/SocCalculation_Subsys/SocResetState/OcvBasedSocCalc_Subsys'
 * '<S21>'  : 'soc/soc/SocOutputs_Subsys/BottomOfDischargeResetSubsys'
 * '<S22>'  : 'soc/soc/SocOutputs_Subsys/CalculatePackSoc_Subsys'
 * '<S23>'  : 'soc/soc/SocOutputs_Subsys/SocFaults'
 * '<S24>'  : 'soc/soc/SocOutputs_Subsys/TopOfChargeResetSubsys'
 * '<S25>'  : 'soc/soc/SocOutputs_Subsys/BottomOfDischargeResetSubsys/CompareToConstant'
 * '<S26>'  : 'soc/soc/SocOutputs_Subsys/BottomOfDischargeResetSubsys/TimerLimit'
 * '<S27>'  : 'soc/soc/SocOutputs_Subsys/CalculatePackSoc_Subsys/CapacityRemaining'
 * '<S28>'  : 'soc/soc/SocOutputs_Subsys/CalculatePackSoc_Subsys/CapacityToFullCharge'
 * '<S29>'  : 'soc/soc/SocOutputs_Subsys/SocFaults/KeSoc_frc_lowSocResetThd'
 * '<S30>'  : 'soc/soc/SocOutputs_Subsys/SocFaults/KeSoc_frc_lowSocSetThd'
 * '<S31>'  : 'soc/soc/SocOutputs_Subsys/TopOfChargeResetSubsys/CompareToConstant2'
 * '<S32>'  : 'soc/soc/SocOutputs_Subsys/TopOfChargeResetSubsys/TimerLimitCalculation'
 * '<S33>'  : 'soc/soc/SocStateMachine_Subsys/SOC_StateMachine_Chart'
 */

/*-
 * Requirements for '<Root>': soc

 */
#endif                                 /* soc_model_h_ */
