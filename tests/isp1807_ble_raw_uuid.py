"""Generic BLE GATT UUID discovery smoke test on ISP1807.

Upload lib/ble_gatt_uuid.py to /lib/ble_gatt_uuid.py on the board first.
This script needs no vendor UUID preregistration.
"""

from ubluepy import Peripheral, Scanner
from ble_gatt_uuid import service_uuid, characteristic_uuid

TARGET_ADDR = "d0:ef:3b:c9:9b:55"  # Change to the peripheral being tested

target = None
for entry in Scanner().scan(5000):
    if entry.addr().lower() == TARGET_ADDR.lower():
        target = entry
        break

if target is None:
    raise RuntimeError("Target not found")

central = Peripheral()
central.connect(target.addr(), addr_type=target.addr_type())
print("CONNECTED")

for service in central.getServices():
    start = service.getStartHandle()
    try:
        name = service_uuid(central, service)
    except Exception as exc:
        name = "<unavailable: %s>" % repr(exc)
    print("SERVICE", start, name)

    for characteristic in service.getCharacteristics():
        value_handle = characteristic.getHandle()
        try:
            name = characteristic_uuid(central, characteristic)
        except Exception as exc:
            name = "<unavailable: %s>" % repr(exc)
        print("  CHAR", value_handle, name)
