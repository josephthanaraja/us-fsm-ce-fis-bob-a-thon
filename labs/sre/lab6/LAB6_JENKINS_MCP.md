# Lab 6 — Jenkins Pipeline Insights with MCP

## Table of Contents

- [Overview](#overview)
  - [What you'll build](#what-youll-build)
- [Before you start](#before-you-start)
- [Part 1 — Jenkins MCP Server](#part-1--jenkins-mcp-server)
- [Part 2 — Pipeline Information](#part-2--pipeline-information)
- [Part 3 — Analysis and Insights](#part-3--analysis-and-insights)
- [Part 4 — Optional: Advanced Jenkins Automation](#part-4--optional-advanced-jenkins-automation)
- [Troubleshooting](#troubleshooting)

---

## Overview

In this lab, you'll configure the Jenkins MCP server to interact with your Jenkins instance directly from Bob, enabling pipeline monitoring, build analysis, and automated insights without leaving your IDE. This is a simpler lab and does not involve any modifications to your Jenkins instance or the pipeline you have built throughout the workshop. The lab will give you a sense for life with and without the MCP server

**Without the Jenkins MCP server:**

- Switch to Jenkins UI to check build status
- Manually search through console logs
- Copy/paste log snippets into Bob for analysis
- Context-switch between tools

**With the Jenkins MCP server:**

- Query pipeline status from Bob: "What's the status of my last 5 builds?"
- Analyze failures in context: "Why did build #42 fail?"
- Generate insights: "Show me all failed builds from today"
- Automate monitoring: "Alert me if the success rate drops below 80%"
- Correlate with code: "Which commit caused build #42 to fail?"

> [!NOTE]
>
> - It is assumed you have completed some or all of the previous labs so that there will be pipelines and pipeline runs in the instance.
> - The Jenkins MCP server is configured using `mcp-jenkins` via `uvx`, following the same pattern you used for the Jira MCP server in the advanced features introduction lab.

### What you'll build

In this lab, you won't actually build anything, but you will use the Jenkins MCP server to interact with your Jenkins instance directly from Bob. You will use the MCP server to explore:

- **Pipeline discovery tools** — query all pipelines on your Jenkins instance, explore their configurations, and understand their structure.

- **Build analysis capabilities** — inspect specific builds, retrieve logs, analyze test results, and identify failure causes.

- **Automated insights** — generate reports on pipeline health, identify patterns in failures, spot flaky tests, and correlate issues with code changes.

By the end, you'll be able to monitor and analyze your Jenkins pipelines entirely through Bob, automating common queries and generating actionable insights.

---

## Before you start

- [ ] Lab 1 complete (you understand Jenkins pipeline structure and have a working pipeline)
- [ ] Completed `labs/intro-labs/bob-lab-2-advanced-features.md` (you've set up an MCP server before with Jira)
- [ ] `uv` installed on your system ([install instructions](https://docs.astral.sh/uv/getting-started/installation/))
- [ ] Jenkins credentials provided by your instructor (URL, username, API token)

---

## Part 1 — Jenkins MCP Server

The Jenkins MCP server is a Model Context Protocol server that connects Bob to your Jenkins instance through the Jenkins REST API. It provides tools that let Bob query pipelines, inspect builds, retrieve logs, and analyze results — all through natural language.

The `mcp-jenkins` server provides these following tools (just a subset of the available tools):

- **`list_jobs`** — List all pipelines/jobs on the Jenkins instance
- **`get_job_info`** — Get detailed information about a specific job (configuration, parameters, recent builds)
- **`list_builds`** — List recent builds for a specific job
- **`get_build_info`** — Get detailed information about a specific build (status, duration, stages, artifacts)
- **`get_build_log`** — Retrieve the console output for a build
- **`get_build_test_results`** — Get test results from a build (passed, failed, skipped)

To configure the server, we will use the exact same pattern you used for the Jira MCP server in the advanced features lab. First lets setup an API key for the Jenkins instannce.

1. Open your Jenkins URL in a browser and log in.

1. Click on your profile picture in the top right corner and select **Security** from the left panel.

    ![jenkins_apikey_1.png](assets/jenkins_apikey_1.png)

1. Click on the **Add new token** button, then in the popup modal give your token a name, then click **Generate** button.

1. Copy the token value, you will need it later, and click the **Done** button.

Next, lets setup the MCP server. The `.bob/mcp.json` file already exists at the repo root.

1. Open the `.bob/mcp.json` file. If you completed the advanced features lab, it might already have the Jira/Atlassian server configured. That's fine — we'll add the Jenkins server alongside it.

1. Add the Jenkins server block to the `mcpServers` object:

    ```json
    {
    "mcpServers": {
        "jenkins": {
        "command": "bash",
        "args": [
            "-c",
            "set -a; source .env; set +a; exec uvx mcp-jenkins --jenkins-url \"$JENKINS_URL\" --jenkins-username \"$JENKINS_USERNAME\" --jenkins-password \"$JENKINS_API_TOKEN\""

        ],
        "disabled": false,
        "alwaysAllow": []
        }
    }
    }
    ```

    - If you already have the Atlassian server configured, your file should look like this:

        ```json
        {
        "mcpServers": {
            "atlassian": {
                .....
            },
            "jenkins": {
            "command": "bash",
            "args": [
                "-c",
                "set -a; source .env; set +a; exec uvx mcp-jenkins --jenkins-url \"$JENKINS_URL\" --jenkins-username \"$JENKINS_USERNAME\" --jenkins-password \"$JENKINS_API_TOKEN\""
            ],
            "disabled": false,
            "alwaysAllow": []
            }
        }
        }
        ```

1. Save the `mcp.json` file.

Next, we have to add the credentials to our environment file. If you completed the advanced features lab, it already has your Jira credentials — that's fine, we'll add Jenkins credentials below them.

1. Open the `.env` file at the repo root and add these lines (update it with your username and the token you created in the previous steps):

    ```bash
    JENKINS_URL=https://jenkins.example.com
    JENKINS_USERNAME=your-username
    JENKINS_API_TOKEN=your-api-token
    ```

    > [!NOTE]
    > - You dont need quotes around the values, nor spaces around the `=`
    > - The URL should include `https://` but no trailing slash
    > - `.env` is gitignored, so your token won't be committed

1. Save the `.env` file. and restart Bob (Bob reads `.bob/mcp.json` and `.env` once at startup). 

Let's verify the MCP server started.

1. Open Settings (gear icon) near the top right of the Bob IDE, then click on the `MCP` option on the left panel

    ![bob_mcp_settings_1.png](assets/bob_mcp_settings.png)

1. Look for `jenkins` in the MCP server list

1. Status should show **Connected** (green).

1. Just to be sure, restart the MCP server by clicking on the `jenkins` MCP server and then clicking the `Restart server` icon

    ![bob_mcp_settings_1.png](assets/bob_mcp_settings_2.png)

1. If you see **Failed**, check the following (do not proceed to the next section until you have successfully connected to the MCP server):

    - Double-check `.env` is at the repo root
    - Verify all three Jenkins values are filled in
    - Ensure no quotes or extra spaces
    - Check the Jenkins URL is accessible from your machine
    - Review the MCP server logs in Settings → MCP → jenkins → View Logs

Finally, lets run a quick test to make sure the MCP server is working.

1. Switch to **Advanced mode** (MCP tools aren't available in Plan, Code, or Ask).

    ```text
    use the jenkins mcp server to check what pipeliens are available
    ```

1. If Bob says the jenkins server isn't available, go back to the previous step and verify the connection status. If Bob display a response with your pipeline, you are connected to the Jenkins instance

    ![jenkins_mcp_1.png](assets/jenkins_mcp_1.png)

---

## Part 2 — Pipeline Information

Now that the server is connected, let's explore what's on your Jenkins instance.

1. Switch to the **Advanced mode**, ask Bob:

    ```text
    Use the jenkins MCP server to list all jobs/pipelines on the system.
    ```

1. Bob will call the `get_all_item` tool and show you all pipelines. You should see your pipelines (e.g., `user1/user1-pipeline`).

1. Now focus on your specific pipeline. Replace `user1/user1-pipeline` with your actual pipeline name and run:

    ```text
    Use the jenkins MCP server to get detailed information about the user1/user1-pipeline pipeline.
    ```

    > **Note:** we are using the folder/pipelinename syntax to specify the pipeline. It should match what was returned in step 1 of Part 2.

Bob will call several tools to provide a comprehensive summary of your pipeline including details like: Pipeline description, Last build number and status, Recent build history, Build artifacts (if any), and more.

1. Spend some time exploring the response from Bob.

1. Ask Bob to show you the recent builds for this pipeline (remember to replace the pipeline name with your own pipeline name):

    ```text
    Use the jenkins MCP server to list the last 10 builds for the job "user20-pipeline".
    ```

1. Bob will use the `get_build` tools to show information about the pipeline builds, including status, duration, timestamps, etc. Along with a summary of success rate and its own observations.

1. Finally, lets ask Bob to give us some analysis on the build information we have so far. Ask Bob to explain what it sees:

    ```text
    Based on the job information and recent builds, explain the structure and health of my pipeline.
    ```

1. Bob will analyze the data and give you some trends around your pipeline builds, potential issues and recommendations for improvement.

---

## Part 3 — Analysis and Insights

Now let's explore a couple of more complex / comprehensive scenarios we can explore with Bob.

1. Pick a recent build number from Part 2 that either had a `FAILURE` OR `UNSTABLE` (let's say build #12). Ask Bob to retrieve and analyze the logs (remember to replace the pipeline name with your own pipeline name)::

    ```text
    Use the jenkins MCP server to get the console log for build #12 of "user1-pipeline". Analyze it and tell me what caused the failure.
    ```

1. To understand what changed between a successful and failed build, ask Bob to compare two build numbers (be sure to use a successful and a failed build that you saw from Part 2 and remember to replace the pipeline name with your own pipeline name).

    ```text
    Compare build #14 (successful) with build #12 (failed) of "user1-pipeline". What changed?
    ```

1. Bob will retrieve information for both builds and tell you what changed between the two builds. Focusing on: GIT comitts, files that changed, test differences, etc.

1. We can also ask Bob to do more than compare two builds, but provide analysis across various builds. Go ahead and ask Bob to look for patterns (remember to replace the pipeline name with your own pipeline name):

    ```text
    Use the jenkins MCP server to analyze the last 20 builds of "user1-pipeline". What patterns do you see in failures? What's the success rate? What's the average build duration?
    ```

1. Again, Bob will retrieve data and provide its analysis. Providing things like success rate, failure patterns, average durations, etc.

1. Finally, lets ask Bob to create a comprehensive report for us using the following prompt (remember to replace the pipeline name with your own pipeline name):

    ```text
    Use the jenkins MCP server to create a health report for "user1-pipeline" covering the last 10 builds. Include:
    - Success rate
    - Average build duration
    - Most common failure causes
    - Test stability
    - Trends over time
    - Recommendations for improvement
    ```

---

## Part 4 — Optional: Advanced Jenkins Automation

The above sections are just some of the things you can do with Bob integrated with the Jenkins MCP server. Feel free to explore different scenarios and use cases with different prompts. Keep in mind that getting information in/out of the Jenkins instance is based on the tools available in the MCP server.  If you've completed Parts 1-3 and want to explore further, try these challenges.

### Challenge 1: Additional Prompts

Not really a challenge, but here are some additional prompts you can use to explore what else you can have Bob do with Jenkins:

- Pick a recent build number from Part 3 (let's say build #15). Ask Bob :

    ```text
    Use the jenkins MCP server to get detailed information about build #15 of the job "user1-pipeline".
    ```

- Test case failures:

    ```text
    Use the jenkins MCP server to check the last 15 builds of "user1-pipeline". Are any tests failing intermittently? Which tests are flaky?
    ```

- Daily monitor query:

    ```text
    Create a summary of all builds that ran today across all pipelines on the Jenkins instance. For each failed build, include the job name, build number, failure cause, and a link to the build.
    ```

### Challenge 2: Create a Jenkins Analysis Mode

Build a custom Bob mode specialized for Jenkins pipeline analysis.

**Goal:** Create a mode that:

- Has access to Jenkins MCP tools
- Formats output for reports
- Includes common queries as prompts
- Follows a consistent analysis structure

**Steps:**
1. Switch to **Mode Writer** mode

2. Create a mode with slug `jenkins-pipeline-analyzer`
3. Include tool groups: read only (no execute)
4. Add the jenkins MCP server to the mode's `mcpServers` list
5. Define prompts for common queries (health check, failure analysis, trend report)
6. Test the mode by switching to it and running queries

**Success criteria:**

- Mode appears in Bob's mode dropdown
- Mode can access Jenkins MCP tools
- Output is consistently formatted
- Common queries are easier to run

### Challenge 3: Build a Multi-Pipeline Health Dashboard

Generate a health report across all pipelines on the Jenkins instance.

**Goal:** Create a dashboard showing:

- All pipelines and their current status
- Success rates for each pipeline
- Recent failures with root causes
- Pipelines that need attention
- Overall system health score

**Prompt to try:**

```text
Use the jenkins MCP server to create a health dashboard for all pipelines. For each pipeline, show:
- Current status (last build result)
- Success rate over last 10 builds
- Average build duration
- Most recent failure cause (if any)
- Health score (0-100)

Then provide an overall system health summary and list the top 3 pipelines that need attention.
```

**Success criteria:**

- Dashboard covers all pipelines
- Metrics are accurate
- Priorities are clear
- Report is actionable

### Challenge 4: Pipeline Optimization Insights

Analyze build performance over time and suggest optimizations.

**Goal:** Generate insights about:

- Build duration trends
- Slowest stages
- Stages that are getting slower
- Opportunities for parallelization
- Caching opportunities

**Prompt to try:**

```text
Use the jenkins MCP server to analyze the last 50 builds of "user1-pipeline". For each stage:
- Calculate average duration
- Identify duration trends (getting faster/slower)
- Compare to other pipelines
- Suggest optimization opportunities

Then provide:
- Top 3 slowest stages
- Stages with increasing duration
- Specific optimization recommendations
- Expected time savings
```

**Success criteria:**

- Analysis covers sufficient history
- Trends are identified correctly
- Recommendations are specific and actionable
- Expected impact is quantified

---

## Troubleshooting

| Issue | Symptom | Solutions |
|-------|---------|-----------|
| **🔌 MCP Server Won't Connect** | Settings → MCP shows jenkins server as "Failed" or "Disconnected" | ✓ Verify `uv` is installed: `uv --version`<br>✓ Check `.env` file exists at repo root and has all three Jenkins values<br>✓ Ensure no quotes around values in `.env`<br>✓ Verify Jenkins URL is accessible: open it in a browser<br>✓ Check for typos in `.bob/mcp.json` (valid JSON?)<br>✓ Restart Bob completely (quit and reopen)<br>✓ Check MCP server logs: Settings → MCP → jenkins → View Logs |
| **🔐 Authentication Failures** | MCP server connects but tools fail with "401 Unauthorized" or "403 Forbidden" | ✓ Verify API token is correct (regenerate in Jenkins if needed)<br>✓ Check username matches your Jenkins login exactly<br>✓ Ensure API token has appropriate permissions (read access to jobs)<br>✓ Test credentials by logging into Jenkins UI<br>✓ Verify Jenkins URL doesn't have a trailing slash in `.env` |
| **🔍 "Job not found" Errors** | Bob says the job/pipeline doesn't exist | ✓ Verify job name matches exactly (case-sensitive)<br>✓ Use `list_jobs` first to see available job names<br>✓ Check you have permissions to access the job in Jenkins UI<br>✓ Ensure the job exists (wasn't deleted or renamed)<br>✓ Try the full job path if it's in a folder (e.g., "folder/job-name") |
| **⚙️ `uvx` Command Not Found** | MCP server fails to start with "uvx: command not found" | ✓ Install `uv`: Follow [installation instructions](https://docs.astral.sh/uv/getting-started/installation/)<br>✓ Verify installation: `uv --version`<br>✓ Restart terminal after installation<br>✓ Check `uv` is in your PATH: `which uv`<br>✓ Try running `uvx --version` directly |

---

**You've completed the SRE lab series! You now have:**

- ✅ Automated PR reviews (Lab 1)
- ✅ Intelligent test failure analysis (Lab 2)
- ✅ Security scanning with Bob (Lab 3)
- ✅ Multi-tool linting and compliance (Lab 4)
- ✅ DCR and Jira integration (Lab 5)
- ✅ Jenkins pipeline insights and automation (Lab 6)

**Next steps:**

- Apply these patterns to your own projects
- Create custom modes for your team's workflows
- Explore other MCP servers (Slack, PagerDuty, Datadog, etc.)
- Share your Bob configurations with your team
- Build automation that combines multiple MCP servers

Congratulations on completing the SRE portion of this workshop! 🎉