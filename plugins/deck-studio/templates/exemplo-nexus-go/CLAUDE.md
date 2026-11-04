# NEXUS-GO defense deck: project memory

This folder builds the defense presentation of Yeonatan Mauhnoom's Master's dissertation,
*NEXUS-GO: Network-Extended Unified Sequence Embeddings for Gene Ontology Function
Annotation* (IC/Unicamp, defense on November 16, 2026).

The kickoff instructions are in `PROMPT.md`. The specification lives in `docs/`:

| File | Read it for |
|---|---|
| `docs/CONTEXT.md` | where the files are, the author's rules, known inconsistencies |
| `docs/STORYLINE.md` | the 45 slides, one by one (titles, text, visuals, reveal order, notes) |
| `docs/FACTS.md` | every number allowed on a slide, with its source |
| `docs/FIGURES.md` | the 26 dissertation figures and where each one goes |
| `docs/DESIGN.md` | palette, type, layout, motion, chart rules |
| `docs/INTERACTIVES.md` | specs of every new animation, diagram and chart |
| `docs/BUILD.md` | stack, engine, build pipeline, Beamer, GIFs |
| `docs/QA.md` | Playwright tests, number audit, definition of done |
| `docs/SKILLS.md` | skills to install and how to use them |
| `data/thesis_tables.json` | 34 tables parsed from `dissertation.tex` (regenerate first) |
| `tools/` | `extract_tables.py`, `numbering.py` |

## Rules that always apply

- The dissertation and the code repository are read-only. Never modify or delete anything
  under the repository's `data/` folder. No git commits or pushes.
- Every number on a slide must come from the newest `dissertation.tex` (or `FACTS.md` §1 for
  publication data). Charts read `data/thesis_tables.json`; never type chart numbers by hand.
- Slide text: English, short bullets, no em-dashes, no meta-commentary.
- Talk to the author in Brazilian Portuguese.
- Work autonomously until the definition of done in `docs/QA.md` is met. Log judgement calls in
  `DECISIONS.md`. Ask only when blocked.
- Windows paths contain accents and spaces; quote them.
