/*
 * Flash tail reservation for the Switch Science ISP1807 Breakout bootloader.
 *
 * S140 v6 application start: 0x26000
 * Bootloader/application boundary: 0xED000
 * Flash end: 0x100000
 *
 * Reserve 0x13000 bytes at the top of flash for the bootloader, MBR parameter
 * page and bootloader settings.
 */

_bootloader_tail_size = 0x13000;
