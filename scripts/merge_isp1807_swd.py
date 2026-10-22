#!/usr/bin/env python3
"""Build and verify a one-shot SWD HEX containing S140/MBR and MicroPython.

Uses Intel HEX address records, retaining the SoftDevice vector table at 0x0.
Does not include an Adafruit bootloader, DFU settings, or UICR.
"""
import argparse
from pathlib import Path

from intelhex import IntelHex

FLASH_END = 0x100000
APP_START = 0x26000
APP_END = FLASH_END
RAM_START = 0x20000000
RAM_END = 0x20040000


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("softdevice", type=Path)
    parser.add_argument("application", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    sd = IntelHex(str(args.softdevice))
    app = IntelHex(str(args.application))
    if not sd.addresses() or not app.addresses():
        raise SystemExit("empty SoftDevice or application image")

    def flash_addresses(image, description):
        addresses = image.addresses()
        if any(addr < 0 or addr >= FLASH_END for addr in addresses):
            raise SystemExit(f"{description} contains addresses outside flash")
        return set(addresses)

    sd_addrs = flash_addresses(sd, "SoftDevice")
    app_addrs = flash_addresses(app, "application")
    if 0 not in sd_addrs or 4 not in sd_addrs:
        raise SystemExit("SoftDevice vector table is missing at 0x000000")
    if any(addr >= APP_START for addr in sd_addrs):
        raise SystemExit("SoftDevice overlaps the application area")
    if min(app_addrs) != APP_START:
        raise SystemExit(f"application must start at 0x{APP_START:06X}")
    if sd_addrs & app_addrs:
        raise SystemExit("SoftDevice and application overlap")
    if max(app_addrs) >= APP_END:
        raise SystemExit("application exceeds physical flash")

    sp = int.from_bytes(bytes(app[APP_START + i] for i in range(4)), "little")
    rv = int.from_bytes(bytes(app[APP_START + 4 + i] for i in range(4)), "little")
    if not (RAM_START <= sp <= RAM_END) or sp % 4:
        raise SystemExit(f"invalid application stack pointer 0x{sp:08X}")
    if not (rv & 1) or not (APP_START <= (rv & ~1) < APP_END):
        raise SystemExit(f"invalid application reset vector 0x{rv:08X}")

    merged = IntelHex()
    merged.merge(sd, overlap="error")
    merged.merge(app, overlap="error")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    merged.write_hex_file(str(args.output))

    # Verify the produced artifact against both original inputs.
    check = IntelHex(str(args.output))
    if len(check.addresses()) != len(sd_addrs) + len(app_addrs):
        raise SystemExit("merged HEX changed the address count")
    for source in (sd, app):
        if any(check[addr] != source[addr] for addr in source.addresses()):
            raise SystemExit("merged HEX differs from source")
    print(f"Verified standalone SWD image: {args.output}")
    print(f"S140: 0x{min(sd_addrs):06X}-0x{max(sd_addrs):06X}")
    print(f"Application: 0x{min(app_addrs):06X}-0x{max(app_addrs):06X}")


if __name__ == "__main__":
    main()
