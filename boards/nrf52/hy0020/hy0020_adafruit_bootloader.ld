/*
 * Flash layout for AE-HY0020-DIP with the Adafruit nRF52 bootloader.
 *
 * S132 v6.1.1 application start: 0x26000
 * Arduino/Adafruit application end: 0x6D000
 * Writable MicroPython filesystem: 0x6D000-0x74000 (28 KiB)
 * Adafruit bootloader start: 0x74000
 * Flash end: 0x80000
 *
 * The 0x74000 bootloader start and 0x7E000/0x7F000 parameter/settings pages
 * match Adafruit's nRF52832 bootloader linker script.
 */

_bootloader_tail_size = 0xC000;

/* Keep the application within the same 0x26000-0x6D000 region used by the
 * Adafruit nRF52832 BSP, and use the remaining 28 KiB before the bootloader as
 * writable MicroPython storage.
 */
_micropy_hw_romfs_part0_size = 0;
_fs_size = 0x7000;
