"""Build the deck: deck/src/shell.html + fonts.css + deck.css + components/*.css + components/*.js + engine.js +
slides/*.html (in name order) -> one HTML file.

Usage: python -I -X utf8 deck/build.py [--studio]
             deck/dist/deck.html, the deck to present and share
  --studio   deck/build/studio/deck.html, for Deck Studio: every element of a slide carries
             data-loc="deck/src/slides/<file>:<line>:<col>", its start tag's '<' (1-based; parse5 counts CR, LF and
             CRLF as one line break, and columns in UTF-16 units), and deck/build/studio/csp.json holds
             {"scripts": ["'sha256-...'"]}, the hashes of the shell's inline scripts for the studio's CSP
Images: src="img/<name>" in a slide becomes a data URI of deck/src/img/<name>; a missing file, or a name that leaves
deck/src/img, fails the build (a slide never pulls another file into the deck). So does a section.slide without an
id, or with the id of another slide.
Standard library only.
"""
import base64
import bisect
import hashlib
import json
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote

DECK = Path(__file__).resolve().parent
ROOT = DECK.parent
SRC = DECK / "src"
IMG = SRC / "img"
IMAGE = re.compile(r"""(?<![\w-])(src\s*=\s*)(["'])(img/[^"']*)\2""", re.I)
COMMENT = re.compile(r"(<!--.*?-->)", re.S)
TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif",
         ".svg": "image/svg+xml"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
# never located, nor anything inside them: code, a template, or what a browser reads as text (a data-loc in a
# textarea would show on the slide)
SKIP = {"style", "script", "template", "textarea", "title", "xmp", "plaintext", "noscript", "iframe", "noembed",
        "noframes"}


class Locations(HTMLParser):
    """The start tags to locate, as (offset of '<', end of the tag name): every element inside a section.slide,
    the section included. Open elements are tracked as core/source_edit.py does, so each location resolves there."""

    def __init__(self, text):
        super().__init__()
        self.nl = [0] + [m.end() for m in re.finditer("\n", text)]  # getpos() counts \n only
        self.stack = []  # (tag, "out" | "in" | "skip") of each open element
        self.found = []
        self.ids = []  # the id of each section.slide ("" when it has none)
        self.text = text
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        line, col = self.getpos()
        start = self.nl[line - 1] + col
        outer = self.stack[-1][1] if self.stack else "out"
        cls = next((v for k, v in attrs if k == "class"), None) or ""
        where = ("skip" if outer == "skip" or tag in SKIP
                 else "in" if outer == "in" or (tag == "section" and "slide" in cls.split()) else "out")
        if where == "in" and outer == "out":
            self.ids.append(next((v for k, v in attrs if k == "id"), None) or "")
        if where == "in":
            self.found.append((start, start + re.match(r"<[^\s/>]+", self.text[start:]).end()))
        if tag not in VOID:
            self.stack.append((tag, where))

    def handle_startendtag(self, tag, attrs):
        # '/>' closes void and foreign (svg, math) elements only; an HTML <div/> stays open
        self.handle_starttag(tag, attrs)
        if tag not in VOID and any(t in ("svg", "math") for t, _ in self.stack):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return


def locate(rel, text, found):
    """The slide file's text with data-loc="<rel>:<line>:<col>" right after the name of each start tag found."""
    breaks = [m.end() for m in re.finditer(r"\r\n?|\n", text)]
    out, last = [], 0
    for start, name_end in found:
        line = bisect.bisect_right(breaks, start)
        col = len(text[breaks[line - 1] if line else 0:start].encode("utf-16-le")) // 2 + 1
        out += [text[last:name_end], f' data-loc="{attr(rel)}:{line + 1}:{col}"']
        last = name_end
    return "".join(out) + text[last:]


def attr(s):
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")


def check_ids(parsed):
    """Exits unless every slide has an id of its own: the studio finds a selected slide by its id."""
    seen = {}
    for f, found in parsed.items():
        for i in found.ids:
            if not i:
                sys.exit(f'build failed: a slide in deck/src/slides/{f.name} has no id (<section class="slide" id="s07">)')
            if i in seen:
                sys.exit(f"build failed: two slides have the id {i}, in {seen[i]} and {f.name}; give each its own")
            seen[i] = f.name


def inline_images(slides):
    """Each src="img/<name>" as a data URI; exits with the names that are missing or leave deck/src/img."""
    missing, img = [], IMG.resolve()

    def uri(m):
        p = (IMG / unquote(m[3][4:])).resolve()
        if not (p.is_relative_to(img) and p.is_file() and p.suffix.lower() in TYPES):
            missing.append(m[3])
            return m[0]
        return f"{m[1]}{m[2]}data:{TYPES[p.suffix.lower()]};base64,{base64.b64encode(p.read_bytes()).decode()}{m[2]}"

    chunks = COMMENT.split(slides)  # comments (odd chunks) are left alone
    slides = "".join(c if k % 2 else IMAGE.sub(uri, c) for k, c in enumerate(chunks))
    if missing:
        sys.exit(f"build failed: these images are not files in deck/src/img: {', '.join(missing)}\n"
                 "Copy the image there (mcp__plugin_deck-studio_deck__add_image) and write src=\"img/<name>\".")
    return slides


def read(path):
    return path.read_bytes().decode("utf-8")  # line ends as they are: the locations count them


def fill(css, slides, js):
    """The shell with its placeholders filled, in one pass: a slide or the CSS that holds a placeholder's text is
    never filled in turn."""
    parts = {"/*__CSS__*/": css, "<!--__SLIDES__-->": slides, "/*__JS__*/": js}
    return re.sub("|".join(map(re.escape, parts)), lambda m: parts[m[0]], read(SRC / "shell.html"))


def csp_hash(script):
    """The CSP source of an inline script: the browser hashes its text with CRLF and CR read as LF."""
    digest = hashlib.sha256(re.sub(r"\r\n?", "\n", script).encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode()}'"


def main(studio):
    t0 = time.perf_counter()
    files = sorted((SRC / "slides").glob("*.html"))
    texts = {f: read(f) for f in files}
    parsed = {f: Locations(text) for f, text in texts.items()}
    check_ids(parsed)
    slides = inline_images("\n".join(locate(f"deck/src/slides/{f.name}", texts[f], parsed[f].found) if studio
                                     else texts[f] for f in files))
    # the components (deck/src/components/*.js in name order, _base.js first) register in COMPONENTS before the engine
    comps = SRC / "components"
    code = "".join(read(f) + "\n" for f in sorted(comps.glob("*.js"))) or "const COMPONENTS = {};\n"
    js = re.sub(r"</(script)", r"<\\/\1", code + read(SRC / "engine.js") + "\nstartDeck(COMPONENTS, {});\n", flags=re.I)
    # the embedded fonts (deck/src/fonts.css, OFL) come first, so the deck reads the same offline
    fonts = read(SRC / "fonts.css") + "\n" if (SRC / "fonts.css").is_file() else ""
    css = "".join("\n" + read(f) for f in sorted(comps.glob("*.css")))
    html = fill(fonts + read(SRC / "deck.css") + css, slides, js)
    out = DECK / "build" / "studio" / "deck.html" if studio else DECK / "dist" / "deck.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(html.encode("utf-8"))
    if studio:
        # the studio serves its deck with a CSP that runs only the shell's own scripts, never one that a slide or the
        # CSS holds: their hashes, from the shell filled the same way but with no slides and no CSS
        scripts = re.findall(r"<script\b(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script\s*>", fill("", "", js), re.S | re.I)
        (out.parent / "csp.json").write_text(json.dumps({"scripts": [csp_hash(s) for s in scripts]}), encoding="utf-8")
    print(f"built {out.relative_to(ROOT).as_posix()}: {len(files)} slide files in {(time.perf_counter() - t0) * 1000:.0f} ms")


if __name__ == "__main__":
    main("--studio" in sys.argv[1:])
