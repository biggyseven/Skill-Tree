# AWS expert : architecture à grande échelle, sécurité et fiabilité

## Présentation du cours

Ce cours constitue le troisième niveau du parcours AWS. Il suppose la maîtrise des bases du cloud, du réseau VPC, de l'identité IAM, des services de calcul et de stockage, ainsi que des premières pratiques Terraform et CI/CD.

L'objectif est de passer de la construction d'une infrastructure fonctionnelle à la conception d'une plateforme cloud gouvernée, sécurisée, résiliente, observable et économiquement maîtrisée.

Les compétences des autres parcours techniques sont intégrées :
- Git pour la revue et la traçabilité des changements ;
- CI/CD pour les déploiements contrôlés ;
- Terraform pour la gestion de l'infrastructure à grande échelle ;
- Ansible pour les configurations système qui le nécessitent ;
- Docker et Kubernetes pour les charges conteneurisées ;
- SRE pour les SLI, SLO, budgets d'erreur et incidents.

### Objectifs pédagogiques

À la fin du cours, il faudra être capable de :

- Concevoir une organisation AWS multi-comptes.
- Définir des garde-fous de gouvernance.
- Concevoir une stratégie d'identité fédérée et de privilèges minimaux.
- Centraliser les journaux, la détection et l'audit.
- Concevoir des architectures résilientes multi-AZ et multi-régions.
- Choisir une stratégie de reprise après sinistre.
- Structurer Terraform pour plusieurs comptes et environnements.
- Sécuriser les pipelines CI/CD et les chaînes d'approvisionnement.
- Déployer progressivement les applications.
- Mesurer la fiabilité à l'aide de SLI et SLO.
- Organiser la réponse aux incidents.
- Gouverner les coûts et la capacité.
- Évaluer les compromis d'architecture avec AWS Well-Architected.

## 1. Repenser l'infrastructure comme une plateforme

Une infrastructure experte ne se résume pas à une collection de ressources AWS.

Elle doit fournir des capacités communes aux équipes :
- identité et accès ;
- réseau ;
- journalisation ;
- sécurité ;
- déploiement ;
- sauvegarde ;
- supervision ;
- gouvernance ;
- facturation ;
- réponse aux incidents.

L'objectif est de permettre aux équipes de livrer des applications sans réinventer les contrôles fondamentaux à chaque projet.

### 1.1. Architecture de plateforme

```text
                         Organisation
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
         Identité         Gouvernance      Observabilité
              |               |               |
              +---------------+---------------+
                              |
                              v
                    Comptes AWS gouvernés
                              |
             +----------------+----------------+
             |                |                |
             v                v                v
         Développement     Préproduction    Production
             |                |                |
             +----------------+----------------+
                              |
                              v
                   Services applicatifs
```

Une plateforme efficace combine :
- des contrôles communs ;
- des modèles d'infrastructure ;
- des chemins de déploiement approuvés ;
- une autonomie encadrée pour les équipes.

## 2. AWS Organizations et stratégie multi-comptes

### 2.1. Pourquoi plusieurs comptes ?

Un compte AWS est une frontière importante d'isolation, de gestion des accès et de facturation.

Séparer les environnements réduit le rayon d'impact d'une erreur ou d'une compromission.

Les comptes peuvent isoler :
- la production ;
- le développement ;
- les journaux d'audit ;
- les outils de sécurité ;
- l'infrastructure réseau partagée ;
- les expérimentations ;
- les services communs.

### 2.2. Exemple d'organisation

```text
AWS Organization
|
+-- Management Account
|
+-- Security OU
|    +-- Audit Account
|    +-- Security Tooling Account
|
+-- Infrastructure OU
|    +-- Network Account
|    +-- Shared Services Account
|
+-- Workloads OU
|    +-- Development Account
|    +-- Staging Account
|    +-- Production Account
|
+-- Sandbox OU
     +-- Experiment Account
```

Cette hiérarchie est un exemple, pas une structure universelle.

Le compte de management doit être réservé aux tâches de gestion de l'organisation. Il ne doit pas héberger les applications ordinaires de production.

La structure doit correspondre aux frontières de confiance, aux exigences de conformité et aux responsabilités opérationnelles.

### 2.3. AWS Organizations

AWS Organizations permet d'organiser les comptes et de gérer certaines politiques à l'échelle de l'organisation.

Il fournit notamment :
- une hiérarchie d'unités organisationnelles ;
- des politiques de contrôle des services ;
- une administration centralisée ;
- des possibilités de facturation consolidée ;
- l'intégration avec des services de gouvernance.

Les permissions IAM locales restent importantes. Une politique de contrôle des services ne donne pas elle-même une permission à une identité : elle définit notamment les actions maximales autorisables dans le périmètre concerné.

### 2.4. Service Control Policies

Les SCP définissent des garde-fous applicables aux comptes ou unités organisationnelles concernés.

Exemples de cas d'usage :
- interdire certains services non approuvés ;
- limiter certaines actions à des régions autorisées ;
- empêcher certaines modifications sensibles ;
- limiter les actions de certaines catégories de comptes.

Les SCP doivent être testées soigneusement. Une restriction mal conçue peut bloquer les opérations d'exploitation, de sécurité ou de récupération.

Une SCP ne remplace pas les politiques IAM. L'autorisation effective résulte de l'ensemble des politiques et conditions applicables.

### 2.5. AWS Control Tower

AWS Control Tower aide à mettre en place et gouverner un environnement multi-comptes fondé sur des contrôles et une zone d'accueil.

Il peut faciliter :
- l'organisation initiale ;
- la création de comptes ;
- l'application de garde-fous ;
- la cohérence des configurations ;
- la gouvernance centralisée.

Le choix entre une organisation construite manuellement et Control Tower dépend du contexte, des exigences et des capacités de l'équipe.

## 3. Identité fédérée et privilèges minimaux

### 3.1. Architecture d'identité

Dans une organisation, l'accès humain doit généralement s'appuyer sur une source d'identité centralisée.

```text
Utilisateur
    |
    v
Fournisseur d'identité
    |
    v
Authentification et MFA
    |
    v
AWS IAM Identity Center
    |
    v
Permission Set / Accès attribué
    |
    v
Compte AWS cible
```

Cette architecture réduit la nécessité de multiplier les identités locales et facilite la révocation des accès.

### 3.2. Séparer les rôles

Exemples de rôles :
- lecture seule ;
- développement ;
- déploiement ;
- administration réseau ;
- sécurité ;
- audit ;
- intervention d'urgence.

Les permissions doivent correspondre aux tâches réellement effectuées.

Une même personne peut avoir besoin de plusieurs niveaux d'accès, mais les privilèges élevés doivent être encadrés, temporaires lorsque possible et audités.

### 3.3. Accès privilégié

Un mécanisme d'accès privilégié doit prévoir :
- une justification ;
- une durée limitée ;
- une approbation si nécessaire ;
- une journalisation ;
- une procédure de révocation ;
- une procédure d'urgence ;
- des tests réguliers.

Les comptes d'urgence, souvent appelés break-glass, doivent être très fortement protégés et leur utilisation doit déclencher une vérification.

### 3.4. Identités des charges de travail

Une application doit obtenir des permissions sans stocker de secrets permanents.

Exemples :
- rôles d'instance EC2 ;
- rôles d'exécution Lambda ;
- rôles de tâche ECS ;
- mécanismes d'identité des pods EKS ;
- rôles assumés par des pipelines CI/CD.

Les rôles doivent être distincts lorsqu'ils ont des responsabilités différentes.

Une identité utilisée pour lire des objets S3 ne devrait pas obtenir par défaut des permissions d'administration du réseau ou des comptes.

## 4. Sécurité centralisée et détection

### 4.1. Journalisation

Une stratégie de journalisation doit couvrir les événements pertinents et protéger les journaux contre la modification non autorisée.

Services et capacités à connaître :
- AWS CloudTrail pour les événements d'activité AWS ;
- Amazon CloudWatch pour les métriques et journaux ;
- AWS Config pour l'historique de configuration et l'évaluation de règles ;
- Amazon GuardDuty pour la détection de menaces ;
- AWS Security Hub pour la centralisation de constats de sécurité selon les services et intégrations configurés ;
- Amazon S3 pour la conservation de journaux lorsque cela convient.

Les services, régions et fonctionnalités disponibles doivent être vérifiés selon l'environnement.

### 4.2. Architecture de sécurité

```text
Comptes applicatifs
      |
      +-- Événements CloudTrail
      +-- Constats de sécurité
      +-- Configuration des ressources
      +-- Journaux des applications
                 |
                 v
        Collecte et centralisation
                 |
       +---------+---------+
       |         |         |
       v         v         v
     Audit    Détection   Alertes
       |         |         |
       +---------+---------+
                 |
                 v
         Réponse aux incidents
```

La centralisation ne doit pas introduire un nouveau point de faiblesse. Les permissions, les accès aux journaux et la rétention doivent être protégés.

### 4.3. CloudTrail

CloudTrail aide à examiner les actions effectuées via les API AWS prises en charge.

Questions utiles :
- quelle identité a appelé l'API ?
- quelle action a été demandée ?
- quelle ressource était concernée ?
- quand l'action a-t-elle eu lieu ?
- depuis quel contexte disponible l'action a-t-elle été effectuée ?

Les événements de gestion, les événements de données et les autres catégories de journalisation ont des caractéristiques et des coûts différents. La couverture doit être conçue en fonction des risques.

### 4.4. AWS Config

AWS Config permet d'évaluer et d'enregistrer certains changements de configuration des ressources prises en charge.

Exemples de contrôles :
- ressources devant être chiffrées ;
- règles réseau trop permissives ;
- configuration de certaines ressources ;
- conformité à des règles définies.

Une règle de conformité ne garantit pas l'absence de vulnérabilité. Il faut combiner les contrôles préventifs, détectifs et correctifs.

### 4.5. GuardDuty et Security Hub

GuardDuty analyse des sources de données prises en charge pour détecter des activités potentiellement malveillantes.

Security Hub peut agréger des constats provenant de services de sécurité et d'intégrations compatibles.

Il faut définir :
- les comptes et régions couverts ;
- les responsabilités de triage ;
- les niveaux de gravité ;
- les procédures d'escalade ;
- les délais de traitement ;
- les règles de suppression des faux positifs ;
- les mesures correctives.

Une détection qui n'est pas traitée ne réduit pas suffisamment le risque.

## 5. Sécuriser les données

### 5.1. Classification

Avant de choisir les contrôles, classifier les données :
- publiques ;
- internes ;
- confidentielles ;
- sensibles ou réglementées.

La classification détermine notamment les exigences de chiffrement, d'accès, de conservation, de localisation et de suppression.

### 5.2. Chiffrement

AWS KMS permet de gérer des clés de chiffrement utilisées par les services et applications compatibles.

Il faut distinguer :
- chiffrement au repos ;
- chiffrement en transit ;
- gestion des clés ;
- contrôle d'accès aux clés ;
- rotation lorsque prise en charge et appropriée ;
- récupération et disponibilité des clés.

Le chiffrement ne suffit pas si une identité non autorisée peut lire les données en clair à travers une application ou une permission trop large.

### 5.3. Secrets

Les secrets peuvent inclure :
- mots de passe ;
- jetons ;
- clés d'API ;
- certificats privés ;
- identifiants de bases de données.

Utiliser un gestionnaire adapté, comme AWS Secrets Manager ou Systems Manager Parameter Store selon le besoin.

Bonnes pratiques :
1. Limiter les permissions de lecture.
2. Éviter les secrets dans le code.
3. Éviter les secrets dans les images de conteneurs.
4. Éviter les secrets dans les journaux.
5. Prévoir la rotation lorsque possible.
6. Contrôler les accès.
7. Prévoir le remplacement et la révocation.

## 6. Architecture réseau à grande échelle

### 6.1. Réseau centralisé ou distribué

Deux grandes approches peuvent être envisagées.

**Réseaux distribués**

Chaque compte gère une partie de son réseau, avec des règles d'interconnexion définies.

**Réseau centralisé**

Une équipe ou un compte réseau fournit les capacités partagées : connectivité, inspection, DNS, accès hybride ou services communs.

Une architecture centralisée peut faciliter la gouvernance, mais elle doit éviter de devenir un goulot d'étranglement ou un point de défaillance.

### 6.2. Transit Gateway

AWS Transit Gateway permet de connecter plusieurs VPC et réseaux compatibles au moyen d'une topologie de transit.

Exemple :

```text
                Transit Gateway
                /      |      \
               /       |       \
              v        v        v
          VPC-dev   VPC-prod   VPC-shared
                                  |
                                  v
                            Services communs
```

La conception doit inclure :
- les tables de routage ;
- les associations et propagations ;
- les CIDR ;
- les frontières de confiance ;
- les flux autorisés ;
- les besoins de segmentation ;
- les coûts de transit et de transfert.

L'interconnexion ne signifie pas que tous les réseaux doivent pouvoir communiquer librement.

### 6.3. AWS PrivateLink

AWS PrivateLink permet de proposer ou de consommer certains services de façon privée entre réseaux compatibles.

Il peut être utile lorsque :
- un service doit être consommé sans exposer un endpoint public ;
- l'interconnexion complète de réseaux n'est pas souhaitée ;
- l'accès doit être limité à un service spécifique.

Le choix entre Transit Gateway, PrivateLink, peering et autres solutions dépend du modèle de connectivité et des besoins d'isolation.

### 6.4. Connectivité hybride

Une organisation peut connecter ses réseaux sur site à AWS via des mécanismes compatibles, tels que :
- VPN site à site ;
- AWS Direct Connect ;
- architecture hybride combinant plusieurs chemins.

La conception doit couvrir :
- routage ;
- redondance ;
- chiffrement ;
- résolution DNS ;
- supervision ;
- capacité ;
- bascule ;
- procédures de test.

## 7. Architecture multi-AZ et multi-régions

### 7.1. Haute disponibilité et reprise après sinistre

Ces notions sont complémentaires, mais différentes.

**Haute disponibilité**

Réduire l'interruption lors de pannes locales ou de composants.

**Reprise après sinistre**

Restaurer le service après un incident majeur pouvant affecter une région ou un ensemble de dépendances.

### 7.2. Modèles de reprise

| Stratégie | Description | Compromis |
|---|---|---|
| Sauvegarde et restauration | Restaurer après l'incident | Coût réduit, RTO potentiellement élevé |
| Pilot light | Maintenir les composants essentiels | Restauration plus rapide, orchestration nécessaire |
| Warm standby | Maintenir une version réduite de l'environnement | Coût continu plus important |
| Multi-site actif | Plusieurs environnements actifs | Coût et complexité élevés |

Ces catégories décrivent des modèles généraux. La stratégie réelle dépend de la cohérence des données, des services utilisés et des objectifs métier.

### 7.3. RPO et RTO

Chaque système critique doit posséder des objectifs de reprise.

Exemple illustratif :

```text
Service A
  RPO cible : 5 minutes
  RTO cible : 30 minutes

Service B
  RPO cible : 24 heures
  RTO cible : 12 heures
```

Les valeurs doivent venir des exigences métier, pas d'une préférence technique arbitraire.

Il faut vérifier que l'architecture et les procédures permettent d'atteindre ces objectifs dans les conditions définies.

### 7.4. Dépendances cachées

Une application multi-région peut rester indisponible si elle dépend d'un service unique :
- identité ;
- DNS ;
- secret ;
- clé de chiffrement ;
- pipeline de déploiement ;
- base de données ;
- API externe ;
- quota.

La reprise doit couvrir la chaîne de dépendances complète.

### 7.5. Tester la reprise

Un plan de reprise doit être exercé.

Tests possibles :
- restauration d'une sauvegarde ;
- bascule contrôlée ;
- simulation de perte d'une AZ ;
- restauration dans une autre région ;
- validation des données ;
- vérification des accès ;
- test des procédures d'escalade.

Les exercices doivent être planifiés et réalisés dans un périmètre autorisé, avec une méthode de retour arrière.

## 8. Terraform à grande échelle

Le parcours IaC précédent couvre les modules, l'état et les environnements. Ici, l'objectif est d'appliquer ces principes à une organisation AWS.

### 8.1. Séparer les couches

Une architecture possible :

```text
terraform-platform/
|
+-- organization/
|    +-- accounts/
|    +-- organizational-units/
|    +-- guardrails/
|
+-- network/
|    +-- transit/
|    +-- shared-services/
|
+-- security/
|    +-- logging/
|    +-- detection/
|    +-- identity/
|
+-- workloads/
     +-- application-a/
     +-- application-b/
```

Cette structure est indicative. Les frontières doivent refléter les responsabilités, le cycle de vie et les permissions nécessaires.

### 8.2. Modules réutilisables

Un module doit :
- avoir une responsabilité claire ;
- exposer des entrées compréhensibles ;
- fournir des sorties utiles ;
- documenter les hypothèses ;
- limiter les options inutiles ;
- être testé ;
- être versionné ;
- évoluer avec une stratégie de compatibilité.

Un module qui tente de gérer tous les services AWS devient difficile à tester et à maintenir.

### 8.3. Backend et état

Pour les équipes, l'état doit être stocké dans un backend approprié et protégé.

La conception doit prendre en compte :
- chiffrement ;
- contrôle d'accès ;
- verrouillage de l'état lorsque disponible ;
- séparation des environnements ;
- récupération ;
- rétention et audit ;
- accès des pipelines ;
- prévention des modifications concurrentes.

Le backend S3 peut être utilisé pour l'état Terraform selon une configuration appropriée et les capacités de la version choisie. Il faut vérifier les mécanismes de verrouillage disponibles pour cette version et cette configuration.

### 8.4. Promotion entre environnements

Ne pas recopier manuellement des fichiers d'infrastructure différents sans contrôle.

Un flux possible :

```text
Modification Terraform
        |
        v
Revue de code
        |
        v
Lint / Validate / Tests
        |
        v
Plan en développement
        |
        v
Application contrôlée
        |
        v
Validation
        |
        v
Promotion vers recette
        |
        v
Approbation et application en production
```

Les différences d'environnement doivent être explicites et auditables.

### 8.5. Prévenir les dérives

Une dérive apparaît lorsque la réalité ne correspond plus à l'état déclaré.

Causes :
- modifications manuelles ;
- changements effectués par d'autres outils ;
- changements externes ;
- modules modifiés ;
- ressources importées ou non gérées ;
- changements de configuration.

Mesures :
- limiter les changements manuels ;
- inspecter les plans ;
- effectuer des contrôles réguliers ;
- documenter les exceptions ;
- importer les ressources existantes si approprié ;
- corriger les dérives de manière contrôlée.

Ne pas appliquer aveuglément un plan de correction sur un environnement critique.

## 9. Sécuriser la chaîne CI/CD

### 9.1. Chaîne d'approvisionnement logicielle

La sécurité concerne :
- le code source ;
- les dépendances ;
- les outils de build ;
- les images de conteneurs ;
- les artefacts ;
- les identités du pipeline ;
- les permissions de déploiement ;
- la provenance des livrables.

### 9.2. Principes

1. Protéger les branches et les environnements.
2. Réviser les changements.
3. Exécuter des tests.
4. Analyser les dépendances.
5. Analyser les images.
6. Produire des artefacts immuables lorsque possible.
7. Limiter les permissions du pipeline.
8. Utiliser des identifiants temporaires.
9. Séparer les environnements.
10. Conserver des traces d'exécution.
11. Protéger les secrets.
12. Prévoir le retour arrière.

### 9.3. OIDC et AWS

Un pipeline peut obtenir des identifiants temporaires via une fédération OIDC correctement configurée.

La politique de confiance doit restreindre précisément l'identité du workflow autorisé.

Il faut vérifier :
- le fournisseur OIDC ;
- l'audience ;
- le dépôt ;
- l'organisation ;
- la branche ou l'environnement ;
- les permissions du rôle ;
- les permissions du workflow.

Un rôle qui fait confiance à un ensemble trop large de workflows peut permettre à un pipeline non prévu d'obtenir des permissions sensibles.

### 9.4. Séparer build et déploiement

Une bonne conception distingue les responsabilités :

```text
Code source
    |
    v
Build et tests
    |
    v
Artefact versionné
    |
    v
Analyse et validation
    |
    v
Promotion contrôlée
    |
    v
Déploiement
    |
    v
Vérification post-déploiement
```

Lorsque cela convient, promouvoir le même artefact validé entre environnements réduit le risque de reconstruire un livrable différent.

## 10. Déploiements progressifs

### 10.1. Déploiement classique

Une nouvelle version remplace l'ancienne selon une stratégie donnée.

Le risque dépend notamment :
- de la compatibilité ;
- du nombre d'instances ;
- de la disponibilité ;
- de la gestion des données ;
- des mécanismes de retour arrière.

### 10.2. Blue-green

Deux environnements existent :
- bleu : version actuelle ;
- vert : version candidate.

```text
Avant bascule :

Trafic ---> Environnement bleu
            Environnement vert (préparé)

Après validation :

Trafic ---> Environnement vert
            Environnement bleu (repli possible)
```

Le retour arrière n'est sûr que si les données et les changements sont compatibles avec l'ancienne version.

### 10.3. Canary

La nouvelle version reçoit une partie limitée du trafic avant une augmentation progressive.

```text
100 % du trafic
       |
       v
Version stable

Phase canary :
  95 % stable
   5 % nouvelle version

Après validation :
  50 % stable
  50 % nouvelle version

Fin :
   0 % stable
 100 % nouvelle version
```

Les proportions sont illustratives.

Les critères de progression doivent être mesurables :
- taux d'erreur ;
- latence ;
- saturation ;
- erreurs métier ;
- impact sur les données.

### 10.4. Migrations de base de données

Les changements de schéma peuvent empêcher un retour arrière immédiat.

Une approche souvent utile est le modèle expand-and-contract :
1. Ajouter les nouveaux éléments de schéma.
2. Déployer une version compatible avec l'ancien et le nouveau schéma.
3. Migrer progressivement les données.
4. Vérifier l'utilisation.
5. Supprimer les éléments obsolètes lors d'une étape distincte.

Cette stratégie doit être adaptée au moteur et aux contraintes transactionnelles.

## 11. Kubernetes et conteneurs sur AWS

Les connaissances des cours Docker et Kubernetes sont maintenant appliquées aux services AWS.

### 11.1. Choisir le niveau de gestion

**ECS**

Convient lorsque l'équipe veut une orchestration de conteneurs intégrée à AWS sans avoir nécessairement besoin de l'écosystème Kubernetes.

**EKS**

Convient lorsque Kubernetes est requis pour ses API, son écosystème, ses opérateurs ou ses standards de plateforme.

**Lambda**

Convient à certaines charges événementielles ou de courte durée, lorsque le modèle d'exécution répond au besoin.

Le choix doit prendre en compte l'exploitation, le coût, les compétences, les limites d'exécution et les exigences de portabilité.

### 11.2. Sécurité d'EKS

Examiner :
- les permissions du plan de contrôle et des opérateurs ;
- l'authentification et l'autorisation Kubernetes ;
- les rôles IAM des composants ;
- l'identité des pods ;
- les Network Policies compatibles ;
- le chiffrement ;
- les mises à jour ;
- les images ;
- les journaux d'audit ;
- les contrôles de déploiement ;
- les sauvegardes des données persistantes.

Le plan de contrôle géré ne supprime pas la responsabilité de sécuriser les workloads et leurs identités.

### 11.3. Coûts d'orchestration

Les coûts peuvent inclure :
- le cluster et les fonctions de contrôle facturées selon le service ;
- les nœuds ou capacités de calcul ;
- les load balancers ;
- le stockage ;
- le trafic inter-AZ ;
- les journaux ;
- les NAT Gateways ;
- les transferts de données.

Un cluster peu utilisé peut coûter plus cher qu'un service plus simple. Il faut comparer le coût total et la charge opérationnelle.

## 12. SRE sur AWS : SLI, SLO et budgets d'erreur

### 12.1. SLI

Un Service Level Indicator est une mesure de qualité du service.

Exemples :
- proportion de requêtes réussies ;
- latence au 95e percentile ;
- durée d'exécution d'une opération métier ;
- taux de succès des traitements asynchrones.

La mesure doit refléter l'expérience réelle des utilisateurs lorsque cela est possible.

### 12.2. SLO

Un Service Level Objective est un objectif défini pour un SLI sur une période donnée.

Exemple :

```text
SLI : proportion de requêtes conformes
SLO : 99,9 % sur une fenêtre de 30 jours
```

Il faut définir les requêtes incluses, les erreurs comptées, les exclusions et les fenêtres de mesure.

### 12.3. Budget d'erreur

Le budget d'erreur correspond à la part d'échec tolérée par l'objectif.

Pour un SLO de disponibilité de 99,9 %, le budget théorique est de 0,1 % des événements comptabilisés sur la fenêtre considérée.

Le budget doit être calculé à partir du SLI réel. Il ne faut pas convertir automatiquement un pourcentage en minutes sans connaître la méthode de mesure.

### 12.4. Alarmes et impact utilisateur

Une alarme CPU élevée n'est pas toujours une panne utilisateur. À l'inverse, une application peut être en échec alors que la CPU est faible.

Privilégier les alertes basées sur :
- le taux d'erreur ;
- la latence ;
- les symptômes visibles ;
- les indicateurs métier ;
- l'épuisement du budget d'erreur.

Les métriques d'infrastructure restent importantes pour diagnostiquer les causes.

## 13. Gestion des incidents

### 13.1. Préparation

Avant un incident :
- définir les rôles ;
- documenter les services critiques ;
- tenir à jour les procédures ;
- vérifier les accès d'urgence ;
- définir les canaux de communication ;
- tester les sauvegardes ;
- pratiquer les exercices de reprise.

### 13.2. Cycle de réponse

```text
Détection
   |
   v
Qualification
   |
   v
Évaluation de l'impact
   |
   v
Confinement
   |
   v
Rétablissement
   |
   v
Validation du service
   |
   v
Postmortem
   |
   v
Actions correctives
```

Le confinement peut nécessiter la révocation d'identifiants, la restriction d'accès, l'isolement de ressources ou l'arrêt d'un déploiement. Les actions doivent être adaptées à l'incident et réalisées par les personnes autorisées.

### 13.3. Postmortem sans recherche de coupable

Le postmortem vise à comprendre les facteurs qui ont contribué à l'incident et à réduire le risque de récidive.

Il doit préciser :
- la chronologie ;
- l'impact ;
- les mécanismes de détection ;
- les causes techniques et organisationnelles ;
- les facteurs contributifs ;
- les actions correctives ;
- les responsables et échéances ;
- les mesures permettant de vérifier l'efficacité.

## 14. Gouvernance financière et FinOps

### 14.1. Responsabilité des coûts

La gestion des coûts ne doit pas être une opération ponctuelle menée uniquement après une facture élevée.

Elle s'appuie sur :
- une attribution claire ;
- des budgets ;
- des métriques d'usage ;
- des revues régulières ;
- des alertes ;
- des décisions d'architecture ;
- une responsabilité partagée entre équipes techniques et financières.

### 14.2. Tags et allocation

Exemple de tags :

```text
Environment = production
Application  = catalogue
Owner        = equipe-platform
CostCenter   = CC-104
ManagedBy    = Terraform
```

Les noms et valeurs doivent suivre une convention définie par l'organisation.

Les tags peuvent faciliter la recherche, la gouvernance et l'allocation des coûts, mais tous les services et rapports ne les exploitent pas exactement de la même manière.

### 14.3. Coût total

Le coût d'une architecture inclut notamment :
- calcul ;
- stockage ;
- base de données ;
- transferts ;
- NAT et load balancers ;
- journaux ;
- sauvegardes ;
- services de sécurité ;
- coûts opérationnels ;
- capacité de reprise.

Une architecture moins chère à l'heure peut être plus coûteuse à exploiter si elle exige de nombreuses interventions manuelles.

### 14.4. Optimisation

Pistes :
- dimensionner selon l'usage réel ;
- supprimer les ressources inutilisées ;
- ajuster la rétention des journaux ;
- réduire les transferts inutiles ;
- choisir les classes de stockage adaptées ;
- automatiser l'arrêt des environnements temporaires ;
- examiner les options tarifaires compatibles avec le profil de charge ;
- comparer les coûts et les risques de disponibilité.

Une optimisation ne doit pas dégrader silencieusement la sécurité, la durabilité ou les objectifs de service.

## 15. AWS Well-Architected Framework

AWS Well-Architected fournit un cadre pour évaluer une architecture à travers six piliers.

### 15.1. Les six piliers

1. Excellence opérationnelle.
2. Sécurité.
3. Fiabilité.
4. Efficacité des performances.
5. Optimisation des coûts.
6. Durabilité.

### 15.2. Méthode de revue

Pour chaque charge de travail :
1. Définir les exigences métier.
2. Identifier les risques majeurs.
3. Évaluer chaque pilier.
4. Documenter les décisions et compromis.
5. Prioriser les écarts.
6. Définir les actions correctives.
7. Mesurer les améliorations.
8. Refaire la revue lorsque l'architecture évolue.

Le cadre ne remplace ni les tests, ni l'audit de sécurité, ni la validation des exigences métier. Il structure les décisions et les améliorations.

## 16. Architecture de référence experte

### 16.1. Vue logique

```text
                       Utilisateurs
                            |
                            v
                     DNS / Point d'entrée
                            |
                            v
                 Protection et distribution
                            |
                            v
                Couche applicative multi-AZ
                            |
               +------------+------------+
               |                         |
               v                         v
          Données                    Services AWS
               |                         |
               +------------+------------+
                            |
                            v
                 Journaux et métriques
                            |
                            v
                Sécurité et observabilité

Gouvernance transversale :
  - comptes et organisations
  - identité et accès
  - réseau
  - politiques
  - sauvegardes
  - coûts
  - CI/CD
  - réponse aux incidents
```

Cette vue est conceptuelle. Les services précis sont choisis selon le besoin.

### 16.2. Décisions à documenter

Pour chaque composant :
- fonction ;
- propriétaire ;
- niveau de criticité ;
- frontière de sécurité ;
- disponibilité attendue ;
- stratégie de sauvegarde ;
- RPO et RTO ;
- mécanismes de supervision ;
- coût ;
- procédure de changement ;
- procédure de restauration.

## 17. Travaux pratiques experts

### TP 1 — Concevoir une organisation multi-comptes

Définir :
- le compte de management ;
- les comptes de sécurité ;
- les comptes réseau ;
- les comptes applicatifs ;
- les environnements ;
- les rôles d'administration ;
- les garde-fous ;
- les journaux centralisés.

Livrables :
- schéma de l'organisation ;
- matrice des responsabilités ;
- matrice d'accès ;
- stratégie de gouvernance.

Ne pas appliquer de SCP restrictive sur une organisation de production sans tests, validation et plan de récupération.

### TP 2 — Créer un modèle Terraform gouverné

Construire un dépôt qui comprend :
- des modules réutilisables ;
- une séparation des environnements ;
- un backend protégé ;
- un contrôle des versions ;
- des validations automatiques ;
- une revue de plan ;
- des permissions CI/CD limitées ;
- une procédure de récupération.

Les ressources de gouvernance doivent être testées dans un compte de laboratoire ou une organisation de test avant d'être généralisées.

### TP 3 — Concevoir une stratégie multi-région

Définir :
- le RPO ;
- le RTO ;
- les données répliquées ;
- les dépendances ;
- le DNS et la bascule ;
- les mécanismes d'identité ;
- la disponibilité des clés ;
- les quotas ;
- les tests de reprise ;
- les coûts.

Expliquer pourquoi la stratégie retenue est adaptée aux exigences métier.

### TP 4 — Simuler une réponse à incident

Scénario : une identité de pipeline présente des appels API inattendus.

Travail demandé :
1. Identifier les sources de journaux.
2. Déterminer l'identité et les ressources concernées.
3. Évaluer le périmètre.
4. Proposer un confinement.
5. Décrire la révocation des accès.
6. Vérifier l'intégrité des ressources.
7. Documenter la restauration.
8. Écrire un postmortem.
9. Proposer des mesures préventives.

L'exercice doit être simulé dans un environnement autorisé, sans compromettre un compte réel.

### TP 5 — Relier SLO et déploiement progressif

Définir un SLO de disponibilité pour une application.

Créer une stratégie canary qui :
- commence avec une faible part du trafic ;
- mesure les erreurs et la latence ;
- augmente progressivement la proportion ;
- bloque la progression si les indicateurs se dégradent ;
- permet un retour arrière ;
- produit des traces d'exécution.

Préciser comment les changements de données affectent le retour arrière.

## 18. Exercices corrigés

### Exercice 1 — SCP et IAM

Une SCP autorise certaines actions, mais l'utilisateur reçoit toujours `AccessDenied`. Pourquoi ?

**Correction :** une SCP n'accorde pas elle-même une permission. Les politiques IAM et de ressource, les conditions, les refus explicites et les autres restrictions doivent être examinés.

### Exercice 2 — Multi-région

Une application est déployée dans deux régions, mais les secrets et la base de données sont disponibles uniquement dans la région principale.

Est-elle pleinement résiliente à la perte de cette région ?

**Correction :** pas nécessairement. Les dépendances de données, d'identité, de clés et de configuration doivent également être disponibles ou restaurables dans la région de reprise.

### Exercice 3 — Déploiement canary

Le taux d'erreur augmente pendant une phase canary. Quelle action faut-il prévoir ?

**Correction :** arrêter la progression et déclencher la procédure définie, qui peut inclure le retour à la version stable. Il faut ensuite examiner les indicateurs et journaux avant de reprendre le déploiement.

### Exercice 4 — Terraform

Pourquoi séparer l'état Terraform de plusieurs environnements ?

**Correction :** limiter le rayon d'impact, éviter les modifications croisées, contrôler les accès et rendre les cycles de vie indépendants. Les détails dépendent de l'architecture du dépôt et du backend.

### Exercice 5 — Coût et fiabilité

Une équipe supprime une NAT Gateway pour réduire les coûts, mais les applications privées ne peuvent plus télécharger leurs dépendances.

Que faut-il faire ?

**Correction :** réexaminer les besoins de sortie réseau. Selon les services utilisés, des VPC endpoints, un proxy contrôlé, une architecture sans accès Internet ou une autre solution peuvent convenir. L'optimisation doit préserver les exigences fonctionnelles et de sécurité.

## 19. Projet final — Plateforme AWS gouvernée et résiliente

### Scénario

Une organisation exploite plusieurs applications, avec des environnements de développement, de recette et de production. Elle veut standardiser les déploiements, limiter les risques de sécurité et maîtriser ses coûts.

### Livrables

1. Architecture multi-comptes.
2. Stratégie d'identité et d'accès.
3. Politiques de gouvernance.
4. Architecture réseau.
5. Modèle Terraform réutilisable.
6. Chaîne CI/CD sécurisée.
7. Stratégie de journalisation et de détection.
8. Stratégie de sauvegarde et de reprise.
9. SLI, SLO et alertes.
10. Stratégie de déploiement progressif.
11. Modèle d'allocation des coûts.
12. Procédure de réponse à incident.
13. Plan de tests et de validation.
14. Documentation d'exploitation.

### Critères d'évaluation

- Isolation des environnements.
- Permissions minimales et identités traçables.
- Infrastructure reproductible.
- Chaîne d'approvisionnement contrôlée.
- Déploiements réversibles lorsque possible.
- Journalisation et détection exploitables.
- RPO et RTO justifiés.
- Tests de restauration.
- SLO mesurables.
- Coûts attribuables et maîtrisés.
- Procédures opérationnelles réalistes.

## 20. Checklist de production

### Gouvernance

- [ ] Comptes et environnements isolés.
- [ ] Propriétaires identifiés.
- [ ] Garde-fous documentés et testés.
- [ ] Accès privilégiés contrôlés.

### Identité et sécurité

- [ ] MFA et fédération adaptées.
- [ ] Permissions minimales.
- [ ] Secrets protégés.
- [ ] Journaux d'audit protégés.
- [ ] Détection et traitement des constats définis.

### Réseau et données

- [ ] Flux réseau documentés.
- [ ] Ressources publiques limitées.
- [ ] Chiffrement configuré.
- [ ] Sauvegardes protégées.
- [ ] Restauration testée.

### Déploiement

- [ ] Revue de code.
- [ ] Tests automatisés.
- [ ] Contrôle des artefacts.
- [ ] Permissions CI/CD limitées.
- [ ] Procédure de retour arrière.
- [ ] Changements destructifs encadrés.

### Fiabilité et exploitation

- [ ] SLI et SLO définis.
- [ ] Alertes actionnables.
- [ ] Procédures d'incident disponibles.
- [ ] RPO et RTO validés.
- [ ] Exercices de reprise effectués.

### FinOps

- [ ] Tags cohérents.
- [ ] Budgets configurés.
- [ ] Coûts examinés par service et environnement.
- [ ] Ressources inutilisées identifiées.
- [ ] Compromis coût-fiabilité documentés.

## 21. Glossaire

- **AWS Organizations** : gestion hiérarchique de comptes AWS.
- **Control Tower** : service de mise en place et de gouvernance multi-comptes.
- **SCP** : politique de contrôle des services.
- **OIDC** : mécanisme d'identité fédérée utilisé notamment par certains pipelines.
- **CloudTrail** : journalisation des événements d'activité AWS pris en charge.
- **AWS Config** : historique et évaluation de configuration.
- **GuardDuty** : détection de menaces.
- **Security Hub** : centralisation de constats de sécurité compatibles.
- **KMS** : service de gestion de clés cryptographiques.
- **Transit Gateway** : service de transit réseau entre réseaux compatibles.
- **PrivateLink** : connectivité privée à certains services.
- **RPO** : objectif de perte maximale de données.
- **RTO** : objectif de durée de restauration.
- **SLI** : indicateur de niveau de service.
- **SLO** : objectif de niveau de service.
- **FinOps** : pratique de gestion et d'optimisation économique du cloud.

## 22. Documentation officielle

### Architecture et gouvernance

- AWS Well-Architected : https://docs.aws.amazon.com/wellarchitected/
- AWS Organizations : https://docs.aws.amazon.com/organizations/
- AWS Control Tower : https://docs.aws.amazon.com/controltower/
- IAM Identity Center : https://docs.aws.amazon.com/singlesignon/
- Stratégie multi-comptes : https://docs.aws.amazon.com/wellarchitected/latest/framework/sec_securely_operate_multi_accounts.html

### Sécurité et audit

- IAM : https://docs.aws.amazon.com/IAM/latest/UserGuide/
- AWS CloudTrail : https://docs.aws.amazon.com/awscloudtrail/
- AWS Config : https://docs.aws.amazon.com/config/
- Amazon GuardDuty : https://docs.aws.amazon.com/guardduty/
- AWS Security Hub : https://docs.aws.amazon.com/securityhub/
- AWS KMS : https://docs.aws.amazon.com/kms/
- AWS Secrets Manager : https://docs.aws.amazon.com/secretsmanager/

### Réseau et reprise

- Amazon VPC : https://docs.aws.amazon.com/vpc/
- AWS Transit Gateway : https://docs.aws.amazon.com/vpc/latest/tgw/
- AWS PrivateLink : https://docs.aws.amazon.com/vpc/latest/privatelink/
- AWS Backup : https://docs.aws.amazon.com/aws-backup/
- AWS Elastic Disaster Recovery : https://docs.aws.amazon.com/drs/

### Infrastructure et déploiement

- Terraform AWS Provider : https://registry.terraform.io/providers/hashicorp/aws/latest/docs
- Bonnes pratiques Terraform pour AWS : https://docs.aws.amazon.com/prescriptive-guidance/latest/terraform-aws-provider-best-practices/
- Amazon ECS : https://docs.aws.amazon.com/ecs/
- Amazon EKS : https://docs.aws.amazon.com/eks/
- AWS CodeDeploy : https://docs.aws.amazon.com/codedeploy/
- AWS CodePipeline : https://docs.aws.amazon.com/codepipeline/

### Exploitation et coûts

- Amazon CloudWatch : https://docs.aws.amazon.com/cloudwatch/
- AWS Cost Management : https://docs.aws.amazon.com/cost-management/
- AWS Pricing Calculator : https://calculator.aws/
- AWS Budgets : https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html