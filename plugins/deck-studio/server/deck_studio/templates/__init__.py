"""Project templates: fill_template makes a new project folder from templates/project (docs/IMPORT.md, "Templates")."""
import json
import re
import unicodedata
from pathlib import Path

PROJECT = Path(__file__).resolve().parent / "project"
# empty folders of the template, which git does not keep: made in every new project all the same
EMPTY_DIRS = ("deck/src/img", "beamer/apresentacao/figures")
PLACEHOLDER = re.compile(r"\{\{([A-Z_]+)\}\}")
TEX = {"\\": r"\textbackslash{}", "{": r"\{", "}": r"\}", "$": r"\$", "&": r"\&", "#": r"\#", "_": r"\_",
       "%": r"\%", "^": r"\textasciicircum{}", "~": r"\textasciitilde{}"}
TEX_TYPOGRAPHY = set("–—‘’“”„…•€")  # beyond Latin-1 and Latin Extended-A, what pdfLaTeX's utf8 input knows
UI = {  # the deck's own words (notes bar, help, presenter view, the Beamer front matter's placeholders), in pt-BR and in
    # English, as the slides' LANG says
    "UI_CLOSE": ("Fechar", "Close"),
    "UI_CLOSE_NOTES": ("Fechar as notas", "Close notes"),
    "UI_SHORTCUTS": ("Atalhos do teclado", "Keyboard shortcuts"),
    "UI_KEYS": ("Teclas", "Keys"),
    "UI_SPACE": ("Espaço", "Space"),
    "UI_NEXT_STEP": ("próximo passo ou slide", "next step or slide"),
    "UI_PREV_STEP": ("passo ou slide anterior", "previous step or slide"),
    "UI_FIRST_LAST": ("primeiro / último slide", "first / last slide"),
    "UI_DIGITS": ("número e G", "digits, then G"),
    "UI_GO": ("ir para o slide", "go to slide"),
    "UI_OVERVIEW": ("visão geral", "overview"),
    "UI_NOTES": ("notas do apresentador", "speaker notes"),
    "UI_PRESENTER": ("modo apresentador", "presenter view"),
    "UI_THEME": ("tema claro ou escuro", "light or dark theme"),
    "UI_FULLSCREEN": ("tela cheia", "fullscreen"),
    "UI_BACKUP": ("slides de reserva", "backup slides"),
    "UI_HELP": ("esta ajuda", "this help"),
    "UI_NEXT": ("Próximo", "Next"),
    "UI_STEP": ("passo", "step"),
    "UI_OF": ("de", "of"),
    "UI_PRESENTER_TITLE": ("Apresentador", "Presenter"),
    "UI_TABLE": ("Tabela", "Table"),
    "UI_VALUE": ("Valor", "Value"),
    "UI_DIFFERENCE": ("Diferença", "Difference"),
    "UI_ROUTE": ("rota", "route"),
    "UI_ALL": ("Tudo", "All"),
    "UI_AUTHOR": ("[autor]", "[author]"),
    "UI_INSTITUTION": ("[instituição]", "[institution]"),
    "UI_EVENT": ("[evento e data]", "[event and date]"),
}


def _html(value):
    return value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _tex(value):
    """Text for pdfLaTeX: specials escaped; a character it cannot typeset (an emoji, say) becomes its ASCII
    letters, or nothing, rather than an error."""
    out = []
    for c in " ".join(value.split()):
        if c in TEX:
            out.append(TEX[c])
        elif c.isascii() or " " <= c <= "ſ" or c in TEX_TYPOGRAPHY:
            out.append(c)
        else:
            out.append(unicodedata.normalize("NFKD", c).encode("ascii", "ignore").decode())
    return "".join(out)


def _json(value):  # inside a "..." string of JSON or Python
    return json.dumps(value, ensure_ascii=False)[1:-1]


ESCAPE = {".html": _html, ".tex": _tex, ".json": _json, ".py": _json}


def fill_template(dest, values):
    """Copy the project template into dest, which must be absent or empty, and replace every {{KEY}} in its text
    files with values[KEY] (plain strings), escaped for each file's type: HTML, TeX, JSON and Python strings;
    Markdown and the rest take the text as it is. BABEL (the Beamer deck's language) and the UI_* words follow LANG
    unless given. Raises ValueError, before writing anything, when the template has a placeholder that values lack."""
    dest = Path(dest)
    if dest.exists() and any(dest.iterdir()):
        raise FileExistsError(f"{dest} is not empty")
    english = values.get("LANG") != "pt-BR"
    values = {"BABEL": "english" if english else "brazilian", **{k: v[english] for k, v in UI.items()}, **values}
    files, missing = {}, set()
    for src in sorted(PROJECT.rglob("*")):
        if "__pycache__" in src.parts:
            continue
        data = None if src.is_dir() else src.read_bytes()
        if data and b"{{" in data:
            text, escape = data.decode("utf-8"), ESCAPE.get(src.suffix, str)
            missing |= set(PLACEHOLDER.findall(text)) - values.keys()
            # one pass: a value that holds "{{...}}" is never filled in turn
            data = PLACEHOLDER.sub(lambda m: escape(str(values[m[1]])) if m[1] in values else m[0], text).encode()
        files[src.relative_to(PROJECT)] = data
    if missing:
        raise ValueError(f"no value for {', '.join(sorted(missing))}")
    dest.mkdir(parents=True, exist_ok=True)
    for d in EMPTY_DIRS:
        (dest / d).mkdir(parents=True, exist_ok=True)
    for rel, data in files.items():
        if data is None:
            (dest / rel).mkdir(parents=True, exist_ok=True)
        else:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            (dest / rel).write_bytes(data)
    return dest
