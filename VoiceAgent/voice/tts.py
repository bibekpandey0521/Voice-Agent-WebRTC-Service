"""Streaming TTS with Kokoro."""

import numpy as np
from fastrtc import get_tts_model
from config import settings


class TTS:
    """Thin Kokoro wrapper."""

    def __init__(self):
        """Load and warm up."""
        self.model = get_tts_model()
        self.voice = settings.KOKORO_VOICE
        self.speed = 1.0
        self.options = {"voice": self.voice, "speed": self.speed}
        try:
            list(self.speak("Hello"))
        except Exception:
            pass

    def speak(self, text):
        """Yield audio chunks."""
        text = (text or "").strip()
        if not text:
            return
        try:
            for chunk in self.model.stream_tts_sync(text, options=self.options):
                if isinstance(chunk, tuple):
                    sr, audio = chunk
                    yield (sr, np.ascontiguousarray(audio, dtype=np.float32))
                else:
                    yield chunk
        except Exception:
            sr, audio = self.model.tts(text)
            yield (sr, np.ascontiguousarray(audio, dtype=np.float32))
