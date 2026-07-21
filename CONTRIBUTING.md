# Contributing to Lazy Me

Thanks for wanting to help. This project sorts people's real inboxes and can
move their real mail to Trash, so the bar for changes is "would I run this
against my own Gmail?" Everything below exists to keep that answer yes.

New here? Look for issues labelled [`good first issue`](https://github.com/J-anubhav/Laze-Me/labels/good%20first%20issue).

---

## Ways to contribute

- **Heuristic rules** — teach the free sorter about senders it gets wrong. The
  easiest useful PR: add patterns to `heuristic()` in [`src/categorize.py`](src/categorize.py).
- **Categories** — add a bucket to `CATEGORY_META` in [`src/config.py`](src/config.py).
- **Delivery channels** — Discord, WhatsApp, Slack. Mirror the shape of
  [`src/telegram_client.py`](src/telegram_client.py).
- **Bug fixes** — with a test that fails before your fix and passes after.
- **Docs** — if something confused you, it confuses others. Fix it.

Please open an issue before starting anything large (a new delivery channel, a
new storage backend, a refactor). It's no fun to write a big PR that gets
declined on direction.

---

## Setting up

```bash
git clone https://github.com/YOUR-USERNAME/Laze-Me.git
cd Laze-Me
python -m venv .venv
. .venv/Scripts/activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in your own values
```

You do **not** need Gmail or Telegram credentials to run the test suite — every
external call is mocked. You only need real credentials to run the digest itself.

## Running the tests

```bash
python -m unittest discover tests -v
```

All 61 tests must pass before you open a PR. CI runs the same suite on Python
3.9 and 3.12; a red build blocks the merge.

To check your change end to end without sending anything:

```bash
python src/main.py --dry-run
```

## Adding tests

Every behaviour change needs a test in [`tests/test_lazy_me.py`](tests/test_lazy_me.py).
Tests use stdlib `unittest` and `unittest.mock` only — please don't add pytest
or other test dependencies.

Two rules specific to this repo:

- **Never let a test hit the network.** Mock the Gmail, Telegram, and Gemini
  clients. A test that needs credentials can't run in CI.
- **Security behaviour needs a regression test.** If you touch authorization,
  the token store, or anything that decides what gets trashed, add a test that
  fails if the protection is removed. See `BotAuthTests` for the pattern.

---

## Security-sensitive areas

These parts of the codebase have deliberate protections. Changes here get
reviewed closely — please explain your reasoning in the PR description.

| Area | The protection | Don't break it by |
|---|---|---|
| [`src/bot.py`](src/bot.py) `_authorized()` | Checks both the chat id **and** the tapping user's id | Dropping the `from.id` check — in a group chat that lets any member trash the owner's mail |
| [`src/categorize.py`](src/categorize.py) `_PROMPT` | Marks email text as untrusted data | Removing the guard, or interpolating email content outside the delimited block |
| [`src/config.py`](src/config.py) `TRASH_EXEMPT` | Keeps `Other/Important` off the bulk-trash button | Adding a trash button to a category the LLM can route important mail into |
| [`src/state.py`](src/state.py) | Tokens expire, are single-use, and writes are atomic | Removing the TTL, or reusing a token after it's consumed |
| [`src/gmail_client.py`](src/gmail_client.py) | Uses the `TRASH` label, never a hard delete | Switching to `messages().delete()` — that is unrecoverable |
| [`src/main.py`](src/main.py) | Escapes all email-derived text before Telegram | Building message HTML without `tg.esc()` |

**Never widen the Gmail scope past `gmail.modify`.** That scope can trash
(recoverable ~30 days) but cannot permanently delete. Any PR requesting
`https://mail.google.com/` or `gmail.settings.*` will be declined.

---

## Pull request process

1. Fork, then branch from `main`: `git checkout -b feat/short-description`
2. Make your change. Keep it focused — one concern per PR.
3. Add or update tests. Run the suite.
4. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
5. Push and open a PR against `main`. Fill in the template.
6. CI must be green and one maintainer must approve before merge.

Direct pushes to `main` are blocked for everyone, including maintainers. All
changes go through a PR.

### What gets a PR declined

- Adds a runtime dependency without a clear justification (this project is
  deliberately light — stdlib plus the Google/Telegram clients)
- Sends telemetry, analytics, or any email content to a third party the user
  didn't configure
- Widens OAuth scope, or adds a hard-delete path
- Removes a security protection listed above without replacing it
- Unpins a dependency or an action SHA in `requirements.txt` / workflows

## Style

Match the surrounding code. Practically: 4-space indent, `snake_case`,
docstrings on modules and non-obvious functions, comments that explain *why*
rather than *what*. No formatter is enforced — just don't reformat files you
aren't otherwise changing, since it buries the real diff.

## Reporting security issues

Don't open a public issue. See [SECURITY.md](SECURITY.md).

## License

By contributing you agree your work is licensed under the [MIT License](LICENSE).
