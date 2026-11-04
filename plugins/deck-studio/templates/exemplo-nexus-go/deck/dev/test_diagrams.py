"""Isolated test of INT-MP, INT-PLM, INT-RW, INT-RULES and INT-FUNNEL.

Build first:  node deck/build.mjs --page deck/dev/diagrams.html
Run:          python -I deck/dev/test_diagrams.py
Steps every component forward and back (component DOM and state must match), checks console
errors and containment, hovers and focuses every INT-RULES chip, checks reduced motion and the
INT-MP render(t) determinism, and saves screenshots of every step in both themes to
qa/shots/dev/diagrams/<theme>/<slide>-<step>.png.
"""
import json
import re
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGE = (ROOT / "deck" / "build" / "harness" / "diagrams.html").as_uri()
OUT = ROOT / "qa" / "shots" / "dev" / "diagrams"
TABLES = json.loads((ROOT / "deck" / "build" / "thesis_tables.json").read_text(encoding="utf8"))
# slide number, component id, number of steps
COMPS = [(1, "INT-MP", 4), (2, "INT-PLM", 4), (3, "INT-RW", 3), (4, "INT-RULES", 5), (5, "INT-FUNNEL", 3)]
SETTLE = 2700  # ms: longest transition chain (funnel line, PLM pooling, MP colour drift)

SNAP = """id => { const el = document.querySelector(`[data-component="${id}"]`);
  return { html: el.outerHTML, state: JSON.stringify(deck.component(id).state()) }; }"""
# every descendant box must sit inside the container (the INT-RULES popover is allowed above it)
CONTAIN = """id => { const el = document.querySelector(`[data-component="${id}"]`), c = el.getBoundingClientRect();
  const bad = [];
  for (const n of el.querySelectorAll('*')) {
    if (n.closest('.rls-pop') || n.closest('mjx-container')) continue;
    const r = n.getBoundingClientRect();
    if (!r.width && !r.height) continue;
    if (r.left < c.left - 1 || r.top < c.top - 1 || r.right > c.right + 1 || r.bottom > c.bottom + 1)
      bad.push(`${n.tagName}.${n.getAttribute('class') || ''} ${Math.round(r.left - c.left)},${Math.round(r.top - c.top)},${Math.round(r.right - c.left)},${Math.round(r.bottom - c.top)}`);
  }
  return { w: Math.round(c.width), h: Math.round(c.height), bad }; }"""
LATE = {r[0]: r[-1] for r in TABLES["late"]["rows"][1:]}
CHIPS = {"linear": "Linear interpolation (\\gamma)", "max": "Maximum", "min": "Minimum", "ic": "IC sigmoid",
         "degree": "Degree sigmoid", "master": "Master equation", "dt": "Stacking (decision tree)",
         "lr": "Stacking (logistic regression)", "mlp": "Stacking (MLP)", "rf": "Stacking (random forest)",
         "gb": "Stacking (gradient boosting)"}
SIZES = {"INT-MP": (696, 400), "INT-PLM": (817, 560), "INT-RW": (1424, 630), "INT-RULES": (1424, 110), "INT-FUNNEL": (1424, 360)}


def run():
    errors, fails = [], []
    check = lambda cond, msg: None if cond else fails.append(msg)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(PAGE)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")

        for theme in ("light", "dark"):
            (OUT / theme).mkdir(parents=True, exist_ok=True)
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            for k, cid, n in COMPS:
                fwd = []
                for f in range(n + 1):
                    page.evaluate(f"deck.go({k}, {f})")
                    page.wait_for_timeout(SETTLE)
                    fwd.append(page.evaluate(SNAP, cid))
                    page.screenshot(path=str(OUT / theme / f"{k}-{cid.lower()}-{f}.png"))
                    if theme == "light":
                        box = page.evaluate(CONTAIN, cid)
                        check((box["w"], box["h"]) == SIZES[cid], f"{cid} size {box['w']}x{box['h']}")
                        check(not box["bad"], f"{cid} step {f} outside container: {box['bad'][:5]}")
                for f in range(n, -1, -1):
                    page.evaluate(f"deck.go({k}, {f})")
                    page.wait_for_timeout(60)
                    got = page.evaluate(SNAP, cid)
                    check(got == fwd[f], f"{cid} {theme} step {f}: back != forward ({got['state']} vs {fwd[f]['state']})")

        page.evaluate("document.documentElement.dataset.theme = 'light'")
        # INT-MP: states and render(t) determinism
        st = [page.evaluate(f"(deck.go(1, {f}), deck.component('INT-MP').state())") for f in range(5)]
        check([s["hops"] for s in st] == [0, 0, 1, 2, 2] and st[4]["converged"] and not st[3]["converged"], f"INT-MP states {st}")
        dots = """() => [...document.querySelectorAll('[data-component="INT-MP"] .mp-msg')].filter(c => getComputedStyle(c.parentNode).display !== 'none').map(c => { const r = c.getBoundingClientRect(); return [Math.round(r.x * 10), Math.round(r.y * 10), +getComputedStyle(c).opacity]; })"""
        page.evaluate("deck.go(1, 3)")
        frame = lambda t: page.evaluate(f"deck.component('INT-MP').render({t})") or page.evaluate(dots)
        a, mid, c = frame(0.6), frame(1.9), frame(0.6)
        check(a == c and a != mid and len(a) == 12, f"INT-MP render(t) not deterministic ({len(a)} dots)")
        page.evaluate("deck.component('INT-MP').play()")

        # INT-FUNNEL: hidden before step 2, nine stations at 2, test at 3; derived counts
        fs = [page.evaluate(f"(deck.go(5, {f}), deck.component('INT-FUNNEL').state())") for f in range(4)]
        check([s["visible"] for s in fs] == [0, 0, 9, 10], f"INT-FUNNEL visible {[s['visible'] for s in fs]}")
        comp = [s["compared"] for s in fs[3]["stations"]]
        check(comp == ["2 compared", "6 compared", "4 compared", "T = 0–10, per head", "α = 0.1–0.9", "GCN vs GAT, 2 heads", "max vs sum", "60-run grid", "71 per ontology", ""], f"INT-FUNNEL counts {comp}")
        win = [s["winner"] for s in fs[3]["stations"]]
        check(win[3] == "T = 1/2/0 (vector)" and win[4] == "α = 0.7/0.8", f"INT-FUNNEL winners {win}")

        # INT-RULES: hidden before step 4; every chip by hover and by focus
        page.evaluate("deck.go(4, 3)")
        check(page.evaluate("deck.component('INT-RULES').state().visible") is False, "INT-RULES visible at step 3")
        check(not page.is_visible("#rls-linear"), "INT-RULES chip visible at step 3")
        page.evaluate("deck.go(4, 4)")
        page.wait_for_timeout(100)
        for i, (cid, row) in enumerate(CHIPS.items()):
            for how in ("hover", "focus"):
                page.mouse.move(5, 5)
                page.evaluate("document.activeElement && document.activeElement.blur()")
                page.hover(f"#rls-{cid}") if how == "hover" else page.focus(f"#rls-{cid}")
                pop = page.evaluate("""() => { const p = document.querySelector('.rls-pop'), r = p.getBoundingClientRect();
                  return { hidden: p.hidden, svg: !!p.querySelector('.rls-pop-eq svg'), text: p.innerText, top: r.top, left: r.left, right: r.right }; }""")
                st = page.evaluate("deck.component('INT-RULES').state()")
                num = re.findall(r"\d+\.\d\d", pop["text"])
                check(not pop["hidden"] and pop["svg"], f"INT-RULES {cid} {how}: popover {pop}")
                check(num and float(num[-1]) == LATE[row], f"INT-RULES {cid}: number {num} vs {LATE[row]}")
                check(st == {"visible": True, "active": cid}, f"INT-RULES {cid} state {st}")
                check(pop["top"] >= 0 and pop["left"] >= 0 and pop["right"] <= 1600, f"INT-RULES {cid} popover off canvas {pop}")
                if how == "hover" and cid in ("linear", "ic", "gb"):
                    page.screenshot(path=str(OUT / "light" / f"4-int-rules-pop-{cid}.png"))
        page.keyboard.press("Escape")
        check(page.evaluate("deck.component('INT-RULES').state().active") is None, "INT-RULES Escape")
        page.evaluate("document.documentElement.dataset.theme = 'dark'")
        page.hover("#rls-master")
        page.screenshot(path=str(OUT / "dark" / "4-int-rules-pop-master.png"))
        page.mouse.move(5, 5)
        page.evaluate("document.documentElement.dataset.theme = 'light'")
        check(page.evaluate("deck.state().slide") == 4, "INT-RULES interaction changed the slide")

        # reduced motion: final states at once, same component state as the normal run
        ctx = b.new_context(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        rp = ctx.new_page()
        rp.on("console", lambda m: m.type == "error" and errors.append("reduced: " + m.text))
        rp.goto(PAGE)
        rp.wait_for_function("window.deck !== undefined")
        (OUT / "reduced").mkdir(parents=True, exist_ok=True)
        for k, cid, n in COMPS:
            rp.evaluate(f"deck.go({k}, {n})")
            rp.wait_for_timeout(120)
            rs = rp.evaluate(f"deck.component('{cid}').state()")
            page.evaluate(f"deck.go({k}, {n})")
            ns = page.evaluate(f"deck.component('{cid}').state()")
            ns.pop("playing", None), rs.pop("playing", None)
            check(rs == ns, f"{cid} reduced state {rs} != {ns}")
            rp.screenshot(path=str(OUT / "reduced" / f"{k}-{cid.lower()}-{n}.png"))
        b.close()
    check(not errors, f"console errors: {errors}")
    for f in fails:
        print("FAIL", f)
    print(f"diagrams: {len(COMPS)} components, {len(fails)} failures")
    return not fails


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
