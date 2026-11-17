# Repo — host settings, branches, community files

Host settings are read with the host's CLI (`gh api …`, `glab api …`), which needs credentials, so those rules are `M`; an unauthenticated CLI makes them `only you can do: gh auth login`. Changing a setting is an account action (kernel §5): the finding gives the exact command or settings path as `only you can do`. A solo repository (one committer in the last year, `git shortlog -sn --since=1.year HEAD`) needs no required reviewers and no CODEOWNERS.

### RPO-01 [HIGH] Default branch accepts force-push, deletion or unchecked merges
- **Detect:** a default branch without protection (ruleset or classic rule): force-push or deletion allowed, no linear history; with a hosted CI, its checks not required before merge; with more than one committer, no required review; a ruleset bypass list holding admins or broad roles with no recorded reason. Read: `gh api repos/{owner}/{repo}/rulesets`, `gh api repos/{owner}/{repo}/branches/{branch}/protection`.
- **Mech:** M (host API)
- **Fix:** a ruleset (classic protection where the plan has no rulesets) on the default branch: block force-push and deletion, require linear history, require the CI checks that actually run, one approving review on team repos, an empty bypass list.
- **Impact:** one mistaken force-push or unchecked merge rewrites or breaks the shared history with no gate.
- **Source:** Reversibility; GitHub Docs, About rulesets and About protected branches; GitLab Docs, Protected branches.

### RPO-02 [HIGH] Merge settings produce noisy history or stale branches
- **Detect:** merge commits or rebase merges allowed beside squash where changelog or version come from PR titles; squash commits not titled from the PR title; head branches kept after merge; auto-merge enabled (DOP-15). Read: `gh api repos/{owner}/{repo} --jq '{allow_squash_merge,allow_merge_commit,allow_rebase_merge,squash_merge_commit_title,delete_branch_on_merge,allow_auto_merge}'`.
- **Mech:** M (host API)
- **Fix:** squash only, titled from the PR title, head branches deleted on merge, auto-merge off.
- **Impact:** a mixed history breaks commit-driven release tooling; merged branches pile up.
- **Source:** GitHub Docs, Configuring pull request merges; Conventional Commits 1.0.0.

### RPO-04 [MEDIUM] Team repo without owners for sensitive paths
- **Detect:** more than one committer in the last year and no `CODEOWNERS`, or one that misses CI config, infrastructure, auth, migrations and API contracts, or names users or teams that no longer exist.
- **Mech:** T `git shortlog -sn --since=1.year HEAD` · `git ls-files | grep -E '(^|/)CODEOWNERS$'`
- **Fix:** a `CODEOWNERS` file (`.github/` on GitHub; root, `docs/` or `.gitlab/` on GitLab) mapping those paths to accountable owners.
- **Impact:** a change to a sensitive path is reviewed by whoever notices it, not by the person accountable for it.
- **Source:** GitHub Docs, About code owners; GitLab Docs, Code owners.

### RPO-06 [MEDIUM] Stale branches and oversized history
- **Detect:** branches untouched for over 30 days with no open PR; branches merged into the default and not deleted; remote-tracking refs whose upstream is gone; blobs over 10 MB anywhere in history.
- **Mech:** T `git for-each-ref --sort=committerdate --format='%(committerdate:short) %(refname:short)' refs/heads refs/remotes` · `git branch -r --merged HEAD` · `git rev-list --objects --all | git cat-file --batch-check='%(objectsize) %(objectname) %(rest)' | awk '$1 > 10485760'`
- **Fix:** delete merged branches and prune remotes (`git remote prune origin`); unmerged stale branches and history rewrites (`git filter-repo --strip-blobs-bigger-than 10M`, or Git LFS to keep the file) are `only you can do`: they lose commits or break every clone.
- **Impact:** dead branches hide which work is live; large blobs slow every clone for good.
- **Source:** git-filter-repo; Git LFS; Pro Git, Branch management.

### RPO-07 [MEDIUM] Public repo without licence, security policy or contribution guide
applies_when: public_repo=yes
- **Detect:** no `LICENSE` with an SPDX-listed licence, or `SPDX-License-Identifier` headers that disagree with it; no `SECURITY.md` naming a private reporting channel and a response time; no `CONTRIBUTING.md` (setup, tests, PR expectations). Dependency licence compatibility is SEC-14.
- **Mech:** T `for n in 'LICEN[CS]E|COPYING' SECURITY CONTRIBUTING; do git ls-files | grep -qiE "(^|/)($n)(\.[a-z]+)?$" || echo "no $n file tracked"; done` · `git grep -hoIE 'SPDX-License-Identifier:[[:space:]]*[^[:space:]*]+' -- ':!*.md' | sort | uniq -c | awk '{l[NR]=$0} END{if(NR>1)for(i=1;i<=NR;i++)print l[i]}'`
- **Fix:** add the missing files (SECURITY.md: supported versions, private channel, acknowledgement time); keep SPDX headers consistent with LICENSE.
- **Impact:** without a licence the code is not open for reuse; without a private channel a found vulnerability goes public before a fix.
- **Source:** GitHub Docs, Community health files; SPDX License List; REUSE specification.

### RPO-08 [LOW] Public repo hard to find or recognise
applies_when: public_repo=yes
- **Detect:** empty description, fewer than 3 topics, no homepage URL where a site exists, no custom social preview image (1280×640). Read: `gh repo view --json description,repositoryTopics,homepageUrl`.
- **Mech:** M (host API)
- **Fix:** a one-sentence description (≤ 100 characters), 3 or more topics, the homepage URL, a preview image with the name and one-liner.
- **Impact:** search results and shared links show a blank, generic card.
- **Source:** GitHub Docs, Classifying your repository with topics and Customizing your repository's social media preview.

### RPO-11 [HIGH] Tracked files depend on something outside the repository
- **Detect:** a tracked file pointing at an absolute machine-local path (`/Users/…`, `/home/…`, `C:\Users\…`) for a rule, spec, decision log, script or generator the project needs; a governing document that exists in one untracked copy.
- **Mech:** T `git grep -nIE '(/Users/|/home/|[A-Z]:.Users.)[A-Za-z0-9._-]+' -- ':!*.lock'`
- **Fix:** move the artifact into the repo (or a versioned sibling repo) and reference it relatively; machine-specific values come from the environment.
- **Impact:** it works on one machine only; losing that machine loses the artifact and its history.
- **Source:** Twelve-Factor I (Codebase) and III (Config).

### RPO-12 [HIGH] Host security features left off
- **Detect:** secret scanning or push protection off; dependency alerts or security-update PRs off (alerts feed DOP-06); private vulnerability reporting off on a public repo; code scanning not configured where the plan offers it. Read: `gh api repos/{owner}/{repo} --jq .security_and_analysis`, `gh api repos/{owner}/{repo}/vulnerability-alerts` (204 = on), `gh api repos/{owner}/{repo}/private-vulnerability-reporting`, `gh api repos/{owner}/{repo}/code-scanning/default-setup --jq .state`.
- **Mech:** M (host API)
- **Fix:** turn them on under Settings → Code security, given as `only you can do` with the matching `gh api -X PUT` or `-X PATCH` call; code scanning default setup runs on GitHub Actions, so with Actions off a local static-analysis step in the gate takes its place.
- **Impact:** a pushed secret lands in history unblocked, a vulnerable dependency goes unflagged, and a researcher has no private channel.
- **Source:** Secure / private by default; GitHub Docs, Push protection, Dependabot alerts, Private vulnerability reporting and Code scanning default setup.
