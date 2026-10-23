import json
from pathlib import Path

CONTENT_DIR = Path("content")
MIN_LESSON_CHARS = 8000  # Seuil pour considérer un cours complet
MIN_QUIZ_QUESTIONS = 5   # Nombre minimum de questions par quiz

def verifier_lecons():
    print("\n📚 VÉRIFICATION DES COURS (.md) :")
    dossiers = CONTENT_DIR / "lessons"
    if not dossiers.exists():
        return
    
    incomplets = []
    for p in sorted(dossiers.glob("*.md")):
        try:
            contenu = p.read_text(encoding="utf-8")
            taille = len(contenu)
            if taille < MIN_LESSON_CHARS:
                incomplets.append(p.name)
                print(f"  ❌ [INCOMPLET] {p.name:30} : {taille} caractères (min: {MIN_LESSON_CHARS})")
        except Exception as e:
            print(f"  ⚠️ [ERREUR] {p.name} : {e}")
            
    if not incomplets:
        print("  ✅ Tous les cours sont complets !")
    else:
        print(f"\n  ⚠️ {len(incomplets)} cours sont trop courts ou tronqués.")

def verifier_quiz():
    print("\n🧠 VÉRIFICATION DES QUIZ (.json) :")
    dossiers = CONTENT_DIR / "quiz"
    if not dossiers.exists():
        return
        
    incomplets = []
    for p in sorted(dossiers.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            questions = data.get("questions", [])
            if len(questions) < MIN_QUIZ_QUESTIONS:
                incomplets.append(p.name)
                print(f"  ❌ [INCOMPLET] {p.name:30} : Seulement {len(questions)} questions (min: {MIN_QUIZ_QUESTIONS})")
            else:
                # Vérifier que les questions ont bien un prompt et des choix
                for q in questions:
                    if not q.get("prompt") or not q.get("choices"):
                        print(f"  ⚠️ [STRUCTURE INVALIDE] {p.name} : Une question est vide ou sans choix.")
                        break
        except json.JSONDecodeError:
            print(f"  ❌ [JSON CASSÉ] {p.name} : Fichier corrompu, impossible à lire.")
        except Exception as e:
            print(f"  ⚠️ [ERREUR] {p.name} : {e}")

    if not incomplets:
        print("  ✅ Tous les quiz ont au moins 5 questions !")
    else:
        print(f"\n  ⚠️ {len(incomplets)} quiz ont moins de 5 questions.")

if __name__ == "__main__":
    print("=== 🔍 AUDIT DE TON CONimport json
import re
from pathlib import Path

CONTENT_DIR = Path("content")

def verifier_lecons():
    print("\n📚 AUDIT STRUCTUREL DES COURS (.md) :")
    dossiers = CONTENT_DIR / "lessons"
    if not dossiers.exists():
        return
    
    incomplets = []
    for p in sorted(dossiers.glob("*.md")):
        # On ignore les terminaux et les consignes de défi (fichiers courts par nature)
        if p.name.startswith("terminal-") or p.name.startswith("challenge-"):
            continue
            
        try:
            contenu = p.read_text(encoding="utf-8").strip()
            
            # 1. Vérifier les blocs de code non fermés
            blocs_code = contenu.count("```")
            if blocs_code % 2 != 0:
                incomplets.append(p.name)
                print(f"  ❌ [CODE NON FERMÉ] {p.name} : Il manque un ``` à la fin.")
                continue
                
            # 2. Vérifier si le fichier se termine brutalement (pas de ponctuation)
            derniers_chars = contenu[-15:].strip()
            # Si ça ne se termine ni par une ponctuation, ni un backtick, ni un chiffre, c'est suspect
            if not re.search(r'[.!?\`\*\_\]\)\d]$', derniers_chars):
                incomplets.append(p.name)
                print(f"  ❌ [FIN BRUTALE]  {p.name} : Se termine par '...{derniers_chars}' (coupé par l'IA ?)")
                continue
                
            # 3. Vérifier s'il manque des sections clés attendues
            if "## " not in contenu:
                incomplets.append(p.name)
                print(f"  ❌ [SANS STRUCTURE] {p.name} : Aucun titre de section (##) trouvé.")
                continue

        except Exception as e:
            print(f"  ⚠️ [ERREUR] {p.name} : {e}")

    if not incomplets:
        print("  ✅ Tous les cours semblent structurellement complets !")
    else:
        print(f"\n  ⚠️ {len(incomplets)} cours posent problème.")

def verifier_quiz():
    print("\n🧠 AUDIT STRUCTUREL DES QUIZ (.json) :")
    dossiers = CONTENT_DIR / "quiz"
    if not dossiers.exists():
        return
        
    problemes = 0
    for p in sorted(dossiers.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            questions = data.get("questions", [])
            
            if len(questions) == 0:
                print(f"  ❌ [VIDE] {p.name} : Aucune question.")
                problemes += 1
                continue
                
            for idx, q in enumerate(questions):
                # Vérifier que la question a un texte
                if not q.get("prompt") or not str(q.get("prompt")).strip():
                    print(f"  ❌ [PROMPT VIDE] {p.name} : Question {idx+1} n'a pas de texte.")
                    problemes += 1
                    break
                    
                # Vérifier le type de question
                q_type = q.get("type", "qcm")
                if q_type == "qcm":
                    choices = q.get("choices", [])
                    if len(choices) < 2:
                        print(f"  ❌ [CHOIX MANQUANTS] {p.name} : Question {idx+1} a moins de 2 choix.")
                        problemes += 1
                        break
                    if "answer" not in q or not isinstance(q["answer"], int):
                        print(f"  ❌ [RÉPONSE MANQUimport json
import re
from pathlib import Path

CONTENT_DIR = Path("content")

def verifier_lecons():
    print("\n📚 AUDIT STRUCTUREL DES COURS (.md) :")
    dossiers = CONTENT_DIR / "lessons"
    if not dossiers.exists():
        return
    
    incomplets = []
    for p in sorted(dossiers.glob("*.md")):
        if p.name.startswith("terminal-") or p.name.startswith("challenge-"):
            continue
            
        try:
            contenu = p.read_text(encoding="utf-8").strip()
            
            # 1. Vérifier les blocs de code non fermés
            blocs_code = contenu.count("```")
            if blocs_code % 2 != 0:
                incomplets.append(p.name)
                print(f"  ❌ [CODE NON FERMÉ] {p.name} : Il manque un ``` à la fin.")
                continue
                
            # 2. Vérifier si le fichier se termine brutalement
            derniers_chars = contenu[-15:].strip()
            if not re.search(r'[.!?\`\*\_\]\)\d]$', derniers_chars):
                incomplets.append(p.name)
                print(f"  ❌ [FIN BRUTALE]  {p.name} : Se termine par '...{derniers_chars}'")
                continue
                
            # 3. Vérifier s'il manque des sections clés
            if "## " not in contenu:
                incomplets.append(p.name)
                print(f"  ❌ [SANS STRUCTURE] {p.name} : Aucun titre (##) trouvé.")
                continue

        except Exception as e:
            print(f"  ⚠️ [ERREUR] {p.name} : {e}")

    if not incomplets:
        print("  ✅ Tous les cours semblent structurellement complets !")
    else:
        print(f"\n  ⚠️ {len(incomplets)} cours posent problème.")

def verifier_quiz():
    print("\n🧠 AUDIT STRUCTUREL DES QUIZ (.json) :")
    dossiers = CONTENT_DIR / "quiz"
    if not dossiers.exists():
        return
        
    problemes = 0
    for p in sorted(dossiers.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            questions = data.get("questions", [])
            
            if len(questions) == 0:
                print(f"  ❌ [VIDE] {p.name} : Aucune question.")
                problemes += 1
                continue
                
            for idx, q in enumerate(questions):
                if not q.get("prompt") or not str(q.get("prompt")).strip():
                    print(f"  ❌ [PROMPT VIDE] {p.name} : Question {idx+1}")
                    problemes += 1
                    break
                    
                q_type = q.get("type", "qcm")
                if q_type == "qcm":
                    choices = q.get("choices", [])
                    if len(choices) < 2:
                        print(f"  ❌ [CHOIX MANQUANTS] {p.name} : Question {idx+1}")
                        problemes += 1
                        break
                    if "answer" not in q or not isinstance(q["answer"], int):
                        print(f"  ❌ [RÉPONSE MANQUANTE] {p.name} : Question {idx+1}")
                        problemes += 1
                        break
                        
        except json.JSONDecodeError:
            print(f"  ❌ [JSON CASSÉ] {p.name} : Fichier invalide.")
            problemes += 1

    if problemes == 0:
        print("  ✅ Tous les quiz sont valides !")

if __name__ == "__main__":
    print("=== 🔍 AUDIT DE TON CONTENU ===")
    verifier_lecons()
    verifier_quiz()
    print("\n=== Audit terminé ===")ANTE] {p.name} : Question {idx+1} n'a pas d'index 'answer' valide.")
                        problemes += 1
                        break
                        
        except json.JSONDecodeError:
            print(f"  ❌ [JSON CASSÉ] {p.name} : Impossible de lire le fichier JSON.")
            problemes += 1
        except Exception as e:
            print(f"  ⚠️ [ERREUR] {p.name} : {e}")
            problemes += 1

    if problemes == 0:
        print("  ✅ Tous les quiz sont valides !")

if __name__ == "__main__":
    print("=== 🔍 AUDIT DE TON CONTENU (VERSION AVANCÉE) ===")
    verifier_lecons()
    verifier_quiz()
    print("\n=== Audit terminé ===")TENU ===")
    verifier_lecons()
    verifier_quiz()
    print("\n=== Audit terminé ===")

def verifier_lecons():
    print("\n📚 VÉRIFICATION DES COURS (.md) :")
    dossiers = CONTENT_DIR / "lessons"
    if not dossiers.exists():
        return
    
    incomplets = []
    for p in sorted(dossiers.glob("*.md")):
        # On ignore les fichiers de type terminal ou challenge
        if p.name.startswith("terminal-") or p.name.startswith("challenge-"):
            continue
            
        try:
            contenu = p.read_text(encoding="utf-8")
            taille = len(contenu)
            if taille < MIN_LESSON_CHARS:
                incomplets.append(p.name)
                print(f"  ❌ [INCOMPLET] {p.name:30} : {taille} caractères (min: {MIN_LESSON_CHARS})")
        except Exception as e:
            print(f"  ⚠️ [ERREUR] {p.name} : {e}")
            
    if not incomplets:
        print("  ✅ Tous les cours sont complets !")
    else:
        print(f"\n  ⚠️ {len(incomplets)} cours sont trop courts ou tronqués.")