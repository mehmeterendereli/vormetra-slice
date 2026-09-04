"""Locations the control layer needs: the slicer binary, the VORMETRA vendor
profiles, and a scratch datadir for the engine's own state.

Everything is overridable via environment variables so the same code works
against an official prebuilt binary or a reviewed local source build without
source edits.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../vormetra-slice


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value) if value else default


def _optional_env_path(name: str) -> Path | None:
    value = os.environ.get(name)
    return Path(value) if value else None


SLICER_BIN = _env_path(
    "VERA_SLICER_BIN",
    REPO_ROOT / "build" / "src" / "Release" / "orca-slicer.exe",
)

PROFILES_DIR = _env_path("VERA_PROFILES_DIR", REPO_ROOT / "resources" / "profiles")
VORMETRA_PROFILES_DIR = PROFILES_DIR / "VORMETRA"

DATA_DIR = _env_path("VERA_DATA_DIR", REPO_ROOT / "vera-control" / ".vera-datadir")

DEFAULT_MACHINE = VORMETRA_PROFILES_DIR / "machine" / "VORMETRA G1000 5.0 nozzle.json"
DEFAULT_PROCESS = VORMETRA_PROFILES_DIR / "process" / "2.00mm Standard.json"
DEFAULT_FILAMENT = VORMETRA_PROFILES_DIR / "filament" / "VORMETRA PETG Pellet.json"

# Optional read-only LinuxCNC conversion integration. There is intentionally no
# machine-specific default: callers must opt in with VERA_FGF_POST_PATH.
FGF_POST_PATH = _optional_env_path("VERA_FGF_POST_PATH")

FILAMENT_CHOICES = {
    "petg": VORMETRA_PROFILES_DIR / "filament" / "VORMETRA PETG Pellet.json",
    "pla": VORMETRA_PROFILES_DIR / "filament" / "VORMETRA PLA Pellet.json",
}

# Software envelope used by validate_model() before the slicer is invoked.
MACHINE_LIMITS = {
    "bed_x_mm": 1000.0,
    "bed_y_mm": 1000.0,
    "bed_z_mm": 1000.0,
    "nozzle_diameter_mm": 5.0,
}
