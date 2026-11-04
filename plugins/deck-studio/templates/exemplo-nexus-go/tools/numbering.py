"""Compute table, figure and equation numbers from dissertation.tex.

Usage: python -I tools/numbering.py path/to/dissertation.tex data/numbering.json

Chapters before \\begin{appendices} are numbered 1..n; appendix chapters are A, B, ...
Unnumbered environments (equation*, figure without caption) are not counted.
"""
import re, json, sys

tex = open(sys.argv[1], encoding="utf-8").read()
app = tex.find("\\begin{appendices}")
chap = [m.start() for m in re.finditer(r"\\chapter\{", tex)]
n_main = sum(1 for c in chap if app < 0 or c < app)

def chapter_id(pos):
    i = max(k for k, c in enumerate(chap) if c <= pos)
    return str(i + 1) if (app < 0 or chap[i] < app) else "ABCDEFG"[i - n_main]

out = {"table": {}, "figure": {}, "equation": {}}
for env, key in [("table", "table"), ("figure", "figure"),
                 ("equation", "equation"), ("align", "equation")]:
    counts = {}
    for m in re.finditer(r"\\begin\{%s\}" % env, tex):
        p = m.start()
        end = tex.index("\\end{%s}" % env, p)
        c = chapter_id(p)
        counts[c] = counts.get(c, 0) + 1
        labels = re.findall(r"\\label\{([^}]*)\}", tex[p:end])
        out[key].setdefault(c, []).append((p, labels))
# equations from equation and align share one counter per chapter: sort by position
final = {"table": {}, "figure": {}, "equation": {}}
for key in out:
    for c, items in out[key].items():
        for i, (p, labels) in enumerate(sorted(items), 1):
            final[key][f"{c}.{i}"] = labels
json.dump(final, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print({k: len(v) for k, v in final.items()})
