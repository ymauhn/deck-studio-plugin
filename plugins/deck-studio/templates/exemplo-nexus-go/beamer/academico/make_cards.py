"""Build cards.html (speaker cards, one per slide) from cards.json.

Run: python -I -X utf8 beamer/academico/make_cards.py
"""
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
cards = json.loads((HERE / "cards.json").read_text(encoding="utf8"))
pt = json.loads((HERE / "cards_pt.json").read_text(encoding="utf8"))
assert len(cards) == 45 and all(3 <= len(c["points"]) <= 5 for c in cards)
assert [c["id"] for c in pt] == [c["id"] for c in cards]
assert all(len(a["points"]) == len(b["points"]) for a, b in zip(cards, pt))


def secs(t):
    m, s = t.split(":")
    return int(m) * 60 + int(s)


def clock(s):
    return f"{s // 60}:{s % 60:02d}"


def rich(t):
    t = html.escape(t)
    t = re.sub(r"\b(w?F|S)_(max|min)\b", r"\1<sub>\2</sub>", t)
    return t


parts, cards_html, start = [], [], 0
def both(pt_html, en_html):
    return f'<span class="pt">{pt_html}</span><span class="en">{en_html}</span>'


for c, q in zip(cards, pt):
    if (q["part"], c["part"]) not in parts:
        parts.append((q["part"], c["part"]))
    n = int(c["id"][1:])
    pts = "".join(f'<li class="pt">{rich(a)}</li>' for a in q["points"]) +           "".join(f'<li class="en">{rich(a)}</li>' for a in c["points"])
    cards_html.append(f"""
<article class="card" id="{c['id'].lower()}" data-part="{html.escape(c['part'])}">
  <header>
    <span class="num">{n:02d}</span>
    <div class="meta"><span class="part">{both(html.escape(q['part']), html.escape(c['part']))}</span>
      <h2>{rich(c['title'])}</h2></div>
    <div class="time"><b>{c['time']}</b><span>{both("aos", "at")} {clock(start)}</span></div>
  </header>
  <ul>{pts}</ul>
  <p class="next"><span class="lbl">{both("Próximo", "Next")}</span>{both(rich(q['transition']), rich(c['transition']))}</p>
</article>""")
    start += secs(c["time"])

chips = "".join(f'<button type="button" class="chip" data-f="{html.escape(e)}">{both(html.escape(p), html.escape(e))}</button>'
                for p, e in parts)
total = clock(start)

page = (HERE / "cards_template.html").read_text(encoding="utf8")
page = page.replace("{{CHIPS}}", chips).replace("{{CARDS}}", "".join(cards_html)).replace("{{TOTAL}}", total)
(HERE / "cards.html").write_text(page, encoding="utf8")
print("cards.html written, total", total)
