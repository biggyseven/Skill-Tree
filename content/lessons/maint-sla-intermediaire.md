# SLA, OLA et satisfaction utilisateur

> **Mise en contexte**
>
> Un service est annoncé « disponible à 99,9 % ». Pourtant, un incident majeur a empêché les agents de travailler pendant une longue période, et le rapport mensuel indique que l'engagement est respecté. L'équipe utilise manifestement une définition de disponibilité différente de celle attendue par les utilisateurs. Les engagements de service doivent préciser ce qui est mesuré, sur quelle période, avec quelles exclusions et quelles responsabilités.

## Objectifs du cours

Tu apprendras à différencier SLA, OLA et engagement fournisseur, définir les indicateurs d'un service, interpréter des objectifs de disponibilité, distinguer prise en charge et résolution, relier les objectifs aux processus opérationnels et intégrer la satisfaction utilisateur sans réduire la qualité à un seul chiffre.

## 1. SLA, OLA et contrat fournisseur

- **SLA (Service Level Agreement)** : accord de niveau de service entre le fournisseur du service et le client ou utilisateur métier. Il définit des objectifs mesurables, leur période et les modalités de suivi.
- **OLA (Operational Level Agreement)** : accord opérationnel interne entre des équipes qui contribuent à fournir le service. Il répartit les responsabilités nécessaires pour soutenir l'engagement global.
- **Engagement fournisseur ou contrat de support :** obligation convenue avec un tiers, qui peut contribuer au service sans être identique au SLA présenté au client.

Un SLA ne doit pas promettre un résultat qu'aucune équipe ou dépendance ne peut soutenir. Les OLA aident à répartir les étapes : support, réseau, systèmes, application et fournisseur. Les objectifs internes sont souvent plus exigeants que l'engagement global pour laisser du temps à la coordination, mais ils doivent rester réalistes et définis.

## 2. Définir un indicateur mesurable

Un indicateur utile précise le service, la population, l'unité, la source, la période, la méthode de calcul, les exclusions, le responsable et la conduite à tenir si l'objectif n'est pas atteint. Les termes « rapide » ou « disponible presque tout le temps » ne sont pas mesurables.

| Indicateur | Ce qu'il décrit | Exemple de définition à préciser |
|---|---|---|
| Disponibilité | Part de la période où le service répond selon la définition retenue | Contrôle synthétique pendant les heures de service ou 24 h/24 selon le contrat |
| Temps de réponse | Délai pour accuser réception ou fournir une première réponse | Horodatages du ticket et règles de pause explicites |
| Temps de rétablissement | Temps jusqu'au retour du service selon un critère validé | Début et fin de l'interruption, vérifiés à partir des preuves |
| Taux de résolution au premier contact | Part des tickets résolus sans transfert ni nouvelle interaction selon une définition convenue | Catégories de tickets incluses et règles de réouverture |
| Satisfaction | Retour des utilisateurs sur l'expérience et la communication | Question, échelle, population et taux de réponse |

Le temps de première réponse n'est pas le temps de résolution. Un ticket peut recevoir une réponse rapide mais nécessiter une longue investigation. Le temps de rétablissement d'un service critique peut être différent de l'heure de clôture administrative du ticket.

## 3. Comprendre le calcul de disponibilité

La formule simple est :

**Disponibilité (%) = (durée de service prévue − indisponibilité comptabilisée) / durée de service prévue × 100**

La définition de « durée prévue » et des interruptions prises en compte doit être convenue. Si un SLA mesure 30 jours en continu, la durée théorique est de 30 × 24 × 60 = 43 200 minutes. Un objectif de 99,9 % correspond alors à 0,1 % d'indisponibilité, soit environ 43,2 minutes sur cette période. Ce calcul ne s'applique pas tel quel si le service n'est couvert que pendant certaines heures ou si le contrat prévoit d'autres règles.

Une moyenne peut masquer un incident très pénalisant. Un tableau de bord de disponibilité doit être accompagné d'informations sur les incidents majeurs, les utilisateurs affectés et la durée des interruptions.

## 4. Aligner les OLA et les dépendances

Imagine un service métier qui dépend du réseau, d'un serveur applicatif, d'une base de données et d'un fournisseur externe. Le SLA global est compromis si chaque équipe attend que l'autre agisse, ou si les délais internes dépassent l'objectif disponible pour le rétablissement.

~~~mermaid
flowchart TD
    A[Engagement SLA du service] --> B[OLA du support]
    A --> C[OLA réseau et systèmes]
    A --> D[OLA applicatif et données]
    A --> E[Engagement fournisseur]
    B --> F[Coordination de l'incident]
    C --> F
    D --> F
    E --> F
    F --> G[Mesures, communication et revue]
~~~

Chaque accord interne doit préciser les interfaces : qui accepte un transfert, quelles informations sont requises, qui communique, quand une escalade est déclenchée et quelles preuves valident la résolution. Un contrat fournisseur ne transfère pas automatiquement à celui-ci la responsabilité de la communication envers les utilisateurs.

## 5. Priorité et objectifs de service

Définis les objectifs selon la priorité et le type de service. Par exemple, un incident critique peut imposer une prise en charge immédiate et des mises à jour fréquentes, tandis qu'une demande standard suit une file planifiée. Les valeurs exactes doivent venir du contrat et de la politique locale.

Pour éviter les ambiguïtés, précise :
- le moment exact où le chronomètre démarre ;
- les pauses autorisées, par exemple l'attente d'une information utilisateur, si le contrat le prévoit ;
- le calendrier applicable, les jours fériés et le fuseau horaire ;
- les règles de priorité et les conditions de reclassement ;
- le critère objectif de service rétabli ;
- les exceptions prévues et leur justification ;
- le propriétaire de la mesure et la procédure de contestation.

Les pauses ne doivent pas être utilisées pour améliorer artificiellement les résultats. Toute exclusion doit être prévue, traçable et cohérente avec l'accord.

## 6. Mesurer la satisfaction sans déformer la réalité

Une enquête de satisfaction aide à comprendre si la communication, la solution et le délai ont répondu aux attentes. Elle doit être interprétée avec son taux de réponse et la population interrogée. Les personnes très satisfaites ou très mécontentes répondent parfois plus souvent que les autres.

Complète les notes de satisfaction par les réouvertures, les incidents récurrents, les délais réels et les commentaires qualitatifs. Un technicien ne doit pas pousser un utilisateur à donner une bonne note. Les commentaires doivent être traités avec respect et partagés uniquement avec les personnes autorisées.

Une mauvaise satisfaction n'implique pas toujours une mauvaise exécution technique : elle peut révéler une communication insuffisante, un contournement peu pratique ou un engagement qui ne correspond plus aux besoins du métier.

## 7. Reporting et traitement des écarts

Le rapport périodique doit présenter les objectifs, les résultats, les tendances, les incidents ayant affecté les engagements, les exceptions, les actions correctives, les propriétaires et les échéances. Le calcul doit être reproductible et provenir d'une source de données identifiée.

Lorsqu'un objectif n'est pas respecté :
1. valide les horodatages et la définition du calcul ;
2. confirme l'impact réel et les exclusions prévues ;
3. informe les parties selon le processus ;
4. cherche les facteurs contributifs et les dépendances en cause ;
5. attribue les actions et mesure leur progression ;
6. vérifie que l'amélioration produit un meilleur résultat pour l'utilisateur.

Ne modifie pas rétroactivement la définition d'un indicateur pour effacer un écart. Toute modification du SLA ou de l'OLA doit être approuvée, documentée et annoncée.

## Mise en pratique

### Laboratoire : définir un SLA et ses OLA

Choisis un service fictif, par exemple un outil de ticketing disponible durant les heures de travail ou une application métier utilisée en continu. Rédige une fiche contenant périmètre, calendrier, disponibilité cible, délais de première réponse selon la priorité, critère de rétablissement, méthode de calcul, exclusions autorisées, source des horodatages et responsable.

Établis ensuite les contributions du support, de l'équipe réseau/systèmes et de l'équipe applicative. Pour chaque OLA, indique le délai de prise en charge, le contenu d'une passation correcte, le déclencheur d'escalade et le propriétaire de la communication. Calcule un exemple de disponibilité avec des données fictives et explique les limites du résultat.

**Résultat attendu :** un engagement que deux personnes peuvent interpréter de la même manière, vérifier à partir des mêmes données et utiliser pour déclencher une action.

## Exercices corrigés

**1. Quelle différence entre SLA et OLA ?**

Correction : le SLA décrit les objectifs convenus pour le service fourni au client ou au métier ; l'OLA décrit les accords opérationnels entre équipes internes qui contribuent à cet engagement.

**2. Un ticket reçoit une première réponse en cinq minutes, mais le service reste indisponible pendant deux heures. Le délai de résolution est-il respecté ?**

Correction : cela dépend des objectifs distincts définis. La première réponse rapide ne prouve pas que le délai de rétablissement a été respecté.

**3. Quelle indisponibilité correspond à 99,9 % sur 30 jours continus ?**

Correction : 30 jours correspondent à 43 200 minutes ; 0,1 % de cette période représente 43,2 minutes. Il faut adapter le calcul au calendrier et aux règles d'exclusion convenus.

**4. Pourquoi suivre le taux de réponse d'une enquête de satisfaction ?**

Correction : parce que les réponses peuvent ne pas représenter tous les utilisateurs. Le taux et la composition des répondants aident à interpréter les notes avec prudence.

## Défi final corrigé

Un rapport affiche une disponibilité mensuelle de 99,9 %. Pourtant, plusieurs équipes ont été bloquées par un incident de deux heures. Le support affirme que son SLA est respecté parce que tous les tickets ont reçu une réponse initiale rapide.

**Correction attendue :** vérifier la définition contractuelle de disponibilité, le calendrier et les périodes incluses ; examiner les preuves et l'impact de l'incident ; distinguer disponibilité, première réponse et rétablissement ; calculer à nouveau avec la méthode approuvée ; vérifier si les engagements internes des équipes ont soutenu la cible globale ; communiquer les écarts selon le processus et attribuer des actions. Si le contrat ne couvre pas correctement l'expérience métier, proposer une révision formelle plutôt que modifier rétroactivement les règles.


## 8. Définir précisément le périmètre et les heures de service

Un engagement de disponibilité ne peut être mesuré correctement que si le service est défini. Précise le service rendu, les utilisateurs couverts, les régions ou sites concernés, les fonctions incluses, les périodes de service, les dépendances, le mode de mesure, les exclusions approuvées et le propriétaire du calcul. Une application peut fonctionner pour les utilisateurs du siège et être indisponible depuis une agence ; il faut décider si l'engagement s'applique au service global, à un site ou à une fonction critique.

La fenêtre de service change l'interprétation d'une panne. Pour une application disponible 24 h/24, une interruption de nuit peut compter au même titre qu'une interruption de jour. Pour un service de bureau ouvert de 8 h à 18 h, le temps hors de cette fenêtre peut être traité différemment si l'accord le prévoit. N'invente pas les exclusions : elles doivent être explicitement acceptées par les parties. Une maintenance planifiée ne doit pas être exclue rétroactivement simplement pour améliorer le score.

~~~mermaid
flowchart TD
    A[Accord de service] --> B[Définir service et utilisateurs]
    B --> C[Fixer fenêtre et objectifs]
    C --> D[Définir source et méthode de mesure]
    D --> E[Documenter exclusions et responsabilités]
    E --> F[Collecter résultats]
    F --> G[Calculer et revoir les écarts]
~~~

Les engagements doivent être lisibles par le métier et techniquement vérifiables. « Le système sera rapide » n'est pas un objectif mesurable. « Le 95e percentile du temps de réponse du parcours de connexion doit rester inférieur à la cible convenue pendant la fenêtre définie » peut être mesuré, à condition que le parcours, le point de mesure, la fenêtre et la méthode d'exclusion soient précisés. Une valeur de temps ne remplace pas une expérience utilisateur satisfaisante si les tests ne couvrent pas les étapes réellement utilisées.

## 9. Calculer disponibilité et budget d'indisponibilité

La disponibilité est souvent exprimée comme la proportion de temps où le service respecte les critères convenus. Une formule courante est :

Disponibilité (%) = (temps de service convenu − temps d'indisponibilité comptabilisé) / temps de service convenu × 100

Le numérateur et le dénominateur dépendent de l'accord. Il faut définir la fenêtre, l'unité, les sources et les cas d'indisponibilité partielle. Certaines organisations utilisent le nombre de requêtes réussies plutôt que la durée ; la méthode doit être documentée et ne pas être modifiée d'un mois à l'autre sans explication.

Exemple de calcul avec une fenêtre continue de 30 jours : 30 × 24 × 60 = 43 200 minutes. Pour un objectif de 99,9 %, le budget d'indisponibilité théorique est 0,001 × 43 200 = 43,2 minutes. Ce résultat suppose une couverture 24 h/24, 7 j/7, un mois conventionnel de 30 jours et aucune exclusion additionnelle. Le calcul réel doit appliquer les fenêtres et les règles du contrat.

Un taux de 99,9 % n'explique pas à lui seul l'impact. Une interruption unique de quarante minutes, une multitude de microcoupures et une panne affectant seulement les paiements peuvent produire une mesure proche, mais des conséquences différentes. Complète la disponibilité par la durée et le nombre d'incidents, l'impact métier, l'expérience utilisateur, les erreurs, la période et le contexte.

~~~mermaid
flowchart LR
    A[Définition contractuelle] --> B[Temps attendu]
    A --> C[Événements de disponibilité]
    B --> D[Appliquer fenêtre et exclusions]
    C --> D
    D --> E[Calcul reproductible]
    E --> F[Contrôle des données]
    F --> G[Résultat SLA et explication]
~~~

Un SLA peut fixer un objectif de service, mais la qualité du calcul dépend de la collecte. Vérifie les horloges, les fuseaux horaires, les changements d'heure, les trous de supervision, les doublons d'incidents, les maintenances et les changements de périmètre. Une absence de données ne doit pas être convertie arbitrairement en disponibilité ou indisponibilité : elle doit être traitée selon une règle convenue et signalée comme limite.

## 10. Réponse, rétablissement et résolution : les horloges diffèrent

Le temps de réponse peut mesurer le délai avant qu'un opérateur prenne le dossier en charge. Le temps de rétablissement indique le temps nécessaire pour restaurer le service. Le temps de résolution peut inclure l'analyse approfondie, la correction durable et le suivi. Ces horloges doivent avoir des événements de départ et de fin explicités dans l'accord. Une équipe ne doit pas présenter un accusé de réception rapide comme la preuve que le service a été restauré rapidement.

Les indicateurs MTTA, MTTR et MTBF ont des usages différents. MTTA peut mesurer le temps moyen jusqu'à la prise en charge ; MTTR est ambigu s'il n'est pas défini (repair, restore, respond ou resolve selon les organisations) ; MTBF mesure la durée opérationnelle moyenne entre des défaillances réparables. Les définitions varient : indique toujours ce que la lettre R représente, quelle population est incluse et comment les incidents réouverts sont comptés. Atlassian décrit les métriques et leurs limites dans ses ressources de gestion d'incidents : https://www.atlassian.com/incident-management/kpis/common-metrics.

Les moyennes doivent être complétées par une distribution ou des percentiles lorsque c'est utile. Une moyenne de 20 minutes peut masquer un petit nombre d'incidents qui durent plusieurs heures. Les cas extrêmes doivent être examinés au lieu de disparaître dans l'agrégat. Ne compare pas deux équipes si les périmètres, les heures d'ouverture, les niveaux de gravité ou les règles de pause des horloges diffèrent.

## 11. Aligner les SLA, OLA et contrats fournisseurs

Un SLA envers un utilisateur ou un métier dépend souvent d'engagements internes et de prestataires. Les OLA alignent les responsabilités entre équipes ; les accords fournisseurs décrivent les engagements externes. Si le service s'engage à rétablir une application en deux heures mais qu'une dépendance externe garantit seulement une réponse en huit heures, l'architecture et le plan d'escalade comportent une incohérence. Les parties doivent rendre visibles les dépendances et les marges de récupération.

Un tableau d'alignement relie, pour chaque engagement, le service métier, les composants, le groupe responsable, la source de mesure, les dépendances, l'objectif, le délai d'escalade et le recours fournisseur. Les contacts et obligations de notification doivent être révisés quand le contrat, l'organisation ou l'architecture changent. L'engagement externe ne transfère pas automatiquement la responsabilité de communication envers les utilisateurs finaux.

Les crédits de service ou pénalités éventuels ne constituent pas un objectif de fiabilité. Ils doivent être interprétés à partir du contrat approuvé, y compris les exclusions, les périodes, les limites et le processus de contestation. Le cours ne remplace pas une revue juridique ou commerciale. Les indicateurs doivent servir d'abord à comprendre le service et à corriger les risques.

## 12. Satisfaction utilisateur : mesure qualitative et quantitative

La satisfaction peut être mesurée via une question courte après le traitement, un échantillonnage, un retour du propriétaire métier ou l'analyse des réouvertures. Il faut éviter de conclure que la qualité est excellente sur la base d'une enquête à laquelle seule une petite fraction des utilisateurs répond. Précise le nombre de réponses, la période, le taux de participation, les populations concernées et les limites d'interprétation.

Les mesures quantitatives comme la disponibilité ou le délai de résolution ne décrivent pas tout. Une solution peut rétablir le service mais être difficile à utiliser ; un ticket peut être fermé rapidement avec une communication insatisfaisante. Associe donc les métriques opérationnelles à des retours qualitatifs et à des exemples. Respecte la confidentialité : les commentaires individuels ne doivent pas être affichés largement si les résultats peuvent être présentés sous forme agrégée.

~~~mermaid
flowchart TD
    A[Mesures techniques] --> D[Revue de qualité de service]
    B[Délais et tickets] --> D
    C[Retours utilisateurs] --> D
    D --> E[Identifier causes et segments]
    E --> F[Action responsable et échéance]
    F --> G[Mesure après amélioration]
~~~

Évite les enquêtes qui demandent à l'utilisateur d'évaluer une équipe pour laquelle il n'a reçu aucun service clair. Le questionnaire doit porter sur des aspects observables, par exemple clarté des mises à jour, facilité de contact et confirmation de retour. Les réponses servent à repérer des tendances, pas à tirer des conclusions individuelles sans contexte.

## 13. Travaux pratiques avancés

### TP 6 — Définir un SLA pour une application interne

Décris le service, les utilisateurs, la fenêtre, les critères de disponibilité, la réponse attendue, le délai de rétablissement, les exclusions, les dépendances, la source de mesure, les rôles et le reporting.

**Correction attendue :** les critères doivent être mesurables, la fenêtre explicite et les exclusions approuvées. Les OLA des équipes techniques doivent soutenir l'objectif global avec un délai permettant le diagnostic et la reprise. Les métriques et le périmètre sont validés par le propriétaire métier avant de devenir un engagement.

### TP 7 — Calculer un mois de disponibilité

Une fenêtre 24/7 de 30 jours comporte 38 minutes d'indisponibilité comptabilisée. Calcule le pourcentage sous la méthode temps et compare-le à l'objectif de 99,9 %.

**Correction :** temps attendu = 43 200 minutes. Disponibilité = (43 200 − 38) / 43 200 × 100 ≈ 99,912 %. Sous les hypothèses annoncées, le résultat dépasse 99,9 %. Si le contrat a une autre fenêtre, des exclusions ou une mesure par requêtes, le calcul doit être adapté.

### TP 8 — Un SLA conforme, des utilisateurs mécontents

Les indicateurs de disponibilité sont conformes, mais les utilisateurs trouvent le service lent.

**Correction :** vérifier si la mesure couvre le parcours complet, le point de sonde, les percentiles, les erreurs et les périodes d'activité. Il est possible que l'application soit techniquement joignable tout en étant difficile à utiliser. Définir une mesure de performance complémentaire, analyser les retours et faire valider la modification de l'accord si elle modifie l'engagement.

## 14. Défi final — Construire une revue de service crédible

Prépare une revue trimestrielle avec disponibilité, délais de réponse et de rétablissement, satisfaction, incidents majeurs, écarts SLA, contributions des OLA, dépendances fournisseur et actions d'amélioration. Explique quelles données restent incertaines et quelles décisions sont attendues.

**Correction détaillée :** présenter d'abord les services et impacts métier, puis la méthode de calcul et les limites, les résultats par période, les écarts documentés, la parole utilisateur agrégée et les actions avec propriétaire, échéance et preuve de réussite. Distinguer les délais d'accusé et de rétablissement, et définir les sigles MTTR utilisés. Une métrique non fiable doit être marquée comme telle ; il ne faut pas la remplacer par une estimation pour produire un graphique complet.

## 15. Sources à consulter

- PeopleCert, pratique Service Level Management : https://www.peoplecert.org/browse-certifications/it-governance-and-service-management/ITIL-1/itil-4-practitioner-service-level-management-3867
- Zabbix, configuration des services et SLA : https://www.zabbix.com/documentation/current/en/manual/web_interface/frontend_sections/services/service
- Atlassian, MTBF, MTTR, MTTA et limites d'interprétation : https://www.atlassian.com/incident-management/kpis/common-metrics
