#ifndef ABS_SYSDEFS_H
#define ABS_SYSDEFS_H

/* ===========================================================================
 *
 *                CONFIDENTIAL AMERICAN BATTERY SOLUTIONS
 *
 *   This is an unpublished work of authorship, which contains
 *   trade secrets, created in 2022.  American Battery Solutions owns
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
    /* Function execution successfull */
    ABS_OK = 0,
    /* Function Execution Failed */
    ABS_N_OK,
    /* The Input parameter are Invalid */
    ABS_PARAM_ERR,
    /* Dependency component returned an failure */
    ABS_INTERFACE_FAIL
} status_t;

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

#endif /* ==== End of file ABS_SYSDEFS_H_ ================================ */
