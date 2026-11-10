MCU_SERIES = m4
MCU_VARIANT = nrf52
MCU_SUB_VARIANT = nrf52832
SOFTDEV_VERSION = 6.1.1

# HY0020 uses the 512 KiB / 64 KiB nRF52832.
LD_FILES += boards/nrf52832_512k_64k.ld

# Match the Adafruit nRF52 bootloader memory map used by the Akizuki kit.
HY0020_NO_BOOTLOADER ?= 0
ifeq ($(HY0020_NO_BOOTLOADER),1)
LD_FILES += $(BOARD_DIR)/hy0020_standalone.ld
else
LD_FILES += $(BOARD_DIR)/hy0020_adafruit_bootloader.ld
endif

NRF_DEFINES += -DNRF52832_XXAA

MICROPY_VFS_LFS2 = 1

# Mount internal flash at / and perform the P0.12 REPL-mode selection before
# boot.py/main.py run.
FROZEN_MANIFEST ?= $(BOARD_DIR)/manifest.py
