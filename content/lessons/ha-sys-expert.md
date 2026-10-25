# DRP et PRA : Reprise d'activité et continuité des services
## Cours expert — Gestion de crise, stratégies de récupération, sauvegardes, réplication et reconstruction du système d'information

## 1. Présentation du cours

### 1.1 Objectif général

Dans les niveaux précédents, tu as appris à construire des mécanismes de haute disponibilité avec Keepalived, HAProxy, Pacemaker, Corosync et DRBD.

Tu sais désormais qu'un service peut basculer d'un serveur vers un autre, qu'une adresse IP virtuelle peut être déplacée et qu'un cluster peut gérer des ressources selon des contraintes.

Mais imaginons maintenant les situations suivantes :

- Les deux nœuds d'un cluster deviennent indisponibles.
- Un incendie détruit la salle informatique.
- Une baie de stockage tombe définitivement en panne.
- Une mauvaise manipulation supprime une base de données.
- Un rançongiciel chiffre les données de production et les sauvegardes accessibles.
- Une mise à jour défectueuse rend plusieurs services inutilisables.
- Les serveurs restent allumés, mais les utilisateurs ne peuvent plus travailler.
- Le site de secours est disponible, mais personne ne sait dans quel ordre redémarrer les applications.

Dans ces situations, la haute disponibilité locale ne suffit pas nécessairement.

Il faut une stratégie préparée pour rétablir les services, récupérer les données, reconstruire les systèmes et coordonner les opérations techniques et humaines.

C'est le rôle du **PRA — Plan de Reprise d'Activité**, appelé **DRP — Disaster Recovery Plan** en anglais. L'ANSSI emploie cette équivalence dans son CyberDico. Le PRA décrit les procédures nécessaires pour rétablir et reprendre les activités après un incident. Le PCA, ou Plan de Continuité d'Activité, vise davantage à maintenir les activités pendant la perturbation, éventuellement en mode dégradé. [ANSSI — CyberDico](https://cyber.gouv.fr/cyberdico/)

Ce cours va t'apprendre à concevoir un PRA qui ne repose pas uniquement sur des équipements redondants, mais sur une organisation complète : objectifs métier, dépendances, sauvegardes, infrastructure de secours, procédures, responsabilités, tests et validation.

### 1.2 Compétences visées

À l'issue de ce cours, tu devras être capable de :

- Distinguer haute disponibilité, PCA, PRA, sauvegarde et réponse à incident.
- Réaliser une analyse d'impact sur l'activité.
- Définir des objectifs de récupération RTO et RPO réalistes.
- Identifier les applications prioritaires et leurs dépendances.
- Concevoir une stratégie de reprise sur un site secondaire.
- Comparer les architectures de secours à froid, tiède et chaud.
- Concevoir une stratégie de sauvegarde indépendante et protégée.
- Protéger les sauvegardes contre les erreurs humaines et les rançongiciels.
- Déterminer l'ordre de restauration des services.
- Préparer la reconstruction de l'identité, du DNS, du réseau et des services d'infrastructure.
- Comprendre les limites d'un cluster local en cas de sinistre.
- Intégrer Keepalived, HAProxy, Pacemaker, Corosync et DRBD dans une stratégie de résilience.
- Organiser une reprise de base de données avec contrôle de cohérence.
- Préparer des procédures de basculement et de retour au site principal.
- Gérer une reprise après cyberattaque sans réintroduire un système compromis.
- Construire des procédures d'exploitation utilisables en situation de crise.
- Tester, mesurer et améliorer un PRA.

### 1.3 Prérequis

Le cours suppose que tu maîtrises les bases et notions intermédiaires suivantes :

- Administration Linux.
- Configuration réseau et résolution DNS.
- Administration des services avec systemd.
- Keepalived et VRRP.
- HAProxy et équilibrage de charge.
- Pacemaker et Corosync.
- Quorum et fencing.
- DRBD et réplication par blocs.
- Notions de stockage, de systèmes de fichiers et de bases de données.
- Sauvegarde et restauration de fichiers.
- Journaux système et diagnostic réseau.

Les exemples utilisent principalement Linux et des services Web, mais les principes de PRA sont applicables à des infrastructures hybrides comprenant également Windows Server, des bases de données, des services cloud et des applications métier.

### 1.4 Environnement de référence

Tout au long du cours, nous utiliserons une entreprise fictive disposant de deux sites.

<text_unused></text_unused>
```text
                         UTILISATEURS
                              |
                              v
                        ACCÈS CLIENTS
                              |
                              v
                +---------------------------+
                |       SITE PRINCIPAL      |
                |                           |
                |  Keepalived / HAProxy     |
                |  Cluster Pacemaker        |
                |  Services applicatifs     |
                |  Base de données          |
                |  Stockage de production   |
                +-------------+-------------+
                              |
                      Réplication contrôlée
                              |
                              v
                +---------------------------+
                |      SITE DE SECOURS      |
                |                           |
                |  Hôtes de secours         |
                |  Applications répliquées  |
                |  Stockage secondaire      |
                |  Réseau de reprise        |
                +---------------------------+

                +---------------------------+
                |  INFRASTRUCTURE BACKUP     |
                |                           |
                |  Sauvegardes protégées    |
                |  Copies hors site         |
                |  Copies immuables ou      |
                |  hors ligne               |
                |  Procédures de restauration|
                +---------------------------+
```

Ce schéma décrit trois fonctions distinctes :

1. La production fournit les services normaux.
2. Le site de secours permet de reprendre les services après certains incidents.
3. L'infrastructure de sauvegarde permet de restaurer des données et des systèmes depuis des points de récupération connus.

Le site de secours et la sauvegarde ne doivent pas être considérés comme deux noms pour le même mécanisme. Une réplication peut propager une corruption ; une sauvegarde permet de revenir à un état antérieur, si une copie saine a été conservée.

## 2. Comprendre la différence entre HA, PCA et PRA

### 2.1 Haute disponibilité : réduire l'interruption

La haute disponibilité, ou HA, repose sur des mécanismes qui détectent certaines pannes et permettent au service de continuer ou de reprendre automatiquement.

Exemples :

- Keepalived transfère une VIP.
- HAProxy retire un backend défaillant.
- Pacemaker redémarre une ressource sur un autre nœud.
- Une application est répartie sur plusieurs instances.
- Un stockage résilient survit à certaines défaillances.

Une architecture hautement disponible est principalement conçue pour des pannes définies et des mécanismes de récupération prévus.

Elle ne garantit pas que l'ensemble du site sera disponible si toutes les machines, tous les réseaux ou toutes les données dépendent d'une infrastructure détruite.

### 2.2 PCA : maintenir l'activité

Le PCA vise à maintenir les activités essentielles pendant une perturbation.

Il peut prévoir :

- Un fonctionnement en mode dégradé.
- Une procédure manuelle temporaire.
- Un service alternatif.
- Des moyens de communication de secours.
- Un site de remplacement.
- Une réorganisation des équipes.
- Des priorités métier différentes pendant la crise.

Exemple : le site Web public est indisponible, mais les équipes commerciales peuvent encore traiter les commandes par un canal de secours.

### 2.3 PRA : rétablir l'activité

Le PRA décrit comment restaurer les services et reprendre un fonctionnement conforme aux besoins métier.

Il doit répondre à des questions précises :

- Qui déclare l'activation du PRA ?
- Quel scénario a été détecté ?
- Quelles applications faut-il restaurer en priorité ?
- Quelles données peuvent être récupérées ?
- Quel est le site cible ?
- Dans quel ordre faut-il redémarrer les services ?
- Comment vérifier la cohérence des données ?
- Comment les utilisateurs accèdent-ils à nouveau aux applications ?
- Quand la reprise est-elle considérée comme validée ?
- Comment revenir à l'architecture nominale ?

### 2.4 Comparaison des mécanismes

| Mécanisme | Objectif principal | Exemple |
|---|---|---|
| Haute disponibilité | Absorber certaines pannes techniques | Basculement Pacemaker |
| PCA | Maintenir les opérations essentielles | Procédure temporaire de traitement manuel |
| PRA | Rétablir les services après une interruption importante | Activation du site secondaire |
| Sauvegarde | Retrouver des données ou un système antérieur | Restaurer une base de données |
| Réplication | Maintenir une copie de données ou d'un état | Réplication DRBD |
| Réponse à incident | Détecter, contenir et traiter l'incident | Isoler des serveurs compromis |
| Reconstruction | Recréer un environnement sain | Réinstaller un service depuis une image validée |

Ces mécanismes doivent être complémentaires.

## 3. Les scénarios de sinistre

### 3.1 Définir les risques avant de choisir la technologie

Un PRA doit partir des risques que l'organisation souhaite traiter.

Les scénarios peuvent comprendre :

**Pannes matérielles**

- Panne d'un serveur.
- Panne d'une baie de stockage.
- Défaillance d'un commutateur.
- Défaillance d'une alimentation électrique.

**Pannes logicielles**

- Mise à jour défectueuse.
- Corruption d'un système de fichiers.
- Erreur de configuration.
- Défaillance d'une application.

**Erreurs humaines**

- Suppression accidentelle d'une base de données.
- Mauvaise modification du DNS.
- Suppression de fichiers de production.
- Destruction involontaire d'une ressource de cluster.
- Changement de configuration sans sauvegarde préalable.

**Incidents de cybersécurité**

- Rançongiciel.
- Compromission d'un compte administrateur.
- Suppression des sauvegardes accessibles.
- Modification malveillante des configurations.
- Compromission des systèmes de gestion.
- Persistance d'un attaquant dans le système d'information.

**Sinistres physiques ou régionaux**

- Incendie.
- Inondation.
- Coupure électrique prolongée.
- Inaccessibilité du site.
- Incident majeur de télécommunication.
- Indisponibilité prolongée d'un fournisseur.

Un même incident peut toucher plusieurs catégories.

### 3.2 Construire une matrice de risque

Le risque combine généralement une estimation de probabilité et une estimation d'impact.

Un modèle pédagogique consiste à attribuer une note à chaque dimension :

| Probabilité | Note illustrative |
|---|---:|
| Rare | 1 |
| Peu probable | 2 |
| Possible | 3 |
| Probable | 4 |
| Très probable | 5 |

| Impact | Note illustrative |
|---|---:|
| Très faible | 1 |
| Faible | 2 |
| Modéré | 3 |
| Élevé | 4 |
| Critique | 5 |

Un score simple peut être calculé :

\[
\text{Score de risque} = \text{Probabilité} \times \text{Impact}
\]

Ce score permet de comparer des scénarios dans un modèle simplifié, mais il ne doit pas remplacer l'analyse métier.

Exemple :

| Scénario | Probabilité | Impact | Score |
|---|---:|---:|---:|
| Panne d'un serveur Web | 3 | 3 | 9 |
| Perte d'une base métier | 2 | 5 | 10 |
| Suppression des sauvegardes | 2 | 5 | 10 |
| Perte du site principal | 1 | 5 | 5 |
| Compromission d'un compte administrateur | 3 | 5 | 15 |

Le score n'est pas une mesure exacte de la probabilité de perte. Il sert à organiser la discussion et à identifier les risques qui méritent des contrôles supplémentaires.

### 3.3 Décrire chaque scénario

Un scénario de PRA doit contenir :

- L'événement déclencheur.
- Les composants potentiellement affectés.
- Les critères de déclaration du sinistre.
- Les conséquences métier.
- Les mesures de confinement.
- La stratégie de reprise.
- Les dépendances nécessaires.
- Les responsabilités.
- Les critères de sortie de crise.

Exemple :

```text
Scénario : perte du site principal

Déclencheur :
  Indisponibilité durable de l'infrastructure principale.

Conséquences :
  Applications métier inaccessibles.
  Base de données de production indisponible.
  Stockage principal inutilisable.

Objectif :
  Reprendre les services critiques sur le site secondaire.

Dépendances :
  Connectivité du site de secours.
  DNS.
  Identités et accès.
  Stockage disponible.
  Copie de données cohérente.

Décision :
  Activation formelle du PRA.

Validation :
  Contrôles techniques et métier réussis.
```

## 4. Analyse d'impact sur l'activité (BIA)

### 4.1 Qu'est-ce qu'une BIA ?

L'analyse d'impact sur l'activité, souvent appelée *Business Impact Analysis* ou BIA, permet de déterminer quelles activités sont critiques et quelles conséquences leur interruption entraîne.

Elle aide à répondre à quatre questions :

1. Quelles activités doivent absolument continuer ou être reprises rapidement ?
2. Combien de temps peuvent-elles rester indisponibles ?
3. Quelle quantité de données peut être perdue sans dépasser les limites acceptées ?
4. De quelles ressources et applications ces activités dépendent-elles ?

La BIA est fondamentale : une architecture technique ne devrait pas définir seule les objectifs de reprise.

### 4.2 Identifier les activités métier

Prenons une entreprise qui possède :

- Un portail de commande.
- Un système de gestion des stocks.
- Une base de données des commandes.
- Un serveur de fichiers.
- Un service de courrier électronique.
- Un portail documentaire.
- Un environnement de développement.

Toutes ces activités n'ont pas nécessairement la même priorité.

Si le système de commande est indisponible, l'entreprise peut perdre des ventes. Si l'environnement de développement est indisponible, le travail peut généralement être reporté plus longtemps.

La priorité dépend du contexte réel de l'entreprise.

### 4.3 Construire une fiche d'analyse

Pour chaque activité, relève :

- Le responsable métier.
- Les utilisateurs concernés.
- Les plages horaires d'utilisation.
- Les conséquences d'une interruption.
- Les dépendances techniques.
- Les solutions de contournement.
- La durée maximale d'interruption admissible.
- Le point de reprise des données attendu.
- Le coût et les conséquences d'un dépassement.

Exemple :

| Activité | Conséquence d'une panne | Solution de secours |
|---|---|---|
| Commandes | Perte ou retard de commandes | Procédure manuelle temporaire |
| Gestion de stock | Erreurs d'inventaire | Enregistrement temporaire contrôlé |
| Fichiers internes | Retard de travail | Espace documentaire de secours |
| Environnement de test | Retard de développement | Report des tests non urgents |

Les solutions de contournement doivent être réalistes et validées par les équipes métier.

### 4.4 Construire une cartographie des dépendances

Une application dépend souvent de composants qui ne sont pas immédiatement visibles pour ses utilisateurs.

Exemple :

```text
APPLICATION DE COMMANDE
|
+-- Serveur Web
|   |
|   +-- DNS
|   +-- Certificats TLS
|
+-- Service applicatif
|   |
|   +-- Authentification
|   +-- Service de configuration
|
+-- Base de données
|   |
|   +-- Stockage
|   +-- Réseau
|
+-- Services d'infrastructure
    |
    +-- Résolution de noms
    +-- Synchronisation de l'heure
    +-- Gestion des secrets
    +-- Supervision
```

Une application peut être correctement restaurée tout en restant inutilisable si son DNS, ses certificats ou son système d'authentification ne sont pas disponibles.

### 4.5 Cartographier les dépendances critiques

Pour chaque dépendance, documente :

- Son rôle.
- Son emplacement.
- Son propriétaire.
- Son mode de reprise.
- Sa sauvegarde.
- Sa criticité.
- Son ordre de restauration.
- Ses dépendances propres.

Exemple :

| Dépendance | Besoin | Conséquence si absente |
|---|---|---|
| DNS | Résoudre les noms de services | Accès impossible ou perturbé |
| NTP | Maintenir une heure cohérente | Problèmes d'authentification et de journaux |
| Identité | Authentifier les utilisateurs | Connexions impossibles |
| Certificats | Sécuriser les connexions TLS | Erreurs de sécurité et d'accès |
| Base de données | Fournir les données métier | Application inutilisable |
| Stockage | Accéder aux fichiers | Services incomplets |

L'ordre de reprise doit refléter ces dépendances.

## 5. RTO, RPO et durée maximale d'interruption

### 5.1 RTO : objectif de temps de reprise

Le RTO (*Recovery Time Objective*) correspond à la durée ciblée pour rétablir un service.

Exemple :

Le portail de commande doit être de nouveau opérationnel dans les 60 minutes suivant un sinistre.

Le RTO cible est donc de 60 minutes.

La reprise doit inclure plus que le démarrage de la VM. Elle doit inclure la récupération des données nécessaires, le fonctionnement des dépendances, les contrôles de cohérence et la validation fonctionnelle.

### 5.2 RPO : objectif de point de reprise

Le RPO (*Recovery Point Objective*) indique l'écart temporel maximal que l'organisation accepte entre l'état des données au moment de l'incident et l'état récupéré.

Exemple :

Si une base de données peut perdre au maximum cinq minutes de données, son RPO cible est de cinq minutes.

Un RPO nul est un objectif particulièrement exigeant. Il ne doit jamais être annoncé simplement parce qu'une réplication est activée : il faut démontrer qu'aucune écriture confirmée n'est perdue dans les scénarios couverts.

### 5.3 Distinguer les objectifs

| Terme | Question |
|---|---|
| RTO | Dans quel délai le service doit-il être rétabli ? |
| RPO | Jusqu'à quel point dans le temps les données doivent-elles être récupérables ? |
| DMIA / MTPD | Quelle durée d'interruption l'activité peut-elle tolérer au maximum ? |
| Délai de restauration | Combien de temps la récupération technique prend-elle réellement ? |
| Délai de validation | Combien de temps faut-il pour confirmer que le service est fiable ? |

La DMIA est la durée maximale d'interruption admissible pour l'activité. Il est dangereux de choisir un RTO égal à cette durée sans prévoir de marge.

### 5.4 Exemple de calcul du temps de reprise

Supposons le scénario suivant :

| Étape | Durée estimée |
|---|---:|
| Détection et qualification | 5 min |
| Décision d'activation du PRA | 5 min |
| Préparation de l'environnement cible | 10 min |
| Récupération des données | 20 min |
| Démarrage des applications | 10 min |
| Validation fonctionnelle | 10 min |
| Total | 60 min |

Ce tableau est un exemple.

Il faut mesurer les temps réels et vérifier que les opérations ne se chevauchent pas de manière incorrecte.

La reprise doit respecter les dépendances. Il ne suffit pas d'additionner des durées si certaines étapes doivent impérativement se dérouler dans un ordre précis.

### 5.5 Les objectifs doivent être approuvés

Le responsable technique peut estimer le temps nécessaire à une opération, mais c'est généralement l'organisation qui doit décider de la durée d'interruption acceptable.

Un RTO de cinq minutes peut exiger une infrastructure coûteuse. Un RPO de zéro peut demander une réplication fortement contrainte et une architecture applicative adaptée.

La stratégie doit donc concilier :

- Besoin métier.
- Coût.
- Risque.
- Niveau de complexité.
- Capacité d'exploitation.
- Exigences de sécurité.

## 6. Définir les niveaux de criticité

### 6.1 Classer les services

Une classification permet d'attribuer des objectifs de reprise différents aux services.

Exemple de classification :

**Niveau 1 — Critique**

Interruption très coûteuse. Les services doivent être repris rapidement, avec une perte de données très faible selon les besoins métier.

**Niveau 2 — Important**

L'interruption est acceptable pour une période limitée. Une réplication ou une sauvegarde fréquente peut être adaptée.

**Niveau 3 — Standard**

Le service peut être restauré avec une priorité plus faible.

**Niveau 4 — Non critique**

Le service peut être reconstruit ou restauré après les systèmes prioritaires.

Ces niveaux ne sont pas une norme universelle. Ils doivent être définis par l'organisation.

### 6.2 Exemple de matrice de reprise

| Service | Criticité | RTO cible | RPO cible | Stratégie indicative |
|---|---|---:|---:|---|
| Commandes | Critique | 30 min | 5 min | Réplication et sauvegarde |
| Base de données métier | Critique | 30 min | 5 min | Réplication native adaptée et sauvegarde |
| Portail interne | Important | 2 h | 30 min | Reconstruction ou réplication selon les besoins |
| Serveur de fichiers | Important | 4 h | 1 h | Sauvegarde fréquente et stockage de secours |
| Environnement de test | Standard | 24 h | 24 h | Reconstruction depuis des modèles |

Les méthodes retenues doivent être validées par des tests.

### 6.3 Ne pas rendre chaque système « critique »

Si chaque application reçoit une priorité maximale, l'organisation ne dispose plus d'une règle de priorisation exploitable.

Le classement doit permettre d'arbitrer lorsqu'il n'est pas possible de reprendre tous les services simultanément.

Il faut également prévoir des dépendances communes : une application de priorité 1 peut dépendre d'un service d'identité qui doit lui-même être classé comme prioritaire.

## 7. Choisir une stratégie de reprise

### 7.1 Site de secours à froid

Un site de secours à froid dispose principalement de l'infrastructure ou des capacités nécessaires pour reconstruire les systèmes.

Il peut nécessiter :

- L'installation des serveurs.
- Le déploiement des systèmes d'exploitation.
- La restauration des données.
- La reconfiguration du réseau.
- Le démarrage des applications.

Avantages :

- Coût souvent plus faible.
- Moins de composants actifs à maintenir.
- Possibilité de reconstruire depuis des modèles validés.

Inconvénients :

- Temps de reprise potentiellement long.
- Dépendance à la disponibilité des équipes et du matériel.
- Temps important de restauration et de validation.

### 7.2 Site de secours tiède

Un site tiède dispose déjà d'une partie des ressources préparées.

Il peut comprendre :

- Des serveurs prêts à être utilisés.
- Des systèmes configurés.
- Des copies de données.
- Une connectivité préparée.
- Des procédures d'activation.

Le site n'est pas nécessairement en mesure de prendre immédiatement toute la charge de production.

Il faut vérifier la capacité et le niveau de mise à jour des systèmes avant de compter sur cette stratégie.

### 7.3 Site de secours chaud

Un site chaud maintient un environnement opérationnel ou presque opérationnel, avec les ressources et les données nécessaires à une reprise rapide.

Il peut inclure :

- Une réplication des machines virtuelles.
- Une réplication de la base de données.
- Une configuration de réseau préparée.
- Des services d'infrastructure disponibles.
- Des procédures de basculement testées.

Il nécessite davantage de ressources, de supervision et de maintenance.

Un site chaud n'est pas automatiquement un site capable de résister à une attaque : sa proximité logique ou ses accès administratifs peuvent constituer des risques communs.

### 7.4 Comparaison

| Critère | Froid | Tiède | Chaud |
|---|---|---|---|
| Coût de maintien | Souvent faible | Moyen | Souvent élevé |
| Préparation technique | Limitée | Partielle | Avancée |
| Délai de reprise | Généralement plus long | Intermédiaire | Généralement plus court |
| Ressources immédiatement disponibles | Peu nombreuses | Partiellement disponibles | Plus largement disponibles |
| Besoin de tests | Élevé | Élevé | Élevé |
| Risque de dépendance à la réplication | Faible à modéré | Variable | Souvent plus élevé |

Un site chaud doit malgré tout conserver des sauvegardes indépendantes.

### 7.5 Actif-passif et actif-actif

**Actif-passif**

Le site principal traite le trafic. Le site secondaire est préparé pour reprendre le service.

**Actif-actif**

Plusieurs sites traitent simultanément le trafic ou les charges, avec une architecture qui permet de répartir les requêtes ou les utilisateurs.

L'actif-actif peut améliorer l'utilisation des ressources et la continuité, mais il peut aussi compliquer :

- La cohérence des données.
- Le routage.
- Les sessions utilisateurs.
- Les transactions.
- La résolution des conflits.
- Le diagnostic des incidents.

Il ne faut pas choisir l'actif-actif simplement parce qu'il paraît plus avancé.

## 8. Architecture d'un PRA pour une infrastructure Linux

### 8.1 Le site principal

Le site principal peut utiliser :

- Keepalived pour les VIP locales.
- HAProxy pour l'équilibrage de charge.
- Pacemaker pour les ressources critiques.
- Corosync pour la communication du cluster.
- DRBD ou un mécanisme applicatif pour certaines réplications.
- Un stockage local ou partagé adapté.
- Une infrastructure de sauvegarde.

Il est important de distinguer le rôle du cluster local de celui de la reprise intersite.

### 8.2 Le site secondaire

Le site secondaire doit pouvoir fonctionner sans dépendre exclusivement des composants détruits du site principal.

Il faut examiner :

- Les chemins réseau.
- Les VLAN et les plages IP.
- Le DNS.
- Les certificats TLS.
- Les systèmes d'authentification.
- Les comptes d'administration.
- Le stockage.
- Les logiciels et leurs licences.
- Les secrets nécessaires.
- Les sauvegardes et les procédures de restauration.

Si le site secondaire dépend d'un serveur DNS qui se trouve uniquement sur le site principal, sa capacité à reprendre les services peut être compromise.

### 8.3 Schéma d'architecture

```text
                           UTILISATEURS
                                |
                                v
                     MÉCANISME D'ACCÈS
                     DNS / routage / VIP
                                |
                 +--------------+--------------+
                 |                             |
                 v                             v
          SITE PRINCIPAL                SITE SECONDAIRE
          ---------------                --------------
          HAProxy / VIP                  HAProxy / VIP
          Applications                  Applications de secours
          Base de données               Copie de données
          Stockage                      Stockage cible
          Cluster local                 Ressources de reprise
                 |                             ^
                 |                             |
                 +------- Réplication --------+
                                |
                                v
                       CONTRÔLES DE SANTÉ


                 INFRASTRUCTURE DE SAUVEGARDE
                 ----------------------------
                 Copies protégées
                 Copies hors site
                 Copies immuables ou hors ligne
                 Procédures de restauration
```

Les mécanismes de réplication, de routage et d'activation doivent être adaptés aux objectifs et au type de service.

### 8.4 La VIP locale ne suffit pas pour un PRA intersite

VRRP est couramment employé pour gérer une VIP sur un même segment réseau ou dans une architecture réseau explicitement adaptée à ce protocole.

Il ne faut pas supposer qu'une VIP Keepalived peut être déplacée simplement d'un site géographique à l'autre.

Les deux sites peuvent utiliser des sous-réseaux différents, séparés par des routeurs et des pare-feu.

Pour une reprise intersite, il faut plutôt examiner les mécanismes appropriés :

- Basculement DNS avec des procédures et des délais documentés.
- Routage contrôlé.
- Annonce de préfixes lorsque l'organisation maîtrise ce mécanisme.
- Publication de services via une infrastructure d'accès adaptée.
- Mise à jour des règles réseau.
- Modification contrôlée des points d'accès clients.

Une modification DNS ne sera pas nécessairement visible immédiatement par tous les clients, notamment à cause des caches et des TTL.

### 8.5 Éviter les dépendances croisées

Le site de secours ne devrait pas nécessiter en permanence des composants critiques du site principal dont la perte doit être couverte.

Exemple de dépendance problématique :

```text
Site principal indisponible
        |
        v
DNS principal indisponible
        |
        v
Site de secours impossible à joindre par son nom
        |
        v
Reprise retardée
```

Une architecture de PRA doit prévoir les services d'infrastructure nécessaires à son activation.

## 9. Stratégie de sauvegarde

### 9.1 La sauvegarde est une fonction critique

La sauvegarde ne consiste pas uniquement à copier des fichiers.

Elle doit permettre de récupérer des données connues, cohérentes et exploitables après un incident.

Les risques à considérer comprennent :

- La suppression accidentelle.
- La corruption logique.
- La panne du stockage.
- Le rançongiciel.
- La compromission d'un compte administrateur.
- La suppression malveillante des sauvegardes.
- La perte de l'infrastructure de production.
- L'indisponibilité du serveur de sauvegarde.

L'ANSSI recommande de formaliser les procédures de sauvegarde et de restauration, de protéger les sauvegardes et de tester régulièrement leur restauration. Son guide consacré à la sauvegarde des systèmes d'information détaille notamment la séparation des rôles, la protection des copies et l'ordre de restauration. [ANSSI — Sauvegarde des systèmes d'information](https://messervices.cyber.gouv.fr/guides/sauvegarde-des-systemes-dinformation)

### 9.2 Règle 3-2-1

Une méthode courante consiste à conserver :

- Trois copies des données, en comptant la donnée de production.
- Deux supports ou modalités de stockage distincts.
- Une copie hors ligne ou autrement isolée.

Cette approche réduit le risque de perdre toutes les copies lors d'une même panne.

La règle doit cependant être adaptée au contexte : trois copies accessibles avec le même compte administrateur peuvent rester vulnérables au même incident.

### 9.3 Ajouter l'isolation et la vérification

Pour renforcer l'approche :

- Conserve une copie hors ligne ou immuable lorsque cela est possible.
- Protège les comptes d'administration de la sauvegarde.
- Sépare les permissions d'exploitation et d'administration avancée.
- Contrôle l'intégrité des sauvegardes.
- Effectue des restaurations de test.
- Protège les journaux et les configurations de sauvegarde.
- Vérifie que les sauvegardes couvrent les dépendances critiques.

Une copie immuable doit être protégée contre les modifications ou suppressions non autorisées pendant sa période de rétention, selon les capacités du système utilisé.

### 9.4 Exemple d'architecture de sauvegarde

```text
DONNÉES DE PRODUCTION
        |
        v
Sauvegarde locale rapide
        |
        v
Copie secondaire hors site
        |
        v
Copie immuable ou hors ligne
        |
        v
Contrôle périodique de restauration
```

Les copies ne doivent pas toutes dépendre du même compte privilégié ni du même environnement de gestion.

### 9.5 Sauvegarder les données et les configurations

Un PRA doit prévoir la protection des données métier, mais aussi des composants nécessaires à la reconstruction.

Il peut s'agir de :

- Configurations des serveurs.
- Fichiers de configuration réseau.
- Définitions des ressources Pacemaker.
- Configuration Keepalived et HAProxy.
- Paramètres de stockage.
- Configurations DNS.
- Certificats et secrets, protégés selon leur sensibilité.
- Scripts d'automatisation.
- Images système de référence.
- Dépendances logicielles.
- Documentation des procédures.

Une sauvegarde de fichiers ne suffit pas toujours pour reconstruire rapidement un service si ses dépendances et sa configuration ne sont pas documentées.

### 9.6 Contrôler la qualité des sauvegardes

Un journal indiquant « sauvegarde réussie » ne prouve pas que la restauration fonctionne.

Il faut notamment vérifier :

- La présence de la copie.
- La taille attendue.
- L'intégrité du contenu.
- La disponibilité de la clé de chiffrement si nécessaire.
- L'accès aux logiciels requis pour restaurer.
- La cohérence des données.
- La capacité de restauration vers un environnement propre.
- La durée réelle de restauration.

Pour une base de données, il faut vérifier qu'elle peut être restaurée et ouverte correctement, et pas seulement que le fichier de sauvegarde existe.

### 9.7 Tester les restaurations

Un plan de restauration doit préciser :

1. Quelle copie choisir.
2. Comment vérifier son intégrité.
3. Où restaurer les données.
4. Comment éviter d'écraser les données de production.
5. Comment contrôler la cohérence.
6. Comment valider l'application.
7. Comment documenter le résultat.

Il est recommandé de pratiquer les tests de restauration au minimum selon la fréquence définie par la politique de sécurité applicable et les exigences de l'organisation.

En l'absence de contraintes plus exigeantes, une vérification régulière planifiée, au moins annuelle, constitue un point de départ ; pour des services critiques, la fréquence doit être plus élevée.

### 9.8 Les sauvegardes doivent résister aux incidents de cybersécurité

Dans le cas d'un rançongiciel, il faut éviter de restaurer immédiatement un système potentiellement compromis dans un réseau encore infecté.

Le processus doit inclure une évaluation de l'incident, l'isolement des systèmes affectés et la préparation d'un environnement de reprise propre.

CISA recommande notamment de conserver des sauvegardes hors ligne et chiffrées, de tester leur disponibilité et leur intégrité et de reconstruire les systèmes touchés à partir d'images fiables lorsque c'est approprié. [CISA — StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide)

## 10. Sauvegarde, réplication et restauration : trois objectifs différents

### 10.1 Réplication

La réplication maintient une copie des données ou de l'état d'un système sur un autre emplacement.

Elle peut réduire le temps de reprise.

Cependant, selon la technologie, elle peut aussi répliquer des modifications indésirables, une corruption logique ou des suppressions.

### 10.2 Sauvegarde

La sauvegarde conserve des points de récupération permettant de retrouver un état antérieur.

Elle est essentielle pour récupérer des données supprimées ou corrompues, si un point de récupération sain existe.

### 10.3 Restauration

La restauration est l'opération consistant à récupérer des données et des systèmes à partir d'une copie ou d'un point de récupération.

La durée dépend de la taille des données, de la bande passante, de l'emplacement, du système de stockage et des vérifications nécessaires.

### 10.4 Comparaison

| Mécanisme | Fonction principale | Limite importante |
|---|---|---|
| Keepalived / VRRP | Déplacer une adresse virtuelle | Ne copie pas les données |
| Pacemaker | Gérer des ressources et leur reprise | Ne remplace pas une sauvegarde |
| DRBD | Répliquer des blocs de stockage | Peut propager une corruption logique |
| Réplication de base de données | Maintenir une copie de données transactionnelles | Dépend du moteur et du mode de réplication |
| Sauvegarde | Conserver des points de restauration | La restauration peut prendre du temps |
| Image système | Faciliter la reconstruction d'un environnement | Doit être maintenue et vérifiée |
| Réplication intersite | Maintenir des données ou services sur un autre site | Peut partager des risques de sécurité avec la production |

Un PRA robuste choisit chaque mécanisme selon sa fonction.

## 11. L'ordre de restauration des systèmes

### 11.1 Pourquoi l'ordre est important

Une application peut dépendre d'un ensemble de services.

Si tu démarres le serveur Web avant la base de données, le site peut être accessible tout en affichant des erreurs.

Si l'authentification n'est pas disponible, les utilisateurs peuvent ne pas réussir à se connecter.

L'ordre de récupération doit suivre les dépendances réelles.

### 11.2 Exemple de séquence

```text
PHASE 1 : ENVIRONNEMENT
|
+-- Électricité et connectivité
+-- Stockage disponible
+-- Hyperviseur ou serveurs de secours
|
v
PHASE 2 : SERVICES D'INFRASTRUCTURE
|
+-- DNS
+-- Synchronisation de l'heure
+-- Identité / authentification
+-- Services réseau nécessaires
|
v
PHASE 3 : DONNÉES
|
+-- Vérification du stockage
+-- Récupération ou promotion des copies
+-- Contrôle de cohérence des bases
|
v
PHASE 4 : APPLICATIONS
|
+-- Services applicatifs
+-- API
+-- Serveurs Web
|
v
PHASE 5 : ACCÈS CLIENTS
|
+-- VIP / routage / DNS
+-- Tests fonctionnels
+-- Réouverture aux utilisateurs
```

Cet ordre est un exemple, pas une règle universelle. Il faut l'adapter aux dépendances de chaque application.

### 11.3 Services souvent oubliés

Les équipes concentrent souvent leur attention sur les applications, mais oublient des composants nécessaires à leur démarrage.

Exemples :

- DNS.
- Synchronisation NTP.
- Certificats TLS.
- Gestion des secrets.
- Authentification.
- Dépôts logiciels.
- Proxy.
- Services de licence.
- Résolution des noms internes.
- Supervision.
- Journalisation.
- Accès aux sauvegardes.

Ces services doivent être recensés dans le PRA.

### 11.4 Construire une matrice de dépendances

| Service | Dépendances | Priorité de reprise |
|---|---|---|
| DNS de secours | Réseau, système de noms | Très élevée |
| Base de données | Stockage, configuration, cohérence | Très élevée |
| API métier | Base de données, authentification | Élevée |
| Serveur Web | API, réseau, certificats | Élevée |
| Portail documentaire | Stockage, authentification | Selon besoin métier |
| Environnement de test | Ressources de développement | Plus faible |

La priorité de reprise est déterminée par l'activité métier et les dépendances, pas uniquement par la facilité technique du redémarrage.

## 12. Intégrer Pacemaker dans un PRA

### 12.1 Le cluster local ne remplace pas le site de secours

Pacemaker est conçu pour gérer les ressources du cluster selon les nœuds, la communication, le quorum et les contraintes configurées.

Si tous les nœuds sont dans le même bâtiment et que le bâtiment devient indisponible, le cluster peut être perdu.

Il faut donc distinguer :

- Le basculement local.
- Le basculement vers une infrastructure distincte.
- La restauration après perte complète des systèmes.
- La reprise après une compromission de sécurité.

### 12.2 Que faut-il conserver ?

Pour permettre une reconstruction ou une reprise, conserve de manière sécurisée :

- La configuration du cluster.
- Les définitions des ressources.
- Les contraintes.
- Les agents nécessaires.
- Les informations réseau.
- Les paramètres de quorum.
- La configuration de fencing.
- Les dépendances des applications.
- Les procédures d'exploitation.
- Les informations de connexion au stockage.
- Les clés et secrets nécessaires, protégés séparément.

Les sauvegardes de configuration doivent être cohérentes avec la version de Pacemaker et les agents effectivement utilisés.

### 12.3 Reprise des ressources

Après un sinistre, il ne faut pas supposer que l'ancienne configuration du cluster peut être appliquée sans modification sur une nouvelle infrastructure.

Le site de secours peut avoir :

- Des adresses différentes.
- Des interfaces différentes.
- Des noms de nœuds différents.
- Un autre stockage.
- Une autre topologie réseau.
- Des règles de sécurité différentes.
- Des dépendances qui ne sont pas présentes sur le site principal.

La configuration doit donc être préparée et testée pour les conditions réelles de la reprise.

### 12.4 Fencing et reprise après sinistre

Si le site principal est partiellement accessible et que le site de secours est activé, il faut empêcher un retour inattendu du site principal d'écrire simultanément sur les mêmes ressources.

Les procédures de basculement doivent déterminer :

- Qui possède l'autorité de décision.
- Quel site est autorisé à servir les clients.
- Quel site est autorisé à écrire les données.
- Comment l'ancien site est isolé.
- Comment le retour est préparé et validé.

Une reprise intersite ne doit pas se limiter au lancement du cluster secondaire.

### 12.5 Vérifier avant d'activer

Avant une activation automatique ou manuelle du site de secours, il faut déterminer si le site principal est réellement indisponible ou simplement isolé du réseau de contrôle.

Une erreur de diagnostic pourrait entraîner deux sites actifs simultanément alors qu'ils sont censés se partager une même ressource de données.

Selon l'architecture, ce problème peut nécessiter des mécanismes de quorum intersite, une autorité d'activation clairement définie et une isolation fiable.

## 13. Intégrer Keepalived et HAProxy dans un PRA

### 13.1 Rôle local de Keepalived

Keepalived peut déplacer une VIP entre les nœuds qui participent à l'instance VRRP.

Cela permet de protéger un point d'entrée dans le réseau prévu par l'architecture.

### 13.2 Rôle local de HAProxy

HAProxy distribue les requêtes vers les backends disponibles selon ses contrôles de santé et ses règles.

Il peut détecter qu'une application ne répond plus et éviter de lui envoyer de nouvelles requêtes, selon sa configuration.

### 13.3 Limites intersites

Le basculement d'une VIP locale ne suffit pas pour faire accéder les clients à une nouvelle région réseau.

Il faut prévoir comment les clients trouveront le service du site de secours.

Les mécanismes peuvent inclure :

- Mise à jour d'un enregistrement DNS.
- Modifications contrôlées du routage.
- Mise à jour d'un point d'accès global.
- Réorientation des clients via une infrastructure dédiée.
- Modification des règles de publication.

Le délai de convergence doit être mesuré.

### 13.4 Ne pas automatiser un basculement intersite sans stratégie de cohérence

Un basculement automatique intersite peut être dangereux si le site principal n'est pas réellement arrêté ou si les données du site secondaire sont en retard.

Il faut définir les critères d'autorisation du basculement, la gestion du site isolé, les règles d'écriture et la procédure de retour.

La disponibilité du réseau ne doit pas être le seul critère de décision.

## 14. Reprise des bases de données

### 14.1 Pourquoi la base de données est souvent centrale

Une application peut être réinstallée rapidement, mais ses données métier sont souvent plus difficiles à reconstruire.

La reprise doit tenir compte des transactions, de la cohérence, des dépendances applicatives et du mode de réplication.

### 14.2 Méthodes de protection

Selon le moteur, les solutions peuvent comprendre :

- Sauvegardes complètes.
- Sauvegardes incrémentales.
- Journaux transactionnels.
- Réplication asynchrone.
- Réplication synchrone.
- Réplication native avec promotion contrôlée.
- Export logique.
- Sauvegarde physique cohérente.
- Restauration à un instant précis lorsque le moteur et la chaîne de sauvegarde le permettent.

Le choix dépend du volume, de la charge, de la latence et du RPO.

### 14.3 PostgreSQL : sauvegarde logique d'exemple

Pour une base PostgreSQL, `pg_dump` peut produire une sauvegarde logique.

Exemple à adapter :

```bash
pg_dump \
    --format=custom \
    --file=/backup/gestion.dump \
    gestion
```

Cette commande suppose que le compte exécutant la sauvegarde possède les permissions nécessaires et que le répertoire de destination existe.

Il faut également définir la gestion des identifiants, des journaux, du code de sortie, de la rétention et du transfert sécurisé.

### 14.4 Vérifier l'archive

Une commande telle que :

```bash
pg_restore --list /backup/gestion.dump
```

permet d'examiner le contenu de l'archive.

Cela ne prouve pas que la restauration complète réussira.

La preuve la plus utile consiste à restaurer la sauvegarde dans une instance de test isolée, à vérifier son intégrité et à exécuter des contrôles applicatifs.

### 14.5 Restaurer dans un environnement isolé

Une restauration de test doit éviter d'écraser la production.

Procédure générale :

1. Préparer une instance de test.
2. Vérifier la version du moteur.
3. Récupérer une sauvegarde connue.
4. Vérifier l'intégrité de l'archive.
5. Restaurer dans une base distincte.
6. Vérifier le schéma.
7. Exécuter des contrôles sur les données.
8. Faire valider le résultat par le propriétaire métier.
9. Mesurer le temps de restauration.
10. Documenter le résultat.

La procédure de production doit ensuite utiliser la méthode adaptée au moteur, à la taille de la base et aux contraintes métier.

### 14.6 Promotion d'une réplique

Si une base de données possède une réplique secondaire, la promotion doit suivre la procédure officielle du moteur.

Il faut notamment vérifier :

- Le retard de réplication.
- Le dernier point cohérent.
- Le risque de perte de données.
- L'état du serveur primaire.
- L'unicité du primaire autorisé à écrire.
- Le comportement des applications.
- Le changement de point d'accès.
- Le suivi de la nouvelle topologie.

Une promotion irréfléchie peut entraîner deux instances acceptant des écritures divergentes.

## 15. PRA après cyberattaque ou rançongiciel

### 15.1 Le sinistre cyber est différent d'une panne matérielle

Une panne de serveur n'implique pas nécessairement que les systèmes restants soient compromis.

Après une cyberattaque, la cause de l'indisponibilité peut encore être présente :

- Compte administrateur compromis.
- Maliciel persistant.
- Identifiants volés.
- Serveur de gestion compromis.
- Sauvegardes altérées.
- Scripts de déploiement malveillants.
- Clés ou certificats compromis.

Dans ce contexte, rallumer les anciens serveurs ou restaurer immédiatement les données dans le réseau habituel peut réintroduire la compromission.

### 15.2 La priorité est de maîtriser l'incident

Le PRA cyber doit se coordonner avec le plan de réponse à incident.

Les étapes comprennent notamment :

1. Détecter et qualifier l'incident.
2. Isoler les systèmes touchés selon la procédure de crise.
3. Préserver les éléments nécessaires à l'investigation.
4. Déterminer le périmètre de compromission.
5. Protéger les sauvegardes encore saines.
6. Préparer un environnement de récupération propre.
7. Reconstruire ou restaurer les systèmes.
8. Réinitialiser ou remplacer les secrets compromis.
9. Vérifier la sécurité avant la reconnexion.
10. Restaurer progressivement les services.

Il ne faut pas supprimer les éléments utiles à l'enquête sans coordination avec l'équipe de réponse à incident.

### 15.3 Environnement de reprise propre

Un environnement de reprise propre, parfois appelé *clean room*, isole les opérations de reconstruction des systèmes susceptibles d'être compromis.

Il peut comprendre :

- Un réseau distinct.
- Des systèmes d'administration propres.
- Des images de système validées.
- Des dépôts logiciels fiables.
- Des comptes dédiés.
- Des outils de vérification.
- Un accès strictement contrôlé aux sauvegardes.

L'objectif est d'éviter de réintroduire un système compromis dans la nouvelle infrastructure.

### 15.4 Pourquoi les sauvegardes hors ligne ou immuables sont essentielles

Un attaquant disposant d'un accès administratif étendu peut tenter de supprimer les copies accessibles par les mêmes identifiants que ceux utilisés en production.

Les sauvegardes doivent donc être protégées par une architecture et des autorisations distinctes.

CISA recommande de conserver des sauvegardes hors ligne et chiffrées, et de tester leur intégrité ainsi que leur disponibilité dans un scénario de reprise. [CISA — StopRansomware](https://www.cisa.gov/stopransomware/ransomware-guide)

L'ANSSI recommande également de protéger les sauvegardes contre les incidents qui pourraient les rendre inexploitables. [ANSSI — Fondamentaux de la sauvegarde](https://messervices.cyber.gouv.fr/documents-guides/anssi-fondamentaux-sauvegarde_systemes_dinformation_v1-0.pdf)

### 15.5 Reconstituer la confiance

Après une compromission, il ne suffit pas de restaurer un serveur.

Il faut déterminer si les identifiants, les clés, les certificats et les systèmes de gestion doivent être remplacés.

La reprise peut nécessiter :

- La réinitialisation de certains secrets.
- La création de comptes administratifs propres.
- L'invalidation de sessions ou de jetons.
- La rotation des clés.
- La reconstruction des serveurs de gestion.
- La mise à jour des systèmes.
- L'examen des journaux de sécurité.
- La vérification des droits et des configurations.

Cette étape doit être coordonnée avec l'équipe de sécurité.

### 15.6 Validation avant reconnexion

Avant de réintroduire un service restauré dans le réseau de production, vérifie :

- L'origine de l'image ou de la sauvegarde.
- L'absence de compromission connue dans l'environnement de restauration.
- Les mises à jour de sécurité.
- Les comptes et permissions.
- Les secrets utilisés.
- Les règles réseau.
- Les journaux.
- Les contrôles fonctionnels.
- Les critères d'autorisation de reconnexion.

La vitesse ne doit pas conduire à rétablir une infection dans un environnement reconstruit.

Documentation : [NIST — Incident Response](https://csrc.nist.gov/projects/incident-response).

## 16. Autorité de décision et gestion de crise

### 16.1 Les décisions ne sont pas uniquement techniques

Un basculement peut modifier la cohérence des données, le périmètre de service et la capacité disponible.

Dans certains scénarios, les équipes techniques ne doivent pas activer le site secondaire sans approbation de l'autorité prévue par la procédure.

Le PRA doit préciser qui possède cette responsabilité.

### 16.2 Définir les rôles

Une organisation peut attribuer des responsabilités à :

- Direction ou autorité de crise.
- Responsable informatique.
- Responsable sécurité.
- Équipe systèmes.
- Équipe réseau.
- Équipe base de données.
- Responsables applicatifs.
- Responsables métier.
- Communication interne.
- Fournisseurs ou prestataires.

### 16.3 Exemple de matrice RACI

RACI signifie :

- **R — Responsible** : réalise l'action.
- **A — Accountable** : porte la responsabilité finale.
- **C — Consulted** : est consulté.
- **I — Informed** : est informé.

Exemple :

| Action | Direction | IT | Sécurité | Métier |
|---|---|---|---|---|
| Déclarer la crise | A | C | C | I |
| Évaluer l'infrastructure | I | R/A | C | I |
| Confirmer une compromission | I | C | R/A | I |
| Autoriser le basculement intersite | A | R | C | C |
| Valider les données métier | I | C | I | R/A |
| Autoriser le retour nominal | A | R | C | C |

Cette matrice est illustrative. Elle doit être adaptée à l'organisation et aux responsabilités réelles.

### 16.4 Journal de crise

Toutes les actions importantes doivent être consignées.

Exemple :

```text
Date / heure :
Identifiant de l'incident :
Personne ayant effectué l'action :
Action ou décision :
Motif :
Impact estimé :
Résultat :
Prochaine étape :
```

Le journal permet de reconstruire la chronologie, de coordonner les équipes et de faciliter le retour d'expérience.

### 16.5 Éviter les décisions contradictoires

Dans une crise, différentes équipes peuvent être tentées de résoudre le problème chacune de leur côté.

Une équipe réseau peut modifier le routage tandis qu'une autre active le site de secours. Une équipe base de données peut promouvoir une réplique sans connaître l'état du site principal.

Le PRA doit prévoir une autorité de coordination et un canal de communication adapté.

## 17. Procédure d'activation du PRA

### 17.1 Critères d'activation

Le plan doit définir les conditions qui justifient son activation.

Exemples :

- Perte complète du site principal.
- Durée de panne dépassant le seuil fixé par l'organisation.
- Perte durable du stockage de production.
- Indisponibilité des services essentiels sans solution de contournement.
- Incident de sécurité imposant une reconstruction.
- Décision formelle de l'autorité de crise.

Les critères doivent être explicites et documentés.

### 17.2 Phases de l'activation

```text
Incident détecté
        |
        v
Qualification de l'incident
        |
        v
Évaluation du périmètre
        |
        v
Décision d'activation du PRA
        |
        v
Confinement et protection des données
        |
        v
Préparation du site cible
        |
        v
Récupération des données
        |
        v
Démarrage des services
        |
        v
Validation technique et métier
        |
        v
Réouverture contrôlée
```

L'ordre peut différer dans un incident de cybersécurité. La protection des preuves et le confinement peuvent être prioritaires sur la restauration.

### 17.3 Liste de contrôle d'activation

Avant de déclencher une reprise intersite, vérifie :

- Le périmètre de l'incident est identifié.
- L'état du site principal est connu autant que possible.
- L'autorité d'activation a été identifiée.
- Les risques de double écriture ont été évalués.
- Le site secondaire dispose des ressources nécessaires.
- Le stockage est disponible.
- Les données sont suffisamment récentes.
- Les dépendances sont identifiées.
- Les accès administratifs fonctionnent.
- Les contrôles de sécurité sont prévus.
- Les utilisateurs et responsables métier sont informés selon le plan.

## 18. Runbook de reprise : exemple opérationnel

Un runbook est une procédure d'exploitation détaillée qui indique quoi vérifier, quoi exécuter et comment savoir si chaque étape a réussi.

Le plan doit être suffisamment clair pour être utilisé par une équipe autorisée pendant une crise.

### 18.1 Fiche du service

Exemple pour un service Web critique :

```text
Service :
  Portail de commande

Responsable métier :
  Responsable des opérations

Responsable technique :
  Équipe systèmes

Site principal :
  SITE-A

Site de secours :
  SITE-B

RTO cible :
  30 minutes

RPO cible :
  5 minutes

Point d'accès nominal :
  commandes.exemple.internal

Point d'accès de secours :
  Défini dans le plan réseau de reprise

Base de données :
  PostgreSQL, selon la configuration de production

Dépendances :
  DNS, authentification, base de données,
  réseau applicatif, certificats TLS

Autorité d'activation :
  Selon la matrice de crise approuvée
```

Les adresses, les comptes et les informations confidentielles doivent être conservés dans un espace documentaire protégé, avec un accès prévu même lorsque les systèmes de production sont indisponibles.

### 18.2 Étape 1 — Évaluer l'état

Collecte les informations disponibles sur :

- Les nœuds.
- Le stockage.
- Les réseaux.
- La base de données.
- Les sauvegardes.
- La réplication.
- Les journaux.
- Les changements récents.

Ne lance pas une récupération destructive tant que le bon point de reprise n'a pas été identifié.

### 18.3 Étape 2 — Préparer l'environnement de secours

Vérifie :

- Les ressources matérielles.
- La capacité de calcul.
- La mémoire.
- Le stockage.
- Le réseau.
- Les VLAN.
- Le DNS.
- Les règles d'accès.
- Les certificats et secrets.
- Les outils de gestion.

Les configurations doivent correspondre à l'état réellement disponible sur le site de secours.

### 18.4 Étape 3 — Vérifier les données

Pour une application répliquée, contrôle le statut de la réplication et le point de cohérence.

Pour une sauvegarde, contrôle la date, l'intégrité, l'origine et les conditions de restauration.

Les données doivent être cohérentes avant d'autoriser l'écriture en production sur le site de secours.

### 18.5 Étape 4 — Démarrer les dépendances

Démarre les ressources dans l'ordre documenté.

Exemple :

```text
Stockage disponible
        |
        v
Base de données
        |
        v
Services applicatifs
        |
        v
HAProxy / serveur Web
        |
        v
Accès utilisateurs
```

Cet ordre doit être ajusté aux besoins de l'application.

### 18.6 Étape 5 — Contrôler les services

Sur une application Web, un contrôle HTTP peut aider à confirmer que l'endpoint répond.

Exemple :

```bash
curl --fail \
     --silent \
     --show-error \
     --max-time 5 \
     https://service-secours.exemple.internal/healthz
```

Le domaine est fictif et doit être remplacé par le point de contrôle autorisé.

Ce test permet d'obtenir un indice technique. Il ne remplace pas la validation fonctionnelle de l'application, des transactions et des données.

### 18.7 Étape 6 — Valider l'accès

Vérifie :

- La résolution DNS.
- La connectivité réseau.
- L'authentification.
- Le certificat TLS.
- L'accès à la base de données.
- Les opérations applicatives critiques.
- La cohérence des données.
- L'accès depuis un client représentatif.

La reprise doit être confirmée par les responsables techniques et métier selon le plan.

### 18.8 Étape 7 — Ouvrir le service

La réouverture peut se faire progressivement.

Il est possible de :

- Commencer par un groupe pilote.
- Valider les transactions.
- Surveiller la charge.
- Contrôler les erreurs.
- Étendre l'accès.
- Informer les utilisateurs.

Le point d'entrée ne doit être réorienté vers le site de secours qu'une fois que celui-ci satisfait les critères prévus.

## 19. Contrôles techniques après restauration

### 19.1 Systèmes

Vérifie :

- L'état du système d'exploitation.
- Les systèmes de fichiers.
- L'espace disque.
- Les services.
- Les permissions.
- Les paquets nécessaires.
- Les journaux.
- Les mises à jour.
- Les erreurs de démarrage.

Commandes Linux utiles :

```bash
uptime
df -h
free -h
systemctl --failed
journalctl -p err -b
```

Ces commandes donnent une vue ponctuelle. Les résultats doivent être interprétés selon les services concernés.

### 19.2 Réseau

Vérifie :

```bash
ip -br address
ip route
getent hosts service-secours.exemple.internal
```

Puis teste les ports et services attendus.

Un ping réussi n'est pas une preuve que l'application est fonctionnelle.

### 19.3 Keepalived

Dans une architecture utilisant Keepalived :

```bash
sudo systemctl status keepalived
sudo journalctl -u keepalived --no-pager -n 100
ip -br address
```

Vérifie que la VIP se trouve sur le détenteur prévu et qu'elle n'est pas accidentellement portée par plusieurs nœuds.

### 19.4 Pacemaker

Dans une architecture utilisant Pacemaker :

```bash
sudo pcs status --full
sudo corosync-quorumtool -s
```

Vérifie :

- L'état des nœuds.
- Le quorum.
- Les ressources actives.
- Les erreurs.
- Le mécanisme de fencing.
- L'emplacement des rôles.

Ne réactive pas un nœud qui pourrait continuer à écrire sur les données sans avoir validé son état.

### 19.5 DRBD

Si DRBD est utilisé :

```bash
sudo drbdadm status
```

Vérifie le rôle des nœuds, l'état de la connexion et la synchronisation avant de reprendre un service dépendant des données.

N'essaie pas de forcer une promotion sans comprendre l'état des copies et les risques de divergence.

## 20. Failback : revenir au site principal

### 20.1 Pourquoi le retour est risqué

Après un basculement, le site secondaire peut être devenu l'environnement qui accepte les écritures.

Le site principal ancien peut contenir des données plus anciennes ou un état incompatible.

Le retour au site principal doit donc être traité comme une opération distincte, souvent appelée *failback*.

### 20.2 Les phases du retour

```text
Site de secours en service
        |
        v
Inspection du site principal
        |
        v
Réparation et validation
        |
        v
Synchronisation des données
        |
        v
Contrôle de cohérence
        |
        v
Préparation du retour
        |
        v
Basculement planifié
        |
        v
Validation du site principal
        |
        v
Réactivation du mode nominal
```

### 20.3 Ne pas remettre l'ancien site en écriture trop tôt

Si deux sites peuvent modifier les mêmes données indépendamment, le risque de divergence est important.

Il faut définir :

- Le site qui possède l'autorité d'écriture.
- Le mécanisme de resynchronisation.
- La fenêtre de retour.
- Les vérifications de cohérence.
- La décision finale de basculement.
- La surveillance après retour.

### 20.4 Retour vers un cluster Pacemaker

Avant de remettre les ressources sur un nœud ou un site restauré, vérifie :

- L'état des nœuds.
- Le quorum.
- Le fencing.
- L'état du stockage.
- La synchronisation des données.
- Les contraintes de placement.
- La configuration réseau.
- Les agents de ressources.
- Les applications dépendantes.

Le simple retour d'un nœud dans le cluster ne signifie pas que toutes ses données et ressources sont prêtes pour la production.

### 20.5 Retour d'une VIP

Pour Keepalived, le comportement de préemption peut provoquer un retour de la VIP vers un serveur préféré.

Si ce comportement est indésirable pendant une reprise, il faut définir une politique contrôlée de préférence ou de préemption et tester le résultat.

Le retour automatique ne doit pas interrompre inutilement un service qui fonctionne correctement sur le nœud secondaire.

### 20.6 Clôturer le retour

Après le failback :

- Vérifie les services.
- Contrôle les transactions.
- Confirme la cohérence des données.
- Vérifie les sauvegardes.
- Contrôle les journaux.
- Revalide les accès.
- Actualise l'inventaire.
- Documente les écarts.
- Prépare le site secondaire pour le prochain incident.

Le retour nominal doit être confirmé, pas supposé.

## 21. Tests du PRA

### 21.1 Pourquoi tester régulièrement ?

Un PRA qui n'a jamais été testé constitue une hypothèse, pas une preuve de capacité de reprise.

Les tests servent à identifier :

- Les procédures incomplètes.
- Les mots de passe indisponibles.
- Les copies inutilisables.
- Les dépendances oubliées.
- Les délais sous-estimés.
- Les responsabilités ambiguës.
- Les différences entre documentation et réalité.

### 21.2 Niveaux de test

**Revue documentaire**

Vérifier la cohérence des procédures sans exécuter d'opérations techniques risquées.

**Exercice sur table**

Les participants examinent un scénario et expliquent les décisions et actions prévues.

**Test technique isolé**

Tester un composant ou une restauration dans un laboratoire.

**Test de restauration**

Restaurer réellement des données ou une application dans un environnement séparé.

**Test de basculement contrôlé**

Déclencher un changement de rôle dans un périmètre autorisé.

**Exercice de reprise complet**

Exécuter le PRA sur un environnement adapté, avec des objectifs, des rôles et des mesures documentés.

Le niveau de test choisi doit correspondre aux risques, aux objectifs de disponibilité et aux capacités de l'organisation.

### 21.3 Préparer un test

Un test doit définir :

- L'objectif.
- Le scénario.
- Le périmètre.
- Les participants.
- Les prérequis.
- Les risques.
- Les critères de réussite.
- Les conditions d'arrêt.
- Le retour arrière.
- Les données à collecter.
- Les conditions de clôture.

Ne déclenche pas une panne réelle sans procédure approuvée, surveillance et plan de récupération.

### 21.4 Mesurer les résultats

Pour chaque test, consigne :

| Mesure | Objectif |
|---|---|
| Temps de détection | Délai avant reconnaissance de l'incident |
| Temps de décision | Délai avant autorisation du PRA |
| Temps de restauration | Délai de récupération des données et services |
| Temps de validation | Délai avant confirmation de fonctionnement |
| RTO mesuré | Temps réel avant reprise opérationnelle |
| RPO mesuré | Écart de données entre le point d'incident et le point récupéré |
| Résultat fonctionnel | Capacité à réaliser les opérations métier |
| Écarts | Problèmes rencontrés et actions correctives |

Les mesures doivent être conservées afin de comparer les tests successifs.

### 21.5 Tester la restauration d'une sauvegarde

La procédure doit vérifier que la copie permet effectivement de retrouver une donnée cohérente.

Pour une application, cela peut inclure :

- La restauration de ses fichiers.
- La restauration de sa base de données.
- Le redémarrage des services.
- Les contrôles de cohérence.
- Les tests de connexion.
- Une validation métier.

Une sauvegarde simplement présente sur un stockage ne prouve pas que l'application pourra être restaurée.

### 21.6 Après le test : retour d'expérience

Après chaque exercice, documente :

- Les étapes réussies.
- Les étapes échouées.
- Les délais observés.
- Les écarts par rapport aux objectifs.
- Les procédures obsolètes.
- Les droits manquants.
- Les ressources supplémentaires nécessaires.
- Les actions correctives.
- Les responsables et échéances.

Le PRA doit évoluer avec l'infrastructure.

## 22. Construire un dossier PRA professionnel

### 22.1 Structure recommandée

Un dossier PRA peut contenir les éléments suivants :

```text
PRA
|
+-- 01 - Gouvernance et responsabilités
|
+-- 02 - Analyse d'impact métier
|
+-- 03 - Cartographie des services
|
+-- 04 - Scénarios de sinistre
|
+-- 05 - Objectifs RTO et RPO
|
+-- 06 - Architecture de secours
|
+-- 07 - Sauvegarde et restauration
|
+-- 08 - Runbooks techniques
|
+-- 09 - Procédure d'activation
|
+-- 10 - Procédure de failback
|
+-- 11 - Communication de crise
|
+-- 12 - Plan de tests
|
+-- 13 - Résultats et retours d'expérience
|
+-- 14 - Contacts et fournisseurs
|
+-- 15 - Procédures d'urgence
```

Les documents doivent être accessibles même si les services habituels d'identité ou de collaboration sont indisponibles.

### 22.2 Informations sensibles

Le PRA peut contenir des informations sensibles :

- Architecture détaillée.
- Adresses des équipements.
- Informations de récupération.
- Contacts d'urgence.
- Procédures de sécurité.
- Références de comptes.
- Modalités d'accès aux sauvegardes.

Il faut protéger ces informations sans rendre le document impossible à consulter pendant une crise.

Une solution consiste à conserver une copie sécurisée et indépendante, accessible à l'équipe de crise selon des procédures prévues.

### 22.3 Versionner le PRA

Le plan doit indiquer :

- Son propriétaire.
- Sa date de dernière validation.
- La version.
- Les responsables approbateurs.
- Les changements récents.
- Les résultats du dernier test.
- La prochaine date de révision.

Une procédure modifiée sans contrôle de version peut provoquer des erreurs pendant une crise.

### 22.4 Mettre à jour après chaque changement significatif

Le PRA doit être revu après :

- Un changement de réseau.
- Un changement de serveur.
- Une migration de base de données.
- Un changement de stockage.
- Un changement de fournisseur.
- Une modification de sauvegarde.
- L'ajout d'une application critique.
- Un changement de responsable.
- Un test ayant révélé un défaut.

La documentation doit correspondre à l'environnement réel.

## 23. Exercices d'application avec corrigés

### Exercice 1 — Le cluster local est disponible, mais le site est détruit

Une entreprise possède deux nœuds Pacemaker dans le même bâtiment. Un incendie rend la salle informatique inutilisable.

**Question :** le cluster local suffit-il à assurer la reprise ?

**Corrigé :** non. Les deux nœuds partagent le même domaine de panne physique. Il faut une stratégie hors site, avec les données, les ressources, les dépendances et les procédures nécessaires pour rétablir les services.

### Exercice 2 — Le site secondaire n'est pas à jour

Le site secondaire peut démarrer les applications, mais la dernière réplication de la base date de 45 minutes. Le RPO cible est de cinq minutes.

**Question :** peut-on considérer l'objectif respecté ?

**Corrigé :** non. Le point de récupération disponible dépasse la perte de données acceptée. L'équipe doit évaluer les possibilités de récupérer un point plus récent et faire approuver la décision de reprise au regard des conséquences métier. La reprise ne doit pas masquer l'écart au RPO.

### Exercice 3 — Le serveur Web est restauré, mais le DNS est indisponible

Le site de secours fonctionne localement, mais les utilisateurs ne peuvent pas le trouver.

**Question :** que révèle cet incident ?

**Corrigé :** la cartographie des dépendances est incomplète ou la procédure de reprise DNS n'est pas suffisamment préparée. Le PRA doit inclure les services d'infrastructure nécessaires à l'accès aux applications.

### Exercice 4 — DRBD est synchronisé, mais une corruption est détectée

L'application a supprimé des données par erreur. Le même état a été répliqué vers le nœud secondaire.

**Question :** pourquoi la réplication ne résout-elle pas le problème ?

**Corrigé :** DRBD réplique des blocs ; il ne conserve pas automatiquement une version saine de toutes les données précédentes. Il faut récupérer une sauvegarde ou un point de restauration approprié.

### Exercice 5 — Rançongiciel et sauvegarde accessible

Un rançongiciel compromet les serveurs de production et le compte d'administration des sauvegardes.

**Question :** quelle stratégie doit être prévue ?

**Corrigé :** isoler les systèmes concernés, évaluer la compromission, protéger les copies restantes et préparer un environnement de récupération propre. La restauration doit partir de sauvegardes saines, avec les identifiants et les systèmes de gestion nécessaires sécurisés. Il ne faut pas reconnecter aveuglément les systèmes potentiellement compromis.

### Exercice 6 — Les ressources sont restaurées dans le désordre

Le service Web démarre avant sa base de données et échoue pendant plusieurs minutes.

**Question :** quel élément du PRA doit être amélioré ?

**Corrigé :** l'ordre de restauration et les dépendances. Il faut définir les prérequis, l'ordre des opérations, les contrôles et la réaction lorsque la dépendance n'est pas disponible.

### Exercice 7 — Le retour au site principal provoque une divergence

Le site secondaire a accepté des écritures pendant le PRA. Le site principal est ensuite redémarré sans synchronisation complète.

**Question :** quel est le risque ?

**Corrigé :** les deux sites peuvent avoir des états différents. Le retour doit être planifié avec une autorité d'écriture clairement définie, une resynchronisation et un contrôle de cohérence avant de remettre le service sur le site principal.

### Exercice 8 — RTO respecté, service inutilisable

L'équipe a restauré la machine virtuelle en 25 minutes alors que le RTO cible était de 30 minutes, mais les utilisateurs ne peuvent pas effectuer de transactions.

**Question :** peut-on annoncer la réussite du PRA ?

**Corrigé :** non. Le démarrage de la VM ne signifie pas que le service métier est rétabli. Le temps de reprise doit être mesuré jusqu'à la validation fonctionnelle selon les critères convenus.

### Exercice 9 — Le plan n'a pas été révisé après une migration

Le PRA prévoit que les sauvegardes sont accessibles depuis un ancien serveur, supprimé depuis plusieurs mois.

**Question :** quel enseignement en tirer ?

**Corrigé :** le plan ne reflète plus l'infrastructure réelle. Il faut maintenir les procédures à jour et vérifier les prérequis pendant les tests réguliers.

### Exercice 10 — Deux sites restent actifs

Après une coupure réseau, le site secondaire est activé alors que le site principal continue à traiter des transactions.

**Question :** quel élément doit être renforcé ?

**Corrigé :** la décision de basculement, le contrôle de l'état du site principal, la gestion de l'autorité d'écriture et les mécanismes d'isolation ou d'arbitrage doivent être revus. Un basculement intersite nécessite une stratégie qui prévient les doubles écritures incompatibles.

## 24. Travaux pratiques guidés

Les travaux pratiques suivants sont conçus pour un environnement de laboratoire et des données non critiques. Les tests de sinistre, de stockage et de fencing ne doivent pas être exécutés sans préparation, autorisation et possibilité de retour arrière.

### TP 1 — Réaliser une analyse d'impact métier

**Objectif :** déterminer les priorités de reprise.

Étapes :

1. Inventorier les applications.
2. Identifier les responsables métier.
3. Décrire les conséquences d'une interruption.
4. Définir des objectifs de RTO.
5. Définir les objectifs de RPO.
6. Identifier les dépendances.
7. Classer les services.
8. Faire valider les priorités.

Résultat attendu : une matrice d'analyse d'impact approuvée.

### TP 2 — Cartographier les dépendances

**Objectif :** identifier les services nécessaires à une application métier.

Étapes :

1. Choisir une application.
2. Identifier son serveur Web.
3. Identifier son service applicatif.
4. Identifier sa base de données.
5. Identifier le stockage.
6. Identifier les services DNS et d'authentification.
7. Identifier les certificats et secrets.
8. Construire un diagramme.
9. Définir l'ordre de reprise.

Résultat attendu : un diagramme de dépendances et une liste des prérequis de démarrage.

### TP 3 — Vérifier une sauvegarde

**Objectif :** prouver qu'une sauvegarde est exploitable.

Étapes :

1. Sélectionner une copie de test.
2. Vérifier sa provenance.
3. Vérifier son intégrité selon le type de sauvegarde.
4. Préparer un environnement isolé.
5. Restaurer les données.
6. Vérifier le résultat technique.
7. Effectuer un test fonctionnel.
8. Mesurer la durée.
9. Comparer le délai au RTO.
10. Documenter les résultats.

Résultat attendu : un rapport de restauration vérifié, pas uniquement un statut de sauvegarde réussi.

### TP 4 — Préparer une reprise d'application Web

**Objectif :** concevoir une reprise contrôlée de l'application.

Étapes :

1. Préparer le site de secours.
2. Vérifier le réseau.
3. Vérifier le contenu Web.
4. Vérifier les dépendances.
5. Vérifier le DNS.
6. Préparer le point d'entrée.
7. Définir les contrôles de santé.
8. Réaliser un test de service.
9. Documenter les résultats.
10. Définir le retour au site principal.

Résultat attendu : une procédure testable et un schéma d'architecture.

### TP 5 — Construire un runbook de basculement Pacemaker

**Objectif :** formaliser les actions en situation de crise.

Étapes :

1. Documenter le cluster.
2. Lister ses ressources.
3. Documenter le quorum.
4. Documenter le fencing.
5. Identifier les dépendances.
6. Définir le déclencheur d'activation.
7. Définir les contrôles avant et après reprise.
8. Définir le traitement d'un échec.
9. Définir les conditions d'arrêt du test.
10. Définir la procédure de retour.

Résultat attendu : un runbook qui peut être utilisé par un administrateur habilité.

### TP 6 — Réaliser un exercice sur table

**Objectif :** tester la coordination des équipes sans provoquer de panne réelle.

Scénario : le site principal est inaccessible et la dernière copie de base de données date de dix minutes, alors que le RPO cible est de cinq minutes.

Les participants doivent :

1. Qualifier l'incident.
2. Identifier l'autorité de décision.
3. Vérifier les informations disponibles.
4. Évaluer l'écart de RPO.
5. Déterminer les données récupérables.
6. Décider si le site secondaire doit être activé.
7. Définir les communications.
8. Documenter les risques.
9. Déterminer les contrôles post-reprise.
10. Produire un retour d'expérience.

Résultat attendu : un compte rendu identifiant les décisions, les manques de documentation et les actions correctives.

### TP 7 — Mesurer un RTO

**Objectif :** comparer la procédure à l'objectif.

Étapes :

1. Définir l'événement déclencheur.
2. Définir l'heure de début du test.
3. Activer le plan dans le périmètre prévu.
4. Restaurer les systèmes.
5. Effectuer les contrôles.
6. Faire valider le service.
7. Enregistrer l'heure de reprise fonctionnelle.
8. Calculer le temps mesuré.
9. Comparer au RTO.
10. Analyser les écarts.

Résultat attendu : un RTO mesuré avec des preuves et une liste d'améliorations.

## 25. Projet final : concevoir un PRA complet

### 25.1 Contexte

Une entreprise possède une infrastructure Linux avec :

- Deux serveurs d'équilibrage Keepalived / HAProxy.
- Plusieurs serveurs applicatifs.
- Un cluster Pacemaker pour un service critique.
- Une base de données.
- Un mécanisme de réplication de données.
- Une infrastructure de sauvegarde.

L'entreprise veut pouvoir rétablir les services après :

- La panne d'un serveur.
- La perte d'un cluster local.
- La perte du site principal.
- Une corruption des données.
- Une attaque par rançongiciel.

### 25.2 Architecture cible

```text
                   ACTIVITÉS MÉTIER
                          |
                          v
                   SERVICE CRITIQUE
                          |
              +-----------+-----------+
              |                       |
              v                       v
        SITE PRINCIPAL          SITE DE SECOURS
        --------------          --------------
        HAProxy / VIP            HAProxy / VIP
        Applications             Environnement cible
        Base principale          Réplique ou restauration
        Stockage                 Stockage secondaire
        Cluster local            Ressources de reprise
              |                       ^
              +---- Réplication ------+
                          |
                          v
                  SAUVEGARDES PROTÉGÉES
                  ----------------------
                  Copies isolées
                  Copies hors site
                  Copies immuables
                  Tests de restauration
```

L'architecture doit être adaptée aux caractéristiques de l'application et aux objectifs de reprise.

### 25.3 Livrables attendus

Le projet doit contenir :

- Une analyse d'impact métier.
- Une matrice de criticité.
- Les objectifs RTO et RPO.
- Un inventaire des systèmes et dépendances.
- Un schéma de l'infrastructure.
- Une stratégie de sauvegarde.
- Une architecture de réplication.
- Un plan de reprise intersite.
- Un plan de restauration des données.
- Un runbook d'activation.
- Un runbook de failback.
- Une procédure de gestion de crise cyber.
- Une procédure de validation fonctionnelle.
- Un plan de tests.
- Un rapport des tests réalisés.
- Une liste d'actions correctives.

### 25.4 Critères de réussite

Le projet est réussi si :

- Les objectifs sont approuvés par les responsables concernés.
- Les dépendances sont documentées.
- Les sauvegardes sont indépendantes et protégées.
- La restauration a été testée.
- Le site de secours possède les prérequis nécessaires.
- L'autorité d'activation du PRA est définie.
- Les risques de double écriture sont maîtrisés.
- Les contrôles fonctionnels sont documentés.
- Le RTO et le RPO ont été mesurés ou leurs écarts explicitement reconnus.
- Le retour au site principal est préparé.
- Les procédures peuvent être exécutées sans improvisation.

## 26. Défi final — Reprise après sinistre complexe

Une entreprise utilise une application de commande dont les données sont hébergées sur une base PostgreSQL. Le site principal dispose de Keepalived, HAProxy et d'un cluster Pacemaker. Une partie des données est répliquée vers un site secondaire.

La direction impose les objectifs suivants :

- RTO de 30 minutes pour le service de commande.
- RPO cible de cinq minutes.
- Capacité de reprise après la perte complète du site principal.
- Protection des sauvegardes contre un rançongiciel.
- Validation de la cohérence des commandes après reprise.

Tu dois construire un plan technique qui répond à toutes les questions suivantes.

### Partie A — Analyse métier

Définis les conséquences d'une interruption, les limites de perte de données et les priorités de reprise.

### Partie B — Architecture

Décris les mécanismes nécessaires pour :

- Faire fonctionner les services dans le site principal.
- Répliquer les données.
- Préparer le site secondaire.
- Accéder au service après le basculement.
- Éviter une double écriture.

### Partie C — Sauvegarde

Définis :

- Les types de sauvegarde.
- La fréquence.
- La rétention.
- La protection des copies.
- Le contrôle d'intégrité.
- La restauration dans un environnement isolé.

### Partie D — Reprise

Prépare :

- Les critères de déclenchement.
- L'autorité de décision.
- L'ordre de démarrage.
- Les contrôles de base de données.
- Les contrôles applicatifs.
- La validation métier.
- Le traitement d'un dépassement du RPO.

### Partie E — Sécurité

Définis les opérations nécessaires après une cyberattaque pour éviter la réintroduction d'un système compromis.

### Partie F — Tests

Prépare un exercice sur table, un test technique de restauration et un test de reprise complet dans un périmètre autorisé.

Le dossier doit montrer comment le RTO et le RPO seront mesurés et quelles décisions devront être prises si les objectifs ne sont pas atteints.

## 27. Fiche de révision opérationnelle

| Besoin | Élément à vérifier |
|---|---|
| Qualifier un sinistre | Scénario, périmètre, impact |
| Déterminer les priorités | BIA et criticité des activités |
| Définir la durée de reprise | RTO |
| Définir la perte de données acceptable | RPO |
| Maintenir une activité en mode dégradé | PCA |
| Rétablir les services après un sinistre | PRA |
| Déplacer une VIP locale | Keepalived / VRRP |
| Répartir le trafic applicatif | HAProxy ou IPVS |
| Gérer des ressources clusterisées | Pacemaker |
| Gérer la communication et le quorum | Corosync |
| Vérifier l'état des ressources du cluster | `pcs status --full` |
| Examiner le quorum | `corosync-quorumtool -s` |
| Vérifier la réplication DRBD | `drbdadm status` |
| Vérifier un service Web | Contrôle HTTP adapté |
| Restaurer une base | Procédure propre au moteur |
| Protéger les copies contre un rançongiciel | Sauvegardes isolées, hors ligne ou immuables |
| Vérifier la restaurabilité | Test de restauration |
| Revenir au site principal | Procédure de failback |
| Améliorer le plan | Retour d'expérience et actions correctives |

## 28. Bonnes pratiques de l'expert

### Gouvernance et organisation

- Définis les responsabilités avant la crise.
- Obtiens l'approbation des objectifs métier.
- Maintiens un inventaire actualisé.
- Documente les dépendances.
- Prévois des canaux de communication indépendants du système principal.
- Protège et versionne le dossier PRA.
- Prévois un responsable de la validation fonctionnelle.

### Architecture

- Ne confonds pas HA locale et reprise intersite.
- Identifie les points uniques de défaillance.
- Vérifie l'indépendance réelle du site de secours.
- Documente le réseau et le DNS.
- Prépare l'ordre de démarrage.
- Définis une autorité d'écriture claire.
- Mesure les temps de reprise.

### Sauvegarde

- Conserve plusieurs copies.
- Sépare les droits d'administration.
- Protège les sauvegardes contre la suppression.
- Prévois une copie hors ligne ou immuable lorsque le scénario l'exige.
- Contrôle les intégrités.
- Teste les restaurations.
- Sauvegarde également les configurations nécessaires à la reconstruction.
- Protège les clés nécessaires au déchiffrement des copies.

### Cyber-résilience

- Distingue une panne matérielle d'une compromission.
- Préserve les preuves utiles à l'investigation.
- Isole les systèmes compromis selon le plan.
- Prépare un environnement de reconstruction propre.
- Vérifie l'origine des sauvegardes.
- Renouvelle les secrets compromis.
- Ne reconnecte pas aveuglément les systèmes restaurés.
- Coordonne le PRA avec le plan de réponse à incident.

### Exploitation

- Utilise des runbooks testés.
- Enregistre les actions importantes.
- Fixe des critères d'arrêt pour les opérations risquées.
- Vérifie la cohérence des données.
- Ne force pas un basculement intersite sans évaluer le risque de double écriture.
- Mesure le RTO et le RPO réellement obtenus.
- Documente les écarts.
- Mets à jour le plan après les changements majeurs.

## 29. Glossaire expert

**PRA — Plan de Reprise d'Activité :** procédures permettant de rétablir et de reprendre les activités après un incident.

**DRP — Disaster Recovery Plan :** terme anglais correspondant au Plan de Reprise d'Activité.

**PCA — Plan de Continuité d'Activité :** dispositif visant à maintenir les activités essentielles pendant une perturbation, éventuellement en mode dégradé.

**BIA — Business Impact Analysis :** analyse d'impact sur l'activité qui permet de classer les services et de définir les priorités de reprise.

**RTO — Recovery Time Objective :** délai maximal ciblé pour rétablir un service.

**RPO — Recovery Point Objective :** perte de données temporelle maximale acceptable.

**DMIA :** durée maximale d'interruption admissible pour une activité.

**Haute disponibilité (HA) :** ensemble de mécanismes visant à réduire l'indisponibilité de certains services.

**Basculement (failover) :** transfert d'un service ou d'une ressource vers un autre système.

**Failback :** retour contrôlé vers le site ou le système nominal après une reprise.

**Réplication :** maintien d'une copie de données ou d'un état sur un autre système.

**Sauvegarde :** copie conservée pour permettre la restauration d'un état antérieur.

**Immutabilité :** propriété empêchant la modification ou la suppression d'une copie pendant la période définie, selon les capacités de la solution.

**Clean room :** environnement isolé de reconstruction et de récupération, destiné notamment aux reprises après compromission.

**Fencing :** mécanisme d'isolation fiable d'un nœud qui ne doit plus utiliser les ressources du cluster.

**Quorum :** mécanisme de décision qui détermine si le cluster dispose des votes requis pour continuer à gérer ses ressources.

**DRBD :** technologie de réplication de périphériques de stockage par blocs.

**Runbook :** procédure opérationnelle structurée détaillant les contrôles et actions à réaliser.

**RACI :** matrice décrivant qui réalise, approuve, conseille et doit être informé.

**Test de restauration :** opération permettant de vérifier que des données peuvent être récupérées et utilisées.

**Retour d'expérience (RETEX) :** analyse des actions, résultats et écarts après un incident ou un exercice.

## 30. Documentation de référence

### Références institutionnelles françaises

- [ANSSI — CyberDico : définitions PCA et PRA](https://cyber.gouv.fr/cyberdico/)
- [ANSSI — Sauvegarde des systèmes d'information](https://messervices.cyber.gouv.fr/guides/sauvegarde-des-systemes-dinformation)
- [ANSSI — Fondamentaux de la sauvegarde des systèmes d'information (PDF)](https://messervices.cyber.gouv.fr/documents-guides/anssi-fondamentaux-sauvegarde_systemes_dinformation_v1-0.pdf)
- [ANSSI — Référentiel de mesures de sécurité](https://monservicesecurise.cyber.gouv.fr/referentiel-mesures)

### Planification de reprise et gestion des incidents

- [NIST SP 800-34 Revision 1 — Contingency Planning Guide](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final)
- [NIST — Incident Response](https://csrc.nist.gov/projects/incident-response)
- [CISA — StopRansomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide)

### Haute disponibilité Linux

- [Ubuntu Server — Haute disponibilité](https://ubuntu.com/server/docs/reference/high-availability/)
- [Ubuntu Server — Présentation de la haute disponibilité](https://ubuntu.com/server/docs/explanation/high-availability/)
- [Ubuntu Server — DRBD](https://ubuntu.com/server/docs/how-to/high-availability/install-drbd/)
- [Red Hat Enterprise Linux 10 — Clusters haute disponibilité](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/10/html-single/configuring_and_managing_high_availability_clusters/index)

## Conclusion

Un PRA expert ne se résume pas à démarrer des serveurs sur un autre site. Il doit permettre à l'organisation de comprendre ce qui est perdu, de prendre une décision coordonnée, de restaurer les données, de rétablir les dépendances et de valider que les activités peuvent reprendre.

Keepalived, HAProxy, Pacemaker, Corosync et DRBD sont des composants possibles de cette stratégie. Ils contribuent respectivement à la gestion d'une adresse virtuelle, à l'équilibrage de charge, à la coordination des ressources, à la communication du cluster et à la réplication des données.

Mais aucun de ces outils ne remplace l'analyse d'impact métier, les sauvegardes indépendantes, les procédures de crise, la sécurité des accès et les tests de restauration.

La compétence experte consiste à pouvoir démontrer, avec des procédures et des résultats mesurés, que l'organisation peut reprendre ses activités dans les limites convenues, y compris lorsque l'incident dépasse le simple arrêt d'un serveur.

**La règle essentielle est la suivante : la haute disponibilité limite certaines interruptions, la réplication maintient des copies de données, et le PRA organise une reprise contrôlée. Seuls des tests réalistes permettent de vérifier que l'ensemble fonctionne réellement.**