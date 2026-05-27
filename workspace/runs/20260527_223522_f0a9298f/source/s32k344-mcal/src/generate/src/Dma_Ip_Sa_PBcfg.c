/*==================================================================================================
*   Project              : RTD AUTOSAR 4.7
*   Platform             : CORTEXM
*   Peripheral           : DMA,CACHE,TRGMUX,LCU,EMIOS,FLEXIO
*   Dependencies         : none
*
*   Autosar Version      : 4.7.0
*   Autosar Revision     : ASR_REL_4_7_REV_0000
*   Autosar Conf.Variant :
*   SW Version           : 6.0.0
*   Build Version        : S32K3_RTD_6_0_0_D2506_ASR_REL_4_7_REV_0000_20250610
*
*   Copyright 2020 - 2025 NXP
*
*
*   NXP Confidential and Proprietary. This software is owned or controlled by NXP and may only be 
*   used strictly in accordance with the applicable license terms.  By expressly 
*   accepting such terms or by downloading, installing, activating and/or otherwise 
*   using the software, you are agreeing that you have read, and that you agree to 
*   comply with and are bound by, such license terms.  If you do not agree to be 
*   bound by the applicable license terms, then you may not retain, install,
*   activate or otherwise use the software.
==================================================================================================*/

#ifdef __cplusplus
extern "C"
{
#endif


/*==================================================================================================
*                                          INCLUDE FILES
* 1) system and project includes
* 2) needed interfaces from external units
* 3) internal and external interfaces from this unit
==================================================================================================*/
#include "Dma_Ip_Cfg.h"

/*==================================================================================================
*                                 SOURCE FILE VERSION INFORMATION
==================================================================================================*/
#define DMA_IP_SA_PBCFG_VENDOR_ID_C                     43
#define DMA_IP_SA_PBCFG_AR_RELEASE_MAJOR_VERSION_C      4
#define DMA_IP_SA_PBCFG_AR_RELEASE_MINOR_VERSION_C      7
#define DMA_IP_SA_PBCFG_AR_RELEASE_REVISION_VERSION_C   0
#define DMA_IP_SA_PBCFG_SW_MAJOR_VERSION_C              6
#define DMA_IP_SA_PBCFG_SW_MINOR_VERSION_C              0
#define DMA_IP_SA_PBCFG_SW_PATCH_VERSION_C              0

/*==================================================================================================
*                                     FILE VERSION CHECKS
==================================================================================================*/
/* Check if Dma_Ip_Sa_PBcfg.c file and Dma_Ip_Cfg.h file are of the same vendor */
#if (DMA_IP_SA_PBCFG_VENDOR_ID_C != DMA_IP_CFG_VENDOR_ID)
    #error "Dma_Ip_Sa_PBcfg.c and Dma_Ip_Cfg.h have different vendor ids"
#endif

/* Check if Dma_Ip_Sa_PBcfg.c file and Dma_Ip_Cfg.h file are of the same Autosar version */
#if ((DMA_IP_SA_PBCFG_AR_RELEASE_MAJOR_VERSION_C != DMA_IP_CFG_AR_RELEASE_MAJOR_VERSION) || \
     (DMA_IP_SA_PBCFG_AR_RELEASE_MINOR_VERSION_C != DMA_IP_CFG_AR_RELEASE_MINOR_VERSION) || \
     (DMA_IP_SA_PBCFG_AR_RELEASE_REVISION_VERSION_C != DMA_IP_CFG_AR_RELEASE_REVISION_VERSION) \
    )
    #error "AutoSar Version Numbers of Dma_Ip_Sa_PBcfg.c and Dma_Ip_Cfg.h are different"
#endif

/* Check if Dma_Ip_Sa_PBcfg.c file and Dma_Ip_Cfg.h file are of the same Software version */
#if ((DMA_IP_SA_PBCFG_SW_MAJOR_VERSION_C != DMA_IP_CFG_SW_MAJOR_VERSION) || \
     (DMA_IP_SA_PBCFG_SW_MINOR_VERSION_C != DMA_IP_CFG_SW_MINOR_VERSION) || \
     (DMA_IP_SA_PBCFG_SW_PATCH_VERSION_C != DMA_IP_CFG_SW_PATCH_VERSION) \
    )
    #error "Software Version Numbers of Dma_Ip_Sa_PBcfg.c and Dma_Ip_Cfg.h are different"
#endif


/*==================================================================================================
*                                        LOCAL MACROS
==================================================================================================*/

/*==================================================================================================
                          LOCAL TYPEDEFS (STRUCTURES, UNIONS, ENUMS)
==================================================================================================*/

/*==================================================================================================
                                       LOCAL CONSTANTS
==================================================================================================*/

/*==================================================================================================
                                       LOCAL VARIABLES
==================================================================================================*/

/*==================================================================================================
                                       GLOBAL CONSTANTS
==================================================================================================*/

/*==================================================================================================
                                       GLOBAL VARIABLES
==================================================================================================*/

/*==================================================================================================
                                   LOCAL FUNCTION PROTOTYPES
==================================================================================================*/

/*==================================================================================================
                                       LOCAL FUNCTIONS
==================================================================================================*/

/*==================================================================================================
                                       GLOBAL FUNCTIONS
==================================================================================================*/

#define MCL_START_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

/* DMA Logic Instance Configuration */
static const Dma_Ip_LogicInstanceConfigType LogicInstance0ConfigPB =
{
	{
		/* uint32 logicInstId; */ SA_DMA_LOGIC_INST_0,
		/* uint8 hwVersId;     */ DMA_IP_HARDWARE_VERSION_3,
		/* uint8 hwInst;       */ DMA_IP_HW_INST_0,
	},
	/* boolean EnDebug; */                 (boolean)FALSE,
	/* boolean EnRoundRobin; */            (boolean)FALSE,
	/* boolean EnHaltAfterError; */        (boolean)FALSE,
	/* boolean EnChLinking; */             (boolean)FALSE,
	/* boolean EnGlMasterIdReplication; */ (boolean)FALSE,
};

/* DMA Logic Instance Configuration Array */
static const Dma_Ip_LogicInstanceConfigType * const Dma_Ip_paxLogicInstanceConfigArrayPB[1] =
{
		&LogicInstance0ConfigPB,
};


#define MCL_STOP_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"


#define MCL_START_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"


/* DMA Logic Channel Configurations */
static const Dma_Ip_GlobalConfigType LogicChannel0GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO0,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_GlobalConfigType LogicChannel1GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO1,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_GlobalConfigType LogicChannel2GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO0,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_GlobalConfigType LogicChannel3GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO0,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_GlobalConfigType LogicChannel4GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO0,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_GlobalConfigType LogicChannel5GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO0,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_GlobalConfigType LogicChannel6GlobalConfigPB =
{
	{
		/* boolean EnMasterIdReplication; */ (boolean)FALSE,
		/* boolean EnBufferedWrites; */      (boolean)FALSE,
	}, /* Control */
	{
		/* boolean EnRequest; */             (boolean)FALSE,
	}, /* Request */
	{
		/* boolean EnErrorInt; */            (boolean)TRUE,
	}, /* Interrupt */
	{
		/* uint8 SwapSize; */                (uint8)0U,
	}, /* Swap */
	{
		/* uint8 Group; */                   DMA_IP_GROUP_PRIO0,
		/* uint8 Level; */                   DMA_IP_LEVEL_PRIO1,
		/* boolean EnPreemption; */          (boolean)FALSE,
		/* boolean DisPreempt; */            (boolean)FALSE,
	}, /* Priority */
};
static const Dma_Ip_TransferConfigType LogicChannel0TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};
static const Dma_Ip_TransferConfigType LogicChannel1TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};
static const Dma_Ip_TransferConfigType LogicChannel2TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};
static const Dma_Ip_TransferConfigType LogicChannel3TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};
static const Dma_Ip_TransferConfigType LogicChannel4TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};
static const Dma_Ip_TransferConfigType LogicChannel5TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};
static const Dma_Ip_TransferConfigType LogicChannel6TransferConfigPB =
{
	{
		/* uint32 ScatterGatherAddr; */    0U,
		/* uint32 DestinationStoreAddr; */ 0U,
		/* uint8 BandwidthControl; */      DMA_IP_BWC_ENGINE_NO_STALL,
		/* uint8 TransferModeControl; */   0U,
		/* boolean EnStart; */             (boolean)FALSE,
		/* boolean EnMajorInt; */          (boolean)TRUE,
		/* boolean EnHalfMajorInt; */      (boolean)FALSE,
		/* boolean DisAutoHwRequest; */    (boolean)FALSE,
		/* boolean EnEndOfPacketSignal; */ (boolean)FALSE,
	}, /* Control */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Source */
	{
		/* uint32 addr; */         0U,
		/* sint32 lastAddrAdj; */  0,
		/* sint16 signedOffset; */ 0,
		/* uint8 transferSize; */  DMA_IP_TRANSFER_SIZE_1_BYTE,
		/* uint8 modulo; */        0U,
	}, /* Destination */
	{
		/* uint32 size; */         0U,
		/* sint32 offset; */       0,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
		/* boolean EnSrcOffset; */ (boolean)FALSE,
		/* boolean EnDstOffset; */ (boolean)FALSE,
	}, /* MinorLoop */
	{
		/* uint16 count; */        0U,
		/* uint8 LogicLinkCh; */   0U,
		/* boolean EnLink; */      (boolean)FALSE,
	}, /* MajorLoop */
};

#define MCL_STOP_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"


#define MCL_START_SEC_VAR_CLEARED_UNSPECIFIED_NO_CACHEABLE
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"


#define MCL_STOP_SEC_VAR_CLEARED_UNSPECIFIED_NO_CACHEABLE
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

#define MCL_START_SEC_VAR_INIT_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

#define MCL_STOP_SEC_VAR_INIT_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

#define MCL_START_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

static const Dma_Ip_LogicChannelConfigType LogicChannel0ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_0 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_0,
				/* Dma_Ip_Callback IntCallback; */    Lpspi_Ip_LPSPI_2_IrqTxDmaHandler,
				/* Dma_Ip_Callback ErrIntCallback; */ Dma0_Ch0_IRQHandler_Error,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel0GlobalConfigPB,
		&LogicChannel0TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType LogicChannel1ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_1 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_1,
				/* Dma_Ip_Callback IntCallback; */    Lpspi_Ip_LPSPI_2_IrqRxDmaHandler,
				/* Dma_Ip_Callback ErrIntCallback; */ Dma0_Ch1_IRQHandler_Error,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel1GlobalConfigPB,
		&LogicChannel1TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType LogicChannel2ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_2 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_2,
				/* Dma_Ip_Callback IntCallback; */    DMA_Can_Callback0,
				/* Dma_Ip_Callback ErrIntCallback; */ DMA_Can_Callback0,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel2GlobalConfigPB,
		&LogicChannel2TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType LogicChannel3ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_3 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_3,
				/* Dma_Ip_Callback IntCallback; */    DMA_Can_Callback3,
				/* Dma_Ip_Callback ErrIntCallback; */ DMA_Can_Callback3,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel3GlobalConfigPB,
		&LogicChannel3TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType LogicChannel4ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_4 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_16,
				/* Dma_Ip_Callback IntCallback; */    DMA_Can_Callback5,
				/* Dma_Ip_Callback ErrIntCallback; */ DMA_Can_Callback5,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel4GlobalConfigPB,
		&LogicChannel4TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType LogicChannel5ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_5 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_17,
				/* Dma_Ip_Callback IntCallback; */    Lpspi_Ip_LPSPI_4_IrqTxDmaHandler,
				/* Dma_Ip_Callback ErrIntCallback; */ Dma0_Ch17_IRQHandler_Error,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel5GlobalConfigPB,
		&LogicChannel5TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType LogicChannel6ConfigPB = 
{
		{
				/* uint32 LogicChId; */               SA_DMA_LOGIC_CH_6 ,
				/* uint8 HwVersId; */                 DMA_IP_HARDWARE_VERSION_3,
				/* uint8 HwInst; */                   DMA_IP_HW_INST_0,
				/* uint8 HwChId; */                   DMA_IP_HW_CH_18,
				/* Dma_Ip_Callback IntCallback; */    Lpspi_Ip_LPSPI_4_IrqRxDmaHandler,
				/* Dma_Ip_Callback ErrIntCallback; */ Dma0_Ch18_IRQHandler_Error,
		}, /* Dma_Ip_LogicChannelIdType */
		&LogicChannel6GlobalConfigPB,
		&LogicChannel6TransferConfigPB,
		NULL_PTR,
};

static const Dma_Ip_LogicChannelConfigType * const Dma_Ip_paxLogicChannelConfigArrayPB[7] =
{
		&LogicChannel0ConfigPB,
		&LogicChannel1ConfigPB,
		&LogicChannel2ConfigPB,
		&LogicChannel3ConfigPB,
		&LogicChannel4ConfigPB,
		&LogicChannel5ConfigPB,
		&LogicChannel6ConfigPB,
};

#define MCL_STOP_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

#define MCL_START_SEC_VAR_CLEARED_UNSPECIFIED_NO_CACHEABLE
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

/* DMA Hardware Channel 0 */
static Dma_Ip_HwChannelStateType HwChannel0StatePB;

/* DMA Hardware Channel 1 */
static Dma_Ip_HwChannelStateType HwChannel1StatePB;

/* DMA Hardware Channel 2 */
static Dma_Ip_HwChannelStateType HwChannel2StatePB;

/* DMA Hardware Channel 3 */
static Dma_Ip_HwChannelStateType HwChannel3StatePB;

/* DMA Hardware Channel 4 */
static Dma_Ip_HwChannelStateType HwChannel4StatePB;

/* DMA Hardware Channel 5 */
static Dma_Ip_HwChannelStateType HwChannel5StatePB;

/* DMA Hardware Channel 6 */
static Dma_Ip_HwChannelStateType HwChannel6StatePB;

#define MCL_STOP_SEC_VAR_CLEARED_UNSPECIFIED_NO_CACHEABLE
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

#define MCL_START_SEC_VAR_INIT_UNSPECIFIED_NO_CACHEABLE
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

/* DMA Hardware Channel State and DMA Logic Channel Configuration Array */
static Dma_Ip_HwChannelStateType * Dma_Ip_paxHwChannelStateArrayPB[7] =
{
		&HwChannel0StatePB,
		&HwChannel1StatePB,
		&HwChannel2StatePB,
		&HwChannel3StatePB,
		&HwChannel4StatePB,
		&HwChannel5StatePB,
		&HwChannel6StatePB,
};

#define MCL_STOP_SEC_VAR_INIT_UNSPECIFIED_NO_CACHEABLE
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

#define MCL_START_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"

/* DMA Initialization Structure */
const Dma_Ip_InitType Dma_Ip_Sa_xDmaInitPB = 
{
		/* Dma_Ip_HwChannelStateType ** HwChStateArray */                            &Dma_Ip_paxHwChannelStateArrayPB[0U],         /* Static */
		/* const Dma_Ip_LogicChannelConfigType * const LogicChConfigArray   */       &Dma_Ip_xLogicChannelResetConfig,           /* Static */
		/* const Dma_Ip_LogicChannelConfigType * const * LogicChConfigArray */       &Dma_Ip_paxLogicChannelConfigArrayPB[0U],     /* Static */
		/* const Dma_Ip_LogicInstanceConfigType * const LogicInstConfigArray   */    &Dma_Ip_xLogicInstanceResetConfig,          /* Static */
		/* const Dma_Ip_LogicInstanceConfigType * const  * LogicInstConfigArray */   &Dma_Ip_paxLogicInstanceConfigArrayPB[0U],    /* Static */
		/* const uint8 NumOfLogicChannel   */                                        7U,
		/* const uint8 NumOfLogicInstance */                                         1U,
};
#define MCL_STOP_SEC_CONFIG_DATA_UNSPECIFIED
/* @violates @ref Mcl_Dma_h_REF_1 MISRA 2012 Required Directive 4.10, Precautions shall be taken in order to prevent the contents of a header file being included more than once. */
#include "Mcl_MemMap.h"
#ifdef __cplusplus
}
#endif

/** @} */


