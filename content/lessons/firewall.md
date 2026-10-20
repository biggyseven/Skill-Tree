# Pare-feu et NGFW — stateful, zones, NAT et inspection

> **Objectif** : concevoir et diagnostiquer un filtrage réseau moderne. Comprendre la différence entre packet filter, firewall stateful, zones de sécurité et NGFW, maîtriser NAT/conntrack, et savoir écrire des règles Linux et Cisco.

---

## 1. Du filtre de paquets au NGFW

Un pare-feu est un point de contrôle qui applique une politique de sécurité entre des réseaux de confiance différente. La première génération filtrait des paquets selon IP, protocole et port. Les firewalls modernes suivent les connexions, comprennent les applications, inspectent le contenu et s'intègrent à des systèmes de détection.

| Génération | Principe | Limite |
|---|---|---|
| Packet filter | Règles stateless sur en-têtes | Ne comprend pas le retour des connexions |
| Stateful | Table de connexions | Ne voit pas le contenu applicatif |
| Proxy | Terminaison applicative | Coût et complexité |
| NGFW | DPI, IPS, applications, utilisateurs | Performance et faux positifs |

Un firewall n'est pas un routeur avec une ACL : c'est un équipement de politique, de journalisation et souvent de traduction d'adresses.

---

## 2. Stateful vs stateless

### 2.1 Stateless

Une ACL stateless évalue chaque paquet indépendamment. Pour autoriser un client vers un serveur web, il faut penser au retour :

```text
Autoriser 10.10.1.0/24 -> 10.10.2.10:80
Autoriser 10.10.2.10:80 -> 10.10.1.0/24 (ports hauts)
```

Si l'on oublie la seconde règle, la connexion ne s'établit pas. Les ACL Cisco sont généralement stateless, sauf fonction `reflexive` ou `established`.

### 2.2 Stateful

Un firewall stateful crée une entrée dans une table de connexions au premier paquet. Le retour est automatiquement autorisé s'il appartient à une connexion connue.

```text
Client                          Firewall                         Serveur
  |--- SYN ----------------------->|                                 |
  |                               | crée NEW                        |
  |                               |--- SYN ------------------------>|
  |                               |<-- SYN-ACK ---------------------|
  |<-- SYN-ACK -------------------| ESTABLISHED                     |
  |--- ACK ----------------------->|                                 |
  |--- GET / --------------------->| ESTABLISHED                     |
```

États usuels :

| État | Signification |
|---|---|
| `NEW` | Premier paquet d'une connexion |
| `ESTABLISHED` | Connexion vue dans les deux sens |
| `RELATED` | Connexion liée à une autre (FTP, ICMP d'erreur) |
| `INVALID` | Paquet incohérent ou hors connexion |
| `UNTRACKED` | Paquet exclu du suivi |

### 2.3 TCP et suivi de connexion

Le firewall ne voit pas seulement des ports : il suit les flags TCP. Un `SYN` sans réponse, un `ACK` orphelin ou un `FIN` hors séquence peuvent être classés `INVALID`. Les timeouts varient selon le protocole : TCP établi, UDP, ICMP.

```text
NEW        : SYN
ESTABLISHED: SYN-ACK, ACK, données
RELATED    : ICMP fragmentation needed, FTP data
INVALID    : ACK sans connexion, checksum invalide
```

### 2.4 UDP et ICMP

UDP n'a pas de handshake. Le firewall crée une entrée au premier paquet et autorise le retour pendant un timeout court. ICMP est suivi par type et identifiant ; les erreurs ICMP peuvent être `RELATED` à une connexion TCP/UDP.

---

## 3. Zones de sécurité

Une zone regroupe des interfaces ayant le même niveau de confiance. La politique s'exprime entre zones, pas seulement entre adresses.

```text
        +---------------------+
        |      Internet       |
        |      zone OUT       |
        +----------+----------+
                   |
              +----v----+
              | Firewall|
              +----+----+
                   |
        +----------+----------+
        |                     |
+-------v-------+     +-------v-------+
|     DMZ       |     |   INSIDE      |
| serveurs web  |     | utilisateurs  |
+---------------+     +---------------+
```

| Zone | Confiance | Exemple de politique |
|---|---|---|
| Inside | Élevée | Accès Internet, DMZ limitée |
| DMZ | Moyenne | Entrants HTTP/HTTPS, sortants contrôlés |
| Outside | Faible | Refus par défaut, réponses établies |
| Management | Très élevée | SSH/HTTPS depuis bastion uniquement |

### 3.1 Matrice de flux

| Source | Destination | Service | Action |
|---|---|---|---|
| Inside | Outside | HTTP/HTTPS | Autoriser |
| Inside | DMZ | HTTP/HTTPS | Autoriser |
| Outside | DMZ | HTTP/HTTPS | Autoriser |
| Outside | Inside | Tout | Refuser |
| DMZ | Inside | Tout | Refuser |
| Management | Tous | SSH/HTTPS | Autoriser depuis bastion |

Une matrice de flux est un document de conception, pas une simple collection de règles. Elle doit être revue à chaque nouveau service.

### 3.2 Zones et routage

Un firewall peut être en mode routé (une interface par réseau) ou en mode transparent (bridge). En mode routé, il faut penser aux routes de retour, au NAT et au routage asymétrique. En mode transparent, il filtre sans changer les adresses, mais reste un point de panne.

### 3.3 Asymmetric routing

Si l'aller passe par un firewall et le retour par un autre, le stateful voit des paquets `INVALID` ou hors connexion. Les solutions : symétrie de routage, clustering actif/actif avec synchronisation, ou filtrage stateless pour certains flux.

---

## 4. NAT et firewall

NAT et filtrage sont souvent configurés ensemble, mais ce sont deux fonctions distinctes. Le NAT traduit des adresses ; le firewall décide ce qui passe.

### 4.1 Types de NAT

| Type | Direction | Exemple |
|---|---|---|
| SNAT | Sortant | Masquer le LAN derrière l'IP publique |
| DNAT | Entrant | Publier un serveur DMZ |
| PAT | Sortant/entrant | Plusieurs hôtes derrière un port |
| Hairpin | Interne vers externe | Accès au service public depuis le LAN |
| NAT64 | IPv6 vers IPv4 | Transition |

### 4.2 Ordre des opérations

Selon la plateforme, le NAT peut être appliqué avant ou après le filtrage. Il faut connaître cet ordre pour écrire des règles cohérentes.

```text
Paquet entrant
  -> routage
  -> DNAT éventuel
  -> filtrage
  -> routage final
  -> SNAT éventuel
  -> sortie
```

Sur Linux, les chaînes `PREROUTING`, `FORWARD` et `POSTROUTING` matérialisent ces étapes. Sur Cisco ASA, les règles NAT et ACL ont leur propre ordre ; un `deny` peut s'appliquer à l'adresse traduite ou réelle selon la configuration.

### 4.3 DNAT et sécurité

Publier un service ne signifie pas l'ouvrir à tous. Une DNAT doit être associée à une ACL et à une politique applicative. Un serveur DMZ compromis ne doit pas pouvoir atteindre directement le LAN.

### 4.4 NAT et journaux

Avec NAT, les logs doivent indiquer l'adresse source réelle et traduite. Sans cette corrélation, une enquête est impossible. Les équipements doivent envoyer leurs logs à un collecteur synchronisé en NTP.

---

## 5. NGFW : inspection et applications

Un NGFW (Next-Generation Firewall) ajoute :

- identification des applications (au-delà du port) ;
- inspection profonde des paquets (DPI) ;
- prévention d'intrusion (IPS) ;
- filtrage URL et réputation ;
- inspection TLS ;
- contrôle utilisateur et posture ;
- sandboxing et threat intelligence.

### 5.1 DPI et IPS

Le DPI analyse les payloads à la recherche de signatures, de protocoles anormaux ou de malwares. L'IPS peut bloquer, l'IDS alerte seulement.

| Mode | Action | Risque |
|---|---|---|
| IDS | Alerte | Aucun blocage, plus sûr pour tester |
| IPS | Bloque | Faux positifs possibles |
| Tap | Copie passivement | Pas dans le chemin |

Une signature doit être révisée : un faux positif peut couper une application métier. On commence souvent en mode détection, on mesure, puis on active le blocage.

### 5.2 Inspection TLS

Le firewall peut déchiffrer et réchiffrer le trafic pour l'inspecter. Cela nécessite une autorité de certification interne et une gestion rigoureuse des certificats. Les applications avec épinglage de certificat peuvent casser. Il faut exclure les flux sensibles ou réglementés et documenter la politique.

### 5.3 Filtrage applicatif

Bloquer le port 443 ne bloque pas « le web » : il faut identifier l'application, l'utilisateur, la catégorie et le contexte. Les politiques modernes combinent :

- source/destination ;
- utilisateur/groupe (via annuaire) ;
- application ;
- URL/catégorie ;
- profil de menace ;
- horaire.

### 5.4 Performance

L'inspection coûte du CPU et de la latence. On dimensionne le débit avec inspection activée, pas seulement le débit brut. Les fonctions de sûreté (IPS, anti-malware, TLS) ont souvent un débit maximal inférieur au forwarding.

---

## 6. Haute disponibilité

Un firewall est un point de passage obligé : sa panne coupe le réseau. On déploie souvent :

- paire active/standby avec synchronisation d'état ;
- paire active/active avec répartition ;
- liens redondants et routage dynamique ;
- monitoring de session et bascule testée.

```text
        +----------+       +----------+
        | FW actif |=======| FW standby|
        +----+-----+       +-----+-----+
             |                   |
        réseau interne       réseau interne
```

La synchronisation doit inclure les sessions conntrack, les tables NAT et les états VPN. Une bascule sans synchronisation coupe les connexions établies.

---

## 7. Règles Linux avec iptables

### 7.1 Politique par défaut

```bash
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT
```

Une politique `DROP` par défaut est la base d'un filtrage sûr. On ajoute ensuite des règles explicites.

### 7.2 Stateful minimal

```bash
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -m conntrack --ctstate NEW -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -p tcp --dport 80 -m conntrack --ctstate NEW -j ACCEPT
```

### 7.3 Journalisation

```bash
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "INPUT-DROP: "
iptables -A INPUT -j DROP
```

Le `limit` évite d'inonder les logs. On journalise ce qui est refusé, pas chaque paquet.

### 7.4 NAT Linux

```bash
sysctl -w net.ipv4.ip_forward=1
iptables -t nat -A POSTROUTING -s 10.10.1.0/24 -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j DNAT --to-destination 10.10.2.10:80
iptables -A FORWARD -p tcp -d 10.10.2.10 --dport 80 -j ACCEPT
```

### 7.5 nftables

```nft
table inet filter {
  chain forward {
    type filter hook forward priority 0; policy drop;
    ct state established,related accept
    tcp dport 80 ct state new accept
  }
}
```

`nftables` remplace progressivement iptables, mais les concepts restent les mêmes : hooks, chaînes, politique, conntrack.

---

## 8. Cisco ASA et FTD

### 8.1 ASA : ACL et NAT

```cisco
object network WEB
 host 10.10.2.10
object service HTTP
 service tcp destination eq 80

nat (dmz,outside) static 203.0.113.10 service HTTP HTTP
access-list OUTSIDE-IN extended permit tcp any object WEB eq 80
access-group OUTSIDE-IN in interface outside
```

### 8.2 Vérifications ASA

```cisco
show access-list
show nat
show conn
show xlate
packet-tracer input outside tcp 198.51.100.10 12345 203.0.113.10 80 detailed
```

`packet-tracer` est l'outil clé : il simule le parcours d'un paquet et indique où il est accepté ou refusé.

### 8.3 FTD

Sur FTD, la politique est souvent gérée par FMC : règles ACP, pré-filtre, NAT, inspection. Les commandes CLI servent au diagnostic, mais la configuration est centralisée.

---

## 9. Méthode de dépannage

1. Identifier la source, la destination, le protocole et le port.
2. Vérifier le routage aller et retour.
3. Vérifier la politique de zone et l'ordre des règles.
4. Vérifier NAT et traductions.
5. Vérifier conntrack et les timeouts.
6. Capturer avant et après le firewall.
7. Lire les logs et les compteurs.

```bash
tcpdump -ni any host 10.10.2.10 and port 80
conntrack -L 2>/dev/null | grep 10.10.2.10
iptables -L -n -v
```

Un paquet qui arrive mais ne repart pas indique souvent un problème de route de retour. Un paquet qui n'arrive pas au firewall indique un problème de routage ou de lien. Un paquet qui arrive mais est bloqué indique une règle, un NAT ou un état conntrack.

---

## 10. Conception et bonnes pratiques

- politique de refus par défaut ;
- documentation de chaque flux et de son propriétaire ;
- séparation management / données ;
- DMZ pour les services exposés ;
- NAT explicite et journalisé ;
- IPS en détection avant blocage ;
- supervision des sessions et des logs ;
- tests de bascule HA ;
- revue périodique des règles ;
- protection contre l'usurpation et le spoofing.

Un firewall mal documenté devient une boîte noire. Une règle sans propriétaire ni date de revue est une dette de sécurité. On préfère des objets nommés, des commentaires et des politiques lisibles.

---

## 11. Cas pratique : zone-based firewall Cisco

Sur Cisco IOS, un firewall zoné applique une politique d'inspection entre zones. Contrairement à une ACL appliquée interface par interface, la politique décrit le flux entre une zone source et une zone destination.

```cisco
zone security INSIDE
zone security OUTSIDE
zone security DMZ

interface GigabitEthernet0/1
 description Utilisateurs
 zone-member security INSIDE
interface GigabitEthernet0/2
 description Internet
 zone-member security OUTSIDE
interface GigabitEthernet0/3
 description Serveurs exposes
 zone-member security DMZ

class-map type inspect match-any WEB-TRAFFIC
 match protocol http
 match protocol https

policy-map type inspect INSIDE-TO-OUTSIDE
 class type inspect WEB-TRAFFIC
  inspect
 class class-default
  drop log

zone-pair security INSIDE-TO-OUTSIDE source INSIDE destination OUTSIDE
 service-policy type inspect INSIDE-TO-OUTSIDE
```

Le mot-clé `inspect` crée un état pour le flux autorisé : le retour est permis sans écrire une ACL inverse. `drop log` journalise les refus. On crée une zone-pair par direction ; il n'existe pas de retour implicite entre zones si aucune politique n'est appliquée.

| Élément | Rôle |
|---|---|
| `zone security` | Déclare une zone de confiance |
| `zone-member security` | Rattache une interface à une zone |
| `class-map type inspect` | Sélectionne le trafic à inspecter |
| `policy-map type inspect` | Définit l'action (`inspect`, `pass`, `drop`) |
| `zone-pair` | Applique la politique entre deux zones |

Un piège classique consiste à appliquer une ACL sur l'interface physique plutôt qu'une politique de zone. Les deux mécanismes peuvent coexister, mais l'ordre et la lisibilité deviennent vite dangereux. On documente toujours la zone source, la zone destination et la direction.

## 12. Cas pratique : publication d'un service DMZ

Prenons un serveur web `10.10.2.10:443` publié sur `203.0.113.10:443`. Le flux entrant doit être autorisé, le retour aussi, mais le serveur ne doit pas initier de connexion vers le LAN.

```text
Internet ---> FW ---> DMZ web
                   |
                   +--X--> INSIDE (interdit)
```

La politique se lit ainsi :

1. DNAT de `203.0.113.10:443` vers `10.10.2.10:443`.
2. Autoriser `OUTSIDE -> DMZ` sur TCP 443 en `NEW`.
3. Autoriser le retour `DMZ -> OUTSIDE` en `ESTABLISHED,RELATED`.
4. Refuser `DMZ -> INSIDE` en `NEW`.
5. Autoriser éventuellement `DMZ -> Internet` pour les mises à jour, avec un proxy ou une liste blanche.

Le NAT seul ne protège pas : si l'on publie l'adresse sans ACL, le service est ouvert. À l'inverse, une ACL sans NAT peut autoriser un flux vers une adresse privée qui n'est pas routable depuis Internet. Il faut tester les deux côtés et vérifier les logs de traduction.

### 12.1 Timeouts et applications longues

Les timeouts par défaut ne conviennent pas à toutes les applications. Une session SSH inactive, une sauvegarde longue ou un flux UDP peut être coupé par le firewall. On ajuste les timeouts avec prudence et on surveille les sessions. Pour les applications qui utilisent plusieurs canaux, comme FTP, SIP ou certains protocoles de visioconférence, il faut un inspection applicative ou des règles `RELATED` adaptées.

### 12.2 Vérification de cohérence

| Test | Résultat attendu |
|---|---|
| `packet-tracer` depuis la zone externe | Dénaté, ACL autorisée, route correcte |
| `show conn` pendant le flux | Session établie avec les bonnes adresses |
| `show xlate` | Traduction active |
| Capture côté serveur | Adresse source traduite ou réelle selon le design |
| Log de refus | Flux non autorisé visible et qualifié |

## 13. Exercices

1. Écrire une politique stateful qui autorise HTTP et bloque ICMP.
2. Publier un serveur DMZ avec DNAT et vérifier le retour.
3. Configurer un firewall Linux avec politique DROP et journalisation.
4. Simuler un paquet avec `packet-tracer` sur ASA.
5. Diagnostiquer une connexion bloquée par un routage asymétrique.
6. Comparer les règles nécessaires en stateless et en stateful.
7. Mettre en place une inspection TLS et expliquer ses limites.
8. Concevoir une matrice de flux pour un site avec DMZ.
9. Vérifier les traductions NAT et les sessions actives.
10. Rédiger une procédure de revue trimestrielle des règles.
