# vera-control

`vera-control` is the MIT-licensed programmatic control layer for VORMETRA Slice. It wraps the OrcaSlicer-derived command-line interface once and exposes the same operations through HTTP, stdio MCP, and direct Python imports.

**Status:** the portable test suite and all three entry paths are runnable. A real slice still requires an explicitly configured slicer binary. Physical-machine behaviour is outside this package's evidence boundary.

## Install and verify

Python 3.10 or newer is required.

```bash
cd vera-control
python -m pip install -e ".[dev]"
python -m pip check
python -m pytest -q
```

The development extra includes the supported MCP 1.x dependency so CI verifies the stdio server with a real client handshake. The `mcp` extra remains available for runtime-only installations:

```bash
python -m pip install -e ".[mcp]"
```

## Configuration

Runtime paths are environment variables, not source-code defaults.

| Variable | Purpose | Default |
|---|---|---|
| `VERA_SLICER_BIN` | OrcaSlicer-compatible executable | Repository `build/src/Release/orca-slicer.exe` |
| `VERA_PROFILES_DIR` | Profile root containing `VORMETRA/` | Repository `resources/profiles` |
| `VERA_DATA_DIR` | Locks and generated output | `vera-control/.vera-datadir` |
| `VERA_FGF_POST_PATH` | Optional reviewed LinuxCNC converter file | Unset |
| `VERA_HOST` | HTTP bind host | `127.0.0.1` |
| `VERA_PORT` | HTTP port | `8765` |

Example from the repository root on Windows:

```powershell
$env:VERA_SLICER_BIN = (Resolve-Path ".\build\src\Release\orca-slicer.exe")
$env:VERA_PROFILES_DIR = (Resolve-Path ".\resources\profiles")
$env:VERA_DATA_DIR = (Join-Path $env:TEMP "vera-control-data")
Set-Location .\vera-control
```

## HTTP API and console

```bash
python run_dev.py
```

Open `http://127.0.0.1:8765/` for the local console.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Runtime configuration and slice-lock state |
| `GET` | `/profiles` | Available filaments and software envelope |
| `POST` | `/validate` | STL bounding-box validation without slicing |
| `POST` | `/slice` | Real slice with the configured binary |

Example validation request:

```powershell
$body = @{ stl_path = (Resolve-Path ".\model.stl") } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8765/validate" -ContentType "application/json" -Body $body
```

The server is a local development interface. It checks loopback `Host` and `Origin` values for state-changing requests, but it does not provide authentication or TLS. Do not bind it to an untrusted network.

## MCP

```bash
python -m vera_control.mcp_server
```

The stdio server exposes:

- `list_filaments`
- `get_machine_limits`
- `validate_model`
- `slice_stl`

The dependency is intentionally constrained to `mcp>=1,<2` because this release uses the 1.x `FastMCP` API. The test suite starts the module as a subprocess, completes an MCP client initialization, lists the four tools, and calls the two non-destructive metadata tools.

## Direct Python API

```python
from vera_control import slicer_bridge

print(slicer_bridge.list_filaments())
result = slicer_bridge.validate_model("model.stl")
if result["fits"]:
    sliced = slicer_bridge.slice_model("model.stl", filament="petg")
    print(sliced.stats)
```

`slice_model()` rejects unknown materials, missing inputs, competing slice jobs, and unavailable binaries with explicit exceptions. It never reports a half-created artifact as success.

## Evidence layers

- **Portable:** STL parsing, profile safety, HTTP behaviour, MCP startup, locks, timeouts, G-code header parsing, and archive repair.
- **Real slicer:** enabled only when `VERA_SLICER_BIN` resolves to a file.
- **External conversion:** enabled only when `VERA_FGF_POST_PATH` resolves to the reviewed converter.
- **Physical machine:** not exercised or implied by this package.

The hosted workflow runs the portable suite on Ubuntu and Windows with Python 3.10 and 3.13. Optional dependency skips remain visible in pytest output and are not counted as real-engine or physical evidence.

## Runtime safety

Only one real slicer process may run at a time. An in-process lock plus a `slice.lock` file under `VERA_DATA_DIR` prevents accidental parallel jobs; a competing HTTP request returns `409`. On Windows, the bridge uses below-normal process priority when available. Stale, malformed, and cross-platform lock files have explicit recovery behaviour covered by tests.

## License

`vera-control` is available under the [MIT License](LICENSE). The OrcaSlicer-derived engine and VORMETRA profiles at the repository root remain under [AGPLv3](../LICENSE.txt).
