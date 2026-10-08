# OrcaSlicer #15201 validation record

**Target:** https://github.com/OrcaSlicer/OrcaSlicer/issues/15201  
**Patch:** [orcaslicer-15201.patch](./orcaslicer-15201.patch)  
**Upstream base checked:** `67a16dabca4af8b0de871d75bea08a7ce2cfc9f8`  
**Patch blob:** `2563158cab139caf3eaeb5e6cdbe5144519a2d2b`  
**Patch SHA-256:** `7041103afea6aeb14bed165979214b5884df1e23793aba4476d9f5e679a27f53`

## Change

All four shipped SparkX i7 nozzle profiles (0.2, 0.4, 0.6 and 0.8 mm) change the purge-line exit move from:

```gcode
G91
G1 X-1 Z-0.3
```

to:

```gcode
G91
G1 X-1 Z0.1
```

Because `G91` selects relative positioning, the old move lowered the nozzle 0.3 mm after the 0.2 mm purge line. The replacement raises it 0.1 mm while retaining the X wipe.

## Verification

Run against the current upstream profile tree on 2026-10-08:

- `git apply --check`: clean on upstream `67a16dab`
- `git diff --check`: clean
- four profile JSON files parsed; 4 safe relative lifts and 0 old negative-Z moves
- `python3 scripts/orca_profile_tool.py check --vendor Creality --profiles resources/profiles`: 0 errors, 0 warnings
- `python3 -m unittest discover -s scripts/tests -t scripts`: 281 passed, 1 skipped
- official nightly `OrcaSlicer_profile_validator` SHA-256: `0286ab913daa0ac589a0a9f6d3fa25f1c8407f2bebcb8d287796436f64dfd2fd`
- system-profile validation: 68 vendors loaded; successful
- slice validation: 1,129 printer presets plus 10 extra process presets, 123 extra filament presets and 1 by-object printer; all 1,263 slices succeeded
- filament-subtype validation: successful

The slicer validator emitted one non-fatal Afinia `nozzle_info.json` parse message in this environment, then reported all 1,263 slices and the validation successful.

## Boundary

No physical SparkX i7 was available, so the nozzle motion has not been observed on hardware. The patch has not been submitted to OrcaSlicer and does not count as an accepted contribution.

## Ready upstream PR

**Title:** `profiles: lift SparkX i7 nozzle after purge line`

**Body:**

Fixes #15201.

The four SparkX i7 machine profiles entered relative positioning with `G91` and then issued `G1 X-1 Z-0.3` after drawing the purge line at Z0.2. That moves the nozzle 0.3 mm toward the bed and can produce the reported scrape. This changes the relative Z component to `Z0.1`, matching the reporter's tested workaround while preserving the X wipe.

Validation: clean application to current main; profile-tool check 0 errors/0 warnings; 281 profile-tool tests passed (1 skipped); official nightly validator loaded 68 vendors and completed all 1,263 slice checks; filament-subtype validation passed.

Hardware validation was not performed.
