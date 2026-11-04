"""Beamer checks of docs/QA.md §3 and §5: on-screen text and numbers match the HTML deck.

For the final state of every slide, compares the words of the Beamer page (pdftotext) with the
words of the HTML slide (innerText), and checks every number on the Beamer page against the
numbers of the same HTML slide (which passed qa/audit_numbers.py) and dissertation.tex.
Usage: python -I -X utf8 beamer/tools/check_text.py      -> qa/beamer_text.md
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "qa"))
from audit_numbers import canon, tex_numbers  # noqa: E402

URL = (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()
PDF = ROOT / "beamer" / "nexus-go-defense.pdf"
NUM = re.compile(r"\d+(?:[.,]\d+)*")
WORD = re.compile(r"[A-Za-z][A-Za-z\-']+")


def main():
    L = json.loads((ROOT / "beamer" / "build" / "layout.json").read_text(encoding="utf8"))
    tex = tex_numbers()
    page, rows, bad = 1, [], 0
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        pg.goto(URL)
        pg.wait_for_function("window.deck !== undefined")
        for s in L["slides"]:
            k = s["states"].index(str(s["steps"]))
            pdf = subprocess.run(["pdftotext", "-f", str(page + k), "-l", str(page + k), "-enc", "UTF-8", str(PDF), "-"],
                                 capture_output=True, text=True, encoding="utf8").stdout
            page += len(s["states"]) + (1 if s["n"] == 24 else 0)
            pdf = re.sub(r"-\s*\n\s*", "-", pdf)                                  # a word broken after its hyphen
            pdf = re.sub(r"\b\d+ / \d+\s*$|\bB\d\s*$", "", pdf.strip())          # the slide number chrome (allowed, QA §3)
            pg.evaluate(f"deck.go({s['n']}, {s['steps']})")
            html = pg.evaluate("""() => { const c = document.querySelector('section.slide.active').cloneNode(true);
              c.querySelectorAll('aside.notes, mjx-container, option').forEach((e) => e.remove()); document.body.append(c);
              c.style.cssText = 'position:absolute;left:-99999px;visibility:visible;opacity:1'; const t = c.innerText; c.remove(); return t; }""")
            # hyphens are dropped before comparing: pdftotext removes a hyphen at the end of a line
            parts = lambda t: Counter(w.lower().replace("-", "") for w in WORD.findall(t))
            wb, wh = parts(pdf), parts(html)
            missing = sorted((wh - wb).elements())
            nums_h = {canon(x) for x in NUM.findall(html)}
            odd = sorted({x for x in NUM.findall(pdf) if canon(x) not in nums_h and canon(x) not in tex and not x.isdigit() or
                          (x.isdigit() and canon(x) not in nums_h and canon(x) not in tex and int(x) > 12)})
            bad += bool(missing) + bool(odd)
            rows.append(f"| {s['label']} | {', '.join(missing) or 'none'} | {', '.join(odd) or 'none'} |")
        b.close()
    out = ["# Beamer text check", "", "Final state of every slide: words of the HTML slide missing from the Beamer page,",
           "and numbers on the Beamer page found neither on the HTML slide nor in dissertation.tex.", "",
           "| Slide | HTML words missing in Beamer | Numbers without a source |", "|---|---|---|", *rows, ""]
    (ROOT / "qa" / "beamer_text.md").write_text("\n".join(out), encoding="utf8")
    print(f"{len(rows)} slides, {bad} findings -> qa/beamer_text.md")


if __name__ == "__main__":
    main()
