# QA: tests, audits and the definition of done

Write the checks as Python Playwright scripts under `qa/` (the `webapp-testing` skill shows
the pattern; the deck is a static file, so open it with `file://` and no server). Run the full
suite after every major change and before finishing. Record results in `qa/REPORT.md`.

## 1. Fact audit (before building anything)

1. Unzip the newest thesis into `source/thesis/` and regenerate `data/thesis_tables.json`
   with `tools/extract_tables.py` (copy of the extractor shipped in this kit).
2. Diff it with the kit's copy. Any changed number: update `FACTS.md` and the storyline, and
   log it in `DECISIONS.md`.
3. Recompute figure/table/equation numbering (`data/numbering.json`) and fix slide sources.
4. Clone the public repository (https://github.com/ymauhn/nexus-go) into `source/nexus-go/` and compare its consolidated result tables
   (look in `results/`, e.g. CSV tables of all runs, ensemble logs) with the dissertation's
   tables for: the late-fusion AVG values, the test-set rows of the three confrontation
   tables, and the cost table. Report agreements and disagreements. The dissertation is the
   reference for what the deck shows; a disagreement is reported to the user, not silently
   "fixed".
5. Also compare with `resultados_novos_pos_CC_update/tabelas/results_all_178runs.csv` (178
   runs, of which 8 superseded CC runs are excluded, leaving the 170 of the campaign).

## 2. Deck tests (Playwright, Chromium)

Run at 1600×900. Also take screenshots at 1280×720, 1920×1080 and 390×844 (phone).

| # | Check | Pass condition |
|---|---|---|
| 1 | Load | no console errors, no failed requests other than Google Fonts when offline |
| 2 | Slide count | 45 main slides, plus backup slides |
| 3 | Fragments | for every slide, the number of fragment steps equals `STORYLINE.md`; stepping forward then back restores the same DOM state |
| 4 | Overflow | every visible element's bounding box lies inside the 1600×900 canvas; no text element has `scrollWidth > clientWidth + 1` or `scrollHeight > clientHeight + 1` |
| 5 | Overlap | no two text boxes on a slide intersect (ignore intended overlays such as labels on charts, listed in an allowlist) |
| 6 | Figures | every one of the 26 figures in `FIGURES.md` appears at least once; each `<img>` has non-empty `alt` and `naturalWidth > 0` |
| 7 | Keys | →, ←, Space, PageDown, PageUp, Home, End, O, N, T, B, `#24` deep link all behave as in `BUILD.md` |
| 8 | Themes | screenshots of every slide in light and dark; text contrast against the slide surface ≥ 4.5:1 for body text, ≥ 3:1 for captions (compute from computed styles) |
| 9 | Reduced motion | with `reduced_motion="reduce"`, every slide's final fragment state matches the normal final state |
| 10 | INT-PROP | changing T and α changes node fills; Σ hop weights = 1; iterate == closed form; isolated node norm equals α^T · initial norm (±1e-6) |
| 11 | INT-PIPE | each route button sets the expected nodes to full opacity and dims the rest |
| 12 | INT-TEST | each tab × metric shows bar values equal to `thesis_tables.json` (read the rendered labels) |
| 13 | INT-DEDUP | sum shows 0.81 / 0.19; max shows 0.46 / 0.54 |
| 14 | Charts | every chart has a tooltip on hover and a table toggle |
| 15 | Size | `deck/dist/nexus-go-defense.html` under 12 MB (hard limit 16 MB) |
| 16 | Offline | with network blocked, the deck still renders with embedded fonts and all images |

Save screenshots as `qa/shots/<theme>/<slide>-<fragment>.png` and build a contact sheet
`qa/contact-<theme>.png` (all slides, final fragment state) so the user can review the whole
deck in one image per theme.

## 3. Number audit

Extract every number from the rendered text of each slide (final fragment state) and from the
Beamer PDF text (`pdftotext`). Each number must either occur in `dissertation.tex`, in
`FACTS.md` §1 (publication data), or be a derived value listed in `FACTS.md` with its source.
Allow slide numbers, years, `1600`, `900` and layer numbers. Also allow the illustrative
values of the schematic demos (INT-GBA edge scores, the INT-PROP toy graph, INT-FOLD geometry),
which must be labelled on screen as illustrative, and the INT-DEDUP example, which is the
dissertation's own example (0.80 written five times vs 0.95 written once). Print every unmatched number with
its slide; fix or justify each one in `DECISIONS.md`.

## 4. Visual review

After the automated checks pass, look at the contact sheets yourself, slide by slide, and fix
anything that reads poorly from a distance: crowded slides, tiny labels (nothing under 18 px
on the canvas except figure captions), figures too small to read, inconsistent alignment
between sibling elements, colour used outside its semantic meaning.

## 5. Beamer checks

- Compiles twice without errors; no `Overfull \hbox` larger than 10 pt on a frame.
- Frame titles and on-screen text match the HTML deck (diff the extracted texts).
- Every figure present; every new diagram present as vector PDF or 2× PNG.

## 6. Definition of done

- [ ] `deck/dist/nexus-go-defense.html` opens offline, 45 slides + backups, all checks green.
- [ ] Every number traceable; `qa/REPORT.md` lists the fact audit and the repo comparison.
- [ ] All 26 figures used; Figure 5.6 cropped and the mismatch reported.
- [ ] Interactives: INT-PIPE, INT-PROP, INT-DEDUP, INT-TEST, INT-RULES work by mouse and
      keyboard and survive going back and forth.
- [ ] Speaker notes on every slide; 30-minute cut list in the report.
- [ ] Beamer `.tex` + PDF (or Overleaf zip) with overlays and notes.
- [ ] GIFs (and MP4s if ffmpeg exists) in `gifs/`.
- [ ] `DECISIONS.md` complete; final report to the user in Portuguese.
