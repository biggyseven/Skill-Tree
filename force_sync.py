import os
import sqlite3
from app.db import connect, DEFAULT_DB, ensure_ready
from app.loader import load_content, CONTENT_DIR

print("1️⃣ Suppression de l'ancienne base de données...")
for ext in ["", "-shm", "-wal"]:
    filepath = f"{DEFAULT_DB}{ext}"
    if os.path.exists(filepath):
        try: os.remove(filepath)
        except Exception as e: print(f"   ❌ Impossible de supprimer {filepath} : {e}")

print("\n2️⃣ Connexion et désactivation temporaire des Foreign Keys...")
conn = connect(DEFAULT_DB)
conn.execute("PRAGMA foreign_keys = OFF;") # Désactive la vérification stricte

print("\n3️⃣ Création et synchronisation de la base...")
ensure_ready(conn)
load_content(conn, CONTENT_DIR)

conn.commit()

print("\n4️⃣ Réactivation des Foreign Keys pour l'application...")
conn.execute("PRAGMA foreign_keys = ON;")
conn.close()

print("\n✅ Terminé ! La base de données est créée avec succès.")