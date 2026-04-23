#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
# Workshop Jenkins Teardown
#
# Removes the Jenkins deployment and all workshop-specific state
# (Secret + ConfigMap) from the current OpenShift project.
# Leaves the project itself intact.
#
# Usage:
#   ./teardown.sh
# ═══════════════════════════════════════════════════════════════════

set -euo pipefail

PROJECT=$(oc project -q)
echo "Tearing down workshop Jenkins in project: $PROJECT"

# Jenkins resources created by `oc new-app jenkins-persistent`
oc delete all,pvc,configmap -l app=jenkins --ignore-not-found
oc delete sa jenkins --ignore-not-found
oc delete rolebinding jenkins_edit --ignore-not-found

# Workshop-specific resources
oc delete secret jenkins-workshop-admin --ignore-not-found
oc delete configmap jenkins-workshop-init --ignore-not-found

echo "Workshop Jenkins removed from project: $PROJECT"
