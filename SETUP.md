# Setup Guide

This guide walks you through deploying the Dental Claims application to an OpenShift cluster from scratch and optionally adding Jenkins CI/CD. It assumes you have no prior OpenShift experience.

**Time required:** ~20 minutes for the app (plus ~10 minutes for image builds), ~10 more minutes if adding Jenkins

---

## Prerequisites

Install these tools first (macOS):

```bash
xcode-select --install          # gives you git, make, and curl
brew install openshift-cli      # the oc CLI
brew install podman             # builds container images locally
```

Start the Podman machine (one-time setup):

```bash
podman machine init
podman machine start
```

---

## Step 1: Reserve a TechZone Environment

Go to the [Base OpenShift TechZone collection](https://techzone.ibm.com/collection/695ee737853c17e9e412046e/journey-base-open-shift) and select **"OCP-V on IBM Cloud"** to reserve your environment.

When configuring the reservation, select the **16 vCPU / 64 GB RAM** worker node flavor with **100 GB** ephemeral storage. This is the minimum size that comfortably runs all services — smaller flavors run out of CPU for scheduling.

Once your reservation is ready (usually 15-30 minutes), you'll receive credentials on the reservation page:

| Credential | What It's For |
|---|---|
| **API URL** | Used for `oc login` (e.g., `https://api.your-cluster.cloud.ibm.com:6443`) |
| **Cluster admin username** | Login username (e.g., `kubeadmin`) |
| **Cluster admin password** | Login password |
| **OCP Console URL** | Web UI for browsing the cluster (optional) |

Keep this page open — you'll need these values in Step 3.

### What You Get

- OpenShift 4.18 cluster with up to 7 worker nodes (16 vCPU / 64 GB RAM each)
- Public ingress (your app will be accessible via HTTPS)
- A built-in container image registry (no Docker Hub or external registry needed)

---

## Step 2: Install the OpenShift CLI

The `oc` command-line tool is how you interact with the cluster from your terminal.

**macOS (Homebrew):**
```bash
brew install openshift-cli
```

**Other platforms:**
Download from the OCP Console (your TechZone reservation provides the URL) — click the **?** icon in the top-right → **Command Line Tools**.

**Verify it installed:**
```bash
oc version
```

---

## Step 3: Log In to Your Cluster

Use the credentials from your TechZone reservation page:

```bash
oc login --username=<cluster-admin-username> --password=<password> --server=<api-url>
```

Example:
```bash
oc login --username=kubeadmin --password=abc123-XYZ --server=https://api.my-cluster.cloud.ibm.com:6443
```

You may see a certificate warning — type `y` to accept (TechZone clusters use self-signed certs).

> **Tip:** Save your full `oc login` command somewhere handy (e.g., a sticky note or text file). OpenShift tokens expire after a period of inactivity and you'll need to re-authenticate. Having the command ready makes it quick to get back in.

**Verify you're connected:**
```bash
oc whoami        # Should print your username
oc get nodes     # Should list the cluster's worker nodes
```

---

## Step 4: Create a Project (Namespace)

A project is a logical space on the cluster that holds all your app's resources.

```bash
oc new-project dental-claims
```

---

## Step 5: Enable the Internal Image Registry

OpenShift has a built-in container image registry. On TechZone UPI clusters, it starts disabled. You need to turn it on so the deploy script can push your images.

### 5a: Deploy the Registry

Check if the registry is already running:
```bash
oc get configs.imageregistry.operator.openshift.io/cluster -o jsonpath='{.spec.managementState}'
```

- If the output is **`Managed`** — skip to Step 5b.
- If the output is **`Removed`** — deploy it:

```bash
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge \
  --patch '{"spec":{"managementState":"Managed","storage":{"emptyDir":{}}}}'
```

Wait for the registry pod to start:
```bash
oc get pods -n openshift-image-registry -w
```

Press `Ctrl+C` once you see `image-registry-xxxxx` at `1/1 Running`.

> **Note:** `emptyDir` storage means images are lost if the registry pod restarts. This is fine for demos — just re-run `make oc-deploy` if it happens.

### 5b: Expose the Registry Route

This creates a public hostname so you can push images from your laptop:

```bash
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge \
  --patch '{"spec":{"defaultRoute":true}}'
```

Verify the route was created:
```bash
oc get route default-route -n openshift-image-registry
```

You should see a hostname like `default-route-openshift-image-registry.apps.your-cluster.cloud.ibm.com`.

---

## Step 6: Add Your Bob Shell API Key

Bob CLI runs inside the cluster and provides AI-assisted operations (diagnosing failures, fixing configurations, recovering deployments). You need a Bob Shell API key before deploying.

Check your Slack history for a welcome message from Ask Bob that includes your key. Then create a `.env` file in the project root:

```
BOBSHELL_API_KEY=your-key-here
```

The deploy script reads this file on your machine, creates a Kubernetes Secret on the cluster, and the Bob CLI pod picks up the key from that Secret. The `.env` file stays on your machine — it is not copied into any container.

> **Important:** Never commit the `.env` file to git. It is already in `.gitignore`.

---

## Step 7: Deploy the Application

```bash
make oc-deploy
```

That's it. The script handles everything automatically:

1. Verifies you're logged in and in the right project
2. Gets the registry hostname from the cluster
3. Creates a service account token and logs into the registry
4. Builds all 5 container images with `podman build --platform linux/amd64` (safe on Apple Silicon and Intel Macs)
5. Pushes the images to the internal registry
6. Applies security context constraints (so database containers can run)
7. Creates ConfigMaps for database initialization scripts
8. Applies all Kubernetes manifests (dynamically rewrites image references)
9. Applies the frontend Route for public HTTPS access
10. Builds and deploys the Bob CLI pod with your API key
11. Prints the app URL

**Build times:** Expect ~10 minutes on the first run (downloading base images + cross-compilation on Apple Silicon). Subsequent runs are faster thanks to layer caching.

Once you see `Deployment complete!`, wait for all pods to be ready:

```bash
oc get pods -w
```

Watch until every pod shows `1/1` under the `READY` column. This may take 1-2 minutes as the databases initialize and the services start. Press `Ctrl+C` once they're all ready.

---

## Step 8: Verify the Deployment

**Get your app URL:**
```bash
oc get route frontend -o jsonpath='{.spec.host}'
```

Open `https://<that-host>` in your browser. You should see the Dental Claims frontend.

**Check pod status:**
```bash
oc get pods
```

All pods should show `Running` with `1/1` ready. It may take 1-2 minutes for all pods to start.

---

## Architecture Notes

### Frontend Runs as a Single Replica

The frontend deployment is set to `replicas: 1`. This is intentional — the AI Operations terminal uses Server-Sent Events (SSE) with an in-memory event bus. Multiple replicas would cause events from the bob-cli pod to land on different frontend pods than the user's browser SSE connection, resulting in missing terminal events.

### SSE Route Timeout

The frontend route includes a `haproxy.router.openshift.io/timeout: 300s` annotation. Bob CLI can take 60-90 seconds to analyze and respond to issues. Without this annotation, HAProxy's default 30-second timeout kills the SSE connection mid-operation, causing missed events.

If you manually create the route instead of using `oc apply -f k8s/openshift/frontend-route.yaml`, add the annotation:

```bash
oc annotate route frontend haproxy.router.openshift.io/timeout=300s
```

---

## Jenkins CI/CD Setup (Optional)

This section adds Jenkins CI/CD to your OpenShift deployment. It gives the Pipeline page a real Jenkins backend so you can demo AI-augmented pipelines with live builds instead of mock data.

**Prerequisite:** Complete Steps 1-8 above first — all services must be running on the cluster before setting up Jenkins.

### What You'll Need

Before starting, gather these two things:

| Secret | Where to Get It |
|---|---|
| **GitHub Enterprise PAT** | [github.ibm.com/settings/tokens](https://github.ibm.com/settings/tokens) — create a token with `repo` scope |
| **Bob Shell API Key** | Same key from your `.env` file (you already have this from Step 6) |

### Step 9: Deploy Jenkins + Create Pipeline Job

One command does everything — deploys Jenkins, installs plugins, configures credentials, and creates the pipeline job:

```bash
make oc-deploy-jenkins
```

The script will prompt you for your GitHub PAT and Bob API key. Or pass them as environment variables to skip the prompts:

```bash
GITHUB_PAT=ghp_xxx BOB_API_KEY=sk-xxx make oc-deploy-jenkins
```

**What this does automatically:**

1. Deploys Jenkins on OpenShift with 2Gi memory and 5Gi persistent storage
2. Waits for Jenkins to fully start (2-5 minutes)
3. Installs required plugins (Pipeline, Git, GitHub, Credentials)
4. Creates two credentials in Jenkins (`github-pat` and `bobshell-api-key`)
5. Creates the `dental-pipeline` job pointing to the `Jenkinsfile` in this repo
6. Patches the frontend to run as the `jenkins` service account — this auto-mounts a fresh, auto-rotating SA token so the Pipeline page can trigger builds without storing a static token
7. Sets `JENKINS_URL` and `JENKINS_AUTH_MODE` on the frontend deployment

**First time opening Jenkins UI:** When you visit the Jenkins URL, OpenShift will show a permissions consent screen asking Jenkins to access `user:info` and `user:check-access`. Click **"Allow selected permissions"** — this is standard OpenShift OAuth and lets Jenkins authenticate you as your cluster user. It's a one-time prompt per user.

When the setup script finishes, it prints the Jenkins URL:

```
========================================
  Jenkins setup complete!
========================================

Jenkins UI:     https://jenkins-dental-claims.apps.your-cluster.cloud.ibm.com
Pipeline job:   https://jenkins-dental-claims.apps.your-cluster.cloud.ibm.com/job/dental-pipeline/
```

### Step 10: Test It

#### From Jenkins UI

1. Open the Jenkins URL from Step 9 in your browser
2. Click on **dental-pipeline**
3. Click **"Build with Parameters"** on the left sidebar
4. Leave BRANCH as `demo/happy-path` (or change to another demo branch)
5. Click **Build**

Watch the build progress in Jenkins. If you have the app's Pipeline page open with the toggle set to **Live**, events will stream in real-time.

#### From the App

1. Open your app (`oc get route frontend -o jsonpath='{.spec.host}'`)
2. Go to the **Pipeline** page
3. Flip the toggle in the top-right from **Mock** to **Live**
4. Select a scenario and click **Run Pipeline**
5. Watch the stages animate and the terminal fill with real build output

> **Note:** If you haven't created the demo branches yet (Step 11), use Mock mode. The Live toggle triggers real Jenkins builds that need the branches to exist on GitHub.

### Step 11: Create Demo Branches (Optional)

The pipeline uses different Git branches to demonstrate different failure scenarios. Each branch is forked from `main` with one targeted change:

| Branch | What's Different | Pipeline Outcome |
|---|---|---|
| `demo/happy-path` | Minor change (comment, version bump) | All stages pass, Bob approves |
| `demo/test-failure` | Bug in ClaimService.java — missing null check | Test fails, Bob identifies fix |
| `demo/security-vuln` | Old base image in Dockerfile | Security scan finds CVEs, Bob analyzes |
| `demo/db-migration` | SQL migration adds column that already exists | Deploy fails, Bob fixes migration |

Create them from `main` after merging any pending PRs:

```bash
# Start from main
git checkout main
git pull

# Happy path — minor change so there's a diff for Bob to review
git checkout -b demo/happy-path
# Make a small change (add a comment, bump a version, etc.)
git commit -am "minor: add coverage notes to README"
git push origin demo/happy-path

# Test failure — remove null check in ClaimService
git checkout main
git checkout -b demo/test-failure
# Edit claims/service/src/.../service/ClaimService.java
# Remove the null check in validatePatient() so patient.getId() throws NPE
git commit -am "refactor: simplify patient validation"
git push origin demo/test-failure

# Security vulnerability — use old base image
git checkout main
git checkout -b demo/security-vuln
# Edit claims/service/Dockerfile — change base image to eclipse-temurin:17.0.8-jre-alpine
git commit -am "chore: pin base image version"
git push origin demo/security-vuln

# DB migration failure — add column that already exists
git checkout main
git checkout -b demo/db-migration
# Create claims/database/V4__add_coverage_type.sql with:
#   ALTER TABLE claims ADD COLUMN coverage_type VARCHAR(50);
# (without IF NOT EXISTS — this is the bug)
git commit -am "feat: add coverage type to claims"
git push origin demo/db-migration
```

---

## Troubleshooting

### Pods stuck in `ImagePullBackOff`
The registry may have lost its images (emptyDir storage). Re-run:
```bash
make oc-deploy
```

### Database pods stuck in `CrashLoopBackOff`
The security context constraint (SCC) patch may not have applied. Check:
```bash
oc get clusterrolebinding dental-claims-anyuid
```
If it doesn't exist, the script should have created it. Try re-running `make oc-deploy`.

### Pods crash with `exec format error`
Images were built for the wrong CPU architecture. The deploy script uses `--platform linux/amd64` to handle this automatically. If you see this error, make sure you're using the `setup.sh` script (via `make oc-deploy`) and not building images manually.

### `oc login` fails with connection errors
- Double-check the API URL from your TechZone reservation page
- Make sure you're on a network that can reach IBM Cloud (some corporate VPNs may block it)
- If your reservation expired, request a new one

### Frontend loads but shows no data
The backend services or databases may still be starting. Wait a minute and refresh. Check:
```bash
oc logs deployment/claims-service --tail=20
```

### Jenkins pod stuck in `Pending`
The cluster may not have enough resources. Check:
```bash
oc describe pod -l name=jenkins
```
Look for "Insufficient cpu" or "Insufficient memory" in the Events section. You may need to scale down other deployments or use a larger TechZone flavor.

### "JENKINS_TOKEN not configured and no SA token mounted" error in the app
The frontend pod isn't running as the `jenkins` service account. Re-run Jenkins setup to patch it:
```bash
make oc-deploy-jenkins
```
Or patch it manually:
```bash
oc patch deployment/frontend --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/serviceAccountName","value":"jenkins"}]'
```

### Pipeline triggers but no events appear in the app
Jenkins events are sent to `http://frontend:3000/api/ai-ops/events` (cluster-internal). Check:
1. Jenkins can reach the frontend service: `oc exec dc/jenkins -- curl -s http://frontend:3000/health`
2. The `FRONTEND_URL` in the Jenkinsfile matches the frontend service name

### GitHub clone fails with SSL error
`github.ibm.com` uses IBM's internal CA. In Jenkins UI:
1. Go to **Manage Jenkins** → **Global Tool Configuration** → **Git**
2. Add extra git option: `-c http.sslVerify=false`

Or set it cluster-wide for the Jenkins pod:
```bash
oc set env dc/jenkins GIT_SSL_NO_VERIFY=true
```

---

## Day-to-Day Commands

```bash
# Redeploy everything (rebuild all images + apply manifests)
make oc-deploy

# Redeploy a single service (faster — only rebuilds one image)
make oc-redeploy-claims
make oc-redeploy-patients
make oc-redeploy-providers
make oc-redeploy-analytics
make oc-redeploy-frontend

# View logs
oc logs deployment/claims-service -f
oc logs deployment/frontend -f

# Check pod status
oc get pods

# Remove everything from the cluster
make oc-teardown

# Deploy/update Jenkins
make oc-deploy-jenkins

# Remove Jenkins from the cluster
make oc-teardown-jenkins

# View Jenkins logs
oc logs dc/jenkins -f

# Restart Jenkins
oc rollout restart dc/jenkins

# Trigger a build from the command line
oc get route jenkins -o jsonpath='{.spec.host}' | xargs -I{} \
  curl -sk -X POST "https://{}/job/dental-pipeline/buildWithParameters?BRANCH=demo/happy-path" \
  -H "Authorization: Basic $(echo -n admin:<your-token> | base64)"
```

---

## Switching to a New TechZone Environment

When your TechZone reservation expires and you get a new one, just repeat Steps 3-5 and 7 (your `.env` file is already in place):

```bash
oc login --username=<new-user> --password=<new-password> --server=<new-api-url>
oc new-project dental-claims

# Enable registry (Steps 5a and 5b)
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge \
  --patch '{"spec":{"managementState":"Managed","storage":{"emptyDir":{}}}}'
# Wait for registry pod...
oc patch configs.imageregistry.operator.openshift.io/cluster --type merge \
  --patch '{"spec":{"defaultRoute":true}}'

# Deploy
make oc-deploy

# Then re-deploy Jenkins (if using it)
make oc-deploy-jenkins
```

No code changes needed. The deploy script detects everything from the cluster automatically. Your demo branches on GitHub Enterprise persist across environments — no need to recreate them.
