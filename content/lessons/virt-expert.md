# Cloud Privé et Infogérance

## Niveau Expert

## 1. Présentation générale du cours

La virtualisation permet de faire fonctionner plusieurs machines virtuelles sur un même ensemble de serveurs physiques. Cependant, disposer d’un cluster d’hyperviseurs ne signifie pas nécessairement que l’on possède un cloud privé.

Un cloud privé mature doit fournir des ressources informatiques sous forme de services standardisés, avec des mécanismes d’allocation, d’isolation, d’automatisation, de supervision, de sécurité, de facturation interne et de gestion des incidents.

L’infogérance ajoute une dimension opérationnelle et contractuelle : une équipe ou un prestataire s’engage à administrer, maintenir, surveiller et faire évoluer tout ou partie de cette plateforme selon des responsabilités et des niveaux de service définis.

Ce cours aborde donc trois dimensions complémentaires :

- **Infrastructure et architecture** : compute, stockage, réseau, haute disponibilité, reprise après sinistre.
- **Plateforme cloud** : multi-tenant, catalogue de services, libre-service, API, orchestration et Infrastructure as Code.
- **Exploitation et infogérance** : supervision, incidents, changements, capacité, sécurité, SLA, continuité d’activité et gouvernance.

Le fil conducteur sera la conception d’un cloud privé destiné à plusieurs clients internes ou externes, avec des exigences de disponibilité, de sécurité et d’exploitabilité.

## 2. Objectifs pédagogiques

À la fin du parcours, l’apprenant doit être capable de :

1. Concevoir une architecture de cloud privé adaptée à une organisation.
2. Distinguer une infrastructure virtualisée d’une véritable plateforme de cloud.
3. Définir une architecture multi-tenant avec des limites d’accès et de consommation.
4. Organiser les ressources de calcul, de stockage et de réseau autour d’un catalogue de services.
5. Automatiser la création et le cycle de vie des ressources.
6. Construire une chaîne de déploiement reproductible avec Git, OpenTofu ou Terraform et Ansible.
7. Concevoir une stratégie de haute disponibilité et de reprise après sinistre.
8. Mettre en place une supervision orientée services.
9. Définir des indicateurs SLI, des objectifs SLO et des engagements SLA.
10. Organiser les processus d’incident, de changement, de problème et de demande de service.
11. Formaliser une offre d’infogérance avec une matrice de responsabilités.
12. Piloter les coûts, la capacité, les risques et la qualité du service.
13. Diagnostiquer des incidents complexes dans une plateforme multi-tenant.
14. Concevoir et défendre un projet de cloud privé exploitable en production.

## 3. Prérequis

Ce cours suppose que l’apprenant maîtrise déjà les notions suivantes :

- Hyperviseurs et machines virtuelles.
- Gestion du cycle de vie des VM.
- Allocation CPU et mémoire.
- Stockage local et partagé.
- Réseaux virtuels, bridges, VLAN et routage.
- Sauvegardes et restaurations.
- Templates, clones et snapshots.
- Principes de clustering et de migration des machines virtuelles.
- Administration Linux et notions de réseau TCP/IP.
- Bases de l’automatisation système.

Les exemples utiliseront principalement OpenStack, Proxmox VE, KVM/libvirt, Ceph, OpenTofu ou Terraform, Ansible et Prometheus.

Ces technologies ne sont pas interchangeables dans tous les contextes. Chaque commande doit être adaptée à la distribution, à la version, aux droits disponibles et à l’architecture réellement déployée.

## 4. Comprendre ce qu'est réellement un cloud privé

### 4.1 Infrastructure virtualisée ou cloud privé ?

Une infrastructure virtualisée peut être entièrement administrée manuellement. Un technicien se connecte à l’hyperviseur, crée une VM, configure son réseau, lui attribue du stockage et transmet les informations au demandeur.

Cette méthode fonctionne pour un petit parc, mais elle devient difficile à industrialiser lorsque plusieurs équipes consomment des centaines de ressources.

Un cloud privé ajoute une couche de services et de gouvernance.

| Fonctionnalité | Virtualisation classique | Cloud privé industrialisé |
|---|---|---|
| Création d’une VM | Intervention administrative fréquente | Demande via catalogue ou API |
| Gestion des utilisateurs | Comptes hyperviseur ou outils locaux | Identités, rôles et périmètres |
| Allocation des ressources | Décision manuelle | Quotas, politiques et placement |
| Réseau | Bridges, VLAN et configuration manuelle | Réseaux virtuels provisionnés par API |
| Stockage | Datastores et volumes administrés séparément | Classes de stockage et demandes standardisées |
| Automatisation | Scripts ponctuels | Infrastructure as Code et workflows |
| Supervision | Métriques des hyperviseurs | Indicateurs techniques et indicateurs de service |
| Coûts | Inventaire de capacité | Allocation et imputation des coûts |
| Cycle de vie | Procédures variables | Workflow reproductible avec contrôles |
| Gouvernance | Dépend de l’équipe | Politiques formalisées et auditables |

Le cloud privé ne se résume donc pas à installer un portail Web devant des hyperviseurs. Il faut rendre la consommation des ressources prévisible, sécurisée et répétable.

### 4.2 Les caractéristiques d'un cloud privé mature

Un cloud privé professionnel possède généralement les caractéristiques suivantes :

**Libre-service contrôlé :** les utilisateurs peuvent demander des ressources autorisées sans devenir administrateurs de la plateforme.

**Mutualisation :** les ressources physiques sont partagées entre plusieurs consommateurs, sans supprimer les frontières de sécurité.

**Provisionnement automatisé :** la création et la suppression d’une ressource suivent un processus documenté.

**Mesure de consommation :** les ressources sont inventoriées et leur utilisation peut être imputée à un service ou à un client.

**Élasticité contrôlée :** la capacité d’un service peut évoluer selon des limites et des règles définies.

**Résilience :** les défaillances prévues sont traitées selon des mécanismes de détection, de bascule, de restauration ou de reconstruction.

**Observabilité :** l’équipe peut déterminer si le service fonctionne et identifier les causes probables d’une dégradation.

**Sécurité et traçabilité :** les accès, les opérations sensibles et les changements sont contrôlés et enregistrés.

### 4.3 Schéma d'ensemble

```text
                     UTILISATEURS ET CLIENTS
                               |
                 +-------------+-------------+
                 |                           |
             Portail Web                 API / CLI
                 |                           |
                 +-------------+-------------+
                               |
                    IDENTITE ET AUTORISATION
                     SSO / MFA / RBAC / IAM
                               |
                    CATALOGUE DE SERVICES
                               |
                  ORCHESTRATION ET POLITIQUES
                  Workflow / Quotas / Validation
                               |
                   PLATEFORME DE CLOUD PRIVE
              +----------------+----------------+
              |                |                |
         Calcul / VM        Réseau            Stockage
              |                |                |
           Hyperviseurs    VLAN / VXLAN     Volumes / Objets
              |                |                |
              +----------------+----------------+
                               |
                  INFRASTRUCTURE PHYSIQUE
                  Serveurs / Switches / Disques
                               |
              +----------------+----------------+
              |                |                |
          Supervision       Sauvegardes      Sécurité
          Logs / Alertes    PRA / Tests      Audit / SIEM
                               |
                     CENTRE D'EXPLOITATION
                  ITSM / Incidents / Changements
                     SLA / Capacité / Finances
```

Chaque couche doit avoir des interfaces claires et des responsabilités connues.

Le portail ne doit pas contourner les contrôles de la plateforme. Le système d’automatisation ne doit pas stocker les secrets en clair. La supervision ne doit pas dépendre exclusivement du service qu’elle surveille.

## 5. Choisir le modèle technologique

### 5.1 Proxmox VE et KVM/libvirt

Proxmox VE offre une plateforme de virtualisation avec gestion des clusters, des machines virtuelles, des conteneurs, du stockage, du réseau, des sauvegardes et des contrôles d’accès.

KVM/libvirt fournit les briques nécessaires à la gestion de machines virtuelles Linux. Il est possible de construire une plateforme autour de ces briques, mais il faut alors concevoir soi-même une partie de la couche de service : catalogue, orchestration, identité, automatisation, facturation ou interface libre-service.

Ce choix est intéressant lorsque l’objectif principal est une plateforme de virtualisation administrable, avec un niveau raisonnable de complexité opérationnelle.

### 5.2 OpenStack

OpenStack est une plateforme cloud composée de services spécialisés.

| Service | Fonction principale |
|---|---|
| Keystone | Identité, authentification et autorisation |
| Nova | Cycle de vie des instances de calcul |
| Placement | Inventaire et allocation des ressources |
| Neutron | Réseaux, ports, routeurs et connectivité virtuelle |
| Glance | Images de machines |
| Cinder | Stockage bloc |
| Swift | Stockage objet |
| Manila | Partages de fichiers |
| Horizon | Interface Web |
| Heat | Orchestration de ressources par modèles |
| Barbican | Gestion de secrets et de clés |
| Octavia | Services d'équilibrage de charge |
| Ceilometer | Collecte de mesures de consommation et de télémétrie |

La liste exacte des services déployés dépend du besoin. Il ne faut pas installer chaque service simplement parce qu’il existe.

OpenStack est adapté aux environnements nécessitant une plateforme cloud complète, des API, une séparation des projets et une orchestration avancée. En contrepartie, son exploitation exige une véritable compétence sur l’architecture distribuée, les mises à jour, les dépendances et le diagnostic des services.

### 5.3 Comparaison des approches

| Critère | Proxmox/KVM administré | OpenStack |
|---|---|---|
| Complexité initiale | Faible à moyenne | Moyenne à élevée |
| Gestion des VM | Native | Native via Nova |
| Libre-service multi-tenant avancé | À construire ou intégrer | Fonctions cloud natives |
| API et automatisation | Disponibles | Élément central de la plateforme |
| Réseau cloud complexe | Dépend de la conception et des composants intégrés | Modèle cloud avec Neutron |
| Exploitation | Plus simple dans un petit environnement | Plus exigeante à grande échelle |
| Cas d'utilisation | Infrastructure virtualisée industrialisée | Plateforme IaaS à grande échelle ou multi-projets |

Il faut valider les exigences avant de choisir. La taille du parc ne suffit pas : une petite plateforme pour plusieurs clients fortement isolés peut être plus exigeante qu’un grand cluster dédié à une seule équipe.

### 5.4 Architecture de référence retenue pour le projet

Le projet de ce cours retiendra le modèle suivant :

- Plateforme IaaS basée sur OpenStack pour le libre-service et la gestion multi-tenant.
- Ceph pour le stockage distribué lorsque les exigences de résilience et les moyens d’exploitation le justifient.
- OpenTofu ou Terraform pour décrire les ressources et leurs dépendances.
- Ansible pour configurer les systèmes invités et les composants administrables par configuration.
- Prometheus et Alertmanager pour la supervision métrique et les alertes.
- OpenTelemetry pour la collecte des traces, métriques et journaux applicatifs lorsqu’il est pertinent.
- Un outil ITSM pour les demandes, incidents, problèmes et changements.
- Un système de sauvegarde distinct du stockage de production.

Cette sélection est une architecture pédagogique, pas une obligation universelle. Une plateforme plus simple peut reprendre les mêmes principes avec Proxmox VE, une API et un catalogue automatisé.

## 6. Concevoir une architecture physique résiliente

### 6.1 Séparer les domaines de panne

Un cloud privé ne doit pas dépendre d’un serveur unique pour l’ensemble de ses fonctions critiques.

Il faut identifier au minimum :

- Les serveurs de calcul.
- Les contrôleurs ou services de gestion.
- Les nœuds de stockage.
- Les commutateurs réseau.
- Les équipements d’alimentation.
- Les accès d’administration.
- Les dépôts de sauvegarde.
- Les systèmes d’identité, DNS et NTP.
- Les mécanismes d’accès distant et de supervision.

Une redondance réelle exige que les composants redondants ne partagent pas tous le même point de défaillance.

Deux serveurs reliés au même commutateur unique ne fournissent pas une résilience complète contre une panne de ce commutateur.

### 6.2 Exemple de topologie physique

```text
                    RESEAU EXTERNE / CLIENTS
                              |
                     +--------+--------+
                     |                 |
                  FW-ACTIF          FW-SECOURS
                     |                 |
                 +---+-----------------+---+
                 |  COUCHE RESEAU REDONDANTE |
                 |    SWITCH-A / SWITCH-B    |
                 +----+----------+----------+
                      |          |
             +--------+          +--------+
             |                            |
       CLUSTER CALCUL                CLUSTER STOCKAGE
       +------------+                +--------------+
       | Compute-01 |                | Storage-01   |
       | Compute-02 |                | Storage-02   |
       | Compute-03 |                | Storage-03   |
       | Compute-04 |                | Storage-04   |
       +------------+                +--------------+
             |                            |
             +--------------+-------------+
                            |
                 RESEAU ADMINISTRATION
                            |
                 +----------+----------+
                 |                     |
            Supervision          Sauvegardes
                 |                     |
             Alertmanager          Dépôt isolé
```

Le nombre de nœuds affiché est illustratif. Il ne constitue pas une recommandation de dimensionnement applicable à toutes les charges.

### 6.3 Séparer les réseaux

Dans un environnement de production, on distingue généralement plusieurs plans réseau :

| Réseau | Fonction | Contrôles attendus |
|---|---|---|
| Administration | SSH, API d'administration, gestion des hôtes | Accès restreint, MFA en amont, journalisation |
| Services de contrôle | Communications entre composants cloud | Filtrage, segmentation, ports documentés |
| Stockage | Réplication et accès aux données | Débit, latence et disponibilité maîtrisés |
| Migration | Déplacement de VM ou de mémoire | Réseau isolé, permissions spécifiques |
| Management des VM | Accès d'administration des systèmes invités | Bastion, segmentation par client |
| Trafic applicatif | Flux des applications hébergées | Pare-feu et politiques par service |
| Sauvegarde | Transfert et restauration des données | Identités dédiées, chemin contrôlé |

La séparation peut être logique ou physique selon le risque, la capacité et le budget.

Un VLAN seul n’est pas une garantie absolue d’isolation. La conception doit aussi prendre en compte le routage, les listes de contrôle d’accès, les pare-feu, la gestion du plan d’administration et les possibilités de contournement.

### 6.4 Disponibilité du plan de contrôle

Le plan de contrôle regroupe les fonctions qui créent, modifient, surveillent et suppriment les ressources.

Dans OpenStack, une panne de Nova API, Keystone, de la base de données ou du système de messagerie peut empêcher certaines opérations de gestion même si des VM existantes continuent à fonctionner.

Il faut distinguer :

- La disponibilité du plan de contrôle.
- La disponibilité du plan de données.
- La disponibilité du réseau de gestion.
- La disponibilité des applications hébergées.

Une plateforme peut présenter une API indisponible alors que certaines VM continuent à répondre. À l’inverse, une API opérationnelle ne garantit pas que les applications des clients fonctionnent.

## 7. Concevoir une plateforme multi-tenant

### 7.1 Définition

Un tenant représente une frontière logique d’administration, de consommation et de ressources. Selon la technologie, il peut s’appuyer sur un projet, une organisation, un compte ou un espace de ressources.

Le multi-tenant permet d’héberger plusieurs consommateurs sur une même infrastructure physique tout en appliquant des règles d’accès et de séparation.

Les frontières de sécurité ne doivent pas reposer uniquement sur les noms des VM ou sur des conventions de nommage.

### 7.2 Organisation logique

```text
                    CLOUD PRIVE
                        |
          +-------------+-------------+
          |             |             |
       CLIENT-A       CLIENT-B       CLIENT-C
          |             |             |
       Projet-A       Projet-B       Projet-C
          |             |             |
      +---+---+      +---+---+      +---+---+
      |       |      |       |      |       |
    WEB-A   DB-A   WEB-B   DB-B   APP-C   DB-C
      |       |      |       |      |       |
      +-------+      +-------+      +-------+
          |             |             |
       Réseau-A      Réseau-B      Réseau-C
```

Chaque client doit avoir une identité, un périmètre d’administration et des ressources qui lui sont attribuées explicitement.

### 7.3 Les mécanismes d'isolation

Une séparation complète implique plusieurs niveaux :

1. **Identité** : un utilisateur du client A ne doit pas administrer les ressources du client B.
2. **API** : les appels doivent être autorisés selon le projet et le rôle.
3. **Réseau** : les ressources réseau privées ne doivent pas permettre des accès non autorisés entre clients.
4. **Stockage** : les volumes, snapshots, images privées et sauvegardes doivent être protégés contre l’accès inter-tenant.
5. **Calcul** : les VM ne doivent pas pouvoir accéder à la mémoire ou aux données d’un autre tenant.
6. **Journaux** : un client ne doit pas consulter les événements contenant les informations confidentielles d’un autre.
7. **Sauvegarde** : les droits de restauration et de consultation doivent suivre les mêmes exigences de confidentialité.
8. **Facturation** : les coûts et les consommations ne doivent pas être mélangés.

Une isolation logique dans un environnement partagé reste différente d’une isolation physique dédiée. Les environnements soumis à des contraintes réglementaires ou à un risque élevé peuvent exiger des mesures supplémentaires.

### 7.4 OpenStack : projets, domaines, utilisateurs et rôles

Dans OpenStack, Keystone fournit des mécanismes d’identité et d'autorisation. Un domaine peut regrouper des identités et des projets ; un projet représente généralement un périmètre de ressources.

Les rôles déterminent ce qu’un utilisateur peut faire dans le périmètre où ces rôles lui sont attribués.

Exemple conceptuel :

```text
Domaine : clients
|
+-- Projet : client-a-production
|   +-- Utilisateur : ops-a
|   +-- Rôle : membre du projet
|
+-- Projet : client-b-production
|   +-- Utilisateur : ops-b
|   +-- Rôle : membre du projet
|
+-- Projet : infogerance
    +-- Utilisateur : plateforme-admin
    +-- Rôle : administrateur autorisé selon la politique
```

Les rôles effectivement disponibles, leur portée et leur comportement dépendent de la politique de la version déployée.

Il faut éviter de donner systématiquement des privilèges administrateur globaux au personnel d’exploitation ou aux comptes d’automatisation.

### 7.5 Exemple d'administration avec OpenStack CLI

Les commandes suivantes illustrent la création d’un projet et d’un utilisateur. Elles nécessitent une identité disposant des privilèges correspondants.

```bash
# Créer un projet pour un client
openstack project create \
  --domain clients \
  client-a-production

# Créer un utilisateur de service
openstack user create \
  --domain clients \
  --password-prompt \
  automation-client-a

# Vérifier le projet
openstack project show client-a-production

# Examiner les rôles disponibles
openstack role list
```

L’attribution du rôle doit respecter la politique de l’organisation. Par exemple, un rôle de membre du projet peut être adapté à un opérateur client, tandis qu’un compte de plateforme nécessite des permissions distinctes.

Ne placez pas de mot de passe dans l’historique du terminal, dans le dépôt Git ou dans une documentation partagée.

### 7.6 Vérifier l'isolation

Une recette multi-tenant doit inclure des tests négatifs, pas uniquement des tests fonctionnels.

Exemples de vérifications :

- Un utilisateur A peut lire ses instances.
- Un utilisateur A ne peut pas modifier une instance B.
- Un utilisateur A ne peut pas lire les volumes privés B.
- Une VM A ne peut pas joindre un réseau B sans règle explicite.
- Un tenant ne peut pas créer des ressources au-delà de son quota.
- Les journaux visibles par un client ne contiennent pas les secrets d’un autre.
- Les sauvegardes et les autorisations de restauration respectent la séparation.

Le test doit être effectué avec des comptes représentatifs de chaque rôle. Un test exécuté avec un compte administrateur global ne prouve pas que les permissions d’un client sont correctes.

## 8. Concevoir un catalogue de services cloud

### 8.1 Pourquoi utiliser un catalogue ?

Sans catalogue, chaque demande peut devenir un projet spécifique avec ses propres conventions et ses propres scripts.

Un catalogue définit des offres reproductibles, avec des paramètres contrôlés et des engagements explicites.

Exemple :

| Offre | Ressources indicatives | Usage |
|---|---|---|
| VM-S1 | 1 vCPU, 2 Go RAM, 30 Go | Service léger |
| VM-S2 | 2 vCPU, 4 Go RAM, 60 Go | Application standard |
| VM-M1 | 4 vCPU, 8 Go RAM, 100 Go | Application métier |
| VM-M2 | 8 vCPU, 16 Go RAM, 200 Go | Service exigeant |
| DB-HA | Calcul, volumes et architecture spécifiques | Base de données à haute disponibilité |
| ENV-DEV | Ressources limitées, données non sensibles | Environnement de développement |
| ENV-PROD | Contrôles renforcés, sauvegarde et supervision | Production |

Ces valeurs sont des exemples de catalogue. Une offre réelle doit être validée selon la capacité, les profils de charge et les objectifs de service.

### 8.2 Une offre doit définir plus que les ressources

Chaque offre doit préciser :

- Le nombre de vCPU et la politique de partage CPU.
- La quantité de mémoire et les éventuelles réservations.
- Le type, la capacité et les performances attendues du stockage.
- Les réseaux autorisés.
- La méthode d’accès administratif.
- Les sauvegardes incluses.
- La durée de conservation des sauvegardes.
- Les objectifs de disponibilité.
- Les limites de capacité.
- Les options de supervision.
- La répartition des responsabilités entre client et infogérant.
- Le coût et les règles de facturation.
- La procédure de changement et de retrait du service.

Il est dangereux de vendre une « VM haute performance » sans définir ce que cette expression signifie en termes mesurables.

### 8.3 Workflow de provisionnement

```text
[Demande utilisateur]
         |
         v
[Authentification]
         |
         v
[Vérification du rôle]
         |
         v
[Validation du catalogue]
         |
         v
[Contrôle du quota]
         |
         v
[Contrôle de capacité]
         |
         v
[Création des ressources]
         |
         v
[Configuration du système]
         |
         v
[Contrôles de sécurité]
         |
         v
[Enregistrement CMDB]
         |
         v
[Activation supervision et sauvegarde]
         |
         v
[Notification / Mise à disposition]
```

Le workflow doit être capable de signaler un échec, d’identifier les ressources déjà créées et de reprendre ou d’annuler proprement l’opération.

### 8.4 Gestion de la suppression

La suppression est une opération de cycle de vie à part entière.

Avant de supprimer une ressource de production, le processus doit vérifier :

1. La demande de suppression est autorisée.
2. Le propriétaire et l’impact sont identifiés.
3. La politique de conservation des données est respectée.
4. Une sauvegarde est nécessaire ou non selon la politique.
5. Les dépendances sont identifiées : DNS, volumes, IP, règles réseau, certificats et supervision.
6. Les données devant être conservées sont archivées.
7. Les ressources supprimées sont retirées de l’inventaire.
8. Les consommations et les coûts sont clôturés.

Une suppression réussie ne signifie pas nécessairement qu’il faut détruire immédiatement toutes les sauvegardes : les règles de conservation peuvent imposer une durée de rétention distincte.

## 9. Quotas, réservations et gouvernance des ressources

### 9.1 Pourquoi les quotas sont nécessaires

Un utilisateur disposant d’une API de création de VM pourrait, sans limites, consommer toute la capacité partagée.

Les quotas rendent la consommation contrôlable.

Ils peuvent porter sur :

- Le nombre d’instances.
- Les vCPU.
- La mémoire.
- Les volumes.
- La capacité de stockage.
- Le nombre de réseaux.
- Le nombre de ports.
- Les adresses IP flottantes ou publiques.
- Les snapshots.
- Les ressources de sécurité.
- Les services ou fonctionnalités coûteux.

Les quotas ne doivent pas être confondus avec la capacité physique réellement disponible.

### 9.2 Exemple de calcul de capacité

Une plateforme possède quatre hyperviseurs avec chacun :

- 32 cœurs physiques.
- 256 Go de RAM.
- 3 To de stockage local, non destiné à héberger les données principales des VM.

Capacité nominale :

```text
CPU nominal :
4 x 32 = 128 cœurs physiques

Mémoire nominale :
4 x 256 Go = 1 024 Go RAM
```

Supposons que l’on souhaite tolérer la perte d’un hyperviseur et réserver 20 % de la capacité de calcul restante à l’exploitation, à la variabilité de charge et aux tâches système.

CPU de planification :

```text
Capacité physique totale              = 128 cœurs
Capacité après perte d'un nœud        =  96 cœurs
Marge d'exploitation de 20 %          =  19,2 cœurs
Capacité indicative de planification  =  76,8 cœurs
```

Pour la mémoire, avec une marge de 15 % appliquée aux 768 Go restants :

```text
Mémoire physique après perte d'un nœud = 768 Go
Marge de 15 %                          = 115,2 Go
Capacité indicative de planification   = 652,8 Go
```

Cette estimation n’intègre pas encore les réservations précises de l’hyperviseur, les contraintes NUMA, les profils de charge ni les éventuelles limitations du stockage. Elle sert de point de départ, pas de garantie de capacité.

### 9.3 Surallocation CPU

La surallocation CPU permet de faire fonctionner plus de vCPU que de cœurs physiques.

Un ratio de 4:1 signifie que quatre vCPU sont provisionnés pour un cœur physique.

Ce ratio ne garantit pas que chaque vCPU recevra une performance constante. Son acceptabilité dépend notamment :

- Du type de charge.
- Du niveau de simultanéité.
- Du temps d’attente CPU.
- Des pics d’activité.
- De l’importance des latences.
- De la capacité restante lors de la panne d’un hôte.

Il est préférable de mesurer la contention et de fixer des limites par classe de service plutôt que d’appliquer un ratio uniforme à toutes les applications.

### 9.4 Surallocation mémoire

La surallocation mémoire est plus risquée lorsqu’elle repose sur l’hypothèse que les VM n’utiliseront jamais toute la mémoire qui leur est attribuée.

Il faut prendre en compte :

- La mémoire réellement consommée.
- Les réservations et limites configurées.
- L’activité du noyau de l’hyperviseur.
- Les mécanismes de ballooning.
- Le swap, le cas échéant.
- Les pics simultanés de consommation.
- Le risque d'épuisement mémoire et de terminaison de processus.

Une plateforme de production ne doit pas compter exclusivement sur le swap pour assurer sa capacité de service.

### 9.5 Quota par client et capacité globale

Exemple de politique :

```text
Client A :
  vCPU autorisés      : 64
  RAM autorisée       : 256 Go
  Volumes autorisés   : 2 To
  Instances maximum   : 50

Client B :
  vCPU autorisés      : 32
  RAM autorisée       : 128 Go
  Volumes autorisés   : 1 To
  Instances maximum   : 25
```

Les quotas ne constituent pas forcément des réservations physiques.

Deux clients peuvent avoir des quotas cumulés supérieurs à la capacité disponible si la plateforme applique une politique de surallocation. Cela oblige à distinguer :

- Le quota accordé.
- Les ressources réellement consommées.
- Les ressources réservées.
- La capacité disponible.
- La capacité garantie après une panne.

La politique de capacité doit documenter chacune de ces notions.

## 10. Réseau cloud : conception et isolation

### 10.1 Réseau virtuel de tenant

Dans un cloud, les consommateurs doivent pouvoir disposer de réseaux privés indépendants, même si leurs adresses IP se chevauchent.

Exemple :

```text
CLIENT-A
Réseau : 10.10.0.0/24
  WEB-A : 10.10.0.10
  DB-A  : 10.10.0.20

CLIENT-B
Réseau : 10.10.0.0/24
  WEB-B : 10.10.0.10
  DB-B  : 10.10.0.20
```

Le chevauchement des adresses est possible si l’architecture assure correctement l’isolation et le routage des réseaux virtuels. Une connexion entre ces réseaux exige un mécanisme explicite de communication ou de traduction.

Dans OpenStack, Neutron gère les réseaux et ports virtuels, les sous-réseaux, les routeurs, les groupes de sécurité et les mécanismes de connectivité, selon le pilote réseau utilisé.

### 10.2 Flux réseau de référence

```text
               INTERNET / WAN
                      |
               [Pare-feu périmétrique]
                      |
                [Réseau public]
                      |
              [Routeur du tenant]
                      |
                  [Réseau privé]
                      |
                +-----+-----+
                |           |
             [WEB-01]     [WEB-02]
                |           |
                +-----+-----+
                      |
                [Réseau applicatif]
                      |
                  [API / APP]
                      |
                 [Réseau DB]
                      |
                   [DB-01]
```

La base de données ne doit pas être exposée directement à Internet simplement parce qu’une machine virtuelle est présente sur le même cluster.

### 10.3 Principes de filtrage

Définir une politique réseau à partir des besoins applicatifs :

- Autoriser uniquement les flux nécessaires.
- Appliquer une règle d’entrée explicite aux services exposés.
- Limiter les ports d’administration aux bastions ou réseaux autorisés.
- Empêcher les communications entre tenants qui ne sont pas nécessaires.
- Documenter les exceptions.
- Tester les règles avec les identités et réseaux concernés.
- Supprimer les règles devenues inutiles.

Exemple conceptuel :

```text
Internet -> Reverse proxy :
  Autoriser TCP/443

Reverse proxy -> Application :
  Autoriser TCP/8443

Application -> Base de données :
  Autoriser TCP/5432

Poste d'administration -> Bastion :
  Autoriser TCP/22 ou accès distant contrôlé

Internet -> Base de données :
  REFUSER
```

Les ports illustrés dépendent des applications. Ils ne constituent pas une configuration universelle.

### 10.4 Groupes de sécurité OpenStack

Exemple de création d’un groupe de sécurité :

```bash
openstack security group create web-https
```

Exemple de règle autorisant HTTPS :

```bash
openstack security group rule create \
  --ingress \
  --protocol tcp \
  --dst-port 443 \
  web-https
```

Exemple de consultation :

```bash
openstack security group show web-https
openstack security group rule list web-https
```

La manière dont les règles sont appliquées dépend du pilote Neutron. Il faut aussi contrôler les règles de sortie, le routage, les groupes attachés aux ports et les éventuels pare-feu externes.

### 10.5 Diagnostic réseau

En présence d’un problème d’accès, avancer du niveau le plus proche de la source vers la destination.

```text
1. VM démarrée ?
       |
2. Interface et adresse IP correctes ?
       |
3. Passerelle accessible ?
       |
4. Route présente ?
       |
5. Règles de sécurité correctes ?
       |
6. Pare-feu intermédiaire autorisant le flux ?
       |
7. Service en écoute ?
       |
8. Réponse et routage retour corrects ?
```

Commandes Linux utiles :

```bash
ip -br address
ip route
ip neigh
ping -c 4 <adresse>
tracepath <adresse>
ss -lntup
sudo nft list ruleset
```

`ping` peut être bloqué alors que le service fonctionne ; inversement, une réponse ICMP ne prouve pas qu’un port applicatif est accessible.

## 11. Stockage distribué et Ceph

### 11.1 Pourquoi utiliser du stockage distribué ?

Le stockage distribué vise à rendre les données accessibles malgré certaines défaillances de disques, d’hôtes ou de chemins réseau.

Ceph fournit plusieurs interfaces de stockage :

- RADOS : couche fondamentale de stockage objet distribué.
- RBD : stockage bloc, notamment pour les disques de VM.
- CephFS : système de fichiers distribué.
- RADOS Gateway : interface de stockage objet compatible avec des API de type S3 selon la configuration.

Le choix d’un stockage distribué ajoute de la résilience et de la flexibilité, mais augmente les exigences en matière de réseau, de supervision, de capacité et de maintenance.

### 11.2 Architecture simplifiée de Ceph

```text
                HYPERVISEURS / CLIENTS
                         |
               +---------+---------+
               |                   |
             RBD                CephFS / RGW
               |                   |
               +---------+---------+
                         |
                     RADOS
                         |
              +----------+----------+
              |          |          |
           MON-A       MON-B      MON-C
              |          |          |
              +----------+----------+
                         |
               CRUSH / Placement
                         |
            +------------+------------+
            |            |            |
          OSD-A        OSD-B        OSD-C
            |            |            |
          Disques      Disques      Disques
```

Les MON maintiennent notamment l’état du cluster et le quorum. Les OSD stockent les données et participent aux opérations de réplication ou de reconstruction. L’architecture exacte varie en fonction de la version et des fonctionnalités activées.

### 11.3 La réplication a un coût

Supposons un ensemble de disques contenant au total 30 To bruts.

Avec une réplication de trois copies, la capacité théorique maximale avant les réserves opérationnelles est :

```text
30 To bruts / 3 = 10 To de données utiles
```

Cette estimation est simplifiée. Il faut ensuite tenir compte de la capacité non remplie, des métadonnées, des choix de placement, des déséquilibres entre OSD, des marges de récupération et des politiques propres aux pools.

L’espace réellement utilisable doit être calculé selon la politique de réplication ou d’erasure coding retenue.

### 11.4 Résilience et domaines de panne

Une réplication répartie sur plusieurs disques d’un même serveur ne protège pas contre la perte complète du serveur.

Pour obtenir la résilience attendue, il faut définir les domaines de placement : disque, hôte, baie, rack ou autre domaine de panne pris en charge par la conception.

Une configuration conçue pour survivre à la perte d’un hôte doit disposer d’assez de capacité et de domaines indépendants pour respecter cette exigence.

### 11.5 Vérifications de base

Sur une plateforme Ceph disposant de la CLI et des autorisations appropriées :

```bash
ceph -s
ceph health detail
ceph osd tree
ceph df
ceph osd df
```

Ces commandes donnent une vue générale de l’état du cluster, de l’utilisation de capacité et de la répartition des OSD.

Elles ne suffisent pas à garantir la cohérence des sauvegardes ni les performances d’une application.

### 11.6 Diagnostic d'un cluster en santé dégradée

```text
Alerte : état HEALTH_WARN ou HEALTH_ERR
                  |
                  v
         Lire les détails de santé
                  |
                  v
       Identifier PG, OSD ou MON concernés
                  |
                  v
     Vérifier disponibilité et placement des OSD
                  |
                  v
       Vérifier réseau et saturation disque
                  |
                  v
       Estimer l'effet de la récupération
                  |
                  v
    Appliquer le runbook adapté et contrôler
```

Ne redémarrez pas tous les OSD ou ne changez pas la politique de réplication sans analyser l’état du cluster. Une intervention précipitée peut aggraver une situation déjà dégradée.

### 11.7 Stockage de production et sauvegarde

Un stockage distribué avec plusieurs copies n’est pas une sauvegarde.

Si un administrateur supprime les données, si un logiciel chiffre tous les fichiers ou si une application corrompt logiquement ses données, les mécanismes de réplication peuvent propager la corruption ou la suppression.

La sauvegarde doit donc être pensée comme un système indépendant de la haute disponibilité.

## 12. Infrastructure as Code

### 12.1 Pourquoi décrire l'infrastructure en code ?

L’Infrastructure as Code consiste à définir les ressources et leur état souhaité dans des fichiers versionnés.

Au lieu de créer chaque ressource manuellement, l’équipe utilise des descriptions reproductibles.

Les bénéfices recherchés sont :

- Réduction des opérations manuelles.
- Réutilisation de modèles.
- Contrôle des modifications.
- Revue par les pairs.
- Traçabilité des déploiements.
- Capacité à reconstruire un environnement.
- Standardisation des configurations.

Un fichier IaC n’est pas automatiquement sécurisé. Il doit être révisé, testé, protégé et intégré à une chaîne d’exécution gouvernée.

### 12.2 Infrastructure as Code et gestion de configuration

Ces deux approches répondent à des besoins différents.

| Besoin | Approche habituelle |
|---|---|
| Créer une machine virtuelle | OpenTofu/Terraform, API du cloud |
| Créer un réseau virtuel | OpenTofu/Terraform, API du cloud |
| Définir les ressources d’un projet | IaC et/ou orchestration cloud |
| Installer et configurer un serveur | Ansible |
| Déployer un fichier de configuration | Ansible ou outil équivalent |
| Configurer un service système | Ansible |
| Vérifier la conformité des hôtes | Outils de configuration et de contrôle |
| Gérer un changement complexe | Pipeline CI/CD avec approbations |

OpenTofu ou Terraform peuvent créer des ressources puis Ansible configurer le système d’exploitation invité. Les deux outils ne remplacent pas tous les contrôles de sécurité et de validation nécessaires.

### 12.3 Cycle de vie IaC

```text
[Demande]
    |
    v
[Modification des fichiers]
    |
    v
[Git : commit et revue]
    |
    v
[Contrôle syntaxique]
    |
    v
[Validation et tests]
    |
    v
[Plan de changements]
    |
    v
[Approbation selon le risque]
    |
    v
[Application contrôlée]
    |
    v
[Tests après déploiement]
    |
    v
[Inventaire et supervision mis à jour]
```

Une modification de production doit être évaluée selon son impact, pas uniquement selon le fait qu’elle provient d’un pipeline automatisé.

### 12.4 Exemple OpenTofu/Terraform : paramètres d'une VM

Les exemples suivants utilisent des noms et variables illustratifs. La création réelle d’une machine exige un fournisseur compatible, un réseau valide, une image, des identifiants et une configuration adaptée à l’environnement.

Exemple de variables :

```hcl
variable "instance_name" {
  description = "Nom logique de la machine"
  type        = string
}

variable "flavor_name" {
  description = "Profil de calcul autorisé"
  type        = string
}

variable "image_id" {
  description = "Identifiant de l'image validée"
  type        = string
}

variable "network_id" {
  description = "Identifiant du réseau du projet"
  type        = string
}
```

Exemple de ressource conceptuelle pour un fournisseur OpenStack :

```hcl
resource "openstack_compute_instance_v2" "application" {
  name      = var.instance_name
  flavor_id = var.flavor_name
  image_id  = var.image_id

  network {
    uuid = var.network_id
  }
}
```

Les versions du fournisseur peuvent différer sur les attributs et leurs types. Il faut consulter la documentation du fournisseur installé avant d’utiliser ce fragment en production.

### 12.5 Commandes de validation

Dans un répertoire initialisé avec la version d’OpenTofu ou Terraform retenue :

```bash
tofu fmt -check
tofu validate
tofu plan
```

Après revue du plan et validation selon les règles de changement, l’application peut être exécutée dans le contexte prévu :

```bash
tofu apply
```

N’appliquez jamais un plan non vérifié en production simplement parce que la commande a réussi dans un environnement de test.

### 12.6 État IaC et secrets

Le fichier d’état peut contenir des métadonnées sensibles, et certaines valeurs considérées comme secrètes peuvent aussi y apparaître.

Il doit être traité comme une donnée sensible.

Bonnes pratiques :

- Stockage distant adapté aux besoins de l’équipe.
- Contrôle d’accès strict.
- Verrouillage des opérations concurrentes lorsque le backend le prend en charge.
- Chiffrement au repos et en transit.
- Sauvegarde de l’état.
- Évitement du stockage de l’état dans Git.
- Protection des fichiers de plan.
- Politique de rotation des secrets.
- Séparation des états selon les périmètres d’administration.

Un fichier d’état perdu, écrasé ou partagé sans contrôle peut provoquer des dérives de configuration ou exposer des informations.

### 12.7 Idempotence et dérive

Une opération idempotente peut être répétée sans modifier indéfiniment le résultat recherché une fois l’état attendu atteint.

L’idempotence est importante pour les automatisations de configuration.

La dérive apparaît lorsque l’environnement réel change sans que cette modification soit représentée dans la source de vérité.

Exemple :

```text
État décrit dans Git
       |
       v
VM configurée par le pipeline
       |
       v
Technicien modifie manuellement SSH
       |
       v
Écart entre l'état déclaré et l'état réel
       |
       v
Audit / plan / contrôle de conformité
       |
       v
Correction approuvée
```

Une correction automatique peut être utile, mais elle peut également annuler une intervention d’urgence. Il faut définir comment la plateforme traite les modifications manuelles, les exceptions et les changements non planifiés.

## 13. Configuration automatisée avec Ansible

### 13.1 Pourquoi Ansible ?

Ansible permet de décrire les tâches d’administration et de configuration dans des playbooks. Il peut configurer des systèmes Linux et Windows, installer des logiciels, déployer des fichiers ou exécuter des opérations d’exploitation.

Dans un cloud privé, il peut intervenir après la création de la machine virtuelle pour appliquer une configuration standardisée.

### 13.2 Exemple d'inventaire

```ini
[web]
web-01 ansible_host=192.0.2.21
web-02 ansible_host=192.0.2.22

[database]
db-01 ansible_host=192.0.2.31

[production:children]
web
database
```

Les adresses `192.0.2.0/24` sont réservées à la documentation. Elles doivent être remplacées par des adresses appartenant à l’environnement réel.

### 13.3 Exemple de playbook

Le playbook suivant illustre l’installation d’un paquet et le démarrage d’un service sur Debian ou Ubuntu.

```yaml
---
- name: Configurer les serveurs Web
  hosts: web
  become: true
  gather_facts: true

  tasks:
    - name: Installer Nginx
      ansible.builtin.apt:
        name: nginx
        state: present
        update_cache: true

    - name: Activer et démarrer Nginx
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true
```

Exécution :

```bash
ansible-inventory -i inventory.ini --graph
ansible -i inventory.ini web -m ansible.builtin.ping
ansible-playbook -i inventory.ini configure-web.yml --check
ansible-playbook -i inventory.ini configure-web.yml
```

Le mode `--check` est utile, mais son exactitude dépend du module. Il ne garantit pas qu’aucun effet de bord ne se produira dans tous les cas.

### 13.4 Gestion de la configuration sensible

Il faut éviter de mettre des mots de passe ou des clés privées en clair dans les fichiers YAML.

Utiliser un système adapté à la gestion des secrets, par exemple Ansible Vault ou un gestionnaire externe compatible avec la politique de sécurité.

Il faut également protéger :

- Les clés SSH.
- Les identifiants d’API.
- Les certificats privés.
- Les jetons d’accès.
- Les variables sensibles.
- Les journaux des pipelines qui pourraient afficher des valeurs secrètes.

## 14. Construire une chaîne CI/CD pour l'infrastructure

### 14.1 Pourquoi une chaîne de déploiement ?

Une chaîne CI/CD d’infrastructure permet de contrôler les changements avant qu’ils ne modifient les ressources de production.

Elle doit inclure les vérifications adaptées au risque : syntaxe, validation, tests, politique, plan, approbation, déploiement et vérification du résultat.

### 14.2 Exemple de pipeline

```text
             Développeur / Ingénieur cloud
                           |
                           v
                    Dépôt Git
                           |
                           v
                Vérification automatique
                 +---------------------+
                 | Format / Syntaxe    |
                 | Lint / Validation  |
                 | Scan secrets       |
                 | Contrôles sécurité |
                 +---------------------+
                           |
                           v
                   Plan des changements
                           |
                           v
                   Revue par un pair
                           |
                           v
                Approbation de production
                           |
                           v
                Exécution par le runner
                           |
                           v
                Tests et contrôle d'état
                           |
                           v
                   Traces d'audit
```

### 14.3 Séparer les environnements

Ne réutilisez pas sans contrôle les mêmes identifiants d’administration, les mêmes états IaC et les mêmes règles de déploiement pour le développement et la production.

Il faut distinguer :

- Les environnements de test.
- Les environnements de préproduction.
- Les environnements de production.
- Les identités utilisées dans chaque environnement.
- Les états IaC et les ressources gérées.
- Les approbations et les règles de déploiement.

Les artefacts peuvent être promus d’un environnement à un autre, mais les secrets, les autorisations et les paramètres doivent être adaptés.

### 14.4 Stratégie de retour arrière

Le retour arrière d’une infrastructure n’est pas toujours équivalent à un retour arrière logiciel.

Une modification de VM peut être réversible. Une migration de format de disque, une suppression de données, une modification de schéma de base de données ou un changement de réseau peut être difficile à annuler.

Avant le changement, identifier :

- L’état initial.
- Les ressources impactées.
- Les dépendances.
- Le mécanisme de sauvegarde ou de restauration.
- La condition qui déclenche l’annulation.
- La procédure de retour arrière.
- Les conséquences si le retour arrière échoue.

## 15. Automatiser le provisionnement de bout en bout

### 15.1 Exemple de demande de VM

Prenons le cas d’un client qui demande une machine de production.

Les paramètres de la demande peuvent comprendre :

```text
Identité du demandeur
Client / tenant
Nom logique de la VM
Environnement : production
Profil : VM-M1
Image autorisée
Réseau autorisé
Clé d'accès ou méthode de gestion
Groupe de sécurité
Politique de sauvegarde
Fenêtre de maintenance
Propriétaire applicatif
Centre de coûts
```

Le demandeur ne doit pas pouvoir choisir arbitrairement un réseau d’administration ou une image non approuvée.

### 15.2 Contrôles avant création

Le moteur de provisionnement doit vérifier :

1. L’identité du demandeur.
2. Son autorisation à créer des ressources pour ce tenant.
3. La conformité des paramètres.
4. La disponibilité du quota.
5. La capacité du cluster.
6. L’existence de l’image et du réseau.
7. Les politiques de sécurité.
8. Le coût estimé.
9. L’approbation éventuelle pour la production.
10. Le respect des règles de nomenclature et d’inventaire.

### 15.3 Idempotence du workflow

Une demande peut être rejouée à la suite d’un timeout ou d’une interruption réseau.

Le système doit donc reconnaître la demande et identifier les ressources déjà créées.

```text
Demande : REQ-2026-00125
             |
             v
Recherche d'une exécution existante
             |
       +-----+-----+
       |           |
   Existe déjà   Nouvelle demande
       |           |
 Reprendre ou     Valider et
 rapprocher       provisionner
       |           |
       +-----+-----+
             |
             v
     Vérifier l'état réel
             |
             v
       Finaliser la demande
```

Une deuxième exécution ne doit pas créer automatiquement une deuxième VM identique simplement parce que la première réponse de l’API a été perdue.

### 15.4 Gestion des erreurs partielles

Une création de service peut échouer après avoir créé le réseau, le volume ou la VM.

Un mécanisme robuste doit enregistrer les étapes accomplies et leur résultat.

Il doit être capable de :

- Identifier les ressources créées.
- Réessayer une opération lorsque cela est sûr.
- Éviter les créations en double.
- Annuler ou compenser les étapes nécessaires.
- Signaler un échec non récupérable.
- Préserver les preuves de l’opération.

Les systèmes distribués ne garantissent pas qu’une opération multi-service se comporte comme une transaction atomique unique. Il faut concevoir explicitement la reprise et la compensation.

## 16. Haute disponibilité, capacité et domaines de panne

### 16.1 La haute disponibilité n'est pas une option unique

La haute disponibilité peut désigner plusieurs capacités :

- Maintenir une application malgré la panne d’un processus.
- Faire basculer un service réseau.
- Redémarrer une VM sur un autre hyperviseur.
- Répliquer des données sur plusieurs nœuds.
- Maintenir les API de gestion.
- Continuer à fournir le service malgré la perte d’un site.

Ces objectifs ne nécessitent pas tous les mêmes mécanismes.

### 16.2 Résilience à la panne d'un hyperviseur

```text
AVANT LA PANNE

Hôte-01          Hôte-02          Hôte-03
+--------+       +--------+       +--------+
| VM-A   |       | VM-C   |       | VM-E   |
| VM-B   |       | VM-D   |       | VM-F   |
+--------+       +--------+       +--------+


PANNE DE L'HÔTE-02

Hôte-01          Hôte-02          Hôte-03
+--------+       XXXXXXXXX        +--------+
| VM-A   |       X  PANNE X       | VM-E   |
| VM-B   |       XXXXXXXXX        | VM-F   |
+--------+                         +--------+
                                       |
                                       v
                              Reprise possible de
                              VM-C et VM-D ailleurs
```

La reprise est possible uniquement si l’architecture le permet : capacité disponible, accès aux données, réseau fonctionnel, mécanisme de détection, configuration compatible et politique HA activée.

La perte d’un hôte peut interrompre les VM concernées avant leur redémarrage sur une autre machine. Une HA de VM n’équivaut pas à une continuité applicative sans interruption.

### 16.3 Capacité en mode N+1

Le modèle N+1 prévoit qu’un composant supplémentaire ou une marge de capacité permet de continuer à fonctionner malgré la perte d’un composant.

Pour un cluster de quatre hôtes, le dimensionnement doit être examiné en mode dégradé :

- Les trois hôtes restants peuvent-ils héberger les VM prioritaires ?
- Le stockage peut-il servir les données pendant la reconstruction ?
- La bande passante restante suffit-elle ?
- Les migrations ou redémarrages peuvent-ils provoquer une congestion ?
- Les services de contrôle disposent-ils encore de leur quorum ?
- La reprise est-elle possible dans la durée contractuelle prévue ?

Un cluster qui fonctionne correctement en régime nominal peut échouer lors de la perte d’un hôte si les ressources sont trop fortement surallouées.

### 16.4 Choisir les services à protéger en priorité

Exemple de niveaux de criticité :

| Niveau | Exemple | Priorité |
|---|---|---|
| Critique | Identité centrale, base transactionnelle essentielle | Très élevée |
| Élevée | Application métier principale | Élevée |
| Standard | Application interne courante | Normale |
| Développement | Environnement de test | Faible selon le contrat |

Ces niveaux doivent être approuvés par le propriétaire du service. Ils déterminent les politiques de capacité, de sauvegarde, de surveillance, de maintenance et de reprise.

## 17. Sauvegarde, PRA et continuité d'activité

### 17.1 HA, sauvegarde et PRA répondent à des objectifs différents

La haute disponibilité limite les interruptions provoquées par certaines pannes.

La sauvegarde permet de retrouver des données ou un état antérieur après une suppression, une corruption ou une perte.

Le plan de reprise d’activité (PRA) décrit les procédures permettant de rétablir les services après un sinistre majeur.

Le plan de continuité d’activité (PCA) organise le maintien des activités essentielles pendant une perturbation.

Ces dispositifs sont complémentaires, pas substituables.

### 17.2 RPO et RTO

Le **RPO** (Recovery Point Objective) est la perte maximale de données acceptable exprimée en temps.

Le **RTO** (Recovery Time Objective) est le délai cible de rétablissement du service.

Exemple :

```text
Dernière sauvegarde valide : 02 h 00
Incident détecté           : 10 h 15
```

Si une restauration repose uniquement sur cette sauvegarde et que les données générées après 02 h 00 ne sont pas récupérables autrement, la perte potentielle peut dépasser huit heures.

Il ne faut pas confondre le RPO contractuel avec la fréquence planifiée des sauvegardes. La politique doit tenir compte du moment réel de la dernière sauvegarde valide, de sa cohérence et de la disponibilité des journaux ou mécanismes de réplication complémentaires.

### 17.3 Exemple de matrice de sauvegarde

| Classe | Exemple | Fréquence indicative | Conservation indicative |
|---|---|---|---|
| A | Données transactionnelles critiques | Selon RPO, sauvegardes fréquentes et/ou journaux | Politique définie par le métier |
| B | Serveur applicatif standard | Quotidienne ou adaptée à la charge | Plusieurs semaines selon besoin |
| C | Environnement de développement | Selon la valeur des données | Durée limitée |
| D | Données temporaires reconstructibles | Pas nécessairement de sauvegarde | Politique documentée |

Ces fréquences ne sont pas des valeurs universelles. Il faut négocier les exigences avec le propriétaire métier et valider les performances et les coûts.

### 17.4 Architecture de sauvegarde

```text
                  ENVIRONNEMENT DE PRODUCTION
                              |
                     [Moteur de sauvegarde]
                              |
                   +----------+----------+
                   |                     |
             Dépôt de sauvegarde    Copie secondaire
                   |                     |
             Accès restreint         Site distinct
                   |                     |
             Rétention protégée     Protection adaptée
                   |
            Tests de restauration
                   |
            Validation des données
```

Lorsque le niveau de risque le justifie, utiliser des mécanismes de protection contre l’altération ou la suppression, une séparation des identités et une copie indépendante.

Un dépôt accessible en écriture avec les mêmes privilèges qu’un compte compromis de production peut être exposé au même incident.

### 17.5 Définir un plan de reprise

Un PRA exploitable doit préciser :

1. Les services à rétablir.
2. Les priorités et les dépendances.
3. Les contacts et les rôles.
4. Les critères de déclenchement.
5. Le site ou environnement de reprise.
6. Les données à restaurer.
7. L’ordre de démarrage des services.
8. Les contrôles fonctionnels.
9. Les critères de retour en production normale.
10. Les responsabilités de communication.
11. La méthode de mesure des RTO et RPO réellement obtenus.
12. Les preuves et enseignements de chaque exercice.

### 17.6 Tester la restauration

Une sauvegarde dont la restauration n’a jamais été testée n’apporte pas une preuve suffisante de récupérabilité.

Un test doit vérifier :

- La lisibilité et la cohérence des données.
- Les clés et identifiants nécessaires.
- La durée de restauration.
- Les dépendances DNS, réseau et identité.
- Le fonctionnement réel de l’application.
- La capacité à isoler la restauration d’une production potentiellement compromise.
- La réussite des objectifs définis.

Une restauration de VM réussie ne suffit pas toujours. La base de données peut démarrer sans que l’application soit cohérente ou fonctionnelle.

## 18. Sécurité du cloud privé

### 18.1 Modèle de menace

Avant de sélectionner les contrôles, identifier les scénarios de risque.

| Menace | Conséquence possible | Contrôle prioritaire |
|---|---|---|
| Compromission d'un compte administrateur | Contrôle complet de la plateforme | MFA, comptes séparés, audit |
| Accès inter-tenant | Fuite de données | Isolation IAM, réseau et stockage |
| Secret exposé dans Git | Accès non autorisé aux API | Gestion des secrets, rotation |
| Image compromise | Propagation de vulnérabilités | Validation et signature des artefacts |
| Compte de sauvegarde compromis | Suppression ou altération des copies | Identités isolées et rétention protégée |
| Règle réseau trop permissive | Exposition des services | Politique par défaut restrictive |
| API non corrigée | Exploitation d'une vulnérabilité | Gestion des correctifs |
| Modification manuelle non tracée | Configuration non maîtrisée | Audit et contrôles de dérive |
| Saturation volontaire ou accidentelle | Dégradation multi-tenant | Quotas et limites de ressources |

### 18.2 Gestion des identités

La stratégie IAM doit prévoir :

- Identités nominatives pour les administrateurs.
- MFA pour les accès sensibles lorsque la plateforme le permet.
- Comptes de service distincts pour les automatisations.
- Principe du moindre privilège.
- Séparation des rôles d’exploitation et d’approbation.
- Rotation et révocation des identifiants.
- Durée de vie appropriée des jetons.
- Accès d’urgence avec journalisation renforcée.
- Revue périodique des permissions.
- Désactivation rapide des comptes inutiles.

### 18.3 Gestion des secrets

Ne pas intégrer les secrets directement dans :

- Les dépôts Git.
- Les fichiers de configuration partagés.
- Les images de base.
- Les logs de déploiement.
- Les commandes conservées dans l’historique.
- Les documents transmis aux clients.

Une architecture de production doit prévoir un mécanisme sûr d’injection des secrets, des permissions limitées et des procédures de rotation.

### 18.4 Sécurisation des images

Les images utilisées par les consommateurs peuvent être un vecteur de risque.

Le processus de publication devrait inclure :

1. Une source approuvée.
2. Une vérification d’intégrité.
3. Des mises à jour de sécurité.
4. Une réduction de la surface d’attaque.
5. L’absence de secrets permanents dans l’image.
6. Une configuration initiale standardisée.
7. Des tests de démarrage.
8. Une version identifiable.
9. Un propriétaire.
10. Une date de révision ou une règle de retrait.

Il est préférable d’automatiser la production d’images standard que de corriger indéfiniment des machines créées à partir d’images inconnues.

### 18.5 Segmentation de l'administration

L’accès à l’administration du cloud ne doit pas être confondu avec celui d’un système hébergé.

Un technicien chargé de redémarrer une VM ne doit pas obtenir automatiquement le droit de modifier le stockage distribué ou les identités globales.

La segmentation doit être appliquée aux API, aux comptes, aux réseaux d’administration, aux bastions et aux procédures d’approbation.

## 19. Observabilité et supervision de service

### 19.1 Supervision technique et supervision métier

La supervision technique suit les composants : CPU, RAM, disque, réseau, API et services système.

La supervision métier vérifie que les opérations importantes pour les utilisateurs fonctionnent réellement.

Une API HTTP peut répondre avec un code 200 alors que les données affichées sont incorrectes. Une VM peut être démarrée alors que l’application ne répond plus.

La plateforme doit donc surveiller plusieurs niveaux.

```text
NIVEAU 1 : INFRASTRUCTURE
CPU / RAM / Disques / Interfaces / Alimentation
                 |
                 v
NIVEAU 2 : PLATEFORME
API cloud / Hyperviseurs / Stockage / Réseau
                 |
                 v
NIVEAU 3 : SERVICES
DNS / Authentification / Base de données / API
                 |
                 v
NIVEAU 4 : EXPERIENCE UTILISATEUR
Disponibilité / Latence / Erreurs / Transactions métier
```

### 19.2 Les trois grandes familles de télémétrie

- **Métriques** : valeurs mesurées dans le temps, comme le taux d’erreur ou l’utilisation CPU.
- **Journaux** : événements horodatés décrivant ce qui s’est passé.
- **Traces distribuées** : cheminement d’une requête entre plusieurs composants.

OpenTelemetry peut aider à instrumenter et à transporter ces données de manière indépendante du fournisseur. Il ne remplace pas à lui seul le stockage, l’analyse et la visualisation de la télémétrie.

### 19.3 Métriques pertinentes

| Domaine | Métriques |
|---|---|
| Hyperviseur | CPU utilisé, mémoire disponible, charge, erreurs matérielles |
| Stockage | Latence, débit, IOPS, saturation, erreurs, espace libre |
| Réseau | Pertes, erreurs d'interface, débit, latence, congestion |
| API cloud | Disponibilité, latence, taux d'erreur, requêtes par seconde |
| Machines virtuelles | État, disponibilité, saturation et activité |
| Sauvegardes | Dernier succès, âge de la dernière copie, durée, erreurs |
| Sécurité | Échecs d'authentification, accès administratifs, changements critiques |
| Services métier | Transactions réussies, latence perçue, taux d'échec |

Une métrique doit être associée à un usage. Collecter des milliers de mesures sans savoir comment elles participeront à une décision crée du bruit et augmente les coûts.

### 19.4 Exemple de requête PromQL

Supposons que Prometheus collecte une métrique d’utilisation CPU d’un système d’exploitation nommé `node_cpu_seconds_total`.

Exemple de calcul du pourcentage CPU occupé sur cinq minutes :

```promql
100 * (
  1 - avg by (instance) (
    rate(node_cpu_seconds_total{mode="idle"}[5m])
  )
)
```

Cette requête correspond à un indicateur d’utilisation CPU exposé par un exportateur compatible. Le résultat dépend de la collecte, de la qualité des données et du périmètre de mesure.

Il ne représente pas directement la contention CPU vue par chaque VM et ne remplace pas la mesure des temps d’attente ou de la saturation applicative.

### 19.5 Exemple de règle d'alerte Prometheus

```yaml
groups:
  - name: infrastructure
    rules:
      - alert: InstanceCpuSustainedHigh
        expr: |
          100 * (
            1 - avg by (instance) (
              rate(node_cpu_seconds_total{mode="idle"}[5m])
            )
          ) > 90
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Utilisation CPU durablement élevée"
          description: >-
            L'instance {{ $labels.instance }} présente
            une utilisation CPU supérieure à 90 % pendant
            la période de confirmation.
```

Cette règle est un exemple pédagogique. Le seuil doit être ajusté selon la charge, la latence, le niveau de service et le risque de faux positifs.

Une alerte CPU élevée ne doit pas déclencher automatiquement une migration ou un redimensionnement sans tenir compte des dépendances et de la politique de capacité.

### 19.6 Réduire le bruit des alertes

Une stratégie d’alerting doit distinguer :

- Les alertes nécessitant une intervention immédiate.
- Les dégradations à surveiller.
- Les événements informatifs.
- Les alertes dupliquées.
- Les alertes déjà couvertes par un incident plus large.

Les seuils, durées de confirmation, inhibitions, regroupements et fenêtres de maintenance doivent être définis.

Une notification n’est utile que si elle aide quelqu’un à comprendre une situation ou à agir. Un volume élevé d’alertes sans action associée augmente le risque que les alertes importantes soient ignorées.

### 19.7 Supervision hors bande

La supervision doit rester accessible lorsque la plateforme supervisée rencontre une panne.

Éviter que tous les composants d’observabilité dépendent exclusivement du même cluster de production, du même stockage et du même réseau.

Selon les exigences, les collecteurs, le stockage des métriques, les journaux de sécurité et les systèmes de notification peuvent nécessiter des domaines de panne séparés.

## 20. SLA, SLO et SLI

### 20.1 Définitions

**SLI — Service Level Indicator :** mesure d’un aspect du service.

Exemples : pourcentage de requêtes réussies, latence au 95e percentile, nombre d’interruptions.

**SLO — Service Level Objective :** objectif interne mesurable assigné à un SLI.

Exemple : atteindre 99,9 % de disponibilité mensuelle sur le périmètre défini.

**SLA — Service Level Agreement :** engagement contractuel entre les parties, avec un périmètre, des conditions de mesure et éventuellement des conséquences en cas de non-respect.

Un SLO peut être plus exigeant ou plus prudent que la cible contractuelle. Il sert notamment à détecter les dégradations avant qu’elles n’entraînent une violation du SLA.

### 20.2 Exemple de calcul de disponibilité

Pour un mois de 30 jours :

```text
Durée totale :
30 x 24 x 60 = 43 200 minutes
```

Pour une cible de disponibilité de 99,9 % :

```text
Indisponibilité théorique maximale :
43 200 x (1 - 0,999) = 43,2 minutes
```

Pour une cible de 99,95 % :

```text
43 200 x (1 - 0,9995) = 21,6 minutes
```

Ces résultats sont des budgets théoriques calculés sur une période de 30 jours. L’engagement effectif dépend de la méthode de mesure, du périmètre, des exclusions contractuelles et du calendrier retenu.

### 20.3 Attention au périmètre de mesure

Il faut déterminer précisément ce que signifie « disponible ».

Une API qui répond n’est pas nécessairement une application fonctionnelle.

Le service peut être mesuré à partir :

- De sondes externes.
- De requêtes applicatives.
- De transactions synthétiques.
- D’indicateurs internes.
- De la disponibilité d’une VM.
- De métriques de la plateforme.

Le choix dépend de l’engagement. Si le contrat concerne une application métier, la mesure doit refléter autant que possible l’accès réel au service convenu.

### 20.4 Exemple de SLO

```text
Service :
  Portail de réservation

Indicateur :
  Pourcentage de transactions de consultation réussies

Objectif :
  99,9 % sur une fenêtre mensuelle

Latence :
  p95 inférieur ou égal à 500 ms
  pour le scénario testé

Collecte :
  Sonde synthétique et métriques applicatives

Exclusions :
  Définies contractuellement, sans ambiguïté

Responsable :
  Équipe d'exploitation applicative

Escalade :
  Selon gravité, durée et impact
```

La latence, la disponibilité et le taux d’erreur doivent être calculés selon une méthode documentée, stable et vérifiable.

### 20.5 Budget d'erreur

Le budget d’erreur représente la marge de dégradation compatible avec l’objectif de fiabilité.

Si un service vise 99,9 % de disponibilité, les périodes d’indisponibilité consomment progressivement cette marge.

L’approche aide à décider si l’équipe doit :

- Accélérer une livraison.
- Reporter un changement risqué.
- Investir dans la résilience.
- Corriger une cause récurrente.
- Renforcer les tests de restauration.
- Réduire la fréquence des interventions à risque.

Le budget d’erreur ne doit pas être confondu avec une autorisation de provoquer volontairement des incidents.

## 21. Infogérance : rôles, périmètre et contrat

### 21.1 Définir l'infogérance

L’infogérance consiste à confier à un prestataire une partie définie des responsabilités de gestion d’un système d’information.

Le contrat peut couvrir :

- L’infrastructure physique.
- La virtualisation.
- Le cloud privé.
- Le réseau.
- Les sauvegardes.
- La supervision.
- Les systèmes d’exploitation.
- Les bases de données.
- Les applications.
- La sécurité.
- Le support aux utilisateurs.

Le périmètre doit être explicite. Une obligation de « maintenir les serveurs opérationnels » ne précise pas qui corrige les applications, qui valide les changements ou qui répond d’une erreur de configuration métier.

### 21.2 Modèles d'exploitation

| Modèle | Client | Infogérant |
|---|---|---|
| Infrastructure gérée | Administre les OS et applications | Gère serveurs et hyperviseurs |
| Plateforme gérée | Gère applications et données métier | Gère la plateforme cloud |
| Service géré | Définit besoins métier et usages | Gère une partie plus large du service |
| Coresponsabilité | Garde certaines fonctions critiques | Partage les opérations selon une matrice formelle |

Le contrat doit désigner les responsabilités même lorsque plusieurs équipes travaillent sur le même composant.

### 21.3 Matrice RACI

RACI signifie :

- **R — Responsible** : exécute l’activité.
- **A — Accountable** : porte la responsabilité finale de l’activité.
- **C — Consulted** : est consulté.
- **I — Informed** : est informé.

Exemple :

| Activité | Client | Infogérant cloud | Équipe applicative |
|---|---|---|---|
| Définition des besoins métier | A/R | C | C |
| Provisionnement VM | I | A/R | C |
| Configuration OS | Selon contrat | A/R ou C | C |
| Déploiement applicatif | A ou C | C | R |
| Sécurité de la plateforme | C | A/R | C |
| Sauvegarde de l'infrastructure | I/C | A/R | C |
| Validation de restauration métier | A | R/C | R/C |
| Approbation du changement applicatif | A | C | R |
| Gestion d'incident majeur | A selon contrat | R selon périmètre | R selon périmètre |

Une matrice réelle doit nommer les rôles et clarifier ce qui est inclus ou exclu. Il faut éviter les lignes où personne n’est responsable de la décision finale.

### 21.4 Périmètre contractuel

Un contrat d’infogérance devrait préciser :

- Les systèmes concernés et leur inventaire.
- Les horaires de service.
- Les objectifs de disponibilité.
- Les délais de prise en charge.
- Les objectifs de rétablissement.
- Les niveaux de gravité.
- Les fenêtres de maintenance.
- Les procédures d’escalade.
- Les limites de responsabilité.
- Les services hors périmètre.
- Les règles de changement.
- Les exigences de sécurité.
- Les exigences de confidentialité.
- Les responsabilités de sauvegarde.
- Les conditions d’audit.
- Les livrables de reporting.
- Les modalités de réversibilité en fin de contrat.

Les obligations légales, réglementaires et de protection des données doivent être examinées avec les parties compétentes. Une procédure technique seule ne remplace pas le cadrage contractuel.

## 22. Gestion des incidents

### 22.1 Cycle de vie d'un incident

Un incident est un événement qui perturbe ou menace le fonctionnement normal d’un service.

Le processus doit permettre de le détecter, de le qualifier, de le traiter et de rétablir le service.

```text
[DÉTECTION]
     |
     v
[ENREGISTREMENT]
     |
     v
[QUALIFICATION / IMPACT]
     |
     v
[PRIORISATION]
     |
     v
[DIAGNOSTIC]
     |
     v
[CONFINEMENT OU MESURE DE RÉDUCTION]
     |
     v
[RESTAURATION DU SERVICE]
     |
     v
[VALIDATION AVEC LES PARTIES CONCERNÉES]
     |
     v
[COMMUNICATION / CLÔTURE]
     |
     v
[ANALYSE DE CAUSE SI NÉCESSAIRE]
```

La fermeture d’un incident doit préciser le résultat obtenu et les éventuelles actions de suivi.

### 22.2 Gravité et priorité

L’urgence et l’impact ne sont pas identiques.

- L’impact décrit les conséquences du problème.
- L’urgence décrit le délai dans lequel une action est nécessaire.
- La priorité résulte de règles de classement documentées.

Exemple de grille :

| Impact | Urgence | Priorité indicative |
|---|---|---|
| Tous les clients touchés | Immédiate | Critique |
| Service critique indisponible pour un client | Élevée | Haute |
| Dégradation limitée avec solution de contournement | Moyenne | Normale |
| Défaut sans impact immédiat | Faible | Basse |

Les délais de réponse doivent être définis dans le contrat. Il ne faut pas confondre le délai de prise en charge avec le délai de résolution.

### 22.3 Exemple d'incident majeur

**Incident :** plusieurs VM deviennent inaccessibles après une modification réseau.

L’équipe doit :

1. Identifier le périmètre réellement impacté.
2. Ouvrir et qualifier l’incident.
3. Communiquer un état initial factuel.
4. Identifier les changements récents.
5. Vérifier les chemins réseau, routes, règles de sécurité et équipements.
6. Appliquer une mesure de réduction du risque.
7. Restaurer le service.
8. Vérifier avec les propriétaires que les flux métier fonctionnent.
9. Communiquer la fin de l’incident.
10. Documenter la cause et les actions préventives.

Il ne faut pas attendre la fin de l’analyse de cause pour rétablir le service lorsque cela peut être fait sans aggraver la situation.

### 22.4 Exemple de fiche d'incident

```text
ID incident       : INC-2026-0042
Service           : Cloud privé production
Gravité           : Haute
Détection         : 09:14
Début estimé      : 09:10
Impact            : Plusieurs VM inaccessibles
Cause supposée    : Modification de routage
Statut            : En cours
Responsable       : Équipe réseau
Mesure immédiate  : Retour contrôlé sur configuration précédente
Validation        : Tests réseau et applicatifs
Prochaine action  : Analyse de cause et revue du changement
```

Les heures et identifiants de cet exemple sont fictifs.

### 22.5 Post-incident et amélioration continue

Une analyse post-incident doit porter sur le système et les conditions qui ont rendu l’incident possible, sans se limiter à rechercher une personne à blâmer.

Elle doit répondre aux questions suivantes :

- Que s’est-il passé ?
- Quel a été l’impact réel ?
- Pourquoi les contrôles n’ont-ils pas empêché l’incident ?
- Pourquoi la détection a-t-elle eu lieu à ce moment ?
- Quelle mesure a permis le rétablissement ?
- Quelles actions réduiront le risque de répétition ?
- Qui est responsable de ces actions ?
- Comment leur efficacité sera-t-elle mesurée ?

## 23. Gestion des changements

### 23.1 Pourquoi encadrer les changements ?

Un cloud privé concentre des composants mutualisés. Un changement réalisé sur un élément commun peut affecter plusieurs clients.

Exemples :

- Mise à jour des hyperviseurs.
- Modification des réseaux virtuels.
- Changement de configuration Ceph.
- Rotation d’un certificat.
- Mise à niveau des API.
- Modification d’une politique IAM.
- Migration de stockage.

La procédure doit proportionner les contrôles au risque.

### 23.2 Types de changement

**Standard :** procédure répétable, préautorisée et suffisamment testée.

**Normal :** changement nécessitant une évaluation et une approbation selon les règles définies.

**Urgent :** changement nécessaire pour limiter un incident ou un risque immédiat, avec une approbation et une traçabilité adaptées.

Une modification urgente ne doit pas devenir une méthode de contournement systématique de la gouvernance.

### 23.3 Modèle de demande de changement

```text
ID changement :
Service impacté :
Demandeur :
Responsable d'exécution :
Date et fenêtre prévue :

Objectif :
Périmètre :
Risques :
Clients concernés :
Dépendances :
Plan d'exécution :
Plan de validation :
Plan de retour arrière :
Pré-requis :
Sauvegarde ou point de restauration :
Approbation :
Résultat :
Écarts :
Clôture :
```

### 23.4 Exemple de mise à jour d'un cluster

Pour mettre à jour les hyperviseurs d’un cluster, prévoir :

1. Vérification de la capacité disponible en mode dégradé.
2. Vérification de l’état de santé du stockage.
3. Confirmation de l’existence de sauvegardes récentes et récupérables.
4. Contrôle de compatibilité.
5. Validation des dépendances et des versions.
6. Maintenance d’un nœud ou d’un groupe selon le runbook.
7. Migration ou arrêt contrôlé des charges.
8. Mise à jour selon la procédure du fournisseur.
9. Vérification de la santé du nœud.
10. Réintégration et tests.
11. Passage au nœud suivant après validation.
12. Bilan et mise à jour de l’inventaire.

L’ordre précis dépend de l’hyperviseur, du stockage, du quorum et des contraintes de compatibilité. Il ne faut pas appliquer un runbook générique sans l’adapter.

## 24. Gestion des problèmes et des causes racines

Un incident décrit une interruption ou une dégradation. Un problème désigne la cause inconnue, récurrente ou systémique derrière un ou plusieurs incidents.

Exemple :

```text
Incident 1 : VM très lente
Incident 2 : VM très lente sur le même hôte
Incident 3 : délai élevé des I/O sur le même stockage
                    |
                    v
             Analyse commune
                    |
                    v
       Saturation durable du stockage
                    |
                    v
          Problème identifié
                    |
                    v
  Action corrective : capacité / politique I/O
                    |
                    v
       Mesure de non-récurrence
```

L’analyse de cause doit distinguer les symptômes, les causes immédiates et les conditions systémiques.

Une cause racine proposée doit être étayée par des éléments mesurables. « Problème réseau » n’est pas une cause racine suffisamment précise.

## 25. CMDB et inventaire de services

### 25.1 Pourquoi une CMDB ?

Une CMDB (Configuration Management Database) centralise les éléments de configuration et les relations utiles à l’exploitation.

Elle peut recenser :

- Les hôtes physiques.
- Les hyperviseurs.
- Les clusters.
- Les machines virtuelles.
- Les réseaux.
- Les volumes.
- Les sauvegardes.
- Les certificats.
- Les services applicatifs.
- Les propriétaires.
- Les contrats.
- Les fenêtres de maintenance.
- Les dépendances.

### 25.2 Exemple de chaîne de dépendances

```text
Service métier
     |
     v
Application
     |
     v
VM applicative
     |
     +--------> Réseau virtuel
     |
     +--------> Volume
                    |
                    v
              Stockage distribué
                    |
                    v
               Nœuds OSD
                    |
                    v
               Infrastructure
```

En cas d’incident sur un OSD ou un réseau, les relations aident à identifier les services potentiellement impactés.

Une CMDB doit être maintenue à jour par des processus cohérents et automatisés. Un inventaire incomplet ou obsolète peut donner une fausse impression de maîtrise.

### 25.3 Données minimales d'une VM

Exemple de fiche logique :

```text
ID de configuration :
Nom :
Tenant :
Environnement :
Adresse IP :
Profil de calcul :
Réseau :
Volume :
Propriétaire technique :
Propriétaire métier :
Application :
Criticité :
Politique de sauvegarde :
SLO associé :
Date de création :
Date de dernière vérification :
Date de retrait prévue :
```

Les données sensibles d’accès ne doivent pas être stockées dans l’inventaire comme de simples champs texte.

## 26. Capacity planning

### 26.1 Pourquoi prévoir la capacité ?

La capacité doit être planifiée avant que les ressources ne deviennent un goulot d’étranglement.

Une bonne analyse prend en compte :

- L’évolution des consommations.
- Les saisons de forte activité.
- Les projets prévus.
- Les contraintes de licences.
- Les marges de haute disponibilité.
- Les besoins de reconstruction et de migration.
- La croissance des sauvegardes.
- Les besoins de réplication.
- Les latences acceptables.

### 26.2 Indicateurs de capacité

Exemple de tableau de pilotage :

| Ressource | Capacité totale | Capacité planifiable | Consommation | Marge |
|---|---:|---:|---:|---:|
| CPU | 128 cœurs | 76,8 cœurs | 58 cœurs provisionnés dans le modèle | À interpréter selon la contention |
| RAM | 1 024 Go | 652,8 Go en scénario N+1 | 540 Go alloués dans le modèle | Marge limitée |
| Stockage utile | 100 To théoriques après politique de protection | 80 To cibles avec marge | 64 To utilisés | 16 To de marge cible |
| Réseau stockage | 2 liens redondants | Dépend du scénario de panne | Mesure nécessaire | À établir |
| Dépôt de sauvegarde | Selon le dimensionnement | Selon la rétention | Selon le taux de croissance | À établir |

Les valeurs sont illustratives et ne constituent pas des mesures réelles. Le tableau montre que capacité physique, capacité planifiable, consommation provisionnée et consommation réelle sont des notions distinctes.

### 26.3 Projection de croissance

Supposons une consommation de stockage de 40 To, qui augmente en moyenne de 2 To par mois.

Après six mois, une projection linéaire donne :

```text
Stockage actuel : 40 To
Croissance      : 2 To par mois
Durée           : 6 mois

Projection      : 40 + (2 x 6)
                = 52 To
```

Cette projection ne tient pas compte des changements de rétention, de réplication, de compression ou de croissance non linéaire.

Le capacity planning doit être recalculé régulièrement à partir des données observées et des événements connus.

### 26.4 Surveiller la marge opérationnelle

Une plateforme doit conserver assez de marge pour :

- Absorber les pics de charge.
- Migrer des VM.
- Effectuer une maintenance.
- Réparer un disque ou un nœud.
- Reconstruire des données.
- Répondre à une croissance inattendue.
- Maintenir les objectifs de service en mode dégradé.

Le taux de capacité nominale ne suffit pas pour décider si une plateforme peut accueillir de nouvelles charges.

## 27. FinOps et modèle économique

### 27.1 Pourquoi le FinOps est utile en cloud privé

Le FinOps applique des pratiques de gestion financière à la consommation de ressources technologiques.

Il vise à rapprocher le coût, l’utilisation, la valeur métier et les décisions de capacité.

Dans un cloud privé, les coûts peuvent comprendre :

- Les serveurs physiques.
- Le stockage.
- Le réseau.
- L’énergie et le refroidissement.
- Les licences.
- Les contrats de support.
- Les sauvegardes.
- L’exploitation.
- La supervision.
- Les espaces de datacenter.
- L’amortissement des équipements.
- Les coûts de sécurité et de reprise.

Le coût facturé à un client peut également inclure une marge, un niveau de service ou des prestations spécifiques.

### 27.2 Chargeback et showback

**Showback :** afficher au client ou à l’équipe sa consommation et les coûts associés, sans nécessairement effectuer une refacturation.

**Chargeback :** affecter ou refacturer les coûts à un client, une direction ou un centre budgétaire.

Le choix dépend du modèle économique et de la gouvernance.

### 27.3 Exemple de calcul de coût

Supposons que le coût mensuel de la plateforme soit estimé ainsi :

| Poste | Coût mensuel fictif |
|---|---:|
| Serveurs et amortissement | 4 000 € |
| Stockage et sauvegardes | 1 200 € |
| Réseau | 700 € |
| Énergie et hébergement | 900 € |
| Support et exploitation | 2 500 € |
| Coût total | 9 300 € |

La capacité planifiable du service est estimée à 300 unités de ressources mensuelles équivalentes.

```text
Coût unitaire moyen :
9 300 € / 300 = 31 € par unité
```

Cette unité est une hypothèse de calcul. Dans un vrai modèle, les ressources sont hétérogènes et doivent être pondérées selon le coût et l’usage : CPU, RAM, stockage, sauvegarde, réseau ou niveau de service.

Un coût moyen ne doit pas masquer les écarts entre une VM de développement et une base de données critique nécessitant une architecture redondante.

### 27.4 Réduire les dépenses sans fragiliser le service

Les actions possibles incluent :

- Supprimer les ressources abandonnées après validation.
- Redimensionner les VM surdimensionnées.
- Adapter les profils de stockage aux besoins.
- Définir une durée de vie pour les environnements temporaires.
- Optimiser la rétention des sauvegardes selon la politique.
- Réduire les licences inutilisées.
- Améliorer l’utilisation des ressources physiques.
- Mettre en place des alertes de consommation.
- Mesurer le coût des environnements de test.
- Éviter les duplications non nécessaires.

Une économie obtenue en supprimant une copie indispensable ou en supprimant la marge N+1 peut accroître fortement le risque opérationnel. Le coût doit être évalué avec les engagements de service.

## 28. Gestion des niveaux de support

### 28.1 Organisation du support

Une organisation d’infogérance peut distinguer plusieurs niveaux de responsabilité.

**Niveau 1 :** enregistrement, qualification, vérifications standard et application des procédures simples.

**Niveau 2 :** diagnostic technique approfondi, exploitation de la plateforme, réseaux, systèmes et stockage.

**Niveau 3 :** expertise spécialisée, défaut logiciel complexe, architecture, fournisseur ou développement correctif.

Cette répartition est organisationnelle. Elle ne signifie pas que toutes les entreprises doivent avoir exactement trois équipes séparées.

### 28.2 Escalade

Une escalade doit préciser :

- Le motif.
- Le niveau d’urgence.
- L’impact confirmé.
- Les vérifications déjà réalisées.
- Les journaux ou métriques utiles.
- Les mesures prises.
- Les risques des prochaines actions.
- Le responsable de communication.

Éviter l’escalade qui consiste à transférer un ticket sans contexte, sans synthèse et sans preuve du diagnostic.

### 28.3 Passation entre équipes

Une passation d’exploitation doit communiquer :

- Les incidents ouverts.
- Les changements en cours.
- Les alertes importantes.
- Les ressources en maintenance.
- L’état des sauvegardes.
- Les risques de capacité.
- Les actions attendues.
- Les contacts et escalades.
- L’heure de dernière vérification.

L’objectif est qu’une autre personne puisse comprendre l’état du service sans dépendre uniquement d’une conversation orale.

## 29. Maintenance et mises à jour de la plateforme

### 29.1 Cycle de patch management

```text
[Inventaire des versions]
          |
          v
[Analyse des vulnérabilités et avis]
          |
          v
[Évaluation de compatibilité]
          |
          v
[Test en laboratoire]
          |
          v
[Test sur préproduction]
          |
          v
[Approbation du changement]
          |
          v
[Déploiement progressif]
          |
          v
[Contrôles de santé]
          |
          v
[Clôture et mise à jour de l'inventaire]
```

Les vulnérabilités critiques peuvent exiger une procédure accélérée, sans supprimer toute validation de risque.

### 29.2 Dépendances de versions

Une mise à jour peut affecter :

- L’hyperviseur.
- Le noyau.
- Les pilotes réseau et stockage.
- La version de Ceph.
- Les services cloud.
- Les API.
- Les fournisseurs IaC.
- Les scripts d’automatisation.
- Les agents de supervision.

Il faut vérifier la compatibilité et prévoir les contraintes d’ordre de mise à jour.

### 29.3 Maintenance planifiée et communication client

Avant une maintenance, communiquer :

- Les systèmes concernés.
- Le risque d’interruption.
- La fenêtre de maintenance.
- La durée prévue, lorsqu’elle est connue.
- Les actions attendues du client.
- Le mécanisme de retour arrière.
- Le canal de suivi.
- La procédure en cas de dépassement.

Après l’opération, publier le résultat réel, les interruptions observées et les éventuelles actions restantes.

## 30. Réversibilité et sortie d'un contrat d'infogérance

La sortie d’un contrat doit être planifiée autant que son démarrage.

La réversibilité comprend notamment :

- L’inventaire des services.
- Les configurations.
- Les images et modèles.
- Les procédures d’exploitation.
- Les données et sauvegardes concernées.
- La documentation réseau.
- Les certificats et mécanismes de renouvellement.
- Les comptes et autorisations.
- Les contrats et licences transférables.
- Les journaux et preuves nécessaires.
- Les contacts fournisseurs.
- Les procédures de transition.

Les secrets doivent être transférés ou renouvelés selon un processus contrôlé, et les accès de l’ancien prestataire doivent être révoqués à la fin de sa période d’autorisation.

Un export de VM n’est pas une réversibilité complète si les dépendances réseau, les volumes, les certificats, les données, les images et les procédures ne sont pas documentés.

## 31. Étude de cas : cloud privé pour plusieurs clients

### 31.1 Contexte

Une entreprise d’infogérance souhaite héberger les services de cinq clients sur sa propre plateforme de cloud privé.

Les besoins sont :

- Fournir des VM rapidement.
- Isoler les ressources des différents clients.
- Appliquer des politiques de sécurité cohérentes.
- Suivre la capacité.
- Proposer un service de sauvegarde.
- Fournir un rapport mensuel.
- Respecter des objectifs de disponibilité.
- Permettre l’évolution de la capacité.
- Réduire les interventions manuelles.

### 31.2 Architecture logique proposée

```text
                        CLIENTS
                           |
                    Portail de services
                           |
                    IAM / MFA / RBAC
                           |
                    Catalogue et quotas
                           |
                 API / Orchestration / IaC
                           |
        +------------------+------------------+
        |                  |                  |
     Tenant-A           Tenant-B           Tenant-C
        |                  |                  |
   Réseau privé        Réseau privé        Réseau privé
        |                  |                  |
   Groupe de sécurité  Groupe de sécurité  Groupe de sécurité
        |                  |                  |
        +------------------+------------------+
                           |
                   Plateforme de calcul
                           |
                    Stockage distribué
                           |
                Sauvegarde indépendante
                           |
             Supervision / Logs / Alertes
                           |
                 ITSM / Reporting / SLA
```

Les tenants D et E suivent le même modèle logique, avec des quotas et paramètres propres.

### 31.3 Ce qui doit être défini avant la mise en service

- Le catalogue des profils de VM.
- Les quotas par tenant.
- Les règles de réseau.
- La méthode de création des identités.
- Les images autorisées.
- Les politiques de sauvegarde.
- Les engagements contractuels.
- Les niveaux de support.
- Les procédures de maintenance.
- Les scénarios de reprise.
- Le modèle de coût.
- Les indicateurs du rapport mensuel.
- Les procédures de retrait de ressources.

### 31.4 Critères de validation

Le service ne doit pas être déclaré prêt uniquement parce qu’une VM peut être créée.

Il faut également démontrer :

- Qu’un client ne peut pas accéder aux ressources d’un autre.
- Que les quotas sont appliqués.
- Que le système d’audit enregistre les opérations sensibles.
- Que la VM peut être reconstruite ou restaurée selon le contrat.
- Que les alertes utiles atteignent les bonnes personnes.
- Que l’équipe sait traiter un incident majeur.
- Que les changements sont documentés.
- Que la capacité en mode dégradé a été examinée.
- Que les responsabilités contractuelles sont comprises.
- Que le coût peut être estimé à partir de données fiables.

## 32. Travaux pratiques guidés

### TP 1 — Définir le catalogue

Construire un catalogue avec au moins trois offres.

Pour chaque offre, préciser :

- Les ressources.
- Les limites.
- La criticité.
- La sauvegarde.
- Le réseau.
- La politique de maintenance.
- Les mesures de supervision.
- Le coût estimatif.
- Les responsabilités client et infogérant.

Livrable : un fichier Markdown décrivant le catalogue et les règles de validation.

### TP 2 — Séparer deux tenants

Créer deux projets de test ou deux périmètres isolés, selon l’environnement disponible.

Valider :

1. L’accès autorisé du client A à ses ressources.
2. Le refus d’accès du client A aux ressources privées du client B.
3. La séparation des réseaux.
4. La séparation des règles de sécurité.
5. La séparation des quotas.
6. La traçabilité des actions.

Livrable : une matrice de tests positifs et négatifs, avec les résultats.

### TP 3 — Créer une VM de manière reproductible

Construire un workflow d’automatisation décrivant :

- Le projet ou tenant.
- L’image.
- Le profil.
- Le réseau.
- Les règles de sécurité.
- La configuration système.
- Les contrôles fonctionnels.
- L’inscription à la supervision.

Le workflow doit pouvoir être relancé sans créer une deuxième VM par accident.

Livrable : le code, les paramètres, les résultats de tests et une documentation de mise en œuvre.

### TP 4 — Mettre en place la surveillance

Créer un ensemble minimum d’indicateurs :

- Utilisation CPU.
- Mémoire disponible.
- Espace libre.
- Disponibilité d’un endpoint applicatif.
- Dernière sauvegarde réussie.
- Latence d’un service.

Définir les seuils, les périodes de confirmation, les destinataires et les procédures associées.

Livrable : un tableau des alertes et un runbook pour chaque alerte critique.

### TP 5 — Tester une procédure de reprise

Sur un environnement de test, simuler une perte de VM ou une indisponibilité contrôlée d’un composant.

Mesurer :

- Le délai de détection.
- Le délai de prise en charge.
- Le délai de rétablissement.
- Les données perdues.
- Les contrôles nécessaires après reprise.
- Les difficultés rencontrées.

Livrable : un rapport de test PRA avec résultats mesurés, écarts et actions correctives.

### TP 6 — Produire un rapport d'infogérance

Créer un rapport mensuel fictif qui contient :

- La disponibilité mesurée.
- Les incidents et leurs durées.
- Les changements exécutés.
- Les résultats des sauvegardes.
- Les tests de restauration.
- Les vulnérabilités et correctifs.
- La consommation de capacité.
- Les tendances de coût.
- Les risques ouverts.
- Le plan d’amélioration.

Le rapport doit distinguer les mesures réelles, les estimations et les objectifs contractuels.

## 33. Exercices d'application avec corrections

### Exercice 1 — Quotas

Un tenant dispose d’un quota de 40 vCPU et d’un quota de 96 Go de RAM. Il possède déjà 8 VM qui consomment au total 28 vCPU et 64 Go de RAM.

Quelle quantité de ressources peut-il encore demander en tenant compte uniquement des quotas ?

**Correction :**

```text
vCPU disponibles dans le quota :
40 - 28 = 12 vCPU

RAM disponible dans le quota :
96 - 64 = 32 Go
```

Ce résultat ne garantit pas que la plateforme possède physiquement la capacité nécessaire.

### Exercice 2 — Budget d'indisponibilité

Un service vise une disponibilité de 99,95 % sur 30 jours.

Calculer le budget d’indisponibilité théorique.

**Correction :**

```text
Durée totale :
30 x 24 x 60 = 43 200 minutes

Indisponibilité :
43 200 x 0,0005 = 21,6 minutes
```

Le budget est de 21,6 minutes, sous réserve de la méthode de mesure contractuelle.

### Exercice 3 — Sauvegarde

Un client demande un RPO de 15 minutes. Les sauvegardes complètes sont effectuées une fois par nuit. Est-ce suffisant ?

**Correction :**

Non, pas à elles seules. Une sauvegarde quotidienne ne permet pas de garantir une perte maximale de 15 minutes si les données changent régulièrement.

Il faut étudier des mécanismes complémentaires : sauvegardes plus fréquentes, journaux transactionnels, réplication ou autre méthode cohérente avec l’application. Le résultat doit être mesuré par des tests de restauration.

### Exercice 4 — Incident réseau

Plusieurs VM ont perdu l’accès à leur passerelle immédiatement après un changement de réseau.

Quelle doit être la première démarche ?

**Correction :**

Qualifier l’impact, établir les faits, examiner le changement récent et vérifier les routes, interfaces, règles de sécurité et équipements concernés. Si les éléments confirment une relation avec le changement, appliquer le plan de retour arrière approuvé ou une mesure de réduction du risque, puis valider le fonctionnement réseau et applicatif.

Il ne faut pas redémarrer toutes les VM sans hypothèse technique, car cela risque d’ajouter des interruptions sans corriger la cause.

### Exercice 5 — Incident ou problème ?

Une VM est lente une seule fois après un pic ponctuel. Un mois plus tard, dix VM présentent régulièrement la même dégradation liée aux I/O du stockage.

**Correction :**

Chaque dégradation peut donner lieu à un incident. La répétition d’un symptôme similaire sur plusieurs VM indique la nécessité d’une analyse de problème, afin de déterminer si une cause commune explique les incidents.

### Exercice 6 — Coût d'un service

Une plateforme coûte 12 000 € par mois. Son modèle financier attribue une unité de coût équivalente à chaque unité de ressource planifiable, pour un total de 400 unités.

Quel est le coût moyen mensuel par unité ?

**Correction :**

```text
12 000 / 400 = 30 €
```

Le coût moyen estimé est de 30 € par unité et par mois. Il ne devient un tarif contractuel que si la méthode de calcul, les services inclus et les règles de facturation sont définis.

### Exercice 7 — Surallocation

Un cloud héberge plusieurs VM fortement consommatrices de CPU. Le ratio de surallocation est de 5:1, mais le taux d’attente CPU augmente fortement aux heures de pointe.

Que faut-il examiner avant d’ajouter de nouvelles VM ?

**Correction :**

Il faut mesurer la contention, l’utilisation réelle, les profils de charge, les pics simultanés, les latences applicatives et la capacité disponible après panne. Il faut aussi examiner les possibilités de redimensionnement, de déplacement contrôlé et d’ajout de capacité.

Réduire le ratio de surallocation peut être pertinent, mais ce n’est pas la seule solution possible.

### Exercice 8 — Isolation multi-tenant

Un utilisateur du tenant A peut consulter les informations détaillées d’un volume du tenant B grâce à un endpoint d’API.

Que révèle ce comportement ?

**Correction :**

Il indique une possible défaillance d’autorisation ou un problème de configuration. Il faut préserver les éléments de preuve, qualifier l’impact, limiter le risque, tester les permissions et examiner les journaux. Il faut également vérifier que les données du volume ne sont pas accessibles et déterminer si d’autres ressources sont concernées.

## 34. Projet de fin de niveau

### Concevoir une offre de cloud privé infogéré

L’apprenant doit proposer une architecture de cloud privé destinée à plusieurs clients, comprenant au minimum trois tenants distincts.

Le projet doit démontrer que le service peut être fourni de manière répétable, sécurisée et exploitable.

### Livrable A — Dossier d'architecture

Documenter :

- Les composants physiques et logiques.
- Les domaines de panne.
- Les réseaux de la plateforme.
- L’architecture de calcul.
- La stratégie de stockage.
- Le modèle de haute disponibilité.
- Les dépendances de la plateforme.
- Les hypothèses et limites du dimensionnement.

### Livrable B — Modèle multi-tenant

Définir :

- Les identités et rôles.
- Les projets.
- Les quotas.
- Les réseaux.
- Les règles d’isolation.
- Les contrôles d’accès.
- Les tests négatifs d’autorisation.

### Livrable C — Catalogue et automatisation

Fournir :

- Trois offres de ressources.
- Un modèle IaC adapté à la plateforme choisie.
- Un playbook Ansible ou un mécanisme équivalent.
- Une procédure de création.
- Une procédure de suppression.
- Une gestion des erreurs partielles.
- Une validation après déploiement.

### Livrable D — Exploitation

Fournir :

- La supervision.
- Les alertes.
- Les procédures de diagnostic.
- Les procédures de sauvegarde.
- Le PRA.
- Le plan de maintenance.
- Les procédures d’incident et de changement.
- L’inventaire des composants.

### Livrable E — Infogérance et gouvernance

Rédiger :

- La matrice RACI.
- Les SLI et SLO.
- Les engagements SLA proposés.
- Le processus d’escalade.
- Le modèle de rapport mensuel.
- Le modèle de coût.
- La procédure de réversibilité.

### Livrable F — Démonstration

La démonstration doit montrer :

1. La création d’une ressource par une procédure reproductible.
2. Le refus d’une opération non autorisée.
3. La présence de la ressource dans l’inventaire.
4. L’activation de la supervision.
5. L’association à une politique de sauvegarde.
6. L’analyse d’un incident simulé.
7. La production d’un compte rendu exploitable.

Le projet ne peut être considéré comme réussi si la démonstration se limite à créer une VM.

## 35. Défi expert : panne, dérive et SLA

### Scénario

Le cloud privé héberge cinq clients. Le service de stockage montre une dégradation de latence. Plusieurs clients signalent des applications lentes. Une automatisation récemment exécutée a modifié la configuration de certaines VM. Parallèlement, un des nœuds de stockage est indisponible.

Les objectifs de disponibilité du mois risquent d’être dépassés.

### Mission

Tu dois organiser la réponse à cet incident en respectant les priorités suivantes :

1. Qualifier les services et les clients impactés.
2. Vérifier si l’incident constitue un incident majeur.
3. Réduire l’impact sans aggraver l’état du stockage.
4. Déterminer la relation entre l’automatisation et la dégradation.
5. Vérifier la capacité et l’état de reconstruction du stockage.
6. Identifier les changements récents.
7. Communiquer régulièrement avec les responsables concernés.
8. Rétablir le service et effectuer les tests applicatifs.
9. Calculer l’impact sur les indicateurs de service.
10. Définir les actions correctives et préventives.
11. Documenter les écarts entre procédure et exécution.
12. Proposer des améliorations de gouvernance.

### Résultat attendu

Un rapport d’incident structuré en quatre parties :

**Partie 1 — Situation et impact :** faits établis, périmètre, chronologie et conséquences.

**Partie 2 — Mesures opérationnelles :** vérifications, mesures de réduction de l’impact, décision de reprise et validation.

**Partie 3 — Engagements de service :** mesures de disponibilité, délai de rétablissement et conséquences éventuelles selon le contrat.

**Partie 4 — Prévention :** correction de la cause, contrôles du pipeline, seuils de supervision et mises à jour du runbook.

Le défi consiste à démontrer une maîtrise technique et organisationnelle du service, pas uniquement la capacité à redémarrer un composant.

## 36. Bonnes pratiques à retenir

### Architecture

- Séparer les responsabilités des composants.
- Identifier les domaines de panne.
- Vérifier la capacité en mode dégradé.
- Documenter les dépendances.
- Choisir les outils selon les besoins réels.
- Éviter les points uniques de défaillance sur les services critiques.

### Multi-tenant

- Définir des frontières explicites.
- Appliquer le moindre privilège.
- Tester les refus d’accès.
- Isoler les réseaux et les données.
- Séparer les responsabilités d’administration.
- Auditer les opérations sensibles.

### Automatisation

- Versionner les configurations.
- Revoir les changements avant application.
- Tester en dehors de la production.
- Protéger l’état et les secrets.
- Rendre les workflows idempotents.
- Traiter les erreurs partielles.
- Contrôler les dérives de configuration.

### Exploitation

- Associer les alertes à des procédures.
- Garder une supervision utile pendant les pannes.
- Tester les restaurations.
- Réviser les runbooks.
- Mesurer les RTO et les RPO réels.
- Analyser les incidents récurrents.
- Préserver les preuves et les chronologies.

### Infogérance

- Définir les périmètres.
- Formaliser les responsabilités.
- Distinguer SLA, SLO et SLI.
- Documenter l’escalade.
- Prévoir les changements urgents.
- Produire des rapports fondés sur des mesures vérifiables.
- Planifier la réversibilité dès le démarrage du contrat.

### FinOps

- Mesurer la consommation.
- Distinguer quotas et capacité physique.
- Définir une méthode transparente de calcul des coûts.
- Éliminer les ressources inutilisées après validation.
- Ne pas réduire la résilience sans analyser le risque.
- Ajuster les politiques à partir des consommations observées.

## 37. Référence opérationnelle rapide

| Besoin | Outil ou mécanisme |
|---|---|
| Gestion des identités et des rôles | Keystone ou IAM de la plateforme |
| Gestion des machines cloud | Nova ou API de virtualisation |
| Gestion des réseaux virtuels | Neutron, API réseau ou mécanisme équivalent |
| Stockage bloc distribué | Ceph RBD ou solution adaptée |
| Orchestration cloud | Heat, workflow ou orchestrateur compatible |
| Infrastructure as Code | OpenTofu ou Terraform |
| Configuration des systèmes | Ansible |
| Supervision métrique | Prometheus |
| Routage et regroupement d'alertes | Alertmanager |
| Télémétrie applicative | OpenTelemetry et backend compatible |
| Sauvegarde | Plateforme de sauvegarde indépendante |
| Gestion des incidents | ITSM |
| Suivi des dépendances | CMDB ou inventaire de configuration |
| Gestion de capacité | Métriques, prévisions et revues périodiques |
| Pilotage financier | Showback, chargeback et FinOps |

## 38. Glossaire

**API :** interface permettant à un programme d’interagir avec un service.

**Capacity planning :** planification des ressources nécessaires au maintien des niveaux de service.

**Chargeback :** affectation ou refacturation des coûts à un consommateur.

**CMDB :** base de données des éléments de configuration et de leurs relations.

**Cloud privé :** environnement cloud destiné à une organisation ou à un périmètre d’utilisateurs défini, avec des ressources et des politiques administrées selon son modèle de gouvernance.

**Ceph :** plateforme de stockage distribué offrant notamment des interfaces objet, bloc et fichiers.

**CI/CD :** chaîne d’intégration et de déploiement automatisée.

**Dérive de configuration :** différence entre l’état attendu et l’état réel d’un système.

**FinOps :** pratiques de pilotage financier et d’optimisation économique des ressources technologiques.

**HA :** haute disponibilité.

**IAM :** gestion des identités et des accès.

**IaC :** Infrastructure as Code.

**Infogérance :** gestion opérationnelle d’un périmètre informatique confiée à un prestataire selon un cadre défini.

**Incident :** interruption ou dégradation d’un service.

**ITSM :** organisation et outils de gestion des services informatiques.

**N+1 :** capacité ou redondance permettant de tolérer la perte d’un composant prévu dans le modèle de résilience.

**OpenStack :** plateforme cloud composée de services spécialisés, notamment pour le calcul, l’identité, le réseau, le stockage et l’orchestration.

**OpenTelemetry :** ensemble d’API, de SDK et d’outils pour produire, collecter et exporter des données de télémétrie.

**OpenTofu / Terraform :** outils d’Infrastructure as Code permettant de décrire et de gérer des ressources.

**PCA :** plan de continuité d’activité.

**PRA :** plan de reprise d’activité.

**RACI :** matrice de responsabilités : Responsible, Accountable, Consulted, Informed.

**RPO :** perte maximale de données acceptable exprimée en temps.

**RTO :** objectif de délai de rétablissement du service.

**SLA :** engagement de niveau de service défini contractuellement.

**SLI :** indicateur de niveau de service.

**SLO :** objectif de niveau de service mesurable.

**Showback :** présentation des coûts et consommations à un consommateur sans refacturation nécessairement associée.

**Tenant :** périmètre logique d’un consommateur ou d’une organisation au sein d’une plateforme mutualisée.

**Workflow :** séquence d’opérations avec étapes, conditions, résultats et mécanismes de reprise.

## 39. Documentation officielle

### OpenStack

- Documentation générale : https://docs.openstack.org/
- Guides d'installation : https://docs.openstack.org/install-guide/
- Services de la plateforme : https://docs.openstack.org/install-guide/openstack-services.html
- Identité Keystone : https://docs.openstack.org/keystone/latest/
- Calcul Nova : https://docs.openstack.org/nova/latest/
- Réseau Neutron : https://docs.openstack.org/neutron/latest/
- Stockage bloc Cinder : https://docs.openstack.org/cinder/latest/
- Orchestration Heat : https://docs.openstack.org/heat/latest/
- Télémétrie Ceilometer : https://docs.openstack.org/ceilometer/latest/

Vérifier la version de la documentation correspondant à la version effectivement déployée, en particulier pour les procédures de mise à niveau et les politiques d’accès.

### Proxmox VE et virtualisation

- Documentation officielle Proxmox : https://www.proxmox.com/en/downloads/proxmox-virtual-environment/documentation
- Guide d'administration Proxmox VE : https://pve.proxmox.com/pve-docs/pve-admin-guide.pdf
- Documentation QEMU : https://www.qemu.org/docs/master/
- Documentation libvirt : https://www.libvirt.org/docs.html
- Manuel de `virsh` : https://www.libvirt.org/manpages/virsh.html

### Ceph

- Documentation officielle : https://docs.ceph.com/en/latest/
- Architecture : https://docs.ceph.com/en/latest/architecture/
- Documentation d’administration : https://docs.ceph.com/en/latest/rados/operations/

### Infrastructure as Code et configuration

- Documentation OpenTofu : https://opentofu.org/docs/
- Langage de configuration OpenTofu : https://opentofu.org/docs/language/
- État et gestion des ressources Terraform : https://developer.hashicorp.com/terraform/language/state
- Langage Terraform : https://developer.hashicorp.com/terraform/language
- Playbooks Ansible : https://docs.ansible.com/projects/ansible/latest/playbook_guide/index.html

### Observabilité

- Vue d'ensemble Prometheus : https://prometheus.io/docs/introduction/overview/
- Alerting Prometheus : https://prometheus.io/docs/alerting/latest/overview/
- Documentation OpenTelemetry : https://opentelemetry.io/docs/

## 40. Conclusion du niveau expert

La gestion d’un cloud privé en production demande bien davantage que la maîtrise des machines virtuelles.

L’ingénieur cloud doit relier les contraintes de calcul, de stockage et de réseau aux besoins des consommateurs, aux politiques de sécurité, aux procédures d’exploitation et aux engagements contractuels.

Une plateforme correctement industrialisée ne se contente pas de démarrer des VM. Elle doit pouvoir les créer de façon reproductible, contrôler leurs permissions, mesurer la consommation, détecter les dégradations, récupérer après une panne, documenter les changements et démontrer la qualité du service fourni.

L’infogérance exige en plus une organisation fiable : responsabilités explicites, escalade structurée, gestion des changements, rapports mesurables, analyse des incidents et capacité à transférer le service à un autre opérateur.

Le niveau expert est atteint lorsque l’ingénieur est capable de **concevoir, sécuriser, automatiser, exploiter et faire évoluer l’ensemble du service**, tout en démontrant que les objectifs techniques et contractuels peuvent être respectés.