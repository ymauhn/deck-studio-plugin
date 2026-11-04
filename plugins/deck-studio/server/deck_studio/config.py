"""Deck adapter: the only place that knows the target deck (SPEC "Deep modules" 1).

Commands are argv lists run in the kit root, never shell strings."""
import asyncio
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from deck_studio.core import plataforma


# the kit's deck/tools/export_pdf.py, run on the Portuguese deck: it is loaded as is and its SRC is replaced
EXPORT_PT = ("import importlib.util as u; s = u.spec_from_file_location('export_pdf', 'deck/tools/export_pdf.py'); "
             "m = u.module_from_spec(s); s.loader.exec_module(m); "
             "m.SRC = (m.ROOT / 'deck' / 'dist' / 'nexus-go-defesa-pt.html').as_uri(); "
             "m.main(m.ROOT / 'deck' / 'dist' / 'nexus-go-defesa-pt.pdf')")


def nexus_go_config(kit):
    clean_build = ["node", "deck/build.mjs"]
    clean_pt = [*clean_build, "--pt"]
    publish = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "deck/tools/publish_netlify.ps1"]
    # publish_netlify.ps1 puts the Portuguese deck at /pt when deck/dist has one: with the tree in the kit, every
    # publish builds it fresh too, whatever language is on screen (an old /pt went up with EN on screen, 04/11)
    has_pt = (Path(kit) / "deck" / "src-pt" / "slides").is_dir()
    user_skills = str(Path.home() / ".claude" / "skills")
    return {
        "kitRoot": str(Path(kit).resolve()),
        "slidesDir": "deck/src/slides",
        "studioBuild": ["node", "deck/build.mjs", "--studio"],
        "studioOut": "deck/build/studio/nexus-go-defense.html",
        # the studio sections of one slide file: + its file name -> partOut/<file name>.json {part, css, slides}
        "partBuild": ["node", "deck/build.mjs", "--studio", "--part"],
        "partOut": "deck/build/studio/parts",
        "cleanBuild": clean_build,
        "contextDir": "context",
        "imagesDir": "deck/src/img",
        "fontsCss": "deck/build/fonts.css",
        # beamer/academico is the hand-written Beamer deck; its tables.tex is generated (gen_tables.py), and
        # latexmk runs a latexmkrc in the folder it compiles in as Perl
        "allowWrite": ["deck/src/**", "deck/src-pt/**", "context/**", ".claude/skills/**", "beamer/academico/**"],
        "denyWrite": ["source/**", "data/**", "beamer/slides.tex", "beamer/academico/tables.tex",
                      "beamer/academico/latexmkrc", "beamer/academico/.latexmkrc", "deck/dist/**", "deck/build/**",
                      "deck/node_modules/**"],
        # the studio deck runs only the scripts of the shell (CSP hashes from the studio build): the code they are built
        # from changes with the author's approval
        "askWrite": ["deck/src/*.js", "deck/src/*.mjs", "deck/src/*.cjs", "deck/src/shell.html",
                     "deck/src-pt/*.js", "deck/src-pt/*.mjs", "deck/src-pt/*.cjs", "deck/src-pt/shell.html",
                     # what the studio runs: the build, the job tools and their settings, the packages, and what
                     # Claude Code reads as instructions or settings (at every autonomy level; review of PR #3)
                     "deck/build.mjs", "deck/package.json", "deck/package-lock.json", "deck/tools/**", "tools/**",
                     "beamer/tools/**", "CLAUDE.md", "**/CLAUDE.md", "AGENTS.md", ".claude/settings.json",
                     ".claude/settings.local.json", "qa/*.py"],
        # the deck's own commands, which the Autônomo level runs without asking (core/shell_policy.py); each one is
        # protected above, so a script is never changed and run without the author
        "localScripts": ["deck/build.mjs", "qa/run_all.py", "qa/audit_numbers.py", "qa/shoot.py",
                         "qa/test_components.py", "qa/test_smoke.py", "deck/tools/export_pdf.py", "beamer/tools/build.py"],
        "askWriteDirs": [user_skills],
        "readDirs": [user_skills],
        # the Portuguese deck is a tree of its own, deck/src-pt (build.mjs --pt -> deck/dist/nexus-go-defesa-pt.html);
        # with PT on screen (features/language.py) these keys replace the base ones. The kit's export_pdf.py reads the
        # English file only, so the PT export runs it with its SRC pointed at the Portuguese one (no kit change)
        "languageTrees": {"pt": {
            "slidesDir": "deck/src-pt/slides",
            "imagesDir": "deck/src-pt/img",  # build.mjs --pt takes a slide's own images from deck/src-pt/img
            "studioBuild": ["node", "deck/build.mjs", "--studio", "--pt"],
            "partBuild": ["node", "deck/build.mjs", "--studio", "--pt", "--part"],
            "cleanBuild": clean_pt,
            "otherCleanBuilds": [clean_build],
            "jobs": {
                "export-pdf": [clean_pt, ["python", "-I", "-u", "-c", EXPORT_PT]],
                "publish": [clean_build, clean_pt, publish],  # the site has both decks: both are built fresh
            },
            "jobOutputs": {"export-pdf": "deck/dist/nexus-go-defesa-pt.pdf"},
        }},
        # -u: Python prints reach the job's live log as they happen, not when the tool exits
        "jobs": {
            "export-pdf": [clean_build, ["python", "-I", "-u", "deck/tools/export_pdf.py"]],
            "publish": [clean_build, clean_pt, publish] if has_pt else [clean_build, publish],
            "beamer": [["python", "-I", "-u", "-X", "utf8", "beamer/tools/build.py"]],
        },
        # the PDF each job writes; /api/jobs/files serves the PDFs in the export's folder
        "jobOutputs": {"export-pdf": "deck/dist/nexus-go-defense.pdf", "beamer": "beamer/nexus-go-defense.pdf"},
        "otherCleanBuilds": [clean_pt] if has_pt else [],  # they write deck/build too: they take the build lock
        "publishSite": "deck/tools/netlify-site.json",  # {url} of the site that publish updates, once it exists
        "publishPaths": ["/", "/pt"] if has_pt else ["/"],  # what Publicar updates, named in its confirmation
        # the project, as GET /api/status describes it to the UI
        "title": "NEXUS-GO",
        "format": "html",
        "startMode": "html",
        "beamerStart": None,
        "provenance": True,  # every number traces back to dissertation.tex or the number audit
        # the agent appendix's lines on the selection's kinds, what to edit, the deck's rules and where behavior goes
        # (agent/prompt.py), word for word
        "promptKinds": 'Kinds: "component" is a runtime-rendered diagram or chart: edit the component, not its runtime '
                       'DOM. "table" is\n  generated from the dissertation and read-only. "math" is a formula.',
        "promptPaths": "Edit only the deck sources, the context folder and the project skills. Never the dissertation "
                       "sources, data/, or\n  generated files (deck/dist, deck/build, beamer/slides.tex).",
        "promptRules": "Follow the deck's rules: every number comes from the dissertation or docs/FACTS.md; slide text "
                       "in English, short\n  bullets, no em dashes. New elements and slides use the deck's own grid, "
                       "classes and components.",
        "promptBehavior": "Behavior belongs in a component (deck/src/components), not in slide markup.",
    }


def generic_config(kit, fmt="html"):
    """A project made by Deck Studio from deck_studio/templates/project (docs/IMPORT.md "Config"), in the format the
    author chose (html | beamer); its studio.json (title, format, language, start mode) merges over this. Its tools
    run on the studio's own Python."""
    py = sys.executable
    clean_build = [py, "-I", "-X", "utf8", "deck/build.py"]
    user_skills = str(Path.home() / ".claude" / "skills")
    beamer = fmt == "beamer"
    return {
        "kitRoot": str(Path(kit).resolve()),
        "slidesDir": "deck/src/slides",
        "studioBuild": [*clean_build, "--studio"],
        "studioOut": "deck/build/studio/deck.html",
        "partBuild": None,  # no hot swap: an edit means a full build and a deck reload
        "cleanBuild": clean_build,
        "contextDir": "context",
        "imagesDir": "deck/src/img",
        "fontsCss": None,  # system font stacks: /ui/fonts.css is an empty stylesheet
        "allowWrite": ["deck/src/**", "context/**", ".claude/skills/**", "beamer/**"],
        # the * crosses folders: beamer/*latexmkrc covers any beamer/**/latexmkrc and .latexmkrc, which latexmk runs
        "denyWrite": ["studio.json", "deck/build/**", "deck/dist/**", "exports/**", "beamer/*latexmkrc"],
        # the shell's scripts run in the studio deck, and the studio runs the build and the job tools; Claude Code
        # reads a CLAUDE.md, or a .claude folder below the project's own, in any folder it works in as instructions
        "askWrite": ["deck/src/*.js", "deck/src/*.mjs", "deck/src/*.cjs", "deck/src/shell.html", "deck/build.py",
                     "deck/tools/**", "tools/**", "CLAUDE.md", "**/CLAUDE.md", "*/.claude/*", "qa/*.py",
                     # the judge checks the agent: its prompt and rubric change only with the author
                     ".claude/agents/**", "qa/RUBRICA.md"],
        "localScripts": ["deck/build.py", "deck/tools/export_pdf.py", "tools/overleaf_zip.py", "qa/check_deck.py",
                         "qa/audit_numbers.py", "qa/shoot.py"],
        "askWriteDirs": [user_skills],
        "readDirs": [user_skills],
        # the chosen format's outputs (the other format's folder is the template, untouched): the HTML deck's PDF, or
        # the Beamer deck's Overleaf zip, whose PDF the Beamer view opens (Abrir PDF)
        # (a Beamer deck goes to Overleaf by the Beamer bar's Exportar para o Overleaf, features/beamer.py)
        "jobs": ({} if beamer else
                 {"export-pdf": [clean_build, [py, "-I", "-u", "deck/tools/export_pdf.py"]]}),
        "jobOutputs": {"export-pdf": "deck/dist/deck.pdf"},
        "publishSite": None,
        "title": Path(kit).resolve().name,
        "format": "beamer" if beamer else "html",
        "language": "pt",  # or "en"
        "startMode": "beamer" if beamer else "html",  # unless studio.json names another
        "beamerStart": "beamer/apresentacao/apresentacao.tex",
        "provenance": False,
        # the agent appendix's own lines; the paths it may edit are named from the write rules above. The template's
        # build loads no components and no deck table comes from a dissertation
        "promptKinds": 'Kinds: "figure" is an image, "text" a box of text, "element" any other box: all of them are '
                       "the slide's own\n  HTML, which you edit.",
        "promptRules": "Follow the project's CLAUDE.md and the slide rules there. New elements and slides use the "
                       "deck's own grid and classes.",
        "promptBehavior": "This deck has no components: motion comes from the fragments its CLAUDE.md describes.",
    }


def with_publish(config):
    """A project with a registered Netlify site (deck/tools/netlify-site.json, written by "Cadastrar link de
    publicação") publishes like the NEXUS-GO kit: the clean build, then deck/tools/publish_netlify.py."""
    if config.get("format") == "html" and (Path(config["kitRoot"]) / "deck/tools/netlify-site.json").is_file():
        config["jobs"] = {**config["jobs"], "publish": [config["cleanBuild"],
                                                        [sys.executable, "-I", "-u", "deck/tools/publish_netlify.py"]]}
        config["publishSite"] = "deck/tools/netlify-site.json"
    return config


def merge(a, b):
    """Dicts merge key by key; lists and scalars in b replace a."""
    if isinstance(a, dict) and isinstance(b, dict):
        return {**a, **{k: merge(a.get(k), v) for k, v in b.items()}}
    return b


def load_config(kit, config_path=None):
    """A kit with a studio.json is a project made by Deck Studio; any other is the NEXUS-GO kit. --config goes on top."""
    own = Path(kit) / "studio.json"
    if own.is_file():
        project = json.loads(own.read_text(encoding="utf-8-sig"))
        config = with_publish(merge(generic_config(kit, project.get("format")), project))
    else:
        config = nexus_go_config(kit)
    if config_path:
        config = merge(config, json.loads(Path(config_path).read_text(encoding="utf-8")))
    return config


async def run_command(config, argv):
    """Run one command in the kit root; returns (exit code, stdout + stderr, ms). A missing program is code None."""
    t0 = time.perf_counter()
    try:
        proc = await asyncio.create_subprocess_exec(
            shutil.which(argv[0]) or argv[0], *argv[1:], cwd=config["kitRoot"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, creationflags=plataforma.NO_WINDOW)
        out, _ = await proc.communicate()
        code, output = proc.returncode, out.decode("utf-8", "replace")
    except OSError as e:
        code, output = None, str(e)
    return code, output, round((time.perf_counter() - t0) * 1000)
