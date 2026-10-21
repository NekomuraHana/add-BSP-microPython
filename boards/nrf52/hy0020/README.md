# AE-HY0020-DIP MicroPython BSP (initial bring-up)

This directory contains the first bring-up BSP for the Akizuki **AE-HY0020-DIP**
(product 131342), using the FDK HY0020 / nRF52832.

The goal of this revision is deliberately small: produce a firmware image that
can be installed through the Adafruit nRF52 bootloader, provide a UART REPL when
requested at reset, and otherwise release the only hardware UART for normal
MicroPython applications.

## Assumptions

- MCU: nRF52832, 512 KiB Flash / 64 KiB RAM.
- SoftDevice: S132 6.1.1.
- Bootloader: Adafruit nRF52 bootloader already installed on the Akizuki kit.
- Bootloader UART wiring: TX=P0.06, RX=P0.08.
- P0.20 remains the Adafruit/Akizuki active-low DFU input.
- P0.12 is used only by this initial MicroPython BSP as the REPL-mode selector.

## REPL mode selection

Immediately after reset, the native nRF startup code enables the P0.12
pull-up and **latches the pin level once**, before initializing the Python VM.
Both modes execute frozen `_boot.py` and filesystem `boot.py` **before** the mode-specific UART handoff. `boot.py` can configure and use UART0 with any supported pins and baud rate. After `boot.py` returns, the firmware waits up to **50 ms** for any UART0 TX in progress to complete, then uninitializes UART0 regardless of how `boot.py` configured it. If TX is still active at the deadline, the UART is nevertheless uninitialized (the remaining bytes may be lost).

- **P0.12 LOW**: after that handoff, initialize UART0 as the 115200-bps REPL on TX=P0.06 / RX=P0.08 and **skip `main.py`**.
- **P0.12 HIGH** (internal pull-up/default): leave UART0 uninitialized for the application, execute `main.py`, and **do not connect the user's UART to REPL**.

If `boot.py` hangs or never returns, the UART handoff and REPL cannot occur; this mode is not a guaranteed recovery path for a broken `boot.py`.

For maintenance/debugging, hold the P0.12 switch LOW, assert reset, release
reset, then release the P0.12 switch.  The REPL remains active for that boot.

Changing P0.12 after reset no longer changes the selected mode; another hardware
reset is required. This avoids a race against MicroPython's Python-level startup.

In normal mode, `machine.UART(0)` is free for application use after the boot-script handoff, even when `boot.py` previously used a different UART0 pin/baud mapping.  The repository's
existing nRF UART pin-selection patch allows alternate pins, for example:

```python
from machine import Pin, UART

uart = UART(
    0,
    115200,
    tx=Pin("P0_18"),
    rx=Pin("P0_16"),
)
```

## Flash layout

The initial layout intentionally follows the Adafruit nRF52832 application
boundary while retaining a small writable MicroPython filesystem:

| Region | Range |
| --- | --- |
| S132 6.1.1 | 0x00000 - 0x25FFF |
| MicroPython application | 0x26000 - 0x6CFFF |
| MicroPython LFS | 0x6D000 - 0x73FFF (28 KiB) |
| Adafruit bootloader / params / settings | 0x74000 - 0x7FFFF |

No VfsROM partition is reserved in this first build.

## Serial DFU artifact

CI builds `firmware-dfu.zip` with SoftDevice requirement `0x00B7` (S132
6.1.1).  With a USB-UART bridge connected to P0.06/P0.08, enter DFU using the
board's normal Adafruit/Akizuki procedure and upload with `adafruit-nrfutil`.

Example:

```sh
adafruit-nrfutil dfu serial -pkg firmware-dfu.zip -p COMx -b 115200 --singlebank
```

## Pin notes

The initial exposed-pin aliases are:

`P0_02 P0_03 P0_04 P0_05 P0_06 P0_07 P0_08 P0_09 P0_10 P0_12 P0_16 P0_18 P0_20 P0_28 P0_30`

P0.09/P0.10 are also NFC pins on nRF52832 and need separate verification before
treating them as unrestricted GPIO.  P0.20 is owned by the Adafruit bootloader
as the DFU selector while the bootloader is retained.

## Initial-scope limits

This revision does **not** yet:

- move REPL TX/RX to P0.18/P0.16,
- provide a bootloader-free SWD image,
- verify every UART/I2C/SPI/PWM/ADC pin combination on hardware,
- change P0.20 away from its bootloader DFU role.

Those are follow-up items after the first firmware is proven on the real board.
