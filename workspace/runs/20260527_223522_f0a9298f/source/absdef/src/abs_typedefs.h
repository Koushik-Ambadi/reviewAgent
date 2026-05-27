#ifndef ABS_TYPEDEFS_H
#define ABS_TYPEDEFS_H

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
/* This is needed to provide floating-point defines to determine the sizes of
 * 'float' and 'double' standard types */
#include <float.h>

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
/* Project-wide alias for 32-bit IEEE-754 single precision */
typedef float float32_t;

#if (FLT_MANT_DIG != 24)
    #error "float32_t requires 24-bit mantissa (IEEE-754 single)."
#endif

#if (FLT_MAX_EXP != 128)
    #error "float32_t requires max exponent of 128 (IEEE-754 single)."
#endif

/* Optional ABI sanity check (C99-safe) */
typedef char float32_t_must_be_4_bytes[(sizeof(float32_t) == 4U) ? 1 : -1];

/* 64-bit floating-point type (IEEE-754 double precision) */
typedef double float64_t;

#if (DBL_MANT_DIG != 53)
    #error "float64_t requires 53-bit mantissa (IEEE-754 double precision)."
#endif

#if (DBL_MAX_EXP != 1024)
    #error "float64_t requires max exponent of 1024 (IEEE-754 double precision)."
#endif

/* ABI sanity check (C99-safe) */
typedef char float64_t_must_be_8_bytes[(sizeof(float64_t) == 8U) ? 1 : -1];

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

#endif /* ==== End of file ABS_TYPEDEFS_H ================================ */
