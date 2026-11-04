# CONTEXT: the project, the files, the rules

## 1. What this is

Yeonatan Mauhnoom's Master's dissertation at the Institute of Computing, Unicamp:
**NEXUS-GO: Network-Extended Unified Sequence Embeddings for Gene Ontology Function
Annotation**. It predicts Gene Ontology terms for proteins by combining ProtT5 protein
language model embeddings with the STRING protein interaction network, on a CAFA5-derived
multi-species corpus, under a transductive node-classification protocol. The defense is
scheduled for November 16, 2026.

The task: a 40–45 slide presentation (built as 45 + backup slides) of the whole work, for a
30 to 60 minute defense talk, in English, as (1) an interactive single-file HTML deck and
(2) a LaTeX Beamer version, plus GIF exports of the animations.

The dissertation was written and revised over many rounds; it is final and must not be
edited by this task. Work only on copies.

## 2. Where the files are (user's Windows machine)

Paths contain accented characters and spaces; always quote them. In Git Bash the same paths

| What | Path | Notes |
|---|---|---|
| Thesis-writing pipeline (ignore) | `C:\multi-agentic-writer\` | Not needed for the deck. |
| **Code repository** | https://github.com/ymauhn/nexus-go | Public. Look for a local clone first (a folder named `nexus-go`, `NEXUS-GO` or the old name `propelg-go`, or any folder containing both `ppi_only/` and `ppi_v4/`). If none, `git clone` it into `source/nexus-go/`. |

First step of the job: search the machine for anything newer than the `ultimo_ajuste` zip
(a newer zip, an unzipped folder with a newer `dissertation.tex`, a newer PDF), because the
author may have kept editing. Use the newest one and say which in the report.

Repository layout (from Appendix A.8): `ppi_only/` first generation, `ppi_v4/` second
generation, `configs/`, `data/`, `raw/` (ProtT5 cache), `results/` (manifests, probabilities,
consolidated tables), `runs/`, `precomp/` (GNN embeddings), `docs/`. Pull the latest
(`git pull` on an existing clone only if it has no local changes; otherwise read it as is).

## 3. Rules from the author (always apply)

1. **Never modify or delete anything under `data/`** of the repository. Treat the whole
   repository as read-only: no commits, no pushes, no file changes.
2. Never edit the dissertation sources or PDFs. Work on copies inside this project folder.
3. The author does not use em-dashes in prose. Slide text and notes use none.
4. No meta-commentary on slides ("as shown in the source file", "this slide shows"). Slides
   read as the researcher's own material.
5. Numbers come from the dissertation, with its precision. Do not invent statistics (for
   example, global UniProt counts are not in the dissertation, so the "gap" visual is
   schematic and unlabelled).
6. Talk to the author in Brazilian Portuguese. The deck itself is in English.
7. Work autonomously until there is a complete version. Ask only when truly blocked (for
   example, a missing tool that needs his approval to install). Log every judgement call in
   `DECISIONS.md`.

## 4. Facts about the status of the work that are newer than the `.tex`

- Publications: the VISAPP 2026 paper is published. The extended and revised version
  (*Beyond Learnable Graphs: Fixed Multi-Hop PPI Diffusion of Sequence Embeddings for Robust
  Protein Function Prediction*, same four authors) was **accepted** in Communications in
  Computer and Information Science (CCIS), expected publication December 21, 2026. It covers
  only the fixed-propagation route, continuing the VISAPP method and adding an MLP head next
  to the vision head. The `.tex` may still say "submitted ... under review"; the deck uses the
  accepted status.
- The bibliography was revised in September 2026 (51 corrections, UniProt 2025 and Gene
  Ontology 2026 entries added). If a slide cites a reference, use the corrected entry.
- Defense date: November 16, 2026, as the author said on 2026-10-28. The `.tex` still has
  `\datadadefesa{05}{11}{2026}`; the deck uses November 16.

## 5. Known inconsistencies to handle (report them, do not fix the thesis)

1. Figure 5.6 (`cap5/fig_5_06_hybrid_pipeline.png`): its late-fusion box lists rules that do
   not exist in the text (average, geometric mean, validation-weighted). Crop it in the deck
   and report it (see `FIGURES.md`).
2. Coverage table naming: Table 6.28 says "This work (all routes)", Table B.3 says
   "NEXUS-GO (all routes)". The deck uses "NEXUS-GO (all routes)".
3. Figure 5.7 has text slightly overflowing its boxes ("layer 22 / 1024-d / per residue").
   Use as is; mention it in the report as cosmetic.

## 6. Glossary

- **First Generation**: network-only models (STRING profile → MLP/CNN/vision backbone);
  reported as a topology-only control, no route name.
- **ProtT5 baseline**: the fixed operator at T = 0 (graph switched off), vector head.
- **NEXUS-GO/Fixed**, **/GNN**, **/Early**, **/Late**: the four routes of the second generation.
- **Vector head**: MLP. **Vision head**: embedding reshaped into a 3 × 32 × 32 image for a CNN
  backbone.
- **wF<sub>max</sub>**: information-content weighted maximum F-measure, the selection metric.
- **pp**: percentage points. **Interpretability floor**: 0.5 pp, below which differences are
  read as ties (single seed).
