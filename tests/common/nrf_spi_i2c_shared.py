"""nRF shared SPI0/TWI0 resource arbitration and deinit regression test.

Wiring: SPI0 MOSI -> MISO loopback, and I2C0 SDA/SCL with pull-ups.
Edit test_config.py for your board. Both bus IDs are intentionally forced to
zero because SPI0 and TWI0 share a peripheral on nRF52832/nRF52840.
Run on real hardware (not host CI). A timeout is an explicit FAIL.
"""
import errno
from machine import I2C, Pin, SPI
from test_config import (
    SPI_SCK_PIN, SPI_MOSI_PIN, SPI_MISO_PIN,
    I2C_SCL_PIN, I2C_SDA_PIN, I2C_FREQ,
)

CYCLES = 10
PAYLOAD = bytes((0x00, 0x55, 0xAA, 0xFF, 0x13))


def open_spi0():
    return SPI(0, baudrate=125000, polarity=0, phase=0,
               sck=Pin(SPI_SCK_PIN), mosi=Pin(SPI_MOSI_PIN),
               miso=Pin(SPI_MISO_PIN))


def open_i2c0():
    return I2C(0, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN),
               freq=I2C_FREQ)


def expect_busy(create, label):
    try:
        obj = create()
    except OSError as exc:
        if exc.errno != errno.EBUSY:
            raise AssertionError("%s: expected EBUSY, got %r" % (label, exc))
    else:
        obj.deinit()
        raise AssertionError("%s: conflicting init unexpectedly succeeded" % label)


for cycle in range(CYCLES):
    print("Cycle", cycle + 1, "/", CYCLES)
    spi = open_spi0()
    try:
        expect_busy(open_i2c0, "I2C0 while SPI0 owns resource")
        rx = bytearray(len(PAYLOAD))
        spi.write_readinto(PAYLOAD, rx)
        assert bytes(rx) == PAYLOAD, "SPI0 loopback mismatch: %r" % rx
    finally:
        spi.deinit()
        spi.deinit()  # Repeated deinit must be safe.

    i2c = open_i2c0()
    try:
        expect_busy(open_spi0, "SPI0 while I2C0 owns resource")
        print("I2C devices:", [hex(a) for a in i2c.scan()])
    finally:
        i2c.deinit()
        i2c.deinit()  # Repeated deinit must be safe.

print("RESULT: PASS")
