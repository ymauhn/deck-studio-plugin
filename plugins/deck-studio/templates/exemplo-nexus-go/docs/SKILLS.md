# SKILLS: what to install and when to use it

Install from Anthropic's public skills marketplace inside Claude Code (the user runs these
once, or you ask the user to run them if you cannot):

```
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
/plugin install document-skills@anthropic-agent-skills
```

`example-skills` bundles: algorithmic-art, brand-guidelines, canvas-design, doc-coauthoring,
frontend-design, internal-comms, mcp-builder, skill-creator, slack-gif-creator, theme-factory,
web-artifacts-builder, webapp-testing. `document-skills` bundles: docx, pdf, pptx, xlsx.

## Use these

| Skill | Use it for | How |
|---|---|---|
| `frontend-design` | Design execution of the HTML deck | Load before writing the stylesheet and the slide templates. `DESIGN.md` already fixes palette, type and layout; use the skill to execute them well (spacing, hierarchy, motion restraint) and to catch generic-looking choices. If it conflicts with `DESIGN.md`, `DESIGN.md` wins. |
| `webapp-testing` | All Playwright testing | Python Playwright, sync API, headless Chromium. The deck is a static file, so no server: open `file://…/nexus-go-defense.html`. Follow its "reconnaissance then action" pattern for the interactive slides. Use its console-logging example to capture errors. |
| `pdf` | Reading the dissertation PDF and checking the Beamer PDF | Extract text from the compiled dissertation PDF to cross-check figure/table numbers; extract text from the Beamer PDF for the number audit. |
| `slack-gif-creator` | GIF export helpers | Reuse its `GIFBuilder` (frame assembly, optimization) and easing helpers. Ignore its Slack limits (128 px / 480 px, 3 s): our GIFs are up to 1200 px wide and several seconds long. |

## Optional

| Skill | When |
|---|---|
| `pptx` | Only if the user later asks for a PowerPoint version. Not part of this task. |
| `theme-factory` | Only to show the user one or two alternative colour themes after the main deck is done. Do not replace the semantic palette of `DESIGN.md`. |
| `canvas-design` / `algorithmic-art` | Only if the title hero (INT-HERO) needs more craft. Keep it subtle. |

## Do not use for this task

- `web-artifacts-builder`: it scaffolds React + Tailwind + shadcn and bundles with Parcel.
  The deck is a hand-written single file with a small engine; the extra stack adds size and
  complexity with no benefit here.
- `docx`, `xlsx`, `mcp-builder`, `internal-comms`, `brand-guidelines`, `doc-coauthoring`,
  `skill-creator`: not relevant.

## Claude Code features worth using

- **Plan mode** for Phase 0–1 (read, verify, plan), then normal mode to build.
- **Subagents** (the Task tool) once the engine and tokens exist: build independent
  components in parallel (e.g. one subagent for INT-PROP, one for INT-PIPE, one for the charts,
  one for the Beamer file). Give each subagent the relevant doc sections and the component
  interface from `INTERACTIVES.md`, and integrate their outputs yourself.
- **A todo list** with one item per slide and per component, so progress is visible.
- **Permissions**: ask the user once for the commands you need (node, npm, python, pip,
  playwright, git, pdflatex/xelatex, ffmpeg) instead of interrupting repeatedly.

## Tools to install if missing (ask once, then install)

- Node.js 20+ and npm (`mathjax-full`, optional `sharp` for images).
- Python 3.11+ with `playwright` (`pip install playwright` then `python -m playwright install
  chromium`), `pillow`, `imageio`, `numpy`, `fonttools[woff]` (for font subsetting).
- Git (to clone `github.com/ymauhn/nexus-go`).
- A TeX distribution for Beamer: MiKTeX or TeX Live on Windows. If the user prefers not to
  install one, deliver the Overleaf zip instead.
- ffmpeg (optional, for MP4 exports).
