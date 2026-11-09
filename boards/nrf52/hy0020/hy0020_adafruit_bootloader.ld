/*
 * Flash layout for AE-HY0020-DIP with the Adafruit nRF52 bootloader.
 *
 * S132 v6.1.1 application start: 0x26000
 * MicroPython application end: 0x65000 (below Adafruit's 0x6D000 limit)
 * Writable MicroPython filesystem: 0x65000-0x74000 (60 KiB)
 * Adafruit bootloader start: 0x74000
 * Flash end: 0x80000
 *
 * The 0x74000 bootloader start and 0x7E000/0x7F000 parameter/settings pages
 * match Adafruit's nRF52832 bootloader linker script.
 */

_bootloader_tail_size = 0xC000;

/* Shrink the application reservation to 0x26000-0x65000 to reserve 60 KiB
 * for MicroPython LFS2. This extends writable storage into the Adafruit
 * standard application range: DFU file preservation MUST be hardware-tested.
 */
_micropy_hw_romfs_part0_size = 0;
_fs_size = 0xF000;
