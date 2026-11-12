/*
 * HY0020 standalone SWD layout (S132 6.1.1, no Adafruit bootloader).
 *
 * S132:              0x00000-0x25FFF
 * MicroPython:       0x26000-0x67FFF
 * LFS2 (96 KiB):     0x68000-0x7FFFF
 *
 * This image is NOT compatible with Adafruit serial DFU. Flashing it
 * requires SWD and a full S132 + application image on a blank device.
 * Moving the filesystem invalidates the previous 0x64000-based layout.
 */
_bootloader_tail_size = 0;
_micropy_hw_romfs_part0_size = 0;
_fs_size = 0x18000;
