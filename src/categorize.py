"""OpenAI: classify each email into a category and write short summaries."""
import json

from openai import OpenAI

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


def _fallback(emails):
    """If the LLM fails, dump everything under Other/Important so nothing is lost."""
    return {
        "emails": [
            {
                "index": i,
                "category": "Other/Important",
                "summary": f"{e['subject']} — {e['from']}",
            }
            for i, e in enumerate(emails)
        ],
        "category_digests": {
            "Other/Important": "LLM classification unavailable; raw list below."
        },
    }


def categorize(emails):
    """Return {emails: [...], category_digests: {...}}."""
    if not emails:
        return {"emails": [], "category_digests": {}}

    compact = [
        {"index": i, "from": e["from"], "subject": e["subject"], "snippet": e["snippet"]}
        for i, e in enumerate(emails)
    ]
    prompt = _PROMPT.format(
        categories="\n".join(f"- {c}" for c in config.CATEGORIES),
        emails=json.dumps(compact, ensure_ascii=False, indent=2),
    )

    try:
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = json.loads(resp.choices[0].message.content)
        if not isinstance(data.get("emails"), list):
            raise ValueError("missing 'emails' list")
        return data
    except Exception as exc:  # noqa: BLE001 - never let triage crash the digest
        print(f"[categorize] OpenAI failed ({exc}); using fallback.")
        return _fallback(emails)
