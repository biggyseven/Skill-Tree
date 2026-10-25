#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Répare les banques JSON quiz/exam pour respecter le contrat d'app.loader.

À lancer depuis la racine du dépôt : python fix_all_json_files.py
Les fichiers modifiés sont sauvegardés une seule fois en *.json.bak. Les banques
qui ciblent un node_id absent de content/nodes.json sont déplacées dans
content/_quarantine_json/ au lieu d'être détruites ou associées à un mauvais nœud.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

NODE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
VALID_QUESTION_TYPES = {"qcm", "input", "terminal"}
DEFAULT_CHOICES = [
    "La première proposition",
    "La deuxième proposition",
    "Information insuffisante",
    "Aucune des propositions précédentes",
]


def read_json(path: Path) -> Any:
    """Lit un JSON UTF-8 avec ou sans BOM."""
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_node_ids(content_dir: Path) -> set[str]:
    """Charge les identifiants valides de content/nodes.json."""
    nodes_path = content_dir / "nodes.json"
    if not nodes_path.is_file():
        raise RuntimeError(f"Fichier obligatoire introuvable : {nodes_path}")
    try:
        raw_nodes = read_json(nodes_path)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Impossible de lire {nodes_path} : {exc}") from exc
    if not isinstance(raw_nodes, list):
        raise RuntimeError(f"{nodes_path} : la racine doit être une liste de nœuds.")

    ids: set[str] = set()
    invalid: list[str] = []
    for index, raw in enumerate(raw_nodes, 1):
        node_id = raw.get("id") if isinstance(raw, dict) else None
        if isinstance(node_id, str) and NODE_ID_RE.fullmatch(node_id):
            ids.add(node_id)
        else:
            invalid.append(f"entrée {index}")
    if invalid:
        print(
            f"⚠️ {len(invalid)} entrée(s) de nodes.json ont un id absent/invalide : "
            + ", ".join(invalid[:10]),
            file=sys.stderr,
        )
    if not ids:
        raise RuntimeError(f"Aucun id de nœud valide trouvé dans {nodes_path}.")
    return ids


def placeholder_question(node_id: str, index: int, reason: str) -> dict[str, Any]:
    readable = node_id.replace("-", " ").replace("_", " ")
    return {
        "type": "qcm",
        "prompt": (
            f"Question de secours pour {readable} (question {index}) : "
            f"le contenu doit être complété. Motif : {reason}."
        ),
        "choices": DEFAULT_CHOICES.copy(),
        "answer": 2,
        "explanation": (
            "Question technique provisoire générée pour permettre le chargement. "
            "Remplacer cette question par une question pédagogique vérifiée."
        ),
    }


def is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def valid_choices(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(is_nonempty_string(item) for item in value)
        and len({item.strip() for item in value}) == 4
    )


def normalize_question(raw: Any, node_id: str, index: int) -> dict[str, Any]:
    """Normalise une question selon le validateur réel du loader."""
    if not isinstance(raw, dict):
        return placeholder_question(node_id, index, "la question n'est pas un objet JSON")

    prompt = raw.get("prompt")
    if not is_nonempty_string(prompt):
        prompt = f"Question provisoire sur {node_id.replace('-', ' ')} (question {index}) ?"
    else:
        prompt = prompt.strip()

    explanation = raw.get("explanation", "")
    if not isinstance(explanation, str):
        explanation = ""
    else:
        explanation = explanation.strip()

    raw_type = raw.get("type", "qcm")
    question_type = raw_type.strip().lower() if isinstance(raw_type, str) else "qcm"
    if question_type not in VALID_QUESTION_TYPES:
        question_type = "qcm"

    if question_type == "qcm":
        choices = raw.get("choices")
        if valid_choices(choices):
            choices = [item.strip() for item in choices]
        else:
            choices = DEFAULT_CHOICES.copy()

        answer = raw.get("answer")
        if isinstance(answer, str) and answer.strip().isdigit():
            answer = int(answer.strip())
        if not isinstance(answer, int) or isinstance(answer, bool) or not 0 <= answer <= 3:
            answer = 2

        return {
            "type": "qcm",
            "prompt": prompt,
            "choices": choices,
            "answer": answer,
            "explanation": explanation,
        }

    # Pour input/terminal, le loader exige une réponse non vide et une regex valide
    # qui correspond intégralement à la réponse. Une question non réparable est
    # convertie en QCM provisoire plutôt que de bloquer toute la synchronisation.
    answer = raw.get("answer")
    pattern = raw.get("regex")
    if is_nonempty_string(answer) and is_nonempty_string(pattern):
        answer = answer.strip()
        pattern = pattern.strip()
        try:
            compiled = re.compile(pattern)
            if compiled.fullmatch(answer, re.IGNORECASE) is not None:
                return {
                    "type": question_type,
                    "prompt": prompt,
                    "answer": answer,
                    "regex": pattern,
                    "explanation": explanation,
                }
        except re.error:
            pass

    fallback = placeholder_question(node_id, index, "réponse ou expression régulière invalide")
    fallback["prompt"] = prompt
    fallback["explanation"] = explanation or fallback["explanation"]
    return fallback


def normalize_payload(payload: Any, path: Path, scope: str) -> tuple[dict[str, Any], list[str]]:
    """Produit un objet conforme au schéma attendu sans modifier le fond valide."""
    changes: list[str] = []
    node_id = path.stem

    # Une racine-liste peut déjà contenir les questions : on la conserve.
    if isinstance(payload, list):
        payload = {"questions": payload}
        changes.append("racine-liste convertie en objet")
    elif not isinstance(payload, dict):
        payload = {}
        changes.append("racine JSON invalide remplacée par un objet minimal")

    payload = dict(payload)
    if payload.get("node_id") != node_id:
        payload["node_id"] = node_id
        changes.append(f"node_id défini à {node_id!r}")

    if payload.get("scope") != scope:
        payload["scope"] = scope
        changes.append(f"scope défini à {scope!r}")

    raw_questions = payload.get("questions")
    if not isinstance(raw_questions, list) or not raw_questions:
        raw_questions = [placeholder_question(node_id, 1, "liste questions absente, invalide ou vide")]
        changes.append("questions remplacé par une liste contenant une question de secours")
    else:
        normalized: list[dict[str, Any]] = []
        prompts_seen: set[str] = set()
        for index, raw_question in enumerate(raw_questions, 1):
            question = normalize_question(raw_question, node_id, index)
            # _parse_bank rejette les prompts dupliqués après normalisation espaces/casse.
            base_prompt = question["prompt"]
            key = " ".join(base_prompt.lower().split())
            if key in prompts_seen:
                question["prompt"] = f"{base_prompt} (question {index})"
                key = " ".join(question["prompt"].lower().split())
                suffix = 2
                while key in prompts_seen:
                    question["prompt"] = f"{base_prompt} (question {index}-{suffix})"
                    key = " ".join(question["prompt"].lower().split())
                    suffix += 1
                changes.append(f"prompt dupliqué corrigé à la question {index}")
            prompts_seen.add(key)
            normalized.append(question)

            if raw_question != question:
                changes.append(f"question {index} normalisée")
        raw_questions = normalized

    payload["questions"] = raw_questions
    return payload, changes


def atomic_write_json(path: Path, payload: dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="\n", dir=path.parent,
        prefix=f".{path.name}.", suffix=".tmp", delete=False
    ) as handle:
        temporary = Path(handle.name)
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    try:
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def backup_once(path: Path, dry_run: bool) -> Path:
    backup = path.with_suffix(path.suffix + ".bak")
    if not dry_run and not backup.exists():
        shutil.copy2(path, backup)
    return backup


def quarantine(path: Path, content_dir: Path, dry_run: bool) -> Path:
    rel = path.relative_to(content_dir)
    destination = content_dir / "_quarantine_json" / rel
    if destination.exists():
        stem, suffix = destination.stem, destination.suffix
        counter = 2
        while destination.exists():
            destination = destination.with_name(f"{stem}-{counter}{suffix}")
            counter += 1
    if not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(destination))
    return destination


def repair(content_dir: Path, dry_run: bool = False) -> int:
    node_ids = load_node_ids(content_dir)
    folders = [(content_dir / "quiz", "quiz"), (content_dir / "exam", "exam"), (content_dir / "exams", "exam")]
    files: list[tuple[Path, str]] = []
    for folder, scope in folders:
        if folder.is_dir():
            files.extend((path, scope) for path in sorted(folder.glob("*.json")) if path.is_file())

    if not files:
        print(f"Aucun fichier JSON de quiz/examen trouvé dans {content_dir}.")
        return 0

    changed_files = 0
    quarantined_files = 0
    errors: list[str] = []

    print(f"Dossier de contenu : {content_dir.resolve()}")
    print(f"Nœuds connus : {len(node_ids)} | Fichiers JSON inspectés : {len(files)}")
    if (content_dir / "exams").is_dir():
        print("⚠️ Le loader actuel charge content/exam (singulier), pas content/exams.")

    for path, expected_scope in files:
        node_id = path.stem
        if not NODE_ID_RE.fullmatch(node_id):
            destination = quarantine(path, content_dir, dry_run)
            quarantined_files += 1
            print(f"⚠️ {path.relative_to(content_dir)} : nom de fichier invalide; placé en quarantaine -> {destination.relative_to(content_dir)}")
            continue
        if node_id not in node_ids:
            destination = quarantine(path, content_dir, dry_run)
            quarantined_files += 1
            print(
                f"⚠️ {path.relative_to(content_dir)} : node_id {node_id!r} absent de nodes.json; "
                f"fichier préservé en quarantaine -> {destination.relative_to(content_dir)}"
            )
            continue

        raw_bytes = path.read_bytes()
        original_had_bom = raw_bytes.startswith(b"\xef\xbb\xbf")
        try:
            payload = json.loads(raw_bytes.decode("utf-8-sig"))
            parse_failed = False
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            parse_failed = True
            payload = {}
            print(f"⚠️ {path.relative_to(content_dir)} : JSON irrécupérable ({exc}); un .bak sera conservé.")

        normalized, changes = normalize_payload(payload, path, expected_scope)
        if parse_failed:
            changes.insert(0, "JSON illisible remplacé par un quiz de secours")
        if original_had_bom:
            changes.append("BOM UTF-8 supprimé")

        # Vérification finale des champs principaux avant écriture.
        if not isinstance(normalized.get("node_id"), str) or normalized["node_id"] != node_id:
            errors.append(f"{path}: node_id final invalide")
            continue
        if normalized.get("scope") != expected_scope:
            errors.append(f"{path}: scope final invalide")
            continue
        questions = normalized.get("questions")
        if not isinstance(questions, list) or not questions:
            errors.append(f"{path}: questions final invalide")
            continue

        if changes:
            backup = backup_once(path, dry_run)
            atomic_write_json(path, normalized, dry_run)
            changed_files += 1
            action = "À réparer" if dry_run else "Réparé"
            print(f"{action}: {path.relative_to(content_dir)} ({'; '.join(dict.fromkeys(changes))})")
            if not dry_run:
                print(f"  Sauvegarde : {backup.relative_to(content_dir)}")

    print("\nBilan")
    print(f"  Fichiers inspectés : {len(files)}")
    print(f"  Fichiers à réparer/réparés : {changed_files}")
    print(f"  Fichiers mis en quarantaine : {quarantined_files}")
    print(f"  Mode simulation : {'oui' if dry_run else 'non'}")
    if errors:
        print("Erreurs non résolues :", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        return 2
    print("✅ Validation structurelle terminée.")
    print("⚠️ Les questions de secours doivent être remplacées par du contenu pédagogique réel.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--content-dir", type=Path,
        default=Path(__file__).resolve().parent / "content",
        help="Dossier content/ (par défaut : content/ à côté du script)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Affiche les corrections prévues sans écrire ni déplacer de fichiers",
    )
    args = parser.parse_args()
    try:
        return repair(args.content_dir.resolve(), dry_run=args.dry_run)
    except (OSError, RuntimeError) as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
