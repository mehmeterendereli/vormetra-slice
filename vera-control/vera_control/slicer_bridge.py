"""Thin wrapper around the OrcaSlicer-derived CLI so any AI agent (or the
embedded Vera panel) can slice a model without knowing the exact, somewhat
unforgiving CLI incantation.

The invocation and the profile-authoring gotchas it works around are
documented in ``resources/profiles/VORMETRA/README.md`` -- notably: critical
machine fields (printable_area, gcode_flavor, pellet_modded_printer,
machine_start_gcode) must live in the *leaf* (instantiation:true) machine
JSON, not just its ``common`` parent, or the CLI's direct-file-load path
silently ignores them and shrinks the bed to the model's own bounding box.
"""
from __future__ import annotations

import os
import re
import struct
import subprocess
import threading
import uuid
import zipfile
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from . import config
from .stl_utils import read_bounding_box


class VeraSlicerError(RuntimeError):
    """Raised when the underlying slicer binary fails or is misconfigured."""


class VeraSlicerBusy(VeraSlicerError):
    """Raised when a slice is already running and a second job would queue up."""


_SLICE_THREAD_LOCK = threading.Lock()
_SLICE_LOCK_FD: Optional[int] = None


@dataclass
class SliceResult:
    gcode_3mf_path: Path
    gcode_text: str
    stats: dict = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""


def _require_binary() -> Path:
    if not config.SLICER_BIN.exists():
        raise VeraSlicerError(
            f"slicer binary not found at {config.SLICER_BIN}. Set VERA_SLICER_BIN "
            "to a built or downloaded orca-slicer.exe (see vera-control/README.md)."
        )
    return config.SLICER_BIN


def is_slice_running() -> bool:
    return _SLICE_THREAD_LOCK.locked() or _slice_lock_is_active()


def _slice_lock_path() -> Path:
    return config.DATA_DIR / "slice.lock"


def _read_slice_lock(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="ascii").splitlines()
    except OSError:
        return {}
    lock_info = {}
    for line in lines:
        key, _, value = line.partition("=")
        if key and value:
            lock_info[key] = value
    return lock_info


def _pid_is_running(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def _slice_lock_is_active() -> bool:
    lock_path = _slice_lock_path()
    if not lock_path.exists():
        return False

    lock_info = _read_slice_lock(lock_path)
    if lock_info.get("platform") == os.name:
        try:
            pid = int(lock_info.get("pid", ""))
        except ValueError:
            return True
        if not _pid_is_running(pid):
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass
            return False

    return True


def _acquire_slice_slot() -> bool:
    global _SLICE_LOCK_FD
    if not _SLICE_THREAD_LOCK.acquire(blocking=False):
        return False

    try:
        lock_path = _slice_lock_path()
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        _slice_lock_is_active()
        _SLICE_LOCK_FD = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        payload = f"pid={os.getpid()}\nplatform={os.name}\n"
        os.write(_SLICE_LOCK_FD, payload.encode("ascii"))
        return True
    except FileExistsError:
        _SLICE_THREAD_LOCK.release()
        return False
    except Exception:
        _SLICE_THREAD_LOCK.release()
        raise


def _release_slice_slot() -> None:
    global _SLICE_LOCK_FD
    fd = _SLICE_LOCK_FD
    _SLICE_LOCK_FD = None
    if fd is not None:
        os.close(fd)
    try:
        _slice_lock_path().unlink()
    except FileNotFoundError:
        pass
    finally:
        _SLICE_THREAD_LOCK.release()


def _slicer_creationflags() -> int:
    if not hasattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS"):
        return 0
    flags = subprocess.BELOW_NORMAL_PRIORITY_CLASS
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        flags |= subprocess.CREATE_NO_WINDOW
    return flags


def validate_model(stl_path: str, machine_limits: Optional[dict] = None) -> dict:
    """Bounding-box sanity check against the G1000 build volume. Cheap, and
    catches an obviously-oversized model before spending time on a real slice."""
    limits = machine_limits or config.MACHINE_LIMITS
    bbox = read_bounding_box(stl_path)
    problems = []
    if bbox.size_x > limits["bed_x_mm"]:
        problems.append(f"X boyutu {bbox.size_x:.1f}mm > bed {limits['bed_x_mm']}mm")
    if bbox.size_y > limits["bed_y_mm"]:
        problems.append(f"Y boyutu {bbox.size_y:.1f}mm > bed {limits['bed_y_mm']}mm")
    if bbox.size_z > limits["bed_z_mm"]:
        problems.append(f"Z boyutu {bbox.size_z:.1f}mm > bed {limits['bed_z_mm']}mm")
    return {
        "fits": not problems,
        "problems": problems,
        "bounding_box_mm": {
            "x": round(bbox.size_x, 2),
            "y": round(bbox.size_y, 2),
            "z": round(bbox.size_z, 2),
        },
    }


def list_filaments() -> list[str]:
    return sorted(config.FILAMENT_CHOICES.keys())


def slice_model(
    stl_path: str,
    filament: str = "petg",
    machine: Optional[Path] = None,
    process: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    datadir: Optional[Path] = None,
    extra_args: Optional[list[str]] = None,
) -> SliceResult:
    """Slice ``stl_path`` with the given VORMETRA G1000 profile and return the
    resulting G-code (plus the stats OrcaSlicer prints in the G-code header).

    Raises VeraSlicerError with the real stdout/stderr on any failure --
    never returns a half-successful result silently.
    """
    machine = machine or config.DEFAULT_MACHINE
    process = process or config.DEFAULT_PROCESS
    filament_path = config.FILAMENT_CHOICES.get(filament.lower())
    if filament_path is None:
        raise VeraSlicerError(
            f"unknown filament '{filament}', choices: {list_filaments()}"
        )

    stl_path = Path(stl_path)
    if not stl_path.exists():
        raise VeraSlicerError(f"model not found: {stl_path}")

    if not _acquire_slice_slot():
        raise VeraSlicerBusy(
            "another slice is already running; refusing to queue another slicer job"
        )

    try:
        binary = _require_binary()

        run_id = uuid.uuid4().hex[:8]
        output_dir = Path(output_dir) if output_dir else config.DATA_DIR / "out" / run_id
        output_dir.mkdir(parents=True, exist_ok=True)
        run_datadir = Path(datadir) if datadir else config.DATA_DIR / "runs" / run_id
        run_datadir.mkdir(parents=True, exist_ok=True)

        out_3mf = output_dir / f"{stl_path.stem}.gcode.3mf"

        cmd = [
            str(binary),
            "--datadir", str(run_datadir),
            "--load-settings", f"{machine};{process}",
            "--load-filaments", str(filament_path),
            "--slice", "0",
            "--export-3mf", str(out_3mf),
            *(extra_args or []),
            str(stl_path),
        ]

        run_kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": 300,
            "cwd": binary.parent,
        }
        creationflags = _slicer_creationflags()
        if creationflags:
            run_kwargs["creationflags"] = creationflags

        # The engine resolves its own bundled resources (fonts, localization, ...)
        # relative to CWD, not to the binary's own path -- so we must run with cwd
        # set to the binary's directory or it fails with an opaque, low-detail error.
        proc = subprocess.run(cmd, **run_kwargs)
        if proc.returncode != 0 or not out_3mf.exists():
            raise VeraSlicerError(
                "slice failed (exit "
                f"{proc.returncode}):\n{proc.stdout}\n{proc.stderr}"
            )
    finally:
        _release_slice_slot()

    _ensure_archive_thumbnails(out_3mf)
    gcode_text = _extract_gcode(out_3mf)
    stats = _parse_header(gcode_text)
    return SliceResult(
        gcode_3mf_path=out_3mf,
        gcode_text=gcode_text,
        stats=stats,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _placeholder_png(size: int = 64) -> bytes:
    """Return a valid neutral RGBA PNG for headless CLI exports.

    OrcaSlicer writes thumbnail relationships into a G-code 3MF even when
    OpenGL is unavailable and no thumbnail files were rendered. Supplying a
    small placeholder keeps the archive internally consistent and prevents
    the GUI importer from logging missing-file errors.
    """

    def chunk(kind: bytes, data: bytes) -> bytes:
        payload = kind + data
        return (
            struct.pack(">I", len(data))
            + payload
            + struct.pack(">I", zlib.crc32(payload) & 0xFFFFFFFF)
        )

    pixel = b"\x25\x2b\x36\xff"
    rows = b"".join(b"\x00" + pixel * size for _ in range(size))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows))
        + chunk(b"IEND", b"")
    )


def _ensure_archive_thumbnails(gcode_3mf_path: Path) -> None:
    """Fill thumbnail targets that OrcaSlicer cannot render headlessly."""
    required = ("Metadata/plate_1.png", "Metadata/plate_1_small.png")
    try:
        with zipfile.ZipFile(
            gcode_3mf_path, mode="a", compression=zipfile.ZIP_DEFLATED
        ) as zf:
            existing = set(zf.namelist())
            placeholder = _placeholder_png()
            for name in required:
                if name not in existing:
                    zf.writestr(name, placeholder)
    except (OSError, zipfile.BadZipFile) as exc:
        raise VeraSlicerError(
            f"could not finalize thumbnails in {gcode_3mf_path}: {exc}"
        ) from exc


def _extract_gcode(gcode_3mf_path: Path) -> str:
    with zipfile.ZipFile(gcode_3mf_path) as zf:
        gcode_names = [n for n in zf.namelist() if n.endswith(".gcode")]
        if not gcode_names:
            raise VeraSlicerError(f"no .gcode found inside {gcode_3mf_path}")
        with zf.open(gcode_names[0]) as f:
            return f.read().decode("utf-8", errors="replace")


_HEADER_PATTERNS = {
    "total_layers": re.compile(r"total layer number:\s*(\d+)"),
    "filament_density": re.compile(r"filament_density:\s*([\d.]+)"),
    "filament_diameter": re.compile(r"filament_diameter:\s*([\d.]+)"),
    "max_z_height_mm": re.compile(r"max_z_height:\s*([\d.]+)"),
}


def _parse_header(gcode_text: str) -> dict:
    header = gcode_text.split("; EXECUTABLE_BLOCK_START", 1)[0]
    stats: dict = {}
    for key, pattern in _HEADER_PATTERNS.items():
        m = pattern.search(header)
        if m:
            value = m.group(1)
            stats[key] = int(value) if key == "total_layers" else float(value)
    bed_shape_match = re.search(r"bed_shape\s*=\s*([\d.x,\-]+)", gcode_text)
    if bed_shape_match:
        stats["bed_shape"] = bed_shape_match.group(1)
    return stats
