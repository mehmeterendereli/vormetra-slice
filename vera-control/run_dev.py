"""Start the local Vera Console and HTTP API.

Runtime paths are configured only through environment variables or the
repository-relative defaults in :mod:`vera_control.config`.
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vera_control import api  # noqa: E402

if __name__ == "__main__":
    api.serve(
        host=os.environ.get("VERA_HOST", "127.0.0.1"),
        port=int(os.environ.get("VERA_PORT", "8765")),
    )
