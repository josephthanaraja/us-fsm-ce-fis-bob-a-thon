# Workshop Jenkins Kit

Reusable deployment for a workshop-style Jenkins:

- **No OpenShift credentials required from participants** — Jenkins uses its own user database, not OAuth
- **Pre-created accounts** — `workshop-admin` plus `user1 … userN` with predictable passwords
- **Matrix-based authorization** — participants can read / build / create / configure their own jobs; admin has everything
- **All code, no UI clicks** — deploy with one script, tear down with another

This kit is intentionally OpenShift-specific. It uses the `jenkins-persistent` template shipped with OpenShift.

---

## Files

| File | Role |
|------|------|
| `jenkins-init.groovy` | Runs at Jenkins startup (or via Script Console). Creates users, switches Security Realm to local DB, applies matrix auth. Idempotent. |
| `setup.sh` | One-shot deploy: provisions Jenkins with OAuth disabled, wires the init script in as a ConfigMap, injects the admin password from a Secret. |
| `teardown.sh` | Removes Jenkins + workshop-specific Secret/ConfigMap. Leaves the project. |

---

## Usage

### Fresh deploy

```bash
# From any OpenShift project you have edit/admin on
oc project my-workshop-namespace

# Pick an admin password — do NOT commit this
export WORKSHOP_ADMIN_PW='pick-a-strong-one'

# Optional: change participant count (default 20)
export USER_COUNT=20

# Run
./setup.sh
```

Output ends with the Jenkins URL and the credential pattern. Hand out `userN` / `bobathon-N` to participants.

### Teardown

```bash
./teardown.sh
```

Leaves the project so you can redeploy into it without re-creating the namespace.

### Apply to an existing Jenkins (no redeploy)

If you already have Jenkins running and want to add workshop users without redeploying:

1. Open Jenkins → **Manage Jenkins → Script Console**
2. Set the env vars in the Jenkins container first (below), then paste the contents of `jenkins-init.groovy` into the console
3. Click **Run**

To set env vars on an existing Jenkins:

```bash
oc create secret generic jenkins-workshop-admin \
    --from-literal=WORKSHOP_ADMIN_PW='your-password'
oc set env dc/jenkins --from=secret/jenkins-workshop-admin
oc set env dc/jenkins WORKSHOP_USER_COUNT=20 ENABLE_OAUTH=false
oc rollout restart dc/jenkins
```

Then run the script via the Script Console. Current OAuth session will be invalidated; log back in as `workshop-admin` with your password.

---

## Reusing this kit for a different workshop

Things you'll probably want to tweak:

| What | Where |
|------|-------|
| Participant password pattern | `jenkins-init.groovy`, line with `"bobathon-${i}"` |
| Number of participants | `USER_COUNT` env var to `setup.sh` (no code change needed) |
| Authorization permissions | `jenkins-init.groovy`, the `strategy.add(...)` block near the bottom |
| Jenkins memory / PVC size | `MEMORY_LIMIT` / `VOLUME_CAPACITY` env vars to `setup.sh` |

If your participants need more / fewer Jenkins permissions (e.g. can't configure jobs, can only build), edit the matrix in `jenkins-init.groovy`. The available permission constants are in the [Jenkins model API](https://javadoc.jenkins.io/hudson/model/Item.html).

---

## Requirements and assumptions

- OpenShift 4.x cluster with the `jenkins-persistent` template available in the `openshift` namespace (check with `oc get template jenkins-persistent -n openshift`)
- Current user has `edit` on the target project
- `matrix-auth` plugin is available in the shipped Jenkins image (standard in OpenShift Jenkins)
- The Jenkins image reads `init.groovy.d/*.groovy` at startup (standard for all modern Jenkins)

## Security notes

- `WORKSHOP_ADMIN_PW` is injected from a Secret — never commit it
- Participant passwords follow a predictable pattern (`bobathon-N`) — fine for a time-boxed workshop, **not** for anything that persists. Change the pattern in the script if you need stronger isolation.
- Jenkins route is public (HTTP-reachable); anyone with the URL sees the login page. That's by design — you want participants to reach it without a VPN.
