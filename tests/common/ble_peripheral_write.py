"""BLE Peripheral GATT Write logger using legacy ubluepy.
Writes /ble_peripheral_test.txt; inspect after switching back to REPL.
The callback only queues small events. The main loop performs filesystem I/O.
No LED / GPIO is used. Reboot to end the test.
"""
import time
from ubluepy import Service, Characteristic, UUID, Peripheral, constants

LOG_FILE = "/ble_peripheral_test.txt"
SERVICE_UUID = UUID("12345678-1234-5678-1234-56789abcdef0")
WRITE_CHAR_UUID = UUID("12345678-1234-5678-1234-56789abcdef1")
DEVICE_NAME = "MicroPython-BSP"
MAX_PENDING_EVENTS = 16
pending = []
dropped = 0

service = Service(SERVICE_UUID)
write_char = Characteristic(
    WRITE_CHAR_UUID,
    props=Characteristic.PROP_WRITE | Characteristic.PROP_WRITE_WO_RESP,
)
service.addCharacteristic(write_char)
peripheral = Peripheral()
peripheral.addService(service)


def ble_event(event_id, handle, data):
    global dropped
    # Do not perform flash writes from BLE callbacks.
    if len(pending) < MAX_PENDING_EVENTS:
        pending.append((event_id, handle, None if data is None else bytes(data)))
    else:
        dropped += 1
    if event_id == constants.EVT_GAP_DISCONNECTED:
        peripheral.advertise(device_name=DEVICE_NAME, services=[service])


peripheral.setConnectionHandler(ble_event)
with open(LOG_FILE, "w") as log:
    log.write("BLE Peripheral GATT Write test\n")
    log.write("service: 12345678-1234-5678-1234-56789abcdef0\n")
    log.write("write char: 12345678-1234-5678-1234-56789abcdef1\n")
peripheral.advertise(device_name=DEVICE_NAME, services=[service])

while True:
    # The BLE callback may be invoked asynchronously; only logging happens here.
    if pending or dropped:
        with open(LOG_FILE, "a") as log:
            while pending:
                event_id, handle, data = pending.pop(0)
                if event_id == constants.EVT_GAP_CONNECTED:
                    label = "CONNECTED"
                elif event_id == constants.EVT_GAP_DISCONNECTED:
                    label = "DISCONNECTED"
                elif event_id == constants.EVT_GATTS_WRITE:
                    label = "WRITE"
                else:
                    label = "EVENT"
                log.write("%s event=%d handle=%s data=%r\n" % (label, event_id, handle, data))
            if dropped:
                log.write("WARNING: dropped %d events\n" % dropped)
                dropped = 0
    time.sleep_ms(100)
