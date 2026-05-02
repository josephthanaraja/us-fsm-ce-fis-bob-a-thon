# Lab 2 — Extension Ideas

Lab 2's base exercise gets you a `Unit Tests` stage that runs `mvn test`, publishes the JUnit XML to Jenkins, and has Bob diagnose any failures via `pipeline-test-failure-analyzer`. That's the floor. This doc collects extensions that take Bob from "explains what broke" to "actively helps you write better tests, fix flaky ones, and propose patches."

The base lab keeps Bob read-only on purpose — failure analysis shouldn't mutate code mid-build. Several extensions below relax that constraint *outside* the build (for example, by writing patches as artifacts the developer applies locally), which is a useful pattern: keep CI deterministic, but still let Bob do real work.

## Table of Contents

- [Easy wins (single-stage tweaks)](#easy-wins-single-stage-tweaks)
  - [1. Failure classification](#1-failure-classification)
  - [2. First-failure-only mode](#2-first-failure-only-mode)
  - [3. Coverage gap surfacing on success](#3-coverage-gap-surfacing-on-success)
  - [4. Annotate JUnit XML with Bob's analysis](#4-annotate-junit-xml-with-bobs-analysis)
  - [5. Flaky test surfacing](#5-flaky-test-surfacing)
  - [6. Dependency-bump correlation](#6-dependency-bump-correlation)
- [Medium-effort extensions (multi-stage or new mode)](#medium-effort-extensions-multi-stage-or-new-mode)
  - [7. Bob proposes a patch — as an artifact, not a commit](#7-bob-proposes-a-patch--as-an-artifact-not-a-commit)
  - [8. Mutation-testing analysis](#8-mutation-testing-analysis)
  - [9. Test-impact analysis](#9-test-impact-analysis)
  - [10. Test-quality review](#10-test-quality-review)
  - [11. Auto-generate tests for newly-added classes](#11-auto-generate-tests-for-newly-added-classes)
  - [12. Property-based test suggestions](#12-property-based-test-suggestions)
- [Bigger swings (workshop-shaped extensions)](#bigger-swings-workshop-shaped-extensions)
  - [13. Self-healing pipeline (with human gate)](#13-self-healing-pipeline-with-human-gate)
  - [14. Convert legacy JUnit 4 to JUnit 5](#14-convert-legacy-junit-4-to-junit-5)
  - [15. Cross-language test-failure analysis](#15-cross-language-test-failure-analysis)
  - [16. Performance regression detection](#16-performance-regression-detection)
  - [17. Coverage-trend dashboard](#17-coverage-trend-dashboard)
- [A note on guardrails](#a-note-on-guardrails)

---

## Easy wins (single-stage tweaks)

### 1. Failure classification

Right now Bob produces one summary for whatever failed. Different failure modes deserve different remediation, so split them:

- **Compilation error** — `mvn` exited non-zero before tests ran. Bob should focus on the source of the error, not pretend tests failed
- **Assertion failure** — actual logic bug. Standard Bob analysis applies
- **Environment failure** — Spring context didn't load, port binding, missing config. Bob should look at config files and the test's `@SpringBootTest` setup
- **Timeout / hang** — Bob looks at the test's I/O and threading

Add a small classifier step *before* `askBob` (parse the surefire XML for `<error>` vs `<failure>`, plus the message) and pass the classification into the prompt. The mode's rules can then steer the analysis differently per class.

### 2. First-failure-only mode

When 30 tests fail because one shared fixture broke, getting a 30-test analysis is overwhelming. Have the mode:

- Identify the *earliest* failure by file/line in the surefire output
- Produce a deep dive on just that one
- Add a one-line tail: "N other failures may be downstream of this — re-run after fix"

The rule for "earliest" matters — chronological isn't always right. Smallest test class, fewest dependencies, simplest setup is usually a better heuristic.

### 3. Coverage gap surfacing on success

The base lab only invokes Bob on failure. On success, surface what *isn't* tested:

- Run jacoco (or your tool of choice) and write the per-class coverage report to `coverage.txt`
- Even on a green build, call Bob with a "coverage triage" prompt — what classes have the lowest coverage, which uncovered branches look highest-risk, what tests would Bob suggest writing
- Archive `bob-coverage-suggestions.md` alongside the test analysis

Useful for catching "we're 90% green but the 10% is the actual business logic."

### 4. Annotate JUnit XML with Bob's analysis

Bob's analysis lives in a separate artifact. Make it show up in Jenkins's native test reports:

- After `askBob`, parse the analysis and inject the relevant summary into each `<failure>` element's text content (or as a sibling `<bob-analysis>` element if the JUnit consumer is forgiving)
- Re-write the XML before the `junit` step picks it up
- Result: clicking a failed test in Jenkins shows Bob's explanation inline, no need to dig into a separate artifact

### 5. Flaky test surfacing

Track per-test pass/fail history across builds:

- Persist results to a known location (Jenkins build artifact, or a small file in `s3://`/the workspace volume)
- On each run, identify tests that flipped pass→fail→pass over the last N builds and surface them as a "flaky watch list"
- Have Bob explicitly *not* propose code fixes for flaky tests — the right output is "this test is flaky, see history" rather than "the SUT is broken"

Heuristic, not perfect, but cheap to add.

### 6. Dependency-bump correlation

When tests fail right after a `pom.xml` (or `package.json`) change, that's almost always the cause. Make Bob aware:

- Check whether the diff against the previous green commit touched dependency files
- Pass that signal into the prompt as `recent-dep-changes.txt`
- The mode should mention the suspect dependency by name and suggest a downgrade-to-confirm step before assuming the bug is in the test code

---

## Medium-effort extensions (multi-stage or new mode)

### 7. Bob proposes a patch — as an artifact, not a commit

Don't let CI mutate code. *Do* let Bob propose a fix:

- New mode (`pipeline-test-failure-fixer`) — read-only on the build's source tree, but allowed to *write* a unified diff to `proposed-fix.patch`
- Archive the patch as a build artifact
- The developer pulls the artifact and applies it with `git apply proposed-fix.patch` if they like the proposal — fully reviewable, fully reversible

This is the safe version of "self-healing pipelines" — Bob does the work, the human stays in control.

### 8. Mutation-testing analysis

Coverage tells you *what* is executed; mutation testing tells you whether the assertions are *meaningful*:

- Run [pitest](https://pitest.org/) on the order-service in a separate pipeline stage (slow — only on `main` or nightly, not every PR)
- Pass the surviving-mutants report to a Bob mode and ask it to triage which mutants represent real test gaps vs. equivalent mutants
- Output goes to `bob-mutation-analysis.md`

This is a "ratchet up test quality over time" extension. Most teams that care about test quality don't run pitest because the output is overwhelming — Bob makes it triageable.

### 9. Test-impact analysis

For large test suites, running everything on every PR wastes time:

- Compute the diff against `main` (already done in Lab 1)
- Map changed source files → owning test classes (heuristic: same package, name matches `*Test.java`, or a maintained mapping file)
- Run only the impacted tests in a fast `Unit Tests (Impacted)` stage; run the full suite separately on a slower cadence
- Have Bob review the impact mapping and flag changes whose impact looks suspiciously narrow — e.g., a change to `OrderService.java` that doesn't pull in `OrderControllerTest.java`

### 10. Test-quality review

Beyond "do the tests pass," is the *test code itself* any good? Have a mode review the test files Bob generated (or that the developer wrote):

- Read existing `*Test.java` files
- Flag smells: assertions on mocks (`verify` without `assertThat`), tests with no assertions, test names that don't describe behavior, over-mocking, hidden coupling between tests
- Output is read-only triage, not a rewrite — pair with idea 7 if you want patches

### 11. Auto-generate tests for newly-added classes

Lab 2's `java-unit-test-mode` lives in the IDE. Move (a copy of) it into the pipeline:

- Detect classes added in the diff (`git diff --name-status origin/main..HEAD | grep '^A.*\.java$'`) that don't have a corresponding `*Test.java`
- Have Bob produce the missing test classes as artifacts (`generated-tests/<ClassName>Test.java`)
- Don't commit them — the developer reviews and pulls

The base IDE mode is opinionated about JUnit 5 + Mockito, which is what you want for consistency. Don't fork the rules between the IDE and pipeline modes — share them via a common rules directory.

### 12. Property-based test suggestions

For pure functions and simple data transformers, property-based tests (jqwik for JVM) catch edge cases unit tests miss. Have Bob:

- Read a class and identify pure-ish methods (no I/O, no side effects, deterministic)
- Suggest jqwik properties — invariants the method should satisfy regardless of input
- Output goes to `bob-property-suggestions.md`, the developer decides which ones to keep

Niche, but high-value when it lands.

---

## Bigger swings (workshop-shaped extensions)

### 13. Self-healing pipeline (with human gate)

Combine ideas 1, 2, and 7 into a real workflow:

- Test fails → Bob classifies → Bob proposes patch → patch is committed to a `bob/auto-fix-${BUILD}` branch → PR is opened with Bob as the author and the developer as reviewer
- Pipeline does **not** automerge. The developer reviews and merges if it's right
- Track Bob's accept rate over time as a quality signal — if patches consistently get rejected, the modes need tuning

The interesting question here is the failure modes: Bob proposes a fix that masks a real bug, and a tired reviewer rubber-stamps it. Document the review checklist and keep the patch scope tight (single test, single assertion).

### 14. Convert legacy JUnit 4 to JUnit 5

If your codebase has a JUnit 4 long tail, this is a perfect Bob job:

- Mode reads a JUnit 4 test file, produces a JUnit 5 equivalent
- Run as a one-shot per file, not on every CI build — set up a `migrate-tests` Jenkins job that processes a list
- Output is a patch artifact; developer reviews and applies

The migration rules are mostly mechanical (`@Before` → `@BeforeEach`, `@Test(expected=...)` → `assertThrows`, `@Rule` → `@ExtendWith`). Encode them in the mode's rules so the model isn't reinventing the conversion every file.

### 15. Cross-language test-failure analysis

The base mode is Java-specific. If your real pipeline runs Python, Node, Go services too, generalize:

- Per-language input parsers — pytest XML, Jest XML, `go test -json`
- Per-language Bob mode (`pipeline-test-failure-analyzer-python`, etc.) — different idioms, different common failures
- Shared rules: classification, deduplication, output format

The key insight is that the *output format* should be language-agnostic so downstream consumers (PR comment, dashboard) don't need to care which stack failed.

### 16. Performance regression detection

Tests that pass but are *slower* than yesterday are a real signal:

- Capture per-test runtime from surefire (`<testcase time="...">`)
- Diff against the previous green build's runtimes
- A Bob mode reviews regressions, separating "infrastructure noise" from "actual code that got slower"
- Surface as `bob-perf-deltas.md`

This is the "wide and shallow" sibling to mutation testing — cheap to compute, occasionally surfaces real problems.

### 17. Coverage-trend dashboard

One-build-at-a-time analysis only goes so far. Aggregate over time:

- Push per-build coverage + test-count + failure-rate to a time-series store (Prometheus, InfluxDB, or just append to a CSV in object storage)
- Build a Grafana dashboard
- A weekly Bob job reads the dashboard data and writes a "what changed in test health this week" digest to a Slack channel

Most of the work here is plumbing, not Bob. But the digest is the kind of thing nobody on the team would write by hand, which is exactly when Bob earns its keep.

---

## A note on guardrails

The base lab is conservative for a reason — a build that auto-rewrites your code is a build you've stopped trusting. Most of the higher-blast-radius extensions above sit *outside* the inner CI loop (artifacts, separate jobs, gated PRs) for that reason. Stay disciplined about that boundary:

- The `pipeline-test-failure-analyzer` mode is `read` only. If you add an `edit` group, rename the mode and document why — `pipeline-test-failure-fixer` makes the elevated permission scan-visible
- Patches that Bob proposes (idea 7, 13) are not commits Bob made. Keep them as artifacts or branches that always go through human review. "Bob committed it" is a fine description of what happened; it's a bad description of who's accountable
- Self-healing extensions (idea 13) work or fail on the strength of the review checklist. Treat the checklist as part of the rules, not as folklore — if it's not written down, the next reviewer will skip it
- Coverage-driven test generation (idea 11) is satisfying but produces tests that test what the code *does*, not what the code *should* do. Tag generated tests so future maintainers know to scrutinize them harder than human-written ones

---

If you build one of these and it works well, drop a `solution-` prefixed mode in `.bob/custom_modes.yaml` and a short paragraph in this file describing what it does and what to watch out for. The next workshop benefits.
