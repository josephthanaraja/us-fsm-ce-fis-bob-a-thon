# Bob Pipeline Entry Points

All possible places Bob can be integrated into the Jenkins pipeline. Each entry point follows the same pattern: collect context from the pipeline stage, send it to Bob via `askBob()`, use the response.

## Entry Points

| # | Entry Point | Pipeline Stage | When it runs | What Bob does | Input to Bob | In our solution? | In other lab? |
|---|---|---|---|---|---|---|---|
| 1 | **PR Analysis** | After Checkout | Every build | Summarizes the PR, identifies risks, tells reviewers what to focus on | Changed files list + diff stat | Yes | Yes |
| 2 | **Lint Failure Diagnosis** | Lint (Step 2) | Only on failure | Explains checkstyle violations and how to fix them | Raw checkstyle output | No | No |
| 3 | **PCI Compliance Diagnosis** | PCI Compliance (Step 3) | Only on failure | Explains why code violates PCI DSS, cites specific requirements, provides fix | Raw PCI checkstyle output | Yes | No (they don't have PCI stage) |
| 4 | **Test Failure Diagnosis** | Unit Tests (Step 4) | Only on failure | Identifies which tests failed, root cause in app code, suggests fix | Last 50 lines of test output | Yes | Yes |
| 5 | **Security Scan Triage** | Security Scan (Step 5) | Only on HIGH/CRITICAL | Explains each CVE, whether it's exploitable in context, PCI impact, fix version | Trivy scan results | Yes | Yes |
| 6 | **DCR Generation** | Approval Gate (Step 6) | Every build | Writes a formal Deployment Change Request with risk assessment, validation evidence, rollback plan, recommendation | All previous stage results combined | Yes | No (they don't have approval gate) |
| 7 | **Full Code Review** | After Security Scan | Every build | Reviews full diff for bugs, security issues, best practices | Full git diff (truncated) | No | Yes |
| 8 | **Smoke Test Triage** | Smoke Tests (Step 9) | Only on failure | Analyzes which services are unhealthy, whether to rollback | Smoke test script output | Yes | No (they don't have smoke tests) |
| 9 | **Change Control Update** | After Smoke Tests (Step 10) | Every build | Writes a status update for the DCR with deployment results, whether ticket can be closed | Deploy status + smoke test results | Yes | No |

## What the other lab covers (their 3 client pain points)

| Pain Point | Their entry point | Our equivalent |
|---|---|---|
| "We need AI to understand PRs before we review them" | #1 PR Analysis | #1 — same |
| "When tests fail, developers waste time reading logs" | #4 Test Failure Diagnosis | #4 — same |
| "Security scan output is overwhelming, we don't know what to fix first" | #5 Security Scan Triage | #5 — same |

## What we add that they don't have

| Entry Point | Why it matters for SRE |
|---|---|
| #3 PCI Compliance | Regulated environment — code-level compliance checks, not just CVEs |
| #6 DCR Generation | Formal change management — Bob writes the ticket, not a human |
| #8 Smoke Test Triage | Post-deploy verification — Bob recommends rollback if services are unhealthy |
| #9 Change Control Update | Closes the loop — DCR ticket updated with deployment outcome |

## Reliability notes

| Entry Point | Reliability | Notes |
|---|---|---|
| #1 PR Analysis | High | Always runs, deterministic input (git diff) |
| #3 PCI Compliance | High | Deterministic — custom checkstyle rules we control, same result every time |
| #4 Test Failure | High | Deterministic — unit tests either pass or fail |
| #5 Security Scan | Medium | Depends on Trivy CVE database download + which CVEs exist at the time |
| #6 DCR Generation | High | Always runs, input is just the collected stage results |
| #7 Full Code Review | High | Always runs, deterministic input (git diff) |
| #8 Smoke Test Triage | High | Deterministic — curl to health endpoints |
| #9 Change Control Update | High | Always runs, input is deploy status |
