# Code Translation - Python to JavaScript

## Overview

In this lab, you'll learn to use Bob to translate code from one programming language to another while maintaining functionality and applying language-specific best practices. You'll translate a Python data processing script to JavaScript (Node.js).

### Translation Scope

**Source**: Python data processing script

- File I/O operations
- Data transformation with pandas/numpy
- List comprehensions
- Dictionary operations
- Error handling
- Type hints

**Target**: JavaScript (Node.js) equivalent implementation

- File system operations (Node.js)
- Array methods and transformations
- Object manipulation
- Promise-based async operations
- Error handling
- JSDoc type annotations

**Duration**: 20 minutes
**Difficulty**: Intermediate

### Lab Objectives

Lab Structure:

```text
Lab
├── Step 1: Analyze Python Code 
├── Step 2: Plan Translation Strategy
├── Step 3: Implement Translation
└── Step 4: Verify & Compare
```

By the end of this lab, you will:

- ✅ Use Ask mode to analyze source code
- ✅ Use Architect mode to plan translation strategy
- ✅ Use Code mode to implement translation
- ✅ Understand language-specific patterns
- ✅ Map Python features to JavaScript equivalents
- ✅ Maintain code functionality across languages
- ✅ Apply best practices in both languages

### Prerequisites

Before starting, ensure you have:

- [ ] UV and Python 3.8+ installed
- [ ] Node.js 14+ installed
- [ ] Bob installed and running

---

## Code Migration Workflow

### Analyze Python Code

1. Let's examine the Python data processor that we'll be translating. Open `source/data_processor.py` and review the code structure.

    **Key Features to Notice:**

    - Class-based design
    - Type hints (`: str`, `-> Dict`)
    - Context managers (`with open()`)
    - List comprehensions
    - Dictionary operations
    - CSV and JSON handling

1. Open Bob and switch to **Ask Mode** (❓). **Prompt Bob** with the following:

    ```text
    Analyze the Python code in source/data_processor.py and explain:
    1. What is the overall purpose of this code?
    2. What are the main components and their responsibilities?
    3. What Python-specific features are being used?
    4. What are the key data structures and algorithms?
    ```

    Bob should explain:

    - **Purpose**: Processes CSV data and generates statistical summaries
    - **Components**:
    - `DataProcessor` class with methods for loading, analyzing, and exporting
    - File I/O operations
    - Statistical calculations
    - **Python Features**:
    - Type hints for better code documentation
    - Context managers for safe file handling
    - List comprehensions for concise data processing
    - Dictionary comprehensions
    - **Data Structures**: Lists, dictionaries, CSV rows

1. Lets figure out what issues and challenges we might encounter during the language migration. Still in *Ask mode**, prompt Bob with the following:

    ```text
    What challenges might we face when translating this Python code to JavaScript?
    Consider:
    - Language syntax differences
    - Built-in library differences
    - Async/sync patterns
    - Type system differences
    ```

    > Bob should identify different challenges, some of the ones that might come up are:
    >
    > - **File I/O**: Python's `with open()` vs Node.js async file operations
    > - **CSV Parsing**: Python's `csv` module vs JavaScript libraries
    > - **Type Hints**: Python's type hints vs JSDoc or TypeScript
    > - **List Comprehensions**: Python's concise syntax vs JavaScript array methods
    > - **Synchronous vs Asynchronous**: Python's sync I/O vs Node.js async patterns

### Plan Translation Strategy

1. Now let's create a detailed translation plan. Change from Ask to **Plan Mode** (🎯). **Prompt Bob** with the following:

    ```text
    Create a detailed translation plan for converting the Python data processor to JavaScript.
    Include:
    1. Feature-by-feature mapping (Python → JavaScript)
    2. Library/module equivalents
    3. Syntax transformations needed
    4. Recommended JavaScript patterns
    5. File structure for the JavaScript version
    ```

1. Bob should respond with a mapping of the Python features to their JavaScript equivalents.

1. Lets use Bob to plan the target module structure. Still in **Plan Mode**, prompt Bob with the following:

    ```text
    Design the JavaScript module structure for the translated code.
    Should we use:
    - ES6 modules or CommonJS?
    - Classes or functional approach?
    - Async/await or promises?
    - Any additional error handling?
    ```

1. Identify the recommended JavaScript patterns and libraries/modules, prompt Bob with:

    ```text
    What npm packages will we need for the JavaScript version?
    List the packages and their purposes.
    ```

### Implement Translation

1. While we could perform the translation through a granular approach. For example, prompting Bob to do each of these steps individually:

    - Create a package.json file for the Javascript data processor with name, version, dependencies, main entry point, and scripts for running the processor
    - Translate the entire DataProcessor class from Python to JavaScript. Including constructor, methods, JSDoc comments, async/await, error handling, and main execution logic.

1. We are going to follow the plan we asked Bob to build. Change to **Code Mode** (💻) and **prompt Bob:**

    ```text
    Go ahead and implement the translation plan. Store the translated content to a translated-js-version folder.
    ```

1. Watch as Bob translates the entire class structure at once, creating a complete JavaScript implementation with all methods. You may be prompted to save files as Bob is working through the implementation.

    > **Note:** Bob may want to write a translation guide and run validation tests as part of its implementation plan. Feel free to let Bob do the testing for you or ask it to skip the testing as we will be doing that in a separate section.

1. Now let's examine how Bob translated specific components. **Switch to Ask Mode** (❓) to explore the translated code. **Prompt Bob with the examples below**

    ```text
    Explain how you translated the load_data method from Python to JavaScript.
    What are the key differences between Python's context manager and JavaScript's stream-based approach?
    ```

    ```text
    Explain how you translated the calculate_statistics method.
    How did you convert Python's list comprehensions and built-in functions to JavaScript?
    ```

    ```text
    Explain how you translated the export_results method.
    What's the difference between Python's synchronous file writing and JavaScript's async approach?
    ```

    ```text
    Explain how you translated Python's if __name__ == '__main__' pattern to JavaScript.
    Why did you use an async IIFE (Immediately Invoked Function Expression)?
    ```

**💡 Key Learning**: Code mode handles the actual translation while maintaining functionality.

---

### Verify & Compare

Let's test both versions and compare the results.

1. Create a sample CSV file called sample_data.csv for testing:

    ```csv
    name,age,score,grade
    Alice,25,95.5,A
    Bob,30,87.3,B
    Charlie,22,92.1,A
    Diana,28,88.7,B
    ```

1. Run Python Version

    ```bash
    uv run data_processor.py
    ```

    **Expected Output:**

    ```text
    Processing complete!
    Results saved to statistics.json
    ```

    **statistics.json:**

    ```json
    {
    "age": {
        "mean": 26.25,
        "min": 22,
        "max": 30,
        "count": 4
    },
    "score": {
        "mean": 90.9,
        "min": 87.3,
        "max": 95.5,
        "count": 4
    }
    }
    ```

1. Run JavaScript Version

    ```bash
    cd translated-js-version
    npm install
    node data_processor.js
    ```

    **Expected Output:**

    ```text
    ✅ Processing complete!
    Results saved to statistics.json
    ```

1. In addition to comparing the output yourself, you can also ask Bob to run this validation for you. 

    ```text
    Compare the Python and JavaScript implementations.
    What are the key differences in:
    1. Code structure
    2. Syntax
    3. Async handling
    4. Error handling
    5. Performance characteristics
    ```

1. You should see that both impelementations produce the same output.

    - ✅ Same statistical calculations
    - ✅ Same JSON structure
    - ✅ Same file handling
    - ✅ Equivalent error handling

---

## Congratulations! 🎉

You've successfully completed Lab 3! You've learned to:

- ✅ Analyze code structure across languages
- ✅ Plan translation strategies systematically
- ✅ Map language-specific features
- ✅ Implement translations maintaining functionality
- ✅ Handle async/sync differences
- ✅ Apply best practices in both languages
- ✅ Verify translated code correctness

## Additional Resources

- Python Resources
  - [Python Documentation](https://docs.python.org/)
  - [Type Hints Guide](https://docs.python.org/3/library/typing.html)
  - [CSV Module](https://docs.python.org/3/library/csv.html)

- JavaScript Resources
  - [Node.js Documentation](https://nodejs.org/docs/)
  - [MDN JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
  - [csv-parser](https://www.npmjs.com/package/csv-parser)

- Translation Guides
  - [Python to JavaScript Cheat Sheet](https://github.com/topics/python-to-javascript)
  - [Async Patterns](https://javascript.info/async-await)
  - [JSDoc Guide](https://jsdoc.app/)

---

*Adapted from Client Engineering `bob-intro-labs`. Last Updated: December 2025*
