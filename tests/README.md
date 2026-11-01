# Hardware smoke tests

The reusable scripts are in `tests/common/`. They are **manual, on-device**
hardware tests, not host-side CI unit tests. Each board needs physical wiring,
a flashed firmware, and a `test_config.py` adjusted to its pin map.

## Setup
1. Copy `tests/common/test_config.py` and edit it for your target board.
2. Copy that configuration file alongside the specific common test to the board
   (or ensure the same directory is on `sys.path`).
3. For a board sharing REPL and UART0, place the test on the filesystem as `main.py` or launch it in the **normal UART mode** after reset. Do not run UART0 tests in UART-REPL mode.
4. Switch back to REPL mode and **reset the device** before reading the UART-related persisted log files. For boards with a separate USB REPL, tests may also be launched from that REPL.
5. Each UART-related test run overwrites its own log. `RESULT: PASS` is evidence only for that physical run.

## What each test needs

| Test | Connections / requirements |
| --- | --- |
| `gpio.py` | LED or monitored output and a separately driven input |
| `uart_loopback.py` | TX wired to RX; UART not in use for console; writes `/uart_test.txt` |
| `i2c_sht3x.py` | Sensirion SHT30/SHT31/SHT35 on 0x44 or 0x45, SDA/SCL pull-ups |
| `spi_loopback.py` | MOSI wired to MISO (hardware SPI) |
| `nrf_spi_i2c_shared.py` | nRF SPI0 MOSI wired to MISO, I2C0 SDA/SCL pull-ups; tests conflict EBUSY, 10 alternating cycles, repeated deinit |
| `ble_peripheral_write.py` | BLE Peripheral advertising; show connect/disconnect and GATT Write payloads on REPL; requires a BLE Central to write |
| `ble_central_scan.py` | Repeating 1-second BLE advertisements scan: device name + advertised Primary Service UUID list; stop with Ctrl-C |
| `ble_central_gatt_rw.py` | Match NUS-to-UART peer by advertised Primary Service UUID, perform GATT Read/Write and UART check, write `/ble_central_gatt_test.txt` |

BLE Peripheral write test outputs events to REPL (no file logging) and uses service UUID `12345678-1234-5678-1234-56789abcdef0` and write characteristic UUID `12345678-1234-5678-1234-56789abcdef1`. Write data is displayed in full as bytes; there is no LED control. Ensure the REPL remains available during BLE events.

BLE GATT test requires a peer exposing `0bf10001-7dfb-4e4a-b734-f40d695f67ab`
(readable settings) and NUS RX characteristic `6e400002-b5a3-f393-e0a9-e50e24dcca9e`;
**it does not test Notify**. It must not alter peer persistent UART configuration.

The original `tests/isp1807_ble_*.py` are retained unchanged as ISP1807
historical/known-wiring regression examples. Generalized scripts use `test_config.py` for wiring and the Central peer's Primary Service UUID rather than a fixed MAC. `ble_central_scan.py` uses `ble_parse_adv.py` to decode AD types 0x08/0x09 (names) and 0x02/0x03/0x06/0x07 (advertised service UUIDs). It does not connect to devices or enumerate their full GATT database. The Central peer must actually advertise the configured UUID; if the UUID is omitted due to the 31-byte legacy advertising limit, automatic matching is not possible with this test.

## Shared nRF SPI0/I2C0 regression (Issue #19)

The nRF peripheral instances `SPI0` and `I2C(0)` (TWI0) compete for the
same hardware resource. The patch in `patches/micropython/nrf-spi-i2c-resource-management.patch`
makes the attempted second initialization raise `OSError(errno.EBUSY)` without
preempting the first driver. The application releases ownership with the
corresponding `deinit()` call; repeated `deinit()` is harmless.

For the hardware test, configure SPI loopback pins and an I2C bus with pull-ups
in `tests/common/test_config.py`. Run `nrf_spi_i2c_shared.py`; it forces
instance 0 for both buses, exercises expected busy errors in each direction,
performs SPI loopback and I2C scan, and alternates 10 times.
`RESULT: PASS` requires actual device execution; successful CI compilation is
**not** hardware verification. If a transfer times out, it should raise
`OSError(ETIMEDOUT)` instead of hanging REPL. This test does not verify a
sensor's returned data.

## Board notes
- ISP1807: REPL uses native USB CDC, so hardware UART0 is available for tests.
  SHT31 example wiring previously tested: SCL=P0.26, SDA=P0.14.
- HY0020 (planned): nRF52832 only has one hardware UART peripheral; tests
  requiring UART0 must run in the normal (non-UART-REPL) boot mode.
- SPI loopback verifies the physical port and wiring, **not** an SPI sensor.
- The test suite does not yet automate physical-device testing in CI.

## Reading test logs from REPL

After the UART test finishes, switch to REPL mode and reset the board, then run:

```python
with open("/uart_test.txt") as f:
    print(f.read())

with open("/ble_central_gatt_test.txt") as f:
    print(f.read())
```

Read only the files from tests that were executed. The flash filesystem must be
mounted read/write in the test mode and remain persistent across software/hard
resets. These are filesystem writes, so do not cut power before log writes
complete. The BLE Peripheral test instead requires an active REPL to view its output.
