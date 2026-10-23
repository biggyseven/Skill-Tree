import os
import sys
import requests
import json
import re

# ⚠️ REMPLACE LA LIGNE CI-DESSOUS PAR TA VRAIE CLÉ API OPENROUTER
OPENROUTER_API_KEY = "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"

def generate_course(sujet, node_id, niveau):
    if OPENROUTER_API_KEY == "sk-or-v1-TA_CLE_ICI":
        print("❌ ERREUR : Tu dois remplacer la clé API dans le script.")
        return

    print(f"⏳ Génération du cours niveau {niveau} pour : {sujet}...")
    
    try:
        with open("prompt.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
    except FileNotFoundError:
        print("❌ ERREUR : Le fichier 'prompt.txt' est introuvable.")
        return

    prompt = prompt.replace("__SUJET__", sujet)
    prompt = prompt.replace("__NIVEAU__", niveau)
    prompt = prompt.replace("__NODE_ID__", node_id)

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "anthropic/claude-sonnet-5.5", 
                "messages": [{"role": "user", "content": prompt}]
            })
        )
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erreur API : {e}")
        return

    contenu = response.json()['choices'][0]['message']['content']

    contenu = re.sub(r'^```markdown\s*', '', contenu)
    contenu = re.sub(r'\s*```$', '', contenu)

    chemin_fichier = f"content/lessons/{node_id}.md"
    os.makedirs(os.path.dirname(chemin_fichier), exist_ok=True)
    
    with open(chemin_fichier, "w", encoding="utf-8") as f:
        f.write(contenu)
        
    print(f"✅ Cours sauvegardé avec succès dans : {chemin_fichier}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print('Usage: python generate_course.py "Nom du sujet" "id-du-noeud" "Niveau"')
        sys.exit(1)
        
    generate_course(sys.argv[1], sys.argv[2], sys.argv[3])