import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

# Charger la clé API
load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    print("Erreur : GROQ_API_KEY n'est pas définie dans le fichier .env")
    exit(1)

client = Groq(api_key=API_KEY)
MODEL = "openai/gpt-oss-120b"

# Liste des nœuds à générer (tu peux en ajouter autant que tu veux)
NODES_TO_GENERATE = [
    {"id": "mpls", "title": "MPLS et VRF", "category": "Routage Avancé"},
    {"id": "qos", "title": "Qualité de Service (QoS)", "category": "Routage Avancé"},
    {"id": "sdwan", "title": "SD-WAN", "category": "Cloud & Automatisation"},
    {"id": "zero-trust", "title": "Architecture Zero Trust", "category": "Sécurité"},
    {"id": "ansible", "title": "Automatisation avec Ansible", "category": "Cloud & Automatisation"},
    {"id": "vxlan", "title": "VXLAN et Datacenter", "category": "Cloud & Automatisation"},
]

def verifier_modele():
    """Vérifie que le modèle choisi est bien disponible sur Groq."""
    try:
        modeles = client.models.list()
        ids_disponibles = [m.id for m in modeles.data]
        if MODEL not in ids_disponibles:
            print(f"⚠️ Le modèle '{MODEL}' n'est pas disponible.")
            print(f"Modèles disponibles sur ton compte : {ids_disponibles}")
            return False
        return True
    except Exception as e:
        print(f"Impossible de vérifier les modèles : {e}")
        return False
        
def generate_lesson(node_id, title):
    print(f"Génération du cours pour : {title}...")
    prompt = f"""Tu es un expert réseau de niveau CCIE. Rédige un cours intensif, complet et technique (niveau Admin Réseau Senior) sur le sujet : {title}.
Le cours doit faire au moins 10 000 caractères. 
Utilise le format Markdown. 
Inclus des tableaux comparatifs, des schémas ASCII, des commandes Cisco/Linux exactes et un atelier de dépannage.
Ne mets pas de balises ```markdown au début et à la fin, renvoie juste le texte brut."""
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        temperature=0.7,
        max_tokens=4096,
    )
    content = response.choices[0].message.content
    
    # Sauvegarde
    path = Path(f"content/lessons/{node_id}.md")
    path.write_text(content, encoding="utf-8")
    print(f" -> Cours sauvegardé : {path}")

def generate_quiz(node_id, title):
    print(f"Génération du quiz pour : {title}...")
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
    
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL,
        temperature=0.5,
        response_format={"type": "json_object"} # Force le format JSON
    )
    content = response.choices[0].message.content
    
    # Sauvegarde
    path = Path(f"content/quiz/{node_id}.json")
    path.write_text(content, encoding="utf-8")
    print(f" -> Quiz sauvegardé : {path}")

def main():
    print("--- Démarrage de l'usine à contenu ---")
    
    # S'assurer que les dossiers existent
    Path("content/lessons").mkdir(parents=True, exist_ok=True)
    Path("content/quiz").mkdir(parents=True, exist_ok=True)

    for node in NODES_TO_GENERATE:
        # On vérifie si le fichier existe déjà pour ne pas écraser
        if Path(f"content/lessons/{node['id']}.md").exists():
            print(f"Le cours {node['id']} existe déjà. On passe.")
            continue

        try:
            generate_lesson(node["id"], node["title"])
            time.sleep(2) # Pause pour éviter le rate limit de l'API
            generate_quiz(node["id"], node["title"])
            time.sleep(2)
        except Exception as e:
            print(f"Erreur sur le nœud {node['id']} : {e}")

    print("--- Génération terminée ! Lance 'python main.py import' pour tout charger. ---")

if __name__ == "__main__":
    main()