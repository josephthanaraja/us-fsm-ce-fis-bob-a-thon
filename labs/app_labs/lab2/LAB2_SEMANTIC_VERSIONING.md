# Lab 2: Interactive Semantic Versioning Journey with IBM Bob

## 🎬 Your Decisions Shape the Outcome

Welcome to Lab 2 — an **interactive, choose-your-own-adventure lab** where you own a real production release from start to finish.

You are the **Lead Engineer** responsible for shipping:

> 🚀 `order-service vNext`

Every decision you make will shape the release outcome. You'll face real-world scenarios where versioning decisions have consequences—some lead to smooth releases, others to production incidents.

---

## 📑 Table of Contents

- [🧠 Core Learning Principle](#-core-learning-principle)
- [👥 Your Environment](#-your-environment)
- [📋 Prerequisites](#-prerequisites)
- [🚀 IBM Bob Acceleration Guide](#-ibm-bob-acceleration-guide)
- [🟢 Part 0 — Establish the Baseline](#-part-0--establish-the-baseline)
- [🔵 Part 1 — Safe, Backward-Compatible Change](#-part-1--safe-backward-compatible-change)
- [🟡 Part 2 — Accidental Breaking Change](#-part-2--accidental-breaking-change)
- [🔴 Part 3 — Third-Party Dependency Breaking Change](#-part-3--third-party-dependency-breaking-change)
- [🟣 Part 4 — Release Decision & Communication](#-part-4--release-decision--communication)
- [⚫ Part 5 — Consumer Impact Simulation (Optional)](#-part-5--consumer-impact-simulation-optional)
- [🎓 Lab Summary](#-lab-summary)
- [🔄 Try Again?](#-try-again)
- [🎯 Key Takeaway](#-key-takeaway)

---

## 🧠 Core Learning Principle

> Great engineers don't just make changes.  
> They understand impact, anticipate failures, and use tools like IBM Bob to make safer, faster decisions.

**What Makes This Lab Different:**
- 🔀 **Branching scenarios** - Your choices matter
- 🎮 **Interactive decision points** - You decide the path
- 📊 **Multiple outcomes** - Success, incidents, or learning moments
- 🔄 **Replayability** - Try different paths to see different results
- 🎓 **Learn by doing** - Experience consequences safely

---

## 👥 Your Environment

You are the **Lead Engineer** for the Order Service team at a fast-growing e-commerce company.

**Your Team:**
- 3 downstream consumer teams depend on your service
- Auto-upgrade policy: PATCH and MINOR versions deploy automatically
- MAJOR versions require coordination and migration planning
- You're accountable for production stability

**Your Challenge:**
Balance velocity with safety. Ship features fast, but don't break production.

---

## 📋 Prerequisites

- **IBM Bob in Advanced Mode** (required)
- order-service repository access
- Basic understanding of semantic versioning
- 60-90 minutes to complete

**Start by confirming Bob is in Advanced Mode:**
```text
I'm starting Lab 2: Interactive Semantic Versioning. Please confirm you're in Advanced Mode, or switch to it now.
```

---

## 🚀 IBM Bob Acceleration Guide

This lab demonstrates **where and how IBM Bob accelerates developer workflows** in semantic versioning tasks.

### 🧠 Core Idea

> Bob transforms multi-hour manual engineering tasks into minutes while improving accuracy and reducing risk.

### ⚡ Time Savings by Lab Section

| Task | Manual Time | With Bob | Improvement |
|------|------------|----------|------------|
| **Part 0**: Baseline analysis | 60 min | 2 min | 30× faster |
| **Part 1**: Impact analysis | 30 min | 2 min | 15× faster |
| **Part 2**: Breaking change detection | Often missed | 3 min | Major |
| **Part 3**: Dependency research | 2 hrs | 5 min | 24× faster |
| **Part 4**: Version decision | 20 min | 1 min | 20× faster |
| **Part 5**: Incident analysis | 2 hrs | 5 min | 24× faster |

### 🎯 What Bob Does in Each Part

**Part 0 - Baseline Analysis:**
- Extracts all REST endpoints automatically
- Infers request/response schemas
- Detects implicit behavior contracts
- Lists dependencies and versions
- **Result:** ~95% time reduction, more complete and accurate

**Part 1 - Feature Impact Analysis:**
- Detects API vs model changes
- Identifies behavior modifications
- Recommends correct version bump
- **Result:** 10-15× faster, fewer missed impacts

**Part 2 - Breaking Change Detection:**
- Identifies failing requests post-change
- Detects behavioral breaking changes
- Generates real failure scenarios
- **Result:** Finds issues humans often miss, prevents production incidents

**Part 3 - Dependency Upgrade Analysis:**
- Summarizes breaking changes in dependencies
- Identifies impacted code sections
- Estimates migration effort
- **Result:** Eliminates research overhead

**Part 4 - Version Decision:**
- Classifies breaking/non-breaking changes
- Recommends correct version bump with rationale
- **Result:** Faster and more consistent decisions

**Part 5 - Incident Analysis:**
- Traces failures to specific changes
- Identifies missed signals
- Recommends prevention strategies
- **Result:** Rapid insights from incidents

### 🚀 Final Takeaway

> IBM Bob is not just a helper—it is a **force multiplier** that automates analysis, improves accuracy, and prevents costly mistakes.

---


# 🟢 PART 0 — Establish the Baseline

You cannot safely change what you don't understand.

## 🎯 Goal

Understand your current system before modifying it.

## 📝 The Task

**Prompt to Bob:**
```text
Analyze the order-service and create a baseline report:

1. List all REST endpoints with HTTP methods
2. Document request/response models
3. Identify current version (check pom.xml and git tags)
4. Note any behavioral contracts consumers might rely on
5. List all dependencies and their versions

Save as: baseline-report.md
```

**What to look for:**
- Current version number
- Public API surface
- Implicit behaviors (error handling, validation, etc.)
- Dependency versions


## ⚡ Automation Insight

Without Bob: 45–60 min  
With Bob: ~2 min  
**Improvement:** 30× faster

---

# 🔵 PART 1 — Safe, Backward-Compatible Change

Sarah from Payments requests:
- New endpoint: `GET /api/orders/summary`
- Optional `priority` field on orders

These changes are added to **your release branch**.

---

## 🎯 Goal

Determine the impact of these changes.

## 💭 Before You Start

**Think about these questions:**
1. What version bump does this require? (PATCH/MINOR/MAJOR)
2. Are you confident in your assessment?
3. What could go wrong?

---

## 🎯 DECISION POINT 1: How Will You Analyze This?

**Your Task:** Write a prompt to Bob to implement and analyze these changes.

### 💭 Think About:
- How thorough should your analysis be?
- What could you miss with a quick review?
- What's the right balance of speed vs safety?
- Should you compare with the baseline?
- How do you verify backward compatibility?

### 📝 Prompt Structure Guidance

A good prompt should:
1. **Specify the implementation** - What needs to be added/changed
2. **Request analysis** - Ask Bob to compare before/after
3. **Check compatibility** - Verify existing clients won't break
4. **Categorize changes** - API, model, or behavior changes
5. **Request documentation** - Ask for a report file

### 📋 Suggested Prompt

[View recommended prompt for Part 1](LAB2_RECOMMENDED_PROMPTS.md#part-1-safe-backward-compatible-change)

---

## ✅ Validate Your Decision

**Prompt to Bob:**
```text
Review my Part 1 changes and tell me:
1. What version bump is required? (PATCH/MINOR/MAJOR)
2. Why?
3. What risks did I miss (if any)?
4. Would this pass code review?

Be honest about any shortcuts I took.
```

**Expected Answer:** MINOR version (1.0.0 → 1.1.0)


## ⚡ Automation Insight

Manual: 30 min  
Bob: 2 min  
**Improvement:** 15× faster

---

# 🟡 PART 2 — Accidental Breaking Change

Alex merges validation rules:

```
PENDING → PROCESSING → SHIPPED → DELIVERED
```

Invalid transitions now throw exceptions.

This is in YOUR release branch.

---

## 🎯 Goal

Determine if this is a breaking change.

## 💭 Before You Start

**Think about:**
1. Is this a bug fix (PATCH) or breaking change (MAJOR)?
2. The method signature didn't change - does that matter?
3. What could break for consumers?

---

## 🎯 DECISION POINT 2: Is This Really Just a Bug Fix?

**Your Task:** Write a prompt to Bob to analyze this change.

### 💭 Think About:
- Should you trust the developer's assessment?
- How can you verify if this is breaking?
- What would happen to existing consumers?
- How do you test behavior changes vs code changes?
- What requests might fail that used to succeed?

### 📝 Prompt Structure Guidance

A good prompt should:
1. **Implement the change** - Add the validation logic
2. **Compare behavior** - Before vs after, not just code
3. **Identify impact** - What requests fail now that didn't before
4. **Classify the change** - Bug fix or breaking change?
5. **Simulate consumers** - Test with realistic scenarios
6. **Recommend version** - Based on the analysis

### 📋 Suggested Prompt

[View recommended prompt for Part 2](LAB2_RECOMMENDED_PROMPTS.md#part-2-accidental-breaking-change)

---

## ⚡ ACCELERATED APPROACH: Using Bob Slash Commands

Instead of crafting detailed prompts, you can use Bob's built-in `/review` command for instant breaking change analysis.

### Option A: Quick Breaking Change Check

**Command:**
```bash
/review --breaking-changes
```

**What it does:**
- Automatically detects behavioral changes in your code
- Identifies requests that would fail after the change
- Classifies the change as breaking or non-breaking
- Recommends the correct semantic version bump

**Expected output:**
- Breaking change analysis report
- List of affected API endpoints
- Semantic version recommendation (PATCH/MINOR/MAJOR)
- Risk assessment

**Time savings:** 2-3 minutes vs 10-15 minutes with manual prompts

---

### Option B: Comprehensive Semantic Version Analysis

**Command:**
```bash
/review --semantic-version
```

**What it does:**
- Full code review focused on semantic versioning impact
- Analyzes all changes in your working directory
- Compares behavior before and after
- Generates detailed version recommendation with rationale

**Expected output:**
- Complete semantic versioning analysis
- Breaking vs non-breaking change classification
- Consumer impact assessment
- Recommended version number with justification

**Time savings:** 5 minutes vs 20-30 minutes with manual analysis

---

### 💡 When to Use Each Approach

| Scenario | Recommended Command | Why |
|----------|-------------------|-----|
| Quick validation of a single change | `/review --breaking-changes` | Fast, focused analysis |
| Multiple changes to analyze | `/review --semantic-version` | Comprehensive view |
| Learning prompt engineering | Manual prompts | Educational value |
| Time-constrained situation | Slash commands | Maximum efficiency |

---

### 🎓 Learning Tip

Try both approaches:
1. First, write your own prompt and analyze the change
2. Then run `/review --breaking-changes` to validate your assessment
3. Compare the results - did you catch everything?

This helps you learn what to look for while benefiting from automated validation.


---

## 🔍 The Truth Revealed

**Prompt to Bob:**
```text


1. Is this change breaking? Why or why not?
2. What's the correct version bump?
3. What would happen if we shipped this as PATCH?
4. Simulate the production incident that would occur

Generate: part2-truth-revealed.md
```


## ⚡ Automation Insight

Manual: unreliable (often missed)  
Bob: catches hidden breaking changes  
**Improvement:** Major - prevents incidents

---

# 🔴 PART 3 — Third-Party Dependency Breaking Change

Critical vulnerability in Jackson.

Upgrade is required before release.

---

## 📧 The Alert

**From:** Security Team  
**Subject:** URGENT: Jackson vulnerability CVE-2024-XXXX

> Critical vulnerability in Jackson 2.15.x (used by Spring Boot).
> Upgrade to Jackson 2.17.x required within 48 hours.
> 
> Severity: HIGH
> CVSS Score: 8.1

---

## 🎯 Goal

Upgrade safely without breaking consumers.

## 📝 Assess the Situation

You need to understand the Jackson dependency situation before proceeding. Consider:

1. What version are we currently using?
2. What's the vulnerability?
3. What version do we need to upgrade to?
4. Is this a simple dependency bump or could it break things?

---

## ⚡ Using Bob Slash Commands

Follow this recommended workflow to analyze the Jackson dependency upgrade:

### 🎯 Recommended Workflow

1. **Initial Assessment** (30 seconds):
   ```bash
   /analyze dependencies --security
   ```
   Get immediate visibility into the Jackson vulnerability
   
   **What it does:**
   - Scans all dependencies in pom.xml
   - Identifies known vulnerabilities (CVEs)
   - Reports severity levels and CVSS scores
   - Recommends upgrade paths

2. **Impact Analysis** (2 minutes):
   ```bash
   /analyze jackson-upgrade --breaking-changes
   ```
   Understand what will break and why
   
   **What it does:**
   - Focuses specifically on Jackson upgrade impact
   - Identifies serialization behavior changes
   - Detects null handling differences
   - Recommends semantic version bump

3. **Decision Making** (5 minutes):
   Review the analysis and choose your upgrade strategy:
   - Quick upgrade with MAJOR version bump
   - Compatibility layer with MINOR version bump
   - Phased migration approach

4. **Validation** (2 minutes):
   ```bash
   /review --semantic-version
   ```
   Confirm your version decision is correct

**Total time with slash commands:** ~10 minutes
**Total time with manual approach:** 2-4 hours

---


## ⚡ Automation Insight

Manual: hours of research  
Bob: minutes of analysis  
**Improvement:** 24× faster

---

# 🟣 PART 4 — Release Decision & Communication

You now have ONE release with:

- New endpoint
- New field
- Refactor behavior change
- Dependency upgrade

---

## 🎯 Goal

Generate release artifacts for your version.

---

## 📋 Generate Release Artifacts

**Prompt to Bob:**
```text
Generate release artifacts for version [YOUR_CHOSEN_VERSION]:

1. Release notes (consumer-focused, under 10 bullets)
2. Migration guide (if MAJOR version)
3. Rollback plan
4. Communication plan for downstream teams

Save as:
- part4-release-notes.md
- part4-migration-guide.md (if needed)
- part4-rollback-plan.md
```

## ⚡ Automation Insight

Manual: error-prone  
Bob: instant + consistent  
**Improvement:** 20× faster

---
---

## 📊 Step 4.3: Risk Assessment

Before deploying, have Bob review your decisions and assess the risk.

### ⚡ RECOMMENDED: Use Bob's Review Command

**Command:**
```bash
/review --semantic-version
```

**What it does:**
- Reviews all changes from Parts 1-3 in your working directory
- Analyzes thoroughness of your implementation
- Validates breaking change detection
- Assesses dependency upgrade strategy
- Evaluates final version decision
- Generates comprehensive risk assessment

**Expected output:**
```
Risk Assessment Report
======================

Risk Level: Medium

Breaking Changes Detected:
✓ Status transition validation (Part 2) - MAJOR change
✓ Jackson serialization behavior (Part 3) - MAJOR change

Version Recommendation: 2.0.0 (MAJOR)
Current Version: 1.0.0

Key Risks:
- Auto-upgrade will affect all consumers
- Status validation may break existing workflows
- Jackson changes affect JSON serialization

Decisions That Increased Risk:
- None - all breaking changes properly identified

Decisions That Reduced Risk:
✓ Thorough breaking change analysis in Part 2
✓ Comprehensive dependency impact assessment in Part 3
✓ Correct MAJOR version bump chosen

Overall Readiness: READY FOR PRODUCTION
Recommendation: Proceed with 2.0.0 release with migration guide
```

**Time savings:** 1 minute vs 20 minutes of manual review

---

### Alternative: Manual Prompt Approach

If you prefer to craft your own prompt:

**Prompt to Bob:**
```text
Review all my decisions and prompts from Parts 1-4:

1. Analyze the thoroughness of my analysis approach
2. Evaluate if I caught breaking changes
3. Assess my dependency upgrade strategy
4. Review my final version decision

Then generate a risk assessment:
- Risk Level: Low/Medium/High/Critical
- Key risks identified
- Decisions that increased risk
- Decisions that reduced risk
- Overall readiness for production

Generate: part4-risk-assessment.md
```

---

### 🎯 Why Use `/review` for Risk Assessment?

| Benefit | Description |
|---------|-------------|
| **Comprehensive** | Analyzes all changes across all parts automatically |
| **Consistent** | Same analysis criteria for all students |
| **Fast** | Instant feedback vs 20+ minutes manual review |
| **Accurate** | Catches issues humans often miss |
| **Actionable** | Clear recommendations for next steps |

---

### 💡 Learning Checkpoint

After running `/review --semantic-version`, ask yourself:

1. Did I catch all the breaking changes Bob found?
2. Was my version number choice correct?
3. What risks did I underestimate?
4. What would I do differently next time?

This reflection reinforces learning while benefiting from automated validation.

---

**This assessment will help you understand:**
- How well you analyzed the changes
- What you might have missed
- Whether your version choice is appropriate
- What could go wrong in production

---


# ⚫ PART 5 — Consumer Impact Simulation (Optional)

Your release is deployed.

Now you must understand what happened.

---

## 🎯 Goal

Analyze the outcome of your release.

## 📝 Simulate the Release

**Prompt to Bob:**
```text
Simulate what happens when version [YOUR_VERSION] is released:

1. Do consumers auto-upgrade? (PATCH/MINOR = yes, MAJOR = no)
2. What breaks (if anything)?
3. When is it detected?
4. What's the impact?
5. Create a realistic incident timeline (if applicable)

Generate: part5-outcome-simulation.md
```

---

## 🎯 Possible Outcomes

### 🟢 Perfect Release
```
✅ Version 1.1.0 deployed successfully
✅ All tests pass in consumer environments
✅ No incidents reported
✅ Positive feedback from downstream teams
✅ Feature adoption begins immediately

CONGRATULATIONS! You balanced speed and safety perfectly.
```

---

### 🟡 Minor Issues
```
⚠️  Version 2.0.0 deployed (MAJOR)
⚠️  Some consumers delayed upgrade (expected)
⚠️  Migration took longer than estimated
⚠️  One team found undocumented behavior change
✅ Issues resolved within 1 week
✅ No production incidents

GOOD JOB! You caught the major issues, minor friction expected.
```

---

### 🟠 Production Incident
```
🔥 Version 1.1.0 deployed (should have been 2.0.0)
🔥 Consumers auto-upgraded overnight
🔥 Payment Service refunds start failing at 2:00 AM
🔥 PagerDuty alerts fire
🔥 Emergency rollback at 3:30 AM
🔥 2 hours of downtime
🔥 Post-incident review scheduled

INCIDENT! Your shortcuts caught up with you.
```

**Prompt to Bob:**
```text
Generate a detailed incident report:
1. Timeline of events
2. Root cause analysis
3. Impact assessment (technical and business)
4. Lessons learned
5. Prevention strategies

Save as: part5-incident-report.md
```

---

### 🔴 Major Outage
```
💥 Version 1.1.0 deployed with multiple breaking changes
💥 All 3 consumer teams affected simultaneously
💥 Payment processing down
💥 Order fulfillment blocked
💥 Customer-facing errors
💥 4 hours to identify all issues
💥 6 hours total downtime
💥 Executive escalation
💥 $500K+ revenue impact

CRITICAL FAILURE! Multiple shortcuts compounded.
```

**Prompt to Bob:**
```text
Generate a comprehensive post-mortem:
1. Detailed incident timeline
2. Multiple root causes
3. Blast radius analysis
4. Business impact calculation
5. Process failures that allowed this
6. Comprehensive prevention plan
7. Team communication plan

Save as: part5-major-outage-postmortem.md
```

---

## 🧠 Final Reflection

**Prompt to Bob:**
```text
Help me reflect on this lab experience:

My outcome: [YOUR_OUTCOME]

Create a personalized lessons-learned document:

1. What decisions led to my outcome?
2. What would I do differently?
3. What did I do well?
4. How does semantic versioning build trust?
5. What processes would prevent my mistakes?
6. Key takeaways for my real work

Generate: part5-personal-lessons-learned.md
```

## ⚡ Automation Insight

Manual: 2 hrs  
Bob: 5 min  
**Improvement:** 24× faster

---

# 🎓 Lab Summary

## What You Experienced

This lab demonstrated how **your versioning decisions have real consequences**:

1. **Part 0**: Established baseline understanding
2. **Part 1**: Chose between speed and thoroughness
3. **Part 2**: Detected (or missed) behavioral breaking changes
4. **Part 3**: Balanced security, safety, and speed
5. **Part 4**: Made final version decision
6. **Part 5**: Experienced the consequences

## Key Insights

**Without Proper Analysis:**
- Fast decisions → Production incidents
- Missed breaking changes → Consumer trust erosion
- Shortcut mentality → Technical debt and outages

**With Bob as Your Copilot:**
- Automated change analysis
- Instant consumer impact assessment
- Confident version decisions
- Proactive incident prevention
- Fast AND safe releases

## Files Bob Created

Your journey through this lab with Bob created:
- `baseline-report.md` - Starting point
- `part1-*` - Feature analysis
- `part2-*` - Breaking change detection
- `part3-*` - Dependency analysis
- `part4-*` - Release artifacts
- `part5-*` - Outcome and lessons learned

---

# 🔄 Try Again?

Want to see a different outcome? 

**Replay the lab with different choices:**
- Take the risky path to experience an incident safely
- Take the safe path to see perfect execution
- Mix approaches to understand trade-offs

Each playthrough teaches different lessons!

---

# 🎯 Key Takeaway

> **Semantic versioning is not about numbers.**  
> **It's about trust, predictability, and safety at scale.**

IBM Bob helps you:
- Make confident versioning decisions
- Catch subtle breaking changes
- Ship faster without sacrificing safety
- Build trust with downstream teams

And:

> IBM Bob is your **force multiplier** — not using it is the real risk.

---

**Lab Version:** 2.0 Interactive  
**Last Updated:** 2026-05-13  
**Estimated Time:** 60-90 minutes  
**Replayability:** High - Try different paths!