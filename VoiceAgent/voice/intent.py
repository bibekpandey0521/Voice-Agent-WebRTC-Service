"""Dynamic intent detection."""

import json
import httpx
from config import settings

_client = httpx.Client(base_url=settings.OLLAMA_BASE_URL, timeout=15.0)
PROMPT = 'Classify text. Reply JSON only: {"action":"pause|resume|exit|reset|chat","prompt":"text to answer or empty"}.'
CONTROL = ("pause", "resume", "exit", "quit", "reset", "stop", "start", "new", "goodbye", "wake", "hold", "wait", "continue")


def detect_intent(text, is_paused=False):
    """Return an action dict."""
    words = text.split()
    low = text.lower()
    if not is_paused and len(words) > 4 and not any(w in low for w in CONTROL):
        return {"action": "chat", "prompt": text}
    payload = {"model": settings.INTENT_MODEL, "messages": [{"role": "system", "content": PROMPT}, {"role": "user", "content": f"paused={is_paused}\ntext={text}"}], "stream": False, "format": "json", "options": {"temperature": 0.0, "num_predict": 40}}
    try:
        r = _client.post("/api/chat", json=payload)
        r.raise_for_status()
        data = json.loads(r.json().get("message", {}).get("content", "{}"))
    except Exception:
        data = {}
    action = data.get("action", "chat")
    if action not in ("pause", "resume", "exit", "reset", "chat"):
        action = "chat"
    return {"action": action, "prompt": data.get("prompt") or text}
