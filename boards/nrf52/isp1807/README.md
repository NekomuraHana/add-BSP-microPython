# Switch Science ISP1807 Breakout BSP

MicroPython BSP for the Switch Science ISP1807 development/breakout board using
the Insight SiP ISP1807-LR (nRF52840) module.

The initial hardware target is the USB Type-C board (SSCI-064545). The older
Micro-B board uses the same ISP1807 breakout design and should share the same
MCU-side mappings.

## Console

The MicroPython REPL is configured for the board's native USB connector using
USB CDC.

USB identity follows the official Switch Science Arduino board definition:

- VID: `0x2786`
- PID: `0x920D`
- Manufacturer: `Switch Science, Inc.`
- Product: `SSCI ISP1807 Breakout`
- CDC interface: `MicroPython REPL`

Note that VID/PID alone should not be used to distinguish the bootloader from
the application. The board's software ecosystem can use the board-assigned USB
identity in both contexts.

Hardware UART remains available to Python applications through
`machine.UART(0, ...)` and `machine.UART(1, ...)`, but neither instance is
attached to the REPL.

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

Board aliases are also provided:

- `LED` -> P0.06
- `TX` -> P0.11
- `RX` -> P0.25

For example, the on-board LED can be opened with
`Pin("LED", Pin.OUT)`.

UART0 keeps P0.11/P0.25 as the board defaults, while the repository's nRF UART
patch also allows applications to select other exposed GPIOs. The same patch
exposes the nRF52840's second UARTE peripheral as `UART(1)`.

```python
from machine import Pin, UART

# UART0 board defaults: TX=P0.11, RX=P0.25
uart0 = UART(0, 115200)

# Override UART0 routing when another pair of exposed GPIOs is needed.
uart0 = UART(0, 115200, tx=Pin(13), rx=Pin(14))

# UARTE1 is also available. Select its pins explicitly so it does not reuse
# UART0's board-default routing.
uart1 = UART(1, 115200, tx=Pin(15), rx=Pin(16))
```

The nRF52840 hardware already provides UARTE0/UARTE1 and the upstream nrfx
configuration enables both. The repository patch only extends MicroPython's nRF
`machine.UART` binding so its object table and IRQ roots can represent both
instances.

## Bootloader / flash layout

The Switch Science board uses an Adafruit-compatible serial DFU bootloader and
S140 6.1.1. The MicroPython application starts at 0x26000 and the current BSP
keeps the application below 0xED000.

This BSP reserves 0xED000-0x100000 so MicroPython's ROMFS/LittleFS regions do
not extend into the top-of-flash bootloader/settings area used by this board
family.

## Filesystem

Internal flash uses LittleFS2.

The upstream MicroPython nRF port mounts its internal flash filesystem at
`/flash`. This BSP uses a board-specific frozen `_boot.py` and mounts the same
flash block device at `/` instead. This makes absolute file paths such as
`/main.py` work with generic MicroPython host tools, including MicroPico's
`Upload File to Board` command.

The filesystem storage region itself is unchanged; only the VFS mount point is
changed for this board.

## Firmware outputs

CI produces both raw debugger images and a serial-DFU package:

```text
firmware.hex
firmware.bin
firmware.elf
firmware.uf2
firmware-dfu.zip
```

For a board that still has the Switch Science/Adafruit-compatible bootloader,
`firmware.uf2` is the easiest image for drag-and-drop installation through
the UF2 mass-storage bootloader. The CI converts the built HEX with
MicroPython's own `tools/uf2conv.py` using the nRF52840 family ID
`0xADA52840`.

`firmware-dfu.zip` remains available for serial DFU. Serial DFU updates the
bootloader's application metadata as part of the normal update flow.

A raw `firmware.hex` is useful for SWD/J-Link development, but replacing only
the application flash while retaining old bootloader settings can leave the
bootloader's stored application metadata inconsistent with the new image.

Example serial DFU command after entering the bootloader:

```bash
adafruit-nrfutil dfu serial \
  --package firmware-dfu.zip \
  -p <serial-port> \
  -b 115200
```

## Local build

The local helper mirrors the nRF build sequence used by CI, but does not install
the compiler toolchain.

From the repository root:

```bash
git submodule update --init
python3 scripts/build.py isp1807
```

The local helper applies the repository-maintained MicroPython patches before
building. Re-running the helper is safe when those patches are already applied.

## GitHub Actions

CI follows the upstream MicroPython nRF build pattern directly. It also runs
`scripts/verify_isp1807_firmware.py` against the generated binary so a build
fails if the vector table, application bounds, USB VID/PID, or expected USB
strings are not actually present in the firmware.
