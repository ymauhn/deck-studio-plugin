"""Export the HTML deck to PDF: one 1600×900 page per slide, at its last step, light theme, vector text.

Usage: python -I deck/tools/export_pdf.py [out.pdf]   (default deck/dist/deck.pdf)
It prints deck/dist/deck.html, the clean build: run python -I -X utf8 deck/build.py first.
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "deck" / "dist" / "deck.html"


def main(out):
    with sync_playwright() as p:
        b = p.chromium.launch()
        try:
            page = b.new_page(viewport={"width": 1600, "height": 900})
            page.route(re.compile(r"^https?://"), lambda route: route.abort())  # the deck is one file
            page.goto(SRC.as_uri())
            page.wait_for_function("window.deck !== undefined")
            page.evaluate("document.fonts.ready")
            page.evaluate("""() => {
              document.documentElement.dataset.theme = 'light';
              deck.steps().forEach((n, k) => deck.go(k + 1, n));   // every slide at its last step
              document.documentElement.classList.add('printing');
              const total = deck.state().total;
              document.querySelectorAll('section.slide').forEach((s) => {
                if (!s.classList.contains('s-title')) s.dataset.printNum = s.classList.contains('backup') ? s.dataset.label : `${s.dataset.label} / ${total}`;
              });
            }""")
            page.wait_for_timeout(300)
            out.parent.mkdir(parents=True, exist_ok=True)
            page.pdf(path=str(out), width="1600px", height="900px", print_background=True, prefer_css_page_size=True)
        finally:
            b.close()
    shown = out.relative_to(ROOT).as_posix() if out.is_relative_to(ROOT) else out
    print(f"wrote {shown} ({out.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "deck" / "dist" / "deck.pdf")
