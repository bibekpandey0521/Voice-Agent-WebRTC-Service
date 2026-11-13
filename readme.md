🎙️ Local Real-Time Voice Agent

A privacy-focused, local-first, real-time AI voice assistant powered by Python, WebRTC, Faster-Whisper, Ollama, and Kokoro TTS.

Build your own AI voice assistant that listens, understands, thinks, and speaks — entirely on your local machine.

The application captures audio through your browser microphone, transcribes speech using Faster-Whisper, generates intelligent responses using a locally hosted Ollama model, and converts responses into natural speech using Kokoro TTS.

With incremental sentence-level audio streaming, users can hear responses before the language model finishes generating the complete answer.

It also supports voice interruption, optional background conversation logging through n8n, and a FastAPI health endpoint for custom frontend integrations.

✨ Features
🎤 Real-Time Voice Input — Capture microphone audio directly from your browser using WebRTC and FastRTC.
📝 Speech-to-Text — Transcribe audio locally using Faster-Whisper.
🧠 Local AI Intelligence — Generate responses using Ollama-hosted language models.
🔊 Natural Text-to-Speech — Generate speech using Kokoro TTS.
⚡ Incremental Audio Streaming — Generate and play audio sentence by sentence.
🛑 Voice Interruption — Interrupt ongoing assistant responses using FastRTC interruption handling.
🔒 Local-First Architecture — Keep STT, LLM, and TTS processing on your machine.
🔄 Optional n8n Integration — Send conversation logs to an n8n webhook asynchronously.
🚀 FastAPI Backend — Expose health checks and integrate custom frontend applications.
🧩 Modular Architecture — Keep speech recognition, language generation, synthesis, and orchestration separated.
🏗️ System Architecture

The application follows a modular, event-driven voice processing architecture.

Each component handles a dedicated responsibility, allowing individual pipeline stages to be modified, tested, and optimized independently.

1. High-Level Architecture
mermaid
flowchart TB
    subgraph CLIENT["🌐 CLIENT SIDE"]
        A["🎤 Browser Microphone"]
        B["WebRTC Audio Stream"]
        H["🔊 Browser Audio Output"]
    end

    subgraph BACKEND["⚙️ PYTHON BACKEND"]
        C["FastRTC / WebRTC Handler"]
        D["Voice Pipeline Orchestrator"]

        subgraph PIPELINE["AI PROCESSING PIPELINE"]
            E["Speech-to-Text<br/>Faster-Whisper"]
            F["Language Model<br/>Ollama"]
            G["Text-to-Speech<br/>Kokoro"]
        end

        I["Sentence Stream Buffer"]
    end

    subgraph LOCAL["💻 LOCAL MODEL SERVICES"]
        J["Whisper Model"]
        K["Ollama API"]
        L["Kokoro Voice Model"]
    end

    subgraph AUTOMATION["🔗 OPTIONAL AUTOMATION"]
        M["Background Thread"]
        N["n8n Webhook"]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E <--> J
    E --> F
    F <--> K
    F --> I
    I --> G
    G <--> L
    G --> H

    D -.-> M
    M --> N

    style CLIENT fill:#172554,stroke:#3B82F6,color:#fff
    style BACKEND fill:#164E63,stroke:#06B6D4,color:#fff
    style PIPELINE fill:#134E4A,stroke:#10B981,color:#fff
    style LOCAL fill:#422006,stroke:#F59E0B,color:#fff
    style AUTOMATION fill:#3B0764,stroke:#A855F7,color:#fff

Architecture Components
Component	Technology	Responsibility
Audio Input	Browser Microphone	Captures user speech
Communication	WebRTC / FastRTC	Transfers audio between client and server
Backend	Python / FastAPI	Manages application lifecycle and API
Orchestration	VoicePipelineOrchestrator	Coordinates the voice processing pipeline
STT	Faster-Whisper	Converts speech into text
LLM	Ollama	Generates AI responses locally
Sentence Processing	Python	Extracts complete sentences from streamed text
TTS	Kokoro	Converts generated text into speech
Automation	n8n	Receives optional conversation logs
🔄 How the Voice Pipeline Works

The voice assistant processes each user interaction through a sequence of stages.

2. End-to-End Workflow Diagram
mermaid
flowchart TD
    START(["🚀 Start Conversation"])

    A["🎤 Capture User Speech"]
    B["WebRTC Audio Transmission"]
    C["FastRTC Voice Handler"]
    D{"Speech Segment Completed?"}

    E["Prepare Audio"]
    F["Convert Stereo to Mono"]
    G["Normalize Audio"]
    H["Resample to 16 kHz"]

    I["🎯 Faster-Whisper Transcription"]
    J["Recognized User Text"]

    K["🧠 Send Prompt to Ollama"]
    L["Stream LLM Response"]
    M["Sentence Buffer"]
    N{"Complete Sentence Available?"}

    O["🔊 Kokoro TTS"]
    P["Generate Audio Chunk"]
    Q["Stream Audio to Browser"]

    R{"More Response Text?"}
    S["Assemble Full Assistant Response"]

    T["📨 Optional n8n Logging"]
    U(["✅ Conversation Turn Completed"])

    START --> A
    A --> B
    B --> C
    C --> D

    D -- No --> A
    D -- Yes --> E

    E --> F --> G --> H
    H --> I --> J
    J --> K --> L --> M
    M --> N

    N -- No --> M
    N -- Yes --> O --> P --> Q
    Q --> R

    R -- Yes --> M
    R -- No --> S

    S --> T
    T --> U

    style START fill:#166534,color:#fff
    style U fill:#166534,color:#fff
    style I fill:#1D4ED8,color:#fff
    style K fill:#7E22CE,color:#fff
    style O fill:#0F766E,color:#fff

3. Detailed Processing Stages
Stage 1 — Audio Capture

The browser captures microphone input and streams audio through WebRTC.

User speaks through the browser microphone.
FastRTC receives incoming audio.
Voice activity and pause detection determine when a speech segment is ready for processing.
Stage 2 — Audio Preprocessing

Before transcription, the incoming audio is prepared for Faster-Whisper.

Processing includes:

Stereo-to-mono conversion.
Normalization of int16 samples to float32 when required.
Resampling to 16 kHz when necessary.
Ensuring contiguous NumPy arrays for downstream processing.
Stage 3 — Speech Recognition

Faster-Whisper converts the prepared audio into text.

text
Input:
    Browser microphone audio

Processing:
    Faster-Whisper

Output:
    "What is artificial intelligence?"

Stage 4 — Local LLM Generation

The recognized text is sent to Ollama through its local API.

The language model generates a response incrementally rather than waiting for the entire response.

Example:

text
User:
    Explain artificial intelligence.

LLM Stream:
    Artificial intelligence is a field of computer science...

    It enables machines to perform tasks that typically require...

    human intelligence.

Stage 5 — Sentence-Level Streaming

The LLM output is collected in a sentence buffer.

Whenever a complete sentence becomes available, it is passed to Kokoro TTS.

This allows speech synthesis to begin while the LLM is still generating subsequent sentences.

Stage 6 — Text-to-Speech

Kokoro converts each sentence into an audio chunk.

The generated audio is streamed back to the browser for playback.

Stage 7 — Optional Conversation Logging

After the response is assembled, the application can dispatch the conversation to an n8n webhook through a background thread.

This prevents webhook network requests from blocking the main voice-processing path.

⚡ Real-Time Streaming Architecture

One of the main advantages of this project is sentence-level streaming.

Instead of waiting for the LLM to finish generating its entire response, the application starts speech synthesis as soon as a complete sentence is available.

4. Streaming Workflow
mermaid
flowchart TD
    A["Ollama Token Stream"]

    B["Sentence Accumulator"]

    C{"Sentence Complete?"}

    D["Extract Complete Sentence"]

    E["Send Sentence to Kokoro"]

    F["Generate Audio Chunk"]

    G["Stream Audio to Browser"]

    H["Continue Receiving LLM Tokens"]

    I{"LLM Finished?"}

    J(["Response Completed"])

    A --> B
    B --> C
    C -- No --> H
    C -- Yes --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I -- No --> A
    I -- Yes --> J

    style A fill:#1D4ED8,color:#fff
    style E fill:#0F766E,color:#fff
    style J fill:#166534,color:#fff

Why Sentence-Level Streaming?
Traditional Processing	Streaming Processing
Waits for the full LLM response	Processes output incrementally
Starts TTS after generation completes	Starts TTS when a sentence is ready
Higher initial response delay	Lower potential time to first audio
Generates audio after text completion	Generates audio while text generation continues

Result: A more responsive conversational experience.

🛑 Voice Interruption Handling

The application supports interruption handling through FastRTC.

This allows users to interrupt an ongoing assistant response and begin another conversational turn.

5. Interruption Workflow
mermaid
flowchart TD
    A["Assistant Generating Response"]
    B["Streaming Audio to Browser"]
    C{"User Interrupts?"}

    D["Stop Current Response"]
    E["Handle Interruption"]
    F["Capture New User Speech"]
    G["Start New Voice Turn"]

    H["Continue Audio Playback"]
    I(["Response Completed"])

    A --> B --> C

    C -- Yes --> D
    D --> E
    E --> F
    F --> G
    G --> A

    C -- No --> H
    H --> I

    style D fill:#991B1B,color:#fff
    style G fill:#1D4ED8,color:#fff
    style I fill:#166534,color:#fff


The exact cancellation behavior depends on how the active FastRTC reply and audio generator are configured.

📁 Project Structure
text
Voice-Agent-WebRTC-Service/
│
├── main.py
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py
│
└── src/
    │
    ├── server.py
    │
    ├── webrtc/
    │   └── handler.py
    │
    ├── pipeline/
    │   ├── stt.py
    │   ├── llm.py
    │   └── tts.py
    │
    └── automation/
        └── n8n_client.py

File Responsibilities
File	Responsibility
main.py	Application entry point
config/settings.py	Centralized application configuration
src/server.py	FastAPI initialization, CORS, and health endpoint
src/webrtc/handler.py	WebRTC integration and voice orchestration
src/pipeline/stt.py	Faster-Whisper transcription
src/pipeline/llm.py	Ollama streaming and sentence splitting
src/pipeline/tts.py	Kokoro audio generation
src/automation/n8n_client.py	Background n8n webhook integration
🛠️ Technology Stack
Technology	Purpose
Python 3.10+	Core application development
FastAPI	Backend API
WebRTC	Real-time browser audio communication
FastRTC	WebRTC voice pipeline integration
Faster-Whisper	Speech recognition
Ollama	Local language model inference
Kokoro TTS	Text-to-speech synthesis
NumPy	Audio preprocessing
n8n	Optional workflow automation
🚀 Getting Started
1. Prerequisites

Install the following:

Python 3.10 or later
Git
Ollama
A supported browser with microphone access

Download Ollama:

https://ollama.com/

Pull the example model:

bash
ollama pull llama3.2


Make sure Ollama is running and accessible at:

text
http://localhost:11434

2. Clone the Repository
bash
git clone https://github.com/bibekpx/Voice-Agent-WebRTC-Service.git

cd Voice-Agent-WebRTC-Service

3. Create a Virtual Environment

Windows — Command Prompt

bat
python -m venv .venv
.venv\Scripts\activate


Windows — PowerShell

powershell
python -m venv .venv
.venv\Scripts\Activate.ps1


Linux / macOS

bash
python3 -m venv .venv
source .venv/bin/activate

4. Install Dependencies
bash
python -m pip install --upgrade pip

pip install -r requirements.txt


For Faster-Whisper GPU acceleration, install compatible CUDA and cuDNN dependencies according to your environment and the CTranslate2 requirements.

5. Configure the Application

Open:

text
config/settings.py


Review the available configuration values.

Setting	Example	Description
WHISPER_MODEL_SIZE	base.en	Whisper model size
OLLAMA_BASE_URL	http://localhost:11434	Ollama API address
OLLAMA_MODEL	llama3.2	Local language model
N8N_WEBHOOK_URL	Empty string	Optional n8n webhook

Use the actual setting names and defaults implemented in your checkout.

6. Start the Application
Option A — Browser Voice Interface

Run:

bash
python main.py


Open:

text
http://localhost:7860


Allow microphone access and start speaking.

Option B — FastAPI Backend

Run:

bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload


Health endpoint:

http
GET http://localhost:8000/health


The FastAPI command assumes that main.py exports an app object. Use the entry point and application object provided by your checkout.

🔌 Optional n8n Integration

The application supports optional conversation logging through an n8n webhook.

The integration runs asynchronously in a background thread to keep network requests outside the main voice-processing path.

6. n8n Workflow Diagram
mermaid
flowchart TD
    A["Voice Conversation Completed"]

    B["Collect User Prompt"]

    C["Collect Assistant Response"]

    D["Background Thread"]

    E["HTTP POST Request"]

    F["n8n Webhook Trigger"]

    G["Process Conversation Data"]

    H["Store in Database"]

    I["Send Notification"]

    J["Execute Additional Automation"]

    K(["Workflow Completed"])

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G

    G --> H
    G --> I
    G --> J

    H --> K
    I --> K
    J --> K

    style D fill:#7E22CE,color:#fff
    style F fill:#EA580C,color:#fff
    style K fill:#166534,color:#fff

Example Webhook Payload
json
{
  "user_prompt": "Explain machine learning",
  "assistant_response": "Machine learning is a branch of artificial intelligence..."
}

Configuration

Set the webhook URL in your application configuration:

python
N8N_WEBHOOK_URL = "https://your-n8n-instance/webhook/voice-agent"


Leave it empty to disable logging.

Privacy note: Conversation data is sent to the configured n8n endpoint when logging is enabled. Local model inference does not automatically mean that external integrations are local.

🔍 Function Call Flow

The main voice interaction is coordinated by:

python
VoicePipelineOrchestrator.handle_voice_turn(audio)


Located in:

text
src/webrtc/handler.py

Execution Sequence
mermaid
sequenceDiagram
    autonumber

    actor User
    participant Browser
    participant WebRTC as FastRTC Handler
    participant STT as Faster-Whisper
    participant LLM as Ollama
    participant TTS as Kokoro
    participant n8n as Optional n8n

    User->>Browser: Speak into microphone
    Browser->>WebRTC: Send audio stream
    WebRTC->>WebRTC: Detect completed speech segment

    WebRTC->>STT: transcribe(audio, sample_rate)
    STT-->>WebRTC: Recognized text

    WebRTC->>LLM: generate_sentence_stream(prompt)

    loop Stream generated sentences
        LLM-->>WebRTC: Complete sentence
        WebRTC->>TTS: stream_audio(sentence)
        TTS-->>Browser: Audio chunk
        Browser-->>User: Play generated speech
    end

    WebRTC->>n8n: Background conversation logging (optional)
    Note over WebRTC,n8n: Logging runs asynchronously

    Browser-->>User: Conversation completed

⚙️ Configuration and Customization
Requirement	File	Main Function / Area
Change assistant personality	src/pipeline/llm.py	generate_sentence_stream()
Change Ollama model	config/settings.py	Model configuration
Change Whisper model	src/pipeline/stt.py	STTService.__init__()
Enable GPU inference	src/pipeline/stt.py	Device and compute type
Change TTS voice	src/pipeline/tts.py	stream_audio()
Modify API routes	src/server.py	create_app()
Customize webhook payload	src/automation/n8n_client.py	_send_webhook_sync()
Modify interruption behavior	src/webrtc/handler.py	create_stream()
Change voice-turn detection	src/webrtc/handler.py	ReplyOnPause(...)
📈 Performance Optimization

For a responsive real-time voice experience, consider the following:

1. Keep Processing Asynchronous

Avoid blocking the audio-processing loop with slow network requests, database operations, or unrelated background tasks.

2. Stream Responses Incrementally

Generate speech as complete sentences become available rather than waiting for the complete LLM response.

3. Optimize Whisper

Choose a model size based on your hardware and transcription quality requirements.

Model	General Consideration
tiny.en	Lower resource usage
base.en	Balanced starting point
small.en	Higher transcription capacity
4. Use Compatible GPU Acceleration

Faster-Whisper supports GPU inference through CTranslate2. Ensure NVIDIA drivers and the required CUDA/cuDNN libraries are compatible before enabling CUDA.

5. Preserve Audio Array Compatibility

Use:

python
np.ascontiguousarray(audio)


Where required by downstream audio-processing libraries.

6. Optimize the Spoken Response

Keep LLM output suitable for speech.

Avoid unnecessary:

Markdown formatting
Emojis
Complex code blocks
Decorative symbols
7. Keep Integrations Optional

The assistant should continue operating when n8n logging is disabled or unavailable.

🧪 Troubleshooting
Problem	Possible Solution
Ollama connection error	Check whether Ollama is running and verify the API URL
Model not found	Run ollama list and pull the configured model
Microphone unavailable	Check browser permissions and operating-system input settings
Whisper initialization error	Verify Python dependencies and model availability
CUDA initialization error	Check NVIDIA drivers and CUDA/cuDNN compatibility
No audio output	Verify Kokoro initialization and browser audio playback
n8n logs missing	Verify webhook URL and workflow activation
Slow response	Review model sizes, inference device, and sentence buffering
WebRTC connection issues	Check browser support and network configuration
🔐 Privacy and Security

This project is designed around local inference.

Speech recognition can run locally.
Language generation can run through a local Ollama service.
Speech synthesis can run locally.
n8n integration is optional.
Webhook logging should be disabled when not required.

For deployment beyond local development:

Restrict access to backend endpoints.
Configure appropriate CORS policies.
Avoid exposing Ollama directly to untrusted networks.
Use HTTPS for remote browser microphone access.
Store webhook credentials securely.
Avoid committing secrets, local model files, or environment configurations.
🗺️ Future Improvements

Potential enhancements include:

Conversation history and persistent memory.
Wake-word detection.
Voice activity detection improvements.
Multiple Kokoro voice profiles.
Streaming transcription.
Improved interruption and cancellation handling.
Conversation management UI.
Local vector database integration.
Tool calling and agent workflows.
Docker-based deployment.
Performance monitoring and latency metrics.
🤝 Contributing

Contributions are welcome!

Fork the repository.
Create a feature branch.
Implement your changes.
Test the affected pipeline components.
Submit a pull request.

Keep the real-time processing path responsive and avoid committing secrets, model files, or machine-specific configuration.

📄 License

Add the repository's license information once a license has been selected and committed.

⭐ Acknowledgements

This project brings together several powerful open-source technologies:

Python
FastAPI
FastRTC
WebRTC
Faster-Whisper
Ollama
Kokoro TTS
n8n

<div align="center">

🎙️ Build Locally. Speak Naturally. Think Intelligently.

A local-first voice assistant for real-time AI conversations.

⭐ If you find this project useful, consider giving it a star!

GitHub Repository

</div>
