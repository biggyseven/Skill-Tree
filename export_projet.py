import os

# Dossiers à ignorer pour ne pas surcharger le fichier
EXCLUDE_DIRS = {'.git', '__pycache__', '.venv', 'venv', 'env', 'backups', 'node_modules'}
# Extensions de fichiers à inclure
INCLUDE_EXTS = {'.py', '.json', '.md', '.html', '.sh', '.txt'}

output_file = "projet_complet.md"

with open(output_file, "w", encoding="utf-8") as out:
    out.write("# Code Source Complet - SAAS RS\n\n")
    
    for root, dirs, files in os.walk("."):
        # Filtrer les dossiers
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            ext = os.path.splitext(file)[1]
            if ext in INCLUDE_EXTS:
                filepath = os.path.join(root, file)
                # Ne pas inclure le fichier en cours de création
                if filepath == f".\\{output_file}" or filepath == f"./{output_file}":
                    continue
                    
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                    out.write(f"## Fichier : {filepath}\n")
                    out.write(f"```{ext[1:]}\n{content}\n```\n\n---\n\n")
                except Exception as e:
                    pass # Ignore les fichiers illisibles (binaires, etc.)

print(f"✅ Terminé ! Ouvre le fichier {output_file}")