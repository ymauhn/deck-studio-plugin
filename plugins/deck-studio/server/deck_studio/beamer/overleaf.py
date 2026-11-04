"""Exportar para o Overleaf (pedido do dono, 04/11/2026): a Beamer deck's main .tex and every file it needs, zipped so
that Overleaf (New Project > Upload Project) compiles it as it is, with the PDF of the last compile beside it.

What goes in: the main .tex; what it reads, found in its text (\\input and \\include, recursively; \\includegraphics
through \\graphicspath, with TeX's extension order; \\bibliography and \\addbibresource; a local \\bibliographystyle,
\\usepackage, \\usetheme) and, when the last compile left one, in its .fls (every INPUT inside the deck's folder);
the folder's latexmkrc, which Overleaf follows, and its LEIA-ME.md or README.md. Only files inside the deck's folder, and never a compile's own files.
`check` compiles an extracted copy in an empty folder, as Overleaf would, and lists what is undefined ([?])."""
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from deck_studio.beamer import engine

BUILD = (".aux", ".bbl", ".bcf", ".blg", ".dvi", ".fdb_latexmk", ".fls", ".log", ".nav", ".out", ".run.xml", ".snm",
         ".synctex", ".synctex.gz", ".toc", ".vrb", ".xdv")  # the template's tools/overleaf_zip.py list
GRAPHICS = ("", ".pdf", ".png", ".jpg", ".jpeg", ".eps")  # pdfLaTeX's order, after the name as written
COMMENT = re.compile(r"(?<!\\)%.*")
INPUT = re.compile(r"\\(?:input|include)\s*\{([^}]+)\}")
GRAPHIC = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
GRAPHICSPATH = re.compile(r"\\graphicspath\s*\{((?:\{[^}]*\})+)\}")
BIB = re.compile(r"\\(?:bibliography|addbibresource)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
BST = re.compile(r"\\bibliographystyle\s*\{([^}]+)\}")
PACKAGE = re.compile(r"\\(?:usepackage|RequirePackage)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
THEME = re.compile(r"\\use(theme|colortheme|fonttheme|innertheme|outertheme)\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}")
UNDEFINED = re.compile(r"(?:Citation|Reference) [`']([^']+)' (?:on page \d+ )?undefined")


def _inside(root, path):
    try:
        return path.resolve().is_relative_to(root.resolve())
    except OSError:
        return False


def _first(root, base, names):
    for n in names:
        p = (base / n)
        if p.is_file() and _inside(root, p):
            return p
    return None


def _from_text(main):
    """The files the deck's text names, recursively through its \\input and \\include."""
    root, found, todo = main.parent, set(), [main]
    while todo:
        tex = todo.pop()
        if tex in found:
            continue
        found.add(tex)
        text = COMMENT.sub("", tex.read_text(encoding="utf-8", errors="replace"))
        dirs = [""]
        for m in GRAPHICSPATH.finditer(text):
            dirs += re.findall(r"\{([^}]*)\}", m[1])
        for m in INPUT.finditer(text):
            name = m[1].strip()
            p = _first(root, root, [name, f"{name}.tex"])
            if p and p.suffix == ".tex":
                todo.append(p)
            elif p:
                found.add(p)
        for m in GRAPHIC.finditer(text):
            name = m[1].strip()
            p = _first(root, root, [f"{d}{name}{ext}" for d in dirs for ext in GRAPHICS])
            if p:
                found.add(p)
        for m in BIB.finditer(text):
            for name in m[1].split(","):
                name = name.strip()
                p = _first(root, root, [name if name.endswith(".bib") else f"{name}.bib"])
                if p:
                    found.add(p)
        for m in BST.finditer(text):
            if p := _first(root, root, [f"{m[1].strip()}.bst"]):
                found.add(p)
        for m in PACKAGE.finditer(text):
            for name in m[1].split(","):
                if p := _first(root, root, [f"{name.strip()}.sty"]):
                    found.add(p)
        for m in THEME.finditer(text):
            kind = "" if m[1] == "theme" else m[1].removesuffix("theme")
            if p := _first(root, root, [f"beamer{kind}theme{m[2].strip()}.sty"]):
                found.add(p)
    return found


def _from_fls(main, work):
    """The files inside the deck's folder that the last compile read, from its .fls (latexmk writes one)."""
    fls = Path(work or "") / f"{main.stem}.fls"
    if not work or not fls.is_file():
        return set()
    lines = fls.read_text(encoding="utf-8", errors="replace").splitlines()
    pwd = Path(next((ln[4:] for ln in lines if ln.startswith("PWD ")), str(main.parent)))
    out = set()
    for ln in lines:
        if ln.startswith("INPUT "):
            p = (pwd / ln[6:].strip()).resolve()
            if p.is_file() and _inside(main.parent, p) and not p.name.endswith(BUILD):
                out.add(p)
    return out


def inputs(main, work=None):
    """Every file of the deck's folder the deck needs, sorted, the main .tex first."""
    main = Path(main).resolve()
    files = _from_text(main) | _from_fls(main, work)
    for rc in ("latexmkrc", ".latexmkrc", "LEIA-ME.md", "README.md"):  # what Overleaf follows, and the deck's notes
        if (main.parent / rc).is_file():
            files.add((main.parent / rc).resolve())
    files = {f.resolve() for f in files if not f.name.endswith(BUILD)}
    return [main] + sorted(f for f in files if f != main)


def build(main, pdf, out_dir, work=None):
    """The zip <out_dir>/<deck>-overleaf.zip: the deck's files at their paths in its folder, and `pdf` (the last
    compile's) as <deck>.pdf. Returns (zip path, the zipped names)."""
    main = Path(main).resolve()
    out = Path(out_dir) / f"{main.stem}-overleaf.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    names = []
    tmp = out.with_suffix(".zip.tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in inputs(main, work):
            name = f.relative_to(main.parent).as_posix()
            z.write(f, name)
            names.append(name)
        if pdf:
            z.write(pdf, f"{main.stem}.pdf")
            names.append(f"{main.stem}.pdf")
    tmp.replace(out)
    return out, names


def check(zip_path, main_name):
    """Compile an extracted copy of the zip in an empty folder, as Overleaf does. {ok, errors, undefined}: undefined
    lists the citations and references that came out as [?]."""
    root = Path(tempfile.mkdtemp(prefix="deck-overleaf-"))
    try:
        src = root / "projeto"
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(src)
        (src / Path(main_name).with_suffix(".pdf").name).unlink(missing_ok=True)  # the copy makes its own
        r = engine.compile({"main": str(src / main_name)}, root / "saida")
        log = root / "saida" / f"{Path(main_name).stem}.log"
        text = log.read_text(encoding="utf-8", errors="replace") if log.is_file() else ""
        undefined = sorted(set(UNDEFINED.findall(text)))
        errors = [e["message"] for e in r["errors"]]
        return {"ok": r["ok"] and not undefined and bool(r["pdf"]), "errors": errors[:10], "undefined": undefined}
    finally:
        shutil.rmtree(root, ignore_errors=True)
