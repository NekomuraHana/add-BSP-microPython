#!/usr/bin/env python3
"""Sanity-check an ISP1807 MicroPython application image."""

from __future__ import annotations

import argparse
from pathlib import Path

APP_START = 0x26000
APP_END = 0xED000
RAM_START = 0x20000000
RAM_END = 0x20040000
MAX_APP_SIZE = APP_END - APP_START

USB_DESCRIPTOR_VID_PID_LE = bytes.fromhex("86 27 0d 92")
USB_MANUFACTURER = b"Switch Science, Inc."
USB_PRODUCT = b"SSCI ISP1807 Breakout"
USB_INTERFACE = b"MicroPython REPL"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("firmware_bin", type=Path)
    args = parser.parse_args()

    data = args.firmware_bin.read_bytes()
    if len(data) < 8:
        raise SystemExit("firmware.bin is too small to contain a vector table")
    if len(data) > MAX_APP_SIZE:
        raise SystemExit(
            f"firmware.bin is too large: {len(data)} > {MAX_APP_SIZE} bytes"
        )

    initial_sp = int.from_bytes(data[0:4], "little")
    reset_vector = int.from_bytes(data[4:8], "little")

    if not (RAM_START <= initial_sp <= RAM_END):
        raise SystemExit(f"invalid initial SP: 0x{initial_sp:08X}")
    if initial_sp & 0x3:
        raise SystemExit(f"initial SP is not word aligned: 0x{initial_sp:08X}")

    if not (reset_vector & 1):
        raise SystemExit(f"reset vector is not Thumb: 0x{reset_vector:08X}")

    reset_address = reset_vector & ~1
    if not (APP_START <= reset_address < APP_END):
        raise SystemExit(
            f"reset vector outside application region: 0x{reset_vector:08X}"
        )

    checks = {
        "USB VID/PID 2786:920D": USB_DESCRIPTOR_VID_PID_LE,
        "USB manufacturer": USB_MANUFACTURER,
        "USB product": USB_PRODUCT,
        "USB CDC interface": USB_INTERFACE,
    }

    missing = [name for name, value in checks.items() if value not in data]
    if missing:
        raise SystemExit("missing firmware markers: " + ", ".join(missing))

    print(f"firmware size : {len(data)} bytes")
    print(f"initial SP    : 0x{initial_sp:08X}")
    print(f"reset vector  : 0x{reset_vector:08X}")
    for name in checks:
        print(f"{name}: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
