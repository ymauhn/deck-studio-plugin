"""Isolated test of the eight chart components. Usage:
    node deck/build.mjs --page deck/dev/charts.html
    python -I deck/dev/test_charts.py

Steps every chart 0..max and back (same DOM), checks console errors, overflow of the container,
tooltip by mouse and keyboard, the table toggle, reduced motion, the INT-TEST labels for every
tab × metric against thesis_tables.json, and saves screenshots in both themes.
"""
import json
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGE = (ROOT / "deck" / "build" / "harness" / "charts.html").as_uri()
OUT = ROOT / "qa" / "shots" / "dev" / "charts"
DATA = json.loads((ROOT / "deck" / "build" / "thesis_tables.json").read_text(encoding="utf-8"))
CHARTS = ["INT-G1", "INT-FL", "INT-LATE", "INT-VV", "INT-JOURNEY", "INT-TEST", "INT-COV", "INT-GAIN"]

EL = "(id) => [...document.querySelectorAll('[data-component]')].find((e) => e.dataset.component === id)"
OVERFLOW = """(id) => {
  const el = (%s)(id), r = el.getBoundingClientRect(), bad = [];
  for (const e of el.querySelectorAll('*')) {
    if (!e.checkVisibility({ visibilityProperty: true })) continue;
    const b = e.getBoundingClientRect();
    if (!b.width && !b.height) continue;
    if (b.left < r.left - 1 || b.top < r.top - 1 || b.right > r.right + 1 || b.bottom > r.bottom + 1)
      bad.push(`${e.tagName} "${(e.textContent || '').trim().slice(0, 28)}" [${Math.round(b.left - r.left)},${Math.round(b.top - r.top)} → ${Math.round(b.right - r.left)},${Math.round(b.bottom - r.top)}] in ${Math.round(r.width)}×${Math.round(r.height)}`);
    if (!(e instanceof SVGElement) && (e.scrollWidth > e.clientWidth + 1 || e.scrollHeight > e.clientHeight + 1) && getComputedStyle(e).overflow !== 'visible')
      bad.push(`${e.tagName}.${e.className} scrolls`);
  }
  return bad;
}""" % EL
SNAP = "(id) => (%s)(id).outerHTML" % EL
num = lambda t: float(t.replace("−", "-").replace("%", ""))


def run():
    errors, fails = [], []
    check = lambda cond, msg: None if cond else fails.append(msg)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: m.type in ("error", "warning") and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(PAGE)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        steps = page.evaluate("deck.steps()")

        for k, cid in enumerate(CHARTS, start=1):
            n = steps[k - 1]
            comp = f"deck.component('{cid}')"
            # forward then back: same DOM per step; nothing outside the container
            fwd = []
            for f in range(n + 1):
                page.evaluate(f"deck.go({k}, {f})")
                page.wait_for_timeout(320)
                fwd.append(page.evaluate(SNAP, cid))
                for x in page.evaluate(OVERFLOW, cid):
                    fails.append(f"{cid} step {f}: outside {x}")
            for f in range(n, -1, -1):
                page.evaluate(f"deck.go({k}, {f})")
                if page.evaluate(SNAP, cid) != fwd[f]:
                    fails.append(f"{cid}: step {f} differs going back")
            check(page.evaluate(f"typeof {comp}.state()") == "object", f"{cid}: state()")

            # final step: tooltip by mouse and by keyboard, table toggle
            page.evaluate(f"deck.go({k}, {n})")
            page.wait_for_timeout(320)
            el = page.locator(f"[data-component='{cid}']")
            mk = el.locator(".mk").first
            mk.hover()
            tip = el.locator(".tip")
            check(tip.is_visible() and tip.inner_text().strip(), f"{cid}: no tooltip on hover")
            for x in page.evaluate(OVERFLOW, cid):
                fails.append(f"{cid} tooltip: outside {x}")
            (OUT / "light").mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(OUT / "light" / f"{cid}-tip.png"))
            page.mouse.move(5, 5)
            el.locator(".ch-tb").focus()
            page.keyboard.press("Tab")
            check(tip.is_visible(), f"{cid}: no tooltip on keyboard focus")
            el.locator(".ch-tb").focus()
            page.keyboard.press("Enter")
            check(el.locator(".ch-tbl table.t").count() >= 1 and not el.locator("svg.chart").is_visible(), f"{cid}: table toggle")
            check(page.evaluate("deck.state().fragment") == n, f"{cid}: table button advanced the slide")
            for x in page.evaluate(OVERFLOW, cid):
                fails.append(f"{cid} table: outside {x}")
            for theme in ("light", "dark"):
                page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
                (OUT / theme).mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(OUT / theme / f"{cid}-table.png"))
            page.evaluate("document.documentElement.dataset.theme = 'light'")
            el.locator(".ch-tb").click()
            check(el.locator("svg.chart").is_visible(), f"{cid}: table toggle back")

        # INT-TEST: every tab × metric against the JSON; controls only from step 4
        k = CHARTS.index("INT-TEST") + 1
        el = page.locator("[data-component='INT-TEST']")
        for f in range(5):
            page.evaluate(f"deck.go({k}, {f})")
            check(el.locator("#test-CC").is_disabled() == (f < 4), f"INT-TEST: controls at step {f}")
        page.evaluate(f"deck.go({k}, 4)")
        el.locator("#test-CC").click()
        check(page.evaluate("deck.state().fragment") == 4, "INT-TEST: tab click advanced the slide")
        check(page.evaluate("deck.component('INT-TEST').state().ontology") == "CC", "INT-TEST: tab click")
        el.locator("#test-metric").select_option("Smin")
        check(page.evaluate("deck.component('INT-TEST').state().metric") == "Smin", "INT-TEST: metric select")
        metrics = el.locator("#test-metric option").evaluate_all("(os) => os.map((o) => o.value)")
        n_checked = 0
        for o in ("BP", "CC", "MF"):
            head, *body = DATA[f"test_{o}"]["rows"]
            for j, m in enumerate(metrics, start=1):
                page.evaluate(f"deck.component('INT-TEST').set('{o}', '{m}')")
                got = {e.get_attribute("data-v"): num(e.text_content()) for e in el.locator("[data-v]").all()}
                for r in body:
                    n_checked += 1
                    check(got.get(r[0]) == round(r[j], 2), f"INT-TEST {o} {m} {r[0]}: shows {got.get(r[0])}, table has {r[j]}")
                st = page.evaluate("deck.component('INT-TEST').state()")
                check(st["ontology"] == o and st["metric"] == m and len(st["values"]) == len(body), f"INT-TEST state {o} {m}")
                for x in page.evaluate(OVERFLOW, "INT-TEST"):
                    fails.append(f"INT-TEST {o} {m}: outside {x}")
        print(f"INT-TEST: {n_checked} rendered labels compared with thesis_tables.json")

        # screenshots of every step, both themes
        for theme in ("light", "dark"):
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            for k, cid in enumerate(CHARTS, start=1):
                for f in range(steps[k - 1] + 1):
                    page.evaluate(f"deck.go({k}, {f})")
                    page.wait_for_timeout(320)
                    page.screenshot(path=str(OUT / theme / f"{cid}-{f}.png"))

        # reduced motion: revealed marks are fully opaque at once
        ctx = b.new_context(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        rp = ctx.new_page()
        rp.on("pageerror", lambda e: errors.append(str(e)))
        rp.goto(PAGE)
        rp.wait_for_function("window.deck !== undefined")
        for k, cid in enumerate(CHARTS, start=1):
            rp.evaluate(f"deck.go({k}, {steps[k - 1]})")
            ops = rp.evaluate(f"(id) => [...({EL})(id).querySelectorAll('.o.on')].map((e) => getComputedStyle(e).opacity)", cid)
            check(all(o == "1" for o in ops), f"{cid}: reduced motion not final at once")
        b.close()

    check(not errors, f"console: {errors}")
    for f in fails:
        print("FAIL", f)
    print(f"charts: {len(CHARTS)} components, {len(fails)} failures")
    return not fails


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(0 if run() else 1)
