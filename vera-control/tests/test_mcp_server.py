import sys

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


def test_mcp_stdio_startup_and_tools():
    async def exercise_server():
        parameters = StdioServerParameters(
            command=sys.executable,
            args=["-m", "vera_control.mcp_server"],
        )
        async with stdio_client(parameters) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                available = await session.list_tools()
                names = {tool.name for tool in available.tools}
                assert names == {
                    "get_machine_limits",
                    "list_filaments",
                    "slice_stl",
                    "validate_model",
                }

                filaments = await session.call_tool("list_filaments")
                assert filaments.isError is False
                filament_text = " ".join(block.text for block in filaments.content)
                assert "petg" in filament_text
                assert "pla" in filament_text

                limits = await session.call_tool("get_machine_limits")
                assert limits.isError is False
                limit_text = " ".join(block.text for block in limits.content)
                assert "bed_x_mm" in limit_text

    anyio.run(exercise_server)
