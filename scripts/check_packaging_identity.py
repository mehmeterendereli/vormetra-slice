#!/usr/bin/env python3
"""Validate that the configured application key has Linux package assets."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "version.inc"
KEY_PATTERN = re.compile(r'set\(SLIC3R_APP_KEY\s+"([^"]+)"\)')


def main() -> int:
    match = KEY_PATTERN.search(VERSION_FILE.read_text(encoding="utf-8"))
    if match is None:
        print("version.inc does not define SLIC3R_APP_KEY", file=sys.stderr)
        return 1

    app_key = match.group(1)
    required = (
        ROOT / "resources" / "images" / f"{app_key}_192px.png",
        ROOT / "scripts" / "flatpak" / f"com.orcaslicer.{app_key}.metainfo.xml",
    )
    missing = [path.relative_to(ROOT) for path in required if not path.is_file()]
    if missing:
        print(
            f"SLIC3R_APP_KEY {app_key!r} has no complete Linux packaging identity:",
            file=sys.stderr,
        )
        for path in missing:
            print(f"- missing {path.as_posix()}", file=sys.stderr)
        return 1

    print(f"Linux packaging identity is complete for {app_key}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
