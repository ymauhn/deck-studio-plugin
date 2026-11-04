"""Beamer mode (docs/PYTHON.md "Beamer mode"): the kit's Beamer projects as pages whose clicks select sources.

- A hand-written project compiles in the background into data_dir/beamer/<id>, one compile at a time, full compiles
  coalesced. Each compile that makes a PDF becomes the project's view: a copy of that PDF and its SyncTeX, which
  pages and clicks read while the next compile writes.
- The generated deck is never compiled: its view is the kit's own PDF.
- `beamer` events: {project (as GET /api/beamer/projects lists it), scope: "full" | "frame", state: "running" | "ok"
  | "error"}."""
import asyncio
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pymupdf
from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse

from deck_studio.beamer import engine, overleaf
from deck_studio.server.api import ApiError, json_body

router = APIRouter()


def view_of(pdf, version, frame=None, offset=None):
    """What pages and clicks read: the PDF, its version (in page URLs), page count and page size in points."""
    with pymupdf.open(pdf) as d:
        r = d[0].rect
        return {"pdf": str(pdf), "version": version, "pages": d.page_count, "width": r.width, "height": r.height,
                "frame": frame, "offset": offset}


def kit_path(state, path):
    """A path as the UI and the agent see it: kit-relative with forward slashes."""
    p = Path(path)
    return p.relative_to(state.kit_root).as_posix() if p.is_relative_to(state.kit_root) else p.as_posix()


# "Overfull \hbox (30.0pt too wide) in paragraph at lines 4--4", "Underfull \vbox (badness 10000) detected at line 9"
BOX = re.compile(r"((?:Overfull|Underfull) \\[hv]box \((?:([\d.]+)pt too \w+|badness \d+)\))(?:.*? lines? (\d+))?")
TEX_NAME = re.compile(r"\.tex(?=[\s)\"]|$)", re.I)


def boxes_of(log, cwd):
    """The overfull boxes over 1 pt and the underfull ones of a TeX log, each {file, line, message} with TeX's words
    ("Overfull \\vbox (7.97742pt too high)"). The file is the one TeX was reading, from the log's file stack: "(<path>"
    opens a file and its ")" closes it (names relative to cwd); a box's contents, shown under it up to a blank line,
    are text. ponytail: a stray parenthesis elsewhere in the log's text shifts the stack; the file is then off."""
    out, stack, shown = [], [], False
    for text in log.split("\n"):
        if shown:
            shown = bool(text.strip())
            continue
        if m := BOX.match(text):
            shown = True
            if m[2] is None or float(m[2]) > 1:  # an underfull box has a badness, not a size
                out.append({"file": stack[-1] if stack else None, "line": m[3] and int(m[3]), "message": m[1]})
            continue
        for p in re.finditer(r"[()]", text):
            if p[0] == ")":
                del stack[-1:]
                continue
            rest = text[p.end():]
            stack.append(next((os.path.normpath(f) for e in TEX_NAME.finditer(rest)
                               if (f := Path(cwd, rest[:e.end()].strip('"'))).is_file()), None))
    return out


class Project:
    def __init__(self, state, found):
        self.state = state
        self.found = found
        self.kind, self.rel, self.main = found["kind"], found["rel"], Path(found["main"])
        self.id = re.sub(r"[^\w-]+", "-", self.rel.removeprefix("beamer/").removesuffix(".tex"))
        self.work = state.data_dir / "beamer" / self.id
        self.view = None
        self.last = None  # the last compile: {scope, ok, ms, errors}
        self.running = None  # the scope of the compile running
        self.starts = []  # the first page of each frame in the last good full compile, from its .nav
        self.compiled = None  # the sources' stamp when the last full compile started; None: never opened
        self.saving = False  # a frame save is writing: the compiles it starts itself follow
        self.lock = asyncio.Lock()
        self.queued = None  # the full compile not started yet
        self.tasks = set()

    def current(self):
        """The view: the last compile's, or for the generated deck the kit's PDF (Regenerar Beamer rewrites it)."""
        if self.kind == "generated":
            pdf = self.main.with_suffix(".pdf")
            version = str(pdf.stat().st_mtime_ns) if pdf.is_file() else None
            if version and (self.view or {}).get("version") != version:
                self.view = view_of(pdf, version)
        return self.view

    def public(self):
        view = self.current()
        return {"id": self.id, "kind": self.kind, "rel": self.rel, "last": self.last,
                "running": self.running or ("full" if self.queued else None),
                "view": view and {k: view[k] for k in ("version", "pages", "frame", "offset")}}

    def stamp(self):
        """The newest change to the project's .tex files."""
        return max((f.stat().st_mtime_ns for f in self.main.parent.rglob("*.tex")), default=0)

    def full(self):
        """A full compile that starts after this call, shared by every request made before it starts. The task's result:
        {ok, pages, errors, boxes}, each error and each box {file (kit-relative), line, message} (see boxes_of)."""
        if self.queued is None:
            self.queued = self._start(self._compile(None))
        return self.queued

    def frame(self, index):
        """Frame `index` of the main file compiled alone, a preview (about 1.5 s against 2.5 s or more for the whole
        deck), and then the whole deck."""
        return self._start(self._compile(index))

    def _start(self, coro):
        task = asyncio.ensure_future(coro)
        self.tasks.add(task)
        task.add_done_callback(self.tasks.discard)
        return task

    async def _compile(self, frame):
        async with self.lock:
            scope = "full" if frame is None else "frame"
            if frame is None:
                self.queued, self.compiled = None, self.stamp()
            self.running = scope
            await self.say(scope, "running")
            try:
                r = await asyncio.to_thread(engine.compile, self.found, self.work, frame)
            except Exception as e:  # noqa: BLE001 - no latexmk, say: the compile still ends, as an error
                r = {"ok": False, "pdf": None, "errors": [{"file": None, "line": None, "message": str(e)}], "ms": 0}
            finally:
                self.running = None
            nav = self.work / f"{self.main.stem}.nav"
            if r["ok"] and frame is None and nav.is_file():
                self.starts = [int(a) for a in re.findall(r"\\beamer@framepages \{(\d+)\}", nav.read_text("utf-8"))]
            if r["pdf"]:
                self._keep(Path(r["pdf"]), frame)
            log = self.work / f"{self.main.stem}.log"  # the whole deck's, which this compile wrote when it made a PDF
            boxes = boxes_of(log.read_text("utf-8", "replace"), self.main.parent) if (
                frame is None and r["pdf"] and log.is_file()) else []
            self.last = {"scope": scope, "ok": r["ok"], "ms": r["ms"],
                         "errors": [{**e, "file": e["file"] and kit_path(self.state, e["file"])} for e in r["errors"]]}
            await self.say(scope, "ok" if r["ok"] else "error")
            if frame is not None:  # a preview is always followed by the whole deck, so the view never stays on it
                self.full()
            return {"ok": r["ok"], "pages": self.view["pages"] if r["pdf"] else 0, "errors": self.last["errors"],
                    "boxes": [{**b, "file": b["file"] and kit_path(self.state, b["file"])} for b in boxes]}

    def _keep(self, pdf, frame):
        """A compile's PDF and SyncTeX, copied, become the view; older views go."""
        version = str(time.time_ns())
        copy = self.work / f"view-{version}.pdf"
        shutil.copyfile(pdf, copy)
        if pdf.with_suffix(".synctex.gz").is_file():
            shutil.copyfile(pdf.with_suffix(".synctex.gz"), copy.with_suffix(".synctex.gz"))
        offset = self.starts[frame] if frame is not None and frame < len(self.starts) else None  # its first deck page
        self.view = view_of(copy, version, frame, offset)
        for old in self.work.glob("view-*"):
            if not old.name.startswith(f"view-{version}."):
                try:
                    old.unlink()
                except OSError:  # being read right now: the next view removes it
                    pass

    async def say(self, scope, state):
        await self.state.events.publish("beamer", project=self.public(), scope=scope, state=state)


TITLE = re.compile(r"^\s*\\(?:begin\{frame\}(?:<[^>]*>|\[[^\]]*\])*|frametitle(?:<[^>]*>)?)\{(.*)\}", re.M)


def source_of(path, frame):
    """A frame's lines, with LF line ends as a textarea gives them back, and its title as written."""
    lines = Path(path).read_bytes().decode("utf-8").split("\n")[frame["start"] - 1:frame["end"]]
    text = "\n".join(line.removesuffix("\r") for line in lines)
    title = TITLE.search(re.sub(r"(?<!\\)%.*", "", text))
    return {**frame, "text": text, "title": title[1].strip() if title else ""}


def discover(state):
    """The kit's projects, found again on each call; a project keeps its state (compiles, view) by id."""
    known = state.extras.setdefault("beamer", {})
    out = []
    for found in engine.discover_projects(state.kit_root):
        p = Project(state, found)
        out.append(known.setdefault(p.id, p))
    return out


def project_of(state, pid):
    p = state.extras.get("beamer", {}).get(pid) or next((p for p in discover(state) if p.id == pid), None)
    if not p:
        raise ApiError(404, "no-project", "Projeto Beamer não encontrado.")
    return p


def deck_for(state, path=None):
    """The hand-written deck whose main .tex is `path` (kit-relative), else the config's beamerStart, else the only
    one: what the start mode and the agent's tools open. ValueError with the reason, for the agent."""
    decks = [p for p in discover(state) if p.kind == "handwritten"]
    names = ", ".join(p.rel for p in decks) or "none"
    want = path or state.config.get("beamerStart")
    if not want:
        if len(decks) != 1:
            raise ValueError(f"Name the deck with path; the hand-written Beamer decks here: {names}.")
        return decks[0]
    p = next((p for p in decks if p.main.resolve() == (state.kit_root / want).resolve()), None)
    if not p:
        raise ValueError(f"{want} is not a hand-written Beamer deck; the ones here: {names}.")
    return p


def tex_of(state, p, file):
    """The path of one of the project's .tex files, from its kit-relative name; nothing else."""
    path = (state.kit_root / file).resolve()
    if path.suffix != ".tex" or not path.is_relative_to(p.main.parent.resolve()):
        raise ApiError(400, "bad-file", "Aqui só valem os arquivos .tex deste projeto.")
    return path


async def watch(state):
    """After each tool call of an agent turn (the author watches the deck being written), and whenever the turn lock is
    free again (an agent turn, an edit or an undo ended), each opened hand-written project whose .tex files changed
    since its last full compile compiles again."""
    async for e in state.events.stream():
        tool_ended = e["type"] == "chat" and e.get("kind") == "tool" and e.get("state") != "running"
        if not (tool_ended or (e["type"] == "status" and not e["busy"])):
            continue
        for p in list(state.extras.get("beamer", {}).values()):
            try:
                if p.compiled is not None and not p.saving and p.stamp() != p.compiled:
                    p.full()
            except OSError:  # its folder went away: it stays as it was
                pass


async def startup(state):
    state.extras["beamer-watch"] = asyncio.create_task(watch(state))
    if state.config.get("startMode") == "beamer":  # a Beamer project opens on its deck: it compiles from the start
        try:
            deck_for(state).full()
        except ValueError:  # no such deck: the view lists what there is
            pass


async def shutdown(state):
    """The studio is closing: compiles waiting stop (the server's process tree takes latexmk with it)."""
    tasks = [state.extras.pop("beamer-watch"), *(t for p in state.extras.get("beamer", {}).values() for t in p.tasks)]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)


@router.get("/api/beamer/projects")
async def list_projects(request: Request):
    return [p.public() for p in discover(request.app.state.studio)]


@router.post("/api/beamer/projects/{pid}/open")
async def open_project(pid: str, request: Request):
    """A hand-written project compiles when its sources changed since its last full compile (and on the first open)."""
    p = project_of(request.app.state.studio, pid)
    if p.kind == "handwritten" and p.compiled != p.stamp():
        p.full()
    return p.public()


@router.post("/api/beamer/projects/{pid}/overleaf")
async def export_overleaf(pid: str, request: Request):
    """Exportar para o Overleaf: the deck's zip (beamer/overleaf.py) in the kit's exports/ folder, with the PDF of the
    last compile of the whole deck (a hand-written deck whose sources changed since compiles first), then the zip
    compiled again from an empty folder: {zip (kit-relative), files, check: {ok, errors, undefined}}."""
    state = request.app.state.studio
    p = project_of(state, pid)
    view = p.current()
    if p.kind == "handwritten" and (p.compiled != p.stamp() or not view or view["frame"] is not None):
        r = await p.full()
        view = p.current()
        if not r["ok"] or not view:
            raise ApiError(409, "not-compiled", "O deck não compila agora: corrija os erros antes de exportar.")
    if not view:
        raise ApiError(409, "no-pdf", "Este deck ainda não tem PDF: gere-o antes de exportar.")
    zip_path, names = await asyncio.to_thread(overleaf.build, p.main, view["pdf"], state.kit_root / "exports", p.work)
    result = await asyncio.to_thread(overleaf.check, zip_path, p.main.name)
    return {"zip": zip_path.relative_to(state.kit_root).as_posix(), "files": len(names), "check": result}


@router.post("/api/beamer/exports/open")
async def open_exports(request: Request):
    """Abrir pasta: the kit's exports/ folder in the system's file manager (only that folder)."""
    folder = request.app.state.studio.kit_root / "exports"
    folder.mkdir(exist_ok=True)
    if sys.platform == "win32":
        os.startfile(folder)  # a folder of this kit, in Explorer
    else:
        subprocess.Popen(["xdg-open", str(folder)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return {"folder": str(folder)}


@router.get("/api/beamer/projects/{pid}/pages/{n}")
async def page_png(pid: str, n: int, v: str, w: int, request: Request):
    """Page n of the view with version v, as a PNG w pixels wide."""
    view = project_of(request.app.state.studio, pid).current()
    if not view or view["version"] != v or not 1 <= n <= view["pages"]:
        raise ApiError(404, "no-page", "Esta página não existe mais.")
    dpi = round(min(max(w, 16), 4000) * 72 / view["width"])
    png = await asyncio.to_thread(engine.render_page, view["pdf"], n, dpi)
    return Response(png, media_type="image/png", headers={"Cache-Control": "private, max-age=31536000, immutable"})


@router.get("/api/beamer/projects/{pid}/pdf")
async def view_pdf(pid: str, v: str, request: Request):
    """The view with version v as a PDF, when it is the whole deck (not a frame's preview): the Abrir PDF link."""
    p = project_of(request.app.state.studio, pid)
    view = p.current()
    if not view or view["version"] != v or view["frame"] is not None:
        raise ApiError(404, "no-pdf", "Este PDF não existe mais. Abra o da última compilação.")
    return FileResponse(view["pdf"], media_type="application/pdf", filename=f"{p.main.stem}.pdf",
                        content_disposition_type="inline", headers={"Cache-Control": "no-store"})


@router.post("/api/beamer/projects/{pid}/click")
async def click(pid: str, request: Request):
    """{page, x, y}, x and y as fractions of the page. A hand-written deck: the TeX line there (engine.locate) as a
    selection, with its frame's source. The generated deck: {slide, step, x, y}, the same point of the HTML slide
    (1600 x 900), where the UI selects through the deck's picker."""
    state = request.app.state.studio
    p = project_of(state, pid)
    body = await json_body(request)
    view, n, fx, fy = p.current(), body.get("page"), body.get("x"), body.get("y")
    if not (view and type(n) is int and 1 <= n <= view["pages"]
            and all(type(v) in (int, float) and 0 <= v <= 1 for v in (fx, fy))):
        raise ApiError(400, "bad-click", "Clique fora da página.")
    x, y = fx * view["width"], fy * view["height"]
    if p.kind == "generated":
        pages = await asyncio.to_thread(engine.page_map, state.kit_root)
        if n > len(pages):
            raise ApiError(404, "no-slide", "Esta página não corresponde a um slide do HTML.")
        return {"slide": pages[n - 1]["n"], "step": pages[n - 1]["step"], **engine.pdf_to_html(x, y)}
    hit = await asyncio.to_thread(engine.locate, view["pdf"], n, x, y)
    if not hit:
        raise ApiError(404, "no-source", "Este ponto da página não tem um lugar na fonte.")
    file = kit_path(state, hit["file"])
    source = hit["frame"] and {"file": file, **source_of(hit["file"], hit["frame"])}
    in_deck = view["offset"] + n - 1 if view["frame"] is not None and view["offset"] else n  # a frame preview's page
    return {"selection": {"kind": "tex", "file": file, "frame": hit["frame"], "line": hit["line"], "text": hit["text"],
                          "page": in_deck, "title": source["title"] if source else ""},
            "source": source}


@router.post("/api/beamer/projects/{pid}/frame")
async def save_frame(pid: str, request: Request):
    """{file, start, oldText, newText}: the frame at line `start` of one of the project's .tex files becomes newText,
    as one undoable turn (EditService). Then a frame of the main file compiles alone, a fast preview, and then the
    whole deck."""
    state = request.app.state.studio
    p = project_of(state, pid)
    body = await json_body(request)
    file, start, old, new = body.get("file"), body.get("start"), body.get("oldText"), body.get("newText")
    if not (p.kind == "handwritten" and isinstance(file, str) and type(start) is int
            and isinstance(old, str) and isinstance(new, str)):
        raise ApiError(400, "bad-edit", "Pedido de edição incompleto.")
    path = tex_of(state, p, file)
    lines = new.replace("\r\n", "\n").strip("\n").split("\n")
    if engine.frames("\n".join(lines)) != [{"start": 1, "end": len(lines)}]:
        raise ApiError(422, "not-a-frame", "O texto precisa ser um frame só, de \\begin{frame} até \\end{frame}.")

    def change(text):
        rows = text.split("\n")
        frame = next((f for f in engine.frames(text) if f["start"] == start), None)
        now = frame and "\n".join(r.removesuffix("\r") for r in rows[start - 1:frame["end"]])
        if now != old.replace("\r\n", "\n"):
            raise ApiError(409, "stale", "O frame mudou desde que foi aberto. Clique nele de novo e refaça a mudança.")
        eol = "\r" if rows[start - 1].endswith("\r") else ""  # the file's own line ends
        rows[start - 1:frame["end"]] = [line + eol for line in lines]
        return "\n".join(rows)

    p.saving = True  # the turn's end wakes the watcher; this save starts its own compiles, in its own order
    try:
        turn_id = await state.edits.apply(f"Frame editado em {path.name}:{start}", {file: change})
    finally:
        p.saving = False
    if path == p.main.resolve():
        p.frame([f["start"] for f in engine.frames(p.main.read_bytes().decode("utf-8"))].index(start))
    else:  # a frame in an \input file: no preview of its own
        p.full()
    return {"turnId": turn_id, "frame": {"start": start, "end": start + len(lines) - 1}}


@router.get("/api/beamer/projects/{pid}/frame")
async def frame_source(pid: str, file: str, line: int, request: Request):
    """The frame around `line` of one of the project's .tex files as it is now: the pane follows changes made elsewhere."""
    state = request.app.state.studio
    path = tex_of(state, project_of(state, pid), file)
    text = path.read_bytes().decode("utf-8") if path.is_file() else ""
    frame = next((f for f in engine.frames(text) if f["start"] <= line <= f["end"]), None)
    if not frame:
        raise ApiError(404, "no-frame", "Este frame não existe mais.")
    return {"file": file, **source_of(path, frame)}
