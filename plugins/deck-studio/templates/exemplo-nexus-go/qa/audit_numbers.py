"""Number audit (docs/QA.md §3): every number in the rendered text of each slide (final fragment
state, components included) must occur in dissertation.tex, in FACTS.md §1, or in the allow list
below. Math rendered as SVG has no text and is checked by reading the slide sources instead.

Usage: python -I qa/audit_numbers.py   (writes qa/number_audit.md)
"""
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
TEX = (ROOT / "source" / "thesis" / "dissertation.tex").read_text(encoding="utf8")
URL = (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()
ILLUSTRATIVE = ["INT-PROP", "INT-GBA", "INT-FOLD", "INT-HERO", "INT-MP", "INT-PLM"]  # QA §3: labelled demos
# FACTS.md §1 (publication data, dates) and conventions allowed by QA §3
ALLOW = {
    "157": "VISAPP pages", "166": "VISAPP pages", "2026": "year", "16": "defense date", "21": "CCIS issue date",
    "1600": "canvas", "900": "canvas", "22": "ProtT5 layer", "23": "ProtT5 layer", "24": "ProtT5 layer",
    "1": "ordinal / count", "2": "count", "3": "count", "4": "count", "6": "count", "7": "count", "0": "zero",
    "13": "FACTS §8: GCN/fixed ≈ 13.1× time, 'a thirteenth'",
    "0.81": "INT-DEDUP: 4.00 / 4.95, the dissertation's own example (QA §3)",
}
YEARS = {str(y) for y in range(2003, 2027)}
import json as _json
_NUM = _json.loads((ROOT / "data" / "numbering.json").read_text(encoding="utf8"))
for _kind, _d in _NUM.items():
    for _k in _d:
        ALLOW.setdefault(_k, f"{_kind} number")


def canon(s):
    s = s.replace(",", "")
    try:
        f = float(s)
    except ValueError:
        return s
    return repr(round(f, 6))


def tex_numbers():
    t = TEX.replace("{,}", ",")
    t = re.sub(r"(\d)\\,(\d)", r"\1\2", t)
    nums = set()
    for m in re.finditer(r"\d+(?:,\d{3})*(?:\.\d+)?", t):
        nums.add(canon(m.group()))
    return nums


def main():
    known = tex_numbers()
    rows, unmatched = [], 0
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.goto(URL)
        page.wait_for_function("window.deck !== undefined")
        steps, labels = page.evaluate("deck.steps()"), page.evaluate("deck.labels()")
        for i, n in enumerate(steps, start=1):
            page.evaluate(f"deck.go({i}, {n})")
            page.wait_for_timeout(250 if i not in (21, 30) else 2800)
            txt = page.evaluate("""(ill) => {
              const s = document.querySelector('section.slide.active').cloneNode(true);
              s.querySelectorAll('aside.notes, mjx-container, .tip, text.tick').forEach((e) => e.remove()); // axis ticks are scale, not data
              const demo = [];
              for (const id of ill) s.querySelectorAll(`[data-component="${id}"]`).forEach((e) => { demo.push(e.innerHTML.replace(/<[^>]+>/g, ' ')); e.remove(); });
              const words = (r) => { const w = document.createTreeWalker(r, NodeFilter.SHOW_TEXT); const o = []; while (w.nextNode()) o.push(w.currentNode.textContent); return o.join(' '); };
              return [words(s), demo.join(' ')];
            }""", ILLUSTRATIVE)
            main_txt, demo_txt = txt
            seen = {}
            for m in re.finditer(r"(?<![\w.])\d+(?:,\d{3})*(?:\.\d+)?(?![\w])", main_txt.replace("−", "-")):
                v = m.group()
                if v in seen:
                    continue
                c = canon(v)
                if c in known:
                    seen[v] = "tex"
                elif v in ALLOW:
                    seen[v] = ALLOW[v]
                elif v in YEARS:
                    seen[v] = "year (reference)"
                else:
                    seen[v] = "UNMATCHED"
                    unmatched += 1
            for v, why in seen.items():
                if why != "tex":
                    rows.append((labels[i - 1], v, why))
            demo_nums = sorted(set(re.findall(r"\d+(?:\.\d+)?", demo_txt)))
            if demo_nums:
                rows.append((labels[i - 1], " ".join(demo_nums[:30]), "illustrative component (labelled on screen)"))
        b.close()
    out = ["# Number audit", "", "Numbers on slides that do not occur verbatim in `dissertation.tex`, with the reason they are allowed.",
           "Every other number on every slide was found in the `.tex`.", "", "| Slide | Number | Status |", "|---|---|---|"]
    out += [f"| {a} | {b_} | {c} |" for a, b_, c in rows]
    out += ["", f"Unmatched: {unmatched}"]
    (ROOT / "qa" / "number_audit.md").write_text("\n".join(out) + "\n", encoding="utf8")
    for a, b_, c in rows:
        if c == "UNMATCHED":
            print(f"UNMATCHED {a}: {b_}")
    print(f"number audit: {unmatched} unmatched")
    return unmatched == 0


if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
