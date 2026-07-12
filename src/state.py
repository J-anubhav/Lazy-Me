"""Tiny JSON store mapping a short token -> the Gmail ids for one category card.

Telegram callback_data is capped at 64 bytes, so we can't put ids in the button.
Instead the button carries a short token; this store resolves it to the ids.
"""
import json
import os
import secrets

# Store next to the project root (src/..). Git-ignored.
_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "state.json")


def _load() -> dict:
    if not os.path.exists(_PATH):
        return {}
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save(data: dict) -> None:
    with open(_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def new_token() -> str:
    return secrets.token_hex(4)  # 8 chars -> "trash:<token>" fits in 64 bytes


def put(token: str, category: str, ids: list) -> None:
    data = _load()
    data[token] = {"category": category, "ids": ids}
    _save(data)


def get(token: str):
    return _load().get(token)


def delete(token: str) -> None:
    data = _load()
    if token in data:
        del data[token]
        _save(data)
