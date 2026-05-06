# Lab 1: Code Review with IBM Bob

**Objective:** Learn how to use Bob's Code Reviewer mode to analyze code quality, enforce coding standards (PCI compliance), and generate automated reports for wiki publishing.

**Difficulty:** Beginner
**Prerequisites:**
- order-service code available
- Basic understanding of coding standards

---

## Lab Overview

In this lab, you will:
1. Learn about Bob's Code Reviewer mode and coding standards
2. Perform a comprehensive code review of the order-service
3. Generate automated markdown reports for wiki publishing
4. Apply remediation and verify improvements
5. Create automation scripts for repeatable code reviews

---

## Part 1: Setup and Inject PCI Violations

> **Note:** Stay in **Code mode** (💻 Code) for Part 1.

### Step 1.1: Review PCI Coding Standards

The order-service follows PCI DSS coding standards defined in `pipeline/pci-checkstyle.xml`. Let's review these standards:

**Prompt to Bob:**
```
Read and summarize the coding standards in pipeline/pci-checkstyle.xml. For each rule, explain:
1. What the rule checks for
2. Why it's important for security
3. Provide an example of code that would violate the rule
```

**What Bob does:**
- Reads the PCI checkstyle configuration
- Explains each rule and its security rationale
- Provides examples of code that would violate each rule

**Expected Standards:**
1. **PCI-01**: No System.out/err (prevents PII leakage in logs)
2. **PCI-02**: No hardcoded passwords, tokens, or API keys
3. **PCI-03**: No hardcoded IP addresses
4. **PCI-04**: No printStackTrace() (prevents information disclosure)
5. **PCI-05**: No java.util.Random (use SecureRandom instead)
6. **PCI-06**: No TODO/FIXME/HACK in production code

### Step 1.3: Inject PCI Violations for Practice

Now let's inject some simple PCI violations into the code so you can practice identifying and fixing them with Bob's Code Reviewer mode.

**Prompt to Bob:**
```
Bob, run script labs/app_labs/lab1/inject-pci-violations.sh
```

**What Bob does:**
- Executes the injection script using `execute_command`
- The script creates a backup of OrderService.java
- Injects 6 simple PCI violations (one for each rule)
- Each violation is easy to identify and fix

**Injected Violations:**

1. **PCI-01**: `System.out.println()` on line 108
2. **PCI-02**: Hardcoded API key on line 80
3. **PCI-03**: Hardcoded IP address on line 154
4. **PCI-04**: `printStackTrace()` on line 147
5. **PCI-05**: Weak `Random` on line 141
6. **PCI-06**: Unresolved `TODO` on line 133

**Expected Output:**
```
🔧 PCI Violations Injector
================================
This script will inject 6 simple PCI coding standard violations into OrderService.java
Each violation corresponds to one PCI rule and is easy to fix.

📋 Creating backup...
✅ Backup created: order-service/src/main/java/com/example/orders/service/OrderService.java.backup

💉 Injecting PCI violations...

✅ PCI-01: System.out.println() injected (line 108)
✅ PCI-02: Hardcoded API key injected (line 80)
✅ PCI-03: Hardcoded IP address injected (line 154)
✅ PCI-04: printStackTrace() injected (line 147)
✅ PCI-05: Weak Random injected (line 141)
✅ PCI-06: Unresolved TODO injected (line 133)

✅ Injection Complete
================================
Ready for lab! 🎉
```

**Verify the injection:**
- Open `order-service/src/main/java/com/example/orders/service/OrderService.java`
- You should see the file now has 157 lines (original was 62 lines)
- The violations are now present in the code

Now you're ready to use Code Reviewer mode to detect and fix these violations!

---

## Part 2: Perform Code Review on Order Service

### Step 2.1: Understanding Code Reviewer Mode

Bob has a built-in **Code Reviewer** mode that provides comprehensive code quality analysis. This mode helps you:
- Enforce coding standards and best practices
- Identify code quality issues
- Ensure PCI DSS compliance
- Generate detailed review reports

### Step 2.2: Switch to Code Reviewer Mode

1. **Change Bob's mode:**
   - Click the current mode indicator at the top of Bob
   - Select **"🔍 Code Reviewer"** from the dropdown
   - Bob is now in code review mode

2. **Verify mode switch:**
   - The mode indicator should show: **"🔍 Code Reviewer"**

### Step 2.3: Perform Comprehensive Code Review

Now let's have Bob perform a full code review of the order-service application.

**Prompt to Bob:**
```
Perform a comprehensive code review of the order-service application. Analyze all Java files for:
1. PCI coding standards compliance (based on pipeline/pci-checkstyle.xml)
2. Code quality issues
3. Best practice violations
4. Security concerns
5. Maintainability issues

Generate a detailed code review report.
```

**What Bob does:**
- Scans all Java source files in order-service
- Checks compliance with PCI standards
- Identifies code quality issues
- Analyzes code patterns and practices
- Evaluates maintainability and readability
- Generates comprehensive code review report
- **Populates Bob Findings panel** with all detected issues for easy navigation and tracking

**Expected Analysis Areas:**

**1. Standards Compliance:**
- PCI-01 violations (System.out usage)
- PCI-02 violations (hardcoded credentials)
- PCI-03 violations (hardcoded IPs)
- PCI-04 violations (printStackTrace)
- PCI-05 violations (weak Random)
- PCI-06 violations (TODO/FIXME)

**2. Code Quality:**
- Unused imports
- Dead code
- Code duplication
- Complex methods
- Long parameter lists
- Magic numbers

**3. Best Practices:**
- Exception handling
- Logging practices
- Null safety
- Resource management
- API design
- Error messages

**4. Security:**
- Input validation
- SQL injection risks
- Authentication/authorization
- Data exposure
- Secure communication

**5. Maintainability:**
- Code organization
- Naming conventions
- Documentation
- Test coverage
- Dependency management

### Step 2.4: Review the Generated Report

Bob will generate a comprehensive report with **20 issues identified**, including all 6 PCI violations. Here's what you'll see:

**Executive Summary:**
```markdown
# Comprehensive Code Review Report - Order Service Application

## Executive Summary

Completed comprehensive code review of the order-service application. **20 issues identified** across 5 Java files, including **6 PCI DSS compliance violations** (critical/high severity) and **14 additional code quality, security, and maintainability issues**.

All findings have been added to the **Bob Findings panel** for easy navigation and remediation tracking.
```

**PCI Compliance Status:**
```markdown
## PCI Compliance Status

### ❌ NOT COMPLIANT

**6 PCI DSS violations detected:**

| Rule | Violation | Line | Status |
|------|-----------|------|--------|
| PCI-01 | System.out usage | OrderService.java:46 | ❌ |
| PCI-02 | Hardcoded credentials | OrderService.java:18 | ❌ |
| PCI-03 | Hardcoded IP address | OrderService.java:92 | ❌ |
| PCI-04 | printStackTrace() usage | OrderService.java:85 | ❌ |
| PCI-05 | Weak random generator | OrderService.java:79-80 | ❌ |
| PCI-06 | Unresolved TODO | OrderService.java:71 | ❌ |

**All 6 violations must be resolved before the application can be considered PCI DSS compliant.**
```

**Issue Breakdown:**
```markdown
## Summary by Category

| Category | Critical | High | Medium | Low | Total |
|----------|----------|------|--------|-----|-------|
| **Security** | 1 | 4 | 3 | 0 | **8** |
| **Functionality** | 0 | 0 | 3 | 2 | **5** |
| **Maintainability** | 0 | 0 | 0 | 5 | **5** |
| **Performance** | 0 | 0 | 0 | 1 | **1** |
| **Code Quality** | 0 | 0 | 0 | 1 | **1** |
| **TOTAL** | **1** | **4** | **6** | **9** | **20** |
```

**Key Findings Examples:**

1. **🔴 Critical: PCI-02 Hardcoded API Key** (Line 18)
   - Hardcoded `sk_test_1234567890` in source code
   - Fix: Move to environment variable with `@Value("${api.key}")`

2. **🟠 High: PCI-01 System.out.println()** (Line 46)
   - Logging customer info to stdout
   - Fix: Replace with `logger.info()`

3. **🟠 High: PCI-04 printStackTrace()** (Line 85)
   - Exposes sensitive system information
   - Fix: Use `logger.error()` with exception parameter

4. **🟠 High: PCI-05 Weak Random** (Lines 79-80)
   - Using `java.util.Random` for confirmation codes
   - Fix: Replace with `SecureRandom`

5. **🟡 Medium: PCI-06 Unresolved TODO** (Line 71)
   - TODO comment for order validation logic
   - Fix: Implement validation or remove comment

**Verification:**
```bash
# Check report was created
ls -lh CODE_REVIEW_REPORT.md

# View the full report
cat CODE_REVIEW_REPORT.md

# Count total issues
grep -c "^###" CODE_REVIEW_REPORT.md
```

**What to expect:**
- Detailed description of each issue with code examples
- Recommended fixes with implementation code
- Severity classification (Critical, High, Medium, Low)
- Category tags (Security, Functionality, Maintainability, etc.)
- All issues also appear in Bob Findings panel for easy navigation

---

## Part 3: Generate Automated Code Review Report

> **Note:** Switch to **Documentation Writer mode** (📝 Documentation Writer) for Part 3. This mode specializes in creating well-formatted documentation and wiki reports.

### Step 3.1: Create Wiki-Ready Report Format

Let's format the report for wiki publishing with proper structure and navigation.

**Switch to Documentation Writer mode:**
1. Click the current mode indicator (🔍 Code Reviewer)
2. Select **"📝 Documentation Writer"** from the dropdown
3. Verify the mode shows: **"📝 Documentation Writer"**

> **Why Documentation Writer mode?** This mode is specifically designed for creating professional documentation with proper formatting, structure, and navigation - perfect for wiki reports!

**Prompt to Bob:**
```
Reformat the code review report for wiki publishing. Include:
1. Table of contents with anchor links
2. Summary dashboard with metrics and status indicators
3. Categorized findings with severity badges (🔴 Critical, 🟠 High, 🟡 Medium, 📘 Low)
4. Code snippets showing violations and fixes
5. Remediation examples with step-by-step instructions
6. Export as CODE_REVIEW_WIKI.md
```

**What Bob does:**
- Uses Documentation Writer mode's formatting expertise
- Restructures the report with wiki-friendly markdown
- Adds navigation and table of contents with anchor links
- Includes visual elements (emoji badges, tables, code blocks)
- Provides actionable remediation examples
- Ensures consistent formatting throughout
- Exports as `CODE_REVIEW_WIKI.md`

**Expected Wiki Format:**

```markdown
# Order Service - Code Review Report

## 📊 Dashboard

| Metric | Value | Status |
|--------|-------|--------|
| Files Reviewed | 5 | ✅ |
| Critical Issues | 0 | ✅ |
| High Priority | 2 | ⚠️ |
| Medium Priority | 5 | ℹ️ |
| Low Priority | 3 | ℹ️ |
| Overall Rating | B | 👍 |

## 📑 Table of Contents

1. [Executive Summary](#executive-summary)
2. [PCI Standards Compliance](#pci-standards-compliance)
3. [Critical Issues](#critical-issues)
4. [High Priority Issues](#high-priority-issues)
5. [Medium Priority Issues](#medium-priority-issues)
6. [Low Priority Issues](#low-priority-issues)
7. [Code Quality Metrics](#code-quality-metrics)
8. [Recommendations](#recommendations)

## 🎯 Executive Summary

This code review analyzed the order-service application...

[... rest of formatted content ...]
```

### Step 3.2: Verify Wiki Report

```bash
# Check wiki report was created
ls -lh CODE_REVIEW_WIKI.md

# View the formatted report
cat CODE_REVIEW_WIKI.md
```

---

## Part 4: Fix PCI Violations and Achieve Compliance

> **Note:** You should already be in **Documentation Writer mode** (📝 Documentation Writer) from Part 3. You'll switch to **Code mode** (💻 Code) for Step 4.2.

### Step 4.1: Create PCI Remediation Plan

First, let's create a comprehensive remediation document that Bob can use to fix all violations in one go.

**Prompt to Bob:**
```
Create a PCI remediation plan document called PCI_REMEDIATION_PLAN.md based on the code review report. For each of the 6 PCI violations, document:
1. Violation ID and severity
2. Current code (what needs to be fixed)
3. Required fix with exact code changes
4. File path and line numbers
5. Configuration changes needed (if any)

Format it as a clear, actionable remediation plan that can be executed step-by-step.
```

**What Bob does:**
- Reads CODE_REVIEW_REPORT.md
- Extracts all 6 PCI violations
- Creates detailed remediation plan with code examples
- Organizes by severity (Critical → High → Medium)
- Includes file paths and line numbers
- Documents configuration changes
- Exports as `PCI_REMEDIATION_PLAN.md`

**Expected Remediation Plan Structure:**

The remediation plan will include detailed information for each of the 6 PCI violations with current code, required fixes, and configuration changes.

**Summary Section:**

```markdown
## Summary

**Total Violations:** 6
**Files to Modify:** 2
- `OrderService.java` (6 code changes)
- `application.properties` (2 configuration additions)

**Violations by Severity:**
- Critical: 1 (PCI-02 - Hardcoded API Key)
- High: 4 (PCI-01, PCI-03, PCI-04, PCI-05)
- Medium: 1 (PCI-06 - Unresolved TODO)

**Estimated Time:** 30 minutes
**Testing Required:** Yes - Run full test suite after changes
```

**Verification:**
```bash
# Check the remediation plan was created
ls -lh PCI_REMEDIATION_PLAN.md

# View the plan
cat PCI_REMEDIATION_PLAN.md
```

---

### Step 4.2: Execute All Fixes with One Prompt

Now that we have a detailed remediation plan, Bob can fix all violations in one go!

**Switch to Code mode:**
1. Click mode indicator (📝 Documentation Writer)
2. Select **"💻 Code"**
3. Verify mode shows: **"💻 Code"**

**Prompt to Bob:**
```
Read the PCI_REMEDIATION_PLAN.md file and implement ALL 6 fixes exactly as specified in the remediation plan. Make all code changes to OrderService.java and update application.properties with the required configuration changes. Do not verify the changes - stop after making the fixes.
```

**What Bob does:**
- Reads PCI_REMEDIATION_PLAN.md
- Applies all 6 fixes to OrderService.java:
  1. Removes hardcoded API key, adds @Value injection
  2. Replaces System.out with logger.info()
  3. Replaces printStackTrace() with logger.error()
  4. Replaces Random with SecureRandom
  5. Externalizes hardcoded IP address to configuration
  6. Resolves TODO comment (implements or removes)
- Updates application.properties with new configuration
- Ensures all imports are correct
- Maintains code formatting

**Expected Changes:**

**Files Modified:**
- ✅ `order-service/src/main/java/com/example/orders/service/OrderService.java` (6 fixes)
- ✅ `order-service/src/main/resources/application.properties` (2 additions)

**Summary of Changes:**
```
Modified: OrderService.java
- Line 18: Hardcoded API key → @Value injection
- Line 108: System.out → logger.info()
- Line 133: TODO comment → Implemented or removed
- Line 141-142: Random → SecureRandom
- Line 147: printStackTrace() → logger.error()
- Line 154: Hardcoded IP → @Value injection

Modified: application.properties
+ api.key=${API_KEY}
+ external.service.url=http://external-service:8080/api
```
- Updates to use `secureRandom.nextInt(1000000)`
- Adds proper formatting with `String.format("%06d", confirmationCode)`

**Expected Fix:**
```java
SecureRandom secureRandom = new SecureRandom();
int confirmationCode = secureRandom.nextInt(1000000);
String formattedCode = String.format("%06d", confirmationCode);
return "Order #" + orderId + " - Confirmation: " + formattedCode;
```

---

### Step 4.3: Verify PCI Compliance

After fixing all 6 violations, let's verify we've achieved compliance.

**Switch to Code Reviewer mode:**
1. Click mode indicator (💻 Code)
2. Select **"🔍 Code Reviewer"**
3. Verify mode shows: **"🔍 Code Reviewer"**

**Prompt to Bob:**
```
Re-run the code review on order-service focusing on PCI compliance. Compare with the previous report and show that all 6 PCI violations have been resolved.
```

**What Bob does:**
- Performs new code review in Code Reviewer mode
- Checks all 6 PCI rules
- Compares with previous findings
- Generates compliance comparison report
- **Updates Bob Findings panel** to reflect the current state (resolved issues will be removed/updated)

> **Note:** If Bob Findings still shows old violations after the re-review, you can clear them with this prompt:
> ```
> Clear all findings from the Bob Findings panel and re-scan the order-service to show only current issues.
> ```
>
> Alternatively, you can manually clear them by:
> 1. Opening the Bob Findings panel
> 2. Clicking the "Clear All" or refresh icon
> 3. Re-running the code review prompt to populate with current findings only

**Expected Compliance Report:**

```markdown
# PCI Compliance Verification Report

## ✅ PCI COMPLIANCE ACHIEVED!

All 6 PCI DSS violations have been successfully resolved.

## Compliance Status Comparison

| Rule | Before | After | Status |
|------|--------|-------|--------|
| PCI-01 | ❌ System.out usage | ✅ Using logger | FIXED |
| PCI-02 | ❌ Hardcoded API key | ✅ Environment variable | FIXED |
| PCI-03 | ❌ Hardcoded IP | ✅ Configuration property | FIXED |
| PCI-04 | ❌ printStackTrace() | ✅ Using logger.error() | FIXED |
| PCI-05 | ❌ Weak Random | ✅ Using SecureRandom | FIXED |
| PCI-06 | ❌ Unresolved TODO | ✅ Implemented/Removed | FIXED |

## Overall Improvement

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **PCI Violations** | **6** | **0** | **✅ -6** |
| Critical Issues | 1 | 0 | ✅ -1 |
| High Priority | 4 | 0 | ✅ -4 |
| Medium Priority | 6 | 5 | ✅ -1 |
| **PCI Compliance** | **❌ NOT COMPLIANT** | **✅ COMPLIANT** | **✅ ACHIEVED** |

## Remaining Issues

The following non-PCI issues remain (optional improvements):
- 5 Medium Priority issues (functionality, maintainability)
- 9 Low Priority issues (documentation, code quality)

These can be addressed in future iterations but are not required for PCI compliance.
```

**Verification Commands:**
```bash
# View the new compliance report
cat CODE_REVIEW_COMPLIANCE_REPORT.md

# Run checkstyle to verify PCI compliance
cd order-service && mvn checkstyle:check -Dcheckstyle.config.location=../pipeline/pci-checkstyle.xml

# Expected output: BUILD SUCCESS with 0 violations
```

---

## Part 5: Automate Report Generation (Optional)

### Step 5.1: Create Report Generation Script

Let's create a script to automate the code review process.

**Prompt to Bob:**
```
Create a bash script called generate-code-review-report.sh that automates the code review process. The script should:
1. Run code review analysis
2. Generate standard report
3. Generate wiki-formatted report
4. Create summary metrics
5. Save all outputs with timestamps
```

**What Bob does:**
- Creates `labs/app_labs/lab1/generate-code-review-report.sh`
- Includes all automation steps
- Adds error handling
- Provides usage instructions

**Expected Script Structure:**

```bash
#!/bin/bash
# generate-code-review-report.sh
# Automates code review report generation for order-service

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="code-review-reports"
SERVICE_DIR="order-service"

echo "🔍 Starting automated code review..."

# Create reports directory
mkdir -p "$REPORT_DIR"

# Run code review
echo "📊 Analyzing code..."
# [Bob analysis commands]

# Generate standard report
echo "📝 Generating standard report..."
# [Report generation]

# Generate wiki report
echo "📚 Generating wiki-formatted report..."
# [Wiki report generation]

# Create summary
echo "📈 Creating summary metrics..."
# [Summary generation]

echo "✅ Code review complete!"
echo "📁 Reports saved to: $REPORT_DIR/"
```

### Step 5.2: Test the Automation Script

```bash
# Make script executable
chmod +x labs/app_labs/lab1/generate-code-review-report.sh

# Run the script
./labs/app_labs/lab1/generate-code-review-report.sh

# Verify outputs
ls -lh code-review-reports/
```

### Step 5.3: Create Report Template

**Prompt to Bob:**
```
Create a markdown template file called code-review-report-template.md that can be used for consistent code review reporting.
```

**What Bob does:**
- Creates template with standard sections
- Includes placeholders for metrics
- Provides formatting guidelines
- Adds examples

---

## Lab Summary

### What You Accomplished

✅ **Learned Code Reviewer Mode:**
- Switched to Code Reviewer mode
- Understood Bob's code analysis capabilities
- Used Bob Findings for inline analysis

✅ **Performed Code Review:**
- Analyzed order-service for PCI compliance
- Identified code quality issues
- Generated comprehensive review report
- Reviewed security and maintainability

✅ **Generated Wiki Reports:**
- Created wiki-formatted reports
- Added navigation and visual elements
- Made reports ready for publishing

✅ **Applied Remediation:**
- Fixed identified issues
- Verified improvements with Bob
- Compared before/after metrics

✅ **Created Automation:**
- Built report generation script
- Created reusable templates
- Automated the review workflow

### Key Takeaways

1. **Bob's Code Reviewer Mode** provides comprehensive code analysis beyond basic linting
2. **PCI Standards** are enforced through automated checks
3. **Wiki Reports** make findings accessible to the entire team
4. **Automation** enables consistent, repeatable code reviews
5. **Bob Findings** provides real-time feedback during development

### Files Created

```
labs/app_labs/lab1/
├── LAB1_CODE_REVIEW.md                    # This lab guide
├── generate-code-review-report.sh         # Automation script
├── code-review-report-template.md         # Report template
└── CODING_STANDARDS.md                    # PCI standards reference

code-review-reports/                       # Generated reports
├── CODE_REVIEW_REPORT.md                  # Standard report
├── CODE_REVIEW_WIKI.md                    # Wiki-formatted report
└── CODE_REVIEW_COMPARISON.md              # Before/after comparison
```

---

## Best Practices

### When to Run Code Reviews

- **Before Pull Requests:** Catch issues before code review
- **After Major Changes:** Verify quality after refactoring
- **Regular Intervals:** Weekly or sprint-based reviews
- **Before Releases:** Final quality check

### Tips for Effective Reviews

1. **Focus on High Priority Issues First:** Address critical and high-severity items
2. **Use Bob Findings During Development:** Catch issues early
3. **Document Remediation:** Track what was fixed and why
4. **Share Reports with Team:** Use wiki format for visibility
5. **Automate Regular Reviews:** Use scripts for consistency

### Integrating with Workflow

```bash
# Add to pre-commit hook
./labs/app_labs/lab1/generate-code-review-report.sh

# Add to CI/CD pipeline
- name: Code Review
  run: ./labs/app_labs/lab1/generate-code-review-report.sh

# Schedule regular reviews
0 9 * * 1 /path/to/generate-code-review-report.sh  # Every Monday at 9 AM
```

---

## Troubleshooting

### Issue: Bob can't find files

**Solution:**
```bash
# Verify you're in the correct directory
pwd
# Should be: /Users/jordanbond/Desktop/fis_app_bob/app-project-main

# List order-service files
ls -la order-service/src/main/java/com/example/orders/
```

### Issue: Code Reviewer mode not available

**Solution:**
- Ensure Bob CLI is up to date
- Check available modes: Click mode selector
- Code Reviewer should be in the list

### Issue: Report generation fails

**Solution:**
```bash
# Check Bob can access files
ls -R order-service/src/

# Verify permissions
chmod -R u+r order-service/

# Check disk space
df -h
```

### Issue: PCI violations not showing

**Solution:**
```bash
# Make sure you ran the injection script
./labs/app_labs/lab1/inject-pci-violations.sh

# Verify violations were injected
grep -n "System.out\|API_KEY\|192.168\|printStackTrace\|new Random\|TODO" \
  order-service/src/main/java/com/example/orders/service/OrderService.java

# Check Bob Findings in the editor
```

---

## Cleanup (Optional)

After completing the lab, you can restore the original code:

### Restore Original Code

**Run the restore script:**
```bash
./labs/app_labs/lab1/restore-pci-violations.sh
```

**What it does:**
- Restores OrderService.java from backup
- Removes all injected PCI violations
- Cleans up the backup file

**Verify restoration:**
```bash
# Check Bob Findings (should show no issues)
# Or run checkstyle
cd order-service && mvn checkstyle:check -Dcheckstyle.config.location=../pipeline/pci-checkstyle.xml
```

### Remove Generated Reports

```bash
rm -rf code-review-reports/
```

---

## Advanced Exercises

### Exercise 1: Custom Coding Standards

Add custom rules to the code review:

**Prompt:**
```
Bob, add custom code review rules to check for:
1. Methods longer than 50 lines
2. Classes with more than 10 methods
3. Missing unit tests for public methods
```

### Exercise 2: Trend Analysis

Track code quality over time:

**Prompt:**
```
Bob, create a script that tracks code review metrics over time and generates a trend report showing improvements or regressions.
```

### Exercise 3: Team Dashboard

Create a team-wide code quality dashboard:

**Prompt:**
```
Bob, generate a team dashboard showing code quality metrics for all services, with comparisons and rankings.
```

---

## Additional Resources

### Documentation
- [PCI DSS Requirements](https://www.pcisecuritystandards.org/)
- [Java Code Conventions](https://www.oracle.com/java/technologies/javase/codeconventions-contents.html)
- [Clean Code Principles](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)

### Tools
- [Checkstyle](https://checkstyle.org/) - Java code style checker
- [PMD](https://pmd.github.io/) - Source code analyzer
- [SpotBugs](https://spotbugs.github.io/) - Bug pattern detector
- [SonarQube](https://www.sonarqube.org/) - Code quality platform

### Related Labs
- `labs/lab3/LAB3_SECURITY_ANALYSIS.md` - Security-focused analysis
- `labs/app_labs/lab2/LAB2_SEMANTIC_VERSIONING.md` - Version analysis

---

## Feedback

Did you complete this lab successfully? Have suggestions for improvement?

**Share your feedback:**
- Create an issue in the repository
- Submit a pull request with improvements
- Share your experience with the team

---

**Lab Version:** 1.0  
**Last Updated:** April 24, 2026  
**Author:** Bob (Senior Software Engineer)  
**Difficulty:** Beginner