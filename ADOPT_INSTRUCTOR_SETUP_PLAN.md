# Adopt Instructor Setup — Plan

> **Status:** The `setup/` toolchain is validated end-to-end. Dry run on `jenkins-andy-test` proved Helm deploy, per-user Jenkins folders with credential isolation, per-user OpenShift namespaces, custom `bob-cli` image, shared workspace across the pipeline pod, and custom-mode loading from a checked-out branch all work. See `DRY_RUN_PLAN.md` for the exact path taken and `CHANGES_NEEDED.md` for every local deviation from the coworker's docs. **This plan is the work remaining** to bake those deviations into `setup/` and clean up the repo.

**Branch:** `adopt-instructor-setup`.

**Commit style:** group related changes into functionally-scoped commits. A commit should represent one logical concern — it can span multiple files if they share that concern, and it can touch part of a file if other concerns in that file belong in a different commit. Don't split for the sake of splitting. After each commit, stop and wait for explicit "committed" before the next one. Don't amend, don't force-push.

---

## 1. Work sequence

Three phases. Within each phase, commits are ordered so `main` stays coherent at every point.

---

### Phase 1 — reconcile `setup/` with dry-run findings

Apply the fixes from `CHANGES_NEEDED.md` so a fresh instructor can follow `INSTRUCTOR_SETUP_TZ.md` top-to-bottom without any local workarounds.

| # | Commit | Files touched | CHANGES_NEEDED items |
|---|---|---|---|
| A | **Configure the Kubernetes cloud declaratively** | `setup/assets/template-jenkins-values_v2.yaml` | #5 |
| B | **Fix per-folder matrix auth — grant VIEW, remove DELETE** | `setup/INSTRUCTOR_SETUP_TZ.md` §3.1.7 Groovy block | #6, #9 |
| C | **Document adding a per-user GitHub PAT** | `setup/INSTRUCTOR_SETUP_TZ.md` (new §3.4) | #7 |
| D | **Reconcile Bob image build + registry push + secret** | `setup/INSTRUCTOR_SETUP_TZ.md` §1.2, §1.3, §1.3.1, §5.1, §5.2, troubleshooting, rotate-key snippet | #1, #2, #3, #4 |

Details for each commit follow below. Each includes what we observed during the dry run, the proposed change, and why — intended to be readable by whoever originally wrote `setup/`.

**Verify before moving to Phase 2:** re-run `DRY_RUN_PLAN.md` against a fresh namespace (e.g., `jenkins-andy-test-2`). Every "deliberate deviation" at the top of `DRY_RUN_PLAN.md` should now be unnecessary. If any are still needed, Phase 1 isn't done.

---

#### Commit A — Configure the Kubernetes cloud declaratively

**File:** `setup/assets/template-jenkins-values_v2.yaml`

**What we observed.** The first pipeline run during the dry run failed with `ERROR: No Kubernetes cloud was found.` Jenkins has the Kubernetes plugin installed, but no cloud is configured. The values file currently has `JCasC.defaultConfig: false` and `configScripts: {}` — both empty — so the chart's default cloud config is skipped and nothing replaces it. During the dry run we worked around this by pasting a Groovy `KubernetesCloud` setup into the Script Console as admin.

**Proposed change.** Add an explicit `configScripts.kubernetes-cloud` block to the JCasC section:

```yaml
controller:
  JCasC:
    enabled: true
    overwriteConfiguration: true
    defaultConfig: false
    configScripts:
      kubernetes-cloud: |
        jenkins:
          clouds:
            - kubernetes:
                name: "kubernetes"
                namespace: "{{ .Release.Namespace }}"
                jenkinsUrl: "http://jenkins.{{ .Release.Namespace }}.svc.cluster.local:8080"
                jenkinsTunnel: "jenkins-agent.{{ .Release.Namespace }}.svc.cluster.local:50000"
                containerCapStr: "10"
```

**Why declarative rather than a documented Groovy step.** The chart applies this at `helm install` time, so Jenkins comes up with the cloud already configured — the instructor never needs to paste Groovy for this. `{{ .Release.Namespace }}` is Go-template syntax that the Jenkins chart evaluates via its own `tpl` helper, so the values file stays namespace-agnostic and works in whatever namespace the instructor installs into.

---

#### Commit B — Fix per-folder matrix auth (add VIEW, remove DELETE)

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` §3.1.7 step 4 (the per-folder matrix auth Groovy block).

**What we observed — issue 1, Credentials link invisible.** After running the current matrix-auth Groovy, logged in as `user1`, the **Credentials** link did not appear in the `user1` folder's left sidebar. Without it, a participant has no UI path to add their own GitHub PAT. The block grants `CredentialsProvider.CREATE/UPDATE/DELETE/MANAGE_DOMAINS` but not `CredentialsProvider.VIEW`. On current Jenkins + Credentials plugin versions, the sidebar entry requires `VIEW` explicitly even if write permissions are granted.

**What we observed — issue 2, `Item.DELETE` lets users delete their own folder.** The block grants `Item.DELETE` per user. That permission is attached to the user's folder and applies to the folder itself — `user1` can click **Delete Folder** in the sidebar and wipe their own workspace mid-lab. A participant footgun.

**Proposed change.** Two line-level edits to the Groovy block:

```groovy
// ADD one line:
prop.add(com.cloudbees.plugins.credentials.CredentialsProvider.VIEW, username)

// REMOVE this line:
prop.add(Item.DELETE, username)
```

Keep `Run.DELETE` — that's a separate permission scoped to deleting individual build-history entries, not items. Useful for participants to clean up their own build list.

**Tradeoff note.** After this change, participants also can't delete individual pipeline jobs they created. Admin has to delete on request. For a time-boxed workshop that's acceptable; `Item.CONFIGURE` still lets participants rename or reconfigure, and admin-only deletion is the safer default for a multi-user setup.

---

#### Commit C — Document adding a per-user GitHub PAT

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` (new section after matrix auth, e.g., §3.4).

**What we observed.** The existing doc ends at matrix auth (§3.1.7) and proceeds to cluster permissions (§3.2) — there's no documented flow for how a workshop participant adds their own GitHub PAT. During the dry run, the first attempt (via the top-right username → **Credentials** link) landed the PAT in the user-personal credential store. That store is scoped to the user identity but does not surface to pipeline jobs, so the credential was unselectable when configuring the pipeline. The problem only became obvious when the Credentials dropdown was empty at pipeline-config time.

**Root cause.** Jenkins has three credential store types:

- **System store** (Jenkins root) — visible to all jobs; requires admin to write. Matrix auth denies root write to participants (correctly).
- **Folder store** — visible to jobs inside the folder. Matrix auth grants `userN` write access to `userN`'s folder store.
- **User-personal store** — scoped to the user identity, visible only in system-level contexts, **not** to pipeline jobs running on an agent.

Only the folder store makes credentials visible in the pipeline Credentials dropdown. The UI exposes three entry points labeled similarly, and the most visually prominent one (top-right username → Credentials) leads to the user-personal store.

**Proposed change.** Add a section with explicit navigation:

1. From the Jenkins homepage, click the `userN` folder.
2. In the folder's left sidebar, click **Credentials**.
3. Under "Stores scoped to userN", click **(global)**.
4. Click **Add Credentials**.
5. Kind: `Username with password`. Scope: `Global`. Username: GitHub username. Password: a GitHub PAT with `repo` scope. ID: `userN-github-pat`.
6. Click **Create**.

Include a brief note clarifying that **"Scope: Global"** in this dialog refers to which URLs the credential can auto-match against — not who can see the credential. That naming is a common source of confusion, and the isolation guarantee comes from the store picked in step 3, not the scope setting.

---

#### Commit D — Reconcile Bob image build + registry push + secret

**Files:** `setup/INSTRUCTOR_SETUP_TZ.md` — §1.2 (namespace diagram), §1.3 + §1.3.1 (per-build pod table + credential flow), §5.1 (Bob image build and push), §5.2 (Bob API key secret), troubleshooting table entry, rotate-key snippet.

Four related issues across §5.1 and §5.2 that collectively tell one story — "getting the Bob image into the cluster and authenticated" — and splitting them would leave the doc in an inconsistent state (e.g., new secret name referenced by §1.3 but old name in §5.2). Bundled into one commit for that reason.

**Issue 1 — secret/env naming doesn't match our Bob CLI binary.** The doc currently uses:

- Secret name: `bob-api-key`
- Secret key: `api-key`
- Env var injected into the `bob` container: `BOB_API_KEY`

Our shipping Bob Shell CLI binary reads `BOBSHELL_API_KEY` from env. Under the current names, the secret mounts correctly but Bob can't find its API key and authentication fails. During the dry run we created the secret with the CLI's expected names as a local deviation.

*Proposed change:* use the names the CLI actually reads — secret `bob-cli-credentials` with key `BOBSHELL_API_KEY` injected as env `BOBSHELL_API_KEY`. Affects §1.2 namespace diagram, §1.3 pod container table, §1.3.1 credential flow diagram, §5.2 `oc create secret` command and the `oc create role` resource-name immediately after, the troubleshooting table row about `BOB_API_KEY`, and the rotate-key snippet at the bottom.

**Issue 2 — §5.1 has no Dockerfile build step.** The section starts with "Log into the OpenShift internal registry, tag and push `bob-cli:latest`" but doesn't describe where `bob-cli:latest` comes from. The original Dockerfile lived on the `instructor-setup` branch and wasn't carried through the merge into `main`. A fresh instructor has nothing to tag.

*Proposed change:* add a build step at the start of §5.1 referencing the Dockerfile we kept:

```bash
cd k8s/openshift/bob-cli-sidecar
podman build -t bob-cli:latest .
```

**Issue 3 — in-cluster registry URL is unreachable from the instructor's laptop.** §5.1's `podman login/tag/push` commands use `image-registry.openshift-image-registry.svc:5000`. That hostname is an in-cluster Service DNS entry — it resolves only from inside the cluster. From a laptop on a TechZone cluster, DNS resolution fails. The existing parenthetical ("*you may have to get the image registry route*") flags the issue without documenting the fix.

*Proposed change:* add a step to enable the registry's default route, then capture the external hostname and use it for login/tag/push:

```bash
oc patch configs.imageregistry.operator.openshift.io/cluster \
  --type merge -p '{"spec":{"defaultRoute":true}}'

REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')

podman login -u unused -p "$(oc whoami -t)" --tls-verify=false "$REGISTRY"
podman tag bob-cli:latest "$REGISTRY/<namespace>/bob-cli:latest"
podman push --tls-verify=false "$REGISTRY/<namespace>/bob-cli:latest"
```

OpenShift exposes the registry route with a self-signed cert, so `--tls-verify=false` on login and push is the standard workaround for instructor-laptop use.

**Issue 4 — `podman login -u $(oc whoami)` fails on `kube:admin`.** The current command is `podman login -u $(oc whoami) -p $(oc whoami -t) ...`. When the instructor is authenticated as `kube:admin` (the default bootstrap identity on a fresh TechZone cluster), `oc whoami` returns the string `kube:admin`. The colon makes podman parse it as `user:password` format and reject the login with `invalid username/password`.

*Proposed change:* use a literal dummy username. The OpenShift registry's auth path doesn't validate the username — only the bearer token on `-p` matters:

```bash
podman login -u unused -p "$(oc whoami -t)" --tls-verify=false "$REGISTRY"
```

Any literal works (`any`, `admin`, `unused`); `unused` is self-documenting.

---

### Phase 2 — delete what's been superseded

Only after Phase 1 is verified end-to-end on a fresh namespace.

| # | Commit | What gets deleted |
|---|---|---|
| E | **Remove the old `jenkins-persistent`-template deploy kit** | `k8s/openshift/jenkins-workshop/` (entire dir) + `WORKSHOP_SETUP.md` + update "Starting Points" section in `README.md` to point at `setup/INSTRUCTOR_SETUP_TZ.md` |
| F | **Remove the non-TechZone variant and its tooling** | `setup/INSTRUCTOR_SETUP_NotTZ.md`, `setup/scripts/generate-htpasswd.sh`, `setup/scripts/generate-htpasswd.py`, `setup/scripts/requirements.txt`, `setup/scripts/generate-jenkins-users.py` (v1 JCasC-YAML variant) |
| G | **Remove superseded Helm values templates** | `setup/assets/template-jenkins-values_v1.yaml`, `setup/assets/template-jenkins-values_rhcop.yaml` |
| H | **Remove unused job template** | `setup/assets/job-template.xml` |

### Keep (not deleted in Phase 2)

| File / dir | Reason |
|---|---|
| `setup/INSTRUCTOR_SETUP_TZ.md` | Canonical setup doc |
| `setup/assets/template-jenkins-values_v2.yaml` | Helm values file |
| `setup/assets/jenkins-scc.yaml` | SCC ClusterRoleBinding template |
| `setup/assets/workshop-user-project-quota.yaml` | Per-user quota |
| `setup/scripts/generate-security-setup.py` | Post-install security bootstrap (load-bearing) |
| `setup/scripts/generate-jenkins-users_v2.py` | User creation via Groovy |
| `setup/scripts/create-projects.sh` | Per-user OpenShift namespace provisioning |
| `k8s/openshift/bob-cli-sidecar/Dockerfile` | Our Bob image — source of truth |
| `Jenkinsfile.test` | Smoke test; re-run after each Phase 1 commit to catch regressions |
| `Jenkinsfile`, `Jenkinsfile.lab*solution`, `Jenkinsfile.finalsolution`, `labs/`, `order-service/`, `.bob/`, `README.md` | Workshop content; handled in Phase 3 |
| `k8s/openshift/jenkins-agent/` | Deleted in Phase 3 commit **J** (tied to Jenkinsfile rewrites) |

---

### Phase 3 — migrate Jenkinsfiles + participant docs

Every existing Jenkinsfile references the custom `jenkins-agent` image that's being dropped. Migrate them all to the 3-container pattern from `Jenkinsfile.test`, then delete the custom image. After that, fill in lab content cumulatively.

| # | Commit | Scope |
|---|---|---|
| I | **Migrate all Jenkinsfiles to 3-container pod spec** | Sweep edit across `Jenkinsfile`, `Jenkinsfile.lab1solution`, `Jenkinsfile.lab2solution`, `Jenkinsfile.lab3solution`, `Jenkinsfile.lab4solution`, `Jenkinsfile.finalsolution`. Replace the 2-container pod spec with the 3-container pattern (`build-tools` + `oc-tools` + `bob`, explicit `workspace-volume` + `workingDir` + `HOME=/workspace` on every container). No stage changes. Also settle the namespace inconsistency (`fis-bobathon-test` vs `fis-bobathon` vs `jenkins` — pick one, or parameterize). |
| J | **Drop custom `jenkins-agent` image** | Delete `k8s/openshift/jenkins-agent/`. Safe now — nothing references it after commit I. |
| K | **Rewrite `labs/00_SETUP.md` for the new deploy** | New credential pattern (`userN` / `userNWorkshop2026!`), folder-scoped navigation, credential store guidance. Mirror `DRY_RUN_PLAN.md` step 17. |
| L | **Lab 1 — PR review cumulative** | Add the Lab 1 (PR review) stage to `Jenkinsfile.lab1solution`, `.lab2solution`, `.lab3solution`, `.lab4solution`, `.finalsolution`. Write `labs/LAB1_PR_REVIEW.md`. |
| M | **Lab 2 — unit tests cumulative** | Verify / rebuild Lab 2 stage in `.lab2solution` through `.finalsolution` (currently `.lab2solution` has Lab 2 only; needs to include Lab 1 after commit L). `labs/LAB2_UNIT_TESTING.md` exists — review and adjust if needed. |
| N | **Lab 3 — security scanning cumulative** | Add Lab 3 stage to `.lab3solution`, `.lab4solution`, `.finalsolution`. Write `labs/LAB3_SECURITY_SCANNING.md`. |
| O | **Lab 4 — linting cumulative** | Add Lab 4 stage to `.lab4solution`, `.finalsolution`. Write `labs/LAB4_LINTING.md`. |
| P | **Lab 5 — DCR + Jira** | Add Lab 5 stage to `.finalsolution`. Write `labs/LAB5_DCR_REPORTING.md`. Register the Jira MCP server in `.bob/mcp.json`. |

Commits L–P can be owned by lab leads rather than done all at once; the plan just tracks that they're outstanding.

---

### Phase 4 — retire the planning docs

| # | Commit | What gets deleted |
|---|---|---|
| Q | **Remove planning docs** | `ADOPT_INSTRUCTOR_SETUP_PLAN.md` (this file), `CHANGES_NEEDED.md`, `DRY_RUN_PLAN.md` |

Do this last, once Phase 3 is complete and nothing else references these files.

---

## 2. For the next session

- **Read order:** this file → `CHANGES_NEEDED.md` → `DRY_RUN_PLAN.md` if you need the validation evidence.
- **Trust the cluster over memory.** If a Phase 1 edit references something that doesn't match live state, check `git log` and the cluster before acting.
- **Commit pacing.** One commit per functional concern. Wait for "committed" between commits.
