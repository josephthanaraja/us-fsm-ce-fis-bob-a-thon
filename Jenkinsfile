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

// Per-instance Jira credential routing. Each pipeline self-selects which
// jira-creds-{a,b,c} secret to mount based on the user number parsed
// from its job name. See setup/JIRA_ACCOUNT_SETUP.md Section 3.3.
def jobName = env.JOB_NAME ?: ''
def userMatch = jobName =~ /user0*(\d+)/
def userNum = userMatch ? userMatch[0][1].toInteger() : 0
def jiraSecret = (userNum >= 1  && userNum <= 5)  ? 'jira-creds-a' :
                 (userNum >= 6  && userNum <= 10) ? 'jira-creds-b' :
                 (userNum >= 11 && userNum <= 15) ? 'jira-creds-c' :
                                                    'jira-creds-c'

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
    - name: JIRA_URL
      valueFrom:
        secretKeyRef:
          name: ${jiraSecret}
          key: JIRA_URL
    - name: JIRA_USERNAME
      valueFrom:
        secretKeyRef:
          name: ${jiraSecret}
          key: JIRA_USERNAME
    - name: JIRA_API_TOKEN
      valueFrom:
        secretKeyRef:
          name: ${jiraSecret}
          key: JIRA_API_TOKEN
    - name: JIRA_PROJECT
      valueFrom:
        secretKeyRef:
          name: ${jiraSecret}
          key: JIRA_PROJECT
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
        //    Add a stage here that runs Bob in a "senior developer"
        //    mode against the git diff. See labs/LAB1_PR_REVIEW.md.

        // ── Lab 2: Unit Testing ──────────────────────────────────
        //    Add a mvn test stage + Bob test-failure analysis.
        //    See labs/LAB2_UNIT_TESTING.md.

        // ── Lab 3: Security Scanning ─────────────────────────────
        //    Add a scanner stage + Bob CVE/vuln analysis.
        //    See labs/LAB3_SECURITY_SCANNING.md.

        // ── Lab 4: Linting ───────────────────────────────────────
        //    Add a lint stage + Bob lint analysis + parse and post
        //    Jenkins report as a PR comment.
        //    See labs/LAB4_LINTING.md.

        // ── Lab 5: DCR & Reporting ───────────────────────────────
        //    Add a DCR generation stage; Bob pushes the result to
        //    Jira via the Jira MCP server.
        //    See labs/LAB5_DCR_REPORTING.md.

        stage('Jira MCP Smoke Test') {
            steps {
                container('bob') {
                    sh '''
                        set -e
                        set -x

                        # Fail fast if any required JIRA env var is missing.
                        : "${JIRA_URL:?JIRA_URL not set}"
                        : "${JIRA_USERNAME:?JIRA_USERNAME not set}"
                        : "${JIRA_API_TOKEN:?JIRA_API_TOKEN not set}"
                        : "${JIRA_PROJECT:?JIRA_PROJECT not set}"

                        # Echo non-secret values so we can confirm routing.
                        echo "JIRA_URL=$JIRA_URL"
                        echo "JIRA_USERNAME=$JIRA_USERNAME"
                        echo "JIRA_PROJECT=$JIRA_PROJECT"

                        TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
                        PROMPT="Use the atlassian MCP server. Call jira_create_issue exactly once to create a Task in project ${JIRA_PROJECT} with summary 'Bob MCP smoke test ${TIMESTAMP}' and description 'Test ticket from Jenkins to verify MCP wiring.' Then print only the new issue key on a single line."

                        bob "$PROMPT" \
                            --chat-mode ask \
                            --max-coins 5 \
                            -y \
                            --hide-intermediary-output
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "=== Pipeline Complete ==="
            echo "Result: ${currentBuild.result ?: 'SUCCESS'}"
        }
    }
}