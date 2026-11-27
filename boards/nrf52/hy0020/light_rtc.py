"""Lightweight Unix clock backed by MicroPython monotonic ticks.

Call time_ms(), time(), or update() at least once per half tick period,
including while idle. Not safe for concurrent or interrupt-context calls.
The clock is not retained across resets and must be initialized again.
"""
import time


class LightRTC:
    def __init__(self, unixtime, time_module=time):
        self._time = time_module
        self.set_time(unixtime)

    def set_time(self, unixtime):
        self._last_ticks = self._time.ticks_ms()
        self._unix_ms = int(unixtime) * 1000

    def update(self):
        now = self._time.ticks_ms()
        elapsed = self._time.ticks_diff(now, self._last_ticks)
        if elapsed < 0:
            raise RuntimeError("LightRTC tick interval exceeded")
        self._unix_ms += elapsed
        self._last_ticks = now

    def time_ms(self):
        self.update()
        return self._unix_ms

    def time(self):
        return self.time_ms() // 1000
