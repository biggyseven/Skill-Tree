# Rédiger un rapport d'incident

> **Mise en contexte** — Ce cours s'adresse à un technicien intermédiaire qui doit agir dans un environnement réel, respecter les contraintes de service et laisser des preuves réutilisables. L'objectif n'est pas seulement de connaître les outils, mais de comprendre pourquoi une action est choisie, dans quelles conditions elle est sûre, comment vérifier son résultat et quand demander de l'aide.

## Présentation et enjeux

Le rapport d'incident constitue une trace structurée des faits, de l'impact, de la chronologie, des décisions et des actions. Il doit séparer les informations confirmées des hypothèses afin d'aider le support, les responsables métier et les équipes techniques à prendre des décisions réutilisables. Cette discipline s'inscrit dans une démarche de qualité de service : chaque opération doit être reliée au besoin métier, au risque accepté et à un critère d'acceptation observable. L'intervenant doit pouvoir expliquer l'état initial, la décision prise, les résultats obtenus et les limites qui subsistent.

Dans une équipe de maintenance, les informations sont souvent réparties entre tickets, conversations, inventaires, systèmes de supervision et mémoire individuelle. Une méthode fiable les relie dans une trace commune et limite les décisions fondées sur une seule observation. Le cours met l'accent sur les preuves, les contrôles proportionnés, la reproductibilité et la communication utile.

Le niveau intermédiaire suppose que les gestes de base sont acquis. La difficulté consiste maintenant à traiter des environnements hétérogènes, des incidents ambigus, des changements qui touchent plusieurs composants et des situations où la donnée est imparfaite. Les règles présentées doivent être adaptées aux procédures approuvées de l'organisation et vérifiées dans un environnement de test avant toute action ayant un impact sur la production.

## Objectifs pédagogiques

À la fin du parcours, l'apprenant pourra :

- expliquer les principes et les limites des outils utilisés dans le domaine ;
- choisir un contrôle ou une méthode à partir de l'impact, de la criticité et des preuves disponibles ;
- effectuer une démarche reproductible et distinguer observation, hypothèse et décision ;
- interpréter les indicateurs sans confondre corrélation, résultat technique et expérience utilisateur ;
- rédiger une trace claire, traiter les exceptions et organiser une escalade ;
- vérifier l'effet d'une action, décrire le risque résiduel et proposer une amélioration mesurable.

## Prérequis et cadre de travail

Avant de commencer, savoir utiliser un terminal, lire les journaux, identifier un actif, comprendre les tickets et appliquer les règles locales de sécurité. Les commandes ci-dessous sont illustratives : adapter les noms d'hôte, les chemins et les versions, utiliser des cibles de test autorisées et ne jamais copier de secret dans un document. Une commande d'observation doit être préférée à une modification lorsqu'elle suffit à qualifier la situation.

Les principes directeurs sont les suivants : intervention autorisée, moindre privilège, sauvegarde ou retour arrière adaptés, fenêtre connue, communication compréhensible et preuve de validation. Si un contrôle critique échoue, ne pas continuer mécaniquement. Noter le constat, évaluer le risque et utiliser le point d'arrêt ou l'escalade défini par la procédure.

## Vocabulaire métier

| Terme | Utilisation opérationnelle |
|---|---|
| État initial | Description mesurée du système avant toute intervention. |
| Criticité | Conséquence potentielle de l'indisponibilité ou de la mauvaise configuration. |
| Preuve | Élément daté qui peut être vérifié par un autre intervenant. |
| Écart | Différence entre le résultat attendu et l'observation. |
| Exception | Situation où la procédure standard ne s'applique pas ou n'atteint pas son objectif. |
| Validation | Contrôle confirmant que le service ou l'opération satisfait les critères convenus. |
| Retour arrière | Séquence permettant de retrouver un état stable si les critères de réussite ne sont pas satisfaits. |
| Récurrence | Réapparition d'un problème similaire après un traitement précédent. |

## Cartographie des processus

### Schéma 1 — chaîne opérationnelle

```mermaid
flowchart LR
  A[Signal] --> B[Collecte] --> C[Seuil] --> D[Décision] --> E[Action]
```

Ce schéma résume la chaîne à observer pour rédiger un rapport d'incident. Chaque étape possède une entrée, une sortie et une responsabilité. Si une transition n'est pas visible, la procédure doit prévoir une vérification plutôt que supposer que l'étape précédente a réussi.

### Schéma 2 — cycle de traitement

```mermaid
flowchart LR
  A[Préparer] --> B[Exécuter] --> C[Contrôler] --> D[Valider] --> E[Tracer]
```

Le cycle doit être parcouru du début à la fin, sans supprimer la validation ni la trace. Une intervention peut être techniquement terminée alors que son résultat n'est pas encore accepté par le service concerné.

### Schéma 3 — maîtrise du risque

```mermaid
flowchart LR
  A[Actif] --> B[Risque] --> C[Contrôle] --> D[Preuve] --> E[Revue]
```

La décision finale doit tenir compte du risque et des preuves. Une alerte, une action ou un changement de statut n'est utile que si l'information est assez fiable pour permettre la suite du travail.

### Schéma 4 — parcours d'une demande

```mermaid
flowchart LR
  A[Demande] --> B[Qualification] --> C[Traitement] --> D[Validation] --> E[Clôture]
```

Le parcours doit laisser au technicien un état explicite à chaque étape : en attente, en cours, bloqué, validé ou escaladé. Des états ambigus rendent les indicateurs de délai et le pilotage peu fiables.

### Schéma 5 — démarche d'analyse

```mermaid
flowchart LR
  A[Mesure] --> B[Analyse] --> C[Hypothèse] --> D[Test] --> E[Conclusion]
```

L'analyse gagne à séparer constat, hypothèse et conclusion. Les preuves qui ne soutiennent pas l'hypothèse doivent rester disponibles afin d'expliquer pourquoi une piste a été écartée.

### Schéma 6 — boucle d'amélioration

```mermaid
flowchart LR
  A[Détection] --> B[Escalade] --> C[Diagnostic] --> D[Rétablissement] --> E[Retour]
```

La boucle se ferme lorsque les retours et incidents servent à changer le dispositif, puis qu'un contrôle démontre l'effet de cette amélioration. Une action documentaire sans vérification de terrain reste incomplète.

## Fondements techniques du domaine

### 1. Résumé exécutif

Le résumé explique le service touché, la durée connue, l'impact utilisateur, l'état actuel et les prochaines étapes. Commencer par les faits qui permettent de décider puis conserver les détails techniques dans les sections adaptées.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Relier chaque affirmation importante à une mesure ou à une source consultable. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Une cause non confirmée formulée comme certitude peut entraîner une décision incorrecte. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 2. Périmètre et impact

Le rapport identifie sites, utilisateurs, fonctions métier et services effectivement affectés. Quantifier les conséquences lorsque les sources le permettent et préciser les limites d'estimation.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Conserver les tickets et sources de mesure qui permettent de retracer le périmètre. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Dire « tout le monde » sans vérification rend l'analyse peu fiable. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 3. Chronologie

Les événements relient détection, escalade, changements, actions et validation du retour au service. Normaliser les fuseaux horaires sans effacer l'heure d'origine et distinguer l'heure de l'événement de celle de sa découverte.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Comparer supervision, logs et messages afin de réduire les biais de mémoire. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Des horloges désynchronisées peuvent inverser l'ordre apparent des événements. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 4. Preuves

Une preuve doit soutenir une hypothèse, une décision ou une mesure, au lieu d'être jointe sans contexte. Enregistrer source, horodatage, contexte, empreinte si utile et niveau de sensibilité.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Index des pièces jointes et références de ticket rendent le rapport vérifiable. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Secrets et données personnelles doivent être expurgés des copies distribuées. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 5. Cause et incertitude

Les conclusions doivent indiquer le niveau de confiance et les hypothèses encore ouvertes. Relier la cause proposée aux observations et aux tests qui éliminent les alternatives.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Séparer les faits et les hypothèses permet d'actualiser le rapport sans réécrire l'historique. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Une simple corrélation temporelle ne démontre pas la causalité. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 6. Rétablissement

Il faut distinguer le contournement qui remet le service en route de la correction durable. Décrire les modifications, validations, effets secondaires observés et risques restant à traiter.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Les configurations avant/après et les tests applicatifs soutiennent la décision de reprise. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Un contournement temporaire doit avoir une échéance ou une condition de retrait. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 7. Communication

Le rapport précise qui a été informé, quand, avec quel niveau d'information et quelles décisions ont été prises. Relier les messages aux faits disponibles au moment de leur envoi.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Les traces horodatées expliquent le déroulé de l'incident. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Ne pas prêter d'intention personnelle sans preuve ; décrire actions et contexte. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

### 8. Actions correctives

Chaque action doit adresser un mécanisme de risque et posséder un responsable, une échéance et une mesure de succès. Distinguer correction immédiate, prévention, détection, documentation et gouvernance.

**Mise en œuvre.** Pour appliquer ce principe dans rédiger un rapport d'incident, commencer par fixer le périmètre et l'état attendu. Identifier ensuite la donnée qui permet d'observer le résultat, la personne autorisée à prendre la décision et le moment où le contrôle doit être réalisé. Le test doit être assez précis pour qu'un second technicien puisse le reproduire sans demander une explication orale complémentaire. Si plusieurs méthodes sont possibles, noter pourquoi la méthode retenue est la plus proportionnée au risque et au temps disponible.

**Preuves et interprétation.** Lier le rapport au suivi des actions empêche les engagements de disparaître après publication. L'intervenant doit garder la source, l'heure, le résultat, le contexte et la limite éventuelle de l'observation. Une preuve isolée n'a parfois qu'une valeur indicative ; elle doit alors être croisée avec un autre signal indépendant. Les données manquantes ne doivent pas être remplacées par une supposition. Lorsqu'une mesure est indirecte, préciser ce qu'elle démontre réellement et ce qu'elle ne démontre pas.

**Pièges et décision.** Une action vague ne permet pas de vérifier sa réalisation ni son efficacité. En cas d'écart, classer le résultat comme confirmé, probable ou inconnu et déterminer la prochaine action. Ne pas masquer un résultat défavorable par une moyenne, une fermeture de ticket ou un changement de catégorie. Si le risque dépasse l'autorité de l'intervenant, conserver les preuves et escalader plutôt que poursuivre sur la base d'une hypothèse fragile.

## Méthode transversale pour une opération maîtrisée

### 1. Gouvernance

L'intervention doit être reliée à un objectif de service, un propriétaire et une décision explicite. Le contrôle de gouvernance n'a de valeur que s'il aide à identifier qui peut accepter le risque et qui doit être informé. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 2. Cycle de vie

La solution doit être pensée depuis la préparation jusqu'à la sortie, y compris le maintien des compétences et le retrait des anciennes données. Une étape oubliée en fin de cycle transforme souvent une réussite ponctuelle en risque latent. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 3. Qualité de données

Toute mesure dépend de la qualité de son périmètre, de l'horodatage, de l'unité et de la provenance. Il faut identifier les champs manquants et les conventions contradictoires avant de tirer une conclusion. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 4. Gestion du risque

Le risque se juge par probabilité, impact, capacité de détection et marge de récupération. Les éléments critiques doivent recevoir plus de contrôles, sans imposer la même lourdeur aux opérations réversibles et aux changements irréversibles. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 5. Communication

Une communication utile indique ce qui est connu, ce qui reste à vérifier, qui agit ensuite et quand une nouvelle information sera fournie. Les formulations doivent éviter les promesses non vérifiées. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 6. Sécurité

Le périmètre technique doit rester limité aux systèmes autorisés, avec une identité traçable et les droits minimaux nécessaires. Les secrets doivent être protégés dans les fichiers, les journaux, les captures et les exports. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 7. Traçabilité

Une action exploitable doit laisser un résultat vérifiable, un horodatage, un propriétaire et un lien avec le ticket ou le changement. La trace doit permettre à un autre technicien de comprendre ce qui a été fait. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 8. Gestion des exceptions

Les cas hors procédure doivent être visibles et conduire à un point d'arrêt, une décision ou une escalade. Une exception récurrente est souvent le signal qu'il faut faire évoluer la procédure plutôt que la répéter. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 9. Amélioration continue

Les incidents, les retours utilisateurs et les contrôles qualité doivent transformer les règles et procédures. Il faut vérifier si les modifications réduisent réellement le risque, et pas seulement si les documents ont été mis à jour. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 10. Capacité

Les ressources, compétences, fenêtres et dépendances limitent le volume d'opérations réalisables. Une planification crédible tient compte de la charge, des temps de contrôle et des imprévus. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 11. Contrôle du changement

Une modification nécessite un état initial connu, un périmètre, des critères de réussite et une solution de repli adaptée au risque. L'urgence ne supprime pas le besoin de garder une trace des décisions. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 12. Mesure d'efficacité

Un indicateur ne vaut que si sa définition reste constante et si sa variation peut conduire à une décision. Les chiffres doivent être accompagnés d'une période, d'un périmètre et des limites de mesure. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 13. Passation

Une tâche doit pouvoir être reprise par une autre personne sans dépendre des souvenirs du technicien présent. La transmission contient contexte, preuves, étapes déjà tentées et prochaine action. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

### 14. Validation métier

Le résultat technique doit être confirmé du point de vue du service. Un équipement joignable ou un script qui termine sans erreur ne suffit pas si l'utilisateur ne peut pas accomplir son opération. Pour rédiger un rapport d'incident, cela signifie que la personne qui agit doit relier la règle à un élément concret : complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue. Avant l'opération, noter l'état de départ et ce qui fera considérer le résultat comme acceptable. Pendant l'action, conserver le contexte des changements et indiquer immédiatement les écarts. Après l'action, exécuter le contrôle correspondant au risque, enregistrer le résultat et affecter les suites restantes. Cette discipline augmente la qualité de la passation et réduit la dépendance à une personne unique.

## Indicateurs : définition, lecture et limites

Les indicateurs les plus utiles pour ce domaine sont : **complétude du rapport, délai de publication, actions correctives suivies, chronologies vérifiées, corrections requises après revue**. Chaque indicateur doit avoir une définition écrite. Il faut préciser l'unité, la source, le périmètre, la fréquence, la période et les exclusions. Lorsque les données ne couvrent qu'une partie de l'environnement, le rapport doit le signaler au lieu d'extrapoler silencieusement. Un indicateur doit permettre une décision : prioriser, déclencher une vérification, ajuster une capacité, revoir une procédure ou accepter explicitement un risque.

Un bon tableau de bord met en évidence la tendance et les écarts significatifs, sans supprimer la donnée de départ. Il distingue les valeurs brutes, les seuils, les anomalies confirmées et les périodes sans mesure. Une moyenne peut cacher des situations extrêmes ; il est donc souvent nécessaire d'observer la distribution, les percentiles, les valeurs maximales et la répartition par service ou par criticité. Les changements de définition doivent être versionnés pour éviter de comparer des séries qui ne signifient plus la même chose.

Les indicateurs ne doivent pas devenir des objectifs isolés. Par exemple, réduire le délai moyen n'est pas une amélioration si les tickets sont fermés avant validation et immédiatement rouverts. De même, atteindre un taux de conformité en excluant les actifs inconnus peut donner une image artificiellement favorable. Associer un KPI à un contrôle de qualité et à un résultat métier permet de repérer ces effets indésirables.

## Procédure opérationnelle recommandée

1. **Préparer.** Confirmer la demande, le périmètre, le propriétaire, l'autorisation et la fenêtre. Vérifier les dépendances, les sauvegardes et les accès nécessaires.
2. **Établir l'état initial.** Recueillir les mesures, l'état des services, les alertes, la dernière intervention et les écarts connus. Noter les éléments non vérifiables.
3. **Évaluer les risques.** Déterminer impact, probabilité, détectabilité, réversibilité et critère de report. Définir un point d'arrêt compréhensible.
4. **Exécuter par étapes.** Utiliser les outils approuvés, limiter le périmètre et vérifier les résultats intermédiaires avant de passer à l'étape suivante.
5. **Contrôler.** Comparer l'état final à l'état attendu et tester le service selon un scénario réaliste, pas uniquement le composant technique.
6. **Tracer.** Enregistrer les horaires, commandes ou actions, résultats, décisions et écarts dans le ticket ou le référentiel prévu.
7. **Communiquer.** Annoncer le résultat en termes compréhensibles, préciser les limites et indiquer qui gère les actions ouvertes.
8. **Améliorer.** Rechercher les étapes ambiguës ou les contrôles inefficaces et proposer une modification versionnée, testée et approuvée.

## Outils et contrôles pratiques

Les outils doivent être sélectionnés selon l'objectif, les droits et le type de preuve recherché. L'usage d'un outil connu ne dispense pas de contrôler son contexte : version, paramètres, cible, unité, état de connexion et limite de la mesure. ITSM, journaux, supervision, horodatage UTC, diff de configuration, modèle de rapport, revue post-incident constituent des exemples de technologies possibles ; leur choix exact dépend de l'environnement et des politiques internes.

| Contrôle | Question à poser | Trace à conserver |
|---|---|---|
| Identité de la cible | Est-ce bien l'actif ou le service autorisé ? | Identifiant, inventaire et horodatage. |
| État initial | Quelle condition de départ a été mesurée ? | Valeur, source, capture ou sortie. |
| Autorisation | Qui a approuvé l'action et pour quelle fenêtre ? | Ticket, validation et périmètre. |
| Résultat | Qu'est-ce qui démontre que le résultat est correct ? | Test de contrôle et résultat observé. |
| Écart | Que faire si le résultat attendu n'est pas obtenu ? | Point d'arrêt, escalade et action attribuée. |

### Commandes et exemples

Les commandes de cette section servent à illustrer la collecte de preuves. Remplacer les valeurs de test par des cibles autorisées et vérifier localement les options selon la distribution et la version de l'outil.

#### Exemple 1 — Capturer des journaux sur une période

```bash
journalctl --since '2026-10-27 08:00:00' --until '2026-10-27 09:00:00' --no-pager
```

Interpréter la sortie avec le contexte de l'intervention. Un retour nul ne démontre pas toujours que la fonction métier est opérationnelle. Relever les erreurs, vérifier l'heure des journaux et comparer les observations avec une seconde source lorsque l'impact le justifie. Ne pas intégrer un résultat de terminal dans un rapport sans préciser la machine, la période et la commande effectivement exécutée.

#### Exemple 2 — Établir l'heure UTC

```bash
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

Interpréter la sortie avec le contexte de l'intervention. Un retour nul ne démontre pas toujours que la fonction métier est opérationnelle. Relever les erreurs, vérifier l'heure des journaux et comparer les observations avec une seconde source lorsque l'impact le justifie. Ne pas intégrer un résultat de terminal dans un rapport sans préciser la machine, la période et la commande effectivement exécutée.

#### Exemple 3 — Calculer l'empreinte d'une preuve

```bash
sha256sum preuve.log
```

Interpréter la sortie avec le contexte de l'intervention. Un retour nul ne démontre pas toujours que la fonction métier est opérationnelle. Relever les erreurs, vérifier l'heure des journaux et comparer les observations avec une seconde source lorsque l'impact le justifie. Ne pas intégrer un résultat de terminal dans un rapport sans préciser la machine, la période et la commande effectivement exécutée.

#### Exemple 4 — Vérifier les changements de configuration suivis

```bash
git status --short && git diff --check
```

Interpréter la sortie avec le contexte de l'intervention. Un retour nul ne démontre pas toujours que la fonction métier est opérationnelle. Relever les erreurs, vérifier l'heure des journaux et comparer les observations avec une seconde source lorsque l'impact le justifie. Ne pas intégrer un résultat de terminal dans un rapport sans préciser la machine, la période et la commande effectivement exécutée.

## Atelier pratique guidé

### Situation de départ

L'équipe reçoit une demande concernant rédiger un rapport d'incident. Le contexte est incomplet : l'utilisateur décrit un symptôme, une mesure semble inhabituelle et une intervention antérieure est mentionnée sans détail. Le travail consiste à produire une réponse reproductible, sans prendre de risque inutile et sans annoncer une conclusion que les preuves ne soutiennent pas.

### Phase A — Qualification

Créer ou mettre à jour le ticket ; identifier le service, les utilisateurs concernés, le propriétaire technique, la période et les changements récents. Réunir les journaux et les mesures disponibles. Séparer les faits confirmés des déclarations de l'utilisateur. Déterminer si le problème est en cours, intermittent ou résolu, et préciser ce qui manque encore. Définir l'impact selon les critères de service et la priorité de traitement. Si la cible n'est pas certaine, valider son identité par l'inventaire avant d'exécuter la moindre action.

### Phase B — Hypothèses et tests

Formuler au moins deux hypothèses concurrentes. Pour chacune, préciser le signal qui devrait être observé si elle est vraie, le signal qui permettrait de la rejeter et le coût du test. Commencer par les contrôles en lecture seule, puis ne réaliser une modification que si elle est autorisée et nécessaire. Garder les résultats qui contredisent l'hypothèse initiale ; ils évitent de persister sur la mauvaise piste. Si les tests se contredisent, vérifier l'horloge, la version des données, la portée du contrôle et la possibilité d'une panne intermittente.

### Phase C — Action contrôlée

Choisir une action proportionnée au risque et limitée au périmètre identifié. Avant de modifier, noter l'état initial, confirmer la sauvegarde ou le retour arrière adapté et prévenir les personnes concernées. Exécuter une seule modification majeure à la fois lorsque cela permet d'isoler son effet. Si un point d'arrêt est atteint, conserver les preuves et contacter le niveau compétent plutôt que contourner la règle. Après l'action, répéter le test initial et vérifier le service par une transaction ou un parcours représentatif.

### Phase D — Validation et restitution

Comparer le résultat aux critères d'acceptation. Décrire ce qui a changé, ce qui a été vérifié, ce qui reste incertain et les actions ouvertes. La restitution doit être compréhensible pour un utilisateur non spécialiste et suffisamment technique pour un collègue qui reprendrait le dossier. Associer chaque action à un responsable et une échéance. Lorsque la procédure a été difficile à appliquer, signaler précisément la phrase, le champ ou le contrôle à améliorer.

## Études de cas

### Cas 1 — Interruption d'un service

**Situation.** Un service indisponible pendant quarante minutes nécessite la contribution de plusieurs équipes. Le service doit être préservé et les actions doivent rester explicables. La première réaction ne doit pas consister à redémarrer ou modifier au hasard : il faut d'abord vérifier le périmètre, l'heure, l'état initial et les changements concomitants.

**Analyse.** Assembler alertes, communications et changements dans une chronologie unifiée puis calculer la durée selon les règles de service. Consigner les observations qui distinguent les hypothèses, puis rechercher les dépendances susceptibles de produire le même symptôme. Si une source de donnée est absente, l'indiquer et prévoir un moyen de la récupérer pour une prochaine occurrence. Vérifier aussi l'effet sur les autres services et le risque que l'action proposée crée une interruption plus large que le problème initial.

**Décision et preuve.** Présenter les causes confirmées, les limites de preuve et les actions restantes. La conclusion doit préciser le niveau de confiance et les contrôles qui ont été effectués après l'action. Si la cause n'est pas démontrée, préférer une formule prudente et assigner l'investigation complémentaire plutôt que fermer le dossier sur une supposition.

### Cas 2 — Cause inconnue au moment de la publication

**Situation.** Les tests montrent une piste probable mais aucune preuve décisive. Le service doit être préservé et les actions doivent rester explicables. La première réaction ne doit pas consister à redémarrer ou modifier au hasard : il faut d'abord vérifier le périmètre, l'heure, l'état initial et les changements concomitants.

**Analyse.** Décrire les faits, signaler l'hypothèse avec son niveau de confiance et affecter les tests supplémentaires. Consigner les observations qui distinguent les hypothèses, puis rechercher les dépendances susceptibles de produire le même symptôme. Si une source de donnée est absente, l'indiquer et prévoir un moyen de la récupérer pour une prochaine occurrence. Vérifier aussi l'effet sur les autres services et le risque que l'action proposée crée une interruption plus large que le problème initial.

**Décision et preuve.** Versionner la conclusion si des éléments nouveaux modifient le diagnostic. La conclusion doit préciser le niveau de confiance et les contrôles qui ont été effectués après l'action. Si la cause n'est pas démontrée, préférer une formule prudente et assigner l'investigation complémentaire plutôt que fermer le dossier sur une supposition.

### Cas 3 — Rapport sensible

**Situation.** Les journaux contiennent des identifiants et des adresses internes. Le service doit être préservé et les actions doivent rester explicables. La première réaction ne doit pas consister à redémarrer ou modifier au hasard : il faut d'abord vérifier le périmètre, l'heure, l'état initial et les changements concomitants.

**Analyse.** Limiter l'accès, expurger les secrets et garder les preuves complètes dans un emplacement autorisé. Consigner les observations qui distinguent les hypothèses, puis rechercher les dépendances susceptibles de produire le même symptôme. Si une source de donnée est absente, l'indiquer et prévoir un moyen de la récupérer pour une prochaine occurrence. Vérifier aussi l'effet sur les autres services et le risque que l'action proposée crée une interruption plus large que le problème initial.

**Décision et preuve.** Valider que la copie partagée demeure utile à la décision sans divulguer les données inutiles. La conclusion doit préciser le niveau de confiance et les contrôles qui ont été effectués après l'action. Si la cause n'est pas démontrée, préférer une formule prudente et assigner l'investigation complémentaire plutôt que fermer le dossier sur une supposition.

## Exercices d'application avec corrigés

### Exercice 1 — Définir le périmètre

**Question.** Une demande décrit un problème sans identifier clairement l'actif concerné. Quelles informations obtenir avant de lancer un contrôle ?

**Corrigé expliqué.** Identifier le service, la cible, l'utilisateur, la période, l'impact, l'autorisation, les dépendances et le résultat attendu. Aucun changement ne doit précéder la confirmation de la cible. Dans le contexte de rédiger un rapport d'incident, appliquer cette réponse en reliant le raisonnement à une preuve disponible, au risque et au service concerné. L'objectif n'est pas de remplir un formulaire, mais de rendre la décision reproductible et d'éviter qu'un résultat ambigu soit transformé en certitude.

### Exercice 2 — Distinguer fait et hypothèse

**Question.** Une alerte apparaît juste après une modification. Peut-on écrire que la modification est la cause ?

**Corrigé expliqué.** Non. La proximité temporelle est un indice. Il faut comparer l'état avant/après, tester le mécanisme supposé et évaluer les autres facteurs possibles. Dans le contexte de rédiger un rapport d'incident, appliquer cette réponse en reliant le raisonnement à une preuve disponible, au risque et au service concerné. L'objectif n'est pas de remplir un formulaire, mais de rendre la décision reproductible et d'éviter qu'un résultat ambigu soit transformé en certitude.

### Exercice 3 — Choisir la mesure

**Question.** Un indicateur semble bon mais les utilisateurs signalent un problème. Quelle démarche appliquer ?

**Corrigé expliqué.** Vérifier que le point de mesure représente le service, examiner le périmètre et la fraîcheur des données, puis croiser avec un test de bout en bout et le retour utilisateur. Dans le contexte de rédiger un rapport d'incident, appliquer cette réponse en reliant le raisonnement à une preuve disponible, au risque et au service concerné. L'objectif n'est pas de remplir un formulaire, mais de rendre la décision reproductible et d'éviter qu'un résultat ambigu soit transformé en certitude.

### Exercice 4 — Protéger la production

**Question.** Une opération comporte un risque de perte de données ou d'indisponibilité. Quelles garanties vérifier ?

**Corrigé expliqué.** Autorisation, fenêtre, état initial, sauvegarde ou retour arrière adapté, prérequis, lot limité, critères de réussite, point d'arrêt et responsable du rétablissement. Dans le contexte de rédiger un rapport d'incident, appliquer cette réponse en reliant le raisonnement à une preuve disponible, au risque et au service concerné. L'objectif n'est pas de remplir un formulaire, mais de rendre la décision reproductible et d'éviter qu'un résultat ambigu soit transformé en certitude.

### Exercice 5 — Rédiger la passation

**Question.** Un autre technicien reprend l'incident en milieu d'investigation. Quelles informations minimales transmettre ?

**Corrigé expliqué.** Résumé, impact, heure, cible, faits, hypothèses testées, preuves, actions déjà effectuées, changements récents, risques, propriétaire et prochaine action proposée. Dans le contexte de rédiger un rapport d'incident, appliquer cette réponse en reliant le raisonnement à une preuve disponible, au risque et au service concerné. L'objectif n'est pas de remplir un formulaire, mais de rendre la décision reproductible et d'éviter qu'un résultat ambigu soit transformé en certitude.

### Exercice 6 — Vérifier l'efficacité

**Question.** Comment démontrer qu'une action corrective a amélioré la situation ?

**Corrigé expliqué.** Définir une référence, un indicateur, une fenêtre d'observation et un critère de réussite avant l'action ; mesurer ensuite le résultat et documenter les limites. Dans le contexte de rédiger un rapport d'incident, appliquer cette réponse en reliant le raisonnement à une preuve disponible, au risque et au service concerné. L'objectif n'est pas de remplir un formulaire, mais de rendre la décision reproductible et d'éviter qu'un résultat ambigu soit transformé en certitude.

## Glossaire opérationnel

| Terme | Définition et usage |
|---|---|
| Chronologie | Suite d'événements horodatés permettant de comprendre le déroulement du problème. |
| Impact | Conséquence sur les utilisateurs, les opérations, les données ou les engagements. |
| Contournement | Mesure temporaire qui réduit l'impact sans supprimer nécessairement la cause. |
| Cause confirmée | Explication appuyée par des preuves et des tests appropriés. |
| Action corrective | Action qui réduit la probabilité ou la gravité de la récidive. |
| Niveau de confiance | Appréciation documentée de la solidité des conclusions. |
| Preuve | Élément observable, daté et traçable qui étaye une affirmation. |
| Diffusion maîtrisée | Partage conforme au besoin d'en connaître et à la sensibilité des données. |

## Checklist de qualité avant clôture

- [ ] Le périmètre et le propriétaire de l'opération sont clairs.
- [ ] Les autorisations, prérequis et limites de la procédure ont été vérifiés.
- [ ] L'état initial et les données utiles sont datés et traçables.
- [ ] Les hypothèses sont séparées des faits et les tests sont reproductibles.
- [ ] Les modifications sont limitées au périmètre autorisé et liées à un ticket ou changement.
- [ ] Le contrôle post-action confirme le résultat technique et le service réel.
- [ ] Les écarts et incertitudes restent visibles, avec un propriétaire de suivi.
- [ ] Les informations sensibles ne figurent pas dans les copies diffusées sans nécessité.
- [ ] Le compte rendu précise la prochaine action et la date de revue si le dossier reste ouvert.
- [ ] Les apprentissages sont intégrés à la procédure lorsque l'écart peut se reproduire.

## Défi final — traiter un cas de bout en bout

Le service responsable vous signale une dégradation après plusieurs changements récents. Les données sont partielles, une mesure contredit un témoignage et la prochaine fenêtre d'intervention est limitée. Vous devez livrer un dossier que pourrait reprendre un collègue, sans multiplier les manipulations et sans promettre une résolution avant preuve.

**Travail demandé.** Rédiger le périmètre, la chronologie, trois hypothèses, les preuves associées, le test le moins risqué, la décision d'escalade éventuelle, le plan de validation, les actions de suivi et le message destiné au demandeur. Pour chaque étape, préciser les conditions qui vous feraient arrêter ou changer de stratégie.

**Correction attendue.** Le dossier commence par l'impact et les faits confirmés, puis présente les hypothèses avec des tests discriminants. Les contrôles en lecture seule précèdent les modifications. L'action choisie est autorisée, limitée et réversible dans la mesure du possible. Le résultat est vérifié par une mesure indépendante et une validation du service. Les éléments manquants restent explicitement notés. Les conclusions sont prudentes, les preuves sont accessibles et les actions restantes possèdent un propriétaire, une échéance et un indicateur d'efficacité.

## Synthèse

Une pratique intermédiaire de qualité associe connaissance technique, gestion du risque, mesure, communication et apprentissage. L'outil n'est pas la méthode : il fournit des observations ou exécute des actions, tandis que le technicien définit le périmètre, vérifie les prérequis, interprète les résultats et prend une décision proportionnée. Pour rédiger un rapport d'incident, la réussite se mesure à la fois par le résultat obtenu et par la capacité à expliquer comment ce résultat a été atteint, quelles limites subsistent et comment prévenir la récidive.
