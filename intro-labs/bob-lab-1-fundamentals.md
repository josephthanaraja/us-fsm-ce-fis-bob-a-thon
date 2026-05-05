# Lab 1: Bob Fundamentals
**Duration:** 40 minutes  
**Objective:** Learn Bob’s core workflows, built-in modes, approvals, and basic project assistance

**Prerequisites:**
- Bob application installed and running

> 📌 Here is where you can find Bob documentation if you ever get stuck or want to explore: https://bob.ibm.com/docs/ide

---

## Table of Contents
1. [Start Here](#getting-started-with-bob)
2. [Bob Modes](#understanding-bobs-modes)
3. [Approvals](#approvals-and-safe-collaboration)
4. [Planning](#planning-with-bob)
5. [Quick Practice](#quick-build-practice)
6. [Key Takeaways](#key-takeaways)
7. [Troubleshooting](#troubleshooting-tips)

---

## Overview

This lab gives a lightweight introduction to Bob.

### Learning Objectives

By the end of this lab, you will:

- ✅ Understand Bob’s main built-in modes
- ✅ Understand the approval flow
- ✅ Practice planning before implementation
- ✅ Use Bob to create and edit files safely
- ✅ Build confidence working with Bob interactively

---

## Getting Started with Bob

### The Bob Interface

Open the Bob application, it is very similar to the VSCode interface, but for Bob interactions you’ll mainly use:

- **Mode selector**: shows your current mode and lets you switch between Plan, Code, Ask, and Advanced
- **Chat history**: shows the conversation between you and Bob so you can follow the workflow
- **Tool activity**: shows when Bob is reading files, editing files, or using other tools
- **Input box**: where you type prompts, questions, and requests for Bob

### Other Key Interface Components

#### Settings
Access Bob's configuration options including:
- API keys and model selection
- Auto-approval preferences
- Custom mode configurations
- Theme and display options

#### Extensions
Extend Bob's capabilities with additional tools and integrations:
- Browse available extensions
- Install and manage extensions
- Configure extension settings

#### File Explorer
Navigate your project structure:
- View all files and folders in your workspace
- Create, rename, and delete files
- Organize your project hierarchy
- Quick access to any file

#### File Viewer
Review and edit files directly:
- View file contents with syntax highlighting
- See Bob's proposed changes before approval
- Compare original and modified versions
- Edit files manually when needed

> 📌 See more information about all the chat features here: https://bob.ibm.com/docs/ide/features/chat-interface

### First Interaction

Try:

```text
Hi Bob! I'm new here. Can you tell me 3 simple things you can help me with?
```

Then:

```text
What mode are you in right now, and what does that mean?
```

These two prompts provide you some initial information on what Bob does and what modes are. Feel free to try out other prompts and questions to see how Bob responds. 

Let's build an understanding of Modes and how they work for Bob. 

---

## Understanding Bob's Modes

Bob has three distinct modes, each optimized for different tasks:

> **🎯 Bob Differentiator: [Customizable Modes](../bob-differentiators.md#1--extensible-architecture)**
> Bob's mode system is one of its key differentiators. Unlike other AI assistants, Bob allows you to create custom modes tailored to your team's specific workflows. The three built-in modes you'll use in this lab are just the beginning—you can create specialized modes for code review, documentation, architecture design, and more. 

#### 🎯 Plan Mode
**When to use**: Planning, designing, strategizing
- Create project structures
- Design API endpoints
- Plan database schemas
- Make architectural decisions

#### 💻 Code Mode
**When to use**: Writing, modifying, refactoring code
- Implement features
- Create files
- Modify existing code
- Fix bugs

#### ❓ Ask Mode
**When to use**: Learning, understanding, getting help
- Explain code concepts
- Get documentation
- Understand errors
- Learn best practices

### Switching Between Modes

In Bob's interface:
1. Look for the mode selector (usually at the bottom left of the chat panel)
2. Click to see available modes
3. Select the mode you need
4. Bob will adapt its behavior accordingly

### Mode Practice

Try switching into Plan mode, then ask:

```text
Help me plan a simple personal notes project. What files should I create?
```

Then switch to Ask mode and ask:

```text
What is the difference between HTML, CSS, and JavaScript?
```

You can start to see how different modes can help with specific types of requests and how easy it is to switch between modes.


> 📌 See more infromation about modes here: https://bob.ibm.com/docs/ide/features/modes 

---

## Approvals and Safe Collaboration

Approvals are a core part of working with Bob. They help you stay in control, review changes before they happen, and catch mistakes early.
### Best Practice

Before approving:
1. Read the preview
2. Check the target file
3. Make sure it matches what you asked for

### Quick Approval Exercise

Ask Bob:

```text
Create a file called hello.txt with the text "Hello from Bob"
```

Watch for:
- which tool Bob uses
- when the approval prompt appears
- what the preview shows

### Understanding Auto-Approvals

**Auto-approvals** allow Bob to make multiple changes without asking for confirmation each time.

To enable auto-approvals:
1. Look for auto-approval settings in Bob
2. Enable for this session
3. Bob will now create multiple files rapidly

**⚠️ Important**: Review the files after Bob creates them to ensure they match your requirements.

> 📌 See more infromation about approvals here: https://bob.ibm.com/docs/ide/features/auto-approving-actions 

---

## Planning with Bob

**Switch to Plan Mode** and ask Bob:

```
I want to create a todo application with a Python Flask backend and JavaScript frontend.
Please help me plan:
1. Project directory structure
2. API endpoints needed
3. Database schema
4. Technology stack recommendations
```

**Bob's Interactive Approach:**

Before providing a plan, Bob will ask clarifying questions to understand your requirements better. This is a key differentiator—Bob lets you drive the process while making helpful suggestions.

Bob might ask:
- "How complex should the application be?"
- "Which database would you prefer (SQLite, PostgreSQL, MySQL)?"
- "Do you need user authentication?"
- "Should we include additional features like categories or priorities?"

**For this lab, respond with basic requirements:**
- Simple/basic complexity
- SQLite database (no installation needed)
- No user authentication
- Basic CRUD operations only

This collaborative approach ensures Bob builds exactly what you need, not what it assumes you want.

---

## Quick Build Practice

Switch Bob into Code Mode. This section should be fast. You’re just trying a few core actions: create, edit, connect, and explain.

### Step 1: Create HTML

```text
Create an index.html file for a simple notes page with:
- a heading
- a textarea
- a save button
Keep it minimal.
```

### Step 2: Add CSS

```text
Create a style.css file that makes the page clean and easy to read.
Keep it simple.
```

### Step 3: Add JavaScript

```text
Create an app.js file that shows a message when the save button is clicked.
Keep it very simple.
```

### Step 4: Connect the files

```text
Update index.html to link style.css and app.js.
```

### Step 5: Ask for an explanation

```text
Explain what each file does in simple terms:
- index.html
- style.css
- app.js
```

### Step 6: Make an edit

```text
Add a short comment at the top of app.js explaining what the file does.
```

Great! Now that we have run through a quick workflow you have a basice understanding of how Bob works and how to work with Bob! Take a moment to review the takeaways and tips before we move into the next lab!

---

## Key Takeaways

### Bob's Modes
- **Architect**: Perfect for planning and design decisions
- **Code**: Best for implementation and file creation
- **Ask**: Great for learning and understanding
- **Custom Modes**: Create your own specialized modes ([Learn more](../bob-differentiators.md#customizable-modes))

### Approvals
- Bob shows what it wants to do before taking action, you stay in control of all changes
- Always review before approving

---

## Troubleshooting Tips

### Bob is doing too much

Ask more narrowly:

```text
Create only index.html for now.
```

or

```text
Keep it minimal and do not build a full application.
```

### The generated files are too complex

Ask:

```text
Please simplify this to beginner-friendly code with minimal features.
```

### I’m not sure which mode to use

Use this rule:
- planning → Plan mode
- creating/editing → Code mode
- explanation → Ask mode
- mixed workflows → Advanced mode

### I don’t understand the code

Ask:

```text
Explain this file line by line in plain English.
```

---

## What You've Learned

✅ How to interact with Bob in a beginner-friendly way  
✅ How to switch between built-in modes  
✅ How approvals work and why they matter  
✅ How to plan before implementing  
✅ How to create and edit simple files  

---

## Additional Resources

- [Bob Documentation](https://bob.ibm.com/docs/ide)

---

**Lab 1 Complete! 🎉**

You’ve completed Bob Lab 1 using short, practical exercises that teach the core workflow without requiring a full build.