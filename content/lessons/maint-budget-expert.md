# Budgétisation et calcul du ROI — niveau expert

> **Mise en contexte —** Un budget n'est ni une simple liste de dépenses ni une prévision que l'on met à jour uniquement quand le financement manque. C'est un modèle explicite des ressources, des coûts, des résultats attendus, des risques et des arbitrages. Une décision d'investissement doit expliquer ce que l'organisation cherche à obtenir, quelles alternatives existent, combien elles coûtent sur leur durée de vie, quels bénéfices peuvent être attribués à l'investissement, quand ces bénéfices apparaîtront et dans quelles conditions la décision cesserait d'être pertinente. Le niveau expert consiste à construire des estimations vérifiables, distinguer comptabilité et trésorerie, comparer les flux à des dates cohérentes, prendre en compte l'incertitude et suivre la valeur réellement obtenue après la dépense. Un ROI élevé sur une hypothèse optimiste n'est pas une preuve de valeur ; une VAN positive ne rend pas acceptable un risque critique non maîtrisé ; un projet obligatoire à ROI financier faible peut rester nécessaire pour la sécurité, la conformité ou la continuité.

## Objectifs de maîtrise

À la fin de ce cours, l'apprenant doit pouvoir :

- traduire les objectifs métier en hypothèses budgétaires, résultats attendus et critères d'arbitrage ;
- distinguer budget, prévision, engagement, dépense réelle, flux de trésorerie et coût comptable ;
- construire un coût total de possession (TCO) sur un horizon défini, avec coûts directs, indirects, récurrents, de transition et de sortie ;
- distinguer CAPEX et OPEX selon les règles comptables applicables, sans confondre classification comptable et flux économique ;
- préparer une estimation traçable, documenter les sources, la maturité, les hypothèses et les marges de risque ;
- calculer et interpréter le ROI, le délai de récupération, la valeur actuelle nette (VAN), le taux de rendement interne (TRI) et le seuil de rentabilité ;
- choisir une méthode de comparaison cohérente avec l'horizon, le risque, la temporalité des flux et l'objectif de la décision ;
- éviter le double comptage des économies, des bénéfices, du temps libéré et des coûts évités ;
- analyser les scénarios optimiste, central et prudent, ainsi que les sensibilités et les valeurs de bascule ;
- comparer les options « ne rien faire », « faire le minimum », « améliorer l'existant », « acheter », « internaliser » et « externaliser » ;
- relier un business case aux priorités, à la capacité, à la continuité, à la sécurité, aux fournisseurs et aux risques opérationnels ;
- construire un budget opérationnel, un plan d'investissement, une prévision glissante et une analyse d'écarts ;
- distinguer économies de trésorerie, réduction de coûts, gain de capacité, bénéfices qualitatifs et bénéfices réellement encaissables ;
- organiser la gouvernance des investissements, les seuils d'autorisation, les contrôles indépendants et la gestion des changements ;
- planifier la réalisation des bénéfices, nommer les responsables, définir les mesures avant/après et vérifier l'effet après mise en service ;
- présenter à la direction une recommandation transparente, avec hypothèses, risques, options, limites et conditions d'arrêt.

La maîtrise experte ne consiste pas à produire le plus grand modèle Excel. Elle consiste à fournir assez de détails pour que la décision soit fiable, à expliquer ce qui reste incertain et à éviter qu'un calcul exact en apparence masque des hypothèses fragiles.

## Prérequis et cadre de responsabilité

Le cours s'inscrit après « Management d'une équipe technique ». La budgétisation dépend en effet de la capacité réelle, des compétences disponibles, des priorités et des décisions de l'équipe. Un investissement peut réduire une dépense tout en augmentant la charge de maintenance, la dépendance fournisseur ou le besoin de compétences internes. Ces effets doivent apparaître dans le modèle.

Les calculs proposés sont pédagogiques. Le traitement comptable de CAPEX/OPEX, la fiscalité, la déductibilité, les règles d'immobilisation, les taux d'actualisation, les obligations de financement et les seuils d'autorisation dépendent du pays, du secteur, du référentiel comptable et de la politique de l'organisation. Les exemples ne remplacent pas l'avis du contrôle de gestion, de la comptabilité, de la fiscalité, des achats ou du juridique lorsque leur intervention est nécessaire.

Toujours distinguer :
- une donnée observée d'une estimation ;
- un coût engagé d'une dépense déjà payée ;
- un bénéfice théorique d'un bénéfice vérifié ;
- un gain économique d'une économie encaissable ;
- une décision financière d'une décision de conformité ou de sécurité ;
- le résultat d'un modèle de sa précision réelle.

Un business case est un support de décision, non un moyen de justifier après coup une option déjà choisie. Les hypothèses doivent être exposées suffisamment tôt pour permettre une contestation constructive.

## 1. Comprendre le budget comme un modèle de décision

### 1.1 Budget, prévision, engagement et réalisé

Ces notions se ressemblent dans les tableaux financiers mais répondent à des questions différentes.

| Notion | Question | Exemple |
|---|---|---|
| Budget approuvé | Quelle enveloppe et quelle finalité ont été autorisées ? | 80 000 unités monétaires prévues pour moderniser la supervision |
| Prévision (forecast) | Où estime-t-on finir compte tenu des informations actuelles ? | Coût révisé à 92 000 après découverte d'une interface supplémentaire |
| Engagement | Quelle somme est contractuellement réservée ou promise ? | Bon de commande signé pour 45 000 |
| Réalisé comptable | Quel montant a été comptabilisé sur la période selon les règles de l'organisation ? | Facture de 12 000 imputée au projet |
| Trésorerie | Quelle somme est effectivement payée et à quelle date ? | Paiement de 12 000 prévu le mois suivant |
| Coût à terminaison | Quelle dépense totale estime-t-on à la fin du projet ? | Dépenses comptabilisées, engagements restants et travail restant estimé |
| Écart budgétaire | Quelle différence existe entre une base de comparaison et le résultat ? | Prévision à terminaison moins budget approuvé |

Il faut définir le signe des écarts dans le modèle. Une valeur positive peut représenter un dépassement dans un fichier et une économie dans un autre. Une analyse professionnelle explique aussi la cause, le caractère ponctuel ou structurel, l'effet sur la prévision et la décision requise.

Un budget autorisé n'est pas une invitation à dépenser toute l'enveloppe. Inversement, une dépense inférieure au budget n'est pas automatiquement une réussite : le projet peut avoir livré moins de fonctionnalités, reporté une dépense indispensable ou déplacé le coût vers une autre équipe.

### 1.2 Relier l'argent à un résultat

Avant de bâtir les lignes, préciser le problème à résoudre. Pour un service de maintenance, les questions peuvent porter sur les incidents répétés, le temps de rétablissement, le vieillissement des équipements, la capacité de l'équipe, le risque de perte de données, la fin de support d'un produit ou les coûts de prestation. Le budget doit relier ces causes aux interventions envisagées et aux résultats attendus.

Un bon cadrage mentionne :
- la situation de référence et sa source ;
- le résultat métier ou opérationnel recherché ;
- le périmètre inclus et exclu ;
- les options étudiées ;
- les hypothèses de volume, de prix et de calendrier ;
- les dépendances internes et externes ;
- les risques de ne pas agir ;
- la manière dont le bénéfice sera mesuré ;
- l'autorité responsable de l'arbitrage.

Un budget qui ne comporte que des catégories de dépenses peut être utile pour le suivi comptable, mais ne suffit pas à démontrer la valeur d'un investissement. Relier chaque enveloppe importante à un résultat, un risque ou une obligation.

### 1.3 Les options de référence

Toute évaluation devrait envisager une référence comparable. Les options peuvent inclure « ne rien faire », « faire le minimum nécessaire », améliorer les outils actuels, remplacer un composant, acheter une solution, développer en interne, externaliser, mutualiser ou phaser l'investissement.

L'option « ne rien faire » n'a pas nécessairement un coût nul. Elle peut entraîner des incidents, du temps perdu, une fin de support, un risque de non-conformité, une dépendance à des personnes clés ou des coûts de maintenance croissants. Ces conséquences doivent être estimées avec la même rigueur que les coûts de l'investissement.

L'option minimale permet de distinguer ce qui est obligatoire de ce qui apporte une valeur supplémentaire. Elle peut aussi fournir une alternative si le budget complet n'est pas disponible. Les options ne doivent pas être volontairement caricaturales : chacune doit être assez réaliste pour soutenir une décision honnête.

~~~mermaid
flowchart TD
  A[Problème ou opportunité] --> B[Situation de référence]
  B --> C[Ne rien faire / minimum nécessaire]
  B --> D[Améliorer l'existant]
  B --> E[Remplacer, acheter ou développer]
  B --> F[Option hybride ou phasée]
  C --> G[Coûts, bénéfices, risques et faisabilité]
  D --> G
  E --> G
  F --> G
  G --> H[Comparaison cohérente]
  H --> I[Recommandation et conditions de décision]
~~~

La comparaison doit utiliser un périmètre, un horizon et des hypothèses cohérents. Ne pas comparer un prix d'achat d'une option à cinq ans de coût total d'une autre sans rendre le décalage explicite.

### 1.4 Budget annuel et décision pluriannuelle

Le budget annuel organise l'autorisation et le suivi des dépenses sur une période. La décision d'investissement doit souvent étudier plusieurs années : le coût initial peut être faible alors que les renouvellements, le support, la consommation ou la sortie sont coûteux ; à l'inverse, une dépense initiale élevée peut générer des bénéfices sur la durée.

Distinguer la période budgétaire de l'horizon économique. Une organisation peut autoriser la première année tout en évaluant la valeur sur cinq ans. Le dossier doit montrer les conséquences au-delà de la période financée, les dépenses récurrentes à prévoir et les hypothèses sur lesquelles repose la poursuite du service.

### 1.5 Gouvernance et responsabilités

La qualité financière exige plusieurs regards. Le propriétaire métier définit le résultat, les opérations vérifient la faisabilité, l'équipe technique estime les efforts, les achats évaluent le marché, la finance contrôle les hypothèses et les règles, la sécurité examine les risques pertinents, et l'autorité désignée décide. Un seul auteur peut construire le fichier, mais ne devrait pas être le seul à valider ses hypothèses critiques.

Le dossier précise qui :
- possède l'objectif et le bénéfice ;
- construit et actualise l'estimation ;
- valide les prix, volumes et règles comptables ;
- accepte le risque résiduel ;
- approuve l'engagement ;
- contrôle le coût à terminaison ;
- vérifie les bénéfices après la mise en service.

La séparation des rôles doit être proportionnée. Pour une dépense modeste, une validation simplifiée peut suffire ; pour une dépense stratégique ou difficilement réversible, une revue indépendante, une analyse détaillée et des jalons de décision sont justifiés.

## 2. Construire un coût total de possession fiable

### 2.1 Le TCO : périmètre et horizon

Le coût total de possession (TCO, *Total Cost of Ownership*) agrège les coûts pertinents sur un horizon défini pour acquérir, déployer, utiliser, maintenir et sortir une solution. Il ne s'agit pas d'une liste universelle : les éléments dépendent de l'actif et du modèle opérationnel.

Pour un outil logiciel ou une plateforme technique, examiner notamment :
- licences, abonnement, droits d'usage et indexation ;
- matériel, hébergement, réseau, énergie, stockage et sauvegarde ;
- conception, installation, intégration, migration, tests et bascule ;
- travail interne de projet, architecture, sécurité, exploitation et gestion ;
- formation, documentation, transfert de connaissances et conduite du changement ;
- maintenance corrective et préventive, support, astreintes et pièces ;
- supervision, journalisation, audits, conformité et gestion des vulnérabilités ;
- montées de version, extensions, croissance de volumes et renouvellements ;
- incidents, interruptions, reprise, récupération de données et remédiation ;
- sortie fournisseur, export, migration future, transfert et suppression contrôlée.

Tous les postes ne doivent pas nécessairement apparaître dans chaque dossier. Il faut néanmoins expliquer pourquoi un coût matériellement important est exclu ou traité séparément. Un TCO n'est comparable que si les options incluent des services et des limites comparables.

### 2.2 Direct, indirect, récurrent et ponctuel

Les coûts directs sont directement attribuables à la solution ; les coûts indirects sont partagés ou plus difficiles à affecter. Les coûts ponctuels apparaissent une fois ou lors d'un changement ; les coûts récurrents reviennent pendant l'exploitation. Un coût peut être direct et récurrent, ou indirect et ponctuel.

Les coûts internes sont souvent oubliés parce qu'ils ne créent pas de nouvelle facture. Le temps d'un ingénieur mobilisé sur une migration a un coût d'opportunité : il ne peut pas simultanément traiter le backlog, maintenir la documentation ou réaliser un projet différent. Toutefois, ne pas facturer ce temps additionnel ne signifie pas qu'il doit être valorisé deux fois. Le modèle doit définir s'il utilise des coûts de trésorerie, un coût économique complet ou une approche mixte, et éviter les doubles comptes.

### Schéma — Cartographier les coûts sur tout le cycle de vie

~~~mermaid
flowchart TD
  A[Décision d'acquisition] --> B[Coût initial]
  B --> C[Déploiement et migration]
  C --> D[Exploitation récurrente]
  D --> E[Maintenance, support et sécurité]
  E --> F[Évolution et renouvellement]
  F --> G[Sortie, transfert et suppression]
  B --> H[Coûts internes et risques]
  C --> H
  D --> H
  E --> H
  F --> H
  G --> H
  H --> I[TCO sur horizon et hypothèses définis]
~~~

Le total doit inclure les postes pertinents sans compter deux fois un même effort. Les incertitudes matérielles restent visibles dans une plage ou un scénario au lieu d'être remplacées par un coût nul.

### 2.3 Exemple de registre TCO

| Poste | Type | Pilote | Source de l'estimation | Période | Risque / hypothèse |
|---|---|---|---|---|---|
| Achat ou abonnement | Direct, initial ou récurrent | Achats / finance | Offre valide et prix contractuel | Par année | Indexation, devise, taxes |
| Intégration | Direct, initial | Projet / technique | Estimation par activité | Mise en œuvre | Interfaces non découvertes |
| Migration | Direct, ponctuel | Technique / métier | Volumes et méthode | Transition | Qualité des données |
| Travail interne | Coût de capacité | Responsable d'équipe | Effort × coût de référence | Projet et exploitation | Disponibilité réelle |
| Support | Direct, récurrent | Service propriétaire | Contrat / historique | Par année | Couverture hors horaires |
| Exploitation | Direct ou réparti | Opérations | Consommation / capacité | Par année | Croissance de charge |
| Sécurité et conformité | Mixte | Sécurité / conformité | Contrôles et audits | Selon cadence | Exigences évolutives |
| Incidents résiduels | Coût attendu ou scénario | Risque / métier | Historique, fréquence et impact | Selon hypothèse | Probabilité incertaine |
| Sortie | Ponctuel futur | Achats / technique | Scénario et devis | Fin d'horizon | Format propriétaire |
| Valeur de récupération | Entrée potentielle | Finance / actif | Hypothèse réaliste | Fin d'horizon | Valeur incertaine |

Une valeur monétaire à la fin de l'horizon ne doit être utilisée que si elle est défendable et pertinente. Pour un équipement ou une licence, la revente ou la valeur résiduelle peut être nulle. Ne pas créer artificiellement un bénéfice de récupération pour faire augmenter le ROI.

### 2.4 CAPEX et OPEX : distinguer la classification de la décision économique

CAPEX désigne généralement des dépenses d'investissement ou de capital, tandis qu'OPEX désigne des dépenses opérationnelles. Le traitement comptable exact dépend du référentiel appliqué et des critères d'immobilisation : il ne faut pas déduire le classement uniquement de l'intitulé de la facture ou du fait que la dépense est élevée.

La distinction est importante pour le budget, la trésorerie, le compte de résultat et le bilan. Une dépense immobilisée peut être payée maintenant mais comptabilisée au résultat au fil de sa durée d'amortissement. Une dépense opérationnelle peut être récurrente et peser immédiatement sur le résultat. Du point de vue de l'analyse de projet, les flux de trésorerie doivent être modélisés à la date réelle, indépendamment de leur présentation comptable.

Exemples à vérifier avec la finance :
- achat d'équipement durable ;
- frais de développement ou de mise en œuvre ;
- configuration, migration et formation ;
- abonnement cloud ou SaaS ;
- maintenance corrective et évolution ;
- licences perpétuelles ou souscription ;
- coûts de démantèlement et de sortie.

Ne pas supposer que tous les coûts de projet peuvent être capitalisés. La comptabilité doit confirmer les règles applicables. Pour comparer deux solutions, examiner les flux économiques complets en plus de leur effet sur les comptes.

### 2.5 Estimer par lots de travail

Une estimation ascendante (*bottom-up*) décompose le projet en activités, quantités et coûts unitaires. Elle est souvent utile lorsque le périmètre est assez détaillé. Une estimation descendante (*top-down*) utilise des références de projets comparables, des ratios ou un budget cible pour cadrer l'ordre de grandeur. L'estimation analogique compare avec des projets similaires ; l'estimation paramétrique utilise une relation mesurée entre le coût et un facteur ; une estimation à trois points présente les valeurs optimiste, centrale et prudente.

Aucune méthode n'est parfaite. Un modèle détaillé peut donner une fausse impression de certitude si les quantités et hypothèses sont fragiles. Une référence historique peut être biaisée par des projets réussis seulement ou des contextes différents. Documenter le niveau de maturité et trianguler les méthodes lorsque le montant ou le risque le justifie.

Pour chaque lot, préciser le périmètre, les quantités, le coût unitaire, la source, la date de la source, l'inflation ou l'indexation, les hypothèses, les exclusions et le responsable. La somme doit être rapprochée de l'estimation globale et des capacités disponibles.

### 2.6 Coût à terminaison et dépenses engagées

Pour suivre un projet en cours, distinguer :
- les dépenses déjà réalisées ;
- les engagements contractuels restant à payer ;
- les coûts des activités restantes ;
- les changements approuvés ;
- les risques ou incertitudes non encore matérialisés ;
- les économies ou crédits dont la réalisation est suffisamment certaine.

Le coût estimé à terminaison (*Estimate at Completion*, EAC) représente ce que le projet devrait coûter au total selon les informations actuelles. Il peut être calculé comme le coût réel cumulé plus le coût à terminaison estimé des travaux restants, à condition que les deux éléments soient cohérents et sans double comptage. Ne pas assimiler le budget consommé au travail livré : les deux peuvent évoluer différemment.

Un rapport de prévision montre l'écart au budget, sa cause, son caractère réversible ou non, l'effet sur le calendrier et les options d'arbitrage. Le but n'est pas d'attendre la fin pour déclarer le dépassement, mais de permettre une action lorsqu'elle peut encore changer l'issue.

~~~mermaid
flowchart TD
  A[Définir le périmètre et l'horizon] --> B[Décomposer les activités]
  B --> C[Collecter prix, quantités et coûts internes]
  C --> D[Ajouter transition, exploitation et sortie]
  D --> E[Documenter exclusions et hypothèses]
  E --> F[Tester incertitude et scénarios]
  F --> G[Revue indépendante et validation]
  G --> H[Base de coût approuvée]
  H --> I[Actualiser avec les coûts réels et changements]
~~~

## 3. Construire un budget opérationnel et une prévision glissante

### 3.1 Les catégories du budget

Un budget de maintenance ou d'exploitation peut distinguer :
- coûts fixes et variables ;
- contrats et abonnements ;
- pièces, consommables et interventions ;
- personnel interne, formation et astreintes ;
- maintenance préventive et corrective ;
- investissements, renouvellements et modernisation ;
- coûts de projets, migrations et mise en service ;
- sécurité, continuité, tests et conformité ;
- provisions ou contingences selon la méthode de l'organisation.

Le découpage doit permettre la comparaison avec les factures et les responsabilités, sans être tellement détaillé qu'il devient impossible à tenir à jour. Les catégories d'un outil financier doivent correspondre à des définitions comprises par les opérationnels.

### 3.2 Budget fixe, variable et mixte

Les coûts fixes restent relativement stables dans une plage de capacité et pendant une période donnée : abonnement de base, contrat annuel, loyer ou équipe permanente. Les coûts variables évoluent avec le volume : consommation cloud, nombre de transactions, pièces ou déplacements. Les coûts mixtes combinent une part fixe et une part variable.

Distinguer la variabilité réelle de la simple corrélation. Un abonnement par utilisateur peut être récurrent mais varier par palier, pas linéairement. Un contrat forfaitaire peut sembler fixe jusqu'à une limite de volume puis déclencher des frais. Le modèle doit enregistrer les seuils, unités et tarifs marginaux.

Cette analyse permet de tester l'impact d'une croissance ou d'une baisse d'activité. Elle aide aussi à identifier le coût marginal d'une demande supplémentaire, mais ne doit pas encourager à accepter des demandes sans regarder leur valeur ou leur risque.

### 3.3 Construire une prévision glissante

Une prévision glissante (*rolling forecast*) actualise périodiquement les estimations pour un horizon futur constant, par exemple les douze prochains mois, en remplaçant les périodes écoulées par de nouvelles périodes. Elle ne doit pas réécrire le budget initial approuvé. Garder séparés la base budgétaire, les prévisions successives et les résultats réels permet de mesurer la qualité de prévision.

La prévision peut s'appuyer sur :
- coûts contractuels et calendriers ;
- volumes réels et consommation récente ;
- projets en cours, jalons et changements ;
- renouvellements de contrats ;
- demandes d'investissement validées ou probables, distinguées ;
- risques, contingences et dépendances ;
- capacité et disponibilité des équipes ;
- hypothèses de change, d'inflation et de prix lorsque pertinentes.

Pour chaque mise à jour, expliquer les écarts : changement de volume, de prix, de périmètre, de calendrier, d'hypothèse ou de risque. Le rapport doit montrer ce qui est déjà engagé, ce qui est estimé et ce qui reste optionnel.

### Schéma — Comprendre un écart avant de choisir une action

~~~mermaid
flowchart TD
  A[Budget, engagements et réalisé] --> B[Calculer l'écart selon une convention définie]
  B --> C[Décomposer prix, volume, périmètre et calendrier]
  C --> D[Identifier causes et preuves]
  D --> E[Mettre à jour le coût à terminaison]
  E --> F{Dépassement ou risque hors tolérance ?}
  F -->|Non| G[Documenter et suivre]
  F -->|Oui| H[Préparer options et impacts]
  H --> I[Obtenir arbitrage et approbation]
  I --> J[Actualiser forecast sans effacer la base]
~~~

Une mesure de contrôle utile explique l'origine et les conséquences de l'écart ; elle ne se contente pas de colorer une cellule en rouge. Le budget initial, les changements autorisés et les prévisions successives restent identifiables.

### 3.4 Analyse des écarts

Un écart de budget peut être décomposé en effet de volume, effet de prix, effet de mix ou de périmètre, effet de calendrier et erreur de prévision. Cette décomposition aide à trouver les décisions correctes. Si les dépenses sont supérieures à cause d'un volume de demandes réellement plus élevé, réduire un prix unitaire ne résout pas le problème. Si un contrat a été indexé, l'action peut être de vérifier la formule, de négocier selon les droits contractuels ou de réviser la prévision.

L'analyse doit distinguer :
- **écart ponctuel :** événement isolé sans effet récurrent ;
- **écart structurel :** modèle ou hypothèse systématiquement erroné ;
- **écart de calendrier :** la dépense est décalée, mais peut rester nécessaire ;
- **écart de périmètre :** la réalisation n'est plus la même que celle autorisée ;
- **écart de prix ou volume :** variation des coûts unitaires ou de la demande ;
- **écart de qualité :** coûts de reprise, défauts ou livrables incomplets.

Éviter les économies purement temporaires présentées comme durables. Un report de maintenance peut diminuer la dépense du trimestre mais augmenter le risque futur. Un retard de facture ne constitue pas une économie. Une vacance de poste peut réduire les coûts de personnel tout en abaissant la capacité et en augmentant les coûts de prestation.

### 3.5 Prévoir la contingence sans la cacher

Une contingence couvre une incertitude identifiable selon le modèle de gestion des risques de l'organisation. Elle ne doit pas être utilisée comme un montant arbitraire pour compenser une estimation faible ni comme une réserve cachée à dépenser sans approbation. Son calcul peut s'appuyer sur des historiques, des scénarios, des distributions de coûts ou une méthode proportionnée à la maturité du projet.

Séparer la contingence de la base estimée lorsque c'est utile ; documenter ce qu'elle couvre, les conditions de libération, le décideur et la façon dont son utilisation est suivie. Une fois un risque connu et chiffré, il doit être intégré de façon cohérente plutôt que compter simultanément dans le coût de base et la réserve.

### 3.6 Biais d'optimisme

Les estimations sont souvent trop favorables : les projets prennent plus de temps, les coûts d'intégration apparaissent tard, les bénéfices prennent plus longtemps à se réaliser et l'adoption est moins rapide que prévu. Ce biais peut être réduit par la comparaison avec des projets passés, la documentation des hypothèses, des estimations indépendantes, des scénarios prudents et l'ajustement progressif lorsque des risques précis sont mieux compris.

Les valeurs génériques d'une institution ne doivent pas être reprises mécaniquement dans tous les contextes. Le meilleur référentiel est souvent l'historique de l'organisation : estimations initiales et coûts finaux de projets réellement comparables. Quand les données sont faibles, le niveau d'incertitude doit être déclaré et la marge doit être discutée explicitement.

## 4. Calculer le ROI sans se tromper de question

### 4.1 Définir le ROI et le périmètre

Le retour sur investissement (ROI) mesure le rendement d'un investissement selon une définition explicite des coûts et des bénéfices sur une période donnée. Une formule simple fréquemment utilisée est :

[
ROI = rac{	ext{Bénéfices retenus} - 	ext{Coûts retenus}}{	ext{Coûts retenus}} 	imes 100%
]

Cette formule n'est pas universelle si l'organisation définit le ROI différemment. Il faut préciser si les valeurs sont avant ou après impôts, si les coûts comprennent le fonctionnement, si les bénéfices sont cumulés ou annuels et si les flux sont actualisés. Un ROI de 40 % sur une période de trois ans n'est pas équivalent à 40 % par an.

Exemple simple : un investissement coûte 20 000 unités monétaires et produit 30 000 de bénéfices quantifiés sur l'horizon, sans autres coûts selon les hypothèses retenues. Le gain net est 10 000 ; le ROI simple est 10 000 / 20 000 = 50 %. Ce chiffre n'a de sens que si les 30 000 sont des bénéfices réellement attribuables, si le périmètre de coûts est complet et si le calendrier des flux n'est pas déterminant pour la décision.

### 4.2 Le ROI ne décrit pas le calendrier

Deux projets peuvent avoir le même ROI simple mais des flux très différents. Le projet A génère des bénéfices dès le premier trimestre ; le projet B les génère principalement dans la cinquième année. Le second comporte un risque d'exécution et de réalisation plus long. Le ROI simple ne pénalise pas explicitement l'attente et ne mesure pas à lui seul le risque.

Le ROI ne doit pas être utilisé isolément lorsque :
- les projets ont des durées de vie différentes ;
- les bénéfices apparaissent à des dates éloignées ;
- les coûts ou bénéfices varient fortement par année ;
- le risque de réalisation est important ;
- les options sont mutuellement exclusives et le capital est limité ;
- des obligations de sécurité ou de conformité ne se traduisent pas directement en bénéfices financiers.

Dans ces situations, compléter par les flux temporels, la VAN, le délai de récupération et les scénarios de risque.

### 4.3 Définir les bénéfices sans double compter

Les bénéfices potentiels peuvent être :
- une dépense contractuelle réellement évitée ;
- une réduction de consommation ;
- une baisse de fréquence ou de coût des incidents ;
- une meilleure disponibilité ou qualité ;
- une réduction d'heures supplémentaires ;
- une capacité libérée pour d'autres activités ;
- un revenu supplémentaire ;
- un coût futur évité ;
- une réduction du risque ou une meilleure conformité ;
- une meilleure expérience utilisateur.

Il faut distinguer les bénéfices financiers encaissables des bénéfices de capacité et des bénéfices qualitatifs. Si une automatisation libère 200 heures par an, ces heures ne sont pas automatiquement une économie de trésorerie. Il faut déterminer si elles permettent de réduire un coût externe, d'éviter un recrutement, de réduire les heures supplémentaires ou de produire une valeur additionnelle mesurable. Sinon, présenter un gain de capacité plutôt qu'une économie comptable.

Éviter le double comptage. Si le temps économisé est utilisé pour réduire le coût d'incident, ne pas ajouter une deuxième fois la même économie d'heures au bénéfice total. Si la réduction d'interruption inclut déjà le revenu préservé, ne pas additionner à nouveau le même revenu sous une autre étiquette. Chaque bénéfice doit avoir un mécanisme causal, une base de référence et un propriétaire responsable de sa vérification.

### 4.4 Séparer économies, coûts évités et valeur qualitative

Une économie de trésorerie réduit une sortie de fonds réelle. Un coût évité évite une dépense future qui aurait autrement eu lieu. Un gain de productivité libère de la capacité. Une valeur qualitative améliore une dimension qui n'est pas raisonnablement monétisée, comme la réduction de risques ou l'expérience utilisateur.

Ces catégories peuvent toutes influencer une décision, mais elles ne doivent pas être mélangées sans explication. Si la direction veut utiliser une valeur financière pour une amélioration de qualité, il faut une méthode d'estimation défendable, une source et une analyse de sensibilité. Si la monétisation est fragile, mieux vaut conserver une mesure non financière explicite que d'inventer un prix pour rendre le ROI attractif.

### 4.5 ROI annuel, cumulatif et actualisé

Le ROI peut être calculé pour une année, une période cumulée ou selon une méthode actualisée. Les rapports doivent nommer la version utilisée. Un ROI annuel peut exclure l'investissement initial ou utiliser un flux différent ; un ROI cumulé peut mélanger des montants reçus tôt et tard. Pour une décision de capital, la VAN est souvent plus adaptée pour comparer la valeur monétaire des flux à une date commune.

Ne pas multiplier un ROI de trois ans par un facteur pour le présenter comme une performance annuelle. Toute annualisation doit suivre une méthode explicitement définie et cohérente avec la temporalité des flux.

## 5. VAN, taux d'actualisation, délai de récupération et TRI

### 5.1 Valeur actuelle nette (VAN)

La valeur actuelle nette (VAN) transforme les flux de trésorerie futurs en valeur à une date commune en utilisant un taux d'actualisation adapté. Pour une série de flux (F_t) où l'investissement initial est représenté par un flux négatif, une forme simple est :

[
VAN = sum_{t=0}^{n} rac{F_t}{(1+r)^t}
]

où (F_t) est le flux net à la période (t), (r) le taux d'actualisation par période, (t=0) représentant généralement le flux initial, et (n) l'horizon. Lorsque le flux initial est séparé, on peut écrire VAN = − investissement initial + somme actualisée des flux futurs.

Une VAN positive indique que les flux modélisés dépassent le rendement requis incorporé dans le taux et les hypothèses. Elle ne garantit pas que le projet est faisable, abordable ou sans risque. Un projet peut avoir une VAN positive mais dépasser la capacité disponible, violer une exigence obligatoire ou dépendre d'un fournisseur indisponible.

### 5.2 Exemple chiffré de VAN

Supposons un investissement initial de 50 000 unités monétaires et des flux nets de 20 000 à la fin de chacune des trois années suivantes. Pour un taux d'actualisation illustratif de 10 % par an :

- Année 1 : 20 000 / 1,10 ≈ 18 181,82
- Année 2 : 20 000 / 1,10² ≈ 16 528,93
- Année 3 : 20 000 / 1,10³ ≈ 15 026,30

La somme actuelle des flux futurs est environ 49 737,05. La VAN est donc environ −262,95. Avec ces hypothèses, l'investissement est proche du point d'équilibre mais légèrement négatif. La conclusion changerait avec une variation relativement faible de flux, de coût, de calendrier ou de taux ; il faut donc vérifier les hypothèses au lieu de prendre le résultat comme une vérité absolue.

Tous les nombres sont illustratifs. Il faut conserver une convention cohérente sur le moment des flux, le taux et la période. Un taux annuel ne doit pas être appliqué comme s'il s'agissait d'un taux mensuel.

### 5.3 Choisir le taux d'actualisation

Le taux exprime le coût d'opportunité et le cadre de décision applicable. Dans une entreprise privée, il peut être lié au coût du capital ou à une politique interne approuvée ; dans une évaluation publique, la méthode peut utiliser un taux social prescrit. Ces approches ne sont pas interchangeables et ne doivent pas être choisies après calcul pour faire passer ou échouer un projet.

Le modèle doit préciser :
- la source du taux et l'autorité qui l'approuve ;
- la période et l'horizon ;
- si les flux sont nominaux ou en monnaie constante ;
- si l'inflation est incluse dans les flux ;
- le traitement des devises et du risque de change ;
- si les flux sont avant ou après impôt ;
- si les risques sont intégrés aux flux, au taux ou aux scénarios ;
- la date de référence.

Une erreur fréquente consiste à utiliser un flux nominal intégrant l'inflation avec un taux réel, ou un flux en devise locale avec un taux qui correspond à une autre devise. Les conventions doivent être cohérentes. Éviter aussi de compter deux fois le risque en diminuant les bénéfices et en ajoutant une prime de risque sans justification.

### Schéma — Choisir l'indicateur financier selon la question

~~~mermaid
flowchart TD
  A[Question de décision] --> B{Quel aspect doit être compris ?}
  B -->|Rendement simple sur période définie| C[ROI avec périmètre et horizon]
  B -->|Valeur des flux à une date commune| D[VAN avec taux cohérent]
  B -->|Temps pour récupérer l'investissement| E[Délai de récupération]
  B -->|Taux implicite des flux| F[TRI, avec vérification des limites]
  C --> G[Comparer risques, capacité et contraintes]
  D --> G
  E --> G
  F --> G
  G --> H[Décision combinée et documentée]
~~~

Les indicateurs répondent à des questions différentes. Leur calcul doit être cohérent, et aucun résultat isolé ne remplace l'analyse de faisabilité, du risque, de l'abordabilité et de la valeur métier.

### 5.4 Délai de récupération simple

Le délai de récupération mesure le temps nécessaire pour que les flux cumulés compensent l'investissement initial. Avec des flux uniformes, il peut être estimé par investissement initial / flux net périodique. Avec des flux variables, additionner les flux par période et déterminer quand le cumul devient positif.

Le délai simple est intuitif mais ignore la valeur temporelle de l'argent après le point de récupération et les flux qui suivent. Il peut aussi favoriser les projets qui récupèrent vite mais génèrent peu de valeur à long terme. L'utiliser comme indicateur complémentaire, pas comme seul critère de choix.

### 5.5 Délai de récupération actualisé

Le délai de récupération actualisé cumule les flux après actualisation. Il tient compte de la valeur temporelle selon le taux retenu, mais ignore encore les flux au-delà du point de récupération. Il ne remplace donc pas la VAN. Dans les projets à long terme, les deux délais peuvent différer sensiblement.

### 5.6 Taux de rendement interne (TRI)

Le taux de rendement interne est le taux qui rend la VAN égale à zéro pour les flux définis. Il fournit un taux de rendement implicite, mais peut être difficile à interpréter lorsque les flux changent plusieurs fois de signe, que les projets ont des tailles différentes ou que les options se font concurrence. Dans certains profils de flux, il peut exister plusieurs solutions ou aucune solution économiquement utile.

Ne pas choisir automatiquement le projet dont le TRI est le plus élevé. Un projet petit peut afficher un taux très élevé mais créer moins de valeur totale qu'un investissement plus grand. Pour des options mutuellement exclusives, la VAN, l'abordabilité, le risque et les contraintes de capacité sont souvent plus utiles à la décision que le seul classement par TRI.

### 5.7 Exemple : même ROI, valeurs différentes

Option A investit 100 et reçoit 130 en fin de période ; option B investit 1 000 et reçoit 1 300 dans les mêmes conditions temporelles. Les deux présentent un ROI simple de 30 % selon une formule un-période. Toutefois, l'enjeu de capital, le montant de valeur créée, le risque, les capacités mobilisées et les coûts fixes peuvent différer. On ne choisit pas uniquement le plus grand pourcentage : vérifier la VAN, le financement disponible, les contraintes et les risques.

### 5.8 Comparer des options mutuellement exclusives

Si l'organisation ne peut choisir qu'une seule des options, comparer la même période ou ajuster l'horizon selon une méthode appropriée. Un équipement d'une durée de vie de trois ans ne doit pas être comparé naïvement à une solution de six ans sans traiter la valeur résiduelle, le renouvellement et les coûts de remplacement.

Il faut aussi vérifier si les flux sont incrémentaux par rapport à la référence. Le calcul doit mesurer ce qui change grâce à l'option, pas attribuer à l'investissement des bénéfices qui seraient obtenus de toute façon. C'est le principe de l'analyse différentielle : les coûts et bénéfices communs à toutes les options n'influencent généralement pas le classement, même s'ils restent présents dans le budget global.

~~~mermaid
flowchart TD
  A[Définir horizon et scénario de référence] --> B[Construire les flux incrémentaux]
  B --> C[Valider coûts et bénéfices]
  C --> D[Choisir taux et conventions cohérents]
  D --> E[Calculer ROI, VAN et délai de récupération]
  E --> F[Tester scénarios et sensibilités]
  F --> G[Examiner risques, capacité et obligations]
  G --> H[Décision motivée et conditions]
~~~

## 6. Business case : relier chiffres, risques et options

### 6.1 Les dimensions d'un dossier de décision

Un business case robuste expose :
- **Stratégie :** pourquoi agir et quel résultat soutenir ;
- **Options :** quelles alternatives réalistes répondent au besoin ;
- **Économie :** quels coûts, bénéfices, risques et flux distinguent les options ;
- **Financement :** quand les fonds sont nécessaires et s'ils sont disponibles ;
- **Mise en œuvre :** qui réalise le travail, avec quelles capacités et quels jalons ;
- **Réalisations :** comment la valeur sera mesurée après livraison.

Certaines organisations utilisent des modèles formels à plusieurs dimensions. Les structures peuvent différer, mais les questions restent utiles : l'option répond-elle au besoin, présente-t-elle une valeur crédible, est-elle abordable, faisable, gouvernée et mesurable ?

### 6.2 Identifier les hypothèses critiques

Lister les hypothèses qui changent le résultat : volume de transactions, taux d'adoption, coût de licence, durée de mise en œuvre, taux de défaut, nombre d'incidents, réduction de temps, délai de disponibilité, coût interne, capacité de migration, coût de sortie ou taux d'actualisation. Pour chacune, noter une valeur centrale, une source, une plage plausible, un propriétaire, la date de révision et l'impact si elle change.

Une bonne hypothèse est falsifiable ou au moins révisable à partir d'une preuve. « La productivité augmentera » est trop vague. « Le temps moyen consacré à une tâche définie devrait diminuer selon une étude de référence, sous réserve d'une adoption de 70 % » peut être mesuré et réexaminé.

### 6.3 Analyser le coût de ne pas agir

Ne pas investir peut entraîner une dépense ou un risque : panne récurrente, fin de support, coût de maintenance croissant, perte de compétences, exposition de sécurité, incapacité à livrer ou non-respect d'une obligation. Mais ces conséquences ne doivent pas être exagérées pour forcer l'option préférée.

Définir la période et la probabilité des événements, utiliser l'historique lorsque possible, préciser les coûts directs et les effets indirects, puis tester les hypothèses. Pour une perte rare mais majeure, la valeur moyenne attendue ne décrit pas toute la décision ; le niveau de tolérance au risque, l'assurance, les exigences obligatoires et la possibilité de continuité doivent être examinés séparément.

### 6.4 Coût attendu et valeur du risque

Une estimation de risque peut utiliser une approximation « probabilité × impact » lorsqu'elle est pertinente. Par exemple, un événement estimé à 10 % de probabilité avec un impact financier de 100 000 correspond à une valeur attendue de 10 000 selon ce modèle simple. Cela ne signifie pas que l'organisation paiera exactement 10 000 ni que l'impact est faible : l'événement peut être rare et très dommageable.

Si la distribution, les dépendances ou les scénarios sont complexes, éviter de résumer le risque à un produit unique. Présenter des scénarios, des intervalles, des mesures de prévention, les conséquences extrêmes et l'autorité qui accepte le risque résiduel. Ne pas compter un coût de risque dans la contingence et une seconde fois dans les flux sans expliquer la relation.

### Schéma — Du business case à une recommandation finançable

~~~mermaid
flowchart TD
  A[Objectif métier] --> B[Options réalistes]
  B --> C[TCO, flux et bénéfices]
  C --> D[ROI, VAN et scénarios]
  D --> E[Risques et obligations]
  E --> F[Capacité de réalisation]
  F --> G[Besoin de financement par période]
  G --> H{Valeur, faisabilité et financement compatibles ?}
  H -->|Non| I[Phaser, réduire, revoir ou différer]
  H -->|Oui| J[Soumettre à l'autorité d'approbation]
~~~

Le dossier doit montrer à la fois la valeur, la faisabilité et le financement. Une option rentable mais non réalisable avec les compétences ou les fonds disponibles n'est pas immédiatement exécutable.

### 6.5 Affordabilité et valeur ne sont pas la même question

Un projet peut créer de la valeur mais ne pas être finançable dans l'année. Inversement, un projet dans le budget peut avoir une valeur faible. Le dossier doit montrer séparément :
- si l'option produit une valeur crédible ;
- si les fonds sont disponibles aux bonnes dates ;
- si les coûts récurrents sont soutenables ;
- si l'équipe peut livrer et exploiter ;
- si les risques sont acceptables ;
- si le financement d'autres priorités serait déplacé.

Un problème de financement peut conduire à phaser le projet, à réduire le périmètre, à rechercher une source de fonds ou à retarder une option. Il ne justifie pas de dégrader les hypothèses pour afficher artificiellement un ROI plus élevé.

### 6.6 Risque de retard et dépendances

Les bénéfices sont souvent conditionnés à la disponibilité d'autres équipes, à des contrats fournisseurs, à l'accès aux données, à une migration réussie ou à une adoption réelle. Le calendrier doit identifier le chemin critique, les dépendances et les hypothèses de disponibilité. Retarder une livraison peut réduire les bénéfices tout en conservant les coûts de projet.

Un scénario prudent modifie le calendrier, les coûts et les bénéfices en cohérence. Si la mise en service est retardée de six mois, le modèle ne doit pas conserver automatiquement les douze mois complets de bénéfices de la première année.

## 7. Prévisions de bénéfices et économies vérifiables

### 7.1 Définir une chaîne de bénéfices

Chaque bénéfice doit avoir un mécanisme causal explicite :
1. une intervention ou une capacité est livrée ;
2. une pratique ou un processus change ;
3. une mesure opérationnelle évolue ;
4. cet effet produit un bénéfice métier ;
5. une personne propriétaire vérifie le résultat.

Par exemple, un outil de supervision réduit le temps de détection. Cette réduction peut abaisser le temps d'indisponibilité, mais seulement si l'équipe peut réagir et si les procédures sont adaptées. La baisse d'indisponibilité peut limiter le coût d'incident, à condition d'avoir une méthode de valorisation pertinente. Le bénéfice ne se déduit donc pas automatiquement du seul achat de l'outil.

### 7.2 Distinguer bénéfices encaissables et capacité libérée

Imaginons qu'une automatisation économise 500 heures de travail par an. Trois cas sont possibles :
- une dépense externe ou des heures supplémentaires sont réellement réduites ;
- le même effectif traite davantage de demandes ou réduit le backlog ;
- le temps est libéré mais aucun usage de valeur n'est défini.

Le premier peut produire une économie de trésorerie. Le deuxième crée une capacité additionnelle, dont la valeur dépend du travail utile qui sera réalisé. Le troisième est un gain potentiel non encore matérialisé. Les trois peuvent être pertinents, mais ne doivent pas être présentés comme des économies budgétaires identiques.

Pour transformer une capacité en bénéfice, préciser son affectation : réduire un contrat externe, éviter un recrutement, augmenter la capacité de traitement, réduire le délai, renforcer la prévention ou améliorer le niveau de service. Le responsable du bénéfice confirme l'effet après mise en œuvre, en comparant avec la référence.

### 7.3 Établir un contrefactuel crédible

Pour mesurer un bénéfice, il faut comparer ce qui est observé à ce qui se serait probablement produit sans l'intervention. Ce contrefactuel peut utiliser une période historique, un service similaire, une tendance, un groupe de comparaison ou une modélisation explicite. La méthode dépend du contexte.

Contrôler les changements concomitants : volume, saisonnalité, équipe, contrat, périmètre et environnement. Si les incidents diminuent après une nouvelle supervision mais qu'un changement de service a aussi réduit le trafic, il est prématuré d'attribuer tout le gain à l'outil. Noter l'incertitude et utiliser une plage lorsque la causalité n'est pas établie.

### Schéma — Prouver qu'un bénéfice est réellement obtenu

~~~mermaid
flowchart LR
  A[Intervention livrée] --> B[Pratique ou processus change]
  B --> C[Indicateur opérationnel évolue]
  C --> D[Effet métier observé]
  D --> E[Propriétaire vérifie contre référence]
  E --> F{Bénéfice attribuable et confirmé ?}
  F -->|Oui| G[Enregistrer valeur réalisée]
  F -->|Partiel ou non| H[Analyser adoption et facteurs]
  H --> I[Action, responsable et date]
  I --> C
~~~

Le bénéfice dépend généralement d'actions au-delà de la livraison technique. Le propriétaire doit pouvoir expliquer la référence, les changements concomitants et les limites d'attribution.

### 7.4 Propriété du bénéfice

Le chef de projet n'est pas toujours la personne la mieux placée pour confirmer un bénéfice. Le propriétaire métier ou opérationnel qui maîtrise le processus doit assumer l'indicateur. Pour chaque bénéfice, consigner :
- nom et définition ;
- valeur de référence ;
- cible et période ;
- méthode de mesure ;
- propriétaire ;
- dépendances et actions nécessaires ;
- date de réalisation attendue ;
- fréquence de revue ;
- coûts associés à la réalisation ;
- risques d'attribution ou de double comptage.

Un bénéfice sans propriétaire reste une hypothèse de business case. Le suivi doit continuer après clôture du projet si les résultats n'apparaissent qu'en exploitation.

### 7.5 Exemple de fiche de bénéfice

| Champ | Exemple illustratif |
|---|---|
| Bénéfice | Réduire les interventions manuelles de vérification |
| Référence | 1 200 heures annuelles sur le périmètre mesuré |
| Résultat attendu | Réduction ciblée de 25 % après période d'adoption |
| Mesure | Heures tracées selon une méthode constante, contrôlées par échantillon |
| Bénéficiaire | Responsable des opérations |
| Dépendances | Formation, qualité des données, adoption de l'automatisation |
| Risque de mesure | Heures saisies de façon incomplète ou transfert du travail vers une autre équipe |
| Validation | Comparaison après stabilisation, en ajustant pour les volumes |
| Traitement financier | Capacité libérée ; économie de trésorerie uniquement si une dépense diminue |

Le pourcentage est fictif. Les cibles doivent être basées sur l'observation et faire l'objet d'une décision préalable.

## 8. Sensibilité, scénarios et incertitude

### 8.1 Pourquoi une seule valeur ne suffit pas

Un chiffre central peut masquer des hypothèses fragiles. Les coûts, le délai, l'adoption et le bénéfice ne sont pas toujours connus avec précision. L'analyse de sensibilité fait varier une hypothèse à la fois pour voir son influence, tandis que l'analyse de scénarios modifie plusieurs hypothèses de façon cohérente. Les deux répondent à des questions complémentaires.

Une décision est plus robuste lorsque l'option reste acceptable dans plusieurs conditions plausibles, ou lorsqu'un seuil de bascule est clairement défini. L'analyse ne doit pas être manipulée pour confirmer l'option préférée. Les hypothèses prudentes doivent rester plausibles et être reliées à des preuves, à l'expérience ou à un jugement expliqué.

### 8.2 Trois scénarios

Un modèle simple peut inclure :
- **Optimiste :** adoption rapide, intégration sans difficulté majeure, coûts conformes aux devis et bénéfices atteints tôt ;
- **Central :** hypothèses les plus plausibles selon les données disponibles ;
- **Prudent :** adoption plus lente, coût d'intégration plus élevé, retard, bénéfices partiels ou coûts de support supérieurs.

Le scénario prudent ne doit pas être une catastrophe arbitraire. Il combine des événements crédibles et explique leur justification. Un scénario sévère mais plausible peut être présenté à part si l'enjeu ou l'irréversibilité le justifie.

### 8.3 Analyse de sensibilité à un facteur

Faire varier les hypothèses importantes : coût initial, coût récurrent, volume, taux d'adoption, bénéfice par unité, retard de mise en service, durée de vie, coût de support et taux d'actualisation. Identifier les paramètres qui changent le plus la VAN ou le classement des options.

Un graphique de type tornado peut présenter les hypothèses classées selon leur effet sur le résultat. Le classement est utile pour la gouvernance : il révèle où une meilleure donnée ou une négociation peut réellement améliorer la décision. Il ne doit pas masquer les risques non financiers qui peuvent être éliminatoires.

### 8.4 Valeur de bascule

La valeur de bascule est la valeur à partir de laquelle la recommandation ou la conclusion change. Exemples :
- à quel coût initial la VAN devient-elle négative ?
- quel taux d'adoption minimal est nécessaire pour atteindre le seuil de rentabilité ?
- combien de mois de retard annulent la valeur attendue ?
- quel coût de sortie rend une alternative préférable ?
- combien d'incidents doivent être évités pour couvrir l'investissement ?

Cette analyse produit une limite opérationnelle claire. Si le coût dépasse le seuil, l'équipe doit redéfinir le périmètre, renégocier ou revenir à l'autorité de décision au lieu de poursuivre automatiquement.

### Schéma — Réduire l'incertitude au meilleur coût

~~~mermaid
flowchart TD
  A[Hypothèse incertaine] --> B[Mesurer son influence sur la décision]
  B --> C{Peut-elle changer l'option retenue ?}
  C -->|Non| D[Documenter et surveiller]
  C -->|Oui| E[Choisir une preuve de réduction d'incertitude]
  E --> F[Devis, pilote, test, benchmark ou revue indépendante]
  F --> G[Actualiser la plage et les scénarios]
  G --> H{Décision désormais robuste ?}
  H -->|Non| E
  H -->|Oui| I[Soumettre les conditions d'approbation]
~~~

Il ne faut pas chercher à réduire chaque incertitude avec le même effort. Prioriser les hypothèses qui peuvent changer la décision et choisir une vérification proportionnée au coût, au risque et au calendrier.

### 8.5 Incertitude et qualité de l'estimation

Pour chaque hypothèse, évaluer la qualité de la source : devis ferme, contrat signé, mesure historique, estimation technique, avis expert, benchmark ou simple hypothèse. La précision des calculs ne doit pas dépasser celle des données. Si le coût de sortie est inconnu, afficher une plage ou un scénario plutôt qu'un montant faussement précis.

Les estimations peuvent être renforcées par une revue indépendante, des références de projets comparables, des devis, un prototype, un test de charge, une exploration technique ou une analyse détaillée du périmètre. Choisir la mesure de réduction de l'incertitude qui a un coût et un délai proportionnés à la décision.

~~~mermaid
flowchart TD
  A[Modèle central] --> B[Identifier hypothèses sensibles]
  B --> C[Définir plages et sources]
  C --> D[Tester une variable à la fois]
  C --> E[Construire scénarios cohérents]
  D --> F[Mesurer l'effet sur VAN et coût]
  E --> F
  F --> G{La décision change selon le scénario ?}
  G -->|Oui| H[Définir seuil de bascule et mesure de réduction]
  G -->|Non| I[Documenter la robustesse et les limites]
  H --> J[Recommander avec conditions]
  I --> J
~~~

### 8.6 Probabilité et valeur attendue

Lorsque les données le permettent, la valeur attendue d'un événement peut être calculée en pondérant les résultats par leurs probabilités. Mais cette moyenne ne révèle pas toute la distribution du risque. Un événement rare avec un impact majeur peut rester inacceptable même si sa valeur attendue est faible. Les dépendances et risques corrélés doivent aussi être pris en compte : plusieurs risques ne sont pas nécessairement indépendants.

Pour un investissement de valeur élevée ou irréversible, des méthodes plus avancées — simulation Monte-Carlo, arbres de décision, analyse d'options réelles ou distributions de coûts — peuvent être utiles, mais elles doivent être calibrées sur des données crédibles. La complexité du modèle ne compense pas l'absence de données.

## 9. Budgéter le risque, la continuité et la résilience

### 9.1 Le coût du risque n'est pas qu'une ligne optionnelle

Une réduction de coût peut augmenter la probabilité d'incident, la dépendance à un fournisseur, le délai de reprise ou la fatigue de l'équipe. À l'inverse, une dépense de redondance, de maintenance préventive, de sauvegarde ou de transfert de compétence peut réduire un risque. La décision doit comparer les coûts et les effets possibles, sans supposer que toute dépense de résilience sera rentabilisée par des incidents évités.

Le budget doit considérer :
- sauvegardes et tests de restauration ;
- capacité de secours et essais de bascule ;
- maintenance préventive, pièces et obsolescence ;
- supervision, sécurité et journalisation ;
- exercices de crise et de continuité ;
- formation croisée, documentation et relève ;
- assistance de transition et réversibilité fournisseur ;
- réserves justifiées pour risques identifiés.

Ces dépenses doivent être reliées à des scénarios et à une tolérance au risque. Les exigences obligatoires ne peuvent pas être supprimées simplement parce que le ROI direct est négatif.

### 9.2 Coût attendu d'un incident

Une estimation peut combiner fréquence, coût direct, temps de rétablissement, coût de main-d'œuvre, pénalités éventuelles, pertes de production ou de revenus, remédiation et coût de reprise. Certains effets sont difficiles à monétiser et doivent être présentés séparément. Éviter de compter deux fois les heures déjà incluses dans un contrat ou les pertes qui se recouvrent.

Si l'historique est court, déclarer la limitation. Compléter par des scénarios, benchmarks, avis techniques ou tests. La valeur obtenue est une estimation de décision, pas une promesse sur la facture future.

### 9.3 Budgéter la continuité comme une capacité

Un plan de reprise qui n'a pas de ressources affectées peut être inapplicable. Vérifier les coûts des licences de secours, du stockage, du réseau, des accès d'urgence, de la documentation, des tests, des pièces, de la capacité fournisseur et des personnes nécessaires. Le coût annuel de préparation doit être comparé au niveau de service et de risque requis.

Le budget doit également inclure le coût d'opportunité des exercices et le travail nécessaire à corriger leurs écarts. Un exercice qui révèle des défauts mais dont aucune action n'est financée améliore la connaissance du risque sans nécessairement améliorer la résilience.

### 9.4 Sécurité et projets obligatoires

Certains investissements sont obligatoires pour respecter un contrôle de sécurité, une exigence légale, une fin de support ou une règle d'exploitation. Un ROI financier faible ne constitue alors pas le seul critère. Comparer les options conformes, leurs coûts et leurs risques, puis documenter pourquoi la solution retenue est appropriée.

Il peut être utile d'estimer le coût évité ou la réduction de risque, mais ne pas fabriquer une économie pour rendre l'investissement attractif. La décision doit distinguer la nécessité obligatoire, les bénéfices financiers et les bénéfices de risque ou de conformité.

## 10. Choisir entre investissement, externalisation et amélioration interne

### 10.1 Coût du fournisseur et coût de maîtrise interne

Une proposition d'externalisation doit inclure le prix du fournisseur, la gouvernance, les services internes conservés, la transition, les contrôles, les frais de changement, la gestion des incidents et la sortie. L'internalisation doit inclure recrutement, formation, rémunération, outils, disponibilité, gestion et continuité. Comparer uniquement un tarif fournisseur à un salaire ne fournit pas un coût complet.

Le modèle doit aussi considérer les compétences stratégiques et la capacité de contrôle. Une organisation qui externalise entièrement une compétence peut perdre la capacité d'évaluer les travaux, de détecter une mauvaise recommandation ou de changer de prestataire.

### 10.2 Acheter, développer ou réutiliser

Les options doivent être évaluées sur un horizon identique et un périmètre cohérent. Le développement interne peut apporter de la flexibilité et du contrôle, mais augmenter le délai, le coût de maintenance et la dépendance à des personnes. Une solution du marché peut accélérer la mise en service tout en créant un abonnement, des limites ou une dépendance propriétaire. La réutilisation peut réduire les coûts mais nécessiter un refactoring ou une modernisation.

Comparer les coûts initiaux et récurrents, les délais, les compétences, la capacité, la sécurité, l'intégration, l'évolution, le verrouillage, les options de sortie et les bénéfices. La décision ne se résume pas à la préférence technique ; elle doit démontrer la valeur et les risques.

### 10.3 Coût de changement et réversibilité

Le coût de sortie doit être estimé avant l'achat. Il peut inclure l'export de données, les licences, la migration, l'assistance du fournisseur, les tests, la formation, la double exploitation, le retrait des accès, la suppression des copies et les coûts d'interruption. Les valeurs doivent être liées à un plan réaliste et aux clauses contractuelles.

Un projet qui affiche un ROI favorable mais rend la sortie impossible peut créer une dépendance coûteuse à long terme. Intégrer la réversibilité dans les exigences et les contrats, puis tester les hypothèses si le risque est important. Ne pas présumer qu'un simple export suffit : les configurations, les processus, les journaux et les compétences peuvent aussi être nécessaires.

## 11. Préparer la décision d'investissement et les contrôles de gouvernance

### 11.1 Les portes d'approbation

Les investissements complexes peuvent être soumis à plusieurs jalons : approbation du besoin, validation des options, autorisation du budget, engagement contractuel, passage en réalisation, mise en service, revue des bénéfices. Le nombre de portes et les seuils dépendent des règles internes, de la valeur, du risque et de la réversibilité.

À chaque porte, la question change. L'approbation du besoin n'autorise pas nécessairement la dépense. Un budget approuvé ne vaut pas signature de contrat. Une livraison technique ne garantit pas que les bénéfices seront obtenus. Chaque étape a un décideur, des preuves et des conditions de passage.

~~~mermaid
flowchart TD
  A[Besoin et résultat] --> B[Analyse des options]
  B --> C[Estimation et risques]
  C --> D{Valeur crédible et financement abordable ?}
  D -->|Non| E[Revoir l'option ou arrêter]
  D -->|Oui| F[Autorisation et délégation]
  F --> G[Engagement et réalisation]
  G --> H[Contrôle à terminaison et recette]
  H --> I[Mise en service]
  I --> J[Mesure des bénéfices]
  J --> K[Revue post-investissement]
~~~

Les portes doivent être proportionnées. Une procédure trop lourde pour une dépense faible consomme elle-même des ressources ; une validation trop légère pour un investissement stratégique expose l'organisation. Les critères sont établis et connus avant le lancement.

### 11.2 Le dossier pour la direction

Un dossier de décision n'a pas besoin de répéter tout le tableur. Il doit permettre de comprendre :
- le problème et pourquoi agir maintenant ;
- les options réelles, y compris l'inaction ou le minimum nécessaire ;
- le coût initial, récurrent, à terminaison et de sortie ;
- les bénéfices financiers et non financiers ;
- les métriques clés : ROI, VAN, délai de récupération et hypothèses ;
- la sensibilité, les scénarios et les valeurs de bascule ;
- la faisabilité, la capacité et les dépendances ;
- le financement requis par période ;
- les risques et les mesures de réduction ;
- la recommandation, l'autorité sollicitée et les conditions de réussite.

Le résumé doit être cohérent avec le modèle détaillé. Si la direction demande un scénario plus prudent ou une option supplémentaire, le calcul doit être mis à jour et versionné.

### 11.3 Contrôles de qualité du modèle financier

Un modèle vérifiable comporte :
- des cellules d'entrée séparées des formules ;
- des unités, devises, périodes et hypothèses clairement identifiées ;
- des sources et dates de référence ;
- une distinction entre coûts, bénéfices et flux de trésorerie ;
- des formules cohérentes et des totaux de contrôle ;
- des scénarios et paramètres facilement modifiables ;
- une trace des versions et des changements ;
- une revue indépendante des calculs critiques ;
- des contrôles de signe, de période et de double comptage ;
- une réconciliation du montant total avec le budget et les engagements.

Un modèle doit pouvoir être réutilisé par une autre personne sans dépendre de la mémoire de l'auteur. Les feuilles de calcul doivent aussi être protégées contre les modifications accidentelles ; cette protection ne remplace pas une vérification indépendante.

### 11.4 Règles de changement après approbation

Le périmètre, le prix, le calendrier, les bénéfices attendus ou la structure de financement peuvent évoluer. Définir les seuils et les changements qui imposent une nouvelle approbation. Les modifications doivent être documentées : raison, effet, options, risque, autorité et impact sur le business case.

Ne pas réécrire rétroactivement le budget de base pour faire disparaître un dépassement. Conserver la référence initiale et distinguer l'évolution autorisée du résultat contre la base initiale. Cette discipline permet d'évaluer la qualité des estimations et d'améliorer les futurs projets.

## 12. Suivre l'exécution et les bénéfices après livraison

### 12.1 Dépenser dans le budget n'est pas atteindre le bénéfice

Le suivi du projet et le suivi de valeur sont différents. Le projet peut être livré à temps et au budget sans que les utilisateurs adoptent la solution. Il peut aussi dépasser le budget mais produire un bénéfice important, sous réserve que la gouvernance approuve l'écart et que le résultat soit réel. Il faut suivre séparément la livraison, le coût et la valeur.

La revue post-investissement compare le résultat à la base, explique les écarts, examine les causes, confirme ce qui a été réalisé et identifie les mesures correctives. Elle doit avoir lieu à un moment où les bénéfices ont eu le temps d'apparaître. Pour certains projets, une seule revue ne suffit pas ; prévoir plusieurs points après la mise en service.

### 12.2 Contrôler les dépenses et le coût à terminaison

Chaque période, comparer budget, réalisé, engagements, prévision à terminaison et variation. Examiner les changements de périmètre, retards, achats complémentaires, consommation, coûts internes, incidents et travaux non prévus. Les coûts doivent être rattachés à une cause et à une action.

Un dépassement peut exiger une mesure : réduire une fonctionnalité non essentielle, renégocier une activité, phaser la livraison, revoir les hypothèses ou demander une autorisation. L'action choisie doit être évaluée sur son effet secondaire. Couper les tests pour respecter un budget peut transférer le coût vers des incidents et de la reprise.

### 12.3 Suivi des bénéfices

Pour chaque bénéfice, suivre la référence, la cible, la valeur observée, la date, la qualité de la mesure, le responsable et les actions à prendre. Distinguer :
- bénéfice attendu mais pas encore mesurable ;
- bénéfice partiellement réalisé ;
- bénéfice réalisé et confirmé ;
- bénéfice non réalisé ;
- bénéfice qui dépend d'une action supplémentaire ;
- bénéfice abandonné ou devenu non pertinent.

Documenter l'écart, sans l'expliquer automatiquement par une mauvaise adoption. Les causes peuvent être une hypothèse incorrecte, une donnée de référence fragile, une migration incomplète, un changement de volume ou l'absence de ressource pour exploiter la capacité gagnée.

### 12.4 Leçons apprises et calibration

Comparer estimation initiale et coût réel : coût d'intégration, durée, effort interne, consommation, bénéfices, coût des incidents et de sortie. Le but n'est pas de punir l'auteur des estimations, mais de renforcer la méthode. Agréger les erreurs de prévision par catégorie permet d'améliorer les estimations futures et de documenter le biais d'optimisme.

Les références doivent être comparables. Comparer le coût d'un projet simple à celui d'un projet complexe sans ajuster les facteurs n'est pas utile. Conserver les différences de périmètre, de maturité, d'échelle, de réglementation et de technologie.

~~~mermaid
flowchart TD
  A[Base approuvée] --> B[Suivre réel, engagements et forecast]
  B --> C[Comparer coût et calendrier]
  C --> D[Mettre à jour les risques]
  D --> E[Livrer et accepter le résultat]
  E --> F[Mesurer bénéfices après adoption]
  F --> G{Bénéfices confirmés ?}
  G -->|Oui| H[Documenter valeur et leçons]
  G -->|Partiel ou non| I[Analyser cause et plan correctif]
  I --> F
  H --> J[Améliorer les modèles et références]
~~~

## 13. Exemple financier détaillé — arbitrer une automatisation de maintenance

### 13.1 Situation et options

Une équipe traite manuellement les alertes et prépare des rapports de maintenance. Elle envisage une automatisation. Le problème n'est pas seulement le nombre d'heures : certaines alertes sont répétées, les rapports arrivent tard, les incidents restent longtemps sans qualification et les experts sont interrompus.

Trois options sont envisagées :
- **Option A — amélioration manuelle :** standardiser les modèles et procédures sans acheter de nouvelle plateforme ;
- **Option B — automatisation ciblée :** automatiser les alertes répétitives et la génération des rapports ;
- **Option C — plateforme complète :** déployer une solution plus large, avec intégrations et gouvernance supplémentaire.

Les montants ci-dessous sont fictifs. Avant une décision réelle, les prix, volumes, temps de travail, coûts de transition, bénéfices et taux doivent être confirmés.

### 13.2 Définir les coûts

Pour chaque option, l'estimation inclut :
- coûts de conception et de mise en œuvre ;
- licences et infrastructure ;
- intégration et nettoyage des données ;
- formation et transfert de connaissances ;
- support et maintenance ;
- charge interne d'exploitation ;
- coût de sortie ou de remplacement ;
- bénéfices quantifiés selon la même période.

Option B peut avoir un coût initial de 40 000 et des coûts supplémentaires de 10 000 par an pendant trois ans. Ces valeurs ne doivent pas être considérées comme réelles sans devis et validation. Option A pourrait avoir un coût initial plus faible mais nécessiter plus d'effort récurrent ; Option C pourrait couvrir plus de fonctions mais présenter davantage de dépendances et un délai plus long.

### 13.3 Construire les bénéfices

Supposons, pour l'exercice, que l'option B réduise certains coûts externes et heures supplémentaires de 24 000 par an, et crée 12 000 de capacité utile par an. Le deuxième montant n'est pas automatiquement une économie de trésorerie. Pour le calcul de ROI financier, compter uniquement les bénéfices inclus par la définition approuvée. La capacité libérée peut être présentée séparément, avec un plan d'utilisation.

Si les économies encaissables sont estimées à 24 000 par an pendant trois ans, le total nominal est de 72 000 avant coûts récurrents et actualisation. Le coût nominal simplifié serait 40 000 + 3 × 10 000 = 70 000. Le gain net nominal de cette version simplifiée serait 2 000. Le ROI simple serait 2 000 / 70 000 ≈ 2,86 %. Cette comparaison doit encore être ajustée si les flux ne sont pas annuels, si des coûts internes ont été omis ou si les économies ne se réalisent pas pleinement.

Cette démonstration montre pourquoi annoncer « 36 000 de valeur annuelle » sans séparer économies et capacité produirait un ROI excessivement favorable. Le modèle doit préciser ce qui peut réellement être encaissé ou éviter une dépense.

### 13.4 Ajouter le calendrier et l'actualisation

Si les bénéfices ne commencent qu'au deuxième trimestre après déploiement, la première année ne produit pas douze mois de bénéfices. Si le support est payé dès la signature, ses flux commencent plus tôt que les bénéfices. L'actualisation et la date de chaque flux modifient la VAN. Il faut donc élaborer un tableau par période, et non calculer les bénéfices sur trois années pleines si l'application n'est active que pendant une partie de la première.

Le modèle peut comporter les colonnes : flux initial, coûts par année, économies de trésorerie, autres bénéfices séparés, flux net, facteur d'actualisation et flux actualisé. Conserver un scénario qui distingue période de mise en œuvre, montée en adoption et régime stable.

### 13.5 Interpréter la décision

Si la VAN est proche de zéro, la décision peut dépendre de la fiabilité des hypothèses et de risques non financiers. Il faut vérifier si l'option A produit une partie de la valeur pour un coût inférieur, si l'option C répond à des exigences obligatoires, ou si le modèle d'option B sous-estime la maintenance. Un résultat presque neutre n'est pas un échec automatique ; il signifie que la décision mérite une analyse des hypothèses et des bénéfices non monétisés.

Le dossier doit recommander une option ou une expérimentation limitée, définir les conditions de succès et arrêter les critères de poursuite. Si le pilote ne démontre pas le bénéfice minimal, l'organisation doit pouvoir réduire le périmètre ou abandonner la généralisation sans coûts disproportionnés.

### 13.6 Revue après mise en service

Après trois et six mois, comparer les coûts réels, l'adoption, les heures, les incidents, la qualité des alertes et les dépenses externes. Contrôler si les heures libérées ont été utilisées comme prévu. Si le gain de capacité est réel mais aucune dépense n'a diminué, le rapport le présente comme une capacité créée, pas comme une économie encaissable.

Le responsable des bénéfices documente les résultats, les causes d'écart, les limites de mesure, les améliorations et la valeur restante sur l'horizon. Cette revue alimente les budgets suivants et la calibration des estimations.

## 14. Procédure opérationnelle — du besoin à la revue post-investissement

### Étape 1 — Cadrer la décision

Écrire le problème, la situation de référence, les bénéficiaires, le périmètre, les objectifs et les contraintes. Identifier les exigences obligatoires et les objectifs souhaitables. Définir ce qui doit être décidé, par qui et à quelle date.

### Étape 2 — Étudier les options

Comparer l'inaction, le minimum nécessaire et plusieurs options réalistes. Utiliser le même horizon et les mêmes hypothèses de volume, de service, de disponibilité et de sécurité. Identifier les dépendances, les risques, les compromis et la possibilité de changer d'option.

### Étape 3 — Construire le modèle financier

Estimer le coût initial, les coûts récurrents, les coûts internes, la transition, la sortie et les risques. Définir les bénéfices, éviter les doubles comptes, préciser le calendrier et les conventions. Calculer les indicateurs appropriés et vérifier les formules.

### Étape 4 — Tester la robustesse

Construire des scénarios, tester les variables sensibles et déterminer les valeurs de bascule. Documenter la qualité des preuves et les mesures qui peuvent réduire l'incertitude avant l'engagement.

### Étape 5 — Valider l'abordabilité et la gouvernance

Confirmer les fonds nécessaires par période, les coûts récurrents, les compétences, les décisions d'autorisation et les conditions de passage. Obtenir les avis financiers, techniques, opérationnels, achats ou sécurité requis.

### Étape 6 — Réaliser avec contrôle

Suivre dépense, engagements, coût à terminaison, périmètre, risques, jalons, changements et dépendances. Mettre à jour la prévision sans écraser le budget de base. Escalader un dépassement lorsque la décision peut encore modifier le résultat.

### Étape 7 — Mesurer la valeur

À la mise en service et aux dates définies, vérifier les résultats et bénéfices. Comparer aux références, séparer économies et capacité, expliquer les écarts, corriger ou arrêter lorsque nécessaire.

### Étape 8 — Apprendre

Comparer l'estimation initiale avec les coûts et bénéfices réels. Actualiser les références, les méthodes et les hypothèses. Les résultats d'un projet doivent améliorer la fiabilité de la prochaine décision.

## 15. Erreurs financières fréquentes et comment les éviter

### Erreur 1 — Comparer seulement le prix initial

Le prix d'achat peut être inférieur alors que le support, la consommation, la migration et la sortie sont supérieurs. Comparer les coûts pertinents sur le même horizon et expliciter les éléments inconnus.

### Erreur 2 — Compter le temps économisé comme une économie immédiate

Un gain d'heures crée une économie de trésorerie seulement si une dépense est effectivement réduite ou évitée selon une méthode défendable. Sinon, c'est une capacité libérée. Définir son usage et son propriétaire.

### Erreur 3 — Présenter un ROI sans horizon

Un pourcentage n'est interprétable que si les coûts, bénéfices, période et méthode sont connus. Indiquer si le ROI est annuel, cumulatif, simple ou construit selon une autre définition.

### Erreur 4 — Ignorer le délai de réalisation

Un bénéfice retardé a une valeur moindre dans une analyse actualisée et peut compromettre le financement. Représenter les flux à leurs dates probables, pas uniquement en montants annuels cumulés.

### Erreur 5 — Ajouter une contingence sans justification

Une réserve arbitraire peut gonfler ou sous-estimer le coût. Relier la contingence aux risques, à la maturité du modèle, aux historiques et aux règles de libération.

### Erreur 6 — Confondre amortissement et sortie de trésorerie

La dépense d'investissement, son paiement, sa classification et son effet comptable dans le temps sont différents. Modéliser correctement les flux et consulter la comptabilité pour le traitement fiscal et comptable applicable.

### Erreur 7 — Utiliser le taux d'actualisation pour favoriser une option

Le taux doit provenir d'une méthode ou politique approuvée et rester cohérent avec la monnaie, l'inflation, la période et le risque. Ne pas le changer après calcul sans raison documentée.

### Erreur 8 — Oublier le scénario de référence

Attribuer à l'investissement des bénéfices qui auraient été obtenus même sans lui surestime la valeur. Construire les flux incrémentaux par rapport à une référence réaliste.

### Erreur 9 — Compter deux fois un bénéfice

Le temps économisé peut déjà être inclus dans la baisse de coût, et la réduction d'incident dans la réduction des heures. Définir chaque bénéfice, son mécanisme et ses chevauchements.

### Erreur 10 — Accepter une VAN positive comme décision automatique

La VAN n'examine pas seule l'abordabilité, les contraintes de capacité, la conformité ou les risques non acceptables. La décision doit réunir ces dimensions.

### Erreur 11 — Masquer un dépassement en modifiant le budget de référence

Conserver la base approuvée et distinguer les changements approuvés, les prévisions actuelles et les résultats. Cette transparence permet d'apprendre de la qualité des estimations.

### Erreur 12 — Fermer le business case à la livraison

La livraison ne prouve pas la réalisation des bénéfices. Nommer un propriétaire, une date de mesure et une méthode de vérification avant de lancer l'investissement.

## 16. Exercices d'application avec corrigés détaillés

### Exercice 1 — Construire un ROI simple

**Question :** un projet coûte 30 000 et produit 45 000 de bénéfices quantifiés sur trois ans. Aucun autre coût n'est inclus dans cet exercice. Quel est le ROI simple cumulé ?

**Correction :** gain net = 45 000 − 30 000 = 15 000. ROI = 15 000 / 30 000 × 100 = 50 %. Ce résultat est un ROI cumulé sur trois ans selon un périmètre simplifié, pas un rendement annuel. Il faut vérifier que les bénéfices sont attribuables, que la période est cohérente et qu'aucun coût pertinent n'a été omis.

### Exercice 2 — Distinguer capacité libérée et économie

**Question :** une automatisation réduit de 300 heures par an le travail manuel. Le nombre d'employés et les dépenses externes ne changent pas. Peut-on déclarer une économie budgétaire égale à 300 heures multipliées par le coût horaire ?

**Correction :** pas automatiquement. Le calcul valorise une capacité libérée, mais aucune dépense n'a nécessairement été réduite. Il faut identifier l'usage de cette capacité : baisse d'heures supplémentaires, évitement d'un recrutement, diminution d'un contrat ou traitement de travaux supplémentaires. Si le bénéfice est opérationnel plutôt que financier, le présenter séparément et mesurer sa réalisation.

### Exercice 3 — Calculer une VAN

**Question :** un investissement initial est de 10 000. Il génère un flux net de 6 000 à la fin de chacune des deux années suivantes. Avec un taux d'actualisation illustratif de 10 % par an, quelle est la VAN approximative ?

**Correction :** VAN = −10 000 + 6 000/1,10 + 6 000/1,10². Les flux actualisés sont environ 5 454,55 et 4 958,68. La VAN est donc environ 413,23. Avec ces hypothèses, la valeur est positive. Elle dépend du calendrier, du taux et de l'exhaustivité des flux. Il faut comparer cette valeur aux risques et à l'abordabilité.

### Exercice 4 — Le ROI favorise le mauvais projet

**Question :** le projet A annonce un ROI de 60 % et le projet B un ROI de 35 %. B crée pourtant une valeur nette actualisée plus élevée et répond à un besoin de capacité obligatoire. Peut-on choisir automatiquement A ?

**Correction :** non. Les ROI peuvent porter sur des tailles, des durées ou des flux différents. Comparer la VAN, le calendrier, les risques, la capacité, les contraintes obligatoires et l'abordabilité. Si les options sont mutuellement exclusives, examiner la valeur différentielle et la robustesse. Le ROI seul ne constitue pas une règle d'attribution universelle.

### Exercice 5 — Tester une hypothèse d'adoption

**Question :** un business case suppose que 90 % des utilisateurs adopteront un nouvel outil en deux mois. Aucun pilote ni mesure similaire n'existe. Quel est le problème et quelle action prendre ?

**Correction :** l'hypothèse est critique mais faiblement étayée. Établir une plage plausible, réaliser un pilote ou collecter des retours structurés, estimer la formation et le temps d'adoption, puis recalculer les bénéfices dans les scénarios. Ne pas conserver 90 % comme certitude. Le responsable métier doit être propriétaire de l'adoption et de sa mesure.

### Exercice 6 — Dépense de sortie oubliée

**Question :** une solution présente un TCO inférieur sur trois ans, mais la sortie nécessite une migration coûteuse et le contrat ne précise pas le prix de l'export. Que faut-il faire ?

**Correction :** établir le scénario de sortie et les éléments nécessaires : données, formats, configurations, licences, assistance, double exploitation, tests et suppression. Demander une estimation ou une condition contractuelle avant engagement. Tester la réversibilité si le risque le justifie. Intégrer le coût de sortie dans le TCO ou présenter une plage explicite ; ne pas traiter une inconnue importante comme un coût nul.

### Exercice 7 — Analyser un dépassement

**Question :** un projet est à 70 % de son calendrier mais a consommé 90 % de son budget. Quelles conclusions sont possibles ?

**Correction :** la situation signale un risque mais ne suffit pas à calculer le dépassement final. Vérifier l'avancement réel, les coûts déjà engagés, le travail restant, les différences de calendrier, le périmètre et les changements. Construire un coût à terminaison et plusieurs scénarios. Une dépense élevée au début peut être normale selon le profil, mais elle doit être justifiée par la base de coûts. Le rapport doit proposer une décision et non se limiter à comparer les pourcentages.

### Exercice 8 — Bénéfices qui se chevauchent

**Question :** une solution réduit les heures de traitement et les incidents. Le modèle compte le coût des heures économisées, puis compte à nouveau les mêmes heures comme réduction du coût des incidents. Quelle est la correction ?

**Correction :** cartographier les mécanismes de bénéfice, identifier les mêmes ressources ou flux concernés et supprimer le double comptage. Les deux effets peuvent être réels mais doivent correspondre à des postes distincts. Utiliser une base de référence, un responsable et une méthode de mesure pour chacun, en expliquant les dépendances.

### Exercice 9 — Projet obligatoire à ROI faible

**Question :** un projet est nécessaire pour corriger un risque de sécurité majeur, mais le ROI financier estimé est faible. Que faire ?

**Correction :** ne pas inventer de bénéfices financiers. Documenter l'obligation, les risques évités, les options conformes, les coûts, la faisabilité et le risque résiduel. Comparer les solutions admissibles et obtenir l'approbation selon la gouvernance. Le ROI financier informe la décision, mais ne remplace pas une exigence de conformité ou une règle de sécurité.

### Exercice 10 — Inflation et taux d'actualisation

**Question :** le modèle utilise des coûts nominaux qui augmentent chaque année avec l'inflation, mais un taux d'actualisation réel. Quel risque présente cette méthode ?

**Correction :** les flux et le taux ne sont pas sur une base cohérente. Choisir des flux nominaux et un taux nominal, ou des flux en monnaie constante et un taux réel, selon la méthode applicable. Documenter les hypothèses d'inflation, les devises et le traitement des prix. Une incohérence peut changer la VAN et le classement.

### Exercice 11 — Contingence et risque compté deux fois

**Question :** le modèle ajoute 10 % de contingence pour un risque d'intégration puis inclut aussi le coût complet de ce même risque dans les flux de scénario central. Que vérifier ?

**Correction :** vérifier le périmètre de la réserve, la définition du scénario central et la méthode de traitement des risques. Si le coût du risque est déjà compris dans la base, la réserve peut le compter une seconde fois. Séparer coût de base, risque identifié, contingence et scénarios, puis faire valider la structure par la gouvernance financière. Ne pas supprimer le risque ; corriger la représentation pour qu'il ne soit ni doublé ni oublié.

### Exercice 12 — Suivre les bénéfices après livraison

**Question :** l'outil a été déployé au budget et dans les délais, mais les indicateurs métier n'ont pas changé. Le projet doit-il être déclaré réussi ?

**Correction :** la livraison peut avoir réussi tandis que les bénéfices ne sont pas réalisés. Examiner l'adoption, la qualité de la mise en œuvre, le processus métier, les formations, les hypothèses initiales et la mesure. Définir des actions, un propriétaire et une date de réexamen. Si le bénéfice est définitivement inaccessible, documenter la différence, mettre à jour le business case et intégrer l'apprentissage dans les décisions futures.

## 17. Défi final — arbitrer un portefeuille de maintenance

### Scénario

Une organisation dispose d'une enveloppe limitée pour trois projets :
- **Projet A :** automatiser une tâche fréquente afin de réduire des coûts de prestation et de libérer de la capacité ;
- **Projet B :** remplacer une plateforme en fin de support pour réduire un risque de continuité et de sécurité ;
- **Projet C :** moderniser un reporting qui améliore la visibilité mais dont le bénéfice financier n'est pas encore mesuré.

Les estimations sont de maturité différente. Le projet A possède des mesures historiques partielles mais l'adoption reste incertaine. Le projet B est plus coûteux et les bénéfices sont surtout liés au risque évité. Le projet C dispose d'une démonstration convaincante, mais peu de preuves que la direction prendra de meilleures décisions avec le reporting. Les trois projets demandent du temps aux mêmes experts techniques.

### Travail demandé

Préparer un dossier d'arbitrage qui comprend :
1. la situation de référence et les options, dont l'inaction ou le minimum nécessaire ;
2. un budget de coût de cycle de vie pour chaque option ;
3. la distinction des dépenses, flux de trésorerie, coûts économiques et bénéfices qualitatifs ;
4. les hypothèses critiques, leurs sources et leurs niveaux de confiance ;
5. le calcul des indicateurs financiers appropriés lorsqu'ils sont pertinents ;
6. une analyse de scénarios, de sensibilité et de valeurs de bascule ;
7. l'analyse des risques, de la continuité et de la fin de support ;
8. l'analyse de capacité et des conflits de ressources ;
9. une recommandation de financement, de phasage ou de report, avec justification ;
10. les jalons d'autorisation, les conditions d'arrêt et les preuves avant engagement ;
11. les propriétaires des bénéfices, les références et les dates de mesure ;
12. un plan de revue après livraison et d'amélioration des estimations.

### Correction de référence

**Projet A.** Quantifier le coût externe réellement évitable, les coûts de mise en œuvre, les licences, l'intégration, la formation, l'exploitation, le support et la sortie. Séparer le coût de trésorerie évité de la capacité libérée. Tester l'adoption et la qualité des automatisations. Si la valeur dépend d'un taux d'adoption inconnu, réaliser un pilote ou un jalon de décision avant de financer tout le déploiement.

**Projet B.** Estimer le coût complet du remplacement et les conséquences plausibles du maintien de la plateforme en fin de support. Les risques de sécurité et de continuité doivent être évalués sans monétisation artificielle. Définir les options conformes, le calendrier de sortie du support, la capacité de migration et les critères techniques. Si le risque impose une échéance, expliquer cette contrainte de décision indépendamment du ROI financier.

**Projet C.** Définir ce que le reporting doit changer : délai d'arbitrage, exactitude, visibilité, qualité des prévisions ou réduction d'un travail manuel. Mesurer la base de référence et préciser comment le gain sera observé. Un pilote ou une mise en œuvre limitée peut tester si l'amélioration d'information change réellement les décisions. Sans mécanisme de bénéfice démontré, présenter l'option comme hypothèse à valider, et non comme économie certaine.

**Portefeuille et capacité.** Les projets partagent des ressources critiques. Le budget disponible n'est pas la seule contrainte : la capacité des experts peut ralentir la réalisation et retarder les bénéfices. Définir les séquences, les compétences et les possibilités de soutien externe. Ne pas attribuer simultanément la même capacité à trois plannings.

**Décision.** Comparer la valeur financière, la criticité, l'obligation, le délai, le risque, l'abordabilité et les ressources. Une solution robuste peut financer le minimum nécessaire du projet B pour réduire un risque obligatoire, lancer un pilote limité de A pour vérifier les économies et reporter une partie de C jusqu'à preuve du bénéfice. Une autre combinaison peut être justifiée si les données locales diffèrent. La correction n'impose pas une combinaison unique : elle évalue la qualité de la méthode, la transparence des hypothèses et la cohérence de la décision.

**Gouvernance.** Chaque projet a un responsable de bénéfice, une base approuvée, des portes de décision, des critères de passage et des conditions d'arrêt. Les coûts et bénéfices réels sont suivis sans réécrire le budget initial. Les résultats enrichissent les références pour les budgets futurs.

### Barème pédagogique sur 100

| Dimension | Points |
|---|---:|
| Cadrage, options et référence | 10 |
| TCO, budget et cohérence des flux | 15 |
| ROI, VAN et méthode adaptée | 15 |
| Qualité des hypothèses et analyse de sensibilité | 15 |
| Risques, conformité et continuité | 15 |
| Capacité, financement et phasage | 10 |
| Mesure des bénéfices et responsables | 10 |
| Gouvernance, conditions d'arrêt et apprentissage | 10 |

Une réponse experte peut conclure qu'un projet n'est pas encore prêt à être financé. Cette conclusion est utile si elle identifie les preuves manquantes, la mesure nécessaire pour les obtenir, le coût du délai et l'autorité qui décidera ensuite.

## 18. Références et approfondissement

Les ressources ci-dessous sont des références de méthode et de gouvernance financière. Leur application dépend de la juridiction, du secteur, du type d'organisation et des règles de financement. Elles ne remplacent pas les politiques comptables ou financières locales.

- [HM Treasury — The Green Book 2026](https://www.gov.uk/government/publications/the-green-book--2/the-green-book-2026) : guidance britannique d'évaluation des propositions, actualisée en février 2026. Elle traite notamment des options, de la valeur, du risque et du biais d'optimisme. Son taux et ses méthodes publiques ne doivent pas être transposés mécaniquement à une entreprise privée ou à un autre pays.
- [HM Treasury — Guidance on developing business cases](https://www.gov.uk/government/publications/guidance-on-developing-business-cases) : guidance sur les business cases de projets et programmes, mise à jour le 30 juin 2026. Elle s'appuie sur le modèle des cinq cas et accompagne la construction d'un dossier décisionnel.
- [UK Government — Cost Estimating Guidance](https://www.gov.uk/government/publications/cost-estimating-guidance/cost-estimating-guidance) : principes de construction d'estimations, documentation d'hypothèses, analyse de sensibilité et prise en compte du biais d'optimisme.
- [U.S. Government Accountability Office — Cost Estimating and Assessment Guide (GAO-20-195G)](https://www.gao.gov/products/gao-20-195g) : guide de bonnes pratiques pour l'estimation des coûts, le cycle de vie, les hypothèses, la sensibilité, l'incertitude, la validation indépendante et la mise à jour par les coûts observés.
- [NIST — SP 800-161 Rev. 1, Cybersecurity Supply Chain Risk Management Practices](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) : utile pour relier le coût d'un fournisseur, les dépendances de chaîne et les risques de sécurité lorsque l'investissement touche des technologies ou services tiers.

La bonne pratique consiste à enregistrer, pour chaque référence, le titre, la version, la date, le périmètre utile et le responsable de vérification. Un guide peut inspirer la méthode sans être juridiquement applicable. La décision financière doit toujours être reliée aux données et hypothèses réellement pertinentes pour le projet.

## Synthèse finale

La budgétisation experte relie la stratégie aux ressources, les ressources aux résultats et les résultats à des preuves. Un coût crédible couvre le cycle de vie et documente ses incertitudes. Un ROI interprétable définit ses coûts, bénéfices et son horizon. La VAN tient compte du temps et des flux actualisés, mais ne remplace ni l'analyse du risque, ni l'abordabilité, ni les contraintes obligatoires. Les scénarios et valeurs de bascule révèlent où une hypothèse peut faire changer la décision.

La qualité du modèle dépend aussi de la mesure des bénéfices. Le temps libéré n'est pas automatiquement une économie, une dépense retardée n'est pas une économie durable et une livraison au budget ne prouve pas la réalisation de la valeur. Chaque bénéfice doit avoir une référence, une méthode, un propriétaire et une date de contrôle.

Enfin, le budget doit rester vivant sans réécrire l'histoire. Conserver la base approuvée, actualiser la prévision, expliquer les écarts et apprendre des coûts réels. Une organisation financièrement mature ne prétend pas connaître exactement l'avenir : elle rend ses hypothèses visibles, sait quelles données peuvent changer sa décision et définit quoi faire si la réalité s'écarte du modèle.
