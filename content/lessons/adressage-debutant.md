# L’adressage IP — Niveau débutant
## Comprendre les adresses, les masques et la communication entre machines

> **Niveau :** Débutant  
> **Prérequis :** notions de réseau local, de switch et de routeur.  
> **Objectif :** lire une adresse IPv4, reconnaître les plages privées, comprendre le masque et configurer une machine dans un réseau simple.

---


> **Schémas intégrés :** le code SVG est directement présent dans ce fichier Markdown. Aucun dossier `images` séparé n’est nécessaire.

---


## 1. Qu’est-ce qu’une adresse IP ?

Une adresse IP est une adresse logique affectée à une interface réseau. Elle aide les équipements à identifier les destinations et à acheminer des paquets au niveau IP.

- **Adresse IP :** adressage logique et routage.
- **Adresse MAC :** adresse de couche liaison utilisée notamment pour la livraison d’une trame sur Ethernet local.
- **Nom DNS :** nom tel que `serveur.example.com`, qui peut être traduit en adresse IP.

Exemple de configuration :

```text
Ordinateur : PC-01
IPv4       : 192.168.10.25
Masque     : 255.255.255.0
Préfixe    : /24
Passerelle : 192.168.10.1
DNS        : selon le réseau
```

Ces paramètres ont des rôles différents : l’adresse identifie l’interface, le masque détermine le préfixe réseau, la passerelle fournit une prochaine étape pour les destinations distantes et le DNS résout des noms.

## 2. IPv4 : 32 bits en quatre octets

Une adresse IPv4 contient 32 bits, présentés sous la forme de quatre nombres décimaux séparés par des points. Chaque groupe est un **octet de 8 bits** et sa valeur peut aller de 0 à 255.

```text
192 . 168 . 10 . 25
 |     |    |    |
 8 bits par octet
```

Chaque bit d’un octet correspond à une valeur : 128, 64, 32, 16, 8, 4, 2 ou 1.

Exemple : `192 = 128 + 64`, donc 192 s’écrit `11000000` en binaire. De même, `10 = 8 + 2`, donc 10 s’écrit `00001010`.

L’adresse `192.168.10.25` s’écrit en binaire :

```text
11000000.10101000.00001010.00011001
```

Tu n’as pas besoin de convertir chaque adresse à la main au début, mais la logique binaire est utile pour comprendre les masques et le sous-réseautage.

## 3. Le masque et le préfixe

Le masque indique quelle partie de l’adresse correspond au préfixe réseau et quelle partie reste disponible pour les hôtes.

```text
Adresse : 11000000.10101000.00001010.00011001
Masque  : 11111111.11111111.11111111.00000000
          <-------- 24 bits réseau -------><hôte>
```

Le masque `255.255.255.0` correspond à `/24`, car les 24 premiers bits du masque sont à 1.

Avec `192.168.10.25/24` :

- réseau : `192.168.10.0/24` ;
- adresse de l’interface : `192.168.10.25` ;
- les adresses `192.168.10.x` du même préfixe appartiennent au même sous-réseau, sauf règles particulières ou configuration différente.

## 4. Lire les préfixes CIDR

La notation CIDR écrit le nombre de bits du préfixe après une barre oblique.

| Préfixe | Masque IPv4 | Adresses totales |
|---|---|---:|
| `/8` | `255.0.0.0` | 16 777 216 |
| `/16` | `255.255.0.0` | 65 536 |
| `/24` | `255.255.255.0` | 256 |
| `/25` | `255.255.255.128` | 128 |
| `/26` | `255.255.255.192` | 64 |
| `/27` | `255.255.255.224` | 32 |
| `/28` | `255.255.255.240` | 16 |

Dans un sous-réseau IPv4 classique, l’adresse réseau et l’adresse de broadcast ne sont généralement pas attribuées à des hôtes. Donc, un `/24` contient 256 adresses au total et 254 adresses hôtes utilisables dans le modèle classique. Les préfixes `/31` et `/32` sont des cas particuliers étudiés au niveau expert.

## 5. Réseau, adresse hôte et broadcast

Pour `192.168.10.0/24` :

| Élément | Adresse | Rôle |
|---|---|---|
| Réseau | `192.168.10.0` | Identifie le sous-réseau |
| Première adresse hôte classique | `192.168.10.1` | Utilisable par un équipement |
| Exemple d’hôte | `192.168.10.25` | Interface d’un poste |
| Dernière adresse hôte classique | `192.168.10.254` | Utilisable par un équipement |
| Broadcast IPv4 | `192.168.10.255` | Diffusion vers le sous-réseau |

L’adresse `192.168.10.50/24` appartient au même sous-réseau que `192.168.10.25/24`. En revanche, `192.168.11.50/24` appartient à `192.168.11.0/24` et nécessite un mécanisme de routage pour communiquer avec le premier réseau.

## 6. Schéma : deux ordinateurs dans le même sous-réseau



<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 340" role="img" aria-labelledby="beginner_network-title beginner_network-desc">
  <title id="beginner_network-title">Deux ordinateurs dans le même sous-réseau</title>
  <desc id="beginner_network-desc">PC-01 et PC-02 sont reliés à un switch et utilisent des adresses du réseau 192.168.10.0/24.</desc>
  <defs>
    <marker id="beginner_network-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#55d6be"/></marker>
    <style>
      .bg{fill:#0b1220}.panel{fill:#151f32;stroke:#34435e;stroke-width:1.5}.title{fill:#f1f5f9;font:700 19px sans-serif}.label{fill:#cbd5e1;font:15px sans-serif}.small{fill:#94a3b8;font:13px sans-serif}.wire{fill:none;stroke:#55d6be;stroke-width:3;stroke-dasharray:9 8;marker-end:url(#beginner_network-arrow);animation:beginner_network-flow 1.6s linear infinite}.wire2{fill:none;stroke:#60a5fa;stroke-width:3}@keyframes beginner_network-flow{to{stroke-dashoffset:-34}}@media(prefers-reduced-motion:reduce){.wire{animation:none}}
    </style>
  </defs>
  <rect class="bg" width="940" height="340" rx="18"/>
  <text class="title" x="30" y="36">Même réseau logique : 192.168.10.0/24</text>
  <rect class="panel" x="36" y="82" width="240" height="120" rx="12"/>
  <rect x="58" y="102" width="44" height="32" rx="3" fill="none" stroke="#60a5fa" stroke-width="2"/><path d="M80 134v8m-12 0h24" stroke="#60a5fa" stroke-width="2"/>
  <text class="title" x="118" y="117">PC-01</text><text class="label" x="58" y="163">192.168.10.25/24</text><text class="small" x="58" y="184">Réseau : 192.168.10.0</text>
  <rect class="panel" x="350" y="104" width="240" height="90" rx="12"/><text class="title" x="470" y="139" text-anchor="middle">Switch</text><text class="small" x="470" y="163" text-anchor="middle">Commutation Ethernet</text>
  <path class="wire2" d="M276 142 H350"/><path class="wire" d="M276 142 H350"/><path class="wire2" d="M590 142 H665"/><path class="wire" d="M590 142 H665"/>
  <rect class="panel" x="665" y="82" width="240" height="120" rx="12"/>
  <rect x="687" y="102" width="44" height="32" rx="3" fill="none" stroke="#60a5fa" stroke-width="2"/><path d="M709 134v8m-12 0h24" stroke="#60a5fa" stroke-width="2"/>
  <text class="title" x="746" y="117">PC-02</text><text class="label" x="687" y="163">192.168.10.50/24</text><text class="small" x="687" y="184">Même préfixe /24</text>
  <rect x="36" y="238" width="869" height="69" rx="10" fill="#102b33" stroke="#236e70"/><text x="58" y="265" fill="#99f6e4" font="600 15px sans-serif">À retenir</text><text class="label" x="58" y="288">Les deux adresses appartiennent à 192.168.10.0/24 : aucun routeur n’est requis</text><text class="label" x="58" y="306">pour acheminer le trafic entre ces deux hôtes, si le réseau local le permet.</text>
</svg>



Les deux PC utilisent le préfixe `192.168.10.0/24`. Le switch commute les trames Ethernet entre les ports. Le trafic IP entre deux hôtes du même sous-réseau n’a normalement pas besoin de passer par un routeur, si le lien, la configuration et les règles de sécurité le permettent.

## 7. Les adresses privées IPv4

Les trois plages privées RFC 1918 sont :

| Plage | Préfixe | Exemple |
|---|---|---|
| `10.0.0.0` à `10.255.255.255` | `10.0.0.0/8` | `10.20.5.10` |
| `172.16.0.0` à `172.31.255.255` | `172.16.0.0/12` | `172.20.1.15` |
| `192.168.0.0` à `192.168.255.255` | `192.168.0.0/16` | `192.168.1.20` |

Attention : `172.20.10.5` est privé, mais `172.32.10.5` n’appartient pas à la plage privée RFC 1918. Une adresse privée n’est pas automatiquement protégée contre les autres machines du même réseau.

Les réseaux privés accèdent souvent à Internet au moyen d’un routeur et d’une traduction d’adresses (NAT). Le NAT n’est pas un remplacement d’un pare-feu ni d’une politique de filtrage.

## 8. La passerelle par défaut

La passerelle par défaut est généralement l’adresse d’un routeur présente sur le sous-réseau local. Le poste la consulte pour acheminer du trafic lorsqu’aucune route plus spécifique ne convient.

- Destination locale (`192.168.10.50/24`) : le poste tente une livraison directe sur le réseau local.
- Destination distante (`8.8.8.8`) : le poste utilise normalement une route vers le routeur, souvent la route par défaut.



<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 940 320" role="img" aria-labelledby="beginner_gateway-t beginner_gateway-d">
  <title id="beginner_gateway-t">Rôle de la passerelle par défaut</title><desc id="beginner_gateway-d">Un PC envoie le trafic local directement vers un hôte local et remet le trafic distant au routeur.</desc>
  <defs><marker id="beginner_gateway-ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fbbf24"/></marker><style>
  .bg{fill:#0b1220}.p{fill:#151f32;stroke:#34435e;stroke-width:1.5}.h{fill:#f1f5f9;font:700 17px sans-serif}.tx{fill:#cbd5e1;font:14px sans-serif}.sm{fill:#94a3b8;font:12px sans-serif}.route{fill:none;stroke:#fbbf24;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#beginner_gateway-ar);animation:beginner_gateway-go 1.5s linear infinite}@keyframes beginner_gateway-go{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.route{animation:none}}
  </style></defs>
  <rect class="bg" width="940" height="320" rx="18"/><text class="h" x="28" y="34">Destination locale ou distante ?</text>
  <rect class="p" x="28" y="92" width="200" height="90" rx="12"/><text class="h" x="128" y="121" text-anchor="middle">PC-01</text><text class="tx" x="128" y="145" text-anchor="middle">192.168.10.25/24</text><text class="sm" x="128" y="164" text-anchor="middle">Passerelle .10.1</text>
  <rect class="p" x="355" y="60" width="220" height="75" rx="12"/><text class="h" x="465" y="89" text-anchor="middle">Hôte local</text><text class="tx" x="465" y="113" text-anchor="middle">192.168.10.50</text>
  <rect class="p" x="355" y="198" width="220" height="75" rx="12"/><text class="h" x="465" y="227" text-anchor="middle">Routeur</text><text class="tx" x="465" y="251" text-anchor="middle">192.168.10.1</text>
  <rect class="p" x="700" y="198" width="210" height="75" rx="12"/><text class="h" x="805" y="227" text-anchor="middle">Réseau distant</text><text class="tx" x="805" y="251" text-anchor="middle">Ex. 8.8.8.8</text>
  <path class="route" d="M228 111 H355"/><path class="route" d="M228 159 L300 234 H355"/><path class="route" d="M575 235 H700"/><text class="sm" x="278" y="91">Local</text><text class="sm" x="255" y="199">Distant</text>
  <text class="sm" x="30" y="303">Le choix dépend de la table de routage, pas seulement de la différence visuelle entre les adresses.</text>
</svg>



La passerelle doit être correctement configurée et joignable sur le lien local. Le fait que deux adresses commencent par `192.168` ne suffit pas pour conclure qu’elles se trouvent dans le même sous-réseau : il faut prendre en compte le préfixe.

## 9. DHCP et DNS

**DHCP** attribue automatiquement des paramètres IP, selon la configuration du serveur : adresse, masque/préfixe, passerelle, DNS et durée de bail. Une réservation DHCP permet généralement de retrouver la même adresse pour un équipement identifié.

**DNS** traduit des noms en informations d’adressage. Une résolution réussie ne garantit pas que le service distant soit disponible : le routage, le pare-feu ou le serveur peuvent être en panne. À l’inverse, un service peut être joignable par IP alors que sa résolution DNS échoue.

## 10. Première comparaison entre IPv4 et IPv6

| Caractéristique | IPv4 | IPv6 |
|---|---|---|
| Taille d’adresse | 32 bits | 128 bits |
| Notation | Décimale avec points | Hexadécimale avec deux-points |
| Exemple | `192.168.10.25` | `2001:db8:10::25` |
| Loopback | `127.0.0.1` | `::1` |
| Link-local | `169.254.0.0/16` | `fe80::/10` |

Le préfixe IPv6 `2001:db8::/32` est réservé à la documentation et aux exemples. Ne l’utilise pas comme préfixe de production.

## 11. Travaux pratiques

### Topologie

```text
PC-01 ---------------- Switch ---------------- PC-02
192.168.10.25/24                         192.168.10.50/24
```

| Paramètre | PC-01 | PC-02 |
|---|---|---|
| IPv4 | `192.168.10.25` | `192.168.10.50` |
| Masque | `255.255.255.0` | `255.255.255.0` |
| Préfixe | `/24` | `/24` |
| Passerelle | `192.168.10.1` si elle existe | `192.168.10.1` si elle existe |

Ne configure une passerelle que si un routeur possède réellement cette adresse dans le réseau prévu.

### Windows

```powershell
ipconfig /all
route print
ping 127.0.0.1
ping 192.168.10.50
```

### Linux

```bash
ip -br address
ip -4 route
ping -c 4 192.168.10.50
```

Un échec de `ping` ne prouve pas toujours que l’équipement est inaccessible : ICMP peut être filtré. Vérifie aussi les interfaces, les routes, la résolution des voisins et les pare-feu.

## 12. Méthode de diagnostic

1. Vérifier le câble, le Wi-Fi, le lien physique et l’état de l’interface.
2. Vérifier l’adresse IP et le masque.
3. Chercher un doublon d’adresse.
4. Tester un hôte du même sous-réseau.
5. Vérifier la passerelle pour les destinations distantes.
6. Tester DNS si le problème concerne un nom.
7. Examiner les routes, les ACL et les pare-feu.

Modifie un seul paramètre à la fois afin de ne pas masquer la cause réelle.

## 13. Exercices

### Exercice 1

Pour `192.168.5.25/24`, donne le masque, l’adresse réseau, le broadcast et le nombre classique d’hôtes utilisables.

### Exercice 2

`192.168.20.10/24` et `192.168.21.10/24` sont-elles dans le même sous-réseau ? Explique.

### Exercice 3

Identifie les adresses appartenant à une plage privée RFC 1918 :

- `10.20.30.40`
- `172.20.10.5`
- `172.32.10.5`
- `192.168.4.15`
- `8.8.8.8`

### Exercice 4

Un poste joint un serveur local par IP mais n’atteint pas les réseaux distants. Cite trois vérifications prioritaires.

## 14. Corrigés

**Exercice 1 :** masque `255.255.255.0`, réseau `192.168.5.0`, broadcast `192.168.5.255`, 254 adresses hôtes classiques utilisables.

**Exercice 2 :** non. Les réseaux sont `192.168.20.0/24` et `192.168.21.0/24`; un routage doit les relier.

**Exercice 3 :** privées : `10.20.30.40`, `172.20.10.5`, `192.168.4.15`. Pas dans les plages RFC 1918 : `172.32.10.5`, `8.8.8.8`.

**Exercice 4 :** passerelle, table de routage, connectivité du routeur, filtrage et éventuellement NAT selon l’architecture.

## 15. À retenir

- IPv4 utilise des adresses de 32 bits.
- Le masque ou préfixe définit la taille du réseau.
- Les réseaux privés RFC 1918 sont `10.0.0.0/8`, `172.16.0.0/12` et `192.168.0.0/16`.
- DHCP configure les clients ; DNS résout les noms ; le routage achemine les paquets entre réseaux.
- Une panne DNS n’est pas nécessairement une panne IP.

## 16. Références

- [RFC 791 — Internet Protocol](https://www.rfc-editor.org/rfc/rfc791)
- [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 4632 — Classless Inter-domain Routing](https://www.rfc-editor.org/rfc/rfc4632)
- [Registre IANA des adresses IPv4 spéciales](https://www.iana.org/assignments/iana-ipv4-special-registry)

---

**Suite :** `adressage-intermediaire.md` — calcul de sous-réseaux, CIDR, VLSM et diagnostic méthodique.
