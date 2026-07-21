<!--
⚠️ Never include tokens, .env contents, credentials.json, or real email content
in this PR — it is public and permanent in git history.
-->

## What this changes

<!-- One or two sentences. What does the user get that they didn't have before? -->

## Why

<!-- Link the issue if there is one: Closes #123 -->

## How it was tested

<!-- Check what you actually did. -->

- [ ] `python -m unittest discover tests` passes
- [ ] Added or updated tests for this change
- [ ] Ran `python src/main.py --dry-run` against a real inbox
- [ ] Tested the Telegram bot path (`python src/bot.py`)
- [ ] Docs only — no code change

## Security checklist

<!-- Every box must be true, or explain below why it doesn't apply. -->

- [ ] Doesn't widen the Gmail OAuth scope past `gmail.modify`
- [ ] Doesn't add a permanent-delete path (Trash only)
- [ ] Email-derived text is escaped before it reaches Telegram
- [ ] Doesn't weaken the callback authorization check in `src/bot.py`
- [ ] Doesn't send email content anywhere the user didn't configure
- [ ] New dependencies are pinned in `requirements.txt` (and justified below)
- [ ] No secrets, tokens, or personal email content in the diff

## Anything reviewers should know

<!-- Trade-offs, follow-up work, things you're unsure about. -->
