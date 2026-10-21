"""Hardware SPI loopback. Physically connect MOSI -> MISO (3.3V).
SPI instance/pins must be supported by the board's nRF port.
"""
from machine import Pin, SPI
from test_config import SPI_ID, SPI_SCK_PIN, SPI_MOSI_PIN, SPI_MISO_PIN

spi = SPI(SPI_ID, baudrate=100000, polarity=0, phase=0,
          sck=Pin(SPI_SCK_PIN), mosi=Pin(SPI_MOSI_PIN),
          miso=Pin(SPI_MISO_PIN))
payload = bytes((0x00, 0x55, 0xaa, 0xff, 0x13))
rx = bytearray(len(payload))
spi.write_readinto(payload, rx)
assert bytes(rx) == payload, "SPI loopback mismatch: %r" % rx
print("RESULT: PASS")
