"""The example deck through the MCP server, as a colleague opens it: abrir_exemplo copies it to an empty folder, runs
npm ci and builds it; then slide 1 is checked and photographed. Needs Node and the network (npm). Run from the
server folder: uv run python tests/exemplo.py"""
import asyncio
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).resolve().parent.parent


def text(result):
    assert not result.is_error, result
    return "\n".join(c.text for c in result.content if c.type == "text")


async def main():
    work = Path(tempfile.mkdtemp(prefix="deck-plugin-exemplo-"))
    params = StdioServerParameters(command=sys.executable, args=["-m", "deck_tools"], cwd=str(SERVER),
                                   env={"DECK_DATA": str(work / "dados"), "DECK_NO_BROWSER": "1"})
    async with stdio_client(params) as (read, write), ClientSession(read, write) as s:
        await s.initialize()
        out = text(await s.call_tool("abrir_exemplo", {"pasta": str(work / "exemplo")}, read_timeout_seconds=900))
        assert out.startswith("Exemplo pronto em") and "build falhou" not in out, out
        check = text(await s.call_tool("check_slide", {"slide": 1}))
        shot = await s.call_tool("screenshot_slide", {"slide": 1})
        assert any(c.type == "image" for c in shot.content), shot
    print(f"exemplo ok: {out.splitlines()[0]} | {check}")


asyncio.run(main())
