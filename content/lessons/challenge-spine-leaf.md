# Challenge d'architecture réseau — Spine-Leaf Fabric

> **Fichier :** `challenge-spine-leaf.md`
>
> **Domaine :** architecture réseau de datacenter, fabric leaf-spine, routage L3 et overlays.
>
> **Progression :** Débutant → Intermédiaire → Expert.
>
> **Environnement :** datacenter hébergeant des serveurs physiques, des machines virtuelles, des applications et des services partagés.
>
> **Technologies étudiées :** architecture Clos, leaf-spine, routage IP, OSPF, BGP, ECMP, VLAN, VXLAN, EVPN, VTEP, VNI, VRF, multihoming, MTU, QoS et automatisation.
>
> **Objectif final :** concevoir, configurer, sécuriser et valider une fabric leaf-spine évolutive, capable de répartir le trafic sur plusieurs chemins et de maintenir la connectivité lors des pannes prévues.
>
> **Important :** les adresses, ASN, VLAN et identifiants présentés sont des valeurs de laboratoire. Les configurations réelles dépendent du constructeur, du système réseau, des versions logicielles et des fonctionnalités disponibles.


# 1. Présentation du challenge

## 1.1. Contexte de l'entreprise

Vous êtes ingénieur réseau pour **NovaDC**, une entreprise qui modernise son datacenter afin d'améliorer les performances, la disponibilité et la capacité d'évolution de son infrastructure.

Le datacenter héberge :

- Des serveurs Web.
- Des serveurs applicatifs.
- Des bases de données.
- Des hyperviseurs.
- Des systèmes de stockage.
- Des cibles de sauvegarde.
- Des outils de supervision.
- Des services d'administration.
- Plusieurs environnements de test et de production.

L'architecture actuelle repose sur un modèle hiérarchique traditionnel. Les serveurs sont raccordés à des commutateurs d'accès, qui envoient leur trafic vers des équipements d'agrégation.

Cette architecture commence à présenter plusieurs limites :

- Les chemins ne sont pas tous exploités de façon optimale.
- Certains liens sont saturés alors que d'autres restent peu utilisés.
- L'ajout de serveurs exige des modifications sur plusieurs équipements.
- La convergence après une panne doit être améliorée.
- Les communications entre applications ne sont pas suffisamment documentées.
- Les extensions de couche 2 deviennent difficiles à contrôler.
- Les équipes souhaitent réduire la dépendance à un grand domaine STP.
- Les besoins de virtualisation et de mobilité des charges augmentent.

La direction technique décide d'étudier une architecture **leaf-spine**, également appelée fabric Clos dans de nombreux contextes de datacenter.

Votre mission consiste à concevoir cette infrastructure, à valider les chemins de trafic et à démontrer que les mécanismes de redondance fonctionnent réellement.

## 1.2. Objectifs de la migration

Le projet doit permettre de :

1. Raccorder les serveurs à des leafs.
2. Relier chaque leaf aux spines prévus dans la topologie.
3. Router le trafic dans l'underlay.
4. Exploiter plusieurs chemins de coût égal.
5. Réduire les domaines de panne.
6. Limiter l'utilisation de grands domaines de couche 2.
7. Séparer les réseaux de production, de gestion et de stockage.
8. Contrôler les flux entre applications.
9. Préparer une extension par ajout de leafs.
10. Étudier VXLAN EVPN pour les besoins d'overlay.
11. Prévoir des mécanismes de multihoming adaptés aux serveurs.
12. Automatiser les vérifications et contrôler les changements.

## 1.3. Hypothèses de travail

| Élément | Hypothèse |
|---|---|
| Datacenter | Un site |
| Spines | 2 |
| Leafs initiaux | 4 |
| Raccordement des serveurs | Principalement sur les leafs |
| Underlay | IP routé |
| IGP initial | OSPF |
| ECMP | Activé lorsque la topologie et les métriques le permettent |
| Extension experte | BGP EVPN avec VXLAN |
| Adressage underlay | Bloc privé dédié |
| Réseaux serveurs | VLAN locaux ou segments overlay selon le niveau |
| Environnements | Production et test |
| Stockage | Réseau dédié selon la technologie |
| Administration | Réseau séparé et accès contrôlé |
| Supervision | Mesures et journaux centralisés |
| Redondance | Deux chemins leaf-spine par leaf dans le scénario initial |

Ces valeurs sont destinées à un laboratoire. Un déploiement réel doit tenir compte des capacités des commutateurs, de la bande passante nécessaire, du nombre de ports, du type de serveur et des contraintes d'exploitation.

## 1.4. Trois notions à distinguer

L'architecture repose sur trois domaines techniques différents.

**Underlay :** le réseau IP physique qui assure la connectivité entre les équipements de la fabric.

**Overlay :** le réseau logique éventuellement construit au-dessus de l'underlay, par exemple avec VXLAN.

**Plan de contrôle :** les protocoles et mécanismes qui diffusent les routes et les informations nécessaires au fonctionnement de l'underlay et de l'overlay.

Ces domaines sont liés, mais ils ne doivent pas être confondus.

Un underlay opérationnel ne garantit pas que l'overlay est correctement configuré. Inversement, un EPG ou un segment VXLAN correctement défini ne fonctionnera pas si les VTEP ne peuvent pas communiquer à travers l'underlay.


# 2. Progression des niveaux

## Niveau 1 — Débutant : construire une fabric routée

Vous devez :

- Comprendre le rôle des leafs et des spines.
- Dessiner la topologie physique.
- Créer un plan d'adressage.
- Configurer l'underlay IP.
- Déployer OSPF.
- Vérifier les voisins et les routes.
- Comprendre ECMP.
- Connecter les réseaux de serveurs.
- Tester les chemins et la redondance.
- Documenter les résultats.

**Livrable :** une fabric leaf-spine routée, avec un plan IP et des preuves de connectivité.

## Niveau 2 — Intermédiaire : améliorer la disponibilité et la segmentation

Vous devez :

- Comparer OSPF et BGP pour l'underlay.
- Évaluer le ratio de surallocation.
- Séparer les domaines applicatifs.
- Étudier le multihoming des serveurs.
- Concevoir une politique de filtrage.
- Mesurer les effets de la perte d'un lien.
- Diagnostiquer les problèmes ECMP.
- Vérifier le MTU et les compteurs.
- Préparer un plan d'extension.

**Livrable :** une fabric résiliente accompagnée d'une matrice de flux, d'un plan de capacité et d'un plan de dépannage.

## Niveau 3 — Expert : déployer un overlay évolutif

Vous devez :

- Concevoir un underlay adapté à l'overlay.
- Utiliser BGP EVPN pour distribuer les informations de l'overlay.
- Définir les VTEP.
- Planifier les VNI.
- Séparer plusieurs tenants ou environnements.
- Étudier l'anycast gateway.
- Comparer le multihoming EVPN et les solutions MLAG/vPC.
- Valider les routes EVPN.
- Tester les pannes et le MTU.
- Automatiser les contrôles.
- Définir les procédures de changement et de retour arrière.

**Livrable :** une architecture leaf-spine complète avec underlay, overlay, segmentation, haute disponibilité, supervision et validation.


# 3. Défi 1 — Comprendre l'architecture leaf-spine

## 3.1. Architecture traditionnelle à comparer

Dans une architecture hiérarchique classique, les serveurs sont raccordés à des switches d'accès, qui remontent vers des switches d'agrégation puis éventuellement un cœur de réseau.

```text
                  +------------------+
                  |      CŒUR        |
                  +------------------+
                           |
                  +------------------+
                  |   AGRÉGATION     |
                  +------------------+
                     /            \
                    /              \
                   v                v
             +-----------+    +-----------+
             | ACCÈS A   |    | ACCÈS B   |
             +-----------+    +-----------+
                |   |             |   |
                v   v             v   v
               PC  VM            PC  VM
```

Ce modèle peut convenir à de nombreux environnements. Cependant, le comportement des liens redondants, la segmentation L2 et la distribution des chemins doivent être étudiés.

## 3.2. Architecture leaf-spine

Dans une fabric leaf-spine :

- Les leafs raccordent les serveurs et les équipements de périphérie.
- Les spines assurent le transit entre les leafs.
- Chaque leaf est raccordé à chaque spine prévu dans la fabric.
- Les liens leaf-spine fonctionnent généralement en couche 3 dans un underlay moderne.
- ECMP peut répartir les flux sur plusieurs chemins de coût égal.
- Les spines ne servent normalement pas à raccorder directement les serveurs.
- Les leafs ne servent pas de transit physique vers d'autres leafs dans le modèle classique.

Schéma :

```text
                 +----------------+
                 |    SPINE-01    |
                 +----------------+
                  |    |    |    |
                  |    |    |    |
                  |    |    |    |
                 +----------------+
                 |    SPINE-02    |
                 +----------------+
                  |    |    |    |
                  |    |    |    |
                  |    |    |    |
                  v    v    v    v

              +------+ +------+ +------+ +------+
              | L101 | | L102 | | L201 | | L202 |
              +------+ +------+ +------+ +------+
                 |       |        |        |
                 v       v        v        v
              Serveurs Serveurs  Stockage  Services
              Rack A   Rack B    autorisé  de bordure
```

Le schéma simplifie les traits de liaison. La topologie réelle est un réseau complet de liens leaf-spine : chaque leaf possède un lien vers SPINE-01 et un lien vers SPINE-02.

## 3.3. Topologie détaillée des huit liens

```text
                 +------------------+
                 |     SPINE-01     |
                 +------------------+
                   |   |   |   |
                   |   |   |   |
                   |   |   |   |
                   |   |   |   |
                   |   |   |   |
                   v   v   v   v
                 +----+----+----+----+
                 | L101 L102 L201 L202|
                 +----+----+----+----+
                   ^   ^   ^   ^
                   |   |   |   |
                   |   |   |   |
                   |   |   |   |
                   |   |   |   |
                 +------------------+
                 |     SPINE-02     |
                 +------------------+
```

Chaque leaf est raccordé aux deux spines. Pour vérifier la topologie, ne vous contentez pas de compter les liens : vous devez pouvoir identifier les deux extrémités de chaque lien.

Le plan d'adressage de l'underlay et les interfaces physiques seront documentés dans les sections suivantes.

## 3.4. Pourquoi éviter les liens leaf-leaf dans le modèle initial ?

Dans le modèle classique, le trafic entre deux leafs passe par un spine.

Exemple :

```text
             LEAF-101
             /      \
            /        \
       SPINE-01     SPINE-02
            \        /
             \      /
             LEAF-201
```

Cette règle rend le comportement de transit uniforme et facilite le raisonnement sur les chemins.

Des architectures particulières peuvent inclure d'autres connexions, notamment pour le multihoming ou des besoins de service. Elles doivent être documentées explicitement et ne doivent pas être ajoutées sans analyse.

## 3.5. Avantages de la fabric

- Topologie régulière.
- Chemins multiples entre leafs.
- Possibilité d'utiliser ECMP.
- Ajout de leafs sans reconstruire une hiérarchie complète.
- Réduction de la dépendance aux grands domaines L2.
- Possibilité de construire un overlay VXLAN.
- Modèle de connectivité adapté aux communications est-ouest.
- Capacité à dimensionner la fabric selon le débit et le nombre de ports.

Ces avantages dépendent de la capacité des équipements, de la qualité de la conception et de la configuration.


# 4. Architecture physique de référence

## 4.1. Rôles des équipements

| Équipement | Fonction |
|---|---|
| SPINE-01 | Transit entre les leafs |
| SPINE-02 | Transit redondant entre les leafs |
| LEAF-101 | Raccordement des serveurs de production |
| LEAF-102 | Raccordement des serveurs de production |
| LEAF-201 | Raccordement de services de stockage ou de bordure |
| LEAF-202 | Raccordement redondant de services de stockage ou de bordure |
| Routeur/passerelle de bordure | Connectivité vers WAN, campus ou réseaux externes |
| Serveurs | Hébergement des applications |
| Hyperviseurs | Exécution de machines virtuelles |
| Système de stockage | Hébergement des volumes ou partages |
| Cible de sauvegarde | Protection et récupération des données |

Les fonctions exactes des leafs peuvent varier. Un leaf peut raccorder des serveurs, du stockage ou des connexions externes selon la conception.

## 4.2. Règles physiques

Pour le laboratoire :

1. Tous les leafs doivent être reliés aux deux spines.
2. Les liens leaf-spine utilisent des interfaces IP point à point.
3. Le routage de l'underlay est activé sur ces liens.
4. Les serveurs ne sont pas raccordés directement aux spines.
5. Les liens et interfaces sont documentés.
6. Le réseau de gestion est identifié.
7. Les connexions de stockage sont répertoriées.
8. Les chemins de redondance sont testés.

## 4.3. Raccordement des serveurs

Un serveur simple peut être raccordé à un seul leaf.

```text
       SERVEUR
          |
       NIC-1
          |
       LEAF-101
        /     \
       v       v
   SPINE-01  SPINE-02
```

Cette architecture offre plusieurs chemins dans la fabric à partir du leaf, mais elle ne protège pas contre la panne de LEAF-101 ou du lien unique entre le serveur et LEAF-101.

Pour protéger la connexion du serveur lui-même, un raccordement redondant doit être prévu.

## 4.4. Raccordement redondant d'un serveur

Deux approches peuvent être envisagées :

- Une solution de multichâssis telle qu'un MLAG ou un mécanisme équivalent du constructeur.
- Un mécanisme EVPN multihoming lorsque la plateforme et l'architecture le prennent en charge.

```text
                   SERVEUR
                 NIC-1   NIC-2
                   |       |
                   v       v
                LEAF-101 LEAF-102
                    \     /
                     \   /
                   SPINE LAYER
```

Ce schéma indique la redondance recherchée. Il ne signifie pas que les deux liens peuvent être agrégés librement.

Le mode de raccordement doit être compatible avec les commutateurs, les cartes réseau et le logiciel serveur. Un LACP réparti sur deux leafs exige une solution de multichâssis ou un mécanisme de multihoming adapté.


# 5. Défi 2 — Plan d'adressage de l'underlay

Le réseau underlay transporte les paquets IP entre les interfaces de la fabric et les loopbacks nécessaires.

## 5.1. Plan des loopbacks

Utilisez le bloc `10.255.255.0/24` pour les loopbacks du laboratoire.

| Équipement | Loopback | Rôle |
|---|---|---|
| SPINE-01 | `10.255.255.1/32` | Spine principal |
| SPINE-02 | `10.255.255.2/32` | Spine secondaire |
| LEAF-101 | `10.255.255.11/32` | Leaf de calcul A |
| LEAF-102 | `10.255.255.12/32` | Leaf de calcul B |
| LEAF-201 | `10.255.255.21/32` | Leaf de stockage ou bordure A |
| LEAF-202 | `10.255.255.22/32` | Leaf de stockage ou bordure B |

Les loopbacks servent d'identifiants stables. Elles peuvent être utiles pour la gestion, les sessions de routage ou les extrémités VTEP de l'overlay.

## 5.2. Plan des liens point à point

Utilisez `10.255.0.0/16` pour les liens d'underlay, avec des sous-réseaux `/31` si les équipements les prennent en charge.

| Liaison | Sous-réseau | Adresse spine | Adresse leaf |
|---|---|---|---|
| SPINE-01 ↔ LEAF-101 | `10.255.0.0/31` | `10.255.0.0` | `10.255.0.1` |
| SPINE-02 ↔ LEAF-101 | `10.255.0.2/31` | `10.255.0.2` | `10.255.0.3` |
| SPINE-01 ↔ LEAF-102 | `10.255.0.4/31` | `10.255.0.4` | `10.255.0.5` |
| SPINE-02 ↔ LEAF-102 | `10.255.0.6/31` | `10.255.0.6` | `10.255.0.7` |
| SPINE-01 ↔ LEAF-201 | `10.255.0.8/31` | `10.255.0.8` | `10.255.0.9` |
| SPINE-02 ↔ LEAF-201 | `10.255.0.10/31` | `10.255.0.10` | `10.255.0.11` |
| SPINE-01 ↔ LEAF-202 | `10.255.0.12/31` | `10.255.0.12` | `10.255.0.13` |
| SPINE-02 ↔ LEAF-202 | `10.255.0.14/31` | `10.255.0.14` | `10.255.0.15` |

L'utilisation de `/31` pour des liens point à point est adaptée lorsque les plateformes le prennent en charge et que le plan d'adressage est cohérent.

## 5.3. Tableau des interfaces

Complétez ce tableau avec les interfaces réelles du laboratoire.

| Lien | Interface côté A | Interface côté B | Débit | État attendu |
|---|---|---|---|---|
| SPINE-01 ↔ LEAF-101 | À renseigner | À renseigner | À définir | Actif |
| SPINE-02 ↔ LEAF-101 | À renseigner | À renseigner | À définir | Actif |
| SPINE-01 ↔ LEAF-102 | À renseigner | À renseigner | À définir | Actif |
| SPINE-02 ↔ LEAF-102 | À renseigner | À renseigner | À définir | Actif |
| SPINE-01 ↔ LEAF-201 | À renseigner | À renseigner | À définir | Actif |
| SPINE-02 ↔ LEAF-201 | À renseigner | À renseigner | À définir | Actif |
| SPINE-01 ↔ LEAF-202 | À renseigner | À renseigner | À définir | Actif |
| SPINE-02 ↔ LEAF-202 | À renseigner | À renseigner | À définir | Actif |

## 5.4. Exercice d'adressage

Pour chaque équipement :

1. Configurer la loopback.
2. Configurer les interfaces point à point.
3. Vérifier les masques.
4. Vérifier l'absence d'adresse dupliquée.
5. Vérifier que chaque lien correspond au bon sous-réseau.
6. Tester la connectivité entre voisins directs.
7. Documenter la correspondance entre interface physique et lien logique.

La topologie ne doit pas être considérée comme prête tant que toutes les interfaces ne sont pas identifiées et documentées.


# 6. Architecture 2 — Underlay IP avec OSPF

L'underlay doit fournir une connectivité IP entre les équipements de la fabric.

Dans le niveau débutant, nous utilisons OSPF afin de nous concentrer sur le modèle leaf-spine et le fonctionnement de la convergence.

## 6.1. Principe

Dans la topologie de référence :

- Tous les liens leaf-spine sont des interfaces L3.
- Chaque interface appartient au domaine de routage underlay.
- Les loopbacks sont annoncées par l'IGP.
- Les métriques des liens sont cohérentes.
- Les chemins de coût égal peuvent être installés lorsque le calcul et la plateforme le permettent.

## 6.2. Schéma du plan de contrôle

```text
                  OSPF UNDERLAY
             +-----------------------+
             | Loopbacks             |
             | Préfixes de liens     |
             | Coûts de chemins      |
             +-----------------------+
                       |
          +------------+-------------+
          |            |             |
          v            v             v
       SPINE-01     SPINE-02      LEAFS
          |            |             |
          +------------+-------------+
                       |
                Table de routage IP
                       |
                Transfert des paquets
```

Le plan de contrôle détermine les routes disponibles. Le plan de données utilise les résultats de routage pour transmettre les paquets.

## 6.3. Choix de conception

Pour le laboratoire :

- Une seule aire OSPF suffit.
- Les loopbacks doivent être annoncées.
- Les liens leaf-spine doivent être configurés en L3.
- Les interfaces de liens ne doivent pas être transformées en trunks L2 sans justification.
- La métrique des chemins doit être cohérente pour étudier ECMP.
- Les interfaces qui ne doivent pas former de voisinages ne doivent pas être activées inutilement dans l'IGP.

Ces choix simplifient le laboratoire. Une architecture réelle peut utiliser une autre organisation OSPF ou un autre IGP.

## 6.4. Configuration conceptuelle

La syntaxe dépend du système réseau. Les éléments suivants indiquent les objets à configurer, et non une configuration universelle prête à copier :

```text
Processus OSPF
  Router ID unique
  Loopback annoncée
  Interfaces leaf-spine actives dans l'IGP
  Métriques documentées
  Voisinages attendus
  Réseau de gestion traité selon la politique
```

Sur un système Cisco IOS ou IOS XE, des commandes de vérification peuvent inclure :

```text
show ip interface brief
show ip ospf neighbor
show ip route
show ip ospf interface
show logging
```

Sur d'autres plateformes, utilisez les commandes équivalentes.

## 6.5. Contrôles obligatoires

Avant de passer à ECMP :

- Chaque lien physique est actif.
- Chaque voisin OSPF attendu est établi.
- Les loopbacks sont présentes dans les tables de routage.
- Les routes vers les loopbacks sont cohérentes.
- Les métriques des chemins sont connues.
- La convergence après perte de lien est observée.
- Les journaux ne montrent pas de réinitialisations répétées.


# 7. Défi 3 — Comprendre ECMP

ECMP signifie **Equal-Cost Multi-Path**.

Lorsque plusieurs chemins vers une destination possèdent un coût égal selon le mécanisme de routage et les politiques applicables, le routeur peut installer plusieurs prochains sauts.

Le trafic peut alors être réparti sur différents chemins.

## 7.1. Exemple de chemins parallèles

```text
                  LEAF-101
                   /    \
                  /      \
                 v        v
            SPINE-01    SPINE-02
                 \        /
                  \      /
                   v    v
                  LEAF-201
```

Dans cette topologie, le trafic entre LEAF-101 et LEAF-201 peut utiliser deux chemins via les deux spines.

Le mécanisme de répartition dépend de la plateforme, de l'algorithme de hachage et des informations disponibles dans le paquet.

## 7.2. ECMP ne signifie pas répartition parfaite

De nombreux systèmes utilisent un hachage de flux pour déterminer le chemin.

Les champs pouvant intervenir dépendent de l'implémentation, par exemple :

- Adresse IP source.
- Adresse IP destination.
- Protocole.
- Ports source et destination.
- Autres champs disponibles.

Il ne faut pas supposer que chaque paquet individuel sera réparti à parts égales entre les chemins.

Un hachage par flux permet généralement de conserver l'ordre des paquets d'une même conversation, mais certains flux volumineux peuvent concentrer une part importante du trafic sur un chemin.

## 7.3. Exercice ECMP

1. Relevez les routes vers les loopbacks distantes.
2. Vérifiez les prochains sauts installés.
3. Générez plusieurs flux de test.
4. Observez les compteurs des liens leaf-spine.
5. Vérifiez si plusieurs chemins sont utilisés.
6. Mesurez la répartition du trafic.
7. Comparez les résultats lorsque les champs des flux sont différents.
8. Déconnectez un lien dans un environnement de test.
9. Vérifiez la route restante.
10. Mesurez la perte et le temps de reprise.

## 7.4. Questions de validation

- Les deux chemins ont-ils réellement le même coût ?
- La plateforme permet-elle le nombre de chemins attendu ?
- La table de routage installe-t-elle plusieurs prochains sauts ?
- Le trafic suit-il les chemins attendus ?
- Le hachage est-il suffisamment diversifié ?
- Une panne provoque-t-elle une reconvergence ?
- Les flux existants sont-ils interrompus ou simplement redistribués ?


# 8. Défi 4 — Dimensionner une fabric spine-leaf

La qualité d'une fabric dépend de la capacité des équipements, du nombre de liens et du volume de trafic.

Le nombre de leafs et de spines ne suffit pas pour déterminer si la fabric répond aux besoins.

## 8.1. Mesurer la surallocation

La surallocation, ou oversubscription, compare la capacité agrégée des ports descendants et celle des liens montants.

Exemple pédagogique :

- 32 ports serveurs à 25 Gbit/s.
- 4 uplinks à 100 Gbit/s vers les spines.
- 2 uplinks vers chaque spine.

Capacité théorique des ports serveurs :

```text
32 × 25 Gbit/s = 800 Gbit/s
```

Capacité théorique des uplinks :

```text
4 × 100 Gbit/s = 400 Gbit/s
```

Rapport de surallocation :

```text
800 / 400 = 2
```

Le rapport théorique est donc de **2:1** dans cette direction de calcul.

Cette valeur ne mesure pas à elle seule les performances réellement observées. Il faut considérer la direction du trafic, la répartition, les capacités des équipements et les charges réelles.

## 8.2. Schéma de capacité d'un leaf

```text
             SERVEURS CONNECTÉS
             32 ports à 25 Gbit/s
                    |
                    v
             +-------------+
             | LEAF        |
             +-------------+
               |  |  |  |
               |  |  |  |
             4 uplinks à 100 Gbit/s
               |  |  |  |
          +----+  |  |  +----+
          |       |  |       |
          v       v  v       v
       SPINE-01  Liens   Liens  SPINE-02
```

Les valeurs représentent un exemple de dimensionnement, pas une configuration obligatoire. Vérifiez le nombre réel de ports disponibles, les limites d'interface et les capacités de la plateforme.

## 8.3. Questions de capacité

Pour chaque leaf, déterminez :

1. Le nombre de ports serveurs.
2. Le débit de chaque port.
3. Le nombre d'uplinks.
4. Le débit des uplinks.
5. Le ratio de surallocation.
6. Le volume est-ouest prévu.
7. Le trafic de sauvegarde.
8. Le trafic de stockage.
9. La perte de capacité en cas de panne.
10. Le besoin de croissance.

## 8.4. Dimensionnement après panne

Une fabric peut répondre aux besoins en fonctionnement normal tout en étant saturée lorsqu'un lien ou une spine tombe en panne.

Évaluez le scénario suivant :

- Deux spines sont opérationnels.
- Un leaf répartit son trafic sur les deux spines.
- Un spine devient indisponible.
- Tout le trafic continue via l'autre spine.

Vous devez calculer la capacité restante et comparer celle-ci au trafic attendu.

Un plan de redondance n'est utile que si le réseau conserve une capacité suffisante ou si les conséquences d'une dégradation sont acceptables.


# 9. Défi 5 — Limiter les domaines de panne

## 9.1. Underlay en couche 3

Dans une fabric moderne, les liens entre leafs et spines sont généralement routés.

Cette approche réduit la dépendance à un grand domaine L2 et permet au routage de gérer les chemins de transit.

Cela ne signifie pas que STP disparaît nécessairement de l'infrastructure : des domaines L2 locaux peuvent subsister sur les connexions des serveurs et dans les zones d'accès.

La conception doit distinguer :

- Les liens L3 du backbone interne.
- Les VLAN de raccordement des serveurs.
- Les domaines L2 locaux nécessaires.
- Les overlays L2 éventuels.

## 9.2. Architecture L3 routée

```text
             +-------------+       +-------------+
             | SPINE-01    |       | SPINE-02    |
             +-------------+       +-------------+
                |  L3  |              |  L3  |
                |      |              |      |
                v      v              v      v
             +-------------+       +-------------+
             | LEAF-101    |       | LEAF-201    |
             +-------------+       +-------------+
                 |                      |
            VLAN locaux             VLAN locaux
                 |                      |
              Serveurs               Serveurs
```

Les liens leaf-spine appartiennent à l'underlay IP.

Les VLAN présents sur les ports serveurs ne sont pas automatiquement étendus sur les liens leaf-spine. Si un réseau L2 doit être étendu entre plusieurs leafs, cela doit être traité par un mécanisme adapté, par exemple un overlay VXLAN dans la conception experte.

## 9.3. Exercice STP et L2

Dans le laboratoire, comparez :

1. Une architecture où de grands domaines L2 sont étendus à travers la fabric.
2. Une architecture où l'underlay est routé et les domaines L2 sont limités aux leafs.
3. Une architecture avec VXLAN pour étendre certains segments.

Expliquez les différences en matière de :

- Boucles.
- Domaines de diffusion.
- Convergence.
- Mobilité des VM.
- Extension des réseaux.
- Dépannage.
- Limites de la plateforme.


# 10. Niveau intermédiaire — Comparer OSPF et BGP pour l'underlay

Le routage OSPF est utilisé dans le laboratoire de départ, mais les architectures leaf-spine peuvent également utiliser BGP pour le routage de l'underlay.

Les designs basés sur eBGP sont notamment décrits dans la [RFC 7938 — Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938.html).

## 10.1. Option A : OSPF underlay

Caractéristiques :

- Un domaine IGP.
- Des loopbacks annoncées.
- Des liens point à point.
- Des métriques déterminant les chemins.
- ECMP lorsque les coûts et la plateforme le permettent.

Avantages possibles :

- Mise en place familière pour une équipe OSPF.
- Calcul de routes automatique.
- Diagnostic fondé sur les métriques et les voisinages.
- Adapté à une topologie de laboratoire.

Points à surveiller :

- Cohérence des aires.
- Choix des métriques.
- Contrôle de la portée des annonces.
- Stabilité de l'IGP.
- Comportement de convergence.

## 10.2. Option B : BGP underlay

Une architecture peut utiliser eBGP entre chaque leaf et chaque spine.

Caractéristiques possibles :

- Liens L3 point à point.
- ASN définis par équipement.
- Annonce des routes nécessaires.
- Filtrage des préfixes.
- ECMP lorsque les chemins sont considérés comme équivalents par le système et que les politiques le permettent.

Avantages possibles :

- Politique explicite d'annonce de routes.
- Isolation des voisins.
- Modèle de routage adapté à une topologie Clos.
- Possibilité de contrôler précisément les préfixes échangés.

Points à surveiller :

- Politique BGP.
- ASNs et sessions.
- Attributs influençant la sélection.
- Multipath selon la plateforme.
- Filtres de préfixes.
- Retrait des routes en cas de panne.

## 10.3. Tableau comparatif

| Critère | OSPF underlay | BGP underlay |
|---|---|---|
| Modèle de routage | IGP à état de liens | Routage par politique |
| Informations diffusées | Topologie et préfixes selon la configuration | Routes et attributs BGP |
| Convergence | Dépend du calcul SPF et des mécanismes associés | Dépend des sessions, des politiques et des mécanismes BGP |
| ECMP | Possible si les coûts sont équivalents et la plateforme le permet | Possible si les chemins sont éligibles et la plateforme le permet |
| Contrôle des annonces | Filtres et politique IGP selon le système | Politique BGP explicite |
| Exploitation | Adaptée aux équipes maîtrisant un IGP | Adaptée aux équipes maîtrisant BGP et ses politiques |
| Évolution | Selon l'organisation du domaine | Selon la politique de sessions et de préfixes |

## 10.4. Exercice

Concevez deux plans :

- Une fabric avec OSPF underlay.
- Une fabric avec eBGP underlay.

Pour les deux variantes, fournissez :

1. Le plan IP.
2. Les identifiants des équipements.
3. Le plan d'annonces.
4. Les critères d'ECMP.
5. La politique en cas de panne.
6. Les commandes de vérification.
7. Les risques de configuration.
8. Le retour arrière.

Vous devez choisir une seule variante pour le laboratoire principal. La deuxième variante est un exercice de conception, pas une raison de faire tourner plusieurs protocoles sans besoin.


# 11. Architecture 3 — Segmentation des réseaux de serveurs

Le plan de segmentation dépend de l'environnement.

Dans le niveau débutant, des VLAN locaux peuvent suffire pour séparer les serveurs. Dans le niveau expert, VXLAN EVPN peut fournir des segments logiques au-dessus de l'underlay L3.

## 11.1. Plan de VLAN de référence

| VLAN | Nom | Usage | Sous-réseau |
|---:|---|---|---|
| 110 | WEB | Frontends Web | `10.110.10.0/24` |
| 120 | APP | Applications métier | `10.110.20.0/24` |
| 130 | DB | Bases de données | `10.110.30.0/24` |
| 140 | MGMT | Gestion des serveurs | `10.110.40.0/24` |
| 150 | BACKUP | Sauvegarde | `10.110.50.0/24` |
| 160 | STORAGE | Stockage dédié | `10.110.60.0/24` |
| 170 | MONITORING | Supervision | `10.110.70.0/24` |
| 999 | PARKING | Ports inutilisés | Sans usage utilisateur |

Le plan IP doit être documenté et vérifié pour éviter les chevauchements. Les passerelles sont placées selon l'architecture retenue : SVI sur les leafs, passerelles distribuées ou autre mécanisme supporté.

## 11.2. Architecture à segmentation locale

```text
                   UNDERLAY L3
                       |
                +--------------+
                | LEAF-101     |
                +--------------+
                  |   |   |   |
                  |   |   |   |
                  v   v   v   v
                WEB  APP  DB  MGMT
               VLAN 110 120 130 140
```

Dans cette variante, les VLAN sont locaux au leaf et la connectivité inter-réseaux est fournie par le mécanisme de routage retenu.

Cette approche peut être adaptée lorsque les besoins de mobilité et d'extension L2 restent limités.

## 11.3. Architecture multi-leaf

Si des serveurs du même réseau doivent se trouver sur plusieurs leafs, vous devez déterminer comment ce réseau sera étendu.

Options possibles :

- Limiter le domaine L2 à un leaf lorsque l'application le permet.
- Concevoir un routage L3 jusqu'aux serveurs.
- Utiliser un overlay VXLAN EVPN si l'extension du segment L2 est réellement nécessaire.

Ne considérez pas que tous les serveurs d'un même rôle doivent nécessairement appartenir au même domaine L2.

## 11.4. Matrice de flux applicative

| Source | Destination | Politique de référence |
|---|---|---|
| WEB | APP | Autoriser les ports nécessaires |
| WEB | DB | Refuser par défaut |
| APP | DB | Autoriser les ports nécessaires |
| APP | WEB | Refuser par défaut pour les nouvelles connexions initiées, sauf besoin |
| Utilisateurs | MGMT | Refuser |
| Admin autorisé | MGMT | Autoriser selon les rôles |
| Serveurs | BACKUP | Autoriser les flux requis |
| Utilisateurs | STORAGE | Refuser par défaut |
| MONITORING | Serveurs | Autoriser les protocoles de collecte prévus |
| Réseau non autorisé | DB | Refuser |

Cette matrice constitue un point de départ. Les règles finales doivent identifier les sources, destinations, protocoles, ports et points de filtrage.


# 12. Défi 6 — Multihoming des serveurs

Un serveur raccordé à un seul leaf dépend du port, du câble et du leaf pour sa connectivité.

Si la disponibilité exige qu'un serveur reste accessible après la panne d'un leaf, il faut étudier le multihoming.

## 12.1. Solution A — Serveur connecté à un seul leaf

```text
          SERVEUR
             |
             v
          LEAF-101
          /     \
         v       v
     SPINE-01  SPINE-02
```

Avantages :

- Simplicité.
- Pas de coordination de multichâssis côté serveur.
- Dépannage relativement direct.

Limites :

- Pas de protection contre la panne du leaf.
- Pas de protection contre la panne du lien serveur-leaf.
- Une intervention sur le leaf peut affecter les serveurs qui y sont raccordés.

## 12.2. Solution B — Multihoming via MLAG ou vPC

Des mécanismes de multichâssis permettent, selon le constructeur et la plateforme, de présenter plusieurs leafs comme un domaine de raccordement coordonné pour certains liens.

```text
                  SERVEUR
                NIC-1   NIC-2
                  |       |
                  v       v
               LEAF-101 LEAF-102
                  \       /
                   \     /
                 Mécanisme MLAG
                 / vPC équivalent
```

Le dessin représente l'intention. Le mécanisme exact, les liens de peer, la cohérence des états et les scénarios de split-brain dépendent de la plateforme.

Un LACP standard entre un serveur et deux commutateurs indépendants ne fonctionne pas automatiquement comme un seul agrégat logique. La prise en charge de multichâssis doit être explicite.

## 12.3. Solution C — EVPN multihoming

Dans certains designs EVPN, un Ethernet Segment peut être raccordé à plusieurs équipements participant au multihoming EVPN.

La procédure dépend de l'architecture et de la plateforme. Le multihoming EVPN n'est pas simplement une autre façon d'écrire MLAG : le plan de contrôle et les mécanismes de convergence diffèrent.

## 12.4. Comparaison

| Critère | Connexion simple | MLAG/vPC | EVPN multihoming |
|---|---|---|---|
| Complexité | Faible | Moyenne à élevée | Élevée |
| Protection contre la panne d'un lien | Non si lien unique | Oui si correctement configuré | Oui selon la conception |
| Protection contre la panne d'un leaf | Non | Possible selon le mécanisme | Possible selon le mécanisme |
| Dépendances | Port et leaf | Pair de commutateurs et mécanisme de coordination | Plan de contrôle EVPN et Ethernet Segment |
| Exploitation | Simple | Dépendante du constructeur | Dépendante de la plateforme et du modèle EVPN |

## 12.5. Exercices de panne

Dans un environnement de test autorisé :

1. Perdez un lien serveur-leaf.
2. Vérifiez la connectivité.
3. Perdez le second lien si la topologie le prévoit.
4. Simulez la perte d'un leaf.
5. Mesurez l'interruption.
6. Vérifiez les états du mécanisme de multihoming.
7. Contrôlez les journaux.
8. Vérifiez qu'aucune boucle ou duplication de trafic n'apparaît.
9. Rétablissez les liens.
10. Documentez le retour à l'état nominal.


# 13. Niveau expert — VXLAN EVPN

Cette section introduit un overlay au-dessus de l'underlay.

VXLAN est un mécanisme d'encapsulation qui transporte des trames Ethernet dans des paquets UDP/IP. La RFC 7348 en décrit le fonctionnement. EVPN peut fournir un plan de contrôle BGP pour l'échange des informations nécessaires à un overlay VXLAN. La RFC 8365 décrit cette utilisation d'EVPN pour la virtualisation de réseau.

## 13.1. Pourquoi utiliser un overlay ?

Un overlay peut être utile lorsque :

- Les réseaux logiques doivent exister sur plusieurs leafs.
- Les machines virtuelles peuvent migrer entre des emplacements.
- Plusieurs tenants doivent partager la même infrastructure physique.
- Les domaines L2 doivent être étendus de manière contrôlée.
- Des segments de couche 2 et de couche 3 doivent être représentés indépendamment de la topologie physique.

Un overlay n'est pas indispensable dans tous les datacenters. Un routage L3 jusqu'aux serveurs peut être plus simple lorsque les applications n'ont pas besoin d'extension L2.

## 13.2. Underlay et overlay

```text
               OVERLAY LOGIQUE
        +--------------------------------+
        | VNI 10110 : WEB                |
        | VNI 10120 : APP                |
        | VNI 10130 : DB                 |
        +--------------------------------+
                  |              |
                  v              v
              +-------+      +-------+
              |VTEP   |      |VTEP   |
              |LEAF101|      |LEAF201|
              +-------+      +-------+
                  |              |
                  +------+-------+
                         |
                 UNDERLAY IP ROUTÉ
                         |
                  +--------------+
                  | LEAF-SPINE   |
                  | ECMP         |
                  +--------------+
```

Les VTEP sont les points qui encapsulent et décapsulent le trafic VXLAN.

L'underlay doit permettre à chaque VTEP de joindre les autres VTEP concernés par l'overlay.

Le VNI identifie le segment VXLAN transporté. Il ne faut pas confondre VNI et VLAN : un VNI est un identifiant de segment VXLAN, tandis qu'un VLAN est un identifiant de domaine de couche 2 dans le contexte Ethernet correspondant.

## 13.3. Plan de VNI de référence

| Segment | VLAN local illustratif | VNI illustrative |
|---|---:|---:|
| WEB | 110 | 10110 |
| APP | 120 | 10120 |
| DB | 130 | 10130 |
| MGMT | 140 | 10140 |
| BACKUP | 150 | 10150 |
| STORAGE | 160 | 10160 |

Ces valeurs sont des choix de laboratoire. Dans une plateforme réelle, il faut vérifier le plan d'allocation des VNI, les capacités et le modèle de segmentation du produit.

Les réseaux de stockage et de gestion ne doivent pas être ajoutés à un overlay sans vérifier que cela convient aux exigences et à la technologie employée.

## 13.4. VTEP et loopbacks

Les loopbacks des leafs peuvent servir d'adresses VTEP.

Exemple :

| Leaf | Loopback VTEP illustrative |
|---|---|
| LEAF-101 | `10.255.255.11/32` |
| LEAF-102 | `10.255.255.12/32` |
| LEAF-201 | `10.255.255.21/32` |
| LEAF-202 | `10.255.255.22/32` |

Dans ce laboratoire, ces adresses correspondent aux loopbacks prévues pour les leafs. L'underlay doit les annoncer et permettre leur joignabilité.

## 13.5. Trafic VXLAN entre deux leafs

Supposons que deux VMs du même segment logique se trouvent sur des leafs différents.

```text
          VM-A                               VM-B
           |                                  |
           v                                  v
      +----------+                       +----------+
      | LEAF-101 |                       | LEAF-201 |
      | VTEP-A   |                       | VTEP-B   |
      +----------+                       +----------+
           |                                  ^
           |                                  |
           v                                  |
        SPINE-01 / SPINE-02 ------------------+
           |
           v
        Underlay IP
```

Le schéma représente une communication entre VTEP. Les paquets VXLAN traversent le réseau IP physique, puis sont décapsulés au VTEP de destination.

Le chemin réel dépend d'ECMP, des routes VTEP, du hachage, de la disponibilité des liens et des informations de contrôle EVPN.

## 13.6. MTU de l'overlay

VXLAN ajoute des en-têtes au paquet transporté. Le réseau underlay doit donc pouvoir transporter des paquets suffisamment grands.

Vous devez vérifier :

- Le MTU des interfaces des serveurs.
- Le MTU des ports d'accès.
- Le MTU des uplinks leaf-spine.
- Le MTU des interfaces VTEP.
- Les contraintes de l'hyperviseur.
- Les éventuels tunnels supplémentaires.
- Les chemins de secours.

Ne supposez pas que la taille maximale des paquets d'une configuration Ethernet standard est suffisante pour transporter toutes les trames encapsulées sans problème.

Le calcul doit tenir compte du paquet interne, de l'en-tête Ethernet interne éventuel et de l'encapsulation externe utilisée.


# 14. Défi expert — BGP EVPN

EVPN peut être utilisé comme plan de contrôle de l'overlay.

Dans un design courant, les leafs qui hébergent les VTEP échangent les informations nécessaires à la connectivité des endpoints par BGP EVPN.

## 14.1. Architecture conceptuelle

```text
                   PLAN DE CONTRÔLE EVPN
             +------------------------------+
             | Informations MAC/IP          |
             | Découverte des VTEP          |
             | Routes EVPN                  |
             | Multihoming selon le design  |
             +------------------------------+
                           |
                  Sessions BGP EVPN
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
          LEAF-101      LEAF-102      LEAF-201


                   PLAN DE DONNÉES VXLAN
             +------------------------------+
             | Encapsulation / Décapsulation|
             | VNI                          |
             | Routage et transfert          |
             +------------------------------+
```

Le plan de contrôle distribue les informations nécessaires à l'overlay. Le plan de données encapsule, transporte et décapsule les paquets.

Une session BGP EVPN établie ne garantit pas que les endpoints sont correctement associés à leurs réseaux logiques ou que les règles de sécurité sont complètes.

## 14.2. Rôle des spines en tant que route reflectors

Dans un design courant, les spines peuvent fonctionner comme route reflectors BGP EVPN afin d'éviter une full-mesh de sessions iBGP entre tous les leafs.

Cette organisation doit être compatible avec la plateforme et le modèle BGP retenu.

Les route reflectors distribuent les routes selon les règles BGP applicables. Ils ne deviennent pas automatiquement des points de transit de données entre les VTEP.

Schéma :

```text
                 +------------------+
                 | SPINE-01         |
                 | BGP RR            |
                 +------------------+
                    ^    ^    ^
                    |    |    |
                    |    |    |
                 +------------------+
                 | SPINE-02         |
                 | BGP RR            |
                 +------------------+
                    ^    ^    ^
                    |    |    |
                    |    |    |
              +---------+---------+---------+
              |         |         |         |
              v         v         v         v
           LEAF-101  LEAF-102  LEAF-201  LEAF-202
```

Ce schéma simplifie les sessions de contrôle. Dans un déploiement réel, les paramètres BGP, la redondance des route reflectors et les politiques doivent être documentés précisément.

## 14.3. Types de routes EVPN à connaître

Dans le cadre du challenge, il est utile de comprendre les rôles des principales catégories de routes EVPN.

| Type EVPN | Rôle général |
|---|---|
| Type 1 — Ethernet A-D | Découverte et signalisation associées aux Ethernet Segments et aux EVI |
| Type 2 — MAC/IP Advertisement | Annonce d'informations MAC et éventuellement IP |
| Type 3 — Inclusive Multicast Ethernet Tag | Signalisation utilisée notamment pour la réplication BUM selon l'architecture |
| Type 4 — Ethernet Segment | Informations liées aux Ethernet Segments et au multihoming |
| Type 5 — IP Prefix | Annonce de préfixes IP dans les architectures EVPN qui utilisent cette fonction |

Les usages exacts et les traitements dépendent du service EVPN et du modèle de déploiement.

L'overlay ne doit pas être considéré comme un simple mécanisme de diffusion des adresses MAC. Le plan de contrôle permet notamment de gérer la découverte, la portée des informations et certains mécanismes de multihoming.

## 14.4. Exercice EVPN

Vous devez démontrer :

1. La connectivité underlay entre VTEP.
2. L'état des sessions BGP EVPN.
3. La présence des VNI nécessaires.
4. L'apprentissage des endpoints.
5. La distribution des informations d'endpoint.
6. La connectivité L2 sur le segment attendu.
7. La connectivité L3 entre réseaux autorisés.
8. L'absence de communication entre segments interdits.
9. La convergence lors de la perte d'un chemin.
10. La cohérence du MTU.


# 15. Défi 10 — Multitenancy avec VXLAN EVPN

Le multi-tenant permet de partager une infrastructure physique tout en maintenant des domaines logiques séparés.

Dans un overlay VXLAN EVPN, les VNIs peuvent séparer les segments L2 et les contextes L3 de façon adaptée à l'architecture.

## 15.1. Plan de tenants

Le scénario utilise trois environnements :

- Tenant Alpha.
- Tenant Beta.
- Services communs.

Chaque tenant possède des segments séparés.

| Tenant | Réseau | Fonction | VNI illustrative |
|---|---|---|---:|
| Alpha | WEB | Frontend | 10110 |
| Alpha | APP | Application | 10120 |
| Alpha | DB | Base de données | 10130 |
| Beta | WEB | Frontend | 10210 |
| Beta | APP | Application | 10220 |
| Beta | DB | Base de données | 10230 |
| Common | DNS | Service partagé | 10010 |
| Common | Monitoring | Supervision | 10030 |

Les VNIs doivent être uniques ou organisés selon les règles de l'architecture et de la plateforme. Les valeurs du tableau sont des exemples pédagogiques.

## 15.2. Architecture logique

```text
                  UNDERLAY LEAF-SPINE
                           |
                +----------+----------+
                |                     |
                v                     v
          +-----------+         +-----------+
          | LEAF-101  |         | LEAF-201  |
          +-----------+         +-----------+
                |                     |
        +-------+------+       +------+-------+
        |              |       |              |
        v              v       v              v
    TENANT A        TENANT B  TENANT A      TENANT B
    VNI 10110       VNI 10210 VNI 10120     VNI 10220
```

Le schéma illustre les segments des tenants sur plusieurs leafs. Dans une architecture réelle, les objets de routage, VNIs L2/L3 et politiques doivent être définis conformément au modèle EVPN utilisé.

## 15.3. Principes d'isolation

- Alpha ne doit pas communiquer avec Beta sans autorisation.
- Les services communs doivent être accessibles uniquement aux tenants prévus.
- Les réseaux de production et de test doivent être séparés.
- Les interfaces de gestion doivent être protégées.
- Les routes doivent être limitées aux préfixes nécessaires.
- Le partage de services doit être documenté.
- L'isolation doit être testée sur le plan de données.

Un VNI différent contribue à identifier un segment overlay, mais un VNI seul ne remplace pas une politique de sécurité complète.

## 15.4. Exercice

Concevez une matrice de communication entre :

- WEB Alpha.
- APP Alpha.
- DB Alpha.
- WEB Beta.
- APP Beta.
- DB Beta.
- DNS partagé.
- Supervision.
- Administration.

Pour chaque flux, indiquez :

- Source.
- Destination.
- VNI.
- VRF.
- Protocole.
- Port.
- Point de filtrage.
- Résultat attendu.
- Test positif.
- Test négatif.


# 16. Défi 11 — Anycast gateway et routage distribué

Dans certains designs VXLAN EVPN, les leafs fournissent une passerelle distribuée ou Anycast Gateway pour les endpoints des réseaux concernés.

Cette fonction peut permettre à des endpoints d'utiliser une passerelle cohérente même s'ils se trouvent sur des leafs différents.

## 16.1. Schéma conceptuel

```text
                SEGMENT LOGIQUE WEB
                    10.110.10.0/24

            +-----------------------------+
            |                             |
            v                             v
        +----------+                 +----------+
        | LEAF-101 |                 | LEAF-201 |
        | Gateway  |                 | Gateway  |
        +----------+                 +----------+
            |                             |
            v                             v
          VM-A                          VM-B

        Même adresse de passerelle logique
        selon le modèle Anycast supporté.
```

Ce schéma est conceptuel. La configuration de l'adresse Anycast, des MAC associées et des politiques de routage dépend de la plateforme.

## 16.2. Avantages potentiels

- Passerelle disponible sur plusieurs leafs.
- Routage distribué du trafic entre sous-réseaux.
- Réduction de certains détours vers une passerelle centralisée.
- Adaptation à une architecture avec mobilité des endpoints.

## 16.3. Points de vigilance

- Un underlay stable est indispensable.
- Le plan IP doit être cohérent.
- Les passerelles doivent suivre le modèle supporté.
- Le routage inter-VRF exige des règles spécifiques.
- Les politiques de sécurité doivent être cohérentes avec le routage distribué.
- La redondance de la passerelle ne remplace pas la redondance du serveur ni de ses liens.

## 16.4. Exercice

Comparez :

1. Une passerelle centralisée.
2. Une passerelle distribuée sur les leafs.
3. Une architecture sans extension L2, avec routage L3 jusqu'aux serveurs.

Pour chaque solution, analysez :

- Le chemin des paquets.
- La latence.
- La convergence.
- La complexité d'administration.
- La mobilité des machines virtuelles.
- Les mécanismes de sécurité.
- Le comportement lors d'une panne de leaf.


# 17. Défi 12 — Multihoming EVPN

Le multihoming EVPN permet, dans les architectures qui le prennent en charge, de raccorder un même Ethernet Segment à plusieurs équipements de réseau et de coordonner la connectivité.

Il ne doit pas être confondu avec un simple LACP entre deux commutateurs indépendants.

## 17.1. Schéma conceptuel

```text
                   SERVEUR / HYPERVISEUR
                     NIC-1       NIC-2
                       |           |
                       v           v
                    +------+     +------+
                    | L101 |     | L102 |
                    +------+     +------+
                       \           /
                        \         /
                    Ethernet Segment
                         /     \
                        v       v
                    SPINE-01  SPINE-02
```

Le schéma exprime la logique générale du raccordement à deux leafs. Les liens, l'agrégation et les procédures de multihoming exactes dépendent du design EVPN et du matériel.

## 17.2. Points à étudier

- Identification de l'Ethernet Segment.
- Attribution de l'ESI lorsque le mécanisme l'utilise.
- État des chemins.
- Comportement lors de la perte d'un lien.
- Comportement lors de la perte d'un leaf.
- Répartition du trafic.
- Prévention des boucles.
- Détection des chemins inactifs.
- Cohérence entre l'underlay et l'overlay.

## 17.3. Exercice de panne

Dans le laboratoire :

1. Établir le raccordement redondant.
2. Vérifier la connectivité.
3. Perdre un lien.
4. Mesurer l'interruption.
5. Vérifier les routes et états EVPN.
6. Perdre un leaf dans un environnement isolé.
7. Vérifier le comportement de reprise.
8. Rétablir le leaf.
9. Observer la convergence.
10. Vérifier qu'aucune boucle ni duplication permanente de trafic n'apparaît.

Les tests de panne doivent être effectués dans un environnement de laboratoire ou pendant une fenêtre de maintenance autorisée.


# 18. Défi 13 — MTU et VXLAN

L'encapsulation VXLAN ajoute des en-têtes au paquet transporté.

La RFC 7348 recommande de dimensionner le MTU du réseau physique pour prendre en compte l'augmentation de taille due à l'encapsulation, afin d'éviter les problèmes de fragmentation ou de perte de paquets. Le comportement exact dépend du chemin et des équipements.

## 18.1. Ce qu'il faut vérifier

- MTU des cartes réseau.
- MTU des ports d'accès.
- MTU des uplinks leaf-spine.
- MTU des interfaces VTEP.
- MTU des hyperviseurs.
- MTU des chemins de secours.
- Présence d'autres tunnels.
- Compteurs d'abandon.
- Messages liés à la découverte du MTU de chemin.

## 18.2. Exercice de diagnostic

Une VM peut établir une session TCP vers un service distant, mais certains transferts échouent lorsqu'ils deviennent volumineux.

Hypothèses possibles :

- MTU insuffisant.
- ICMP nécessaire à la découverte du MTU bloqué.
- Route asymétrique.
- Pertes de paquets.
- Congestion.
- Problème du service.

Procédure :

1. Comparer les transferts courts et longs.
2. Relever les compteurs des interfaces.
3. Vérifier la connectivité entre les VTEP.
4. Contrôler le MTU des chemins.
5. Examiner les retransmissions.
6. Vérifier les messages de contrôle pertinents.
7. Comparer le chemin principal et le chemin de secours.
8. Corriger la configuration démontrée comme incorrecte.
9. Refaire les tests.
10. Documenter les valeurs et les hypothèses.

Ne changez pas arbitrairement le MTU sur tous les équipements.


# 19. Défi 14 — Sécurité dans une fabric leaf-spine

Une fabric connecte de nombreux endpoints. Si les règles de sécurité sont trop permissives, une compromission peut permettre un déplacement latéral entre plusieurs serveurs.

La sécurité doit être conçue pour les flux est-ouest comme pour les flux nord-sud.

## 19.1. Principes de sécurité

- Séparer les environnements et rôles.
- Autoriser uniquement les flux nécessaires.
- Protéger le réseau de gestion.
- Contrôler l'accès aux services de stockage.
- Séparer le trafic de sauvegarde.
- Utiliser des identités individuelles.
- Superviser les connexions administratives.
- Limiter les routes et annonces réseau.
- Documenter les exceptions.
- Tester les communications interdites.

## 19.2. Matrice de flux

| Source | Destination | Politique de référence |
|---|---|---|
| WEB | APP | Autoriser les ports applicatifs nécessaires |
| WEB | DB | Refuser par défaut |
| APP | DB | Autoriser les ports nécessaires |
| Serveurs | MGMT | Refuser par défaut |
| Poste d'administration | MGMT | Autoriser selon les rôles |
| Production | BACKUP | Autoriser les flux nécessaires |
| Utilisateurs | STORAGE | Refuser par défaut |
| MONITORING | Serveurs | Autoriser les protocoles de collecte |
| Réseau test | Production | Refuser par défaut |
| Tenant Alpha | Tenant Beta | Refuser par défaut |
| WAN | Services publiés | Autoriser uniquement les ports publiés |

La matrice doit être traduite dans les mécanismes de filtrage réellement disponibles : ACL, pare-feu, politiques distribuées ou autres outils adaptés.

Une fabric leaf-spine ne fournit pas automatiquement une segmentation applicative complète simplement parce que l'underlay est routé.

## 19.3. Séparer les plans de gestion

Le plan de gestion doit être accessible depuis des sources autorisées.

Il faut distinguer :

- Le trafic de gestion des commutateurs.
- Le trafic d'administration des hyperviseurs.
- Les interfaces BMC.
- La gestion du stockage.
- La supervision.
- Le trafic de données des applications.

Le choix d'un VLAN de gestion doit être accompagné de politiques appropriées. Un VLAN seul n'est pas une garantie de sécurité.


# 20. Défi 15 — Supervision de la fabric

Une bonne supervision doit fournir des informations sur la topologie, les chemins et les services.

## 20.1. Indicateurs à collecter

| Domaine | Indicateurs |
|---|---|
| Interfaces | État, débit, erreurs et drops |
| OSPF | Voisinages, routes, changements de topologie |
| BGP | Sessions, routes, changements de politique |
| ECMP | Prochains sauts installés et répartition observée |
| VTEP | Joignabilité et état de l'overlay |
| VXLAN | VNI, erreurs et compteurs selon la plateforme |
| EVPN | Routes, endpoints et état des sessions |
| LACP/MLAG | État des liens et mécanismes de multihoming |
| MTU | Paramètres et compteurs d'abandon |
| Serveurs | CPU, mémoire, réseau et disponibilité |
| Stockage | Latence, débit, état des chemins et erreurs |
| Sauvegarde | Succès, durée et résultats des restaurations |

La présence d'une route ne garantit pas que le flux utilise le chemin attendu. Les mesures de contrôle et de transfert doivent être rapprochées.

## 20.2. Supervision de bout en bout

Créez des sondes pour tester :

- La connectivité entre loopbacks.
- L'accès au service Web.
- Les appels applicatifs.
- Les flux vers le stockage.
- Les services DNS.
- Les communications entre VTEP.
- La connectivité après perte d'un lien.

Les tests doivent distinguer les pannes de transport des pannes applicatives.

## 20.3. Exercice

Construisez un tableau de bord permettant de répondre à ces questions :

1. Tous les leafs et spines sont-ils opérationnels ?
2. Les voisinages IGP ou BGP sont-ils établis ?
3. Les chemins ECMP sont-ils présents ?
4. Les liens sont-ils saturés ?
5. Les VTEP sont-ils joignables ?
6. Les sessions EVPN sont-elles opérationnelles ?
7. Les communications entre tenants sont-elles conformes ?
8. Une panne a-t-elle changé les routes ?
9. Les services applicatifs sont-ils disponibles ?
10. La capacité restante est-elle suffisante en cas de perte d'un chemin ?


# 21. Défi expert — Architecture de bordure

Une fabric leaf-spine doit souvent se connecter à :

- Un réseau WAN.
- Un campus.
- Un autre datacenter.
- Un pare-feu.
- Un réseau de stockage externe.
- Des services cloud.

Ces connexions doivent être conçues sans transformer le backbone en une topologie irrégulière difficile à exploiter.

## 21.1. Schéma de bordure

```text
                  RÉSEAUX EXTERNES
                         |
                    +----------+
                    | PARE-FEU |
                    +----------+
                       |    |
                       v    v
                  +-------+ +-------+
                  | L201  | | L202  |
                  |BORDER | |BORDER |
                  +-------+ +-------+
                     | \     / |
                     |  \   /  |
                     v   v v   v
                  +----------------+
                  | SPINE LAYER    |
                  +----------------+
                     |   |   |
                     v   v   v
                    LEAFS DE CALCUL
```

Le dessin est simplifié. Chaque leaf raccordé à la fabric doit conserver les liens leaf-spine prévus. Les leafs de bordure possèdent en plus les connexions externes définies par l'architecture.

## 21.2. Routage externe

Le routage externe doit préciser :

- Les préfixes annoncés.
- Les préfixes acceptés.
- Les routes par défaut.
- Les routes de retour.
- Les politiques BGP éventuelles.
- Les contrôles de préfixes.
- Les chemins de secours.
- Le comportement si une bordure devient indisponible.

Ne propagez pas automatiquement toutes les routes de l'extérieur à tous les segments internes.

## 21.3. Exercice

Vous devez publier un réseau applicatif à travers la paire de leafs de bordure.

Documentez :

1. Les adresses de transit.
2. Les sessions de routage.
3. Les préfixes annoncés.
4. Les filtres de routes.
5. La politique de sécurité.
6. Le comportement lors de la perte d'un lien.
7. Le comportement lors de la perte d'un leaf de bordure.
8. Les routes de retour.
9. Les journaux.
10. Les tests de non-régression.


# 22. Défi expert — Automatisation

Une fabric qui évolue régulièrement bénéficie d'une source de vérité et de contrôles automatisés.

L'objectif de l'automatisation est de réduire les erreurs répétitives et d'améliorer la traçabilité, pas de propager aveuglément des modifications.

## 22.1. Éléments à automatiser

Vous pouvez automatiser :

- La vérification des interfaces.
- La comparaison des adresses de liens.
- Le contrôle des loopbacks.
- La collecte des routes.
- La vérification des voisins.
- L'analyse de l'ECMP.
- Le contrôle du MTU.
- La collecte des informations VXLAN.
- La vérification des VNI.
- Le contrôle des sessions EVPN.
- La comparaison entre configuration attendue et configuration réelle.
- La génération du rapport de conformité.

## 22.2. Cycle de changement

```text
             SOURCE DE VÉRITÉ
                    |
                    v
             VALIDATION DES DONNÉES
                    |
                    v
             ANALYSE DE CONFIGURATION
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
             TESTS AUTOMATISÉS
                    |
                    v
             VALIDATION FINALE
                    |
                    v
             RETOUR ARRIÈRE SI NÉCESSAIRE
```

## 22.3. Garde-fous obligatoires

- Tester les changements en laboratoire.
- Contrôler les données d'entrée.
- Vérifier les changements de routes.
- Limiter les privilèges des comptes d'automatisation.
- Sauvegarder les configurations.
- Déployer progressivement.
- Arrêter le déploiement si une vérification échoue.
- Journaliser les opérations.
- Préparer une procédure de retour arrière.
- Vérifier les communications autorisées et interdites.

## 22.4. Exercice

Construisez un outil ou un playbook qui vérifie :

- La présence de tous les liens attendus.
- Les bonnes adresses IP.
- Les voisins OSPF ou BGP.
- Les routes vers les loopbacks.
- Le nombre de chemins ECMP prévu.
- Les VNI et VTEP attendus, si VXLAN est utilisé.
- Les sessions EVPN.
- Les états des interfaces.
- Les anomalies de MTU connues.

L'outil doit distinguer une donnée manquante, une panne de collecte et une configuration réellement incorrecte.


# 23. Scénarios de dépannage

## Scénario A — Un leaf n'apprend plus les loopbacks distantes

### Symptôme

Les interfaces physiques sont actives, mais le leaf n'a plus de route vers certains autres leafs.

### Hypothèses

- Voisinage OSPF en échec.
- Configuration incorrecte d'une interface.
- Route annoncée ou filtrée incorrectement.
- Erreur d'adressage.
- Problème de coût ou de route.
- Instabilité physique.
- Mauvais router ID.

### Démarche

1. Vérifier les interfaces.
2. Contrôler les adresses.
3. Examiner les voisins OSPF.
4. Contrôler la table de routage.
5. Vérifier les annonces de loopbacks.
6. Examiner les journaux.
7. Vérifier les métriques.
8. Tester la connectivité entre voisins directs.
9. Corriger la cause démontrée.
10. Vérifier que les autres chemins fonctionnent.


## Scénario B — ECMP est attendu, mais un seul chemin est installé

### Hypothèses

- Les métriques diffèrent.
- Les routes ne sont pas équivalentes.
- La limite de chemins ECMP est atteinte.
- Les attributs BGP diffèrent.
- Une politique de routage privilégie un chemin.
- La plateforme ne prend pas en charge la combinaison attendue.

### Démarche

1. Vérifier la topologie physique.
2. Comparer les métriques des chemins.
3. Examiner les routes et prochains sauts.
4. Vérifier les options ECMP de la plateforme.
5. Contrôler les politiques.
6. Mesurer les compteurs d'interface.
7. Comparer avec un chemin de laboratoire.
8. Modifier un paramètre à la fois.
9. Vérifier la nouvelle répartition.
10. Documenter le résultat.

Un seul chemin installé n'est pas nécessairement une panne : il peut être la conséquence d'un choix de routage valide.


## Scénario C — Un lien tombe, mais la perte de paquets est excessive

### Hypothèses

- Convergence lente.
- Détection de panne tardive.
- ECMP incorrect.
- Route alternative indisponible.
- Lien restant saturé.
- Politique d'agrégation ou de multihoming défectueuse.
- Mauvaise configuration du mécanisme de secours.

### Démarche

1. Enregistrer le moment de la panne.
2. Vérifier l'état du lien.
3. Contrôler les événements de routage.
4. Mesurer la perte de paquets.
5. Examiner les routes après la panne.
6. Vérifier le débit sur les chemins restants.
7. Contrôler le comportement du serveur si un accès redondant existe.
8. Rétablir le lien.
9. Observer le retour à l'état nominal.
10. Documenter les temps et effets mesurés.


## Scénario D — Les VTEP sont joignables, mais les VM de deux leafs ne communiquent pas

### Hypothèses

- VNI incorrect.
- Session EVPN absente.
- Route MAC/IP absente.
- Mauvaise association VLAN/VNI.
- Mauvaise appartenance au segment.
- Politique de filtrage.
- MTU insuffisant.
- Endpoint mal appris.
- Problème de passerelle ou de routage.

### Démarche

1. Vérifier l'underlay.
2. Vérifier la joignabilité des VTEP.
3. Contrôler les sessions EVPN.
4. Vérifier les VNI.
5. Examiner les informations MAC/IP.
6. Contrôler l'appartenance des endpoints.
7. Vérifier le filtrage.
8. Examiner les compteurs.
9. Tester le MTU.
10. Comparer avec un segment qui fonctionne.


## Scénario E — La fabric fonctionne, mais le stockage subit des interruptions

### Hypothèses

- MTU incohérent.
- Lien saturé.
- Multipathing mal configuré.
- Une panne affecte tous les chemins physiques.
- QoS inadaptée.
- Problème sur le système de stockage.
- Mauvais raccordement.
- Erreurs physiques.

### Démarche

1. Vérifier les alertes du stockage.
2. Contrôler les ports physiques.
3. Examiner les routes et VLAN pertinents.
4. Vérifier les chemins de stockage.
5. Mesurer la latence.
6. Contrôler les erreurs et pertes.
7. Examiner le MTU.
8. Vérifier l'indépendance des chemins.
9. Tester le rétablissement après panne.
10. Documenter les causes et limitations.


## Scénario F — La répartition du trafic est déséquilibrée

### Hypothèses

- Hachage insuffisamment diversifié.
- Peu de flux volumineux.
- Trop peu de chemins disponibles.
- Limite de capacité sur un lien.
- Agrégation des flux en amont.
- Politiques de routage différentes.
- Un seul flux monopolise une part importante de la bande passante.

### Démarche

1. Mesurer les débits par interface.
2. Identifier le nombre de flux.
3. Comparer les chemins installés.
4. Examiner le mécanisme de hachage de la plateforme.
5. Comparer les champs des flux.
6. Vérifier la capacité des liens.
7. Mesurer sur une durée représentative.
8. Évaluer les options d'ingénierie de trafic disponibles.
9. Tester les changements en laboratoire.
10. Comparer les résultats après changement.

Ne considérez pas un déséquilibre de trafic comme une preuve automatique de mauvaise configuration ECMP.


# 24. Défi final — Incident combiné de fabric

Plusieurs incidents sont signalés simultanément :

1. Une application devient lente.
2. Un leaf a perdu une session de routage.
3. Un chemin ECMP n'apparaît plus dans la table de routage.
4. Les machines virtuelles d'un même segment se trouvant sur des leafs différents ne communiquent plus.
5. Les sauvegardes saturent un lien.
6. Une bascule de serveur provoque une interruption.
7. La supervision ne fournit pas de chronologie cohérente.

Vous ne savez pas si ces incidents ont une cause commune.

## 24.1. Règles d'intervention

Vous devez :

- Préserver les journaux.
- Identifier les flux affectés.
- Séparer les problèmes d'underlay, d'overlay et d'application.
- Ne pas modifier toutes les métriques simultanément.
- Ne pas désactiver le routage pour tester une hypothèse.
- Ne pas retirer les VNI ou les routes sans sauvegarde.
- Ne pas changer le MTU sans mesures.
- Maintenir une voie d'administration.
- Documenter chaque changement.
- Valider les chemins après correction.

## 24.2. Tableau de collecte

| Symptôme | Domaine | Première vérification |
|---|---|---|
| Application lente | Performance | Latence, pertes, débit et charge |
| Session de routage perdue | Underlay | Interface, voisin et journaux |
| ECMP absent | Routage | Coûts, attributs et limites |
| VM inter-leaf injoignable | Overlay | VTEP, VNI, EVPN et politiques |
| Sauvegarde saturante | Capacité | Débits et files d'attente |
| Bascule serveur interrompue | Multihoming | États des liens et mécanisme de reprise |
| Chronologie incohérente | Supervision | Horloges et collecte des journaux |

## 24.3. Phase 1 — Établir les faits

Pour chaque incident, identifiez :

- Les équipements concernés.
- Le périmètre des utilisateurs.
- Les liens parcourus.
- Les routes attendues.
- Les routes réellement installées.
- Les mesures disponibles.
- Les changements récents.
- Les mécanismes de redondance impliqués.

## 24.4. Phase 2 — Vérifier les dépendances

Exemples :

- Une perte de session OSPF peut modifier l'ensemble des routes disponibles.
- L'absence d'un chemin ECMP peut augmenter le taux d'utilisation du chemin restant.
- La perte de communication entre VM peut être liée à l'overlay même si l'underlay reste joignable.
- Une saturation pendant les sauvegardes peut expliquer une partie des lenteurs sans expliquer automatiquement la perte d'un voisinage.
- Une interruption après bascule peut être liée au multihoming ou à la convergence du routage.

Ne concluez pas qu'une corrélation temporelle démontre une cause unique.

## 24.5. Phase 3 — Corriger et valider

1. Prioriser les services critiques.
2. Recueillir une preuve pour chaque hypothèse.
3. Identifier le changement minimal.
4. Sauvegarder les configurations.
5. Appliquer le changement dans le cadre autorisé.
6. Vérifier les routes et les chemins.
7. Vérifier le comportement de l'overlay.
8. Mesurer les pertes et la latence.
9. Tester les communications interdites.
10. Contrôler les effets sur les autres services.
11. Documenter la cause racine.
12. Mettre à jour les procédures.


# 25. Architecture cible consolidée

## 25.1. Vue d'ensemble

```text
                        FABRIC SPINE-LEAF
                               |
               +---------------+---------------+
               |                               |
               v                               v
        +--------------+                 +--------------+
        | SPINE-01     |                 | SPINE-02     |
        +--------------+                 +--------------+
          |    |    |                      |    |    |
          |    |    |                      |    |    |
          v    v    v                      v    v    v
       +------+ +------+ +------+ +------+ 
       |L101  | |L102  | |L201  | |L202  |
       +------+ +------+ +------+ +------+
          |       |        |        |
          v       v        v        v
       Serveurs Serveurs  Stockage Services
       / VMs    / VMs     autorisé de bordure

             UNDERLAY IP / OSPF ou BGP
                        |
                        v
               Routes et ECMP
                        |
                        v
             OVERLAY VXLAN EVPN
             si requis par le besoin
                        |
            +-----------+-----------+
            |                       |
            v                       v
       VNI production          VNI test / tenants
```

Dans la version détaillée du dossier, chaque leaf doit être représenté avec deux liens distincts, un vers SPINE-01 et un vers SPINE-02.

## 25.2. Résumé des décisions

| Domaine | Décision de référence |
|---|---|
| Topologie | Leaf-spine avec liens L3 |
| Underlay débutant | OSPF |
| Underlay alternatif | eBGP selon le besoin et les compétences |
| ECMP | Chemins de coût ou d'attributs équivalents |
| Adressage | Loopbacks et liens point à point documentés |
| Segmentation simple | VLAN et routage L3 |
| Overlay expert | VXLAN EVPN |
| VTEP | Loopbacks leaf configurées selon la plateforme |
| EVPN | Contrôle de l'overlay |
| Multihoming | MLAG/vPC ou EVPN multihoming selon la plateforme |
| Stockage | Réseau et politiques dédiés |
| Administration | Accès contrôlé |
| Sécurité | Matrice de flux et contrôles cohérents |
| MTU | Vérifié de bout en bout |
| Supervision | Routes, chemins et services surveillés |
| Automatisation | Déploiement progressif avec retour arrière |


# 26. Barème d'évaluation sur 100 points

| Domaine | Points |
|---|---:|
| Compréhension de l'architecture leaf-spine | 8 |
| Architecture physique et adressage | 8 |
| Underlay IP et routage | 10 |
| ECMP et mesure des chemins | 10 |
| Dimensionnement et surallocation | 7 |
| Segmentation des réseaux serveurs | 7 |
| Multihoming et redondance | 8 |
| VXLAN et VNI | 8 |
| BGP EVPN | 8 |
| MTU et performances | 6 |
| Sécurité et matrice de flux | 6 |
| Supervision et dépannage | 6 |
| Automatisation et changements | 4 |
| Documentation finale | 4 |
| **Total** | **100** |

## 26.1. Critères d'excellence

Une bonne solution doit :

- Présenter une topologie détaillée et cohérente.
- Définir une adresse unique pour chaque interface.
- Vérifier la connectivité underlay.
- Expliquer le fonctionnement d'ECMP.
- Mesurer les effets d'une panne.
- Dimensionner la fabric pour la charge réelle.
- Choisir le routage selon les besoins.
- Séparer underlay et overlay.
- Démontrer la connectivité VXLAN EVPN lorsqu'elle est utilisée.
- Tester les mécanismes de multihoming.
- Vérifier le MTU.
- Présenter les preuves de validation.
- Prévoir un retour arrière pour les changements.

## 26.2. Erreurs graves

Les erreurs suivantes doivent entraîner une pénalité importante :

- Configurer une topologie sans identifier tous les liens.
- Utiliser des adresses de liens dupliquées.
- Supposer qu'une topologie redondante garantit une interruption nulle.
- Considérer ECMP comme une répartition parfaitement uniforme.
- Étendre tous les VLAN sur tous les liens sans besoin.
- Mélanger les concepts underlay et overlay.
- Utiliser VXLAN sans vérifier la connectivité VTEP.
- Négliger le MTU de l'encapsulation.
- Agréger des liens de serveur vers deux leafs sans mécanisme compatible.
- Déployer un overlay sans contrôler les routes.
- Faire des changements sans sauvegarde.
- Valider des tests sans preuves.


# 27. Modèle du dossier technique final

## 27.1. Résumé exécutif

Présentez :

- Le besoin initial.
- La topologie retenue.
- Les objectifs de capacité.
- Le protocole underlay.
- Le modèle de segmentation.
- La stratégie de redondance.
- Les risques principaux.
- Les résultats des tests.

## 27.2. Architecture physique

Fournissez :

- Le plan leaf-spine.
- Les équipements.
- Les interfaces de chaque lien.
- Le débit des liens.
- Le câblage.
- Les ports serveurs.
- Les chemins de stockage.
- Les connexions de bordure.
- Le mécanisme de multihoming.

## 27.3. Architecture logique

Fournissez :

- Les loopbacks.
- Les adresses de liens.
- Les routes attendues.
- Les métriques.
- Le plan des VLAN.
- Les sous-réseaux.
- Les VRF, si utilisées.
- Le plan de VNI.
- Les VTEP.
- Les politiques de filtrage.
- Les routes et sessions EVPN.

## 27.4. Tableau des liens

| Lien | Adresse A | Adresse B | Débit | Fonction | Résultat de validation |
|---|---|---|---|---|---|
| SPINE-01 ↔ LEAF-101 | `10.255.0.0/31` | `10.255.0.1/31` | À renseigner | Underlay | À tester |
| SPINE-02 ↔ LEAF-101 | `10.255.0.2/31` | `10.255.0.3/31` | À renseigner | Underlay | À tester |
| SPINE-01 ↔ LEAF-102 | `10.255.0.4/31` | `10.255.0.5/31` | À renseigner | Underlay | À tester |
| SPINE-02 ↔ LEAF-102 | `10.255.0.6/31` | `10.255.0.7/31` | À renseigner | Underlay | À tester |
| SPINE-01 ↔ LEAF-201 | `10.255.0.8/31` | `10.255.0.9/31` | À renseigner | Underlay | À tester |
| SPINE-02 ↔ LEAF-201 | `10.255.0.10/31` | `10.255.0.11/31` | À renseigner | Underlay | À tester |
| SPINE-01 ↔ LEAF-202 | `10.255.0.12/31` | `10.255.0.13/31` | À renseigner | Underlay | À tester |
| SPINE-02 ↔ LEAF-202 | `10.255.0.14/31` | `10.255.0.15/31` | À renseigner | Underlay | À tester |

## 27.5. Tableau de validation

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | Connectivité des liens | Tous les liens conformes | À renseigner | À exécuter |
| T02 | Loopbacks | Toutes les loopbacks joignables | À renseigner | À exécuter |
| T03 | OSPF/BGP underlay | Voisinages conformes | À renseigner | À exécuter |
| T04 | ECMP | Chemins attendus présents | À renseigner | À exécuter |
| T05 | Panne d'un lien spine-leaf | Reprise conforme au plan | À renseigner | À exécuter |
| T06 | Segmentation VLAN | Réseaux correctement séparés | À renseigner | À exécuter |
| T07 | VTEP | Joignabilité underlay | À renseigner | À exécuter |
| T08 | BGP EVPN | Sessions et routes attendues | À renseigner | À exécuter |
| T09 | Connectivité VXLAN | Communication conforme | À renseigner | À exécuter |
| T10 | Isolation inter-tenant | Flux non autorisés bloqués | À renseigner | À exécuter |
| T11 | MTU | Paquets conformes au chemin | À renseigner | À exécuter |
| T12 | Multihoming | Bascule validée en test | À renseigner | À exécuter |
| T13 | Supervision | Alertes et mesures disponibles | À renseigner | À exécuter |
| T14 | Retour arrière | Procédure validée | À renseigner | À exécuter |

Un statut « OK » doit correspondre à un test réellement exécuté et documenté.


# 28. Checklist finale

## Architecture physique

- [ ] Chaque leaf possède les liens prévus vers chaque spine.
- [ ] Chaque lien possède des adresses IP documentées.
- [ ] Les interfaces sont identifiées.
- [ ] Les serveurs ne dépendent pas de liens non documentés.
- [ ] Les chemins redondants sont identifiés.
- [ ] Les capacités des liens sont connues.
- [ ] Les points uniques de panne sont documentés.

## Underlay

- [ ] Les loopbacks sont uniques.
- [ ] Les interfaces point à point sont correctement adressées.
- [ ] Les voisins OSPF ou BGP sont établis.
- [ ] Les routes attendues sont présentes.
- [ ] Les métriques ou attributs sont documentés.
- [ ] ECMP est vérifié.
- [ ] La convergence a été mesurée.
- [ ] Les routes de gestion sont cohérentes.

## Overlay

- [ ] Les besoins d'extension L2 sont justifiés.
- [ ] Les VNI sont documentées.
- [ ] Les VTEP sont joignables.
- [ ] Les sessions EVPN sont validées.
- [ ] Les endpoints sont correctement appris.
- [ ] Les règles de routage et de sécurité sont cohérentes.
- [ ] Les mécanismes de multihoming sont compris.
- [ ] Le MTU prend en compte l'encapsulation.

## Sécurité

- [ ] Les réseaux de production et de test sont séparés.
- [ ] Les services de gestion sont protégés.
- [ ] Le stockage est réservé aux sources nécessaires.
- [ ] Les flux autorisés sont documentés.
- [ ] Les flux interdits sont testés.
- [ ] Les routes et annonces sont contrôlées.
- [ ] Les comptes d'administration sont protégés.
- [ ] Les journaux sont disponibles.

## Exploitation

- [ ] Les configurations sont sauvegardées.
- [ ] Les changements sont tracés.
- [ ] La supervision couvre underlay et overlay.
- [ ] Les procédures de panne sont documentées.
- [ ] Le retour arrière est défini.
- [ ] Les tests de non-régression sont conservés.
- [ ] Les résultats et risques résiduels sont présentés.


# 29. Références techniques

- [RFC 7938 — Use of BGP for Routing in Large-Scale Data Centers](https://www.rfc-editor.org/rfc/rfc7938.html) : architecture de routage BGP pour les grands datacenters.
- [RFC 7348 — Virtual eXtensible Local Area Network (VXLAN)](https://www.rfc-editor.org/rfc/rfc7348.html) : encapsulation VXLAN et transport de réseaux logiques sur une infrastructure IP.
- [RFC 7432 — BGP MPLS-Based Ethernet VPN](https://www.rfc-editor.org/rfc/rfc7432.html) : architecture et mécanismes EVPN de base.
- [RFC 8365 — A Network Virtualization Overlay Solution Using EVPN](https://www.rfc-editor.org/rfc/rfc8365.html) : utilisation d'EVPN comme solution d'overlay, notamment avec VXLAN.
- [RFC 9746 — BGP EVPN Multihoming Extensions for Split-Horizon Filtering](https://www.rfc-editor.org/rfc/rfc9746.html) : mise à jour du traitement de certains mécanismes de multihoming EVPN.
- Documentation officielle du constructeur : underlay IP, OSPF, BGP, ECMP, VXLAN, EVPN et multihoming.
- Documentation officielle de l'hyperviseur : vSwitch, réseaux virtuels, LACP et raccordement redondant.
- Documentation Wireshark : capture et analyse du trafic.
- Documentation de supervision : télémétrie, compteurs d'interface et suivi des routes.

Les RFC décrivent des protocoles ou des architectures. Les commandes exactes, les capacités ECMP, les procédures EVPN et les limites matérielles dépendent du système réseau utilisé.


# Conclusion

Le challenge doit démontrer qu'une fabric spine-leaf n'est pas simplement une topologie comportant plusieurs commutateurs reliés entre eux.

C'est une architecture dans laquelle la connectivité physique, le routage, la répartition des flux, la segmentation logique et la convergence doivent être conçus ensemble.

La réussite repose sur six principes :

1. **Topologie régulière :** chaque leaf est relié aux spines prévus et chaque lien est documenté.
2. **Underlay maîtrisé :** les routes et les chemins sont cohérents avant l'introduction d'un overlay.
3. **ECMP mesuré :** la répartition des flux est observée au lieu d'être supposée.
4. **Overlay justifié :** VXLAN EVPN est introduit lorsque la segmentation ou l'extension logique le nécessite.
5. **Redondance testée :** la panne d'un lien ou d'un leaf fait l'objet d'un test et d'une mesure.
6. **Exploitation documentée :** les politiques, la supervision, les changements et les procédures de retour arrière sont vérifiables.

La meilleure architecture leaf-spine n'est pas nécessairement la plus complexe. C'est celle qui répond aux besoins de capacité et de disponibilité, qui maintient des domaines de panne maîtrisables et qui permet aux ingénieurs d'expliquer et de tester le chemin réel des paquets.