from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app import api


class ContextualTutorApiTests(unittest.TestCase):
    def test_tutor_receives_course_context_selected_passage_and_history(self) -> None:
        completion = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Voici une explication claire."))]
        )
        groq_client = MagicMock()
        groq_client.chat.completions.create.return_value = completion

        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}):
                    with patch("groq.Groq", return_value=groq_client):
                        with TestClient(api.app) as client:
                            response = client.post(
                                "/api/tutor",
                                json={
                                    "node_id": "intro-reseau-intermediaire",
                                    "question": "Pourquoi cette notion est-elle importante ?",
                                    "selected_text": "Le passage à expliquer",
                                    "history": [
                                        {"role": "user", "content": "Explique la notion"},
                                        {"role": "assistant", "content": "Voici une première explication."},
                                    ],
                                },
                            )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json()["answer"], "Voici une explication claire.")
        messages = groq_client.chat.completions.create.call_args.kwargs["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertIn("CONTENU DU COURS", messages[0]["content"])
        self.assertIn("PASSAGE SÉLECTIONNÉ PAR L'APPRENANT", messages[0]["content"])
        self.assertIn("Le passage à expliquer", messages[0]["content"])
        self.assertEqual(messages[1]["content"], "Explique la notion")
        self.assertEqual(messages[2]["content"], "Voici une première explication.")
        self.assertEqual(messages[3]["content"], "Pourquoi cette notion est-elle importante ?")


    def test_tutor_explains_how_to_configure_missing_groq_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            database_path = Path(temporary) / "skilltree.db"
            with patch.object(api, "DB_PATH", database_path):
                with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
                    with TestClient(api.app) as client:
                        response = client.post(
                            "/api/tutor",
                            json={"node_id": "intro-reseau-intermediaire", "question": "Explique cette notion"},
                        )

        self.assertEqual(response.status_code, 200, response.text)
        self.assertIn("Environment", response.json()["answer"])
        self.assertIn("console.groq.com", response.json()["answer"])


if __name__ == "__main__":
    unittest.main()
