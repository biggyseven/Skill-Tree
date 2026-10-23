import json
import os

NODES_FILE = "content/nodes.json"
QUIZ_DIR = "content/quiz"
LAB_DIR = "content/labs"

# Charger nodes.json
with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

# Créer les dossiers s'ils n'existent pas
os.makedirs(QUIZ_DIR, exist_ok=True)
os.makedirs(LAB_DIR, exist_ok=True)

print("🔍 Analyse des nœuds et génération des quiz/labs manquants...\n")

for node in nodes:
    node_id = node["id"]
    title = node.get("title", node_id)
    reqs = node.get("requirements", [])

    # --- GESTION DES QUIZ ---
    if any(r["kind"] == "quiz" for r in reqs):
        quiz_file = os.path.join(QUIZ_DIR, f"{node_id}.json")
        if not os.path.exists(quiz_file):
            dummy_quiz = {
                "node_id": node_id,
                "scope": "quiz",
                "questions": [{
                    "type": "qcm",
                    "prompt": f"Question temporaire pour : {title}",
                    "choices": ["Réponse A", "Réponse B", "Réponse C", "Réponse D"],
                    "answer": 0,
                    "explanation": "Ceci est un quiz généré automatiquement. Remplace-le par le vrai contenu."
                }]
            }
            with open(quiz_file, "w", encoding="utf-8") as f:
                json.dump(dummy_quiz, f, indent=2, ensure_ascii=False)
            print(f"✅ Quiz créé : {node_id}.json")

    # --- GESTION DES LABS ---
    if any(r["kind"] == "lab" for r in reqs):
        lab_file = os.path.join(LAB_DIR, f"{node_id}.json")
        lab_folder = os.path.join(LAB_DIR, node_id)
        
        # On vérifie si ni le fichier .json, ni le dossier Docker n'existent
        if not os.path.exists(lab_file) and not os.path.exists(lab_folder):
            dummy_lab = {
                "node_id": node_id,
                "mode": "contains",
                "prompt": f"Saisissez le mot 'ok' pour valider le lab temporaire de {title}.",
                "hint": "Tapez ok",
                "pattern": "ok"
            }
            with open(lab_file, "w", encoding="utf-8") as f:
                json.dump(dummy_lab, f, indent=2, ensure_ascii=False)
            print(f"🔬 Lab créé : {node_id}.json")

print("\n🎉 Terminé ! Tu peux relancer la synchronisation.")