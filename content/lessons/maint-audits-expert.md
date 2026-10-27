# Audit technique : préparation, preuves et plan d’action

> **Mise en contexte**
>
> Une revue d'exploitation révèle que plusieurs serveurs n'appliquent pas la même politique de journalisation, que les comptes d'urgence sont rarement contrôlés et que les preuves de sauvegarde sont conservées dans des dossiers différents. On te demande un audit technique avant une revue de conformité. Le risque ne vient pas seulement des écarts : il vient aussi d'un périmètre flou, de preuves non vérifiables, d'un échantillon biaisé ou de recommandations impossibles à suivre. Au niveau expert, l'audit doit produire des constats reproductibles, justifier leur criticité et permettre de vérifier l'efficacité des corrections.
>
> Un audit n'est pas une collecte indiscriminée de captures d'écran. Il doit avoir un objectif, une autorité, des critères, un périmètre et des règles de traitement des preuves. Il ne remplace pas les procédures d'urgence et ne donne pas le droit de réaliser des tests destructifs en production.

## Objectifs pédagogiques

Tu vas apprendre à construire un programme d'audit fondé sur le risque, rédiger un plan précis, protéger l'indépendance de l'évaluation, recueillir des preuves suffisamment fiables, échantillonner sans surinterpréter, formuler des constats factuels, prioriser les risques et suivre les actions jusqu'à leur vérification.

## Prérequis et limites

Il est préférable de maîtriser l'inventaire, les changements, les tickets, la supervision, la sauvegarde et les contrôles d'accès. Les audits de systèmes réglementés peuvent exiger des compétences, des critères ou des habilitations particulières. Adapte la méthode au contrat, au référentiel et aux obligations applicables. Une recommandation pédagogique ne remplace ni un avis juridique ni une norme complète.

## 1. Définir l'objectif et l'autorité

Avant la collecte, demande : pourquoi cet audit est-il réalisé ? Quel risque ou quelle décision doit-il éclairer ? Qui le demande et qui peut autoriser l'accès ? Qui accepte le risque résiduel ? Le commanditaire et la personne auditée peuvent fournir le contexte, mais ne doivent pas dicter les conclusions.

Un audit technique peut examiner la conformité d'une configuration, la qualité des opérations, la sécurité, la continuité, la gestion d'accès, le cycle de vie des actifs ou l'efficacité d'une mesure de réduction du risque. Il faut choisir un objectif observable. « Vérifier que les sauvegardes sont bonnes » est trop vague ; « déterminer si les sauvegardes des bases de données critiques sont surveillées, protégées et restaurables selon les critères approuvés » est vérifiable.

### Schéma 1 — Le cycle d'audit

~~~mermaid
flowchart TD
    A[Mandat et objectif] --> B[Périmètre et critères]
    B --> C[Plan de collecte des preuves]
    C --> D[Entretiens, observations et tests autorisés]
    D --> E[Validation des faits et des écarts]
    E --> F[Constats et évaluation du risque]
    F --> G[Rapport et plan d'action]
    G --> H[Vérification de l'efficacité]
~~~

## 2. Établir le périmètre et les critères

Le périmètre énumère les sites, actifs, processus, périodes et interfaces couverts, ainsi que les exclusions. Définis une limite temporelle : une preuve ancienne peut être utile pour étudier une tendance, mais ne démontre pas nécessairement l'état actuel. Pour des actifs critiques, indique leur identifiant d'inventaire ou une règle de sélection reproductible.

Les critères sont les attentes auxquelles les preuves seront comparées : politique interne approuvée, configuration de référence, exigence contractuelle, exigence de contrôle ou procédure validée. Distingue une obligation explicite d'une recommandation. Si le critère n'est pas clair ou ne peut pas être vérifié, note cette limitation ; ne transforme pas une préférence personnelle en non-conformité.

Le plan doit également identifier les interlocuteurs, les accès nécessaires, les périodes de changement interdites, la sensibilité des données et les tests qui exigent une autorisation séparée. Une vérification qui pourrait interrompre un service doit être reportée à un environnement adapté ou à une fenêtre approuvée.

## 3. Garantir une collecte de preuves fiable

Une preuve peut être une configuration exportée, un journal horodaté, un résultat de restauration, une mesure de supervision, un échantillon de tickets, une observation directe ou une déclaration corroborée. Sa force dépend de sa pertinence par rapport au critère, de son authenticité, de son intégrité, de sa fraîcheur et de la possibilité de la retrouver.

Les déclarations d'entretien aident à comprendre le processus, mais elles ne suffisent pas toujours à prouver son exécution. Un document de procédure prouve qu'un document existe, pas que les opérateurs l'appliquent. Une capture d'écran peut manquer de date, de contexte ou d'identification de l'actif. Lorsque c'est possible, recoupe plusieurs sources indépendantes et consigne les limites de chacune.

### Fiche de preuve

- Identifiant de preuve et lien avec le constat.
- Source, propriétaire, date et heure, fuseau et période couverte.
- Actif, environnement et configuration visés.
- Méthode de collecte, outil et version s'il y a lieu.
- Résultat attendu et observation réelle.
- Contrôles d'intégrité ou de conservation requis.
- Sensibilité, droits d'accès et règle de conservation.
- Limites d'interprétation ou informations manquantes.

N'expose pas inutilement les secrets, clés privées, jetons, données personnelles ou détails qui permettraient d'abuser d'un système. Masque-les dans la version diffusée tout en préservant, dans un espace autorisé, les éléments nécessaires à la vérification. Ne collecte pas de données au-delà du mandat.

## 4. Utiliser l'échantillonnage avec prudence

Un audit n'a pas toujours besoin d'examiner chaque actif. L'échantillonnage peut privilégier les systèmes critiques, les configurations récemment modifiées, les incidents récurrents, les actifs exposés ou un échantillon aléatoire complémentaire. Décris la méthode, la taille, la période et les raisons du choix.

Un échantillon ciblé permet de rechercher des cas à risque, mais il ne permet pas d'estimer directement la fréquence d'un écart dans toute la population. Un échantillon aléatoire peut aider à estimer une proportion, mais sa taille et sa méthode doivent être adaptées à l'objectif et à l'incertitude tolérée. Si les actifs n'ont pas tous la même criticité, divise la population par strates pertinentes au lieu de supposer qu'elle est homogène.

### Schéma 2 — Les deux usages de l'échantillon

~~~mermaid
flowchart TD
    A[Population définie] --> B{Objectif de l'audit}
    B --> C[Rechercher les cas à risque]
    B --> D[Estimer une fréquence]
    C --> E[Échantillon ciblé et limites explicites]
    D --> F[Méthode de sélection représentative]
    E --> G[Constats sur les éléments examinés]
    F --> H[Estimation avec incertitude]
~~~

Ne conclus jamais « tous les serveurs sont conformes » parce que cinq serveurs examinés sont conformes. Tu peux écrire que les cinq éléments testés satisfont le critère, et préciser ce qui reste inconnu. Un constat négatif doit également être interprété selon sa portée : une mauvaise configuration isolée ne prouve pas qu'un processus entier est défaillant, mais elle peut justifier une extension de l'échantillon.

## 5. Formuler les constats sans confusion

Un constat robuste sépare quatre éléments :

1. **Critère** : ce qui devait être respecté.
2. **Preuve** : ce qui a été observé et comment.
3. **Écart** : la différence entre le critère et la preuve.
4. **Risque ou conséquence** : l'effet possible et son niveau de criticité.

Évite les formulations vagues comme « la sécurité est mauvaise ». Préfère une constatation précise : « Sur 12 comptes privilégiés examinés dans le périmètre du site A, 3 ne disposent pas d'une revue d'autorisation datée dans la période prévue par la politique X. Les éléments consultés ne permettent pas de démontrer que leurs droits ont été recertifiés. » Cette formulation identifie le périmètre, l'échantillon et la limite de preuve.

Distingue la non-conformité confirmée, l'observation d'amélioration et la limite d'audit. Une absence de preuve peut révéler un défaut de traçabilité ou une impossibilité de conclure ; elle n'est pas toujours la preuve directe que l'action n'a jamais eu lieu. L'incertitude doit apparaître dans le rapport.

### Schéma 3 — Transformer une observation en constat

~~~mermaid
flowchart LR
    A[Critère identifié] --> B[Preuve vérifiable]
    B --> C[Comparaison explicite]
    C --> D[Écart factuel]
    D --> E[Conséquence et risque]
    E --> F[Constat rédigé]
    F --> G[Validation des faits avec le propriétaire]
~~~

La revue contradictoire sert à vérifier la justesse des faits et du contexte, pas à permettre à la personne auditée de supprimer une conclusion gênante sans preuve. Si un désaccord subsiste, documente les arguments, les preuves disponibles et la raison de la conclusion.

## 6. Évaluer la criticité et prioriser les corrections

La priorité doit s'appuyer sur des critères cohérents : impact potentiel, vraisemblance, exposition, durée, facilité de détection, possibilité de contourner le risque et criticité métier. Un écart à faible fréquence mais à conséquence catastrophique peut être prioritaire. À l'inverse, une divergence documentaire sans effet immédiat peut recevoir une action planifiée, si aucun autre critère n'impose une urgence supérieure.

Il ne faut pas inventer une précision numérique. Une grille peut employer trois ou quatre classes (critique, élevée, modérée, faible) si chaque classe a une définition et si les personnes qui évaluent l'utilisent de manière cohérente. Si une note calculée est utilisée, indique ses facteurs et ne la présente pas comme une mesure scientifique exacte.

## 7. Construire un plan d'action contrôlable

Un plan d'action doit contenir l'identifiant du constat, l'action, le responsable, l'échéance, les dépendances, les ressources, le risque réduit, la preuve attendue et le critère de fermeture. « Sensibiliser les équipes » n'est pas suffisant sans préciser le comportement visé, le support, le public, la méthode de vérification et les actions complémentaires si la lacune persiste.

Distingue la correction immédiate de la prévention durable. Par exemple, retirer les droits excessifs corrige les comptes identifiés ; mettre en place une revue périodique, une alerte d'expiration et une trace d'approbation peut réduire la probabilité de réapparition. Une mesure compensatoire peut accepter temporairement un risque, mais elle doit avoir un propriétaire, une justification, une échéance et les conditions de renouvellement ou de retrait.

### Exemple de registre

| Constat | Action | Responsable | Preuve de fermeture |
|---|---|---|---|
| Revue d'accès manquante | Recertifier les comptes échantillonnés et examiner la population restante | Propriétaire des accès | Export daté et approbations |
| Sauvegarde non restaurée en test | Réaliser une restauration contrôlée et corriger les étapes ambiguës | Responsable de la plateforme | Rapport d'essai avec critères réussis |
| Procédure obsolète | Valider une version, la publier et retirer la version retirée des points d'accès | Propriétaire de procédure | Version, approbation et contrôle de publication |

## 8. Vérifier la fermeture et l'efficacité

Une action déclarée terminée n'est pas forcément efficace. Vérifie la preuve attendue, puis mesure si le risque s'est réellement réduit. Pour une mise en place de revue des accès, vérifie la couverture, la qualité des décisions et la suppression des droits injustifiés. Pour un processus de sauvegarde, vérifie une restauration réelle et ses délais, pas seulement le statut vert du job.

Précise qui a le droit d'accepter le risque résiduel. Le responsable de l'action démontre la mise en œuvre ; l'auditeur ou la personne chargée de vérification évalue les preuves selon l'indépendance prévue. Si la preuve est insuffisante, l'action reste ouverte ou passe à une étape de correction.

### Schéma 4 — De l'action à l'assurance

~~~mermaid
flowchart TD
    A[Action déclarée terminée] --> B[Vérifier la preuve convenue]
    B --> C{Preuve complète ?}
    C -- Non --> D[Action encore ouverte ou complétée]
    C -- Oui --> E[Tester l'efficacité sur le risque visé]
    E --> F{Résultat satisfaisant ?}
    F -- Non --> G[Réviser l'action et l'échéance]
    F -- Oui --> H[Clôture traçable et risque résiduel accepté]
~~~

## 9. TP guidé : auditer un processus de restauration

**Mission.** Évaluer si une équipe peut restaurer un service critique à partir des sauvegardes définies par son processus.

1. Écris le critère : quelles données sont incluses, quelle fréquence est exigée, quels délais de reprise sont approuvés ?
2. Sélectionne les actifs selon la criticité et documente la méthode.
3. Consulte la configuration de sauvegarde, les journaux et les tickets de restauration.
4. Ne lance pas une restauration en production sans autorisation ; choisis un environnement de test approuvé.
5. Définis les résultats attendus avant l'essai : intégrité des données, accessibilité, temps et dépendances.
6. Compare les preuves au critère, formule les limites et propose les actions.
7. Rejoue un échantillon après correction pour vérifier l'efficacité.

**Critère de réussite :** le dossier permet à un autre auditeur de reconstituer l'objectif, le périmètre, la méthode, les éléments examinés, les constats et le raisonnement de priorité.

## 10. Exercices corrigés

### Exercice 1 — Preuve insuffisante

Le responsable indique que « tous les comptes sont revus chaque trimestre ». Le document de politique est à jour, mais aucun registre de revue n'est disponible. Quelle conclusion est défendable ?

**Correction.** La politique prouve qu'une règle existe, pas qu'elle est exécutée. Conclus que l'exécution n'a pas pu être démontrée à partir des éléments consultés. Examine d'autres traces autorisées et formule le constat selon le critère, sans affirmer que la revue n'a jamais eu lieu si cette absence n'est pas établie.

### Exercice 2 — Échantillon biaisé

Un auditeur sélectionne uniquement les équipements les plus faciles à joindre et conclut que 100 % de la flotte est conforme. Quel est le défaut méthodologique ?

**Correction.** La sélection peut surreprésenter les systèmes les mieux documentés ou les moins risqués. Il faut expliciter le ciblage, ne pas généraliser à l'ensemble de la flotte et, si l'objectif exige une estimation de population, construire une méthode représentative adaptée.

### Exercice 3 — Action fermée sans efficacité

Une équipe déclare l'action terminée après avoir publié une nouvelle procédure. Aucun test n'a été effectué. Peut-on clôturer le constat ?

**Correction.** La publication démontre une étape de mise en œuvre, mais pas l'efficacité. Il faut vérifier que la version approuvée est accessible, que l'ancienne est retirée, que les utilisateurs concernés peuvent appliquer la procédure et que les critères de résultat sont satisfaits.

## 11. Défi final corrigé

**Mission.** Prépare l'audit d'un ensemble de serveurs qui héberge des services importants. La direction souhaite comprendre les risques d'accès privilégiés, de sauvegarde et de traçabilité des changements.

**Correction type.** Le mandat précise le service, les critères, les périodes, les autorisations et les exclusions. Le plan choisit les actifs selon la criticité et inclut un échantillon ciblé ainsi qu'un échantillon représentatif si l'objectif nécessite une estimation. Chaque preuve est datée, liée à l'actif et protégée. Chaque constat contient critère, preuve, écart, impact et limites. Les actions ont un responsable, une échéance et une preuve de fermeture convenue. La vérification finale comprend des tests réels dans un environnement autorisé et une décision documentée sur le risque résiduel.

## Références pour approfondir

- [ISO 19011:2026 — Guidelines for auditing management systems](https://www.iso.org/standard/19011) — principes et lignes directrices relatives à l'audit des systèmes de management.
- [NIST — Computer Security Resource Center](https://csrc.nist.gov/) — publications de référence sur les contrôles et la gestion des risques.
- Les politiques internes, contrats, exigences réglementaires et procédures approuvées définissent les critères applicables au cas étudié.
