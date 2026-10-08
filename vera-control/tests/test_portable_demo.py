import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def test_portable_demo_runs_without_slicer_binary():
    control_root = Path(__file__).resolve().parents[1]
    demo = control_root / "examples" / "portable_validation.py"

    completed = subprocess.run(
        [sys.executable, str(demo)],
        cwd=control_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    assert report["model"] == {
        "fixture_mm": {"x": 200, "y": 200, "z": 100},
        "source": "generated_fixture",
        "storage": "temporary_removed",
    }
    assert report["available_filaments"] == ["petg", "pla"]
    assert report["validation"] == {
        "bounding_box_mm": {"x": 200.0, "y": 200.0, "z": 100.0},
        "fits": True,
        "problems": [],
    }
    assert "no slicer binary" in report["evidence_boundary"]


def test_portable_demo_proof_matches_report(tmp_path):
    control_root = Path(__file__).resolve().parents[1]
    demo = control_root / "examples" / "portable_validation.py"
    proof = tmp_path / "portable-validation-proof.svg"

    completed = subprocess.run(
        [sys.executable, str(demo), "--proof-svg", str(proof)],
        cwd=control_root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads(completed.stdout)
    root = ET.parse(proof).getroot()
    rendered_text = " ".join("".join(root.itertext()).split())

    box = report["validation"]["bounding_box_mm"]
    limits = report["machine_limits_mm"]
    assert root.attrib["role"] == "img"
    assert "aria-labelledby" in root.attrib
    assert f"{box['x']} x {box['y']} x {box['z']} mm" in rendered_text
    assert (
        f"{limits['bed_x_mm']} x {limits['bed_y_mm']} x "
        f"{limits['bed_z_mm']} mm"
    ) in rendered_text
    assert "FITS" in rendered_text
    assert "No slicer binary or physical machine was exercised" in rendered_text
    assert "href" not in proof.read_text(encoding="utf-8")
    committed_proof = control_root.parent / "docs" / "portable-validation-proof.svg"
    assert proof.read_bytes() == committed_proof.read_bytes()
