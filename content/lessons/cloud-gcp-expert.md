
# Google Cloud Platform — Niveau Expert
## Architecture d'entreprise, landing zones, sécurité avancée, SRE, résilience et FinOps

**Fichier :** `cloud-gcp-expert.md`  
**Niveau :** Expert  
**Domaine :** Architecture cloud, gouvernance, cybersécurité, réseau hybride, ingénierie de fiabilité et optimisation des coûts  
**Plateforme :** Google Cloud Platform (GCP)

## 1. Positionnement du niveau expert

Le niveau expert prolonge le niveau intermédiaire. Il ne consiste pas à multiplier les services Google Cloud, mais à savoir concevoir un système global dont la sécurité, la disponibilité, la gouvernance, les performances et les coûts sont maîtrisés.

L'expert doit être capable de justifier les décisions d'architecture, d'identifier les risques, de définir des objectifs mesurables, de construire des mécanismes de contrôle et de démontrer que l'organisation peut exploiter et restaurer ses systèmes.

### Compétences attendues

À la fin du cours, l'apprenant doit pouvoir :

- concevoir une landing zone Google Cloud pour une organisation ;
- structurer une hiérarchie d'organisation, de dossiers et de projets ;
- appliquer des stratégies de gouvernance et des contrôles préventifs ;
- concevoir un modèle IAM à grande échelle ;
- renforcer la protection des identités, des données et des charges de travail ;
- concevoir des réseaux hybrides et multi-région ;
- comparer les architectures de haute disponibilité et de reprise après sinistre ;
- appliquer les principes SRE, SLI, SLO, budgets d'erreur et réduction du travail répétitif ;
- sécuriser les chaînes CI/CD et la chaîne d'approvisionnement logicielle ;
- industrialiser l'Infrastructure as Code ;
- concevoir des stratégies FinOps ;
- produire une architecture argumentée, documentée, testable et exploitable.

## 2. Principes de conception à l'échelle entreprise

Une architecture experte doit équilibrer plusieurs objectifs qui peuvent entrer en conflit.

| Objectif | Question d'architecture |
|---|---|
| Sécurité | Qui peut accéder à quoi, et dans quelles conditions ? |
| Disponibilité | Quelle panne le système peut-il supporter ? |
| Performance | Quelle latence et quel débit sont nécessaires ? |
| Résilience | Comment récupérer après une panne ou une corruption ? |
| Gouvernance | Quels changements sont autorisés et contrôlés ? |
| Exploitabilité | Comment diagnostiquer et maintenir le système ? |
| Coût | Quel est le coût total de fonctionnement ? |
| Évolutivité | Comment augmenter la capacité sans refonte majeure ? |
| Conformité | Où les données sont-elles traitées et conservées ? |

Il n'existe pas une architecture universelle qui maximise tous ces critères. Les choix doivent partir des exigences métier, des risques et des contraintes mesurables.

## 3. Landing zone Google Cloud

### 3.1 Définition

Une landing zone est un socle de plateforme préparé pour accueillir des projets et des applications. Elle fournit des conventions, des mécanismes de sécurité, une organisation des ressources, des réseaux, une journalisation et des contrôles d'exploitation.

Elle ne se résume pas à un VPC. Elle couvre l'ensemble des éléments nécessaires pour créer, sécuriser, exploiter et gouverner les environnements cloud.

### 3.2 Architecture logique

```text
Organisation Google Cloud
|
+-- Dossier : Platform
|   |
|   +-- Projet : réseau central
|   +-- Projet : sécurité
|   +-- Projet : journalisation
|   +-- Projet : automatisation
|
+-- Dossier : Non-production
|   |
|   +-- Projet : application-dev
|   +-- Projet : application-test
|   +-- Projet : application-staging
|
+-- Dossier : Production
    |
    +-- Projet : application-prod
    +-- Projet : données-prod
    +-- Projet : services critiques

Services transverses :
- IAM et identité
- Stratégies d'organisation
- Journalisation et audit
- Gestion des secrets
- Réseau et connectivité
- Détection des menaces
- Facturation et budgets
- CI/CD et Infrastructure as Code
```

Cette architecture est un modèle conceptuel. Les projets exacts, les dossiers et les limites de confiance dépendent de la structure de l'entreprise.

### 3.3 Séparer les responsabilités

Il est souvent utile de séparer :
- l'administration du réseau ;
- l'administration de la sécurité ;
- la collecte et la conservation des journaux ;
- la construction des artefacts ;
- les environnements de développement ;
- les environnements de production.

Cette séparation réduit les risques de conflit de permissions et facilite les audits. Elle ne doit cependant pas créer un nombre excessif de projets sans propriétaire ni usage clairement définis.

### 3.4 Principes de conception

1. Créer les projets à partir de modèles contrôlés.
2. Appliquer les stratégies de sécurité au niveau approprié.
3. Éviter les droits d'administration permanents inutiles.
4. Centraliser les mécanismes communs lorsque cela est pertinent.
5. Prévoir des chemins d'exception documentés.
6. Contrôler les ressources créées hors des processus approuvés.
7. Suivre la consommation et le propriétaire de chaque projet.
8. Prévoir la désactivation et la suppression sécurisée des projets inutilisés.

## 4. Gouvernance : politiques d'organisation et contrôles

### 4.1 Gouvernance préventive et détective

Les contrôles préventifs empêchent ou limitent une action avant qu'elle ne se produise. Les contrôles détectifs identifient une situation non conforme après son apparition.

```text
Demande de création d'une ressource
              |
              v
      Contrôle préventif
              |
       +------+------+
       |             |
    Conforme      Non conforme
       |             |
       v             v
  Création      Refus ou exception
       |
       v
Contrôles détectifs
       |
       v
Journalisation, alertes et remédiation
```

Exemples de contrôles :
- limiter les régions autorisées selon les exigences ;
- empêcher les configurations de sécurité interdites ;
- restreindre la création de clés de comptes de service ;
- détecter les ressources publiques non autorisées ;
- identifier les projets sans propriétaire ;
- détecter les ressources dont la configuration dérive du standard.

### 4.2 Organization Policy

Les stratégies d'organisation Google Cloud permettent d'appliquer certaines contraintes à des ressources de la hiérarchie. Elles sont distinctes des politiques IAM : les stratégies d'organisation définissent des contraintes, tandis que IAM contrôle les permissions d'accès.

Une stratégie peut être héritée de l'organisation vers les dossiers et les projets, sous réserve de sa configuration et des règles de politique applicables.

Avant d'imposer une contrainte à l'ensemble de l'organisation :
1. identifier les projets concernés ;
2. inventorier les services utilisés ;
3. tester la stratégie dans un périmètre pilote ;
4. mesurer les effets sur les déploiements ;
5. prévoir les exceptions autorisées ;
6. déployer progressivement ;
7. surveiller les refus et les effets opérationnels.

### 4.3 Exemple de stratégie de gouvernance

Supposons que l'organisation souhaite empêcher la création de ressources dans des régions non approuvées.

Le processus est :

```text
Politique régionale approuvée
           |
           v
Inventaire des ressources existantes
           |
           v
Test sur un périmètre pilote
           |
           v
Détection des incompatibilités
           |
           v
Correction ou exception documentée
           |
           v
Application progressive
           |
           v
Surveillance continue
```

Ne copiez pas un nom de contrainte ou une configuration de stratégie sans vérifier sa disponibilité et sa syntaxe dans la version actuelle de Google Cloud. Les contraintes disponibles et leurs comportements varient selon le service et peuvent évoluer.

### 4.4 Exception de gouvernance

Une exception doit contenir :
- le contrôle concerné ;
- le besoin métier ;
- le périmètre précis ;
- le responsable ;
- le risque accepté ;
- les mesures compensatoires ;
- la date d'expiration ;
- la procédure de réexamen.

Une exception permanente sans propriétaire devient progressivement une faille de gouvernance.

## 5. IAM à grande échelle

### 5.1 Modèle d'accès

```text
Identité humaine ou workload
             |
             v
      Authentification
             |
             v
      Évaluation IAM
             |
             +-- Rôles attribués
             +-- Héritage des rôles
             +-- Conditions éventuelles
             +-- Contraintes applicables
             |
             v
      Autorisation ou refus
             |
             v
      Journalisation selon le service
```

L'évaluation réelle peut également impliquer des stratégies de refus, des contrôles de périmètre et des mécanismes propres au service. Il ne faut pas réduire l'analyse d'accès à la seule liste des rôles directement affectés au projet.

### 5.2 Identités humaines et identités applicatives

Une identité humaine sert à une personne. Une identité de workload sert à une application ou à un processus automatisé.

Ces identités doivent être distinguées :

```text
Administrateur
    |
    +-- Accès administratif contrôlé
    +-- Opérations ponctuelles
    +-- Audit des changements

Pipeline CI/CD
    |
    +-- Identité de construction
    +-- Permissions limitées aux artefacts

Application
    |
    +-- Identité d'exécution
    +-- Accès aux données nécessaires uniquement
```

Ne partagez pas une identité administrative entre plusieurs applications. Une compromission aurait alors un rayon d'impact plus important.

### 5.3 Workload Identity Federation

Workload Identity Federation permet à certains workloads externes ou à des environnements compatibles d'obtenir des identités reconnues par Google Cloud sans devoir conserver une clé JSON de compte de service.

Le modèle dépend du fournisseur d'identité et de la configuration du pool et du fournisseur.

```text
Pipeline externe
      |
      v
Identité du fournisseur
      |
      v
Fédération d'identité
      |
      v
Principal reconnu par Google Cloud
      |
      v
Permissions IAM limitées
      |
      v
Ressource cible
```

Points de contrôle :
- restreindre les identités externes autorisées ;
- vérifier l'émetteur et les attributs des jetons ;
- limiter les dépôts, branches, environnements ou workloads admis ;
- éviter les conditions trop larges ;
- limiter les rôles de la ressource cible ;
- tester la révocation et la rotation des paramètres concernés.

La fédération d'identité réduit la dépendance aux clés persistantes, mais elle ne rend pas automatiquement un pipeline digne de confiance. Si le dépôt ou le workflow est compromis, les permissions du pipeline restent exploitables.

### 5.4 Accès privilégié

Les accès d'administration devraient être accordés uniquement lorsque nécessaire, avec une durée limitée lorsque les outils disponibles le permettent, une approbation adaptée au risque et une journalisation.

Principes :
- comptes administratifs distincts des comptes de travail ordinaires ;
- authentification forte ;
- permissions ciblées ;
- procédures de secours testées ;
- examen périodique des accès ;
- suppression rapide des accès inutilisés.

### 5.5 Audit des autorisations

L'audit doit examiner :
- les rôles au niveau de l'organisation ;
- les rôles hérités des dossiers ;
- les rôles des projets ;
- les autorisations sur les ressources individuelles ;
- les conditions IAM ;
- les comptes de service et leurs rôles ;
- les clés persistantes éventuelles ;
- les identités inactives ;
- les accès privilégiés et les exceptions.

Le résultat attendu n'est pas simplement un export JSON. Il faut identifier les permissions inutiles, les accès excessifs, les identités orphelines et les risques associés.

## 6. Protection des données et architecture de sécurité

### 6.1 Classification des données

Une entreprise devrait classer ses données selon leur sensibilité et leurs exigences de protection.

Exemple de modèle interne :

| Classe | Exemple conceptuel | Contrôles à envisager |
|---|---|---|
| Publique | Documentation publiée | Intégrité et disponibilité |
| Interne | Documentation opérationnelle | Accès limité à l'organisation |
| Confidentielle | Données commerciales | IAM restrictif, journalisation et protection renforcée |
| Très sensible | Secrets ou données réglementées | Accès exceptionnellement limité, contrôles renforcés et procédures de récupération |

Les catégories exactes doivent être définies par l'organisation. Le tableau n'est pas une classification réglementaire universelle.

### 6.2 Chiffrement

Il faut distinguer :
- le chiffrement au repos ;
- le chiffrement en transit ;
- la gestion des clés ;
- la rotation des clés ;
- le contrôle des opérations cryptographiques ;
- la récupération en cas de perte ou de désactivation d'une clé.

Les services Google Cloud fournissent généralement un chiffrement au repos par défaut, selon le service et sa configuration. Les exigences avancées peuvent nécessiter des clés gérées par le client et Cloud KMS.

L'utilisation de clés gérées par le client augmente le contrôle, mais également les responsabilités opérationnelles. La désactivation ou la destruction d'une clé peut rendre les données inaccessibles.

### 6.3 Cloud KMS

Cloud Key Management Service permet de gérer des clés cryptographiques utilisées par des services compatibles ou par des applications.

Les décisions à prendre comprennent :
- le type de clé ;
- la localisation ;
- les identités autorisées à utiliser ou administrer la clé ;
- les besoins de rotation ;
- les journaux d'audit ;
- les procédures de secours ;
- les règles de destruction ;
- la séparation entre administration des clés et administration des données.

Une personne qui peut administrer une clé n'a pas nécessairement besoin d'accéder aux données protégées, et inversement. Cette séparation peut limiter les risques internes.

### 6.4 Protection contre la perte de données

Une stratégie de données doit couvrir :
- les erreurs humaines ;
- les suppressions accidentelles ;
- les corruptions logiques ;
- les compromissions de comptes ;
- les rançongiciels ;
- les pannes régionales ;
- les défaillances de configuration ;
- les exigences de conservation légale.

Les mécanismes peuvent inclure des sauvegardes, la rétention, le versionnement, la réplication et des copies séparées. Ils ne sont pas interchangeables et doivent être validés par des tests de restauration.

## 7. Sécurité du périmètre et des workloads

### 7.1 Défense en profondeur

```text
Utilisateurs et workloads
          |
          v
Identité forte et autorisation
          |
          v
Point d'entrée contrôlé
          |
          v
Réseau et filtrage
          |
          v
Application et dépendances
          |
          v
Données protégées

Transversal :
- Journalisation
- Détection
- Gestion des secrets
- Gestion des vulnérabilités
- Réponse aux incidents
```

### 7.2 Cloud Armor

Cloud Armor peut fournir des protections applicables aux architectures compatibles avec ses mécanismes d'intégration, notamment des politiques de sécurité de couche applicative.

Selon les besoins et la configuration, les contrôles peuvent inclure :
- des règles de filtrage ;
- des listes d'adresses ;
- des règles fondées sur des conditions ;
- des protections contre certaines attaques web ;
- des politiques de limitation ou de traitement des requêtes prises en charge.

Cloud Armor ne remplace pas la validation des entrées, les contrôles d'identité, les correctifs applicatifs ni la gestion des secrets.

### 7.3 Protection contre l'exfiltration

VPC Service Controls peut contribuer à réduire certains risques d'exfiltration pour des services et ressources pris en charge en définissant des périmètres de service.

Ce mécanisme ne constitue pas une protection universelle pour tout le trafic réseau ou chaque API. Il faut vérifier les services couverts, les accès nécessaires, les ponts éventuels, les identités et les chemins de communication.

Processus de conception :

```text
Identifier les données sensibles
            |
            v
Identifier les services concernés
            |
            v
Définir le périmètre de confiance
            |
            v
Lister les flux légitimes
            |
            v
Tester les accès attendus
            |
            v
Tester les accès non autorisés
            |
            v
Déployer et surveiller
```

Un périmètre trop strict peut bloquer des flux légitimes, y compris des tâches d'administration et de maintenance. Il doit être testé avant un déploiement global.

### 7.4 Sécurité des images de conteneurs

La chaîne de sécurité des conteneurs doit inclure :
- des images de base maintenues ;
- une analyse des vulnérabilités ;
- une provenance traçable ;
- des dépendances maîtrisées ;
- des identités de construction limitées ;
- des artefacts immuables ou référencés par digest ;
- des règles de déploiement ;
- une procédure de correction des vulnérabilités.

Un tag tel que `latest` ne constitue pas une identification immuable de l'image. Pour un déploiement reproductible, l'identification par digest est préférable lorsqu'elle est prise en charge par le processus.

## 8. Architecture réseau hybride et multi-région

### 8.1 Architecture réseau d'entreprise

```text
                Réseau du siège
                      |
                Routeurs locaux
                      |
               Connexions hybrides
                      |
           +----------+----------+
           |                     |
       Région A              Région B
           |                     |
       VPC principal         VPC secondaire
           |                     |
       Applications          Applications
           |                     |
       Services privés       Services privés
           |                     |
           +---- Données et dépendances ----+
```

Ce schéma ne signifie pas que tous les flux sont automatiquement routés entre les régions. Il faut définir les connexions, le routage, les règles de sécurité et les mécanismes de bascule.

### 8.2 Modèle hub-and-spoke

Le modèle hub-and-spoke centralise certains services réseau dans un réseau central et relie les réseaux des applications selon des mécanismes appropriés.

```text
                   Réseau Hub
                /      |      \
               /       |       \
          Spoke A   Spoke B   Spoke C
             |         |         |
         Application Application Application
```

Avantages possibles :
- centralisation de certains contrôles ;
- réduction de la duplication ;
- gestion cohérente de la connectivité ;
- séparation entre réseau central et charges de travail.

Risques :
- dépendance à des composants centraux ;
- complexité de routage ;
- limites de capacité ;
- impact potentiel d'une mauvaise configuration globale.

La conception doit préciser les domaines de routage, les plages IP, les règles de filtrage, les chemins de sortie et les responsabilités d'exploitation.

### 8.3 Shared VPC

Shared VPC permet à des ressources de projets de service d'utiliser des sous-réseaux d'un projet hôte configuré à cet effet.

Il peut séparer la gestion du réseau de celle des applications.

```text
Projet hôte
|
+-- VPC partagé
    |
    +-- Sous-réseau A
    |   +-- Ressources d'un projet de service
    |
    +-- Sous-réseau B
        +-- Ressources d'un autre projet de service
```

Les permissions du projet hôte, les rôles réseau, les projets de service et les règles de pare-feu doivent être conçus ensemble. Le Shared VPC ne remplace pas une architecture IAM adaptée.

### 8.4 Connectivité hybride résiliente

Une architecture hybride résiliente doit étudier :
- les équipements et liens côté entreprise ;
- les passerelles cloud ;
- la redondance des tunnels ou circuits ;
- le routage dynamique ou statique ;
- les annonces BGP ;
- les plages IP ;
- les MTU ;
- la supervision des chemins ;
- les scénarios de bascule ;
- les dépendances DNS.

La redondance théorique n'est pas suffisante. Il faut provoquer des défaillances contrôlées, mesurer la bascule et vérifier que les applications récupèrent correctement.

### 8.5 DNS hybride

Les problèmes DNS peuvent ressembler à des problèmes réseau : un service peut être accessible par adresse IP mais pas par nom.

Il faut documenter :
- les zones privées ;
- les zones publiques ;
- les transferts ou redirections de requêtes ;
- les résolveurs autorisés ;
- les règles de résolution entre réseau local et cloud ;
- les dépendances des applications ;
- les comportements lors d'une panne.

La stratégie DNS doit être cohérente avec le routage et la segmentation. Une résolution réussie ne garantit pas que la connexion au service est autorisée.

## 9. Architecture multi-région et haute disponibilité

### 9.1 Ne pas confondre les niveaux de disponibilité

- **Redondance de composants :** plusieurs instances ou composants peuvent supporter certaines pannes.
- **Haute disponibilité zonale :** la solution peut continuer à fonctionner en cas de panne d'une zone, si tous les éléments nécessaires sont redondés.
- **Haute disponibilité régionale :** la solution peut résister à certaines pannes à l'échelle régionale.
- **Reprise après sinistre :** la solution peut être restaurée après un scénario de perte majeure selon un plan défini.

Une architecture multizone ne garantit pas une reprise après sinistre régionale.

### 9.2 Modèles de déploiement

```text
Modèle A : une seule zone
Utilisateur -> Zone A -> Application et données

Modèle B : plusieurs zones d'une région
Utilisateur -> Répartition du trafic
                     |
             +-------+-------+
             |               |
           Zone A           Zone B

Modèle C : deux régions
Utilisateur -> Routage global
                     |
             +-------+-------+
             |               |
          Région A         Région B
```

Le modèle multi-région peut améliorer la résilience, mais ajoute des contraintes de cohérence des données, de routage, de déploiement et de coût.

### 9.3 Architecture active-active

Deux régions servent simultanément du trafic.

Avantages possibles :
- capacité distribuée ;
- possibilité de continuer à servir du trafic en cas de panne d'une région ;
- utilisation continue des régions secondaires.

Défis :
- synchronisation des données ;
- gestion des écritures concurrentes ;
- cohérence ;
- bascule du trafic ;
- prévention des doubles traitements ;
- complexité du diagnostic ;
- coûts permanents.

### 9.4 Architecture active-passive

Une région principale sert le trafic et une région secondaire est prête à prendre le relais.

Avantages possibles :
- complexité opérationnelle réduite dans certains scénarios ;
- possibilité de limiter la capacité permanente de secours.

Défis :
- délai de bascule ;
- capacité de la région secondaire ;
- synchronisation des données ;
- risque de configuration obsolète ;
- tests de reprise.

La région secondaire doit être réellement exploitable : identités, secrets, images, quotas, réseau, DNS, données et procédures doivent être prêts.

### 9.5 Concevoir le plan de reprise

Pour chaque service :
1. définir les scénarios de panne ;
2. définir le RPO et le RTO ;
3. identifier les dépendances ;
4. sélectionner les mécanismes de sauvegarde et de réplication ;
5. prévoir les identités et les accès de secours ;
6. documenter les procédures ;
7. tester la reprise ;
8. mesurer le résultat ;
9. corriger les écarts.

## 10. RPO, RTO et stratégies de reprise

### 10.1 Définitions

**RPO — Recovery Point Objective**

Quantité maximale de données que l'entreprise accepte de perdre, exprimée comme un intervalle de temps entre l'incident et le point de données récupérable.

**RTO — Recovery Time Objective**

Durée maximale visée pour rétablir le service après une interruption.

Ces objectifs doivent être définis avec les responsables métier. Ils ne doivent pas être choisis uniquement par l'équipe technique.

### 10.2 Comparaison des stratégies

| Stratégie | Principe | Compromis principal |
|---|---|---|
| Sauvegarde et restauration | Recréer le service à partir de copies | Reprise généralement plus longue |
| Environnement minimal de secours | Socle prêt, capacité limitée | Temps d'extension de capacité |
| Warm standby | Environnement secondaire déjà opérationnel en partie | Coût permanent et synchronisation |
| Active-passive | Second environnement prêt à prendre le relais | Bascule et cohérence des données |
| Active-active | Plusieurs régions servent le trafic | Complexité et coût plus élevés |

Ces stratégies sont des catégories d'architecture. Les capacités exactes dépendent des services choisis, de leur configuration et des exigences de l'application.

### 10.3 Plan de reprise documenté

Un plan exploitable comprend :
- les critères de déclaration d'incident majeur ;
- les responsables et les canaux de communication ;
- les prérequis techniques ;
- les étapes de bascule ;
- les contrôles de cohérence ;
- les tests de validation métier ;
- les critères de retour à la normale ;
- les conditions de retour vers la région principale ;
- les preuves et résultats des exercices.

La reprise ne se termine pas lorsque l'application répond à une requête. Il faut vérifier les données, les traitements différés, les intégrations et les processus métier.

## 11. SRE : ingénierie de fiabilité des services

### 11.1 Qu'est-ce que le SRE ?

Site Reliability Engineering (SRE) applique des pratiques d'ingénierie à l'exploitation des services. Il vise à rendre la fiabilité mesurable et à améliorer les systèmes par l'automatisation, l'observabilité, l'analyse des incidents et l'apprentissage continu.

### 11.2 SLI, SLO et SLA

- **SLI :** indicateur mesuré de la qualité d'un service.
- **SLO :** objectif interne de fiabilité fondé sur un ou plusieurs SLI.
- **SLA :** engagement contractuel ou formel associé à des conditions définies.

Exemple :

```text
SLI : proportion de requêtes réussies
              |
              v
SLO : objectif de succès sur une période donnée
              |
              v
SLA : engagement contractuel si applicable
```

Un SLO ne doit pas être confondu avec une promesse contractuelle. Il sert notamment à guider les décisions d'exploitation et de développement.

### 11.3 Définir un SLI pertinent

Pour une API, un SLI peut mesurer :
- le taux de requêtes réussies ;
- la latence sous un seuil défini ;
- la disponibilité d'une opération métier ;
- la fraîcheur des données ;
- la réussite d'un traitement asynchrone.

Un indicateur doit refléter l'expérience réelle des utilisateurs. La seule disponibilité d'une machine ou d'un conteneur ne garantit pas que l'application fonctionne correctement.

### 11.4 Exemple de SLO

Supposons qu'une API définisse un objectif de 99,9 % de requêtes valides et réussies sur une période de 30 jours.

L'objectif doit préciser :
- quelles requêtes sont incluses ;
- comment sont comptées les erreurs ;
- comment sont traités les appels internes ;
- quelle période est utilisée ;
- comment les données sont collectées ;
- quels cas sont exclus et pourquoi.

Pour une période de 30 jours de 43 200 minutes, un objectif de disponibilité de 99,9 % correspond à environ 43,2 minutes d'indisponibilité équivalente, si la mesure est réellement fondée sur le temps et si la définition est cohérente.

Pour un SLI fondé sur les requêtes, le budget d'erreur se calcule à partir du nombre de requêtes éligibles, et non simplement en minutes.

### 11.5 Budget d'erreur

Si le SLO exige 99,9 % de succès, la fraction d'erreur autorisée est de 0,1 % sur la période de mesure.

```text
Objectif de succès : 99,9 %
Fraction d'erreur :  0,1 %

Budget d'erreur
      |
      +-- erreurs consommées lentement
      |      -> continuer les changements avec vigilance
      |
      +-- erreurs consommées rapidement
             -> réduire le risque et stabiliser
```

Le budget d'erreur doit influencer les décisions de livraison. Lorsqu'il est consommé trop rapidement, l'équipe peut réduire les changements risqués, prioriser les corrections et améliorer les contrôles.

### 11.6 Réduire le toil

Le toil désigne le travail opérationnel répétitif, manuel, automatisable et généralement peu générateur de valeur durable.

Exemples :
- redémarrer manuellement le même service chaque semaine ;
- appliquer manuellement une configuration identique ;
- copier des données entre environnements ;
- examiner chaque jour des alertes sans action nouvelle.

Le processus d'amélioration consiste à :
1. mesurer le temps consommé ;
2. identifier les tâches répétitives ;
3. automatiser avec des contrôles ;
4. vérifier le comportement en cas d'échec ;
5. mesurer le gain ;
6. maintenir l'automatisation.

L'automatisation ne doit pas transformer une procédure manuelle imparfaite en une panne automatique à grande échelle.

## 12. Gestion des incidents et postmortems

### 12.1 Cycle d'incident

```text
Détection
   |
   v
Qualification
   |
   v
Réduction de l'impact
   |
   v
Diagnostic
   |
   v
Restauration du service
   |
   v
Vérification
   |
   v
Postmortem
   |
   v
Actions correctives
```

La priorité initiale est de limiter l'impact utilisateur et de restaurer le service de manière sûre. Le diagnostic approfondi peut continuer après le rétablissement.

### 12.2 Contenu d'un postmortem

Un postmortem utile contient :
- le résumé de l'incident ;
- l'impact mesuré ;
- la chronologie ;
- le mécanisme de détection ;
- les causes techniques et organisationnelles ;
- les facteurs qui ont aggravé l'incident ;
- les actions correctives ;
- les propriétaires des actions ;
- les échéances ;
- les preuves de résolution.

Une culture sans recherche de coupable encourage la remontée des erreurs et l'amélioration du système. Elle n'empêche pas de traiter les comportements dangereux : elle privilégie l'analyse des mécanismes et des contrôles plutôt que la simple attribution de faute.

### 12.3 Exemple de diagnostic

**Symptôme :** hausse soudaine du taux d'erreur d'une API.

Hypothèses à tester :
1. changement de code ou de configuration ;
2. dépendance externe indisponible ;
3. épuisement des connexions à la base ;
4. quota atteint ;
5. hausse de trafic ;
6. problème DNS ou réseau ;
7. erreur d'identité ou de permissions ;
8. saturation des ressources.

Pour chaque hypothèse, chercher un signal discriminant. Par exemple, une hausse de latence de la base accompagnée d'un épuisement du pool de connexions n'indique pas la même cause qu'un refus IAM.

## 13. Sécurité de la chaîne CI/CD

### 13.1 Chaîne de confiance

```text
Code source
    |
    v
Revue et contrôles
    |
    v
Construction isolée
    |
    v
Analyse des dépendances
    |
    v
Image produite
    |
    v
Provenance et attestations
    |
    v
Politique de déploiement
    |
    v
Environnement cible
```

L'objectif est de savoir quel code a produit quel artefact, dans quel environnement, avec quelles dépendances et selon quelles validations.

### 13.2 Contrôles essentiels

- protéger les branches importantes ;
- imposer une revue pour les changements sensibles ;
- isoler les environnements de construction ;
- limiter les identités du pipeline ;
- contrôler les dépendances ;
- analyser les images ;
- utiliser des versions immuables d'artefacts ;
- conserver les traces de construction ;
- contrôler les changements Terraform ;
- exiger des validations adaptées au risque ;
- séparer les permissions de construction et de production.

### 13.3 Provenance et artefacts

Une provenance documente les informations sur la manière dont un artefact a été produit. Une attestation peut servir à prouver qu'un artefact respecte certaines exigences, si elle est générée, protégée et vérifiée correctement.

Une politique de déploiement doit vérifier les preuves attendues, et pas simplement faire confiance à un champ déclaré par le pipeline lui-même.

### 13.4 Sécuriser Terraform

Pour l'Infrastructure as Code :
1. versionner les configurations ;
2. utiliser des modules maîtrisés ;
3. verrouiller les versions des fournisseurs ;
4. vérifier les changements ;
5. analyser les configurations ;
6. protéger l'état ;
7. limiter l'identité de déploiement ;
8. empêcher les modifications non autorisées ;
9. documenter les exceptions ;
10. contrôler la dérive.

Le fait qu'une configuration soit déclarative ne la rend pas sûre. Une erreur Terraform peut créer une exposition réseau, supprimer des données ou attribuer un rôle excessif.

## 14. Automatisation et modèles de plateforme

### 14.1 Infrastructure comme produit

Une équipe plateforme peut proposer des modèles validés pour :
- créer un projet ;
- configurer les journaux ;
- activer les API approuvées ;
- créer des réseaux ;
- déployer un service ;
- appliquer les rôles ;
- créer des budgets ;
- configurer les alertes.

```text
Demande d'une équipe
        |
        v
Catalogue de modèles approuvés
        |
        v
Validation automatique
        |
        v
Provisionnement
        |
        v
Contrôles de conformité
        |
        v
Service prêt à être utilisé
```

Un catalogue réduit la duplication et favorise les bonnes pratiques. Il ne doit pas devenir une boîte noire : les équipes doivent comprendre les ressources créées, les limites du modèle et les procédures de dépannage.

### 14.2 Modules Terraform

Un module devrait avoir :
- une responsabilité clairement définie ;
- des entrées validées ;
- des sorties documentées ;
- des versions contrôlées ;
- des tests ;
- des exemples ;
- des limites de support ;
- une politique de mise à jour.

Évitez les modules qui exposent des dizaines de paramètres sans conventions cohérentes. Un module plateforme doit proposer des choix sûrs par défaut tout en permettant les besoins justifiés.

### 14.3 Promotion entre environnements

Une architecture fiable promeut le même artefact validé entre les environnements, lorsque le modèle de livraison le permet, plutôt que de reconstruire un artefact différent à chaque étape.

```text
Code validé
     |
     v
Artefact versionné
     |
     v
Préproduction
     |
     v
Tests et approbation
     |
     v
Production avec le même artefact
```

La configuration d'environnement peut varier, mais elle doit être contrôlée, séparée des secrets et versionnée selon les besoins.

## 15. Observabilité avancée

### 15.1 Corrélation des signaux

Pour diagnostiquer un incident distribué, les équipes doivent pouvoir relier les logs, les métriques et les traces.

```text
Requête utilisateur
       |
       v
Passerelle
       |
       v
Service A
       |
       v
Service B
       |
       v
Base de données

Trace : durée et chemin de la requête
Logs : événements détaillés
Métriques : débit, latence, erreurs et saturation
```

La corrélation doit utiliser des identifiants de requête ou de trace lorsqu'ils sont disponibles et correctement propagés.

### 15.2 Métriques de service

Les quatre grands signaux souvent utilisés sont :
- latence ;
- trafic ;
- erreurs ;
- saturation.

Ils ne suffisent pas à eux seuls. Un système métier peut aussi nécessiter des mesures de fraîcheur des données, de retard de traitement, de réussite des transactions ou de cohérence.

### 15.3 Alertes fondées sur l'impact

Une alerte sur un CPU élevé peut être utile, mais elle ne signifie pas automatiquement que l'utilisateur subit un problème. À l'inverse, un service peut produire un taux d'erreur élevé alors que le CPU reste faible.

Privilégiez des alertes qui combinent :
- un symptôme pertinent ;
- une durée suffisante pour éviter le bruit ;
- un seuil adapté au SLO ;
- une procédure de réponse claire ;
- une gravité liée à l'impact.

### 15.4 Conservation et accès aux logs

La stratégie de journalisation doit préciser :
- les types de logs collectés ;
- les projets de destination ;
- la durée de conservation ;
- les droits de lecture ;
- les droits de suppression ;
- les exigences d'audit ;
- le coût de collecte et de stockage ;
- les règles de traitement des données sensibles.

La journalisation peut elle-même devenir une source de risque si des secrets ou des données personnelles sont enregistrés sans nécessité.

## 16. FinOps avancé

### 16.1 Principes

FinOps associe les équipes techniques, financières et métier pour rendre les dépenses cloud visibles, attribuables et optimisables.

```text
Ingénierie
   |
   +-- Performance et architecture
   |
Finance
   |
   +-- Budgets et prévisions
   |
Métier
   |
   +-- Valeur et priorités
   |
   v
Décisions partagées sur le coût et la valeur
```

L'objectif n'est pas de minimiser chaque facture indépendamment. Il s'agit de maximiser la valeur fournie en respectant les exigences de sécurité, de fiabilité et de performance.

### 16.2 Allocation des coûts

Pour attribuer les dépenses :
- séparer les projets par environnement lorsque cela convient ;
- appliquer des labels cohérents aux ressources compatibles ;
- identifier les propriétaires ;
- distinguer coûts partagés et coûts directement attribuables ;
- suivre les transferts réseau ;
- contrôler les ressources inutilisées ;
- établir des rapports par équipe ou service.

Les labels n'offrent pas automatiquement une allocation parfaite. Certaines dépenses sont partagées ou ne sont pas attribuables directement à une ressource individuelle.

### 16.3 Budgets et alertes

Un budget permet de suivre la dépense et d'envoyer des notifications à certains seuils. Il ne constitue pas, à lui seul, un plafond qui bloque toutes les dépenses.

Pour réduire le risque de dépassement :
- configurer des alertes adaptées ;
- analyser les tendances ;
- surveiller les ressources à forte variabilité ;
- définir une procédure de réponse ;
- examiner les quotas et les limites ;
- automatiser la suppression des ressources temporaires lorsque cela est sûr.

### 16.4 Coût total d'une architecture

Le coût d'un service peut comprendre :
- le calcul ;
- le stockage ;
- les opérations de stockage ;
- les transferts de données ;
- la connectivité ;
- les bases de données ;
- la journalisation et la supervision ;
- les sauvegardes ;
- les services de sécurité ;
- les ressources de secours ;
- le temps d'exploitation.

Une architecture active-active peut coûter davantage qu'une architecture active-passive, mais réduire le risque d'interruption. Le choix doit tenir compte de la valeur métier de la disponibilité.

### 16.5 Exemple d'analyse de coût

Supposons qu'une application utilise :
- des instances de calcul ;
- une base relationnelle ;
- un stockage d'objets ;
- des journaux ;
- une région secondaire.

La méthode correcte consiste à :
1. mesurer le coût par composant ;
2. identifier les coûts fixes et variables ;
3. analyser le trafic et la capacité ;
4. vérifier les transferts interrégionaux ;
5. examiner la capacité réellement utilisée ;
6. estimer le coût des scénarios de reprise ;
7. proposer des changements ;
8. mesurer les économies réelles ;
9. vérifier qu'aucun SLO ou contrôle de sécurité n'est dégradé.

## 17. Performance et capacité

### 17.1 Approche de dimensionnement

Le dimensionnement doit partir des exigences :
- nombre de requêtes ;
- concurrence ;
- latence cible ;
- taille des données ;
- croissance attendue ;
- profils de charge ;
- dépendances externes ;
- tolérance aux pannes.

Ne choisissez pas une taille de machine ou un nombre de réplicas uniquement parce qu'une configuration fonctionne pendant un test manuel.

### 17.2 Tests de charge

Un plan de test doit définir :
- le scénario utilisateur ;
- les données de test ;
- le profil de montée en charge ;
- la durée ;
- les métriques collectées ;
- les seuils d'arrêt ;
- les limites des systèmes tiers ;
- les règles empêchant de perturber la production.

```text
Charge initiale
      |
      v
Montée progressive
      |
      v
Mesure de la latence et des erreurs
      |
      v
Identification du goulot d'étranglement
      |
      v
Correction
      |
      v
Nouveau test comparatif
```

### 17.3 Goulots d'étranglement

Les causes courantes incluent :
- un pool de connexions insuffisant ;
- des requêtes SQL coûteuses ;
- une dépendance lente ;
- un verrouillage ;
- une limitation de quota ;
- une mauvaise configuration de concurrence ;
- un manque de mémoire ;
- des transferts de données excessifs.

Augmenter les ressources peut masquer temporairement un problème sans résoudre sa cause.

## 18. Conformité et souveraineté des données

Une architecture d'entreprise doit intégrer les contraintes légales, contractuelles et internes dès la conception.

À documenter :
- les catégories de données ;
- les régions de stockage et de traitement ;
- les transferts entre régions ;
- les accès des opérateurs ;
- les exigences de conservation ;
- les mécanismes de suppression ;
- les journaux d'audit ;
- les sous-traitants et dépendances ;
- les procédures de récupération ;
- les preuves nécessaires aux audits.

Le choix d'une région ne suffit pas, à lui seul, à démontrer la conformité. Il faut examiner le comportement réel du service, les flux de données, les services dépendants et les exigences juridiques applicables.

## 19. Gestion des changements et du risque

### 19.1 Niveaux de changement

On peut distinguer :
- changements standard à faible risque et déjà approuvés ;
- changements planifiés nécessitant une revue ;
- changements d'urgence visant à réduire un impact immédiat.

Les règles doivent être adaptées au risque. Un changement de documentation ne nécessite pas les mêmes contrôles qu'une modification de politique IAM à l'échelle de l'organisation.

### 19.2 Procédure de changement

```text
Demande
  |
  v
Analyse de l'impact
  |
  v
Revue et approbation adaptées
  |
  v
Plan de mise en œuvre
  |
  v
Validation et déploiement
  |
  v
Contrôles après changement
  |
  +-- Réussi -> clôture
  |
  +-- Échec -> retour arrière ou mitigation
```

Un changement important doit disposer d'un plan de retour arrière, de critères de succès et d'une procédure d'escalade.

## 20. Travaux pratiques experts

### TP 1 — Concevoir une landing zone

**Objectif :** produire une architecture de gouvernance pour une organisation fictive.

Livrables :
1. diagramme de la hiérarchie organisationnelle ;
2. liste des projets et leurs propriétaires ;
3. modèle de séparation entre production et non-production ;
4. stratégie IAM ;
5. stratégie réseau ;
6. modèle de journalisation ;
7. conventions de nommage et de labels ;
8. stratégie de facturation ;
9. contrôles préventifs et détectifs ;
10. procédure d'exception.

**Validation :** chaque projet doit avoir un objectif, un responsable, un modèle d'accès et une procédure de cycle de vie.

### TP 2 — Auditer les permissions IAM

**Objectif :** identifier les accès excessifs.

Procédure :
1. inventorier les rôles de l'organisation, des dossiers et des projets ;
2. identifier les comptes de service ;
3. examiner les rôles primitifs trop larges ;
4. repérer les clés persistantes ;
5. analyser les identités inactives ;
6. identifier les accès hérités ;
7. proposer des rôles plus précis ;
8. tester les changements dans un environnement pilote ;
9. vérifier les opérations nécessaires après réduction des permissions.

**Livrable :** tableau des risques, des permissions concernées, des corrections proposées et des preuves de validation.

Ne supprimez pas un rôle uniquement parce qu'il semble large. Vérifiez d'abord les dépendances et les besoins opérationnels afin d'éviter une panne d'administration ou de production.

### TP 3 — Concevoir un plan de reprise

**Scénario :** une application critique utilise une base de données et un service applicatif dans une région principale.

Définir :
- les scénarios de perte de zone et de région ;
- le RPO et le RTO ;
- les mécanismes de sauvegarde et de réplication ;
- le modèle de région secondaire ;
- la procédure de bascule ;
- les contrôles de cohérence ;
- la validation métier ;
- les conditions de retour ;
- les coûts estimés.

**Livrable :** diagramme, runbook de reprise et compte rendu d'un test simulé.

### TP 4 — Concevoir des SLO et alertes

Pour une API :
1. définir la population de requêtes mesurée ;
2. définir un SLI de réussite ;
3. définir un SLI de latence ;
4. choisir des SLO ;
5. calculer le budget d'erreur ;
6. concevoir une alerte fondée sur l'impact ;
7. rédiger la procédure de réponse ;
8. définir le tableau de bord ;
9. décrire le postmortem après dépassement.

**Validation :** les indicateurs doivent être mesurables, reproductibles et reliés à des décisions d'exploitation.

### TP 5 — Sécuriser une chaîne CI/CD

Concevoir une chaîne dans laquelle :
- le code est versionné ;
- les changements sensibles sont revus ;
- les tests s'exécutent automatiquement ;
- les dépendances sont contrôlées ;
- l'image est publiée dans un registre ;
- l'identité du pipeline est limitée ;
- les artefacts sont traçables ;
- la production nécessite les validations appropriées ;
- les journaux permettent l'audit ;
- le retour arrière est testé.

**Livrable :** diagramme de la chaîne, matrice des identités et permissions, stratégie d'artefacts et procédure d'incident.

## 21. Exercices corrigés

### Exercice 1 — Landing zone

**Question :** pourquoi une landing zone ne doit-elle pas être réduite à un VPC central ?

**Correction :** parce qu'elle doit aussi fournir la gouvernance des projets, les identités, les stratégies de sécurité, la journalisation, les processus de création, la gestion des coûts et le cycle de vie des ressources. Le réseau est une composante du socle, pas le socle entier.

### Exercice 2 — IAM

**Question :** un pipeline utilise une clé JSON de compte de service stockée comme secret. Quel est le principal risque et quelle amélioration envisager ?

**Correction :** la clé est un secret persistant susceptible d'être volé ou réutilisé. Une fédération d'identité compatible avec le fournisseur CI peut réduire cette dépendance. Il faut aussi limiter les permissions, restreindre les identités autorisées et contrôler les changements du pipeline.

### Exercice 3 — Haute disponibilité

**Question :** une application possède plusieurs instances dans une seule région. Est-elle protégée contre la perte de cette région ?

**Correction :** pas nécessairement. La redondance d'instances peut couvrir certaines pannes de composants ou de zones selon la configuration, mais la perte régionale nécessite une stratégie distincte, avec les données, les dépendances, le réseau et les procédures de reprise adaptés.

### Exercice 4 — SRE

**Question :** pourquoi un taux de CPU faible ne prouve-t-il pas que le service fonctionne correctement ?

**Correction :** le service peut échouer à cause d'une dépendance indisponible, de permissions incorrectes, d'erreurs applicatives ou d'un problème DNS. Les indicateurs doivent couvrir le résultat perçu par l'utilisateur, pas uniquement les ressources de calcul.

### Exercice 5 — Budget d'erreur

**Question :** que devrait faire une équipe lorsque son budget d'erreur se consomme très rapidement ?

**Correction :** analyser l'impact, stabiliser le service et réduire les changements risqués selon la politique SRE. Il faut identifier la cause, corriger les problèmes et améliorer les contrôles avant de reprendre un rythme normal de livraison.

### Exercice 6 — VPC Service Controls

**Question :** VPC Service Controls remplace-t-il IAM et les pare-feu ?

**Correction :** non. Il répond à certains risques liés aux accès et à l'exfiltration pour des services pris en charge. IAM, les contrôles réseau, la sécurité applicative et la protection des données restent nécessaires.

### Exercice 7 — FinOps

**Question :** comment comparer une architecture active-active à une architecture active-passive ?

**Correction :** comparer le coût total, la disponibilité visée, les objectifs RPO/RTO, la cohérence des données, la complexité d'exploitation et le coût d'une interruption. L'architecture la moins chère n'est pas nécessairement la plus rentable si elle entraîne des pertes métier plus importantes.

### Exercice 8 — Gouvernance

**Question :** pourquoi tester une stratégie d'organisation sur un périmètre pilote ?

**Correction :** pour détecter les incompatibilités avec les ressources et les déploiements existants, identifier les exceptions nécessaires et réduire le risque de blocage généralisé.

## 22. Projet final corrigé — Plateforme cloud d'entreprise résiliente

### 22.1 Contexte

Une entreprise souhaite héberger une application métier critique sur Google Cloud. Elle possède des équipes de développement et d'exploitation, des données persistantes, des exigences de sécurité, un réseau d'entreprise et un objectif de reprise après sinistre.

Le projet doit fournir une architecture cohérente et des procédures vérifiables.

### 22.2 Exigences à définir

Avant toute implémentation, établir :
- les utilisateurs et les rôles métier ;
- les exigences de disponibilité ;
- les objectifs de latence ;
- le RPO et le RTO ;
- les catégories de données ;
- les régions autorisées ;
- les flux entre réseau local et cloud ;
- les identités humaines et applicatives ;
- les contraintes de conformité ;
- les limites de coût ;
- les responsabilités d'exploitation.

Aucune valeur de disponibilité, de performance ou de coût ne doit être inventée comme si elle était déjà approuvée par le métier.

### 22.3 Architecture de référence

```text
                         Utilisateurs
                              |
                       Point d'entrée
                              |
                  Contrôles d'accès et filtrage
                              |
                    Routage vers l'application
                              |
              +---------------+---------------+
              |                               |
         Région principale               Région secondaire
              |                               |
        Services applicatifs             Services de secours
              |                               |
        Données principales <----------> Données répliquées
              |
        Observabilité centrale
              |
      Logs, métriques, alertes

Organisation GCP
|
+-- Platform
|   +-- Réseau
|   +-- Sécurité
|   +-- Journalisation
|   +-- Automatisation
|
+-- Non-production
|   +-- Développement
|   +-- Préproduction
|
+-- Production
    +-- Application
    +-- Données
```

Les liens de réplication et de bascule sont conceptuels. Le mécanisme réel dépend du service de données et du modèle de cohérence retenu.

### 22.4 Étape 1 — Construire le socle de gouvernance

Définir :
- l'organisation et les dossiers ;
- les projets de plateforme ;
- les projets d'applications ;
- les conventions de nommage ;
- les labels ;
- les propriétaires ;
- les stratégies d'organisation ;
- les mécanismes d'exception ;
- les budgets et les alertes.

**Résultat attendu :** chaque ressource appartient à un périmètre gouverné et possède un propriétaire identifiable.

### 22.5 Étape 2 — Concevoir les identités

Créer une matrice indiquant :
- le principal ;
- le rôle ;
- la ressource cible ;
- la justification ;
- la durée ou la périodicité de revue ;
- les risques ;
- le mécanisme de révocation.

Séparer les identités des administrateurs, des pipelines, des workloads et des opérations de secours.

**Résultat attendu :** aucun composant ne possède de privilèges généraux sans justification.

### 22.6 Étape 3 — Concevoir le réseau

Documenter :
- les plages CIDR ;
- les sous-réseaux ;
- les chemins de trafic ;
- les règles de pare-feu ;
- la connectivité hybride ;
- les mécanismes DNS ;
- les flux interrégionaux ;
- les chemins de sortie ;
- les besoins de filtrage centralisé ;
- les tests de bascule.

**Résultat attendu :** chaque flux autorisé a une raison métier, une source, une destination et une méthode de validation.

### 22.7 Étape 4 — Déployer les applications

Choisir le service de calcul selon les besoins :
- Cloud Run pour les workloads compatibles avec son modèle ;
- GKE lorsque les besoins Kubernetes justifient la complexité supplémentaire ;
- Compute Engine lorsque le contrôle direct de la machine est nécessaire.

Définir les identités, les ressources, les secrets, les limites de mise à l'échelle et les contrôles de déploiement.

**Résultat attendu :** le service fonctionne dans des conditions représentatives et les procédures d'exploitation sont documentées.

### 22.8 Étape 5 — Protéger les données

Pour chaque stockage ou base de données :
1. classifier les données ;
2. définir les accès ;
3. définir la localisation ;
4. sélectionner les mécanismes de chiffrement ;
5. définir les sauvegardes ;
6. définir la réplication si nécessaire ;
7. définir la rétention ;
8. tester la restauration ;
9. vérifier les journaux d'accès ;
10. documenter les conditions de suppression.

**Résultat attendu :** les données sont protégées contre les accès non autorisés et récupérables selon les objectifs convenus.

### 22.9 Étape 6 — Industrialiser le déploiement

Construire une chaîne de livraison :
- validation du code ;
- tests ;
- analyse des dépendances ;
- construction d'artefacts ;
- traçabilité ;
- déploiement en préproduction ;
- validation ;
- approbation ;
- déploiement en production ;
- vérification post-déploiement.

Utiliser des identités de pipeline limitées et un mécanisme de fédération d'identité lorsqu'il est adapté.

**Résultat attendu :** chaque version peut être reliée au code, aux tests et à l'artefact déployé.

### 22.10 Étape 7 — Définir la fiabilité

Établir :
- les SLI ;
- les SLO ;
- les budgets d'erreur ;
- les alertes ;
- les tableaux de bord ;
- les runbooks ;
- les responsabilités d'astreinte ;
- les procédures d'incident ;
- les postmortems ;
- les actions d'amélioration.

**Résultat attendu :** les décisions de livraison et d'exploitation reposent sur des mesures observables.

### 22.11 Étape 8 — Tester la reprise après sinistre

Réaliser un exercice contrôlé :
1. vérifier les sauvegardes ;
2. préparer l'environnement secondaire ;
3. simuler un scénario défini ;
4. exécuter le runbook ;
5. vérifier les données ;
6. tester les flux applicatifs ;
7. mesurer le temps de reprise ;
8. mesurer la perte éventuelle de données ;
9. consigner les écarts ;
10. améliorer le plan.

**Résultat attendu :** le RPO et le RTO sont évalués par des résultats observés, pas uniquement par une estimation théorique.

### 22.12 Étape 9 — Valider les coûts

Produire :
- une estimation par composant ;
- une ventilation par projet ;
- une estimation des transferts ;
- une estimation des sauvegardes ;
- le coût du secours ;
- une stratégie de budgets ;
- un tableau des ressources inutilisées ;
- des mesures d'optimisation.

**Résultat attendu :** l'organisation comprend les principaux postes de dépense et peut prendre des décisions sans dégrader silencieusement les objectifs de fiabilité.

### 22.13 Dossier final à remettre

Le dossier d'architecture doit contenir :
1. diagramme global ;
2. décisions d'architecture et justifications ;
3. matrice IAM ;
4. plan réseau ;
5. modèle de gouvernance ;
6. stratégie de protection des données ;
7. pipeline CI/CD ;
8. stratégie d'observabilité ;
9. SLI, SLO et budgets d'erreur ;
10. plan de reprise ;
11. résultats des tests ;
12. estimation de coûts ;
13. procédures d'incident ;
14. risques résiduels ;
15. feuille de route d'amélioration.

### 22.14 Critères d'évaluation

| Domaine | Critère de réussite |
|---|---|
| Architecture | Les choix répondent aux exigences métier |
| Gouvernance | Les projets et ressources sont contrôlés |
| IAM | Les permissions sont justifiées et limitées |
| Réseau | Les flux sont documentés et testés |
| Données | Accès, rétention et restauration sont définis |
| CI/CD | Les artefacts et changements sont traçables |
| SRE | Les indicateurs et alertes sont exploitables |
| Reprise | Le plan est testé et mesuré |
| FinOps | Les coûts sont attribuables et suivis |
| Exploitation | Les responsabilités et procédures sont claires |

## 23. Checklist de niveau expert

- [ ] Je sais concevoir une landing zone multi-projets.
- [ ] Je sais séparer les responsabilités de plateforme, de sécurité et d'application.
- [ ] Je comprends les stratégies d'organisation et leur héritage.
- [ ] Je sais concevoir un modèle IAM à grande échelle.
- [ ] Je comprends la fédération d'identité et ses risques.
- [ ] Je sais distinguer les rôles IAM des contraintes de gouvernance.
- [ ] Je sais concevoir la protection des données et la gestion des clés.
- [ ] Je comprends les réseaux hybrides et les architectures hub-and-spoke.
- [ ] Je sais comparer des stratégies multi-région.
- [ ] Je sais définir un RPO, un RTO et un plan de reprise.
- [ ] Je sais définir des SLI, des SLO et un budget d'erreur.
- [ ] Je sais analyser un incident et rédiger un postmortem.
- [ ] Je sais sécuriser une chaîne CI/CD.
- [ ] Je sais industrialiser Terraform avec des contrôles.
- [ ] Je sais concevoir une stratégie FinOps.
- [ ] Je sais présenter les compromis, risques et coûts d'une architecture.
- [ ] Je sais démontrer la résilience par des tests mesurés.

## 24. Glossaire expert

- **Active-active :** architecture dans laquelle plusieurs environnements servent simultanément le trafic.
- **Active-passive :** architecture dans laquelle un environnement principal sert le trafic et un environnement secondaire est préparé pour la reprise.
- **FinOps :** discipline de gestion collaborative de la valeur et des dépenses cloud.
- **Landing zone :** socle gouverné destiné à accueillir les charges de travail.
- **Postmortem :** analyse structurée d'un incident et des actions d'amélioration.
- **RPO :** objectif de point de reprise.
- **RTO :** objectif de temps de reprise.
- **SLA :** engagement formel de niveau de service.
- **SLI :** indicateur mesuré de niveau de service.
- **SLO :** objectif de niveau de service.
- **SRE :** approche d'ingénierie de la fiabilité des services.
- **Toil :** travail opérationnel répétitif et automatisable.
- **Workload Identity Federation :** mécanisme de fédération permettant à des identités externes compatibles d'obtenir un accès à Google Cloud sans dépendre nécessairement de clés persistantes.

## 25. Documentation officielle

- Documentation générale Google Cloud : https://cloud.google.com/docs
- Architecture Framework : https://cloud.google.com/architecture/framework
- Architecture Center : https://cloud.google.com/architecture
- Resource Manager : https://cloud.google.com/resource-manager/docs
- Organization Policy : https://cloud.google.com/resource-manager/docs/organization-policy/overview
- IAM : https://cloud.google.com/iam/docs
- Workload Identity Federation : https://cloud.google.com/iam/docs/workload-identity-federation
- Cloud KMS : https://cloud.google.com/kms/docs
- VPC Service Controls : https://cloud.google.com/vpc-service-controls/docs
- VPC : https://cloud.google.com/vpc/docs
- Network Connectivity : https://cloud.google.com/network-connectivity/docs
- Cloud Armor : https://cloud.google.com/armor/docs
- Google Kubernetes Engine : https://cloud.google.com/kubernetes-engine/docs
- Cloud Run : https://cloud.google.com/run/docs
- Cloud Logging : https://cloud.google.com/logging/docs
- Cloud Monitoring : https://cloud.google.com/monitoring/docs
- SRE de Google : https://sre.google/
- Google Cloud FinOps : https://cloud.google.com/cost-management
- Terraform pour Google Cloud : https://cloud.google.com/docs/terraform

## 26. Conclusion

Le niveau expert repose sur la capacité à relier les services techniques aux objectifs métier et aux contraintes opérationnelles.

Une architecture de qualité n'est pas celle qui utilise le plus de services ou le plus de mécanismes de sécurité. C'est celle dont les choix sont justifiés, dont les risques sont compris, dont les contrôles sont vérifiables et dont les modes de défaillance ont été anticipés.

La maîtrise de GCP à l'échelle entreprise exige donc trois capacités complémentaires :

1. **Concevoir** des architectures adaptées aux exigences de sécurité, de performance, de disponibilité et de coût.
2. **Industrialiser** les déploiements, les contrôles et les opérations au moyen de mécanismes reproductibles.
3. **Démontrer** la fiabilité par des mesures, des audits, des exercices de reprise et des améliorations continues.

Le cours est terminé lorsque l'apprenant peut non seulement expliquer une architecture, mais aussi justifier ses compromis, la déployer de façon contrôlée, la diagnostiquer en cas d'incident et démontrer sa capacité à récupérer.
