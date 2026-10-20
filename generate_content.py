import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Charger la clé API
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("Erreur : OPENROUTER_API_KEY n'est pas définie dans le fichier .env")
    exit(1)

# Configuration du client pour OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# Le routeur automatique : sélectionne un modèle gratuit disponible
MODEL = "openrouter/free"

# Les 30 nœuds manquants du Master Plan
NODES_TO_GENERATE = [
    {"id": "cabling", "title": "Câblage et Normes", "category": "Fondamentaux"},
    {"id": "poe", "title": "Power over Ethernet (PoE)", "category": "Fondamentaux"},
    {"id": "etherchannel", "title": "Agrégation de liens (LACP)", "category": "Couche 2 — Commutation"},
    {"id": "vtp", "title": "VTP et gestion des VLANs", "category": "Couche 2 — Commutation"},
    {"id": "eigrp", "title": "EIGRP", "category": "Routage"},
    {"id": "pbr", "title": "Policy-Based Routing (PBR)", "category": "Routage"},
    {"id": "bgp-advanced", "title": "BGP Avancé", "category": "Routage"},
    {"id": "vrf", "title": "VRF (Virtual Routing)", "category": "Routage"},
    {"id": "multicast", "title": "Multicast (PIM, IGMP)", "category": "Routage"},
    {"id": "qos-advanced", "title": "QoS Avancée", "category": "Routage"},
    {"id": "vxlan", "title": "VXLAN et Datacenter", "category": "Cloud & Automatisation"},
    {"id": "spine-leaf", "title": "Architecture Spine/Leaf", "category": "Cloud & Automatisation"},
    {"id": "aws-vpc", "title": "AWS VPC", "category": "Cloud & Automatisation"},
    {"id": "azure-vnet", "title": "Azure VNet", "category": "Cloud & Automatisation"},
    {"id": "sd-wan", "title": "SD-WAN", "category": "Cloud & Automatisation"},
    {"id": "ipsec", "title": "VPN IPsec", "category": "Sécurité"},
    {"id": "wireguard", "title": "VPN WireGuard", "category": "Sécurité"},
    {"id": "radius", "title": "Authentification RADIUS", "category": "Sécurité"},
    {"id": "pki", "title": "PKI et Certificats", "category": "Sécurité"},
    {"id": "zero-trust-architecture", "title": "Zero Trust", "category": "Sécurité"},
    {"id": "ddos-mitigation", "title": "Attaques DDoS", "category": "Sécurité"},
    {"id": "layer2-security", "title": "Sécurité L2", "category": "Sécurité"},
    {"id": "netmiko", "title": "Python et Netmiko", "category": "Cloud & Automatisation"},
    {"id": "restconf", "title": "API RESTCONF/NETCONF", "category": "Cloud & Automatisation"},
    {"id": "terraform", "title": "Terraform", "category": "Cloud & Automatisation"},
    {"id": "napalm", "title": "NAPALM", "category": "Cloud & Automatisation"},
    {"id": "cicd-network", "title": "CI/CD pour le réseau", "category": "Cloud & Automatisation"},
    {"id": "wireshark-advanced", "title": "Wireshark Avancé", "category": "Exploitation"},
    {"id": "mtu-pmtud", "title": "Dépannage MTU", "category": "Exploitation"},
    {"id": "itil-rca", "title": "ITIL et RCA", "category": "Exploitation"}
]

def generate_lesson(node_id, title):
    path = Path(f"content/lessons/{node_id}.md")
    if path.exists():
        print(f"⏩ Le cours {node_id} existe déjà.")
        return

    print(f"⏳ Génération du cours pour : {title}...")
    prompt = f"""Tu es un expert réseau de niveau CCIE. Rédige un cours intensif, complet et technique sur le sujet : {title}.
Le cours doit faire environ 10 000 caractères. 
Utilise le format Markdown. 
Inclus des tableaux comparatifs, des schémas ASCII, des commandes Cisco/Linux exactes et un atelier de dépannage.
TRÈS IMPORTANT : Assure-toi de terminer toutes tes phrases et tous tes tableaux.
Ne mets pas de balises ```markdown au début et à la fin, renvoie juste le texte brut."""
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODEL,
                temperature=0.7,
                max_tokens=8192,
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("L'IA a renvoyé un contenu vide.")
                
            path.write_text(content, encoding="utf-8")
            print(f"  ✅ Cours sauvegardé : {path}")
            return
        except Exception as e:
            print(f"  ⚠️ Tentative {attempt+1} échouée : {e}")
            time.sleep(3)
    print(f"  ❌ ÉCHEC DÉFINITIF pour le cours {node_id}")

def generate_quiz(node_id, title):
    path = Path(f"content/quiz/{node_id}.json")
    if path.exists():
        print(f"⏩ Le quiz {node_id} existe déjà.")
        return

    print(f"⏳ Génération du quiz pour : {title}...")
    prompt = f"""Tu es un expert réseau. Génère un quiz de 10 questions à choix multiples (QCM) sur le sujet : {title}.
Tu dois renvoyer UNIQUEMENT un objet JSON valide, sans aucune explication avant ou après.
Le format doit être exactement celui-ci :
{{
  "node_id": "{node_id}",
  "scope": "quiz",
  "questions": [
    {{
      "type": "qcm",
      "prompt": "La question ici ?",
      "choices": ["Choix A", "Choix B", "Choix C", "Choix D"],
      "answer": 1,
      "explanation": "Explication de la bonne réponse."
    }}
  ]
}}
Assure-toi que 'answer' est l'index de la bonne réponse (0, 1, 2 ou 3)."""
    
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=MODEL,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("L'IA a renvoyé un contenu vide (None).")
            
            # Vérification que le JSON est valide
            parsed_json = json.loads(content)
            if "questions" not in parsed_json or len(parsed_json["questions"]) == 0:
                raise ValueError("Le JSON ne contient pas de questions valides.")
                
            path.write_text(content, encoding="utf-8")
            print(f"  ✅ Quiz sauvegardé : {path}")
            return
        except Exception as e:
            print(f"  ⚠️ Tentative {attempt+1} échouée : {e}")
            time.sleep(3)
    print(f"  ❌ ÉCHEC DÉFINITIF pour le quiz {node_id}")

def main():
    print("--- 🏭 Démarrage de l'usine à contenu (OpenRouter Auto-Router) ---")
    
    Path("content/lessons").mkdir(parents=True, exist_ok=True)
    Path("content/quiz").mkdir(parents=True, exist_ok=True)

    for node in NODES_TO_GENERATE:
        generate_lesson(node["id"], node["title"])
        time.sleep(2)
        generate_quiz(node["id"], node["title"])
        time.sleep(2)

    print("--- 🎉 Génération terminée ! Lance 'python main.py import' pour tout charger. ---")

if __name__ == "__main__":
    main()