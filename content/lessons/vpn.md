# VPN et tunnels — IPsec, TLS, WireGuard et architectures

> **Objectif** : comprendre les VPN de bout en bout, choisir entre site-to-site et accès distant, configurer IPsec et WireGuard, diagnostiquer les problèmes d'IKE, de NAT, de routage et de MTU.

---

## 1. Qu'est-ce qu'un VPN ?

Un VPN (Virtual Private Network) crée un tunnel logique entre deux points sur un réseau non fiable. Il assure généralement trois propriétés :

- **confidentialité** : le contenu est chiffré ;
- **intégrité** : les modifications sont détectées ;
- **authentification** : les extrémités sont identifiées.

Un VPN ne remplace ni le filtrage, ni l'authentification applicative, ni la segmentation. Il déplace la frontière de confiance ; il ne la supprime pas.

```text
Site A                                                     Site B
+---------+        Internet (non fiable)        +---------+
| LAN A   |--- VPN gateway ============ gateway ---| LAN B   |
+---------+        tunnel chiffré                 +---------+
```

### 1.1 Site-to-site vs remote access

| Critère | Site-to-site | Remote access |
|---|---|---|
| Extrémités | Passerelles fixes | Utilisateur nomade |
| Authentification | PSK ou certificats | Utilisateur + certificat/MFA |
| Routage | Réseaux entiers | Adresse ou split tunnel |
| Client | Aucun sur les postes | Client VPN requis |
| Cas d'usage | Interconnexion de sites | Télétravail, mobilité |

### 1.2 Tunnel vs transport

En mode **tunnel**, tout le paquet IP original est encapsulé dans un nouveau paquet. En mode **transport**, seules les données de la couche supérieure sont protégées ; les adresses IP restent visibles. Le mode tunnel est le plus courant pour les VPN site-to-site.

### 1.3 Overlay et underlay

L'underlay est le réseau physique ou logique qui transporte le tunnel. L'overlay est le réseau privé construit au-dessus. Un problème de MTU, de routage ou de NAT dans l'underlay casse l'overlay même si la configuration VPN semble correcte.

---

## 2. IPsec : architecture

IPsec est une suite de protocoles qui sécurise IP au niveau réseau. Il combine :

- **IKE** pour négocier les paramètres et authentifier les pairs ;
- **AH** ou **ESP** pour protéger les paquets ;
- des bases de données de politiques et d'associations de sécurité (SPD/SAD).

```text
Pair A                                                   Pair B
  |--- IKE phase 1 : tunnel de management -------------->|
  |<-- échange de clés, authentification ---------------|
  |--- IKE phase 2 : IPsec SA ------------------------->|
  |<-- SPI, algorithmes, durée de vie ------------------|
  |--- ESP : données chiffrées ------------------------>|
```

### 2.1 IKEv1 et IKEv2

| Version | Caractéristiques |
|---|---|
| IKEv1 | Phase 1 (main/aggressive), phase 2 rapide ; encore présent sur du legacy |
| IKEv2 | Moins de messages, renégociation, mobilité, EAP, MOBIKE |

IKEv2 est recommandé. Le mode aggressive d'IKEv1 expose l'identité et doit être évité. Les propositions doivent être alignées des deux côtés : chiffrement, intégrité, groupe Diffie-Hellman, durée de vie.

### 2.2 AH vs ESP

| Protocole | Chiffrement | Intégrité | NAT |
|---|---|---|---|
| AH | Non | Oui, en-tête IP inclus | Incompatible avec NAT |
| ESP | Oui | Oui | Compatible avec NAT-T |

AH protège aussi l'en-tête IP, mais il est bloqué par le NAT car les adresses sont modifiées. ESP est utilisé dans la majorité des VPN. En mode transport, ESP protège la charge utile ; en mode tunnel, il encapsule tout le paquet.

### 2.3 Associations de sécurité

Une SA est un contrat unidirectionnel : SPI, algorithme, clés, durée de vie. Une communication IPsec utilise généralement deux SA, une par direction. Les SA expirent et sont renégociées ; une horloge dérivée ou une politique différente peut empêcher la renégociation.

### 2.4 NAT-T et détection de pair mort

NAT-T encapsule ESP dans UDP 4500 pour traverser le NAT. Le port 500 sert à IKE. La détection de pair mort (DPD) envoie des probes pour détecter une extrémité silencieuse et déclencher la bascule.

```text
IKE        UDP 500
NAT-T      UDP 4500
ESP        IP protocole 50
AH         IP protocole 51
```

### 2.5 Perfect Forward Secrecy

PFS garantit qu'une compromission de clé à long terme ne permet pas de déchiffrer les sessions passées. On utilise un groupe DH par phase 2. Sans PFS, la clé de session peut être dérivée d'une clé maîtresse compromise.

---

## 3. Configuration IPsec Cisco IOS

### 3.1 IKEv2 et IPsec

```cisco
crypto ikev2 proposal IKE-PROP
 encryption aes-cbc-256
 integrity sha256
 group 14
!
crypto ikev2 policy IKE-POL
 proposal IKE-PROP
!
crypto ikev2 keyring SITE-B
 peer 203.0.113.2
  address 203.0.113.2
  pre-shared-key local MonSecretLocal
  pre-shared-key remote MonSecretRemote
!
crypto ikev2 profile IKE-PROFILE
 match identity remote address 203.0.113.2 255.255.255.255
 identity local address 203.0.113.1
 authentication remote pre-share
 authentication local pre-share
 keyring local SITE-B
 dpd 10 3 on-demand
!
crypto ipsec transform-set TS esp-aes 256 esp-sha256-hmac
 mode tunnel
!
crypto ipsec profile IPSEC-PROFILE
 set transform-set TS
 set ikev2-profile IKE-PROFILE
 set pfs group14
!
interface Tunnel100
 ip address 10.255.0.1 255.255.255.252
 tunnel source GigabitEthernet0/0
 tunnel destination 203.0.113.2
 tunnel mode ipsec ipv4
 tunnel protection ipsec profile IPSEC-PROFILE
```

Les réseaux intéressants sont routés vers le tunnel :

```cisco
ip route 10.20.0.0 255.255.255.0 Tunnel100
```

### 3.2 Vérifications IPsec

```cisco
show crypto ikev2 sa
show crypto ikev2 session
show crypto ipsec sa
show crypto ipsec profile
show ip route
show interface Tunnel100
```

| Commande | Ce qu'elle montre |
|---|---|
| `show crypto ikev2 sa` | État de l'IKE SA, identités, chiffrement |
| `show crypto ipsec sa` | SPI, paquets encapsulés/décapsulés, erreurs |
| `show interface Tunnel100` | MTU, état, compteurs |
| `show ip route` | Le trafic intéressant est-il routé dans le tunnel ? |

Des compteurs `encaps` qui augmentent mais `decaps` à zéro indiquent souvent un problème de retour, de NAT ou de politique chez le pair.

---

## 4. SSL/TLS VPN

Un VPN TLS utilise TLS (souvent 443) pour créer un tunnel ou un accès applicatif. Il traverse mieux les réseaux restrictifs et s'appuie sur l'infrastructure PKI.

### 4.1 Clientless vs full tunnel

| Mode | Accès | Cas d'usage |
|---|---|---|
| Clientless | Portail web, applications publiées | Accès ponctuel |
| Full tunnel | Tout le trafic ou des sous-réseaux | Télétravail complet |
| Split tunnel | Seulement certains réseaux | Réduire la charge et la latence |

Le split tunnel améliore les performances mais réduit le contrôle : le trafic hors tunnel ne passe pas par la politique de sécurité. On l'autorise seulement si le poste est géré.

### 4.2 AnyConnect et certificats

Cisco Secure Client (AnyConnect) utilise TLS et éventuellement DTLS pour la performance. L'authentification combine souvent certificat machine, utilisateur et MFA. Le profil doit définir les serveurs, les routes, les DNS et les politiques de posture.

### 4.3 OpenVPN

OpenVPN utilise TLS pour la négociation et peut transporter le trafic en UDP ou TCP. Il est très portable et flexible, mais moins performant qu'un VPN noyau sur certains débits. Les certificats, la révocation et la gestion des clients sont essentiels.

### 4.4 Considérations TLS

- certificats valides et chaîne complète ;
- révocation (CRL/OCSP) ;
- versions et suites TLS à jour ;
- terminaison et inspection ;
- protection contre le downgrade ;
- séparation des profils utilisateurs.

Un VPN TLS mal configuré peut être vulnérable au MITM si le client ignore les erreurs de certificat. L'épinglage et la validation stricte sont indispensables.

---

## 5. WireGuard

WireGuard est un VPN moderne, simple et rapide, basé sur le protocole Noise. Il utilise des clés publiques/privées par pair et un ensemble minimal d'algorithmes.

### 5.1 Modèle

```text
Interface wg0
  PrivateKey = ...
  Address = 10.200.0.1/24
  ListenPort = 51820

[Peer]
  PublicKey = ...
  AllowedIPs = 10.200.0.2/32, 10.20.0.0/24
  Endpoint = 203.0.113.2:51820
```

`AllowedIPs` sert à la fois de routage cryptographique et de filtre : un pair ne peut envoyer que les préfixes autorisés.

### 5.2 Commandes

```bash
ip link add wg0 type wireguard
ip addr add 10.200.0.1/24 dev wg0
wg setconf wg0 /etc/wireguard/wg0.conf
ip link set wg0 up
wg show
ip route add 10.20.0.0/24 dev wg0
```

### 5.3 Avantages et limites

| Avantages | Limites |
|---|---|
| Configuration simple | Pas de gestion native de PKI |
| Performances élevées | Pas de clientless |
| Roaming intégré | Nécessite un contrôle d'accès externe |
| Code réduit | Pas de fédération d'identité intégrée |

WireGuard est excellent pour les tunnels de site à site et les accès gérés, mais il faut ajouter la gestion des clés, la révocation, l'audit et la politique de sécurité.

---

## 6. Routage, MTU et NAT

### 6.1 Trafic intéressant

Un VPN site-to-site ne transporte que le trafic qui correspond à une route ou à une ACL de trafic intéressant. Si les routes ne pointent pas vers le tunnel, le paquet part en clair ou est perdu.

```text
LAN A 10.10.0.0/24 <--- route ---> Tunnel <--- route ---> LAN B 10.20.0.0/24
```

### 6.2 MTU et MSS

L'encapsulation ajoute des en-têtes. Un paquet de 1500 octets peut dépasser le MTU du tunnel et être fragmenté ou rejeté. On ajuste le MTU du tunnel et le MSS des sessions TCP.

```cisco
interface Tunnel100
 ip mtu 1400
 ip tcp adjust-mss 1360
```

Le MSS clamping évite que les serveurs envoient des segments trop gros. Un ping fonctionne souvent alors qu'un transfert de fichier échoue : c'est le symptôme classique du MTU.

### 6.3 NAT et VPN

Le NAT peut casser IPsec AH, exiger NAT-T et compliquer le routage. Un VPN derrière un NAT doit souvent utiliser ESP dans UDP 4500. Les équipements intermédiaires doivent laisser passer IKE et NAT-T.

### 6.4 Chevauchement d'adresses

Deux sites qui utilisent le même réseau `192.168.1.0/24` ne peuvent pas être routés simplement. Les solutions : renumérotation, NAT de site, VRF, ou architecture avec adressage centralisé. Le chevauchement est une cause fréquente d'échec de tunnel.

---

## 7. VPN remote access et sécurité

### 7.1 Authentification

Un accès distant doit combiner :

- identité utilisateur (mot de passe, MFA) ;
- posture de l'appareil (antivirus, chiffrement, mises à jour) ;
- certificat ou clé ;
- autorisation par groupe.

Le VPN ne doit pas donner un accès réseau complet à tous les utilisateurs. On applique le moindre privilège et une segmentation.

### 7.2 Split tunnel et DNS

Un split tunnel mal configuré peut envoyer les requêtes DNS internes vers Internet ou provoquer des fuites. On contrôle les serveurs DNS poussés au client et on interdit les résolveurs non approuvés.

### 7.3 Attaques et hardening

| Menace | Contre-mesure |
|---|---|
| PSK faible | Clé longue, rotation, certificats |
| IKE aggressive | IKEv2, identités protégées |
| Downgrade | Propositions strictes, pas de 3DES/SHA1 |
| MITM TLS | Validation stricte, épinglage |
| Usurpation d'endpoint | Authentification mutuelle, DPD |
| DDoS | Anycast, rate limiting, protection amont |

### 7.4 Journalisation

On journalise les connexions, les échecs d'authentification, les changements de tunnel et les erreurs de politique. Les logs doivent inclure l'identité, l'adresse, la durée et la raison de fermeture. Sans NTP, ils sont inexploitables.

---

## 8. Dépannage IPsec

### 8.1 IKE ne monte pas

1. Vérifier UDP 500/4500 et le NAT.
2. Vérifier les propositions et la politique.
3. Vérifier l'identité et la PSK/certificat.
4. Vérifier l'heure (certificats).
5. Lire `show crypto ikev2 sa` et les logs.

```cisco
debug crypto ikev2 packet
debug crypto ikev2 error
```

Un debug doit être limité dans le temps et filtré. Sur un équipement de production, il peut saturer le CPU.

### 8.2 IPsec monte mais pas de trafic

1. Vérifier les routes vers les réseaux distants.
2. Vérifier les ACL/SPD et le trafic intéressant.
3. Vérifier le NAT et les traductions.
4. Vérifier le MTU/MSS.
5. Vérifier `show crypto ipsec sa` (encaps/decaps).

### 8.3 Tunnel instable

Chercher : DPD, rekey, perte de paquets, NAT timeout, MTU, asymétrie, surcharge. Un tunnel qui tombe toutes les heures peut être un problème de durée de vie ou de rekey mal aligné.

---

## 9. Conception et bonnes pratiques

- préférer IKEv2 et AES-GCM/SHA-2 ;
- éviter les PSK partagées par tous les sites ;
- utiliser des certificats et une PKI ;
- définir précisément le trafic intéressant ;
- prévoir le MTU/MSS dès la conception ;
- router de façon symétrique ;
- surveiller les tunnels et les rekey ;
- documenter les réseaux et les politiques ;
- tester la bascule et la restauration ;
- intégrer le VPN à une stratégie zero trust.

Un VPN n'est qu'un tuyau. La sécurité réelle vient de l'authentification, de l'autorisation, de la segmentation et de la surveillance. Un tunnel chiffré entre deux réseaux mal cloisonnés reste une surface d'attaque.

---

## 10. Cas pratique : VPN derrière un firewall

Un tunnel site-to-site traverse souvent un firewall. La politique doit autoriser les flux de contrôle et les flux chiffrés, mais pas tout le trafic.

| Flux | Protocole/port | Direction |
|---|---|---|
| IKE | UDP 500 | Gateway A ↔ Gateway B |
| NAT-T | UDP 4500 | Gateway A ↔ Gateway B (si NAT) |
| ESP | IP 50 | Gateway A ↔ Gateway B (sans NAT) |
| Données internes | Selon politique | Réseaux A ↔ réseaux B |

Si le firewall fait du NAT, ESP seul est incompatible avec AH et peut nécessiter NAT-T. Si le firewall inspecte le trafic, il doit reconnaître les paquets ESP comme un flux légitime, ou laisser le tunnel se terminer sur une interface dédiée.

Un VPN traversant un firewall stateful doit aussi gérer les timeouts. Un tunnel sans trafic peut voir sa session NAT expirée ; les keepalives IKE/DPD maintiennent l'état. On surveille les logs de rekey et de fermeture pour distinguer une coupure réseau d'une expiration de session.

### 10.1 DMVPN et hub-and-spoke

DMVPN combine mGRE, NHRP et IPsec pour construire des tunnels dynamiques entre un hub et des spokes. Le hub centralise les routes, les spokes établissent des tunnels à la demande. Les variantes :

- phase 1 : spokes vers hub uniquement ;
- phase 2 : spokes peuvent se parler via le hub ;
- phase 3 : raccourci direct entre spokes.

DMVPN réduit la configuration par site mais ajoute de la complexité de routage et de MTU. Les mêmes règles s'appliquent : routes cohérentes, MSS clamping, authentification forte et surveillance des rekey.

### 10.2 Zero trust et VPN

Le VPN traditionnel place l'utilisateur dans un réseau de confiance. Le modèle zero trust vérifie chaque accès, chaque appareil et chaque application. Un VPN peut rester un transport, mais l'autorisation doit être granulaire : identité, posture, application, contexte. Les architectures modernes combinent VPN, proxy inverse, ZTNA et segmentation.

## 11. Exercices

1. Configurer un tunnel IPsec IKEv2 entre deux routeurs.
2. Vérifier les SA et les compteurs de paquets.
3. Provoquer un échec de PSK et lire les logs.
4. Configurer WireGuard entre deux hôtes et router un LAN.
5. Diagnostiquer un transfert qui échoue à cause du MTU.
6. Comparer split tunnel et full tunnel.
7. Mettre en place un accès distant TLS avec certificat.
8. Tester la révocation d'un certificat client.
9. Concevoir une architecture site-to-site avec deux FAI.
10. Rédiger une procédure de vérification d'un tunnel après incident.
