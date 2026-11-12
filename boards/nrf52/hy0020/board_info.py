"""HY0020 BSP-specific metadata frozen into both firmware variants.

The standard MicroPython runtime already provides board/MCU/interpreter data
via os.uname() and sys.implementation; do not duplicate it here.
"""

BSP_VERSION = (0, 1, 0)

# Variant is selected by the firmware build's frozen manifest.
from _hy0020_variant import FIRMWARE_VARIANT, REPL_SELECT_PIN

# REPL UART pins are identical in both firmware variants.
REPL_TX_PIN = "P0_18"
REPL_RX_PIN = "P0_16"
