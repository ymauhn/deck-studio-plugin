"""Deck test suite: the 16 checks of docs/QA.md §2 against deck/dist/nexus-go-defense.html.

Usage: python -I qa/run_all.py            (writes qa/results.json and prints a summary)
Screenshots and contact sheets come from qa/shoot.py; component checks 10, 11, 13 from
qa/test_components.py (run here too).
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PT = os.environ.get("NX_PT") == "1"
DIST = ROOT / "deck" / "dist" / ("nexus-go-defesa-pt.html" if PT else "nexus-go-defense.html")  # NX_PT=1: Portuguese deck
URL = DIST.as_uri()
DATA = json.loads((ROOT / "deck" / "build" / "thesis_tables.json").read_text(encoding="utf8"))
CHARTS = ["INT-G1", "INT-FL", "INT-LATE", "INT-VV", "INT-JOURNEY", "INT-TEST", "INT-COV", "INT-GAIN"]
FIGS = [f"2.{i}" for i in range(1, 8)] + [f"4.{i}" for i in range(1, 4)] + [f"5.{i}" for i in range(1, 11)] + [f"6.{i}" for i in range(1, 7)]

results = {}


def record(n, name, fails):
    results[n] = {"check": name, "pass": not fails, "fails": fails[:40]}
    print(f"{n:>2} {'PASS' if not fails else 'FAIL'} {name}" + ("" if not fails else f"  ({len(fails)})"))
    for f in fails[:12]:
        print("     -", f)


def expected_steps():
    """Fragment steps per slide from docs/STORYLINE.md (max F number of each Reveal line)."""
    txt = (ROOT / "docs" / "STORYLINE.md").read_text(encoding="utf8")
    out = []
    for m in re.finditer(r"^### S(\d\d)\..*?^- \*\*Reveal\*\*: (.*?)(?=\n- \*\*|\n\n|\Z)", txt, re.S | re.M):
        line = m.group(2)
        nums = [int(x) for x in re.findall(r"F(\d)", line)]
        nums += [int(b) for _, b in re.findall(r"F(\d)\s*[–-]\s*F?(\d)", line)]
        out.append(max(nums) if nums else 0)
    return out


SLIDE = "document.querySelector('section.slide.active')"


def go_final(page, i):
    page.evaluate(f"deck.go({i}, deck.steps()[{i - 1}])")


def main():
    errors, failed_requests = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1600, "height": 900})
        page = ctx.new_page()
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("requestfailed", lambda r: failed_requests.append(r.url))
        page.goto(URL)
        page.wait_for_function("window.deck !== undefined")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(500)
        steps, labels = page.evaluate("deck.steps()"), page.evaluate("deck.labels()")
        st = page.evaluate("deck.state()")
        total = st["total"]

        # 2 slide count
        record(2, "slide count", [] if total == 45 and st["backups"] == 8 else [f"{total} main, {st['backups']} backup"])

        # 3 fragments: counts and forward/back DOM equality
        fails = []
        exp = expected_steps()
        for i, (got, want) in enumerate(zip(steps[:45], exp), start=1):
            if got != want:
                fails.append(f"S{i:02d}: {got} steps, storyline says {want}")
        if len(exp) != 45:
            fails.append(f"storyline parse found {len(exp)} slides")
        for i, n in enumerate(steps, start=1):
            page.evaluate(f"deck.go({i}, 0)")
            snaps = []
            for f in range(n + 1):
                page.evaluate(f"deck.go({i}, {f})")
                snaps.append(page.evaluate(f"{SLIDE}.querySelectorAll('.f.on, .fo.off').length"))
            for f in range(n, -1, -1):
                page.evaluate(f"deck.go({i}, {f})")
                if page.evaluate(f"{SLIDE}.querySelectorAll('.f.on, .fo.off').length") != snaps[f]:
                    fails.append(f"{labels[i - 1]} step {f}: fragment state differs going back")
                    break
        record(3, "fragments", fails)

        # 4 overflow and 5 overlap (final state of every slide)
        over, overlap = [], []
        for i, n in enumerate(steps, start=1):
            go_final(page, i)
            page.wait_for_timeout(350 if i not in (21, 30) else 3000)
            res = page.evaluate("""() => {
              const s = document.querySelector('section.slide.active');
              const vis = (el) => { for (let e = el; e && e !== s; e = e.parentElement) { const cs = getComputedStyle(e);
                  if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.05) return false; } return true; };
              const out = [], texts = [];
              for (const el of s.querySelectorAll('*')) {
                if (el.closest('aside.notes, .tip, [hidden]') || !vis(el)) continue;
                const r = el.getBoundingClientRect();
                if (r.width < 1 || r.height < 1) continue;
                if (r.left < -1 || r.top < -1 || r.right > 1601 || r.bottom > 901) out.push(`outside canvas: ${el.tagName.toLowerCase()}.${el.className && el.className.baseVal === undefined ? el.className : ''} ${Math.round(r.left)},${Math.round(r.top)},${Math.round(r.right)},${Math.round(r.bottom)}`);
                const cs = getComputedStyle(el);
                if (!el.closest('svg') && /block|flex|grid|list-item|table-cell/.test(cs.display) && el.clientWidth > 0 && cs.overflow !== 'visible' &&
                    (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)) out.push(`clipped: ${el.tagName.toLowerCase()}.${el.className} ${el.scrollWidth}x${el.scrollHeight} > ${el.clientWidth}x${el.clientHeight}`);
                // leaf text boxes outside components, for the overlap check
                if (!el.closest('[data-component], svg, mjx-container, table') && [...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim()))
                  texts.push({ t: el.textContent.trim().slice(0, 40), r: [r.left, r.top, r.right, r.bottom], el });
              }
              for (const c of s.querySelectorAll('[data-component]')) { if (!vis(c)) continue; const r = c.getBoundingClientRect(); texts.push({ t: 'component ' + c.dataset.component, r: [r.left, r.top, r.right, r.bottom], el: c }); }
              const ov = [];
              for (let a = 0; a < texts.length; a++) for (let b = a + 1; b < texts.length; b++) {
                const A = texts[a], B = texts[b];
                if (A.el.contains(B.el) || B.el.contains(A.el)) continue;
                const w = Math.min(A.r[2], B.r[2]) - Math.max(A.r[0], B.r[0]), h = Math.min(A.r[3], B.r[3]) - Math.max(A.r[1], B.r[1]);
                if (w > 3 && h > 3) ov.push(`"${A.t}" overlaps "${B.t}"`);
              }
              return { out: out.slice(0, 8), ov: ov.slice(0, 8) };
            }""")
            over += [f"{labels[i - 1]}: {x}" for x in res["out"]]
            overlap += [f"{labels[i - 1]}: {x}" for x in res["ov"]]
        record(4, "overflow", over)
        record(5, "overlap", overlap)

        # 6 figures
        fails = []
        caps = page.evaluate("[...document.querySelectorAll('figcaption, .cap')].map(c => c.textContent).join(' | ')")
        for f in FIGS:
            if not re.search(rf"Figs?\.[^|]*\b{re.escape(f)}\b", caps):
                fails.append(f"Fig. {f} not captioned on any slide")
        bad = page.evaluate("""[...document.querySelectorAll('section.slide img')].filter(i => !i.alt.trim() || !i.naturalWidth).map(i => (i.alt || i.src.slice(0, 40)))""")
        fails += [f"img without alt or not loaded: {x}" for x in bad]
        record(6, "figures", fails)

        # 7 keys
        fails = []
        page.evaluate("deck.go(1, 0)")
        def key(k, want, msg):
            page.keyboard.press(k)
            got = page.evaluate("deck.state()")
            if any(got[x] != v for x, v in want.items()):
                fails.append(f"{msg}: {got}")
        key("ArrowRight", {"slide": 2}, "ArrowRight")
        key("ArrowLeft", {"slide": 1}, "ArrowLeft")
        key("Space", {"slide": 2}, "Space")
        page.evaluate("deck.go(3, 0)")
        key("PageDown", {"slide": 3, "fragment": 1}, "PageDown")
        key("PageUp", {"slide": 3, "fragment": 0}, "PageUp")
        key("End", {"slide": 45}, "End")
        key("Home", {"slide": 1}, "Home")
        key("b", {"label": "B1"}, "B")
        page.keyboard.press("o")
        if not page.evaluate("document.getElementById('deck').classList.contains('ov')"): fails.append("O overview")
        page.keyboard.press("o")
        page.keyboard.press("n")
        if not page.is_visible("#notes"): fails.append("N notes")
        page.keyboard.press("n")
        t0 = page.evaluate("document.documentElement.dataset.theme || ''")
        page.keyboard.press("t")
        if page.evaluate("document.documentElement.dataset.theme") == t0: fails.append("T theme")
        page.keyboard.press("t")
        page.goto(URL + "#24")
        page.wait_for_function("window.deck !== undefined")
        if page.evaluate("deck.state().slide") != 24: fails.append("#24 deep link")
        record(7, "keys", fails)

        # 8 contrast (light and dark), body >= 4.5, captions >= 3
        fails = []
        for theme in ("light", "dark"):
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            for i, n in enumerate(steps, start=1):
                go_final(page, i)
                low = page.evaluate("""() => {
                  const s = document.querySelector('section.slide.active');
                  const rgb = (c) => { const m = c.match(/[\\d.]+/g); return m ? m.map(Number) : null; };
                  const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
                  const bg = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c && (c.length < 4 || c[3] > .5)) return c; } return [255, 255, 255]; };
                  const out = [];
                  for (const el of s.querySelectorAll('*')) {
                    if (el.closest('aside.notes, svg, mjx-container, .tip, [hidden], .plate') || ![...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim())) continue;
                    const cs = getComputedStyle(el); if (+cs.opacity < .5 || cs.visibility === 'hidden') continue;
                    const fg = rgb(cs.color), b = bg(el); if (!fg) continue;
                    const L1 = lum(fg), L2 = lum(b), cr = (Math.max(L1, L2) + .05) / (Math.min(L1, L2) + .05);
                    const cap = el.closest('.cap, figcaption, .hd .part, #num') || parseFloat(cs.fontSize) <= 18;
                    if (cr < (cap ? 3 : 4.5)) out.push(`${cr.toFixed(2)} "${el.textContent.trim().slice(0, 30)}"`);
                  }
                  return out.slice(0, 5);
                }""")
                fails += [f"{theme} {labels[i - 1]}: {x}" for x in low]
        page.evaluate("document.documentElement.dataset.theme = 'light'")
        record(8, "contrast", fails)

        # 12 INT-TEST values vs JSON (rendered labels)
        fails = []
        k = page.evaluate("[...document.querySelectorAll('section.slide')].indexOf(document.querySelector('[data-component=\"INT-TEST\"]').closest('section')) + 1")
        go_final(page, k)
        page.wait_for_timeout(300)
        head = DATA["test_BP"]["rows"][0]
        metric_ids = page.evaluate("[...document.querySelectorAll('#test-metric option')].map(o => o.value)")
        for ont in ("BP", "CC", "MF"):
            page.click(f"#test-{ont}")
            for mi, mv in enumerate(metric_ids):
                page.select_option("#test-metric", mv)
                page.wait_for_timeout(120)
                labels_txt = page.evaluate("""[...document.querySelector('[data-component="INT-TEST"]').querySelectorAll('text, .val, [data-val]')].map(t => t.textContent.trim())""")
                if PT:  # NX_PT=1: the Portuguese deck writes a decimal comma
                    labels_txt = [x.replace(",", ".") for x in labels_txt]
                vals = {re.sub(r"[^\d.]", "", x) for x in labels_txt if re.fullmatch(r"[−+-]?\d+\.\d{2}", x.strip())}
                for row in DATA[f"test_{ont}"]["rows"][1:]:
                    name, v = row[0], row[1 + mi]
                    if isinstance(v, float) and not name.lower().startswith("naive") and f"{v:.2f}" not in vals:
                        fails.append(f"{ont} {head[1 + mi]}: {name} {v:.2f} not among rendered labels")
        record(12, "INT-TEST values", fails)

        # 14 charts: tooltip and table toggle
        fails = []
        for cid in CHARTS:
            k = page.evaluate(f"[...document.querySelectorAll('section.slide')].indexOf(document.querySelector('[data-component=\"{cid}\"]').closest('section')) + 1")
            go_final(page, k)
            page.wait_for_timeout(400)
            root = f'[data-component="{cid}"]'
            marks = page.locator(f"{root} [data-tip], {root} [data-interactive]")
            hovered = False
            for j in range(min(marks.count(), 6)):
                try:
                    marks.nth(j).hover(timeout=1500)
                    page.wait_for_timeout(120)
                    if page.evaluate(f"[...document.querySelectorAll('{root} .tip, body > .tip')].some(t => !t.hidden && getComputedStyle(t).display !== 'none' && getComputedStyle(t).visibility !== 'hidden' && t.textContent.trim())"):
                        hovered = True
                        break
                except Exception:
                    pass
            if not hovered:
                fails.append(f"{cid}: no tooltip on hover")
            btn = page.locator(f"{root} button", has_text=re.compile("tabela" if PT else "table", re.I))
            if btn.count() == 0:
                fails.append(f"{cid}: no table toggle")
            else:
                btn.first.click()
                if not page.evaluate(f"!!document.querySelector('{root} table') && document.querySelector('{root} table').offsetParent !== null"):
                    fails.append(f"{cid}: table toggle shows no table")
                btn.first.click()
            page.mouse.move(5, 5)
        record(14, "charts: tooltip and table", fails)

        # 1 load
        record(1, "load", [f"console: {e}" for e in errors] + [f"request failed: {u}" for u in failed_requests if "fonts.g" not in u])

        # 9 reduced motion
        fails = []
        rctx = b.new_context(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        rp = rctx.new_page()
        rerr = []
        rp.on("pageerror", lambda e: rerr.append(str(e)))
        rp.goto(URL)
        rp.wait_for_function("window.deck !== undefined")
        for i, n in enumerate(steps, start=1):
            go_final(page, i); go_final(rp, i)
            page.wait_for_timeout(3000 if i in (21, 30) else 300)
            a = page.evaluate(f"[{SLIDE}.querySelectorAll('.f.on').length, {SLIDE}.innerText.replace(/\\s+/g, ' ')]")
            r = rp.evaluate(f"[{SLIDE}.querySelectorAll('.f.on').length, {SLIDE}.innerText.replace(/\\s+/g, ' ')]")
            if a[0] != r[0]:
                fails.append(f"{labels[i - 1]}: {r[0]} fragments shown with reduced motion vs {a[0]}")
            elif a[1] != r[1]:
                fails.append(f"{labels[i - 1]}: text differs with reduced motion")
        fails += [f"pageerror: {e}" for e in rerr]
        rctx.close()
        record(9, "reduced motion", fails)

        # 16 offline
        fails = []
        octx = b.new_context(viewport={"width": 1600, "height": 900})
        octx.route(re.compile(r"^https?://"), lambda route: route.abort())
        op = octx.new_page()
        op.goto(URL)
        op.wait_for_function("window.deck !== undefined")
        op.evaluate("document.fonts.ready")
        for fam in ("Atkinson Hyperlegible Next", "Bricolage Grotesque", "IBM Plex Mono"):
            if not op.evaluate(f"document.fonts.check('16px \"{fam}\"') && [...document.fonts].some(f => f.family.replace(/\"/g, '') === '{fam}' && f.status === 'loaded')"):
                fails.append(f"font not available offline: {fam}")
        bad = op.evaluate("[...document.querySelectorAll('img')].filter(i => { i.loading = 'eager'; return !i.complete || !i.naturalWidth; }).length")
        if bad:
            fails.append(f"{bad} images not rendered offline")
        octx.close()
        record(16, "offline", fails)
        b.close()

    # 15 size
    mb = DIST.stat().st_size / 1024 / 1024
    record(15, f"size {mb:.2f} MB", [] if mb < 12 else [f"{mb:.2f} MB"])

    # 10, 11, 13 component checks
    r = subprocess.run([sys.executable, "-I", str(ROOT / "qa" / "test_components.py")], capture_output=True, text=True)
    lines = [l for l in r.stdout.splitlines() if l.startswith("FAIL")]
    for n, tag in ((10, "INT-PROP"), (11, "INT-PIPE"), (13, "INT-DEDUP")):
        record(n, tag, [l for l in lines if tag in l or ("console" in l and n == 10)])

    out = {k: results[k] for k in sorted(results)}
    (ROOT / "qa" / ("results-pt.json" if os.environ.get("NX_PT") == "1" else "results.json")).write_text(json.dumps(out, indent=1), encoding="utf8")
    bad = [k for k, v in out.items() if not v["pass"]]
    print(f"\n{16 - len(bad)} of 16 checks pass" + (f"; failing: {bad}" if bad else ""))
    return not bad


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
