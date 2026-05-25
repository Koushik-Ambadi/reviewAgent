MEMORY {
    sram_rsvd1  : ORIGIN = 0x20400000, LENGTH=0
    sram_memory : ORIGIN = .,          LENGTH=320k
    sram_rsvd2  : ORIGIN = .,          LENGTH=0

    dtcm0_rsvd1  : ORIGIN = 0x20000000, LENGTH=0
    dtcm0_memory : ORIGIN = .,          LENGTH=128k
    dtcm0_rsvd2  : ORIGIN = .,          LENGTH=0

    itcm0_rsvd1  : ORIGIN = 0x00000000, LENGTH=0
    itcm0_memory : ORIGIN = .,          LENGTH=64k
    itcm0_rsvd2  : ORIGIN = .,          LENGTH=0

    flash_rsvd1  : ORIGIN = 0x00400000, LENGTH=0
    flash_memory : ORIGIN = .,          LENGTH=4M
    flash_rsvd2  : ORIGIN = .,          LENGTH=0
}
DEFAULTS {
    /* VCAST_NO_MALLOC already creates a static harness heap buffer.
       Keep linker heap padding at 0 to avoid reserving heap twice. */
    heap_reserve = 0K
    stack_reserve = 16K
}
//
// Program layout for running out of RAM.
//
//

SECTIONS
{

//
// The text segment
//

    .picbase                                            : >> dtcm0_memory, sram_memory
    .text                                               : >> .
    .syscall                                            : > .
    .intercall                                          : > .
    .interfunc                                          : > .
    .fixaddr                                            : > .
    .fixtype                                            : > .
    .rodata                                             : >> .
    .secinfo                                            : > .

//
// The data segment
//

    .pidbase                                  ALIGN(32) : > .
    .sdabase                                            : > .
    .sbss                                               : > .
    .sdata                                              : >> .
    .data                                               : >> .
    .bss                                                : > .
    .ghcovfz					  CLEAR : > .
    .ghcovcz					  CLEAR : > .
    .ghcovdz					  CLEAR : > .
    .heap                   ALIGN(32) PAD(heap_reserve) : > .
    .stack                 ALIGN(32) PAD(stack_reserve) : > .
//
// These special symbols mark the bounds of RAM and ROM memory.
// They are used by the MULTI debugger.
//
    __ghs_romstart  = MEMADDR(flash_rsvd1);
    __ghs_romend    = MEMENDADDR(flash_rsvd2);
    __ghs_ramstart  = MEMADDR(dtcm0_rsvd1);
    __ghs_ramend    = MEMENDADDR(sram_rsvd2);
        
}
