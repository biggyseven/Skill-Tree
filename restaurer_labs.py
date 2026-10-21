import json
from pathlib import Path

labs = {
    "lab_acl": {"node_id": "acl", "timeout": 120, "prompt": "Bloque le ping entre les deux hôtes tout en autorisant le HTTP.", "hint": "Utilise iptables sur le routeur. HTTP = port 80, Ping = ICMP."},
    "lab_bridge": {"node_id": "lab_bridge", "timeout": 90, "prompt": "Attache les deux veths au bridge pour rétablir la connectivité L2.", "hint": "ip link set <if> master br-lab"},
    "lab_dhcp": {"node_id": "dhcp-dns", "timeout": 120, "prompt": "Le serveur DHCP/DNS dnsmasq tourne dans le namespace srv. Dans le namespace cli, obtiens une IP et résous un nom.", "hint": "Utilise dhclient ou udhcpc, puis dig."},
    "lab_dns_adv": {"node_id": "dns-advanced", "timeout": 120, "prompt": "Configure un serveur DNS local dans le namespace dns (10.80.0.53). La zone lab doit résoudre app.lab.", "hint": "Utilise dnsmasq avec host-record."},
    "lab_firewall": {"node_id": "firewall", "timeout": 120, "prompt": "Le routeur fw est en politique FORWARD DROP. Mets en place un firewall stateful avec conntrack.", "hint": "Autorise ESTABLISHED,RELATED et le port 80 en NEW."},
    "lab_ha": {"node_id": "ha", "timeout": 150, "prompt": "Configure un bond0 LACP (802.3ad) dans ns1 et ns2 avec les deux liens fournis, pose 10.10.0.1/24 et 10.10.0.2/24.", "hint": "ip link add bond0 type bond mode 802.3ad"},
    "lab_netns": {"node_id": "lab_netns", "timeout": 90, "prompt": "Configure l'adressage et les routes pour que ns-a et ns-b se joignent à travers ns-router.", "hint": "ip netns exec ns-router ip addr add... puis ip route add default..."},
    "lab_ospf": {"node_id": "ospf", "timeout": 120, "prompt": "Configure le routage entre r1 et r2 pour que h1 et h2 se joignent à travers le lien 10.255.0.0/30.", "hint": "ip netns exec r1 ip route add..."},
    "lab_troubleshoot_vlan": {"node_id": "lab_troubleshoot_vlan", "timeout": 120, "prompt": "Le ping entre ns1 et ns2 échoue. Trouve l'erreur de configuration VLAN sur le bridge.", "hint": "Compare les VLAN avec bridge vlan show."},
    "lab_tshoot_dns": {"node_id": "lab_tshoot_dns", "timeout": 120, "prompt": "Le client n'arrive pas à résoudre intranet.lab. Le serveur DNS 10.70.0.53 est mal configuré.", "hint": "Vérifie l'enregistrement A sur le serveur DNS."},
    "lab_tshoot_mtu": {"node_id": "lab_tshoot_mtu", "timeout": 120, "prompt": "Le ping passe depuis h1 vers h2, mais les gros paquets avec DF échouent : le MTU est trop petit sur le chemin.", "hint": "Trouve l'interface avec un MTU trop bas et corrige-le."},
    "lab_tshoot_route": {"node_id": "lab_tshoot_route", "timeout": 120, "prompt": "Deux réseaux ne communiquent pas. Le routeur r2 n'a pas de route pour renvoyer le trafic.", "hint": "Ajoute une route par défaut sur r2."}
}

for folder, data in labs.items():
    path = Path(f"content/labs/{folder}/lab.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    
    # On ajoute les champs communs
    full_data = {
        "kind": "docker",
        "image": "skilltree/lab:latest",
        **data
    }
    
    path.write_text(json.dumps(full_data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"✅ Recréé : {path}")

print("\nTous les lab.json ont été recréés avec succès.")