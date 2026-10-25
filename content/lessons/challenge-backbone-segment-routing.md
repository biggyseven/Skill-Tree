# Challenge d'architecture réseau — Backbone et Segment Routing

> **Fichier :** `challenge-backbone-segment-routing.md`
>
> **Domaine :** architecture backbone opérateur, routage IP/MPLS, Segment Routing, ingénierie de trafic et haute disponibilité.
>
> **Progression :** Débutant → Intermédiaire → Expert.
>
> **Environnement :** réseau de transport IP d'un opérateur ou d'une grande entreprise multisite.
>
> **Technologies étudiées :** IPv4, IPv6, OSPF, IS-IS, MPLS, SR-MPLS, Prefix-SID, Node-SID, Adjacency-SID, SR Policy, BGP, protection locale et SRv6.
>
> **Objectif final :** concevoir, configurer, sécuriser et valider un backbone capable de transporter des services avec des chemins prévisibles, une convergence maîtrisée et une politique de routage documentée.


# 1. Présentation du challenge

## 1.1. Contexte

Vous êtes ingénieur réseau au sein de **NovaCarrier**, un opérateur qui fournit des services IP aux entreprises, des liaisons intersites, des VPN IP/MPLS et des services de connectivité à plusieurs points de présence.

Le réseau actuel repose sur des routeurs interconnectés par des liens à haut débit. Le routage IP fonctionne, mais plusieurs problèmes sont apparus :

- Les chemins empruntés par certains flux sont difficiles à prévoir.
- Une panne de lien entraîne parfois une interruption plus longue que prévu.
- La répartition du trafic ne correspond pas toujours aux capacités disponibles.
- Les politiques de routage sont complexes à maintenir.
- Certains liens sont fortement utilisés alors que d'autres restent peu chargés.
- L'exploitation des services VPN dépend de plusieurs technologies et configurations.
- Les changements doivent être soigneusement coordonnés entre les équipes.
- Les ingénieurs souhaitent mieux contrôler les chemins du trafic sans créer une configuration manuelle différente pour chaque flux.

L'entreprise envisage d'introduire **Segment Routing (SR)** dans son backbone.

Votre mission consiste à concevoir une architecture évolutive qui conserve les fonctions classiques du routage IP, introduit Segment Routing de manière progressive et permet de démontrer le fonctionnement des chemins et des mécanismes de protection.

## 1.2. Le problème à résoudre

Un protocole de routage IP classique sélectionne des chemins selon sa métrique et sa politique de calcul.

Cette approche est efficace pour construire une connectivité robuste. Cependant, elle ne permet pas toujours à l'opérateur d'exprimer simplement des intentions de chemin particulières, par exemple :

- Faire passer un trafic par une région précise du backbone.
- Éviter un lien connu pour être proche de la saturation.
- Préférer un chemin présentant une latence plus faible.
- Diriger certains flux vers un point de sortie déterminé.
- Définir une politique principale et une politique de secours.
- Préparer une protection locale contre certaines pannes.
- Appliquer des intentions de transport cohérentes à plusieurs services.

Segment Routing permet de représenter un chemin comme une séquence d'instructions appelées **segments**.

Dans SR-MPLS, ces instructions sont représentées dans une pile de labels MPLS. Dans SRv6, elles sont représentées par des identifiants de segments IPv6, avec les mécanismes définis pour cette technologie.

Les notions fondamentales de Segment Routing sont décrites dans la [RFC 8402 — Segment Routing Architecture](https://www.rfc-editor.org/rfc/rfc8402.html).

## 1.3. Objectifs métier

NovaCarrier souhaite :

1. Assurer la connectivité entre tous ses points de présence.
2. Réduire les interruptions lors des pannes de liens.
3. Contrôler certains chemins de bout en bout.
4. Équilibrer plus efficacement la charge.
5. Simplifier la signalisation des chemins par rapport à certaines architectures MPLS traditionnelles.
6. Conserver une architecture de routage compréhensible.
7. Séparer le routage de transport des services VPN.
8. Mettre en place des mécanismes de validation avant les changements.
9. Superviser les chemins, les labels et les politiques SR.
10. Préparer une éventuelle évolution vers SRv6.

Ces objectifs ne signifient pas que Segment Routing apporte automatiquement une garantie de bande passante, une latence minimale ou une absence d'interruption. Ces résultats dépendent de la conception, des mécanismes de protection, de la capacité des liens et des fonctions effectivement prises en charge par les équipements.


# 2. Organisation des niveaux

Le challenge est divisé en trois niveaux cumulatifs.

## Niveau 1 — Débutant : comprendre le backbone

Vous devez :

- Identifier les routeurs de cœur et de bordure.
- Comprendre la différence entre IGP, BGP et MPLS.
- Construire une topologie IP cohérente.
- Définir les loopbacks et les adresses de liens.
- Configurer OSPF ou IS-IS.
- Comprendre le fonctionnement de la table de routage.
- Vérifier les chemins principaux et les chemins de secours.
- Comprendre la différence entre un routeur PE et un routeur P.
- Expliquer les objectifs de Segment Routing.

**Livrable :** une architecture backbone fonctionnelle et documentée, sans dépendre initialement de Segment Routing.

## Niveau 2 — Intermédiaire : mettre en place SR-MPLS

Vous devez :

- Activer les extensions Segment Routing d'un IGP pris en charge.
- Définir un plan de SIDs.
- Distinguer Node-SID, Prefix-SID et Adjacency-SID.
- Comprendre le rôle du SRGB.
- Vérifier la distribution des informations SR.
- Interpréter une pile de labels.
- Comprendre une politique de chemin.
- Tester les mécanismes de protection.
- Diagnostiquer les incohérences de labels et de routage.

**Livrable :** une architecture SR-MPLS validée, avec un plan de SIDs et des preuves de transfert des paquets.

## Niveau 3 — Expert : ingénierie de trafic et architecture avancée

Vous devez :

- Concevoir des SR Policies.
- Comprendre les couleurs et les endpoints de politique.
- Étudier les chemins explicites et les chemins calculés.
- Évaluer la protection locale et la convergence.
- Concevoir une politique de secours.
- Étudier les interactions avec BGP et les VPN.
- Comprendre l'utilisation éventuelle de BGP-LS et PCEP.
- Évaluer les performances et les risques liés à la taille des piles.
- Comparer SR-MPLS et SRv6.
- Préparer l'automatisation et les procédures de retour arrière.

**Livrable :** un dossier complet de backbone avec politiques de transport, scénarios de panne, tests de convergence et justification de l'architecture retenue.


# 3. Défi 1 — Identifier les composants d'un backbone

## 3.1. Les rôles principaux

Un backbone est un réseau de transport reliant plusieurs sites ou points de présence. Il transporte les communications d'un grand nombre de services.

Les fonctions suivantes doivent être distinguées.

| Élément | Rôle principal |
|---|---|
| Routeur PE | Routeur de bordure auquel les clients ou les services sont raccordés |
| Routeur P | Routeur de cœur qui transporte le trafic à travers le backbone |
| IGP | Diffuse la topologie interne et calcule les routes de transport |
| BGP | Échange des routes entre systèmes autonomes ou transporte des informations de service selon l'architecture |
| MPLS | Transporte les paquets à l'aide de labels |
| Segment Routing | Encode des instructions de chemin dans les paquets |
| Node-SID | Identifie une instruction de transport associée à un nœud |
| Adjacency-SID | Identifie une instruction associée à une adjacence particulière |
| SR Policy | Associe une intention de chemin à une séquence de segments |
| BGP-LS | Expose des informations de topologie et de routage à des systèmes qui en ont besoin |
| PCEP | Permet, dans les architectures qui le prennent en charge, l'échange de demandes ou d'informations de chemin entre un client et un serveur PCE |
| NMS / contrôleur | Supervise ou pilote l'infrastructure selon les capacités retenues |

Les rôles P et PE décrivent des fonctions dans une architecture opérateur. Ils ne déterminent pas à eux seuls les fonctions matérielles d'un modèle de routeur particulier.

## 3.2. Routeur P et routeur PE

Le routeur P appartient au cœur de transport.

Il assure principalement le transfert des paquets à l'intérieur du backbone. Il n'a pas nécessairement besoin de connaître tous les préfixes client ou toutes les routes VPN.

Le routeur PE se trouve à la frontière entre le réseau de transport et les services.

Il peut notamment :

- Raccorder les sites clients.
- Terminer des interfaces de service.
- Appliquer des politiques de sécurité ou de QoS.
- Participer au routage BGP des services.
- Ajouter ou retirer les labels de service appropriés.

Dans une architecture MPLS VPN, le PE joue un rôle important dans la séparation des routes des clients. Le plan de transport SR-MPLS ne remplace pas le plan de service BGP VPN lorsqu'il est nécessaire.

## 3.3. Schéma de référence

```text
          SITE CLIENT A                         SITE CLIENT B
               |                                     |
               |                                     |
          +----------+                          +----------+
          | PE-A     |                          | PE-B     |
          | Bordure  |                          | Bordure  |
          +----------+                          +----------+
               | \                                 / |
               |  \                               /  |
               |   \                             /   |
               |    v                           v    |
               |  +----------+             +----------+
               |  |   P-1    |             |   P-2    |
               |  | CŒUR IP  |             | CŒUR IP  |
               |  +----------+             +----------+
               |       \                       /       |
               |        \                     /        |
               |         +-------------------+         |
               |                                       |
               +---------------------------------------+
                               |
                     Réseau de transport
                     IP / MPLS / Segment Routing
```

Ce schéma montre les rôles généraux. Il ne représente pas encore une topologie suffisamment détaillée pour vérifier les chemins de secours.

Vous devrez développer un plan de câblage logique où chaque lien et chaque voisinage de routage sont identifiables.


# 4. Architecture 1 — Backbone IP de référence

Avant de configurer Segment Routing, construisez un backbone IP fonctionnel.

Segment Routing s'appuie sur l'existence d'une connectivité de transport cohérente. Une architecture SR mal conçue ne compensera pas un plan d'adressage incorrect, une mauvaise topologie ou un IGP instable.

## 4.1. Topologie du laboratoire

Le laboratoire comprend :

- Trois routeurs de bordure : PE1, PE2 et PE3.
- Deux routeurs de cœur : P1 et P2.
- Des liens redondants entre les PE et les routeurs P.
- Des loopbacks utilisées pour identifier les routeurs.
- Un IGP unique dans le domaine de transport.

## 4.2. Schéma physique et logique

```text
                      +------------------+
                      |      PE1         |
                      | Point de présence|
                      +------------------+
                        |              |
                        |              |
                        v              v
                  +-----------+   +-----------+
                  |    P1     |   |    P2     |
                  |  ROUTEUR  |   |  ROUTEUR  |
                  |  DE CŒUR  |   |  DE CŒUR  |
                  +-----------+   +-----------+
                        ^              ^
                        |              |
                        |              |
                 +------+--------------+------+
                 |                             |
                 |                             |
                 v                             v
             +----------+                  +----------+
             |   PE2    |                  |   PE3    |
             | Bordure  |                  | Bordure  |
             +----------+                  +----------+
```

La représentation est simplifiée. La topologie détaillée retenue pour le challenge est la suivante :

```text
                         PE1
                        /   \
                       /     \
                      P1     P2
                     /  \   /  \
                    /    \ /    \
                   PE2            PE3
```

Pour la suite des exercices, considérez que **chaque PE est directement connecté à P1 et P2**. Chaque lien PE–P doit être indépendant au niveau de la connexion physique autant que le laboratoire le permet.

Cette topologie offre des chemins alternatifs entre les PE. Elle n'implique pas qu'ils seront tous utilisés simultanément : cela dépend du routage, de la métrique et des politiques de transfert.

## 4.3. Objectifs de la première phase

Avant d'activer Segment Routing, vous devez démontrer que :

1. Tous les liens sont actifs.
2. Chaque routeur possède une loopback unique.
3. Les voisinages IGP sont établis.
4. Tous les routeurs apprennent les loopbacks nécessaires.
5. Les chemins sont cohérents.
6. Une panne de lien provoque le comportement attendu.
7. Les tables de routage ne contiennent pas de préfixes inattendus.

Les commandes exactes dépendront de votre plateforme. Dans le laboratoire, utilisez les commandes équivalentes à :

```text
show ip interface brief
show interfaces
show ip route
show ospf neighbor
show isis adjacency
show logging
```

Certaines commandes sont propres à OSPF, d'autres à IS-IS. Elles représentent des exemples d'outils de vérification, pas une liste à copier intégralement sur chaque équipement.


# 5. Défi 2 — Plan d'adressage du backbone

## 5.1. Principes

Le plan d'adressage doit distinguer :

- Les loopbacks des routeurs.
- Les liens point à point.
- Les réseaux de gestion.
- Les interfaces de service.
- Les réseaux client.
- Les adresses utilisées pour les tests.

Les adresses illustratives de cette section appartiennent à des plages privées et sont réservées au laboratoire. Elles ne doivent pas être réutilisées sans contrôle dans un environnement connecté à d'autres réseaux.

## 5.2. Loopbacks

Utilisez le bloc `10.255.255.0/24` pour les loopbacks du domaine de transport.

| Routeur | Loopback0 | Rôle |
|---|---|---|
| PE1 | `10.255.255.1/32` | Bordure A |
| PE2 | `10.255.255.2/32` | Bordure B |
| PE3 | `10.255.255.3/32` | Bordure C |
| P1 | `10.255.255.11/32` | Cœur 1 |
| P2 | `10.255.255.12/32` | Cœur 2 |

Les adresses `/32` donnent à chaque routeur un identifiant stable, indépendant de l'adresse de ses interfaces de transport.

Les loopbacks doivent être annoncées dans l'IGP si les autres routeurs en ont besoin pour le transport, les sessions de routage ou les fonctions SR retenues.

## 5.3. Adressage des liens point à point

Pour le laboratoire, utilisez des sous-réseaux `/31` si les équipements prennent en charge ce type de lien IPv4.

| Lien | Sous-réseau | Première extrémité | Seconde extrémité |
|---|---|---|---|
| PE1–P1 | `10.255.0.0/31` | PE1 `10.255.0.0` | P1 `10.255.0.1` |
| PE1–P2 | `10.255.0.2/31` | PE1 `10.255.0.2` | P2 `10.255.0.3` |
| PE2–P1 | `10.255.0.4/31` | PE2 `10.255.0.4` | P1 `10.255.0.5` |
| PE2–P2 | `10.255.0.6/31` | PE2 `10.255.0.6` | P2 `10.255.0.7` |
| PE3–P1 | `10.255.0.8/31` | PE3 `10.255.0.8` | P1 `10.255.0.9` |
| PE3–P2 | `10.255.0.10/31` | PE3 `10.255.0.10` | P2 `10.255.0.11` |

Un lien `/31` fournit deux adresses d'extrémité. Vérifiez la prise en charge de ce préfixe par le système utilisé.

## 5.4. Diagramme de l'adressage

```text
                         PE1
                Lo0: 10.255.255.1/32
                    /             \
                   /               \
       10.255.0.0/31             10.255.0.2/31
                 /                   \
                v                     v
        P1: 10.255.0.1          P2: 10.255.0.3
        Lo0: 10.255.255.11       Lo0: 10.255.255.12
                ^                     ^
                |                     |
       10.255.0.4/31             10.255.0.6/31
                |                     |
                +--------- PE2 -------+
                         Lo0:
                    10.255.255.2/32

PE3 est également raccordé à P1 et P2 :
- PE3–P1 : 10.255.0.8/31
- PE3–P2 : 10.255.0.10/31
- Loopback PE3 : 10.255.255.3/32
```

Ce diagramme illustre les valeurs d'adressage. Le plan complet de câblage doit être conservé dans le dossier technique avec les numéros d'interfaces de chaque lien.

## 5.5. Vérifications

Sur chaque routeur :

1. Vérifiez l'adresse de Loopback0.
2. Vérifiez les adresses de toutes les interfaces de transport.
3. Vérifiez les masques.
4. Confirmez l'état des interfaces.
5. Vérifiez les routes vers toutes les loopbacks.
6. Testez la connectivité entre chaque paire de loopbacks.
7. Vérifiez qu'aucune adresse n'est dupliquée.

Ne passez pas à Segment Routing tant que le domaine de transport de base n'est pas stable.


# 6. Défi 3 — IGP : OSPF ou IS-IS

## 6.1. Rôle de l'IGP

L'IGP fournit une représentation de la topologie interne et calcule les chemins vers les destinations du domaine de transport.

Segment Routing s'appuie couramment sur les extensions de protocoles de routage à état de liens afin de distribuer les informations nécessaires aux segments.

Les principales options du challenge sont :

- OSPF avec les extensions SR correspondantes.
- IS-IS avec les extensions SR correspondantes.

Les extensions SR pour OSPF sont décrites dans la [RFC 8665](https://www.rfc-editor.org/rfc/rfc8665.html). Les extensions SR pour IS-IS sont décrites dans la [RFC 8667](https://www.rfc-editor.org/rfc/rfc8667.html).

## 6.2. OSPF ou IS-IS ?

| Critère | OSPF | IS-IS |
|---|---|---|
| Type | IGP à état de liens | IGP à état de liens |
| Organisation | Aires OSPF | Niveaux IS-IS |
| Usage en entreprise | Très courant | Moins courant dans certains environnements |
| Usage opérateur | Courant | Très courant dans les réseaux de transport |
| Extensions SR | Disponibles selon les extensions et la plateforme | Disponibles selon les extensions et la plateforme |
| Choix | Dépend des compétences et de l'environnement | Dépend des compétences et de l'environnement |

Il n'existe pas de choix universellement meilleur pour tous les backbones.

Pour le laboratoire, choisissez **un seul IGP principal** afin de comprendre précisément le comportement de la topologie et de ses extensions SR.

La configuration simultanée d'OSPF et d'IS-IS n'est pas nécessaire pour cet exercice. Elle introduirait des questions de redistribution et de cohérence qui ne sont pas utiles à ce stade.

## 6.3. Paramètres à définir

Le dossier doit préciser :

- L'identité de chaque routeur.
- Les interfaces incluses dans l'IGP.
- Les loopbacks annoncées.
- Les métriques des liens.
- Les aires ou niveaux.
- Les mécanismes d'authentification disponibles.
- Les filtres d'annonces éventuels.
- Les mécanismes de convergence.
- Les extensions SR qui seront activées.

Dans un backbone de transport, il est important d'éviter les modifications incohérentes des métriques. Une métrique mal choisie peut déplacer des volumes de trafic importants.

## 6.4. Exercice de métriques

Supposons que :

- PE1 possède deux chemins vers PE2.
- Le chemin via P1 est préféré par la métrique IGP.
- Le chemin via P2 constitue une alternative.

Vous devez :

1. Relever les métriques des liens.
2. Calculer le coût de chaque chemin.
3. Vérifier le chemin retenu.
4. Modifier une métrique dans le laboratoire.
5. Observer la nouvelle route.
6. Vérifier le trafic réellement transmis.
7. Mesurer le temps de convergence.

Une route dans la table de routage ne garantit pas que le paquet observé emprunte le chemin imaginé si d'autres mécanismes interviennent dans le transfert.


# 7. Architecture 2 — Comprendre MPLS avant Segment Routing

## 7.1. Rappel sur MPLS

MPLS permet de transporter des paquets à l'aide d'étiquettes, ou labels.

Dans une architecture MPLS, un routeur peut utiliser les labels pour transférer un paquet vers le prochain saut sans effectuer uniquement une recherche classique sur le préfixe IP de destination.

Les routeurs utilisent les informations de transfert MPLS pour déterminer l'action à appliquer aux labels présents dans le paquet.

Selon la technologie et l'architecture, les actions comprennent notamment :

- L'ajout d'un label.
- Le remplacement d'un label.
- Le retrait d'un label.
- Le transfert vers le prochain saut.
- La gestion d'une pile contenant plusieurs labels.

## 7.2. Architecture MPLS de référence

```text
                  PAQUET IP DU CLIENT
                           |
                           v
                      +----------+
                      | PE1      |
                      | Ingress  |
                      +----------+
                           |
                  Ajout d'une pile
                    de labels MPLS
                           |
                           v
                      +----------+
                      | P1       |
                      | Transit  |
                      +----------+
                           |
                    Échange du label
                    selon la LFIB
                           |
                           v
                      +----------+
                      | PE2      |
                      | Egress   |
                      +----------+
                           |
                    Retrait du label
                    de transport
                           |
                           v
                   PAQUET VERS CLIENT
```

Le schéma représente un chemin simplifié. Les opérations exactes dépendent des labels présents et du service transporté.

Dans une architecture VPN, il peut exister un label de transport et un label de service, par exemple un label associé à une route VPN ou à une fonction de transfert au PE distant.

## 7.3. Rôle du LDP et du RSVP-TE

Dans des architectures MPLS traditionnelles :

- LDP peut distribuer des labels associés aux routes de transport.
- RSVP-TE peut établir des chemins explicitement contrôlés avec des mécanismes de signalisation et de réservation selon la configuration.
- BGP peut transporter les routes et informations de services VPN.
- L'IGP assure la découverte et le routage de base du domaine.

Ces protocoles ont des rôles distincts.

Segment Routing permet de représenter des chemins en utilisant une séquence de segments. En SR-MPLS, ces segments sont transportés sous forme de labels MPLS.

Dans une architecture SR-MPLS, il n'est pas nécessaire de déployer LDP ou RSVP-TE uniquement pour établir les chemins SR de base. Toutefois, SR peut coexister avec des mécanismes MPLS traditionnels dans certains environnements.

Ne concluez pas que l'introduction de SR supprime automatiquement toutes les fonctions ou toutes les dépendances MPLS existantes. Il faut analyser les services réellement utilisés.

## 7.4. Exercice comparatif

Comparez les architectures suivantes :

1. IP avec IGP seul.
2. MPLS avec LDP.
3. MPLS avec RSVP-TE.
4. SR-MPLS avec IGP étendu.
5. SR-MPLS avec des SR Policies.

Pour chacune, expliquez :

- Comment le chemin est établi.
- Comment les informations nécessaires sont distribuées.
- Où se trouve l'état associé au chemin.
- Comment une panne est traitée.
- Comment les chemins explicites sont représentés.
- Quelles fonctions supplémentaires sont nécessaires à l'ingénierie de trafic.
- Quelles limites restent présentes.


# 8. Défi 4 — Introduction à Segment Routing

## 8.1. Principe fondamental

Segment Routing repose sur une liste ordonnée de segments.

Un segment représente une instruction appliquée au traitement d'un paquet.

Dans SR-MPLS, les segments sont représentés par des labels MPLS.

Dans SRv6, ils sont représentés par des identifiants IPv6 et peuvent utiliser un Segment Routing Header, ou SRH.

L'architecture générale est spécifiée par la [RFC 8402](https://www.rfc-editor.org/rfc/rfc8402.html).

## 8.2. Schéma conceptuel

```text
                ROUTEUR D'ENTRÉE
                       |
                       | Le trafic correspond
                       | à une politique SR
                       v
              +-------------------+
              | LISTE DE SEGMENTS |
              |                   |
              | Segment 1         |
              | Segment 2         |
              | Segment 3         |
              +-------------------+
                       |
                       v
                  ROUTEUR DE
                    TRANSIT
                       |
             Traitement du segment
             actif et transfert
                       |
                       v
                ROUTEUR SUIVANT
                       |
                       v
                 ROUTEUR FINAL
```

La liste de segments exprime un chemin ou une séquence d'instructions. Le comportement exact dépend du type de SID utilisé.

Le routeur d'entrée est souvent appelé headend de la politique. C'est à ce point que le trafic est associé à la politique SR.

Les routeurs intermédiaires suivent les instructions qu'ils comprennent. Ils n'ont pas nécessairement besoin d'un état de signalisation distinct pour chaque chemin de bout en bout, contrairement à certaines architectures utilisant des LSP signalés individuellement.

## 8.3. Les deux principales formes

### SR-MPLS

```text
+----------------------------------------------------------+
| Ethernet | Label externe | Label suivant | Paquet IP    |
+----------------------------------------------------------+
```

Les segments sont représentés par une pile de labels MPLS.

### SRv6

```text
+----------------------------------------------------------+
| Ethernet | En-tête IPv6 | SRH avec SIDs | Paquet interne |
+----------------------------------------------------------+
```

SRv6 utilise le plan de données IPv6 et le Segment Routing Header lorsque les mécanismes SRH sont employés.

Le détail des champs du SRH est défini dans la [RFC 8754](https://www.rfc-editor.org/rfc/rfc8754.html). Les comportements de programmation réseau SRv6 sont décrits dans la [RFC 8986](https://www.rfc-editor.org/rfc/rfc8986.html).

## 8.4. Pourquoi Segment Routing ?

Les objectifs peuvent inclure :

- Exprimer des chemins de façon flexible.
- Réduire le besoin d'état par chemin dans le cœur pour de nombreux scénarios.
- Contrôler les chemins des flux.
- Faciliter certaines stratégies d'ingénierie de trafic.
- Exploiter les informations de topologie diffusées par l'IGP.
- Intégrer les politiques au plan de transport.

Ces avantages dépendent de la plateforme, du plan de contrôle et de la façon dont les services sont conçus.

Segment Routing ne remplace pas l'IGP. L'IGP reste fondamental pour la connaissance de la topologie, l'accessibilité des destinations et de nombreux mécanismes de transfert.


# 9. Défi 5 — Comprendre les SIDs

Un SID, ou Segment Identifier, identifie une instruction de Segment Routing.

Tous les SIDs ne représentent pas la même action. Il est essentiel de comprendre leur rôle.

## 9.1. Prefix-SID et Node-SID

Un Prefix-SID est associé à un préfixe annoncé par un routeur. Un cas très courant est le Node-SID associé à la loopback d'un routeur.

Le Node-SID représente une instruction permettant d'atteindre le nœud correspondant en utilisant le chemin calculé par l'IGP.

Ce chemin n'est pas nécessairement un chemin physique unique si le réseau dispose de plusieurs chemins à coût égal.

## 9.2. Adjacency-SID

Un Adjacency-SID représente une instruction associée à une adjacence particulière.

Il peut être utilisé lorsqu'une politique doit emprunter un lien ou une adjacence spécifique, sous réserve des capacités de la plateforme et des règles de traitement.

Un Adjacency-SID est généralement local à son nœud d'origine. Il ne faut pas le traiter comme une étiquette globale qui désignerait partout le même lien.

## 9.3. Binding SID

Un Binding SID, ou BSID, permet d'identifier une politique ou une instruction de segment liée à un ensemble de segments ou à un comportement de transfert.

Il peut simplifier la représentation d'une politique complexe en permettant à d'autres politiques ou services de référencer ce point d'entrée.

Son fonctionnement exact et les possibilités d'imbrication dépendent du type de SID et de la plateforme.

## 9.4. Tableau de synthèse

| Type de SID | Rôle | Portée conceptuelle |
|---|---|---|
| Prefix-SID | Instruction associée à un préfixe | Généralement distribuée dans le domaine SR |
| Node-SID | Atteindre un nœud via le chemin IGP | Typiquement globale dans le SRGB commun, si ce mode est utilisé |
| Adjacency-SID | Utiliser une adjacence particulière | Généralement locale au nœud |
| Binding SID | Référencer une politique ou un comportement lié à une liste de segments | Selon l'allocation et la plateforme |
| SID de service | Appliquer un traitement de service défini | Selon le type de SID et le plan de données |

La distinction entre le plan de contrôle qui annonce les informations SR et le plan de données qui applique les instructions est fondamentale.

## 9.5. Exercice

Pour chaque type de SID :

1. Expliquez le rôle.
2. Indiquez comment il est distribué ou installé.
3. Décrivez son comportement.
4. Identifiez les équipements qui doivent le comprendre.
5. Expliquez son intérêt pour la politique de chemin.
6. Décrivez ce qui se passe si l'information attendue est absente.
7. Proposez un test permettant de vérifier son fonctionnement.


# 10. Défi 6 — SRGB, index et plan de SIDs

## 10.1. Qu'est-ce que le SRGB ?

Le Segment Routing Global Block, ou SRGB, est une plage de labels réservée à l'usage des SIDs globaux dans SR-MPLS.

Lorsqu'un SID global est représenté par un index, le label correspondant est calculé à partir de la base SRGB et de l'index, selon les conventions et le mode d'allocation de la plateforme.

Exemple pédagogique :

```text
SRGB de référence :
  Début : 16000
  Fin   : 23999

Index du Node-SID :
  101

Calcul illustratif :
  Label = 16000 + 101
        = 16101
```

Ce calcul ne doit être utilisé que si les équipements partagent la convention de SRGB prévue et si la plateforme représente le SID par cet index.

Tous les équipements n'utilisent pas nécessairement une plage identique. Une incohérence de SRGB ou de représentation des SIDs peut conduire à une interprétation différente de la même valeur.

## 10.2. Plan de SIDs du laboratoire

Pour les exercices, utilisez les index suivants avec un SRGB de référence `16000–23999`.

| Routeur | Loopback | Index de Node-SID | Label illustratif |
|---|---|---:|---:|
| PE1 | `10.255.255.1/32` | 101 | 16101 |
| PE2 | `10.255.255.2/32` | 102 | 16102 |
| PE3 | `10.255.255.3/32` | 103 | 16103 |
| P1 | `10.255.255.11/32` | 111 | 16111 |
| P2 | `10.255.255.12/32` | 112 | 16112 |

Les labels du tableau sont des valeurs dérivées de la convention pédagogique. Ils ne doivent pas être copiés comme configuration universelle.

Pour les Adjacency-SIDs, documentez la portée et l'action associée. Évitez d'attribuer arbitrairement des labels présentés comme globalement significatifs à des SIDs locaux.

## 10.3. Règles d'allocation

Un plan de SIDs doit préciser :

- La plage SRGB.
- Les index réservés.
- Les Node-SIDs affectés.
- La méthode d'attribution.
- Les règles en cas d'ajout de routeur.
- La cohérence entre équipements.
- Les valeurs locales de SID.
- Les procédures de remplacement de matériel.
- Les outils de validation.

Le plan doit aussi tenir compte des contraintes de la plateforme et des éventuelles fonctions déjà présentes dans la configuration.

## 10.4. Exercice de cohérence

Pour chaque routeur :

1. Relevez le SRGB configuré.
2. Relevez le Node-SID annoncé.
3. Vérifiez le calcul ou la représentation retenue.
4. Comparez la valeur attendue à celle observée.
5. Contrôlez la table de labels.
6. Vérifiez la connectivité à la loopback.
7. Confirmez que les autres routeurs interprètent le SID de manière cohérente.

Une simple présence du label dans une table ne garantit pas que le paquet empruntera le chemin attendu.


# 11. Architecture 3 — Backbone SR-MPLS

Cette architecture constitue la cible principale du niveau intermédiaire.

## 11.1. Schéma logique

```text
                         +------------------+
                         | PE1              |
                         | Headend potentiel|
                         +------------------+
                             |          |
                             |          |
                             v          v
                       +---------+  +---------+
                       | P1      |  | P2      |
                       | SR-MPLS |  | SR-MPLS |
                       +---------+  +---------+
                             |          |
                             |          |
                             v          v
                         +------------------+
                         | PE2              |
                         | Egress potentiel |
                         +------------------+
                                  |
                             Site distant
```

Les routeurs doivent posséder les informations nécessaires pour transférer les paquets suivant les SIDs présents dans la pile.

Le domaine SR repose sur :

- Un underlay routé.
- Un IGP cohérent.
- Les extensions SR du protocole retenu.
- Un plan de SIDs cohérent.
- Les fonctions MPLS requises par la plateforme.
- Les politiques de sécurité et d'exploitation.

## 11.2. Architecture de contrôle

```text
                    PLAN DE CONTRÔLE
              +--------------------------+
              | OSPF ou IS-IS avec SR    |
              | Topologie / préfixes    |
              | Informations de SIDs     |
              +--------------------------+
                           |
                  Informations distribuées
                           |
           +---------------+----------------+
           |               |                |
           v               v                v
          PE1              P1               PE2


                    PLAN DE DONNÉES
              +--------------------------+
              | Labels MPLS / LFIB       |
              | Transfert des paquets    |
              +--------------------------+
                           |
             +-------------+-------------+
             |                           |
             v                           v
          Chemin SR                  Chemin alternatif
          préféré                   selon les politiques
```

Le plan de contrôle décrit la topologie et les informations nécessaires aux chemins SR.

Le plan de données applique les actions de transfert aux paquets.

Les deux plans doivent être vérifiés séparément pendant le dépannage.

## 11.3. Activation de SR-MPLS

La procédure exacte dépend de la plateforme.

Le processus conceptuel comprend :

1. Vérifier que MPLS est pris en charge et correctement préparé.
2. Configurer le SRGB si le système le demande.
3. Activer les extensions SR de l'IGP.
4. Associer les SIDs attendus aux préfixes.
5. Vérifier la distribution des informations.
6. Vérifier les labels et leur comportement de transfert.
7. Vérifier les routes et les chemins.
8. Réaliser un test sur un flux contrôlé.
9. Préparer le retour arrière.

La syntaxe de configuration n'est pas universelle. Utilisez les commandes adaptées au système réseau exact.

## 11.4. Vérifications

Collectez les informations équivalentes à :

```text
État des interfaces
Voisinages OSPF ou IS-IS
Table de routage IP
Informations SR annoncées par l'IGP
SRGB et SIDs locaux
Table LFIB / transfert MPLS
Chemin suivi par un paquet de test
Événements de routage et de transfert
```

Le dossier du laboratoire doit contenir des captures de commandes avant et après l'activation de SR-MPLS.


# 12. Défi 7 — Comprendre une pile de labels SR-MPLS

Une pile de labels représente une suite d'instructions de transport.

Le label situé au sommet de la pile est traité en premier par le nœud qui reçoit le paquet.

## 12.1. Exemple conceptuel

Supposons que PE1 doive envoyer un paquet vers PE2 en empruntant un chemin contrôlé par les segments suivants :

1. Node-SID de P1.
2. Node-SID de PE2.

La pile de labels peut être représentée conceptuellement comme suit :

```text
Sommet de pile
      |
      v
+---------------------+
| Node-SID P1         |
| Label illustratif   |
+---------------------+
| Node-SID PE2        |
| Label illustratif   |
+---------------------+
| Paquet IP original  |
+---------------------+
      |
      v
Bas de pile
```

Dans cet exemple, le premier segment demande d'atteindre P1. Une fois le segment correspondant traité, le segment suivant guide le paquet vers PE2.

Le chemin précis dépend du comportement associé au SID, du calcul IGP, des éventuels chemins à coût égal et des autres politiques de transfert.

## 12.2. Important : un Node-SID ne désigne pas nécessairement un lien précis

Un Node-SID représente généralement une instruction pour atteindre un nœud selon le chemin IGP prévu.

Si plusieurs chemins à coût égal existent, le trafic peut être réparti conformément aux mécanismes de transfert.

Pour contraindre une politique à une adjacence précise, un Adjacency-SID peut être pertinent lorsque la plateforme et l'architecture le prennent en charge.

## 12.3. Exercice

Vous devez répondre aux questions suivantes :

1. Quel SID est au sommet de la pile ?
2. Quel routeur doit traiter ce SID en premier ?
3. Quelle instruction est exécutée ensuite ?
4. Comment le paquet passe-t-il au segment suivant ?
5. Où le label peut-il être retiré ?
6. Comment vérifier la pile pendant le transfert ?
7. Quelles conséquences auraient un SID incorrect ou absent ?
8. Comment le chemin change-t-il si l'IGP modifie les métriques ?


# 13. Défi 8 — Protection contre les pannes

Segment Routing peut être combiné à différents mécanismes de protection et de convergence.

Toutefois, il faut distinguer :

- La convergence de l'IGP.
- La protection locale d'un lien ou d'un nœud.
- Le recalcul d'une politique SR.
- Le basculement vers un chemin alternatif.
- Le rétablissement du chemin nominal.

Ces mécanismes n'ont pas nécessairement le même délai et ne protègent pas contre toutes les défaillances.

## 13.1. Topologie de protection

```text
                      PE1
                     /   \
                    /     \
                   P1     P2
                    \     /
                     \   /
                      PE2
```

Le chemin préféré peut emprunter P1, tandis que P2 fournit un chemin alternatif.

## 13.2. Scénario de panne

Avant la panne :

```text
PE1 ---> P1 ---> PE2
         ^
         |
    Chemin préféré
```

Après la panne d'un lien :

```text
PE1 ---> P2 ---> PE2
         ^
         |
    Chemin alternatif
```

Ce dessin illustre le comportement souhaité, mais il ne garantit pas qu'un équipement basculera automatiquement de P1 vers P2. Le résultat dépend de l'état des liens, des routes, des mécanismes de protection et des politiques configurées.

## 13.3. Fast Reroute

Les mécanismes de protection rapide peuvent permettre au routeur de contourner localement une défaillance avant que le calcul global de routage soit entièrement convergé.

Selon la plateforme et le protocole, différentes techniques sont disponibles.

Dans ce challenge, vous devez distinguer :

- Un basculement réalisé par une protection locale préinstallée.
- Un changement de chemin après convergence IGP.
- Une modification de SR Policy.
- Un basculement opéré par un contrôleur ou une logique externe.

La présence de Segment Routing ne signifie pas que toutes les protections sont automatiquement activées.

## 13.4. Mesurer la convergence

Pour chaque test, enregistrez :

- L'heure de début de la panne.
- L'heure de détection.
- Le moment du changement de transfert.
- La perte de paquets observée.
- La durée d'interruption.
- Le chemin après bascule.
- Le retour éventuel au chemin nominal.
- Les alertes reçues.
- Les effets sur les services.

Répétez les mesures lorsque cela est possible, car la convergence peut varier suivant le contexte.

## 13.5. Scénarios à tester

1. Perte d'un lien PE–P.
2. Perte d'un routeur P.
3. Perte d'une adjacence IGP.
4. Perte d'un nœud dont le SID est utilisé.
5. Perte d'une route vers une destination.
6. Retrait d'un segment d'une politique.
7. Indisponibilité d'un équipement de bordure.
8. Défaillance d'un chemin qui transporte des flux à forte priorité.

Pour chaque scénario, décrivez le mécanisme censé assurer la reprise et la preuve permettant de valider le résultat.


# 14. Défi expert — Segment Routing Policy

Une SR Policy permet d'exprimer une intention de chemin en associant un headend, un endpoint, une couleur et une ou plusieurs listes de segments candidates.

L'architecture des SR Policies est détaillée dans la [RFC 9256 — Segment Routing Policy Architecture](https://www.rfc-editor.org/rfc/rfc9256.html).

## 14.1. Pourquoi utiliser une SR Policy ?

Un opérateur peut vouloir appliquer différents chemins au trafic selon son service ou ses objectifs.

Exemples :

- Chemin préféré pour un service à faible latence.
- Chemin différent pour une grande quantité de trafic de sauvegarde.
- Chemin explicitement contrôlé pour une application critique.
- Chemin de secours vers une destination.
- Politique temporaire pendant des travaux.
- Politique de transport correspondant à une intention métier.

Une SR Policy ne garantit pas à elle seule le respect de toutes les propriétés demandées. La latence, la capacité disponible et les contraintes du chemin doivent être évaluées et contrôlées.

## 14.2. Identification d'une politique

Une SR Policy est associée conceptuellement à :

- Un headend.
- Une couleur.
- Un endpoint.

Le headend est le nœud où la politique est instanciée et où les paquets sont aiguillés vers cette politique.

La couleur est une valeur qui représente une intention, par exemple une catégorie de service. Elle ne constitue pas à elle seule une mesure de latence ni une garantie de bande passante.

L'endpoint identifie la destination ou le point logique vers lequel la politique est construite.

## 14.3. Schéma de deux politiques

```text
                         PE1
                          |
                +---------+---------+
                |                   |
                v                   v
           Politique A         Politique B
           Couleur 100         Couleur 200
           Faible latence      Chemin de secours
                |                   |
                v                   v
               P1                  P2
                |                   |
                +---------+---------+
                          |
                          v
                         PE2
```

Le schéma représente deux intentions de chemin. Il ne signifie pas que le choix d'une couleur réserve automatiquement les ressources nécessaires ou que les deux chemins sont nécessairement disjoints.

## 14.4. Exemple de plan de couleurs

Pour le challenge, définissez la convention suivante :

| Couleur | Intention | Objectif |
|---:|---|---|
| 100 | LOW-LATENCY | Privilégier un chemin répondant à un objectif de latence mesuré |
| 200 | HIGH-CAPACITY | Utiliser un chemin dimensionné pour un trafic volumineux |
| 300 | BACKUP | Identifier une politique alternative |
| 400 | MAINTENANCE | Préparer une politique temporaire de maintenance |

Ces valeurs sont des conventions locales de laboratoire. Elles ne possèdent aucune signification universelle dans Segment Routing.

## 14.5. Travail demandé

Pour chaque SR Policy, fournissez :

1. Le headend.
2. L'endpoint.
3. La couleur.
4. Les listes de segments candidates.
5. Les contraintes de chemin.
6. Le critère de sélection du chemin actif.
7. Le comportement en cas d'indisponibilité.
8. Les critères de validation.
9. Les commandes de vérification.
10. La procédure de retour au chemin normal.


# 15. Défi expert — Ingénierie de trafic

## 15.1. Pourquoi l'IGP ne suffit pas toujours

Un IGP sélectionne des chemins selon ses métriques et son calcul de routes.

Ce comportement peut être adapté à de nombreux réseaux. Toutefois, l'opérateur peut souhaiter influencer le chemin d'un flux afin d'atteindre des objectifs qui ne sont pas exprimés par la seule métrique de coût.

Exemples :

- Éviter un lien saturé.
- Utiliser une région spécifique.
- Préserver un chemin pour un service critique.
- Réduire la latence observée entre deux points.
- Séparer les chemins de production et de sauvegarde.
- Appliquer une stratégie de chemin temporaire.

Une politique SR fournit une façon de représenter ces intentions.

## 15.2. Schéma d'une topologie à plusieurs chemins

```text
                         +------ P1 ------+
                        /                  \
                       /                    \
                      /                      \
                    PE1                      PE2
                      \                      /
                       \                    /
                        \                  /
                         +------ P2 ------+

            Chemin A : PE1 -> P1 -> PE2
            Chemin B : PE1 -> P2 -> PE2
```

Dans ce schéma, les deux chemins existent logiquement. Pour les utiliser de manière contrôlée, il faut vérifier les routes, les SIDs, les métriques, la disponibilité des liens et la SR Policy réellement installée.

## 15.3. Mesurer avant d'optimiser

Avant de définir une politique de chemin, collectez :

- La latence de bout en bout.
- La perte de paquets.
- L'utilisation des interfaces.
- Les débits.
- Les métriques IGP.
- Les routes utilisées.
- Les changements de topologie.
- Les erreurs physiques.
- Les contraintes de capacité.
- Les exigences de l'application.

Une mesure ponctuelle ne représente pas toujours le comportement aux heures de pointe.

## 15.4. Une faible latence n'est pas une garantie de bande passante

Un chemin présentant une latence plus faible peut avoir moins de capacité disponible.

Inversement, un chemin disposant d'une capacité élevée peut être plus long.

Le challenge doit donc distinguer :

- Optimisation de latence.
- Gestion de capacité.
- Protection de chemin.
- Contrôle d'admission.
- Qualité de service.
- Répartition de trafic.
- Disponibilité.

Segment Routing permet d'exprimer des instructions de chemin, mais il n'effectue pas automatiquement l'ensemble du contrôle de capacité nécessaire pour garantir une bande passante.

## 15.5. Contrôleur de chemin

Dans une architecture plus avancée, un contrôleur ou un Path Computation Element (PCE) peut contribuer au calcul ou à la distribution de politiques.

BGP-LS peut être utilisé pour transmettre des informations de topologie à un système externe, tandis que PCEP peut participer à certains modèles de calcul et de contrôle de chemins.

Ces mécanismes sont optionnels et dépendent de l'architecture.

Les extensions BGP-LS pour les informations SR sont décrites dans la [RFC 9085](https://www.rfc-editor.org/rfc/rfc9085.html), mise à jour par la [RFC 9356](https://www.rfc-editor.org/rfc/rfc9356.html). La RFC 9256 définit l'architecture des SR Policies.

## 15.6. Exercice de conception

Vous devez proposer :

- Une politique pour le trafic interactif sensible à la latence.
- Une politique pour le trafic de sauvegarde.
- Une politique de secours.
- Une règle de sélection du chemin.
- Les métriques nécessaires.
- Les seuils d'alerte.
- Les conditions de retrait ou de remplacement d'une politique.
- Les tests de validation.

Expliquez quelles fonctions relèvent de Segment Routing et lesquelles relèvent de la supervision, de la QoS, du calcul de chemin ou d'autres mécanismes.


# 16. Défi 10 — BGP et services VPN dans un backbone SR

Segment Routing fournit un moyen de contrôler le transport. Il ne remplace pas automatiquement BGP ou les fonctions de service utilisées dans un backbone opérateur.

## 16.1. Séparation des rôles

Dans une architecture classique :

- L'IGP diffuse les informations nécessaires au transport interne.
- SR ajoute les informations nécessaires aux segments.
- Le plan MPLS effectue le transfert à l'aide de labels.
- BGP peut distribuer les routes des services et des clients.
- Les mécanismes VPN maintiennent la séparation logique des services.
- Les politiques SR peuvent contrôler certains chemins de transport.

Il faut comprendre quel protocole est responsable de chaque information.

## 16.2. Schéma des fonctions

```text
                    +-------------------------+
                    | IGP + EXTENSIONS SR     |
                    | Topologie et SIDs       |
                    +-------------------------+
                                |
                                v
                    +-------------------------+
                    | PLAN DE TRANSPORT       |
                    | IP / MPLS / SR-MPLS     |
                    +-------------------------+
                                |
                                v
                    +-------------------------+
                    | ROUTEURS PE             |
                    | Services et VPN         |
                    +-------------------------+
                                |
                                v
                    +-------------------------+
                    | BGP / ROUTES DE SERVICE |
                    | VPN / Clients           |
                    +-------------------------+
```

Le dessin sépare les rôles conceptuels, mais les interactions effectives dépendent de la plateforme et de la configuration.

## 16.3. Exercice VPN

Supposons que deux clients utilisent chacun une plage IPv4 identique, par exemple `10.10.0.0/16`.

Vous devez expliquer :

1. Pourquoi cette situation ne doit pas être confondue avec le plan d'adressage du backbone.
2. Comment des tables de routage distinctes peuvent isoler ces réseaux.
3. Quel rôle les routeurs PE jouent dans le service.
4. Comment le trafic client est transporté au travers de la fabric.
5. Où les labels de transport et de service peuvent être utilisés.
6. Comment une politique SR peut influencer le transport.
7. Comment vérifier que les deux clients restent isolés.

Le challenge porte sur l'architecture et les rôles. La syntaxe de configuration d'une VPN MPLS varie selon les constructeurs et ne doit pas être inventée à partir d'un exemple générique.


# 17. Défi 11 — SR-MPLS et SRv6

SR-MPLS et SRv6 suivent le même principe général de liste de segments, mais utilisent des plans de données différents.

## 17.1. SR-MPLS

Dans SR-MPLS :

- Les SIDs sont représentés par des labels.
- Les instructions de transport sont transportées dans une pile de labels MPLS.
- Le réseau doit prendre en charge MPLS.
- Les extensions SR de l'IGP diffusent les informations nécessaires.
- Les politiques et mécanismes de contrôle dépendent des fonctions disponibles.

### Schéma

```text
PAQUET SR-MPLS

+--------------------------------------------------+
| En-tête Ethernet                                 |
+--------------------------------------------------+
| Label de transport / Segment actif               |
+--------------------------------------------------+
| Label suivant de la liste                        |
+--------------------------------------------------+
| Paquet IP ou paquet de service                   |
+--------------------------------------------------+
```

La pile peut contenir un ou plusieurs labels de segments, selon la politique choisie et les mécanismes employés.

## 17.2. SRv6

SRv6 applique Segment Routing au plan de données IPv6.

Les segments sont représentés par des identifiants IPv6, et le SRH peut contenir les informations de segments nécessaires au comportement demandé.

La RFC 8754 décrit l'en-tête SRH. La RFC 8986 décrit les comportements SRv6 de programmation réseau.

### Schéma

```text
PAQUET SRv6

+--------------------------------------------------+
| En-tête Ethernet                                 |
+--------------------------------------------------+
| En-tête IPv6 externe                             |
+--------------------------------------------------+
| Segment Routing Header (SRH), si utilisé         |
| Liste de SIDs IPv6                               |
+--------------------------------------------------+
| Paquet interne / trafic transporté              |
+--------------------------------------------------+
```

La taille du paquet, les politiques de filtrage et les contraintes de MTU doivent être évaluées avec les en-têtes utilisés par la plateforme.

## 17.3. Comparaison

| Critère | SR-MPLS | SRv6 |
|---|---|---|
| Plan de données | MPLS | IPv6 |
| Représentation des segments | Labels MPLS | Identifiants IPv6 |
| Dépendance | Support MPLS | Support IPv6 et fonctions SRv6 |
| SIDs | Labels associés à des instructions | SIDs IPv6 associés à des comportements |
| Outils de diagnostic | Tables MPLS, IGP, politique SR | IPv6, SRH, SIDs et politique SR |
| MTU | Dépend de la pile de labels et du chemin | Dépend des en-têtes IPv6/SRH et du chemin |
| Migration | Peut s'intégrer à un domaine MPLS existant | Demande la prise en charge de SRv6 sur le chemin concerné |
| Choix | Selon l'architecture et l'écosystème existant | Selon les objectifs et les capacités de la plateforme |

## 17.4. Critères de décision

Vous devez analyser :

- La prise en charge matérielle.
- La charge opérationnelle.
- Les compétences de l'équipe.
- Les services à transporter.
- La capacité du réseau à gérer les en-têtes.
- Les outils de supervision disponibles.
- Les besoins d'interopérabilité.
- Les contraintes de migration.
- Les gains attendus.
- Le coût de la transition.

Ne migrez pas vers SRv6 uniquement parce qu'il s'agit d'un plan de données différent. La décision doit répondre à un besoin précis.


# 18. Défi 12 — MTU et profondeur de pile

Une politique SR peut ajouter des informations de contrôle dans le paquet.

Dans SR-MPLS, chaque label ajouté augmente la taille du paquet transporté.

Dans SRv6, les en-têtes IPv6 et SRH peuvent augmenter la taille du paquet.

Ces éléments ont des conséquences sur le MTU, la capacité des interfaces et parfois la performance du matériel.

## 18.1. Conséquences possibles

- Fragmentation ou comportement de fragmentation selon le protocole et le chemin.
- Paquets abandonnés si la taille dépasse les limites.
- Échecs de certaines connexions.
- Comportement différent selon les services.
- Surconsommation de bande passante due aux en-têtes.
- Besoin d'adapter les capacités de capture et de supervision.

## 18.2. Exercice de calcul

Pour un chemin SR-MPLS, vous devez déterminer la taille totale du paquet en tenant compte :

- Du paquet initial.
- Du ou des labels ajoutés.
- Des en-têtes Ethernet selon le point de mesure.
- Des éventuels en-têtes supplémentaires.
- Du MTU de chaque lien.

Pour un chemin SRv6, vous devez déterminer la taille totale en tenant compte :

- Du paquet initial.
- De l'en-tête IPv6 externe.
- Du SRH et des SIDs transportés.
- Des éventuelles encapsulations.
- Du MTU des liens.

N'utilisez pas une valeur de MTU par habitude. Documentez la taille calculée, le point de mesure et les hypothèses.

## 18.3. Tests de validation

1. Mesurer le MTU des interfaces.
2. Vérifier les chemins entre chaque paire d'équipements.
3. Vérifier la prise en charge des tailles nécessaires.
4. Observer les compteurs d'abandon.
5. Tester plusieurs tailles de paquets dans un laboratoire.
6. Examiner les messages de contrôle associés à la découverte du MTU.
7. Valider avec la politique SR réellement installée.
8. Répéter les tests sur le chemin de secours.

Une valeur de MTU adaptée au chemin nominal peut ne pas convenir à un chemin de secours différent.


# 19. Défi 13 — Automatisation et validation des politiques SR

Les backbones évoluent. De nouveaux routeurs, préfixes, SIDs et politiques peuvent être ajoutés.

Une modification mal contrôlée peut affecter un grand nombre de services.

## 19.1. Éléments à automatiser

Votre système d'automatisation peut vérifier :

- Les loopbacks.
- Les adresses des liens.
- Les voisinages IGP.
- Les SRGB.
- Les SIDs attendus.
- Les sessions BGP lorsque cela est pertinent.
- Les routes vers les endpoints.
- Les listes de segments.
- Les politiques SR installées.
- Les états des interfaces.
- Les compteurs d'erreurs.
- Les différences entre configuration voulue et configuration réelle.

## 19.2. Cycle de changement

```text
                 BESOIN DE CHANGEMENT
                          |
                          v
                 DONNÉES DE RÉFÉRENCE
                          |
                          v
                VALIDATION DU MODÈLE
                          |
                          v
                GÉNÉRATION DU PLAN
                          |
                          v
               REVUE TECHNIQUE
                          |
                          v
              SAUVEGARDE PRÉALABLE
                          |
                          v
              DÉPLOIEMENT PROGRESSIF
                          |
                          v
             TESTS DE CONNECTIVITÉ
                          |
                          v
             VALIDATION / RETOUR ARRIÈRE
```

## 19.3. Exercice

Construisez un contrôle qui compare :

- Les SIDs attendus.
- Les SIDs observés.
- Les voisinages IGP.
- Les routes installées.
- Les politiques SR.
- L'état des chemins.

Le programme doit détecter les écarts sans modifier automatiquement toute la configuration.

Un écart détecté doit être classé selon son importance : information, avertissement ou incident critique.

## 19.4. Protection contre une erreur de déploiement

Préparez une stratégie de changement qui prévoit :

- Une mise à jour sur un seul routeur de laboratoire.
- Une validation avant propagation.
- Un groupe limité de routeurs lors du déploiement initial.
- Des tests après chaque étape.
- L'interruption du déploiement si une condition n'est pas respectée.
- Un retour arrière clair.
- La conservation des preuves.

N'automatisez pas la modification de chemins de production sans comprendre les dépendances entre IGP, SIDs, politiques SR et services.


# 20. Défi 14 — Supervision du backbone

## 20.1. Éléments à superviser

| Domaine | Mesures et états |
|---|---|
| Interfaces | État, erreurs, drops, débit et saturation |
| IGP | Voisinages, routes et changements de topologie |
| Segment Routing | SIDs, SRGB et informations SR distribuées |
| MPLS | Labels, LFIB et état des opérations de transfert |
| SR Policies | État de la politique, chemin actif et disponibilité des candidats |
| BGP | Sessions, préfixes et changements lorsqu'utilisé |
| Protection | Détection de panne, bascule et convergence |
| MTU | Paramètres, pertes et anomalies |
| Plateforme | Charge, mémoire et capacité de traitement |
| Synchronisation | État et cohérence temporelle |
| Services | Latence, pertes et disponibilité de bout en bout |

La supervision doit distinguer les états du plan de contrôle et les résultats du plan de données.

Un voisinage IGP établi ne garantit pas que chaque paquet est transféré correctement. Inversement, une route présente ne démontre pas que la politique SR attendue est appliquée au flux.

## 20.2. Événements à corréler

Pour un incident de transport, corrélez si possible :

- Les changements d'état d'interface.
- Les événements IGP.
- Les changements de routes.
- Les changements de SIDs.
- Les modifications de politiques SR.
- Les bascules de chemin.
- Les variations de latence.
- Les pertes de paquets.
- Les modifications de configuration.

La synchronisation de l'heure facilite la reconstitution de la chronologie.

## 20.3. Exercice

Créez un tableau de bord présentant :

1. La disponibilité de chaque routeur.
2. L'état des voisinages IGP.
3. L'état des informations SR.
4. Les politiques SR actives.
5. Le débit des liens principaux.
6. Les erreurs de transfert.
7. Les événements de convergence.
8. La latence de plusieurs flux de test.

Définissez ensuite des alertes utiles, en distinguant un état réellement critique d'un changement normal de topologie.


# 21. Scénarios de dépannage

## Scénario A — Les routes IP fonctionnent, mais le trafic SR-MPLS échoue

### Symptôme

Les loopbacks sont joignables, mais un flux qui devrait emprunter un chemin SR échoue.

### Hypothèses

- Informations SR absentes.
- Node-SID incohérent.
- SRGB différent entre équipements.
- Label non installé ou mal interprété.
- Politique SR non active.
- Problème de pile de labels.
- Filtrage ou limitation MPLS.
- Incompatibilité de configuration.

### Démarche

1. Vérifier les routes IP.
2. Vérifier les voisinages IGP.
3. Contrôler les extensions SR annoncées.
4. Comparer les SIDs et le SRGB.
5. Examiner la table de labels et la LFIB.
6. Vérifier la politique SR appliquée au flux.
7. Contrôler le chemin et les compteurs.
8. Vérifier le MTU et les drops.
9. Comparer avec un flux de référence qui fonctionne.

### Preuve attendue

La route de transport et la politique SR doivent être cohérentes, et le transfert réel doit suivre le comportement attendu.


## Scénario B — Le Node-SID mène à un chemin inattendu

### Symptôme

Un paquet arrive à destination, mais emprunte un chemin différent de celui prévu dans le schéma.

### Hypothèses

- Métriques IGP inattendues.
- Chemins à coût égal.
- Node-SID utilisé sans contrainte d'adjacence.
- Changement de topologie.
- Politique SR différente de celle attendue.
- Le flux n'est pas aiguillé vers la politique prévue.

### Démarche

1. Vérifier la topologie IGP.
2. Vérifier les métriques des liens.
3. Examiner le Node-SID annoncé.
4. Vérifier le chemin SPF vers le nœud.
5. Vérifier les chemins à coût égal.
6. Contrôler la politique SR active.
7. Examiner la liste de segments réellement utilisée.
8. Vérifier l'application du mécanisme de sélection de trafic.
9. Corriger la politique si un chemin explicite est nécessaire.

Un Node-SID n'impose pas à lui seul un lien physique unique.


## Scénario C — Le chemin principal fonctionne, mais le secours échoue

### Symptôme

Le réseau transporte le trafic normalement. Lorsqu'un lien tombe, les paquets sont perdus plus longtemps que prévu ou ne reviennent pas.

### Hypothèses

- Aucun mécanisme de protection n'est configuré.
- Chemin alternatif incomplet.
- Adjacency-SID invalide ou indisponible.
- Route absente après convergence.
- Politique de secours inactive.
- Filtrage différent sur le chemin alternatif.
- Ressources insuffisantes.
- Problème de MTU sur le chemin de secours.

### Démarche

1. Identifier le mécanisme de secours prévu.
2. Vérifier qu'il est réellement installé.
3. Simuler la panne dans un environnement autorisé.
4. Mesurer la durée d'interruption.
5. Contrôler le chemin alternatif.
6. Examiner les tables de labels.
7. Contrôler les politiques et les compteurs.
8. Vérifier le service de bout en bout.
9. Restaurer le lien et observer le retour à la normale.

La présence d'un deuxième chemin physique ne garantit pas que la politique de transfert saura l'utiliser correctement.


## Scénario D — Une SR Policy existe, mais le trafic ne l'emprunte pas

### Symptôme

La politique SR est visible sur le routeur, mais les paquets suivent le chemin IGP habituel.

### Hypothèses

- La politique n'est pas active.
- L'endpoint n'est pas résolu.
- La liste de segments est invalide.
- Le trafic n'est pas aiguillé vers la politique.
- Une autre politique a priorité.
- La configuration de steering n'est pas appliquée.
- Une condition de sélection n'est pas satisfaite.

### Démarche

1. Vérifier l'identification de la politique.
2. Vérifier le headend, la couleur et l'endpoint.
3. Examiner les chemins candidats.
4. Confirmer le candidat actif.
5. Vérifier l'endpoint.
6. Vérifier le contenu de la liste de segments.
7. Vérifier la résolution des SIDs.
8. Examiner la règle d'aiguillage du trafic.
9. Capturer ou observer le transfert du flux.
10. Tester avec un flux contrôlé.

Une politique installée n'est pas nécessairement utilisée par le trafic. La présence de la politique et son utilisation sont deux éléments distincts.


## Scénario E — La politique SR fonctionne, mais le débit est insuffisant

### Symptôme

Le trafic emprunte le chemin prévu, mais le débit obtenu est inférieur aux attentes.

### Hypothèses

- Lien saturé.
- QoS.
- Congestion.
- Limitation de capacité.
- Trop grand nombre de paquets avec une profondeur de pile importante.
- Charge CPU du routeur.
- Politiques de files d'attente.
- Problème du service final.
- Mauvaise répartition de flux.

### Démarche

1. Mesurer le débit de référence.
2. Contrôler la capacité de chaque lien.
3. Examiner les drops et les files d'attente.
4. Vérifier l'utilisation de chaque routeur.
5. Observer la distribution réelle du trafic.
6. Contrôler la QoS.
7. Mesurer la latence et les pertes.
8. Comparer le chemin nominal et le chemin alternatif.
9. Modifier une seule variable.
10. Mesurer à nouveau.

Une politique SR ne garantit pas qu'une quantité de bande passante soit réservée. Il faut examiner les fonctions de QoS, de contrôle de capacité et d'admission employées.


## Scénario F — Une route BGP est présente, mais le service VPN est inaccessible

### Symptôme

Le routeur PE connaît la route attendue, mais le service client ne fonctionne pas.

### Hypothèses

- Mauvaise table de routage VPN.
- Problème de forwarding.
- Erreur de label de service.
- Politique SR transportant le mauvais endpoint.
- Route retour absente.
- Mauvaise association de service.
- Interface client indisponible.
- Filtrage ou MTU.

### Démarche

1. Vérifier la route de service.
2. Vérifier le routage du client.
3. Vérifier le chemin de transport.
4. Examiner la pile de labels.
5. Contrôler le PE d'entrée et le PE de sortie.
6. Tester le chemin retour.
7. Vérifier l'état de l'interface client.
8. Examiner les journaux de la plateforme.
9. Comparer avec un autre service fonctionnel.

Ne considérez pas qu'un service VPN fonctionne automatiquement parce que le backbone SR-MPLS est opérationnel.


# 22. Défi final — Incident combiné

Vous êtes ingénieur d'astreinte sur le backbone.

Plusieurs anomalies apparaissent presque simultanément :

1. Un flux entre PE1 et PE2 perd des paquets.
2. Une SR Policy ne semble plus utiliser le chemin attendu.
3. Une session IGP a été réinitialisée.
4. Un lien présente une utilisation élevée.
5. Le chemin alternatif est disponible, mais la convergence est trop lente.
6. Un service VPN devient inaccessible.
7. Les mesures de latence sont incohérentes entre plusieurs sondes.

Vous ne savez pas si tous ces symptômes sont liés.

## 22.1. Règles d'intervention

Vous devez :

- Préserver les journaux et mesures.
- Identifier le périmètre du problème.
- Distinguer le plan de contrôle du plan de données.
- Ne pas modifier plusieurs métriques simultanément.
- Ne pas désactiver SR pour tester une hypothèse sans analyse.
- Ne pas retirer des SIDs utilisés en production.
- Ne pas supprimer les politiques sans sauvegarde.
- Ne pas modifier le MTU sans mesure.
- Documenter chaque changement.
- Vérifier le service de bout en bout après correction.

## 22.2. Tableau de collecte

| Symptôme | Domaine | Première vérification |
|---|---|---|
| Perte de paquets | Plan de données | Interfaces, drops, capacité |
| Chemin inattendu | SR Policy / IGP | Politique active et métriques |
| Voisinage réinitialisé | IGP / physique | Interface, timers et journaux |
| Lien chargé | Capacité | Débit, files et répartition |
| Secours lent | Protection / convergence | Mécanisme de bascule |
| VPN inaccessible | Service / labels | Routes de service et chemin de transport |
| Latence incohérente | Mesures / chemin | Synchronisation, source et destination |

## 22.3. Phase 1 — Collecte des faits

Identifiez :

- Les flux affectés.
- Les routeurs traversés.
- Les politiques SR utilisées.
- Les routes de transport.
- Les SIDs en jeu.
- Les liens saturés.
- Les événements IGP.
- Les changements récents.
- Les événements de service VPN.
- Les résultats de tests indépendants.

Ne supposez pas qu'une hausse d'utilisation de lien est nécessairement la cause initiale de la perte de paquets.

## 22.4. Phase 2 — Construire des hypothèses vérifiables

Exemples :

- Une métrique modifiée a déplacé trop de trafic.
- Une politique SR n'est plus résolue.
- Une panne de lien a supprimé un chemin candidat.
- Un Node-SID mène à un chemin IGP différent de celui prévu.
- Le trafic de service utilise une route de transport invalide.
- La protection locale n'est pas active.
- Les sondes utilisent des chemins ou des horaires différents.

Pour chaque hypothèse, notez la preuve nécessaire et le test qui permet de la confirmer ou de la réfuter.

## 22.5. Phase 3 — Corriger

1. Prioriser la restauration des services critiques.
2. Établir un état de référence.
3. Identifier le composant défaillant.
4. Préparer le changement minimal.
5. Sauvegarder les configurations.
6. Appliquer le changement dans le cadre autorisé.
7. Vérifier les routes et les SIDs.
8. Contrôler le chemin réel.
9. Mesurer les pertes et la latence.
10. Tester la protection.
11. Vérifier les services VPN.
12. Documenter la cause racine.

## 22.6. Rapport post-incident

Le rapport doit contenir :

- La chronologie.
- L'étendue de l'incident.
- Les flux affectés.
- Les hypothèses testées.
- Les preuves.
- La cause racine.
- Les modifications effectuées.
- La durée d'interruption.
- Les mesures avant et après.
- Les risques résiduels.
- Les actions de prévention.

Une cause racine doit être démontrée par des faits observables, et non déduite uniquement de la proximité temporelle entre plusieurs événements.


# 23. Architecture cible complète

Cette architecture représente la cible pédagogique après l'introduction de SR-MPLS.

## 23.1. Schéma global

```text
                       CLIENTS / SITES
                             |
                             v
                       +-----------+
                       | PE1       |
                       | Bordure   |
                       +-----------+
                         |       |
                         |       |
                         v       v
                    +--------+ +--------+
                    | P1     | | P2     |
                    | SR-MPLS| | SR-MPLS|
                    +--------+ +--------+
                         ^       ^
                         |       |
                         |       |
                       +-----------+
                       | PE2       |
                       | Bordure   |
                       +-----------+
                             |
                             v
                       SERVICES VPN
                       ET SITES DISTANTS


                    PLAN DE CONTRÔLE
             +--------------------------------+
             | IGP + extensions SR            |
             | Topologie, préfixes et SIDs    |
             +--------------------------------+
                             |
                             v
                    INFORMATIONS SR
                             |
                             v
                    ROUTEURS DU BACKBONE


                    PLAN DE TRANSPORT
             +--------------------------------+
             | MPLS / Labels / LFIB            |
             | SR Policies si requises         |
             +--------------------------------+
                             |
                             v
                 Flux transportés de bout en bout


                   SUPERVISION / EXPLOITATION
             +--------------------------------+
             | Routes / SIDs / Politiques      |
             | Liens / Pertes / Latence        |
             | Alertes / Changements           |
             +--------------------------------+
```

Le dossier final doit compléter ce schéma avec les adresses, les liens, les loopbacks, les SIDs, les politiques et les chemins de secours.

## 23.2. Décisions d'architecture

| Domaine | Décision de référence |
|---|---|
| Underlay | IP routé avec un IGP |
| IGP | OSPF ou IS-IS avec extensions SR |
| Plan de données de transport | SR-MPLS dans le scénario principal |
| Identification des nœuds | Loopbacks et Node-SIDs documentés |
| SIDs globaux | Plan cohérent avec le SRGB |
| SIDs locaux | Portée et usage documentés |
| Ingénierie de trafic | SR Policies selon le besoin |
| Protection | Mécanismes locaux et convergence vérifiés |
| Services | BGP/VPN conservés lorsqu'ils sont nécessaires |
| Supervision | Contrôle séparé du plan de contrôle et du transfert |
| MTU | Dimensionné selon les piles et les liens |
| Automatisation | Contrôles, déploiement progressif et retour arrière |
| Évolution | SRv6 étudié selon les besoins et capacités |


# 24. Barème d'évaluation sur 100 points

| Domaine | Points |
|---|---:|
| Compréhension de l'architecture backbone | 8 |
| Topologie et plan d'adressage | 8 |
| Routage IGP et convergence | 10 |
| Compréhension MPLS et des labels | 8 |
| Plan de SIDs et SRGB | 10 |
| Activation et vérification SR-MPLS | 10 |
| SR Policies et ingénierie de trafic | 12 |
| Protection et mécanismes de secours | 8 |
| BGP et services VPN | 6 |
| MTU et analyse des performances | 5 |
| Supervision et automatisation | 6 |
| Dépannage et rapport d'incident | 5 |
| Analyse SRv6 et justification d'évolution | 4 |
| **Total** | **100** |

## 24.1. Critères d'excellence

Une solution de qualité doit :

- Présenter un backbone stable.
- Disposer d'un plan IP documenté.
- Définir des SIDs cohérents.
- Expliquer l'interprétation des labels.
- Démontrer le chemin effectivement utilisé.
- Distinguer Node-SID et Adjacency-SID.
- Définir des SR Policies justifiées.
- Tester la protection et la convergence.
- Identifier les limites des mécanismes utilisés.
- Prévoir les tests avant et après changement.
- Documenter les risques et les procédures de retour arrière.

## 24.2. Erreurs graves

Les erreurs suivantes doivent entraîner une pénalité importante :

- Activer SR avant d'avoir stabilisé l'IGP.
- Utiliser un plan de SIDs incohérent.
- Confondre Node-SID et Adjacency-SID.
- Supposer qu'un Node-SID impose un lien physique unique.
- Croire qu'une SR Policy garantit automatiquement la bande passante.
- Déclarer la protection fonctionnelle sans test de panne.
- Confondre route de service et route de transport.
- Ignorer la capacité de transfert des équipements.
- Modifier les métriques sans mesurer les effets.
- Ajouter des segments sans vérifier les limites de MTU.
- Considérer SRv6 comme une simple modification de syntaxe de SR-MPLS.
- Ne pas conserver de preuves.


# 25. Modèle du dossier technique final

## 25.1. Résumé exécutif

Présentez :

- Le besoin initial.
- Les objectifs d'architecture.
- La topologie choisie.
- Le protocole IGP retenu.
- Le plan de SIDs.
- Les mécanismes de protection.
- Les fonctions d'ingénierie de trafic.
- Les résultats des tests.

## 25.2. Architecture physique

Fournissez :

- Le schéma du backbone.
- La liste des routeurs.
- Les liens physiques.
- Les interfaces.
- La capacité des liens.
- Les chemins redondants.
- Les équipements de bordure.

## 25.3. Architecture logique

Fournissez :

- Les loopbacks.
- Les préfixes de liens.
- Les métriques IGP.
- Les SIDs.
- Le SRGB.
- Les routes de service.
- Les SR Policies.
- Les chemins de secours.
- Le plan de contrôle et le plan de données.

## 25.4. Dossier de politique SR

Pour chaque politique, documentez :

| Champ | Description |
|---|---|
| Nom | Identifiant lisible |
| Headend | Routeur où la politique est instanciée |
| Endpoint | Destination de la politique |
| Couleur | Intention locale documentée |
| Liste de segments | Séquence de SIDs attendue |
| Chemin candidat | Chemin et conditions d'utilisation |
| Comportement en panne | Résultat attendu |
| Mesures | Latence, pertes et charge |
| Tests | Vérifications positives et négatives |
| Retour arrière | Procédure de retrait ou restauration |

## 25.5. Tableau de validation

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | Voisinages IGP | Voisinages conformes | À renseigner | À exécuter |
| T02 | Loopbacks | Toutes les loopbacks attendues sont joignables | À renseigner | À exécuter |
| T03 | Informations SR | SIDs et SRGB cohérents | À renseigner | À exécuter |
| T04 | Labels MPLS | Actions de transfert conformes | À renseigner | À exécuter |
| T05 | Trafic SR-MPLS | Chemin conforme au scénario | À renseigner | À exécuter |
| T06 | Politique SR | Politique active et utilisée | À renseigner | À exécuter |
| T07 | Panne d'un lien | Comportement de secours conforme | À renseigner | À exécuter |
| T08 | Panne d'un routeur | Impact et convergence mesurés | À renseigner | À exécuter |
| T09 | Service VPN | Connectivité conforme | À renseigner | À exécuter |
| T10 | MTU | Taille et chemin validés | À renseigner | À exécuter |
| T11 | Supervision | Événements et mesures disponibles | À renseigner | À exécuter |
| T12 | Retour arrière | Procédure vérifiée | À renseigner | À exécuter |

Un résultat ne doit être marqué « OK » que lorsqu'un test a été effectivement exécuté et que sa preuve est disponible.


# 26. Checklist finale

## Architecture

- [ ] Les rôles des routeurs sont documentés.
- [ ] Les liens du backbone sont identifiés.
- [ ] Les adresses des interfaces sont cohérentes.
- [ ] Les loopbacks sont uniques.
- [ ] Les chemins redondants sont documentés.
- [ ] Les capacités des liens sont connues.
- [ ] Les points uniques de panne sont identifiés.

## IGP et MPLS

- [ ] Les voisinages sont établis.
- [ ] Les routes attendues sont présentes.
- [ ] Les métriques sont documentées.
- [ ] Les fonctions MPLS sont comprises.
- [ ] Les éventuelles dépendances LDP ou RSVP-TE sont identifiées.
- [ ] Les services sont distingués du transport.

## Segment Routing

- [ ] Le SRGB est documenté.
- [ ] Le plan de Node-SIDs est cohérent.
- [ ] Les Adjacency-SIDs sont distingués des SIDs globaux.
- [ ] Les informations SR sont annoncées.
- [ ] Les labels sont installés correctement.
- [ ] La pile de labels est vérifiée.
- [ ] Les SR Policies sont justifiées.
- [ ] Les politiques sont réellement utilisées par les flux prévus.

## Résilience

- [ ] Les scénarios de panne sont définis.
- [ ] Les chemins de secours sont disponibles.
- [ ] Les mécanismes de protection sont vérifiés.
- [ ] La convergence est mesurée.
- [ ] Le chemin nominal est restauré correctement.
- [ ] Les services VPN sont testés pendant et après les pannes.

## Exploitation

- [ ] Les commandes de vérification sont documentées.
- [ ] Les journaux sont disponibles.
- [ ] La supervision inclut les plans de contrôle et de données.
- [ ] Les changements sont tracés.
- [ ] Les configurations sont sauvegardées.
- [ ] Les procédures de retour arrière existent.
- [ ] Les résultats des tests sont conservés.
- [ ] La capacité et les limites des équipements sont connues.


# 27. Références techniques

Les références suivantes permettent d'approfondir les architectures et protocoles étudiés.

- [RFC 8402 — Segment Routing Architecture](https://www.rfc-editor.org/rfc/rfc8402.html) : concepts fondamentaux, segments et architecture SR.
- [RFC 8660 — Segment Routing with the MPLS Data Plane](https://www.rfc-editor.org/rfc/rfc8660.html) : représentation de Segment Routing sur le plan de données MPLS.
- [RFC 8665 — OSPF Extensions for Segment Routing](https://www.rfc-editor.org/rfc/rfc8665.html) : extensions SR pour OSPF.
- [RFC 8667 — IS-IS Extensions for Segment Routing](https://www.rfc-editor.org/rfc/rfc8667.html) : extensions SR pour IS-IS.
- [RFC 9256 — Segment Routing Policy Architecture](https://www.rfc-editor.org/rfc/rfc9256.html) : architecture et fonctionnement des SR Policies.
- [RFC 8754 — IPv6 Segment Routing Header (SRH)](https://www.rfc-editor.org/rfc/rfc8754.html) : format du SRH en SRv6.
- [RFC 8986 — Segment Routing over IPv6 (SRv6) Network Programming](https://www.rfc-editor.org/rfc/rfc8986.html) : comportements de programmation réseau SRv6.
- [RFC 9085 — BGP-LS Extensions for Segment Routing](https://www.rfc-editor.org/rfc/rfc9085.html) : extensions BGP-LS relatives à SR, à lire avec les mises à jour applicables, notamment la RFC 9356.
- [RFC 9356 — BGP-LS Extensions for SRv6](https://www.rfc-editor.org/rfc/rfc9356.html) : extensions BGP-LS associées aux informations SRv6.
- Documentation officielle du constructeur : configuration IGP, MPLS, SRGB, SIDs, politiques SR et protection locale.
- Documentation officielle de la plateforme : commandes de diagnostic, tables LFIB, télémétrie, limites de labels et MTU.

Les standards décrivent les mécanismes et les protocoles. La syntaxe des commandes, les capacités de protection, les limites matérielles et certaines fonctions d'ingénierie de trafic varient selon les plateformes et les versions logicielles.


# Conclusion

Ce challenge doit vous permettre de comprendre et de concevoir un backbone dans lequel le routage IP, le transport MPLS, les SIDs, les politiques SR et les mécanismes de protection fonctionnent de manière cohérente.

La réussite repose sur six principes :

1. **Stabiliser l'underlay :** un backbone IP cohérent est indispensable avant l'introduction de Segment Routing.
2. **Maîtriser les SIDs :** leur portée, leur allocation et leur comportement doivent être compris.
3. **Contrôler le chemin :** une politique doit être validée par le transfert réel des paquets.
4. **Préparer les pannes :** la protection et la convergence doivent être testées, pas simplement supposées.
5. **Mesurer avant d'optimiser :** capacité, latence, pertes et MTU doivent être observés.
6. **Automatiser avec prudence :** les changements doivent être contrôlés, traçables et réversibles.

Segment Routing est un outil de conception et de contrôle du transport. Il ne remplace ni l'analyse de capacité, ni la qualité de service, ni la supervision, ni les politiques de sécurité.

**Un backbone bien conçu doit pouvoir expliquer pourquoi un paquet emprunte un chemin donné, démontrer comment il réagit à une panne et permettre à l'équipe d'exploitation de vérifier ces comportements de façon reproductible.**