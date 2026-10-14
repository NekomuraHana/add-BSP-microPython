"""Generic BLE GATT UUID discovery on the ISP1807 (legacy ubluepy).

Works without pre-registering any vendor UUID. Reads ATT service and
characteristic declaration values using handles from discovery.
ATT read errors are reported, not guessed or silently reinterpreted.
"""

from ubluepy import Peripheral, Scanner

TARGET_ADDR = "d0:ef:3b:c9:9b:55"

def decode_uuid(raw):
    # Attribute values encode UUIDs little-endian.
    if len(raw) == 2:
        return "0x%04x" % int.from_bytes(raw, "little")
    if len(raw) != 16:
        raise ValueError("Unexpected UUID length: %d" % len(raw))
    h = "".join("%02x" % x for x in reversed(raw))
    return "%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])

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
        value = bytes(central.readHandle(start))
        # Primary service declaration (0x2800) holds a 2- or 16-byte UUID.
        name = decode_uuid(value)
    except Exception as exc:
        name = "<unavailable: %s>" % repr(exc)
    print("SERVICE", start, name)

    for characteristic in service.getCharacteristics():
        value_handle = characteristic.getHandle()
        # ATT characteristic declaration normally immediately precedes the value.
        # We validate the declaration's embedded value handle before trusting it.
        declaration_handle = value_handle - 1
        try:
            data = bytes(central.readHandle(declaration_handle))
            if len(data) not in (5, 19):
                raise ValueError("Invalid declaration length %d" % len(data))
            declared_handle = data[1] | (data[2] << 8)
            if declared_handle != value_handle:
                raise ValueError("Declaration value handle mismatch")
            uuid_text = decode_uuid(data[3:])
        except Exception as exc:
            uuid_text = "<unavailable: %s>" % repr(exc)
        print("  CHAR", value_handle, uuid_text)
