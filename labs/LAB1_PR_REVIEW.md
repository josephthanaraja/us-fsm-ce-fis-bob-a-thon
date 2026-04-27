# Lab 1 — PR / Git Diff Review with Bob

## What you'll build

- An **`askBob` helper function** in your Jenkinsfile — a clean way to call Bob from any stage without repeating the plumbing. You'll reuse this in every subsequent lab.
- A custom Bob mode **`pipeline-git-diff-overview`** that reads a git diff like a senior developer glancing at a PR — summarizing what changed, risk-ranking each change, and calling out areas worth a closer look.
- A **`PR Review` stage** in your Jenkinsfile that runs right after `Checkout`, captures the diff of the commit that triggered the build, and hands it to Bob via the helper.

By the end, every push will trigger a rubber-duck senior reviewer that surfaces risk before any other stage runs.

---

## Before you start

- [ ] Lab 0 complete (branch created, pipeline pointed at it, one successful `Checkout`-only build)
- [ ] You're on your working branch (e.g. `user1-labs`)

---

## Part 1 — Add the `askBob` helper to your Jenkinsfile

Every stage that invokes Bob has to do the same two things: step into `container('bob')` and run `bob --chat-mode …`. Factor that out **once** and each stage just passes a prompt and a mode, and gets back the analysis string to do whatever it wants with.

Because this helper is shared workshop infrastructure — you'll call it the same way in every subsequent lab — we're giving you the code directly rather than having you generate it. Paste it into your `@Jenkinsfile` at the bottom, **outside** the `pipeline { }` block:

```groovy
// ── Helper: ask Bob, optionally with a specific custom mode ──────────────────
// Writes the prompt to a tempfile in the shared workspace and runs
// `bob` in the bob container, adding `--chat-mode <mode>` only if mode is
// provided (otherwise Bob uses its built-in default mode). Returns the
// analysis as a string. Using a tempfile (instead of inlining the prompt
// on the command line) avoids shell-escaping issues when the prompt
// contains quotes, backticks, or newlines — common with diffs.
def askBob(String prompt, String mode = null) {
    container('bob') {
        def promptFile = ".bob-prompt-${System.currentTimeMillis()}.txt"
        writeFile file: promptFile, text: prompt

        def modeFlag = mode ? "--chat-mode ${mode}" : ""
        def analysis = sh(
            script: """bob ${modeFlag} -p "\$(cat ${promptFile})" --hide-intermediary-output""",
            returnStdout: true
        ).trim()

        sh "rm -f ${promptFile}"
        return analysis
    }
}
```

A few things to notice while you paste it in:

- **It lives outside `pipeline { }`.** Groovy functions at the top level of the Jenkinsfile are callable from any stage. Functions declared *inside* `pipeline { }` get interpreted as stage definitions by the Jenkins DSL, which isn't what you want.
- **It runs inside `container('bob')`.** The pipeline pod has three containers (`build-tools`, `oc-tools`, `bob`). Bob only lives in the last one, so every `bob` command has to be wrapped in `container('bob')`.
- **`mode` is optional** (`String mode = null`). Call `askBob("quick question")` to use Bob's default mode, or `askBob("do the thing", "some-custom-mode")` to pin a specific mode. For every lab in this workshop you'll pass a mode — that's the whole point of custom modes — but keeping the parameter optional means the helper is also usable for one-off asks.
- **The prompt goes through a file, not the command line.** This is the pattern you'll use to hand Bob larger inputs (diffs, scan outputs, logs) later in the workshop. Keeps shell quoting clean no matter what's in the prompt.
- **The helper is deliberately minimal.** It doesn't print banners, write archives, or decide what to do with the result — each stage handles that for itself. Keeps the helper composable for later labs that might do different things with Bob's output (fail the build on a keyword, post a PR comment, push to Jira, etc.).

No push yet — nothing calls the helper. On to the mode.

---

## Part 2 — Create the `pipeline-git-diff-overview` custom mode

The `askBob` helper is mode-agnostic. The *behavior* — what Bob actually does when invoked — comes from the custom mode you pass in. For Lab 1 that's a "senior developer glancing at a PR" mode: a short, risk-ranked summary, not an exhaustive review.

Start a new task and switch to the built-in **Mode Writer** mode. Paste this as a starting prompt, or write your own:

```
Write me a custom mode called pipeline-git-diff-overview. The slug should be exactly: pipeline-git-diff-overview.

The mode's job is to look at a git diff like a senior developer glancing at a pull request. It is NOT a full code review — it's a quick risk-oriented overview. For each notable change, it should:
  - Summarize what changed in one or two plain-English sentences
  - Rank the risk as high / medium / low
  - Call out specific things the reviewer should look at closely — null-safety, concurrency, behavior changes, security surface, performance hot paths, tests missing for new branches, etc.

Output constraints:
  - Readable in a Jenkins console — plain text only, no ANSI colors, no markdown tables that rely on column alignment
  - Section headers like "Summary", "Risk", "Watch for"
  - Short — this is a quick triage, not a dissertation. If nothing notable changed, say so in one sentence.

Tool groups: read (only). This mode runs in CI and should have minimum permissions.

Add a rules directory for this mode with XML files describing how to structure the output and what kinds of observations to prioritize.

Append the new mode to the bottom of the existing @.bob/custom_modes.yaml file — do not overwrite anything.
```

Watch Bob work and provide input where it helps.

Notice that this mode has only `read` permission — deliberately narrower than an IDE mode. A pipeline mode should do the minimum it needs to.

Since you won't be invoking this mode from the IDE, there's **no need to restart Bob IDE**. When the pipeline runs, Bob reads `.bob/custom_modes.yaml` fresh from the checked-out workspace, so the new mode is available as soon as the branch is pushed.

---

## Part 3 - Add Groovy Export Mode for Jenkinsfiles??????

Haven't done this yet will have to experiment

## Part 3 — Add the `PR Review` stage to your Jenkinsfile

Now wire the two together. Start a new task and switch to **Code** mode. Ask Bob to add a `PR Review` stage after `Checkout` in `@Jenkinsfile`. Example prompt:

```
In @Jenkinsfile, add a new stage called "PR Review" that runs immediately after the Checkout stage. The stage should:

1. Compute a git diff of the commit that triggered the build. Use `git diff HEAD~1 HEAD` and write the output to /workspace/git-diff.txt. Make the shell step resilient — if there's only one commit on the branch, `HEAD~1` doesn't exist and the diff should fall back to an empty file (don't fail the build).

2. Call my askBob helper with:
     - mode: "pipeline-git-diff-overview"
     - prompt: something short telling Bob to read /workspace/git-diff.txt and produce the senior-developer overview the mode is trained for

3. Capture the return value into a local variable (e.g. `def review = askBob(...)`).

4. Print a banner to the Jenkins console with the review between banner lines, so it's easy to spot in the build log. Something like:
     echo ''
     echo '════════════════════════════════════════════════════'
     echo '  Bob — PR Review'
     echo '════════════════════════════════════════════════════'
     echo review
     echo '════════════════════════════════════════════════════'

5. Write the review to a file called bob-pr-review.md and archive it as a build artifact (either in the stage's steps or a post-always block).
```

Bob will wire it up. Before pushing, read the diff and sanity-check:

- The stage sits between `Checkout` and wherever Lab 2's `Unit Tests` stage will go.
- `askBob` is called with the exact mode slug you created in Part 2.
- The `archiveArtifacts` path matches the `writeFile` path.

---

## Part 4 — Push and watch

```bash
git add Jenkinsfile .bob/
git commit -m "Lab 1 — PR review stage with askBob helper + pipeline-git-diff-overview mode"
git push
```

In Jenkins, click **Build Now** on your pipeline and watch the console.

Expected:

- `Checkout` stage turns green
- `PR Review` stage runs next. The console shows your stage's banner (`Bob — PR Review` or however you wrote it) with Bob's summary / risk / watch-for output between the banner lines
- Build page lists `bob-pr-review.md` under **Build Artifacts**
- Pipeline ends SUCCESS

Open the archived artifact from the build page and you've got a persistent record of Bob's take on that commit — searchable in Jenkins's build history.

**Optional:** make a commit that does something a senior developer would flag — add a null-unchecked parameter, or a broad `catch (Exception e)` that swallows errors, or a hardcoded secret — push, and read Bob's output. Does the risk ranking match your intuition? Does Bob surface the thing you'd mention in a code review? Tune the mode's rules if not.

---

## Stuck?

- **Pipeline fails with something like `askBob: method not found`.** Your helper function is inside the `pipeline { }` block. Move it to the top level of the file (outside the `pipeline { }` braces).
- **Bob stage runs but says the mode wasn't found.** Check (a) `.bob/custom_modes.yaml` contains the slug `pipeline-git-diff-overview`, (b) you're passing that exact string to `askBob`, (c) you committed and pushed `.bob/`. Bob reads `custom_modes.yaml` fresh from the workspace on every run.
- **The diff is empty on the first build.** `git diff HEAD~1 HEAD` needs at least two commits on the branch. If you only just created the branch and pushed one commit, `HEAD~1` doesn't exist. Push any small follow-up change (a newline in the Jenkinsfile works) and rebuild.
- **Bob output looks like a novel, not a triage summary.** The mode's rules file probably isn't constraining output length. Re-open Mode Writer and refine the rules to enforce brevity — cap per-change output to a few lines, require the three-section structure, tell Bob to skip uninteresting changes.
- **`Jenkinsfile` not working?** Copy `Jenkinsfile.lab1solution` from the repo root over your own `Jenkinsfile` and push. That's the reference state after Lab 1 and a safe reset point.

---

When you're ready, open [LAB2_UNIT_TESTING.md](LAB2_UNIT_TESTING.md).
