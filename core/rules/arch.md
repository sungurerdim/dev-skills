# Arch — structure: layers, state, boundaries, processes

Module-level design for any stack. Code-level checks (errors, complexity, duplication, concurrency) are in [code.md](code.md); removing what should not exist is the lean phase ([simplify.md](simplify.md)).

### ARC-01 [HIGH] Business logic or data access in entry points
- **Detect:** a route handler, controller, CLI command, UI event handler or message consumer that makes business decisions, computes, or queries storage itself instead of parse input → call one service or use case → format output; a lower layer importing the transport layer.
- **Mech:** T `git grep -nIE '(^|[^[:alnum:]_])(SELECT|INSERT INTO|UPDATE|DELETE FROM)([^[:alnum:]_]|$)|\.(query|execute|findMany|findOne|aggregate)\(' -- '*controller*' '*handler*' '*route*' '*views*' '*endpoint*' ':!*.md'`
- **Fix:** move the logic into a service or use-case function; the entry point keeps only parsing, the call and formatting.
- **Impact:** logic inside an entry point cannot be reused by another transport or unit-tested without it, and each route re-implements the same rule.
- **Source:** Separation of concerns; Martin, *Clean Architecture*; Cockburn, Hexagonal Architecture (ports and adapters).

### ARC-02 [HIGH] Shared mutable state without one owner
- **Detect:** the same state written from several modules or components; module-level or singleton mutable state written per request; objects passed between layers and mutated in place; two-way bindings that update each other.
- **Mech:** M
- **Fix:** one owner per piece of state; others send events or commands and read snapshots; values that cross layers are immutable (the language's readonly, frozen or value types).
- **Impact:** a write through one reference silently changes what another layer holds, so state changes cannot be traced or reproduced.
- **Source:** DRY / single source of truth; Flux unidirectional data flow; Evans, *Domain-Driven Design* (value objects); Bloch, *Effective Java* (minimize mutability).

### ARC-04 [HIGH] Business logic builds its own infrastructure
- **Detect:** domain or service code that instantiates concrete clients, drivers or repositories, or reaches a global singleton, instead of receiving them; the code cannot run in a test without the real service.
- **Mech:** T `git grep -nIE 'new [A-Z][A-Za-z]*(Client|Repository|Gateway|Driver)\(' -- ':!*test*' ':!*spec*' ':!*.md'`
- **Fix:** pass dependencies in through constructor or function parameters, wired once at the entry point (the framework's injection where it has one); no container for a handful of objects.
- **Impact:** the module is locked to one implementation and its tests need the network, a database or a paid API.
- **Source:** SOLID — dependency inversion (Martin, *Agile Software Development*).

### ARC-07 [HIGH] Module boundaries not held
- **Detect:** import cycles between modules; imports that reach past a module's public entry into another feature's internals; a tree grouped by type where one feature change touches many directories; a module exporting far more than its consumers import (shallow module); a dependency direction stated in docs that no tool checks.
- **Mech:** T `lint-imports` · `depcruise . --output-type err`
- **Fix:** group by feature, each with one public entry; break a cycle by moving the shared part down or inverting the call (callback, event); encode the allowed direction in the stack's boundary checker (import-linter, dependency-cruiser, ArchUnit, Go `internal/` packages) and run it in the gate.
- **Impact:** with a cycle or a deep import no module can change or be tested alone, and the layering erodes one convenient import at a time.
- **Source:** Separation of concerns; Martin, *Clean Architecture* (acyclic dependencies principle); Ousterhout, *A Philosophy of Software Design* (deep modules); fitness functions (Ford, Parsons, Kua).

### ARC-12 [HIGH] God module rewritten in one step
- **Detect:** a module most of the codebase imports through (dozens of re-exported symbols, the anchor of an import cycle) or one class spanning unrelated domains, with a plan or branch that rewrites it in a single pass or splits it into several per-layer god modules.
- **Mech:** M
- **Fix:** strangler-fig phases, each shipped green: move leaf dependents (constants, pure helpers) to their real home; break the remaining cycles by inversion; split the rest by domain and migrate call sites last.
- **Impact:** a big-bang rewrite of the most imported module cannot be reviewed or reverted in parts and stalls half-migrated.
- **Source:** Reversibility; Fowler, StranglerFigApplication (https://martinfowler.com/bliki/StranglerFigApplication.html); Gall's law.

### ARC-16 [MEDIUM] Module with more than one reason to change
- **Detect:** a module whose history mixes unrelated features (`git log --format= --name-only -- {file}`); exports that share no nouns and no callers; one responsibility (validation, formatting, retry) implemented separately in 3+ modules; one requirement change touching more than 3 modules; a subtype that stubs or narrows its parent (LSP); implementors stubbing interface members they do not need (ISP); a new variant that needs edits to switches in several places (OCP); logic reading 3+ fields of another module's object (information expert).
- **Mech:** T `git grep -nIE 'raise NotImplementedError|throw new (UnsupportedOperationException|NotImplementedException|NotSupportedException)|unimplemented!\(|todo!\(' -- ':!*test*' ':!*.md'`
- **Fix:** split by reason to change; route a scattered responsibility through one owner; move logic next to the data it reads; replace a type switch with polymorphism or a table only once a third variant exists.
- **Impact:** a change for one feature breaks another, and a fix lands in one of several variants while the others keep the bug.
- **Source:** SOLID (Martin, *Agile Software Development*); GRASP (Larman, *Applying UML and Patterns*); separation of concerns (Dijkstra).

### ARC-21 [MEDIUM] Inheritance used to share code
- **Detect:** a base class whose subclasses are not kinds of it and inherit only to reuse helpers (`BaseHelper`, `CommonUtils`, mixins stacked for features); an own class hierarchy three or more levels deep; a subclass overriding a parent method to disable or bypass it (the LSP case is ARC-16). Framework-required bases (test cases, UI widgets, ORM models) are not findings.
- **Mech:** T `git grep -nIE 'class[[:space:]]+[[:alnum:]_]+[[:space:]]*(\(|extends[[:space:]]|:)[[:space:]]*[[:alnum:]_.]*(Base|Abstract|Mixin|Helper|Util|Common)' -- ':!*test*' ':!*.md'`
- **Fix:** pass the shared behaviour in as a collaborator or plain function and keep inheritance for a true is-a; flatten the hierarchy to one level below an interface.
- **Impact:** a change to the base ripples into every subclass, which then cannot be understood, tested or reused without the whole chain.
- **Source:** Composition over inheritance (Gamma et al., *Design Patterns*); Bloch, *Effective Java* (favor composition over inheritance).

### ARC-17 [MEDIUM] One concept, several names or shapes
- **Detect:** at least 3 concrete examples of one drift: the same concept named differently across layers or surfaces (code identifiers, CLI flags and subcommands, config keys and env vars, API fields, docs, UI copy: `--dry-run` here, `--simulate` there, `timeout` in config, `wait` in the docs, "workspace" in the UI, "project" in the API); one word meaning two things; analogous functions with different parameter order or options shape; the same operation with divergent signatures in two modules; mixed units or formats at boundaries (ms and s, local time and UTC, snake and camel case); `throw`, `Result` and `null` mixed as the error signal inside one layer.
- **Mech:** M (3 examples, each `file:line`)
- **Fix:** pick the dominant name or shape, record it in the project's glossary or agent rules file, rename the rest in one unit.
- **Impact:** every caller must remember which convention applies where, and mismatched units produce silently wrong values.
- **Source:** Evans, *Domain-Driven Design* (ubiquitous language); principle of least astonishment.

### RTP-10 [HIGH] Process not disposable
applies_when: api≠none or deploy≠none
- **Detect:** no handler for SIGTERM/SIGINT (or the platform's stop hook) that stops intake, drains in-flight work with a bounded timeout and closes connections; per-process state that must survive a restart (in-memory sessions, local-disk uploads, an in-process queue treated as durable).
- **Mech:** S `git grep -qIE 'SIGTERM|SIGINT|NotifyContext|addShutdownHook|ApplicationStopping|on_shutdown' -- ':!*.md' || echo 'no shutdown handler in tracked code'`
- **Fix:** on SIGTERM stop accepting work, drain, close pools, exit; non-zero when the drain times out. Durable state goes to a backing service. Health endpoints: OBS-02 in [ops.md](ops.md).
- **Impact:** every deploy or scale-down drops in-flight requests and can leave half-written data.
- **Source:** Twelve-Factor VI Processes and IX Disposability (https://12factor.net/disposability).

### AIA-07 [HIGH] LLM call without an input and output boundary
applies_when: integrations∋openai or integrations∋anthropic
- **Detect:** untrusted text (user input, fetched pages, file contents, tool results) concatenated into the instructions; model output executed, rendered as HTML, used in SQL, shell or file paths, or parsed without a schema check; tools the model can trigger beyond the request's scope; prompt changes with no eval set; no token or spend limit per call or user.
- **Mech:** T `git grep -nIE '(completions|messages|responses)\.create\(|generateContent\(|invoke_model\(' -- ':!*.md'`
- **Fix:** keep instructions and untrusted content in separate roles or fields; validate output against a schema and treat it as untrusted input (encode, parameterize); give tools least privilege and confirm side effects; run a small eval set on every prompt change; set max tokens and a per-user budget.
- **Impact:** injected text steers the model into leaking data or acting for an attacker; unchecked output becomes XSS, injection or wrong data; spend has no ceiling.
- **Source:** Fail fast; Least privilege; OWASP Top 10 for LLM Applications 2025 — LLM01 Prompt Injection, LLM05 Improper Output Handling, LLM06 Excessive Agency, LLM10 Unbounded Consumption (https://genai.owasp.org/llm-top-10/).
