"""Write beamer/slides.tex from beamer/build/layout.json (step 2 of 2; step 1 is extract.py).

Every frame is drawn on the 1600×900 px canvas of the HTML deck (1 px = 0.1 mm):
  - the visual layer of each overlay (a vector PDF page printed by Chromium),
  - native figures (\\includegraphics) and figure masks,
  - native text: every text leaf of the HTML, line by line, with the browser's line breaks,
  - links over the interactive controls and the animate sequences.
Usage: python -I -X utf8 beamer/tools/make_tex.py
"""
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
B = ROOT / "beamer"
L = json.loads((B / "build" / "layout.json").read_text(encoding="utf8"))
SLIDES = {s["n"]: s for s in L["slides"]}
MAIN = sum(1 for s in L["slides"] if "backup" not in s["cls"])

TOKENS = {"ink": "ink", "ink-2": "inkii", "muted": "muted", "hair": "hair", "plate": "plate", "plate-edge": "plateedge",
          "slide": "slide", "seq": "seq", "net": "net", "fuse": "fuse", "warn": "warn"}
RGB = {}
for k, v in TOKENS.items():
    RGB.setdefault(L["colors"][k], v)

FONTS = {"\\fbR": "AtkinsonNext-Regular.ttf", "\\fbB": "AtkinsonNext-Bold.ttf", "\\fbI": "AtkinsonNext-Regular.ttf",
         "\\fbBI": "AtkinsonNext-Bold.ttf", "\\fmR": "PlexMono-Regular.ttf", "\\fmM": "PlexMono-Medium.ttf",
         "\\fdA": "Bricolage-w650-o96.ttf", "\\fdB": "Bricolage-w700-o96.ttf"}
CMAP = {cmd: set(TTFont(B / "fonts" / f)["cmap"].getBestCmap()) for cmd, f in FONTS.items()}
SPECIAL = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", " ": "~"}
# glyphs missing from the latin subsets: typeset as math, like the deck's own formulas
MATH = {"→": r"\rightarrow", "←": r"\leftarrow", "∈": r"\in", "∪": r"\cup", "≈": r"\approx", "≥": r"\geq", "≤": r"\leq",
        "α": r"\alpha", "γ": r"\gamma", "κ": r"\kappa", "λ": r"\lambda", "ρ": r"\rho", "τ": r"\tau", "Δ": r"\Delta",
        "σ": r"\sigma", "μ": r"\mu", "ℓ": r"\ell", "−": "-"}
WARN = []


def num(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def color(c):
    if c in RGB:
        return f"\\color{{{RGB[c]}}}"
    r, g, b = (round(float(x)) for x in re.findall(r"[\d.]+", c)[:3])
    return f"\\color[RGB]{{{r},{g},{b}}}"


def fontcmd(f):
    if f["fam"] == "b":
        return {(0, 0): "\\fbR", (1, 0): "\\fbB", (0, 1): "\\fbI", (1, 1): "\\fbBI"}[(int(f["w"] >= 600), int(f["it"]))]
    if f["fam"] == "m":
        return "\\fmM" if f["w"] >= 500 else "\\fmR"
    if f["w"] not in (650, 700):
        WARN.append(f"display weight {f['w']} mapped to the nearest instance")
    return "\\fdB" if f["w"] >= 700 else "\\fdA"


def esc(s, cmd):
    out = []
    for ch in s:
        if ch in SPECIAL:
            out.append(SPECIAL[ch])
        elif ord(ch) in CMAP[cmd]:
            out.append(ch)
        elif ch in MATH:
            out.append(f"${MATH[ch]}$" if MATH[ch] != "-" else "-")
        else:
            raise SystemExit(f"no glyph for {ch!r} (U+{ord(ch):04X}) in {FONTS[cmd]} and no fallback")
    return "".join(out)


def style(f):
    return (fontcmd(f), round(f["size"], 2), f["color"], round(f["ls"], 4), f["va"])


def lines_of(toks):
    lines = []
    for t in toks:
        if lines:
            p = lines[-1][-1]
            if t["r"]["x"] < p["r"]["x"] + p["r"]["w"] - 1 and t["r"]["y"] > p["r"]["y"] + 0.35 * min(t["r"]["h"], p["r"]["h"]):
                lines.append([t])
                continue
            lines[-1].append(t)
        else:
            lines.append([t])
    return lines


def baseline(line, base_size):
    ws = [t["r"]["y"] + t["r"]["h"] - t["f"]["desc"] for t in line if t["k"] == "w" and t["f"]["va"] == 0 and abs(t["f"]["size"] - base_size) < 0.5]
    ws = ws or [t["r"]["y"] + t["r"]["h"] - t["f"]["desc"] for t in line if t["k"] == "w" and t["f"]["va"] == 0]
    ws = ws or [t["base"] for t in line if t["k"] == "m"]
    ws = ws or [t["r"]["y"] + t["r"]["h"] for t in line]
    ws.sort()
    return ws[len(ws) // 2]


def line_tex(line, base):
    out, i = [], 0
    while i < len(line):
        t = line[i]
        sp = " " if t["sp"] and i else ""
        if t["k"] == "w":
            st = style(t["f"])
            words = [esc(t["s"], st[0])]
            j = i + 1
            while j < len(line) and line[j]["k"] == "w" and style(line[j]["f"]) == st:
                words.append((" " if line[j]["sp"] else "") + esc(line[j]["s"], st[0]))
                j += 1
            text = "".join(words)
            pre = ""
            if st[0] != base[0]:
                pre += st[0]
            if st[1] != base[1] and not st[4]:
                pre += f"\\fz{{{num(st[1])}}}{{{num(st[1] * 1.2)}}}"
            if st[2] != base[2]:
                pre += color(st[2])
            if st[3] != base[3] or (pre and st[3]):
                pre += f"\\ls{{{num(st[3] * 100)}}}"
            text = f"{{{pre}{{}}{text}}}" if pre else text
            if st[4] == -1:
                text = f"\\textsubscript{{{text}}}"
            elif st[4] == 1:
                text = f"\\textsuperscript{{{text}}}"
            out.append(sp + text)
            i = j
            continue
        if t["k"] == "m":
            m = f"$\\displaystyle {t['tex']}$" if t["display"] else f"${t['tex']}$"
            c = color(t["color"]) if t["color"] != base[2] else ""
            out.append(f"{sp}{{\\fz{{{num(t['em'])}}}{{{num(t['em'] * 1.2)}}}{c}{m}}}")
        elif t["k"] == "g":
            out.append(f"{sp}\\hspace*{{{num(t['w'])}\\px}}")
        i += 1
    return "".join(out)


def leaf_tex(d):
    """One TikZ node for a text leaf; lines keep the browser's breaks and baselines."""
    toks = [t for t in d["toks"] if t["r"]["w"] > 0 or t["k"] == "m"]
    if not toks:
        return None
    f = d["font"]
    base = style(f)
    lines = lines_of(toks)
    bl = [baseline(ln, f["size"]) for ln in lines]
    lh = d["lh"] or (bl[1] - bl[0] if len(bl) > 1 else f["size"] * 1.2)
    al = {"center": "c", "right": "r", "end": "r"}.get(d["align"], "l")
    left = min(ln[0]["r"]["x"] for ln in lines)
    right = max(ln[-1]["r"]["x"] + ln[-1]["r"]["w"] for ln in lines)
    x = {"l": left, "c": (lines[0][0]["r"]["x"] + lines[0][-1]["r"]["x"] + lines[0][-1]["r"]["w"]) / 2, "r": right}[al]
    rows = []
    for k, ln in enumerate(lines):
        s = line_tex(ln, base)
        if al == "l" and ln[0]["r"]["x"] - left > 0.75:
            s = f"\\hspace*{{{num(ln[0]['r']['x'] - left)}\\px}}" + s
        if k:
            d_extra = (bl[k] - bl[k - 1]) - lh
            rows.append(f"\\\\[{num(d_extra)}\\px]" if abs(d_extra) >= 0.5 else "\\\\")
        rows.append(s)
    pre = f"{base[0]}\\fz{{{num(f['size'])}}}{{{num(lh)}}}{color(f['color'])}"
    if base[3]:
        pre += f"\\ls{{{num(base[3] * 100)}}}"
    return f"[t{al}] at ({num(x)},{num(bl[0])}) {{{pre}\\L{al}{{{''.join(rows)}}}}}"


def spec(ovs, total):
    ovs = sorted(set(ovs))
    if ovs == list(range(1, total + 1)):
        return ""
    rs, a = [], None
    for o in ovs:
        if a is None:
            a = p = o
        elif o == p + 1:
            p = o
        else:
            rs.append((a, p)); a = p = o
    rs.append((a, p))
    return "<" + ",".join(str(x) if x == y else f"{x}-{y}" for x, y in rs) + ">"


# ---------- figures ----------
def figure(name):
    src = ROOT / "deck" / "build" / "img" / f"{name}.webp"
    (B / "figures").mkdir(exist_ok=True)
    png = B / "figures" / f"{name}.png"
    jpg = B / "figures" / f"{name}.jpg"
    if not png.exists() and not jpg.exists():
        im = Image.open(src)
        alpha = im.mode in ("RGBA", "LA") or "transparency" in im.info
        im = im.convert("RGBA" if alpha else "RGB")
        im.save(png, optimize=True)
        if not alpha and png.stat().st_size > 1_500_000:   # photo-like and large: a high-quality JPEG
            im.save(jpg, quality=93, subsampling=0)
            png.unlink()
    return f"figures/{name}.png" if png.exists() else f"figures/{name}.jpg"


# ---------- notes ----------
class Notes(HTMLParser):
    TAGS = {"b": "\\textbf{", "strong": "\\textbf{", "i": "\\textit{", "em": "\\textit{", "code": "\\texttt{",
            "sub": "\\textsubscript{", "sup": "\\textsuperscript{"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag == "p" and self.out:
            self.out.append("\n\n")
        elif tag in self.TAGS:
            self.out.append(self.TAGS[tag])

    def handle_endtag(self, tag):
        if tag in self.TAGS:
            self.out.append("}")

    def handle_data(self, data):
        self.out.append(esc(re.sub(r"\s+", " ", data), "\\fbR"))


def notes(h):
    p = Notes()
    p.feed(h)
    return "".join(p.out).strip()


# ---------- frames ----------
def body(s, overlays, extra=None):
    """TikZ lines for slide s. overlays: list of state indices, one per overlay (1-based position)."""
    total = len(overlays)
    out = ["\\begin{tikzpicture}[deck]"]
    files = {}
    for o, k in enumerate(overlays, start=1):
        files.setdefault(s["layers"][k], []).append(o)
    for pg, ovs in files.items():
        out.append(f"\\node{spec(ovs, total)}[box] at (0,0) {{\\includegraphics[page={pg},width=1600\\px]{{build/layers}}}};")
    for im in s["imgs"]:
        ovs = [o for o, k in enumerate(overlays, start=1) if k in im["vis"]]
        if ovs:
            r = im["r"]
            out.append(f"\\node{spec(ovs, total)}[box] at ({num(r['x'])},{num(r['y'])}) "
                       f"{{\\includegraphics[width={num(r['w'])}\\px,height={num(r['h'])}\\px]{{{figure(im['src'])}}}}};")
    for m in s["masks"]:
        ovs = [o for o, k in enumerate(overlays, start=1) if k in m["vis"]]
        if ovs:
            r = m["r"]
            out.append(f"\\fill{spec(ovs, total)}[plate] ({num(r['x'])},{num(r['y'])}) rectangle ++({num(r['w'])},{num(r['h'])});")
    out += extra or []
    for lid in sorted(s["leaves"], key=int):
        d = s["leaves"][lid]
        if "toks" not in d:
            continue
        ovs = [o for o, k in enumerate(overlays, start=1) if k in d["vis"]]
        t = leaf_tex(d) if ovs else None
        if t:
            out.append(f"\\node{spec(ovs, total)}{t};")
    if "s-title" not in s["cls"]:
        lab = s["label"] if "backup" in s["cls"] else f"{s['label']} / {MAIN}"
        n = L["num"]
        out.append(f"\\node[tr] at ({num(n['right'])},{num(n['base'])}) {{\\fmR\\fz{{16}}{{16}}\\color{{muted}}{lab}}};")
    out.append("\\end{tikzpicture}")
    return out


def hot(r, target, ovs=None, total=None, pad=0):
    sp = spec(ovs, total) if ovs else ""
    return (f"\\node{sp}[box] at ({num(r['x'] - pad)},{num(r['y'] - pad)}) "
            f"{{\\hot{{{num(r['w'] + 2 * pad)}}}{{{num(r['h'] + 2 * pad)}}}{{{target}}}}};")


def under(r, sp):
    """Slide-coloured patch under a cropped frame, so no sliver of the layer below shows at its edges."""
    return f"\\fill{sp}[slide] ({num(r['x'] - 2)},{num(r['y'] - 2)}) rectangle ++({num(r['w'] + 4)},{num(r['h'] + 4)}); "


def anim(seq, fps, ovs, total):
    r = L["seqs"][seq]["rect"]
    sp = spec(ovs, total)
    return (under(r, sp) + f"\\node{sp}[box] at ({num(r['x'])},{num(r['y'])}) "
            f"{{\\animategraphics[autoplay,loop,width={num(r['w'])}\\px]{{{fps}}}{{build/seq/{seq}}}{{}}{{}}}};")


def crop(seq, page, ovs, total):
    r = L["seqs"][seq]["rect"]
    sp = spec(ovs, total)
    return (under(r, sp) + f"\\node{sp}[box] at ({num(r['x'])},{num(r['y'])}) "
            f"{{\\includegraphics[page={page},width={num(r['w'])}\\px]{{build/seq/{seq}}}}};")


def slider(r, values, lo, hi, thumb=16):
    """Click zones along a range input, one per value."""
    xs = [r["x"] + thumb / 2 + (v - lo) / (hi - lo) * (r["w"] - thumb) for v in values]
    zones = []
    for i, x in enumerate(xs):
        a = (xs[i - 1] + x) / 2 if i else r["x"]
        b = (xs[i + 1] + x) / 2 if i + 1 < len(xs) else r["x"] + r["w"]
        zones.append({"x": a, "y": r["y"] - 8, "w": b - a, "h": r["h"] + 16})
    return zones


def targets(name, total):
    return [f"\\hypertarget<{o}>{{{name}.{o}}}{{}}" for o in range(1, total + 1)]


def frame(s, overlays, extra=None, head=None, with_notes=True):
    lines = ["\\begin{frame}[plain]"]
    lines += head or []
    lines += body(s, overlays, extra)
    if with_notes and s["notes"].strip():
        lines.append(f"\\note{{{notes(s['notes'])}}}")
    lines.append("\\end{frame}")
    return lines


def title_rect(s):
    for d in s["leaves"].values():
        if d.get("tag") == "h2":
            t = d["toks"]
            x0 = min(q["r"]["x"] for q in t); y0 = min(q["r"]["y"] for q in t)
            x1 = max(q["r"]["x"] + q["r"]["w"] for q in t); y1 = max(q["r"]["y"] + q["r"]["h"] for q in t)
            return {"x": x0, "y": y0, "w": x1 - x0, "h": y1 - y0}


def main():
    out = ["% Generated by beamer/tools/make_tex.py from the HTML deck. Edit the HTML and regenerate,",
           "% or edit this file directly once the HTML is final.", ""]
    part = None
    appendix = []
    for n, s in SLIDES.items():
        if s["part"] != part and "backup" not in s["cls"]:
            part = s["part"]
            out.append(f"\\section{{{esc(part, chr(92) + 'fbR')}}}")
        if "backup" in s["cls"] and part != "Backup":
            part = "Backup"
            out.append("\\section{Backup}")
        st = s["states"]
        ov = list(range(len(st)))
        extra, head = [], []
        last = st.index(str(s["steps"])) + 1   # overlay of the last fragment
        if n == 21:   # INT-PIPE: route buttons, figure toggle, animation on the "all" overlay
            total = len(ov)
            head = targets("s21", total)
            c = s["controls"]
            ovs = list(range(st.index("3") + 1, total + 1))
            for r_, o in (("fixed", st.index("3") + 1), ("gnn", st.index("4") + 1), ("early", st.index("5") + 1),
                          ("late", st.index("6") + 1), ("all", st.index("all") + 1)):
                extra.append(hot(c[f"#pipe-{r_}"], f"s21.{o}", ovs, total))
            extra.append(hot(c["#pipe-fig"], "s21fig", ovs, total))
            extra.append(anim("pipe-anim", 10, [st.index("all") + 1], total))
            fig = SLIDES[21]
            back = [hot(c[f"#pipe-{r_}"], f"s21.{o}") for r_, o in (("fixed", st.index("3") + 1), ("gnn", st.index("4") + 1),
                    ("early", st.index("5") + 1), ("late", st.index("6") + 1), ("all", st.index("all") + 1))]
            back += [hot(c["#pipe-fig"], f"s21.{st.index('all') + 1}"), hot(title_rect(fig), f"s21.{st.index('all') + 1}", pad=6),
                     crop("pipe-fig", 1, [1], 1)]
            appendix += frame(fig, [st.index("all")], extra=back, head=["\\hypertarget{s21fig}{}"], with_notes=False)
        elif n == 23:   # INT-DEDUP: sum and max
            total = len(ov)
            head = targets("s23", total)
            c = s["controls"]
            ovs = list(range(st.index("2") + 1, total + 1))
            extra += [hot(c["#dd-sum"], f"s23.{st.index('3') + 1}", ovs, total), hot(c["#dd-max"], f"s23.{st.index('max') + 1}", ovs, total)]
        elif n == 24:   # INT-PROP: T and alpha sliders, play; explorer grid in the appendix
            ov = ov + [st.index(str(s["steps"]))]   # one more overlay: the animation over the last state
            total = len(ov)
            head = targets("s24", total)
            c = s["controls"]
            cur = {o: (2, 5) for o in range(1, total + 1)}
            cur[st.index("T0") + 1] = (0, 5)
            cur[st.index("T6") + 1] = (6, 5)
            main_of = {(2, 5): last, (0, 5): st.index("T0") + 1, (6, 5): st.index("T6") + 1}
            dest = lambda t, a: f"s24.{main_of[(t, a)]}" if (t, a) in main_of else f"s24x.{(a - 1) * 11 + t + 1}"
            tz, az = slider(c["#prop-T"], range(11), 0, 10), slider(c["#prop-alpha"], range(1, 10), 1, 9)
            for o in range(st.index("2") + 1, total + 1):
                t0, a0 = cur[o]
                extra += [hot(z, dest(t, a0), [o], total) for t, z in enumerate(tz)]
                extra += [hot(z, dest(t0, a), [o], total) for a, z in zip(range(1, 10), az)]
                extra.append(hot(c["#prop-play"], f"s24.{total}", [o], total))
            extra.append(anim("prop-anim", 2, [total], total))
            g = 99
            xs = [crop("prop-grid", k, [k], g) for k in range(1, g + 1)]
            for k in range(1, g + 1):
                a0, t0 = divmod(k - 1, 11)
                a0 += 1
                xs += [hot(z, dest(t, a0), [k], g) for t, z in enumerate(tz)]
                xs += [hot(z, dest(t0, a), [k], g) for a, z in zip(range(1, 10), az)]
                xs.append(hot(c["#prop-play"], f"s24.{total}", [k], g))
            xs.append(hot(title_rect(s), f"s24.{last}", pad=6))
            appendix += frame(s, [st.index(str(s["steps"]))] * g, extra=xs, head=targets("s24x", g), with_notes=False)
        elif n == 38:   # INT-TEST: ontology tabs, metric selector; explorer grid in the appendix
            total = len(ov)
            head = targets("s38", total)
            c = s["controls"]
            mets = L["seqs"]["test-grid"]["metrics"]
            onts = ["BP", "CC", "MF"]
            main_of = {"BP": last, "CC": st.index("CC") + 1, "MF": st.index("MF") + 1}
            dest = lambda o, m: f"s38.{main_of[o]}" if m == "wFmax" else f"s38x.{onts.index(o) * len(mets) + mets.index(m) + 1}"
            nxt = lambda m: mets[(mets.index(m) + 1) % len(mets)]
            for o in range(last, total + 1):
                ont = {last: "BP", st.index("CC") + 1: "CC", st.index("MF") + 1: "MF"}[o]
                extra += [hot(c[f"#test-{x}"], dest(x, "wFmax"), [o], total) for x in onts]
                extra.append(hot(c["#test-metric"], dest(ont, nxt("wFmax")), [o], total))
            g = 3 * len(mets)
            xs = [crop("test-grid", k, [k], g) for k in range(1, g + 1)]
            for k in range(1, g + 1):
                ont, met = onts[(k - 1) // len(mets)], mets[(k - 1) % len(mets)]
                xs += [hot(c[f"#test-{x}"], dest(x, met), [k], g) for x in onts]
                xs.append(hot(c["#test-metric"], dest(ont, nxt(met)), [k], g))
            xs.append(hot(title_rect(s), f"s38.{last}", pad=6))
            appendix += frame(s, [st.index(str(s["steps"]))] * g, extra=xs, head=targets("s38x", g), with_notes=False)
        out += frame(s, ov, extra=extra, head=head)
        out.append("")
    out += ["\\section{Interactive states}", ""] + appendix
    (B / "slides.tex").write_text("\n".join(out) + "\n", encoding="utf8")
    for w in sorted(set(WARN)):
        print("warning:", w)
    print(f"slides.tex: {sum(1 for x in out if x.startswith(chr(92) + 'begin{frame}'))} frames")


if __name__ == "__main__":
    main()
