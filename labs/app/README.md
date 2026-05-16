# Application Labs

Two hands-on labs that show how IBM Bob fits into the day-to-day workflow of an application development team — code review and release engineering — using a Spring Boot order-service as the substrate.

## What's here

| Lab | File | What you do |
|---|---|---|
| **Lab 1 — Code Review with Bob** | [`lab1/LAB1_CODE_REVIEW.md`](lab1/LAB1_CODE_REVIEW.md) | Add a refund endpoint to the order-service, then run the diff through three review laps before commit: the built-in `/review` slash command, a custom standards-aware mode you build with Mode Writer, and the provided `software-security-reviewer` mode. Commit with a Bob-generated message and open the PR via `/create-pr`. |
| **Lab 2 — Semantic Versioning with Bob** | [`lab2/LAB2_SEMANTIC_VERSIONING.md`](lab2/LAB2_SEMANTIC_VERSIONING.md) | Walk through a baseline, a backward-compatible change, an accidental breaking change, and a third-party-dep breaking change. Bob acts as the release engineer — detects what kind of bump is needed and drafts release communications. |

Lab 1 → Lab 2 is the intended order. Lab 2 doesn't depend on Lab 1's code changes.

## Tech stack

- **App:** order-service (Spring Boot 3.2, Java 17, Maven, PostgreSQL 15)
- **Bob:** IDE only — no Jenkins or cluster setup required for these two labs
- **Other files in `lab1/`:** `software-security-reviewer.yaml` — the security review mode Lab 1 reuses in its third review lap

## Prerequisites

- Bob IDE installed and signed in
- Cloned working copy of this repo on a working branch (not `main`)
- `gh` CLI authenticated (Lab 1 uses it to post a PR comment) — `gh auth status` should show you logged in
- `mvn test` passes from `order-service/` before you start

## Related labs in adjacent tracks

- **Intro labs** — [`../intro-labs/`](../intro-labs/) for Bob fundamentals, BobShell, MCP, and custom-mode basics. Run these first if you've never used Bob.
- **SRE track** — [`../sre/`](../sre/) for the same Bob features applied to Jenkins pipeline stages instead of in-IDE workflows.
- **Handoff labs** — [`../handoff-labs/`](../handoff-labs/) for self-paced material on modes, MCP server building, and auto-recovery.
