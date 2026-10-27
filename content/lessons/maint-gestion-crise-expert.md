# Gestion de crise et Plan de Reprise

> **Mise en contexte — Gestion de crise et PRA** : La gestion de crise consiste à coordonner des décisions lorsque les procédures ordinaires ne suffisent plus, tandis que le plan de reprise d'activité (PRA) décrit comment restaurer les services prioritaires après une interruption. Il faut distinguer réponse à incident, continuité des activités, reprise informatique et gestion de crise : ces dispositifs se recoupent, mais leurs objectifs et responsables ne sont pas identiques. Une panne électrique, une compromission d'identités, une indisponibilité fournisseur, un dégât matériel ou une erreur de changement peuvent affecter plusieurs services à la fois. La crise est autant organisationnelle que technique : les équipes doivent établir ce qui est connu, choisir des priorités, protéger les personnes et les données, communiquer sans spéculer et rétablir les capacités selon un ordre défendable.

## Objectifs pédagogiques

À l'issue du cours, l'apprenant sera capable de :

- conduire l'activation et la coordination d'une cellule de crise
- utiliser une analyse d'impact métier pour prioriser les services
- définir RTO, RPO, dépendances et stratégies de reprise
- construire et maintenir un PRA testable
- organiser des exercices, mesurer leurs résultats et corriger les écarts
- communiquer aux parties prenantes sans créer de fausses certitudes

## Prérequis et cadre de responsabilité

Le parcours s'adresse à un professionnel capable de lire les procédures, les tickets et les indicateurs du service concerné. Les décisions qui affectent la production, les personnes, les données, les finances ou les contrats doivent respecter les seuils d'autorisation de l'organisation. Les exemples du cours sont pédagogiques : adapter les cibles, les rôles et les obligations à l'environnement, au pays, au secteur et aux engagements effectivement applicables. Ne jamais remplacer une validation juridique, de sécurité, financière ou opérationnelle exigée par une hypothèse ou un exemple générique.

Avant une action importante, préciser le besoin, la portée, la personne qui décide, la preuve attendue, les risques, les conditions d'arrêt et la procédure de remontée. Si une donnée importante manque ou qu'une dépendance n'est pas confirmée, rendre cette incertitude visible et faire valider la suite par la personne habilitée.

## Vocabulaire de référence

| Terme | Définition |
|---|---|
| Cellule de crise | Groupe habilité à coordonner les décisions interfonctionnelles lors d'une perturbation majeure. |
| PCA | Plan de continuité d'activité destiné à maintenir ou adapter les activités prioritaires. |
| PRA | Plan de reprise d'activité décrivant les moyens de restaurer les capacités après une interruption. |
| BIA | Analyse d'impact métier qui relie les interruptions aux conséquences au fil du temps. |
| RTO | Objectif de délai dans lequel le service doit être rétabli à un niveau convenu. |
| RPO | Point dans le temps jusqu'auquel les données doivent pouvoir être restaurées ; il traduit une perte de données acceptable. |
| MTPD | Période maximale de perturbation tolérable avant que l'impact ne devienne inacceptable, selon la méthode locale. |
| Mode dégradé | Mode temporaire qui fournit un niveau de service réduit avec des contrôles et limites explicités. |

## Schémas de référence

### Schéma 1 — Objectifs et activation

~~~mermaid
flowchart TD
  A[Signal de perturbation] --> B{Seuil de crise atteint ?}
  B -->|Non| C[Gestion incident normale]
  B -->|Oui ou incertain| D[Activation provisoire]
  D --> E[Évaluer impact et périmètre]
  E --> F[Confirmer ou désactiver la cellule]
~~~

Activer la coordination : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 2 — Rôles et décisions

~~~mermaid
flowchart LR
  A[Coordinateur] --> B[Décision et priorités]
  C[Responsable technique] --> D[Actions de reprise]
  E[Communication] --> F[Messages approuvés]
  G[Propriétaire métier] --> H[Validation service]
  B --> I[Journal de crise]
  D --> I
  F --> I
  H --> I
~~~

Responsabilités de crise : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 3 — Cartographie des dépendances

~~~mermaid
flowchart TD
  A[Identité et réseau] --> B[Plateforme de données]
  B --> C[Application]
  C --> D[Validation métier]
  E[DNS, certificats, secrets] --> C
  F[Fournisseur] --> B
~~~

Dépendances PRA : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 4 — Cycle de traitement

~~~mermaid
flowchart TD
  A[Service indisponible] --> B{Intégrité des données connue ?}
  B -->|Non| C[Préserver et vérifier]
  B -->|Oui| D{Sauvegarde récupérable ?}
  D -->|Oui| E[Restaurer et tester]
  D -->|Non| F[Option de secours ou mode dégradé]
~~~

Choix de reprise : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 5 — Escalade et information

~~~mermaid
flowchart LR
  A[Faits confirmés] --> B[Impact et mesures]
  B --> C[Message interne]
  B --> D[Message utilisateur]
  B --> E[Message décideur]
  C --> F[Prochain point fixé]
  D --> F
  E --> F
~~~

Communication de crise : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 6 — Validation du résultat

~~~mermaid
flowchart TD
  A[Infrastructure disponible] --> B[Identité et accès testés]
  B --> C[Données cohérentes]
  C --> D[Transaction métier]
  D --> E{Objectifs atteints ?}
  E -->|Oui| F[Valider service]
  E -->|Non| G[Mitigation et escalade]
~~~

Test de rétablissement : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 7 — Mesure et gouvernance

~~~mermaid
flowchart LR
  A[Activité métier] --> B[Impact dans le temps]
  B --> C[RTO approuvé]
  B --> D[RPO approuvé]
  C --> E[Option de reprise]
  D --> E
~~~

BIA et objectifs : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 8 — Traitement des écarts

~~~mermaid
flowchart TD
  A[Écart constaté] --> B[Preuve et impact]
  B --> C[Action responsable]
  C --> D[Échéance et critère]
  D --> E[Test d'efficacité]
  E --> F{Écart supprimé ?}
  F -->|Non| C
~~~

Écart d'exercice : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 9 — Amélioration continue

~~~mermaid
flowchart LR
  A[BIA] --> B[Stratégie]
  B --> C[PRA documenté]
  C --> D[Exercice]
  D --> E[Actions correctives]
  E --> A
~~~

Cycle de résilience : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 10 — Sortie et retour d'expérience

~~~mermaid
flowchart TD
  A[Service rétabli] --> B[Propriétaire confirme]
  B --> C[Risques résiduels consignés]
  C --> D[Clôture de crise]
  D --> E[REX et actions suivies]
~~~

Fin de crise : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

## 1. Séparer incident, crise, continuité et reprise

Un incident opérationnel est une perturbation qui peut souvent être traitée dans la chaîne normale de support. Une crise apparaît lorsque l'impact, l'incertitude, les interdépendances ou la durée exigent une gouvernance renforcée. Il n'existe pas de seuil universel de crise : les critères d'activation doivent être approuvés en amont, associés à des scénarios et compris par les équipes de garde. Attendre une certitude parfaite peut retarder une coordination nécessaire ; l'activation peut donc être provisoire et réévaluée.

La gestion de crise coordonne la décision, les priorités, la communication, les ressources et les arbitrages. La continuité organise le maintien des activités essentielles pendant la perturbation. Le PRA se concentre sur le rétablissement des capacités techniques selon des dépendances et des objectifs. Le plan de réponse à incident de sécurité peut avoir ses propres obligations de conservation des preuves, de notification et de limitation de propagation. Un scénario cyber peut donc nécessiter deux actions en parallèle : protéger l'environnement compromis et restaurer un service propre depuis des sources vérifiées.

L'organisation doit définir qui peut activer la crise, qui assume le rôle de coordinateur, qui prend les décisions techniques, qui valide la communication externe et qui peut accepter un risque résiduel. Utiliser une matrice d'escalade et une chaîne de suppléance. Si une personne essentielle est indisponible, le plan doit prévoir un remplaçant habilité ; la crise ne doit pas dépendre d'un seul contact personnel.

La préparation consiste à rendre le dispositif activable, pas seulement à rédiger un document. Les coordonnées, canaux alternatifs, accès d'urgence, copies des procédures, fournisseurs de secours, lieux de repli et moyens de communication doivent être contrôlés périodiquement. Les documents de crise doivent rester accessibles si le système d'identité ou la plateforme documentaire principale est indisponible, tout en protégeant les données sensibles.

## 2. Réaliser une analyse d'impact métier (BIA)

L'analyse d'impact métier identifie les activités essentielles, les conséquences d'une interruption dans le temps, les dépendances et le niveau de service minimal acceptable. Elle doit être conduite avec les propriétaires métier et les équipes techniques, car un serveur critique sur le plan informatique n'est pas forcément le service dont l'arrêt produit le plus grand impact métier. Examiner les délais immédiats, les périodes de pointe, les obligations contractuelles, les risques de sécurité, les effets financiers et la confiance des utilisateurs.

La BIA doit distinguer le service métier, ses applications, ses données, les identités, le réseau, l'énergie, les locaux, les fournisseurs, le personnel compétent et les moyens manuels. Une dépendance commune peut rendre indisponibles plusieurs services pourtant hébergés sur des systèmes distincts. Cartographier les dépendances et vérifier les hypothèses avec des responsables qui connaissent l'exécution réelle, pas uniquement les schémas d'architecture.

RTO et RPO sont deux objectifs différents. Le RTO limite le délai de reprise ; le RPO limite le point jusqu'auquel les données doivent être récupérables. Un service peut être techniquement relancé en deux heures tout en étant inutilisable si ses données sont trop anciennes ou si une dépendance n'est pas prête. À l'inverse, un point de données récent ne rend pas acceptable une interruption longue. Définir aussi les fonctionnalités minimales et la validation métier nécessaire pour déclarer le rétablissement.

Les objectifs ont un coût. Des objectifs très courts peuvent nécessiter réplication, sites alternatifs, infrastructure doublée, contrats prioritaires et exercices plus fréquents. Une BIA ne doit pas recopier automatiquement l'objectif souhaité par chaque équipe : comparer les conséquences et le coût des options, expliciter les arbitrages et obtenir une validation de la personne habilitée. La cohérence entre MTPD, RTO, RPO et le temps d'activation est un contrôle essentiel.

## 3. Concevoir les stratégies de reprise

Les options peuvent inclure restauration à partir de sauvegardes, réplication, redondance géographique, infrastructure de secours, reconstruction automatisée, repli vers une procédure manuelle ou remplacement temporaire d'une capacité. Chaque option a des prérequis et des compromis. Une réplication rapide peut répliquer aussi une corruption logique ; une sauvegarde hors ligne peut être plus lente mais protéger contre certains scénarios ; une infrastructure de secours peut échouer si les identités, DNS, certificats ou licences ne sont pas disponibles.

Construire un ordre de reprise à partir des dépendances et des objectifs. Par exemple, rétablir une application avant son annuaire ou son réseau peut produire un succès apparent sans capacité de service réelle. Le plan doit identifier les préconditions, les propriétaires, les paramètres autorisés, les validations par étape et les critères de passage à la suivante. Les hypothèses doivent être testées dans un environnement qui représente les limites réelles, notamment la capacité des liaisons et la disponibilité des fournisseurs.

Un plan de reprise doit indiquer les critères de bascule, l'autorité qui déclenche le basculement, la source de vérité des données, les responsabilités pendant l'exécution, les conditions de retour à l'environnement normal et le moyen de vérifier l'intégrité après retour. Le retour peut être plus dangereux que la bascule si des données ont divergé. La décision doit donc inclure une fenêtre, une procédure de synchronisation et un point d'arrêt si l'état des données ne peut pas être confirmé.

Le mode dégradé est une stratégie, pas une improvisation. Décrire les transactions qui restent possibles, les volumes maximaux, les contrôles compensatoires, la saisie différée et la procédure de rapprochement lorsque les outils reviennent. Si une opération manuelle ne peut pas garantir l'identité ou l'intégrité des données, limiter sa portée et exiger une validation supplémentaire. Fixer les critères qui imposent l'arrêt ou le retour au mode sécurisé.

## 4. Diriger la cellule de crise et communiquer

Le coordinateur tient une situation commune à jour : impact confirmé, périmètre connu, services touchés, décisions, responsable de chaque action, échéance, risques et prochaine mise à jour. Séparer les faits, les hypothèses et les décisions. Désigner un rédacteur de journal de crise pour conserver les heures, les arbitrages et les raisons. Quand plusieurs équipes travaillent, faire une synchronisation courte et régulière au lieu de multiplier les fils de discussion non rattachés à une source commune.

La communication doit répondre aux questions de l'audience : ce qui est affecté, ce que les personnes doivent faire, les solutions provisoires, ce qui est inconnu et quand une mise à jour sera communiquée. Ne pas annoncer une heure de résolution sans estimation défendable ; préférer un prochain point d'information. Les messages externes suivent les rôles habilités et les obligations contractuelles ou réglementaires applicables. Une communication transparente n'exige pas de révéler des détails de sécurité qui augmenteraient le risque.

Les priorités peuvent être contradictoires : restaurer vite, préserver les preuves, protéger des données, respecter la sécurité des personnes et éviter une réinfection. La cellule doit arbitrer selon les responsabilités prévues, pas par influence ou ancienneté. Les décisions importantes doivent mentionner l'option retenue, les alternatives écartées, le risque accepté et la personne qui approuve. Si la situation change, réexaminer les décisions antérieures plutôt que continuer par inertie.

La fatigue, le stress et l'incertitude détériorent la qualité des décisions. Prévoir la relève, des rôles explicites, des rotations et des pauses lorsque la situation le permet. Limiter le nombre de personnes dans le canal de décision, tout en diffusant un compte rendu opérationnel clair aux groupes qui exécutent. Les messages de crise doivent éviter les accusations prématurées : la priorité est la sécurité, la maîtrise de l'impact et l'apprentissage ultérieur.

## 5. Tester, maintenir et auditer le PRA

Un plan doit être testé au niveau correspondant au risque. La revue documentaire confirme que le contenu existe ; un exercice sur table teste les décisions et les dépendances ; un test technique vérifie des étapes précises ; une restauration complète ou un basculement démontre davantage mais comporte plus de risques et de coûts. Le choix dépend du service, de la criticité, des impacts de test et du niveau de confiance recherché.

Chaque exercice doit avoir des objectifs mesurables, un scénario, un périmètre, des participants, des hypothèses, les règles d'arrêt et un observateur. Mesurer les temps réels, l'accessibilité des procédures, la disponibilité des personnes, les dépendances manquantes, les écarts entre résultats attendus et observés, et la qualité de la communication. Une réussite technique qui nécessite une intervention improvisée d'un expert absent du dispositif ne démontre pas une reprise reproductible.

Le compte rendu d'exercice doit transformer chaque anomalie en action attribuée, avec une échéance, une preuve attendue et un test d'efficacité. Ne pas déclarer l'action terminée parce que le document est modifié ; vérifier qu'un autre opérateur peut suivre le parcours ou que le service atteint les objectifs. Les défauts critiques justifient un arbitrage formel sur le risque résiduel jusqu'à leur correction.

La maintenance du plan est déclenchée par les changements d'architecture, de fournisseurs, de données, d'identités, de locaux, de contrats, d'objectifs métier ou de responsables. Une revue périodique seule ne suffit pas si un changement majeur survient le lendemain. Relier le PRA au processus de changement et à l'inventaire, puis vérifier que les copies et les contacts restent accessibles hors du système principal.

## Méthode opérationnelle — du diagnostic à la décision

Une démarche experte suit un enchaînement traçable. Commencer par formuler la question à résoudre et le résultat attendu, puis identifier les sources de données, les personnes concernées, les contraintes et les risques. Construire un état initial avant d'agir : période, périmètre, dépendances, règles en vigueur et qualité des données. Énoncer les hypothèses de façon à pouvoir les confirmer ou les rejeter. Préférer des contrôles qui distinguent réellement les causes possibles plutôt qu'une accumulation de vérifications sans lien avec la décision.

Avant toute décision à impact, examiner les options et les conséquences, y compris l'option de ne pas agir immédiatement. Pour chaque option, documenter bénéfices, risques, coût, dépendances, réversibilité et conditions de réussite. Choisir une action proportionnée et approuvée, assigner un responsable et une échéance, puis mesurer le résultat avec le même critère que celui défini au départ. Si une hypothèse importante est invalidée, interrompre le scénario prévu et requalifier la situation plutôt que continuer mécaniquement.

La preuve doit permettre à un collègue indépendant de comprendre ce qui a été décidé, pourquoi et à partir de quelles informations. Distinguer fait observé, déclaration, estimation, hypothèse et décision. Conserver les exceptions et résultats contradictoires qui modifient l'interprétation. Lorsque le niveau de confiance reste insuffisant, réduire la portée de la conclusion, expliquer la limitation et préciser le contrôle suivant qui permettrait de progresser.

## Mesure, gouvernance et amélioration

Chaque indicateur de pilotage doit avoir un objectif, une formule ou une méthode, une source, une période, un propriétaire, des limites et une décision associée. Un chiffre sans dénominateur, définition ou état de fraîcheur est difficile à interpréter. Contrôler la couverture de la population, les valeurs manquantes, les doublons, les changements de définition et les exclusions. Les résultats d'une action doivent être comparés à une référence crédible, avec les changements simultanés et les effets secondaires identifiés.

Ne pas optimiser un indicateur isolé au détriment du service. Une baisse de délai peut cacher des clôtures prématurées ; un gain de prix peut créer un coût de sortie très élevé ; une reprise technique peut rester inutilisable pour le métier ; une réduction d'effectifs peut concentrer une compétence critique. Associer les mesures de résultat à des indicateurs de qualité, de risque, de charge et de durabilité afin de vérifier que l'amélioration est réelle.

La gouvernance exige des responsabilités explicites. Pour chaque décision significative, noter qui propose, qui examine, qui approuve, qui exécute et qui vérifie. Une revue doit se terminer par des décisions suivies, pas uniquement par un compte rendu. Les actions comportent un propriétaire, une échéance, une preuve de réalisation et un critère d'efficacité. En cas de retard, faire apparaître le risque et demander une décision explicite sur les mesures temporaires.

## Atelier pratique — Reprise d'un service de gestion

### Situation de départ

Une entreprise fictive perd l'accès à son service de gestion après un incident affectant l'identité centrale et une partie du stockage. Les équipes disposent d'une sauvegarde récente mais ne savent pas si les identifiants de récupération et le DNS de secours sont disponibles. L'exercice ne doit toucher aucun environnement de production. Les participants doivent établir une situation initiale, décider de l'activation de crise et cartographier les dépendances avant de proposer la reprise.

### Phase A — Qualification

Identifier les services, utilisateurs, sites et données touchés. Distinguer les faits observés des hypothèses. Estimer les conséquences au fil du temps et confirmer auprès du propriétaire métier les fonctions minimales. Noter les données manquantes et l'heure de prochaine mise à jour.

### Phase B — Objectifs et priorités

Utiliser la BIA existante ou en produire une version provisoire pour l'exercice. Déterminer le RTO/RPO validé, les dépendances critiques, les mesures préventives et la source de données de reprise. Ne pas inventer un objectif pour remplir le plan ; escalader toute cible non approuvée.

### Phase C — Choix de stratégie

Comparer restauration, bascule et mode dégradé. Pour chaque option, inscrire prérequis, autorisation, délai estimé, risques de corruption et critère d'arrêt. Choisir une séquence de reprise et les tests qui confirmeront la disponibilité métier, pas uniquement le démarrage technique.

### Phase D — Commandement et communication

Distribuer les rôles, ouvrir un journal de crise et produire deux messages : un destiné aux utilisateurs et un résumé aux décideurs. Indiquer impact confirmé, action en cours, incertitudes, consignes et prochaine mise à jour. Escalader tout risque qui dépasse le mandat.

### Phase E — Exercice et amélioration

Simuler les étapes dans une maquette, relever les écarts et attribuer les actions. Le compte rendu identifie les objectifs atteints, les délais réels, les preuves et les limites. Un test de restauration ultérieur doit valider la procédure corrigée.

### Critères de réussite

Le livrable de l'atelier doit être reproductible, lié à des critères explicites et suffisamment clair pour être repris par une autre équipe. Les décisions non confirmées doivent rester présentées comme hypothèses. Toute action comporte ses conditions d'application, les risques, les validations nécessaires et une preuve du résultat. Le succès ne se déduit pas d'une présentation convaincante ou d'une case cochée : il se démontre avec des résultats et une revue indépendante adaptée au risque.

## Études de cas

### Cas 1 — Dépendance oubliée

La base de données est restaurée mais l'application ne fonctionne pas car le service d'identité est absent. Le plan doit suivre les dépendances réelles et définir les tests de service après chaque jalon.

### Cas 2 — Sauvegarde inutilisable

Le fichier de sauvegarde existe mais la clé de déchiffrement est conservée uniquement dans le système indisponible. La stratégie doit vérifier l'accès aux secrets de reprise, sous contrôle de sécurité, et tester leur disponibilité hors environnement principal.

### Cas 3 — Communication contradictoire

Deux équipes donnent des estimations différentes aux utilisateurs. Une source commune de situation, un porte-parole désigné et une cadence d'information réduisent les messages divergents.

## Exercices d'application avec corrigés

### Exercice 1 — Définir le critère

**Question.** Pourquoi RTO et RPO doivent-ils être définis séparément ?

**Corrigé expliqué.** Le RTO concerne le délai de reprise ; le RPO concerne le point de données récupérable et la perte de données acceptable. Un service peut être restauré vite avec des données trop anciennes, ou posséder des données récentes mais rester indisponible trop longtemps.

### Exercice 2 — Interpréter les preuves

**Question.** Une sauvegarde indique succès. Le PRA est-il validé ?

**Corrigé expliqué.** Non. Il faut vérifier la restauration, l'intégrité des données, les dépendances, la durée et une validation de service selon des critères approuvés. Un succès de sauvegarde ne démontre pas le rétablissement complet.

### Exercice 3 — Choisir une action

**Question.** Qui décide l'activation de crise ?

**Corrigé expliqué.** La personne ou le rôle habilité par le plan d'escalade. Le seuil doit être défini à l'avance et les suppléants connus ; la technique apporte les faits, mais une activation ne doit pas attendre une certitude absolue si les critères sont atteints.

### Exercice 4 — Traiter une dépendance

**Question.** Que faire si la restauration dépasse le RTO ?

**Corrigé expliqué.** Documenter l'écart réel, informer la cellule de crise, choisir des mesures de mitigation et réévaluer les priorités. Ne pas modifier rétroactivement le RTO pour que le test semble réussi ; l'objectif et le risque résiduel doivent être arbitrés.

### Exercice 5 — Évaluer un écart

**Question.** Quel est le rôle d'un test sur table ?

**Corrigé expliqué.** Évaluer les décisions, les rôles, la communication, les dépendances et la compréhension du plan. Il ne remplace pas une restauration technique lorsqu'on doit démontrer l'intégrité des données et les temps réels.

### Exercice 6 — Vérifier l'efficacité

**Question.** Comment clôturer une action issue d'exercice ?

**Corrigé expliqué.** Fournir une preuve de réalisation puis un test d'efficacité correspondant au défaut : exercice rejoué, procédure suivie par un second opérateur, temps mesuré ou validation de la dépendance corrigée.

## Défi final — mise en situation experte

Le comité de direction demande de démontrer que quatre services critiques peuvent être repris dans leurs objectifs après une panne combinant perte d'identité, indisponibilité d'un fournisseur et risque de corruption des données. Produire le mandat d'exercice, une BIA, les objectifs RTO/RPO, un arbre de décision, une stratégie de reprise par ordre de dépendance, le plan de communication, les preuves attendues et le suivi des écarts. Le correctif attendu ne promet pas une reprise garantie : il définit les conditions mesurables, les hypothèses testées, les limites et les décisions d'acceptation de risque.

**Livrable attendu.** Produire un dossier professionnel réutilisable par une équipe qui n'a pas participé à l'exercice. Il doit inclure le contexte, le périmètre, les objectifs, les critères, les données utilisées, les rôles, les décisions, les risques, les limites, les résultats et le plan de suivi. Justifier les choix en reliant chacun d'eux à une preuve ou à une hypothèse explicitement marquée. Décrire comment vérifier l'efficacité de la réponse et ce qui déclencherait une révision de la décision.

**Correction attendue.** Une solution experte ne se contente pas de choisir une option ; elle compare les scénarios, fixe les critères avant le résultat, documente les responsabilités et signale les informations manquantes. Elle prévoit les conditions d'arrêt, les mesures temporaires, la communication, les dépendances et la vérification de fin. Le plan d'action est réaliste, ses résultats sont mesurables et le risque résiduel est soumis à une personne habilitée.

## Ressources techniques et références

- [ISO 22301 — systèmes de management de la continuité d'activité](https://www.iso.org/standard/75106.html)
- [NIST SP 800-34 Rev. 1 — planification de contingence des systèmes d'information](https://csrc.nist.gov/pubs/sp/800/34/r1/final)

Les documents de référence apportent des principes et des méthodes, mais leur applicabilité dépend du contexte réel. Vérifier l'édition et le statut de la source au moment de l'utiliser, surtout lorsqu'il s'agit de normes, d'exigences réglementaires ou de guides de marché. Une référence n'est pas à elle seule la preuve de conformité d'une organisation : les contrôles doivent être reliés aux exigences applicables et aux preuves recueillies.

## Synthèse

Gestion de crise et Plan de Reprise exige une méthode qui transforme l'expérience en décisions traçables, des responsabilités claires, une analyse des risques proportionnée et des vérifications orientées résultats. Le professionnel expert documente les critères, maintient les incertitudes visibles et veille à ce que les décisions soient appliquées et contrôlées. La qualité du dispositif se mesure dans son fonctionnement réel, sa résilience aux imprévus et sa capacité à améliorer durablement les opérations.