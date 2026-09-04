#!/usr/bin/env python3
"""Reject upstream publishing credentials and release actions in fork CI."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "build_all.yml",
    ROOT / ".github" / "workflows" / "build_check_cache.yml",
    ROOT / ".github" / "workflows" / "build_deps.yml",
    ROOT / ".github" / "workflows" / "build_orca.yml",
)
FORBIDDEN = (
    "WebFreak001/deploy-nightly",
    "rickstaa/action-create-tag",
    "uploads.github.com/repos/OrcaSlicer/OrcaSlicer/releases",
    "force_push_tag:",
    "ORCA_UPDATER_SIG_KEY",
    "BUILD_CERTIFICATE_BASE64",
    "APPLE_DEV_ACCOUNT",
    "secrets: inherit",
    "refs/heads/release/",
    "belt-printer",
)


def main() -> int:
    findings: list[str] = []
    for workflow in WORKFLOWS:
        content = workflow.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            if token in content:
                findings.append(f"{workflow.relative_to(ROOT).as_posix()}: {token}")

    if findings:
        print("Fork build workflows still contain upstream publishing capability:", file=sys.stderr)
        for finding in findings:
            print(f"- {finding}", file=sys.stderr)
        return 1

    print("Fork build workflows contain no upstream publishing capability.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
