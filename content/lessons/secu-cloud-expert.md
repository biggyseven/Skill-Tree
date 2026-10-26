# Sécurité du Cloud (AWS/Azure/GCP)

> **Mise en contexte**
>
> Le cloud permet de créer des serveurs, des bases de données, des réseaux, des identités et des services applicatifs en quelques minutes. Cette rapidité apporte de la souplesse, mais elle déplace aussi une partie de la sécurité vers la configuration, les identités, les API de gestion et l’automatisation. Un stockage rendu public, un rôle trop puissant, une clé laissée dans un dépôt ou une sauvegarde non protégée peuvent exposer des données sans qu’aucun intrus n’ait besoin de franchir un pare-feu traditionnel. Sécuriser le cloud demande donc de comprendre le modèle de responsabilité partagée, la hiérarchie des ressources, les autorisations, les chemins réseau, la protection des données, la journalisation et les mécanismes de réponse aux incidents propres à chaque fournisseur.

## Objectifs pédagogiques et scénario fil conducteur

Ce cours expert présente les principes communs de sécurité des environnements AWS, Microsoft Azure et Google Cloud. Il aide à concevoir une fondation cloud gouvernée, limiter les privilèges des utilisateurs et des charges de travail, réduire les expositions réseau et stockage, gérer les clés et secrets, centraliser les journaux, détecter les configurations dangereuses, protéger les chaînes de déploiement et organiser une réponse cloud documentée.

Le fil conducteur est une entreprise fictive appelée **Atlas Formation**. Elle héberge son portail, une API, des données d’apprenants, des fichiers de cours, des sauvegardes et des outils CI/CD. Une partie de l’environnement est sur AWS, une autre sur Azure et un projet expérimental sur Google Cloud. L’organisation souhaite comprendre les contrôles communs sans supposer que les produits portent les mêmes noms ou appliquent les mêmes règles.

Les manipulations pratiques doivent être menées dans un compte ou projet de test que vous contrôlez, avec des données fictives et des droits limités. Il n’est pas nécessaire de créer des ressources payantes pour effectuer les exercices de conception, rédiger les matrices IAM, vérifier des configurations d’exemple ou élaborer des plans d’incident. Ne créez pas volontairement une ressource exposée publiquement en production pour reproduire une mauvaise configuration.

## 1. Modèle de responsabilité partagée

### 1.1 Le fournisseur sécurise le cloud, le client sécurise son usage

Le fournisseur cloud protège les éléments qu’il opère : les bâtiments, une partie de l’infrastructure physique, les équipements et certaines couches de la plateforme, selon le service choisi. Le client reste responsable de décisions telles que les identités, les permissions, les données, la configuration réseau, les paramètres applicatifs, les clés dont il garde la maîtrise et les contrôles qui lui incombent.

La frontière exacte dépend du service. Avec une machine virtuelle IaaS, le client administre généralement le système d’exploitation invité, ses correctifs, le pare-feu hôte, les applications et les données. Avec une base de données managée PaaS, le fournisseur opère davantage de composants, mais le client doit encore configurer les accès, le réseau, les utilisateurs de base, les sauvegardes, la classification et la protection des données. Avec une application SaaS, le fournisseur contrôle l’essentiel de la plateforme, mais l’organisation doit toujours gérer les comptes, le MFA, le partage, les rôles, la rétention et les paramètres de sécurité disponibles.

~~~text
IaaS : le client gère davantage de couches
  identité / permissions / données
  applications / runtime / OS invité
  configuration réseau et sécurité du workload
  ---------------------------------------------
  infrastructure physique et couche cloud opérée

PaaS : le fournisseur gère plus de plateforme
  identité / permissions / données / application
  configuration des paramètres et accès
  ---------------------------------------------
  runtime, OS et infrastructure selon le service

SaaS : l'organisation gouverne surtout l'usage
  comptes / MFA / rôles / partage / données
  règles de conservation et intégration
  ---------------------------------------------
  application et plateforme opérées par le fournisseur
~~~

Ce schéma est conceptuel : la liste exacte des responsabilités varie selon le contrat et le service. Vérifiez le modèle documenté par le fournisseur pour la ressource concernée. Une base de données managée n’est pas automatiquement privée ; une application SaaS n’est pas automatiquement configurée selon la politique de partage de l’organisation.

### 1.2 Les malentendus fréquents

Les erreurs de responsabilité partagée produisent des hypothèses dangereuses : « le fournisseur chiffre tout, donc nous n’avons aucune clé à gérer » ; « la base est managée, donc personne ne peut l’atteindre publiquement » ; « les journaux existent, donc ils sont activés et conservés » ; « le cloud applique les correctifs, donc notre machine virtuelle est corrigée ». Ces affirmations peuvent être fausses ou incomplètes.

Pour chaque service, documentez ce que le fournisseur opère, ce que l’équipe cloud configure, ce que le propriétaire applicatif doit faire et les preuves disponibles. La matrice de responsabilités doit associer chaque contrôle à un propriétaire, une fréquence et un moyen de vérification.

~~~text
Contrôle                    Responsable principal
Sécurité physique           Fournisseur cloud
IAM de l'organisation       Client / équipe identité
Règles IAM du workload      Client / propriétaire applicatif
Correctifs OS invité IaaS   Client / équipe système
Moteur d'une base managée   Fournisseur selon le service
Paramètres d'accès à la DB  Client
Classification des données Client / métier
Activation des journaux     Client selon le service
Protection de l'historique  Client et capacités du service
~~~

### 1.3 Choisir un service en connaissant les compromis

Un service plus managé peut réduire le nombre de systèmes que l’équipe doit patcher, mais il ne supprime pas la responsabilité des données, de l’autorisation et de la configuration. Un service géré par le client peut offrir davantage de contrôle, mais crée une charge opérationnelle. La décision doit considérer sécurité, disponibilité, compétences, coût total, portabilité, résidence des données et capacité à collecter les preuves requises.

## 2. Concevoir une fondation cloud gouvernée

### 2.1 La hiérarchie des ressources est une frontière de sécurité

Chaque fournisseur organise les ressources dans une hiérarchie. Cette structure sert à répartir les propriétaires, les politiques et les permissions. Si l’organisation crée des environnements au hasard, les équipes peuvent contourner des garde-fous, mêler test et production ou accorder des droits globaux pour résoudre un besoin local.

Sur AWS, les comptes peuvent être organisés au moyen d’AWS Organizations et d’unités organisationnelles ; les Service Control Policies (SCP) peuvent fixer des limites de permissions au niveau de l’organisation ou d’unités organisationnelles, sans accorder à elles seules les permissions d’exécution. Sur Azure, les groupes d’administration, abonnements et groupes de ressources structurent la gouvernance ; Azure Policy sert à auditer ou appliquer des exigences de configuration tandis qu’Azure RBAC contrôle les actions autorisées. Sur Google Cloud, l’organisation, les dossiers, projets et ressources forment la hiérarchie ; IAM et les politiques d’organisation contribuent respectivement au contrôle d’accès et aux garde-fous.

~~~text
AWS
Organisation
  ├── OU Production
  │     ├── Compte Portail
  │     └── Compte Données
  └── OU Non-production
        ├── Compte Test
        └── Compte Développement

Azure
Tenant / groupes d'administration
  ├── Groupe Production -> abonnement -> groupes de ressources
  └── Groupe Non-production -> abonnements de test

Google Cloud
Organisation
  ├── Dossier Production -> projets Portail et Données
  └── Dossier Non-production -> projet Test
~~~

Les trois modèles ne sont pas identiques : une organisation AWS, un tenant Azure et une organisation Google Cloud ne sont pas des unités interchangeables. Le but est de comprendre les niveaux d’héritage, les périmètres d’administration et les limites de permissions. Les détails doivent être validés selon la configuration réelle.

### 2.2 Séparer production, test et développement

Séparez les environnements avec des frontières qui limitent l’impact d’une erreur. La séparation peut reposer sur des comptes ou abonnements distincts, des projets, des réseaux et des identités différentes. Évitez que les développeurs aient un rôle global de production simplement pour tester une application. Les données de production ne doivent pas être recopiées telles quelles vers un environnement moins protégé sans analyse et traitement adaptés.

Un utilisateur peut accéder à plusieurs environnements selon son rôle, mais les autorisations doivent être limitées et visibles. Les comptes d’urgence et identités de déploiement ont des périmètres documentés. Les environnements de test utilisent des données synthétiques et des secrets distincts.

### 2.3 Landing zone et garde-fous

Une landing zone est une fondation reproductible qui définit l’organisation des comptes ou projets, les identités, le réseau, la journalisation, les clés, les politiques, les tags ou labels et les contrôles de sécurité. Elle ne doit pas être réduite à un script qui crée quelques sous-réseaux : elle établit un modèle de gouvernance que les workloads peuvent réutiliser.

~~~text
Fondation cloud
  |
  +--> Hiérarchie / séparation des environnements
  +--> Identités et rôles standardisés
  +--> Réseau et accès privé
  +--> Journaux centraux protégés
  +--> Clés et secrets
  +--> Garde-fous de configuration
  +--> Inventaire, tags et propriétaires
  +--> Sauvegarde / reprise / réponse aux incidents
          |
          v
    Workloads déployés selon le modèle
~~~

La fondation doit fournir des chemins simples pour faire correctement les choses. Si l’équipe doit contourner un garde-fou pour déployer une application, l’architecture est probablement trop difficile à utiliser ou la règle est mal adaptée. Documentez le mécanisme d’exception, son approbateur, ses compensations et sa date d’expiration.

### 2.4 Contrôles préventifs, détectifs et correctifs

Une politique préventive interdit une configuration au moment de sa création ou de sa modification. Une politique détective repère l’écart et alerte. Une action corrective peut, lorsque c’est sûr et autorisé, ramener automatiquement une ressource à l’état attendu. Ces approches se complètent : une interdiction absolue est adaptée à un risque clair, tandis qu’une alerte est utile quand la remédiation automatique pourrait interrompre un service légitime.

~~~text
Configuration demandée
        |
        v
Garde-fou préventif
  ├── refus si violation non dérogeable
  └── autorisation si conforme
        |
        v
Évaluation continue de l'état réel
  ├── conforme : conserver une preuve
  └── non conforme : alerte / ticket / remédiation contrôlée
~~~

Les garde-fous doivent être versionnés et testés. Une règle qui interdit tous les accès publics peut casser un site qui doit publier des ressources ; une bonne règle peut exiger que seuls des objets précis soient publics, qu’un propriétaire approuve l’exposition et que le contenu soit séparé du plan d’administration. La politique doit exprimer le risque plutôt qu’un simple réflexe d’interdiction.

## 3. Identités et contrôles d'accès cloud

### 3.1 Principals, rôles et permissions

Un principal peut être un utilisateur, un groupe, un rôle, un compte de service ou une identité de charge de travail. Une permission décrit une action possible sur une ressource. Un rôle rassemble des permissions. Une politique associe identités, ressources, actions et conditions, selon le modèle du fournisseur. Il faut examiner non seulement les rôles directement accordés mais aussi les héritages, groupes, délégations et permissions implicites.

Un rôle global de propriétaire ou d’administrateur est un outil de dernier recours, pas un rôle par défaut. Préférez des rôles intégrés minimaux lorsque leur portée correspond au besoin ; utilisez des rôles personnalisés si nécessaire, avec une revue attentive. Les permissions sensibles incluent la création ou modification d’identités, l’attribution de rôles, la suppression de journaux, la modification de règles réseau, l’accès aux secrets, le changement des politiques d’organisation et la désactivation des mécanismes de détection.

~~~text
Demande : lire les fichiers d'un cours
  Principal : service API
  Ressource : stockage privé de cours
  Action : lecture d'objets nécessaires
  Conditions : identité de workload valide
  Résultat : accès à la seule ressource attendue

Demande : gérer tout le compte cloud
  Principal : même service API
  Résultat : refus, la permission dépasse sa fonction
~~~

### 3.2 Moindre privilège et séparation des tâches

Le moindre privilège limite les droits à une tâche et une durée. La séparation des tâches évite qu’une seule identité puisse modifier la configuration, approuver sa propre modification et supprimer les preuves. Par exemple, la personne qui publie une application ne devrait pas nécessairement pouvoir désactiver la journalisation centrale ou modifier la politique de sauvegarde.

Les permissions doivent être revues lors d’un changement de rôle, d’un départ, d’une fin de projet ou d’un changement de responsabilité. Les groupes historiques et les comptes orphelins doivent être découverts. Une revue périodique ne suffit pas si un accès peut être révoqué automatiquement lors d’un changement d’identité ; les deux pratiques se complètent.

### 3.3 Identités humaines, MFA et accès privilégié

Les comptes humains doivent être fédérés lorsque cela convient à l’organisation, protégés par une authentification forte et surveillés. Le MFA ne compense pas un rôle surdimensionné. Les administrateurs devraient utiliser des comptes dédiés à l’administration, avec une élévation temporaire lorsque possible et des alertes sur les changements critiques.

Protégez les comptes de récupération et de secours. Un mécanisme break-glass doit être rare, isolé, vérifié régulièrement et déclencher une alerte. Les secrets de secours ne doivent pas être conservés dans un document partagé avec un accès plus large que le compte qu’ils permettent de récupérer. Définissez la durée d’élévation, le motif, les approbations et les éléments d’audit.

### 3.4 Identités de charge de travail

Les applications et pipelines doivent utiliser des identités dédiées au lieu de clés permanentes copiées dans des fichiers. Selon le fournisseur, on peut utiliser des rôles de workload, des identités managées, des comptes de service, une fédération de charge de travail ou des jetons temporaires. L’équivalence n’est pas un-à-un : comparez la façon d’obtenir les identifiants, les audiences, les permissions, la rotation et la révocation.

~~~text
CI/CD
  |
  | fédération d'identité vers le cloud
  v
Identité de déploiement à durée limitée
  |
  +--> publier l'artefact approuvé
  +--> déployer dans l'environnement cible
  X--> lire toutes les données de production
  X--> modifier les comptes d'administration
  X--> désactiver les journaux
~~~

Une clé statique peut être nécessaire pour certains systèmes hérités, mais elle doit être documentée, placée dans un gestionnaire de secrets, limitée, surveillée et renouvelée. Son exposition dans un dépôt ou une image doit déclencher une révocation, pas seulement une suppression du fichier. Vérifiez aussi les identités utilisées par les agents de build, scripts de migration, fonctions et tâches planifiées.

### 3.5 Héritage et permissions effectives

Les systèmes de permissions cloud utilisent souvent des héritages : un droit accordé haut dans la hiérarchie peut affecter plusieurs projets ou abonnements. Les conditions peuvent aussi restreindre la portée. Une revue doit vérifier les permissions effectives, pas seulement les politiques attachées directement à une ressource. La propagation d’un changement de rôle peut prendre du temps selon le service ; le plan d’incident doit connaître ces délais.

## 4. AWS : principales couches de sécurité

### 4.1 Comptes et AWS Organizations

AWS permet d’organiser les comptes sous une organisation et des unités organisationnelles. Séparer les comptes de production, de journalisation, de sécurité, de test et de développement peut réduire le rayon d’impact et clarifier les responsabilités. Les comptes membres doivent utiliser une fédération et des rôles explicites plutôt que partager des identifiants racine.

Les Service Control Policies (SCP) peuvent définir les permissions maximales disponibles dans des périmètres organisationnels, mais elles ne donnent pas à elles seules une permission d’exécution. Il faut comprendre les interactions entre SCP, politiques IAM, politiques de ressource, permissions boundaries et autres mécanismes appliqués. Une SCP est un garde-fou, non un substitut à une politique IAM de moindre privilège.

~~~text
AWS Organizations
  |
  +--> OU Security
  |      +--> compte de journalisation
  |      +--> compte sécurité
  |
  +--> OU Production
  |      +--> compte application
  |      +--> compte données
  |
  +--> OU Sandbox
         +--> comptes temporaires à durée limitée

Garde-fous : SCP
Accès : IAM / rôles / politiques de ressource
Preuves : CloudTrail / configuration / alertes
~~~

### 4.2 IAM, rôles et accès temporaires

Évitez les clés d’accès de longue durée lorsque des rôles et identifiants temporaires sont possibles. Examinez les politiques pour les actions, ressources et conditions accordées. Les politiques trop générales utilisant une ressource wildcard peuvent être justifiées dans certains contextes, mais elles doivent être expliquées et testées. Une permission d’assumer un rôle doit préciser qui peut l’assumer et dans quelles conditions.

Le compte racine doit être protégé, utilisé uniquement pour les tâches nécessaires et non pour le travail quotidien. Vérifiez la MFA, les mécanismes de récupération, les coordonnées et les alertes. Réduisez l’usage de clés statiques, identifiez leur propriétaire et leur dernière utilisation, puis révoquez les clés inutiles. Contrôlez aussi les accès inter-comptes : une relation de confiance mal définie peut étendre le rayon d’impact.

### 4.3 Réseau, instances et services managés

Les VPC, sous-réseaux, tables de routage, groupes de sécurité et ACL réseau contribuent à la séparation des flux. Les groupes de sécurité appliquent des règles à des ressources ; les ACL réseau opèrent au niveau du sous-réseau selon leur modèle. Ne publiez pas une base de données sur Internet simplement parce qu’une application a besoin d’y accéder. Préférez un accès privé entre la couche applicative et les données, des règles source-destination-port minimales et des chemins d’administration contrôlés.

Pour les machines virtuelles, durcissez l’OS, corrigez les vulnérabilités, limitez les ports d’administration, surveillez les agents et protégez les métadonnées d’instance selon les recommandations du service. Une règle réseau cloud ne remplace pas le pare-feu système et les contrôles applicatifs.

### 4.4 Stockage, clés et journaux

Les buckets S3 doivent être privés par défaut, et les mécanismes de blocage de l’accès public doivent être examinés aux périmètres compte et bucket selon le besoin. Vérifiez les politiques de bucket, les ACL historiques, les points d’accès, les URL présignées, la réplication et les journaux. Une URL présignée reste un moyen d’accès temporaire ; sa durée et la permission du signataire influencent le risque.

AWS KMS peut gérer des clés pour plusieurs services ; les politiques de clé et les politiques IAM doivent être étudiées ensemble. CloudTrail enregistre des activités de compte et d’API selon sa configuration. AWS Config permet de suivre et d’évaluer la configuration des ressources. Des services de détection comme GuardDuty peuvent contribuer à repérer des signaux de menace. L’activation, le périmètre, la conservation, les coûts et les flux vers le compte de sécurité doivent être vérifiés explicitement.

~~~text
Compte workload
  |
  +--> IAM roles : permissions minimales
  +--> VPC / Security Groups : flux nécessaires
  +--> S3 privé : accès explicite et versionnement si requis
  +--> KMS : clés et permissions séparées
  |
  v
Compte sécurité / journalisation
  +--> CloudTrail centralisé
  +--> Config et règles de conformité
  +--> alertes de détection
  +--> stockage de preuves protégé
~~~

### 4.5 Questions d'audit AWS

Un audit en lecture seule peut examiner les identités, politiques, accès publics au stockage, groupes de sécurité ouverts, présence de journaux et règles de chiffrement. Les outils de ligne de commande et interfaces doivent être employés dans un compte autorisé, avec une attention particulière à leurs effets. Ne copiez pas les clés ou jetons dans un rapport.

Questions importantes :
- Les clés d’accès racine sont-elles absentes ou désactivées lorsque le service le permet ?
- Les utilisateurs humains utilisent-ils une fédération et des rôles temporaires ?
- Les rôles de service sont-ils limités au compte et au workload ?
- Aucun stockage sensible n’est-il exposé sans justification ?
- Les traces d’administration sont-elles envoyées vers un périmètre distinct et protégées contre la suppression ?
- Les ressources critiques ont-elles un propriétaire, un tag et une procédure de restauration ?

## 5. Microsoft Azure : principales couches de sécurité

### 5.1 Tenant, groupes d’administration, abonnements et ressources

Azure organise les ressources au travers d’un tenant, des groupes d’administration, des abonnements et des groupes de ressources. Les choix de hiérarchie déterminent comment les politiques et permissions héritées s’appliquent. Séparez les abonnements de production et de non-production lorsque c’est pertinent, et évitez les rôles globaux tenant pour les tâches courantes.

Azure RBAC permet d’attribuer des rôles à des identités dans des portées définies. Un rôle au niveau de l’abonnement peut produire un effet beaucoup plus large qu’un rôle au niveau d’une ressource. Examinez les rôles directs, groupes, héritages, permissions d’application et identités de service.

~~~text
Tenant Microsoft Entra ID
  |
  +--> Groupe d'administration Production
  |       +--> Abonnement Production
  |               +--> Groupe de ressources Portail
  |               +--> Groupe de ressources Données
  |
  +--> Groupe d'administration Non-production
          +--> Abonnements Test / Développement

Azure RBAC : qui peut faire quoi, et à quelle portée
Azure Policy : configurations exigées ou évaluées
Entra ID : identités, authentification et fédération
~~~

### 5.2 Entra ID, rôles et accès privilégié

Microsoft Entra ID fournit les fonctions d’identité et d’authentification des environnements Azure. Protégez les comptes administratifs avec MFA et des politiques d’accès conditionnel adaptées. L’accès conditionnel peut évaluer des signaux tels que l’utilisateur, l’application, l’appareil et le risque selon les capacités disponibles et configurées ; testez les politiques pour éviter un verrouillage non planifié.

Privileged Identity Management (PIM), lorsqu’il est disponible et configuré, peut aider à rendre certaines attributions éligibles plutôt que permanentes et exiger des conditions pour l’activation. Définissez approbations, justifications, durée, notifications et revue. L’existence d’un outil ne garantit pas que les rôles dangereux ne sont plus attribués en permanence.

### 5.3 Azure Policy et Defender for Cloud

Azure Policy permet d’auditer ou de faire respecter certains états de configuration à la portée choisie. Les effets possibles et modes de remédiation dépendent de la définition et de l’affectation de la politique. Testez les initiatives avant leur extension à tous les abonnements ; une politique restrictive peut bloquer des déploiements valides si le contexte du workload n’est pas compris.

Microsoft Defender for Cloud peut contribuer à l’évaluation de posture, aux recommandations de sécurité et à la détection pour les environnements pris en charge. La couverture dépend des plans, connecteurs, ressources et configurations activés. Ne supposez pas que toutes les capacités sont présentes ou gratuites. Validez quelles ressources sont connectées, quelles alertes sont transmises et qui est responsable du traitement.

### 5.4 Réseau, secrets et journaux

Les réseaux virtuels, groupes de sécurité réseau (NSG), routes, pare-feu et Private Link peuvent contribuer à isoler les ressources. Une adresse privée n’équivaut pas toujours à une protection suffisante : le routage, les peerings, les règles de sortie, les accès de gestion et les identités restent importants.

Azure Key Vault peut protéger secrets, clés et certificats avec des contrôles d’accès. Attribuez les permissions les plus étroites possible, surveillez les lectures et changements, et utilisez une identité managée lorsque le service le permet. L’Azure Activity Log et les journaux des ressources couvrent des catégories différentes ; activez l’acheminement et la conservation requis, car le simple fait qu’une catégorie de logs existe ne signifie pas qu’elle est consultable dans le SIEM central.

~~~text
Fondation Azure
  |
  +--> Entra ID : MFA / accès conditionnel / identités
  +--> RBAC : permissions et portées minimales
  +--> Azure Policy : garde-fous de configuration
  +--> NSG / Private Link : flux ciblés
  +--> Key Vault : secrets et clés
  +--> Activity Log / diagnostics : visibilité
  +--> Defender for Cloud : posture et alertes selon couverture
~~~

## 6. Google Cloud : principales couches de sécurité

### 6.1 Organisation, dossiers et projets

Google Cloud organise les ressources en organisation, dossiers et projets. Cette hiérarchie détermine l’héritage des politiques IAM et des politiques d’organisation. La séparation des projets aide à isoler les environnements, propriétaires, quotas, facturation et ressources. Elle ne garantit pas automatiquement que les réseaux ou les identités sont indépendants ; examinez les permissions héritées et les connexions inter-projets.

~~~text
Organisation Google Cloud
  |
  +--> Dossier Production
  |      +--> Projet Portail
  |      +--> Projet Données
  |
  +--> Dossier Non-production
  |      +--> Projet Tests
  |
  +--> Dossier Sécurité / Journalisation
         +--> ressources de surveillance
~~~

### 6.2 IAM, comptes de service et politiques d’organisation

Google Cloud IAM associe des rôles à des principals dans des périmètres. Les rôles prédéfinis peuvent être préférables à un rôle de base trop large, mais la portée et les permissions doivent être vérifiées. Les rôles Owner, Editor ou Viewer historiques ne doivent pas être accordés systématiquement si un rôle plus limité existe. Les politiques d’organisation peuvent imposer des restrictions à certains types de ressources ou usages, selon les contraintes du service.

Les comptes de service sont des identités de workloads. Évitez de télécharger une clé de compte de service persistante lorsqu’une identité attachée à la charge de travail ou une fédération est possible. Si une clé est indispensable, protégez son stockage, limitez son usage, tracez sa dernière utilisation et révoquez-la lorsqu’elle n’est plus nécessaire. Workload Identity Federation peut permettre à des workloads externes autorisés d’obtenir un accès sans conserver une clé permanente, selon les systèmes et configurations pris en charge.

### 6.3 Réseau, stockage et services de données

Les VPC, règles de pare-feu, routes, contrôles de sortie et mécanismes d’accès privé déterminent les chemins possibles. Cloud Storage doit utiliser une politique d’accès appropriée et les contrôles de prévention de l’accès public quand c’est pertinent. Les droits au niveau du bucket ou du projet peuvent être plus larges que prévu ; testez les accès effectifs et les liens de partage.

VPC Service Controls peut contribuer à créer des périmètres autour de services pris en charge et réduire certains risques d’exfiltration ; il ne remplace pas IAM ou le contrôle des identités. Évaluez dépendances, appels de services et flux légitimes avant d’appliquer les périmètres. Cloud KMS gère des clés cryptographiques ; les identités autorisées à utiliser ou administrer une clé doivent être séparées lorsque le risque le justifie.

### 6.4 Journaux, inventaire et posture

Cloud Audit Logs couvre plusieurs catégories d’activité et d’accès ; toutes les catégories n’ont pas nécessairement le même mode d’activation ou de conservation. Cloud Asset Inventory aide à découvrir les ressources et suivre des données de configuration selon ses capacités. Security Command Center peut fournir des fonctions de posture et de détection selon l’édition, la couverture et la configuration. Vérifiez les projets, services et catégories réellement surveillés plutôt que de considérer un tableau de bord comme une preuve de couverture complète.

~~~text
Organisation / dossiers / projets
  |
  +--> IAM : rôles et principals
  +--> Org Policy : garde-fous applicables
  +--> VPC / firewall : flux réseau
  +--> Cloud Storage : accès et exposition
  +--> Cloud KMS : gestion des clés
  +--> Cloud Audit Logs : activités
  +--> Cloud Asset Inventory : découverte
  +--> Security Command Center : posture / détection selon périmètre
~~~

## 7. Comparer les fournisseurs sans supposer une équivalence parfaite

### 7.1 Tableau de repères

Les noms ci-dessous servent de points de départ. Ils ne représentent pas des équivalences fonctionnelles exactes : chaque service a ses portées, coûts, conditions d’activation, intégrations et limites. Il faut comparer le résultat de sécurité attendu plutôt que d’aligner des marques.

| Besoin de sécurité | AWS | Microsoft Azure | Google Cloud |
|---|---|---|---|
| Hiérarchie multi-environnements | Organizations / OU / comptes | Tenant / groupes d’administration / abonnements | Organisation / dossiers / projets |
| Accès aux ressources | IAM, rôles, politiques de ressource | Entra ID, Azure RBAC, identités managées | IAM, rôles, comptes de service, fédération |
| Garde-fous de configuration | SCP, AWS Config, règles | Azure Policy, initiatives | Organization Policy, règles de conformité |
| Activité de gestion | CloudTrail | Activity Log | Cloud Audit Logs |
| Posture et détection | Config, GuardDuty et services associés | Defender for Cloud et services associés | Security Command Center et services associés |
| Gestion des clés et secrets | KMS, Secrets Manager | Key Vault | Cloud KMS, Secret Manager |
| Découverte des ressources | Inventaire et configuration selon les outils | Azure Resource Graph et outils associés | Cloud Asset Inventory |
| Réseau et accès privé | VPC, groupes de sécurité, endpoints privés | VNet, NSG, Private Link | VPC, règles de pare-feu, accès privé |
| Protection des workloads | Services et contrôles selon le workload | Defender et contrôles selon les ressources | Protections selon le workload |

Le fait de retrouver un nom similaire ne garantit pas la même couverture. Confirmez la portée de journalisation, les événements enregistrés, les régions prises en charge, la rétention, les coûts, la profondeur de détection et les intégrations SIEM. Les services évoluent et certaines fonctions peuvent être incluses dans des offres différentes.

### 7.2 Méthode de comparaison technique

Pour comparer deux services, établissez une fiche avec le besoin, l’événement ou la configuration contrôlée, l’identité nécessaire, les données collectées, les régions, la conservation, la latence, la sortie du système, les coûts et les responsabilités. Testez ensuite avec un scénario contrôlé. Une fonction qui génère une alerte mais ne transmet pas l’événement au bon espace de travail ne répond pas au besoin opérationnel.

~~~text
Besoin : détecter une exposition publique de stockage
  1. Quel service vérifie la configuration ?
  2. Quelle ressource et quelle portée sont couvertes ?
  3. L'exposition est-elle bloquée ou seulement signalée ?
  4. Qui reçoit l'alerte et dans quel délai ?
  5. Qui peut supprimer ou altérer la preuve ?
  6. Comment la correction est-elle confirmée ?
~~~

### 7.3 Multi-cloud et complexité

Le multi-cloud peut répondre à des besoins commerciaux, réglementaires ou techniques, mais il augmente souvent le nombre de modèles IAM, de politiques réseau, de formats de journaux et de mécanismes de chiffrement à comprendre. Une équipe doit éviter de masquer ces différences derrière une abstraction qui ne représente pas les permissions réelles. Définissez un socle organisationnel commun et conservez les particularités nécessaires à chaque fournisseur dans des modules explicites.

Un modèle commun peut exprimer « aucune ressource de données sensible ne doit avoir un accès public non approuvé », mais les règles techniques diffèrent selon les services. Les tests et rapports doivent indiquer quel fournisseur, quelle ressource, quelle règle et quel état sont concernés.

## 8. Données, chiffrement et gestion des clés

### 8.1 Classifier les données

Les données doivent être classées selon leur sensibilité, les besoins métier, les obligations de conservation et les risques d’exposition. La classification détermine les permissions, les chemins de partage, les exigences de chiffrement, la surveillance, les copies autorisées et les délais de suppression. Des données publiques peuvent nécessiter une protection d’intégrité ; des résultats d’apprentissage, informations personnelles ou secrets de déploiement exigent une protection plus stricte.

~~~text
Inventaire des données
   |
   +--> propriétaire métier et finalité
   +--> classe de sensibilité
   +--> emplacement et copies
   +--> rôles de lecture / écriture / export
   +--> chiffrement et gestion des clés
   +--> conservation / suppression
   +--> journaux et réponse aux incidents
~~~

N’oubliez pas les exports CSV, rapports, caches, sauvegardes, index de recherche, copies de test et journaux. La protection du système primaire ne compense pas une copie confidentielle téléchargée dans un environnement moins contrôlé.

### 8.2 Chiffrement au repos et en transit

Le chiffrement au repos réduit certains risques lorsque le support est perdu ou que l’accès direct au stockage est obtenu, mais ne protège pas contre un principal autorisé qui lit les données. Le chiffrement en transit protège le canal entre les points qui l’utilisent, mais ne résout pas un mauvais contrôle de permissions à la destination. Vérifiez les protocoles, certificats, paramètres, exclusions et chemins de communication.

### 8.3 Gérer les clés séparément

La sécurité dépend de qui peut créer, utiliser, exporter, désactiver ou supprimer une clé. Séparez les rôles d’administration de la clé et d’utilisation des données lorsque le risque le justifie. Documentez la rotation, les versions de clés, l’expiration des certificats, les sauvegardes nécessaires et les conditions de révocation. Une clé supprimée sans comprendre les dépendances peut rendre des données irrécupérables.

~~~text
Compte de workload
  |
  +--> peut demander l'usage d'une clé pour une opération précise
  X--> ne peut pas supprimer ou modifier la politique de clé

Équipe sécurité / clés
  |
  +--> gère le cycle de vie et les autorisations
  +--> surveille les usages sensibles
  +--> teste les procédures de récupération
~~~

### 8.4 Secrets et coffre-fort

Les secrets d’application incluent mots de passe, clés d’API, jetons, certificats privés et chaînes de connexion. Ils doivent être stockés dans un gestionnaire de secrets adapté, récupérés par des identités de workload autorisées, masqués dans les logs et rotatés selon le risque. L’accès à tous les secrets de tous les environnements par une même identité constitue un privilège excessif.

La rotation est un processus, pas seulement un clic. Il faut déterminer quels consommateurs utilisent le secret, déployer la nouvelle valeur, vérifier la transition, révoquer l’ancienne et surveiller les échecs. En cas d’exposition, révoquez immédiatement selon l’urgence et examinez les usages éventuels.

### 8.5 Résidence et conformité

Le choix d’une région peut influencer la disponibilité, la latence, la résidence, les mécanismes de reprise et les obligations applicables. Évitez de promettre une conformité uniquement parce qu’un fournisseur propose une région dans un pays donné. L’organisation doit définir la catégorie de données, les contrats et obligations applicables, la localisation des copies et journaux, les accès de support, la conservation et la suppression, puis vérifier le service et la configuration réels.

## 9. Réseau cloud et expositions publiques

### 9.1 Inventorier les chemins réseau

Les réseaux virtuels, sous-réseaux, tables de routage, groupes de sécurité, listes de contrôle, pare-feu, NAT, passerelles et connexions privées déterminent les chemins d’accès. Un service sans IP publique peut être accessible via un proxy, un service managé ou une route de peering. Il faut comprendre les chemins réels, et ne pas déduire la sécurité de la seule présence d’une adresse privée.

~~~text
Navigateur
   |
   v
Point d'entrée public limité
   |
   v
Frontend / API en réseau privé
   |
   +--> données privées via flux minimal
   +--> gestion via identité et chemin administré
   |
   X--> aucune route générale du poste vers la base
~~~

### 9.2 Revoir les règles trop larges

Une règle d’entrée ouverte à toute source, notamment sur un port d’administration, doit être considérée comme un signal à examiner. Ce n’est pas la seule exposition possible : un service peut être accessible via une passerelle, un endpoint public d’API, un partage de fichier ou une configuration de stockage. Le remède dépend du besoin : accès privé, authentification, restriction de source, proxy, pare-feu applicatif ou retrait de la ressource.

Pour l’administration, privilégiez des voies contrôlées telles qu’un bastion, une console à accès restreint ou un mécanisme d’accès privé approprié. Évitez les règles permanentes temporaires et planifiez leur suppression. Si un flux doit être ouvert à Internet, documentez le service, les contrôles applicatifs, les alertes et le responsable.

### 9.3 Contrôler les sorties et l'exfiltration

Les flux sortants peuvent permettre l’exfiltration ou la récupération d’outils non autorisés. Limitez les destinations et services nécessaires lorsque c’est réalisable, surveillez les volumes inhabituels et contrôlez les résolutions DNS et les proxys selon le modèle de menace. Un filtrage de sortie peut casser les dépendances de mise à jour ; le mode d’application doit être observé et documenté.

La prévention d’exfiltration combine identités, contrôle d’accès aux données, segmentation, restrictions d’export, quotas, chiffrement, journaux et détection de comportements inhabituels. Aucun contrôle unique ne suffit. Un compte autorisé à exporter toutes les données vers un stockage externe peut exfiltrer sans contourner une ACL réseau. La règle d’export doit être définie au niveau de l’application et de l’identité.

## 10. Journalisation, détection et posture cloud

### 10.1 Activer les bons journaux

Les plateformes proposent différentes catégories : opérations de gestion, accès aux données, événements d’identité, flux réseau, événements applicatifs et détection. Certaines catégories doivent être activées, routées ou configurées séparément. Confirmez les événements attendus et réalisez un test observable. Ne supposez pas que l’existence d’un menu de journalisation signifie que tous les événements sont envoyés et conservés.

~~~text
Sources
  +--> identité / authentification
  +--> API de gestion du cloud
  +--> ressources et données
  +--> flux réseau / DNS
  +--> workloads / applications
  +--> posture / alertes de sécurité
          |
          v
Collecte centralisée et horodatage
          |
          v
Normalisation / corrélation / règles d'alerte
          |
          v
Ticket / réponse / preuve de clôture
~~~

### 10.2 Séparer et protéger les preuves

Les journaux critiques ne devraient pas être modifiables ou supprimables par les mêmes identités que celles surveillées. Utilisez des périmètres distincts, des droits restreints, des mécanismes d’intégrité disponibles et une conservation adaptée aux besoins. Les événements doivent comporter assez de contexte pour attribuer une action sans copier des secrets ni des données inutiles.

### 10.3 Détection de configuration et de comportement

Une mauvaise configuration peut être repérée par une règle : stockage rendu public, base exposée, chiffrement absent, identités trop privilégiées, journal désactivé ou ressource non approuvée. Une détection comportementale observe des activités inhabituelles : rôle administrateur créé, secret consulté en masse, export important, modifications inhabituelles de règles réseau ou suppression des journaux.

Les outils de CSPM (Cloud Security Posture Management) évaluent la posture de configuration selon les ressources et règles couvertes. Ils ne remplacent pas la validation métier ni les tests d’accès. Un outil peut classer une ressource selon une règle générique, mais l’équipe doit qualifier l’impact et la pertinence dans le contexte de l’application.

### 10.4 Alertes actionnables et tests de couverture

Une alerte devrait contenir le type d’événement, le compte ou projet, la ressource, l’heure, le principal concerné, le risque, les actions récentes liées, l’équipe responsable et la procédure de réponse. Définissez un seuil de gravité et un délai de prise en charge. Évitez les alertes très nombreuses sans propriétaire : elles deviennent du bruit et les vrais événements peuvent être manqués.

Vérifiez régulièrement qu’un événement de test apparaît dans la destination attendue et déclenche le bon traitement. Testez aussi les cas où la collecte s’arrête, la destination est indisponible, la limite de quota est atteinte ou une ressource n’envoie plus de logs. La couverture doit être mesurée sur les ressources critiques, les catégories d’événements et le délai d’arrivée, et non uniquement avec un indicateur « connecté ».

## 11. Gestion des vulnérabilités, durcissement et IaC

### 11.1 Inventaire et priorité

L’inventaire doit identifier ressources, système d’exploitation, versions, expositions, propriétaire, sensibilité et dépendances. La priorité d’une vulnérabilité dépend de la possibilité d’exploitation, de l’exposition, de l’importance de l’actif, de la présence d’un exploit et des mesures compensatoires. Un score technique élevé mérite l’attention mais ne résume pas tout le contexte opérationnel.

Les ressources éphémères doivent également être inventoriées. Une machine créée par un pipeline peut disparaître de la console, mais l’image, le modèle de déploiement et les identifiants utilisés ont besoin d’un contrôle. Les scans périodiques peuvent manquer une ressource de courte durée ; l’infrastructure as code et l’intégration CI peuvent ajouter des contrôles avant déploiement.

### 11.2 Durcir les workloads IaaS

Pour les machines virtuelles, choisissez des images de base maintenues, supprimez les comptes inutiles, limitez les ports, mettez en place des mises à jour, activez une protection endpoint adaptée et évitez les identifiants partagés. Les snapshots et disques détachés peuvent contenir des données sensibles ; ils doivent être chiffrés, limités et supprimés selon la politique.

### 11.3 Sécurité des images et des artefacts

Les images conteneurs, paquets, scripts de déploiement et modèles IaC font partie de la chaîne d’approvisionnement. Scannez les dépendances, vérifiez les provenances et signatures disponibles, contrôlez les permissions des pipelines et protégez les artefacts approuvés. Les images doivent être versionnées et reproductibles ; évitez les tags mutables non contrôlés pour les déploiements critiques.

~~~text
Commit approuvé
    |
    v
Analyse de code / dépendances / IaC
    |
    v
Build isolé avec identité limitée
    |
    v
Contrôles de l'artefact et provenance
    |
    v
Registre contrôlé
    |
    v
Déploiement vers l'environnement autorisé
    |
    v
Vérification de configuration après déploiement
~~~

### 11.4 Infrastructure as Code

Les politiques cloud devraient être encodées dans des modèles versionnés lorsque c’est possible. Cela améliore la revue et la reproductibilité, mais ne garantit pas automatiquement la sécurité. Il faut contrôler les variables, valeurs par défaut, secrets, permissions, modules externes, changements de plan et état réel après déploiement. La dérive manuelle peut faire diverger la ressource de son modèle.

Séparez les permissions de lecture, de planification et d’application quand le risque le justifie. Les pipelines de production devraient exiger une approbation adaptée, un artefact versionné et un identifiant de déploiement. N’intégrez jamais un secret dans un fichier de variables suivi par Git simplement parce que le modèle est du code.

## 12. Sauvegarde, résilience et réponse aux incidents

### 12.1 Sauvegarde indépendante

Les sauvegardes sont une cible : un attaquant ayant obtenu un rôle administrateur peut chercher à les supprimer ou les chiffrer. Limitez les identités qui peuvent créer, lire, supprimer ou restaurer les sauvegardes. Considérez les copies inter-comptes ou inter-projets, les mécanismes d’immuabilité disponibles, l’accès aux clés et les procédures de restauration. Une sauvegarde non testée n’est pas une preuve de récupérabilité.

~~~text
Données de production
       |
       v
Sauvegarde protégée
       |
       +--> compte / projet de sauvegarde séparé
       +--> droits de suppression plus stricts
       +--> chiffrement et clés gérées
       +--> copie selon le plan de reprise
       +--> tests de restauration documentés
~~~

### 12.2 Définir RPO et RTO

Le Recovery Point Objective (RPO) indique la quantité de perte de données temporelle acceptable. Le Recovery Time Objective (RTO) indique le délai cible pour restaurer le service. Les deux sont des exigences métier qui guident la fréquence des sauvegardes, la réplication et les tests. Répliquer une suppression ou une corruption ne constitue pas toujours une sauvegarde suffisante ; il faut pouvoir revenir à une version saine.

### 12.3 Répondre à un incident cloud

Un incident peut impliquer un secret exposé, une identité compromise, une ressource publique accidentelle, une suppression de logs, un rôle trop puissant ou une activité anormale d’une charge de travail. Le plan de réponse doit préciser les identités d’intervention, la conservation des preuves, les actions d’isolement, la rotation des secrets, la restauration et les communications.

~~~text
Détection
  |
  v
Triage : compte/projet, identité, ressource, gravité
  |
  v
Contenir : révoquer identité/jeton, isoler flux ou workload
  |
  v
Préserver les preuves : journaux et artefacts autorisés
  |
  v
Éradiquer : corriger la politique, reconstruire un état sain
  |
  v
Récupérer : restaurer, vérifier et surveiller
  |
  v
Revue : cause, impact, actions et prévention de récidive
~~~

### 12.4 Préserver les preuves sans aggraver l’incident

Ne supprimez pas immédiatement une ressource compromise sans examiner les exigences de preuve. Une instance peut être isolée, ses identifiants révoqués et ses journaux copiés dans un périmètre protégé selon la procédure. Évitez toutefois de retarder un confinement nécessaire simplement pour recueillir chaque artefact. Le plan doit définir les priorités et qui peut approuver les actions.

### 12.5 Séparation des privilèges pendant la crise

Les identités de réponse doivent être préparées avant l’incident. Si les seuls administrateurs capables d’enquêter sont les mêmes identités potentiellement compromises, la réponse peut échouer. Préparez des comptes d’intervention protégés, une journalisation indépendante et des procédures de récupération de l’accès. Testez les scénarios de perte du fournisseur d’identité principal ou de compromission du compte de gestion central.

## 13. Gouvernance, coût, conformité et risques humains

### 13.1 Tags, labels et propriétaires

Les tags ou labels peuvent documenter l’application, le propriétaire, l’environnement, la classe de données, le centre de coût, la date d’expiration et la criticité. Ils permettent de cibler les politiques et rapports, mais ne constituent pas une preuve indépendante si un utilisateur peut les modifier librement. Définissez des contrôles qui vérifient leur présence et restreignent les changements.

Les ressources sans propriétaire sont difficiles à maintenir et à sécuriser. Une ressource temporaire devrait avoir une durée prévue et une procédure de suppression. Une règle de nettoyage automatique doit d’abord être testée pour éviter de supprimer un actif critique mal étiqueté.

### 13.2 Coût et disponibilité des contrôles

La collecte, le stockage et l’analyse des logs, les outils de détection, les scans et les copies de sauvegarde peuvent engendrer des coûts. Ne désactivez pas un contrôle critique à la suite d’un dépassement sans examiner le besoin, la rétention et les volumes. Établissez un budget, des filtres qui n’éliminent pas les événements essentiels, des alertes de quota et une revue régulière du coût de sécurité.

### 13.3 Conformité ne signifie pas absence de risque

Une certification ou un rapport de conformité peut aider à évaluer un fournisseur et une portée. Il ne prouve pas qu’une ressource précise est configurée correctement. Vérifiez la période, les services couverts, les régions, les responsabilités du client et les exclusions. Maintenez des preuves de configuration et des tests internes pour votre propre environnement.

### 13.4 Gestion des changements

Un changement de politique IAM ou réseau peut affecter de nombreuses ressources à cause de l’héritage. Exigez une revue pour les changements à fort impact, comparez le plan proposé à l’état actuel et conservez un retour arrière. Les changements urgents doivent rester traçables et faire l’objet d’une revue après coup. La gestion des changements est un contrôle de sécurité, pas uniquement une formalité administrative.

## 14. Méthode d'audit cloud pratique

### 14.1 Construire un inventaire de sécurité

Pour chaque compte, abonnement ou projet, collectez les ressources, propriétaires, environnements, permissions, expositions réseau, paramètres de stockage, chiffrement, journaux, sauvegardes et services de détection activés. Identifiez les identités humaines et machine, y compris celles utilisées par CI/CD, jobs planifiés et applications.

~~~text
Fiche d'audit d'une ressource
  ID / compte / projet :
  Type et propriétaire :
  Environnement / criticité :
  Données et classe de sensibilité :
  Principals / permissions effectives :
  Entrées et sorties réseau :
  Accès public ou privé :
  Chiffrement / clés / secrets :
  Journaux / alertes :
  Sauvegardes / restauration :
  Exceptions et échéances :
  Preuves / résultat / responsable :
~~~

### 14.2 Tests de lecture seule

Commencez par des vérifications en lecture seule dans un périmètre autorisé. Les requêtes d’inventaire, les rapports IAM et les évaluations de configuration doivent être adaptés à l’environnement réel. Ne copiez pas de credentials dans un terminal partagé ou un rapport. Si une commande ou un outil est inconnu, validez d’abord sa portée et son effet, puis préférez le mode d’évaluation sans modification.

### 14.3 Résultats reproductibles

Un constat utile précise le périmètre, la ressource, la règle attendue, le résultat observé, la preuve, l’impact, la recommandation, le propriétaire et la date de correction. Capturez un minimum de données sensibles. Les contrôles automatisés doivent conserver la version de la règle et de l’outil pour pouvoir reproduire le résultat.

## 15. Travaux pratiques corrigés

### TP 1 — Concevoir la fondation cloud d’Atlas Formation

**Objectif :** séparer les environnements, définir les responsabilités et choisir les garde-fous communs.

**Contexte :** le portail, la base de résultats et le pipeline sont répartis entre AWS, Azure et Google Cloud. Les équipes de développement souhaitent tous les droits pour accélérer les tests. L’équipe sécurité veut isoler production et non-production, centraliser les preuves et limiter les changements globaux.

**Étape 1.** Dessinez la hiérarchie des ressources choisie dans chaque fournisseur. Documentez les comptes AWS et unités organisationnelles, les groupes d’administration et abonnements Azure, ainsi que l’organisation, dossiers et projets Google Cloud. Identifiez les périmètres de journalisation.

**Étape 2.** Affectez un propriétaire à chaque workload et définissez des rôles distincts pour développeur, opérateur, sécurité, auditeur et pipeline. Limitez les permissions de production et définissez une procédure d’exception.

**Étape 3.** Définissez les garde-fous qui doivent s’appliquer partout : pas de stockage public non approuvé, aucun secret en clair dans le dépôt, journaux critiques activés et acheminés, ressources critiques identifiées, chiffrement adapté, flux minimaux et accès administratifs protégés.

**Étape 4.** Prévoyez le mode d’application : refuser les configurations clairement dangereuses, auditer les écarts qui exigent une validation métier et corriger automatiquement seulement lorsque le risque de casse est maîtrisé.

~~~text
Résultat attendu
Production : identités restreintes, données réelles, journaux protégés
Test : données fictives, secrets séparés, permissions réduites
Développement : ressources temporaires, durée de vie limitée
Sécurité : inventaire, alertes, preuves séparées des workloads
Pipeline : identité temporaire et déploiement limité au périmètre prévu
~~~

**Correction expliquée.** La structure ne doit pas copier à l’identique les mêmes objets dans les trois clouds. Elle établit des objectifs communs, puis les implémente avec les fonctions natives de chaque fournisseur. Les garde-fous préventifs doivent être testés avant extension ; un contrôle qui bloque les déploiements sans donner de voie légitime d’exception encouragera les contournements.

**Critères d’acceptation :** chaque workload possède un propriétaire ; production est séparée de non-production ; le pipeline ne peut pas gérer l’ensemble de l’organisation ; les journaux sont envoyés vers un périmètre protégé ; les exceptions ont une échéance ; les tests démontrent le refus des configurations interdites.

### TP 2 — Revue IAM d'une charge de travail multi-cloud

**Objectif :** détecter les permissions excessives et remplacer les secrets persistants lorsque possible.

**Contexte :** une API lit les fichiers de cours, met à jour la progression et déploie une version via CI/CD. L’API possède un rôle global pour faciliter l’accès à plusieurs projets ; le pipeline a une clé statique de longue durée. Les noms de ressources sont fictifs.

**Étape 1.** Énumérez les actions nécessaires à l’API et au pipeline. Distinguez lecture des fichiers, écriture de progression, publication de l’artefact, création de ressources et administration des identités.

**Étape 2.** Définissez des rôles distincts : l’API lit uniquement le stockage de cours et écrit uniquement les données de progression prévues ; le pipeline publie un artefact approuvé dans l’environnement cible ; l’équipe d’identité gère les attributions privilégiées selon un processus séparé.

**Étape 3.** Remplacez si possible la clé persistante par une identité de workload ou une fédération adaptée. Fixez une audience et une durée, éliminez les secrets du dépôt et prévoyez la révocation des clés existantes après migration.

**Étape 4.** Testez les refus : l’API essaie de modifier les rôles cloud, le pipeline tente de lire les données de production, un compte de test essaie de déployer en production et une ancienne clé doit être refusée après révocation.

~~~text
API :
  autorisé -> lire les objets de cours ciblés
  autorisé -> écrire la progression prévue
  refusé   -> modifier IAM et politiques d'organisation

Pipeline :
  autorisé -> déployer un artefact approuvé dans le périmètre cible
  refusé   -> lire des secrets sans rapport avec le build
  refusé   -> désactiver les journaux / gérer les comptes globaux
~~~

**Correction expliquée.** La meilleure permission correspond à l’action réellement nécessaire. Un rôle global évite parfois de comprendre les dépendances, mais rend une compromission beaucoup plus grave. Une identité de workload ou une fédération peut réduire la présence de secrets persistants. Si une clé statique reste temporairement obligatoire, elle doit être stockée de façon sûre, limitée, surveillée et assortie d’une date de retrait.

**Critères d’acceptation :** matrice de permission par principal ; justification de chaque droit sensible ; tests de refus ; identités et secrets séparés par environnement ; révocation prouvée ; aucune clé dans les fichiers de code ou journaux.

### TP 3 — Détecter et corriger une exposition de stockage et de réseau

**Objectif :** transformer une mauvaise configuration cloud en constat vérifiable et en correction contrôlée.

**Contexte :** un scanner signale qu’un stockage de supports de cours pourrait être public et qu’une machine d’administration accepte une connexion réseau trop large. N’effectuez aucun changement dans un compte réel sans approbation ; réalisez l’exercice à partir d’une configuration fictive ou d’un environnement de laboratoire.

**Étape 1.** Identifiez les données, le propriétaire, la portée exacte de la politique et les chemins d’accès. Distinguez accès public volontaire, partage temporaire, accès par identité et accès au niveau du compte.

**Étape 2.** Vérifiez les permissions effectives et les règles héritées. Identifiez les politiques de bucket ou conteneur, les liens présignés, les règles NSG ou groupes de sécurité, les routes et les points d’entrée indirects.

**Étape 3.** Pour les données non publiques, retirez l’exposition non approuvée et choisissez un mécanisme d’accès privé ou une autorisation explicite. Pour la machine d’administration, utilisez le chemin contrôlé et restreignez les sources, destinations et ports selon le besoin.

**Étape 4.** Vérifiez le changement avec une identité autorisée et une identité non autorisée. Confirmez les journaux, l’absence de chemin de contournement et la continuité des usages légitimes.

~~~text
Avant
Stockage de supports -> accès public non justifié
Machine d'administration -> source réseau trop large

Après
Stockage -> permissions explicites / partage limité / audit
Administration -> identité forte + chemin contrôlé + source minimale
Preuve -> test autorisé et test refusé + logs vérifiés
~~~

**Correction expliquée.** Une alerte générique doit être qualifiée : certains contenus sont volontairement publics et les téléchargements temporaires peuvent répondre à un besoin métier. La correction ne consiste pas simplement à désactiver tout accès, mais à garantir qu’il correspond au besoin approuvé. La règle réseau doit être corrigée sur toutes les portées concernées et non uniquement sur l’interface visible.

**Critères d’acceptation :** le propriétaire confirme la classe des données ; la règle réelle est identifiée ; l’accès non autorisé échoue ; l’accès légitime continue ; les journaux contiennent la preuve utile ; aucune route directe alternative n’est oubliée.

### TP 4 — Répondre à un incident de clé cloud exposée

**Objectif :** orchestrer confinement, révocation, preuve, récupération et prévention de récidive.

**Contexte :** une clé de service est découverte dans l’historique d’un dépôt. Elle est supposée compromise. Le service a accès à un stockage de fichiers et à une partie des métadonnées applicatives.

**Étape 1.** Qualifiez l’identité, les permissions, la date d’exposition et la dernière utilisation observée. Conservez les journaux disponibles et l’identifiant du ticket sans recopier le secret lui-même.

**Étape 2.** Révoquez la clé ou limitez immédiatement ses permissions selon le plan d’intervention, en tenant compte de la disponibilité. Créez une nouvelle identité ou méthode d’authentification plus sûre et préparez la transition des consommateurs.

**Étape 3.** Recherchez les usages inhabituels : lectures massives, création de rôles, accès depuis un contexte atypique, changements de réseau ou suppression de journaux. Évaluez les ressources accessibles et les données potentiellement exposées.

**Étape 4.** Supprimez le secret des sources où il ne doit pas apparaître, mais ne confondez pas suppression du texte et révocation. Déployez la nouvelle configuration, vérifiez le fonctionnement et éliminez la clé ancienne. Ajoutez une règle de détection de secret et réduisez la permission de l’identité.

~~~text
Clé exposée
  |
  +--> identifier principal, portée et permissions
  +--> conserver preuves sans recopier le secret
  +--> révoquer / contenir selon le plan
  +--> créer une identité sûre et migrer le workload
  +--> rechercher les usages suspects et impacts
  +--> vérifier logs, données et chemins d'accès
  +--> supprimer l'ancienne clé et prévenir la récidive
~~~

**Correction expliquée.** Supprimer la clé du dernier commit ne la rend pas confidentielle, car elle peut exister dans l’historique, les forks, caches ou logs. La révocation est centrale. Le délai de rotation doit être équilibré avec l’impact sur la disponibilité, mais la possibilité d’un usage actif doit être traitée en priorité. Le périmètre des permissions indique la zone à examiner ; les journaux permettent de réduire l’incertitude sans garantir à eux seuls qu’aucun usage n’a échappé à la collecte.

**Critères d’acceptation :** la clé ancienne est refusée ; le service fonctionne avec l’identité nouvelle ; les logs et ressources accessibles ont été examinés ; le secret n’apparaît plus dans les configurations actives ; un test de prévention de secret est ajouté ; le ticket indique la cause et les actions de suivi.

## 16. Exercices corrigés

### Exercice 1 — Responsabilité partagée

Une équipe utilise une base de données managée et suppose que le fournisseur configure automatiquement les droits d’accès aux données.

**Correction :** le fournisseur opère la plateforme selon le service, mais le client reste responsable des permissions, utilisateurs, classification, réseau et paramètres accessibles. Il faut vérifier le modèle de responsabilité du service précis et tester l’accès effectif.

### Exercice 2 — Rôle d’administrateur sur tous les environnements

Tous les développeurs possèdent un rôle global car les ressources de test et production sont organisées ensemble.

**Correction :** séparez les environnements, appliquez des rôles ciblés et retirez les permissions de production inutiles. La hiérarchie cloud doit soutenir la réduction du rayon d’impact. Un rôle global ne doit pas être le raccourci habituel pour résoudre les erreurs de permission.

### Exercice 3 — Stockage supposé privé

Un bucket ou conteneur n’a pas d’adresse publique affichée, mais une politique permet à un principal très large de lire les objets.

**Correction :** une adresse réseau ou une interface privée ne suffit pas à prouver la confidentialité. Vérifiez les permissions effectives, politiques héritées, liens partagés et accès directs. Appliquez l’accès minimal puis testez avec une identité autorisée et une autre qui doit être refusée.

### Exercice 4 — Chiffrement automatique

Une organisation active le chiffrement au repos et estime qu’un compte cloud compromis ne peut plus lire les données.

**Correction :** le chiffrement au repos ne bloque pas un principal autorisé à utiliser le service pour déchiffrer et lire les données. Les permissions sur les ressources et les clés, l’identité, la détection et la séparation des tâches restent essentielles.

### Exercice 5 — Clé dans une image de conteneur

Une clé cloud est copiée dans une image pour que le conteneur puisse accéder au stockage.

**Correction :** l’image peut être copiée et inspectée. Retirez le secret, révoquez-le s’il a été publié, utilisez une identité de charge de travail ou un coffre-fort approprié et réduisez les permissions. Les images doivent être reconstruites à partir d’un état sain.

### Exercice 6 — Journaux activés dans la console

Le portail affiche une section CloudTrail, Activity Log ou Cloud Audit Logs ; l’équipe suppose donc que toute activité est capturée.

**Correction :** catégories, périmètres, services, destinations et durées de rétention varient. Effectuez une action de test autorisée et confirmez l’arrivée du bon événement dans la destination de surveillance. Testez aussi les pertes de collecte et les quotas.

### Exercice 7 — Équivalence des outils de posture

Un acheteur considère AWS Config, Azure Policy et Google Cloud Organization Policy comme des outils exactement identiques.

**Correction :** ces services couvrent des fonctions qui se recoupent partiellement mais n’ont pas la même portée ni le même comportement. Définissez le besoin — prévention, audit, détection ou remédiation — puis comparez les capacités, coûts, couverture, héritages et preuves.

### Exercice 8 — Permissions héritées

Une ressource a une politique directe minimale, mais un groupe parent possède un rôle plus large.

**Correction :** les droits effectifs peuvent venir de l’héritage ou d’autres mécanismes. Examinez la hiérarchie, groupes, rôles et politiques qui s’appliquent. Corrigez le périmètre responsable puis vérifiez que le droit excessif n’est plus effectif.

### Exercice 9 — Clé de production dans les tests

Une équipe réutilise la même clé de service en développement et production pour simplifier la configuration.

**Correction :** créez des identités et secrets distincts, avec des permissions et ressources séparées. La compromission de l’environnement moins protégé ne doit pas fournir un chemin direct vers la production.

### Exercice 10 — Accès réseau large

Une règle autorise l’administration d’une machine depuis toutes les adresses Internet car l’équipe « utilise plusieurs réseaux ».

**Correction :** recensez les origines nécessaires et choisissez un accès administré, un bastion ou une politique privée adaptée. Les exceptions temporaires doivent expirer. Vérifiez également les chemins indirects, les règles héritées et l’accès par console.

### Exercice 11 — Clé gérée par le fournisseur

Le client ne gère pas directement une clé et suppose que cela règle tous les risques cryptographiques.

**Correction :** la gestion par le fournisseur peut réduire certaines tâches, mais le choix de service, les permissions, les accès de l’application, la disponibilité et les exigences de rotation restent à vérifier. Distinguez les responsabilités selon la clé et le service.

### Exercice 12 — Politiques préventives partout

Une règle bloque automatiquement toute ressource non conforme, y compris des environnements de test temporaires.

**Correction :** tous les risques ne justifient pas le même mode de remédiation. Les contrôles préventifs conviennent aux risques clairs ; les écarts qui nécessitent une analyse peuvent être signalés et traités avec un délai. Il faut éviter les contournements et disposer d’un workflow d’exception.

### Exercice 13 — Service de détection non connecté

L’équipe a activé un produit de posture, mais les alertes n’arrivent jamais dans le SIEM.

**Correction :** vérifiez la couverture des ressources, catégories d’événements, permissions de collecte, destination, filtres, quotas et erreurs. Réalisez un test contrôlé, confirmez la réception et attribuez une responsabilité de suivi.

### Exercice 14 — Sauvegarde dans le même périmètre

Un compte de production et un rôle applicatif peuvent supprimer simultanément les données et les sauvegardes.

**Correction :** séparez les permissions et le périmètre de sauvegarde, protégez les clés et activez les mécanismes d’immuabilité disponibles lorsqu’ils sont requis. Testez la restauration depuis un incident simulé et confirmez RPO et RTO.

### Exercice 15 — Multi-cloud masqué

Un outil de gouvernance présente les trois clouds dans un tableau unique et supprime toute indication du fournisseur de chaque constat.

**Correction :** conservez une vue commune du risque, mais gardez la provenance, la ressource et la règle propre à chaque fournisseur. Sans ces détails, il devient impossible de reproduire ou corriger précisément un constat.

### Exercice 16 — Image de base non maintenue

Une machine virtuelle utilise une image ancienne parce que l’instance fonctionne toujours.

**Correction :** inventoriez le système, l’exposition et les vulnérabilités, puis mettez à jour ou remplacez l’image selon un processus testé. La stabilité apparente ne prouve pas la sécurité. Les images et templates doivent être versionnés et contrôlés.

### Exercice 17 — Secret supprimé du commit

Une clé apparaît dans un commit, puis le développeur supprime la ligne de configuration dans un commit ultérieur.

**Correction :** révoquez et remplacez la clé. Analysez les journaux et usages possibles, examinez les permissions et réduisez la portée de la nouvelle identité. La suppression du fichier n’efface pas toutes les copies historiques.

### Exercice 18 — Conformité fournisseur

Un fournisseur annonce une certification ; l’entreprise considère tous ses workloads conformes sans examiner leur configuration.

**Correction :** la certification couvre une portée, une période et un ensemble de contrôles. Les clients doivent encore configurer et tester leur environnement, vérifier les responsabilités qui leur incombent et conserver les preuves de leur mise en œuvre.

### Exercice 19 — Détection d’anomalies non testée

Une règle d’alerte est configurée mais n’a jamais été déclenchée en exercice.

**Correction :** testez le scénario, vérifiez les journaux et la livraison, contrôlez la qualification de l’alerte et le délai de réponse. Documentez le résultat, les faux positifs et les actions de correction. Une règle non validée ne fournit pas une assurance solide.

### Exercice 20 — Remédiation automatique

Un outil corrige automatiquement toutes les règles réseau jugées trop larges sans connaître les dépendances des applications.

**Correction :** commencez par l’inventaire et l’observation, qualifiez les flux puis choisissez les remédiations réversibles. Une correction automatique doit disposer de garde-fous, de tests, d’une preuve de résultat et d’un mécanisme de retour arrière. Les changements critiques doivent suivre la gouvernance définie.

## 17. Défi final corrigé — sécuriser la plateforme cloud d'Atlas Formation

### Situation

Atlas Formation constate quatre problèmes : le pipeline de production possède un rôle trop large ; les fichiers de cours sont stockés dans un service cloud sans classification complète ; les événements d’administration sont collectés dans certains comptes mais pas tous ; et une clé d’API utilisée par un service est présente dans un ancien dépôt. La direction veut une amélioration mesurable sans interrompre le portail.

### Travail demandé

1. Prioriser les risques et identifier les actifs exposés.
2. Définir les corrections d’identité, de stockage, de journalisation et de secrets.
3. Comparer l’approche AWS, Azure et Google Cloud sans affirmer une équivalence exacte.
4. Définir des tests de validation, des preuves et des critères de sortie.
5. Préparer une feuille de route progressive et un plan d’incident.

### Correction détaillée

**1. Priorité.** Traitez d’abord la clé potentiellement exposée et l’identité de pipeline surpuissante. Identifiez le périmètre exact des permissions et les activités récentes. Les fichiers doivent être classifiés ; ceux qui contiennent des données personnelles ou confidentielles ne doivent être accessibles qu’aux identités prévues. La lacune de journalisation doit être évaluée pour déterminer quelles opérations n’ont pas de preuve disponible.

**2. Identités.** Réduisez le rôle du pipeline au dépôt d’artefacts et au déploiement de la cible déterminée. Remplacez les clés statiques par une identité de workload ou une fédération si le modèle le permet. Révoquez l’ancienne clé après transition et examinez son usage. Les comptes humains et administratifs doivent utiliser des contrôles forts, une portée minimale et une élévation temporaire adaptée.

**3. Données.** Attribuez un propriétaire et une classe à chaque jeu de fichiers. Définissez les droits de lecture et d’écriture. Vérifiez les permissions héritées, l’accès public éventuel, les liens partagés, le chiffrement, les clés et les journaux d’accès. Séparez les exports et sauvegardes, puis confirmez les voies de restauration.

**4. Observabilité.** Activez et acheminez les catégories nécessaires pour les opérations de gestion, l’identité, l’accès aux données et les alertes de posture. Les tests doivent déclencher une action contrôlée dans chaque environnement et confirmer la réception de l’événement. Définissez une alerte lors de changements de rôles sensibles, de désactivation de journaux et d’exposition de stockage.

**5. Mise en œuvre multi-cloud.** Définissez les objectifs communs : moindre privilège, absence d’accès public non approuvé, journaux critiques centralisés, secrets hors des dépôts et propriétaires identifiés. Implémentez les garde-fous dans AWS Organizations/IAM/Config/CloudTrail, Azure RBAC/Policy/Activity Log/Key Vault et Google Cloud IAM/Organization Policy/Cloud Audit Logs/Secret Manager selon les services réels. Vérifiez les différences de périmètre et d’héritage dans chaque cloud.

**6. Tests et sortie.** Le pipeline ne doit plus modifier les identités globales ; l’ancien secret est refusé ; les identités non autorisées ne lisent pas les fichiers confidentiels ; les actions de gestion apparaissent dans la destination centrale ; l’exposition d’un stockage provoque un signal et un traitement attribué. La release ne se termine pas à la simple activation d’un service : les tests doivent prouver le résultat et l’équipe de réponse doit savoir comment traiter une alerte.

~~~text
Plan d'action
Phase 1 : contenir la clé exposée et réduire le pipeline
Phase 2 : inventorier et classifier fichiers et ressources
Phase 3 : compléter journaux et alertes des environnements
Phase 4 : appliquer les garde-fous par fournisseur
Phase 5 : tester accès, refus, révocation et restauration
Phase 6 : mesurer les écarts et attribuer les responsables
~~~

### Grille de notation suggérée

~~~text
Priorisation et modèle de responsabilité          15 points
IAM et identités de workload                      25 points
Classification, stockage et secrets              20 points
Journalisation, détection et réponse              20 points
Tests, preuves et déploiement progressif           20 points
Total                                            100 points
Seuil recommandé de validation                    80 points
~~~

Une bonne réponse n’est pas celle qui active le plus grand nombre de produits. Elle relie actifs et menaces à des contrôles effectifs, fournit des preuves reproductibles, définit un propriétaire et une procédure de réponse et tient compte des différences entre services cloud.

## 18. Checklist de mise en production cloud

- [ ] La responsabilité du fournisseur et celle du client sont documentées pour chaque service critique.
- [ ] La hiérarchie des comptes, abonnements ou projets sépare les environnements et limite l’héritage.
- [ ] Les rôles humains et machines sont minimaux et revus.
- [ ] Les comptes privilégiés sont protégés par authentification forte et accès temporaire lorsque possible.
- [ ] Les identités de workload remplacent les clés statiques quand la plateforme le permet.
- [ ] Les secrets ne sont pas présents dans les dépôts, images, journaux ou artefacts.
- [ ] Les ressources de stockage sont privées par défaut et toute exposition publique est approuvée.
- [ ] Les règles réseau n’exposent pas les ports d’administration sans justification.
- [ ] Les permissions de clés sont séparées et les procédures de rotation testées.
- [ ] Les données, exports et sauvegardes sont classifiés et protégés.
- [ ] Les événements d’identité, d’administration, de données et de réseau nécessaires sont collectés.
- [ ] Les journaux sont centralisés, protégés contre la modification et conservés selon les besoins.
- [ ] Les mécanismes de posture et de détection couvrent les bonnes ressources.
- [ ] Les alertes ont un propriétaire, un seuil, un délai et une procédure de traitement.
- [ ] Les vulnérabilités et images de base sont inventoriées et mises à jour.
- [ ] Les modèles IaC et pipelines sont versionnés, relus et limités par environnement.
- [ ] La restauration des sauvegardes a été testée selon le RPO et le RTO attendus.
- [ ] Les plans de révocation, confinement et récupération ont été exercés.
- [ ] Les garde-fous et remédiations automatiques disposent d’un retour arrière testé.
- [ ] Les écarts et exceptions ont un responsable, une justification et une échéance.

## 19. Glossaire

**Cloud computing :** accès à la demande à des ressources informatiques opérées selon un modèle de service défini.  
**IaaS :** modèle fournissant principalement des ressources d’infrastructure, laissant au client la gestion de nombreuses couches.  
**PaaS :** modèle où le fournisseur gère une partie plus importante de la plateforme d’exécution.  
**SaaS :** application fournie comme service, dont l’usage doit encore être configuré et gouverné par le client.  
**Responsabilité partagée :** répartition des tâches de sécurité entre fournisseur et client.  
**IAM :** gestion des identités, rôles, permissions et politiques d’accès.  
**Principal :** identité à laquelle une permission peut s’appliquer.  
**Moindre privilège :** attribution des droits minimaux nécessaires.  
**Landing zone :** fondation gouvernée pour organiser les environnements cloud, identités, réseau et contrôles.  
**SCP :** Service Control Policy AWS, garde-fou limitant les permissions disponibles sans les accorder à lui seul.  
**Azure RBAC :** contrôle des actions Azure selon une identité, un rôle et une portée.  
**Azure Policy :** mécanisme de gouvernance pour auditer ou imposer des états de configuration.  
**Organization Policy :** règles de garde-fou dans la hiérarchie Google Cloud.  
**Workload Identity :** identité attribuée à une application ou un processus automatisé.  
**Gestionnaire de secrets :** service de gestion des secrets dont l’accès doit lui-même être contrôlé.  
**KMS :** service ou système de gestion de clés cryptographiques.  
**CSPM :** Cloud Security Posture Management, évaluation de l’état de configuration et des écarts de sécurité.  
**CloudTrail / Activity Log / Cloud Audit Logs :** exemples de services de journalisation d’activités de gestion avec des portées différentes.  
**IaC :** Infrastructure as Code, définition versionnée des ressources et de leur configuration.  
**RPO :** quantité maximale de perte de données temporelle acceptable lors d’une reprise.  
**RTO :** délai cible de restauration d’un service.  
**Break-glass :** accès d’urgence exceptionnel et surveillé.  
**Exfiltration :** transfert non autorisé de données hors de l’environnement protégé.  
**Permissions effectives :** résultat de l’ensemble des politiques, rôles, héritages et conditions qui s’appliquent réellement.  
**Dérive de configuration :** différence entre la configuration attendue et l’état réel d’une ressource.

## 20. Références officielles

- NIST SP 800-210, *General Access Control Guidance for Cloud Systems* : https://csrc.nist.gov/pubs/sp/800/210/final
- AWS Well-Architected Framework : https://docs.aws.amazon.com/wellarchitected/
- AWS Well-Architected Framework — Security Pillar : https://docs.aws.amazon.com/wellarchitected/2025-02-25/framework/a-security.html
- AWS IAM User Guide : https://docs.aws.amazon.com/IAM/latest/UserGuide/
- AWS CloudTrail User Guide : https://docs.aws.amazon.com/awscloudtrail/latest/userguide/
- Microsoft Cloud Security Benchmark : https://learn.microsoft.com/en-us/security/benchmark/
- Microsoft Learn — Azure role-based access control : https://learn.microsoft.com/en-us/azure/role-based-access-control/
- Microsoft Learn — Azure Policy : https://learn.microsoft.com/en-us/azure/governance/policy/
- Microsoft Learn — Microsoft Defender for Cloud : https://learn.microsoft.com/en-us/azure/defender-for-cloud/
- Google Cloud Well-Architected Framework — Security, Privacy and Compliance : https://docs.cloud.google.com/architecture/framework/security
- Google Cloud Enterprise Foundations Blueprint : https://docs.cloud.google.com/architecture/blueprints/security-foundations
- Google Cloud IAM documentation : https://cloud.google.com/iam/docs
- Google Cloud Audit Logs : https://cloud.google.com/logging/docs/audit
- CISA Cloud Security Technical Reference Architecture : https://www.cisa.gov/topics/cybersecurity-best-practices/executive-order-improving-nations-cybersecurity

Les consoles et services cloud évoluent ; certaines fonctionnalités varient selon la région, l’édition, le niveau de licence ou le type de ressource. Avant de déployer un contrôle, vérifiez la documentation officielle courante, la portée de la fonction, les coûts et les événements réellement collectés. Dans un environnement réel, reliez chaque exigence à un test, à une preuve et à un propriétaire responsable.

Fin du cours.