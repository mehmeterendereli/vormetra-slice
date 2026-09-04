# C++ test guidance

The C++ test tree is inherited from OrcaSlicer. Use the upstream build configuration that matches the engine change, then run the narrow affected test group and the broader suite supported by that platform.

## Test quality

- Tests must be order-independent and clean up their own temporary files.
- Prefer deterministic assertions; record and report any random seed used to reproduce a failure.
- Avoid environment-specific absolute paths and access to private services.
- Keep fixtures synthetic or publicly distributable.
- Treat hardware-, GPU-, locale-, and platform-dependent skips as explicit boundaries rather than successful coverage.

Repository-specific Python control and profile tests are maintained separately under `vera-control/tests/` and run with:

```bash
cd vera-control
python -m pip install -e ".[dev]"
python -m pytest -q -rs
```

For the complete upstream engine build and test entry points, see [README.upstream.md](../README.upstream.md) and the CMake configuration in this repository.
