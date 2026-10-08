"""Run a portable VORMETRA model-validation demo.

Without an argument, this script creates a closed 200 x 200 x 100 mm binary
STL in a temporary directory. Pass an STL path to inspect your own model.
Neither mode invokes the slicer binary or writes persistent output.
"""
from __future__ import annotations

import argparse
import json
import struct
import tempfile
from pathlib import Path
from typing import Sequence

from vera_control import config, slicer_bridge


def _write_cube_stl(path: Path, sx: float, sy: float, sz: float) -> None:
    corners = [
        (0, 0, 0),
        (sx, 0, 0),
        (sx, sy, 0),
        (0, sy, 0),
        (0, 0, sz),
        (sx, 0, sz),
        (sx, sy, sz),
        (0, sy, sz),
    ]
    triangles = [
        (0, 2, 1),
        (0, 3, 2),
        (4, 5, 6),
        (4, 6, 7),
        (0, 1, 5),
        (0, 5, 4),
        (3, 6, 2),
        (3, 7, 6),
        (0, 4, 7),
        (0, 7, 3),
        (1, 2, 6),
        (1, 6, 5),
    ]

    with path.open("wb") as output:
        output.write(b"VORMETRA portable validation fixture".ljust(80, b"\0"))
        output.write(struct.pack("<I", len(triangles)))
        for a, b, c in triangles:
            output.write(struct.pack("<3f", 0, 0, 0))
            for index in (a, b, c):
                output.write(struct.pack("<3f", *corners[index]))
            output.write(struct.pack("<H", 0))


def _report(stl_path: Path, source: str) -> dict:
    model = {"source": source}
    if source == "provided_file":
        model["path"] = str(stl_path)
    else:
        model["fixture_mm"] = {"x": 200, "y": 200, "z": 100}
        model["storage"] = "temporary_removed"

    return {
        "model": model,
        "available_filaments": slicer_bridge.list_filaments(),
        "machine_limits_mm": dict(config.MACHINE_LIMITS),
        "validation": slicer_bridge.validate_model(str(stl_path)),
        "evidence_boundary": (
            "Portable bounding-box validation only; no slicer binary or "
            "physical machine was exercised."
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect an STL against the VORMETRA G1000 software envelope."
    )
    parser.add_argument(
        "stl",
        nargs="?",
        type=Path,
        help="STL to inspect; omit to use a temporary 200 x 200 x 100 mm fixture.",
    )
    args = parser.parse_args(argv)

    if args.stl is not None:
        stl_path = args.stl.expanduser().resolve()
        if not stl_path.is_file():
            parser.error(f"STL file not found: {stl_path}")
        report = _report(stl_path, "provided_file")
    else:
        with tempfile.TemporaryDirectory(prefix="vormetra-demo-") as directory:
            stl_path = Path(directory) / "g1000-fixture.stl"
            _write_cube_stl(stl_path, 200, 200, 100)
            report = _report(stl_path, "generated_fixture")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["validation"]["fits"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
