# Hardware smoke tests

The reusable scripts are in `tests/common/`. They are **manual, on-device**
hardware tests, not host-side CI unit tests. Each board needs physical wiring,
a flashed firmware, and a `test_config.py` adjusted to its pin map.

## Setup
1. Copy `tests/common/test_config.py` and edit it for your target board.
2. Copy that configuration file alongside the specific common test to the board
   (or ensure the same directory is on `sys.path`).
3. Run a test through the device's REPL with `exec(open("name.py").read())`
   or an equivalent `mpremote run` command.
4. Treat `RESULT: PASS` as hardware evidence only for the run performed.

## What each test needs

| Test | Connections / requirements |
| --- | --- |
| `gpio.py` | LED or monitored output and a separately driven input |
| `uart_loopback.py` | TX wired to RX; UART not in use for console |
| `i2c_sht3x.py` | Sensirion SHT30/SHT31/SHT35 on 0x44 or 0x45, SDA/SCL pull-ups |
| `spi_loopback.py` | MOSI wired to MISO (hardware SPI) |
| `ble_raw_uuid.py` | Legacy `ubluepy` Central firmware and a BLE peer address |
| `ble_central_gatt_rw.py` | Specific NUS-to-UART bridge peripheral, matching UART wiring |

BLE GATT test requires a peer exposing `0bf10001-7dfb-4e4a-b734-f40d695f67ab`
(readable settings) and NUS RX characteristic `6e400002-b5a3-f393-e0a9-e50e24dcca9e`;
**it does not test Notify**. It must not alter peer persistent UART configuration.

The original `tests/isp1807_ble_*.py` are retained unchanged as ISP1807
historical/known-wiring regression examples. Generalized scripts use
`test_config.py` rather than hardcoded peer MACs and GPIOs.

## Board notes
- ISP1807: REPL uses native USB CDC, so hardware UART0 is available for tests.
  SHT31 example wiring previously tested: SCL=P0.26, SDA=P0.14.
- HY0020 (planned): nRF52832 only has one hardware UART peripheral; tests
  requiring UART0 must run in the normal (non-UART-REPL) boot mode.
- SPI loopback verifies the physical port and wiring, **not** an SPI sensor.
- The test suite does not yet automate physical-device testing in CI.
