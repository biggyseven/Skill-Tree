# Rédiger un reporting mensuel

> **Mise en contexte**
>
> À la fin du mois, la direction demande un bilan du support informatique : les interruptions, les sauvegardes, les mises à jour, le parc, les tickets en retard et les améliorations. L'équipe rassemble des captures de tableaux de bord, copie des chiffres depuis plusieurs fichiers et rédige un long message. Les nombres ne correspondent pas d'un document à l'autre, certaines données ne couvrent pas la même période et les actions du mois précédent ne sont pas reprises. Le reporting devient un exercice de mise en forme au lieu d'aider l'organisation à décider.
>
> Un reporting mensuel utile transforme des données de maintenance en une lecture fiable de l'état des services et des risques. Il doit expliquer ce qui a changé, ce qui a fonctionné, ce qui s'est dégradé, ce qui demeure inconnu et ce que l'organisation doit faire ensuite. Il ne sert ni à cacher les problèmes sous des moyennes ni à classer des techniciens sans contexte. Il fournit un langage commun entre équipes techniques, responsables de service et direction.
>
> Ce cours t'apprend à définir les audiences, collecter des données fiables, établir des métriques cohérentes, analyser les tendances, expliquer les écarts et présenter un plan d'action avec des responsables et des échéances. Les exemples numériques sont fictifs et ne constituent pas des objectifs universels ; les règles de calcul doivent être approuvées et adaptées au service.

## 1. Objectifs pédagogiques et rôle du reporting

À la fin du cours, tu dois être capable de produire un rapport mensuel lisible, réutilisable et vérifiable. Tu sauras différencier un tableau de bord opérationnel d'un reporting périodique, préciser une période et un périmètre, calculer des indicateurs avec une définition stable, détecter les limites des sources, commenter les variations sans inventer de causes, et transformer les résultats en décisions suivies.

Le reporting relie plusieurs sources : tickets et helpdesk, supervision, sauvegardes, inventaire, maintenance préventive, changements, rapports d'incident, contrats, satisfaction utilisateur et automatisation. Chaque source a sa propre définition et sa qualité. Le nombre de tickets n'est pas le nombre de pannes ; un incident majeur peut créer plusieurs tickets ; la présence d'une sauvegarde programmée ne prouve pas qu'une restauration a été validée ; un actif découvert n'est pas nécessairement géré correctement.

Le reporting mensuel répond à plusieurs questions :
- **État du service :** quelles interruptions et dégradations ont affecté les utilisateurs ?
- **Charge et performance :** quels volumes, délais et arriérés observe-t-on ?
- **Maîtrise des risques :** quelles sauvegardes, mises à jour, alertes et actions restent non conformes ?
- **Évolution :** les résultats s'améliorent-ils, se détériorent-ils ou changent-ils de périmètre ?
- **Décisions :** quels arbitrages de priorité, capacité, budget, accès ou calendrier sont nécessaires ?
- **Responsabilité :** qui réalise quelle action, pour quelle date, et quelle preuve confirmera la fin ?

Le rapport n'est pas une collection de graphiques. Chaque section doit apporter une information, une interprétation ou une décision. Les détails techniques importants restent disponibles en annexe ou par lien vers la source de vérité, plutôt que de surcharger le résumé.

## 2. Définir périmètre, période et audience

Avant de chercher des chiffres, définis la période couverte, le fuseau horaire, le périmètre technique, les services inclus, les sites, les exclusions et les lecteurs. Un mois civil n'est pas toujours identique à une période de facturation ou de service. Pour comparer deux périodes, applique les mêmes définitions ou explique clairement les changements.

Un rapport de « maintenance informatique » peut couvrir le support utilisateur, les serveurs, le réseau, les sauvegardes, la sécurité opérationnelle, le parc et les changements. Il faut distinguer les services réellement inclus de ceux qui ne remontent pas les données. Si la supervision d'un site a été interrompue pendant une journée, ne présente pas la disponibilité mensuelle comme parfaitement connue sans indiquer cette limite.

L'audience détermine la structure :
- **Direction :** impacts, risques, tendances, besoins de décision, coût ou capacité si les données sont validées.
- **Responsables de service :** objectifs, écarts SLA, dépendances, actions et échéances.
- **Équipes techniques :** détails d'incidents, causes connues ou hypothèses, mesures, changements et dette opérationnelle.
- **Audit ou conformité :** période, méthode de calcul, sources, exceptions, preuves et approbations.

Le même fait peut être présenté de façons différentes sans changer sa signification. « 27 alertes de stockage liées au volume DB-02 » est pertinent pour l'équipe technique. Le résumé exécutif dira plutôt : « Le risque de saturation de la base a augmenté ; une extension de capacité ou une réduction de rétention doit être décidée avant la date estimée. » Le rapport ne doit pas masquer la gravité, mais il doit traduire le fait en conséquence et en décision.

~~~mermaid
flowchart TD
    A[Mandat du reporting] --> B[Période et périmètre]
    B --> C[Audience et décisions]
    C --> D[Sources et définitions]
    D --> E[Contrôles de qualité]
    E --> F[Analyse des tendances]
    F --> G[Résumé et plan d'action]
    G --> H[Validation et diffusion]
~~~

## 3. Concevoir un dictionnaire d'indicateurs

Une métrique doit avoir un nom, une définition, une unité, une source, un périmètre, une fréquence, une règle de calcul, un propriétaire, des exclusions et une règle d'interprétation. Sans dictionnaire, deux personnes peuvent utiliser le même nom pour mesurer des choses différentes. Par exemple, le MTTR peut signifier réparation, rétablissement, réponse ou résolution selon l'organisation. Il faut définir précisément quelle horloge est utilisée.

Une fiche d'indicateur peut prendre cette forme :

| Champ | Exemple fictif |
|---|---|
| Nom | Temps moyen de prise en charge |
| Définition | Temps entre la création d'un incident admissible et sa première prise en charge enregistrée |
| Unité | Minutes ouvrées |
| Source | Outil de tickets |
| Périmètre | Incidents des équipes N1 et N2 |
| Exclusions | Demandes de service ; tickets de test |
| Calcul | Somme des durées définies / nombre d'incidents admissibles |
| Propriétaire | Responsable support |
| Contrôle | Comparer un échantillon de tickets et les horodatages |
| Interprétation | Examiner aussi les percentiles et les incidents les plus longs |

Distingue un compteur, un taux, une moyenne, un percentile et un objectif. Un nombre de tickets clôturés est un compteur ; une proportion de tâches terminées à l'heure est un taux ; le MTTA est une moyenne définie ; le 95e percentile montre un délai sous lequel se situent 95 % des observations, selon la méthode retenue ; un SLA est un engagement ou un objectif convenu. Ces objets ne s'interprètent pas de la même manière.

Un indicateur doit encourager la bonne décision. Le taux de clôture peut augmenter si les tickets sont fermés trop tôt, puis réouverts. Le nombre d'incidents peut baisser si leur enregistrement est incomplet. Le taux de sauvegardes « réussies » peut paraître élevé si les tâches exclues du périmètre sont oubliées. Les chiffres doivent être rapprochés de la qualité de service et de la réalité opérationnelle.

## 4. Collecter les sources sans perdre leur contexte

Identifie les sources de vérité : tickets pour les demandes enregistrées, supervision pour les mesures instrumentées, outil de sauvegarde pour les tâches, inventaire pour les actifs, registre des changements pour les modifications, et enquêtes pour les retours utilisateur. Un rapport peut réunir ces sources, mais il ne doit pas les fondre sans conserver la possibilité de remonter à l'origine.

La collecte doit préciser l'instant de l'extraction, la période couverte, les filtres et les statuts inclus. Lorsque des exports CSV ou des feuilles sont utilisés, conserve une copie contrôlée, note la version et évite les modifications manuelles non traçables. Si les données sont corrigées, indique la règle de correction et le motif. Les captures d'écran peuvent illustrer mais elles ne sont pas la meilleure source pour recalculer des mesures.

Contrôles de qualité à réaliser avant le calcul :
1. vérifier que la période et le fuseau sont cohérents ;
2. repérer les doublons, tickets de test et identifiants manquants ;
3. vérifier les valeurs nulles ou anciennes et distinguer zéro de donnée absente ;
4. rapprocher les volumes avec la période précédente et l'inventaire du périmètre ;
5. confirmer les définitions de statut, priorité et clôture ;
6. échantillonner quelques enregistrements pour vérifier que la règle de calcul correspond aux données réelles ;
7. conserver les filtres et les limites de couverture.

~~~mermaid
flowchart LR
    A[Exports des systèmes] --> B[Normaliser dates et identifiants]
    B --> C[Dédupliquer et contrôler]
    C --> D[Appliquer le dictionnaire KPI]
    D --> E[Comparer avec les sources]
    E --> F{Qualité suffisante ?}
    F -->|Non| G[Documenter l'écart et corriger]
    G --> C
    F -->|Oui| H[Analyser et publier]
~~~

N'invente pas des valeurs manquantes pour que le rapport ait l'air complet. Si le site n'a pas été instrumenté pendant une période, indique le trou. Si le propriétaire d'une action est inconnu, présente cette action comme non assignée et fais de l'affectation une décision. La transparence sur les limites donne au rapport sa crédibilité.

## 5. Structurer le reporting mensuel

Une structure récurrente permet de comparer les périodes :
1. titre, période, périmètre et date d'extraction ;
2. résumé exécutif ;
3. état des services et incidents significatifs ;
4. indicateurs et tendances ;
5. sauvegardes, maintenance et changements ;
6. risques, exceptions et données manquantes ;
7. actions du mois précédent : terminées, en retard ou bloquées ;
8. plan d'action du mois suivant ;
9. annexes techniques, définitions et références.

Le résumé exécutif doit être rédigé après l'analyse, même s'il apparaît au début. Il ne doit pas répéter toutes les sections : il présente les quelques constats majeurs, leur implication et les décisions attendues. Une structure utile est « constat / impact / action ou décision ». Par exemple : « Les échecs de sauvegarde du serveur de fichiers ont été réduits, mais le test de restauration annuel reste en retard. Le responsable stockage doit réserver un créneau de test et confirmer le résultat avant la prochaine revue. »

Le rapport doit comparer la période avec le mois précédent et, lorsque c'est utile, avec la même période de l'année précédente ou une cible approuvée. Une comparaison doit tenir compte des différences de volume, de nombre d'utilisateurs, de jours ouvrés, d'incidents majeurs et de couverture. Si le nombre de tickets augmente de 20 %, cela peut indiquer une dégradation, une amélioration du signalement, un élargissement du périmètre ou une migration. Il faut examiner les éléments avant de conclure.

## 6. Mesurer le support et les incidents

Pour les tickets, on peut suivre le volume reçu, le volume résolu, le stock ouvert, les réouvertures, les tickets en attente, l'âge du backlog et la part des tickets avec priorité élevée. Il faut éviter de considérer les clôtures de la période comme une mesure exhaustive du travail : les demandes reçues et résolues peuvent appartenir à des cohortes différentes. Un stock stable peut masquer une accumulation de dossiers très anciens ; un stock en baisse peut s'expliquer par une fermeture incorrecte.

Pour les incidents, distingue la gravité, l'impact, la durée, les services affectés, les récurrences et le statut des analyses de cause racine. Une même panne peut produire plusieurs tickets individuels ; compte les incidents selon une définition partagée et relie les tickets au dossier principal si le système le permet. Le rapport doit présenter séparément le volume de demandes et les événements majeurs.

Les indicateurs de délai doivent définir leur horloge. Le MTTA peut mesurer le temps jusqu'à l'accusé de réception ; le temps de rétablissement mesure la période jusqu'au retour du service ; le temps de résolution peut inclure les actions durables. L'acronyme MTTR est ambigu et doit être défini dans le dictionnaire. Atlassian explique l'usage et les limites de MTTA, MTTR, MTBF et MTTF : https://www.atlassian.com/incident-management/kpis/common-metrics.

Les moyennes peuvent masquer des incidents longs. Présente les médianes ou percentiles lorsque les distributions sont asymétriques, et examine les valeurs extrêmes. Un faible nombre d'incidents critiques peut être plus important qu'un grand nombre de demandes simples. Les comparaisons d'équipes ne sont pertinentes que si leurs périmètres, horaires et niveaux de gravité sont comparables.

## 7. Disponibilité, supervision et SLA

Pour la disponibilité, cite la méthode de calcul, la fenêtre de service, les exclusions convenues et le point de mesure. Un ping réussi ne prouve pas que l'application est fonctionnelle. Les trous de données doivent être signalés, et les événements doivent pouvoir être rattachés à des preuves. Si un objectif de 99,9 % est suivi, précise ce que ce pourcentage représente pour le mois en question : 24/7, heures ouvrées ou une autre fenêtre.

Les métriques de supervision peuvent inclure la disponibilité définie, les temps de réponse, la part des contrôles sans données récentes, les alertes par gravité, les faux positifs significatifs et le temps de prise en charge. Les alertes doivent être liées à une action et à un propriétaire ; une croissance du nombre d'alertes sans analyse peut simplement révéler un seuil mal réglé ou un bruit accru.

Les SLA et OLA doivent être rapprochés des résultats du service. Le reporting signale les écarts, les fenêtres de maintenance, les dépendances et les actions requises. Ne conclus pas automatiquement qu'un écart technique signifie un manquement contractuel : les règles et exclusions du contrat s'appliquent. Le rapport technique donne des preuves au propriétaire du service, qui valide l'interprétation contractuelle avec les rôles concernés.

## 8. Sauvegardes, maintenance et gestion du parc

Une section sauvegarde doit présenter la proportion de tâches conformes, les échecs répétés, les objets exclus, l'âge du dernier point récupérable, la capacité du dépôt et les tests de restauration planifiés et réussis. Les tâches qui terminent sans erreur ne suffisent pas à prouver que les données sont récupérables. Il faut différencier exécution, intégrité, cohérence et restauration validée.

La section maintenance doit distinguer le plan prévu, les tâches terminées, les tâches reportées par criticité, les exceptions approuvées et les incidents après intervention. Le nombre de tâches terminées ne prouve pas à lui seul que le risque a diminué. Si les travaux critiques sont retardés faute de pièces ou d'une fenêtre, le rapport doit demander une décision ou montrer un plan de réduction du risque.

La section parc peut montrer les actifs sans propriétaire, les agents inactifs, les doublons, les garanties à échéance, les actifs en fin de vie et les écarts d'inventaire. Pour chaque indicateur, indique le périmètre connu. Si la découverte ne couvre pas tous les segments réseau, ne présente pas l'inventaire découvert comme le parc total.

La section changement peut suivre les changements prévus et réalisés, les changements d'urgence, les retours arrière, les incidents liés dans la période et les revues non terminées. Les liens temporels ne prouvent pas toujours la causalité ; le reporting doit indiquer ce qui est confirmé et ce qui reste à examiner.

~~~mermaid
flowchart TD
    A[Résultat de sauvegarde] --> E[Vue des risques de maintenance]
    B[Tâche préventive] --> E
    C[Inventaire et cycle de vie] --> E
    D[Changements et incidents] --> E
    E --> F[Écarts et tendances]
    F --> G[Actions et décisions]
    G --> H[Suivi au mois suivant]
~~~

## 9. Analyser une tendance sans inventer de cause

Une variation montre ce qui a changé, mais ne prouve pas pourquoi. Pour interpréter, compare plusieurs périodes lorsque c'est pertinent, vérifie les changements de périmètre, observe les événements majeurs et formule des hypothèses. Utilise des mots précis : « observé », « associé dans le temps », « suspecté », « confirmé par le test » ou « non déterminé ». Ne présente pas une hypothèse comme une conclusion.

Un volume de tickets supérieur peut être lié à une panne, à l'arrivée de nouveaux utilisateurs, à une campagne de mise à jour ou à une amélioration de la déclaration. Un délai plus long peut venir de problèmes complexes, du manque de pièces, de la charge, d'un fournisseur ou d'une modification du calendrier. Pour chaque explication importante, indique la preuve qui la soutient ou la limite qui reste.

Le graphique doit montrer une unité, un axe lisible, la période, le périmètre et les valeurs manquantes. Ne coupe pas l'axe pour rendre une petite variation spectaculaire, ni n'agrège des éléments différents dans une seule moyenne si le lecteur pourrait en tirer une conclusion trompeuse. Un indicateur sans contexte peut être moins utile qu'une explication qualitative bien documentée.

## 10. Construire un plan d'action exploitable

Le reporting a de la valeur lorsque les constats conduisent à des actions. Un tableau d'action peut contenir : identifiant, constat lié, action précise, responsable, priorité, échéance, dépendance, état, preuve attendue et date de revue. Évite les verbes vagues comme « améliorer », « suivre » ou « sensibiliser » sans livrable vérifiable.

~~~mermaid
flowchart LR
    A[Constat et preuve] --> B[Évaluer risque et priorité]
    B --> C[Définir action précise]
    C --> D[Nommer responsable et échéance]
    D --> E[Définir preuve de réussite]
    E --> F[Suivi au reporting suivant]
    F --> G{Risque réduit ?}
    G -->|Non| B
    G -->|Oui| H[Clôture documentée]
~~~

Exemples :
- Constat : deux sauvegardes critiques ont échoué trois fois. Action : analyser le journal, corriger le blocage, puis vérifier deux exécutions successives et un test de restauration selon la politique.
- Constat : le stock contient des tickets de plus de 60 jours sans responsable. Action : attribuer chaque ticket ou documenter le blocage dans une campagne avec date de revue.
- Constat : les alertes du lien principal sont trop nombreuses. Action : analyser les déclencheurs, tester un ajustement sur un segment, vérifier la chaîne de notification et mesurer le taux de fausses alertes après changement.
- Constat : inventaire non fiable d'un site. Action : rapprocher l'inventaire automatique et la liste de stock, affecter les écarts et enregistrer la date de contrôle.

Le responsable d'une action n'est pas forcément le technicien qui rédige le rapport. Il doit avoir l'autorité ou la capacité d'obtenir les ressources nécessaires. Lorsqu'une action dépend d'une décision de direction, identifie clairement le décideur et la date attendue. Les actions en retard doivent rester visibles ; ne les recopie pas chaque mois sans commentaire, explique le blocage et la décision nécessaire.

## 11. Automatiser la production sans perdre la traçabilité

Une partie du reporting peut être automatisée : extraction, agrégation, calcul, génération de tableaux et création du brouillon. Mais il faut protéger les sources, stabiliser les définitions et contrôler la sortie. L'automatisation peut répéter rapidement une erreur de filtre ou de date si elle n'est pas testée.

Utilise des formats structurés quand ils existent, conserve les paramètres d'extraction et sépare les données brutes des transformations. Les calculs doivent être reproductibles. Les corrections manuelles doivent être identifiées, justifiées et revues. Les données sensibles doivent être minimisées avant diffusion. La version destinée à la direction peut être différente de l'annexe technique, tout en provenant des mêmes chiffres validés.

Une procédure de génération peut :
1. figer la période et le périmètre ;
2. extraire les sources ;
3. contrôler les doublons, trous et valeurs anormales ;
4. calculer les indicateurs définis ;
5. comparer avec les périodes précédentes et objectifs ;
6. générer les graphiques et tables ;
7. rédiger un brouillon d'interprétation ;
8. faire valider les chiffres et le récit par le propriétaire ;
9. publier avec liens, date et version ;
10. archiver le rapport et les données d'entrée selon la politique.

L'automatisation ne doit pas envoyer un rapport non validé à un groupe large uniquement parce qu'un cron a réussi. Prévois une revue humaine pour les écarts importants, les données incomplètes et les conclusions qui pourraient conduire à une décision financière, contractuelle ou de sécurité.

## 12. Travaux pratiques guidés

### TP 1 — Créer un dictionnaire KPI

Définis au moins huit indicateurs couvrant le support, la disponibilité, la sauvegarde, la maintenance, le parc et les changements. Pour chacun, écris la formule, le périmètre, la source, la fréquence, les exclusions, le propriétaire et les contrôles.

**Correction attendue :** les métriques ont une définition stable et des sources qui permettent de recalculer le chiffre. Le MTTR doit avoir une signification explicite. Le nombre de sauvegardes terminées doit être séparé du nombre de restaurations réussies. Les données manquantes sont identifiées au lieu d'être supposées conformes.

### TP 2 — Contrôler un export de tickets

Un export contient 450 lignes, mais certaines lignes sont des tickets de test, des doublons ou des demandes de service. Explique comment tu prépares le comptage mensuel.

**Correction attendue :** appliquer les filtres documentés, identifier la clé utilisée pour repérer les doublons, séparer incidents et demandes selon les règles, vérifier la période de création ou de clôture selon l'indicateur, puis comparer un échantillon avec l'outil source. Conserver les paramètres de filtre.

### TP 3 — Analyser une hausse de 30 %

Le nombre de tickets augmente de 30 % et le délai moyen de prise en charge baisse. Rédige une analyse prudente.

**Correction attendue :** les deux évolutions doivent être rapportées, mais elles n'expliquent pas à elles seules la cause. Vérifier le périmètre, les types de tickets, la période, les changements de déclaration et la distribution des délais. Indiquer les hypothèses et les tests nécessaires avant une conclusion.

### TP 4 — Reporting des sauvegardes

Présente trois tâches en erreur, un test de restauration manquant et un dépôt qui approche du seuil de capacité.

**Correction attendue :** différencier le résultat des tâches, l'âge du dernier point récupérable, la validation de restauration et la capacité. Nommer les services touchés et proposer des actions avec responsables et échéances. Éviter le simple indicateur « 97 % de succès » sans périmètre.

### TP 5 — Résumé exécutif

À partir de résultats fictifs, écris cinq lignes présentant l'état du service, le risque principal, la tendance, les limites de données et une décision attendue.

**Correction attendue :** le texte doit être court, factuel, orienté décision et cohérent avec les tables techniques. Il ne doit pas annoncer une cause non confirmée ni cacher un risque majeur dans une annexe.

## 13. Exercices corrigés

### Exercice 1 — Une moyenne rassurante

Le délai moyen de résolution baisse, mais trois incidents critiques ont duré plusieurs heures.

**Correction :** présenter la moyenne avec le nombre et la gravité des cas, puis examiner la distribution et les incidents longs. La moyenne peut masquer un risque métier important. Les actions doivent se fonder sur les causes et les impacts des cas critiques.

### Exercice 2 — Données manquantes

La supervision d'un site n'a envoyé aucune donnée pendant huit heures, et le rapport indique 100 % de disponibilité car aucune alerte n'existe.

**Correction :** l'absence d'alerte n'est pas une preuve de disponibilité lorsque la collecte est interrompue. Signaler la fenêtre comme donnée manquante, chercher la cause de l'absence et appliquer la règle de calcul convenue. Un contrôle de fraîcheur permet de rendre ce défaut visible.

### Exercice 3 — Clôture en masse

Le taux de clôture augmente après une fermeture automatique de tickets sans confirmation utilisateur.

**Correction :** la métrique peut être artificiellement améliorée. Séparer clôture technique, confirmation du besoin et réouverture. Évaluer un échantillon et définir les critères de clôture. Les résultats doivent décrire la qualité, pas seulement le volume.

### Exercice 4 — Comparaison entre équipes

L'équipe A résout plus de tickets que l'équipe B.

**Correction :** ne pas en conclure que A est plus performante sans comparer le périmètre, la complexité, les horaires, les types de demande, l'effectif et les critères de clôture. Le volume doit être mis en relation avec la qualité, le stock restant et les retours utilisateurs.

### Exercice 5 — Rapport incomplet mais envoyé à temps

Le reporting est envoyé à la date prévue, mais les chiffres de sauvegarde n'ont pas été validés.

**Correction :** un délai respecté ne remplace pas la qualité. Le rapport doit signaler l'indicateur non validé, le propriétaire de la source, le risque et la date prévue de correction. Une version corrigée doit être identifiée si le chiffre publié change.

### Exercice 6 — Actions sans responsable

Trois mois de suite, les mêmes actions figurent dans le plan sans responsable défini.

**Correction :** le reporting doit faire apparaître le manque d'ownership comme un blocage. Demander une décision d'affectation, préciser les rôles nécessaires et la date de décision. Le simple copier-coller d'une action ne constitue pas un suivi.

## 14. Défi final corrigé — Construire le reporting d'une PME

Une PME de 80 personnes dispose d'un helpdesk, d'un réseau multi-site, d'une application de facturation, d'un inventaire et d'une plateforme de sauvegarde. Tu dois produire un reporting mensuel après une période comprenant un incident majeur, deux échecs de sauvegarde, une opération de maintenance reportée et un nettoyage de parc.

### Travail demandé

1. définir la période, le périmètre et les lecteurs ;
2. créer le dictionnaire de dix KPI ;
3. extraire et contrôler les données de tickets et de supervision ;
4. calculer disponibilité, délais et stock, en documentant les limites ;
5. analyser les sauvegardes, la maintenance et les écarts d'inventaire ;
6. écrire un résumé exécutif et un tableau d'action ;
7. définir qui valide le rapport et quand les actions seront revues.

### Correction détaillée

Le rapport commence par la période, le périmètre, les sources et la méthode. Le résumé présente l'incident majeur, la disponibilité selon la règle convenue, l'état des sauvegardes et la maintenance reportée. Il distingue les faits établis de l'analyse encore ouverte. Les échecs de sauvegarde sont rapprochés de l'âge des points récupérables et du test de restauration, et non seulement du nombre de jobs. La tâche préventive reportée est associée à un risque et une décision attendue. Le nettoyage de parc montre les actifs concernés, la méthode de rapprochement et les écarts restants.

Le tableau d'actions contient un responsable, une échéance, une priorité et une preuve de succès. Les actions des périodes précédentes sont montrées avec leur état actualisé. Les indicateurs sont vérifiés par leurs propriétaires ; les trous de données sont explicités. Le rapport est ensuite approuvé et archivé selon la procédure. Le mois suivant, l'équipe vérifie les actions réalisées et la tendance, sans supposer qu'une amélioration est due à une seule action si les preuves ne l'établissent pas.

### Barème indicatif

- 15 % : périmètre et sources précisés ;
- 20 % : définitions et calculs reproductibles ;
- 15 % : qualité des données et limites ;
- 15 % : interprétation factuelle des tendances ;
- 15 % : lien entre indicateurs et risques métier ;
- 15 % : actions avec responsables et preuves ;
- 5 % : clarté du résumé et maîtrise de la confidentialité.

## 15. Checklist avant diffusion

- période, fuseau horaire et périmètre inscrits ;
- audience et décisions visées identifiées ;
- définitions des indicateurs disponibles ;
- sources et dates d'extraction vérifiables ;
- doublons, filtres et données manquantes contrôlés ;
- valeurs comparées à une période et une base cohérentes ;
- hypothèses séparées des faits ;
- impacts métier validés avec les propriétaires ;
- actions anciennes mises à jour ;
- nouvelles actions affectées à un responsable ;
- secrets et données personnelles minimisés ;
- résumé cohérent avec les annexes ;
- rapport approuvé, versionné et archivé.

## 16. Sources utiles

- Atlassian, métriques d'incident MTTR/MTTA/MTBF : https://www.atlassian.com/incident-management/kpis/common-metrics
- PeopleCert, Service Level Management : https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil-4-practitioner-service-level-management-3867
- Zabbix, définition des services et SLA : https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/services/service
