import json

NODES_FILE = "content/nodes.json"

print("🔍 Analyse des prérequis dans nodes.json...\n")

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

# On récupère tous les IDs valides
valid_ids = {n["id"] for n in nodes}
fixed = False

for node in nodes:
    if "prereqs" in node and node["prereqs"]:
        valid_prereqs = []
        for p in node["prereqs"]:
            if p in valid_ids:
                valid_prereqs.append(p)
            else:
                print(f"⚠️ Le cours '{node['id']}' demande le prérequis '{p}' qui n'existe plus. (Supprimé)")
                fixed = True
        node["prereqs"] = valid_prereqs

if fixed:
    with open(NODES_FILE, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2, ensure_ascii=False)
    print("\n✅ Le fichier nodes.json a été réparé avec succès !")
else:import json

NODES_FILE = "content/nodes.json"

with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

valid_ids = {n["id"] for n in nodes}
erreurs = 0

for node in nodes:
    if "prereqs" in node and node["prereqs"]:
        valides = []
        for p in node["prereqs"]:
            if p in valid_ids:
                valides.append(p)
            else:
                print(f"❌ Le cours '{node['id']}' demande '{p}' (inexistant). Supprimé.")
                erreurs += 1
        node["prereqs"] = valides

if erreurs > 0:
    with open(NODES_FILE, "w", encoding="utf-8") as f:
        json.dump(nodes, f, indent=2, ensure_ascii=False)
    print(f"\n✅ {erreurs} erreurs corrigées dans nodes.json !")
else:
    print("\n✅ Aucun prérequis invalide trouvé. Le problème vient d'ailleurs.")
    print("\n✅ Aucun prérequis cassé trouvé.")