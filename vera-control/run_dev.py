"""Dev-server entry point: points the control layer at the official
prototype binary until the custom fork build (see VOR-6 / DECISIONS.md
ADR-043) finishes, then serves the Vera Console + HTTP API on :8765.
"""
import os
import sys
from pathlib import Path

os.environ.setdefault(
    "VERA_SLICER_BIN",
    r"C:\Users\pc\Desktop\vormetra-slice-prototype\extracted\orca-slicer.exe",
)
os.environ.setdefault(
    "VERA_PROFILES_DIR",
    r"C:\Users\pc\Desktop\vormetra-slice-prototype\extracted\resources\profiles",
)

sys.path.insert(0, str(Path(__file__).parent))

from vera_control import api  # noqa: E402

if __name__ == "__main__":
    api.serve()
