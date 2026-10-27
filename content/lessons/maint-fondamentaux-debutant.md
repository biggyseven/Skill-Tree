# Fondamentaux de maintenance : rôles et cycle d’intervention

> **Mise en contexte**
>
> Tu viens d’intégrer une équipe chargée de maintenir les équipements informatiques d’une entreprise. À 8 h 15, un utilisateur signale que son ordinateur est devenu très lent. À 8 h 20, une équipe entière indique qu’elle ne peut plus accéder à un dossier partagé. À 8 h 25, un technicien remarque qu’un onduleur affiche une alerte. Dans le même temps, une intervention préventive sur un commutateur est prévue dans la matinée.
>
> Ces événements ne doivent pas être traités comme quatre tâches identiques. Le ralentissement d’un poste peut gêner une personne ; l’indisponibilité d’un dossier partagé peut bloquer plusieurs services ; l’alerte de l’onduleur peut annoncer un risque pour l’infrastructure ; l’opération planifiée doit être coordonnée pour ne pas provoquer une interruption inattendue.
>
> Le rôle de la maintenance ne consiste donc pas à « réparer vite » en multipliant les manipulations. Il consiste à organiser une intervention sûre, adaptée à l’impact réel, autorisée, traçable et vérifiée. La méthode protège les utilisateurs, les techniciens, les données et la continuité de l’activité.
>
> Dans ce cours, tu vas apprendre à comprendre les rôles, à distinguer les événements, à organiser le cycle complet d’une intervention et à produire une trace qui permette à un collègue de reprendre le travail sans repartir de zéro. Les exemples concernent principalement les équipements et services informatiques, mais les principes de préparation, de sécurité, de validation et de retour d’expérience s’appliquent aussi à d’autres environnements techniques.

## 1. Objectifs pédagogiques

À la fin de ce cours, tu seras capable de :

- expliquer la contribution de la maintenance au fonctionnement d’une organisation ;
- distinguer un équipement, un actif, un service et un processus métier ;
- reconnaître les principales familles de maintenance sans les confondre ;
- différencier un signalement, une demande, un incident, une panne, un symptôme et une cause ;
- identifier les responsabilités des utilisateurs, techniciens, responsables et équipes spécialisées ;
- comprendre le rôle d’un ticket, d’un ordre de travail et de l’historique d’un actif ;
- décrire les étapes d’une intervention avant, pendant et après les travaux ;
- évaluer l’impact et l’urgence sans décider uniquement sur la personne qui insiste le plus ;
- recueillir les informations utiles avant d’effectuer une action ;
- préparer les moyens, autorisations, sauvegardes, tests et conditions de retour arrière ;
- reconnaître les risques physiques, opérationnels et numériques ;
- respecter les limites de compétence, d’habilitation et d’autorisation ;
- vérifier qu’un service fonctionne réellement avant de clôturer une intervention ;
- rédiger un compte rendu factuel et compréhensible ;
- proposer des indicateurs simples pour améliorer la qualité de la maintenance.

## 2. Comprendre à quoi sert la maintenance

### 2.1 Définition opérationnelle

La maintenance regroupe les activités organisées pour conserver un équipement dans un état attendu ou le rétablir lorsqu’il ne remplit plus sa fonction. Selon le contexte, elle comprend l’inspection, le contrôle, le diagnostic, la réparation, le remplacement de composants, les essais, l’entretien périodique, la mise à jour de la documentation et le suivi des résultats.

Dans un service informatique, les objets maintenus peuvent être :

- les postes de travail, portables, écrans et périphériques ;
- les serveurs physiques ou virtuels ;
- les équipements réseau tels que les commutateurs, routeurs et points d’accès ;
- les solutions de stockage et de sauvegarde ;
- les systèmes d’alimentation, de refroidissement et les onduleurs ;
- les systèmes d’exploitation, applications et agents techniques ;
- les outils de sécurité, de supervision et de gestion des équipements ;
- les services hébergés chez un fournisseur ou dans le cloud ;
- les configurations, procédures et informations nécessaires à leur exploitation.

La maintenance n’est donc pas seulement un ensemble de gestes techniques. Elle associe des personnes, des équipements, des données, des procédures et des décisions.

### 2.2 Équipement, actif, service et activité métier

Ces quatre notions sont proches, mais ne sont pas interchangeables.

| Notion | Signification | Exemple |
|---|---|---|
| Équipement | Élément physique ou logiciel sur lequel on peut intervenir. | Un serveur, un ordinateur, un commutateur. |
| Actif | Ressource que l’organisation identifie, suit et gère au cours de son cycle de vie. | Le serveur SRV-FICHIERS-01 avec son numéro d’inventaire. |
| Service | Fonction fournie à des utilisateurs ou à d’autres systèmes. | Accès aux dossiers partagés. |
| Activité métier | Travail que l’organisation cherche à accomplir. | Préparer les commandes des clients. |

Un serveur peut être allumé alors que le service qu’il héberge est indisponible. Un service peut être accessible alors qu’un composant redondant est défaillant. Un ordinateur peut fonctionner techniquement mais empêcher un salarié de travailler parce qu’un accès ou une application manque.

La maintenance doit donc vérifier la fonction attendue, pas seulement l’état apparent de l’équipement.

### Schéma 1 — De l’équipement à la continuité d’activité

~~~mermaid
flowchart TD
    A[Équipement ou composant] --> B[Service informatique]
    B --> C[Utilisateurs et applications]
    C --> D[Activité métier]
    A -. panne ou dégradation .-> E[Incident technique]
    E --> F[Impact sur le service]
    F --> G[Conséquence métier]
~~~

**Comment lire le schéma ?** Une panne matérielle n’a pas toujours le même impact. Un équipement de test isolé et un commutateur qui relie un étage entier n’ont pas la même criticité. La priorité doit tenir compte des services dépendants et des conséquences pour l’organisation.

### 2.3 Les objectifs de la maintenance

**Disponibilité.** Le service doit être accessible au moment où il est attendu. Une intervention qui rétablit le service en trente minutes peut être préférable à une opération plus longue qui vise à corriger immédiatement tous les défauts, à condition que le risque restant soit accepté et qu’un plan de correction durable soit défini.

**Fiabilité.** Le service doit fonctionner de façon régulière et prévisible. La répétition d’une panne similaire montre qu’une simple remise en route ne suffit peut-être pas.

**Sécurité.** Les personnes, les données et les équipements doivent être protégés. Une intervention ne doit pas neutraliser une protection, exposer des identifiants ou créer un danger pour gagner quelques minutes.

**Maintenabilité.** L’équipement doit pouvoir être inspecté, réparé, testé et documenté avec des moyens raisonnables. La disponibilité de pièces, d’outils, de documentation et d’accès sûrs influence la qualité du travail.

**Traçabilité.** Un collègue doit pouvoir comprendre ce qui a été observé, décidé, modifié et vérifié. La mémoire personnelle d’un technicien ne suffit pas pour assurer la continuité du service.

**Maîtrise des coûts.** Il faut tenir compte du temps passé, des pièces, des interruptions, des interventions répétées et du coût d’une panne évitable. La solution la moins chère immédiatement n’est pas forcément la moins coûteuse sur la durée.

## 3. Les grandes familles de maintenance

Les organisations utilisent plusieurs catégories. Leur nom précis peut varier selon le secteur et les procédures internes ; il faut donc toujours se référer au vocabulaire adopté localement.

### 3.1 Maintenance corrective

Elle intervient après qu’un défaut ou une défaillance a été détecté, afin de rétablir la fonction attendue.

Exemples :

- remplacer une alimentation défaillante ;
- corriger une configuration réseau qui empêche l’accès à un service ;
- réparer un système de fichiers après un incident, selon une procédure autorisée ;
- rétablir un service interrompu par une panne logicielle.

La maintenance corrective peut être urgente ou planifiée. Une petite anomalie sur un équipement non critique peut attendre une fenêtre appropriée. Une défaillance qui interrompt une activité essentielle peut nécessiter une réponse immédiate.

Une distinction utile est celle entre le **dépannage** et la **réparation durable**. Le dépannage cherche souvent à rétablir rapidement une fonction, parfois au moyen d’une solution temporaire. La réparation durable vise à supprimer ou à maîtriser la cause identifiée. Une solution de contournement peut être nécessaire, mais elle doit être documentée, limitée dans le temps et suivie.

### 3.2 Maintenance préventive

Elle est réalisée avant la panne, selon un calendrier ou des critères définis. Son objectif est de réduire la probabilité d’une défaillance ou une dégradation de fonctionnement.

Exemples :

- vérifier périodiquement l’état des batteries d’un onduleur selon les instructions du fabricant ;
- contrôler la capacité disponible sur un stockage ;
- inspecter l’état des ventilateurs et les températures ;
- vérifier qu’une sauvegarde a été exécutée et qu’une restauration de test est possible ;
- contrôler les journaux et les alertes d’équipements ;
- réviser les procédures et vérifier la présence des pièces de rechange critiques.

La maintenance préventive n’est pas une série d’actions automatiques sans réflexion. Il faut définir la tâche, la fréquence, la personne responsable, les critères de réussite et la preuve attendue.

### 3.3 Maintenance conditionnelle et prédictive

La maintenance conditionnelle déclenche une action à partir de l’état observé : température, vibration, erreurs, capacité, nombre de cycles ou autre indicateur pertinent.

La maintenance prédictive va plus loin lorsqu’elle exploite des tendances ou des modèles pour estimer la possibilité d’une défaillance future. Elle peut s’appuyer sur des données historiques, de la télémétrie ou des techniques statistiques.

Exemple : la hausse progressive des erreurs d’un disque, combinée à d’autres observations, peut justifier une investigation avant la panne. Une simple alerte isolée ne prouve toutefois pas qu’un composant va tomber en panne ; elle constitue un signal à vérifier selon la procédure.

### 3.4 Maintenance évolutive ou amélioration

Une intervention évolutive modifie un équipement, un logiciel ou un processus pour répondre à un besoin nouveau ou améliorer le service : capacité supplémentaire, nouvelle fonctionnalité, changement d’architecture, amélioration de sécurité ou réduction d’une faiblesse récurrente.

Elle ne doit pas être confondue avec la correction d’un incident. Une évolution peut nécessiter une demande de changement, des tests, une approbation et une stratégie de retour arrière.

### Schéma 2 — Choisir une famille de maintenance

~~~mermaid
flowchart TD
    A[Besoin détecté] --> B{Le service ou l'équipement est-il défaillant ?}
    B -->|Oui| C[Maintenance corrective]
    B -->|Non| D{Existe-t-il une tâche planifiée ?}
    D -->|Oui| E[Maintenance préventive]
    D -->|Non| F{Un indicateur révèle-t-il une dégradation ?}
    F -->|Oui| G[Maintenance conditionnelle ou prédictive]
    F -->|Non| H{Une amélioration est-elle demandée ?}
    H -->|Oui| I[Maintenance évolutive ou amélioration]
    H -->|Non| J[Surveiller, qualifier ou clarifier le besoin]
~~~

Le choix dépend du contexte réel. Si l’on ne dispose pas d’informations suffisantes, la bonne action est de qualifier le besoin plutôt que de choisir arbitrairement une catégorie.

## 4. Les personnes et leurs responsabilités

La maintenance est un travail coordonné. Même dans une petite entreprise où un technicien réalise plusieurs fonctions, les responsabilités doivent être claires.

### 4.1 L’utilisateur ou le demandeur

Il décrit ce qu’il observe et ce qu’il essaie de faire. Il peut fournir l’heure d’apparition, le message d’erreur, le nom de l’application, les actions précédentes et le nombre de personnes affectées.

Il n’a pas à diagnostiquer lui-même la cause. Il doit éviter de communiquer ses mots de passe dans le ticket ou de multiplier les manipulations si celles-ci risquent d’altérer les preuves ou les données.

### 4.2 Le service d’assistance ou helpdesk

Il reçoit les signalements, vérifie les informations minimales, catégorise la demande, évalue l’impact initial, attribue une priorité selon les règles de l’organisation et suit la communication.

Il peut résoudre les cas correspondant à ses procédures et à ses autorisations. Il doit transmettre les situations hors de son périmètre sans perdre l’historique ni obliger l’utilisateur à tout répéter.

### 4.3 Le technicien de maintenance

Il réalise les contrôles et les actions relevant de ses compétences. Il distingue les faits, les hypothèses et les conclusions. Il respecte les autorisations, les règles de sécurité et les conditions d’intervention. Il documente les actions et vérifie les résultats.

Le technicien ne doit pas transformer une supposition en certitude. Si la cause n’est pas connue, il doit préciser ce qui a été observé, ce qui a été exclu et ce qui reste à analyser.

### 4.4 Le responsable de maintenance ou du support

Il répartit le travail, valide les priorités selon les règles internes, organise les ressources et s’assure que les opérations peuvent être réalisées dans de bonnes conditions. Il suit la charge, les incidents récurrents, les interventions en attente et la qualité des comptes rendus.

Il n’est pas nécessairement la personne qui exécute chaque tâche. Son rôle comprend l’organisation, l’arbitrage et l’amélioration.

### 4.5 Le propriétaire du service ou représentant métier

Il explique l’importance du service pour l’activité, les périodes sensibles, les utilisateurs concernés et les conditions de remise en service. Il peut contribuer à accepter un risque métier ou à définir un critère de validation, selon les droits établis par l’organisation.

### 4.6 Les équipes spécialisées

Selon le contexte, une intervention peut nécessiter un administrateur système, un spécialiste réseau, un expert stockage, un responsable sécurité, un administrateur de base de données, un électricien habilité ou un prestataire.

Faire appel à une personne spécialisée n’est pas un échec. C’est un moyen de limiter le risque lorsque l’intervention dépasse les connaissances, les accès ou les autorisations disponibles.

### 4.7 La coordination avec la production et les fournisseurs

Lorsque les équipements soutiennent une activité en cours, l’équipe de maintenance doit coordonner l’interruption, les essais et la restitution avec les personnes qui exploitent le service. Le fournisseur peut apporter une documentation, une expertise ou une pièce, mais son intervention doit elle aussi respecter les règles de l’organisation.

### Schéma 3 — Qui fait quoi ?

~~~mermaid
flowchart LR
    U[Utilisateur] -->|Décrit le besoin| H[Helpdesk ou réception]
    H -->|Qualifie et priorise| R[Responsable ou ordonnanceur]
    R -->|Planifie et autorise| T[Technicien]
    T -->|Escalade si nécessaire| S[Équipe spécialisée]
    T -->|Résultats et preuves| R
    R -->|Validation métier ou service| M[Propriétaire du service]
    T -->|Compte rendu| H
    H -->|Information de clôture| U
~~~

Ce schéma est volontairement générique. Dans une petite structure, plusieurs rôles peuvent être assumés par la même personne. En revanche, une opération à risque peut nécessiter une approbation indépendante ou une habilitation spécifique.

### 4.8 La matrice RACI

La matrice RACI sert à clarifier les rôles :

- **R — Réalise :** effectue le travail.
- **A — Assume la responsabilité finale :** répond de la décision ou de l’acceptation du résultat.
- **C — Consulté :** apporte une expertise avant la décision.
- **I — Informé :** reçoit l’information utile.

Exemple indicatif pour une intervention planifiée :

| Activité | Responsable maintenance | Technicien | Propriétaire du service | Sécurité |
|---|---|---|---|---|
| Évaluer la demande | A | C | C | I |
| Préparer la procédure | A | R | C | C |
| Autoriser la fenêtre d’interruption | C | I | A | C si nécessaire |
| Réaliser les tâches techniques | I | R | I | C si nécessaire |
| Vérifier les critères techniques | A | R | C | I |
| Confirmer le service métier | C | C | A/R selon l’organisation | I |
| Archiver et analyser | A | R | C | C si incident de sécurité |

Il s’agit d’un exemple, pas d’une règle universelle. L’organisation doit attribuer explicitement chaque responsabilité, notamment pour les changements à fort impact.

## 5. Le vocabulaire de base à maîtriser

Une terminologie claire évite les malentendus. Les termes suivants sont liés, mais ne signifient pas la même chose.

| Terme | Définition simple | Exemple |
|---|---|---|
| Signalement | Information indiquant qu’un événement ou un besoin a été observé. | « Le dossier partagé n’est plus accessible. » |
| Demande de service | Demande d’une prestation prévue par le catalogue ou la procédure. | Demander l’installation d’une application autorisée. |
| Incident | Événement qui interrompt ou dégrade un service attendu. | Les utilisateurs ne peuvent plus ouvrir leurs dossiers. |
| Panne | Défaillance d’un élément qui ne remplit plus sa fonction. | Une alimentation ne fournit plus l’énergie attendue. |
| Symptôme | Manifestation observable du problème. | Le voyant du port réseau reste éteint. |
| Cause | Facteur qui explique le défaut constaté. | Un câble a été débranché lors d’une intervention. |
| Contournement | Moyen temporaire permettant de réduire l’impact sans supprimer nécessairement la cause. | Utiliser une liaison de secours approuvée pendant une réparation. |
| Correction | Action destinée à supprimer le défaut ou à rétablir la fonction. | Remplacer le câble défectueux et vérifier la liaison. |
| Problème récurrent | Situation qui se répète et peut nécessiter une analyse de cause racine. | La même liaison tombe plusieurs fois par semaine. |
| Changement | Modification contrôlée d’un service, d’un actif ou de sa configuration. | Modifier la configuration d’un commutateur de production. |
| Ordre de travail | Instruction structurée décrivant les travaux autorisés à réaliser. | Contrôler les ventilateurs d’un serveur pendant une fenêtre planifiée. |
| Critère d’acceptation | Condition observable qui doit être satisfaite pour déclarer le résultat acceptable. | Les utilisateurs autorisés accèdent au dossier et les journaux ne montrent pas la même erreur. |

Un symptôme ne constitue pas une preuve suffisante de la cause. Un ordinateur lent peut être affecté par un manque de ressources, une application, un stockage, une connexion réseau, un logiciel malveillant ou un problème temporaire. Redémarrer peut masquer le symptôme sans expliquer ce qui s’est produit.

### Schéma 4 — De l’observation à la correction

~~~mermaid
flowchart TD
    A[Observation vérifiable] --> B[Hypothèses possibles]
    B --> C[Contrôles discriminants]
    C --> D{Une cause est-elle suffisamment étayée ?}
    D -->|Non| E[Recueillir d'autres preuves ou escalader]
    D -->|Oui| F[Choisir une action proportionnée]
    F --> G[Tester le résultat]
    G --> H{Critères satisfaits ?}
    H -->|Non| I[Arrêter, réévaluer et documenter]
    H -->|Oui| J[Documenter et clôturer]
~~~

Le diagnostic est une démarche fondée sur des preuves. Il ne consiste pas à essayer au hasard toutes les solutions connues.

## 6. Les outils de suivi : ticket, ordre de travail et historique

### 6.1 Pourquoi une demande doit-elle laisser une trace ?

Un échange oral ou un message isolé ne donne pas toujours une vision complète de l’incident. Sans suivi structuré, plusieurs techniciens peuvent réaliser les mêmes contrôles, une action risquée peut être répétée et une panne peut être déclarée résolue sans preuve.

Le ticket ou l’enregistrement de maintenance permet de conserver :

- une référence unique ;
- la date et l’heure du signalement ;
- le demandeur et les moyens de le contacter selon les règles locales ;
- l’équipement ou le service concerné ;
- les symptômes et le périmètre affecté ;
- l’impact, l’urgence et la priorité ;
- les informations et preuves recueillies ;
- les décisions et autorisations ;
- les actions effectuées et leurs résultats ;
- les pièces utilisées, le temps passé et les intervenants ;
- les tests de validation ;
- le statut final, les limitations éventuelles et les suites à donner.

Il ne faut pas enregistrer des informations sensibles qui ne sont pas nécessaires. Les mots de passe, clés privées, jetons d’accès et secrets doivent être protégés par des mécanismes adaptés, pas copiés dans le commentaire d’un ticket.

### 6.2 Ticket et ordre de travail : quelle différence ?

Le ticket suit le besoin, l’incident ou la demande. Il porte notamment sur l’impact, la communication et la résolution.

L’ordre de travail organise l’exécution d’une tâche de maintenance : activités prévues, ressources, durée, procédures, risques, pièces, prérequis et critères de fin.

Dans certains outils, le ticket et l’ordre de travail sont deux objets distincts. Dans une petite organisation, ils peuvent être réunis dans un seul enregistrement. L’essentiel est que les responsabilités, les autorisations et les résultats restent compréhensibles.

### 6.3 La GMAO et l’ITSM

Une GMAO, ou gestion de maintenance assistée par ordinateur, aide à gérer les équipements, les interventions, les plans préventifs, les pièces et l’historique. Un outil ITSM organise plus spécifiquement les services informatiques, les incidents, les demandes, les problèmes et les changements.

Les outils peuvent être intégrés et les fonctionnalités se recouper. Ils ne remplacent pas une bonne procédure : une demande mal qualifiée reste mal qualifiée même si elle est enregistrée dans une plateforme moderne.

### Schéma 5 — Les informations restent liées

~~~mermaid
flowchart TD
    A[Ticket : incident ou demande] --> B[Diagnostic et décision]
    B --> C[Ordre de travail]
    C --> D[Actions et mesures]
    D --> E[Tests et réception]
    E --> F[Compte rendu]
    F --> G[Historique de l'actif]
    G --> H[Amélioration du plan de maintenance]
    H --> C
~~~

## 7. Le cycle complet d’une intervention

L’INRS rappelle que la prévention et la maîtrise des interventions ne concernent pas uniquement les gestes effectués sur l’équipement : la préparation en amont et les opérations qui suivent font également partie du processus. Le détail doit être adapté au type d’équipement et aux règles de l’organisation. Voir la [fiche pratique de l’INRS sur les étapes de la maintenance](https://www.inrs.fr/media.html?refINRS=ED+129) et ses recommandations sur l’[organisation de la maintenance](https://www.inrs.fr/risques/maintenance/prevention.html).

Pour apprendre simplement, on peut regrouper le cycle en trois grandes phases : **avant, pendant et après**.

### Schéma 6 — Vue générale du cycle

~~~mermaid
flowchart LR
    subgraph AVANT
        A[Détecter et signaler] --> B[Qualifier et prioriser]
        B --> C[Diagnostiquer]
        C --> D[Préparer et autoriser]
    end
    subgraph PENDANT
        E[Sécuriser] --> F[Intervenir]
        F --> G[Contrôler le résultat]
    end
    subgraph APRES
        H[Restaurer le service] --> I[Documenter et clôturer]
        I --> J[Analyser et améliorer]
    end
    D --> E
    G --> H
~~~

### 7.1 Première étape : détecter et signaler

Une intervention commence par un déclencheur : défaut, alarme, demande, inspection, échéance de maintenance ou observation d’un technicien.

Le signalement doit décrire un fait observable. Compare :

- « Le réseau est cassé » ;
- « Depuis 9 h 10, les postes du deuxième étage ne peuvent plus accéder au serveur de fichiers ; les postes du premier étage fonctionnent encore ».

La seconde formulation indique une heure, un périmètre et un service précis. Elle aide à orienter les vérifications sans affirmer une cause inconnue.

Les sources possibles comprennent le demandeur, la supervision, les journaux, les contrôles périodiques, les alertes du fabricant ou la détection par un technicien.

### 7.2 Deuxième étape : qualifier la demande

La qualification doit permettre de répondre à plusieurs questions :

- Quel équipement ou service est concerné ?
- Quelle fonction ne marche plus comme prévu ?
- Depuis quand le problème est-il observé ?
- Combien de personnes ou de services sont affectés ?
- Existe-t-il une solution de contournement déjà approuvée ?
- Une modification récente a-t-elle eu lieu ?
- Le problème empêche-t-il un processus métier important ?
- Y a-t-il un risque immédiat pour des personnes, des données ou d’autres équipements ?
- Quelle preuve permet de confirmer le symptôme ?

La personne qui reçoit le signalement ne doit pas exiger de l’utilisateur un diagnostic complet. Son objectif est de réunir assez d’informations pour attribuer, prioriser et orienter la demande.

### 7.3 Troisième étape : évaluer l’impact et l’urgence

L’**impact** décrit les conséquences sur les utilisateurs, les services, les données ou l’activité. L’**urgence** décrit le délai dont on dispose avant que les conséquences deviennent inacceptables ou plus graves.

La priorité est déterminée par la politique de l’organisation. Il ne faut pas inventer une règle universelle : les services critiques, les engagements contractuels et les risques de sécurité peuvent imposer des règles particulières.

Exemple de grille simple, uniquement illustrative :

| Impact | Urgence faible | Urgence moyenne | Urgence élevée |
|---|---|---|---|
| Faible | Planifier normalement | Prendre dans la file standard | Traiter rapidement si le délai devient critique |
| Moyen | Planifier et informer | Prioriser dans la file | Mobiliser une réponse accélérée |
| Élevé | Faire valider la planification | Coordonner immédiatement | Déclencher la procédure critique prévue |

Cette grille ne remplace ni les procédures d’urgence ni l’analyse de sécurité. Une alerte de sécurité, un risque de perte de données ou un danger pour une personne peut nécessiter une action immédiate même si le nombre d’utilisateurs touchés est faible.

### Schéma 7 — Qualifier avant de choisir la priorité

~~~mermaid
flowchart TD
    A[Signalement reçu] --> B{Risque immédiat pour personnes ou données ?}
    B -->|Oui| C[Appliquer la procédure d'urgence]
    B -->|Non| D[Identifier le service et le périmètre]
    D --> E[Évaluer impact et urgence]
    E --> F[Appliquer la matrice de priorité locale]
    F --> G[Attribuer un responsable et informer]
    G --> H[Réévaluer si la situation évolue]
~~~

Une priorité n’est pas définitive. Si le périmètre s’élargit ou si un risque nouveau apparaît, il faut la réévaluer et notifier les personnes concernées.

### 7.4 Quatrième étape : établir un diagnostic initial

Le diagnostic consiste à comparer l’état observé à l’état attendu, recueillir les preuves et tester des hypothèses raisonnables.

Une démarche simple est la suivante :

1. confirmer le symptôme et sa date d’apparition ;
2. identifier le périmètre affecté et les éléments encore fonctionnels ;
3. consulter les journaux ou indicateurs disponibles selon les autorisations ;
4. rechercher les changements récents pertinents ;
5. formuler quelques hypothèses testables ;
6. choisir un contrôle qui distingue les hypothèses ;
7. noter le résultat et décider de la prochaine étape.

Il est préférable de modifier une variable à la fois lorsque cela est possible. Si plusieurs modifications sont appliquées en même temps, il devient difficile de savoir laquelle a réglé le problème ou créé un effet secondaire.

Le diagnostic doit avoir des limites. Si les contrôles nécessitent un accès qui n’est pas autorisé, une compétence spécialisée, une interruption ou un risque non maîtrisé, il faut s’arrêter et faire intervenir la personne compétente.

### 7.5 Cinquième étape : préparer les travaux

La préparation traduit le diagnostic en un plan d’intervention réalisable. Elle couvre :

- l’objectif de l’intervention et son périmètre ;
- les compétences, personnes et responsabilités nécessaires ;
- les procédures et documents techniques ;
- les outils, pièces et équipements de protection ;
- les autorisations et validations ;
- la fenêtre de travail et les personnes à prévenir ;
- les dépendances techniques et les autres interventions simultanées ;
- les sauvegardes ou mécanismes de récupération adaptés ;
- les risques et mesures de prévention ;
- les tests de réussite ;
- le plan de retour arrière ou d’arrêt si le résultat attendu n’est pas obtenu.

Une bonne préparation ne garantit pas qu’aucun imprévu ne surviendra. Elle permet toutefois de le détecter plus tôt et de réagir avec méthode.

### Schéma 8 — Une préparation prête à démarrer ?

~~~mermaid
flowchart TD
    A[Plan d'intervention proposé] --> B{Compétences et autorisations disponibles ?}
    B -->|Non| Z[Reporter ou escalader]
    B -->|Oui| C{Risques évalués et mesures prévues ?}
    C -->|Non| Z
    C -->|Oui| D{Outils, pièces et documentation prêts ?}
    D -->|Non| Z
    D -->|Oui| E{Tests et retour arrière définis ?}
    E -->|Non| Z
    E -->|Oui| F[Confirmer la fenêtre et informer]
    F --> G[Autoriser le démarrage selon la procédure]
~~~

L’organisation peut adapter la liste aux risques de la tâche. Une opération simple et réversible ne nécessite pas toujours la même préparation qu’un changement sur une infrastructure critique. En revanche, les risques ne doivent jamais être ignorés uniquement parce que l’intervention paraît familière.

### 7.6 Sixième étape : sécuriser l’environnement

Avant d’intervenir, il faut s’assurer que le lieu, les personnes, l’équipement et les données sont protégés.

Selon la nature du travail, cela peut comprendre :

- délimiter la zone de travail ;
- prévenir les personnes concernées ;
- vérifier les règles d’accès au local ;
- protéger les composants sensibles contre les décharges électrostatiques ;
- éviter les câbles qui créent un risque de chute ;
- respecter les procédures d’arrêt et d’isolation des énergies ;
- protéger les sauvegardes, les supports et les informations confidentielles ;
- utiliser un compte et des droits adaptés à la tâche ;
- confirmer qu’une intervention simultanée ne crée pas un danger supplémentaire.

**Ne jamais considérer un équipement comme sûr simplement parce qu’il est arrêté.** Certaines énergies peuvent rester stockées, certaines fonctions peuvent redémarrer automatiquement et certaines opérations exigent des compétences particulières. La consignation, la vérification de l’absence d’énergie dangereuse et la remise en service doivent suivre les procédures locales et être exécutées par des personnes qualifiées.

Les principes de contrôle des énergies dangereuses sont détaillés dans la réglementation américaine OSHA relative au [lockout/tagout](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147). Cette référence fournit un exemple de cadre de prévention ; elle ne remplace pas la réglementation, les habilitations ou les procédures applicables sur ton site.

### 7.7 Septième étape : exécuter l’intervention

Pendant la réalisation :

- suivre le plan autorisé ;
- vérifier l’identité de l’équipement avant d’agir ;
- conserver l’ordre logique des opérations ;
- noter les résultats et anomalies significatives ;
- éviter les modifications non prévues sans autorisation appropriée ;
- surveiller les effets sur les services dépendants ;
- arrêter l’intervention si un risque nouveau apparaît ou si les conditions ne correspondent plus au plan.

Une consigne simple est utile : **observer, agir, vérifier, enregistrer**. Ce cycle évite d’enchaîner de nombreuses manipulations sans connaître leurs effets.

En cas d’écart, il ne faut pas masquer ce qui s’est produit. Il faut sécuriser la situation, prévenir les responsables requis, conserver les éléments utiles et décider de la suite.

### 7.8 Huitième étape : tester la fonction attendue

Une réparation ne peut pas être déclarée réussie uniquement parce que l’alerte a disparu ou qu’un équipement s’allume. Il faut vérifier la fonction attendue.

Exemples de critères :

- le poste se connecte au service autorisé ;
- les utilisateurs concernés retrouvent l’accès attendu ;
- la sauvegarde de test peut être restaurée dans un environnement prévu ;
- la liaison réseau transmet le trafic attendu sans erreur anormale ;
- les journaux et mesures ne montrent pas le même défaut ;
- les fonctions de sécurité demeurent actives ;
- les performances reviennent à un niveau acceptable ;
- les dépendances essentielles restent opérationnelles.

Un test doit être défini avant l’action lorsque c’est possible. Cela évite de déclarer le succès sur la base d’une impression subjective.

### Schéma 9 — Le test détermine la suite

~~~mermaid
flowchart TD
    A[Action terminée] --> B[Exécuter les tests prévus]
    B --> C{Critères techniques satisfaits ?}
    C -->|Non| D[Consigner l'échec et contenir le risque]
    D --> E[Revenir à l'état sûr ou escalader]
    C -->|Oui| F{Validation du service nécessaire ?}
    F -->|Oui| G[Demander une confirmation au responsable concerné]
    F -->|Non| H[Préparer la clôture]
    G --> I{Acceptation confirmée ?}
    I -->|Non| D
    I -->|Oui| H
~~~

### 7.9 Neuvième étape : remettre en service

La remise en service est une étape à part entière. Elle peut inclure la restauration des connexions, le retrait contrôlé des protections temporaires, la vérification des auxiliaires, les essais, la surveillance initiale et la communication à la personne qui exploite le service.

Le technicien ne doit pas retirer une consignation ou une mesure de protection en dehors de la procédure applicable. Les personnes doivent être informées de la fin des travaux avant qu’un équipement soit réutilisé, lorsqu’une coordination est requise.

Si le service fonctionne avec une limitation, celle-ci doit être explicitement décrite : ce qui fonctionne, ce qui ne fonctionne pas, les risques résiduels, les mesures temporaires et le responsable de la suite.

### 7.10 Dixième étape : documenter et clôturer

La clôture est une décision fondée sur les preuves. Un dossier peut être clôturé lorsque les critères de fin sont satisfaits, que les tests sont notés, que le demandeur ou le propriétaire du service a été informé et que les tâches restantes disposent d’un suivi.

Une clôture correcte doit préciser :

- le symptôme initial ;
- le périmètre affecté ;
- les constatations essentielles ;
- la cause confirmée, si elle est connue ;
- les actions réalisées ;
- les pièces ou configurations modifiées ;
- les résultats des tests ;
- l’état final et les limites éventuelles ;
- les personnes informées ;
- les actions complémentaires, leur priorité et leur responsable.

Si la cause n’est pas confirmée, ne pas écrire « cause trouvée ». Une formulation exacte serait : « Le service est rétabli après remplacement du câble ; l’origine de la déconnexion initiale reste à confirmer. » La précision améliore la fiabilité de l’historique.

### 7.11 Onzième étape : tirer les enseignements

La fin d’une intervention peut révéler une amélioration à apporter : mettre à jour une procédure, corriger l’inventaire, ajouter un contrôle préventif, améliorer une alerte, stocker une pièce de rechange ou organiser une formation.

Le retour d’expérience ne doit pas chercher automatiquement un coupable. Il doit aider à comprendre les conditions ayant permis le défaut et à réduire sa probabilité ou ses conséquences futures.

## 8. Sécurité, autorisation et points d’arrêt

### 8.1 Les risques physiques

Les travaux peuvent exposer à l’électricité, aux pièces mobiles, aux équipements lourds, aux températures, aux batteries, à la poussière ou aux risques liés à l’environnement. Le danger dépend de l’installation et de la tâche.

Ne retire pas une protection, ne déplace pas une charge lourde et n’interviens pas dans un équipement électrique sous tension sans formation, habilitation, équipement et procédure adaptés. En cas de doute, suspendre l’intervention et demander une évaluation compétente.

### 8.2 Les risques numériques

Une intervention informatique peut aussi provoquer :

- la perte ou l’altération de données ;
- une interruption plus large que prévu ;
- une exposition d’informations confidentielles ;
- l’utilisation excessive de privilèges ;
- la désactivation d’une protection de sécurité ;
- une modification non autorisée ;
- l’impossibilité de revenir à un état stable.

Avant une modification importante, il faut comprendre ce qui sera changé, qui l’autorise, comment le résultat sera vérifié et comment limiter l’impact si le résultat est incorrect.

### 8.3 Les sauvegardes et le retour arrière

Une sauvegarde n’est utile que si elle est disponible, suffisamment récente et adaptée au besoin de récupération. La présence d’un voyant vert ou d’un message « réussi » ne prouve pas à elle seule qu’une restauration fonctionnera.

Pour une intervention à risque, le plan de retour arrière doit être précis : état à retrouver, méthode, dépendances, durée estimée, autorité qui décide du retour arrière et tests à effectuer ensuite. Si la récupération n’est pas possible ou n’est pas suffisamment garantie, il faut faire évaluer le risque avant de commencer.

### 8.4 Quand faut-il arrêter ?

Interromps la tâche et sollicite l’aide nécessaire lorsque :

- le périmètre réel dépasse le périmètre autorisé ;
- une protection doit être neutralisée pour continuer ;
- une énergie dangereuse ne peut pas être isolée selon la procédure ;
- la sauvegarde ou la récupération nécessaire n’est pas disponible ;
- les preuves montrent que la tâche risque d’aggraver la situation ;
- un doute existe sur l’identité de l’équipement ;
- une modification imprévue affecte un service critique ;
- l’intervention dépasse les compétences ou autorisations de l’intervenant ;
- une suspicion de compromission ou de fuite de données apparaît.

### Schéma 10 — Règle de décision en cas de doute

~~~mermaid
flowchart TD
    A[Une difficulté ou un imprévu apparaît] --> B{La sécurité et le périmètre restent-ils maîtrisés ?}
    B -->|Oui| C[Continuer selon la procédure approuvée]
    B -->|Non ou incertain| D[Arrêter l'action en sécurité]
    D --> E[Préserver les preuves et limiter l'impact]
    E --> F[Informer le responsable compétent]
    F --> G[Réévaluer et obtenir une nouvelle autorisation]
    G --> H[Reprendre seulement si les conditions sont réunies]
~~~

L’arrêt contrôlé est une décision professionnelle. L’objectif est d’éviter qu’une incertitude locale devienne un incident plus important.

## 9. Exemple complet : un dossier partagé inaccessible

### 9.1 Situation initiale

À 9 h 10, plusieurs utilisateurs d’un service indiquent qu’ils ne peuvent plus ouvrir un dossier partagé. D’autres applications fonctionnent. Le service concerné est utilisé pour traiter les commandes de la journée.

Le premier signalement est : « Le serveur est en panne ». Cette phrase est trop imprécise. Le technicien commence par confirmer le service, le périmètre et les symptômes, sans décider d’avance que le serveur est la cause.

### 9.2 Qualification

Le helpdesk recueille :

- l’heure approximative de début ;
- les utilisateurs et postes concernés ;
- le chemin ou nom du service partagé ;
- les messages affichés ;
- si les utilisateurs concernés sont dans le même site ou le même segment ;
- si des changements ou opérations étaient planifiés ;
- si certains utilisateurs ont encore accès au service.

Le ticket décrit les faits et la priorité est déterminée avec la matrice locale. Comme plusieurs personnes et un processus métier sont affectés, la demande n’est pas traitée comme un incident isolé d’un poste.

### 9.3 Diagnostic initial

Le technicien vérifie les éléments autorisés et disponibles : supervision, journaux, état du service, connectivité selon les procédures approuvées, changements récents et périmètre d’impact.

Il ne redémarre pas immédiatement le serveur. Un redémarrage pourrait interrompre d’autres fonctions, rendre des journaux plus difficiles à analyser ou aggraver le problème.

Les observations orientent vers plusieurs hypothèses : problème de connectivité, problème d’authentification, service indisponible ou droits d’accès. Chaque hypothèse appelle un contrôle différent.

### 9.4 Préparation et intervention

Lorsque le diagnostic justifie une action corrective, le technicien vérifie son autorisation, les dépendances, le risque pour les données et la méthode de récupération. Si un changement de production est requis, il respecte le processus de changement local.

Les actions sont consignées au fur et à mesure. Si un contrôle ne correspond pas au résultat attendu, le technicien revient à un état sûr ou escalade au lieu d’enchaîner des modifications sans explication.

### 9.5 Validation

Après la correction, il faut vérifier :

1. que le service est actif ;
2. qu’un utilisateur autorisé peut accéder au dossier ;
3. que les opérations usuelles attendues fonctionnent ;
4. que les utilisateurs ou équipes affectés sont informés ;
5. que les alertes et journaux ne signalent pas un défaut persistant ;
6. que le risque restant, s’il existe, est documenté.

### 9.6 Compte rendu final

Un compte rendu pourrait prendre la forme suivante, à compléter avec les résultats réellement observés :

**Symptôme :** le dossier partagé était inaccessible à plusieurs utilisateurs depuis 9 h 10.

**Impact :** le traitement des commandes du service concerné était perturbé.

**Constats :** les applications non liées au dossier partagé continuaient de fonctionner. Les vérifications complémentaires et leurs résultats sont consignés dans le ticket.

**Action :** décrire précisément la modification ou la réparation réellement effectuée, avec l’autorisation correspondante.

**Validation :** indiquer les tests exécutés, le résultat de chaque test et la confirmation du service lorsque celle-ci est requise.

**État final :** indiquer si le service est rétabli, partiellement disponible ou encore affecté.

**Suite :** si la cause profonde reste incertaine, créer ou rattacher une tâche de suivi et désigner un responsable.

Cet exemple ne prétend pas qu’une cause unique explique toute panne de partage. Il montre comment construire un dossier compréhensible sans inventer des résultats techniques.

## 10. Bien communiquer pendant l’intervention

La communication doit être régulière, factuelle et adaptée à la personne destinataire. L’utilisateur a besoin de comprendre l’impact et la prochaine étape, pas de recevoir un flot de termes techniques sans explication.

### 10.1 Accuser réception

Exemple :

« Nous avons enregistré votre signalement concernant l’accès au dossier partagé. Nous vérifions actuellement le périmètre affecté et vous informerons de la prochaine étape. »

Cette réponse confirme la prise en compte sans annoncer une heure de résolution non confirmée.

### 10.2 Informer d’un retard

Exemple :

« Le premier contrôle n’a pas permis de confirmer la cause. Nous poursuivons les vérifications avec l’équipe compétente. Le service reste perturbé ; la prochaine mise à jour sera communiquée selon le rythme prévu par notre procédure. »

Il vaut mieux expliquer ce qui est connu et ce qui reste incertain que promettre une résolution sans preuve.

### 10.3 Confirmer le rétablissement

Exemple :

« Le service a été rétabli et les tests prévus ont été exécutés. Merci de confirmer que votre activité habituelle est de nouveau possible. Nous conserverons le ticket ouvert si un défaut persiste ou si une action complémentaire est nécessaire. »

### 10.4 Passer le relais à une autre équipe

Un transfert de qualité contient :

- la description du symptôme ;
- le périmètre et l’impact ;
- la chronologie ;
- les preuves disponibles ;
- les hypothèses déjà testées ;
- les résultats des contrôles ;
- les actions déjà réalisées ;
- les risques connus ;
- la question précise adressée à l’équipe suivante.

Évite le message « ça ne marche toujours pas ». Il ne permet pas au destinataire de savoir ce qu’il doit vérifier ni ce qui a déjà été tenté.

## 11. Les indicateurs simples de maintenance

Les indicateurs peuvent aider à comprendre la qualité du service, mais aucun chiffre ne doit être interprété sans contexte.

| Indicateur | Signification | Précaution |
|---|---|---|
| Temps moyen de réparation ou MTTR | Mesure de durée définie par l’organisation pour les réparations ou rétablissements. | Vérifier ce que le chronomètre inclut : diagnostic, attente de pièces, validation ou remise en service. |
| MTBF | Temps moyen entre défaillances d’un équipement réparable, selon une méthode de calcul définie. | Une moyenne ne prédit pas la date exacte de la prochaine panne. |
| Disponibilité | Proportion de temps où le service est disponible selon la définition retenue. | Préciser les périodes d’observation et les exclusions. |
| Résolution au premier contact | Part des demandes résolues dès le premier contact, selon la règle retenue. | Ne pas pousser à une résolution rapide si le problème exige une analyse approfondie. |
| Récurrence | Réapparition d’un incident similaire après une intervention. | Un incident peut sembler identique sans avoir la même cause ; vérifier les faits. |
| Respect du préventif planifié | Part des tâches préventives réalisées dans la période convenue. | Une tâche cochée n’est pas une preuve que le contrôle a été correctement fait. |
| Taille du backlog | Nombre ou volume des tâches en attente. | Tenir compte de l’âge, de la criticité et des dépendances, pas uniquement du total. |
| Satisfaction utilisateur | Retour des utilisateurs sur le service reçu. | Le résultat doit être analysé avec les délais, la qualité et la complexité des cas. |

### 11.1 Pourquoi un indicateur ne suffit pas

Une équipe peut fermer beaucoup de tickets sans résoudre les causes récurrentes. Un MTTR faible peut être obtenu au prix de dépannages temporaires qui entraînent de nouvelles interruptions. Un taux élevé de tâches préventives terminées ne garantit pas la qualité si les contrôles sont mal définis.

Il faut combiner les données : délais, récurrence, disponibilité, criticité, sécurité, qualité de la documentation et résultats de validation.

### Schéma 11 — Les indicateurs alimentent l’amélioration

~~~mermaid
flowchart LR
    A[Traces des interventions] --> B[Indicateurs]
    B --> C[Analyse des tendances]
    C --> D[Causes récurrentes et risques]
    D --> E[Actions d'amélioration]
    E --> F[Procédures et plans révisés]
    F --> A
~~~

## 12. Check-lists pratiques

Les check-lists ne remplacent pas une procédure spécialisée. Elles aident à ne pas oublier les étapes courantes.

### 12.1 Avant l’intervention

- [ ] La demande et le service concernés sont identifiés.
- [ ] Le symptôme et le périmètre sont suffisamment décrits.
- [ ] L’impact et la priorité sont évalués selon la règle locale.
- [ ] Le responsable et les personnes à informer sont identifiés.
- [ ] Les compétences et autorisations requises sont disponibles.
- [ ] Les documents, outils et pièces nécessaires sont prêts.
- [ ] Les risques et dépendances sont évalués.
- [ ] Les sauvegardes ou moyens de récupération requis sont vérifiés.
- [ ] Les critères de réussite sont définis.
- [ ] Le plan de retour arrière ou les conditions d’arrêt sont clairs.
- [ ] La fenêtre et l’impact attendu ont été communiqués.

### 12.2 Pendant l’intervention

- [ ] L’équipement visé est confirmé avant toute action.
- [ ] Les procédures et mesures de sécurité sont appliquées.
- [ ] Les actions restent dans le périmètre autorisé.
- [ ] Les résultats importants sont consignés au fur et à mesure.
- [ ] Les effets secondaires et changements de périmètre sont surveillés.
- [ ] Tout imprévu dangereux entraîne un arrêt et une réévaluation.

### 12.3 Après l’intervention

- [ ] Les tests techniques prévus sont exécutés et leurs résultats consignés.
- [ ] Le service est vérifié dans les conditions attendues.
- [ ] Les protections temporaires et l’environnement sont remis dans l’état prévu.
- [ ] Le demandeur ou propriétaire du service est informé.
- [ ] Les actions réalisées et les pièces utilisées sont enregistrées.
- [ ] Les limites ou risques résiduels sont explicitement décrits.
- [ ] Les tâches complémentaires ont un responsable et une échéance.
- [ ] L’historique de l’actif est mis à jour lorsque nécessaire.
- [ ] Le ticket est fermé uniquement si les critères de clôture sont satisfaits.

## 13. Travaux pratiques guidés

Les situations ci-dessous sont des exercices de méthode. Elles doivent être réalisées sur des exemples fictifs ou dans un environnement autorisé, sans appliquer d’action risquée sur la production.

### TP 1 — Transformer un signalement vague en ticket utile

**Situation :** un utilisateur écrit : « L’informatique ne marche plus, venez vite. »

**Étape 1 : poser des questions utiles.**

Demande quelle fonction ne marche plus, depuis quand, quel message apparaît, si d’autres utilisateurs sont concernés et si une opération récente est connue. Ne demande pas de mot de passe.

**Étape 2 : établir une description factuelle.**

Exemple de ticket après clarification :

- **Titre :** accès au dossier partagé impossible depuis le poste utilisateur ;
- **Symptôme :** le chemin habituel renvoie un message d’accès refusé ;
- **Début observé :** vers 10 h, à confirmer ;
- **Périmètre :** un utilisateur confirmé, autres utilisateurs non encore vérifiés ;
- **Impact :** activité documentaire retardée ;
- **Actions déjà faites :** aucune action de correction exécutée ;
- **Prochaine étape :** vérifier l’identité du service, le périmètre et les autorisations selon la procédure ;
- **Priorité :** à déterminer après évaluation de l’impact et de l’urgence.

**Correction attendue :** le ticket décrit le comportement observé, distingue les faits des hypothèses et précise une prochaine étape. Il ne conclut pas que le serveur ou le réseau est défaillant avant les contrôles.

### TP 2 — Décider si une intervention peut commencer

**Situation :** une tâche planifiée consiste à modifier un paramètre sur un équipement réseau. L’intervenant a accès à l’équipement, mais la procédure de retour arrière n’est pas disponible et personne n’a confirmé la fenêtre d’intervention.

**Questions :**

1. Le fait d’avoir un accès technique suffit-il pour démarrer ?
2. Quelles conditions sont manquantes ?
3. Quelle décision dois-tu prendre ?
4. Que faut-il enregistrer ?

**Correction :**

1. Non. L’accès technique ne vaut pas autorisation d’effectuer une modification de production.
2. Il manque au minimum la confirmation de la fenêtre, la méthode approuvée, les critères de réussite et les conditions de retour arrière adaptées au risque.
3. Reporter ou suspendre le démarrage, puis obtenir les validations et informations nécessaires.
4. Documenter les prérequis manquants, informer le responsable et ne reprendre qu’après réévaluation et autorisation.

**Compétence évaluée :** savoir reconnaître qu’une tâche n’est pas prête, même si sa partie technique semble facile.

### TP 3 — Construire un compte rendu

**Situation :** après contrôle, un technicien remplace un câble défectueux. La liaison revient, mais le service n’a pas encore été testé par un utilisateur.

**Mauvaise conclusion :** « Tout est réparé, problème définitivement résolu. »

**Compte rendu acceptable :**

- **Constat :** la liaison ne fonctionnait pas avant intervention ;
- **Action :** remplacement du câble identifié comme défectueux ;
- **Résultat technique :** la liaison est revenue lors du contrôle effectué ;
- **Validation restante :** vérifier le service applicatif avec un utilisateur autorisé et confirmer l’absence d’anomalie persistante ;
- **Statut :** en attente de validation finale selon la procédure.

**Correction attendue :** le technicien ne prétend pas avoir vérifié un résultat qu’il n’a pas encore observé. La clôture dépend des critères définis.

## 14. Exercices d’application avec corrigés

### Exercice 1 — Incident ou demande de service ?

Classe chaque situation : incident, demande de service ou tâche préventive.

A. Une application utilisée quotidiennement ne s’ouvre plus alors qu’elle fonctionnait auparavant.

B. Un collaborateur demande l’installation d’un logiciel autorisé.

C. Un contrôle périodique de l’état des batteries est prévu dans le planning.

**Corrigé :** A est un incident, B est une demande de service et C est une tâche de maintenance préventive. La catégorie précise peut dépendre du catalogue de services de l’organisation.

### Exercice 2 — Symptôme ou cause ?

Un utilisateur indique : « Le serveur est cassé parce que mon dossier est inaccessible. »

Quel est le fait établi ? Quelle est la cause ?

**Corrigé :** le fait établi est que l’utilisateur ne peut pas accéder au dossier, si ce symptôme a bien été confirmé. La cause n’est pas encore connue : serveur, réseau, authentification, droits ou autre élément peuvent expliquer le problème.

### Exercice 3 — Que faut-il prioriser ?

Un poste de test isolé présente une anomalie mineure. Au même moment, plusieurs équipes ne peuvent plus accéder à un service indispensable à leur travail.

Quelle situation doit généralement être évaluée en premier ?

**Corrigé :** l’indisponibilité qui affecte plusieurs équipes doit normalement recevoir une priorité plus élevée, sous réserve de la matrice locale et des risques particuliers. Le nombre d’utilisateurs, la criticité du service et les conséquences métier sont des facteurs importants.

### Exercice 4 — Faut-il redémarrer immédiatement ?

Une application répond lentement. Aucun diagnostic n’a encore été effectué. Un technicien propose de redémarrer le serveur qui l’héberge.

**Corrigé :** pas sans évaluation. Il faut d’abord confirmer le périmètre, recueillir les preuves disponibles, vérifier les dépendances et déterminer si le redémarrage est autorisé et proportionné. Un redémarrage peut rétablir le service, mais aussi interrompre d’autres applications ou faire perdre des informations utiles au diagnostic.

### Exercice 5 — Peut-on clôturer ?

Après remplacement d’un composant, le voyant de l’équipement est vert. Aucun test de la fonction attendue n’a été exécuté.

**Corrigé :** le voyant est une observation utile, mais il ne suffit pas nécessairement à confirmer le service. Il faut réaliser les tests définis, noter les résultats et obtenir la validation requise avant de déclarer le travail terminé.

### Exercice 6 — Une tâche hors compétence

Un technicien débutant constate qu’une réparation nécessite une opération électrique pour laquelle il n’a pas d’habilitation.

**Corrigé :** il doit cesser cette partie de l’intervention, sécuriser la situation selon les consignes locales, informer le responsable et faire intervenir une personne qualifiée. Il ne doit pas improviser ni contourner la protection.

### Exercice 7 — Identifier les informations manquantes

Compte rendu : « J’ai changé le composant et ça marche. »

Nomme cinq informations qui pourraient rendre ce compte rendu exploitable.

**Corrigé possible :** équipement concerné, symptôme initial, composant remplacé, tests exécutés et résultats, heure de l’intervention, pièce utilisée, autorisation ou ordre de travail, état final, éventuelles limites et validation du service.

### Exercice 8 — Dépannage ou correction durable ?

Après une défaillance, un service est basculé sur une solution de secours. La cause de la panne n’est pas connue.

Comment décrire l’état et quelle suite prévoir ?

**Corrigé :** le service est rétabli ou partiellement rétabli au moyen d’un contournement, selon les tests réellement réalisés. La cause reste à déterminer. Il faut documenter le risque résiduel, attribuer l’analyse complémentaire et fixer une échéance de suivi.

### Exercice 9 — Un indicateur est-il suffisant ?

Une équipe ferme davantage de tickets que le mois précédent, mais le nombre d’incidents récurrents augmente.

**Corrigé :** le volume de clôture ne suffit pas à conclure que la maintenance s’améliore. Il faut examiner la récurrence, la qualité de résolution, la criticité, les délais, les résultats de validation et les causes des incidents répétés.

### Exercice 10 — Vrai ou faux ?

1. Une intervention peut être considérée comme terminée dès que la manipulation technique est effectuée.
2. Une hypothèse de diagnostic doit être distinguée d’une cause confirmée.
3. Une autorisation technique donne automatiquement le droit de modifier la production.
4. Le retour d’expérience peut conduire à modifier le plan préventif.
5. Si les risques changent pendant l’intervention, la préparation doit être réévaluée.

**Corrigé :**

1. Faux : il faut contrôler le résultat et réaliser les étapes de restitution prévues.
2. Vrai.
3. Faux : autorisation d’accès et autorisation de changement sont distinctes.
4. Vrai.
5. Vrai.

## 15. Défi final corrigé — Organiser une intervention de bout en bout

### Le scénario

Tu es technicien débutant dans une entreprise de distribution. À 14 h 05, le helpdesk reçoit trois signalements : des collaborateurs ne peuvent plus accéder à l’application de gestion des stocks, un poste situé dans un autre bureau semble fonctionner normalement et la supervision a enregistré une alerte réseau peu avant le premier appel.

Le responsable métier indique que les préparations de commandes sont ralenties. Une intervention planifiée sur un équipement réseau doit aussi avoir lieu dans l’après-midi, mais tu ne sais pas encore si elle a un lien avec l’incident.

Tu dois préparer une prise en charge. Les seules informations confirmées sont les signalements et l’alerte. La cause exacte n’est pas connue.

### Partie A — Qualification initiale

Rédige un titre et une description factuelle. Évalue les questions à poser et les informations à conserver.

**Correction proposée :**

- **Titre :** accès à l’application de gestion des stocks perturbé pour plusieurs utilisateurs ;
- **Heure de détection :** premiers signalements reçus à 14 h 05 ;
- **Impact provisoire :** préparation des commandes ralentie ;
- **Périmètre connu :** plusieurs collaborateurs signalent le défaut ; un poste dans un autre bureau semble fonctionner ;
- **Signal associé :** une alerte réseau a été enregistrée peu avant le premier appel ;
- **Cause :** inconnue ;
- **Prochaine action :** confirmer le périmètre, identifier le service et les équipements concernés, consulter les données autorisées et rechercher les changements récents.

L’alerte réseau n’est pas automatiquement la cause. Elle est une preuve à analyser parmi d’autres.

### Partie B — Priorité et coordination

Explique comment choisir la priorité et pourquoi l’intervention planifiée doit être examinée.

**Correction proposée :**

L’impact métier et le nombre d’utilisateurs justifient une évaluation rapide. La priorité finale dépend de la matrice et des règles de l’organisation, de la criticité de l’application et de l’évolution du périmètre.

L’intervention planifiée doit être vérifiée car elle pourrait être liée à l’incident ou affecter les contrôles en cours. Il faut consulter le planning et le responsable avant de décider de la maintenir, de la reporter ou de la coordonner. Une modification supplémentaire non évaluée risque de compliquer le diagnostic.

### Partie C — Diagnostic raisonné

Propose quatre contrôles initiaux sans supposer la cause.

**Correction possible :**

1. confirmer quelles personnes, zones et fonctions sont affectées ;
2. comparer les observations entre le poste qui fonctionne et ceux qui ne fonctionnent pas, dans les limites autorisées ;
3. consulter l’heure et le contenu de l’alerte de supervision ainsi que les journaux disponibles ;
4. vérifier les changements récents et les dépendances entre application, réseau et systèmes hébergeant le service.

Pour chaque contrôle, il faut noter l’observation et ce qu’elle confirme ou écarte. Les commandes et actions qui modifient la production ne doivent être lancées qu’après autorisation et préparation adaptées.

### Partie D — Conditions de démarrage

Liste les conditions à réunir si un changement technique devient nécessaire.

**Correction proposée :**

Il faut avoir un diagnostic suffisamment étayé pour justifier l’action, un périmètre identifié, une autorisation appropriée, un responsable, une évaluation des risques, une fenêtre coordonnée lorsque nécessaire, une procédure adaptée, les moyens de récupération ou de retour arrière requis, des critères de test, des personnes à prévenir et un plan de communication.

Si l’une des conditions indispensables à la sécurité manque, le technicien doit suspendre ou escalader la tâche au lieu de démarrer par défaut.

### Partie E — Validation et clôture

Après l’action, les utilisateurs indiquent que l’application s’ouvre. Quelles vérifications restent à réaliser ?

**Correction proposée :**

L’ouverture est un premier résultat, mais il faut vérifier les fonctions attendues, notamment l’accès aux données autorisées et le parcours métier nécessaire. Il faut consulter les indicateurs et journaux pertinents, vérifier l’absence d’anomalie persistante et s’assurer que les autres services dépendants restent stables.

Le compte rendu doit noter les tests réellement exécutés. Si l’analyse de cause racine n’est pas terminée, la résolution de l’incident ne doit pas être présentée comme une preuve que la cause durable a été éliminée. Une tâche de suivi peut être nécessaire pour analyser la récurrence et améliorer la prévention.

### Critères de réussite du défi

Le défi est réussi si tu peux :

- décrire l’incident sans inventer la cause ;
- expliquer la priorité à partir de l’impact et de l’urgence ;
- proposer des contrôles qui permettent de distinguer plusieurs hypothèses ;
- identifier les autorisations et risques avant une modification ;
- définir des tests qui vérifient le service et pas seulement un équipement ;
- produire un compte rendu qui sépare faits, actions, résultats et suites à donner.

## 16. Les réflexes à retenir

La qualité d’une intervention se construit sur toute sa durée.

1. **Comprendre avant d’agir.** Un symptôme est un point de départ, pas un diagnostic définitif.
2. **Prioriser selon le risque et l’impact.** Le volume de demandes ou la pression d’un demandeur ne doit pas remplacer les règles de priorité.
3. **Préparer l’intervention.** Les outils, pièces, compétences, autorisations, tests et moyens de récupération sont des éléments du travail technique.
4. **Protéger les personnes et les données.** Si une opération dépasse les moyens de prévention ou les compétences disponibles, il faut s’arrêter et demander de l’aide.
5. **Agir dans un périmètre autorisé.** Une réparation ne donne pas le droit d’ajouter des modifications non évaluées.
6. **Tester la fonction attendue.** Un équipement allumé ou une alerte disparue ne prouvent pas nécessairement que le service fonctionne.
7. **Documenter les faits.** Les actions, résultats, limites et risques restants doivent être compréhensibles par un autre intervenant.
8. **Apprendre de chaque intervention.** Les tendances et incidents répétés doivent conduire à examiner les procédures, les plans préventifs et les moyens disponibles.

## 17. Pour approfondir

Les ressources suivantes ont servi à structurer les notions de préparation, de prévention, de remise en service et de contrôle des énergies. Les procédures internes et les règles applicables sur le lieu d’intervention restent prioritaires.

- [INRS — Organisation de la maintenance : prévention et organisation du travail](https://www.inrs.fr/risques/maintenance/prevention.html). Recommandations sur la préparation des interventions, les moyens, les risques, la coordination, les essais, la restitution du service et le retour d’expérience.
- [INRS — Fiche pratique ED 129 : Maintenance](https://www.inrs.fr/media.html?refINRS=ED+129). Présente les étapes incontournables d’un processus de maintenance, avant, pendant et après l’intervention.
- [INRS — Publications sur la prévention des risques en maintenance](https://www.inrs.fr/risques/maintenance/publications-outils-liens-utiles). Point de départ pour retrouver les supports sur la prévention et les consignations.
- [OSHA — Control of Hazardous Energy, 29 CFR 1910.147](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147). Exemple de cadre détaillant la maîtrise des énergies dangereuses pendant certaines opérations de maintenance. Les exigences exactes applicables varient selon la juridiction, l’équipement et le lieu.

La prochaine étape du parcours approfondira des compétences plus spécialisées : outils de diagnostic, maintenance matérielle et systèmes, helpdesk, planification préventive et reporting. Ces sujets pourront compléter ce cours sans le transformer en simple catalogue de procédures techniques.
