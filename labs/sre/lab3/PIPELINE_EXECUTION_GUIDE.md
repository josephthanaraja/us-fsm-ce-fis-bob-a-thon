# Pipeline Execution Guide
**Complete Step-by-Step Instructions for Running the Security Analysis Pipeline**

---

## Prerequisites

Before starting the pipeline, ensure you have:

- ✅ Jenkins running (OpenShift or local)
- ✅ SonarQube running on http://localhost:9000
- ✅ SonarQube token generated (from earlier steps)
- ✅ Vulnerabilities injected in order-service (if testing)
- ✅ Git repository with latest changes committed

---

## Step 1: Access Jenkins

### Option A: OpenShift Jenkins
```bash
# Get Jenkins route
oc get route jenkins -n sre-deploy-lab

# Open in browser (example)
open https://jenkins-sre-deploy-lab.apps.your-cluster.com
```

### Option B: Local Jenkins
```bash
# Open Jenkins
open http://localhost:8080

# Default credentials (if first time)
# Username: admin
# Password: (check initial admin password)
cat /var/jenkins_home/secrets/initialAdminPassword
```

---

## Step 2: Configure Jenkins Job

### Create/Update Pipeline Job

1. **Navigate to Jenkins Dashboard**
   - Click "New Item" (if creating new)
   - Or click on existing "order-service-pipeline" job

2. **Configure Pipeline**
   - **Name:** `order-service-pipeline`
   - **Type:** Pipeline
   - Click "OK"

3. **Pipeline Configuration**
   - **Definition:** Pipeline script from SCM
   - **SCM:** Git
   - **Repository URL:** Your git repository URL
   - **Branch:** `*/main` (or your branch)
   - **Script Path:** `Jenkinsfile`

4. **Generate and Add SonarQube Token Credential**
   
   **First, generate your token from the cluster SonarQube:**
   
   Your instructor will provide the SonarQube URL. Use it to generate your token:
   
   ```bash
   # Replace <SONARQUBE_URL> with the URL from your instructor
   curl -u demo:Demo123lab123@ -X POST "<SONARQUBE_URL>/api/user_tokens/generate?name=order-service-scan-$(date +%s)" 2>/dev/null
   ```
   
   **Example:**
   ```bash
   curl -u demo:Demo123lab123@ -X POST "https://sonarqube-sre-deploy-lab.apps.cluster.com/api/user_tokens/generate?name=order-service-scan-$(date +%s)" 2>/dev/null
   ```
   
   **Copy the token from the JSON response.**
   
   **Then add it to Jenkins:**
   - Go to: Jenkins → Manage Jenkins → Credentials
   - Click "(global)" domain
   - Click "Add Credentials"
   - **Kind:** Secret text
   - **Secret:** [Paste your token here]
   - **ID:** `sonar-token`
   - **Description:** SonarQube Analysis Token
   - Click "Create"

5. **Update Jenkinsfile Environment**
   Add to Jenkinsfile environment section:
   ```groovy
   environment {
       GITHUB_TOKEN = credentials('github-pat')
       SONAR_TOKEN = credentials('sonar-token')  // Add this line
   }
   ```

6. **Save Configuration**

---

## Step 3: Start the Pipeline

### Method 1: Manual Trigger (Recommended for Testing)

1. **Go to Pipeline Job**
   - Click on "order-service-pipeline"

2. **Click "Build with Parameters"** (or "Build Now" if no parameters)
   - **BRANCH:** `main` (or your branch name)
   - Click "Build"

3. **Monitor Build Progress**
   - Build will appear in "Build History"
   - Click on build number (e.g., #1, #2)
   - Click "Console Output" to see live logs

### Method 2: Git Push Trigger (Automated)

```bash
# Make a change and commit
git add .
git commit -m "Test security pipeline"
git push origin main

# Pipeline will automatically trigger (if webhook configured)
```

### Method 3: API Trigger

```bash
# Trigger via Jenkins API
curl -X POST http://localhost:8080/job/order-service-pipeline/build \
  --user admin:your-api-token \
  --data-urlencode json='{"parameter": [{"name":"BRANCH", "value":"main"}]}'
```

---

## Step 4: Monitor Pipeline Execution

### Watch Console Output

1. **Click on Build Number** (e.g., #1)
2. **Click "Console Output"**
3. **Watch Real-time Logs**

You'll see stages execute in order:

```
══════════════════════════════════════════
  STEP 1: Checkout PR Branch
══════════════════════════════════════════
✅ Checkout complete

══════════════════════════════════════════
  STEP 3: Standard Linting
══════════════════════════════════════════
✅ Checkstyle passed

══════════════════════════════════════════
  STEP 4: PCI Compliance Checks
══════════════════════════════════════════
⚠️  PCI compliance FAILED

══════════════════════════════════════════
  STEP 5: Running Unit Tests
══════════════════════════════════════════
❌ Tests FAILED

══════════════════════════════════════════
  STEP 6: Comprehensive Security Analysis
══════════════════════════════════════════

[6.1] Running SonarQube Static Analysis...
✅ SonarQube analysis complete
SonarQube Results:
  • BLOCKER:  1
  • CRITICAL: 2
  • MAJOR:    8
  • TOTAL:    11

[6.2] Running PCI Security Compliance Checks...
⚠️  PCI Security violations found: 5

[6.3] Scanning Dependencies for Vulnerabilities...
Trivy Dependency Scan:
  • CRITICAL: 0
  • HIGH:     0

[6.4] Running AI-Powered CVE Analysis...
✅ No critical or high CVEs detected - skipping detailed analysis

[6.5] Calculating Overall Security Risk...

[6.6] Generating Security Summary...
╔════════════════════════════════════════════════════════════╗
║           SECURITY ANALYSIS SUMMARY                        ║
╚════════════════════════════════════════════════════════════╝

Overall Security Risk: CRITICAL (Rating: E)
Risk Score: 21/100

[... detailed summary ...]

[6.7] Determine Pipeline Action...
❌ SECURITY GATE FAILED: Critical vulnerabilities detected. Deployment blocked.
```

### View Stage View

1. **Go to Build Page**
2. **Click "Pipeline Steps"** or view the stage visualization
3. **See which stages passed/failed:**
   - ✅ Green = Passed
   - ⚠️ Yellow = Unstable
   - ❌ Red = Failed

---

## Step 5: Access Security Reports

### SonarQube Dashboard

1. **Open SonarQube**
   ```bash
   open http://localhost:9000
   ```

2. **Login**
   - Username: `demo`
   - Password: `Demo123lab123@`

3. **View Project**
   - Click on "order-service" project
   - See overview with metrics:
     - Bugs: 2
     - Vulnerabilities: 1
     - Code Smells: 8
     - Security Rating: E

4. **Explore Issues**
   - Click "Issues" tab
   - Filter by severity: BLOCKER, CRITICAL, MAJOR
   - Click on each issue for details:
     - Location in code
     - Description
     - Remediation guidance

5. **View Security Hotspots**
   - Click "Security Hotspots" tab
   - Review items requiring manual security review

### Bob's Analysis Report

1. **Access Workspace**
   ```bash
   cd /Users/jordanbond/Desktop/fis_sre_bob/sre-project-test3
   ```

2. **Open Bob's Report**
   ```bash
   open BOB_FINDINGS_ANALYSIS_REPORT.md
   # Or
   cat BOB_FINDINGS_ANALYSIS_REPORT.md
   ```

3. **Review Findings**
   - Executive Summary
   - 6 Critical vulnerabilities with details
   - Remediation roadmap
   - Secure code examples

### SonarQube Analysis Report

1. **Open SonarQube Report**
   ```bash
   open SONARQUBE_ANALYSIS_REPORT.md
   # Or
   cat SONARQUBE_ANALYSIS_REPORT.md
   ```

2. **Review Contents**
   - Overall metrics
   - Issue breakdown by severity
   - Comparison with Bob's analysis
   - Remediation priorities

### CVE Analysis Report (if CVEs detected)

1. **Access Jenkins Workspace**
   ```bash
   # Find workspace path in Jenkins console output
   # Example: /var/jenkins_home/workspace/order-service-pipeline
   ```

2. **View CVE Report**
   ```bash
   cat /path/to/jenkins/workspace/CVE_ANALYSIS_REPORT.md
   ```

3. **Download from Jenkins**
   - Go to build page
   - Click "Build Artifacts"
   - Download `CVE_ANALYSIS_REPORT.md`

### Security Summary

1. **View in Console Output**
   - Scroll to Step 6.6 in console output
   - See formatted security summary

2. **Download from Workspace**
   ```bash
   cat /path/to/jenkins/workspace/security-summary.txt
   ```

---

## Step 6: Interpret Results

### Understanding Security Risk Levels

| Risk Level | Rating | Risk Score | Action |
|------------|--------|------------|--------|
| **CRITICAL** | E | 20+ | ❌ Deployment BLOCKED |
| **HIGH** | D | 10-19 | ⚠️ Manual approval required |
| **MEDIUM** | C | 5-9 | ⚠️ Proceed with caution |
| **LOW** | B | 1-4 | ✅ Approved with notes |
| **MINIMAL** | A | 0 | ✅ Approved |

### Risk Score Calculation

```
Risk Score = (BLOCKER × 10) + (CRITICAL × 5) + (HIGH × 2) + PCI_VIOLATIONS
```

**Example with injected vulnerabilities:**
- BLOCKER: 1 × 10 = 10
- CRITICAL: 2 × 5 = 10
- MAJOR: 8 × 2 = 16
- PCI Violations: 5 × 1 = 5
- **Total: 41 points = CRITICAL risk**

### Deployment Decisions

**❌ BLOCKED (CRITICAL Risk):**
- Pipeline fails with error
- Deployment cannot proceed
- Must fix BLOCKER/CRITICAL issues
- Re-run pipeline after fixes

**⚠️ UNSTABLE (HIGH Risk):**
- Pipeline marked unstable
- Requires manual approval at Step 7
- Security team review needed
- Can proceed with sign-off

**✅ PASSED (LOW/MINIMAL Risk):**
- Pipeline continues to deployment
- Automatic approval
- Issues tracked for future sprints

---

## Step 7: Take Action Based on Results

### If Pipeline is BLOCKED (CRITICAL)

1. **Review Security Reports**
   - Read BOB_FINDINGS_ANALYSIS_REPORT.md
   - Check SonarQube dashboard
   - Review CVE_ANALYSIS_REPORT.md (if exists)

2. **Fix Critical Issues**
   ```bash
   # Example: Remove hardcoded credentials
   cd order-service/src/main/java/com/example/orders/service
   
   # Edit OrderService.java
   # Remove lines 19-20 (hardcoded credentials)
   # Replace System.out with logger
   # Fix other BLOCKER/CRITICAL issues
   ```

3. **Restore Clean Code (if testing)**
   ```bash
   # Restore original code
   bash labs/lab3/restore_vulnerabilities.sh
   ```

4. **Commit and Re-run**
   ```bash
   git add .
   git commit -m "Fix critical security vulnerabilities"
   git push origin main
   
   # Or manually trigger pipeline again
   ```

### If Pipeline is UNSTABLE (HIGH Risk)

1. **Review Issues**
   - Check which HIGH severity issues exist
   - Assess business impact

2. **Proceed to Approval Gate**
   - Pipeline will pause at Step 7: Approval
   - Review deployment summary
   - Click "Approve Deployment" or "Abort"

3. **Document Risk Acceptance**
   - If approving with known issues
   - Document in ticket/JIRA
   - Schedule remediation

### If Pipeline PASSES

1. **Review Reports**
   - Even if passed, review findings
   - Address MEDIUM/LOW issues in backlog

2. **Continue to Deployment**
   - Pipeline proceeds automatically
   - Builds container image
   - Deploys via ArgoCD
   - Runs smoke tests

---

## Step 8: View Deployment Status

### Monitor ArgoCD Sync

1. **Access ArgoCD** (if using OpenShift)
   ```bash
   # Get ArgoCD route
   oc get route argocd-server -n openshift-gitops
   
   # Open in browser
   open https://argocd-server-openshift-gitops.apps.your-cluster.com
   ```

2. **Login to ArgoCD**
   - Username: `admin`
   - Password: Get from secret
     ```bash
     oc get secret argocd-cluster -n openshift-gitops \
       -o jsonpath='{.data.admin\.password}' | base64 -d
     ```

3. **View Application**
   - Click on "order-service" application
   - See sync status: Synced/OutOfSync
   - See health status: Healthy/Degraded
   - View resource tree

### Check Deployment

```bash
# Check deployment status
oc get deployment order-service

# Check pods
oc get pods -l app=order-service

# Check service
oc get service order-service

# View logs
oc logs -f deployment/order-service
```

### Verify Smoke Tests

1. **View Console Output**
   - Scroll to Step 10: Smoke Tests
   - See test results

2. **Manual Verification**
   ```bash
   # Get service URL
   SERVICE_URL=$(oc get route order-service -o jsonpath='{.spec.host}')
   
   # Test health endpoint
   curl http://${SERVICE_URL}/actuator/health
   
   # Test orders endpoint
   curl http://${SERVICE_URL}/api/orders
   ```

---

## Step 9: Archive and Review

### Download Build Artifacts

1. **Go to Build Page**
2. **Click "Build Artifacts"**
3. **Download:**
   - CVE_ANALYSIS_REPORT.md
   - security-summary.txt
   - trivy-results.json
   - pci-security.txt

### Review Metrics

1. **Track Over Time**
   - Build duration
   - Security issues found
   - Risk scores
   - Deployment success rate

2. **Create Dashboard**
   - Use Jenkins Blue Ocean
   - Or export to monitoring tool

---

## Troubleshooting

### Pipeline Fails at SonarQube Stage

**Problem:** SonarQube connection fails

**Solution:**
```bash
# Check SonarQube is running
curl http://localhost:9000/api/system/status

# Verify token
curl -u demo:Demo123lab123@ http://localhost:9000/api/user_tokens/search

# Check Jenkins credential
# Jenkins → Credentials → verify sonar-token exists
```

### Pipeline Fails at Trivy Stage

**Problem:** Trivy not installed

**Solution:**
```bash
# Install Trivy in Jenkins agent
# Add to Dockerfile or install in pipeline:
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
```

### Cannot Access Reports

**Problem:** Reports not found in workspace

**Solution:**
```bash
# Check workspace location
echo $WORKSPACE

# Verify files exist
ls -la $WORKSPACE/*.md

# Check permissions
chmod 644 $WORKSPACE/*.md
```

### Pipeline Stuck at Approval

**Problem:** Waiting for manual approval

**Solution:**
1. Go to build page
2. See "Paused for Input" message
3. Click "Approve Deployment" or "Abort"
4. Or approve via CLI:
   ```bash
   # Get input ID from console
   # Then approve:
   curl -X POST http://localhost:8080/job/order-service-pipeline/1/input/approve \
     --user admin:token
   ```

---

## Quick Reference Commands

### Start Pipeline
```bash
# Via Jenkins UI
# Dashboard → order-service-pipeline → Build Now

# Via CLI
jenkins-cli build order-service-pipeline -p BRANCH=main
```

### Check Status
```bash
# Get latest build status
jenkins-cli get-build order-service-pipeline 1

# View console output
jenkins-cli console order-service-pipeline 1
```

### View Reports
```bash
# Bob's analysis
cat BOB_FINDINGS_ANALYSIS_REPORT.md

# SonarQube analysis
cat SONARQUBE_ANALYSIS_REPORT.md

# CVE analysis (if generated)
cat $WORKSPACE/CVE_ANALYSIS_REPORT.md

# Security summary
cat $WORKSPACE/security-summary.txt
```

### Access Dashboards
```bash
# SonarQube
open http://localhost:9000/dashboard?id=order-service

# Jenkins
open http://localhost:8080/job/order-service-pipeline

# ArgoCD (if using)
open https://argocd-server-openshift-gitops.apps.your-cluster.com
```

---

## Best Practices

1. **Run Pipeline on Every PR**
   - Catch issues early
   - Prevent vulnerable code from merging

2. **Review Reports Regularly**
   - Don't just look at pass/fail
   - Understand the issues
   - Track trends over time

3. **Fix Issues Promptly**
   - BLOCKER: Immediately
   - CRITICAL: Within 24 hours
   - HIGH: Within 1 week
   - MEDIUM/LOW: Next sprint

4. **Document Decisions**
   - Why issues were accepted
   - Compensating controls
   - Remediation plans

5. **Keep Tools Updated**
   - SonarQube rules
   - Trivy database
   - Security plugins

6. **Train the Team**
   - Share security reports
   - Explain findings
   - Teach secure coding

---

## Next Steps

After running the pipeline successfully:

1. ✅ **Review all security reports**
2. ✅ **Fix critical vulnerabilities**
3. ✅ **Re-run pipeline to verify fixes**
4. ✅ **Deploy to staging/production**
5. ✅ **Monitor application in production**
6. ✅ **Schedule regular security reviews**

---

## Support

**Documentation:**
- Bob Findings Report: `BOB_FINDINGS_ANALYSIS_REPORT.md`
- SonarQube Report: `SONARQUBE_ANALYSIS_REPORT.md`
- CVE Analysis Prompt: `pipeline/CVE_ANALYSIS_PROMPT.md`
- Vulnerability Guide: `labs/lab3/VULNERABILITY_INJECTION_GUIDE.md`

**Dashboards:**
- Jenkins: http://localhost:8080
- SonarQube: http://localhost:9000
- ArgoCD: (OpenShift route)

**Commands:**
- Restore code: `bash labs/lab3/restore_vulnerabilities.sh`
- Inject vulnerabilities: `bash labs/lab3/inject_vulnerabilities_modify_existing.sh`
- Generate token: `curl -u demo:Demo123lab123@ -X POST "http://localhost:9000/api/user_tokens/generate?name=token-$(date +%s)"`

---

**Last Updated:** 2026-04-08  
**Version:** 1.0  
**Maintained By:** SRE Team