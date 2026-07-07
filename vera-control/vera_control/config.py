"""Locations the control layer needs: the slicer binary, the VORMETRA vendor
profiles, and a scratch datadir for the engine's own state.

Everything is overridable via environment variables so the same code works
against the official prebuilt binary (prototyping) and our own fork build
(``build/OrcaSlicer/orca-slicer.exe`` once VOR-6 finishes) without edits.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../vormetra-slice


def _env_path(name: str, default: Path) -> Path:
    value = os.environ.get(name)
    return Path(value) if value else default


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

FILAMENT_CHOICES = {
    "petg": VORMETRA_PROFILES_DIR / "filament" / "VORMETRA PETG Pellet.json",
    "pla": VORMETRA_PROFILES_DIR / "filament" / "VORMETRA PLA Pellet.json",
}

# From TECHNICAL_REQUIREMENTS.md / g1000-profile-spec.md in the main knowledge-base
# repo -- kept here too so validate() doesn't need the slicer to reject an
# obviously-oversized model.
MACHINE_LIMITS = {
    "bed_x_mm": 1000.0,
    "bed_y_mm": 1000.0,
    "bed_z_mm": 1000.0,
    "nozzle_diameter_mm": 5.0,
}
