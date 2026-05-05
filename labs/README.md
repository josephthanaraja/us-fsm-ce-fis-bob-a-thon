# Labs

## Table of Contents

- [For Participants](#for-participants)
- [For Lab Contributors](#for-lab-contributors)

---

## For Participants

**Start with [`00_SETUP.md`](00_SETUP.md)** — it walks through creating your working branch and configuring your Jenkins pipeline before Lab 1.

## For Lab Contributors

Each workshop lab is a single markdown file in this directory named `LAB<N>_<TOPIC>.md` (e.g., `LAB1_PR_REVIEW.md`, `LAB2_UNIT_TESTING.md`).

As you build a lab:

1. Add your lab doc here.
2. Flesh out `Jenkinsfile.lab<N>solution` at the repo root with the
   stages your lab teaches.
3. Add your solution mode(s) to `.bob/custom_modes.yaml` with a
   `solution-<slug>` prefix.
4. If your lab needs tools in the Jenkins agent container (maven,
   a scanner, a linter, etc.), update
   `k8s/openshift/jenkins-agent/Dockerfile` and rebuild the image.
5. If your lab affects the `bob-cli-sidecar` image (MCP servers,
   etc.), update that Dockerfile instead.

See the top-level [README](../README.md) for the broader 5-lab structure.
