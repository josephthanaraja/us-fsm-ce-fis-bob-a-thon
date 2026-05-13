# Lab 2: Recommended Prompts Reference

This document contains recommended prompts for each decision point in the Interactive Semantic Versioning lab. Use these as reference if you want to see well-structured prompts, or use them directly if you prefer.


## ⚡ NEW: Slash Command Alternatives

For faster, more consistent analysis, consider using Bob's built-in slash commands instead of crafting prompts:

### Quick Reference

| Lab Section | Slash Command | Alternative Prompt |
|-------------|---------------|-------------------|
| Part 2: Breaking Changes | `/review --breaking-changes` | [Manual prompt](#part-2-accidental-breaking-change) |
| Part 2: Semantic Version | `/review --semantic-version` | [Manual prompt](#part-2-accidental-breaking-change) |
| Part 3: Security Scan | `/analyze dependencies --security` | [Manual prompt](#part-3-third-party-dependency-breaking-change) |
| Part 3: Upgrade Impact | `/analyze jackson-upgrade --breaking-changes` | [Manual prompt](#part-3-third-party-dependency-breaking-change) |
| Part 3: Vulnerabilities | `/analyze pom.xml --vulnerabilities` | [Manual prompt](#part-3-third-party-dependency-breaking-change) |
| Part 4: Risk Assessment | `/review --semantic-version` | [Manual prompt](#version-calculation-part-4) |

### When to Use Slash Commands vs Manual Prompts

**Use Slash Commands When:**
- You want fast, consistent analysis
- You're iterating through multiple scenarios
- You need to validate your manual analysis
- Time is limited (simulating real-world pressure)

**Use Manual Prompts When:**
- You want to practice prompt engineering
- You need custom analysis criteria
- You're learning what to look for
- You want maximum control over the analysis

### 💡 Best Practice: Hybrid Approach

1. Start with manual prompts to learn the concepts
2. Validate with slash commands to catch what you missed
3. Use slash commands for subsequent iterations
4. Reflect on differences between your analysis and Bob's

---

---

## Part 1: Safe, Backward-Compatible Change

### Recommended Prompt

```text
Implement the changes with full analysis:

1. Add GET /api/orders/summary endpoint
2. Add optional "priority" field to Order model
3. Compare with baseline to identify all modifications
4. Categorize changes (API, model, behavior)
5. Verify backward compatibility by simulating old clients
6. Check if new fields are truly optional
7. Confirm no existing behavior changed

Generate: part1-thorough-analysis.md
```

**Why this approach:** Catches issues early, prevents surprises later, minimal time cost for major risk reduction.

[↩️ Return to Part 1 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-1--safe-backward-compatible-change)

---

## Part 2: Accidental Breaking Change

### Recommended Prompt

```text
Analyze Alex's status transition validation change:

1. Implement the validation logic
2. Compare behavior BEFORE and AFTER
3. Identify what requests would succeed before but fail now
4. Determine if this is truly a bug fix or a breaking change
5. Simulate a consumer that tries invalid transitions
6. Recommend the correct version bump

Generate: part2-breaking-change-analysis.md
```

**Why this approach:** Behavioral changes are the hardest to catch. This verifies the claim and prevents production incidents.

[↩️ Return to Part 2 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-2--accidental-breaking-change)

---

## Part 3: Third-Party Dependency Breaking Change

### Recommended Prompt

```text
Upgrade Jackson but analyze the impact first:

1. Document current Jackson version and behavior
2. Upgrade to Jackson 2.17.x
3. Identify behavioral changes in 2.17.x:
   - Serialization differences
   - Null handling changes
   - Date format changes
4. Test with sample requests/responses
5. Determine if this requires MAJOR version bump
6. Recommend mitigation strategies

Generate: part3-jackson-upgrade-analysis.md
```

**Why this approach:** Balances security urgency with safety. You meet the deadline while understanding the impact.

[↩️ Return to Part 3 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-3--third-party-dependency-breaking-change)

---

## Additional Helpful Prompts

### Trade-off Analysis (Part 3)

```text
Compare all three approaches for the Jackson upgrade:

Create a decision matrix with:
1. Risk level (Low/Medium/High)
2. Time to implement
3. Consumer impact
4. Technical debt created
5. Security compliance timeline
6. Recommended approach for our situation

Generate: part3-decision-matrix.md
```

[↩️ Return to Part 3 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-3--third-party-dependency-breaking-change)

### Version Calculation (Part 4)

```text
Review all changes from Parts 1-3:

Part 1: New endpoint + optional field
Part 2: Status transition validation
Part 3: Jackson upgrade

For each change, determine:
1. Is it breaking or non-breaking?
2. What version bump does it require?
3. Why?

Then calculate the FINAL version number based on semantic versioning rules.

Generate: part4-version-calculation.md
```

[↩️ Return to Part 4 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-4--release-decision--communication)

### Release Artifacts (Part 4)

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

[↩️ Return to Part 4 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-4--release-decision--communication)

### Outcome Simulation (Part 5)

```text
Simulate what happens when version [YOUR_VERSION] is released:

Based on my risk score of [YOUR_SCORE] points:

1. Do consumers auto-upgrade? (PATCH/MINOR = yes, MAJOR = no)
2. What breaks (if anything)?
3. When is it detected?
4. What's the impact?
5. Create a realistic incident timeline (if applicable)

Generate: part5-outcome-simulation.md
```

[↩️ Return to Part 5 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-5--consumer-impact-simulation-optional)

### Incident Report (Part 5 - if incident occurs)

```text
Generate a detailed incident report:
1. Timeline of events
2. Root cause analysis
3. Impact assessment (technical and business)
4. Lessons learned
5. Prevention strategies

Save as: part5-incident-report.md
```

[↩️ Return to Part 5 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-5--consumer-impact-simulation-optional)

### Personal Reflection (Part 5)

```text
Help me reflect on this lab experience:

My final risk score: [YOUR_SCORE]
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

[↩️ Return to Part 5 in main lab](LAB2_SEMANTIC_VERSIONING.md#-part-5--consumer-impact-simulation-optional)