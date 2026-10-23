# L’adressage IP — Niveau intermédiaire
## Sous-réseaux, CIDR, VLSM et conception d’un plan IPv4/IPv6

> **Niveau :** Intermédiaire  
> **Prérequis :** savoir lire une adresse IPv4, un masque et le rôle d’une passerelle.  
> **Objectif :** calculer précisément des sous-réseaux, dimensionner les préfixes et construire un plan sans chevauchement.

---


> **Schémas intégrés :** le code SVG est directement présent dans ce fichier Markdown. Aucun dossier `images` séparé n’est nécessaire.

---


## 1. De la configuration au plan d’adressage

Un plan d’adressage doit répondre à quatre questions : combien d’hôtes chaque segment doit-il accueillir, quelle plage lui attribuer, comment les routeurs achemineront-ils les paquets, et comment éviter les chevauchements ou le gaspillage ?

CIDR utilise la longueur du préfixe réseau. Plus le nombre après `/` est grand, plus le préfixe est long et plus le sous-réseau est petit.

## 2. Nombre d’adresses et d’hôtes

Une adresse IPv4 contient 32 bits. Pour un préfixe `/p`, le nombre de bits hôtes est `h = 32 - p`.

Dans le modèle IPv4 classique :

```text
Adresses totales = 2^(32 - préfixe)
Hôtes utilisables = adresses totales - 2
```

La seconde formule retire l’adresse réseau et le broadcast. Elle ne s’applique pas directement aux cas particuliers `/31` et `/32`.

| Préfixe | Bits hôtes | Adresses totales | Hôtes classiques utilisables |
|---|---:|---:|---:|
| `/24` | 8 | 256 | 254 |
| `/25` | 7 | 128 | 126 |
| `/26` | 6 | 64 | 62 |
| `/27` | 5 | 32 | 30 |
| `/28` | 4 | 16 | 14 |
| `/29` | 3 | 8 | 6 |
| `/30` | 2 | 4 | 2 |

## 3. Trouver le masque et la taille de bloc

Les bits du masque sont des `1` de gauche à droite, suivis de `0`.

```text
/24 = 255.255.255.0
/25 = 255.255.255.128
/26 = 255.255.255.192
/27 = 255.255.255.224
/28 = 255.255.255.240
```

Lorsque le masque change dans un octet donné, on peut calculer la taille de bloc :

```text
Taille du bloc = 256 - valeur du masque dans l’octet concerné
```

Pour `/26`, le dernier octet du masque vaut 192, donc `256 - 192 = 64`. Les blocs dans un `/24` avancent donc de 64 adresses : `.0`, `.64`, `.128`, `.192`.

## 4. Exemple de calcul : `192.168.10.70/26`

- Masque : `255.255.255.192`
- Taille de bloc : 64 adresses
- 70 appartient au bloc `.64` à `.127`.

| Élément | Valeur |
|---|---|
| Adresse réseau | `192.168.10.64` |
| Première adresse hôte classique | `192.168.10.65` |
| Dernière adresse hôte classique | `192.168.10.126` |
| Broadcast | `192.168.10.127` |
| Total | 64 adresses |
| Hôtes classiques utilisables | 62 |



<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 370" role="img" aria-labelledby="intermediate_subnets-t intermediate_subnets-d">
  <title id="intermediate_subnets-t">Découpage d’un réseau /24 en quatre réseaux /26</title><desc id="intermediate_subnets-d">Le bloc 192.168.10.0/24 est divisé en quatre sous-réseaux de 64 adresses chacun, dont 62 adresses hôtes utilisables dans le cas classique.</desc>
  <defs><style>
  .bg{fill:#0b1220}.card{fill:#151f32;stroke:#34435e;stroke-width:1.3}.h{fill:#f1f5f9;font:700 18px sans-serif}.tx{fill:#cbd5e1;font:14px sans-serif}.sm{fill:#94a3b8;font:12px sans-serif}.c1{fill:#123c4a;stroke:#39b8d4}.c2{fill:#1d3452;stroke:#60a5fa}.c3{fill:#39294d;stroke:#c084fc}.c4{fill:#49341e;stroke:#fbbf24}.line{fill:none;stroke:#55d6be;stroke-width:3;stroke-dasharray:8 7;animation:intermediate_subnets-move 1.7s linear infinite}@keyframes intermediate_subnets-move{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.line{animation:none}}
  </style><marker id="intermediate_subnets-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#55d6be"/></marker></defs>
  <rect class="bg" width="960" height="370" rx="18"/><text class="h" x="28" y="34">Réseau parent : 192.168.10.0/24</text><text class="tx" x="28" y="57">256 adresses au total</text>
  <rect class="card" x="28" y="80" width="904" height="46" rx="8"/><text class="h" x="480" y="109" text-anchor="middle">Découpage en blocs de 64 adresses</text><path class="line" d="M480 126 V154" marker-end="url(#intermediate_subnets-arr)"/><path d="M140 164 H820 M140 164 V184 M366 164 V184 M594 164 V184 M820 164 V184" stroke="#55d6be" stroke-width="2" fill="none"/>
  <rect class="c1" x="28" y="184" width="220" height="130" rx="10"/><text class="h" x="138" y="211" text-anchor="middle">Sous-réseau 1</text><text class="tx" x="138" y="236" text-anchor="middle">192.168.10.0/26</text><text class="sm" x="138" y="259" text-anchor="middle">.0 – .63</text><text class="sm" x="138" y="280" text-anchor="middle">62 hôtes classiques</text>
  <rect class="c2" x="258" y="184" width="220" height="130" rx="10"/><text class="h" x="368" y="211" text-anchor="middle">Sous-réseau 2</text><text class="tx" x="368" y="236" text-anchor="middle">192.168.10.64/26</text><text class="sm" x="368" y="259" text-anchor="middle">.64 – .127</text><text class="sm" x="368" y="280" text-anchor="middle">62 hôtes classiques</text>
  <rect class="c3" x="488" y="184" width="220" height="130" rx="10"/><text class="h" x="598" y="211" text-anchor="middle">Sous-réseau 3</text><text class="tx" x="598" y="236" text-anchor="middle">192.168.10.128/26</text><text class="sm" x="598" y="259" text-anchor="middle">.128 – .191</text><text class="sm" x="598" y="280" text-anchor="middle">62 hôtes classiques</text>
  <rect class="c4" x="718" y="184" width="214" height="130" rx="10"/><text class="h" x="825" y="211" text-anchor="middle">Sous-réseau 4</text><text class="tx" x="825" y="236" text-anchor="middle">192.168.10.192/26</text><text class="sm" x="825" y="259" text-anchor="middle">.192 – .255</text><text class="sm" x="825" y="280" text-anchor="middle">62 hôtes classiques</text>
  <text class="sm" x="28" y="345">Les quatre blocs couvrent exactement le /24, sans chevauchement ni espace restant.</text>
</svg>



Le schéma montre quatre blocs de 64 adresses qui couvrent le `/24` sans chevauchement.

## 5. Dimensionner un sous-réseau selon le besoin

Pour accueillir 50 machines en IPv4 classique, cherche le plus petit nombre de bits hôtes `h` tel que `2^h - 2 >= 50`.

- 5 bits : `32 - 2 = 30`, insuffisant.
- 6 bits : `64 - 2 = 62`, suffisant.
- Le préfixe vaut `32 - 6 = /26`.

| Besoin | Préfixe minimal classique | Capacité classique |
|---:|---|---:|
| 10 | `/28` | 14 |
| 20 | `/27` | 30 |
| 50 | `/26` | 62 |
| 100 | `/25` | 126 |
| 200 | `/24` | 254 |
| 500 | `/23` | 510 |
| 1 000 | `/22` | 1 022 |

Il faut encore tenir compte des passerelles, équipements d’infrastructure, adresses réservées, croissance et contraintes opérationnelles.

## 6. VLSM : tailles de blocs différentes

VLSM (*Variable Length Subnet Mask*) permet d’allouer des préfixes de tailles différentes dans un même bloc parent. La méthode pratique consiste à trier les besoins du plus grand au plus petit, choisir un préfixe pour chacun, puis attribuer des blocs contigus et correctement alignés.

### Cas pratique

Le bloc est `192.168.40.0/24` et les besoins sont :

| Segment | Besoin |
|---|---:|
| Utilisateurs | 100 machines |
| Administration | 50 machines |
| Serveurs | 20 machines |
| Gestion | 10 machines |
| Lien point à point de laboratoire | 2 extrémités |

### Allocation valide

| Segment | Réseau | Première adresse hôte classique | Dernière adresse hôte classique | Broadcast |
|---|---|---|---|---|
| Utilisateurs | `192.168.40.0/25` | `.1` | `.126` | `.127` |
| Administration | `192.168.40.128/26` | `.129` | `.190` | `.191` |
| Serveurs | `192.168.40.192/27` | `.193` | `.222` | `.223` |
| Gestion | `192.168.40.224/28` | `.225` | `.238` | `.239` |
| Lien de labo | `192.168.40.240/30` | `.241` | `.242` | `.243` |

Les adresses du tableau sont abrégées dans les quatre dernières colonnes : elles gardent toutes le préfixe `192.168.40`. Le `/30` est utilisé pour l’exercice ; un `/31` peut être approprié sur un véritable lien point à point si les équipements le prennent en charge.

### La plage restante : correction importante

Les adresses `.244` à `.255` sont libres. Elles se découpent exactement en deux préfixes CIDR alignés :

- `192.168.40.244/30` : `.244` à `.247` ;
- `192.168.40.248/29` : `.248` à `.255`.

`192.168.40.244/30` est bien aligné, car 244 est divisible par 4. Ces préfixes couvrent les 12 adresses restantes sans chevauchement.



<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 360" role="img" aria-labelledby="intermediate_vlsm-t intermediate_vlsm-d">
  <title id="intermediate_vlsm-t">Architecture d’adressage VLSM d’un site</title><desc id="intermediate_vlsm-d">Un équipement de couche 3 relie des segments logiques dimensionnés avec des préfixes différents.</desc>
  <defs><marker id="intermediate_vlsm-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/></marker><style>
  .bg{fill:#0b1220}.box{fill:#151f32;stroke:#34435e;stroke-width:1.3}.h{fill:#f1f5f9;font:700 16px sans-serif}.tx{fill:#cbd5e1;font:13px sans-serif}.sm{fill:#94a3b8;font:12px sans-serif}.link{fill:none;stroke:#60a5fa;stroke-width:3;stroke-dasharray:8 7;marker-end:url(#intermediate_vlsm-arrow);animation:intermediate_vlsm-route 1.8s linear infinite}@keyframes intermediate_vlsm-route{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.link{animation:none}}
  </style></defs>
  <rect class="bg" width="960" height="360" rx="18"/><text class="h" x="25" y="32">Bloc du site : 192.168.40.0/24 — sous-réseaux de tailles différentes</text>
  <rect class="box" x="335" y="55" width="290" height="62" rx="12"/><text class="h" x="480" y="81" text-anchor="middle">Routeur / couche L3</text><text class="sm" x="480" y="101" text-anchor="middle">Passerelle de chaque VLAN</text>
  <path class="link" d="M480 117 V151 H102 V181"/><path class="link" d="M480 151 H290 V181"/><path class="link" d="M480 151 H490 V181"/><path class="link" d="M480 151 H690 V181"/><path class="link" d="M480 151 H870 V181"/>
  <rect class="box" x="22" y="181" width="160" height="112" rx="10"/><text class="h" x="102" y="208" text-anchor="middle">Utilisateurs</text><text class="tx" x="102" y="232" text-anchor="middle">192.168.40.0/25</text><text class="sm" x="102" y="255" text-anchor="middle">126 hôtes max.</text>
  <rect class="box" x="202" y="181" width="176" height="112" rx="10"/><text class="h" x="290" y="208" text-anchor="middle">Administration</text><text class="tx" x="290" y="232" text-anchor="middle">192.168.40.128/26</text><text class="sm" x="290" y="255" text-anchor="middle">62 hôtes max.</text>
  <rect class="box" x="402" y="181" width="176" height="112" rx="10"/><text class="h" x="490" y="208" text-anchor="middle">Serveurs</text><text class="tx" x="490" y="232" text-anchor="middle">192.168.40.192/27</text><text class="sm" x="490" y="255" text-anchor="middle">30 hôtes max.</text>
  <rect class="box" x="602" y="181" width="176" height="112" rx="10"/><text class="h" x="690" y="208" text-anchor="middle">Gestion</text><text class="tx" x="690" y="232" text-anchor="middle">192.168.40.224/28</text><text class="sm" x="690" y="255" text-anchor="middle">14 hôtes max.</text>
  <rect class="box" x="802" y="181" width="136" height="112" rx="10"/><text class="h" x="870" y="208" text-anchor="middle">Lien labo</text><text class="tx" x="870" y="232" text-anchor="middle">.240/30</text><text class="sm" x="870" y="255" text-anchor="middle">2 hôtes</text>
  <text class="sm" x="25" y="326">Un VLAN n'est pas à lui seul une route : les interfaces de couche 3 assurent l'acheminement.</text>
</svg>



Le routeur ou le commutateur de couche 3 réalise le routage entre les réseaux associés aux VLAN. Un VLAN n’est pas, à lui seul, une route : les interfaces de couche 3 et les tables de routage doivent être correctement configurées.

## 7. Routes et préfixe le plus long

Exemple de table de routage simplifiée :

```text
192.168.10.0/24   directement connecté
192.168.20.0/24   via 192.168.10.254
10.50.0.0/16      via 192.168.10.253
0.0.0.0/0         passerelle par défaut
```

La route `0.0.0.0/0` est la route par défaut IPv4. Pour le transfert, on retient généralement la route valide la plus spécifique qui correspond à la destination, selon les règles de sélection et la table installée.

Exemple : les routes `10.0.0.0/8` et `10.20.0.0/16` correspondent toutes deux à `10.20.5.8`; `/16` est le préfixe le plus long et le plus spécifique.

## 8. Agrégation CIDR

Quatre réseaux `/24` contigus et alignés :

```text
10.20.0.0/24
10.20.1.0/24
10.20.2.0/24
10.20.3.0/24
```

peuvent être résumés par `10.20.0.0/22`. Le résumé ne doit pas englober involontairement des adresses appartenant à un autre site ou à un autre domaine de routage. Il faut vérifier la plage couverte, l’alignement, la disponibilité des routes internes et le comportement en cas de panne.

## 9. Introduction à IPv6

IPv6 utilise 128 bits et une notation hexadécimale. Exemple développé :

```text
2001:0db8:0010:0000:0000:0000:0000:0025
```

Notation raccourcie :

```text
2001:db8:10::25
```

Règles essentielles : enlever les zéros en tête de chaque groupe et utiliser `::` pour remplacer une suite contiguë de groupes à zéro, une seule fois dans une adresse.

| Plage/adresse | Usage |
|---|---|
| `::1/128` | Loopback |
| `fe80::/10` | Link-local |
| `fc00::/7` | Unique Local Addresses (ULA) |
| `2001:db8::/32` | Documentation |
| `ff00::/8` | Multicast |

IPv6 n’a pas d’adresse broadcast. Les réseaux locaux IPv6 utilisent fréquemment un préfixe `/64`, notamment pour les mécanismes d’autoconfiguration. Les préfixes de documentation ne doivent pas être utilisés en production.

## 10. Diagnostic des erreurs classiques

### Mauvais masque

Un poste `192.168.10.70/26` appartient à `192.168.10.64/26`. Il ne considère pas `192.168.10.1` comme un voisin local avec ce masque. Si `192.168.10.1` devait être sa passerelle, la conception du sous-réseau et les paramètres doivent être corrigés.

### Mauvaise passerelle

Un poste `192.168.10.25/24` configuré avec `192.168.20.1` comme passerelle a probablement une configuration incohérente : la passerelle n’est pas dans le sous-réseau local prévu.

### Chevauchement

Deux interfaces L3 indépendantes ne doivent pas utiliser involontairement des réseaux qui se chevauchent. Cela peut créer des décisions de routage ambiguës et des échecs intermittents.

### Panne DNS

Sous Linux :

```bash
ip address
ip route
getent hosts example.com
```

Sous Windows :

```powershell
ipconfig /all
route print
nslookup example.com
```

## 11. Atelier

Une organisation possède `10.50.0.0/22` et veut créer :

- utilisateurs : 400 machines ;
- serveurs : 100 machines ;
- administration : 40 machines ;
- invités : 80 machines ;
- réserve de croissance.

Travail demandé :

1. Trouver les préfixes minimaux.
2. Affecter des blocs alignés, non chevauchants et inclus dans `10.50.0.0/22`.
3. Prévoir passerelles, DHCP et réserves statiques.
4. Vérifier que la somme des blocs tient dans le `/22`.
5. Définir les routes entre les segments.

Indice : `10.50.0.0/22` couvre `10.50.0.0` à `10.50.3.255`, soit 1 024 adresses. Il faut disposer les blocs alignés, et non simplement additionner des capacités d’hôtes.

## 12. Exercices corrigés

### Exercice 1

Pour `172.16.35.123/20`, le masque est `255.255.240.0`. La taille de bloc dans le troisième octet vaut 16 : 35 appartient au bloc 32–47.

- Réseau : `172.16.32.0/20`
- Première adresse hôte classique : `172.16.32.1`
- Dernière adresse hôte classique : `172.16.47.254`
- Broadcast : `172.16.47.255`

### Exercice 2

Pour 120 machines, le `/25` permet 126 hôtes classiques utilisables : c’est le plus petit préfixe adapté.

### Exercice 3

`10.10.0.0/24` à `10.10.3.0/24` peuvent être agrégés en `10.10.0.0/22`, les quatre blocs étant contigus et correctement alignés.

### Exercice 4

Si la passerelle répond mais qu’une destination distante échoue, examiner la table de routage du poste, les routes du routeur, le filtrage, les interfaces et le NAT éventuel. Si un nom est testé, vérifier aussi le DNS.

## 13. Contrôle avant déploiement

- [ ] Chaque préfixe est dimensionné pour le besoin et la croissance.
- [ ] Les préfixes respectent leurs frontières CIDR.
- [ ] Aucun chevauchement involontaire n’existe.
- [ ] Les passerelles sont dans les réseaux appropriés.
- [ ] Les plages DHCP et statiques sont coordonnées.
- [ ] Les routes et les politiques de sécurité sont validées.
- [ ] Les préfixes IPv6 utilisés sont réellement attribués à l’organisation.

## 14. Références

- [RFC 1918 — Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 4632 — CIDR](https://www.rfc-editor.org/rfc/rfc4632)
- [RFC 3021 — Préfixes IPv4 /31 point à point](https://www.rfc-editor.org/rfc/rfc3021)
- [RFC 4291 — IPv6 Addressing Architecture](https://www.rfc-editor.org/rfc/rfc4291)
- [RFC 5952 — Représentation textuelle IPv6](https://www.rfc-editor.org/rfc/rfc5952)

---

**Suite :** `adressage-expert.md` — hiérarchie des préfixes, agrégation avancée, cas particuliers IPv4 et architecture IPv6.
