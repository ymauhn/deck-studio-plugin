# {{TITLE}}: a talk made from a PDF in Deck Studio

The author watches the deck next to the chat while you build and edit it.

## Rules

- **Language.** Every message to the author is in Brazilian Portuguese: the answers, the short notes between tool calls and the summary, even when the sources are in English. The slides are in {{LANGUAGE}}.
- **Sources.** Every number, name and claim on a slide comes from the imported PDF, `{{PDF}}`. Never invent results, references or numbers. Copy each number as the PDF prints it, except its decimal separator, which follows the slides' language (73.18 in English is 73,18 in Portuguese). Put the source page in the slide's notes (p. 12).
- **Citations.** A work that the PDF cites goes on a slide by its authors' surname and year, as "Silva (2021)" or "Silva et al. (2021)", never by the PDF's number ([20]), which the audience cannot look up. List the works the slides cite on a references slide after the closing one, with their entries from the PDF's reference list.
- **Style.** Short bullets, one idea per slide, no em dashes.
- **The extracted PDF** is in `context/{{SLUG}}/`:
  - `texto.md`, the text page by page, with a line per table row;
  - `info.json`, with the pages, title, author, and each figure with its page and caption;
  - `figuras/`, the PDF's images (`p012-1.png`), and each captioned figure that the PDF draws as vectors, such as a chart or a diagram, rendered from its page (`p028-fig-2-4.png`).

  A figure that `info.json` does not list (it has no caption, or the extraction missed it): look at its page of the PDF with the Read tool. Then say what matters in text or a table, or leave it out and name it in your summary.
- **Format.** `studio.json` names the one the author chose (`format`). Work in that one; leave the other folder as the template made it unless the author asks.
- **A whole talk:** follow the skill `criar-apresentacao`.

## HTML deck (`deck/`)

- **Files.** The slides live in `deck/src/slides/*.html`, built in name order: `00-title.html`, then one file per part of the talk (`01-introducao.html`, ...), each with several slides.
- **The method.** A whole talk follows the skill `criar-apresentacao`, in phases: a briefing with the author, `docs/FACTS.md` and `docs/FIGURES.md`, `docs/STORYLINE.md` (the author approves it), the slides, then `mcp__plugin_deck-studio_deck__run_qa` and the `deck-studio:juiz` subagent until they pass. `docs/briefing.json` keeps the author's choices and `docs/DECISIONS.md` yours. Edit `qa/` only when the author asks: they check your work.
- **Style.** The rules are in the plugin skill `deck-studio:criar-apresentacao`, file `ESTILO.md`: the theme's three concept colours (`--c1`, `--c2`, `--c3`, each tied to one concept), one idea per slide, an affirmative title, one item per step, shorten the text rather than the font, the source page at the end of the notes.
- **Markup.** Copy each slide from the example of its type in the plugin skill `deck-studio:criar-apresentacao`, file `exemplos/` and use only its classes:
  - `<section class="slide" id="s07" data-part="Part name">`. The id is unique in the deck and never changes; a slide added later takes a new one, such as `s07b`.
  - `<h2 class="title">`, the title; the engine puts `data-part` above it.
  - `<div class="bd">`, the 12-column grid. Each child takes a column class: `col-w` (12), `col-main` + `col-side` (8 + 4), `col-a` + `col-b` (5 + 7), `col-text` + `col-fig` (5 + 7).
  - Steps: `class="f"` shows an element on the next click, `data-f="2"` puts it in click 2, and `class="fo"` hides it at its click.
  - `<aside class="notes">`, the speaker notes, with the source page.
  - Slides for questions go after the closing slide, with `class="slide backup"`.
- **Figures.** Call `mcp__plugin_deck-studio_deck__add_image` with `contextFile: "{{SLUG}}/figuras/p012-1.png"`. It copies the figure into `deck/src/img/` and gives you the `<img>` tag. Give each figure a real alt text and a caption with its number and page.
- **Never** write a `<script>`, an inline handler or an external URL in a slide; the studio does not run them. Leave `deck/src/engine.js`, `shell.html` and `deck/build.py` alone, and change `deck/src/deck.css` only when no pattern fits.
- **Builds.** The deck rebuilds after each edit. When a build fails, the error comes back to you: fix it.
- **Checks.** Check every slide you write with `mcp__plugin_deck-studio_deck__screenshot_slide` and `mcp__plugin_deck-studio_deck__check_slide`, and fix any overflow, clipping or overlap.

## Beamer deck (`beamer/apresentacao/`)

- **Front matter.** `apresentacao.tex` compiles with pdfLaTeX at 16:9. Replace the bracketed `\author`, `\institute` and `\date` with the PDF's, unless the author's instructions in the first request name who presents, the event or the date. What neither names keeps its bracketed placeholder, in the slides' language, and your summary says so: never a description of the work such as "Dissertação de mestrado", since `\author` shows in every footline. A long title also needs a short one for the footline: `\title[Short]{Full}`.
- **Frames.** Write one `\begin{frame}{Title}` ... `\end{frame}` per slide, each command on a line of its own. Put a `\section{Part}` before each part; the outline frame lists them.
  - Steps: `\pause` or overlays such as `\item<2->`.
  - Notes: the source page goes in a `\note{p. 12}` inside the frame.
- **Figures.** Copy every figure the talk may use from `context/{{SLUG}}/figuras/` into `beamer/apresentacao/figures/` with a single `cp` command, right after you read `info.json`: the author approves every shell command, and is watching at the start. Then use `\includegraphics[height=0.6\textheight]{p012-1}` in a `figure` with a `\caption`. If the copy is denied, leave the figures out and name them in your summary.
- **References** go in a frame after the closing one, as in the HTML deck.
- **Tables** use `booktabs`.
- **Packages:** only those of a standard TeX distribution, and nothing that needs shell escape.
- **Checks.** Compile with `mcp__plugin_deck-studio_deck__compile_beamer` until it reports 0 errors and no Overfull box in `boxes` (the Underfull ones are hints: act on them only when the page looks wrong): a frame overfull by a few points runs into the footline, as a figure at `0.7\textheight` with a two-line caption does. Then look at the pages with `mcp__plugin_deck-studio_deck__screenshot_beamer_page`.
