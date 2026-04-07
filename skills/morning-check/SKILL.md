---
name: morning-check
description: Check Gmail inbox and GitHub repo activity on a schedule. Use when Stone asks to set up morning/afternoon email and git checks, or when running scheduled inbox + repo status checks. Runs silently (no output) when nothing new is found; reports new emails, comments, or issues when found.
---

# morning-check

Check Gmail unread emails and GitHub repo notifications/comments. Reports only when new activity is found.

## Gmail Check

Use `gog gmail messages search` (not `gog gmail search`) to get per-message results:

```bash
gog gmail messages search "in:inbox is:unread" --max 20 --account $GMAIL_ACCOUNT
```

Filter by `newer_than:1h` to avoid re-reporting old unread emails.

## GitHub Check

Use the Moltbook/MoltGitHub API to check:
- New comments on repos
- New issues / issue comments
- Review requests

```bash
# Check notifications via GitHub API (unauthenticated for public repos)
curl -s "https://api.github.com/repos/$REPO/notifications" | jq '.[] | select(.reason != "author") | {repo: .repository.full_name, type: .subject.type, title: .subject.title, url: .subject.url}'
```

For GitHub comments on issues/PRs, poll each repo's issue comments endpoint. Check ALL StarbugMolt repos:
- StarbugMolt/starbug-website
- StarbugMolt/pz-rcon-skill
- StarbugMolt/starbugmolt.github.io

```bash
# Check notifications across all repos (unauthenticated for public repos)
for REPO in StarbugMolt/starbug-website StarbugMolt/pz-rcon-skill StarbugMolt/starbugmolt.github.io; do
  curl -s "https://api.github.com/repos/$REPO/notifications" | jq '.[] | select(.reason != "author") | {repo: .repository.full_name, type: .subject.type, title: .subject.title}'
done
```

For GitHub comments on issues/PRs, poll each repo's issue comments endpoint:
```bash
curl -s "https://api.github.com/repos/$REPO/issues/comments?per_page=10&sort=created&direction=desc" | jq '.[] | {user: .user.login, body: .body[0:200], created: .created_at, url: .html_url}'
```

## Report Format

If new activity found, format report as:

```
📧 **Gmail** (N new)
- From: <sender> | Subject: <subject> | Preview: <first line>
- ...

🐙 **GitHub** (N new)
- <repo>#<number> @<user>: <comment preview>
- ...
```

If nothing new: output `NO_REPLY` (no message, silent skip).

## Security Rules

- **Never hardcode secrets** in this skill or any script it calls.
- API tokens / credentials → `~/.env` or environment variables only.
- If a script needs credentials, pass them via env vars, never as args.
- When in doubt: ask Stone before pushing anything.
