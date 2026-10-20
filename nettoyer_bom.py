import json
from pathlib import Path

def nettoyer_bom():
    dossier = Path("content/quiz")
    fichiers_corriges = 0

    for fichier in dossier.glob("*.json"):
        # Lire en utf-8-sig (qui gère le BOM) et réécrire en utf-8 standard
        try:
            contenu = fichier.read_text(encoding="utf-8-sig")
            # On vérifie que c'est du JSON valide avant d'écraser
            json.loads(contenu)
            fichier.write_text(contenu, encoding="utf-8")
            fichiers_corriges += 1
        except json.JSONDecodeError as e:
            print(f"⚠️ Fichier ignoré (JSON invalide) : {fichier.name} -> {e}")
        except Exception as e:
            print(f"⚠️ Erreur sur {fichier.name} : {e}")

    print(f"✅ {fichiers_corriges} fichiers ont été nettoyés (BOM supprimé).")

if __name__ == "__main__":
    nettoyer_bom()