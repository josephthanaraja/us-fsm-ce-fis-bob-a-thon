#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Workshop Jenkins Deployment
#
# Deploys Jenkins into the current OpenShift project with:
#   - OAuth disabled (ENABLE_OAUTH=false)
#   - Local user DB bootstrapped by init.groovy.d script
#   - Admin password injected from a Secret
#   - N participant accounts (user1 .. userN / bobathon-1 .. bobathon-N)
#
# Required env vars:
#   WORKSHOP_ADMIN_PW      admin password to set for workshop-admin
#
# Optional env vars:
#   USER_COUNT             number of participants (default: 20)
#   MEMORY_LIMIT           Jenkins memory cap (default: 2Gi)
#   VOLUME_CAPACITY        PVC size (default: 10Gi)
#
# Usage:
#   export WORKSHOP_ADMIN_PW='pick-a-strong-password'
#   ./setup.sh
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

: "${WORKSHOP_ADMIN_PW:?set WORKSHOP_ADMIN_PW before running}"
: "${USER_COUNT:=20}"
: "${MEMORY_LIMIT:=2Gi}"
: "${VOLUME_CAPACITY:=10Gi}"

PROJECT=$(oc project -q)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "════════════════════════════════════════════════════════"
echo "  Workshop Jenkins Deploy"
echo "════════════════════════════════════════════════════════"
echo "  Project:       $PROJECT"
echo "  User count:    $USER_COUNT"
echo "  Memory limit:  $MEMORY_LIMIT"
echo "  Volume size:   $VOLUME_CAPACITY"
echo "════════════════════════════════════════════════════════"

# ── 1. Deploy Jenkins via template, OAuth disabled ──────────────────
echo "[1/6] Deploying Jenkins (ENABLE_OAUTH=false)"
oc new-app jenkins-persistent \
    --param MEMORY_LIMIT="$MEMORY_LIMIT" \
    --param VOLUME_CAPACITY="$VOLUME_CAPACITY" \
    --param ENABLE_OAUTH=false

# ── 2. Create Secret with admin password ────────────────────────────
echo "[2/6] Creating jenkins-workshop-admin Secret"
oc create secret generic jenkins-workshop-admin \
    --from-literal=WORKSHOP_ADMIN_PW="$WORKSHOP_ADMIN_PW"

# ── 3. Create ConfigMap with the init script ────────────────────────
echo "[3/6] Creating jenkins-workshop-init ConfigMap"
oc create configmap jenkins-workshop-init \
    --from-file=workshop-init.groovy="$SCRIPT_DIR/jenkins-init.groovy"

# ── 4. Mount the init script into Jenkins ───────────────────────────
echo "[4/6] Mounting init script into /var/lib/jenkins/init.groovy.d"
oc set volume dc/jenkins --add \
    --name=workshop-init-scripts \
    --configmap-name=jenkins-workshop-init \
    --mount-path=/var/lib/jenkins/init.groovy.d

# ── 5. Inject admin password + user count as env vars ───────────────
echo "[5/6] Wiring WORKSHOP_ADMIN_PW (from Secret) and WORKSHOP_USER_COUNT"
oc set env dc/jenkins --from=secret/jenkins-workshop-admin
oc set env dc/jenkins WORKSHOP_USER_COUNT="$USER_COUNT"

# ── 6. Wait for rollout ─────────────────────────────────────────────
echo "[6/6] Waiting for Jenkins rollout"
oc rollout status dc/jenkins --timeout=600s

# ── Done ────────────────────────────────────────────────────────────
ROUTE=$(oc get route jenkins -o jsonpath='{.spec.host}')
echo ""
echo "════════════════════════════════════════════════════════"
echo "  Workshop Jenkins Ready"
echo "════════════════════════════════════════════════════════"
echo "  URL:          https://$ROUTE"
echo "  Admin:        workshop-admin / (password you set)"
echo "  Participants: user1 .. user${USER_COUNT}"
echo "                bobathon-1 .. bobathon-${USER_COUNT}"
echo "════════════════════════════════════════════════════════"
