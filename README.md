# Lazy Me — Daily Gmail Digest Bot

Reads **today's** Gmail, sorts it into buckets (job rejections, interviews, ads,
bills, personal, newsletters…) with **Gemini**, and pushes a tidy summary to
**Telegram**. Runs itself daily on **GitHub Actions** — no PC needed.

```
Gmail API (today's mail)  ->  Gemini (classify + summarize)  ->  Telegram
```

## Layout

```
auth_setup.py                 one-time local script to mint a Gmail refresh token
src/
  main.py                     orchestrator (fetch -> categorize -> send)
  config.py                   env vars, categories, timezone
  gmail_client.py             Gmail API auth + fetch today's mail
  categorize.py               Gemini classify + summarize -> JSON
  telegram_client.py          send to Telegram Bot API
.github/workflows/digest.yml  daily cron + manual trigger
```

## One-time setup

### 1. Google Cloud (Gmail access)
1. [console.cloud.google.com](https://console.cloud.google.com/) → new project.
2. **APIs & Services → Library** → enable **Gmail API**.
3. **OAuth consent screen** → External → add your own email as a **Test user**.
4. **Credentials → Create credentials → OAuth client ID → Desktop app** → download
   the JSON, save it in this folder as `credentials.json`.

### 2. Mint the refresh token (local, once)
```bash
python -m venv .venv && . .venv/Scripts/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python auth_setup.py
```
A browser opens → approve read-only Gmail access → the script prints
`GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`.

### 3. Gemini key
Get one at [aistudio.google.com/apikey](https://aistudio.google.com/apikey).

### 4. Telegram bot
1. Message **@BotFather** → `/newbot` → copy the **bot token**.
2. Send any message to your new bot.
3. Message **@userinfobot** (or open
   `https://api.telegram.org/bot<TOKEN>/getUpdates`) to get your numeric **chat id**.

### 5. Fill `.env`
```bash
cp .env.example .env   # then paste the values from steps 2–4
```

## Test locally
```bash
python src/main.py --dry-run                 # today, print only, sends nothing
python src/main.py                           # today, actually sends to Telegram
python src/main.py --date yesterday          # yesterday's mail
python src/main.py --date 2026-07-10          # a specific day (YYYY-MM-DD)
python src/main.py --date yesterday --dry-run # combine flags
```
`--date` accepts `today` (default), `yesterday`, or `YYYY-MM-DD`, in `DIGEST_TIMEZONE`.
The daily GitHub Actions run always digests **today**.

## Deploy (GitHub Actions)
1. Push this repo to GitHub.
2. **Settings → Secrets and variables → Actions → New repository secret** — add:
   `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REFRESH_TOKEN`,
   `GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
3. **Actions** tab → **Daily Gmail Digest** → **Run workflow** to test now.
4. It then runs automatically every day at **21:00 IST** (`30 15 * * *` UTC).
   Change the time in [`.github/workflows/digest.yml`](.github/workflows/digest.yml).

## Customize
- **Categories:** edit `CATEGORIES` in [`src/config.py`](src/config.py).
- **Timezone / schedule:** `DIGEST_TIMEZONE` env + the cron in the workflow.
- **Quiet on empty days:** set `SEND_ON_EMPTY=false`.

## Notes
- Gmail scope is **read-only** (`gmail.readonly`) — the bot can't send or delete.
- Secrets live only in `.env` (git-ignored) and GitHub Actions secrets.
