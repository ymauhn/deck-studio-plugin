"""Smoke test of the deck engine (Phase 3). Usage: python -I qa/test_smoke.py

Opens deck/dist/nexus-go-defense.html over file://, checks the engine contract and saves
screenshots of every slide (final fragment state) in both themes to qa/shots/smoke/.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DECK = (ROOT / "deck" / "dist" / "nexus-go-defense.html").as_uri()
OUT = ROOT / "qa" / "shots" / "smoke"


def run():
    errors, fails = [], []
    check = lambda cond, msg: None if cond else fails.append(msg)
    with sync_playwright() as p:
        b = p.chromium.launch()
        # reduced motion: reveal animations jump to their end, so forward and back snapshots compare state only
        page = b.new_page(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(DECK)
        page.wait_for_function("window.deck !== undefined")
        st = page.evaluate("deck.state()")
        check(st["slide"] == 1 and st["fragment"] == 0, f"initial state {st}")
        steps = page.evaluate("deck.steps()")
        total = len(steps)

        # forward through every step, then back to the start, comparing DOM snapshots
        # class order is not state: normalize it before comparing snapshots
        snap = """(() => { const c = document.querySelector('section.slide.active').cloneNode(true);
      // ambient animation (time-based, not fragment state) is left out of the comparison
      c.querySelectorAll('[data-component="INT-HERO"], [data-component="INT-FOLD"], .pi-dots, [data-component="INT-MP"] animateMotion').forEach((e) => e.replaceChildren());
      for (const e of [c, ...c.querySelectorAll('[class]')]) { const k = [...e.classList].sort(); e.removeAttribute('class'); if (k.length) e.setAttribute('class', k.join(' ')); }
      return c.outerHTML; })()"""
        seen = []
        for _ in range(sum(steps) + total - 1):
            seen.append((page.evaluate("JSON.stringify(deck.state())"), page.evaluate(snap)))
            page.keyboard.press("ArrowRight")
        last = page.evaluate("deck.state()")
        check(last["label"] == "B8" and last["fragment"] == steps[-1], f"end state {last}")
        for want in reversed(seen):
            page.keyboard.press("ArrowLeft")
            got = (page.evaluate("JSON.stringify(deck.state())"), page.evaluate(snap))
            if got != want:
                i = next((k for k, (x, y) in enumerate(zip(got[1], want[1])) if x != y), 0)
                fails.append(f"back-step mismatch at {got[0]}: ...{got[1][max(0, i - 120):i + 80]}... vs ...{want[1][max(0, i - 120):i + 80]}...")
                break

        # clicker keys and deep link
        page.keyboard.press("PageDown"); check(page.evaluate("deck.state().slide") == 2, "PageDown")
        page.keyboard.press("PageUp"); check(page.evaluate("deck.state().slide") == 1, "PageUp")
        page.keyboard.press("End"); check(page.evaluate("deck.state().slide") == page.evaluate("deck.state().total"), "End")
        page.keyboard.press("Home"); check(page.evaluate("deck.state().slide") == 1, "Home")
        page.goto(DECK + "#2"); page.wait_for_function("window.deck !== undefined")
        check(page.evaluate("deck.state().slide") == 2, "deep link #2")

        # overlays
        page.keyboard.press("n"); check(page.is_visible("#notes"), "notes open")
        check(len(page.inner_text("#notes-body")) > 20, "notes text")
        page.keyboard.press("n"); check(not page.is_visible("#notes"), "notes close")
        page.keyboard.press("o"); check(page.evaluate("document.getElementById('deck').classList.contains('ov')"), "overview")
        page.screenshot(path=str(OUT / "overview.png"))
        page.keyboard.press("o")
        page.keyboard.press("t"); check(page.evaluate("document.documentElement.dataset.theme") == "dark", "theme dark")
        page.keyboard.press("t"); check(page.evaluate("document.documentElement.dataset.theme") == "light", "theme light")
        page.keyboard.press("?"); check(page.is_visible("#help"), "help")
        page.keyboard.press("Escape"); check(not page.is_visible("#help"), "help close")

        # screenshots, final state of each slide, both themes
        for theme in ("light", "dark"):
            (OUT / theme).mkdir(parents=True, exist_ok=True)
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            for i, n in enumerate(steps, start=1):
                page.evaluate(f"deck.go({i}, {n})")
                page.wait_for_timeout(450)
                page.screenshot(path=str(OUT / theme / f"{i:02d}.png"))
        b.close()
    check(not errors, f"console errors: {errors}")
    for f in fails:
        print("FAIL", f)
    print(f"smoke: {total} slides, {sum(steps)} steps, {len(fails)} failures")
    return not fails


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    sys.exit(0 if run() else 1)
