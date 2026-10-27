# Gestion des fournisseurs — niveau expert

> **Mise en contexte —** Un fournisseur ne se résume ni à une facture ni à un interlocuteur commercial. Il peut assurer une capacité indispensable, héberger des données, maintenir une infrastructure, fournir des pièces, posséder une compétence rare ou dépendre lui-même d'acteurs que l'acheteur ne voit pas. La gestion des fournisseurs consiste à maîtriser cette relation pendant tout son cycle de vie : qualification, contractualisation, démarrage, performance, risque, changement, renouvellement et sortie. Une gestion trop légère laisse apparaître les problèmes lorsqu'ils deviennent des incidents ; une gestion excessivement administrative multiplie les réunions et les tableaux de bord sans améliorer le service. Le niveau expert consiste à proportionner les contrôles à la criticité, établir des mesures fiables, résoudre les écarts avec des preuves, collaborer sans abandonner l'autorité de l'acheteur et maintenir une possibilité réelle de continuité ou de substitution.

## Objectifs de maîtrise

À la fin du cours, l'apprenant devra être capable de :

- segmenter un portefeuille de fournisseurs en fonction de la criticité, de la substituabilité, de l'accès, de la dépendance et des conséquences d'une défaillance ;
- concevoir une gouvernance adaptée à chaque catégorie, avec des responsabilités, une fréquence de revue, des seuils et des voies d'escalade ;
- mener une diligence raisonnable proportionnée avant contrat et pendant la relation, en distinguant déclarations, preuves documentaires, tests et engagements contractuels ;
- construire un dossier fournisseur fiable et tenir à jour les propriétaires, services, sous-traitants, dépendances, échéances et plans de continuité ;
- mesurer la performance à partir de données vérifiables, définir des indicateurs équilibrés et détecter les effets indésirables d'un pilotage uniquement fondé sur les chiffres ;
- conduire une revue de performance utile, distinguer symptôme et cause, et attribuer les actions correctives à des responsables avec preuves d'efficacité ;
- gérer les incidents majeurs et les défauts récurrents sans perdre la maîtrise opérationnelle ni dégrader inutilement la relation commerciale ;
- évaluer les risques financiers, opérationnels, humains, juridiques, éthiques, de cybersécurité et de chaîne d'approvisionnement ;
- vérifier les dépendances de rang deux et les prestataires auxquels le fournisseur confie des fonctions sensibles ;
- organiser une relation collaborative lorsque la valeur en dépend, tout en conservant une séparation claire entre coopération, contrôle et acceptation du risque ;
- préparer une renégociation, une remise en concurrence, un renouvellement ou une sortie sur la base de faits, d'un calendrier et d'un plan de continuité ;
- transformer les enseignements en améliorations du portefeuille, des contrats, des appels d'offres et des pratiques internes.

La maîtrise ne consiste pas à attribuer chaque fournisseur une note ou une couleur. Elle consiste à rendre les risques compréhensibles, à anticiper les évolutions et à décider ce qui doit être corrigé, surveillé, réduit ou accepté — par la bonne autorité.

## Prérequis et responsabilité

Le cours s'adresse à un professionnel qui connaît la gestion des contrats, les achats, les opérations ou le pilotage de services. Le parcours recommande le cours « Rédaction d'appels d'offres — Expert » comme prérequis : la relation fournisseur doit prolonger les exigences et les engagements de l'achat, et non recréer des règles après la signature.

Les exemples sont pédagogiques. Les règles de passation, les droits d'audit, les obligations de conservation, les contrôles anti-corruption, les exigences de données et les possibilités de résiliation varient selon le pays, le secteur, le statut de l'acheteur, le financement et les contrats. Une procédure présentée dans ce cours ne remplace pas le droit applicable, le contrat signé, les délégations internes ni un avis juridique lorsque celui-ci est requis.

Avant de demander une action au fournisseur, vérifier le fondement de la demande, le propriétaire de la décision, le contrat, le risque, le délai, les coûts, la preuve de résultat et les conséquences pour le service. Un fournisseur ne doit pas être déclaré en faute sur une simple impression, pas plus qu'une relation de confiance ne permet d'ignorer une non-conformité objectivement établie.

## 1. Comprendre le cycle de vie fournisseur

La gestion commence avant la signature. La qualification, l'appel d'offres et la négociation créent des engagements qui devront être exécutés. Ensuite, le fournisseur doit être intégré, ses accès et ses responsabilités doivent être vérifiés, les services doivent démarrer selon une méthode acceptée, puis la performance et les risques doivent être suivis. Le renouvellement et la sortie doivent être préparés assez tôt pour éviter qu'une échéance contractuelle impose une décision précipitée.

~~~mermaid
flowchart TD
  A[Besoin et stratégie d'achat] --> B[Qualification et due diligence]
  B --> C[Sélection et contrat]
  C --> D[Transition et démarrage contrôlé]
  D --> E[Mesure de la performance]
  E --> F[Revue des risques et actions]
  F --> G{Situation à réexaminer ?}
  G -->|Amélioration| H[Plan correctif et vérification]
  H --> E
  G -->|Renouvellement proche| I[Évaluation stratégique et options]
  I --> J{Continuer ?}
  J -->|Oui| K[Renouveler sous conditions validées]
  J -->|Non| L[Transition, remplacement et sortie]
  K --> E
  L --> M[Clôture et retour d'expérience]
~~~

Le cycle n'est pas strictement linéaire. Un incident peut conduire à revoir la qualification ou le contrat ; un changement de propriétaire ou de sous-traitant peut déclencher une nouvelle analyse de risque ; une performance durablement faible peut accélérer une remise en concurrence. Le processus doit donc prévoir des événements déclencheurs et pas seulement des revues calendaires.

### 1.1 Pourquoi la gestion fournisseur échoue

Les difficultés courantes proviennent moins d'un manque de tableaux que d'une rupture entre contrat et exploitation. Les équipes techniques connaissent le comportement du service mais ignorent la clause applicable. Les achats connaissent le prix et les engagements, mais ne voient pas le backlog réel. Le responsable métier reçoit un rapport agrégé sans comprendre les défauts. Le fournisseur présente une bonne moyenne annuelle qui masque plusieurs pannes critiques. La direction autorise un renouvellement parce que l'échéance est proche, alors que la réversibilité n'a jamais été testée.

Ces problèmes indiquent qu'il faut relier trois vues :
- **Vue contractuelle :** obligations, périmètre, exclusions, prix, responsabilités, recours, dates et autorisations.
- **Vue opérationnelle :** incidents, demandes, changements, résultats, capacité, qualité, dépendances et expérience utilisateur.
- **Vue de risque et de valeur :** criticité, concentration, exposition, coût complet, options de substitution, continuité et évolution du besoin.

Une donnée de performance doit pouvoir remonter à la clause ou au besoin qu'elle vérifie. Une obligation importante qui n'a aucune mesure ou preuve est difficile à piloter. Inversement, un indicateur qui n'aide aucune décision peut être coûteux à produire sans apporter de valeur.

### 1.2 Distinguer contrat, fournisseur, service et sous-traitant

Un fournisseur juridique peut détenir plusieurs contrats, délivrer plusieurs services ou utiliser plusieurs sous-traitants. Il faut éviter de confondre la notation d'une entité commerciale avec le risque d'un service particulier. Un même fournisseur peut être performant sur un service simple et présenter un risque élevé sur un autre service critique qui donne accès aux données ou aux systèmes d'administration.

Un référentiel robuste relie les objets suivants : fournisseur légal, groupe économique si pertinent, contrat, service, actif, propriétaire métier, propriétaire opérationnel, données concernées, accès autorisés, sous-traitants, lieu de traitement si applicable, niveaux de service, risques, incidents, factures et échéances. Une relation entre ces objets permet d'identifier les conséquences d'une défaillance et d'éviter les doublons dans les rapports.

### 1.3 Définir les responsabilités internes

La gestion des fournisseurs ne peut pas reposer uniquement sur le gestionnaire de contrat. Le modèle de responsabilité attribue les tâches :
- le **propriétaire métier** définit la valeur attendue, les priorités et l'acceptabilité du service ;
- le **responsable opérationnel** surveille la production, l'incidentologie et les résultats quotidiens ;
- les **achats** pilotent les mécanismes commerciaux, le marché, la remise en concurrence et la cohérence avec la stratégie ;
- le **juridique** conseille sur les obligations, les modifications, les différends et les options de résiliation ;
- les **finances** contrôlent les dépenses, les écarts de prix, les prévisions, les factures et les engagements ;
- la **sécurité et la protection des données** définissent ou vérifient les contrôles adaptés au risque ;
- le **gestionnaire fournisseur** coordonne la relation et maintient les décisions, les risques et les actions ;
- le **sponsor exécutif** arbitre lorsque le risque, le coût ou l'impact dépasse les délégations ordinaires.

Dans certaines organisations, une personne remplit plusieurs rôles. Il faut alors établir des contrôles compensatoires pour les décisions sensibles : approbation indépendante, vérification des données, deuxième validation d'une modification ou revue des conflits d'intérêts. Une matrice de responsabilités doit préciser qui réalise, qui approuve, qui contribue et qui doit être informé.

### Schéma — Relier chaque rôle à une décision

~~~mermaid
flowchart TD
  A[Mesure opérationnelle] --> B[Responsable de service valide les faits]
  B --> C[Gestionnaire fournisseur relie faits et contrat]
  C --> D[Achats / juridique évaluent les options contractuelles]
  C --> E[Sécurité / risque évaluent l'exposition]
  D --> F[Décision dans la délégation]
  E --> F
  F --> G[Action attribuée et date de contrôle]
  G --> H[Preuve et mise à jour du registre]
~~~

Une décision est robuste lorsque les informations utiles sont réunies sans diluer la responsabilité. Le groupe de travail conseille et produit les preuves ; l'autorité habilitée décide dans les limites de sa délégation. Le schéma doit être adapté à l'organisation et à ses fonctions réelles.

## 2. Segmenter le portefeuille selon la criticité

### 2.1 Pourquoi la segmentation est indispensable

Traiter de la même façon un fournisseur de fournitures courantes et un prestataire qui administre une infrastructure critique entraîne soit trop de contrôle, soit trop peu. La segmentation adapte l'effort à la conséquence d'une défaillance. Elle doit considérer la criticité du service rendu, l'impact d'une interruption, la substituabilité, les accès, les données, la concentration, les délais de remplacement, les obligations et le niveau d'incertitude.

La dépense annuelle peut contribuer à l'analyse, mais ne suffit pas. Un fournisseur à faible chiffre d'affaires peut être indispensable s'il détient une pièce rare ou une compétence introuvable. Un fournisseur coûteux n'est pas nécessairement critique si le service est remplaçable rapidement sans effet majeur. Il faut donc séparer la valeur économique de la criticité opérationnelle.

### 2.2 Dimensions de criticité

Évaluer notamment :
- l'impact d'une interruption sur les utilisateurs, les opérations, les revenus, les obligations et la sécurité ;
- le temps maximal acceptable avant qu'un effet devienne intolérable ;
- le délai réaliste pour activer une alternative ;
- le nombre de fournisseurs réellement substituables ;
- la dépendance à une technologie propriétaire, à une compétence rare ou à un accès privilégié ;
- la nature et le volume des données traitées ;
- la possibilité d'une interruption commune chez plusieurs services ;
- la maturité et la transparence du fournisseur ;
- le recours à des sous-traitants, à des régions ou à des infrastructures partagées ;
- la capacité de l'organisation à continuer en mode dégradé.

Une évaluation de criticité doit expliquer les justifications et les informations manquantes. Un score issu de réponses approximatives ne devient pas fiable parce qu'il est calculé dans un tableur.

### 2.3 Exemple de segmentation

| Segment indicatif | Profil | Gouvernance adaptée |
|---|---|---|
| Critique / stratégique | Défaillance pouvant interrompre une activité essentielle, compromettre des données ou nécessiter une longue transition | Propriétaire exécutif, gestionnaire nommé, revue formelle des risques, continuité testée, suivi régulier de performance |
| Important | Impact significatif mais options de substitution ou contournement identifiées | Revue périodique, scorecard, plan correctif selon les écarts et calendrier de renouvellement anticipé |
| Courant | Service standard, faible impact et substitution assez accessible | Contrôle contractuel et financier proportionné, revue simplifiée |
| Faible exposition / transactionnel | Achat simple, faible dépendance et impact limité | Contrôles de base, conformité de la facture, échéances et suivi des anomalies |

Les noms et seuils des segments sont locaux. Un fournisseur peut changer de segment lorsque le service devient plus central, que les données augmentent, qu'un sous-traitant change ou que le marché se concentre. Recalculer le segment uniquement une fois par an serait insuffisant si un événement majeur modifie immédiatement le risque.

~~~mermaid
flowchart TD
  A[Inventaire fournisseur] --> B[Évaluer impact d'une défaillance]
  B --> C[Évaluer substituabilité et délai de sortie]
  C --> D[Évaluer accès, données et dépendances]
  D --> E[Documenter incertitudes]
  E --> F[Attribuer un segment provisoire]
  F --> G[Validation par métier, achats et risque]
  G --> H[Choisir cadence et profondeur de contrôle]
  H --> I[Réévaluer après changement ou incident majeur]
  I --> B
~~~

### 2.4 Modèle de notation de criticité

Une grille illustrative peut attribuer de 1 à 5 à l'impact opérationnel, au risque de sécurité et de données, à la substituabilité inverse (5 lorsque la substitution est très difficile), à la dépendance de chaîne et à l'exposition contractuelle. La somme pondérée n'est utile que si les pondérations et seuils sont approuvés, calibrés et testés contre des cas réels. Si un seul critère critique est présent — par exemple l'administration d'un système essentiel — la règle locale peut imposer un segment élevé indépendamment de la somme.

Le modèle doit éviter le double comptage. Par exemple, « impact opérationnel » et « durée de sortie » peuvent être liés sans mesurer la même chose. Une équipe doit pouvoir expliquer pourquoi une réponse entraîne une note et quelle donnée pourrait conduire à la changer.

Les notes servent à orienter la diligence et la gouvernance, non à automatiser toutes les décisions. Le résultat doit être revu lorsque la situation change et par une personne responsable. Une classification calculée ne peut pas prendre seule la décision d'accepter un risque critique.

## 3. Qualification et diligence raisonnable

### 3.1 Avant l'engagement : établir le dossier minimal

Avant d'accorder une responsabilité importante, comprendre qui est le fournisseur, quelle capacité il fournit, qui la contrôle et dans quelles conditions. Le dossier varie avec le type d'achat et le régime applicable, mais peut couvrir :
- l'identité juridique, les coordonnées et les responsables pertinents ;
- la capacité financière et la continuité d'activité ;
- l'expérience, les compétences, les qualifications et les ressources annoncées ;
- les sous-traitants clés, les dépendances de rang deux et les lieux de prestation lorsque c'est pertinent ;
- les contrôles de qualité, de sécurité, de confidentialité et de gestion des accès ;
- les incidents significatifs, les plans de correction et les preuves de tests utiles ;
- l'assurance, les certifications et les attestations, en vérifiant leur portée et leur validité ;
- les conflits d'intérêts, la conformité éthique et les engagements pertinents ;
- les hypothèses commerciales, les exclusions et la possibilité de sortie ;
- les risques particuliers du secteur, du pays, du produit ou du financement.

La diligence doit être proportionnée au risque et aux règles d'achat. Elle ne doit pas devenir une collecte illimitée d'informations personnelles ou commerciales sans base ni nécessité. Définir les données demandées, leur finalité, le périmètre des personnes autorisées, la durée de conservation et les modalités de protection.

### 3.2 Déclarations, preuves et tests ne sont pas équivalents

Une déclaration du fournisseur est un point de départ. Une politique démontre qu'un processus a été documenté, mais pas nécessairement appliqué. Une certification peut couvrir une entité, un site, une période et un périmètre précis, mais pas toute la chaîne de prestation. Un rapport indépendant comporte des exclusions, des limites et parfois des sous-traitants non couverts. Un test démontre un comportement dans les conditions testées, mais pas dans toutes les circonstances. Un engagement contractuel permet d'exiger une action dans le temps, mais ne démontre pas à lui seul une capacité technique.

La revue doit consigner la question posée, la preuve reçue, son périmètre, sa date, les exclusions, la conclusion permise et l'action requise. Si une preuve importante manque, les options peuvent inclure une vérification supplémentaire, une limitation d'accès, une condition préalable au démarrage, une mesure compensatoire ou le refus d'exposition au risque selon l'autorité compétente.

### 3.3 Solidité financière et continuité du fournisseur

La santé financière ne se résume pas au bénéfice d'une année ou à un score externe. Selon la criticité et les règles applicables, examiner la capacité à financer la prestation, les retards de paiement, la dépendance à quelques clients, la concentration de revenus, les engagements importants, les besoins d'investissement et les signes de tension opérationnelle. Les données doivent être lues avec prudence : un indicateur isolé ne prédit pas mécaniquement une défaillance.

Pour un fournisseur critique, demander comment il maintiendra le service en cas d'incident majeur, de perte de personnel clé, de panne de site, de problème financier ou de défaillance d'un sous-traitant. Vérifier si le plan de continuité correspond au service réellement fourni et si les contacts d'escalade sont utilisables. Les assurances contractuelles peuvent limiter certains impacts mais ne remplacent pas un plan de continuité et une solution de substitution.

### 3.4 Vérifier les capacités réelles

La qualification doit relier les promesses aux opérations : compétences réellement affectées, disponibilité des experts, processus de support, astreinte, pièces, outils, environnements de test, qualité de la documentation et résultats d'exercices. Pour une prestation technique, une démonstration ou un test peut être utile si sa méthode et son usage sont autorisés et comparables.

Les références clients nécessitent une interprétation prudente. Un projet réussi dans un contexte différent ne prouve pas que le fournisseur peut assurer un service à plus grande échelle, dans une autre zone, avec des obligations de sécurité ou un délai de reprise plus exigeant. Demander à connaître le périmètre exact de la référence et les conditions qui rendent le résultat comparable.

## 4. Construire un référentiel fournisseur fiable

### 4.1 Les objets à tenir à jour

Un référentiel utile ne doit pas être un simple carnet d'adresses. Il relie :
- les identifiants légaux et commerciaux ;
- la catégorie et le segment de criticité ;
- les contrats, avenants, dates, options et clauses importantes ;
- les services et actifs couverts ;
- les propriétaires métier, opérationnels, contractuels et de risque ;
- les contacts principaux et de secours ;
- les sous-traitants clés, régions ou infrastructures partagées pertinentes ;
- les niveaux de service, indicateurs, données sources et rapports ;
- les risques, incidents, plans correctifs et décisions d'acceptation ;
- les factures, variations de coût, prévisions et engagements ;
- les preuves de diligence, les dates d'expiration et les revues programmées ;
- les conditions et étapes de renouvellement, transfert ou sortie.

Chaque champ critique doit avoir une source et un propriétaire. Si personne n'est responsable d'une donnée, elle devient rapidement obsolète. Le référentiel doit aussi distinguer une information confirmée d'une information déclarée ou inconnue.

### 4.2 Contrôler la qualité des données fournisseur

Les incohérences typiques incluent un contrat terminé toujours indiqué comme actif, un sous-traitant qui n'est plus à jour, un contact qui a quitté l'entreprise, des dates de préavis erronées, deux fiches pour le même fournisseur, une facture rattachée au mauvais contrat ou un indicateur dont la formule change selon les mois.

Un contrôle périodique peut comparer le référentiel aux contrats signés, aux données de facturation, aux outils de ticketing, aux inventaires techniques et aux attestations. L'automatisation permet de détecter les dates et écarts, mais les exceptions doivent rester examinées par une personne responsable.

La qualité du référentiel doit être mesurée en fonction des décisions qu'il soutient. Une donnée de contact qui sert à joindre une cellule d'urgence exige une vérification plus fréquente qu'un champ administratif peu utilisé. La conservation doit respecter les règles applicables et limiter les informations qui ne sont pas nécessaires au pilotage.

## 5. Gouvernance de la relation et collaboration

### 5.1 Adapter la relation au type de fournisseur

Un fournisseur transactionnel peut être géré par un processus simple de commande, de réception et de conformité de facture. Un partenaire stratégique, un opérateur d'infrastructure ou un prestataire critique peut exiger une gouvernance conjointe, un partage contrôlé de prévisions, des revues régulières, des exercices, un comité d'escalade et un plan de création de valeur.

Collaborer ne signifie pas renoncer aux contrôles. Une relation de confiance devrait rendre les problèmes visibles plus tôt, améliorer les résolutions et clarifier les dépendances. Elle ne doit pas créer une tolérance à des manquements contractuels non évalués, des changements non approuvés ou des accès non justifiés. Les mêmes personnes ne devraient pas à la fois négocier les intérêts commerciaux, certifier seules les résultats et accepter les risques les plus critiques.

### 5.2 Gouvernance à plusieurs niveaux

Un modèle de gouvernance peut comprendre :
- **Opérationnel :** suivi des tickets, changements, disponibilité, interventions et actions immédiates.
- **Tactique :** tendances, causes racines, ressources, coûts, risques, capacité et plans d'amélioration.
- **Stratégique :** évolution de la relation, valeur, dépendances, investissement, performance globale, risques majeurs et renouvellement.

Ces niveaux doivent s'alimenter. Un problème technique récurrent peut devenir un risque stratégique si le fournisseur ne peut pas maintenir une compétence. Un désaccord commercial peut bloquer une action opérationnelle et exiger un arbitrage. Un comité stratégique ne devrait pas traiter chaque ticket ; il doit résoudre les obstacles qui dépassent la délégation opérationnelle.

### 5.3 Cadence des réunions et décisions

La fréquence dépend de la criticité, de la performance et du changement. Les revues fréquentes sont utiles pendant un incident ou un démarrage, mais peuvent devenir inutiles si elles répètent les mêmes chiffres sans décisions. Une revue périodique doit utiliser un ordre du jour stable :
1. résultat de service et changements depuis la dernière revue ;
2. écarts aux obligations, tendances et causes ;
3. risques, dépendances et signaux faibles ;
4. état des actions et preuves d'efficacité ;
5. changements, capacité et prévisions ;
6. valeur, coût total et opportunités d'amélioration ;
7. décisions attendues, autorité, échéance et communication.

Chaque réunion produit des décisions et actions attribuées. Le compte rendu doit indiquer ce qui est approuvé, ce qui reste à confirmer, qui agit et quand le sujet revient. Une réunion sans décision peut être nécessaire pour informer, mais elle ne doit pas être confondue avec une revue de performance.

### 5.4 Désaccords et relation commerciale

Un désaccord de performance doit se fonder sur le contrat et les données, pas sur des accusations générales. Le fournisseur peut contester une mesure si la formule, la source ou les exclusions ne sont pas claires. L'acheteur doit pouvoir justifier le calcul. Si les deux parties ne peuvent pas reproduire le résultat, il faut traiter le défaut de mesure avant d'argumenter sur la pénalité.

Gérer la relation demande aussi une écoute réelle du fournisseur : une dépendance de l'acheteur peut empêcher la prestation, une demande de changement peut sortir du périmètre et une prévision de volume erronée peut affecter la capacité. La responsabilité doit être répartie sur les faits. Collaborer pour résoudre une cause ne signifie pas effacer les responsabilités contractuelles ; appliquer une clause sans vérifier le contexte peut toutefois aggraver le problème au lieu de le résoudre.

### Schéma — De la donnée brute à une décision de performance

~~~mermaid
flowchart TD
  A[Événements et mesures sources] --> B[Contrôle du périmètre et de l'horodatage]
  B --> C[Calcul selon la définition approuvée]
  C --> D[Comparaison à la cible et aux périodes précédentes]
  D --> E{Données fiables et résultat interprétable ?}
  E -->|Non| F[Corriger la mesure et déclarer la limite]
  E -->|Oui| G[Analyser impact, tendance et cause]
  F --> G
  G --> H[Décision, action et responsable]
  H --> I[Test ou revue au point suivant]
~~~

La mesure est un processus gouverné. Si les données sont incomplètes, le rapport doit le signaler au lieu de présenter une précision fictive. La décision tient compte de la qualité de la mesure et de la conséquence métier.

## 6. Mesurer la performance qui compte vraiment

### 6.1 Les indicateurs doivent éclairer une décision

Un KPI n'est pas utile parce qu'il est facile à compter. Il doit représenter un résultat ou un risque, avoir une définition stable, s'appuyer sur une source fiable et déclencher une décision possible. Le gestionnaire doit être capable d'expliquer la formule, le périmètre, les exclusions, la période et les limites.

Distinguer :
- **Résultat de service :** disponibilité, qualité, délai, exactitude, expérience utilisateur.
- **Processus :** prise en charge, affectation, escalade, respect des étapes.
- **Capacité :** charge, backlog, expertise, ressources et délais d'approvisionnement.
- **Conformité :** respect d'obligations, de contrôles et d'exigences de preuve.
- **Amélioration :** récurrence des incidents, efficacité des actions, réduction de coûts évitables.
- **Valeur :** réduction du risque, gains d'efficacité et qualité du résultat métier.

Un indicateur de processus ne remplace pas un indicateur de résultat. Un ticket peut être pris en charge dans le délai mais ne jamais être résolu. Le nombre de formations réalisées ne prouve pas que les opérateurs savent exécuter la procédure. Le volume de rapports fournis n'indique pas leur exactitude.

### 6.2 Définition de l'indicateur

Pour chaque KPI, documenter :
- le nom et la question de gestion ;
- la formule exacte et l'unité ;
- le périmètre inclus et exclu ;
- la source et le propriétaire des données ;
- la période, la fréquence et l'heure de référence ;
- le seuil, la cible et les niveaux d'escalade ;
- le traitement des incidents en cours ou des données manquantes ;
- les limites connues ;
- le destinataire du résultat et la décision attendue.

Si la formule change, conserver les anciennes définitions et expliquer la rupture de série. Sinon, une amélioration apparente peut simplement venir d'une modification de la méthode de calcul.

### 6.3 Exemples d'indicateurs et de pièges

| Indicateur | Définition à préciser | Piège possible |
|---|---|---|
| Disponibilité | Service, période, sonde, fenêtres et exclusions | Une sonde verte ne prouve pas que l'utilisateur peut travailler |
| Délai de prise en charge | Notification valide jusqu'au début d'une action qualifiée | Un accusé automatique peut être compté comme prise en charge |
| Temps de rétablissement | Début de l'impact jusqu'au retour de capacité définie | Le fournisseur peut fermer un ticket alors que le service reste dégradé |
| Taux de réouverture | Tickets réouverts / tickets clôturés, selon règles définies | Décourager la réouverture masque les problèmes au lieu de les résoudre |
| Défauts récurrents | Incidents de même cause ou symptôme selon classification stable | Une classification incohérente rend la tendance inutilisable |
| Respect des changements | Changements autorisés, testés et documentés | Une procédure légère peut être contournée si l'indicateur récompense seulement le volume |
| Prévision de consommation | Écart entre prévision et utilisation observée | Un biais de prévision peut affecter coût et capacité sans être imputable uniquement au fournisseur |
| Actions correctives efficaces | Actions qui passent le test défini / actions arrivées à échéance | Clôturer un ticket sans retest augmente artificiellement le taux de réussite |
| Exactitude de facturation | Factures conformes aux clauses, unités et preuves | Une facture correcte en forme peut contenir un volume non démontré |
| Satisfaction utilisateur | Méthode, population et taux de réponse documentés | Les réponses ne représentent pas nécessairement tous les utilisateurs |

### 6.4 Indicateurs équilibrés et effets pervers

Tout indicateur peut être manipulé, même sans fraude intentionnelle. Un délai de prise en charge trop dominant encourage à envoyer des accusés automatiques. Un objectif de clôture de tickets peut conduire à découper les incidents ou à fermer trop tôt. Une pénalité fondée uniquement sur la disponibilité peut détourner l'attention des erreurs de transaction. Un objectif de réduction des coûts peut faire diminuer la maintenance préventive, puis augmenter les pannes.

Pour limiter les effets pervers, équilibrer résultats, qualité, conformité, récurrence et expérience métier. Vérifier les indicateurs les uns contre les autres. Compléter les moyennes par des percentiles, des cas extrêmes et des données par criticité. Un service peut avoir 99,9 % de disponibilité mais subir une panne qui affecte toutes les commandes pendant l'heure la plus critique. Les indicateurs doivent rendre visible la concentration de l'impact.

### 6.5 Scorecard fournisseur

Une scorecard doit refléter les critères importants et inclure les commentaires, les actions et le niveau de confiance dans les données. Les poids sont propres à la prestation et ne doivent pas être copiés sans analyse.

Exemple pédagogique pour un service de maintenance critique :

| Dimension | Poids indicatif | Exemple de preuve |
|---|---:|---|
| Résultat et disponibilité du service | 25 % | Mesures indépendantes et incidents majeurs |
| Qualité de résolution et non-récurrence | 20 % | Causes racines, réouvertures et tests d'efficacité |
| Respect des engagements et communication | 15 % | Horodatages, escalades et comptes rendus |
| Continuité et sécurité | 15 % | Tests, preuves d'accès, sauvegarde et plans |
| Qualité de coopération et transfert | 10 % | Complétude de documentation et transfert de connaissances |
| Maîtrise des coûts et prévisions | 10 % | Factures, unités, tendances et écarts |
| Amélioration et valeur | 5 % | Résultats démontrés et risques supprimés |

Une note globale ne doit pas masquer un défaut critique. Une règle d'escalade peut imposer un plan d'action indépendant du score si une exigence de sécurité, une obligation majeure ou la continuité est compromise.

### Schéma — Du risque identifié à son acceptation maîtrisée

~~~mermaid
flowchart TD
  A[Événement de risque] --> B[Causes, conséquences et preuve]
  B --> C[Contrôles en place et lacunes]
  C --> D[Évaluer le risque actuel]
  D --> E[Réduire, transférer, éviter ou accepter]
  E --> F{Dans la délégation et la tolérance ?}
  F -->|Non| G[Escalade avec options et conséquences]
  F -->|Oui| H[Enregistrer propriétaire et échéance]
  G --> H
  H --> I[Mesurer l'efficacité et réévaluer]
~~~

Il faut calculer le risque après les contrôles réellement appliqués, pas après les actions prévues. Une acceptation n'est valable que si elle est prise par l'autorité habilitée et assortie d'une portée, d'une durée ou d'une date de réexamen.

## 7. Gérer les risques de bout en bout

### 7.1 Construire un registre de risques fournisseur

Pour chaque risque, consigner l'événement, la cause ou les facteurs, les conséquences, les contrôles existants, les signaux d'alerte, le responsable, la probabilité et l'impact selon la méthode locale, les mesures de réduction, le risque résiduel et la date de réexamen. Distinguer les faits observés des hypothèses. Un risque sans propriétaire, action ou décision d'acceptation reste simplement une liste de préoccupations.

Exemples :
- défaillance financière ou incapacité de maintenir les équipes ;
- perte d'une compétence rare ;
- fournisseur de rang deux non connu ou non remplaçable ;
- accès privilégié trop large ;
- vulnérabilité dans un produit ou un service livré ;
- indisponibilité régionale ;
- stockage ou transfert des données contraire aux exigences ;
- pièce en fin de vie ;
- hausse rapide des coûts ;
- non-respect répété du SLA ;
- litige sur la portée contractuelle ;
- absence de documentation ou d'export exploitable ;
- changement de propriétaire, fusion, cession ou réorganisation ;
- dépendance concentrée à un seul fournisseur ou à une même plateforme sous-jacente.

### 7.2 Probabilité, impact et risque résiduel

La cotation doit être un langage partagé, pas une précision fictive. Une note « 4 sur 5 » doit correspondre à une définition explicite. Le risque résiduel est celui qui subsiste après les contrôles et les actions réellement en place, pas après les mesures seulement prévues. Si une action n'est pas terminée, ne pas compter son bénéfice dans l'évaluation actuelle.

Les contrôles doivent être qualifiés comme préventifs, détectifs ou correctifs. Une obligation contractuelle de notification est un contrôle utile, mais elle ne prévient pas nécessairement l'incident. Une revue annuelle détecte certains changements, mais peut être trop lente si le fournisseur possède un accès permanent. Une assurance couvre certaines pertes selon des conditions, mais ne rétablit pas automatiquement le service.

Les risques critiques sont escaladés au rôle autorisé. Le gestionnaire fournisseur peut proposer des mesures et documenter l'analyse, mais ne doit pas accepter un risque qui dépasse sa délégation. Toute acceptation doit inclure un motif, un périmètre, une date d'expiration ou de réexamen et les signaux qui déclencheront une nouvelle décision.

### 7.3 Concentration et dépendance

Une entreprise peut dépendre :
- d'un fournisseur unique ;
- d'un fournisseur et de son distributeur exclusif ;
- d'un même cloud ou d'une même région pour plusieurs services ;
- d'une seule équipe spécialisée ;
- d'un logiciel qui impose un format propriétaire ;
- d'une seule personne connaissant les configurations ;
- d'un contrat dont les données ou actifs ne peuvent être récupérés rapidement.

Cartographier les dépendances et calculer l'effet d'une défaillance commune. La diversification n'est pas toujours la bonne réponse : multiplier les fournisseurs peut ajouter des interfaces, des coûts, des incohérences et de nouveaux risques. Comparer le bénéfice de substituabilité au coût de coordination et tester si les sources sont réellement indépendantes.

Une concentration peut être acceptée si l'alternative est trop coûteuse ou indisponible, mais elle doit être explicite et compensée : plan de continuité, documentation, stock, réserve de capacité, droits de sortie, tests réguliers et surveillance de l'évolution du marché.

### 7.4 Dépendances de rang deux et chaîne d'approvisionnement

Le fournisseur principal peut sous-traiter l'hébergement, le support, la logistique, le développement, le traitement de données ou des interventions. Les contrôles doivent se concentrer sur les sous-traitants qui peuvent affecter les résultats, l'accès ou la continuité. Demander la transparence nécessaire, les règles de notification des changements et les obligations de sécurité applicables, en respectant la confidentialité et le cadre contractuel.

Pour les prestations numériques, la chaîne peut inclure des composants logiciels, des bibliothèques, des services cloud, des systèmes de construction et des outils d'administration. NIST SP 800-161 Rev. 1, mise à jour finale en novembre 2024, propose une approche de gestion du risque de cybersécurité de la chaîne d'approvisionnement à plusieurs niveaux. Il faut vérifier la portée actuelle de la ressource avant de l'utiliser comme référentiel. Les exigences doivent ensuite être adaptées au risque et à l'architecture réellement achetée.

~~~mermaid
flowchart TD
  A[Service acheté] --> B[Fournisseur principal]
  B --> C[Sous-traitant d'exploitation]
  B --> D[Hébergement ou cloud]
  B --> E[Composants / éditeur]
  C --> F[Personnel et outils d'accès]
  D --> G[Région et connectivité]
  E --> H[Maintenance et mises à jour]
  F --> I[Impact sur le service]
  G --> I
  H --> I
  I --> J[Contrôles, preuve et plan de substitution]
~~~

Le schéma rappelle que le risque peut se trouver en dehors de l'entité qui signe le contrat. L'objectif n'est pas d'exiger une liste infinie de tous les fournisseurs indirects, mais de connaître suffisamment les dépendances susceptibles d'affecter le service et la capacité de réponse.

## 8. Risques de cybersécurité, données et accès

### 8.1 Évaluer selon l'accès réel

Un fournisseur qui n'accède qu'à une documentation publique présente un profil différent d'un prestataire qui administre les serveurs, accède aux données clients ou déploie du code en production. Définir la classification, les données, les comptes, les privilèges, les interfaces, les régions, les environnements et les opérations permises. La qualification doit être basée sur les accès réellement accordés, pas uniquement sur le nom de la prestation.

Les contrôles peuvent inclure l'authentification forte, des comptes nominatifs, le moindre privilège, la séparation des environnements, l'enregistrement des actions sensibles, les sessions temporaires, les revues d'accès, les procédures d'urgence, la gestion des vulnérabilités et la notification des incidents. Le choix et le niveau d'exigence dépendent du risque et des obligations réelles.

### Schéma — Contrôler un accès fournisseur sensible

~~~mermaid
flowchart TD
  A[Demande d'accès motivée] --> B[Propriétaire confirme le périmètre]
  B --> C[Sécurité vérifie les privilèges et conditions]
  C --> D{Autorisation valide ?}
  D -->|Non| E[Refuser ou demander une nouvelle justification]
  D -->|Oui| F[Accès nominatif et limité dans le temps]
  F --> G[Journaliser les actions sensibles]
  G --> H[Revue après intervention]
  H --> I[Révoquer ou renouveler selon besoin]
~~~

Un accès fournisseur doit avoir une finalité et un propriétaire. La revue après intervention permet de confirmer les modifications, de détecter un accès excessif et de mettre à jour l'inventaire. Les cas d'urgence doivent suivre un processus explicite et être contrôlés après usage.

### 8.2 Accès privilégiés et opérations à distance

Un accès fournisseur doit avoir un propriétaire, un motif, un périmètre, une durée, un mécanisme d'approbation, une journalisation et une procédure de révocation. Les comptes partagés rendent plus difficile la traçabilité ; les accès permanents augmentent l'exposition. Les exceptions d'urgence doivent rester limitées et examinées après usage.

Pour les opérations sensibles, prévoir une validation à deux personnes ou une fenêtre de changement contrôlée lorsque c'est nécessaire. Un fournisseur ne doit pas pouvoir modifier à la fois les contrôles qui surveillent son activité et les preuves qui servent à mesurer sa performance sans garde-fou. Les accès doivent être réévalués lors des changements d'équipe, de sous-traitant, de contrat ou de rôle.

### 8.3 Données, confidentialité et incident

Le contrat et le processus opérationnel doivent préciser les catégories de données traitées, les finalités permises, les lieux pertinents, les sous-traitants, la conservation, la suppression, les preuves d'incident et les responsabilités. Les clauses juridiques doivent correspondre au traitement réel. Une liste de sécurité générique ne remplace pas l'analyse des flux de données.

Définir comment le fournisseur signale un incident, quelles informations initiales sont nécessaires, comment les mises à jour sont transmises, qui peut engager des actions de confinement, comment préserver les preuves et comment coordonner la reprise. Le délai et le contenu de notification doivent suivre les lois, les contrats et les politiques applicables ; aucune valeur universelle ne convient à tous les cas.

### 8.4 Vérifier les preuves de sécurité

Examiner le périmètre de tout certificat, rapport d'audit ou attestation : entité juridique, site, produit, service, période, contrôles exclus, sous-traitants et exceptions. Vérifier si les mesures de correction sont documentées et si les contrôles couvrent les accès réellement accordés. Une attestation concernant le siège social ne prouve pas automatiquement que l'équipe qui exploite le service est dans le périmètre.

Les preuves expirées ou dont la portée ne correspond plus au service exigent une décision : obtenir une preuve actualisée, ajouter des contrôles compensatoires, limiter l'exposition ou faire approuver le risque résiduel par l'autorité compétente. Ne pas confondre « aucun incident signalé » avec « risque faible » si la visibilité du fournisseur est limitée.

## 9. Continuité opérationnelle et résilience fournisseur

### 9.1 Ce qui peut interrompre une prestation

Les perturbations peuvent provenir d'une panne de site, d'un événement climatique, d'un incident cyber, d'une rupture télécom, d'un problème logistique, d'une grève, d'un manque de compétence, d'une faillite, d'une défaillance de sous-traitant ou d'une modification du cadre réglementaire. Le plan de continuité fournisseur doit identifier les scénarios significatifs pour la prestation réelle, les moyens de détection, les rôles, les options de repli, les conditions de communication et les responsabilités.

Demander un plan générique ne suffit pas. Vérifier le périmètre des services couverts, les dépendances, le temps de mobilisation, les sites alternatifs, les compétences, les moyens de contact, les sauvegardes, les pièces et les résultats des exercices. Dans la mesure appropriée, l'acheteur doit participer à un test ou examiner une preuve qui concerne son propre service.

### 9.2 Relier la continuité du fournisseur aux besoins de l'acheteur

Les objectifs de continuité doivent être cohérents. Un fournisseur peut avoir un objectif de reprise plus long que celui que l'acheteur a promis à ses utilisateurs. Il faut vérifier où les objectifs diffèrent, quel mode dégradé existe et qui accepte la conséquence. Le service peut aussi dépendre d'un sous-traitant dont le plan est moins mature que celui du fournisseur principal.

Documenter les scénarios de panne, les contacts d'escalade, les solutions temporaires, les conditions de transfert vers une alternative, les besoins de données, les actions à réaliser par l'acheteur et les critères de reprise. Les tests doivent mesurer le résultat réel plutôt qu'accepter une simple déclaration de disponibilité.

~~~mermaid
flowchart TD
  A[Incident chez le fournisseur] --> B[Notification et qualification]
  B --> C[Évaluer l'impact sur le service acheté]
  C --> D{Continuité fournisseur suffisante ?}
  D -->|Oui| E[Activer plan et suivre les preuves]
  D -->|Non| F[Mode dégradé ou solution de substitution]
  E --> G[Validation du résultat métier]
  F --> G
  G --> H[Revue des causes et du risque résiduel]
  H --> I[Actions et test d'efficacité]
~~~

### 9.3 Scénarios de test

Les tests peuvent varier :
- exercice sur table pour les rôles et les décisions ;
- test d'un contact de secours ou d'un accès d'urgence ;
- restauration d'un jeu de données ou d'une configuration dans un environnement isolé ;
- démonstration de la capacité à fournir des pièces ou à faire venir un expert ;
- test de réversibilité sur un export de données ;
- test de reprise coordonné entre le fournisseur et l'acheteur ;
- exercice de crise avec un événement injecté.

Chaque test doit avoir un but, un périmètre, une date, des participants, une règle d'arrêt et des critères d'acceptation. Un test incomplet n'est pas inutile : il faut clairement indiquer ce qu'il démontre et ce qu'il ne démontre pas.

### 9.4 Dépendance à une personne clé

Une relation peut être fragile même si l'entreprise fournisseur semble solide. Un seul ingénieur peut connaître l'installation, un seul commercial peut détenir les informations contractuelles ou un seul technicien peut avoir les habilitations utiles. Identifier les compétences indispensables, les remplaçants, les délais de mobilisation, la documentation et les actions de transfert.

Les demandes de transfert doivent rester contractuellement et juridiquement fondées. Le plan peut prévoir de la documentation, des formations croisées, des exercices avec une personne de relève et un dépôt contrôlé des configurations. Les informations confidentielles restent protégées, mais ne doivent pas être retenues au point d'empêcher l'acheteur d'exploiter le service qu'il a payé.

## 10. Gérer les incidents, écarts et plans correctifs

### 10.1 Distinguer incident, non-conformité et tendance

Un incident est un événement opérationnel. Une non-conformité est un écart par rapport à une exigence ou à une obligation. Une tendance est une évolution qui peut annoncer une dégradation. Ils peuvent se recouper, mais nécessitent des réponses différentes. Un incident ponctuel sans violation contractuelle peut demander une amélioration ; un manquement à une exigence critique peut déclencher une procédure formelle même si le service est ensuite rétabli.

Le gestionnaire établit les faits : chronologie, impact, périmètre, données, obligations, actions du fournisseur et dépendances de l'acheteur. Les hypothèses restent explicitement identifiées. Avant de demander une pénalité ou d'annoncer un défaut grave, vérifier les clauses, les mesures et la procédure d'escalade. Une réaction excessive peut augmenter le risque et détériorer la relation ; une réaction trop lente peut rendre la non-conformité habituelle.

### 10.2 Une analyse de cause n'est pas une recherche de coupable

Une analyse de cause utile examine les conditions et mécanismes qui ont permis l'événement : qualité de la conception, capacité, changement, surveillance, compétence, procédure, équipement, communication, contrat ou dépendance. Elle doit distinguer la cause technique, les facteurs contributifs et les défauts de contrôle. Une phrase comme « erreur humaine » n'est pas une explication suffisante si le processus permet facilement la même erreur.

La méthode choisie dépend de la complexité : chronologie, cinq pourquoi, arbre causal ou analyse structurée plus poussée. Il est important de ne pas imposer prématurément une cause unique lorsque plusieurs facteurs ont contribué. Le résultat doit conduire à des actions qui réduisent le risque de récurrence et à des critères qui prouvent leur efficacité.

### 10.3 Plan correctif robuste

Un plan correctif contient :
- un écart observé et sa preuve ;
- l'impact ou le risque associé ;
- la cause et les facteurs, avec le niveau de confiance ;
- une action concrète et son propriétaire ;
- un délai et les dépendances ;
- une mesure temporaire jusqu'à correction ;
- une preuve de mise en œuvre ;
- un test d'efficacité ;
- le risque résiduel si la correction échoue ou est retardée ;
- l'autorité qui accepte ce risque et la date de réexamen.

La clôture ne doit pas dépendre uniquement d'un statut dans un outil. Si une procédure a été réécrite, faire exécuter un scénario par une autre équipe. Si la capacité est en cause, mesurer sous la charge attendue. Si un problème de qualité de données est observé, vérifier un échantillon défini ou une période pertinente. La preuve doit correspondre au défaut initial.

~~~mermaid
flowchart TD
  A[Écart observé] --> B[Valider la preuve et l'obligation]
  B --> C[Analyser causes et facteurs]
  C --> D[Définir action, propriétaire et délai]
  D --> E[Mettre en œuvre et garder une mesure transitoire]
  E --> F[Tester l'efficacité]
  F --> G{Défaut supprimé ?}
  G -->|Non| H[Réviser le plan et escalader]
  H --> C
  G -->|Oui| I[Clore avec preuve et réviser le risque]
~~~

### Schéma — Escalade proportionnée d'un écart

~~~mermaid
flowchart TD
  A[Écart confirmé ou risque majeur] --> B[Équipe opérationnelle et action immédiate]
  B --> C{Résultat dans le délai convenu ?}
  C -->|Oui| D[Vérifier l'efficacité et documenter]
  C -->|Non| E[Plan correctif formel]
  E --> F{Progrès et risque acceptables ?}
  F -->|Oui| G[Suivi rapproché avec critères]
  F -->|Non| H[Arbitrage contractuel et risque]
  H --> I{Reste dans les délégations ?}
  I -->|Oui| J[Appliquer le remède prévu]
  I -->|Non| K[Escalade exécutive / juridique]
  K --> L[Décision documentée]
  J --> L
  G --> D
~~~

L'escalade doit être fondée sur des seuils et des preuves. Elle ne remplace pas la résolution opérationnelle : les mesures de continuité, de sécurité ou de confinement peuvent être requises pendant que les discussions contractuelles se poursuivent.

### 10.4 Escalade progressive

Une escalade utile est déclenchée par des seuils prévus : criticité de l'incident, dépassement de SLA, répétition, absence de progrès, risque financier, défaut de sécurité ou non-réponse. Chaque niveau doit identifier qui participe, quelle décision est attendue et à quel moment le problème est réexaminé.

Un modèle peut comporter :
1. échange opérationnel avec actions et échéance ;
2. plan correctif formel avec revue rapprochée ;
3. arbitrage contractuel et commercial ;
4. comité exécutif ou de risque pour les conséquences majeures ;
5. mécanismes formels de différend, remèdes ou sortie selon le contrat.

L'escalade doit éviter deux extrêmes : menacer prématurément de résiliation pour chaque incident, ou maintenir indéfiniment des réunions sans résultat. Les communications restent factuelles, consignées et proportionnées. Les engagements, concessions et décisions doivent être pris par les personnes habilitées.

## 11. Gérer le coût, les factures et la valeur

### 11.1 Relier facture et preuve de service

La conformité d'une facture se vérifie contre le contrat, les tarifs, les unités, les périodes, les livrables, les autorisations et les preuves de consommation ou de réception. Un processus fiable compare les lignes facturées à la source opérationnelle et signale les écarts : volumes inhabituels, doublons, frais non prévus, indexation incorrecte, déplacement sans autorisation ou jalon non accepté.

Ne pas bloquer tout paiement sans analyse parce qu'une ligne est contestée. Suivre la procédure contractuelle, isoler l'écart, protéger les droits de l'organisation et payer les sommes indiscutées selon les règles applicables. Les modalités exactes relèvent du contrat et du droit applicable.

### 11.2 Évaluer le coût total de la relation

Le coût complet peut inclure le prix contractuel, les dépenses internes de pilotage, les coûts d'intégration, les changements, les incidents, la formation, les frais de déplacement, la gestion de la qualité, les coûts d'indisponibilité et la sortie. Ces éléments ne sont pas tous imputables au fournisseur ; il faut comprendre leur origine avant de décider.

La comparaison doit rester cohérente avec les règles de financement et de comptabilité. Éviter les coûts fictifs ou les hypothèses ajoutées après coup pour justifier une décision. Les scénarios servent à éclairer les choix, par exemple poursuivre avec un plan correctif, changer le périmètre, renégocier ou préparer une substitution.

### 11.3 Identifier la valeur au-delà des économies

La valeur fournisseur peut résider dans une réduction de risque, une qualité plus stable, un délai raccourci, un transfert de compétences ou une capacité nouvelle. Chaque bénéfice doit avoir une base de comparaison, une mesure et un responsable. Une promesse de gain d'efficacité doit intégrer les coûts de mise en œuvre, de changement et d'exploitation supplémentaire.

Le partage de gains ou les mécanismes incitatifs exigent des règles transparentes : métrique, base de référence, attribution, coûts inclus, audit, limites et traitement des effets indésirables. Une incitation mal définie peut pousser le fournisseur à optimiser un indicateur plutôt que le résultat global.

## 12. Changements, renégociation et amélioration

### 12.1 Gérer les changements sans perdre la maîtrise

Tout changement significatif de périmètre, de technologie, de sous-traitant, de région, de données, d'équipe clé, de prix ou de niveau de service doit être analysé. Le processus vérifie le besoin, la justification, la conformité contractuelle, le coût, les délais, les risques, la sécurité, la continuité et l'autorité. La décision est enregistrée avant exécution, sauf processus d'urgence explicitement prévu.

Les changements cumulés méritent une vue d'ensemble. Plusieurs petits avenants peuvent transformer le risque ou la portée globale. Contrôler leur effet cumulatif sur le prix, les obligations, la procédure d'achat, les ressources et la possibilité de remettre le marché en concurrence. Ne pas traiter chaque changement comme isolé si l'ensemble modifie profondément l'accord initial.

### 12.2 Renégocier : préparer des options

La renégociation peut concerner des prix, des volumes, le niveau de service, des délais, des ressources, la portée, la gouvernance ou la sortie. Avant la réunion, établir la base contractuelle, les résultats mesurés, les coûts, les alternatives, les dépendances, les concessions disponibles et les limites d'autorisation. Définir ce qui doit absolument être résolu et les sujets sur lesquels un compromis est possible.

La meilleure alternative à l'accord négocié doit être réaliste, pas imaginaire. Si aucun autre fournisseur ne peut reprendre le service avant dix-huit mois, menacer d'une sortie immédiate n'est pas une position crédible. Il faut développer une stratégie de réduction progressive de la dépendance, documenter ce que la transition exige et éviter de compromettre la continuité pour obtenir une concession à court terme.

### 12.3 Innovation et amélioration conjointe

Un fournisseur peut proposer une automatisation, une nouvelle méthode de diagnostic, une réduction de consommation ou une modification d'architecture. Examiner la proposition avec une méthode distincte des opérations courantes : problème ciblé, valeur attendue, coût, prérequis, risque, test, propriété intellectuelle, réversibilité et critères de succès.

Les expérimentations doivent être autorisées, contenues et mesurées. Un pilote réussi dans un périmètre limité ne garantit pas la capacité à généraliser. Définir l'environnement, les données, la durée, les personnes impliquées, les critères d'arrêt et la décision qui suivra. Les économies ou bénéfices ne sont comptabilisés qu'après vérification.

## 13. Renouvellement, remise en concurrence et sortie fournisseur

### 13.1 Démarrer tôt la décision

La date de renouvellement ne doit pas être la date de début de réflexion. Les préavis, la durée de transition, les tests, le budget, les autorisations et les délais de marché peuvent être longs. Définir une échéance de décision en amont, avec les responsabilités et les livrables requis.

La revue de renouvellement considère :
- les résultats réels par rapport aux engagements ;
- la récurrence des défauts et l'efficacité des corrections ;
- le coût total, les changements et la prévisibilité ;
- la pertinence du besoin et les options disponibles ;
- la dépendance, la concentration et les risques de continuité ;
- la conformité, les incidents de sécurité et les preuves manquantes ;
- la qualité de documentation et la possibilité de sortie ;
- l'état du marché et la crédibilité d'une alternative ;
- les conséquences d'un changement et les coûts de transition ;
- les contraintes de la procédure et du contrat applicable.

### Schéma — Préparer une décision de renouvellement ou de sortie

~~~mermaid
flowchart TD
  A[Revue à l'avance de l'échéance] --> B[Performance, risques, coûts et marché]
  B --> C[Tester la capacité de sortie et la transition]
  C --> D[Comparer renouvellement, correction, concurrence ou internalisation]
  D --> E{Risque acceptable et décision autorisée ?}
  E -->|Oui, poursuivre| F[Renouveler avec conditions et objectifs]
  E -->|Non ou valeur insuffisante| G[Préparer remise en concurrence ou sortie]
  F --> H[Mettre à jour le contrat et la gouvernance]
  G --> I[Planifier données, accès, compétences et continuité]
  H --> J[Contrôle à date définie]
  I --> J
~~~

Il faut commencer la décision avant les préavis et la durée de transition. Une bonne performance courante n'efface pas un risque de dépendance ; inversement, un incident ne prouve pas à lui seul qu'un changement de fournisseur sera plus sûr.

### 13.2 Options de décision

Une décision n'est pas limitée à « renouveler » ou « résilier immédiatement ». Les options peuvent inclure le renouvellement aux conditions existantes, un renouvellement conditionnel avec plan correctif, une renégociation permise, une remise en concurrence, un changement de périmètre, une internalisation partielle, une solution hybride ou une sortie ordonnée. Chaque option comporte un coût, un risque et un calendrier.

| Option | Quand elle peut être pertinente | Contrôles indispensables |
|---|---|---|
| Renouveler | Résultats adaptés, risque maîtrisé, procédure permise | Justifier la valeur et confirmer les objectifs futurs |
| Renouveler sous conditions | Écarts corrigeables et contrôle du risque possible | Jalons, conséquences, preuve d'efficacité et date de réexamen |
| Renégocier | Les clauses, la stratégie et le cadre permettent l'évolution | Autorité, base contractuelle, limites et piste écrite |
| Remettre en concurrence | Marché viable et besoin de comparaison ou de substitution | Calendrier, continuité, données et transfert |
| Internaliser partiellement | Certaines compétences sont stratégiques ou doivent être maîtrisées | Capacité interne, recrutement, documentation et transfert |
| Sortir / remplacer | Risque excessif, besoin modifié ou performance durablement inacceptable | Plan de sortie, droits, données, continuité et obligations restantes |

La décision doit être fondée sur des preuves et approuvée selon les délégations. Une préférence personnelle pour un fournisseur ne remplace pas l'analyse, et une mauvaise performance ne suffit pas à prouver qu'un autre fournisseur pourra réussir sans préparation.

### 13.3 Planifier la réversibilité

Le plan de sortie commence avec l'achat. Il précise les données à restituer, les formats, les configurations, les licences, la documentation, les contacts, la formation, les actifs, les journaux, les accès, les obligations de confidentialité et la suppression des copies. Il décrit les responsabilités du fournisseur sortant, du successeur et de l'acheteur.

Pour une solution numérique, la réversibilité peut inclure l'export des données, schémas, historiques, configurations, scripts, secrets remis selon un canal sûr, documentation d'exploitation, règles de supervision, inventaire d'interfaces et procédure de restauration. Tout ne peut pas être exigé dans tous les contrats : définir les droits et livrables pertinents, puis vérifier qu'ils sont juridiquement et techniquement possibles.

Le test de réversibilité doit mesurer la capacité de récupérer, comprendre et réutiliser les informations. Un fichier exporté n'est pas utile s'il est incomplet, non documenté, dans un format illisible ou dépourvu des identifiants qui relient les objets. Un test sur un échantillon peut révéler les limites avant la sortie complète.

~~~mermaid
flowchart TD
  A[Décision de sortir] --> B[Autoriser et planifier la transition]
  B --> C[Inventaire données, actifs et connaissances]
  C --> D[Export et transfert sécurisé]
  D --> E[Importer dans l'environnement cible]
  E --> F[Contrôler complétude et intégrité]
  F --> G{Service cible validé ?}
  G -->|Non| H[Corriger et conserver le secours selon plan]
  H --> E
  G -->|Oui| I[Transfert opérationnel accepté]
  I --> J[Révoquer accès du sortant]
  J --> K[Confirmer restitution, suppression et clôture]
~~~

### 13.4 Après la sortie

La clôture inclut l'inventaire des livrables reçus, le statut des paiements, les différends ouverts, les garanties restantes, les actifs et licences, les comptes désactivés, les données et copies, les accès, les responsabilités de support résiduel et les preuves de suppression si prévues. Le service doit rester surveillé pendant le transfert et après l'ouverture par le successeur.

Le retour d'expérience examine ce qui a bien fonctionné, ce qui a été perdu, les coûts non prévus, les lacunes de contrat et les risques qui auraient pu être détectés plus tôt. Les résultats alimentent les prochains appels d'offres, les modèles de contrats et les règles de qualification. La sortie est un test de la qualité de la relation : si l'organisation ne peut pas quitter un fournisseur sans interrompre l'activité, la dépendance a été mal maîtrisée en amont.

## 14. Outils de travail et modèles réutilisables

### 14.1 Fiche d'identité et de criticité fournisseur

| Champ | Contenu attendu |
|---|---|
| Identité | Raison sociale, identifiant et entité contractante |
| Service / contrat | Périmètre réel, version, durée et options |
| Propriétaires | Métier, opérationnel, contrat, sécurité et risque |
| Segment | Niveau de criticité et justification |
| Dépendances | Sous-traitants, plateformes, compétences, sites et pièces |
| Accès / données | Type d'accès, privilèges et catégories de données |
| Continuité | Contacts, options de secours, tests et limites |
| Performance | KPI, source, période, seuils et dernières tendances |
| Risques | Risques résiduels, propriétaires, échéances et décisions |
| Coûts | Prix, évolution, coûts hors contrat et prévision |
| Échéances | Renouvellement, préavis, diligence, preuves et tests |
| Sortie | Formats, délais, livrables, coûts et dernier test |

### 14.2 Modèle de scorecard de revue

| Dimension | Résultat observé | Cible / engagement | Tendance | Preuve / source | Décision ou action |
|---|---|---|---|---|---|
| Résultat de service | À renseigner | Contrat / besoin | Stable, amélioration ou baisse | Mesure reproductible | Action si écart |
| Incidents critiques | À renseigner | Seuil convenu | Fréquence et impact | Chronologie et rapports | Analyse de cause |
| Qualité corrective | À renseigner | Critères d'efficacité | Répétition ou suppression | Tests et données | Clôture ou escalade |
| Sécurité / continuité | À renseigner | Contrôles convenus | Évolution des risques | Preuves et limites | Réduction ou arbitrage |
| Coût / facture | À renseigner | Prix et volumes | Variation | Contrat et source opérationnelle | Validation ou contestation |
| Documentation / transfert | À renseigner | Livrables prévus | Retard / complétude | Révision ou exercice | Action attribuée |
| Valeur / amélioration | À renseigner | Base de comparaison | Gain démontré | Mesure avant/après | Étendre ou abandonner |

Ne pas confondre cette scorecard avec une évaluation automatique du fournisseur. Les commentaires et les risques critiques doivent rester visibles, même si la moyenne est favorable. La réunion de revue doit aboutir à des décisions concrètes et à des responsables.

### 14.3 Registre de risques fournisseur

| Risque / événement | Cause ou facteur | Impact | Contrôle actuel | Risque résiduel | Propriétaire | Action / date |
|---|---|---|---|---|---|---|
| À définir | Fait ou hypothèse | Service, coûts, données ou conformité | Preuve du contrôle | Niveau restant | Rôle responsable | Action mesurable et échéance |

Un risque résiduel est calculé après prise en compte des contrôles effectivement appliqués. Une action prévue mais non achevée ne doit pas être considérée comme efficace. Les risques hors délégation sont transmis à l'autorité compétente.

### 14.4 Agenda type d'une revue trimestrielle

1. Vérification des décisions et actions précédentes.
2. Résultats de service et écarts contractuels.
3. Incidents, causes racines et récurrence.
4. Évolution de la criticité, des accès, données et sous-traitants.
5. Risques, continuité et preuves d'exercice.
6. Facturation, évolution de coût et prévisions.
7. Changements, capacité et feuille de route.
8. Valeur créée et améliorations démontrées.
9. Renouvellement, préavis et réversibilité.
10. Décisions, responsables, échéances et prochain contrôle.

Une revue trimestrielle n'est pas obligatoire pour tous les fournisseurs. La fréquence dépend de la criticité, des engagements, du changement et des risques. En situation majeure, un rythme plus rapproché peut être nécessaire ; pour une relation transactionnelle faible, un contrôle simplifié suffit.

### 14.5 Exemple de décision d'escalade

**Situation :** trois incidents similaires ont affecté le service en deux mois. Le fournisseur a respecté le délai de prise en charge pour deux incidents, mais les délais de rétablissement ont dépassé l'objectif à deux reprises. La cause annoncée est différente à chaque fois, mais aucune analyse n'explique pourquoi les symptômes sont similaires.

**Décision possible :** ouvrir un plan correctif formel, demander une analyse consolidée, exiger une vérification indépendante des causes si le contrat le permet, renforcer temporairement la surveillance et fixer une date d'examen. L'action est close uniquement après un test ou une période de preuve qui correspond au risque. Si le seuil d'escalade contractuel est atteint, appliquer également la procédure prévue, sans transformer le plan correctif en dispense implicite d'obligations.

## 15. Atelier pratique — revue trimestrielle d'un fournisseur critique

### Situation de départ

Une organisation utilise un prestataire pour maintenir une application qui traite des commandes et synchronise l'entrepôt. Le contrat prévoit des niveaux de service, des rapports mensuels, un plan de continuité, une notification des incidents et des livrables documentaires. Au cours du trimestre :
- deux incidents critiques ont duré plus longtemps que l'objectif de rétablissement ;
- les tickets ont été pris en charge dans le délai pour la majorité des cas ;
- la documentation de la dernière modification est incomplète ;
- le rapport fournisseur présente une disponibilité favorable, mais utilise une méthode de calcul non expliquée ;
- un sous-traitant technique a changé sans que l'équipe interne sache si la notification prévue a été reçue ;
- le renouvellement est à dix mois, et le dernier test d'export des données remonte à plus d'un an.

Les éléments sont fictifs. L'apprenant doit vérifier les preuves, éviter les conclusions non étayées et préparer une revue qui produise des décisions.

### Phase A — Reconstituer la relation

Rassembler le contrat signé, les avenants, les KPI, les tickets, les changements, les factures, les rapports, les obligations de notification et le registre des sous-traitants. Vérifier la version et les formules. Séparer les éléments confirmés des données manquantes. Déterminer qui détient l'autorité sur les décisions de risque et de remède contractuel.

**Livrable :** une fiche de situation avec faits, inconnues, obligations concernées et questions à résoudre.

### Phase B — Valider les mesures

Recalculer les indicateurs à partir des sources, ou demander les données brutes si le rapport ne permet pas de reproduction. Vérifier le périmètre, les exclusions et la date de début et de fin des incidents. Distinguer le délai de prise en charge du rétablissement. Décrire la qualité des données et le niveau de confiance dans les résultats.

**Livrable :** une scorecard qui présente les chiffres et leurs limites, pas seulement une note globale.

### Phase C — Évaluer les risques

Analyser l'effet des incidents, la documentation incomplète, le changement de sous-traitant et la réversibilité non testée. Établir les dépendances, les contrôles existants et les mesures urgentes. Vérifier si les accès ou données sont concernés par le changement du sous-traitant et si une notification ou une approbation était requise.

**Livrable :** un registre de risques avec propriétaire, action, échéance, preuve et risque résiduel.

### Phase D — Construire un plan d'amélioration

Demander une analyse consolidée des incidents, fixer un calendrier de correction, définir la preuve et le test d'efficacité. Clarifier la méthode de calcul des KPI. Vérifier le référentiel de sous-traitants. Programmer un test de réversibilité et les actions qui doivent précéder le renouvellement. Les mesures temporaires doivent être proportionnées à l'impact.

**Livrable :** un plan d'action avec priorités, dépendances, responsables et règles d'escalade.

### Phase E — Décider du renouvellement

Évaluer si les écarts sont corrigibles, si le fournisseur tient ses engagements, si les coûts restent soutenables et si une alternative est réaliste. Commencer tôt la remise en concurrence éventuelle. Si un renouvellement conditionnel est envisagé, vérifier qu'il est autorisé et définir des conditions mesurables. Si une sortie est nécessaire, planifier les données, les accès, la documentation, les équipes et la continuité.

**Livrable :** une note de décision avec options, coûts, risques, limites et approbations.

### Critères de réussite de l'atelier

La revue est réussie si les indicateurs sont reproductibles, les écarts reliés aux obligations, les hypothèses séparées des faits, les risques hiérarchisés, les actions mesurables et la décision de renouvellement prise assez tôt. Une note favorable ou défavorable sans preuve n'est pas suffisante.

## 16. Études de cas et corrections

### Cas 1 — Le rapport fournisseur n'est pas reproductible

Le fournisseur annonce une disponibilité de 99,95 %, mais les données brutes, les exclusions et le périmètre ne sont pas fournis. L'équipe interne observe pourtant des interruptions signalées par les utilisateurs.

**Analyse :** aucune des deux perceptions ne doit être acceptée sans vérification. Le contrat et la méthode de mesure sont examinés, les sources sont comparées, les incidents sont horodatés et les exclusions sont testées. Il faut déterminer si la sonde ne couvre qu'une fonction technique, si certaines plages sont exclues ou si les tickets utilisateur portent sur une dégradation non comptée.

**Correction :** exiger la reproduction du calcul selon les droits et clauses applicables, documenter les écarts et revoir la mesure si elle est insuffisante. Toute modification future de la formule doit être approuvée et conservée sans effacer l'historique. Ne pas attribuer une non-conformité avant d'avoir établi la règle et les faits ; ne pas accepter une moyenne non vérifiable comme preuve suffisante.

### Cas 2 — Un sous-traitant change sans visibilité

Le fournisseur principal annonce qu'une partie de l'exploitation est désormais assurée par un partenaire. Le contrat exige une notification préalable pour certaines catégories de sous-traitance. Le gestionnaire ne trouve pas de dossier d'approbation.

**Analyse :** le fait du changement doit être confirmé et comparé au contrat. Il faut vérifier le périmètre, les accès, les données, les régions, les compétences, les obligations de notification et les risques de continuité. L'absence de dossier dans le référentiel ne prouve pas à elle seule qu'aucune notification n'a été faite ; il faut chercher les preuves et consigner l'incertitude.

**Correction :** demander les éléments contractuellement prévus, évaluer le risque avec sécurité, métier et juridique, prendre une décision sur les mesures de limitation et mettre à jour le référentiel. Si une approbation ou un remède contractuel est requis, suivre la procédure locale. La relation commerciale ne doit pas remplacer le contrôle d'un changement sensible.

### Cas 3 — Le renouvellement est préparé trop tard

À deux mois de l'échéance, l'équipe découvre qu'une nouvelle consultation nécessiterait au moins cinq mois, que la documentation est incomplète et que seul le fournisseur actuel sait reconstruire l'environnement.

**Analyse :** le retard a réduit la capacité de négociation et créé une dépendance. Il faut distinguer les solutions juridiquement autorisées — prolongation, procédure de transition, nouvel achat ou internalisation partielle — et mesurer leurs risques. Il n'est pas acceptable de supposer qu'un renouvellement est automatiquement permis parce que le calendrier a été mal géré.

**Correction :** documenter les options, solliciter les autorités compétentes et protéger la continuité, tout en préparant un plan de réduction de dépendance. Pour les prochains contrats, instaurer des jalons de décision suffisamment tôt et vérifier périodiquement la réversibilité.

### Cas 4 — La moyenne masque des incidents à fort impact

Un fournisseur respecte le SLA dans 98 % des tickets. Les 2 % hors délai concernent cependant l'accès aux commandes pendant les périodes de pointe.

**Analyse :** le taux moyen ne pondère pas suffisamment la criticité métier. Le pilotage doit séparer les tickets par priorité, période et impact, examiner les événements extrêmes et vérifier les conséquences de chaque dépassement. Une moyenne n'est pas un substitut à des seuils de crise.

**Correction :** établir des indicateurs par criticité, une analyse de l'impact métier, des règles d'escalade et un plan de capacité. Les pondérations doivent être reliées au besoin et ne doivent pas être modifiées rétroactivement pour faire apparaître le fournisseur meilleur ou moins bon.

### Cas 5 — Les pénalités n'améliorent pas la performance

L'acheteur applique des crédits de service chaque mois, mais les incidents continuent. Le fournisseur présente les crédits comme une réduction de facture et aucune action corrective n'est testée.

**Analyse :** le mécanisme financier ne traite pas nécessairement la cause. Il faut vérifier si le contrat prévoit une démarche corrective, examiner le comportement incitatif, chercher la cause récurrente et définir des preuves d'amélioration. Les droits financiers et la résolution du problème sont deux questions complémentaires.

**Correction :** combiner l'application du contrat, lorsque requise, avec un plan correctif vérifiable : actions, responsabilités, échéances, mesures transitoires, test et seuil d'escalade. Les écarts récurrents peuvent mener à une décision de risque, de renégociation ou de sortie selon le contrat.

### Cas 6 — Le fournisseur propose une innovation

Un fournisseur propose d'automatiser le diagnostic et promet une réduction de 25 % du temps de traitement. Le mécanisme requiert un accès supplémentaire aux logs et une modification de l'architecture.

**Analyse :** l'innovation a une valeur potentielle mais introduit des risques d'accès, de données, de fonctionnement et de dépendance. La réduction annoncée est une hypothèse, pas un bénéfice démontré. Il faut cadrer un pilote, la sécurité, les mesures avant/après, la réversibilité et les droits sur les éléments produits.

**Correction :** autoriser seulement un essai approuvé, isolé et mesurable. Définir les données, le périmètre, les critères de réussite et d'arrêt, la supervision, les coûts, les responsabilités et les droits. Étendre le dispositif uniquement après preuve suffisante et décision formelle.

## 17. Exercices d'application avec corrigés détaillés

### Exercice 1 — Segmenter un petit fournisseur critique

**Question :** un fournisseur ne représente que 1 % des dépenses, mais il est le seul à fournir une pièce dont l'absence peut arrêter une ligne de production pendant plusieurs jours. Comment le classer ?

**Correction :** la dépense ne domine pas l'analyse. Il faut évaluer l'impact d'une rupture, la substituabilité, les délais, la possibilité de réparer ou de stocker, les dépendances de rang deux et le coût d'une indisponibilité. Il peut être classé comme critique malgré une faible facture. Les mesures peuvent inclure un stock raisonnable, une seconde source qualifiée, la documentation et un plan d'approvisionnement alternatif. Il faut éviter de constituer un stock sans gérer l'obsolescence ni vérifier la compatibilité.

### Exercice 2 — Le SLA est respecté mais le service souffre

**Question :** le fournisseur respecte le délai de prise en charge, mais les utilisateurs attendent des heures avant de retrouver le service. Quelle mesure manque ?

**Correction :** la prise en charge mesure une étape et ne prouve pas le rétablissement. Il faut suivre le temps de rétablissement, la résolution définitive, l'impact métier, les cas extrêmes et les causes récurrentes. Les formules et les points de mesure doivent être définis dans le contrat ou selon le mécanisme de gouvernance prévu. La correction peut inclure une meilleure classification, des procédures d'escalade, des compétences disponibles ou une capacité de secours.

### Exercice 3 — Distinguer déclaration et preuve

**Question :** un fournisseur déclare que son plan de continuité est « testé chaque année », mais ne fournit ni périmètre ni résultat. Que conclure ?

**Correction :** la déclaration constitue une information à vérifier. Demander la portée, le scénario, la date, les services inclus, les résultats, les écarts, les actions et les limites, dans les droits et obligations prévus. Un rapport d'exercice peut lui-même ne couvrir qu'une partie du service. La décision dépend du risque : accepter provisoirement avec mesure compensatoire, exiger une preuve supplémentaire ou limiter l'exposition. Ne pas transformer l'absence de rapport en preuve automatique d'absence de test, ni la déclaration en preuve suffisante de résilience.

### Exercice 4 — Sous-traitant de rang deux

**Question :** le fournisseur principal respecte son SLA, mais l'hébergement partagé par plusieurs services subit une panne majeure. Pourquoi une analyse du fournisseur principal seule ne suffit-elle pas ?

**Correction :** la disponibilité des services dépend d'une capacité sous-jacente commune. Il faut cartographier le sous-traitant pertinent, l'infrastructure ou région partagée, les responsabilités de notification et l'option de secours. Les indicateurs du fournisseur principal doivent être interprétés au regard de la chaîne. Exiger la transparence suffisante sur les dépendances critiques et préparer des mesures de continuité réalistes ; diversifier sans analyser les causes communes peut seulement déplacer le risque.

### Exercice 5 — Fermer une action corrective

**Question :** le fournisseur réécrit une procédure après un incident. Peut-on fermer l'action ?

**Correction :** seulement si l'action visait uniquement la correction documentaire et si la preuve attendue est satisfaite. Si le défaut concernait une exécution, l'accès, la restauration ou le délai, il faut un test correspondant. Une personne différente de l'auteur de la procédure peut exécuter le scénario et produire une preuve d'efficacité. Si le test échoue, l'action reste ouverte, le plan est révisé et le risque résiduel est examiné.

### Exercice 6 — Pénalité ou plan d'amélioration

**Question :** une non-conformité donne droit à un crédit contractuel, mais le service est encore en danger. Quelle approche est correcte ?

**Correction :** appliquer le contrat selon le processus prévu, mais ne pas considérer le crédit comme une correction du défaut. Définir des mesures immédiates, une action de cause racine, une échéance, un responsable, un test et un seuil d'escalade. Vérifier les délégations de décision et communiquer de façon factuelle. La continuité ou la sécurité peut exiger une action urgente indépendante du règlement financier.

### Exercice 7 — Renouveler un fournisseur performant mais verrouillant

**Question :** le fournisseur atteint ses KPI, mais les données et configurations sont dans un format propriétaire et le coût de sortie est inconnu. Faut-il renouveler ?

**Correction :** la performance courante est un facteur important mais ne suffit pas. Évaluer le coût et la faisabilité de sortie, le risque de dépendance, les alternatives, les délais de migration, les droits contractuels et la valeur future. Une option peut être de renouveler sous conditions d'amélioration de la réversibilité si cela est autorisé et négociable ; une autre est de préparer une remise en concurrence ou une internalisation partielle. La décision doit être prise assez tôt et chiffrée, pas sous la seule pression de l'échéance.

### Exercice 8 — Rapport de performance contradictoire

**Question :** les chiffres du fournisseur et de l'acheteur diffèrent de 7 %. Que faire avant de parler de manquement ?

**Correction :** comparer les définitions, le périmètre, les fuseaux horaires, les périodes, les exclusions, les sources, les incidents et les règles de calcul. Identifier un échantillon de cas, refaire le calcul et consigner l'écart. Si la définition contractuelle manque de précision, solliciter les responsables compétents et suivre la procédure de changement pour les périodes futures ; ne pas imposer rétroactivement une formule nouvelle sans base. Une mesure non reproductible est d'abord un problème de gouvernance de données.

### Exercice 9 — Évaluer un risque de sous-traitance

**Question :** un fournisseur veut sous-traiter une partie de la maintenance à une équipe située dans une autre région, avec potentiellement un nouvel accès à des données. Quelles étapes suivre ?

**Correction :** vérifier le contrat et le processus d'autorisation ou de notification ; identifier les tâches, les données, les lieux, les privilèges et les personnes ; évaluer les exigences juridiques et de sécurité ; examiner la qualification, le contrôle des accès, la continuité, le transfert de responsabilité et les preuves. Décider avec les autorités compétentes avant l'accès lorsque l'accord l'exige. Mettre à jour le référentiel, les risques et les contacts. Le simple fait que le fournisseur principal reste responsable ne supprime pas tous les risques de rang deux.

### Exercice 10 — Choisir une action de valeur

**Question :** un fournisseur annonce une économie de 15 % après automatisation. Quelles preuves sont nécessaires avant de considérer le gain comme réalisé ?

**Correction :** définir la base de comparaison et les coûts inclus, mesurer le volume et la qualité avant et après, intégrer le coût d'automatisation, de supervision, de formation, de licence et de changement, et contrôler que la qualité du service ne s'est pas dégradée. Définir la méthode et le périmètre du calcul. Si les économies reposent sur une hypothèse de charge différente, présenter cette limite. Le bénéfice devient crédible lorsque le résultat est vérifié et peut être reproduit.

## 18. Défi final — piloter un fournisseur critique de bout en bout

### Scénario

Une organisation dépend d'un prestataire pour l'exploitation d'une application de commandes. Le fournisseur répond rapidement aux tickets, mais deux pannes majeures ont dépassé les objectifs de rétablissement. Le rapport mensuel affiche une bonne disponibilité sans fournir les données nécessaires à la reproduction du calcul. L'accès d'administration est géré par le prestataire ; l'inventaire des comptes et sous-traitants est incomplet. La documentation d'exploitation n'est pas à jour. Le contrat arrive à échéance dans dix mois, et le test de réversibilité n'a jamais été réalisé. Le fournisseur affirme que le changement serait risqué et coûteux. Une autre solution existe sur le marché, mais la capacité de migration n'est pas vérifiée.

### Travail demandé

Produire un dossier de gestion fournisseur comportant :
1. une segmentation motivée du fournisseur et un modèle de gouvernance ;
2. le référentiel minimal des services, contrats, propriétaires, accès, données et sous-traitants ;
3. une analyse des KPI et de la qualité des mesures, avec les données à demander ;
4. un registre des risques, en distinguant faits, hypothèses et incertitudes ;
5. une analyse des causes possibles des incidents et un plan correctif mesurable ;
6. les mesures immédiates de réduction du risque sur les accès et la documentation ;
7. une méthode de revue de sécurité et de dépendances de rang deux ;
8. un plan de continuité fournisseur et un test de reprise adapté au service ;
9. un tableau des coûts, risques et options pour renouveler, renégocier ou remplacer ;
10. un calendrier de décision avant les préavis et la date de fin ;
11. un plan de réversibilité avec responsabilités, formats, vérifications et conditions d'arrêt ;
12. une note de recommandation indiquant l'autorité, les risques résiduels et la prochaine date de réexamen.

### Correction de référence

**Segmentation.** Le fournisseur doit être classé selon l'impact métier, la dépendance, les accès et le délai de substitution. La valeur des factures ne suffit pas. Établir le propriétaire métier, opérationnel, contractuel et sécurité, les suppléants et une cadence de revue adaptée.

**Performance.** Demander la formule de disponibilité, les données sources et les exclusions ; rapprocher les rapports des événements observés. Distinguer l'accusé ou la prise en charge du rétablissement réel. Comparer par criticité et examiner les incidents extrêmes plutôt que se fier à la moyenne.

**Risques.** Inscrire les comptes privilégiés non inventoriés, les sous-traitants incertains, la documentation obsolète, la mesure non reproductible et la réversibilité non testée. Chaque risque reçoit un propriétaire, une échéance et une mesure de réduction. Les accès sensibles doivent être examinés selon les procédures et les autorisations ; toute révocation ou modification doit éviter de perturber le service sans plan.

**Plan correctif.** Demander une analyse consolidée des deux pannes, des changements liés, des facteurs de surveillance, de capacité et de compétence. Définir des actions comme mettre à jour l'inventaire, valider la documentation par exécution indépendante, tester le rétablissement et rendre la mesure de disponibilité reproductible. Les actions doivent être retestées.

**Continuité et sécurité.** Vérifier les services de rang deux, les accès, la capacité, les sauvegardes, les contacts de crise et les tests du fournisseur. Mettre au clair les responsabilités et les délais d'escalade. Faire remonter à l'autorité compétente tout risque qui dépasse la délégation. Les contrôles doivent correspondre à l'exposition réelle de l'application.

**Options commerciales.** Comparer un renouvellement conditionnel, une renégociation permise, une remise en concurrence et une substitution progressive. Inclure le coût de transition, la continuité, la formation, l'export et la capacité interne. La déclaration du fournisseur selon laquelle la sortie est coûteuse n'est ni une preuve que la sortie est impossible ni une preuve que la proposition concurrente est viable. Chiffrer et tester.

**Réversibilité.** Définir données, configurations, inventaires, procédures, historiques, licences, accès, livrables, transfert de connaissances, coûts, délai et tests d'intégrité. Tester tôt un export représentatif et documenter les limites. Prévoir une solution de continuité et des critères d'arrêt si les données ne sont pas réutilisables.

**Décision.** Le renouvellement ne doit pas être automatiquement accordé pour éviter un risque de transition, ni refusé uniquement en réaction aux incidents. Une recommandation défendable combine données de performance, risque, coût complet, alternatives et calendrier. Elle indique les conditions, l'autorité, le risque résiduel et le prochain jalon. Les décisions contractuelles suivent le contrat, les délégations et le cadre applicable.

### Barème pédagogique sur 100

| Dimension | Points |
|---|---:|
| Segmentation, propriétaires et gouvernance | 15 |
| Qualité des mesures et analyse de performance | 15 |
| Registre des risques et sécurité des accès | 15 |
| Plan correctif et preuve d'efficacité | 15 |
| Continuité et dépendances de rang deux | 10 |
| Comparaison des options et coûts de transition | 10 |
| Réversibilité testable et maîtrise des échéances | 15 |
| Traçabilité, approbations et risques résiduels | 5 |

Une excellente réponse rend visibles les incertitudes, évite les décisions prématurées et transforme les constats en actions mesurables. Elle ne confond pas la bonne relation commerciale avec l'absence de contrôle.

## 19. Références et méthode de veille

Les ressources suivantes sont des points d'appui méthodologiques. Leur applicabilité dépend du type de fournisseur, du secteur, du contrat, de la juridiction et des obligations réellement en vigueur.

- [NIST SP 800-161 Rev. 1, mise à jour finale](https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final) : pratiques de gestion des risques de cybersécurité dans la chaîne d'approvisionnement. Le site NIST indique une mise à jour finale au 1er novembre 2024 ; vérifier le périmètre et les mises à jour avant de l'utiliser comme référence de contrôle.
- [ISO 44001:2017 — Management collaboratif des relations d'affaires](https://www.iso.org/standard/72798.html) : cadre pour identifier, développer et gérer les relations d'affaires collaboratives. L'ISO indique une révision de projet ISO/DIS 44001 en cours en 2026 ; le projet ne doit pas être présenté comme une norme publiée ou une obligation applicable avant son statut final.
- [ISO/TS 44005:2026 — Recommandations de leadership pour le travail collaboratif](https://www.iso.org/fr/standard/87388.html) : ressource publiée en juin 2026 sur le leadership dans les relations collaboratives, utile lorsque la coopération inter-organisationnelle est réellement centrale.
- [Banque mondiale — Contract Management Practice Procurement Guidance, juin 2024](https://thedocs.worldbank.org/en/doc/a5487590ccec42b5709816f40ae8b068-0290012024/contract-management-practice-procurement-guidance-june-2024-final) : conseils sur la gouvernance du contrat, la mesure de performance, les scorecards et les actions correctives. Son cadre d'application dépend du projet et des règles de financement.
- [OCDE — Recommandation sur les marchés publics](https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0411) : principes de transparence, intégrité, gestion des risques, responsabilité et efficacité utiles pour réfléchir à la gouvernance des relations contractuelles.
- [OCDE — Guide sur le devoir de diligence pour une conduite responsable des entreprises](https://www.oecd.org/en/publications/oecd-due-diligence-guidance-for-responsible-business-conduct_9789264292684-en.html) : approche de diligence raisonnable et de gestion des impacts négatifs dans les chaînes d'activité, à adapter aux exigences applicables.

La veille doit enregistrer le titre de la source, son édition ou sa date, son statut, les points utilisés, les limites et le responsable de la vérification. Une norme ou un guide n'est pas une preuve automatique de conformité. Il faut relier les exigences applicables aux contrats, responsabilités, contrôles et résultats observés.

## Synthèse finale

Une gestion fournisseur experte repose sur une segmentation pertinente, un référentiel fiable, des preuves proportionnées, une mesure qui reflète réellement le service, une gouvernance adaptée et une maîtrise des risques de chaîne. Les indicateurs sont utiles s'ils éclairent une décision ; la collaboration est utile si elle améliore le résultat sans effacer les responsabilités ; les plans correctifs sont utiles s'ils sont vérifiés. La continuité n'est pas garantie par la seule présence d'un plan, pas plus que la performance n'est démontrée par une moyenne flatteuse.

Le gestionnaire doit préserver la capacité de l'organisation à décider. Il sait quand demander une preuve, quand lancer une action corrective, quand escalader, quand renégocier et quand préparer une alternative. Il anticipe les échéances contractuelles, les dépendances aux personnes et aux sous-traitants, la sortie et le transfert des connaissances. Enfin, il transforme les incidents et les revues en améliorations du prochain appel d'offres et du modèle de gestion.

La qualité de la relation ne se mesure ni au nombre de réunions ni à l'absence apparente de conflit. Elle se mesure à la transparence des risques, à la fiabilité des résultats, à la résolution des problèmes, à l'équilibre des intérêts et à la capacité à maintenir le service tout en restant libre de ses décisions.
