"""ISP1807 Central GATT Read/Write/optional Notify hardware test.

Use only against a test peripheral whose writable characteristic is known.
Set TARGET_ADDR and WRITE_UUID, and explicitly opt in to writing.
For loopback, set NOTIFY_UUID and a verified CCCD_HANDLE.
The test refuses to write before the notification subscription succeeds.
CCCD_HANDLE must come from a GATT descriptor inspector, not handle + 1.
"""
import time
from ubluepy import Peripheral, Scanner

TARGET_ADDR = "d0:ef:3b:c9:9b:55"
WRITE_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"  # NUS RX (peripheral)
NOTIFY_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"  # NUS TX (peripheral)
WRITE_DATA = b"isp1807-test"
ENABLE_WRITE = True
WITH_RESPONSE = True
CCCD_HANDLE = None  # REQUIRED: externally verified TX CCCD (UUID 0x2902)
WAIT_NOTIFY_MS = 3000

PROP_READ = 0x02
PROP_WRITE_NO_RSP = 0x04
PROP_WRITE = 0x08
PROP_NOTIFY = 0x10


def uuid_text(raw):
    if len(raw) == 2:
        return "0x%04x" % (raw[0] | (raw[1] << 8))
    if len(raw) != 16:
        raise ValueError("Invalid UUID size %d" % len(raw))
    h = "".join("%02x" % n for n in reversed(raw))
    return "%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])


def find_target(central):
    selected = {}
    for service in central.getServices():
        for char in service.getCharacteristics():
            declaration = bytes(central.readHandle(char.getDeclarationHandle()))
            if len(declaration) not in (5, 19):
                raise ValueError("Invalid characteristic declaration")
            handle = declaration[1] | (declaration[2] << 8)
            if handle != char.getHandle():
                raise ValueError("Characteristic declaration handle mismatch")
            props = declaration[0]
            uuid = uuid_text(declaration[3:])
            print("CHAR", handle, uuid, "props=0x%02x" % props)
            key = uuid.lower()
            if key in selected:
                raise ValueError("Duplicate characteristic UUID: %s" % uuid)
            selected[key] = (handle, props)
    return selected


def main():
    found = None
    for entry in Scanner().scan(5000):
        if entry.addr().lower() == TARGET_ADDR.lower():
            found = entry
            break
    if found is None:
        raise RuntimeError("Target not found")

    central = Peripheral()
    central.connect(found.addr(), addr_type=found.addr_type())
    print("CONNECTED")
    database = find_target(central)
    target = database.get(WRITE_UUID.lower()) if WRITE_UUID else None
    if target is None:
        print("Set WRITE_UUID to one of the printed characteristic UUIDs.")
        return
    handle, props = target
    notify_target = database.get(NOTIFY_UUID.lower()) if NOTIFY_UUID else None
    if NOTIFY_UUID and notify_target is None:
        raise ValueError("NOTIFY_UUID not discovered")

    if not ENABLE_WRITE:
        print("WRITE disabled. Review the target and set ENABLE_WRITE=True.")
        return
    if not (props & (PROP_WRITE if WITH_RESPONSE else PROP_WRITE_NO_RSP)):
        raise ValueError("Selected write mode not advertised by characteristic")
    if len(WRITE_DATA) > 20:
        raise ValueError("This firmware limits GATT writes to 20 bytes")

    if CCCD_HANDLE is None:
        print("Set CCCD_HANDLE from an external GATT descriptor discovery; WRITE not attempted.")
        return
    if notify_target is None or not (notify_target[1] & PROP_NOTIFY):
        raise ValueError("Selected TX characteristic does not advertise Notify")

    received = []

    def on_notify(value_handle, data):
        if value_handle == notify_target[0]:
            received.append(bytes(data))
            print("NOTIFY", value_handle, bytes(data))

    central.setNotificationHandler(on_notify)
    # Subscribe first; do not transmit if enabling notifications fails.
    central.writeHandle(CCCD_HANDLE, bytes((1, 0)), True)
    print("CCCD enabled:", CCCD_HANDLE)
    try:
        central.writeHandle(handle, WRITE_DATA, WITH_RESPONSE)
        print("WRITE sent:", WRITE_DATA, "with_response=", WITH_RESPONSE)
        time.sleep_ms(WAIT_NOTIFY_MS)
        print("LOOPBACK:", "PASS" if WRITE_DATA in received else "NO MATCH")
    finally:
        central.writeHandle(CCCD_HANDLE, bytes((0, 0)), True)
        print("CCCD disabled")


main()
