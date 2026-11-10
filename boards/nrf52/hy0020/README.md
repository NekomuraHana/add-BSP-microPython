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

## SPI/I2C soft reset cleanup

On a MicroPython Ctrl+D soft reboot, `spi_init0()` and `i2c_init0()`
release previously initialized nrfx driver instances (including their PRS
resource claims). This prevents a missing Python `deinit()` call from
leaving `OSError: 16` across soft resets. It does not auto-release hardware
when a Python script ends without a soft reset.

On HY0020, verify using SPI0 **and** I2C0 (not the non-conflicting SPI1
sensor example below). See `tests/README.md` for the Ctrl+D test sequence.

## SPI sensor smoke test

The reusable test `tests/nrf_spi_lsm6ds3.py` checks an **LSM6DS3**
accelerometer/gyroscope on SPI1 using a WHO_AM_I read (`0x69`), sensor
configuration writes, and a 12-byte burst read of gyro/acceleration samples.
It defaults to the following HY0020 wiring:

| LSM6DS3 | HY0020 |
| --- | --- |
| SA0 / SDO (MISO) | P0.02 |
| CS (active low) | P0.03 |
| SDA / SDI (MOSI) | P0.04 |
| SCL / SPC (SCK) | P0.05 |

Also connect 3.3 V and GND. Change the pin constants at the top of the
shared test for a different board. The test configures SPI mode 3 at 1 MHz,
reports the measured acceleration/gyro values, and deinitializes SPI at exit.
The HY0020 sensor test passed on hardware using SPI1; SPI0/I2C0
resource-sharing problems are tracked separately in Issue #19.

The shared nRF SPI/I2C patch under review in Issue #19 adds
`OSError(EBUSY)` for competing SPI0/TWI0 initialization, an explicit
`I2C.deinit()`, and a bounded SPI transfer wait. To validate the fix, wire
SPI0 MOSI to MISO, configure I2C0 pull-ups, and run
`tests/common/nrf_spi_i2c_shared.py`. The **new** alternating-bus test is
pending HY0020 hardware verification; the previous SPI1 sensor result does
not establish SPI0/TWI0 correctness.

**Remaining UART handoff hardware check:** put a UART0 transmission in
`boot.py`, verify that it completes, and verify REPL mode can reconnect
using TX=P0.06/RX=P0.08 while normal mode's `main.py` can reconfigure
UART0 with different pins and baud. A successful build does not replace this
real-device check.

## VS Code / MicroPico

When using the **MicroPico** VS Code extension with HY0020's UART REPL,
`Run Current File on Board` may fail when MicroPico performs a soft reset
before execution. The extension may log
`[RunCommand] Failed to execute script on Pico.` and reconnect the serial
port. This was reproduced even with an empty `boot.py`.

As a workaround, set the following in VS Code **settings.json** (workspace or user settings):

```json
{
    "micropico.noSoftResetOnRun": true
}
```

With this setting, the repeated run failures stopped in the HY0020 hardware
test. This is a **workaround**, not a confirmed MicroPico root-cause fix.
Manual UART terminal tests successfully reached friendly REPL after soft
reset and executed code using raw REPL, so the observed failure is not
evidence of a general MicroPython REPL failure. Note that disabling the
automatic reset means Python state may persist between runs; use a deliberate
reset when a clean VM is required.

## Flash layout

The current layout reserves 64 KiB for writable MicroPython LFS2 by reducing
application space below the standard Adafruit nRF52832 application boundary.
This requires DFU compatibility testing before deployment to devices with
valuable user files:

| Region | Range |
| --- | --- |
| S132 6.1.1 | 0x00000 - 0x25FFF |
| MicroPython application | 0x26000 - 0x63FFF (248 KiB) |
| MicroPython LFS | 0x64000 - 0x73FFF (64 KiB) |
| Adafruit bootloader / params / settings | 0x74000 - 0x7FFFF |

No VfsROM partition is reserved. The former filesystem started at 0x6D000;
the new one starts at 0x64000. Updating from the interim 60 KiB
layout also changes the filesystem start (0x65000 to 0x64000); back up scripts
before that update as well. **Back up files on the old firmware before
updating.** An existing filesystem may need reformatting after this layout
change; do not assume user data survives the change. Furthermore, the new FS
lies partly inside the Adafruit bootloader's normal application region
(0x64000-0x6CFFF). **Preservation of this area across serial DFU has not been
verified**; the new layout should not be treated as production-safe until
DFU updates with existing files have been tested on hardware.

After flashing a test device, check `os.statvfs("/")` for 16 blocks of 4096
bytes (64 KiB total), verify file read/write and reboot persistence, then
perform a serial DFU update while recording whether user files survive.

## Standalone SWD build (experimental)

The optional `HY0020_NO_BOOTLOADER=1` build removes the 0x74000-0x7FFFF
Adafruit bootloader reservation. This first-stage change **does not move any
pins**: UART REPL remains TX=P0.06/RX=P0.08, the reset-time REPL selector
remains P0.12, and P0.20 is not repurposed yet.

| Region | Standalone SWD range |
| --- | --- |
| S132 6.1.1 | 0x00000 - 0x25FFF |
| MicroPython application | 0x26000 - 0x67FFF (264 KiB reserved) |
| LFS2 | 0x68000 - 0x7FFFF (96 KiB) |
| Adafruit bootloader | Not installed |

The existing serial DFU build still uses the original 64 KiB LFS2 layout
at 0x64000-0x73FFF. The standalone layout moves the filesystem start;
**back up any files before changing images**. The first flash may need to
format LFS2. The merged `hy0020-s132-micropython-swd.hex` contains the
SoftDevice and application, but deliberately does not write the FS region.
It does not preserve an old filesystem layout. A full-chip erase, when
performed by the SWD programmer, also destroys all user files and any
previous bootloader.

CI builds both variants and publishes `fdk-hy0020-micropython-swd` alongside
the existing DFU artifacts. Manual build after staging the BSP and applying
the repository's MicroPython patches:

```sh
make -C micropython/ports/nrf BOARD=HY0020 SD=s132 \
  HY0020_NO_BOOTLOADER=1 BUILD=build-HY0020-s132-standalone
```

Use an SWD probe (such as J-Link) to program the merged HEX. Serial
Adafruit DFU cannot install the standalone firmware. After programming,\n**power-cycle** the module and verify with J-Link Commander\n`mem32 0x1000120C 1` (expected `FFFFFFFE`). Flash erases/recover\noperations can erase the UICR setting. Switching back to NFC mode requires\nerasing UICR first, which may require backing up and reflashing firmware and\nfilesystem. Do not connect an NFC antenna while using the GPIO configuration;\nNFC overvoltage protection is disabled.

Hardware checks before merge: cold boot, P0.12 LOW/HIGH REPL/application
modes, Issue #18 reset-time selector behavior, UART0 handoff,\nP0.09/P0.10 GPIO I2C scan after cold boot,
`os.statvfs("/")` (24 x 4096-byte blocks), file write/read and reset
persistence, BLE/S132 initialization, and bootloader-free SWD reflashing.
CI validation is not a substitute for these physical board tests.

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
