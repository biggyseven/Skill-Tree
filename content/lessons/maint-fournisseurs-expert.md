# Pilotage et évaluation des fournisseurs

> **Mise en contexte**
>
> Une entreprise s'appuie sur plusieurs prestataires : hébergement, maintenance des équipements, licences, sauvegarde externalisée, connectivité et assistance. Les rapports mensuels affichent des SLA convenables, mais les incidents récurrents augmentent, les sous-traitants ne sont pas tous connus et la récupération des données dépend d'un format propriétaire. Le pilotage expert ne consiste pas à attribuer une note annuelle : il faut maîtriser la dépendance, comparer la performance aux engagements réels, traiter les risques de sécurité et organiser une sortie réaliste.
>
> Un fournisseur peut être performant sur un indicateur tout en présentant un risque majeur sur un autre. La décision doit combiner service rendu, criticité, coûts, sécurité, continuité et possibilité de remplacement.

## Objectifs pédagogiques

Tu vas apprendre à segmenter les fournisseurs selon le risque, construire une évaluation qui repose sur des preuves, interpréter des SLA sans confusion, intégrer le risque de chaîne d'approvisionnement et de sous-traitance, définir des exigences contractuelles mesurables, gérer les incidents fournisseurs et préparer un plan de sortie.

## Prérequis

Une compréhension des contrats de services, des changements, de la gestion des incidents et des niveaux de service est recommandée. Les décisions contractuelles et juridiques finales relèvent des personnes habilitées de l'organisation ; le technicien apporte les critères techniques, les preuves et l'analyse du risque.

## 1. Comprendre le cycle de vie d'un fournisseur

Le risque existe avant la signature et demeure après la fin du contrat. Il faut distinguer la qualification, la sélection, l'intégration, l'exploitation, la revue, le renouvellement et la sortie. À chaque étape, l'organisation doit savoir qui décide, quels éléments de preuve sont exigés et comment un risque non acceptable est traité.

### Schéma 1 — Cycle de gouvernance

~~~mermaid
flowchart TD
    A[Besoin et criticité] --> B[Qualification du fournisseur]
    B --> C[Due diligence et analyse du risque]
    C --> D[Sélection et contrat]
    D --> E[Intégration et contrôle des accès]
    E --> F[Suivi du service et des risques]
    F --> G{Renouveler ?}
    G -- Oui --> H[Revue et plan d'amélioration]
    H --> F
    G -- Non --> I[Sortie, transfert et révocation des accès]
~~~

Le contrat doit correspondre au service réellement fourni. Un service de support standard ne présente pas les mêmes dépendances qu'une plateforme de sauvegarde ou qu'un fournisseur qui administre à distance les équipements de cœur de réseau. Documente les fonctions, les données, les accès, les dépendances, les délais de reprise et les conséquences d'une indisponibilité.

## 2. Segmenter les fournisseurs selon le risque

Une segmentation utile prend en compte plusieurs dimensions :

- **Criticité métier** : impact sur la continuité, la sécurité ou le fonctionnement de l'entreprise.
- **Accès** : privilèges, accès à distance, accès aux données sensibles et capacité de modification.
- **Dépendance** : difficulté de remplacement, portabilité des données, exclusivité technique.
- **Exposition** : connectivité externe, chaîne de sous-traitance, surface d'attaque et maturité de sécurité.
- **Concentration** : part du service ou des actifs dépendant d'un seul fournisseur.
- **Récupération** : disponibilité d'une solution de repli, délai de transition et compétences internes.

Évite une formule qui donne une fausse impression de précision. Une grille qualitative peut être appropriée si les critères sont définis et documentés. Pour un fournisseur critique, une faiblesse sur les contrôles d'accès ou l'absence d'une voie de sortie peut bloquer la validation même si le score moyen reste élevé.

### Exemple de classement

| Classe | Exemple | Revue attendue |
|---|---|---|
| Critique | Hébergement de systèmes essentiels, sauvegarde centrale, réseau cœur | Revue approfondie et périodique, exercices de continuité, suivi des incidents majeurs |
| Élevée | Fournisseur d'un service important avec données ou accès privilégiés | Vérification des accès, sécurité, SLA et plans de remédiation |
| Modérée | Service métier important mais facilement remplaçable | Suivi de la performance et vérification des obligations pertinentes |
| Faible | Prestation limitée sans accès sensible ni dépendance forte | Contrôle proportionné et réévaluation si le périmètre change |

## 3. Réaliser une due diligence utile

La due diligence ne se réduit pas à demander une brochure. Elle vérifie que le fournisseur est capable de délivrer le service de manière durable et dans les conditions de risque acceptées. Selon la criticité, recueille les éléments sur l'organisation, la sécurité, les accès, la gestion des vulnérabilités, les mises à jour, le traitement des incidents, la continuité, la localisation des données, les sous-traitants, les pratiques de sauvegarde et la gestion des changements.

Demande des preuves ciblées : rapports de contrôle pertinents, procédures, résultats de tests, attestations dont le périmètre est clair, plans de traitement d'écarts et dates de dernière revue. Une attestation ne prouve pas nécessairement que tous les services ou toutes les régions sont couverts. Vérifie les exclusions, la période et les systèmes concernés. Lorsque les preuves ne peuvent pas être obtenues, note la limite et évalue le risque compensatoire.

### Schéma 2 — Chaîne de confiance

~~~mermaid
flowchart LR
    A[Organisation] --> B[Fournisseur principal]
    B --> C[Sous-traitant]
    C --> D[Service technique spécialisé]
    A --> E[Critères et obligations]
    E --> B
    E --> C
    E --> D
    D --> F[Preuves et suivi du risque]
    F --> A
~~~

La responsabilité ne disparaît pas parce qu'une tâche est sous-traitée. Identifie qui assure le contrôle, qui reçoit les alertes et qui peut autoriser une dérogation. Vérifie les accès tiers, leur durée, la traçabilité des actions, la révocation et le traitement d'un compte compromis.

## 4. Définir les engagements de service de manière mesurable

Un SLA doit définir le service, le début et la fin d'une mesure, la période, les exclusions, la source des données, la méthode de calcul et les responsabilités de chaque partie. « Disponibilité de 99,9 % » ne suffit pas sans préciser le service mesuré, la fenêtre, les maintenances exclues et la façon de gérer les pannes partielles.

Distingue les temps de prise en charge, de réponse technique, de restauration du service et de résolution définitive. Ils décrivent des résultats différents. Un fournisseur peut répondre rapidement à un ticket sans rétablir le service. De même, un accord peut exclure une panne qui est pourtant importante pour l'entreprise ; il faut alors examiner l'adéquation du contrat au besoin métier.

Établis un dictionnaire des indicateurs. Pour chaque KPI, note le propriétaire, l'origine, la fréquence, les règles de calcul, les seuils, les limites et la décision déclenchée. Compare les données internes et les rapports du fournisseur, surtout après un incident majeur. Des périodes d'indisponibilité arrondies, des horodatages non alignés ou des exclusions mal appliquées peuvent changer le résultat.

## 5. Construire un scorecard sans cacher les risques critiques

Un tableau de bord peut rassembler :

- performance du service et respect des engagements ;
- incidents, récurrence, gravité et qualité de résolution ;
- qualité de communication et de reporting ;
- conformité aux exigences de sécurité et délai de traitement des écarts ;
- continuité, résultats d'essais et disponibilité du plan de sortie ;
- prévisibilité des coûts, transparence des changements et facturation ;
- qualité de la coopération et réalisation des actions d'amélioration.

Choisis les pondérations avant la revue et documente les preuves. Un score agrégé ne doit pas effacer un échec critique. Par exemple, un bon respect des délais de ticket ne compense pas une incapacité à révoquer rapidement un accès privilégié ou à restaurer des données. Définis les critères bloquants et les règles d'escalade séparément du score moyen.

### Schéma 3 — Revue des performances

~~~mermaid
flowchart TD
    A[Mesures internes et rapport fournisseur] --> B[Réconcilier les définitions]
    B --> C[Vérifier période et exclusions]
    C --> D[Comparer aux engagements et au risque]
    D --> E[Identifier tendance et écarts]
    E --> F[Action avec responsable et échéance]
    F --> G[Revue d'efficacité]
~~~

## 6. Gérer un incident fournisseur

Pendant une panne, stabiliser le service et protéger les personnes passe avant l'évaluation contractuelle. Utilise le processus d'incident : qualifier l'impact, coordonner les équipes, conserver les événements, communiquer selon les responsabilités, valider le rétablissement et documenter les décisions. Le contrat aide à activer l'escalade, mais ne remplace pas le plan technique d'urgence.

Après la stabilisation, évalue la chronologie, l'information reçue, les décisions et les dépendances. Distingue la cause technique, les facteurs contributifs et la qualité de réponse du fournisseur. Demande des actions avec une preuve mesurable et suis leur réalisation. Si les engagements ont été respectés mais que le service reste insuffisant pour le besoin réel, révise les exigences internes plutôt que de s'en tenir à un indicateur contractuel inadapté.

## 7. Intégrer le risque cyber de la chaîne d'approvisionnement

Le risque peut provenir d'un logiciel vulnérable, d'un accès d'administration externalisé, d'une sous-traitance inconnue, d'une mise à jour non maîtrisée, d'un composant contrefait ou d'une défaillance de disponibilité. Définis des obligations proportionnées : authentification forte, comptes nominatifs, accès limité dans le temps, journalisation, notification d'incident, contrôle des sous-traitants, gestion des vulnérabilités, support de sécurité, protection des données et suppression vérifiable en fin de service.

Les exigences doivent préciser le délai et le canal de notification, les informations attendues, la coopération lors des investigations et les conditions d'utilisation des données. Vérifie aussi les modalités de récupération, l'export dans un format exploitable, les délais, les coûts de sortie, l'effacement et la preuve de révocation des accès. Une clause vague comme « le fournisseur appliquera les bonnes pratiques » est difficile à contrôler.

### Fiche de revue cyber

- Quels actifs, données et environnements sont accessibles au fournisseur ?
- Les accès sont-ils nominaux, approuvés, limités et journalisés ?
- Les sous-traitants et leurs rôles sont-ils identifiés ?
- Comment sont gérés les correctifs et vulnérabilités critiques ?
- Qui doit notifier un incident et dans quel délai convenu ?
- Quels éléments de preuve sont disponibles et quelle est leur période de couverture ?
- Comment les données sont-elles exportées et supprimées lors de la sortie ?
- Quel plan de continuité existe en cas d'indisponibilité du fournisseur ?

## 8. Préparer une stratégie de sortie réaliste

La sortie doit être préparée avant l'urgence. Identifie les données à récupérer, les formats, les dépendances, les comptes, les clés, les configurations, les licences, les contrats liés et les compétences nécessaires au transfert. Vérifie qu'un autre fournisseur peut reprendre le service et que l'organisation pourra accéder aux données pendant la transition.

Un plan de sortie devrait préciser le déclencheur, le décideur, le calendrier, la séquence de transfert, les critères d'acceptation, la continuité temporaire, la révocation des accès, les preuves d'effacement et le sort des composants. Effectue un exercice pour les fournisseurs critiques. Un plan jamais testé peut échouer au moment où le temps et les ressources manquent.

## 9. TP guidé : évaluer un fournisseur de sauvegarde

**Scénario.** Un prestataire héberge des copies de sauvegarde et gère une console d'administration distante. Son rapport annonce un SLA conforme, mais les restaurations complètes ne sont testées qu'une fois par an.

1. Cartographie les données, les accès, les sous-traitants et les dépendances.
2. Définis les résultats de reprise attendus avec les propriétaires métier.
3. Vérifie les règles de notification, la couverture du contrat et les exclusions du SLA.
4. Examine les preuves d'accès, de journalisation, de protection et de révocation.
5. Conçois un test de restauration autorisé en environnement adapté.
6. Évalue le plan de sortie et la portabilité des données.
7. Produit un scorecard avec preuves, points bloquants, actions, responsables et échéances.

**Critère de réussite :** la conclusion relie chaque note à une donnée ou une preuve, indique les incertitudes et ne laisse pas un bon score global masquer une lacune critique.



## 10. Gouvernance opérationnelle : qui décide, qui contrôle, qui accepte le risque ?

La gestion des fournisseurs ne doit pas reposer sur une seule personne qui connaît « le prestataire ». Les achats négocient souvent les conditions commerciales, le service propriétaire connaît l'usage métier, l'exploitation observe la disponibilité, la sécurité étudie les contrôles, le juridique vérifie les obligations, la finance examine le coût et la direction décide du risque résiduel selon ses délégations. Le responsable fournisseur coordonne ces perspectives, mais ne peut pas se substituer à tous les propriétaires.

La gouvernance doit exister avant la signature et rester active pendant tout le contrat. Elle définit les seuils de décision, les preuves minimales, les personnes autorisées à accepter une exception, les situations imposant une escalade et le rythme des revues. Sans cette gouvernance, la relation est souvent pilotée par les urgences : on relit le contrat après un incident, on découvre tardivement un sous-traitant, ou on renouvelle automatiquement un service impossible à remplacer.

### 10.1 Une matrice de responsabilités utile

La matrice RACI identifie qui réalise (R), qui est responsable de la décision finale (A), qui est consulté (C) et qui est informé (I). Elle doit correspondre à la structure réelle de l'organisation et ne doit pas produire plusieurs personnes « responsables finales » pour une même décision si la règle interne exige un décideur unique.

| Activité | Responsable métier | Gestionnaire fournisseur | Achats / juridique | IT / sécurité | Finance |
|---|---|---|---|---|---|
| Définir le besoin et l'impact | A/R | C | C | C | I |
| Classer la criticité | A | R | C | R/C | I |
| Conduire la due diligence | C | A/R | C | R | I |
| Négocier prix et contrat | C | R | A/R | C | C |
| Valider les exigences de sécurité | C | C | C | A/R | I |
| Mesurer le service | A | R | I | R/C | C |
| Accepter un risque important | A selon délégation | C | C | C | C |
| Renouveler ou sortir | A | R | R/C | C | C |

Le tableau est un exemple pédagogique. Certaines organisations attribuent l'acceptation du risque à une fonction dédiée ; d'autres la réservent à un comité ou à une direction. Il faut suivre la délégation réelle, particulièrement quand l'achat implique des données sensibles, un service essentiel ou une dépendance longue.

### 10.2 Le comité fournisseur

Une revue fournisseur utile est orientée vers des décisions. Elle ne doit pas être une réunion où chacun lit son tableau. Son ordre du jour peut comprendre les engagements du mois, les incidents majeurs, les risques ouverts, les changements de périmètre, les sous-traitants, les évolutions tarifaires, les actions en retard, les projets à venir et les décisions qui exigent un arbitrage.

Pour éviter les échanges stériles, prépare avant la réunion :
- un scorecard avec les définitions et la période ;
- la liste des écarts qui dépassent les seuils ;
- les preuves et les limites des données ;
- le statut des actions convenues à la revue précédente ;
- les décisions attendues, avec options, impact et recommandation ;
- le nom d'un décideur et d'un propriétaire pour chaque action.

Le compte rendu doit consigner les décisions, les désaccords significatifs, les responsables, les dates cibles et les critères de clôture. « Le fournisseur va améliorer la qualité » est un vœu. « Le fournisseur fournit avant le 15 du mois un rapport d'analyse des trois incidents récurrents, propose deux mesures correctives et démontre leur efficacité sur les incidents du mois suivant » est vérifiable.

~~~mermaid
flowchart TD
    A[Préparer les données et décisions] --> B[Revue fournisseur]
    B --> C[Confirmer les faits et limites]
    C --> D[Arbitrer risques et priorités]
    D --> E[Attribuer responsables et échéances]
    E --> F[Suivre les preuves d'exécution]
    F --> G{Résultat obtenu ?}
    G -->|Non| H[Escalade ou plan renforcé]
    H --> B
    G -->|Oui| I[Clôture et capitalisation]
~~~

## 11. Due diligence : vérifier au-delà du questionnaire

La due diligence est une vérification préalable et proportionnée de la capacité du fournisseur à fournir le service attendu, à protéger les actifs confiés et à rester disponible. Elle ne se réduit pas à un questionnaire de sécurité rempli par le commercial. Les réponses peuvent être incomplètes, anciennes ou rédigées à un niveau général qui ne couvre pas le service réellement acheté.

La profondeur de l'examen doit suivre le risque. Pour une prestation de faible impact qui n'accède à aucune donnée sensible, un contrôle limité peut suffire. Pour un fournisseur qui héberge des données critiques, administre l'infrastructure ou devient impossible à remplacer rapidement, il faut davantage de preuves et une décision d'acceptation formalisée.

### 11.1 Les domaines à examiner

| Domaine | Questions | Preuves possibles |
|---|---|---|
| Identité et capacité juridique | L'entité signataire est-elle celle qui fournira le service ? | Informations légales, structure du groupe, signataire autorisé |
| Solidité financière | Le fournisseur peut-il soutenir le service sur la durée ? | Informations financières proportionnées, références, plan de continuité |
| Compétence opérationnelle | Dispose-t-il des équipes, méthodes et capacités requises ? | CV/compétences pertinents, certifications utiles, procédures, indicateurs |
| Sécurité | Comment les accès, secrets, vulnérabilités et journaux sont-ils gérés ? | Résumé d'audit, description des contrôles, preuves d'application et réserves |
| Confidentialité et données | Où les données résident-elles et qui peut y accéder ? | Architecture, accords de traitement applicables, flux et lieux de stockage |
| Continuité | Comment le service reprend-il après un incident ? | Plans, résultats d'exercice, objectifs et dépendances |
| Chaîne de sous-traitance | Quelles autres organisations participent au service ? | Liste des sous-traitants, rôles, localisation, processus d'approbation |
| Dépendance technique | Les formats et interfaces sont-ils propriétaires ? | Spécifications, API, formats d'export, procédure de migration |
| Réputation et conformité | Des incidents pertinents ou sanctions doivent-ils être évalués ? | Sources publiques fiables, notifications contractuelles, contrôles adaptés |

Ne demande pas systématiquement des documents sensibles que l'organisation ne peut pas stocker ou protéger. Demande une assurance pertinente et proportionnée, vérifie son périmètre, et limite la conservation des documents confidentiels selon la politique de l'entreprise. Les certifications ou rapports indépendants peuvent aider, mais ne constituent pas une preuve universelle : il faut lire leur période, leur périmètre, les exclusions et les réserves.

### 11.2 Vérifier les réponses d'un questionnaire

Pour chaque réponse importante, demande-toi :
- est-elle liée au service acheté plutôt qu'à l'ensemble du groupe ?
- est-elle récente et couvre-t-elle la période pertinente ?
- est-elle soutenue par une preuve ou seulement déclarée ?
- l'organisme de contrôle est-il indépendant et sa mission adaptée ?
- les exceptions sont-elles décrites ?
- les actions correctives sont-elles identifiées et suivies ?
- le contrôle est-il réellement mis en œuvre pendant notre utilisation du service ?

Une réponse « oui » à « les données sont-elles sauvegardées ? » ne montre pas combien de copies existent, qui peut les supprimer, combien de temps elles sont conservées, si la restauration a été testée ou si la copie inclut toutes les données utiles. La bonne question d'audit réclame un résultat : « Montrez le dernier test de restauration représentatif, le temps mesuré, les éléments restaurés et la validation du propriétaire du service. »

### 11.3 Risque intrinsèque et risque résiduel

Le risque intrinsèque représente le risque avant de tenir compte des contrôles identifiés ; le risque résiduel est celui qui reste après leur prise en compte. Cette distinction n'est utile que si les contrôles sont réellement vérifiés. Une déclaration de sécurité ne doit pas faire artificiellement passer un fournisseur critique de risque élevé à risque faible.

~~~mermaid
flowchart LR
    A[Service et données concernés] --> B[Scénario de risque intrinsèque]
    B --> C[Contrôles déclarés]
    C --> D[Preuves de conception et d'exécution]
    D --> E[Évaluer efficacité et limites]
    E --> F[Risque résiduel]
    F --> G{Sous le seuil accepté ?}
    G -->|Oui| H[Approbation et suivi]
    G -->|Non| I[Mesures compensatoires, renégociation ou refus]
~~~

Le propriétaire habilité peut accepter un risque résiduel dans les limites de sa délégation, pour une durée définie et avec des conditions. L'acceptation devrait préciser le risque, les raisons, les mesures compensatoires, l'expiration, le responsable de la revue et les événements qui déclenchent une réévaluation. Un risque sans date de revue est susceptible de devenir une exception permanente.

## 12. Écrire des exigences contractuelles mesurables

Un contrat fournisseur doit traduire les besoins métier et les risques en engagements compréhensibles par les deux parties. L'équipe technique aide à définir les critères, les mesures, la preuve et le mode de validation ; le service juridique valide le texte définitif. Le cours ne constitue pas un avis juridique et les clauses doivent être adaptées au droit applicable, au secteur, à la juridiction et au pouvoir de négociation.

### 12.1 Décrire le service et ses frontières

Le contrat doit permettre de savoir quel service est fourni, quels environnements sont couverts, quels horaires s'appliquent, quelles dépendances sont sous la responsabilité du client, quelles exclusions s'appliquent et quels éléments sont fournis par le fournisseur. Les désaccords de SLA proviennent souvent d'un périmètre mal défini : le fournisseur mesure le cœur de plateforme tandis que le client mesure tout le parcours utilisateur.

Pour chaque engagement, indique :
- la définition opérationnelle ;
- le périmètre et les éléments exclus ;
- la période de calcul ;
- la source faisant autorité ;
- la fréquence du rapport ;
- les seuils et cas d'escalade ;
- la façon de traiter les mesures manquantes ou contestées ;
- les actions en cas d'écart ;
- le droit d'obtenir une explication et des preuves suffisantes.

### 12.2 Clauses techniques à considérer

Selon le service et les risques, les exigences peuvent couvrir les accès administratifs, la MFA, la gestion des comptes de service, la journalisation, la notification d'incident, les correctifs, les tests de restauration, les objectifs de reprise, la localisation des données, la suppression des données en fin de contrat, la gestion des vulnérabilités, le recours à des sous-traitants, les changements importants, l'auditabilité et la coopération pendant la sortie.

Ne copie pas automatiquement une liste de clauses d'un autre contrat. Demande si chaque obligation est nécessaire, mesurable, faisable, assignée à une partie et vérifiable. Une clause exigeant une notification « immédiate » sans définir le déclencheur ni le canal peut créer une ambiguïté. Une exigence de notification doit définir l'événement, le délai, le contenu minimal, les mises à jour, le contact et les modalités de coopération.

### 12.3 SLA, SLO et OLA

Un **SLA** formalise un engagement de service entre le fournisseur et son client. Un **SLO** est un objectif de niveau de service défini pour guider les opérations ; il n'est pas automatiquement une obligation contractuelle. Un **OLA** formalise des engagements opérationnels internes entre équipes qui contribuent à la prestation. Les usages exacts varient selon les organisations : le document doit préciser ce qu'il appelle SLA, SLO et OLA.

Exemple :
- SLA client : disponibilité mensuelle de la fonction de commande mesurée selon une méthode définie, avec exclusions explicites et procédure de contestation ;
- SLO technique : latence au 95e percentile sous un seuil convenu, mesurée sur des requêtes représentatives ;
- OLA interne : équipe infrastructure répond à une alerte de criticité donnée dans un délai cible et fournit un compte rendu à l'équipe de service.

Un SLA de disponibilité de 99,9 % sur une période théorique de 30 jours correspond à 43,2 minutes d'indisponibilité sur cette période si la mesure couvre toute la fenêtre et si aucun intervalle n'est exclu. Ce calcul ne doit pas être utilisé sans vérifier la définition contractuelle : les fenêtres de maintenance, exclusions, unités de mesure et méthodes de calcul peuvent modifier le résultat.

~~~text
Objectif métier
      |
      v
SLA contractuel fournisseur
      |
      v
SLO technique des composants
      |
      v
OLA entre équipes internes
      |
      v
Mesure cohérente de bout en bout
      |
      v
Décision si la cible n'est pas atteinte
~~~

## 13. Mesurer la performance sans fabriquer une bonne note

La performance d'un fournisseur est multidimensionnelle. Le coût le plus bas ne signifie pas le meilleur service ; une disponibilité élevée n'efface pas une mauvaise réponse aux incidents ; une bonne relation commerciale ne remplace pas les preuves. Le scorecard doit faire apparaître les arbitrages, les tendances et les risques bloquants.

### 13.1 Concevoir des indicateurs actionnables

| Dimension | Indicateur possible | Piège à éviter |
|---|---|---|
| Disponibilité | Disponibilité mesurée de bout en bout | Ne mesurer qu'un composant facile |
| Incident | Temps d'accusé de réception, de restauration et de résolution | Confondre ces trois durées |
| Qualité | Taux de réouverture, récurrence, incidents liés à un changement | Récompenser le volume de tickets clos sans qualité |
| Support | Respect des priorités, qualité des escalades, disponibilité des compétences | Utiliser seulement une moyenne globale |
| Sécurité | Délai de traitement des vulnérabilités, accès privilégiés conformes, actions ouvertes | Se fier uniquement à un questionnaire annuel |
| Continuité | Résultats d'exercices, temps de reprise observé, écarts non résolus | Confondre plan documenté et capacité démontrée |
| Coûts | Coût total, variation, coûts de changement et de sortie | Comparer des périmètres différents |
| Innovation | Délais d'amélioration, qualité des changements, valeur livrée | Mesurer le nombre de changements sans résultat |
| Collaboration | Précision des rapports, transparence, suivi des actions | Remplacer des preuves par une appréciation subjective |

Chaque KPI doit avoir un propriétaire, une source, une fréquence, une formule et une cible. Si l'équipe change de méthode, garde la version et explique l'effet sur les comparaisons historiques. Les valeurs manquantes doivent être indiquées et investiguées, non remplacées par zéro ou par la dernière valeur connue sans signalement.

### 13.2 Score pondéré et critères bloquants

Un score pondéré peut aider à comparer des fournisseurs, à condition de ne pas cacher un défaut critique. Exemple indicatif : service 30 %, sécurité 25 %, continuité 20 %, coopération 10 %, coût et valeur 15 %. Les pondérations doivent refléter les objectifs de l'organisation et être décidées avant de regarder les résultats, sinon elles peuvent être ajustées pour légitimer un renouvellement déjà souhaité.

Définis des conditions éliminatoires ou des seuils d'escalade en dehors de la moyenne : défaut non maîtrisé d'accès à des données critiques, absence de coopération sur un incident grave, impossibilité de restaurer un service essentiel ou refus d'appliquer une obligation contractuelle applicable. Un score de 92/100 ne doit pas rendre acceptable automatiquement un contrôle bloquant défaillant.

~~~mermaid
flowchart TD
    A[Collecter les KPI avec définitions] --> B[Contrôler la qualité des données]
    B --> C[Calculer les scores par dimension]
    C --> D{Critère bloquant dépassé ?}
    D -->|Oui| E[Escalade et décision de risque]
    D -->|Non| F[Calcul du score pondéré]
    F --> G[Analyser tendances, incidents et actions]
    G --> H[Renouveler, corriger, renégocier ou sortir]
~~~

### 13.3 Calculer et interpréter un SLA

Supposons que le fournisseur annonce 99,95 % de disponibilité dans un tableau de bord. Le client constate que plusieurs utilisateurs ne peuvent pas passer une commande. Avant de conclure à une violation, vérifie :
- si l'indicateur mesure le service de bout en bout ou un composant ;
- si les tentatives utilisateur et les erreurs de dépendance sont incluses ;
- si l'horloge, la fenêtre et les exclusions correspondent au contrat ;
- si les maintenances annoncées sont réellement couvertes par les exclusions ;
- si la donnée provient du fournisseur, du client ou d'une mesure commune ;
- si le calcul est reproductible et si les journaux sont disponibles.

Le but n'est pas d'accuser automatiquement le fournisseur, mais d'établir une base de mesure commune. Une contestation fondée sur des horodatages, une définition et des échantillons réconciliés a davantage de chances de déboucher sur une correction que deux tableaux de bord contradictoires.

## 14. Cyberrisque de la chaîne d'approvisionnement et sous-traitance

La chaîne d'approvisionnement numérique inclut bien plus que le fournisseur directement payé. Elle peut comprendre l'hébergeur, un service d'identité, un service de supervision, un éditeur de bibliothèque, un sous-traitant de support, un centre de données, un fournisseur de mises à jour et un outil utilisé pour construire le produit. Une relation indirecte peut donc introduire un risque même lorsque le contrat principal semble robuste.

NIST SP 800-161 Rev. 1, Update 1 recommande d'intégrer la gestion des risques cyber de la chaîne d'approvisionnement aux pratiques de gestion du risque de l'organisation. NIST SP 1305 explique comment utiliser le Cybersecurity Framework 2.0, notamment la catégorie GV.SC, pour structurer une capacité de gestion du risque et communiquer les exigences aux fournisseurs. Ces ressources sont des guides à adapter au contexte ; elles ne remplacent pas les obligations applicables ni l'analyse technique du service réellement utilisé.

### 14.1 Cartographier les dépendances

Pour chaque fournisseur important, identifie les composants et sous-traitants qui contribuent au service, les données qu'ils touchent, les privilèges qu'ils possèdent, la localisation pertinente, les points de défaillance communs et la manière dont tu seras informé d'un changement. Tu ne connaîtras pas forcément toute la chaîne en détail : consigne les limites de visibilité et demande une transparence proportionnée au risque.

~~~mermaid
flowchart TD
    A[Organisation cliente] --> B[Fournisseur principal]
    B --> C[Hébergeur]
    B --> D[Prestataire de support]
    B --> E[Service d'identité]
    C --> F[Infrastructure sous-jacente]
    D --> G[Outils et accès du sous-traitant]
    E --> H[Service amont]
    F --> I[Effet potentiel sur le service client]
    G --> I
    H --> I
~~~

La cartographie doit aider à répondre à une question : si un élément tombe en panne ou est compromis, quel service, quelle donnée et quelle décision sont touchés ? Une liste de fournisseurs sans liens de dépendance ne permet pas de comprendre les effets en cascade.

### 14.2 Contrôles de sécurité fournisseur

Les contrôles à examiner dépendent du modèle du service, mais peuvent comprendre :
- gestion des identités et des accès, avec privilèges minimaux et révocation dans les délais ;
- MFA et gestion distincte des comptes d'administration lorsque cela est requis ;
- sécurité du personnel, des postes d'administration et des accès distants ;
- gestion des vulnérabilités, correctifs et composants logiciels ;
- protection et conservation des journaux ;
- séparation des clients et gestion des configurations ;
- contrôle de l'intégrité des artefacts, des mises à jour et des composants ;
- gestion des incidents, notification, préservation de preuves et coopération ;
- sauvegarde, restauration, continuité et exercices ;
- gestion des sous-traitants et changements de chaîne d'approvisionnement ;
- suppression des données et retrait des accès à la fin de la prestation.

Ne suppose pas qu'un fournisseur sans certification est nécessairement mauvais ni qu'un fournisseur certifié est automatiquement sûr. Une certification peut être utile si le périmètre et les contrôles sont pertinents ; elle ne couvre pas nécessairement le produit, la région, la période ou les configurations que tu utilises. Vérifie aussi les exceptions et les actions en cours.

### 14.3 Sécurité des logiciels et des mises à jour

Pour les services logiciels, la provenance des composants, le processus de développement, la gestion des dépendances, la signature des versions, la gestion des vulnérabilités et la capacité à notifier une faille influencent la confiance. Selon le type de service, une nomenclature logicielle (SBOM), des attestations de construction, un mécanisme de signature ou des preuves de test peuvent être pertinentes. Ne demande pas un artefact juste pour cocher une case : définis la question à laquelle il doit répondre et comment tu vérifieras son utilité.

L'organisation doit aussi savoir ce qu'elle fera après une alerte de sécurité : qui évalue la pertinence, quel actif ou produit est concerné, quelles mesures compensatoires sont possibles, qui décide d'une mise à jour ou d'un arrêt, et comment l'impact sera communiqué. Une notification de vulnérabilité ne doit pas être laissée dans la boîte mail du gestionnaire fournisseur sans propriétaire technique.

### 14.4 Changement de sous-traitant ou de localisation

Le remplacement d'un sous-traitant, le déplacement d'un centre de données ou l'introduction d'un nouvel outil d'accès peut modifier le risque. Les mécanismes contractuels doivent prévoir un avis raisonnable, des critères de validation et un processus pour évaluer l'effet sur la sécurité, la confidentialité et la continuité. Si l'organisation ne peut pas s'opposer à un changement, elle peut au moins demander une notification, les informations nécessaires, une transition et les options de sortie applicables.

## 15. Continuité, incident et escalade fournisseur

La qualité d'une relation se révèle souvent lorsque le service est dégradé. Une procédure d'incident fournisseur doit préciser qui constate l'événement, qui ouvre le ticket, quelles preuves sont collectées, comment la sévérité est évaluée, qui communique avec les utilisateurs, qui coordonne les équipes et qui accepte la fin de l'incident.

### 15.1 Distinguer les temps de service

Ne confonds pas :
- accusé de réception ;
- prise en charge par une compétence adaptée ;
- début du diagnostic ;
- contournement ;
- rétablissement du service ;
- résolution durable ;
- livraison d'un rapport d'incident ;
- validation des actions correctives.

Un contrat peut définir un temps de réponse sans engager un temps de restauration. Un scorecard qui regroupe ces temps dans une seule moyenne peut masquer un point de défaillance. Définis chaque horodatage et le canal qui fait autorité ; précise aussi les conditions de pause du chronomètre, si elles existent, et qui peut les valider.

### 15.2 Construire une matrice de sévérité partagée

La sévérité devrait combiner impact et urgence, par exemple le nombre d'utilisateurs touchés, la criticité métier, l'existence d'un contournement, les risques de sécurité, la perte ou corruption des données et la durée. Le fournisseur et le client doivent comprendre les seuils ; sinon chacun peut attribuer une priorité différente au même incident.

~~~mermaid
flowchart TD
    A[Signalement d'incident fournisseur] --> B[Confirmer service, heure et impact]
    B --> C[Classer la sévérité avec critères partagés]
    C --> D[Activer contacts et escalade]
    D --> E[Collecter faits et chronologie]
    E --> F[Contournement autorisé si nécessaire]
    F --> G[Tester le rétablissement]
    G --> H[Rapport et analyse de cause]
    H --> I[Actions correctives vérifiées]
~~~

### 15.3 Vérifier la continuité réellement démontrée

Un plan de continuité documenté n'est pas une preuve de capacité à reprendre le service. Demande les résultats d'exercices, les scénarios couverts, les dépendances, les écarts, les personnes présentes, les délais observés et le traitement des défaillances. Vérifie les objectifs de reprise et de perte de données contre la tolérance métier, pas seulement contre les capacités annoncées par le fournisseur.

Les exercices doivent être adaptés à la criticité. Une revue documentaire peut être suffisante pour une prestation faible risque ; un service critique peut nécessiter un test coordonné de restauration, de basculement ou de transfert dans un environnement isolé. Aucun test perturbant ne doit être réalisé sans mandat, fenêtre, plan de retour et coordination du propriétaire du service.

### 15.4 Après l'incident

Le bilan fournisseur doit décrire la chronologie, la portée, l'impact, la cause confirmée ou les limites de l'analyse, les mesures immédiates, les facteurs contributifs et les actions de prévention. Un rapport qui se contente de « redémarrage effectué » ne répond pas nécessairement à la question de récidive. Pour les incidents répétés, demande une analyse reliant les incidents et démontre si les actions précédentes ont changé le résultat.

Évite que le fournisseur soit l'unique juge de sa propre correction. Lorsque le risque le justifie, utilise une mesure côté client, une vérification indépendante ou un exercice conjoint dont les critères de réussite ont été définis à l'avance.

## 16. Préparer une sortie et démontrer la réversibilité

La réversibilité ne se réduit pas à une clause indiquant que les données peuvent être exportées. Une sortie peut échouer parce que l'export ne contient pas les métadonnées, parce qu'une licence est nécessaire pour lire les données, parce que les identités sont gérées par le fournisseur, parce que le nouveau prestataire n'a pas de capacité disponible ou parce que les données sont transférées mais pas validées par le métier.

Le plan de sortie doit commencer dès la conception de la relation. Pour un service critique, il devrait identifier les données, configurations, secrets, journaux, documents, interfaces, scripts, licences, comptes, personnes clés, droits de propriété, coûts, délais et dépendances. Il précise qui fournit quoi, dans quel format, à quel moment et selon quel contrôle de réussite.

### 16.1 Les étapes d'une transition

~~~mermaid
flowchart TD
    A[Déclencheur de sortie] --> B[Nommer le responsable et le calendrier]
    B --> C[Inventorier données, configurations et dépendances]
    C --> D[Préparer export, accès et transfert]
    D --> E[Importer dans la cible de remplacement]
    E --> F[Vérifier intégrité et fonctionnalité]
    F --> G{Résultats acceptés ?}
    G -->|Non| H[Corriger et répéter les tests]
    H --> E
    G -->|Oui| I[Basculer avec plan de retour]
    I --> J[Révoquer accès et secrets du fournisseur]
    J --> K[Confirmer restitution ou effacement]
    K --> L[Clôturer les obligations et les risques]
~~~

### 16.2 Liste de contrôle de la sortie

Vérifie notamment :
- les formats d'export sont documentés, utilisables et testés ;
- les données, pièces jointes, historiques et métadonnées nécessaires sont inclus ;
- les identifiants et référentiels restent cohérents ;
- les journaux et éléments utiles à une enquête sont conservés selon les règles applicables ;
- les clés et secrets sont transférés ou renouvelés de manière sécurisée ;
- les licences, certificats, domaines, DNS et intégrations sont traités ;
- les comptes de service, accès privilégiés et accès de sous-traitants sont révoqués ;
- le transfert est accompagné par les personnes compétentes ;
- le nouveau service est validé par des tests techniques et métier ;
- la suppression des copies résiduelles est confirmée, dans le périmètre prévu ;
- les frais de sortie, périodes de préavis, dépendances et contraintes de rétention sont connus ;
- un plan de retour existe si la bascule échoue.

Ne suppose pas qu'un fournisseur peut effacer toutes les copies immédiatement : des contraintes légales, de sauvegarde ou de rétention peuvent imposer un délai. Le contrat et les règles de conservation doivent préciser comment la suppression est organisée et prouvée, sans promettre un résultat techniquement impossible.

### 16.3 Dépendance et coût de sortie

Le coût de sortie comprend plus que les frais contractuels : temps des équipes, conversion de formats, re-développement d'intégrations, double exploitation, formation, transfert de données, contrôle de sécurité, risques d'interruption et coûts de licences. Il faut le comparer aux bénéfices de la relation actuelle et au coût d'un fournisseur alternatif. Une sortie théorique coûteuse ou jamais testée peut constituer une dépendance stratégique.

Pour les fournisseurs à risque élevé, un exercice de réversibilité en environnement de test peut détecter les difficultés avant la fin du contrat. Définis en amont les critères : intégrité des données, délai, fonctionnalité minimale, correspondance des identifiants, absence de secret exposé et acceptation du propriétaire métier.

## 17. Coût total, valeur et renouvellement

Le coût total de possession (TCO) prend en compte les dépenses directes et indirectes pendant le cycle de vie. Pour comparer des offres, utilise un périmètre identique : coûts de licence, consommation, support, intégration, migration, formation, supervision, conformité, coûts de changement, frais de sortie et effort interne. Une offre avec un prix d'entrée faible peut coûter davantage si les fonctions essentielles sont en option, les limites de consommation strictes ou l'export facturé séparément.

### 17.1 Décomposer le coût total

| Composante | Questions à poser |
|---|---|
| Prix de base | Le prix dépend-il d'un utilisateur, d'un actif, d'une transaction ou d'une capacité ? |
| Options | Quelles fonctions essentielles sont facturées séparément ? |
| Consommation | Existe-t-il des limites, dépassements ou variations saisonnières ? |
| Intégration | Qui finance les connecteurs, la migration et les changements d'architecture ? |
| Exploitation | Quel effort interne reste nécessaire pour gérer le service ? |
| Support | Quels niveaux, horaires, langues et expertises sont inclus ? |
| Sécurité et conformité | Quels contrôles ou audits représentent un coût supplémentaire ? |
| Réversibilité | Quel est le coût d'export, de transition et de suppression ? |
| Indexation | Quelle formule s'applique aux renouvellements et sur quelle base ? |

Les coûts doivent être rapprochés de la valeur. Si un fournisseur évite des interruptions ou réduit des tâches manuelles, demande des mesures de base avant et après et signale les hypothèses. Ne présente pas chaque économie théorique comme un bénéfice réalisé. Un retour sur investissement solide indique l'investissement initial, les coûts récurrents, la durée, les incertitudes, le scénario de référence et les bénéfices observés ou attendus.

### 17.2 Décider du renouvellement

Le renouvellement doit être préparé suffisamment tôt pour conserver des options. Revois la performance, la sécurité, la dépendance, l'évolution du besoin, le coût total, les alternatives, le calendrier de migration et les obligations de préavis. Si le service est critique, lance l'évaluation d'alternatives avant la date limite de notification : lorsque le délai de sortie a expiré, le fournisseur peut disposer d'un levier de négociation important.

~~~mermaid
flowchart TD
    A[Revue de renouvellement] --> B[Performance et incidents]
    A --> C[Risque cyber et conformité]
    A --> D[Coût total et valeur]
    A --> E[Alternatives et réversibilité]
    B --> F[Évaluer options]
    C --> F
    D --> F
    E --> F
    F --> G{Risque et valeur acceptables ?}
    G -->|Oui| H[Renouveler avec objectifs révisés]
    G -->|Sous conditions| I[Renégocier avec plan daté]
    G -->|Non| J[Activer la sortie]
~~~

### 17.3 Négociation basée sur des faits

Prépare la négociation avec des données vérifiables, des priorités claires et une alternative réaliste. Distingue les obligations minimales, les objectifs souhaitables et les points pouvant faire l'objet d'un compromis. Par exemple, un prix plus faible ne compense pas nécessairement une absence de notification d'incident ou un export impossible. Les concessions doivent être évaluées par rapport à leur valeur et au risque créé, et enregistrées dans le contrat et le processus d'approbation.

L'équipe technique ne doit pas accepter seule des conditions commerciales ou juridiques. Elle fournit les mesures, les dépendances, les exigences de sécurité et le coût opérationnel ; les fonctions habilitées négocient, valident et signent.

## 18. Auditer les preuves et piloter les plans d'amélioration

Un fournisseur peut envoyer des rapports très soignés qui ne démontrent pas le contrôle dont le client a réellement besoin. L'évaluation doit tester la cohérence entre le rapport, le service livré, les incidents observés, les données du client et les obligations contractuelles.

### 18.1 Une fiche de preuve fournisseur

Pour chaque constat important, consigne :
- le critère : clause, SLA, politique ou exigence approuvée ;
- le fournisseur, le service et la période ;
- la preuve reçue, sa source et sa date ;
- le test ou le rapprochement effectué ;
- la limite de la preuve ;
- le fait observé ;
- le risque et les conséquences possibles ;
- le niveau de confiance de la conclusion ;
- l'action demandée, son propriétaire et son échéance ;
- la preuve de clôture et le test d'efficacité.

Une capture d'écran peut prouver un état affiché à une heure donnée ; elle ne démontre pas forcément l'historique, la totalité de la population ou la configuration de tous les environnements. Un PDF de certification peut démontrer qu'un périmètre a été évalué selon une méthode donnée pendant une période donnée ; il ne prouve pas automatiquement que le service particulier utilisé est couvert. Précise toujours ce que la preuve permet d'affirmer, et ce qu'elle ne permet pas.

### 18.2 Classer les écarts par niveau

Une classification utile distingue les points bloquants, les écarts élevés, modérés et mineurs, selon les définitions approuvées. Les critères exacts ne sont pas universels : ils doivent être adaptés à la criticité, aux obligations et à la tolérance au risque.

| Niveau indicatif | Exemple | Action de pilotage |
|---|---|---|
| Bloquant | Le fournisseur critique ne démontre pas le contrôle d'accès à des données sensibles | Escalade immédiate, mesures de protection et décision du propriétaire du risque |
| Élevé | Les résultats de restauration ne satisfont pas l'objectif convenu | Plan daté, preuve de test et revue rapprochée |
| Modéré | Rapports mensuels incomplets ou actions récurrentes en retard | Échéance de correction et contrôle à la revue suivante |
| Faible | Défaut de forme sans impact significatif démontré | Amélioration planifiée et vérification proportionnée |

Ne classe pas un défaut comme faible uniquement parce qu'il est facile à corriger, ni élevé uniquement parce qu'il semble techniquement complexe. L'impact métier, l'exposition, la capacité de détection, les mesures compensatoires et les conséquences doivent être explicites. Un fournisseur doit pouvoir examiner les faits et contester une erreur factuelle, mais le désaccord ne doit pas effacer un risque confirmé.

### 18.3 Vérifier l'efficacité de l'action

Une action déclarée terminée n'est pas forcément efficace. Si le fournisseur déclare avoir corrigé le processus de désactivation des comptes, demande la nouvelle procédure, puis des exemples récents couvrant le périmètre pertinent, la preuve de révocation des comptes concernés et les exceptions traitées. Pour un problème récurrent, vérifie la tendance après correction sur une période adaptée au service.

~~~mermaid
flowchart TD
    A[Écart documenté] --> B[Analyse de cause et portée]
    B --> C[Action avec responsable et échéance]
    C --> D[Preuve de réalisation]
    D --> E[Test d'efficacité convenu]
    E --> F{Le risque a-t-il diminué ?}
    F -->|Non| G[Action complémentaire ou escalade]
    G --> C
    F -->|Oui| H[Clôture avec preuve]
~~~

Si le fournisseur ne respecte pas son engagement, applique l'escalade contractuelle et de gouvernance prévue. Les crédits de service ou pénalités peuvent être pertinents, mais ils ne remplacent pas la réduction du risque. Un crédit financier n'empêche pas une récidive et ne restaure pas des données perdues.

## 19. Parcours pratique expert : mener une revue fournisseur en dix jours

Ce parcours sert de méthode de travail pour une revue réelle. Adapte-le à la criticité et à la disponibilité des preuves ; pour un fournisseur essentiel, la mission peut être beaucoup plus longue ou nécessiter des équipes spécialisées.

### Jours 1–2 : cadrage

Identifie le propriétaire métier, le service, les usages, les contrats, la période, les critères de décision et les restrictions. Définis ce qui serait un incident critique ou un motif de suspension. Demande l'inventaire des sous-traitants pertinents, les rapports de performance, les incidents récents, les résultats de continuité et les plans d'action ouverts.

### Jours 3–4 : revue des preuves

Compare les rapports fournisseur aux mesures internes. Vérifie les définitions, les périodes, les exclusions et la cohérence avec les tickets et changements. Sélectionne quelques cas représentatifs, y compris une exception et un incident majeur. Vérifie le périmètre des attestations et les réserves.

### Jours 5–6 : ateliers techniques et métier

Avec les personnes habilitées, examine les accès, la journalisation, les sauvegardes, la notification d'incident, les changements, les dépendances et la sortie. Ne lance aucun test actif ou perturbant sans autorisation, périmètre, fenêtre et plan de retour. Formule les questions sous forme de contrôles observables et de résultats attendus.

### Jours 7–8 : constats et risques

Sépare les faits prouvés, les déclarations, les hypothèses et les éléments manquants. Classe les écarts selon la méthode approuvée. Évalue l'impact métier, les mesures compensatoires et le risque résiduel. Partage les constats factuels avec le fournisseur pour corriger une erreur éventuelle, sans lui déléguer la décision d'accepter le risque client.

### Jour 9 : plan d'action et options

Chaque action doit avoir un résultat attendu, un responsable, une échéance et une preuve de fermeture. Pour un défaut important, prévois le suivi rapproché, l'escalade, les conditions de renouvellement ou une option de sortie. Ne demande pas seulement un plan d'action générique : la réponse doit traiter la cause et le contrôle qui empêchera la récidive.

### Jour 10 : décision

Présente une synthèse, le niveau de confiance, les écarts majeurs, les risques non résolus, les limites de visibilité, les décisions requises et le prochain jalon. La conclusion peut recommander de poursuivre sous conditions, de renégocier, de limiter temporairement l'usage ou d'activer une sortie. La décision finale appartient à l'autorité prévue.

~~~text
FICHE DE REVUE FOURNISSEUR

Fournisseur / service :
Propriétaire métier :
Gestionnaire de la relation :
Criticité et justification :
Périmètre / période :
Contrat et annexes applicables :
Sous-traitants connus et limites de visibilité :
SLA / KPI / sources de mesure :
Incidents majeurs et récurrences :
Sécurité / accès / données :
Sauvegarde / continuité / exercices :
Risques et preuves manquantes :
Actions ouvertes / retards :
Coût total / changement de prix :
Réversibilité / sortie :
Décision recommandée :
Risque résiduel et autorité d'acceptation :
Prochain point / responsables / échéances :
~~~

## 20. TP 2 guidé : revue d'un fournisseur SaaS de gestion des incidents

### Situation

Une entreprise utilise un service SaaS pour gérer les tickets. Le fournisseur promet une disponibilité mensuelle de 99,9 %, une première réponse sous une heure pour les incidents critiques et un export des données « disponible sur demande ». Le service contient les noms d'utilisateurs, des descriptions d'incidents, des fragments de journaux parfois sensibles et des historiques de changements. Le fournisseur utilise un sous-traitant d'hébergement et un service tiers d'envoi de courriels. Les rapports du fournisseur indiquent 99,96 % de disponibilité le mois dernier, mais plusieurs utilisateurs ont rapporté des échecs de connexion. Le contrat arrive à échéance dans quatre mois.

### Travail demandé

1. Identifie les informations que tu dois obtenir avant de conclure sur le SLA.
2. Définis au moins six contrôles pour la due diligence sécurité.
3. Propose un plan de vérification de l'export et de la réversibilité.
4. Prépare une liste de questions pour la revue contractuelle.
5. Formule une recommandation conditionnelle de renouvellement.

### Correction détaillée

Pour le SLA, clarifie si l'indicateur porte sur l'interface web, l'API, l'authentification, la création et la lecture d'un ticket ou l'ensemble du service. Vérifie la fenêtre de mesure, les exclusions, la zone, la méthode de calcul, les fenêtres de maintenance et la façon dont les erreurs de connexion sont enregistrées. Compare le rapport du fournisseur aux observations client, aux horaires, aux tickets et aux éventuels journaux disponibles. Le chiffre de 99,96 % peut être correct pour le composant mesuré tout en ne reflétant pas l'expérience de tous les utilisateurs.

Pour la sécurité, examine les comptes privilégiés et la MFA, la révocation des accès de support, la protection des données, la journalisation, la notification d'incident, les vulnérabilités, la sous-traitance, la restauration et la gestion des changements. Vérifie les preuves et la portée des rapports, pas uniquement les réponses du questionnaire. Évalue si des journaux sensibles sont envoyés par courriel, qui peut les consulter et comment les accès sont tracés.

Pour l'export, demande un schéma de données, les formats, les pièces jointes, les horodatages, les commentaires, les relations entre tickets, les champs personnalisés, les pièces de configuration et les limites de taille. Exécute un export de test autorisé, importe-le dans une cible de validation et compare les comptes, volumes, relations et empreintes des fichiers. Chronomètre les étapes et relève les éléments manquants. N'attends pas l'expiration du contrat pour découvrir que les historiques de changements ne sont pas exportables.

Pour le contrat, clarifie la définition du SLA, les seuils et escalades, le délai de notification d'incident, les engagements de sous-traitance, les lieux de traitement, l'accès aux preuves, le droit de vérifier les contrôles, les coûts de sortie, la durée de disponibilité de l'export, la suppression et les obligations de coopération. Les personnes habilitées valident les clauses et toute exigence juridique applicable.

La recommandation peut être : renouveler uniquement si les écarts de mesure sont clarifiés, si les contrôles de sécurité prioritaires sont démontrés, si l'export représentatif réussit et si un plan d'action daté est approuvé pour les lacunes restantes. À défaut, limiter le renouvellement à une période courte ou préparer une solution alternative selon les décisions et pouvoirs de l'organisation. Le score global ne doit pas effacer une réversibilité non démontrée.

## 21. Checklist de revue fournisseur

### Gouvernance et contrat
- [ ] Propriétaire métier et responsable de relation nommés.
- [ ] Criticité, périmètre, données et dépendances décrits.
- [ ] Contrat, annexes, SLA et sous-traitants identifiés.
- [ ] Décideurs, escalades et acceptation du risque définis.
- [ ] Date de renouvellement et préavis connus.

### Performance et qualité
- [ ] KPI définis avec formule, source, période et exclusions.
- [ ] Incidents comparés aux mesures internes.
- [ ] Temps de réponse, de restauration et de résolution séparés.
- [ ] Actions précédentes contrôlées.
- [ ] Répétitions, tendance et impact métier analysés.

### Sécurité et chaîne d'approvisionnement
- [ ] Accès, privilèges et révocation vérifiés.
- [ ] Données, journaux, lieux de traitement et responsabilités compris.
- [ ] Sous-traitants et dépendances critiques cartographiés.
- [ ] Notification d'incident et coopération définies.
- [ ] Preuves de continuité et de restauration examinées.
- [ ] Périmètre et limites des rapports ou certifications compris.

### Coût, continuité et sortie
- [ ] Coût total de possession estimé sur un périmètre cohérent.
- [ ] Changements de prix et options explicités.
- [ ] Dépendances propriétaires et alternatives connues.
- [ ] Export et réversibilité documentés et testés selon le risque.
- [ ] Suppression, restitution et révocation des accès planifiées.

### Décision et suivi
- [ ] Constat lié à une preuve et un critère.
- [ ] Risque résiduel clairement décrit.
- [ ] Actions assignées à un responsable et une échéance.
- [ ] Critères de clôture et d'efficacité définis.
- [ ] Décision de renouvellement, renégociation ou sortie consignée.
- [ ] Le risque restant est accepté par la personne habilitée, si nécessaire.


## 22. Exercices corrigés

### Exercice 1 — SLA conforme, service insatisfaisant

Le fournisseur respecte les délais de réponse, mais les interruptions restent longues. Quelle analyse faut-il faire ?

**Correction.** Sépare réponse, restauration et résolution. Vérifie les définitions contractuelles, la période de calcul, les exclusions et les données internes. Si le SLA n'exige qu'une réponse rapide, l'indicateur ne mesure pas la restauration. Propose une mesure adaptée à l'impact métier et engage la révision contractuelle via les personnes compétentes.

### Exercice 2 — Score global élevé, risque critique

Un fournisseur obtient 92/100 mais ne peut pas démontrer la révocation des accès d'un sous-traitant. Peut-on le déclarer acceptable ?

**Correction.** Pas automatiquement. Définis la lacune comme un point bloquant ou un risque explicitement accepté par l'autorité prévue. Demande la preuve de révocation, limite les accès si c'est autorisé et vérifie la chaîne de sous-traitance. Un score moyen ne remplace pas les seuils critiques.

### Exercice 3 — Absence de plan de sortie

Le fournisseur affirme qu'un export de données « sera possible ». Quelles preuves demander ?

**Correction.** Le format et le périmètre des données, les délais, les coûts, les dépendances de licences, les procédures, les contrôles d'intégrité, les accès pendant la transition, l'effacement et les tests. Pour les dépendances critiques, organise un exercice de transfert dans un environnement de test autorisé.

## 23. Défi final corrigé

**Mission.** Tu dois présenter à un comité de service la revue annuelle de trois fournisseurs : un hébergeur critique, un prestataire de support et un service d'inventaire.

**Correction type.** Segmente les fournisseurs par criticité et dépendance. Définis des indicateurs correspondant à chaque service et des critères bloquants de sécurité. Réconcilie les mesures, documente les preuves et les exclusions, examine les incidents et les tendances, puis classe les actions selon le risque. Pour l'hébergeur, valide la continuité et la sortie ; pour le support, vérifie la qualité d'escalade et de résolution ; pour l'inventaire, vérifie la qualité des données et la gestion des accès. Chaque décision de renouvellement doit expliciter le risque restant et l'autorité qui l'accepte.

## 24. Références et approfondissement

Les ressources officielles ci-dessous permettent d'approfondir les pratiques de gestion des risques fournisseur. Elles constituent des guides ou des normes de référence, et ne deviennent pas automatiquement des obligations contractuelles ou légales pour chaque organisation. Choisis les exigences qui correspondent au périmètre, à la juridiction, au service acheté et au niveau de risque.

- [NIST SP 800-161 Rev. 1, Update 1 — Cybersecurity Supply Chain Risk Management Practices for Systems and Organizations](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) — guide de gestion des risques cyber tout au long de la chaîne d'approvisionnement, avec une approche intégrée aux pratiques de gestion des risques.
- [NIST SP 1305 — Cybersecurity Framework 2.0: Quick-Start Guide for Cybersecurity Supply Chain Risk Management](https://csrc.nist.gov/pubs/sp/1305/final) — guide pratique pour établir une capacité C-SCRM et communiquer les exigences aux fournisseurs à l'aide du CSF 2.0, notamment sa catégorie GV.SC.
- [NIST Cyber Supply Chain Risk Management](https://csrc.nist.gov/Projects/Cyber-Supply-Chain-Risk-Management) — ressources et pratiques relatives à la gestion des dépendances et des risques fournisseurs.
- [ISO/IEC 27036-2:2022 — Cybersecurity: Supplier relationships, Part 2: Requirements](https://www.iso.org/standard/82060.html) — exigences relatives à la définition, l'exploitation, la surveillance, la revue et l'amélioration des relations entre fournisseur et acquéreur.
- [ISO/IEC 27036-3:2023 — Guidelines for hardware, software, and services supply chain security](https://www.iso.org/standard/82890.html) — lignes directrices sur la visibilité et la sécurité des chaînes d'approvisionnement multicouches en matériel, logiciel et services.
- [CISA — ICT Supply Chain Risk Management Essentials](https://www.cisa.gov/sites/default/files/2023-01/ict_scrm_essentials_508.pdf) — actions pratiques pour identifier, comprendre, évaluer, vérifier et suivre les fournisseurs, prestataires et composants.
- Les clauses contractuelles définitives doivent être validées par les équipes juridiques, sécurité, achats et responsables métier de l'organisation.

## 25. Conclusion

Le pilotage expert d'un fournisseur repose sur une relation vérifiable : objectifs clairement définis, responsabilités partagées, exigences contractuelles mesurables, preuves suffisantes, risques proportionnés, décisions explicites et actions suivies jusqu'à l'efficacité. Il ne consiste ni à faire confiance aveuglément à un score fourni par le prestataire, ni à traiter chaque fournisseur comme une menace. Il consiste à adapter les contrôles à la dépendance réelle et à organiser la relation de manière à préserver le service, la sécurité, la valeur et la capacité de choix de l'organisation.

La règle à retenir est simple : **ce qui est important doit être défini, mesuré, prouvé, attribué et suivi**. Un bon fournisseur ne se juge pas uniquement à la signature ou au tarif initial. La qualité de la relation se démontre dans la durée, notamment lorsque surviennent une dégradation, un incident, un changement de sous-traitant ou une sortie.