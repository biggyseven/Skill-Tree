# Gestion des fournisseurs

> **Mise en contexte — Pilotage de la relation fournisseur** : La gestion des fournisseurs ne s'arrête ni à la sélection ni à la signature du contrat. Elle couvre la performance, le risque, les changements, la qualité, la sécurité, la continuité, l'évolution des coûts et la sortie. L'expert organise une relation mesurable dans laquelle les responsabilités restent claires, les promesses sont vérifiées et les écarts conduisent à des décisions documentées. Un fournisseur peut être techniquement compétent tout en présentant des risques élevés de concentration, de dépendance, de sous-traitance opaque ou d'indisponibilité. Inversement, une baisse ponctuelle d'un SLA peut être causée par une dépendance interne ou une mesure mal définie. Il faut analyser la performance en contexte, sans accepter les déclarations commerciales comme substitut aux preuves ni attribuer automatiquement chaque incident au fournisseur.

## Objectifs pédagogiques

À l'issue du cours, l'apprenant sera capable de :

- segmenter le portefeuille selon la criticité et la dépendance
- construire une gouvernance de contrat et une revue de performance
- mesurer les SLA et examiner la qualité des preuves
- gérer les risques financiers, opérationnels, cyber et de continuité
- conduire des plans d'amélioration et des escalades contractuelles
- préparer la réversibilité et la fin de contrat

## Prérequis et cadre de responsabilité

Le parcours s'adresse à un professionnel capable de lire les procédures, les tickets et les indicateurs du service concerné. Les décisions qui affectent la production, les personnes, les données, les finances ou les contrats doivent respecter les seuils d'autorisation de l'organisation. Les exemples du cours sont pédagogiques : adapter les cibles, les rôles et les obligations à l'environnement, au pays, au secteur et aux engagements effectivement applicables. Ne jamais remplacer une validation juridique, de sécurité, financière ou opérationnelle exigée par une hypothèse ou un exemple générique.

Avant une action importante, préciser le besoin, la portée, la personne qui décide, la preuve attendue, les risques, les conditions d'arrêt et la procédure de remontée. Si une donnée importante manque ou qu'une dépendance n'est pas confirmée, rendre cette incertitude visible et faire valider la suite par la personne habilitée.

## Vocabulaire de référence

| Terme | Définition |
|---|---|
| Fournisseur critique | Partenaire dont la défaillance peut affecter significativement les services ou les obligations de l'organisation. |
| SLA | Engagement de service mesuré selon une période, une formule et des règles définies. |
| OLA | Accord opérationnel entre équipes internes qui contribue à un service de bout en bout. |
| KPI fournisseur | Mesure de performance qui permet une décision contractuelle ou opérationnelle. |
| Risque de concentration | Dépendance à un fournisseur, une technologie, une région ou un sous-traitant commun. |
| Plan d'amélioration | Actions, responsables, échéances et tests destinés à corriger une performance ou un risque. |
| Réversibilité | Transfert planifié du service, des données, des configurations et des responsabilités à un nouveau modèle. |
| Due diligence | Vérification proportionnée des capacités, finances, contrôles et risques avant ou pendant la relation. |

## Schémas de référence

### Schéma 1 — Objectifs et activation

~~~mermaid
flowchart LR
  A[Propriétaire service] --> D[Revue fournisseur]
  B[Achats et contrat] --> D
  C[Sécurité et risque] --> D
  D --> E[Décisions consignées]
~~~

Gouvernance fournisseur : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 2 — Rôles et décisions

~~~mermaid
flowchart TD
  A[Définition SLA/KPI] --> B[Source de référence]
  B --> C[Calcul reproductible]
  C --> D[Contrôle d'échantillon]
  D --> E[Revue contradictoire]
  E --> F[Actions]
~~~

Scorecard fiable : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 3 — Cartographie des dépendances

~~~mermaid
flowchart TD
  A[Fournisseur et service] --> B[Criticité]
  B --> C[Concentration et sous-traitants]
  C --> D[Contrôles existants]
  D --> E[Risque résiduel]
  E --> F[Plan de mitigation]
~~~

Registre de risque : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 4 — Cycle de traitement

~~~mermaid
flowchart TD
  A[Écart confirmé] --> B[Impact et SLA]
  B --> C[Mitigation immédiate]
  C --> D[Revue fournisseur]
  D --> E{Amélioration démontrée ?}
  E -->|Non| F[Escalade contractuelle]
~~~

Escalade : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 5 — Escalade et information

~~~mermaid
flowchart LR
  A[Périmètre de preuve] --> B[Entité et services]
  B --> C[Période et exclusions]
  C --> D[Écarts et plans]
  D --> E[Décision de risque]
~~~

Due diligence : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 6 — Validation du résultat

~~~mermaid
flowchart LR
  A[Temps de prise en charge] --> D[Résultat de bout en bout]
  B[Temps de résolution] --> D
  C[Réouverture et qualité] --> D
  D --> E[Analyse des causes]
~~~

Revue des SLA : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 7 — Mesure et gouvernance

~~~mermaid
flowchart TD
  A[Fournisseur principal] --> B[Sous-traitant]
  B --> C[Accès et données]
  C --> D[Obligations et contrôle]
  D --> E[Notification et décision]
~~~

Sous-traitance : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 8 — Traitement des écarts

~~~mermaid
flowchart TD
  A[Cause et preuve] --> B[Action testable]
  B --> C[Owner et échéance]
  C --> D[Preuve d'implémentation]
  D --> E[Test d'efficacité]
~~~

Plan d'amélioration : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 9 — Amélioration continue

~~~mermaid
flowchart LR
  A[Performance] --> D[Analyse de renouvellement]
  B[Coût complet] --> D
  C[Risque et marché] --> D
  D --> E[Renouveler, améliorer ou sortir]
~~~

Décision renouvellement : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 10 — Sortie et retour d'expérience

~~~mermaid
flowchart TD
  A[Plan de sortie activé] --> B[Transférer le savoir]
  B --> C[Exporter et valider les données]
  C --> D[Tester le service entrant]
  D --> E[Révoquer les accès]
  E --> F[Clôture prouvée]
~~~

Sortie de fournisseur : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

## 1. Segmenter le portefeuille et définir la gouvernance

Tous les fournisseurs ne nécessitent pas le même effort de gestion. Classer les partenaires selon la criticité des services, l'accès aux données, le pouvoir de remplacement, la concentration, le coût, les dépendances et les conséquences d'une interruption. Un fournisseur peu coûteux peut être critique s'il détient une compétence unique ou un accès privilégié ; une offre chère mais facilement substituable peut présenter un risque différent. La segmentation doit guider la fréquence de revue, le niveau d'assurance et les plans de sortie.

Pour chaque fournisseur critique, établir une fiche de relation : services, contrat, renouvellement, contacts, sous-traitants, sites, systèmes, données, accès, SLA, risques, plans d'amélioration, incidents, assurances ou attestations pertinentes et dépendances internes. Le propriétaire de service reste responsable du besoin et des résultats opérationnels ; les achats gèrent les processus commerciaux ; le juridique interprète les clauses ; la sécurité évalue les risques de contrôle. La matrice RACI clarifie les décisions communes.

La gouvernance comprend une revue opérationnelle régulière, une revue stratégique et un processus d'escalade. La première traite tickets, délais et problèmes courants ; la seconde examine capacité, coûts, innovations, risques, contrat et évolution de besoin. Une revue stratégique sans données fiables devient un échange de présentations ; une revue opérationnelle sans décisions sur les risques laisse les problèmes structurels s'accumuler.

La relation doit fonctionner même si le gestionnaire de contrat est absent. Conserver les décisions, les engagements, les écarts et les contacts dans un référentiel contrôlé. Éviter que la seule preuve d'un accord soit un message privé. Les décisions qui modifient prix, périmètre, responsabilité ou sécurité doivent suivre l'autorisation prévue et être intégrées au contrat ou au registre de changement.

## 2. Mesurer la performance réellement utile

Les KPI doivent refléter les résultats attendus du service, pas seulement ce que le fournisseur sait exporter. Les dimensions peuvent inclure disponibilité, résolution dans les délais, respect des fenêtres de maintenance, taux de réouverture, qualité des livrables, défauts après changement, sécurité, satisfaction, capacité, transparence et coût. Chacun a une définition, une source, un dénominateur, une période, les exclusions et un propriétaire. Quand un même indicateur existe dans plusieurs outils, définir la source de référence.

Le SLA mesure une obligation contractuelle, alors qu'un KPI de pilotage peut détecter une tendance sans constituer une obligation. Ne pas appliquer automatiquement une pénalité à un indicateur qui n'a pas été contractualisé. Réciproquement, ne pas remplacer une mesure contractuelle par un indicateur plus favorable après une période difficile. Toute modification de méthode doit être gouvernée et appliquée de façon cohérente.

Les mesures doivent refléter l'expérience de bout en bout. Un fournisseur peut respecter son temps de prise en charge tout en laissant le service indisponible pendant des heures à cause d'une attente de pièces ou d'une escalade. Distinguer ses étapes de celles qui dépendent de l'organisation tout en conservant la mesure globale du service. L'objectif n'est pas de déplacer le blâme, mais d'identifier où la chaîne perd du temps et quelle partie peut agir.

Les revues doivent examiner les distributions et les cas extrêmes, pas seulement les moyennes. Une moyenne satisfaisante peut cacher une série d'incidents critiques ou des tickets laissés ouverts hors du calcul. Demander des éléments sources sur un échantillon, examiner les changements de classification et comparer les résultats avec la supervision ou les dossiers internes. La confiance dans un KPI dépend de sa reproductibilité.

## 3. Maîtriser les risques du fournisseur

Les risques financiers comprennent la capacité à poursuivre l'activité, la concentration des revenus, l'évolution des coûts et les dépendances de financement. Les risques opérationnels incluent les compétences rares, la sous-traitance, la capacité de support, les pièces, les sites, les délais d'approvisionnement et la continuité. Les risques cyber et de données concernent accès, comptes privilégiés, connectivité, journaux, incident, notification, sous-traitants, localisation et restitution. Adapter la profondeur de contrôle à la criticité et au contexte contractuel.

Vérifier les attestations et rapports indépendants selon leur portée et période. Une certification d'une entité ou d'un produit ne prouve pas automatiquement que toutes les prestations, régions et sous-traitants sont inclus. Les exceptions, limites, opinions, périodes couvertes et changements depuis le rapport doivent être examinés. Si les preuves directes ne sont pas accessibles, chercher des contrôles compensatoires et documenter ce qui ne peut pas être confirmé.

Le risque de concentration peut exister au-delà du fournisseur direct : deux prestataires différents peuvent utiliser le même hébergeur, opérateur de télécommunications, chaîne logistique ou service d'identité. Cartographier les dépendances communes pour comprendre les scénarios de panne corrélée. Les plans de continuité doivent prévoir des alternatives réalistes, notamment les ressources, habilitations, licences et formats nécessaires pour poursuivre le service.

Les changements de fournisseur sont des moments sensibles. Un changement d'actionnaire, de sous-traitant, de localisation, d'équipe, d'architecture, de modèle de prix ou de version peut modifier le profil de risque. Le contrat doit préciser les notifications requises et les droits de revue. Évaluer le changement avant de l'accepter et vérifier après sa mise en œuvre que les contrôles restent efficaces.

## 4. Gérer écarts, incidents et amélioration

Un écart significatif doit faire l'objet d'un dossier qui précise l'engagement concerné, les faits, la source, l'impact, les responsabilités à confirmer et la mesure de mitigation. Le fournisseur doit pouvoir répondre et apporter des preuves ; cette réponse est évaluée, pas automatiquement acceptée ni rejetée. Les discussions commerciales se séparent autant que possible de l'urgence opérationnelle afin que la restauration du service ne soit pas bloquée par la négociation d'un litige.

Le plan d'amélioration doit définir le résultat attendu, la cause, les actions, les propriétaires, les échéances, les dépendances, les preuves et le test d'efficacité. « Améliorer la communication » ne suffit pas ; préciser le canal, l'heure, le contenu et les critères de bonne exécution. Mesurer si les actions réduisent le risque et non seulement si des réunions ont été tenues. En cas de récidive, réexaminer la cause, la capacité et les incitations.

L'escalade doit suivre le contrat et la gravité. Définir les niveaux, les décideurs, les délais, les informations nécessaires, le mécanisme de résolution de désaccord et les mesures conservatoires. Une escalade n'est pas un substitut à des faits précis. Conserver une chronologie pour distinguer les retards attribuables, les dépendances internes, les attentes fournisseurs et les décisions qui ont prolongé la résolution.

Lorsque la performance ne s'améliore pas, les options peuvent comprendre une révision du plan, une mitigation, une mise en demeure selon le contrat, l'activation de droits de contrôle ou la préparation d'une sortie. Ces décisions doivent être prises par les personnes habilitées et conseillées par le juridique si nécessaire. La fin de contrat n'est pas toujours immédiate ni économiquement réaliste ; la dépendance doit être réduite dès que le risque est identifié.

## 5. Préparer renouvellement et sortie

Le renouvellement doit être décidé avant l'échéance contractuelle avec une analyse des performances, du coût complet, de la capacité interne, du marché, des risques, des changements de besoin et de la réversibilité. Renouveler par inertie peut prolonger une dépendance coûteuse. Changer pour un prix inférieur sans plan de transition peut aussi augmenter le risque et le coût de sortie.

La réversibilité précise les données, configurations, inventaires, dossiers, historiques, licences, scripts, documentation, connaissances et accès qui doivent être transférés. Définir formats, délais, responsabilités, validation d'intégrité, confidentialité, suppression des copies et assistance du fournisseur sortant. Ces exigences doivent être prévues au contrat de départ ; demander une exportation complète lorsque le contrat se termine peut être tardif ou coûteux.

Le plan de transition inclut coexistence, transfert des incidents ouverts, tests d'accès, calendrier de migration, critères de passage, coordination des sous-traitants et possibilité de retour arrière. Vérifier la continuité des services, pas uniquement la livraison de fichiers. La fermeture du contrat doit inclure la révocation des accès, la restitution ou suppression des données, le règlement des obligations, les preuves de fin de service et la conservation des traces requises.

Une revue après sortie permet de mesurer les coûts réels, les écarts entre plan et expérience, les enseignements et les clauses à améliorer. Les données de cette revue alimentent les consultations suivantes. Sans retour structuré, les mêmes ambiguïtés commerciales et opérationnelles se retrouvent dans le prochain contrat.

## Méthode opérationnelle — du diagnostic à la décision

Une démarche experte suit un enchaînement traçable. Commencer par formuler la question à résoudre et le résultat attendu, puis identifier les sources de données, les personnes concernées, les contraintes et les risques. Construire un état initial avant d'agir : période, périmètre, dépendances, règles en vigueur et qualité des données. Énoncer les hypothèses de façon à pouvoir les confirmer ou les rejeter. Préférer des contrôles qui distinguent réellement les causes possibles plutôt qu'une accumulation de vérifications sans lien avec la décision.

Avant toute décision à impact, examiner les options et les conséquences, y compris l'option de ne pas agir immédiatement. Pour chaque option, documenter bénéfices, risques, coût, dépendances, réversibilité et conditions de réussite. Choisir une action proportionnée et approuvée, assigner un responsable et une échéance, puis mesurer le résultat avec le même critère que celui défini au départ. Si une hypothèse importante est invalidée, interrompre le scénario prévu et requalifier la situation plutôt que continuer mécaniquement.

La preuve doit permettre à un collègue indépendant de comprendre ce qui a été décidé, pourquoi et à partir de quelles informations. Distinguer fait observé, déclaration, estimation, hypothèse et décision. Conserver les exceptions et résultats contradictoires qui modifient l'interprétation. Lorsque le niveau de confiance reste insuffisant, réduire la portée de la conclusion, expliquer la limitation et préciser le contrôle suivant qui permettrait de progresser.

## Mesure, gouvernance et amélioration

Chaque indicateur de pilotage doit avoir un objectif, une formule ou une méthode, une source, une période, un propriétaire, des limites et une décision associée. Un chiffre sans dénominateur, définition ou état de fraîcheur est difficile à interpréter. Contrôler la couverture de la population, les valeurs manquantes, les doublons, les changements de définition et les exclusions. Les résultats d'une action doivent être comparés à une référence crédible, avec les changements simultanés et les effets secondaires identifiés.

Ne pas optimiser un indicateur isolé au détriment du service. Une baisse de délai peut cacher des clôtures prématurées ; un gain de prix peut créer un coût de sortie très élevé ; une reprise technique peut rester inutilisable pour le métier ; une réduction d'effectifs peut concentrer une compétence critique. Associer les mesures de résultat à des indicateurs de qualité, de risque, de charge et de durabilité afin de vérifier que l'amélioration est réelle.

La gouvernance exige des responsabilités explicites. Pour chaque décision significative, noter qui propose, qui examine, qui approuve, qui exécute et qui vérifie. Une revue doit se terminer par des décisions suivies, pas uniquement par un compte rendu. Les actions comportent un propriétaire, une échéance, une preuve de réalisation et un critère d'efficacité. En cas de retard, faire apparaître le risque et demander une décision explicite sur les mesures temporaires.

## Atelier pratique — revue trimestrielle d'un fournisseur critique

### Situation de départ

Un fournisseur assure la maintenance d'une plateforme critique. Les incidents respectent en moyenne le délai d'accusé de réception mais le délai de rétablissement s'allonge, trois actions sont en retard et un sous-traitant a changé de région sans dossier central complet. Le contrat arrive à renouvellement dans six mois. L'équipe doit établir le risque et un plan de décision sans confondre les engagements contractuels avec les indicateurs de pilotage.

### Phase A — Reconstituer le contrat

Identifier le périmètre, SLA, exclusions, obligations de notification, droits d'audit, sous-traitance et sortie. Déterminer les clauses applicables au changement de région et aux actions en retard ; faire valider les interprétations contractuelles par la fonction compétente.

### Phase B — Valider les mesures

Comparer les KPI fournis avec les incidents sources, la période et les règles de calcul. Segmenter prise en charge, réparation, attente et rétablissement ; identifier les données manquantes et les incidents extrêmes.

### Phase C — Évaluer le risque

Examiner la criticité, la concentration, le changement de sous-traitant, la continuité, les accès et l'effet du retard des actions. Définir les contrôles compensatoires et l'escalade appropriée.

### Phase D — Plan d'amélioration

Attribuer les trois actions en retard, définir leurs preuves, dates et tests d'efficacité, et fixer une cadence de revue. Séparer les actions sous responsabilité fournisseur de celles qui dépendent de l'acheteur.

### Phase E — Décision de renouvellement

Comparer prolongation, remédiation, appel d'offres et transition. Calculer les coûts, risques, délais et conditions de sortie. Documenter les décisions et les validations requises.

### Critères de réussite

Le livrable de l'atelier doit être reproductible, lié à des critères explicites et suffisamment clair pour être repris par une autre équipe. Les décisions non confirmées doivent rester présentées comme hypothèses. Toute action comporte ses conditions d'application, les risques, les validations nécessaires et une preuve du résultat. Le succès ne se déduit pas d'une présentation convaincante ou d'une case cochée : il se démontre avec des résultats et une revue indépendante adaptée au risque.

## Études de cas

### Cas 1 — Rapport fournisseur non reproductible

Le tableau indique 99,9 % de disponibilité sans fournir le temps de service attendu ni les exclusions. Exiger la définition, les sources et le rapprochement avec le contrat avant de calculer les conséquences.

### Cas 2 — Sous-traitant non déclaré

Le fournisseur change un acteur qui traite des données sensibles. Vérifier les obligations de notification, la localisation, les contrôles et les droits de l'organisation, sans supposer automatiquement la même couverture contractuelle.

### Cas 3 — Renouvellement trop tardif

Les achats commencent la consultation deux semaines avant l'échéance. La dépendance peut rendre le changement irréaliste ; établir à l'avance le calendrier, les décisions et les options de continuité.

## Exercices d'application avec corrigés

### Exercice 1 — Définir le critère

**Question.** Pourquoi segmenter les fournisseurs ?

**Corrigé expliqué.** Parce que la criticité, la substituabilité, l'accès aux données et le risque de concentration varient. Le niveau de diligence et la cadence de revue doivent être proportionnés à ces facteurs.

### Exercice 2 — Interpréter les preuves

**Question.** Un SLA est respecté mais le service reste insatisfaisant. Que vérifier ?

**Corrigé expliqué.** Mesurer le parcours de bout en bout, les exclusions, les OLA internes et les indicateurs de résultat ; vérifier que le SLA contractualisé couvre le besoin réellement critique.

### Exercice 3 — Choisir une action

**Question.** Quelle preuve suffit à démontrer l'efficacité d'un plan d'action ?

**Corrigé expliqué.** Un résultat observé répondant à un critère prédéfini, contrôlé sur les données pertinentes ; la fermeture du ticket seule n'est pas suffisante.

### Exercice 4 — Traiter une dépendance

**Question.** Un certificat fournisseur couvre-t-il automatiquement le service acheté ?

**Corrigé expliqué.** Non. Vérifier l'entité, les sites, les services, la période, les exclusions et les sous-traitants compris dans la portée.

### Exercice 5 — Évaluer un écart

**Question.** Que doit couvrir la réversibilité ?

**Corrigé expliqué.** Données, configurations, documents, historiques, accès, formats, assistance, délais, coûts, validation d'intégrité et suppression ou restitution en fin de contrat.

### Exercice 6 — Vérifier l'efficacité

**Question.** Comment traiter un désaccord sur l'attribution d'un incident ?

**Corrigé expliqué.** Établir une chronologie commune, rapprocher les preuves, identifier les dépendances et responsabilités sans déplacer arbitrairement le blâme, puis appliquer la voie d'escalade contractuelle.

## Défi final — mise en situation experte

Élaborer un dossier de gouvernance d'un fournisseur de maintenance critique sur douze mois : segmentation, registre de risques, tableau de bord SLA/KPI, calendrier de revue, plan d'amélioration, procédure d'escalade, due diligence annuelle, scénario de défaillance du fournisseur et plan de sortie. Le corrigé doit distinguer faits, risques et interprétations contractuelles, expliquer comment les données sont vérifiées et démontrer que la relation peut être pilotée même lorsqu'un indicateur est contesté.

**Livrable attendu.** Produire un dossier professionnel réutilisable par une équipe qui n'a pas participé à l'exercice. Il doit inclure le contexte, le périmètre, les objectifs, les critères, les données utilisées, les rôles, les décisions, les risques, les limites, les résultats et le plan de suivi. Justifier les choix en reliant chacun d'eux à une preuve ou à une hypothèse explicitement marquée. Décrire comment vérifier l'efficacité de la réponse et ce qui déclencherait une révision de la décision.

**Correction attendue.** Une solution experte ne se contente pas de choisir une option ; elle compare les scénarios, fixe les critères avant le résultat, documente les responsabilités et signale les informations manquantes. Elle prévoit les conditions d'arrêt, les mesures temporaires, la communication, les dépendances et la vérification de fin. Le plan d'action est réaliste, ses résultats sont mesurables et le risque résiduel est soumis à une personne habilitée.


## Scorecard fournisseur, registre de risques et revue trimestrielle

Le pilotage fournisseur nécessite un jeu cohérent de données et une méthode de revue. La scorecard doit associer engagements contractuels et indicateurs de pilotage, sans attribuer automatiquement une pénalité à une mesure non contractualisée. Les chiffres sont préparés avant la réunion, rapprochés avec les sources et présentés avec les exceptions ; la réunion est consacrée aux causes, arbitrages, risques et actions plutôt qu'à la lecture des tableaux.

### Modèle de scorecard

| Domaine | Mesure possible | Source de vérification | Décision associée |
|---|---|---|---|
| Service | Disponibilité définie par le contrat | Supervision et méthode de calcul validée | Plan de remédiation, crédit ou revue selon le contrat |
| Résolution | Temps par classe de criticité et percentiles | Tickets et chronologie rapprochés | Analyse des goulots et ressources |
| Qualité | Taux de réouverture et incidents récurrents | Tickets et échantillon de clôtures | Revoir la validation et les actions |
| Changements | Changements réussis, incidents post-déploiement, preuves de test | Registre de changement et systèmes | Renforcer la recette ou le contrôle |
| Sécurité | Actions en retard, accès revus, incidents notifiés selon les obligations applicables | Registre sécurité et preuves autorisées | Escalade, mitigation et revue de risque |
| Continuité | Tests, dépendances, capacité et résultats de reprise | Exercices et comptes rendus | Exiger une preuve ou corriger le PRA |
| Commercial | TCO, consommation, écarts de facturation, indexation | Contrat, factures et volumes | Corriger la facture ou arbitrer un changement |
| Collaboration | Délais de réponse, qualité des livrables et stabilité des interlocuteurs | Registre de demandes et retours validés | Plan de service et transfert de connaissances |

La scorecard doit éviter un score unique qui cache un risque critique. Un résultat global vert ne compense pas automatiquement une notification de sécurité manquante ou un test de continuité jamais réalisé. Afficher les seuils contractuels, les objectifs internes et les limites de couverture dans des colonnes distinctes. Les exceptions et les données non disponibles sont visibles au même titre que les résultats.

### Registre de risques fournisseur

Pour chaque risque, consigner le scénario, le service et les données concernés, les causes possibles, la probabilité, l'impact, les contrôles existants, les preuves, le risque résiduel, les mesures, le propriétaire et la prochaine revue. Évaluer les risques directs et les dépendances communes : fournisseurs cloud, opérateurs télécoms, fabricants, sous-traitants et services d'identité. La défaillance d'un fournisseur primaire peut être aggravée par un sous-traitant utilisé par plusieurs partenaires.

Ne pas traiter une attestation ou certification comme une preuve universelle. Vérifier la portée, la période, les services, les sites, les exceptions, les sous-traitants et les changements depuis la date de la preuve. Si un fournisseur ne donne pas accès à certaines informations sensibles, convenir de modalités de contrôle raisonnables ou documenter la limitation ; l'absence de visibilité doit entrer dans le risque résiduel.

### Agenda d'une revue trimestrielle

1. Confirmer le périmètre et les modifications depuis la revue précédente.
2. Examiner les SLA/KPI, leur qualité de données, les exceptions et les écarts.
3. Revoir les incidents majeurs, les récidives et les changements ayant eu un effet sur le service.
4. Vérifier les actions, les échéances, les preuves d'implémentation et les tests d'efficacité.
5. Examiner les risques de sous-traitance, de continuité, de sécurité, de concentration et de coût.
6. Décider des actions, de l'escalade, des mesures temporaires et des responsabilités.
7. Revoir les évolutions de contrat, les capacités futures, les coûts et la date de renouvellement.
8. Confirmer le compte rendu, le propriétaire de chaque action et le prochain point de contrôle.

### Exemple de décision en cas de performance dégradée

Un fournisseur respecte 98 % des délais d'accusé de réception, mais le temps de rétablissement des services critiques augmente depuis deux trimestres. Une conclusion « fournisseur performant » tirée du seul accusé de réception serait incomplète. Il faut segmenter le parcours entre détection, prise en charge, diagnostic, attente de pièce, action et validation. Si le fournisseur attend l'accès ou une approbation interne, une action conjointe est nécessaire ; si les délais de pièce sont sous sa responsabilité, le plan devra contenir des mesures de stock, de logistique ou de substitution.

Le plan d'amélioration doit fixer une période de mesure, une population comparable, les sources, les actions de chaque partie et le critère d'efficacité. Les engagements de résultat qui ne figurent pas au contrat peuvent servir d'objectif de travail, mais les conséquences contractuelles s'appliquent uniquement selon les clauses et règles valides. Le but est d'améliorer le service et d'établir une décision défendable avant le renouvellement.



## Gestion des situations difficiles et du renouvellement

Une relation fournisseur critique peut traverser une dégradation progressive, un incident majeur, un changement de propriétaire, une crise financière, un conflit de mesure ou une transition accélérée. L'expert doit préparer ces scénarios en amont et différencier la mitigation immédiate, les obligations contractuelles, les négociations commerciales et la décision de dépendre ou non du partenaire à moyen terme.

### Escalader sans perdre la maîtrise opérationnelle

L'escalade est déclenchée par des conditions définies : violation d'un engagement, risque élevé, répétition d'un défaut, délai d'action dépassé, changement non notifié ou absence de preuve sur un contrôle critique. Le dossier d'escalade contient la chronologie, le service affecté, les données mesurées, le critère concerné, l'impact, les mesures déjà prises, la décision attendue et l'échéance. Éviter les messages accusatoires ou les qualificatifs non démontrés ; un dossier factuel est plus utile à la résolution comme à la gestion contractuelle.

La mitigation doit être décidée avant que l'analyse commerciale soit terminée lorsque le service est en danger. Par exemple, une capacité de secours peut être activée selon le plan autorisé pendant que les parties reconstituent la cause. Les frais ou responsabilités peuvent être examinés ensuite conformément au contrat. Cela n'autorise pas l'équipe à ignorer les droits contractuels, mais évite qu'un débat sur la faute retarde une action nécessaire pour réduire l'impact.

### Tableau de décision de renouvellement

| Question | Preuve nécessaire | Option possible si la réponse est défavorable |
|---|---|---|
| Le service atteint-il les objectifs ? | KPI vérifiés, dossiers d'exception et retours métier | Plan de remédiation avec jalons |
| Le coût reste-t-il justifié ? | TCO, consommation, prix futurs et coûts d'évolution | Renégociation ou nouvelle consultation |
| La dépendance est-elle maîtrisée ? | Cartographie de sous-traitants, technologie et accès | Mesures de portabilité ou solution de repli |
| La sécurité et la continuité sont-elles démontrées ? | Preuves et tests dans la portée pertinente | Réduction d'accès, contrôles compensatoires ou sortie planifiée |
| Une sortie est-elle faisable ? | Formats, délais, ressources, tests et coûts | Préparer des étapes de réversibilité avant l'échéance |

Le renouvellement n'est pas une simple validation de satisfaction. C'est une décision sur la future exposition au risque, le coût et la capacité du fournisseur à soutenir la feuille de route. Si la sortie immédiate n'est pas réaliste, la décision peut être un renouvellement conditionnel accompagné de jalons, de réduction de dépendance et d'un calendrier de reconsultation approuvé.

### Planifier un test de réversibilité

Définir les données à transférer, leurs formats, le volume, les pièces jointes, la configuration, la documentation, l'historique et les identifiants. Sélectionner un échantillon de bout en bout, exporter, importer dans un environnement contrôlé, vérifier le nombre d'objets, la cohérence des relations et la lisibilité. Vérifier aussi la passation des incidents ouverts, des accès, des contacts, des clés et des procédures. Le test ne doit pas exposer des secrets ni créer une duplication non maîtrisée des données.

Une réversibilité réussie est une capacité démontrée, pas une clause seulement relue. Le risque de sortie doit être traité au début du contrat, réexaminé aux revues et testé avant le moment où une défaillance rendrait la transition urgente.


## Ressources techniques et références

- [UK Government — The Sourcing Playbook](https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks)
- [World Bank — Procurement Framework](https://www.worldbank.org/ext/en/what-we-do/project-procurement/framework)

Les documents de référence apportent des principes et des méthodes, mais leur applicabilité dépend du contexte réel. Vérifier l'édition et le statut de la source au moment de l'utiliser, surtout lorsqu'il s'agit de normes, d'exigences réglementaires ou de guides de marché. Une référence n'est pas à elle seule la preuve de conformité d'une organisation : les contrôles doivent être reliés aux exigences applicables et aux preuves recueillies.

## Synthèse

Gestion des fournisseurs exige une méthode qui transforme l'expérience en décisions traçables, des responsabilités claires, une analyse des risques proportionnée et des vérifications orientées résultats. Le professionnel expert documente les critères, maintient les incertitudes visibles et veille à ce que les décisions soient appliquées et contrôlées. La qualité du dispositif se mesure dans son fonctionnement réel, sa résilience aux imprévus et sa capacité à améliorer durablement les opérations.