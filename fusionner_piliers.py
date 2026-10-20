import json
from pathlib import Path

# Les nouveaux nœuds à ajouter (issus du Master Plan)
NOUVEAUX_NOEUDS = [
    # --- PILIER 1 & 2 : Fondations & Cœur ---
    {"id": "cabling", "title": "Câblage et Normes", "category": "Fondamentaux", "order": 4, "description": "Cuivre, fibre, normes T568A/B.", "prereqs": [], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "poe", "title": "Power over Ethernet (PoE)", "category": "Fondamentaux", "order": 7, "description": "Alimenter les équipements via le câble.", "prereqs": ["cabling"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "etherchannel", "title": "Agrégation de liens (LACP)", "category": "Couche 2 — Commutation", "order": 56, "description": "Combiner plusieurs liens physiques.", "prereqs": ["vlan"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "vtp", "title": "VTP et gestion des VLANs", "category": "Couche 2 — Commutation", "order": 57, "description": "Propager les VLANs entre switchs.", "prereqs": ["vlan"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    
    # --- PILIER 3 : Routage Avancé ---
    {"id": "eigrp", "title": "EIGRP", "category": "Routage", "order": 112, "description": "Protocole de routage hybride Cisco.", "prereqs": ["routing"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "pbr", "title": "Policy-Based Routing (PBR)", "category": "Routage", "order": 113, "description": "Router selon la source ou le port.", "prereqs": ["routing"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "bgp-advanced", "title": "BGP Avancé", "category": "Routage", "order": 121, "description": "Route Reflectors, communautés.", "prereqs": ["bgp"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "vrf", "title": "VRF (Virtual Routing)", "category": "Routage", "order": 122, "description": "Isolation de tables de routage.", "prereqs": ["routing"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "multicast", "title": "Multicast (PIM, IGMP)", "category": "Routage", "order": 123, "description": "Routage un-vers-plusieurs.", "prereqs": ["routing"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "qos-advanced", "title": "QoS Avancée", "category": "Routage", "order": 124, "description": "LLQ, CBWFQ, Shaping.", "prereqs": ["routing"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    
    # --- PILIER 4 : Cloud & Datacenter ---
    {"id": "vxlan", "title": "VXLAN et Datacenter", "category": "Cloud & Automatisation", "order": 161, "description": "Encapsulation L2 sur L3.", "prereqs": ["vlan"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "spine-leaf", "title": "Architecture Spine/Leaf", "category": "Cloud & Automatisation", "order": 162, "description": "Topologie datacenter moderne.", "prereqs": ["etherchannel"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "aws-vpc", "title": "AWS VPC", "category": "Cloud & Automatisation", "order": 163, "description": "Réseau virtuel AWS.", "prereqs": ["cloud"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "azure-vnet", "title": "Azure VNet", "category": "Cloud & Automatisation", "order": 164, "description": "Réseau virtuel Azure.", "prereqs": ["cloud"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "sd-wan", "title": "SD-WAN", "category": "Cloud & Automatisation", "order": 165, "description": "Gestion centralisée du WAN.", "prereqs": ["routing"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    
    # --- PILIER 5 : Sécurité ---
    {"id": "ipsec", "title": "VPN IPsec", "category": "Sécurité", "order": 145, "description": "Tunnels chiffrés site-à-site.", "prereqs": ["vpn"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "wireguard", "title": "VPN WireGuard", "category": "Sécurité", "order": 146, "description": "VPN moderne et rapide.", "prereqs": ["vpn"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "radius", "title": "Authentification RADIUS", "category": "Sécurité", "order": 147, "description": "Contrôle d'accès centralisé.", "prereqs": ["aaa"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "pki", "title": "PKI et Certificats", "category": "Sécurité", "order": 148, "description": "Autorités de certification.", "prereqs": ["aaa"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "zero-trust-architecture", "title": "Zero Trust", "category": "Sécurité", "order": 149, "description": "Micro-segmentation et SASE.", "prereqs": ["firewall"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "ddos-mitigation", "title": "Attaques DDoS", "category": "Sécurité", "order": 150, "description": "Mitigation des attaques volumétriques.", "prereqs": ["firewall"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "layer2-security", "title": "Sécurité L2", "category": "Sécurité", "order": 151, "description": "ARP Spoofing, DHCP Snooping.", "prereqs": ["vlan"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    
    # --- PILIER 6 : Automatisation ---
    {"id": "netmiko", "title": "Python et Netmiko", "category": "Cloud & Automatisation", "order": 171, "description": "SSH automatisé vers les routeurs.", "prereqs": ["automation"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "restconf", "title": "API RESTCONF/NETCONF", "category": "Cloud & Automatisation", "order": 172, "description": "Configuration via API HTTP.", "prereqs": ["automation"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "terraform", "title": "Terraform", "category": "Cloud & Automatisation", "order": 173, "description": "Infrastructure as Code.", "prereqs": ["automation"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "napalm", "title": "NAPALM", "category": "Cloud & Automatisation", "order": 174, "description": "Abstraction multi-constructeurs.", "prereqs": ["automation"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "cicd-network", "title": "CI/CD pour le réseau", "category": "Cloud & Automatisation", "order": 175, "description": "Git et pipelines de déploiement.", "prereqs": ["automation"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    
    # --- PILIER 7 : Exploitation ---
    {"id": "wireshark-advanced", "title": "Wireshark Avancé", "category": "Exploitation", "order": 152, "description": "Analyse de captures complexes.", "prereqs": ["troubleshooting"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "mtu-pmtud", "title": "Dépannage MTU", "category": "Exploitation", "order": 153, "description": "PMTUD et fragmentation.", "prereqs": ["troubleshooting"], "requirements": [{"kind": "quiz", "min_score": 80}]},
    {"id": "itil-rca", "title": "ITIL et RCA", "category": "Exploitation", "order": 154, "description": "Gestion d'incident et cause racine.", "prereqs": ["troubleshooting"], "requirements": [{"kind": "quiz", "min_score": 80}]}
]

def fusionner():
    chemin = Path("content/nodes.json")
    if not chemin.exists():
        print("Erreur : content/nodes.json introuvable.")
        return
        
    noeuds_existants = json.loads(chemin.read_text(encoding="utf-8"))
    ids_existants = {n["id"] for n in noeuds_existants}
    
    ajoutes = 0
    for nouveau in NOUVEAUX_NOEUDS:
        if nouveau["id"] not in ids_existants:
            noeuds_existants.append(nouveau)
            ajoutes += 1
            
    # On trie par order pour garder un arbre propre
    noeuds_existants.sort(key=lambda x: x.get("order", 0))
    
    chemin.write_text(json.dumps(noeuds_existants, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Succès : {ajoutes} nouveaux nœuds ajoutés à nodes.json.")
    print(f"Total de nœuds dans l'arbre : {len(noeuds_existants)}")

if __name__ == "__main__":
    fusionner()