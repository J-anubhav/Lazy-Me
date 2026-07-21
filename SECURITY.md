# Security Policy

Lazy Me holds an OAuth refresh token for someone's Gmail and can move their mail
to Trash. Security reports are taken seriously.

## Reporting a vulnerability

**Please do not open a public issue for a security problem.**

Report it privately via GitHub's
[private vulnerability reporting](https://github.com/J-anubhav/Laze-Me/security/advisories/new)
(Security tab → Report a vulnerability). If that's unavailable, email
**anubhavjha.dev@gmail.com** with `[SECURITY]` in the subject.

Please include:

- What the issue is and roughly how bad you think it is
- Steps to reproduce, or a proof of concept
- Affected files or functions if you know them

You can expect an acknowledgement within about 72 hours and an assessment within
a week. This is a hobby project maintained by one person, so please be patient.
Fixes ship as soon as practical; I'll credit you in the release notes unless you
prefer otherwise. Please give me a reasonable window to fix before publishing.

## Supported versions

Only the current `main` branch is supported. There are no backports.

## Threat model

**Handled:**

| Threat | Mitigation |
|---|---|
| Malicious email content steering the AI classifier | The prompt marks email text as untrusted data and instructs the model to ignore embedded commands; `Other/Important` never gets a bulk-trash button |
| Sender name spoofing | Digest cards show the real email address next to the display name |
| HTML injection into Telegram messages | All email-derived text is escaped with `html.escape` |
| Someone else tapping your Trash buttons | Callbacks are checked against both `TELEGRAM_CHAT_ID` and `TELEGRAM_OWNER_ID` |
| Replayed or stale Trash buttons | Tokens are single-use and expire after 3 days |
| Accidental permanent deletion | Gmail scope is capped at `gmail.modify`; deletes go to Trash (recoverable ~30 days) |
| Dependency supply chain | `requirements.txt` is fully pinned; GitHub Actions are pinned to commit SHAs |
| CI token abuse | Workflows declare least-privilege `permissions:` |

**Out of scope — you own these:**

- **Your `.env` file and `credentials.json`.** They are git-ignored, but anyone
  with filesystem access to them has your Gmail. Don't commit, paste, or share them.
- **Your GitHub Actions secrets.** Anyone with write access to the repo can read
  them via a workflow. Don't give write access to people you don't trust.
- **Your Telegram bot token.** Whoever holds it can read your digests.
- **The self-hosted deployment.** If you run `src/bot.py` on a shared machine,
  its environment is as exposed as that machine.
- **Google and Telegram themselves.** Report issues in their platforms to them.

## If you fork this project

- Generate your **own** OAuth client and bot token. Never reuse someone else's.
- Keep the consent screen restricted to your own Google account unless you know
  what publishing it means.
- If you make your fork public, verify `.env` and `credentials.json` were never
  committed: `git log --all --name-only --diff-filter=A | grep -E '\.env$|credentials'`
- If a token ever leaks, revoke it immediately at
  [Google Account permissions](https://myaccount.google.com/permissions), and
  rotate the bot token with [@BotFather](https://t.me/BotFather) `/revoke`.
