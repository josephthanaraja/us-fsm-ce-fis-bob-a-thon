# Lab 1 — Extension Ideas

Lab 1's base exercise gets you to a working PR Review stage that prints a risk-ranked summary into the Jenkins console and archives it as `bob-pr-review.md`. That's the floor. This doc collects extensions you can layer on top — most of them reuse the `pipeline-git-diff-overview` mode (or a near-cousin of it) and either change *what* Bob sees, *how* Bob's output is consumed, or *who* gets notified.

A lot of "code review automation" projects fail because they generate noise. Pick extensions that increase signal — that surface things a reviewer would otherwise miss — rather than ones that just produce more text.

## Table of Contents

- [Easy wins (single-stage tweaks)](#easy-wins-single-stage-tweaks)
  - [1. Post the review as a GitHub PR comment](#1-post-the-review-as-a-github-pr-comment)
  - [2. Conventional Commits awareness](#2-conventional-commits-awareness)
  - [3. Sectioned risk perspectives](#3-sectioned-risk-perspectives)
  - [4. Skip-uninteresting heuristic](#4-skip-uninteresting-heuristic)
  - [5. JSON output for downstream tooling](#5-json-output-for-downstream-tooling)
- [Medium-effort extensions (multi-stage or new mode)](#medium-effort-extensions-multi-stage-or-new-mode)
  - [6. Inline review comments on specific lines](#6-inline-review-comments-on-specific-lines)
  - [7. PR-description-aware review](#7-pr-description-aware-review)
  - [8. Diff-classified change summary](#8-diff-classified-change-summary)
  - [9. Cross-reference with the linked Jira ticket](#9-cross-reference-with-the-linked-jira-ticket)
  - [10. Risk-band gating](#10-risk-band-gating)
- [Bigger swings (workshop-shaped extensions)](#bigger-swings-workshop-shaped-extensions)
  - [11. Two-pass review (triage → deep-dive)](#11-two-pass-review-triage--deep-dive)
  - [12. Reviewer assignment](#12-reviewer-assignment)
  - [13. Test-coverage-aware review](#13-test-coverage-aware-review)
  - [14. Architectural drift detection](#14-architectural-drift-detection)
  - [15. PR review checklist for the human](#15-pr-review-checklist-for-the-human)
- [A note on guardrails](#a-note-on-guardrails)

---

## Easy wins (single-stage tweaks)

### 1. Post the review as a GitHub PR comment

The base lab archives the review as a Jenkins artifact, which means a reviewer has to know to click into the build to find it. Take it to where reviewers actually live:

- Add a step after `askBob` that POSTs the analysis as a comment on the PR via the GitHub REST API (`POST /repos/:owner/:repo/issues/:number/comments`)
- The PR number isn't always in `BRANCH_NAME` — for multibranch pipelines it's `CHANGE_ID`. For a regular pipeline you may need to look it up from `git ls-remote` or compute it from the branch
- Use the GitHub PAT credential the workshop already has (`userN-github-pat`) — wrap with `withCredentials([usernamePassword(...)])` so the token never lands in a build log
- Tag the comment with a hidden marker (e.g. `<!-- bob-review -->`) so a future "idempotent comment" extension can find and replace it

### 2. Conventional Commits awareness

Most teams now write commit messages with `feat:` / `fix:` / `chore:` / `BREAKING CHANGE:` prefixes. The base mode ignores them. Have the rules instruct Bob to:

- Read commit subject lines from `git log origin/main..HEAD --pretty=format:'%s'` and pre-classify the PR (feature / fix / chore / breaking)
- Surface a `BREAKING CHANGE:` footer in any commit as an automatic *high* risk regardless of diff size
- Note when commits don't follow the convention — useful nudge for teams enforcing it

### 3. Sectioned risk perspectives

The base output is one risk band per change. Some teams want multiple lenses. Split the output into:

- **Security** — auth, input validation, secret handling
- **Reliability** — null-safety, concurrency, error handling
- **Performance** — hot paths, allocation churn, N+1 queries
- **Maintainability** — readability, naming, complexity

Each section gets its own band, plus a single rolled-up "overall" band for the gate. Tighten the rules to enforce each section is at most three bullets — the whole point is signal, not coverage.

### 4. Skip-uninteresting heuristic

The base lab tells Bob "if nothing notable, say so in one sentence." Make that mechanical:

- If the diff only touches a small allowlist of paths (`.gitignore`, `*.md`, `LICENSE`, formatter-only changes), short-circuit before calling Bob and write a one-line `bob-pr-review.md` ("Docs/config-only — skipping review").
- Saves Bob calls, saves console noise, makes the build faster

The risk is misclassifying — a config change can ship a real bug. Keep the allowlist narrow.

### 5. JSON output for downstream tooling

Markdown is fine for humans. Downstream automation prefers structure:

- Add a parallel mode (`pipeline-git-diff-overview-json`) with rules requiring strict JSON output: `{ "summary": "...", "risk": "high|medium|low", "watch_for": [...] }`
- Archive `bob-pr-review.json` alongside the markdown
- Future stages (a merge gate, a metrics dashboard, a Slack notifier) can consume the JSON without scraping markdown

---

## Medium-effort extensions (multi-stage or new mode)

### 6. Inline review comments on specific lines

Posting a single PR comment is fine for a summary. Pointing at the actual line a reviewer should look at is better:

- Have the JSON-output mode (idea 5) include `{ "file": "...", "line": N, "comment": "..." }` entries
- Use the GitHub Reviews API (`POST /repos/:owner/:repo/pulls/:number/reviews`) to submit a review with line-level comments
- Cap to ~5 inline comments — over that and Bob is being noisy, not helpful

This is the extension that most makes Bob feel like a teammate rather than a robot. Worth the effort.

### 7. PR-description-aware review

The base lab only gives Bob the diff. The PR description usually tells you *why* the change exists — and the diff that doesn't match the description is where the bugs live:

- Fetch the PR body via the GitHub API and write it to `pr-description.txt`
- Tell the mode to read both files and explicitly flag mismatches: "PR says X, diff also does Y"
- Surface "missing description" or "description is just the title" as its own warning

### 8. Diff-classified change summary

The diff stat shows *which* files changed. Pre-classify them by glob and feed Bob structured input:

- `**/*.sql` / migrations → "schema change" group
- `**/Dockerfile*`, `**/*.yaml` under `k8s/` → "infra change"
- `pom.xml`, `package.json` → "dependency change"
- `**/test/**` → "test change"
- everything else → "code change"

Have the mode produce one bullet per group rather than per file. Drastically reduces noise on PRs that touch dozens of files for one logical reason.

### 9. Cross-reference with the linked Jira ticket

If the branch name or commit messages contain a Jira key:

- Use the `atlassian` MCP server (the same one Lab 5 wires up) to fetch the ticket
- Pass the ticket title, description, and acceptance criteria to Bob alongside the diff
- The mode evaluates whether the diff *actually addresses what the ticket says*. Surface gaps as a "Coverage" section

This is one of the most valuable code-review questions and the one most reviewers don't have time to ask.

### 10. Risk-band gating

Take the band Bob produces and act on it:

- High → set the GitHub commit status to `failure` (`POST /repos/:owner/:repo/statuses/:sha`) — blocks merge until a reviewer overrides
- Medium → status `pending` until a human acks
- Low → status `success`

Pair with idea 1 so the comment includes a "to override, comment `/bob override <reason>`" hint. Make sure the override path is auditable.

---

## Bigger swings (workshop-shaped extensions)

### 11. Two-pass review (triage → deep-dive)

The base mode tries to be both fast and thorough. Split it:

- **Pass 1** — current `pipeline-git-diff-overview`. Risk band, three-section output, fast
- **Pass 2** — only runs when Pass 1 returns `high`. New mode `pipeline-git-diff-deepdive`, gets the *full* diff plus the changed files' surrounding context, produces a long-form review

Cheaper than running deep-dive on every PR, more thorough than a single pass on the high-risk ones. Models the way a senior reviewer actually triages.

### 12. Reviewer assignment

Don't just review the PR — pick the human who should also look at it:

- Maintain a `CODEOWNERS`-style map (or read GitHub's own CODEOWNERS) of file globs → owner
- Have a new mode (`pipeline-pr-router`) read the diff stat and propose 1–2 reviewers from the matched owners
- Tag them in the PR comment, or use `POST /repos/:owner/:repo/pulls/:number/requested_reviewers`

The interesting bit is the tiebreaker logic — least-recently-reviewed, fewest-pending-reviews, on-call rotation. Encode that in the rules, not the model.

### 13. Test-coverage-aware review

If a PR adds production code without tests, the base mode might mention it; this extension makes it mechanical:

- Run a coverage delta in the pipeline (jacoco diff between `main` and `HEAD`)
- Pass the delta to Bob as `coverage-delta.txt`
- Mode rule: if any new branches are uncovered, automatic *medium* risk minimum, with the file/line list as a "Tests missing for" section

Pairs naturally with Lab 2's `java-unit-test-mode` — Bob can both flag the gap and (in a later push) write the test.

### 14. Architectural drift detection

The most expensive bugs aren't in any single file — they're in subtle architectural drift across files:

- Maintain a list of architectural rules (`controllers don't call repositories directly`, `nothing in `core/` imports from `web/``, etc.) in a checked-in file
- New mode (`pipeline-arch-review`) reads the diff plus the rules file, flags violations
- This is essentially a model-driven ArchUnit. Catches things lint can't

Worth doing only if your codebase actually has architectural rules worth enforcing. If it doesn't, this extension makes a great forcing function for writing them down.

### 15. PR review checklist for the human

Bob's review supplements the human reviewer; it doesn't replace them. Generate a checklist *for* the human:

- Per-file "things to look at first" pulled from the diff (`OrderService.java line 142 — new branch, no test`)
- Pulled directly into the PR description as a section ("## Reviewer checklist") via the GitHub API
- Reviewer ticks boxes as they go — review-as-conversation, not review-as-assertion

---

## A note on guardrails

Code review is an opinionated activity. Bob will sometimes be wrong, and "Bob said it was fine" is a bad reason to merge a bug. Keep that in mind:

- The base lab's mode is read-only. Most extensions add `mcp` (for GitHub/Jira/Slack tool calls). Stay disciplined about `alwaysAllow` — `create comment` is fine, `merge PR` is not
- Risk-band gating (idea 10) and reviewer assignment (idea 12) shift human accountability. Make sure the override paths are documented and auditable; "who can bypass Bob" matters more than "what Bob blocks"
- `pipeline-` prefixed modes are read-mostly by convention. If your extension introduces meaningful mutation (idea 1, 6, 10, 12), keep the alwaysAllow list narrow and document what the mode is allowed to write
- Inline comments and PR comments are public artifacts of your team's process. Tune the mode's tone explicitly — sarcasm and snark age badly when archived for years

---

If you build one of these and it works well, drop a `solution-` prefixed mode in `.bob/custom_modes.yaml` and a short paragraph in this file describing what it does and what to watch out for. The next workshop benefits.
