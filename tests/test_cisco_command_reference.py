import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_NAME = "Commandes & Aide-mémoire"
EXPECTED = {
    "cmd-base": "Configuration de base (Hostname, SSH, Mots de passe, NTP)",
    "cmd-interfaces": "Interfaces & VLANs (Switchport, Trunk, Router-on-a-stick)",
    "cmd-routage": "Routage & OSPF (Routes statiques, OSPF, EIGRP)",
    "cmd-securite": "Sécurité & ACL (Access-lists, Port-security, DHCP Snooping)",
    "cmd-verification": "Vérification & Diagnostic (Show, Debug, Ping, Traceroute)",
}


def _nodes():
    return json.loads((ROOT / "content" / "nodes.json").read_text(encoding="utf-8"))


def _word_count(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return len(re.findall(r"\b[\wÀ-ÿ’'-]+\b", text, flags=re.UNICODE))


def test_cisco_cheatsheet_module_is_registered_in_catalog_source():
    catalog = (ROOT / "app" / "main_ui" / "skilltree-catalog.js").read_text(encoding="utf-8")

    assert "id: 'commandes', label: 'Commandes & Aide-mémoire'" in catalog
    assert "icon: '⌨️'" in catalog
    for item in [
        "Config de base",
        "Interfaces & VLANs",
        "Routage & OSPF",
        "Sécurité & ACL",
        "Vérification & Diagnostic",
    ]:
        assert item in catalog
    assert "if (id.startsWith('cmd-')) return 'commandes';" in catalog
    for node_id in EXPECTED:
        assert f"'{node_id}': 'intermediaire'" in catalog


def test_cisco_cheatsheet_nodes_are_open_and_have_no_quiz_requirement():
    nodes = _nodes()
    by_id = {node["id"]: node for node in nodes}

    assert len(by_id) == len(nodes), "Les identifiants de nœuds doivent être uniques."
    for node_id, title in EXPECTED.items():
        node = by_id[node_id]
        assert node["module"] == MODULE_NAME
        assert node["title"] == title
        assert node.get("prereqs", []) == []
        assert node.get("requirements", []) == []

        lesson = ROOT / "content" / "lessons" / f"{node_id}.md"
        assert lesson.is_file(), f"Fiche manquante : {lesson.name}"
        assert 800 <= _word_count(lesson) <= 1200, f"La fiche {lesson.name} doit comporter entre 800 et 1200 mots."
        assert not (ROOT / "content" / "quiz" / f"{node_id}.json").exists(), f"Quiz individuel inattendu pour {node_id}"
