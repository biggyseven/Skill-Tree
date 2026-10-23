import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Charger la clé API depuis le .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

if not API_KEY:
    print("❌ Erreur : OPENROUTER_API_KEY manquante dans le .env")
    exit(1)

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=API_KEY)
MODEL = "openrouter/free" # Ou "meta-llama/llama-3.3-70b-instruct" si tu as des crédits

# La liste des cours cassés à régénérer
COURS_A_REGENERER = [
    {"id": "adressage-debutant", "title": "L'adressage IP pour les débutants", "category": "Fondamentaux"},
    {"id": "itil-rca", "title": "Gestion d'incident (ITIL et RCA)", "category": "Exploitation"},
    {"id": "osi", "title": "Modèle OSI & TCP/IP", "category": "Fondamentaux"},
    {"id": "intro-reseau", "title": "Qu'est-ce qu'un réseau ?", "category": "Fondamentaux"},
    {"id": "materiel-reseau", "title": "Le matériel réseau", "category": "Fondamentaux"}
]

def generer_cours(node_id, title):
    path = Path(f"content/lessons/{node_id}.md")
    
    print(f"⏳ Génération du cours complet : {title}...")
    prompt = f"""Tu es un expert réseau de niveau CCIE. Rédige un cours TRÈS COMPLET et TECHNIQUE sur le sujet : {title}.
Le cours doit faire environ 10 000 caractères (c'est très important, ne t'arrête pas avant).
Utilise le format Markdown. 
Inclus des tableaux comparatifs, des schémas ASCII, des commandes exactes et un atelier de dépannage.
TRÈS IMPORTANT : Assure-toi de TERMINER TOUTES TES PHRASES et de conclure par une section "## À retenir". 
Ne mets pas de balises ```markdown au début et à la fin, renvoie juste le texte brut."""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=MODEL,
            temperature=0.7,
            max_tokens=8192,
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Contenu vide reçu.")
            
        path.write_text(content, encoding="utf-8")
        print(f"  ✅ Cours sauvegardé : {path} ({len(content)} caractères)")
        
    except Exception as e:
        print(f"  ❌ ÉCHEC : {e}")

if __name__ == "__main__":
    print("--- 🏭 Démarrage de la régénération des cours manquants ---")
    for cours in COURS_A_REGENERER:
        generer_cours(cours["id"], cours["title"])
        time.sleep(2) # Petite pause pour ne pas surcharger l'API
    print("\n--- 🎉 Terminé ! Lance 'python verifier_contenu.py' pour vérifier. ---")