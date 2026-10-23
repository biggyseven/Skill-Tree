import os
import sqlite3
from collections import Counter
import json
from app.db import connect, DEFAULT_DB, ensure_ready
from app.loader import load_content, CONTENT_DIR

print("1️⃣ Vérification des doublons d'ID dans nodes.json...")
with open("content/nodes.json", "r", encoding="utf-8") as f:
    nodes = json.load(f)
ids = [n["id"] for n in nodes]
doublons = [item for item, count in Counter(ids).items() if count > 1]
if doublons:
    print(f"❌ ATTENTION : Doublons trouvés dans nodes.json : {doublons}")
    print("👉 Supprime les doublons dans ton fichier avant de continuer.")
    exit(1)
else:
    print("✅ Aucun doublon d'ID détecté.")

print("\n2️⃣ Suppression forcée de l'ancienne base de données...")
for ext in ["", "-shm", "-wal"]:
    filepath = f"{DEFAULT_DB}{ext}"
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            print(f"   🗑️ Supprimé : {filepath}")
        except Exception as e:
            print(f"   ❌ Impossible de supprimer {filepath} : {e}")
            print("   ⚠️ Assure-toi que Uvicorn est bien ARRÊTÉ (Ctrl+C).")
            exit(1)

print("\n3️⃣ Création de la nouvelle base de données...")
conn = connect(DEFAULT_DB)
ensure_ready(conn)
load_content(conn, CONTENT_DIR)
conn.commit()
conn.close()

print("\n✅ Synchronisation réussie ! La base de données est toute propre.")