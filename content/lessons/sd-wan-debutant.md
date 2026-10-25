# SD-WAN — Niveau débutant

## Comprendre le WAN logiciel, les tunnels, les politiques applicatives et le pilotage intelligent du trafic


# PRÉSENTATION DU COURS

Le SD-WAN (*Software-Defined Wide Area Network*) est une approche de conception et d'exploitation des réseaux WAN qui permet de piloter de manière centralisée les connexions entre plusieurs sites d'une organisation, en s'appuyant sur des logiciels, des politiques et des mécanismes d'automatisation.

Dans une architecture WAN traditionnelle, chaque site doit disposer d'une connectivité vers les autres sites ou vers les services centraux. Les entreprises peuvent utiliser des circuits opérateur privés, du MPLS, des accès Internet professionnels, de la fibre, des connexions mobiles 4G/5G ou plusieurs de ces moyens simultanément.

Le problème apparaît lorsque le réseau doit utiliser plusieurs types de connectivité, garantir des performances suffisantes pour certaines applications et s'adapter rapidement à une panne.

Un accès Internet peut être moins coûteux qu'un circuit privé, mais sa latence et ses pertes de paquets peuvent varier. Un circuit privé peut offrir des caractéristiques de service mieux maîtrisées, mais son coût et ses délais de mise en service peuvent être plus importants. Une connexion mobile peut apporter une solution de secours, sous réserve de couverture, de capacité et de conditions de service adaptées.

Le SD-WAN permet de gérer ces différentes possibilités à travers une architecture cohérente. Les équipements de bordure peuvent mesurer les performances des chemins, appliquer des politiques de trafic et utiliser une connectivité adaptée aux besoins des applications.

Il ne faut cependant pas considérer le SD-WAN comme une technologie qui garantit automatiquement la meilleure performance. Les résultats dépendent de la qualité des liens, de la conception du réseau, des fonctions disponibles sur la plateforme et des politiques définies par l'administrateur.

Ce cours présente les fondements nécessaires avant de passer à la configuration des équipements, à l'établissement des tunnels, à la sélection dynamique des chemins et au dépannage avancé.

## Place dans le parcours

Ce document constitue le premier niveau d'un parcours progressif.

```text
NIVEAU DÉBUTANT — sd-wan-debutant.md
        |
        v
Comprendre le WAN traditionnel
Découvrir le SD-WAN
Distinguer underlay et overlay
Comprendre les rôles des équipements
Découvrir les politiques applicatives
Comprendre la sécurité et la résilience
        |
        v
NIVEAU INTERMÉDIAIRE — sd-wan-intermediaire.md
        |
        v
Construire un laboratoire multi-sites
Préparer l'underlay IP
Enregistrer et authentifier les équipements
Établir les connexions sécurisées
Configurer les routes et les politiques
Mesurer les chemins et tester les basculements
        |
        v
NIVEAU EXPERT — sd-wan-expert.md
        |
        v
Concevoir une architecture multi-sites évolutive
Optimiser les politiques applicatives
Maîtriser le routage et les mécanismes de contrôle
Organiser la segmentation et la sécurité
Étudier la haute disponibilité
Automatiser les validations et les opérations
```

**Continuité pédagogique :** les trois cours utiliseront la même entreprise fictive, comprenant un siège, deux agences et des services hébergés dans le cloud. Le niveau intermédiaire reprendra cette topologie pour construire un réseau de laboratoire. Le niveau expert approfondira ensuite sa conception, sa sécurité, sa disponibilité et son exploitation.


# OBJECTIFS PÉDAGOGIQUES

À la fin de ce cours, l'apprenant doit être capable de :

1. Expliquer le rôle du WAN dans une entreprise multisite.
2. Identifier les limites courantes d'une architecture WAN traditionnelle.
3. Définir le SD-WAN et ses principaux objectifs.
4. Distinguer l'underlay de l'overlay.
5. Comprendre le rôle d'un équipement SD-WAN de bordure.
6. Distinguer les fonctions de gestion, de contrôle et de transport des données.
7. Comprendre les principes des tunnels sécurisés entre les sites.
8. Expliquer le rôle des politiques applicatives.
9. Comprendre les notions de latence, de gigue, de perte de paquets et de bande passante.
10. Expliquer comment une solution SD-WAN peut choisir un chemin adapté à une application.
11. Comprendre la différence entre basculement de connexion et sélection dynamique des chemins.
12. Découvrir l'accès direct à Internet depuis une agence.
13. Identifier les principales fonctions de sécurité et de segmentation.
14. Construire une représentation cohérente d'une architecture SD-WAN multisite.
15. Préparer le laboratoire qui servira de point de départ aux niveaux suivants.

## Prérequis

Il est recommandé de connaître :

- L'adressage IPv4.
- Les sous-réseaux et les routes IP.
- Les rôles d'un routeur et d'un commutateur.
- Le fonctionnement général d'un réseau LAN.
- Les notions de TCP, UDP et ICMP.
- Les bases des VPN.
- Les principes fondamentaux des VLAN et des pare-feu.

La connaissance de MPLS est utile, mais n'est pas obligatoire.

Les commandes de configuration propres à un constructeur ne sont pas nécessaires pour suivre ce premier niveau.


# PARTIE 1 — COMPRENDRE LE WAN TRADITIONNEL

## 1. Qu'est-ce qu'un WAN ?

WAN signifie *Wide Area Network*. Il s'agit d'un réseau qui relie des équipements ou des réseaux locaux répartis sur une zone géographique étendue.

Une entreprise peut posséder un siège, plusieurs agences, des entrepôts, des centres de données et des utilisateurs distants. Ces environnements doivent communiquer pour accéder aux applications, aux fichiers, aux services d'identité et aux systèmes d'information.

Le réseau WAN assure le transport entre ces différents emplacements.

Il peut utiliser plusieurs types de connectivité :

- Des circuits privés fournis par un opérateur.
- Des services MPLS.
- Des accès Internet professionnels.
- Des connexions fibre ou Ethernet.
- Des accès mobiles 4G/5G.
- Des liaisons spécialisées selon les besoins.

Chaque solution possède ses caractéristiques en matière de coût, de capacité, de disponibilité, de latence et de gestion.

Il est donc important de ne pas considérer toutes les connexions WAN comme équivalentes.

## 2. Exemple d'un réseau d'entreprise traditionnel

Considérons une entreprise appelée **NovaTech**.

Elle possède un siège social, deux agences et une application hébergée dans un centre de données.

Les utilisateurs doivent accéder aux applications centrales. Les agences doivent également échanger des informations et accéder à des services Internet.

Dans une architecture WAN traditionnelle, les sites peuvent utiliser des circuits opérateur et des routeurs dont les chemins sont définis par la conception du réseau.

```text
                 CENTRE DE DONNÉES
                  Applications
                       |
                       |
                    WAN/MPLS
                  /          \
                 /            \
                v              v
           SIÈGE SOCIAL     AGENCE A
                                |
                                |
                             AGENCE B
```

Ce dessin représente une relation logique simplifiée. Une véritable architecture opérateur peut utiliser plusieurs routeurs, chemins et mécanismes de redondance.

Le réseau doit définir comment les sites sont reliés, quelles routes sont disponibles et quelles connexions doivent être utilisées pour joindre les applications.

Dans une architecture simple, le chemin d'un flux dépend essentiellement des routes et des mécanismes de forwarding disponibles. La sélection ne tient pas nécessairement compte de la qualité instantanée de chaque lien pour chaque application.

## 3. Les difficultés d'une architecture WAN traditionnelle

Les réseaux WAN traditionnels peuvent être fiables et parfaitement adaptés à certains besoins. Les difficultés apparaissent surtout lorsque le nombre de sites, les types de liens et les exigences applicatives augmentent.

### 3.1 La multiplication des sites

Lorsqu'une entreprise passe de trois à cinquante agences, la gestion des configurations, des routes et des politiques peut devenir plus complexe.

Chaque nouveau site demande une préparation des équipements, une connectivité adaptée et des contrôles permettant de vérifier qu'il peut joindre les services nécessaires.

Si chaque opération doit être définie individuellement et reproduite manuellement, les délais d'exploitation peuvent augmenter.

### 3.2 La coexistence de plusieurs accès

Une agence peut disposer d'un circuit privé et d'un accès Internet. Un autre site peut utiliser une connexion Internet et un lien mobile de secours.

L'entreprise doit alors décider comment exploiter ces connexions, quelles applications peuvent les utiliser et quelles conditions justifient un changement de chemin.

Une simple présence de deux interfaces WAN ne signifie pas que le réseau utilise intelligemment les deux connexions.

Il faut aussi disposer de routes appropriées, de politiques de sélection et de mécanismes permettant de détecter les problèmes.

### 3.3 Les différences de comportement des applications

Toutes les applications ne possèdent pas les mêmes exigences.

La voix et la visioconférence sont sensibles à la latence, à la gigue et aux pertes de paquets. Un transfert de fichiers volumineux est souvent davantage dépendant du débit disponible et de la durée de transfert.

Une application de gestion métier peut avoir besoin d'une connectivité stable vers un serveur précis, tandis qu'une navigation Internet ordinaire peut tolérer certains changements de chemin.

Le réseau doit donc prendre en compte les besoins applicatifs plutôt que d'appliquer une règle identique à tous les flux.

### 3.4 La visibilité opérationnelle

Lorsqu'un utilisateur signale qu'une application fonctionne lentement, l'administrateur doit déterminer si le problème provient du LAN, du lien WAN, du routage, d'une application distante ou d'une autre cause.

Une architecture bien supervisée doit permettre d'examiner les performances des liens et les chemins utilisés par les applications.

Le SD-WAN peut apporter une visibilité supplémentaire, mais il ne remplace pas les outils de supervision des services, des serveurs, des réseaux locaux et des fournisseurs.


# PARTIE 2 — DÉCOUVRIR LE SD-WAN

## 4. Définition

Le SD-WAN applique des principes de gestion logicielle et de politiques à un réseau WAN.

Au lieu de considérer uniquement les connexions physiques et les routes, l'architecture permet de définir des règles de fonctionnement adaptées aux besoins de l'entreprise.

Selon la solution utilisée, ces règles peuvent prendre en compte :

- L'application concernée.
- La destination.
- Le site d'origine.
- Le type de trafic.
- La disponibilité des liens.
- Les mesures de performance.
- Les priorités de l'organisation.
- Les exigences de sécurité.

Les équipements de bordure utilisent ces règles pour traiter les flux et sélectionner les chemins autorisés ou préférés.

Les capacités exactes varient d'une solution à l'autre. Les mécanismes de classification applicative, les métriques mesurées, les algorithmes de sélection et les options de sécurité doivent être vérifiés dans la documentation de la plateforme retenue.

## 5. Ce que change le SD-WAN

Dans une architecture classique, l'administrateur définit principalement la connectivité et les règles de routage.

Dans une architecture SD-WAN, il peut également définir une politique qui exprime le comportement attendu pour certaines applications.

Par exemple, l'entreprise peut définir que la voix utilise un chemin répondant à des critères de qualité et qu'un autre chemin soit sélectionné lorsque ces critères ne sont plus satisfaits.

Cette politique est différente d'une simple route IP. Elle porte sur les conditions dans lesquelles le trafic doit utiliser un chemin plutôt qu'un autre.

### Exemple

Une agence possède deux accès :

- Un circuit privé.
- Un accès Internet professionnel.

La voix doit utiliser un chemin qui satisfait les critères de performance définis. Les téléchargements ordinaires peuvent utiliser un accès différent selon les règles de l'entreprise.

Le SD-WAN peut mesurer les performances des liens et appliquer les politiques adaptées lorsque les conditions changent.

Il ne peut cependant pas créer une capacité inexistante. Si les deux liens sont saturés ou défaillants, aucune politique de sélection ne peut garantir une excellente qualité de service sans capacité ou chemin utilisable.

## 6. Objectifs habituels du SD-WAN

### Simplifier l'exploitation

Une gestion centralisée peut permettre de définir des paramètres et des politiques communes aux équipements.

Cette approche évite de devoir reproduire manuellement chaque règle sur chaque site, à condition que les équipements et les modèles de configuration soient correctement conçus.

### Utiliser plusieurs connexions

L'architecture peut exploiter plusieurs accès WAN plutôt que de réserver systématiquement un lien à une utilisation unique.

Cette possibilité dépend des politiques de trafic, des fonctionnalités de la plateforme et du type d'applications.

### Adapter les chemins aux besoins des applications

Les politiques peuvent prendre en compte des critères de qualité pour sélectionner un chemin.

Cette approche est particulièrement utile lorsque les applications présentent des exigences différentes.

### Améliorer la visibilité

Les solutions SD-WAN offrent généralement des mécanismes de supervision des tunnels, des équipements et des connexions.

Cette visibilité facilite le diagnostic, mais elle doit être complétée par la surveillance des applications et des services.

### Faciliter le déploiement des sites

L'intégration d'un nouveau site peut être simplifiée grâce à des modèles, à une gestion centralisée et à des procédures d'enregistrement des équipements.

Le degré d'automatisation du déploiement dépend cependant de la solution, de la préparation du site et des opérations nécessaires chez les fournisseurs d'accès.


# PARTIE 3 — COMPRENDRE L'UNDERLAY ET L'OVERLAY

## 7. L'underlay : le réseau de transport

L'underlay correspond aux réseaux IP ou aux services WAN qui assurent le transport des paquets entre les sites.

Il peut comprendre des liaisons Internet, des services MPLS, des connexions Ethernet ou des accès mobiles.

Son rôle est de fournir les chemins nécessaires à la communication entre les équipements SD-WAN.

L'underlay peut comporter plusieurs fournisseurs, plusieurs routes et plusieurs technologies de transport. Il n'est pas obligatoirement homogène.

Un accès Internet et un circuit privé peuvent fonctionner simultanément tout en présentant des caractéristiques différentes.

L'administrateur doit comprendre ces différences avant de définir les politiques d'utilisation.

## 8. L'overlay : le réseau logique SD-WAN

L'overlay représente les connexions logiques et sécurisées établies au-dessus du transport sous-jacent, selon les mécanismes de la solution SD-WAN.

Ces connexions peuvent utiliser des tunnels chiffrés entre les équipements de bordure.

Les réseaux locaux des différents sites peuvent alors échanger des données au moyen de cette architecture logique, sans que chaque flux applicatif doive être géré manuellement sur chaque connexion physique.

Un overlay peut utiliser plusieurs chemins underlay selon la conception et les politiques.

### Comprendre la relation

```text
                 OVERLAY SD-WAN
         Tunnels et politiques logiques
                       |
                       v
                 UNDERLAY WAN
          Internet / MPLS / 4G / 5G
                       |
                       v
              Réseaux des fournisseurs
```

L'overlay et l'underlay sont complémentaires.

Un tunnel peut être correctement défini dans la configuration, mais rester inutilisable si le réseau de transport ne permet pas de joindre sa destination.

De même, un underlay fonctionnel ne garantit pas que les tunnels, les routes de l'overlay ou les politiques applicatives sont corrects.

## 9. Pourquoi plusieurs underlays sont-ils utiles ?

Une entreprise peut utiliser plusieurs technologies de transport pour améliorer la disponibilité et adapter les coûts.

Par exemple, un lien privé peut constituer le chemin principal d'une application métier tandis qu'un accès Internet fournit une autre possibilité de transport.

L'intérêt dépend du comportement réel des liens.

Il ne suffit pas de posséder deux accès : il faut vérifier qu'ils sont suffisamment indépendants, qu'ils disposent d'une capacité adéquate et que les politiques permettent leur utilisation.

Deux connexions fournies par des opérateurs différents peuvent encore dépendre d'une même infrastructure physique dans certaines circonstances. La redondance doit donc être évaluée en fonction des risques réels.


# PARTIE 4 — IDENTIFIER LES COMPOSANTS D'UNE ARCHITECTURE SD-WAN

## 10. Les équipements SD-WAN de bordure

Les équipements de bordure, souvent appelés *WAN Edge*, se trouvent dans les agences, au siège, dans les centres de données ou dans les environnements cloud.

Ils assurent le traitement des paquets des utilisateurs et des applications.

Selon la plateforme, ils peuvent notamment réaliser :

- Le routage local.
- La classification du trafic.
- L'application des politiques.
- L'établissement et le maintien des tunnels.
- Le chiffrement des données transportées.
- La mesure des performances des chemins.
- Le choix du chemin de forwarding.
- La séparation des réseaux logiques.
- Certaines fonctions de pare-feu ou de qualité de service.

Tous les équipements n'offrent pas exactement les mêmes fonctions. Les capacités de sécurité, de routage et de performance doivent être vérifiées selon le produit choisi.

## 11. Le plan de gestion

Le plan de gestion permet d'administrer et de superviser la solution.

Il peut offrir une interface permettant de définir les politiques, préparer les modèles de configuration, visualiser l'état des équipements et consulter les résultats des contrôles.

Une gestion centralisée permet de modifier une politique une seule fois puis de la distribuer aux équipements concernés, selon les mécanismes de la plateforme.

Cette centralisation facilite l'exploitation, mais elle implique aussi de protéger l'accès au système de gestion.

Une erreur appliquée à un grand nombre de sites peut avoir un impact important. La validation des changements, la séparation des environnements et les mécanismes de retour arrière restent indispensables.

## 12. Le plan de contrôle

Le plan de contrôle transporte les informations nécessaires au fonctionnement logique du réseau.

Selon l'architecture, il peut distribuer des informations de reachability, de routage, de topologie et de politique entre les équipements.

Il permet de coordonner les décisions relatives aux chemins logiques et aux connexions sécurisées.

Il ne faut pas confondre le plan de contrôle avec le transport du trafic applicatif. Dans une architecture SD-WAN typique, les données des utilisateurs sont transmises par les équipements de bordure, tandis que les composants de contrôle distribuent les informations nécessaires au fonctionnement du réseau.

## 13. Le plan d'orchestration

L'orchestration facilite l'intégration initiale des équipements dans le système.

Elle peut notamment aider à reconnaître les équipements autorisés, à établir leur association avec les services de gestion et de contrôle et à préparer leur arrivée dans l'overlay.

Les mécanismes précis varient d'une plateforme à l'autre.

Certaines architectures disposent de composants distincts pour la gestion, le contrôle et l'orchestration. D'autres regroupent certaines de ces fonctions.

Il est donc préférable de comprendre les rôles logiques plutôt que de mémoriser les noms commerciaux d'une solution particulière.

## 14. Les différents plans ne remplissent pas le même rôle

| Fonction | Responsabilité principale |
|---|---|
| Gestion | Administrer, configurer et superviser les équipements |
| Orchestration | Faciliter l'enregistrement et l'intégration des équipements |
| Contrôle | Distribuer les informations nécessaires à la topologie, aux routes et aux politiques |
| Données | Transmettre le trafic applicatif selon l'état de forwarding et les politiques |

Cette séparation permet de comprendre plusieurs situations.

Une interface de gestion peut être indisponible alors que le trafic utilisateur continue de circuler grâce aux états déjà établis. À l'inverse, une perte du plan de contrôle peut empêcher l'établissement de nouveaux chemins ou la mise à jour des routes, même si certaines communications existantes continuent à fonctionner.

Le comportement exact dépend de la plateforme. Il doit être étudié dans la documentation de la solution retenue.


# PARTIE 5 — CONSTRUIRE LA TOPOLOGIE DE NOVATECH

## 15. L'entreprise utilisée dans les trois cours

NovaTech est une entreprise fictive qui possède quatre emplacements :

- Un siège social.
- Une agence A.
- Une agence B.
- Des services hébergés dans un environnement cloud.

Chaque agence possède un réseau local et doit accéder aux applications de l'entreprise.

Les agences disposent de plusieurs types de connexion WAN. La politique doit pouvoir adapter les chemins en fonction des applications et des performances des liens.

### Topologie logique

```text
                    SERVICES CLOUD
                          |
                          |
                    SIÈGE NOVATECH
                          |
                +---------+---------+
                |                   |
                v                   v
             AGENCE A            AGENCE B
```

Ce schéma montre les emplacements logiques, pas tous les tunnels ni tous les liens physiques.

Une topologie SD-WAN peut utiliser un modèle hub-and-spoke, dans lequel les agences communiquent principalement via un point central, ou des connexions directes entre les sites lorsque les politiques et la plateforme le prévoient.

Le choix dépend des flux applicatifs, des besoins de sécurité, du nombre de sites et des capacités de l'architecture.

## 16. Les connexions de chaque site

Pour le laboratoire conceptuel, chaque agence dispose de deux accès WAN.

Le premier peut représenter un circuit privé. Le second représente un accès Internet professionnel.

Le siège possède également une connectivité permettant aux agences de joindre les services centraux.

Les accès sont présentés de manière abstraite afin que le même scénario puisse être réutilisé avec différents équipements lors du niveau intermédiaire.

```text
AGENCE A                     AG ENCE B
   |                             |
   +-- Circuit privé             +-- Circuit privé
   +-- Internet                  +-- Internet
             \                   /
              \                 /
               \               /
                RÉSEAU WAN
                    |
                    v
                 SIÈGE
                    |
                    v
             SERVICES INTERNES
```

Les deux accès d'une agence ne garantissent pas une redondance complète si leurs chemins physiques ou leurs points de défaillance sont communs.

Une conception sérieuse doit examiner les fournisseurs, les infrastructures, l'alimentation électrique, les équipements et les dépendances de transport.

## 17. Les sites ne doivent pas nécessairement partager le même plan physique

Le SD-WAN permet de construire une connectivité logique qui ne dépend pas uniquement de la topologie physique.

Deux agences peuvent communiquer au moyen de tunnels logiques, même si leurs paquets traversent des réseaux de fournisseurs différents.

Cette indépendance est l'un des avantages de l'overlay.

Cependant, le transport sous-jacent reste essentiel : ses routes doivent permettre de joindre les points de terminaison et les tunnels doivent être autorisés et opérationnels.


# PARTIE 6 — COMPRENDRE LES TUNNELS SÉCURISÉS

## 18. Pourquoi créer un tunnel ?

Un tunnel permet de transporter du trafic à travers un réseau intermédiaire en utilisant une encapsulation spécifique.

Dans une solution SD-WAN, les tunnels peuvent relier des équipements de bordure entre eux et transporter les données des sites.

Lorsqu'une solution utilise IPsec, les données transportées bénéficient des propriétés cryptographiques prévues par les mécanismes configurés.

Le fait de parler de SD-WAN ne signifie toutefois pas que tous les produits utilisent exactement le même protocole de tunnel ou le même modèle de sécurité.

Les paramètres de chiffrement, l'authentification, les mécanismes de gestion des clés et les comportements de reprise dépendent de l'implémentation.

## 19. Exemple de tunnel entre deux agences

Imaginons que l'agence A doive envoyer un paquet vers une application située au siège.

Le routeur SD-WAN de l'agence identifie le trafic, détermine la politique applicable et transmet le paquet vers un chemin autorisé.

Si le chemin utilise un tunnel sécurisé, le paquet est encapsulé et protégé conformément à la configuration de la solution.

Le transport underlay achemine ensuite le paquet extérieur vers le point de terminaison distant, qui traite le tunnel et transmet le trafic vers son réseau de destination.

Cette opération permet de séparer le transport physique de la connectivité logique des sites.

## 20. Que protège le chiffrement ?

Lorsque le tunnel utilise correctement un mécanisme de chiffrement, les données transportées sont protégées selon les propriétés du protocole choisi.

Le chiffrement du tunnel ne signifie pas que l'ensemble de l'infrastructure est sécurisé.

Il reste nécessaire de contrôler :

- Les identités des équipements.
- Les droits d'administration.
- Les flux autorisés entre les réseaux.
- Les règles de pare-feu.
- Les logiciels et leurs mises à jour.
- Les clés et les paramètres cryptographiques.
- La surveillance des événements.

Un tunnel correctement chiffré peut transporter un trafic non souhaité si les politiques de sécurité autorisent une communication qui ne devrait pas l'être.

## 21. Établissement d'un tunnel

La création d'un tunnel sécurisé exige plusieurs conditions.

Les équipements doivent pouvoir atteindre les destinations de transport, être authentifiés selon la solution retenue et disposer de paramètres compatibles.

Ils doivent également connaître les routes ou les informations de forwarding nécessaires au trafic qui empruntera le tunnel.

Une configuration peut donc présenter un tunnel établi sans que les communications applicatives fonctionnent correctement.

Il est nécessaire de vérifier les routes, les politiques et les tests de bout en bout après l'établissement de la connectivité logique.


# PARTIE 7 — COMPRENDRE LES POLITIQUES APPLICATIVES

## 22. Pourquoi la sélection de chemin est-elle importante ?

Un réseau WAN peut disposer de plusieurs chemins possibles entre les sites.

Ces chemins ne présentent pas nécessairement les mêmes performances à un instant donné.

Un lien peut posséder une latence faible mais une capacité limitée. Un autre peut offrir davantage de bande passante mais subir des pertes de paquets. Un troisième peut être adapté au trafic de secours sans être souhaitable pour les applications sensibles.

Le SD-WAN peut comparer les chemins aux exigences définies pour les applications.

La sélection peut utiliser des critères de disponibilité, de latence, de gigue, de pertes, de capacité ou d'autres mesures prises en charge par la solution.

Les politiques doivent être construites à partir des objectifs opérationnels, et non de l'idée abstraite qu'un type de connexion est toujours meilleur qu'un autre.

## 23. Classification applicative

La classification consiste à déterminer à quelle application ou catégorie appartient le trafic.

Selon la plateforme et les fonctions disponibles, cette classification peut utiliser les adresses, les ports, les protocoles, des signatures applicatives ou d'autres mécanismes.

La classification n'est pas toujours parfaite. Des applications peuvent utiliser des ports partagés, des protocoles chiffrés ou des services hébergés derrière des infrastructures communes.

L'administrateur doit comprendre comment la plateforme identifie les applications, quelles limites elle possède et ce qui se produit lorsqu'un flux ne peut pas être classé avec suffisamment de certitude.

## 24. Exemple de politique applicative

NovaTech possède trois catégories de trafic :

- La voix et la visioconférence.
- Les applications métier.
- Les transferts de fichiers ordinaires.

La voix est sensible à la latence, à la gigue et aux pertes. L'application métier peut exiger un chemin stable et une disponibilité élevée. Les transferts de fichiers peuvent utiliser un chemin moins prioritaire si la capacité disponible reste suffisante.

La politique ne doit pas se limiter à dire « voix = circuit privé ». Elle doit préciser les conditions que le circuit doit satisfaire et ce qui se produit lorsque ces conditions ne sont plus réunies.

Cette approche permet de choisir un chemin en fonction de son état réel lorsque la plateforme possède les fonctions nécessaires.


# PARTIE 8 — COMPRENDRE LES MÉTRIQUES DE PERFORMANCE

## 25. La latence

La latence représente le délai de transport d'un paquet entre deux points.

Elle peut être mesurée dans un sens ou par un aller-retour selon la méthode utilisée.

Une latence élevée augmente le temps de réaction des applications interactives. Les conversations vocales et la visioconférence deviennent plus difficiles lorsque le délai global dépasse les objectifs retenus.

La latence dépend notamment de la distance, du chemin, des files d'attente, du traitement des équipements et de la charge du réseau.

Un accès plus coûteux n'est pas automatiquement plus rapide pour toutes les destinations.

## 26. La gigue

La gigue décrit les variations du délai des paquets.

Pour une application temps réel, un délai stable peut être préférable à un délai qui varie fortement.

Par exemple, si des paquets vocaux arrivent avec des délais très différents, l'application doit gérer ces variations avec ses mécanismes de tampon et de lecture.

Une gigue importante peut provoquer une restitution moins fluide, même si la latence moyenne semble acceptable.

## 27. La perte de paquets

La perte de paquets désigne la proportion de paquets envoyés qui n'atteignent pas leur destination dans le contexte de mesure considéré.

Elle peut provenir de files d'attente saturées, d'erreurs de transmission, d'une panne de chemin, d'un filtrage ou d'autres conditions.

La perte peut fortement dégrader les applications temps réel et ralentir certains transferts utilisant TCP.

Elle doit être mesurée dans un contexte précis : direction du trafic, intervalle de temps, chemin et point de mesure.

## 28. La bande passante et le débit utile

La bande passante représente la capacité théorique ou disponible du lien selon la convention utilisée.

Le débit utile représente la quantité de données applicatives effectivement transportée pendant une durée donnée.

Ces deux notions ne sont pas identiques.

Un lien de grande capacité peut fournir un débit utile faible si le trafic est perdu, si les files sont saturées ou si d'autres contraintes limitent le flux.

À l'inverse, une application qui échange très peu de données peut fonctionner correctement sur un lien à capacité limitée si ses exigences de performance sont satisfaites.

## 29. Pourquoi utiliser plusieurs mesures ?

Aucune métrique ne suffit à elle seule à caractériser la qualité d'un chemin.

La latence ne révèle pas nécessairement les pertes. La bande passante annoncée ne garantit pas que la capacité est disponible. La gigue peut varier au cours de la journée. Les mesures dépendent également du sens du trafic.

Une politique SD-WAN doit donc sélectionner les critères qui correspondent réellement au besoin applicatif.

Un seuil trop strict peut déclencher des basculements fréquents. Un seuil trop permissif peut laisser une application sur un chemin dégradé.

Le choix des seuils doit être justifié par les exigences du service et validé par des mesures du réseau.


# PARTIE 9 — COMPRENDRE LE SLA ET LES SEUILS

## 30. Qu'est-ce qu'un seuil de performance ?

Un seuil de performance exprime une limite ou une condition que le chemin doit respecter.

Par exemple, l'entreprise peut définir un objectif de latence maximale pour la voix, un objectif de pertes de paquets et un niveau de disponibilité nécessaire.

Les valeurs doivent être choisies selon l'application, les exigences métier et la méthode de mesure.

Il n'existe pas un jeu de seuils qui conviendrait à toutes les entreprises ou à toutes les technologies.

## 31. Exemple pédagogique de critères

Pour illustrer une politique, NovaTech définit les objectifs fictifs suivants pour sa voix :

- Latence mesurée inférieure ou égale à 100 ms.
- Perte de paquets inférieure ou égale à 1 %.
- Gigue inférieure ou égale à 30 ms.

Ces valeurs sont des exemples destinés aux exercices. Elles ne constituent pas une recommandation universelle pour toute application vocale.

Le réseau pourra considérer un chemin comme satisfaisant cette politique uniquement si les métriques sont mesurées de façon cohérente et si les autres conditions nécessaires sont remplies.

## 32. Que se passe-t-il si un seuil est dépassé ?

Lorsqu'un chemin ne satisfait plus la politique, l'équipement peut sélectionner un autre chemin si un chemin de remplacement est disponible et autorisé.

Cependant, la transition peut dépendre des mécanismes de mesure, des délais de détection, des règles de sélection et des capacités de la solution.

La sélection ne doit pas être comprise comme un changement instantané qui se produit sans délai ni interruption.

Il faut aussi prendre en compte le risque de basculement fréquent lorsque les mesures se situent près du seuil.

## 33. Pourquoi les seuils doivent-ils être validés ?

Des seuils trop stricts peuvent conduire le réseau à alterner entre plusieurs liens dont la qualité varie légèrement.

Des seuils trop permissifs peuvent empêcher un basculement alors que l'application est dégradée.

L'administrateur doit aussi vérifier que le chemin de secours possède une capacité suffisante.

Un lien peut respecter les critères de latence lorsqu'il transporte peu de trafic, puis devenir saturé une fois que plusieurs applications y sont redirigées.

Une politique efficace doit donc considérer la capacité, les dépendances et les conséquences du basculement.


# PARTIE 10 — DIFFÉRENCE ENTRE BASCULEMENT ET SÉLECTION DYNAMIQUE

## 34. Le basculement classique

Dans un mécanisme de secours classique, un chemin principal est utilisé tant qu'il reste disponible selon les critères de détection définis.

Lorsque ce chemin devient indisponible, le trafic est transféré vers un chemin de secours.

Ce mécanisme peut être parfaitement adapté à des exigences simples de disponibilité.

Toutefois, tant que le lien principal reste techniquement disponible, il peut continuer à être utilisé même si ses performances sont devenues insuffisantes pour une application sensible.

Cela dépend des mécanismes de détection et des politiques de routage en place.

## 35. La sélection dynamique des chemins

Dans une approche SD-WAN fondée sur les politiques, plusieurs chemins peuvent rester disponibles simultanément.

Le système peut évaluer leurs mesures et sélectionner le chemin qui respecte le mieux les critères définis pour l'application.

Cette logique peut conduire à utiliser un autre lien sans attendre une panne complète du premier.

La possibilité de changer le chemin, la fréquence de mesure, les conditions de sélection et la granularité de décision dépendent de la solution.

## 36. Exemple

Supposons que le circuit privé reste opérationnel mais que la gigue augmente au point de dépasser le seuil retenu pour la voix.

Un mécanisme de basculement fondé uniquement sur l'état de l'interface peut ne pas considérer le circuit comme en panne.

Une politique SD-WAN qui mesure la gigue peut, si elle est configurée pour cela, décider d'utiliser un autre chemin dont les caractéristiques satisfont mieux les exigences.

Cette sélection reste conditionnée par la disponibilité et les performances du chemin alternatif.

Le comportement doit être testé plutôt que supposé.


# PARTIE 11 — INTERNET BREAKOUT ET ACCÈS AUX APPLICATIONS CLOUD

## 37. Pourquoi faire sortir directement le trafic Internet ?

Dans certaines architectures WAN traditionnelles, le trafic Internet des agences transite d'abord par le siège ou par un centre de données, où il est filtré avant de sortir vers Internet.

Cette organisation peut faciliter une politique de sécurité centralisée, mais elle peut aussi créer un détour pour les applications hébergées dans le cloud.

Lorsque le trafic doit parcourir un chemin long avant d'atteindre sa destination, la latence peut augmenter et les liens centraux peuvent être davantage sollicités.

Le SD-WAN peut permettre une sortie Internet directe depuis une agence, souvent appelée *direct Internet access* ou *Internet breakout*, si la solution et les politiques de sécurité le permettent.

Cette approche permet à certains flux d'accéder directement à Internet plutôt que de passer systématiquement par le site central.

## 38. Exemple de sortie Internet centralisée

```text
AGENCE
   |
   v
TUNNEL WAN VERS LE SIÈGE
   |
   v
SIÈGE / PARE-FEU CENTRAL
   |
   v
INTERNET
```

Cette architecture permet de centraliser certaines fonctions de sécurité, mais elle peut entraîner un détour pour les applications qui n'ont pas besoin de joindre les systèmes internes.

Le résultat dépend notamment de la capacité du siège, de la distance au service cloud et des politiques de routage.

## 39. Exemple de sortie Internet directe

```text
AGENCE
   |
   +---- Trafic interne
   |          |
   |          v
   |      Overlay SD-WAN
   |          |
   |          v
   |       SIÈGE
   |
   +---- Trafic Internet
              |
              v
        Sécurité locale
              |
              v
           INTERNET
```

Dans cette architecture, les flux Internet autorisés peuvent sortir directement de l'agence, tandis que les flux destinés aux applications internes utilisent l'overlay.

Le point essentiel n'est pas de choisir automatiquement la sortie directe. Il faut définir quels flux sont concernés et quels contrôles de sécurité doivent être appliqués à cet emplacement.

## 40. Les risques d'une sortie directe

Une sortie Internet directe modifie le chemin du trafic et peut modifier l'endroit où les politiques de sécurité sont appliquées.

Il faut vérifier :

- Le filtrage local.
- La protection contre les menaces.
- Les politiques DNS.
- Les contrôles d'identité.
- Les règles d'accès aux applications.
- Les exigences de journalisation.
- Les mécanismes de protection des données.

Une sortie directe mal contrôlée peut contourner certaines protections prévues au siège.

Il faut donc évaluer la sécurité de l'agence avant de modifier le chemin d'accès à Internet.


# PARTIE 12 — SEGMENTATION ET SÉCURITÉ

## 41. Pourquoi segmenter un réseau SD-WAN ?

La segmentation permet de séparer logiquement différents types de trafic ou différents groupes d'utilisateurs.

Une entreprise peut souhaiter distinguer :

- Le réseau des employés.
- Les équipements de gestion.
- Les systèmes de paiement.
- Les terminaux invités.
- Les équipements industriels.
- Les systèmes sensibles.

La segmentation limite les possibilités de communication et contribue à appliquer des politiques adaptées à chaque domaine.

Les mécanismes précis varient selon les solutions : VRF, segments logiques, domaines de routage ou autres fonctions de séparation peuvent être utilisés.

## 42. Exemple de segmentation

NovaTech sépare les utilisateurs, les serveurs et les équipements de gestion.

Les trois catégories ne doivent pas communiquer librement uniquement parce qu'elles sont connectées au même WAN.

Chaque segment possède des règles d'accès adaptées à ses besoins.

L'accès d'un utilisateur à une application métier peut être autorisé, tandis que l'accès direct au réseau de gestion peut être interdit.

Le SD-WAN peut participer à l'application de ces politiques selon ses fonctions, mais celles-ci doivent être complétées par les contrôles nécessaires sur les LAN, les serveurs et les pare-feu.

## 43. Le chiffrement des tunnels

Les tunnels SD-WAN peuvent utiliser IPsec ou d'autres mécanismes de protection selon la plateforme.

L'objectif est de protéger le trafic qui circule entre les points de terminaison.

Il faut cependant vérifier les paramètres réellement utilisés : algorithmes, authentification, gestion des clés, suites cryptographiques et politiques de renouvellement.

Le terme SD-WAN ne signifie pas que toutes les solutions utilisent exactement le même protocole ou le même mécanisme de gestion des clés.

## 44. Le SD-WAN n'est pas un remplacement complet du pare-feu

Un SD-WAN peut intégrer certaines fonctions de sécurité et s'associer à des systèmes de pare-feu ou à des services de sécurité cloud.

Toutefois, le routage intelligent et la sélection de chemin ne constituent pas à eux seuls une politique de sécurité complète.

Les contrôles doivent répondre à des questions distinctes :

- Qui peut se connecter ?
- Vers quelles applications ?
- Depuis quel site ?
- Sur quels chemins ?
- Avec quelles protections ?
- Quelles communications doivent être enregistrées ?
- Que se passe-t-il lorsque le système de sécurité est indisponible ?

Ces questions doivent être traitées dans la conception globale du réseau.


# PARTIE 13 — QUALITÉ DE SERVICE ET CAPACITÉ DES LIENS

## 45. Pourquoi la QoS reste-t-elle importante ?

La QoS (*Quality of Service*) désigne les mécanismes qui permettent de traiter différemment les flux en fonction de leurs priorités ou de leurs exigences.

Même si un SD-WAN peut sélectionner un chemin en fonction de sa qualité, il doit également gérer la congestion qui apparaît sur les liens utilisés.

Un chemin peut être performant à faible charge et se dégrader lorsque plusieurs applications envoient du trafic simultanément.

Les mécanismes de mise en file, de priorisation, de limitation et de gestion de congestion peuvent alors être nécessaires.

La capacité réelle de la QoS dépend des équipements, des politiques et du comportement des fournisseurs de transport.

## 46. Prioriser les applications

NovaTech peut donner une priorité supérieure à la voix et à la visioconférence par rapport aux transferts de fichiers non urgents.

Cette politique ne signifie pas que les autres applications doivent être systématiquement bloquées.

Elle définit plutôt un ordre de traitement sous certaines conditions, notamment lorsque la capacité devient insuffisante.

Il faut éviter d'appliquer une priorité élevée à trop de catégories, car cela réduit l'efficacité de la différenciation.

La classification doit également être fiable. Une mauvaise classification peut attribuer une priorité excessive à un flux qui ne devrait pas en bénéficier.

## 47. Capacité du lien de secours

Un lien de secours doit être dimensionné selon le trafic qui pourrait y basculer.

Si une agence possède un circuit principal de grande capacité et un accès mobile plus limité, celui-ci peut être suffisant pour certaines applications mais pas pour toutes les applications simultanément.

La politique doit alors définir les flux essentiels et les conditions d'utilisation du lien de secours.

Le basculement ne crée pas de capacité supplémentaire. Lorsque la demande dépasse la capacité disponible, il faut soit limiter certains usages, soit augmenter les ressources, soit accepter une dégradation prévue et documentée.


# PARTIE 14 — SUPERVISION ET DIAGNOSTIC

## 48. Pourquoi mesurer en permanence ?

La sélection dynamique des chemins dépend des informations disponibles au moment de la décision.

La supervision sert à connaître l'état des équipements, des connexions et des tunnels, ainsi que les performances des chemins.

Elle peut également aider à identifier les causes d'un problème applicatif.

Les données pertinentes comprennent notamment :

- L'état des interfaces.
- La disponibilité des tunnels.
- La latence.
- La gigue.
- Les pertes de paquets.
- Le débit.
- Les changements de chemin.
- Les erreurs d'authentification.
- Les événements de routage.
- Les anomalies de sécurité.

La collecte de ces données doit tenir compte des limites des méthodes de mesure et des capacités de la plateforme.

## 49. Dépanner par couches

Lorsque l'utilisateur d'une agence signale une application lente, il ne faut pas immédiatement conclure que le SD-WAN a mal choisi le chemin.

Le problème peut provenir du LAN, du fournisseur d'accès, du tunnel, du routage, de l'application distante ou du serveur.

Une démarche structurée permet de localiser la première couche dont le comportement ne correspond plus aux attentes.

### Ordre de diagnostic

```text
Application
    |
    v
LAN local
    |
    v
Routeur SD-WAN
    |
    v
Underlay WAN
    |
    v
Tunnel / Overlay
    |
    v
Réseau distant
    |
    v
Serveur ou application cible
```

Cet ordre est un modèle de raisonnement. Les observations peuvent conduire à examiner directement une autre couche lorsqu'une preuve permet de localiser la panne.

## 50. Cas de diagnostic : tunnel indisponible

Si le tunnel est indisponible, l'administrateur doit vérifier les éléments suivants :

1. Les interfaces WAN sont-elles opérationnelles ?
2. Les adresses de transport sont-elles correctement configurées ?
3. Les destinations nécessaires sont-elles joignables ?
4. L'authentification des équipements fonctionne-t-elle ?
5. Les paramètres de sécurité sont-ils compatibles ?
6. Les règles de filtrage permettent-elles le trafic requis ?
7. Les composants de contrôle échangent-ils les informations attendues ?
8. Le tunnel est-il correctement établi ?
9. Les routes de l'overlay sont-elles installées ?

La dernière étape est importante : un tunnel actif ne garantit pas nécessairement que les bonnes routes sont présentes.

## 51. Cas de diagnostic : application lente

Lorsqu'un tunnel est établi mais qu'une application fonctionne mal, il faut examiner les performances des chemins et les mesures applicables à cette application.

L'administrateur doit vérifier si le chemin sélectionné respecte les seuils définis, si le lien est saturé et si les paquets subissent des pertes ou des variations de délai.

Il faut aussi examiner le chemin retour, car une communication peut être dégradée lorsque les chemins aller et retour présentent des caractéristiques différentes.

Enfin, il est nécessaire de distinguer un problème WAN d'un problème du serveur ou du service applicatif.


# PARTIE 15 — LABORATOIRE CONCEPTUEL NOVATECH

## 52. Mission

Le laboratoire du niveau débutant consiste à concevoir une politique SD-WAN et à expliquer ses effets avant de passer à la configuration réelle au niveau intermédiaire.

NovaTech possède :

- Un siège.
- Deux agences.
- Deux accès WAN par agence.
- Des applications métier centrales.
- Un service de voix et de visioconférence.
- Des applications Internet et cloud.

L'apprenant doit définir des règles qui prennent en compte les exigences applicatives, la disponibilité et la sécurité.

## 53. Plan de connectivité

Pour simplifier l'étude, nous considérons :

| Site | Accès principal | Accès alternatif |
|---|---|---|
| Siège | Circuit privé | Internet professionnel |
| Agence A | Circuit privé | Internet |
| Agence B | Internet professionnel | Connexion mobile |
| Services cloud | Connectivité du fournisseur | Chemin alternatif selon l'architecture |

Cette table est illustrative. Elle ne constitue pas une recommandation universelle sur les types de liens à choisir.

Le choix dépend de la capacité, du coût, de la disponibilité, de la couverture mobile, des applications et du modèle de service.

## 54. Définir les politiques

L'apprenant doit définir trois politiques conceptuelles.

**Politique A — Voix et visioconférence**

Le trafic doit utiliser un chemin autorisé qui respecte les critères de latence, de gigue et de perte définis par l'entreprise. Si le chemin courant se dégrade, l'équipement peut utiliser une autre possibilité qui satisfait les mêmes exigences, lorsqu'elle existe.

**Politique B — Applications métier**

Le trafic vers les applications centrales doit utiliser les chemins autorisés vers le siège ou le centre de données. La disponibilité de l'application doit être vérifiée indépendamment du statut du tunnel.

**Politique C — Accès Internet**

Les flux Internet autorisés peuvent utiliser une sortie directe depuis l'agence si le modèle de sécurité le permet. Les flux internes doivent rester dirigés vers les destinations internes prévues.

## 55. Tableau de décision

| Situation | Décision conceptuelle | Vérification nécessaire |
|---|---|---|
| Le chemin principal respecte tous les seuils | Continuer à utiliser le chemin choisi | Confirmer que les autres critères sont satisfaits |
| La latence dépasse le seuil mais un chemin alternatif respecte les règles | Sélectionner le chemin alternatif si la politique le permet | Vérifier la disponibilité et la capacité |
| Tous les chemins autorisés sont dégradés | Appliquer la politique de dégradation ou de priorité prévue | Éviter de déclarer un chemin acceptable sans preuve |
| Le tunnel fonctionne mais l'application ne répond pas | Diagnostiquer le routage et le service distant | Contrôler le chemin de bout en bout |
| Le service de sécurité local devient indisponible | Appliquer la politique de sécurité prévue | Ne pas autoriser automatiquement tous les flux |

Cette table décrit une logique de décision. Elle ne prétend pas représenter le comportement exact d'un produit donné.


# PARTIE 16 — EXERCICES CORRIGÉS

## 56. Exercice 1 — Définition du SD-WAN

**Question :** quelle différence existe entre un WAN traditionnel et une architecture SD-WAN ?

### Correction

Le WAN traditionnel s'appuie principalement sur les connexions de transport et les mécanismes de routage configurés pour relier les sites.

Le SD-WAN ajoute une couche de gestion logicielle et de politiques qui peut contrôler plus dynamiquement les chemins utilisés par les applications.

Les fonctions précises dépendent de la plateforme. Un réseau traditionnel peut lui aussi disposer de redondance, de supervision et de mécanismes de routage avancés.

Le SD-WAN n'est donc pas une opposition absolue au WAN traditionnel, mais une approche d'architecture et d'exploitation.

## 57. Exercice 2 — Underlay et overlay

**Question :** pourquoi un tunnel SD-WAN peut-il être indisponible alors que l'accès Internet fonctionne ?

### Correction

L'accès Internet peut être opérationnel sans que l'overlay soit fonctionnel.

Le tunnel peut rencontrer un problème d'authentification, de paramètres de sécurité, de filtrage ou de configuration. Le plan de contrôle peut aussi ne pas fournir les informations nécessaires à son établissement.

Il faut distinguer l'état de l'accès WAN de l'état du tunnel et des routes de l'overlay.

## 58. Exercice 3 — Sélection applicative

**Question :** pourquoi une application vocale ne doit-elle pas nécessairement suivre exactement la même politique qu'un transfert de fichiers ?

### Correction

La voix est sensible à la latence, à la gigue et aux pertes de paquets. Un transfert de fichiers peut être davantage dépendant de la capacité et de la durée totale du transfert.

Une politique distincte permet de définir des critères adaptés à chaque catégorie. Les seuils et les décisions doivent toutefois être mesurés, justifiés et validés dans le contexte réel.

## 59. Exercice 4 — Perte de qualité

**Question :** le circuit principal fonctionne encore, mais la qualité de la voix est devenue insuffisante. Que peut apporter le SD-WAN ?

### Correction

Si la plateforme mesure les performances du chemin et prend en charge une sélection fondée sur ces mesures, une politique peut choisir un autre chemin qui respecte les critères de qualité.

Cette décision doit être testée. La présence d'un lien alternatif ne garantit pas que celui-ci possède assez de capacité ou qu'il fournit de meilleures performances.

## 60. Exercice 5 — Sortie Internet directe

**Question :** quel est l'intérêt d'une sortie Internet directe dans une agence ?

### Correction

Elle peut éviter que certains flux Internet transitent inutilement par le siège avant de rejoindre leur destination.

Elle peut réduire certains détours et la charge du réseau central.

Cette approche nécessite toutefois des contrôles de sécurité adaptés à l'agence, notamment pour le filtrage et l'application des politiques d'accès.

## 61. Exercice 6 — Tunnel établi

**Question :** un tunnel est actif entre une agence et le siège, mais l'application métier ne répond pas. Quelle conclusion faut-il tirer ?

### Correction

La connectivité du tunnel ne prouve pas que l'application est accessible.

Il faut vérifier les routes, les politiques, le segment réseau, le pare-feu, le chemin retour et l'état du service distant.

Le diagnostic doit identifier la première couche dont le comportement est incorrect.

## 62. Exercice 7 — Liens multiples

**Question :** une agence possède deux liens WAN. Est-ce suffisant pour garantir la haute disponibilité ?

### Correction

Non.

Il faut vérifier que les chemins sont réellement utilisables, que leur indisponibilité peut être détectée et que les politiques autorisent le basculement.

Il faut également tenir compte des dépendances communes, de la capacité du lien alternatif et des éventuelles interruptions pendant le basculement.

## 63. Exercice 8 — Mesures de performance

**Question :** pourquoi la bande passante ne suffit-elle pas à choisir un chemin pour toutes les applications ?

### Correction

La bande passante représente une capacité de transport, mais elle ne décrit pas à elle seule la latence, la gigue ou les pertes.

Une application temps réel peut préférer un chemin de capacité plus limitée si ses critères de performance sont satisfaits.

Le choix doit être lié aux besoins de l'application et à l'état mesuré du chemin.


# PARTIE 17 — ERREURS FRÉQUENTES

## 64. Confondre SD-WAN et accès Internet

Un accès Internet peut servir d'underlay, mais il ne constitue pas à lui seul une architecture SD-WAN.

**Bonne pratique :** distinguer la connexion de transport des fonctions de tunnel, de contrôle, de gestion et de politique.

## 65. Penser que le SD-WAN supprime le besoin de routage

Les équipements doivent toujours disposer d'informations de forwarding et de routes appropriées.

Le SD-WAN peut automatiser ou distribuer certaines décisions, mais il ne rend pas le routage inutile.

## 66. Croire que deux liens garantissent la continuité

Un lien secondaire peut être sous-dimensionné, mal configuré ou dépendre d'une infrastructure similaire au lien principal.

**Bonne pratique :** tester réellement le comportement du réseau lors d'une défaillance et vérifier la capacité résiduelle.

## 67. Considérer un tunnel actif comme une preuve de fonctionnement applicatif

Le tunnel peut être établi alors que les routes, les politiques ou les services ne fonctionnent pas correctement.

**Bonne pratique :** combiner la supervision des tunnels avec les tests réseau et applicatifs de bout en bout.

## 68. Utiliser des seuils arbitraires

Une politique trop stricte peut provoquer des changements incessants de chemin. Une politique trop permissive peut maintenir le trafic sur un lien dégradé.

**Bonne pratique :** utiliser des objectifs justifiés par les besoins de l'application et les valider avec des mesures.

## 69. Oublier la sécurité de la sortie Internet

Une sortie directe peut modifier les points où le trafic est filtré.

**Bonne pratique :** vérifier que les contrôles nécessaires restent appliqués au nouvel emplacement.

## 70. Confondre gestion centralisée et fonctionnement centralisé

La gestion peut être centralisée tandis que le trafic est transmis directement entre des équipements de bordure.

**Bonne pratique :** distinguer les composants de gestion et de contrôle des équipements qui transportent effectivement les paquets.


# PARTIE 18 — GLOSSAIRE

## 71. Termes essentiels

**WAN — Wide Area Network :** réseau reliant plusieurs emplacements géographiquement séparés.

**SD-WAN — Software-Defined Wide Area Network :** approche logicielle de gestion et de pilotage du réseau WAN à l'aide de politiques.

**Underlay :** réseau ou service de transport sous-jacent utilisé pour acheminer les paquets.

**Overlay :** réseau logique construit au-dessus de l'underlay, notamment au moyen de tunnels.

**WAN Edge :** équipement situé à la bordure d'un site ou d'un environnement cloud et chargé de la connectivité WAN.

**Plan de gestion :** fonctions utilisées pour administrer, configurer et superviser la solution.

**Plan de contrôle :** fonctions qui distribuent les informations nécessaires aux routes, à la topologie et aux politiques.

**Plan de données :** fonctions qui transmettent effectivement le trafic des utilisateurs et des applications.

**Orchestration :** fonctions facilitant notamment l'enregistrement, l'intégration et la préparation des équipements.

**Tunnel :** mécanisme d'encapsulation permettant de transporter le trafic à travers un réseau intermédiaire.

**IPsec :** ensemble de mécanismes de sécurité IP pouvant notamment fournir un transport protégé pour les tunnels.

**Latence :** délai de transport d'un paquet entre deux points, mesuré selon une méthode définie.

**Gigue :** variation des délais des paquets dans le temps.

**Perte de paquets :** proportion de paquets qui n'atteignent pas leur destination dans le contexte de mesure.

**Bande passante :** capacité de transport du lien selon la métrique utilisée.

**Débit utile :** quantité de données utiles transportées par unité de temps.

**QoS — Quality of Service :** mécanismes qui permettent de différencier le traitement du trafic selon les priorités et les exigences.

**SLA — Service Level Agreement :** engagement de niveau de service, défini selon un ensemble de paramètres et de conditions convenus.

**Internet breakout :** sortie directe de certains flux vers Internet depuis un site, au lieu de faire transiter tout le trafic par un site central.

**Segmentation :** séparation logique des réseaux ou des groupes de trafic selon une politique.

**Basculement :** transfert du trafic vers un autre chemin lorsque certaines conditions sont réunies.

**Classification applicative :** mécanisme utilisé pour identifier le type d'application ou la catégorie d'un flux.


# PARTIE 19 — ÉVALUATION DE FIN DE NIVEAU

## 72. Questions théoriques

L'apprenant doit répondre aux questions suivantes sans consulter le cours.

1. Quel est le rôle du WAN dans une entreprise multisite ?
2. Quelle différence existe entre un WAN traditionnel et le SD-WAN ?
3. Pourquoi le SD-WAN ne remplace-t-il pas l'underlay ?
4. Quelle différence existe entre underlay et overlay ?
5. Quel est le rôle d'un équipement WAN Edge ?
6. Quelle différence existe entre les plans de gestion, de contrôle et de données ?
7. Pourquoi utiliser plusieurs accès WAN ?
8. Quel est le rôle d'un tunnel sécurisé ?
9. Pourquoi un tunnel actif ne prouve-t-il pas que l'application fonctionne ?
10. Pourquoi la classification applicative est-elle importante ?
11. Quelle est la différence entre latence, gigue et perte de paquets ?
12. Pourquoi la bande passante ne suffit-elle pas pour caractériser la qualité d'un lien ?
13. Quelle différence existe entre basculement classique et sélection dynamique des chemins ?
14. Quel est l'intérêt d'un Internet breakout ?
15. Quels contrôles de sécurité doivent être examinés avant une sortie Internet directe ?
16. Pourquoi la QoS reste-t-elle importante dans un réseau SD-WAN ?
17. Comment identifier une panne d'underlay ?
18. Comment identifier une panne d'overlay ?
19. Pourquoi deux liens WAN ne garantissent-ils pas automatiquement la disponibilité ?
20. Quels sont les objectifs du laboratoire NovaTech ?

## 73. Travaux pratiques conceptuels

### Travail 1 — Dessiner l'architecture

Représentez le siège et les deux agences de NovaTech.

Faites apparaître les deux accès WAN de chaque agence, les équipements SD-WAN et les applications centrales.

Précisez les rôles des liens et les chemins envisagés pour la voix, les applications métier et Internet.

### Travail 2 — Définir une politique de voix

Définissez les critères de sélection d'un chemin pour la voix.

Précisez les métriques surveillées, les seuils choisis et le comportement attendu si aucun chemin ne respecte les objectifs.

### Travail 3 — Analyser une panne

Supposez que le tunnel de l'agence A vers le siège est actif, mais que les utilisateurs ne peuvent plus joindre l'application métier.

Rédigez une méthode de diagnostic permettant de distinguer un problème d'overlay, de routage, de filtrage ou de service applicatif.

### Travail 4 — Concevoir une sortie Internet directe

Définissez les flux autorisés à sortir directement depuis l'agence.

Indiquez les contrôles de sécurité, les règles de filtrage et les mécanismes de journalisation qui doivent être disponibles.

### Travail 5 — Tester la redondance

Décrivez un test contrôlé de perte du lien principal.

Précisez les mesures à enregistrer, les applications à surveiller et les éléments permettant de vérifier que le chemin alternatif respecte les exigences.


# PARTIE 20 — PRÉPARER LE NIVEAU INTERMÉDIAIRE

## 74. Ce qui est maintenant acquis

Le niveau débutant a permis d'identifier les limites d'une gestion WAN purement fondée sur les connexions physiques et les routes traditionnelles.

L'apprenant comprend maintenant les rôles de l'underlay, de l'overlay, des équipements de bordure, des fonctions de gestion et de contrôle, ainsi que des tunnels sécurisés.

Il a également découvert les politiques applicatives, les métriques de performance, les mécanismes de sélection des chemins, la sortie Internet directe et les principes de segmentation.

Le niveau intermédiaire transformera ces connaissances en un laboratoire concret.

## 75. Le fil conducteur du cours suivant

Le cours `sd-wan-intermediaire.md` reprendra la même entreprise NovaTech.

Les mêmes emplacements, applications et accès WAN seront conservés. L'objectif sera de construire un scénario opérationnel sur une plateforme de laboratoire choisie, plutôt que de remplacer la topologie par un nouvel exemple sans lien avec le premier cours.

Le niveau intermédiaire devra notamment couvrir :

- La préparation du plan d'adressage.
- La configuration de l'underlay.
- L'enregistrement et l'authentification des équipements.
- L'établissement des connexions de contrôle.
- La création des tunnels de données.
- L'apprentissage et la distribution des routes.
- Les politiques de sélection de chemin.
- Les mécanismes de mesure de performance.
- Les tests de basculement et les vérifications applicatives.
- Le dépannage des erreurs de configuration.

Les commandes et les procédures dépendront de la plateforme choisie. Les exemples devront distinguer les principes génériques du SD-WAN des mécanismes spécifiques à un constructeur.

## 76. Progression complète

```text
DÉBUTANT
Comprendre le SD-WAN
        |
        v
INTERMÉDIAIRE
Configurer, tester et dépanner
        |
        v
EXPERT
Concevoir, sécuriser et optimiser
        |
        v
EXPLOITATION AVANCÉE
Automatisation, observabilité,
haute disponibilité et gouvernance
```

Les niveaux ne doivent pas répéter intégralement les mêmes explications. Chacun doit s'appuyer sur les acquis précédents et introduire des compétences plus avancées.


# CONCLUSION GÉNÉRALE

Le SD-WAN permet d'organiser la connectivité entre plusieurs sites à travers une architecture fondée sur des politiques, des mécanismes de gestion et des équipements de bordure.

Il peut utiliser plusieurs technologies de transport et construire un overlay permettant aux sites de communiquer de manière cohérente. Les équipements peuvent sélectionner des chemins adaptés aux applications, sous réserve que les liens disponibles, les mesures et les politiques satisfassent les objectifs définis.

Le fonctionnement d'un réseau SD-WAN exige de distinguer l'underlay et l'overlay, les plans de gestion et de contrôle, le transport des données, les politiques applicatives et les mesures de performance.

La disponibilité des tunnels ne garantit pas à elle seule le bon fonctionnement des services. Les routes, les politiques, les capacités, les contrôles de sécurité et les applications doivent être vérifiés ensemble.

Le niveau intermédiaire réutilisera l'entreprise NovaTech pour construire un laboratoire de connectivité multisite et tester les mécanismes opérationnels du SD-WAN. Le niveau expert approfondira ensuite les stratégies de routage, la segmentation, la haute disponibilité, la sécurité et l'optimisation.

**Principe final : comprendre le transport, construire un overlay cohérent, définir des politiques adaptées aux applications, mesurer les performances réelles et vérifier la sécurité de chaque chemin avant de considérer le réseau comme opérationnel.**


# RÉFÉRENCES TECHNIQUES

- **MEF 70.2 — SD-WAN Service Attributes and Service Framework**  
  https://www.mef.net/resources/mef-70-2-sd-wan-service-attributes-and-service-framework/

  Référence sur les caractéristiques d'un service SD-WAN, les concepts fonctionnels et la relation entre le service d'overlay et les services de transport sous-jacents.

- **MEF — Présentation des services SD-WAN**  
  https://www.mef.net/service-standards/overlay/sd-wan/

  Présente notamment le rôle du SD-WAN Edge, les services underlay et les possibilités de sortie Internet directe.

- **Cisco Catalyst SD-WAN — Design Guide**  
  https://www.cisco.com/c/en/us/td/docs/solutions/CVD/SDWAN/cisco-sdwan-design-guide.html

  Exemple de documentation d'architecture décrivant les plans de gestion, de contrôle, d'orchestration et de données d'une implémentation particulière.

- **Cisco Catalyst SD-WAN — Solution Overview**  
  https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/solution/cisco-catalyst-sd-wan-solution-overview/solution.html

  Exemple de fonctionnement du plan de contrôle, des routes overlay et des fonctions des équipements de bordure dans une solution spécifique.

Les fonctions et les commandes SD-WAN ne sont pas identiques chez tous les constructeurs. Le cours intermédiaire devra choisir une plateforme de laboratoire et vérifier les capacités, les commandes et les mécanismes réellement disponibles sur cette plateforme.