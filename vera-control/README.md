# vera-control

AI-controllable control layer for VORMETRA Slice. Wraps the slicer engine's
CLI so that Claude Code, other AI agents, and the embedded "Vera" assistant
can drive it programmatically instead of only through the desktop GUI.

**License:** MIT (see `LICENSE` in this directory) -- separate from the
engine's AGPLv3 (root `LICENSE.txt`). This is a standalone program that talks
to the engine over a CLI/subprocess boundary, not a linked derivative of it,
so it isn't required to be AGPL; VORMETRA chose to open it under MIT anyway
for community contribution (founder decision, 2026-07-07 -- see the main
knowledge-base repo's `DECISIONS.md` ADR-047).

Three ways in, same underlying `vera_control.slicer_bridge`:

- **HTTP API** (`vera_control/api.py`, stdlib only, no new dependency) --
  `/health`, `/profiles`, `/validate`, `/slice`. Also serves the Vera
  Console web UI at `/`.
- **MCP server** (`vera_control/mcp_server.py`, needs the `mcp` package) --
  `list_filaments`, `get_machine_limits`, `validate_model`, `slice_stl` as
  native tools for any MCP-compatible AI client (Claude Code included).
- **Direct import** -- `from vera_control import slicer_bridge` and call
  `slicer_bridge.slice_model(...)` yourself.

## Setup

```
cd vera-control
python -m pip install -e ".[dev]"        # core + pytest
python -m pip install -e ".[mcp]"        # only if you need the MCP server
```

Point the layer at a real engine binary (our own build once
`build/src/Release/orca-slicer.exe` exists, or the official portable build
for prototyping):

```
set VERA_SLICER_BIN=C:\path\to\orca-slicer.exe
set VERA_PROFILES_DIR=C:\path\to\resources\profiles   # must contain VORMETRA/
```

## Run

```
python run_dev.py                 # HTTP API + Vera Console on :8765
python -m vera_control.mcp_server # MCP server (stdio transport)
```

## Test

```
python -m pytest -q
```

The real-engine integration test (`test_slice_model_real_binary_end_to_end`)
auto-skips if `VERA_SLICER_BIN` isn't set to an existing file -- everything
else (bridge logic, HTTP API, STL bounding-box math) runs with no engine
required.

## The CLI gotchas this layer exists to hide

`slicer_bridge.py`'s docstring and `resources/profiles/VORMETRA/README.md`
both document four real bugs found and fixed while building this (Marlin
G92-E0 validation, the CLI's direct-file-load path silently ignoring
inherited machine fields and shrinking the bed to the model's own bounding
box, `pellet_flow_coefficient` not auto-converting to `filament_diameter`
outside the GUI, and undefined custom placeholder variables). If slicing
starts failing again after an engine upgrade, check there first before
assuming the profile JSON is wrong.
