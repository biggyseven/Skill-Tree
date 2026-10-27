# Gestion de crise et Plan de Reprise

> **Mise en contexte —** Une organisation ne démontre pas sa résilience en possédant un document intitulé « PRA », en ayant des sauvegardes ou en affichant deux centres de données. Elle la démontre quand les bonnes personnes peuvent prendre des décisions explicites sous pression, quand les activités prioritaires sont connues, quand les dépendances ont été vérifiées, quand la restauration fonctionne réellement et quand les résultats sont validés par le métier. Une crise peut commencer par une panne, une erreur de changement, un incendie, une rupture fournisseur, une corruption de données ou une compromission d’identités. Le déclencheur est technique, mais les conséquences touchent souvent les clients, les équipes, les finances, les engagements contractuels et la confiance. Le professionnel expert doit donc relier gouvernance, processus métier, architecture technique, sécurité, communication et amélioration continue.

## Objectifs pédagogiques et critères de maîtrise

À l’issue de ce cours, l’apprenant devra être capable de :

- distinguer la gestion d’incident, la gestion de crise, le plan de continuité d’activité (PCA), le plan de reprise d’activité (PRA) et la réponse à incident de cybersécurité, sans isoler artificiellement des dispositifs qui doivent coopérer ;
- établir des critères d’activation, désigner les rôles de décision et maintenir une situation opérationnelle partagée ;
- conduire une analyse d’impact métier (BIA) documentée, avec des hypothèses, des propriétaires, des conséquences temporelles et des priorités défendables ;
- différencier le MTPD, le RTO, le RPO et le niveau minimal de service, puis vérifier la cohérence entre ces objectifs ;
- représenter les dépendances de bout en bout, notamment les identités, le DNS, les certificats, les secrets, les fournisseurs, les opérateurs et les mécanismes de contrôle cloud ;
- comparer des stratégies de reprise selon le risque, le coût, la complexité, la capacité, la cohérence des données et le délai réel d’activation ;
- rédiger un runbook utilisable par une équipe de relève, avec préconditions, autorisations, étapes, preuves, contrôles, points d’arrêt et retour arrière ;
- coordonner une reprise pendant une suspicion de compromission sans réintroduire un environnement hostile ni détruire les preuves utiles ;
- préparer des communications adaptées aux équipes, aux décideurs, aux clients et aux autorités compétentes, sans spéculer sur la cause ou le délai de résolution ;
- concevoir des exercices sûrs et mesurables, exploiter les écarts et vérifier l’efficacité des actions correctives ;
- présenter une décision de reprise avec les faits disponibles, les incertitudes, les options étudiées, les risques résiduels et l’autorité qui approuve.

La maîtrise experte ne se réduit pas à réciter des définitions. Elle consiste à justifier un choix, à exposer ses limites, à produire des preuves et à rendre le dispositif exécutable par d’autres personnes.

## Prérequis et cadre de responsabilité

Ce cours s’adresse à une personne qui connaît les processus de support, les services informatiques et la documentation technique. Une expérience de la gestion des changements, des sauvegardes, de la supervision, de la sécurité et des environnements de production est utile. Les notions sont expliquées dans le cours, mais les ateliers supposent de savoir décrire un service, lire un journal d’événements et distinguer une hypothèse d’un fait établi.

Les exemples sont pédagogiques. Les objectifs, rôles, délais et obligations doivent être adaptés à l’organisation, au secteur, au pays, aux contrats et aux exigences réellement applicables. Aucune valeur illustrative de RTO ou de RPO ne doit être adoptée sans validation métier et technique. Ce cours ne remplace ni les procédures internes approuvées, ni le conseil juridique, ni les règles de sécurité, ni les autorisations de changement. Une personne ne doit pas effectuer une bascule en production, modifier une source de données ou interrompre un service au seul motif qu’un exemple du cours le suggère.

Avant une action risquée, confirmer au minimum : le but recherché, le périmètre, l’autorité qui autorise, les préconditions, les conséquences possibles, la preuve attendue, le critère d’arrêt, le plan de retour et la personne qui doit être informée. Si l’intégrité des données ou la sécurité des personnes est incertaine, rendre l’incertitude explicite et demander l’arbitrage prévu.

## 1. Vocabulaire, frontières et modèle mental

| Terme | Sens opérationnel |
|---|---|
| Incident | Événement qui perturbe ou menace un service et qui peut être traité dans un processus défini. |
| Crise | Situation dans laquelle l’impact, l’incertitude, la durée ou les interdépendances imposent une coordination et des décisions renforcées. |
| Cellule de crise | Groupe habilité à coordonner les décisions interfonctionnelles et à suivre la situation. |
| PCA | Dispositif pour maintenir les activités prioritaires à un niveau défini malgré la perturbation. |
| PRA | Procédures, moyens et critères pour restaurer des capacités après une interruption. Le sigle est parfois employé pour des périmètres larges : préciser toujours le périmètre local. |
| Réponse à incident cyber | Actions de préparation, détection, analyse, confinement, éradication et récupération d’un événement de sécurité. |
| BIA | Analyse des conséquences métier d’une interruption et des capacités nécessaires pour limiter ces conséquences. |
| MTPD | Période maximale pendant laquelle l’activité peut être perturbée avant que les conséquences deviennent inacceptables, selon la méthode de l’organisation. |
| RTO | Objectif de délai de rétablissement d’un service à un niveau convenu, dans un scénario défini. |
| RPO | Point de récupération visé pour les données ; il détermine la perte de données tolérable dans le scénario considéré. |
| Niveau minimal de service | Capacité minimale nécessaire pour continuer une activité critique ; elle peut être inférieure au service nominal. |
| Mode dégradé | Fonctionnement temporaire limité, avec capacités, contrôles, responsabilités et critères de sortie explicites. |
| Bascule | Passage du service d’un environnement ou d’un chemin à un autre. |
| Retour arrière | Action qui ramène à un état antérieur connu ou à une stratégie de repli si l’opération échoue. |
| Retour au site ou au service nominal | Retour planifié après usage du dispositif de secours. Ce n’est pas nécessairement un simple inversement de la bascule. |
| REX / RETEX | Retour d’expérience structuré, centré sur les faits, les facteurs contributifs et les améliorations à vérifier. |

### Les quatre questions à ne pas confondre

La gestion de crise répond à : qui coordonne, qui arbitre, quelles priorités et quelle communication ? La continuité répond à : comment maintenir l’activité essentielle pendant la perturbation ? La reprise répond à : comment restaurer les capacités, les données et les dépendances ? La réponse cyber répond à : comment comprendre et contenir la compromission, préserver les preuves et retrouver un environnement digne de confiance ?

Ces fonctions sont distinctes, mais elles se chevauchent. Une attaque par rançongiciel peut nécessiter simultanément une cellule de crise, l’activation d’un PCA manuel, le confinement cyber, une reprise technique depuis un environnement propre et une évaluation des obligations de notification. Une équipe ne doit pas attendre qu’une autre ait fini pour coordonner les décisions interdépendantes.

~~~mermaid
flowchart TD
  A[Événement perturbateur] --> B[Coordination de crise]
  B --> C[Priorités et décisions]
  C --> D[PCA : maintien minimal]
  C --> E[PRA : restauration]
  C --> F[Réponse cyber si nécessaire]
  D --> G[Validation métier]
  E --> G
  F --> H[Environnement maîtrisé]
  H --> E
  G --> I[Retour contrôlé et REX]
~~~

Le diagramme décrit une relation de coordination, pas une séquence obligatoire. Selon le scénario, le maintien métier peut commencer avant la reprise technique, et le confinement cyber peut suspendre temporairement une restauration. Le plan local doit préciser les dépendances entre ces fonctions.

## 2. Gouvernance de résilience et critères d’activation

### 2.1 Préparer avant l’événement

Une cellule de crise ne devrait pas découvrir en pleine perturbation qui peut autoriser une communication, approuver une dépense urgente, déclencher une bascule ou accepter un risque résiduel. La gouvernance doit exister avant l’événement. Elle définit le périmètre des services couverts, les critères d’activation, les responsables principaux et suppléants, les délégations de décision, les canaux de secours, la tenue du journal de décision et les critères de clôture.

Les coordonnées et procédures ne doivent pas dépendre exclusivement du système susceptible d’être indisponible. Prévoir des copies hors ligne contrôlées, des moyens de contact alternatifs, des accès d’urgence protégés et un processus d’authentification de secours. « Accessible hors ligne » ne veut pas dire « exposé sans protection » : les copies sensibles restent limitées, traçables et périodiquement vérifiées.

Les seuils doivent être compréhensibles en situation stressante. Un déclencheur peut être lié à la sécurité des personnes, à l’indisponibilité d’un service critique, à une suspicion de compromission de comptes privilégiés, à une corruption de données, à la perte d’un site, à l’indisponibilité d’un fournisseur incontournable ou au risque de dépasser un objectif de continuité. Chaque organisation fixe ses seuils selon son appétit au risque et ses obligations.

Il est utile de séparer le signal d’activation de la certitude sur la cause. Une cellule peut être activée à titre provisoire lorsque l’impact possible est élevé et les faits incomplets. Cette activation met les décideurs en relation et autorise une collecte coordonnée ; elle ne constitue pas une déclaration que le pire scénario est confirmé. L’activation provisoire doit être réévaluée à un moment défini et conservée dans le journal.

### 2.2 Un algorithme simple, mais gouverné

~~~mermaid
flowchart TD
  A[Alerte reçue] --> B[Confirmer source et heure]
  B --> C[Évaluer sécurité, portée et services]
  C --> D{Critère d'activation atteint ou incertain avec impact élevé ?}
  D -->|Non| E[Gestion normale et surveillance]
  D -->|Oui| F[Activer ou activer provisoirement]
  F --> G[Nommer coordinateur et suppléants]
  G --> H[Ouvrir journal et situation commune]
  H --> I[Réévaluer seuils à heure fixée]
  I --> J{Crise confirmée ?}
  J -->|Oui| K[Conduite de crise]
  J -->|Non| L[Désescalade consignée]
~~~

Une procédure d’activation doit répondre à six questions : qui peut déclarer l’activation, qui peut le remplacer, quels signaux la déclenchent, comment joindre la cellule, où se trouvent les documents et quand le statut sera réévalué. En dehors des heures ouvrées, le dispositif doit rester exécutable. Un plan qui exige une personne toujours disponible n’est pas robuste.

### 2.3 Gravité, priorité et incertitude

Un score de gravité peut aider à standardiser la discussion, mais il ne remplace pas le jugement. Une matrice peut considérer l’impact métier, l’étendue, la durée estimée, la sécurité, l’intégrité des données, la dépendance fournisseur et la confiance dans le diagnostic. Les règles doivent indiquer quels critères imposent une escalade immédiate, même si le score total paraît modéré. Un risque vital ou une compromission probable d’identifiants d’administration ne doit pas être compensé par plusieurs indicateurs verts.

Ne pas confondre « faible confiance dans les faits » et « faible gravité ». Une petite quantité d’informations fiables peut imposer une posture prudente si les conséquences possibles sont importantes. À l’inverse, une alerte bruyante mais circonscrite peut rester dans la chaîne normale, à condition que les critères soient confirmés.

### 2.4 Rôles, délégations et séparation des décisions

Les rôles courants sont les suivants, mais les intitulés peuvent varier :

- **Sponsor ou responsable exécutif :** arbitre les enjeux majeurs, fournit les ressources et décide des risques qui dépassent les délégations opérationnelles.
- **Coordinateur de crise :** maintient la situation commune, organise le rythme de décision, suit les actions et fait remonter les arbitrages nécessaires.
- **Responsable de l’incident technique :** conduit l’analyse et les opérations techniques dans le cadre autorisé.
- **Propriétaire métier :** définit les capacités minimales, les priorités métier, les contrôles manuels et confirme l’acceptabilité du service restauré.
- **Responsable sécurité :** conseille sur le confinement, l’intégrité, les preuves, les accès et les critères d’un retour en environnement de confiance.
- **Responsable communication :** prépare et diffuse les messages validés pour chaque audience.
- **Journaliste de crise ou secrétaire :** horodate les faits, décisions, responsables, engagements et modifications de statut.
- **Responsables RH, juridique, conformité, achats ou fournisseurs :** sont mobilisés selon le scénario et les obligations réelles.

Une même personne peut porter plusieurs rôles dans une petite organisation, mais la séparation des décisions critiques reste à prévoir. Si le responsable technique exécute une restauration, il ne doit pas être le seul à déclarer que les contrôles métier et de sécurité sont satisfaits. Une validation indépendante, proportionnée au risque, réduit les erreurs d’angle mort.

| Décision | Prépare l’analyse | Autorité à identifier dans le plan | Preuve attendue |
|---|---|---|---|
| Activer la crise | Astreinte ou responsable de service | Rôle d’activation désigné | Heure, critère déclenché, portée initiale |
| Déclarer un mode dégradé | Propriétaire métier et opérations | Autorité métier désignée | Capacités et limites acceptées |
| Démarrer une restauration | Opérations / propriétaire de la plateforme | Autorité de changement ou de crise | Source, périmètre, préconditions et plan d’arrêt |
| Déclarer un environnement cyber propre | Sécurité et équipes techniques | Rôle sécurité / risque défini localement | Contrôles d’intégrité, accès et traces |
| Valider le service métier | Utilisateur référent / propriétaire métier | Propriétaire du service | Scénarios métier et critères d’acceptation réussis |
| Clôturer la crise | Coordinateur et responsables concernés | Autorité prévue par la gouvernance | Statut, risques résiduels et actions suivies |

Cette matrice est un modèle à adapter, non une délégation universelle. L’organisation doit documenter les conflits d’intérêts, les suppléances et les situations dans lesquelles une autorité normale est elle-même indisponible.

## 3. Conduite de crise : situation commune et qualité des décisions

### 3.1 Construire une image opérationnelle partagée

Dès l’activation, le coordinateur crée une situation commune, parfois appelée *common operating picture*. Elle peut être tenue dans un document protégé ou un outil dédié, mais elle doit être accessible aux rôles concernés et survivre à l’indisponibilité du service principal. Elle réunit :

- l’heure de début et les événements importants ;
- les services et populations touchés, avec le périmètre encore inconnu ;
- les faits confirmés séparés des hypothèses ;
- les effets observés et les impacts métier possibles ;
- les actions en cours, leur responsable et leur prochaine échéance ;
- les décisions prises, leur autorité, leur justification et leurs conditions ;
- les risques, les dépendances et les ressources manquantes ;
- le prochain point de synchronisation et le prochain message destiné aux parties prenantes.

Une phrase comme « le système est revenu » est insuffisante. Préciser quel système, depuis quand, pour quels utilisateurs, selon quel test, avec quelle intégrité de données et avec quelles limites connues.

### 3.2 Tenir un journal de décision

Le journal n’est ni un chat recopié ni un historique exhaustif de toutes les commandes. C’est une trace chronologique qui permet de comprendre qui savait quoi, quand une décision a été prise, quelle hypothèse la justifiait et quel résultat a suivi. Une entrée utile contient l’heure avec fuseau si plusieurs sites sont impliqués, le fait ou l’incertitude, la décision, les options considérées, le décideur, le responsable d’exécution, l’échéance, le résultat et le prochain point de contrôle.

Exemple :

| Heure | Élément | Décision ou action | Responsable | Condition / résultat |
|---|---|---|---|---|
| 09:12 | Échecs répétés de connexion à l’application de commandes | Ouvrir l’incident majeur et qualifier la portée | Astreinte | Périmètre encore à confirmer |
| 09:24 | Service identité dégradé sur deux sites | Activer provisoirement la cellule | Responsable d’activation | Réévaluation à 09:45 |
| 09:38 | Intégrité des sauvegardes non confirmée | Interdire la restauration depuis la dernière image jusqu’au contrôle | Sécurité + opérations | Préserver les copies candidates |
| 10:05 | Procédure manuelle validée par le métier | Autoriser un mode dégradé limité | Propriétaire métier | Plafond de transactions et rapprochement obligatoires |
| 10:50 | Service restauré en environnement de secours | Démarrer la validation fonctionnelle | Responsable de service | Pas encore de clôture |

Les heures et éléments de cet exemple sont fictifs. Le but est de montrer la structure. Un journal opérationnel réel doit contenir les faits issus de sources observables.

### 3.3 Rythme de coordination

Une crise nécessite un rythme de synchronisation défini. Au début, les points peuvent être rapprochés ; ils s’espacent lorsque la situation devient stable. Chaque point doit répondre aux mêmes questions : qu’est-ce qui a changé, quel impact est confirmé, que fait-on maintenant, quelles décisions sont attendues, quels obstacles persistent et quand informe-t-on la prochaine fois ? Cela évite des réunions longues où chaque équipe répète ses activités sans résoudre les dépendances.

Pendant le point de coordination, traiter les décisions transverses et les obstacles. Les investigations détaillées restent dans les groupes techniques. Le coordinateur doit éviter que plusieurs équipes appliquent simultanément des changements incompatibles. Une liste d’actions comporte un seul responsable principal par action, même si plusieurs contributeurs sont mobilisés.

La fatigue est un risque opérationnel. Prévoir une relève, transmettre l’état courant, conserver les hypothèses, signaler les changements en cours et documenter les accès temporaires. La passation doit inclure ce qui a échoué et ce qui ne doit surtout pas être répété, pas seulement la liste des tâches restantes.

### 3.4 Décider sous incertitude

Une décision experte n’exige pas de connaître parfaitement la cause ; elle exige de comprendre les conséquences de l’action, les conditions de sécurité et ce qui ferait réviser la décision. Décrire les options, le bénéfice attendu, les risques, la réversibilité, le délai, la preuve nécessaire et l’autorité d’approbation.

Lorsqu’un désaccord persiste, formuler la question à trancher, exposer les faits qui soutiennent chaque option, préciser les risques de l’attente et solliciter la personne habilitée. Le coordinateur ne doit pas transformer un désaccord technique en compétition personnelle. Une décision peut être contestée et rester applicable jusqu’à son réexamen, sauf si une condition d’arrêt définie est déclenchée.

## 4. Réaliser une analyse d’impact métier de niveau expert

### 4.1 Partir de l’activité, pas du serveur

La BIA décrit les conséquences d’une interruption sur l’activité. Elle commence par les produits, services, opérations et populations dépendantes. Un serveur peut être techniquement important sans être le premier service à restaurer. Inversement, un outil apparemment secondaire peut devenir critique s’il est le seul moyen d’authentifier les opérateurs, d’émettre une commande ou d’identifier un client.

Pour chaque activité, identifier le propriétaire métier, le service rendu, les périodes de pointe, les volumes, les données nécessaires, les alternatives manuelles, les obligations, les fournisseurs, les personnes indispensables et les dépendances techniques. Interroger les personnes qui exécutent vraiment le processus. Les organigrammes et inventaires d’actifs sont des sources de départ, pas une preuve que le flux réel est compris.

### 4.2 Étudier l’impact dans le temps

Les conséquences évoluent. Une interruption de dix minutes peut être absorbable, alors qu’une interruption de plusieurs heures entraîne une accumulation de commandes, la perte d’une fenêtre de traitement, des pénalités ou un risque pour les personnes. Il faut recueillir les impacts selon plusieurs horizons et pour plusieurs dimensions :

- **Opérationnelle :** volumes non traités, files d’attente, retards, indisponibilité des compétences ou des installations.
- **Financière :** revenu perdu, heures supplémentaires, coût de reprise, frais de prestataires, pénalités éventuelles.
- **Client et réputation :** incapacité à servir, confiance, délais de réponse et qualité des informations.
- **Réglementaire et contractuelle :** obligations applicables, délais d’information ou de traitement, conservation de preuves.
- **Sécurité et environnement :** risques pour les personnes, les équipements, les données et les installations.
- **Intégrité :** transactions en double, commandes perdues, états divergents ou impossibilité de prouver une opération.
- **Interdépendance :** effet sur d’autres activités, sites, filiales ou partenaires.

Le montant financier ne doit pas être le seul critère. Une activité peu rentable peut être essentielle pour la sécurité, le respect d’une obligation ou la protection d’autres services.

### 4.3 Différencier MTPD, RTO et RPO

Le **MTPD** représente la période maximale tolérable de perturbation selon les critères métier retenus. Le **RTO** est l’objectif de délai de reprise du service défini dans un scénario donné. Le **RPO** est le point de récupération des données visé. Ce sont des objectifs distincts.

Un RTO ne signifie pas que toutes les fonctions du service doivent revenir simultanément au niveau nominal. Le plan peut prévoir une étape de service minimal dans un délai, puis une restauration des fonctions complètes dans un autre. Le niveau minimal doit avoir des critères concrets : opérations autorisées, débit maximal, population concernée, contrôles supplémentaires, limitations et durée acceptable.

Le RPO ne se lit pas comme « la sauvegarde tourne toutes les quatre heures » sans vérifier le mécanisme. Une sauvegarde périodique de quatre heures peut donner un RPO inférieur ou supérieur selon les heures d’exécution, la cohérence applicative, les journaux nécessaires et le scénario de corruption. Une réplication quasi temps réel peut réduire la perte après une panne physique, mais elle peut aussi propager une suppression ou une corruption logique. Le RPO doit donc être confirmé par des tests de restauration et de cohérence dans des scénarios représentatifs.

La relation recherchée est généralement : le délai de reprise cible doit laisser une marge avant le seuil où l’impact devient inacceptable. Il faut inclure le temps de détection, de décision, d’accès aux ressources, de restauration, de validation, de communication et de stabilisation. Si le RTO suppose que les opérateurs peuvent commencer en cinq minutes mais que le plan nécessite une autorisation qui prend habituellement quarante minutes, l’objectif est incohérent.

~~~mermaid
flowchart LR
  A[Interruption détectée] --> B[Qualifier et décider]
  B --> C[Activer les ressources]
  C --> D[Restaurer les dépendances]
  D --> E[Restaurer le service minimal]
  E --> F[Valider les données et le métier]
  F --> G[Stabiliser et augmenter la capacité]
  G --> H[Service nominal]
~~~

Le temps mesuré pour évaluer le RTO doit commencer au point défini par la méthode interne et s’arrêter au point de service convenu. Si l’organisation mesure seulement le temps de restauration d’une machine virtuelle, elle mesure une étape technique et non nécessairement la reprise du service.

### 4.4 Étude chiffrée : service de commande

Supposons un service de commandes qui permet à 120 agents de saisir environ 600 commandes par heure pendant les heures de pointe. Il alimente la préparation des expéditions, l’entrepôt et la facturation. Le responsable métier estime qu’une interruption supérieure à trois heures durant la période de pointe entraîne un retard difficilement récupérable dans la journée. Pour l’exercice, le MTPD retenu est de trois heures, le RTO cible est de deux heures et le RPO est de quinze minutes. Ces valeurs ne sont pas des recommandations universelles : elles illustrent le raisonnement.

L’inventaire initial indique que l’application dépend du service d’identité, du DNS, d’un certificat applicatif, d’une base de données, d’une file de messages et d’une liaison vers le système d’expédition. Le runbook de reprise semble estimer une restauration de la base à quarante minutes, le démarrage de l’application à vingt minutes et les tests fonctionnels à vingt minutes. Il ne prévoit pourtant pas la récupération du service d’identité ni la reconstruction de la file de messages.

Le RTO apparent est alors incomplet. Les étapes manquantes pourraient consommer une part importante des deux heures. Le plan doit mesurer la durée de toute la chaîne, y compris les files d’attente, la validation métier et la disponibilité des personnes ayant les droits nécessaires. Un objectif approuvé sans ressources ni tests est une intention, pas une capacité démontrée.

### 4.5 Construire une fiche BIA exploitable

Une fiche de BIA devrait contenir au minimum :

| Champ | Question |
|---|---|
| Activité et propriétaire | Qui est responsable du résultat métier ? |
| Périodes critiques | À quels moments l’interruption coûte-t-elle le plus ? |
| Clients et bénéficiaires | Qui subit l’indisponibilité, directement ou indirectement ? |
| Impacts par horizon | Quelles conséquences apparaissent après 15 min, 1 h, 4 h, 1 jour ou un autre horizon pertinent ? |
| Niveau minimal de service | Que faut-il absolument permettre, et que peut-on suspendre ? |
| MTPD et justification | À partir de quand les conséquences deviennent-elles inacceptables, et pourquoi ? |
| RTO / RPO | Quels objectifs sont approuvés, par qui et dans quel scénario ? |
| Données et transactions | Quelles données doivent être cohérentes, et comment le vérifier ? |
| Dépendances | Quelles personnes, applications, identités, liaisons, sites et fournisseurs sont nécessaires ? |
| Solutions de continuité | Quelles procédures manuelles ou options de substitution sont possibles ? |
| Ressources nécessaires | Quelles compétences, licences, capacités et autorisations sont indispensables ? |
| Validation de retour | Quels tests prouvent que l’activité est acceptable ? |
| Incertitudes | Quelles hypothèses restent à confirmer et quel plan d’action en découle ? |

La BIA doit être validée par les propriétaires métier concernés, challengée par les équipes techniques et sécurité, puis arbitrée lorsque les objectifs dépassent les capacités ou le budget. Si plusieurs services revendiquent la même ressource rare, un arbitrage explicite est nécessaire.

## 5. Cartographier les dépendances réelles

### 5.1 Du service visible à la chaîne de capacités

Un service utilisateur dépend souvent de couches qui ne sont pas visibles dans son écran. Pour reprendre une application, il peut falloir le réseau, la résolution DNS, l’identité, les secrets, les certificats, une base de données, les files de messages, les licences, la supervision, un fournisseur et une procédure métier. Un plan qui ne liste que les serveurs applicatifs est incomplet.

Les dépendances doivent être décrites dans les deux sens. Pour chaque service, lister ce dont il dépend ; pour chaque capacité partagée, identifier les services qu’elle affecte. Le second sens permet d’estimer le rayon d’impact d’une panne d’identité ou du DNS et d’éviter que les équipes restaurent des services qui ne peuvent pas être utilisés.

~~~mermaid
flowchart TD
  U[Utilisateur ou agent] --> APP[Application de commande]
  APP --> ID[Identité et autorisations]
  APP --> DNS[DNS et certificats]
  APP --> DB[Base de données]
  APP --> MQ[File de messages]
  DB --> STORE[Stockage et journaux]
  MQ --> WMS[Système entrepôt]
  APP --> EXT[Fournisseur ou API externe]
  OPS[Accès opérateur et secrets] --> ID
  OPS --> STORE
  MON[Supervision et journalisation] --> APP
  MON --> DB
~~~

Ce modèle doit être adapté à l’architecture réelle. Ajouter les dépendances humaines et organisationnelles : opérateurs habilités, fournisseur d’électricité, opérateur télécom, accès aux locaux, gardiennage, contrats, licences, support éditeur ou capacité de joindre les clients.

### 5.2 Éviter les dépendances communes cachées

Deux environnements ne sont pas réellement indépendants si la même identité, le même plan de gestion, la même région cloud, le même opérateur télécom ou les mêmes identifiants administratifs conditionnent les deux. La redondance physique ne suffit pas si un composant logique commun peut rendre les deux côtés inutilisables.

Évaluer les domaines de défaillance : site, alimentation, réseau, région, compte d’administration, fournisseur, chaîne de livraison logicielle, secrets, équipe humaine. Les contrôles de résilience doivent porter sur les causes communes, pas uniquement sur la présence de deux équipements. Vérifier aussi la capacité des liaisons entre les sites : un lien de secours peut être disponible sans transporter le volume nécessaire à la reprise.

### 5.3 Cartographie et qualité de l’inventaire

Chaque dépendance importante doit avoir un propriétaire, un contact, un état de criticité, une localisation ou zone, une méthode de récupération, un délai réaliste et une preuve de test. Les dépendances dont la source est incertaine doivent être signalées. Une carte très détaillée mais non tenue à jour peut être plus dangereuse qu’une carte plus simple dont les limites sont claires.

Relier la cartographie aux processus de changement, à la gestion des fournisseurs et à l’inventaire des actifs. Tout changement de DNS, de certificat, de région cloud, de schéma de base de données, de mécanisme d’authentification ou de contrat de support peut modifier le PRA. La révision du plan doit être déclenchée par le changement pertinent et non seulement par une date anniversaire.

## 6. Concevoir une stratégie de reprise adaptée au risque

Aucune stratégie unique ne convient à tous les services. La solution doit être choisie selon l’impact, les objectifs, les dépendances, la capacité, les ressources disponibles et les risques de corruption ou de compromission. La conception doit inclure l’exploitation quotidienne du mécanisme, pas seulement son coût initial.

### 6.1 Sauvegarde et restauration

Une sauvegarde est une copie de données ou d’états destinée à permettre une récupération. Elle doit être protégée contre la modification, la suppression, l’accès abusif et la corruption. Les principes couramment utilisés incluent plusieurs copies, des supports ou domaines d’administration distincts, une copie hors ligne ou immuable lorsque c’est pertinent, le chiffrement, la séparation des privilèges et des tests réguliers. La règle souvent nommée « 3-2-1 » est un repère d’architecture, pas une preuve de résilience : elle doit être complétée par l’analyse des menaces et la vérification de restauration.

Vérifier le contenu exact de la sauvegarde. Une sauvegarde des fichiers peut ne pas capturer l’état transactionnel cohérent d’une base. Une image de machine peut contenir une configuration obsolète ou un secret compromis. Les journaux nécessaires à une récupération dans un point donné peuvent être stockés séparément. Les clés de chiffrement et les procédures pour les obtenir sont elles-mêmes des dépendances critiques.

Le test doit couvrir la restauration, la cohérence applicative, les autorisations, le temps de transfert, la capacité de stockage, les contrôles métier et la réouverture progressive. Un message « sauvegarde réussie » prouve seulement que le travail concerné a rapporté un succès selon ses critères. Il ne prouve ni que les données sont restaurables, ni que l’application démarrera, ni que le RTO sera atteint.

### 6.2 Réplication et cohérence

La réplication copie des changements vers un autre environnement, de manière synchrone ou asynchrone selon la technologie. Elle peut réduire la perte de données pour certaines pannes, mais elle propage potentiellement les erreurs logiques, suppressions, mauvaises configurations ou corruptions. Un environnement répliqué n’est pas automatiquement une sauvegarde indépendante.

Préciser le mode de réplication, le retard observé, les scénarios couverts, le mécanisme de promotion, les règles de quorum et le traitement du split-brain. Si deux côtés acceptent des écritures indépendantes, il faut une stratégie explicite de résolution des conflits. Le plan doit prévenir les deux côtés de devenir simultanément maîtres sans mécanisme de cohérence prévu.

### 6.3 Niveaux de préparation d’un site de secours

Les organisations emploient souvent des notions comme *cold site*, *warm site* et *hot site*, ou des variantes telles que *pilot light*. Ces termes n’ont pas une définition universelle unique ; chaque plan doit décrire le niveau réel de préparation.

| Option | Atout principal | Contraintes et risques |
|---|---|---|
| Sauvegarde puis reconstruction | Coût d’exploitation potentiellement moindre | Temps de reconstruction, capacité de restauration et dépendances à démontrer |
| Site froid | Ressources physiques ou cloud disponibles mais peu préconfigurées | Délai important d’activation et dépendance aux approvisionnements |
| Site tiède | Une partie des composants est préparée | Configuration, capacité ou données peuvent encore exiger du travail |
| Site chaud | Environnement déjà opérationnel ou rapidement activable | Coût, complexité, dérive de configuration et tests permanents |
| Pilot light | Socle minimal maintenu, montée en capacité lors de la reprise | Ordonnancement, automatisation, quotas et dépendances à valider |
| Actif-actif | Service exécuté sur plusieurs environnements en régime courant | Complexité de cohérence, routage, arbitrage, capacité et opérations |

L’étiquette choisie ne doit pas remplacer un essai. Un « site chaud » qui n’a pas de certificat valide, d’accès opérateur ou de capacité de stockage suffisante est chaud sur le schéma, pas nécessairement en production.

### 6.4 Comparer les options de façon défendable

Évaluer au minimum le RTO plausible, le RPO démontré, la résilience aux causes communes, le coût total, la compétence nécessaire, la complexité d’exploitation, le risque de corruption, le temps d’approvisionnement, le comportement sous charge et la possibilité d’un retour contrôlé. Les objectifs les plus ambitieux peuvent nécessiter des coûts et des opérations disproportionnés. Le bon choix est celui qui réduit les conséquences critiques à un niveau accepté, avec des preuves suffisamment solides.

La comparaison devrait contenir les hypothèses et les inconnues. Si le temps de récupération du fournisseur n’est pas garanti ou mesuré, ne pas l’annoncer comme certain. Prévoir un test ou une action de réduction d’incertitude.

### 6.5 Capacités et goulots d’étranglement

Le site de secours ne doit pas seulement démarrer ; il doit tenir une charge adaptée. Calculer les volumes, les connexions simultanées, les débits de données, le stockage temporaire, les besoins réseau, la capacité de traitement et les ressources des équipes. Une capacité nominale annoncée par un fournisseur doit être validée dans les conditions réelles ou dans un test représentatif.

Si le secours ne supporte que la moitié du volume normal, documenter comment prioriser les transactions, limiter les requêtes, retarder les tâches non critiques et protéger les fonctions vitales. Un mode dégradé est acceptable seulement si ses limites et risques sont compris, approuvés et surveillés.

## 7. Construire un runbook de reprise exécutable

Un runbook est une procédure opératoire qui permet d’agir de manière ordonnée et répétable. Il est différent d’un document stratégique qui explique pourquoi la reprise est importante. Le runbook doit être assez précis pour qu’une équipe qualifiée, mais qui n’a pas écrit la procédure, puisse le suivre sans dépendre de la mémoire d’un expert unique.

### 7.1 Structure recommandée

1. **Identification :** service, version, propriétaire, date de validation, scénario et périmètre.
2. **Critères de déclenchement :** signaux, seuils et rôle qui décide.
3. **Préconditions :** autorisations, accès, ressources, sauvegardes candidates, versions et dépendances.
4. **État de départ :** source de vérité, dernier état connu, erreurs connues, modifications en cours.
5. **Étapes numérotées :** action, responsable, entrée nécessaire, résultat attendu et preuve.
6. **Points d’arrêt :** situation dans laquelle l’opérateur doit suspendre l’exécution et escalader.
7. **Validation technique :** tests de connectivité, intégrité, sécurité, capacité et observabilité.
8. **Validation métier :** scénario utilisateur, cohérence de transactions et niveau minimal de service.
9. **Communication :** audiences, approbateur, canal, contenu et prochaine mise à jour.
10. **Retour arrière et retour au nominal :** conditions, séquence, données, autorité et critères d’acceptation.
11. **Clôture :** état final, risques résiduels, actions, journaux et preuves conservées.

### 7.2 Exemple de séquence avec points de contrôle

~~~mermaid
flowchart TD
  A[Autorisation enregistrée] --> B[Vérifier l'état et le périmètre]
  B --> C{Source de récupération approuvée ?}
  C -->|Non| X[Arrêt et escalade]
  C -->|Oui| D[Vérifier accès, clés, réseau et capacité]
  D --> E{Préconditions satisfaites ?}
  E -->|Non| X
  E -->|Oui| F[Restaurer dans l'ordre documenté]
  F --> G[Contrôler intégrité et journaux]
  G --> H{Tests techniques réussis ?}
  H -->|Non| X
  H -->|Oui| I[Tests métier et sécurité]
  I --> J{Critères acceptés ?}
  J -->|Non| X
  J -->|Oui| K[Ouverture progressive et surveillance]
~~~

Le point d’arrêt est une fonction de sécurité du runbook. Il ne doit pas être vu comme un échec personnel. Il empêche la procédure de continuer à partir d’une hypothèse devenue fausse.

### 7.3 Mesurer la durée de bout en bout

Une estimation de reprise doit compter toutes les phases nécessaires : détection, qualification, autorisation, mobilisation, disponibilité des accès, récupération de l’infrastructure, restauration de données, démarrage, tests, mise en production contrôlée et validation métier. Ces phases peuvent se chevaucher, mais le chevauchement doit être justifié ; on ne peut pas simplement additionner des durées théoriques ou supposer que toutes les équipes sont immédiatement disponibles.

| Phase | Mesure à recueillir | Exemple d’échec à rechercher |
|---|---|---|
| Détection / qualification | Délai avant compréhension du périmètre | La supervision détecte le serveur mais pas l’impact métier |
| Décision | Délai d’activation et d’autorisation | Seul un titulaire absent peut approuver |
| Mobilisation | Disponibilité des équipes et accès | Les comptes d’urgence sont expirés |
| Infrastructure | Temps pour fournir ressources et réseau | Quota ou capacité insuffisants |
| Données | Restauration et rattrapage des journaux | Point récupéré incompatible avec l’application |
| Service | Démarrage et configuration | Certificat expiré ou secret manquant |
| Validation | Tests techniques et métier | Un test de disponibilité masque une erreur transactionnelle |
| Stabilisation | Surveillance et capacité sous charge | Le service tombe après l’ouverture générale |

Après chaque essai, distinguer le temps observé, l’objectif approuvé et l’incertitude restante. Ne pas modifier rétroactivement l’objectif pour donner à l’exercice une apparence de succès.

### 7.4 Autorisations, secrets et accès de secours

Le plan doit prévoir comment les opérateurs obtiennent les accès indispensables si l’identité principale est indisponible. Les identifiants d’urgence doivent être protégés, individuels lorsque c’est possible, audités, limités dans le temps et soumis à un processus de révocation après usage. Les clés, certificats et secrets ne doivent pas être copiés dans un document non protégé pour faciliter la reprise.

Les opérations sensibles devraient appliquer une vérification à deux personnes lorsque le risque le justifie : l’une exécute et l’autre valide la portée ou la preuve. Ce contrôle est particulièrement important pour changer la source de vérité, promouvoir une base, modifier les routes, restaurer des données de production ou désactiver des contrôles de sécurité.

### 7.5 Retour au nominal et retour arrière

Le retour au service normal est une opération planifiée à part entière. L’environnement de secours peut avoir reçu des écritures nouvelles, tandis que l’ancien environnement contient des états plus anciens ou une configuration différente. Il faut définir la source faisant autorité, la méthode de synchronisation, la fenêtre, les contrôles de cohérence, le propriétaire qui valide et les critères d’arrêt.

Ne pas confondre retour arrière et retour au nominal. Le retour arrière annule ou arrête une étape qui n’a pas donné le résultat attendu. Le retour au nominal met fin à une période d’utilisation du secours et doit préserver les données générées pendant celle-ci. Une bascule de retour précipitée peut entraîner une seconde interruption ou une perte de transactions.

## 8. Protéger l’intégrité des données et la cohérence métier

### 8.1 Restaurer des données, pas seulement des fichiers

Les systèmes applicatifs comportent souvent plusieurs états liés : base de données, pièces jointes, files de messages, index, journaux, exports et systèmes aval. Restaurer chaque composant à un instant différent peut créer des incohérences. Une commande peut être présente dans la base mais absente de la file qui déclenche l’expédition ; un paiement peut être enregistré sans sa référence comptable ; un compte peut exister sans les permissions correspondantes.

Le plan de reprise doit indiquer la relation entre les états : quel composant constitue la source de vérité, comment les transactions incomplètes sont identifiées, quels journaux doivent être rejoués, comment éviter les doublons et qui valide la cohérence métier. Les mécanismes de reprise propres à chaque base ou application doivent être compris, documentés et testés.

### 8.2 Idempotence, doublons et rattrapage

Une action idempotente produit le même état effectif lorsqu’elle est exécutée plusieurs fois avec les mêmes paramètres. Ce principe est utile pour rejouer des tâches, mais il ne faut pas supposer que toutes les opérations le sont. Une demande d’expédition, un paiement ou une émission de facture peut créer un doublon s’il est relancé sans identifiant de transaction ou mécanisme de déduplication.

Avant le rattrapage, définir les fenêtres temporelles, la clé d’unicité, le traitement des transactions en cours, les règles d’ordre et la procédure de rapprochement. Des résultats de restauration doivent être comparés à des totaux et contrôles attendus. Si les écarts ne peuvent pas être expliqués, ils doivent être consignés et arbitrés plutôt que corrigés silencieusement.

### 8.3 RPO mesuré et scénario de corruption

Le RPO doit être défini pour chaque type de sinistre pertinent. Après une panne matérielle, une réplication récente peut suffire. Après une suppression accidentelle, la dernière réplique peut déjà contenir la suppression. Après une compromission, le point le plus récent peut être hostile. Dans ce dernier cas, l’objectif doit intégrer une estimation de la période de présence de l’attaquant et la possibilité d’une récupération à un état sain.

Le mécanisme technique n’est donc pas à lui seul le critère de sélection. Le responsable doit choisir un point de restauration compatible avec le scénario, l’intégrité connue, la qualité des journaux et les conséquences des transactions perdues. Cette décision peut être un arbitrage majeur de crise et doit être documentée.

~~~mermaid
flowchart TD
  A[Scénario de perte connu ?] -->|Non| B[Préserver les sources et analyser]
  A -->|Oui| C[Identifier les points de récupération]
  B --> C
  C --> D[Examiner intégrité et période suspecte]
  D --> E{Point sain et cohérent ?}
  E -->|Non| F[Autre source ou reconstruction contrôlée]
  E -->|Oui| G[Restaurer en zone contrôlée]
  F --> H[Tests de cohérence et rapprochement]
  G --> H
  H --> I{Données et règles métier validées ?}
  I -->|Non| J[Arrêt, investigation et arbitrage]
  I -->|Oui| K[Ouverture contrôlée]
~~~

## 9. Gestion de crise en cas de cyberattaque

### 9.1 Ne pas confondre remise en ligne et retour à la confiance

Dans une crise cyber, l’environnement peut paraître disponible tout en restant compromis. Remettre en ligne un système contenant des mécanismes persistants, des comptes détournés, des secrets exposés ou une configuration altérée peut réintroduire l’incident. La reprise doit être coordonnée avec la réponse de sécurité, qui peut imposer le confinement, l’acquisition de preuves, la révocation des accès et la validation d’une source saine.

Le plan doit établir comment préserver les journaux et éléments de preuve utiles, qui peut isoler un système, comment collecter les informations sans accroître le risque et quelles personnes peuvent autoriser la reconstruction. La préservation des preuves n’interdit pas toute action urgente ; il faut arbitrer selon le risque pour les personnes et les services, le périmètre et les procédures applicables.

NIST SP 800-61 Rev. 3, finalisée en avril 2025, intègre la réponse aux incidents dans une approche plus large de gestion du risque cyber et de préparation organisationnelle. Elle remplace la révision 2 de ce guide. Le modèle local doit être cohérent avec les recommandations actuelles utilisées par l’organisation, et les références plus anciennes doivent être identifiées comme telles.

### 9.2 Priorités dans une suspicion de rançongiciel

La cellule doit éviter plusieurs erreurs fréquentes : restaurer immédiatement le dernier instantané sans vérifier l’intégrité, reconnecter une sauvegarde au même domaine compromis, utiliser des identifiants d’administration suspects, effacer les traces pour accélérer l’opération, ou réactiver tous les services avant d’avoir confirmé le périmètre.

Une séquence adaptée au contexte peut inclure :
1. protéger les personnes et limiter l’extension de l’impact ;
2. activer la gouvernance de crise et les spécialistes appropriés ;
3. préserver les preuves nécessaires selon la procédure de sécurité ;
4. isoler les systèmes ou chemins compromis dans les limites autorisées ;
5. évaluer les comptes, secrets, sauvegardes et environnements de gestion ;
6. sélectionner une source de récupération dont l’intégrité peut être défendue ;
7. reconstruire ou restaurer dans un périmètre contrôlé ;
8. restaurer une chaîne de confiance, dont les identités et accès privilégiés ;
9. valider intégrité, configuration, fonctionnement et transactions métier ;
10. ouvrir progressivement avec surveillance renforcée et critères d’arrêt ;
11. gérer les obligations de notification selon le droit, le contrat et la nature des données ;
12. conduire un REX sans accusation prématurée, puis suivre les actions correctives.

Cette séquence est un cadre de préparation, pas une procédure universelle de réponse à incident. L’ordre exact dépend du scénario, de l’architecture et des autorités compétentes.

### 9.3 Sauvegardes réellement résistantes

Une copie est vulnérable si les mêmes identifiants privilégiés peuvent modifier la production et détruire toutes les sauvegardes. Des contrôles peuvent inclure une séparation de comptes, des droits limités, une copie hors ligne ou immuable, une protection des clés, une surveillance de suppression, une période de rétention adaptée et des tests de restauration isolés. La stratégie doit couvrir les configurations, les certificats, les secrets, les images de reconstruction, les procédures et les données métier, selon les besoins du système.

La présence d’une immutabilité n’élimine pas tous les risques : une sauvegarde peut contenir des données déjà compromises, une clé peut être indisponible, la rétention peut être trop courte ou la procédure de restauration peut être erronée. Le résultat doit être vérifié en pratique.

### 9.4 Conditions de retour dans un environnement de confiance

Définir des critères mesurables : sources de système approuvées, versions vérifiées, vulnérabilités critiques traitées ou explicitement arbitrées, accès privilégiés réinitialisés selon une stratégie sûre, secrets renouvelés si nécessaire, traces conservées, contrôles de sécurité actifs, segmentation appropriée, supervision opérationnelle et validation métier. Les critères dépendent du scénario et doivent être décidés avec les responsables habilités.

Le contrôle doit aussi considérer les fournisseurs et la chaîne de livraison. Si l’incident provient d’un compte ou d’un service tiers, reconstruire l’application sans modifier la relation de confiance peut ne rien résoudre. Les équipes doivent documenter les dépendances examinées, les preuves et les risques qui restent ouverts.

## 10. Continuité métier et mode dégradé

### 10.1 Concevoir un véritable mode dégradé

Un mode dégradé ne se limite pas à dire « utiliser un fichier Excel » ou « prendre les commandes par téléphone ». Il définit les opérations autorisées, le canal à utiliser, la personne qui valide, l’identification des clients, les limites de volume, la conservation des traces, la protection des données, le rapprochement ultérieur et les conditions de sortie.

Un mode manuel peut augmenter les risques de fraude, de perte de données, de duplication ou de divulgation. Il nécessite des contrôles compensatoires : double validation des opérations sensibles, journal numéroté, accès restreints, suivi de la capacité, procédure d’escalade et inventaire de toutes les transactions effectuées hors système. Ces contrôles doivent rester proportionnés : un dispositif trop lourd peut rendre le processus manuel inutilisable alors qu’un contrôle inexistant peut rendre le retour au nominal plus dangereux.

### 10.2 Exemple de fiche de mode dégradé

| Élément | Exemple illustratif |
|---|---|
| Activité | Enregistrer les commandes indispensables |
| Population autorisée | Équipe formée et responsable de permanence |
| Capacité maximale | Plafond quotidien fixé avec le métier |
| Données capturées | Référence unique, client, articles, heure, opérateur, validation |
| Contrôles compensatoires | Vérification d’identité, seconde approbation au-delà d’un seuil |
| Interdictions | Pas de modification manuelle des données de paiement sensibles |
| Rapprochement | Import ordonné, contrôle des doublons, validation des totaux |
| Critères d’arrêt | Perte de traçabilité, dépassement de capacité ou doute d’intégrité |
| Communication | Mention claire des délais et limites au client si nécessaire |
| Sortie | Application restaurée, backlog traité et rapprochement approuvé |

Les valeurs concrètes doivent être définies par l’organisation. La procédure doit expliquer comment reprendre les transactions du mode manuel sans les saisir deux fois ni perdre la chronologie.

### 10.3 Dépendances humaines et fournisseurs

La continuité peut échouer parce qu’une compétence unique est absente, parce qu’un fournisseur ne peut être joint ou parce que le contrat de support n’inclut pas l’option de secours imaginée. Prévoir des suppléants formés, une documentation que l’équipe peut réellement comprendre, des contacts alternatifs, les numéros de contrat, les informations à fournir pour escalader et les conditions d’accès d’urgence.

Pour chaque fournisseur critique, demander ce qui est réellement garanti : périmètre du service, objectifs contractuels, mécanisme d’escalade, dépendances sous-jacentes, localisation des données, modalités d’export, assistance de reprise, limitation de responsabilité et preuve des tests disponibles. Un SLA courant ne garantit pas nécessairement un rétablissement lors d’une crise majeure ; vérifier le contrat et le scénario.

## 11. Communication de crise et gestion des parties prenantes

### 11.1 Principes

Une communication efficace est rapide, factuelle, cohérente, adaptée à l’audience et révisable. Elle sépare ce qui est confirmé de ce qui est en cours d’analyse. Elle indique les actions que le destinataire doit entreprendre et l’heure du prochain point, même lorsque le délai final de résolution est inconnu.

Ne pas promettre une heure de retour sur une intuition. Préférer « prochaine mise à jour à 11 h 30 » à « tout sera réparé à midi » lorsque la seconde affirmation n’est pas étayée. Ne pas attribuer de cause avant que les éléments la soutiennent. La transparence n’oblige pas à révéler publiquement des détails techniques qui exposeraient davantage les systèmes ou des données personnelles.

### 11.2 Adapter le message

- **Équipes opérationnelles :** périmètre, priorités, tâches, interdictions, canal et prochain point.
- **Direction :** impact métier, options, risques, besoin d’arbitrage, coût potentiel et confiance dans l’estimation.
- **Clients :** service affecté, conséquences pratiques, contournement approuvé, protection des données si cela est établi et prochain point d’information.
- **Fournisseurs :** identifiant d’incident, service et région concernés, heures, preuves pertinentes, priorité demandée, actions déjà exécutées et responsable de contact.
- **Juridique et conformité :** faits établis, nature des données ou obligations possiblement concernées, décisions prises et délais applicables à confirmer.
- **Personnel interne :** consignes pour éviter les rumeurs, les réponses contradictoires et la divulgation de données sensibles.

### 11.3 Modèle de message initial

**Objet : Incident majeur affectant [service] — situation à [heure]**

À [heure], nous avons constaté [symptôme confirmé] affectant [périmètre confirmé]. L’équipe vérifie encore [éléments inconnus]. La priorité est [protection des personnes, confinement, maintien d’une activité, restauration ou autre action approuvée]. Pour le moment, les utilisateurs concernés doivent [consigne validée]. Aucune estimation fiable de rétablissement complet n’est disponible à ce stade. Une prochaine mise à jour sera diffusée à [heure] ou plus tôt si un changement significatif intervient. Contact de coordination : [canal autorisé].

Ce modèle doit être adapté et approuvé par les fonctions responsables. Ne jamais inclure de données sensibles, secrets, détails d’investigation ou affirmation non vérifiée par simple souci de remplir un modèle.

### 11.4 Modèle de décision à l’attention de la direction

**Décision demandée :** [question concrète].  
**Situation confirmée :** [faits et heure].  
**Incertitudes :** [points non confirmés et conséquences potentielles].  
**Options :** [option A, B, éventuellement C].  
**Recommandation :** [choix et raisons].  
**Risques de l’option :** [impact, réversibilité et risque résiduel].  
**Condition préalable :** [preuve, autorisation ou ressource manquante].  
**Délai d’arbitrage :** [heure motivée par l’impact].  
**Décideur habilité :** [rôle].  
**Prochain contrôle :** [heure, critère de révision].

Une bonne demande d’arbitrage rend possible une décision. Une demande vague telle que « que devons-nous faire ? » ne montre ni les options ni les conséquences.

### 11.5 Rumeurs, contradiction et porte-parole

Pendant une crise, des messages contradictoires peuvent créer autant de confusion que l’incident lui-même. Désigner une source de vérité interne, un processus d’approbation pour les messages externes et un canal de correction. Les personnes non habilitées doivent savoir à qui transmettre une question, sans être laissées sans consigne. Toute correction importante doit indiquer ce qui a changé et pourquoi.

Les communications doivent être horodatées et archivées selon les règles locales. En cas de données potentiellement compromises ou d’obligations légales, le contenu et le calendrier sont déterminés avec les fonctions compétentes. Le cours ne prescrit pas un délai universel : les échéances varient selon le droit applicable, le secteur et le contrat.

## 12. Exercices et tests du PRA

### 12.1 Des tests de nature différente

| Type de test | Ce qu’il peut démontrer | Ce qu’il ne démontre pas à lui seul |
|---|---|---|
| Revue documentaire | Documents, contacts, versions et responsabilités déclarés | Que la restauration fonctionne réellement |
| Exercice sur table | Décisions, escalade, coordination et communication | Temps technique réel et intégrité des données restaurées |
| Test de composant | Fonctionnement d’une étape isolée | Que la chaîne complète atteindra le RTO |
| Restauration isolée | Récupération d’un jeu de données ou service dans un périmètre contrôlé | Capacité en production, toutes dépendances ou comportement sous pic |
| Test de chaîne intégrée | Interactions de plusieurs composants | Tous les scénarios et causes communes |
| Bascule contrôlée | Fonctionnement opérationnel et temps dans le périmètre testé | Les scénarios non testés ou la reprise après toute compromission |
| Exercice complet | Coordination et capacité de récupération plus représentatives | Une garantie absolue pour les scénarios futurs |

Le niveau de test doit être proportionné au risque et à la criticité. Une restauration complète en production peut être risquée et doit avoir une autorisation, un périmètre, un mécanisme d’arrêt, des surveillants et un plan de retour. Un exercice ne doit pas mettre en danger des personnes ou compromettre les données simplement pour obtenir une preuve plus spectaculaire.

### 12.2 Concevoir un scénario utile

Un bon scénario décrit le contexte sans donner immédiatement la solution. Il fixe les objectifs, le périmètre, les participants, le contrôleur, les événements injectés, les règles de sécurité, les critères d’arrêt et les preuves à collecter. Les injects peuvent inclure un service indisponible, un contact introuvable, une sauvegarde candidate douteuse, un fournisseur non joignable, une divergence des données ou une contrainte de communication.

Les observateurs notent des actions observables : délai d’activation, identification du décideur, accès au runbook, qualité du journal, détection d’une dépendance, validation du RPO, délai de réponse fournisseur et preuve d’acceptation métier. « Les participants ont trouvé l’exercice intéressant » peut être un retour utile, mais ce n’est pas un critère suffisant de réussite.

### 12.3 Sécurité d’un test

Avant un test technique, vérifier l’environnement, les données utilisées, les personnes informées, les limites, la fenêtre, les droits, l’impact potentiel, le mécanisme de retour et les critères d’interruption. L’équipe chargée du test doit pouvoir s’arrêter sans dépendre du seul opérateur qui exécute l’action. Les participants doivent connaître la différence entre une simulation et une action réelle.

Pour les essais impliquant la sécurité, utiliser les règles d’engagement définies par l’organisation. Éviter les actions destructives non autorisées, l’exfiltration de vraies données ou l’isolement de systèmes non inclus dans le périmètre. Une simulation de rançongiciel peut être faite avec des événements préparés et des systèmes de test plutôt qu’en exécutant un code malveillant sur la production.

### 12.4 Mesurer sans masquer les échecs

Définir avant l’essai ce que signifie la réussite. Par exemple : restauration d’un jeu de données précis dans le RPO ciblé, accès par le compte de secours, exécution d’une transaction métier de bout en bout, observation active, procédure de retour comprise, et confirmation par le propriétaire du service.

Le rapport doit distinguer les objectifs réussis, partiellement réussis, échoués et non testés. Une action non réalisée n’est pas un succès. Un RTO manqué ne devient pas atteint parce que l’équipe a retiré le temps de validation du calcul après l’exercice. Si la mesure a changé, il faut expliquer pourquoi, conserver la comparaison et faire approuver tout changement d’objectif selon la gouvernance.

### 12.5 Suivre les écarts jusqu’à l’efficacité

Chaque écart sérieux reçoit un propriétaire, une échéance, une priorité basée sur l’impact, une action concrète et une preuve de clôture. Un défaut de procédure peut nécessiter un test de relecture par une autre équipe ; un problème de capacité peut demander une mesure sous charge ; un problème de sauvegarde exige une restauration réelle et le contrôle de cohérence.

Ne pas clore une action parce que le texte du runbook a été modifié. Il faut démontrer que le problème a été résolu ou que le risque résiduel a été formellement accepté par la bonne autorité. Les écarts récurrents méritent une analyse de cause : manque de budget, architecture trop complexe, responsabilité non claire, processus de changement défaillant ou dépendance fournisseur non maîtrisée.

~~~mermaid
flowchart LR
  A[Objectif de test] --> B[Scénario et critères]
  B --> C[Exécution contrôlée]
  C --> D[Preuves et mesures]
  D --> E[Écarts priorisés]
  E --> F[Action, propriétaire et échéance]
  F --> G[Test d'efficacité]
  G --> H{Défaut supprimé ?}
  H -->|Non| F
  H -->|Oui| I[Mise à jour de la stratégie]
~~~

## 13. Mesures, gouvernance et amélioration continue

Le nombre de documents produits ne mesure pas à lui seul la résilience. Les indicateurs doivent refléter la capacité opérationnelle, les résultats des tests et la maîtrise des dépendances. Chaque indicateur doit être défini : périmètre, méthode de calcul, source de données, propriétaire, fréquence, seuil et limites d’interprétation.

Exemples d’indicateurs :
- proportion de services critiques disposant d’objectifs approuvés par le métier ;
- proportion des dépendances critiques dont le propriétaire et le mécanisme de reprise ont été vérifiés ;
- proportion de procédures critiques testées dans une période définie ;
- délai réel entre détection, activation, décision, reprise technique et validation métier ;
- écart entre RTO cible et durée mesurée, en distinguant les scénarios ;
- RPO observé lors d’essais et état de cohérence des données ;
- pourcentage de sauvegardes restaurées avec succès selon une preuve définie ;
- nombre de risques majeurs acceptés au-delà de leur date de réexamen ;
- délai de clôture et taux de récurrence des défauts issus des exercices ;
- disponibilité des contacts, accès d’urgence et copies de procédures hors du système principal.

Ne pas transformer ces indicateurs en objectifs artificiels. Si une équipe est récompensée uniquement pour le nombre de tests réussis, elle peut choisir des scénarios trop faciles ou masquer les défauts. La mesure doit favoriser la découverte maîtrisée des faiblesses avant un incident réel.

### 13.1 Calendrier de maintenance fondé sur les changements

Revoir la stratégie lorsque changent l’architecture, le modèle d’identité, les applications, les données, les fournisseurs, les objectifs métier, les contrats, les sites, les compétences, les ressources ou les obligations. Conserver la date de la dernière validation et les changements qui l’ont déclenchée. Une revue périodique reste utile, mais elle ne remplace pas une révision immédiate après un changement majeur.

Un PRA valide doit avoir un propriétaire, des approbateurs, une version et une prochaine date de revue. Les équipes doivent savoir quelle version est approuvée. Des copies contradictoires peuvent conduire à restaurer la mauvaise source ou à utiliser un contact périmé.

### 13.2 Modèle de maturité pratique

| Niveau | Caractéristiques observables |
|---|---|
| Initial | Dépendance à des personnes clés, documentation incomplète, tests improvisés |
| Répétable | Rôles et procédures principales identifiés, tests ponctuels, écarts partiellement suivis |
| Défini | BIA approuvée, runbooks structurés, responsabilités et critères communs |
| Mesuré | RTO/RPO testés, preuves conservées, capacité et qualité suivies par scénario |
| Amélioré | Tests guidés par le risque, défauts récurrents analysés, changements automatiquement reliés aux plans |

Cette échelle est pédagogique, pas un modèle de certification. Le but n’est pas d’afficher un niveau élevé, mais d’identifier la prochaine faiblesse que l’organisation peut réellement corriger.

## 14. Atelier pratique — Reprise d’un service de gestion des commandes

### Situation initiale

Une entreprise traite des commandes via une application web. Les commandes sont stockées dans une base relationnelle ; un système de messages les transmet à l’entrepôt et à la facturation. Le service d’identité est commun à plusieurs applications. Le support confirme à 09 h 10 des erreurs de connexion. Une alerte technique signale une forte hausse des échecs de requêtes sur la base. L’équipe ne sait pas encore si l’incident provient d’une défaillance d’infrastructure, d’une erreur de changement ou d’une activité malveillante.

Le propriétaire métier indique que les commandes critiques doivent pouvoir être acceptées en moins de deux heures et que la perte de données acceptable a été approuvée à quinze minutes pour le scénario de panne ordinaire. Il ne sait pas si ce même RPO s’applique à un scénario de corruption malveillante. Le runbook annonce que la restauration de la base prend normalement quarante minutes, mais le dernier test documenté date de onze mois.

### Phase A — Qualifier avant d’agir

1. Enregistrer l’heure et les symptômes observés sans affirmer la cause.
2. Vérifier si d’autres services dépendant de l’identité ou de la base sont touchés.
3. Déterminer si des signaux imposent l’activation de la cellule selon les critères de l’entreprise.
4. Nommer le coordinateur, le responsable technique, le propriétaire métier, la sécurité et le rédacteur du journal.
5. Préserver les changements récents, les alertes et les journaux nécessaires au diagnostic.
6. Interdire les modifications concurrentes non coordonnées qui pourraient changer la source de vérité.

**Livrable attendu :** une fiche de situation avec faits, hypothèses, inconnues, périmètre et prochaines actions. « La base est tombée à cause d’une mise à jour » n’est acceptable que si la preuve le confirme.

### Phase B — Prioriser les capacités

Les équipes doivent clarifier les capacités indispensables : authentification des opérateurs, lecture des commandes existantes, création de nouvelles commandes, transmission à l’entrepôt, facturation et consultation des états. Il est possible que certaines fonctions reviennent avant les autres.

Le propriétaire métier décrit le niveau minimal de service et les conséquences d’un retard supplémentaire. Le responsable technique cartographie les dépendances, notamment identité, DNS, certificats, base, file de messages, stockage et accès administrateur. La sécurité explique les critères de confiance si un scénario cyber reste plausible.

**Livrable attendu :** une matrice de priorité qui distingue le service minimal, les fonctions différables, les limites acceptées et la personne qui valide.

### Phase C — Choisir une stratégie de reprise

Trois options sont discutées :

- restaurer la base à partir de la copie candidate la plus récente ;
- basculer vers un environnement de secours avec réplication ;
- maintenir un mode dégradé limité pendant que l’équipe confirme l’intégrité de la source de récupération.

L’équipe compare le temps complet, le point de données, les dépendances, le risque de propager une corruption, la capacité et la possibilité de revenir en arrière. La copie la plus récente n’est pas automatiquement la meilleure si la cause peut avoir modifié les données. Une bascule n’est pas approuvée sur la seule base d’un ping réussi.

**Livrable attendu :** une recommandation avec les options écartées, leurs raisons, l’autorité qui approuve, le point d’arrêt et les preuves exigées avant l’ouverture.

### Phase D — Exécuter et valider

Avant de démarrer, vérifier l’autorisation, le périmètre, les accès, les certificats, la capacité, la source de données et la disponibilité du plan de retour. Exécuter le runbook en enregistrant les heures et les résultats. Après la restauration, vérifier la santé des composants, l’intégrité des données, les files de messages, les comptes de service, la supervision et l’exécution d’une commande de test de bout en bout.

Le propriétaire métier valide les cas prioritaires. L’équipe n’annonce pas la fin de crise tant que les transactions en mode dégradé ne sont pas rapprochées ou que les risques résiduels ne sont pas attribués et acceptés.

### Phase E — Faire le retour d’expérience

Le rapport mesure les délais réels et les compare aux objectifs approuvés. Il relève notamment le test de restauration trop ancien, les dépendances découvertes, le manque de règle RPO en cas de corruption et toute autorisation ayant retardé la reprise. Chaque écart reçoit un responsable, une date et une preuve d’efficacité attendue.

**Livrable final :** une décision documentée, une chronologie, des preuves de validation, la liste des risques résiduels, les écarts et les actions d’amélioration.

### Critères de réussite de l’atelier

Le travail est satisfaisant lorsque l’apprenant n’invente pas la cause, ne confond pas une infrastructure démarrée avec un service métier valide, justifie les décisions, distingue les points de récupération selon les scénarios, identifie les dépendances, fixe des points d’arrêt et clôture par des actions dont l’efficacité peut être vérifiée.

## 15. Études de cas approfondies

### Cas 1 — Le site de secours dépend de l’identité en panne

Une équipe bascule l’application vers un environnement secondaire. Les machines démarrent et le réseau répond, mais les utilisateurs ne peuvent pas se connecter. L’annuaire et la fédération d’identité sont partagés entre les deux sites. Le PRA traitait cette identité comme une dépendance disponible, sans la tester indépendamment.

**Analyse :** le site secondaire n’est pas autonome vis-à-vis de la cause de panne. L’architecture contient une dépendance commune ; la redondance applicative n’élimine donc pas le domaine de défaillance de l’identité. Le temps de reprise doit intégrer une stratégie d’identité de secours sûre, les droits d’urgence et l’accès des opérateurs.

**Amélioration :** créer une carte des dépendances communes, tester les accès de secours en environnement contrôlé, vérifier les journaux d’utilisation et planifier la révocation après usage. La correction ne consiste pas à créer un compte d’administration partagé et permanent, car cette solution peut augmenter le risque.

### Cas 2 — La dernière sauvegarde contient une corruption

Une application a subi une erreur logique qui a modifié les enregistrements. La réplication continue de fonctionner et les sauvegardes suivantes contiennent la même corruption. La copie la plus récente est disponible, mais l’heure exacte de la première corruption n’est pas immédiatement connue.

**Analyse :** la disponibilité d’une copie ne prouve pas son intégrité. Le point de reprise doit être sélectionné en fonction de la période saine, des journaux, des données métier et des contrôles de cohérence. Il peut être nécessaire de restaurer une copie ancienne dans un environnement isolé, puis de rejouer sélectivement des opérations valides avec une procédure contrôlée.

**Amélioration :** entraîner l’équipe à reconnaître le scénario de corruption, documenter la conservation des copies, définir les tests d’intégrité et établir une méthode de rapprochement. Toute perte de transactions doit être estimée et validée par le propriétaire métier.

### Cas 3 — Une communication annonce un délai non confirmé

Un responsable annonce publiquement que le service sera rétabli dans trente minutes alors que les équipes n’ont pas confirmé les dépendances. Après quarante minutes, l’application est toujours indisponible. Le support reçoit des demandes contradictoires et les équipes doivent corriger le message initial.

**Analyse :** l’estimation a été présentée comme un engagement sans être étayée. Le message a confondu le délai d’une étape technique avec le rétablissement du service. L’organisation doit annoncer le prochain point de communication, expliciter l’incertitude et distinguer le service partiel du service complet.

**Amélioration :** mettre en place un processus d’approbation des messages, un vocabulaire partagé de statut et des indicateurs de confiance. Corriger rapidement l’information erronée, sans chercher à masquer l’erreur.

### Cas 4 — Un fournisseur annonce un retour mais le service reste dégradé

Le fournisseur d’une plateforme confirme que son infrastructure est disponible. L’organisation constate cependant des retards et des erreurs dans les transactions, car la limite de débit de l’API est atteinte et le backlog n’a pas été vidé.

**Analyse :** la disponibilité déclarée du fournisseur ne prouve pas que le service métier fonctionne à son niveau attendu. Il faut contrôler la capacité, les files, les erreurs, les limites contractuelles et les données en attente.

**Amélioration :** intégrer au test de reprise des mesures de débit, de retard et de cohérence, définir le traitement du backlog et conserver des preuves distinctes de l’état fournisseur et du résultat métier.

### Cas 5 — Le retour au nominal crée des transactions dupliquées

Pendant l’indisponibilité, l’équipe a enregistré des commandes manuellement. Lorsque l’application revient, un opérateur saisit à nouveau une partie des commandes sans vérifier les références uniques. Le système expédie certaines commandes deux fois.

**Analyse :** le mode dégradé n’avait pas prévu la déduplication, les identifiants de transaction, le rapprochement ni une autorité pour décider de l’ordre de réimport.

**Amélioration :** exiger une référence unique, une liste centrale des transactions manuelles, des contrôles de doublons, une validation des totaux et un responsable de réconciliation. Tester la sortie du mode dégradé autant que son activation.

## 16. Exercices d’application avec corrigés détaillés

### Exercice 1 — La définition du rétablissement

**Question :** l’équipe déclare la reprise terminée parce que le serveur web répond en HTTPS. Quel est le problème ?

**Correction :** le test prouve uniquement qu’une réponse HTTPS a été reçue sur le périmètre testé. Il ne démontre pas l’accès des utilisateurs, l’authentification, la disponibilité de la base, la cohérence des transactions, le fonctionnement des systèmes aval ou la capacité sous charge. Il faut définir les critères techniques et métier et les exécuter. Le propriétaire du service confirme que les capacités convenues sont atteintes. La déclaration de reprise doit distinguer disponibilité du composant, service minimal, service nominal et risques résiduels.

### Exercice 2 — Cohérence des objectifs

**Question :** une BIA indique un MTPD de deux heures, un RTO de trois heures et un délai de validation métier de quarante-cinq minutes non inclus dans le RTO. Quelle conclusion tirer ?

**Correction :** les objectifs sont incohérents avec le scénario. Le RTO cible dépasse le délai tolérable défini, et le temps de validation omis rend le délai de service réel encore plus long. Il faut revoir la stratégie, les ressources ou les objectifs avec le propriétaire métier et l’autorité de risque. On ne doit pas simplement modifier le MTPD ou le RTO après coup pour justifier l’architecture existante.

### Exercice 3 — Sauvegarde ou réplication

**Question :** les données sont répliquées toutes les quelques secondes. Pourquoi conserver des sauvegardes séparées et tester une restauration ?

**Correction :** la réplication protège certains scénarios de panne mais peut propager une suppression, une corruption logique ou des modifications malveillantes. Des sauvegardes séparées peuvent préserver des points antérieurs, sous réserve de leur protection et de leur intégrité. La restauration vérifie que les données, les journaux, les clés, la capacité et les procédures permettent réellement de reconstituer le service. Le dispositif doit être conçu contre les scénarios identifiés et non autour d’une promesse générale.

### Exercice 4 — Dépendance oubliée

**Question :** l’application tourne sur un site secondaire, mais le DNS interne pointe encore vers le site principal indisponible. Comment prévenir cette erreur ?

**Correction :** cartographier le DNS comme dépendance et non comme simple paramètre de configuration. Le runbook doit préciser qui peut le modifier, les valeurs attendues, les délais de propagation, les contrôles depuis les réseaux utilisateurs et les conséquences d’un changement erroné. L’exercice doit valider la résolution, les certificats et le chemin de trafic depuis le périmètre pertinent. Le retour au nominal doit inclure un nouveau contrôle DNS.

### Exercice 5 — Compromission possible

**Question :** l’équipe veut restaurer la sauvegarde la plus récente après une suspicion de compromission d’un compte privilégié. Quelles conditions doivent être vérifiées avant l’autorisation ?

**Correction :** qualifier le périmètre, préserver les preuves pertinentes, évaluer si les sauvegardes et le plan de gestion ont pu être touchés, identifier les accès compromis, choisir une source de récupération dont l’intégrité peut être défendue, reconstruire ou restaurer dans un environnement contrôlé et définir les critères de confiance. Le scénario exige une coordination avec la sécurité. Il ne suffit pas que la sauvegarde soit récente ou que le test de restauration passe.

### Exercice 6 — Une action corrective est-elle terminée ?

**Question :** après un exercice, le responsable modifie le document et clôture le ticket. La procédure n’a pas été retestée. Peut-on considérer l’écart comme supprimé ?

**Correction :** non, pas si le défaut concernait l’exécution réelle. Le document peut être une partie de la correction, mais l’efficacité doit être testée selon le risque. Une autre équipe peut suivre la procédure, les préconditions peuvent être disponibles et le critère mesuré doit être atteint. En attendant, l’action reste ouverte ou le risque résiduel doit être accepté par l’autorité compétente, avec une date de réexamen.

### Exercice 7 — Mode dégradé et intégrité

**Question :** une équipe saisit des commandes sur papier pendant la panne. Quelles mesures sont nécessaires avant la réouverture du système ?

**Correction :** numéroter et protéger les enregistrements, identifier l’opérateur et le client, conserver l’horodatage, définir une référence unique, contrôler les opérations sensibles, limiter le volume, désigner le responsable de saisie et de rapprochement, détecter les doublons, vérifier les totaux et obtenir la validation métier. Fixer des critères d’arrêt si la traçabilité se perd. Sans cette procédure de sortie, le mode dégradé peut déplacer le risque de l’indisponibilité vers l’intégrité.

### Exercice 8 — Communiquer sans estimation fiable

**Question :** la direction exige une heure de rétablissement, mais l’équipe ne sait pas si la source de données est saine. Quel message proposer ?

**Correction :** expliquer l’impact confirmé, indiquer que la source de récupération est en cours de validation, décrire les actions en cours et préciser l’heure de la prochaine mise à jour. Donner une estimation uniquement si elle repose sur des données et des hypothèses explicites, en présentant son niveau de confiance. Le prochain point doit être tenu même si le diagnostic n’est pas terminé. Il vaut mieux réviser une estimation prudente et justifiée que promettre une heure non défendable.

## 17. Défi final — Piloter une crise de bout en bout

### Scénario

À 08 h 40, le service de commandes d’un opérateur logistique devient très lent. À 08 h 48, plusieurs utilisateurs signalent des erreurs. À 08 h 55, la supervision indique que le service d’identité est partiellement indisponible. À 09 h 05, l’équipe infrastructure constate que le site principal répond encore, mais que certains journaux de base de données présentent des erreurs. À 09 h 12, le responsable métier informe la cellule que la période de pointe commence dans moins d’une heure. Le PRA a été testé pour la dernière fois neuf mois auparavant. Le site de secours dispose d’une copie répliquée, mais personne ne peut confirmer immédiatement si la corruption apparente s’est propagée. Le RTO approuvé du service nominal est de deux heures ; la définition du RPO en cas de corruption n’est pas claire. Une partie des commandes peut être enregistrée par une procédure manuelle limitée.

### Travail demandé

Produire un dossier de crise comprenant :

1. une décision motivée d’activation ou de non-activation de la cellule ;
2. une fiche de situation initiale qui sépare faits, hypothèses et inconnues ;
3. les rôles nécessaires, les suppléances et l’autorité qui approuve les décisions majeures ;
4. une première priorisation métier et les fonctions qui doivent revenir en premier ;
5. une carte textuelle des dépendances critiques et des domaines de défaillance communs ;
6. deux options de reprise et une comparaison de leurs avantages, risques, preuves et délais inconnus ;
7. les points d’arrêt empêchant une restauration depuis une source dont l’intégrité n’est pas confirmée ;
8. une procédure de mode dégradé avec capacité, contrôles et méthode de rapprochement ;
9. un message interne et un message destiné aux clients, rédigés sans cause ni délai inventés ;
10. les critères de validation technique et métier avant déclaration de reprise ;
11. les critères de clôture et un plan de retour au nominal ;
12. un plan de test et au moins cinq actions correctives assorties d’un propriétaire, d’une échéance et d’une preuve d’efficacité.

### Correction de référence

**1. Activation.** L’activation provisoire est défendable parce que plusieurs services et dépendances peuvent être touchés, l’intégrité des données est incertaine et une période de pointe approche. La décision doit citer les critères du plan local. Elle ne conclut pas que la cause est cyber ou que la corruption est confirmée. Si le seuil local n’est pas atteint, l’apprenant doit expliquer comment les alertes seront surveillées et à quel seuil la crise sera activée.

**2. Situation initiale.** Les faits confirmés sont limités : lenteur, erreurs utilisateur, indisponibilité partielle de l’identité et erreurs de journaux signalées. Les hypothèses possibles comprennent une défaillance d’infrastructure, un défaut logiciel, une corruption logique ou un scénario de sécurité. Les inconnues comprennent le périmètre exact, le point de début des erreurs, le retard de réplication, la qualité de la copie et la capacité du site secondaire. Aucune cause ne doit être présentée comme prouvée.

**3. Organisation.** Nommer un coordinateur, un responsable technique, le propriétaire métier, la sécurité, la communication et une personne chargée du journal. Identifier les suppléants et utiliser un canal disponible hors du service principal si nécessaire. Le décideur de crise autorise la stratégie selon les délégations ; le responsable technique n’est pas seul à accepter le risque métier.

**4. Priorités.** Identifier le niveau minimal de commande, l’accès des opérateurs et les transactions indispensables à la période de pointe. Confirmer ce qui peut être différé. Le service d’identité peut être un prérequis ; la base, les messages et l’intégration avec l’entrepôt doivent être vérifiés. Les priorités doivent être validées par le propriétaire métier, pas déduites uniquement de la facilité technique.

**5. Dépendances.** Inclure identité, DNS, certificats, réseau, stockage, journaux de base, réplication, file de messages, accès opérateur, clés et support fournisseur. La copie répliquée n’est pas une source saine tant que la période et la cohérence n’ont pas été évaluées. Si les deux sites dépendent du même système d’identité, le secours partage un domaine de panne.

**6. Options.** Option A : poursuivre le diagnostic et préparer une restauration dans un environnement isolé depuis un point validé. Cette option peut prendre plus de temps mais réduit le risque de réintroduire une corruption. Option B : préparer le site de secours et restaurer le service minimal après validation de la source et des dépendances. Cette option peut accélérer la remise en service mais ne doit pas devenir une bascule aveugle. Les délais des deux options sont incertains tant que les dépendances et points de récupération ne sont pas testés.

**7. Points d’arrêt.** Ne pas promouvoir la copie répliquée avant l’évaluation de l’intégrité ; ne pas utiliser des accès privilégiés suspects ; ne pas annoncer la réussite sur la seule disponibilité réseau ; suspendre si les tests de cohérence échouent ou si le périmètre dépasse l’autorisation. Chaque arrêt déclenche une notification au coordinateur et une décision documentée.

**8. Mode dégradé.** Limiter les opérations aux commandes indispensables, utiliser des références uniques, conserver les heures et les opérateurs, vérifier l’identité, imposer une double validation sur les transactions sensibles et fixer un plafond de volume. Préparer dès l’activation la méthode d’import, de déduplication et de rapprochement. Si la traçabilité devient insuffisante, suspendre la procédure manuelle et solliciter un arbitrage.

**9. Communication.** Dire que le service est perturbé, indiquer les fonctions confirmées comme touchées, donner les consignes approuvées et fixer la prochaine mise à jour. Éviter d’affirmer une panne de base, une cyberattaque ou une heure de retour tant que ces points ne sont pas confirmés. Les messages sont approuvés par les rôles prévus.

**10. Validation.** Vérifier les composants, les accès, la sécurité, les données, les messages en attente, la capacité, la supervision et les tests métier de bout en bout. Le propriétaire métier valide le service minimal, puis le rétablissement nominal. Comparer les temps mesurés à l’objectif de deux heures sans exclure la validation.

**11. Clôture et retour.** Confirmer les fonctions encore dégradées, les données à rapprocher, les risques acceptés, la surveillance renforcée et les tâches de reprise. Définir l’autorité qui autorise le retour au nominal, la source de vérité, la synchronisation, la fenêtre, les critères d’arrêt et les tests après retour. La crise n’est pas close uniquement parce que le tableau de bord est vert.

**12. Amélioration.** Exemples d’actions : clarifier le RPO en cas de corruption avec le propriétaire métier ; tester la restauration isolée ; tester l’identité de secours ; ajouter les files de messages à la validation ; créer un runbook de rapprochement des commandes manuelles ; vérifier les contacts fournisseur ; organiser un exercice sur table puis un test de bout en bout. Pour chaque action, définir un responsable, une date, un résultat observable et un test d’efficacité.

### Barème proposé sur 100

| Dimension | Points |
|---|---:|
| Activation, gouvernance et journal de crise | 15 |
| BIA, priorité métier et cohérence RTO/RPO | 15 |
| Cartographie des dépendances et domaine de panne | 15 |
| Choix de reprise et traitement de l’intégrité | 20 |
| Mode dégradé et rapprochement | 10 |
| Communication factuelle et adaptée | 10 |
| Critères de validation, clôture et retour | 10 |
| Actions correctives mesurables | 5 |

Une réponse excellente rend visibles les incertitudes et les risques résiduels. Elle ne se contente pas de choisir vite : elle montre pourquoi la décision est défendable, ce qui pourrait la rendre invalide et quelles preuves permettront de poursuivre.

## 18. Modèles réutilisables

### 18.1 Fiche de situation commune

| Champ | À renseigner |
|---|---|
| Identifiant de crise | Référence unique |
| Date, heure et fuseau | Heure de l’événement et horodatage des mises à jour |
| Coordinateur / suppléant | Rôles et moyen de contact de secours |
| Statut | Investigation, confinement, reprise, service dégradé, stabilisation ou clôture |
| Faits confirmés | Éléments associés à une source ou une preuve |
| Hypothèses | Éléments possibles, niveau de confiance et action de confirmation |
| Impact | Activités, services, utilisateurs et régions concernés |
| Dépendances | Composants indisponibles ou non confirmés |
| Décisions attendues | Question, autorité, échéance et conséquences d’un retard |
| Actions en cours | Responsable, statut, prochaine étape et blocage |
| Prochain point | Heure et audience |
| Risques résiduels | Description, autorité d’acceptation et date de réexamen |

### 18.2 Fiche de reprise technique

| Champ | Description |
|---|---|
| Scénario | Panne, perte de site, corruption, cyberattaque ou autre scénario autorisé |
| Périmètre | Services, données, régions et composants inclus |
| Autorisation | Identité ou rôle de l’autorité, heure et référence de décision |
| Source de récupération | Origine, date, intégrité et critères d’acceptation |
| Préconditions | Accès, clés, certificats, réseau, stockage, capacité et dépendances |
| Étapes | Action, exécuteur, résultat attendu et preuve |
| Point d’arrêt | Condition qui impose la suspension |
| Tests techniques | Santé, données, sécurité, capacité et observabilité |
| Tests métier | Scénarios et résultats acceptables |
| Plan de retour | Condition de déclenchement, procédure et autorité |
| Résultat | Heures mesurées, écart au RTO/RPO et limites |
| Approbation finale | Responsable technique, sécurité et propriétaire métier selon le risque |

### 18.3 Fiche d’action corrective

| Champ | Description |
|---|---|
| Écart | Ce qui a été observé et la preuve |
| Impact | Conséquence possible et scénario concerné |
| Cause contributive | Facteurs validés, en distinguant les hypothèses |
| Action | Modification concrète à réaliser |
| Responsable | Une personne ou un rôle clairement désigné |
| Échéance | Date ou jalon approuvé |
| Dépendances | Budget, fournisseur, changement, compétence ou décision |
| Preuve de mise en œuvre | Ce qui démontrera que l’action a été réalisée |
| Test d’efficacité | Essai ou mesure qui prouvera que le défaut est corrigé |
| Risque résiduel | Ce qui reste et qui l’accepte jusqu’à quand |

## 19. Références, normes et méthode de veille

Les ressources ci-dessous servent à approfondir la conception et à vérifier les pratiques. Les normes intégrales peuvent être payantes ; un résumé public ne suffit pas à démontrer la conformité. Il faut consulter la version et les obligations réellement applicables au moment de l’usage.

- [ISO 22301 — Sécurité et résilience, systèmes de management de la continuité d’activité](https://www.iso.org/fr/standard/75106.html). Référence de management pour établir, mettre en œuvre, maintenir et améliorer un système de continuité. Vérifier l’état de révision et les amendements publiés au moment de préparer une politique ou un audit.
- [NIST SP 800-61 Rev. 3 — Incident Response Recommendations and Considerations for Cybersecurity Risk Management](https://csrc.nist.gov/pubs/sp/800/61/r3/final). Version finale publiée en avril 2025, intégrant la réponse aux incidents à la gestion du risque cyber et au CSF 2.0.
- [NIST SP 800-34 Rev. 1 — Contingency Planning Guide for Federal Information Systems](https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final). Guide de planification de contingence qui traite notamment de la BIA, des stratégies de récupération, des procédures, des tests et de la maintenance. Publication ancienne à contextualiser selon les environnements modernes.
- [NIST SP 800-184 — Guide for Cybersecurity Event Recovery](https://csrc.nist.gov/pubs/sp/800/184/final). Guide dédié à la planification, l’exécution et l’amélioration de la récupération après un événement cyber.
- [CISA — Ransomware Guide](https://www.cisa.gov/stopransomware/ransomware-guide). Recommandations de préparation et de récupération, notamment la protection et le test des sauvegardes.
- [NIST Cybersecurity Framework 2.0](https://www.nist.gov/cyberframework). Cadre de gestion du risque cyber utile pour relier gouvernance, identification des actifs, protection, détection, réponse et récupération.

Pour chaque référence, noter le titre, l’édition ou la date, le périmètre utile, les exigences qui concernent l’organisation et les contrôles locaux associés. Ne pas conclure à la conformité parce qu’un plan cite une norme. Il faut relier les exigences applicables à des responsabilités, des procédures, des preuves et des résultats de test.

## Synthèse finale

Un dispositif expert de gestion de crise et de reprise est une capacité opérationnelle vérifiable. Il relie les activités métier aux dépendances techniques, fixe des objectifs cohérents, donne aux décideurs l’autorité et les informations nécessaires, et fournit aux équipes des procédures dotées de contrôles et de points d’arrêt. Les sauvegardes, la réplication et la redondance sont des moyens ; aucun ne démontre à lui seul la restauration d’un service fiable.

La qualité se vérifie pendant les exercices : l’équipe sait-elle activer la crise, établir les faits, protéger les données, choisir une source saine, mobiliser les accès et fournisseurs, restaurer dans un délai réaliste, valider les transactions, communiquer avec précision et revenir au nominal sans incohérence ? Les écarts ne sont pas dissimulés : ils deviennent des actions attribuées et leur efficacité est retestée.

La posture experte consiste enfin à rendre visibles les limites. Un objectif non testé, une dépendance inconnue, un délai fournisseur non garanti, une copie d’intégrité incertaine ou un risque non accepté doivent être déclarés comme tels. La résilience ne vient ni du volume documentaire ni de la confiance, mais d’une gouvernance claire, d’une préparation réaliste, de preuves répétables et d’une amélioration soutenue.
