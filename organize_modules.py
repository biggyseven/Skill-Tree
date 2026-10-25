import json

NODES_FILE = "content/nodes.json"

print("📂 Lecture de nodes.json...")
with open(NODES_FILE, "r", encoding="utf-8") as f:
    nodes = json.load(f)

count_sys = 0
count_devops = 0
count_reseau = 0

# On parcourt tous les cours
for node in nodes:
    cat = node.get("category", "")
    node_id = node.get("id", "")

    # 1. Détection du module Administration Système
    if cat == "Systèmes" or any(node_id.startswith(p) for p in ["linux-", "storage-", "users-", "process-", "packages-", "scripting-", "reseau-linux-", "web-server-", "db-", "windows-server-", "ha-sys-", "virt-", "monitoring-", "backup-"]):
        node["module"] = "Administration Système"
        count_sys += 1

    # 2. Détection du module DevOps
    elif cat == "DevOps" or any(node_id.startswith(p) for p in ["cicd-", "git-", "docker-", "k8s-", "iac-", "observability-", "devsecops-", "mesh-"]):
        # Exception : cicd-network est de l'automatisation réseau, pas du DevOps pur
        if node_id.startswith("cicd-network"):
            node["module"] = "Administration Réseaux"
            count_reseau += 1
        else:
            node["module"] = "DevOps"
            count_devops += 1

    # 3. Tout le reste est du Réseau
    else:
        node["module"] = "Administration Réseaux"
        count_reseau += 1

# Sauvegarde du fichier mis à jour
with open(NODES_FILE, "w", encoding="utf-8") as f:
    json.dump(nodes, f, indent=2, ensure_ascii=False)

print("\n✅ Organisé avec succès !")
print(f"🌐 Administration Réseaux : {count_reseau} cours")
print(f"🖥️ Administration Système : {count_sys} cours")
print(f"⚙️ DevOps : {count_devops} cours")
print("\nTu peux maintenant relancer la synchronisation (force_sync.py).")