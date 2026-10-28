import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROJECT_MODULE = "Gestion de Projet IT"
AIOPS_MODULE = "AIOps & Intelligence Artificielle"


def _nodes():
    return json.loads((ROOT / "content" / "nodes.json").read_text(encoding="utf-8"))


def _word_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", text, flags=re.UNICODE))


def test_project_module_is_registered_in_the_served_frontend():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")

    assert "id: 'gestion-projet-it', label: 'Gestion de Projet IT'" in html
    assert "raw.toLowerCase() === 'gestion de projet it'" in html
    assert "id.startsWith('proj-')" in html


def test_aiops_module_is_registered_in_the_served_frontend():
    html = (ROOT / "static" / "index.html").read_text(encoding="utf-8")

    assert "id: 'aiops', label: 'AIOps & Intelligence Artificielle'" in html
    assert "raw === 'AIOps & Intelligence Artificielle'" in html
    assert "id.startsWith('aiops-')" in html


def test_project_catalog_has_18_complete_courses_and_quizzes():
    nodes = _nodes()
    by_id = {node["id"]: node for node in nodes}
    project_nodes = [node for node in nodes if node.get("module") == PROJECT_MODULE]
    aiops_nodes = [node for node in nodes if node.get("module") == AIOPS_MODULE]

    assert len(by_id) == len(nodes), "Les identifiants de nœuds doivent être uniques."
    assert len(project_nodes) == 18
    assert len(aiops_nodes) == 18, "L'ajout du projet ne doit pas retirer les cours AIOps."

    project_orders = [node["order"] for node in project_nodes]
    assert len(set(project_orders)) == 18
    assert min(project_orders) > max(
        node["order"] for node in nodes if node.get("module") != PROJECT_MODULE
    )

    for node in project_nodes:
        for prereq in node.get("prereqs", []):
            assert prereq in by_id, f"{node['id']} référence un prérequis absent : {prereq}"

        lesson = ROOT / "content" / "lessons" / f"{node['id']}.md"
        quiz_file = ROOT / "content" / "quiz" / f"{node['id']}.json"
        assert lesson.is_file(), f"Leçon manquante : {lesson.name}"
        assert _word_count(lesson) >= 5000, f"Leçon trop courte : {lesson.name}"
        assert quiz_file.is_file(), f"Quiz manquant : {quiz_file.name}"

        quiz = json.loads(quiz_file.read_text(encoding="utf-8"))
        assert quiz.get("node_id") == node["id"]
        questions = quiz.get("questions")
        assert isinstance(questions, list) and len(questions) == 5
        for question in questions:
            assert len(question.get("choices", [])) == 4
            assert question.get("answer") in range(4)
            assert question.get("prompt", "").strip()
            assert question.get("explanation", "").strip()
