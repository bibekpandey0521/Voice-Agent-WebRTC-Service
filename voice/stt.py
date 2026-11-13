"""Speech-to-text with Faster-Whisper."""

import numpy as np
from faster_whisper import WhisperModel
from config import settings
from webrtc.audio import prepare_audio


class STT:
    """Thin Whisper wrapper."""

    def __init__(self):
        """Load and warm up the model."""
        self.model = WhisperModel(settings.WHISPER_SIZE, device="cpu", compute_type="int8", cpu_threads=4)
        try:
            self.model.transcribe(np.zeros(8000, dtype=np.float32), beam_size=1)
        except Exception:
            pass

    def transcribe(self, audio_data, sample_rate):
        """Return text for captured audio."""
        audio = prepare_audio(audio_data, sample_rate)
        if len(audio) == 0:
            return ""
        segments, _ = self.model.transcribe(audio, language="en", beam_size=1, best_of=1, temperature=0.0, condition_on_previous_text=False, vad_filter=True, without_timestamps=True)
        return " ".join(s.text for s in segments).strip()
