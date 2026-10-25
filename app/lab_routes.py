from fastapi import APIRouter, Depends, HTTPException
from typing import Iterator
from pathlib import Path
import json
import os

from app.engine import SkillTree
from app.db import connect, DEFAULT_DB

router = APIRouter()
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LABS_V2_DIR = PROJECT_ROOT / "labs_v2"

def get_tree() -> Iterator[SkillTree]:
    db_path = Path(os.environ.get("SKILLTREE_DB", DEFAULT_DB))
    conn = connect(db_path, check_same_thread=False)
    try:
        yield SkillTree(conn)
    finally:
        conn.close()

def get_nested_value(data, path):
    keys = path.replace('[', '.').replace(']', '').split('.')
    for key in keys:
        if not key: continue
        if isinstance(data, dict) and key in data:
            data = data[key]
        elif isinstance(data, list) and key.isdigit() and int(key) < len(data):
            data = data[int(key)]
        else:
            return None
    return data

@router.get("/lab/v2/{lab_id}")
async def get_lab_v2(lab_id: str, tree: SkillTree = Depends(get_tree)):
    lab_path = LABS_V2_DIR / f"{lab_id}.json"
    
    if lab_path.exists():
        with open(lab_path, "r", encoding="utf-8-sig") as f:
            lab_data = json.load(f)
    else:
        try:
            node = tree.node(lab_id)
        except Exception:
            raise HTTPException(status_code=404, detail=f"Le cours {lab_id} n'existe pas.")
        
        lab_data = {
            "id": lab_id,
            "title": node.title,
            "level": "Sandbox",
            "prompt": f"Bienvenue dans l'espace de travail pour le cours : {node.title}.\n\nCet espace est vierge. Glissez des équipements depuis la palette pour construire votre propre topologie.",
            "objectives": ["Construire une topologie", "Tester vos configurations"],
            "initial_topology": {"schema_version": 2, "nodes": [], "links": [], "simulation": {"state": "idle", "event_log": []}},
            "check": {"type": "manual_review", "rules": [], "pass_threshold": 1.0}
        }
        
    return {"id": lab_id, "schema_version": 2, "definition": lab_data, "initial_topology": lab_data.get("initial_topology")}

@router.post("/lab/v2/{lab_id}/check")
async def check_lab_v2(lab_id: str, payload: dict, tree: SkillTree = Depends(get_tree)):
    lab_path = LABS_V2_DIR / f"{lab_id}.json"
    if not lab_path.exists():
        return {"passed": True, "score": 1.0, "results": [{"rule_id": "sandbox", "passed": True, "message": "Bac à sable : aucune règle de validation."}]}
    
    with open(lab_path, "r", encoding="utf-8-sig") as f:
        lab_def = json.load(f)

    rules = lab_def.get("check", {}).get("rules", [])
    if not rules:
        return {"passed": True, "score": 1.0, "results": [{"rule_id": "no_rules", "passed": True, "message": "Aucune règle définie."}]}

    topo = payload.get("topology", {})
    nodes = {n["id"]: n for n in topo.get("nodes", [])}
    results = []
    passed_count = 0

    for rule in rules:
        dev_id = rule.get("device")
        path = rule.get("path")
        operator = rule.get("operator")
        expected = rule.get("expected")
        
        device = nodes.get(dev_id)
        if not device:
            results.append({"rule_id": rule["id"], "passed": False, "message": f"Équipement {dev_id} manquant."})
            continue

        actual = get_nested_value(device, path)
        passed = False

        if operator == "equals":
            passed = (str(actual) == str(expected))
        elif operator == "contains_network":
            if actual and isinstance(actual, list):
                passed = any(str(expected["network"]) in str(a.get("network", "")) for a in actual)
        
        if passed: passed_count += 1
        results.append({"rule_id": rule["id"], "passed": passed, "message": rule.get("description", "Règle") + (" (OK)" if passed else " (Échec)")})

    score = passed_count / len(rules) if rules else 1.0
    return {"passed": score >= 0.7, "score": score, "results": results}
