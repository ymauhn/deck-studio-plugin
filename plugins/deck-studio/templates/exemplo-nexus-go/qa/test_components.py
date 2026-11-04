"""Component checks of docs/QA.md §2: 10 (INT-PROP), 11 (INT-PIPE), 13 (INT-DEDUP).

Usage: python -I qa/test_components.py [page.html]   (default: the full deck in deck/dist/)
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "qa" / "shots" / "components"

# INT-PIPE: route -> node ids that must stay at full opacity (docs/INTERACTIVES.md)
PIPE_ROUTES = {
    "fixed": {"seq", "prott5", "h0", "string", "dedup", "W", "P", "fixprop", "headfix", "pfix"},
    "gnn": {"seq", "prott5", "h0", "string", "dedup", "W", "edges", "gnn", "g", "headgnn", "pgnn"},
    "early": {"seq", "prott5", "h0", "string", "dedup", "W", "P", "fixprop", "edges", "gnn", "g", "early", "headearly", "outearly"},
    "late": {"seq", "prott5", "h0", "string", "dedup", "W", "P", "fixprop", "headfix", "pfix", "edges", "gnn", "g", "headgnn", "pgnn", "late", "out"},
}


def slide_of(page, cid):
    return page.evaluate(f"""(() => {{ const el = document.querySelector('[data-component="{cid}"]');
        if (!el) return 0; return [...document.querySelectorAll('section.slide')].indexOf(el.closest('section')) + 1; }})()""")


def run(url):
    fails, errors = [], []
    ok = lambda c, m: None if c else fails.append(m)
    SHOTS.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(url)
        page.wait_for_function("window.deck !== undefined")

        # ---- 10: INT-PROP ----
        k = slide_of(page, "INT-PROP")
        if k:
            page.evaluate(f"deck.go({k}, deck.steps()[{k - 1}])")
            c = "deck.component('INT-PROP')"
            before = page.evaluate(f"{c}.state().fills")
            page.locator("#prop-T").fill("6")
            mid = page.evaluate(f"{c}.state()")
            ok(mid["T"] == 6 and mid["fills"] != before, "INT-PROP: T slider does not change node fills")
            page.locator("#prop-alpha").fill("0.2")
            page.wait_for_timeout(500)
            st = page.evaluate(f"{c}.state()")
            ok(abs(st["alpha"] - 0.2) < 1e-9 and st["fills"] != mid["fills"], "INT-PROP: alpha slider does not change node fills")
            page.screenshot(path=str(SHOTS / "prop-T6-a02.png"))
            for T in range(0, 11):
                for a in (0.1, 0.3, 0.5, 0.7, 0.9):
                    s = page.evaluate(f"({c}.set({T}, {a}), {c}.state())")
                    ok(abs(s["sumWeights"] - 1) < 1e-9, f"INT-PROP: sum of hop weights {s['sumWeights']} at T={T} a={a}")
                    ok(s["closedFormError"] < 1e-9, f"INT-PROP: iterate != closed form ({s['closedFormError']}) at T={T} a={a}")
                    for iso in s["isolated"]:
                        ok(abs(iso["norm"] - a ** T * iso["initial"]) < 1e-6, f"INT-PROP: isolated node {iso['node']} norm at T={T} a={a}")
            page.evaluate(f"{c}.set(2, 0.5)")
        else:
            fails.append("INT-PROP not found")

        # ---- 11: INT-PIPE ----
        k = slide_of(page, "INT-PIPE")
        if k:
            page.evaluate(f"deck.go({k}, deck.steps()[{k - 1}])")
            page.wait_for_timeout(300)
            for route, want in PIPE_ROUTES.items():
                page.click(f"#pipe-{route}")
                page.wait_for_timeout(450)
                got = page.evaluate("""[...document.querySelectorAll('.pi-node')].map(n => [n.dataset.id, +getComputedStyle(n).opacity])""")
                ids = {i for i, _ in got}
                ok(want <= ids, f"INT-PIPE: missing node ids {want - ids}")
                for i, o in got:
                    if i in want:
                        ok(o > 0.99, f"INT-PIPE /{route}: {i} should be full opacity, is {o}")
                    else:
                        ok(o < 0.2, f"INT-PIPE /{route}: {i} should be dimmed, is {o}")
                page.screenshot(path=str(SHOTS / f"pipe-{route}.png"))
            page.click("#pipe-all")
            page.wait_for_timeout(450)
            dim = page.evaluate("""[...document.querySelectorAll('.pi-node')].filter(n => +getComputedStyle(n).opacity < 0.99).length""")
            ok(dim == 0, f"INT-PIPE /All: {dim} nodes dimmed")
            page.click("#pipe-fig")
            ok(page.is_visible(".pipe-fig"), "INT-PIPE: dissertation figure toggle")
            page.screenshot(path=str(SHOTS / "pipe-figure.png"))
            page.click("#pipe-fig")
            ok(not page.is_visible(".pipe-fig"), "INT-PIPE: figure toggle back")
        else:
            fails.append("INT-PIPE not found")

        # ---- 13: INT-DEDUP ----
        k = slide_of(page, "INT-DEDUP")
        if k:
            page.evaluate(f"deck.go({k}, deck.steps()[{k - 1}])")
            page.click("#dd-sum")
            ok(page.inner_text('[data-norm-v="A"]') == "0.81" and page.inner_text('[data-norm-v="B"]') == "0.19", "INT-DEDUP: sum does not show 0.81 / 0.19")
            page.click("#dd-max")
            ok(page.inner_text('[data-norm-v="A"]') == "0.46" and page.inner_text('[data-norm-v="B"]') == "0.54", "INT-DEDUP: max does not show 0.46 / 0.54")
            ok(page.evaluate("deck.state().slide") == k, "INT-DEDUP: clicking the toggle changed the slide")
        b.close()
    ok(not errors, f"console errors: {errors}")
    for f in fails:
        print("FAIL", f)
    print(f"components: {len(fails)} failures")
    return not fails


if __name__ == "__main__":
    target = Path(sys.argv[1]).resolve().as_uri() if len(sys.argv) > 1 else (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()
    sys.exit(0 if run(target) else 1)
