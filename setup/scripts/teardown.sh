#!/usr/bin/env bash
# ============================================================================
# teardown.sh
# Tears down a Jenkins-on-OpenShift workshop deployment.
#
# Removes (in order, with --ignore-not-found everywhere so it's safe to re-run):
#   1. The Helm release (uses `helm uninstall` first so PVs/PVCs are cleaned up
#      cleanly rather than orphaned by a raw namespace delete)
#   2. Any PVCs the chart left behind (defensive)
#   3. The Jenkins project — takes Route, ImageStream, Secret, SA, Role,
#      RoleBinding, ConfigMap, etc. with it
#   4. All per-user dev namespaces matching userN-dev (any padding)
#   5. The cluster-scoped jenkins-anyuid ClusterRoleBinding
#   6. The workshop-participants group
#
# Does NOT touch:
#   - The image-registry defaultRoute patch (cluster-wide; benign and
#     potentially shared with other tenants)
#   - Anything in openshift-* or kube-* namespaces
#
# Usage:
#   ./teardown.sh                              # tear down the default 'jenkins'
#   JENKINS_NS=jenkins-andy-2 ./teardown.sh    # override the Jenkins namespace
#   HELM_RELEASE=bob-jenkins ./teardown.sh     # override the Helm release name
#
# All variables and their defaults:
#   JENKINS_NS          jenkins
#   HELM_RELEASE        jenkins
#   SCC_BINDING         jenkins-anyuid
#   PARTICIPANTS_GROUP  workshop-participants
# ============================================================================

set -uo pipefail

JENKINS_NS="${JENKINS_NS:-jenkins}"
HELM_RELEASE="${HELM_RELEASE:-jenkins}"
SCC_BINDING="${SCC_BINDING:-jenkins-anyuid}"
PARTICIPANTS_GROUP="${PARTICIPANTS_GROUP:-workshop-participants}"

# ── Sanity checks ──────────────────────────────────────────────────
if ! command -v oc >/dev/null 2>&1; then
  echo "ERROR: 'oc' CLI not installed or not in PATH." >&2
  exit 1
fi

if ! command -v helm >/dev/null 2>&1; then
  echo "ERROR: 'helm' CLI not installed or not in PATH." >&2
  exit 1
fi

if ! oc whoami >/dev/null 2>&1; then
  echo "ERROR: not logged into OpenShift. Run 'oc login' first." >&2
  exit 1
fi

echo "============================================================"
echo "  Workshop Teardown"
echo "============================================================"
echo "  Jenkins namespace:    $JENKINS_NS"
echo "  Helm release:         $HELM_RELEASE"
echo "  SCC ClusterRoleBinding: $SCC_BINDING"
echo "  Participants group:   $PARTICIPANTS_GROUP"
echo "============================================================"
echo ""

# ── 1. Helm uninstall ──────────────────────────────────────────────
echo "[1/6] Uninstalling Helm release '$HELM_RELEASE' from '$JENKINS_NS'..."
if helm status "$HELM_RELEASE" -n "$JENKINS_NS" >/dev/null 2>&1; then
  helm uninstall "$HELM_RELEASE" -n "$JENKINS_NS"
else
  echo "      (no release found, skipping)"
fi

# ── 2. Defensive PVC cleanup ───────────────────────────────────────
echo "[2/6] Deleting any remaining PVCs in '$JENKINS_NS'..."
oc delete pvc --all -n "$JENKINS_NS" --ignore-not-found 2>/dev/null || true

# ── 3. Delete the Jenkins project ──────────────────────────────────
echo "[3/6] Deleting project '$JENKINS_NS'..."
oc delete project "$JENKINS_NS" --wait=false --ignore-not-found

# ── 4. Per-user dev namespaces (handles user1-dev and user01-dev) ──
echo "[4/6] Deleting per-user dev namespaces (userN-dev)..."
USER_PROJECTS=$(oc get projects -o name 2>/dev/null \
                | grep -E '^project/user[0-9]+-dev$' \
                || true)
if [ -n "$USER_PROJECTS" ]; then
  echo "$USER_PROJECTS" | xargs -r oc delete --wait=false --ignore-not-found
else
  echo "      (no userN-dev projects found)"
fi

# ── 5. Cluster-scoped SCC binding ──────────────────────────────────
echo "[5/6] Deleting ClusterRoleBinding '$SCC_BINDING'..."
oc delete clusterrolebinding "$SCC_BINDING" --ignore-not-found

# ── 6. Participants group ──────────────────────────────────────────
echo "[6/6] Deleting group '$PARTICIPANTS_GROUP'..."
oc delete group "$PARTICIPANTS_GROUP" --ignore-not-found

# ── Wait for async namespace termination ───────────────────────────
echo ""
echo "Waiting for projects to terminate (up to 2 minutes)..."
TIMEOUT=120
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
  REMAINING=$(oc get projects -o name 2>/dev/null \
              | grep -E "^project/(${JENKINS_NS}|user[0-9]+-dev)$" \
              || true)
  if [ -z "$REMAINING" ]; then
    echo "All projects fully deleted."
    break
  fi
  COUNT=$(echo "$REMAINING" | wc -l | tr -d ' ')
  echo "      Still terminating: $COUNT project(s)..."
  sleep 3
  ELAPSED=$((ELAPSED + 3))
done

if [ $ELAPSED -ge $TIMEOUT ]; then
  echo ""
  echo "WARNING: some projects didn't terminate within ${TIMEOUT}s."
  echo "Check for stuck finalizers:"
  echo "  oc get project <name> -o yaml | grep -A5 finalizers"
  echo "  oc patch project <name> --type=merge -p '{\"metadata\":{\"finalizers\":null}}'"
fi

# ── Orphaned PV check ──────────────────────────────────────────────
echo ""
echo "Checking for orphaned PVs..."
ORPHANED=$(oc get pv 2>/dev/null | grep -E 'Released|Failed' || true)
if [ -n "$ORPHANED" ]; then
  echo "WARNING: PVs in Released or Failed state — may be tied to the deleted"
  echo "Jenkins PVC and need manual cleanup. Inspect each before deleting:"
  echo "$ORPHANED"
  echo ""
  echo "Delete with: oc delete pv <pv-name>"
else
  echo "No orphaned PVs."
fi

echo ""
echo "============================================================"
echo "  Teardown complete."
echo "============================================================"
