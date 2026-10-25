#!/usr/bin/env python3
"""Patch additif et prudent pour aligner app/api.py sur static/index.html.

Par défaut, le script ne modifie rien (--dry-run implicite). Utiliser --apply
pour écrire après validation des ancres, sauvegarde horodatée et contrôles AST.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import re
import shutil
import sys
from pathlib import Path


QUIZ_ROUTE = '''@app.get("/api/node/{node_id}/quiz")
def read_quiz(node_id: str, tree: SkillTree = Depends(get_tree)) -> dict[str, Any]:
    """Fournit uniquement l'énoncé et les choix; les réponses restent côté serveur."""
    try:
        tree.playable(node_id)
    except DomainError as error:
        raise HTTPException(status_code=409, detail=str(error))

    questions = tree.questions(node_id, ProofKind.QUIZ)
    if not questions:
        raise HTTPException(status_code=404, detail="Aucun quiz défini pour ce cours.")
    return {
        "questions": [
            {
                "id": question.id,
                "type": question.question_type,
                "prompt": question.prompt,
                "choices": list(question.choices),
            }
            for question in questions
        ]
    }


'''

EXAM_ROUTES = '''@app.post("/api/exam/build")
def exam_build(payload: dict[str, Any] = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    """Construit un examen filtré par les nœuds envoyés par l'interface."""
    raw_node_ids = payload.get("node_ids")
    if not isinstance(raw_node_ids, list) or not raw_node_ids:
        raise HTTPException(status_code=422, detail="node_ids doit être une liste non vide.")
    if len(raw_node_ids) > 500 or any(not isinstance(value, str) or not value.strip() for value in raw_node_ids):
        raise HTTPException(status_code=422, detail="Liste node_ids invalide.")

    node_ids = list(dict.fromkeys(value.strip() for value in raw_node_ids))
    count = payload.get("count", EXAM_QUESTION_COUNT)
    time_limit = payload.get("time_limit", EXAM_DURATION_SECONDS)
    if type(count) is not int or not 1 <= count <= 100:
        raise HTTPException(status_code=422, detail="count doit être un entier entre 1 et 100.")
    if type(time_limit) is not int or not 60 <= time_limit <= 3600:
        raise HTTPException(status_code=422, detail="time_limit doit être compris entre 60 et 3600 secondes.")

    available_nodes = {node.id: node for node in tree.nodes()}
    unknown = [node_id for node_id in node_ids if node_id not in available_nodes]
    if unknown:
        raise HTTPException(status_code=404, detail={"message": "Cours inconnus.", "node_ids": unknown})

    pool = [
        (available_nodes[node_id], question)
        for node_id in node_ids
        for question in tree.questions(node_id, ProofKind.QUIZ)
    ]
    if not pool:
        raise HTTPException(status_code=422, detail="Aucune question de quiz dans ce périmètre.")

    selected = random.sample(pool, min(count, len(pool)))
    now = int(time.time())
    session_id = uuid.uuid4().hex
    module = str(payload.get("module") or "custom")
    levels = payload.get("levels", [])
    if not isinstance(levels, list) or any(not isinstance(level, str) for level in levels):
        raise HTTPException(status_code=422, detail="levels doit être une liste de chaînes.")

    # Stockage des couples nœud/question : aucun changement de schéma SQLite requis.
    question_refs = [{"node_id": node.id, "question_id": question.id} for node, question in selected]
    tree.conn.execute(
        "INSERT INTO exam_sessions (session_id, category, question_ids, started_at, expires_at) VALUES (?, ?, ?, ?, ?)",
        (session_id, module, json.dumps(question_refs, ensure_ascii=False), now, now + time_limit),
    )
    tree.conn.commit()
    return {
        "id": session_id,
        "category": module,
        "module": module,
        "levels": levels,
        "time_limit": time_limit,
        "duration_seconds": time_limit,
        "questions": [
            {"id": question.id, "type": question.question_type, "prompt": question.prompt, "choices": list(question.choices)}
            for _, question in selected
        ],
    }


@app.post("/api/exam/submit")
def exam_submit(payload: dict[str, Any] = Body(...), tree: SkillTree = Depends(get_tree)) -> dict:
    """Corrige un examen côté serveur et rend la soumission idempotente."""
    session_id = payload.get("session_id")
    answers = payload.get("answers")
    if not isinstance(session_id, str) or not session_id.strip():
        raise HTTPException(status_code=422, detail="session_id manquant ou invalide.")
    if not isinstance(answers, list):
        raise HTTPException(status_code=422, detail="answers doit être une liste.")

    # Table additive indépendante; les sessions existantes restent compatibles.
    tree.conn.execute(
        "CREATE TABLE IF NOT EXISTS exam_submissions ("
        "session_id TEXT PRIMARY KEY, submitted_at INTEGER NOT NULL, result_json TEXT NOT NULL, passed INTEGER NOT NULL DEFAULT 0)"
    )
    previous = tree.conn.execute(
        "SELECT result_json FROM exam_submissions WHERE session_id = ?", (session_id,)
    ).fetchone()
    if previous:
        try:
            return json.loads(previous["result_json"])
        except (TypeError, ValueError, KeyError):
            raise HTTPException(status_code=500, detail="Résultat d'examen enregistré illisible.")

    session = tree.conn.execute(
        "SELECT session_id, category, question_ids, started_at, expires_at FROM exam_sessions WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if not session:
        raise HTTPException(status_code=404, detail="Session d'examen introuvable. Relance l'examen.")
    if int(time.time()) > int(session["expires_at"]) + EXAM_SUBMIT_GRACE_SECONDS:
        raise HTTPException(status_code=409, detail="Session expirée. Relance l'examen.")

    try:
        stored_refs = json.loads(session["question_ids"] or "[]")
    except (TypeError, ValueError):
        raise HTTPException(status_code=500, detail="La liste des questions de cette session est invalide.")
    all_nodes = {node.id: node for node in tree.nodes()}
    selected: list[tuple[Node, Question]] = []

    if stored_refs and isinstance(stored_refs[0], dict):
        # Format utilisé par le correctif et par les sessions créées depuis /api/exam/build.
        cache: dict[str, dict[str, Question]] = {}
        for ref in stored_refs:
            node_id = ref.get("node_id")
            question_id = ref.get("question_id")
            if node_id not in all_nodes or not isinstance(question_id, str):
                raise HTTPException(status_code=409, detail="Une question de la session n'existe plus.")
            if node_id not in cache:
                cache[node_id] = {q.id: q for q in tree.questions(node_id, ProofKind.QUIZ)}
            question = cache[node_id].get(question_id)
            if question is None:
                raise HTTPException(status_code=409, detail="Une question de la session n'existe plus.")
            selected.append((all_nodes[node_id], question))
    else:
        # Compatibilité avec les sessions créées avant le patch, qui ne stockaient que q.id.
        legacy_nodes = [node for node in tree.nodes() if node.category == session["category"]]
        by_id: dict[str, list[tuple[Node, Question]]] = {}
        for node in legacy_nodes:
            for question in tree.questions(node.id, ProofKind.QUIZ):
                by_id.setdefault(question.id, []).append((node, question))
        for question_id in stored_refs:
            candidates = by_id.get(question_id, []) if isinstance(question_id, str) else []
            if len(candidates) != 1:
                raise HTTPException(
                    status_code=409,
                    detail="Cette ancienne session ne peut pas être associée sans ambiguïté à ses questions. Relance l'examen.",
                )
            selected.append(candidates[0])

    if not selected:
        raise HTTPException(status_code=409, detail="La session ne contient aucune question exploitable.")
    if len(answers) != len(selected):
        raise HTTPException(status_code=422, detail=f"Nombre de réponses incorrect : {len(answers)} reçues pour {len(selected)} questions.")

    details = []
    correct = 0
    for (_, question), answer in zip(selected, answers):
        if answer is None:
            matches = False
        elif question.question_type in {"input", "terminal"}:
            matches = _answer_matches(
                question.answer_regex or "", str(answer), terminal=question.question_type == "terminal"
            )
        else:
            matches = answer == question.answer
        correct += int(matches)
        details.append({
            "id": question.id,
            "correct": matches,
            "answer": question.answer,
            "explanation": question.explanation,
        })

    total = len(selected)
    score = round(100 * correct / total)
    result = {
        "success": True,
        "score": score,
        "passed": score >= EXAM_PASS_SCORE,
        "correct": correct,
        "total": total,
        "details": details,
        "submitted_at": int(time.time()),
    }
    tree.conn.execute(
        "INSERT OR IGNORE INTO exam_submissions (session_id, submitted_at, result_json, passed) VALUES (?, ?, ?, ?)",
        (session_id, result["submitted_at"], json.dumps(result, ensure_ascii=False), int(result["passed"])),
    )
    tree.conn.commit()
    # En cas de double soumission concurrente, renvoyer le résultat canonique enregistré.
    saved = tree.conn.execute(
        "SELECT result_json FROM exam_submissions WHERE session_id = ?", (session_id,)
    ).fetchone()
    return json.loads(saved["result_json"]) if saved else result


'''

TOPOLOGY_GET_ROUTE = '''@app.get("/api/topology")
def read_topology(tree: SkillTree = Depends(get_tree)) -> dict:
    """Renvoie la dernière topologie sauvegardée, au format attendu par Drawflow."""
    row = tree.conn.execute(
        "SELECT data FROM topologies ORDER BY updated_at DESC, rowid DESC LIMIT 1"
    ).fetchone()
    if not row:
        return {}
    try:
        data = json.loads(row["data"])
    except (TypeError, ValueError, KeyError):
        raise HTTPException(status_code=500, detail="La topologie sauvegardée est invalide.")
    if not isinstance(data, dict):
        raise HTTPException(status_code=500, detail="Le format de la topologie sauvegardée est invalide.")
    return data


'''


def insert_before_once(source: str, anchor: str, block: str, label: str, newline: str) -> str:
    count = source.count(anchor)
    if count != 1:
        raise ValueError(f"Ancre {label!r} attendue une fois, trouvée {count}. Aucun fichier n'a été écrit.")
    return source.replace(anchor, block.replace("\n", newline) + anchor, 1)


def patch_source(source: str, newline: str, html_text: str) -> str:
    # Détecte un patch déjà appliqué pour éviter les routes dupliquées.
    if '@app.get("/api/node/{node_id}/quiz")' in source:
        raise ValueError("La route GET quiz existe déjà; examen manuel requis, aucune modification faite.")
    if 'challenge_payload = None' in source or 'stored_exam_passes' in source:
        raise ValueError("Le correctif semble déjà appliqué; examen manuel requis, aucune modification faite.")
    if '@app.post("/api/exam/build")' in source or '@app.post("/api/exam/submit")' in source:
        raise ValueError("Une route examen à ajouter existe déjà; examen manuel requis, aucune modification faite.")
    if '@app.get("/api/topology")' in source:
        raise ValueError("La route GET topology existe déjà; examen manuel requis, aucune modification faite.")

    # L'endpoint GET /api/node expose le défi sans sa topologie attendue; l'interface ne peut donc pas lancer le défi.
    challenge_anchor = '    challenge = _challenge_row(tree, node.id)'
    challenge_block = (
        '    challenge_payload = None\n'
        '    if challenge:\n'
        '        expected_topology = challenge["expected_topology"]\n'
        '        if isinstance(expected_topology, str):\n'
        '            try:\n'
        '                expected_topology = json.loads(expected_topology)\n'
        '            except (TypeError, ValueError):\n'
        '                expected_topology = None\n'
        '        challenge_payload = {"prompt": node.description, "time_limit": challenge["time_limit"], "expected_topology": expected_topology}\n'
        '\n'
    )
    source = insert_before_once(source, challenge_anchor, challenge_block, "initialisation challenge", newline)
    challenge_old = '"challenge": {"prompt": node.description, "time_limit": challenge["time_limit"]} if challenge else None,'
    challenge_new = '"challenge": challenge_payload,'
    if source.count(challenge_old) != 1:
        raise ValueError("Expression du payload challenge attendue une fois. Aucun fichier n'a été écrit.")
    source = source.replace(challenge_old, challenge_new, 1)

    # Le seuil d'examen du front-end est la référence : l'interface indique 70 %.
    frontend_score = re.search(r"\bconst\s+PASS_SCORE\s*=\s*(\d+)\s*;", html_text)
    if not frontend_score:
        raise ValueError("Constante PASS_SCORE introuvable dans static/index.html; impossible d'aligner le seuil sans deviner.")
    score_old = re.search(r"(?m)^EXAM_PASS_SCORE\s*=\s*\d+\s*$", source)
    if not score_old:
        raise ValueError("Constante EXAM_PASS_SCORE introuvable dans app/api.py; aucune modification faite.")
    if len(re.findall(r"(?m)^EXAM_PASS_SCORE\s*=\s*\d+\s*$", source)) != 1:
        raise ValueError("Plusieurs constantes EXAM_PASS_SCORE trouvées; adaptation manuelle requise.")
    source = source[:score_old.start()] + f"EXAM_PASS_SCORE = {int(frontend_score.group(1))}" + source[score_old.end():]

    # La statistique profil comptait les examens dans attempts, mais aucune route de soumission
    # n'en créait. Compter séparément les sessions envoyées par cette nouvelle route.
    profile_anchor = '    exams = tree.conn.execute("SELECT COUNT(*) FROM attempts WHERE kind=\'exam\' AND passed=1").fetchone()[0]'
    profile_count = source.count(profile_anchor)
    if profile_count != 1:
        raise ValueError(f"Requête de compteur d'examens du profil attendue une fois, trouvée {profile_count}.")
    profile_block = (
        newline +
        '    try:' + newline +
        '        stored_exam_passes = tree.conn.execute("SELECT COUNT(*) FROM exam_submissions WHERE passed = 1").fetchone()[0]' + newline +
        '        exams += int(stored_exam_passes or 0)' + newline +
        '    except sqlite3.OperationalError:' + newline +
        '        # Table creee lors de la premiere soumission.' + newline +
        '        pass' + newline
    )
    source = source.replace(profile_anchor, profile_anchor + profile_block, 1)

    source = insert_before_once(source, '@app.post("/api/node/{node_id}/quiz")', QUIZ_ROUTE, "POST quiz", newline)
    source = insert_before_once(source, '@app.post("/api/exam/start")', EXAM_ROUTES, "POST exam/start", newline)
    source = insert_before_once(source, '@app.post("/api/topology")', TOPOLOGY_GET_ROUTE, "POST topology", newline)

    old = 'json.dumps([q.id for _, q in selected])'
    replacement = 'json.dumps([{"node_id": node.id, "question_id": q.id} for node, q in selected], ensure_ascii=False)'
    n = source.count(old)
    if n != 1:
        raise ValueError(f"Expression de stockage des questions d'examen attendue une fois, trouvée {n}. Aucun fichier n'a été écrit.")
    source = source.replace(old, replacement, 1)
    return source


def verify(api_text: str, html_text: str) -> list[str]:
    ast.parse(api_text, filename="app/api.py")
    required = {
        ("get", "/api/node/{node_id}/quiz"),
        ("post", "/api/exam/build"),
        ("post", "/api/exam/submit"),
        ("get", "/api/topology"),
    }
    found = set((method.lower(), route) for method, route in re.findall(
        r"@app\.(get|post|put|patch|delete|websocket)\(\s*['\"]([^'\"]+)['\"]", api_text
    ))
    missing = required - found
    if missing:
        raise ValueError(f"Routes attendues absentes après patch : {sorted(missing)}")
    if "'/api/exam/build'" not in html_text and '"/api/exam/build"' not in html_text:
        raise ValueError("L'interface fournie ne semble plus appeler /api/exam/build; source HTML différent du fichier audité.")
    if "'/api/exam/submit'" not in html_text and '"/api/exam/submit"' not in html_text:
        raise ValueError("L'interface fournie ne semble plus appeler /api/exam/submit; source HTML différent du fichier audité.")
    front_score = re.search(r"\bconst\s+PASS_SCORE\s*=\s*(\d+)\s*;", html_text)
    api_score = re.search(r"(?m)^EXAM_PASS_SCORE\s*=\s*(\d+)\s*$", api_text)
    if not front_score or not api_score or front_score.group(1) != api_score.group(1):
        raise ValueError("Le seuil EXAM_PASS_SCORE de l'API ne correspond pas au PASS_SCORE de l'interface.")
    return [
        "Syntaxe Python vérifiée avec ast.parse.",
        "Routes ajoutées détectées : GET quiz, POST exam/build, POST exam/submit, GET topology.",
        "Payload challenge : expected_topology est exposé sous forme JSON pour le défi Drawflow.",
        f"Seuil d'examen harmonisé avec l'interface : {front_score.group(1)} %.",
        "Le profil compte les examens réussis reçus par l'API sans modifier la table attempts.",
        "L'interface statique conserve ses appels existants; aucun changement HTML n'est requis par ce patch.",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path.cwd(), help="Racine du dépôt contenant app/api.py et static/index.html")
    parser.add_argument("--apply", action="store_true", help="Applique le patch après sauvegarde (sinon simulation seule)")
    args = parser.parse_args()

    root = args.project_root.resolve()
    api_path = root / "app" / "api.py"
    html_path = root / "static" / "index.html"
    for path in (api_path, html_path):
        if not path.is_file():
            print(f"ERREUR : fichier attendu introuvable : {path}", file=sys.stderr)
            return 2

    # newline="" préserve les fins de ligne du dépôt; les nouveaux blocs suivent le style existant.
    with api_path.open("r", encoding="utf-8", newline="") as fh:
        original_api = fh.read()
    with html_path.open("r", encoding="utf-8", newline="") as fh:
        original_html = fh.read()
    newline = "\r\n" if "\r\n" in original_api else "\n"

    try:
        patched_api = patch_source(original_api, newline, original_html)
        reports = verify(patched_api, original_html)
    except (ValueError, SyntaxError) as exc:
        print(f"PRÉCONTRÔLE ÉCHOUÉ : {exc}", file=sys.stderr)
        return 3

    print(f"Projet détecté : {root}")
    print("Modifications prévues : app/api.py uniquement (ajouts de routes et format interne des nouvelles sessions d'examen).")
    for report in reports:
        print(f"[OK] {report}")
    if not args.apply:
        print("SIMULATION SEULE : aucun fichier modifié. Relancer avec --apply pour sauvegarder puis appliquer.")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = root / "backups" / f"api-compat-{stamp}"
    try:
        backup_dir.mkdir(parents=True, exist_ok=False)
        shutil.copy2(api_path, backup_dir / "api.py")
        shutil.copy2(html_path, backup_dir / "index.html")
        # Écriture atomique pour éviter un fichier tronqué en cas d'interruption.
        temp_path = api_path.with_suffix(".py.api-compat-tmp")
        with temp_path.open("w", encoding="utf-8", newline="") as fh:
            fh.write(patched_api)
            fh.flush()
        temp_path.replace(api_path)
        # Relecture du fichier écrit et derniers contrôles. En cas d'échec, restaurer immédiatement.
        with api_path.open("r", encoding="utf-8", newline="") as fh:
            written_api = fh.read()
        verify(written_api, original_html)
        print(f"[OK] Sauvegarde créée : {backup_dir}")
        print("[OK] Patch appliqué et revérifié. static/index.html n'a pas été modifié.")
        print("Restauration possible : recopier backups/api-compat-.../api.py vers app/api.py.")
        return 0
    except Exception as exc:
        try:
            if (backup_dir / "api.py").exists():
                shutil.copy2(backup_dir / "api.py", api_path)
        except Exception as rollback_exc:
            print(f"ERREUR CRITIQUE : patch échoué ({exc}); restauration automatique échouée ({rollback_exc}).", file=sys.stderr)
            return 5
        print(f"ÉCHEC DU PATCH — fichier API restauré depuis la sauvegarde : {exc}", file=sys.stderr)
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
