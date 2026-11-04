"""Source editor (pure): resolve a data-loc (line:col of a start tag, parse5 numbering, 1-based)
to its element in a part file, and splice one of its text nodes."""
import bisect
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser, attrfind_tolerant, tagfind_tolerant

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
ATTR_ESCAPES = {"&": "&amp;", '"': "&quot;", "<": "&lt;", ">": "&gt;", "\r": "&#13;", "\n": "&#10;"}


@dataclass
class Child:
    index: int
    type: str  # text, comment or element
    start: int
    end: int


@dataclass
class Element:
    tag: str
    start: int
    end: int
    start_tag_end: int
    attrs: dict
    children: list


@dataclass
class EditResult:
    ok: bool
    html: str | None = None
    code: str | None = None
    message: str | None = None


@dataclass(eq=False)
class _Node:
    type: str
    tag: str = ""
    start: int = 0
    end: int = 0
    start_tag_end: int = 0
    loc: tuple = ()
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


class _Tree(HTMLParser):
    """The fragment as a tree with raw offsets, built from html.parser events."""
    # ponytail: implied end tags (an open <li> or <p> closed by the next block) and SVG camelCase
    # names (viewBox comes back as viewbox) are not modeled, unlike parse5; the kit closes every element

    def __init__(self, html):
        super().__init__()
        self.html = html
        self.nl = [0] + [m.end() for m in re.finditer("\n", html)]  # getpos() counts \n only
        self.breaks = [m.end() for m in re.finditer(r"\r\n?|\n", html)]  # parse5 counts CR, LF and CRLF
        self.root = _Node("root")
        self.stack = [self.root]
        self.text = None  # the text node that adjacent data extends
        self.ending = None  # the node that ends where the construct being handled ends
        self.feed(html)
        self.close()
        for n in self.stack[1:]:  # still open at the end of the file
            n.end = len(html)

    def _at(self):
        line, col = self.getpos()
        return self.nl[line - 1] + col

    def updatepos(self, i, j):
        j = super().updatepos(i, j)
        if self.ending:
            self.ending.end, self.ending = self._at(), None
        return j

    def handle_starttag(self, tag, attrs):
        start = self._at()
        line = bisect.bisect_right(self.breaks, start)
        col = len(self.html[self.breaks[line - 1] if line else 0:start].encode("utf-16-le")) // 2 + 1
        node = _Node("element", tag, start, start_tag_end=start + len(self.get_starttag_text()), loc=(line + 1, col))
        for name, value in attrs:
            node.attrs.setdefault(name, value or "")  # parse5 keeps the first of duplicate attributes
        self.stack[-1].children.append(node)
        self.text = None
        if tag in VOID:
            node.end = node.start_tag_end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        # '/>' closes void and foreign (svg, math) elements only; an HTML <div/> stays open
        self.handle_starttag(tag, attrs)
        if any(n.tag in ("svg", "math") for n in self.stack):
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        start = self._at()
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                for n in self.stack[i + 1:]:  # closed implicitly by this end tag
                    n.end = start
                self.ending, self.text = self.stack[i], None
                del self.stack[i:]
                return

    def handle_data(self, data):
        if not self.text:
            self.text = _Node("text", start=self._at())
            self.stack[-1].children.append(self.text)
        self.ending = self.text

    def handle_comment(self, data):
        self.ending, self.text = _Node("comment", start=self._at()), None
        self.stack[-1].children.append(self.ending)


def _path(html, line, col):
    """[...ancestors, element] for the element whose start tag begins at line:col, or None."""
    def walk(node, path):
        for c in node.children:
            if c.type != "element":
                continue
            if c.loc == (line, col):
                return [*path, c]
            hit = walk(c, [*path, c])
            if hit:
                return hit
    return walk(_Tree(html).root, [])


def locate_element(html, line, col):
    path = _path(html, line, col)
    if not path:
        return None
    el = path[-1]
    return Element(el.tag, el.start, el.end, el.start_tag_end, dict(el.attrs),
                   [Child(i, c.type, c.start, c.end) for i, c in enumerate(el.children)])


def _generated(n):
    """Nodes the build or the runtime generates: inline math, display math, tables, components."""
    classes = n.attrs.get("class", "").split()
    return ("data-component" in n.attrs or (n.tag == "span" and "m" in classes)
            or (n.tag == "div" and ("tbl" in classes or ("m" in classes and "d" in classes))))


def _collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def _fail(code, message):
    return EditResult(ok=False, code=code, message=message)


def replace_text(html, line, col, child_index, old_text, new_text):
    """Splice one text node of the element at line:col; every other byte stays as it was."""
    path = _path(html, line, col)
    if path and any(map(_generated, path)):
        return _fail("not-editable", "Conteúdo gerado (fórmula, tabela ou componente) não se edita aqui. Peça a mudança no chat.")
    kids = path[-1].children if path else []
    if path and child_index == len(kids) and old_text == "":  # a new last text node: End after an inline formula
        return _append_text(html, path[-1], new_text)
    if not (isinstance(child_index, int) and 0 <= child_index < len(kids)):
        return _fail("not-found", f"Não achei esse trecho no arquivo (linha {line}, coluna {col}). Recarregue e tente de novo.")
    t = kids[child_index]
    if t.type != "text":
        return _fail("not-text", "Aqui não há texto simples para editar. Peça a mudança no chat.")
    raw = html[t.start:t.end]
    if "&" in raw:
        return _fail("entities", "Este texto usa entidades HTML (&...;) no arquivo. Peça a mudança no chat.")
    if _collapse(raw) != _collapse(old_text):
        return _fail("stale", "O texto mudou no arquivo desde a seleção. Recarregue e tente de novo.")
    # the raw node's own leading and trailing whitespace (indentation, line breaks) stays
    lead, trail = re.fullmatch(r"(\s*).*?(\s*)", raw, re.S).groups()
    eol = m.group() if (m := re.search(r"\r?\n", html)) else "\n"
    text = new_text.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\r\n|\r|\n", eol, text)
    return EditResult(ok=True, html=html[:t.start] + lead + text + trail + html[t.end:])


def _append_text(html, el, new_text):
    """Text after the element's last child, just before its end tag: a box that ends with an inline formula (<i>,
    <sub>...) has no text node there for the author to type into. A leading space of new_text is kept."""
    m = re.search(rf"</\s*{re.escape(el.tag)}\s*>$", html[el.start:el.end], re.I)
    if not m or not new_text.strip():
        return _fail("not-text", "Aqui não há texto simples para editar. Peça a mudança no chat.")
    at = el.start + m.start()
    eol = m.group() if (m := re.search(r"\r?\n", html)) else "\n"
    text = new_text.strip().replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = (" " if new_text[:1].isspace() else "") + re.sub(r"\r\n|\r|\n", eol, text)
    return EditResult(ok=True, html=html[:at] + text + html[at:])


def set_attribute(html, line, col, name, value):
    """Set (or, with value None, remove) one attribute of the element at line:col; every other byte stays.
    A component's own box takes attributes; math, tables and anything inside them or a component do not."""
    path = _path(html, line, col)
    if not path:
        return _fail("not-found", f"Não achei essa caixa no arquivo (linha {line}, coluna {col}). Recarregue e tente de novo.")
    *outer, el = path
    if any(map(_generated, outer)) or (_generated(el) and "data-component" not in el.attrs):
        return _fail("not-editable", "Conteúdo gerado (fórmula, tabela ou componente) não se altera aqui. Peça a mudança no chat.")
    tag = html[el.start:el.start_tag_end]
    if value is not None:  # no raw line break either: the file keeps its lines
        value = '="' + re.sub(r'[&"<>\r\n]', lambda c: ATTR_ESCAPES[c.group()], value) + '"'
    t = tagfind_tolerant.match(tag, 1)
    end, k = t.end(1), t.end()
    while m := attrfind_tolerant.match(tag, k):  # the attributes as html.parser reads them
        before, start, end, k = end, m.start(1), m.end(2) if m.group(2) else m.end(1), m.end()
        if m.group(1).lower() == name.lower():
            if value is None:  # with the space before it
                return _splice(html, el.start + before, el.start + end, "")
            return _splice(html, el.start + start, el.start + end, m.group(1) + value)
    if value is None:
        return EditResult(ok=True, html=html)
    return _splice(html, el.start + end, el.start + end, f" {name}{value}")


def _splice(html, start, end, text):
    return EditResult(ok=True, html=html[:start] + text + html[end:])
