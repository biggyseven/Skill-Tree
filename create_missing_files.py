import os
import json

NODES_FILE = "content/nodes.json"
LESSON_DIR = "content/lessons"
QUIZ_DIR = "content/quiz"
LAB_DIR = "content/labs"
TERM_DIR = "content/terminal"

for d in [LESSON_DIR, QUIZ_DIR, LAB_DIR, TERM_DIR]:
    os.makedirs(d, exist_ok=True)

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

# 1. On scanne les dossiers Docker existants pour connaître les node_id déjà gérés
docker_lab_nodes = set()
if os.path.exists(LAB_DIR):
    for entry in os.listdir(LAB_DIR):
        folder_path = os.path.join(LAB_DIR, entry)
        if os.path.isdir(folder_path):
            lab_json = os.path.join(folder_path, "lab.json")
            if os.path.exists(lab_json):
                try:
                    with open(lab_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if "node_id" in data:
                            docker_lab_nodes.add(data["node_id"])
                except:
                    pass

print("🔍 Analyse des nœuds et création des fichiers manquants...\n")
created_count = 0

for node in nodes:
    node_id = node["id"]
    title = node.get("title", node_id)
    reqs = node.get("requirements", [])

    # Cours .md
    lesson_path = os.path.join(LESSON_DIR, f"{node_id}.md")
    if not os.path.exists(lesson_path):
        with open(lesson_path, "w", encoding="utf-8") as f:
            f.write(f"---\nnode_id: {node_id}\ntitle: {title}\n---\n\n# {title}\n\n> **Note** : En cours de rédaction.")
        created_count += 1

    # Quiz .json
    if any(r["kind"] == "quiz" for r in reqs):
        quiz_path = os.path.join(QUIZ_DIR, f"{node_id}.json")
        if not os.path.exists(quiz_path):
            dummy = {"node_id": node_id, "scope": "quiz", "questions": [{"type": "qcm", "prompt": "Temp", "choices": ["A", "B", "C", "D"], "answer": 0, "explanation": "Temp"}]}
            with open(quiz_path, "w", encoding="utf-8") as f: json.dump(dummy, f)
            created_count += 1

    # Lab .json (on vérifie si un dossier docker existe DÉJÀ pour ce node_id)
    if any(r["kind"] == "lab" for r in reqs):
        lab_path = os.path.join(LAB_DIR, f"{node_id}.json")
        if not os.path.exists(lab_path) and node_id not in docker_lab_nodes:
            dummy = {"node_id": node_id, "mode": "contains", "prompt": "Tapez ok", "hint": "ok", "pattern": "ok"}
            with open(lab_path, "w", encoding="utf-8") as f: json.dump(dummy, f)
            created_count += 1

    # Terminal .json
    if any(r["kind"] == "terminal" for r in reqs):
        term_path = os.path.join(TERM_DIR, f"{node_id}.json")
        if not os.path.exists(term_path):
            dummy = {"node_id": node_id, "prompt": "Tapez ok", "answer": "ok", "regex": "^ok$", "explanation": "Temp"}
            with open(term_path, "w", encoding="utf-8") as f: json.dump(dummy, f)
            created_count += 1

print(f"✅ {created_count} fichiers générés avec succès !")