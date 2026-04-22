# Workshop Setup Guide

End-to-end instructions for an **instructor/admin** standing up this workshop for a group.

Participants never need to run any `oc` commands — they just log into Jenkins with pre-made credentials, edit `.bob/custom_modes.yaml` on their own branch, push, and click Build Now. This doc covers everything **you** need to do before they arrive.

Estimated setup time: **45 minutes** the first time, **15 minutes** once you're familiar with the flow.

---

## What you're building

By the end of this setup, you'll have:

- One OpenShift project containing Jenkins + the Bob CLI sidecar image
- A shared Jenkins instance with `workshop-admin` + 20 (or N) participant accounts, no OpenShift credentials required
- A working test pipeline that proves the sidecar mechanism loads custom Bob modes from a repo
- A credential list to hand out to participants

During the workshop, each participant:
1. Logs into Jenkins with their pre-made credentials
2. Creates their own pipeline job pointed at their own Git branch
3. Pushes new Bob modes to their branch
4. Runs their pipeline and watches Bob use the new modes

---

## Prerequisites

Before starting, you need:

- [ ] An **IBM TechZone** account (or equivalent OpenShift cluster access)
- [ ] **`oc` CLI** installed locally ([download](https://mirror.openshift.com/pub/openshift-v4/clients/ocp/))
- [ ] A **Bob Shell API key** from https://bob.ibm.com
- [ ] **Git access** to this repo (read access if public; a Personal Access Token if private)
- [ ] Ability to push a branch to this repo (participants will need this too)
- [ ] Basic familiarity with OpenShift / Kubernetes (enough to run `oc` commands)

---

## Step 1 — Reserve a TechZone environment

1. Log into [IBM TechZone](https://techzone.ibm.com/)
2. Reserve an **OpenShift cluster** environment (Red Hat OpenShift on IBM Cloud, or any OCP 4.x reservation works)
3. Wait for provisioning — typically **30–60 minutes**. TechZone emails you when it's ready.
4. When you get the email, it contains:
   - The cluster API URL (e.g. `https://api.itz-xxxxxx.infra01-lb.dal14.techzone.ibm.com:6443`)
   - A `kubeadmin` password, OR instructions to log in with your IBM ID via the OpenShift web console

**Tip for later**: note the cluster's expiration date. TechZone environments self-destruct after a set period (typically 3–5 days). Plan your workshop within that window.

---

## Step 2 — Log in and create your project

From your local terminal:

```bash
# Easiest: grab the login command from the OpenShift web console
# Click your username (top-right) → "Copy login command" → Display Token → paste the `oc login ...` command

# Or, login with kubeadmin creds directly:
oc login --server=<cluster-api-url> -u kubeadmin -p <password>

# Confirm access
oc whoami
oc auth can-i create projects   # should print: yes

# Create your project (pick a unique name)
oc new-project bob-workshop-<your-identifier>
```

Take note of the **project name** — you'll use it in Step 5.

---

## Step 3 — Clone this repo and build the Bob CLI sidecar image

```bash
# Clone or pull latest
git clone <this-repo-url>
cd us-fsm-ce-fis-bob-a-thon

# Build the Bob CLI sidecar image into your project's internal registry
cd k8s/openshift/bob-cli-sidecar
oc new-build --binary --name=bob-cli-sidecar --strategy=docker
oc start-build bob-cli-sidecar --from-dir=. --follow

# Verify
oc get imagestream bob-cli-sidecar
```

Expected: a ~2–5 minute build producing an ImageStream named `bob-cli-sidecar` with tag `latest`.

---

## Step 4 — Create the Bob API key Secret

```bash
# In your terminal, set the key (use single quotes)
export BOBSHELL_API_KEY='<paste-your-bob-api-key>'

# Create the Secret
oc create secret generic bob-cli-credentials \
    --from-literal=BOBSHELL_API_KEY="$BOBSHELL_API_KEY"

# Verify
oc get secret bob-cli-credentials
```

---

## Step 5 — Deploy the Workshop Jenkins

This is where the reusable kit does the heavy lifting.

```bash
cd k8s/openshift/jenkins-workshop

# Pick an admin password — do NOT commit this anywhere
export WORKSHOP_ADMIN_PW='pick-a-strong-one'

# Optional: override the default 20 participants
# export USER_COUNT=15

# Run the kit
./setup.sh
```

The script:
- Deploys Jenkins via the `jenkins-persistent` template (OAuth disabled)
- Creates the admin password Secret
- Mounts the Groovy init script as a ConfigMap into `init.groovy.d`
- Wires up env vars, waits for rollout
- Prints the Jenkins URL and credential pattern

**Save the output** — you'll need the Jenkins URL and participant credentials list.

---

## Step 6 — Update the Jenkinsfile with your project name

The test pipeline's pod spec hardcodes the namespace for the Bob CLI image pull (OpenShift limitations — it can't resolve variables at pod provisioning time). You need to update it to match your project.

```bash
# From repo root, on a branch you control
# Open Jenkinsfile and replace the namespace
# Search for: fis-bobathon
# Replace with: your project name from Step 2
```

Or via sed (adjust the project name):

```bash
sed -i '' "s/fis-bobathon/$(oc project -q)/g" Jenkinsfile
```

Commit and push this change to the branch participants will fork from (typically `main` or a workshop-specific branch).

---

## Step 7 — Add GitHub credential for repo checkout

Jenkins needs to clone this repo. If your repo is:

- **Public** (accessible without auth): no credential needed; skip to Step 8
- **Private** (github.ibm.com or any private repo): create a GitHub Personal Access Token and add it to Jenkins

To create the credential:

1. Open the Jenkins URL from Step 5's output
2. Log in as `workshop-admin` with your chosen password
3. Go to **Manage Jenkins → Credentials → System → Global credentials → Add Credentials**
4. Fill in:
   - **Kind:** `Username with password`
   - **Username:** your GitHub username
   - **Password:** your GitHub PAT (must have `repo` scope)
   - **ID:** `github-pat` (exact string — participants' pipelines will reference this)
   - **Description:** `GitHub PAT for workshop repo`
5. Save

---

## Step 8 — Test the setup yourself

Before participants arrive, prove the pipeline works end-to-end.

In Jenkins (logged in as `workshop-admin`):

1. Click **New Item**
2. Name: `test-pipeline`
3. Select **Pipeline** → **OK**
4. Scroll to **Pipeline** section:
   - **Definition:** `Pipeline script from SCM`
   - **SCM:** `Git`
   - **Repository URL:** your repo URL
   - **Credentials:** select `github-pat` (if private)
   - **Branch Specifier:** `*/main` (or whatever branch has the Jenkinsfile)
   - **Script Path:** `Jenkinsfile` (or leave blank — it's the Jenkins default)
5. **Save**, then **Build Now**

Watch the Console Output. The pipeline should complete the `Checkout` stage and finish `SUCCESS`, with the workspace contents listed — you should see `.bob/`, `Jenkinsfile`, `order-service/`, etc.

The lab stages are placeholders until each lab colleague fleshes them out; this smoke test only proves that the agent pod provisions, both containers start, and the repo lands in the shared workspace volume.

If the pipeline fails, see the Troubleshooting section below.

---

## Step 9 — Hand out credentials to participants

For each participant, provide:

- **Jenkins URL**: from Step 5 output
- **Username**: `user1` through `user20` (assign one per person)
- **Password**: `bobathon-1` through `bobathon-20` (matches the username suffix)
- **Git repo URL**: where they'll push their branches
- **Credential ID to reference**: `github-pat` (if your repo is private)

**Recommended**: create a table or shared doc mapping names → credentials so you don't assign the same login twice.

---

## During the workshop — what participants do

Participants follow this loop independently:

1. Clone the repo, create their own branch (e.g. `user1-modes`)
2. Edit `.bob/custom_modes.yaml` to add a custom mode
3. Commit + push their branch
4. Log into Jenkins with their assigned `userN` credentials
5. Create their own pipeline job pointed at their branch (config is the same as Step 8, but with their branch name)
6. Click **Build Now** — watch Bob pick up their mode

They can iterate as many times as they want — push a change, rebuild, see the new mode in action.

---

## After the workshop — teardown

When the event is done:

```bash
cd k8s/openshift/jenkins-workshop
./teardown.sh

# Optional: delete the whole project (if you don't need the artifacts)
oc delete project <your-project-name>
```

TechZone environments auto-expire anyway, but tearing down cleanly is a good habit.

---

## Troubleshooting

### `jenkins-persistent` template not found (Step 5)

Run `oc get template jenkins-persistent -n openshift` — if it returns `not found`, your cluster is missing the template. Options:

- Use a different TechZone environment type (the "OpenShift sandbox" reservations typically have it)
- Install the Jenkins Operator manually (out of scope for this doc)

### Pipeline fails with `ImagePullBackOff`

The image URL in `Jenkinsfile` probably still says `fis-bobathon` (or someone else's project). Revisit Step 6.

### Participant login doesn't work

Double-check the password pattern: `user1` → `bobathon-1`, `user2` → `bobathon-2`, etc. If it still fails, log into Jenkins as `workshop-admin` and check **Manage Jenkins → Users** — the account may not have been created (check the Jenkins pod logs for `[workshop-init]` output to confirm the init script ran).

### Bob API rate limits during the workshop

20+ participants hammering one API key can hit rate limits. If you see `Rate limit exceeded` errors in pipeline console output:
- Pause and restart later, OR
- Prepare a second API key in advance and swap it:
  ```bash
  oc delete secret bob-cli-credentials
  oc create secret generic bob-cli-credentials \
      --from-literal=BOBSHELL_API_KEY='<fallback-key>'
  # Next pipeline run picks up the new key automatically
  ```

---

## References

- [`k8s/openshift/jenkins-workshop/README.md`](k8s/openshift/jenkins-workshop/README.md) — workshop Jenkins kit internals, for teams adapting the kit
- [Bob Shell docs](https://bob.ibm.com/docs)
- [IBM TechZone](https://techzone.ibm.com/)
