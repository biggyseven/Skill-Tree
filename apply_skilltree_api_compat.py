#!/usr/bin/env python3
"""Correctifs ciblés de compatibilité Skill Tree (app/api.py ↔ static/index.html).

Exécuter depuis la racine du dépôt :
    python apply_skilltree_api_compat.py

Le script crée une sauvegarde datée, refuse les versions inattendues, puis
valide la syntaxe Python et les routes concernées. Il ne modifie pas index.html
et n'ajoute aucun endpoint de fonctionnalité qui n'existe pas déjà.
"""
from __future__ import annotations

import argparse
import ast
import sys
from datetime import datetime
from pathlib import Path


REPLACEMENTS: list[tuple[str, str, str]] = [
    (
        "lab textuel : ne pas exposer au panneau terminal Docker",
        '''        "lab": (
            {"kind": lab.kind, "prompt": lab.prompt, "hint": lab.hint} if lab is not None else None
        ),''',
        '''        # L'interface actuelle ne sait lancer qu'un lab Docker interactif.
        # Les labs historiques de type "text" ne doivent pas afficher un bouton
        # qui aboutit nécessairement à un HTTP 404 sur /api/lab/start.
        "lab": (
            {"kind": lab.kind, "prompt": lab.prompt, "hint": lab.hint}
            if lab is not None and lab.kind == "docker"
            else None
        ),''',
    ),
    (
        "alias exam/start attendu par l'interface",
        '''@app.post("/api/exam/generate")
def generate_exam(''',
        '''@app.post("/api/exam/generate")
@app.post("/api/exam/start")
def generate_exam(''',
    ),
    (
        "exam : ne tirer que des QCM affichables par l'interface",
        '''    for node in nodes:
        for question in tree.questions(node.id, ProofKind.QUIZ):
            pool.append((node, question))''',
        '''    for node in nodes:
        for question in tree.questions(node.id, ProofKind.QUIZ):
            # index.html fournit des choix radio uniquement pour les QCM.
            # Les questions input/terminal auraient un énoncé sans contrôle de réponse.
            if question.question_type != "qcm":
                continue
            pool.append((node, question))''',
    ),
    (
        "message clair quand aucune question QCM n'est disponible",
        '''        raise HTTPException(
            status_code=404,
            detail="Aucune question d'exercice dans cette catégorie.",
        )''',
        '''        raise HTTPException(
            status_code=404,
            detail="Aucune question QCM utilisable dans cette catégorie.",
        )''',
    ),
    (
        "exam : identifiant racine attendu par index.html",
        '''    return {
        "session_id": session_id,
        "category": category,
        "requested": EXAM_QUESTION_COUNT,''',
        '''    return {
        # id est le nom utilisé par static/index.html ; session_id est conservé
        # pour les clients qui consomment encore l'ancien contrat de l'API.
        "id": session_id,
        "session_id": session_id,
        "category": category,
        "requested": EXAM_QUESTION_COUNT,''',
    ),
    (
        "exam : accepter exam_id et l'ancien session_id à la soumission",
        '''    session_id = payload.get("session_id")
    answers = payload.get("answers")
    if not isinstance(session_id, str) or not session_id.strip():
        raise HTTPException(status_code=422, detail="Le champ session_id est obligatoire.")''',
        '''    # index.html envoie exam_id ; session_id reste accepté pour rétrocompatibilité.
    session_id = payload.get("exam_id") or payload.get("session_id")
    answers = payload.get("answers")
    if not isinstance(session_id, str) or not session_id.strip():
        raise HTTPException(
            status_code=422,
            detail="Le champ exam_id (ou session_id) est obligatoire.",
        )''',
    ),
    (
        "seuil d'examen inclusif et cohérent avec l'expiration serveur",
        '''    score = round(100 * correct_count / total) if total else 0
    passed = score > EXAM_PASS_SCORE
    now = int(time.time())
    time_expired = now > session["expires_at"] + EXAM_SUBMIT_GRACE_SECONDS''',
        '''    score = round(100 * correct_count / total) if total else 0
    now = int(time.time())
    time_expired = now > session["expires_at"] + EXAM_SUBMIT_GRACE_SECONDS
    # Un score exactement égal au seuil est réussi ; hors délai, le résultat
    # ne doit pas être présenté à l'interface comme un examen réussi.
    passed = score >= EXAM_PASS_SCORE and not time_expired''',
    ),
]


def route_pairs(source: str) -> set[tuple[str, str]]:
    tree = ast.parse(source)
    found: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.lower()
            if method not in {"get", "post", "put", "patch", "delete"} or not decorator.args:
                continue
            path = decorator.args[0]
            if isinstance(path, ast.Constant) and isinstance(path.value, str):
                found.add((method.upper(), path.value))
    return found


def verify(source: str) -> list[str]:
    """Valide la syntaxe et les contrats ciblés ; retourne les erreurs éventuelles."""
    errors: list[str] = []
    try:
        ast.parse(source, filename="app/api.py")
    except SyntaxError as exc:
        return [f"Syntaxe Python invalide : {exc}"]

    routes = route_pairs(source)
    required = {
        ("POST", "/api/lab/start"),
        ("POST", "/api/lab/exec"),
        ("POST", "/api/lab/validate"),
        ("POST", "/api/exam/generate"),
        ("POST", "/api/exam/start"),
        ("POST", "/api/exam/submit"),
        ("GET", "/api/topology"),
        ("POST", "/api/topology"),
    }
    for route in sorted(required - routes):
        errors.append(f"Route attendue absente : {route[0]} {route[1]}")

    checks = {
        "filtrage des questions non-QCM": 'if question.question_type != "qcm":' in source,
        "id d'examen attendu par l'interface": '"id": session_id,' in source,
        "soumission compatible exam_id/session_id": 'payload.get("exam_id") or payload.get("session_id")' in source,
        "seuil d'examen inclusif": "passed = score >= EXAM_PASS_SCORE and not time_expired" in source,
        "labs visibles limités au type Docker": 'lab is not None and lab.kind == "docker"' in source,
    }
    errors.extend(f"Contrôle échoué : {label}" for label, ok in checks.items() if not ok)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Racine du dépôt Skill Tree (défaut : dossier courant).")
    parser.add_argument("--check", action="store_true", help="Vérifie le fichier sans le modifier.")
    args = parser.parse_args()

    api_path = args.root.resolve() / "app" / "api.py"
    index_path = args.root.resolve() / "static" / "index.html"
    if not api_path.is_file():
        print(f"ERREUR : fichier introuvable : {api_path}", file=sys.stderr)
        return 2
    if not index_path.is_file():
        print(f"ERREUR : index.html introuvable : {index_path}", file=sys.stderr)
        return 2

    source = api_path.read_text(encoding="utf-8")
    if args.check:
        errors = verify(source)
        if errors:
            print("Échec des vérifications :\n- " + "\n- ".join(errors), file=sys.stderr)
            return 1
        print("OK : syntaxe Python et contrats /api/lab/*, /api/exam/*, /api/topology vérifiés.")
        return 0

    updated = source
    changed: list[str] = []
    for label, old, new in REPLACEMENTS:
        if new in updated:
            continue  # correctif déjà appliqué
        count = updated.count(old)
        if count != 1:
            print(
                f"ERREUR : impossible d'appliquer '{label}' : motif source trouvé {count} fois. "
                "Aucun fichier n'a été modifié. Vérifie la version de app/api.py.",
                file=sys.stderr,
            )
            return 3
        updated = updated.replace(old, new, 1)
        changed.append(label)

    errors = verify(updated)
    if errors:
        print("Le contenu calculé n'a pas passé les vérifications :\n- " + "\n- ".join(errors), file=sys.stderr)
        return 4

    if not changed:
        print("Aucun changement nécessaire : les correctifs sont déjà présents.")
        print("OK : syntaxe Python et contrats API vérifiés.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = api_path.with_name(f"api.py.bak-{stamp}")
    backup_path.write_text(source, encoding="utf-8")
    api_path.write_text(updated, encoding="utf-8", newline="\n")

    # Vérifie le fichier relu du disque pour éviter de déclarer un faux succès.
    final_errors = verify(api_path.read_text(encoding="utf-8"))
    if final_errors:
        api_path.write_text(source, encoding="utf-8", newline="\n")
        print("Vérification finale échouée ; la version originale a été restaurée.", file=sys.stderr)
        print("- " + "\n- ".join(final_errors), file=sys.stderr)
        return 5

    print("Correctifs appliqués à app/api.py :")
    for item in changed:
        print(f"  - {item}")
    print(f"Sauvegarde originale : {backup_path}")
    print("OK : syntaxe Python et contrats API vérifiés.")
    print("Note : ces contrôles statiques ne remplacent pas les tests d'intégration avec Docker et SQLite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
