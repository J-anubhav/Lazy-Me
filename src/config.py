"""Configuration: env vars, categories, timezone."""
import os

from dotenv import load_dotenv

load_dotenv()

# --- Gmail OAuth (built from a refresh token, no browser needed at runtime) ---
GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN", "")
GMAIL_TOKEN_URI = "https://oauth2.googleapis.com/token"
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# --- LLM (OpenAI) ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# --- Behavior ---
DIGEST_TIMEZONE = os.environ.get("DIGEST_TIMEZONE", "Asia/Kolkata")
# Max chars of each email body sent to the LLM (keeps token usage low).
BODY_TRUNCATE = int(os.environ.get("BODY_TRUNCATE", "500"))
# Send a message even when the inbox had no mail for the day.
SEND_ON_EMPTY = os.environ.get("SEND_ON_EMPTY", "true").lower() == "true"

# Ordered category list. Gemini must pick exactly one of these per email.
CATEGORIES = [
    "Job — Rejection",
    "Job — Interview/Progress",
    "Job — Application Received",
    "Finance/Bills",
    "Ads/Promotions",
    "Personal",
    "Newsletters",
    "Other/Important",
]


def require(*names: str) -> None:
    """Fail fast with a clear message if a required env var is missing."""
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise SystemExit(
            "Missing required environment variables: "
            + ", ".join(missing)
            + "\nSet them in a local .env (see .env.example) or as GitHub secrets."
        )
