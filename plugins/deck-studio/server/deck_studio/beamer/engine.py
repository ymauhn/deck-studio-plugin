"""Beamer engine: find projects, compile with latexmk, render pages, map clicks to source lines."""
import gzip
import json
import os
import re
import shutil
import subprocess
import time
import unicodedata
from pathlib import Path

import pymupdf

from deck_studio.core import plataforma

BEAMER_CLASS = re.compile(r"^[^%\n]*\\documentclass(\[[^\]]*\])?\{beamer\}", re.M)
# latexmk switches. Never LuaLaTeX: its Lua code writes files in the project folder even with shell escape
# off (io.open('latexmkrc', 'w') lands there); a lualatex magic comment falls back to the preamble rule
ENGINES = {"pdflatex": "-pdf", "xelatex": "-xelatex"}
TIMEOUT = 300
# MiKTeX's switch for no log wrapping; TeX Live has no such switch and reads max_print_line (tex_env)
LOG_WIDTH = ["-max-print-line=10000"] if plataforma.WINDOWS else []
# \input, \include and \includegraphics reach only files under the folder TeX runs in (no absolute path, no ..): the
# agent writes the .tex with no approval, and a page holding another file of this computer would reach the agent's
# screenshots and the author's PDF. ponytail: MiKTeX does not apply it to \openin + \read; only a sandbox closes that
SAFE_INPUTS = {"MIKTEX_CORE_ALLOWUNSAFEINPUTFILES": "false"}
# MiKTeX's latexmk is a Perl script: without a perl on PATH it stops with "could not find the script engine 'perl'"
# (2026-11-04: the studio, opened from Explorer, does not have Git's usr/bin on its PATH). Where to look besides PATH:
# (not C:\Strawberry: any user may create a folder at the root of C:, and the studio would run that perl.exe)
PERL_PLACES = [] if not plataforma.WINDOWS else [r"%ProgramFiles%\Git\usr\bin", r"%ProgramFiles(x86)%\Git\usr\bin", r"%LOCALAPPDATA%\Programs\Git\usr\bin",
               r"%ProgramFiles%\Strawberry\perl\bin"]
NO_PERL = ("O latexmk precisa do Perl, e nenhum foi achado (nem no PATH, nem no Git for Windows, nem no Strawberry "
           "Perl): o studio compilou com o pdflatex e o bibtex direto. Para usar o latexmk, instale o Git for Windows "
           "(git-scm.com) ou o Strawberry Perl (strawberryperl.com) e abra o Deck Studio de novo.")


def find_perl(path=None, places=PERL_PLACES):
    """The folder of a perl.exe: on PATH first, then in Git for Windows' or Strawberry Perl's usual folders."""
    found = shutil.which("perl", path=path if path is not None else os.environ.get("PATH", ""))
    if found:
        return str(Path(found).parent)
    for place in places:
        folder = Path(os.path.expandvars(place))
        if "%" not in str(folder) and (folder / "perl.exe").is_file():
            return str(folder)
    return None


def tex_env(perl=None):
    """The TeX tools' environment: safe inputs, and perl's folder at the end of PATH, for them only (at the end,
    nothing in that folder shadows a TeX tool)."""
    # max_print_line: no log wrapping, so errors parse; MiKTeX takes it as the -max-print-line switch, TeX Live's
    # kpathsea reads it from the environment (it overrides texmf.cnf)
    env = {**os.environ, **SAFE_INPUTS, "max_print_line": "10000"}
    if perl:
        env["PATH"] = env.get("PATH", "") + os.pathsep + perl
    return env


def run(argv, cwd, env=None):
    """Run a TeX tool; on timeout stop its whole process tree (latexmk starts perl and the engine)."""
    p = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                         encoding="utf-8", errors="replace", creationflags=plataforma.NO_WINDOW, **plataforma.NEW_GROUP,
                         env=env or tex_env())
    try:
        out = p.communicate(timeout=TIMEOUT)[0]
    except subprocess.TimeoutExpired:
        plataforma.kill_tree(p.pid)
        out = p.communicate()[0] + f"\ntimeout after {TIMEOUT} s"
    return p.returncode, out


def discover_projects(kit_root):
    """Main .tex files with the beamer class under <kit>/beamer. A main whose folder has build/layout.json
    (the HTML measure that page_map reads) is the deck generated from the HTML; the others are hand-written."""
    root = Path(kit_root)
    out = []
    for tex in sorted((root / "beamer").rglob("*.tex")):
        if not BEAMER_CLASS.search(tex.read_text(encoding="utf-8", errors="replace")):
            continue
        pdf = tex.with_suffix(".pdf")
        out.append({"kind": "generated" if (tex.parent / "build" / "layout.json").exists() else "handwritten",
                    "rel": tex.relative_to(root).as_posix(), "main": str(tex), "pdf": str(pdf) if pdf.exists() else None})
    return out


def frames(tex_text):
    """1-based {start, end} lines of every \\begin{frame} ... \\end{frame} written on lines of their own."""
    out, start = [], None
    for i, line in enumerate(tex_text.split("\n"), 1):
        s = line.lstrip()
        if s.startswith("\\begin{frame}"):
            start = i
        elif s.startswith("\\end{frame}") and start:
            out.append({"start": start, "end": i})
            start = None
    return out


def _bib_tool(text):
    """biber for biblatex, bibtex for \\bibliography{...}, None without a bibliography."""
    code = "\n".join(line.split("%")[0] for line in text.split("\n"))
    if re.search(r"\\usepackage(\[[^\]]*\])?\{biblatex\}|\\addbibresource", code):
        return "biber"
    return "bibtex" if re.search(r"\\bibliography\{", code) else None


def _bib_after_first_pass(work, stem):
    """The bibliography tool the first pass asks for, from its own files: biber when it wrote <stem>.bcf (biblatex),
    bibtex when the .aux has a \\bibdata (also from a \\bibliography inside an \\input file), else None."""
    if (work / f"{stem}.bcf").exists():
        return "biber"
    try:
        aux = (work / f"{stem}.aux").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return "bibtex" if "\\bibdata{" in aux else None


def _without_latexmk(tex, text, src, work, cwd, env):
    """What latexmk does for a deck, without Perl: the engine, the bibliography tool, then the engine twice (the
    citations, then the references and the page numbers settle). Returns (exit code of the last run, output, the
    bibliography tool's error or None): bibtex and biber exit with 2 or more on an error (1 is warnings only)."""
    engine = [tex, "-synctex=1", "-interaction=nonstopmode", "-file-line-error", "-no-shell-escape",
              *LOG_WIDTH, f"-output-directory={work}", str(src)]
    code, out = run(engine, cwd, env)
    outs, bib_error = [out], None
    tool = _bib_after_first_pass(work, src.stem) or _bib_tool(text)
    if tool and (work / f"{src.stem}.aux").exists():
        argv = (["biber", f"--input-directory={cwd}", f"--output-directory={work}", src.stem] if tool == "biber"
                else ["bibtex", src.stem])
        bib_code, bib_out = run(argv, cwd if tool == "biber" else work, env)
        outs.append(bib_out)
        try:
            blg = (work / f"{src.stem}.blg").read_text(encoding="utf-8", errors="replace")
        except OSError:
            blg = ""
        # TeX Live's bibtex exits with 2 on an error, MiKTeX's with 1 (and 0 on warnings): the .blg says which
        if bib_code is None or bib_code >= 2 or re.search(r"\(There (?:was|were) \d+ error messages?\)|^ERROR - ",
                                                          blg, re.M):
            bib_error = (f"O {tool} falhou (código {bib_code}): as citações ficam [?]. "
                         + " ".join(bib_out.strip().splitlines()[-3:]))
    for _ in range(2):
        code, out = run(engine, cwd, env)
        outs.append(out)
    return code, "\n".join(outs), bib_error


def compile(project, work_dir, frame=None, perl=...):
    """latexmk with SyncTeX into work_dir, run from the project folder so relative inputs resolve.
    `perl`, the folder of the perl.exe latexmk runs on, is found by default (find_perl); with none, the deck is
    compiled without latexmk, and its errors say how to get one.
    frame=i (0-based index into frames(main)) compiles the preamble plus that frame alone, with the
    frame kept on its own line numbers, so errors and clicks map back to the main file unchanged."""
    main = Path(project["main"])
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    text = main.read_text(encoding="utf-8")
    tex = engine_of(text)
    src = main
    if frame is not None:
        lines = text.split("\n")
        f = frames(text)[frame]
        doc = next(i for i, line in enumerate(lines) if "\\begin{document}" in line.split("%")[0])
        keep = lines[:doc + 1] + [""] * (f["start"] - 2 - doc) + lines[f["start"] - 1:f["end"]] + ["\\end{document}"]
        src = work / f"{main.stem}-frame-{frame}.tex"
        src.write_text("\n".join(keep) + "\n", encoding="utf-8")
    t = time.perf_counter()
    # the agent writes in the project folder with no approval, so nothing there may run: no latexmkrc (Perl)
    # and no \write18. ponytail: -max-print-line (no log wrapping, so errors parse) is a MiKTeX switch; TeX Live
    # reads it from texmf.cnf
    perl = find_perl() if perl is ... else perl
    # bibtex runs in work_dir, where the .aux is: the .bib and .bst next to the deck are found through these (latexmk
    # on Git's MSYS perl did not pass the folder on: the citations came out as [?])
    # the deck's folder first, then what the author set, then the TeX defaults (the empty entry)
    env = tex_env(perl)
    for var in ("BIBINPUTS", "BSTINPUTS"):
        env[var] = os.pathsep.join([str(main.parent), os.environ.get(var, ""), ""])
    bib_error = None
    if perl:
        code, out = run(["latexmk", "-norc", ENGINES[tex], "-synctex=1", "-interaction=nonstopmode", "-file-line-error",
                         "-latexoption=-no-shell-escape", *(f"-latexoption={a}" for a in LOG_WIDTH), f"-outdir={work}",
                         str(src)], main.parent, env)
    else:
        code, out, bib_error = _without_latexmk(tex, src.read_text(encoding="utf-8"), src, work, main.parent, env)
    pdf = work / f"{src.stem}.pdf"
    syn = work / f"{src.stem}.synctex.gz"
    if src != main and syn.exists():   # point SyncTeX at the main file, so locate() answers with it
        lines = gzip.decompress(syn.read_bytes()).split(b"\n")
        for i, line in enumerate(lines):
            if line.startswith(b"Input:"):
                tag, path = line[6:].split(b":", 1)
                if same(path.decode("utf-8", "surrogateescape"), src):
                    lines[i] = b"Input:" + tag + b":" + os.path.normpath(main).encode("utf-8")
        syn.write_bytes(gzip.compress(b"\n".join(lines)))
    log = work / f"{src.stem}.log"
    errors = errors_of(log.read_text(encoding="utf-8", errors="replace") if log.exists() else "", main.parent)
    for e in errors:
        if e["file"] and same(e["file"], src):
            e["file"] = os.path.normpath(main)
    if code and not errors:
        errors = [{"file": None, "line": None, "message": out.strip()[-500:]}]
    if bib_error:  # the PDF exists, but its citations are [?]: not a good compile
        errors.append({"file": None, "line": None, "message": bib_error})
    ok = code == 0 and not bib_error
    if not ok and (not perl or "script engine 'perl'" in out):  # what to do, before the TeX details
        errors.insert(0, {"file": None, "line": None, "message": NO_PERL})
    return {"ok": ok, "pdf": str(pdf) if pdf.exists() else None, "errors": errors, "engine": tex,
            "ms": round((time.perf_counter() - t) * 1000)}


def engine_of(text):
    """The `% !TEX program` magic comment wins; otherwise fontspec or unicode-math in the preamble means XeLaTeX."""
    m = re.search(r"^%\s*!TEX\s+(?:TS-)?program\s*=\s*(\w+)", text, re.M | re.I)
    if m and m[1].lower() in ENGINES:
        return m[1].lower()
    preamble = text.split("\\begin{document}")[0]
    return "xelatex" if re.search(r"^[^%\n]*\\usepackage(\[[^\]]*\])?\{(fontspec|unicode-math)\}", preamble, re.M) else "pdflatex"


def same(a, b):
    return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))


def errors_of(log, cwd):
    """TeX errors of a -file-line-error log as {file, line, message}, each once."""
    out = []
    for m in re.finditer(r"^(?:(.+?):(\d+): |! )(.+)$", log, re.M):
        e = {"file": os.path.normpath(Path(cwd) / m[1]) if m[1] else None, "line": int(m[2]) if m[2] else None,
             "message": m[3].strip()}
        if e not in out:
            out.append(e)
    return out


def page_count(pdf):
    with pymupdf.open(pdf) as d:
        return d.page_count


def render_page(pdf, page, dpi=144):
    """PNG bytes of a 1-based page."""
    with pymupdf.open(pdf) as d:
        return d[page - 1].get_pixmap(dpi=dpi).tobytes("png")


def norm(s):
    """Lower-case word tokens of PDF text or of a TeX line without its commands (the 2026-10-27 spike's rule)."""
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\\\\(\[[^\]]*\])?", " ", s)
    s = re.sub(r"\\[a-zA-Z@]+\*?(\[[^\]]*\])?(\{[\d.\-]+\})*", " ", s)
    s = re.sub(r"[{}$\\]", " ", s)
    return re.findall(r"\w+", s.lower())


def visual_line(pdf, page, x, y):
    """The PDF word under the point and the words of its visual line (same top, gaps under 15 pt)."""
    with pymupdf.open(pdf) as d:
        words = d[page - 1].get_text("words")
    w = next((w for w in words if w[0] <= x <= w[2] and w[1] <= y <= w[3]), None)
    if not w:
        return None, []
    group = []
    for v in sorted((v for v in words if abs(v[1] - w[1]) < 1), key=lambda v: v[0]):
        if group and v[0] - group[-1][2] > 15:
            if w in group:
                break
            group = []
        group.append(v)
    return w[4], [v[4] for v in group]


def locate(pdf, page, x_pt, y_pt):
    """Source of a click on a PDF page (points from the top left). SyncTeX in Beamer only knows the frame,
    so the line is the one in that frame (then in the preamble) that best matches the clicked visual line."""
    _, out = run(["synctex", "edit", "-o", f"{page}:{x_pt:.2f}:{y_pt:.2f}:{pdf}"], Path(pdf).parent)
    m = re.search(r"^Input:(.+)$\s+^Line:(\d+)", out, re.M)
    if not m or not os.path.isfile(m[1].strip()):
        return None
    file, line = os.path.normpath(m[1].strip()), int(m[2])
    text = Path(file).read_text(encoding="utf-8", errors="replace")
    src = text.split("\n")
    frame = next((f for f in frames(text) if f["start"] <= line <= f["end"]), None)
    hit = {"file": file, "line": line, "frame": frame, "text": "", "method": "synctex"}
    word, line_words = visual_line(pdf, page, x_pt, y_pt)
    if not word:
        return hit
    toks, wt = norm(" ".join(line_words)), norm(word)
    joined = "".join(toks)

    def score(i):
        lt = norm(re.sub(r"(?<!\\)%.*", "", src[i - 1]))   # comments are never typeset
        return joined in "".join(lt), sum(t in lt for t in toks) + 2 * sum(t in lt for t in wt), -i

    doc = next((i for i, s in enumerate(src, 1) if "\\begin{document}" in s.split("%")[0]), 0)
    hit["text"] = " ".join(line_words)
    for lo, hi in ([(frame["start"], frame["end"])] if frame else [(1, len(src))]) + [(1, doc)]:
        best = max(range(lo, hi + 1), key=score, default=None)
        if best and score(best)[:2] != (False, 0):
            return {**hit, "line": best, "method": "synctex+text"}
    return hit


def page_map(root):
    """Slide, step and kind of every page of the deck generated from the HTML (beamer/tools/make_tex.py):
    frame k of the .nav is slide k of build/layout.json and its pages are that slide's states in order
    ("step", or "state" for the extra states such as "all"), plus "animation" pages over the last step;
    the frames after the slides are "explorer" pages, found by the slide number they print."""
    gen = next((p for p in discover_projects(root) if p["kind"] == "generated"), None)
    if not gen:
        return []
    main = Path(gen["main"])
    slides = json.loads((main.parent / "build" / "layout.json").read_text(encoding="utf-8"))["slides"]
    spans = re.findall(r"\\beamer@framepages \{(\d+)\}\{(\d+)\}", main.with_suffix(".nav").read_text(encoding="utf-8"))
    tex = (main.parent / "slides.tex").read_text(encoding="utf-8")
    lines, fr = tex.split("\n"), frames(tex)
    label = {s["label"]: s for s in slides}
    out = []
    for k, (a, b) in enumerate(spans):
        if k < len(slides):
            s = slides[k]
        else:
            body = "\n".join(lines[fr[k]["start"] - 1:fr[k]["end"]])
            s = label[re.search(r"\\color\{muted\}([^}/]+)", body)[1].strip()]
        for i, page in enumerate(range(int(a), int(b) + 1)):
            if k >= len(slides):
                state, kind = None, "explorer"
            elif i >= len(s["states"]):
                state, kind = str(s["steps"]), "animation"
            else:
                state = s["states"][i]
                kind = "step" if state.isdigit() else "state"
            step = int(state) if state and state.isdigit() else s["steps"]
            out.append({"page": page, "slide": s["id"], "n": s["n"], "step": step, "state": state, "kind": kind})
    return out


def pdf_to_html(x_pt, y_pt):
    """A point of the generated deck's PDF (points from the top left) in the 1600x900 HTML slide space (1 px = 0.1 mm)."""
    return {"x": x_pt * 254 / 72, "y": y_pt * 254 / 72}
