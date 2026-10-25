import json
import os

NODES_FILE = "content/nodes.json"
QUIZ_DIR = "content/quiz"
LAB_DIR = "content/labs"
TERM_DIR = "content/terminal"
EXAM_DIR = "content/exam"

# Créer les dossiers s'ils n'existent pas
for d in [QUIZ_DIR, LAB_DIR, TERM_DIR, EXAM_DIR]:
    os.makedirs(d, exist_ok=True)

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

print("🔍 Analyse des nœuds et création des fichiers manquants...\n")
created_count = 0

for node in nodes:
    node_id = node["id"]
    title = node.get("title", node_id)
    reqs = node.get("requirements", [])

    # 1. Quiz
    if any(r["kind"] == "quiz" for r in reqs):
        quiz_path = os.path.join(QUIZ_DIR, f"{node_id}.json")
        if not os.path.exists(quiz_path):
            dummy_quiz = {
                "node_id": node_id,
                "scope": "quiz",
                "questions": [{
                    "type": "qcm",
                    "prompt": f"Question temporaire pour {title}",
                    "choices": ["Réponse A", "Réponse B", "Réponse C", "Réponse D"],
                    "answer": 0,
                    "explanation": "Ceci est un quiz généré automatiquement."
                }]
            }
            with open(quiz_path, "w", encoding="utf-8") as f:
                json.dump(dummy_quiz, f, indent=2, ensure_ascii=False)
            print(f"🧪 Quiz créé : {node_id}.json")
            created_count += 1

    # 2. Lab
    if any(r["kind"] == "lab" for r in reqs):
        lab_path = os.path.join(LAB_DIR, f"{node_id}.json")
        lab_folder = os.path.join(LAB_DIR, node_id)
        
        if not os.path.exists(lab_path) and not os.path.exists(lab_folder):
            dummy_lab = {
                "node_id": node_id,
                "mode": "contains",
                "prompt": f"Saisissez le mot 'ok' pour valider le lab temporaire de {title}.",
                "hint": "Tapez ok",
                "pattern": "ok"
            }
            with open(lab_path, "w", encoding="utf-8") as f:
                json.dump(dummy_lab, f, indent=2, ensure_ascii=False)
            print(f"🔬 Lab créé : {node_id}.json")
            created_count += 1

    # 3. Examen
    if any(r["kind"] == "exam" for r in reqs):
        exam_path = os.path.join(EXAM_DIR, f"{node_id}.json")
        if not os.path.exists(exam_path):
            dummy_exam = {
                "node_id": node_id,
                "scope": "exam",
                "questions": [{
                    "type": "qcm",
                    "prompt": f"Question d'examen pour {title}",
                    "choices": ["Choix A", "Choix B", "Choix C", "Choix D"],
                    "answer": 0,
                    "explanation": "Examen généré automatiquement."
                }]
            }
            with open(exam_path, "w", encoding="utf-8") as f:
                json.dump(dummy_exam, f, indent=2, ensure_ascii=False)
            print(f"🎓 Examen créé : {node_id}.json")
            created_count += 1

print(f"\n✅ Terminé ! {created_count} fichiers ont été créés.")