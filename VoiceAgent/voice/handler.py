"""Voice turn orchestration."""

import os
import time
import queue
import threading
from fastrtc import Stream, ReplyOnPause, AlgoOptions
from config import settings
from voice.stt import STT
from voice.llm import LLM
from voice.tts import TTS
from voice.intent import detect_intent


class VoiceHandler:
    """Orchestrate one voice turn."""

    def __init__(self):
        """Load STT, LLM, and TTS once."""
        self.stt = STT()
        self.llm = LLM()
        self.tts = TTS()
        self.is_paused = False
        self._abort = threading.Event()
        self._turn_lock = threading.Lock()

    def _answer(self, prompt, stt_ms=0, abort=None):
        """Run LLM in a producer thread and TTS on the consumer thread."""
        q = queue.Queue()
        def producer():
            try:
                for sentence in self.llm.ask(prompt, abort=abort):
                    if abort is not None and abort.is_set():
                        break
                    q.put(sentence)
            finally:
                q.put(None)
        threading.Thread(target=producer, daemon=True).start()
        start = time.time()
        first = None
        while True:
            if abort is not None and abort.is_set():
                break
            sentence = q.get()
            if sentence is None:
                break
            if abort is not None and abort.is_set():
                break
            for chunk in self.tts.speak(sentence):
                if abort is not None and abort.is_set():
                    break
                if first is None:
                    first = (time.time() - start) * 1000
                    print(f"[STT: {stt_ms:.0f}ms | Time to First Audio: {first:.0f}ms]")
                yield chunk

    def handle_voice_turn(self, audio):
        """Process one captured audio turn."""
        sr, data = audio
        stt_start = time.time()
        text = self.stt.transcribe(data, sr)
        stt_ms = (time.time() - stt_start) * 1000
        if not text:
            return
        print(f"[User]: {text}")
        self._abort.clear()
        try:
            with self._turn_lock:
                intent = detect_intent(text, self.is_paused)
                action = intent["action"]
                prompt = intent["prompt"]
                if action == "pause":
                    self.is_paused = True
                    yield from self.tts.speak("Paused.")
                    return
                if action == "resume":
                    self.is_paused = False
                    yield from self.tts.speak("Resumed.")
                    return
                if action == "exit":
                    yield from self.tts.speak("Goodbye.")
                    time.sleep(1.2)
                    os._exit(0)
                if action == "reset":
                    self.llm.reset_history()
                    self.is_paused = False
                    if prompt:
                        yield from self._answer(prompt, stt_ms, abort=self._abort)
                    else:
                        yield from self.tts.speak("History cleared.")
                    return
                if self.is_paused:
                    return
                yield from self._answer(prompt, stt_ms, abort=self._abort)
        finally:
            self._abort.set()

    def create_stream(self):
        """Create the FastRTC audio stream."""
        algo = AlgoOptions(audio_chunk_duration=0.25, started_talking_threshold=0.15, speech_threshold=0.08)
        return Stream(handler=ReplyOnPause(self.handle_voice_turn, can_interrupt=True, algo_options=algo), modality="audio", mode="send-receive")
