# Security policy

## Supported scope

This repository accepts reports for the VORMETRA G1000 profiles, VORMETRA-specific integrations, and the `vera-control` HTTP, MCP, and direct Python interfaces.

If a defect also reproduces in an unmodified OrcaSlicer checkout, use the [OrcaSlicer security policy](https://github.com/OrcaSlicer/OrcaSlicer/security/policy). When the boundary is unclear, report it here first so the maintainer can route it without exposing details.

## Private reporting

Do not disclose vulnerability details in a public issue. Use [GitHub private vulnerability reporting](https://github.com/mehmeterendereli/vormetra-slice/security/advisories/new).

Include, when available:

- the affected commit and component;
- minimal reproduction conditions;
- the expected security impact;
- a proposed mitigation.

Redact credentials, customer data, real machine identifiers, private models, and local filesystem paths. If the private reporting link is unavailable, open a public issue without technical details and request a private channel.

## Runtime boundary

`vera-control` binds its development server to loopback by default. It does not provide authentication or TLS and must not be exposed to an untrusted network. A successful software test does not establish the safety of physical-machine motion, heating, extrusion, or emergency-stop behaviour.
