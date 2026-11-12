# AE-HY0020-DIP MicroPython BSP (initial bring-up)

This directory contains the first bring-up BSP for the Akizuki **AE-HY0020-DIP**
(product 131342), using the FDK HY0020 / nRF52832.

The goal of this revision is deliberately small: produce a firmware image that
can be installed through the Adafruit nRF52 bootloader, provide a UART REPL when
requested at reset, and otherwise release the only hardware UART for normal
MicroPython applications.

## Board identity and firmware version

The interpreter already exposes the board and MicroPython version:

```python
import os, sys
print(os.uname().machine)
print(sys.implementation.version)
```

This BSP also freezes `board_info` into both firmware variants, so software
can identify the **firmware packaging** independently of flash layout:

```python
import board_info
print(board_info.info())
print(board_info.BSP_VERSION)
print(board_info.FIRMWARE_VARIANT)
print(board_info.HAS_BOOTLOADER)
```

| Field | Adafruit DFU build | Standalone SWD build |
| --- | --- | --- |
| `BOARD_ID` | `HY0020` | `HY0020` |
| `BSP_VERSION` | `(0, 1, 0)` | `(0, 1, 0)` |
| `FIRMWARE_VARIANT` | `adafruit-dfu` | `standalone-swd` |
| `HAS_BOOTLOADER` | `True` | `False` |
| `REPL_SELECT_PIN` | `P0_12` | `P0_20` |

`BSP_VERSION` is a manually maintained software-version tuple and **not**
the MicroPython interpreter version or physical PCB revision. The module
returns `HARDWARE_REVISION = None` because the physical board revision
cannot be reliably determined from software. These values identify the
build configuration and are compiled into frozen modules, not guessed by
inspecting runtime filesystem size or UICR.

## UART pin assignments and boot modes

Both firmware variants use the pads outside the DIP20 footprint for the
**MicroPython UART REPL**: TX=P0.18, RX=P0.16 (115200 bps).
These are the MCU's TX/RX directions; cross them when connecting a USB-UART
adapter. Bootloader-enabled DFU **still uses TX=P0.06, RX=P0.08** independently.

| Function | Adafruit UART DFU firmware | Standalone SWD firmware |
| --- | --- | --- |
| MicroPython REPL TX / RX | P0.18 / P0.16 | P0.18 / P0.16 |
| Reset-time REPL selector | P0.12 (LOW) | P0.20 (LOW) |
| Selector HIGH / floating | Run main.py | Run main.py |
| Bootloader serial DFU | P0.06 / P0.08, P0.20 LOW at boot | Unavailable |
| P0.12 | REPL selector | Ordinary GPIO |
| P0.20 | Adafruit DFU selector | REPL selector |

The selection pin is pulled up and sampled once during the MicroPython startup:
hold it LOW while resetting to enter UART REPL and skip `main.py`. Hold it
HIGH (or leave it floating) to run `main.py` without attaching REPL to
UART0. Because the Adafruit bootloader runs before MicroPython, the DFU build
cannot guarantee selection precisely at the external reset edge; see Issue #18.

Both modes run frozen `_boot.py` and filesystem `boot.py` before UART handoff.
`boot.py` can use UART0 with any supported pins/baud. Upon its return,
the firmware waits up to 50 ms for ongoing UART transmission and then
uninitializes UART0; remaining bytes may be lost if the deadline expires.
When REPL is selected UART0 is subsequently attached using P0.18/P0.16.
Otherwise UART0 is available for `main.py`, including on other pins.

**Important:** A hanging `boot.py` can still prevent entering REPL, so the
mode selector alone does not guarantee recovery from broken boot code.
A Ctrl+D soft reset does not re-sample the hardware selector; power-cycle or
hardware-reset to choose a different mode.

Example of user-mode UART0 configuration (independent of the default REPL pins):

```python
from machine import Pin, UART

uart = UART(0, 115200, tx=Pin("P0_06"), rx=Pin("P0_08"))
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
using TX=P0.18/RX=P0.16 while normal mode's `main.py` can reconfigure
UART0 with different pins and baud. A successful build does not replace this
real-device check.

## VS Code / MicroPico

When using the **MicroPico** VS Code extension with HY0020's UART REPL
(TX=P0.18, RX=P0.16),
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
Adafruit bootloader reservation. The standalone firmware sets the REPL selector to P0.20 while the
bootloader-enabled firmware retains P0.12. Both use REPL TX=P0.18/RX=P0.16.

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
Adafruit DFU cannot install the standalone firmware. After programming,
**power-cycle** the module and verify with J-Link Commander
`mem32 0x1000120C 1` (expected `FFFFFFFE`). Flash erases/recover
operations can erase the UICR setting. Switching back to NFC mode requires
erasing UICR first, which may require backing up and reflashing firmware and
filesystem. Do not connect an NFC antenna while using the GPIO configuration;
NFC overvoltage protection is disabled.

Hardware checks before merge: cold boot, P0.12 LOW/HIGH modes on DFU
firmware and P0.20 LOW/HIGH modes on standalone firmware, UART0 handoff,
P0.09/P0.10 GPIO I2C scan after cold boot,
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

P0.09/P0.10 are also NFC pins on nRF52832. The merged standalone SWD HEX
configures UICR.NFCPINS for GPIO (NFC disabled). P0.20 is owned by the
Adafruit bootloader as the DFU selector only in the bootloader-enabled build.

## Out of scope of the REPL pin relocation

This change does not modify unhandled-exception logging, `print()` routing,
or application-mode execution beyond the existing UART handoff. Those
management-mode design questions remain tracked in Issue #25. NFC remains
a separate future consideration in Issue #24.
