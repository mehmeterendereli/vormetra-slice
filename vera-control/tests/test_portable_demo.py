import json
import subprocess
import sys
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
