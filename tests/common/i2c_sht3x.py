"""Sensirion SHT3x (e.g. SHT31) I2C temperature/humidity test.
Default single-shot high-repeatability mode without clock stretching.
SHT3x I2C address: 0x44 or 0x45. Requires powered sensor, common GND,
and proper SDA/SCL pull-ups. No heater activation or persistent writes.
"""
import time
from machine import Pin, I2C
from test_config import I2C_ID, I2C_SCL_PIN, I2C_SDA_PIN, I2C_FREQ


def crc8(data):
    crc = 0xff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc << 1) ^ 0x31) & 0xff if crc & 0x80 else (crc << 1) & 0xff
    return crc


i2c = I2C(I2C_ID, scl=Pin(I2C_SCL_PIN), sda=Pin(I2C_SDA_PIN), freq=I2C_FREQ)
addresses = [a for a in i2c.scan() if a in (0x44, 0x45)]
if len(addresses) != 1:
    raise RuntimeError("Expected exactly one SHT3x at 0x44 or 0x45; found %r" % addresses)
addr = addresses[0]
i2c.writeto(addr, b"\x24\x00")
time.sleep_ms(20)
data = i2c.readfrom(addr, 6)
if len(data) != 6 or crc8(data[:2]) != data[2] or crc8(data[3:5]) != data[5]:
    raise ValueError("SHT3x CRC/length mismatch: %r" % data)
raw_t = (data[0] << 8) | data[1]
raw_rh = (data[3] << 8) | data[4]
print("SHT3x 0x%02x: %.2f C, %.2f %%RH" % (addr, -45 + 175 * raw_t / 65535, 100 * raw_rh / 65535))
print("RESULT: PASS")
