"""Generic GATT UUID extraction for the legacy nRF ubluepy Central port.

Copy this file to /lib/ble_gatt_uuid.py on the MicroPython device.
No vendor UUID registration is necessary.

ATT declaration attributes contain UUID bytes in little-endian order.
Only declaration reads are implemented; this is not a BLE protocol stack.
"""


def format_uuid(raw):
    """Return canonical UUID text for a 2- or 16-byte little-endian UUID."""
    if len(raw) == 2:
        return "0x%04x" % (raw[0] | (raw[1] << 8))
    if len(raw) != 16:
        raise ValueError("Expected a 2- or 16-byte UUID, got %d bytes" % len(raw))
    hex_text = "".join("%02x" % value for value in reversed(raw))
    return "%s-%s-%s-%s-%s" % (
        hex_text[:8], hex_text[8:12], hex_text[12:16],
        hex_text[16:20], hex_text[20:],
    )


def service_uuid(central, service):
    """Read UUID from the Primary Service Declaration attribute."""
    raw = bytes(central.readHandle(service.getStartHandle()))
    return format_uuid(raw)


def characteristic_uuid(central, characteristic):
    """Read UUID from Characteristic Declaration and check its value handle."""
    raw = bytes(central.readHandle(characteristic.getDeclarationHandle()))
    if len(raw) not in (5, 19):
        raise ValueError("Invalid characteristic declaration length: %d" % len(raw))
    value_handle = raw[1] | (raw[2] << 8)
    if value_handle != characteristic.getHandle():
        raise ValueError("Characteristic value handle mismatch")
    return format_uuid(raw[3:])
