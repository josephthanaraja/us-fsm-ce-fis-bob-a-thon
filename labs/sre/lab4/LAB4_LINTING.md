# Lab 4 — Linting and Compliance with Bob

## Table of Contents

- [Overview of Lab 4](#overview-of-lab-4)
  - [What you'll build in Lab 4](#what-youll-build-in-lab-4)
  - [What you'll reuse from earlier labs](#what-youll-reuse-from-earlier-labs)
- [Before you start](#before-you-start)
- [Part 1 — Warm up in the IDE with Checkstyle and Bob](#part-1--warm-up-in-the-ide-with-checkstyle-and-bob)
- [Part 2 — Inspect the provided pipeline lint targets in the IDE](#part-2--inspect-the-provided-pipeline-lint-targets-in-the-ide)
- [Part 3 — Create the `iac-lint-fix-advisor` IDE mode](#part-3--create-the-iac-lint-fix-advisor-ide-mode)
- [Part 4 — Use the mode to improve one or two findings locally](#part-4--use-the-mode-to-improve-one-or-two-findings-locally)
- [Part 5 — Create the `pipeline-lint-reporter` mode](#part-5--create-the-pipeline-lint-reporter-mode)
- [Part 6 — Build the linting stages in Jenkins](#part-6--build-the-linting-stages-in-jenkins)
- [Part 7 — Push and watch](#part-7--push-and-watch)
- [Part 8 — Optional: post a Bob-generated lint summary to GitHub from the IDE](#part-8--optional-post-a-bob-generated-lint-summary-to-github-from-the-ide)
- [Part 9 — Optional: Add Error Prone for compile-time bug detection](#part-9--optional-add-error-prone-for-compile-time-bug-detection)
- [Stuck?](#stuck)

---

## Overview

In this lab, you'll add a multi-tool linting and compliance workflow to the pipeline. All the while using IBM Bob to interpret results and provide recommendations.

- You'll use the Checkstyle for Java linter to find and fix Java code quality issues in the IDE.
- You'll use [Hadolint](https://github.com/hadolint/hadolint) to find issues in the `Dockerfile`.
- You'll use [Checkov](https://www.checkov.io/) to find issues in the deployment manifests.
- You'll use [KubeLinter](https://docs.kubelinter.io/) to find issues in the Kubernetes workload. 

This lab intentionally makes use of slightly flawed deployment files with predictable findings. That allows us to focus on using AI to:

- interpret the linter findings
- anticipate likely pipeline findings before Jenkins runs
- recommend fixes
- produce a consolidated lint report
- prepare a PR-comment-ready summary

### What you'll build in Lab 4

1. **A Bob mode for lint remediation** (`iac-lint-fix-advisor`) — a mode that reads the Dockerfile and deployment manifests, predicts likely pipeline findings, and helps propose minimal fixes.

2. **A Bob mode for lint reporting** (`pipeline-lint-reporter`) — a read-only mode that reads the raw output from multiple linters and turns it into a Jenkins-friendly report.

3. **A new set of pipeline stages** — one stage runs the linters (including Checkstyle), one stage asks Bob to summarize the results, and one stage posts a condensed comment to the PR.

4. **A final Bob-enriched lint report** — archived in Jenkins as a build artifact and summarized in a PR comment.

By the end, Bob will not just say that linting found problems — but it will explain what matters, which issues overlap across tools, what to fix first, and how to remediate them.

---

## Before you start

- [ ] Lab 1 complete at minimum (your Jenkinsfile already has [`askBob()`](labs/sre/lab1/Jenkinsfile.lab1solution:153))
- [ ] You're on your working branch (for example `user1-labs`)

> **Note:** [`order-service/pom.xml`](order-service/pom.xml:74-88) already includes [Checkstyle](https://checkstyle.sourceforge.io/) configuration with Google's style checks. This lab leverages that existing configuration for both IDE and pipeline linting.

---

## Part 1 — Checkstyle for Java Linting

Before touching the pipeline, start in the Bob IDE with a high level analysis.

1. If we were starting in a new application, we could have Bob review our application and help us identify linters already in place and recommendations for additional linters.

1. Start a new task in Bob and ensure you are in the **Ask** mode. Then prompts Bob with the following:

    ```text
    Analyze the files in my @/order-service  application and recommend what linters I should use in my build and deploy pipeline
    ```

1. Bob will review what linters are in place and what gaps might exist based on the files in the application.

1. Lets narrow in on a specific linter. Start a new task in Bob and ensure you are in the **Ask** mode. Then prompts Bob with the following:

```text
Read @order-service/src/main/java/com/example/orders/service/OrderService.java.
Give me a concise view of what kinds of issues Checkstyle will likely flag here, which ones matter most, and what would you recommend fixing first?
```

1. Bob itself understands different linting frameworks and can be used to get intuition about what issues Checkstyle will likely flag here, which ones matter most, and what it recommends fixing first.

1. Next, lets actually run Checkstyle from the command line to generate a report with all findings:

    ```bash
    cd order-service
    mvn checkstyle:check
    ```

1. This will generate a full report at `order-service/target/checkstyle-result.xml`. Lets ask Bob to analyze the output. In **Ask** mode, prompt Bob with the following:

    ```text
    I ran `mvn checkstyle:check` in the order-service directory. Read the output and explain:
    1. What are the most critical violations?
    2. Which ones could impact production reliability?
    3. What should I fix first?
    ```

    > **Note:** Bob will request permission to read the target directory and will find the correct output report xml file.

1. Bob was not only able to find and read the report, it was able to provide immediate feedback for which are the most critical issues, which impact reliability and a prioritization for fixing the issues.

> **Note:** The prompts we are using here can be adapted based on different perspectives and end users. 

---

## Part 2 — Inspect the provided pipeline lint targets in the IDE

Before writing any pipeline code, use Bob in the IDE to inspect the files that the pipeline linters will scan:

- [`order-service/Dockerfile`](order-service/Dockerfile)
- [`order-service/deploy-flawed/deployment.yaml`](order-service/deploy-flawed/deployment.yaml)
- [`order-service/deploy-flawed/service.yaml`](order-service/deploy-flawed/service.yaml)
- [`order-service/deploy-flawed/route.yaml`](order-service/deploy-flawed/route.yaml)

Start a new task and switch to **Ask** mode. Try a prompt like:

```text
Read @order-service/Dockerfile and the manifests under @order-service/deploy-flawed/.
What issues are likely to be flagged by Hadolint, Checkov, or KubeLinter?
Group them by file and explain which ones are most important to fix first.
```

This gives you immediate Bob-driven feedback before Jenkins is involved.

You should see Bob point out issues such as:

- use of `latest` in container images
- plaintext secrets or credentials in env vars
- missing probes
- missing resource requests and limits
- weak or incomplete `securityContext`
- overly permissive route or service settings

That prediction step is useful for two reasons:

1. it helps you understand what the pipeline scanners are likely to find
2. it gives you a baseline to compare with the actual lint output later

---

## Part 3 — Create the `iac-lint-fix-advisor` IDE mode

Now create a reusable IDE mode that specializes in lint remediation for Dockerfiles and Kubernetes/OpenShift manifests.

Start a new task and switch to **Mode Writer** mode.

Use this as a starter prompt:

```text
Write a custom mode with slug `iac-lint-fix-advisor`. Append it to @.bob/custom_modes.yaml — don't overwrite anything else.

Job: help improve Dockerfiles and Kubernetes/OpenShift deployment manifests for this repo.
Before making edits, read the existing files under @order-service/ and match the repo's style.
Focus on:
- Hadolint findings in @order-service/Dockerfile
- Checkov findings in @order-service/deploy-flawed/
- KubeLinter findings in @order-service/deploy-flawed/

When asked to fix findings:
- explain the issue briefly
- suggest the smallest reasonable remediation
- keep the changes realistic for a workshop app
- avoid overengineering
- preserve readability

Tool groups:
- read
- edit

Add instruction files in Markdown if needed.
```

Once Bob creates the mode, restart the IDE if needed so the new mode appears.

---

## Part 4 — Use the mode to improve one or two findings locally

In a new task, switch to your new **IAC Lint Fix Advisor** mode.

Ask Bob to improve one or two issues in the provided files. For example:

```text
Read @order-service/Dockerfile and @order-service/deploy-flawed/deployment.yaml.
Pick the two highest-value findings and fix them with minimal changes.
Explain what you changed and why.
```

You are not trying to eliminate every single finding in the IDE. The goal is to:

- practice using a specialized remediation mode
- understand how the findings map back to real files
- see Bob make targeted improvements before the pipeline exists

After Bob makes the changes, you can ask in **Ask** mode:

```text
Summarize which likely lint findings remain in @order-service/Dockerfile and @order-service/deploy-flawed/.
```

You can also ask Bob to connect the IDE warm-up to the pipeline-focused files:

```text
Compare the Checkstyle issues we discussed in the Java code with the likely pipeline findings in @order-service/Dockerfile and @order-service/deploy-flawed/.
What themes show up across both, and which issues would you prioritize first from an SRE perspective?
```

That gives you a before-and-after comparison while keeping the command-line lint execution in Jenkins, where it belongs for this lab.

---

## Part 5 — Create the `pipeline-lint-reporter` mode

Your IDE mode is good for making fixes. The pipeline needs something different: a read-only mode that can synthesize raw lint output from multiple tools and turn it into a concise report.

Start a new task and switch to **Mode Writer** mode again.

Use this starter prompt:

```text
Write a custom mode with slug `pipeline-lint-reporter`. Append it to @.bob/custom_modes.yaml — don't overwrite anything else.

Job: read lint output from Checkstyle, Hadolint, Checkov, and KubeLinter, plus the relevant source files under @order-service/.
Produce a short Jenkins-friendly report that:
- groups findings by severity
- identifies overlap across tools
- names the most important fix-first items
- suggests concrete remediations
- stays concise and practical

Output: plain text or Markdown suitable for a Jenkins artifact and easy to summarize in a PR comment.
Use sections:
- Executive Summary
- Highest Priority Findings
- Findings by Tool
- Cross-Tool Themes
- Recommended Fix Order

If findings are duplicated across tools, call that out instead of repeating the same issue many times.

Tool groups: read only.
```

This mode will do the heavy lifting in the pipeline.

---

## Part 6 — Build the linting stages in Jenkins

Start a new task and switch to the provided **Jenkins Pipeline Integration** mode.

Ask Bob to update [`Jenkinsfile`](Jenkinsfile) with a lint workflow after the earlier stages.

Use a prompt like:

```text
Update @Jenkinsfile to add linting and reporting stages after the existing earlier lab stages.

Requirements:
- Add a `lint-tools` container to the Kubernetes agent pod YAML using the workshop lint image
- Run Checkstyle on the Java code: `mvn -f order-service/pom.xml checkstyle:check`
- Copy the Checkstyle XML report to `lint-results/checkstyle.xml`
- Run Hadolint on @order-service/Dockerfile
- Run Checkov on @order-service/deploy-flawed/
- Run KubeLinter on @order-service/deploy-flawed/
- Save each tool's output into a `lint-results/` directory in the workspace
- Continue the pipeline even if the linters find issues
- Call askBob with the `pipeline-lint-reporter` mode to analyze the raw lint outputs and the relevant files under @order-service/
- Save the full analysis to `bob-lint-report.md`
- Save a condensed PR comment body to `bob-lint-pr-comment.md`
- Archive the lint outputs and Bob-generated report files
- Print a short summary to the console
- Post the PR comment to GitHub using a Jenkins-provided token
```

### Recommended stage shape

A good implementation will usually split the work into stages such as:

- `Run Linters` (runs Checkstyle, Hadolint, Checkov, KubeLinter)
- `Bob Lint Analysis` (analyzes all findings)
- `Post Lint PR Comment` (posts summary to GitHub)

### Recommended output files

Your pipeline should produce files like:

- `lint-results/checkstyle.xml` (or checkstyle.txt)
- `lint-results/hadolint.txt`
- `lint-results/checkov.txt`
- `lint-results/kubelinter.txt`
- `bob-lint-report.md`
- `bob-lint-pr-comment.md`

### Important design pattern

The linters should run in their appropriate containers:
- Checkstyle runs in the `build-tools` (Maven) container
- Hadolint, Checkov, and KubeLinter run in the `lint-tools` container

The Bob analysis should run through [`askBob()`](labs/sre/lab1/Jenkinsfile.lab1solution:153).

Jenkins should orchestrate:

- running the tools
- saving files
- archiving artifacts
- posting the PR comment

Bob should do the interpretation:

- grouping findings
- prioritizing fixes
- suggesting remediation
- generating the report text

### Example Checkstyle Stage Snippet

```groovy
stage('Run Linters') {
    steps {
        script {
            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                // Run Checkstyle in Maven container
                sh '''
                    mkdir -p lint-results
                    mvn -f order-service/pom.xml checkstyle:check || true
                    cp order-service/target/checkstyle-result.xml lint-results/checkstyle.xml || true
                '''
                
                // Run other linters in lint-tools container
                container('lint-tools') {
                    sh '''
                        hadolint order-service/Dockerfile > lint-results/hadolint.txt || true
                        checkov -d order-service/deploy-flawed -o cli > lint-results/checkov.txt || true
                        kube-linter lint order-service/deploy-flawed > lint-results/kubelinter.txt || true
                    '''
                }
            }
        }
    }
}
```

---

## Part 7 — Push and watch

Once your Jenkinsfile and mode definitions are ready:

```bash
git add Jenkinsfile .bob/ order-service/deploy-flawed/
git commit -m "Lab 4 — linting and compliance with Bob (Checkstyle edition)"
git push
```

In Jenkins, click **Build Now** and watch the pipeline.

Expected behavior:

- earlier stages still run
- Checkstyle runs in the Maven container
- the other lint tools run inside the `lint-tools` container
- raw outputs are written under `lint-results/`
- Bob prints a short summary in the console
- [`bob-lint-report.md`](labs/sre/lab4/bob-lint-report.md) is archived as a build artifact
- the pipeline posts a condensed lint summary comment to the PR
- the build may end **UNSTABLE** if findings exist, but should still complete

When you open the artifact, you should see a consolidated report that is far more useful than the raw scanner output alone.

---

## Part 8 — Optional: post a Bob-generated lint summary to GitHub from the IDE

If your Bob IDE is configured with the GitHub MCP server, you can also demonstrate the report workflow before Jenkins runs.

Suggested flow:

1. Generate or refine a lint summary in the IDE using Bob.
2. Switch to **Advanced** mode.
3. Ask Bob to post the summary as a PR comment using the GitHub MCP server.

For example:

```text
Read @bob-lint-pr-comment.md and post it as a comment to my current pull request using the GitHub MCP server.
```

This is optional and intentionally separate from the Jenkins path. The core lab should still work even if GitHub MCP is not configured in the IDE.

---

## Part 9 — Optional: Add Error Prone for compile-time bug detection

[Error Prone](https://errorprone.info/) is Google's static analysis tool that catches common Java mistakes at compile time. Unlike Checkstyle (which focuses on style and conventions), Error Prone finds actual bugs like null pointer dereferences, resource leaks, and incorrect API usage.

### Why Error Prone?

- **Compile-time detection**: Catches bugs during compilation, not as a separate linting step
- **Low false positives**: Focuses on real bugs, not style preferences
- **Complements Checkstyle**: Checkstyle handles style, Error Prone handles correctness
- **Production-ready**: Used extensively at Google and other large organizations

### Adding Error Prone to Your Project

#### Step 1: Update pom.xml

Add Error Prone to your [`order-service/pom.xml`](order-service/pom.xml) build configuration:

```xml
<build>
    <plugins>
        <!-- Existing Spring Boot plugin -->
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
        </plugin>
        
        <!-- Existing Checkstyle plugin -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-checkstyle-plugin</artifactId>
            <version>3.3.1</version>
            <configuration>
                <configLocation>google_checks.xml</configLocation>
            </configuration>
        </plugin>
        
        <!-- Add Error Prone -->
        <plugin>
            <groupId>org.apache.maven.plugins</groupId>
            <artifactId>maven-compiler-plugin</artifactId>
            <version>3.11.0</version>
            <configuration>
                <source>17</source>
                <target>17</target>
                <compilerArgs>
                    <arg>-XDcompilePolicy=simple</arg>
                    <arg>-Xplugin:ErrorProne</arg>
                </compilerArgs>
                <annotationProcessorPaths>
                    <path>
                        <groupId>com.google.errorprone</groupId>
                        <artifactId>error_prone_core</artifactId>
                        <version>2.23.0</version>
                    </path>
                </annotationProcessorPaths>
            </configuration>
        </plugin>
    </plugins>
</build>
```

#### Step 2: Test Error Prone Locally

Run a Maven compile to see Error Prone in action:

```bash
cd order-service
mvn clean compile
```

Error Prone will report issues during compilation. For example:

```
[ERROR] /path/to/OrderService.java:[45,20] [MissingOverride] method overrides method in supertype but is missing @Override
```

#### Step 3: Ask Bob to Analyze Error Prone Findings

Switch to **Ask** mode and try:

```text
I ran `mvn clean compile` with Error Prone enabled. Here are the findings:
[paste Error Prone output]

Explain:
1. Which findings are most critical?
2. How do these differ from Checkstyle findings?
3. What should I fix first?
```

#### Step 4: Add Error Prone to Jenkins Pipeline (Optional)

Error Prone runs automatically during compilation, so it's already included if your pipeline compiles the code. However, you can make the findings more visible:

```groovy
stage('Compile with Error Prone') {
    steps {
        script {
            catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                sh '''
                    mvn -f order-service/pom.xml clean compile 2>&1 | tee lint-results/errorprone.txt || true
                '''
            }
        }
    }
}
```

Then update your Bob lint analysis prompt to include Error Prone:

```text
Read the lint output files in lint-results/ including:
- lint-results/checkstyle.xml
- lint-results/errorprone.txt
- lint-results/hadolint.txt
- lint-results/checkov.txt
- lint-results/kubelinter.txt

Analyze all findings and create a consolidated report...
```

### Error Prone vs. Checkstyle: When to Use Each

| Tool | Focus | When to Use |
|------|-------|-------------|
| **Checkstyle** | Code style and conventions | Enforce team coding standards, maintain consistency |
| **Error Prone** | Bug detection and correctness | Catch actual bugs, prevent runtime errors |

**Best Practice**: Use both! Checkstyle keeps code readable and consistent, while Error Prone catches bugs that could cause production issues.

---

## Stuck?

- **The `lint-tools` container is missing.** The workshop environment may not have been prepared for the lint lab yet. Follow [`setup/LINT_TOOLS_SETUP.md`](setup/LINT_TOOLS_SETUP.md) and ensure the pod YAML in [`Jenkinsfile`](Jenkinsfile) includes the `lint-tools` container.
- **Checkstyle fails with `command not found`.** Checkstyle runs via Maven, not as a standalone command. Use `mvn checkstyle:check` in the Maven container, not the lint-tools container.
- **Hadolint, Checkov, or KubeLinter fail with `command not found`.** The image was built incorrectly or the wrong image is referenced in the Jenkins pod YAML. Verify the image from [`setup/lint-tools/Dockerfile`](setup/lint-tools/Dockerfile) was pushed and is being used.
- **The linters fail the build before Bob can analyze anything.** Wrap the lint command block in `catchError` or use `|| true` so output files are still written and Bob can read them.
- **Checkstyle output is in XML format.** That's expected. Bob can read XML. Alternatively, use `mvn checkstyle:checkstyle` to generate an HTML report, or parse the XML to plain text if needed.
- **Checkov output is huge and noisy.** Narrow the scan target to [`order-service/deploy-flawed/`](order-service/deploy-flawed) rather than the whole repo.
- **KubeLinter reports nothing useful.** Make sure you are linting the deployment manifests, especially [`order-service/deploy-flawed/deployment.yaml`](order-service/deploy-flawed/deployment.yaml).
- **Bob's report repeats the same issue multiple times.** Refine the `pipeline-lint-reporter` mode so it explicitly de-duplicates overlapping findings across tools.
- **The PR comment step fails.** Check that Jenkins has the expected GitHub PAT credential configured and that your pipeline knows the PR number or can discover it from the job context.
- **Error Prone compilation fails.** Ensure you're using Java 11 or later and Maven 3.6+. Check that the Error Prone version is compatible with your Java version.
- **`Jenkinsfile` not working?** Use the reference solution in [`labs/sre/lab4/Jenkinsfile.lab4solution`](labs/sre/lab4/Jenkinsfile.lab4solution) as your reset point once it is available in the repo.

---

When you're ready, continue to [`labs/sre/lab5/LAB5_DCR_JIRA.md`](labs/sre/lab5/LAB5_DCR_JIRA.md).