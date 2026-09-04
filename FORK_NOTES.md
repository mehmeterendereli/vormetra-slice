# Fork notes

VORMETRA Slice is a thin product fork of OrcaSlicer. The upstream Git history and AGPLv3 source tree are preserved even though GitHub does not display this repository with a fork badge.

## VORMETRA-specific surface

Changes specific to this product should normally remain in:

- `resources/profiles/VORMETRA/` and `resources/profiles/VORMETRA.json`;
- `vera-control/`;
- VORMETRA-specific documentation and repository community files;
- the smallest engine delta required by a verified profile or integration need.

`src/`, `deps/`, `deps_src/`, and `cmake/` are inherited engine areas. Do not modify them when the profile or control layer can solve the problem.

## Why the full source tree remains

The upstream-derived tree is retained for:

- complete corresponding source under AGPLv3;
- reproducible Windows, macOS, and Linux builds;
- compatibility checks for profiles, project files, and G-code behaviour;
- future upstream security and compatibility updates.

Large or apparently unused directories must not be removed without building and testing the affected platforms and packages.

## Upstream synchronization

Use two local remotes:

```text
origin    https://github.com/mehmeterendereli/vormetra-slice.git
upstream  https://github.com/OrcaSlicer/OrcaSlicer.git
```

Keep upstream synchronization separate from VORMETRA feature work. Resolve conflicts with explicit profile-format and platform-build verification. Report engine-wide defects upstream; keep G1000 profiles, pellet/FGF behaviour, and `vera-control` issues in this repository.
