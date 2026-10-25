# Challenge d'architecture réseau — Hybrid Cloud

> **Fichier :** `challenge-hybrid-cloud.md`  
> **Domaine :** architecture réseau hybride, cloud public, infrastructure sur site et cybersécurité  
> **Progression :** Débutant → Intermédiaire → Expert  
> **Environnement :** entreprise disposant d'un datacenter local et de ressources hébergées dans le cloud  
> **Technologies étudiées :** réseau IP, VLAN, VPN, routage, DNS, IAM, segmentation, observabilité, Infrastructure as Code et reprise après sinistre  
> **Approche :** conception, simulation, validation, dépannage et justification des choix techniques  
> **Objectif final :** concevoir une architecture hybride sécurisée, évolutive, supervisable et économiquement maîtrisée.


# 1. Présentation du challenge

## 1.1. Contexte de l'entreprise

Vous êtes ingénieur réseau et cloud pour **NovaTech Solutions**, une entreprise qui possède une infrastructure informatique sur site et souhaite déplacer progressivement certaines applications vers le cloud.

L'entreprise dispose actuellement :

- D'un petit datacenter local.
- D'un pare-feu professionnel.
- De commutateurs administrables.
- D'un réseau utilisateur segmenté.
- D'un serveur de fichiers ou d'un NAS.
- D'une application métier historique.
- D'une base de données contenant des informations professionnelles.
- D'un annuaire d'utilisateurs.
- De services DNS, DHCP et NTP.
- D'une connexion Internet principale.
- D'un système de sauvegarde local.

La direction souhaite utiliser le cloud pour héberger de nouvelles applications, améliorer la disponibilité de certains services et faciliter l'accès à des ressources informatiques supplémentaires.

Cependant, toutes les applications ne peuvent pas être déplacées immédiatement.

Certaines dépendent de serveurs locaux. D'autres accèdent à des équipements présents dans le bâtiment. Certaines données doivent rester dans l'environnement existant pendant une phase de transition. Enfin, les applications migrées doivent continuer à communiquer avec certains services locaux.

L'entreprise doit donc mettre en place une architecture **hybride**.

## 1.2. Qu'est-ce qu'une architecture hybride ?

Une architecture hybride associe plusieurs environnements informatiques distincts, par exemple :

- Un réseau d'entreprise sur site.
- Un datacenter privé.
- Un cloud public.
- Des applications SaaS.
- Des services de sécurité ou de gestion fournis à distance.

Ces environnements doivent communiquer selon des règles précises.

Une architecture hybride ne consiste pas simplement à créer un VPN. Il faut également concevoir :

- L'adressage IP.
- Le routage dans les deux directions.
- Les frontières de sécurité.
- Les mécanismes d'identité.
- La résolution DNS.
- La connectivité aux services.
- La supervision.
- La sauvegarde.
- La gestion des secrets.
- Les coûts récurrents.
- Les procédures de reprise.

Un tunnel VPN opérationnel ne garantit donc pas qu'une application soit correctement accessible, sécurisée et exploitable.

## 1.3. Objectifs de l'entreprise

NovaTech Solutions veut :

1. Migrer une application Web vers le cloud.
2. Conserver temporairement sa base de données sur site.
3. Permettre aux utilisateurs locaux d'accéder à l'application cloud.
4. Permettre à l'application cloud d'atteindre uniquement les services locaux nécessaires.
5. Éviter l'exposition publique des bases de données.
6. Séparer les environnements de production et de test.
7. Protéger les comptes d'administration.
8. Superviser les flux entre les deux environnements.
9. Sauvegarder les ressources critiques.
10. Réduire le risque de dépendance à une seule connexion réseau.
11. Préparer la migration future d'autres applications.
12. Contrôler les coûts et éviter les ressources cloud inutilisées.

## 1.4. Hypothèses du scénario

| Élément | Hypothèse |
|---|---|
| Site principal | Bureau avec petit datacenter |
| Utilisateurs | Environ 50 |
| Infrastructure locale | Serveurs, annuaire, fichiers et base de données historique |
| Cloud | Un cloud public |
| Réseau local global | `10.70.0.0/16` |
| Réseau cloud de production | `10.80.0.0/16` |
| Réseau cloud de test | `10.81.0.0/16` |
| Connexion hybride initiale | VPN site-à-site |
| Évolution possible | Liaison privée dédiée fournie par un opérateur ou un fournisseur cloud |
| Applications cloud | Frontend Web et services applicatifs |
| Base de données principale | Conservée temporairement sur site |
| Identités | Annuaire local et identités cloud |
| Accès administratif | Poste d'administration dédié et bastion selon les besoins |
| Sauvegardes | Locales et copies séparées |
| Supervision | Mesures et journaux centralisés |
| Objectif | Migration progressive sans rupture majeure d'activité |

Ces valeurs sont des hypothèses pédagogiques. Elles ne constituent pas un plan prêt à déployer. Les adresses doivent être comparées aux réseaux existants, aux VPN, aux autres sites et aux plages utilisées dans le cloud.

## 1.5. Contraintes à respecter

La solution doit :

- Fonctionner avec l'infrastructure existante lorsque cela est raisonnable.
- Limiter les changements nécessaires sur les systèmes historiques.
- Empêcher les accès non autorisés entre les réseaux.
- Préserver la disponibilité des applications critiques.
- Éviter la création de routes ambiguës.
- Documenter les dépendances du cloud.
- Limiter les coûts récurrents.
- Permettre un retour arrière en cas d'échec de migration.
- Éviter de rendre toute l'infrastructure locale dépendante d'un seul tunnel VPN.
- Utiliser des services cloud adaptés aux exigences réelles.

**Le but n'est pas de déplacer tous les systèmes vers le cloud immédiatement. Le but est de créer une architecture dans laquelle les environnements local et cloud peuvent fonctionner ensemble de manière maîtrisée.**


# 2. Progression des niveaux

## Niveau 1 — Débutant : relier le réseau local au cloud

Vous devez :

- Comprendre les besoins.
- Dessiner l'architecture physique et logique.
- Planifier les réseaux IP.
- Créer la structure réseau du cloud.
- Mettre en place une connectivité VPN dans un laboratoire.
- Comprendre les routes locales et distantes.
- Vérifier le chemin aller et le chemin retour.
- Tester DNS, accès applicatifs et filtrage.
- Documenter les flux.

**Livrable :** une architecture hybride fonctionnelle et documentée.

## Niveau 2 — Intermédiaire : sécuriser l'architecture

Vous devez :

- Définir une segmentation locale et cloud.
- Limiter les communications entre les environnements.
- Protéger les identités et les accès d'administration.
- Concevoir une résolution DNS hybride.
- Prévoir une connectivité redondante lorsque nécessaire.
- Superviser les tunnels et les flux.
- Gérer les secrets et les certificats.
- Appliquer les principes de moindre privilège.
- Diagnostiquer les pannes de routage et d'accès.

**Livrable :** une architecture hybride sécurisée avec matrice de flux et procédures de dépannage.

## Niveau 3 — Expert : industrialiser la plateforme hybride

Vous devez :

- Concevoir des réseaux cloud segmentés par environnement.
- Comparer VPN et connectivité privée dédiée.
- Concevoir une stratégie de routage hybride.
- Étudier les architectures hub-and-spoke.
- Contrôler l'accès aux services privés.
- Automatiser la création des ressources.
- Contrôler les changements de configuration.
- Concevoir une stratégie de reprise après sinistre.
- Évaluer les coûts et les transferts de données.
- Définir une stratégie de migration et de retour arrière.
- Concevoir une architecture hybride observable et exploitable.

**Livrable :** un dossier d'architecture complet, accompagné d'une feuille de route, de tests et d'une analyse des risques.


# 3. Défi 1 — Analyser les besoins et classer les applications

Avant de concevoir le réseau, vous devez déterminer quelles applications resteront sur site et lesquelles pourront être hébergées dans le cloud.

## 3.1. Inventaire des applications

Le scénario comprend les systèmes suivants.

| Application ou service | Emplacement initial | Destination envisagée | Dépendances |
|---|---|---|---|
| Portail Web interne | Sur site | Cloud | Base de données, DNS, identité |
| API métier | Sur site | Cloud | Base de données historique |
| Base de données principale | Sur site | Sur site temporairement | API métier |
| Serveur de fichiers | Sur site | Sur site dans un premier temps | Utilisateurs et sauvegardes |
| Annuaire local | Sur site | Maintenu pendant la transition | Authentification |
| Supervision | Sur site | Hybride selon les besoins | Journaux et métriques |
| Sauvegarde | Sur site | Copie supplémentaire hors site | Stockage et identité |
| Environnement de test | Limité | Cloud | Données de test |
| Services collaboratifs | SaaS | SaaS | Identités et accès Internet |

Le choix de migration doit prendre en compte les dépendances techniques et métier, les exigences de sécurité et les coûts.

## 3.2. Questions à poser pour chaque application

- Quelle est sa criticité ?
- Qui l'utilise ?
- Quelle est sa charge moyenne et maximale ?
- Quelles données traite-t-elle ?
- Quelles sont ses dépendances ?
- Quel niveau de latence est acceptable ?
- Quelle quantité de données est échangée avec les systèmes locaux ?
- Quelle indisponibilité est acceptable ?
- Quelle est la durée de migration envisageable ?
- L'application peut-elle fonctionner si le lien hybride tombe ?
- Peut-on restaurer l'application dans un autre environnement ?
- Quelles licences sont nécessaires ?
- Quels services cloud sont facturés à l'heure, au volume ou au transfert ?
- Existe-t-il des exigences contractuelles ou réglementaires ?

## 3.3. Évaluer les dépendances

Une application migrée peut encore dépendre :

- D'un DNS local.
- D'un annuaire sur site.
- D'une base de données locale.
- D'un serveur de fichiers.
- D'un service NTP.
- D'un système de licence.
- D'une API interne.
- D'un système de sauvegarde.
- D'un service métier inaccessible depuis le cloud.

Une migration réussie doit prendre en compte ces dépendances avant de déplacer l'application.

## 3.4. Matrice de dépendances

Complétez le tableau suivant.

| Source | Destination | Fonction | Criticité | Latence admissible | Plan de reprise |
|---|---|---|---|---|---|
| Frontend cloud | API cloud | Traitement métier | Élevée | À mesurer | Redéploiement |
| API cloud | Base locale | Données métier | Élevée | À mesurer | Procédure à définir |
| Cloud | DNS local | Résolution interne | Moyenne à élevée | À mesurer | DNS secondaire ou cache selon le besoin |
| Utilisateurs locaux | Frontend cloud | Utilisation de l'application | Élevée | À mesurer | Accès alternatif si nécessaire |
| Cloud | Sauvegarde | Protection des données | Élevée | Dépend du RPO | Restauration testée |
| Administrateur | Console cloud | Administration | Élevée | Faible sensibilité à la latence | Accès d'administration de secours |

Cette matrice révèle les dépendances qui pourraient rendre le système indisponible même lorsque le cloud lui-même fonctionne normalement.


# 4. Architecture 1 — Connectivité hybride de base

## 4.1. Schéma général

La première architecture relie le réseau local au réseau privé du cloud au moyen d'un VPN site-à-site.

```text
                         UTILISATEURS
                              |
                              v
                       +--------------+
                       | LAN LOCAL    |
                       | 10.70.0.0/16 |
                       +--------------+
                              |
                       +--------------+
                       | PARE-FEU     |
                       | LOCAL        |
                       +--------------+
                              |
                         INTERNET
                              |
                       Tunnel VPN IPsec
                              |
                       +--------------+
                       | VPN / GW     |
                       | CÔTÉ CLOUD   |
                       +--------------+
                              |
                       +--------------+
                       | RÉSEAU CLOUD |
                       | 10.80.0.0/16 |
                       +--------------+
                              |
                 +------------+-------------+
                 |                          |
                 v                          v
          APPLICATION WEB              API MÉTIER
                 |
                 v
          Base de données
          selon l'architecture
          et les règles prévues
```

Le tunnel crée un chemin chiffré entre les équipements ou passerelles concernés. Il ne remplace pas les règles de filtrage.

Les routes et les politiques de sécurité doivent être configurées des deux côtés.

## 4.2. Rôles des composants

### Pare-feu local

Le pare-feu local contrôle les communications entre les réseaux internes, le réseau cloud et Internet.

Il doit notamment :

- Définir les routes vers les préfixes cloud.
- Autoriser les flux nécessaires dans le VPN.
- Refuser les communications inutiles.
- Journaliser les événements importants.
- Contrôler les connexions entrantes et sortantes.
- Permettre le dépannage sans exposition générale des interfaces d'administration.

### Passerelle VPN cloud

La passerelle côté cloud termine le tunnel ou participe à son établissement.

Sa configuration dépend du service cloud choisi. Il faut définir :

- Les préfixes locaux autorisés.
- Les préfixes cloud.
- Les paramètres de tunnel.
- Les mécanismes d'authentification.
- Les paramètres de chiffrement.
- Les routes.
- Les règles de sécurité associées.
- Les mécanismes de surveillance de l'état du tunnel.

### Réseau privé cloud

Le réseau privé cloud accueille les ressources qui ne doivent pas être directement exposées à Internet.

Il doit être découpé en sous-réseaux et zones correspondant aux rôles :

- Frontend.
- Applications.
- Services de données.
- Gestion.
- Supervision.
- Environnements de test.

Le choix exact du découpage dépend du fournisseur et de ses capacités réseau.

## 4.3. Ce que le VPN ne garantit pas

Un tunnel VPN actif ne garantit pas que :

- Les routes sont correctes.
- Le chemin retour existe.
- Le DNS fonctionne.
- Le service distant est actif.
- Le trafic est autorisé par les règles de sécurité.
- Le MTU est adapté.
- La bande passante est suffisante.
- Le tunnel résiste à la perte de la connexion Internet.
- Les applications tolèrent la latence.

Un test doit donc vérifier le chemin réseau et le service applicatif, pas uniquement l'état du tunnel.


# 5. Architecture 2 — Segmenter les environnements local et cloud

## 5.1. Plan d'adressage de référence

Pour cet exercice, utilisez le bloc local `10.70.0.0/16` et des blocs distincts pour les environnements cloud.

| Environnement | Sous-réseau | Fonction |
|---|---|---|
| Local — Utilisateurs | `10.70.10.0/24` | Postes des collaborateurs |
| Local — Administration | `10.70.20.0/24` | Postes d'administration |
| Local — Serveurs | `10.70.30.0/24` | Services maintenus sur site |
| Local — Sauvegarde | `10.70.40.0/24` | Services et cibles de sauvegarde locales |
| Local — Gestion des équipements | `10.70.50.0/24` | Interfaces de gestion |
| Cloud — Frontend production | `10.80.10.0/24` | Entrée applicative |
| Cloud — Applications production | `10.80.20.0/24` | API et services métier |
| Cloud — Services internes | `10.80.30.0/24` | Services internes autorisés |
| Cloud — Gestion | `10.80.40.0/24` | Administration des ressources cloud, selon le modèle |
| Cloud — Test | `10.81.10.0/24` | Applications de test |
| Cloud — Services de test | `10.81.20.0/24` | Données et services de test |

Les réseaux sont des exemples. Les sous-réseaux doivent être adaptés au fournisseur, au nombre d'hôtes et aux services déployés.

Les plages locales, cloud, VPN et autres sites doivent être vérifiées ensemble afin d'éviter tout chevauchement.

## 5.2. Schéma logique

```text
                        ENVIRONNEMENT LOCAL
                 +-------------------------------+
                 |                               |
                 | VLAN 10 - UTILISATEURS        |
                 | VLAN 20 - ADMINISTRATION      |
                 | VLAN 30 - SERVEURS            |
                 | VLAN 40 - SAUVEGARDE           |
                 | VLAN 50 - GESTION              |
                 +---------------+---------------+
                                 |
                            PARE-FEU
                                 |
                            TUNNEL VPN
                                 |
                           PASSERELLE CLOUD
                                 |
                 +---------------+----------------+
                 |                                |
                 v                                v
          CLOUD PRODUCTION                   CLOUD TEST
          10.80.0.0/16                       10.81.0.0/16
                 |                                |
        +--------+---------+             +--------+--------+
        |        |         |             |                 |
        v        v         v             v                 v
     FRONTEND  APPS     SERVICES       APP TEST         DATA TEST
     10.80.10 10.80.20  10.80.30       10.81.10         10.81.20
```

Les environnements de test ne doivent pas pouvoir communiquer librement avec la production simplement parce qu'ils appartiennent au même abonnement, compte ou réseau d'organisation.

Il faut définir les routes et les règles de sécurité entre les environnements, y compris pour les services partagés.

## 5.3. Pourquoi des réseaux distincts ?

Le découpage permet :

- De limiter l'étendue d'une erreur de configuration.
- D'appliquer des politiques de sécurité différentes.
- De réduire les risques de mouvements latéraux.
- De séparer les données de test des données de production.
- De faciliter la supervision.
- De comprendre les chemins de trafic.
- De simplifier la planification de la migration.

Les sous-réseaux ne doivent pas être multipliés sans justification. Chaque zone doit correspondre à un besoin opérationnel ou de sécurité.

## 5.4. Exercice de planification

Pour chaque sous-réseau, documentez :

1. Son usage.
2. Le nombre d'adresses nécessaires.
3. Les adresses réservées.
4. Les routes associées.
5. Les ressources qui peuvent y être déployées.
6. Les sources autorisées.
7. Les destinations autorisées.
8. Les points de filtrage.
9. Les besoins de supervision.
10. La procédure de dépannage.


# 6. Défi 2 — Routage hybride

## 6.1. Les deux directions doivent fonctionner

Pour qu'une connexion fonctionne entre un poste local et une application cloud, il faut au minimum :

1. Que le poste envoie le paquet vers sa passerelle.
2. Que le réseau local possède une route vers le sous-réseau cloud.
3. Que le paquet atteigne la passerelle cloud.
4. Que les règles de sécurité autorisent le flux.
5. Que la ressource cloud possède une route de retour vers le réseau local.
6. Que les règles de sécurité cloud autorisent le retour de la connexion.
7. Que le service cible soit opérationnel.

Une erreur de route retour peut donner l'impression que la requête arrive à destination alors que la connexion échoue.

## 6.2. Schéma du chemin aller et retour

```text
                 POSTE LOCAL
                10.70.10.25
                     |
                     v
               PASSERELLE LAN
                     |
                     v
                PARE-FEU LOCAL
                     |
                     v
                  TUNNEL VPN
                     |
                     v
               PASSERELLE CLOUD
                     |
                     v
             APPLICATION CLOUD
                10.80.20.15


        CHEMIN RETOUR À VÉRIFIER :

             APPLICATION CLOUD
                     |
                     v
               ROUTE VERS LAN
                     |
                     v
               PASSERELLE CLOUD
                     |
                     v
                  TUNNEL VPN
                     |
                     v
                PARE-FEU LOCAL
                     |
                     v
               PASSERELLE LAN
                     |
                     v
                 POSTE LOCAL
```

Les deux directions doivent être vérifiées, même si le pare-feu suit automatiquement l'état des connexions.

## 6.3. Routes statiques

Dans une première architecture, les routes peuvent être définies statiquement.

Exemple conceptuel sur le réseau local :

```text
Réseau distant : 10.80.0.0/16
Prochain saut  : passerelle VPN ou interface VPN
```

Côté cloud :

```text
Réseau distant : 10.70.0.0/16
Prochain saut  : passerelle VPN
```

Ces lignes décrivent le principe, pas une configuration prête à copier. La syntaxe dépend du fournisseur et de l'équipement réseau.

Lorsque le fournisseur utilise des tables de routage associées à des sous-réseaux, des passerelles de connexion ou des objets de routage spécifiques, configurez-les conformément à la documentation de cette plateforme.

## 6.4. Routes statiques ou routage dynamique ?

Les routes statiques peuvent convenir lorsque :

- Le nombre de réseaux est limité.
- La topologie est stable.
- Les changements sont rares.
- Les procédures de mise à jour sont maîtrisées.

Le routage dynamique peut être adapté lorsque :

- Le nombre de préfixes augmente.
- Plusieurs sites sont connectés.
- Plusieurs chemins doivent être utilisés.
- La convergence automatique est nécessaire.
- Le service cloud et le matériel prennent en charge le protocole choisi.

Le choix doit être justifié par les exigences. Un protocole de routage dynamique mal contrôlé peut propager des routes incorrectes plus rapidement qu'une configuration statique.

## 6.5. Exercice de diagnostic

Un poste local peut joindre le pare-feu local, mais l'application cloud ne répond pas.

Vérifiez successivement :

1. La route locale vers le réseau cloud.
2. L'état du tunnel.
3. Les compteurs et journaux du VPN.
4. La route vers le réseau local côté cloud.
5. Les règles de sécurité cloud.
6. Les règles du pare-feu local.
7. La configuration IP de l'application.
8. Le port du service.
9. Le chemin retour.
10. Les journaux applicatifs.

Ne désactivez pas les politiques de sécurité pour conclure qu'il s'agit d'un problème de routage.


# 7. Défi 3 — VPN site-à-site et connectivité privée dédiée

## 7.1. VPN site-à-site

Un VPN IPsec site-à-site permet de chiffrer le trafic transporté entre le réseau local et une passerelle cloud compatible.

Ses avantages peuvent inclure :

- Une mise en place relativement rapide.
- Une réutilisation de la connexion Internet existante.
- Le chiffrement du trafic sur le réseau de transit public.
- Une solution adaptée aux premières phases de migration.

Ses limites potentielles comprennent :

- La dépendance à l'accès Internet.
- La bande passante disponible.
- La latence et sa variabilité.
- Les limites de débit de l'équipement.
- Les changements d'adresse publique.
- Les contraintes de MTU et de fragmentation.
- La nécessité de surveiller les tunnels.

La capacité réelle doit être mesurée avec la configuration de sécurité utilisée.

## 7.2. Connectivité privée dédiée

Certains fournisseurs et opérateurs proposent une connectivité privée reliant l'entreprise à un réseau cloud.

Cette solution peut apporter :

- Une connectivité plus prévisible.
- Des options de bande passante adaptées.
- Une intégration au réseau privé de l'opérateur.
- Des chemins de connectivité dédiés selon le service choisi.

Cependant, le terme « privé » ne signifie pas nécessairement que tout le trafic est chiffré de bout en bout. Il faut vérifier les garanties du service, les options de chiffrement, les responsabilités de l'opérateur et les contrôles applicables.

La connexion privée doit également avoir un plan de routage et une politique de sécurité.

## 7.3. Schéma comparatif

```text
OPTION A — VPN IPsec

RÉSEAU LOCAL
     |
PARE-FEU
     |
INTERNET
     |
TUNNEL VPN CHIFFRÉ
     |
PASSERELLE CLOUD
     |
RÉSEAU CLOUD


OPTION B — CONNECTIVITÉ PRIVÉE

RÉSEAU LOCAL
     |
ROUTEUR / PARE-FEU
     |
ACCÈS DE L'OPÉRATEUR
     |
CIRCUIT OU SERVICE PRIVÉ
     |
POINT DE PRÉSENCE CLOUD
     |
RÉSEAU CLOUD
```

La seconde architecture ne doit pas être considérée automatiquement comme plus sécurisée que la première. Le chiffrement, le contrôle d'accès, le routage et la supervision restent nécessaires selon le besoin.

## 7.4. Tableau de comparaison

| Critère | VPN IPsec | Connectivité privée dédiée |
|---|---|---|
| Mise en place initiale | Souvent plus simple | Souvent plus longue |
| Dépendance à Internet | Généralement oui | Selon l'offre et l'accès |
| Chiffrement | IPsec selon la configuration | À vérifier selon le service |
| Débit | Dépend des liens et équipements | Dépend du circuit choisi |
| Latence | Peut varier | Peut être plus prévisible, selon le service |
| Coût récurrent | Équipement, Internet et exploitation | Service opérateur et éventuels frais associés |
| Redondance | Possible avec plusieurs tunnels et accès | Possible selon l'offre et les chemins |
| Exploitation | Maîtrisée par l'équipe réseau | Coordination avec l'opérateur souvent nécessaire |

## 7.5. Décision attendue

Vous devez indiquer :

- Quelle solution répond au besoin actuel.
- Quel débit est nécessaire.
- Quel niveau de disponibilité est attendu.
- Quel coût récurrent est acceptable.
- Quelle solution de secours est prévue.
- Comment la bascule est testée.
- Quelles données nécessitent un chiffrement.
- Comment les routes sont contrôlées.

Ne choisissez pas une liaison privée uniquement parce qu'elle paraît plus professionnelle. Justifiez-la par les besoins, les mesures et les contraintes métier.


# 8. Défi 4 — Architecture hub-and-spoke

Lorsque plusieurs environnements cloud, sites distants ou réseaux virtuels existent, une architecture hub-and-spoke peut centraliser certaines fonctions réseau.

Le hub peut héberger ou relier :

- Les passerelles VPN.
- Les fonctions de routage centralisé.
- Les services DNS partagés.
- Les politiques de filtrage inter-réseaux.
- Les points de sortie Internet.
- La supervision du trafic.
- Les accès vers le réseau local.

Les spokes représentent les réseaux applicatifs, les projets, les environnements ou les unités organisationnelles.

## 8.1. Schéma logique

```text
                       RÉSEAU LOCAL
                            |
                            |
                       VPN / LIEN PRIVÉ
                            |
                            v
                 +----------------------+
                 | HUB RÉSEAU CLOUD     |
                 | Routage partagé      |
                 | Inspection si prévue |
                 | Services partagés    |
                 +----------------------+
                    /         |         \
                   /          |          \
                  v           v           v
           +-----------+ +-----------+ +-----------+
           | SPOKE A   | | SPOKE B   | | SPOKE C   |
           | PROD      | | TEST      | | SERVICES  |
           +-----------+ +-----------+ +-----------+
                |             |              |
             Apps prod     Apps test      DNS / outils
```

Le schéma représente une architecture logique. La façon exacte de créer les hubs, les spokes, les tables de routage et les connexions dépend du fournisseur cloud.

## 8.2. Avantages potentiels

- Administration centralisée de la connectivité.
- Réutilisation des connexions vers le réseau local.
- Séparation des environnements.
- Contrôle des flux entre réseaux.
- Services partagés.
- Possibilité de centraliser certains journaux.

## 8.3. Risques et limites

- Le hub peut devenir un point de défaillance.
- Le trafic peut subir des détours inutiles.
- Les coûts de traitement et de transfert peuvent augmenter.
- Les règles centralisées peuvent devenir complexes.
- Les spokes peuvent être trop largement autorisés.
- Un changement dans le hub peut affecter plusieurs applications.

La conception doit préciser les chemins attendus. Une architecture hub-and-spoke ne signifie pas que tous les spokes doivent pouvoir communiquer directement.

## 8.4. Exercice

Concevez trois spokes :

- Production.
- Test.
- Services partagés.

Définissez :

1. Les routes de chaque spoke.
2. Les règles d'accès au hub.
3. Les communications interdites.
4. Les flux vers le réseau local.
5. Les accès Internet.
6. Les services partagés nécessaires.
7. Le comportement si le hub est indisponible.
8. Les coûts associés au trafic inter-réseaux.
9. Les mécanismes de supervision.
10. Les procédures de modification et de retour arrière.


# 9. Défi 5 — DNS hybride

Le DNS est l'un des composants les plus importants d'une architecture hybride.

Une route correcte ne suffit pas si les clients ne peuvent pas résoudre les noms des applications.

## 9.1. Problèmes possibles

- Les postes locaux ne résolvent pas les noms des ressources cloud.
- Les ressources cloud ne résolvent pas les noms internes.
- Les enregistrements pointent vers des adresses incorrectes.
- Une application utilise un ancien nom ou une ancienne adresse.
- Un résolveur est inaccessible depuis le tunnel.
- Une règle de sécurité bloque les requêtes DNS.
- Le DNS public expose un nom qui ne devrait pas être publié.
- Une mauvaise réponse DNS entraîne l'utilisation d'un chemin réseau non prévu.

## 9.2. Architecture logique de référence

```text
                      POSTES LOCAUX
                            |
                            v
                    DNS LOCAL / ENTREPRISE
                            |
                  +---------+----------+
                  |                    |
                  v                    v
            Noms locaux          Résolution cloud
                  |                    |
                  |               Liaison hybride
                  |                    |
                  |                    v
                  |             RÉSOLVEUR CLOUD
                  |                    |
                  |                    v
                  |             Ressources privées
                  |
                  v
            Services internes
```

L'architecture exacte dépend de l'existence d'une zone DNS interne, d'un annuaire, de zones privées cloud ou de mécanismes de résolution conditionnelle.

Il ne faut pas supposer que le DNS fourni automatiquement par une plateforme cloud résoudra tous les noms locaux.

## 9.3. Choix de conception

Vous devez documenter :

- Les zones internes.
- Les zones publiques.
- Les résolveurs locaux et cloud.
- Les domaines à résoudre de chaque côté.
- Les mécanismes de transfert ou de résolution conditionnelle.
- Les règles de pare-feu nécessaires.
- La façon dont les enregistrements sont mis à jour.
- Les stratégies de cache.
- Les procédures en cas de panne de DNS.

Les transferts de zone ne doivent pas être ouverts à des clients quelconques. Utilisez les mécanismes de sécurité et les restrictions appropriées à la plateforme DNS.

## 9.4. Tests DNS

Sur un poste Windows :

```powershell
ipconfig /all
nslookup nom-de-test
```

Sur Linux :

```bash
resolvectl status
dig nom-de-test
```

Les noms de test doivent correspondre à des enregistrements réellement prévus dans l'environnement.

Pour chaque test, vérifiez :

1. Le résolveur utilisé.
2. Le nom demandé.
3. La réponse obtenue.
4. L'adresse retournée.
5. Le temps de réponse.
6. Le chemin jusqu'au service.
7. La cohérence des règles de filtrage.

## 9.5. Exercice d'incident

Une application cloud est joignable par son adresse IP privée, mais échoue lorsque l'utilisateur utilise son nom habituel.

Déterminez si la cause est :

- Un enregistrement DNS incorrect.
- Un résolveur inaccessible.
- Une règle de filtrage.
- Un problème de routage.
- Un certificat ou un nom de serveur incorrect.
- Une dépendance applicative.

Ne concluez pas à un problème DNS tant que vous n'avez pas vérifié ce que la requête retourne réellement.


# 10. Défi 6 — Sécurité des identités et des accès

Le réseau hybride relie des environnements distincts, mais les comptes et les identités constituent également une frontière de sécurité essentielle.

Un utilisateur disposant de privilèges excessifs dans le cloud pourrait créer des ressources, modifier les routes, élargir les règles de filtrage ou exposer des services, même si le VPN est correctement sécurisé.

## 10.1. Les principaux domaines de sécurité

Vous devez traiter séparément :

- Les identités des utilisateurs.
- Les identités des administrateurs.
- Les identités des machines et applications.
- Les permissions cloud.
- Les comptes d'urgence.
- Les secrets et certificats.
- Les accès aux consoles d'administration.
- Les accès aux ressources réseau.
- Les autorisations de sauvegarde.

## 10.2. Architecture de contrôle

```text
                    ADMINISTRATEUR
                           |
                           v
                  AUTHENTIFICATION
                  FORTE SI DISPONIBLE
                           |
                           v
                  +------------------+
                  | COMPTE ADMIN     |
                  | PRIVILEGES LIMITÉS|
                  +------------------+
                           |
                           v
                  +------------------+
                  | CONSOLE / API    |
                  | D'ADMINISTRATION |
                  +------------------+
                           |
                    Contrôles IAM
                           |
            +--------------+--------------+
            |              |              |
            v              v              v
        Réseau cloud    Machines       Sauvegardes
```

L'IAM, ou gestion des identités et des accès, doit définir qui peut effectuer quelles actions sur quelles ressources.

Le simple fait d'être connecté au réseau d'entreprise ne doit pas automatiquement donner des droits d'administration cloud.

## 10.3. Principes de sécurité

- Utiliser des identités individuelles.
- Appliquer le moindre privilège.
- Séparer les comptes utilisateur et administrateur.
- Utiliser une authentification multifacteur lorsque disponible et adaptée.
- Limiter les comptes permanents très privilégiés.
- Révoquer rapidement les accès devenus inutiles.
- Éviter les identifiants partagés.
- Stocker les secrets dans un mécanisme adapté.
- Journaliser les opérations sensibles.
- Protéger les comptes d'urgence.
- Tester la procédure de récupération d'un compte administratif.

## 10.4. Identités de service

Une application cloud qui accède à une base de données ou à un service local ne doit pas nécessairement utiliser le compte personnel d'un administrateur.

Privilégiez une identité de service ou un mécanisme équivalent adapté à la plateforme.

Documentez :

- Les ressources auxquelles l'identité a accès.
- Les actions autorisées.
- La méthode d'authentification.
- Les secrets utilisés, le cas échéant.
- Le cycle de vie de l'identité.
- Les journaux disponibles.
- La procédure de révocation.

Évitez les clés ou secrets permanents lorsqu'une identité de charge de travail ou un mécanisme à durée limitée convient.

## 10.5. Exercice IAM

Un développeur doit pouvoir consulter les journaux de son application de test mais ne doit pas pouvoir modifier les règles du réseau de production.

Concevez une politique qui distingue :

- La lecture des journaux de test.
- Le déploiement en test.
- La lecture des ressources de production.
- La modification des règles de production.
- L'administration des identités.
- La suppression des sauvegardes.

Chaque permission doit être justifiée et testée avec un compte représentant le rôle prévu.


# 11. Défi 7 — Séparer les plans de gestion, de données et d'administration

## 11.1. Pourquoi cette séparation est nécessaire

Une infrastructure hybride peut être atteinte par plusieurs chemins :

- Depuis le LAN.
- Depuis le VPN.
- Depuis une console cloud.
- Depuis une API.
- Depuis un bastion.
- Depuis un système d'automatisation.
- Depuis un fournisseur ou prestataire autorisé.

La sécurité doit prendre en compte tous ces points d'accès.

Une séparation réseau est utile, mais elle doit être accompagnée de règles IAM, de journaux et d'un contrôle des identités.

## 11.2. Schéma logique

```text
                 +------------------------+
                 | PLAN UTILISATEUR       |
                 | Postes et applications |
                 +------------------------+
                            |
                       Règles d'accès
                            |
                 +------------------------+
                 | PLAN APPLICATIF        |
                 | Frontend / API / DB    |
                 +------------------------+


                 +------------------------+
                 | PLAN D'ADMINISTRATION  |
                 | Bastion / IAM / API    |
                 +------------------------+
                            |
                    Accès contrôlé
                            |
                 +----------+-----------+
                 |                      |
                 v                      v
             Réseau local           Ressources cloud


                 +------------------------+
                 | PLAN DE SAUVEGARDE     |
                 | Données et copies      |
                 +------------------------+
```

Les plans peuvent être logiquement ou physiquement séparés selon les contraintes de l'environnement.

## 11.3. Administration du réseau cloud

L'administration réseau doit être limitée aux actions nécessaires.

Exemples d'opérations privilégiées :

- Création d'un réseau virtuel.
- Modification d'une route.
- Ouverture d'un port.
- Modification d'un tunnel VPN.
- Création d'une passerelle.
- Modification des permissions réseau.
- Publication d'un service.
- Création d'une connexion entre environnements.

Les changements susceptibles d'exposer un réseau entier doivent suivre une procédure d'approbation adaptée.

## 11.4. Exercice

Créez trois rôles :

1. Administrateur réseau.
2. Administrateur applicatif.
3. Opérateur de supervision.

Définissez pour chacun :

- Les ressources visibles.
- Les opérations autorisées.
- Les opérations interdites.
- Les conditions d'élévation de privilèges.
- Les journaux à collecter.
- Les tests permettant de vérifier le rôle.


# 12. Défi 8 — Sécurité des services privés cloud

Une ressource cloud ne doit pas être exposée publiquement simplement pour faciliter la connexion depuis le réseau local.

Dans de nombreux environnements cloud, il est possible d'utiliser des interfaces privées, des endpoints privés ou des mécanismes analogues pour accéder à certains services sans passer par une exposition publique.

La disponibilité et le fonctionnement exacts de ces mécanismes dépendent du fournisseur et du service.

## 12.1. Architecture conceptuelle

```text
                     RÉSEAU LOCAL
                          |
                     VPN / PRIVÉ
                          |
                          v
                  +------------------+
                  | RÉSEAU CLOUD     |
                  | PRIVÉ             |
                  +------------------+
                          |
                          v
                  +------------------+
                  | APPLICATION      |
                  | PRIVÉE           |
                  +------------------+
                          |
                  Accès réseau limité
                          |
                          v
                  +------------------+
                  | SERVICE MANAGÉ   |
                  | ENDPOINT PRIVÉ   |
                  | SI DISPONIBLE    |
                  +------------------+
```

Le diagramme présente une idée générale. Les endpoints privés ne fonctionnent pas de la même manière pour tous les services.

La résolution DNS, les routes, les politiques de sécurité et les autorisations IAM doivent être conçues ensemble.

## 12.2. Travail demandé

Déterminez pour une base de données cloud ou un service de stockage :

1. Si une adresse publique est nécessaire.
2. Si un endpoint privé est disponible.
3. Quels réseaux peuvent joindre le service.
4. Quelles identités sont autorisées.
5. Quelle résolution DNS est nécessaire.
6. Quels journaux sont disponibles.
7. Comment sont protégés les secrets.
8. Comment le service est sauvegardé.
9. Comment l'accès est testé depuis le réseau local.
10. Comment l'accès est testé depuis une source non autorisée.

## 12.3. Validation

Un service privé doit être testé depuis :

- Une source autorisée.
- Une source non autorisée.
- Un réseau de test.
- Le réseau d'administration lorsqu'un accès est requis.

Il faut également vérifier qu'une ressource ne reste pas accessible par un chemin public alternatif non prévu.


# 13. Défi 9 — Disponibilité et redondance hybride

Une architecture hybride dépend de plusieurs composants :

- Le réseau local.
- Le pare-feu local.
- L'accès Internet.
- Le tunnel VPN ou la liaison privée.
- La passerelle cloud.
- Les tables de routage cloud.
- Les ressources applicatives.
- Les systèmes DNS.
- Les identités.
- Les services de stockage.
- Les sauvegardes.

Le cloud ne supprime donc pas les points de défaillance du réseau d'entreprise.

## 13.1. Architecture de connectivité redondante

```text
                        RÉSEAU LOCAL
                             |
                       +-------------+
                       | PARE-FEU A  |
                       +-------------+
                             |
                   +---------+---------+
                   |                   |
                   v                   v
              ACCÈS WAN A          ACCÈS WAN B
                   |                   |
                   v                   v
                VPN A                VPN B
                   |                   |
                   +---------+---------+
                             |
                      +--------------+
                      | PASSERELLE   |
                      | CÔTÉ CLOUD   |
                      +--------------+
                             |
                      +--------------+
                      | RÉSEAUX CLOUD|
                      +--------------+
```

Ce schéma représente deux chemins possibles. Il ne signifie pas que le trafic basculera automatiquement.

Il faut vérifier :

- Les équipements réellement indépendants.
- Les routes utilisées par chaque tunnel.
- La détection de panne.
- La convergence.
- La façon de prévenir les chemins asymétriques problématiques.
- Les coûts du second accès.
- Les règles de filtrage sur les deux chemins.
- Les mécanismes de surveillance.

## 13.2. Scénarios de panne

Testez les scénarios suivants dans un environnement adapté :

1. Perte d'un tunnel VPN.
2. Perte de l'accès Internet principal.
3. Indisponibilité de la passerelle cloud.
4. Perte d'une route vers un sous-réseau cloud.
5. Indisponibilité du DNS local.
6. Indisponibilité du DNS cloud.
7. Perte de l'identité centralisée.
8. Panne du frontend cloud.
9. Panne de la base de données locale.
10. Indisponibilité de la cible de sauvegarde.

Pour chaque scénario, documentez :

- Le service affecté.
- Le mécanisme de détection.
- Le comportement attendu.
- La procédure de reprise.
- Le temps d'interruption mesuré.
- Les données potentiellement perdues.
- Les tests à réaliser après rétablissement.

## 13.3. Le cloud peut rester disponible alors que l'entreprise ne peut plus l'utiliser

Si le tunnel VPN tombe, une application cloud peut continuer à fonctionner, mais les employés locaux peuvent ne plus pouvoir y accéder.

Il faut donc distinguer :

- La disponibilité de la ressource cloud.
- La disponibilité du chemin réseau.
- La disponibilité de l'identité.
- La disponibilité de la résolution DNS.
- La disponibilité de l'application métier.

Le suivi de disponibilité doit mesurer la chaîne complète du service, et pas uniquement l'état de la machine virtuelle.


# 14. Défi 10 — Sécurité et filtrage entre environnements

## 14.1. Matrice de flux de référence

La matrice suivante indique le comportement attendu pour l'exercice. Les règles réelles doivent préciser les adresses et services effectivement utilisés.

| Source | Destination | Politique de référence | Justification |
|---|---|---|---|
| Utilisateurs locaux | Frontend cloud | Autoriser selon le service | Accès applicatif |
| Internet | Frontend public cloud | Autoriser uniquement les ports publiés | Publication contrôlée |
| Internet | API non publiée | Refuser | Éviter l'exposition inutile |
| Frontend cloud | API cloud | Autoriser les flux nécessaires | Traitement applicatif |
| API cloud | Base locale | Autoriser sous condition | Dépendance historique |
| Frontend cloud | Base locale | Refuser par défaut | Empêcher l'accès direct depuis le frontend |
| Cloud test | Production | Refuser par défaut | Isolement des environnements |
| Administrateur autorisé | Console cloud | Autoriser selon IAM | Administration |
| Poste utilisateur | Interface d'administration cloud | Refuser | Réduction des privilèges |
| Supervision autorisée | Ressources | Autoriser les mécanismes nécessaires | Collecte de mesures |
| Cloud | DNS local | Autoriser si nécessaire | Résolution des noms internes |
| Cloud | Gestion des équipements locaux | Refuser par défaut | Protection du réseau de gestion |
| Serveurs locaux | Ressources cloud privées | Autoriser selon le besoin | Intégration hybride |
| Réseau cloud | Réseau de sauvegarde local | Refuser par défaut, exceptions documentées | Protection des copies |
| Administrateurs de sauvegarde | Cibles de sauvegarde | Autoriser sous condition | Exploitation protégée |

## 14.2. Règle importante pour la base de données locale

Dans le scénario, l'API cloud doit joindre la base de données locale.

Cette dépendance doit être limitée.

La politique doit préciser :

- L'adresse de l'API autorisée.
- L'adresse de la base.
- Le protocole.
- Le port exact requis.
- La règle appliquée côté cloud.
- La règle appliquée côté local.
- L'identité utilisée par l'application.
- La méthode d'authentification à la base.
- Les journaux disponibles.
- Le comportement après coupure du tunnel.

N'autorisez pas tout le réseau cloud à communiquer avec toute la zone des serveurs locaux.

## 14.3. Filtrage aux bons endroits

Une architecture hybride peut comporter plusieurs niveaux de filtrage :

- Pare-feu local.
- Règles de sécurité cloud.
- ACL de sous-réseau, si disponibles.
- Pare-feu du système d'exploitation.
- WAF ou contrôle applicatif.
- Contrôles IAM.
- Politique d'accès aux services managés.
- Contrôle réseau de l'hyperviseur.

Ces contrôles sont complémentaires. Il faut éviter les règles contradictoires, les accès implicites et les flux autorisés par plusieurs chemins mal documentés.

## 14.4. Tester la matrice

Pour chaque flux critique :

1. Test positif depuis la bonne source.
2. Test négatif depuis une source non autorisée.
3. Vérification du journal.
4. Vérification du port et du protocole.
5. Vérification du chemin retour.
6. Vérification de l'adresse source réellement vue par la destination.
7. Vérification de l'absence d'un chemin alternatif.
8. Documentation du résultat.

Une connexion qui échoue ne prouve pas que le filtrage est correct : le service peut être arrêté ou la route absente. Utilisez les journaux et les tests pour distinguer ces causes.


# 15. Défi 11 — MTU, VPN et performances

L'encapsulation VPN ajoute des en-têtes aux paquets. Selon la topologie, la configuration et le matériel, cela peut réduire la taille effective du paquet transportable sans fragmentation.

Un MTU inadapté peut provoquer :

- Des connexions qui établissent la session puis se bloquent.
- Des transferts de fichiers lents.
- Des problèmes avec certains protocoles.
- Des retransmissions.
- Des difficultés de découverte du MTU de chemin.
- Des comportements différents selon les applications.

## 15.1. Démarche de diagnostic

1. Mesurer la connectivité de base.
2. Tester les services qui échouent.
3. Observer les retransmissions.
4. Vérifier les interfaces et les tunnels.
5. Contrôler les paramètres MTU aux deux extrémités.
6. Examiner les messages ICMP utiles à la découverte du MTU.
7. Tester différents paquets dans un laboratoire autorisé.
8. Vérifier les effets sur les connexions existantes.
9. Documenter la valeur retenue et sa justification.

Ne changez pas le MTU sur tous les équipements à partir d'un seul symptôme.

## 15.2. Mesurer les performances

Pour chaque flux important, mesurez :

- La latence.
- La perte de paquets.
- Le débit.
- La variation de latence.
- L'utilisation CPU des équipements concernés.
- Le comportement aux heures de pointe.
- La performance lorsque les sauvegardes s'exécutent.
- La performance lorsque le lien hybride est utilisé simultanément par plusieurs applications.

Les mesures doivent être réalisées à partir de points représentatifs et dans des conditions contrôlées.

## 15.3. Exercice

Une API cloud met plusieurs secondes à répondre lorsqu'elle interroge la base locale.

Déterminez si le délai provient :

- Du temps de traitement de l'API.
- De la latence du lien.
- De requêtes trop nombreuses à la base.
- De la résolution DNS.
- D'une inspection du trafic.
- D'une mauvaise configuration du pool de connexions.
- D'une limitation de ressources.
- D'un problème de retransmission ou de MTU.

Proposez des mesures pour isoler les causes et justifier les améliorations.


# 16. Défi 12 — Observabilité et journalisation hybride

Une architecture hybride ne peut pas être exploitée correctement si chaque environnement possède des journaux isolés que personne ne peut corréler.

## 16.1. Sources d'observation

| Composant | Informations à collecter |
|---|---|
| Pare-feu local | Connexions, refus, sessions VPN et événements |
| Passerelle VPN | État des tunnels, métriques et erreurs |
| Réseau cloud | Routes, interfaces, flux et changements |
| Application | Erreurs, latence et statut du service |
| Base de données | Connexions, erreurs et performances |
| DNS | Requêtes, échecs et disponibilité |
| IAM | Connexions et modifications sensibles |
| Ressources cloud | Charge, réseau et disponibilité |
| Sauvegarde | Succès, échecs et durée des opérations |
| Infrastructure locale | État des interfaces, CPU et mémoire |

Les métriques ne doivent pas être collectées uniquement parce qu'elles sont disponibles. Déterminez quelles mesures aident à détecter ou diagnostiquer un incident.

## 16.2. Corrélation

Pour diagnostiquer une application hybride, il peut être nécessaire de rapprocher :

- Les logs du frontend.
- Les logs de l'API.
- Les logs de la base.
- Les logs du pare-feu.
- Les événements VPN.
- Les routes observées.
- Les réponses DNS.
- Les événements IAM.

Les horloges des systèmes doivent être synchronisées autant que possible.

Une heure incorrecte peut rendre la corrélation des incidents difficile et produire une chronologie trompeuse.

## 16.3. Tableau de bord minimal

Créez un tableau de bord qui montre :

- L'état du tunnel hybride.
- Le taux de perte vers les services critiques.
- La latence entre le cloud et le réseau local.
- La disponibilité du frontend.
- La disponibilité de l'API.
- La latence des requêtes à la base.
- Les erreurs DNS.
- Les connexions refusées importantes.
- La consommation de bande passante.
- L'état des sauvegardes.

## 16.4. Exercice

Provoquez un échec de connexion à un service de test et identifiez les preuves disponibles.

Votre rapport doit pouvoir répondre à :

1. Le client a-t-il envoyé la requête ?
2. Le paquet a-t-il traversé le tunnel ?
3. La passerelle distante l'a-t-elle reçu ?
4. Une règle l'a-t-elle bloqué ?
5. Le service a-t-il répondu ?
6. Le retour est-il arrivé au client ?
7. Le nom DNS était-il correct ?
8. L'identité disposait-elle des droits nécessaires ?


# 17. Défi 13 — Infrastructure as Code

La création manuelle de ressources cloud peut être adaptée à un laboratoire ou à un premier test. Pour un environnement d'entreprise, il devient important de contrôler, reproduire et auditer les modifications.

L'Infrastructure as Code, ou IaC, permet de décrire les ressources au moyen de fichiers versionnés et de processus automatisés.

## 17.1. Ressources à gérer

Votre modèle peut décrire :

- Les réseaux virtuels.
- Les sous-réseaux.
- Les tables de routage.
- Les passerelles VPN.
- Les règles de sécurité.
- Les interfaces réseau.
- Les ressources applicatives.
- Les associations DNS.
- Les permissions d'identité.
- Les systèmes de supervision.
- Les ressources de sauvegarde.

Toutes les ressources ne doivent pas forcément être créées par le même outil. Certaines opérations peuvent nécessiter une coordination avec les administrateurs réseau locaux ou les opérateurs.

## 17.2. Cycle de déploiement

```text
            BESOIN / CHANGEMENT VALIDÉ
                       |
                       v
              CODE VERSIONNÉ
                       |
                       v
              VALIDATION SYNTAXIQUE
                       |
                       v
              ANALYSE DU PLAN
                       |
                       v
             REVUE ET APPROBATION
                       |
                       v
              DÉPLOIEMENT CONTRÔLÉ
                       |
                       v
               TESTS TECHNIQUES
                       |
                       v
           VALIDATION / RETOUR ARRIÈRE
```

Un outil IaC exact n'est pas imposé. Terraform, OpenTofu ou les outils natifs du fournisseur peuvent convenir selon les exigences et l'environnement.

## 17.3. Règles de sécurité pour l'automatisation

- Ne stockez pas les secrets dans le dépôt de code.
- Vérifiez l'identité utilisée par le processus d'automatisation.
- Limitez ses permissions.
- Séparez les environnements de test et de production.
- Analysez le plan avant l'application.
- Contrôlez les changements de routes et de règles.
- Utilisez des validations automatisées.
- Préservez un historique des déploiements.
- Préparez le retour arrière.
- Évitez qu'une seule identité puisse modifier le code, l'approuver et supprimer toutes les traces.

L'automatisation doit réduire les erreurs, mais elle peut aussi propager rapidement une configuration dangereuse si les garde-fous sont insuffisants.

## 17.4. Exercice

Automatisez la création d'un réseau cloud de test contenant :

- Un réseau privé.
- Deux sous-réseaux.
- Une table de routage.
- Une règle de sécurité minimale.
- Une VM de test, si cela fait partie du périmètre.
- Des balises ou métadonnées identifiant l'environnement.
- Les paramètres permettant de détruire proprement les ressources de laboratoire.

Les identifiants, clés et mots de passe ne doivent pas être placés en clair dans le code.

Avant le déploiement, vérifiez le plan généré. Après déploiement, confirmez que les routes et les règles correspondent à la conception.


# 18. Défi 14 — Gestion des coûts cloud

Une architecture hybride peut être techniquement correcte tout en devenant trop coûteuse si les transferts de données, les passerelles, les journaux et les ressources sont mal dimensionnés.

## 18.1. Catégories de coûts

Évaluez au minimum :

- Les machines virtuelles ou services de calcul.
- Les disques et le stockage.
- Les sauvegardes.
- Les transferts de données sortants.
- Les transferts entre zones ou régions, selon l'offre.
- Les passerelles VPN.
- La connectivité privée.
- Les pare-feu et services d'inspection.
- Les systèmes de supervision.
- La rétention des journaux.
- Les licences.
- Les ressources laissées en marche inutilement.
- Les tests de reprise.
- Les coûts d'exploitation.

Les règles tarifaires varient selon le fournisseur, la région, le service et le type de trafic. Consultez les tarifs applicables à l'environnement choisi avant de calculer un budget réel.

## 18.2. Schéma des flux qui peuvent générer des coûts

```text
                  UTILISATEURS
                       |
                       v
                  FRONTEND CLOUD
                       |
                       v
                    API CLOUD
                       |
             +---------+---------+
             |                   |
             v                   v
        BASE LOCALE        STOCKAGE CLOUD
             |                   |
             v                   v
      TRAFIC HYBRIDE       TRAFIC INTER-RÉGION
             |                   |
             +---------+---------+
                       |
                       v
              TRANSFERTS FACTURABLES
              SELON LE SERVICE ET LE
              TYPE DE CONNEXION
```

Ce schéma montre les chemins qui doivent être examinés. Il ne signifie pas que chaque transfert est nécessairement facturé de la même façon.

## 18.3. Exercice d'optimisation

L'API cloud interroge la base locale plusieurs centaines de fois par minute. Les données changent relativement peu.

Proposez des options pour réduire le coût et la latence sans compromettre la cohérence ni la sécurité.

Vous pouvez analyser :

- La réduction des appels réseau.
- La mise en cache lorsque le modèle de données le permet.
- Le regroupement des requêtes.
- La migration de la base lorsque cela est justifié.
- La réplication des données selon le besoin.
- La réduction des journaux non nécessaires.
- Le dimensionnement des ressources.
- La suppression des environnements inutilisés.

Toute mise en cache ou réplication doit préciser les conséquences sur la fraîcheur des données, la cohérence et la reprise après incident.

## 18.4. Tableau de contrôle des coûts

| Ressource | Coût estimé | Utilisation observée | Action possible |
|---|---:|---:|---|
| Calcul cloud | À renseigner | À mesurer | Ajuster le dimensionnement |
| Stockage principal | À renseigner | À mesurer | Réduire les copies inutiles |
| Sauvegarde | À renseigner | À mesurer | Revoir la rétention selon les besoins |
| VPN | À renseigner | Débit mesuré | Vérifier la capacité nécessaire |
| Transferts | À renseigner | Volume mesuré | Optimiser les chemins |
| Journaux | À renseigner | Volume mensuel | Définir une rétention adaptée |
| Test | À renseigner | Temps d'activité | Arrêter les ressources inutilisées |

Les coûts doivent être mesurés sur une période représentative, puis comparés aux objectifs métier.


# 19. Défi 15 — Migration d'une application vers le cloud

La migration d'une application ne se résume pas à créer une machine virtuelle.

Elle nécessite une préparation technique, un inventaire des dépendances, une validation de sécurité et un plan de retour arrière.

## 19.1. Phase 1 — Découverte

Recueillez :

- La configuration de l'application.
- Les adresses utilisées.
- Les dépendances DNS.
- Les connexions aux bases de données.
- Les accès aux fichiers.
- Les besoins d'authentification.
- Les ports utilisés.
- Les contraintes de certificat.
- Les volumes de trafic.
- Les besoins de supervision.
- Les exigences de sauvegarde.

## 19.2. Phase 2 — Préparation

Avant la migration :

1. Préparer les réseaux cloud.
2. Préparer les routes.
3. Définir les règles de sécurité.
4. Valider le DNS.
5. Configurer les identités.
6. Préparer la supervision.
7. Vérifier les sauvegardes.
8. Tester les accès aux dépendances locales.
9. Préparer un environnement de validation.
10. Définir le retour arrière.

## 19.3. Phase 3 — Validation

Dans l'environnement de test :

- Vérifier l'accès à l'application.
- Tester les dépendances.
- Tester le comportement avec une latence représentative.
- Vérifier la sécurité.
- Tester les erreurs et les timeouts.
- Vérifier le DNS.
- Mesurer les performances.
- Vérifier les journaux.
- Réaliser un test de restauration.

## 19.4. Phase 4 — Bascule

Une procédure de bascule doit préciser :

- La fenêtre de changement.
- Les personnes responsables.
- Les opérations de préparation.
- La méthode de bascule DNS ou de publication.
- Les tests immédiatement après migration.
- Les seuils d'arrêt.
- Le retour vers l'ancien environnement.
- La façon de traiter les données modifiées pendant la bascule.

Le temps de propagation DNS n'est pas un mécanisme de synchronisation des données. Si l'application écrit dans une base, la cohérence des données doit être traitée séparément.

## 19.5. Architecture avant et après migration

### Avant

```text
UTILISATEURS
     |
     v
RÉSEAU LOCAL
     |
     v
APPLICATION LOCALE
     |
     v
BASE LOCALE
```

### Pendant la phase hybride

```text
UTILISATEURS
     |
     v
FRONTEND CLOUD
     |
     v
API CLOUD
     |
  VPN / LIEN PRIVÉ
     |
     v
BASE LOCALE
```

### Cible éventuelle

```text
UTILISATEURS
     |
     v
FRONTEND CLOUD
     |
     v
API CLOUD
     |
     v
BASE CLOUD
     |
     v
SAUVEGARDE SÉPARÉE
```

La cible éventuelle n'est pas automatiquement la meilleure solution. Elle dépend de la performance, des contraintes de sécurité, de la cohérence des données et de la capacité de l'entreprise à exploiter le nouveau modèle.


# 20. Défi expert — Reprise après sinistre hybride

La reprise après sinistre doit être conçue pour les applications, les données, le réseau et l'identité.

Une application peut être restaurée alors que le DNS pointe encore vers l'ancien environnement, que les routes ne sont pas prêtes ou que les comptes nécessaires sont indisponibles.

## 20.1. Les composants à prendre en compte

- Les images ou artefacts applicatifs.
- Les données et bases.
- Les paramètres d'application.
- Les secrets.
- Les certificats.
- Les identités.
- Les routes.
- Les règles de sécurité.
- Le DNS.
- Les sauvegardes.
- Les journaux.
- Les outils d'administration.

## 20.2. Architecture de reprise

```text
                    ENVIRONNEMENT PRINCIPAL
                              |
                   +----------+----------+
                   |                     |
                   v                     v
              APPLICATION            BASE DE DONNÉES
                   |                     |
                   +----------+----------+
                              |
                      SAUVEGARDES / COPIES
                              |
                              v
                    ENVIRONNEMENT DE SECOURS
                              |
                  +-----------+-----------+
                  |                       |
                  v                       v
             APPLICATION              DONNÉES
             DE SECOURS                RESTAURÉES
                  |
                  v
           TESTS AVANT REMISE
           EN SERVICE UTILISATEUR
```

L'environnement de secours peut être un autre site, une région cloud différente ou une autre architecture approuvée.

Le schéma ne signifie pas qu'une copie de données suffit à assurer la reprise : les identités, les routes, les certificats, les configurations et les dépendances doivent aussi être disponibles.

## 20.3. Exercices de reprise

Testez au moins les scénarios suivants :

1. Perte du tunnel hybride.
2. Perte de l'application cloud.
3. Perte de la base de données locale.
4. Perte de la résolution DNS.
5. Perte d'un compte administratif.
6. Perte d'une copie de sauvegarde.
7. Restauration de l'application dans un environnement différent.
8. Modification des routes vers une ressource de secours.
9. Bascule DNS.
10. Retour vers l'environnement principal.

Chaque scénario doit préciser les conditions de démarrage, les responsabilités, les validations et les critères d'arrêt.

## 20.4. RPO et RTO

Pour chaque application critique, définissez :

- Le RPO : quantité maximale de données que l'entreprise accepte de perdre.
- Le RTO : délai cible de remise en service.

Exemple de fiche :

| Élément | Valeur à définir |
|---|---|
| Application | À renseigner |
| Criticité | À renseigner |
| RPO cible | À convenir avec le responsable métier |
| RTO cible | À convenir avec le responsable métier |
| Source de sauvegarde | À renseigner |
| Environnement de reprise | À renseigner |
| Dépendances réseau | À documenter |
| Dépendances DNS et identité | À documenter |
| Dernier test de restauration | À renseigner |
| Résultat du dernier test | À renseigner |

Les objectifs doivent être réalistes et démontrés par des tests. Une réplication fréquente ne garantit pas que la restauration complète sera assez rapide.


# 21. Scénarios de dépannage

## Scénario A — Le VPN est actif, mais l'application cloud est inaccessible

### Hypothèses

- Route locale manquante.
- Route cloud manquante.
- Mauvaise adresse de passerelle.
- Filtrage local.
- Règle de sécurité cloud.
- Service arrêté.
- DNS incorrect.
- Chemin retour absent.
- Problème MTU.

### Démarche

1. Vérifier le sous-réseau du client.
2. Vérifier sa passerelle.
3. Vérifier la route locale vers le cloud.
4. Vérifier l'état et les compteurs du tunnel.
5. Vérifier la route retour.
6. Tester l'adresse IP et le port du service.
7. Vérifier la résolution DNS.
8. Consulter les règles et les journaux.
9. Tester le service depuis une source cloud autorisée.
10. Valider le retour du trafic.

Ne vous arrêtez pas à l'indicateur « tunnel actif ».


## Scénario B — Le cloud accède au serveur local, mais le poste utilisateur n'y accède pas

### Hypothèses

- Règle du pare-feu local.
- Routage entre VLAN.
- Politique qui différencie les sources.
- Adresse source inattendue.
- DNS différent.
- Service accessible uniquement depuis un sous-réseau autorisé.
- Problème de retour.

### Démarche

1. Comparer les adresses IP sources.
2. Comparer les chemins réseau.
3. Vérifier les routes et les règles.
4. Examiner les journaux côté local.
5. Tester le service à partir de deux sources.
6. Vérifier la résolution DNS.
7. Corriger la politique sans élargir inutilement les accès.


## Scénario C — Le VPN fonctionne, mais les transferts sont très lents

### Hypothèses

- Bande passante limitée.
- Latence élevée.
- Saturation du pare-feu.
- MTU incorrect.
- Perte de paquets.
- Volume de requêtes excessif.
- Mauvaise architecture d'accès aux données.
- Trafic de sauvegarde concurrent.

### Démarche

1. Mesurer la latence.
2. Mesurer le débit.
3. Comparer avec la capacité du lien.
4. Examiner les compteurs d'interface.
5. Vérifier la charge du pare-feu.
6. Observer les retransmissions.
7. Vérifier le MTU.
8. Comparer le volume des appels applicatifs.
9. Contrôler les tâches concurrentes.
10. Mesurer l'effet des changements.


## Scénario D — L'application cloud ne résout plus les noms internes

### Hypothèses

- DNS local indisponible.
- Route vers le résolveur absente.
- Règles de sécurité.
- Résolveur incorrect.
- Résolution conditionnelle mal configurée.
- Enregistrement manquant.
- Cache DNS incorrect.
- Dépendance au tunnel.

### Démarche

1. Identifier le résolveur utilisé.
2. Effectuer une requête ciblée.
3. Vérifier la route.
4. Contrôler les règles de filtrage.
5. Examiner les enregistrements.
6. Vérifier les journaux DNS.
7. Tester depuis une autre source.
8. Documenter les dépendances DNS.


## Scénario E — Une application de test peut accéder à la production

### Gravité

Élevée si la séparation entre les environnements est une exigence.

### Hypothèses

- Routes trop larges.
- Règles de sécurité permissives.
- Peering ou connexion entre réseaux trop largement autorisé.
- Mauvaise association de sous-réseau.
- Permissions IAM trop étendues.
- Chemin alternatif.
- Contrôle incomplet côté système d'exploitation.

### Démarche

1. Identifier la source et la destination.
2. Vérifier l'adresse IP réelle.
3. Déterminer le chemin.
4. Examiner les routes et règles.
5. Vérifier les permissions de la ressource cible.
6. Corriger au point de contrôle approprié.
7. Tester un accès autorisé depuis test.
8. Vérifier que les flux de production légitimes fonctionnent toujours.
9. Documenter le risque résiduel.


## Scénario F — Les utilisateurs ne peuvent plus s'authentifier

### Hypothèses

- Annuaire local indisponible.
- Résolution DNS.
- Synchronisation d'identité défaillante.
- Certificat expiré.
- Service d'authentification cloud indisponible.
- Erreur de configuration ou changement récent.
- Problème d'heure sur les systèmes.

### Démarche

1. Identifier le mécanisme d'authentification.
2. Vérifier la portée de l'incident.
3. Vérifier la résolution DNS et la connectivité.
4. Examiner les journaux d'authentification.
5. Vérifier l'état des certificats et leur validité.
6. Contrôler les horloges.
7. Tester avec un compte de diagnostic autorisé.
8. Vérifier la procédure d'accès d'urgence.
9. Ne pas désactiver la sécurité pour rétablir rapidement tous les accès.


# 22. Défi expert — Incident combiné

Vous êtes d'astreinte et les incidents suivants apparaissent simultanément :

1. Les utilisateurs locaux ne peuvent plus accéder à l'application cloud.
2. Le tunnel VPN est déclaré actif.
3. L'API cloud ne joint plus la base locale.
4. Les journaux montrent des échecs de résolution DNS.
5. Les règles de sécurité ont été modifiées récemment.
6. Le trafic vers le cloud a augmenté.
7. Le réseau de test peut établir une connexion inattendue vers une ressource de production.

Vous ignorez si ces incidents ont une cause commune.

## 22.1. Règles de l'intervention

Vous devez :

- Préserver les journaux.
- Identifier la portée de chaque incident.
- Prioriser l'exposition de production.
- Garder un accès administratif autorisé.
- Ne pas désactiver globalement les règles.
- Ne pas supprimer les routes sans connaître leur usage.
- Ne pas modifier simultanément le DNS, le routage et le filtrage.
- Documenter les changements.
- Vérifier les tests positifs et négatifs après chaque correction.

## 22.2. Première phase — Collecte

| Symptôme | Première vérification |
|---|---|
| Application inaccessible | Source, destination, port et route |
| VPN actif | Compteurs, trafic réel et routes |
| API vers base en échec | Adresse cible, règles, chemin retour |
| DNS en échec | Résolveur, réponse et connectivité |
| Modification récente | Historique du changement |
| Trafic augmenté | Débit, volume, charge et point d'origine |
| Test vers production | Source réelle, route, filtrage et droits |

## 22.3. Deuxième phase — Isoler les causes

Pour chaque symptôme, établissez :

- Ce qui fonctionne encore.
- Ce qui est en échec.
- Le moment où l'incident a commencé.
- Les changements survenus juste avant.
- Les équipements traversés.
- Les règles applicables.
- Les logs disponibles.
- Les dépendances impliquées.

Ne partez pas du principe que le VPN est la cause simplement parce qu'une application est inaccessible à distance.

## 22.4. Troisième phase — Correction

Pour chaque problème :

1. Formulez une hypothèse.
2. Cherchez une preuve.
3. Identifiez le changement minimal.
4. Sauvegardez les configurations concernées.
5. Réalisez le changement.
6. Vérifiez le résultat.
7. Vérifiez les autres flux.
8. Documentez la cause et les actions préventives.

## 22.5. Rapport d'incident

Le rapport doit contenir :

- La chronologie.
- Les services affectés.
- Les tests effectués.
- Les hypothèses retenues ou rejetées.
- Les preuves.
- La cause racine démontrée.
- Les modifications réalisées.
- Les tests de non-régression.
- Les conséquences sur la sécurité.
- Les risques résiduels.
- Les recommandations.

Une hypothèse raisonnable ne devient une cause racine que lorsqu'elle est confirmée par des éléments observables.


# 23. Architecture cible consolidée

## 23.1. Schéma global

```text
                        UTILISATEURS LOCAUX
                                |
                                v
                    +-------------------------+
                    | RÉSEAU LOCAL            |
                    | Utilisateurs / Serveurs  |
                    | Administration          |
                    +-------------------------+
                                |
                         +--------------+
                         | PARE-FEU     |
                         | POLITIQUES   |
                         | ROUTAGE      |
                         +--------------+
                                |
                      VPN IPsec ou liaison privée
                                |
                                v
                    +-------------------------+
                    | HUB / PASSERELLE CLOUD  |
                    | Routage / Contrôles     |
                    +-------------------------+
                       |           |           |
                       v           v           v
                  +---------+ +---------+ +---------+
                  | PROD    | | TEST    | | SERVICES|
                  | APPS    | | APPS    | | PARTAGÉS|
                  +---------+ +---------+ +---------+
                       |
                       v
                SERVICES APPLICATIFS
                       |
                       v
                BASE DE DONNÉES
                SELON LA TOPOLOGIE
                       |
                       v
                SAUVEGARDE DISTINCTE


                  PLAN D'ADMINISTRATION
                           |
                    Identités / IAM
                           |
                    Bastion / Console
                           |
                 Accès limité aux ressources


                  OBSERVABILITÉ HYBRIDE
                           |
             +-------------+--------------+
             |             |              |
             v             v              v
           Réseau        Cloud          Applications
           local        et IAM          et données
```

Ce schéma décrit les principaux domaines. Le dossier final doit préciser les routes, les interfaces, les sous-réseaux, les règles de sécurité et les chemins réels.

## 23.2. Résumé des décisions

| Domaine | Décision de référence |
|---|---|
| Connectivité initiale | VPN site-à-site |
| Adressage | Réseaux locaux et cloud sans chevauchement |
| Production | Réseau logique distinct |
| Test | Réseau indépendant de la production |
| Administration | Identités dédiées, permissions limitées et bastion selon le besoin |
| Routage | Routes explicites et retour contrôlé |
| DNS | Résolution interne et cloud documentée |
| Sécurité | Règles locales et cloud cohérentes |
| Identité | Moindre privilège et journalisation |
| Services privés | Accès privé lorsque disponible et adapté |
| Résilience | Chemins de secours définis selon les objectifs |
| Supervision | Journaux et métriques corrélés |
| Sauvegarde | Copies protégées et restauration testée |
| Automatisation | Code versionné, validation et retour arrière |
| Coûts | Mesures et contrôles réguliers |
| Migration | Tests, bascule documentée et possibilité de retour arrière |


# 24. Barème d'évaluation sur 100 points

| Domaine évalué | Points |
|---|---:|
| Analyse des besoins et dépendances | 8 |
| Architecture physique et logique | 8 |
| Plan d'adressage et segmentation | 8 |
| Routage hybride | 10 |
| VPN et connectivité privée | 7 |
| DNS hybride | 7 |
| Sécurité réseau et IAM | 12 |
| Haute disponibilité et reprise | 8 |
| Supervision et journalisation | 6 |
| Infrastructure as Code | 7 |
| Gestion des coûts cloud | 5 |
| Migration et retour arrière | 6 |
| Dépannage et rapport d'incident | 8 |
| **Total** | **100** |

## 24.1. Critères d'excellence

Une solution de qualité doit :

- Expliquer pourquoi chaque environnement existe.
- Définir des routes cohérentes.
- Éviter les chevauchements IP.
- Contrôler les flux dans les deux directions.
- Protéger les identités.
- Préserver la séparation entre test et production.
- Démontrer la disponibilité du service de bout en bout.
- Prévoir des tests de panne.
- Documenter les coûts et leurs facteurs principaux.
- Protéger les sauvegardes.
- Prévoir des changements reproductibles.
- Présenter les risques résiduels.

## 24.2. Erreurs graves

Les erreurs suivantes entraînent une pénalité importante :

- Autoriser tout le réseau cloud vers le réseau local sans justification.
- Supposer qu'un VPN actif signifie que les applications fonctionnent.
- Utiliser des plages IP qui se chevauchent entre environnements.
- Omettre les routes retour.
- Exposer publiquement une ressource qui doit rester privée.
- Donner des permissions administratives trop larges.
- Stocker des clés ou secrets dans le code.
- Oublier les conséquences DNS pendant la migration.
- Considérer le cloud comme indépendant du réseau local lorsque les applications ont encore des dépendances sur site.
- Ne pas tester la restauration.
- Modifier les règles de production sans retour arrière.
- Ignorer les coûts de transfert ou de journalisation.
- Déclarer la solution validée sans tests observables.


# 25. Modèle du dossier final

## 25.1. Résumé exécutif

Présentez :

- Le contexte de l'entreprise.
- Le périmètre de migration.
- Les applications concernées.
- L'architecture proposée.
- Les bénéfices attendus.
- Les risques et dépendances.
- Les décisions budgétaires nécessaires.

## 25.2. Architecture réseau

Fournissez :

- Un schéma de l'infrastructure locale.
- Un schéma du réseau cloud.
- Le chemin VPN ou privé.
- Les tables de routage.
- Le plan IP.
- Les zones de sécurité.
- Les chemins d'administration.
- Les services DNS.
- Les réseaux de sauvegarde.
- Les mécanismes de redondance.

## 25.3. Matrice de flux

Chaque flux doit préciser :

| Champ | Description |
|---|---|
| ID | Identifiant unique |
| Source | Réseau ou ressource source |
| Destination | Réseau ou ressource cible |
| Protocole | TCP, UDP, ICMP ou autre |
| Port | Port réellement nécessaire |
| Justification | Besoin métier ou technique |
| Point de filtrage | Pare-feu, règle cloud ou autre |
| Journalisation | Événements à conserver |
| Tests | Vérifications positives et négatives |
| Responsable | Personne ou équipe responsable |

## 25.4. Procédure de migration

Documentez :

- Les prérequis.
- La sauvegarde préalable.
- Les dépendances.
- Le plan de test.
- La fenêtre de changement.
- Les étapes de bascule.
- Les critères d'acceptation.
- La procédure de retour arrière.
- Les risques résiduels.
- Les responsables.

## 25.5. Tableau de validation

| ID | Test | Résultat attendu | Résultat obtenu | Statut |
|---|---|---|---|---|
| T01 | VPN | Tunnel établi et trafic de test fonctionnel | À renseigner | À exécuter |
| T02 | Route locale vers cloud | Route correcte | À renseigner | À exécuter |
| T03 | Route retour cloud vers local | Route correcte | À renseigner | À exécuter |
| T04 | DNS local vers nom cloud | Résolution attendue | À renseigner | À exécuter |
| T05 | API cloud vers base locale | Flux autorisé fonctionnel | À renseigner | À exécuter |
| T06 | Test vers production | Accès non autorisé refusé | À renseigner | À exécuter |
| T07 | Administration cloud | Accès selon le rôle | À renseigner | À exécuter |
| T08 | Perte de tunnel | Comportement conforme au plan | À renseigner | À exécuter |
| T09 | Supervision | Métriques et journaux disponibles | À renseigner | À exécuter |
| T10 | Restauration | Service restauré et validé | À renseigner | À exécuter |
| T11 | Coûts | Estimation comparée à l'utilisation | À renseigner | À exécuter |
| T12 | Retour arrière | Procédure exécutée ou validée en test | À renseigner | À exécuter |

Un statut « OK » doit correspondre à un test réellement effectué. Les résultats inconnus doivent rester indiqués comme à exécuter.


# 26. Checklist finale

## Conception

- [ ] Les besoins métier sont documentés.
- [ ] Les applications et leurs dépendances sont inventoriées.
- [ ] Les environnements local et cloud sont cartographiés.
- [ ] Le plan IP ne comporte pas de chevauchement.
- [ ] Les réseaux de production et de test sont distincts.
- [ ] Les besoins de performance sont évalués.
- [ ] Les besoins de disponibilité sont définis.
- [ ] Les services critiques sont identifiés.

## Connectivité

- [ ] Le tunnel ou la liaison privée est documenté.
- [ ] Les routes locales sont correctes.
- [ ] Les routes cloud sont correctes.
- [ ] Les chemins retour sont vérifiés.
- [ ] Le DNS est adapté aux deux environnements.
- [ ] Le MTU est cohérent.
- [ ] Les limites de bande passante sont connues.
- [ ] Les pannes de liaison ont été étudiées.

## Sécurité

- [ ] Les règles de sécurité sont documentées.
- [ ] Les flux non nécessaires sont refusés.
- [ ] Les bases ne sont pas exposées publiquement par défaut.
- [ ] Les rôles IAM sont adaptés.
- [ ] Les comptes administratifs sont protégés.
- [ ] Les secrets sont stockés de manière appropriée.
- [ ] Les ressources de test sont séparées de la production.
- [ ] Les règles IPv4 et IPv6 sont cohérentes lorsque les deux protocoles sont utilisés.
- [ ] Les journaux sont accessibles et protégés.

## Exploitation

- [ ] Les ressources cloud sont documentées.
- [ ] Les coûts récurrents sont suivis.
- [ ] La supervision couvre toute la chaîne du service.
- [ ] Les sauvegardes sont protégées.
- [ ] Les restaurations sont testées.
- [ ] La procédure de changement est définie.
- [ ] Le retour arrière est documenté.
- [ ] L'automatisation est versionnée et validée.
- [ ] Les dépendances de reprise sont connues.

## Validation

- [ ] Les flux autorisés fonctionnent.
- [ ] Les flux interdits sont bloqués.
- [ ] Les applications critiques ont été testées.
- [ ] Les pannes représentatives ont été étudiées.
- [ ] Les journaux permettent de diagnostiquer les incidents.
- [ ] Les résultats des tests sont consignés.
- [ ] Les risques résiduels sont documentés.
- [ ] L'architecture peut être maintenue par une autre personne de l'équipe.


# 27. Références techniques à consulter

Pour approfondir les technologies abordées, consultez notamment :

- **RFC 1918 — Address Allocation for Private Internets** : plages IPv4 privées.
- **RFC 7296 — Internet Key Exchange Protocol Version 2 (IKEv2)** : établissement et gestion des associations de sécurité IPsec.
- **RFC 4301 — Security Architecture for the Internet Protocol** : architecture de sécurité IPsec.
- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)** : routage BGP, lorsque ce protocole est utilisé.
- **Documentation du fournisseur cloud choisi** : réseaux virtuels, sous-réseaux, routage, VPN, services privés et règles réseau.
- **Documentation IAM du fournisseur** : rôles, identités de service, permissions et audit.
- **Documentation du fournisseur DNS** : zones privées, résolution conditionnelle et intégration hybride.
- **Documentation officielle de l'outil IaC retenu** : plans, état, déploiement, gestion des secrets et changements.
- **Documentation Wireshark** : filtres de capture, filtres d'affichage et analyse des protocoles.
- **Documentation du système de sauvegarde** : restauration, rétention, immutabilité et contrôle des accès.

Les mécanismes disponibles, leur nom, leur tarification et leurs limites dépendent du fournisseur cloud et de l'offre choisie. Consultez sa documentation officielle avant de transformer les exemples pédagogiques en configuration réelle.


# Conclusion

Une architecture hybride doit être considérée comme un système unique du point de vue des dépendances, de la sécurité et de l'exploitation, même lorsque ses composants sont répartis entre un datacenter local et plusieurs services cloud.

La réussite du challenge repose sur six principes :

1. **Comprendre les dépendances :** aucune application ne doit être migrée sans identifier ses besoins en réseau, DNS, identité, données et services.
2. **Construire un routage cohérent :** les routes aller et retour doivent être documentées et vérifiées.
3. **Limiter les communications :** la connectivité ne doit jamais se transformer en accès général entre tous les environnements.
4. **Protéger les identités :** les droits réseau et cloud doivent être limités au besoin.
5. **Prévoir les incidents :** la supervision, la sauvegarde, la reprise et le retour arrière doivent être testés.
6. **Maîtriser les coûts :** les ressources, les transferts, les journaux et la connectivité doivent être suivis.

Le VPN n'est qu'un composant de l'architecture. La réussite repose sur la cohérence du routage, la qualité des contrôles de sécurité, la résolution DNS, la maîtrise des identités, la visibilité opérationnelle et la capacité à restaurer les services.

**La meilleure architecture hybride est celle qui permet aux applications de fonctionner entre les environnements sans créer de dépendances invisibles, d'accès excessifs ou de coûts incontrôlés.**