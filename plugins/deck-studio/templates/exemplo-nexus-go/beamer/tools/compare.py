"""Compare the Beamer PDF with the HTML deck, state by state (QA for the Beamer version).

Renders each Beamer page (MiKTeX pdftoppm, 1600 px wide) and the matching HTML state
(Playwright, same settle as extract.py), and writes qa/beamer/<label>-<state>.png with
HTML | Beamer | difference, plus a score (mean absolute difference, 0-255) per page.
Usage: python -I -X utf8 beamer/tools/compare.py [label ...]     (default: final state of every slide)
       add --all to compare every state of the listed slides
"""
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageChops, ImageOps
from playwright.sync_api import sync_playwright

sys.path.insert(0, str(Path(__file__).parent))
from extract import AMBIENT, EXTRA, JS, URL  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PDF = ROOT / "beamer" / "nexus-go-defense.pdf"
OUT = ROOT / "qa" / "beamer"
TOPPM = Path.home() / "AppData/Local/Programs/MiKTeX/miktex/bin/x64/miktex-pdftoppm.exe"


def main(args):
    every = "--all" in args
    labels = [a for a in args if not a.startswith("--")]
    L = json.loads((ROOT / "beamer" / "build" / "layout.json").read_text(encoding="utf8"))
    page, where = 1, {}
    for s in L["slides"]:
        where[s["label"]] = (s, page)
        page += len(s["states"]) + (1 if s["n"] == 24 else 0)
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    scores = []
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        pg.goto(URL)
        pg.wait_for_function("window.deck !== undefined")
        pg.evaluate("document.fonts.ready")
        pg.evaluate(JS)
        pg.evaluate("document.documentElement.classList.remove('bx')")
        for lab in labels or list(where):
            s, p0 = where[lab]
            ks = range(len(s["states"])) if every else [s["states"].index(str(s["steps"]))]
            for k in ks:
                name, n = s["states"][k], s["n"]
                f = int(name) if name.isdigit() else s["steps"]
                pg.evaluate(f"deck.go({n}, {f})")
                pg.evaluate(f"""() => {{ for (const id of {json.dumps(AMBIENT)}) {{ const c = deck.component(id, {n}); if (c) c.pause(); }}
                  const fo = deck.component('INT-FOLD', {n}); if (fo) fo.render(7); const h = deck.component('INT-HERO', {n}); if (h) h.render(4); }}""")
                js = dict(EXTRA.get(n, [])).get(name)
                if js:
                    pg.evaluate(js)
                pg.wait_for_timeout(250)
                html = Image.open(io.BytesIO(pg.screenshot())).convert("RGB")
                subprocess.run([str(TOPPM), "-f", str(p0 + k), "-l", str(p0 + k), "-scale-to-x", "1600", "-scale-to-y", "900",
                                "-png", str(PDF), str(tmp / "p")], check=True)
                bea = Image.open(next(tmp.glob("p*.png"))).convert("RGB")
                for q in tmp.glob("p*.png"):
                    q.unlink()
                diff = ImageChops.difference(html, bea)
                score = sum(ImageOps.grayscale(diff).getdata()) / (1600 * 900)
                scores.append((score, f"{lab}-{name}"))
                sheet = Image.new("RGB", (2400, 450), "white")
                for i, im in enumerate((html, bea, ImageOps.invert(diff.point(lambda v: min(255, v * 4))))):
                    sheet.paste(im.resize((800, 450), Image.LANCZOS), (i * 800, 0))
                sheet.save(OUT / f"{lab}-{name}.png")
        b.close()
    for sc, nm in sorted(scores, reverse=True):
        print(f"{sc:6.2f}  {nm}")


if __name__ == "__main__":
    main(sys.argv[1:])
