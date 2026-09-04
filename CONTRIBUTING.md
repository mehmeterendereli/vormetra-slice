# Contributing to VORMETRA Slice

Contributions should preserve the repository's thin-fork structure, upstream attribution, license boundaries, and evidence discipline.

## Scope

- Keep VORMETRA-specific profiles under `resources/profiles/VORMETRA/`.
- Keep the independent MIT control layer under `vera-control/`.
- Avoid broad upstream engine changes unless the profile or control layer cannot solve the verified problem.
- Do not copy secrets, private repository references, customer data, or machine-specific absolute paths into public files.

## Verification

For control-layer or profile changes:

```bash
cd vera-control
python -m pip install -e ".[dev]"
python -m pip check
python -m compileall -q vera_control
python -m pytest -q -rs
```

Dependency-bound tests must remain explicit. A skipped real-binary, converter, or hardware test is not a pass for that layer.

For engine changes, follow the upstream build and test guidance in [README.upstream.md](README.upstream.md) and [tests/TESTING.md](tests/TESTING.md). Record the compiler, platform, commands, and exact result in the pull request.

## Evidence language

Separate these claims in code review and documentation:

1. portable Python verification;
2. execution with a real slicer binary;
3. optional LinuxCNC converter execution;
4. physical machine testing.

Do not infer commissioning, throughput, accuracy, surface quality, or reliability from software-only evidence. Label numerical configuration values as design inputs, reference starting points, or measured results with a source.

## Licenses

The OrcaSlicer-derived engine and VORMETRA profiles are AGPLv3. `vera-control` is MIT-licensed as a separate program that invokes the engine through a command-line process boundary. Preserve existing copyright and attribution notices when modifying either scope.

## Pull requests

Use focused commits and describe the problem, root cause, implementation, verification, evidence limits, risks, and rollback path. Do not commit generated build directories, local runtime data, credentials, or unreviewed release binaries.
