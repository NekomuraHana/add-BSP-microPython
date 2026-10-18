"""BLE Peripheral write-event smoke test (legacy ubluepy).

Run on a board with working BLE support and an accessible REPL.
A BLE Central can connect and write to the characteristic; events and the
received byte payload are printed to the REPL. No LEDs or GPIOs are used.

The characteristic is write-only (with and without response). This test
does not check notifications or reads.
"""
import time
from ubluepy import Service, Characteristic, UUID, Peripheral, constants

SERVICE_UUID = UUID("12345678-1234-5678-1234-56789abcdef0")
WRITE_CHAR_UUID = UUID("12345678-1234-5678-1234-56789abcdef1")
DEVICE_NAME = "MicroPython-BSP"

service = Service(SERVICE_UUID)
write_char = Characteristic(
    WRITE_CHAR_UUID,
    props=Characteristic.PROP_WRITE | Characteristic.PROP_WRITE_WO_RESP,
)
service.addCharacteristic(write_char)

peripheral = Peripheral()
peripheral.addService(service)


def ble_event(event_id, handle, data):
    print("BLE event:", event_id, "handle:", handle, "data:", data)

    if event_id == constants.EVT_GAP_CONNECTED:
        print("connected")
    elif event_id == constants.EVT_GAP_DISCONNECTED:
        print("disconnected")
        peripheral.advertise(device_name=DEVICE_NAME, services=[service])
    elif event_id == constants.EVT_GATTS_WRITE:
        if data is None:
            print("write: None")
        else:
            print("write:", bytes(data))


peripheral.setConnectionHandler(ble_event)
peripheral.advertise(device_name=DEVICE_NAME, services=[service])
print("Advertising:", DEVICE_NAME)

while True:
    time.sleep(1)
