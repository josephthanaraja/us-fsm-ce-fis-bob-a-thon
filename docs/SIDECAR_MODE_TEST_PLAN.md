# Bob CLI Sidecar Implementation Plan

## Overview

This plan details the implementation of Bob CLI as a sidecar container in Jenkins pods, enabling custom modes to be defined in Git repositories and automatically available during pipeline execution. This approach allows workshop participants to create, version control, and share custom Bob modes as part of their project code, making it easy for teams to standardize AI-assisted workflows.

The sidecar pattern solves a key challenge: how do we make custom Bob modes available to CI/CD pipelines without requiring manual configuration on each Jenkins agent? By running Bob CLI as a sidecar container that shares the workspace volume with the Jenkins agent, any `.bob/custom_modes.yaml` file checked into the repository becomes immediately available to Bob during pipeline execution. This creates a seamless experience where developers can define specialized modes (like an SRE operator mode for deployment analysis or a security reviewer mode for vulnerability assessment) and have them automatically available in their pipelines.

For workshop participants, this means they can experiment with creating custom modes, commit them to their repository, and immediately test them in their Jenkins pipelines. The modes travel with the code, making it easy to share best practices across teams and ensure consistent AI assistance across different projects. This hands-on approach helps participants understand both the power of custom modes and the practical aspects of integrating AI into their CI/CD workflows.

---

## 🎯 Two Audiences for This Plan

### For Workshop Instructors/Admins (Phases 0-7)
**You need:** `oc` CLI, cluster admin access, Bob API key
**You do:** One-time infrastructure setup - deploy Jenkins, build images, create secrets, configure pipeline
**Time:** 30-60 minutes

### For Workshop Participants/Lab Users (Phase 9)
**You need:** Git access, code editor, Jenkins UI access (browser)
**You do:** Edit `.bob/custom_modes.yaml`, commit, push, click "Build Now" in Jenkins
**Time:** 5-10 minutes per iteration
**NO `oc` CLI required!**

---

## Prerequisites

### For Workshop Instructors/Admins (Setup Only)

**IMPORTANT:** This plan will guide you through the complete setup from scratch, including OpenShift cluster provisioning, Jenkins deployment, and Bob CLI sidecar configuration. You can start this plan even if your OpenShift cluster is still provisioning.

**What You Need:**
- Access to provision an OpenShift cluster (e.g., TechZone, ROKS, CRC)
- **`oc` CLI installed on your local machine** (for setup only)
- Bob Shell API key (get from https://bob.ibm.com)
- Git repository with admin access (to set up initial `.bob/custom_modes.yaml`)
- Basic familiarity with Kubernetes/OpenShift concepts

**What You'll Set Up (One-Time):**
1. OpenShift cluster (if not already provisioned)
2. Jenkins deployment with necessary ServiceAccounts
3. Bob CLI sidecar container image
4. Custom modes configuration
5. Test pipeline to verify everything works

### For Workshop Participants/Lab Users (No Setup Required)

**What You Need:**
- Git repository access (clone, commit, push)
- Code editor (VS Code, vim, etc.)
- Jenkins UI access (browser)
- **NO `oc` CLI required!**
- **NO cluster access required!**

**What You'll Do:**
1. Clone the Git repository
2. Edit `.bob/custom_modes.yaml` to add your custom modes
3. Commit and push your changes
4. Go to Jenkins UI and click "Build Now"
5. Watch your custom modes in action!

**Your Workflow:**
```
Edit .bob/custom_modes.yaml → Commit → Push → Jenkins UI "Build Now" → See Results
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Jenkins Pod (Kubernetes)                                    │
│                                                             │
│  ┌────────────────────┐      ┌────────────────────┐       │
│  │ jenkins-agent      │      │ bob-cli            │       │
│  │                    │      │                    │       │
│  │ - Runs pipeline    │      │ - Runs Bob Shell   │       │
│  │ - Checks out Git   │      │ - Reads modes      │       │
│  │ - Executes stages  │      │ - Executes prompts │       │
│  │                    │      │                    │       │
│  │ workingDir:        │      │ workingDir:        │       │
│  │   /workspace       │      │   /workspace       │       │
│  └─────────┬──────────┘      └─────────┬──────────┘       │
│            │                           │                   │
│            └──────────┬────────────────┘                   │
│                       │                                    │
│              ┌────────▼─────────┐                          │
│              │ Shared Volume    │                          │
│              │ (emptyDir)       │                          │
│              │                  │                          │
│              │ /workspace/      │                          │
│              │ ├── .bob/        │                          │
│              │ │   └── custom_  │                          │
│              │ │       modes.   │                          │
│              │ │       yaml     │                          │
│              │ ├── Jenkinsfile  │                          │
│              │ └── (repo files) │                          │
│              └──────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Steps

### Phase 0: OpenShift Cluster Setup

#### Step 0.1: Wait for Cluster Provisioning (If Applicable)

If your OpenShift cluster is still provisioning:

```bash
# Wait for cluster to be ready
# This typically takes 30-60 minutes for TechZone environments

# Once you receive cluster credentials, test access:
oc login --token=<your-token> --server=<your-server>

# Verify cluster is accessible
oc cluster-info
oc get nodes
```

**Expected Output:**
```
Kubernetes control plane is running at https://...
NAME                         STATUS   ROLES    AGE   VERSION
ip-10-0-xxx-xxx.ec2.internal Ready    master   1h    v1.xx.x
...
```

#### Step 0.2: Create and Set Your Namespace

```bash
# Create a new project/namespace for this workshop
oc new-project sre-deploy-lab

# Or use an existing one
# oc project sre-deploy-lab

# Set environment variable for later use
export NAMESPACE=$(oc project -q)
echo "Using namespace: $NAMESPACE"
```

#### Step 0.3: Deploy Jenkins

**Option A: Using OpenShift Template (Recommended)**

```bash
# Deploy Jenkins using the built-in template
oc new-app jenkins-persistent \
    --param MEMORY_LIMIT=2Gi \
    --param VOLUME_CAPACITY=10Gi

# Wait for Jenkins to be ready (takes 2-5 minutes)
# NOTE: jenkins-persistent creates a DeploymentConfig, not a Deployment —
# so we roll-out status against dc/jenkins
oc rollout status dc/jenkins

# Get Jenkins URL (Route is created automatically by the template)
oc get route jenkins -o jsonpath='{.spec.host}'
```

**Option B: Using Helm (Alternative)**

```bash
# Add Jenkins Helm repo
helm repo add jenkins https://charts.jenkins.io
helm repo update

# Install Jenkins (ClusterIP, we add a Route ourselves below)
helm install jenkins jenkins/jenkins \
    --set persistence.enabled=true \
    --set persistence.size=10Gi \
    --set controller.serviceType=ClusterIP

# Wait for Jenkins to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=jenkins --timeout=300s

# Expose Jenkins via an OpenShift Route so you can reach the UI
# (Helm's ClusterIP service is not reachable from outside the cluster)
oc expose svc/jenkins
oc get route jenkins -o jsonpath='{.spec.host}'
```

**Verify Jenkins Deployment:**

```bash
# Check if Jenkins is running
# Option A (template) uses DeploymentConfig: `oc get dc jenkins`
# Option B (Helm)     uses Deployment:       `oc get deployment jenkins`
oc get dc jenkins 2>/dev/null || oc get deployment jenkins
oc get pods -l app=jenkins

# Check if jenkins ServiceAccount was created
oc get sa jenkins

# Get Jenkins admin password (if using template)
oc get secret jenkins -o jsonpath='{.data.password}' | base64 -d
```

**Expected Output (Option A — template):**
```
NAME      REVISION   DESIRED   CURRENT   TRIGGERED BY
jenkins   1          1         1         config,image(jenkins:2)

NAME                      READY   STATUS    RESTARTS   AGE
jenkins-1-xxxxx           1/1     Running   0          2m

NAME      SECRETS   AGE
jenkins   2         2m
```

**Access Jenkins UI:**

```bash
# Get the Jenkins URL
JENKINS_URL=$(oc get route jenkins -o jsonpath='{.spec.host}')
echo "Jenkins URL: https://$JENKINS_URL"

# Open in browser and login with admin credentials
```

---

### Phase 0.5: Remove Obsolete Per-User Bob CLI Assets

Before building the new sidecar image, remove the repo files for the **old per-user Bob CLI deployment pattern** that this plan replaces. Keeping them around invites participants to run the wrong setup script or copy the wrong Dockerfile.

**Files being removed:**

| Path | What it was |
|------|-------------|
| `k8s/bob-cli-deployment.yaml` | Deployment manifest for the per-user `bob-cli` pod |
| `k8s/openshift/bob-cli/Dockerfile` | Image definition for that old pod |
| `k8s/openshift/bob-cli/` (directory) | Now empty after the Dockerfile is removed |
| `k8s/openshift/bob-cli-setup.sh` | Script that provisioned the old pod |
| `k8s/openshift/bob-cli-teardown.sh` | Teardown counterpart |

**Files NOT touched** (still in use or unrelated):

- `k8s/openshift/bob-cli-sidecar/` — the new sidecar image directory, built in Phase 1
- `k8s/openshift/jenkins-agent/`, `jenkins-setup.sh`, `argocd-*` — used by the broader pipeline, out of scope for this cleanup
- `k8s/order-*`, `labs/`, `pipeline/`, `order-service/` — lab subject-matter, not infrastructure

#### Steps

```bash
# Confirm no retained script references the files being removed
grep -l "bob-cli-setup\|bob-cli-teardown\|bob-cli-deployment" \
    k8s/openshift/setup.sh k8s/openshift/teardown.sh 2>/dev/null
# (should return nothing — if it does, update those scripts first)

# Remove the obsolete files
git rm k8s/bob-cli-deployment.yaml
git rm k8s/openshift/bob-cli-setup.sh
git rm k8s/openshift/bob-cli-teardown.sh
git rm -r k8s/openshift/bob-cli/

# Commit the cleanup
git commit -m "Remove obsolete per-user Bob CLI assets

The per-user Bob pod pattern is replaced by the sidecar container in
this plan. Removing the old Dockerfile, Deployment manifest, and
setup/teardown scripts so participants can't accidentally provision
the deprecated pattern.

Sidecar replacement lives in k8s/openshift/bob-cli-sidecar/ (created
in Phase 1 of docs/SIDECAR_MODE_TEST_PLAN.md)."

# Push
git push
```

#### Verification

```bash
# These should all return "No such file or directory"
ls k8s/bob-cli-deployment.yaml k8s/openshift/bob-cli-setup.sh \
   k8s/openshift/bob-cli-teardown.sh k8s/openshift/bob-cli/ 2>&1 | grep -i "no such"

# Confirm the sidecar directory will be created fresh in Phase 1
ls k8s/openshift/bob-cli-sidecar/ 2>&1 | grep -i "no such"
```

Both checks should confirm the old paths are gone and the new path does not yet exist (we create it in Phase 1).

---

### Phase 1: Prepare Bob CLI Container Image

#### Step 1.1: Create Bob CLI Dockerfile

Create a dedicated directory and Dockerfile:

```bash
mkdir -p k8s/openshift/bob-cli-sidecar
```

**File:** `k8s/openshift/bob-cli-sidecar/Dockerfile`

```dockerfile
FROM node:22-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y curl bash tar jq git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Bob Shell
RUN curl -s https://s3.us-south.cloud-object-storage.appdomain.cloud/bobshell/install-bobshell.sh | bash -s -- --pm npm

# Set environment variables
ENV BOB_ACCEPT_LICENSE=true \
    HOME=/workspace

# Create workspace directory with OpenShift-compatible permissions
# Use group 0 (root group) with group permissions matching user permissions
RUN mkdir -p /workspace/.bob && \
    chgrp -R 0 /workspace && \
    chmod -R g=u /workspace

# Set working directory (will be overridden by pod spec, but good default)
WORKDIR /workspace

# Keep container running
CMD ["sleep", "infinity"]
```

**Key Points:**
- `HOME=/workspace` - Ensures Bob writes config to shared workspace
- `chgrp -R 0 /workspace && chmod -R g=u /workspace` - OpenShift-idiomatic permissions (arbitrary UID, group 0)
- `WORKDIR /workspace` - Default working directory (pod spec will confirm this)
- Named `Dockerfile` (not `bob-cli-sidecar.Dockerfile`) so build strategy finds it

#### Step 1.2: Build and Push Image

```bash
# Navigate to the directory
cd k8s/openshift/bob-cli-sidecar

# Create BuildConfig if it doesn't exist
oc new-build --binary --name=bob-cli-sidecar \
    --strategy=docker \
    --to=bob-cli-sidecar:latest

# Build the image using the directory (contains Dockerfile)
oc start-build bob-cli-sidecar \
    --from-dir=. \
    --follow --wait

# Verify the image
oc get imagestream bob-cli-sidecar
```

**Expected Output:**
```
NAME              IMAGE REPOSITORY                                          TAGS     UPDATED
bob-cli-sidecar   image-registry.openshift-image-registry.svc:5000/...     latest   About a minute ago
```

**Note:** We use `--from-dir=.` (not `--from-file=`) because the Docker build strategy expects a file named `Dockerfile` in the context root.

---

### Phase 2: Create Bob CLI Credentials Secret

#### Step 2.1: Create Secret from API Key

```bash
# Set your API key
export BOBSHELL_API_KEY="your-api-key-here"

# Create the secret
oc create secret generic bob-cli-credentials \
    --from-literal=BOBSHELL_API_KEY="$BOBSHELL_API_KEY"

# Verify secret
oc get secret bob-cli-credentials
```

**Expected Output:**
```
NAME                  TYPE     DATA   AGE
bob-cli-credentials   Opaque   1      5s
```

#### Step 2.2: Verify Secret Contents (Optional)

```bash
# Check that the secret has the right key
oc get secret bob-cli-credentials -o jsonpath='{.data}' | jq
```

**Expected Output:**
```json
{
  "BOBSHELL_API_KEY": "base64-encoded-key"
}
```

---

### Phase 3: Verify Jenkins ServiceAccount

#### Step 3.1: Check ServiceAccount Exists

```bash
# Verify jenkins ServiceAccount exists
oc get sa jenkins

# Check its permissions
oc describe sa jenkins
```

**Expected Output:**
```
Name:                jenkins
Namespace:           sre-deploy-lab
Labels:              <none>
Annotations:         <none>
Image pull secrets:  jenkins-dockercfg-xxxxx
Mountable secrets:   jenkins-dockercfg-xxxxx
Tokens:              jenkins-token-xxxxx
```

#### Step 3.2: Grant Additional Permissions (if needed)

```bash
# If jenkins SA needs additional permissions for your use case
oc policy add-role-to-user edit system:serviceaccount:$NAMESPACE:jenkins

# Verify
oc policy who-can create pods
```

**Note:** Most Jenkins deployments create the ServiceAccount automatically. If it doesn't exist, you need to deploy Jenkins first or create it manually:

```bash
# Only if jenkins SA doesn't exist
oc create sa jenkins
oc policy add-role-to-user edit system:serviceaccount:$NAMESPACE:jenkins
```

---

### Phase 4: Create Custom Modes File

#### Step 4.1: Create `.bob/custom_modes.yaml` in Repository

**File:** `.bob/custom_modes.yaml`

```yaml
customModes:
  - slug: sre-operator
    name: 🔧 SRE Operator
    description: SRE operator mode for Jenkins pipeline operations, deployment analysis, and incident response
    roleDefinition: |
      You are Bob, an SRE operator for a regulated financial services environment.
      You manage Jenkins CI/CD pipelines, assess deployment risk, and enforce change
      management procedures. Your expertise includes:
      - Operating Jenkins pipelines (triggering builds, reading logs, checking status)
      - PCI DSS compliance assessment and violation identification
      - Risk assessment for production deployments
      - Rollback decision-making and post-deployment verification
      - Incident triage and root cause analysis
    whenToUse: |
      Use this mode when operating Jenkins pipelines, diagnosing build failures,
      reviewing deployment readiness, or performing SRE operations.
    groups:
      - read
      - command
      - - edit
        - fileRegex: \.(yaml|yml|properties|sh|groovy)$
          description: Infrastructure and pipeline config files only
    customInstructions: |
      - Always check pipeline status before recommending deployments
      - Never approve a deployment if compliance checks have failed
      - Reference PCI DSS requirements when discussing compliance issues
      - When diagnosing a failed build, always read the full build log
      - For rollbacks, use: oc rollout undo deployment/order-service
      
  - slug: code-reviewer
    name: 👀 Code Reviewer
    description: Code review specialist for Java applications
    roleDefinition: |
      You are Bob, a senior code reviewer specializing in Java applications.
      You review code for:
      - Code quality and maintainability
      - Security vulnerabilities
      - Performance issues
      - Best practices adherence
      - Test coverage
    whenToUse: |
      Use this mode when reviewing pull requests or analyzing code changes.
    groups:
      - read
      - - edit
        - fileRegex: \.(java|xml|properties)$
          description: Java source and config files
    customInstructions: |
      - Focus on security, performance, and maintainability
      - Provide specific line numbers when suggesting changes
      - Explain the reasoning behind each recommendation
      - Consider the context of the entire application
```

#### Step 4.2: Commit and Push

```bash
git add .bob/custom_modes.yaml
git commit -m "Add custom Bob modes for pipeline operations"
git push origin main
```

---

### Phase 5: Create Jenkinsfile with Sidecar Configuration

#### Step 5.1: Get Your Namespace and Image URLs

```bash
# Get your current namespace
NAMESPACE=$(oc project -q)
echo "Namespace: $NAMESPACE"

# Get the full image URLs
BOB_IMAGE="image-registry.openshift-image-registry.svc:5000/$NAMESPACE/bob-cli-sidecar:latest"
echo "Bob CLI Image: $BOB_IMAGE"

# You'll use these in the Jenkinsfile
```

#### Step 5.2: Create Test Jenkinsfile

**File:** `Jenkinsfile.sidecar-test`

**IMPORTANT:** Replace `YOUR_NAMESPACE_HERE` with your actual namespace (e.g., `sre-deploy-lab`)

```groovy
pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    jenkins-agent: sidecar-test
spec:
  serviceAccountName: jenkins
  containers:
  
  # Jenkins Agent Container
  - name: jenkins-agent
    image: jenkins/inbound-agent:latest
    command: ['sleep']
    args: ['infinity']
    workingDir: /workspace
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace
    env:
    - name: HOME
      value: /workspace
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "1"
  
  # Bob CLI Sidecar Container
  - name: bob-cli
    image: image-registry.openshift-image-registry.svc:5000/YOUR_NAMESPACE_HERE/bob-cli-sidecar:latest
    command: ['sleep']
    args: ['infinity']
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
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"
      limits:
        memory: "2Gi"
        cpu: "500m"
  
  # Shared Volume
  volumes:
  - name: workspace-volume
    emptyDir: {}
"""
            defaultContainer 'jenkins-agent'
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
                    echo ""
                    echo "Bob directory contents:"
                    ls -la .bob/ || echo "No .bob directory found"
                '''
            }
        }
        
        stage('Verify Bob CLI Setup') {
            steps {
                echo "=== Verifying Bob CLI in sidecar ==="
                container('bob-cli') {
                    sh '''
                        echo "Current directory in bob-cli container: $(pwd)"
                        echo "Workspace contents from bob-cli:"
                        ls -la
                        echo ""
                        echo "Bob directory from bob-cli:"
                        ls -la .bob/ || echo "No .bob directory found"
                        echo ""
                        echo "Checking Bob installation:"
                        which bob
                        bob --version || echo "Bob version check failed"
                    '''
                }
            }
        }
        
        stage('Test Bob Basic Functionality') {
            steps {
                echo "=== Testing Bob basic functionality ==="
                container('bob-cli') {
                    script {
                        def result = sh(
                            script: '''
                                bob -p "Reply with exactly: BOB_IS_WORKING" \
                                    --hide-intermediary-output 2>&1
                            ''',
                            returnStdout: true
                        ).trim()
                        
                        echo "Bob response:\n${result}"
                        
                        if (result.contains("BOB_IS_WORKING")) {
                            echo "✅ Bob CLI is working!"
                        } else {
                            echo "⚠️  Bob CLI may not be working correctly"
                            echo "Full output: ${result}"
                        }
                    }
                }
            }
        }
        
        stage('Verify Custom Modes Loaded') {
            steps {
                echo "=== Verifying custom modes are loaded ==="
                container('bob-cli') {
                    script {
                        // Test if custom mode can be invoked
                        def result = sh(
                            script: '''
                                bob --chat-mode sre-operator \
                                    -p "Reply with exactly: CUSTOM_MODE_WORKING" \
                                    --hide-intermediary-output 2>&1
                            ''',
                            returnStatus: true
                        )
                        
                        if (result == 0) {
                            echo "✅ Custom mode 'sre-operator' is loaded and working!"
                        } else {
                            echo "❌ Custom mode 'sre-operator' failed to load"
                            error("Custom mode test failed")
                        }
                    }
                }
            }
        }
        
        stage('Test Code Analysis with Custom Mode') {
            steps {
                echo "=== Testing Bob code analysis with custom mode ==="
                container('bob-cli') {
                    script {
                        // Only run if there are Java files
                        def hasJava = sh(
                            script: 'find . -name "*.java" | head -1',
                            returnStdout: true
                        ).trim()
                        
                        if (hasJava) {
                            def analysis = sh(
                                script: '''
                                    bob --chat-mode code-reviewer \
                                        -p "List the Java files in this project and briefly describe what you see" \
                                        --hide-intermediary-output 2>&1
                                ''',
                                returnStdout: true
                            ).trim()
                            
                            echo "Bob analysis:\n${analysis}"
                        } else {
                            echo "No Java files found, skipping code analysis test"
                        }
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo "=== Pipeline Complete ==="
            echo "Result: ${currentBuild.result ?: 'SUCCESS'}"
        }
        success {
            echo "✅ Sidecar setup is working correctly!"
            echo ""
            echo "Next steps:"
            echo "1. Workshop participants can now add their own modes to .bob/custom_modes.yaml"
            echo "2. Modes will be automatically available in subsequent builds"
            echo "3. Try creating a new mode and testing it!"
        }
        failure {
            echo "❌ Sidecar setup needs troubleshooting"
            echo "Check the logs above for errors"
            echo "Common issues:"
            echo "- Image pull errors: verify namespace in image URL"
            echo "- Bob authentication: verify bob-cli-credentials secret"
            echo "- Custom modes not found: verify .bob/custom_modes.yaml in repo"
        }
    }
}
```

**Critical Configuration Points:**

1. **Hardcoded Namespace in Image URL:**
   ```yaml
   image: image-registry.openshift-image-registry.svc:5000/YOUR_NAMESPACE_HERE/bob-cli-sidecar:latest
   ```
   Replace `YOUR_NAMESPACE_HERE` with your actual namespace (e.g., `sre-deploy-lab`). This is evaluated when Jenkins provisions the pod, so it must be a literal value, not a variable.

2. **Shared Volume:**
   ```yaml
   volumes:
   - name: workspace-volume
     emptyDir: {}
   ```

3. **Matching Mount Paths:**
   ```yaml
   volumeMounts:
   - name: workspace-volume
     mountPath: /workspace
   ```

4. **Matching Working Directories:**
   ```yaml
   workingDir: /workspace
   ```

5. **Bob CLI Credentials:**
   ```yaml
   env:
   - name: BOBSHELL_API_KEY
     valueFrom:
       secretKeyRef:
         name: bob-cli-credentials
         key: BOBSHELL_API_KEY
   ```

6. **ServiceAccount:**
   ```yaml
   serviceAccountName: jenkins
   ```
   This must exist (created by Jenkins deployment).

---

### Phase 6: Create Jenkins Pipeline Job

#### Step 6.1: Create Pipeline in Jenkins UI

1. Log into Jenkins
2. Click "New Item"
3. Enter name: `bob-sidecar-test`
4. Select "Pipeline"
5. Click "OK"

#### Step 6.2: Configure Pipeline

**Pipeline Configuration:**

- **Definition:** Pipeline script from SCM
- **SCM:** Git
- **Repository URL:** Your Git repository URL
- **Credentials:** Your Git credentials
- **Branch:** `*/main`
- **Script Path:** `Jenkinsfile.sidecar-test`

Click "Save"

---

### Phase 7: Test the Setup

#### Step 7.1: Trigger Pipeline Build

```bash
# Option 1: Via Jenkins UI
# Go to Jenkins → bob-sidecar-test → Build Now

# Option 2: Via CLI (if Jenkins CLI is configured)
# Trigger the build
curl -X POST "http://jenkins-url/job/bob-sidecar-test/build" \
  --user "username:token"
```

#### Step 7.2: Monitor Build Progress

```bash
# Watch pod creation
oc get pods -w -l jenkins-agent=sidecar-test

# Once pod is running, you can exec into it
POD_NAME=$(oc get pods -l jenkins-agent=sidecar-test -o jsonpath='{.items[0].metadata.name}')
echo "Pod name: $POD_NAME"

# View logs from bob-cli container
oc logs $POD_NAME -c bob-cli -f
```

#### Step 7.3: Expected Output

The pipeline should show:

```
=== Checking out repository ===
Cloning repository...
✓ Repository cloned

=== Verifying workspace contents ===
Current directory: /workspace
Workspace contents:
drwxr-xr-x  .bob
-rw-r--r--  Jenkinsfile.sidecar-test
...

=== Verifying Bob CLI in sidecar ===
Current directory in bob-cli container: /workspace
Bob directory from bob-cli:
-rw-r--r--  custom_modes.yaml

=== Testing Bob basic functionality ===
Bob response:
BOB_IS_WORKING
✅ Bob CLI is working!

=== Verifying custom modes are loaded ===
✅ Custom mode 'sre-operator' is loaded and working!

=== Testing Bob code analysis with custom mode ===
Bob analysis:
[Bob's analysis of the code]

✅ Sidecar setup is working correctly!
```

---

### Phase 8: Troubleshooting Guide

#### Issue 1: "ImagePullBackOff" or "ErrImagePull"

**Symptoms:**
```
Pod status: ImagePullBackOff
Events: Failed to pull image "image-registry.openshift-image-registry.svc:5000/${env.NAMESPACE}/bob-cli-sidecar:latest"
```

**Root Cause:**
The `${env.NAMESPACE}` variable in the Jenkinsfile YAML is not being evaluated because the `environment` block runs after the agent is provisioned.

**Diagnosis:**
```bash
# Check the actual image URL being used
oc describe pod <pod-name> | grep Image:

# You'll see something like:
# Image: image-registry.openshift-image-registry.svc:5000/${env.NAMESPACE}/bob-cli-sidecar:latest
# (literal string, not evaluated)
```

**Solution:**
Replace `${env.NAMESPACE}` with your actual namespace in the Jenkinsfile:

```yaml
# WRONG:
image: image-registry.openshift-image-registry.svc:5000/${env.NAMESPACE}/bob-cli-sidecar:latest

# CORRECT:
image: image-registry.openshift-image-registry.svc:5000/sre-deploy-lab/bob-cli-sidecar:latest
```

Or use a Jenkins global environment variable or parameter that's set before agent provisioning.

---

#### Issue 2: "serviceaccount 'jenkins' not found"

**Symptoms:**
```
Error creating pod: serviceaccounts "jenkins" not found
```

**Root Cause:**
Jenkins hasn't been deployed yet, so the `jenkins` ServiceAccount doesn't exist.

**Diagnosis:**
```bash
# Check if jenkins SA exists
oc get sa jenkins

# If it doesn't exist:
# Error from server (NotFound): serviceaccounts "jenkins" not found
```

**Solution:**
Either deploy Jenkins first (recommended) or create the ServiceAccount manually:

```bash
# Option 1: Deploy Jenkins (recommended)
# Follow your cluster's Jenkins deployment process

# Option 2: Create SA manually (temporary workaround)
oc create sa jenkins
oc policy add-role-to-user edit system:serviceaccount:$(oc project -q):jenkins
```

---

#### Issue 3: "Bob: command not found"

**Symptoms:**
```
/bin/sh: bob: command not found
```

**Diagnosis:**
```bash
# Exec into bob-cli container
POD_NAME=$(oc get pods -l jenkins-agent=sidecar-test -o jsonpath='{.items[0].metadata.name}')
oc exec -it $POD_NAME -c bob-cli -- bash

# Check Bob installation
which bob
ls -la /usr/local/bin/bob
echo $PATH
```

**Solutions:**
1. Verify Bob Shell installed correctly in Dockerfile
2. Check PATH environment variable includes `/usr/local/bin`
3. Rebuild bob-cli-sidecar image
4. Check Bob installation logs during image build

---

#### Issue 4: "Custom mode not found"

**Symptoms:**
```
Error: Mode 'sre-operator' not found
Available modes: code, architect, ...
```

**Root Cause:**
Bob can't find the `.bob/custom_modes.yaml` file.

**Diagnosis:**
```bash
# Exec into bob-cli container
oc exec -it $POD_NAME -c bob-cli -- bash

# Check if custom_modes.yaml exists
ls -la /workspace/.bob/
cat /workspace/.bob/custom_modes.yaml

# Check Bob's current directory
pwd

# Check if file is in a different location
find / -name custom_modes.yaml 2>/dev/null
```

**Solutions:**
1. Verify `.bob/custom_modes.yaml` is in Git repository
2. Verify Jenkins checked out the code successfully (check earlier pipeline stages)
3. Verify YAML syntax: `yamllint .bob/custom_modes.yaml`
4. Verify both containers have same `workingDir: /workspace`
5. Check volume mount paths match in both containers
6. Verify `HOME=/workspace` is set (Bob looks in `$HOME/.bob/` and `$PWD/.bob/`)

---

#### Issue 5: "Permission denied" errors

**Symptoms:**
```
mkdir: cannot create directory '/workspace/.bob': Permission denied
touch: cannot touch '/workspace/test': Permission denied
```

**Diagnosis:**
```bash
# Check workspace permissions
oc exec -it $POD_NAME -c bob-cli -- ls -la /workspace

# Check user ID
oc exec -it $POD_NAME -c bob-cli -- id

# Check if running as arbitrary UID
# OpenShift typically uses UID 1000660000 or similar
```

**Solutions:**
1. Ensure Dockerfile has proper OpenShift permissions:
   ```dockerfile
   RUN mkdir -p /workspace/.bob && \
       chgrp -R 0 /workspace && \
       chmod -R g=u /workspace
   ```
2. Verify OpenShift SCC allows arbitrary UIDs
3. Check volume mount permissions
4. Rebuild image with correct permissions

---

#### Issue 6: Containers can't see each other's files

**Symptoms:**
- Jenkins checks out code but Bob can't see it
- Files exist in jenkins-agent but not in bob-cli
- `ls /workspace` shows different contents in each container

**Diagnosis:**
```bash
# Check from jenkins-agent
oc exec -it $POD_NAME -c jenkins-agent -- ls -la /workspace

# Check from bob-cli
oc exec -it $POD_NAME -c bob-cli -- ls -la /workspace

# Compare mount points
oc exec -it $POD_NAME -c jenkins-agent -- mount | grep workspace
oc exec -it $POD_NAME -c bob-cli -- mount | grep workspace

# Check if they're the same device
oc exec -it $POD_NAME -c jenkins-agent -- df /workspace
oc exec -it $POD_NAME -c bob-cli -- df /workspace
```

**Solutions:**
1. Verify both containers mount the same volume name (`workspace-volume`)
2. Verify both containers mount at the same path (`/workspace`)
3. Check pod spec has shared volume defined:
   ```yaml
   volumes:
   - name: workspace-volume
     emptyDir: {}
   ```
4. Ensure both containers reference the same volume in `volumeMounts`:
   ```yaml
   volumeMounts:
   - name: workspace-volume  # Must match
     mountPath: /workspace   # Must match
   ```

---

#### Issue 7: "API key not found" or authentication errors

**Symptoms:**
```
Error: BOBSHELL_API_KEY not set
Error: Authentication failed
Error: Invalid API key
```

**Diagnosis:**
```bash
# Check secret exists
oc get secret bob-cli-credentials

# Check secret is mounted in pod
oc exec -it $POD_NAME -c bob-cli -- env | grep BOBSHELL

# Verify secret content (be careful with this in production)
oc get secret bob-cli-credentials -o jsonpath='{.data.BOBSHELL_API_KEY}' | base64 -d
```

**Solutions:**
1. Verify secret `bob-cli-credentials` exists in the correct namespace
2. Check secret has key `BOBSHELL_API_KEY` (exact spelling)
3. Verify pod spec references correct secret name and key
4. Recreate secret if needed:
   ```bash
   oc delete secret bob-cli-credentials
   oc create secret generic bob-cli-credentials \
       --from-literal=BOBSHELL_API_KEY="your-key-here"
   ```
5. Restart the pipeline to pick up new secret

---

### Phase 9: Workshop Participant Instructions

---

## 🎓 WORKSHOP PARTICIPANTS START HERE

**If you're a workshop participant/lab user, this is your section!**
**You do NOT need to do Phases 0-8 - those are already set up for you.**

---

#### Your Simple Workflow

```
1. Clone repo → 2. Edit modes → 3. Commit & Push → 4. Jenkins "Build Now" → 5. See results!
```

**No `oc` commands. No cluster access. Just Git, your editor, and Jenkins UI.**

---

#### Step-by-Step Instructions

**Objective:** Create your own custom Bob mode and test it in the Jenkins pipeline.

**What You'll Need:**
- Git repository URL (provided by instructor)
- Jenkins URL (provided by instructor)
- Your favorite code editor

**Steps:**

1. **Clone the repository:**
   ```bash
   git clone <repository-url-from-instructor>
   cd <repository-name>
   ```

2. **Open the custom modes file in your editor:**
   ```bash
   # Use your preferred editor
   code .bob/custom_modes.yaml
   # or
   vi .bob/custom_modes.yaml
   # or open in any editor you like
   ```

3. **Add your custom mode to the file:**
   ```yaml
   customModes:
     # ... existing modes ...
     
     - slug: my-custom-mode
       name: 🎯 My Custom Mode
       description: Your mode description
       roleDefinition: |
         You are Bob, specialized in [your specialty].
         Your expertise includes:
         - [Skill 1]
         - [Skill 2]
       whenToUse: |
         Use this mode when [scenarios].
       groups:
         - read
         - command
       customInstructions: |
         - [Instruction 1]
         - [Instruction 2]
   ```

4. **Validate your YAML (optional but recommended):**
   ```bash
   # Check syntax
   yamllint .bob/custom_modes.yaml
   
   # Or use Python
   python3 -c "import yaml; yaml.safe_load(open('.bob/custom_modes.yaml'))"
   ```

5. **Commit and push:**
   ```bash
   git add .bob/custom_modes.yaml
   git commit -m "Add my custom mode: my-custom-mode"
   git push origin main
   ```

6. **Trigger Jenkins build (NO `oc` COMMANDS!):**
   - Open Jenkins in your browser (URL provided by instructor)
   - Log in with credentials (provided by instructor)
   - Find the `bob-sidecar-test` pipeline
   - Click "Build Now" button
   - Click on the build number (e.g., "#5") to see it running
   - Click "Console Output" to watch the logs

7. **Watch your mode in action:**
   - Look for the "Verifying custom modes are loaded" stage
   - You should see: `✅ Custom mode 'my-custom-mode' is loaded and working!`
   - Watch Bob use your mode in the test stages
   - See the results in the console output

8. **Iterate and improve:**
   - Based on the results, modify your mode in `.bob/custom_modes.yaml`
   - Commit and push your changes
   - Go back to Jenkins UI and click "Build Now" again
   - See your updated mode in action!
   - Repeat as many times as you want

**That's it! No `oc` commands, no cluster access needed.**

---

#### Advanced: Add a Custom Test Stage (Optional)

If you want to add a specific test for your mode, ask your instructor to add a stage to the Jenkinsfile:

```groovy
stage('Test My Custom Mode') {
    steps {
        container('bob-cli') {
            sh '''
                bob --chat-mode my-custom-mode \
                    -p "Your test prompt here" \
                    --hide-intermediary-output
            '''
        }
    }
}
```

Then you can test your mode with specific prompts!

---

#### Troubleshooting for Participants

**Problem:** "My mode isn't showing up"
- **Check:** Did you commit and push your changes?
- **Check:** Is your YAML syntax correct? (Ask instructor to validate)
- **Check:** Did you trigger a new build after pushing?

**Problem:** "Build failed"
- **Check:** Look at the Console Output for error messages
- **Check:** YAML syntax errors are the most common issue
- **Ask:** Your instructor for help - they can check the pod logs

**Problem:** "I don't see the 'Build Now' button"
- **Check:** Are you logged into Jenkins?
- **Check:** Do you have the right permissions? (Ask instructor)

**Remember:** You're only editing Git files and clicking buttons in Jenkins UI. If something's wrong with the infrastructure, ask your instructor!

---

### Phase 10: Validation Checklist

Use this checklist to verify the setup is complete:

**Infrastructure:**
- [ ] Jenkins is deployed and running
- [ ] `jenkins` ServiceAccount exists
- [ ] Obsolete per-user Bob CLI files removed (Phase 0.5)
- [ ] Bob CLI sidecar image built and available
- [ ] Secret `bob-cli-credentials` created with API key
- [ ] Namespace identified and used consistently

**Repository:**
- [ ] `.bob/custom_modes.yaml` exists in repository
- [ ] YAML syntax is valid
- [ ] At least one custom mode defined
- [ ] File committed and pushed to Git

**Pipeline:**
- [ ] `Jenkinsfile.sidecar-test` created
- [ ] Namespace hardcoded in image URL (not `${env.NAMESPACE}`)
- [ ] Jenkins pipeline job `bob-sidecar-test` created
- [ ] Pipeline configured to use correct Git repo and branch

**Execution:**
- [ ] Pipeline runs successfully
- [ ] Pod provisions with both containers
- [ ] Both containers can see shared workspace
- [ ] Bob CLI can execute commands
- [ ] Custom modes are loaded
- [ ] Custom mode can be invoked with `--chat-mode` flag
- [ ] Bob can read files from workspace

**Workshop Ready:**
- [ ] Workshop participants can clone repo
- [ ] Participants can add their own modes
- [ ] Changes to custom_modes.yaml are picked up on next build
- [ ] Clear success/failure indicators in pipeline output

---

## Success Criteria

The implementation is successful when:

1. ✅ Jenkins pipeline runs with Bob CLI sidecar
2. ✅ Bob CLI can see files checked out by Jenkins
3. ✅ Custom modes from `.bob/custom_modes.yaml` are loaded
4. ✅ Bob can be invoked with custom modes
5. ✅ Workshop participants can add/modify modes
6. ✅ Mode changes are reflected in subsequent builds
7. ✅ No ImagePullBackOff or ServiceAccount errors
8. ✅ Both containers share the same workspace

---

## Next Steps

After successful implementation:

1. **Create workshop exercises** for participants to:
   - Create a security reviewer mode
   - Create a deployment analyzer mode
   - Create a documentation generator mode
   - Create a test failure analyzer mode

2. **Add more pipeline stages** that use Bob:
   - Code review automation
   - Test failure analysis
   - Deployment risk assessment
   - Documentation generation
   - Compliance checking

3. **Explore advanced features:**
   - MCP server integration for Jenkins operations
   - Custom skills for specialized tasks
   - Mode chaining for complex workflows
   - Conditional mode selection based on pipeline context

4. **Scale to multiple teams:**
   - Create team-specific mode libraries
   - Share modes across projects
   - Version control mode evolution
   - Document mode best practices

---

## Common Pitfalls and How to Avoid Them

### 1. Variable Evaluation Timing
**Problem:** Using `${env.NAMESPACE}` in the agent YAML block  
**Why it fails:** Environment variables are evaluated after agent provisioning  
**Solution:** Hardcode the namespace or use Jenkins global variables

### 2. Dockerfile Naming
**Problem:** Using `bob-cli-sidecar.Dockerfile` instead of `Dockerfile`  
**Why it fails:** Docker build strategy expects `Dockerfile` in context root  
**Solution:** Name it `Dockerfile` and use `--from-dir=.`

### 3. Missing ServiceAccount
**Problem:** Assuming `jenkins` ServiceAccount exists  
**Why it fails:** Fresh environments don't have it until Jenkins is deployed  
**Solution:** Deploy Jenkins first or create SA manually

### 4. Permission Issues
**Problem:** Using `chmod 777` instead of OpenShift-idiomatic permissions  
**Why it's suboptimal:** Works but not best practice  
**Solution:** Use `chgrp -R 0 && chmod -R g=u`

### 5. Mode Discovery Path Ambiguity
**Problem:** Setting `HOME=/workspace` makes `.bob/` resolve to same location via two paths  
**Why it's confusing:** Can't tell if Bob used project path or global path  
**Solution:** Acceptable for workshop, but document the behavior

---

## Reference Documentation

- [Bob Shell Configuration](https://bob.ibm.com/docs/shell/configuration/configuring)
- [Bob Custom Modes](https://bob.ibm.com/docs/shell/configuration/custom-modes-bobshell)
- [Kubernetes Sidecar Pattern](https://kubernetes.io/docs/concepts/workloads/pods/#how-pods-manage-multiple-containers)
- [Jenkins Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/)
- [OpenShift Security Context Constraints](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)

---

## Support

For issues or questions:

1. **Check the Troubleshooting Guide** (Phase 8) - covers the 7 most common issues
2. **Review Bob CLI logs:** `oc logs <pod-name> -c bob-cli`
3. **Review Jenkins agent logs:** `oc logs <pod-name> -c jenkins-agent`
4. **Check pod events:** `oc describe pod <pod-name>`
5. **Verify workspace sharing:** Exec into both containers and compare `ls /workspace`
6. **Check image pull:** `oc describe pod <pod-name> | grep -A 10 Events`

---

## Appendix: Quick Reference Commands

```bash
# Set your namespace
export NAMESPACE="sre-deploy-lab"
oc project $NAMESPACE

# Build Bob CLI image
cd k8s/openshift/bob-cli-sidecar
oc start-build bob-cli-sidecar --from-dir=. --follow

# Create secret
oc create secret generic bob-cli-credentials \
    --from-literal=BOBSHELL_API_KEY="your-key"

# Verify setup
oc get sa jenkins
oc get secret bob-cli-credentials
oc get imagestream bob-cli-sidecar

# Monitor pipeline
oc get pods -w -l jenkins-agent=sidecar-test

# Debug
POD=$(oc get pods -l jenkins-agent=sidecar-test -o jsonpath='{.items[0].metadata.name}')
oc exec -it $POD -c bob-cli -- bash
oc logs $POD -c bob-cli
oc describe pod $POD