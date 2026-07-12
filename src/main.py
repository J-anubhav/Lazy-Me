"""Lazy Me — fetch today's Gmail, categorize with Gemini, push to Telegram."""
import argparse
import sys

# Emojis in the digest break the default Windows console (cp1252); force UTF-8.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

from collections import OrderedDict
from datetime import datetime
from zoneinfo import ZoneInfo

import categorize as categorize_mod
import config
import gmail_client
import telegram_client as tg


def build_digest(emails, result, day=None) -> str:
    """Format the categorized emails into a Telegram-HTML digest string."""
    tz = ZoneInfo(config.DIGEST_TIMEZONE)
    day = day or datetime.now(tz).date()
    label = day.strftime("%A, %d %b %Y")

    if not emails:
        return f"<b>📭 Lazy Me — {label}</b>\nNo mail on {label}. Enjoy the quiet."

    # Group email one-liners by category, preserving CATEGORIES order.
    grouped = OrderedDict((c, []) for c in config.CATEGORIES)
    for item in result.get("emails", []):
        cat = item.get("category", "Other/Important")
        if cat not in grouped:
            grouped[cat] = []
        summary = item.get("summary", "").strip()
        idx = item.get("index")
        if summary:
            grouped[cat].append(summary)
        elif isinstance(idx, int) and 0 <= idx < len(emails):
            e = emails[idx]
            grouped[cat].append(f"{e['subject']} — {e['from']}")

    digests = result.get("category_digests", {})

    lines = [f"<b>📬 Lazy Me — {label}</b>", f"{len(emails)} mail.\n"]
    for cat, items in grouped.items():
        if not items:
            continue
        lines.append(f"<b>{tg.esc(cat)}</b> ({len(items)})")
        blurb = digests.get(cat, "").strip()
        if blurb:
            lines.append(f"<i>{tg.esc(blurb)}</i>")
        for s in items:
            lines.append(f"• {tg.esc(s)}")
        lines.append("")
    return "\n".join(lines).strip()


def main():
    parser = argparse.ArgumentParser(description="Lazy Me daily Gmail digest.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the digest to stdout instead of sending to Telegram.",
    )
    parser.add_argument(
        "--date",
        default="today",
        help="Which day to digest: 'today' (default), 'yesterday', or YYYY-MM-DD.",
    )
    args = parser.parse_args()

    config.require("GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN")
    if not args.dry_run:
        config.require("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")

    day = gmail_client.resolve_date(args.date)
    print(f"Fetching mail for {day.isoformat()}...")
    emails = gmail_client.fetch_for_date(day)
    print(f"Fetched {len(emails)} email(s).")

    if not emails and not config.SEND_ON_EMPTY:
        print("No mail and SEND_ON_EMPTY is false; nothing to do.")
        return

    if emails:
        config.require("GEMINI_API_KEY")
        print("Categorizing with Gemini...")
        result = categorize_mod.categorize(emails)
    else:
        result = {"emails": [], "category_digests": {}}

    digest = build_digest(emails, result, day)

    if args.dry_run:
        print("\n----- DIGEST (dry-run) -----\n")
        print(digest)
        return

    print("Sending to Telegram...")
    tg.send(digest)
    print("Done.")


if __name__ == "__main__":
    main()
