# Budgétisation et calcul du ROI

> **Mise en contexte — Budgétisation et ROI** : Le budget de maintenance traduit une stratégie de service en engagements de ressources. Le ROI aide à comparer une dépense à ses bénéfices attendus, mais ne suffit pas à lui seul pour décider : les risques, la continuité, le coût complet, la conformité et la capacité de mise en œuvre comptent aussi. Une décision d'investissement se fonde souvent sur des chiffres incomplets : le coût d'acquisition est visible, mais la migration, la formation, l'intégration, les interruptions, la dette technique et la sortie sont sous-estimées. L'expert construit un modèle transparent, sépare les hypothèses des faits, teste des scénarios et suit les bénéfices réalisés après financement.

## Objectifs pédagogiques

À l'issue du cours, l'apprenant sera capable de :

- construire un budget de maintenance lié aux objectifs métier et au risque
- distinguer CAPEX, OPEX, coûts directs, indirects et coût total de possession
- calculer ROI, délai de récupération et valeur actualisée avec hypothèses explicites
- évaluer coûts évités et bénéfices non financiers sans double comptage
- conduire une analyse de sensibilité et comparer plusieurs options
- mettre en place un suivi des dépenses et bénéfices réalisés

## Prérequis et cadre de responsabilité

Ce cours s'adresse à un professionnel capable de travailler avec des procédures, tickets, données et décisions opérationnelles. Toute décision financière, technique, contractuelle, humaine ou de production doit respecter les autorisations et politiques applicables. Les exemples sont pédagogiques ; ils ne remplacent pas un avis juridique, une règle comptable, une politique de sécurité ou une validation interne. Ne pas inventer de seuil ou présenter une hypothèse comme une exigence approuvée.

Avant une action importante, définir le périmètre, les objectifs, la source de données, le responsable, le résultat attendu, les risques et les conditions d'arrêt. Séparer les faits observés des estimations et hypothèses. Si la qualité des données est insuffisante, le signaler, éviter les conclusions trop générales et organiser le contrôle complémentaire.

## Vocabulaire de référence

| Terme | Définition |
|---|---|
| CAPEX | Dépense d'investissement capitalisée selon les règles comptables applicables. |
| OPEX | Dépense d'exploitation consommée durant la période selon les règles applicables. |
| TCO | Coût total de possession pendant l'horizon choisi, incluant acquisition, mise en œuvre, exploitation et sortie. |
| ROI | Indicateur de rendement relatif selon une définition explicitée des bénéfices et coûts. |
| VAN/NPV | Valeur actuelle nette : valeur actualisée des flux futurs moins l'investissement initial selon les hypothèses retenues. |
| Délai de récupération | Temps nécessaire pour que les flux cumulés compensent l'investissement initial selon la méthode choisie. |
| Coût évité | Coût qu'un scénario de référence aurait probablement supporté et que l'option cherche à réduire. |
| Analyse de sensibilité | Étude de l'effet des hypothèses incertaines sur la décision ou le résultat financier. |

## Schémas de référence

### Schéma 1 — Vision et décision

~~~mermaid
flowchart LR
  A[Objectifs de service] --> B[Besoin et baseline]
  B --> C[Options et coûts]
  C --> D[Arbitrage]
  D --> E[Budget approuvé]
  E --> F[Suivi réel et bénéfices]
  F --> B
~~~

Cycle budgétaire : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 2 — Rôles et contrôles

~~~mermaid
flowchart TD
  A[Acquisition] --> D[TCO cycle de vie]
  B[Intégration et migration] --> D
  C[Opérations et support] --> D
  E[Évolution et sortie] --> D
~~~

TCO : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 3 — Données et dépendances

~~~mermaid
flowchart LR
  A[Coûts initiaux] --> B[Flux futurs]
  B --> C[Actualisation]
  C --> D[VAN et sensibilité]
  D --> E[Décision]
~~~

Flux d'investissement : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 4 — Cycle de mise en œuvre

~~~mermaid
flowchart TD
  A[Baseline] --> B[Hypothèses de bénéfices]
  B --> C[Coûts complets]
  C --> D[Calcul versionné]
  D --> E[Suivi après projet]
  E --> F[Valeur réalisée]
~~~

ROI et preuve : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 5 — Risque et exceptions

~~~mermaid
flowchart TD
  A[Volume] --> D[Résultat financier]
  B[Prix et délai] --> D
  C[Adoption et performance] --> D
  D --> E[Scénarios et seuils]
~~~

Sensibilité : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 6 — Validation des résultats

~~~mermaid
flowchart TD
  A[Demande de dépense] --> B[Budget et autorité]
  B --> C{Engagement autorisé ?}
  C -->|Oui| D[Commande et suivi]
  C -->|Non| E[Replanifier ou escalader]
~~~

Garde-fou de budget : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 7 — Gouvernance et mesure

~~~mermaid
flowchart LR
  A[Économie de trésorerie] --> D[Bénéfice total documenté]
  B[Capacité libérée] --> D
  C[Réduction de risque] --> D
  D --> E[Éviter les doubles comptes]
~~~

Bénéfices : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 8 — Traitement des écarts

~~~mermaid
flowchart TD
  A[Prévu vs réel] --> B[Quantité]
  A --> C[Prix]
  A --> D[Calendrier]
  A --> E[Périmètre]
  B --> F[Prévision à terminaison]
  C --> F
  D --> F
  E --> F
~~~

Écart budgétaire : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 9 — Amélioration continue

~~~mermaid
flowchart TD
  A[Options] --> B[Valeur et risque]
  B --> C[Capacité de réalisation]
  C --> D[Priorité]
  D --> E[Décision révisable]
~~~

Arbitrage portefeuille : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

### Schéma 10 — Sortie et apprentissage

~~~mermaid
flowchart LR
  A[Business case] --> B[Mesure de référence]
  B --> C[Déploiement]
  C --> D[Mesure réelle]
  D --> E[Écart et apprentissage]
~~~

Bénéfices après lancement : ce modèle clarifie les étapes de décision, les dépendances ou les contrôles. Les seuils et responsabilités doivent être adaptés aux règles validées de l'organisation.

## 1. Relier le budget à la stratégie de service

Un budget utile part des objectifs de disponibilité, sécurité, continuité, conformité et cycle de vie. Il finance des capacités et des risques maîtrisés, pas uniquement des lignes historiques. Commencer par inventorier les actifs et services, leur criticité, leur état, leur fin de support, la charge de maintenance et les incidents coûteux. Les priorités découlent d'une analyse des conséquences, pas seulement du montant actuel dépensé.

Distinguer le budget récurrent du portefeuille d'investissements. La maintenance corrective, les contrats de support, les licences, les pièces, la formation, l'astreinte et la supervision peuvent relever de catégories budgétaires différentes selon les règles locales. Un projet de remplacement peut exiger une dépense d'investissement et générer ensuite des coûts récurrents. Le responsable doit travailler avec la finance pour respecter les conventions d'immobilisation, d'amortissement, de fiscalité et de période.

Construire le budget à partir de volumes et de facteurs explicatifs : nombre et âge des actifs, incidents, temps de maintenance, pièces, coût horaire, fournisseurs, évolution des prix et projets approuvés. Distinguer le budget de base, les coûts engagés, les estimations à terminaison et la réserve pour les risques. Un montant historique peut être un point de départ, mais ne garantit pas qu'il suffira après une croissance du parc, un changement réglementaire ou une fin de support.

Le budget doit montrer les arbitrages. Reporter un préventif peut réduire la dépense de cette période mais augmenter le risque de panne, de sécurité ou de coût futur. Une réserve n'est pas une dépense autorisée sans contrôle : elle doit avoir des règles d'utilisation et de revue. Si une contrainte budgétaire force à différer une action essentielle, le risque résiduel doit être présenté à l'autorité qui peut l'accepter.

## 2. Construire le coût total de possession

Le TCO estime les coûts sur une période commune et un périmètre cohérent. Inclure acquisition, conception, intégration, migration, licences, hébergement, exploitation, sécurité, surveillance, support, formation, renouvellement, temps interne, arrêt de service, mise à niveau et sortie. Les coûts indirects peuvent être difficiles à mesurer ; indiquer la méthode et l'incertitude plutôt que les ignorer.

Les coûts doivent être séparés par catégorie, année et scénario. Une solution peu chère au départ peut exiger davantage de personnel, facturer les opérations supplémentaires ou imposer un format propriétaire. Un contrat de maintenance peut exclure les interventions de nuit, les pièces spécifiques ou les sites éloignés. Comparer les options sur le même horizon et documenter les exclusions, l'indexation des prix, les volumes et les hypothèses de croissance.

Le temps de travail doit être traité selon la règle de la finance. Si une équipe existante consacre du temps à la migration, cette capacité possède un coût d'opportunité même si aucune facture externe n'est générée. Ne pas compter deux fois le même bénéfice ou la même dépense : par exemple, compter les heures économisées comme un bénéfice en plus de la valeur totale du travail évité peut surestimer le rendement. Distinguer économies de trésorerie, capacité libérée et productivité potentielle.

La sortie et la réversibilité sont souvent oubliées. Prendre en compte l'export des données, la conversion, la migration, la coexistence temporaire, la formation du successeur, la fin des licences et la suppression contrôlée des données. Un horizon court qui omet le remplacement de matériel ou la fin de contrat peut rendre une option artificiellement attractive. Le TCO doit suivre le cycle de vie pertinent du service ou comparer les options sur une durée identique.

## 3. Calculer ROI, VAN et récupération

Le ROI est souvent présenté comme le bénéfice net divisé par le coût de l'investissement, multiplié par cent. Cette formule doit préciser les coûts et bénéfices inclus, l'horizon, le traitement du coût de fonctionnement et le caractère réalisé ou estimé des flux. Un ROI positif ne prouve pas automatiquement qu'une option est préférable : le délai, le risque, la valeur temporelle de l'argent et les options alternatives comptent.

Exemple pédagogique : un projet demande 40 000 unités monétaires au départ et prévoit 18 000 par an d'économies de trésorerie pendant trois ans, avec 6 000 par an de coût récurrent supplémentaire. Le bénéfice net opérationnel attendu est de 12 000 par an, soit 36 000 sur trois ans. Selon une définition simple de ROI net sur l'horizon, le résultat est (36 000 − 40 000) / 40 000 = −10 %. Si des bénéfices additionnels ou des coûts de démantèlement existent, les intégrer explicitement avant d'arrêter le calcul.

La VAN actualise les flux à un taux qui reflète les règles de financement et le risque retenus. Une formule simplifiée consiste à additionner chaque flux net futur divisé par (1+r)^t puis à retirer l'investissement initial. Les flux doivent avoir la même base nominale ou réelle que le taux, être positionnés dans le temps et inclure les coûts récurrents, les investissements futurs et la valeur résiduelle lorsque cette dernière est justifiée.

Le délai de récupération indique quand les flux cumulés compensent l'investissement, mais une méthode simple ignore les flux postérieurs à la récupération et souvent la valeur temporelle de l'argent. Une méthode actualisée peut compléter l'analyse. Présenter le ROI avec TCO, VAN, délai de récupération, risques, bénéfices non financiers et hypothèses rend la décision plus équilibrée. Éviter une précision mathématique excessive lorsque les flux futurs ne sont que des estimations.

## 4. Valoriser les bénéfices et les risques

Les bénéfices peuvent être directs, par exemple la réduction d'une facture, des licences supprimées ou des pièces moins coûteuses ; opérationnels, comme une réduction du temps d'indisponibilité ; ou non financiers, comme une meilleure traçabilité, une baisse du risque ou une capacité de conformité. Séparer les catégories et indiquer qui valide chaque hypothèse. Une capacité libérée n'est pas automatiquement une économie de trésorerie si aucun coût n'est effectivement évité et si le temps n'est pas réaffecté à une valeur utile.

Les coûts évités sont comparés à un scénario de référence crédible. Il faut expliquer pourquoi le scénario serait survenu, quelle probabilité lui est attribuée, quelle période est utilisée et ce qui change avec le projet. Éviter d'attribuer au projet la totalité d'une baisse de panne si plusieurs actions ont été mises en œuvre. Les hypothèses doivent être contrôlables et mises à jour avec les nouvelles données.

L'analyse de risque examine l'incertitude des coûts, des délais, des volumes, des économies et des bénéfices. Construire au minimum un scénario bas, central et haut. Pour les grands projets, une simulation de Monte-Carlo peut être pertinente si les distributions et corrélations sont justifiées ; elle ne crée pas une certitude lorsqu'on invente les paramètres. Documenter les risques de double comptage, de réalisation tardive, de dépendance fournisseur, d'adoption faible et de coût de transition.

Certaines décisions sont obligatoires même si le ROI financier immédiat est faible : correction d'une vulnérabilité majeure, maintien d'une exigence légale, continuité d'une fonction critique ou retrait d'un équipement dangereux. Dans ces cas, utiliser l'analyse économique pour comparer des modalités de réalisation et les coûts du risque, sans faire du ROI le seul critère d'autorisation.

## 5. Suivre l'exécution et les bénéfices réels

Le business case doit désigner un propriétaire de bénéfice, une référence, une formule, une date de mesure et les sources. Les bénéfices sont souvent différés : économies prévues après migration, baisse d'incidents après formation ou réduction du temps d'intervention après standardisation. Définir les indicateurs avant l'approbation et conserver la possibilité de montrer qu'un bénéfice n'a pas été réalisé.

La revue budgetaire suit prévu, engagé, payé, reste à faire et estimation à terminaison. Expliquer les écarts par quantité, prix, calendrier, périmètre ou hypothèses. Un retard peut décaler les bénéfices au prochain exercice tandis que les coûts continuent ; la prévision doit refléter l'échéancier réel, pas la date initiale du projet.

Après livraison, comparer les résultats et les coûts réels avec le business case. Examiner les coûts inattendus, l'adoption, la qualité de données, les incidents, les bénéfices non réalisés et les effets secondaires. Si la stratégie est modifiée, enregistrer la décision et recalculer le scénario restant. Un tableau de suivi doit distinguer les bénéfices confirmés de ceux qui restent à démontrer.

La gouvernance définit qui peut engager une dépense, approuver une variation, utiliser une réserve, changer le périmètre ou arrêter un projet. Les prévisions sont relues par finance et par les propriétaires techniques. Une revue indépendante est utile pour les investissements importants, les estimations optimistes ou les fournisseurs dont la proposition économique repose sur des hypothèses difficiles à vérifier.

## Procédure opérationnelle recommandée

1. Formuler le besoin et le résultat métier attendu, avant de choisir un outil ou une solution.
2. Définir le périmètre, les parties prenantes, les hypothèses, les contraintes et les critères de réussite.
3. Établir un état initial à partir de sources traçables, vérifier leur qualité et documenter les lacunes.
4. Comparer plusieurs options, leurs bénéfices, coûts, risques, dépendances, réversibilité et effets secondaires.
5. Définir la gouvernance, les approbations, les responsabilités, les délais et les conditions d'arrêt.
6. Tester l'option retenue dans un cadre proportionné au risque, en définissant les preuves attendues.
7. Mettre en œuvre par étapes, conserver la traçabilité et communiquer les écarts.
8. Mesurer le résultat selon les critères initialement retenus, analyser la comparabilité et les effets secondaires.
9. Attribuer les actions restantes, les responsables, les échéances et le test d'efficacité.
10. Réviser la décision ou la stratégie lorsque les preuves, les risques ou les hypothèses changent.

## Gouvernance, mesure et amélioration

Toute mesure utile dispose d'une définition, d'une source, d'un propriétaire, d'une période, d'une fréquence, d'un dénominateur et d'une décision associée. Publier le niveau de couverture et les exceptions lorsque des données sont manquantes. Des chiffres calculés avec des méthodes ou des populations différentes ne sont pas comparables sans analyse de la rupture.

Les décisions importantes doivent être reliées aux preuves, aux risques et aux responsabilités. Une approbation ne prouve pas que l'action a été réalisée ; la réalisation ne prouve pas toujours que le résultat attendu est atteint. Définir séparément la preuve d'implémentation et la vérification d'efficacité. Les écarts doivent rester visibles, avec des mesures provisoires et un risque résiduel accepté par une personne habilitée.

## Atelier pratique — arbitrer trois investissements de maintenance

### Situation de départ

Le comité dispose de trois propositions : remplacer des équipements en fin de support, automatiser le triage des incidents et renouveler une plateforme de supervision. Les coûts initiaux, les bénéfices attendus, les risques et les dépendances sont différents. Les estimations n'utilisent pas toutes le même horizon et certains bénéfices sont exprimés comme des heures libérées plutôt que comme des économies réelles. Le comité demande un classement avant de financer les projets.

### Phase A — Normaliser les hypothèses

Définir pour chaque option l'horizon, l'investissement initial, les coûts récurrents, le coût de sortie, les volumes et les sources. Séparer économies de trésorerie, capacité libérée, réduction de risque et bénéfices non financiers.

### Phase B — Construire le TCO

Comparer les options sur la même durée, avec licences, migration, formation, exploitation, pièces, renouvellement et fin de contrat. Identifier les coûts omis et documenter les scénarios bas, central et haut.

### Phase C — Calculer les mesures

Calculer ROI selon une définition explicite, délai de récupération et VAN si les flux annuels et le taux ont été validés. Vérifier unités, signes, périodes, cumul des flux et absence de double comptage.

### Phase D — Comparer risque et obligation

Tenir compte de la criticité, de l'obsolescence, des contraintes contractuelles et des possibilités de déploiement progressif. Ne pas rejeter automatiquement une mesure obligatoire parce que son ROI direct est négatif.

### Phase E — Préparer l'arbitrage

Fournir au comité une recommandation, les hypothèses les plus sensibles, les seuils de décision, les mesures de suivi et les conditions de suspension. Affecter le propriétaire des bénéfices et les dates de revue.

### Critères de réussite

Le dossier doit être repris par une personne qui n'a pas participé à l'exercice. Il doit montrer le besoin, la méthode, les données, les décisions, les risques et les validations. Les hypothèses non vérifiées restent identifiées ; les actions sont attribuées et mesurables ; le résultat est confronté à une baseline ou à des critères approuvés. Une conclusion convaincante mais non reproductible n'est pas validée.

## Études de cas

### Cas 1 — Économies comptées deux fois

Les heures libérées sont valorisées à un taux interne puis ajoutées à une économie de prestation externe qui couvre déjà le même travail. Décomposer les flux et supprimer le recouvrement.

### Cas 2 — Dépense de sortie oubliée

La solution proposée paraît rentable sur trois ans mais exige des frais importants d'export et de migration en fin de période. Intégrer la sortie ou expliquer pourquoi elle n'est pas dans l'horizon.

### Cas 3 — Projet obligatoire à ROI faible

Une mise à niveau est nécessaire pour respecter un engagement de support ou de sécurité. Comparer les options et les coûts du risque, mais faire traiter l'obligation selon le processus de gouvernance.

## Exercices d'application avec corrigés

### Exercice 1 — Définir et comparer

**Question.** Un investissement de 20 000 produit 28 000 de bénéfices nets cumulés sur l'horizon, hors investissement. Quel ROI simple ?

**Corrigé expliqué.** ROI = (28 000 − 20 000) / 20 000 × 100 = 40 %, selon cette définition. Il faut encore préciser si les 28 000 comprennent tous les coûts récurrents et si les flux sont actualisés.

### Exercice 2 — Interpréter le résultat

**Question.** Pourquoi comparer les TCO sur un horizon identique ?

**Corrigé expliqué.** Un horizon court peut omettre licences, renouvellement ou sortie. La comparaison doit couvrir un cycle de vie comparable et expliciter les hypothèses qui ne sont pas symétriques.

### Exercice 3 — Sélectionner une méthode

**Question.** Les techniciens économisent 100 heures par mois. Est-ce une économie financière réalisée ?

**Corrigé expliqué.** Pas nécessairement. Il s'agit d'abord d'une capacité libérée. Elle devient un bénéfice financier uniquement si elle évite un coût ou si son réemploi productif est mesuré et validé.

### Exercice 4 — Traiter un risque

**Question.** Qu'apporte la sensibilité ?

**Corrigé expliqué.** Elle montre quelles hypothèses influencent la décision, par exemple volume, coût d'intégration, adoption ou taux de panne. Elle aide à fixer des conditions d'arrêt ou des paliers d'investissement.

### Exercice 5 — Évaluer la preuve

**Question.** Une VAN positive suffit-elle à financer le projet ?

**Corrigé expliqué.** Non. Examiner risques, obligations, capacité d'exécution, dépendances, options alternatives, effets non financiers et seuils d'approbation.

### Exercice 6 — Vérifier l'efficacité

**Question.** Comment prouver un bénéfice après déploiement ?

**Corrigé expliqué.** Comparer des mesures postérieures à une référence cohérente, attribuer un propriétaire, vérifier la qualité des données et analyser les autres changements qui influencent le résultat.

## Défi final — mise en situation experte

Présenter un dossier d'investissement sur cinq ans pour remplacer une famille d'actifs vieillissants, automatiser certains contrôles et renouveler un contrat de support. Inclure baseline, TCO, flux par période, ROI, VAN avec taux approuvé, délai de récupération, scénarios, risques et bénéfices non financiers. Le corrigé doit tracer les hypothèses, éviter le double comptage, distinguer capacité libérée et économies encaissées, et définir les revues qui confirmeront les bénéfices.

**Livrable attendu.** Produire un dossier qui présente la situation, la décision, les options, les preuves, les risques et le plan de suivi. Chaque recommandation doit être liée à une raison, un propriétaire et un critère de réussite. Expliquer les incertitudes, les limites du périmètre et les conditions qui feraient réviser la décision.

**Correction attendue.** Une solution experte est cohérente, mesurable et gouvernée. Elle ne confond pas une estimation et un résultat confirmé, ne masque pas les coûts ou risques, compare les options dans un cadre commun et prévoit le contrôle de fin. Elle identifie les décisions qui nécessitent une validation spécialisée et laisse une piste compréhensible pour une revue ultérieure.


## Exemple financier détaillé — arbitrage d'un projet d'automatisation

Le dossier financier doit rendre les hypothèses lisibles. Considérons un projet fictif d'automatisation des contrôles de maintenance avec un investissement initial de 40 000 unités monétaires. Le projet prévoit 24 000 unités d'économies de trésorerie par an, mais exige 6 000 unités de coûts récurrents supplémentaires. Le bénéfice net annuel attendu est donc de 18 000 unités, si les économies sont réellement réalisables et si tous les coûts récurrents pertinents sont inclus.

Sur trois ans, les bénéfices nets non actualisés totalisent 54 000 unités. Le ROI simple défini comme (bénéfices nets cumulés − investissement initial) / investissement initial donne (54 000 − 40 000) / 40 000 = 35 %. Le délai de récupération simple est 40 000 / 18 000, soit environ 2,22 ans, si les flux sont uniformes et si les économies commencent immédiatement. Ces chiffres ne prennent pas en compte la valeur temporelle de l'argent, les variations de calendrier ni un éventuel coût de sortie.

Avec un taux d'actualisation illustratif de 8 % et trois flux de 18 000 à la fin de chaque année, la VAN est approximativement : 18 000/1,08 + 18 000/1,08² + 18 000/1,08³ − 40 000, soit environ 6 400 unités positives. Le taux utilisé doit provenir des règles de financement ou de l'analyse approuvée ; il ne faut pas choisir un taux après calcul dans le but de rendre la VAN positive.

### Tester la robustesse du business case

| Scénario | Bénéfice net annuel estimé | Durée | Lecture de la décision |
|---|---:|---:|---|
| Bas | 10 000 | 3 ans | Flux total de 30 000 avant actualisation ; le projet ne récupère pas les 40 000 d'investissement dans l'horizon |
| Central | 18 000 | 3 ans | Flux total de 54 000 avant actualisation, avec ROI simple de 35 % |
| Haut | 23 000 | 3 ans | Flux total de 69 000 avant actualisation ; la valeur augmente, mais les hypothèses doivent être justifiées |

Ce tableau ne constitue pas une prévision. Il montre que la décision est sensible à la réalisation des économies. Le propriétaire des bénéfices doit expliquer d'où vient l'économie annuelle, quel contrat ou poste budgétaire peut réellement baisser, quand cet effet apparaît et quelles tâches seront réaffectées. Si les 24 000 unités correspondent essentiellement à des heures libérées, le bénéfice de trésorerie doit être recalculé et la capacité libérée décrite séparément.

### Budget opérationnel de maintenance

Le budget opérationnel doit être accompagné d'un profil temporel. Les dépenses de pièces peuvent dépendre des délais et de la saisonnalité ; un projet de remplacement requiert un financement avant que les économies se matérialisent ; un contrat annuel peut facturer une prestation avant les mesures de bénéfice. Le phasage évite que le budget global paraisse équilibré alors que la trésorerie et les ressources sont insuffisantes dans les premiers mois.

Chaque ligne importante porte sa source, quantité, prix unitaire, hypothèse de croissance, propriétaire, niveau de confiance, engagement, calendrier et risque associé. Les variations sont analysées séparément : effet prix, effet volume, effet de calendrier, changement de périmètre et dérive de l'estimation. Une provision pour risque doit être associée à un événement et à des règles de consommation. Elle ne sert pas à compenser des estimations délibérément basses.

### Règles de décision et suivi après investissement

Avant d'approuver, décider les conditions qui entraîneraient un report, une étape pilote ou l'arrêt. Pour une automatisation, un critère peut exiger un taux d'erreur inférieur à un seuil et une traçabilité complète avant de réduire le contrôle manuel. Pour un remplacement, la décision peut dépendre de la disponibilité des pièces, de la réussite des tests de migration et de la capacité à maintenir le service pendant la transition.

Après mise en œuvre, suivre les flux réalisés et les bénéfices selon la même définition. Si les coûts sont au-dessus du budget ou les économies inférieures, expliquer les causes, prévoir les conséquences sur la VAN et choisir une action : corriger le périmètre, renégocier, suspendre une vague ou accepter un nouvel état de bénéfice. L'équipe ne doit pas réécrire le business case initial sans conserver son historique, car la direction doit pouvoir comprendre ce qui a changé.



## Construire une prévision, gérer les incertitudes et défendre un arbitrage

Un budget annuel doit évoluer avec les données. Le responsable conserve le budget approuvé comme référence, puis suit les dépenses engagées, les factures, les commandes, les coûts prévus et les changements de périmètre. La prévision à terminaison est l'estimation actuelle du coût total à la fin de la période ou du projet ; elle ne doit pas être assimilée au budget initial. Un écart peut venir d'un changement de quantité, d'un effet de prix, d'un glissement du calendrier ou d'une hypothèse incorrecte, et chacun appelle une réponse différente.

### Exemple de variation budgétaire

Un contrat de maintenance était prévu pour 120 actifs à un tarif unitaire annuel de 100 unités monétaires, soit 12 000. En cours d'année, l'inventaire confirme 135 actifs éligibles. À tarif constant, le coût attendu devient 13 500 : l'écart de 1 500 provient du volume. Si le tarif passe aussi de 100 à 105, le coût total est 14 175. Pour expliquer l'écart total de 2 175 par rapport à la base, séparer la variation de volume et la variation de prix en utilisant une méthode cohérente, puis documenter toute interaction si le modèle l'exige. Cette explication est plus actionnable que de dire simplement « dépassement de 18,1 % ».

### Réserver les ressources et mettre à jour les hypothèses

Les prévisions de maintenance doivent intégrer les risques d'arrêt, de pièces, d'obsolescence, de reprise, de capacité et de transition. Une dépense peut être faible en moyenne mais volatile ; les événements rares avec un impact élevé doivent être présentés comme des scénarios de risque et non dissimulés dans une moyenne. La réserve est liée à une justification, un propriétaire et des règles d'approbation. Utiliser une réserve pour couvrir un dépassement permanent signifie souvent que le budget de base n'est pas réaliste.

Pour les investissements, prévoir les ressources internes en plus du financement. Une migration peut être techniquement financée mais impossible si l'équipe d'exploitation n'a pas le temps de valider les configurations, de former le support et de maintenir le service existant. La feuille de route financière doit donc inclure capacité, formation, environnement de test, sécurité, migration, support et transition.

### Faire une revue de valeur après livraison

À une date convenue, réunir finance, propriétaire de service et responsable du projet pour comparer la baseline, les coûts réels et les bénéfices. Si le projet réduit le temps de traitement mais n'entraîne aucune économie de trésorerie, le compte rendu peut reconnaître une amélioration de capacité, expliquer comment cette capacité sera utilisée et distinguer le résultat du business case financier initial. Ne pas reclasser rétroactivement une capacité libérée en économie réalisée sans une règle et une preuve correspondantes.

Les écarts aux bénéfices attendus peuvent conduire à une action corrective : améliorer l'adoption, changer le processus, revoir le contrat ou arrêter une fonction qui ne crée pas de valeur. La revue doit préserver l'historique des hypothèses afin que les futurs investissements bénéficient de l'expérience. Cette discipline évite de bâtir les dossiers suivants sur des bénéfices théoriques jamais vérifiés.


## Ressources techniques et références

- [HM Treasury — The Green Book (édition 2026)](https://www.gov.uk/government/publications/the-green-book--2)
- [HM Treasury — Sourcing Playbook et évaluation des options](https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks)

Ces ressources apportent des principes et des méthodes ; vérifier leur édition, leur périmètre et leur applicabilité avant de les utiliser comme critères de décision. Les règles locales de finance, de contrat, de sécurité, de ressources humaines et de maintenance restent à confirmer avec les responsables compétents.

## Synthèse

Budgétisation et calcul du ROI demande une articulation cohérente entre objectifs, pratiques, gouvernance, ressources et preuves. Une démarche experte formule des critères avant d'agir, documente les risques et les incertitudes, vérifie le résultat réel et transforme les écarts en actions. Le niveau de maîtrise se mesure moins au nombre d'outils ou de rapports qu'à la qualité des décisions et à la capacité du système à s'améliorer durablement.