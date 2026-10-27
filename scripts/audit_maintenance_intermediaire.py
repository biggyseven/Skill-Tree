from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
MIN_WORDS = 5000
MIN_DIAGRAMS = 6
EXPECTED = [
    ("maint-monitoring-intermediaire", "maint-securite-bases-debutant"),
    ("maint-sauvegarde-intermediaire", "maint-monitoring-intermediaire"),
    ("maint-maintenance-preventive-intermediaire", "maint-sauvegarde-intermediaire"),
    ("maint-gestion-parc-intermediaire", "maint-maintenance-preventive-intermediaire"),
    ("maint-procedure-intermediaire", "maint-gestion-parc-intermediaire"),
    ("maint-escalade-intermediaire", "maint-procedure-intermediaire"),
    ("maint-itil-intermediaire", "maint-escalade-intermediaire"),
    ("maint-rca-intermediaire", "maint-itil-intermediaire"),
    ("maint-sla-intermediaire", "maint-rca-intermediaire"),
    ("maint-reporting-technique-intermediaire", "maint-sla-intermediaire"),
    ("maint-reporting-mensuel-intermediaire", "maint-reporting-technique-intermediaire"),
    ("maint-automatisation-intermediaire", "maint-reporting-mensuel-intermediaire"),
]
REQUIRED_SECTIONS = (
    "Mise en contexte",
    "Atelier pratique",
    "Exercices d'application avec corrigés",
    "Défi final",
)


def word_count(text: str) -> int:
    return len(re.findall(r"[\wÀ-ÿ]+(?:['’\-][\wÀ-ÿ]+)*", text, flags=re.UNICODE))


def diagram_count(text: str) -> int:
    mermaid = len(re.findall(r"(?m)^\s*```mermaid\s*$", text))
    svg = len(re.findall(r"<svg\b", text, flags=re.IGNORECASE))
    ascii_diagrams = 0
    for block in re.findall(r"```(?:text|ascii)\s*\n(.*?)\n```", text, flags=re.DOTALL | re.IGNORECASE):
        if re.search(r"(-->|──|→|┌|┐|└|┘|├|┤|\+[-+|]{2,})", block):
            ascii_diagrams += 1
    return mermaid + svg + ascii_diagrams


def main() -> int:
    errors: list[str] = []
    try:
        nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERREUR: impossible de lire content/nodes.json: {exc}")
        return 1

    by_id = {node.get("id"): node for node in nodes if isinstance(node, dict) and isinstance(node.get("id"), str)}
    print("Audit du parcours Maintenance & Reporting — niveau intermédiaire")

    for node_id, expected_prereq in EXPECTED:
        lesson_path = CONTENT / "lessons" / f"{node_id}.md"
        quiz_path = CONTENT / "quiz" / f"{node_id}.json"
        node = by_id.get(node_id)

        if node is None:
            errors.append(f"{node_id}: nœud absent de content/nodes.json")
        else:
            if node.get("module") != "Maintenance & Reporting":
                errors.append(f"{node_id}: module inattendu ({node.get('module')!r})")
            if node.get("prereqs") != [expected_prereq]:
                errors.append(f"{node_id}: prérequis {node.get('prereqs')!r}, attendu [{expected_prereq!r}]")
            if not any(req.get("kind") == "quiz" for req in node.get("requirements", []) if isinstance(req, dict)):
                errors.append(f"{node_id}: exigence de quiz absente")

        if not lesson_path.is_file():
            errors.append(f"{node_id}: cours Markdown absent")
            continue

        try:
            lesson = lesson_path.read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{node_id}: lecture du cours impossible ({exc})")
            continue

        words = word_count(lesson)
        diagrams = diagram_count(lesson)
        missing_sections = [section for section in REQUIRED_SECTIONS if section.casefold() not in lesson.casefold()]

        if words < MIN_WORDS:
            errors.append(f"{node_id}: {words} mots, minimum {MIN_WORDS}")
        if diagrams < MIN_DIAGRAMS:
            errors.append(f"{node_id}: {diagrams} schémas, minimum {MIN_DIAGRAMS}")
        if missing_sections:
            errors.append(f"{node_id}: sections absentes: {', '.join(missing_sections)}")
        if re.search(r"(?m)^\s*---\s*$", lesson):
            errors.append(f"{node_id}: séparateur horizontal YAML/Markdown interdit")
        if re.search(r"\[Contenu à rédiger\]|\bTODO\b", lesson, flags=re.IGNORECASE):
            errors.append(f"{node_id}: texte provisoire détecté")

        if not quiz_path.is_file():
            errors.append(f"{node_id}: quiz homonyme absent")
            question_count = 0
        else:
            try:
                quiz = json.loads(quiz_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{node_id}: JSON de quiz invalide ({exc})")
                quiz = {}
            if quiz.get("node_id") != node_id:
                errors.append(f"{node_id}: node_id incohérent dans le quiz")
            questions = quiz.get("questions", [])
            question_count = len(questions) if isinstance(questions, list) else 0
            if question_count != 10:
                errors.append(f"{node_id}: {question_count} questions, attendu 10")
            if not isinstance(questions, list):
                questions = []
            for index, question in enumerate(questions, start=1):
                if not isinstance(question, dict):
                    errors.append(f"{node_id}: question {index} n'est pas un objet")
                    continue
                prompt = str(question.get("prompt", "")).strip()
                choices = question.get("choices", [])
                answer = question.get("answer")
                if not prompt or re.match(r"question (?:temporaire|provisoire)", prompt, flags=re.IGNORECASE):
                    errors.append(f"{node_id}: question {index} vide ou provisoire")
                if not isinstance(choices, list) or len(choices) < 2:
                    errors.append(f"{node_id}: question {index} sans choix suffisants")
                if not isinstance(answer, int) or isinstance(answer, bool) or not isinstance(choices, list) or answer < 0 or answer >= len(choices):
                    errors.append(f"{node_id}: réponse invalide à la question {index}")

        print(f"  {node_id}: {words} mots | {diagrams} schémas | {question_count} questions")

    if errors:
        print(f"ÉCHEC: {len(errors)} problème(s)")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("SUCCÈS: les 12 nœuds, cours, schémas, prérequis et quiz respectent les seuils.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
