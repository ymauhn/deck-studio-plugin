"""Shell commands the "Autônomo" level runs without asking (pure; feedback of 2026-11-04: the author still got cards
for the deck's own build and QA, and for plain reads).

A command passes when every part of it (split at && || ; |) is one of:
- a read-only command (ls, cat, grep, diff, sed -n, find without -exec or -delete, git status/diff/log/show, the
  PowerShell Get-* cmdlets...), reading any folder: the Read tool may read outside the kit at this level too;
- a known local command of the deck: an interpreter (python, py, node) with plain flags and one of the kit's own
  scripts (config "localScripts", which the write guard protects), resolved from the current folder;
- a TeX tool (pdflatex, xelatex, bibtex, biber, or latexmk with -norc), without shell escape;
- cd to any folder.
Anything else asks: a redirection into a file, a heredoc, a command substitution, python -c or -m, a network or
publishing word, a command not on these lists. Paths written the Git Bash way (/c/Users/...) are read as C:\\Users\\....
ponytail: a lexical check, not a sandbox; it errs toward asking."""
import ntpath
import re
import shlex

READ_ONLY = {"ls", "dir", "cat", "head", "tail", "grep", "egrep", "fgrep", "rg", "diff", "cmp", "wc", "file", "echo",
             "pwd", "sort", "uniq", "cut", "tr", "stat", "du", "tree", "which", "where", "type", "true", "basename",
             "dirname", "realpath", "nl", "column", "test", "[",
             "get-content", "gc", "get-childitem", "gci", "get-item", "gi", "select-string", "sls", "test-path",
             "measure-object", "select-object", "where-object", "sort-object", "format-table", "format-list",
             "out-string", "write-output", "write-host", "resolve-path", "get-location", "set-location", "pushd",
             "popd", "cd", "sl"}
GIT_READ = {"status", "diff", "log", "show", "ls-files", "rev-parse", "blame", "branch"}
TEX = {"pdflatex", "xelatex", "lualatex", "bibtex", "biber", "latexmk", "makeindex"}
INTERPRETERS = {"python", "python3", "py", "node"}
PLAIN_FLAGS = {"-I", "-u", "-B", "-E", "-s", "-S", "-3", "-X"}  # -X takes a value (utf8)
EXTERNAL = re.compile(r"publish|netlify|deploy|vercel|https?://|\bcurl\b|\bwget\b|invoke-(webrequest|restmethod)|"
                      r"\b(iwr|irm)\b|\bssh\b|\bscp\b|\bs?ftp\b|\bgit\s+(push|remote|fetch|pull|clone)\b|\bgh\b|"
                      r"\bnpm\s+(publish|login|install|i)\b|\bnpx\b|\bpip\s+install\b|start-process", re.I)
OPERATORS = {"&&", "||", ";", "|", "&", "\n"}


def _win(path):
    """A path as Windows reads it: /c/Users/x is C:\\Users\\x."""
    m = re.match(r"^/([a-zA-Z])(/.*)?$", path)
    return f"{m[1].upper()}:{(m[2] or '/')}" if m else path


def _inside(root, path):
    r, p = ntpath.normcase(ntpath.normpath(root)), ntpath.normcase(ntpath.normpath(path))
    return p == r or p.startswith(r.rstrip("\\") + "\\")


def _tokens(command):
    lexer = shlex.shlex(command.replace("\r", ""), posix=True, punctuation_chars=";&|<>()")
    lexer.whitespace = " \t"  # a newline stays a separator of its own
    lexer.wordchars += "\\:.-/~*?[]{}=+,%@#$!^"
    out = []
    for tok in lexer:
        out.extend(["\n"] if tok == "\n" else [tok])
    return out


def _segments(tokens):
    seg = []
    for t in tokens:
        if t in OPERATORS or set(t) <= {"\n"}:
            if seg:
                yield seg
            seg = []
        else:
            seg.append(t)
    if seg:
        yield seg


def _name(word):
    w = word.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return w[:-4] if w.endswith(".exe") else w


def local_command(command, kit_root, local_scripts, read_only=False, readable=()):
    """(True, why) when the command passes at the Autônomo level, else (False, why). With read_only (the default
    level, "Editar o deck"), only read-only commands pass, and every path they name, or cd to, must be inside the kit
    or one of the `readable` folders."""
    if not isinstance(command, str) or not command.strip():
        return False, "comando vazio"
    if EXTERNAL.search(command):
        return False, "ação externa (rede ou publicação)"
    if "$(" in command or "`" in command:
        return False, "substituição de comando"
    try:
        tokens = _tokens(command)
    except ValueError:  # an open quote, a heredoc body
        return False, "o comando não pôde ser lido com segurança"
    scripts = {ntpath.normcase(ntpath.normpath(ntpath.join(kit_root, s))) for s in local_scripts}
    cwd = kit_root
    for seg in _segments(tokens):
        # redirections: only into nothing (2>&1, >/dev/null, > nul)
        for i, t in enumerate(seg):
            if t in ("<<", "<<<"):
                return False, "heredoc"
            if t in (">", ">>", ">|", ">&"):
                target = seg[i + 1] if i + 1 < len(seg) else ""
                if not (target in ("/dev/null", "nul", "NUL", "$null") or (t == ">&" or target.startswith("&"))
                        or (t == ">" and target == "&" and i + 2 < len(seg) and seg[i + 2] in ("1", "2"))):
                    return False, "redirecionamento para um arquivo"
        words = [w for w in seg if w not in (">", ">>", "&", "<", "(", ")") and not re.fullmatch(r"\d", w)]
        while words and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=\S*", words[0]):  # NX_PT=1 python ...
            words = words[1:]
        if not words:
            continue
        cmd = _name(words[0])
        args = words[1:]
        if cmd in ("cd", "set-location", "sl", "pushd") and args:
            cwd = ntpath.normpath(ntpath.join(cwd, _win(args[0])))
            if read_only and not any(_inside(r, cwd) for r in (kit_root, *readable)):
                return False, "leitura fora do deck"
            continue
        if read_only:
            if cmd in INTERPRETERS or cmd in TEX:
                return False, f"{cmd} roda código: só no Autônomo"
            for a in args:  # every path a read names, from the current folder
                if a.startswith("-") or not re.search(r"[\\/]|^\.\.?$|\.\w+$", a):
                    continue
                path = ntpath.normpath(ntpath.join(cwd, _win(a)))
                if not any(_inside(r, path) for r in (kit_root, *readable)):
                    return False, "leitura fora do deck"
        if cmd == "git":
            if not args or args[0] not in GIT_READ:
                return False, f"git {args[0] if args else ''}"
            continue
        if cmd == "find" and any(a in ("-exec", "-execdir", "-delete", "-ok", "-fprint", "-fls", "-fprintf")
                                 for a in args):
            return False, "find que executa ou apaga"
        if cmd == "sed" and any(a.startswith("-i") or a == "--in-place" or re.search(r"(^|;)\s*w\s", a)
                                for a in args):
            return False, "sed que grava"
        if cmd in READ_ONLY or cmd in ("find", "sed"):
            continue
        if cmd in TEX:
            if any("shell-escape" in a or "write18" in a for a in args):
                return False, "TeX com shell escape"
            if cmd == "latexmk" and "-norc" not in args:
                return False, "latexmk sem -norc (rodaria o latexmkrc da pasta)"
            continue
        if cmd in INTERPRETERS:
            rest, i = args, 0
            while i < len(rest) and rest[i].startswith("-"):
                if rest[i] not in PLAIN_FLAGS:
                    return False, f"{cmd} {rest[i]}"
                i += 2 if rest[i] == "-X" else 1
            if i >= len(rest):
                return False, f"{cmd} sem script"
            script = ntpath.normcase(ntpath.normpath(ntpath.join(cwd, _win(rest[i]))))
            if script not in scripts or not _inside(kit_root, script):
                return False, f"script que não é do deck: {rest[i]}"
            continue
        return False, f"comando fora da lista: {words[0]}"
    return True, "comando local do deck"
