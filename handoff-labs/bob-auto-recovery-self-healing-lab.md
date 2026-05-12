# Lab: Auto-Recovery and Self-Healing with Bob in Jenkins Pipelines

**Duration:** ~45 minutes
**Level:** Intermediate to Advanced
**Prerequisites:**
- Jenkins pipeline knowledge
- Maven familiarity
- Access to Jenkins environment with Bob CLI

---

## Table of Contents

- [Overview](#overview)
- [Understanding Auto-Recovery in CI/CD](#understanding-auto-recovery-in-cicd)
- [Part 1: Detecting and Recovering from Build Failures](#part-1-detecting-and-recovering-from-build-failures)
- [Part 2: Self-Healing Test Failures](#part-2-self-healing-test-failures)
- [Part 3: Automated Dependency Resolution](#part-3-automated-dependency-resolution)
- [Part 4: Building a Self-Healing Pipeline Mode](#part-4-building-a-self-healing-pipeline-mode)
- [Best Practices](#best-practices)
- [Key Takeaways](#key-takeaways)

---

## Overview

### What You'll Build

In this lab, you'll extend your existing Jenkins pipeline with self-healing capabilities:

1. **Automated error detection** - Bob analyzes failures and identifies root causes
2. **Intelligent recovery** - Bob attempts automatic fixes for common issues
3. **Verification loops** - Bob validates fixes before proceeding
4. **Self-healing pipeline mode** - A custom mode that orchestrates recovery workflows

### Learning Objectives

By the end of this lab, you will be able to:

- ✅ Implement automated error detection in Jenkins pipelines
- ✅ Create self-healing stages that recover from common failures
- ✅ Build custom modes for auto-recovery workflows
- ✅ Integrate Bob's analysis with automated remediation
- ✅ Monitor and improve self-healing effectiveness

### Why Auto-Recovery Matters in CI/CD

**Traditional Pipeline:**
```
Build fails → Developer notified → Manual investigation → 
Fix applied → Pipeline rerun → Hours of downtime
```

**Self-Healing Pipeline:**
```
Build fails → Bob analyzes → Automatic fix attempted → 
Tests verify → Pipeline continues or reports → Minutes of recovery
```

---

## Understanding Auto-Recovery in CI/CD

### Common Recoverable Scenarios

| Scenario | Detection | Recovery Action |
|----------|-----------|-----------------|
| **Maven Build Failure** | Compilation errors, missing dependencies | Update pom.xml, resolve conflicts |
| **Test Failures** | JUnit/Surefire failures | Fix test code, update assertions |
| **Dependency Conflicts** | Version mismatches | Resolve dependency tree |
| **Configuration Errors** | Missing properties, wrong values | Update application.properties |
| **Code Quality Issues** | Linting failures | Apply auto-fixes |

### Bob's Auto-Recovery Workflow

```
┌─────────────────────────────────────────────────────────┐
│                   PIPELINE STAGE                        │
│                  (Build/Test/Lint)                      │
└─────────────────────────────────────────────────────────┘
                          ↓
                    [Success?]
                          ↓ No
┌─────────────────────────────────────────────────────────┐
│              BOB ERROR ANALYSIS                         │
│  - Read error logs                                      │
│  - Identify root cause                                  │
│  - Determine if auto-fixable                            │
└─────────────────────────────────────────────────────────┘
                          ↓
                  [Auto-fixable?]
                          ↓ Yes
┌─────────────────────────────────────────────────────────┐
│              BOB APPLIES FIX                            │
│  - Modify source files                                  │
│  - Update configurations                                │
│  - Commit changes                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              VERIFICATION                               │
│  - Rerun failed stage                                   │
│  - Validate fix worked                                  │
│  - Report results                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Part 1: Detecting and Recovering from Build Failures

### Exercise 1.1: Create a Build Failure Detection Mode

We'll create a custom mode that analyzes Maven build failures and suggests fixes.

**Step 1: Switch to Mode Writer**

Start a new task and switch to **Mode Writer** mode. Use this prompt:

```
Create a custom mode with slug `pipeline-build-recovery`. Append it to @.bob/custom_modes.yaml.

Job: Analyze Maven build failures in Jenkins pipelines and attempt automatic recovery.

Responsibilities:
- Read Maven build logs from the workspace
- Identify the root cause (compilation errors, missing dependencies, plugin issues)
- Determine if the issue is auto-fixable
- For auto-fixable issues: modify pom.xml or source files to resolve
- For non-auto-fixable issues: provide detailed guidance for manual fix

Recovery patterns to handle:
1. Missing dependencies - add to pom.xml
2. Version conflicts - resolve dependency tree
3. Simple compilation errors - fix syntax issues
4. Plugin configuration errors - update plugin config

Output format: Plain text for Jenkins console with sections:
- Root Cause Analysis
- Auto-Fix Applied (if applicable)
- Verification Steps
- Manual Action Required (if not auto-fixable)

Tool groups: read, edit (Java and XML files only), command (for mvn commands)

File restrictions: Only edit files matching: \.(java|xml|properties)$
```

**Step 2: Test the Mode Locally**

Before adding to the pipeline, test the mode in your IDE:

```bash
# Introduce a build failure
# Edit order-service/pom.xml and remove a required dependency

# Switch to your new mode
# Ask Bob to analyze and fix the build failure
```

### Exercise 1.2: Add Self-Healing Build Stage

Now integrate the mode into your Jenkins pipeline.

**Step 1: Switch to Jenkins Pipeline Integration Mode**

Start a new task and use the **Jenkins Pipeline Integration** mode:

```
Add a self-healing wrapper around the existing build stage in @Jenkinsfile.

The stage should:
1. Try to build with: mvn clean package -DskipTests
2. If build fails, capture the error log
3. Call askBob with the pipeline-build-recovery mode
4. Let Bob analyze and attempt auto-fix
5. If Bob applied a fix, retry the build once
6. Archive both the error log and Bob's analysis
7. Use catchError so pipeline continues even if recovery fails

Structure:
- Use container('build-tools') for Maven commands
- Use container('bob') via askBob helper
- Write error logs to build-error.log
- Archive bob-build-recovery.md
```

**Expected Stage Structure:**

```groovy
stage('Build with Auto-Recovery') {
    steps {
        script {
            def buildSuccess = false
            def recoveryAttempted = false
            
            container('build-tools') {
                // First build attempt
                def buildResult = sh(
                    script: 'mvn clean package -DskipTests',
                    returnStatus: true
                )
                
                if (buildResult == 0) {
                    buildSuccess = true
                    echo "✅ Build succeeded"
                } else {
                    echo "❌ Build failed, attempting auto-recovery..."
                    
                    // Capture error for Bob
                    sh 'mvn clean package -DskipTests > build-error.log 2>&1 || true'
                    
                    // Ask Bob to analyze and fix
                    def prompt = """Analyze the Maven build failure in build-error.log.
                    
If the issue is auto-fixable (missing dependency, version conflict, simple syntax error):
1. Apply the fix to the appropriate files
2. Explain what you fixed
3. Indicate that a retry should be attempted

If not auto-fixable:
1. Explain the root cause
2. Provide step-by-step manual fix instructions"""
                    
                    def analysis = askBob(prompt, 'pipeline-build-recovery')
                    writeFile file: 'bob-build-recovery.md', text: analysis
                    
                    // Check if Bob indicated a fix was applied
                    if (analysis.contains('Fix applied') || analysis.contains('fix applied')) {
                        echo "🔧 Bob applied a fix, retrying build..."
                        recoveryAttempted = true
                        
                        buildResult = sh(
                            script: 'mvn clean package -DskipTests',
                            returnStatus: true
                        )
                        
                        if (buildResult == 0) {
                            buildSuccess = true
                            echo "✅ Build succeeded after auto-recovery!"
                        }
                    }
                }
            }
            
            // Archive results
            archiveArtifacts artifacts: 'bob-build-recovery.md', allowEmptyArchive: true
            archiveArtifacts artifacts: 'build-error.log', allowEmptyArchive: true
            
            if (!buildSuccess) {
                error("Build failed" + (recoveryAttempted ? " even after auto-recovery attempt" : ""))
            }
        }
    }
}
```

**Step 3: Test the Self-Healing Build**

```bash
# Commit and push
git add .bob/custom_modes.yaml Jenkinsfile
git commit -m "Add self-healing build stage"
git push

# In Jenkins, click Build Now
# Watch the console output to see Bob's recovery attempt
```

---

## Part 2: Self-Healing Test Failures

### Exercise 2.1: Extend Test Analysis for Auto-Fix

We already have a test failure analyzer from Lab 2. Let's enhance it with auto-fix capabilities.

**Step 1: Create Enhanced Test Recovery Mode**

Switch to **Mode Writer** and create:

```
Create a custom mode with slug `pipeline-test-auto-healer`. Append to @.bob/custom_modes.yaml.

Job: Analyze JUnit test failures and automatically fix simple issues.

Auto-fixable test issues:
1. Assertion mismatches (expected vs actual) - update test assertions
2. Null pointer exceptions in tests - add null checks
3. Mock configuration issues - fix mock setup
4. Test data issues - update test data
5. Timeout issues - increase timeout values

Non-auto-fixable issues (provide guidance only):
1. Logic errors in production code
2. Complex integration failures
3. Environmental issues

Process:
1. Read test failure reports from target/surefire-reports/
2. Read failing test source files
3. Identify if issue is in test code or production code
4. For test code issues: apply fix and explain
5. For production code issues: provide detailed fix guidance

Output: Plain text with sections:
- Test Failure Summary
- Root Cause Analysis
- Auto-Fixes Applied (with file paths and line numbers)
- Manual Fixes Required (if any)
- Verification Command

Tool groups: read, edit (Java files only), command (for test execution)
File restrictions: \.(java)$
```

**Step 2: Add Self-Healing Test Stage**

Update your test stage to include auto-recovery:

```groovy
stage('Unit Tests with Auto-Healing') {
    steps {
        script {
            def testsPass = false
            def healingAttempted = false
            
            container('build-tools') {
                // First test run
                def testResult = sh(
                    script: 'mvn test',
                    returnStatus: true
                )
                
                if (testResult == 0) {
                    testsPass = true
                    echo "✅ All tests passed"
                } else {
                    echo "❌ Tests failed, attempting auto-healing..."
                    
                    // Let Bob analyze and potentially fix
                    def prompt = """Analyze the test failures in target/surefire-reports/.
                    
For each failure:
1. Determine if it's a test code issue or production code issue
2. If it's a simple test code issue (assertion, mock, null check), fix it automatically
3. If it's a production code issue, provide detailed fix guidance

After applying any fixes, indicate whether tests should be rerun."""
                    
                    def analysis = askBob(prompt, 'pipeline-test-auto-healer')
                    writeFile file: 'bob-test-healing.md', text: analysis
                    
                    // Check if Bob applied fixes
                    if (analysis.contains('Fix applied') || analysis.contains('fixes applied')) {
                        echo "🔧 Bob applied test fixes, rerunning tests..."
                        healingAttempted = true
                        
                        testResult = sh(
                            script: 'mvn test',
                            returnStatus: true
                        )
                        
                        if (testResult == 0) {
                            testsPass = true
                            echo "✅ Tests passed after auto-healing!"
                        }
                    }
                }
            }
            
            // Always archive results
            archiveArtifacts artifacts: 'bob-test-healing.md', allowEmptyArchive: true
            archiveArtifacts artifacts: 'target/surefire-reports/*.xml', allowEmptyArchive: true
            
            if (!testsPass) {
                unstable("Tests failed" + (healingAttempted ? " even after auto-healing" : ""))
            }
        }
    }
}
```

---

## Part 3: Automated Dependency Resolution

### Exercise 3.1: Dependency Conflict Auto-Resolution

**Step 1: Create Dependency Resolution Mode**

```
Create a custom mode with slug `pipeline-dependency-resolver`. Append to @.bob/custom_modes.yaml.

Job: Resolve Maven dependency conflicts automatically.

Capabilities:
1. Analyze dependency tree conflicts
2. Identify version mismatches
3. Apply dependency management best practices
4. Update pom.xml with resolutions

Resolution strategies:
- Use dependency management section for version control
- Add explicit exclusions for transitive conflicts
- Upgrade to compatible versions
- Document why each resolution was chosen

Output: Plain text with:
- Conflict Analysis
- Resolution Strategy
- Changes Applied to pom.xml
- Verification Steps

Tool groups: read, edit (XML only), command (mvn dependency:tree)
File restrictions: \.xml$
```

**Step 2: Add Dependency Check Stage**

```groovy
stage('Dependency Health Check') {
    steps {
        container('build-tools') {
            script {
                echo "=== Checking dependency health ==="
                
                // Generate dependency tree
                sh 'mvn dependency:tree > dependency-tree.txt 2>&1 || true'
                
                // Check for conflicts
                def hasConflicts = sh(
                    script: 'grep -i "conflict" dependency-tree.txt || true',
                    returnStdout: true
                ).trim()
                
                if (hasConflicts) {
                    echo "⚠️ Dependency conflicts detected, attempting resolution..."
                    
                    def prompt = """Analyze the dependency tree in dependency-tree.txt.
                    
Identify all conflicts and:
1. Determine the best resolution strategy
2. Update pom.xml to resolve conflicts
3. Explain each change made
4. Verify the resolution works"""
                    
                    def analysis = askBob(prompt, 'pipeline-dependency-resolver')
                    writeFile file: 'bob-dependency-resolution.md', text: analysis
                    
                    // Verify resolution
                    sh 'mvn dependency:tree'
                    echo "✅ Dependencies resolved"
                } else {
                    echo "✅ No dependency conflicts found"
                }
                
                archiveArtifacts artifacts: 'dependency-tree.txt', allowEmptyArchive: true
                archiveArtifacts artifacts: 'bob-dependency-resolution.md', allowEmptyArchive: true
            }
        }
    }
}
```

---

## Part 4: Building a Self-Healing Pipeline Mode

### Exercise 4.1: Create Orchestrator Mode for Self-Healing

Now let's create a master mode that orchestrates all self-healing capabilities.

**Step 1: Create Self-Healing Orchestrator Mode**

```
Create a custom mode with slug `pipeline-self-healing-orchestrator`. Append to @.bob/custom_modes.yaml.

Job: Orchestrate self-healing across the entire pipeline.

This mode coordinates recovery efforts:
1. Monitors pipeline stage failures
2. Determines appropriate recovery strategy
3. Delegates to specialized recovery modes
4. Tracks recovery attempts and success rates
5. Escalates to humans when auto-recovery fails

Decision tree:
- Build failure → pipeline-build-recovery
- Test failure → pipeline-test-auto-healer  
- Dependency issue → pipeline-dependency-resolver
- Unknown failure → Detailed analysis + manual guidance

Output: Structured report with:
- Failure Summary
- Recovery Strategy Selected
- Recovery Outcome
- Lessons Learned (for future prevention)
- Escalation Required (yes/no)

Tool groups: read, edit (all source files), command, mcp (if available)
```

**Step 2: Add Orchestrator Post-Build Action**

```groovy
post {
    failure {
        script {
            echo "=== Pipeline failed, initiating self-healing analysis ==="
            
            container('bob') {
                def prompt = """The pipeline has failed. Analyze all available logs and artifacts:
                - build-error.log (if exists)
                - target/surefire-reports/ (if exists)
                - dependency-tree.txt (if exists)
                - Console output
                
Determine:
1. What failed and why
2. Was auto-recovery attempted? Did it work?
3. What should be done next?
4. Can this failure be prevented in the future?

Provide a comprehensive post-mortem and recommendations."""
                
                def analysis = askBob(prompt, 'pipeline-self-healing-orchestrator')
                writeFile file: 'bob-pipeline-postmortem.md', text: analysis
                archiveArtifacts artifacts: 'bob-pipeline-postmortem.md'
                
                echo "📊 Self-healing analysis complete. Check bob-pipeline-postmortem.md"
            }
        }
    }
    
    success {
        script {
            // Check if any recovery was performed
            def recoveryFiles = findFiles(glob: 'bob-*-recovery.md')
            if (recoveryFiles.length > 0) {
                echo "✅ Pipeline succeeded with auto-recovery assistance"
                echo "📈 Recovery files: ${recoveryFiles.collect { it.name }.join(', ')}"
            }
        }
    }
}
```

---

## Best Practices

### 1. **Limit Auto-Fix Scope**
- Only auto-fix low-risk issues (test assertions, formatting, simple syntax)
- Always require human review for production code logic changes
- Use file restrictions to limit what modes can modify

### 2. **Verification is Critical**
- Always rerun tests/builds after applying fixes
- Archive before/after states for audit trail
- Set maximum retry attempts (typically 1-2)

### 3. **Fail Safely**
- Use `catchError` to prevent recovery failures from blocking pipeline
- Mark builds as UNSTABLE rather than FAILED when recovery is attempted
- Always provide detailed logs for manual investigation

### 4. **Monitor and Learn**
- Track recovery success rates
- Identify patterns in failures
- Update modes based on common issues
- Share learnings across teams

### 5. **Security Considerations**
- Never auto-commit fixes to main branch
- Require PR review for auto-generated fixes
- Limit file modification permissions
- Audit all automated changes

---

## Key Takeaways

### What You've Learned

1. ✅ **Auto-recovery patterns** - How to detect, analyze, and fix common CI/CD failures
2. ✅ **Self-healing modes** - Creating specialized modes for different recovery scenarios
3. ✅ **Pipeline integration** - Embedding recovery logic into Jenkins stages
4. ✅ **Verification loops** - Ensuring fixes actually work before proceeding
5. ✅ **Orchestration** - Coordinating multiple recovery strategies

### Real-World Applications

- **Reduce MTTR** - From hours to minutes for common failures
- **Improve developer experience** - Fewer interruptions, more focus time
- **Increase deployment confidence** - Automated safety nets catch issues early
- **Learn from failures** - Build institutional knowledge into modes

---

## Additional Resources

- [Bob Custom Modes Documentation](https://bob.ibm.com/docs/ide/configuration/custom-modes)
- [Jenkins Pipeline Best Practices](https://www.jenkins.io/doc/book/pipeline/pipeline-best-practices/)
- [Maven Dependency Management](https://maven.apache.org/guides/introduction/introduction-to-dependency-mechanism.html)
- Workshop Labs 1-2 for foundational pipeline patterns

---

**Congratulations!** You've built a self-healing CI/CD pipeline that can automatically detect and recover from common failures. This reduces operational burden and improves developer productivity.