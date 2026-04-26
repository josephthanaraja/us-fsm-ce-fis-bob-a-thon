# Lab 2 — Unit Testing with Bob

## What you'll build

- A custom Bob mode for **writing** unit tests (used in your IDE)
- A custom Bob mode for **analyzing** test failures (used in the pipeline)
- A `Unit Tests` stage in your Jenkinsfile that runs `mvn test`
- A deliberately broken test that shows your failure-analyzer mode in action

By the end, your pipeline will catch a failing test, keep going, and have Bob explain — in plain English, in the Jenkins console — what broke and why.

---

## Before you start

- [ ] Lab 1 complete (your Jenkinsfile already has a PR Review stage)
- [ ] You're working on your branch (e.g. `user1-labs`)

---

## Part 1 — Create a custom mode for writing unit tests

Start a new task and switch to the built-in **Mode Writer** mode. Read this prompt template, then adjust how you see fit before sending. If you have personal preferences about how to write unit tests (naming conventions, @DisplayName annotations, whatever) add it to the prompt. 

```
Write me a custom mode for writing Java unit tests. This mode should be an expert at JUnit 5 + Mockito unit test best practices. Specifically for a Spring Boot application. This mode should also read existing unit tests to ensure we match code style and naming conventions of existing tests. 

The slug should be: java-unit-test-mode

Tool groups:
  - `read`
  - `edit`

Add a rules directory with XML files for this mode. 

Append this to the bottom of the existing custom_modes file, don't overwrite anything. 
```

Watch Bob work on the task, and provide input where needed. 

Once the task is complete, restart Bob IDE for the mode to appear in your mode dropdown. 

---

## Part 2 — Use your new mode to add a test

Start a new task and switch Bob to Ask mode.

Ask Bob:

> "Read @OrderService.java and @OrderServiceTest.java. What edge cases aren't covered?"

Pick one of Bob's suggestions, then in the same task switch to your new unit test mode, and tell Bob:

> "Write a test for [the edge case] and add it to @OrderServiceTest.java."

Bob will write the test. 

Then ask Bob: 

> "Can you run the test and ensure it passes?"

Bob should automatically switch modes and run the tests. 

```bash
cd order-service
mvn test
```

---

## Part 3 — Add the unit test stage to your Jenkinsfile

Start a new task and switch to Code mode. Ask Bob to add a `Unit Tests` stage to `@Jenkinsfile`. 

- Runs `mvn test` inside `order-service/`
- **Doesn't kill the pipeline if tests fail** — you want the next stage (Bob's analysis) to run so you can see what broke. Look up the `catchError` step with `buildResult: 'UNSTABLE'`.
- Publishes test results to the Jenkins UI via the `junit` step

---

## Part 4 — Create a custom mode for analyzing test failures

Your test-writer mode is great for the IDE, but for the pipeline you want something different: a mode that only reads (no edits), trained on test-failure diagnosis.

Start a new task and switch to Mode Writer mode. Paste this as a starting prompt, or enter your own prompt.

```
Write me a custom mode for analyzing test failures on my jenkins pipeline. The mode's purpose to analyze failed test logs and provide a human readable output with actionable steps to rectify. 

Tool groups: read

Slug: pipeline-test-failure-analyzer

Add a rules directory with XML files for this mode. 

Append this to the bottom of the existing custom_modes file, don't overwrite anything. 
```

Notice how this mode has **fewer** permissions than your test-writer — just `read`. That's deliberate: a mode invoked from CI pipelines should do the minimum it needs to.

Since you won't be using this mode in the IDE, there is no need to restart Bob. When we push the branch to github and run the jenkins pipeline, the Bob pod will pickup the new mode. 

---

## Part 5 — Add the Bob to the Unit Test stage of your Jenkinsfile

Start a new task and switch to Code mode. 

Ask Bob to adjust the `Unit Tests` stage in `@Jenkinsfile` to call Bob using your new mode when there is a test failure, then post Bob's output to the Jenkins console output. You can use the example prompt or write your own. 

> "In @Jenkinsfile, adjust the `Unit Tests` stage to call Bob with the test failure logs. Use `container('bob-cli')` to run a shell command invoking `bob --chat-mode pipeline-test-failure-analyzer -p '...'` with a prompt telling Bob to read `/workspace/order-service/target/surefire-reports/` and relevant sources under `/workspace/order-service/src/`."

---

## Part 6 — Break a test intentionally and watch Bob analyze it

Pick one of the existing tests (or the one your test-writer mode added) and flip an assertion so it'll fail. For example, in `OrderServiceTest.java`:

```java
// before
assertThat(result).isEqualTo(expected);

// after (deliberate break)
assertThat(result).isEqualTo(expected + 1);
```

After making that change, `git add` all of the new files you made, git commit and push your branch to github. 

In Jenkins, click **Build Now**. Watch:

- `Unit Tests` turns **yellow (UNSTABLE)** — the failing test is recorded, but the pipeline continues
- Jenkins's Test Results link surfaces the failure with the exact assertion message
- `Bob Test Analysis` runs, and the console shows Bob's plain-English breakdown: which test failed, what kind of failure, the likely root cause, and a suggested fix

**That's Lab 2 done.** Revert the broken test, push once more to get back to green, and you're ready for Lab 3.

---

## Stuck?

- **Jenkinsfile not working?** Copy `Jenkinsfile.lab2solution` from the repo root over your own `Jenkinsfile` and push. That's the reference state after Lab 2 — Lab 1 + Lab 2 stages in one file.
- **Mode not loading?** Check (a) `.bob/custom_modes.yaml` has the slug you're passing to `--chat-mode`, (b) the mode's `groups` matches what it needs to do, (c) `.bob/` is on your branch and pushed. Bob reads `.bob/custom_modes.yaml` fresh from the workspace on every pipeline run.
- **`mvn test` fails the stage hard?** You forgot the `catchError` wrapper — without it, Maven's non-zero exit code kills the pipeline before Bob ever runs.
- **`junit` step says "no test reports"?** Check the path: `order-service/target/surefire-reports/*.xml`.

---

When you're ready, open [LAB3_SECURITY_SCANNING.md](LAB3_SECURITY_SCANNING.md).
w