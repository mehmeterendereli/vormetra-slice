# OrcaSlicer #15201 validation record

**Target:** https://github.com/OrcaSlicer/OrcaSlicer/issues/15201  
**Patch:** [orcaslicer-15201.patch](./orcaslicer-15201.patch)  
**Upstream main checked:** `785a1946a6a8f9d5f48fd4c8b3287194908c010a`  
**Patch blob:** `738e5e1594921b5b45f699de7137c3c47230cea2`  
**Patch SHA-256:** `f504ae8102569f3a6f8a3d0ed8bb1fd63faf202876cb3924161d5457143ae954`

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

The patch also increments the sibling Creality vendor profile version from `02.03.02.87` to `02.03.02.88`, as required by OrcaSlicer's current profile-change rules.

## Verification

Re-run on 2026-10-09 against the final five-file patch:

- the four SparkX profile blobs and `resources/profiles/Creality.json` on upstream `main` are byte-identical to the local validation base
- `git diff --check`: clean
- five JSON files parsed; 4 safe relative lifts, 0 old negative-Z moves, vendor version `02.03.02.88`
- `python3 scripts/orca_profile_tool.py check --vendor Creality --profiles resources/profiles`: 0 errors, 0 warnings
- `python3 -m unittest discover -s scripts/tests -t scripts`: 281 passed, 1 skipped
- official `OrcaSlicer_profile_validator` SHA-256: `0286ab913daa0ac589a0a9f6d3fa25f1c8407f2bebcb8d287796436f64dfd2fd`
- full-vendor slice validation: 1,129 printer presets, 10 extra process presets, 123 extra filament presets and 1 by-object printer; all 1,263 slices succeeded
- filament-subtype validation: successful

The validator emitted one non-fatal Afinia `nozzle_info.json` parse message in this environment, then returned exit 0 after reporting all 1,263 slices successful.

## Boundary

No physical SparkX i7 was available, so the nozzle motion has not been observed on hardware. The patch has not been merged by OrcaSlicer and does not count as an accepted contribution.

## Ready upstream PR

**Title:** `profiles: lift SparkX i7 nozzle after purge line`

**Body:**

Fixes #15201.

The four SparkX i7 machine profiles entered relative positioning with `G91` and then issued `G1 X-1 Z-0.3` after drawing the purge line at Z0.2. That moves the nozzle 0.3 mm toward the bed and can produce the reported scrape. This changes the relative Z component to `Z0.1`, matching the reporter's tested workaround while preserving the X wipe.

The Creality vendor profile version is bumped from `02.03.02.87` to `02.03.02.88`, as required for profile changes.

Validation: profile-tool check 0 errors/0 warnings; 281 profile-tool tests passed (1 skipped); the official validator loaded all vendors and completed 1,263 slice checks successfully; filament-subtype validation passed.

Hardware validation was not performed.
