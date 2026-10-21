"""Manual GPIO output/input smoke test; connect input to a safe logic source."""
import time
from machine import Pin
from test_config import GPIO_OUTPUT_PIN, GPIO_INPUT_PIN

out_pin = Pin(GPIO_OUTPUT_PIN, Pin.OUT)
input_pin = Pin(GPIO_INPUT_PIN, Pin.IN)
try:
    for _ in range(10):
        out_pin.value(1 - out_pin.value())
        print("GPIO OUT:", out_pin.value(), "IN:", input_pin.value())
        time.sleep_ms(500)
finally:
    out_pin.value(0)
