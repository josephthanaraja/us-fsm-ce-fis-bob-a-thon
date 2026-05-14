# FIS Bob-a-thon Workshop

Comprehensive workshop collection demonstrating how to integrate [IBM Bob](https://bob.ibm.com) into development workflows, CI/CD pipelines, and custom automation scenarios.

## Getting Started

**All participants must complete setup first:**

1. **📋 [Prerequisites](PREREQUISITES.md)** — Ensure you have the requirements and initial configuration for the labs.
2. **🎓 [Intro Labs](labs/intro-labs/bob-lab-1-fundamentals.md)** — Complete these first to learn Bob fundamentals (1-2 hours)
3. **Choose your track** based on your role
    - [SRE](labs/sre/) - Series of labs around Bob for the SRE and CI Pipeline.
    - [Applciation Team](labs/app/) - Series of labs around Bob for app teams and development processes.
4. **Optional:** Explore [Handoff Labs](labs/handoff-labs/) for advanced scenarios after completing your track

---

## Workshop Structure

### 🎓 [Intro Labs](labs/intro-labs/) — Bob Fundamentals

**Duration:** 1-2 hours | **Level:** Beginner | **Required for all participants**

Learn Bob's core capabilities through hands-on exercises:

- **Lab 1: Fundamentals** — Master Bob's interface, modes, and approval workflows
- **Lab 2: Advanced Features** — Explore custom modes, MCP servers, and advanced workflows

**Complete these labs first before proceeding to your track.**

---

### 🏗️ [SRE Labs](labs/sre/) — Jenkins Pipeline Integration

**Duration:** 3-5 hours | **Level:** Intermediate to Advanced | **For SRE teams**

Build a complete Jenkins CI/CD pipeline with Bob integration across 5 progressive labs:

1. **PR / Git Diff Review** — Bob analyzes diffs, identifies risks, provides summaries
2. **Unit Testing** — Generate tests, diagnose failures, add pipeline test stages
3. **Security Scanning** — Run security scans, Bob analyzes vulnerabilities
4. **Linting** — Run linters, Bob analyzes findings and posts PR comments
5. **DCR & Reporting** — Generate Deployment Change Requests, push reports to Jira via MCP
6. **Jenkins Pipeline Insights with MCP** — Configure the Jenkins MCP server to interact with your Jenkins instance directly from Bob

**Prerequisites:** Jenkins access, basic pipeline knowledge. Complete [`labs/sre/00_SETUP.md`](labs/sre/00_SETUP.md) before starting Lab 1.

#### Pipeline Scaffolding

The SRE labs use a progressive Jenkinsfile approach where you build up the pipeline stage by stage:

- **`Jenkinsfile`** — Base pipeline with pod spec + Checkout stage (no Bob calls yet). This is your starting point.
- **`Jenkinsfile.lab<N>solution`** — Reference state after Lab N. Use these to catch up if you fall behind.
- **`Jenkinsfile.finalsolution`** — Complete end-state with all 5 labs integrated.

**How it works:** Each pipeline build spins up a Kubernetes pod with multiple side car containers:

- **`jenkins-agent`** — Runs pipeline shell steps (builds, tests, scans, lints)
- **`bob-cli`** — Runs Bob CLI when invoked via `container('bob-cli') { ... }`

The containers share an `emptyDir` workspace volume at `/workspace`. When the pipeline does `checkout scm`, the repo lands there, and Bob reads `.bob/custom_modes.yaml` directly from it — so any mode on your branch is available at pipeline runtime without rebuilding images.

---

### 💻 [App Labs](labs/app_labs/) — Application Development

**Duration:** 1 hour | **Level:** Intermediate | **For application development teams**

Experience Bob as an always-on partner for application development in regulated environments:

1. **Lab 1: Code Review** — PCI compliance analysis, automated reports, remediation guidance
2. **Lab 2: Semantic Versioning** — Breaking change detection, version recommendations, release notes

**Tech Stack:** Spring Boot 3.2, Java 17, PostgreSQL, Maven

---

### 🚀 [Handoff Labs](labs/handoff-labs/) — Additional Scenarios

**Duration:** 30 min - 3+ hours | **Level:** Intermediate to Advanced | **Optional / After completing your track**

Advanced labs for specialized use cases and extending Bob's capabilities:

- **Auto-Recovery & Self-Healing** — Automate error detection and recovery in pipelines
- **OpenShift Deployment** — Automated deployment validation, orchestration, and rollback
- **Bob Mode Builder** — Create custom Bob modes for your workflows (includes 5 examples + templates)
- **Example MCP Servers** — 8 production-ready MCP server implementations

**For:** Teams with specific integration requirements or those wanting to customize Bob for their workflows.

---

## Repository Layout

```text
├── labs/
│   ├── intro-labs/          Bob fundamentals (START HERE)
│   ├── sre/                 Jenkins pipeline integration (5 labs)
│   ├── app/                 Application development workflows
│   └── handoff-labs/        Advanced scenarios and custom modes
│
├── order-service/           Spring Boot demo app (used in SRE & App labs)
│
├── setup/                   Instructor setup guides and scripts
│
├── Jenkinsfile              Base pipeline (SRE labs starting point)
├── .bob/                    Bob configuration (modes, MCP servers)
└── PREREQUISITES.md         System requirements and dependencies
```

---

## Support & Resources

- **Lab-specific questions:** Check the troubleshooting section in each lab
- **Bob documentation:** https://bob.ibm.com/docs
- **Quick references:** Most labs include Quick Start guides for common prompts
