"""Test BLE Central NUS Write -> peripheral UART TX -> device under test UART RX.

Connections (3.3 V logic, common ground):
  Peripheral TX -> device under test P0.07 (UART0 RX)
  Peripheral RX <- device under test P0.08 (UART0 TX)  [not used by this test]
  Peripheral GND -- device under test GND

GATT Read checks only the peripheral UART settings. No CCCD or Notify.
The peer must bridge received NUS data to its UART TX.
"""
import time
from machine import Pin, UART
from ubluepy import Peripheral, Scanner

from test_config import BLE_TARGET_ADDR as TARGET_ADDR
READ_UUID = "0bf10001-7dfb-4e4a-b734-f40d695f67ab"  # Peripheral UART settings (read-only test)
WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # Peripheral NUS RX
WRITE_DATA = b"bsp-test"
WITH_RESPONSE = True
from test_config import UART_ID
from test_config import UART_BAUD
from test_config import UART_TX_PIN, UART_RX_PIN
UART_TIMEOUT_MS = 3000
PROP_READ = 0x02
PROP_WRITE_NO_RSP = 0x04
PROP_WRITE = 0x08


def uuid_text(raw):
    if len(raw) == 2:
        return "0x%04x" % (raw[0] | (raw[1] << 8))
    if len(raw) != 16:
        raise ValueError("Invalid UUID size %d" % len(raw))
    h = "".join("%02x" % n for n in reversed(raw))
    return "%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])


def discover_characteristics(central):
    database = {}
    for service in central.getServices():
        for char in service.getCharacteristics():
            declaration = bytes(central.readHandle(char.getDeclarationHandle()))
            if len(declaration) not in (5, 19):
                raise ValueError("Invalid characteristic declaration")
            value_handle = declaration[1] | (declaration[2] << 8)
            if value_handle != char.getHandle():
                raise ValueError("Characteristic declaration handle mismatch")
            props = declaration[0]
            uuid = uuid_text(declaration[3:]).lower()
            if uuid in database:
                raise ValueError("Duplicate characteristic UUID: " + uuid)
            database[uuid] = (value_handle, props)
    return database


def read_uart_bytes(uart, expected_length):
    received = bytearray()
    deadline = time.ticks_add(time.ticks_ms(), UART_TIMEOUT_MS)
    while len(received) < expected_length and time.ticks_diff(deadline, time.ticks_ms()) > 0:
        available = uart.any()
        if available:
            data = uart.read(min(available, expected_length - len(received)))
            if data:
                received.extend(data)
        else:
            time.sleep_ms(10)
    # Catch unwanted trailing bytes (e.g. a newline or repeated transmission).
    time.sleep_ms(100)
    while uart.any():
        data = uart.read()
        if not data:
            break
        received.extend(data)
    return bytes(received)


def main():
    if not WRITE_DATA or len(WRITE_DATA) > 20:
        raise ValueError("WRITE_DATA must contain 1..20 bytes")
    uart = UART(UART_ID, UART_BAUD, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN))
    found = None
    for entry in Scanner().scan(5000):
        if entry.addr().lower() == TARGET_ADDR.lower():
            found = entry
            break
    if found is None:
        raise RuntimeError("Target not found")
    central = Peripheral()
    central.connect(found.addr(), addr_type=found.addr_type())
    database = discover_characteristics(central)
    read_target = database.get(READ_UUID.lower())
    if read_target is None or not (read_target[1] & PROP_READ):
        raise ValueError("UART settings characteristic missing or not readable")
    settings = bytes(central.readHandle(read_target[0]))
    target = database.get(WRITE_UUID.lower())
    if target is None:
        raise ValueError("NUS RX UUID not found")
    value_handle, properties = target
    required = PROP_WRITE if WITH_RESPONSE else PROP_WRITE_NO_RSP
    if not (properties & required):
        raise ValueError("Selected characteristic does not support requested write mode")

    # Remove previous UART data so only this test message is compared.
    while uart.any():
        uart.read()
    central.writeHandle(value_handle, WRITE_DATA, WITH_RESPONSE)
    actual = read_uart_bytes(uart, len(WRITE_DATA))
    return settings, actual


# UART0 may also carry the REPL on some boards. Persist results instead of
# depending on console output (read after rebooting into REPL mode).
LOG_FILE = "/ble_central_gatt_test.txt"
try:
    settings, actual = main()
    verdict = "PASS" if actual == WRITE_DATA else "FAIL"
    error = None
except Exception as exc:
    settings, actual = None, None
    verdict = "ERROR"
    error = repr(exc)
with open(LOG_FILE, "w") as log:
    log.write("BLE Central GATT + UART test\n")
    log.write("settings: %r\n" % settings)
    log.write("expected UART: %r\n" % WRITE_DATA)
    log.write("actual UART: %r\n" % actual)
    if error:
        log.write("error: %s\n" % error)
    log.write("RESULT: %s\n" % verdict)
