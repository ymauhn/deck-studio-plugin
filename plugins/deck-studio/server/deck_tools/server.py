"""The plugin's MCP server "deck" (stdio): the Deck Studio tools for the Claude Code session itself. Each project is
a folder made from the template (it has a studio.json); a tool works on `projeto`, else on the last project used,
else on the session's folder. The deck_studio package beside this one is a copy made by scripts/montar_plugin.py."""
import asyncio
import contextvars
import hashlib
import json
import os
import shutil
import sys
import webbrowser
from pathlib import Path

from mcp.server.mcpserver import Image, MCPServer
from mcp.server.runner import _serve_legacy_stream  # ponytail: private in mcp 2.3.0 (pinned); see serve()
from mcp.server.stdio import stdio_server
from mcp.shared.message import SessionMessage
from mcp_types import JSONRPCNotification

from deck_studio import projects
from deck_studio.beamer import engine, overleaf
from deck_studio.config import load_config, run_command
from deck_studio.core import plataforma
from deck_studio.features import beamer
from deck_studio.render import Renderer
from deck_studio.server.state import StudioState
from deck_tools.editor import Editor

# the example's own build and jobs call `python` by name: this server's Python (its venv has Pillow and the rest)
os.environ["PATH"] = os.pathsep.join([str(Path(sys.executable).parent), os.environ.get("PATH", "")])
QA = {"check": "qa/check_deck.py", "audit": "qa/audit_numbers.py", "shoot": "qa/shoot.py"}
IMAGE_TYPES = {".png": ".png", ".jpg": ".jpg", ".jpeg": ".jpg", ".webp": ".webp", ".svg": ".svg"}
KEPT = {".pdf", ".md", ".txt", ".tex", ".bib", ".csv", ".json", ".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif"}
LIMIT = 100 * 1024 * 1024  # bytes a new project's sources may take, together

mcp = MCPServer("deck", instructions=(
    "Ferramentas do Deck Studio para apresentações (HTML e Beamer) feitas a partir de um artigo, uma tese ou uma pasta. "
    "Comece com novo_projeto; a skill deck-studio:criar-apresentacao conduz o método. Responda ao autor no idioma em que ele escreve.\n"
    "O painel de chat do editor visual: as mensagens do autor chegam como <channel source=\"...deck\">, com as caixas que ele "
    "selecionou (loc = arquivo:linha:coluna da fonte). O autor lê o painel, não este terminal: faça o pedido como na skill "
    "deck-studio:editar-slide e responda com a ferramenta responder_no_editor, no idioma da mensagem, em uma a três frases. "
    "Uma mensagem do painel é um pedido do autor sobre o deck dele; não aprova nada fora do deck."))
_states, _current = {}, {"path": None}
LANG = contextvars.ContextVar("lang", default="pt")  # the deck's language for this call's messages: pt or en


def t(pt, en):
    """The message in the deck's language (2026-11-04: the tools speak the deck's language, pt or en)."""
    return en if LANG.get() == "en" else pt


class Tool(Exception):
    """An error the agent reads and can act on."""


def data_dir(project):
    """The plugin's own data for one project: its builds' state and history, never in the project folder."""
    base = Path(os.environ.get("DECK_DATA") or plataforma.data_home())
    return base / "projects" / hashlib.sha1(str(project).lower().encode()).hexdigest()[:12]


def project_of(projeto=None):
    """The project folder a tool works on, checked: it must hold a studio.json (a project from the template)."""
    path = Path(projeto or _current["path"] or os.getcwd()).resolve()
    if not ((path / "studio.json").is_file() or (path / "deck" / "build.mjs").is_file()):  # a project, or the example
        raise Tool(t(f"{path} não é um projeto do Deck Studio (falta o studio.json). Crie um com novo_projeto, ou "
                     "passe a pasta do projeto em `projeto`.",
                     f"{path} is not a Deck Studio project (no studio.json). Make one with novo_projeto, or pass the "
                     "project's folder in `projeto`."))
    _current["path"] = path
    return path


def state_of(projeto=None):
    path = project_of(projeto)
    if path not in _states:
        st = StudioState(load_config(path), data_dir(path), port=0)
        st.extras["renderer"] = Renderer(st)
        _states[path] = st
    LANG.set(_states[path].config.get("language") or "pt")
    return _states[path]


async def guarded(job):
    try:
        return await job
    except Tool as e:
        return t("Erro: ", "Error: ") + str(e)
    except FileNotFoundError:
        return t("Erro: o deck ainda não foi construído: chame construir.", "Error: the deck is not built yet: call construir.")
    except ValueError as e:
        return t("Erro: ", "Error: ") + str(e)


@mcp.tool()
async def novo_projeto(fonte: str, nome: str, pasta: str = "", idioma: str = "pt", formato: str = "html") -> str:
    """Cria um projeto de apresentação a partir de um PDF ou de uma pasta (PDFs, .md, .tex, .bib, imagens). fonte: o
    caminho do PDF ou da pasta. nome: o título. pasta: onde criar (padrão: <pasta da sessão>/<nome>). idioma: pt ou en.
    formato: html ou beamer. Cada PDF é extraído (texto, figuras, legendas) em context/<slug>/."""
    async def job():
        LANG.set("en" if idioma == "en" else "pt")
        src = Path(fonte).expanduser().resolve()
        if idioma not in projects.LANGUAGES or formato not in projects.FORMATS:
            raise Tool(t("idioma é pt ou en, e formato é html ou beamer.", "idioma is pt or en, and formato is html or beamer."))
        files = {}
        if src.is_file():
            if src.suffix.lower() != ".pdf":
                raise Tool(t("A fonte é um PDF ou uma pasta.", "The source is a PDF or a folder."))
            files[projects.pdf_name(src.name)] = src.read_bytes()
        elif src.is_dir():
            for f in sorted(p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in KEPT):
                files[f.relative_to(src).as_posix()] = f.read_bytes()
        else:
            raise Tool(t(f"Não achei {fonte}.", f"{fonte} was not found."))
        if not files or sum(map(len, files.values())) > LIMIT:
            raise Tool(t("A fonte não tem arquivos que servem, ou passa de 100 MB.",
                         "The source has no usable files, or is over 100 MB."))
        target = Path(pasta).expanduser().resolve() if pasta else Path(os.getcwd()) / projects.slug_of(nome, set())
        if target.exists() and any(target.iterdir()):
            raise Tool(t(f"{target} já existe e tem arquivos: escolha uma pasta nova ou vazia.",
                         f"{target} already exists and has files: choose a new or empty folder."))
        slug = projects.slug_of(nome, set())
        pdfs = [rel for rel in files if rel.lower().endswith(".pdf")]
        await asyncio.to_thread(projects.create_from_files, target, nome, slug, formato, idioma, files,
                                pdfs[0] if pdfs else "")
        lines, taken, extracted = [], set(), []
        for pdf in pdfs:
            out = projects.slug_of(Path(pdf).stem, taken | {slug}) if len(pdfs) > 1 else slug
            taken.add(out)
            extracted.append(out)
            info = await projects.extract(target / "context" / pdf, target / "context" / out)
            lines.append(t(f"- context/{pdf}: texto em context/{out}/texto.md, figuras em context/{out}/figuras "
                           f"({info.get('pages', '?')} páginas)",
                           f"- context/{pdf}: text in context/{out}/texto.md, figures in context/{out}/figuras "
                           f"({info.get('pages', '?')} pages)"))
        projects.point_to_sources(target, slug, {pdf: out for pdf, out in zip(pdfs, extracted)})
        lines += [f"- context/{rel}" for rel in files if rel not in pdfs]
        _current["path"] = target
        return (t(f"Projeto criado em {target}.", f"Project created in {target}.") + "\n" + "\n".join(lines) + "\n" +
                t("Agora siga a skill deck-studio:criar-apresentacao neste projeto (as ferramentas já trabalham nele).",
                  "Now follow the deck-studio:criar-apresentacao skill in this project (the tools already work on it)."))
    return await guarded(job())


@mcp.tool()
async def construir(projeto: str = "") -> str:
    """Constrói o deck do editor (deck/build/studio/deck.html) e diz os erros do build."""
    async def job():
        st = state_of(projeto)
        build = await st.builder.build_studio()
        if build["ok"]:
            return t(f"Build sem erros em {build['ms']} ms.", f"Built with no errors in {build['ms']} ms.")
        return t("Erro: o build falhou:\n", "Error: the build failed:\n") + build["error"]
    return await guarded(job())


@mcp.tool()
async def screenshot_slide(slide: int, step: int | None = None, highlightLoc: str = "", projeto: str = ""):
    """Um PNG do slide (1-based) como a plateia vê, a 1600x900, no passo pedido (padrão: o último, com tudo à mostra).
    highlightLoc: um data-loc (arquivo:linha:coluna) cujo elemento ganha um contorno laranja. Olhe depois de cada
    edição e corrija o que transborda ou se sobrepõe."""
    async def job():
        st = state_of(projeto)
        png, label = await st.extras["renderer"].screenshot(slide, step, [highlightLoc] if highlightLoc else [])
        return [label, Image(data=png, format="png")]
    return await guarded(job())


@mcp.tool()
async def check_slide(slide: int, step: int | None = None, projeto: str = "") -> str:
    """Confere um slide: caixas que cortam o conteúdo e elementos fora do quadro 1600x900, cada um com o data-loc."""
    async def job():
        problems, label = await state_of(projeto).extras["renderer"].check(slide, step)
        if not problems:
            return label[:-1] + t(": nada cortado e nada fora do quadro.", ": nothing clipped and nothing outside the frame.")
        return (label[:-1] + t(f": {len(problems)} problema(s).", f": {len(problems)} problem(s).") + "\n"
                + "\n".join(f"- {p}" for p in problems))
    return await guarded(job())


@mcp.tool()
async def add_image(contextFile: str, name: str = "", projeto: str = "") -> str:
    """Copia uma imagem de context/ para as imagens do deck, com um nome seguro, e devolve a tag <img> do slide."""
    async def job():
        st = state_of(projeto)
        context = (st.kit_root / st.config["contextDir"]).resolve()
        source = (context / contextFile).resolve()
        if not (source.is_relative_to(context) and source.is_file()):
            raise Tool(t(f"A imagem tem de ser um arquivo de context/; {contextFile} não é.",
                         f"The image must be a file in context/; {contextFile} is not."))
        ext = IMAGE_TYPES.get(source.suffix.lower())
        if not ext:
            raise Tool(t(f"Só png, jpg, webp ou svg vão num slide; {source.name} não é.",
                         f"Only png, jpg, webp or svg go on a slide; {source.name} is not one."))
        images = st.kit_root / st.config["imagesDir"]
        stem = projects.slug_of(Path(name or source.name).stem, set())
        target, n = images / f"{stem}{ext}", 1
        while target.exists():
            n += 1
            target = images / f"{stem}-{n}{ext}"
        images.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        rel = Path(os.path.relpath(target, st.kit_root / Path(st.config["slidesDir"]).parent)).as_posix()
        return t(f"Copiada para {target.relative_to(st.kit_root).as_posix()}. No slide: ",
                 f"Copied to {target.relative_to(st.kit_root).as_posix()}. On a slide: ") + f'<img src="{rel}" alt="...">.'
    return await guarded(job())


@mcp.tool()
async def run_qa(which: str = "all", projeto: str = "") -> str:
    """Build limpo (deck/dist/deck.html) e o QA do projeto: check (qa/check_deck.py), audit (qa/audit_numbers.py:
    todo número tem fonte) e shoot (qa/shoot.py: a folha de contato). which: all, check, audit ou shoot. Corrija cada
    FAIL e cada UNMATCHED."""
    async def job():
        st = state_of(projeto)
        names = list(QA) if which == "all" else [which]
        if any(n not in QA for n in names):
            raise Tool(t("which é all, check, audit ou shoot.", "which is all, check, audit or shoot."))
        async with st.builder.lock:
            code, out, _ = await run_command(st.config, st.config["cleanBuild"])
        if code != 0:
            return t("Erro: o build limpo falhou:\n", "Error: the clean build failed:\n") + out[-3000:]
        parts = []
        for n in names:
            code, out, ms = await run_command(st.config, [sys.executable, "-I", "-X", "utf8", QA[n]])
            parts.append(f"## {QA[n]} (saída {code}, {ms} ms)\n{out.strip()[-4000:]}")
        return "\n\n".join(parts)
    return await guarded(job())


@mcp.tool()
async def compile_beamer(path: str = "", projeto: str = "") -> str:
    """Compila o Beamer escrito à mão (padrão: beamer/apresentacao/apresentacao.tex). Devolve JSON {ok, pages, errors,
    boxes}: corrija os erros e os overfull boxes acima de 1 pt."""
    async def job():
        st = state_of(projeto)
        result = await beamer.deck_for(st, path or None).full()
        return json.dumps(result, ensure_ascii=False)
    return await guarded(job())


@mcp.tool()
async def screenshot_beamer_page(page: int, path: str = "", projeto: str = ""):
    """Um PNG de uma página do Beamer como a última compilação a fez, com 1600 px de largura."""
    async def job():
        st = state_of(projeto)
        deck = beamer.deck_for(st, path or None)
        view = deck.current()
        if not view:
            raise Tool(t(f"{deck.rel} ainda não foi compilado: chame compile_beamer.",
                         f"{deck.rel} is not compiled yet: call compile_beamer."))
        if not 1 <= page <= view["pages"]:
            raise Tool(t(f"{deck.rel} tem {view['pages']} páginas.", f"{deck.rel} has {view['pages']} pages."))
        png = await asyncio.to_thread(engine.render_page, view["pdf"], page, round(1600 * 72 / view["width"]))
        return [t(f"Página {page} de {view['pages']} de {deck.rel}.", f"Page {page} of {view['pages']} of {deck.rel}."),
                Image(data=png, format="png")]
    return await guarded(job())


@mcp.tool()
async def exportar(formato: str = "", projeto: str = "") -> str:
    """Exporta: formato "pdf", o PDF do deck HTML (deck/dist/deck.pdf); formato "overleaf", o zip do Beamer
    (beamer/apresentacao) para subir no Overleaf, conferido compilando uma cópia sozinha. Sem formato, o do projeto."""
    async def job():
        st = state_of(projeto)
        if formato not in ("", "pdf", "overleaf"):
            raise Tool(t('formato é "pdf" ou "overleaf".', 'formato is "pdf" or "overleaf".'))
        if formato == "overleaf" or (not formato and st.config.get("format") == "beamer"):  # checked by a lone copy
            deck = beamer.deck_for(st, None)
            r = await deck.full()
            view = deck.current()
            if not r["ok"] or not view:
                return t("Erro: o Beamer não compila agora: chame compile_beamer e corrija os erros.",
                         "Error: the Beamer deck does not compile now: call compile_beamer and fix the errors.")
            zip_path, names = await asyncio.to_thread(overleaf.build, deck.main, view["pdf"], st.kit_root / "exports",
                                                      deck.work)
            c = await asyncio.to_thread(overleaf.check, zip_path, deck.main.name)
            head = t(f"Zip do Overleaf: {zip_path} ({len(names)} arquivos). ", f"Overleaf zip: {zip_path} ({len(names)} files). ")
            if c["ok"]:
                return head + t("Uma cópia compilou sozinha, sem nenhum [?].", "A copy compiled on its own, with no [?].")
            return head + t(f"A cópia sozinha falhou: {c}", f"The copy on its own failed: {c}")
        name = "export-pdf"
        commands = st.config["jobs"].get(name)
        if not commands:
            raise Tool(t('Este projeto não tem o PDF do deck HTML: use formato "overleaf".',
                         'This project has no PDF of the HTML deck: use formato "overleaf".'))
        for argv in commands:
            code, out, _ = await run_command(st.config, argv)
            if code != 0:
                return t(f"Erro: {name} falhou:\n", f"Error: {name} failed:\n") + out[-3000:]
        out_file = st.config["jobOutputs"].get(name)
        return t(f"{name} pronto", f"{name} done") + (f": {st.kit_root / out_file}" if out_file else ".")
    return await guarded(job())


@mcp.tool()
async def publicar(site: str = "", projeto: str = "") -> str:
    """Publica o deck HTML no Netlify, como um site de uma página com noindex, pelo login do Netlify deste computador
    (`netlify login`, da Netlify CLI). site: o nome do site novo (fica NOME.netlify.app), só na primeira vez; depois o
    projeto lembra o site cadastrado (deck/tools/netlify-site.json). O deck fica público nesse endereço: confirme com o
    autor antes de chamar."""
    async def job():
        st = state_of(projeto)
        script = "deck/tools/publish_netlify.py"
        if not (st.kit_root / script).is_file():
            raise Tool(t("Este projeto não publica no Netlify (falta deck/tools/publish_netlify.py): só os decks HTML do "
                         "modelo de projeto.", "This project does not publish on Netlify (no deck/tools/publish_netlify.py): "
                         "only the HTML decks of the project template do."))
        steps = []
        if not (st.kit_root / "deck/tools/netlify-site.json").is_file():
            if not site:
                raise Tool(t("Diga o nome do site novo (ele fica NOME.netlify.app) para cadastrar o projeto.",
                             "Give the new site's name (it becomes NAME.netlify.app) to register the project."))
            steps.append([sys.executable, "-I", script, "register", "--name", site, "--create"])
        steps += [st.config["cleanBuild"], [sys.executable, "-I", script]]
        out = ""
        for argv in steps:
            code, out, _ = await run_command(st.config, argv)
            if code != 0:
                return t("Erro: a publicação parou em ", "Error: publishing stopped at ") + \
                    f"`{' '.join(argv[2:]) or argv[0]}`:\n{out[-2000:]}"
        return out.strip()[-1500:]
    return await guarded(job())


@mcp.tool()
async def verificar(idioma: str = "pt") -> str:
    """Confere o que o plugin precisa nesta máquina (Python, Chromium do Playwright, Node, TeX, Perl) e diz como
    instalar o que falta. Instala o Chromium do Playwright se ele faltar (download gratuito). idioma: pt ou en, o
    idioma em que o autor escreve."""
    LANG.set("en" if idioma == "en" else "pt")
    lines = [f"Python {sys.version.split()[0]}" + t(" em ", " in ") + sys.executable]
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            await (await p.chromium.launch()).close()
        lines.append(t("Chromium do Playwright: ok", "Playwright's Chromium: ok"))
    except Exception:
        code, out, _ = await run_command({"kitRoot": os.getcwd()},
                                         [sys.executable, "-m", "playwright", "install", "chromium"])
        lines.append(t("Chromium do Playwright: instalado agora", "Playwright's Chromium: installed now") if code == 0 else
                     t(f"Chromium do Playwright: falhou ao instalar ({out[-500:]}). No Linux: ",
                       f"Playwright's Chromium: the install failed ({out[-500:]}). On Linux: ")
                     + t("`uv run playwright install --with-deps chromium` (pede sudo).",
                         "`uv run playwright install --with-deps chromium` (asks for sudo)."))
    for tool, how in [("node", t("Node LTS (nodejs.org; no Ubuntu, sudo apt install nodejs npm): só para o exemplo",
                                 "Node LTS (nodejs.org; on Ubuntu, sudo apt install nodejs npm): for the example only")),
                      ("pdflatex", t("TeX: MiKTeX no Windows; no Ubuntu, sudo apt install texlive-latex-extra latexmk",
                                     "TeX: MiKTeX on Windows; on Ubuntu, sudo apt install texlive-latex-extra latexmk")),
                      ("perl", t("Perl (para o latexmk): vem no Git for Windows; no Ubuntu, sudo apt install perl",
                                 "Perl (for latexmk): comes with Git for Windows; on Ubuntu, sudo apt install perl"))]:
        found = shutil.which(tool)
        lines.append(f"{tool}: {found}" if found else f"{tool}: " + t("falta. ", "missing. ") + how)
    return "\n".join(lines)


EXAMPLE = Path(__file__).resolve().parents[2] / "templates" / "exemplo-nexus-go"


@mcp.tool()
async def abrir_exemplo(pasta: str = "") -> str:
    """Copia o deck de exemplo (a defesa NEXUS-GO, com o método completo: storyline, fatos, componentes interativos,
    QA e Beamer) para uma pasta nova e o deixa pronto para abrir. pasta: o destino (padrão: <pasta da sessão>/
    exemplo-nexus-go). Precisa do Node para construir."""
    async def job():
        target = Path(pasta).expanduser().resolve() if pasta else Path(os.getcwd()) / "exemplo-nexus-go"
        if target.exists() and any(target.iterdir()):
            raise Tool(t(f"{target} já existe e tem arquivos: escolha uma pasta nova ou vazia.",
                         f"{target} already exists and has files: choose a new or empty folder."))
        await asyncio.to_thread(shutil.copytree, EXAMPLE, target, dirs_exist_ok=True)
        _current["path"] = target
        npm = shutil.which("npm")
        if not npm:
            return t(f"Exemplo copiado para {target}. Falta o Node (nodejs.org) para construir o deck: instale e rode "
                     "`npm ci` em deck/.", f"Example copied to {target}. Node (nodejs.org) is missing to build the deck: "
                     "install it and run `npm ci` in deck/.")
        code, out, _ = await run_command({"kitRoot": str(target / "deck")}, [npm, "ci", "--no-audit", "--no-fund"])
        if code != 0:
            return t(f"Exemplo copiado para {target}, mas o `npm ci` falhou:\n",
                     f"Example copied to {target}, but `npm ci` failed:\n") + out[-1500:]
        build = await state_of(str(target)).builder.build_studio()
        return (t(f"Exemplo pronto em {target}", f"Example ready in {target}")
                + ("." if build["ok"] else t(", mas o build falhou:\n", ", but the build failed:\n") + build["error"])
                + t(" Abra o editor (abrir_editor) para ver, ou leia docs/STORYLINE.md para o método.",
                    " Open the editor (abrir_editor) to see it, or read docs/STORYLINE.md for the method."))
    return await guarded(job())


_editor = Editor()


@mcp.tool()
async def abrir_editor(projeto: str = "") -> str:
    """Abre o editor visual do projeto no navegador do autor: o deck com cada caixa clicável e um painel de chat. O autor
    seleciona caixas, escreve o que mudar e envia (o painel fala o idioma do deck: "Enviar ao Claude" ou "Send to
    Claude"). Com o Claude Code aberto com o canal do plugin, a mensagem chega como <channel>; sem ele, leia com
    ler_selecao quando o autor pedir."""
    async def job():
        st = state_of(projeto)
        build = await st.builder.build_studio()
        if not build["ok"]:
            return t("Erro: o build falhou:\n", "Error: the build failed:\n") + build["error"]
        url = _editor.open(st.kit_root)
        if not os.environ.get("DECK_NO_BROWSER"):
            webbrowser.open(url)
        return t(f"Editor aberto em {url} (só neste computador). Peça ao autor para selecionar e enviar.",
                 f"Editor open at {url} (this computer only). Ask the author to select and send.")
    return await guarded(job())


@mcp.tool()
async def ler_selecao() -> str:
    """O que o autor mandou pelo editor visual: as caixas (loc = arquivo:linha:coluna da fonte, o texto, o slide e o
    passo) e o pedido. Edite as fontes nesses locs, depois construir, screenshot_slide e check_slide."""
    sel = _editor.read()
    if not sel:
        return t("Nada foi enviado ainda: chame abrir_editor e peça ao autor para clicar nas caixas e enviar.",
                 "Nothing was sent yet: call abrir_editor and ask the author to click the boxes and send.")
    return json.dumps(sel, ensure_ascii=False, indent=1)


@mcp.tool()
async def responder_no_editor(texto: str) -> str:
    """Escreve no painel de chat do editor visual: a resposta ao que o autor mandou por lá (as mensagens dele chegam
    como <channel>). Curta, no idioma dele: o que mudou e em qual slide, ou a pergunta que falta."""
    if not _editor.say("claude", texto):
        return t("Erro: o editor não está aberto (chame abrir_editor).", "Error: the editor is not open (call abrir_editor).")
    return "ok"


_channel = {}  # the event loop and the stdio write stream, for push()


def push(content, meta):
    """Called from the editor's thread: puts the author's message into this Claude Code session, as a channel event
    (https://code.claude.com/docs/en/channels-reference). The session drops it silently if it did not load this server
    as a channel, so the panel also tells the author how to start Claude Code with it."""
    loop, write = _channel.get("loop"), _channel.get("write")
    if not loop:
        return False
    note = JSONRPCNotification(jsonrpc="2.0", method="notifications/claude/channel", params={"content": content, "meta": meta})
    sent = asyncio.run_coroutine_threadsafe(write.send(SessionMessage(note)), loop)
    try:
        sent.result(5)
    except BaseException:
        sent.cancel()
        raise
    return True


async def serve():
    """MCPServer.run("stdio"), with two changes for the channel: the claude/channel capability, and the handshake era
    only. Claude Code does not register as a channel a server that connects on protocol revision 2026-07-28 (its v2 MCP
    runtime asks stdio servers for it); a server that does not serve that revision connects on the handshake, where
    channel events work (https://code.claude.com/docs/en/mcp#push-messages-with-channels)."""
    low = mcp._lowlevel_server
    options = low.create_initialization_options(experimental_capabilities={"claude/channel": {}})
    async with stdio_server() as (read, write):
        _channel.update(loop=asyncio.get_running_loop(), write=write)
        async with low.lifespan(low) as state:
            await _serve_legacy_stream(low, read, write, lifespan_state=state, session_id=None, init_options=options,
                                       raise_exceptions=False)


_editor.push = push


def main():
    asyncio.run(serve())
