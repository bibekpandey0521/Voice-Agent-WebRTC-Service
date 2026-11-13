"""Dynamic intent detection."""

import json
import httpx
from config import settings

_client = httpx.Client(base_url=settings.OLLAMA_BASE_URL, timeout=15.0)
PROMPT = (
    "Classify the user text. Reply JSON only: "
    '{"action":"pause|resume|exit|reset|voice|speed|model|chat","prompt":"value or text to answer"}. '
    "reset means clear history and answer the trailing prompt. "
    "Detect synonyms and natural phrasing dynamically."
)


def detect_intent(text, is_paused=False, model_name=None):
    """Return an action dict."""
    words = text.split()
    if not is_paused and len(words) > 6:
        return {"action": "chat", "prompt": text}
    payload = {"model": model_name or settings.INTENT_MODEL, "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": f"paused={is_paused}\ntext={text}"}], "stream": False, "format": "json", "options": {"temperature": 0.0, "num_predict": 45}}
    try:
        r = _client.post("/api/chat", json=payload)
        r.raise_for_status()
        data = json.loads(r.json().get("message", {}).get("content", "{}"))
    except Exception:
        data = {}
    action = data.get("action", "chat")
    if action not in ("pause", "resume", "exit", "reset", "voice", "speed", "model", "chat"):
        action = "chat"
    return {"action": action, "prompt": data.get("prompt") or text}
