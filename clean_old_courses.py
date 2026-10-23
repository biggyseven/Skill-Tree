import os

LESSON_DIR = "content/lessons"

# Liste des anciens fichiers à supprimer
old_files = [
    "intro-reseau", "materiel-reseau", "cabling", "equipment", "osi",
    "tcp-udp", "poe", "ethernet", "wifi", "etherchannel", "vtp",
    "ipv4", "adressage-debutant", "arp", "nat", "routing",
    "ntp-syslog", "acl", "firewall", "vpn", "aaa", "troubleshooting", "cloud",
    "cisco-aci", "spine-leaf", "ddos-mitigation", "ids-ips", "ipsec", "radius",
    "wireguard", "pki", "wireshark", "itil-rca", "mtu-pmtud", "wireshark-advanced",
    "netmiko", "restconf", "napalm", "cicd-network", "netconf-yang", "terraform",
    "automation", "aws-vpc", "azure-vnet", "bgp", "bgp-advanced", "dhcp-dns",
    "dns-advanced", "eigrp", "evpn", "ha", "ipv6", "layer2-security", "mpls",
    "multicast", "ospf", "ospf-advanced", "qos", "qos-advanced", "sd-wan", "sdwan",
    "segment-routing", "stp", "vlan", "vrf", "vxlan", "zero-trust", "zero-trust-architecture"
]

print("🧹 Suppression des anciens cours...\n")
for file in old_files:
    path = os.path.join(LESSON_DIR, f"{file}.md")
    if os.path.exists(path):
        os.remove(path)
        print(f"🗑️ Supprimé : {file}.md")

print("\n✅ Nettoyage terminé !")