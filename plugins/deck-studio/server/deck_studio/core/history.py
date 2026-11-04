"""History: per-turn snapshots of the files a turn wrote, for diff and undo."""
import base64
import difflib
import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import quote


@dataclass
class Turn:
    id: str
    meta: dict | None
    files: list  # kit-relative paths
    ended: bool
    undone: bool


@dataclass
class UndoResult:
    ok: bool
    restored: list = field(default_factory=list)
    removed: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)


def _snap(p):
    """A file's exact bytes as base64, or None when the file does not exist."""
    try:
        return base64.b64encode(Path(p).read_bytes()).decode("ascii")
    except FileNotFoundError:
        return None


def _load(p):
    """A stored turn, or None for a damaged record (say, a crash mid-write): it is skipped and left
    on disk, so startup never fails on it."""
    try:
        return json.loads(p.read_text("utf-8"))
    except (OSError, ValueError):
        return None


def _lines(data):
    """Lines split at LF only (a CR stays in its line); a last line without one is marked, as diff does."""
    lines = re.findall(r"[^\n]*\n|[^\n]+", data.decode("utf-8", "replace"))
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n\\ No newline at end of file\n"
    return lines


class History:
    def __init__(self, dir, kit_root):
        # one JSON file per turn, rewritten whenever the turn changes
        self.dir, self.kit_root = Path(dir), os.fspath(kit_root)
        self.dir.mkdir(parents=True, exist_ok=True)
        stored = sorted(filter(None, map(_load, self.dir.glob("*.json"))), key=lambda t: t["seq"])
        self.turns = {t["id"]: t for t in stored}  # in creation order
        self.seq = stored[-1]["seq"] if stored else 0

    def _save(self, t):
        (self.dir / f"{quote(t['id'], safe='')}.json").write_text(json.dumps(t), "utf-8")

    def begin(self, turn_id, meta=None):
        self.seq += 1
        self.turns[turn_id] = t = {"id": turn_id, "seq": self.seq, "meta": meta, "files": [], "ended": False, "undone": False}
        self._save(t)

    def get(self, turn_id):
        t = self.turns.get(turn_id)
        return self._summary(t) if t else None

    def list(self):
        return [self._summary(t) for t in self.turns.values()]

    def _summary(self, t):
        return Turn(t["id"], t["meta"], [self._rel(f["path"]) for f in t["files"]], t["ended"], t["undone"])

    def before_write(self, turn_id, path):
        """Only the first write to a file in a turn is snapshotted (paths compare as Windows does);
        the snapshot is on disk before the write happens."""
        t, p = self.turns[turn_id], os.path.abspath(os.path.join(self.kit_root, path))
        if any(f["path"].lower() == p.lower() for f in t["files"]):
            return
        t["files"].append({"path": p, "before": _snap(p)})
        self._save(t)

    snapshot = before_write  # the name docs/PYTHON.md uses for the PreToolUse hook

    def before_text(self, turn_id, path):
        """The text a file had before the turn's first write to it; None when unknown or the file was new."""
        t, p = self.turns.get(turn_id), os.path.abspath(os.path.join(self.kit_root, path))
        f = next((f for f in (t or {}).get("files", []) if f["path"].lower() == p.lower()), None)
        if not f or f["before"] is None:
            return None
        return base64.b64decode(f["before"]).decode("utf-8", "replace")

    def end(self, turn_id):
        t = self.turns[turn_id]
        for f in t["files"]:
            f["after"] = _snap(f["path"])
        t["ended"] = True
        self._save(t)

    def undo(self, turn_id):
        """All or nothing: every file must still hold what the turn left in it (a running turn conflicts)."""
        t = self.turns[turn_id]
        conflicts = [self._rel(f["path"]) for f in t["files"] if "after" not in f or _snap(f["path"]) != f["after"]]
        if conflicts:
            return UndoResult(ok=False, conflicts=conflicts)
        restored, removed = [], []
        # ponytail: a write error halfway (a locked file) leaves the earlier files restored, and a retry
        # reports them as conflicts; roll back on error if that ever shows up
        for f in t["files"]:
            if f["before"] == f["after"]:
                continue
            if f["before"] is None:
                Path(f["path"]).unlink(missing_ok=True)
                removed.append(self._rel(f["path"]))
            else:
                Path(f["path"]).write_bytes(base64.b64decode(f["before"]))
                restored.append(self._rel(f["path"]))
        t["undone"] = True
        self._save(t)
        return UndoResult(ok=True, restored=restored, removed=removed)

    def diff(self, turn_id):
        """One unified diff of the files the turn changed, named by kit-relative paths."""
        out = []
        for f in self.turns[turn_id]["files"]:
            before, after = f["before"], f.get("after")
            if before == after:
                continue
            name = self._rel(f["path"])
            a = "/dev/null" if before is None else f"a/{name}"
            b = "/dev/null" if after is None else f"b/{name}"
            old, new = base64.b64decode(before or ""), base64.b64decode(after or "")
            if b"\0" in old or b"\0" in new:  # a NUL byte marks a binary file, as in git
                out.append(f"Binary files {a} and {b} differ\n")
            else:
                out.extend(difflib.unified_diff(_lines(old), _lines(new), a, b, n=4))
        return "".join(out)

    def _rel(self, p):
        try:
            return os.path.relpath(p, self.kit_root).replace("\\", "/")
        except ValueError:  # another drive: the absolute path, as Node's path.relative gives
            return p.replace("\\", "/")


create_history = History  # the contract's name (docs/PYTHON.md)
