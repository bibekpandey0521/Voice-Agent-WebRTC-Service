"""Streaming chat with Ollama."""

import json
import httpx
from config import settings

SYSTEM = "You are a voice assistant. Reply in 1-2 short spoken sentences. No markdown."
PUNCT = {".", "?", "!", "\n"}
CLAUSE = {",", ";", ":"}


class LLM:
    """Thin Ollama wrapper."""

    def __init__(self):
        """Create client and warm up."""
        self.model = settings.OLLAMA_MODEL
        self.client = httpx.Client(base_url=settings.OLLAMA_BASE_URL, timeout=60.0)
        self.history = []
        try:
            self.client.post("/api/chat", json={"model": self.model, "messages": [{"role": "user", "content": "hi"}], "stream": False, "keep_alive": "30m", "options": {"num_predict": 1, "num_ctx": 512}}, timeout=10.0)
        except Exception:
            pass

    def reset_history(self):
        """Clear history."""
        self.history = []

    def ask(self, prompt):
        """Yield reply sentences."""
        self.history.append({"role": "user", "content": prompt})
        self.history = self.history[-6:]
        messages = [{"role": "system", "content": SYSTEM}] + self.history
        payload = {"model": self.model, "messages": messages, "stream": True, "keep_alive": "30m", "options": {"temperature": 0.6, "num_predict": 65, "num_ctx": 512}}
        buffer = ""
        full = ""
        yielded_first = False
        with self.client.stream("POST", "/api/chat", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                token = data.get("message", {}).get("content", "")
                buffer += token
                if not yielded_first and len(buffer) >= 20:
                    idx = -1
                    for i, c in enumerate(buffer):
                        if c in CLAUSE or c in PUNCT:
                            idx = i
                            break
                    if idx >= 0:
                        part = buffer[:idx + 1].strip()
                        if part:
                            yield part
                            full += part + " "
                            buffer = buffer[idx + 1:]
                            yielded_first = True
                if any(c in token for c in PUNCT):
                    parts = []
                    last = 0
                    for i, c in enumerate(buffer):
                        if c in PUNCT:
                            parts.append(buffer[last:i + 1].strip())
                            last = i + 1
                    for part in parts:
                        if part:
                            yield part
                            full += part + " "
                    buffer = buffer[last:]
                if data.get("done", False):
                    break
        if buffer.strip():
            yield buffer.strip()
            full += buffer.strip()
        self.history.append({"role": "assistant", "content": full.strip()})
        self.history = self.history[-6:]
