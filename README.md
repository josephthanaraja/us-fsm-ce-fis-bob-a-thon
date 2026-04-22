# FIS Bob-a-thon Workshop

Hands-on workshop that teaches participants to integrate [IBM Bob](https://bob.ibm.com) into a Jenkins CI pipeline across 5 progressive labs. Each lab adds one stage to a Jenkinsfile participants are building up.

## The Five Labs

1. **PR / Git Diff Review** — Bob as a senior developer looking over a diff, calling out risks and summary.
2. **Unit Testing** — generate Java unit tests with Bob, run them, add a pipeline test stage, Bob diagnoses failures.
3. **Security Scanning** — run a security scan in the IDE, add a pipeline stage, Bob analyzes vulnerabilities.
4. **Linting** — run a linter in the IDE, add a pipeline stage, Bob analyzes findings and posts a PR comment.
5. **DCR & Reporting** — add a Deployment Change Request stage; Bob pushes the report to Jira via MCP.

Lab docs live in [`labs/`](labs/). Each lab is a single markdown file (`LAB1_PR_REVIEW.md`, etc.).

## Starting Points

- **Instructors / admins** setting up the workshop → [WORKSHOP_SETUP.md](WORKSHOP_SETUP.md)
- **Workshop participants** → ask your instructor for your Jenkins credentials and assigned branch, then open `labs/LAB1_*.md`
- **Lab contributors** building a new lab → [`labs/README.md`](labs/README.md)

## Pipeline Scaffolding

- **`Jenkinsfile`** — base pipeline (pod spec + Checkout stage, no Bob calls yet). Participants build on this.
- **`Jenkinsfile.lab<N>solution`** — reference state after Lab N. Use to catch up if you fall behind.
- **`Jenkinsfile.finalsolution`** — complete end-state with all 5 labs integrated.

## Repository Layout

```
.bob/custom_modes.yaml        Bob custom mode definitions (solution + participant)
.bob/mcp.json                 Bob MCP server registrations (Jira added in Lab 5)
Jenkinsfile*                  Base + progressive solution Jenkinsfiles
WORKSHOP_SETUP.md             Instructor setup guide
labs/                         Per-lab participant instructions
order-service/                Spring Boot app — subject matter for all labs
k8s/openshift/
├── bob-cli-sidecar/          Bob CLI container image
├── jenkins-agent/            Jenkins agent container image (tools for pipeline)
└── jenkins-workshop/         Reusable Jenkins deploy kit (no OAuth, pre-made users)
```

## Under the Hood

Each pipeline build spins up a Kubernetes pod with two containers:
- `jenkins-agent` — runs pipeline shell steps (builds, tests, scans, lints)
- `bob-cli` — runs Bob CLI when the pipeline invokes it via `container('bob-cli') { ... }`

Both containers share an `emptyDir` workspace volume at `/workspace`. When the pipeline does `checkout scm`, the repo lands there, and Bob reads `.bob/custom_modes.yaml` directly from it — so any mode on the participant's branch is available at pipeline runtime without rebuilding any image.

## Licensing / Attribution

[Add appropriate attribution here when ready for external use.]
