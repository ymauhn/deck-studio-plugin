"""Render the two TikZ figures of §2.2.3 (perceptron, MLP) to SVG with latex + dvisvgm.

Usage: python -I deck/tools/render_tikz.py <dissertation.tex> <out_dir> <work_dir>
Writes <out_dir>/tikz_perceptron.svg and <out_dir>/tikz_mlp.svg, recoloured to the plate ink.
"""
import re
import subprocess
import sys
from pathlib import Path

INK, SEQ = "#0f1d29", "#2a78d6"  # --ink (light theme) and --seq: the figures sit on light plates


def main(tex, out, work):
    src = Path(tex).read_text(encoding="utf8")
    out, work = Path(out), Path(work)
    out.mkdir(parents=True, exist_ok=True)
    work.mkdir(parents=True, exist_ok=True)
    for name in ("perceptron", "mlp"):
        lab = src.index(r"\label{fig:%s}" % name)
        a = src.rindex(r"\begin{tikzpicture}", 0, lab)
        b = src.index(r"\end{tikzpicture}", a) + len(r"\end{tikzpicture}")
        doc = "\n".join([r"\documentclass[border=4pt]{standalone}", r"\usepackage{amsmath,amssymb,xcolor,tikz}",
                         r"\usetikzlibrary{positioning}", r"\begin{document}", src[a:b], r"\end{document}"])
        (work / f"{name}.tex").write_text(doc, encoding="utf8")
        subprocess.run(["latex", "-interaction=nonstopmode", f"{name}.tex"], cwd=work, check=True, capture_output=True)
        subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "-o", f"{name}.svg", f"{name}.dvi"], cwd=work, check=True, capture_output=True)
        svg = (work / f"{name}.svg").read_text(encoding="utf8")
        svg = svg.replace("stroke='#000'", f"stroke='{INK}'").replace("fill='#00f'", f"fill='{SEQ}'")
        svg = re.sub(r"<svg ", f"<svg fill='{INK}' ", svg, count=1)
        (out / f"tikz_{name}.svg").write_text(svg, encoding="utf8")
        print(f"tikz_{name}.svg")


if __name__ == "__main__":
    main(*sys.argv[1:4])
