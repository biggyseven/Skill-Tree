import os
import json

LAB_DIR = "content/labs"

print("🔍 Recherche des doublons de labs...\n")

# Dictionnaire pour stocker les labs par node_id
labs = {}

# 1. Parcourir tous les fichiers et dossiers dans le dossier labs
for filename in os.listdir(LAB_DIR):
    path = os.path.join(LAB_DIR, filename)
    
    # Si c'est un fichier .json (ex: acl.json)
    if os.path.isfile(path) and filename.endswith(".json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                node_id = data.get("node_id")
                if node_id:
                    if node_id not in labs: labs[node_id] = []
                    labs[node_id].append(path)
        except Exception:
            pass
            
    # Si c'est un dossier (ex: lab_acl/)
    elif os.path.isdir(path):
        lab_json = os.path.join(path, "lab.json")
        if os.path.exists(lab_json):
            try:
                with open(lab_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    node_id = data.get("node_id")
                    if node_id:
                        if node_id not in labs: labs[node_id] = []
                        labs[node_id].append(path)
            except Exception:
                pass

# 2. Trouver et supprimer les doublons
doublons_trouves = False
for node_id, paths in labs.items():
    if len(paths) > 1:
        doublons_trouves = True
        print(f"⚠️ Doublon pour le cours « {node_id} » :")
        
        # On parcourt les chemins. Si c'est un fichier .json, on le supprime.
        # On garde le dossier (qui contient le vrai lab Docker).
        for p in paths:
            if os.path.isfile(p):
                print(f"   🗑️ Suppression du fichier en trop : {p}")
                os.remove(p)
            else:
                print(f"   📁 Dossier Docker conservé : {p}")

if not doublons_trouves:
    print("✅ Aucun doublon trouvé !")

print("\n🎉 Nettoyage terminé. Tu peux relancer la synchronisation.")