/*==================================================================================================
*   Project              : RTD AUTOSAR 4.7 
*   Platform             : CORTEXM
*   Peripheral           : SIUL2
*   Dependencies         : none
*
*   Autosar Version      : 4.7.0
*   Autosar Revision     : ASR_REL_4_7_REV_0000
*   Autosar Conf.Variant :
*   SW Version           : 6.0.0
*   Build Version        : S32K3_S32M27x_Real-Time_Drivers_AUTOSAR_R21-11_Version_6_0_0_D2506_ASR_REL_4_7_REV_0000_20250610
*
*   Copyright 2020 - 2025 NXP
*
*   NXP Confidential. This software is owned or controlled by NXP and may only be
*   used strictly in accordance with the applicable license terms. By expressly
*   accepting such terms or by downloading, installing, activating and/or otherwise
*   using the software, you are agreeing that you have read, and that you agree to
*   comply with and are bound by, such license terms. If you do not agree to be
*   bound by the applicable license terms, then you may not retain, install,
*   activate or otherwise use the software.
==================================================================================================*/

#ifndef SIUL2_PORT_IP_CFG_H
#define SIUL2_PORT_IP_CFG_H

/**
*   @file      Siul2_Port_Ip_Cfg.h
*
*   @addtogroup Port_CFG
*   @{
*/

#ifdef __cplusplus
extern "C"{
#endif


/*==================================================================================================
                                         INCLUDE FILES
 1) system and project includes
 2) needed interfaces from external units
 3) internal and external interfaces from this unit
==================================================================================================*/
#include "S32K344_SIUL2.h"
#include "Siul2_Port_Ip_Types.h"

/*==================================================================================================
*                              SOURCE FILE VERSION INFORMATION
==================================================================================================*/
#define SIUL2_PORT_IP_VENDOR_ID_CFG_H                       43
#define SIUL2_PORT_IP_AR_RELEASE_MAJOR_VERSION_CFG_H        4
#define SIUL2_PORT_IP_AR_RELEASE_MINOR_VERSION_CFG_H        7
#define SIUL2_PORT_IP_AR_RELEASE_REVISION_VERSION_CFG_H     0
#define SIUL2_PORT_IP_SW_MAJOR_VERSION_CFG_H                6
#define SIUL2_PORT_IP_SW_MINOR_VERSION_CFG_H                0
#define SIUL2_PORT_IP_SW_PATCH_VERSION_CFG_H                0

/*==================================================================================================
*                                     FILE VERSION CHECKS
==================================================================================================*/
/* Check if the files Siul2_Port_Ip_Cfg.h and Siul2_Port_Ip_Types.h are of the same version */
#if (SIUL2_PORT_IP_VENDOR_ID_CFG_H != SIUL2_PORT_IP_TYPES_VENDOR_ID_H)
    #error "Siul2_Port_Ip_Cfg.h and Siul2_Port_Ip_Types.h have different vendor ids"
#endif
/* Check if Siul2_Port_Ip_Cfg.h and Siul2_Port_Ip_Types.h are of the same Autosar version */
#if ((SIUL2_PORT_IP_AR_RELEASE_MAJOR_VERSION_CFG_H    != SIUL2_PORT_IP_TYPES_AR_RELEASE_MAJOR_VERSION_H) || \
     (SIUL2_PORT_IP_AR_RELEASE_MINOR_VERSION_CFG_H    != SIUL2_PORT_IP_TYPES_AR_RELEASE_MINOR_VERSION_H) || \
     (SIUL2_PORT_IP_AR_RELEASE_REVISION_VERSION_CFG_H != SIUL2_PORT_IP_TYPES_AR_RELEASE_REVISION_VERSION_H) \
    )
    #error "AutoSar Version Numbers of Siul2_Port_Ip_Cfg.h and Siul2_Port_Ip_Types.h are different"
#endif
/* Check if Siul2_Port_Ip_Cfg.h and Siul2_Port_Ip_Types.h are of the same Software version */
#if ((SIUL2_PORT_IP_SW_MAJOR_VERSION_CFG_H != SIUL2_PORT_IP_TYPES_SW_MAJOR_VERSION_H) || \
     (SIUL2_PORT_IP_SW_MINOR_VERSION_CFG_H != SIUL2_PORT_IP_TYPES_SW_MINOR_VERSION_H) || \
     (SIUL2_PORT_IP_SW_PATCH_VERSION_CFG_H != SIUL2_PORT_IP_TYPES_SW_PATCH_VERSION_H)    \
    )
    #error "Software Version Numbers of Siul2_Port_Ip_Cfg.h and Siul2_Port_Ip_Types.h are different"
#endif
/*==================================================================================================
                                           CONSTANTS
==================================================================================================*/

/*==================================================================================================
                                      DEFINES AND MACROS
==================================================================================================*/
#define SIUL2_MSCR_SSS_MASK                      (0xFU)
#define SIUL2_MSCR_SSS_SHIFT                     (0U)
#define SIUL2_MSCR_SSS_WIDTH                     (4U)
#define SIUL2_MSCR_SSS(x)                        (((uint32)(((uint32)(x)) << SIUL2_MSCR_SSS_SHIFT)) & SIUL2_MSCR_SSS_MASK)

#define SIUL2_MSCR_SRE_MASK                      (0x4000U)
#define SIUL2_MSCR_SRE_SHIFT                     (14U)
#define SIUL2_MSCR_SRE_WIDTH                     (1U)
#define SIUL2_MSCR_SRE(x)                        (((uint32)(((uint32)(x)) << SIUL2_MSCR_SRE_SHIFT)) & SIUL2_MSCR_SRE_MASK)


/*! @brief Definitions for PortContainer_0_BOARD_InitPeripherals Functional Group */

/*! @brief User number of configured pins */
#define NUM_OF_CONFIGURED_PINS_PortContainer_0_BOARD_InitPeripherals 116

#define PORT_START_SEC_CONFIG_DATA_UNSPECIFIED
#include "Port_MemMap.h"

/*! @brief User configuration structure */
extern const Siul2_Port_Ip_PinSettingsConfig g_pin_mux_InitConfigArr_PortContainer_0_BOARD_InitPeripherals[NUM_OF_CONFIGURED_PINS_PortContainer_0_BOARD_InitPeripherals];

#define PORT_STOP_SEC_CONFIG_DATA_UNSPECIFIED
#include "Port_MemMap.h"

/*! @brief Defines for user pin and port configurations */
#define ECAN_TXD_PIN            12u
#define ECAN_TXD_PORT           PTE_L_HALF
#define ECAN_RXD_PIN            1u
#define ECAN_RXD_PORT           PTD_H_HALF
#define BCAN_TXD_PIN            0u
#define BCAN_TXD_PORT           PTC_L_HALF
#define BCAN_RXD_PIN            1u
#define BCAN_RXD_PORT           PTC_L_HALF
#define BCAN_ERR_N_PIN          9u
#define BCAN_ERR_N_PORT         PTD_L_HALF
#define BCAN_EN_PIN             8u
#define BCAN_EN_PORT            PTD_L_HALF
#define BCAN_WAKE_PIN           1u
#define BCAN_WAKE_PORT          PTC_H_HALF
#define BCAN_STB_PIN            0u
#define BCAN_STB_PORT           PTC_H_HALF
#define DUKOSI_DATA_RDY_PIN     10u
#define DUKOSI_DATA_RDY_PORT    PTB_H_HALF
#define DUKOSI_SPI_MISO_PIN     12u
#define DUKOSI_SPI_MISO_PORT    PTB_H_HALF
#define DUKOSI_SPI_MOSI_PIN     11u
#define DUKOSI_SPI_MOSI_PORT    PTB_H_HALF
#define DUKOSI_SPI_CLK_PIN      15u
#define DUKOSI_SPI_CLK_PORT     PTC_L_HALF
#define DUKOSI_SPI_CS0_PIN      9u
#define DUKOSI_SPI_CS0_PORT     PTB_H_HALF
#define CAN_STB_PIN             4u
#define CAN_STB_PORT            PTC_H_HALF
#define CAN_EN_PIN              5u
#define CAN_EN_PORT             PTC_H_HALF
#define DUKOSI_FAULT_PIN        14u
#define DUKOSI_FAULT_PORT       PTC_L_HALF
#define DUKOSI_nFAULT_PIN       3u
#define DUKOSI_nFAULT_PORT      PTB_L_HALF
#define LPSPI0_PCS0_PIN         4u
#define LPSPI0_PCS0_PORT        PTE_L_HALF
#define LPSPI0_SOUT_PIN         2u
#define LPSPI0_SOUT_PORT        PTE_L_HALF
#define LPSPI0_SCK_PIN          1u
#define LPSPI0_SCK_PORT         PTE_L_HALF
#define LPSPI0_SIN_PIN          0u
#define LPSPI0_SIN_PORT         PTE_L_HALF
#define LPSPI4_SIN_PIN          11u
#define LPSPI4_SIN_PORT         PTB_L_HALF
#define LPSPI4_SCK_PIN          10u
#define LPSPI4_SCK_PORT         PTB_L_HALF
#define LPSPI4_SOUT_PIN         9u
#define LPSPI4_SOUT_PORT        PTB_L_HALF
#define LPSPI4_PCS0_PIN         8u
#define LPSPI4_PCS0_PORT        PTB_L_HALF
#define GPIO_19_PIN             3u
#define GPIO_19_PORT            PTA_H_HALF
#define GPIO_20_PIN             4u
#define GPIO_20_PORT            PTA_H_HALF
#define GPIO_142_PIN            14u
#define GPIO_142_PORT           PTE_L_HALF
#define GPIO_30_PIN             14u
#define GPIO_30_PORT            PTA_H_HALF
#define GPIO_131_PIN            3u
#define GPIO_131_PORT           PTE_L_HALF
#define GPIO_31_PIN             15u
#define GPIO_31_PORT            PTA_H_HALF
#define ECAN_WAKE_PIN           0u
#define ECAN_WAKE_PORT          PTD_H_HALF
#define GPIO_110_PIN            14u
#define GPIO_110_PORT           PTD_L_HALF
#define GPIO_109_PIN            13u
#define GPIO_109_PORT           PTD_L_HALF
#define GPIO_50_PIN             2u
#define GPIO_50_PORT            PTB_H_HALF
#define GPIO_51_PIN             3u
#define GPIO_51_PORT            PTB_H_HALF
#define GPIO_52_PIN             4u
#define GPIO_52_PORT            PTB_H_HALF
#define GPIO_53_PIN             5u
#define GPIO_53_PORT            PTB_H_HALF
#define GPIO_136_PIN            8u
#define GPIO_136_PORT           PTE_L_HALF
#define GPIO_36_PIN             4u
#define GPIO_36_PORT            PTB_L_HALF
#define GPIO_37_PIN             5u
#define GPIO_37_PORT            PTB_L_HALF
#define GPIO_101_PIN            5u
#define GPIO_101_PORT           PTD_L_HALF
#define GPIO_54_PIN             6u
#define GPIO_54_PORT            PTB_H_HALF
#define GPIO_61_PIN             13u
#define GPIO_61_PORT            PTB_H_HALF
#define GPIO_74_PIN             10u
#define GPIO_74_PORT            PTC_L_HALF
#define GPIO_91_PIN             11u
#define GPIO_91_PORT            PTC_H_HALF
#define GPIO_92_PIN             12u
#define GPIO_92_PORT            PTC_H_HALF
#define GPIO_49_PIN             1u
#define GPIO_49_PORT            PTB_H_HALF
#define GPIO_119_PIN            7u
#define GPIO_119_PORT           PTD_H_HALF
#define GPIO_2_PIN              2u
#define GPIO_2_PORT             PTA_L_HALF
#define GPIO_123_PIN            11u
#define GPIO_123_PORT           PTD_H_HALF
#define GPIO_124_PIN            12u
#define GPIO_124_PORT           PTD_H_HALF
#define GPIO_1_PIN              1u
#define GPIO_1_PORT             PTA_L_HALF
#define GPIO_0_PIN              0u
#define GPIO_0_PORT             PTA_L_HALF
#define GPIO_150_PIN            6u
#define GPIO_150_PORT           PTE_H_HALF
#define GPIO_13_PIN             13u
#define GPIO_13_PORT            PTA_L_HALF
#define GPIO_56_PIN             8u
#define GPIO_56_PORT            PTB_H_HALF
#define GPIO_29_PIN             13u
#define GPIO_29_PORT            PTA_H_HALF
#define GPIO_67_PIN             3u
#define GPIO_67_PORT            PTC_L_HALF
#define ADC0_P0_PIN             1u
#define ADC0_P0_PORT            PTD_L_HALF
#define ADC0_P1_PIN             0u
#define ADC0_P1_PORT            PTD_L_HALF
#define ADC0_P6_PIN             11u
#define ADC0_P6_PORT            PTE_L_HALF
#define ADC0_P5_PIN             10u
#define ADC0_P5_PORT            PTE_L_HALF
#define ADC0_S20_PIN            9u
#define ADC0_S20_PORT           PTC_H_HALF
#define ADC0_S17_PIN            11u
#define ADC0_S17_PORT           PTC_L_HALF
#define ADC0_S21_PIN            10u
#define ADC0_S21_PORT           PTC_H_HALF
#define ADC0_S14_PIN            0u
#define ADC0_S14_PORT           PTB_L_HALF
#define ADC0_S13_PIN            9u
#define ADC0_S13_PORT           PTC_L_HALF
#define ADC0_S12_PIN            8u
#define ADC0_S12_PORT           PTC_L_HALF
#define ADC0_S11_PIN            7u
#define ADC0_S11_PORT           PTA_L_HALF
#define INT_CAN_TXD_PIN         11u
#define INT_CAN_TXD_PORT        PTA_H_HALF
#define ADC0_S18_PIN            6u
#define ADC0_S18_PORT           PTA_L_HALF
#define ADC0_S22_PIN            4u
#define ADC0_S22_PORT           PTD_H_HALF
#define ADC0_S9_PIN             14u
#define ADC0_S9_PORT            PTB_L_HALF
#define ADC0_S23_PIN            5u
#define ADC0_S23_PORT           PTD_H_HALF
#define ADC0_S8_PIN             13u
#define ADC0_S8_PORT            PTB_L_HALF
#define ADC0_S19_PIN            4u
#define ADC0_S19_PORT           PTD_L_HALF
#define ADC0_S10_PIN            3u
#define ADC0_S10_PORT           PTD_L_HALF
#define ADC0_S16_PIN            2u
#define ADC0_S16_PORT           PTD_L_HALF
#define ADC0_P7_PIN             9u
#define ADC0_P7_PORT            PTA_L_HALF
#define ADC0_P2_PIN             8u
#define ADC0_P2_PORT            PTA_L_HALF
#define INT_CAN_RXD_PIN         12u
#define INT_CAN_RXD_PORT        PTA_H_HALF
#define ADC1_S19_PIN            13u
#define ADC1_S19_PORT           PTE_L_HALF
#define ADC1_S15_PIN            1u
#define ADC1_S15_PORT           PTB_L_HALF
#define EMADC1_S12_PIN          0u
#define EMADC1_S12_PORT         PTB_H_HALF
#define ADC1_S11_PIN            15u
#define ADC1_S11_PORT           PTB_L_HALF
#define ADC1_S17_PIN            3u
#define ADC1_S17_PORT           PTA_L_HALF
#define ADC1_S20_PIN            8u
#define ADC1_S20_PORT           PTD_H_HALF
#define ADC1_S23_PIN            13u
#define ADC1_S23_PORT           PTD_H_HALF
#define ADC1_S16_PIN            7u
#define ADC1_S16_PORT           PTC_L_HALF
#define ADC1_S18_PIN            6u
#define ADC1_S18_PORT           PTC_L_HALF
#define ADC1_S13_PIN            0u
#define ADC1_S13_PORT           PTA_H_HALF
#define ADC1_P7_PIN             15u
#define ADC1_P7_PORT            PTA_L_HALF
#define ADC1_P4_PIN             14u
#define ADC1_P4_PORT            PTA_L_HALF
#define ADC2_P0_PIN             2u
#define ADC2_P0_PORT            PTA_H_HALF
#define ADC2_S12_PIN            5u
#define ADC2_S12_PORT           PTA_H_HALF
#define ADC2_S8_PIN             5u
#define ADC2_S8_PORT            PTE_L_HALF
#define ADC2_S23_PIN            7u
#define ADC2_S23_PORT           PTC_H_HALF
#define ADC2_S22_PIN            8u
#define ADC2_S22_PORT           PTC_H_HALF
#define ADC2_S21_PIN            15u
#define ADC2_S21_PORT           PTC_H_HALF
#define ADC2_S20_PIN            7u
#define ADC2_S20_PORT           PTE_L_HALF
#define ADC2_S19_PIN            1u
#define ADC2_S19_PORT           PTA_H_HALF
#define ADC2_S18_PIN            6u
#define ADC2_S18_PORT           PTD_H_HALF
#define ADC2_S16_PIN            10u
#define ADC2_S16_PORT           PTD_H_HALF
#define ADC2_S14_PIN            15u
#define ADC2_S14_PORT           PTD_H_HALF
#define ADC2_S10_PIN            1u
#define ADC2_S10_PORT           PTE_H_HALF
#define ADC2_S11_PIN            2u
#define ADC2_S11_PORT           PTE_H_HALF
#define ADC2_P3_PIN             5u
#define ADC2_P3_PORT            PTE_H_HALF
#define ADC2_P6_PIN             10u
#define ADC2_P6_PORT            PTE_H_HALF
#define GPI_24_PIN              8u
#define GPI_24_PORT             PTA_H_HALF
#define GPI_25_PIN              9u
#define GPI_25_PORT             PTA_H_HALF
#define EIRQ_31_PIN             15u
#define EIRQ_31_PORT            PTD_L_HALF
#define EIRQ_8_PIN              9u
#define EIRQ_8_PORT             PTE_L_HALF
#define EIRQ_10_PIN             2u
#define EIRQ_10_PORT            PTB_L_HALF
#define FFCU_ER1_PIN            0u
#define FFCU_ER1_PORT           PTE_H_HALF
#define FFCU_ER0_PIN            15u
#define FFCU_ER0_PORT           PTE_L_HALF

/*==================================================================================================
                                           ENUMS
==================================================================================================*/

/*==================================================================================================
                               STRUCTURES AND OTHER TYPEDEFS
==================================================================================================*/

/*==================================================================================================
                               GLOBAL VARIABLE DECLARATIONS
==================================================================================================*/

/*==================================================================================================
                               FUNCTION PROTOTYPES
==================================================================================================*/

#ifdef __cplusplus
}
#endif

#endif /* SIUL2_PORT_IP_CFG_H */

