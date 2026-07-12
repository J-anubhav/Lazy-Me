"""Gmail API: build credentials from a refresh token and fetch today's mail."""
import base64
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

import config


def _service():
    creds = Credentials(
        token=None,
        refresh_token=config.GMAIL_REFRESH_TOKEN,
        client_id=config.GMAIL_CLIENT_ID,
        client_secret=config.GMAIL_CLIENT_SECRET,
        token_uri=config.GMAIL_TOKEN_URI,
        scopes=config.GMAIL_SCOPES,
    )
    # google-auth refreshes the access token automatically on first API call.
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def resolve_date(spec: str | None):
    """Turn a date spec into a date in the configured tz.

    Accepts None/'today', 'yesterday', or 'YYYY-MM-DD'. Returns a date object.
    """
    tz = ZoneInfo(config.DIGEST_TIMEZONE)
    today = datetime.now(tz).date()
    if not spec or spec.lower() == "today":
        return today
    if spec.lower() == "yesterday":
        return today - timedelta(days=1)
    try:
        return datetime.strptime(spec, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit(
            f"Bad --date '{spec}'. Use 'today', 'yesterday', or YYYY-MM-DD."
        )


def _day_window(day):
    """Return (start_epoch, end_epoch) covering the given date in the configured tz."""
    tz = ZoneInfo(config.DIGEST_TIMEZONE)
    start = datetime(day.year, day.month, day.day, tzinfo=tz)
    end = start + timedelta(days=1)
    return int(start.timestamp()), int(end.timestamp())


def _header(headers, name, default=""):
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", default)
    return default


def _extract_body(payload) -> str:
    """Walk the MIME tree and return the first text/plain body found."""
    if not payload:
        return ""
    mime = payload.get("mimeType", "")
    body = payload.get("body", {})
    data = body.get("data")
    if mime == "text/plain" and data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    for part in payload.get("parts", []) or []:
        text = _extract_body(part)
        if text:
            return text
    # Fall back to any text/html so we at least have something.
    if mime == "text/html" and data:
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    return ""


def fetch_for_date(day):
    """Return a list of {from, subject, snippet} for the given date's messages."""
    service = _service()
    start, end = _day_window(day)
    query = f"after:{start} before:{end}"

    ids = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token, maxResults=100)
            .execute()
        )
        ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    emails = []
    for mid in ids:
        msg = (
            service.users()
            .messages()
            .get(userId="me", id=mid, format="full")
            .execute()
        )
        payload = msg.get("payload", {})
        headers = payload.get("headers", [])
        body = _extract_body(payload) or msg.get("snippet", "")
        body = " ".join(body.split())  # collapse whitespace
        emails.append(
            {
                "from": _header(headers, "From"),
                "subject": _header(headers, "Subject", "(no subject)"),
                "snippet": body[: config.BODY_TRUNCATE],
            }
        )
    return emails
