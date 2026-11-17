# Code — errors, complexity, duplication, concurrency

Function- and file-level checks for any stack; structure is in [arch.md](arch.md). Thresholds are the project's configured linter settings; a tool default applies only when none is set. Dead code, single-use wrappers and one fact in two homes are the lean phase ([simplify.md](simplify.md)).

### ARC-06 [HIGH] Errors swallowed or signalled inconsistently
- **Detect:** an empty `catch`/`except`, `except: pass`, `_ = err`, or a catch of the broadest type in business logic that neither handles, re-throws nor logs; expected outcomes (validation, not found) signalled by exceptions in one place and `null` or sentinels in another; error text that does not say what was expected, what arrived and what to do.
- **Mech:** S `git grep -nIE 'except( [A-Za-z.]+)?:[[:space:]]*pass([^[:alnum:]_]|$)|catch[[:space:]]*(\([^)]*\))?[[:space:]]*\{[[:space:]]*\}|(^|[^[:alnum:]_])_[[:space:]]*=[[:space:]]*err(^|[^[:alnum:]_])' -- ':!*.md'` · `ruff check --select S110,E722,BLE001 --output-format concise .`
- **Fix:** one error model per layer: expected outcomes as typed results or specific error types (the language's idiom: `Result`, `(value, error)`, a discriminated union, specific exceptions); unexpected ones propagate to one top-level handler that logs and maps them; a catch handles, adds context and re-throws, or logs at warning or above.
- **Impact:** some failures are logged and some vanish, so the caller reports success on a failed write and nobody can say why.
- **Source:** CWE-390 (Detection of Error Condition Without Action); CWE-754; fail fast.

### TST-06 [HIGH] Linter or type checker missing, ignored or silenced
- **Detect:** no linter or type checker configured for a present stack; type errors left red; suppressions without a reason (`# type: ignore`, `@ts-ignore`, `eslint-disable`, `# noqa`, `@SuppressWarnings` with nothing after them); a strict mode switched off.
- **Mech:** S `git grep -nIE '(#[[:space:]]*type:[[:space:]]*ignore|//[[:space:]]*@ts-ignore|eslint-disable(-next-line)?|#[[:space:]]*noqa)[[:space:]]*$' -- ':!*.md'`
- **Fix:** enable the stack's default linter and type checker in strict mode ([toolchains.md](../toolchains.md)); each suppression names its rule and reason on the same line.
- **Impact:** wrong types, unreachable code and hallucinated APIs reach review only if a person spots them.
- **Source:** Fail fast; TypeScript `strict`; mypy and Pyright strict modes; golangci-lint; Clippy.

### ARC-10 [MEDIUM] Function too complex to review
- **Detect:** functions over the configured complexity, length, nesting or parameter threshold; where the tool reports cognitive complexity, prefer it. Skip inherently complex domains (parsers, cryptography, numeric kernels) and flat dispatch switches.
- **Mech:** S `lizard -w -x "./node_modules/*" -x "./vendor/*" .` · `ruff check --select C901,PLR0912,PLR0913,PLR0915 --output-format concise .` · `gocyclo -over 15 .`
- **Fix:** early returns, named extracted steps, a parameter object; set the threshold in the linter config so the gate holds it (ESLint `complexity`/`max-depth`/`max-params`/`max-lines-per-function`, ruff `C901`, detekt, SwiftLint `cyclomatic_complexity`).
- **Impact:** past the threshold a function takes longer to review correctly and hides more defects per line.
- **Source:** KISS; McCabe, "A Complexity Measure" (1976); Campbell, Cognitive Complexity (SonarSource, 2018).

### ARC-22 [LOW] Call chain reaching through collaborators
- **Detect:** four or more chained calls that walk an object graph (`order.getCustomer().getAddress().getCity().getName()`), so the caller knows the structure of objects it does not own. Fluent builders, query builders, streams and promise chains that return the same kind of object are not findings.
- **Mech:** T `git grep -nIE '([[:alnum:]_]+\([^()]*\)\.){3,}[[:alnum:]_]+\(' -- ':!*test*' ':!*.md' ':!*.lock'`
- **Fix:** ask the direct collaborator for what is needed (`order.shippingCity()`), or pass the needed value in.
- **Impact:** a change to any object in the chain breaks every caller that reached through it.
- **Source:** Law of Demeter (Lieberherr and Holland, "Assuring Good Style for Object-Oriented Programs", 1989).

### ARC-18 [HIGH] Data race or check-then-act on shared state
- **Detect:** state shared between threads, goroutines, async tasks or processes written without a lock, atomic or single owner; a read-modify-write split across awaits or requests on a shared row or key; check-then-act on files or records (exists then create, select then insert without a unique constraint); a stack with a race detector whose test run does not use it.
- **Mech:** T `git grep -nIE 'os\.path\.exists\(|fs\.existsSync\(|File\.Exists\(|Files\.exists\(' -- ':!*test*' ':!*.md'` · `git grep -nIE '(^|[^[:alnum:]_])go test([^[:alnum:]_]|$)' -- ':!*.md' | grep -v -- '-race'`
- **Fix:** one owner (actor, channel, queue) or a lock or atomic; atomic database operations (`SET n = n + 1`, unique constraint plus upsert, a version column); create-exclusive open flags instead of exists-then-create; run tests under Go `-race` or ThreadSanitizer.
- **Impact:** lost updates, double charges or bookings and corrupted files that appear only under load and never reproduce locally.
- **Source:** CWE-362; CWE-367 (TOCTOU); Go race detector (https://go.dev/doc/articles/race_detector); ThreadSanitizer (Clang docs).

### ARC-19 [HIGH] Async work started and never awaited
- **Detect:** a Promise, Task or coroutine that is neither awaited, returned nor given an error handler; a goroutine, thread or background task whose error is dropped; ignored error returns.
- **Mech:** T `errcheck ./...` · `ruff check --select RUF006 --output-format concise .`
- **Fix:** await or return it; fire-and-forget only through a supervisor that logs failures (task group, `errgroup`, a queue); enable `@typescript-eslint/no-floating-promises`, `errcheck` or ruff `RUF006` in the gate.
- **Impact:** the failure vanishes: the caller reports success while the write never happened, or the process exits before the task ends.
- **Source:** Fail fast; CWE-252 (Unchecked Return Value); typescript-eslint `no-floating-promises`.

### ARC-20 [HIGH] Work that grows faster than its input
- **Detect:** nested loops or a linear lookup (`in list`, `indexOf`, `find`) inside a loop over a user- or data-sized collection; sorting or copying inside a loop; a regex with nested or overlapping quantifiers (`(a+)+`, `(.*)*`, `(a|a)*`) applied to user input.
- **Mech:** T `git grep -nIE '\([^()]*[+*]\)[+*{]' -- ':!*.md' ':!*.lock'`
- **Fix:** look up through a set or map, precompute outside the loop, bound the input size; rewrite the regex without nested quantifiers, or use a linear-time engine (RE2, Go `regexp`, Rust `regex`) or a match timeout; add a test at the maximum input size.
- **Impact:** a request that is fast in tests takes seconds or minutes at production size, and one crafted string pins a CPU (ReDoS).
- **Source:** CWE-407; CWE-1333; OWASP ReDoS.
