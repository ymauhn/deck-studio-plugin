"""Export the HTML deck to PDF: one 1600×900 page per slide, every fragment shown, vector text.

Usage: python -I deck/tools/export_pdf.py [out.pdf]   (default deck/dist/nexus-go-defense.pdf)
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
SRC = (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()


def main(out):
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.goto(SRC)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        page.evaluate("""() => {
          document.documentElement.dataset.theme = 'light';
          deck.steps().forEach((n, k) => deck.go(k + 1, n));   // final fragment state, components mounted and stepped
          const fold = deck.component('INT-FOLD'); if (fold) fold.render(7);   // folded still
          for (const id of ['INT-HERO', 'INT-PIPE', 'INT-MP', 'INT-GBA']) {
            for (let n = 1; n <= deck.steps().length; n++) { const c = deck.component(id, n); if (c) c.pause(); }
          }
          document.documentElement.classList.add('printing');
          const total = deck.state().total;
          document.querySelectorAll('section.slide').forEach((s) => {
            if (!s.classList.contains('s-title')) s.dataset.printNum = s.classList.contains('backup') ? s.dataset.label : `${s.dataset.label} / ${total}`;
          });
        }""")
        page.wait_for_timeout(600)
        page.pdf(path=str(out), width="1600px", height="900px", print_background=True, prefer_css_page_size=True)
        b.close()
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} ({out.stat().st_size / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main(Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "deck" / "dist" / "nexus-go-defense.pdf")
