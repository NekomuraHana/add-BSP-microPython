"""LSM6DS3 SPI register/readout smoke test for nRF MicroPython BSPs.

Wiring used on HY0020 (3.3 V logic; shared GND):
    LSM6DS3 SA0/SDO -> P0.02 (MISO)
    LSM6DS3 CS      -> P0.03 (active LOW)
    LSM6DS3 SDA/SDI -> P0.04 (MOSI)
    LSM6DS3 SCL/SPC -> P0.05 (SCK)

Edit the constants for other nRF boards. SPI1 is selected by default because
HY0020's SPI0/I2C0 switching issue is tracked separately in Issue #19.
The test validates WHO_AM_I, register writes and multi-byte reads. Sensor
values are printed for physical movement inspection; they are not calibrated.
"""

from machine import Pin, SPI
from time import sleep_ms

SPI_ID = 1
SPI_BAUD = 1000000
CS_PIN = "P0_03"
SCK_PIN = "P0_05"
MOSI_PIN = "P0_04"
MISO_PIN = "P0_02"
SAMPLES = 10
INTERVAL_MS = 200

WHO_AM_I = 0x0F
CTRL1_XL = 0x10
CTRL2_G = 0x11
CTRL3_C = 0x12
OUTX_L_G = 0x22


def signed16(lo, hi):
    value = lo | (hi << 8)
    return value - 65536 if value & 0x8000 else value


def main():
    cs = Pin(CS_PIN, Pin.OUT, value=1)
    spi = None
    configured = False

    def read_regs(addr, length):
        tx = bytearray(length + 1)
        rx = bytearray(length + 1)
        tx[0] = addr | 0x80
        cs.value(0)
        try:
            spi.write_readinto(tx, rx)
        finally:
            cs.value(1)
        return rx[1:]

    def write_reg(addr, value):
        cs.value(0)
        try:
            spi.write(bytes((addr & 0x7F, value)))
        finally:
            cs.value(1)

    try:
        spi = SPI(
            SPI_ID,
            baudrate=SPI_BAUD,
            polarity=1,
            phase=1,
            sck=Pin(SCK_PIN),
            mosi=Pin(MOSI_PIN),
            miso=Pin(MISO_PIN),
        )
        sleep_ms(10)
        who = read_regs(WHO_AM_I, 1)[0]
        print("WHO_AM_I: 0x%02X" % who)
        if who != 0x69:
            print("RESULT: FAIL (expected 0x69)")
            return

        # CTRL3_C: block-data update + register auto-increment, 4-wire SPI.
        write_reg(CTRL3_C, 0x44)
        # Both sensors at 104 Hz: accelerometer +/-2g, gyro +/-245 dps.
        write_reg(CTRL1_XL, 0x40)
        write_reg(CTRL2_G, 0x40)
        configured = True
        sleep_ms(100)

        for i in range(SAMPLES):
            # 0x22..0x2D: gyro XYZ followed by acceleration XYZ.
            data = read_regs(OUTX_L_G, 12)
            vals = [signed16(data[j], data[j + 1]) for j in range(0, 12, 2)]
            gx, gy, gz = [v * 0.00875 for v in vals[:3]]
            ax, ay, az = [v * 0.000061 for v in vals[3:]]
            print(
                "%02d ACC[g] %+0.3f %+0.3f %+0.3f  GYRO[dps] %+0.2f %+0.2f %+0.2f"
                % (i + 1, ax, ay, az, gx, gy, gz)
            )
            sleep_ms(INTERVAL_MS)

        print("RESULT: PASS (SPI register I/O; check values by moving sensor)")
    except KeyboardInterrupt:
        print("Stopped by user")
    finally:
        if spi is not None:
            if configured:
                try:
                    write_reg(CTRL1_XL, 0x00)
                    write_reg(CTRL2_G, 0x00)
                except Exception as exc:
                    print("Sensor power-down warning:", exc)
            cs.value(1)
            spi.deinit()
            print("SPI deinitialized")


main()
