import os
import json
import shutil

NODES_FILE = "content/nodes.json"

# 1. Charger les IDs valides depuis nodes.json
print("🔍 Lecture de nodes.json...")
try:
    with open(NODES_FILE, "r", encoding="utf-8") as f:
        nodes = json.load(f)
    valid_ids = {n["id"] for n in nodes}
    print(f"✅ {len(valid_ids)} cours valides trouvés.\n")
except Exception as e:
    print(f"❌ Erreur lors de la lecture de nodes.json : {e}")
    exit(1)

deleted_count = 0

def clean_directory(dir_path, is_folder_based=False):
    global deleted_count
    if not os.path.exists(dir_path):
        return
    
    for filename in os.listdir(dir_path):
        path = os.path.join(dir_path, filename)
        
        # Ignorer les fichiers cachés ou systèmes
        if filename.startswith('.'):
            continue

        node_id = None

        # --- CAS 1 : Fichiers Markdown (.md) ---
        if not is_folder_based and filename.endswith(".md"):
            node_id = os.path.splitext(filename)[0]

        # --- CAS 2 : Fichiers JSON (.json) ---
        elif not is_folder_based and filename.endswith(".json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    node_id = data.get("node_id")
            except Exception:
                pass # Si le JSON est cassé, on le laissera, le loader gérera l'erreur

        # --- CAS 3 : Dossiers (ex: labs Docker) ---
        elif is_folder_based and os.path.isdir(path):
            lab_json = os.path.join(path, "lab.json")
            if os.path.exists(lab_json):
                try:
                    with open(lab_json, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        node_id = data.get("node_id")
                except Exception:
                    pass

        # --- SUPPRESSION ---
        if node_id and node_id not in valid_ids:
            print(f"🗑️  Suppression (ID '{node_id}' introuvable) : {path}")
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            deleted_count += 1

# 2. Lancer le nettoyage sur tous les dossiers
print("🧹 Nettoyage des leçons (.md)...")
clean_directory("content/lessons")

print("\n🧹 Nettoyage des quiz (.json)...")
clean_directory("content/quiz")

print("\n🧹 Nettoyage des terminaux (.json)...")
clean_directory("content/terminal")

print("\n🧹 Nettoyage des examens (.json)...")
clean_directory("content/exam")

print("\n🧹 Nettoyage des labs (fichiers .json et dossiers)...")
# On nettoie d'abord les fichiers .json dans content/labs
clean_directory("content/labs")
# On nettoie ensuite les dossiers (ex: lab_acl)
clean_directory("content/labs", is_folder_based=True)

print("\n" + "="*40)
if deleted_count > 0:
    print(f"✅ Terminé ! {deleted_count} fichiers/dossiers orphelins ont été supprimés.")
else:
    print("✨ Tout est propre ! Aucun fichier orphelin trouvé.")
print("="*40)
print("Tu peux maintenant relancer la synchronisation :")
print('python -c "from app.db import connect, DEFAULT_DB, ensure_ready; from app.loader import load_content, CONTENT_DIR; conn = connect(DEFAULT_DB); ensure_ready(conn); load_content(conn, CONTENT_DIR); conn.commit(); print(\'Synchronisation réussie !\')"')