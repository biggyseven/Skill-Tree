"""Tuteur IA pluggable — OpenAI si la clé est présente, sinon message d'aide."""
import os

def ask(node_id: str | None, question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "Le tuteur IA n'est pas configuré côté serveur. "
            "Définis `OPENAI_API_KEY` dans l'environnement pour l'activer."
        )
    try:
        from openai import OpenAI
    except ImportError:
        return "Le package `openai` n'est pas installé. `pip install openai`."

    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content":
                "Tu es un tuteur réseau francophone. Réponds de façon concise, "
                "pédagogique, en t'appuyant sur le contexte du nœud."},
            {"role": "user", "content":
                f"Nœud : {node_id or 'inconnu'}\n\nQuestion : {question}"},
        ],
        max_tokens=500,
        temperature=0.4,
    )
    return resp.choices[0].message.content or "(pas de réponse)"