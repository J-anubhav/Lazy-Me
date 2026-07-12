"""Send the digest to Telegram via the Bot API."""
import html

import requests

import config

_API = "https://api.telegram.org/bot{token}/sendMessage"
_MAX = 4096  # Telegram hard limit per message.


def _chunks(text: str):
    """Split on newlines so messages stay under the Telegram size limit."""
    if len(text) <= _MAX:
        yield text
        return
    buf = ""
    for line in text.split("\n"):
        if len(buf) + len(line) + 1 > _MAX:
            if buf:
                yield buf
            buf = line
        else:
            buf = f"{buf}\n{line}" if buf else line
    if buf:
        yield buf


def send(text: str):
    url = _API.format(token=config.TELEGRAM_BOT_TOKEN)
    for chunk in _chunks(text):
        resp = requests.post(
            url,
            json={
                "chat_id": config.TELEGRAM_CHAT_ID,
                "text": chunk,
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=30,
        )
        resp.raise_for_status()


def esc(text: str) -> str:
    """Escape user/email text for Telegram HTML parse mode."""
    return html.escape(text, quote=False)
