"""The plugin's MCP server "deck" (stdio): the Deck Studio tools for the Claude Code session itself. Each project is
a folder made from the template (it has a studio.json); a tool works on `projeto`, else on the last project used,
else on the session's folder. The deck_studio package beside this one is a copy made by scripts/montar_plugin.py."""
import asyncio
import hashlib
import json
import os
import shutil
import sys
import webbrowser
from pathlib import Path

from mcp.server.mcpserver import Image, MCPServer

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
    "Comece com novo_projeto; a skill deck-studio:criar-apresentacao conduz o método. Responda ao autor em português."))
_states, _current = {}, {"path": None}


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
        raise Tool(f"{path} não é um projeto do Deck Studio (falta o studio.json). Crie um com novo_projeto, ou passe "
                   "a pasta do projeto em `projeto`.")
    _current["path"] = path
    return path


def state_of(projeto=None):
    path = project_of(projeto)
    if path not in _states:
        st = StudioState(load_config(path), data_dir(path), port=0)
        st.extras["renderer"] = Renderer(st)
        _states[path] = st
    return _states[path]


async def guarded(job):
    try:
        return await job
    except Tool as e:
        return f"Erro: {e}"
    except FileNotFoundError:
        return "Erro: o deck ainda não foi construído: chame construir."
    except ValueError as e:
        return f"Erro: {e}"


@mcp.tool()
async def novo_projeto(fonte: str, nome: str, pasta: str = "", idioma: str = "pt", formato: str = "html") -> str:
    """Cria um projeto de apresentação a partir de um PDF ou de uma pasta (PDFs, .md, .tex, .bib, imagens). fonte: o
    caminho do PDF ou da pasta. nome: o título. pasta: onde criar (padrão: <pasta da sessão>/<nome>). idioma: pt ou en.
    formato: html ou beamer. Cada PDF é extraído (texto, figuras, legendas) em context/<slug>/."""
    async def job():
        src = Path(fonte).expanduser().resolve()
        if idioma not in projects.LANGUAGES or formato not in projects.FORMATS:
            raise Tool("idioma é pt ou en, e formato é html ou beamer.")
        files = {}
        if src.is_file():
            if src.suffix.lower() != ".pdf":
                raise Tool("A fonte é um PDF ou uma pasta.")
            files[projects.pdf_name(src.name)] = src.read_bytes()
        elif src.is_dir():
            for f in sorted(p for p in src.rglob("*") if p.is_file() and p.suffix.lower() in KEPT):
                files[f.relative_to(src).as_posix()] = f.read_bytes()
        else:
            raise Tool(f"Não achei {fonte}.")
        if not files or sum(map(len, files.values())) > LIMIT:
            raise Tool("A fonte não tem arquivos que servem, ou passa de 100 MB.")
        target = Path(pasta).expanduser().resolve() if pasta else Path(os.getcwd()) / projects.slug_of(nome, set())
        if target.exists() and any(target.iterdir()):
            raise Tool(f"{target} já existe e tem arquivos: escolha uma pasta nova ou vazia.")
        slug = projects.slug_of(nome, set())
        pdfs = [rel for rel in files if rel.lower().endswith(".pdf")]
        await asyncio.to_thread(projects.create_from_files, target, nome, slug, formato, idioma, files,
                                pdfs[0] if pdfs else "")
        lines, taken = [], set()
        for pdf in pdfs:
            out = projects.slug_of(Path(pdf).stem, taken | {slug}) if len(pdfs) > 1 else slug
            taken.add(out)
            info = await projects.extract(target / "context" / pdf, target / "context" / out)
            lines.append(f"- context/{pdf}: texto em context/{out}/texto.md, figuras em context/{out}/figuras "
                         f"({info.get('pages', '?')} páginas)")
        lines += [f"- context/{rel}" for rel in files if rel not in pdfs]
        _current["path"] = target
        return (f"Projeto criado em {target}.\n" + "\n".join(lines) +
                "\nAgora siga a skill deck-studio:criar-apresentacao neste projeto (as ferramentas já trabalham nele).")
    return await guarded(job())


@mcp.tool()
async def construir(projeto: str = "") -> str:
    """Constrói o deck do editor (deck/build/studio/deck.html) e diz os erros do build."""
    async def job():
        st = state_of(projeto)
        build = await st.builder.build_studio()
        return f"Build sem erros em {build['ms']} ms." if build["ok"] else f"Erro: o build falhou:\n{build['error']}"
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
            return f"{label[:-1]}: nada cortado e nada fora do quadro."
        return f"{label[:-1]}: {len(problems)} problema(s).\n" + "\n".join(f"- {p}" for p in problems)
    return await guarded(job())


@mcp.tool()
async def add_image(contextFile: str, name: str = "", projeto: str = "") -> str:
    """Copia uma imagem de context/ para as imagens do deck, com um nome seguro, e devolve a tag <img> do slide."""
    async def job():
        st = state_of(projeto)
        context = (st.kit_root / st.config["contextDir"]).resolve()
        source = (context / contextFile).resolve()
        if not (source.is_relative_to(context) and source.is_file()):
            raise Tool(f"A imagem tem de ser um arquivo de context/; {contextFile} não é.")
        ext = IMAGE_TYPES.get(source.suffix.lower())
        if not ext:
            raise Tool(f"Só png, jpg, webp ou svg vão num slide; {source.name} não é.")
        images = st.kit_root / st.config["imagesDir"]
        stem = projects.slug_of(Path(name or source.name).stem, set())
        target, n = images / f"{stem}{ext}", 1
        while target.exists():
            n += 1
            target = images / f"{stem}-{n}{ext}"
        images.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        rel = Path(os.path.relpath(target, st.kit_root / Path(st.config["slidesDir"]).parent)).as_posix()
        return f'Copiada para {target.relative_to(st.kit_root).as_posix()}. No slide: <img src="{rel}" alt="...">.'
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
            raise Tool("which é all, check, audit ou shoot.")
        async with st.builder.lock:
            code, out, _ = await run_command(st.config, st.config["cleanBuild"])
        if code != 0:
            return f"Erro: o build limpo falhou:\n{out[-3000:]}"
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
            raise Tool(f"{deck.rel} ainda não foi compilado: chame compile_beamer.")
        if not 1 <= page <= view["pages"]:
            raise Tool(f"{deck.rel} tem {view['pages']} páginas.")
        png = await asyncio.to_thread(engine.render_page, view["pdf"], page, round(1600 * 72 / view["width"]))
        return [f"Página {page} de {view['pages']} de {deck.rel}.", Image(data=png, format="png")]
    return await guarded(job())


@mcp.tool()
async def exportar(projeto: str = "") -> str:
    """Exporta o formato do projeto: o PDF do deck HTML (deck/dist/deck.pdf) ou o zip do Overleaf do Beamer."""
    async def job():
        st = state_of(projeto)
        if st.config.get("format") == "beamer":  # the Overleaf zip, checked by compiling a copy alone
            deck = beamer.deck_for(st, None)
            r = await deck.full()
            view = deck.current()
            if not r["ok"] or not view:
                return "Erro: o Beamer não compila agora: chame compile_beamer e corrija os erros."
            zip_path, names = await asyncio.to_thread(overleaf.build, deck.main, view["pdf"], st.kit_root / "exports",
                                                      deck.work)
            c = await asyncio.to_thread(overleaf.check, zip_path, deck.main.name)
            return (f"Zip do Overleaf: {zip_path} ({len(names)} arquivos). " +
                    ("Uma cópia compilou sozinha, sem nenhum [?]." if c["ok"] else f"A cópia sozinha falhou: {c}"))
        name, commands = next(iter(st.config["jobs"].items()))
        for argv in commands:
            code, out, _ = await run_command(st.config, argv)
            if code != 0:
                return f"Erro: {name} falhou:\n{out[-3000:]}"
        out_file = st.config["jobOutputs"].get(name)
        return f"{name} pronto" + (f": {st.kit_root / out_file}" if out_file else ".")
    return await guarded(job())


@mcp.tool()
async def verificar() -> str:
    """Confere o que o plugin precisa nesta máquina (Python, Chromium do Playwright, Node, TeX, Perl) e diz como
    instalar o que falta. Instala o Chromium do Playwright se ele faltar (download gratuito)."""
    lines = [f"Python {sys.version.split()[0]} em {sys.executable}"]
    try:
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            await (await p.chromium.launch()).close()
        lines.append("Chromium do Playwright: ok")
    except Exception:
        code, out, _ = await run_command({"kitRoot": os.getcwd()},
                                         [sys.executable, "-m", "playwright", "install", "chromium"])
        lines.append("Chromium do Playwright: instalado agora" if code == 0 else
                     f"Chromium do Playwright: falhou ao instalar ({out[-500:]}). No Linux: "
                     "`uv run playwright install --with-deps chromium` (pede sudo).")
    for tool, how in [("node", "Node LTS (nodejs.org; no Ubuntu, sudo apt install nodejs npm): só para o exemplo"),
                      ("pdflatex", "TeX: MiKTeX no Windows; no Ubuntu, sudo apt install texlive-latex-extra latexmk"),
                      ("perl", "Perl (para o latexmk): vem no Git for Windows; no Ubuntu, sudo apt install perl")]:
        found = shutil.which(tool)
        lines.append(f"{tool}: {found}" if found else f"{tool}: falta. {how}")
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
            raise Tool(f"{target} já existe e tem arquivos: escolha uma pasta nova ou vazia.")
        await asyncio.to_thread(shutil.copytree, EXAMPLE, target, dirs_exist_ok=True)
        _current["path"] = target
        npm = shutil.which("npm")
        if not npm:
            return (f"Exemplo copiado para {target}. Falta o Node (nodejs.org) para construir o deck: instale e rode "
                    "`npm ci` em deck/.")
        code, out, _ = await run_command({"kitRoot": str(target / "deck")}, [npm, "ci", "--no-audit", "--no-fund"])
        if code != 0:
            return f"Exemplo copiado para {target}, mas o `npm ci` falhou:\n{out[-1500:]}"
        build = await state_of(str(target)).builder.build_studio()
        return (f"Exemplo pronto em {target}" + ("." if build["ok"] else f", mas o build falhou:\n{build['error']}") +
                " Abra o editor (abrir_editor) para ver, ou leia docs/STORYLINE.md para o método.")
    return await guarded(job())


_editor = Editor()


@mcp.tool()
async def abrir_editor(projeto: str = "") -> str:
    """Abre o editor visual do projeto no navegador do autor: o deck com cada caixa clicável. O autor seleciona caixas,
    escreve o que mudar e clica em "Enviar ao Claude"; depois leia com ler_selecao."""
    async def job():
        st = state_of(projeto)
        build = await st.builder.build_studio()
        if not build["ok"]:
            return f"Erro: o build falhou:\n{build['error']}"
        url = _editor.open(st.kit_root)
        if not os.environ.get("DECK_NO_BROWSER"):
            webbrowser.open(url)
        return f"Editor aberto em {url} (só neste computador). Peça ao autor para selecionar e enviar."
    return await guarded(job())


@mcp.tool()
async def ler_selecao() -> str:
    """O que o autor mandou pelo editor visual: as caixas (loc = arquivo:linha:coluna da fonte, o texto, o slide e o
    passo) e o pedido. Edite as fontes nesses locs, depois construir, screenshot_slide e check_slide."""
    sel = _editor.read()
    if not sel:
        return "Nada foi enviado ainda: chame abrir_editor e peça ao autor para clicar nas caixas e enviar."
    return json.dumps(sel, ensure_ascii=False, indent=1)


def main():
    mcp.run("stdio")
