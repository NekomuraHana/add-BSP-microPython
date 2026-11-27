"""Manual HY0020 scheduler smoke test; requires unused Timer4."""
import micropython
import time
from machine import Timer

assert hasattr(micropython, "schedule")
events = 0
queued = False
queue_full = False
value = 0


def deferred(arg):
    global events, queued, value
    # Allocate a large integer in VM context, not in the IRQ.
    value = 1700000000000 + arg
    events += 1
    queued = False


def irq(timer):
    global queued, queue_full
    if not queued:
        queued = True
        try:
            micropython.schedule(deferred, 1)
        except RuntimeError:
            queued = False
            queue_full = True


micropython.schedule(deferred, 0)
start = time.ticks_ms()
while events == 0 and time.ticks_diff(time.ticks_ms(), start) < 2000:
    time.sleep_ms(10)
assert events == 1
assert value == 1700000000000

timer = Timer(4, period=1000000, mode=Timer.PERIODIC, callback=irq)
try:
    timer.start()
    start = time.ticks_ms()
    while events < 4 and time.ticks_diff(time.ticks_ms(), start) < 10000:
        time.sleep_ms(10)
    assert events >= 4, events
    assert value == 1700000000001
    assert not queue_full
finally:
    timer.stop()
    timer.deinit()

print("RESULT: PASS")
