"""ISP1807 nRF52 legacy ubluepy Central / NUS validation.

Before running, wire the BLE-UART converter UART TX to RX (3.3V logic).
Set TARGET_ADDR and (after determining it from a BLE GATT inspector) CCCD_HANDLE.
NUS is a notification-based protocol; its TX characteristic is not GATT-readable.
"""

from ubluepy import Scanner, Peripheral, UUID
import time

TARGET_ADDR = "d0:ef:3b:c9:9b:55"  # Change if your device has a different address
CCCD_HANDLE = None  # Set the discovered descriptor handle (UUID 0x2902) for NUS TX
NUS_SERVICE = UUID("6e400001-b5a3-f393-e0a9-e50e24dcca9e")
NUS_RX = UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e")
NUS_TX = UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e")
TEST_DATA = b"ISP1807_LOOPBACK\r\n"

# IMPORTANT: Create all 128-bit UUID objects before service discovery!
# Nordic SoftDevice only resolves vendor UUIDs for registered bases.
print("Scanning...")
target = None
for entry in Scanner().scan(5000):
    print(entry.addr(), entry.rssi())
    if entry.addr().lower() == TARGET_ADDR.lower():
        target = entry
if target is None:
    raise RuntimeError("Target not found")

ble = Peripheral()
ble.connect(target.addr(), addr_type=target.addr_type())
print("Connected")
rx = None
tx = None
for svc in ble.getServices():
    print("Service:", svc.uuid())
    for ch in svc.getCharacteristics():
        print("  Characteristic:", ch.uuid(), "handle:", ch.getHandle())
        if ch.uuid().binVal() == NUS_RX.binVal() and ch.uuid().binVal() == 2:
            rx = ch
        if ch.uuid().binVal() == NUS_TX.binVal() and ch.uuid().binVal() == 3:
            tx = ch
if rx is None or tx is None:
    raise RuntimeError("NUS RX/TX not discovered. Confirm UUID registration and firmware patch")

received = []
def on_notify(handle, data):
    print("Notify:", handle, data)
    received.append(bytes(data))

ble.setNotificationHandler(on_notify)
if CCCD_HANDLE is None:
    print("Set CCCD_HANDLE to NUS TX's 0x2902 descriptor handle before the loopback test.")
else:
    ble.writeHandle(CCCD_HANDLE, b"\x01\x00")  # enable notifications via CCCD
    time.sleep_ms(100)
    rx.write(TEST_DATA)
    print("Wrote:", TEST_DATA)
    for _ in range(40):
        if received:
            break
        time.sleep_ms(100)
    if TEST_DATA in received:
        print("LOOPBACK PASS")
    else:
        print("LOOPBACK NOT CONFIRMED", received)

# Standard GATT Read smoke test (Device Name UUID 0x2A00):
for svc in ble.getServices():
    for ch in svc.getCharacteristics():
        if ch.uuid().binVal() == 0x2A00:
            print("Device Name GATT Read:", ch.read())
