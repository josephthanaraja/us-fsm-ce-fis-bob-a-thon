# Lab 1 — Code Review with Bob

## Table of Contents

- [Overview of Lab 1](#overview-of-lab-1)
  - [The story](#the-story)
  - [What you'll build in Lab 1](#what-youll-build-in-lab-1)
  - [What you'll reuse from the repo](#what-youll-reuse-from-the-repo)
- [Before you start](#before-you-start)
- [Part 1 — Capture your team's standards as Bob rules](#part-1--capture-your-teams-standards-as-bob-rules)
- [Part 2 — Build the refund feature in Code mode](#part-2--build-the-refund-feature-in-code-mode)
- [Part 3 — Pre-commit gauntlet, lap 1: built-in `/review`](#part-3--pre-commit-gauntlet-lap-1-built-in-review)
- [Part 4 — Pre-commit gauntlet, lap 2: standards-aware review with a custom mode](#part-4--pre-commit-gauntlet-lap-2-standards-aware-review-with-a-custom-mode)
- [Part 5 — Pre-commit gauntlet, lap 3: security review](#part-5--pre-commit-gauntlet-lap-3-security-review)
- [Part 6 — Commit with a Bob-generated message](#part-6--commit-with-a-bob-generated-message)
- [Part 7 — Open the PR and post the security review](#part-7--open-the-pr-and-post-the-security-review)
- [Stuck?](#stuck)

---

## Overview of Lab 1

You'll add a real feature to the order-service, then put the diff through the same review gauntlet your team should be running before any commit hits `main`. Each lap of the gauntlet is a different Bob surface — built-in slash command, custom mode you write, and a security mode provided in the repo — and each one catches things the others miss.

### The story

You're on the order-service team. Java 17, Spring Boot 3.2, PostgreSQL, PCI-scoped. Remember the refund endpoint ticket you created in the morning intro lab? Customer support needs that endpoint live so they can issue refunds on existing orders. The ticket has acceptance criteria attached.

You'll pull the ticket down with the Jira MCP server you configured this morning, deliver to spec, then run the diff through three reviewers before you commit — because in this codebase the cost of a bug shipping is real money and an audit finding.

### What you'll build in Lab 1

1. **Workspace rules** in `.bob/rules/` — your team's coding standards (logging, money handling, no hardcoded secrets, commit message convention) written once. Every Bob mode that runs in this workspace reads them, including `/review` and the commit-message generator.

2. **The refund feature itself** — POST `/api/orders/{id}/refund`, status transition to `REFUNDED`, tests. Built in **Code** mode against the Jira ticket. The spec is intentionally loose; the gaps are what review is for.

3. **An `orders-code-reviewer` custom mode** — built with **Mode Writer**, rules in `.bob/rules-orders-code-reviewer/`. Pinned output shape, domain-specific concerns (audit logging, `@Transactional`, money comparisons, PII in logs).

4. **Three review laps** before commit:
   - **Lap 1** — built-in `/review` (broad strokes, populates Bob Findings)
   - **Lap 2** — your `orders-code-reviewer` mode (your standards)
   - **Lap 3** — the provided `software-security-reviewer` mode (vulnerability-focused)

5. **The PR** — created with `/create-pr`, with the security review posted as an inline PR comment via the `gh` CLI. The saved markdown doubles as a wiki-ready review artifact.

### What you'll reuse from the repo

- **The `software-security-reviewer` mode** in `.bob/custom_modes.yaml`, with its rules in `.bob/rules-software-security-reviewer/` — same security review used elsewhere in this repo, applied here pre-merge instead of in CI.
- **The pre-existing `OrderService.java`** has its own pile of issues (hardcoded API key, MD5, `java.util.Random`, `printStackTrace`). Your diff only touches part of that file; the security lap surfaces the rest as follow-up tickets.

---

## Before you start

- [ ] You're on a working branch, not `main` (e.g. `lab1-refunds`)
- [ ] `gh auth status` shows you're logged into GitHub
- [ ] `mvn test` passes from `order-service/`
- [ ] You have the **ticket key** from the refund ticket you created in the morning intro lab (the one Jira assigned when Bob created it — e.g. `OS-7`, `REF-12`, etc.). If you didn't write it down, jump back to Settings → MCP → atlassian, switch to Advanced mode, and ask: `Use jira_search to find the refund ticket I created earlier.`

---

## Part 1 — Capture your team's standards as Bob rules

Real teams have coding standards that aren't fully expressible in a linter — "don't log customer names," "every status transition emits an audit log," "money is always `BigDecimal`." A Bob rules file makes those standards visible to every mode that runs in the workspace, including `/review` and the commit-message generator. You write them once, every reviewer reads them.

Create `.bob/rules/coding-standards.md`:

```markdown
# Order Service Coding Standards

## Logging
- Use SLF4J `logger.info / warn / error`. Never `System.out` or `System.err`.
- Never log customer PII (customerName, email, account id, card number) — not at any level.
- Use `logger.error("message", ex)`, never `e.printStackTrace()`.

## Money handling
- All amounts use `BigDecimal`. Compare with `.compareTo()`, never `==` or `.equals()`.
- Never `double` or `float` for money.

## Configuration
- No hardcoded secrets, IP addresses, URLs, or business thresholds.
- Externalize via `@Value("${...}")` and `application.properties`.

## Persistence and transactions
- Service-layer methods that perform multiple writes must be `@Transactional`.
- Status transitions on `Order` must be validated and audit-logged.

## Crypto
- Never `java.util.Random` for security-sensitive values; use `SecureRandom`.
- Never MD5 or SHA-1; use SHA-256 or stronger.

## Commit messages
- Conventional Commits: `feat | fix | refactor | test | docs | chore`.
- Subject line: `<type>(orders): [ORD-XXXX] <description>` — Jira ticket required.
- Subject ≤ 72 chars. Body explains the *why*, not the *what*.
```

These rules apply everywhere Bob runs in this workspace. You don't have to restate them in any prompt for the rest of the lab.

---

## Part 2 — Pull the ticket from Jira and build the feature

Remember the refund ticket you created in the morning intro lab? Time to pull it down and implement it.

Switch to **🤖 Advanced** mode (so MCP tools are available), start a new task, and paste — replacing `<your-ticket-key>` with the actual key Jira assigned to your refund ticket:

```
Use jira_get_issue to fetch <your-ticket-key>. Then switch to Code mode and implement the feature described in the acceptance criteria. Update the Order model, OrderService, OrderController, and add tests.
```

Bob calls `jira_get_issue` on the Atlassian MCP server, reads the description and acceptance criteria back, then proposes the switch to **💻 Code** mode and delivers the feature against the ticket. Approve the mode switch when prompted.

When Bob finishes:

```bash
cd order-service && mvn test
```

The build should pass. **Don't commit yet.** The interesting part of this lab is what the spec didn't ask for — audit logging, idempotency on retries, authorization, validation that the refund amount doesn't exceed the original — and what each review lap catches. Real Jira tickets don't spell these out; that's what code review is for.

---

## Part 3 — Pre-commit gauntlet, lap 1: built-in `/review`

`/review` is Bob's built-in code review command. With no arguments, it analyzes uncommitted changes in your working tree.

In the same task, type:

```
/review
```

Bob scans the diff and populates the **Bob Findings** panel. Expect things like:

- Missing tests for failure paths (refunding an already-refunded order, refund amount over original)
- Magic numbers (e.g. a hardcoded refund window or threshold)
- Possible NPEs in the request-body parsing
- Broad `catch (Exception e)` blocks

Each finding has **Fix with Bob** / **Mark as Resolved** / **Dismiss**. Use **Fix with Bob** on the ones you agree with; dismiss the stylistic noise.

`/review` is the broad pass. It picks up `.bob/rules/coding-standards.md` automatically because workspace rules apply to every mode. The next two laps tighten the focus.

---

## Part 4 — Pre-commit gauntlet, lap 2: standards-aware review with a custom mode

`/review` won't always emphasize your domain's specific concerns — audit logging on money movement, `@Transactional` discipline, money comparisons. A custom code-review mode pins the lens.

Switch to **🪄 Mode Writer** in a new task and paste:

```
Write a custom mode with slug `orders-code-reviewer`. Append it to @.bob/custom_modes.yaml — don't overwrite anything else.

Job: code review specialist for our Java/Spring Boot order-service. Focus on:
- Audit logging on every status transition and money movement
- @Transactional coverage for service methods that perform multiple writes
- BigDecimal-only money handling, .compareTo() not == or .equals()
- No PII (customerName, email, card data) in logs at any level
- Authorization checks for actions that move money (refund, cancel)
- Idempotency guards on operations that can be retried (refunds, payments)

Read @.bob/rules/coding-standards.md and apply those standards. Cite file:line for every finding. Group findings by severity: BLOCKER, MAJOR, MINOR. End with a one-line verdict: "READY TO MERGE" or "BLOCKED ON N FINDINGS".

Tool groups: read only.
```

Mode Writer creates the mode entry in `.bob/custom_modes.yaml` and a `.bob/rules-orders-code-reviewer/` directory with rules that constrain the output shape. Read-only is deliberate — review modes should report and recommend, not edit.

**Restart Bob IDE** so the new mode appears in your mode dropdown.

In a new task, switch to **Orders Code Reviewer** and paste:

```
Review the uncommitted refund changes against our standards.
```

This pass should surface things `/review` glossed over — missing audit log on the refund, no `@Transactional`, a `customerName` in a log line, no idempotency guard, no validation that refund amount ≤ original order amount. Apply the fixes you agree with (in Code mode — Orders Code Reviewer is read-only).

---

## Part 5 — Pre-commit gauntlet, lap 3: security review

The first two laps covered standards and quality. The third lap is about exploitable risk. The repo already includes a **🛡️🔐 Software Security Reviewer** mode (in `.bob/custom_modes.yaml`, rules in `.bob/rules-software-security-reviewer/`). Reuse it.

In a new task, switch to **Software Security Reviewer** and paste:

```
Review the uncommitted changes plus any pre-existing code in OrderService.java the diff context touches. Focus on:
- Money-movement endpoints without authorization
- PII / cardholder data exposure in logs or error responses
- Weak cryptography (MD5, SHA-1, java.util.Random for security-sensitive values)
- Hardcoded secrets in surrounding code

Output the standard CRITICAL / HIGH / MEDIUM / LOW findings with code patches. Save the result to bob-security-review.md.
```

This lap widens the lens beyond your diff. The pre-existing `OrderService.java` has hardcoded `LEGACY_API_KEY` and `BACKUP_DB_PASSWORD`, MD5 in `generateOrderVerificationCode()`, `Random` in `generateTrackingNumber()`, and `printStackTrace()` in two catch blocks. The security mode finds them all and proposes patches.

You don't have to fix every pre-existing issue in this PR — but you now have a saved review markdown to file as follow-up tickets, and you'll post it on the PR in Part 7 so reviewers see the full picture.

---

## Part 6 — Commit with a Bob-generated message

Stage what you accepted from the three laps:

```bash
git add order-service/ .bob/
```

In the **Source Control** panel, click the **sparkle icon** next to the commit message box. Bob reads the staged diff, your branch name, and `.bob/rules/coding-standards.md` — including the commit message convention you wrote in Part 1.

Expected first suggestion (something like):

```
feat(orders): [<your-ticket-key>] add refund endpoint with audit logging

- POST /api/orders/{id}/refund issues a refund and transitions the order to REFUNDED
- Validates refund amount against original order total
- Emits audit log entry on every refund
- Adds tests for happy path, already-refunded, and over-refund cases
```

If the first one misses something, click the sparkle again for an alternative. Edit by hand to add specifics. Then commit and push:

```bash
git push -u origin lab1-refunds
```

---

## Part 7 — Open the PR and post the security review

In a new task in any mode, type:

```
/create-pr
```

Bob asks you to confirm the base branch (pick `main`), generates a PR title and description from the commit history and diff, and applies your project's PR template if one exists at `.github/pull_request_template.md`. Confirm and Bob creates the PR via `gh`, returning the link in chat.

Now post the security review as an inline PR comment so reviewers see the full risk picture, not just the diff. Grab the PR number:

```bash
gh pr view --json number -q .number
```

Then post `bob-security-review.md` (saved in Part 5) as a comment:

```bash
gh pr comment <PR-number> --body-file bob-security-review.md
```

The PR now carries:

- **What changed** — the description Bob generated from the diff and commits (`/create-pr`)
- **How risky it is** — the security review markdown posted as a comment (Part 5 + `gh pr comment`)
- **Which standards it follows** — the commit message convention enforced by `.bob/rules/coding-standards.md` (Part 6)

That's a complete pre-merge review record, produced by one slash command, one custom mode you built, and one mode the repo provided. The same `bob-security-review.md` doubles as a wiki-ready artifact — drop it into your team wiki and it's already formatted.

---

## Stuck?

- **`/review` says "no changes detected".** It reviews uncommitted changes by default. If you committed early, run `/review main` to compare your branch against `main` instead.

- **The `orders-code-reviewer` mode doesn't appear in the dropdown.** Custom modes load at IDE startup. Restart Bob IDE. Confirm the mode exists: `grep "orders-code-reviewer" .bob/custom_modes.yaml`.

- **Commit message generator doesn't include the Jira ticket prefix.** The rule in `.bob/rules/coding-standards.md` may be too vague. Open it and make the format explicit: `<type>(orders): [ORD-XXXX] <description>`. Click the sparkle again — Bob re-reads the rules every time.

- **The custom mode produces a wall of text instead of structured findings.** The rules in `.bob/rules-orders-code-reviewer/` aren't constraining output enough. Re-open Mode Writer and tighten — explicit BLOCKER/MAJOR/MINOR sections, file:line citation required, one-line verdict at the end.

- **`gh pr comment` fails with "must specify --body or --body-file".** The security review markdown wasn't saved. Re-run the Part 5 prompt with an explicit instruction to write the output to `bob-security-review.md`, then verify with `ls -lh bob-security-review.md`.

- **`/create-pr` fails with auth errors.** Run `gh auth status` to confirm you're logged in. If not, `gh auth login` and try again.

- **You want to start over.** The lab makes only additive changes. Reset with `git checkout -- order-service/ .bob/ && rm -f .bob/rules/coding-standards.md bob-security-review.md && rm -rf .bob/rules-orders-code-reviewer/`. The `orders-code-reviewer` mode entry will still be in `.bob/custom_modes.yaml` — remove it by hand or with another Mode Writer prompt.

---

When you're ready, open [LAB2_SEMANTIC_VERSIONING.md](../lab2/LAB2_SEMANTIC_VERSIONING.md).
