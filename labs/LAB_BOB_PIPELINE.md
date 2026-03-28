# Lab: Integrating Bob into Your Pipeline

In this lab you will add Bob AI to a working Jenkins pipeline, one integration point at a time. Each exercise adds Bob at a specific stage, and you'll test it by running the pipeline against a branch that triggers that failure.

**Time:** ~45 minutes
**Prerequisites:** Setup complete (app, ArgoCD, Bob CLI, Jenkins all running). The default `Jenkinsfile` is the baseline pipeline with no Bob. The completed version is at `labs/solution/Jenkinsfile.solution`.

---

## Scenario branches

Four branches are set up with intentional issues. The baseline pipeline catches these failures but only dumps raw output. You'll add Bob to explain what went wrong and how to fix it.

| Branch | What's broken | Pipeline stage that catches it |
|---|---|---|
| `lab/happy-path` | Nothing — clean build | All stages pass |
| `lab/security-vuln` | `System.out.println` + old base image | Step 3 (PCI Compliance) + Step 5 (Security Scan) |
| `lab/test-failure` | Status validation removed from OrderService | Step 4 (Unit Tests) |
| `lab/smoke-failure` | Health endpoint returns 503 | Step 9 (Smoke Tests) — passes all other checks |

**Try it now.** Before adding Bob, run a build in Jenkins with `BRANCH=lab/security-vuln` to see what a failure looks like without AI assistance. Look at the PCI Compliance stage output — it's raw Maven checkstyle output. By the end of this lab, Bob will explain that in plain language.

---

## How Bob works on the cluster

Bob CLI runs in a pod labeled `component=bob-cli`. From any other pod on the cluster (including the Jenkins agent), you can call Bob like this:

```bash
# Find the pod
BOB_POD=$(oc get pods -l component=bob-cli -o jsonpath='{.items[0].metadata.name}')

# Send a prompt
oc exec $BOB_POD -- bob -p "Your question here" --hide-intermediary-output
```

You will wrap this pattern in a Groovy helper function so every pipeline stage can call it with one line.

---

## Exercise 1: Add the `askBob` helper function

Open `Jenkinsfile` in your editor. At the very bottom of the file, **after** the closing `}` of the `pipeline` block, add this helper function:

```groovy
// ── Helper: ask Bob CLI a question ──────────────────────────────────────
def askBob(prompt) {
    def bobPod = sh(
        script: "oc get pods -l component=bob-cli -o jsonpath='{.items[0].metadata.name}' 2>/dev/null",
        returnStdout: true
    ).trim()

    if (!bobPod) {
        echo "Warning: bob-cli pod not found"
        return "Bob CLI not available"
    }

    // Write the prompt to a file to avoid shell escaping issues
    def promptFile = ".bob-prompt-${System.currentTimeMillis()}.txt"
    writeFile(file: promptFile, text: prompt)
    sh "oc cp ${promptFile} ${bobPod}:/tmp/bob-prompt.txt 2>/dev/null"
    sh "rm -f ${promptFile}"

    def result = sh(
        script: """oc exec ${bobPod} -- bash -c 'bob -p "\$(cat /tmp/bob-prompt.txt)" --hide-intermediary-output' 2>/dev/null || echo "Bob analysis unavailable" """,
        returnStdout: true
    ).trim()

    return result
}
```

**Why a file instead of inline?** Prompts contain newlines, quotes, and special characters. Passing them as shell arguments breaks. Writing to a file and `oc cp`-ing it to the Bob pod avoids all escaping issues.

**Test it.** Add a temporary stage right after Checkout to verify the helper works:

```groovy
stage('Test Bob Connection') {
    steps {
        script {
            def response = askBob("Reply with exactly: BOB_OK")
            echo "Bob says: ${response}"
            if (!response.contains("BOB_OK")) {
                echo "Warning: Bob did not respond as expected. Check the bob-cli pod."
            }
        }
    }
}
```

Commit, push, and run the pipeline:

```bash
git add Jenkinsfile
git commit -m "lab: add askBob helper function"
git push origin main
```

In Jenkins, build with `BRANCH=main`. Check the console output for the "Test Bob Connection" stage.

> **Checkpoint:** You see Bob's response in the Jenkins console. Remove the test stage before continuing (or leave it — your call).

---

## Exercise 2: Bob analyzes failures

Now you'll add Bob at two points where the pipeline **already detects a problem** but only dumps raw output. Bob will explain the problem in plain language.

### 2a — PCI compliance failure diagnosis

Find the `PCI Compliance Check` stage. Look for this comment block:

```groovy
// ╔════════════════════════════════════════════════════╗
// ║  LAB 2, EXERCISE 2: Add Bob PCI analysis here     ║
// ╚════════════════════════════════════════════════════╝
```

Replace it with:

```groovy
env.BOB_PCI_ANALYSIS = askBob("""PCI compliance check failed in a regulated financial environment.

These are PCI DSS compliance violations that must be fixed before deployment.

Violations:
${output}

For each violation:
1. Explain why this is a PCI compliance issue
2. What the specific risk is (data exposure, audit failure, etc.)
3. How to fix it

Be specific and reference PCI DSS requirements where applicable.""")

echo "Bob's PCI Analysis:\n${env.BOB_PCI_ANALYSIS}"
```

**What this does:** When the PCI checkstyle rules fail, instead of just showing the raw Maven output, Bob explains *why* each violation matters in PCI DSS terms and how to fix it.

### 2b — Unit test failure diagnosis

Find the `Test` stage. Look for this comment block:

```groovy
// ╔════════════════════════════════════════════════════╗
// ║  LAB 2, EXERCISE 3: Add Bob test analysis here    ║
// ╚════════════════════════════════════════════════════╝
```

Replace it with:

```groovy
env.BOB_TEST_ANALYSIS = askBob("""Unit tests failed. Analyze the failure and identify the root cause.

Test output:
${testOutput}

Provide:
1. Which test(s) failed and why
2. The root cause in the application code
3. Suggested fix

Be specific — reference exact class names and methods.""")

echo "Bob's Test Analysis:\n${env.BOB_TEST_ANALYSIS}"
```

**What this does:** When tests fail, Bob reads the test output, identifies the root cause, and tells the developer exactly what to fix.

### Test it

Commit and push your changes:

```bash
git add Jenkinsfile
git commit -m "lab: add Bob failure diagnosis for PCI and test failures"
git push origin main
```

**PCI failure:** Run a build with `BRANCH=lab/security-vuln`. Watch the PCI Compliance stage — instead of raw Maven output, Bob explains why `System.out.println` is a PCI violation and how to fix it.

**Test failure:** Run a build with `BRANCH=lab/test-failure`. Watch the Test stage — Bob identifies the missing status validation and suggests the fix.

> **Checkpoint:** Bob's analysis appears in the console output for both failure types.

---

## Exercise 3: Bob generates a Deployment Change Request

This is the highest-value integration point. Instead of a human writing a change management ticket, Bob generates a formal DCR that includes all the validation evidence from the pipeline.

Find the `Approval` stage. Look for this comment block:

```groovy
// ╔════════════════════════════════════════════════════════╗
// ║  LAB 2, EXERCISE 4: Replace this manual summary with  ║
// ║  a Bob-generated Deployment Change Request (DCR)      ║
// ╚════════════════════════════════════════════════════════╝
```

Replace the **entire `script` block** in the Approval stage with:

```groovy
script {
    def pciStatus = env.PCI_FAILED == 'true' ? 'FAILED' : 'PASSED'
    def testStatus = env.TEST_FAILED == 'true' ? 'FAILED' : 'PASSED'
    def canDeploy = (env.PCI_FAILED != 'true' && env.TEST_FAILED != 'true')

    env.DCR_SUMMARY = askBob("""Create a formal Deployment Change Request (DCR) for a PCI-regulated financial services environment.

CHANGE DETAILS:
- Branch: ${params.BRANCH}
- Changed files: ${env.CHANGED_FILES}

VALIDATION RESULTS:
- PCI compliance: ${pciStatus}
- Unit tests: ${testStatus} (${env.TEST_SUMMARY})
- Security scan: ${env.SECURITY_RISK} risk
${env.PCI_FAILED == 'true' && env.BOB_PCI_ANALYSIS ? '- PCI Issues: ' + env.BOB_PCI_ANALYSIS : ''}
${env.TEST_FAILED == 'true' && env.BOB_TEST_ANALYSIS ? '- Test Failures: ' + env.BOB_TEST_ANALYSIS : ''}

Create a DCR with:
1. CHANGE DESCRIPTION — What is changing and why
2. RISK ASSESSMENT — Low/Medium/High/Critical with justification
3. AFFECTED SERVICES — What services and environments are impacted
4. VALIDATION EVIDENCE — Summary of all check results
5. ROLLBACK PLAN — How to revert if deployment fails
6. RECOMMENDATION — APPROVE or REJECT

${canDeploy ? 'All checks passed.' : 'IMPORTANT: Some checks FAILED. Reflect this in the risk assessment and recommendation.'}

Be formal and concise. This will be reviewed by team management.""")

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          DEPLOYMENT CHANGE REQUEST (DCR)                ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "${env.DCR_SUMMARY}"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    try {
        input message: """
${env.DCR_SUMMARY}

Do you approve this deployment?
""",
            ok: 'Approve Deployment',
            submitter: ''
    } catch (e) {
        echo "Deployment REJECTED."
        error("DCR rejected — deployment aborted")
    }
    echo "Deployment APPROVED."
}
```

**What changed:** The approval gate now shows Bob's full DCR — risk assessment, validation evidence, rollback plan, and a recommendation — instead of a bare-bones summary. The reviewer has everything they need to make an informed decision without reading raw build logs.

### Test it

Commit and push:

```bash
git add Jenkinsfile
git commit -m "lab: add Bob-generated DCR at approval gate"
git push origin main
```

**Clean build:** Run a build with `BRANCH=lab/happy-path`. The DCR should show all checks passed and recommend APPROVE.

**Failed build:** Run a build with `BRANCH=lab/security-vuln`. The DCR should flag the PCI failure and recommend REJECT.

> **Checkpoint:** The approval gate shows Bob's full DCR instead of the bare-bones summary.

---

## Exercise 5: Bob triages smoke test failures

After deployment, smoke tests verify the service is actually working. When they fail, Bob can analyze the output and recommend whether to rollback.

Find the `Smoke Tests` stage. Look for this comment block:

```groovy
// ╔════════════════════════════════════════════════════╗
// ║  LAB 2, EXERCISE 5: Add Bob smoke test analysis   ║
// ╚════════════════════════════════════════════════════╝
```

Replace it with:

```groovy
env.BOB_SMOKE_ANALYSIS = askBob("""Post-deployment smoke tests detected issues.

Smoke test output:
${smokeOutput}

Analyze:
1. Which services are unhealthy and why
2. Is this a deployment issue or a pre-existing problem?
3. Should we rollback?

Be concise.""")

echo "Bob's Smoke Test Analysis:\n${env.BOB_SMOKE_ANALYSIS}"
```

### Test it

Commit and push:

```bash
git add Jenkinsfile
git commit -m "lab: add Bob smoke test triage"
git push origin main
```

Run a build with `BRANCH=lab/smoke-failure`. This branch changes the health endpoint to return 503. All pipeline checks pass (lint, PCI, tests, security), the build and deploy succeed, but the smoke tests fail post-deployment. Bob should analyze the 503 and recommend rollback.

> **Checkpoint:** Bob identifies the broken health endpoint and recommends rollback.

---

## What you built

You started with a pipeline that had no AI integration and added four capabilities:

| What you added | Where | What it does |
|---|---|---|
| `askBob()` helper | Bottom of Jenkinsfile | Sends any prompt to Bob CLI and returns the response |
| Failure diagnosis | PCI + Test stages | When a check fails, Bob explains why and how to fix it |
| DCR generation | Approval stage | Bob writes a formal change management ticket from pipeline data |
| Smoke test triage | Smoke Tests stage | When post-deploy checks fail, Bob recommends rollback or investigation |

### The pattern

Every integration point follows the same pattern:

1. **Collect context** — gather the data Bob needs (diff, test output, scan results)
2. **Write a clear prompt** — tell Bob what role to play, what data you're giving it, and what format you want back
3. **Call `askBob()`** — send the prompt, get the response
4. **Use the response** — display it in the console, feed it to the next stage, or show it at the approval gate

This pattern works for any pipeline stage. Some other places teams integrate Bob:

- **Post-deploy monitoring** — Bob analyzes logs and metrics after deployment
- **Rollback decision** — when smoke tests fail, Bob recommends whether to rollback or investigate
- **Environment config generation** — Bob generates properties files for new environments
- **Incident response** — Bob analyzes alerts and suggests remediation steps

---

## Bonus: Try it yourself

Pick one of these and implement it on your own, following the same pattern:

**A. PR summary** — Add a new stage after Checkout that asks Bob to summarize the PR diff:
```
"Summarize this PR for a code reviewer. Changed files: ${env.CHANGED_FILES}. Diff: [include diff output]. What is this change doing and what should the reviewer focus on?"
```

**B. Post-deploy status update** — Add a stage after Smoke Tests that asks Bob to write a status update for the change control ticket:
```
"The deployment is complete. Status: ${env.DEPLOY_STATUS}. Write a formal status update for the DCR ticket. Include: timestamp, verification results, whether the ticket can be closed."
```

**C. Environment config** — Use `make oc-bob` to ask Bob to generate a production properties file:
```bash
make oc-bob PROMPT="Analyze the order-service application. Generate application-prod-uk.properties for a production environment with an external PostgreSQL at db-prod.uk-cluster.internal:5432. Explain each setting."
```

---

## Cleanup

When you're done, you can tear everything down:

```bash
make teardown
```

Or leave it running for further experimentation.
