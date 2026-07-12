"""One-time LOCAL OAuth setup: mint a Gmail refresh token for headless use.

Usage:
    1. Put your downloaded OAuth client file next to this script as credentials.json
       (Google Cloud -> APIs & Services -> Credentials -> Desktop OAuth client).
    2. python auth_setup.py
    3. A browser opens; approve access to your Gmail (read-only).
    4. Copy the printed values into your .env / GitHub secrets.
"""
import os

from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "credentials.json"


def main():
    if not os.path.exists(CREDENTIALS_FILE):
        raise SystemExit(
            f"'{CREDENTIALS_FILE}' not found. Download your Desktop OAuth client JSON "
            "from Google Cloud Console and save it here as credentials.json."
        )

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")

    if not creds.refresh_token:
        raise SystemExit(
            "No refresh token returned. Delete prior consent and re-run "
            "(the flow requests prompt=consent to force one)."
        )

    values = {
        "GMAIL_CLIENT_ID": creds.client_id,
        "GMAIL_CLIENT_SECRET": creds.client_secret,
        "GMAIL_REFRESH_TOKEN": creds.refresh_token,
    }
    _write_env(values)
    print("\nGmail auth OK. Wrote GMAIL_CLIENT_ID / SECRET / REFRESH_TOKEN to .env")
    print("(secrets not shown here). Do NOT commit .env.")


def _write_env(values: dict):
    """Create/update .env in-place with the given keys (no secrets printed)."""
    path = ".env"
    lines = []
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

    keys = set(values)
    out = []
    for line in lines:
        key = line.split("=", 1)[0].strip() if "=" in line else ""
        if key in keys:
            out.append(f"{key}={values.pop(key)}")
        else:
            out.append(line)
    for k, v in values.items():  # any not already present
        out.append(f"{k}={v}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
