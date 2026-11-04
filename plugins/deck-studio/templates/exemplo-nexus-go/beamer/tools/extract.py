"""Measure the HTML deck for the Beamer version (step 1 of 2; step 2 is make_tex.py).

For every slide and every fragment state (plus the extra states listed in EXTRA) this records
the text leaves with word positions (they become native LaTeX text), the raster figures and
masks (native \\includegraphics and rectangles), and prints the remaining visuals ("layer") as a
vector PDF page. It also renders the frame sequences for the animate package and the explorer
states behind the clickable controls.

Usage: python -I -X utf8 beamer/tools/extract.py      -> beamer/build/{layout.json,layers.pdf,seq/}
"""
import base64
import hashlib
import io
import json
import shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

ROOT = Path(__file__).resolve().parents[2]
URL = (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()
OUT = ROOT / "beamer" / "build"
JS = (Path(__file__).with_name("extract.js")).read_text(encoding="utf8")
C = "deck.component('{id}', {n})"

# extra states after the last fragment, in the linear flow (docs/BUILD.md §4)
EXTRA = {
    21: [("all", "document.querySelector('#pipe-all').click()")],
    23: [("max", C.format(id="INT-DEDUP", n=23) + ".setMode('max')")],
    24: [("T0", C.format(id="INT-PROP", n=24) + ".set(0, 0.5)"), ("T6", C.format(id="INT-PROP", n=24) + ".set(6, 0.5)")],
    38: [("CC", C.format(id="INT-TEST", n=38) + ".set('CC', 'wFmax')"), ("MF", C.format(id="INT-TEST", n=38) + ".set('MF', 'wFmax')")],
}
# controls whose rectangles become PDF links
CONTROLS = {
    21: ["#pipe-all", "#pipe-fixed", "#pipe-gnn", "#pipe-early", "#pipe-late", "#pipe-fig"],
    23: ["#dd-sum", "#dd-max"],
    24: ["#prop-T", "#prop-alpha", "#prop-play"],
    38: ["#test-BP", "#test-CC", "#test-MF", "#test-metric"],
}
AMBIENT = ["INT-HERO", "INT-FOLD", "INT-PIPE", "INT-MP", "INT-GBA", "INT-PLM", "INT-RW", "INT-GAP"]


IMG = {hashlib.sha1(p.read_bytes()).hexdigest(): p.stem for p in (ROOT / "deck" / "build" / "img").glob("*.webp")}


def img_name(src):
    """The build inlines figures as data URIs; find the deck/build/img file with the same bytes."""
    if not src.startswith("data:"):
        return Path(src).stem
    return IMG[hashlib.sha1(base64.b64decode(src.split(",", 1)[1])).hexdigest()]


def crop(pdf, r):
    """One page of a 1600×900 px PDF, with every page box set to the rectangle r (canvas px)."""
    p = PdfReader(io.BytesIO(pdf)).pages[0]
    s = float(p.mediabox.width) / 1600
    H = float(p.mediabox.height)
    box = RectangleObject((r["x"] * s, H - (r["y"] + r["h"]) * s, (r["x"] + r["w"]) * s, H - r["y"] * s))
    p.mediabox = box; p.cropbox = box; p.trimbox = box; p.artbox = box; p.bleedbox = box
    return p


def save_pdf(path, pages):
    """One multi-page PDF; fonts and images repeated across pages are stored once
    (XeLaTeX keeps that sharing when it includes several pages of the same file)."""
    w = PdfWriter()
    for p in pages:
        w.add_page(p)
    w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    with open(path, "wb") as f:
        w.write(f)


def save_seq(name, pages):
    save_pdf(OUT / "seq" / f"{name}.pdf", pages)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "seq").mkdir(parents=True)
    layer_pages, hashes = [], {}   # every distinct visual layer of the deck, one page each
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(URL)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        page.evaluate("document.documentElement.dataset.theme = 'light'")
        page.evaluate(JS)
        steps = page.evaluate("deck.steps()")
        colors = page.evaluate("""() => { const o = {}; const d = document.createElement('i'); document.body.append(d);
          for (const k of ['ink','ink-2','muted','hair','plate','plate-edge','slide','seq','net','fuse','warn']) { d.style.color = `var(--${k})`; o[k] = getComputedStyle(d).color; }
          d.remove(); return o; }""")

        def settle(n):
            page.evaluate(f"""() => {{
              for (const id of {json.dumps(AMBIENT)}) {{ const c = deck.component(id, {n}); if (c) c.pause(); }}
              const f = deck.component('INT-FOLD', {n}); if (f) f.render(7);
              const h = deck.component('INT-HERO', {n}); if (h) h.render(4);
            }}""")
            page.wait_for_timeout(120)

        def pdf_page():
            return page.pdf(width="1600px", height="900px", print_background=True, prefer_css_page_size=True)

        slides = []
        num = None
        for n, last in enumerate(steps, start=1):
            page.evaluate(f"deck.go({n}, {last})")
            settle(n)
            prep = page.evaluate("BX.prepare()")
            info = page.evaluate("""() => { const s = document.querySelector('section.slide.active');
              return { label: s.dataset.label, part: s.dataset.part || '', cls: s.className, id: s.id,
                       notes: (s.querySelector('aside.notes') || {}).innerHTML || '' }; }""")
            if num is None and "s-title" not in info["cls"]:
                num = page.evaluate("BX.num()")
            states = [(str(f), f, None) for f in range(last + 1)] + [(nm, last, js) for nm, js in EXTRA.get(n, [])]
            leaves, imgs, masks, layers = {}, {}, {}, []
            for k, (name, f, js) in enumerate(states):
                page.evaluate(f"deck.go({n}, {f})")
                settle(n)
                if js:
                    page.evaluate(js)
                    page.wait_for_timeout(120)
                snap = page.evaluate("want => BX.snapshot(want)", [i for i in range(prep["leaves"]) if str(i) not in leaves])
                for i in snap["vis"]:
                    leaves.setdefault(str(i), {"vis": []})["vis"].append(k)
                for i, d in snap["data"].items():
                    leaves[str(i)].update(d)
                for im in snap["imgs"]:
                    e = imgs.setdefault(im["i"], {"src": img_name(im["src"]), "r": im["r"], "vis": []})
                    if im["vis"]:
                        e["vis"].append(k)
                for m in snap["masks"]:
                    e = masks.setdefault(m["i"], {"r": m["r"], "vis": []})
                    if m["vis"]:
                        e["vis"].append(k)
                page.evaluate("BX.layer(true)")
                h = hashlib.sha1(page.screenshot()).hexdigest()
                if h not in hashes:
                    layer_pages.append(PdfReader(io.BytesIO(pdf_page())).pages[0])
                    hashes[h] = len(layer_pages)
                layers.append(hashes[h])
                page.evaluate("BX.layer(false)")
            controls = {}
            if n in CONTROLS:
                page.evaluate(f"deck.go({n}, {last})")
                settle(n)
                controls = {sel: page.evaluate("s => BX.rect(s)", sel) for sel in CONTROLS[n]}
            slides.append({**info, "n": n, "steps": last, "states": [s[0] for s in states], "layers": layers,
                           "leaves": leaves, "imgs": list(imgs.values()), "masks": list(masks.values()), "controls": controls})
            print(f"{info['label']:>3}: {len(states)} states, {len(set(layers))} layers, {prep['leaves']} leaves")

        # frame sequences: animations (animate package) and explorer states behind the controls
        seqs = {}

        def sequence(name, n, sel, setups):
            page.evaluate(f"deck.go({n}, {steps[n - 1]})")
            settle(n)
            pages = []
            r = None
            for js in setups:
                page.evaluate(js)
                r = page.evaluate("s => BX.solo(s)", sel)
                pages.append(crop(pdf_page(), r))
                page.evaluate("BX.solo(null)")
            save_seq(name, pages)
            seqs[name] = {"n": n, "rect": r, "count": len(pages)}
            print(f"seq {name}: {len(pages)} frames")

        pipe = C.format(id="INT-PIPE", n=21)
        sequence("pipe-anim", 21, '[data-component="INT-PIPE"]', [f"{pipe}.render({i / 10})" for i in range(100)])
        sequence("pipe-fig", 21, '[data-component="INT-PIPE"]',
                 ["document.querySelector('#pipe-all').click(); document.querySelector('#pipe-fig').click()"])
        prop = C.format(id="INT-PROP", n=24)
        dur = page.evaluate(f"(deck.go(24, {steps[23]}), {prop}.duration)")
        sequence("prop-anim", 24, '[data-component="INT-PROP"]', [f"{prop}.render({(i + 0.5) * 0.5})" for i in range(int(dur / 0.5))])
        sequence("prop-grid", 24, '[data-component="INT-PROP"]',
                 [f"{prop}.set({t}, {a / 10})" for a in range(1, 10) for t in range(11)])
        test = C.format(id="INT-TEST", n=38)
        metrics = page.evaluate(f"(deck.go(38, {steps[37]}), [...document.querySelectorAll('#test-metric option')].map(o => o.value))")
        sequence("test-grid", 38, '[data-component="INT-TEST"]', [f"{test}.set('{o}', '{m}')" for o in ("BP", "CC", "MF") for m in metrics])
        seqs["test-grid"]["metrics"] = metrics
        b.close()
    if errs:
        raise SystemExit(f"page errors: {errs}")
    save_pdf(OUT / "layers.pdf", layer_pages)
    (OUT / "layout.json").write_text(json.dumps({"colors": colors, "num": num, "slides": slides, "seqs": seqs}, indent=1), encoding="utf8")
    size = sum(p.stat().st_size for p in OUT.rglob("*.pdf")) / 1024 / 1024
    print(f"layout.json: {len(slides)} slides; PDFs {size:.1f} MB")


if __name__ == "__main__":
    main()
