// ═══════════════════════════════════════════════════════════════════
// FIS Bob-a-thon — Base Pipeline (Jenkinsfile)
//
// Starting point for the 5-lab workshop. Provisions a Kubernetes
// agent pod with three containers — build-tools (Maven + JDK17),
// oc-tools (OpenShift CLI), and bob (IBM Bob CLI) — sharing a
// workspace-volume emptyDir mounted at /workspace on all three,
// with HOME set to /workspace so Bob can read .bob/custom_modes.yaml
// from the checkout.
//
// This file has a single Checkout stage. Each lab adds one more
// stage beneath it; see labs/LAB<N>_*.md for instructions.
//
// Before running: if your OpenShift project is NOT named `jenkins`,
// update the `bob` container image URL below.
// ═══════════════════════════════════════════════════════════════════

pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
  - name: build-tools
    image: maven:3.9-eclipse-temurin-17
    command: ['sleep', 'infinity']
    workingDir: /workspace
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace
    env:
    - name: HOME
      value: /workspace
  - name: oc-tools
    image: quay.io/openshift/origin-cli:latest
    command: ['sleep', 'infinity']
    workingDir: /workspace
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace
    env:
    - name: HOME
      value: /workspace
  - name: lint-tools
    image: image-registry.openshift-image-registry.svc:5000/jenkins/lint-tools:latest
    command: ['sleep', 'infinity']
    workingDir: /workspace
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace
    env:
    - name: HOME
      value: /workspace
  - name: bob
    image: image-registry.openshift-image-registry.svc:5000/jenkins/bob-cli:latest
    command: ['sleep', 'infinity']
    workingDir: /workspace
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace
    env:
    - name: BOBSHELL_API_KEY
      valueFrom:
        secretKeyRef:
          name: bob-cli-credentials
          key: BOBSHELL_API_KEY
    - name: BOB_ACCEPT_LICENSE
      value: "true"
    - name: HOME
      value: /workspace
  volumes:
  - name: workspace-volume
    emptyDir: {}
"""
            defaultContainer 'build-tools'
        }
    }

    stages {
        stage('Checkout') {
            steps {
                echo "=== Checking out repository ==="
                checkout scm

                echo "=== Verifying workspace contents ==="
                sh '''
                    echo "Current directory: $(pwd)"
                    echo "Workspace contents:"
                    ls -la
                '''
            }
        }

        // ── Lab 1: PR / Git Diff Review ──────────────────────────
        stage('PR Review') {
            options {
                timeout(time: 5, unit: 'MINUTES')
            }
            steps {
                script {
                    echo '════════════════════════════════════════════════════════'
                    echo '  Bob — PR Review'
                    echo '════════════════════════════════════════════════════════'
                    
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        // Configure git safe directory and compute diff
                        sh '''
                            git config --global --add safe.directory "$WORKSPACE"
                            git diff origin/main...HEAD > git-diff.txt || : > git-diff.txt
                        '''
                        
                        // Ask Bob to analyze the diff
                        def analysis = askBob(
                            "Read git-diff.txt and produce the senior-developer PR overview.",
                            'solution-pipeline-git-diff-overview'
                        )
                        
                        echo analysis
                        echo '════════════════════════════════════════════════════════'
                        
                        // Save analysis for archiving
                        writeFile file: 'bob-pr-review.md', text: analysis
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bob-pr-review.md', allowEmptyArchive: true
                }
            }
        }

        // ── Lab 2: Unit Testing ──────────────────────────────────

        // ── Lab 3: Security Scanning ─────────────────────────────

        // ── Lab 4: Linting ───────────────────────────────────────
        stage('Run Linters') {
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            steps {
                script {
                    echo '════════════════════════════════════════════════════════'
                    echo '  Running Linters'
                    echo '════════════════════════════════════════════════════════'
                    
                    // Create lint-results directory
                    sh 'mkdir -p lint-results'
                    
                    // Run Checkstyle
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        echo '  → Running Checkstyle...'
                        sh 'mvn -f order-service/pom.xml checkstyle:check || true'
                        sh 'cp order-service/target/checkstyle-result.xml lint-results/checkstyle.xml || true'
                    }
                    
                    // Run Hadolint
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        container('lint-tools') {
                            echo '  → Running Hadolint...'
                            sh 'hadolint order-service/Dockerfile > lint-results/hadolint.txt || true'
                        }
                    }
                    
                    // Run Checkov
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        container('lint-tools') {
                            echo '  → Running Checkov...'
                            sh 'checkov -d order-service/deploy-flawed/ --compact --quiet > lint-results/checkov.txt || true'
                        }
                    }
                    
                    // Run KubeLinter
                    catchError(buildResult: 'UNSTABLE', stageResult: 'UNSTABLE') {
                        container('lint-tools') {
                            echo '  → Running KubeLinter...'
                            sh 'kube-linter lint order-service/deploy-flawed/ > lint-results/kubelinter.txt || true'
                        }
                    }
                    
                    echo '════════════════════════════════════════════════════════'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'lint-results/*', allowEmptyArchive: true
                }
            }
        }

        stage('Bob Lint Analysis') {
            when {
                expression {
                    return fileExists('lint-results/checkstyle.xml') ||
                           fileExists('lint-results/hadolint.txt') ||
                           fileExists('lint-results/checkov.txt') ||
                           fileExists('lint-results/kubelinter.txt')
                }
            }
            options {
                timeout(time: 10, unit: 'MINUTES')
            }
            steps {
                script {
                    echo '════════════════════════════════════════════════════════'
                    echo '  Bob — Lint Analysis'
                    echo '════════════════════════════════════════════════════════'
                    
                    catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                        // Build prompt telling Bob to read the files directly
                        def prompt = """
Analyze the linting results from multiple tools and provide a consolidated report.

Read and analyze the following lint result files:
- lint-results/checkstyle.xml
- lint-results/hadolint.txt
- lint-results/checkov.txt
- lint-results/kubelinter.txt

Also review the source code and configurations:
- order-service/src/
- order-service/Dockerfile
- order-service/deploy-flawed/

Your analysis should:
1. Group findings by severity (Critical, High, Medium, Low)
2. De-duplicate overlapping findings from different tools
3. Identify the highest-priority remediations
4. Recommend concrete fixes with code examples

Produce a comprehensive markdown report.
"""
                        
                        // Ask Bob to analyze the lint results
                        def analysis = askBob(prompt, 'pipeline-lint-analyzer')
                        
                        echo ''
                        echo '  ✅ Lint analysis complete'
                        
                        // Save full analysis
                        writeFile file: 'bob-lint-report.md', text: analysis
                        
                        // Generate PR comment
                        def prCommentPrompt = """
Read bob-lint-report.md and produce a concise PR comment summarizing the key findings.

The comment should:
- Be brief (max 10-15 lines)
- Highlight critical and high-severity issues only
- Include a count of findings by severity
- Provide 2-3 top priority action items
- Use markdown formatting suitable for a GitHub PR comment

Keep it actionable and focused on what developers need to fix first.
"""
                        
                        def prComment = askBob(prCommentPrompt, 'pipeline-lint-analyzer')
                        
                        // Save PR comment
                        writeFile file: 'bob-lint-pr-comment.md', text: prComment
                        
                        // Print summary to console
                        echo ''
                        echo '  📊 Summary:'
                        if (analysis.contains('Critical')) {
                            echo '    🔴 Critical issues found'
                        }
                        if (analysis.contains('High')) {
                            echo '    🟠 High-severity issues found'
                        }
                        echo '    📄 Full report: bob-lint-report.md'
                        echo '    💬 PR comment: bob-lint-pr-comment.md'
                    }
                    
                    echo '════════════════════════════════════════════════════════'
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bob-lint-report.md,bob-lint-pr-comment.md',
                                   allowEmptyArchive: true
                }
            }
        }

        // ── Lab 5: DCR & Reporting ───────────────────────────────
    }

    post {
        always {
            echo "=== Pipeline Complete ==="
            echo "Result: ${currentBuild.result ?: 'SUCCESS'}"
        }
    }
}

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