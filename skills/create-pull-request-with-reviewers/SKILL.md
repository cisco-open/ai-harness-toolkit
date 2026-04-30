---
name: create-pull-request-with-reviewers
description: Create a pull request with automatically recommended reviewers based on git history. Use this skill when the user wants to create a PR with reviewers, open a pull request, or submit changes for review with the right people assigned.
compatibility: Requires git and GitHub CLI (gh) to be installed
metadata:
  repository: ""
  defaultReviewer: ""
  jiraBaseUrl: ""
  version: "1.0"
---

# Create Pull Request with Reviewers

## Setup

Before using this skill, check if any metadata fields are empty strings. If any are empty:
1. Prompt the user to provide the missing values (only prompt for fields that are empty):
   - `repository`: GitHub repository in format "org/repo"
   - `defaultReviewer`: Default reviewer GitHub username to use if no reviewers found
2. Update the SKILL.md frontmatter with the provided values so they don't need to configure again

## Instructions

1. **Get Changed Files**

Get files changed between current branch and main:

```bash
git diff --name-only origin/main...HEAD
```

2. **Analyze Git History for Reviewers**

For each changed file, find contributors with commit counts and recency:

```bash
git log --format='%an|%ar' -- <file> | sort | uniq -c | sort -rn | head -10
```

Run this for each file from Step 1 to build per-file reviewer data.

3. **Get Eligible Collaborators**

Get collaborators who can review:

```bash
gh api /repos/<metadata.repository>/collaborators --jq '.[].login'
```

Omit generic/service accounts (usernames matching common bot or service-account patterns).

4. **Get Current User**

Get the current git user to exclude from reviewers:

```bash
git config user.name
```

5. **Rank Reviewers**

- Match git history contributors with GitHub collaborators
- **Exclude** the current user (PR author) from recommendations
- Rank by number of commits to the affected files
- Select **up to 3** reviewers (default to metadata.defaultReviewer if none found)

6. **Analyze Changes for PR Content**

Understand the changes to generate PR details:

```bash
git log main..HEAD --oneline
git diff main...HEAD --stat
git diff main...HEAD
```

7. **Generate PR Details**

Generate PR title using format: `JIRA-KEY - Verb + description`

Extract Jira keys from commit messages or branch name.

Generate description using this template:

```markdown
## 🚀 Description, Motivation, and Context
<summary of changes>

## 📖 Issues and Related PRs
- [JIRA-KEY](<metadata.jiraBaseUrl>/browse/JIRA-KEY)

## 🌮 Required Items Complete:
- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Coverage verified
- [ ] Functionally tested
- [ ] Deployable to production
- [ ] Uses feature flags
- [ ] README updated
- [ ] Build passes
```

8. **Present for Confirmation**

Present both the PR details and reviewer recommendations:

```markdown
🚀 **Ready to Create PR**

**Title:** EADL-1234 - Add circuit breaker retry logic

**Description:**
## 🚀 Description, Motivation, and Context
Adds circuit breaker pattern with configurable retry logic for LLM calls.

## 📖 Issues and Related PRs
- [EADL-1234](<metadata.jiraBaseUrl>/browse/EADL-1234)

---

🎯 **Recommended Reviewers (based on git history):**

**alice** (3/3 files, 33 total commits)
| File | Commits | Last Active |
|------|---------|-------------|
| circuit.py | 23 | 1 week ago |
| llm_factory.py | 6 | 1 month ago |
| test_circuit.py | 4 | 3 months ago |

**bob** (2/3 files, 23 total commits)
| File | Commits | Last Active |
|------|---------|-------------|
| llm_factory.py | 15 | 3 weeks ago |
| circuit.py | 8 | 2 months ago |

**carol** (1/3 files, 12 total commits)
| File | Commits | Last Active |
|------|---------|-------------|
| test_circuit.py | 12 | 2 weeks ago |

---

Create PR with these reviewers? [Y/n]
```

9. **Create PR with Reviewers**

After user confirms, create the PR with reviewers in one command:

```bash
gh pr create \
  --repo <metadata.repository> \
  --base main \
  --head "$(git branch --show-current)" \
  --title "TITLE" \
  --body "BODY" \
  --reviewer <reviewer1>,<reviewer2>,<reviewer3>
```

10. **Display PR Link**

After creating the PR, display the URL as a clickable hyperlink so the user can easily navigate to it.
