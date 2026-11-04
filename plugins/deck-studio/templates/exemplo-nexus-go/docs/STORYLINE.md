# STORYLINE: 45 slides, slide by slide

This is the script of the defense deck. Build every slide exactly as listed here, in this
order. The HTML deck and the Beamer deck share this storyline one to one.

How to read each entry:

- **Title**: the slide title as it appears on screen.
- **On screen**: the only text that appears on the slide. Bullets stay short. No paragraphs.
- **Visual**: a dissertation figure (path relative to the unzipped thesis folder, see
  `FIGURES.md`), a new component (id defined in `INTERACTIVES.md`), or both.
- **Reveal**: fragment order. `F1`, `F2`… appear one per keypress, in that order.
- **Notes**: speaker notes for the presenter view (English, 2 to 4 sentences).
- **Source**: where in `dissertation.tex` the content comes from. Every number on a slide
  must be traceable to this source (see `FACTS.md`).
- **Cut**: `30-min cut: skip` marks slides that can be hidden for a short version.

Copy rules for every slide: English; active voice; no em-dashes in slide text; numbers keep
the dissertation's precision (two decimals for metrics, `pp` for percentage points); ontology
names always in the order BP, CC, MF; method names exactly as in the dissertation
(`NEXUS-GO/Fixed`, `NEXUS-GO/GNN`, `NEXUS-GO/Early`, `NEXUS-GO/Late`, `First Generation`,
`ProtT5 baseline`).

Target duration: about 45 minutes at full length, about 30 minutes with the cut applied.

---

## Part 0. Opening

### S01. Title

- **Title**: NEXUS-GO
- **On screen**:
  - Subtitle: Network-Extended Unified Sequence Embeddings for Gene Ontology Function Annotation
  - Yeonatan Mauhnoom
  - Advisor: Prof. Dr. Zanoni Dias · Co-advisors: Prof. Dr. Hélio Pedrini and Dr. Gabriel Bianchin de Oliveira
  - Master's dissertation defense · Institute of Computing, University of Campinas (Unicamp) · November 16, 2026
- **Visual**: `INT-HERO` (ambient: a small protein chain at left, a PPI graph at right, a
  three-segment rule in the sequence/network/fusion colors joining them). Must render a
  complete still frame at load; animation is ambient only.
- **Reveal**: none.
- **Notes**: Good morning. My dissertation asks how far a protein interaction network can go
  toward predicting Gene Ontology annotations, alone and combined with a protein language
  model. The answer is NEXUS-GO, a framework that propagates ProtT5 embeddings over STRING.
- **Source**: preamble of `dissertation.tex` (title, advisors); date from `FACTS.md` §1 (the author,
  2026-10-28; the `.tex` still has `\datadadefesa{05}{11}{2026}`).

### S02. Roadmap

- **Title**: Roadmap
- **On screen**: six parts, each with a one-line hook:
  1. Motivation: the sequence-function gap
  2. Background and related work
  3. Data and evaluation
  4. Method: two generations, four NEXUS-GO routes
  5. Results: ablations, literature, cost, connectivity
  6. Conclusions
- **Visual**: horizontal track of six stations; the current part is highlighted on every later
  slide (the header part label reuses these names).
- **Reveal**: none.
- **Notes**: Six parts. The method part follows the same three decisions for every model:
  representation, propagation and prediction head.
- **Source**: Chapter 1, Document Structure.

---

## Part 1. Motivation

### S03. Proteins, and the gap between sequence and function

- **Title**: Millions of sequences, few known functions
- **On screen**:
  - Proteins take part in almost every cellular process
  - Sequencing is fast; experimental characterization is slow and expensive
  - Few records carry experimentally supported annotations
  - Automated prediction tries to close the gap (CAFA benchmark)
- **Visual**: `INT-FOLD` (bead chain folding into a compact 3D structure, rotating; label
  "schematic"). Next to it, `INT-GAP`: two growing bars labelled "sequences known" and
  "functions characterized", schematic, not to scale, no numbers.
- **Reveal**: F1 bullet 1 with `INT-FOLD` playing; F2 bullets 2–3 with `INT-GAP` growing;
  F3 bullet 4.
- **Notes**: Proteins catalyze reactions, signal, transport and give structure. Sequence
  databases grow far faster than experimental annotation, so most proteins have no
  experimentally supported function. CAFA measures automated predictors on proteins whose
  function was not yet public.
- **Source**: §1.1; §3.1.1.

### S04. Gene Ontology and the True Path Rule

- **Title**: Function as a hierarchy of terms
- **On screen**:
  - Three ontologies: Biological Process (BP), Cellular Component (CC), Molecular Function (MF)
  - Each is a directed acyclic graph of terms (`is_a`, `part_of`)
  - True Path Rule: a term implies all its ancestors
  - Task: hierarchical multi-label classification
- **Visual**: `fig4_go_hierarchy_EN.png` (left panel inconsistent, right panel consistent).
- **Reveal**: F1 three ontologies; F2 figure left half emphasized; F3 right half and the rule;
  F4 task statement.
- **Notes**: A protein carries many terms at different levels of specificity. If a specific
  term is annotated, every ancestor must be too. Predictions are made hierarchy-consistent
  before any metric is computed.
- **Source**: §2.1.2; §4.2 (hierarchical consistency, Eq. 4.1).

### S05. Context matters: protein interaction networks

- **Title**: Function also depends on context
- **On screen**:
  - Proteins act in complexes and pathways
  - PPI networks: nodes are proteins, edges are associations
  - Guilt by association: connected proteins tend to share functions
  - But STRING mixes evidence of uneven reliability, and about one third of proteins have no edge
- **Visual**: `fig1_protein_EN.png` (complex A-B) on the left; on the right `INT-GBA`, a small
  graph where an unlabelled node takes the colours of its neighbours (one pass), with the
  caption "a probabilistic guideline, not a rule".
- **Reveal**: F1 bullets 1–2 with the complex figure; F2 bullet 3 with `INT-GBA`; F3 bullet 4
  in the warning style.
- **Notes**: Sequence-derived features are strong, but part of a protein's function is set by
  its cellular context. STRING aggregates experiments, curated databases, co-expression,
  genomic context and text mining into one confidence score. Coverage is uneven, which
  becomes the central limitation of a network-only model.
- **Source**: §1.1; §2.1.3; §4.1.3.

### S06. Research questions

- **Title**: Seven research questions
- **On screen** (short labels, full wording in notes):
  - RQ1 Which network representation works best?
  - RQ2 How much does propagating ProtT5 over STRING add?
  - RQ3 Fixed vs learned aggregation, vector vs image heads
  - RQ4 Do early and late fusion help?
  - RQ5 How deep, and how much retention?
  - RQ6 How does it compare with the literature?
  - RQ7 Does it work on one global, aggregated network?
- **Visual**: two columns of RQ chips; each chip is reused on S42 with its answer.
- **Reveal**: F1 RQ1–RQ3; F2 RQ4–RQ5; F3 RQ6–RQ7.
- **Notes**: Read the full questions from §1.3 only if asked. Each one is answered on the
  conclusions slide.
- **Source**: §1.3.

### S07. Contributions and publications

- **Title**: Contributions
- **On screen**:
  1. NEXUS-GO: non-parametric multi-hop propagation of ProtT5 embeddings over STRING
  2. Controlled comparison of fixed vs learned (GCN, GAT) aggregation
  3. Vector vs image classification heads over the same embeddings
  4. Early and late fusion of fixed and learned routes
  5. Benchmark against five reimplemented methods, same splits and setting
  - Publications strip:
    - VISAPP 2026, *From Graphs to Images: Non-Parametric PPI Context Integration for
      Vision-Based Protein Function Prediction* (published, pp. 157–166)
    - Extended version, *Beyond Learnable Graphs: Fixed Multi-Hop PPI Diffusion of Sequence
      Embeddings for Robust Protein Function Prediction*, accepted in Communications in
      Computer and Information Science (CCIS), expected December 2026
- **Visual**: five numbered rows (numbering is real: they are the five announced
  contributions); publication strip at the bottom.
- **Reveal**: F1 contributions 1–3; F2 contributions 4–5; F3 publications.
- **Notes**: Five contributions, each answered with a result at the end. The first paper
  reported the first, sum-deduplicated campaign; the extended version continues the fixed
  route and adds a vector head next to the vision head.
- **Source**: §1.4; §1.5 (the dissertation text still says "under review"; the user confirmed
  the extended version was accepted, see `CONTEXT.md`).

---

## Part 2. Background and related work

### S08. Graphs and message passing

- **Title**: Graphs, adjacency and message passing
- **On screen**:
  - G = (V, E, w): proteins, associations, STRING confidence
  - Adjacency matrix A; sparse storage O(|E|)
  - Message passing: aggregate neighbours, update the node
  - L layers reach L hops; too many cause oversmoothing
- **Visual**: `fig_graph_notation.png` (left); `INT-MP` (right): a node, then its 1-hop ring,
  then its 2-hop ring, with messages flowing in.
- **Reveal**: F1 graph figure; F2 `INT-MP` 1-hop; F3 2-hop; F4 oversmoothing line.
- **Notes**: GCN aggregates with a symmetrically normalized adjacency; GAT learns attention
  weights over neighbours. Each layer widens the receptive field by one hop, and too many
  layers make neighbouring representations indistinguishable.
- **Source**: §2.2.1; §2.2.3 (GNN subsection).

### S09. Building blocks used later

- **Title**: Building blocks
- **On screen**: three panels with one line each:
  - MLP: the vector prediction head
  - CNN: the backbone of the image route (ResNet-50, ConvNeXt-Tiny)
  - Autoencoder: the compression inside deepNF, one of the baselines
- **Visual**: perceptron and MLP rendered from the TikZ in §2.2.3 (`tikz_perceptron.png`,
  `tikz_mlp.png`, see `FIGURES.md`); `fig2_cnn_EN.png`; `fig3_autoencoder_EN.png`.
- **Reveal**: F1 MLP; F2 CNN; F3 autoencoder.
- **Notes**: Only what the rest of the talk needs. The MLP is the vector head, the CNN is the
  vision head, and the autoencoder is how deepNF compresses diffusion states.
- **Source**: §2.2.3, §2.2.4.
- **Cut**: 30-min cut: skip.

### S10. Protein language models and ProtT5

- **Title**: Protein language models
- **On screen**:
  - Self-supervised pretraining on hundreds of millions of sequences
  - Transformer encoder: every residue attends to every other
  - ProtT5-XL-U50: T5 encoder, BFD then UniRef50, 15% residue masking
  - Used here as a frozen feature extractor
- **Visual**: `INT-PLM`: a short amino-acid string (e.g. `MKTAYIAKQR…`), tokens light up,
  attention arcs draw between residues, a pooled vector appears at the end. Schematic.
- **Reveal**: F1–F4 one bullet each; the animation steps with them.
- **Notes**: Language models turn function prediction into ordinary multi-label
  classification over a fixed-length vector. No gradient from our task reaches ProtT5; we
  read three encoder layers and keep them fixed.
- **Source**: §2.2.4, §2.2.5; §3.1.1; §5.4.1.
- **Cut**: 30-min cut: skip.

### S11. Related work: where do the parameters live?

- **Title**: From neighbour voting to graph transformers
- **On screen**:
  - Timeline: neighbour voting → diffusion → node embeddings → hybrids and GNNs → graph
    transformers
  - Each step added parameters, tuning surface and cost
  - Five methods retrained here: Mashup, deepNF, MELISSA, DeepGraphGO, SEGT-GO
- **Visual**: `INT-RW`: a horizontal timeline (top) and below it a "parameter placement" strip
  for the five baselines: Mashup and deepNF place none in the diffusion and all in the
  compression; DeepGraphGO between propagation steps; SEGT-GO in the transformer after a
  non-parametric multi-hop aggregation; MELISSA injects labels into the network construction.
- **Reveal**: F1 timeline; F2 statement on parameters; F3 the five-method strip.
- **Notes**: The field moved from fixed diffusion to learned attention, and each step added
  parameters. Decoupled methods such as SGC and APPNP move against that trend, and SEGT-GO's
  multi-hop aggregation is itself a plain matrix product.
- **Source**: §3.1.2, §3.1.3, §3.2, §3.3.

### S12. The gap and our position

- **Title**: The open question
- **On screen**:
  - Is a learned graph component still needed once the propagated object is informative?
  - Proposal: propagate ProtT5 embeddings with a fixed, finite-step operator, then use an
    ordinary head
  - A sequence representation exists for every protein, so the network adds instead of
    supplies
  - No prior visual route starts from a propagated language-model embedding
- **Visual**: a large question line in display type, then three compact claims.
- **Reveal**: F1 question; F2 proposal; F3 coverage claim; F4 visual route claim.
- **Notes**: The contribution is an architectural placement, not a new propagation mechanism.
  To our knowledge no previous work propagates protein language model embeddings directly
  while simplifying what consumes them.
- **Source**: §3.3.

---

## Part 3. Data and evaluation

### S13. A CAFA5-derived corpus

- **Title**: Data: a CAFA5-derived corpus
- **On screen**: compact table:

  | | Training | Validation | Test | Terms |
  |---|---|---|---|---|
  | BP | 73,768 | 9,221 | 9,221 | 500 |
  | CC | 74,328 | 9,292 | 9,292 | 498 |
  | MF | 62,909 | 7,864 | 7,864 | 499 |

  - 80 / 10 / 10 split, disjoint at protein level, no temporal or homology constraint
  - Labels per protein (mean): 25.91 BP, 12.48 CC, 7.55 MF
  - Label matrix density: 5.18%, 2.51%, 1.51%
- **Visual**: table plus a tiny density bar per ontology.
- **Reveal**: F1 table; F2 split properties; F3 label statistics.
- **Notes**: The official CAFA5 test labels were not available, so the splits come from the
  training corpus. Only about five hundred most frequent terms per ontology are kept, which
  makes absolute values not comparable with CAFA numbers.
- **Source**: Tables 4.1 and 4.2; §4.1.1, §4.1.2.

### S14. The STRING network

- **Title**: STRING v11.5: one aggregated network
- **On screen**:
  - 2,422,234 records, 791,011 distinct pairs, 86,423 proteins
  - Combined score in [0.400, 0.999]; confidence, not binding strength
  - Each pair repeated 3.06 times on average (up to 170), always with the same score
  - Degree is heavy-tailed: median 5–7, maximum near 800
- **Visual**: `fig_cap4_score_and_degree.png`.
- **Reveal**: F1 bullets 1–2 with left panel; F2 bullet 3; F3 bullet 4 with right panel.
- **Notes**: The medium-confidence floor of 400 comes with the inherited file. Repeated
  records carry no extra score information, which later decides the deduplication rule. Some
  knowledge circularity with the annotations cannot be excluded.
- **Source**: §4.1.3; Tables 4.3, 4.4.

### S15. One third of the proteins are isolated

- **Title**: One third of the proteins have no edge
- **On screen**:
  - Isolated: 36.65% BP, 34.95% CC, 32.19% MF
  - Stable across training, validation and test
  - Thresholds up to 0.40 are inert; at 0.90 more than half the proteins are isolated
- **Visual**: `fig_cap4_isolated_by_split.png` (left) and `fig_cap4_isolated_vs_threshold.png`
  (right).
- **Reveal**: F1 left figure and bullet 1–2; F2 right figure and bullet 3.
- **Notes**: Isolated proteins were kept as nodes so that every protein is scored. For a model
  that sees only the network, these proteins have no input at all. This is the limitation the
  second generation is built to remove.
- **Source**: §4.1.3; Table 4.4; Figures 4.2, 4.3.

### S16. How predictions are scored

- **Title**: Six protein-centric metrics
- **On screen**:
  - Primary criterion: wF<sub>max</sub>, information-content weighted
  - Also F<sub>max</sub>, F*<sub>max</sub> (root excluded), S<sub>min</sub> (bits, lower is
    better), AuPRC, IAuPRC
  - Predictions made hierarchy-consistent before scoring
  - 101 thresholds; full evaluation mode (unpredicted proteins count as zero recall)
- **Visual**: wF<sub>max</sub> equation (pre-rendered math, Eq. 4.8–4.10 condensed):
  `wF_max = max_τ 2·wpr(τ)·wrc(τ) / (wpr(τ)+wrc(τ))`, with `IC(v) = −log2 P(v | pa(v))` as a
  side note. Small inline diagram of score propagation `s̃_iv = max over descendants`.
- **Reveal**: F1 primary metric with equation; F2 the other five; F3 hierarchy and thresholds.
- **Notes**: wF<sub>max</sub> weights each term by information content, so frequent terms
  near the root count little. It is the selection criterion everywhere. The ancestor closure
  of predictions uses `is_a` only, which matters most for CC.
- **Source**: §4.2, §4.3.

### S17. Protocol: transductive, masked, validated once

- **Title**: Learning regime and protocol
- **On screen**:
  - One graph over train ∪ validation ∪ test; labels read only for training proteins
  - Every design decision on validation; test read once
  - Single seed: differences below 0.5 pp are ties (interpretability floor)
- **Visual**: `fig_5_02_learning_regime.png`.
- **Reveal**: F1 figure and bullet 1; F2 bullet 2; F3 bullet 3.
- **Notes**: Validation and test proteins contribute features and edges but never labels. The
  first generation uses a stricter train-basis construction. With a single seed, the talk
  treats sub-0.5 pp gaps as ties.
- **Source**: §5.2; §6.1.

---

## Part 4. Method

### S18. Two generations, three decisions

- **Title**: Two generations, three decisions
- **On screen**:
  - Representation → Propagation → Prediction head
  - Generation 1: network only
  - Generation 2 (NEXUS-GO): ProtT5 + network
- **Visual**: `fig_5_01_chapter_map.png`.
- **Reveal**: F1 the axis; F2 generation 1 row; F3 the band "≈1/3 isolated → null
  descriptor"; F4 generation 2 row.
- **Notes**: Every model decomposes into the same three decisions. The limitation of the first
  generation is a property of its input, and it motivates the second.
- **Source**: §5.1.

### S19. Generation 1: the network alone

- **Title**: Generation 1: the network alone
- **On screen**:
  - Input: row of the weighted adjacency, against training proteins
  - Pooling: raw, max, avg
  - Vector route: MLP or 1-D CNN
  - Image route: outer-difference matrix |v<sub>i</sub> − v<sub>j</sub>|, 224 × 224, ResNet-50
    or ConvNeXt-Tiny
  - Floor: a naive guilt-by-association baseline
- **Visual**: `fig_5_04_network_only_pipeline.png` (left, portrait);
  `fig_5_03_outer_difference.png` (right).
- **Reveal**: F1 pipeline; F2 vector route; F3 image route with the outer-difference figure.
- **Notes**: The descriptor is already a one-hop aggregation, so there is no separate
  propagation stage. The image route imports a convolutional bias into a non-visual vector,
  as SUPERMAGOv2 and DeepInsight did with isolated descriptors.
- **Source**: §5.3.

### S20. Generation 1 hits a wall

- **Title**: An isolated protein has no input
- **On screen**:
  - Null profile → null matrix → uniform image
  - The head can only return the class prior
  - No architecture can recover what is absent
  - Requirement: a representation that exists for every protein
- **Visual**: `fig_5_05_isolated_vs_connected.png`, shown next to a thumbnail of
  `fig_5_03_outer_difference.png` at the same scale for contrast.
- **Reveal**: F1 figure; F2 bullets 1–3; F3 requirement (accent style).
- **Notes**: For a third of the corpus the first generation sees nothing. The amino-acid
  sequence satisfies the requirement by construction, and that is where the second
  generation starts.
- **Source**: §5.3.5.

### S21. NEXUS-GO at a glance

- **Title**: NEXUS-GO: four routes
- **On screen**:
  - Sequence → ProtT5 → H<sup>(0)</sup> ∈ ℝ<sup>3072</sup>
  - STRING → weighted graph W → P = W D<sub>c</sub><sup>−1</sup>
  - Routes: /Fixed · /GNN · /Early · /Late
- **Visual**: `INT-PIPE` (interactive data-flow diagram with animated flow and route buttons).
  A toggle "Dissertation figure" swaps in `fig_5_06_hybrid_pipeline.png` (cropped, see
  `FIGURES.md`).
- **Reveal**: F1 sequence branch flows; F2 network branch flows; F3 /Fixed lights up; F4 /GNN;
  F5 /Early; F6 /Late. After F6 the route buttons stay clickable.
- **Notes**: Two inputs, two propagation routes and two ways of combining them. The first
  generation is reported as a topology-only control and carries no route name.
- **Source**: §5.1, §5.4.

### S22. The sequence representation

- **Title**: ProtT5-XL-U50, three layers, frozen
- **On screen**:
  - Chunks of at most 1,022 residues; masked mean-pool, then mean over chunks
  - Layers 24, 23, 22, concatenated: 3 × 1024 = 3072 dimensions
  - Exists for every protein, isolated or not
- **Visual**: `fig_5_07_prott5_extraction.png`.
- **Reveal**: F1 figure and bullet 1; F2 bullet 2; F3 bullet 3.
- **Notes**: Reading three adjacent layers avoids committing to one point between the
  pretraining objective and structural signal, at no tuning cost. Extraction is inherited
  from SUPERMAGOv2.
- **Source**: §5.4.1 (Sequence Embeddings); Appendix A.4.

### S23. The graph as an operator

- **Title**: From records to an operator
- **On screen**:
  - Symmetric weights, no self-loops, sparse COO (≤ 1.13 M stored entries; dense would be
    25–35 GB)
  - Deduplication: max keeps the score; sum multiplies it by the record count
  - Column-stochastic P = W D<sub>c</sub><sup>−1</sup>: weights are relative to each
    protein's neighbours
- **Visual**: `INT-DEDUP`: one protein with two neighbours, A (score 0.80, 5 records) and B
  (0.95, 1 record). Toggle `sum | max`: bar heights of their normalized weights swap order
  (sum: A 4.00 vs B 0.95, normalized 0.81 / 0.19; max: 0.80 vs 0.95, normalized 0.46 / 0.54).
- **Reveal**: F1 bullet 1; F2 `INT-DEDUP` with toggle; F3 bullet 3.
- **Notes**: Repeated records carry no extra score, so summing rewards how often a pair was
  written down. The maximum keeps the STRING score on its own scale. Normalization does not
  undo the reordering.
- **Source**: §5.4.1 (Interaction Graph; Edge Weighting and Deduplication); Table 6.10.
- **Cut**: 30-min cut: skip.

### S24. Fixed propagation (interactive)

- **Title**: Fixed propagation: no parameters
- **On screen**:
  - H<sup>(h)</sup> = α H<sup>(h−1)</sup> + (1 − α) Pᵀ H<sup>(h−1)</sup>, h = 1…T
  - Closed form: hop k gets weight C(T,k) α<sup>T−k</sup> (1 − α)<sup>k</sup>
  - Computed once, cached, reused every epoch
  - T = 0 or α = 1: the graph is switched off (internal control)
- **Visual**: `INT-PROP`: a graph of about 14 nodes (two isolated), node colours = 3-d
  "embeddings"; sliders for T (0–10) and α (0.1–0.9); a bar chart of binomial hop weights;
  the isolated nodes visibly shrink toward grey by α<sup>T</sup>.
- **Reveal**: F1 equation; F2 demo becomes interactive; F3 closed form bars; F4 control line.
- **Notes**: α retains part of the previous step, not of the original, so it slows mixing
  instead of re-injecting the input. The weights over hop counts are binomial with mean
  T(1 − α). Unlike personalized PageRank, the initial state is never reintroduced.
- **Source**: §5.4.2 (Fixed Propagation; Eq. 5.11, 5.12).

### S25. What propagation does to real proteins

- **Title**: Propagation on four real proteins
- **On screen**:
  - Connected proteins keep their structure and absorb their neighbourhood
  - An isolated protein becomes α<sup>T</sup> H<sup>(0)</sup>: same direction, smaller scale
  - So degree-zero gains cannot come from neighbourhood information
- **Visual**: `fig_5_08_fixed_propagation.png` (CC, T = 0 top, T = 6 and α = 0.4 bottom).
- **Reveal**: F1 figure; F2 bullet 1; F3 bullets 2–3.
- **Notes**: The rescaling is a structural property of the operator, not a tuned setting. The
  learned route adds self-loops and never mixes an isolated node with others.
- **Source**: §5.4.2 (Fixed Propagation); Figure 5.8.

### S26. Learned propagation

- **Title**: Learned propagation: GCN and GAT
- **On screen**:
  - GCN: symmetric normalization of W + I, then a trained transform
  - GAT: attention over neighbours, 4 heads, edge score as attribute
  - 2 layers, width 1024, output g ∈ ℝ<sup>1024</sup> for the head
  - Full-graph forward on every step: about 289 propagations per epoch
- **Visual**: two equations (Eq. 5.14 and 5.15) as pre-rendered math; a small contrast strip
  "fixed: computed once · learned: recomputed every step".
- **Reveal**: F1 GCN; F2 GAT; F3 sizes; F4 cost line.
- **Notes**: The GCN takes the STRING confidence as an edge weight; the GAT re-estimates it.
  Exact propagation with a mini-batch loss forces a full-graph pass for every batch, which is
  where the cost comes from.
- **Source**: §5.4.2 (Learned Propagation; Depth and Smoothing); Appendix A.7.
- **Cut**: 30-min cut: skip.

### S27. Two prediction heads

- **Title**: Vector head and vision head
- **On screen**:
  - Vector: MLP [1024, 512], batch norm, dropout 0.4
  - Vision: σ(clip(z)) split into three 32 × 32 channels, one per ProtT5 layer
  - Backbones: ResNet-50 and ConvNeXt-Tiny (ImageNet), fully fine-tuned
  - Caution: pixel adjacency has no meaning here
- **Visual**: `fig_5_09_reshape_to_image.png`.
- **Reveal**: F1 vector; F2 vision with figure; F3 backbones; F4 caution.
- **Notes**: The image is built inside the forward pass and never written to disk. Neighbouring
  pixels are neighbouring embedding coordinates only by storage order, a caveat that the
  results confirm.
- **Source**: §5.4.3.

### S28. The objective

- **Title**: Training objective: ProteinLoss
- **On screen**:
  - ℒ = ℒ<sub>ZLPR</sub> · (1 − wF1<sup>GO</sup>) · (1 − wF1<sup>prot</sup>)
  - ZLPR separates positive from negative terms at threshold zero
  - Two soft, IC-weighted F1 factors: one across terms, one across proteins
  - Brings training closer to the evaluation criterion
- **Visual**: the equation (Eq. 5.20) large; a two-axis sketch (terms × proteins in a batch)
  highlighting the slice each factor reduces over.
- **Reveal**: F1 equation; F2 ZLPR; F3 the two factors with the sketch; F4 rationale.
- **Notes**: Inherited from InterLabelGO+ through the group's sequence-only line. It beats
  binary cross-entropy by 5.47 pp on the first-generation mean, so every later run uses it.
- **Source**: §5.5.
- **Cut**: 30-min cut: skip.

### S29. Fusion: early or late

- **Title**: Combining the fixed and learned routes
- **On screen**:
  - Early: join representations, train one head (concat 4096 or block-wise add 3072)
  - Late: train each route, combine probabilities
  - Eleven late rules: linear γ, max, min, IC sigmoid, degree sigmoid, master equation, five
    stacking meta-classifiers
  - Coefficients chosen on validation (71 configurations per ontology)
- **Visual**: `fig_5_10_early_late_fusion.png`; below it a compact chip row with the eleven
  rules (`INT-RULES`, static chips that highlight on hover).
- **Reveal**: F1 figure; F2 early; F3 late; F4 the eleven rules; F5 selection note.
- **Notes**: The two routes are alternatives, no model is shared. Early fusion lets one head
  learn how to weigh the sources; late fusion leaves each route to its own optimization and
  needs no training to combine.
- **Source**: §5.6; Appendix A.6.

---

## Part 5. Results

### S30. The campaign

- **Title**: 170 runs, one funnel
- **On screen**:
  - 170 runs, about 136.3 GPU-hours (147 on an RTX A5500)
  - Each stage picks its winner on validation and hands it on
  - Test read once, at the end
- **Visual**: `INT-FUNNEL`: stages left to right: objective → vector architecture → vision
  backbone → depth T → retention α → learned encoder → deduplication → early fusion → late
  fusion → test. Each stage shows its winner label (ProteinLoss, MLP raw, ConvNeXt-Tiny,
  T per ontology, α per ontology, GCN, max, add+GCN+vector, linear γ, NEXUS-GO/Late).
- **Reveal**: F1 counts; F2 funnel animates stage by stage; F3 test node.
- **Notes**: The selection never touches the test partition. Every reported test number is a
  single evaluation of a frozen configuration.
- **Source**: §5.7; §6.1; Appendix A.7.

### S31. What Generation 1 settles

- **Title**: Generation 1 settles three choices
- **On screen**:
  - Naive term-frequency baseline: 43.56 mean wF<sub>max</sub>
  - ProteinLoss beats binary cross-entropy: +5.47 pp mean (+8.87 in MF)
  - MLP on the raw profile wins: 44.51; best 1-D CNN 41.16
  - Vision backbones: 36.99 to 37.62
- **Visual**: `INT-G1`: one horizontal bar chart of mean validation wF<sub>max</sub> for Naive,
  BCE, ProteinLoss(MLP max), MLP avg, MLP raw, CNN1D best, ResNet-50 avg, ConvNeXt-Tiny avg;
  a dashed reference line at the naive 43.56.
- **Reveal**: F1 naive line; F2 loss bars; F3 architecture bars; F4 backbone bars.
- **Notes**: Topology alone barely clears a predictor that looks at nothing: 0.95 pp on the
  mean, and below it in BP. The vector route wins, and ConvNeXt-Tiny is carried forward on a
  0.57 pp margin plus the earlier VISAPP campaign.
- **Source**: Tables 6.1–6.4; §6.2.

### S32. How deep? Vector head

- **Title**: One or two hops, high retention
- **On screen**:
  - Peak depth: T = 1 BP, T = 2 CC, T = 0 MF
  - Beyond the peak, performance falls 12.80 to 17.60 pp by T = 10
  - Best retention: α = 0.7 BP, α = 0.8 CC
  - The graph corrects the protein's own representation; it does not replace it
- **Visual**: `fig_hops_vetorial.png` (left), `fig_alpha_vetorial.png` (right).
- **Reveal**: F1 depth figure and bullets 1–2; F2 α figure and bullet 3; F3 bullet 4.
- **Notes**: In MF no amount of propagation helps; the best configuration switches the graph
  off. In CC everything below α = 0.4 is worse than everything above it; in BP the single
  exception is α = 0.9.
- **Source**: Tables 6.5, 6.6; §6.3.1.

### S33. The vision head behaves differently

- **Title**: The vision head wants deep propagation
- **On screen**:
  - Peak depth: T = 7 BP, T = 6 CC, T = 0 MF; a plateau, not a peak
  - Gains over T = 0: +5.84 BP, +2.93 CC (vector head: +1.85, +0.92)
  - Collapse at α ≤ 0.2: isolated nodes shrink as α<sup>T</sup> (10<sup>−7</sup> at T = 7)
  - Its best BP value, 52.17, is still below the vector head's graph-free 53.36
- **Visual**: `fig_hops_visual.png` (left), `fig_alpha_visual.png` (right).
- **Reveal**: F1 depth figure and bullets 1–2; F2 α figure and bullet 3; F3 bullet 4.
- **Notes**: The vision head extracts less from the node itself, so dilution costs it less and
  the neighbourhood average helps more. MF peaks at T = 0 in both heads, the strongest form of
  that observation.
- **Source**: Tables 6.7, 6.8; §6.3.1 (Vision Route).
- **Cut**: 30-min cut: skip.

### S34. Fixed vs learned aggregation

- **Title**: Learning the aggregation does not pay
- **On screen**:
  - GCN beats GAT in all 6 pairs (3.88 to 9.31 pp), and in 30 of 30 fusion pairs
  - Fixed 65.12 vs GCN 63.32 mean wF<sub>max</sub>
  - GCN ahead in BP by 0.55 (a tie); behind in CC by 0.59 and MF by 5.35
  - Deduplication: max never loses beyond noise; GAT gains most (+3.83 vision)
- **Visual**: `INT-FL`: grouped bars per ontology for Fixed (vector), GCN (vector), GAT
  (vector); a small inset strip with the six dedup Δ values and the 0.64 pp noise band.
- **Reveal**: F1 GCN vs GAT; F2 fixed vs GCN; F3 per-ontology margins; F4 dedup inset.
- **Notes**: Attention does not recover a better weighting than the STRING score it was
  handed. A plausible reason: the loss is masked to training nodes, so attention parameters
  see gradient only through a two-hop receptive field.
- **Source**: Tables 6.9, 6.11 (dedup); §6.3.2, §6.3.3.

### S35. Fusion: late beats early

- **Title**: Fusion helps; combining predictions helps more
- **On screen**:
  - Early, one configuration (add, GCN, vector): 65.80, +0.68 over fixed alone
  - Late, linear γ (0.50 BP, 0.55 CC and MF): 67.06, best in every ontology
  - Gains over the better component: +2.18 BP, +1.85 CC, +1.26 MF
  - Stacking importances: the two probabilities carry almost all the weight
- **Visual**: `INT-LATE`: horizontal bars of the eleven late rules (AVG), linear highlighted;
  next to it two small importance bars (decision tree: 0.960 fixed, 0.030 GNN, IC 7.8 × 10⁻⁶,
  log-degree 0.010).
- **Reveal**: F1 early; F2 late bars; F3 gains; F4 importances.
- **Notes**: A single scalar beats every elaborate rule, including gradient boosting. The
  auxiliary features do not predict which route is right, and the conditional rules converged
  to the flattest sigmoid in the grid. The ensemble fits one extra parameter on validation.
- **Source**: Tables 6.12–6.14; §6.3.4, §6.3.5; Appendix A.6 (Tables A.3–A.5).

### S36. Vector beats vision

- **Title**: Vector head wins 12 of 12
- **On screen**:
  - Margin on the mean: +6.62, +3.96, +2.69, +3.35 pp across the four stages
  - No trend toward zero
  - Neither image has the locality a convolution assumes
- **Visual**: `INT-VV`: dumbbell chart, four stages × three ontologies (vector dot vs vision
  dot), stage means labelled.
- **Reveal**: F1 chart; F2 margins; F3 interpretation.
- **Notes**: Generation 1 images index arbitrary training proteins; generation 2 images reshape
  embedding coordinates. Three independent pieces of evidence agree: pooling order, the 1-D
  CNN failure and this table.
- **Source**: Tables 6.15, 6.16; §6.4.

### S37. The validation journey

- **Title**: Where the gains come from
- **On screen**:
  - Mean validation wF<sub>max</sub>: Naive 43.56 → Generation 1 44.51 → ProtT5 alone 63.92
    → Fixed 65.12 → Early 65.84 → Late 67.06
  - Most of the jump is the language model; the graph adds the rest
- **Visual**: `INT-JOURNEY`: step chart (staircase) with the six stages, the sequence jump
  coloured blue, network gains orange, fusion gains green (semantic colours from
  `DESIGN.md`).
- **Reveal**: F1 first two steps; F2 ProtT5 jump; F3 graph and fusion steps; F4 takeaway.
- **Notes**: This is the whole dissertation on one axis. The protein language model explains
  most of the distance, and the graph contributes a consistent remainder in BP and CC. Each
  value is a mean of per-ontology champions on validation; the learned GNN alone (63.32)
  sits below the ProtT5 control because of MF, so it is not a step of the staircase.
- **Source**: Tables 6.1, 6.3 (MLP raw), 6.5 (T = 0 AVG), 6.15, 6.14.

### S38. Against the literature (test set)

- **Title**: Test set: NEXUS-GO vs five methods
- **On screen**:
  - NEXUS-GO/Late best in every column of the three tables, except AuPRC in MF
  - wF<sub>max</sub> margin over the strongest baseline: +9.77 BP, +8.67 CC, +4.93 MF
  - S<sub>min</sub>: 17.12 vs 20.11 (BP), 8.22 vs 9.67 (CC), 5.14 vs 5.67 (MF)
  - The ProtT5 baseline alone already beats every literature method on wF<sub>max</sub>
- **Visual**: `INT-TEST`: ontology tabs (BP, CC, MF) × metric selector (six metrics); horizontal
  bars for the 12 rows of Tables 6.17–6.19, grouped (literature, controls, NEXUS-GO routes);
  S<sub>min</sub> axis reversed with a "lower is better" label.
- **Reveal**: F1 chart in wF<sub>max</sub> BP; F2 margins; F3 S<sub>min</sub>; F4 ProtT5 note.
  After F4 the controls are clickable.
- **Notes**: Every baseline was retrained on the same corpus and scored with the same code.
  Three of them lose their multi-network mechanism on a single aggregated graph, so the
  ordering describes these adapted configurations, not the original papers.
- **Source**: Tables 6.17–6.19; §6.5; Appendix B.
- **Default state**: BP, wF<sub>max</sub>.

### S39. Coverage

- **Title**: Every protein gets a prediction
- **On screen**:
  - NEXUS-GO: 100% of the test partition in BP, CC, MF
  - DeepGraphGO and SEGT-GO: 95.1–96.3% (homology search)
  - Mashup, MELISSA, deepNF: 63.6–68.7% (network members only)
- **Visual**: `INT-COV`: three grouped horizontal bars per ontology.
- **Reveal**: F1 chart; F2 interpretation.
- **Notes**: Missing proteins count as misses in the comparison, so part of the distance to
  the network-only methods is reach, not ranking quality. The proteins they cannot reach are
  exactly the band where sequence-aware routes score highest.
- **Source**: Table 6.28; Table B.3.

### S40. Cost

- **Title**: A thirteenth of the time per epoch
- **On screen**:
  - Fixed + vector: 5.24 s/epoch, 6.4 GiB peak
  - GCN alone: 68.76 s/epoch, 14.1 GiB; GAT 161.41 s, 20.7 GiB
  - Matches or beats the GCN at about 1/13 of the time and under half the memory
  - Early fusion costs the same as fixed propagation once g is stored
- **Visual**: `fig_custo.png`.
- **Reveal**: F1 figure; F2 bullets 1–2; F3 bullet 3 (the central practical claim); F4 bullet 4.
- **Notes**: The fixed operator runs once per experiment; the learned ones recompute a
  full-graph propagation at every optimization step. Early-fusion cost excludes training the
  GCN checkpoint it consumes.
- **Source**: Table 6.20; §6.6.1; Appendix A.7 (Table A.6).

### S41. Connectivity: the degree paradox

- **Title**: The graph helps where there is graph
- **On screen**:
  - Every ProtT5 route scores worse on connected than on isolated proteins
  - The graph-free control already shows it, so the graph does not cause it
  - The graph's gain grows with degree: up to +9.05 BP, +8.71 CC, +4.64 MF at degree ≥ 50
- **Visual**: `fig_grau.png` (top), `INT-GAIN` (bottom): a heat strip of the gain table, rows
  BP/CC/MF, columns degree bands 0, 1–2, 3–5, 6–14, 15–49, ≥ 50, cells labelled with the gain
  and the winning route letter (f fixed, g GNN, h early fusion).
- **Reveal**: F1 figure; F2 bullet 1–2; F3 heat strip and bullet 3.
- **Notes**: Hubs tend to be multifunctional and harder for a sequence model. In BP the hardest
  proteins have degree 3 to 5, not zero. Degree-zero differences come from rescaling and
  refitting, so read topological gains from degree one upward.
- **Source**: Tables 6.21–6.27; Figure 6.6; §6.6.2.

---

## Part 6. Conclusions

### S42. Answers

- **Title**: Answers to the research questions
- **On screen** (one line per RQ chip from S06):
  - RQ1 The unreduced profile and an MLP; imposed locality hurts
  - RQ2 Large gain, mostly from ProtT5; propagation adds +1.87 BP, +2.15 CC, nothing in MF (test)
  - RQ3 Late 67.06 > Early 65.84 > Fixed 65.12 > GNN 63.32 (validation); vector head throughout
  - RQ4 Both help; late more (+1.26 to +2.18 pp, validation)
  - RQ5 One or two hops, α 0.7–0.8; MF prefers none
  - RQ6 Best in every column but one; +9.77 / +8.67 / +4.93 pp wF<sub>max</sub> (test)
  - RQ7 Works on one global aggregated network; partitioned graphs not tested
- **Visual**: the RQ chips from S06, each now with its answer.
- **Reveal**: F1 RQ1–RQ3; F2 RQ4–RQ5; F3 RQ6–RQ7.
- **Notes**: Use the conclusions chapter wording if asked for detail. RQ7 is applicability,
  not superiority over partitioned graphs.
- **Source**: Chapter 7.

### S43. Limitations

- **Title**: Limitations
- **On screen**:
  - Single seed; the 0.5 pp floor is a reading convention, not a confidence interval
  - Random protein-level split: transductive interpolation, possible homology leakage
  - STRING scores may encode annotation knowledge (circularity)
  - Fixed vs learned is not a single-factor ablation (α<sup>T</sup> scaling, normalization)
  - Baselines adapted to one aggregated network and a reduced label space
- **Visual**: plain list, warning colour for the markers.
- **Reveal**: F1–F2 bullets 1–3; F3 bullets 4–5.
- **Notes**: State these before the committee does. Each one is documented in the
  dissertation with its consequence.
- **Source**: Chapter 7 (limitations paragraphs).

### S44. Future work

- **Title**: Next steps
- **On screen**:
  - Separate the graph by organism, or one model per organism
  - Keep STRING evidence channels apart (typed or parallel edges)
  - Heterogeneous graphs (proteins, terms, evidence); compare with ProtHGT
  - Sampled aggregation (GraphSAGE) for a cheaper learned route
  - Richer node features: structure, domains, expression; most promising for MF
- **Visual**: five cards in a 3 + 2 grid, each with a small glyph drawn in SVG (no emoji).
- **Reveal**: F1 cards 1–3; F2 cards 4–5.
- **Notes**: The two most immediate are taxonomic scope and evidence channels. MF is where the
  network contributed least, so new node features matter most there.
- **Source**: Chapter 7 (future directions).

### S45. Thank you

- **Title**: Thank you
- **On screen**:
  - NEXUS-GO: fixed propagation of ProtT5 over STRING, fused with a GCN, best in every
    ontology at a fraction of the cost
  - Code: github.com/ymauhn/nexus-go
  - Publications: VISAPP 2026; extended version accepted in CCIS (expected December 2026)
  - Funding: CAPES, BTG Pactual · Computing resources: IC/Unicamp
  - Questions
- **Visual**: `INT-HERO` reprise (same composition as S01, calmer).
- **Reveal**: none.
- **Notes**: Thank the committee, the advisors and the funders. Open for questions.
- **Source**: Acknowledgements; Appendix A.2, A.8 (repository).

---

## Backup slides (after S45, hidden from the main count)

Add these after the thank-you slide, reachable by key `B` or by continuing past S45. They do
not count toward the 45.

- **B1** Hyperparameters (Table A.2) as a compact table.
- **B2** Late-fusion grid and selected coefficients (Tables A.3, A.4).
- **B3** Full early-fusion provenance × source grid (Table 6.13).
- **B4** Isolated vs connected wF<sub>max</sub> per route (Table 6.22).
- **B5** Spearman ρ between degree and per-protein F1 (Table 6.27).
- **B6** Adaptations of the five baselines (Table B.1) and their cost and coverage (Table B.2).
- **B7** Hierarchy closure: `is_a` only; affects 11.0% of ancestor pairs in BP, 46.7% in CC,
  one pair in MF.
- **B8** Computational environments (Table A.1).
