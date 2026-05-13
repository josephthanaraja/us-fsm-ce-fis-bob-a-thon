# Lab 2: Semantic Versioning with IBM Bob
## How Bob Improves Quality of Life for Application Teams

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

---

## Lab Structure

This quick lab consists of 5 parts that can be completed in 60-90 minutes:

- **Part 0**: Establish the Baseline
- **Part 1**: Safe, Backward-Compatible Change (MINOR)
- **Part 2**: Accidental Breaking Change
- **Part 3**: Third-Party Dependency Breaking Change
- **Part 4**: Release Decision & Communication
- **Part 5**: Consumer Impact Simulation (Optional)

---

## Part 0 — Establish the Baseline

**Goal:** Understand what "stable" means to consumers today.

### Step 0.1: Ensure Advanced Mode

**Prompt to Bob:**
```text
I am starting Lab 2.3 on Semantic Versioning. Please confirm you are in Advanced Mode. If not, please switch to Advanced Mode now.
```

**Expected Response:**
Bob should confirm Advanced Mode is active or switch to it.

---

### Step 0.2: Identify the Public API Surface

**Prompt to Bob:**
```text
Analyze the order-service and identify the public API surface:

1. List all REST endpoints with their HTTP methods
2. Identify request/response models
3. Document current behavior and contracts
4. Note any implicit behaviors consumers might rely on

Generate a baseline-api-surface.md report.
```

---

### Step 0.3: Review Current Version

**Prompt to Bob:**
```text
What is the current version of order-service? Check:
1. pom.xml version
2. Any version constants in code
3. Git tags

Document the current version as our baseline.
```

---

### What Bob Did for You
- Identified the effective public contract beyond method signatures
- Highlighted behavioral assumptions consumers rely on
- Established a baseline for comparison

**Quality-of-Life Impact:** No tribal knowledge required. No guessing which behaviors are relied upon.

---

## Part 1 — Safe, Backward-Compatible Change (MINOR)

**Scenario:** A feature request that should be low risk.

### Step 1.1: Implement New Features

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

### Step 1.2: Analyze and Validate Changes

**Before using Bob to analyze, make your own decision:**

**Your Decision (record this):**
- What version bump do you recommend? (PATCH / MINOR / MAJOR)
- Why?

**Now verify with Bob:**

**Prompt to Bob:**
```text
Analyze the changes I just made to order-service. Compare with the baseline from Part 0.

Categorize changes by:
1. API changes (new endpoints, modified endpoints, removed endpoints)
2. Model changes (new fields, modified fields, removed fields)
3. Behavior changes (logic modifications)

For each change, determine:
- Is it breaking or non-breaking?
- What version bump does it require?
- Why?

Then verify backward compatibility:
1. Simulate an old client that doesn't know about the new fields
2. Confirm that:
   - Old clients can still use existing endpoints
   - New fields are truly optional
   - No existing behavior changed

Generate a part1-change-analysis.md report with both the analysis and validation results.
```

---

### What Bob Did for You
- Verified backward compatibility across downstream consumers
- Confirmed no hidden behavioral changes
- Recommended a safe MINOR version increment

**Quality-of-Life Impact:** Confident decisions without waiting for downstream validation or extended review cycles.

---

## Part 2 — Accidental Breaking Change

**Scenario:** A refactor that appears harmless but isn't.

### Step 2.1: Inject the Breaking Change

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

### Step 2.2: Initial Assessment

**Before analyzing with Bob, answer:**
- Is this change breaking? Why or why not?
- The method signature didn't change - does that matter?
- What version bump would you recommend?

**Record your answers in:** `part2-initial-assessment.md`

---

### Step 2.3: Detect the Breaking Change

**Prompt to Bob:**
```text
Analyze the status transition validation change I just made.

Compare behavior before and after:
1. What requests would succeed before but fail now?
2. Are there any API signature changes?
3. Is this a breaking change even though the signature is the same?
4. What version bump is required?

Test this by simulating a consumer that tries to update an order from SHIPPED back to PROCESSING (which might have worked before).

Generate a part2-breaking-analysis.md report.
```

---

### What Bob Did for You
- Flagged behavioral breaking changes invisible at the API level
- Simulated downstream consumer expectations
- Explained why the change requires a MAJOR version

**Quality-of-Life Impact:** Breaking changes caught early—before production incidents or escalations.

---

## Part 3 — Third-Party Dependency Breaking Change

**Scenario:** A routine dependency upgrade introduces risk.

### Step 3.1: Analyze Current Dependencies

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

Generate a part3-dependency-inventory.md report.
```

---

### Step 3.2: Simulate Dependency Upgrade

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

Create a part3-jackson-upgrade-analysis.md report.
```

---

### Step 3.3: Decide on Release Strategy

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

## Part 4 — Release Decision & Communication

**Scenario:** You need to ship without slowing the team down.

### Step 4.1: Determine Version and Generate Release Notes

**Prompt to Bob:**
```text
Review all changes from Parts 1-3:
- Part 1: New endpoint and optional field (MINOR)
- Part 2: Status transition validation (MAJOR)
- Part 3: Jackson upgrade (potentially MAJOR)

1. What is the final version number we should release?
2. Explain your reasoning based on semantic versioning rules.

Then generate concise release notes for this release:
1. Version number
2. Breaking changes (with migration guidance)
3. New features
4. Bug fixes
5. Dependency updates

Keep it under 10 bullet points. Focus on consumer impact.

Save as: part4-release-notes.md
```

---

### Step 4.2: Create Migration Guide

**Prompt to Bob:**
```text
Create a migration guide for consumers upgrading to this version:

1. What changes will break existing code?
2. What code changes are required?
3. Provide before/after examples
4. Estimate migration effort (hours/days)
5. Suggest a rollout strategy

Save as: part4-migration-guide.md
```

---

### What Bob Did for You
- Suggested the correct semantic version increment
- Drafted concise, consumer-focused release notes
- Prepared migration guidance based on actual breakage

**Quality-of-Life Impact:** Clear communication without starting from a blank page.

---

## Part 5 — Consumer Impact Simulation (Optional)

**Scenario:** A wrong version decision reaches consumers.

### Step 5.1: Simulate Incorrect Versioning

**Prompt to Bob:**
```text
Simulate what would happen if we released the breaking changes from Part 2 as a MINOR version (1.1.0 instead of 2.0.0):

1. Consumers auto-upgrade (they trust MINOR versions)
2. What breaks in production?
3. What error messages do they see?
4. How long until the issue is detected?
5. What is the blast radius?

Create a part5-incident-simulation.md report.
```

---

### Step 5.2: Analyze the Incident

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

1. **Part 0**: Bob established a baseline understanding of your API surface
2. **Part 1**: Bob verified backward compatibility for new features
3. **Part 2**: Bob detected behavioral breaking changes invisible at the API level
4. **Part 3**: Bob analyzed third-party dependency impact
5. **Part 4**: Bob recommended version numbers and drafted release communications
6. **Part 5**: Bob simulated the cost of incorrect versioning decisions

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

### Files Created

During this lab, Bob helped you create:
- `baseline-api-surface.md` - Public API documentation
- `part1-change-analysis.md` - Backward compatibility analysis
- `part2-breaking-analysis.md` - Breaking change detection
- `part3-dependency-inventory.md` - Dependency risk assessment
- `part3-jackson-upgrade-analysis.md` - Third-party impact analysis
- `part4-release-notes.md` - Consumer-focused release notes
- `part4-migration-guide.md` - Migration guidance
- `part5-incident-simulation.md` - Cost of incorrect versioning

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