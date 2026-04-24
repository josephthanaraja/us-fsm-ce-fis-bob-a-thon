# Dry Run — Validate `setup/` Before Adopting

**Goal:** Stand up a fresh OpenShift + Jenkins environment using the `setup/` toolchain as-shipped, and prove a pipeline run where Bob loads a custom mode from a shared workspace. No changes to `setup/` get committed during the dry run — every deviation is a local workaround, and each one tells us what Phase 2 of `ADOPT_INSTRUCTOR_SETUP_PLAN.md` needs to fix.

**Branch:** `adopt-instructor-setup` (or any branch with `.bob/custom_modes.yaml` at the repo root — the test pipeline checks out a branch and reads `.bob/` from it).

All commands below are copy-pasteable as-is. Fill in only the placeholders in `<angle-brackets>`.

---

## Namespaces for this dry run

Your coworker has already deployed the setup once under the default names (`jenkins`, `user1-dev`, …). To avoid collisions we use suffixed names:

| Role | Default in the docs | This dry run |
|---|---|---|
| Jenkins namespace | `jenkins` | `jenkins-andy-test` |
| Per-user namespaces | `user1-dev`, `user2-dev`, … | `user1-andy-dev`, `user2-andy-dev` |
| SCC ClusterRoleBinding | `jenkins-anyuid` (cluster-scoped) | `jenkins-andy-test-anyuid` |
| Bob image registry path | `<registry>/jenkins/bob-cli:latest` | `<registry>/jenkins-andy-test/bob-cli:latest` |
| Jenkins usernames | `user1` … | unchanged (still `user1`, `user2`, …) |
| Helm release name | `jenkins` | unchanged (release is scoped to the namespace) |

All renames are applied via local sed pipes and inline commands — no files in `setup/` are edited.

---

## Three deliberate deviations from the original setup docs

1. **Bob image source.** The doc says "tag and push `bob-cli:latest`" but doesn't include a Dockerfile. Build from `setup/bob-cli/Dockerfile` (in this repo).
2. **Secret naming.** Create the secret as `bob-cli-credentials` with key `BOBSHELL_API_KEY`. Our Bob binary reads `BOBSHELL_API_KEY` from env and won't authenticate under the doc's `bob-api-key` / `api-key` names.
3. **Test pipeline pod spec.** Use the corrected pipeline in step 18. It keeps the 3-container shape from the doc but adds explicit shared-volume + `workingDir` + `HOME=/workspace` on every container — see [Why the explicit pod spec](#why-the-explicit-pod-spec) below.

---

## 1. Install local tooling

On macOS with Homebrew:

```bash
brew install helm podman jq
```

(`oc` you presumably already have; `curl` and `python3` ship with macOS.)

Verify:

```bash
oc version --client
helm version --short
podman --version
python3 --version
```

The Python scripts we run (`generate-security-setup.py`, `generate-jenkins-users_v2.py`) use stdlib only — no `pip install` needed.

## 2. Log into the cluster

```bash
oc login --server=<cluster-api-url> -u <your-user>
oc whoami
oc auth can-i create projects    # should print: yes
```

## 3. Create the Jenkins namespace

```bash
oc new-project jenkins-andy-test \
  --description='Andy dry-run Jenkins' \
  --display-name='Jenkins (Andy dry run)'
```

## 4. Add the Jenkins Helm repo

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
```

## 5. Apply the Jenkins SCC binding

Jenkins runs as UID 1000; OpenShift's default `restricted-v2` SCC blocks this. The binding grants the `jenkins` ServiceAccount the `anyuid` SCC so the pod can start.

The shipped YAML targets namespace `jenkins` and names the ClusterRoleBinding `jenkins-anyuid`. Rewrite it on the fly so it targets our namespace and doesn't collide with your coworker's binding:

```bash
sed -e 's/namespace: jenkins$/namespace: jenkins-andy-test/' \
    -e 's/name: jenkins-anyuid/name: jenkins-andy-test-anyuid/' \
    setup/assets/jenkins-scc.yaml | oc apply -f -

oc get clusterrolebinding jenkins-andy-test-anyuid
```

## 6. Prepare the Jenkins Helm values file

```bash
cp setup/assets/template-jenkins-values_v2.yaml setup/assets/jenkins-values.yaml
```

`jenkins-values.yaml` is gitignored — safe to edit locally if you ever need to.

## 7. Install Jenkins

```bash
helm install jenkins jenkins/jenkins \
  -f setup/assets/jenkins-values.yaml \
  -n jenkins-andy-test \
  --wait \
  --timeout 10m
```

Expected: runs ~3–5 minutes, ends with `STATUS: deployed`.

## 8. Retrieve the admin password and create a route

```bash
# Admin password (auto-generated on first install)
oc get secret jenkins -n jenkins-andy-test \
  -o jsonpath='{.data.jenkins-admin-password}' | base64 -d
echo

# Edge-terminated route (HTTPS in, HTTP to the pod)
oc create route edge jenkins \
  --service=jenkins \
  --port=8080 \
  --insecure-policy=Redirect \
  -n jenkins-andy-test

# Route hostname — save this URL
oc get route jenkins -n jenkins-andy-test -o jsonpath='{.spec.host}'
echo
```

Note down the admin password and the route hostname. You'll use them in the next three steps.

## 9. Enable Jenkins security

Jenkins starts unsecured. Generate a Groovy script that turns on security and creates the `admin` account with the password you just retrieved.

```bash
python3 setup/scripts/generate-security-setup.py --password '<admin-password>'
```

Copy the entire script output. Open `https://<jenkins-route>/script` in your browser, paste, click **Run**. You should see `Security configured`. (If you get an "Oops" page, that's normal — reload the login page and log in as `admin`.)

## 10. Create the workshop Jenkins users

Generate the Groovy that creates `user1`–`user20`:

```bash
python3 setup/scripts/generate-jenkins-users_v2.py 20 --password 'Workshop2026!'
```

Copy the output. Logged in as `admin` at `https://<jenkins-route>/script`, paste and **Run**. Expected: `Done — 20 users created`.

Credential pattern after this step: username `userN`, password `userNWorkshop2026!` (e.g., `user1` / `user1Workshop2026!`).

## 11. Set up per-user folders with matrix auth

This is the feature we're validating: each user gets a folder where only they can see / edit jobs and credentials.

Paste the following Groovy into `https://<jenkins-route>/script` (still logged in as `admin`) and click **Run**:

```groovy
import jenkins.model.*
import hudson.security.*
import com.cloudbees.hudson.plugins.folder.*
import com.cloudbees.hudson.plugins.folder.properties.AuthorizationMatrixProperty

def instance = Jenkins.getInstance()

// Global strategy — authenticated users can log in but see nothing
def strategy = new ProjectMatrixAuthorizationStrategy()
strategy.add(Jenkins.ADMINISTER, "admin")
strategy.add(Jenkins.READ,       "authenticated")
instance.setAuthorizationStrategy(strategy)
instance.save()

// Per-folder permissions
(1..20).each { i ->
    def username = String.format("user%d", i)

    def folder = instance.getItem(username)
    if (!folder) {
        folder = instance.createProject(Folder, username)
        println "Created folder: ${username}"
    }

    def prop = new AuthorizationMatrixProperty()
    prop.add(Item.BUILD,      username)
    prop.add(Item.CANCEL,     username)
    prop.add(Item.CONFIGURE,  username)
    prop.add(Item.CREATE,     username)
    prop.add(Item.DELETE,     username)
    prop.add(Item.DISCOVER,   username)
    prop.add(Item.READ,       username)
    prop.add(Item.WORKSPACE,  username)
    prop.add(Run.DELETE,      username)
    prop.add(Run.UPDATE,      username)
    prop.add(Run.ARTIFACTS,   username)
    prop.add(com.cloudbees.plugins.credentials.CredentialsProvider.VIEW,           username)
    prop.add(com.cloudbees.plugins.credentials.CredentialsProvider.CREATE,         username)
    prop.add(com.cloudbees.plugins.credentials.CredentialsProvider.UPDATE,         username)
    prop.add(com.cloudbees.plugins.credentials.CredentialsProvider.DELETE,         username)
    prop.add(com.cloudbees.plugins.credentials.CredentialsProvider.MANAGE_DOMAINS, username)

    folder.addProperty(prop)
    folder.save()
    println "Configured folder: ${username}"
}

println "Done — each user can only see their own folder"
```

Log out of admin and log back in as `user1` / `user1Workshop2026!` to confirm you see only the `user1` folder on the homepage, and that clicking into the folder shows a **Credentials** link in the left sidebar.

> **Note — one addition vs. the coworker's Groovy.** The block above adds `CredentialsProvider.VIEW` to each user's folder permissions. Without it, the Credentials link doesn't render in the folder sidebar even though `CREATE/UPDATE/DELETE` are granted — user ends up with no UI path to add their own PAT. This is a Phase 2 change needed in `setup/INSTRUCTOR_SETUP_TZ.md` §3.1.7; flag it for the adoption plan.

## 12. Grant the Jenkins ServiceAccount cluster permissions

```bash
# Allow Jenkins to manage pods in its own namespace (dynamic agents)
oc adm policy add-role-to-user edit \
  system:serviceaccount:jenkins-andy-test:jenkins \
  -n jenkins-andy-test

# Allow Jenkins to pull images from the internal registry
oc policy add-role-to-user system:image-puller \
  system:serviceaccount:jenkins-andy-test:jenkins \
  -n jenkins-andy-test
```

## 13. Configure the Jenkins Kubernetes cloud

The Helm values file sets `JCasC.defaultConfig: false`, which skips the chart's default Kubernetes cloud config. Without a cloud, pipelines fail with `ERROR: No Kubernetes cloud was found.` Configure one now.

Logged in as `admin`, open `https://<jenkins-route>/script` and paste-and-run:

```groovy
import jenkins.model.*
import org.csanchez.jenkins.plugins.kubernetes.KubernetesCloud

def jenkins = Jenkins.getInstance()
jenkins.clouds.removeAll { it instanceof KubernetesCloud }

def cloud = new KubernetesCloud("kubernetes")
cloud.setNamespace("jenkins-andy-test")
cloud.setJenkinsUrl("http://jenkins.jenkins-andy-test.svc.cluster.local:8080")
cloud.setJenkinsTunnel("jenkins-agent.jenkins-andy-test.svc.cluster.local:50000")
cloud.setContainerCapStr("10")

jenkins.clouds.add(cloud)
jenkins.save()

println "Kubernetes cloud configured: ${cloud.name} in ${cloud.namespace}"
```

Expected output: `Kubernetes cloud configured: kubernetes in jenkins-andy-test`.

Verify via UI if you want: **Manage Jenkins → Clouds** should now list a `kubernetes` cloud pointing at `jenkins-andy-test`.

> This is a Phase 2 gap in `setup/INSTRUCTOR_SETUP_TZ.md` — see `CHANGES_NEEDED.md` item #5. The coworker's doc doesn't set up a cloud, and the values file's `defaultConfig: false` disables the chart's auto-config.

---

## 14. Create per-user OpenShift namespaces

`setup/scripts/create-projects.sh` hardcodes `JENKINS_NS='jenkins'` and `USERS=(user1 … user20)`. Rather than edit it, just inline the two commands-per-user it contains, using our names:

```bash
for USER in user1-andy user2-andy; do
  NS="${USER}-dev"

  # Create the namespace
  oc new-project "$NS" \
    --description="Workshop namespace for $USER (Andy dry run)" \
    --display-name="$USER - Workshop" || true

  # Grant the Jenkins SA deploy rights in this namespace
  oc adm policy add-role-to-user edit \
    system:serviceaccount:jenkins-andy-test:jenkins \
    -n "$NS"

  # Allow agent pods launched into this NS to pull the bob-cli image
  # from the jenkins-andy-test namespace's internal registry
  oc policy add-role-to-user system:image-puller \
    "system:serviceaccount:${NS}:default" \
    -n jenkins-andy-test

  # Apply the resource quota
  oc apply -f setup/assets/workshop-user-project-quota.yaml -n "$NS"
done
```

## 15. Build the Bob CLI image

Build from our Dockerfile, tagged as `bob-cli:latest` (keeping the doc's image name).

```bash
cd setup/bob-cli
podman build -t bob-cli:latest .
cd -
```

Expose the internal OpenShift registry for external push access (TechZone clusters don't expose it by default):

```bash
oc patch configs.imageregistry.operator.openshift.io/cluster \
  --type merge \
  -p '{"spec":{"defaultRoute":true}}'

# Wait for the route to appear (usually <30 seconds)
until oc get route default-route -n openshift-image-registry >/dev/null 2>&1; do sleep 2; done

REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')
echo "Registry: $REGISTRY"
```

Log in, tag, push:

```bash
podman login -u "$(oc whoami)" -p "$(oc whoami -t)" --tls-verify=false "$REGISTRY"
podman tag bob-cli:latest "$REGISTRY/jenkins-andy-test/bob-cli:latest"
podman push --tls-verify=false "$REGISTRY/jenkins-andy-test/bob-cli:latest"
```

Verify the ImageStream:

```bash
oc get imagestream bob-cli -n jenkins-andy-test
```

Expected: a row with tag `latest`.

## 16. Create the Bob API key secret

**This deviates from the doc** — we use our secret name and key so our Bob binary authenticates.

```bash
oc create secret generic bob-cli-credentials \
  --from-literal=BOBSHELL_API_KEY='<your-bob-api-key>' \
  -n jenkins-andy-test
```

Grant the Jenkins ServiceAccount read access to the secret:

```bash
oc create role bob-secret-reader \
  --verb=get \
  --resource=secrets \
  --resource-name=bob-cli-credentials \
  -n jenkins-andy-test

oc create rolebinding bob-secret-reader \
  --role=bob-secret-reader \
  --serviceaccount=jenkins-andy-test:jenkins \
  -n jenkins-andy-test
```

## 17. (Private repo only) Add a user-scoped GitHub PAT

Skip this step if your workshop repo is public.

**The credential must land in the *folder* store, not the *user* store.** Folder-store credentials show up in the pipeline Credentials dropdown; user-store credentials don't. The navigation below goes directly to the folder store — follow it exactly, don't click the **Credentials** link under your username in the top-right menu (that path lands on the wrong store).

1. Log into Jenkins as `user1` / `user1Workshop2026!`.
2. From the Jenkins homepage, click the **`user1`** folder (the one with the folder icon in the list of items).
3. In the folder's left sidebar, click **Credentials**.
4. You land on the folder's credential page. Click the **`(global)`** link under the **Stores scoped to user1** section (or, if a Stores table is shown, click the row labeled **Folder** with scope `user1`).
5. Click **Add Credentials** (top-right of the page, or the left-sidebar link).
6. Fill in:
   - **Kind:** Username with password
   - **Scope:** Global (this is the URL-matching domain — see note below)
   - **Username:** your GitHub username
   - **Password:** a GitHub PAT with `repo` scope
   - **ID:** `user1-github-pat`
   - **Description:** anything
7. **Create.**

> **About "Scope: Global".** Confusingly named — it does **not** mean "visible to all users." It means "applicable to any URL" (as opposed to a domain-restricted credential). Visibility is determined by the *store* you picked in step 4 (the `user1` folder store), which is only accessible to `user1` and admin. Other workshop users cannot see this PAT.

You'll pick this credential by its ID (`user1-github-pat`) when configuring the pipeline in step 18.

## 18. Push the branch and run the test pipeline

The test pipeline lives in `Jenkinsfile.test` on this branch. It's a 3-container pod (`build-tools` + `oc-tools` + `bob`) with explicit shared volumes, pointing at `jenkins-andy-test/bob-cli:latest` and the `bob-cli-credentials` secret — everything the prior steps set up.

### 18a. Commit and push the branch

From the repo root on your laptop:

```bash
git add Jenkinsfile.test DRY_RUN_PLAN.md ADOPT_INSTRUCTOR_SETUP_PLAN.md
git commit -m "Dry-run test pipeline for setup/ validation"
git push -u origin adopt-instructor-setup
```

### 18b. Create the Jenkins pipeline job

Still logged in as `user1`:

1. Click on the `user1` folder on the Jenkins homepage.
2. Click **New Item** → name it `setup-dry-run` → select **Pipeline** → **OK**.
3. Scroll to the **Pipeline** section at the bottom:
   - **Definition:** `Pipeline script from SCM`
   - **SCM:** `Git`
   - **Repository URL:** your GitHub repo URL (the one you just pushed to)
   - **Credentials:** the `user1-github-pat` you added in step 17 (leave as `- none -` if the repo is public)
   - **Branch Specifier:** `*/adopt-instructor-setup`
   - **Script Path:** `Jenkinsfile.test`
4. **Save.**
5. Click **Build Now.**

The pipeline will clone your branch, land it in `/workspace` on all three containers, and then the `bob` container runs `bob --chat-mode solution-code-reviewer -p "..."` to prove the custom mode loads from the checked-out `.bob/custom_modes.yaml`.

## 19. Validation gates

Watch the Console Output and confirm each gate:

- [ ] **Pod provisions** with three user containers (`build-tools`, `oc-tools`, `bob`) plus the auto-injected `jnlp`. No `ImagePullBackOff`.
- [ ] **Checkout stage**: `pwd` prints `/workspace`; `ls -la` shows `.bob/`, `Jenkinsfile`, `order-service/`.
- [ ] **Bob stage — PWD/HOME**: log shows `PWD: /workspace HOME: /workspace`.
- [ ] **Bob stage — `.bob/` visible**: `ls -la .bob/` inside the `bob` container lists `custom_modes.yaml`. *This is the shared-workspace check.*
- [ ] **Bob stage — mode loads**: console contains `CUSTOM_MODE_WORKING`.
- [ ] **Credential isolation**: log in as `user2` → confirm you can't see `user1`'s folder, `mode-test` pipeline, or the PAT.

If all six pass, the `setup/` toolchain is validated end-to-end.

If any fail, **don't edit `setup/`** — fix in the test pipeline or secret naming and note the fix. Those notes become Phase 2's change list in `ADOPT_INSTRUCTOR_SETUP_PLAN.md`.

---

## 20. Cleanup

Tear down everything this dry run created:

```bash
# Delete the Jenkins namespace (takes everything inside with it:
# the StatefulSet, PVC, ImageStream, Secret, Route, Role, RoleBinding)
oc delete project jenkins-andy-test --wait=false

# Delete the per-user namespaces
oc delete project user1-andy-dev user2-andy-dev --wait=false

# Delete the cluster-scoped SCC binding (survives namespace deletion)
oc delete clusterrolebinding jenkins-andy-test-anyuid --ignore-not-found
```

Namespace deletes are asynchronous — `oc get project | grep andy` should come back empty within a minute or two. The image-registry `defaultRoute` patch from step 15 is cluster-wide; leave it in place.

---

## Why the explicit pod spec

The doc's `template-jenkins-pipeline` declares no `volumes:`, no `workingDir:`, and no `HOME` env on the `bob` container. The Jenkins Kubernetes plugin *can* auto-inject a workspace volume across containers, but three things make that unreliable for our image on OpenShift:

- **Plugin-version-dependent behavior** — not something to hang a workshop on.
- **Our Bob image bakes in `WORKDIR /workspace` + `HOME=/workspace`** — if the plugin remaps CWD to `/home/jenkins/agent` but doesn't also change `HOME`, Bob writes state to one path and reads mode files from another.
- **OpenShift random-UID-in-group-0** — `/workspace` in our Dockerfile is pre-created with `chgrp 0` + `chmod g=u` so a random UID in group 0 can write to `.bob/`. `/home/jenkins/agent` in the `node:22-slim` base image isn't tuned this way; first write from a random UID fails.

Our proven pod spec (see `Jenkinsfile` lines 30–78) declares all four mechanisms explicitly: a named `workspace-volume` emptyDir at pod level, `volumeMounts` on each container to `/workspace`, `workingDir: /workspace` on each, and `env: HOME=/workspace` on each. The test pipeline in step 18 merges that mechanism into the doc's 3-container public-image shape.

---

## Implications for the adoption plan

Two scope items `ADOPT_INSTRUCTOR_SETUP_PLAN.md` doesn't call out that this dry run will confirm:

- **Phase 2 scope gap on `template-jenkins-pipeline`.** The current plan lists three line-level Bob-naming edits. If we want it to be a genuinely working reference, it also needs the shared-volume mechanism added — or delete it outright in Phase 5 since `Jenkinsfile.lab*solution` is the real reference.
- **Path A vs Path B (plan §7).** Path A ("adopt the 3-container model unchanged") isn't viable without the pod-spec additions. Either keep our 2-container pattern (our `jenkins-agent` image) or adopt the 3-container pattern **plus** the shared-volume mechanics — not a "public images only, zero custom work" option.

---

## Troubleshooting

- **`.bob/` not visible in the `bob` container after checkout.** The `workspace-volume` mount on the `bob` container didn't take. Run `oc describe pod <agent-pod-name> -n jenkins-andy-test` and confirm the `volumeMounts` under `bob` matches the other two containers. If the volume is mounted but empty, `defaultContainer` isn't writing to `/workspace` — the test pipeline sets `defaultContainer 'build-tools'`, so confirm it's present.
- **Bob authentication error (`401` / `API key not found`).** `BOBSHELL_API_KEY` isn't reaching the container. Run `oc describe pod <agent-pod-name> -n jenkins-andy-test` and on the `bob` container confirm the env lists `BOBSHELL_API_KEY` from `bob-cli-credentials.BOBSHELL_API_KEY`.
- **`ImagePullBackOff` on the `bob` container.** Usually means the pod's ServiceAccount can't pull from `jenkins-andy-test`. For agent pods running in `jenkins-andy-test`, the `system:image-puller` grant in step 12 covers it. If the pod lands in a different namespace (e.g., a user-dev namespace), ensure that namespace's `default` SA has image-puller on `jenkins-andy-test` — step 14's loop already does this for `user1-andy-dev` and `user2-andy-dev`.
- **Pod stays `Pending`.** Run `oc describe pod <agent-pod-name> -n jenkins-andy-test` and `oc describe quota -n jenkins-andy-test`. The Helm values file doesn't set a namespace quota, so this is usually a scheduling issue (node selectors, SCC mismatch) rather than capacity.
- **Permission denied writing `.bob/`.** The `bob` container is running under a UID outside group 0, or `/workspace` wasn't mounted with group-writable perms. `oc rsh -n jenkins-andy-test -c bob <agent-pod-name>` → `id` and `ls -la /workspace`. Our Dockerfile's `chgrp -R 0 /workspace && chmod -R g=u /workspace` should cover this; if the dirs are owned by UID 0 with group 0 and no group-write, the image didn't build with that RUN step — rebuild.
- **Podman push fails with TLS error.** OpenShift's registry uses a self-signed cert exposed via the route; `--tls-verify=false` on both `login` and `push` is the expected workaround for dev / dry-run use.
