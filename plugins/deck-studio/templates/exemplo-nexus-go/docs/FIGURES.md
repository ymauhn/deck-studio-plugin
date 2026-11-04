# FIGURES: the 24 dissertation figures, plus 2 TikZ figures

Every figure below must appear in the deck (the user asked for all figures of the text).
Paths are relative to the unzipped thesis folder (see `CONTEXT.md`). Sizes were measured on
the September 2026 zip; re-check them.

| # | File | Size (px) | Dissertation | Slide | Notes |
|---|---|---|---|---|---|
| 1 | `fig4_go_hierarchy_EN.png` | 2525×1450 | Fig. 2.1, True Path Rule | S04 | Two panels: reveal left, then right |
| 2 | `fig1_protein_EN.png` | 643×643 | Fig. 2.2, complex A-B | S05 | Transparent background (RGBA); place on the figure plate |
| 3 | `fig_graph_notation.png` | 1800×1066 | Fig. 2.3, G=(V,E), adjacency | S08 | |
| 4 | `fig2_cnn_EN.png` | 960×540 | Fig. 2.6, CNN pipeline | S09 | Low resolution; do not upscale beyond 1.2× |
| 5 | `fig3_autoencoder_EN.png` | 2400×1400 | Fig. 2.7, autoencoder | S09 | Downscale for the web build |
| 6 | `fig_cap4_score_and_degree.png` | 1909×889 | Fig. 4.1 | S14 | Reveal left panel, then right |
| 7 | `fig_cap4_isolated_by_split.png` | 1485×869 | Fig. 4.2 | S15 | |
| 8 | `fig_cap4_isolated_vs_threshold.png` | 1485×889 | Fig. 4.3 | S15 | |
| 9 | `cap5/fig_5_01_chapter_map.png` | 3168×1892 | Fig. 5.1 | S18 | Reveal by rows using CSS clip masks |
| 10 | `cap5/fig_5_02_learning_regime.png` | 1242×598 | Fig. 5.2 | S17 | |
| 11 | `cap5/fig_5_04_network_only_pipeline.png` | 1644×2964 | Fig. 5.3 | S19 | Portrait; give it the left third |
| 12 | `cap5/fig_5_03_outer_difference.png` | 2345×990 | Fig. 5.4 | S19, S20 | Thumbnail reused on S20 |
| 13 | `cap5/fig_5_05_isolated_vs_connected.png` | 2345×990 | Fig. 5.5 | S20 | |
| 14 | `cap5/fig_5_06_hybrid_pipeline.png` | 2516×3960 | Fig. 5.6 | S21 (toggle) | **Crop**, see below |
| 15 | `cap5/fig_5_07_prott5_extraction.png` | 984×385 | Fig. 5.7 | S22 | Small; render at ≤ 1.6× |
| 16 | `cap5/fig_5_08_fixed_propagation.png` | 2957×1697 | Fig. 5.8 | S25 | |
| 17 | `cap5/fig_5_09_reshape_to_image.png` | 2617×774 | Fig. 5.9 | S27 | |
| 18 | `cap5/fig_5_10_early_late_fusion.png` | 1016×648 | Fig. 5.10 | S29 | |
| 19 | `fig_hops_vetorial.png` | 1139×680 | Fig. 6.1 | S32 | |
| 20 | `fig_alpha_vetorial.png` | 1139×680 | Fig. 6.2 | S32 | |
| 21 | `fig_hops_visual.png` | 1139×680 | Fig. 6.3 | S33 | |
| 22 | `fig_alpha_visual.png` | 1139×680 | Fig. 6.4 | S33 | |
| 23 | `fig_custo.png` | 1165×740 | Fig. 6.5 | S40 | |
| 24 | `fig_grau.png` | 1495×652 | Fig. 6.6 | S41 | |
| 25 | TikZ perceptron (§2.2.3, `\label{fig:perceptron}`) | render | Fig. 2.4 | S09 | Compile from the `.tex` snippet |
| 26 | TikZ MLP (§2.2.3, `\label{fig:mlp}`) | render | Fig. 2.5 | S09 | Compile from the `.tex` snippet |

Figure and table numbers were computed from the September 2026 `.tex` (see
`data/numbering.json`). Recompute them if the `.tex` changed.

Files present in the zip but **not** used by the dissertation (`fluxograma_g.png`,
`fluxograma_pipeline.png`, `generic_graph_example.png`, `perceptron-arq.png`,
`pipeline_graphs-1.png`, `ppi-image-cnn.png`, `string_ppi_image.png`) are older material in
Portuguese or from the qualifying exam. Do not use them, with one optional exception:
`string_ppi_image.png` (a real STRING neighbourhood view of insulin-pathway proteins) may
appear small on S05 as "what STRING looks like", labelled as a STRING screenshot.

## Known issue: Figure 5.6 late-fusion box

The bottom box of `fig_5_06_hybrid_pipeline.png` ("late fusion") lists rules that do not
match the dissertation text: it shows *average · linear (γ swept) · max · min · geometric mean ·
validation-weighted · stacked*, while §5.6.2 and Table 6.14 define eleven rules: linear γ,
maximum, minimum, IC sigmoid, degree sigmoid, master equation, and five stacking
meta-classifiers. There is no "average", "geometric mean" or "validation-weighted" rule.

In the deck:

1. Show Figure 5.6 cropped above the "late fusion" box (keep everything down to
   "500 logits → σ probabilities"). Find the crop row by scanning the image for the top border
   of the last green box; verify visually.
2. The correct rule list lives on S29 (`INT-RULES`) and S35.
3. Report the mismatch to the user in `qa/REPORT.md` as a suggested fix for the thesis figure.

## Rendering the two TikZ figures

Extract the two `tikzpicture` environments under `\label{fig:perceptron}` and
`\label{fig:mlp}` from `dissertation.tex`, wrap each in a `standalone` document with
`\usepackage{tikz}\usetikzlibrary{positioning}` and `xcolor`, compile with `pdflatex`, convert
to PNG at 300 dpi (`pdftoppm -png -r 300`) and to SVG if `pdf2svg` or `dvisvgm` is available
(SVG preferred for the HTML deck, recoloured to the ink token).

## Web build processing

- Keep originals untouched. Write processed copies to `deck/build/img/`.
- Downscale so the longest side is at most 2× its largest on-slide display size (slides are
  1600×900 logical px), then encode WebP at quality 88 (PNG for figures with sharp text if WebP
  shows artefacts; check `fig_5_07` and `fig4_go_hierarchy` closely).
- Embed as data URIs in the single-file build. Target total HTML size under 12 MB.
- Every thesis figure sits on a **figure plate** (see `DESIGN.md`) because the PNGs have
  light backgrounds; this keeps them readable in dark mode.
- Give every `<img>` an `alt` that states the takeaway, not the file name.
