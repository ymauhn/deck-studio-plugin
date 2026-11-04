# FACTS: every number the deck may show

Rule: a number appears on a slide only if it appears in `dissertation.tex` (the latest
version, see `CONTEXT.md`). This file is a pre-extracted index to save time, not a
replacement for the source. Before building, re-run the extraction against the current
`.tex` and diff it with `data/thesis_tables.json` (procedure in `QA.md`). If a value here
disagrees with the `.tex`, the `.tex` wins; list the disagreement in `qa/REPORT.md`.

`data/thesis_tables.json` holds 34 tables parsed directly from the `.tex` (keys listed at the
end of this file). Charts must read their data from that JSON (or from a regenerated copy),
never from numbers typed by hand.

Conventions: metrics are percentages with two decimals; `pp` = percentage points;
S<sub>min</sub> is in bits and lower is better; ontology order is always BP, CC, MF.
"Validation" and "test" must never be mixed on one chart.

---

## 1. People, venue, dates

- Author: Yeonatan Mauhnoom.
- Advisor: Prof. Dr. Zanoni Dias. Co-advisors: Prof. Dr. Hélio Pedrini and Dr. Gabriel
  Bianchin de Oliveira.
- Institute of Computing (IC), University of Campinas (Unicamp). Master's (mestrado).
- Defense date: November 16, 2026, as the author said on 2026-10-28. `dissertation.tex` still has
  `\datadadefesa{05}{11}{2026}`; the slides follow the author.
- Funding (acknowledgements): CAPES and BTG Pactual; computational resources from IC/Unicamp.
- Repository: https://github.com/ymauhn/nexus-go
- Publications:
  - Published: Mauhnoom, de Oliveira, Pedrini, Dias. *From Graphs to Images: Non-Parametric
    PPI Context Integration for Vision-Based Protein Function Prediction*. Proceedings of the
    21st International Conference on Computer Vision Theory and Applications, Volume 1:
    VISAPP, pp. 157–166, SCITEPRESS, 2026. DOI 10.5220/0014403700004084. (Its results used
    the sum deduplication rule; the dissertation campaign uses max.)
  - Accepted: same authors. *Beyond Learnable Graphs: Fixed Multi-Hop PPI Diffusion of
    Sequence Embeddings for Robust Protein Function Prediction*. Extended and revised version
    of the VISAPP paper, accepted in Communications in Computer and Information Science
    (CCIS), assigned number 8 in the post-publication issue, expected publication
    December 21, 2026. Scope: the fixed-propagation route, with a vector (MLP) head added to
    the vision head. Source: acceptance e-mail relayed by the author (the `.tex` may still say
    "under review"; the deck uses the accepted status).

## 2. Corpus (Chapter 4)

| | Training | Validation | Test | Terms |
|---|---|---|---|---|
| BP | 73,768 | 9,221 | 9,221 | 500 |
| CC | 74,328 | 9,292 | 9,292 | 498 |
| MF | 62,909 | 7,864 | 7,864 | 499 |

- Split ≈ 80/10/10, disjoint at protein level, no temporal/taxonomic/homology constraint.
- Labels per protein, mean (median, max): BP 25.91 (19, 264); CC 12.48 (10, 88);
  MF 7.55 (6, 65).
- Minimum positives per retained term: 907 BP, 68 CC, 80 MF.
- Label matrix density: 5.18% BP, 2.51% CC, 1.51% MF.
- Information content, median (max) bits: BP 1.06 (5.54), CC 2.05 (9.79), MF 1.50 (9.26).
- GO release cited for ontology size (June 19, 2026): 10,052 MF, 4,075 CC, 24,136 BP valid
  terms. Only ~500 per ontology are retained here.
- Metrics computed only over the retained vocabulary; absolute wF<sub>max</sub> and
  S<sub>min</sub> are not comparable with CAFA figures.

## 3. STRING network (Chapter 4, Chapter 5)

- STRING v11.5. Combined score / 1000, medium-confidence floor 400 → scores in
  [0.400, 0.999].
- Inherited file: 2,422,234 records, 791,011 distinct pairs, 86,423 proteins. Mean
  multiplicity 3.06 (max 170); 0 pairs with divergent score across repetitions.
- Mean score by records per pair: 1 → 0.669; 2 → 0.742; 3 → 0.791; 4–5 → 0.839;
  6–10 → 0.897; 11–20 → 0.936; 21–50 → 0.961; > 50 → 0.952. Spearman 0.47.
- Induced graphs:

| | BP | CC | MF |
|---|---|---|---|
| Nodes | 92,210 | 92,912 | 78,637 |
| Undirected edges | 492,920 | 566,566 | 470,206 |
| Isolated | 33,797 (36.65%) | 32,477 (34.95%) | 25,317 (32.19%) |
| Degree mean / median / max | 10.7 / 5 / 763 | 12.2 / 7 / 798 | 12.0 / 7 / 805 |

- Isolated in the test split: 3,421 of 9,221 (37.1%), 3,188 of 9,292 (34.3%), 2,553 of 7,864
  (32.5%).
- Threshold: inert up to 0.400; above 0.900 more than half of the proteins are isolated.
- Sparse: dense matrix would take 25–35 GB in fp32; stored entries ≤ 1,133,132 (CC), density
  1.31 × 10⁻⁴ (CC), 1.52 × 10⁻⁴ (MF).
- Under the max rule mean edge weights: 0.7491 BP, 0.7599 CC, 0.7522 MF. Summation reaches
  167.79 in BP.
- Hierarchy closure of predictions uses `is_a` only: affects 387 of 3,507 ancestor pairs in
  BP (11.0%), 2,056 of 4,405 in CC (46.7%), 1 pair in MF.

## 4. Method constants

- ProtT5-XL-U50 encoder (`Rostlab/prot_t5_xl_half_uniref50-enc`), frozen, bfloat16. BART-like
  denoising, 15% residue masking, BFD then UniRef50.
- Chunks ≤ 1,022 tokens; layers 24, 23, 22; masked mean-pool within chunk, equal-weight mean
  across chunks; concatenation in order 24‖23‖22 → H<sup>(0)</sup> ∈ ℝ<sup>3072</sup>.
- Cache: 791,277 files, ≈ 3.3 GB content, ≈ 6.5 GB allocated.
- P = W D<sub>c</sub><sup>−1</sup>, ε = 10⁻¹².
- Fixed operator: H<sup>(h)</sup> = α H<sup>(h−1)</sup> + (1 − α) Pᵀ H<sup>(h−1)</sup>;
  closed form Σ<sub>k</sub> C(T,k) α<sup>T−k</sup>(1−α)<sup>k</sup> (Pᵀ)<sup>k</sup>
  H<sup>(0)</sup>; mean hop count T(1 − α); unpropagated weight α<sup>T</sup>; isolated node
  → α<sup>T</sup> H<sup>(0)</sup>.
- Learned: GCN and GAT, 2 layers, hidden width 1024, output g ∈ ℝ<sup>1024</sup>; GAT 4 heads
  (hidden), 1 head (output), LeakyReLU slope 0.2; dropout 0.3 between convolutions.
- Heads: vector MLP [1024, 512] with batch norm, ReLU, dropout 0.4. Vision: clip to
  [−50, 50], sigmoid, three 32 × 32 channels (layers 24, 23, 22 → R, G, B), ResNet-50 or
  ConvNeXt-Tiny pretrained on ImageNet, all weights unfrozen, no resizing.
- Generation 1: MLP [512, 256], dropout 0.5, batch 32, max 200 epochs, patience 25; profile
  pooled to 1024 (vector) or 224 (image); outer-difference image 224 × 224 × 3 channels.
- Training (Generation 2): Adam, lr 1 × 10⁻⁴, no weight decay, no schedule, batch 256, max 250
  epochs, early stopping patience 20 on validation loss, seed 1337, 4 data workers, mixed
  precision, gradient checkpointing in convolutions.
- Objective: ProteinLoss = ZLPR × (1 − wF1<sup>GO</sup>) × (1 − wF1<sup>prot</sup>), from
  InterLabelGO+.
- Late fusion grid: 71 configurations per ontology, 213 total. Selected: γ = 0.50 BP,
  0.55 CC, 0.55 MF; IC<sub>thr</sub> 1.1 / 0.4 / 0.4; κ<sub>IC</sub> 1.0 all; d<sub>thr</sub>
  3 / 14 / 28; κ<sub>deg</sub> 0.25 all; λ 0.5 / 0.4 / 0.9.
- Early fusion: concat → 4096; add (block-wise average with g) → 3072; head fixed at
  [1024, 512]; grid of 60 runs.

## 5. Results on validation (Chapter 6)

### Generation 1 (mean over BP, CC, MF)

- Naive term frequency: 39.43 / 47.11 / 44.14 → **43.56**.
- Loss (MLP, max pooling): BCE 37.02 vs ProteinLoss 42.49 (+3.48 BP, +4.07 CC, +8.87 MF,
  +5.47 mean).
- Architecture × pooling: MLP raw **44.51** (36.37 / 48.25 / 48.92), MLP max 42.49, MLP avg
  39.98; CNN1D max 41.16, avg 40.78, raw 39.80. MLP raw leads best CNN by 3.35; raw vs avg
  spread 4.53.
- Backbones (image route): ResNet-50 avg 37.05, max 36.99; ConvNeXt-Tiny avg 37.62, max 37.41.
- Generation 1 beats naive by 0.95 pp on the mean, but is below it in BP.

### Fixed propagation (α = 0.5 for the depth sweep)

- Vector head, T = 0: 53.36 / 65.21 / 73.18 (63.92). Peaks: BP T = 1 (55.21, +1.85), CC T = 2
  (66.13, +0.92), MF T = 0. Decay peak → T = 10: 13.60 / 12.80 / 17.60 pp.
- Vector head α sweep at best depth: BP best α = 0.7 (55.23), CC best α = 0.8 (66.94).
  Amplitude 5.51 BP, 8.45 CC. Band 0.5–0.8: BP within 0.74, CC within 1.08 of optimum.
- Vision head, T = 0: 46.33 / 60.13 / 68.25. Peaks BP T = 7 (52.17, +5.84), CC T = 6 (63.06,
  +2.93), MF T = 0. Decay to T = 10: 1.19 BP, 0.94 CC. Best α = 0.5 both; amplitude 11.51 BP,
  10.62 CC; α ≤ 0.2 collapse (40.66 BP).
- Fixed champion means: vector **65.12** (55.23 / 66.94 / 73.18); vision 61.16.

### Learned propagation

- GCN vector 55.78 / 66.35 / 67.83 (**63.32**); GCN vision 53.10 / 63.33 / 65.46 (60.63);
  GAT vector 46.47 / 61.14 / 63.83 (57.15); GAT vision 46.17 / 59.45 / 61.03 (55.55).
- GCN beats GAT in 6 of 6 pairs, by 3.88 to 9.31 pp; and in 30 of 30 early-fusion pairs, by
  1.37 to 8.22 pp (36 of 36 overall).
- Fixed vs GCN: GCN +0.55 BP (tie), −0.59 CC, −5.35 MF.

### Deduplication (Δ = max − sum on the mean)

- Fixed vector −0.25; fixed vision −0.28; GCN vector +0.21; GCN vision +1.00; GAT vector +0.69;
  GAT vision +3.83. Noise reference (MF at T = 0): 0.27 vector, 0.64 vision.

### Early fusion

- add + GCN + vector: 56.52 / 67.07 / 73.81 (**65.80**); concat + GCN + vector 65.68.
  Per-ontology champions mean **65.84**.
- +0.68 over fixed alone, +2.48 over GCN alone. Gain over better component: 0.74 BP, 0.26 CC,
  0.63 MF; 0.72 on the mean (conclusions).
- Provenance: embedding trained with a vector head wins 10/10 on the vision head (1.86–3.69 pp,
  median 2.91); 14/20 on the vector head (median 1.68). Hyperparameters: vector head prefers its
  own depth/α in 16/16 (median 1.79); vision head indifferent (median −0.27, 2/8).

### Late fusion (AVG)

- Linear γ **67.06** (57.96 / 68.79 / 74.44); master equation 66.48; RF stacking 66.33; MLP
  stacking 66.32; LR stacking 66.17; GB stacking 66.19; IC sigmoid 66.16; max 65.91; DT
  stacking 65.78; degree sigmoid 65.73; min 65.72.
- Gain over better component: +2.18 BP, +1.85 CC, +1.26 MF.
- Importances (fixed prob, GNN prob, IC, log-degree): decision tree 0.960, 0.030, 7.8 × 10⁻⁶,
  0.010; random forest 0.629, 0.359, 0.003, 0.010.

### Vector vs vision (champion means)

- First Generation 44.51 vs 37.89 (+6.62); Fixed 65.12 vs 61.16 (+3.96); GNN 63.32 vs 60.63
  (+2.69); Early 65.84 vs 62.49 (+3.35). Vector wins 12 of 12 ontology × stage comparisons.

### Validation journey (mean of per-ontology champions)

Naive 43.56 → First Generation 44.51 → ProtT5 only (T = 0, vector) 63.92 → NEXUS-GO/Fixed
65.12 → NEXUS-GO/Early 65.84 → NEXUS-GO/Late 67.06. (NEXUS-GO/GNN 63.32 is below the ProtT5
control on the mean.)

## 6. Results on test (Tables 6.17–6.19)

Read the full six-metric rows from `data/thesis_tables.json` keys `test_BP`, `test_CC`,
`test_MF`. Headline wF<sub>max</sub>:

| Method | BP | CC | MF |
|---|---|---|---|
| Naive baseline | 40.22 | 48.13 | 43.38 |
| DeepGraphGO | 48.92 | 60.35 | 68.96 |
| SEGT-GO | 44.57 | 55.52 | 64.12 |
| Mashup | 39.64 | 48.28 | 44.22 |
| MELISSA | 37.72 | 47.19 | 42.86 |
| deepNF | 26.95 | 36.51 | 39.00 |
| First Generation | 37.30 | 48.39 | 48.62 |
| ProtT5 baseline | 53.74 | 64.78 | 72.57 |
| NEXUS-GO/Fixed | 55.61 | 66.93 | 72.57 |
| NEXUS-GO/GNN | 56.95 | 66.70 | 67.77 |
| NEXUS-GO/Early | 57.51 | 67.18 | 72.94 |
| NEXUS-GO/Late | **58.69** | **69.02** | **73.89** |

- Late is best in every column of the three tables except AuPRC in MF (Early 81.88 vs Late
  76.53).
- Margin of Late over the strongest baseline (DeepGraphGO): +9.77 BP, +8.67 CC, +4.93 MF.
- S<sub>min</sub>: Late 17.12 vs DeepGraphGO 20.11 (BP); 8.22 vs 9.67 (CC); 5.14 vs 5.67 (MF).
- First Generation trails the ProtT5 baseline by 16.44 BP, 16.39 CC, 23.95 MF.
- Propagation adds over the ProtT5 baseline on test: +1.87 BP, +2.15 CC, 0 MF.
- In MF, ProtT5 baseline and NEXUS-GO/Fixed are the same run (T = 0).
- The naive baseline is excluded from the ranking.

## 7. Coverage (Table 6.28, Table B.3)

- NEXUS-GO (all routes): 100% (9,221 / 9,292 / 7,864).
- DeepGraphGO / SEGT-GO: 96.3% BP, 95.1% CC, 95.7% MF.
- Mashup / MELISSA / deepNF: 63.6% BP, 66.6% CC, 68.7% MF.

## 8. Cost (Table 6.20, Appendix A.7, Table A.6)

- Campaign: 170 runs, ≈ 136.3 GPU-hours; 147 runs on RTX A5500 (103.0 h); 23 vision runs on
  GTX 1080 Ti (33.3 h, ~8× slower, excluded from timing comparisons).
- s/epoch and peak VRAM (GiB): fixed+vector 5.24, 6.4; fixed+vision 18.45, 6.4; GNN+vector
  102.14, 20.7; GNN+vision 108.41, 21.1; early+vector 5.26, 6.4; early+vision 18.63, 6.4.
- Separated encoders: GCN 68.76 s/epoch, 14.1 GiB; GAT 161.41 s/epoch, 20.7 GiB.
- Ratios used in the text: GCN/fixed ≈ 13.1× time ("a thirteenth"), 2.2× memory ("less than
  half"); family aggregate 19.5× and 3.2×.
- ≈ 289 full-graph propagations per epoch for the learned route (73,768 / 256).
- Baselines: Mashup 10.0 h embedding; MELISSA ≈ 30.3 h; SEGT-GO 34.6 h; DeepGraphGO ≈ 1 h of
  training plus ≈ 3 h of BLAST per ontology and partition.

## 9. Connectivity (Tables 6.21–6.27)

- wF<sub>max</sub> connected minus isolated: ProtT5 −9.66 / −6.92 / −4.45; Early −7.88 / −3.33
  / −2.80; First Generation +19.02 / +19.77 / +16.27.
- Gain of best graph route over T = 0 control by degree band (0, 1–2, 3–5, 6–14, 15–49, ≥ 50):
  BP 3.24h, 1.68h, 1.77f, 3.79h, 5.97h, 9.05h; CC 1.66f, 2.18f, 2.31f, 2.44h, 4.01g, 8.71g;
  MF 0.21h, 0.24h, −0.33h, 1.06h, 1.73h, 4.64h. (f fixed, g GNN, h early fusion.)
- From band 1–2 to ≥ 50 the gain multiplies by 5.4 BP, 4.0 CC, 19 MF.
- BP U-shape: minimum in the 3–5 band, 12–15 pp below each route's isolated figure.
- Spearman ρ (degree vs per-protein F1): control −0.109 / −0.129 / −0.128; best route −0.077 /
  −0.076 / −0.110; GNN in MF −0.185.

## 10. Research question answers (Chapter 7)

Use the S42 lines in `STORYLINE.md`; they paraphrase the conclusions chapter without new
numbers.

## 11. Keys in `data/thesis_tables.json`

`naive, loss, gen1_arch, gen1_backbone, hops_vector, alpha_vector, hops_vision, alpha_vision,
gnn, dedup, early_best, early_grid, late, vector_vs_vision, test_BP, test_CC, test_MF, cost,
isolated_vs_connected, degree_f1_BP, degree_f1_CC, degree_f1_MF, graph_gain_by_degree,
degree_correlation, coverage, corpus, label_space, graph_topology, multiplicity, hyperparams,
fusion_grid, fusion_selected, cost_runs, baselines_cost_coverage`

Each entry has `label` (the LaTeX label), `caption` and `rows` (header row first; numbers as
floats; empty first cells mean "same group as the row above").
