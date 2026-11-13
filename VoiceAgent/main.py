"""Entry point for the voice agent."""

from config import settings
from webrtc.server import create_app

app, stream = create_app()

if __name__ == "__main__":
    stream.ui.launch(server_port=settings.APP_PORT)
