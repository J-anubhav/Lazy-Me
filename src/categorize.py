"""Gemini: classify each email into a category and write short summaries."""
import json

from google import genai
from google.genai import types

import config

_PROMPT = """You are an email triage assistant. Classify each email into EXACTLY ONE
of these categories:
{categories}

For every email, write a one-line summary (max ~15 words) capturing what it is and
any action needed. Then write a brief overall digest per non-empty category.

Return ONLY JSON of this shape:
{{
  "emails": [
    {{"index": 0, "category": "<one category>", "summary": "<one line>"}}
  ],
  "category_digests": {{
    "<category>": "<1-2 sentence summary of that bucket>"
  }}
}}

Emails:
{emails}
"""


def heuristic(email) -> str:
    """Rule-based category from sender + subject. Used when no LLM is available.

    Order matters: more specific rules first.
    """
    text = f"{email.get('subject','')} {email.get('snippet','')}".lower()
    sender = email.get("from", "").lower()

    def has(*words):
        return any(w in text for w in words)

    # Job — Rejection
    if has(
        "unfortunately",
        "we regret",
        "not moving forward",
        "not be moving",
        "not selected",
        "other candidates",
        "decided not to proceed",
        "will not be progressing",
        "unsuccessful",
    ):
        return "Job — Rejection"

    # Job — Interview/Progress
    if has(
        "interview",
        "shortlisted",
        "next round",
        "assessment",
        "coding test",
        "online test",
        "schedule a call",
        "availability",
        "hackerrank",
        "technical round",
        "moving forward with your",
    ):
        return "Job — Interview/Progress"

    # Job — Application Received
    if has(
        "application received",
        "thank you for applying",
        "we received your application",
        "your application has been received",
        "successfully applied",
        "application submitted",
    ):
        return "Job — Application Received"

    # Job — Listings/Alerts (job boards pushing openings)
    if (
        any(s in sender for s in ("jobalerts", "jobs-noreply", "match.indeed", "naukri"))
        or has("is hiring", "new job", "jobs for you", "job alert", "we found jobs", "apply now")
    ):
        return "Job — Listings/Alerts"

    # Finance/Bills
    if has(
        "invoice",
        "payment",
        "receipt",
        "bill",
        "statement",
        "transaction",
        "credited",
        "debited",
        "refund",
        "subscription renew",
    ):
        return "Finance/Bills"

    # Newsletters
    if (
        any(s in sender for s in ("daily.dev", "substack", "medium", "newsletter", "digest"))
        or has("newsletter", "your daily", "weekly digest")
    ):
        return "Newsletters"

    # Personal / networking
    if has(
        "accepted your invitation",
        "wants to connect",
        "want to connect",
        "add ",
        "reacted to",
        "shared their thoughts",
        "invitation to connect",
        "new connection",
    ):
        return "Personal"

    # Ads/Promotions
    if has(
        "% off",
        "sale",
        "discount",
        "deal",
        "stipend",
        "earn ",
        "up for grabs",
        "limited time",
        "offer",
        "coupon",
        "win ",
    ):
        return "Ads/Promotions"

    return "Other/Important"


def _fallback(emails):
    """No-LLM path: classify by rules so tags still work; summary = clean subject."""
    return {
        "emails": [
            {
                "index": i,
                "category": heuristic(e),
                "summary": e.get("subject", "").strip() or "(no subject)",
            }
            for i, e in enumerate(emails)
        ],
        "category_digests": {},
    }


def categorize(emails):
    """Return {emails: [...], category_digests: {...}}.

    Uses Gemini when a key is set; otherwise falls back to the rule-based
    heuristic (free, no API) so tags still work.
    """
    if not emails:
        return {"emails": [], "category_digests": {}}

    if not config.GEMINI_API_KEY:
        print("[categorize] No GEMINI_API_KEY; using rule-based heuristic.")
        return _fallback(emails)

    compact = [
        {"index": i, "from": e["from"], "subject": e["subject"], "snippet": e["snippet"]}
        for i, e in enumerate(emails)
    ]
    prompt = _PROMPT.format(
        categories="\n".join(f"- {c}" for c in config.CATEGORIES),
        emails=json.dumps(compact, ensure_ascii=False, indent=2),
    )

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        resp = client.models.generate_content(
            model=config.GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        data = json.loads(resp.text)
        if not isinstance(data.get("emails"), list):
            raise ValueError("missing 'emails' list")
        return data
    except Exception as exc:  # noqa: BLE001 - never let triage crash the digest
        print(f"[categorize] Gemini failed ({exc}); using fallback.")
        return _fallback(emails)
