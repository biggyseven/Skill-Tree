"""Contenu de démonstration : arbre réseau, quiz, examens et labs."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"


class ExportError(Exception):
    """Export refusé (contenu existant sans --force)."""


# (énoncé, choix, index de la bonne réponse, explication)
QuestionData = tuple[str, list[str], int, str]

NODES: list[dict] = [
    {
        "id": "osi",
        "title": "Modèle OSI & TCP/IP",
        "category": "Fondamentaux",
        "order": 10,
        "description": "Les 7 couches OSI, les 4 couches TCP/IP et l'encapsulation.",
        "prereqs": [],
        "requirements": [("quiz", 80)],
    },
    {
        "id": "tcp-udp",
        "title": "TCP, UDP & ports",
        "category": "Fondamentaux",
        "order": 20,
        "description": "Fiabilité, fenêtrage, multiplexage par ports.",
        "prereqs": ["osi"],
        "requirements": [("quiz", 80)],
    },
    {
        "id": "ethernet",
        "title": "Ethernet & couche 2",
        "category": "Couche 2 — Commutation",
        "order": 30,
        "description": "Trames, adressage MAC et apprentissage du switch.",
        "prereqs": ["osi"],
        "requirements": [("quiz", 80)],
    },
    {
        "id": "vlan",
        "title": "VLAN & trunking 802.1Q",
        "category": "Couche 2 — Commutation",
        "order": 40,
        "description": "Segmentation logique, ports access/trunk, VLAN natif.",
        "prereqs": ["ethernet"],
        "requirements": [("quiz", 80), ("lab", 100)],
    },
    {
        "id": "stp",
        "title": "STP / RSTP",
        "category": "Couche 2 — Commutation",
        "order": 50,
        "description": "Élection du pont racine, états des ports, convergence.",
        "prereqs": ["vlan"],
        "requirements": [("quiz", 80)],
    },
    {
        "id": "ipv4",
        "title": "Adressage IPv4 & sous-réseaux",
        "category": "Couche 3 — Adressage",
        "order": 60,
        "description": "Masques, découpage en sous-réseaux, adresses privées.",
        "prereqs": ["osi"],
        "requirements": [("quiz", 80), ("lab", 100)],
    },
    {
        "id": "arp",
        "title": "ARP & résolution L2/L3",
        "category": "Couche 3 — Adressage",
        "order": 70,
        "description": "Correspondance IP/MAC, cache ARP, proxy ARP.",
        "prereqs": ["ethernet", "ipv4"],
        "requirements": [("quiz", 80)],
    },
    {
        "id": "ipv6",
        "title": "IPv6 & NDP",
        "category": "Couche 3 — Adressage",
        "order": 80,
        "description": "Format, préfixes, link-local, SLAAC et Neighbor Discovery.",
        "prereqs": ["ipv4"],
        "requirements": [("quiz", 80), ("exam", 85)],
    },
    {
        "id": "nat",
        "title": "NAT & PAT",
        "category": "Couche 3 — Adressage",
        "order": 90,
        "description": "Traduction statique, dynamique et surcharge de ports.",
        "prereqs": ["ipv4"],
        "requirements": [("quiz", 80), ("lab", 100)],
    },
    {
        "id": "routing",
        "title": "Routage statique & tables",
        "category": "Routage",
        "order": 100,
        "description": "Table de routage, next-hop, route par défaut.",
        "prereqs": ["ipv4"],
        "requirements": [("quiz", 80), ("lab", 100)],
    },
    {
        "id": "ospf",
        "title": "OSPF",
        "category": "Routage",
        "order": 110,
        "description": "Voisinage, LSDB, coût, areas et LSA.",
        "prereqs": ["routing"],
        "requirements": [("quiz", 80), ("lab", 100)],
    },
    {
        "id": "bgp",
        "title": "BGP",
        "category": "Routage",
        "order": 120,
        "description": "Sessions eBGP/iBGP, AS_PATH et sélection de route.",
        "prereqs": ["ospf"],
        "requirements": [("quiz", 85), ("exam", 85)],
    },
    {
        "id": "dhcp-dns",
        "title": "DHCP & DNS",
        "category": "Services",
        "order": 130,
        "description": "Bail DHCP, résolution de noms et enregistrements.",
        "prereqs": ["ipv4"],
        "requirements": [("quiz", 80)],
    },
    {
        "id": "acl",
        "title": "ACL & filtrage",
        "category": "Sécurité",
        "order": 140,
        "description": "ACL standard/étendue, placement et deny implicite.",
        "prereqs": ["routing"],
        "requirements": [("quiz", 80), ("lab", 100)],
    },
    {
        "id": "troubleshooting",
        "title": "Méthodologie de dépannage",
        "category": "Exploitation",
        "order": 150,
        "description": "Diagnostic structuré, outils et preuve d'un incident réel.",
        "prereqs": ["arp", "dhcp-dns", "routing"],
        "requirements": [("quiz", 85), ("manual", 100)],
    },
]

LABS: dict[str, dict] = {
    "vlan": {
        "mode": "contains",
        "pattern": "switchport mode trunk",
        "prompt": "Configure l'interface Gi0/1 en trunk 802.1Q (commande Cisco).",
        "hint": "interface Gi0/1 puis switchport mode ...",
    },
    "ipv4": {
        "mode": "exact",
        "pattern": "62",
        "prompt": "Combien d'hôtes utilisables dans le réseau 192.168.10.0/26 ?",
        "hint": "2^(32-26) - 2",
    },
    "nat": {
        "mode": "regex",
        "pattern": r"ip\s+nat\s+inside\s+source\s+list\s+10\s+interface\s+\S+\s+overload",
        "prompt": "Écris la commande de surcharge NAT pour la liste 10 sur l'interface WAN.",
        "hint": "ip nat inside source list <id> interface <if> overload",
    },
    "routing": {
        "mode": "regex",
        "pattern": r"ip\s+route\s+0\.0\.0\.0\s+0\.0\.0\.0\s+192\.168\.1\.1",
        "prompt": "Écris la route statique par défaut via 192.168.1.1 (Cisco).",
        "hint": "ip route 0.0.0.0 0.0.0.0 <next-hop>",
    },
    "ospf": {
        "mode": "regex",
        "pattern": r"network\s+10\.0\.0\.0\s+0\.0\.0\.255\s+area\s+0",
        "prompt": "Annonce le réseau 10.0.0.0/24 dans l'area 0 (Cisco).",
        "hint": "network <réseau> <wildcard> area <id>",
    },
    "acl": {
        "mode": "all",
        "pattern": [
            r"access-list\s+100\s+deny\s+tcp\s+192\.168\.2\.0\s+0\.0\.0\.255"
            r"\s+host\s+10\.0\.0\.1\s+eq\s+22",
            r"access-list\s+100\s+permit\s+ip\s+any\s+any",
        ],
        "prompt": "ACL 100 : refuse SSH (22) de 192.168.2.0/24 vers 10.0.0.1, autorise le reste.",
        "hint": "deux lignes : deny tcp ... eq 22, puis permit ip any any",
    },
}

QUIZ: dict[str, list[QuestionData]] = {
    "osi": [
        (
            "À quelle couche OSI appartient le protocole IP ?",
            ["Transport", "Réseau", "Liaison de données", "Session"],
            1,
            "IP est un protocole de couche 3 : il achemine les paquets entre réseaux.",
        ),
        (
            "Quel est le bon ordre d'encapsulation à l'émission ?",
            [
                "Données → segment → paquet → trame → bits",
                "Données → paquet → segment → trame → bits",
                "Données → trame → paquet → segment → bits",
                "Données → segment → trame → paquet → bits",
            ],
            0,
            "Transport (segment), réseau (paquet), liaison (trame), physique (bits).",
        ),
        (
            "Combien de couches compte le modèle TCP/IP ?",
            ["2", "4", "5", "7"],
            1,
            "Accès réseau, Internet, transport, application.",
        ),
    ],
    "tcp-udp": [
        (
            "Quel protocole garantit la retransmission des segments perdus ?",
            ["TCP", "UDP", "ICMP", "ARP"],
            0,
            "TCP acquitte et retransmet ; UDP n'offre aucune garantie.",
        ),
        (
            "Quel port TCP est utilisé par HTTPS ?",
            ["21", "53", "80", "443"],
            3,
            "HTTPS = HTTP sur TLS, port 443.",
        ),
        (
            "Quel mécanisme TCP adapte le débit à la congestion du réseau ?",
            ["La fenêtre de congestion", "Le TTL", "La fragmentation IP", "Le NAT"],
            0,
            "La fenêtre de congestion (slow start, AIMD) régule le débit.",
        ),
    ],
    "ethernet": [
        (
            "Quelle est la taille minimale d'une trame Ethernet sans VLAN ?",
            ["46 octets", "64 octets", "128 octets", "1518 octets"],
            1,
            "64 octets au total, FCS inclus.",
        ),
        (
            "À quoi sert l'adresse MAC ?",
            [
                "Identifier une interface sur le segment local",
                "Router les paquets entre réseaux",
                "Résoudre un nom de domaine",
                "Chiffrer les flux",
            ],
            0,
            "La MAC identifie une interface sur le domaine de commutation.",
        ),
        (
            "Que fait un switch quand la MAC de destination est absente de sa table ?",
            ["Il inonde le VLAN", "Il jette la trame", "Il envoie un ARP", "Il désactive le port"],
            0,
            "Comportement unknown unicast : diffusion dans tout le VLAN.",
        ),
    ],
    "vlan": [
        (
            "Que fait l'étiquette 802.1Q ?",
            [
                "Elle ajoute 4 octets identifiant le VLAN",
                "Elle chiffre la trame",
                "Elle change l'adresse MAC",
                "Elle compresse les données",
            ],
            0,
            "Le tag 802.1Q ajoute 4 octets, dont 12 bits de VLAN ID.",
        ),
        (
            "Quel mode de port transporte plusieurs VLAN ?",
            ["Access", "Trunk", "Routed", "Monitor"],
            1,
            "Un trunk transporte les trames taguées de plusieurs VLAN.",
        ),
        (
            "Quel VLAN est natif par défaut sur un trunk Cisco ?",
            ["VLAN 0", "VLAN 1", "VLAN 100", "VLAN 4095"],
            1,
            "Le VLAN 1 est natif par défaut, donc non tagué sur le trunk.",
        ),
    ],
    "stp": [
        (
            "Quel problème le STP évite-t-il ?",
            ["Les boucles de commutation", "Les collisions IP", "Les attaques ARP", "La fragmentation"],
            0,
            "Sans STP, une boucle L2 provoque une tempête de broadcast.",
        ),
        (
            "Comment est élu le pont racine ?",
            ["Bridge ID le plus faible", "Bridge ID le plus élevé", "Port le plus rapide", "Premier switch démarré"],
            0,
            "Priorité puis adresse MAC la plus basse départagent les Bridge ID.",
        ),
        (
            "En RSTP, quel état regroupe blocking et listening ?",
            ["Discarding", "Learning", "Forwarding", "Blocking"],
            0,
            "RSTP ne conserve que discarding, learning et forwarding.",
        ),
    ],
    "ipv4": [
        (
            "Combien d'hôtes utilisables dans un /26 ?",
            ["30", "62", "64", "126"],
            1,
            "2^6 - 2 = 62 adresses utilisables.",
        ),
        (
            "Quelle est l'adresse réseau de 192.168.10.130/25 ?",
            ["192.168.10.0", "192.168.10.128", "192.168.10.129", "192.168.10.192"],
            1,
            "Un /25 coupe le dernier octet en deux : 128 est l'adresse réseau.",
        ),
        (
            "Quelle plage est privée au sens RFC 1918 ?",
            ["172.16.0.0/12", "172.32.0.0/12", "192.168.0.0/8", "10.0.0.0/16"],
            0,
            "Les plages privées sont 10/8, 172.16/12 et 192.168/16.",
        ),
    ],
    "arp": [
        (
            "Que résout ARP ?",
            ["Une IP vers une MAC", "Une MAC vers une IP", "Un nom vers une IP", "Un port vers un service"],
            0,
            "ARP trouve la MAC associée à une IPv4 sur le segment local.",
        ),
        (
            "Quel message ARP est envoyé en broadcast ?",
            ["La requête", "La réponse", "Les deux", "Aucun"],
            0,
            "La requête part en broadcast, la réponse est unicast.",
        ),
        (
            "À quoi sert le proxy ARP ?",
            [
                "Répondre aux ARP à la place d'un autre réseau",
                "Chiffrer les requêtes ARP",
                "Accélérer le spanning tree",
                "Attribuer des adresses IP",
            ],
            0,
            "Le routeur répond avec sa propre MAC pour joindre un réseau distant.",
        ),
    ],
    "ipv6": [
        (
            "Quelle est la taille d'une adresse IPv6 ?",
            ["32 bits", "64 bits", "128 bits", "256 bits"],
            2,
            "IPv6 utilise 128 bits, soit 8 groupes de 16 bits.",
        ),
        (
            "Quel préfixe est utilisé pour les adresses lien-local ?",
            ["fc00::/7", "fe80::/10", "2000::/3", "ff00::/8"],
            1,
            "Les adresses link-local sont dans fe80::/10.",
        ),
        (
            "Quel protocole remplace ARP en IPv6 ?",
            ["NDP", "DHCPv6", "ICMPv6 Redirect", "SLAAC"],
            0,
            "Neighbor Discovery Protocol, transporté par ICMPv6.",
        ),
    ],
    "nat": [
        (
            "Qu'est-ce que le NAT surchargé (PAT) utilise pour distinguer les flux ?",
            ["Le port source", "L'adresse MAC", "Le TTL", "Le DSCP"],
            0,
            "PAT multiplexe les flux traduits grâce au port source.",
        ),
        (
            "Quelle commande Cisco active la surcharge NAT ?",
            [
                "ip nat inside source list 10 interface Gi0/0 overload",
                "ip nat pool overload",
                "ip nat outside source overload",
                "ip nat inside destination overload",
            ],
            0,
            "La forme « source list ... interface ... overload » active le PAT.",
        ),
        (
            "Quel NAT conserve une correspondance 1:1 permanente ?",
            ["NAT statique", "NAT dynamique", "PAT", "NAT64"],
            0,
            "Le NAT statique mappe une adresse privée vers une adresse publique fixe.",
        ),
    ],
    "routing": [
        (
            "Quelle route représente la route par défaut ?",
            ["0.0.0.0/0", "255.255.255.255/32", "127.0.0.0/8", "10.0.0.0/8"],
            0,
            "0.0.0.0/0 correspond à tous les préfixes et sert de dernier recours.",
        ),
        (
            "Que fait un routeur sans route correspondante ?",
            [
                "Il jette le paquet et renvoie un ICMP unreachable",
                "Il inonde tous les ports",
                "Il envoie un ARP",
                "Il applique le NAT",
            ],
            0,
            "Sans route, le paquet est abandonné et une ICMP est renvoyée.",
        ),
        (
            "Quelle est la distance administrative d'une route statique ?",
            ["0", "1", "90", "110"],
            1,
            "La route statique a une distance administrative de 1.",
        ),
    ],
    "ospf": [
        (
            "Quel est le coût OSPF par défaut d'un lien 1 Gb/s ?",
            ["1", "10", "100", "1000"],
            0,
            "Coût = 100 Mb/s / 1 Gb/s, borné à 1 par défaut.",
        ),
        (
            "Quel LSA annonce les routes externes ?",
            ["Type 1", "Type 2", "Type 3", "Type 5"],
            3,
            "Les LSA de type 5 propagent les routes externes.",
        ),
        (
            "Quel état de voisinage indique que les LSDB sont synchronisées ?",
            ["Init", "2-Way", "Exchange", "Full"],
            3,
            "L'état Full signifie que les bases topologiques sont identiques.",
        ),
    ],
    "bgp": [
        (
            "BGP est un protocole de quel type ?",
            ["Vecteur de distance", "Vecteur de chemin", "État de liens", "Hybride"],
            1,
            "BGP est un path-vector : il transporte la liste des AS traversés.",
        ),
        (
            "Quel port TCP BGP utilise-t-il ?",
            ["22", "89", "179", "443"],
            2,
            "Les sessions BGP s'établissent sur TCP 179.",
        ),
        (
            "Quel attribut BGP est évalué en premier chez Cisco ?",
            ["Weight", "Local Preference", "AS_PATH", "MED"],
            0,
            "Cisco évalue d'abord le Weight, puis Local Preference, AS_PATH, etc.",
        ),
    ],
    "dhcp-dns": [
        (
            "Quel message DHCP confirme l'attribution d'une adresse ?",
            ["DHCPDISCOVER", "DHCPOFFER", "DHCPREQUEST", "DHCPACK"],
            3,
            "Le serveur valide le bail avec DHCPACK.",
        ),
        (
            "Quel enregistrement DNS associe un nom à une IPv4 ?",
            ["AAAA", "A", "CNAME", "MX"],
            1,
            "L'enregistrement A pointe un nom vers une IPv4 ; AAAA pour IPv6.",
        ),
        (
            "Quel port utilise DNS en UDP classique ?",
            ["22", "53", "67", "123"],
            1,
            "DNS utilise le port 53, en UDP pour les requêtes courantes.",
        ),
    ],
    "acl": [
        (
            "Que filtre une ACL standard Cisco ?",
            [
                "L'IP source uniquement",
                "IP source et destination",
                "Les ports",
                "Les adresses MAC",
            ],
            0,
            "Une ACL standard ne peut matcher que l'adresse source.",
        ),
        (
            "Où placer une ACL étendue ?",
            [
                "Au plus près de la source",
                "Au plus près de la destination",
                "Sur le routeur de sortie uniquement",
                "Sur tous les switchs",
            ],
            0,
            "On filtre tôt pour éviter de transporter du trafic destiné à être jeté.",
        ),
        (
            "Que contient implicitement toute ACL Cisco à la fin ?",
            ["deny any", "permit any", "deny ip any any", "permit ip any any"],
            2,
            "Un deny ip any any implicite termine chaque ACL.",
        ),
    ],
    "troubleshooting": [
        (
            "Quelle est la première étape d'un dépannage structuré ?",
            [
                "Définir le problème et son impact",
                "Redémarrer les équipements",
                "Changer le câble",
                "Appeler l'opérateur",
            ],
            0,
            "On qualifie le symptôme, le périmètre et l'impact avant d'agir.",
        ),
        (
            "Quel outil teste la joignabilité de couche 3 ?",
            ["ping", "arp", "netstat", "tcpdump"],
            0,
            "ping envoie des ICMP Echo Request et mesure le RTT.",
        ),
        (
            "Quel outil montre le chemin et les pertes par saut ?",
            ["traceroute", "dig", "ss", "nslookup"],
            0,
            "traceroute révèle les routeurs traversés et les pertes par saut.",
        ),
    ],
}

EXAM: dict[str, list[QuestionData]] = {
    "ipv6": [
        (
            "Quel type d'adresse remplace le broadcast IPv4 en IPv6 ?",
            ["Unicast global", "Multicast", "Anycast", "Lien-local"],
            1,
            "IPv6 n'a pas de broadcast : le multicast ff02::1 joue ce rôle.",
        ),
        (
            "Que fait SLAAC ?",
            [
                "Il configure l'adresse à partir du préfixe annoncé par le routeur",
                "Il attribue une IP depuis un serveur central",
                "Il traduit les adresses",
                "Il signe les Router Advertisements",
            ],
            0,
            "SLAAC combine le préfixe des RA et un identifiant d'interface.",
        ),
        (
            "Quelle est la taille de l'en-tête IPv6 de base ?",
            ["20 octets", "32 octets", "40 octets", "60 octets"],
            2,
            "L'en-tête IPv6 fixe fait 40 octets, extensible par en-têtes optionnels.",
        ),
    ],
    "bgp": [
        (
            "Quel attribut BGP prévient les boucles entre AS ?",
            ["AS_PATH", "MED", "Next-hop", "Origin"],
            0,
            "Un routeur rejette une route dont l'AS_PATH contient son propre AS.",
        ),
        (
            "Quelle session BGP s'établit entre deux AS différents ?",
            ["iBGP", "eBGP", "iBGP confederation", "Route reflector"],
            1,
            "eBGP relie des routeurs appartenant à des AS distincts.",
        ),
        (
            "À quoi sert un route reflector ?",
            [
                "À relayer les routes iBGP sans maillage complet",
                "À convertir BGP en OSPF",
                "À filtrer les MAC",
                "À faire du NAT",
            ],
            0,
            "Le RR réfléchit les routes vers ses clients iBGP.",
        ),
    ],
}


def seed(conn: sqlite3.Connection) -> None:
    """Charge le contenu de démonstration dans une base vide."""
    for node in NODES:
        conn.execute(
            "INSERT INTO nodes (id, title, description, category, sort_order)"
            " VALUES (?, ?, ?, ?, ?)",
            (node["id"], node["title"], node["description"], node["category"], node["order"]),
        )
        for prereq in node["prereqs"]:
            conn.execute(
                "INSERT INTO edges (node_id, prereq_id) VALUES (?, ?)",
                (node["id"], prereq),
            )
        for kind, min_score in node["requirements"]:
            conn.execute(
                "INSERT INTO requirements (node_id, kind, min_score) VALUES (?, ?, ?)",
                (node["id"], kind, min_score),
            )

    for node_id, lab in LABS.items():
        pattern = lab["pattern"]
        if isinstance(pattern, list):
            pattern = json.dumps(pattern)
        conn.execute(
            "INSERT INTO lab_specs (node_id, mode, pattern, prompt, hint) VALUES (?, ?, ?, ?, ?)",
            (node_id, lab["mode"], pattern, lab["prompt"], lab["hint"]),
        )

    for scope, bank in (("quiz", QUIZ), ("exam", EXAM)):
        for node_id, questions in bank.items():
            for position, (prompt, choices, answer, explanation) in enumerate(questions):
                conn.execute(
                    "INSERT INTO questions (node_id, scope, prompt, choices, answer, explanation, position)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (node_id, scope, prompt, json.dumps(choices, ensure_ascii=False), answer, explanation, position),
                )

    conn.commit()


@dataclass(frozen=True)
class ExportReport:
    directory: Path
    nodes: int
    quiz_files: int
    exam_files: int
    lab_files: int
    quiz_questions: int
    exam_questions: int


def _write_json(path: Path, payload) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def _question_payload(question: QuestionData) -> dict:
    prompt, choices, answer, explanation = question
    return {
        "prompt": prompt,
        "choices": list(choices),
        "answer": answer,
        "explanation": explanation,
    }


def export_content(directory: str | Path = CONTENT_DIR, force: bool = False) -> ExportReport:
    """Génère content/ à partir des constantes intégrées (source initiale du contenu).

    Refuse d'écraser un content/ existant sans force=True.
    """
    directory = Path(directory)
    if (directory / "nodes.json").exists() and not force:
        raise ExportError("content/ existe déjà. Utilise --force pour l'écraser depuis seed.py.")

    quiz_dir = directory / "quiz"
    exam_dir = directory / "exam"
    labs_dir = directory / "labs"
    for folder in (directory, quiz_dir, exam_dir, labs_dir):
        folder.mkdir(parents=True, exist_ok=True)

    for folder in (quiz_dir, exam_dir, labs_dir):
        for stale in folder.glob("*.json"):
            stale.unlink()

    _write_json(
        directory / "nodes.json",
        [
            {
                "id": node["id"],
                "title": node["title"],
                "category": node["category"],
                "order": node["order"],
                "description": node["description"],
                "prereqs": list(node["prereqs"]),
                "requirements": [
                    {"kind": kind, "min_score": min_score}
                    for kind, min_score in node["requirements"]
                ],
            }
            for node in NODES
        ],
    )

    for node_id, questions in QUIZ.items():
        _write_json(
            quiz_dir / f"{node_id}.json",
            {
                "node_id": node_id,
                "scope": "quiz",
                "questions": [_question_payload(question) for question in questions],
            },
        )

    for node_id, questions in EXAM.items():
        _write_json(
            exam_dir / f"{node_id}.json",
            {
                "node_id": node_id,
                "scope": "exam",
                "questions": [_question_payload(question) for question in questions],
            },
        )

    for node_id, lab in LABS.items():
        _write_json(
            labs_dir / f"{node_id}.json",
            {
                "node_id": node_id,
                "mode": lab["mode"],
                "pattern": lab["pattern"],
                "prompt": lab["prompt"],
                "hint": lab["hint"],
            },
        )

    return ExportReport(
        directory=directory,
        nodes=len(NODES),
        quiz_files=len(QUIZ),
        exam_files=len(EXAM),
        lab_files=len(LABS),
        quiz_questions=sum(len(questions) for questions in QUIZ.values()),
        exam_questions=sum(len(questions) for questions in EXAM.values()),
    )
