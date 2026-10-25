# BGP Peering & Internet — Débutant

## Mise en contexte : comment les réseaux communiquent-ils à l'échelle mondiale ?

Imagine que tu utilises ton téléphone au Cameroun pour consulter un site hébergé dans un centre de données en Europe. Ton opérateur mobile sait transporter les données sur son propre réseau, mais le serveur appartient peut-être à une entreprise connectée à un autre opérateur, lui-même relié à plusieurs réseaux supplémentaires.

Comment ton opérateur apprend-il quels réseaux permettent d'atteindre le serveur ? Comment les opérateurs échangent-ils des informations de joignabilité ? Et pourquoi deux opérateurs peuvent-ils choisir des chemins différents pour joindre la même destination ?

Une partie essentielle de la réponse est **BGP**, le protocole de routage interdomaines utilisé pour échanger des informations de joignabilité entre systèmes autonomes.

> **Idée essentielle :** Internet n'est pas un réseau unique administré par une seule organisation. C'est un ensemble de réseaux indépendants qui coopèrent. BGP leur permet d'annoncer des destinations IP et d'appliquer leurs propres politiques de routage.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu seras capable de :

- Expliquer le rôle de BGP dans le fonctionnement d'Internet.
- Définir les notions d'AS, d'ASN, de préfixe IP et de table de routage.
- Distinguer le peering, le transit IP et un Internet Exchange Point (IXP).
- Expliquer la différence entre eBGP et iBGP.
- Décrire les grandes étapes de l'établissement d'une session BGP.
- Reconnaître les principaux attributs d'une route BGP.
- Comprendre pourquoi BGP ne choisit pas toujours le chemin qui semble le plus court géographiquement.
- Vérifier une session BGP et diagnostiquer quelques problèmes élémentaires.
- Construire une petite maquette eBGP dans un environnement de laboratoire.
- Identifier les risques des annonces incorrectes et les protections de base.

## 2. Prérequis

Il est utile de connaître les adresses IPv4, la notation CIDR, les sous-réseaux, les routeurs, les tables de routage et les bases de TCP/IP. Il n'est pas nécessaire d'avoir déjà configuré BGP.

# Partie I — Comprendre Internet et le routage interdomaines

## 3. Internet est un réseau de réseaux

À petite échelle, une entreprise possède des routeurs, des commutateurs, des serveurs et des connexions entre ses sites. À grande échelle, des opérateurs relient des villes, des pays et des continents. Ces réseaux peuvent appartenir à des organisations différentes et appliquer des politiques différentes.

On retrouve notamment :

- les fournisseurs d'accès à Internet (FAI) ;
- les opérateurs mobiles ;
- les opérateurs de transport IP ;
- les fournisseurs de transit IP ;
- les fournisseurs de contenu et les plateformes cloud ;
- les universités, les administrations et les grands réseaux d'entreprise ;
- les réseaux de distribution de contenu (CDN).

Ces organisations doivent pouvoir échanger du trafic vers leurs destinations respectives.

### 3.1 Exemple simplifié de chemin

```text
Téléphone ou ordinateur
        |
        v
Réseau d'accès de l'utilisateur
        |
        v
Opérateur local
        |
        v
Réseau de transit ou liaison de peering
        |
        v
Autre opérateur / réseau de contenu
        |
        v
Serveur de destination
```

Ce dessin représente un chemin possible, pas une route obligatoire. Deux réseaux peuvent être reliés directement, se rencontrer dans un point d'échange Internet ou utiliser un fournisseur de transit. Le chemin peut changer à la suite d'une panne ou d'une modification de politique.

Il ne faut pas confondre le chemin logique visible dans BGP avec le chemin physique exact emprunté par les fibres optiques. BGP manipule des informations de routage ; il ne constitue pas une carte détaillée de tous les câbles et routeurs d'Internet.

## 4. Qu'est-ce qu'un système autonome ?

Un **système autonome**, ou **AS** (*Autonomous System*), est un ensemble de réseaux et de routeurs exploités sous une administration commune qui présente une politique de routage cohérente vis-à-vis des autres réseaux.

Chaque AS utilisé dans le routage interdomaines est identifié par un **ASN** (*Autonomous System Number*), c'est-à-dire un numéro de système autonome.

Exemple pédagogique :

| Organisation fictive | ASN de laboratoire | Fonction illustrative |
|---|---:|---|
| Opérateur Alpha | 65010 | Fournisseur d'accès |
| Opérateur Beta | 65020 | Opérateur régional |
| Réseau Gamma | 65030 | Réseau de contenu |

Ces ASN sont des numéros privés réservés aux usages privés. Ils conviennent à une maquette isolée, mais ne doivent pas être utilisés comme identifiants publics uniques sur Internet. Les plages privées documentées sont `64512–65534` et `4200000000–4294967294`.

Pour une utilisation publique, un opérateur obtient un ASN approprié auprès du registre Internet régional compétent, selon les procédures en vigueur. En Afrique, le registre régional est AFRINIC.

### 4.1 Représentation de plusieurs systèmes autonomes

```text
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ AS 65010        │       │ AS 65020        │       │ AS 65030        │
│ Opérateur Alpha │───────│ Opérateur Beta  │───────│ Réseau Gamma    │
└─────────────────┘       └─────────────────┘       └─────────────────┘
```

Les lignes représentent des interconnexions possibles entre réseaux. Elles ne signifient pas automatiquement que tous les réseaux échangent toutes leurs routes.

### 4.2 Pourquoi BGP utilise-t-il les ASN ?

Un ASN permet d'identifier le système autonome à l'origine d'une annonce et de suivre les systèmes autonomes traversés par cette annonce. Cette information apparaît notamment dans l'attribut `AS_PATH`.

Lorsqu'un routeur eBGP reçoit un itinéraire dont le chemin contient déjà son propre ASN, il peut détecter une boucle inter-AS et rejeter cette route selon les règles BGP usuelles. Ce mécanisme est important, mais il ne constitue pas à lui seul une protection complète contre les erreurs de routage.

## 5. Les préfixes IP : comment annoncer une destination

BGP ne publie généralement pas une annonce individuelle pour chaque ordinateur d'un réseau. Il annonce des **préfixes IP** qui représentent des blocs d'adresses.

Par exemple :

- `203.0.113.0/24` représente un bloc IPv4 de 256 adresses au total, dont certaines adresses ont des usages particuliers selon les règles IP ;
- `198.51.100.0/24` représente un autre bloc IPv4 ;
- `2001:db8::/32` est un préfixe réservé aux exemples IPv6.

Ces préfixes appartiennent à des plages prévues pour la documentation et les exemples. Ils sont utiles dans ce cours mais ne doivent pas être annoncés sur l'Internet public.

Le suffixe `/24` est la longueur du préfixe : 24 bits identifient la partie réseau. CIDR permet de représenter des blocs de tailles différentes, plutôt que de se limiter aux anciennes classes A, B et C.

### 5.1 Annoncer un préfixe, c'est quoi ?

Supposons qu'AS65030 héberge le réseau `203.0.113.0/24` et annonce ce préfixe à AS65020. L'annonce signifie essentiellement : « Selon ma politique et mon état de routage, je peux acheminer du trafic vers ce préfixe. »

```text
AS65030 annonce : 203.0.113.0/24
             |
             v
AS65020 apprend une route vers 203.0.113.0/24
             |
             v
AS65020 peut, selon sa politique, réannoncer cette route à AS65010
```

BGP transporte des informations de joignabilité et des attributs. Il ne garantit pas à lui seul que le serveur fonctionne, que chaque routeur intermédiaire soit opérationnel ou que le trafic aboutisse effectivement.

### 5.2 Le plan de contrôle et le plan de transfert

Il est utile de distinguer deux fonctions :

- **Plan de contrôle :** les protocoles de routage, dont BGP, échangent et sélectionnent des routes.
- **Plan de transfert :** le routeur utilise les informations installées dans sa table de transfert pour envoyer réellement chaque paquet vers le prochain saut.

```text
BGP échange des annonces
          |
          v
Le routeur analyse et sélectionne une route
          |
          v
La route est éventuellement installée dans la table de routage
          |
          v
La table de transfert indique le prochain saut pour les paquets
```

Une route présente dans la table BGP n'est pas forcément celle qui sera utilisée pour transférer le trafic. Elle peut être rejetée par une politique, ne pas être la meilleure route BGP ou ne pas être installée dans la table de routage parce qu'une autre route est préférée.

## 6. Pourquoi ne pas utiliser uniquement OSPF ou un autre IGP ?

OSPF et IS-IS sont des protocoles de routage intérieur (IGP) conçus principalement pour organiser le routage au sein d'un réseau sous une même administration. Ils calculent des chemins selon leurs mécanismes et leurs métriques.

BGP est un protocole de routage interdomaines. Il permet à des systèmes autonomes indépendants d'échanger des routes et d'appliquer des politiques différentes en fonction de leurs relations commerciales, techniques et opérationnelles.

| Protocole | Usage typique | Logique principale |
|---|---|---|
| OSPF | Routage interne à une organisation | Calcul de chemins selon le coût OSPF |
| IS-IS | Routage interne, notamment chez certains opérateurs | Calcul de chemins selon les métriques IS-IS |
| eBGP | Échange de routes entre AS différents | Politique interdomaines et attributs BGP |
| iBGP | Diffusion de routes BGP à l'intérieur d'un même AS | Distribution des routes BGP au sein de l'AS |

BGP n'est pas nécessairement « meilleur » qu'OSPF ou l'inverse. Ils répondent à des besoins différents et peuvent fonctionner ensemble. Un opérateur peut, par exemple, utiliser IS-IS dans son cœur de réseau et eBGP pour communiquer avec d'autres opérateurs.

# Partie II — Les principes de fonctionnement de BGP

## 7. Qu'est-ce que BGP ?

**BGP** signifie *Border Gateway Protocol*. La version couramment employée pour le routage Internet est BGP-4, spécifiée notamment dans la RFC 4271.

BGP permet à des routeurs configurés comme voisins, ou *peers*, d'échanger des informations de joignabilité IP. Il fonctionne au-dessus de TCP, utilise normalement le port TCP `179` et conserve une session entre les voisins.

BGP est un protocole de type *path vector*. Pour chaque route, il peut transporter des attributs qui aident à déterminer la provenance, le chemin entre systèmes autonomes, le prochain saut et la politique associée.

BGP ne calcule pas le plus court chemin géographique à travers le monde. Il sélectionne une route parmi celles qui sont disponibles et acceptables selon les règles et les politiques du routeur.

## 8. eBGP et iBGP

Il existe deux grands modes de session BGP.

### 8.1 eBGP — External BGP

**eBGP** est utilisé entre deux systèmes autonomes différents.

```text
Routeur Alpha                         Routeur Beta
AS 65010                              AS 65020
    |                                     |
    └──────────── session eBGP ───────────┘
```

Exemple : un opérateur établit une session eBGP avec un fournisseur de transit ou un réseau participant à un peering.

### 8.2 iBGP — Internal BGP

**iBGP** est utilisé entre des routeurs appartenant au même système autonome.

```text
        AS 65010
┌───────────────────────────────┐
│ Routeur A  <---- iBGP ----> Routeur B │
└───────────────────────────────┘
```

iBGP permet notamment de distribuer à l'intérieur d'un AS des routes apprises par eBGP. Les réseaux de grande taille emploient différentes architectures, comme des sessions iBGP entre routeurs, des *route reflectors* ou des confédérations. Ces mécanismes sont approfondis aux niveaux supérieurs.

### 8.3 Tableau de comparaison

| Critère | eBGP | iBGP |
|---|---|---|
| Voisins | Deux AS différents | Même AS |
| Exemple | AS65010 vers AS65020 | Deux routeurs de l'AS65010 |
| Usage courant | Échange de routes entre réseaux | Distribution des routes BGP dans un AS |
| AS_PATH | L'ASN local est généralement ajouté à l'annonce sortante eBGP | Le chemin AS n'est normalement pas modifié lors d'une annonce iBGP standard |

## 9. Établissement d'une session BGP

La configuration d'un voisin ne suffit pas. Les deux routeurs doivent pouvoir communiquer, avoir une configuration compatible et accepter la session.

BGP utilise une machine à états. Les états les plus courants à reconnaître sont les suivants :

| État | Signification simplifiée |
|---|---|
| `Idle` | Le processus n'établit pas encore la session ou revient à l'état initial. |
| `Connect` | Le routeur tente d'établir la connexion TCP. |
| `Active` | Le routeur essaie de joindre son voisin ; cela ne signifie pas que BGP fonctionne. |
| `OpenSent` | Un message OPEN a été envoyé et le routeur attend la réponse appropriée. |
| `OpenConfirm` | Les paramètres BGP ont été échangés et le routeur attend la confirmation finale. |
| `Established` | La session est établie et les annonces BGP peuvent être échangées. |

L'objectif est généralement d'atteindre l'état `Established`.

### 9.1 Messages BGP principaux

- **OPEN :** présente les paramètres de la session BGP, dont l'ASN et les capacités prises en charge.
- **UPDATE :** annonce de nouvelles routes ou retire des routes précédemment annoncées.
- **KEEPALIVE :** maintient la session et confirme la disponibilité du voisin selon les temporisations configurées.
- **NOTIFICATION :** signale une erreur et entraîne généralement la fermeture de la session.
- **ROUTE-REFRESH :** permet de demander une nouvelle annonce de routes selon les capacités négociées, sans devoir nécessairement réinitialiser la session.

### 9.2 Pré-requis d'une session

Pour une session eBGP simple, vérifie au minimum :

1. La connectivité IP entre les adresses utilisées pour la session.
2. Les adresses IP des voisins configurées correctement sur chaque routeur.
3. L'ASN local et l'ASN distant corrects.
4. Le port TCP 179 et le processus BGP non bloqués par un pare-feu ou une ACL.
5. Les éventuels paramètres d'authentification et de TTL compatibles.
6. Les filtres et politiques qui autorisent les routes attendues.

Une session `Established` indique que la relation BGP est établie. Elle ne garantit pas qu'une route utile est annoncée ou acceptée.

## 10. Comment une route BGP se propage

Considérons trois AS :

```text
AS65010                 AS65020                 AS65030
  Alpha ------------------ Beta ------------------ Gamma
```

Supposons que Gamma annonce le préfixe `198.51.100.0/24` à Beta. Dans une session eBGP standard, Beta ajoute son ASN à l'AS_PATH lorsqu'il réannonce cette route à Alpha.

Alpha peut alors voir, de façon simplifiée :

```text
Préfixe : 198.51.100.0/24
AS_PATH : 65020 65030
```

Cette représentation indique que la route a été annoncée depuis AS65030 puis transmise par AS65020 avant d'arriver à Alpha. L'affichage exact dépend du routeur et de la manière dont les champs sont présentés.

### 10.1 Prévention des boucles par AS_PATH

Si un routeur voit son propre ASN dans l'AS_PATH d'une route reçue via eBGP, il rejette normalement cette route pour éviter une boucle inter-AS. Ce mécanisme ne remplace pas les politiques de filtrage : une annonce erronée peut tout de même être propagée si les protections sont insuffisantes.

### 10.2 BGP n'annonce pas automatiquement tout ce qui est connecté

Dans de nombreuses configurations, l'administrateur choisit explicitement les routes à annoncer. Une route connectée présente dans le routeur n'est pas automatiquement propagée à tous les voisins BGP.

Il faut distinguer :

- la route présente dans la table de routage locale ;
- la route prise en compte par le processus BGP ;
- la route sélectionnée comme meilleure route ;
- la route envoyée à un voisin après application de la politique sortante.

Une route annoncée peut ensuite être rejetée par le voisin selon sa propre politique.

# Partie III — Peering, transit et points d'échange Internet

## 11. Qu'est-ce que le peering ?

Le **peering** est une relation d'interconnexion dans laquelle deux réseaux échangent du trafic destiné à leurs propres réseaux et, selon leur accord, à leurs clients respectifs. Les conditions techniques et commerciales sont définies entre les participants.

Le peering peut se faire :

- par une liaison directe entre deux réseaux ;
- au sein d'un centre de données ou d'une infrastructure d'interconnexion ;
- via un Internet Exchange Point (IXP).

Un peering peut être gratuit ou payant : il n'existe pas de règle universelle disant que tout peering est sans frais. Les accords varient selon les réseaux, les volumes de trafic, les lieux d'interconnexion et les conditions contractuelles.

### 11.1 Exemple de peering direct

```text
        AS65010                           AS65020
   Opérateur Alpha                    Opérateur Beta
          |                                  |
          └──────── liaison d'interconnexion ┘
                        |
                   Session eBGP
```

Les réseaux peuvent échanger les préfixes autorisés par leurs politiques. Le peering n'implique pas qu'un opérateur transmettra tout le trafic de l'autre vers l'ensemble d'Internet.

## 12. Qu'est-ce que le transit IP ?

Un **fournisseur de transit IP** vend un service permettant à un client d'atteindre une grande partie ou la totalité de l'Internet routable, selon le service contracté et les routes fournies.

```text
AS client
    |
    | service de transit IP
    v
AS fournisseur de transit
    |
    v
Autres réseaux accessibles par le fournisseur
```

Le client reçoit généralement des routes du fournisseur : par exemple, une route par défaut ou un ensemble beaucoup plus complet de routes Internet. Le fournisseur applique aussi des politiques à ce qu'il accepte et à ce qu'il annonce au client.

### 12.1 Peering et transit : comparaison

| Élément | Peering | Transit IP |
|---|---|---|
| Objectif | Échanger le trafic autorisé entre les réseaux participants et leurs clients selon l'accord | Fournir l'accès à d'autres réseaux accessibles par le fournisseur |
| Portée des routes | Généralement limitée aux réseaux couverts par l'accord | Généralement beaucoup plus large, selon le contrat |
| Modèle économique | Peut être gratuit ou payant | Généralement un service payé |
| Politique | Définie entre les pairs | Définie par le contrat client-fournisseur et les politiques de routage |

Le peering et le transit peuvent coexister chez le même opérateur. Un opérateur peut échanger directement du trafic avec certains réseaux et acheter du transit pour atteindre le reste d'Internet.

## 13. Internet Exchange Point (IXP)

Un **Internet Exchange Point**, ou **IXP**, est une infrastructure qui permet à plusieurs systèmes autonomes indépendants de s'interconnecter pour échanger du trafic Internet. Il fournit généralement une infrastructure de commutation de niveau 2 et peut proposer des services complémentaires.

Un IXP n'est pas, en soi, un fournisseur de transit. La présence de plusieurs réseaux au même IXP ne crée pas automatiquement une session BGP entre tous les participants : chaque réseau décide avec qui il établit des sessions et quelles routes il accepte ou annonce.

### 13.1 Exemple d'un IXP

```text
               Infrastructure de commutation IXP
              ┌───────────────────────────────┐
AS65010 ──────┤                               ├────── AS65020
              │          réseau L2            │
AS65030 ──────┤                               ├────── AS65040
              └───────────────────────────────┘
```

Les participants peuvent établir des peerings bilatéraux entre eux. Certains IXP fournissent aussi un **route server** : les participants peuvent établir une session BGP avec ce serveur afin d'échanger des routes avec plusieurs autres participants selon les politiques du service. Le trafic des participants ne traverse normalement pas le route server lui-même ; il continue à passer directement par l'infrastructure de commutation de l'IXP.

### 13.2 Pourquoi les IXP sont-ils importants ?

Un IXP peut aider à :

- réduire le nombre d'intermédiaires pour certains chemins ;
- réduire la latence vers certains réseaux ;
- diminuer certains coûts de transit ;
- améliorer la résilience grâce à une interconnexion supplémentaire ;
- garder davantage de trafic local dans une région lorsque les réseaux et les routes le permettent.

Ces avantages ne sont pas automatiques. Ils dépendent des réseaux présents, des accords, de la qualité des interconnexions et de la configuration de routage.

## 14. Peering bilatéral et multilatéral

Dans un peering **bilatéral**, deux AS négocient et configurent directement leur relation BGP.

Dans un peering **multilatéral**, un participant peut échanger des routes avec plusieurs autres participants à travers une plateforme ou un service commun, souvent un route server d'IXP.

Dans les deux cas, les politiques d'annonces restent importantes. Une session BGP ne doit pas être considérée comme une autorisation d'annoncer tous les préfixes dont un réseau a connaissance.

# Partie IV — Lire les routes et comprendre la sélection BGP

## 15. Les informations associées à une route BGP

Une route BGP comprend un préfixe de destination et des attributs. Les attributs permettent aux routeurs d'évaluer la provenance d'une route et de prendre des décisions de politique.

### 15.1 `AS_PATH`

L'`AS_PATH` est la liste des systèmes autonomes parcourus par l'annonce dans les annonces eBGP habituelles. Il aide à détecter certaines boucles et sert souvent à appliquer des politiques.

Exemple :

```text
Préfixe : 198.51.100.0/24
AS_PATH : 65020 65030
```

Une politique peut, par exemple, préférer une route avec un AS_PATH plus court. Cela ne signifie pas que BGP choisit toujours le chemin avec le moins d'ASN : d'autres critères peuvent passer avant.

### 15.2 `NEXT_HOP`

`NEXT_HOP` indique l'adresse IP du prochain saut vers lequel le trafic doit être envoyé pour cette route. Le prochain saut doit être joignable selon le routage local ; sinon la route ne pourra généralement pas être utilisée pour transférer le trafic.

Une session BGP peut donc être établie alors qu'une route reçue n'est pas exploitable parce que son prochain saut est inaccessible.

### 15.3 `LOCAL_PREF`

`LOCAL_PREF` est une préférence utilisée au sein d'un AS pour comparer des routes BGP. Dans les politiques courantes, une valeur plus élevée est préférée. Il sert souvent à choisir le point de sortie d'un AS vers une destination.

Il n'est normalement pas transmis à un voisin eBGP comme attribut standard transporté vers les autres AS ; il sert principalement à la politique interne à l'AS.

### 15.4 `MED`

`MED` (*Multi-Exit Discriminator*) permet généralement à un AS d'indiquer à un AS voisin une préférence relative entre plusieurs points d'entrée vers son réseau. Lorsqu'il est comparé, une valeur plus faible est souvent préférée. Les règles exactes de comparaison dépendent de la configuration et de l'implémentation.

### 15.5 `ORIGIN`

L'attribut `ORIGIN` indique le type d'origine de l'annonce selon les catégories BGP, généralement affichées comme `IGP`, `EGP` ou `INCOMPLETE`. Ces libellés ne désignent pas simplement le protocole IGP actuellement utilisé dans le réseau ; ils représentent un attribut de route BGP.

### 15.6 `COMMUNITY`

Une **community BGP** est une étiquette attachée à une route pour simplifier les politiques. Les opérateurs peuvent utiliser des communities pour signaler des routes à leurs routeurs, exprimer des préférences ou appliquer des actions, selon la politique documentée par l'opérateur.

La signification d'une community dépend du réseau qui l'interprète. Il ne faut pas supposer que n'importe quelle community possède une signification universelle.

## 16. Comment BGP choisit-il une meilleure route ?

Un routeur peut apprendre plusieurs routes vers le même préfixe. Il doit en sélectionner une ou plusieurs selon les mécanismes et la politique configurée. Le résultat dépend notamment de l'implémentation, des attributs, des politiques locales et des possibilités de partage de charge.

Dans un scénario pédagogique, on peut retenir les idées suivantes :

1. Les routes rejetées par une politique ne participent pas à la sélection normale.
2. Le routeur compare les attributs selon son algorithme de sélection.
3. `LOCAL_PREF` est souvent utilisé pour choisir une sortie préférée au sein d'un AS.
4. La longueur d'`AS_PATH` peut intervenir, mais elle n'est pas toujours le critère principal.
5. Le coût IGP vers le prochain saut peut aider à départager des routes dans certains cas.
6. La route sélectionnée par BGP doit encore être installable dans la table de routage.

L'ordre exact des critères n'est pas identique dans tous les constructeurs et peut varier selon la configuration. Les opérateurs utilisent BGP pour appliquer des politiques, pas seulement pour minimiser le nombre d'AS traversés.

### 16.1 Exemple simple

Un routeur apprend deux routes vers `198.51.100.0/24` :

| Route | `LOCAL_PREF` | `AS_PATH` simplifié |
|---|---:|---|
| Via le fournisseur A | 200 | `65020 65030` |
| Via le fournisseur B | 100 | `65040` |

Même si le chemin via B contient moins d'ASN, une politique qui préfère le `LOCAL_PREF` plus élevé peut sélectionner la route via A. Cet exemple illustre un principe de politique ; il ne prétend pas décrire chaque détail de l'algorithme de chaque constructeur.

## 17. Pourquoi le chemin aller peut-il être différent du chemin retour ?

Le routage Internet n'est pas obligatoirement symétrique. Le réseau A peut envoyer du trafic vers B par un fournisseur, tandis que B peut renvoyer le trafic vers A par un autre opérateur.

```text
Trafic aller :  Réseau A ─────> Fournisseur X ─────> Réseau B
Trafic retour : Réseau B ─────> Fournisseur Y ─────> Réseau A
```

Les deux chemins peuvent être différents parce que chaque AS applique ses propres politiques BGP. Cette asymétrie est normale sur Internet, mais elle peut compliquer le dépannage, l'analyse des performances ou certains mécanismes de sécurité.

## 18. BGP, table BGP et table de routage

Les plateformes réseau distinguent généralement plusieurs ensembles de données :

- les routes reçues des voisins ;
- les routes traitées après application des politiques ;
- la meilleure route BGP pour chaque préfixe, selon les critères de sélection ;
- les routes installées dans la table de routage générale ;
- les informations utilisées par le matériel pour transférer les paquets.

Les noms exacts et les commandes d'affichage diffèrent selon le constructeur. Cette distinction explique pourquoi une route peut apparaître dans une sortie BGP sans être utilisée pour le transfert de paquets.

# Partie V — Sécurité et bonnes pratiques d'exploitation

## 19. Pourquoi BGP doit-il être sécurisé ?

BGP repose largement sur la confiance et les politiques configurées entre voisins. Une annonce incorrecte ou malveillante peut détourner du trafic, rendre des destinations injoignables ou conduire des paquets vers un réseau qui ne devrait pas les recevoir.

Les erreurs peuvent être accidentelles : un préfixe trop large est annoncé, un filtre est absent, une route client est réannoncée à un autre fournisseur sans autorisation ou une politique est appliquée dans le mauvais sens.

### 19.1 Détournement de préfixe (*prefix hijack*)

Un détournement de préfixe se produit lorsqu'un réseau annonce de manière non autorisée ou incorrecte un préfixe associé à un autre réseau. Certains routeurs peuvent considérer cette annonce comme une route candidate et envoyer du trafic vers le mauvais AS.

### 19.2 Fuite de routes (*route leak*)

Une fuite de routes se produit lorsqu'un réseau propage des routes au-delà de ce que prévoit sa politique ou son accord. Par exemple, des routes apprises d'un fournisseur peuvent être annoncées à un autre fournisseur alors que cette propagation n'est pas autorisée.

### 19.3 Mesures de protection élémentaires

Les opérateurs mettent en œuvre plusieurs protections complémentaires :

- **Filtres de préfixes en entrée et en sortie :** n'accepter et n'annoncer que les préfixes attendus.
- **Contrôle de l'AS_PATH :** vérifier que les chemins reçus respectent la politique prévue.
- **Limite de nombre de préfixes (*max-prefix*) :** éviter qu'un voisin annonce soudainement un nombre anormal de routes sans contrôle.
- **Protection du plan de contrôle :** limiter l'accès aux sessions BGP et protéger les routeurs concernés.
- **Authentification ou protection de session lorsque c'est adapté :** appliquer une configuration cohérente des deux côtés.
- **ROA et validation RPKI de l'origine :** vérifier si l'AS d'origine annoncé est autorisé à annoncer un préfixe selon les données RPKI disponibles.
- **Surveillance :** détecter les variations anormales des annonces et documenter les changements.

Aucune mesure unique ne règle tous les problèmes BGP. La validation RPKI de l'origine, par exemple, aide à détecter certaines annonces incorrectes, mais ne valide pas à elle seule chaque AS du chemin ni toutes les politiques commerciales.

### 19.4 Le filtrage doit correspondre au rôle du voisin

Un client, un fournisseur de transit et un pair de peering ne doivent pas nécessairement annoncer ou recevoir les mêmes ensembles de routes. Les filtres doivent refléter la relation entre les réseaux et les préfixes que le voisin est autorisé à annoncer.

**Ne configure jamais une session de production en acceptant indistinctement toutes les routes entrantes et en les réannonçant à tous les voisins.** Les exemples de ce cours sont limités à un laboratoire et à des préfixes de documentation.

# Partie VI — Travaux pratiques

## 20. TP : créer un peering eBGP entre deux routeurs

### 20.1 Objectif

Créer une session eBGP entre deux routeurs, annoncer un préfixe de chaque côté et vérifier que chaque routeur apprend le préfixe de l'autre.

### 20.2 Environnement conseillé

Utilise un laboratoire isolé, par exemple une maquette Cisco dans Packet Tracer si les fonctions nécessaires sont prises en charge, ou un environnement Cisco IOS/IOSv, GNS3, EVE-NG ou CML. Les commandes ci-dessous utilisent une syntaxe de type Cisco IOS. Le nom des interfaces et certaines commandes d'affichage peuvent varier selon la plateforme.

**Ne réalise pas ce TP sur des routeurs connectés à l'Internet public.** Les préfixes du TP sont réservés à la documentation et ne doivent pas être annoncés sur Internet.

### 20.3 Topologie

```text
      Réseau local de R1                              Réseau local de R2
       203.0.113.0/24                                  198.51.100.0/24
              |                                                |
        Loopback0 R1                                    Loopback0 R2
        203.0.113.1/24                                  198.51.100.1/24
              |                                                |
        ┌───────────┐       192.0.2.0/30             ┌───────────┐
        │ R1        │ .1 ─────────────────────── .2 │ R2        │
        │ AS 65010  │       eBGP sur TCP/179         │ AS 65020  │
        └───────────┘                                └───────────┘
```

Les plages `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont réservées aux exemples et à la documentation. Elles ne représentent pas des adresses publiques attribuées à un opérateur.

### 20.4 Plan d'adressage

| Équipement | Interface | Adresse | Rôle |
|---|---|---|---|
| R1 | G0/0 | `192.0.2.1/30` | Lien vers R2 |
| R2 | G0/0 | `192.0.2.2/30` | Lien vers R1 |
| R1 | Loopback0 | `203.0.113.1/24` | Préfixe annoncé par R1 |
| R2 | Loopback0 | `198.51.100.1/24` | Préfixe annoncé par R2 |
| R1 | BGP | ASN `65010` | Système autonome local de laboratoire |
| R2 | BGP | ASN `65020` | Système autonome local de laboratoire |

### 20.5 Configuration de R1

Adapte le nom `GigabitEthernet0/0` à la plateforme utilisée.

```text
enable
configure terminal

interface GigabitEthernet0/0
 description Lien-eBGP-vers-R2
 ip address 192.0.2.1 255.255.255.252
 no shutdown
 exit

interface Loopback0
 description Prefixe-de-test-annonce-par-R1
 ip address 203.0.113.1 255.255.255.0
 exit

router bgp 65010
 bgp log-neighbor-changes
 neighbor 192.0.2.2 remote-as 65020
 network 203.0.113.0 mask 255.255.255.0
 exit

end
write memory
```

### 20.6 Configuration de R2

```text
enable
configure terminal

interface GigabitEthernet0/0
 description Lien-eBGP-vers-R1
 ip address 192.0.2.2 255.255.255.252
 no shutdown
 exit

interface Loopback0
 description Prefixe-de-test-annonce-par-R2
 ip address 198.51.100.1 255.255.255.0
 exit

router bgp 65020
 bgp log-neighbor-changes
 neighbor 192.0.2.1 remote-as 65010
 network 198.51.100.0 mask 255.255.255.0
 exit

end
write memory
```

**Point important :** sur Cisco IOS, une instruction BGP `network` annonce le préfixe uniquement si une route correspondante, avec le masque attendu, existe déjà dans la table de routage. Dans ce TP, l'interface Loopback fournit cette route connectée. Les commandes exactes peuvent varier selon le système réseau.

### 20.7 Étape 1 — Vérifier le lien IP

Sur R1 :

```text
show ip interface brief
ping 192.0.2.2
```

Sur R2 :

```text
show ip interface brief
ping 192.0.2.1
```

Le lien doit être actif et les adresses voisines doivent répondre. Si le ping échoue, résous d'abord le problème IP avant de diagnostiquer BGP.

### 20.8 Étape 2 — Vérifier la présence des préfixes locaux

Sur R1 :

```text
show ip route 203.0.113.0
```

Sur R2 :

```text
show ip route 198.51.100.0
```

Chaque routeur doit disposer de sa route locale de test. Si le préfixe n'existe pas exactement dans la table de routage, l'annonce configurée par la commande `network` risque de ne pas être générée.

### 20.9 Étape 3 — Vérifier l'état BGP

Sur R1 et R2 :

```text
show ip bgp summary
```

La session doit finir par atteindre l'état `Established`. Selon la version du logiciel, la colonne affichée peut présenter un état ou un nombre de préfixes reçus ; interprète la sortie avec la documentation de la plateforme.

Pour examiner les routes BGP :

```text
show ip bgp
```

Sur les versions IOS qui prennent en charge ces commandes, tu peux aussi consulter les routes reçues ou annoncées à un voisin avec les commandes `show ip bgp neighbors ... received-routes` ou `show ip bgp neighbors ... advertised-routes`. Certaines commandes nécessitent des options supplémentaires, et leur disponibilité dépend de la plateforme et de sa configuration.

### 20.10 Étape 4 — Vérifier les routes apprises

Sur R1, cherche une route vers :

```text
198.51.100.0/24
```

Sur R2, cherche une route vers :

```text
203.0.113.0/24
```

Utilise notamment :

```text
show ip bgp
show ip route bgp
```

Le préfixe appris depuis le voisin doit apparaître dans BGP et, s'il est sélectionné et installable, dans la table de routage. Le format précis dépend du logiciel et de sa version.

### 20.11 Étape 5 — Tester la connectivité des préfixes

Depuis R1, essaie :

```text
ping 198.51.100.1
```

Depuis R2, essaie :

```text
ping 203.0.113.1
```

Si le ping échoue alors que la session BGP est établie, vérifie les routes apprises et les routes de retour. Dans cette maquette, les deux préfixes doivent être annoncés et appris pour que la communication soit possible dans les deux sens. Selon l'environnement, le filtrage ICMP ou le comportement de la plateforme peut influencer le résultat.

### 20.12 Résultat attendu

À la fin du TP :

- le lien entre R1 et R2 fonctionne ;
- la session eBGP atteint `Established` ;
- R1 annonce `203.0.113.0/24` et apprend `198.51.100.0/24` ;
- R2 annonce `198.51.100.0/24` et apprend `203.0.113.0/24` ;
- les routes sont visibles dans les tables correspondantes ;
- les pings entre les adresses de Loopback fonctionnent si la maquette et les politiques de filtrage les autorisent.

## 21. Dépannage de base

### Cas 1 — La session reste en `Idle` ou `Active`

Vérifie les adresses des voisins, la connectivité IP, les ASN configurés, le port TCP 179 et les règles de filtrage. L'état `Active` signifie que le routeur tente de joindre le voisin ; ce n'est pas une confirmation de réussite.

### Cas 2 — La session est `Established`, mais aucune route attendue n'apparaît

Vérifie que le préfixe local existe dans la table de routage, que la commande `network` correspond au bon préfixe et au bon masque, que l'annonce est autorisée par les politiques sortantes et que le voisin l'accepte.

### Cas 3 — La route apparaît dans BGP mais pas dans la table de routage

Vérifie si une route plus préférée existe, si le `NEXT_HOP` est joignable et si une politique ou une condition d'installation empêche la route d'entrer dans la table de routage.

### Cas 4 — Une route est installée, mais le ping échoue

Vérifie le prochain saut, la route de retour, les ACL, les pare-feu, les adresses de destination et le fonctionnement des interfaces intermédiaires. Le routage BGP et l'accessibilité applicative sont liés, mais ils ne sont pas identiques.

### Cas 5 — Le voisin reçoit trop de routes ou des préfixes inattendus

Vérifie les filtres de préfixes, la politique d'annonce, les limites de préfixes et les routes que chaque voisin est autorisé à annoncer. Dans un vrai réseau, cette vérification est une étape de sécurité importante, pas seulement une mesure de dépannage.

## 22. Commandes de révision

Les commandes suivantes sont fréquentes sur les plateformes Cisco IOS/IOS-XE ; leur disponibilité et leur syntaxe exacte peuvent varier :

| Commande | Utilité |
|---|---|
| `show ip interface brief` | Vérifier l'état et l'adressage des interfaces |
| `show ip route` | Consulter la table de routage IPv4 |
| `show ip route <préfixe>` | Examiner la route vers un préfixe précis |
| `show ip bgp summary` | Contrôler l'état des voisins BGP |
| `show ip bgp` | Voir les routes BGP et certains de leurs attributs |
| `show ip route bgp` | Afficher les routes BGP installées dans la table de routage, selon la plateforme |
| `ping <adresse>` | Vérifier la connectivité IP de base |
| `traceroute <adresse>` | Examiner les sauts visibles sur un chemin IP, si autorisé |

Ne copie pas aveuglément une commande d'un autre constructeur : vérifie la documentation correspondant au système d'exploitation réseau utilisé.

# Partie VII — Exercices corrigés

## 23. Exercice 1 — AS, ASN et préfixes

**Question 1.** Que signifie AS ?

**Question 2.** À quoi sert un ASN ?

**Question 3.** Que représente le préfixe `203.0.113.0/24` dans ce cours ?

**Question 4.** Peut-on utiliser les ASN 65010 et 65020 comme identifiants publics uniques sur Internet ?

### Correction

1. AS signifie *Autonomous System*, ou système autonome : un ensemble de réseaux sous une administration commune avec une politique de routage cohérente vis-à-vis des autres réseaux.
2. L'ASN identifie ce système autonome dans les échanges de routage interdomaines.
3. C'est un préfixe IPv4 d'exemple réservé à la documentation. Il sert à illustrer une annonce BGP, pas à désigner un réseau public réel.
4. Non. Ces deux numéros appartiennent à la plage privée. Ils sont destinés à des usages privés ou de laboratoire et ne sont pas des identifiants publics uniques.

## 24. Exercice 2 — eBGP ou iBGP ?

Indique le type de session dans chaque situation.

1. Un routeur de l'AS65010 établit une session avec un routeur de l'AS65020.
2. Deux routeurs de l'AS65010 échangent des routes BGP.
3. Un opérateur annonce ses routes à un fournisseur de transit qui possède un ASN différent.

### Correction

1. eBGP, car les voisins sont dans deux AS différents.
2. iBGP, car les deux routeurs appartiennent au même AS.
3. eBGP, car le client et le fournisseur appartiennent normalement à des AS différents.

## 25. Exercice 3 — Peering ou transit ?

Un opérateur régional échange directement certaines routes avec un réseau de contenu à un IXP. Pour atteindre les réseaux qu'il ne joint pas grâce à ses peerings, il utilise aussi un fournisseur de transit.

**Question :** l'opérateur fait-il du peering, du transit ou les deux ? Explique.

### Correction

Il utilise les deux. Le peering lui permet d'échanger les routes couvertes par les accords conclus avec les autres participants. Le transit lui fournit une portée d'accès à d'autres réseaux selon le service contracté. Ces deux stratégies sont complémentaires.

## 26. Exercice 4 — Lire un AS_PATH

Un routeur de l'AS65010 apprend le préfixe `198.51.100.0/24` avec l'AS_PATH suivant :

```text
65020 65030
```

**Question 1.** Quels systèmes autonomes figurent dans le chemin annoncé ?

**Question 2.** Pourquoi ce chemin peut-il aider à éviter une boucle ?

### Correction

1. Le chemin contient les ASN 65020 et 65030. Dans cet exemple, la route provient de l'AS65030 et a été transmise par l'AS65020 avant d'arriver à l'AS65010.
2. Si un routeur détecte son propre ASN dans l'AS_PATH reçu via eBGP, il rejette normalement la route afin d'éviter une boucle de routage inter-AS.

## 27. Exercice 5 — Pourquoi la route attendue n'est-elle pas installée ?

Une session BGP est `Established`. La commande BGP affiche le préfixe `198.51.100.0/24`, mais la commande de table de routage ne montre pas ce préfixe comme route BGP active.

Cite au moins trois vérifications possibles.

### Correction

Il faut notamment vérifier :

- si une route concurrente plus préférée existe ;
- si le `NEXT_HOP` est joignable ;
- si une politique empêche la sélection ou l'installation de la route ;
- si le logiciel réseau distingue la route reçue, la meilleure route BGP et la route installée ;
- si une route de même préfixe avec une autre origine est déjà installée.

Une session établie n'implique pas que chaque route reçue sera sélectionnée et utilisée.

## 28. Exercice 6 — Choisir la meilleure route

Un routeur apprend deux routes vers le même préfixe :

| Route | `LOCAL_PREF` | Nombre d'ASN dans l'AS_PATH |
|---|---:|---:|
| A | 200 | 2 |
| B | 100 | 1 |

Dans une politique où le `LOCAL_PREF` est comparé avant la longueur de l'AS_PATH, quelle route sera favorisée ?

### Correction

La route A sera favorisée parce que son `LOCAL_PREF` est plus élevé. Cet exercice illustre le rôle des politiques locales. L'ordre et les critères effectifs dépendent de l'implémentation et de la configuration du routeur.

# Partie VIII — Défi final corrigé

## 29. Défi : concevoir une interconnexion simple entre deux AS

### Scénario

Un petit opérateur, AS65010, doit échanger des routes avec un réseau partenaire, AS65020. Les réseaux souhaitent configurer une session eBGP de laboratoire et tester l'apprentissage réciproque de leurs préfixes.

Le plan d'adressage est le suivant :

| Élément | Valeur |
|---|---|
| Lien entre routeurs | `192.0.2.0/30` |
| Adresse du routeur AS65010 | `192.0.2.1/30` |
| Adresse du routeur AS65020 | `192.0.2.2/30` |
| Préfixe annoncé par AS65010 | `203.0.113.0/24` |
| Préfixe annoncé par AS65020 | `198.51.100.0/24` |

### Travail demandé

1. Expliquer pourquoi il s'agit d'eBGP.
2. Donner les adresses de voisinage à configurer de chaque côté.
3. Indiquer les vérifications nécessaires avant de diagnostiquer BGP.
4. Citer les commandes qui permettent de vérifier l'état de la session et les routes.
5. Expliquer pourquoi une session `Established` peut ne pas suffire à obtenir une connectivité IP de bout en bout.
6. Donner trois protections qu'il faudrait prévoir avant une interconnexion de production.

### Correction détaillée

**1. Type de session**

Il s'agit d'eBGP parce que les deux routeurs appartiennent à des systèmes autonomes différents : AS65010 et AS65020.

**2. Voisins BGP**

Sur le routeur AS65010, le voisin est `192.0.2.2` et l'ASN distant est `65020`. Sur le routeur AS65020, le voisin est `192.0.2.1` et l'ASN distant est `65010`.

**3. Vérifications préalables**

Il faut vérifier que les interfaces sont actives, que l'adressage et le masque sont corrects, que les deux adresses de voisin se joignent en IP, que TCP 179 n'est pas bloqué et que les ASN configurés correspondent à ceux des deux routeurs.

**4. Vérification BGP**

Avec une CLI de type Cisco IOS, les commandes typiques sont :

```text
show ip bgp summary
show ip bgp
show ip route
show ip route bgp
```

On doit également vérifier que les préfixes de test existent dans les tables de routage locales et qu'ils sont bien annoncés au voisin. Les commandes précises peuvent varier selon la plateforme.

**5. Pourquoi `Established` ne suffit-il pas ?**

`Established` indique que la session est formée, pas que les routes attendues ont été annoncées, acceptées, sélectionnées puis installées. De plus, le trafic doit avoir un chemin aller et un chemin retour fonctionnels ; les ACL, les pare-feu ou les erreurs de prochain saut peuvent encore empêcher la communication.

**6. Protections de production**

Parmi les mesures à prévoir :

- appliquer des filtres entrants et sortants limitant les préfixes autorisés ;
- définir une limite de préfixes adaptée au rôle du voisin et surveiller les changements ;
- contrôler l'AS_PATH et les politiques d'annonce ;
- protéger l'accès au plan de contrôle et à la session BGP ;
- envisager la validation de l'origine par RPKI et mettre en place une surveillance opérationnelle.

Une vraie interconnexion exige en plus une coordination avec le pair, une documentation des préfixes autorisés, la validation de la politique de routage et un plan de retour arrière.

# Partie IX — Synthèse et vocabulaire

## 30. Les dix idées à retenir

1. Internet est un ensemble de réseaux indépendants interconnectés.
2. Un AS est identifié par un ASN dans le routage interdomaines.
3. Un préfixe IP représente un bloc d'adresses qui peut être annoncé comme destination.
4. BGP échange des informations de joignabilité entre routeurs voisins.
5. BGP utilise normalement TCP sur le port 179.
6. eBGP relie des AS différents ; iBGP distribue les routes BGP au sein d'un même AS.
7. `AS_PATH` aide à comprendre le chemin inter-AS et à détecter certaines boucles.
8. Le peering échange les routes prévues par un accord ; le transit donne accès à d'autres réseaux selon le service contracté.
9. Un IXP facilite l'interconnexion, mais ne crée pas automatiquement des sessions BGP entre tous ses membres.
10. Une session établie et une route visible ne garantissent pas à elles seules la connectivité complète : les annonces, les politiques, la table de routage et le chemin de retour comptent aussi.

## 31. Glossaire

| Terme | Définition |
|---|---|
| AS | *Autonomous System*, ensemble de réseaux sous une administration commune et une politique de routage cohérente vis-à-vis des autres réseaux |
| ASN | Numéro identifiant un système autonome |
| BGP | Protocole de routage interdomaines qui échange des informations de joignabilité IP |
| eBGP | Session BGP entre deux AS différents |
| iBGP | Session BGP entre routeurs du même AS |
| Préfixe | Bloc d'adresses IP représenté par une adresse réseau et une longueur CIDR |
| Peering | Interconnexion permettant l'échange de trafic entre réseaux selon un accord |
| Transit IP | Service donnant accès à d'autres réseaux via un fournisseur |
| IXP | Infrastructure permettant à plusieurs réseaux indépendants de s'interconnecter |
| Route server | Service IXP facilitant l'échange de routes BGP entre participants ; il ne transporte généralement pas lui-même le trafic utilisateur |
| `AS_PATH` | Attribut qui décrit les systèmes autonomes traversés par une annonce BGP |
| `NEXT_HOP` | Adresse du prochain saut vers lequel envoyer le trafic pour une route |
| `LOCAL_PREF` | Attribut de préférence généralement utilisé à l'intérieur d'un AS ; une valeur plus élevée est habituellement préférée |
| `MED` | Attribut pouvant influencer le choix du point d'entrée dans un AS voisin ; une valeur plus faible est souvent préférée lorsque la comparaison s'applique |
| RIB | Base de données de routage contenant des informations sur les routes, selon le contexte d'utilisation du terme |
| FIB | Base de transfert utilisée pour acheminer les paquets vers le prochain saut |
| ROA | Objet RPKI déclarant qu'un ASN est autorisé à annoncer un préfixe, avec une longueur maximale autorisée |
| Route leak | Propagation d'une route en dehors de la politique ou de la relation prévue |
| Prefix hijack | Annonce non autorisée ou incorrecte d'un préfixe pouvant détourner du trafic |

## 32. Pour poursuivre vers le niveau intermédiaire

Le niveau intermédiaire approfondira la configuration de politiques BGP, les filtres de préfixes, `LOCAL_PREF`, `MED`, les communities, le multihoming, la route par défaut, la sélection de routes, les annonces IPv4 et IPv6, les route servers d'IXP ainsi que les méthodes de dépannage plus structurées.

Le niveau expert pourra ensuite traiter des architectures BGP de grande taille, des route reflectors, des politiques complexes, de la résilience opérateur, de l'ingénierie de trafic, de la validation RPKI, de la prévention des fuites de routes et de la conception d'un réseau opérateur.

## 33. Références techniques

Ces références permettent d'approfondir les notions abordées dans le cours :

- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : spécification de base du protocole BGP. https://www.rfc-editor.org/rfc/rfc4271.html
- **RFC 6996 — Autonomous System (AS) Reservation for Private Use** : plages d'ASN réservées aux usages privés. https://www.rfc-editor.org/rfc/rfc6996.html
- **IANA — Autonomous System Numbers** : registre des ASN et plages réservées. https://www.iana.org/assignments/as-numbers
- **RFC 5737 — IPv4 Address Blocks Reserved for Documentation** : plages IPv4 d'exemple utilisées dans le TP. https://www.rfc-editor.org/rfc/rfc5737.html
- **RFC 7454 — BGP Operations and Security** : recommandations d'exploitation et de sécurisation de BGP. https://www.rfc-editor.org/rfc/rfc7454.html
- **Internet Society — Peering and Internet Exchange Points** : aperçu du peering et des IXP. https://www.internetsociety.org/action-plan/sustainable-peering-infrastructure/

Le présent cours sert à l'apprentissage et à la réalisation de maquettes. Toute interconnexion réelle doit être conçue en fonction de la politique de routage, des accords entre réseaux, de la documentation des préfixes autorisés et des recommandations de sécurité applicables.
