# Reporting avancé du support : piloter par les données sans tromper le métier

> **Mise en contexte**
>
> Un tableau de bord rempli de couleurs ne suffit pas à piloter un service support. Il faut des définitions stables, des données vérifiables, des indicateurs liés à des décisions et une lecture honnête des limites. Au niveau expert, le reporting sert à expliquer la performance, anticiper les risques, arbitrer les moyens et démontrer si les actions améliorent réellement le service.

## 1. Du relevé d'activité au pilotage

Un relevé indique ce qui s’est passé. Un reporting explique ce que cela signifie, où se trouve le risque, quelles hypothèses peuvent l’expliquer et quelle décision est attendue. Le support doit rendre compte à plusieurs publics : l’équipe opérationnelle a besoin de détails exploitables, le responsable de service veut voir les tendances et les capacités, la direction attend l’impact sur le métier, et les responsables techniques ont besoin d’éléments pour agir sur les causes.

Avant de choisir des graphiques, définissez la décision visée. Si personne ne peut nommer l’action qui pourrait changer grâce au chiffre, l’indicateur est probablement décoratif. Un bon rapport tient compte du contexte : nombre d’utilisateurs, volume de demandes, horaires couverts, changements récents, criticité des services et attentes convenues.

## 2. Gouvernance des métriques

Chaque indicateur doit avoir une fiche de définition avec au minimum :
- un nom non ambigu ;
- une formule écrite ;
- la population et la période couvertes ;
- la source de données et la règle d’extraction ;
- le propriétaire métier ;
- la fréquence de mise à jour ;
- les exclusions et les limites connues ;
- le seuil d’alerte et l’action attendue.

Les termes « résolution », « fermeture », « réponse », « réouverture » et « satisfaction » sont souvent utilisés différemment d’un outil à l’autre. Définissez-les avant toute comparaison historique ou inter-équipe. Un rapport peut être visuellement cohérent et néanmoins faux si son dénominateur change silencieusement.

~~~mermaid
flowchart LR
    A[Outil de tickets] --> B[Contrôles de qualité]
    C[Inventaire des services] --> D[Référentiel commun]
    E[Calendrier et SLA] --> D
    B --> F[Modèle de données]
    D --> F
    F --> G[Calcul des métriques]
    G --> H[Validation métier]
    H --> I[Dashboard et rapport]
    I --> J[Décision et action]
~~~

### Mesurer des taux correctement

Un taux de résolution dans les délais peut être défini ainsi :

~~~text
Taux de respect du délai = tickets éligibles résolus dans le délai / tickets éligibles arrivés à échéance × 100
~~~

Le mot « éligibles » doit être défini : périmètre de services, priorités, calendrier de service, pauses permises et tickets annulés. Si le numérateur compte des tickets clos tandis que le dénominateur compte toutes les demandes créées, le résultat n’est pas interprétable.

Pour comparer des équipes de tailles différentes, un volume brut est insuffisant. Complétez le nombre de demandes par un ratio pertinent, par exemple les demandes pour 100 utilisateurs actifs. Pour comparer des délais, précisez si vous utilisez moyenne, médiane ou percentile. La moyenne peut être tirée vers le haut par quelques incidents exceptionnels ; le 90e percentile montre le délai sous lequel se terminent 90 % des cas observés, selon la méthode de calcul retenue.

## 3. Construire un système équilibré d'indicateurs

Un tableau de bord de support doit éviter d’optimiser une mesure au détriment du service. Une réduction du délai moyen peut venir de fermetures précipitées, de tickets reclassés ou d’un transfert de travail vers une autre équipe. Associez donc des indicateurs de débit à des indicateurs de qualité, de récurrence et d’expérience.

| Dimension | Indicateur possible | Question de pilotage |
|---|---|---|
| Demande | Tickets reçus par catégorie et service | Où la demande augmente-t-elle ? |
| Réactivité | Temps avant première réponse utile | Les utilisateurs reçoivent-ils un premier retour pertinent ? |
| Résolution | Délai médian et P90 de résolution | Quels cas restent longs ? |
| Respect des engagements | Pourcentage de SLA respectés, par priorité | Où le risque de manquement se concentre-t-il ? |
| Qualité | Réouvertures et réaffectations | Résout-on le problème ou seulement le ticket ? |
| Prévention | Incidents récurrents, demandes évitées | Les causes durables diminuent-elles ? |
| Expérience | Satisfaction accompagnée du taux de réponse | Quelle expérience est rapportée et par qui ? |
| Capacité | Backlog, âge du backlog, charge par compétence | Le service peut-il absorber la demande ? |

Aucun indicateur ne devrait devenir une cible isolée sans garde-fou. Par exemple, la baisse du temps de première réponse doit être lue avec la qualité de cette réponse : un message automatique « nous avons reçu votre ticket » ne démontre pas une assistance utile.

~~~mermaid
flowchart TD
    A[Demande] --> B[Réactivité]
    B --> C[Résolution]
    C --> D[Qualité et absence de réouverture]
    D --> E[Expérience utilisateur]
    E --> F[Prévention et amélioration]
    F --> A
    G[Capacité et compétences] -. influencent .-> B
    G -. influencent .-> C
~~~

## 4. Qualité des données avant interprétation

Les principaux défauts sont les catégories libres et incohérentes, les horodatages manquants, les tickets dupliqués, les priorités attribuées après coup, les changements de statut non historisés et les clôtures automatiques. Créez des contrôles explicites : champs requis, listes normalisées, détection de doublons, horloge commune, conservation des changements de statut et revue d’échantillons.

Ne corrigez pas silencieusement les données. Si une règle d’exclusion est nécessaire, consignez-la et quantifiez son effet. Une correction rétroactive doit être versionnée afin que le rapport puisse être reproduit.

Distinguez les données absentes des valeurs nulles, des zéros et des cas non applicables. Un taux de satisfaction de 98 % sur dix réponses n’a pas la même représentativité qu’un taux similaire sur mille réponses. Présentez le nombre de réponses et, lorsque c’est utile, le taux de participation. N’imputez pas automatiquement les réponses manquantes.

### Taxonomie cohérente

Une taxonomie doit permettre de reconnaître le service touché, la nature de la demande, la cause connue, le symptôme, la priorité et le résultat. Ne créez pas un niveau de catégorie pour chaque anomalie ponctuelle : le référentiel deviendrait impossible à utiliser. Prévoyez une revue périodique et un propriétaire autorisé à modifier les définitions.

## 5. Analyser les tendances plutôt que commenter un seul chiffre

Une valeur mensuelle ne raconte pas toute l’histoire. Comparez une période à une période de durée équivalente, observez les semaines de pointe et identifiez les changements connus. Le nombre de tickets peut augmenter parce que le parc a grandi, qu’un nouvel outil facilite le signalement ou qu’un incident majeur a concentré la demande.

Utilisez des segments utiles : service, priorité, type de demande, canal, emplacement ou groupe d’utilisateurs. Chaque segment doit disposer d’un volume suffisant et respecter les règles de confidentialité. Pour les très petits groupes, regroupez ou masquez les détails afin d’éviter l’identification indirecte de personnes.

Les cohortes peuvent mettre en lumière des différences : utilisateurs nouvellement intégrés, applications récemment migrées ou demandes apparues après un changement. Une corrélation après un déploiement ne prouve pas à elle seule la causalité. Comparez si possible avec une période similaire ou un groupe non exposé et documentez les facteurs concurrents.

~~~mermaid
flowchart TD
    A[Variation observée] --> B[Valider la donnée]
    B --> C[Comparer des périodes équivalentes]
    C --> D[Segmenter le phénomène]
    D --> E[Examiner les changements connus]
    E --> F[Formuler plusieurs hypothèses]
    F --> G[Tester les causes avec des preuves]
    G --> H[Recommander une action mesurable]
~~~

## 6. Concevoir les rapports selon les décisions

### Rapport opérationnel quotidien

Il met en évidence les incidents critiques actifs, les tickets proches d’un engagement, les files qui vieillissent, les dépendances et les actions dont le propriétaire ou l’échéance manque. Il doit être rapide à parcourir et directement utilisable au point de passage des équipes.

### Rapport de pilotage mensuel

Il explique la demande, la qualité, les délais, le backlog, les causes récurrentes, la capacité et les actions d’amélioration. Il compare les objectifs et tendances, détaille les écarts significatifs et attribue chaque action à un propriétaire et une date de revue.

### Synthèse exécutive

Elle commence par l’impact métier, les risques majeurs, la tendance et les décisions attendues. Elle évite les longues listes de tickets et les acronymes sans explication. Un chiffre doit être accompagné de son sens : « 12 % des demandes prioritaires ont dépassé le délai convenu, principalement dans deux services pendant les incidents de réseau » est plus utile qu’un graphique sans interprétation.

~~~mermaid
flowchart TD
    A[Données contrôlées] --> B[Rapport opérationnel]
    A --> C[Analyse mensuelle]
    C --> D[Synthèse exécutive]
    B --> E[Actions immédiates]
    C --> F[Amélioration et capacité]
    D --> G[Arbitrages et risques]
    E --> H[Suivi des décisions]
    F --> H
    G --> H
~~~

## 7. Exemple chiffré corrigé

**Données fictives du mois :** 1 200 tickets éligibles sont arrivés à échéance. Parmi eux, 1 080 ont été résolus dans le délai convenu. Le backlog passe de 240 à 300 tickets. Les réouvertures passent de 6 % à 9 %. Les tickets reçus sont en hausse de 15 % et le parc géré a augmenté de 10 %.

**Calcul.** Le taux de respect du délai vaut 1 080 / 1 200 × 100 = 90 %. Le backlog a augmenté de 60 tickets, soit 25 % par rapport au point de départ. Les réouvertures augmentent de trois points de pourcentage, de 6 % à 9 %.

**Interprétation.** Le respect du délai est un résultat à analyser par priorité et service, pas un verdict unique. Le backlog grandit plus vite que le parc ; la hausse de demande doit être normalisée par utilisateur et segmentée. L’augmentation des réouvertures suggère d’examiner la qualité de diagnostic, la validation avec l’utilisateur et les clôtures, sans conclure à une cause unique avant l’analyse des cas.

**Décisions proposées.** Examiner les 20 tickets les plus anciens, extraire les catégories qui expliquent la hausse des réouvertures, comparer la charge par compétence et nommer un responsable pour chaque action. Fixer une date de revue au mois suivant.

## 8. Automatiser sans perdre la traçabilité

L’automatisation doit réduire les manipulations manuelles sans cacher les transformations. Centralisez les extractions, versionnez les requêtes, documentez le fuseau horaire et le calendrier ouvré, testez les calculs sur des cas connus et surveillez les ruptures de schéma des outils sources.

Une chaîne robuste comprend des contrôles d’entrée, des règles de transformation, des tests sur les valeurs attendues, un journal d’exécution, un horodatage de fraîcheur et un signalement si une source n’a pas été actualisée. Un tableau de bord qui n’a pas été rafraîchi doit afficher sa date de données plutôt que donner une impression de temps réel.

Contrôles pratiques : la somme des catégories doit être rapprochable du total, les dates de résolution ne doivent pas précéder la création sans justification, les SLA doivent utiliser le calendrier convenu, et les tickets annulés doivent suivre une règle stable. Comparez automatiquement les résultats avec un petit jeu de référence validé.

## 9. Confidentialité et éthique des métriques

Un rapport partagé doit montrer uniquement ce qui est nécessaire à sa finalité. Les commentaires de tickets peuvent contenir des données personnelles, des informations de sécurité ou des secrets techniques. N’exportez pas les contenus détaillés lorsqu’un identifiant agrégé suffit. Appliquez les droits d’accès, la durée de conservation et les procédures de suppression appropriées.

Ne transformez pas un rapport collectif en classement nominatif punitif sans contexte. Les différences de complexité des tickets, de compétences, d’horaires et de périmètre peuvent rendre une comparaison trompeuse. Le reporting sert à comprendre et améliorer le système ; l’évaluation individuelle nécessite une méthode distincte et transparente.

## 10. Atelier pratique : préparer une revue mensuelle

**Contexte.** Le comité constate un délai de résolution plus long et une satisfaction légèrement plus basse. Le rapport doit tenir en une page et proposer des décisions.

1. Vérifiez la fraîcheur des sources et la stabilité des définitions.
2. Comparez la demande à la période précédente et au nombre d’utilisateurs.
3. Ventilez le délai par priorité, service et catégorie.
4. Examinez les percentiles et l’âge du backlog, pas uniquement la moyenne.
5. Sélectionnez un échantillon de tickets réouverts pour identifier les motifs.
6. Présentez les faits, les hypothèses, les risques et les décisions à prendre.

**Exemple de conclusion.** « Le délai médian est stable, mais le P90 augmente fortement pour les demandes d’accès. L’analyse initiale montre des attentes liées à la validation des responsables. Nous proposons de mesurer le temps passé à chaque étape, de clarifier la délégation pour un périmètre pilote et de vérifier l’effet dans quatre semaines. Les données ne permettent pas encore de conclure que l’effectif est la cause principale. »

## 11. Exercices corrigés

**Exercice A.** Le taux de résolution dans les délais passe de 92 % à 96 %, mais le taux de réouverture passe de 4 % à 11 %. Que conclure ?

**Correction.** Les résultats sont contradictoires. Vérifiez les deux définitions, segmentez les cas, puis examinez les tickets clos rapidement et rouverts. Il est possible que la pression sur le délai favorise des clôtures trop précoces, mais cette hypothèse doit être testée.

**Exercice B.** Une équipe traite 800 tickets et une autre 400. Peut-on conclure que la première est plus productive ?

**Correction.** Non. Il faut tenir compte du périmètre, de la complexité, de la disponibilité, des effectifs, des heures de couverture et de la qualité. Un ratio normalisé peut aider, mais ne remplace pas l’analyse de la nature du travail.

## 12. Défi final corrigé

**Défi.** Concevez un reporting expert pour un support multisite : choisissez huit indicateurs maximum, définissez-les, proposez une vue opérationnelle et une vue exécutive, puis présentez une recommandation à partir d’une hausse de 20 % de la demande.

**Proposition de correction.** Retenir le volume normalisé par utilisateur, la demande par catégorie, la médiane et le P90 de résolution, le respect des SLA par priorité, l’âge du backlog, les réouvertures, les incidents récurrents et une mesure d’expérience accompagnée du taux de réponse. Chaque fiche précise formule, source, période, propriétaire et limite. Le rapport opérationnel identifie files vieillissantes et cas critiques ; la synthèse exécutive décrit l’impact, les causes probables, le risque et la décision nécessaire. Avant de réclamer un renfort, contrôler l’évolution du parc, les changements, la qualité de catégorisation et la capacité par compétence. L’action doit avoir un propriétaire, une échéance et un indicateur de vérification.

## 13. Checklist de qualité

- Les indicateurs ont une formule, un propriétaire et une source documentée.
- Les dénominateurs, périodes et calendriers sont cohérents.
- Les valeurs absentes ne sont pas confondues avec des zéros.
- Les tendances sont normalisées et segmentées avec prudence.
- Les graphiques soutiennent une décision et non un effet visuel.
- La fraîcheur des données et les limites sont visibles.
- Les accès, exports et détails sont adaptés à la confidentialité.
- Les actions sont suivies jusqu’à la vérification de leur effet.

**À retenir :** un reporting avancé ne consiste pas à afficher davantage de métriques. Il rend les chiffres fiables, explique les écarts et permet de choisir une action dont le résultat pourra être contrôlé.
