"""Write guard (pure): classify an agent tool call as allow, deny or ask."""
import fnmatch
import ntpath
import os
import re
import sys
from dataclasses import dataclass, field

from deck_studio.core.shell_policy import local_command

# the tools that write a file, with the input key that names it
WRITE_TOOLS = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path", "NotebookEdit": "notebook_path"}
SHELL_TOOLS = ("Bash", "PowerShell")
# the autonomy levels of the chat switch: perguntar sempre, editar o deck sem perguntar (the default), autônomo
LEVELS = ("ask", "deck", "auto")
DEFAULT_LEVEL = "deck"


@dataclass
class Decision:
    behavior: str  # allow, ask or deny
    reason: str
    paths: list = field(default_factory=list)


def _covers(rel, pattern):
    """'dir/**' covers dir and everything under it; a pattern with '*' is a glob whose '*' crosses folders
    ('deck/src/*.js' covers deck/src/components/a.js); anything else is an exact kit-relative file."""
    p = pattern.lower()
    if p.endswith("/**"):
        return rel == p[:-3] or rel.startswith(p[:-2])
    return fnmatch.fnmatchcase(rel, p) if "*" in p else rel == p


def _inside(folder, p):
    """p relative to folder (lowercase, forward slashes), or None when p is not inside it.
    Compares case-insensitively and only on whole segments, as Windows does."""
    fs, ps = folder.rstrip("\\").split("\\"), p.split("\\")
    if [s.lower() for s in ps[:len(fs)]] != [s.lower() for s in fs]:
        return None
    # Win32 trims trailing dots (and spaces) from names: data.\x is data\x
    return "/".join(re.sub(r"[. ]+$", "", s) for s in ps[len(fs):]).lower()


def _norm(base, p):
    """Absolute path with '..' resolved; relative paths resolve against base. The long-path prefix
    is stripped from drive and UNC paths only (//?/C:/x is C:/x, //?/UNC/srv/x is //srv/x): other
    device paths (//?/GLOBALROOT/..., //./pipe/...) stay absolute, hence outside every folder."""
    p = re.sub(r"^[\\/]{2}[?.][\\/](?=[a-z]:[\\/])", "", p, flags=re.I)
    p = re.sub(r"^[\\/]{2}[?.][\\/]UNC[\\/]", r"\\\\", p, flags=re.I)
    p = ntpath.normpath(ntpath.join(base, p))
    # a Windows short name (C:\\Users\\RUNNER~1) is the same folder as its long form, which the kit root has
    return os.path.realpath(p) if sys.platform == "win32" and "~" in p else p


def _bad():
    return Decision("deny", "Caminho ausente ou inválido.")


class Guard:
    def __init__(self, config):
        # kit_root or kitRoot (config.py spells the keys as the Node adapter does): both read as kitroot
        c = {k.replace("_", "").lower(): v for k, v in config.items()}
        self.root = _norm(os.getcwd(), c["kitroot"])
        self.allow_write = c.get("allowwrite", [])
        self.deny_write = c.get("denywrite", [])
        self.ask_write = c.get("askwrite", [])
        self.ask_dirs = [_norm(os.getcwd(), d) for d in c.get("askwritedirs", [])]
        self.readable = [self.root, *(_norm(os.getcwd(), d) for d in c.get("readdirs", []))]
        self.local_scripts = c.get("localscripts", [])  # the deck's own scripts, which Autônomo runs

    def check(self, tool_name, tool_input, level=None):
        """The decision on one tool call. `level` is the chat's autonomy level (LEVELS; any other value is the
        default); None gives the base rules alone."""
        # tool input comes from the model: a missing or odd path is denied, never thrown on
        tool_input = tool_input if isinstance(tool_input, dict) else {}
        d = self._check(tool_name, tool_input, level)
        if level is None or d.behavior != "ask" and not (level == "ask" and tool_name in WRITE_TOOLS):
            return d
        level = level if level in LEVELS else DEFAULT_LEVEL
        if level == "ask" and tool_name in WRITE_TOOLS and d.behavior == "allow":
            return Decision("ask", "Modo perguntar sempre: toda escrita precisa da sua aprovação.", d.paths)
        if level == "deck" and tool_name in SHELL_TOOLS and d.behavior == "ask":
            # reading the deck from the terminal (ls, cat, grep, find...) is like the Read tool there (04/11)
            ok, _ = local_command(tool_input.get("command"), self.root, self.local_scripts, read_only=True,
                                  readable=self.readable[1:])
            if ok:
                return Decision("allow", "Editar o deck: leitura no deck pelo terminal.")
        if level != "auto" or d.behavior != "ask":
            return d
        if tool_name in ("Read", "Grep", "Glob"):  # reading only; the web asks at every level (it goes out)
            return Decision("allow", "Modo autônomo: leitura liberada.", d.paths)
        if tool_name in SHELL_TOOLS:
            ok, why = local_command(tool_input.get("command"), self.root, self.local_scripts)
            if ok:
                return Decision("allow", "Modo autônomo: comando local do deck.")
            return Decision("ask", f"Comando de terminal ({why}): precisa da sua aprovação.")
        return d

    def _check(self, tool_name, tool_input, level):
        if tool_name in WRITE_TOOLS:
            return self._write(self._write_target(tool_name, tool_input), level)
        if tool_name == "Read":
            return self._read(self._target(tool_input.get("file_path")))
        if tool_name in ("Grep", "Glob"):
            path = tool_input.get("path")
            base = self._read(self._target(self.root if path in (None, "", 0) else path))  # JS `path || root`
            pattern = tool_input.get("pattern")
            # the Glob tool honors an absolute pattern even when path points elsewhere; this check is
            # lexical (ponytail: a '**/..' inside a pattern is not expanded)
            if tool_name == "Glob" and isinstance(pattern, str) and base.behavior == "allow":
                reach = self._read(_norm(base.paths[0], pattern))
                if reach.behavior != "allow":
                    return Decision(reach.behavior, reach.reason, base.paths)
            return base
        if tool_name in SHELL_TOOLS:
            return Decision("ask", "Comando de terminal: precisa da sua aprovação. O desfazer não cobre o que ele mudar.")
        if tool_name in ("WebFetch", "WebSearch"):
            return Decision("ask", "Acesso à web: precisa da sua aprovação.")
        if tool_name in ("Task", "Agent"):
            return Decision("deny", "Subagentes não são permitidos: o desfazer não cobriria as edições deles.")
        if tool_name.startswith("mcp__deck__") or tool_name in ("Skill", "TodoWrite", "ToolSearch"):
            return Decision("allow", "Ferramenta do estúdio.")
        return Decision("ask", "Ferramenta desconhecida: precisa da sua aprovação.")

    def _write_target(self, tool_name, tool_input):
        """The file a write tool call targets, normalized as the rules compare it; None for other tools or no path."""
        key = WRITE_TOOLS.get(tool_name)
        return self._target(tool_input.get(key)) if key and isinstance(tool_input, dict) else None

    def write_path(self, tool_name, tool_input):
        """The file a write tool call targets, as this system opens it; None for other tools or a missing path."""
        target = self._write_target(tool_name, tool_input)
        # the rules compare Windows-style strings; the path a caller opens is the system's own (\tmp\x is /tmp/x)
        return target if target is None or sys.platform == "win32" else target.replace("\\", "/")

    def _target(self, p):
        return _norm(self.root, p) if isinstance(p, str) and p else None

    def _read(self, target):
        if target is None:
            return _bad()
        if any(_inside(d, target) is not None for d in self.readable):
            return Decision("allow", "Leitura liberada.", [target])
        return Decision("ask", "Leitura fora do deck: precisa da sua aprovação.", [target])

    def _write(self, target, level=None):
        if target is None:
            return _bad()
        rel = _inside(self.root, target)
        # an NTFS stream (engine.js::$DATA is engine.js) or a short 8.3 name (SHELL~1.HTM can be shell.html) names a
        # file under another spelling, which the exact names and globs below would miss
        if rel is not None and re.search(r":|~\d", rel):
            return Decision("deny", "Use o nome comum do arquivo, sem fluxo NTFS (:) nem nome curto (~1).", [target])
        denied = next((p for p in self.deny_write if rel is not None and _covers(rel, p)), None)
        if denied:
            return Decision("deny", f"Escrita bloqueada: {denied} é protegido.", [target])
        if any(_inside(d, target) is not None for d in self.ask_dirs):
            return Decision("ask", "Escrita fora do deck, numa pasta que pede a sua aprovação.", [target])
        if rel is None:
            return Decision("deny", "Escrita fora do deck não é permitida.", [target])
        if any(_covers(rel, p) for p in self.ask_write):
            return Decision("ask", "Escrita num script do deck: o estúdio roda este código. Precisa da sua aprovação.",
                            [target])
        if any(_covers(rel, p) for p in self.allow_write):
            return Decision("allow", "Escrita na área liberada do deck.", [target])
        if level is not None and level != "ask":  # deck and auto: any unprotected kit file
            return Decision("allow", "Escrita no deck, liberada pelo nível de autonomia.", [target])
        return Decision("ask", "Escrita no deck fora da área liberada: precisa da sua aprovação.", [target])


create_guard = Guard  # the contract's name (docs/PYTHON.md)
