# Lab 2: Semantic Versioning with IBM Bob
## How Bob Improves Quality of Life for Application Teams

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Who This Lab Is For](#who-this-lab-is-for)
3. [Your Role](#your-role)
4. [Prerequisites](#prerequisites)
5. [Lab Structure](#lab-structure)
6. [Part 1: Establish the Baseline](#part-1--establish-the-baseline)
7. [Part 2: Safe, Backward-Compatible Change (MINOR)](#part-2--safe-backward-compatible-change-minor)
8. [Part 3: Accidental Breaking Change](#part-3--accidental-breaking-change)
9. [Part 4: Third-Party Dependency Breaking Change](#part-4--third-party-dependency-breaking-change)
10. [Part 5: Release Decision & Communication](#part-5--release-decision--communication)
11. [Part 6: Consumer Impact Simulation (Optional)](#part-6--consumer-impact-simulation-optional)
12. [Lab Summary](#lab-summary)
13. [Key Takeaway](#key-takeaway)
14. [Executive / Platform Showcase Framing](#executive--platform-showcase-framing)
15. [Next Steps](#next-steps)
16. [Feedback](#feedback)

---

## Executive Summary

Experienced application developers do not struggle with writing code—they struggle with **managing change safely**.

Every change introduces questions that slow teams down:
- Is this change actually breaking for downstream consumers?
- Who will be impacted, and how?
- Is this dependency upgrade safe?
- Do we really need to ship a major version?

Answering these questions usually requires deep manual code review, tribal knowledge, meetings, and post-release cleanup.

**IBM Bob exists to remove this mental and operational tax.**

This lab demonstrates how Bob acts as an always-on **copilot for the team responsible for this service**, helping the team:
- Detect breaking changes humans frequently miss
- Analyze third-party dependency impact automatically
- Reason about changes from a downstream-consumer perspective
- Recommend correct semantic version increments
- Produce clear, concise release notes and migration guidance

The result:
- Faster release decisions
- Fewer production surprises
- Less cognitive load on senior engineers
- Stronger trust between producer and consumer teams

This lab is **not about teaching semantic versioning rules**.  
It is about **offloading semantic-versioning judgment and change-risk analysis to Bob**, so experienced teams can move faster with confidence.

---

## Who This Lab Is For

This lab is designed for **experienced application development teams** who:
- Are responsible for backend services or APIs
- Maintain shared libraries or internal platforms
- Regularly upgrade third-party dependencies
- Are accountable for production stability and incidents

The lab is fully self-paced and does not require instructor involvement.

---

## Your Role

You are part of the **team responsible for this service**—a shared application component used by multiple downstream teams.

### Organizational Reality
- Downstream teams auto-upgrade PATCH and MINOR releases
- MAJOR releases require coordination and migration
- Production incidents reduce trust and slow adoption

Your responsibility is not just to deliver features—it is to **evolve the service safely while protecting consumers**.

IBM Bob works alongside your team as an **always-on copilot**, continuously analyzing changes and their downstream impact.

---

## Prerequisites

- **Advanced Mode Required**: This lab requires Bob's Advanced Mode for full analysis capabilities
- Git (basic usage)
- Java & Maven
- Access to the order-service repository

## IBM Bob Acceleration Guide

This lab demonstrates **where and how IBM Bob accelerates developer workflows** in semantic versioning tasks.

### 🧠 Core Idea

> Bob transforms multi-hour manual engineering tasks into minutes while improving accuracy and reducing risk.

### ⚡ Time Savings by Lab Section

| Task | Manual Time | With Bob | Improvement |
|------|------------|----------|------------|
| **Part 1**: Establish the Baseline | 60 min | ~2 min* | 30× faster |
| **Part 2**: Safe, Backward-Compatible Change | 30 min | ~2 min* | 15× faster |
| **Part 3**: Accidental Breaking Change | Often missed | ~3 min* | Major |
| **Part 4**: Third-Party Dependency Breaking Change | 2 hrs | ~5 min* | 24× faster |
| **Part 5**: Release Decision & Communication | 20 min | ~1 min* | 20× faster |
| **Part 6**: Consumer Impact Simulation | 2 hrs | ~5 min* | 24× faster |

*Times with Bob are estimates and will vary based on complexity and prompt quality.

### 🚀 Final Takeaway

> IBM Bob is not just a helper—it is a **force multiplier** that automates analysis, improves accuracy, and prevents costly mistakes.

---

## Part 1 — Establish the Baseline

**Goal:** Understand what "stable" means to consumers today.

### Step 1.1: Ensure Advanced Mode

Ensure Bob is in Advanced Mode before starting this lab. Advanced Mode is required for full analysis capabilities.

If Bob is not in Advanced Mode, switch to it now using the mode selector in the Bob interface.

---

### Step 1.2: Create Baseline Report

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

---

### What Bob Did for You
- Identified the effective public contract beyond method signatures
- Highlighted behavioral assumptions consumers rely on
- Established a baseline for comparison

**Quality-of-Life Impact:** No tribal knowledge required. No guessing which behaviors are relied upon.

---

### ✅ Checkpoint: Start New Task

**Before proceeding to Part 2, start a new task with Bob:**

This ensures Bob has a clean context for the next section and prevents context overflow.

**How to start a new task:**
1. Click the "New Task" button in Bob's interface, or
2. Use the keyboard shortcut (if available), or
3. Simply type: "Start a new task for Part 2"

---

## Part 2 — Safe, Backward-Compatible Change (MINOR)

**Scenario:** A feature request that should be low risk.

### Step 2.1: Implement New Features

**Prompt to Bob:**
```text
Implement the following backward-compatible changes to order-service:

1. Add a new endpoint GET /api/orders/summary that returns:
   - Total number of orders
   - Count by status
   - No breaking changes to existing endpoints

2. Add an optional "priority" field to the Order model:
   - Type: String
   - Optional (nullable)
   - Default: null
   - Should not affect existing API consumers

Make these changes and show me the modified files.
```

---

### Step 2.2: Create Custom Slash Command for Change Analysis

**Before creating the command, make your own decision:**

**Your Decision:**
- What version bump do you recommend? (PATCH / MINOR / MAJOR)
- Why?

---

**Now create a reusable slash command using the Bob UI:**

**Steps to create the command:**

1. **Open the Command Builder:**
   - Click the lightning bolt icon (⚡) to the right of the mode selector in Bob's interface

2. **Add the Command:**
   - In the "Workspace Commands" section, enter the name: `analyze-changes`
   - Click the plus (+) button to create the command

3. **Configure the Command:**
   - Bob will open an editor for you to define the command
   - Copy and paste the following complete command definition:

```yaml
name: analyze-changes
description: Analyzes code changes and compares with baseline to determine semantic version impact
version: 1.0.0

prompt: |
  Analyze the changes made to the service and compare with the baseline from Part 1.

  ## Step 1: Categorize Changes
  
  Categorize all changes by:
  - **API changes**: new endpoints, modified endpoints, removed endpoints
  - **Model changes**: new fields, modified fields, removed fields
  - **Behavior changes**: logic modifications, validation changes, error handling changes

  ## Step 2: Determine Impact
  
  For each change, determine:
  - Is it breaking or non-breaking?
  - What version bump does it require? (PATCH/MINOR/MAJOR)
  - Why? (Provide clear rationale based on semantic versioning rules)

  ## Step 3: Verify Backward Compatibility
  
  Verify backward compatibility by:
  1. Simulating an old client that doesn't know about new fields
  2. Confirming that:
     - Old clients can still use existing endpoints without modification
     - New fields are truly optional (nullable, have defaults, or are additive only)
     - No existing behavior changed in a way that breaks consumer expectations
     - No endpoints were removed or had their contracts modified

  ## Step 4: Generate Report
  
  Generate a comprehensive change-analysis.md report that includes:
  
  ### Summary
  - Total number of changes
  - Recommended version bump (PATCH/MINOR/MAJOR)
  - Overall risk assessment (Low/Medium/High)
  
  ### Detailed Analysis
  
  #### API Changes
  - List each API change with:
    - Change type (new/modified/removed)
    - Endpoint path and method
    - Breaking or non-breaking classification
    - Impact description
  
  #### Model Changes
  - List each model change with:
    - Change type (new field/modified field/removed field)
    - Model and field name
    - Breaking or non-breaking classification
    - Impact description
  
  #### Behavior Changes
  - List each behavior change with:
    - Component affected
    - Change description
    - Breaking or non-breaking classification
    - Impact description
  
  ### Backward Compatibility Validation
  - Results of old client simulation
  - Confirmation of endpoint compatibility
  - Confirmation of field optionality
  - Confirmation of behavior stability
  
  ### Recommendation
  - Final version bump recommendation
  - Rationale for the recommendation
  - Any migration steps required (if MAJOR version)
  - Risk mitigation strategies
  
  Save the report as: part1-change-analysis.md

parameters: []

examples:
  - description: Analyze changes after adding new endpoint and optional field
    input: ""
    output: |
      # Change Analysis Report
      
      ## Summary
      - Total Changes: 2
      - Recommended Version: 1.1.0 (MINOR)
      - Risk Assessment: Low
      
      ## Detailed Analysis
      
      ### API Changes
      1. **New Endpoint**: GET /api/orders/summary
         - Type: New
         - Classification: Non-breaking
         - Impact: Adds new capability, existing clients unaffected
      
      ### Model Changes
      1. **New Field**: Order.priority
         - Type: New optional field
         - Classification: Non-breaking
         - Impact: Field is nullable, existing clients can ignore it
      
      ### Behavior Changes
      None detected
      
      ## Backward Compatibility Validation
      ✓ Old clients can use all existing endpoints
      ✓ New fields are optional (nullable)
      ✓ No existing behavior changed
      ✓ No endpoints removed or modified
      
      ## Recommendation
      **Version Bump**: 1.0.0 → 1.1.0 (MINOR)
      
      **Rationale**:
      - New functionality added (new endpoint)
      - New optional field added to model
      - All changes are backward compatible
      - No breaking changes detected
      
      **Migration Required**: None
      
      **Risk Mitigation**: None needed - changes are safe for auto-upgrade

tags:
  - semantic-versioning
  - change-analysis
  - backward-compatibility
  - version-bump

metadata:
  author:
  created:
  category: analysis
```

4. **Save the Command:**
   - Save the command definition
   - The command is now available for use

---

**Test your new command:**

Run your newly created command:

```bash
/analyze-changes
```

**Expected output:**
- Categorized list of all changes (API, Model, Behavior)
- Breaking vs non-breaking classification for each change
- Recommended version bump with rationale
- Backward compatibility validation results
- Generated part1-change-analysis.md report

---

### What Bob Did for You
- Verified backward compatibility across downstream consumers
- Confirmed no hidden behavioral changes
- Recommended a safe MINOR version increment

**Quality-of-Life Impact:** Confident decisions without waiting for downstream validation or extended review cycles.

---

### ✅ Checkpoint: Start New Task

**Before proceeding to Part 3, start a new task with Bob:**

This ensures Bob has a clean context for the next section and prevents context overflow.

**How to start a new task:**
1. Click the "New Task" button in Bob's interface, or
2. Use the keyboard shortcut (if available), or
3. Simply type: "Start a new task for Part 3"

---

## Part 3 — Accidental Breaking Change

**Scenario:** A refactor that appears harmless but isn't.

### Step 3.1: Inject the Breaking Change

**Prompt to Bob:**
```text
Simulate an accidental breaking change in order-service:

Modify the OrderService.updateOrderStatus() method to add strict status transition validation:
- Orders can only transition: PENDING → PROCESSING → SHIPPED → DELIVERED
- Invalid transitions should throw an exception
- This seems like a "bug fix" but it's actually breaking

Make this change and show me the code.
```

---

### Step 3.2: Initial Assessment

**Before analyzing with Bob, answer:**
- Is this change breaking? Why or why not?
- The method signature didn't change - does that matter?
- What version bump would you recommend?

---

### ✅ Checkpoint: Start New Task

**Before proceeding to Step 3.3, start a new task with Bob:**

This ensures Bob has a clean context for the analysis and prevents context overflow.

**How to start a new task:**
1. Click the "New Task" button in Bob's interface, or
2. Use the keyboard shortcut (if available), or
3. Simply type: "Start a new task for Step 3.3"

---

### Step 3.3: Detect the Breaking Change

**Prompt to Bob:**
```text
Analyze the status transition validation change I just made.

Compare behavior before and after:
1. What requests would succeed before but fail now?
2. Are there any API signature changes?
3. Is this a breaking change even though the signature is the same?
4. What version bump is required?

Test this by simulating a consumer that tries to update an order from SHIPPED back to PROCESSING (which might have worked before).

Generate a part3-breaking-analysis.md report.
```

---

### What Bob Did for You
- Flagged behavioral breaking changes invisible at the API level
- Simulated downstream consumer expectations
- Explained why the change requires a MAJOR version

**Quality-of-Life Impact:** Breaking changes caught early—before production incidents or escalations.

---

### ✅ Checkpoint: Start New Task

**Before proceeding to Part 4, start a new task with Bob:**

This ensures Bob has a clean context for the next section and prevents context overflow.

**How to start a new task:**
1. Click the "New Task" button in Bob's interface, or
2. Use the keyboard shortcut (if available), or
3. Simply type: "Start a new task for Part 4"

---

## Part 4 — Third-Party Dependency Breaking Change

**Scenario:** A routine dependency upgrade introduces risk.

### Step 4.1: Analyze Current Dependencies

**Prompt to Bob:**
```text
Analyze the current dependencies in order-service pom.xml:

1. List all direct dependencies and their versions
2. Identify dependencies with known security vulnerabilities
3. Check for available updates
4. Highlight any dependencies that are more than 2 major versions behind

Focus on:
- Spring Boot version
- Jackson (JSON serialization)
- PostgreSQL driver
- Hibernate

Generate a part4-dependency-inventory.md report.
```

---

### Step 4.2: Simulate Dependency Upgrade

**Prompt to Bob:**
```text
Simulate a Jackson library upgrade scenario:

1. Document the current Jackson version (comes with Spring Boot)
2. Explain what would happen if we upgraded Jackson from 2.15.x to 2.17.x
3. Identify potential breaking changes in Jackson 2.17.x:
   - Serialization behavior changes
   - Default value handling
   - Date format changes
   - Null handling changes

Even though our API code doesn't change, explain how this could break consumers.

Create a part4-jackson-upgrade-analysis.md report.
```

---

### Step 4.3: Decide on Release Strategy

**Prompt to Bob:**
```text
Given the Jackson upgrade analysis, recommend a release strategy:

Option 1: Apply Compatibility Workaround
- Keep old serialization behavior
- Add configuration to maintain backward compatibility
- Release as PATCH

Option 2: Expose the Breaking Change
- Accept the new Jackson behavior
- Release as MAJOR version
- Provide migration guide

Option 3: Delay the Upgrade
- Keep current Jackson version
- Wait for consumers to be ready

Analyze trade-offs for each option and recommend the best approach.
```

---

### What Bob Did for You
- Identified the precise dependency responsible
- Explained transitive behavioral impact
- Presented release options with clear trade-offs

**Quality-of-Life Impact:** No manual dependency spelunking. No surprise runtime failures.

---

### ✅ Checkpoint: Start New Task

**Before proceeding to Part 5, start a new task with Bob:**

This ensures Bob has a clean context for the next section and prevents context overflow.

**How to start a new task:**
1. Click the "New Task" button in Bob's interface, or
2. Use the keyboard shortcut (if available), or
3. Simply type: "Start a new task for Part 5"

---

## Part 5 — Release Decision & Communication

**Scenario:** You need to ship without slowing the team down.

### Step 5.1: Determine Version and Generate Release Notes

**Prompt to Bob:**
```text
Review all changes from Parts 2-4:
- Part 2: New endpoint and optional field (MINOR)
- Part 3: Status transition validation (MAJOR)
- Part 4: Jackson upgrade (potentially MAJOR)

1. What is the final version number we should release?
2. Explain your reasoning based on semantic versioning rules.

Then generate concise release notes for this release:
1. Version number
2. Breaking changes (with migration guidance)
3. New features
4. Bug fixes
5. Dependency updates

Keep it under 10 bullet points. Focus on consumer impact.

Save as: part5-release-notes.md
```

---

### Step 5.2: Create Migration Guide

**Prompt to Bob:**
```text
Create a migration guide for consumers upgrading to this version:

1. What changes will break existing code?
2. What code changes are required?
3. Provide before/after examples
4. Estimate migration effort (hours/days)
5. Suggest a rollout strategy

Save as: part5-migration-guide.md
```

---

### What Bob Did for You
- Suggested the correct semantic version increment
- Drafted concise, consumer-focused release notes
- Prepared migration guidance based on actual breakage

**Quality-of-Life Impact:** Clear communication without starting from a blank page.

---

### ✅ Checkpoint: Start New Task

**Before proceeding to Part 6, start a new task with Bob:**

This ensures Bob has a clean context for the next section and prevents context overflow.

**How to start a new task:**
1. Click the "New Task" button in Bob's interface, or
2. Use the keyboard shortcut (if available), or
3. Simply type: "Start a new task for Part 6"

---

## Part 6 — Consumer Impact Simulation (Optional)

**Scenario:** A wrong version decision reaches consumers.

### Step 6.1: Simulate Incorrect Versioning

**Prompt to Bob:**
```text
Simulate what would happen if we released the breaking changes from Part 3 as a MINOR version (1.1.0 instead of 2.0.0):

1. Consumers auto-upgrade (they trust MINOR versions)
2. What breaks in production?
3. What error messages do they see?
4. How long until the issue is detected?
5. What is the blast radius?

Create a part6-incident-simulation.md report.
```

---

### Step 6.2: Analyze the Incident

**Prompt to Bob:**
```text
Analyze the simulated incident:

1. What signals would have caught this earlier?
2. How could semantic versioning have prevented this?
3. What is the cost of this mistake?
   - Engineering time
   - Customer impact
   - Trust damage

Document lessons learned.
```

---

### What Bob Did for You
- Explained how the issue would surface in production
- Identified missed signals earlier in the lifecycle
- Demonstrated how Bob would have prevented the incident

**Quality-of-Life Impact:** Learn safely without real outages or pager events.

---

## Lab Summary

### What You Experienced

In this lab, you experienced how IBM Bob acts as an always-on copilot for release engineering:

1. **Part 1**: Bob established a baseline understanding of your API surface
2. **Part 2**: Bob verified backward compatibility for new features
3. **Part 3**: Bob detected behavioral breaking changes invisible at the API level
4. **Part 4**: Bob analyzed third-party dependency impact
5. **Part 5**: Bob recommended version numbers and drafted release communications
6. **Part 6**: Bob simulated the cost of incorrect versioning decisions

### Key Quality-of-Life Improvements

**Without Bob:**
- Manual code review for every change
- Tribal knowledge about consumer dependencies
- Meetings to discuss version bumps
- Post-release incidents and cleanup
- Slow, cautious release cycles

**With Bob:**
- Automated change analysis
- Instant consumer impact assessment
- Confident version decisions
- Proactive incident prevention
- Fast, safe release cycles

---

## Key Takeaway

Semantic versioning is not about version numbers.
It is about **predictability, safety, and trust at scale**.

IBM Bob helps the **team responsible for this service**:
- Spend less time reasoning about release risk
- Catch subtle breakage earlier
- Ship faster with confidence
- Protect downstream teams automatically

---

## Executive / Platform Showcase Framing

**IBM Bob acts as an always-on copilot for teams responsible for critical services**, continuously analyzing changes, dependency upgrades, and consumer impact—reducing release risk without adding process or friction.

**Business Value Demonstrated:**
- Fewer production incidents
- Faster and safer release cycles
- Reduced cognitive load on senior engineers
- Scalable governance without added meetings or approval layers

**One-line executive summary:**

> IBM Bob enables application teams to move faster by automatically handling the hardest parts of change analysis and semantic versioning decisions.

---

## Next Steps

After completing this lab, consider:

1. **Apply to Your Service**: Use Bob to analyze your next release
2. **Automate in CI/CD**: Integrate Bob's analysis into your pipeline
3. **Share with Team**: Demonstrate Bob's value to your team
4. **Expand Usage**: Apply Bob to dependency upgrades, security patches, and more

---

## Feedback

We value your feedback on this lab. Please share:
- What worked well?
- What could be improved?
- How will you use Bob in your daily work?

Contact: [Your feedback channel]

---

**Lab Version:** 2.3  
**Last Updated:** 2026-05-05  
**Estimated Time:** 60-90 minutes