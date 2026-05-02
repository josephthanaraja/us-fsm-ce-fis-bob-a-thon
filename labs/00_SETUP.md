# Lab 0 — Participant Setup

Before you start Lab 1, set up **one Jenkins pipeline** that you'll reuse across all five labs. Each lab adds a new stage to `Jenkinsfile` on your branch; you push, click **Build Now**, and watch Bob do its thing.

## Table of Contents

- [What your instructor should have given you](#what-your-instructor-should-have-given-you)
- [Step 1 — Add a GitHub PAT (private repo only)](#step-1--add-a-github-pat-private-repo-only)
  - [1a. Create the PAT on GitHub](#1a-create-the-pat-on-github)
  - [1b. Add the PAT to your folder's credential store](#1b-add-the-pat-to-your-folders-credential-store)
- [Step 2 — Create your working branch](#step-2--create-your-working-branch)
- [Step 3 — Create your Jenkins pipeline](#step-3--create-your-jenkins-pipeline)
- [Step 4 — Run it once to verify](#step-4--run-it-once-to-verify)
- [You're set — the workflow from here](#youre-set--the-workflow-from-here)
- [Stuck?](#stuck)

---

## What your instructor should have given you

- [ ] **Jenkins URL** (e.g., `https://jenkins-jenkins.<cluster>.techzone.ibm.com`)
- [ ] **Jenkins username** — something like `user1`
- [ ] **Jenkins password** — something like `user1Workshop2024!` (the instructor picked a base password and your password is `<username><base>`)
- [ ] **Git repo URL** — where this workshop's code lives
- [ ] **Whether the repo is public or private** — if private, you'll need to do [Step 1](#step-1--add-a-github-pat-private-repo-only) below. If public, skip it.

---

## Step 1 — Add a GitHub PAT (private repo only)

Skip this step if your instructor told you the repo is public.

You need to add a GitHub Personal Access Token to Jenkins **before** you configure your pipeline — the pipeline's Credentials dropdown won't show the PAT unless it's saved in Jenkins first, and it has to be saved in the right place.

### 1a. Create the PAT on GitHub

1. Go to your GitHub tokens page — `https://github.com/settings/tokens` for github.com, or `https://github.ibm.com/settings/tokens` for GitHub Enterprise (your instructor will tell you which)
2. Click **Generate new token → Generate new token (classic)**
3. Set:
   - **Note:** `bob-a-thon workshop`
   - **Expiration:** 7 or 30 days is fine
   - **Select scopes:** check only **`repo`**
4. Click **Generate token** at the bottom
5. **Copy the token now** — GitHub won't show it to you again

### 1b. Add the PAT to your folder's credential store

**This step is finicky** — there are three places in Jenkins that look like a "Credentials" page, and only one of them makes your PAT visible to your pipeline jobs. Follow this navigation exactly.

Logged into Jenkins as `userN`:

1. From the **Jenkins homepage**, click your `userN` folder (the folder-icon item in the list). **Do not** click your username in the top-right — that goes to a different (wrong) credential store.
2. In the folder's **left sidebar**, click **Credentials**.
3. On the folder's Credentials page, under **Stores scoped to userN**, click **(global)**.
4. Click **Add Credentials**
5. Fill in:
   - **Kind:** `Username with password`
   - **Scope:** `Global` (see note below about what this means)
   - **Username:** your GitHub username
   - **Password:** paste the PAT from step 1a
   - **ID:** `userN-github-pat` — replace `userN` with your actual username, e.g. `user1-github-pat`. The exact ID matters; the pipeline references it by this name.
   - **Description:** anything
6. Click **Create**.

You should land back on the folder's Credentials page, with one row now showing your new `userN-github-pat` credential.

> **Note on "Scope: Global".** The word *Global* in this dialog is misleading — it refers to which **URLs** the credential applies to (it's a URL-matching setting), **not** who can see the credential. Visibility is locked by the store you're in (your folder), and other workshop users can't see it. You can safely pick `Global` as the scope.

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

**Create the pipeline inside your `userN` folder, not at the Jenkins root.** If you create it at the root, you won't have permission to save it and the PAT from Step 1 won't be reachable.

From the Jenkins homepage:

1. Click your `userN` folder (the same one you added the PAT to).
2. Inside the folder, click **New Item** in the left sidebar.
3. Enter a name — something like `user1-pipeline`.
4. Select **Pipeline** from the type list, then click **OK**.
5. You land on the config page. Scroll to the **Pipeline** section at the bottom and fill in:

   | Field | Value |
   |---|---|
   | **Definition** | `Pipeline script from SCM` |
   | **SCM** | `Git` |
   | **Repository URL** | paste the GitHub repo URL from your instructor |
   | **Credentials** | for a public repo: leave as `- none -`. For a private repo: select the `userN-github-pat` credential you created in Step 1 |
   | **Branch Specifier** | `*/user1-labs` — replace with **your** branch name |
   | **Script Path** | `Jenkinsfile` |

6. Click **Save**. You land on your new pipeline's page.

---

## Step 4 — Run it once to verify

Click **Build Now** in the left sidebar. A build appears under "Build History" — click its number, then **Console Output**.

**Expected:** the `Checkout` stage completes and the console prints your workspace contents (`.bob/`, `Jenkinsfile`, `order-service/`, etc.). The pipeline finishes `SUCCESS` with no other stages yet — that's correct; you'll add stages lab by lab.

If something fails, see the [stuck?](#stuck) section at the bottom.

---

## You're set — the workflow from here

The same pipeline runs through all 5 labs. Your loop for each lab:

1. Edit `Jenkinsfile` on your branch to add the new stage the lab describes.
2. If the lab calls for it, edit `.bob/custom_modes.yaml` to add a Bob custom mode.
3. Commit and push:
   ```bash
   git add .
   git commit -m "Lab N changes"
   git push
   ```
4. In Jenkins, click **Build Now** on your pipeline.
5. Watch the new stage run.

Ready? Open [LAB1_PR_REVIEW.md](LAB1_PR_REVIEW.md).

---

## Stuck?

- **Build fails with `ImagePullBackOff`**: the Jenkinsfile's Bob image URL doesn't match your cluster. Ask your instructor to confirm the Bob image is pushed to the `jenkins` namespace.
- **"Credentials dropdown is empty" when configuring the pipeline**: your PAT went into the wrong store. Only **folder-scoped** credentials appear in the pipeline's Credentials dropdown — user-personal credentials (the one you get from the top-right username menu) don't. Re-check Step 1b: navigate from the homepage → your folder → **Credentials** in the folder sidebar (not the one under your top-right username).
- **"Credentials link is missing from the folder sidebar"**: your instructor needs to run the matrix-auth Groovy that grants `CredentialsProvider.VIEW` to each user. Ping them.
- **"Delete Folder" button is missing from my folder**: that's intentional. Matrix auth doesn't grant delete rights on the folder itself so you can't accidentally wipe your workshop work.
- **`git push` fails with auth**: regenerate the PAT (it may have expired) and re-add it in Step 1.
