# ISP1807-LR BSP

Initial MicroPython BSP for the Insight SiP ISP1807-LR module.

## Hardware basis

- SoC: Nordic Semiconductor nRF52840
- Flash: 1 MB
- RAM: 256 kB
- Integrated 32 MHz and 32.768 kHz crystals
- Integrated RF matching, antenna, and DC/DC support components
- 46 module GPIOs
- USB D+/D-/VBUS are exposed
- NFC pins are P0.09 / P0.10

The module does not expose nRF52840 P0.00 or P0.01. Accordingly, the
MicroPython pin table starts at software pin P2.

For the nRF port, software pins P0-P31 correspond to nRF P0.00-P0.31,
and P32-P47 correspond to nRF P1.00-P1.15.

## Initial peripheral defaults

Because ISP1807-LR is a module rather than a complete carrier board,
UART and SPI routing are not physically fixed. This BSP currently uses:

- UART0 RX: P0.08
- UART0 TX: P0.06
- UART hardware flow control: disabled
- SPI0 SCK: P1.15
- SPI0 MOSI: P1.13
- SPI0 MISO: P1.14

Carrier-board-specific BSPs can override these mappings later.

## Build

From the repository root:

```bash
git submodule update --init
python3 scripts/build.py isp1807
```

The default build includes the S140 SoftDevice.
