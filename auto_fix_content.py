import json
import os
import glob

# Chemins des dossiers
NODES_FILE = "content/nodes.json"
QUIZ_DIR = "content/quiz"
LAB_DIR = "content/labs"
LESSON_DIR = "content/lessons"

# Créer les dossiers s'ils n'existent pas
for d in [QUIZ_DIR, LAB_DIR, LESSON_DIR]:
    os.makedirs(d, exist_ok=True)

# Charger nodes.json
with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

# Extraire tous les IDs valides
valid_ids = {n["id"] for n in nodes}

print("🧹 1. Nettoyage des fichiers orphelins...")
for d in [QUIZ_DIR, LAB_DIR, LESSON_DIR]:
    for filepath in glob.glob(f"{d}/*.*"):
        filename = os.path.basename(filepath)
        node_id = os.path.splitext(filename)[0]
        # Si le fichier ne correspond à aucun noeud dans nodes.json, on le supprime
        if node_id not in valid_ids:
            os.remove(filepath)
            print(f"   🗑️ Supprimé : {filepath}")

print("\n✨ 2. Génération des fichiers manquants...")
for node in nodes:
    node_id = node["id"]
    title = node.get("title", node_id)
    reqs = node.get("requirements", [])
    
    # A. Vérifier le fichier de cours (.md)
    lesson_path = os.path.join(LESSON_DIR, f"{node_id}.md")
    if not os.path.exists(lesson_path):
        with open(lesson_path, "w", encoding="utf-8") as f:
            f.write(f"---\nnode_id: {node_id}\ntitle: {title}\n---\n\n# {title}\n\n> **Note** : Ce cours est en cours de rédaction. Utilisez Gemini pour générer le contenu complet !")
        print(f"   📝 Cours créé : {lesson_path}")
        
    # B. Vérifier le Quiz
    if any(r["kind"] == "quiz" for r in reqs):
        quiz_path = os.path.join(QUIZ_DIR, f"{node_id}.json")
        if not os.path.exists(quiz_path):
            dummy_quiz = {
                "node_id": node_id,
                "scope": "quiz",
                "questions": [{
                    "type": "qcm",
                    "prompt": f"Question temporaire pour {title}. Avez-vous lu le cours ?",
                    "choices": ["Oui", "Non", "Peut-être", "Je ne sais pas"],
                    "answer": 0,
                    "explanation": "Ceci est un quiz généré automatiquement pour éviter les erreurs."
                }]
            }
            with open(quiz_path, "w", encoding="utf-8") as f:
                json.dump(dummy_quiz, f, indent=2, ensure_ascii=False)
            print(f"   🧪 Quiz créé : {quiz_path}")
            
    # C. Vérifier le Lab
    if any(r["kind"] == "lab" for r in reqs):
        lab_path = os.path.join(LAB_DIR, f"{node_id}.json")
        if not os.path.exists(lab_path):
            dummy_lab = {
                "node_id": node_id,
                "mode": "contains",
                "prompt": f"Saisissez le mot 'ok' pour valider le lab temporaire de {title}.",
                "hint": "Tapez ok",
                "pattern": "ok"
            }
            with open(lab_path, "w", encoding="utf-8") as f:
                json.dump(dummy_lab, f, indent=2, ensure_ascii=False)
            print(f"   🔬 Lab créé : {lab_path}")

print("\n✅ Opération terminée avec succès ! Tu peux relancer la synchronisation.")