🎙️ Local Real-Time Voice Agent

A privacy-focused, local-first AI voice assistant powered by Python, WebRTC, Faster-Whisper, Ollama, and Kokoro TTS.

Capture audio through your browser microphone, transcribe speech locally, generate responses via a local LLM, and hear natural speech streamed back sentence-by-sentence—all without sending your voice data to the cloud.

✨ Key Features

Real-Time WebRTC Audio: Low-latency microphone capture and audio playback directly in the browser using FastRTC.

100% Local AI Pipeline: Runs speech-to-text (Faster-Whisper), language generation (Ollama), and text-to-speech (Kokoro TTS) entirely on your machine.

Sentence-Level Streaming: Starts synthesizing and playing audio as soon as the first sentence is generated, drastically reducing perceived latency.

Voice Interruption: Naturally interrupt the assistant mid-sentence to start a new turn.

Modular & Extensible: Cleanly separated pipeline stages with a FastAPI backend and optional asynchronous n8n webhook logging.

🏗️ System Architecture

The application uses an event-driven pipeline orchestrated by VoicePipelineOrchestrator. Audio is processed in stages, allowing text generation and speech synthesis to overlap.

flowchart LR
    subgraph Client ["🌐 Browser Client"]
        Mic["🎤 Microphone"]
        Speaker["🔊 Audio Output"]
    end

    subgraph Backend ["⚙️ Python / FastAPI Backend"]
        WebRTC["FastRTC Handler"]
        STT["Faster-Whisper (STT)"]
        LLM["Ollama Stream (LLM)"]
        Buffer["Sentence Buffer"]
        TTS["Kokoro (TTS)"]
    end

    subgraph Optional ["🔗 Async Automation"]
        n8n["n8n Webhook"]
    end

    Mic -->|WebRTC| WebRTC
    WebRTC -->|16kHz Mono| STT
    STT -->|Text| LLM
    LLM -->|Tokens| Buffer
    Buffer -->|Complete Sentence| TTS
    TTS -->|Audio Chunks| WebRTC
    WebRTC -->|WebRTC| Speaker
    LLM -.->|Background Thread| n8n


How It Works

Capture & Preprocess: FastRTC detects speech pauses, converts incoming stereo audio to mono, normalizes samples, and resamples to 16 kHz.

Transcribe: Faster-Whisper converts the audio buffer into text.

Stream & Synthesize: The prompt is sent to Ollama. As tokens stream back, a buffer extracts complete sentences and immediately passes them to Kokoro TTS so you hear the start of the answer while the rest is still generating.

Log (Optional): Once the turn finishes, a background thread dispatches the prompt and response to an n8n webhook without blocking the audio loop.

📁 Project Structure

Voice-Agent-WebRTC-Service/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── config/
│   └── settings.py             # Centralized configuration (models, URLs)
└── src/
    ├── server.py               # FastAPI app, CORS, and /health endpoint
    ├── webrtc/
    │   └── handler.py          # FastRTC stream & VoicePipelineOrchestrator
    ├── pipeline/
    │   ├── stt.py              # Faster-Whisper transcription service
    │   ├── llm.py              # Ollama streaming & sentence chunking
    │   └── tts.py              # Kokoro speech synthesis
    └── automation/
        └── n8n_client.py       # Non-blocking n8n webhook client


🚀 Getting Started

1. Prerequisites

Python 3.10+

Ollama installed and running locally (Download Ollama)

Pull the default language model before starting:

ollama pull llama3.2


2. Installation

Clone the repository and set up a virtual environment:

git clone https://github.com/bibekpx/Voice-Agent-WebRTC-Service.git
cd Voice-Agent-WebRTC-Service

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt


(Note: For GPU acceleration with Faster-Whisper, ensure compatible CUDA and cuDNN libraries are installed for your environment.)

3. Configuration

Review config/settings.py to customize your models and endpoints:

Setting

Default

Description

WHISPER_MODEL_SIZE

base.en

Whisper model size (tiny.en, base.en, small.en)

OLLAMA_BASE_URL

http://localhost:11434

Local Ollama API endpoint

OLLAMA_MODEL

llama3.2

Local LLM used for responses

N8N_WEBHOOK_URL

""

Optional webhook URL for conversation logging

4. Running the Application

Start the Voice UI (FastRTC):

python main.py


Open http://localhost:7860 in your browser, grant microphone permissions, and start talking.

Start the FastAPI Server (Custom Frontends):

uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Verify the server is running via GET http://localhost:8000/health.

🔌 Optional n8n Integration

To log conversations to an external workflow, add your webhook URL in config/settings.py. The service sends an asynchronous POST request at the end of each turn:

{
  "user_prompt": "Explain machine learning",
  "assistant_response": "Machine learning is a branch of artificial intelligence..."
}


Privacy Note: Enabling N8N_WEBHOOK_URL transmits conversation text to that endpoint. Leave it blank for 100% offline operation.

⚙️ Customization & Troubleshooting

Quick Customization Map

Assistant Persona / System Prompt: Edit generate_sentence_stream() in src/pipeline/llm.py.

TTS Voice Profile: Update stream_audio() in src/pipeline/tts.py.

Interruption & VAD Sensitivity: Adjust ReplyOnPause parameters in src/webrtc/handler.py.

Common Issues

Ollama Connection Error: Ensure the Ollama service is active (ollama serve) and accessible at http://localhost:11434.

No Audio / Mic Issues: Ensure your browser has microphone permissions enabled. If deploying remotely, HTTPS is required by modern browsers for WebRTC microphone access.

High Latency: Switch to tiny.en in settings.py, use a smaller quantized Ollama model, or enable CUDA for Faster-Whisper.

🤝 Contributing & License

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request. Ensure you do not commit local model weights or .env secrets.

License: MIT (Update with your chosen license file)