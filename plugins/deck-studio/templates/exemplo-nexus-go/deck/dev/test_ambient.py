"""Dev test of INT-HERO, INT-FOLD, INT-GAP and INT-GBA. Usage:
    node deck/build.mjs --page deck/dev/ambient.html
    python -I deck/dev/test_ambient.py
Screenshots go to qa/shots/dev/ambient/.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PAGE = (ROOT / "deck" / "build" / "harness" / "ambient.html").as_uri()
OUT = ROOT / "qa" / "shots" / "dev" / "ambient"
SEL = {
    "INT-HERO": "#dev1 [data-component]",
    "HERO-CALM": "#dev2 [data-component]",
    "INT-FOLD": '#dev3 [data-component="INT-FOLD"]',
    "INT-GAP": '#dev3 [data-component="INT-GAP"]',
    "INT-GBA": "#dev4 [data-component]",
}
CONTAIN = """(sel) => {
  const c = document.querySelector(sel), r = c.getBoundingClientRect(), bad = [];
  for (const n of c.querySelectorAll('*')) {
    const b = n.getBoundingClientRect();
    if (!b.width && !b.height) continue;
    if (b.left < r.left - 1 || b.top < r.top - 1 || b.right > r.right + 1 || b.bottom > r.bottom + 1)
      bad.push(`${n.tagName}.${n.getAttribute('class')} ${Math.round(b.left)},${Math.round(b.top)},${Math.round(b.right)},${Math.round(b.bottom)}`);
  }
  return bad;
}"""
# Eq. 5.3 on the illustrative data, computed here independently of the component
NB = [(0.88, "A"), (0.45, "ABC"), (0.99, "AB"), (0.62, "BC"), (0.93, "A"), (0.71, "B")]
S = sum(s for s, _ in NB)
WANT_PCT = {k: round(100 * sum(s for s, t in NB if k in t) / S) for k in "ABC"}


def run():
    errors, fails = [], []
    check = lambda cond, msg: None if cond else fails.append(msg)
    OUT.mkdir(parents=True, exist_ok=True)

    def page_for(browser, **kw):
        page = browser.new_page(viewport={"width": 1600, "height": 900}, **kw)
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.goto(PAGE)
        page.wait_for_function("window.deck !== undefined")
        return page

    with sync_playwright() as p:
        b = p.chromium.launch()
        page = page_for(b)
        ev = page.evaluate
        comp = lambda cid, js: ev(f"deck.component('{cid}').{js}")
        shot = lambda key, path=None: page.locator(SEL[key]).screenshot(**({"path": str(path)} if path else {}))
        contained = lambda key, where: (lambda bad: check(not bad, f"{key} overflow at {where}: {bad[:4]}"))(ev(CONTAIN, SEL[key]))

        def set_theme(theme):
            ev(f"document.documentElement.dataset.theme = '{theme}'")
            ev("deck.component('INT-FOLD') && deck.component('INT-FOLD').theme()")

        def ambient(key, cid, ts, get=None):
            """animating while playing, frozen after pause, render(t) frames, seamless loop"""
            get = get or (lambda js: comp(cid, js))
            a = shot(key); page.wait_for_timeout(500); b2 = shot(key)
            check(a != b2, f"{key}: not animating while playing")
            get("pause()")
            check(get("state()")["playing"] is False, f"{key}: still playing after pause")
            a = shot(key); page.wait_for_timeout(500); b2 = shot(key)
            check(a == b2, f"{key}: changed after pause()")
            frames = {}
            for t in ts:
                get(f"render({t})")
                frames[t] = shot(key, OUT / f"{key.lower()}-t{t:05.2f}.png")
                contained(key, f"t={t}")
            cyc = get("state()")["cycle"]
            get(f"render({cyc})")
            check(shot(key) == frames[0], f"{key}: render(cycle) differs from render(0), loop not seamless")
            return frames

        # ---- INT-HERO ----
        ev("deck.go(1, 0)"); page.wait_for_timeout(400)
        ambient("INT-HERO", "INT-HERO", [0, 2, 4, 6, 8, 10])
        st = comp("INT-HERO", "state()")
        check(st["beads"] in range(12, 17) and st["nodes"] == 10 and st["cycle"] == 12, f"hero state {st}")
        comp("INT-HERO", "step(0)"); comp("INT-HERO", "render(0)")
        h0 = shot("INT-HERO"); comp("INT-HERO", "step(3)"); check(shot("INT-HERO") == h0, "hero: step(n) changed the frame")

        # calm hero (S45): the engine exposes only the first instance, so mount a second one
        ev("deck.go(2, 0)"); page.wait_for_timeout(300)
        ev(f"window.__calm = NX.registry['INT-HERO'](document.querySelector('{SEL['HERO-CALM']}'), {{ ...NX.ctx, calm: true, reduced: false, slide: 2 }}); __calm.play()")
        page.wait_for_timeout(300)
        ambient("HERO-CALM", None, [0, 3, 6, 9], get=lambda js: ev(f"__calm.{js}"))
        check(ev("__calm.state().calm") is True, "calm flag")

        # ---- S03: INT-FOLD and INT-GAP, forward then back ----
        snaps = {}
        for n in range(0, 4):
            ev(f"deck.go(3, {n})"); page.wait_for_timeout(1400)
            snaps[n] = ev(f"[document.querySelector('{SEL['INT-FOLD']}').outerHTML, document.querySelector('{SEL['INT-GAP']}').outerHTML]")
            gs = comp("INT-GAP", "state()")
            check(gs["widths"] == ([1, 0.1] if n >= 2 else [0, 0]), f"gap widths at {n}: {gs}")
            if n >= 2:
                w = ev(f"[...document.querySelectorAll('{SEL['INT-GAP']} .gp-bar')].map(b => b.getBoundingClientRect().width / b.parentElement.getBoundingClientRect().width)")
                check(abs(w[0] - 1) < 0.01 and abs(w[1] - 0.1) < 0.01, f"gap rendered widths {w}")
        for n in range(3, -1, -1):
            ev(f"deck.go(3, {n})"); page.wait_for_timeout(300)
            got = ev(f"[document.querySelector('{SEL['INT-FOLD']}').outerHTML, document.querySelector('{SEL['INT-GAP']}').outerHTML]")
            check(got == snaps[n], f"S03 back-step DOM mismatch at fragment {n}")
        ev("deck.go(3, 3)"); page.wait_for_timeout(1400)
        contained("INT-GAP", "final"); contained("INT-FOLD", "playing")
        for t in (0, 0.6, 1.2):
            comp("INT-GAP", f"render({t})"); shot("INT-GAP", OUT / f"int-gap-t{t:04.2f}.png")
        comp("INT-GAP", "step(3)")
        # the fold restarted from the extended chain when it was revealed; check phases
        ts = [0, 0.8, 1.8, 2.8, 3.8, 4.8, 7, 10.7, 11.3]
        ambient("INT-FOLD", "INT-FOLD", ts)
        want = {0: "extended", 0.8: "folding", 4.8: "folded", 7: "folded", 10.7: "folded", 11.3: "unfolding"}
        for t, ph in want.items():
            comp("INT-FOLD", f"render({t})")
            got = comp("INT-FOLD", "state()")["phase"]
            check(got == ph, f"fold phase at {t}: {got} != {ph}")
        check(comp("INT-FOLD", "state()")["cycle"] == 12, "fold cycle")
        # GIF size: mount a 480 x 420 copy and render a frame
        ev("""(() => { const d = document.createElement('div'); d.id = 'gif'; d.style.cssText = 'position:fixed;left:0;top:0;width:480px;height:420px;background:var(--slide);z-index:99';
                 document.body.append(d); window.__gif = NX.registry['INT-FOLD'](d, { ...NX.ctx, reduced: false }); __gif.render(6); })()""")
        page.locator("#gif").screenshot(path=str(OUT / "int-fold-gif-480x420-t06.png"))
        bad = ev(CONTAIN, "#gif"); check(not bad, f"fold 480x420 overflow {bad}")
        ev("__gif.destroy(); document.getElementById('gif').remove()")

        # ---- S05: INT-GBA ----
        snaps = {}
        for n in range(0, 4):
            ev(f"deck.go(4, {n})"); page.wait_for_timeout(2600 if n == 2 else 300)
            snaps[n] = ev(f"document.querySelector('{SEL['INT-GBA']}').outerHTML")
            st = comp("INT-GBA", "state()")
            check(st["phase"] == ("final" if n >= 2 else "question"), f"gba phase at {n}: {st['phase']}")
        for n in range(3, -1, -1):
            ev(f"deck.go(4, {n})"); page.wait_for_timeout(300)
            check(ev(f"document.querySelector('{SEL['INT-GBA']}').outerHTML") == snaps[n], f"GBA back-step DOM mismatch at fragment {n}")
        st = comp("INT-GBA", "state()")
        check(st["percent"] == WANT_PCT, f"gba percent {st['percent']} != {WANT_PCT}")
        check(st["confidences"] == [0.88, 0.45, 0.99, 0.62, 0.93, 0.71], "gba confidences")
        legend = ev(f"document.querySelector('{SEL['INT-GBA']} .gb-legend').innerText")
        for k, v in WANT_PCT.items():
            check(f"{v}%" in legend, f"legend lacks {k} {v}%: {legend!r}")
        ev("deck.go(4, 2)"); page.wait_for_timeout(700)
        check(comp("INT-GBA", "state()")["phase"] == "animating", "gba: no reveal animation at step 2")
        page.wait_for_timeout(2000)
        check(comp("INT-GBA", "state()")["phase"] == "final", "gba: reveal did not finish")
        for t in (0, 0.5, 1.0, 1.4, 1.8, 2.3):
            comp("INT-GBA", f"render({t})"); shot("INT-GBA", OUT / f"int-gba-t{t:03.1f}.png"); contained("INT-GBA", f"t={t}")
        comp("INT-GBA", "step(3)")

        # ---- slide screenshots, both themes ----
        steps = {1: [0], 2: [0], 3: [0, 1, 2, 3], 4: [0, 2, 3]}
        for theme in ("light", "dark"):
            (OUT / theme).mkdir(exist_ok=True)
            set_theme(theme)
            for s, ns in steps.items():
                for n in ns:
                    ev(f"deck.go({s}, {n})"); page.wait_for_timeout(2600 if s == 4 and n == 2 else 1400)
                    if s == 3 and n >= 1:
                        comp("INT-FOLD", "render(7)")  # folded frame, comparable across runs
                    page.screenshot(path=str(OUT / theme / f"s{s}-{n}.png"))
            ev("deck.go(3, 1)"); page.wait_for_timeout(200)
            for t in (0, 3, 7):
                comp("INT-FOLD", f"render({t})"); shot("INT-FOLD", OUT / theme / f"fold-t{t}.png")
        set_theme("light")
        page.close()

        # ---- reduced motion ----
        page = page_for(b, reduced_motion="reduce")
        ev = page.evaluate
        comp = lambda cid, js: ev(f"deck.component('{cid}').{js}")
        shot = lambda key, path=None: page.locator(SEL[key]).screenshot(**({"path": str(path)} if path else {}))
        ev("deck.go(1, 0)"); page.wait_for_timeout(300)
        check(comp("INT-HERO", "state()")["playing"] is False, "reduced: hero plays")
        a = shot("INT-HERO"); page.wait_for_timeout(500); check(a == shot("INT-HERO"), "reduced: hero moves")
        ev("deck.go(3, 1)"); page.wait_for_timeout(300)
        st = comp("INT-FOLD", "state()")
        check(st["phase"] == "folded" and st["playing"] is False, f"reduced fold state {st}")
        a = shot("INT-FOLD"); page.wait_for_timeout(500); check(a == shot("INT-FOLD"), "reduced: fold moves")
        ev("deck.go(3, 2)")
        w = ev(f"[...document.querySelectorAll('{SEL['INT-GAP']} .gp-bar')].map(b => b.getBoundingClientRect().width / b.parentElement.getBoundingClientRect().width)")
        check(abs(w[0] - 1) < 0.01 and abs(w[1] - 0.1) < 0.01, f"reduced: gap not final at once {w}")
        page.wait_for_timeout(300); page.screenshot(path=str(OUT / "reduced-s3-2.png"))
        ev("deck.go(4, 2)")
        check(comp("INT-GBA", "state()")["phase"] == "final", "reduced: gba not final at once")
        page.wait_for_timeout(300); page.screenshot(path=str(OUT / "reduced-s4-2.png"))
        b.close()

    check(not errors, f"console errors: {errors}")
    for f in fails:
        print("FAIL", f)
    print(f"ambient: {len(fails)} failures")
    return not fails


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
