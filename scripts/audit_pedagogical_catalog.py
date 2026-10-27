from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
LEVELS = {"debutant", "intermediaire", "expert"}
PLACEHOLDER_RE = re.compile(
    r"question temporaire|quiz généré automatiquement|question placeholder|avez-vous bien lu ce cours|avez-vous lu le cours",
    re.IGNORECASE,
)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        nodes = json.loads((CONTENT / "nodes.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERREUR: impossible de lire content/nodes.json: {exc}")
        return 1

    ids = [node.get("id") for node in nodes]
    known = {node_id for node_id in ids if isinstance(node_id, str)}
    if len(ids) != len(known):
        errors.append("Identifiants de nœuds dupliqués ou invalides.")
    for node in nodes:
        for prereq in node.get("prereqs", []):
            if prereq not in known:
                errors.append(f"{node.get('id')}: prérequis inconnu {prereq}")

    lessons: dict[str, Path] = {}
    empty_drafts: dict[str, Path] = {}
    for path in sorted((CONTENT / "lessons").glob("*.md")):
        try:
            content = path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            errors.append(f"Lecture impossible de {path.name}: {exc}")
            continue
        if not content:
            # Fichiers créés avant le contenu/nœud : conservés comme brouillons,
            # mais exclus du catalogue actif tant qu'ils restent vides.
            empty_drafts[path.stem] = path
            continue
        lessons[path.stem] = path
    quizzes = {path.stem: path for path in (CONTENT / "quiz").glob("*.json")}
    for lesson_id in sorted(lessons):
        if lesson_id not in known:
            errors.append(f"Cours sans nœud: {lesson_id}")
        if lesson_id not in quizzes:
            errors.append(f"Cours sans quiz homonyme: {lesson_id}")
    for quiz_id, path in sorted(quizzes.items()):
        if quiz_id not in known:
            errors.append(f"Quiz sans nœud: {quiz_id}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"Quiz JSON invalide {path.name}: {exc}")
            continue
        if payload.get("node_id") != quiz_id:
            errors.append(f"{path.name}: node_id incohérent ({payload.get('node_id')!r})")
        questions = payload.get("questions")
        if not isinstance(questions, list) or not questions:
            errors.append(f"{path.name}: liste de questions vide ou invalide")
            continue
        for index, question in enumerate(questions, 1):
            if not isinstance(question, dict):
                errors.append(f"{path.name}: question {index} n'est pas un objet")
                continue
            prompt = str(question.get("prompt", "")).strip()
            choices = question.get("choices", [])
            if not prompt or not isinstance(choices, list) or len(choices) < 2:
                errors.append(f"{path.name}: question {index} sans prompt ou choix suffisants")
            if question.get("type", "qcm") == "qcm":
                answer = question.get("answer")
                if not isinstance(answer, int) or isinstance(answer, bool) or answer < 0 or answer >= len(choices):
                    errors.append(f"{path.name}: réponse invalide à la question {index}")

    tracks: dict[str, set[str]] = defaultdict(set)
    for lesson_id in lessons:
        match = re.match(r"^(.*)-(debutant|intermediaire|expert)$", lesson_id)
        if match:
            tracks[match.group(1)].add(match.group(2))
    missing_tracks = {topic: sorted(LEVELS - levels) for topic, levels in tracks.items() if LEVELS - levels}
    placeholder_quizzes = []
    for quiz_id, path in quizzes.items():
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        quiz_questions = payload.get("questions", [])
        all_text = " ".join(
            str(question.get("prompt", "")) + " " + str(question.get("explanation", "")
            )
            for question in quiz_questions if isinstance(question, dict)
        )
        if PLACEHOLDER_RE.search(all_text):
            placeholder_quizzes.append(quiz_id)
    short_lessons = [
        (lesson_id, path.stat().st_size)
        for lesson_id, path in lessons.items()
        if path.stat().st_size < 8000 and not lesson_id.startswith(("challenge-", "lab_"))
    ]

    print("Audit du catalogue pédagogique Skill-Tree")
    print(f"  Nœuds: {len(nodes)} | cours Markdown actifs: {len(lessons)} | quiz: {len(quizzes)}")
    print(f"  Brouillons Markdown vides ignorés: {len(empty_drafts)}")
    print(f"  Erreurs de rattachement/structure: {len(errors)}")
    print(f"  Parcours incomplets en niveaux: {len(missing_tracks)}")
    for topic, missing in sorted(missing_tracks.items()):
        warnings.append(f"{topic}: niveaux manquants {', '.join(missing)}")
    print(f"  Quiz contenant un marqueur de placeholder: {len(placeholder_quizzes)}")
    print(f"  Cours courts (< 8000 octets): {len(short_lessons)}")
    if warnings:
        print("  Lacunes de niveaux (aperçu): " + "; ".join(warnings[:12]))
    if placeholder_quizzes:
        print("  Quiz placeholders (aperçu): " + ", ".join(sorted(placeholder_quizzes)[:15]))
    if short_lessons:
        print("  Cours courts (aperçu): " + ", ".join(f"{name} ({size})" for name, size in sorted(short_lessons)[:8]))
    for error in errors:
        print(f"ERREUR: {error}")
    if errors:
        return 1
    print("Audit structurel réussi; les lacunes pédagogiques recensées restent à traiter par lots.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
