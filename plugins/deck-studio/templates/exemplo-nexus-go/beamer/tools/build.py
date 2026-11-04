"""Build the Beamer version end to end.

  1. extract.py   measures the HTML deck (deck/dist/nexus-go-defense.html)   [skip with --tex]
  2. make_tex.py  writes beamer/slides.tex
  3. XeLaTeX, twice, for nexus-go-defense.pdf and for nexus-go-defense-notes.pdf (notes on a second screen)
  4. checks the logs (errors, Overfull boxes over 10 pt) and writes the Overleaf zip

Usage: python -I -X utf8 beamer/tools/build.py [--tex]
"""
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "beamer"
TOOLS = Path(__file__).parent
TEX = Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/xelatex.exe"


def run(cmd, **kw):
    r = subprocess.run(cmd, cwd=B, capture_output=True, text=True, encoding="utf8", errors="replace", **kw)
    if r.returncode:
        print(r.stdout[-3000:], r.stderr[-2000:])
        raise SystemExit(f"failed: {' '.join(map(str, cmd))}")
    return r


def xelatex(job, pre=""):
    for _ in range(2):   # remember-picture positions need the second pass
        run([str(TEX), "-interaction=nonstopmode", "-halt-on-error", f"-jobname={job}", pre + r"\input{nexus-go-defense}"])
    log = (B / f"{job}.log").read_text(encoding="utf8", errors="replace")
    over = [float(x) for x in re.findall(r"Overfull \\[hv]box \(([\d.]+)pt too", log)]
    pages = re.search(r"Output written on .*?\((\d+) pages", log)
    print(f"{job}.pdf: {pages.group(1) if pages else '?'} pages, {(B / f'{job}.pdf').stat().st_size / 1024 / 1024:.1f} MB, "
          f"{len(over)} overfull boxes (largest {max(over, default=0):.1f} pt)")
    if any(o > 10 for o in over):
        raise SystemExit("an Overfull box is larger than 10 pt")


def overleaf():
    z = B / "nexus-go-defense-overleaf.zip"
    files = [B / "nexus-go-defense.tex", B / "slides.tex", *sorted((B / "fonts").glob("*.ttf")), *sorted((B / "figures").iterdir()),
             B / "build" / "layers.pdf", *sorted((B / "build" / "seq").glob("*.pdf"))]
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as f:
        for p in files:
            f.write(p, p.relative_to(B).as_posix())
        # Overleaf passes its Compiler setting on the command line (-pdf for the default, pdfLaTeX), and that
        # overrides $pdf_mode: the pdfLaTeX command runs xelatex too, so the zip compiles with any setting
        f.writestr("latexmkrc", "$pdf_mode = 5;  # XeLaTeX\n$pdflatex = 'xelatex %O %S';  # also when Overleaf asks for pdfLaTeX\n")
    print(f"{z.name}: {len(files) + 1} files, {z.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    if "--tex" not in sys.argv:
        subprocess.run([sys.executable, "-I", "-X", "utf8", str(TOOLS / "extract.py")], check=True)
    subprocess.run([sys.executable, "-I", "-X", "utf8", str(TOOLS / "make_tex.py")], check=True)
    xelatex("nexus-go-defense")
    xelatex("nexus-go-defense-notes", r"\def\withnotes{}")
    overleaf()
