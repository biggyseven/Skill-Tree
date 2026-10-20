import json
from pathlib import Path

# Récupérer les IDs existants dans nodes.json
nodes = json.loads(Path("content/nodes.json").read_text(encoding="utf-8"))
ids_existants = {n["id"] for n in nodes}

# Vérifier les cours
print("--- Cours manquants dans nodes.json ---")
for p in Path("content/lessons").glob("*.md"):
    if p.stem not in ids_existants:
        print(f"[MANQUANT] Cours : {p.stem}")

# Vérifier les quiz
print("\n--- Quiz manquants dans nodes.json ---")
for p in Path("content/quiz").glob("*.json"):
    if p.stem not in ids_existants:
        print(f"[MANQUANT] Quiz : {p.stem}")