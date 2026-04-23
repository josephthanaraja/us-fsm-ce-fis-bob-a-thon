# Changes Needed — Discovered During Dry Run

Running log of changes `setup/` (docs + assets) needs so a future instructor can follow `INSTRUCTOR_SETUP_TZ.md` top-to-bottom without local workarounds. Each item is a Phase 2 candidate for `ADOPT_INSTRUCTOR_SETUP_PLAN.md`.

Updated as new issues surface during the dry run.

---

## 1. Bob image / secret / env naming

**Files:** `setup/INSTRUCTOR_SETUP_TZ.md` (§1.2, §1.3, §1.3.1, §5.1, §5.2, troubleshooting, rotate-key), `setup/INSTRUCTOR_SETUP_NotTZ.md` (mirror).

**Current:** `bob-api-key` / key `api-key` / env `BOB_API_KEY`.
**Needed:** `bob-cli-credentials` / key `BOBSHELL_API_KEY` / env `BOBSHELL_API_KEY`.
**Why:** the shipped Bob Shell CLI binary reads `BOBSHELL_API_KEY` — auth fails under the original names.

---

## 2. Bob Dockerfile source missing from §5.1

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` §5.1.

**Current:** "Log into the OpenShift internal registry, tag and push `bob-cli:latest`" — no build step, no pointer to a Dockerfile.
**Needed:** Add a `podman build` step referencing `k8s/openshift/bob-cli-sidecar/Dockerfile` (or wherever the canonical Dockerfile ends up post-Phase-2).
**Why:** The original Dockerfile was on the `instructor-setup` branch and got merged out. A fresh instructor has nothing to tag.

---

## 3. External image-registry route setup missing

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` §5.1.

**Current:** Uses the in-cluster DNS `image-registry.openshift-image-registry.svc:5000`. Not reachable from a laptop on TechZone.
**Needed:** Add a step to expose the external route before `podman login`:
```bash
oc patch configs.imageregistry.operator.openshift.io/cluster \
  --type merge -p '{"spec":{"defaultRoute":true}}'
REGISTRY=$(oc get route default-route -n openshift-image-registry -o jsonpath='{.spec.host}')
```
Use `$REGISTRY` in the `podman login/tag/push` commands with `--tls-verify=false`.
**Why:** TechZone clusters don't expose the registry by default; the in-cluster SVC URL doesn't resolve from a laptop.

---

## 4. `podman login -u` breaks on `kube:admin`

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` §5.1.

**Current:** `podman login -u $(oc whoami) -p $(oc whoami -t) ...`.
**Needed:** `podman login -u unused -p $(oc whoami -t) ...` (or any literal).
**Why:** `oc whoami` returns `kube:admin` on TechZone kubeadmin sessions. The colon makes podman parse it as `user:password`. The username isn't validated by the OpenShift registry — only the token matters, so a dummy literal works.

---

## 5. Kubernetes cloud never configured → pipelines fail

**Files:** `setup/assets/template-jenkins-values_v2.yaml` (JCasC block) + `setup/INSTRUCTOR_SETUP_TZ.md` (missing step between §3.2 and §4).

**Current:** Values file sets `JCasC.defaultConfig: false` and `configScripts: {}`. No Kubernetes cloud gets configured, and no step in the doc creates one. First pipeline run fails with `ERROR: No Kubernetes cloud was found.`
**Needed:** Add an explicit `configScripts.kubernetes-cloud` block to `template-jenkins-values_v2.yaml`:

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

The Jenkins chart runs `tpl` on configScripts values, so `{{ .Release.Namespace }}` is resolved at `helm install` time — works in any namespace without editing the file.

**Why:** Without a cloud, `agent { kubernetes { ... } }` blocks can't provision pods — blocks every pipeline in the workshop. Declarative placement avoids adding a post-install Groovy step; the cloud exists the moment Jenkins finishes starting.

---

## 6. Matrix-auth Groovy missing `CredentialsProvider.VIEW`

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` §3.1.7 step 4 (the per-folder matrix-auth Groovy block).

**Current:** Grants `Item.*`, `Run.*`, and `CredentialsProvider.CREATE/UPDATE/DELETE/MANAGE_DOMAINS` per user.
**Needed:** Also grant `com.cloudbees.plugins.credentials.CredentialsProvider.VIEW, username`.
**Why:** Without `VIEW`, the **Credentials** link doesn't render in the user's folder sidebar even though they can create credentials — user has no UI path to add their own PAT.

---

## 7. Ambiguous credential-store navigation

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` (no PAT-add section today; workshop flow requires one).

**Current:** TZ doc doesn't cover "add a GitHub PAT" end-to-end. Natural-looking paths (top-right username → Credentials) land on the user-personal credential store, which is invisible to pipeline jobs. Users hit "credential not in dropdown" at pipeline config time.
**Needed:** Add a PAT-add section with explicit navigation:
1. Jenkins homepage → click the `userN` folder
2. Folder left sidebar → **Credentials**
3. Click **(global)** under "Stores scoped to userN"
4. Add Credentials

Include a note that "Scope: Global" refers to URL domain, not visibility.
**Why:** User-personal credentials don't surface to pipeline jobs. Only folder-store credentials do.

---

## 9. Matrix-auth `Item.DELETE` lets users delete their own folder

**File:** `setup/INSTRUCTOR_SETUP_TZ.md` §3.1.7 step 4 (the per-folder matrix-auth Groovy block).

**Current:** Grants `Item.DELETE` per user. Because the grant is attached to the user's folder, it applies to the folder object itself — `user1` can click **Delete Folder** in the sidebar and wipe their own workspace.
**Needed:** Remove the `prop.add(Item.DELETE, username)` line. Keep `Run.DELETE` (that's a separate permission covering individual build-history entries, which is fine to leave with users).
**Why:** Participant footgun — one stray click deletes their in-progress lab work. Tradeoff: users also can't delete individual pipeline jobs they created, but `CONFIGURE` lets them rename or reconfigure, and admin can delete for them on request. For a time-boxed workshop this tradeoff is the right call.

---

## 8. ~~`template-jenkins-pipeline` pod spec incomplete~~ — resolved by deletion

Resolved: `setup/assets/template-jenkins-pipeline` has been deleted. The 3-container pod-spec pattern with explicit shared volumes is preserved in `Jenkinsfile.test` and will be applied to every other Jenkinsfile during Step 3 of the adoption plan.

---

## Phase 2 checklist (condensed)

Grouped by target file so Phase 2 commits can be file-scoped per `ADOPT_INSTRUCTOR_SETUP_PLAN.md` §3 ("one commit per file").

**`setup/INSTRUCTOR_SETUP_TZ.md`:**
- [ ] #1 Bob naming across §1.2, §1.3, §1.3.1, §5.1, §5.2, troubleshooting, rotate-key
- [ ] #2 Add Dockerfile build step in §5.1
- [ ] #3 Add external-route setup in §5.1 (registry exposure + `$REGISTRY` variable)
- [ ] #4 Swap `-u $(oc whoami)` → `-u unused` in §5.1 podman login
- [ ] #5 Add Kubernetes cloud configuration step (new §3.3) — or delegate to chart default
- [ ] #6 Add `CredentialsProvider.VIEW` to §3.1.7 step 4 Groovy
- [ ] #7 Add explicit "Add GitHub PAT" section with correct store navigation
- [ ] #9 Remove `Item.DELETE` from §3.1.7 step 4 Groovy

**`setup/assets/template-jenkins-values_v2.yaml`:**
- [ ] #5 Resolve cloud config — flip `JCasC.defaultConfig: true` or add an explicit `clouds.kubernetes` block in `configScripts`

**`setup/assets/template-jenkins-pipeline`:** deleted — no edits needed.

**`setup/INSTRUCTOR_SETUP_NotTZ.md`:**
- [ ] Mirror TZ changes — or delete per adoption plan §9.1
