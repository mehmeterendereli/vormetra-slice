# VORMETRA profile CI verification boundary

This file documents what the public GitHub Actions definition is intended to prove for the VORMETRA profile tree, and what evidence is still pending.

## Portable workflow definition

The `vera-control verification` workflow is configured as a four-cell matrix on Ubuntu and Windows with Python 3.10 and 3.13. It compiles the Python control package and exercises:

- STL parsing and the 1000 × 1000 × 1000 mm software envelope checks;
- HTTP API behaviour and error mapping;
- profile-safety rules, including removal of copied private endpoints;
- single-process locking, stale/corrupt lock recovery and timeout handling;
- G-code header parsing and archive-thumbnail repair.

The upstream-derived `Check profiles` workflow remains responsible for the broader profile-validator path when files under `resources/profiles/**` change.

## Hosted-run status

As of **2026-09-04**, matching pull-request events have not caused GitHub to create a run for either workflow. Repository-level Actions permissions and individual workflow enablement are tracked in [issue #7](https://github.com/mehmeterendereli/vormetra-slice/issues/7).

Until issue #7 is closed with a real run URL and four successful jobs, the checked-in matrix is a reproducible **verification definition**, not completed hosted-CI evidence.

## Explicitly outside the portable CI claim

Even after the portable matrix runs successfully, it will not prove:

- physical G1000 commissioning or production qualification;
- calibrated throughput, accuracy or surface quality;
- execution of tests that require a local `orca-slicer` binary;
- execution of the external LinuxCNC/FGF post-processor integration when its path is absent.

Dependency-bound tests are marked to skip when `VERA_SLICER_BIN` or `VERA_FGF_POST_PATH` is unavailable. Hardware and real-engine evidence remains documented separately in [`README.md`](README.md).
