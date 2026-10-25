# BGP Peering & Internet — Intermédiaire

## Mise en contexte : passer de la compréhension à l'ingénierie du routage

Au niveau débutant, tu as découvert le rôle de BGP, les systèmes autonomes, les préfixes IP, les sessions eBGP et iBGP, ainsi que la différence entre peering et transit IP. À présent, il faut comprendre comment un opérateur contrôle précisément ce qu'il apprend, ce qu'il préfère et ce qu'il annonce à ses voisins.

Dans un réseau réel, établir une session BGP n'est que le début. Un opérateur doit définir une politique d'importation, une politique d'exportation, filtrer les préfixes, contrôler le comportement des routes, gérer plusieurs fournisseurs, surveiller les annonces et limiter les conséquences d'une erreur.

Ce cours étudie ces opérations à un niveau intermédiaire. Les exemples utilisent des organisations fictives et des plages IP réservées à la documentation. Les configurations Cisco IOS sont pédagogiques : la syntaxe et certaines fonctions varient selon le constructeur, la version et la famille d'adresses activée. Une variante conceptuelle avec FRRouting est également présentée dans les exercices.

> **Fil conducteur :** BGP ne consiste pas seulement à apprendre des routes. Il permet à un opérateur de mettre en œuvre une politique de routage. La politique détermine quelles routes sont acceptées, lesquelles sont préférées et lesquelles peuvent être propagées.

## Objectifs pédagogiques

À la fin de ce cours, tu seras capable de :

- expliquer la différence entre politique d'importation et politique d'exportation BGP ;
- lire et interpréter les attributs `AS_PATH`, `NEXT_HOP`, `LOCAL_PREF`, `MED`, `ORIGIN` et `COMMUNITY` ;
- comparer plusieurs routes vers un même préfixe sans supposer que la route la plus courte est toujours la meilleure ;
- construire des filtres de préfixes et des politiques d'annonce explicites ;
- distinguer les fonctions d'un IXP, d'un route server, d'un pair et d'un fournisseur de transit ;
- expliquer les mécanismes courants de multihoming et leurs limites ;
- appliquer une méthode structurée de dépannage d'une session BGP ;
- identifier les risques des fuites de routes, des détournements de préfixes et des erreurs de filtrage ;
- comprendre les rôles de RPKI, de la validation de l'origine et des communautés BGP ;
- réaliser un laboratoire eBGP à trois systèmes autonomes avec filtrage entrant et sortant.

## Prérequis

Il est utile de savoir calculer des sous-réseaux IPv4, lire une table de routage, reconnaître une adresse de prochain saut et configurer des interfaces IP. Tu dois connaître les notions de système autonome (AS), ASN, préfixe, eBGP et iBGP.

## Environnement conseillé

Pour pratiquer, utilise de préférence un environnement isolé : GNS3, EVE-NG, CML, des routeurs virtuels ou des instances FRRouting. N'applique jamais une configuration d'exercice sur un routeur de production sans revue, autorisation, validation et plan de retour arrière.

Les adresses ci-dessous proviennent de plages de documentation, notamment `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24`. Elles sont adaptées aux exemples, pas à des annonces publiques réelles.

# Partie I — Les relations entre réseaux et les politiques BGP

## 1. Rappel : l'AS, le préfixe et le voisin BGP

Un système autonome (AS) regroupe des réseaux placés sous une politique de routage commune vis-à-vis de l'extérieur. Il est identifié par un ASN. Un préfixe IP représente un bloc d'adresses qu'un réseau souhaite rendre joignable.

Exemple fictif :

```text
AS65010, Opérateur Alpha
  Préfixe d'exemple : 203.0.113.0/24
          |
          | session eBGP
          v
AS65020, Opérateur Beta
  Préfixe d'exemple : 198.51.100.0/24
```

Lorsqu'Alpha annonce `203.0.113.0/24` à Beta, il annonce une possibilité de joindre ce préfixe. Il ne garantit pas à lui seul que tous les équipements du préfixe sont opérationnels. La joignabilité dépend aussi du transfert de paquets, des routes internes, des ACL, des interfaces et du chemin retour.

Les ASN `65010`, `65020` et `65030` utilisés dans ce cours sont fictifs et privés. Ils ne doivent pas être confondus avec des ASN publics.

## 2. Les principales relations commerciales et techniques

La relation entre deux systèmes autonomes influence les routes qu'ils échangent. BGP ne déduit pas automatiquement tout le contrat commercial : l'opérateur doit configurer une politique qui reflète la relation réelle.

### 2.1 Client et fournisseur de transit

Un client achète à un fournisseur un service lui permettant d'atteindre une partie étendue d'Internet, généralement au moyen du transit IP.

```text
             Fournisseur de transit
                    AS65020
                   /       \
         routes Internet   routes Internet
                 /           \
          Client A          Client B
          AS65010           AS65030
```

En pratique, le fournisseur annonce au client des routes permettant d'atteindre les destinations couvertes par le service. Le client annonce habituellement au fournisseur ses propres préfixes et ceux de ses clients, selon son contrat et sa politique.

Un fournisseur peut offrir une table Internet complète, une route par défaut ou un ensemble réduit de routes. Le contenu exact doit être convenu et vérifié.

### 2.2 Peering bilatéral

Le peering est une interconnexion dans laquelle deux réseaux échangent du trafic et des routes selon un accord. Un peering public peut se faire dans un IXP ; un peering privé peut utiliser une liaison dédiée ou une interconnexion dans un centre de données.

Dans le modèle habituel entre pairs de même niveau, chaque participant annonce ses propres routes et celles de ses clients, mais ne vend pas nécessairement à son pair un accès général à tout Internet. Les contrats réels peuvent varier.

```text
AS65010 Alpha  ===== peering =====  AS65020 Beta
       \\                              //
        \ routes autorisées selon l'accord /
```

Le point important n'est pas seulement le câble : la politique d'annonce doit respecter l'accord entre les deux parties.

### 2.3 Transit et peering : comparaison

| Critère | Transit IP | Peering |
|---|---|---|
| Objectif principal | Accéder à d'autres réseaux via un fournisseur | Échanger le trafic convenu entre participants |
| Portée des routes | Peut donner accès à une grande partie de l'Internet | Souvent limité aux routes propres et aux routes des clients |
| Modèle économique | Généralement un service acheté | Peut être gratuit ou payant selon les accords et l'interconnexion |
| Politique BGP | Filtrage et propagation selon le service | Filtrage et propagation selon la politique de peering |
| Risque de fuite | Possible si des routes sont propagées au-delà de leur portée | Possible si les routes sont réannoncées à des parties non prévues |

Il ne faut jamais déduire la politique complète d'une relation à partir de son seul nom. Les accords et les filtres précis déterminent ce qui est acceptable.

## 3. Internet Exchange Point (IXP) et route server

Un IXP est une infrastructure où plusieurs réseaux peuvent s'interconnecter, souvent au moyen d'un réseau Ethernet commun. Il permet aux participants d'établir des sessions BGP et d'échanger du trafic sans devoir construire une liaison dédiée avec chaque réseau participant.

Un IXP ne crée pas automatiquement une session BGP avec tous ses participants. Les opérateurs choisissent leurs pairs et définissent les politiques correspondantes.

### 3.1 Peering bilatéral dans un IXP

Deux participants établissent chacun leur session BGP directement :

```text
               Réseau Ethernet de l'IXP
          +--------------------------------+
          |                                |
       AS65010                           AS65020
          |                                |
          +------ session BGP directe -----+
```

### 3.2 Peering via un route server

Un route server de l'IXP facilite la distribution des annonces entre ses clients. Il s'agit d'un service de routage BGP : il ne doit généralement pas être confondu avec un routeur qui transporte lui-même les paquets utilisateur entre les participants.

```text
           AS65010                 AS65020
              |                       |
              | BGP                   | BGP
              v                       v
        +-----------------------------------+
        | Route server de l'IXP             |
        | distribue les annonces autorisées|
        +-----------------------------------+
              ^                       ^
              |                       |
           AS65030                 AS65040
```

Le route server peut transmettre les informations de routage selon les filtres et les règles de l'IXP. Le trafic de données passe généralement directement entre les participants sur l'infrastructure de commutation de l'IXP.

Il faut donc distinguer le plan de contrôle (échange des routes) et le plan de transfert (acheminement des paquets).

## 4. Pourquoi des politiques sont-elles indispensables ?

Un routeur peut être techniquement capable d'échanger une route sans que cette route soit souhaitable. Par exemple, un client ne doit pas automatiquement annoncer à son fournisseur une route Internet apprise d'un autre fournisseur comme s'il était lui-même un fournisseur de transit.

Les politiques BGP servent à :

1. sélectionner les routes autorisées à entrer dans le réseau ;
2. contrôler quelles routes deviennent candidates au meilleur chemin ;
3. décider quelles routes sont annoncées à chaque voisin ;
4. modifier certains attributs pour influencer les décisions ;
5. limiter la propagation d'erreurs et de routes inattendues.

### 4.1 Politique entrante et politique sortante

**Politique entrante (*import policy*)** : filtre et modifie les routes reçues d'un voisin avant qu'elles puissent participer à la décision BGP.

**Politique sortante (*export policy*)** : sélectionne les routes que le routeur a le droit d'annoncer à ce voisin.

```text
Routes reçues du voisin
          |
          v
Filtre entrant / import policy
          |
          v
Routes acceptées et attributs appliqués
          |
          v
Sélection du meilleur chemin BGP
          |
          v
RIB et éventuellement FIB
          |
          v
Filtre sortant / export policy
          |
          v
Routes annoncées à un voisin précis
```

Les noms et les détails internes varient selon les implémentations, mais le principe de contrôle reste le même.

### 4.2 Principe du refus par défaut

Une politique BGP de production ne devrait pas dépendre d'un comportement implicite permissif. La RFC 8212 recommande un comportement eBGP dans lequel les routes ne sont pas considérées comme éligibles et ne sont pas annoncées sans politiques entrante et sortante explicitement appliquées.

**Règle opérationnelle :** n'annonce que les préfixes prévus, et n'accepte que les routes nécessaires à la relation concernée.

# Partie II — Lire et interpréter les attributs BGP

## 5. Une annonce BGP est plus qu'un préfixe

BGP annonce des préfixes accompagnés d'attributs. Ces attributs permettent notamment d'identifier les systèmes autonomes traversés, de connaître le prochain saut, de comparer des chemins et d'appliquer des politiques.

Les attributs ne sont pas tous transmis ou traités de la même manière. Certains sont obligatoires, d'autres facultatifs. Certains sont bien connus, d'autres propres à une extension ou à une implémentation.

## 6. AS_PATH : le chemin inter-AS

L'attribut `AS_PATH` décrit le chemin d'AS associé à une annonce. Lorsqu'une route est annoncée entre AS différents, l'AS qui l'annonce ajoute normalement son ASN au chemin.

Exemple : le préfixe `203.0.113.0/24` est originaire d'AS65010. Après propagation par AS65020 puis AS65030, l'annonce peut présenter un chemin affiché comme suit :

```text
Préfixe : 203.0.113.0/24
AS_PATH : 65030 65020 65010
```

Dans cet exemple, AS65030 voit que l'annonce lui est parvenue via AS65020 et que l'origine apparente du chemin est AS65010.

L'affichage exact dépend du routeur et du contexte. Il faut interpréter la liste dans le sens défini par l'outil utilisé, sans supposer que l'ordre graphique est identique sur toutes les interfaces.

### 6.1 À quoi sert AS_PATH ?

- Observer les AS traversés par l'annonce.
- Détecter certaines boucles inter-AS lorsqu'un routeur retrouve son propre ASN dans le chemin.
- Comparer la longueur de chemins candidats dans l'algorithme de sélection BGP.
- Appliquer des politiques à partir de motifs d'ASN.
- Comprendre les annonces et les changements de chemin pendant un dépannage.

### 6.2 AS_PATH le plus court ne signifie pas toujours meilleur

Supposons que deux routes existent vers le même préfixe :

| Route | LOCAL_PREF | Longueur AS_PATH |
|---|---:|---:|
| A via le fournisseur Alpha | 200 | 3 AS |
| B via le fournisseur Beta | 100 | 1 AS |

Si la politique locale préfère d'abord le plus grand `LOCAL_PREF`, la route A peut être retenue même si son `AS_PATH` est plus long.

BGP n'est pas un protocole qui choisit simplement la distance géographique la plus courte. La décision dépend de plusieurs attributs et des politiques appliquées.

## 7. NEXT_HOP : le prochain saut

L'attribut `NEXT_HOP` désigne l'adresse IP du prochain saut utilisée pour acheminer les paquets vers le préfixe annoncé.

Une route peut être présente dans la table BGP mais ne pas être utilisable si son prochain saut est inconnu ou inaccessible selon les exigences de l'implémentation.

Exemple simplifié :

```text
AS65010                    AS65020
Router A ---------------- Router B
192.0.2.1                 192.0.2.2
        <--- eBGP --->

Préfixe distant : 198.51.100.0/24
NEXT_HOP vu par A : 192.0.2.2
```

Avant d'envisager une politique compliquée, vérifie que le prochain saut est joignable et que les routes internes nécessaires existent.

Avec iBGP, le traitement du prochain saut exige souvent une attention particulière : le routeur qui transmet une route à un pair iBGP ne remplace pas automatiquement le `NEXT_HOP` comme il le fait typiquement lorsqu'il annonce une route en eBGP. Le réseau interne doit pouvoir joindre ce prochain saut, ou une politique comme `next-hop-self` doit être appliquée lorsque c'est pertinent.

## 8. LOCAL_PREF : choisir la sortie préférée de son AS

`LOCAL_PREF` (*Local Preference*) sert généralement à indiquer aux routeurs d'un même AS quelle route de sortie préférer pour atteindre une destination.

Dans la politique BGP courante, une valeur plus élevée est préférée. Cet attribut est normalement propagé au sein de l'AS par iBGP, mais n'est pas envoyé à un voisin eBGP comme attribut inter-AS ordinaire.

Exemple :

```text
                AS65010
             /            \
       Fournisseur A    Fournisseur B
        LOCAL_PREF 200  LOCAL_PREF 100
```

Si les deux routes sont autrement éligibles et que la politique les compare ainsi, le réseau AS65010 préfère la sortie par le fournisseur A.

### 8.1 Exemple de valeurs locales

| Origine de la route | LOCAL_PREF de politique |
|---|---:|
| Transit principal | 200 |
| Peering direct | 180 |
| Transit secondaire | 100 |

Ces valeurs sont purement illustratives. Il n'existe pas de barème universel qui rendrait une valeur de `LOCAL_PREF` obligatoire pour tout opérateur.

Les opérateurs peuvent préférer le peering au transit, le transit principal à un transit de secours, ou construire une politique différente selon les services et les destinations.

## 9. MED : influencer le point d'entrée chez un AS voisin

`MED` signifie *Multi-Exit Discriminator*. Cet attribut peut être utilisé pour proposer à un AS voisin un point d'entrée préféré lorsqu'il existe plusieurs interconnexions entre les mêmes AS.

Dans le cas d'une comparaison de MED applicable, une valeur plus faible est généralement préférée.

```text
        AS65010                       AS65020
           |                              |
           |--- lien 1 : MED 20 ----------|
           |                              |
           |--- lien 2 : MED 80 ----------|
```

Si le routeur voisin compare ces deux MED conformément à sa politique et à son implémentation, il peut préférer le lien portant MED 20.

Attention : le MED n'est pas une garantie universelle. La comparaison du MED dépend notamment des règles du constructeur, de la configuration et de la provenance des routes. Il est généralement utilisé pour influencer un AS voisin, pas pour imposer à l'ensemble d'Internet un chemin précis.

### 9.1 LOCAL_PREF et MED : ne pas les confondre

| Attribut | Usage principal | Valeur habituellement préférée | Portée courante |
|---|---|---|---|
| LOCAL_PREF | Décision de sortie au sein de son propre AS | Plus grande | Interne à l'AS via iBGP |
| MED | Indication de préférence d'un point d'entrée chez un AS voisin | Plus petite, lorsque comparée | Annonce vers le voisin, selon politique |

## 10. ORIGIN : origine de l'information de route

L'attribut `ORIGIN` indique comment l'information de route a été introduite dans BGP. Les trois valeurs historiques sont :

- `IGP` : affichée généralement par `i` ;
- `EGP` : affichée généralement par `e`, héritée d'un protocole ancien ;
- `INCOMPLETE` : affichée généralement par `?`, notamment pour certaines routes redistribuées.

Dans l'ordre de préférence classique, `IGP` est préférable à `EGP`, puis à `INCOMPLETE`, toutes choses égales par ailleurs. L'origine BGP ne doit pas être confondue avec le protocole IGP OSPF ou IS-IS qui fonctionne à l'intérieur d'un réseau.

Un préfixe originaire de BGP via une commande `network` peut recevoir une origine IGP dans l'affichage BGP même si le protocole de routage interne est OSPF. Le terme historique `IGP` dans l'attribut `ORIGIN` a un sens propre au protocole BGP.

## 11. Communities : marquer les routes pour appliquer des politiques

Les communautés BGP sont des étiquettes associées aux routes. Elles permettent de construire une politique plus lisible que des règles répétées sur chaque préfixe.

Un opérateur peut définir ses propres communautés pour indiquer, par exemple :

- qu'une route provient d'un client ;
- qu'une route a été apprise dans une région particulière ;
- que la route ne doit pas être exportée à certains voisins ;
- qu'une route doit recevoir une préférence locale spécifique ;
- qu'une route doit être annoncée avec une politique donnée à certains transitaires.

Les communautés ne forcent pas les autres opérateurs à agir. Leur signification dépend de la politique et de la documentation de l'organisation qui les utilise.

### 11.1 Communautés bien connues

| Community | Signification générale |
|---|---|
| `NO_EXPORT` | Ne pas annoncer la route au-delà de la limite de propagation prévue par cette communauté, notamment hors de l'AS en l'absence de confédération |
| `NO_ADVERTISE` | Ne pas réannoncer la route à d'autres pairs BGP |
| `NO_EXPORT_SUBCONFED` | Restreindre l'annonce aux limites définies pour les confédérations BGP |

La prise en charge précise et le comportement des communautés doivent être vérifiés selon le protocole et l'implémentation. Il ne faut pas considérer une communauté arbitraire comme une commande universelle comprise par chaque opérateur.

### 11.2 Format classique des communautés

Une communauté classique est souvent affichée sous la forme `ASN:valeur`, par exemple :

```text
65020:100
65020:200
```

Ces deux valeurs ne possèdent aucune signification universelle. L'opérateur AS65020 pourrait définir `65020:100` comme « route client » et `65020:200` comme « route à faible priorité », mais seul son document de politique peut confirmer ce sens.

Les Large Communities apportent un format plus extensible, généralement affiché sous la forme de trois nombres. Elles sont documentées dans la RFC 8092.

### 11.3 Une communauté n'est pas une preuve cryptographique

Une communauté peut être ajoutée, modifiée ou retirée au cours de la propagation si la politique et l'implémentation le permettent. Elle ne remplace donc ni la validation de l'origine, ni les filtres, ni la protection des sessions BGP.

## 12. Weight : une notion propre à certaines implémentations

Sur Cisco IOS, `WEIGHT` est un attribut local à l'équipement, généralement utilisé par l'algorithme de sélection Cisco. La valeur la plus élevée est préférée. Il ne s'agit pas d'un attribut BGP standard propagé vers les autres routeurs comme `AS_PATH`.

Il faut donc distinguer :

- les attributs BGP définis par le protocole ;
- les critères locaux d'un constructeur ;
- la séquence exacte de décision configurée sur la plateforme.

Une comparaison de chemins doit toujours préciser le routeur, la politique et l'environnement concernés.

# Partie III — Sélection des routes et ingénierie de trafic

## 13. Comment BGP choisit-il une route ?

Pour un même préfixe, un routeur peut apprendre plusieurs routes. Il doit sélectionner une route préférée selon l'algorithme de décision et les politiques de sa plateforme.

Une vue conceptuelle des critères courants est donnée ci-dessous. Ce tableau n'est pas un algorithme universel à appliquer sans lire la documentation du constructeur.

| Critère courant | Effet habituel |
|---|---|
| Route inéligible ou rejetée par une politique | Elle n'est pas retenue comme meilleure route utilisable |
| Préférence locale propre à l'implémentation, telle que Weight sur Cisco | Une valeur plus élevée peut être préférée |
| LOCAL_PREF | La valeur la plus élevée est généralement préférée |
| Origine locale de la route BGP | Certaines routes produites localement sont favorisées |
| AS_PATH | Un chemin plus court est généralement préféré si les critères précédents ne décident pas |
| ORIGIN | `IGP` est historiquement préféré à `EGP`, puis `INCOMPLETE` |
| MED | Une valeur plus faible est préférée lorsque le MED est comparé et que les autres critères applicables le permettent |
| eBGP contre iBGP | Une route apprise en eBGP est généralement préférée à une route iBGP si les critères précédents sont égaux |
| Coût IGP vers NEXT_HOP | Un coût interne plus faible peut départager des routes |
| Critères de départage | Des identifiants, adresses ou autres règles peuvent départager les routes restantes |

L'ordre exact dépend du constructeur, de la version, de la configuration et parfois d'extensions. Il faut consulter la documentation du routeur exploité.

### 13.1 Décision BGP et transfert IP sont deux choses différentes

BGP choisit une route parmi les routes candidates pour un préfixe. Le transfert IP choisit ensuite le prochain saut à utiliser pour chaque paquet, selon la table de transfert.

Il faut aussi prendre en compte le *longest-prefix match* : si un routeur possède une route vers `203.0.113.0/24` et une route plus spécifique vers `203.0.113.128/25`, une adresse située dans la seconde moitié du `/24` peut utiliser la route `/25`, même si la préférence BGP de la route `/24` était plus élevée. Le choix du préfixe le plus spécifique dans le plan de transfert est distinct du choix du meilleur chemin BGP pour un préfixe donné.

### 13.2 Exemple : LOCAL_PREF avant la longueur AS_PATH

Deux routes vers `203.0.113.0/24` sont disponibles :

| Route | LOCAL_PREF | AS_PATH |
|---|---:|---|
| A via Alpha | 200 | `65020 65030 65040` |
| B via Beta | 100 | `65050` |

Dans une politique qui compare LOCAL_PREF avant AS_PATH, la route A est préférée car 200 est supérieur à 100. La route B a un chemin plus court, mais ce critère intervient plus tard dans cette comparaison.

## 14. Influencer le trafic sortant

Le trafic sortant est le trafic qui quitte ton AS vers une destination externe. Pour influencer la sortie utilisée par les routeurs de ton propre réseau, `LOCAL_PREF` est souvent un outil central.

Exemple :

```text
                 AS65010
                /        \
     Fournisseur Alpha  Fournisseur Beta
        LP 200              LP 100
                \        /
              Préfixe distant
```

Si les routes sont autrement utilisables, les routeurs de l'AS65010 pourront préférer les routes via Alpha.

L'augmentation de `LOCAL_PREF` ne garantit pas qu'Alpha transportera chaque paquet : une panne de lien, une route plus spécifique, une route manquante ou une autre règle de la décision peut modifier le résultat.

## 15. Influencer le trafic entrant

Le trafic entrant est le trafic qui vient d'autres réseaux vers tes préfixes. Il est plus difficile à contrôler, car chaque réseau distant applique ses propres politiques.

Les techniques courantes comprennent :

### 15.1 AS-path prepend

Le réseau annonce son préfixe avec des occurrences supplémentaires de son ASN dans l'AS_PATH. Certains réseaux voisins peuvent alors préférer une autre route vers le même préfixe.

```text
Lien A : AS_PATH vu depuis l'extérieur = 65010
Lien B : AS_PATH vu depuis l'extérieur = 65010 65010 65010
```

L'objectif est de rendre le chemin B moins attractif pour certains voisins. Cependant, l'AS-path prepend n'est pas une commande garantissant le chemin retour : un `LOCAL_PREF` plus élevé chez le réseau distant peut compter davantage que la longueur d'AS_PATH.

### 15.2 MED et communautés du fournisseur

Si le fournisseur les accepte et les documente, MED et les communautés peuvent lui indiquer le point d'entrée souhaité ou une politique de propagation. Il faut vérifier le contrat et le guide des communautés du fournisseur avant de s'en servir.

### 15.3 Annonces plus spécifiques

Une route plus spécifique peut attirer le trafic correspondant, car le transfert IP privilégie le préfixe le plus long. C'est une technique puissante et risquée : elle peut augmenter considérablement la portée d'une erreur d'annonce, consommer des ressources de routage et provoquer des résultats inattendus si les filtres distants la rejettent.

N'annonce pas de préfixes plus spécifiques en production sans planification, justification, contrôle des autorisations et tests. Les règles d'acceptation des préfixes varient selon les réseaux.

# Partie IV — Filtres de routes et politiques d'annonce

## 16. Pourquoi filtrer les préfixes ?

Supposons qu'un client ait le droit d'annoncer uniquement `203.0.113.0/24`. Une erreur de configuration pourrait lui faire annoncer accidentellement un préfixe beaucoup plus large ou une route apprise d'un autre opérateur.

Les filtres réduisent le risque en définissant explicitement ce qui est autorisé.

Les filtres BGP peuvent contrôler :

- le préfixe et sa longueur ;
- l'AS_PATH ;
- les communautés ;
- les attributs de politique ;
- les routes selon le voisin et la direction de l'annonce.

La stratégie exacte dépend de la relation de peering et du service fourni.

## 17. Prefix-list : autoriser des préfixes précis

Une prefix-list permet de définir les réseaux autorisés. La syntaxe varie selon la plateforme.

Sur Cisco IOS, une liste simple peut être écrite ainsi :

```text
ip prefix-list CLIENT-PREFIXES seq 10 permit 203.0.113.0/24
```

Cette entrée correspond précisément au préfixe `203.0.113.0/24`. Elle n'autorise pas automatiquement tous les préfixes contenus dans ce bloc.

Pour contrôler une plage de longueurs, on peut utiliser `ge` et `le`. Par exemple :

```text
ip prefix-list EXEMPLE seq 10 permit 203.0.113.0/24 le 28
```

Cette entrée autorise le `/24` et ses préfixes plus spécifiques jusqu'à `/28`, à condition qu'ils restent dans le bloc indiqué. Elle est plus permissive que l'entrée exacte précédente et ne doit pas être utilisée sans raison.

Une prefix-list possède une règle implicite de refus final dans les usages habituels de Cisco IOS. Il faut donc vérifier toutes les lignes : un préfixe non autorisé explicitement peut être rejeté.

## 18. Contrôle des annonces sortantes

La politique sortante doit correspondre à la relation avec le voisin. Pour un client qui ne doit annoncer qu'un préfixe, configure une liste correspondant à ce préfixe, puis applique-la à la session sortante.

Exemple Cisco IOS :

```text
ip prefix-list CLIENT-OUT seq 10 permit 203.0.113.0/24
!
route-map CLIENT-EXPORT permit 10
 match ip address prefix-list CLIENT-OUT
!
router bgp 65010
 neighbor 192.0.2.2 remote-as 65020
 neighbor 192.0.2.2 route-map CLIENT-EXPORT out
```

Cette configuration montre l'idée générale : seul le préfixe qui correspond à la liste est exporté à ce voisin par cette route-map. La politique doit être vérifiée avec les commandes d'annonce BGP de la plateforme.

Une route-map qui ne comporte qu'une entrée `permit` avec un critère de correspondance se termine par un refus implicite pour les routes non correspondantes. Le résultat doit être intentionnel.

## 19. Contrôle des annonces entrantes

Une liste entrante doit correspondre aux annonces attendues du voisin. Il ne suffit pas de filtrer uniquement les routes sortantes : un opérateur doit aussi limiter les routes acceptées de chaque pair.

Exemple :

```text
ip prefix-list CLIENT-IN seq 10 permit 198.51.100.0/24
!
route-map CLIENT-IMPORT permit 10
 match ip address prefix-list CLIENT-IN
!
router bgp 65010
 neighbor 192.0.2.2 remote-as 65020
 neighbor 192.0.2.2 route-map CLIENT-IMPORT in
```

Dans cet exemple pédagogique, seul le préfixe précis `198.51.100.0/24` est accepté par cette route-map. Dans un vrai réseau, il faut adapter le filtre aux routes réellement prévues dans le contrat et aux besoins de connectivité.

**Attention :** une liste trop stricte peut provoquer une panne si des préfixes légitimes changent, tandis qu'une liste trop permissive peut accepter une annonce dangereuse. Les filtres doivent être maintenus, documentés et surveillés.

## 20. Limiter le nombre de préfixes reçus

Une limite de préfixes (*maximum-prefix*) peut faire partie des protections contre une annonce accidentelle d'un très grand nombre de routes. La fonction exacte et son comportement en cas de dépassement varient selon le constructeur : arrêt de session, avertissement, seuil ou autre traitement.

La limite doit correspondre au nombre attendu de préfixes, avec une marge raisonnée. Elle ne remplace pas un filtrage par préfixes ou par AS_PATH.

Exemple illustratif sur une plateforme Cisco IOS qui prend en charge la syntaxe indiquée :

```text
router bgp 65010
 neighbor 192.0.2.2 maximum-prefix 100
```

Le nombre `100` est seulement un exemple. Il ne convient pas à un fournisseur envoyant une table Internet complète. Certains équipements proposent également un seuil d'avertissement, un comportement de dépassement différent ou une configuration sous une famille d'adresses spécifique.

Avant une mise en production, consulte la documentation de la version utilisée et vérifie ce qui se passe réellement lorsque la limite est franchie.

## 21. Prévenir les fuites de routes

Une fuite de routes (*route leak*) se produit lorsqu'une annonce est propagée au-delà de la portée prévue par la politique ou la relation entre réseaux. Elle peut résulter d'une erreur humaine, d'une politique manquante ou d'une mauvaise coordination.

Exemple :

```text
      Fournisseur A
           |
           | route Internet complète
           v
        AS65010
           |
           | annonce incorrectement tout ce qu'il apprend
           v
      Fournisseur B
```

AS65010 peut alors réannoncer à B des routes qui proviennent de A et qui ne devraient pas être propagées dans cette relation. Cela peut attirer du trafic vers un chemin inattendu ou perturber la connectivité.

Les protections incluent les politiques d'importation et d'exportation, le filtrage des préfixes, la maîtrise de l'AS_PATH, la surveillance et les mécanismes plus récents de signalement des relations BGP.

La RFC 8212 décrit un comportement par défaut plus sûr lorsqu'aucune politique eBGP explicite n'est configurée. La RFC 9234 spécifie des rôles BGP et l'attribut OTC (*Only to Customer*) afin d'améliorer la prévention et la détection de certaines fuites de routes. Ces mécanismes ne remplacent pas une politique correcte.

# Partie V — Multihoming et résilience opérateur

## 22. Qu'est-ce que le multihoming ?

Le multihoming consiste à connecter un réseau à plusieurs fournisseurs ou chemins de sortie. Il peut améliorer la résilience et donner davantage de choix pour le trafic.

Exemple :

```text
                    Fournisseur Alpha
                           |
                           |
                      +----------+
                      | AS65010  |
                      | Client   |
                      +----------+
                           |
                           |
                    Fournisseur Beta
```

La représentation simplifie le schéma. Dans une architecture réelle, chaque fournisseur dispose d'une interface ou d'un lien distinct, et le client doit posséder une politique BGP correspondant à ces liens.

### 22.1 Avantages possibles

- Disposer d'une solution de repli si un fournisseur ou une liaison tombe en panne.
- Choisir une sortie préférée pour certaines destinations.
- Influencer la façon dont les réseaux extérieurs atteignent les préfixes du client.
- Adapter la connectivité à des exigences de capacité, de disponibilité ou de politique.

### 22.2 Contraintes

Le multihoming ajoute de la complexité :

- deux sessions BGP ou plus à surveiller ;
- plusieurs routes candidates vers les mêmes destinations ;
- des politiques de filtrage et de préférence plus élaborées ;
- des risques de chemins asymétriques ;
- des exigences supplémentaires en matière de préfixes, d'adressage et d'autorisations ;
- des besoins de surveillance, de tests de bascule et de documentation.

Une connexion de secours n'est utile que si la route de secours est réellement utilisable et si les services de l'organisation tolèrent les modifications de chemin.

## 23. Le trafic aller et le trafic retour peuvent suivre des chemins différents

Le routage IP n'impose pas que les paquets aller et retour empruntent le même chemin.

```text
Trafic aller :
Client ---- Fournisseur Alpha ---- Serveur

Trafic retour :
Client <--- Fournisseur Beta  <---- Serveur
```

Cette asymétrie est normale dans beaucoup d'environnements. Elle peut toutefois compliquer le dépannage lorsqu'un pare-feu, un dispositif NAT ou un mécanisme de contrôle d'état exige de voir les deux sens du trafic.

Lors d'un incident, vérifie le chemin aller et le chemin retour. Un traceroute dans un seul sens ne démontre pas nécessairement le chemin du retour.

## 24. Route par défaut et table Internet complète

Un opérateur peut apprendre de son fournisseur :

- une route par défaut (`0.0.0.0/0` pour IPv4 ou `::/0` pour IPv6) ;
- un ensemble limité de préfixes ;
- une table de routage Internet beaucoup plus complète.

La bonne option dépend de l'architecture, de la capacité des équipements, des contrats et des besoins de routage.

La route par défaut signifie que le routeur enverra vers son prochain saut les destinations pour lesquelles aucune route plus spécifique n'est disponible. Elle n'indique pas que le prochain saut peut effectivement atteindre toutes les destinations : c'est le contrat de service et le réseau amont qui déterminent la portée réelle.

Lorsque plusieurs fournisseurs annoncent une route par défaut, les politiques locales décident laquelle est préférée ou si des mécanismes de partage sont utilisés. Il faut également vérifier que l'annonce d'une route par défaut n'envoie pas accidentellement du trafic vers une connexion inadaptée.

# Partie VI — Sécurité et fiabilité de BGP

## 25. Le détournement de préfixe

Un détournement de préfixe (*prefix hijack*) survient lorsqu'un AS annonce un préfixe qu'il n'est pas autorisé à annoncer, ou annonce une route qui cause un détournement de trafic. Cela peut être malveillant ou résulter d'une erreur de configuration.

Un exemple conceptuel :

```text
Annonce légitime :
AS65010 annonce 203.0.113.0/24

Annonce incorrecte :
AS65090 annonce aussi 203.0.113.0/24
```

Les réseaux distants peuvent voir deux chemins concurrents. Le chemin retenu dépend de leurs politiques et des informations disponibles. Le fait qu'une annonce possède un `AS_PATH` différent n'indique pas, à lui seul, si son origine est autorisée.

Dans un vrai réseau, les plages IP réservées à la documentation utilisées dans cet exemple ne doivent pas être annoncées sur Internet.

## 26. RPKI et validation de l'origine

RPKI (*Resource Public Key Infrastructure*) permet aux détenteurs de ressources Internet de publier des autorisations vérifiables concernant l'AS qui peut annoncer un préfixe. Une autorisation de route est appelée ROA (*Route Origin Authorization*).

Une ROA peut indiquer :

- le préfixe concerné ;
- l'ASN autorisé à en être l'origine ;
- une longueur maximale de préfixe autorisée, si elle est définie.

Les systèmes de validation utilisent généralement trois résultats pour caractériser une annonce :

| État | Signification générale |
|---|---|
| `Valid` | Le préfixe et l'AS d'origine correspondent à une autorisation RPKI valide |
| `Invalid` | Une autorisation applicable existe, mais l'annonce ne respecte pas les contraintes, par exemple l'ASN d'origine ou la longueur maximale |
| `NotFound` ou `Unknown` | Aucune autorisation couvrant l'annonce n'a été trouvée dans les données validées |

La façon dont un opérateur traite ces états dépend de sa politique. Une stratégie courante consiste à rejeter les annonces `Invalid`, tout en appliquant une politique soigneuse aux états sans autorisation trouvée. Il faut éviter de supposer que toute annonce `NotFound` est malveillante.

### 26.1 Ce que RPKI ne fait pas

La validation de l'origine ne garantit pas l'ensemble du chemin BGP. Elle ne vérifie pas à elle seule chaque AS traversé, la capacité du réseau à transporter les paquets ou la conformité commerciale de toutes les annonces.

RPKI est une protection importante, mais elle doit être combinée avec des filtres, une politique d'annonce correcte et de la surveillance.

## 27. Protection des sessions BGP

Les sessions BGP reposent normalement sur TCP, sur le port 179. Une session doit être protégée contre les connexions non autorisées et les perturbations du plan de contrôle.

Mesures à envisager selon la plateforme et l'architecture :

- limiter les connexions au plan de contrôle aux voisins prévus ;
- filtrer les annonces entrantes et sortantes ;
- utiliser les mécanismes d'authentification de session pris en charge et compatibles avec le voisin ;
- activer des mécanismes de protection du plan de contrôle ;
- surveiller l'état des sessions, les changements d'AS_PATH et les variations de nombre de préfixes ;
- sauvegarder et faire relire les configurations ;
- préparer une procédure de retour arrière avant toute modification.

L'authentification TCP ou une ACL peut réduire certains risques, mais ne prouve pas qu'une route annoncée par un pair est légitime. La sécurité de la session et la sécurité des annonces sont des sujets différents.

# Partie VII — Diagnostic structuré d'une session BGP

## 28. Les états BGP

Les états classiques d'une session BGP incluent notamment :

| État | Interprétation générale |
|---|---|
| `Idle` | La session n'est pas établie ; le routeur attend ou prépare une nouvelle tentative selon son état |
| `Connect` | Le routeur tente d'établir la connexion TCP |
| `Active` | La connexion n'a pas abouti et le routeur poursuit ses tentatives |
| `OpenSent` | Un message OPEN a été envoyé, en attente de la suite de la négociation |
| `OpenConfirm` | La négociation OPEN a progressé et le routeur attend la confirmation finale attendue |
| `Established` | La session BGP est établie et les messages de routage peuvent être échangés |

Le nom d'un état indique la phase de la session, pas l'état de la connectivité IP de bout en bout.

## 29. Méthode de dépannage en sept étapes

Lorsqu'une session ne monte pas ou qu'une route manque, procède dans cet ordre.

### Étape 1 — Vérifier le lien et l'adressage

Contrôle l'état de l'interface, le masque IP, l'adresse du voisin et la présence d'une connectivité IP entre les deux extrémités.

Sur Cisco IOS, commandes typiques :

```text
show ip interface brief
show ip route
ping 192.0.2.2
```

Adapte l'adresse de ping à ton voisin réel.

### Étape 2 — Vérifier l'accessibilité TCP 179

BGP utilise normalement TCP sur le port 179. Une ACL, un pare-feu ou une politique de plan de contrôle peut bloquer la connexion. Les outils et commandes de vérification dépendent de la plateforme.

### Étape 3 — Vérifier les ASN et la configuration du voisin

Compare l'ASN local avec celui prévu dans le voisinage distant. Vérifie l'adresse du voisin, la famille d'adresses activée et la présence d'une politique nécessaire.

### Étape 4 — Contrôler l'état de la session

Sur Cisco IOS, les commandes courantes comprennent :

```text
show ip bgp summary
show ip bgp neighbors
```

Sur certaines versions, la famille d'adresses peut être indiquée explicitement dans les commandes de consultation.

### Étape 5 — Vérifier si la route existe localement

Si une configuration `network` tente d'annoncer un préfixe, vérifie que la route correspondante existe dans la table de routage et que le masque est exact lorsque la plateforme l'exige.

```text
show ip route 203.0.113.0
show ip bgp
```

Le comportement de la commande `network` varie selon la syntaxe et la plateforme. Sur Cisco IOS classique, la route correspondante doit généralement exister dans la table de routage avec le masque attendu.

### Étape 6 — Vérifier les politiques et les annonces

Contrôle les filtres entrants et sortants, les route-maps, les prefix-lists, les politiques de communauté et les éventuelles limites de préfixes.

```text
show ip prefix-list
show route-map
show ip bgp neighbors 192.0.2.2 advertised-routes
```

La dernière commande est disponible sur plusieurs plateformes Cisco IOS, mais la syntaxe et les exigences de rafraîchissement des annonces peuvent varier.

### Étape 7 — Vérifier le transfert réel

Même si la session est `Established` et qu'une route est présente dans BGP, vérifie la table de routage, le prochain saut, les ACL, la route de retour et l'état des interfaces.

```text
show ip route 198.51.100.0
show ip cef 198.51.100.1
traceroute 198.51.100.1
```

Ces commandes illustrent une approche Cisco IOS/IOS-XE. Sur d'autres systèmes, les outils diffèrent.

## 30. Symptômes courants et premières pistes

| Symptôme | Causes possibles | Contrôles prioritaires |
|---|---|---|
| Session bloquée en `Active` | Voisin inaccessible, TCP 179 filtré, adresse incorrecte | Ping, interface, ACL, adresse et port |
| Session rejetée après OPEN | ASN distant incorrect, incompatibilité de paramètres ou de rôles | Journaux, voisin configuré, message de notification |
| Session `Established`, aucune route attendue | Préfixe absent, filtre, famille d'adresses inactive, route non annoncée | Table de routage, BGP, policies, annonces sortantes |
| Route visible dans BGP mais absente de la table IP | Route non meilleure, prochain saut inaccessible, préférence d'une autre source | Détails de route BGP, RIB, next-hop |
| Route apprise mais trafic en panne | Problème de transfert, route retour absente, ACL ou NAT | Table de transfert, tests dans les deux sens |
| Trop de routes reçues | Filtrage absent ou incorrect, annonce inattendue | Filtres, compteur de préfixes, maximum-prefix, logs |
| Chemin changé sans changement local évident | Modifications chez un voisin, retrait d'annonce, politique ou panne distante | Événements BGP, AS_PATH, messages de supervision |

Évite de réinitialiser immédiatement une session BGP en production. La réinitialisation peut interrompre la connectivité et masquer l'information utile au diagnostic. Observe d'abord les états, journaux, routes et politiques.

# Partie VIII — Travaux pratiques

## 31. TP 1 : choisir la route selon la politique

### Objectif

Interpréter deux routes BGP vers le même préfixe.

### Données

Le routeur AS65010 apprend les routes suivantes vers `198.51.100.0/24` :

| Attribut | Route A | Route B |
|---|---|---|
| Voisin | AS65020 | AS65030 |
| LOCAL_PREF | 180 | 120 |
| AS_PATH | `65020 65040` | `65030` |
| ORIGIN | IGP | IGP |

### Questions

1. Quelle route sera préférée si LOCAL_PREF est comparé avant la longueur AS_PATH et si aucune autre règle antérieure ne départage les routes ?
2. Pourquoi la longueur AS_PATH ne suffit-elle pas à décider ?
3. Quelle route pourrait être choisie si les politiques donnaient à la route B un LOCAL_PREF supérieur ?

### Correction

1. La route A est préférée dans le scénario indiqué, car son LOCAL_PREF vaut 180 contre 120.
2. Parce que les attributs et les politiques antérieurs à AS_PATH dans la décision peuvent l'emporter.
3. La route B pourrait être préférée si son LOCAL_PREF était supérieur et si elle restait éligible, sous réserve des critères et règles de l'implémentation.

## 32. TP 2 : concevoir un filtre d'annonces

### Scénario

AS65010 est client de AS65020. Le préfixe autorisé à être annoncé par AS65010 est `203.0.113.0/24`. Aucun autre préfixe ne doit être exporté vers ce voisin.

### Travail demandé

1. Définir une prefix-list autorisant exactement ce préfixe.
2. Créer une route-map d'export.
3. Appliquer la route-map au voisin eBGP.
4. Expliquer pourquoi il faut vérifier les routes réellement annoncées après application.

### Correction Cisco IOS indicative

```text
ip prefix-list CLIENT-OUT seq 10 permit 203.0.113.0/24
!
route-map CLIENT-EXPORT permit 10
 match ip address prefix-list CLIENT-OUT
!
router bgp 65010
 neighbor 192.0.2.2 remote-as 65020
 neighbor 192.0.2.2 route-map CLIENT-EXPORT out
```

La configuration suppose que la session est déjà définie ou qu'elle est à compléter dans ce bloc. La route-map ne permet que les routes correspondant à la liste ; les routes non correspondantes sont rejetées implicitement par la route-map.

La vérification est indispensable, car la syntaxe peut varier et la route peut être absente, inéligible ou déjà filtrée à une autre étape.

## 33. TP 3 : interpréter un route leak

### Scénario

AS65010 possède deux fournisseurs : AS65020 et AS65030. Une route Internet apprise d'AS65020 est annoncée par erreur à AS65030, alors que la relation entre les deux voisins ne prévoit pas la revente de transit.

### Questions

1. Pourquoi ce comportement peut-il être qualifié de fuite de routes ?
2. Quelles politiques devraient empêcher ce problème ?
3. Quelles informations faut-il recueillir avant de corriger ?

### Correction

1. Une annonce est propagée au-delà de la portée prévue par la relation et les politiques de routage. Cela correspond à la notion de route leak.
2. Il faut appliquer des politiques d'export distinctes selon le voisin, annoncer uniquement les routes autorisées et vérifier les routes apprises des clients, pairs et fournisseurs. Les mécanismes de rôles BGP et OTC peuvent apporter une protection supplémentaire lorsqu'ils sont pris en charge et configurés des deux côtés.
3. Il faut établir la liste des préfixes concernés, identifier leur origine et leur chemin AS_PATH, vérifier les route-maps en entrée et en sortie, consulter les journaux et mesurer l'effet de toute modification avant de l'appliquer.

# Partie IX — Laboratoire eBGP à trois systèmes autonomes

## 34. Scénario et plan d'adressage

Ce laboratoire illustre trois AS : un réseau client AS65010, un fournisseur de transit AS65020 et un autre réseau client AS65030. AS65020 fournit le transit entre les deux clients.

Le but est de configurer des sessions eBGP, d'annoncer un préfixe de chaque côté et de limiter les annonces avec des filtres explicites.

### 34.1 Topologie

```text
        203.0.113.0/24                       198.51.100.0/24
       Préfixe du client A                   Préfixe du client B
                |                                     |
           +---------+       +---------+         +---------+
           |   R1    |-------|   R2    |---------|   R3    |
           | AS65010 |       | AS65020 |         | AS65030 |
           +---------+       +---------+         +---------+
             .1/30      .2/30       .5/30       .6/30
          192.0.2.0/30           192.0.2.4/30
```

### 34.2 Plan d'adressage des liaisons

| Liaison | Routeur | Adresse |
|---|---|---|
| R1–R2 | R1 | `192.0.2.1/30` |
| R1–R2 | R2 | `192.0.2.2/30` |
| R2–R3 | R2 | `192.0.2.5/30` |
| R2–R3 | R3 | `192.0.2.6/30` |
| Préfixe client A | R1, loopback | `203.0.113.1/24` |
| Préfixe client B | R3, loopback | `198.51.100.1/24` |

Les interfaces exactes (`GigabitEthernet`, `Ethernet`, etc.) dépendent de la plateforme virtuelle choisie. Configure les adresses et active les interfaces avant de passer à BGP.

### 34.3 Résultat attendu

- R1 forme une session eBGP avec R2.
- R3 forme une session eBGP avec R2.
- R1 annonce uniquement `203.0.113.0/24` vers R2.
- R3 annonce uniquement `198.51.100.0/24` vers R2.
- R2 annonce à R1 le préfixe `198.51.100.0/24`.
- R2 annonce à R3 le préfixe `203.0.113.0/24`.
- Les routes ne sont pas propagées sans contrôle explicite.

## 35. Configuration de R1 — AS65010

La configuration ci-dessous utilise une syntaxe Cisco IOS classique. Les interfaces doivent être adaptées à la maquette.

```text
configure terminal
!
interface GigabitEthernet0/0
 description Lien-vers-R2
 ip address 192.0.2.1 255.255.255.252
 no shutdown
!
interface Loopback0
 description Prefixe-de-test-du-client-A
 ip address 203.0.113.1 255.255.255.0
!
ip prefix-list R1-EXPORT seq 10 permit 203.0.113.0/24
ip prefix-list R1-IMPORT seq 10 permit 198.51.100.0/24
!
route-map R1-OUT permit 10
 match ip address prefix-list R1-EXPORT
!
route-map R1-IN permit 10
 match ip address prefix-list R1-IMPORT
!
router bgp 65010
 bgp log-neighbor-changes
 neighbor 192.0.2.2 remote-as 65020
 neighbor 192.0.2.2 route-map R1-IN in
 neighbor 192.0.2.2 route-map R1-OUT out
 network 203.0.113.0 mask 255.255.255.0
end
write memory
```

La commande `network` dans cet exemple suppose que le préfixe exact `203.0.113.0/24` existe dans la table de routage locale. L'interface Loopback0 fournit cette route connectée. Ce comportement est typique de Cisco IOS classique ; vérifie la documentation de la version utilisée.

## 36. Configuration de R2 — AS65020

R2 joue le rôle du fournisseur de transit du laboratoire. Il reçoit les préfixes autorisés de chaque client et exporte à chaque client uniquement le préfixe de l'autre client.

```text
configure terminal
!
interface GigabitEthernet0/0
 description Lien-vers-R1
 ip address 192.0.2.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description Lien-vers-R3
 ip address 192.0.2.5 255.255.255.252
 no shutdown
!
ip prefix-list FROM-R1 seq 10 permit 203.0.113.0/24
ip prefix-list FROM-R3 seq 10 permit 198.51.100.0/24
ip prefix-list TO-R1 seq 10 permit 198.51.100.0/24
ip prefix-list TO-R3 seq 10 permit 203.0.113.0/24
!
route-map IMPORT-R1 permit 10
 match ip address prefix-list FROM-R1
!
route-map IMPORT-R3 permit 10
 match ip address prefix-list FROM-R3
!
route-map EXPORT-R1 permit 10
 match ip address prefix-list TO-R1
!
route-map EXPORT-R3 permit 10
 match ip address prefix-list TO-R3
!
router bgp 65020
 bgp log-neighbor-changes
 neighbor 192.0.2.1 remote-as 65010
 neighbor 192.0.2.1 route-map IMPORT-R1 in
 neighbor 192.0.2.1 route-map EXPORT-R1 out
 neighbor 192.0.2.6 remote-as 65030
 neighbor 192.0.2.6 route-map IMPORT-R3 in
 neighbor 192.0.2.6 route-map EXPORT-R3 out
end
write memory
```

R2 ne doit pas annoncer automatiquement chaque route reçue à chaque voisin. Les route-maps appliquées à la sortie limitent explicitement les préfixes autorisés.

## 37. Configuration de R3 — AS65030

```text
configure terminal
!
interface GigabitEthernet0/0
 description Lien-vers-R2
 ip address 192.0.2.6 255.255.255.252
 no shutdown
!
interface Loopback0
 description Prefixe-de-test-du-client-B
 ip address 198.51.100.1 255.255.255.0
!
ip prefix-list R3-EXPORT seq 10 permit 198.51.100.0/24
ip prefix-list R3-IMPORT seq 10 permit 203.0.113.0/24
!
route-map R3-OUT permit 10
 match ip address prefix-list R3-EXPORT
!
route-map R3-IN permit 10
 match ip address prefix-list R3-IMPORT
!
router bgp 65030
 bgp log-neighbor-changes
 neighbor 192.0.2.5 remote-as 65020
 neighbor 192.0.2.5 route-map R3-IN in
 neighbor 192.0.2.5 route-map R3-OUT out
 network 198.51.100.0 mask 255.255.255.0
end
write memory
```

## 38. Vérification du laboratoire

### 38.1 Vérifier les liaisons IP

Sur R1 :

```text
ping 192.0.2.2
show ip interface brief
show ip route
```

Sur R2 :

```text
ping 192.0.2.1
ping 192.0.2.6
show ip interface brief
show ip route
```

Sur R3 :

```text
ping 192.0.2.5
show ip interface brief
show ip route
```

Si les liaisons directement connectées ne fonctionnent pas, ne cherche pas encore à résoudre un problème BGP : corrige d'abord le câblage virtuel, les adresses, les masques ou l'état des interfaces.

### 38.2 Vérifier les sessions BGP

Sur les trois routeurs :

```text
show ip bgp summary
show ip bgp neighbors
```

Les deux voisinages configurés sur R2 doivent finir par atteindre l'état `Established`. R1 et R3 n'ont chacun qu'un voisin BGP dans cette maquette.

### 38.3 Vérifier les routes BGP

Sur R1 :

```text
show ip bgp
show ip route bgp
show ip bgp neighbors 192.0.2.2 advertised-routes
```

Sur R2 :

```text
show ip bgp
show ip route bgp
show ip bgp neighbors 192.0.2.1 advertised-routes
show ip bgp neighbors 192.0.2.6 advertised-routes
```

Sur R3 :

```text
show ip bgp
show ip route bgp
show ip bgp neighbors 192.0.2.5 advertised-routes
```

Les commandes `advertised-routes` peuvent dépendre de la plate-forme et de la famille d'adresses. Utilise l'équivalent fourni par ton système si nécessaire.

### 38.4 Tester la connectivité de bout en bout

Depuis R1, teste d'abord l'adresse de loopback de R3 :

```text
ping 198.51.100.1 source 203.0.113.1
```

Depuis R3, teste le retour :

```text
ping 203.0.113.1 source 198.51.100.1
```

Sur certaines versions, la syntaxe de la commande `ping` avec source peut varier. Utilise le mode interactif si nécessaire.

Si les sessions sont établies mais que le ping échoue, vérifie que les routes sont apprises et installées aux deux extrémités, que le prochain saut est résolu et que les interfaces et les politiques ne bloquent pas les paquets.

## 39. Exercices de modification du laboratoire

### Exercice A — Bloquer une annonce

Sur R2, retire temporairement le préfixe `203.0.113.0/24` de la liste entrante qui accepte les annonces de R1, puis vérifie que cette route n'est plus retenue à la suite de la mise à jour de politique.

**Correction attendue :** R2 ne doit plus considérer le préfixe de R1 comme une route reçue éligible via cette session. La route de ce préfixe peut disparaître de la table BGP de R2 si aucune autre route utilisable n'existe.

Rétablis ensuite la règle autorisant le préfixe exact, puis vérifie le retour de la route. Dans une maquette réelle, la commande de rafraîchissement des politiques dépend de la plateforme et de la négociation de route refresh.

### Exercice B — Créer une panne de voisin

Arrête temporairement une interface de liaison dans le laboratoire. Observe l'état BGP, les routes retirées et la connectivité entre les deux clients.

**Correction attendue :** la session correspondante devient indisponible après la détection de la panne. Les routes qui ne disposent plus d'un chemin valide sont retirées ou recalculées. Les commandes de supervision et les journaux permettent de suivre le changement.

### Exercice C — Confondre une session et le service

Laisse la session eBGP à l'état `Established`, mais retire le préfixe du réseau distant de la politique sortante de R2.

**Correction attendue :** la session reste établie, mais la route attendue ne sera plus annoncée à l'autre client. Cet exercice démontre que l'état de session et l'état du service de transit ne sont pas identiques.

# Partie X — Exercices corrigés

## 40. Questions de compréhension

### Question 1

Quelle est la différence entre un AS et un ASN ?

**Correction :** un AS est un ensemble de réseaux et de routeurs exploités sous une politique de routage commune vis-à-vis de l'extérieur. L'ASN est le numéro utilisé pour l'identifier dans le routage interdomaines.

### Question 2

Pourquoi une session BGP `Established` ne garantit-elle pas que le réseau distant soit joignable ?

**Correction :** `Established` indique que la session BGP est formée. Les routes peuvent néanmoins être absentes, filtrées, inéligibles ou non installées. Le prochain saut, les routes de retour, les ACL et le transfert IP peuvent également poser problème.

### Question 3

Quelle différence existe entre une politique entrante et une politique sortante ?

**Correction :** la politique entrante filtre ou modifie les routes reçues d'un voisin. La politique sortante sélectionne les routes qu'on annonce à un voisin précis.

### Question 4

Quel attribut est couramment utilisé pour préférer une sortie depuis son propre AS ?

**Correction :** LOCAL_PREF. Une valeur plus élevée est généralement préférée dans la politique de décision habituelle. Les implémentations et les règles locales doivent toutefois être vérifiées.

### Question 5

Pourquoi l'AS_PATH ne permet-il pas toujours de choisir la route la plus courte ?

**Correction :** les autres attributs et politiques peuvent être évalués avant la longueur d'AS_PATH. Par exemple, un LOCAL_PREF plus élevé peut faire préférer une route ayant un chemin AS_PATH plus long.

### Question 6

Un IXP établit-il automatiquement une session BGP entre tous ses membres ?

**Correction :** non. L'IXP fournit une infrastructure d'interconnexion. Les membres choisissent leurs sessions, éventuellement bilatérales ou via un route server, selon les services et règles de l'IXP.

### Question 7

Une communauté BGP constitue-t-elle une preuve cryptographique qu'une route est légitime ?

**Correction :** non. Une communauté est une étiquette utilisée dans les politiques. Elle peut être modifiée pendant la propagation. Elle ne remplace pas les filtres ni la validation d'origine.

### Question 8

Quel est le but d'une limite maximum-prefix ?

**Correction :** limiter le nombre de préfixes reçus ou déclencher un comportement d'alerte ou de protection lorsqu'un seuil est dépassé. Elle complète les filtres mais ne les remplace pas.

### Question 9

Que vérifie principalement la validation RPKI de l'origine ?

**Correction :** elle vérifie si l'AS d'origine et la longueur du préfixe annoncé sont conformes à une autorisation ROA applicable. Elle ne valide pas l'intégralité du chemin AS_PATH.

### Question 10

Qu'est-ce qu'une fuite de routes ?

**Correction :** c'est la propagation d'annonces BGP au-delà de la portée prévue par les relations et les politiques de routage. Elle peut être due à une mauvaise configuration ou à un comportement malveillant.

## 41. Exercice de sélection de route

Un routeur apprend deux routes vers `198.51.100.0/24` :

| Critère | Route A | Route B |
|---|---:|---:|
| LOCAL_PREF | 180 | 100 |
| AS_PATH | 3 ASN | 1 ASN |
| ORIGIN | IGP | IGP |
| NEXT_HOP | Joignable | Joignable |

On suppose que LOCAL_PREF est comparé avant AS_PATH, que les deux routes sont éligibles et qu'aucun critère antérieur non indiqué ne les départage.

**Question :** quelle route est préférée ?

**Correction :** la route A, car son LOCAL_PREF est plus élevé. Le chemin AS_PATH plus court de la route B ne l'emporte pas sur ce critère antérieur.

## 42. Exercice de politique de transit

Un opérateur AS65010 apprend des routes de ses deux fournisseurs AS65020 et AS65030. Il souhaite utiliser AS65020 comme sortie principale et AS65030 comme sortie de secours.

**Questions :**

1. Quel attribut est couramment utilisé pour influencer la sortie choisie à l'intérieur d'AS65010 ?
2. Quelle valeur doit généralement être plus élevée pour AS65020 ?
3. Cette décision contrôle-t-elle aussi le chemin aller vers les préfixes d'AS65010 ?

**Correction :**

1. LOCAL_PREF.
2. Le LOCAL_PREF des routes apprises d'AS65020 est généralement configuré plus haut que celui d'AS65030 pour les destinations concernées.
3. Non. LOCAL_PREF influence principalement la décision locale de sortie. Le trafic entrant dépend des routes et politiques appliquées par les réseaux distants. Il peut être influencé par des mécanismes comme AS-path prepend, MED ou des communautés acceptées par les fournisseurs, sans garantie absolue.

# Partie XI — Défi final corrigé

## 43. Défi : concevoir une politique eBGP sécurisée pour un petit opérateur

### Scénario

L'opérateur fictif NovaNet exploite AS65010 et possède le préfixe de laboratoire `203.0.113.0/24`. Il est connecté à deux fournisseurs fictifs : AS65020 et AS65030.

Il souhaite :

- annoncer uniquement son propre préfixe à chacun de ses fournisseurs ;
- accepter de chaque fournisseur uniquement les routes prévues par le service ;
- préférer AS65020 pour le trafic sortant, tout en gardant AS65030 en solution de repli ;
- limiter les conséquences d'une erreur d'annonce ;
- vérifier la connectivité après une panne d'un fournisseur.

### Travail demandé

1. Expliquer pourquoi deux sessions eBGP sont nécessaires.
2. Définir la politique sortante de NovaNet.
3. Décrire une politique entrante appropriée.
4. Expliquer comment LOCAL_PREF pourrait sélectionner la sortie principale.
5. Citer quatre protections importantes.
6. Donner une procédure de vérification après une panne.
7. Expliquer pourquoi il faut aussi contrôler les annonces perçues depuis l'extérieur.

### Correction détaillée

**1. Deux sessions eBGP**

Une session eBGP est établie avec chaque voisin, car AS65010 est distinct d'AS65020 et d'AS65030. Chaque relation doit être documentée et configurée séparément.

**2. Politique sortante**

La politique sortante doit autoriser uniquement le préfixe `203.0.113.0/24` si c'est bien le seul préfixe destiné à être annoncé. Il faut vérifier la route localement et contrôler les annonces envoyées à chaque voisin. Les plages d'exemple sont réservées à la documentation : il ne faut jamais les annoncer sur Internet.

**3. Politique entrante**

La politique dépend du service contracté. NovaNet doit documenter si chaque fournisseur livre une route par défaut, un ensemble limité de routes ou une table plus complète. Les filtres doivent accepter les préfixes attendus et rejeter les annonces non autorisées. Une limite de préfixes adaptée à la quantité attendue complète ce filtrage.

**4. Choix du transit principal**

NovaNet peut attribuer aux routes apprises d'AS65020 un LOCAL_PREF plus élevé que celui des routes équivalentes apprises d'AS65030. Si les routes sont disponibles et les autres conditions appropriées, le trafic sortant préférera alors AS65020. Si AS65020 tombe en panne et que ses routes sont retirées, les routes d'AS65030 peuvent devenir utilisables.

**5. Protections**

Une politique entrante explicite, une politique sortante explicite, des filtres de préfixes et une limite de préfixes sont des protections fondamentales. On peut compléter ces mesures par la validation de l'origine RPKI, la surveillance, la protection des sessions et l'utilisation de mécanismes adaptés à la prévention des fuites de routes.

**6. Vérification après panne**

Il faut observer l'état de l'interface et de la session BGP d'AS65020, vérifier le retrait des routes apprises par cette session, contrôler la sélection des routes restantes et vérifier le prochain saut. Ensuite, il faut tester le trafic dans les deux sens, consulter les journaux et confirmer que la connectivité est effectivement rétablie via AS65030.

**7. Contrôle externe**

Les annonces locales ne suffisent pas à prouver que le reste d'Internet les voit correctement. Les opérateurs doivent contrôler leurs annonces à l'export, consulter les données de routage externes ou les outils de leurs fournisseurs et surveiller les variations inattendues de préfixes ou d'AS_PATH.

## 44. Critères d'évaluation du défi

| Compétence | Réussite attendue |
|---|---|
| Compréhension eBGP | Explique le rôle de chaque voisin et de chaque session |
| Politique sortante | Limite les annonces aux préfixes autorisés |
| Politique entrante | Décrit la portée de routage prévue et les filtres associés |
| Sélection BGP | Explique le rôle de LOCAL_PREF sans le confondre avec AS_PATH |
| Sécurité | Cite le filtrage, la limite de préfixes et la validation/monitoring adaptés |
| Résilience | Explique la bascule et la vérification dans les deux sens |
| Exploitation | Distingue session établie, route sélectionnée et connectivité effective |

# Partie XII — Synthèse et préparation du niveau expert

## 45. Les idées essentielles à retenir

1. BGP échange des informations de joignabilité entre systèmes autonomes ; il ne garantit pas à lui seul que le service distant fonctionne.
2. Les relations client-fournisseur, peering et transit influencent les politiques d'annonce.
3. Le plan de contrôle BGP et le plan de transfert des paquets sont deux fonctions distinctes.
4. Les politiques entrantes et sortantes doivent être explicites et propres à chaque voisin.
5. `AS_PATH` décrit les AS traversés, mais un chemin plus court n'est pas forcément préféré.
6. `LOCAL_PREF` influence principalement le choix de sortie à l'intérieur de son propre AS.
7. `MED` peut influencer le choix d'un point d'entrée par un AS voisin, selon sa politique.
8. Les communautés servent d'étiquettes de politique ; leur signification dépend de l'opérateur qui les définit.
9. Les filtres et les limites de préfixes réduisent le risque d'annonces accidentelles, sans remplacer une politique complète.
10. Le multihoming améliore les options de résilience, mais ajoute de la complexité et peut créer de l'asymétrie.
11. RPKI valide l'autorisation de l'origine et la longueur du préfixe ; elle ne valide pas à elle seule tout le chemin.
12. Une session `Established` n'est pas une preuve de connectivité de bout en bout.
13. Les fuites de routes sont souvent liées à des politiques incorrectes ou absentes.
14. Les mécanismes de sécurité doivent être accompagnés de supervision, de documentation et de procédures de modification contrôlées.

## 46. Glossaire

| Terme | Définition |
|---|---|
| AS | Ensemble de réseaux sous une administration et une politique de routage cohérente vis-à-vis de l'extérieur |
| ASN | Numéro identifiant un système autonome |
| BGP | Protocole de routage interdomaines |
| eBGP | Session BGP entre des AS différents |
| iBGP | Session BGP entre routeurs du même AS |
| Préfixe | Bloc d'adresses IP représenté par une adresse réseau et une longueur CIDR |
| IXP | Infrastructure d'interconnexion entre réseaux indépendants |
| Route server | Service de distribution des annonces BGP aux participants d'un IXP, sans être nécessairement dans le chemin de transfert des paquets |
| Peering | Échange de trafic et de routes entre réseaux selon un accord |
| Transit IP | Service donnant accès à d'autres réseaux via un fournisseur |
| AS_PATH | Attribut indiquant les AS traversés par une annonce BGP |
| NEXT_HOP | Attribut identifiant le prochain saut vers la destination annoncée |
| LOCAL_PREF | Attribut utilisé principalement pour préférer une route de sortie à l'intérieur d'un AS |
| MED | Attribut pouvant influencer le choix du point d'entrée chez un AS voisin |
| ORIGIN | Attribut BGP indiquant l'origine historique de l'information de route |
| Community | Étiquette BGP utilisée pour appliquer ou transmettre une politique |
| Prefix-list | Liste de préfixes autorisés ou filtrés selon des critères de longueur |
| Route-map | Mécanisme de politique, notamment chez Cisco, permettant de filtrer ou de modifier des routes |
| Route leak | Propagation d'une annonce au-delà de la portée prévue |
| RPKI | Infrastructure permettant de vérifier des autorisations liées aux ressources Internet |
| ROA | Autorisation indiquant quel AS peut annoncer un préfixe et, si précisé, sa longueur maximale |
| Multihoming | Connexion d'un réseau à plusieurs fournisseurs ou chemins externes |
| RIB | Base de données de routage ; le sens précis dépend du contexte de l'implémentation |
| FIB | Table utilisée pour le transfert effectif des paquets |
| Maximum-prefix | Mécanisme de limitation ou de surveillance du nombre de préfixes reçus d'un voisin |

## 47. Suite du parcours : BGP Peering & Internet — Expert

Le niveau expert pourra approfondir les sujets suivants :

- architecture BGP à grande échelle et conception multi-routeurs ;
- iBGP full mesh et route reflectors ;
- communautés classiques, étendues et Large Communities dans les politiques avancées ;
- agrégation, résumé de routes et gestion des annonces plus spécifiques ;
- ingénierie de trafic à l'entrée et à la sortie ;
- multihoming avancé, redondance et convergence ;
- RPKI à grande échelle et traitement opérationnel des annonces invalides ;
- rôles BGP, attribut OTC et prévention des fuites ;
- supervision, analyse des incidents, changements contrôlés et retour arrière ;
- conception de politiques adaptées aux relations client, fournisseur, pair et route server.

# Références techniques

Les liens ci-dessous mènent à des documents techniques de référence. Ils permettent d'approfondir le fonctionnement du protocole, ses extensions et les bonnes pratiques de sécurité.

1. **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : spécification de base de BGP. https://www.rfc-editor.org/rfc/rfc4271.html
2. **RFC 8212 — Default External BGP Route Propagation Behavior without Policies** : comportement eBGP sans politique explicite. https://www.rfc-editor.org/rfc/rfc8212.html
3. **RFC 4456 — BGP Route Reflection** : route reflection pour la montée en échelle d'iBGP. https://www.rfc-editor.org/rfc/rfc4456.html
4. **RFC 1997 — BGP Communities Attribute** : communautés BGP classiques. https://www.rfc-editor.org/rfc/rfc1997.html
5. **RFC 8092 — BGP Large Communities Attribute** : communautés BGP de grande taille. https://www.rfc-editor.org/rfc/rfc8092.html
6. **RFC 7454 — BGP Operations and Security** : recommandations opérationnelles et de sécurité. https://www.rfc-editor.org/rfc/rfc7454.html
7. **RFC 7908 — Problem Definition and Classification of BGP Route Leaks** : définition et classification des fuites de routes. https://www.rfc-editor.org/rfc/rfc7908.html
8. **RFC 9234 — Route Leak Prevention and Detection Using Roles in UPDATE and OPEN Messages** : rôles BGP et attribut OTC. https://www.rfc-editor.org/rfc/rfc9234.html
9. **RFC 6811 — BGP Prefix Origin Validation** : validation de l'origine des préfixes, à lire avec ses mises à jour ultérieures. https://www.rfc-editor.org/rfc/rfc6811.html
10. **RIPE NCC — BGP Origin Validation** : explication opérationnelle des états RPKI. https://www.ripe.net/manage-ips-and-asns/resource-management/rpki/bgp-origin-validation/
11. **FRRouting — BGP documentation** : référence de configuration pour l'implémentation FRR. https://docs.frrouting.org/en/latest/bgp.html

Les commandes de configuration présentées dans le laboratoire sont des exemples pédagogiques et doivent être adaptées à la plateforme. Avant une interconnexion réelle, il faut faire valider les préfixes, les relations de routage, les politiques d'importation et d'exportation, la sécurité, la supervision et le plan de retour arrière.
