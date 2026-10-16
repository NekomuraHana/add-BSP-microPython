"""UART0 loopback: wire selected TX to RX using 3.3V-compatible pins.
Do not run on the REPL-owned UART (e.g. future HY0020 maintenance mode).
"""
import time
from machine import Pin, UART
from test_config import UART_ID, UART_TX_PIN, UART_RX_PIN, UART_BAUD

uart = UART(UART_ID, UART_BAUD, tx=Pin(UART_TX_PIN), rx=Pin(UART_RX_PIN))
payload = b"micropython-uart-loopback"
while uart.any():
    uart.read()
uart.write(payload)
received = bytearray()
deadline = time.ticks_add(time.ticks_ms(), 2000)
while len(received) < len(payload) and time.ticks_diff(deadline, time.ticks_ms()) > 0:
    data = uart.read()
    if data:
        received.extend(data)
    else:
        time.sleep_ms(10)
assert bytes(received) == payload, "UART loopback mismatch: %r" % bytes(received)
print("RESULT: PASS")
