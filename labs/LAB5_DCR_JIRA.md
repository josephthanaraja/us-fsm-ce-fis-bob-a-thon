# Lab 5 — DCR Generation + Jira MCP Reporting with Bob

## Table of Contents

- [Overview of Lab 5](#overview-of-lab-5)
  - [What you'll build in Lab 5](#what-youll-build-in-lab-5)
  - [What you'll reuse from Labs 1 & 2](#what-youll-reuse-from-labs-1--2)
- [Before you start](#before-you-start)
- [Part 1 — Register the Jira MCP server in `.bob/mcp.json`](#part-1--register-the-jira-mcp-server-in-bobmcpjson)
  - [Key characteristics of this MCP registration](#key-characteristics-of-this-mcp-registration)
  - [Edit `.bob/mcp.json` directly](#edit-bobmcpjson-directly)
- [Part 2 — Create the `pipeline-dcr-jira-reporter` custom mode](#part-2--create-the-pipeline-dcr-jira-reporter-custom-mode)
  - [Key characteristics of this mode](#key-characteristics-of-this-mode)
- [Part 3 — Add the `DCR` stage to your Jenkinsfile](#part-3--add-the-dcr-stage-to-your-jenkinsfile)
- [Part 4 — Push and watch](#part-4--push-and-watch)
- [Stuck?](#stuck)

---

## Overview of Lab 5

Lab 5 is the most involved lab in the workshop. You'll do three things at once: generate a **Deployment Change Request (DCR)** report from the branch, wire **Bob up to a Jira MCP server** so it can act on that report, and add a `DCR` stage to your Jenkinsfile that ties them together.

Up to this point, every Bob mode you've created has been a **read-only analyst** — Bob looks at code/tests/diffs and writes a summary. In this lab Bob actually **does something with an external system**. The mechanism is [MCP (Model Context Protocol)](https://modelcontextprotocol.io): Bob talks to a Jira server through a small adapter process declared in `.bob/mcp.json`, and the custom mode you write tells Bob which Jira tools it's allowed to call.

### What you'll build in Lab 5

1. **A Jira MCP server registration** in `.bob/mcp.json` — declarative config that Bob's pipeline pod picks up at startup. No Jenkins UI changes, no image rebuild.

2. **A custom Bob mode for DCR + Jira reporting** (`pipeline-dcr-jira-reporter`) — a pipeline mode with the `mcp` tool group enabled and a tight `alwaysAllow` list of Jira tools so the mode can post the DCR without prompting for approval mid-build.

3. **A `DCR` stage** in your Jenkinsfile — runs after Unit Tests, gathers the change material (commits since `main`, diff stats, test results, artifacts from earlier stages), hands it to Bob in the new mode, and Bob both writes a `deployment-change-request.md` artifact **and** files/updates a Jira ticket.

By the end, every push produces a structured DCR in Jenkins **and** a Jira ticket your release manager can act on — without anyone copy-pasting between tools.

### What you'll reuse from Labs 1 & 2

- **The `askBob` helper function** — same call pattern, just a new mode slug.
- **The `jenkins-bob-integration` mode** — you'll use this in your IDE to write the DCR stage.
- **Earlier-stage artifacts** — the DCR mode can read `bob-pr-review.md` and `bob-test-analysis.md` from the workspace if you want the report to roll up the rest of the pipeline's findings.

---

## Before you start

- [ ] Labs 1 and 2 complete (PR Review + Unit Tests stages already in your Jenkinsfile)
- [ ] You're on your working branch (e.g. `user1-labs`)
- [ ] **Your instructor has provisioned the Jira credential set in the `jenkins` namespace.** The `bob-cli` sidecar needs `JIRA_URL`, `JIRA_USERNAME`, and `JIRA_API_TOKEN` injected as env vars (same `secretKeyRef` pattern as `BOBSHELL_API_KEY`). If those env vars aren't present in the pod, the MCP server will start but every Jira call will 401. If you don't know whether this has been done, ask your instructor before pushing.
- [ ] **The `bob-cli` image has `uv`/`uvx` installed.** The instructor's `setup/bob-cli/Dockerfile` ships Node only by default. The `mcp-atlassian` server is a Python package launched via `uvx`, so the image needs `uv` added (one extra line in the Dockerfile + a rebuild). If your instructor hasn't done this yet, the MCP block you write in Part 1 will cause the bob container to log `uvx: command not found` the first time the mode tries to use the server.

> **Why this lab needs more environment setup than Labs 1–2.** The earlier labs only needed Bob to read files. This one needs Bob to **call out to a network service with credentials** — that's the cost of doing real work in a CI environment. Once the secret + image plumbing is in place, every future MCP server you add (GitHub, Confluence, ServiceNow, Slack…) follows the same pattern.

---

## Part 1 — Register the Jira MCP server in `.bob/mcp.json`

`.bob/mcp.json` currently exists with an empty `mcpServers` object. Bob loads this file from the workspace exactly the same way it loads `custom_modes.yaml` — fresh on every pipeline run, no rebuild required. Adding a server here is purely a content change on your branch.

You may already have a Jira MCP server configured for your IDE in your personal settings — most participants do, and it usually looks like this:

```json
"atlassian": {
  "command": "uvx",
  "args": ["mcp-atlassian"],
  "env": {
    "JIRA_URL": "${JIRA_URL}",
    "JIRA_USERNAME": "${JIRA_USERNAME}",
    "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
  },
  "disabled": false,
  "alwaysAllow": ["jira_get_issue", "jira_search", "jira_add_comment", "..."]
}
```

The pipeline config is intentionally **almost identical** to the IDE config — same package, same env var names, same shape. The thing to be aware of is that Bob CLI sometimes needs a fully-qualified path to the launcher (`uvx`, `npx`, etc.) when the IDE config can rely on PATH resolution. In our pod the bob image installs `uv` to a known path, so `"command": "uvx"` works without a full path — but if you ever see `command not found` errors on a different cluster, this is the first thing to fix.

### Key characteristics of this MCP registration:

- **Server name**: `atlassian` (this is the string the mode's `alwaysAllow` list and any explicit `mcp__atlassian__*` tool calls reference — pick it carefully, renaming later means touching multiple files)
- **Transport**: `stdio` (the default — `uvx` launches the server as a subprocess of bob)
- **Credentials**: Pulled from the bob container's environment, **not** baked into `mcp.json`. The `${VAR}` syntax means Bob expands the value at startup from whatever is set in the pod
- **`disabled: false`**: explicit because the file is committed to git and a future maintainer reading it shouldn't have to guess
- **`alwaysAllow` list**: kept short and read/comment-leaning. Pipeline modes shouldn't be transitioning issues or deleting things without an explicit prompt — that's a footgun in CI

### Edit `.bob/mcp.json` directly

Open the file (it's currently `{"mcpServers":{}}`) and replace it with:

```json
{
  "mcpServers": {
    "atlassian": {
      "command": "uvx",
      "args": ["mcp-atlassian"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}"
      },
      "disabled": false,
      "alwaysAllow": [
        "jira_get_issue",
        "jira_search",
        "jira_add_comment",
        "jira_get_all_projects",
        "jira_get_project_issues"
      ]
    }
  }
}
```

> **Why such a short `alwaysAllow` list?** Anything in this list runs **without confirmation** in the pipeline pod. Read-style tools (`get_issue`, `search`) are fine. Mutating tools (`jira_add_comment`) are okay too — that's the point of the lab. **Avoid** putting `jira_transition_issue`, `jira_update_issue`, or anything that can move tickets through a workflow in here without thinking hard about blast radius. Anything not in `alwaysAllow` will require the model's tool call to surface a prompt that nobody is around to answer in a CI run, so the Jira write effectively no-ops — which is sometimes what you want. Treat this list as the contract.

> **Why no `cwd` field like the screenshot in the spec docs?** The IBM `ibmi-mcp-server` example sets a fully-qualified `cwd` because it reads tool definitions from a local path on the user's laptop. `mcp-atlassian` is self-contained — it talks to the Jira REST API and needs no project-local files. Skip `cwd` here; adding it just makes the config brittle when the workspace path changes.

No push yet — nothing reads `mcp.json` until a mode declares it can use MCP.

---

## Part 2 — Create the `pipeline-dcr-jira-reporter` custom mode

The MCP registration is just plumbing. The **behavior** comes from a custom mode that (a) knows how to assemble a DCR from pipeline outputs and (b) is allowed to talk to the Jira MCP server.

### Key characteristics of this mode:

- **Purpose**: Generate a Deployment Change Request from the branch's commits, diff, test results, and earlier Bob analyses, then mirror the report into Jira
- **Permissions**: `read` + `mcp` (no `edit` — the mode shouldn't be modifying source code; the DCR file itself is written by the pipeline stage with `writeFile`)
- **MCP scope**: Only the `atlassian` server, only the tools listed in `alwaysAllow`. The mode should **never** invent tool calls outside that list
- **Output format**: Plain markdown DCR with a fixed section structure (Summary, Risk, Changes, Test Results, Rollback Plan, Reviewer Notes) so the artifact is consistent build-to-build and easy for downstream tooling to parse
- **Jira behavior**: Decide between *create new issue* vs *comment on existing issue* based on whether the branch name or commit messages reference an existing ticket key (e.g., `PROJ-123`). If there's a match, comment on it; if not, create a new one in a configured project
- **No IDE restart needed**: pipeline modes are loaded fresh from the workspace on each run

Start a new task and switch to the built-in **Mode Writer** mode. Paste this as a starting prompt, or write your own:

```
Write me a custom mode called pipeline-dcr-jira-reporter. The slug should be exactly: pipeline-dcr-jira-reporter.

The mode's job is to generate a Deployment Change Request (DCR) for a Jenkins pipeline run and then push that report to Jira via the atlassian MCP server.

Inputs the mode should expect to find in the workspace at invocation time:
  - The git branch's commit history and diff (the pipeline stage will pre-compute these into files)
  - bob-pr-review.md (from the Lab 1 PR Review stage), if present
  - bob-test-analysis.md (from the Lab 2 Unit Tests stage), if present
  - A short context file (dcr-context.txt) the pipeline writes that includes the build number, branch name, and any Jira ticket key parsed out of the branch name or commits

Output:
  1. Write a markdown DCR to deployment-change-request.md with these sections (in this order):
     - Summary — one paragraph, what is being deployed and why
     - Changes — bullet list grouped by area (api, db, config, infra, deps)
     - Risk Assessment — high/medium/low with rationale, pulling from bob-pr-review.md if it exists
     - Test Results — pass/fail summary, pulling from bob-test-analysis.md if it exists
     - Rollback Plan — concrete steps, not "revert the commit"
     - Reviewer Notes — what the reviewer should look at first
  2. After writing the file, mirror the DCR to Jira:
     - If dcr-context.txt names an existing Jira ticket key, use jira_add_comment to attach the DCR summary to that ticket
     - If not, do nothing on the Jira side. Do NOT create new tickets — leave that to a follow-up extension. Note in the console that no Jira ticket was referenced.

Tool groups:
  - read
  - mcp (restricted to the atlassian server, with the alwaysAllow tools defined in .bob/mcp.json: jira_get_issue, jira_search, jira_add_comment, jira_get_all_projects, jira_get_project_issues)

Output constraints:
  - Plain markdown, readable in Jenkins console as plain text (no HTML, no fancy tables)
  - Section headers are H2 (##) so the document parses cleanly
  - Total document length capped — this is a release artifact, not a novel. Aim for under 200 lines

Add a rules directory for this mode with XML files describing:
  - The required DCR section structure
  - When to call which Jira MCP tool (e.g., always jira_get_issue first to confirm the ticket exists before commenting)
  - How to format the comment payload (a short DCR digest, not the full file — keep Jira tickets readable)
  - Defensive behavior when the MCP server is unreachable: write the DCR to disk anyway and log the Jira failure clearly, do not fail the pipeline

Append the new mode to the bottom of the existing @.bob/custom_modes.yaml file — do not overwrite anything.
```

Watch Bob work and provide input where it helps. Pay particular attention to two things in what Mode Writer produces:

1. **The `mcp` group declaration** — it should reference the `atlassian` server explicitly and not grant blanket MCP access. If the generated YAML has `groups: [read, mcp]` without scoping, edit it to scope down before saving.
2. **The "do not create new tickets" rule** — this is a deliberate guardrail for the lab's first pass. If you want issue creation, that's in the [extensions doc](LAB5_IDEAS.md), but for now the mode should only comment on tickets it can confirm already exist.

Since you won't be invoking this mode from the IDE, **no need to restart Bob IDE**. The pipeline pod reads `.bob/custom_modes.yaml` and `.bob/mcp.json` together at the start of each build.

---

## Part 3 — Add the `DCR` stage to your Jenkinsfile

Ensure you have restarted Bob IDE so the `jenkins-bob-integration` mode from Lab 1 still appears in your dropdown.

Start a new task and switch to the **Jenkins Bob Integration** mode. Write your own prompt that asks Bob to do all of the following:

- Add a new stage called **`DCR`** to `@Jenkinsfile` that runs **after** `Unit Tests` (so it has access to the test analysis artifact) and is the **last** stage before the global `post` block.
- Before any git command in the stage, configure git's `safe.directory` for the workspace (same `git config --global --add safe.directory "$WORKSPACE"` line as Lab 1).
- Gather the change material into the workspace as **plain relative-path files** Bob can read:
  - `dcr-commits.txt` — output of `git log origin/main..HEAD --pretty=format:'%h %s'`
  - `dcr-diffstat.txt` — output of `git diff origin/main...HEAD --stat`
  - `dcr-context.txt` — a short text file containing `BUILD_NUMBER=${BUILD_NUMBER}`, `BRANCH=${BRANCH_NAME}` (or the equivalent of whatever Jenkins env var holds the branch), and `JIRA_KEY=` followed by any Jira ticket key (`[A-Z]+-[0-9]+`) extracted from the branch name or the most recent commit message. If no key is found, leave the value empty — the mode handles both cases.
- Make all three of those `sh` invocations resilient — fall back to empty files rather than failing the stage if the git command produces no output (same pattern as Lab 1's diff handling).
- Call the `askBob` helper with the mode `pipeline-dcr-jira-reporter` and a short prompt instructing Bob to read `dcr-commits.txt`, `dcr-diffstat.txt`, `dcr-context.txt`, and (if present) `bob-pr-review.md` and `bob-test-analysis.md`, then produce the DCR per the mode's rules and post to Jira if a ticket key is present.
- Capture `askBob`'s return value into a local variable.
- Print the analysis between banner lines in the Jenkins console (same banner pattern as Lab 1).
- The mode itself writes `deployment-change-request.md` to the workspace. Archive that file as a build artifact in the stage's `post.always` block. Use `allowEmptyArchive: true` so a dead MCP server doesn't break the artifact step.
- Wrap the whole Bob invocation in `catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE')` so a Jira outage marks the build UNSTABLE rather than killing it. The DCR file should still be archived even in the UNSTABLE case.

Watch Bob work. Before pushing, read the diff and sanity-check:

- The stage sits **after** `Unit Tests` and **before** the closing `post` block
- `askBob` is called with the exact mode slug `pipeline-dcr-jira-reporter`
- The three input files use **relative** paths, not `/workspace/...` — same trap as Lab 1
- `archiveArtifacts` references `deployment-change-request.md`, not whatever the mode's intermediate output happens to be called
- `catchError` is in place — you don't want a MCP/Jira hiccup turning the build red after the actual code already passed every gate

---

## Part 4 — Push and watch

```bash
git add Jenkinsfile .bob/
git commit -m "Lab 5 — DCR stage with Jira MCP reporting"
git push
```

In Jenkins, click **Build Now** on your pipeline and watch the console.

Expected:

- `Checkout`, `PR Review`, and `Unit Tests` run as in Labs 1 & 2
- `DCR` stage runs last. The console shows your stage's banner with the generated DCR markdown printed between the banner lines
- Build page lists `deployment-change-request.md` under **Build Artifacts**
- If your branch name contains a real Jira key (e.g., `user1-labs-PROJ-42`), the corresponding ticket gets a new comment with the DCR digest. Open the ticket and verify
- If no Jira key was found, the console clearly says so and the DCR is still archived
- Pipeline ends SUCCESS (or UNSTABLE if Jira was unreachable — but the artifact is still there)

**Optional:** rename your branch (or push an extra commit) so a Jira key is present in the message, push again, and confirm the comment lands on the ticket. Inspect the comment — does the digest read like something a release manager would actually use? Tune the mode's rules if not.

---

## Stuck?

- **`uvx: command not found` in the bob container's startup logs.** The image doesn't have `uv` installed. The fix is on the instructor — `setup/bob-cli/Dockerfile` needs `pip install uv` (or `curl -LsSf https://astral.sh/uv/install.sh | sh`) and a rebuild + push. Without this, the MCP server can't launch.
- **MCP server connects but every Jira call returns 401.** The `JIRA_*` env vars aren't reaching the bob container. Confirm the secret was created in the `jenkins` namespace and that the container's `env` block in the Jenkinsfile pod spec references it via `secretKeyRef`. Rotate the API token if the credential is correct but expired.
- **Mode runs, DCR file appears, but no Jira comment is posted.** Check the console for "no Jira ticket referenced" — the ticket-key extraction in `dcr-context.txt` probably failed. The regex is `[A-Z]+-[0-9]+`; lowercase project keys won't match. Either rename the branch or expand the regex in your stage script.
- **Bob says `Tool jira_transition_issue not in alwaysAllow list`.** Working as intended. Mutating tools that aren't in the list trigger an interactive approval prompt, which never gets answered in CI. Either add the tool to `alwaysAllow` (only if you actually want CI to perform that action), or rewrite the mode's rules so it doesn't try to transition.
- **Build goes UNSTABLE but everything else worked.** Open the archived `deployment-change-request.md` and the console output for the `DCR` stage. The most common cause is the MCP server timing out on a slow Jira instance — the DCR file is still good, the build is just flagging that the Jira side didn't confirm.
- **Both `pipeline-dcr-jira-reporter` and the actual Jira ticket already have a DCR digest from the previous build, and now there are duplicates.** That's expected behavior for the first pass — the mode appends comments rather than updating one. The [extensions doc](LAB5_IDEAS.md) covers an idempotent variant.
- **Want to validate `.bob/mcp.json` locally before pushing.** Most JSON validators work, but if you also want to check that Bob can parse it: in your IDE, run `bob --list-mcp-servers` (or whatever the equivalent command is in the version you're on) — the same parser runs in both places.
- **`Jenkinsfile` not working?** Copy `Jenkinsfile.lab5solution` from the repo root over your own `Jenkinsfile` and push. That's the reference state after Lab 5 with all 5 stages integrated.

---

That's Lab 5 — and the workshop. You now have a Jenkins pipeline that reviews diffs, runs and diagnoses tests, and produces a structured release report mirrored into Jira, all driven by Bob and all configured from a single branch in this repo.

Want to push it further? Open [LAB5_IDEAS.md](LAB5_IDEAS.md) for extension exercises.
