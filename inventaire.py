import json
from pathlib import Path

def inventaire():
    # 1. Lire les nœuds déclarés dans l'application
    nodes_path = Path("content/nodes.json")
    if not nodes_path.exists():
        print("Erreur : nodes.json introuvable.")
        return
        
    nodes = json.loads(nodes_path.read_text(encoding="utf-8"))
    
    print("=== 📚 INVENTAIRE DE TES CONNAISSANCES ===\n")
    
    manquants_cours = []
    manquants_quiz = []
    complets = []
    
    for node in nodes:
        node_id = node["id"]
        title = node["title"]
        category = node.get("category", "Général")
        
        has_lesson = Path(f"content/lessons/{node_id}.md").exists()
        has_quiz = Path(f"content/quiz/{node_id}.json").exists()
        
        # On ne s'intéresse qu'aux nœuds qui demandent un quiz ou un cours
        requires_quiz = any(r["kind"] == "quiz" for r in node.get("requirements", []))
        
        if has_lesson and has_quiz:
            complets.append(f"✅ {node_id:20} | {title} ({category})")
        else:
            if not has_lesson:
                manquants_cours.append(f"❌ [COURS MANQUANT] {node_id:20} | {title} ({category})")
            if not has_quiz and requires_quiz:
                manquants_quiz.append(f"❌ [QUIZ MANQUANT]  {node_id:20} | {title} ({category})")

    print(f"🎉 Nœuds 100% complets (Cours + Quiz) : {len(complets)}")
    for item in complets:
        print(f"  {item}")
        
    print(f"\n⚠️ Nœuds avec des éléments manquants : {len(manquants_cours) + len(manquants_quiz)}")
    for item in manquants_cours + manquants_quiz:
        print(f"  {item}")

    print("\n" + "="*50)
    print("📋 COPIE-COLLE CE QUI SUIT DANS CHATGPT POUR GÉNÉRER CE QUI MANQUE :")
    print("="*50)
    print("Génère le cours (Markdown) et le quiz (JSON) pour les sujets suivants :")
    for item in manquants_cours + manquants_quiz:
        # On extrait juste l'ID et le Titre pour le prompt
        parts = item.split("|")
        print(f"- {parts[0].split()[-1]} : {parts[1].split('(')[0].strip()}")
    print("="*50)

if __name__ == "__main__":
    inventaire()