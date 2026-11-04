"""The write guard as a PreToolUse hook (hooks/hooks.json): in a Deck Studio project (a folder with a studio.json
above the file), Write and Edit follow the project's write rules (deck_studio.core.write_guard, the "Editar o deck"
level): the builds, the dist and studio.json are denied, the build script, the QA scripts, the judge's rubric and the
CLAUDE.md ask the author. Outside a project the hook says nothing. Reads the hook's JSON on stdin."""
import json
import sys
from pathlib import Path

# run as a script by the hook (no venv: the guard needs only the standard library), from the server folder's copy
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from deck_studio.config import load_config  # noqa: E402
from deck_studio.core.write_guard import create_guard  # noqa: E402


def project_of(file):
    for folder in Path(file).resolve().parents:
        if (folder / "studio.json").is_file():
            return folder
    return None


def decide(event):
    tool, args = event.get("tool_name", ""), event.get("tool_input") or {}
    file = args.get("file_path") or args.get("notebook_path")
    if not file:
        return None
    file = Path(event.get("cwd") or ".", file)
    project = project_of(file)
    if not project:
        return None
    d = create_guard(load_config(project)).check(tool, {**args, "file_path": str(file)}, "deck")
    if d.behavior == "allow":
        return None
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": d.behavior,
                                   "permissionDecisionReason": f"Deck Studio: {d.reason}"}}


def main():
    try:
        out = decide(json.loads(sys.stdin.read() or "{}"))
    except Exception as e:  # never block the session on a hook error: say it and let Claude Code ask
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                                      "permissionDecisionReason": f"Deck Studio: a guarda falhou ({e})"}}
    if out:
        print(json.dumps(out))  # ASCII: Claude Code reads UTF-8, a Windows console writes its code page


if __name__ == "__main__":
    main()
