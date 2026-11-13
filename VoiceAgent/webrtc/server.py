"""FastAPI app factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from voice.handler import VoiceHandler


def create_app():
    """Create the app and mount the stream."""
    app = FastAPI(title="Voice Agent")
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    handler = VoiceHandler()
    stream = handler.create_stream()
    stream.mount(app)

    @app.get("/health")
    async def health():
        """Health check."""
        return {"status": "ok"}

    return app, stream
