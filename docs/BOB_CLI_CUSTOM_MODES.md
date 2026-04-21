# Bob CLI Custom Modes in Jenkins Sidecar Setup

## Overview

This document explains how Bob CLI running as a sidecar container in a Jenkins pod discovers and uses custom modes defined in your Git repository.

## The Question

**"How does Bob CLI pick up modes from the GitHub URL?"**

The short answer: **It doesn't directly.** Bob CLI picks up modes from the **filesystem**, not from GitHub. The key is understanding how Jenkins and the sidecar share the same workspace.

## Architecture: How the Sidecar Pattern Works

### Pod Structure

```
┌─────────────────────────────────────────────────────────┐
│ Jenkins Pod (Kubernetes)                                │
│                                                         │
│  ┌──────────────────┐      ┌──────────────────┐       │
│  │ jenkins-agent    │      │ bob-cli          │       │
│  │ container        │      │ container        │       │
│  │                  │      │                  │       │
│  │ - Runs pipeline  │      │ - Runs Bob Shell │       │
│  │ - Checks out Git │      │ - Reads files    │       │
│  │ - Executes steps │      │ - Executes cmds  │       │
│  └────────┬─────────┘      └────────┬─────────┘       │
│           │                         │                  │
│           └────────┬────────────────┘                  │
│                    │                                   │
│           ┌────────▼─────────┐                         │
│           │ Shared Volume    │                         │
│           │ /workspace       │                         │
│           │                  │                         │
│           │ ├── .bob/        │                         │
│           │ │   └── custom_  │                         │
│           │ │       modes.   │                         │
│           │ │       yaml     │                         │
│           │ ├── order-       │                         │
│           │ │   service/     │                         │
│           │ └── Jenkinsfile  │                         │
│           └──────────────────┘                         │
└─────────────────────────────────────────────────────────┘
```

## Step-by-Step: How Custom Modes Are Discovered

### 1. Jenkins Checks Out Your Repository

When a Jenkins pipeline runs:

```groovy
stage('Checkout') {
    steps {
        checkout scm  // Clones your Git repo
    }
}
```

This command:
- Clones your repository from GitHub
- Writes all files to `/workspace` (the shared volume)
- Includes `.bob/custom_modes.yaml` from your repo

### 2. Files Are Written to Shared Volume

After checkout, the filesystem looks like:

```
/workspace/
├── .bob/
│   └── custom_modes.yaml    ← Your custom modes file
├── order-service/
├── Jenkinsfile
└── ... (all your repo files)
```

### 3. Bob CLI Reads from the Same Filesystem

When you execute Bob CLI from the Jenkins pipeline:

```groovy
sh 'bob -p "Analyze this code" --chat-mode sre-operator'
```

Bob Shell (running in the sidecar container):
1. Starts up in the `/workspace` directory
2. Looks for configuration files in this order:
   - Command-line arguments
   - Environment variables
   - `/etc/bobshell/custom_modes.yaml` (system-wide)
   - **`.bob/custom_modes.yaml`** ← Finds your file here!
   - `~/.bob/custom_modes.yaml` (user-wide)

### 4. Bob Loads Your Custom Modes

Bob Shell reads `.bob/custom_modes.yaml` and makes your custom modes available:

```yaml
customModes:
  - slug: sre-operator
    name: SRE Operator
    # ... mode definition
```

Now you can use: `bob --chat-mode sre-operator -p "your prompt"`

## Key Kubernetes Configuration

For this to work, your Kubernetes pod spec must mount the same volume to both containers:

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jenkins-agent
    image: jenkins-agent:latest
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace        # ← Same path
    workingDir: /workspace
    
  - name: bob-cli
    image: bob-cli:latest
    volumeMounts:
    - name: workspace-volume
      mountPath: /workspace        # ← Same path
    workingDir: /workspace
    env:
    - name: BOBSHELL_API_KEY
      valueFrom:
        secretKeyRef:
          name: bob-credentials
          key: api-key
    
  volumes:
  - name: workspace-volume
    emptyDir: {}                   # ← Shared empty directory
```

## Why This Works

1. **Shared Volume**: Both containers mount the same `emptyDir` volume
2. **Same Path**: Both mount it at `/workspace`
3. **Same Working Directory**: Both use `/workspace` as their working directory
4. **File Visibility**: Any file written by one container is immediately visible to the other

## Common Misconceptions

### ❌ "Bob CLI connects to GitHub"
**No.** Bob CLI never talks to GitHub. It only reads local files.

### ❌ "Bob CLI needs network access to get modes"
**No.** Everything happens on the local filesystem within the pod.

### ❌ "I need to configure Bob CLI to know my GitHub URL"
**No.** Jenkins handles the Git operations. Bob just reads the resulting files.

## Configuration Priority

Bob Shell uses a layered configuration system. When looking for custom modes, it checks in this order (highest to lowest priority):

| Priority | Source | Location | Scope | Use Case |
|----------|--------|----------|-------|----------|
| 1 | Command-line | `bob --chat-mode custom` | Current session | Override for specific run |
| 2 | Environment | `BOB_MODE=custom` | Current session | CI/CD environment config |
| 3 | System | `/etc/bobshell/custom_modes.yaml` | All users, all projects | Organization-wide modes |
| 4 | **Project** | **`.bob/custom_modes.yaml`** | **Current project** | **Your use case** |
| 5 | User | `~/.bob/custom_modes.yaml` | Current user | Personal preferences |

## Example: Full Pipeline Flow

```groovy
pipeline {
    agent {
        kubernetes {
            yaml """
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: jenkins-agent
    image: jenkins-agent:latest
    volumeMounts:
    - name: workspace
      mountPath: /workspace
  - name: bob-cli
    image: bob-cli:latest
    volumeMounts:
    - name: workspace
      mountPath: /workspace
  volumes:
  - name: workspace
    emptyDir: {}
"""
        }
    }
    
    stages {
        stage('Checkout') {
            steps {
                // Jenkins clones repo to /workspace
                checkout scm
                // Now /workspace/.bob/custom_modes.yaml exists
            }
        }
        
        stage('Bob Analysis') {
            steps {
                container('bob-cli') {
                    // Bob reads /workspace/.bob/custom_modes.yaml
                    sh '''
                        bob --chat-mode sre-operator \
                            -p "Analyze the pipeline for risks"
                    '''
                }
            }
        }
    }
}
```

## Verification Steps

To verify Bob CLI can see your custom modes:

```bash
# 1. Exec into the bob-cli container
kubectl exec -it <pod-name> -c bob-cli -- bash

# 2. Check the workspace
ls -la /workspace/.bob/

# 3. Verify Bob can see the modes
bob --list-modes

# 4. Check Bob's configuration
bob --show-config
```

## Troubleshooting

### Problem: "Mode not found"

**Check:**
1. Is `.bob/custom_modes.yaml` in your Git repo?
2. Did Jenkins successfully check out the code?
3. Are both containers mounting the same volume?
4. Is the YAML syntax correct?

```bash
# Verify file exists
kubectl exec <pod> -c bob-cli -- ls -la /workspace/.bob/

# Validate YAML syntax
kubectl exec <pod> -c bob-cli -- cat /workspace/.bob/custom_modes.yaml
```

### Problem: "Bob CLI can't find files"

**Check:**
1. Working directory: `workingDir: /workspace` in pod spec
2. Volume mount path matches in both containers
3. File permissions (should be readable by all)

## Alternative Approaches

### Option 1: ConfigMap (System-Wide)

If you want modes available to ALL projects:

```bash
# Create ConfigMap from your modes file
kubectl create configmap bob-custom-modes \
  --from-file=custom_modes.yaml=.bob/custom_modes.yaml

# Mount in pod spec
volumes:
- name: bob-modes
  configMap:
    name: bob-custom-modes
    
volumeMounts:
- name: bob-modes
  mountPath: /etc/bobshell/custom_modes.yaml
  subPath: custom_modes.yaml
```

### Option 2: Secret (Sensitive Modes)

For modes with sensitive instructions:

```bash
kubectl create secret generic bob-custom-modes \
  --from-file=custom_modes.yaml=.bob/custom_modes.yaml
```

## Best Practices

1. **Version Control**: Keep `.bob/custom_modes.yaml` in Git
2. **Documentation**: Document each mode's purpose and usage
3. **Testing**: Test modes in a dev environment first
4. **Validation**: Use YAML linters to catch syntax errors
5. **Security**: Don't put secrets in mode definitions (use environment variables)

## References

- [Bob Shell Configuration Docs](https://bob.ibm.com/docs/shell/configuration/configuring)
- [Bob Custom Modes Docs](https://bob.ibm.com/docs/shell/configuration/custom-modes-bobshell)
- [Kubernetes Sidecar Pattern](https://kubernetes.io/docs/concepts/workloads/pods/#how-pods-manage-multiple-containers)

## Summary

**Bob CLI doesn't fetch modes from GitHub.** Instead:

1. Jenkins clones your repo (including `.bob/custom_modes.yaml`)
2. Files are written to a shared volume
3. Bob CLI reads from that same volume
4. Your custom modes are automatically available

The "magic" is the shared filesystem provided by Kubernetes volumes, not any network connection between Bob and GitHub.