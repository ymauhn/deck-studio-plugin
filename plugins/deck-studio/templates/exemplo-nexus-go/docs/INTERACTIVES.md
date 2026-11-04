# INTERACTIVES: new diagrams, animations and charts

Each component below is new (not in the dissertation). Build each as a self-contained module
with this interface, so the deck, the tests and the GIF exporter can drive it the same way:

```js
// deck/src/components/<id>.js
export function mount(el, opts) {
  return {
    step(n) {},        // apply fragment state n (0 = initial), idempotent, also when going back
    render(t) {},      // draw the frame at time t seconds (deterministic, used by GIF export)
    play() {}, pause() {},
    destroy() {},
    state() { return {} } // values the Playwright tests assert on
  };
}
```

General rules: SVG for diagrams and charts (crisp, theme-aware through `currentColor` and CSS
tokens), Canvas for the protein animation. No external fetches; data comes from
`data/thesis_tables.json` (inlined at build time). Every animation is deterministic given
`t`; no `Math.random()` without a fixed seed. With reduced motion, `step(n)` shows final states
and `play()` does nothing. Controls are real `<button>`/`<input type="range">` elements with
labels, stable ids and keyboard focus styles; clicks on them must not advance the slide.

---

## INT-HERO (S01, S45)

Ambient title composition. Left: a short bead chain (12–16 beads) drawn in `--seq`, gently
undulating. Right: a 10-node graph in `--net`, edges drawn with width ∝ a fake confidence
(label nothing; it is decorative). Between them the tri-colour rule, long. One slow loop
(≈ 12 s). Complete and legible as a still frame at t = 0. On S45 use the same layout at lower
intensity.

## INT-FOLD (S03): protein folding, schematic

Canvas, about 640 × 560 px. A chain of N = 54 beads (residues) folds from an extended,
slightly wavy line into a compact three-helix bundle, then rotates slowly about the vertical
axis.

- Target structure: three α-helices of 15 residues each (radius 2.3 Å, rise 1.5 Å per
  residue, 100° per residue), antiparallel, axes about 10 Å apart, joined by 3–4 residue
  loops. Generate coordinates procedurally; no PDB download.
- Animation: interpolate each bead from extended to folded with an ease-in-out over 4 s,
  helices forming one after another (N-terminal first), then rotate at 10°/s. Loop: hold
  folded 6 s, unfold quickly, repeat.
- Drawing: painter's algorithm by depth; bead radius and opacity scale with depth; bonds as
  2 px lines; colour along the chain from `--seq` (N-terminus) to `--fuse` (C-terminus).
- Caption: `schematic, not a real structure`.
- GIF export: 480 × 420, 20 fps, one full cycle.

## INT-GAP (S03)

Two horizontal bars labelled "sequences known" (`--seq`) and "functions characterized
experimentally" (`--fuse`). On reveal the first grows to the full width over 1.2 s, the second
to about one tenth. Caption: `schematic, not to scale`. No numbers, no axis.

## INT-GBA (S05): guilt by association

SVG graph: one centre node with "?" and six neighbours, each neighbour carrying 1–3 coloured
term dots (three term colours from the categorical slots 4, 5, 7 of the dataviz palette, so
they do not collide with the semantic blue/orange/green). Edge widths ∝ confidence scores
written next to them (0.45, 0.62, 0.71, 0.88, 0.93, 0.99). On reveal, pulses travel along the
edges and the centre fills with a donut whose segments are the confidence-weighted vote of
Eq. 5.3, `eq:met_baseline` (the naive baseline). Show the resulting percentages in the donut legend. Footer:
`a probabilistic guideline, not a rule`.

## INT-MP (S08): message passing and receptive field

SVG graph of ~18 nodes (fixed layout). Step 1: highlight a target node. Step 2: its 1-hop
neighbours light up and small dots travel along the edges toward the target; a ring labelled
`1 hop` encloses them. Step 3: same for 2 hops. Step 4: all node colours drift toward their
mean (oversmoothing hint) with label `too many layers: representations converge`.

## INT-PLM (S10): protein language model, schematic

A sequence string in `--font-data` (use a real-looking fragment such as
`MKTAYIAKQRQISFVKSHFSRQ`), tokens as cells. Step 1: tokens appear. Step 2: attention arcs from
one residue to several others (opacity ∝ a fixed weight list). Step 3: three stacked layer
bands labelled `layer 22`, `layer 23`, `layer 24`. Step 4: each band collapses (mean-pool) into
a 1024 bar; the three bars join into one `3072` bar in `--seq`.

## INT-RW (S11): related work, where the parameters live

Top: a timeline with five eras and example methods (years from the dissertation's
references):

| Era | Examples |
|---|---|
| Neighbour voting | Vazquez et al. 2003; Sharan et al. 2007 |
| Diffusion | Zhou et al. 2004; random walk with restart 2006; APPNP 2019 |
| Node embeddings | DeepWalk 2014; node2vec 2016; Mashup 2016; deepNF 2018 |
| Hybrids and GNNs | DeepGO 2018; Graph2GO 2020; DeepGraphGO 2021; CFAGO 2023 |
| Graph transformers and 2025 hybrids | NAGphormer 2023; SEGT-GO 2025; GTPLM-GO, GOBeacon, MSNGO, SPACE, ProtHGT (2025) |

Bottom: one row per method, each a mini pipeline of 2–3 boxes; boxes with trainable
parameters carry a small "weights" glyph (a 3 × 3 dot grid) and a solid border; fixed steps
have a dashed border:

- Mashup: random walk with restart (fixed) → low-dimensional factorization (learned) →
  classifier (k-NN here).
- deepNF: diffusion + PPMI (fixed) → autoencoder (learned) → MLP (learned here).
- MELISSA: labels → biclusters added to the network → signed diffusion (fixed) → k-NN.
- DeepGraphGO: InterPro features → GCN layers (learned transforms between fixed normalized
  adjacency) → output.
- SEGT-GO: InterPro × Â<sup>k</sup>, 4 hops (fixed) → transformer (learned).
- NEXUS-GO/Fixed (last row, highlighted): ProtT5 (frozen) → fixed multi-hop diffusion → MLP
  head (learned).

## INT-PIPE (S21): the NEXUS-GO pipeline, the centrepiece

SVG, full width. Nodes (rounded rectangles) and edges (paths):

```
amino-acid sequence ─▶ ProtT5-XL-U50 (frozen) ─▶ H(0) ∈ ℝ3072 ─┬─▶ Fixed propagation H(T) ─▶ MLP head ─▶ p_fix ─┐
                                                               │                                                ├─▶ Late fusion (linear γ) ─▶ 500 GO terms
STRING records ─▶ dedup (max) ─▶ W ─▶ P = W·Dc⁻¹ ───────────────┘                                                │
                              └──▶ edge index + score ─▶ GCN / GAT (2 layers) ─▶ g ∈ ℝ1024 ─▶ MLP head ─▶ p_gnn ─┘
                                        H(T) ─┐
                                        g ────┴─▶ Early fusion (concat 4096 | add 3072) ─▶ MLP head ─▶ 500 GO terms
```

- Colours: sequence nodes and edges `--seq`; network nodes and propagation `--net`; fusion
  and output `--fuse`; heads `--ink-2` outline.
- Flow animation: animated `stroke-dashoffset` dashes along active edges plus small particles,
  in the edge's semantic colour.
- Route buttons above: `All`, `/Fixed`, `/GNN`, `/Early`, `/Late`. Selecting a route keeps its
  nodes and edges at full opacity and dims the rest to 15%. The /Late route includes both
  base routes. The /Early route includes the stored g.
- Hover a node: tooltip with one line and its numbers (e.g. "Fixed propagation · no
  parameters · computed once and cached · T and α tuned per ontology").
- Toggle `Dissertation figure` swaps the SVG for the cropped `fig_5_06_hybrid_pipeline.png`.
- Fragments drive: F1 sequence branch, F2 network branch, F3–F6 the four routes in order.
- GIF export: cycle All → /Fixed → /GNN → /Early → /Late, 2 s each, 1200 px wide.

## INT-DEDUP (S23): why deduplication matters

One protein with two neighbours. A: score 0.80, written 5 times. B: score 0.95, written once.
Toggle `sum | max`:

- sum: raw weights 4.00 and 0.95 → normalized 0.81 and 0.19 (A dominates).
- max: raw weights 0.80 and 0.95 → normalized 0.46 and 0.54 (B dominates).

Show raw and normalized bars, animate the swap. Caption: example from §5.4.1 (Edge Weighting and Deduplication); real file:
mean multiplicity 3.06, maximum 170, no pair with divergent scores.

## INT-PROP (S24): fixed propagation, live

The most important interactive. SVG graph of 14 nodes on a fixed layout: one connected
component of 12 nodes with a hub (degree 6) and a chain, plus 2 isolated nodes. Each node holds
a 3-dimensional vector in [−1, 1]³ (think: three ProtT5 layers in miniature); draw the node as
a circle filled with `rgb(0.5 + 0.5·v)` and, inside it, three tiny bars for the three values.
The zero vector is mid-grey, so shrinkage is visible.

- Edge weights w ∈ [0.40, 0.99] (draw edge width ∝ w). Build P = W·D<sub>c</sub><sup>−1</sup>
  exactly as Eq. 5.9 (`eq:met_P`) (column-stochastic; isolated columns stay zero).
- Controls: `T` slider 0–10 (step 1), `α` slider 0.1–0.9 (step 0.1), defaults T = 2, α = 0.5;
  a `play` button that sweeps T from 0 to 10.
- Recompute H<sup>(T)</sup> by iterating Eq. 5.11 (`eq:met_recorrencia`) on every change (cheap).
- Right panel: bar chart of hop weights `w_k = C(T,k) α^(T−k) (1−α)^k`, k = 0…T, with the
  readouts `mean hops = T(1−α)` and `own weight = α^T`. Assert in code that Σ w_k = 1 (±1e-9)
  and that iterating and the closed form agree (±1e-9) for the demo graph.
- Isolated nodes: annotate with `α^T · H(0)`; they visibly fade toward grey as T grows or α
  falls (this is the caveat the dissertation states for isolated proteins).
- Optional readout: average pairwise distance among connected nodes, which shrinks with T
  (oversmoothing).
- `state()` returns T, α, the hop weights and the isolated nodes' vector norms.
- GIF export: α = 0.5, T from 0 to 10 and back, then α from 0.9 to 0.1 at T = 7.

## INT-RULES (S29)

Eleven chips in six families: Linear (γ) · Max · Min · IC sigmoid · Degree sigmoid · Master
equation · Stacking ×5 (decision tree, logistic regression, MLP, random forest, gradient
boosting). Hovering a chip shows its formula (Eq. 5.26–5.34, labels `eq:met_ens_*`, pre-rendered SVG) and its
validation AVG from `late`.

## INT-FUNNEL (S30): the selection funnel

Ten stations left to right, each a small label + winner + the number of compared
configurations where the dissertation states it:

objective (2: BCE vs ProteinLoss) → vector architecture × pooling (6) → vision backbone ×
pooling (4) → depth T (0–10, per head) → retention α (0.1–0.9) → learned encoder (GCN vs GAT,
2 heads) → deduplication (max vs sum) → early fusion (60-run grid) → late fusion (71
configurations per ontology) → test (read once).

Winners: ProteinLoss · MLP raw · ConvNeXt-Tiny · T = 1/2/0 (vector) · α = 0.7/0.8 · GCN · max ·
add + GCN + vector · linear γ · NEXUS-GO/Late. Animate left to right on F2; the test station
uses `--fuse`.

## Charts (all read `data/thesis_tables.json`)

| id | Slide | Form | Data key(s) | Notes |
|---|---|---|---|---|
| INT-G1 | S31 | horizontal bars, mean validation wF<sub>max</sub> | `naive`, `loss`, `gen1_arch`, `gen1_backbone` | dashed reference line at naive 43.56 |
| INT-FL | S34 | grouped bars per ontology: Fixed, GCN, GAT (vector head) + dedup Δ strip | `vector_vs_vision` (fixed row), `gnn`, `dedup` | shade the 0.64 pp noise band on the Δ strip |
| INT-LATE | S35 | horizontal bars of 11 rules (AVG) + importance mini-bars | `late` + FACTS §5 importances | highlight linear γ; axis starts at 65 with a visible break marker, or use a dot plot to avoid truncated bars |
| INT-VV | S36 | dumbbell: 4 stages × 3 ontologies, vector vs vision | `vector_vs_vision` | stage mean annotated |
| INT-JOURNEY | S37 | step chart of six means | FACTS §5 journey | sequence jump in `--seq`, network gains `--net`, fusion gains `--fuse` |
| INT-TEST | S38 | ontology tabs × metric select; 12 horizontal bars | `test_BP`, `test_CC`, `test_MF` | keep table order; S<sub>min</sub> reversed; naive as a dashed reference |
| INT-COV | S39 | grouped horizontal bars | `coverage` | 0–100% axis |
| INT-GAIN | S41 | heat strip 3 × 6 with labels | `graph_gain_by_degree` | single-hue `--net` ramp for positive gains; the one negative cell in neutral grey with a "−" label; letter of the winning route in each cell |

For bar charts whose values sit in a narrow range (e.g. 65–67), prefer a dot plot with a
labelled non-zero axis over truncated bars.
