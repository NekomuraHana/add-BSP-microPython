# Switch Science ISP1807 Breakout BSP

MicroPython BSP for the Switch Science ISP1807 development/breakout board using
the Insight SiP ISP1807-LR (nRF52840) module.

The initial hardware target is the USB Type-C board (SSCI-064545). The older
Micro-B board uses the same ISP1807 breakout design and should share the same
MCU-side mappings.

## Console

The MicroPython REPL is configured for the board's native USB connector using
USB CDC.

USB identity follows the Switch Science board definition:

- VID: `0x2786`
- PID: `0x920D`
- Manufacturer: `Switch Science`
- Product: `ISP1807 Breakout`
- CDC interface: `MicroPython REPL`

Hardware UART is still available to Python applications through
`machine.UART(0, ...)`, but it is deliberately not attached to the REPL.

## Board mappings

- User LED: P0.06, active-low
- User button: P1.06
- UART RX: P0.25
- UART TX: P0.11
- SPI0 SCK: P0.14
- SPI0 MOSI: P0.10
- SPI0 MISO: P0.12
- NFC: P0.09 / P0.10

The pin names follow the nRF port convention: P0-P31 map to nRF P0.00-P0.31
and P32-P47 map to nRF P1.00-P1.15.

## Bootloader / flash layout

The Switch Science board ships with an Adafruit-compatible bootloader and S140
6.1.1. The application area starts at 0x26000 and must end before 0xED000.

This BSP reserves 0xED000-0x100000 so MicroPython's ROMFS/LittleFS regions
cannot overlap the pre-installed bootloader and settings pages.

Important: an earlier revision of this BSP did not reserve this flash tail.
Booting that revision could allow filesystem initialisation to touch the
bootloader region. If a board no longer enters the pre-installed bootloader
after testing the older image, restore the Switch Science bootloader before
continuing.

## Local build

The local helper mirrors the same nRF build sequence used by the CI, but does
not install the compiler toolchain. Install the ARM GCC toolchain first.

From the repository root:

```bash
git submodule update --init
python3 scripts/build.py isp1807
```

The build uses S140 6.1.1 and produces:

```text
micropython/ports/nrf/build-ISP1807_LR-s140/
├─ firmware.hex
├─ firmware.bin
└─ firmware.elf
```

The generated `firmware.hex` is the MicroPython application image. It assumes
the board already has the matching S140/bootloader environment supplied by
Switch Science.

## GitHub Actions

CI deliberately does not call `scripts/build.py`. It follows the upstream
MicroPython nRF CI pattern directly:

1. `./tools/ci.sh nrf_setup`
2. stage the ISP1807 board files under `ports/nrf/boards/ISP1807_LR`
3. download S140 6.1.1
4. build `mpy-cross`
5. fetch nRF submodules
6. run the standard nRF `make BOARD=ISP1807_LR SD=s140`

This keeps CI behaviour close to upstream while retaining `build.py` as a
developer convenience for local builds.
