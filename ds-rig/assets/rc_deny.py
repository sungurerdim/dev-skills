#!/usr/bin/env python3
"""ds-rig RC-1..10 command classifier (shell-aware, stdlib only).

Parses the command like a shell would (quotes, escapes, $(...), `...`,
<(...), heredocs, pipelines, chains) and judges each simple command by its
real argv, so text inside quoted messages or heredoc data never triggers,
while code that actually runs (bash -c, eval, $(...), piped interpreters,
heredocs fed to a shell) is inspected recursively.

Modes:
  rc_deny.py "<command>"      exit 0 allow | 1 deny | 2 ask; "RC-n|reason" on stdout
  rc_deny.py --claude-hook    Claude Code PreToolUse adapter (JSON on stdin/stdout)

Honest limit: a guard rail against mistakes, not a sandbox. Scripts run by
path, interpreters' own code (python -c) and runtime-built strings are opaque.
"""
import json
import os
import posixpath
import re
import sys

WINDOWS = os.name == "nt"


def posix(p):
    """Git-Bash-style POSIX form of a host path (C:\\x -> /c/x) so one rule set covers every OS; no-op elsewhere."""
    if not WINDOWS:
        return p
    p = p.replace("\\", "/")
    m = re.match(r"^([A-Za-z]):(/|$)", p)
    return "/" + m.group(1).lower() + p[2:] if m else p


HOME = posix(os.path.expanduser("~"))
CWD = posix(os.getcwd())
USER_ROOTS = ("/Users", "/home", "/c/Users")  # macOS, Linux, Git-Bash-on-Windows parents of home dirs

SHELLS = {"sh", "bash", "zsh", "dash", "ksh", "fish", "ash"}
INTERP_RE = re.compile(r"^(python[0-9.]*|node|perl|ruby|php|deno|bun|osascript|powershell|pwsh)$")
FETCHERS = {"curl", "wget"}
NET_SINKS = {"curl", "wget", "nc", "ncat", "netcat", "socat", "ssh"}
ENV_DUMPS = {"env", "printenv", "set", "export"}
TEXT_SINKS = {"echo", "printf", "git", "gh", "grep", "rg", "ag", "sed", "awk", "jq",
              "sort", "head", "tail", "tee", "cat", "less", "wc", "tr", "cut", "say"}
DB_CLIENTS = {"psql", "mysql", "mariadb", "sqlite3", "duckdb", "clickhouse-client"}
READERS = {"cat", "less", "more", "head", "tail", "bat", "tac", "nl", "od", "xxd", "hexdump",
           "strings", "base64", "cp", "scp", "rsync", "grep", "rg", "awk", "sed", "sort",
           "open", "pbcopy", "tar", "zip", "gzip", "vim", "vi", "nano", "read"}
KEYWORDS = {"if", "then", "else", "elif", "do", "while", "until", "!", "time", "{", "}",
            "fi", "done", "esac", "(", ")"}
SYSTEM_DIRS = ("/etc", "/usr", "/bin", "/sbin", "/var", "/boot", "/opt", "/System",
               "/Library", "/private", "/Applications", "/lib", "/lib64", "/root", "/sys", "/proc",
               "/c/Windows", "/c/Program Files", "/c/Program Files (x86)", "/c/ProgramData")
SYSTEM_OK = ("/usr/local", "/opt/homebrew", "/private/tmp", "/private/var/folders", "/var/folders", "/tmp", "/var/tmp", "/run/user")
CRED = (".ssh", ".gnupg", ".aws", ".config/gcloud", ".kube", "Library/Keychains", ".netrc")
PROTECTED_HOME_DOTDIRS = {".ssh", ".gnupg", ".aws", ".kube", ".config", ".claude", ".codex",
                          ".gemini", ".copilot", ".local"}
HARNESS = (".claude/settings.json", ".claude/settings.local.json", ".claude/hooks", ".config/ds-rig")
PROFILES = (".zshrc", ".zprofile", ".zshenv", ".bashrc", ".bash_profile", ".profile")


class Hit(Exception):
    def __init__(self, rc, reason, ask=False):
        super().__init__(reason)
        self.rc, self.reason, self.ask = rc, reason, ask


# ---------------------------------------------------------------- lexer

class Word:
    __slots__ = ("v", "subs", "procsub", "quoted")

    def __init__(self):
        self.v, self.subs, self.procsub, self.quoted = "", [], [], False


class Cmd:
    def __init__(self):
        self.words, self.redirs, self.heredocs = [], [], []   # redirs: (op, Word)


def _capture(t, i, close):
    """t[i] is just after the opener; return (body, index after closer). Quote-aware."""
    depth, j, n = 1, i, len(t)
    while j < n:
        c = t[j]
        if c == "\\":
            j += 2
            continue
        if c == "'" and close == ")":
            k = t.find("'", j + 1)
            j = n if k < 0 else k + 1
            continue
        if c == '"' and close == ")":
            j += 1
            while j < n and t[j] != '"':
                j += 2 if t[j] == "\\" else 1
            j += 1
            continue
        if close == ")" and c == "(":
            depth += 1
        elif c == close:
            depth -= 1
            if depth == 0:
                return t[i:j], j + 1
        j += 1
    return t[i:], n


OPS = ("&&", "||", ";;", "|&", "&>>", "&>", "<<<", "<<-", "<<", ">>", ">|", "<&", ">&", "<>",
       ";", "&", "|", "<", ">", "(", ")", "\n")
REDIR = {"&>>", "&>", "<<<", "<<-", "<<", ">>", ">|", "<&", ">&", "<>", "<", ">"}


def lex(t):
    """Yield ('w', Word) | ('op', str) | ('hd', body_str, quoted_delim)."""
    i, n, out, pending = 0, len(t), [], []
    while i < n:
        c = t[i]
        if c in " \t":
            i += 1
            continue
        if c == "\\" and t[i + 1:i + 2] == "\n":
            i += 2
            continue
        if c == "#":
            k = t.find("\n", i)
            i = n if k < 0 else k
            continue
        op = next((o for o in OPS if t.startswith(o, i)), None)
        if op and not (op in ("<", ">") and t[i + 1:i + 2] == "("):
            i += len(op)
            out.append(("op", op))
            if op in ("<<", "<<-"):
                w, i = _word(t, i)
                while i < n and t[i] in " \t" and not w.v:
                    w, i = _word(t, i + 1)
                pending.append((w.v, op == "<<-", w.quoted))
                out.append(("w", w))
            if op == "\n" and pending:
                for delim, strip, quoted in pending:
                    lines = []
                    while i < n:
                        k = t.find("\n", i)
                        line = t[i:] if k < 0 else t[i:k]
                        i = n if k < 0 else k + 1
                        if (line.lstrip("\t") if strip else line) == delim:
                            break
                        lines.append(line)
                    out.append(("hd", "\n".join(lines), quoted))
                pending = []
            continue
        w, i = _word(t, i)
        if w.v or w.quoted or w.subs or w.procsub:   # empty = consumed fd prefix (2>&1)
            out.append(("w", w))
    return out


def _word(t, i):
    w, n = Word(), len(t)
    while i < n:
        c = t[i]
        if c in " \t\n;&|()":
            break
        if c in "<>":
            if t[i + 1:i + 2] == "(":
                body, i = _capture(t, i + 2, ")")
                w.procsub.append(body)
                w.v += "<(…)"
                continue
            if w.v.isdigit() and not w.quoted:   # fd prefix like 2>&1
                w.v = ""
            break
        if c == "\\":
            w.v += t[i + 1:i + 2]
            i += 2
        elif c == "'":
            k = t.find("'", i + 1)
            k = n if k < 0 else k
            w.v += t[i + 1:k]
            w.quoted, i = True, k + 1
        elif c == '"':
            w.quoted = True
            i += 1
            while i < n and t[i] != '"':
                if t[i] == "\\" and i + 1 < n:
                    w.v += t[i + 1]
                    i += 2
                elif t.startswith("$(", i) and not t.startswith("$((", i):
                    body, i = _capture(t, i + 2, ")")
                    w.subs.append(body)
                    w.v += "$(" + body + ")"
                elif t[i] == "`":
                    body, i = _capture(t, i + 1, "`")
                    w.subs.append(body)
                else:
                    w.v += t[i]
                    i += 1
            i += 1
        elif t.startswith("$((", i):
            body, i = _capture(t, i + 3, ")")
            i += 1
            w.v += "$((" + body + "))"
        elif t.startswith("$(", i):
            body, i = _capture(t, i + 2, ")")
            w.subs.append(body)
            w.v += "$(" + body + ")"
        elif c == "`":
            body, i = _capture(t, i + 1, "`")
            w.subs.append(body)
        else:
            w.v += c
            i += 1
    return w, i


def parse(t):
    """Return list of pipelines; a pipeline is a list of Cmd."""
    pipes, pipe, cmd = [], [], Cmd()
    toks, k = lex(t), 0

    def end_cmd():
        nonlocal cmd
        if cmd.words or cmd.redirs or cmd.heredocs:
            pipe.append(cmd)
        cmd = Cmd()

    last_hd_cmd = []
    while k < len(toks):
        tok = toks[k]
        if tok[0] == "w":
            cmd.words.append(tok[1])
        elif tok[0] == "hd":
            target = last_hd_cmd.pop(0) if last_hd_cmd else cmd
            target.heredocs.append((tok[1], tok[2]))
        else:
            op = tok[1]
            if op in REDIR:
                nxt = toks[k + 1] if k + 1 < len(toks) and toks[k + 1][0] == "w" else None
                if nxt:
                    k += 1
                    cmd.redirs.append((op, nxt[1]))
                    if op == "<<<":
                        cmd.heredocs.append((nxt[1].v, nxt[1].quoted))
                if op in ("<<", "<<-"):
                    last_hd_cmd.append(cmd)
            elif op in ("|", "|&"):
                end_cmd()
            else:
                end_cmd()
                if pipe:
                    pipes.append(pipe)
                pipe = []
        k += 1
    end_cmd()
    if pipe:
        pipes.append(pipe)
    return pipes


# ---------------------------------------------------------------- paths

def norm(p):
    p = posix(p)
    p = re.sub(r"^(\$\{HOME\}|\$HOME)(?=/|$)", "~", p)
    if p == "~" or p.startswith("~/"):
        p = HOME + p[1:]
    if not p.startswith("/"):
        p = posixpath.join(CWD, p)
    return posixpath.normpath(p)


def under(p, root):
    return p == root or p.startswith(root.rstrip("/") + "/")


def home_rel(p):
    return posixpath.relpath(p, HOME) if under(p, HOME) and p != HOME else None


def is_cred(p):
    r = home_rel(p)
    return bool(r) and not r.endswith(".pub") and any(under(r, c) for c in CRED)


def is_harness(p):
    r = home_rel(p)
    if r and any(under(r, h) for h in HARNESS):
        return True
    return bool(re.search(r"(^|/)\.claude/settings(\.local)?\.json$", p))


def is_system(p):
    return any(under(p, d) for d in SYSTEM_DIRS) and not any(under(p, o) for o in SYSTEM_OK)


def is_catastrophic(p):
    """Recursive delete here is unrecoverable: /, home, system, top-level home dirs."""
    raw = p.rstrip("*").rstrip("/") or "/"
    if raw in ("/", HOME, *USER_ROOTS) or (WINDOWS and re.fullmatch(r"/[a-z]", raw)) or posixpath.dirname(raw) in USER_ROOTS or is_system(raw) or is_cred(raw) or is_harness(raw):
        return True
    r = home_rel(raw)
    if r and "/" not in r:
        return not r.startswith(".") or r in PROTECTED_HOME_DOTDIRS
    return False


def write_class(p):
    """Protected-path class for a write target, or None."""
    if p.startswith("/dev/"):
        return ("RC-7", "redirect to /dev/tcp|udp (network socket)") if re.match(r"/dev/(tcp|udp)/", p) else None
    if is_harness(p):
        return ("RC-10", "write to harness permission/hook config")
    r = home_rel(p)
    if r and (r.startswith("Library/LaunchAgents") or r == ".ssh/authorized_keys"):
        return ("RC-8", "write to a persistence location")
    if is_cred(p):
        return ("RC-6", "write into a credential store")
    if under(p, "/etc") or under(p, "/private/etc") or under(p, "/Library/Launch"):
        return ("RC-8", "write to a system persistence file")
    if is_system(p):
        return ("RC-1", "write to a system path")
    return None


# ---------------------------------------------------------------- analysis

def base(w):
    b = posixpath.basename(posix(w)) if w else ""
    return b[:-4] if WINDOWS and b.lower().endswith(".exe") else b


def strip_wrappers(argv):
    while argv:
        b = base(argv[0])
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0]) or b in KEYWORDS:
            argv = argv[1:]
        elif b in ("sudo", "doas", "su", "pkexec", "run0"):
            raise Hit("RC-3", f"{b} (privilege escalation)")
        elif b == "env":
            argv = argv[1:]
            while argv and (argv[0].startswith("-") or "=" in argv[0]):
                argv = argv[2:] if argv[0] in ("-u", "-C", "-S") else argv[1:]
            if not argv:
                return ["env"]   # bare `env` dumps the environment
        elif b in ("nohup", "command", "builtin", "exec", "caffeinate", "stdbuf", "nice", "timeout", "xargs"):
            argv = argv[1:]
            takes = {"nice": {"-n"}, "xargs": {"-I", "-n", "-P", "-L", "-d", "-E", "-s", "-a"},
                     "timeout": {"-s", "-k"}}.get(b, set())
            while argv and argv[0].startswith("-"):
                argv = argv[2:] if argv[0] in takes else argv[1:]
            if b == "timeout" and argv:
                argv = argv[1:]
        elif b == "rtk":
            argv = argv[1:]
            if argv and argv[0] in ("run", "proxy"):
                argv = argv[1:]
            elif argv and argv[0] == "read":
                argv = ["cat"] + argv[1:]
        else:
            break
    return argv


def flags(args):
    short, long_, pos, end = set(), set(), [], False
    for a in args:
        if end or a == "-" or not a.startswith("-"):
            pos.append(a)
        elif a == "--":
            end = True
        elif a.startswith("--"):
            long_.add(a.split("=", 1)[0])
        else:
            short.update(a[1:])
    return short, long_, pos


def has_fetch(text):
    for pipe in parse(text):
        for c in pipe:
            try:
                argv = strip_wrappers([w.v for w in c.words])
            except Hit:
                continue
            if argv and base(argv[0]) in FETCHERS:
                return True
    return False


def check_cmd(cmd, depth):
    argv = strip_wrappers([w.v for w in cmd.words])
    words = cmd.words[len(cmd.words) - len(argv):]
    for op, w in cmd.redirs:
        if op in (">", ">>", ">|", "&>", "&>>", "<>"):
            wc = write_class(norm(w.v))
            if wc:
                raise Hit(*wc)
            if base(w.v) in PROFILES and home_rel(norm(w.v)):
                raise Hit("RC-8", "write to a shell profile", ask=True)
        if op == "<" and is_cred(norm(w.v)):
            raise Hit("RC-6", "reading a credential file")
        if op in (">&", "<&") and re.match(r"/dev/(tcp|udp)/", w.v):
            raise Hit("RC-7", "redirect to /dev/tcp (reverse-shell pattern)")
    if not argv:
        return
    b, args = base(argv[0]), argv[1:]
    s, l, pos = flags(args)
    lower = " ".join(args).lower()

    if "--dangerously-skip-permissions" in args or "--allow-dangerously-skip-permissions" in args \
            or ("--permission-mode" in args and "bypassPermissions" in args) \
            or "--permission-mode=bypassPermissions" in args:
        raise Hit("RC-10", "flag that disables the permission system")

    # code that runs: sh -c STR, eval, source, heredoc/herestring into a shell
    if b in SHELLS or b in ("eval", "source", "."):
        code = []
        if b in ("eval",):
            code.append(" ".join(args))
        elif b in SHELLS:
            for i, a in enumerate(args):
                if re.match(r"^-[a-z]*c[a-z]*$", a) and i + 1 < len(args):
                    code.append(args[i + 1])
                    break
            if not pos or "s" in s:
                code += [h for h, _ in cmd.heredocs]
        for w in words[1:]:
            for sub in w.subs + w.procsub:
                if has_fetch(sub):
                    raise Hit("RC-4", f"{b} executing fetched remote code")
        for c in code:
            check_text(c, depth + 1)

    if b == "rm":
        rec = bool(s & {"r", "R"}) or "--recursive" in l
        for p in pos:
            np = norm(p)
            if is_harness(np):
                raise Hit("RC-10", f"rm on harness config ({p})")
            if is_cred(np):
                raise Hit("RC-1", f"rm on credential store ({p})")
            if rec and is_catastrophic(np):
                raise Hit("RC-1", f"recursive rm on {p}")
    elif b == "shred":
        raise Hit("RC-1", "shred (irreversible overwrite)")
    elif b == "find" and ("-delete" in args or ("-exec" in args and "rm" in args)):
        roots = args[:next((i for i, a in enumerate(args) if a.startswith("-")), len(args))]
        if any(is_catastrophic(norm(r)) for r in roots):
            raise Hit("RC-1", "find … -delete over a root/home/system tree")
    elif b == "truncate" and any(is_system(norm(p)) for p in pos):
        raise Hit("RC-1", "truncate on a system path")

    elif b == "dd" and any(re.match(r"^of=/dev/(?!null$|stdout$|stderr$)", a) for a in args):
        raise Hit("RC-2", "dd writing to a raw device")
    elif re.match(r"^mkfs(\..+)?$", b) or b in ("fdisk", "gdisk", "sfdisk", "parted", "newfs_apfs", "newfs_hfs"):
        raise Hit("RC-2", f"{b} (disk format/partition)")
    elif b == "diskutil" and args and re.match(r"(?i)^(erase|zero|random|secureerase|partitiondisk|reformat|apfs)", args[0]) \
            and (args[0].lower() != "apfs" or (len(args) > 1 and "delete" in args[1].lower() or "erase" in lower)):
        raise Hit("RC-2", f"diskutil {args[0]}")
    elif b in ("umount", "mount") and any(norm(p) == "/" or is_system(norm(p)) for p in pos):
        raise Hit("RC-2", f"{b} of a system volume")

    elif b in ("chmod", "chown", "chgrp"):
        mode = pos[0] if b == "chmod" and pos else ""
        if re.search(r"[ugo]*\+[rwx]*s|^[2467][0-7]{3}$", mode):
            raise Hit("RC-3", "chmod setting setuid/setgid bits")
        for p in pos[1:]:
            np = norm(p)
            if is_system(np) or is_cred(np) or is_harness(np):
                raise Hit("RC-3", f"{b} on a protected path ({p})")

    elif b == "npx" and (s & {"y"} or "--yes" in l):
        pkg = next((p for p in pos), "")
        if pkg and "@" not in pkg.lstrip("@"):
            raise Hit("RC-4", f"npx -y {pkg} without a pinned @version")
    elif (b in ("pip", "pip3") or (b == "uv" and args[:1] == ["pip"]) or (INTERP_RE.match(b) and "pip" in args[:2])) \
            and "install" in args and any(re.match(r"^(git\+)?https?://", a) for a in args):
        raise Hit("RC-4", "pip install from a bare URL")

    elif b == "git":
        i = 0
        while i < len(args) and args[i].startswith("-"):
            if args[i] == "-c" and i + 1 < len(args) and re.match(r"(?i)core\.hookspath=(/dev/null)?$", args[i + 1]):
                raise Hit("RC-10", "git with hooks disabled (core.hooksPath)")
            i += 2 if args[i] in ("-C", "-c", "--git-dir", "--work-tree", "--namespace") else 1
        sub, rest = (args[i], args[i + 1:]) if i < len(args) else ("", [])
        gs, gl, gpos = flags(rest)
        if "--no-verify" in rest or (sub == "commit" and "n" in gs):
            raise Hit("RC-10", "git hook bypass (--no-verify)")
        if sub == "push":
            if gl & {"--force", "--force-with-lease", "--force-if-includes"} or "f" in gs \
                    or any(p.startswith("+") for p in gpos):
                raise Hit("RC-5", "git push --force")
            if "--mirror" in gl:
                raise Hit("RC-5", "git push --mirror")
            if ("--delete" in gl or "d" in gs) and any("refs/tags" in p or p.startswith("v") for p in gpos[1:]) \
                    or any(p.startswith(":refs/tags") for p in gpos):
                raise Hit("RC-5", "deleting a pushed tag")
        elif sub == "reset" and "--hard" in gl:
            raise Hit("RC-5", "git reset --hard")
        elif sub in ("filter-branch", "filter-repo"):
            raise Hit("RC-5", f"git {sub} (history rewrite)")
        elif sub == "remote" and rest[:1] and rest[0] in ("remove", "rm"):
            raise Hit("RC-5", "git remote remove")
        elif sub == "branch" and ("D" in gs or ("--delete" in gl and "--force" in gl)) \
                and any(p in ("main", "master") for p in gpos):
            raise Hit("RC-5", "force-deleting the default branch")
    elif b == "git-filter-repo":
        raise Hit("RC-5", "git filter-repo (history rewrite)")

    elif b == "security" and args[:1] and (args[0] == "dump-keychain" or
                                           (args[0].startswith("find-") and args[0].endswith("-password") and s & {"w", "g"})):
        raise Hit("RC-6", f"security {args[0]} (keychain secret read)")
    elif b in ("gpg", "gpg2") and l & {"--export-secret-keys", "--export-secret-subkeys"}:
        raise Hit("RC-6", "gpg export of secret keys")

    elif b == "curl":
        urls = [a for a in args if re.match(r"^[a-z]+://|^(localhost|127\.0\.0\.1)([:/]|$)", a)]
        local = urls and all(re.match(r"^(https?://)?(localhost|127\.0\.0\.1|\[::1\])([:/]|$)", u) for u in urls)
        up = "--upload-file" in l or "T" in s
        for i, a in enumerate(args):
            nxt = args[i + 1] if i + 1 < len(args) else ""
            if re.match(r"^(-d|--data|--data-binary|--data-urlencode|--json)$", a) and nxt.startswith("@") and nxt != "@-" \
                    or re.match(r"^-d@|^--data(-binary|-urlencode)?=@", a) \
                    or a in ("-F", "--form") and re.search(r"=[@<]", nxt):
                up = True
        if up and not local:
            raise Hit("RC-7", "curl uploading a local file to a remote host")
    elif b == "wget" and l & {"--post-file", "--body-file"}:
        raise Hit("RC-7", "wget uploading a local file")
    elif b in ("nc", "ncat", "netcat") and s & {"e", "c"}:
        raise Hit("RC-7", "netcat with command execution (reverse shell)")

    elif b == "crontab" and (s & {"e", "r"} or pos):
        raise Hit("RC-8", "crontab edit")
    elif b == "launchctl" and args[:1] and args[0] in ("load", "bootstrap", "enable", "submit"):
        raise Hit("RC-8", f"launchctl {args[0]} (persistence)")
    elif b == "systemctl" and "enable" in args:
        raise Hit("RC-8", "systemctl enable (persistence)")

    elif b in ("terraform", "tofu") and ("destroy" in args or "-destroy" in args):
        raise Hit("RC-9", f"{b} destroy")
    elif b == "aws" and (args[:2] in (["s3", "rb"],) or (args[:2] == ["s3", "rm"] and "--recursive" in l)
                         or any(re.match(r"^(delete|terminate)-", a) for a in args[1:2])):
        raise Hit("RC-9", "aws delete operation")
    elif b in ("gcloud", "az") and "delete" in args:
        raise Hit("RC-9", f"{b} … delete")
    elif b == "kubectl" and args[:1] == ["delete"] and (args[1:2] and args[1] in ("ns", "namespace", "namespaces") or "--all" in l):
        raise Hit("RC-9", "kubectl delete namespace/--all")
    elif b == "redis-cli" and re.search(r"\bflush(all|db)\b", lower):
        raise Hit("RC-9", "redis FLUSHALL/FLUSHDB")
    elif b == "docker" and args[:2] == ["system", "prune"] and ("a" in s or "--all" in l) and "--volumes" in l:
        raise Hit("RC-9", "docker system prune -a --volumes")

    if b not in TEXT_SINKS:
        sql = [lower] + ([h.lower() for h, _ in cmd.heredocs] if b in DB_CLIENTS else [])
        if any(re.search(r"\b(drop|truncate)\s+(database|table|schema)\b", x) for x in sql):
            raise Hit("RC-9", "SQL DROP/TRUNCATE")
    if b in READERS:
        for p in pos:
            if is_cred(norm(p)):
                raise Hit("RC-6", f"reading a credential file ({p})")

    # writes via argv targets
    targets = []
    if b in ("tee",):
        targets = pos
    elif b in ("cp", "mv", "install", "ln", "rsync") and len(pos) >= 2:
        targets = pos[-1:]
    elif b in ("sed", "perl") and (s & {"i"} or any(a.startswith("-i") or a == "--in-place" for a in args)):
        targets = pos[1:] if b == "sed" else pos
    elif b in ("touch", "truncate"):
        targets = pos
    for p in targets:
        np = norm(p)
        wc = write_class(np)
        if wc:
            raise Hit(*wc)
        if base(p) in PROFILES and home_rel(np):
            raise Hit("RC-8", "write to a shell profile", ask=True)


def check_text(text, depth=0):
    if depth > 6:
        return
    for pipe in parse(text):
        names = []
        for cmd in pipe:
            for w in cmd.words:
                for sub in w.subs + w.procsub:
                    check_text(sub, depth + 1)
            for _, w in cmd.redirs:
                for sub in w.subs + w.procsub:
                    check_text(sub, depth + 1)
            for body, quoted in cmd.heredocs:
                if not quoted:
                    for m in re.finditer(r"\$\(", body):
                        check_text(_capture(body, m.end(), ")")[0], depth + 1)
            check_cmd(cmd, depth)
            argv = strip_wrappers([w.v for w in cmd.words])
            names.append(base(argv[0]) if argv else "")
        for i, n in enumerate(names):
            later = names[i + 1:]
            if n in FETCHERS and any(x in SHELLS or INTERP_RE.match(x) for x in later):
                raise Hit("RC-4", f"{n} piped into an interpreter")
            if n in ENV_DUMPS and any(x in NET_SINKS for x in later):
                raise Hit("RC-6", "environment dump piped to a network command")


def classify(command, cwd=None):
    """Return None (allow) or Hit."""
    global CWD
    if cwd:
        CWD = posix(cwd)
    try:
        check_text(command)
    except Hit as h:
        return h
    return None


def main():
    if sys.argv[1:2] == ["--claude-hook"]:
        try:
            env = json.load(sys.stdin)
        except ValueError:
            return 0
        if env.get("tool_name") != "Bash":
            return 0
        cmd = (env.get("tool_input") or {}).get("command") or ""
        try:
            hit = classify(cmd, env.get("cwd"))
        except Exception as e:  # classifier bug: hand to the human, never silently allow
            hit = Hit("RC-?", f"classifier error ({type(e).__name__}); confirm manually", ask=True)
        if hit:
            reason = f"ds-rig {hit.rc}: {hit.reason}."
            if not hit.ask:
                reason += " If the user really wants this, they can run it themselves with `! <command>`."
            json.dump({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                              "permissionDecision": "ask" if hit.ask else "deny",
                                              "permissionDecisionReason": reason}}, sys.stdout)
        return 0
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    hit = classify(cmd) if cmd else None
    if not hit:
        return 0
    print(f"{hit.rc}|{hit.reason}")
    return 2 if hit.ask else 1


if __name__ == "__main__":
    sys.exit(main())
