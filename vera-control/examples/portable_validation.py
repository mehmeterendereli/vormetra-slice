"""Run a portable VORMETRA model-validation demo.

Without an argument, this script creates a closed 200 x 200 x 100 mm binary
STL in a temporary directory. Pass an STL path to inspect your own model.
Neither mode invokes the slicer binary. Use ``--proof-svg`` to save a compact,
accessible visual summary generated from the same JSON report.
"""
from __future__ import annotations

import argparse
import html
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


def _proof_svg(report: dict) -> str:
    """Render a self-contained summary without external fonts or resources."""
    box = report["validation"]["bounding_box_mm"]
    limits = report["machine_limits_mm"]
    fits = report["validation"]["fits"]
    result = "FITS" if fits else "CHECK"
    result_color = "#3fb950" if fits else "#d29922"
    model_label = (
        "GENERATED FIXTURE"
        if report["model"]["source"] == "generated_fixture"
        else "PROVIDED STL"
    )
    result_detail = (
        "0 envelope problems"
        if fits
        else f'{len(report["validation"]["problems"])} envelope problem(s)'
    )

    def clean(value: object) -> str:
        return html.escape(str(value), quote=True)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="440" viewBox="0 0 960 440" role="img" aria-labelledby="title description">
  <title id="title">VORMETRA portable validation result: {result}</title>
  <desc id="description">The inspected {clean(box['x'])} by {clean(box['y'])} by {clean(box['z'])} millimetre STL returns {result} against the configured {clean(limits['bed_x_mm'])} by {clean(limits['bed_y_mm'])} by {clean(limits['bed_z_mm'])} millimetre G1000 software envelope. This is bounding-box validation only.</desc>
  <rect width="960" height="440" rx="20" fill="#0d1117"/>
  <rect x="1" y="1" width="958" height="438" rx="19" fill="none" stroke="#30363d" stroke-width="2"/>
  <rect x="32" y="32" width="896" height="56" rx="10" fill="#161b22"/>
  <circle cx="60" cy="60" r="7" fill="#bd4724"/>
  <text x="82" y="68" fill="#f0f6fc" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="22" font-weight="700">VORMETRA / PORTABLE VALIDATION</text>
  <text x="52" y="132" fill="#8c959f" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">{model_label}</text>
  <text x="52" y="164" fill="#f0f6fc" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="24" font-weight="700">{clean(box['x'])} x {clean(box['y'])} x {clean(box['z'])} mm</text>
  <text x="52" y="208" fill="#8c959f" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">CONFIGURED G1000 ENVELOPE</text>
  <text x="52" y="240" fill="#f0f6fc" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="24" font-weight="700">{clean(limits['bed_x_mm'])} x {clean(limits['bed_y_mm'])} x {clean(limits['bed_z_mm'])} mm</text>
  <text x="52" y="278" fill="#8c959f" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="16">nozzle {clean(limits['nozzle_diameter_mm'])} mm · filaments {clean(' / '.join(report['available_filaments']))}</text>
  <rect x="616" y="122" width="280" height="172" rx="14" fill="#161b22" stroke="#30363d" stroke-width="2"/>
  <text x="644" y="158" fill="#8c959f" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">RESULT</text>
  <circle cx="656" cy="204" r="12" fill="{result_color}"/>
  <text x="682" y="214" fill="#f0f6fc" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="34" font-weight="700">{result}</text>
  <text x="644" y="258" fill="#b1bac4" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="16">{clean(result_detail)}</text>
  <line x1="52" y1="326" x2="908" y2="326" stroke="#30363d" stroke-width="2"/>
  <text x="52" y="364" fill="#f0f6fc" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="16" font-weight="700">EVIDENCE BOUNDARY</text>
  <text x="52" y="394" fill="#b1bac4" font-family="ui-monospace, SFMono-Regular, Consolas, monospace" font-size="15">Portable bounding-box validation only. No slicer binary or physical machine was exercised.</text>
</svg>
"""


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
    parser.add_argument(
        "--proof-svg",
        type=Path,
        metavar="PATH",
        help="write an accessible SVG summary generated from the validation report",
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

    if args.proof_svg is not None:
        proof_path = args.proof_svg.expanduser().resolve()
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(_proof_svg(report), encoding="utf-8")

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["validation"]["fits"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
