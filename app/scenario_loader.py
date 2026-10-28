"""Chargement sécurisé des scénarios War Room depuis content/scenarios."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "content" / "scenarios"
_SCENARIO_ID = re.compile(r"^[A-Z]{3}-\d{3}$")


def load_scenario(scenario_id: str) -> dict[str, Any]:
    """Charge un scénario identifié par un ID strict, sans accepter de chemin fourni par le client."""
    normalized = str(scenario_id or "").strip().upper()
    if not _SCENARIO_ID.fullmatch(normalized):
        raise FileNotFoundError(f"Scénario introuvable : {scenario_id}")
    path = SCENARIO_DIR / f"{normalized}.json"
    if not path.is_file():
        raise FileNotFoundError(f"Scénario introuvable : {normalized}")
    with path.open("r", encoding="utf-8") as handle:
        scenario = json.load(handle)
    if scenario.get("id") != normalized:
        raise ValueError(f"L'identifiant du scénario {normalized} ne correspond pas au nom de fichier.")
    return scenario


def list_scenarios() -> list[dict[str, Any]]:
    """Renvoie les scénarios JSON du dossier, triés par identifiant."""
    scenarios: list[dict[str, Any]] = []
    if not SCENARIO_DIR.is_dir():
        return scenarios
    for path in sorted(SCENARIO_DIR.glob("*.json")):
        if not _SCENARIO_ID.fullmatch(path.stem):
            continue
        try:
            with path.open("r", encoding="utf-8") as handle:
                scenario = json.load(handle)
            if scenario.get("id") == path.stem:
                scenarios.append(scenario)
        except (OSError, json.JSONDecodeError):
            continue
    return scenarios
