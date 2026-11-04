"""Screenshots of every slide in its final step, and one contact sheet per theme: the NEXUS-GO kit's qa/shoot.py,
with the sheet laid out in the browser (no image library needed).

Usage: python -I -X utf8 qa/shoot.py [light|dark|both] [deck.html]     (default: light, deck/dist/deck.html)
Writes qa/shots/<theme>/<label>.png and qa/contact-<theme>.png, the whole deck in one image for review.
Only Playwright and the standard library.
"""
import base64
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
args = sys.argv[1:]
WHICH = args[0] if args and args[0] in ("light", "dark", "both") else "light"
rest = [a for a in args if a not in ("light", "dark", "both")]
DECK = Path(rest[0]).resolve() if rest else ROOT / "deck" / "dist" / "deck.html"
COLS, W = 5, 420


def sheet(page, files, dest):
    h = W * 9 // 16
    cells = "".join(
        f'<figure><img src="data:image/png;base64,{base64.b64encode(f.read_bytes()).decode()}">'
        f"<figcaption>{label}</figcaption></figure>" for label, f in files)
    page.set_content(f"""<!doctype html><style>
      body {{ margin: 0; padding: 12px; background: #8a8f96; font: 600 14px system-ui; color: #fff; }}
      main {{ display: grid; grid-template-columns: repeat({COLS}, {W}px); gap: 12px; }}
      figure {{ margin: 0; }} img {{ display: block; width: {W}px; height: {h}px; }}
      figcaption {{ padding-top: 4px; }}</style><main>{cells}</main>""")
    page.set_viewport_size({"width": COLS * (W + 12) + 12, "height": 400})
    page.screenshot(path=str(dest), full_page=True)


def main():
    if not DECK.is_file():
        print(f"no deck at {DECK}: build it first (python -I -X utf8 deck/build.py)")
        return False
    themes = ["light", "dark"] if WHICH == "both" else [WHICH]
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")  # charts and numbers at their final values
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(DECK.as_uri())
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        steps, labels = page.evaluate("deck.steps()"), page.evaluate("deck.labels()")
        made = {}
        for theme in themes:
            out = ROOT / "qa" / "shots" / theme
            out.mkdir(parents=True, exist_ok=True)
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            files = []
            for i, (n, label) in enumerate(zip(steps, labels), start=1):
                page.evaluate(f"deck.go({i}, {n})")
                page.wait_for_timeout(450)
                f = out / f"{label.zfill(2)}.png"
                page.screenshot(path=str(f))
                files.append((label, f))
            made[theme] = files
        sheet_page = b.new_page()
        for theme, files in made.items():
            dest = ROOT / "qa" / f"contact-{theme}.png"
            sheet(sheet_page, files, dest)
            print(f"wrote {dest.relative_to(ROOT).as_posix()} ({len(files)} slides)")
        b.close()
    for e in errors:
        print("pageerror:", e)
    return not errors


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
