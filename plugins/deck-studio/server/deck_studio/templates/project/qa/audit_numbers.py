"""Number audit: the NEXUS-GO kit's qa/audit_numbers.py, ported to any source. Every number in the rendered text of
each slide (final step, notes and hidden captions left out) must be in the source, in docs/FACTS.md, or be allowed.

Usage: python -I -X utf8 qa/audit_numbers.py [deck.html]    (default deck/dist/deck.html)
The source is every texto.md, .md, .tex and .txt file under context/ (the import puts the PDF's text in
context/<slug>/texto.md). A number matches when the same value is there in either decimal convention: 73,18 on a
Portuguese slide matches 73.18 in an English source. Allowed without a source: years (1900-2099), whole numbers up
to 10 (counts and ordinals), and the canvas size. Left out: a chart's axis ticks, the differences a staircase
chart computes from its own values (both come from numbers that are audited) and the chart's Tabela view, which
repeats them. Writes qa/number_audit.md; exits 1 when a number has no source.
Only Playwright and the standard library.
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DECK = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "deck" / "dist" / "deck.html"
NUMBER = re.compile(r"(?<![\w.,])[-+−]?\d+(?:[.,]\d+)*(?![\w])")
SOURCE_NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
ALLOW = {"1600": "canvas", "900": "canvas"}


def values(token):
    """The numeric values a written number may mean: 1.234 is 1234 or 1.234; 1,5 is 1.5; 1,234.5 is 1234.5."""
    t = token.replace("−", "-").lstrip("+-")
    out = set()
    for dec in (".", ","):
        other = "," if dec == "." else "."
        s = t.replace(other, "")  # the other mark as thousands separator
        if s.count(dec) > 1:
            continue
        try:
            out.add(round(float(s.replace(",", ".")), 6))
        except ValueError:
            pass
    return out


def source_values():
    texts = []
    context = ROOT / "context"
    for f in context.rglob("*") if context.is_dir() else []:
        if f.suffix.lower() in (".md", ".tex", ".txt", ".bib") and f.is_file():
            texts.append(f.read_text(encoding="utf-8", errors="replace"))
    facts = ROOT / "docs" / "FACTS.md"
    if facts.is_file():
        texts.append(facts.read_text(encoding="utf-8"))
    found = set()
    for t in texts:
        t = re.sub(r"(\d)[   ](?=\d{3}\b)", r"\1", t)  # 12 345 and 12 345 written with a thin space
        for m in SOURCE_NUMBER.finditer(t):
            found |= values(m.group())
    return found


def main():
    if not DECK.is_file():
        print(f"no deck at {DECK}: build it first (python -I -X utf8 deck/build.py)")
        return False
    known = source_values()
    rows, unmatched = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")  # numbers that count stop at the end
        page.goto(DECK.as_uri())
        page.wait_for_function("window.deck !== undefined")
        steps, labels = page.evaluate("deck.steps()"), page.evaluate("deck.labels()")
        for i, n in enumerate(steps, start=1):
            page.evaluate(f"deck.go({i}, {n})")
            text = page.evaluate("""() => {
              const s = document.querySelector('section.slide.active').cloneNode(true);
              s.querySelectorAll('aside.notes, figcaption.cap, .cap, script, style, .cp .tick, .cp .delta, .cp-table, .tip').forEach((e) => e.remove());
              const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT); const o = [];
              while (w.nextNode()) o.push(w.currentNode.textContent);
              return o.join(' ');
            }""")
            seen = set()
            for m in NUMBER.finditer(text):
                token = m.group()
                if token in seen:
                    continue
                seen.add(token)
                plain = token.replace("−", "-").lstrip("+-")
                vals = values(token)
                if vals & known:
                    continue
                if plain in ALLOW:
                    why = ALLOW[plain]
                elif plain.isdigit() and 1900 <= int(plain) <= 2099:
                    why = "year"
                elif plain.isdigit() and int(plain) <= 10:
                    why = "count"
                else:
                    why = "UNMATCHED"
                    unmatched += 1
                rows.append((labels[i - 1], token, why))
        b.close()
    out = ["# Number audit", "",
           "Numbers on the slides that are not in the source (context/) nor in docs/FACTS.md, and why each is allowed.",
           "Every other number was found in the source.", "", "| Slide | Number | Status |", "|---|---|---|"]
    out += [f"| {a} | {b_} | {c} |" for a, b_, c in rows]
    out += ["", f"Unmatched: {unmatched}"]
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "qa" / "number_audit.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    for a, b_, c in rows:
        if c == "UNMATCHED":
            print(f"UNMATCHED {a}: {b_}")
    print(f"number audit: {unmatched} unmatched")
    return unmatched == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
