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
        self.stop_speaking = threading.Event()
        self.saved_greeting = None
        self.saved_time = 0.0
        self.turn_lock = threading.Lock()

    def merge_hesitation(self, raw_text):
        """Merge a pending greeting with the new turn when close in time."""
        now = time.time()
        if self.saved_greeting and now - self.saved_time <= 1.8:
            merged = self.saved_greeting + " " + raw_text
            self.saved_greeting = None
            return merged
        self.saved_greeting = None
        return raw_text

    def stream_reply(self, prompt, sentence_box, stop_speaking, stt_ms=0):
        """Run LLM in a producer thread and yield TTS audio chunks."""
        def producer():
            try:
                for sentence in self.llm.ask(prompt, abort=stop_speaking):
                    if stop_speaking.is_set():
                        break
                    sentence_box.put(sentence)
            finally:
                sentence_box.put(None)

        threading.Thread(target=producer, daemon=True).start()
        start = time.time()
        first = None
        while True:
            if stop_speaking.is_set():
                break
            sentence = sentence_box.get()
            if sentence is None:
                break
            if stop_speaking.is_set():
                break
            for audio_chunk in self.tts.speak(sentence):
                if stop_speaking.is_set():
                    break
                if first is None:
                    first = (time.time() - start) * 1000
                    print(f"[STT: {stt_ms:.0f}ms | Time to First Audio: {first:.0f}ms]")
                yield audio_chunk

    def handle_voice_turn(self, audio):
        """Process one captured audio turn."""
        sr, data = audio
        stt_start = time.time()
        raw_text = self.stt.transcribe(data, sr)
        stt_ms = (time.time() - stt_start) * 1000
        if not raw_text:
            return
        fillers = {"um", "uh", "hmm", "ah", "oh", "so", "well"}
        words = raw_text.split()
        if words and all(w.strip("!.,").lower() in fillers for w in words):
            return
        raw_text = self.merge_hesitation(raw_text)
        if raw_text.strip().lower().strip("!.") in {"hello", "hi", "hey"}:
            self.saved_greeting = raw_text
            self.saved_time = time.time()
            deadline = time.time() + 1.1
            while time.time() < deadline:
                time.sleep(0.1)
                if self.saved_greeting is None:
                    return
            if self.saved_greeting == raw_text:
                self.saved_greeting = None
            self.stop_speaking.set()
            self.stop_speaking = threading.Event()
            with self.turn_lock:
                yield from self.stream_reply(raw_text, queue.Queue(), self.stop_speaking, stt_ms)
            return
        print(f"[User]: {raw_text}")
        self.stop_speaking.set()
        self.stop_speaking = threading.Event()
        try:
            with self.turn_lock:
                intent = detect_intent(raw_text, self.is_paused, settings.OLLAMA_MODEL)
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
                        sentence_box = queue.Queue()
                        yield from self.stream_reply(prompt, sentence_box, self.stop_speaking, stt_ms)
                    else:
                        yield from self.tts.speak("History cleared.")
                    return
                if action in ("voice", "speed", "model"):
                    if action == "voice":
                        self.tts.set_voice(voice=prompt)
                    elif action == "speed":
                        self.tts.set_voice(speed=float(prompt))
                    elif action == "model":
                        self.llm.set_model(prompt)
                    yield from self.tts.speak("Updated.")
                    return
                if self.is_paused:
                    return
                sentence_box = queue.Queue()
                yield from self.stream_reply(prompt, sentence_box, self.stop_speaking, stt_ms)
        finally:
            self.stop_speaking.set()

    def create_stream(self):
        """Create the FastRTC audio stream."""
        algo = AlgoOptions(audio_chunk_duration=0.45, started_talking_threshold=0.18, speech_threshold=0.1)
        return Stream(handler=ReplyOnPause(self.handle_voice_turn, can_interrupt=True, algo_options=algo), modality="audio", mode="send-receive")
