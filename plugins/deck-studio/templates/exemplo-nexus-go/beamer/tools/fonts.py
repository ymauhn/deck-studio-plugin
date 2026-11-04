"""Write the deck's web fonts (deck/build/fonts.css, latin subsets) as static TTFs for XeLaTeX.

Bricolage Grotesque is variable (opsz, wght); each (weight, opsz) the slides use becomes one
static instance. Usage: python -I beamer/tools/fonts.py "650:96,700:96"   -> beamer/fonts/*.ttf
"""
import base64, io, re, sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "beamer" / "fonts"
NAMES = {("Atkinson Hyperlegible Next", "400"): "AtkinsonNext-Regular", ("Atkinson Hyperlegible Next", "700"): "AtkinsonNext-Bold",
         ("IBM Plex Mono", "400"): "PlexMono-Regular", ("IBM Plex Mono", "500"): "PlexMono-Medium"}


def main(display):
    OUT.mkdir(parents=True, exist_ok=True)
    css = (ROOT / "deck" / "build" / "fonts.css").read_text(encoding="utf8")
    for face in re.findall(r"@font-face\s*\{[^}]*\}", css):
        fam = re.search(r"font-family:\s*'([^']+)'", face).group(1)
        wt = re.search(r"font-weight:\s*([\d ]+);", face).group(1).strip()
        font = TTFont(io.BytesIO(base64.b64decode(re.search(r"base64,([^)]+)\)", face).group(1))))
        font.flavor = None
        if fam == "Bricolage Grotesque":
            for spec in display.split(","):
                w, o = (float(v) for v in spec.split(":"))
                inst = instantiateVariableFont(TTFont(io.BytesIO(base64.b64decode(re.search(r"base64,([^)]+)\)", face).group(1)))), {"wght": w, "opsz": o})
                inst.flavor = None
                inst.save(OUT / f"Bricolage-w{w:g}-o{o:g}.ttf")
        else:
            if "fvar" in font:  # Atkinson Next is variable too: unpinned, XeLaTeX draws its default (400) for the bold face
                font = instantiateVariableFont(font, {"wght": float(wt)})
                font.flavor = None
            font.save(OUT / f"{NAMES[(fam, wt)]}.ttf")
    print("fonts:", ", ".join(sorted(p.name for p in OUT.glob("*.ttf"))))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "650:96,700:96")
