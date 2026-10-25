from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import api


class TextToSpeechApiTests(unittest.TestCase):
    def test_tts_returns_french_mp3_and_translates_rate(self) -> None:
        captured: dict[str, str] = {}

        class FakeCommunicate:
            def __init__(self, text: str, *, voice: str, rate: str) -> None:
                captured.update({"text": text, "voice": voice, "rate": rate})

            async def stream(self):
                yield {"type": "audio", "data": b"mp3-segment-one"}
                yield {"type": "WordBoundary", "text": "bonjour"}
                yield {"type": "audio", "data": b"mp3-segment-two"}

        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with patch("edge_tts.Communicate", FakeCommunicate):
                    with TestClient(api.app) as client:
                        response = client.post(
                            "/api/tts",
                            json={"text": "Bonjour. Voici une explication.", "rate": 1.2},
                        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.headers["content-type"], "audio/mpeg")
        self.assertEqual(response.content, b"mp3-segment-onemp3-segment-two")
        self.assertEqual(captured["voice"], "fr-FR-DeniseNeural")
        self.assertEqual(captured["rate"], "+20%")
        self.assertEqual(captured["text"], "Bonjour. Voici une explication.")

    def test_tts_rejects_empty_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with TestClient(api.app) as client:
                    response = client.post("/api/tts", json={"text": " "})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
