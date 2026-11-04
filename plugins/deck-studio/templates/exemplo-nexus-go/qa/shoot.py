"""Screenshots of every slide in its final fragment state, plus a contact sheet per theme.

Usage: python -I qa/shoot.py [light|dark|both] [slide numbers...]
Writes qa/shots/<theme>/<label>.png and qa/contact-<theme>.png (contact sheet only for a full run).
"""
import os, sys
from pathlib import Path
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# NX_PT=1: the Portuguese deck, with its shots in qa/shots-pt and qa/contact-pt-<theme>.png
PT = os.environ.get("NX_PT") == "1"
DECK = (ROOT / "deck" / "dist" / ("nexus-go-defesa-pt.html" if PT else "nexus-go-defense.html")).as_uri()


def shoot(themes, only):
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: m.type in ("error", "warning") and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(DECK)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        steps, labels = page.evaluate("deck.steps()"), page.evaluate("deck.labels()")
        for theme in themes:
            out = ROOT / "qa" / ("shots-pt" if PT else "shots") / theme
            out.mkdir(parents=True, exist_ok=True)
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            page.evaluate("for (const c of Object.values(window.NX ? {} : {})) {}")
            files = []
            for i, (n, lab) in enumerate(zip(steps, labels), start=1):
                if only and i not in only:
                    continue
                page.evaluate(f"deck.go({i}, {n})")
                page.wait_for_timeout(3200 if i in (21, 30) else 700)
                f = out / f"{lab.zfill(2)}.png"
                page.screenshot(path=str(f))
                files.append((lab, f))
            if not only:
                sheet(files, ROOT / "qa" / f"contact-{'pt-' if PT else ''}{theme}.png")
        b.close()
    for e in errors:
        print("console:", e)


def sheet(files, dest, cols=6, w=400):
    h = w * 9 // 16
    rows = (len(files) + cols - 1) // cols
    img = Image.new("RGB", (cols * (w + 12) + 12, rows * (h + 34) + 12), "#888888")
    d = ImageDraw.Draw(img)
    for k, (lab, f) in enumerate(files):
        x, y = 12 + (k % cols) * (w + 12), 12 + (k // cols) * (h + 34)
        img.paste(Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        d.text((x, y + h + 6), lab, fill="#ffffff")
    img.save(dest)


if __name__ == "__main__":
    a = sys.argv[1:]
    which = a[0] if a and a[0] in ("light", "dark", "both") else "light"
    nums = {int(x) for x in a if x.isdigit()}
    shoot(["light", "dark"] if which == "both" else [which], nums)
