# BUILD: how the deliverables are produced

## 1. Deliverables

```
<project>/
├── deck/
│   ├── src/                       # editable sources (slides, components, styles, engine)
│   ├── build/                     # generated assets (processed images, math SVG, fonts)
│   └── dist/nexus-go-defense.html # ONE self-contained file: the deck
├── beamer/
│   ├── nexus-go-defense.tex       # Beamer version, same storyline
│   ├── figures/                   # thesis figures + static renders of the new diagrams
│   ├── nexus-go-defense.pdf       # compiled locally if a TeX distribution exists
│   └── nexus-go-defense-overleaf.zip
├── gifs/                          # animated GIFs of the new animations
├── qa/                            # Playwright scripts, screenshots, REPORT.md
├── source/                        # read-only copies: thesis zip unpacked, repo clone
├── data/thesis_tables.json        # regenerated from the current .tex
└── DECISIONS.md                   # every judgement call, one line each
```

## 2. Stack

- Plain HTML, CSS and JavaScript (ES modules in `src/`, bundled into one inline script at
  build time). No framework is needed; do not use React or Tailwind for this deck.
- Node 20+ build script `deck/build.mjs` (or Python 3.11 if Node is unavailable) that:
  1. regenerates `data/thesis_tables.json` from the current `dissertation.tex`;
  2. processes images (resize, WebP/PNG, base64);
  3. pre-renders every equation to SVG with `mathjax-full` (`npm i mathjax-full`), TeX input,
     SVG output, `fontCache: 'none'`, so math needs no runtime library;
  4. downloads WOFF2 files for the three font families once (Google Fonts CSS API with a
     modern user agent), subsets them to Latin + Latin-1 + Greek if `pyftsubset`/`glyphhanger`
     is available, and embeds them as `@font-face` data URIs; also keeps the Google Fonts
     `<link>` so an online viewer gets the same faces;
  5. inlines CSS, JS, data and images into `deck/dist/nexus-go-defense.html`;
  6. prints the final size (target under 12 MB, hard limit 16 MB).
- The HTML must also be valid as a claude.ai artifact (see §6): no `<!DOCTYPE>`/`<html>`/
  `<head>`/`<body>` problems, no external requests except Google Fonts and scripts from
  cdnjs, no `localStorage` dependence (wrap any use in try/catch), no `alert`/`confirm`.

## 3. Deck engine (write it yourself, about 400 lines)

- Fixed 1600×900 canvas per slide, scaled with `transform: scale()` to fit the window,
  letterboxed in `--page`. Recompute on resize.
- Slides are `<section class="slide" data-part="4 · Method" id="s24">` elements. Fragments are
  any element with `class="f"` and an optional `data-f="2"` group index.
- Navigation: `→`, `Space`, `PageDown`, `Enter` = next fragment or slide; `←`, `PageUp`,
  `Backspace` = previous; `Home`/`End`; digits then `G` = go to slide; `O` = overview grid
  (click a thumbnail to jump; overview shows all fragments); `N` = speaker notes panel; `P` =
  presenter view in a second window if `window.open` works, otherwise a notes overlay with a
  timer and next-slide thumbnail; `T` = theme toggle (sets `data-theme` on `<html>`); `F` =
  fullscreen (handle rejection); `B` = jump to backup slides; `?` = key help overlay.
- Most presentation clickers send `PageDown`/`PageUp`; test them.
- Pointer: click on the right two thirds = next, left third = previous, except on
  interactive elements (`button, input, select, [data-interactive]`). Touch swipe left/right.
- Deep link: `#24` opens slide 24 (bare token only; the artifact viewer strips anything else).
- Each slide's components get `mount` on first visit, `step(n)` on every fragment change,
  `play()` when visible and `pause()` when hidden.
- Speaker notes come from `<aside class="notes">` inside each slide.
- Header part label and slide number are generated from `data-part` and the slide index.
- `prefers-reduced-motion`: no transitions; components show final states.
- A tiny `window.deck` API for tests: `deck.go(i)`, `deck.next()`, `deck.prev()`,
  `deck.state()` → `{slide, fragment, fragmentsOnSlide, total}`.

## 4. Beamer version

- `\documentclass[aspectratio=169,11pt]{beamer}`, custom colour theme from the tokens in
  `DESIGN.md` (light theme only), no navigation symbols, frame numbers `n / 45`.
- Fonts: if XeLaTeX or LuaLaTeX is available, use `fontspec` with the same three families
  (TTF/OTF files downloaded into `beamer/fonts/`, loaded by path). Otherwise pdfLaTeX with
  `sourcesanspro` (or `FiraSans`) and `sourcecodepro`.
- Same 45 frames plus the backup frames, same titles and on-screen text. Fragments become
  overlays (`\pause`, `\item<+->`, `\only<n>{}` for figure halves).
- Thesis figures: copy originals into `beamer/figures/`.
- New diagrams and charts: export each component's final state as PDF (vector) with
  Playwright `page.pdf()` on an isolated component page, or as PNG at 2× via
  `locator.screenshot()`; prefer PDF for diagrams and charts. Interactive slides show their
  default state; add one extra frame where a second state matters (S23 sum and max; S24 T = 0
  and T = 6; S38 BP, CC and MF in wF<sub>max</sub>).
- Optional: `animate` package for INT-FOLD and INT-PROP frame sequences (plays in Adobe
  Reader, shows the first frame elsewhere). Keep a static fallback.
- Speaker notes: `\note{}` per frame (same text as the HTML notes).
- Compile twice. If no TeX distribution is installed, do not install one silently; produce the
  Overleaf zip (`.tex` + `figures/` + `fonts/` if XeLaTeX) and tell the user to upload it
  (the user already uses Overleaf for the dissertation). Set the Overleaf compiler in a
  `latexmkrc` inside the zip: `$pdf_mode = 5;` for XeLaTeX, plus `$pdflatex = 'xelatex %O %S';`,
  because Overleaf passes its Compiler setting on the command line (`-pdf` by default), which
  overrides `$pdf_mode`.

## 5. GIFs

- For each animated component (INT-FOLD, INT-PROP, INT-PIPE, INT-MP, INT-GBA), open an
  isolated page that mounts only that component, call `render(t)` for t = 0, 1/fps, …, capture
  each frame with `locator.screenshot()`, and assemble with Pillow or `imageio`
  (`loop=0`, 20 fps, adaptive palette, ≤ 1200 px wide, ≤ 8 MB each).
- The `slack-gif-creator` skill's `GIFBuilder` and easing helpers may be reused, but override
  its Slack-specific size limits.
- Also export an MP4 of INT-PIPE and INT-PROP with ffmpeg if available (better quality for
  PowerPoint).

## 6. Publishing as a claude.ai artifact (optional, after the build)

Claude Code cannot publish claude.ai artifacts. When the deck is done, tell the user in the
final report that he can bring `deck/dist/nexus-go-defense.html` back to the Cowork
conversation to publish it as an artifact. To keep that path open, the HTML must:

- put `<title>NEXUS-GO Defense</title>` and the `<style>` at the top of the file;
- load nothing except Google Fonts stylesheets and pinned scripts from cdnjs (the build
  inlines everything else anyway);
- stay under 16 MB;
- work in both themes through tokens, with an explicit `body` background;
- never rely on `alert`, `confirm`, `prompt`, `window.print` or downloads.
