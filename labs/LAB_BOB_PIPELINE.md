# Lab: Integrating IBM Bob into Your Pipeline

The `main` branch has a working Jenkins pipeline that implements the client's 10-step regulated deployment flow — but it has no AI assistance. When stages fail, the pipeline dumps raw output that's hard to act on. In this lab you'll add Bob at three key pain points to make failures understandable.

**Time:** ~30 minutes
**Prerequisites:** Setup complete (app, ArgoCD, Bob CLI, Jenkins all running). The completed version is at `labs/solution/Jenkinsfile.solution`.

---

## Before you start

Run a build in Jenkins with `BRANCH=main`. The pipeline has intentional issues:

- **PCI Compliance (Step 4)** — a `System.out.println` violates PCI checkstyle rules (yellow)
- **Unit Tests (Step 5)** — status validation was removed, 2 tests fail (yellow)
- **Security Scan (Step 6)** — Spring Boot 3.2.0 has known CVEs (yellow)

Look at the console output for each failing stage. It's raw Maven output, raw test stack traces, and a wall of CVE tables. By the end of this lab, Bob will explain all of it in plain language.

---

## How Bob works on the cluster

Bob CLI runs in a pod labeled `component=bob-cli`. From any pod on the cluster (including the Jenkins agent), you can call Bob like this:

```bash
BOB_POD=$(oc get pods -l component=bob-cli -o jsonpath='{.items[0].metadata.name}')
oc exec $BOB_POD -- bob -p "Your question here" --hide-intermediary-output
```

You will wrap this in a Groovy helper function so every pipeline stage can call it with one line.

---

## Exercise 1: Add the `askBob` helper function

Open `Jenkinsfile` in Bob. At the very bottom of the file, **after** the closing `}` of the `pipeline` block, add:

```groovy
def askBob(prompt) {
    def bobPod = sh(
        script: "oc get pods -l component=bob-cli -o jsonpath='{.items[0].metadata.name}' 2>/dev/null",
        returnStdout: true
    ).trim()

    if (!bobPod) {
        echo "Warning: bob-cli pod not found"
        return "Bob CLI not available"
    }

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

**Test it.** Add a temporary stage right after Checkout:

```groovy
stage('Test Bob Connection') {
    steps {
        script {
            def response = askBob("Reply with exactly: BOB_OK")
            echo "Bob says: ${response}"
        }
    }
}
```

Commit, push, rebuild on `main`. Verify Bob responds, then remove the test stage.

> **Checkpoint:** Bob's response appears in the Jenkins console.

---

## Exercise 2: Bob analyzes the PR

Add a new stage after Checkout. Find this comment in the Jenkinsfile:

```groovy
// ╔════════════════════════════════════════════════════════════╗
// ║  EXERCISE 2: Add a Bob PR Analysis stage here             ║
// ╚════════════════════════════════════════════════════════════╝
```

Replace it with:

```groovy
stage('Bob PR Analysis') {
    steps {
        echo "══════════════════════════════════════════"
        echo "  STEP 2: Bob Analyzes the PR"
        echo "══════════════════════════════════════════"
        script {
            def diffStat = sh(
                script: 'git diff --stat origin/main...HEAD 2>/dev/null || git diff --stat HEAD~1 2>/dev/null || echo "No diff"',
                returnStdout: true
            ).trim()

            env.BOB_PR_ANALYSIS = askBob("""A pull request has been submitted for review.

Changed files:
${env.CHANGED_FILES}

Diff summary:
${diffStat}

Analyze this PR:
1. What is this change doing?
2. What are the potential risks?
3. What should reviewers focus on?

Be concise.""")

            echo "Bob's PR Analysis:\n${env.BOB_PR_ANALYSIS}"
        }
    }
}
```

Commit, push, rebuild. Bob should summarize the changes and flag the risks before any checks run.

> **Checkpoint:** Bob's PR analysis appears in the console before the Lint stage.

---

## Exercise 3: Bob diagnoses test failures

Find this comment in the Test stage:

```groovy
// ╔════════════════════════════════════════════════════╗
// ║  EXERCISE 3: Add Bob test failure analysis here    ║
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

Commit, push, rebuild. The Test stage should still go yellow, but now Bob explains what broke and how to fix it.

> **Checkpoint:** Bob identifies the missing status validation and suggests restoring it.

---

## Exercise 4: Bob triages security vulnerabilities

Find this comment in the Security Scan stage:

```groovy
// ╔════════════════════════════════════════════════════╗
// ║  EXERCISE 4: Add Bob security scan analysis here   ║
// ╚════════════════════════════════════════════════════╝
```

Replace it with:

```groovy
env.BOB_SECURITY_ANALYSIS = askBob("""Security scan found vulnerabilities in a PCI-regulated financial services environment.

Scan results:
${scanResult}

For each vulnerability:
1. What is the vulnerability and is it exploitable in this context?
2. What is the PCI compliance impact?
3. What is the recommended fix (specific version to upgrade to)?

Prioritize by severity. Be concise.""")

echo "Bob's Security Analysis:\n${env.BOB_SECURITY_ANALYSIS}"
```

Commit, push, rebuild. Instead of a raw Trivy table, Bob explains each CVE and tells you exactly what to upgrade.

> **Checkpoint:** Bob's security analysis appears with actionable fix recommendations.

---

## What you built

| Exercise | Pipeline stage | What Bob does |
|---|---|---|
| `askBob()` helper | — | Sends any prompt to the Bob CLI pod |
| PR Analysis | After Checkout (Step 2) | Summarizes the change, identifies risks before checks run |
| Test Failure Diagnosis | Unit Tests (Step 5) | Explains what broke and how to fix it |
| Security Scan Triage | Security Scan (Step 6) | Explains CVEs, PCI impact, and specific version to upgrade |

### The pattern

Every integration point follows the same pattern:

1. **Collect context** — gather the data Bob needs (diff, test output, scan results)
2. **Write a clear prompt** — tell Bob what role to play, what data you're giving it, and what format you want back
3. **Call `askBob()`** — send the prompt, get the response
4. **Use the response** — display it, feed it to the next stage, or show it at the approval gate

---

## Extra exercises

The same pattern works for other stages. Try these on your own:

### DCR Generation (Approval Gate)

Find the `EXTRA` comment in the Approval stage. Replace the entire `script` block so Bob generates a formal Deployment Change Request:

```groovy
script {
    def pciStatus = env.PCI_FAILED == 'true' ? 'FAILED' : 'PASSED'
    def testStatus = env.TEST_FAILED == 'true' ? 'FAILED' : 'PASSED'
    def canDeploy = (env.PCI_FAILED != 'true' && env.TEST_FAILED != 'true' && env.SECURITY_RISK != 'HIGH')

    env.DCR_SUMMARY = askBob("""Create a formal Deployment Change Request (DCR) for a PCI-regulated financial services environment.

CHANGE DETAILS:
- Branch: ${params.BRANCH}
- Changed files: ${env.CHANGED_FILES}

VALIDATION RESULTS:
- PCI compliance: ${pciStatus}
- Unit tests: ${testStatus} (${env.TEST_SUMMARY})
- Security scan: ${env.SECURITY_RISK} risk
${env.BOB_SECURITY_ANALYSIS ? '- Security Issues: ' + env.BOB_SECURITY_ANALYSIS : ''}
${env.BOB_TEST_ANALYSIS ? '- Test Failures: ' + env.BOB_TEST_ANALYSIS : ''}

Create a DCR with:
1. CHANGE DESCRIPTION
2. RISK ASSESSMENT — Low/Medium/High/Critical with justification
3. AFFECTED SERVICES
4. VALIDATION EVIDENCE
5. ROLLBACK PLAN
6. RECOMMENDATION — APPROVE or REJECT

${canDeploy ? 'All checks passed.' : 'IMPORTANT: Some checks FAILED.'}

Be formal and concise.""")

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║          DEPLOYMENT CHANGE REQUEST (DCR)                ║"
    echo "╠══════════════════════════════════════════════════════════╣"
    echo "${env.DCR_SUMMARY}"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    try {
        input message: "${env.DCR_SUMMARY}\n\nDo you approve this deployment?",
            ok: 'Approve Deployment',
            submitter: ''
    } catch (e) {
        echo "Deployment REJECTED."
        error("DCR rejected — deployment aborted")
    }
    echo "Deployment APPROVED."
}
```

### Smoke Test Triage

Find the `EXTRA` comment in the Smoke Tests stage:

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

---

## Cleanup

When you're done, tear everything down:

```bash
make teardown
```
