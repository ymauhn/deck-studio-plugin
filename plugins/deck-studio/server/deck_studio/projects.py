"""Projects (docs/IMPORT.md): the decks Deck Studio makes from a PDF, each in a folder of its own.

- The registry, <home>/projects.json: [{name, slug, path, format, language, created}], in the order they were made.
  The default kit is never in it. Writes are atomic.
- create(): a new project folder from templates/project, with its studio.json and the PDF in context/; extract()
  then writes the PDF's text and figures into context/<slug>/, in a process of its own.
- Studios: each project runs in a studio of its own, on the data dir <home>/projects/<slug> (the default kit's is
  the home itself). start() runs one as a child of this studio; running_url() reads the URL of one that runs.

Every studio started on a home (the default kit's and each project's) can import, so the slug and the registry are
decided across processes: reserve() makes the slug's data dir, and register() adds to the registry under a lock file."""
import asyncio
import collections
import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import unicodedata
import urllib.request
import uuid
from pathlib import Path, PureWindowsPath
from urllib.parse import parse_qs, urlsplit

from deck_studio.core import plataforma
from deck_studio.server.api import ApiError
from deck_studio.templates import fill_template

APP = Path(__file__).resolve().parents[1]  # the folder that holds deck_studio: `python -m deck_studio...` runs from it
BEAMER_START = "beamer/apresentacao/apresentacao.tex"
FORMATS = {"html": "HTML", "beamer": "Beamer"}  # and their names in the first request
# the slides' language: its html lang, its name in the project's CLAUDE.md, and in the first request (pt-BR)
LANGUAGES = {"pt": ("pt-BR", "Português (Brasil)", "português"), "en": ("en", "English", "inglês")}
# the first request, sent in the new project's studio; config["importMessage"] replaces it. Its fields: pdf, format
# (html | beamer), format_name (HTML | Beamer), language, text, figures
# the first request of a project made from a folder or several files: {files} is a list, one line per file
FOLDER_MESSAGE = ("Crie a apresentação a partir dos materiais em `context/`, no formato {format_name}, com os slides em "
                  "{language}. Os arquivos:\n{files}\nSiga a skill criar-apresentacao e o CLAUDE.md do projeto.")
MESSAGE = ("Crie a apresentação a partir do PDF `{pdf}`, no formato {format_name}, com os slides em {language}. O "
           "texto extraído está em `{text}` e as figuras em `{figures}`. Siga a skill criar-apresentacao e o CLAUDE.md "
           "do projeto.")
# Windows paths stop at 260 characters here (LongPathsEnabled is 0): a slug and the saved PDF's name are kept short
SLUG_LIMIT = 40
PDF_LIMIT = 60  # characters of the saved PDF's name, without .pdf


def shorten(text, limit, seps):
    """text, or its start of at most `limit` characters, cut before a separator (one of `seps`) when it has one."""
    if len(text) <= limit:
        return text
    head = text[:limit + 1]
    cut = max(head.rfind(c) for c in seps)
    return (head[:cut] if cut > 0 else text[:limit]).rstrip(seps + " .")


def slug_of(name, taken):
    """Lowercase ASCII from the name, accents removed, with - between words, at most 40 characters cut before a word;
    -2, -3... when `taken` has it, or when Windows reserves it for a device ("Nül" makes "nul")."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    base = shorten(re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-"), SLUG_LIMIT, "-") or "projeto"
    slug, n = base, 1
    while slug in taken or PureWindowsPath(slug).is_reserved():
        n += 1
        slug = f"{base}-{n}"
    return slug


def reserve(home, name, taken):
    """A slug for `name` that is not `taken`, with its data dir <home>/projects/<slug> made now: the studios of one
    home never pick the same one, and a data dir left over is never reused (its chats are another project's)."""
    taken = set(taken)
    while True:
        slug = slug_of(name, taken)
        try:
            (Path(home) / "projects" / slug).mkdir(parents=True)
            return slug
        except FileExistsError:
            taken.add(slug)


def pdf_name(file_name):
    """The name the imported PDF is saved under in context/: its own, cut at 60 characters before a word."""
    return shorten(file_name[:-4], PDF_LIMIT, " _-.") + file_name[-4:]


def registry(home):
    """The registered projects; none when the file is missing or unreadable."""
    try:
        projects = json.loads((Path(home) / "projects.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [p for p in projects if isinstance(p, dict) and all(isinstance(p.get(k), str) for k in ("name", "slug", "path"))
            ] if isinstance(projects, list) else []


def save_registry(home, projects):
    """Write the registry whole: a temp file, then a replace, so a reader never sees half of it."""
    file = Path(home) / "projects.json"
    file.parent.mkdir(parents=True, exist_ok=True)
    temp = file.with_name(f"projects.{uuid.uuid4().hex}.tmp")
    temp.write_text(json.dumps(projects, ensure_ascii=False, indent=1), encoding="utf-8")
    for attempt in range(40):
        try:
            os.replace(temp, file)
            return
        except PermissionError:  # a reader has it open (Python's open() does not share delete): it ends in moments
            if attempt == 39:
                temp.unlink(missing_ok=True)
                raise
            time.sleep(0.05)


@contextlib.contextmanager
def registry_lock(home):
    """The studios of one home change the registry one at a time: a lock on home/projects.lock (the OS drops it if
    its studio ends while holding it). POSIX file locks do not exclude the threads of one process, so a thread lock
    comes first."""
    with _REGISTRY_THREADS, _registry_file_lock(home):
        yield


_REGISTRY_THREADS = threading.Lock()


@contextlib.contextmanager
def _registry_file_lock(home):
    file = Path(home) / "projects.lock"
    file.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(file, os.O_RDWR | os.O_CREAT | plataforma.O_BINARY)
    try:
        plataforma.lock_byte(fd, wait=True)  # Windows waits up to 10 s
        try:
            yield
        finally:
            os.lseek(fd, 0, os.SEEK_SET)
            plataforma.unlock_byte(fd)
    finally:
        os.close(fd)


def register(home, project):
    """Add `project` to the registry as it is now, not as it was when the import began: another studio of this home
    may have added one meanwhile."""
    with registry_lock(home):
        save_registry(home, [*registry(home), project])


def unregister(home, drop):
    """Take off the registry the projects for which drop(project) is true, and return them. Their folders and data
    dirs stay as they are."""
    with registry_lock(home):
        known = registry(home)
        gone = [p for p in known if drop(p)]
        if gone:
            save_registry(home, [p for p in known if not drop(p)])
        return gone


def entry(name, slug, folder, fmt, language):
    return {"name": name, "slug": slug, "path": str(folder), "format": fmt, "language": language,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S")}


def create(folder, name, slug, fmt, language, pdf_name, pdf):
    """The template filled into `folder` (absent or empty), its studio.json, and the PDF as context/<pdf_name>.
    Raises FileExistsError, before writing anything, when the folder has files."""
    create_from_files(folder, name, slug, fmt, language, {pdf_name: pdf}, pdf_name)


def point_to_sources(folder, slug, extracted):
    """A project made from a folder with several PDFs: its CLAUDE.md names them all and their extraction folders
    (extracted: {PDF's context-relative path: its folder in context/}). The template's own text names one PDF and
    context/<slug>/, which then does not exist. Nothing changes with one PDF or none."""
    if len(extracted) < 2:
        return
    claude = Path(folder) / "CLAUDE.md"
    text = claude.read_text(encoding="utf-8")
    first_pdf, first_out = next(iter(extracted.items()))
    pdfs = ", ".join(f"`context/{p}`" for p in extracted)
    folders = ", ".join(f"`context/{out}/` (from `{p}`)" for p, out in extracted.items())
    text = text.replace(f"comes from the imported PDF, `context/{first_pdf}`.",
                        f"comes from the imported PDFs ({pdfs}) and the other files in `context/`.")
    text = text.replace(f"- **The extracted PDF** is in `context/{slug}/`:",
                        f"- **The extracted PDFs** are in `context/`, one folder each: {folders}. In each folder:")
    text = text.replace(f"{slug}/figuras/", f"{first_out}/figuras/")
    claude.write_text(text, encoding="utf-8")


def create_from_files(folder, name, slug, fmt, language, files, main):
    """The template filled into `folder` (absent or empty), its studio.json, and `files` ({context-relative path:
    bytes}) under context/; `main` is the file the template names as the source (a PDF, or "" for the folder)."""
    lang, language_name, _ = LANGUAGES[language]
    fill_template(folder, {"TITLE": name, "LANG": lang, "LANGUAGE": language_name,
                           "PDF": f"context/{main}" if main else "context/", "SLUG": slug})
    studio = {"title": name, "format": fmt, "language": language, "startMode": "beamer" if fmt == "beamer" else "html",
              "beamerStart": BEAMER_START}
    (folder / "studio.json").write_text(json.dumps(studio, ensure_ascii=False, indent=1), encoding="utf-8")
    (folder / "context").mkdir(exist_ok=True)
    for rel, data in files.items():
        target = folder / "context" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)


def stop_tree(pid):
    plataforma.kill_tree(pid)


def running_url(data_dir, wait=0):
    """The URL of the studio that runs on this data dir, else None. Its studio.lock (__main__.lock_data_dir) holds
    the URL, and the byte at 1 GiB stays locked while it runs: reading that byte then fails, and this read never
    takes the lock, so it cannot get in the way of a studio that starts meanwhile. A studio that is still starting
    has the lock and no URL yet: this waits up to `wait` seconds for it."""
    lock = Path(data_dir) / "studio.lock"
    end = time.monotonic() + wait
    while True:
        try:
            fd = os.open(lock, os.O_RDONLY | plataforma.O_BINARY)
        except OSError:
            return None
        try:
            os.lseek(fd, 1 << 30, os.SEEK_SET)
            if not plataforma.byte_locked(fd):
                return None
            # locked: it runs
            url = lock.read_text(encoding="utf-8")  # empty while it starts
            if url or time.monotonic() > end:
                return url or None
        finally:
            os.close(fd)
        time.sleep(0.1)


def start(kit, data_dir, home, extra=(), timeout=60):
    """Start a studio on `kit` as a child of this one: no window, no browser, and it exits when this process does
    (--parent-pid). Waits for its DECK_STUDIO_URL line; returns (process, URL or None, its last output lines).
    Its output is drained for good, and goes on to this studio's stderr."""
    argv = [sys.executable, "-m", "deck_studio", "--kit", str(kit), "--data", str(data_dir), "--home", str(home),
            "--port", "0", "--no-open", "--parent-pid", str(os.getpid()), *extra]
    proc = subprocess.Popen(argv, cwd=APP, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            creationflags=plataforma.NO_WINDOW, **plataforma.NEW_GROUP, env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                            text=True, encoding="utf-8", errors="replace")
    found, done, tail = [], threading.Event(), collections.deque(maxlen=5)

    def drain():
        for line in proc.stdout:
            m = re.fullmatch(r"DECK_STUDIO_URL=(\S+)", line.strip())
            if m and not found:
                found.append(m[1])
                done.set()
            elif line.strip():
                tail.append(line.strip())
                print(f"[{Path(kit).name}] {line.rstrip()}", file=sys.stderr, flush=True)
        done.set()

    threading.Thread(target=drain, name=f"studio-output-{proc.pid}", daemon=True).start()
    done.wait(timeout)
    return proc, (found[0] if found else None), list(tail)


def call(url, path, body=None):
    """A request to the studio at `url` (its launch URL, with the token): `body` posted as JSON, or a GET without
    one. Returns the JSON answer; an HTTP failure raises OSError."""
    u = urlsplit(url)
    request = urllib.request.Request(f"{u.scheme}://{u.netloc}{path}", None if body is None else json.dumps(body).encode(),
                                     {"content-type": "application/json", "x-studio-token": parse_qs(u.query)["t"][0]})
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # straight to 127.0.0.1, never a proxy
    with opener.open(request, timeout=30) as r:
        return json.loads(r.read())


def send_first(url, text):
    """A new chat in the studio at `url`, and `text` as its first message: the agent's turn starts there. Returns the
    chat's id; an HTTP failure raises OSError."""
    chat = call(url, "/api/chats", {})
    call(url, f"/api/chats/{chat['id']}/messages", {"text": text})
    return chat["id"]


def last_chat(url):
    """The chat to show in a new tab of the studio at `url`: the one whose turn runs, else the one used last (a tab
    with no chat named opens a new one). None when it has none or does not answer."""
    try:
        chats = call(url, "/api/chats")
    except (OSError, ValueError):
        return None
    return max(chats, key=lambda c: (c["running"], c["updated"]), default={}).get("id")


def discard(folder, existed):
    """Undo create(): the folder goes, or is left empty when it was there before."""
    shutil.rmtree(folder, ignore_errors=True)
    if existed:
        folder.mkdir(parents=True, exist_ok=True)


async def extract(pdf, out, timeout=120):
    """deck_studio.pdf_import in a process of its own (a PDF that crashes MuPDF never takes the studio with it).
    Returns info.json's object; an unreadable PDF is a 400 ApiError."""
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "deck_studio.pdf_import", str(pdf), str(out), cwd=APP,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, creationflags=plataforma.NO_WINDOW)
    try:
        raw, _ = await asyncio.wait_for(proc.communicate(), timeout)
    except TimeoutError:
        stop_tree(proc.pid)
        raise ApiError(400, "bad-pdf", "Este PDF demorou demais para ser lido.") from None
    except asyncio.CancelledError:  # the studio is closing
        stop_tree(proc.pid)
        raise
    try:
        answer = json.loads(raw)
    except ValueError:
        answer = None
    if proc.returncode == 0 and isinstance(answer, dict):
        return answer
    if proc.returncode == 1 and isinstance(answer, dict) and isinstance(answer.get("message"), str):
        raise ApiError(400, answer.get("error") or "bad-pdf", answer["message"])
    raise ApiError(400, "bad-pdf", "Não foi possível ler este PDF.")
