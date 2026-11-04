# Component contract (for everyone writing `deck/src/components/*`)

Read first: `CLAUDE.md`, `docs/INTERACTIVES.md` (your components), `docs/DESIGN.md`,
`docs/FACTS.md` (numbers), `deck/src/deck.css` (tokens and shared classes),
`deck/src/engine.js` (how components are mounted and stepped) and
`deck/src/components/int-dedup.js` (a finished component: copy its style).

## Files

- `deck/src/components/int-<name>.js`: one ES module per component. The build registers it
  automatically as `data-component="INT-<NAME>"` (file name upper-cased). Do not edit any
  registry.
- `deck/src/components/int-<name>.css`: optional; the build concatenates every `*.css` in
  that folder into the page stylesheet. Prefix every selector with a component class
  (e.g. `.pp-`), so nothing leaks.
- `deck/src/components/int-<name>.math.json`: optional `{key: TeX}`; the build pre-renders
  each to an SVG string with MathJax and passes it as `opts.math[key]`. Keys starting with
  `i:` are inline math, others display math. The SVG uses `currentColor`.
- Shared helpers for charts live in `deck/src/lib/` (import with a relative path).

## Interface

```js
export function mount(el, opts) {
  // opts.data   = parsed deck/build/thesis_tables.json (rows: header row first; numbers are floats)
  // opts.math   = pre-rendered math SVG strings
  // opts.reduced = prefers-reduced-motion
  // opts.slide  = 1-based slide number; plus any JSON from the element's data-opts attribute
  return {
    step(n) {},   // fragment state n of the slide (0 = nothing revealed yet); idempotent; called
                  // on every change, forwards and backwards; must fully define the visual state
    render(t) {}, // deterministic frame at time t seconds (GIF export); no Math.random without a seed
    play() {}, pause() {},  // ambient animation on and off (slide shown / hidden); no-op when reduced
    destroy() {},
    state() { return {}; }, // plain JSON values the Playwright tests assert on
    theme() {},   // optional: called after a theme switch (only needed for canvas drawing)
  };
}
```

- `el` is the container on the slide, already sized (width and height in canvas px are given
  in your task). Fill it; never overflow it. The canvas is 1600×900 logical px, scaled with a
  CSS transform, so use logical px everywhere (and for canvas, a 2× backing store).
- The engine calls `step(n)` with the slide's fragment index, also when going back, and calls
  `step(final)` for the overview. `play()` on slide entry, `pause()` on exit.
- With `opts.reduced`, `step(n)` shows final states at once, and `play()` does nothing.
- Controls are real `<button>` / `<input type="range">` / `<select>` with visible labels,
  stable ids, `aria-pressed` for toggles, and the shared `.btn` / `.seg` / `.controls` classes.
  The engine ignores slide-advancing clicks on `button, input, select, textarea, a, label,
  [data-interactive]`; put `data-interactive` on hover-only SVG targets too.
- Colours only through tokens: `var(--seq)` sequence/BP, `var(--net)` network/CC,
  `var(--fuse)` fusion/MF, `var(--warn)`, `var(--ink)`, `var(--ink-2)`, `var(--muted)`,
  `var(--hair)`, `var(--slide)`. Text never takes a series colour. Both themes must work
  (toggle with `document.documentElement.dataset.theme = 'dark'`).
- Type: labels at least 18 px on the canvas (captions 15 px mono are fine). Body face
  `var(--font-body)`, numbers `var(--font-data)` with tabular figures, titles
  `var(--font-display)`. The embedded font subsets have no Greek: write Greek through
  `opts.math` when it is part of a formula; a bare Greek letter in a small SVG label may fall
  back to the system face, which is acceptable.
- Numbers come from `opts.data`; never type a chart number by hand. Illustrative values are
  allowed only where `docs/INTERACTIVES.md` says so, and must be labelled on screen
  (e.g. caption "illustrative").
- Slide text rules: English, no em-dashes, sentence case, no meta-commentary.
- Charts (docs/DESIGN.md §7): tooltip on hover (`.tip` class), a "table" toggle button showing
  the underlying numbers, a subtitle naming the split ("Validation, …" or "Test, …"),
  S<sub>min</sub> axis reversed and labelled "lower is better".

## Testing in isolation

1. Write a page `deck/dev/<name>.html` holding one or more
   `<section class="slide" id="dev1" data-part="dev"><h2 class="title">…</h2><div class="bd">…</div></section>`
   with your container at the exact size, e.g.
   `<div data-component="INT-FOO" style="grid-column:1/13;height:600px"></div>`.
2. `node deck/build.mjs --page deck/dev/<name>.html` writes `deck/build/harness/<name>.html`
   with only that page and only the components it uses. Never run the build without
   `--page` (the full deck in `deck/dist/` belongs to the integrator).
3. Drive it with Python Playwright (`python -I script.py`), file:// URL, viewport 1600×900:
   `deck.go(1, n)` sets slide 1 at fragment n, `deck.component('INT-FOO').state()`,
   `deck.state()`. Capture `page.on('console')` errors and `pageerror`. Screenshot every step
   in both themes into `qa/shots/dev/` and look at the images (Read tool) before you finish.
4. Check: no console errors, nothing outside the container, step(n) forward then backward
   gives the same DOM, reduced motion (`browser.new_context(reduced_motion='reduce')`) shows
   final states.

Do not edit `deck/src/engine.js`, `deck/src/deck.css`, `deck/build.mjs`, `deck/src/shell.html`,
`deck/src/slides/`, `docs/`, `data/`, `source/`, or other people's components. If you need an
engine change, say so in your final message.
