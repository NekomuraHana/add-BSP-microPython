"""ISP1807 Central GATT Read/Write/optional Notify hardware test.

Use only against a test peripheral whose writable characteristic is known.
Set TARGET_ADDR and TARGET_UUID, and explicitly opt in to writing.
CCCD_HANDLE must come from a GATT descriptor inspector, not handle + 1.
"""
import time
from ubluepy import Peripheral, Scanner

TARGET_ADDR = "d0:ef:3b:c9:9b:55"
TARGET_UUID = None  # e.g. "0000abcd-1234-5678-9abc-0123456789ab"
WRITE_DATA = b"isp1807-test"
ENABLE_WRITE = False
WITH_RESPONSE = True
CCCD_HANDLE = None  # Optional verified descriptor handle (UUID 0x2902)
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
    selected = None
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
            if TARGET_UUID is not None and uuid.lower() == TARGET_UUID.lower():
                if selected is not None:
                    raise ValueError("UUID matches multiple characteristics")
                selected = (handle, props)
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
    target = find_target(central)
    if target is None:
        print("Set TARGET_UUID to one of the printed characteristic UUIDs.")
        return
    handle, props = target

    if props & PROP_READ:
        try:
            print("READ before:", bytes(central.readHandle(handle)))
        except Exception as exc:
            print("READ before failed:", repr(exc))
    else:
        print("READ skipped (property not advertised)")

    if not ENABLE_WRITE:
        print("WRITE disabled. Review the target and set ENABLE_WRITE=True.")
        return
    if not (props & (PROP_WRITE if WITH_RESPONSE else PROP_WRITE_NO_RSP)):
        raise ValueError("Selected write mode not advertised by characteristic")
    if len(WRITE_DATA) > 20:
        raise ValueError("This firmware limits GATT writes to 20 bytes")

    if CCCD_HANDLE is not None:
        if not (props & PROP_NOTIFY):
            raise ValueError("Characteristic does not advertise Notify")

        def on_notify(value_handle, data):
            print("NOTIFY", value_handle, bytes(data))

        central.setNotificationHandler(on_notify)
        central.writeHandle(CCCD_HANDLE, bytes((1, 0)), True)
        print("Notifications enabled using verified CCCD", CCCD_HANDLE)

    central.writeHandle(handle, WRITE_DATA, WITH_RESPONSE)
    print("WRITE sent:", WRITE_DATA, "with_response=", WITH_RESPONSE)

    if props & PROP_READ:
        try:
            print("READ after:", bytes(central.readHandle(handle)))
        except Exception as exc:
            print("READ after failed:", repr(exc))
    if CCCD_HANDLE is not None:
        time.sleep_ms(WAIT_NOTIFY_MS)
        # Best effort to disable notify; disconnect API is unavailable in this port.
        central.writeHandle(CCCD_HANDLE, bytes((0, 0)), True)
        print("Notifications disabled")


main()
