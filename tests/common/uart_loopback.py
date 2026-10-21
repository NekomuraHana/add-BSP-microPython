"""UART loopback: connect TX to RX, then read /uart_test.txt after reboot.
Run only when UART0 is not owned by REPL. File storage must be mounted.
"""
import time
from machine import Pin, UART
from test_config import UART_ID, UART_TX_PIN, UART_RX_PIN, UART_BAUD

LOG_FILE = "/uart_test.txt"
payload = b"micropython-uart-loopback"
result = "FAIL"
received = bytearray()

try:
    uart = UART(UART_ID, UART_BAUD, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN))
    while uart.any():
        uart.read()
    uart.write(payload)
    deadline = time.ticks_add(time.ticks_ms(), 2000)
    while len(received) < len(payload) and time.ticks_diff(deadline, time.ticks_ms()) > 0:
        data = uart.read()
        if data:
            received.extend(data)
        else:
            time.sleep_ms(10)
    result = "PASS" if bytes(received) == payload else "FAIL"
except Exception as exc:
    result = "ERROR: %r" % exc

with open(LOG_FILE, "w") as log:
    log.write("UART loopback\n")
    log.write("expected: %r\n" % payload)
    log.write("received: %r\n" % bytes(received))
    log.write("RESULT: %s\n" % result)
