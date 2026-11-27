import time
from light_rtc import LightRTC


class FakeTime:
    def __init__(self):
        self.now = 250

    def ticks_ms(self):
        return self.now

    def ticks_diff(self, a, b):
        return ((a - b + 128) % 256) - 128


fake = FakeTime()
rtc = LightRTC(1700000000, time_module=fake)
assert rtc.time_ms() == 1700000000000
fake.now = 4
assert rtc.time_ms() == 1700000000010
for _ in range(20):
    fake.now = (fake.now + 100) % 256
    rtc.update()
assert rtc.time_ms() == 1700000002010
assert rtc.time() == 1700000002
rtc.set_time(1800000000)
assert rtc.time_ms() == 1800000000000
fake.now = (fake.now + 128) % 256
try:
    rtc.update()
except RuntimeError:
    pass
else:
    raise AssertionError("ambiguous tick delta not rejected")

rtc = LightRTC(1700000000)
start = rtc.time_ms()
time.sleep_ms(1000)
elapsed = rtc.time_ms() - start
assert 950 <= elapsed <= 1500, elapsed
print("LightRTC PASS")
