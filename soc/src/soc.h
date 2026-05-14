#ifndef SOC_H
#define SOC_H

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

#include "soc_cfg.h"

#define SOC_NUM_OF_CELLS ((int32_t)SOC_NUM_OF_CELLS_I32)

typedef enum
{
    SOC_STATE_INIT = 0, /* Default value */
    SOC_STATE_RESET,
    SOC_STATE_CORRECTION_ON_WAKE,
    SOC_STATE_NORMAL
} Soc_State_t;

/* Initializes the SOC interface function.*/
void Soc_initialize (void);

/* Update the SOC module parameters Periodically.*/
void Soc_tick (void);

/* Provided Interfaces */
/* These provided interfaces are used for sohc*/
status_t Soc_get_batt_resttime (uint32_t * battresttime);
status_t Soc_get_tau_depolar (float32_t * taudepolar);
status_t Soc_get_state (Soc_State_t * socstate);
/*end*/
status_t Soc_get_pack_level (float32_t * packsoc);
status_t Soc_get_user_level (float32_t * usersoc);
status_t Soc_get_min (float32_t * minsoc);
status_t Soc_get_max (float32_t * maxsoc);
status_t Soc_get_cell_levels (float32_t * cellsoc);
status_t Soc_get_cell_cc_levels (float32_t * cellsoccc);
status_t Soc_get_cell_ocv_levels (float32_t * cellsococv);
status_t Soc_reset (bool resetsoc); /* To reset the SOC by UDS DID */

#endif /* SOC_H */
