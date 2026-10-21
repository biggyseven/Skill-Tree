import json
from pathlib import Path

def reparer_labs():
    labs_dir = Path("content/labs")
    fichiers_corriges = 0

    for fichier in labs_dir.rglob("lab.json"):
        try:
            contenu = fichier.read_text(encoding="utf-8-sig")
            # On essaie de parser
            data = json.loads(contenu)
            # Si ça marche, on réécrit proprement (sans BOM)
            fichier.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"✅ OK : {fichier.relative_to(labs_dir)}")
        except json.JSONDecodeError as e:
            print(f"❌ ERREUR dans {fichier.relative_to(labs_dir)} : {e}")
            # On affiche le contenu pour voir ce qui cloche
            print(f"   Contenu brut : {contenu[:200]}...")
            # On supprime le fichier corrompu (il sera recréé plus tard si besoin)
            fichier.unlink()
            print(f"   🗑️ Fichier supprimé pour être recréé.")
        except Exception as e:
            print(f"⚠️ Erreur inattendue : {e}")

    print(f"\nRéparation terminée.")

if __name__ == "__main__":
    reparer_labs()