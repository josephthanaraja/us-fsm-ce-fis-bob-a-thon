// ═══════════════════════════════════════════════════════════════════
// Jenkins Workshop Init Script
//
// Configures a fresh Jenkins for a workshop:
//   - Switches Security Realm to Jenkins' own user database
//   - Creates workshop-admin (password from WORKSHOP_ADMIN_PW env var)
//   - Creates user1 .. userN (password pattern: bobathon-N)
//   - Applies matrix-based authorization
//
// How it runs:
//   (a) at Jenkins startup via init.groovy.d mount (setup.sh handles this)
//   (b) ad-hoc via Manage Jenkins → Script Console (paste and Run)
//
// Required environment variables (must be set on the Jenkins container):
//   WORKSHOP_ADMIN_PW       admin account password
//   WORKSHOP_USER_COUNT     number of participant accounts (default: 20)
//
// The script is idempotent — safe to re-run.
// ═══════════════════════════════════════════════════════════════════

import jenkins.model.*
import hudson.security.*

def jenkins = Jenkins.instance

// ── Read configuration from environment ────────────────────────────
def adminPw = System.getenv("WORKSHOP_ADMIN_PW")
if (!adminPw || adminPw.trim().isEmpty()) {
    throw new IllegalStateException(
        "WORKSHOP_ADMIN_PW env var is not set. " +
        "Mount it from the jenkins-workshop-admin Secret, or export it " +
        "before running via the Script Console."
    )
}

def userCount = (System.getenv("WORKSHOP_USER_COUNT") ?: "20") as Integer
if (userCount < 1) {
    throw new IllegalStateException("WORKSHOP_USER_COUNT must be >= 1, got ${userCount}")
}

// ── Switch Security Realm to Jenkins' own user database ────────────
def realm = jenkins.getSecurityRealm()
if (!(realm instanceof HudsonPrivateSecurityRealm)) {
    realm = new HudsonPrivateSecurityRealm(false)  // false = no public signup
    jenkins.setSecurityRealm(realm)
    println "[workshop-init] Switched Security Realm to local user database"
}

// ── Admin account ──────────────────────────────────────────────────
if (realm.getUser("workshop-admin") == null) {
    realm.createAccount("workshop-admin", adminPw)
    println "[workshop-init] Created workshop-admin"
} else {
    println "[workshop-init] workshop-admin already exists — skipping"
}

// ── Participant accounts (user1 .. userN) ──────────────────────────
(1..userCount).each { i ->
    def username = "user${i}"
    def password = "bobathon-${i}"
    if (realm.getUser(username) == null) {
        realm.createAccount(username, password)
        println "[workshop-init] Created ${username} / ${password}"
    } else {
        println "[workshop-init] ${username} already exists — skipping"
    }
}

// ── Authorization: matrix-based ────────────────────────────────────
def strategy = new GlobalMatrixAuthorizationStrategy()

// Admin gets everything
strategy.add(Jenkins.ADMINISTER, "workshop-admin")

// Participants can read, build, create, configure, cancel their own jobs
(1..userCount).each { i ->
    def u = "user${i}"
    strategy.add(Jenkins.READ, u)
    strategy.add(hudson.model.Item.READ, u)
    strategy.add(hudson.model.Item.BUILD, u)
    strategy.add(hudson.model.Item.CREATE, u)
    strategy.add(hudson.model.Item.CONFIGURE, u)
    strategy.add(hudson.model.Item.CANCEL, u)
    strategy.add(hudson.model.Item.WORKSPACE, u)
}

jenkins.setAuthorizationStrategy(strategy)
jenkins.save()

println "[workshop-init] Applied: admin + ${userCount} participants, matrix auth enabled"
