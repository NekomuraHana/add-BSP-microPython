"""Static HY0020 BSP metadata, frozen into the firmware.

BSP_VERSION identifies the board-support configuration and is independent of
the MicroPython interpreter version. It is a maintained software version,
not a detected physical PCB or module revision.
"""

BOARD_ID = "HY0020"
BOARD_NAME = "Akizuki AE-HY0020-DIP"
MCU = "nRF52832"
BSP_VERSION = (0, 1, 0)
HARDWARE_REVISION = None  # Not detectable from the HY0020 module in software.\n\n# Identifies the actual firmware build, not a guess from FS size or UICR.\nfrom _hy0020_variant import FIRMWARE_VARIANT, HAS_BOOTLOADER, REPL_SELECT_PIN

# Common MicroPython REPL wiring for both firmware variants.
REPL_UART = 0
REPL_TX_PIN = "P0_18"
REPL_RX_PIN = "P0_16"


def info():
    """Return a snapshot of BSP metadata and the running MicroPython version."""
    import sys

    return {
        "board_id": BOARD_ID,
        "board_name": BOARD_NAME,
        "mcu": MCU,
        "bsp_version": BSP_VERSION,
        "hardware_revision": HARDWARE_REVISION,\n        "firmware_variant": FIRMWARE_VARIANT,\n        "has_bootloader": HAS_BOOTLOADER,\n        "repl_select_pin": REPL_SELECT_PIN,
        "micropython_version": sys.implementation.version,
        "repl_uart": REPL_UART,
        "repl_tx": REPL_TX_PIN,
        "repl_rx": REPL_RX_PIN,
    }
