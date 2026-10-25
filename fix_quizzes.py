import json
from pathlib import Path

CONTENT_DIR = Path("content")
QUIZ_DIR = CONTENT_DIR / "quiz"
LESSONS_DIR = CONTENT_DIR / "lessons"

# On s'assure que le dossier quiz existe
QUIZ_DIR.mkdir(parents=True, exist_ok=True)

# On récupère tous les identifiants de cours à partir des fichiers Markdown
node_ids = [f.stem for f in LESSONS_DIR.glob("*.md")]

print(f"🔍 {len(node_ids)} cours trouvés. Vérification des quiz...")

created_count = 0
for node_id in node_ids:
    quiz_file = QUIZ_DIR / f"{node_id}.json"
    if not quiz_file.exists():
        # Création d'un quiz valide
        data = {
            "node_id": node_id,
            "questions": [
                {
                    "id": f"{node_id}-q1",
                    "prompt": "Avez-vous bien lu ce cours ?",
                    "type": "qcm",
                    "choices": ["Oui", "Non"],
                    "answer": 0,
                    "explanation": "Question placeholder générée automatiquement."
                }
            ]
        }
        # On écrit en UTF-8 SANS BOM
        with open(quiz_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        created_count += 1
        print(f"✅ Créé : {node_id}.json")

print(f"\n🎉 Terminé ! {created_count} fichiers de quiz ont été générés.")
print("Tu peux maintenant relancer : python force_sync.py")