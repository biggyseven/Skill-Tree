"""Chargement et génération des scénarios War Room.

Les scénarios pilotes et utilisateur résident en JSON dans content/scenarios.
Les tickets RND sont volontairement éphémères côté fichiers : leur JSON est
persisté dans la table war_room_scenarios avec le ticket associé.
"""
from __future__ import annotations

import copy
import json
import random
import re
import secrets
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .scenario_faults import REQUIRED_ACL_RULE, SCENARIO_FAULTS

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "content" / "scenarios"
_SCENARIO_ID = re.compile(r"^(?:[A-Z]{3}-\d{3}|USER-\d{14,20}(?:-[A-F0-9]{4,8})?)$")
SCENARIO_TYPES = {"incident", "change", "problem"}
SCENARIO_SEVERITIES = {"low", "normal", "medium", "high", "critical"}

TOPOLOGY_LABELS = {
    "lan_simple": "LAN simple",
    "lan_wan": "LAN + WAN",
    "multi_vlan": "VLANs multiples",
}


def _stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")


def _port(identifier: str, *, state: str = "up", vlan: int | None = None, ip: str | None = None,
          mask: str = "255.255.255.0") -> dict[str, Any]:
    item: dict[str, Any] = {"id": identifier, "name": identifier, "state": state}
    if vlan is not None:
        item["vlan"] = vlan
    if ip is not None:
        item.update({"ip": ip, "mask": mask})
    return item


def _switch(identifier: str, x: int, y: int, port_vlans: dict[str, int],
            trunks: set[str] | None = None) -> dict[str, Any]:
    trunks = trunks or set()
    ports = [
        {**_port(port_id, vlan=vlan), "mode": "trunk" if port_id in trunks else "access"}
        for port_id, vlan in port_vlans.items()
    ]
    interfaces: dict[str, Any] = {}
    for port_id, vlan in port_vlans.items():
        if port_id in trunks:
            interfaces[port_id] = {"mode": "trunk", "vlan": vlan, "allowed_vlans": [1, 20, 30]}
        else:
            interfaces[port_id] = {"mode": "access", "vlan": vlan}
    return {
        "id": identifier, "type": "switch", "x": x, "y": y, "label": identifier,
        "model": "Cisco Catalyst 2960", "iconType": "switch", "ports": ports,
        "config": {"hostname": identifier, "vlans": [1, 20, 30], "interfaces": interfaces},
    }


def _router(identifier: str, x: int, y: int, first_ip: str = "10.20.0.1",
            second_ip: str = "192.168.10.1") -> dict[str, Any]:
    ports = [
        _port("Fa0/0", ip=first_ip),
        _port("Fa0/1", ip=second_ip),
    ]
    interfaces = {
        "Fa0/0": {"ip": first_ip, "mask": "255.255.255.0", "ospf_enabled": True},
        "Fa0/1": {"ip": second_ip, "mask": "255.255.255.0", "ospf_enabled": True},
    }
    return {
        "id": identifier, "type": "router", "x": x, "y": y, "label": identifier,
        "model": "Cisco ISR", "iconType": "router", "ports": ports,
        "config": {
            "hostname": identifier,
            "interfaces": interfaces,
            "acls": [f"101 {REQUIRED_ACL_RULE}"],
            "dhcp_enabled": True,
        },
    }


def _pc(identifier: str, x: int, y: int, ip: str = "10.20.0.11",
         gateway: str = "10.20.0.1") -> dict[str, Any]:
    return {
        "id": identifier, "type": "pc", "x": x, "y": y, "label": identifier,
        "model": "PC", "iconType": "pc", "ports": [_port("eth0", ip=ip)],
        "config": {"hostname": identifier, "ip": ip, "mask": "255.255.255.0", "gateway": gateway},
    }


def _link(identifier: str, from_node: str, from_port: str, to_node: str, to_port: str) -> dict[str, Any]:
    return {
        "id": identifier,
        "from": {"node": from_node, "port": from_port},
        "to": {"node": to_node, "port": to_port},
        "cable_type": "copper_straight",
        "state": "up",
    }


def _base_topologies() -> dict[str, dict[str, Any]]:
    # LAN simple : routeur, switch d'accès et un poste. Aucun trunk sur SW1.
    lan_simple = {
        "schema_version": 2,
        "nodes": [
            _router("R1", 100, 170),
            _switch("SW1", 390, 170, {"Fa0/1": 1, "Fa0/7": 20, "Fa0/8": 20}),
            _pc("PC1", 650, 300),
        ],
        "links": [
            _link("L1", "R1", "Fa0/0", "SW1", "Fa0/1"),
            _link("L2", "SW1", "Fa0/7", "PC1", "eth0"),
        ],
    }

    # LAN + WAN : un site distant et son poste, reliés au routeur central.
    lan_wan = {
        "schema_version": 2,
        "nodes": [
            _router("R1", 100, 170),
            _switch("SW1", 365, 170, {"Fa0/1": 1, "Fa0/7": 20, "Fa0/8": 20}, {"Fa0/1"}),
            _pc("PC1", 365, 360),
            _router("R2", 680, 170, "172.16.0.1", "192.168.20.1"),
            _pc("PC2", 880, 360, "172.16.0.10", "172.16.0.1"),
        ],
        "links": [
            _link("L1", "R1", "Fa0/0", "SW1", "Fa0/1"),
            _link("L2", "SW1", "Fa0/7", "PC1", "eth0"),
            _link("L3", "R1", "Fa0/1", "R2", "Fa0/0"),
            _link("L4", "R2", "Fa0/1", "PC2", "eth0"),
        ],
    }

    # VLAN multiples : deux switches, un trunk inter-switch et un routeur L3.
    vlan_multiple = {
        "schema_version": 2,
        "nodes": [
            _router("R1", 390, 70),
            _switch("SW1", 100, 210, {"Fa0/1": 1, "Fa0/7": 20, "Fa0/8": 30}, {"Fa0/1"}),
            _switch("SW2", 650, 210, {"Fa0/1": 1, "Fa0/2": 20, "Fa0/3": 30}, {"Fa0/1"}),
            _pc("PC1", 100, 410, "10.20.0.11", "10.20.0.1"),
            _pc("PC2", 650, 410, "10.30.0.11", "10.30.0.1"),
        ],
        "links": [
            _link("L1", "R1", "Fa0/0", "SW1", "Fa0/1"),
            _link("L2", "SW1", "Fa0/1", "SW2", "Fa0/1"),
            _link("L3", "SW1", "Fa0/7", "PC1", "eth0"),
            _link("L4", "SW2", "Fa0/2", "PC2", "eth0"),
        ],
    }
    return {
        "lan_simple": {"id": "lan_simple", "label": TOPOLOGY_LABELS["lan_simple"], "topology": lan_simple},
        "lan_wan": {"id": "lan_wan", "label": TOPOLOGY_LABELS["lan_wan"], "topology": lan_wan},
        "multi_vlan": {"id": "multi_vlan", "label": TOPOLOGY_LABELS["multi_vlan"], "topology": vlan_multiple},
    }


BASE_TOPOLOGIES = _base_topologies()


def load_scenario(scenario_id: str) -> dict[str, Any]:
    """Charge un scénario depuis le dossier utilisateur/pilote sans accepter un chemin client."""
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


def get_topology_template(topology_id: str) -> dict[str, Any]:
    """Retourne une copie isolée d'un modèle de topologie prédéfini."""
    try:
        return copy.deepcopy(BASE_TOPOLOGIES[str(topology_id)]["topology"])
    except KeyError as exc:
        raise ValueError(f"Topologie inconnue : {topology_id}") from exc


def _device_by_id(topology: dict[str, Any], device_id: str) -> dict[str, Any] | None:
    return next((item for item in topology.get("nodes", []) if str(item.get("id")) == str(device_id)), None)


def _port_by_id(device: dict[str, Any], port_id: str) -> dict[str, Any] | None:
    return next((item for item in device.get("ports", []) if str(item.get("id")) == str(port_id)), None)


def _compatible_device_types(fault_id: str) -> set[str]:
    fault = SCENARIO_FAULTS.get(fault_id)
    if not fault:
        return set()
    target_type = fault.get("target_type")
    if target_type == "any":
        return {"switch", "router", "pc"}
    return {str(target_type)} if target_type in {"switch", "router", "pc"} else set()


def _eligible_ports(device: dict[str, Any], fault_id: str) -> list[dict[str, Any]]:
    interfaces = device.get("config", {}).get("interfaces", {})
    eligible: list[dict[str, Any]] = []
    for port in device.get("ports", []):
        port_id = str(port.get("id", ""))
        interface = interfaces.get(port_id, {}) if isinstance(interfaces, dict) else {}
        if fault_id == "vlan_mismatch" and (
            "vlan" not in port or str(interface.get("mode", "")).casefold() != "access"
            or interface.get("vlan") is None
        ):
            continue
        if fault_id == "ip_wrong" and not (port.get("ip") and (interface.get("ip") or device.get("config", {}).get("ip"))):
            continue
        if fault_id == "acl_missing":
            acls = device.get("config", {}).get("acls", [])
            if not isinstance(acls, list) or not any(REQUIRED_ACL_RULE.casefold() in str(value).casefold() for value in acls):
                continue
        if fault_id == "trunk_missing" and str(interface.get("mode", "")).casefold() != "trunk":
            continue
        if fault_id == "ospf_down" and interface.get("ospf_enabled") is not True:
            continue
        if fault_id == "default_gateway_missing" and not device.get("config", {}).get("gateway"):
            continue
        if fault_id == "dhcp_off" and device.get("config", {}).get("dhcp_enabled") is not True:
            continue
        if fault_id == "port_shutdown" and str(port.get("state", "")).casefold() != "up":
            continue
        eligible.append(port)
    return eligible


def get_compatible_targets(topology_id: str, fault_id: str) -> list[dict[str, Any]]:
    """Retourne les équipements/ports qui supportent réellement la faute choisie."""
    if topology_id not in BASE_TOPOLOGIES:
        return []
    fault = SCENARIO_FAULTS.get(fault_id)
    if not fault:
        return []
    topology = get_topology_template(topology_id)
    target_types = _compatible_device_types(fault_id)
    result: list[dict[str, Any]] = []
    for device in topology["nodes"]:
        if device.get("type") not in target_types:
            continue
        ports = _eligible_ports(device, fault_id)
        if not ports:
            continue
        result.append({
            "id": device["id"],
            "label": device.get("label", device["id"]),
            "type": device.get("type"),
            "ports": [{"id": port["id"], "label": port.get("name", port["id"])} for port in ports],
        })
    return result


def get_scenario_options() -> dict[str, Any]:
    """Structure publique nécessaire aux listes dynamiques du formulaire Alpine."""
    targets: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for topology_id in BASE_TOPOLOGIES:
        targets[topology_id] = {
            fault_id: get_compatible_targets(topology_id, fault_id)
            for fault_id in SCENARIO_FAULTS
        }
    faults = []
    for fault_id, fault in SCENARIO_FAULTS.items():
        compatible = [key for key, matrix in targets.items() if matrix.get(fault_id)]
        faults.append({
            "id": fault_id,
            "label": fault["label"],
            "target_type": fault["target_type"],
            "topologies": compatible,
        })
    return {
        "topologies": [{"id": key, "label": item["label"]} for key, item in BASE_TOPOLOGIES.items()],
        "faults": faults,
        "targets": targets,
    }


def _fault_rule(fault_id: str, device: dict[str, Any], port: dict[str, Any]) -> dict[str, Any]:
    config = device.get("config", {})
    interfaces = config.get("interfaces", {})
    interface = interfaces.get(str(port.get("id", "")), {}) if isinstance(interfaces, dict) else {}
    port_id = str(port.get("id", ""))
    if fault_id == "vlan_mismatch":
        return {"target": device["id"], "path": f"ports.{port_id}.vlan", "operator": "equals",
                "value": interface.get("vlan", port.get("vlan")), "description": f"{device['id']} {port_id} doit rester dans le VLAN attendu."}
    if fault_id == "port_shutdown":
        return {"target": device["id"], "path": f"ports.{port_id}.state", "operator": "equals",
                "value": "up", "description": f"{device['id']} {port_id} doit être administrativement actif (no shutdown)."}
    if fault_id == "ip_wrong":
        expected = port.get("ip") or interface.get("ip") or config.get("ip")
        return {"target": device["id"], "path": f"ports.{port_id}.ip", "operator": "equals",
                "value": expected, "description": f"{device['id']} {port_id} doit retrouver son adresse IP attendue."}
    if fault_id == "acl_missing":
        return {"target": device["id"], "path": "config.acls", "operator": "contains",
                "value": REQUIRED_ACL_RULE, "description": "L'ACL doit autoriser TCP/443 vers le serveur applicatif."}
    if fault_id == "trunk_missing":
        return {"target": device["id"], "path": f"config.interfaces.{port_id}.mode", "operator": "equals",
                "value": "trunk", "description": f"{device['id']} {port_id} doit être configuré en trunk."}
    if fault_id == "ospf_down":
        return {"target": device["id"], "path": f"config.interfaces.{port_id}.ospf_enabled", "operator": "equals",
                "value": True, "description": f"OSPF doit être actif sur {device['id']} {port_id}."}
    if fault_id == "default_gateway_missing":
        return {"target": device["id"], "path": "config.gateway", "operator": "equals",
                "value": config.get("gateway"), "description": f"{device['id']} doit avoir une passerelle par défaut."}
    if fault_id == "dhcp_off":
        return {"target": device["id"], "path": "config.dhcp_enabled", "operator": "equals",
                "value": True, "description": f"Le service DHCP doit être activé sur {device['id']}."}
    raise ValueError(f"Faute inconnue : {fault_id}")


def build_scenario(
    *,
    scenario_id: str,
    title: str,
    scenario_type: str,
    severity: str,
    topology_id: str,
    fault_id: str,
    target_device: str,
    target_port: str,
    sla_minutes: int,
    reward_xp: int = 150,
) -> dict[str, Any]:
    """Construit un scénario validable à partir d'un modèle et d'une faute unique."""
    if scenario_type not in SCENARIO_TYPES:
        raise ValueError("Le type doit être incident, change ou problem.")
    if severity not in SCENARIO_SEVERITIES:
        raise ValueError("La sévérité doit être low, normal, medium, high ou critical.")
    if not 5 <= int(sla_minutes) <= 240:
        raise ValueError("Le SLA doit être compris entre 5 et 240 minutes.")
    fault = SCENARIO_FAULTS.get(fault_id)
    if not fault:
        raise ValueError("Faute inconnue.")
    topology = get_topology_template(topology_id)
    device = _device_by_id(topology, target_device)
    if device is None:
        raise ValueError(f"Équipement cible introuvable : {target_device}")
    if device not in [item for item in topology["nodes"] if item.get("type") in _compatible_device_types(fault_id)]:
        raise ValueError("La faute n'est pas compatible avec le type d'équipement sélectionné.")
    port = _port_by_id(device, target_port)
    if port is None or target_port not in {item["id"] for target in get_compatible_targets(topology_id, fault_id) for item in target["ports"] if target["id"] == target_device}:
        raise ValueError("Le port cible est absent ou incompatible avec la faute.")
    # Vérifier d'abord que le modèle est sain sur cette propriété, puis que
    # l'injection le fait effectivement échouer avant de générer le scénario.
    if not fault["fix_validator"](device, port):
        raise ValueError(f"La topologie {topology_id} ne permet pas d'injecter {fault_id} sur cette cible.")
    rule = _fault_rule(fault_id, device, port)
    fault["apply"](device, port)
    if fault["fix_validator"](device, port):
        raise ValueError(f"La faute {fault_id} n'a pas pu être injectée correctement.")
    return {
        "id": scenario_id,
        "title": str(title).strip(),
        "type": scenario_type,
        "severity": severity,
        "sla_minutes": int(sla_minutes),
        "reward_xp": max(0, int(reward_xp)),
        "story": (
            f"{str(title).strip()} — Le NOC constate une dégradation de connectivité autour de "
            f"{target_device} {target_port}. Qualifiez l'impact, diagnostiquez la configuration, "
            "appliquez une correction ciblée via la CLI et validez le rétablissement."
        ),
        "impact": (
            f"La connectivité des équipements dépendant de {target_device} {target_port} est dégradée. "
            "Des utilisateurs signalent une perte d'accès ou une perturbation d'un service métier."
        ),
        "reported_by": "Centre des opérations réseau (NOC)",
        "diagnostic_steps": [
            {
                "title": "Qualifier l'impact",
                "instructions": f"Identifiez les équipements et services touchés autour de {target_device} {target_port}. Comparez les symptômes avant de modifier la configuration.",
                "hint": "Vérifiez si le problème touche un seul poste, un segment ou plusieurs équipements.",
            },
            {
                "title": "Examiner la configuration",
                "instructions": f"Inspectez {target_device} et son interface {target_port}. Utilisez les commandes show adaptées pour observer l'état opérationnel et la configuration active.",
                "hint": "Suivez les indices de couche 1, couche 2 et couche 3 sans modifier les autres interfaces.",
            },
            {
                "title": "Corriger et vérifier",
                "instructions": f"Appliquez une correction minimale sur {target_device} {target_port}, puis relancez la vérification du ticket.",
                "hint": "Contrôlez à nouveau l'état de l'interface et les paramètres après la commande de correction.",
            },
        ],
        "initial_topology": topology,
        "resolution_check": {"type": "config_assertions", "rules": [rule]},
        "hidden_faults": [{
            "id": "F1",
            "device": target_device,
            "interface": target_port,
            "fault_id": fault_id,
            "detail": fault["label"],
        }],
        "post_mortem_template": {"root_cause": "", "impact": "", "corrective_action": ""},
        "fault_id": fault_id,
        "target_device": target_device,
        "target_port": target_port,
        "topology_template": topology_id,
    }


def generate_random_scenario() -> dict[str, Any]:
    """Génère une faute unique, réparable et stockable ensuite directement en base."""
    topology_id = random.choice(list(BASE_TOPOLOGIES))
    compatible_faults = [
        fault_id for fault_id in SCENARIO_FAULTS
        if get_compatible_targets(topology_id, fault_id)
    ]
    if not compatible_faults:
        raise RuntimeError(f"Aucune faute compatible avec la topologie {topology_id}.")
    fault_id = random.choice(compatible_faults)
    targets = get_compatible_targets(topology_id, fault_id)
    target = random.choice(targets)
    port = random.choice(target["ports"])
    scenario_id = f"RND-{_stamp()}-{secrets.token_hex(3).upper()}"
    fault = SCENARIO_FAULTS[fault_id]
    return build_scenario(
        scenario_id=scenario_id,
        title=f"Ticket surprise — anomalie réseau sur {target['id']} {port['id']}",
        scenario_type=random.choice(sorted(SCENARIO_TYPES)),
        severity=random.choice(["normal", "high", "critical"]),
        topology_id=topology_id,
        fault_id=fault_id,
        target_device=target["id"],
        target_port=port["id"],
        sla_minutes=random.randint(20, 45),
        reward_xp=random.randint(100, 200),
    )
