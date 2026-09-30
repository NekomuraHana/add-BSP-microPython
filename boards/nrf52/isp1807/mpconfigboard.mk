MCU_SERIES = m4
MCU_VARIANT = nrf52
MCU_SUB_VARIANT = nrf52840
SOFTDEV_VERSION = 6.1.1

# nRF52840 memory geometry.
LD_FILES += boards/nrf52840_1M_256k.ld

# The Switch Science board ships with an Adafruit-compatible bootloader whose
# application area ends at 0xED000. Reserve the tail so MicroPython's ROMFS/LFS
# regions can never overlap the bootloader/settings area.
LD_FILES += $(BOARD_DIR)/isp1807_breakout_bootloader.ld

NRF_DEFINES += -DNRF52840_XXAA

MICROPY_VFS_LFS2 = 1

# The upstream nRF _boot.py mounts internal flash at /flash. Use a board-local
# boot script that mounts it at / so generic MicroPython host tools can upload
# files using absolute paths such as /main.py.
FROZEN_MANIFEST ?= $(BOARD_DIR)/manifest.py
