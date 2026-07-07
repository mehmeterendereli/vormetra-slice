"""MCP server exposing VORMETRA Slice as native tools for Claude Code and any
other MCP-compatible AI agent -- this is the direct answer to "kendin ve
başka yapay zekaların da Slicer'ı kontrol edebilecek şekilde geliştir"
(build it so you and other AIs can control the Slicer too).

Run with: python -m vera_control.mcp_server
Then point an MCP client's config at this command (stdio transport).

Requires the optional 'mcp' extra: pip install -e ".[mcp]"

Note: deliberately NOT using `from __future__ import annotations` here --
FastMCP builds each tool's JSON schema by inspecting live parameter/return
type objects at decoration time, and PEP 563's lazy string annotations break
that introspection (`issubclass(param.annotation, Context)` fails because
the annotation is a str, not a class).
"""

from mcp.server.fastmcp import FastMCP

from . import config, slicer_bridge

mcp = FastMCP(
    name="vormetra-slice",
    instructions=(
        "Controls VORMETRA Slice, the AI-fed pellet/FGF 3D-printer slicer for "
        "the VORMETRA G1000. Use validate_model before slice_stl on anything "
        "you didn't already know fits the 1000x1000x1000mm bed."
    ),
)


@mcp.tool()
def list_filaments() -> list[str]:
    """List the VORMETRA G1000 material profiles available to slice with."""
    return slicer_bridge.list_filaments()


@mcp.tool()
def get_machine_limits() -> dict:
    """Return the G1000's build volume and nozzle size, in millimeters."""
    return dict(config.MACHINE_LIMITS)


@mcp.tool()
def validate_model(stl_path: str) -> dict:
    """Check whether an STL's bounding box fits the G1000 build volume.
    Cheap -- does not invoke the slicer. Always call this before slice_stl
    on a model of unknown size."""
    return slicer_bridge.validate_model(stl_path)


@mcp.tool()
def slice_stl(stl_path: str, filament: str = "petg") -> dict:
    """Slice an STL for the VORMETRA G1000 and return the resulting G-code
    stats plus the path to the generated .gcode.3mf. filament is one of
    list_filaments()'s results (default 'petg', per OQ-03's recommendation
    as the lower-risk first material)."""
    result = slicer_bridge.slice_model(stl_path, filament=filament)
    return {
        "gcode_3mf_path": str(result.gcode_3mf_path),
        "stats": result.stats,
    }


if __name__ == "__main__":
    mcp.run()
