import os

# Liste des anciens fichiers à supprimer
old_files = [
    "dhcp-dns", "ipv6", "multicast", "mpls", "layer2-security", 
    "qos", "ospf", "ospf-advanced", "bgp", "bgp-advanced", 
    "eigrp", "vlan", "stp", "ha"
]

folders = ["quiz", "lessons", "labs"]

for folder in folders:
    for file in old_files:
        # On teste l'extension .json et .md
        for ext in [".json", ".md"]:
            path = os.path.join("content", folder, f"{file}{ext}")
            if os.path.exists(path):
                os.remove(path)
                print(f"🗑️ Supprimé : {path}")

print("✅ Nettoyage terminé ! Tu peux relancer la synchronisation.")