# Java Application Modernization with Bob

## Overview

In this lab, you'll learn how to use Bob to modernize legacy Java applications, upgrading from Java 8 to Java 17/21 while leveraging modern language features, improving performance, and maintaining backward compatibility. This lab demonstrates Bob's capabilities in understanding complex codebases and applying systematic modernization patterns.

### Learning Objectives

By the end of this lab, you will be able to:

1. Analyze legacy Java code and identify modernization opportunities
2. Use Bob to upgrade Java 8 code to Java 17/21
3. Leverage modern Java features (records, sealed classes, pattern matching, etc.)
4. Migrate from legacy APIs to modern alternatives
5. Improve performance with modern JVM features
6. Maintain backward compatibility during migration
7. Create comprehensive migration documentation

Key Outcomes:

✅ Java 8 → 17/21 migration skills  
✅ Modern Java feature mastery  
✅ Large-scale refactoring experience  
✅ UI and CLI workflow understanding  
✅ Pattern recognition abilities  

### Prerequisites

- **Java 17 or 21**

## Lab Approach

### What You'll Modernize

This lab focuses on modernizing a legacy Java 8 e-commerce application to Java 17/21, including:

- **Language Features**: Upgrade to records, sealed classes, pattern matching, switch expressions
- **API Modernization**: Migrate from Date to java.time, Collections improvements
- **Concurrency**: Update to modern concurrency utilities and virtual threads
- **Performance**: Leverage JVM improvements and modern garbage collectors
- **Dependencies**: Update libraries and frameworks to modern versions

Lab Structure and Technology Stack

```text
Legacy:             Modern:            Tools:
- Java 8            - Java 17/21       - Bob AI
- POJOs             - Records          - Maven/Gradle
- Old patterns      - Sealed classes   - JUnit 5
                    - Pattern matching
```

```text
simple-java-modernization/
├── README.md                           # This file
|── legacy/                             # Java 8 legacy code
│   ├── src/
│   │   └── main/
│   │       └── java/
│   │           └── com/example/ecommerce/
│   │               ├── model/          # Domain models
│   │               ├── service/        # Business logic
│   │               ├── repository/     # Data access
│   │               └── util/           # Utilities
│   ├── pom.xml                         # Maven configuration (Java 8)
│   └── README.md                       # Legacy code documentation
└── modernized/                         # Java 17/21 modernized code
```

#### Step-by-Step Flow

1. **Legacy Code Analysis**
   - Examine Java 8 codebase
   - Identify modernization opportunities
   - Document current patterns
   - Plan migration strategy

2. **Records Migration**
   - Convert POJOs to records
   - Update constructors and getters
   - Refactor equals/hashCode/toString
   - UI and CLI approaches

3. **Sealed Classes**
   - Identify class hierarchies
   - Apply sealed class patterns
   - Update switch expressions
   - Pattern matching integration

4. **Modern Features**
   - Text blocks for SQL/JSON
   - Pattern matching for instanceof
   - Enhanced switch expressions
   - Stream API improvements

5. **Testing & Validation**
   - Verify functionality
   - Performance comparison
   - Code quality metrics
   - Documentation updates

---

## Part 1: Analyzing Legacy Code

1. First, let's analyze the legacy codebase using Bob's UI:

1. Ensure you're in **Plan Mode** (📝 Plan mode)

1. **Add the Legacy Code to Context**
   - In the Bob chat input field, type `@` to open the file navigator
   - Browse to `simple-java-modernization/legacy/src/` and select the Java files you want to analyze
   - You can select multiple files by typing `@` again for each file
   - Bob will load the selected files into the conversation context

1. Prompt Bob with the following:

   ```text
   Analyze this Java 8 codebase and identify modernization opportunities for upgrading to Java 17.
   Focus on:
   - Opportunities to use records instead of POJOs
   - Places to apply pattern matching
   - Code that can use switch expressions
   - Areas where Optional can replace null checks
   - Streams that can be simplified
   - Date/Time API migration opportunities
   
   Create a detailed analysis report and save it to migration-guide/analysis-report.md
   ```

1. Review Bob's Analysis, Bob will provide:
   - Complexity metrics and maintainability scores
   - Specific modernization opportunities with code examples
   - Breaking changes to watch for
   - Expected performance improvements
   - Estimated migration effort

1. **Bob Will Auto-Save the Analysis**
   - Bob will automatically create and save the markdown file to `migration-guide/analysis-report.md`
   - If Bob doesn't save automatically, explicitly ask: "Please save this analysis to migration-guide/analysis-report.md"

1. Open the generated analysis report to understand:

    1. **Complexity Metrics**: Current code complexity and maintainability
    2. **Modernization Opportunities**: Specific features that can be upgraded
    3. **Breaking Changes**: Potential compatibility issues
    4. **Performance Improvements**: Expected performance gains
    5. **Migration Effort**: Estimated time and complexity

## Part 2: Creating Migration Plan

1. **Stay in Plan Mode** (📝 Plan mode) or switch to it if needed

1. Add the analysis report by typing `@migration-guide/analysis-report.md` and ask Bob to create the migration plan

   ```text
   Create a detailed migration plan for upgrading this Java 8 application to Java 17, including:
   - Phase-by-phase approach
   - Risk assessment
   - Testing strategy
   - Rollback procedures
   - Timeline estimates
   
   Base this on @migration-guide/analysis-report.md and save the plan to migration-guide/migration-plan.md
   ```

1. Review the `migration-guide/migration-plan.md` plan and ask Bob to make adjustments if needed

## Part 3: Modernizing Code

1. Let's modernize the domain models using Bob:

1. **Switch to Code Mode** (💻 Code mode). Type `@simple-java-modernization/legacy/src/main/java/com/example/ecommerce/model/Product.java` to add it to Bob's context

1. Ask Bob to convert the `Product` class to a Java 17 record:

   ```text
   Convert this Product class to a Java 17 record. Include:
   - Compact constructor for validation
   - Null checks for required fields
   - Validation for price (must be non-negative)
   - Proper JavaDoc comments
   
   Save the modernized version to simple-java-modernization/modernized/src/main/java/com/example/ecommerce/model/Product.java
   ```

1. Review the modernized code. You should see that the modernized verrsion is:

    - Reduced from 50+ lines to ~15 lines
    - Immutable by default
    - Built-in equals, hashCode, toString
    - Better performance
    - More readable

1. Next, we are going to use sealed classes for type hierarchies. Asking Bob to modernize the Payment class hierarchy using sealed classes.

1. Open Payment.java, and in Bob's chat, type:

    ```text
    Modernize this Payment class to use sealed classes.
    ```

1. We will continue modernizing the code by modernizing the business logic. Ensure you're still in **Code Mode** (💻)

1. Open legacy/src/main/java/com/example/ecommerce/service/PaymentService.java

1. Highlight the `calculateFee` method (or the entire class). Then Right-click and select "IBM Bob" -> "Add to Context".

1. Ask Bob to modernize the method using this prompt:

   ```text
   Modernize this payment fee calculation method to use Java 17 features:
   - Replace instanceof checks with pattern matching
   - Use switch expressions instead of if-else chains
   - Make the code more concise and readable
   - Ensure exhaustiveness checking with sealed classes
   
   Show me the before and after comparison.
   ```

1. Bob will show the modernized code with pattern matching, go ahead and review the improvements.

1. Lets modernize several more aspects of the application:

    1. To modernize the collection operations, Open the `OrderService.java class` and ask Bob to:

        ```text
        Modernize the stream operations in this code to use Java 17 improvements:
        - Replace .collect(Collectors.toList()) with .toList()
        - Optimize stream pipelines
        - Use modern collection factory methods
        ```

    1. Modernize the Date/Time API from legacy Date/Calendar to java.time by prompting Bob with:

        ```text
        Migrate all Date and Calendar usage to java.time API:
        - Replace Date with LocalDateTime or Instant
        - Replace Calendar with LocalDateTime
        - Update date comparison logic
        - Modernize date formatting
        ```

    1. Modernize the Null checks with Optional usage. **Open repository or service files** with null checks. Then ask Bob:

        ```text
        Refactor this code to use Optional instead of null checks:
        - Replace null returns with Optional
        - Use Optional methods (ifPresent, orElse, etc.)
        - Improve null safety
        ```

1. Let's go through some concurrency modernization

    1. Since we will be targeting Java 21, leverage virtual threads using Bob:

        - **Open AsyncService.java** with ExecutorService usage and request Bob do a virtual thread migration:

            ```text
            Modernize this code to use Java 21 virtual threads:
            - Replace fixed thread pools with virtual thread executors
            - Update ExecutorService creation
            - Optimize for virtual thread usage
            ```

    1. Lets modernize async operations of CompletableFuture using Bob:

        - **Open AsyncService.java** and request Async Modernization in Bob's chat:

            ```text
            Modernize the CompletableFuture usage in this code:
            - Use modern async patterns
            - Improve error handling
            - Optimize async chains
            ```

1. Finally, lets update the application dependencies

    1. Update Maven Configuration - Use Bob to update the `pom.xml` file:

        - **Open pom.xml** in your editor
        - **Request Maven Update** in Bob's chat:

            ```text
            Update this pom.xml for Java 17:
            - Change compiler source and target to 17
            - Add compiler release property
            - Update Spring and other dependencies to Java 17 compatible versions
            - Save to simple-java-modernization/modernized/pom.xml
            ```

    1. Let's check all dependencies for Java 17 compatibility using Bob's UI:

        - **Switch to Plan Mode** (📝)
        - **Open pom.xml** and add to context with `@`
        - **Request Compatibility Analysis** in Bob's chat:

            ```text
            Analyze this pom.xml for Java 17 compatibility:
            - Identify dependencies that need updates
            - Suggest Java 17 compatible versions
            - Flag any incompatible dependencies
            - Recommend alternatives if needed
            
            Save the analysis to simple-java-modernization/migration-guide/dependency-report.md
            ```

1. Review the legacy and modernized code.

## Part 4: Testing and Validation

1. Create tests to validate the migration using Bob's UI:

    1. **Switch to Code Mode** (💻)

    2. **Request Test Generation** in Bob's chat:

        ```text
        Create comprehensive tests to validate the Java 8 to Java 17 migration:
        - Functional equivalence tests
        - Performance comparison tests
        - API compatibility tests
        - Integration tests
        
        Compare behavior between legacy/ and modernized/ code.
        Save to simple-java-modernization/modernized/src/test/java/MigrationValidationTest.java
        ```

1. Compare performance by asking Bob to generate benchmarks. Prompt Bob with:

   ```text
   Create JMH benchmarks to compare performance between Java 8 and Java 17:
   - Record creation vs POJO
   - Pattern matching vs instanceof
   - Stream operations
   - Date/Time operations
   
   Save to simple-java-modernization/modernized/src/test/java/PerformanceBenchmark.java
   ```

## Part 5: Documentation Generation

1. Create comprehensive documentation using Bob:

    1. **Switch to Plan Mode** (📝)
    2. **Request Feature Comparison** in Bob's chat:

        ```text
        Create a detailed comparison document showing:
        - Side-by-side code examples (Java 8 vs Java 17)
        - Performance improvements
        - Code reduction metrics
        - Maintainability improvements
        
        Analyze both legacy/ and modernized/ directories.
        Save to simple-java-modernization/migration-guide/feature-comparison.md
        ```

    3. **Request Best Practices Guide**:

        ```text
        Create a best practices guide for Java modernization:
        - When to use records vs classes
        - Sealed class usage patterns
        - Pattern matching best practices
        - Stream API optimization
        - Concurrency patterns
        
        Save to simple-java-modernization/migration-guide/best-practices.md
        ```

    > **📝 Note:** Bob may create additional markdown files during the lab (such as `JAVADOC_GENERATION_GUIDE.md` or similar) to provide supplementary guidance. These are helpful reference materials that Bob generates to support your learning. You can keep them for reference or remove them if not needed.

1. Generate updated API documentation for the modernized code using Bob:

   ```text
   Generate comprehensive JavaDoc documentation for the modernized code in simple-java-modernization/modernized/src/:
   - Include all public APIs
   - Document Java 17 features used
   - Add usage examples
   - Format as HTML
   
   Save to simple-java-modernization/modernized/docs/api/
   ```

1. Request Architecture Documentation:

   ```text
   Generate architecture documentation for the modernized application:
   - System overview
   - Component relationships
   - Design patterns used
   - Java 17 features utilized
   
   Save to simple-java-modernization/modernized/docs/architecture.md
   ```

---

## Summary

In this lab, you learned:

✅ How to analyze legacy Java code for modernization opportunities.  
✅ Using Bob to upgrade Java 8 code to Java 17/21.  
✅ Leveraging modern Java features (records, sealed classes, pattern matching).  
✅ Migrating from legacy APIs to modern alternatives.  
✅ Creating comprehensive migration documentation  
✅ Testing and validating migrations  

### Additional Resources

- [Java 17 Migration Guide](https://docs.oracle.com/en/java/javase/17/migrate/)
- [Java 21 Features](https://openjdk.org/projects/jdk/21/)
- [Modern Java Patterns](https://www.oracle.com/java/technologies/javase/17-relnote-issues.html)
- [Bob Java Modernization Guide](https://ibm.com/bob/docs/java-modernization)

---
*Adapted from Client Engineering `bob-intro-labs`. Last Updated: May 2026*
