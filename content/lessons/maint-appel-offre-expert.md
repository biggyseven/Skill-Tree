# Rédaction d'appels d'offres

> **Mise en contexte — Appels d'offres et spécifications contractuelles** : Un appel d'offres robuste transforme un besoin opérationnel en exigences compréhensibles, mesurables, comparables et contractuellement exploitables. Il doit permettre aux fournisseurs de proposer des solutions réalistes tout en protégeant l'organisation contre les ambiguïtés, les coûts cachés, les dépendances techniques et les risques de livraison. Les achats de maintenance peuvent couvrir des équipements, un contrat d'assistance, un système ITSM, une migration, une prestation d'audit ou une solution de supervision. Un cahier des charges trop prescriptif réduit la concurrence ; un cahier des charges trop vague laisse au fournisseur le soin de décider ce qui sera livré. L'expert organise la consultation comme une décision gouvernée fondée sur les besoins, les critères d'évaluation, le coût complet et le risque.

## Objectifs pédagogiques

À l'issue du cours, l'apprenant sera capable de :

- transformer le besoin métier en exigences traçables et testables
- structurer un dossier de consultation sans ambiguïtés majeures
- définir critères de recevabilité, critères notés et méthode de pondération
- évaluer coût total, risques de livraison et dépendances
- préparer SLA, sécurité, réversibilité et critères d'acceptation
- organiser clarification, négociation, attribution et transition de contrat

## Prérequis et cadre de responsabilité

Le parcours s'adresse à un professionnel capable de lire les procédures, les tickets et les indicateurs du service concerné. Les décisions qui affectent la production, les personnes, les données, les finances ou les contrats doivent respecter les seuils d'autorisation de l'organisation. Les exemples du cours sont pédagogiques : adapter les cibles, les rôles et les obligations à l'environnement, au pays, au secteur et aux engagements effectivement applicables. Ne jamais remplacer une validation juridique, de sécurité, financière ou opérationnelle exigée par une hypothèse ou un exemple générique.

Avant une action importante, préciser le besoin, la portée, la personne qui décide, la preuve attendue, les risques, les conditions d'arrêt et la procédure de remontée. Si une donnée importante manque ou qu'une dépendance n'est pas confirmée, rendre cette incertitude visible et faire valider la suite par la personne habilitée.

## Vocabulaire de référence

| Terme | Définition |
|---|---|
| Sourcing | Analyse des options d'approvisionnement et des marchés disponibles avant consultation. |
| Cahier des charges | Document décrivant le besoin, les contraintes, les résultats attendus et les critères d'acceptation. |
| Exigence obligatoire | Condition de conformité qui doit être satisfaite pour que l'offre puisse être retenue. |
| Critère pondéré | Critère évalué selon une méthode et un poids annoncés. |
| SLA | Engagement de niveau de service avec mesure, fenêtre, exclusions et conséquences définies. |
| TCO | Coût total de possession sur le cycle de vie, pas seulement le prix initial. |
| BAFO | Meilleure et dernière offre lorsque cette procédure est autorisée et prévue. |
| Réversibilité | Capacité à quitter un fournisseur et transférer service, données, configurations et compétences. |

## Schémas de référence

### Schéma 1 — Objectifs et activation

~~~mermaid
flowchart TD
  A[Besoin métier] --> B[Analyse d'options]
  B --> C[Exigences mesurables]
  C --> D[Stratégie de consultation]
  D --> E[Dossier publié]
~~~

Besoin vers dossier : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 2 — Rôles et décisions

~~~mermaid
flowchart LR
  A[Besoin] --> B[Exigence ID]
  B --> C[Réponse fournisseur]
  C --> D[Critère noté]
  D --> E[Test de recette]
  E --> F[Contrat et preuve]
~~~

Traçabilité exigence : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 3 — Cartographie des dépendances

~~~mermaid
flowchart TD
  A[Critères annoncés] --> B[Échelles définies]
  B --> C[Poids et seuils]
  C --> D[Évaluation indépendante]
  D --> E[Revue des écarts]
  E --> F[Décision approuvée]
~~~

Construire une grille : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 4 — Cycle de traitement

~~~mermaid
flowchart TD
  A[Offre reçue] --> B{Recevabilité ?}
  B -->|Non| C[Décision selon règles]
  B -->|Oui| D[Évaluation technique]
  D --> E[Évaluation commerciale]
  E --> F[Clarifications autorisées]
  F --> G[Classement traçable]
~~~

Évaluation des offres : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 5 — Escalade et information

~~~mermaid
flowchart LR
  A[Prix initial] --> D[TCO sur horizon]
  B[Intégration et migration] --> D
  C[Support et évolution] --> D
  E[Sortie et risque] --> D
~~~

Coût de cycle de vie : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 6 — Validation du résultat

~~~mermaid
flowchart TD
  A[Engagement] --> B[Source de mesure]
  B --> C[Seuil et fenêtre]
  C --> D[Rapport]
  D --> E[Revue contractuelle]
  E --> F[Action ou crédit prévu]
~~~

SLA et recette : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 7 — Mesure et gouvernance

~~~mermaid
flowchart LR
  A[Exigences sécurité] --> B[Réponse fournisseur]
  B --> C[Preuve vérifiable]
  C --> D[Évaluation du risque]
  D --> E[Clause et contrôle]
~~~

Sécurité achat : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 8 — Traitement des écarts

~~~mermaid
flowchart TD
  A[Question reçue] --> B[Canal officiel]
  B --> C[Réponse approuvée]
  C --> D{Information pertinente commune ?}
  D -->|Oui| E[Partager équitablement]
  D -->|Non| F[Tracer le traitement]
~~~

Clarification : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 9 — Amélioration continue

~~~mermaid
flowchart LR
  A[Attribution] --> B[Plan de mobilisation]
  B --> C[Transfert données et accès]
  C --> D[Tests de réception]
  D --> E[Go ou plan de correction]
~~~

Transition : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

### Schéma 10 — Sortie et retour d'expérience

~~~mermaid
flowchart TD
  A[Fin de contrat] --> B[Export données]
  B --> C[Transfert configurations]
  C --> D[Validation intégrité]
  D --> E[Révocation accès]
  E --> F[Suppression attestée]
~~~

Réversibilité : le schéma rend visible la décision ou la dépendance principale. L'équipe doit vérifier que les rôles, critères et points d'arrêt correspondent à ses règles approuvées avant d'utiliser ce modèle comme procédure.

## 1. Partir du besoin et de la stratégie d'achat

La consultation commence par la question à résoudre, pas par la liste de fonctionnalités d'un produit connu. Décrire le problème opérationnel, les utilisateurs, le contexte, les volumes, les périodes de service, les actifs concernés, les résultats souhaités et les limites actuelles. Un atelier réunissant maintenance, exploitation, sécurité, architecture, finance, achats et utilisateurs clés permet de découvrir les dépendances et les critères d'acceptation. Les parties prenantes doivent ensuite distinguer les besoins réellement indispensables des préférences.

Comparer les options d'approvisionnement : faire en interne, acheter une solution standard, contractualiser un service géré, prolonger le contrat actuel, partager un service ou combiner plusieurs modalités. La décision dépend de la capacité interne, de la criticité, de la maturité du marché, de la rapidité requise, des risques de lock-in et du coût sur la durée. Une consultation prématurée peut figer la mauvaise solution ; documenter l'analyse des options avant de définir les exigences détaillées.

L'étude de marché doit être proportionnée et conduire à une spécification neutre. Les échanges préalables avec les fournisseurs sont organisés selon les règles d'équité et de confidentialité applicables. Les hypothèses sur le nombre de fournisseurs, l'innovation ou la maturité doivent être vérifiées. L'objectif est de comprendre les solutions possibles sans favoriser une entreprise par une information privilégiée ni dévoiler des données sensibles inutilement.

Définir les objectifs mesurables de la consultation : réduction d'interruptions, couverture de maintenance, amélioration de la qualité, conformité, délai de rétablissement, meilleure visibilité du parc ou baisse de TCO. Les objectifs doivent avoir une référence ou un plan de mesure. Un objectif « solution moderne » ne permet pas une évaluation objective ; un objectif lié à un résultat observable fournit une base de réception et de revue du contrat.

## 2. Rédiger des exigences testables

Une exigence doit décrire un résultat observable, une condition et un mode de vérification. Remplacer « la plateforme doit être rapide » par une cible mesurée sur un scénario, une charge, une plage de temps et des conditions de test. Remplacer « sécurité élevée » par des exigences adaptées à l'architecture, aux identités, au chiffrement, aux journaux, aux correctifs, à la réponse aux incidents et aux preuves attendues. Les seuils précis doivent venir d'un besoin approuvé et non être inventés dans le dossier.

Séparer exigences fonctionnelles, exigences non fonctionnelles, contraintes d'intégration, exigences de service, exigences de sécurité, livrables, formation, documentation et transition. Définir le périmètre de chaque obligation : quelles équipes, quels sites, quelles versions, quels horaires et quels environnements sont couverts. Une exigence qui n'a ni responsable, ni méthode d'évaluation, ni test de réception risque d'être interprétée différemment par le fournisseur et l'acheteur.

Utiliser des identifiants stables et une matrice de traçabilité. Chaque exigence est reliée à son origine, à son caractère obligatoire ou évalué, au critère de notation, à la réponse du soumissionnaire, au test d'acceptation et au propriétaire interne. Cela évite qu'une exigence critique disparaisse entre le cahier des charges, l'offre, le contrat et le plan de test. Les changements après publication doivent être gouvernés et communiqués équitablement.

Éviter les prescriptions de marque ou de solution sans justification validée. Quand l'interopérabilité impose une technologie, préciser le standard, l'interface ou le résultat requis. Prévoir les exigences de compatibilité avec les systèmes existants, la portabilité des données, les API, les formats d'export, l'accès aux logs et la possibilité de fonctionnement en mode dégradé. Ne pas supposer qu'une fonctionnalité annoncée commercialement est incluse dans le prix ou opérationnelle sans configuration.

## 3. Définir une méthode d'évaluation objective

La méthode de sélection doit être définie avant la réception des offres. Distinguer les contrôles de recevabilité, les critères éliminatoires justifiés et les critères notés. Les poids, échelles, règles d'arrondi, traitement des offres incomplètes, conditions de démonstration, seuils techniques minimaux et méthode de calcul doivent être transparents et conformes aux règles d'achat applicables. Modifier les poids après avoir vu les prix introduit un risque de biais et de contestation.

Pour chaque critère noté, écrire des descriptions de niveaux. Un score 5 doit signifier un niveau observable supérieur au score 3 ; « bon », « très bon » ou « excellent » sans définition rend les évaluateurs incohérents. Un critère peut porter sur la couverture fonctionnelle, l'approche de migration, la résilience, la sécurité, le support, la capacité de transfert, le plan de projet ou le coût de cycle de vie. Limiter les critères redondants pour éviter de compter plusieurs fois la même caractéristique.

La grille d'évaluation peut combiner prix, coût total, qualité, risque, service, transition et critères sociaux ou environnementaux lorsque la règle et le contexte le permettent. Ne pas donner deux fois du poids à un même facteur sans le savoir. La qualité d'une réponse doit être vérifiée à partir des preuves, démonstrations, références, tests ou engagements contractuels pertinents plutôt que de la qualité du graphisme commercial.

La gouvernance de l'évaluation prévoit déclaration des conflits d'intérêts, confidentialité, accès contrôlé, revue croisée et journal des décisions. Les clarifications doivent rester dans le cadre autorisé et être tracées. Les évaluateurs techniques ne doivent pas modifier seuls les critères commerciaux et les décisions d'attribution doivent suivre les seuils d'autorité de l'organisation.

## 4. Maîtriser prix, risques et contrat

Le prix initial n'est pas le coût total. Prévoir licences, souscriptions, intégration, migration, formation, support, matériel, télécommunications, environnement de test, sécurité, exploitation, montée de version, croissance des volumes, taxes et sortie du contrat. Construire des scénarios central, haut et bas avec les hypothèses explicites. Les coûts de changement, le volume de données et les mécanismes d'indexation peuvent modifier profondément le coût à cinq ans.

Les risques doivent être évalués avant attribution : capacité financière du fournisseur, dépendance à des sous-traitants, pénurie de compétences, localisation des services, concentration du marché, évolution du produit, vulnérabilités, continuité, changements de prix, propriété intellectuelle, accès aux données et difficulté de sortie. Les vérifications doivent être proportionnées à la valeur et à la criticité du contrat. Les références clients ne remplacent pas une démonstration du périmètre et des performances qui seront réellement livrés.

Le contrat traduit les engagements en obligations testables : périmètre, livrables, SLA, méthode de mesure, exclusions, escalade, communication, responsabilité, sécurité, gestion des changements, audit, assurance, sous-traitance, droits sur les données et conditions de sortie. Un SLA sans source de mesure, fenêtre de service ou traitement des exclusions donne lieu à des disputes plutôt qu'à un pilotage fiable. Les pénalités ou crédits doivent être revus juridiquement et commercialement dans le contexte local.

Définir la recette et le passage en exploitation avant de signer. Les jalons, critères de qualité, livrables documentaires, tests de performance, essais de reprise, formation, transfert de connaissances et conditions de refus doivent être mesurables. Le paiement devrait être associé aux livrables et validations prévues par le contrat selon les règles financières de l'organisation. Éviter de considérer la livraison d'un fichier ou d'une licence comme la preuve que la capacité est prête à fonctionner.

## 5. Piloter la consultation et préparer la transition

Le calendrier précise les dates de publication, questions, réponses, éventuels échanges, réception, évaluation, approbations et attribution. Les questions fournisseurs doivent passer par le canal officiel prévu afin que l'information pertinente soit partagée équitablement avec les participants concernés. Toute modification importante du dossier suit la procédure applicable et prévoit le temps nécessaire pour que les soumissionnaires répondent sur une base comparable.

Une démonstration doit être scriptée autour de scénarios identiques. L'équipe d'évaluation observe les résultats et consigne les écarts, les hypothèses et les fonctionnalités nécessitant une preuve complémentaire. Pour une solution de maintenance, demander par exemple la création d'un ordre de travail, l'association à un actif, la traçabilité d'une autorisation, la production d'un indicateur et l'export des données ; éviter de laisser le fournisseur sélectionner uniquement ses parcours les plus favorables.

Après attribution, organiser la transition comme un projet : propriétaire, plan, risques, responsabilités, inventaire des données, accès, interfaces, critères de démarrage et mode de retour arrière. Un contrat signé n'est pas la fin du sourcing. Le nouveau fournisseur doit recevoir les informations autorisées et démontrer qu'il sait exécuter le service avant la fin de la période de transition. L'ancien fournisseur peut rester nécessaire pendant une coexistence approuvée.

Préparer le passage entre fournisseur sortant et entrant dès le cahier des charges. Exiger les formats d'export, la disponibilité de documentation et de configurations, les responsabilités sur les licences, les délais d'assistance à la sortie, les règles de suppression ou restitution des données et la coopération avec un successeur. Les clauses de réversibilité sont peu utiles si elles n'ont ni critères d'acceptation ni calendrier ni coût prévu.

## Méthode opérationnelle — du diagnostic à la décision

Une démarche experte suit un enchaînement traçable. Commencer par formuler la question à résoudre et le résultat attendu, puis identifier les sources de données, les personnes concernées, les contraintes et les risques. Construire un état initial avant d'agir : période, périmètre, dépendances, règles en vigueur et qualité des données. Énoncer les hypothèses de façon à pouvoir les confirmer ou les rejeter. Préférer des contrôles qui distinguent réellement les causes possibles plutôt qu'une accumulation de vérifications sans lien avec la décision.

Avant toute décision à impact, examiner les options et les conséquences, y compris l'option de ne pas agir immédiatement. Pour chaque option, documenter bénéfices, risques, coût, dépendances, réversibilité et conditions de réussite. Choisir une action proportionnée et approuvée, assigner un responsable et une échéance, puis mesurer le résultat avec le même critère que celui défini au départ. Si une hypothèse importante est invalidée, interrompre le scénario prévu et requalifier la situation plutôt que continuer mécaniquement.

La preuve doit permettre à un collègue indépendant de comprendre ce qui a été décidé, pourquoi et à partir de quelles informations. Distinguer fait observé, déclaration, estimation, hypothèse et décision. Conserver les exceptions et résultats contradictoires qui modifient l'interprétation. Lorsque le niveau de confiance reste insuffisant, réduire la portée de la conclusion, expliquer la limitation et préciser le contrôle suivant qui permettrait de progresser.

## Mesure, gouvernance et amélioration

Chaque indicateur de pilotage doit avoir un objectif, une formule ou une méthode, une source, une période, un propriétaire, des limites et une décision associée. Un chiffre sans dénominateur, définition ou état de fraîcheur est difficile à interpréter. Contrôler la couverture de la population, les valeurs manquantes, les doublons, les changements de définition et les exclusions. Les résultats d'une action doivent être comparés à une référence crédible, avec les changements simultanés et les effets secondaires identifiés.

Ne pas optimiser un indicateur isolé au détriment du service. Une baisse de délai peut cacher des clôtures prématurées ; un gain de prix peut créer un coût de sortie très élevé ; une reprise technique peut rester inutilisable pour le métier ; une réduction d'effectifs peut concentrer une compétence critique. Associer les mesures de résultat à des indicateurs de qualité, de risque, de charge et de durabilité afin de vérifier que l'amélioration est réelle.

La gouvernance exige des responsabilités explicites. Pour chaque décision significative, noter qui propose, qui examine, qui approuve, qui exécute et qui vérifie. Une revue doit se terminer par des décisions suivies, pas uniquement par un compte rendu. Les actions comportent un propriétaire, une échéance, une preuve de réalisation et un critère d'efficacité. En cas de retard, faire apparaître le risque et demander une décision explicite sur les mesures temporaires.

## Atelier pratique — consulter un service de maintenance

### Situation de départ

Une organisation veut renouveler son service de maintenance des infrastructures. Le contrat actuel mélange support, remplacement de matériel, assistance urgente, mise à jour et formation. Les factures sont difficiles à rapprocher des volumes traités ; les SLA ne définissent pas clairement les pauses ; la migration vers un nouveau fournisseur pourrait interrompre la prise en charge. L'équipe doit créer un dossier de consultation permettant de comparer les offres sans préjuger du gagnant.

### Phase A — Besoin et options

Organiser les parties prenantes, dresser les services et volumes, établir le baseline des incidents et expliquer les limites du contrat actuel. Comparer maintien interne, nouveau marché, service géré et option hybride ; justifier la décision et ses hypothèses.

### Phase B — Cahier des charges

Rédiger exigences fonctionnelles, horaires, criticités, SLA, sécurité, reporting, compétences, livrables, transition et sortie. Pour chaque exigence, indiquer l'origine, le statut obligatoire ou noté, la méthode de preuve et le responsable métier.

### Phase C — Grille de sélection

Créer des critères pondérés avec échelles descriptives, seuils éliminatoires justifiés et règle de calcul. Simuler deux offres fictives afin de vérifier que les poids produisent un résultat compréhensible et que le prix n'est pas compté deux fois.

### Phase D — Coûts et risques

Calculer TCO sur une période approuvée, en incluant transition, licences, support, volumes, indexation, coûts de sortie et risques de dépendance. Construire au moins un scénario défavorable et les mesures de réduction.

### Phase E — Recette et transition

Définir les tests de réception, le transfert des données, les jalons d'autorisation, la coexistence, les responsabilités et les conditions de refus. Préparer le plan de clarification et la piste d'audit de la décision.

### Critères de réussite

Le livrable de l'atelier doit être reproductible, lié à des critères explicites et suffisamment clair pour être repris par une autre équipe. Les décisions non confirmées doivent rester présentées comme hypothèses. Toute action comporte ses conditions d'application, les risques, les validations nécessaires et une preuve du résultat. Le succès ne se déduit pas d'une présentation convaincante ou d'une case cochée : il se démontre avec des résultats et une revue indépendante adaptée au risque.

## Études de cas

### Cas 1 — Exigence trop vague

« Le fournisseur assurera une haute disponibilité » est remplacé par un objectif, une fenêtre de mesure, une source de données et les règles d'exclusion qui seront contractuelles.

### Cas 2 — Offre à bas prix

L'offre semble moins chère mais exclut la migration, les tests de reprise et certains appels hors horaires. Recalculer le coût complet et signaler les risques sans changer les critères après ouverture.

### Cas 3 — Dépendance propriétaire

Le service exporte les tickets dans un format fermé et facture la sortie. Traiter la portabilité, les formats, l'assistance de transition et les frais dans le dossier avant attribution.

## Exercices d'application avec corrigés

### Exercice 1 — Définir le critère

**Question.** Pourquoi faut-il écrire la méthode de notation avant de recevoir les offres ?

**Corrigé expliqué.** Pour préserver la cohérence, l'équité et l'auditabilité de la décision. Les poids, les seuils et les échelles doivent être connus à l'avance et appliqués de façon homogène.

### Exercice 2 — Interpréter les preuves

**Question.** Une offre déclare une certification mais ne fournit pas la portée du document. Que faire ?

**Corrigé expliqué.** Demander une preuve vérifiable selon le processus de clarification autorisé, contrôler l'entité et le périmètre couvert puis distinguer absence de preuve et preuve de non-conformité.

### Exercice 3 — Choisir une action

**Question.** Le prix initial est 15 % inférieur à celui d'un concurrent. Peut-on conclure que le TCO est meilleur ?

**Corrigé expliqué.** Non. Calculer licences, intégration, migration, support, évolutions, volumes et sortie sur un horizon commun avec hypothèses documentées.

### Exercice 4 — Traiter une dépendance

**Question.** Comment éviter une exigence technique trop prescriptive ?

**Corrigé expliqué.** Décrire le besoin, le résultat, les interfaces et les critères d'acceptation ; ne citer une marque ou une solution que si une contrainte justifiée et approuvée l'exige.

### Exercice 5 — Évaluer un écart

**Question.** Quel est le rôle de la recette ?

**Corrigé expliqué.** Confirmer par des tests et preuves que les livrables satisfont les critères convenus avant le passage en exploitation et le paiement ou l'acceptation correspondants.

### Exercice 6 — Vérifier l'efficacité

**Question.** Que doit contenir une clause de réversibilité exploitable ?

**Corrigé expliqué.** Données et formats restitués, documentation, configuration, délais, responsabilités, assistance, coûts connus, sécurité, suppression ou transfert et tests d'acceptation.

## Défi final — mise en situation experte

Rédiger un dossier de consultation pour l'externalisation d'un service de maintenance de 300 actifs, avec support 24/7 sur les services critiques, inventaire imparfait et migration en trois phases. Le dossier doit inclure le besoin, les exigences traçables, la grille pondérée, l'analyse TCO, les risques fournisseurs, les SLA, les critères de recette, la sécurité, la transition et la sortie. Le corrigé attendu justifie chaque critère, montre une évaluation reproductible et explicite les décisions qui nécessitent une validation achat, juridique, sécurité ou financière.

**Livrable attendu.** Produire un dossier professionnel réutilisable par une équipe qui n'a pas participé à l'exercice. Il doit inclure le contexte, le périmètre, les objectifs, les critères, les données utilisées, les rôles, les décisions, les risques, les limites, les résultats et le plan de suivi. Justifier les choix en reliant chacun d'eux à une preuve ou à une hypothèse explicitement marquée. Décrire comment vérifier l'efficacité de la réponse et ce qui déclencherait une révision de la décision.

**Correction attendue.** Une solution experte ne se contente pas de choisir une option ; elle compare les scénarios, fixe les critères avant le résultat, documente les responsabilités et signale les informations manquantes. Elle prévoit les conditions d'arrêt, les mesures temporaires, la communication, les dépendances et la vérification de fin. Le plan d'action est réaliste, ses résultats sont mesurables et le risque résiduel est soumis à une personne habilitée.


## Dossier de consultation approfondi — matrices, notation et réception

Le dossier de consultation doit relier la demande à la livraison puis à l'exploitation. Une règle de rédaction efficace consiste à examiner chaque exigence de bout en bout : qui l'a demandée, pourquoi elle est nécessaire, si elle est obligatoire ou évaluée, quelle preuve sera demandée, comment elle sera notée et comment la livraison sera acceptée.

### Exemple de matrice de traçabilité

| ID | Besoin ou source | Exigence rédigée | Statut | Preuve en consultation | Test de recette |
|---|---|---|---|---|---|
| OPS-01 | Continuité des actifs critiques | Le prestataire remet un plan de continuité documenté couvrant le périmètre nommé et les responsables de reprise | Obligatoire si approuvée comme telle | Plan et description des dépendances | Exercice ou revue selon les critères contractuels |
| DATA-02 | Traçabilité des tickets | Chaque intervention doit conserver un identifiant de ticket, d'actif, une période, un résultat et un propriétaire | Obligatoire | Exemple anonymisé et description du schéma | Échantillon de tickets de réception |
| SEC-03 | Gestion des accès | Les comptes et privilèges doivent suivre le processus d'autorisation défini par l'acheteur | Obligatoire selon le besoin approuvé | Description des contrôles et preuves autorisées | Test de rôle et vérification des journaux |
| SERV-04 | Support hors horaires | La couverture doit préciser les jours, heures, fuseaux, criticités et canaux | Notée ou obligatoire selon la stratégie | Planning, modèle d'astreinte et escalade | Scénario de demande en dehors des horaires normaux |
| EXIT-05 | Sortie de contrat | Les données et documents doivent être restitués dans des formats exploitables selon un calendrier défini | Contractuelle | Plan de réversibilité et coûts | Export, validation de complétude et lecture des données |

Les statuts de cette matrice sont à décider avec les parties compétentes. Il ne faut pas marquer toutes les exigences « obligatoires » par précaution : des critères éliminatoires injustifiés peuvent restreindre la concurrence et réduire le nombre d'offres utiles. À l'inverse, une exigence liée à la sécurité, à la continuité ou à une obligation applicable doit être évaluée explicitement.

### Exemple de grille de notation

Avant publication, le groupe peut définir des critères notés totalisant 100 points, en plus des critères obligatoires vérifiés séparément. Exemple illustratif : approche technique 30 points, qualité et gouvernance du service 25 points, coût total sur l'horizon choisi 20 points, transition et transfert de connaissances 15 points, capacité d'amélioration et de reporting 10 points. La sécurité fondamentale peut être un seuil de conformité si cette décision est justifiée par le besoin et approuvée.

Pour chaque critère, définir l'échelle. Par exemple, un score de 1 peut correspondre à une réponse qui n'explique pas la méthode ou ne fournit pas de preuve ; un score de 3 à une solution cohérente avec des hypothèses encore à confirmer ; un score de 5 à une réponse complète, adaptée au scénario, avec preuve, dépendances, critères de réussite et gestion des exceptions. Le score pondéré se calcule ensuite selon la formule annoncée : score reçu divisé par le score maximal de l'échelle, multiplié par le poids du critère. Les règles d'arrondi et de traitement des égalités doivent être fixées avant l'évaluation.

Des critères descriptifs réduisent l'effet de la préférence personnelle des évaluateurs. Chaque évaluateur note indépendamment, consigne une justification et cite la section de l'offre ou la preuve correspondante. Une réunion de consolidation discute les écarts de note sans effacer les opinions minoritaires importantes. Les conflits d'intérêts sont déclarés selon la procédure applicable. La décision finale est approuvée par l'autorité compétente.

### Questions de clarification et démonstrations

Les clarifications doivent porter sur la compréhension de l'offre dans le cadre autorisé. Tenir un registre avec la question, le destinataire, la réponse, la date, la règle utilisée et l'effet éventuel sur l'évaluation. Si une réponse fournit une information qui modifie de façon significative ce que les concurrents pouvaient proposer, consulter la fonction achats ou juridique pour déterminer le traitement approprié. Ne pas utiliser une clarification pour réécrire après coup les critères de préférence.

Une démonstration est plus informative si elle suit un scénario identique pour chaque offre. L'équipe peut demander au fournisseur de créer une demande, de la relier à un actif, de gérer une priorité, de montrer une autorisation, d'enregistrer une intervention et de produire un rapport comprenant les horodatages et les exclusions. Le test doit aussi inclure une erreur réaliste : un actif inconnu, un ticket réouvert ou un prestataire indisponible. Consigner les différences entre le comportement observé et la réponse écrite de l'offre.

### Recette, acceptation et passage en exploitation

Le plan de recette fixe les environnements, les données de test, les participants, les préconditions, les seuils et la règle de traitement des défauts. Distinguer défaut bloquant, défaut majeur accepté sous réserve et amélioration non bloquante. L'acceptation doit être prononcée par la personne habilitée ; une démonstration réussie ne suffit pas si la migration, la formation, la sécurité, les supports ou les interfaces ne sont pas livrés.

Un dossier d'attribution bien préparé fournit une piste d'audit complète : besoin, stratégie, dossier publié, questions-réponses, offres, grilles d'évaluation, contrôles de recevabilité, analyse des risques, décision, contrat et critères de recette. Cette piste doit être conservée selon les règles applicables, avec accès limité aux documents commerciaux sensibles.



## Contrôle de cohérence du dossier avant publication

Une revue de cohérence examine le dossier comme un ensemble : les exigences, le prix, la notation, le contrat, la recette et la transition doivent se soutenir mutuellement. Si le cahier des charges exige un délai de résolution de quatre heures mais que le modèle de prix ne couvre pas la garde correspondante, l'offre risque d'être non comparable ou le contrat irréaliste. Si la recette demande une fonction qui ne figure ni parmi les exigences ni dans l'offre retenue, le refus à la livraison sera contestable.

### Revue croisée des sections

| Élément | Contrôle de cohérence | Erreur fréquente |
|---|---|---|
| Besoin | Les résultats attendus sont-ils reliés à un propriétaire et à un indicateur ? | Demander des fonctionnalités sans justifier leur valeur |
| Périmètre | Les sites, horaires, volumes, actifs et interfaces sont-ils définis ? | Oublier les sites éloignés ou l'environnement de test |
| Exigences | Chaque exigence importante possède-t-elle un test ou une preuve ? | Formulations vagues ou non mesurables |
| Prix | Les volumes, options, indexations et exclusions sont-ils comparables ? | Comparer seulement un abonnement de base |
| Évaluation | Chaque critère et chaque seuil sont-ils annoncés et notables ? | Critère ajouté durant l'évaluation |
| Contrat | Les engagements, responsabilités, exclusions et recours sont-ils cohérents ? | SLA sans méthode de mesure |
| Recette | Les tests correspondent-ils aux engagements retenus ? | Attendre d'un fournisseur une fonction non contractualisée |
| Sortie | Les données, configurations et accès pourront-ils être transférés ? | Réversibilité sans calendrier ni coût convenu |

Une équipe de relecture doit comprendre les personnes qui porteront le contrat et recevront la solution. Le rédacteur seul ne peut pas confirmer que les clauses de service sont exploitables, que la sécurité est acceptable ou que les critères financiers sont comparables. La revue ne doit pas servir à enrichir le dossier de demandes tardives sans analyse : toute nouvelle exigence doit être reliée au besoin et traitée selon la gouvernance de la consultation.

### Gérer les risques liés aux hypothèses commerciales

Chaque hypothèse majeure est documentée : nombre d'actifs, taux de croissance, nombre de demandes, horaires, volumétrie de données, durée de migration, disponibilité des équipes, performance attendue et nombre de sites. Indiquer si elle provient d'une mesure, d'une estimation, du fournisseur ou d'une décision interne. Le dossier de prix peut exiger que les offres distinguent base, options, unités supplémentaires et frais de changement de volume.

Tester les scénarios qui affectent la comparabilité : croissance du parc, ajout d'un site, incident majeur, période de transition prolongée, changement de devise ou indexation des coûts. Les règles de comparaison doivent être équitables et fixées avant l'évaluation. Les hypothèses ne doivent pas être modifiées après réception dans le seul but de faire gagner une offre.

Cette revue ne remplace pas l'approbation juridique et achat ; elle permet de repérer les incohérences tôt, puis de les faire arbitrer par les fonctions compétentes. Un bon dossier est suffisamment complet pour soutenir le contrat et suffisamment lisible pour permettre aux fournisseurs de comprendre ce qui sera accepté.


## Ressources techniques et références

- [World Bank — Procurement Framework et documents types](https://www.worldbank.org/ext/en/what-we-do/project-procurement/framework)
- [UK Government — Sourcing Playbook et guides de sourcing](https://www.gov.uk/government/publications/the-sourcing-and-consultancy-playbooks)

Les documents de référence apportent des principes et des méthodes, mais leur applicabilité dépend du contexte réel. Vérifier l'édition et le statut de la source au moment de l'utiliser, surtout lorsqu'il s'agit de normes, d'exigences réglementaires ou de guides de marché. Une référence n'est pas à elle seule la preuve de conformité d'une organisation : les contrôles doivent être reliés aux exigences applicables et aux preuves recueillies.

## Synthèse

Rédaction d'appels d'offres exige une méthode qui transforme l'expérience en décisions traçables, des responsabilités claires, une analyse des risques proportionnée et des vérifications orientées résultats. Le professionnel expert documente les critères, maintient les incertitudes visibles et veille à ce que les décisions soient appliquées et contrôlées. La qualité du dispositif se mesure dans son fonctionnement réel, sa résilience aux imprévus et sa capacité à améliorer durablement les opérations.