# CLI and TUI — the terminal is the interface

Loaded for command-line and terminal products (`ui∋cli-tui` or `platforms∋cli`). One command table drives parsing and help (SIM-09).

### CLI-01 [HIGH] No usable `--help` or `--version`
- **Detect:** the entry point has no `--help`/`-h` and no `--version`; help text written by hand next to the parser instead of generated from it, so they disagree; help without a usage line, an example or the exit codes; an unknown flag or missing argument that prints a stack trace instead of the usage line.
- **Mech:** M (run the entry point with `--help`, `--version` and an unknown flag)
- **Fix:** let the argument parser (argparse, click, cobra, clap, commander) generate help and version; add one example per subcommand; on a usage error print the usage line to stderr and exit 2.
- **Impact:** users cannot discover the tool or report the version they run, and scripts break on silent behaviour changes.
- **Source:** GNU Coding Standards, Command-Line Interfaces (`--help`, `--version`); clig.dev, Help (https://clig.dev/).

### CLI-02 [CRITICAL] Exit status does not report failure
- **Detect:** errors caught, printed and followed by exit 0; `main` that always returns 0; one non-zero code for every failure where callers must tell usage errors from runtime failures; a failure in a pipeline step swallowed (`|| true`, missing `set -o pipefail` in shell wrappers).
- **Mech:** T `git grep -nIE '(sys\.exit|os\.Exit|process\.exit|std::process::exit|exit)\(0\)|\|\| true' -- ':!*test*' ':!*.md'`
- **Fix:** exit 0 only on success; 2 for usage errors; documented non-zero codes for the failure classes callers act on; propagate errors to one top-level handler that sets the code.
- **Impact:** CI jobs, scripts and `&&` chains continue after a failure as if it had succeeded.
- **Source:** POSIX, exit status of utilities (IEEE Std 1003.1 XCU 2.8.2); clig.dev, The Basics.

### CLI-03 [HIGH] Data and diagnostics on the wrong stream
- **Detect:** errors, warnings, progress or prompts written to stdout; the command's real output written to stderr; log lines interleaved with machine-readable output (JSON, CSV) on stdout; no machine-readable format (`--json`) where the output is parsed by other tools.
- **Mech:** T `git grep -nIiE '(print|console\.log|fmt\.Print(ln|f)?|println!|echo)[[:space:]]*\(?["'"'"'].*(error|warning|failed)' -- ':!*test*' ':!*.md'`
- **Fix:** results on stdout, everything for the human (errors, progress, prompts) on stderr; a stable `--json` (or `--format`) output for scripts.
- **Impact:** piping the tool into another program feeds it error text, and redirecting output hides the errors.
- **Source:** POSIX, stdin/stdout/stderr conventions; clig.dev, Output.

### CLI-04 [MEDIUM] Colour and animation not gated on a terminal
- **Detect:** ANSI escapes, spinners and progress bars emitted unconditionally; no `isatty` check on the stream being written; `NO_COLOR` not honoured; no `--no-color` flag; animation still drawn when `TERM=dumb` or in CI logs.
- **Mech:** T `git grep -nIE '\\033\[|\\x1b\[|\\u001b\[|\\e\[' -- ':!*.md'` · `git grep -nIE 'NO_COLOR|isatty|IsTerminal|is_terminal|stdout\.isTTY|supportsColor'`
- **Fix:** enable colour and animation only when the stream is a TTY, `NO_COLOR` is unset and `TERM` is not `dumb`; offer `--no-color` and a quiet mode.
- **Impact:** logs and files fill with escape codes, and users who need plain output (screen readers, colour-blind users, CI) cannot get it.
- **Source:** NO_COLOR (https://no-color.org/); clig.dev, Output.

### CLI-05 [HIGH] Prompts block non-interactive use
- **Detect:** interactive prompts or confirmations with no flag to answer them (`--yes`, `--force`, an input file); prompts shown when stdin is not a TTY, so the tool hangs in CI; secrets read only from a prompt or only from argv (visible in `ps`) with no stdin or file option.
- **Mech:** T `git grep -nIE 'input\(|getpass|readline\(|prompt\(|Confirm\.ask|inquirer|survey\.Ask|dialoguer' -- ':!*test*' ':!*.md'`
- **Fix:** every prompt has a flag equivalent; when stdin is not a TTY, fail with a message naming the flag instead of waiting; read secrets from stdin, a file or an environment variable.
- **Impact:** automation hangs until a timeout, and secrets passed on the command line leak to other users of the machine.
- **Source:** clig.dev, Interactivity and Arguments and flags; CWE-214 (sensitive information in process arguments).

### CLI-06 [MEDIUM] Interrupt or resize leaves a broken state
- **Detect:** no SIGINT/SIGTERM handling around temporary files, partial writes, locks or a raw-mode terminal; Ctrl-C printing a stack trace; a TUI that leaves the terminal in raw or alternate-screen mode after a crash; a full-screen UI that ignores `SIGWINCH` and draws at the old size.
- **Mech:** T `git grep -nIE 'SIGINT|SIGTERM|SIGWINCH|KeyboardInterrupt|signal\.Notify|ctrlc|process\.on\(["'"'"']SIG' -- ':!*.md'`
- **Fix:** catch interrupts, clean up and exit 130; write files atomically (temp file then rename); restore the terminal in a `finally`/`defer`/drop guard; redraw on resize.
- **Impact:** an interrupted run corrupts output or leaves a terminal the user must `reset` by hand.
- **Source:** POSIX, signal concepts; clig.dev, Robustness.

### CLI-07 [MEDIUM] Arguments break the shell conventions
- **Detect:** options that cannot be combined (`-ab`) or placed after operands without reason; no `--` end-of-options marker, so a file named `-rf` is read as flags; `-` not accepted for stdin/stdout where the tool reads or writes files; long options with no short form for the common ones, or single-dash long options.
- **Mech:** M (the parser library's configuration shows it)
- **Fix:** use a standard parser with POSIX short options, GNU long options and `--`; accept `-` for standard streams.
- **Impact:** users hit surprises their other tools taught them not to expect, and file names starting with `-` become commands.
- **Source:** POSIX Utility Syntax Guidelines (IEEE Std 1003.1 XBD 12.2); GNU Coding Standards, Command-Line Interfaces.
