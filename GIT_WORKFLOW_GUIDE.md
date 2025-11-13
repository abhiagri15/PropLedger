# Git Workflow Guide

A comprehensive guide for developers working on the PropLedger project with multiple development branches.

## Table of Contents
- [Quick Reference](#quick-reference)
- [Basic Workflow](#basic-workflow)
- [Multi-Developer Workflow](#multi-developer-workflow)
- [Merging to Main Branch](#merging-to-main-branch)
- [Pull Request Workflow](#pull-request-workflow)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Reference

### Essential Commands Cheat Sheet

| Action | Command |
|--------|---------|
| Check current branch | `git branch` or `git status` |
| Switch branch | `git checkout branch-name` |
| Create & switch to new branch | `git checkout -b new-branch-name` |
| Pull latest changes | `git pull origin branch-name` |
| Fetch remote changes | `git fetch origin` |
| Stage all changes | `git add .` |
| Stage specific file | `git add filename` |
| Commit changes | `git commit -m "message"` |
| Push to remote | `git push origin branch-name` |
| Push new branch | `git push -u origin branch-name` |
| Merge branch | `git merge branch-name` |
| Delete local branch | `git branch -d branch-name` |
| Delete remote branch | `git push origin --delete branch-name` |
| View commit history | `git log --oneline` |
| View all branches | `git branch -a` |
| Discard local changes | `git checkout -- filename` |
| Unstage changes | `git reset HEAD filename` |

---

## Basic Workflow

### Standard Feature Development Cycle

```bash
# 1. Start from your development branch
git checkout dev-X
git pull origin dev-X

# 2. Create feature branch
git checkout -b feature/your-feature-name

# 3. Make changes and commit
git add .
git commit -m "Add feature: description"

# 4. Push feature branch (optional but recommended)
git push -u origin feature/your-feature-name

# 5. Merge back to dev branch
git checkout dev-X
git pull origin dev-X
git merge feature/your-feature-name

# 6. Push updated dev branch
git push origin dev-X

# 7. Clean up
git branch -d feature/your-feature-name
git push origin --delete feature/your-feature-name
```

---

## Multi-Developer Workflow

### Scenario: Multiple developers (dev-1, dev-2, dev-3)

Each developer works independently on their own development branch.

### Developer 1 Workflow (dev-1 branch)

```bash
# Start on your branch
git checkout dev-1
git pull origin dev-1

# Create feature branch
git checkout -b feature/add-user-authentication

# Work on feature
# ... make code changes ...
git status
git add .
git commit -m "Add user authentication with JWT tokens"

# Push feature branch
git push -u origin feature/add-user-authentication

# Merge feature to dev-1
git checkout dev-1
git pull origin dev-1
git merge feature/add-user-authentication

# Push updated dev-1
git push origin dev-1

# Clean up
git branch -d feature/add-user-authentication
git push origin --delete feature/add-user-authentication
```

### Developer 2 Workflow (dev-2 branch)

```bash
# Start on your branch
git checkout dev-2
git pull origin dev-2

# Create feature branch
git checkout -b feature/dashboard-redesign

# Work on feature
# ... make code changes ...
git add .
git commit -m "Redesign dashboard with new charts"

# Push feature branch
git push -u origin feature/dashboard-redesign

# Merge feature to dev-2
git checkout dev-2
git pull origin dev-2
git merge feature/dashboard-redesign

# Push updated dev-2
git push origin dev-2

# Clean up
git branch -d feature/dashboard-redesign
git push origin --delete feature/dashboard-redesign
```

### Developer 3 Workflow (dev-3 branch)

```bash
# Start on your branch
git checkout dev-3
git pull origin dev-3

# Create feature branch
git checkout -b feature/payment-integration

# Work on feature
# ... make code changes ...
git add .
git commit -m "Integrate Stripe payment gateway"

# Push feature branch
git push -u origin feature/payment-integration

# Merge feature to dev-3
git checkout dev-3
git pull origin dev-3
git merge feature/payment-integration

# Push updated dev-3
git push origin dev-3

# Clean up
git branch -d feature/payment-integration
git push origin --delete feature/payment-integration
```

---

## Merging to Main Branch

### Scenario: After testing on dev branch, merge to main/master

This is typically done by a team lead or senior developer after code review.

### Option 1: Direct Merge (Simple Projects)

```bash
# 1. Ensure your dev branch is up to date
git checkout dev-1
git pull origin dev-1

# 2. Switch to main branch
git checkout main
git pull origin main

# 3. Merge dev branch into main
git merge dev-1

# 4. Resolve conflicts if any
# (Edit conflicted files, then:)
git add .
git commit

# 5. Push to main
git push origin main

# 6. Tag the release (optional)
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

### Option 2: Merge with Squash (Clean History)

```bash
# 1. Switch to main
git checkout main
git pull origin main

# 2. Merge with squash (combines all commits into one)
git merge --squash dev-1

# 3. Commit the squashed changes
git commit -m "Merge dev-1: Add authentication and dashboard features"

# 4. Push to main
git push origin main
```

### Option 3: Using Rebase (Linear History)

```bash
# 1. Update dev branch
git checkout dev-1
git pull origin dev-1

# 2. Rebase on main
git fetch origin main
git rebase origin/main

# 3. Resolve conflicts if any, then continue
git add .
git rebase --continue

# 4. Force push dev branch (only if it's your personal branch!)
git push origin dev-1 --force

# 5. Switch to main and merge
git checkout main
git pull origin main
git merge dev-1

# 6. Push main
git push origin main
```

### Merging Multiple Dev Branches to Main

When all developers are ready to merge their work:

```bash
# Typically done by team lead

# 1. Start with main
git checkout main
git pull origin main

# 2. Merge dev-1
git merge dev-1
# Resolve conflicts if any
git push origin main

# 3. Merge dev-2
git merge dev-2
# Resolve conflicts if any
git push origin main

# 4. Merge dev-3
git merge dev-3
# Resolve conflicts if any
git push origin main

# 5. Tag release
git tag -a v1.0.0 -m "Release with features from all dev branches"
git push origin v1.0.0
```

---

## Pull Request Workflow

### Using GitHub Pull Requests (Recommended for Teams)

Pull requests allow code review before merging.

### Step 1: Push Your Feature Branch

```bash
# After completing your feature
git checkout feature/your-feature-name
git push -u origin feature/your-feature-name
```

### Step 2: Create Pull Request on GitHub

**Via GitHub Web Interface:**

1. Go to your repository on GitHub
2. Click "Pull requests" tab
3. Click "New pull request"
4. Select base branch (e.g., `dev-1`) and compare branch (e.g., `feature/your-feature-name`)
5. Add title and description
6. Click "Create pull request"
7. Request reviewers
8. Wait for approval

**Via GitHub CLI (gh):**

```bash
# Install GitHub CLI first (if not installed)
# https://cli.github.com/

# Create PR from feature branch to dev branch
gh pr create \
  --base dev-1 \
  --head feature/your-feature-name \
  --title "Add user authentication" \
  --body "This PR adds JWT-based authentication with the following features:
  - Login/logout functionality
  - Token refresh mechanism
  - Protected routes
  "

# List your PRs
gh pr list

# View PR status
gh pr status

# Checkout a PR locally for testing
gh pr checkout 123
```

### Step 3: Code Review Process

```bash
# Reviewers can checkout the PR locally
gh pr checkout 123

# Or manually
git fetch origin pull/123/head:pr-123
git checkout pr-123

# Test the changes
# ... run tests, review code ...

# Comment on GitHub or via CLI
gh pr review 123 --comment -b "Looks good, but please add tests"

# Approve
gh pr review 123 --approve

# Request changes
gh pr review 123 --request-changes -b "Please fix the authentication logic"
```

### Step 4: Update PR Based on Feedback

```bash
# Switch to your feature branch
git checkout feature/your-feature-name

# Make requested changes
# ... edit files ...

# Commit changes
git add .
git commit -m "Address review comments: add authentication tests"

# Push updates (automatically updates PR)
git push origin feature/your-feature-name
```

### Step 5: Merge Pull Request

**Via GitHub Web Interface:**
1. Click "Merge pull request"
2. Choose merge type:
   - **Merge commit**: Keeps all commits
   - **Squash and merge**: Combines all commits into one
   - **Rebase and merge**: Applies commits individually on base branch
3. Click "Confirm merge"
4. Delete branch (optional)

**Via GitHub CLI:**

```bash
# Merge PR
gh pr merge 123

# Merge with squash
gh pr merge 123 --squash

# Merge with rebase
gh pr merge 123 --rebase

# Merge and delete branch
gh pr merge 123 --squash --delete-branch
```

### Step 6: Update Local Repository

```bash
# After PR is merged, update your dev branch
git checkout dev-1
git pull origin dev-1

# Delete local feature branch
git branch -d feature/your-feature-name
```

### Complete PR Workflow Example

```bash
# Developer creates feature
git checkout dev-1
git pull origin dev-1
git checkout -b feature/add-payment

# ... work on feature ...
git add .
git commit -m "Add payment integration"
git push -u origin feature/add-payment

# Create PR (via CLI)
gh pr create --base dev-1 --head feature/add-payment \
  --title "Add Payment Integration" \
  --body "Integrates Stripe payment gateway"

# Reviewer reviews
gh pr checkout 123
# ... test code ...
gh pr review 123 --approve

# Developer merges
gh pr merge 123 --squash --delete-branch

# Developer updates local
git checkout dev-1
git pull origin dev-1
git branch -d feature/add-payment
```

---

## Best Practices

### 1. Branch Naming Conventions

```bash
# Feature branches
feature/add-login
feature/dashboard-redesign
feature/payment-integration

# Bug fixes
bugfix/fix-login-error
bugfix/resolve-database-connection

# Hotfixes (urgent production fixes)
hotfix/critical-security-patch
hotfix/payment-gateway-down

# Enhancements
enhancement/improve-performance
enhancement/update-ui-styling

# Experimental/Research
experiment/test-new-framework
research/evaluate-caching-strategy
```

### 2. Commit Message Best Practices

```bash
# Good commit messages
git commit -m "Add user authentication with JWT"
git commit -m "Fix: Resolve database connection timeout"
git commit -m "Update: Improve dashboard load time by 50%"
git commit -m "Refactor: Simplify payment processing logic"

# Bad commit messages (avoid these)
git commit -m "fix"
git commit -m "updates"
git commit -m "changes"
git commit -m "wip"
```

### 3. Before Starting Work

```bash
# Always pull latest changes
git checkout dev-X
git pull origin dev-X

# Verify you're on the right branch
git branch
git status
```

### 4. Commit Frequently

```bash
# Make small, logical commits
git add file1.py
git commit -m "Add authentication middleware"

git add file2.py
git commit -m "Add user login endpoint"

git add tests/
git commit -m "Add authentication tests"
```

### 5. Keep Feature Branches Updated

```bash
# If working on a feature for multiple days
# Regularly sync with dev branch

git checkout dev-1
git pull origin dev-1

git checkout feature/your-feature
git merge dev-1

# Or use rebase for cleaner history
git rebase dev-1
```

### 6. Never Force Push to Shared Branches

```bash
# ❌ NEVER do this on main or shared dev branches
git push --force origin main
git push --force origin dev-1

# ✅ Only force push on your personal feature branches if needed
git push --force origin feature/your-feature
```

### 7. Protect Important Branches

Configure branch protection on GitHub:
- Go to Settings > Branches
- Add protection rules for `main` and `dev-*` branches
- Enable:
  - Require pull request reviews
  - Require status checks
  - Prevent force pushes
  - Prevent deletion

---

## Troubleshooting

### Merge Conflicts

```bash
# When you see merge conflicts
git merge feature/new-feature
# CONFLICT (content): Merge conflict in app.py

# 1. Check which files have conflicts
git status

# 2. Open conflicted files and look for conflict markers:
#    <<<<<<< HEAD
#    Your current code
#    =======
#    Incoming changes
#    >>>>>>> feature/new-feature

# 3. Edit file to resolve conflict

# 4. Stage resolved files
git add app.py

# 5. Complete merge
git commit

# 6. Push changes
git push origin dev-1
```

### Undo Last Commit (Not Pushed)

```bash
# Keep changes in working directory
git reset --soft HEAD~1

# Remove changes completely
git reset --hard HEAD~1
```

### Undo Last Commit (Already Pushed)

```bash
# Create new commit that reverses changes
git revert HEAD
git push origin dev-1
```

### Accidentally Committed to Wrong Branch

```bash
# You committed to dev-1 but meant to create feature branch

# 1. Create feature branch from current state
git branch feature/my-feature

# 2. Reset dev-1 to before your commits
git reset --hard origin/dev-1

# 3. Switch to feature branch
git checkout feature/my-feature

# Your commits are now on the feature branch!
```

### Discard All Local Changes

```bash
# Discard all uncommitted changes
git reset --hard HEAD

# Remove untracked files
git clean -fd
```

### View What Changed

```bash
# See unstaged changes
git diff

# See staged changes
git diff --cached

# See changes between branches
git diff dev-1..feature/new-feature

# See commit history with changes
git log -p

# See who changed what
git blame filename
```

### Stash Changes Temporarily

```bash
# Save current changes temporarily
git stash

# Switch branches and do other work
git checkout other-branch

# Come back and restore changes
git checkout original-branch
git stash pop

# List stashes
git stash list

# Apply specific stash
git stash apply stash@{0}
```

### Sync Forked Repository

```bash
# Add upstream remote (original repo)
git remote add upstream https://github.com/original/repo.git

# Fetch upstream changes
git fetch upstream

# Merge upstream changes
git checkout main
git merge upstream/main

# Push to your fork
git push origin main
```

---

## Workflow Diagrams

### Feature Development Flow

```
dev-1 (your dev branch)
  │
  ├── git checkout -b feature/new-feature
  │
feature/new-feature
  │
  ├── (make changes)
  ├── git add .
  ├── git commit
  ├── git push -u origin feature/new-feature
  │
  ├── git checkout dev-1
  ├── git merge feature/new-feature
  │
dev-1 (updated)
  │
  └── git push origin dev-1
```

### Multi-Dev to Main Flow

```
main
  │
  ├── dev-1 ──┬── feature/auth ──┐
  │           └── feature/api ───┤
  │                             ├── merge to dev-1
  │                             │
  ├── dev-2 ──┬── feature/ui ───┐
  │           └── feature/css ──┤
  │                             ├── merge to dev-2
  │                             │
  ├── dev-3 ──┬── feature/db ───┐
  │           └── feature/test ─┤
  │                             ├── merge to dev-3
  │                             │
  ├── (after testing)           │
  ├── merge dev-1 ──────────────┤
  ├── merge dev-2 ──────────────┤
  ├── merge dev-3 ──────────────┤
  │                             │
main (updated with all features)
  │
  └── git tag v1.0.0
```

---

## Additional Resources

### Git Configuration

```bash
# Set your identity
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default editor
git config --global core.editor "vim"

# Enable color output
git config --global color.ui auto

# Set default branch name
git config --global init.defaultBranch main

# View all config
git config --list
```

### Useful Aliases

```bash
# Add helpful aliases
git config --global alias.st status
git config --global alias.co checkout
git config --global alias.br branch
git config --global alias.ci commit
git config --global alias.unstage 'reset HEAD --'
git config --global alias.last 'log -1 HEAD'
git config --global alias.visual 'log --oneline --graph --decorate --all'

# Now you can use
git st          # instead of git status
git co dev-1    # instead of git checkout dev-1
git visual      # pretty branch visualization
```

### Learn More

- Official Git Documentation: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com/
- GitHub CLI: https://cli.github.com/
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf

---

## Summary

### Quick Workflow for Daily Work

```bash
# Morning: Start work
git checkout dev-X
git pull origin dev-X
git checkout -b feature/new-thing

# During day: Save work
git add .
git commit -m "Descriptive message"
git push -u origin feature/new-thing

# End of day: Merge if complete
git checkout dev-X
git pull origin dev-X
git merge feature/new-thing
git push origin dev-X
git branch -d feature/new-thing
```

### Remember

1. ✅ **Always pull before starting work**
2. ✅ **Create feature branches for new work**
3. ✅ **Write clear commit messages**
4. ✅ **Push your work regularly**
5. ✅ **Use pull requests for code review**
6. ❌ **Never force push to shared branches**
7. ❌ **Never commit directly to main**
8. ❌ **Never commit sensitive data**

Happy coding! 🚀
