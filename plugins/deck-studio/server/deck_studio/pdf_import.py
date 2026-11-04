"""PDF import (docs/IMPORT.md "PDF extraction"): an imported PDF's text, figures and facts, for the agent.

- texto.md: `# <title guess>`, then `## Página N` per page with its text blocks in reading order; a block whose
  spans are all at least 1.3 x the body font size is a `### ` heading. A table gets a line per row, a long block
  breaks at line ends, and a word broken at a line end is joined when the PDF has it unbroken elsewhere.
- figuras/: the embedded images, each xref once, both sides at least 150 px and not of a single colour, as RGB PNGs
  `p{page:03d}-{n}.png`; and each figure that a caption names but no image holds, such as a chart drawn as vectors,
  rendered from its page at 200 dpi as `p{page:03d}-fig-{number}.png`.
- info.json: {pages, words, title, author, figures: [{file, page, width, height, caption}]}.

The PDF is untrusted data: it is read with PyMuPDF only, nothing in it runs, and pages, text and images (their soft
masks too) are capped; a page is rendered only when none of its images is over the caps.
Callers should run it out of process, from the app folder: `python -m deck_studio.pdf_import <pdf> <out_dir>`
prints info.json's object, or {error, message} with exit code 1. A PDF that crashes MuPDF then cannot take the
studio down, and PyMuPDF, which is not thread-safe, never shares the studio's threads."""
import json
import math
import re
import sys
import unicodedata
from pathlib import Path
from typing import NamedTuple

import pymupdf

from deck_studio.server.api import ApiError

MAX_PAGES = 1000
MAX_CHARS = 5_000_000  # of text (a 145-page dissertation has about 300 000)
MAX_IMAGES = 300
MIN_SIDE = 150  # px: smaller images are icons, bullets and rules
MAX_PIXELS = 40_000_000  # one image's: bigger ones are skipped, as decoding them is the cost
MAX_TOTAL_PIXELS = 400_000_000  # all images'
HEADING = 1.3  # a heading's font size, in body font sizes
LONG = 1000  # characters: a longer block breaks at its next line end (Claude Code's Read cuts lines at 2000)
NUMBER = re.compile(r"[-+−±(]*\d[\d.,]*[%)]*")  # a table's cell: 53.36, 0,71, (2), −1.5, 12%
JOINT = "\x00"  # where a line that ends in a hyphen met the next one
FLAGS = pymupdf.TEXT_PRESERVE_WHITESPACE | pymupdf.TEXT_MEDIABOX_CLIP  # ligatures expanded, no image blocks
CAPTION = re.compile(r"(?:Figure|Figura|FIGURE|FIGURA|Fig\.?|FIG\.?)\s*((?:[A-Z]\.?)?\d+(?:\.\d+)*)")  # "Figura 2.1"
# the front matter's headings (as words_of gives them), never a title: a PDF may start at its abstract
FRONT_MATTER = re.compile(r"resumo|abstract|sumario|(table of )?contents|indice|agradecimentos|acknowledge?ments|"
                          r"lista d[aeo]s? .+|list of .+|dedicatoria|epigrafe|prefacio|preface|foreword|glossario|glossary")
# a figure that a caption names but no extracted image holds (a chart drawn as vectors) is rendered from its page
DPI = 200  # of a rendered figure
LOW = 36  # dpi of the render that finds a figure's ink
WHITE = bytes(range(250, 256))  # grey levels that count as paper
WORDS = 8  # a text line of this many words is running text, never a figure's label
GAP = 48  # pt: the most between a caption and its figure's drawing (an axis title and ticks may lie between)
SPLIT = 14  # pt: the most between two rows of one figure
LABEL = 10  # pt: the most between a figure and a label of its own


class Line(NamedTuple):
    text: str
    bbox: tuple
    small: float  # its smallest font size
    big: float  # its largest
    flat: bool  # horizontal


def extract(pdf_path, out_dir):
    """Write texto.md, figuras/ and info.json into out_dir and return info.json's object. An encrypted or
    unreadable PDF is a 400 ApiError."""
    out = Path(out_dir)
    (out / "figuras").mkdir(parents=True, exist_ok=True)
    try:
        doc = pymupdf.open(pdf_path, filetype="pdf")
    except Exception as e:  # MuPDF has several error types for a file it cannot parse
        raise ApiError(400, "bad-pdf", "Não foi possível ler este PDF.") from e
    with doc:
        if doc.needs_pass:
            raise ApiError(400, "bad-pdf", "O PDF está protegido por senha.")
        pages, sizes, figures, seen = [], {}, [], set()
        cover, chars, pixels = [], 0, 0
        for page in doc:
            if page.number == MAX_PAGES or chars > MAX_CHARS:
                break
            try:
                blocks = blocks_of(page, sizes)
            except Exception:  # a page MuPDF cannot read keeps its heading and no text
                blocks = []
            if not cover and page.number < 3:
                cover = blocks
            texts = [(paragraph(lines), min(line.small for line in lines)) for lines in blocks]
            pages.append(texts)
            chars += sum(len(t) for t, _ in texts)
            try:
                listed = page.get_images(full=True) if len(figures) < MAX_IMAGES else []
                placed = page.get_image_info(xrefs=True) if listed else []
            except Exception:
                listed, placed = [], []
            smasks = {item[0]: item[1] for item in listed}
            caps, n, taken, kept = captions(blocks), 0, set(), []
            for im in placed:
                xref, w, h = im["xref"], im["width"], im["height"]
                if not xref or xref in seen:
                    continue
                seen.add(xref)
                smask = smasks.get(xref, 0)
                cost = w * h + (declared(doc, smask) if smask else 0)  # a soft mask's size is its own
                if (len(figures) == MAX_IMAGES or min(w, h) < MIN_SIDE
                        or cost > min(MAX_PIXELS, MAX_TOTAL_PIXELS - pixels)):
                    continue
                try:
                    pix = rgb(doc, xref, smask)
                except Exception:  # a broken or stencil image is skipped
                    continue
                if unicolor(pix):  # a blank, or a mask the PDF draws a figure through: alone it shows nothing
                    continue
                pixels += cost
                n += 1
                name = f"p{page.number + 1:03d}-{n}.png"
                (out / "figuras" / name).write_bytes(pix.tobytes("png"))
                cap = nearest(caps, im["bbox"])
                taken.add(cap)
                kept.append(pymupdf.Rect(im["bbox"]))
                figures.append({"file": f"figuras/{name}", "page": page.number + 1, "width": pix.width,
                                "height": pix.height, "caption": caps[cap][0] if cap is not None else None})
            free = [c for k, c in enumerate(caps) if k not in taken]
            try:
                if not free or len(figures) == MAX_IMAGES or heavy(doc, page, placed if listed else None, smasks):
                    continue
                for cap, clip in drawn(page, blocks, free, kept):
                    pix = page.get_pixmap(clip=clip, dpi=DPI, annots=False)  # the figure, not a reviewer's marks
                    name = f"p{page.number + 1:03d}-fig-{re.sub(r'\W', '-', cap[1])}.png"
                    if (len(figures) == MAX_IMAGES or pix.width * pix.height > MAX_TOTAL_PIXELS - pixels
                            or (out / "figuras" / name).exists()):
                        continue
                    pixels += pix.width * pix.height
                    (out / "figuras" / name).write_bytes(pix.tobytes("png"))
                    figures.append({"file": f"figuras/{name}", "page": page.number + 1, "width": pix.width,
                                    "height": pix.height, "caption": cap[0]})
            except Exception:  # a page MuPDF cannot draw keeps the figures it has
                continue
        words = {w.lower() for texts in pages for t, _ in texts for w in re.findall(r"\w+", t)}
        title = unbroken(checked(doc.metadata.get("title"), cover) or cover_title(cover)
                         or Path(pdf_path).stem, words)[:300]
        for f in figures:
            f["caption"] = f["caption"] and unbroken(f["caption"], words)
        info = {"pages": doc.page_count, "words": sum(len(t.split()) for texts in pages for t, _ in texts),
                "title": title, "author": checked(doc.metadata.get("author"), cover), "figures": figures}
        # the body font size is the size with the most characters: IMPORT.md says the median, which on a short PDF
        # (a title, two headings, a sentence) can land on the headings' size
        body = max(sizes, key=sizes.get, default=0)
        md = [f"# {title}"]
        for number, texts in enumerate(pages, 1):
            md.append(f"## Página {number}")
            md += [unbroken(f"### {t}" if body and small >= HEADING * body else t, words) for t, small in texts]
        if len(pages) < doc.page_count:
            md.append(f"[Extração parada na página {len(pages)} de {doc.page_count}: o PDF passa dos limites.]")
    (out / "texto.md").write_text("\n\n".join(md) + "\n", encoding="utf-8")
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    return info


def blocks_of(page, sizes):
    """The page's text blocks in the PDF's own order, which is its producer's reading order (columns stay whole,
    unlike a sort by position), each as its Lines. Adds the characters of each font size to sizes."""
    out = []
    for b in page.get_text("dict", flags=FLAGS)["blocks"]:
        lines = []
        for line in b.get("lines", ()):
            spans = [s for s in line["spans"] if s["text"].strip()]
            if not spans:
                continue
            for s in spans:
                size = round(s["size"], 1)
                sizes[size] = sizes.get(size, 0) + len(s["text"].strip())
            lines.append(Line(" ".join("".join(s["text"] for s in line["spans"]).split()), line["bbox"],
                              min(s["size"] for s in spans), max(s["size"] for s in spans), line["dir"][0] > 0.99))
        if lines:
            out.append(lines)
    return out


def join(texts):
    """Lines as one paragraph. A line that ends in a hyphen after a letter meets the next with no space and with
    JOINT after the hyphen, which unbroken() resolves once the whole text is read."""
    out = ""
    for text in texts:
        out += text if not out else JOINT + text if re.search(r"\w-$", out) else " " + text
    return out


def unbroken(text, words):
    """text without JOINTs: "anno-" + "tation" is "annotation" when the PDF has that word unbroken somewhere (words),
    else the hyphen stays, as Portuguese breaks "adotou-se" there."""
    def one(m):
        return m[1] + m[2] if (m[1] + m[2]).lower() in words else f"{m[1]}-{m[2]}"
    return re.sub(rf"(\w+)-{JOINT}(\w+)", one, text).replace(JOINT, "")


def paragraph(lines):
    """A block's text: its lines as one paragraph, but a table gets a line per row (MuPDF gives each cell a line of
    its own), and a long block breaks at a line end every LONG characters."""
    texts = [line.text for line in lines]
    if len(texts) > 1 and 2 * sum(map(tabular, texts)) > len(texts):
        rows = []  # [middle, lines] of each row: the lines whose middles are within half a line of its first one's
        for line in sorted(lines, key=lambda line: line.bbox[1] + line.bbox[3]):
            middle = (line.bbox[1] + line.bbox[3]) / 2
            if rows and middle - rows[-1][0] < (line.bbox[3] - line.bbox[1]) / 2:
                rows[-1][1].append(line)
            else:
                rows.append([middle, [line]])
        return "\n".join(" ".join(line.text for line in sorted(row, key=lambda line: line.bbox[0])) for _, row in rows)
    out = [""]
    for text in texts:
        if len(out[-1]) > LONG and not out[-1].endswith("-"):
            out.append("")
        out[-1] = join([out[-1], text]) if out[-1] else text
    return "\n".join(out)


def tabular(text):
    """Whether a line reads as a table's row: it has a number, and it is short or mostly numbers."""
    words = text.split()
    numbers = sum(1 for w in words if NUMBER.fullmatch(w))
    return numbers > 0 and (len(words) < WORDS or 2 * numbers > len(words))


def captions(blocks):
    """(caption, its figure's number, bbox of its first line, Rect of the caption, its Lines) for each line that
    starts a figure caption; the caption runs from that line to the end of its block."""
    out = []
    for lines in blocks:
        for i, line in enumerate(lines):
            if m := CAPTION.match(line.text):
                rect = pymupdf.Rect(line.bbox)
                for other in lines[i + 1:]:
                    rect |= other.bbox
                out.append((join(other.text for other in lines[i:]), m[1], line.bbox, rect, lines[i:]))
    return out


def nearest(caps, rect):
    """The index of the caption whose first line is nearest to the image's rectangle on the page, or None."""
    def gap(b):
        return math.hypot(max(b[0] - rect[2], rect[0] - b[2], 0), max(b[1] - rect[3], rect[1] - b[3], 0))
    return min(range(len(caps)), key=lambda k: gap(caps[k][2])) if caps else None


def drawn(page, blocks, caps, kept):
    """(caption, clip) of each figure that a caption names and no extracted image took, such as a chart drawn as
    vectors: the ink nearest above the caption, or below it when there is none (ABNT puts the caption above), within
    the running text's column and between its lines, with the short text lines that touch it (labels, ticks)."""
    lines = [line for b in blocks for line in b]
    prose = [pymupdf.Rect(line.bbox) for line in lines if len(line.text.split()) >= WORDS]
    masked, found = [pymupdf.Rect(line.bbox) for line in lines] + kept, []
    for above in (True, False):
        for cap in caps:
            block, own = cap[3], cap[4]
            if any(c is cap for c, _ in found):
                continue
            column = [p for p in prose if p.x0 < block.x1 and block.x0 < p.x1]
            x0, x1 = (min(p.x0 for p in column + [block]), max(p.x1 for p in column + [block])) if column else (
                page.rect.x0, page.rect.x1)
            if above:
                band = pymupdf.Rect(x0, max([p.y1 for p in column if p.y1 <= block.y0], default=page.rect.y0),
                                    x1, block.y0)
            else:
                band = pymupdf.Rect(x0, block.y1, x1,
                                    min([p.y0 for p in column if p.y0 >= block.y1], default=page.rect.y1))
            region = ink(page, band, masked, above) if band.height * DPI / 72 >= MIN_SIDE else None
            if not region:
                continue
            for _ in range(3):  # the tick labels, then the axis title under them
                for line in lines:
                    r = pymupdf.Rect(line.bbox)
                    if (line not in own and len(line.text.split()) < WORDS and r in band
                            and r.intersects(region + (-LABEL, -LABEL, LABEL, LABEL))):
                        region |= r
            clip = (region + (-3, -3, 3, 3)) & band
            if min(clip.width, clip.height) * DPI / 72 >= MIN_SIDE:
                found.append((cap, clip))
                masked.append(clip)
    return found


def ink(page, band, masked, above):
    """The Rect of the drawing nearest to the caption's edge of band: rows with ink, from the caption on, while the
    gaps between them stay small. Looked for on a low-resolution grey render with the text and the masked rects painted
    white, so a chart of a million paths costs no more memory than a blank page."""
    pix = page.get_pixmap(clip=band, dpi=LOW, colorspace=pymupdf.csGRAY, annots=False)
    k = LOW / 72
    for r in masked:  # set_rect keeps to the pixmap: a rect at the band's edge still paints out its spill
        pix.set_rect(pymupdf.IRect(math.floor(r.x0 * k) - 1, math.floor(r.y0 * k) - 1, math.ceil(r.x1 * k) + 1,
                                   math.ceil(r.y1 * k) + 1), (255,))
    w, s, rows = pix.width, pix.samples, []
    for y in range(pix.height):
        row = s[y * w:(y + 1) * w]
        rows.append((w - len(row.lstrip(WHITE)), len(row.rstrip(WHITE))) if row.strip(WHITE) else None)
    order = range(pix.height - 1, -1, -1) if above else range(pix.height)
    hits = [i for i, y in enumerate(order) if rows[y]]
    if not hits or hits[0] > GAP * k:
        return None
    run = hits[:1]
    for i in hits[1:]:
        if i - run[-1] > SPLIT * k:
            break
        run.append(i)
    ys = [order[i] for i in run]
    return pymupdf.Rect((pix.x + min(rows[y][0] for y in ys)) / k, (pix.y + min(ys)) / k,
                        (pix.x + max(rows[y][1] for y in ys)) / k, (pix.y + max(ys) + 1) / k)


def heavy(doc, page, placed, smasks):
    """Whether drawing the page decodes an image or a soft mask over the per-image cap."""
    return (any(im["width"] * im["height"] > MAX_PIXELS for im in (placed or page.get_image_info()))
            or any(declared(doc, s) > MAX_PIXELS for s in smasks.values() if s))


def unicolor(pix):
    """Whether every pixel has the first one's colour (bytes.count runs in C, Pixmap.is_unicolor in Python)."""
    s = pix.samples
    return s.count(s[:pix.n]) * pix.n == len(s)


def declared(doc, xref):
    """An image's pixels as its dictionary declares them, read before anything is decoded; a size that is not two
    plain numbers counts as over every cap."""
    try:
        return int(doc.xref_get_key(xref, "Width")[1]) * int(doc.xref_get_key(xref, "Height")[1])
    except ValueError:
        return MAX_TOTAL_PIXELS + 1


def rgb(doc, xref, smask):
    """An image as an RGB pixmap: transparency is flattened on white, as the page shows it, and CMYK or any other
    colour space is converted."""
    pix = pymupdf.Pixmap(doc, xref)
    mask = pymupdf.Pixmap(doc, smask) if smask else None
    alphas = mask.samples if mask else b""
    if alphas.count(255) < len(alphas):  # an opaque mask changes nothing (Pixmap.is_unicolor loops in Python)
        pix = pymupdf.Pixmap(pix, mask)
    if pix.alpha:
        with pymupdf.open() as tmp:
            page = tmp.new_page(width=pix.width, height=pix.height)
            page.insert_image(page.rect, pixmap=pix)
            pix = page.get_pixmap()  # 72 dpi: one pixel per point
    if pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
    return pix


def words_of(text):
    """Lower-case ASCII words: accents and case do not count."""
    return re.findall(r"[a-z0-9]+", unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower())


def checked(value, cover):
    """A metadata field when it has two words or more and they are all on the first page with text, else None:
    template placeholders ("titulo", "nome do autor") and file names ("Microsoft Word - x.docx") are not."""
    words = words_of(value or "")
    on_page = set(words_of(" ".join(line.text for lines in cover for line in lines)))
    return " ".join(value.split()) if len(words) > 1 and set(words) <= on_page else None


def cover_title(cover):
    """The longest run of adjacent lines in the largest horizontal type of the first page with text, without the front
    matter's headings: an article's title, or a thesis cover's, where the institution, author and title may all share
    one size. None when that type holds only such a heading, as on a page that starts with "Resumo"."""
    lines = [line for lines in cover for line in lines if line.flat and re.search(r"[^\W\d_]", line.text)]
    top = max((line.big for line in lines), default=0)
    runs, last = [], None
    for line in lines:
        if line.big < top - 0.5 or FRONT_MATTER.fullmatch(" ".join(words_of(line.text))):
            last = None
            continue
        if last and line.bbox[1] - last.bbox[3] < 0.6 * top:
            runs[-1].append(line)
        else:
            runs.append([line])
        last = line
    return join(line.text for line in max(runs, key=lambda r: sum(len(line.text) for line in r))) if runs else None


if __name__ == "__main__":
    try:
        print(json.dumps(extract(sys.argv[1], sys.argv[2])))
    except ApiError as e:
        print(json.dumps({"error": e.error, "message": e.message}))
        sys.exit(1)
