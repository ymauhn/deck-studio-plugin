"""Smoke test of the plugin's MCP server over stdio, as Claude Code starts it: a client starts `python -m deck_tools`,
lists the tools, makes a project from a small generated PDF, builds it, checks and photographs slide 1, runs the QA
check and asks the write guard about three files. Run from the server folder: uv run python tests/fumaca.py
Exits 1 on the first failure."""
import asyncio
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from playwright.async_api import async_playwright

SERVER = Path(__file__).resolve().parent.parent
TOOLS = {"novo_projeto", "construir", "screenshot_slide", "check_slide", "add_image", "run_qa", "compile_beamer",
         "screenshot_beamer_page", "exportar", "verificar", "abrir_editor", "ler_selecao", "abrir_exemplo"}


def pdf(path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Um artigo de teste", fontsize=20)
    page.insert_text((72, 110), "O método reduz o erro de 12,5 para 7,25 em 3 conjuntos de dados.", fontsize=11)
    doc.save(path)


def text(result):
    assert not result.is_error, result
    return "\n".join(c.text for c in result.content if c.type == "text")


def guard(file):
    event = {"tool_name": "Write", "tool_input": {"file_path": str(file), "content": "x"}, "cwd": str(file.parent)}
    out = subprocess.run([sys.executable, str(SERVER / "deck_tools" / "guarda.py")], input=json.dumps(event),
                         capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"] if out.stdout.strip() else "allow"


async def main():
    work = Path(tempfile.mkdtemp(prefix="deck-plugin-fumaca-"))
    pdf(work / "artigo.pdf")
    params = StdioServerParameters(command=sys.executable, args=["-m", "deck_tools"], cwd=str(SERVER),
                                   env={"DECK_DATA": str(work / "dados"), "DECK_NO_BROWSER": "1"})
    async with stdio_client(params) as (read, write), ClientSession(read, write) as s:
        await s.initialize()
        names = {t.name for t in (await s.list_tools()).tools}
        assert names == TOOLS, names
        project = work / "Projeto de teste"
        out = text(await s.call_tool("novo_projeto", {"fonte": str(work / "artigo.pdf"), "nome": "Projeto de teste",
                                                      "pasta": str(project)}))
        assert (project / "studio.json").is_file() and (project / "context").is_dir(), out
        assert "Build sem erros" in text(await s.call_tool("construir", {}))
        assert "nada cortado" in text(await s.call_tool("check_slide", {"slide": 1}))
        shot = await s.call_tool("screenshot_slide", {"slide": 1})
        assert any(c.type == "image" for c in shot.content), shot
        qa = text(await s.call_tool("run_qa", {"which": "check"}))
        assert "checks pass" in qa, qa[-800:]
        url = re.search(r"http://127\.0\.0\.1:\d+/\?t=\S+", text(await s.call_tool("abrir_editor", {})))[0]
        async with async_playwright() as p:
            b = await p.chromium.launch()
            page = await b.new_page(viewport={"width": 1600, "height": 900})
            await page.goto(url)
            await page.wait_for_function("() => window.deck && window.deck.state")
            await page.locator("section.slide.active h1, section.slide.active h2").first.click()
            await page.get_by_label("O que mudar").fill("Encurte o título.")
            await page.get_by_role("button", name="Enviar ao Claude").click()
            await page.get_by_text("Enviado.").wait_for()
            await b.close()
        sel = json.loads(text(await s.call_tool("ler_selecao", {})))
        assert sel["pedido"] == "Encurte o título." and sel["itens"][0]["loc"].startswith("deck/src/slides/"), sel
    assert guard(project / "deck/src/slides/00-title.html") == "allow"
    assert guard(project / "deck/dist/deck.html") == "deny"
    assert guard(project / "qa/check_deck.py") == "ask"
    assert guard(work / "fora-do-projeto.txt") == "allow"
    print(f"fumaça ok: {len(names)} ferramentas, projeto, build, check, captura, QA, editor e guarda ({work})")


asyncio.run(main())
