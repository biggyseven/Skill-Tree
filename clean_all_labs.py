import os
import json

NODES_FILE = "content/nodes.json"
LAB_DIR = "content/labs"

# 1. Charger les IDs valides
with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)
valid_ids = {n["id"] for n in nodes}

print("🧹 Nettoyage des labs invalides...\n")

# 2. Parcourir le dossier labs
for filename in os.listdir(LAB_DIR):
    path = os.path.join(LAB_DIR, filename)
    node_id = None
    
    # Si c'est un fichier .json
    if os.path.isfile(path) and filename.endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                node_id = data.get("node_id")
        except Exception:
            pass
            
    # Si c'est un dossier Docker
    elif os.path.isdir(path):
        lab_json = os.path.join(path, "lab.json")
        if os.path.exists(lab_json):
            try:
                with open(lab_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    node_id = data.get("node_id")
            except Exception:
                pass

    # 3. Si on a trouvé un node_id et qu'il n'est plus valide, on supprime
    if node_id and node_id not in valid_ids:
        print(f"🗑️ Suppression de {path} (car le cours '{node_id}' n'existe plus)")
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            import shutil
            shutil.rmtree(path)

print("\n✅ Nettoyage terminé ! Tu peux relancer la synchronisation.")