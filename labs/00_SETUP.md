# Lab 0 — Participant Setup

Before you start Lab 1, set up **one Jenkins pipeline** that you'll reuse across all five labs. Each lab adds a new stage to `Jenkinsfile` on your branch; you push, click Build Now, and watch Bob do its thing.

---

## What your instructor should have given you

- [ ] **Jenkins URL** (e.g., `https://jenkins-<project>.<cluster>.techzone.ibm.com`)
- [ ] **Jenkins username** — something like `user1`
- [ ] **Jenkins password** — something like `bobathon-1`
- [ ] **GitHub repo URL** — where this workshop's code lives
- [ ] **Whether the repo is public or private** — if private, you'll need to do [Step 1](#step-1--add-a-github-pat-credential-private-repo-only) below. If public, skip it.

---

## Step 1 — Add a GitHub PAT credential (private repo only)

Skip this step if your instructor told you the repo is public.

You need to add a GitHub Personal Access Token to Jenkins **before** you configure your pipeline — the pipeline's Credentials dropdown won't show the PAT unless it's saved in Jenkins first.

### 1a. Create the PAT on GitHub

1. Go to **[github.com/settings/tokens](https://github.com/settings/tokens)** (or **[github.ibm.com/settings/tokens](https://github.ibm.com/settings/tokens)** for GitHub Enterprise — your instructor will tell you which)
2. Click **Generate new token → Generate new token (classic)**
3. Set:
   - **Note**: `bob-a-thon workshop`
   - **Expiration**: 7 or 30 days is fine
   - **Select scopes**: check only **`repo`**
4. Click **Generate token** at the bottom
5. **Copy the token now** — GitHub won't show it to you again

### 1b. Add the PAT as a Jenkins credential

In Jenkins, logged in as your assigned `userN`:

1. Click your **username** (e.g. `user1`) in the top-right corner
2. In the sidebar, click **Credentials**
3. Click on your user (e.g. `user1`) in the Stores table
4. Click **Global credentials (unrestricted)**
5. Click **Add Credentials** (top-left button)
6. Fill in:
   - **Kind**: `Username with password`
   - **Scope**: `Global`
   - **Username**: your GitHub username
   - **Password**: paste the PAT
   - **ID**: something unique to you, e.g., `github-pat-user1`
   - **Description**: `my GitHub PAT`
7. Click **Create**

You'll select this credential in Step 3 when you create the pipeline.

---

## Step 2 — Create your working branch

You'll work on your own branch throughout the workshop. A convention like `user1-labs`, `user2-labs`, etc., keeps names unique.

From a terminal on your laptop:

```bash
# Clone the repo (the URL your instructor gave you)
git clone <repo-url>
cd us-fsm-ce-fis-bob-a-thon

# Create your branch and push it
git checkout -b user1-labs
git push -u origin user1-labs
```

Replace `user1-labs` with your actual username (e.g., `user7-labs`). You'll push to this branch after every lab exercise.

---

## Step 3 — Create your Jenkins pipeline

From the Jenkins homepage:

1. Click **New Item** (top-left of the homepage)
2. Enter a name — something like `user1-pipeline`
3. Select **Pipeline** from the type list, then click **OK**
4. You land on the config page. Scroll to the **Pipeline** section at the bottom and fill in:

   | Field | Value |
   |---|---|
   | **Definition** | `Pipeline script from SCM` |
   | **SCM** | `Git` |
   | **Repository URL** | paste the GitHub repo URL from your instructor |
   | **Credentials** | for a public repo: leave as `- none -`. For a private repo: select the PAT credential you added in Step 1 |
   | **Branch Specifier** | `*/user1-labs` — replace with **your** branch name |
   | **Script Path** | `Jenkinsfile` |

5. Click **Save**. You land on your new pipeline's page.

---

## Step 4 — Run it once to verify

Click **Build Now** in the left sidebar. A build appears under "Build History" — click its number, then **Console Output**.

**Expected:** the `Checkout` stage completes and the console prints your workspace contents (`.bob/`, `Jenkinsfile`, `order-service/`, etc.). The pipeline finishes `SUCCESS` with no other stages yet — that's correct; you'll add stages lab by lab.

**If the build fails with `ImagePullBackOff`:** the Jenkinsfile's image URLs don't match your cluster's OpenShift project. Ask your instructor to confirm they ran Step 6 of the instructor setup.

**If the build fails with authentication errors:** your GitHub credentials aren't configured. Re-check Step 1.

---

## You're set — the workflow from here

The same pipeline runs through all 5 labs. Your loop for each lab:

1. Edit `Jenkinsfile` on your branch to add the new stage the lab describes
2. If the lab calls for it, edit `.bob/custom_modes.yaml` to add a Bob custom mode
3. Commit and push:
   ```bash
   git add .
   git commit -m "Lab N changes"
   git push
   ```
4. In Jenkins, click **Build Now** on your pipeline
5. Watch the new stage run

Ready? Open [LAB1_PR_REVIEW.md](LAB1_PR_REVIEW.md).
