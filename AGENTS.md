# AGENTS.md

Instructions for any coding agent working **on** this repository. `CLAUDE.md` holds the same
essentials plus a Claude-Code-specific blueprint profile; nothing here needs to be read twice.

dev-skills is a catalog of 30 Agent Skills — **pure markdown, zero runtime dependencies**. The
only executable code is `install.sh`, `scripts/*.sh`, and `ds-brief/assets/verify-brief.py`.

## Commands

| Task | Command |
|------|---------|
| Run the quality gate (do this before every commit) | `bash scripts/quality.sh` |
| Make the gate run on every commit | `bash scripts/quality.sh --install-hook` |
| Bypass the gate for one commit (say so if you do) | `git commit --no-verify` |
| Install the skills into a host | `./install.sh` (or `--target <dir>`, `--project <dir>`, `--skills a,b`) |
| Install for a Claude-5 host with an always-on rules layer | `./install.sh --profile lean` — strips the `portable-only`-marked blocks at install time; repo files always keep the full portable text |
| Check an installed copy for drift | `./install.sh --check` (profile-aware — reads the profile from the version stamp) |

The gate needs `bash`, `python3`, `shellcheck`, and `typos`. A missing tool fails the run loudly
and names what went unverified — never treat a skipped check as a passing one. There is no CI;
this gate is the only enforcement, by design.

## Conventions that are not guessable from the code

- **Standalone Invariant.** Every skill directory must work when installed alone. A skill may not
  reference another skill's files by path, may not link outside its own directory, and may not cite
  an in-repo file in prose — a lone install ships one directory. Cross-skill *prose* handoffs are
  correct and expected. Enforced by consistency checks 21, 22, 23; point at repo files with a full
  GitHub URL instead.
- **Completion Evidence band** appears verbatim at both the top and the bottom of every `SKILL.md`
  in the repo. Both copies are normative — do not "de-duplicate" them in repo files. The repeat is
  deliberate: model attention is position-biased, and the portable profile supports six hosts. The
  lean install profile (`--profile lean`) strips the closing copy and the other
  `<!-- portable-only -->`-marked blocks at install time only (SKILL-SPEC §1).
- **Size ceilings**, both gated: `SKILL.md` ≤ 500 lines and ≤ 48000 bytes; `README.md` ≤ 80 lines.
- **`SKILL-SPEC.md` is authoritative.** Every `ds-*` directory must satisfy it; changing a skill's
  contract usually means changing the spec and the consistency checks in the same commit.
- **Counts are mechanically checked.** `README.md`'s badge, `CLAUDE.md`'s skill heading, count line,
  and flat list must all agree with the actual number of `ds-*/` directories.
- **A new check needs a fixture.** Checks factored into functions in `scripts/check-consistency.sh`
  carry a self-test that proves they fail on deliberately broken input. Add one with your check.
- **Conventional Commits**, and `feat`/`fix` only when a user-visible capability changes. Docs,
  tests, tooling, and CI get their own type. Direct push to `main` is the deliberate workflow here.

## Gotchas

- `ds/audit/` is gitignored scratch space for skill runs — never commit it, never rely on it.
- Editing a skill's contract line (`**Owns:** … **Delegates:** … **Receives:** …`) breaks the
  reciprocity check unless the delegation target names the delegator back.
- `_typos.toml` exists because `typos` otherwise reports ~90 false hits on this repo's domain
  vocabulary. Add a checked entry rather than silencing the tool.
