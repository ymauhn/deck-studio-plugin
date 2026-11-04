# Kickoff prompt

Paste everything below the line into Claude Code, opened in this folder.

---

You are building the defense presentation of my Master's dissertation, NEXUS-GO, from start to
finish, without stopping to ask me unless you are truly blocked. I want two versions of the
same talk, an interactive single-file HTML deck and a LaTeX Beamer deck, plus GIF exports of
the animations. Talk to me in Portuguese; the slides are in English.

Everything you need is specified in this folder. `CLAUDE.md` lists the documents. Read all of
`docs/` before writing code, in this order: `CONTEXT.md`, `STORYLINE.md`, `FACTS.md`,
`FIGURES.md`, `DESIGN.md`, `INTERACTIVES.md`, `BUILD.md`, `QA.md`, `SKILLS.md`. The storyline
was written by someone who read the whole dissertation, but the dissertation is the source of
truth: you must also read it yourself.

## Goal

A 45-slide talk (plus backup slides) that tells the story of the whole dissertation for a
30 to 60 minute defense: motivation, background, data, method, results and conclusions. It
must be technically complete and faithful to the text, didactic, visually polished, and
interactive in the sense that items appear step by step. Use every figure of the dissertation
(26 including two TikZ figures), and add the new animations, flow diagrams and interactive
demos specified in `INTERACTIVES.md`, which should be clearer and more visual than the thesis
figures. Keep text short: bullets on the slides, the narrative in the speaker notes.

## Phases

Work through these phases in order. Keep a todo list with one item per slide and per
component. After each phase, write a short status line to `DECISIONS.md`.

**Phase 0. Setup.** Check Node, npm, Python, Playwright (with Chromium), Git, a TeX
distribution (pdflatex/xelatex) and ffmpeg. Install what is missing after asking me once for
all of it together. Install the skills listed in `docs/SKILLS.md` if they are not available
(or ask me to run the three `/plugin` commands). Load `frontend-design`, `webapp-testing` and
`pdf`.

**Phase 1. Sources.** Locate the newest dissertation (see `docs/CONTEXT.md` §2; search the
machine for anything newer than the `ultimo_ajuste` zip). Copy and unzip it into
`source/thesis/`. Clone the repository https://github.com/ymauhn/nexus-go (public) into
`source/nexus-go/` (read-only; pull the latest only if the clone has no local changes).
Regenerate `data/thesis_tables.json` and `data/numbering.json` with the scripts in `tools/`,
diff them against the shipped copies, and update `docs/FACTS.md` and `docs/STORYLINE.md` for
any change. Compare the repository's consolidated results and
`resultados_novos_pos_CC_update` with the dissertation tables as described in `docs/QA.md`
§1, and write the findings to `qa/REPORT.md`. Do not change what the deck shows because of
the repository; report disagreements to me.

**Phase 2. Read.** Read `dissertation.tex` in full (all chapters and both appendices) and look
at every figure. Then re-read `docs/STORYLINE.md` and fix anything that no longer matches the
text, logging each change.

**Phase 3. Engine and design system.** Build the deck engine and the token stylesheet from
`docs/BUILD.md` §3 and `docs/DESIGN.md`, with three placeholder slides (one per template),
fragments, notes, overview, themes and the `window.deck` test API. Write the Playwright smoke
test and make it pass before going on.

**Phase 4. Slides.** Build S01 to S45 and the backup slides in order, with the dissertation
figures processed as in `docs/FIGURES.md` (including the Figure 5.6 crop). Pre-render all math.
Write speaker notes for every slide.

**Phase 5. Components.** Build every component of `docs/INTERACTIVES.md` with the shared
interface. INT-PIPE and INT-PROP are the centrepieces; give them the most care. You may use
subagents to build independent components in parallel once the engine exists. Test each
component with Playwright as soon as it exists.

**Phase 6. QA.** Run the full suite of `docs/QA.md` (deck tests, number audit, visual review
of the contact sheets in both themes, phone width, reduced motion, offline). Fix and re-run
until it is green. Then review the contact sheets yourself and polish anything that reads
poorly from the back of a room.

**Phase 7. Beamer.** Build the Beamer version (`docs/BUILD.md` §4): same storyline, overlays
for the step-by-step reveals, static renders of the new diagrams (vector PDF where possible),
speaker notes. Compile locally if TeX is available; always also produce the Overleaf zip.

**Phase 8. GIFs.** Export the animations listed in `docs/BUILD.md` §5.

**Phase 9. Report.** Finish `qa/REPORT.md` and give me a final message in Portuguese with:
where each deliverable is; how to present (keys, presenter notes, deep links); the
30-minute cut; the fact-audit and repository findings; the inconsistencies found in the
dissertation (start with Figure 5.6); every decision I should review. Mention that I can bring
the HTML back to Cowork to publish it as a claude.ai artifact.

## Quality bar

- Faithful: every number traceable to the dissertation; no invented statistics.
- Didactic: one idea per slide; the new diagrams make the method obvious to someone who has
  not read the thesis; the interactive propagation demo shows α, T, the binomial hop weights
  and the α<sup>T</sup> shrinkage of isolated proteins.
- Polished: the design system in `docs/DESIGN.md`, consistent alignment, readable from the
  back of a room, correct in light and dark themes, no overflow, no overlapping text.
- Robust: works offline from a single file, with a projector clicker (PageUp/PageDown), and
  with reduced motion.

Start with Phase 0 now.
