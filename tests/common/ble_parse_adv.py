"""Decode BLE legacy AD structures returned by ubluepy ScanEntry.getScanData()."""


def _uuid(raw):
    if len(raw) == 2:
        return "0x%04x" % (raw[0] | (raw[1] << 8))
    if len(raw) == 16:
        h = "".join("%02x" % b for b in reversed(raw))
        return "%s-%s-%s-%s-%s" % (h[:8], h[8:12], h[12:16], h[16:20], h[20:])
    return None


def advertising_info(entry):
    name = None
    services = []
    for ad_type, description, value in entry.getScanData():
        data = bytes(value)
        if ad_type in (0x08, 0x09):
            # Complete name takes precedence over shortened name.
            if ad_type == 0x09 or name is None:
                try:
                    name = data.decode("utf-8")
                except UnicodeError:
                    name = repr(data)
        elif ad_type in (0x02, 0x03, 0x06, 0x07):
            size = 2 if ad_type in (0x02, 0x03) else 16
            for pos in range(0, len(data) - size + 1, size):
                value_uuid = _uuid(data[pos:pos + size])
                if value_uuid is not None and value_uuid not in services:
                    services.append(value_uuid)
    return name, services
