from pathlib import Path

print("--- Vérification de la taille des cours ---")
for p in sorted(Path("content/lessons").glob("*.md")):
    length = len(p.read_text(encoding="utf-8"))
    if length < 8000:  # On considère qu'un cours de moins de 8000 caractères est incomplet
        print(f"[INCOMPLET] {p.name:30} : {length} caractères")
    else:
        print(f"[OK]        {p.name:30} : {length} caractères")