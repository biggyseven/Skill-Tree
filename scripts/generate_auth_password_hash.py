#!/usr/bin/env python3
"""Generate a PBKDF2 password hash for the Skill-Tree private-site login."""
from __future__ import annotations

import getpass
import sys

from app.auth import create_password_hash


def main() -> int:
    password = getpass.getpass("Nouveau mot de passe Skill-Tree (12 caractères minimum) : ")
    confirm = getpass.getpass("Confirme le mot de passe : ")
    if len(password) < 12:
        print("Erreur : utilise au moins 12 caractères.", file=sys.stderr)
        return 2
    if password != confirm:
        print("Erreur : les deux mots de passe ne correspondent pas.", file=sys.stderr)
        return 2
    print("\nCopie uniquement cette valeur dans la variable Render SKILLTREE_AUTH_PASSWORD_HASH :")
    print(create_password_hash(password))
    print("\nLe mot de passe en clair n'a pas été écrit dans un fichier.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
