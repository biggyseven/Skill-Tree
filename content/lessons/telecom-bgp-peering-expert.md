
# 📡 OPÉRATEURS & TÉLÉCOMS — BGP Peering & Internet
## Niveau Expert — `telecom-bgp-peering-expert.md`

> **Positionnement :** troisième cours du parcours Opérateurs & Télécoms, après Fibre Optique & DWDM (débutant) et MPLS-TP & Métro Ethernet (intermédiaire).
>
> **Niveau :** Expert — ingénierie réseau opérateur, interconnexion IP, architecture multihomée, politiques de routage, résilience et sécurité du routage global.
>
> **Objectif général :** concevoir, déployer, sécuriser, superviser et dépanner une architecture BGP de niveau opérateur, capable de relier plusieurs réseaux autonomes, plusieurs transitaires et plusieurs points d'échange Internet, sans provoquer de fuite de routes ni compromettre la stabilité du routage.

# 1. Présentation du cours

## 1.1. Pourquoi BGP est-il fondamental pour les opérateurs ?

Internet n'est pas un réseau unique exploité par une seule organisation. C'est un ensemble de réseaux indépendants, appelés **systèmes autonomes** ou **Autonomous Systems (AS)**, qui échangent des informations de joignabilité pour permettre aux paquets de traverser plusieurs domaines administratifs.

Ces réseaux appartiennent notamment à :

- Des fournisseurs d'accès à Internet (FAI).
- Des opérateurs mobiles.
- Des opérateurs de transport IP.
- Des fournisseurs de transit international.
- Des fournisseurs de contenus et de services cloud.
- Des entreprises multihomées.
- Des universités, des administrations et des grandes organisations.
- Des réseaux de diffusion de contenu (CDN).
- Des plateformes de cloud et des infrastructures distribuées.

Le protocole **BGP — Border Gateway Protocol** permet à ces systèmes autonomes de communiquer leurs routes et d'appliquer des politiques de routage indépendantes.

BGP ne cherche pas simplement le chemin physiquement le plus court. Il choisit un chemin parmi plusieurs possibilités en fonction d'attributs, de politiques administratives, de règles locales et de critères de sélection.

C'est une différence fondamentale avec un protocole IGP comme OSPF ou IS-IS.

```text
                  ARCHITECTURE LOGIQUE D'INTERNET

       +------------------+          +------------------+
       |      AS 64510    |          |      AS 64520    |
       |   Opérateur A    |          |   Opérateur B    |
       |                  |          |                  |
       | Routeur de bord  |----------| Routeur de bord  |
       +------------------+   eBGP   +------------------+
                |                              |
                |                              |
                |                              |
       +------------------+          +------------------+
       |      AS 64530    |----------|      AS 64540    |
       |     Transit C    |  eBGP    |   Fournisseur    |
       |                  |          |   de contenus    |
       +------------------+          +------------------+

       Chaque AS possède :
       - sa propre administration ;
       - ses propres politiques de routage ;
       - ses propres préfixes et/ou routes apprises ;
       - ses propres objectifs de disponibilité et de coût.

       Les connexions entre AS sont des relations techniques
       et commerciales distinctes.
```

Les numéros d'AS utilisés dans les exemples de ce cours sont réservés à la documentation ou à des environnements de laboratoire.

## 1.2. Ce que vous devez savoir faire à la fin du cours

À l'issue de ce parcours, vous devez être capable de :

1. Concevoir une architecture BGP multihomée.
2. Distinguer transit IP, peering privé et peering public.
3. Construire une architecture de routage avec plusieurs opérateurs.
4. Définir des politiques d'importation et d'exportation de routes.
5. Maîtriser les attributs BGP et leur influence sur les décisions.
6. Déployer des sessions eBGP et iBGP.
7. Comprendre les route reflectors et les limites du routage iBGP.
8. Configurer un peering sur un IXP avec ou sans route server.
9. Concevoir des politiques de préférence et d'ingénierie de trafic.
10. Sécuriser les sessions et filtrer les annonces.
11. Exploiter RPKI, ROA et la validation d'origine des routes.
12. Comprendre les limites de la validation d'origine et les attaques de chemin.
13. Détecter les fuites de routes, les détournements de préfixes et les problèmes de propagation.
14. Diagnostiquer une session BGP établie mais inutilisable.
15. Déployer des mécanismes de résilience et de convergence.
16. Concevoir une stratégie de supervision et de gestion des incidents.
17. Réaliser un laboratoire complet avec plusieurs AS, des transitaires, un IXP et des politiques de filtrage.

## 1.3. Prérequis

Ce cours suppose que vous maîtrisez déjà :

- IPv4 et IPv6.
- Le calcul des préfixes CIDR.
- Les tables de routage.
- Les protocoles Ethernet et IP.
- Les VLAN, le QinQ et le transport de services opérateur.
- Le routage statique.
- Les bases d'OSPF ou d'IS-IS.
- Les interfaces physiques et logiques.
- Les notions de MTU, de passerelle et de next-hop.
- Les commandes de diagnostic réseau.

Les connaissances acquises en Métro Ethernet et MPLS-TP sont utiles pour comprendre les infrastructures qui transportent les sessions BGP, mais BGP reste un protocole de routage de couche 3, distinct du transport Ethernet et MPLS.

## 1.4. Environnement pédagogique

Les exemples de configuration s'appuient principalement sur **FRRouting (FRR)**, avec quelques commandes de diagnostic Linux.

Certaines syntaxes alternatives sont fournies à titre d'illustration pour les équipements Cisco IOS/IOS XE ou d'autres environnements. Les noms de commandes, les fonctionnalités disponibles et les comportements peuvent varier selon les versions, les systèmes d'exploitation réseau et les licences.

Les configurations sont pédagogiques : elles doivent être adaptées à la plateforme cible, testées et validées avant toute utilisation en production.

# 2. Fondamentaux du routage interdomaines

## 2.1. Qu'est-ce qu'un système autonome ?

Un **Autonomous System (AS)** est un ensemble de préfixes IP et de routeurs administrés selon une politique de routage commune, présenté au reste d'Internet sous un identifiant de système autonome.

Le numéro d'AS est attribué selon les procédures de l'organisme de registre Internet régional compétent.

Les opérateurs peuvent utiliser :

- Des numéros d'AS publics pour leur présence sur Internet.
- Des numéros d'AS privés dans des environnements internes ou des scénarios appropriés.
- Des numéros distincts pour des réseaux ou activités différents, lorsque l'architecture et la politique de routage le justifient.

Un AS ne correspond pas nécessairement à un bâtiment, un routeur, un pays ou une seule technologie.

Un opérateur peut exploiter plusieurs centaines de routeurs dans un même AS.

```text
                AS 64510 — OPÉRATEUR ALPHA

    +--------------------------------------------------+
    |                                                  |
    |  +------------+          +------------+          |
    |  | Routeur R1 |----------| Routeur R2 |          |
    |  | Core       |          | Core       |          |
    |  +------------+          +------------+          |
    |        |                        |                |
    |        | iBGP                   | iBGP           |
    |        |                        |                |
    |  +------------+          +------------+          |
    |  | Routeur PE1|          | Routeur PE2|          |
    |  | Bord       |          | Bord       |          |
    |  +------------+          +------------+          |
    |        |                        |                |
    +--------|------------------------|----------------+
             |                        |
           eBGP                     eBGP
             |                        |
          Transit A                Transit B

    Tous les routeurs montrés appartiennent au même AS,
    sauf les équipements des deux transitaires.
```

## 2.2. AS public et AS privé

Les plages d'AS privées sont définies notamment par la RFC 6996.

| Type | Plage |
|---|---|
| AS privés 16 bits | 64512 à 65534 |
| AS privés 32 bits | 4200000000 à 4294967294 |

Le numéro 65535 est réservé et ne doit pas être traité comme un numéro privé ordinaire.

Les AS privés peuvent être utilisés dans des réseaux internes ou des contextes prévus à cet effet. Ils ne doivent pas être propagés aveuglément dans le routage public.

Avant d'utiliser un AS privé avec un fournisseur, il faut définir explicitement les règles de suppression ou de conservation de cet AS dans le chemin AS_PATH.

L'utilisation d'un AS privé n'élimine pas les contraintes liées aux préfixes, aux politiques de routage et aux accords contractuels.

## 2.3. Pourquoi BGP est différent d'OSPF ou d'IS-IS

OSPF et IS-IS sont généralement utilisés comme IGP à l'intérieur d'un domaine administratif.

Ils construisent une représentation de la topologie et calculent des chemins selon des métriques.

BGP est un protocole de routage interdomaines qui échange des informations de joignabilité et applique des politiques.

| Critère | OSPF / IS-IS | BGP |
|---|---|---|
| Usage courant | Routage interne | Routage interdomaines et politiques avancées |
| Nature des informations | État des liens | Préfixes et attributs de chemin |
| Décision | Métriques de l'IGP | Attributs et politique locale |
| Portée habituelle | Domaine IGP | Plusieurs AS pour eBGP |
| Transport | IP directement selon le protocole | TCP, port 179 |
| Connaissance globale de la topologie | Dans la portée IGP | Non, pas de vue globale complète |
| Relations commerciales | Pas un mécanisme natif | Traduites en politiques de routage |
| Convergence | Dépend de l'IGP et de sa topologie | Dépend des sessions, politiques, annonces et mécanismes BGP |

BGP ne remplace pas l'IGP d'un opérateur.

Un opérateur utilise souvent un IGP pour assurer la joignabilité interne de ses loopbacks et de ses infrastructures, tandis que BGP transporte les routes interdomaines.

```text
                     PLAN DE ROUTAGE

    +------------------------------------------+
    |             ROUTAGE EXTERNE              |
    |                                          |
    |  eBGP : échanges entre AS différents     |
    |  iBGP : distribution interne des routes   |
    +--------------------+---------------------+
                         |
                         |
    +--------------------+---------------------+
    |             ROUTAGE INTERNE              |
    |                                          |
    |  OSPF / IS-IS : reachability interne     |
    |  Loopbacks, liens et chemins du core     |
    +--------------------+---------------------+
                         |
                         |
    +--------------------+---------------------+
    |          INFRASTRUCTURE DE TRANSPORT     |
    |                                          |
    | Ethernet / IP / MPLS / liens optiques    |
    +------------------------------------------+
```

## 2.4. eBGP et iBGP

### eBGP — External BGP

eBGP échange des routes entre systèmes autonomes différents.

Exemple :

```text
AS 64510                    AS 64520

+----------------+         +----------------+
| Routeur A      |         | Routeur B      |
|                |---------|                |
| Local AS 64510 |  eBGP   | Local AS 64520 |
+----------------+         +----------------+
```

Dans le fonctionnement classique d'eBGP, le routeur annonce son propre AS dans AS_PATH lorsqu'il propage un préfixe appris depuis une autre origine ou une route interne appropriée.

Un routeur rejette normalement une route dont AS_PATH contient son propre AS, afin d'éviter certaines boucles de routage. Des exceptions et mécanismes particuliers existent, notamment dans des environnements utilisant des confédérations ou des politiques spécifiques.

### iBGP — Internal BGP

iBGP distribue les routes BGP à l'intérieur d'un même AS.

```text
                    AS 64510

           +---------------------+
           | Routeur de bord R1  |
           +---------------------+
                     |
                     | iBGP
                     |
           +---------------------+
           | Routeur de cœur R2  |
           +---------------------+
                     |
                     | iBGP
                     |
           +---------------------+
           | Routeur de bord R3  |
           +---------------------+
```

Un point fondamental : dans le fonctionnement classique de BGP, une route apprise d'un pair iBGP n'est pas réannoncée à un autre pair iBGP.

Cette règle contribue à prévenir les boucles, mais impose une architecture de distribution interne.

Les solutions habituelles sont :

- Le maillage iBGP complet.
- Les route reflectors.
- Les confédérations BGP dans des architectures spécifiques.

# 3. Architecture d'interconnexion Internet

## 3.1. Les trois relations fondamentales

Un opérateur peut établir plusieurs types de relations avec d'autres réseaux.

### A. Transit IP

Un fournisseur de transit permet à son client d'atteindre une partie importante ou la totalité de l'Internet accessible via son réseau.

Le client reçoit généralement une table de routes importante, une route par défaut ou un ensemble de routes défini contractuellement.

Le fournisseur annonce généralement les routes nécessaires à la joignabilité du client, selon les politiques convenues.

Le transit est une relation commerciale et technique. La politique exacte dépend du contrat.

### B. Peering privé

Deux réseaux établissent une interconnexion directe, souvent dans un datacenter ou un point de présence partagé.

Le peering sert généralement à échanger le trafic destiné aux réseaux des deux participants et aux routes qu'ils acceptent de propager.

Le peering n'implique pas automatiquement un accès complet à Internet.

### C. Peering public

Plusieurs réseaux se connectent à une infrastructure commune appelée **Internet Exchange Point (IXP)**.

Ils peuvent établir des sessions BGP bilatérales ou utiliser un ou plusieurs route servers.

Le route server distribue des routes entre participants sans être nécessairement présent dans le chemin de données du trafic.

```text
                         INTERNET

          +----------------+     +----------------+
          | Transit A      |     | Transit B      |
          | AS 64520       |     | AS 64530       |
          +--------+-------+     +-------+--------+
                   |                     |
                 eBGP                  eBGP
                   |                     |
          +--------+---------------------+--------+
          |             AS 64510                   |
          |             OPÉRATEUR                   |
          |                                        |
          |         Routeurs de bord               |
          |                |                       |
          |             Réseau IP                  |
          +----------------+-----------------------+
                           |
                           | Connexion à l'IXP
                           |
                   +-------+--------+
                   | IXP            |
                   | Switch fabric  |
                   | Route server   |
                   +-------+--------+
                           |
              +------------+------------+
              |                         |
        +-----+------+            +-----+------+
        | AS 64540   |            | AS 64550   |
        | CDN        |            | Réseau     |
        |            |            | de contenu |
        +------------+            +------------+
```

## 3.2. Transit et peering : différences opérationnelles

| Critère | Transit | Peering |
|---|---|---|
| Objectif | Accès à des routes externes étendues | Échange de trafic entre participants |
| Portée des routes | Souvent très large | Généralement limitée par l'accord |
| Modèle économique | Souvent payant selon le débit ou la capacité | Variable : gratuit, payant ou conditionnel |
| Route par défaut | Possible | Pas automatique |
| Accès à tout Internet | Selon le service contracté | Non garanti |
| Contrôle des annonces | Politiques contractuelles | Politiques de peering |
| Risque de fuite | Présent | Présent |
| Besoin de filtrage | Obligatoire en pratique | Obligatoire en pratique |

Il faut éviter une erreur fréquente : considérer qu'une session BGP établie signifie que la relation commerciale est correctement mise en œuvre.

Une session peut être opérationnelle tout en annonçant des routes interdites, en recevant des routes inutilisables ou en transportant du trafic asymétrique.

## 3.3. Architecture multihomée

Une entreprise ou un opérateur est multihomé lorsqu'il est connecté à plusieurs réseaux externes, par exemple deux fournisseurs de transit.

```text
                        TRANSIT A
                        AS 64520
                            |
                           eBGP
                            |
                 +----------+----------+
                 |                     |
                 |   AS 64510          |
                 |   Réseau client     |
                 |                     |
                 +----------+----------+
                            |
                           eBGP
                            |
                        TRANSIT B
                        AS 64530
```

Cette architecture peut améliorer la résilience, mais seulement si les chemins sont réellement indépendants.

Deux connexions vers des fournisseurs différents ne garantissent pas l'absence de panne commune. Elles peuvent partager :

- Le même fourreau de fibre.
- Le même datacenter.
- Le même système électrique.
- Le même routeur de bord.
- Le même opérateur de transport.
- Le même câble sous-marin.
- Le même point de présence physique.

L'ingénierie de résilience doit donc couvrir la diversité physique, la diversité de transport, la diversité des routeurs, la diversité des opérateurs et la diversité des chemins de propagation.

# 4. Anatomie d'une session BGP

## 4.1. BGP utilise TCP

BGP utilise TCP, traditionnellement sur le port 179.

Le transport TCP apporte un canal fiable, mais ne résout pas les problèmes de politique de routage, de convergence globale ou de validation des annonces.

Une session BGP exige notamment :

- Une connectivité IP entre les pairs.
- Des paramètres de session compatibles.
- Une configuration cohérente des AS.
- L'autorisation de la connexion TCP.
- Une configuration de sécurité compatible.
- Des capacités BGP compatibles.
- Des politiques d'annonce cohérentes.

Le port 179 ne doit pas être exposé sans contrôle à tous les réseaux.

## 4.2. Les principaux messages BGP

### OPEN

Le message OPEN permet d'initialiser une session et d'échanger notamment les informations relatives à l'AS, à l'identifiant BGP et aux capacités prises en charge.

### UPDATE

Le message UPDATE annonce des routes, retire des routes ou réalise les deux opérations.

Les UPDATE transportent les préfixes et les attributs associés.

### KEEPALIVE

Le message KEEPALIVE permet de confirmer que la session reste active lorsqu'aucun autre mécanisme ou message ne remplit ce rôle.

### NOTIFICATION

Le message NOTIFICATION signale une erreur et conduit généralement à la fermeture de la session.

### ROUTE-REFRESH

Le mécanisme ROUTE-REFRESH permet notamment de demander une nouvelle annonce des routes selon les capacités négociées, sans devoir nécessairement réinitialiser la session.

## 4.3. Les états BGP

Une session BGP suit une machine à états.

```text
                 +----------------+
                 |      Idle      |
                 +--------+-------+
                          |
                          v
                 +----------------+
                 |    Connect     |
                 +--------+-------+
                          |
                Connexion TCP réussie
                          |
                          v
                 +----------------+
                 |     OpenSent   |
                 +--------+-------+
                          |
                    OPEN accepté
                          |
                          v
                 +----------------+
                 |    OpenConfirm |
                 +--------+-------+
                          |
                     KEEPALIVE
                          |
                          v
                 +----------------+
                 |   Established  |
                 +----------------+
```

Les transitions peuvent revenir vers d'autres états à la suite d'une erreur, d'un timeout ou d'une fermeture de session.

### Idle

Le processus BGP n'a pas encore établi de session opérationnelle ou revient à son état initial.

### Connect

Le routeur tente d'établir la connexion TCP.

### Active

Le routeur tente de progresser dans l'établissement de la session après un échec de connexion ou une tentative infructueuse.

**Attention :** l'état Active ne signifie pas que la session est opérationnelle. Une session qui reste durablement en Active indique souvent un problème de transport, de configuration ou de filtrage.

### OpenSent

Le message OPEN a été envoyé et le routeur attend une réponse appropriée.

### OpenConfirm

Les paramètres OPEN ont été échangés et le routeur attend la confirmation de l'autre pair.

### Established

La session est établie et les annonces de routes peuvent être échangées.

Une session en Established ne prouve pas que le plan de données fonctionne correctement. Il faut encore vérifier les routes acceptées, les routes installées et les chemins réellement empruntés par les paquets.

# 5. Les attributs BGP

Les attributs BGP influencent la sélection et la propagation des routes.

Il est essentiel de comprendre la différence entre :

- La route reçue.
- La route acceptée après filtrage.
- La route candidate à la sélection.
- La meilleure route BGP.
- La route installée dans la RIB.
- La route effectivement utilisée par le plan de données.
- La route annoncée à un autre pair.

Ces étapes peuvent diverger.

## 5.1. AS_PATH

AS_PATH représente les informations de chemin AS associées à une route.

Exemple :

```text
Préfixe : 203.0.113.0/24

AS_PATH : 64520 64530 64540

Interprétation simplifiée :

Le préfixe a été propagé au travers de plusieurs AS.
Le routeur local peut utiliser AS_PATH dans sa politique
et dans la sélection de la route.
```

Les segments AS_PATH peuvent être plus complexes qu'une simple liste, notamment avec AS_SEQUENCE et AS_SET dans les formats et cas prévus par les spécifications.

AS_PATH joue plusieurs rôles :

- Indication du chemin de propagation inter-AS.
- Détection de certaines boucles.
- Entrée dans la sélection de route.
- Support de certaines politiques d'importation et d'exportation.

Une longueur AS_PATH plus courte peut être préférée selon l'algorithme de sélection appliqué, mais elle ne garantit pas que la route sera choisie.

La politique locale peut préférer un chemin plus long pour des raisons économiques, de sécurité ou d'ingénierie de trafic.

## 5.2. LOCAL_PREF

LOCAL_PREF exprime une préférence locale entre routes BGP dans un AS.

Plus la valeur est élevée, plus la route est préférée dans le comportement standard.

Exemple :

```text
Route A : LOCAL_PREF 300
Route B : LOCAL_PREF 200
Route C : LOCAL_PREF 100

Si les autres critères pertinents sont comparables :

Préférence locale :
A > B > C
```

LOCAL_PREF est généralement distribué aux pairs iBGP. Il n'est normalement pas propagé tel quel à un AS externe dans les annonces eBGP classiques.

C'est l'un des principaux outils de décision de sortie d'un AS.

Exemple de politique :

- Routes internes : préférence adaptée à l'architecture.
- Routes de clients : préférence élevée.
- Routes de peering : préférence intermédiaire ou élevée selon la stratégie.
- Routes de transit : préférence plus faible.

Ces valeurs ne constituent pas une norme universelle. Elles doivent refléter la politique propre à l'opérateur.

## 5.3. MED — Multi-Exit Discriminator

MED permet de communiquer une préférence relative entre plusieurs points d'entrée vers un même AS distant.

Exemple :

```text
                   AS 64510
                Réseau de destination
                  /            \
                 /              \
             Bord A            Bord B
               |                  |
             MED 50             MED 150
               |                  |
               +------ AS 64520 --+

Dans les conditions appropriées, le chemin via Bord A
peut être préféré par l'AS distant.
```

MED est généralement comparé entre routes issues du même AS voisin, mais son traitement dépend de la plateforme et des options de sélection.

Il ne faut pas confondre MED avec LOCAL_PREF :

- LOCAL_PREF exprime une préférence au sein de l'AS qui le définit.
- MED exprime une indication de préférence d'entrée communiquée à un AS voisin.

MED n'est pas une garantie absolue que le réseau distant choisira le point d'entrée souhaité.

## 5.4. NEXT_HOP

NEXT_HOP identifie le prochain saut associé à une route BGP.

Dans certains scénarios iBGP, une route reçue depuis un pair eBGP peut conserver un next-hop qui n'est pas directement joignable depuis tous les routeurs internes.

```text
              AS 64510

       +------------------+
       | Routeur de bord  |
       | R1               |
       +------------------+
                |
                | iBGP
                |
       +------------------+
       | Routeur interne  |
       | R2               |
       +------------------+

Route annoncée :
203.0.113.0/24

NEXT_HOP :
adresse du routeur externe ou de bord

Condition :
R2 doit disposer d'une route permettant d'atteindre
le NEXT_HOP pour utiliser le chemin.
```

Le routage interne doit donc assurer la joignabilité des next-hops nécessaires.

Des mécanismes tels que `next-hop-self` peuvent modifier le next-hop annoncé dans certaines implémentations et certains scénarios.

Ils doivent être utilisés selon la topologie, et non comme une correction automatique de tout problème de reachability.

## 5.5. ORIGIN

L'attribut ORIGIN décrit la manière dont l'information a été introduite dans BGP selon les règles historiques du protocole.

Les valeurs sont :

- IGP.
- EGP, valeur historique.
- INCOMPLETE.

Il ne faut pas interpréter ORIGIN comme une preuve cryptographique de propriété d'un préfixe.

ORIGIN et la validation d'origine RPKI sont deux notions différentes.

## 5.6. COMMUNITIES

Les communautés permettent d'associer des étiquettes aux routes.

Elles facilitent la mise en œuvre de politiques sans devoir maintenir une multitude de règles individuelles sur chaque préfixe.

Les familles principales sont :

- Communities classiques, 32 bits.
- Large Communities, adaptées notamment aux AS 32 bits et aux politiques complexes.
- Extended Communities, utilisées dans différents domaines, notamment MPLS VPN.

Exemple conceptuel :

```text
Route reçue :
203.0.113.0/24

Communities :
64510:100
64510:200

Politique interne :
64510:100 = route apprise d'un peer
64510:200 = route autorisée à être annoncée à certains voisins
```

Les significations des communautés sont définies par l'opérateur ou par le service proposé par un fournisseur.

Il ne faut jamais supposer qu'une communauté inconnue a une signification universelle.

Les communautés réservées et les communautés documentées par un fournisseur doivent être interprétées selon leurs spécifications.

## 5.7. ATOMIC_AGGREGATE et AGGREGATOR

Ces attributs sont associés à certaines opérations d'agrégation de routes.

L'agrégation permet de représenter plusieurs routes plus spécifiques par une route moins spécifique lorsque cela est justifié.

Exemple :

```text
203.0.112.0/24
203.0.113.0/24
203.0.114.0/24
203.0.115.0/24

Agrégat possible, selon l'alignement et la couverture :
203.0.112.0/22
```

Un agrégat ne doit être annoncé que si le réseau peut effectivement acheminer le trafic destiné à l'ensemble du bloc annoncé.

Un agrégat mal construit peut provoquer un trou noir : l'annonce existe, mais certains sous-réseaux ne sont pas joignables.

Une route de rejet vers l'agrégat peut être utilisée pour éviter des boucles internes lorsque les routes plus spécifiques disparaissent, mais sa conception exige de vérifier que les routes plus spécifiques valides continuent d'être préférées.

## 5.8. Attributs obligatoires et facultatifs

Les attributs BGP appartiennent à plusieurs catégories définies par les spécifications.

On distingue notamment :

- Les attributs well-known mandatory.
- Les attributs well-known discretionary.
- Les attributs optional transitive.
- Les attributs optional non-transitive.

La catégorie détermine comment les implémentations doivent traiter les attributs connus ou inconnus.

Cette distinction est importante pour la compatibilité, la propagation des routes et les diagnostics d'erreurs UPDATE.

# 6. Sélection de la meilleure route

## 6.1. Le principe

Un routeur peut recevoir plusieurs chemins pour le même préfixe.

Il doit déterminer quel chemin privilégier selon son implémentation et sa politique.

La sélection BGP n'est pas simplement « le plus petit nombre d'AS ».

La décision peut dépendre de nombreux critères, dont :

- L'éligibilité du chemin.
- Les attributs de préférence locale.
- Les politiques de sécurité.
- La longueur AS_PATH.
- ORIGIN.
- MED, selon les règles de comparaison.
- Le type de voisin et certaines préférences internes.
- Les coûts et critères de départage de l'implémentation.
- La joignabilité du next-hop.
- Les options configurées par l'administrateur.

Les détails et l'ordre précis des critères de départage peuvent varier selon les implémentations et leurs versions.

## 6.2. Exemple de sélection

Supposons que trois routes atteignent le même préfixe.

| Route | LOCAL_PREF | AS_PATH | MED | Origine |
|---|---:|---|---:|---|
| A | 200 | 64520 64530 | 100 | IGP |
| B | 300 | 64540 64550 64560 | 200 | IGP |
| C | 100 | 64570 | 0 | IGP |

La route B possède le LOCAL_PREF le plus élevé.

Dans une politique standard où les routes sont éligibles et comparées selon les critères habituels, B peut être préférée même si son AS_PATH est plus long.

La décision ne doit pas être prise en examinant un seul attribut isolément.

## 6.3. Table de décision pédagogique

```text
Étape 1 :
La route est-elle valide et éligible ?
  |
  +-- Non --> Elle ne peut pas être utilisée comme meilleure route.
  |
  +-- Oui
       |
       v
Étape 2 :
Appliquer la politique locale.
  |
  v
Étape 3 :
Comparer les attributs selon l'algorithme de la plateforme.
  |
  v
Étape 4 :
Déterminer le meilleur chemin BGP.
  |
  v
Étape 5 :
Vérifier la compatibilité avec la RIB et le next-hop.
  |
  v
Étape 6 :
Vérifier la programmation du plan de données.
```

Il est possible qu'une route soit la meilleure route BGP sans être effectivement installée comme route active dans la table de routage IP, par exemple si une autre source de routage est préférée selon les règles locales ou si le next-hop est inaccessible.

## 6.4. ECMP et multipath BGP

Certaines plateformes permettent d'installer plusieurs chemins BGP dans le plan de données lorsque les conditions de multipath sont satisfaites.

Le multipath ne signifie pas nécessairement que tous les chemins de routes reçues sont installés.

Les critères de compatibilité peuvent inclure :

- Des attributs identiques ou suffisamment compatibles.
- Des contraintes spécifiques de plateforme.
- Des conditions d'AS_PATH.
- Des options de configuration.
- Une joignabilité valide des next-hops.

Le partage de charge s'effectue souvent par hachage des flux. Il ne garantit donc pas une répartition parfaitement égale du débit.

Il faut également distinguer multipath et sélection de meilleure route : une implémentation peut sélectionner une meilleure route BGP tout en installant plusieurs chemins utilisables dans la FIB.

# 7. Conception d'une politique BGP opérateur

## 7.1. Principe de base

Une politique BGP doit être définie avant la configuration des sessions.

Chaque session doit disposer d'une politique d'importation et d'une politique d'exportation explicites.

```text
                    ROUTES REÇUES
                         |
                         v
                +------------------+
                | Filtrage du pair |
                +------------------+
                         |
                         v
                +------------------+
                | Validation RPKI  |
                | et contrôles     |
                +------------------+
                         |
                         v
                +------------------+
                | Attribution des  |
                | communautés      |
                +------------------+
                         |
                         v
                +------------------+
                | LOCAL_PREF et    |
                | autres politiques|
                +------------------+
                         |
                         v
                +------------------+
                | Sélection BGP    |
                +------------------+
                         |
                         v
                  ROUTE RETENUE
```

Cette représentation est simplifiée. L'ordre exact de traitement dépend de l'implémentation, et les contrôles doivent être réalisés aux bons endroits dans la politique effective.

## 7.2. Filtrage à l'importation

Une politique d'importation doit vérifier au minimum :

- Que le préfixe est autorisé.
- Que sa longueur est acceptable.
- Que l'origine est cohérente avec les attentes.
- Que les AS_PATH interdits sont rejetés.
- Que les communautés sont interprétées correctement.
- Que les routes par défaut ne sont acceptées que si cela est prévu.
- Que les routes de documentation, privées ou spéciales ne sont pas propagées dans les contextes où elles sont interdites.
- Que les annonces correspondent au type de relation commerciale.
- Que les limites de volume sont raisonnables.

Le filtrage doit être adapté à la session.

Un client, un transitaire, un peer et un route server n'ont pas nécessairement les mêmes droits d'annonce.

## 7.3. Filtrage à l'exportation

Une politique d'exportation détermine quelles routes peuvent être annoncées à chaque voisin.

Elle doit notamment prévenir :

- L'annonce accidentelle d'une table complète à un peer qui ne l'a pas demandée.
- La propagation de routes apprises d'un transitaire à un autre dans des conditions non autorisées.
- La fuite de routes internes.
- L'annonce de préfixes non autorisés.
- L'annonce de préfixes plus spécifiques non prévus.
- La propagation de routes par défaut à des pairs non concernés.

Le principe de sécurité est le suivant :

**Une route ne doit pas être annoncée simplement parce qu'elle est présente dans la table BGP. Elle doit être explicitement autorisée pour le voisin concerné.**

## 7.4. Modèle de politique par relation

| Type de voisin | Routes reçues possibles | Routes annoncées possibles |
|---|---|---|
| Client | Préfixes déclarés et autorisés du client | Routes de transit et autres routes contractuellement autorisées |
| Transitaire | Table globale, table partielle ou défaut selon le contrat | Préfixes propres et routes client autorisées |
| Peer | Préfixes du réseau distant et routes prévues par l'accord | Préfixes propres et routes client selon la politique de peering |
| Route server IXP | Routes des participants selon les règles de l'IXP | Routes autorisées à ce participant |
| Routeur interne iBGP | Routes internes et routes BGP selon la conception | Routes internes selon les règles de distribution |

Ce tableau décrit des modèles généraux. Les politiques réelles dépendent des contrats, des règles de l'IXP et de l'architecture.

# 8. Exemple d'architecture opérateur multihomée

## 8.1. Objectif

Concevoir un opérateur disposant de :

- Deux routeurs de bord.
- Deux fournisseurs de transit.
- Une connexion à un IXP.
- Des routes internes distribuées par iBGP.
- Une politique de préférence locale.
- Une stratégie d'annonce de préfixes publics.
- Un filtrage d'entrée et de sortie.
- Une protection contre les annonces involontaires.

```text
                         TRANSIT A
                         AS 64520
                             |
                            eBGP
                             |
                    +--------+--------+
                    |   EDGE-1        |
                    |   AS 64510      |
                    +--------+--------+
                             |
                         Réseau IP
                             |
                    +--------+--------+
                    |   CORE-1        |
                    |   AS 64510      |
                    +--------+--------+
                             |
                         Réseau IP
                             |
                    +--------+--------+
                    |   EDGE-2        |
                    |   AS 64510      |
                    +--------+--------+
                             |
                            eBGP
                             |
                         TRANSIT B
                         AS 64530

              EDGE-1 ou routeur dédié vers l'IXP
                             |
                            eBGP
                             |
                      IXP / Route Server
```

Cette architecture représente une vue logique. Dans un déploiement réel, les liens, les interfaces, les routeurs et les chemins doivent être dimensionnés et documentés précisément.

## 8.2. Plan d'adressage de laboratoire

Les plages suivantes sont réservées à la documentation et ne doivent pas être utilisées comme adresses de service publiques réelles.

| Élément | Adresse ou préfixe pédagogique |
|---|---|
| AS opérateur | 64510 |
| Transit A | 64520 |
| Transit B | 64530 |
| AS client de laboratoire | 64540 |
| Préfixe de laboratoire | 203.0.113.0/24 |
| Lien EDGE-1 vers Transit A | 192.0.2.0/30 |
| Lien EDGE-2 vers Transit B | 192.0.2.4/30 |
| Loopback EDGE-1 | 198.51.100.1/32 |
| Loopback CORE-1 | 198.51.100.2/32 |
| Loopback EDGE-2 | 198.51.100.3/32 |

Les plages 192.0.2.0/24, 198.51.100.0/24 et 203.0.113.0/24 sont des plages de documentation. Leur présence dans les exemples ne signifie pas qu'elles sont routables sur Internet.

# 9. Configuration BGP avec FRRouting

## 9.1. Installation et vérifications initiales

Sur un environnement Linux compatible avec FRR :

```bash
sudo apt update
sudo apt install frr frr-pythontools
```

La disponibilité des paquets dépend de la distribution et de ses dépôts.

Vérifiez l'installation :

```bash
vtysh -c "show version"
```

Vérifiez les services :

```bash
systemctl status frr
```

Sur les systèmes qui utilisent la configuration FRR classique, le fichier de configuration est généralement :

```text
/etc/frr/frr.conf
```

Le service BGP doit être activé selon la configuration de la distribution, et le démon bgpd doit être démarré.

Ne modifiez pas une configuration de production sans sauvegarde et sans plan de retour arrière.

## 9.2. Configuration de base d'EDGE-1

Exemple illustratif de configuration FRR :

```text
frr defaults traditional
hostname EDGE-1
service integrated-vtysh-config
!
router bgp 64510
 bgp router-id 198.51.100.1
 no bgp ebgp-requires-policy
 neighbor 192.0.2.2 remote-as 64520
 !
 address-family ipv4 unicast
  neighbor 192.0.2.2 activate
 exit-address-family
!
```

**Attention :** `no bgp ebgp-requires-policy` désactive, sur les versions FRR qui prennent en charge cette option, le garde-fou imposant une politique explicite d'importation et d'exportation eBGP. Cette ligne est donnée uniquement pour expliquer une option de comportement. Elle ne doit pas être utilisée comme raccourci de configuration sûre en production.

Une configuration de production doit utiliser des politiques explicites et les mécanismes de protection adaptés à la version déployée.

La configuration doit également correspondre aux interfaces réellement configurées et à l'adresse du voisin.

## 9.3. Configuration d'une politique d'importation

Exemple de liste de préfixes et de route-map FRR :

```text
ip prefix-list TRANSIT-A-IN seq 10 permit 0.0.0.0/0 le 24
!
route-map TRANSIT-A-IN permit 10
 match ip address prefix-list TRANSIT-A-IN
 set local-preference 150
!
route-map TRANSIT-A-IN deny 100
!
```

Cette politique autorise les préfixes IPv4 compris entre /0 et /24.

Elle est volontairement large pour un exemple de laboratoire. **Elle ne constitue pas un filtre suffisant pour un transit Internet réel.**

Un filtre de production doit aussi prendre en compte les annonces spéciales, les longueurs de préfixes acceptables, les préfixes autorisés, les routes privées, la validation d'origine, les AS_PATH, les exigences du fournisseur et les limites de volume.

La politique peut être attachée à la session :

```text
router bgp 64510
 neighbor 192.0.2.2 route-map TRANSIT-A-IN in
```

Sur une version FRR compatible, vérifiez ensuite :

```text
show running-config
show bgp ipv4 unicast
show bgp ipv4 unicast neighbors 192.0.2.2
```

## 9.4. Préparer un filtre d'exportation

Supposons que l'opérateur ne souhaite annoncer que le préfixe de laboratoire autorisé.

```text
ip prefix-list OWN-PREFIXES seq 10 permit 203.0.113.0/24
!
route-map TRANSIT-A-OUT permit 10
 match ip address prefix-list OWN-PREFIXES
!
route-map TRANSIT-A-OUT deny 100
!
```

Application :

```text
router bgp 64510
 neighbor 192.0.2.2 route-map TRANSIT-A-OUT out
```

Cette politique exprime une règle simple : seules les routes correspondant au préfixe autorisé peuvent être exportées.

En production, il faut aussi vérifier que le préfixe est réellement détenu ou délégué à l'organisation, que son origine est autorisée, que le service accepte ce type d'annonce et que le réseau est effectivement joignable.

Il faut notamment éviter qu'un filtre d'exportation permissif permette l'annonce de routes reçues d'un transitaire.

## 9.5. Configuration d'une route annoncée

Pour annoncer un préfixe via une instruction `network`, la route correspondante doit normalement exister dans la table de routage IP selon le comportement de la plateforme et sa configuration.

Exemple :

```text
router bgp 64510
 address-family ipv4 unicast
  network 203.0.113.0/24
 exit-address-family
```

L'instruction `network` ne crée pas à elle seule l'interface, la route IP ou le service correspondant.

Il faut vérifier :

1. Que le préfixe est autorisé.
2. Que la route correspondante existe selon les conditions requises.
3. Que le routeur peut réellement acheminer le trafic.
4. Que la politique d'exportation autorise le préfixe.
5. Que le voisin accepte l'annonce.

Une annonce BGP valide sur le plan syntaxique peut néanmoins être incorrecte sur le plan opérationnel.

## 9.6. Vérification de la session

Commandes FRR usuelles :

```text
show bgp summary
show bgp ipv4 unicast summary
show bgp ipv4 unicast neighbors 192.0.2.2
show bgp ipv4 unicast
show ip route
```

Selon la version, les commandes et leurs alias peuvent varier.

Le résultat doit permettre de vérifier :

- L'état de la session.
- Le nombre de préfixes reçus.
- Les capacités négociées.
- Les timers.
- Les compteurs de messages.
- Les politiques appliquées.
- La présence des routes attendues.
- Le next-hop associé.
- La sélection de la meilleure route.

# 10. iBGP et route reflectors

## 10.1. Le problème du maillage complet

Dans le modèle classique iBGP, un routeur ne réannonce pas à un autre pair iBGP une route qu'il a apprise par iBGP.

Un maillage complet évite cette limitation, mais devient coûteux lorsque le nombre de routeurs augmente.

Le nombre de sessions dans un maillage complet de N routeurs est :

\[
\frac{N(N-1)}{2}
\]

Exemples :

| Routeurs | Sessions iBGP dans un maillage complet |
|---:|---:|
| 4 | 6 |
| 10 | 45 |
| 20 | 190 |
| 50 | 1225 |
| 100 | 4950 |

La croissance quadratique rend le maillage complet difficile à gérer dans les grandes infrastructures.

## 10.2. Route reflector

Un route reflector distribue des routes entre ses clients iBGP selon les règles de réflexion de routes.

```text
                 AS 64510

             +----------------+
             | Route Reflector|
             | RR-1            |
             +--------+-------+
                      |
           +----------+----------+
           |                     |
           |                     |
     +-----+------+        +-----+------+
     | EDGE-1     |        | EDGE-2     |
     | Client RR  |        | Client RR  |
     +------------+        +------------+
```

Le route reflector permet de réduire le nombre de sessions iBGP.

Mais il introduit aussi des considérations de conception :

- Choix du ou des route reflectors.
- Redondance.
- Répartition des clients.
- Prévention des boucles.
- Cluster ID.
- Politique de sélection des routes.
- Visibilité des chemins.
- Risques de concentration des dépendances.

## 10.3. Redondance des route reflectors

Une architecture critique doit éviter qu'un seul route reflector devienne un point de défaillance.

```text
                  +----------------+
                  | RR-1           |
                  +----------------+
                     /          \
                    /            \
                   /              \
           +------+-----+    +-----+------+
           | EDGE-1     |    | EDGE-2     |
           +------+-----+    +------+-----+
                   \              /
                    \            /
                     \          /
                  +----------------+
                  | RR-2           |
                  +----------------+
```

Chaque routeur client peut établir des sessions avec plusieurs route reflectors.

Cette redondance ne doit pas être considérée comme suffisante en elle-même. Les route reflectors doivent être répartis de manière à limiter les défaillances communes, et les politiques doivent être cohérentes entre eux.

## 10.4. Limites des route reflectors

Un route reflector ne distribue pas nécessairement tous les chemins possibles à tous ses clients.

La sélection des routes, les politiques d'importation, les politiques d'exportation et les mécanismes de réflexion peuvent créer des différences de visibilité.

Cela peut produire des comportements de routage non intuitifs, en particulier lorsque :

- Les chemins sont différents selon les routeurs.
- Les coûts IGP diffèrent.
- Les next-hops sont inaccessibles dans certaines parties du réseau.
- Les politiques locales diffèrent.
- Le route reflector n'a pas une vision adaptée à la topologie du plan de données.

Dans les réseaux opérateurs, il est nécessaire de vérifier la cohérence entre le plan de contrôle et le plan de données.

# 11. Peering public et Internet Exchange Points

## 11.1. Fonctionnement d'un IXP

Un IXP fournit une infrastructure permettant aux réseaux participants d'interconnecter leurs systèmes autonomes.

Les fonctions typiques comprennent :

- Une infrastructure de commutation Ethernet.
- Des ports physiques et logiques.
- Des VLAN ou services de transport associés.
- Des sessions BGP entre participants.
- Éventuellement des route servers.
- Des mécanismes de surveillance et de gestion de l'infrastructure.
- Des règles de participation et d'exploitation.

L'IXP ne garantit pas automatiquement qu'un participant dispose de routes vers tous les autres participants.

La visibilité des routes dépend des sessions établies, des politiques, des annonces et des règles de l'IXP.

## 11.2. Peering bilatéral

Dans le peering bilatéral, deux participants établissent directement une session BGP.

```text
       AS 64510                    AS 64540
     +-----------+                +-----------+
     | Routeur A |----------------| Routeur B |
     +-----------+      eBGP      +-----------+
                    VLAN de l'IXP
```

Avantages :

- Contrôle direct des politiques.
- Relation explicite entre les participants.
- Possibilité d'appliquer des règles particulières.
- Indépendance vis-à-vis d'un route server pour cette relation.

Inconvénients :

- Nombre de sessions à gérer.
- Besoin d'automatiser la configuration à grande échelle.
- Complexité accrue lors de l'ajout de nouveaux participants.
- Gestion des changements de politique.

## 11.3. Route server

Le route server reçoit des annonces de plusieurs participants et les distribue à d'autres participants selon les politiques de l'IXP.

```text
                   AS 64510
                       |
                       | BGP
                       |
              +--------+--------+
              |  Route Server   |
              |  IXP            |
              +---+----------+--+
                  |          |
                BGP          BGP
                  |          |
             +----+---+   +--+------+
             | AS 64540|   | AS 64550|
             | CDN     |   | ISP     |
             +---------+   +---------+

Le route server échange les routes.
Le trafic utilisateur passe généralement directement
entre les participants sur la fabric de l'IXP.
```

Le route server ne doit pas être confondu avec un routeur de transit qui transporte automatiquement le trafic entre les participants.

Dans le modèle habituel, le route server facilite le plan de contrôle. Le trafic de données emprunte le chemin direct entre les réseaux concernés.

Les détails exacts dépendent de l'architecture de l'IXP.

## 11.4. AS_PATH et route server

Un route server IXP peut utiliser des mécanismes particuliers de propagation des routes afin que le chemin AS_PATH reflète correctement les participants et que le serveur ne soit pas présenté comme un transit ordinaire.

Il est important de ne pas supposer que le comportement d'un route server est identique à celui d'un routeur eBGP de transit classique.

Il faut vérifier :

- La documentation de l'IXP.
- Les règles d'annonce.
- Les politiques d'importation et d'exportation.
- Les communautés de contrôle disponibles.
- La façon dont les chemins AS_PATH sont traités.
- Les filtres de préfixes.
- Les mécanismes de prévention des fuites.

## 11.5. Conditions de participation à un IXP

Avant d'activer le peering, vérifier :

1. L'accord de participation.
2. Les VLAN et les paramètres de port.
3. Les adresses IPv4 et IPv6 attribuées.
4. Le numéro d'AS.
5. Les adresses des pairs ou du route server.
6. Les règles de filtrage.
7. Les communautés documentées.
8. Les règles d'acceptation des routes.
9. Les limites de préfixes.
10. Les conditions de sécurité.
11. Les exigences de supervision.
12. Les modalités de maintenance.

# 12. Ingénierie de trafic BGP

## 12.1. Pourquoi l'ingénierie de trafic est-elle nécessaire ?

Un opérateur multihomé possède souvent plusieurs chemins possibles vers une destination.

Il peut vouloir :

- Préférer un fournisseur pour des raisons de coût.
- Utiliser un peer pour certaines destinations.
- Répartir le trafic sur plusieurs liens.
- Préserver la capacité de secours.
- Réduire la latence vers un réseau particulier.
- Éviter un transit saturé.
- Diriger le trafic entrant vers un point de présence spécifique.

Il faut distinguer deux problèmes :

- **Trafic sortant :** comment le réseau local atteint une destination externe.
- **Trafic entrant :** comment les réseaux externes atteignent les préfixes locaux.

Ces deux directions ne sont pas contrôlées de la même façon.

## 12.2. Contrôler le trafic sortant

LOCAL_PREF est un mécanisme central pour préférer un chemin de sortie.

Exemple :

```text
Préfixe externe : 198.51.100.0/24

Route reçue de Transit A :
LOCAL_PREF = 200

Route reçue de Transit B :
LOCAL_PREF = 150

Décision locale :
Transit A est préféré si les routes sont éligibles
et si aucun autre critère ou mécanisme ne modifie
la décision selon la configuration.
```

La valeur de LOCAL_PREF doit être cohérente dans l'AS et appliquée selon la politique définie.

Il faut également vérifier que les routeurs internes disposent d'une route utilisable vers le next-hop choisi.

## 12.3. Contrôler le trafic entrant

Le trafic entrant dépend des décisions prises par les réseaux distants.

Un opérateur peut influencer ces décisions par différents mécanismes :

- L'annonce ou la non-annonce de préfixes plus spécifiques.
- La longueur AS_PATH, lorsque les réseaux distants l'utilisent dans leur sélection.
- MED, dans les scénarios où il est comparé.
- Les communautés prises en charge par les fournisseurs.
- La sélection des relations de peering.
- Les annonces vers certains transitaires plutôt que d'autres.

Aucune de ces techniques ne garantit à elle seule le chemin choisi par tous les réseaux distants.

## 12.4. AS-path prepending

Le prepending consiste à répéter le numéro de l'AS local dans les annonces afin d'allonger artificiellement AS_PATH.

Exemple conceptuel :

```text
Annonce via Transit A :
AS_PATH : 64510

Annonce via Transit B :
AS_PATH : 64510 64510 64510

Politique possible :
certains réseaux distants préfèrent le chemin via Transit A.
```

Le prepending peut influencer certaines décisions, mais il ne doit pas être considéré comme un mécanisme de contrôle absolu.

Un réseau distant peut privilégier son LOCAL_PREF, ses relations commerciales ou une autre route indépendamment de la longueur du chemin.

Le prepending doit être utilisé avec mesure. Il peut également modifier les chemins de secours et la répartition du trafic de manière inattendue.

## 12.5. Annonces plus spécifiques

Une route plus spécifique est généralement préférée à une route moins spécifique pour la transmission IP, en raison de la règle du plus long préfixe correspondant.

Exemple :

```text
Route générale :
203.0.112.0/22

Route plus spécifique :
203.0.113.0/24

Pour une destination dans 203.0.113.0/24 :
la route /24 est généralement utilisée dans la FIB
si elle est présente et valide.
```

Cette propriété est parfois utilisée dans l'ingénierie de trafic entrant.

Mais elle augmente le nombre d'annonces et peut compliquer le routage.

Une annonce plus spécifique doit respecter les politiques de filtrage des réseaux distants, les limites de longueur de préfixe et les règles du fournisseur.

L'usage de préfixes trop spécifiques peut conduire à un rejet de l'annonce.

## 12.6. Communautés de fournisseur

De nombreux transitaires documentent des communautés permettant de demander certaines actions, par exemple :

- Abaisser la préférence locale chez le fournisseur.
- Influencer l'annonce vers certaines régions.
- Empêcher l'exportation vers certains peers.
- Demander des annonces limitées.
- Appliquer certaines politiques de maintenance.

Les communautés et leurs effets sont spécifiques au fournisseur.

Avant de les utiliser :

1. Lire la documentation du fournisseur.
2. Vérifier les communautés acceptées.
3. Vérifier les règles de sécurité.
4. Tester l'effet sur un préfixe de laboratoire.
5. Observer les annonces réellement propagées.
6. Documenter les limites et le retour arrière.

# 13. Sécurisation du routage BGP

## 13.1. Pourquoi BGP est-il exposé aux incidents ?

BGP repose sur l'échange d'informations entre réseaux indépendants.

Les incidents peuvent résulter de :

- Erreurs de configuration.
- Fuites de routes.
- Annonces de préfixes incorrects.
- Détournements de préfixes.
- Mauvaise gestion des communautés.
- Absence de filtrage.
- Erreurs d'agrégation.
- Perte de connectivité vers les next-hops.
- Compromission d'un routeur ou d'un compte d'administration.
- Problèmes de propagation dans le réseau.

Une session BGP peut être techniquement établie et pourtant transporter des annonces incorrectes.

La sécurité doit donc couvrir les sessions, les annonces, les politiques et la gestion opérationnelle.

## 13.2. Filtrage des préfixes

Un routeur doit limiter les annonces reçues aux préfixes autorisés.

Pour un client, la politique doit généralement être fondée sur les préfixes que ce client est autorisé à annoncer.

Pour un transitaire, le filtre est plus complexe : il peut être nécessaire d'accepter une table très large, tout en rejetant les préfixes spéciaux, les annonces non conformes et les routes qui violent la politique locale.

Les préfixes privés IPv4, les adresses de documentation et les plages spéciales doivent être traités selon leur contexte et les recommandations de filtrage applicables.

Les plages réservées ne doivent pas être annoncées publiquement comme des routes Internet ordinaires.

## 13.3. Max-prefix

Une limite de préfixes permet de détecter une augmentation anormale du nombre de routes reçues.

Elle peut protéger contre :

- Une erreur de configuration.
- Une fuite de routes.
- Une annonce accidentelle de table complète.
- Une hausse soudaine des annonces.

Exemple conceptuel :

```text
Voisin : Transit A

Nombre habituel de routes : 950 000
Limite configurée : à définir selon la politique
Comportement à la limite : alerte ou arrêt contrôlé

Objectif :
détecter une variation inattendue du volume de routes.
```

Les nombres ci-dessus sont illustratifs, pas des valeurs recommandées universelles.

Une limite trop basse peut interrompre une session légitime lors de l'évolution normale de la table Internet.

Une limite trop élevée peut perdre son intérêt.

La limite doit être calculée à partir du service réel, de la croissance attendue, des familles d'adresses, de l'implémentation et de la stratégie de récupération.

## 13.4. GTSM et protection de la session

Le **Generalized TTL Security Mechanism (GTSM)**, défini notamment par la RFC 5082, permet de limiter certains risques liés à des paquets BGP envoyés depuis des positions éloignées sur le réseau.

Le principe repose sur la vérification de la valeur TTL ou Hop Limit attendue.

Il est particulièrement pertinent pour certaines sessions directement connectées, sous réserve de compatibilité et de configuration des deux côtés.

GTSM ne remplace pas les autres mécanismes de sécurité.

Il ne prouve pas à lui seul l'identité de l'émetteur et ne protège pas contre toutes les menaces.

## 13.5. Authentification de session

Les mécanismes d'authentification ou de protection du transport doivent être évalués selon les fonctionnalités de la plateforme.

Des environnements prennent en charge l'authentification TCP MD5. TCP-AO constitue une alternative normalisée dans les environnements compatibles.

Il faut vérifier la prise en charge réelle des deux extrémités, les modalités de rotation des clés et la compatibilité de l'infrastructure.

Une clé configurée uniquement d'un côté ou différente entre les deux extrémités peut empêcher l'établissement de la session.

L'authentification du transport ne valide pas la légitimité des préfixes annoncés.

## 13.6. Protection du plan de contrôle

Les routeurs de bord doivent limiter l'accès aux services d'administration et aux sessions de routage.

Mesures possibles :

- ACL sur les interfaces et les adresses des pairs.
- Filtrage du port TCP 179 selon les besoins.
- Séparation des réseaux d'administration.
- Contrôle des accès SSH et API.
- Authentification forte des administrateurs.
- Journalisation des changements.
- Gestion des comptes privilégiés.
- Protection du processeur contre les paquets non autorisés.
- Supervision des ressources.
- Gestion sécurisée des secrets.
- Sauvegarde et validation des configurations.

Il ne faut pas appliquer une ACL qui bloque les flux nécessaires à la session ou à la gestion de l'infrastructure.

Toute modification de sécurité doit être testée et accompagnée d'un plan de retour arrière.

# 14. RPKI, ROA et validation d'origine

## 14.1. Le problème de l'origine des routes

Un réseau peut annoncer un préfixe qu'il ne devrait pas annoncer.

Exemple :

```text
Propriétaire légitime :
203.0.113.0/24

Origine AS autorisée :
AS 64510

Annonce observée :
203.0.113.0/24 avec origine AS 64599

Résultat :
l'annonce peut être considérée comme RPKI Invalid
si les ROA publiés ne l'autorisent pas.
```

Le mécanisme RPKI permet d'associer des autorisations cryptographiquement vérifiables à des préfixes et à des numéros d'AS.

## 14.2. ROA

Un **Route Origin Authorization (ROA)** associe notamment :

- Un préfixe.
- Un AS autorisé à l'annoncer.
- Éventuellement une longueur maximale de préfixe autorisée.

Exemple conceptuel :

```text
Préfixe : 203.0.113.0/24
AS autorisé : 64510
MaxLength : 24

Annonce :
203.0.113.0/24, origine AS 64510
Résultat attendu : Valid

Annonce :
203.0.113.0/24, origine AS 64599
Résultat attendu : Invalid

Annonce :
203.0.113.0/25, origine AS 64510
Résultat attendu : Invalid pour cette autorisation,
car /25 dépasse le MaxLength autorisé.
```

Le résultat exact dépend de l'ensemble des ROA applicables. Un autre ROA peut autoriser une annonce qui serait invalidée par le seul exemple présenté.

## 14.3. Les trois états de validation d'origine

### Valid

L'annonce correspond à au moins une autorisation valide : le préfixe est couvert et l'AS d'origine est autorisé, avec une longueur compatible.

### Invalid

Une autorisation couvre le préfixe, mais l'AS d'origine ou la longueur du préfixe ne correspond pas aux autorisations publiées.

### NotFound

Aucune autorisation applicable ne permet de déterminer que l'annonce est valide ou invalide.

NotFound ne signifie pas nécessairement que l'annonce est malveillante.

Il indique que les données disponibles ne permettent pas de valider l'origine au moyen de ces autorisations.

## 14.4. Validation d'origine et décisions locales

Un opérateur peut définir une politique telle que :

- Rejeter les routes Invalid.
- Accepter les routes Valid.
- Traiter les routes NotFound selon une politique de risque documentée.

Le rejet des routes Invalid peut réduire certains risques de détournement de préfixes.

Cependant, il faut surveiller les erreurs de ROA et les changements de délégation. Une autorisation incorrecte peut conduire au rejet de routes légitimes.

## 14.5. RPKI ne valide pas tout AS_PATH

La validation d'origine RPKI ne prouve pas que tous les AS présents dans AS_PATH ont réellement propagé la route comme annoncé.

Elle ne constitue pas à elle seule une protection complète contre :

- Toutes les fuites de routes.
- Toutes les attaques de chemin.
- Les annonces avec une origine autorisée mais un chemin anormal.
- Les erreurs de politique de propagation.
- Les erreurs d'exploitation.

Il faut combiner validation d'origine, filtrage de préfixes, politiques d'AS_PATH, contrôle des annonces et supervision.

## 14.6. Architecture d'un validateur RPKI

```text
              Dépôts et publications RPKI
                         |
                         v
                 +---------------+
                 | Synchronisation|
                 | et validation |
                 +-------+-------+
                         |
                         v
                 +---------------+
                 | Validateur     |
                 | RPKI           |
                 +-------+-------+
                         |
                     RTR protocol
                         |
                         v
                 +---------------+
                 | Routeur BGP   |
                 | EDGE-1        |
                 +-------+-------+
                         |
                         v
                 Politique BGP :
                 Valid / Invalid / NotFound
```

Le protocole RTR permet à un routeur de récupérer des données de validation auprès d'un cache compatible.

Le service doit être surveillé pour détecter les problèmes de synchronisation, l'expiration des données, les erreurs de configuration et les indisponibilités.

Un opérateur doit définir le comportement attendu lorsque le validateur ou la connexion RTR devient indisponible.

## 14.7. ROA : bonnes pratiques

Avant de publier un ROA :

1. Vérifier l'autorisation sur le préfixe.
2. Identifier les AS d'origine réellement utilisés.
3. Vérifier les longueurs de préfixe nécessaires.
4. Éviter de définir un MaxLength trop large sans justification.
5. Contrôler les scénarios de bascule entre fournisseurs.
6. Documenter les procédures de modification.
7. Vérifier les annonces après publication.
8. Surveiller les résultats de validation depuis plusieurs sources.

Une erreur de MaxLength peut rendre Invalid une annonce légitime plus spécifique.

Une erreur d'AS autorisé peut invalider les routes de secours.

# 15. Fuites de routes et détournements de préfixes

## 15.1. Route leak

Une fuite de routes se produit lorsqu'un réseau propage des routes au-delà de la portée prévue par ses politiques.

Exemple :

```text
                  Transit A
                      |
                      |
                   AS 64510
                   Opérateur
                      |
                      |
                   AS 64540
                   Client

Le client annonce ses propres préfixes à l'opérateur.

Erreur :
l'opérateur réannonce à Transit A des routes
apprises d'un autre fournisseur, sans autorisation.

Conséquence possible :
une partie du trafic est attirée vers un chemin non prévu.
```

Les conséquences peuvent comprendre :

- Des chemins sous-optimaux.
- Une surcharge d'un réseau.
- Une perte de connectivité.
- Une asymétrie importante.
- Une violation contractuelle.
- Une interruption à grande échelle.

## 15.2. Prefix hijack

Un détournement de préfixe se produit lorsqu'un réseau annonce un préfixe qu'il n'est pas autorisé à annoncer, avec pour effet potentiel d'attirer le trafic.

Un détournement peut être accidentel ou malveillant.

Les conséquences dépendent notamment :

- De la longueur du préfixe annoncé.
- Des politiques de filtrage des réseaux distants.
- De la validation RPKI.
- De l'AS_PATH.
- Des préférences locales.
- Des politiques de propagation.
- De la visibilité de l'annonce.

## 15.3. Pourquoi les annonces plus spécifiques sont dangereuses

Le transfert IP privilégie normalement la route correspondant au préfixe le plus long.

Une annonce plus spécifique peut donc attirer le trafic même si une route moins spécifique est également présente.

Les filtres d'annonces et les politiques de validation sont indispensables.

Il ne faut pas considérer la longueur du chemin AS_PATH comme une protection contre les annonces plus spécifiques.

## 15.4. Mesures de prévention

- Définir une liste de préfixes autorisés par voisin.
- Contrôler les longueurs de préfixe.
- Rejeter les annonces de plages non autorisées.
- Appliquer la validation d'origine RPKI.
- Utiliser des politiques de propagation explicites.
- Définir des limites de préfixes.
- Contrôler les AS_PATH lorsque cela est pertinent.
- Documenter les relations client, peer et transit.
- Surveiller les annonces inhabituelles.
- Tester les politiques lors des changements.
- Conserver des preuves de configuration et de routage.

# 16. BGP Graceful Restart, BFD et convergence

## 16.1. Convergence BGP

La convergence est le processus par lequel le routage atteint un état cohérent après un changement de topologie ou de politique.

Les causes de changement comprennent :

- La perte d'un lien.
- La panne d'un routeur.
- La fermeture d'une session.
- Le retrait d'un préfixe.
- Une modification de politique.
- Une variation de joignabilité du next-hop.
- Une défaillance de transport.

La convergence dépend de plusieurs mécanismes. Il ne faut pas la réduire aux seuls timers BGP.

## 16.2. Timers BGP

Les paramètres de maintien de session incluent notamment les intervalles de KEEPALIVE et le Hold Time.

Les valeurs négociées et le comportement dépendent des paramètres des deux pairs et de l'implémentation.

Réduire les timers peut accélérer la détection de certaines défaillances, mais peut aussi augmenter la sensibilité aux congestions et aux retards.

Un réglage agressif doit être justifié par des mesures et une validation de la plateforme.

## 16.3. BFD

Bidirectional Forwarding Detection permet de détecter rapidement certaines défaillances de chemin entre deux systèmes.

BFD peut être associé à BGP lorsque les plateformes et les topologies le prennent en charge.

```text
        Routeur A                    Routeur B
     +-------------+              +-------------+
     | BGP         |              | BGP         |
     |             |              |             |
     | BFD client  |<------------>| BFD client  |
     +------+------+    BFD       +------+------+
            |                            |
            +------------ Lien ----------+

Si BFD détecte une défaillance :
le routeur peut informer rapidement le processus
de routage associé selon l'intégration configurée.
```

BFD n'est pas automatiquement adapté à tous les environnements.

Des intervalles trop agressifs peuvent produire des faux positifs sur des équipements surchargés ou sur des chemins de transport présentant des variations de délai.

## 16.4. Graceful Restart

Graceful Restart peut permettre de préserver temporairement certaines informations de routage lors du redémarrage d'un processus ou d'un équipement compatible.

Son intérêt dépend de l'architecture, des capacités négociées et du comportement du plan de données.

Il ne doit pas être activé sans analyse des risques.

Si le plan de données a réellement perdu la capacité de transférer le trafic, conserver des routes anciennes peut prolonger une panne ou créer un trou noir.

## 16.5. Graceful Shutdown

Graceful Shutdown, décrit notamment par la RFC 8326, vise à faciliter la migration contrôlée du trafic avant la maintenance ou la fermeture d'une session BGP.

Le principe consiste à communiquer une préférence adaptée, souvent via la communauté bien connue prévue à cet effet, pour permettre au voisin de déplacer progressivement le trafic avant l'arrêt.

Le comportement exact dépend du support et de la politique du pair.

La procédure doit être coordonnée entre les réseaux lorsque cela est possible.

# 17. IPv6 et BGP multiprotocole

## 17.1. MP-BGP

Multiprotocol BGP étend BGP pour prendre en charge différentes familles d'adresses et de routes.

Cela permet notamment de transporter :

- IPv4 unicast.
- IPv6 unicast.
- Certaines familles VPN.
- D'autres familles définies par les extensions BGP.

Les capacités doivent être prises en charge et négociées entre les pairs concernés.

## 17.2. Particularités IPv6

Le routage IPv6 exige de vérifier :

- Les adresses de voisinage.
- La joignabilité des next-hops.
- Les filtres IPv6.
- Les préfixes annoncés.
- Les routes link-local lorsqu'elles sont utilisées.
- La cohérence entre interfaces et sessions.
- Les politiques d'exportation.
- Les règles de sécurité propres à IPv6.

Une session IPv4 opérationnelle ne prouve pas que la session IPv6 est configurée correctement.

## 17.3. Filtrage des préfixes IPv6

Les filtres IPv6 doivent être construits séparément des filtres IPv4.

Ils doivent prendre en compte :

- Les préfixes autorisés.
- Les longueurs acceptables.
- Les adresses spéciales.
- Les routes internes.
- Les annonces plus spécifiques.
- Les politiques de chaque voisin.

Il n'existe pas une longueur unique qui convienne à toutes les annonces IPv6. Les politiques doivent refléter les allocations réelles et les pratiques de routage du réseau.

# 18. Surveillance et observabilité BGP

## 18.1. Pourquoi superviser BGP ?

La supervision ne doit pas se limiter à vérifier que les sessions sont en Established.

Une session peut rester établie alors que :

- Les routes attendues ont disparu.
- Le next-hop n'est plus joignable.
- Une route par défaut a été retirée.
- Un filtre bloque des préfixes légitimes.
- Le nombre de routes a fortement augmenté.
- Le trafic passe par un mauvais transitaire.
- Un préfixe est devenu RPKI Invalid.
- Le plan de données ne correspond plus au plan de contrôle.

## 18.2. Indicateurs à surveiller

| Indicateur | Utilité |
|---|---|
| État des sessions | Détection des coupures |
| Durée depuis le dernier changement d'état | Identification des instabilités |
| Nombre de préfixes reçus | Détection des variations de volume |
| Nombre de préfixes annoncés | Contrôle des politiques d'exportation |
| Routes rejetées | Détection des problèmes de filtrage |
| État du validateur RPKI | Contrôle de la disponibilité des données |
| État BFD | Détection rapide des défaillances compatibles |
| Utilisation CPU et mémoire | Détection des saturations |
| État des interfaces | Corrélation avec les pannes de transport |
| Débit par fournisseur | Suivi de l'ingénierie de trafic |
| Latence et pertes | Évaluation de la qualité du chemin |
| Changements AS_PATH | Détection de certaines anomalies |
| Préfixes Invalid | Suivi de la sécurité d'origine |

## 18.3. Collecte de données de routage

Les opérateurs peuvent utiliser différents mécanismes selon leur architecture :

- Journaux des routeurs.
- SNMP lorsque cela est pris en charge.
- Télémétrie.
- Streaming telemetry.
- BMP (BGP Monitoring Protocol).
- Collecteurs de routes.
- Sondes de connectivité.
- Systèmes de supervision de l'infrastructure.
- Outils d'analyse de tables BGP.

BMP est normalisé notamment par la RFC 7854 et ses extensions. Il permet de transmettre des informations BGP vers des systèmes de collecte, selon les capacités et la configuration de la plateforme.

Les données de supervision doivent être protégées : elles peuvent révéler des détails sensibles sur la topologie, les relations de peering et les politiques de routage.

# 19. Diagnostic expert d'une session BGP

## 19.1. Méthode générale

Lorsqu'une session BGP ne fonctionne pas, le diagnostic doit suivre une progression logique.

```text
1. Vérifier l'état de l'interface.
             |
             v
2. Vérifier l'adressage IP et le routage vers le pair.
             |
             v
3. Vérifier TCP/179 et les ACL.
             |
             v
4. Vérifier AS locaux et distants.
             |
             v
5. Vérifier les paramètres d'authentification.
             |
             v
6. Vérifier OPEN, capacités et erreurs BGP.
             |
             v
7. Vérifier les politiques d'importation.
             |
             v
8. Vérifier les routes BGP reçues et retenues.
             |
             v
9. Vérifier la RIB, le next-hop et la FIB.
             |
             v
10. Vérifier le chemin de données réel.
```

Cette méthode évite de modifier arbitrairement plusieurs paramètres à la fois.

## 19.2. Cas 1 — Session bloquée en Active

Causes possibles :

- Adresse du voisin incorrecte.
- Mauvais adressage IP.
- Route vers le voisin absente.
- Filtrage TCP/179.
- Mauvaise interface.
- Problème de connectivité de niveau 2.
- Authentification incompatible.
- Session configurée sur la mauvaise adresse source.
- Mauvaise configuration de l'eBGP multihop dans les cas où il est nécessaire.

Commandes Linux :

```bash
ip addr show
ip route show
ping -c 4 192.0.2.2
ip neigh show
```

Le ping peut être bloqué même lorsque la session BGP fonctionne. Il est donc utile mais ne suffit pas à conclure.

Pour inspecter TCP :

```bash
sudo ss -tnp
```

La capture de paquets peut aider à confirmer l'établissement TCP et l'échange BGP :

```bash
sudo tcpdump -ni any 'tcp port 179'
```

Les captures doivent être réalisées dans le respect des règles de sécurité et de confidentialité du réseau.

## 19.3. Cas 2 — Session Established mais zéro route reçue

Causes possibles :

- Le voisin n'annonce aucun préfixe.
- La famille d'adresses n'est pas activée.
- Une politique d'importation rejette les routes.
- Le fournisseur n'a pas encore autorisé le client.
- La configuration du pair est incomplète.
- Les routes sont annoncées dans une autre famille d'adresses.
- Un mécanisme de filtrage bloque les UPDATE.
- Une route attendue est absente du réseau distant.

Vérifier :

```text
show bgp summary
show bgp ipv4 unicast neighbors 192.0.2.2
show bgp ipv4 unicast
show running-config
```

Ne pas supprimer tous les filtres pour tester. Il vaut mieux isoler la politique concernée et vérifier les routes reçues, rejetées ou annoncées.

## 19.4. Cas 3 — Routes reçues mais non installées

Causes possibles :

- Next-hop inaccessible.
- Route non éligible.
- Politique de sélection.
- Route préférée issue d'une autre source.
- Filtre de routage local.
- Problème d'installation dans la RIB ou la FIB.
- Limite de ressources ou comportement spécifique de plateforme.

Vérifier la route BGP et la route IP :

```text
show bgp ipv4 unicast 203.0.113.0/24
show ip route 203.0.113.0/24
```

Ces commandes illustrent les vérifications à effectuer. Leur syntaxe exacte dépend de la plateforme.

## 19.5. Cas 4 — Routes installées mais trafic en échec

La session BGP peut être correcte, et la route peut être présente, alors que les paquets sont perdus.

Causes possibles :

- Mauvaise route de retour.
- ACL.
- Filtrage du plan de données.
- Problème de MTU.
- Problème de transport.
- Next-hop mal résolu.
- Interface de sortie inactive.
- Routage asymétrique.
- Problème de NAT ou de politique de sécurité.
- Agrégation qui couvre des adresses non joignables.

La procédure de diagnostic doit suivre le chemin des paquets et vérifier les deux directions.

## 19.6. Cas 5 — Préfixe visible chez un pair mais absent chez un autre

Vérifier :

- La politique d'exportation.
- La relation commerciale entre les deux voisins.
- La présence du préfixe dans la table retenue.
- Les communautés appliquées.
- Les filtres du pair distant.
- La longueur du préfixe.
- Les politiques de l'IXP ou du transitaire.
- L'origine RPKI.
- Les règles d'AS_PATH.
- Les annonces effectivement propagées.

Le fait qu'un préfixe soit visible dans une table locale ne prouve pas qu'il a été exporté, accepté par le pair suivant et propagé jusqu'à la destination.

# 20. Laboratoire 1 — Établir une session eBGP

## 20.1. Objectif

Créer deux AS reliés par une session eBGP, puis vérifier l'échange d'un préfixe.

Topologie :

```text
      AS 64510                            AS 64520

  +--------------+                  +--------------+
  | Router A     |                  | Router B     |
  |              |                  |              |
  | 192.0.2.1/30 |------------------| 192.0.2.2/30 |
  +--------------+       eBGP       +--------------+
```

## 20.2. Configuration conceptuelle

Routeur A :

```text
router bgp 64510
 bgp router-id 198.51.100.1
 neighbor 192.0.2.2 remote-as 64520
 address-family ipv4 unicast
  neighbor 192.0.2.2 activate
 exit-address-family
```

Routeur B :

```text
router bgp 64520
 bgp router-id 198.51.100.2
 neighbor 192.0.2.1 remote-as 64510
 address-family ipv4 unicast
  neighbor 192.0.2.1 activate
 exit-address-family
```

Cette configuration suppose que les interfaces sont déjà adressées et que la connectivité IP fonctionne.

Elle n'est pas une configuration complète de production : elle ne contient pas de politique d'importation et d'exportation, de validation d'origine ni de protections avancées.

## 20.3. Vérifications

Sur les deux routeurs :

```text
show bgp summary
```

Résultat attendu : la session doit passer à Established.

Ensuite, vérifier les routes reçues et annoncées :

```text
show bgp ipv4 unicast
show bgp ipv4 unicast neighbors 192.0.2.2
```

Adapter l'adresse du voisin au routeur sur lequel la commande est exécutée.

## 20.4. Exercices

1. Que signifie une session en Active ?
2. Pourquoi une session Established peut-elle recevoir zéro route ?
3. Pourquoi le ping ne prouve-t-il pas à lui seul que BGP fonctionne ?
4. Quelle différence existe entre une route reçue et une route installée ?
5. Pourquoi faut-il ajouter des filtres avant de connecter un routeur de laboratoire à un réseau réel ?

### Correction

1. Active indique que l'établissement de la session n'a pas encore abouti ; le routeur continue ses tentatives ou attend une condition permettant de progresser.
2. Le pair peut n'annoncer aucun préfixe, une famille peut être inactive ou une politique peut rejeter les routes.
3. Le ping teste la connectivité ICMP, pas l'ensemble du fonctionnement BGP.
4. Une route reçue est une annonce BGP ; elle peut être rejetée, non sélectionnée ou non installée.
5. Pour limiter les annonces incorrectes, les fuites de routes et l'exposition involontaire du réseau.

# 21. Laboratoire 2 — Préférer un transitaire avec LOCAL_PREF

## 21.1. Objectif

Créer deux chemins vers un même préfixe et contrôler la préférence locale.

```text
                   Transit A
                   AS 64520
                       |
                      eBGP
                       |
                +------+------+
                | EDGE-1      |
                | AS 64510    |
                +------+------+
                       |
                    iBGP / Core
                       |
                +------+------+
                | EDGE-2      |
                | AS 64510    |
                +------+------+
                       |
                      eBGP
                       |
                   Transit B
                   AS 64530
```

Supposons que les deux transitaires annoncent `203.0.113.0/24` dans l'environnement de laboratoire.

Le routeur doit attribuer une préférence plus élevée au chemin via Transit A.

## 21.2. Politique conceptuelle

```text
Routes apprises de Transit A :
LOCAL_PREF = 200

Routes apprises de Transit B :
LOCAL_PREF = 150
```

La route via Transit A doit être préférée si les routes sont éligibles et si aucun autre critère ou mécanisme ne modifie la décision.

Dans FRR, une route-map peut appliquer une préférence locale :

```text
route-map TRANSIT-A-IN permit 10
 set local-preference 200
!
route-map TRANSIT-B-IN permit 10
 set local-preference 150
```

Ces route-maps sont des fragments illustratifs. Elles doivent être intégrées à des politiques d'importation qui filtrent également les routes autorisées.

## 21.3. Vérification

```text
show bgp ipv4 unicast 203.0.113.0/24
```

Vérifier :

- Les chemins disponibles.
- Le LOCAL_PREF.
- Le next-hop.
- La route sélectionnée.
- La route installée dans la table IP.

## 21.4. Exercices

1. Pourquoi LOCAL_PREF est-il adapté au contrôle du trafic sortant ?
2. Pourquoi AS_PATH n'est-il pas le seul critère de sélection ?
3. Pourquoi faut-il vérifier la joignabilité du next-hop ?
4. LOCAL_PREF peut-il imposer la décision de tous les réseaux Internet distants ?

### Correction

1. Il permet à l'AS local d'exprimer une préférence entre chemins appris de différents voisins.
2. D'autres attributs et politiques peuvent être prioritaires.
3. Un chemin sélectionné mais inutilisable au niveau IP ne permet pas d'acheminer correctement les paquets.
4. Non. LOCAL_PREF est une préférence locale, normalement propagée à l'intérieur de l'AS et non imposée aux réseaux externes.

# 22. Laboratoire 3 — Filtrer les annonces d'un client

## 22.1. Objectif

Autoriser un client à annoncer uniquement les préfixes prévus.

Supposons :

```text
AS opérateur : 64510
AS client    : 64540

Préfixe autorisé :
203.0.113.0/24

Préfixes non autorisés :
198.51.100.0/24
192.0.2.0/24
```

Les trois plages sont réservées à la documentation. Le laboratoire ne doit pas être raccordé à un réseau public avec ces annonces.

## 22.2. Politique FRR illustrative

```text
ip prefix-list CLIENT-64540-IN seq 10 permit 203.0.113.0/24
!
route-map CLIENT-64540-IN permit 10
 match ip address prefix-list CLIENT-64540-IN
!
route-map CLIENT-64540-IN deny 100
!
router bgp 64510
 neighbor 192.0.2.6 remote-as 64540
 neighbor 192.0.2.6 route-map CLIENT-64540-IN in
```

L'adresse `192.0.2.6` est un exemple et doit être remplacée par l'adresse réelle du voisin dans un environnement de test.

## 22.3. Vérifications

1. Vérifier que le préfixe autorisé est accepté.
2. Vérifier qu'un préfixe non autorisé est rejeté.
3. Vérifier que le client n'annonce pas de route par défaut sans autorisation.
4. Vérifier que l'AS_PATH est cohérent avec la relation.
5. Vérifier les routes effectivement exportées vers les autres voisins.

## 22.4. Point d'attention

Le filtrage par préfixe ne suffit pas à lui seul à garantir l'ensemble de la politique.

Il faut aussi considérer :

- Les AS_PATH.
- Les communautés.
- Les longueurs de préfixe.
- Les familles IPv4 et IPv6.
- Les routes par défaut.
- La validation d'origine.
- Les politiques d'exportation.

# 23. Laboratoire 4 — Valider les routes avec RPKI

## 23.1. Objectif

Comprendre le rôle de RPKI et des ROA dans une politique BGP.

### Scénario

Une organisation possède un préfixe et autorise un AS à l'annoncer.

```text
Préfixe : 203.0.113.0/24
AS autorisé : 64510
MaxLength : 24
```

Trois annonces sont observées :

| Préfixe | AS d'origine | Résultat attendu avec ce seul ROA |
|---|---:|---|
| 203.0.113.0/24 | 64510 | Valid |
| 203.0.113.0/24 | 64599 | Invalid |
| 203.0.113.0/25 | 64510 | Invalid |

Le résultat dépend de tous les ROA applicables, et pas seulement de celui présenté dans cet exemple.

## 23.2. Travail demandé

1. Expliquer la différence entre Valid, Invalid et NotFound.
2. Expliquer pourquoi Invalid ne doit pas être confondu avec NotFound.
3. Décrire les conséquences d'un MaxLength incorrect.
4. Expliquer pourquoi RPKI ne valide pas tout AS_PATH.
5. Proposer une politique de traitement des routes invalides.
6. Décrire les contrôles à réaliser après une modification de ROA.

### Correction

- Valid signifie qu'une autorisation couvre le préfixe et valide l'AS d'origine ainsi que la longueur.
- Invalid signifie qu'une autorisation applicable existe, mais que l'annonce ne satisfait pas les critères d'origine ou de longueur.
- NotFound signifie qu'aucune autorisation applicable ne permet de valider l'origine.
- Un MaxLength trop restrictif peut invalider une annonce légitime plus spécifique.
- RPKI origin validation porte sur l'origine de la route et ne certifie pas chaque AS du chemin.
- Une politique robuste rejette généralement Invalid selon les règles opérationnelles définies, tout en surveillant la disponibilité des données et les erreurs d'autorisation.

# 24. Projet final — Concevoir un opérateur multihomé sécurisé

## 24.1. Contexte

Vous êtes responsable réseau d'un opérateur régional.

L'opérateur possède :

- Un AS public réel qui doit être remplacé par un numéro de laboratoire dans cet exercice.
- Deux routeurs de bord.
- Deux fournisseurs de transit.
- Une connexion à un IXP.
- Un réseau interne avec iBGP.
- Des clients professionnels.
- Des services IPv4 et IPv6.
- Des objectifs de disponibilité élevés.
- Des exigences de filtrage et de traçabilité.

Le réseau doit rester joignable lorsqu'un transitaire devient indisponible, sans provoquer de fuite de routes.

## 24.2. Architecture cible

```text
                         INTERNET

              +------------------------+
              |      TRANSIT A         |
              |       AS 64520         |
              +-----------+------------+
                          |
                         eBGP
                          |
                  +-------+-------+
                  |    EDGE-1     |
                  |    AS 64510   |
                  +-------+-------+
                          |
                     Réseau IP
                          |
                  +-------+-------+
                  |    CORE-1     |
                  |    AS 64510   |
                  +-------+-------+
                          |
                     Réseau IP
                          |
                  +-------+-------+
                  |    EDGE-2     |
                  |    AS 64510   |
                  +-------+-------+
                          |
                         eBGP
                          |
              +-----------+------------+
              |      TRANSIT B         |
              |       AS 64530         |
              +------------------------+

                         |
                         | eBGP
                         |
                  +------+------+
                  | IXP / RS    |
                  +------+------+
                         |
                 Réseaux de contenu
```

La topologie est logique. Le projet réel doit documenter la diversité physique et les domaines de panne.

## 24.3. Travail demandé

### Partie A — Architecture

1. Définir les AS.
2. Définir les sessions eBGP.
3. Définir les sessions iBGP.
4. Définir les route reflectors si nécessaire.
5. Définir les interfaces et adresses de peering.
6. Définir la politique de routage interne.
7. Définir les exigences de redondance physique.
8. Définir les scénarios de panne.

### Partie B — Politique d'importation

Créer une politique pour chaque catégorie de voisin :

- Transit A.
- Transit B.
- Route server IXP.
- Client professionnel.

La politique doit spécifier :

- Les préfixes acceptés.
- Les longueurs de préfixe.
- Les routes privées et spéciales.
- Le traitement RPKI.
- Les communautés.
- Les AS_PATH.
- La limite de préfixes.
- La préférence locale.
- Les conditions de rejet.

### Partie C — Politique d'exportation

Définir précisément :

- Les routes exportées vers Transit A.
- Les routes exportées vers Transit B.
- Les routes exportées vers l'IXP.
- Les routes exportées aux clients.
- Les routes internes qui ne doivent jamais être propagées.
- Le traitement des routes par défaut.
- Les préfixes qui ne doivent pas être annoncés plus spécifiquement.

### Partie D — Résilience

Définir :

- Le comportement à la perte de Transit A.
- Le comportement à la perte de Transit B.
- Le comportement à la perte de l'IXP.
- Le comportement à la perte d'EDGE-1.
- Le comportement à la perte d'EDGE-2.
- Le comportement à la perte d'un route reflector.
- Le comportement à l'indisponibilité du validateur RPKI.
- Les procédures de maintenance.

### Partie E — Sécurité

Définir :

- Les filtres de préfixes.
- Les contrôles AS_PATH.
- La validation RPKI.
- La protection des sessions.
- Les ACL.
- Les limites de préfixes.
- La gestion des communautés.
- La supervision des annonces.
- Les procédures de changement.
- Les mécanismes de retour arrière.

### Partie F — Supervision

Définir les indicateurs, les seuils et les alertes :

- État des sessions.
- Préfixes reçus et annoncés.
- Variation du nombre de routes.
- Routes Invalid.
- Erreurs de session.
- Disponibilité des liens.
- Saturation des interfaces.
- Changements de chemin.
- Latence.
- Pertes de paquets.
- Indisponibilité des services.

# 25. Correction du projet final

## 25.1. Architecture recommandée

La conception doit séparer clairement le routage interne du routage externe.

L'IGP assure la joignabilité des infrastructures nécessaires, notamment les loopbacks et les next-hops internes.

iBGP distribue les routes interdomaines dans l'AS. Les sessions eBGP relient les routeurs de bord aux transitaires, au client et au service de peering IXP.

Les route reflectors peuvent réduire le nombre de sessions internes lorsque le réseau devient suffisamment grand.

Deux route reflectors peuvent être déployés dans des domaines de panne distincts, avec des politiques cohérentes.

## 25.2. Politique d'importation recommandée

### Transit A et Transit B

La politique doit accepter les routes prévues par le contrat, tout en rejetant les annonces spéciales, les préfixes interdits et les annonces qui ne respectent pas les critères de sécurité.

La validation RPKI doit être appliquée selon une politique documentée.

Les routes reçues doivent être marquées par des communautés internes si cela simplifie la politique et facilite la supervision.

La préférence locale doit exprimer la stratégie de sortie du réseau.

### IXP

La politique doit respecter les règles de l'IXP.

Elle doit empêcher l'acceptation de routes inattendues et l'exportation involontaire de routes de transit vers les autres participants.

Les communautés IXP ne doivent être utilisées que selon la documentation du service.

### Clients

Les clients doivent disposer de filtres d'entrée stricts basés sur leurs préfixes autorisés.

Leur politique d'exportation doit être explicitement définie en fonction du contrat.

Les routes par défaut ne doivent être envoyées que lorsque cela correspond au service convenu.

## 25.3. Politique d'exportation recommandée

La politique d'exportation doit être restrictive par défaut.

Pour chaque voisin, seules les routes autorisées doivent être annoncées.

Les routes propres de l'opérateur doivent être contrôlées par une liste de préfixes autorisés.

Les routes client doivent être annoncées selon les règles commerciales et techniques convenues.

Les routes apprises d'un transitaire ne doivent pas être propagées à un autre transitaire ou à un peer sans autorisation explicite.

Les annonces IPv4 et IPv6 doivent être traitées séparément, avec des filtres adaptés à chaque famille.

## 25.4. Politique de préférence

La politique doit être déterminée à partir des objectifs réels :

- Coût.
- Latence.
- Capacité.
- Disponibilité.
- Qualité de service.
- Politique de peering.
- Contraintes contractuelles.

Il n'existe pas de règle universelle imposant que le transit A soit toujours préféré au transit B.

Une préférence fixe peut convenir à un laboratoire, mais une production exige une politique fondée sur les besoins et la capacité des chemins.

## 25.5. Scénarios de panne

### Perte de Transit A

Le réseau doit retirer ou rendre inutilisables les routes dépendantes de Transit A, puis utiliser les chemins valides disponibles via Transit B ou l'IXP.

Il faut vérifier que le trafic de retour dispose également d'un chemin utilisable.

### Perte de Transit B

Le même principe s'applique dans l'autre sens.

### Perte de l'IXP

Les routes apprises uniquement via l'IXP doivent être retirées ou devenir inutilisables. Le transit peut fournir un chemin de secours si les politiques et les annonces le permettent.

### Perte d'EDGE-1

Les routes doivent rester disponibles via EDGE-2 lorsque les préfixes, les sessions et l'architecture permettent cette continuité.

Il faut aussi vérifier les chemins physiques et les dépendances communes.

### Perte d'un route reflector

Le second route reflector doit continuer à fournir les routes aux clients concernés, sous réserve d'une configuration correcte et d'une topologie réellement redondante.

### Indisponibilité du validateur RPKI

Le comportement doit être explicitement défini.

Il faut éviter une modification incontrôlée des politiques au cours d'un incident de validateur.

La disponibilité du cache, la fraîcheur des données et le comportement du routeur doivent être supervisés.

## 25.6. Critères d'acceptation

Le projet est accepté lorsque les tests suivants sont réussis :

1. Toutes les sessions prévues atteignent l'état attendu.
2. Les préfixes autorisés sont reçus et annoncés correctement.
3. Les préfixes non autorisés sont rejetés.
4. Les politiques IPv4 et IPv6 sont testées séparément.
5. Les routes Invalid sont traitées conformément à la politique RPKI.
6. Une perte de transit provoque une convergence acceptable.
7. Une perte d'IXP ne provoque pas une fuite de routes.
8. Les route reflectors sont testés en cas de panne.
9. Les annonces sortantes sont vérifiées auprès de chaque voisin.
10. Le plan de données correspond aux routes attendues.
11. Les alertes de supervision fonctionnent.
12. Les procédures de changement et de retour arrière sont documentées.
13. Aucun préfixe de laboratoire réservé à la documentation n'est annoncé sur Internet.

# 26. Exercices avancés corrigés

## Exercice 1 — Sélection de route

Un routeur reçoit trois chemins vers le même préfixe :

| Route | LOCAL_PREF | AS_PATH |
|---|---:|---|
| A | 100 | 64520 64530 |
| B | 200 | 64540 64550 64560 |
| C | 150 | 64570 |

Quelle route doit être préférée selon une politique standard où les chemins sont éligibles et où LOCAL_PREF est le premier critère pertinent de sélection ?

**Correction :** la route B, car son LOCAL_PREF est le plus élevé. La longueur AS_PATH ne suffit pas à rendre la route C ou A préférable.

## Exercice 2 — Session BGP établie, route absente

Une session est en Established, mais le préfixe attendu n'apparaît pas dans la table BGP.

Citez au moins cinq causes possibles.

**Correction :**

- Le pair n'annonce pas le préfixe.
- La famille d'adresses n'est pas activée.
- Une politique d'importation rejette la route.
- Le préfixe est absent de la table du voisin.
- Une limite de préfixes a été atteinte.
- Le voisin utilise une politique d'annonce différente.
- Une erreur de configuration empêche la propagation.
- La route est reçue mais non visible dans la table consultée en raison de la famille ou de la commande utilisée.

## Exercice 3 — Peering et transit

Un opérateur dispose d'un peering avec un CDN et d'un contrat de transit avec un fournisseur.

Le peering CDN tombe. Le transit peut-il automatiquement fournir l'accès au CDN ?

**Correction :** cela dépend des annonces, des politiques et de la joignabilité. Si le fournisseur de transit offre un chemin vers les préfixes du CDN et que les routes correspondantes sont acceptées, un chemin de secours peut exister. Ce n'est pas garanti par la seule existence du contrat de transit.

## Exercice 4 — RPKI Invalid

Une route est Invalid parce que son AS d'origine n'est pas autorisé par les ROA applicables.

Faut-il automatiquement considérer que l'annonce est malveillante ?

**Correction :** non. L'annonce peut résulter d'une erreur de configuration ou d'un ROA incorrect. Cependant, Invalid est un signal de validation important qui doit être traité selon une politique de sécurité définie et faire l'objet d'une investigation.

## Exercice 5 — AS-path prepending

Un opérateur triple son AS_PATH sur Transit B, mais une partie du trafic entrant continue à passer par ce fournisseur.

Pourquoi ?

**Correction :** les réseaux distants peuvent privilégier LOCAL_PREF, leurs relations commerciales, leurs communautés ou d'autres critères avant la longueur AS_PATH. Le prepending influence le chemin sans imposer une décision universelle.

## Exercice 6 — Fuite de routes

Un client annonce une route par défaut à son fournisseur, alors que le contrat ne l'autorise pas.

Quelle protection faut-il appliquer ?

**Correction :** le fournisseur doit appliquer une politique d'importation explicite qui rejette la route par défaut si elle n'est pas autorisée. Une surveillance du volume et des types de routes est également utile, mais ne remplace pas le filtrage.

## Exercice 7 — Next-hop inaccessible

Une route BGP est reçue, mais son next-hop n'est pas joignable.

Quel est le problème ?

**Correction :** la route peut être considérée comme inutilisable ou ne pas être installée, selon la plateforme et le contexte. Il faut rétablir la joignabilité du next-hop ou corriger la conception de l'annonce et de la distribution des routes.

## Exercice 8 — Route reflector unique

Un réseau utilise un seul route reflector. Celui-ci tombe en panne.

Quels sont les risques ?

**Correction :** les sessions de réflexion peuvent disparaître, la visibilité des routes peut être réduite et la convergence peut être affectée. Une redondance de route reflectors, associée à une conception cohérente, limite ce risque.

## Exercice 9 — Route plus spécifique

Un réseau annonce `203.0.112.0/22`. Un autre AS annonce `203.0.113.0/24`.

Quel préfixe sera utilisé pour une destination comprise dans `203.0.113.0/24` si les deux routes sont présentes et valides dans la FIB ?

**Correction :** le `/24`, car la transmission IP utilise le plus long préfixe correspondant. Cela explique pourquoi les annonces plus spécifiques doivent être filtrées et surveillées.

## Exercice 10 — Max-prefix

Une limite de préfixes provoque la fermeture d'une session lors d'une croissance normale du nombre de routes.

Comment corriger le problème sans supprimer la protection ?

**Correction :** analyser la croissance réelle, déterminer la marge nécessaire, revoir la limite et le seuil d'alerte, puis tester le comportement de récupération. Il faut conserver une limite adaptée et surveiller les variations.

# 27. Glossaire expert

| Terme | Définition |
|---|---|
| AS | Système autonome administré selon une politique de routage commune |
| ASN | Numéro identifiant un système autonome |
| BGP | Protocole de routage interdomaines |
| eBGP | BGP entre AS différents |
| iBGP | BGP à l'intérieur d'un AS |
| AS_PATH | Attribut décrivant la propagation inter-AS |
| LOCAL_PREF | Attribut de préférence locale |
| MED | Attribut de préférence relative d'entrée |
| NEXT_HOP | Prochain saut associé à une route |
| ORIGIN | Attribut historique de provenance de l'annonce |
| Community | Étiquette utilisée dans les politiques BGP |
| Large Community | Communauté BGP étendue sur 96 bits |
| IXP | Point d'échange Internet |
| Route server | Système distribuant des routes entre participants |
| Transit IP | Service permettant d'accéder à des routes externes étendues |
| Peering | Échange de trafic et de routes entre réseaux |
| Route leak | Propagation de routes au-delà de la portée prévue |
| Prefix hijack | Annonce non autorisée attirant potentiellement le trafic |
| RPKI | Infrastructure à clés publiques appliquée aux ressources Internet |
| ROA | Autorisation d'origine de route |
| ROV | Validation d'origine de route |
| Valid | Annonce conforme à une autorisation applicable |
| Invalid | Annonce non conforme aux autorisations applicables |
| NotFound | Absence d'autorisation applicable permettant de valider l'origine |
| RTR | Protocole de communication entre un cache RPKI et un routeur |
| BMP | Protocole de collecte d'informations BGP |
| BFD | Mécanisme de détection de défaillance de chemin |
| Graceful Restart | Mécanisme de continuité conditionnelle pendant certains redémarrages |
| Graceful Shutdown | Mécanisme facilitant un retrait contrôlé de trafic |
| Route reflector | Routeur distribuant des routes iBGP |
| ECMP | Multipath à coûts égaux |
| FIB | Table utilisée par le plan de transfert |
| RIB | Base de routes utilisée par le plan de contrôle |
| Max-prefix | Limite du nombre de préfixes reçus |
| AS-path prepending | Répétition du numéro d'AS dans AS_PATH |
| ROA MaxLength | Longueur maximale autorisée pour un préfixe couvert par un ROA |

# 28. Références techniques officielles

Les documents suivants constituent les références principales pour approfondir BGP et la sécurité du routage.

## Spécifications BGP

- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)**  
  https://www.rfc-editor.org/rfc/rfc4271

- **RFC 4760 — Multiprotocol Extensions for BGP-4**  
  https://www.rfc-editor.org/rfc/rfc4760

- **RFC 6793 — BGP Support for Four-Octet Autonomous System (AS) Number Space**  
  https://www.rfc-editor.org/rfc/rfc6793

- **RFC 6996 — Autonomous System (AS) Reservation for Private Use**  
  https://www.rfc-editor.org/rfc/rfc6996

## Sécurité et validation

- **RFC 5082 — The Generalized TTL Security Mechanism (GTSM)**  
  https://www.rfc-editor.org/rfc/rfc5082

- **RFC 6811 — BGP Prefix Origin Validation**  
  https://www.rfc-editor.org/rfc/rfc6811

- **RFC 7454 — BGP Operations and Security**  
  https://www.rfc-editor.org/rfc/rfc7454

- **RFC 8205 — BGPsec Protocol Specification**  
  https://www.rfc-editor.org/rfc/rfc8205

- **RFC 8481 — Clarifications to BGPsec**  
  https://www.rfc-editor.org/rfc/rfc8481

- **RFC 8893 — Resource Public Key Infrastructure (RPKI) Origin Validation for BGP**  
  https://www.rfc-editor.org/rfc/rfc8893

- **RFC 9582 — A Profile for Route Origin Authorizations (ROAs)**  
  https://www.rfc-editor.org/rfc/rfc9582

## Exploitation et convergence

- **RFC 4724 — Graceful Restart Mechanism for BGP**  
  https://www.rfc-editor.org/rfc/rfc4724

- **RFC 8326 — Graceful BGP Session Shutdown**  
  https://www.rfc-editor.org/rfc/rfc8326

- **RFC 7854 — BGP Monitoring Protocol (BMP)**  
  https://www.rfc-editor.org/rfc/rfc7854

- **RFC 8212 — Default External BGP (EBGP) Route Propagation Behavior without Policies**  
  https://www.rfc-editor.org/rfc/rfc8212

- **RFC 9234 — Route Leak Prevention and Detection Using Roles in UPDATE and OPEN Messages**  
  https://www.rfc-editor.org/rfc/rfc9234

## Outils et documentation d'implémentation

- FRRouting — Documentation officielle : https://docs.frrouting.org/
- RIPE NCC — Ressources sur le routage et RPKI : https://www.ripe.net/
- Internet Assigned Numbers Authority (IANA) : https://www.iana.org/
- Internet Engineering Task Force (IETF) : https://www.ietf.org/
- Internet Society : https://www.internetsociety.org/
- PeeringDB : https://www.peeringdb.com/

Les RFC décrivent les spécifications protocolaires et les mécanismes normalisés. Les procédures opérationnelles, les recommandations de sécurité et les fonctionnalités des implémentations doivent être vérifiées dans leur documentation respective.

# 29. Checklist de mise en production

Avant d'activer une nouvelle session BGP, vérifier les points suivants.

## Architecture

- [ ] Le numéro d'AS local est correct.
- [ ] Le numéro d'AS distant est confirmé.
- [ ] L'adresse du voisin est documentée.
- [ ] L'interface et le transport sont validés.
- [ ] La joignabilité du next-hop est confirmée.
- [ ] La diversité des chemins est documentée.
- [ ] Le plan de retour arrière est disponible.

## Politique de routage

- [ ] La politique d'importation est définie.
- [ ] La politique d'exportation est définie.
- [ ] Les préfixes autorisés sont documentés.
- [ ] Les longueurs de préfixe sont contrôlées.
- [ ] Les routes par défaut sont traitées explicitement.
- [ ] Les routes privées et spéciales sont traitées.
- [ ] Les communautés sont documentées.
- [ ] Les limites de préfixes sont adaptées.
- [ ] Les politiques IPv4 et IPv6 sont séparées.

## Sécurité

- [ ] Les ACL autorisent uniquement les flux nécessaires.
- [ ] La sécurité de session est configurée si requise.
- [ ] Les accès d'administration sont protégés.
- [ ] La validation d'origine est configurée selon la politique.
- [ ] Les filtres d'exportation empêchent les fuites.
- [ ] Les procédures de changement sont documentées.
- [ ] Les secrets sont gérés de manière sécurisée.

## Exploitation

- [ ] Les sessions sont supervisées.
- [ ] Le nombre de routes est supervisé.
- [ ] Les annonces sortantes sont vérifiées.
- [ ] Le plan de données est testé.
- [ ] Les scénarios de panne sont validés.
- [ ] Les alertes sont fonctionnelles.
- [ ] Les procédures d'incident sont documentées.

# 30. Conclusion générale

BGP est bien plus qu'un protocole permettant d'échanger des routes. C'est le mécanisme qui permet à des réseaux administrativement indépendants de construire une connectivité globale tout en conservant leurs propres politiques.

La compétence d'un ingénieur BGP expert ne se mesure pas uniquement à sa capacité à établir une session.

Elle se mesure à sa capacité à concevoir une architecture cohérente, à exprimer les politiques de routage de manière explicite, à protéger les annonces, à assurer la convergence, à interpréter les incidents et à démontrer que le trafic suit réellement les chemins attendus.

Les points les plus importants à retenir sont :

1. **Une session établie n'est pas une preuve de routage correct.**
2. **Les politiques d'importation et d'exportation doivent être explicites.**
3. **LOCAL_PREF, AS_PATH et MED remplissent des rôles différents.**
4. **Le transit et le peering correspondent à des relations distinctes.**
5. **Un route server facilite les échanges de routes sans être nécessairement dans le chemin de données.**
6. **RPKI améliore la validation d'origine mais ne sécurise pas à lui seul l'intégralité d'AS_PATH.**
7. **Les fuites de routes doivent être prévenues par des politiques adaptées, et non uniquement détectées après incident.**
8. **La redondance doit couvrir les chemins physiques, les routeurs et les dépendances de contrôle.**
9. **La supervision doit observer les routes, les sessions, le plan de données et les changements de politique.**
10. **Toute modification de routage doit être testée, documentée et réversible.**

La maîtrise de ces principes permet de concevoir des réseaux multihomés et des infrastructures opérateur plus résilientes, plus prévisibles et plus sûres.

