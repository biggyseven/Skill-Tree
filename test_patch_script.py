import ast
import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("apply_api_compat_patch.py")
spec = importlib.util.spec_from_file_location("api_compat_patch", SCRIPT)
patch = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(patch)


class PatchScriptTests(unittest.TestCase):
    def fixture_api(self):
        return '''from typing import Any
import json, random, time, uuid
from fastapi import Body, Depends, FastAPI, HTTPException
from app.domain import Node, Question, ProofKind
app = FastAPI()
EXAM_QUESTION_COUNT = 20
EXAM_DURATION_SECONDS = 1800
EXAM_PASS_SCORE = 85
EXAM_SUBMIT_GRACE_SECONDS = 15
class SkillTree: pass
class DomainError(Exception): pass
def get_tree(): pass
def _challenge_row(tree, node_id): pass
def _answer_matches(pattern, answer, *, terminal=False): return False
@app.get("/api/node/{node_id}")
def read_node(node_id: str, tree: SkillTree = Depends(get_tree)):
    node = type("NodeMock", (), {"id": node_id, "description": "x"})()
    challenge = _challenge_row(tree, node.id)
    return {"challenge": {"prompt": node.description, "time_limit": challenge["time_limit"]} if challenge else None,}
@app.get("/api/profile")
def read_profile(tree: SkillTree = Depends(get_tree)):
    exams = tree.conn.execute("SELECT COUNT(*) FROM attempts WHERE kind='exam' AND passed=1").fetchone()[0]
    return {"exams_passed": exams}
@app.post("/api/node/{node_id}/quiz")
def submit_quiz(node_id, payload, tree=None): pass
@app.post("/api/exam/start")
def exam_start(payload, tree=None):
    tree.conn.execute("INSERT INTO exam_sessions (session_id, category, question_ids, started_at, expires_at) VALUES (?, ?, ?, ?, ?)", (session_id, category, json.dumps([q.id for _, q in selected]), now, now + EXAM_DURATION_SECONDS))
@app.post("/api/topology")
def save_topology(payload, tree=None): pass
'''

    def fixture_html(self):
        return "const PASS_SCORE = 70; fetch('/api/exam/build'); fetch('/api/exam/submit'); fetch('/api/topology');"

    def test_patch_is_syntactically_valid_and_adds_missing_routes(self):
        patched = patch.patch_source(self.fixture_api(), "\n", self.fixture_html())
        ast.parse(patched)
        reports = patch.verify(patched, self.fixture_html())
        self.assertTrue(any("expected_topology" in r for r in reports))
        self.assertIn('@app.get("/api/topology")', patched)
        self.assertIn('@app.get("/api/node/{node_id}/quiz")', patched)
        self.assertIn('@app.post("/api/exam/build")', patched)
        self.assertIn('@app.post("/api/exam/submit")', patched)
        self.assertIn('json.dumps([{"node_id": node.id, "question_id": q.id} for node, q in selected]', patched)

    def test_repeat_patch_fails_closed(self):
        patched = patch.patch_source(self.fixture_api(), "\n", self.fixture_html())
        with self.assertRaises(ValueError):
            patch.patch_source(patched, "\n", self.fixture_html())

    def test_crlf_is_supported(self):
        source = self.fixture_api().replace("\n", "\r\n")
        patched = patch.patch_source(source, "\r\n", self.fixture_html())
        ast.parse(patched)

    def test_apply_creates_backups_and_leaves_html_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "app").mkdir()
            (root / "static").mkdir()
            api_path = root / "app" / "api.py"
            html_path = root / "static" / "index.html"
            api_path.write_text(self.fixture_api(), encoding="utf-8")
            original_html = self.fixture_html()
            html_path.write_text(original_html, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--project-root", str(root), "--apply"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            ast.parse(api_path.read_text(encoding="utf-8"))
            self.assertEqual(html_path.read_text(encoding="utf-8"), original_html)
            backups = list((root / "backups").glob("api-compat-*/api.py"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(encoding="utf-8"), self.fixture_api())

    def test_dry_run_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "app").mkdir()
            (root / "static").mkdir()
            api_path = root / "app" / "api.py"
            html_path = root / "static" / "index.html"
            original_api = self.fixture_api()
            original_html = self.fixture_html()
            api_path.write_text(original_api, encoding="utf-8")
            html_path.write_text(original_html, encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--project-root", str(root)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertEqual(api_path.read_text(encoding="utf-8"), original_api)
            self.assertEqual(html_path.read_text(encoding="utf-8"), original_html)
            self.assertFalse((root / "backups").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
