import os

LESSON_DIR = "content/lessons"
os.makedirs(LESSON_DIR, exist_ok=True)

# Liste des nouveaux cours à créer (ID et Titre)
courses = [
    # --- MODULE CLOUD COMPUTING ---
    ("cloud-aws-debutant", "AWS - Débutant"),
    ("cloud-aws-intermediaire", "AWS - Intermédiaire"),
    ("cloud-aws-expert", "AWS - Expert"),
    ("cloud-azure-debutant", "Azure - Débutant"),
    ("cloud-azure-intermediaire", "Azure - Intermédiaire"),
    ("cloud-azure-expert", "Azure - Expert"),
    ("cloud-gcp-debutant", "GCP - Débutant"),
    ("cloud-gcp-intermediaire", "GCP - Intermédiaire"),
    ("cloud-gcp-expert", "GCP - Expert"),
    ("cloud-serverless-expert", "Architectures Serverless"),

    # --- MODULE OPÉRATEURS & TÉLÉCOMS ---
    ("telecom-dwdm-debutant", "Fibre Optique & DWDM"),
    ("telecom-mpls-tp-intermediaire", "MPLS-TP et Métro Ethernet"),
    ("telecom-bgp-peering-expert", "BGP Peering & Routage Internet"),
    ("telecom-5g-debutant", "Réseaux Mobiles (4G/5G)"),

    # --- MODULE VOIX & COLLABORATION ---
    ("voice-cucm-debutant", "Téléphonie IP (CUCM)"),
    ("voice-sip-intermediaire", "Protocole SIP & Dial Peers"),
    ("voice-qos-expert", "QoS pour la Voix et Vidéo"),

    # --- MODULE RÉSEAUX INDUSTRIELS (OT) ---
    ("ot-scada-debutant", "Introduction aux Réseaux OT / ICS"),
    ("ot-profinet-modbus-intermediaire", "Protocoles Industriels (Modbus, Profinet)"),
    ("ot-securite-expert", "Cybersécurité OT (Purdue Model)")
]

print("✨ Création des fichiers de cours pour les 4 nouveaux modules...\n")
created_count = 0

for node_id, title in courses:
    filepath = os.path.join(LESSON_DIR, f"{node_id}.md")
    
    # Si le fichier n'existe pas, on le crée avec un contenu temporaire
    if not os.path.exists(filepath):
        content = f"""---
node_id: {node_id}
title: {title}
---

# {title}

> **Note** : Ce cours est en cours de rédaction. Utilisez ChatGPT ou Gemini pour générer le contenu complet !
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📝 Créé : {node_id}.md")
        created_count += 1

print(f"\n✅ Terminé ! {created_count} fichiers ont été créés avec succès.")
print("Tu n'as plus qu'à coller le texte généré par l'IA dedans !")