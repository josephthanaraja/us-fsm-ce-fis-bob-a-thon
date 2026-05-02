# Lab 5 — Extension Ideas

Lab 5's base exercise gets you to a working DCR stage that mirrors a digest into Jira. That's the floor, not the ceiling. This doc collects extensions you can layer on if you finish early, want to take Lab 5 home, or are looking for a "real" project to wire Bob into your team's workflow.

Most of these reuse the same `pipeline-dcr-jira-reporter` mode (or a near-cousin of it) — the heavy lifting is in deciding what behavior is safe to automate and what should still pause for a human.

## Table of Contents

- [Easy wins (single-stage tweaks)](#easy-wins-single-stage-tweaks)
  - [1. Idempotent Jira comments](#1-idempotent-jira-comments)
  - [2. Create a Jira ticket when none is referenced](#2-create-a-jira-ticket-when-none-is-referenced)
  - [3. Slack notification alongside Jira](#3-slack-notification-alongside-jira)
  - [4. Risk-band-driven Jira priority](#4-risk-band-driven-jira-priority)
  - [5. Roll up artifacts from earlier stages](#5-roll-up-artifacts-from-earlier-stages)
- [Medium-effort extensions (multi-stage or new mode)](#medium-effort-extensions-multi-stage-or-new-mode)
  - [6. Approvals workflow with input step](#6-approvals-workflow-with-input-step)
  - [7. Multi-server MCP composition](#7-multi-server-mcp-composition)
  - [8. Diff-aware DCR](#8-diff-aware-dcr)
  - [9. Rollback plan from history](#9-rollback-plan-from-history)
  - [10. DCR diffs across builds](#10-dcr-diffs-across-builds)
- [Bigger swings (workshop-shaped extensions)](#bigger-swings-workshop-shaped-extensions)
  - [11. Convert the DCR to a real release-management workflow](#11-convert-the-dcr-to-a-real-release-management-workflow)
  - [12. Compliance / audit-friendly DCR](#12-compliance--audit-friendly-dcr)
  - [13. Contributor-side DCR preview](#13-contributor-side-dcr-preview)
  - [14. DCR as a PR-blocking gate](#14-dcr-as-a-pr-blocking-gate)
- [A note on guardrails](#a-note-on-guardrails)

---

## Easy wins (single-stage tweaks)

### 1. Idempotent Jira comments

The base lab appends a fresh comment on every build, which means a chatty branch fills the ticket with duplicates. Smarter behavior:

- Tag each comment with a hidden marker, e.g., a leading `<!-- bob-dcr-build-${BUILD_NUMBER} -->`
- Before posting, `jira_search` for existing comments on the ticket containing `<!-- bob-dcr-build-` and skip the post if one for the current build already exists
- Or, if you want one rolling comment per branch: search for `<!-- bob-dcr-branch-${BRANCH_NAME} -->`, edit it via the Jira REST API if found, post fresh otherwise

### 2. Create a Jira ticket when none is referenced

The base lab deliberately refuses to create tickets without an explicit branch reference. Lift that restriction:

- Add `jira_create_issue` to the `alwaysAllow` list in `.bob/mcp.json`
- Update the mode's rules to fall back to creation when `dcr-context.txt` has an empty `JIRA_KEY=`
- Configure a default project key (e.g., `RELEASE`) and issue type (e.g., `Deployment`) in the mode's rules so the model isn't guessing
- Write the new ticket key back into the workspace as `dcr-created-key.txt` and archive it — future builds on the same branch should reuse that key

### 3. Slack notification alongside Jira

Add a second MCP server entry to `.bob/mcp.json` for Slack (`@modelcontextprotocol/server-slack` or similar) and update the mode to post a one-line summary to a release channel when the DCR is filed. Keep the message tight — channel link + ticket key + risk band, nothing more. The mode's rules should explicitly forbid pasting the full DCR into Slack.

### 4. Risk-band-driven Jira priority

Have the mode read its own risk assessment back out of `deployment-change-request.md` and set the Jira ticket's priority via `jira_update_issue` based on the band:

- High → `Critical`
- Medium → `Major`
- Low → `Minor`

Add `jira_update_issue` to `alwaysAllow`. This is the first time you're letting the pipeline mutate ticket *state*, not just append text — review what the rules say about it carefully before turning it on.

### 5. Roll up artifacts from earlier stages

The base lab references `bob-pr-review.md` and `bob-test-analysis.md` if they exist, but doesn't fail loudly if they don't. Tighten this:

- In the `DCR` stage, fail fast (or warn loudly in the banner) if the expected artifacts are missing — that's a sign Lab 1/2 stages were skipped or broken
- Add a "Pipeline Health" section to the DCR template that explicitly reports which earlier-stage artifacts were available

---

## Medium-effort extensions (multi-stage or new mode)

### 6. Approvals workflow with input step

After Bob writes the DCR, gate the rest of the pipeline behind a Jenkins `input` step:

- DCR posts to Jira
- Pipeline pauses with a "Approve deployment?" prompt referencing the ticket key and Jenkins build link
- A reviewer clicks Approve in Jenkins → pipeline continues to a (currently nonexistent) `Deploy` stage
- Reject → mode posts a follow-up Jira comment ("Deployment rejected by ${user} at ${timestamp}") and the pipeline ends FAILURE

This is the natural lead-in to a sixth lab if anyone wants to write one — actual deployment to the per-user namespaces that the instructor setup already provisions.

### 7. Multi-server MCP composition

Add a second mode (`pipeline-dcr-multi-target-reporter`) that fans the same DCR out to multiple destinations:

- Jira (existing)
- Confluence — append the DCR to a "Releases" parent page via `confluence_create_page`
- GitHub — post the DCR digest as a PR comment via the GitHub MCP server
- Email — post via an email MCP server (or, more cleanly, a webhook receiver you control)

Each target gets its own MCP server registration in `.bob/mcp.json`. The mode's rules should make the failure isolation explicit: if Confluence is down, Jira and GitHub still get the report. This is where the "MCP server is unreachable, fail open with a clear log" rule from the base lab really starts to earn its keep.

### 8. Diff-aware DCR

The base lab gives Bob the diff *stat* (`git diff --stat`). Extensions:

- Hand Bob the **full diff**, but with a token budget — write the diff to `dcr-fulldiff.txt`, count lines, and either truncate to the top-N most-changed files or fall back to stat-only if the diff is enormous
- Pre-classify hunks by file glob: `**/*.sql` → "schema change" section, `**/Dockerfile*` → "infra change", `**/pom.xml`, `**/package.json` → "dependency change". The mode can use these classifications to populate the DCR's "Changes" section with structure rather than relying on the model's guess
- Detect breaking-change markers in commit messages (`BREAKING CHANGE:` per Conventional Commits) and surface them in the Risk section automatically

### 9. Rollback plan from history

The Rollback Plan section in the base lab is currently the model's best guess. Make it grounded:

- Pre-compute the previous deploy's commit SHA (e.g., the SHA tagged by the most recent successful build of `main`)
- Provide that SHA to the mode as `dcr-previous-sha.txt`
- Have the mode's rules require the rollback section to start with the literal `git revert ${PREVIOUS_SHA}..HEAD` (or whatever fits your team's rollback protocol) before adding any narrative

This turns the section from "vibes" into something a release manager can copy-paste under pressure.

### 10. DCR diffs across builds

When the same branch is rebuilt, generate a *delta* DCR — what changed since the last successful build, not what changed since `main`:

- The pipeline already archives `deployment-change-request.md` per build. Pull the previous artifact via the Jenkins API
- Diff old vs. new and have Bob produce a "Since last build" section that explicitly calls out commits added, risk re-assessments, and test result deltas
- Posting a delta as a Jira comment (vs. the full DCR every time) is much more readable for a long-lived branch

---

## Bigger swings (workshop-shaped extensions)

### 11. Convert the DCR to a real release-management workflow

Combine ideas 1, 2, 4, and 6 into a single stage that:

- Creates a Jira "Deployment" ticket on the first push to a branch
- Reuses that ticket on every subsequent push, editing rather than appending
- Sets priority from risk band
- Transitions the ticket through `To Do → In Review → Approved → Deployed` based on pipeline state and human input
- Posts a final closing comment with the prod commit SHA on a successful deploy

This is essentially "what release engineering does manually for every deploy" automated end-to-end. Perfectly within Bob's reach if you split the responsibility correctly between the mode (decisions) and the pipeline (state transitions, retries).

### 12. Compliance / audit-friendly DCR

For regulated environments, the DCR needs to be more than a friendly summary:

- Add a `Compliance` section with named approvers, security review status, and links to the relevant change-management policy
- Sign the DCR — write a SHA-256 hash of `deployment-change-request.md` to `deployment-change-request.md.sha256`, archive both, and include the hash in the Jira comment
- Mirror the DCR + hash to an immutable store (S3 with object lock, or an internal compliance bucket) for audit retention
- Have the mode refuse to post to Jira if any required compliance field is missing

This is one of those extensions where the value isn't in code complexity — it's in getting the rule structure right so the mode reliably enforces a policy a human would otherwise eyeball.

### 13. Contributor-side DCR preview

Wire the same mode into a pre-push hook (or an IDE command) so a developer can run Bob locally before pushing and see what their DCR will look like. Same mode, same `mcp.json`, just a different invocation point. The IDE already has `${JIRA_*}` available in the developer's local environment for personal use, so the credential plumbing is free. This closes the loop on the "no surprises in CI" idea — by the time the pipeline runs, the developer has already seen and tuned the report.

### 14. DCR as a PR-blocking gate

Take the risk band the mode produces and gate the merge:

- Risk = High → set the GitHub status check to failure unless an override label is present
- Risk = Medium → require a review from the release-management group
- Risk = Low → green by default

Implementing this means adding the GitHub MCP server (or the GitHub Status API directly via curl) and reading the risk band back out of the DCR. The interesting design question is who owns the override — a Jira transition, a GitHub label, a Jenkins parameter? Pick one, document it in the mode's rules, stick to it.

---

## A note on guardrails

Every extension above is technically possible. Not all of them are wise to deploy in a shared workshop environment. When in doubt:

- Keep `alwaysAllow` short. Adding tools makes the mode more capable *and* makes accidents larger. If you're unsure, leave the tool out and take the interactive prompt hit — yes, it'll fail in CI, but at least it fails loudly instead of silently mutating production state
- Treat MCP server credentials with the same care as the Bob API key. Kubernetes Secret, `secretKeyRef` mount, no plaintext in `mcp.json`, no logs that print env vars
- Distinguish between "Bob writes a file" (cheap to undo) and "Bob mutates an external system" (expensive to undo). Most of these extensions blur that line — make sure the mode's rules don't
- The `pipeline-` prefix on mode slugs is a convention for read-mostly CI modes. If your extension introduces non-trivial mutation (idea 11, idea 14), consider a different prefix (e.g., `release-` or `gated-`) to make the higher-blast-radius modes scan-visible in the modes file

---

If you build one of these and it works well, drop a `solution-` prefixed mode in `.bob/custom_modes.yaml` and a short paragraph in this file describing what it does and what to watch out for. The next workshop benefits.
