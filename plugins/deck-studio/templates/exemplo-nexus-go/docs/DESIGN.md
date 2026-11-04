# DESIGN: the visual system of the deck

The deck is a scientific defense talk, projected in a room and also opened on laptops. It
must read from the back row, carry the dissertation's own colour semantics, and avoid the
generic "AI slide" look. Follow this file exactly unless the user says otherwise. If you
load the `frontend-design` skill, use it to sharpen execution, not to replace these choices.

## 1. Concept

**One idea: sequence + network → function.** The dissertation's diagrams already use a
three-colour semantic system: blue for the sequence branch (ProtT5), orange for the network
branch (STRING, propagation), green for fusion and output. The deck makes that system its
identity:

- A **tri-colour rule** (three short segments: blue, orange, green) is the deck's mark. It
  appears on the title slide (long, joining the protein and the graph), under every slide
  title (short, 72 px), and as the colour key of the NEXUS-GO pipeline.
- Inside diagrams, colour always means the same thing: blue = sequence, orange = network,
  green = fusion or prediction. Never use these three hues decoratively.
- In charts that compare ontologies, BP/CC/MF use the same three hues in the same order
  (this is how the dissertation's own plots are coloured, so the thesis figures and the new
  charts agree). Where a chart would need both meanings at once, put ontologies in facets or
  tabs and keep colour for the route family.

## 2. Tokens

Write these at the top of the deck stylesheet. Every colour in the deck comes from a token.

```css
/* Layout: 1600×900 logical canvas, 12-column grid, 88px side margins, header band 150px */
:root {
  --page:   #eef1f4;  /* around the slide */
  --slide:  #fbfcfd;  /* slide surface, cool white, not cream */
  --ink:    #0f1d29;  /* primary text, deep blue-black */
  --ink-2:  #43525f;  /* secondary text */
  --muted:  #74828f;  /* captions, axis labels */
  --hair:   #d9e0e6;  /* hairlines, grid */
  --plate:  #ffffff;  /* figure plates (stay light in both themes) */
  --plate-edge: #d9e0e6;
  --seq:    #2a78d6;  /* sequence, ProtT5, BP */
  --net:    #eb6834;  /* network, STRING, propagation, CC */
  --fuse:   #1baf7a;  /* fusion, prediction, MF */
  --warn:   #c2410c;  /* limitations, caveats */
  --focus:  #2a78d6;
  --font-display: "Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --font-body:    "Atkinson Hyperlegible Next", "Atkinson Hyperlegible", "Segoe UI", system-ui, sans-serif;
  --font-data:    "IBM Plex Mono", ui-monospace, "Cascadia Mono", Consolas, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --page: #070c11; --slide: #0e161e; --ink: #e7edf3; --ink-2: #a8b5c1; --muted: #7d8b98;
    --hair: #22303b; --plate: #f4f6f8; --plate-edge: #2c3a46;
    --seq: #3987e5; --net: #d95926; --fuse: #199e70; --warn: #f0834e; --focus: #6aa8f0;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --page: #070c11; --slide: #0e161e; --ink: #e7edf3; --ink-2: #a8b5c1; --muted: #7d8b98;
  --hair: #22303b; --plate: #f4f6f8; --plate-edge: #2c3a46;
  --seq: #3987e5; --net: #d95926; --fuse: #199e70; --warn: #f0834e; --focus: #6aa8f0;
  color-scheme: dark;
}
body { background: var(--page); color: var(--ink); }
```

Validate the three series hues with the dataviz skill's palette validator for both themes if
that skill is available (they are its default slots 1–3, which pass all-pairs in both modes).

Projector note: some rooms wash out light greys. Keep body text at `--ink` or `--ink-2` only;
`--muted` is for captions and axis labels, never for content the audience must read.

## 3. Type

Load from Google Fonts with `display=swap`, and also embed WOFF2 subsets in the single-file
build so the deck works offline in the defense room (all three families are OFL-licensed).

| Role | Face | Use |
|---|---|---|
| Display | Bricolage Grotesque, 600–700, optical size high | slide titles, statements, big numbers |
| Body | Atkinson Hyperlegible Next, 400 and 700 | bullets, labels, notes. Designed for legibility, which matters on a projector |
| Data | IBM Plex Mono, 400 and 500 | numbers in charts and tables, run ids, part labels, slide numbers |

Scale on the 1600×900 canvas (px): statement 76 · title 54 · lead 34 · body 30 · small 24 ·
caption 18 · data 18–22. Line height 1.05 for titles, 1.35 for body. Titles use
`text-wrap: balance` and slight negative tracking (−0.01em). Numbers in tables and axes use
`font-variant-numeric: tabular-nums`; large standalone numbers use proportional figures.

Math is pre-rendered to SVG with MathJax at build time (see `BUILD.md`) and inherits
`currentColor`, so it follows the theme.

## 4. Layout grammar

- Canvas 1600×900, scaled to fit the window with letterboxing in `--page`. Safe area: 88 px
  left/right, 56 px top, 64 px bottom.
- Header: part label in `--font-data` 16 px (`4 · Method`, sentence case, no all-caps
  eyebrow), slide title below it, tri-colour rule under the title.
- Footer: slide number `24 / 45` bottom right in `--font-data`; a 3 px progress line along the
  bottom edge (track `--hair`, fill `--ink`).
- Templates (pick one per slide):
  1. **Split**: bullets in columns 1–5, visual in 6–12.
  2. **Figure**: visual across 12 columns, bullets as a band below or a narrow column.
  3. **Statement**: one sentence in display type, optional small support line.
  4. **Interactive**: component across 12 columns, controls in one row above it.
  5. **Table**: a real HTML table, hairline rules only, numbers right-aligned.
- Bullets: at most 4 per slide (5 on S07, S43, S44), each at most about 12 words. Use a small
  coloured square marker in the semantic colour when the bullet belongs to a branch; otherwise
  an `--ink-2` dash. No paragraphs on slides; the narrative lives in speaker notes.
- Cards are not the default. Use a bordered box only for figure plates and for the five
  future-work items.

## 5. Figure plates

Thesis figures are PNGs with light backgrounds. Every one sits on a plate: `--plate`
background, 1 px `--plate-edge` border, 8 px radius, 20 px padding, no shadow. Under the plate,
a caption in `--font-data` 15 px `--muted`: `Dissertation, Fig. 5.8`. Plates keep the same light
fill in dark mode on purpose; in dark mode reduce the plate's surrounding glare by giving it a
`--hair` outer outline.

To reveal parts of a figure (left panel, then right panel), overlay a mask element in the
plate colour and animate its width; never crop the source file.

## 6. Motion

- Fragments: fade in and rise 8 px, 260 ms, `cubic-bezier(.2,.7,.2,1)`. Going back hides them
  instantly.
- Slide change: 180 ms cross-fade. No 3D transitions, no zooms.
- The one orchestrated moment is the NEXUS-GO pipeline (S21): flows draw along the edges in
  the semantic colours, branch by branch.
- Ambient animations (title hero, protein fold) run slowly and stop when their slide is not
  visible.
- `prefers-reduced-motion: reduce`: no transitions; every animation shows its final, complete
  state; interactive controls still work.

## 7. Charts

Follow the dataviz skill's procedure if it is installed. Minimum rules:

- One axis per chart. Bars at most 24 px thick, 4 px rounded data end, square at the
  baseline, 2 px gap between adjacent bars.
- Lines 2 px, markers ≥ 8 px with a 2 px surface ring.
- Text never takes a series colour; use `--ink`, `--ink-2`, `--muted`. A coloured mark next
  to the text carries identity.
- Two or more series: a legend is always present, plus direct labels for at most 4 series.
- Every chart has a hover tooltip and a "table" toggle that shows the underlying numbers.
- Validation and test numbers are never on the same chart. Each chart's subtitle says which
  split it shows.
- S<sub>min</sub> is "lower is better": reverse its axis direction and label it.

## 8. Things to avoid

Cream backgrounds with terracotta accents; purple-to-blue gradients; emoji; icons as section
markers; numbered markers where the order means nothing; a rounded shadowed card around every
block; centred body text; Inter or Space Grotesk; stock "AI" illustrations; text set in the
series colours; numbers typed by hand into chart code.
