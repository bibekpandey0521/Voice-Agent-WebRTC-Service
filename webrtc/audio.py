"""Fast 48kHz to 16kHz audio preparation."""

import numpy as np


def prepare_audio(audio_data, sample_rate):
    """Convert captured audio to 16kHz float32."""
    audio = np.asarray(audio_data).squeeze()
    if audio.ndim > 1:
        audio = audio.mean(axis=0)
    if audio.dtype == np.int16:
        audio = audio.astype(np.float32) / 32768.0
    else:
        audio = audio.astype(np.float32)
    if sample_rate != 16000 and len(audio) > 0:
        if sample_rate % 16000 == 0:
            audio = audio[::sample_rate // 16000]
        else:
            n = int(len(audio) * 16000 / sample_rate)
            audio = np.interp(np.linspace(0, len(audio), n, endpoint=False), np.arange(len(audio)), audio).astype(np.float32)
    return np.ascontiguousarray(audio)
