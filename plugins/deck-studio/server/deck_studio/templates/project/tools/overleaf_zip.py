"""Zip the Beamer deck for Overleaf: beamer/apresentacao, without LaTeX's build files, into
exports/{{SLUG}}-overleaf.zip. On Overleaf: New Project > Upload Project, then Recompile (pdfLaTeX).

Usage: python -I tools/overleaf_zip.py
It prints the zip's whole path, in UTF-8 (the studio's job log reads it so, and a folder name may have accents).
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "beamer" / "apresentacao"
OUT = ROOT / "exports" / "{{SLUG}}-overleaf.zip"
BUILD = (".aux", ".bbl", ".bcf", ".blg", ".dvi", ".fdb_latexmk", ".fls", ".log", ".nav", ".out", ".run.xml", ".snm",
         ".synctex", ".synctex.gz", ".toc", ".vrb", ".xdv")


def is_build_file(p):
    """What a compile writes: its auxiliary files, and the PDF of a main .tex (a PDF figure stays)."""
    return p.name.endswith(BUILD) or (p.suffix == ".pdf" and p.with_suffix(".tex").is_file())


def main():
    files = sorted(p for p in SRC.rglob("*") if p.is_file() and not is_build_file(p))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in files:
            z.write(p, p.relative_to(SRC).as_posix())
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"wrote {OUT} ({len(files)} files, {OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
