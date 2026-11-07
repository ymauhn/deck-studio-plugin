"""Smoke test of the plugin's MCP server over stdio, as Claude Code starts it: a client starts `python -m deck_tools`,
lists the tools, makes a project from a small generated PDF, builds it, checks and photographs slide 1, runs the QA
check and asks the write guard about three files. Run from the server folder: uv run python tests/fumaca.py
Exits 1 on the first failure."""
import asyncio
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import netlify_falso  # noqa: E402
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.shared.message import SessionMessage
import anyio
from playwright.async_api import async_playwright

SERVER = Path(__file__).resolve().parent.parent
MAIS = """<section class="slide" id="s02" data-part="Teste">
<h2 class="title">Segundo slide</h2>
<aside class="notes"><p>Teste. (p. 1)</p></aside>
</section>
<section class="slide" id="s03" data-part="Teste">
<h2 class="title">Terceiro slide</h2>
<aside class="notes"><p>Teste. (p. 1)</p></aside>
</section>
"""
TOOLS = {"novo_projeto", "construir", "screenshot_slide", "check_slide", "add_image", "run_qa", "compile_beamer",
         "screenshot_beamer_page", "exportar", "verificar", "abrir_editor", "ler_selecao", "abrir_exemplo", "publicar",
         "responder_no_editor"}


def pdf(path):
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Um artigo de teste", fontsize=20)
    page.insert_text((72, 110), "O método reduz o erro de 12,5 para 7,25 em 3 conjuntos de dados.", fontsize=11)
    doc.save(path)


def launch(work, extra):
    """The server started exactly as the plugin's .mcp.json says, as Claude Code does: ${CLAUDE_PLUGIN_ROOT} and
    ${CLAUDE_PLUGIN_DATA} filled in, from a folder that is not the server's (the session's own)."""
    plugin = SERVER.parent
    spec = json.loads((plugin / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["deck"]
    fill = lambda v: v.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin)).replace("${CLAUDE_PLUGIN_DATA}", str(work / "dados"))
    env = {k: fill(v) for k, v in spec.get("env", {}).items()}
    if os.environ.get("UV_PROJECT_ENVIRONMENT"):  # a test run that already has the venv elsewhere
        env["UV_PROJECT_ENVIRONMENT"] = os.environ["UV_PROJECT_ENVIRONMENT"]
    session = work / "sessao"
    session.mkdir(exist_ok=True)
    return StdioServerParameters(command=spec["command"], args=[fill(a) for a in spec["args"]], cwd=str(session),
                                 env={**env, **extra})


def text(result):
    assert not result.is_error, result
    return "\n".join(c.text for c in result.content if c.type == "text")


def guard(file):
    event = {"tool_name": "Write", "tool_input": {"file_path": str(file), "content": "x"}, "cwd": str(file.parent)}
    out = subprocess.run([sys.executable, str(SERVER / "deck_tools" / "guarda.py")], input=json.dumps(event),
                         capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)["hookSpecificOutput"]["permissionDecision"] if out.stdout.strip() else "allow"


CHANNEL = []  # what the server pushed as channel events (Claude Code would put them in the session)


@contextlib.asynccontextmanager
async def tee(read):
    """The server's messages, less the channel events, which go to CHANNEL: the test client plays Claude Code."""
    send, out = anyio.create_memory_object_stream(100)

    async def pump():
        async with send:
            async for m in read:
                msg = getattr(getattr(m, "message", None), "root", getattr(m, "message", None))
                if isinstance(m, SessionMessage) and getattr(msg, "method", "") == "notifications/claude/channel":
                    CHANNEL.append(msg.params)
                    continue
                await send.send(m)
    async with anyio.create_task_group() as tg:
        tg.start_soon(pump)
        yield out
        tg.cancel_scope.cancel()


async def channel_has(text):
    for _ in range(100):
        if any(text in c["content"] for c in CHANNEL):
            return
        await asyncio.sleep(0.1)
    raise AssertionError(f"{text!r} not pushed: {CHANNEL}")


async def main():
    work = Path(tempfile.mkdtemp(prefix="deck-plugin-fumaca-"))
    pdf(work / "artigo.pdf")
    api, deploys, fake = netlify_falso.start()
    params = launch(work, {"DECK_NO_BROWSER": "1", "NETLIFY_API": api, "NETLIFY_AUTH_TOKEN": "falso"})
    async with stdio_client(params) as (raw, write), tee(raw) as read, ClientSession(read, write) as s:
        init = await s.initialize()
        assert "claude/channel" in (init.capabilities.experimental or {}), init.capabilities
        names = {t.name for t in (await s.list_tools()).tools}
        assert names == TOOLS, names
        project = work / "Projeto de teste"
        out = text(await s.call_tool("novo_projeto", {"fonte": str(work / "artigo.pdf"), "nome": "Projeto de teste",
                                                      "pasta": str(project)}))
        assert (project / "studio.json").is_file() and (project / "context").is_dir(), out
        (project / "deck/src/slides/01-mais.html").write_text(MAIS, encoding="utf-8")
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
            await page.get_by_text("Enviado. O Claude responde aqui.").wait_for()
            # the chat: the message (with the box's loc) goes into the session as a channel event; the reply shows
            await channel_has("Encurte o título.\nCaixas selecionadas")
            assert "deck/src/slides/" in CHANNEL[-1]["content"], CHANNEL[-1]
            assert "ok" == text(await s.call_tool("responder_no_editor", {"texto": "Título encurtado no slide 1."}))
            await page.locator(".ds-claude", has_text="Título encurtado no slide 1.").wait_for()
            await page.locator(".ds-autor", has_text="Encurte o título.").wait_for()
            # Ir para o slide
            await page.get_by_label("Ir para o slide").fill("2")
            await page.get_by_label("Ir para o slide").press("Enter")
            assert await page.evaluate("window.deck.state().slide") == 2
            # Seguir o agente: a slide changed and built again, the page goes to it
            await page.get_by_label("Ir para o slide").fill("1")
            await page.get_by_label("Ir para o slide").press("Enter")
            f = project / "deck/src/slides/01-mais.html"
            f.write_text(f.read_text(encoding="utf-8").replace("Terceiro", "Terceiro, editado"), encoding="utf-8")
            assert "Build sem erros" in text(await s.call_tool("construir", {}))
            await page.get_by_text("Seguindo o agente: slide 3.").wait_for(timeout=20_000)
            assert await page.evaluate("window.deck.state().slide") == 3
            await b.close()
        sel = json.loads(text(await s.call_tool("ler_selecao", {})))
        assert sel["pedido"] == "Encurte o título." and sel["itens"][0]["loc"].startswith("deck/src/slides/"), sel
        assert "export-pdf pronto" in text(await s.call_tool("exportar", {"formato": "pdf"}))
        assert (project / "deck/dist/deck.pdf").is_file()
        if shutil.which("pdflatex"):  # the Overleaf zip compiles the Beamer deck: only with TeX (not on the CI runners)
            ov = text(await s.call_tool("exportar", {"formato": "overleaf"}))
            assert "Zip do Overleaf" in ov and "sem nenhum [?]" in ov, ov
        # the tools and the editor speak the deck's language: an English project
        en = work / "English project"
        text(await s.call_tool("novo_projeto", {"fonte": str(work / "artigo.pdf"), "nome": "English project",
                                                "pasta": str(en), "idioma": "en"}))
        assert "Built with no errors" in text(await s.call_tool("construir", {"projeto": str(en)}))
        assert "Playwright's Chromium" in text(await s.call_tool("verificar", {"idioma": "en"}))
        url_en = re.search(r"http://127\.0\.0\.1:\d+/\?t=\S+", text(await s.call_tool("abrir_editor", {"projeto": str(en)})))[0]
        async with async_playwright() as p:
            b = await p.chromium.launch()
            page = await b.new_page(viewport={"width": 1600, "height": 900})
            await page.goto(url_en)
            await page.wait_for_function("() => window.deck && window.deck.state")
            await page.get_by_label("Go to slide").wait_for()
            await page.get_by_text("Follow the agent").wait_for()
            await page.locator("section.slide.active h1, section.slide.active h2").first.click()
            await page.get_by_label("What to change").fill("Make it shorter.")
            await page.get_by_label("What to change").press("Enter")  # Enter sends
            await page.get_by_text("Sent. Claude answers here.").wait_for()
            await channel_has("Make it shorter.\nSelected boxes")
            assert "ok" == text(await s.call_tool("responder_no_editor", {"texto": "Done: slide 1 is shorter."}))
            await page.locator(".ds-claude", has_text="Done: slide 1 is shorter.").wait_for()
            await page.reload()  # the chat survives the reload after a build
            await page.locator(".ds-claude", has_text="Done: slide 1 is shorter.").wait_for()
            await b.close()
        await s.call_tool("construir", {"projeto": str(project)})  # back to the Portuguese project for what follows
        pub = text(await s.call_tool("publicar", {"site": "deck-teste"}))
        assert "deck-teste.netlify.app" in pub and deploys, pub
        assert (project / "deck/tools/netlify-site.json").is_file()
    fake.shutdown()
    assert guard(project / "deck/src/slides/00-title.html") == "allow"
    assert guard(project / "deck/dist/deck.html") == "deny"
    assert guard(project / "qa/check_deck.py") == "ask"
    assert guard(work / "fora-do-projeto.txt") == "allow"
    print(f"fumaça ok: {len(names)} ferramentas, projeto, build, check, captura, QA, editor (chat pelo canal, ir para o slide, seguir o agente), publicar, os dois idiomas e guarda ({work})")


if __name__ == "__main__":
    asyncio.run(main())
