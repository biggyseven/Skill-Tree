import os
import re

LESSON_DIR = "content/lessons"

def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 1. Détecter et protéger le frontmatter (s'il existe)
    frontmatter = []
    content_start_index = 0
    
    if lines and lines[0].strip() == "---":
        frontmatter.append(lines[0])
        for i in range(1, len(lines)):
            frontmatter.append(lines[i])
            if lines[i].strip() == "---":
                content_start_index = i + 1
                break

    # 2. Nettoyer le reste du contenu
    cleaned_content = []
    for line in lines[content_start_index:]:
        # Si la ligne est exactement un séparateur, on la supprime
        if re.match(r"^\s*(---+|\*\*\*+|___+)\s*$", line):
            continue
        cleaned_content.append(line)

    # 3. Réécrire le fichier
    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(frontmatter)
        f.writelines(cleaned_content)

print("🧹 Nettoyage des séparateurs dans les cours...\n")
count = 0
for filename in os.listdir(LESSON_DIR):
    if filename.endswith(".md"):
        filepath = os.path.join(LESSON_DIR, filename)
        clean_file(filepath)
        count += 1

print(f"✅ {count} fichiers nettoyés avec succès !")