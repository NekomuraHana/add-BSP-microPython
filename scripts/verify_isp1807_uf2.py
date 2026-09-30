#!/usr/bin/env python3
"""Sanity-check the ISP1807 UF2 image produced by CI."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path

UF2_BLOCK_SIZE = 512
UF2_MAGIC_START0 = 0x0A324655
UF2_MAGIC_START1 = 0x9E5D5157
UF2_MAGIC_END = 0x0AB16F30
UF2_FLAG_FAMILY_ID_PRESENT = 0x00002000

NRF52840_FAMILY_ID = 0xADA52840
APP_START = 0x26000
APP_END = 0xED000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("uf2", type=Path)
    args = parser.parse_args()

    data = args.uf2.read_bytes()
    if not data or len(data) % UF2_BLOCK_SIZE:
        raise SystemExit("UF2 size is not a non-zero multiple of 512 bytes")

    block_count = len(data) // UF2_BLOCK_SIZE
    expected_total = None
    first_target = None
    max_end = 0

    for index in range(block_count):
        block = data[index * UF2_BLOCK_SIZE : (index + 1) * UF2_BLOCK_SIZE]
        (
            magic0,
            magic1,
            flags,
            target,
            payload_size,
            block_no,
            total_blocks,
            family_id,
        ) = struct.unpack_from("<IIIIIIII", block, 0)
        magic_end = struct.unpack_from("<I", block, 508)[0]

        if magic0 != UF2_MAGIC_START0 or magic1 != UF2_MAGIC_START1:
            raise SystemExit(f"block {index}: invalid UF2 start magic")
        if magic_end != UF2_MAGIC_END:
            raise SystemExit(f"block {index}: invalid UF2 end magic")
        if not (flags & UF2_FLAG_FAMILY_ID_PRESENT):
            raise SystemExit(f"block {index}: family ID flag is missing")
        if family_id != NRF52840_FAMILY_ID:
            raise SystemExit(
                f"block {index}: unexpected family ID 0x{family_id:08X}"
            )
        if block_no != index:
            raise SystemExit(
                f"block {index}: unexpected block number {block_no}"
            )

        if expected_total is None:
            expected_total = total_blocks
            first_target = target
        elif total_blocks != expected_total:
            raise SystemExit(f"block {index}: inconsistent total block count")

        if not (APP_START <= target < APP_END):
            raise SystemExit(
                f"block {index}: target 0x{target:08X} outside app region"
            )
        if target + payload_size > APP_END:
            raise SystemExit(
                f"block {index}: payload crosses app boundary at 0x{APP_END:08X}"
            )
        max_end = max(max_end, target + payload_size)

    if expected_total != block_count:
        raise SystemExit(
            f"UF2 header says {expected_total} blocks, file contains {block_count}"
        )
    if first_target != APP_START:
        raise SystemExit(
            f"first UF2 target is 0x{first_target:08X}, expected 0x{APP_START:08X}"
        )

    print(f"UF2 blocks    : {block_count}")
    print(f"family ID     : 0x{NRF52840_FAMILY_ID:08X}")
    print(f"first target  : 0x{first_target:08X}")
    print(f"highest end   : 0x{max_end:08X}")
    print("UF2 validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
