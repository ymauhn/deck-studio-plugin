"""Deck checks: the NEXUS-GO kit's qa/run_all.py, ported (checks 1, 3-9, 14-16), plus two text checks of the method.

Usage: python -I -X utf8 qa/check_deck.py [deck.html]     (default: deck/dist/deck.html; build it first:
       python -I -X utf8 deck/build.py)
Reads docs/STORYLINE.md (the steps of each slide, by id) and docs/FIGURES.md (the label of each figure the deck must
show). Writes qa/results.json and prints one line per check; exits 1 when a check fails.
Only Playwright and the standard library: it runs the same in Deck Studio and in any Claude Code project.

 1 load        no console error, no failed request
 3 steps       each slide's steps equal its "Passos" in STORYLINE.md; stepping back restores each state
 4 overflow    every visible box inside the 1600x900 canvas; no text box clipped
 5 overlap     no two text boxes of a slide intersect
 6 figures     each label of FIGURES.md is in a slide's caption; every <img> has alt and loaded
 7 keys        arrows, Space, PageUp/PageDown, Home/End, O, N, T and a #n deep link
 8 contrast    body text >= 4.5:1 and captions >= 3:1, in light and dark
 9 reduced     with reduced motion, every slide's final state is the same
14 charts      every figure.chart has a <title> on its marks and a <details> table
15 size        the deck file under 12 MB
16 offline     with the network blocked, the three embedded fonts load and every image renders
17 notes       every slide has speaker notes that end with the source page: (p. 12) or (pp. 3-4) or (-) for none
18 text        no em dash in slide text or notes; at most 5 items in a list
19 visuals     at least the briefing's animated diagrams (FLUXO) and data charts (BARRAS, ESCADA, PONTOS), by
               default 1 and 2 (docs/briefing.json, "interatividade"); every component mounted
"""
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DECK = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "deck" / "dist" / "deck.html"
FONTS = ("Atkinson Hyperlegible Next", "Bricolage Grotesque", "IBM Plex Mono")
SLIDE = "document.querySelector('section.slide.active')"
results = {}


def record(n, name, fails):
    results[n] = {"check": name, "pass": not fails, "fails": fails[:40]}
    print(f"{n:>2} {'PASS' if not fails else 'FAIL'} {name}" + ("" if not fails else f"  ({len(fails)})"), flush=True)
    for f in fails[:12]:
        print("     -", f, flush=True)


def storyline_steps():
    """{slide id: steps} from docs/STORYLINE.md: `### s07 · Title` and `- **Passos**: F1–F3` (or `nenhum`, or a
    number). None when the file is missing."""
    path = ROOT / "docs" / "STORYLINE.md"
    if not path.is_file():
        return None
    out = {}
    for m in re.finditer(r"^###\s+(\w+)\s*[·.:-].*?^- \*\*Passos\*\*:\s*(.*?)$", path.read_text(encoding="utf-8"),
                         re.S | re.M):
        line = m[2].strip()
        nums = [int(x) for x in re.findall(r"F(\d+)", line)] + ([int(line)] if line.isdigit() else [])
        out[m[1]] = max(nums) if nums else 0
    return out


def visuals_wanted():
    """The minimum animated diagrams and data charts: docs/briefing.json "interatividade", else 1 and 2."""
    want = {"diagramas": 1, "graficos": 2}
    f = ROOT / "docs" / "briefing.json"
    try:
        got = json.loads(f.read_text(encoding="utf-8")).get("interatividade") if f.is_file() else None
    except ValueError:
        got = None
    if isinstance(got, dict):
        want.update({k: int(got[k]) for k in want if isinstance(got.get(k), (int, float))})
    return want


def figure_labels():
    """The Rótulo column of docs/FIGURES.md (`Fig. 3`), the rows of its table."""
    path = ROOT / "docs" / "FIGURES.md"
    if not path.is_file():
        return []
    labels = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) > 2 and line.lstrip().startswith("|") and not set(cells[0]) <= set("-: ") \
                and cells[0].lower() not in ("rótulo", "rotulo", "label") and not cells[0].startswith("["):
            labels.append(cells[0])
    return labels


def go_final(page, i):
    page.evaluate(f"deck.go({i}, deck.steps()[{i - 1}])")


def open_deck(page):
    page.goto(DECK.as_uri())
    page.wait_for_function("window.deck !== undefined")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(300)


def main():
    if not DECK.is_file():
        print(f"no deck at {DECK}: build it first (python -I -X utf8 deck/build.py)")
        return False
    errors, failed = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: m.type == "error" and errors.append(m.text))
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("requestfailed", lambda r: failed.append(r.url))
        open_deck(page)
        steps, labels = page.evaluate("deck.steps()"), page.evaluate("deck.labels()")
        ids = page.evaluate("[...document.querySelectorAll('section.slide')].map((s) => s.id)")
        total = page.evaluate("deck.state().total")

        # 3 steps against the storyline, and forward/back equality
        fails = []
        want = storyline_steps()
        if want is None:
            fails.append("docs/STORYLINE.md is missing")
        else:
            for sid, got in zip(ids, steps):
                if sid not in want:
                    if not sid.startswith("b"):
                        fails.append(f"{sid}: not in STORYLINE.md")
                elif got != want[sid]:
                    fails.append(f"{sid}: {got} steps, STORYLINE.md says {want[sid]}")
            fails += [f"{sid}: in STORYLINE.md, not in the deck" for sid in want if sid not in ids]
        for i, n in enumerate(steps, start=1):
            snaps = []
            for f in range(n + 1):
                page.evaluate(f"deck.go({i}, {f})")
                snaps.append(page.evaluate(f"{SLIDE}.querySelectorAll('.f.on, .fo.off').length"))
            for f in range(n, -1, -1):
                page.evaluate(f"deck.go({i}, {f})")
                if page.evaluate(f"{SLIDE}.querySelectorAll('.f.on, .fo.off').length") != snaps[f]:
                    fails.append(f"{labels[i - 1]} step {f}: the state differs going back")
                    break
        record(3, f"steps ({total} slides)", fails)

        # 4 overflow and 5 overlap, in each slide's final state
        over, overlap = [], []
        for i in range(1, len(steps) + 1):
            go_final(page, i)
            page.wait_for_timeout(320)
            res = page.evaluate("""() => {
              const s = document.querySelector('section.slide.active');
              const vis = (el) => { for (let e = el; e && e !== s; e = e.parentElement) { const cs = getComputedStyle(e);
                  if (cs.display === 'none' || cs.visibility === 'hidden' || +cs.opacity < 0.05) return false; } return true; };
              const out = [], texts = [];
              for (const el of s.querySelectorAll('*')) {
                if (el.closest('aside.notes, details:not([open]) table, [hidden]') || !vis(el)) continue;
                const r = el.getBoundingClientRect();
                if (r.width < 1 || r.height < 1) continue;
                if (r.left < -1 || r.top < -1 || r.right > 1601 || r.bottom > 901) out.push(`outside the canvas: ${el.tagName.toLowerCase()} "${el.textContent.trim().slice(0, 30)}"`);
                const cs = getComputedStyle(el);
                if (!el.closest('svg') && /block|flex|grid|list-item|table-cell/.test(cs.display) && el.clientWidth > 0 && cs.overflow !== 'visible' &&
                    (el.scrollWidth > el.clientWidth + 1 || el.scrollHeight > el.clientHeight + 1)) out.push(`clipped: ${el.tagName.toLowerCase()}.${el.className} "${el.textContent.trim().slice(0, 30)}"`);
                if (!el.closest('svg, table, .mask') && [...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim()))
                  texts.push({ t: el.textContent.trim().slice(0, 40), r: [r.left, r.top, r.right, r.bottom], el });
              }
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
        caps = page.evaluate("[...document.querySelectorAll('figcaption, .cap')].map((c) => c.textContent).join(' | ')")
        for label in figure_labels():
            if not re.search(rf"(?<![\w.]){re.escape(label)}(?![\d])", caps):
                fails.append(f"{label} (FIGURES.md) is in no slide's caption")
        bad = page.evaluate("[...document.querySelectorAll('section.slide img')].filter((i) => !i.alt.trim() || !i.naturalWidth).map((i) => i.alt || i.src.slice(0, 40))")
        fails += [f"img without alt, or not loaded: {x}" for x in bad]
        record(6, "figures", fails)

        # 7 keys
        fails = []
        page.evaluate("deck.go(1, 0)")

        def key(k, want, msg):
            page.keyboard.press(k)
            got = page.evaluate("deck.state()")
            if any(got[x] != v for x, v in want.items()):
                fails.append(f"{msg}: {got}")
        if total > 2:
            key("ArrowRight", {"slide": 2}, "ArrowRight")
            key("ArrowLeft", {"slide": 1}, "ArrowLeft")
            key("Space", {"slide": 2}, "Space")
            stepped = next((i for i, n in enumerate(steps[:total], start=1) if n), None)
            if stepped:
                page.evaluate(f"deck.go({stepped}, 0)")
                key("PageDown", {"slide": stepped, "fragment": 1}, "PageDown")
                key("PageUp", {"slide": stepped, "fragment": 0}, "PageUp")
            key("End", {"slide": total}, "End")
            key("Home", {"slide": 1}, "Home")
        page.keyboard.press("o")
        if not page.evaluate("document.getElementById('deck').classList.contains('ov')"):
            fails.append("O: no overview")
        page.keyboard.press("o")
        page.keyboard.press("n")
        if not page.is_visible("#notes"):
            fails.append("N: no notes")
        page.keyboard.press("n")
        t0 = page.evaluate("document.documentElement.dataset.theme || ''")
        page.keyboard.press("t")
        if page.evaluate("document.documentElement.dataset.theme || ''") == t0:
            fails.append("T: the theme did not change")
        page.keyboard.press("t")
        if total >= 2:
            page.goto(DECK.as_uri() + "#2")
            page.wait_for_function("window.deck !== undefined")
            if page.evaluate("deck.state().slide") != 2:
                fails.append("#2: the deep link did not open slide 2")
        record(7, "keys", fails)

        # 8 contrast, light and dark
        fails = []
        for theme in ("light", "dark"):
            page.evaluate(f"document.documentElement.dataset.theme = '{theme}'")
            for i in range(1, len(steps) + 1):
                go_final(page, i)
                low = page.evaluate("""() => {
                  const s = document.querySelector('section.slide.active');
                  const rgb = (c) => { const m = c.match(/[\\d.]+/g); return m ? m.map(Number) : null; };
                  const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= .03928 ? v / 12.92 : ((v + .055) / 1.055) ** 2.4; }; return .2126 * f(r) + .7152 * f(g) + .0722 * f(b); };
                  const bg = (el) => { for (let e = el; e; e = e.parentElement) { const c = rgb(getComputedStyle(e).backgroundColor); if (c && (c.length < 4 || c[3] > .5)) return c; } return [255, 255, 255]; };
                  const out = [];
                  for (const el of s.querySelectorAll('*')) {
                    if (el.closest('aside.notes, svg, [hidden], .plate, details:not([open])') || ![...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim())) continue;
                    const cs = getComputedStyle(el); if (+cs.opacity < .5 || cs.visibility === 'hidden' || cs.display === 'none') continue;
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

        # 14 charts: a tip on each mark, the numbers in a table
        fails = []
        for c in page.evaluate("""[...document.querySelectorAll('figure.chart')].map((f) => ({
              slide: f.closest('section').dataset.label || f.closest('section').id,
              titles: f.querySelectorAll('svg title').length, table: !!f.querySelector('details table')}))"""):
            if not c["titles"]:
                fails.append(f"{c['slide']}: a chart without <title> on its marks")
            if not c["table"]:
                fails.append(f"{c['slide']}: a chart without its <details> table")
        record(14, "charts: tip and table", fails)

        # 17 notes with the source page, 18 text rules (on the source markup)
        notes, text = [], []
        for s in page.evaluate("""[...document.querySelectorAll('section.slide')].map((s) => {
              const n = s.querySelector('aside.notes');
              const c = s.cloneNode(true); c.querySelectorAll('aside.notes').forEach((e) => e.remove());
              return { id: s.dataset.label || s.id, notes: n ? n.textContent.trim() : '', text: c.textContent,
                       lists: [...s.querySelectorAll('ul.b, ol.b')].map((l) => l.children.length) };
            })"""):
            if not s["notes"]:
                notes.append(f"{s['id']}: no speaker notes")
            elif not re.search(r"\((?:pp?\.\s*[\d\s,–-]+[^)]*|-)\)\s*$", s["notes"]):
                notes.append(f"{s['id']}: the notes do not end with the source page, (p. 12)")
            if "—" in s["text"] or "—" in s["notes"]:
                text.append(f"{s['id']}: an em dash")
            text += [f"{s['id']}: a list with {n} items (5 at most)" for n in s["lists"] if n > 5]
        record(17, "notes with the source page", notes)
        record(18, "text rules", text)

        record(1, "load", [f"console: {e}" for e in errors] + [f"request failed: {u}" for u in failed])

        # 9 reduced motion
        fails = []
        rctx = b.new_context(viewport={"width": 1600, "height": 900}, reduced_motion="reduce")
        rp = rctx.new_page()
        rerr = []
        rp.on("pageerror", lambda e: rerr.append(str(e)))
        open_deck(rp)
        for i in range(1, len(steps) + 1):
            go_final(page, i)
            go_final(rp, i)
            page.wait_for_timeout(300)
            a = page.evaluate(f"[{SLIDE}.querySelectorAll('.f.on').length, {SLIDE}.innerText.replace(/\\s+/g, ' ')]")
            r = rp.evaluate(f"[{SLIDE}.querySelectorAll('.f.on').length, {SLIDE}.innerText.replace(/\\s+/g, ' ')]")
            if a[0] != r[0]:
                fails.append(f"{labels[i - 1]}: {r[0]} steps shown with reduced motion, {a[0]} without")
            elif a[1] != r[1]:
                fails.append(f"{labels[i - 1]}: the text differs with reduced motion")
        fails += [f"pageerror: {e}" for e in rerr]
        rctx.close()
        record(9, "reduced motion", fails)

        # 19 visuals: the kit's level of interactivity, unless the briefing lowered it
        fails = []
        want = visuals_wanted()
        found = page.evaluate("""() => {
          const n = {}; for (const e of document.querySelectorAll('section.slide:not(.backup) [data-component]'))
            n[e.dataset.component] = (n[e.dataset.component] || 0) + 1;
          return n; }""")
        diagrams = found.get("FLUXO", 0)
        charts = sum(found.get(k, 0) for k in ("BARRAS", "ESCADA", "PONTOS"))
        if diagrams < want["diagramas"]:
            fails.append(f"{diagrams} animated diagram(s) (FLUXO), the briefing asks for {want['diagramas']}: see exemplos/13-fluxo.html")
        if charts < want["graficos"]:
            fails.append(f"{charts} data chart(s) (BARRAS, ESCADA, PONTOS), the briefing asks for {want['graficos']}: see exemplos/14 to 16")
        unknown = sorted(set(found) - {"FLUXO", "BARRAS", "ESCADA", "PONTOS", "NUMERO"})
        if unknown:
            fails.append(f"unknown data-component: {', '.join(unknown)}")
        empty = page.evaluate("[...document.querySelectorAll('[data-component]:not([data-component=NUMERO])')]"
                              ".filter((e) => { deck.go([...document.querySelectorAll('section.slide')].indexOf(e.closest('section')) + 1, 0);"
                              " return !e.querySelector('svg, .cp-node'); }).map((e) => e.closest('section').id)")
        fails += [f"{sid}: a component that drew nothing (check its data-opts)" for sid in empty]
        record(19, f"visuals: {diagrams} diagram(s), {charts} chart(s)", fails)

        # 16 offline
        fails = []
        octx = b.new_context(viewport={"width": 1600, "height": 900})
        octx.route(re.compile(r"^https?://"), lambda route: route.abort())
        op = octx.new_page()
        open_deck(op)
        for fam in FONTS:
            if not op.evaluate(f"[...document.fonts].some((f) => f.family.replace(/\"/g, '') === '{fam}' && f.status === 'loaded')"):
                fails.append(f"font not loaded offline: {fam}")
        bad = op.evaluate("[...document.querySelectorAll('img')].filter((i) => { i.loading = 'eager'; return !i.complete || !i.naturalWidth; }).length")
        if bad:
            fails.append(f"{bad} images do not render offline")
        octx.close()
        record(16, "offline", fails)
        b.close()

    mb = DECK.stat().st_size / 1024 / 1024
    record(15, f"size {mb:.2f} MB", [] if mb < 12 else [f"{mb:.2f} MB, over 12 MB"])
    out = {k: results[k] for k in sorted(results)}
    (ROOT / "qa").mkdir(exist_ok=True)
    (ROOT / "qa" / "results.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    bad = [k for k, v in out.items() if not v["pass"]]
    print(f"\n{len(out) - len(bad)} of {len(out)} checks pass" + (f"; failing: {bad}" if bad else ""))
    return not bad


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
