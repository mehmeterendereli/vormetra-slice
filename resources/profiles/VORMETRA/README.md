# VORMETRA G1000 profile

This directory contains the OrcaSlicer vendor profile used by VORMETRA Slice for software evaluation of the G1000 pellet/FGF workflow.

**Status:** active development. Hosted checks parse every JSON file and verify repository names, references, field types, conflicts, and deterministic setting IDs. The current profiles have also been exercised locally through a real OrcaSlicer v2.4.2 CLI. Profile values are configuration inputs and calibration starting points; they are not physical performance measurements.

## Files

```text
machine/    G1000 machine definitions and 5.0 mm nozzle variant
process/    2.00 mm layer-height starting process
filament/   PLA and PETG pellet starting profiles
```

The leaf machine file repeats critical fields that OrcaSlicer's direct `--load-settings` path does not reliably inherit from common files. Keep `printable_area`, `printable_height`, `gcode_flavor`, `pellet_modded_printer`, and machine start/end G-code explicit in the leaf definition.

## Evidence classification

| Profile field | Current value | Classification | Physical status |
|---|---:|---|---|
| Software build envelope | 1000 × 1000 × 1000 mm | G1000 configuration input | Not demonstrated as a commissioned travel envelope |
| Nozzle diameter | 5.0 mm | G1000 configuration input | Requires installed-hardware confirmation before production use |
| Process layer height | 2.0 mm | Initial process setting | Not production-qualified |
| G-code flavor | Marlin | Software interface decision for the converter input | Verified in generated G-code; not a machine commissioning result |
| Multi-zone count | 4 | Extruder design input | Independent physical control of four zones is not validated here |
| Retraction and temperatures | Values in JSON | Reference starting settings | Must be calibrated for the actual material, hardware, and environment |
| Flow-related limits | Values in JSON | Software ceiling or starting value | Must not be read as measured sustainable throughput |

Unresolved calibration values remain visible as `TBD` where the profile schema permits it. Do not replace them with estimates solely to make the profile appear complete.

## Software verification

From `vera-control/`:

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
```

The portable suite checks the selected profile safety fields that do not require a slicer binary: unverified network host values remain empty, the exclusion area is non-degenerate, and the vendor index contains no copied private address. Separate control-layer tests cover the configured 1000 mm software envelope, material selection, lock handling, timeouts, and archive repair.

When `VERA_SLICER_BIN` is configured, three additional tests exercise the actual CLI, including the effective machine profile and generated Marlin-flavor G-code. When `VERA_FGF_POST_PATH` is also configured, the generated G-code is passed through the optional LinuxCNC converter and checked for coordinated U-axis extrusion plus translated heater setpoints. Missing optional dependencies are reported as skips, not passes.

On 2026-09-04 the current repository profile completed all 34 tests with both software dependencies configured. A control run against the older profiles bundled beside the external binary correctly failed because those profiles still emitted Klipper macros; those stale profiles are not accepted as current evidence.

## Known profile constraints

- Direct file loading and GUI preset loading can resolve inheritance differently; critical machine fields are intentionally duplicated in the leaf file.
- Pellet flow coefficient conversion is written explicitly because the relevant automatic conversion is tied to GUI behaviour in the upstream application.
- Vendor-specific placeholder variables that the public OrcaSlicer parser cannot resolve are not emitted.
- The optional converter currently models a single heater-control channel. Four-zone control remains a separate electrical/control validation task.
- Headless CLI runs can omit thumbnail PNG payloads while retaining archive relationships; `vera-control` repairs those missing neutral previews so the generated 3MF remains internally consistent.

## Safety boundary

Do not use this profile as the sole basis for operating an uncommissioned machine. Before physical use, verify motion directions and limits, emergency-stop behaviour, heaters and sensors, extrusion calibration, collision clearance, material data, and the complete controller conversion on the actual hardware. A successful profile or slicing test cannot prove safe machine operation.

## License and upstream basis

The profile is distributed under the repository's [AGPLv3 license](../../../LICENSE.txt) and uses OrcaSlicer's public pellet-profile infrastructure. Upstream project attribution and contributor history are preserved in [README.upstream.md](../../../README.upstream.md) and the Git history.
