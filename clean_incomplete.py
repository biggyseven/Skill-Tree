from pathlib import Path

deleted = []
for p in Path("content/lessons").glob("*.md"):
    if len(p.read_text(encoding="utf-8")) < 8000:
        p.unlink()
        deleted.append(p.stem)

print(f"{len(deleted)} cours incomplets supprimés :")
for d in deleted:
    print(f" - {d}")