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

    def set_voice(self, voice=None, speed=None):
        """Update voice and/or speed."""
        if voice is not None:
            self.voice = voice
        if speed is not None:
            self.speed = speed
        self.options = {"voice": self.voice, "speed": self.speed}

    def _fade(self, audio):
        """Apply a 3ms fade-in/out to avoid clicks."""
        audio = np.ascontiguousarray(audio, dtype=np.float32)
        n = audio.shape[0] if audio.ndim == 1 else audio.shape[-1]
        if n >= 144:
            ramp = np.linspace(0.0, 1.0, 72, dtype=np.float32)
            if audio.ndim == 1:
                audio[:72] *= ramp
                audio[-72:] *= ramp[::-1]
            else:
                audio[..., :72] *= ramp
                audio[..., -72:] *= ramp[::-1]
        return audio

    def speak(self, text):
        """Yield faded audio chunks."""
        text = (text or "").strip()
        if not text:
            return
        try:
            for chunk in self.model.stream_tts_sync(text, options=self.options):
                if isinstance(chunk, tuple):
                    sr, audio = chunk
                    yield (sr, self._fade(audio))
                else:
                    yield chunk
        except Exception:
            sr, audio = self.model.tts(text)
            yield (sr, self._fade(audio))
