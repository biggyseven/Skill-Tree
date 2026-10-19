"""Create consistent SQLite and content backups for the project."""
from __future__ import annotations

import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def create_backup(root: str | Path = PROJECT_ROOT) -> tuple[Path, Path]:
    project_root = Path(root)
    database = project_root / "skilltree.db"
    content = project_root / "content"
    backups = project_root / "backups"

    if not database.is_file():
        raise FileNotFoundError(f"Base SQLite introuvable : {database}")
    if not content.is_dir():
        raise FileNotFoundError(f"Dossier de contenu introuvable : {content}")

    backups.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    database_backup = backups / f"db_{timestamp}.db"
    content_backup = backups / f"content_{timestamp}.zip"

    source = sqlite3.connect(str(database))
    destination = sqlite3.connect(str(database_backup))
    try:
        source.backup(destination)
    finally:
        destination.close()
        source.close()

    archive_base = content_backup.with_suffix("")
    shutil.make_archive(str(archive_base), "zip", root_dir=content)
    print(f"Sauvegarde créée : {database_backup} et {content_backup}")
    return database_backup, content_backup


def main() -> int:
    create_backup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
