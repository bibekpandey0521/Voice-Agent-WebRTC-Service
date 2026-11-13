🎙️ Local Real-Time Voice Agent

A privacy-focused, local-first AI voice assistant powered by Python, WebRTC, Faster-Whisper, Ollama, and Kokoro TTS.

Listen, think, and speak in real time—entirely on your local machine with zero cloud dependencies.

✨ Key Features

🎤 Real-Time WebRTC Audio: Low-latency microphone capture and audio playback directly in your browser using FastRTC.

🔒 100% Local AI Pipeline: Runs speech-to-text (Faster-Whisper), language generation (Ollama), and text-to-speech (Kokoro TTS) locally on your machine.

⚡ Sentence-Level Streaming: Starts synthesizing and playing audio the moment the first sentence is generated, drastically reducing response delay.

🛑 Natural Voice Interruption: Interrupt the assistant mid-sentence to start a new conversational turn seamlessly.

🔗 Modular & Extensible: Cleanly separated pipeline stages with a FastAPI backend and optional asynchronous n8n webhook logging.

🏗️ System Architecture

The application uses an event-driven pipeline orchestrated by VoicePipelineOrchestrator. Audio and text flow asynchronously so speech synthesis begins while the LLM is still generating tokens.

flowchart LR
    subgraph Client ["🌐 Browser Client"]
        direction TB
        Mic["🎤 Microphone"]
        Speaker["🔊 Audio Output"]
    end

    subgraph Backend ["⚙️ Python / FastAPI Backend"]
        direction TB
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
    STT -->|Transcribed Text| LLM
    LLM -->|Token Stream| Buffer
    Buffer -->|Complete Sentence| TTS
    TTS -->|Audio Chunks| WebRTC
    WebRTC -->|WebRTC| Speaker
    LLM -.->|Background Thread| n8n

    style Client fill:#1e293b,stroke:#3b82f6,stroke-width:2px,color:#fff
    style Backend fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff
    style Optional fill:#2e1065,stroke:#a855f7,stroke-width:2px,color:#fff


How the Pipeline Works

Capture & Preprocess: FastRTC detects speech pauses, converts incoming stereo audio to mono, normalizes samples, and resamples to 16 kHz.

Transcribe: Faster-Whisper converts the prepared audio array into text.

Stream & Synthesize: The prompt is sent to Ollama. As tokens stream back, a buffer extracts complete sentences and passes them immediately to Kokoro TTS.

Log (Optional): Once the turn completes, a background thread dispatches the conversation to an n8n webhook without blocking the audio loop.

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

Pull the default language model:

ollama pull llama3.2


2. Installation

Clone the repository and install dependencies inside a virtual environment:

git clone https://github.com/bibekpandey0521/Voice-Agent-WebRTC-Service.git
cd Voice-Agent-WebRTC-Service

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install packages
pip install --upgrade pip
pip install -r requirements.txt


Note on GPU Acceleration: For CUDA support with Faster-Whisper, ensure compatible NVIDIA drivers, CUDA, and cuDNN libraries are installed for your environment.

3. Configuration

Customize your local models and endpoints in config/settings.py:

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

Local LLM used for generating responses

N8N_WEBHOOK_URL

""

Optional webhook URL for conversation logging

4. Running the Application

Option A — Launch the Built-in Voice UI (FastRTC):

python main.py


Open http://localhost:7860 in your browser, allow microphone access, and start speaking.

Option B — Run as a FastAPI Backend (Custom Frontends):

uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Verify the server status via GET http://localhost:8000/health.

🔌 Optional n8n Integration

To log conversations to an external automation workflow, set N8N_WEBHOOK_URL in config/settings.py. The service sends a non-blocking POST request at the end of each turn:

{
  "user_prompt": "Explain machine learning",
  "assistant_response": "Machine learning is a branch of artificial intelligence..."
}


Privacy Note: Enabling N8N_WEBHOOK_URL transmits conversation text to that endpoint. Leave it empty for 100% offline operation.

⚙️ Customization & Troubleshooting

Assistant Persona / System Prompt: Edit generate_sentence_stream() in src/pipeline/llm.py.

TTS Voice Profile: Update stream_audio() in src/pipeline/tts.py.

Interruption & VAD Sensitivity: Adjust ReplyOnPause parameters in src/webrtc/handler.py.

API Routes & CORS: Modify create_app() in src/server.py.

Ollama Connection Error: Ensure the Ollama service is running (ollama serve) and reachable at http://localhost:11434.

Microphone / No Audio Issues: Check browser permissions. If hosting on a remote server, HTTPS is required by modern browsers for WebRTC microphone access.

High Response Latency: Switch to tiny.en in settings.py, use a smaller quantized Ollama model, or enable CUDA inference for Faster-Whisper.

🤝 Contributing & License

Contributions are welcome! Fork the repository, create a feature branch, and open a pull request. Please avoid committing local model weights or .env secrets.

Licensed under the MIT License — see the LICENSE file for details.
