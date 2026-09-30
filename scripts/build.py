#!/usr/bin/env python3
"""Build supported MicroPython BSP targets."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MICROPYTHON = ROOT / "micropython"
BOARDS_ROOT = ROOT / "boards"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=cwd, check=True)


def find_board(board_id: str) -> tuple[Path, dict]:
    matches = list(BOARDS_ROOT.glob(f"*/{board_id}/board.toml"))
    if not matches:
        raise SystemExit(f"Unknown board: {board_id}")
    if len(matches) != 1:
        raise SystemExit(f"Ambiguous board id: {board_id}")

    board_dir = matches[0].parent
    with matches[0].open("rb") as fp:
        config = tomllib.load(fp)
    return board_dir, config


def ensure_micropython() -> None:
    if not (MICROPYTHON / "py").is_dir():
        raise SystemExit(
            "MicroPython submodule is missing. Run: "
            "git submodule update --init"
        )


def stage_nrf_board(board_dir: Path, board_name: str) -> Path:
    """Copy BSP build assets into the upstream nRF board directory."""
    target = MICROPYTHON / "ports" / "nrf" / "boards" / board_name
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)

    ignored = {"board.toml", "README.md"}
    for src in board_dir.iterdir():
        if src.name in ignored:
            continue
        dst = target / src.name
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    for name in ("mpconfigboard.h", "mpconfigboard.mk", "pins.csv"):
        if not (target / name).is_file():
            raise SystemExit(f"Missing staged BSP file: {target / name}")

    return target


def build_micropython_nrf(board_dir: Path, config: dict, jobs: int) -> None:
    board_name = config["micropython_board"]
    softdevice = config.get("softdevice", "")
    softdevice_package = config.get("softdevice_package", "")

    stage_nrf_board(board_dir, board_name)

    run(["make", f"-j{jobs}", "-C", str(MICROPYTHON / "mpy-cross")])
    run(["make", f"-j{jobs}", "-C", str(MICROPYTHON / "ports" / "nrf"), "submodules"])

    if softdevice:
        if not softdevice_package:
            raise SystemExit("softdevice_package is required when softdevice is set")
        run([
            "bash",
            str(MICROPYTHON / "ports" / "nrf" / "drivers" / "bluetooth" / "download_ble_stack.sh"),
            softdevice_package,
        ])

    cmd = [
        "make",
        f"-j{jobs}",
        "-C",
        str(MICROPYTHON / "ports" / "nrf"),
        f"BOARD={board_name}",
    ]
    if softdevice:
        cmd.append(f"SD={softdevice}")
    run(cmd)

    suffix = f"-{softdevice.lower()}" if softdevice else ""
    build_dir = MICROPYTHON / "ports" / "nrf" / f"build-{board_name}{suffix}"

    print("\nBuild complete:")
    for ext in ("hex", "bin", "elf"):
        artifact = build_dir / f"firmware.{ext}"
        if artifact.exists():
            print(f"  {artifact.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("board", help="board id, for example: isp1807")
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=max(1, os.cpu_count() or 1),
        help="parallel make jobs",
    )
    args = parser.parse_args()

    board_dir, config = find_board(args.board)
    ensure_micropython()

    backend = config.get("backend")
    if backend == "micropython-nrf":
        build_micropython_nrf(board_dir, config, args.jobs)
    else:
        raise SystemExit(f"Unsupported backend: {backend}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
