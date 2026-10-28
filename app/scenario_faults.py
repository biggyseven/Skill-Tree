"""Bibliothèque de fautes injectables et de validateurs War Room.

Chaque faute travaille sur un device issu du schéma de topologie v2 et sur
l'un de ses ports. Les validateurs décrivent l'état attendu une fois la faute
corrigée par les commandes CLI du Lab Workspace.
"""
from __future__ import annotations

from typing import Any

REQUIRED_ACL_RULE = "permit tcp any host 10.20.0.50 eq 443"


def _interface_config(device: dict[str, Any], port: dict[str, Any]) -> dict[str, Any]:
    config = device.setdefault("config", {})
    interfaces = config.setdefault("interfaces", {})
    return interfaces.setdefault(str(port.get("id", "")), {})


def _apply_vlan_mismatch(device: dict[str, Any], port: dict[str, Any]) -> None:
    interface = _interface_config(device, port)
    expected = interface.get("vlan", port.get("vlan", 20))
    port["vlan"] = 1 if str(expected) != "1" else 20


def _fix_vlan_mismatch(device: dict[str, Any], port: dict[str, Any]) -> bool:
    expected = _interface_config(device, port).get("vlan")
    return expected is not None and str(port.get("vlan")) == str(expected)


def _apply_port_shutdown(device: dict[str, Any], port: dict[str, Any]) -> None:
    port["state"] = "down"


def _fix_port_shutdown(device: dict[str, Any], port: dict[str, Any]) -> bool:
    return str(port.get("state", "")).casefold() == "up"


def _apply_ip_wrong(device: dict[str, Any], port: dict[str, Any]) -> None:
    current = str(port.get("ip") or "")
    port["ip"] = "192.0.2.254" if current != "192.0.2.254" else "192.0.2.253"


def _fix_ip_wrong(device: dict[str, Any], port: dict[str, Any]) -> bool:
    interface = _interface_config(device, port)
    expected = interface.get("ip") or device.get("config", {}).get("ip")
    return expected is not None and str(port.get("ip")) == str(expected)


def _apply_acl_missing(device: dict[str, Any], port: dict[str, Any]) -> None:
    config = device.setdefault("config", {})
    acls = config.setdefault("acls", [])
    config["acls"] = [rule for rule in acls if REQUIRED_ACL_RULE.casefold() not in str(rule).casefold()]


def _fix_acl_missing(device: dict[str, Any], port: dict[str, Any]) -> bool:
    acls = device.get("config", {}).get("acls", [])
    return isinstance(acls, list) and any(REQUIRED_ACL_RULE.casefold() in str(rule).casefold() for rule in acls)


def _apply_trunk_missing(device: dict[str, Any], port: dict[str, Any]) -> None:
    port["mode"] = "access"
    _interface_config(device, port)["mode"] = "access"


def _fix_trunk_missing(device: dict[str, Any], port: dict[str, Any]) -> bool:
    return str(_interface_config(device, port).get("mode", "")).casefold() == "trunk"


def _apply_ospf_down(device: dict[str, Any], port: dict[str, Any]) -> None:
    _interface_config(device, port)["ospf_enabled"] = False


def _fix_ospf_down(device: dict[str, Any], port: dict[str, Any]) -> bool:
    return _interface_config(device, port).get("ospf_enabled") is True


def _apply_default_gateway_missing(device: dict[str, Any], port: dict[str, Any]) -> None:
    device.setdefault("config", {}).pop("gateway", None)


def _fix_default_gateway_missing(device: dict[str, Any], port: dict[str, Any]) -> bool:
    return bool(str(device.get("config", {}).get("gateway") or "").strip())


def _apply_dhcp_off(device: dict[str, Any], port: dict[str, Any]) -> None:
    device.setdefault("config", {})["dhcp_enabled"] = False


def _fix_dhcp_off(device: dict[str, Any], port: dict[str, Any]) -> bool:
    return device.get("config", {}).get("dhcp_enabled") is True


SCENARIO_FAULTS: dict[str, dict[str, Any]] = {
    "vlan_mismatch": {
        "id": "vlan_mismatch",
        "label": "Mauvais VLAN sur un port",
        "target_type": "switch",
        "apply": _apply_vlan_mismatch,
        "fix_validator": _fix_vlan_mismatch,
    },
    "port_shutdown": {
        "id": "port_shutdown",
        "label": "Port administrativement down",
        "target_type": "any",
        "apply": _apply_port_shutdown,
        "fix_validator": _fix_port_shutdown,
    },
    "ip_wrong": {
        "id": "ip_wrong",
        "label": "Adresse IP incorrecte sur une interface",
        "target_type": "any",
        "apply": _apply_ip_wrong,
        "fix_validator": _fix_ip_wrong,
    },
    "acl_missing": {
        "id": "acl_missing",
        "label": "Règle ACL absente sur un routeur",
        "target_type": "router",
        "apply": _apply_acl_missing,
        "fix_validator": _fix_acl_missing,
    },
    "trunk_missing": {
        "id": "trunk_missing",
        "label": "Port switch configuré en access au lieu de trunk",
        "target_type": "switch",
        "apply": _apply_trunk_missing,
        "fix_validator": _fix_trunk_missing,
    },
    "ospf_down": {
        "id": "ospf_down",
        "label": "OSPF désactivé sur une interface",
        "target_type": "router",
        "apply": _apply_ospf_down,
        "fix_validator": _fix_ospf_down,
    },
    "default_gateway_missing": {
        "id": "default_gateway_missing",
        "label": "Passerelle par défaut absente sur un PC",
        "target_type": "pc",
        "apply": _apply_default_gateway_missing,
        "fix_validator": _fix_default_gateway_missing,
    },
    "dhcp_off": {
        "id": "dhcp_off",
        "label": "Service DHCP désactivé sur un routeur",
        "target_type": "router",
        "apply": _apply_dhcp_off,
        "fix_validator": _fix_dhcp_off,
    },
}

# Nom public plus court, pratique pour les appelants et les tests.
FAULTS = SCENARIO_FAULTS
