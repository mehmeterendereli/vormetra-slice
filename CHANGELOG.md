# Project history

These entries describe repository milestones, not published binary releases. This repository currently has no tags, installer, executable release, or physically qualified production claim.

## Unreleased — 2026-09-04

- Reworked the public README, contribution guide, security policy, issue forms, and pull-request template around the VORMETRA product boundary.
- Replaced internal coordination files and inherited OrcaSlicer account automation with public maintainer documentation.
- Added deterministic VORMETRA profile verification and a hosted `vera-control` matrix for Ubuntu and Windows on Python 3.10 and 3.13.
- Constrained the MCP dependency to the supported 1.x API and added a real stdio client handshake test.
- Removed machine-specific default paths; runtime binaries, profile roots, data directories, and optional conversion code are configured through environment variables.
- Added explicit HTTP host/origin protection, portable safety tests, and an accessible local operations console.
- Assigned deterministic profile setting identifiers and aligned the process profile name with the VORMETRA G1000.
- Reverified the 32-test software suite with an official OrcaSlicer v2.4.2 portable binary, the current repository profiles, and an explicitly configured external converter.

## 0.1.3 — 2026-07-16

- Changed the VORMETRA profile from Klipper-specific macros to plain Marlin-flavour G-code for the optional LinuxCNC conversion boundary.
- Added regression coverage for absence of Klipper macros and for explicitly configured conversion.
- Local software verification exercised a 200 × 200 × 100 mm fixture. This did not establish commissioning, dimensional accuracy, throughput, surface quality, or machine reliability.

## 0.1.2 — 2026-07-10

- Rejected cross-origin and non-loopback state-changing HTTP requests.
- Corrected Windows process-liveness detection and stale, malformed, and cross-platform slice-lock recovery.
- Converted slicer timeouts and malformed lock content into explicit control-layer errors.
- Expanded portable regression coverage for these behaviours.

## 0.1.1 — 2026-07-08

- Published the OrcaSlicer-derived engine and VORMETRA profiles under the repository's AGPLv3 licence.
- Added the separate MIT licence for `vera-control`, which invokes the slicer through a process boundary.

## 0.1.0 — 2026-07-07

- Added the initial G1000 machine, process, and pellet profiles.
- Added the `vera-control` HTTP, MCP, and direct Python interfaces.
- Preserved the original OrcaSlicer overview as `README.upstream.md`.
- Established the 1000 × 1000 × 1000 mm envelope and 5.0 mm nozzle as configuration inputs. They are not measured physical outcomes.
