# Rédaction d'appels d'offres — niveau expert

> **Mise en contexte —** Un appel d’offres n’est pas un formulaire destiné à recueillir plusieurs prix. C’est un dispositif de décision qui transforme un besoin métier en exigences vérifiables, rend les offres comparables, protège l’équité de traitement, maîtrise les risques et prépare l’exécution du contrat. Une consultation mal conçue peut sélectionner le fournisseur le moins cher à court terme tout en créant des coûts de migration, une dépendance technique, une interruption de service ou des litiges. À l’inverse, un dossier proportionné au besoin aide les fournisseurs à comprendre la demande, à chiffrer les risques et à proposer des solutions crédibles. Le niveau expert consiste à articuler stratégie d’achat, analyse du marché, rédaction technique, méthode d’évaluation, gouvernance, contrat, transition, exploitation et sortie du fournisseur. Les règles exactes dépendent du pays, du secteur, du statut de l’acheteur, du financement et de la procédure retenue : les exemples ci-dessous sont des méthodes de travail, jamais une substitution aux règles applicables.

## Objectifs de maîtrise

À l’issue de ce cours, l’apprenant doit pouvoir :
- traduire un besoin métier en stratégie d’achat, résultat attendu et périmètre justifié ;
- mener une analyse de marché sans orienter indûment la concurrence vers un fournisseur ;
- choisir entre achat standard, consultation de solutions, appel d’offres, demande de propositions ou autre procédure autorisée ;
- décider si un marché doit être alloti, regroupé, renouvelé, internalisé ou organisé en accord-cadre ;
- rédiger des exigences fonctionnelles, techniques, de service, de sécurité et de transition qui sont mesurables et vérifiables ;
- distinguer conditions de participation, exigences éliminatoires, critères d’évaluation et obligations contractuelles ;
- concevoir une grille de notation pondérée, explicable, calibrée et reproductible ;
- comparer le coût total de possession, les risques et la valeur sur le cycle de vie, plutôt que le seul prix initial ;
- organiser la consultation, répondre aux questions de manière équitable, sécuriser la réception des offres et documenter les décisions ;
- prévenir les conflits d’intérêts, les biais, les collusions et les modifications non autorisées de critères ;
- préparer la négociation uniquement lorsqu’elle est permise et dans un cadre documenté ;
- transformer l’offre retenue en contrat pilotable, avec indicateurs, niveaux de service, recette, gestion du changement et plan de sortie ;
- préparer une transition fournisseur sans perte de compétences, de données, de contrôle ou de continuité ;
- produire un dossier d’achat auditable, justifier les arbitrages et exploiter les retours d’expérience pour améliorer les consultations suivantes.

Le niveau expert se reconnaît à la qualité des hypothèses, à la traçabilité des choix, au caractère vérifiable des exigences et à la capacité d’anticiper ce qui se produira après la signature.

## Prérequis et limites de responsabilité

Le cours s’adresse à un professionnel qui connaît le besoin métier, les principes de gestion des fournisseurs et les contraintes d’exploitation. Le prérequis du parcours est le cours « Gestion de crise et Plan de Reprise » : cette continuité n’est pas fortuite. Un achat de maintenance, d’infrastructure ou de service critique doit tenir compte des scénarios d’indisponibilité, des objectifs de reprise, des dépendances et de la capacité à changer de fournisseur.

Il faut distinguer au minimum quatre situations :
- **Achat privé :** les règles dépendent des procédures internes, du droit applicable, des engagements contractuels et des principes de gouvernance de l’organisation.
- **Marché public :** la procédure, les seuils, les délais, la publicité, les critères, les recours et la signature sont déterminés par la législation et la réglementation applicables.
- **Achat financé par un bailleur ou un programme :** des règles particulières peuvent s’ajouter au cadre national et au contrat de financement.
- **Achat réglementé ou sensible :** les données, infrastructures, produits, services essentiels ou secteurs concernés peuvent imposer des exigences supplémentaires de sécurité, de traçabilité ou d’autorisation.

Ne jamais importer mécaniquement une procédure d’une juridiction ou d’un bailleur dans une autre. Le document de consultation doit identifier le régime réellement applicable et la personne compétente pour confirmer les formalités. Les ressources citées à la fin sont des références de méthode. Elles ne suffisent pas à conclure à la conformité juridique d’un dossier.

## 1. Le cycle d’achat de bout en bout

Un appel d’offres n’est qu’une étape d’un cycle plus large. Le cycle commence par la définition du besoin et se poursuit jusqu’à la réception, à la mesure du contrat, à son renouvellement ou à la sortie du fournisseur. Une procédure de consultation performante qui ne prépare pas l’exploitation peut tout de même déboucher sur un contrat raté.

~~~mermaid
flowchart TD
  A[Besoin métier documenté] --> B[Stratégie et analyse du marché]
  B --> C[Budget et gouvernance]
  C --> D[Spécifications et dossier]
  D --> E[Publication ou invitation]
  E --> F[Questions et réponses équitables]
  F --> G[Réception et ouverture]
  G --> H[Évaluation selon les critères publiés]
  H --> I[Décision, contrôles et attribution]
  I --> J[Contrat et plan de transition]
  J --> K[Exécution, réception et paiement]
  K --> L[Mesure, risques et changements]
  L --> M[Renouveler, remettre en concurrence ou sortir]
  M --> N[Retour d'expérience]
  N --> B
~~~

Chaque étape produit une preuve : note de besoin, analyse des options, stratégie d’achat, budget, validation du dossier, avis publié, registre des questions, procès-verbal de réception, rapport d’évaluation, autorisations, contrat signé, procès-verbal de recette, rapport de performance et plan de sortie. Une procédure de haute qualité peut être comprise par un réviseur indépendant qui n’a pas participé aux décisions.

### Portes de décision : empêcher le dossier de partir trop tôt

Les validations doivent être conçues comme des portes de décision, et non comme des signatures automatiques. Le dossier ne devrait pas être publié tant que l’on ne sait pas quelle procédure est autorisée, ce qui est acheté, comment les offres seront comparées, qui financera le contrat et comment le résultat sera accepté.

~~~mermaid
flowchart TD
  A[Besoin identifié] --> B{Besoin et options documentés ?}
  B -->|Non| C[Compléter la note de cadrage]
  C --> B
  B -->|Oui| D{Budget, régime et procédure validés ?}
  D -->|Non| E[Arbitrage finance, achats et juridique]
  E --> D
  D -->|Oui| F{Exigences et critères vérifiables ?}
  F -->|Non| G[Revoir le dossier et la matrice de preuves]
  G --> F
  F -->|Oui| H[Autorisation de publication]
~~~

Un dossier techniquement complet peut encore être immature si le budget n’est pas confirmé, si le fournisseur de données n’a pas été identifié ou si le délai de transition est irréaliste. La porte de décision fait apparaître ces obstacles avant qu’ils deviennent des avenants, des retards ou un litige.

### 1.3 Gouvernance de l'achat et responsabilités

Une matrice de responsabilités doit préciser qui est responsable de chaque livrable, qui approuve, qui contribue et qui doit être informé. Elle évite que la rédaction soit confiée exclusivement aux achats ou exclusivement à la technique. Les achats maîtrisent la procédure et la comparaison ; le métier décrit le résultat ; les spécialistes techniques définissent les contraintes et tests ; les finances valident le modèle budgétaire ; le juridique examine le risque contractuel ; la sécurité évalue les exigences liées aux données, aux accès et à la continuité.

La séparation des tâches doit être proportionnée à la valeur et au risque. Une personne ne devrait pas pouvoir, sans contrôle, créer le besoin, choisir seule les candidats, noter les offres, approuver l'attribution et certifier la facture. Dans une petite organisation, la séparation complète n'est pas toujours possible ; il faut alors des contrôles compensatoires, comme une revue indépendante ou une approbation à deux niveaux.

Un registre des décisions devrait indiquer le sujet, les options, la recommandation, l'autorité, la date, la justification et les conditions de réexamen. Un « accord oral » sans trace est fragile, surtout lorsque les personnes changent ou que le dossier est contesté.

### 1.1 Les questions à résoudre avant de rédiger

Avant de lancer la rédaction, réunir le propriétaire métier, l’équipe technique, les achats, les finances, le juridique, la sécurité et, le cas échéant, les responsables environnementaux ou sociaux. Cette équipe doit clarifier :
- quel résultat le besoin doit produire ;
- pourquoi le besoin existe maintenant et ce qui se passerait si l’achat était reporté ;
- quelles options existent, y compris l’amélioration de l’existant, l’internalisation, le partage de ressources ou l’absence d’achat ;
- quel budget total et quel financement sont disponibles, à quel moment et sous quelles conditions ;
- quels risques sont acceptables, quels risques sont à éliminer et quelle autorité les accepte ;
- comment le résultat sera mesuré et qui aura la responsabilité de la réception ;
- quels actifs, données, compétences et contrats seront concernés à la fin du marché.

Un besoin exprimé comme « acheter une nouvelle plateforme » présuppose déjà une solution. Il faut d’abord comprendre la difficulté : délai de traitement, taux d’erreur, disponibilité, coût d’exploitation, manque de capacité, vulnérabilité, incompatibilité ou dépendance fournisseur. Une fois le problème défini, l’acheteur peut comparer plusieurs solutions sans imposer un choix prématuré.

### 1.2 Le cadrage écrit

La note de cadrage peut rester courte, mais doit rendre les arbitrages explicites. Elle comprend le problème, les bénéficiaires, les résultats attendus, le périmètre inclus et exclu, les options envisagées, les contraintes, les dépendances, le calendrier, le budget, les risques majeurs, les critères de réussite et les validations requises.

Le cadrage doit aussi distinguer les faits des hypothèses. Si le volume à traiter est estimé, indiquer la source, la période observée, les variations saisonnières et la marge d’incertitude. Une hypothèse commerciale incertaine peut entraîner une offre imprécise, des réserves tarifaires et des demandes de changement en cours de contrat.

## 2. Choisir la stratégie d’achat et comprendre le marché

### 2.1 Analyse make, buy, reuse et hybrid

L’achat externe n’est pas toujours la meilleure réponse. Comparer la construction ou l’exploitation en interne, l’achat d’un service, la réutilisation d’une capacité existante, une mutualisation ou une solution hybride. La comparaison porte sur la valeur, le délai, les compétences, la maîtrise, la flexibilité, la sécurité, les coûts de cycle de vie et les risques d’exécution.

| Option | Questions à examiner |
|---|---|
| Faire en interne | Disposons-nous des compétences, de la capacité et de la disponibilité sur la durée ? |
| Acheter | Le marché offre-t-il une solution adaptée, testable et soutenable ? |
| Réutiliser l’existant | Peut-on atteindre le résultat par configuration, rationalisation ou amélioration ? |
| Mutualiser | Les besoins, calendriers, règles et niveaux de service sont-ils compatibles ? |
| Approche hybride | Quelles capacités sont stratégiques à conserver, et lesquelles peuvent être confiées au fournisseur ? |

Une comparaison sérieuse évite de présenter l’achat comme la seule option déjà approuvée. Elle conserve une trace des hypothèses, des limites et de la raison de l’option retenue.

### 2.2 Analyse du marché et consultation préliminaire

L’analyse de marché sert à connaître les solutions disponibles, les fournisseurs, les délais, les modèles de prix, les contraintes d’intégration, les normes, les évolutions attendues et les risques de dépendance. Elle peut s’appuyer sur des informations publiques, des références, des démonstrations encadrées, des échanges préliminaires permis et une analyse des contrats similaires.

Il faut séparer l’analyse de marché de la sélection. L’objectif n’est pas de faire gagner un fournisseur déjà connu, mais de mieux définir le besoin et la stratégie. Les échanges préalables doivent être conduits avec prudence : ne pas transmettre des informations confidentielles à un acteur, ne pas accorder un avantage indu, ne pas faire dépendre les exigences d’une solution propriétaire sans justification, et conserver une trace des enseignements utiles à la consultation.

Si un fournisseur contribue à une étude ou à une démonstration, analyser les risques de conflit d’intérêts et les mesures d’équité nécessaires selon le cadre applicable. Les informations réellement utiles au marché doivent, lorsque les règles le requièrent, être rendues accessibles de façon équitable à tous les candidats.

### 2.3 Structure du marché et concurrence

Analyser le nombre de fournisseurs capables, les coûts d’entrée, les compétences rares, les contraintes géographiques, les dépendances aux pièces, les barrières d’intégration et les risques de concentration. Un marché avec deux fournisseurs réellement capables peut justifier des précautions différentes d’un marché avec vingt solutions interchangeables.

Ne pas confondre un grand catalogue de fournisseurs avec une concurrence réelle. Des fournisseurs peuvent dépendre du même éditeur, du même distributeur, de la même chaîne logistique ou du même sous-traitant. Pour un service critique, vérifier le fournisseur de rang deux, la disponibilité des pièces, les temps d’approvisionnement et le soutien en cas de défaillance régionale.

### 2.4 Allotissement et regroupement

L’allotissement peut ouvrir le marché à des entreprises plus petites, permettre une spécialisation et éviter qu’un seul fournisseur contrôle toute la chaîne. Toutefois, il augmente les interfaces, les responsabilités de coordination et les risques de contestation mutuelle entre titulaires. Un marché global peut simplifier la responsabilité et l’intégration, mais il peut réduire la concurrence, augmenter la dépendance et rendre plus difficile un changement partiel de fournisseur.

| Question | Allotissement possible | Marché global possible |
|---|---|---|
| Les prestations peuvent-elles être définies et réceptionnées séparément ? | Oui | Pas nécessairement |
| Des fournisseurs spécialisés existent-ils sur chaque lot ? | Oui | Le marché peut favoriser un intégrateur |
| Les interfaces sont-elles maîtrisables ? | Oui, avec gouvernance inter-lots | Plus de responsabilité centralisée |
| Le risque de dépendance fournisseur est-il élevé ? | Peut permettre une substitution partielle | Peut concentrer le risque |
| Un responsable unique est-il indispensable ? | Coordination renforcée nécessaire | Une responsabilité intégrée peut être utile |

La décision doit être justifiée par le besoin et par l’analyse du marché. Il ne faut pas diviser artificiellement un achat pour contourner une procédure ou, à l’inverse, regrouper des prestations sans rapport pour restreindre les candidats.

### 2.5 Choisir une procédure autorisée

Les appellations varient selon les régimes. Une procédure ouverte, une consultation sur liste limitée, un appel d’offres en deux étapes, une demande de propositions, une procédure avec dialogue ou une négociation ne sont pas interchangeables. Le choix dépend de la réglementation applicable, de la complexité du besoin, de l’état du marché et de l’autorisation interne.

Le dossier de stratégie précise la méthode choisie, sa justification, les étapes, les délais, la façon dont les offres seront reçues, les critères de sélection, les possibilités de clarification ou de négociation et les voies de recours lorsqu’elles sont prévues. Les règles de négociation et de modification des offres sont particulièrement dépendantes du cadre juridique : ne pas présumer qu’une pratique autorisée en achat privé est permise en marché public.

### 2.6 Stratégie de sourcing et continuité d'approvisionnement

La stratégie de sourcing décide comment accéder au marché, quelles catégories de fournisseurs sont admissibles, comment la capacité sera vérifiée et comment le risque d'approvisionnement sera réduit. Pour des pièces critiques ou une prestation de maintenance, il ne suffit pas d'étudier le tarif : il faut identifier le délai de disponibilité, les stocks locaux ou régionaux, les composants de rang deux, les droits de distribution, la capacité de dépannage et la dépendance à une seule personne experte.

Les points d'analyse comprennent le nombre de fournisseurs réellement indépendants, les substitutions autorisées, la disponibilité des pièces en fin de vie, les contraintes d'exportation ou de transport lorsqu'elles s'appliquent, la concentration géographique, les délais de douane, le support du constructeur et la dépendance à un distributeur unique. Les risques doivent être examinés sans transformer des hypothèses en certitudes : demander des preuves adaptées et définir des actions de réduction.

Pour les catégories récurrentes, une stratégie de catégorie peut agréger les achats, harmoniser certaines exigences, négocier des conditions cohérentes et améliorer la visibilité des volumes. Cette agrégation doit toutefois être mise en balance avec le risque de concentration et les conséquences d'une défaillance commune. Un contrat unique peut réduire la charge administrative tout en augmentant le rayon d'impact d'un défaut fournisseur.

~~~mermaid
flowchart TD
  A[Catégorie d'achat] --> B[Évaluer marché et concentration]
  B --> C[Analyser criticité et substitutions]
  C --> D{Source unique inévitable ?}
  D -->|Oui| E[Plan de continuité et stock / compétences]
  D -->|Non| F[Évaluer multi-sourcing ou lots]
  E --> G[Mesures contractuelles et tests]
  F --> G
  G --> H[Surveiller dépendances et marché]
~~~

Le plan de continuité d'approvisionnement peut inclure une source alternative qualifiée, un stock raisonnable, une documentation transférable, un délai d'escalade, un mécanisme d'approbation d'équivalence et un inventaire des pièces en fin de vie. Il doit aussi tenir compte du coût d'obsolescence : maintenir un stock sans politique de rotation et sans vérifier la compatibilité peut créer de la perte plutôt que de la résilience.

## 3. Définir un besoin mesurable et rédiger le cahier des charges

### 3.1 Résultats, fonctions et solutions

Une exigence fonctionnelle décrit ce que le service doit permettre. Une exigence technique fixe une propriété nécessaire de la solution lorsque cette propriété est justifiée. Une exigence de service précise la performance et les conditions de prise en charge. Une exigence de conformité décrit une obligation qui doit être respectée. Une exigence de transition ou de sortie garantit que le résultat pourra être mis en service, maintenu et remplacé sans perdre le contrôle.

Privilégier les résultats et fonctions lorsque plusieurs solutions peuvent les fournir. Prescrire une technologie précise seulement si la compatibilité, la sécurité, la standardisation, la maintenance ou une autre contrainte documentée le justifie. Les références à une marque ou une version doivent suivre les règles applicables et, le cas échéant, comporter les équivalences autorisées.

### 3.2 La formule d’une exigence testable

Une exigence claire définit :
- le sujet ou la capacité attendue ;
- le comportement ou le résultat exigé ;
- les conditions de mesure ;
- l’unité, le seuil ou la tolérance ;
- la méthode de vérification et les preuves recevables ;
- le moment où le contrôle aura lieu ;
- la conséquence d’un résultat non conforme, selon le contrat.

Exigence trop vague : « Le système doit être rapide et fiable. »

Exigence exploitable : « Dans l’environnement de recette décrit en annexe, avec 250 sessions simultanées et un jeu de données de volume défini, le 95e percentile de réponse de la fonction de recherche doit rester inférieur ou égal à 2,0 secondes lors d’un essai de 30 minutes après échauffement. Le fournisseur remet les mesures brutes, la configuration du test, les erreurs et les limites observées. »

Le chiffre est un exemple fictif. Il ne doit être conservé que s’il correspond au besoin et a été validé. Une exigence qui cite un seuil sans expliquer le scénario peut être techniquement mesurable mais commercialement irréaliste.

### 3.3 Éviter les exigences contradictoires ou impossibles à prouver

Les termes « moderne », « innovant », « robuste », « intuitif », « hautement sécurisé » ou « disponibilité maximale » ne décrivent pas une preuve. Les transformer en résultats opérationnels ou en critères d’évaluation annoncés. Les objectifs de disponibilité doivent préciser la période, le périmètre, les maintenances exclues ou incluses, le point de mesure, les dépendances et les règles de calcul.

Éviter de demander simultanément une architecture propriétaire précise et une indépendance complète vis-à-vis de ce fournisseur. Éviter de fixer un délai de réparation incompatible avec le temps de livraison des pièces. Éviter les obligations dont l’acheteur ne sait pas vérifier l’exécution. Un cahier des charges doit être relu pour détecter les contradictions entre les annexes techniques, les délais, les prix, les pénalités et le contrat.

### 3.4 Exigences de maintenance, disponibilité et continuité

Pour un achat de maintenance ou un service essentiel, décrire les périodes de service, les catégories d’incident, les délais de prise en charge, les objectifs de rétablissement, les conditions d’escalade, les astreintes, les pièces, les compétences et les dépendances. Distinguer l’accusé de réception, le début effectif de l’intervention, le contournement, le rétablissement et la résolution définitive.

Les objectifs de reprise doivent correspondre aux besoins métier et aux capacités réellement achetées. Si le fournisseur fournit une sauvegarde, préciser les responsabilités de sauvegarde, de conservation, de chiffrement, de test de restauration et de remise de données à la fin du contrat. Un engagement générique du type « sauvegardes quotidiennes » ne garantit ni un RPO acceptable ni une restauration rapide.

Définir les scénarios d’escalade : perte d’un site, rupture fournisseur, indisponibilité des identités, cyberincident, indisponibilité de pièces et défaillance du sous-traitant. Exiger, lorsque c’est proportionné, un plan de continuité fournisseur, des preuves d’exercice, des contacts de crise, les délais de notification et les mécanismes de coopération. Le fournisseur doit expliquer les dépendances qu’il contrôle et celles qu’il ne contrôle pas.

### 3.5 Sécurité, données et propriété intellectuelle

Un dossier sérieux précise la classification des données, les finalités, les contrôles d’accès, le chiffrement, la journalisation, la gestion des vulnérabilités, la notification d’incident, la localisation ou le transfert des données si applicable, les sous-traitants et les exigences de suppression ou de restitution. Il doit distinguer les exigences obligatoires et les éléments qui seront évalués comme avantages.

Définir les droits d’usage, la propriété des développements, les licences, le traitement des composants tiers, la documentation remise et les conditions de réversibilité. Une clause de propriété intellectuelle vague peut rendre le changement de fournisseur coûteux ou juridiquement difficile. Le juridique doit valider le texte, particulièrement lorsque les livrables réutilisent des composants préexistants.

### 3.6 Accessibilité, durabilité et responsabilité

Les achats peuvent contribuer à la sécurité, à l’accessibilité, à la durabilité environnementale, aux pratiques sociales et à l’innovation. Ces objectifs doivent être pertinents pour le besoin, autorisés par le cadre applicable, proportionnés, mesurables et pris en compte dans le dossier de manière transparente.

Ne pas insérer un critère écologique ou social de façade qui ne peut être vérifié. Définir plutôt les preuves acceptables : consommation énergétique mesurée selon une méthode, durée de vie des équipements, réparabilité, disponibilité des pièces, reprise ou recyclage, accessibilité selon une norme identifiée, ou processus de gestion de la chaîne de sous-traitance. Vérifier que les exigences n’introduisent pas une restriction injustifiée du marché.

### 3.7 Matrice de traçabilité exigence–preuve–contrat

| ID | Besoin / exigence | Criticité | Preuve de l’offre | Vérification en recette | Obligation contractuelle |
|---|---|---|---|---|---|
| F-01 | Fonction de recherche opérationnelle | Élevée | Démonstration et description | Cas d’essai documentés | Fonction maintenue pendant la durée du contrat |
| PERF-01 | Temps de réponse sous charge | Élevée | Mesures du test candidat | Essai avec scénario publié | Seuil et remédiation définis |
| SEC-01 | Accès à privilèges contrôlé | Critique | Architecture et preuves | Revue de configuration et journalisation | Notification, correction et audit définis |
| PRA-01 | Restauration dans l’objectif approuvé | Critique | Procédure et résultats d’exercice | Restauration représentative | Fréquence d’exercice et responsabilités définies |
| EXIT-01 | Restitution des données et documentation | Élevée | Plan de réversibilité | Test d’export si pertinent | Format, délai, assistance et coût définis |

Chaque exigence importante doit être reliée à une preuve avant attribution et à un moyen de contrôle après attribution. Cette continuité empêche qu’une promesse décisive disparaisse entre la notation et le contrat.

### 3.8 Exigences non fonctionnelles et niveaux de preuve

Les exigences fonctionnelles disent ce que l'utilisateur peut accomplir. Les exigences non fonctionnelles définissent dans quelles conditions le service doit fonctionner : performance, disponibilité, maintenabilité, sécurité, observabilité, accessibilité, évolutivité, portabilité et capacité de récupération. Elles sont souvent déterminantes pour les services critiques, mais fréquemment rédigées en termes trop génériques.

Pour chaque exigence non fonctionnelle, choisir un moyen de preuve proportionné :
- déclaration du candidat pour une information descriptive simple ;
- documentation d'architecture lorsque le mécanisme doit être compris ;
- certificat ou attestation lorsque la certification est pertinente pour le périmètre ;
- rapport de test lorsque la performance ou le contrôle doit être démontré ;
- démonstration encadrée lorsque l'interaction est centrale ;
- essai de recette ou exercice lorsque le résultat doit être établi dans un environnement représentatif ;
- engagement contractuel lorsque la capacité doit perdurer après attribution.

Ces preuves ne sont pas équivalentes. Un certificat atteste seulement le périmètre et la période de validité qu'il couvre. Une architecture décrit une conception, sans démontrer nécessairement son exécution. Un essai isolé ne prouve pas le fonctionnement de bout en bout. La matrice de conformité doit donc préciser la preuve attendue au stade de l'offre et la vérification qui aura lieu après attribution.

### Matrice de cohérence entre exigences

Une revue croisée recherche les contradictions entre les annexes. Par exemple, une exigence de support 24 h/24 peut être incompatible avec un délai contractuel de mobilisation de trois jours. Une clause de restitution des données peut être contradictoire avec une licence qui interdit l'export. Un objectif de disponibilité peut être impossible si les maintenances programmées sont longues ou si le fournisseur n'a aucun accès aux composants indispensables.

La revue peut examiner :
- la cohérence des unités et des volumes entre les documents ;
- les mêmes termes définis de façon différente ;
- les frontières de responsabilité entre fournisseur, acheteur et sous-traitants ;
- la compatibilité des délais de livraison, d'intégration, de test et de réception ;
- les hypothèses d'environnement et de disponibilité des équipes ;
- les liens entre la promesse, le critère de notation, la clause contractuelle et la preuve de recette ;
- les options commerciales non chiffrées ou susceptibles de modifier le périmètre ;
- les écarts entre la procédure formelle et les pratiques annoncées aux candidats.

~~~mermaid
flowchart LR
  A[Besoin métier] --> B[Exigence rédigée]
  B --> C[Preuve demandée à l'offre]
  C --> D[Critère de comparaison]
  D --> E[Clause contractuelle]
  E --> F[Test de recette]
  F --> G[Mesure durant le contrat]
  G --> H[Action si écart]
~~~

Si une exigence critique n'a ni preuve d'offre ni recette ni obligation contractuelle, elle est probablement mal conçue. Si un critère noté ne correspond à aucun besoin ou si une obligation de contrat n'a jamais été présentée aux candidats dans un cadre qui exige cette transparence, il faut résoudre l'incohérence avant publication.

## 4. Structurer le dossier de consultation

Un dossier doit donner la même information essentielle à tous les candidats autorisés. Les pièces typiques comprennent la lettre ou l’avis de consultation, le règlement de consultation, les instructions aux candidats, la description du besoin, les spécifications, le calendrier, les critères, les modalités de remise, les formulaires de prix, les conditions contractuelles, les annexes de sécurité, les exigences de transition, les clauses de confidentialité et les modèles de réponse. La structure varie selon le régime et le type d’achat.

### 4.1 Plan du dossier

1. **Contexte et objectifs :** raison du marché, résultat visé, utilisateurs et périmètre.
2. **Instructions :** calendrier, questions, format, validité des offres, modalités de dépôt et langue.
3. **Conditions de participation :** capacité, qualifications, références ou autres pièces permises.
4. **Spécifications :** besoins, quantités, résultats, contraintes et interfaces.
5. **Réponse technique :** informations à fournir, architecture, méthode, calendrier, équipe, preuves et hypothèses.
6. **Réponse financière :** prix détaillés, hypothèses, taxes, unités, options, coûts récurrents et non récurrents.
7. **Évaluation :** critères annoncés, méthode, pondération et étapes.
8. **Contrat :** obligations, niveaux de service, paiement, changements, propriété intellectuelle, risques, sortie et règlement des différends.
9. **Annexes :** données de référence, matrices de conformité, bordereaux, modèles et formulaires.

La liste ne remplace pas un modèle officiel obligatoire. Si l’organisation ou le bailleur impose des documents standards, utiliser la version valide et ne modifier que ce qui est autorisé.

### 4.2 Calendrier réaliste

Le calendrier doit permettre aux candidats de comprendre le dossier, de poser des questions, de préparer une réponse et de réunir les pièces attendues. Il doit aussi laisser du temps à l’acheteur pour répondre, analyser les offres et obtenir les autorisations. Un délai trop court peut limiter la concurrence et augmenter les offres assorties de réserves.

Le calendrier prévoit les validations internes, la publication, les questions, les réponses, les visites ou démonstrations, la date limite, l’ouverture, les évaluations, les vérifications, les éventuelles périodes de recours ou d’attente prescrites, la signature et le lancement. Toute modification du calendrier suit la procédure et est communiquée de manière égale lorsque le cadre l’exige.

### 4.3 Questions et addenda

Les questions des candidats peuvent révéler une ambiguïté importante. Enregistrer chaque demande, la date, la personne chargée de la réponse, la validation nécessaire et la publication. Si une réponse modifie l’interprétation ou la portée du dossier, communiquer l’information de manière cohérente à tous les candidats concernés, selon les règles applicables. Si le changement est majeur, un délai supplémentaire ou une modification formelle peut être nécessaire.

Éviter les réponses orales non consignées, les instructions différentes données à deux candidats ou les changements non publiés. Une clarification ne doit pas devenir une façon de changer discrètement les critères, de réécrire le besoin après avoir vu une offre ou de créer un avantage sélectif.

### 4.4 Gestion des versions et contrôle de publication

Le dossier doit être géré comme un ensemble contrôlé. Affecter un identifiant et une version aux pièces principales, conserver les versions approuvées, contrôler les liens entre annexes et limiter les accès aux brouillons. Au moment de la publication, vérifier que le dossier diffusé est exactement celui qui a reçu l'autorisation. Une annexe locale obsolète peut introduire des critères ou des prix différents du document principal.

Pour chaque modification, enregistrer l'auteur, la raison, la pièce touchée, les validations nécessaires, la date de publication et l'effet sur le calendrier. Distinguer une correction typographique qui n'affecte pas l'interprétation d'un changement qui modifie le besoin, la méthode de prix ou le résultat attendu. L'acheteur ne doit pas supposer qu'une modification est mineure uniquement parce qu'elle porte sur une phrase.

La gestion des versions doit s'appliquer aux fichiers tableurs, formules de score, modèles de prix, annexes et réponses aux questions. Une formule modifiée dans une copie locale peut changer le classement même si le rapport final semble cohérent. Protéger les formules sensibles, documenter les cellules d'entrée, tester le calcul sur un exemple et faire vérifier le résultat par une seconde personne.

## 5. Distinguer admissibilité, conformité et évaluation

Une source fréquente de contestation est le mélange entre les conditions de participation, les exigences obligatoires et les critères de notation.

- **Conditions de participation :** elles déterminent si l’opérateur peut participer selon le régime applicable.
- **Conformité obligatoire :** elle vérifie si les conditions essentielles de l’offre satisfont les exigences minimales annoncées.
- **Critères d’évaluation :** ils permettent de comparer les offres conformes selon la méthode publiée.
- **Vérifications avant attribution :** elles confirment les éléments que les règles permettent ou imposent de vérifier à cette étape.
- **Obligations contractuelles :** elles s’appliquent une fois le contrat conclu et doivent être cohérentes avec les promesses évaluées.

Une exigence éliminatoire ne doit pas être inventée après réception. Une caractéristique annoncée comme avantage noté ne devrait pas devenir une condition obligatoire implicite. La décision d’admettre, de demander une clarification permise ou d’écarter une offre doit être fondée sur le dossier et la procédure applicables.

### 5.1 Clarification, correction et modification d’offre

La clarification sert à comprendre un élément existant dans les limites prévues. Elle ne doit pas autoriser une refonte substantielle de l’offre, une amélioration concurrentielle interdite ou une réparation non disponible aux autres candidats. Les règles de correction des erreurs arithmétiques et de traitement des omissions sont propres au régime applicable et doivent figurer dans les documents ou procédures pertinents.

Le registre des clarifications indique la question, la date, la base procédurale, la réponse, l’effet sur l’évaluation et l’approbateur. Si la clarification change matériellement le sens d’une offre, les évaluateurs doivent consulter l’autorité prévue plutôt que décider au cas par cas.

## 6. Concevoir une grille d’évaluation objective

### 6.1 Critères liés au besoin

Les critères doivent distinguer ce qui est indispensable de ce qui fait réellement varier la valeur. Ils sont liés à l’objet de l’achat, annoncés selon le régime, compréhensibles et applicables de manière cohérente. Les critères possibles incluent le prix, le coût du cycle de vie, la qualité, la performance, la méthode de mise en œuvre, les délais, la maintenance, la continuité, la sécurité, les compétences et d’autres caractéristiques permises et liées au besoin.

Ne pas choisir un critère parce qu’il favorise un fournisseur connu. Ne pas compter deux fois le même avantage sous des critères différents. Si le prix inclut déjà la maintenance, il faut vérifier que la méthode ne récompense pas à nouveau la même composante sans raison.

### 6.2 Exemple de pondération

Pour un service critique de maintenance informatique, une grille pédagogique pourrait utiliser les poids suivants après validation du besoin :

| Critère | Poids illustratif | Question de décision |
|---|---:|---|
| Coût total évalué sur l’horizon | 30 % | Quel est le coût comparable, avec les hypothèses publiées ? |
| Qualité et adéquation de la solution | 20 % | La solution répond-elle aux besoins et contraintes ? |
| Continuité, reprise et SLA | 20 % | Les capacités de secours sont-elles vérifiables et compatibles avec les objectifs ? |
| Méthode, équipe et transition | 15 % | La mise en œuvre, la recette et la réversibilité sont-elles crédibles ? |
| Sécurité, support et gouvernance | 10 % | Les contrôles et responsabilités sont-ils cohérents avec le risque ? |
| Durabilité ou autres objectifs autorisés | 5 % | L’approche apporte-t-elle une valeur mesurable et pertinente ? |

Ces poids sont illustratifs, pas une grille à recopier par défaut. La pondération doit refléter les facteurs qui différencient les offres et être approuvée avant l’évaluation. La méthode doit préciser si certaines conditions sont éliminatoires avant la notation.

### 6.3 Définir des ancres de notation

Une échelle de 0 à 5 doit être définie avant d’évaluer. Par exemple :
- **0 — absent ou inacceptable :** aucune preuve suffisante ou réponse incompatible ;
- **1 — très faible :** lacunes majeures, hypothèses non justifiées, risque élevé ;
- **2 — partiel :** réponse incomplète ou nécessitant des mesures correctives importantes ;
- **3 — conforme :** réponse qui satisfait les exigences et présente des preuves adéquates ;
- **4 — supérieur :** amélioration utile, étayée et pertinente sans risque disproportionné ;
- **5 — excellent :** bénéfice majeur, vérifiable et clairement supérieur au besoin, avec hypothèses transparentes.

Une note élevée ne doit pas être accordée simplement parce que l’offre est plus longue, plus riche en graphiques ou présentée par une équipe convaincante. Les évaluateurs notent la preuve par rapport à l’ancre. Si deux offres sont proches, le rapport doit justifier la différence par une caractéristique concrète.

### 6.4 Calculer un score pondéré

Pour une méthode où une note est attribuée à chaque critère sur 5, un score pondéré peut se calculer comme suit, si cette méthode est autorisée et publiée :

Score total = somme, pour chaque critère, de (note obtenue / note maximale) × poids du critère.

Exemple fictif :
- coût : 4/5 avec poids 30 ;
- adéquation technique : 4/5 avec poids 20 ;
- continuité : 3/5 avec poids 20 ;
- transition : 4/5 avec poids 15 ;
- sécurité/support : 4/5 avec poids 10 ;
- durabilité : 3/5 avec poids 5.

Calcul : 24 + 16 + 12 + 12 + 8 + 3 = 75 points sur 100. Le score ne signifie rien isolément : le rapport doit aussi examiner la conformité, les exigences critiques, les risques et les règles de classement prévues. Si une exigence éliminatoire n’est pas satisfaite, un score élevé sur d’autres critères ne la neutralise pas.

### 6.5 Calibrer les évaluateurs

Avant la notation individuelle, les évaluateurs doivent comprendre les critères, la méthode, les ancres, les règles de clarification et les obligations de confidentialité. Une séance de calibration sur un exemple neutre révèle les interprétations divergentes. Elle ne doit pas devenir une réunion visant à harmoniser les scores autour d’un candidat préféré.

Lorsque les règles le permettent, chaque évaluateur documente d’abord son analyse individuelle. La réunion de consensus traite les divergences à partir des preuves. Toute modification de note doit être motivée. Les personnes ayant un conflit d’intérêts le déclarent et suivent la mesure de récusation ou de gestion prévue par la politique.

~~~mermaid
flowchart TD
  A[Critères validés avant réception] --> B[Réception et contrôle formel]
  B --> C[Conformité aux exigences obligatoires]
  C --> D{Offre conforme selon les règles ?}
  D -->|Non| E[Motiver la décision et appliquer la procédure]
  D -->|Oui| F[Évaluation individuelle par critère]
  F --> G[Comparer les preuves et clarifier si permis]
  G --> H[Calibrer les écarts de notation]
  H --> I[Calcul et vérification indépendante]
  I --> J[Rapport d'évaluation et approbation]
~~~

### 6.6 Preuves, soutenances et démonstrations

Une démonstration peut révéler le fonctionnement réel, mais il faut annoncer son rôle, son scénario, sa durée, les participants et la façon dont les résultats seront utilisés. Si elle est notée, la grille doit être publiée ou définie selon les exigences applicables. Les candidats doivent être évalués selon des conditions comparables.

Les affirmations de l’offre doivent être associées à une preuve adaptée : référence vérifiable, test, certification pertinente, documentation, engagement contractuel, démonstration ou rapport. Une certification générique ne prouve pas nécessairement l’exigence précise à évaluer. De la même manière, une présentation commerciale ne remplace pas un test d’acceptation.

### 6.7 Contrôler la cohérence et les biais de notation

Une grille pondérée peut produire une fausse impression de précision si les critères sont redondants ou les notes mal calibrées. Par exemple, la « qualité de la méthode », la « maturité de l'organisation » et la « confiance dans le fournisseur » peuvent mesurer presque la même chose. Les cumuler donne un poids excessif à un seul facteur. Il faut vérifier que chaque critère mesure une dimension distincte et que les preuves sont notées une seule fois, sauf justification.

Les évaluateurs doivent distinguer la qualité de la rédaction de la qualité de la réponse. Une offre bien mise en page n'est pas nécessairement meilleure. De même, une réponse courte peut être complète si elle apporte la preuve requise ; une réponse longue peut cacher l'absence de détail utile. Les notes doivent citer les paragraphes, documents, mesures ou résultats qui les justifient.

Le contrôle de notation vérifie :
1. que chaque critère a une note et une justification ;
2. que les ancres ont été appliquées de façon cohérente ;
3. que les exigences obligatoires ont été traitées dans la phase appropriée ;
4. que les pondérations et formules correspondent à la version approuvée ;
5. que les clarifications ont été utilisées dans le cadre permis ;
6. que les totaux ont été recalculés indépendamment ;
7. que les différences de classement sont explicables par les critères annoncés ;
8. que les conflits d'intérêts ou les accès non autorisés ont été traités.

~~~mermaid
flowchart TD
  A[Grilles individuelles] --> B[Contrôle des preuves citées]
  B --> C[Revue des écarts de notes]
  C --> D{Écart explicable par le critère ?}
  D -->|Non| E[Revue documentée et clarification interne]
  D -->|Oui| F[Calcul indépendant]
  E --> F
  F --> G[Validation du rapport]
  G --> H[Archivage des versions et justificatifs]
~~~

Une analyse de sensibilité peut être utile lorsque des différences minimes de notes ou des hypothèses financières font basculer le classement. Elle doit rester un contrôle de robustesse, pas une méthode cachée de reclassement. Si la procédure impose une règle précise, c'est cette règle qui gouverne la décision.

## 7. Évaluer le prix et le coût total sur le cycle de vie

### 7.1 Construire un modèle de coût comparable

Le prix initial n’est qu’un élément du coût. Selon l’achat, le coût total de possession peut inclure acquisition, licences, intégration, migration, formation, fonctionnement, énergie, hébergement, maintenance, support, pièces, déplacements, mises à jour, audits, conformité, renouvellements, montée en capacité et sortie. Il faut définir l’horizon, les volumes, les hypothèses et les règles de comparaison avant de recevoir les offres.

Les coûts doivent être répartis par unité, périodicité, hypothèse de volume et caractère obligatoire ou optionnel. Une offre dont le prix dépend d’une consommation non documentée n’est pas directement comparable à une offre forfaitaire. Un prix anormalement bas doit être traité selon les règles de la procédure, pas simplement rejeté sur une impression.

### 7.2 Exemple de tableau de TCO

| Poste | Année 1 | Années suivantes | Hypothèse à vérifier |
|---|---:|---:|---|
| Mise en service | Coût initial | Généralement nul, sauf évolution | Livrables et frais de projet |
| Licences / abonnement | Tarif et prorata | Renouvellement et indexation | Nombre d’utilisateurs ou consommation |
| Intégration et migration | Étendue initiale | Changements additionnels | Données, interfaces et environnement |
| Support et maintenance | Contrat initial | Prix et couverture | Horaires, pièces et escalade |
| Exploitation interne | Charge de l’équipe | Charge récurrente | Compétences et disponibilité |
| Infrastructure / énergie | Capacité utilisée | Hausse ou évolution | Consommation et dimensionnement |
| Formation | Formation initiale | Intégration des nouveaux arrivants | Renouvellement des compétences |
| Sécurité et conformité | Audit initial | Tests et contrôles récurrents | Périmètre et fréquence |
| Sortie et transfert | Préparation prévue | Selon la stratégie de sortie | Export, assistance et suppression |

Pour une comparaison financière complexe, les flux futurs peuvent être actualisés si la méthode retenue l’exige. Le taux, l’horizon, les volumes, l’inflation et la devise doivent être cohérents. Il ne faut pas ajouter des hypothèses financières opportunistes après réception uniquement pour modifier le classement.

### 7.3 Sensibilité et scénarios

Tester plusieurs scénarios : volume faible, attendu et élevé ; renouvellement tarifaire ; retard d’intégration ; évolution du taux de change si pertinent ; coût d’un incident ; hausse du nombre d’utilisateurs ; durée de sortie. La sensibilité révèle quels paramètres pilotent réellement la valeur et où les hypothèses sont fragiles.

Ne pas intégrer un coût hypothétique au score sans l’avoir défini et autorisé dans la méthode. Si l’incertitude est importante, la traiter en risque, en scénario ou en clarification permise, pas en ajoutant un facteur non publié au milieu de l’évaluation.

### 7.4 Structures tarifaires et répartition du risque

Le modèle de prix influence le comportement du fournisseur et la distribution des risques. Un prix forfaitaire peut offrir de la prévisibilité si le périmètre et les conditions sont bien définis. Il peut provoquer des réserves, des hypothèses restrictives ou des demandes de changement si le besoin est incertain. Une facturation à l'unité peut mieux refléter le volume, mais rend le coût total sensible à la consommation. Une tarification au temps passé peut être appropriée dans certains services spécialisés, à condition que les profils, plafonds, taux, autorisations et livrables soient contrôlés.

| Modèle de prix | Atout possible | Risque à gérer |
|---|---|---|
| Forfait ferme | Prévisibilité dans un périmètre stable | Réserves ou litiges lorsque le périmètre est ambigu |
| Prix unitaires | Comparaison par unité et adaptation au volume | Variation du coût final si les volumes changent |
| Régie / temps passé | Adaptation à un besoin difficile à spécifier à l'avance | Contrôle de charge, productivité, autorisations et plafond |
| Abonnement | Simplicité de facturation récurrente | Indexation, limites d'usage, renouvellement et coûts de sortie |
| Paiement par jalon | Paiement lié à des résultats vérifiables | Jalon trop général, réception ambiguë ou dépendance externe |
| Modèle incitatif | Peut aligner certains résultats | Indicateurs manipulables ou effets indésirables s'ils sont mal conçus |

Choisir un modèle n'élimine pas l'incertitude ; il la distribue. Le dossier doit préciser les volumes de référence, le traitement des variations, les unités facturables, les frais inclus, les plafonds, les options, l'indexation, la monnaie, les taxes et les conditions de validation. Une comparaison équitable exige de calculer les offres sur les mêmes hypothèses.

### 7.5 Indexation, devises et hypothèses financières

Les contrats pluriannuels peuvent prévoir des révisions de prix, mais la formule doit être définie, autorisée et transparente. Spécifier l'indice, la date de référence, la périodicité, la part fixe, le plafond ou le plancher éventuel et le traitement d'un indice qui cesse d'être publié. Les devises peuvent exposer l'acheteur au risque de change ; il faut préciser la devise de l'offre, de la facture et du paiement ainsi que la manière dont les fluctuations sont traitées.

Une analyse financière doit distinguer un coût contractuel ferme d'une hypothèse de consommation, d'un coût estimé ou d'une option. Les économies annoncées doivent indiquer la base de comparaison et les coûts de mise en œuvre. Une économie de licence qui nécessite davantage d'exploitation interne n'est pas une économie nette sans valoriser le travail supplémentaire.

## 8. Intégrité, impartialité et traçabilité

### 8.1 Conflits d’intérêts

Un conflit d’intérêts peut être réel, potentiel ou perçu. Les membres de l’équipe doivent déclarer leurs relations pertinentes, investissements, liens familiaux, engagements antérieurs ou intérêts susceptibles de compromettre leur impartialité. La procédure indique comment les déclarations sont examinées, si la personne peut continuer à participer et quelles mesures sont requises.

Un registre des conflits, les décisions de récusation, l’accès contrôlé aux offres et la séparation des responsabilités sont des mesures courantes de gouvernance. Les dispositifs exacts dépendent des règles de l’organisation et du régime d’achat.

### 8.2 Prévenir les biais et la collusion

Les signaux d’alerte peuvent inclure des offres très similaires, des écarts de prix atypiques, des erreurs identiques, une rotation répétée des gagnants ou des candidats qui se retirent sans explication. Aucun signal ne prouve seul une collusion ; il justifie de préserver les informations, de suivre la procédure d’alerte et de consulter les personnes habilitées plutôt que de confronter les fournisseurs de manière improvisée.

Appliquer le même calendrier, les mêmes informations et les mêmes critères. Contrôler l’accès aux offres avant la date limite. Enregistrer les communications. Séparer les données commerciales confidentielles des documents partagés. Les équipes doivent éviter les discussions informelles sur les prix ou les chances d’un candidat avant la fin des étapes autorisées.

### 8.3 Dossier d’audit

Le dossier d’audit contient les versions des documents, les validations, les invitations ou publications, les questions et réponses, les preuves de réception, les déclarations d’intérêts, les grilles, les notes, les motifs des écarts, les clarifications, les calculs, le rapport, les contrôles avant attribution et l’approbation finale. Le but n’est pas d’accumuler des fichiers, mais de démontrer la logique de décision et le respect des règles.

La piste d’audit doit permettre de répondre à quatre questions : qu’a-t-on décidé, sur quelle base, par qui, et quelle preuve confirme l’exécution ? Si le rapport contient un score, les feuilles sources et la formule doivent permettre de refaire le calcul.

### 8.4 Contrôles d'accès, confidentialité et conservation des preuves

Les offres peuvent contenir des informations commerciales sensibles, des données personnelles, des secrets techniques et des informations de sécurité. Limiter les accès aux personnes autorisées, utiliser des canaux de réception conformes à la procédure, consigner les accès lorsque c'est nécessaire et définir une règle de conservation. La durée et les modalités de conservation dépendent du cadre juridique, du financement, des exigences d'audit et des règles internes.

La confidentialité ne doit pas servir à supprimer la piste d'audit. Il faut distinguer les documents qui doivent être rendus accessibles, ceux qui peuvent être communiqués sous réserve de protection et ceux qui doivent rester restreints. Les demandes d'accès, d'information ou les recours doivent être traités conformément au régime applicable. Toute divulgation doit être autorisée, tracée et limitée à ce qui est permis.

Une revue d'intégrité peut inclure les horodatages de réception, les comptes ayant accédé aux dossiers, la version des grilles utilisées, les conflits d'intérêts, le journal des clarifications et les preuves de validation. Un signal d'anomalie doit être transmis à l'autorité appropriée ; les membres de l'équipe ne doivent pas improviser une enquête ou détruire les éléments par inadvertance.

~~~mermaid
flowchart TD
  A[Offres reçues] --> B[Enregistrer date et intégrité du dépôt]
  B --> C[Limiter l'accès aux rôles autorisés]
  C --> D[Déclarations d'intérêts et récusations]
  D --> E[Grilles et clarifications tracées]
  E --> F[Contrôle indépendant du calcul]
  F --> G[Décision autorisée]
  G --> H[Archivage et conservation selon les règles]
~~~

## 9. Clarifications, négociation et attribution

### 9.1 Encadrer les échanges avec les candidats

Après le dépôt, les clarifications autorisées servent à comprendre une réponse ou à appliquer les règles de traitement des erreurs. Elles ne doivent pas devenir une réouverture libre de la concurrence. Le type de procédure détermine ce qui peut être demandé, modifié ou négocié. Consulter le juridique ou le responsable de la procédure en cas de doute.

Toutes les clarifications sont datées et conservées. Le rapport d’évaluation indique leur pertinence et la manière dont la réponse a été utilisée. Une clarification qui apporte une information au-delà du cadre permis ne doit pas être intégrée silencieusement au score.

### 9.2 Négocier lorsque le cadre le permet

La négociation doit avoir un objectif, une autorité, un périmètre et une stratégie approuvés. Définir les sujets négociables, les limites, les éléments non négociables, les concessions possibles, les seuils d’autorisation et la trace à conserver. Les règles d’égalité de traitement, de confidentialité et de procédure doivent rester respectées.

Un négociateur compétent ne négocie pas uniquement le prix facial. Il étudie les niveaux de service, la couverture horaire, les délais, les pièces, les indexations, les paiements, la formation, les livrables, les risques, les garanties, les modalités de sortie et la gestion des changements. Toute concession doit être évaluée en coût, risque et effet sur la valeur.

### 9.3 Vérifier avant l’attribution

Avant de signer, confirmer les approbations requises, la disponibilité du budget, l’absence de conflit non traité, la validité de l’offre, les documents prévus, les vérifications autorisées, le traitement des éventuelles contestations et la cohérence entre l’offre retenue et le contrat final. Les étapes de publication, notification, attente ou recours varient selon la juridiction et la procédure.

Le contrat ne doit pas contredire la proposition évaluée. Si une promesse a influencé le score, elle doit être traduite en obligation, jalon, indicateur, livrable ou critère de réception. Si elle n’est pas intégrée, l’organisation risque d’acheter un argument de vente qu’elle ne pourra pas faire respecter.

### 9.4 Préparer un rapport d'évaluation défendable

Un rapport d'évaluation synthétise la procédure sans remplacer les pièces sources. Il indique la composition de l'équipe, les déclarations d'intérêts, les offres reçues, les étapes réalisées, les contrôles de conformité, les clarifications permises, l'application des critères, les notes motivées, les calculs, les risques déterminants et la recommandation d'attribution. Il est rédigé pour permettre à un réviseur indépendant de reconstruire la logique de décision.

Un bon rapport ne se contente pas d'écrire « offre excellente » ou « fournisseur peu convaincant ». Il décrit l'écart ou la preuve : délai de reprise annoncé, test fourni, réserve contractuelle, absence de format d'export ou hypothèse de prix. Les observations doivent être pertinentes pour les critères ; les opinions non étayées et les formulations désobligeantes sont inutiles.

La recommandation indique les conditions à remplir avant signature et les risques résiduels. Si l'offre retenue comporte des réserves, elles doivent être traitées selon la procédure avant d'engager l'organisation. Une recommandation ne doit pas anticiper des concessions ou des changements majeurs que la procédure ne permet pas.

~~~mermaid
flowchart LR
  A[Contrôles de conformité] --> B[Résultats par critère]
  B --> C[Calcul vérifié]
  C --> D[Risques et réserves]
  D --> E[Recommandation motivée]
  E --> F[Approbations prévues]
  F --> G[Notification et formalités applicables]
  G --> H[Contrat final cohérent avec l'offre retenue]
~~~

## 10. Rédiger un contrat pilotable

### 10.1 De l’offre à l’obligation

Les exigences essentielles doivent être raccordées à des clauses contractuelles. Le contrat précise les livrables, les dates, les dépendances de l’acheteur, les critères d’acceptation, les responsabilités, les modalités de paiement, les garanties, les changements, les niveaux de service, la gestion des risques, les droits sur les livrables et les règles de sortie.

Éviter les termes ambigus comme « rapidement », « dans la mesure du possible » ou « support premium » sans définition. Il faut préciser le déclencheur, la période, le délai, le périmètre et la preuve. Les clauses doivent aussi déterminer qui arbitre lorsqu’une dépendance de l’acheteur empêche le fournisseur de respecter un jalon.

### 10.2 SLA : disponibilité, prise en charge et rétablissement

Un SLA peut inclure la disponibilité, mais il faut définir ce qui est mesuré, où, à quelle fréquence, sur quelle période et avec quelles exclusions. Distinguer l’indisponibilité complète, la dégradation, la perte de fonctions, la performance lente et l’échec de transaction. Les incidents peuvent avoir des priorités et des objectifs différents.

| Élément | Définition à convenir |
|---|---|
| Périmètre mesuré | Composants, fonctions, utilisateurs et points de mesure |
| Disponibilité | Formule, période, fenêtres et exclusions valides |
| Prise en charge | Délai entre notification et début de traitement |
| Rétablissement | Retour de la capacité attendue, éventuellement en mode dégradé |
| Résolution | Correction permanente ou explication et contournement formellement acceptés |
| Escalade | Seuils, contacts et autorités mobilisées |
| Crédit ou pénalité | Méthode, plafond, limites juridiques et relation avec les autres recours |
| Rapport | Données, fréquence, format et droit de vérification |
| Contestation de mesure | Délai, preuves et méthode de résolution |

Une pénalité n’est pas un mécanisme magique de résilience. Elle doit être juridiquement valide, proportionnée au cadre applicable et associée à une méthode de mesure fiable. Il faut aussi traiter les actions correctives, le risque de répétition et les conditions de sortie pour défaillance persistante.

### 10.3 Gouvernance, changements et paiement

Définir un comité de suivi adapté au risque, la fréquence des rapports, les participants, les décisions réservées, la gestion des incidents, les escalades, le plan qualité et la validation des factures. Les paiements doivent correspondre à des jalons, livrables ou unités vérifiables, avec un processus de contestation des factures.

Un changement de périmètre doit décrire le besoin, la raison, les options, le prix, le délai, les risques, les impacts sur les niveaux de service et l’approbation requise. Les changements récurrents peuvent indiquer que les exigences initiales étaient insuffisantes ou que le contrat est mal piloté. Il faut surveiller l’effet cumulatif des avenants et modifications selon les règles applicables.

### 10.4 Réversibilité et sortie fournisseur

La sortie doit être conçue avant la signature. Elle peut nécessiter l’export des données dans un format exploitable, la remise de documentation, le transfert de compétences, la restitution d’actifs, la migration des configurations, la révocation des accès, la suppression contrôlée des copies et l’assistance au successeur.

Définir les délais, formats, responsabilités, coûts, licences nécessaires, contrôles d’intégrité, obligations de confidentialité, coopération avec le fournisseur suivant et critères de fin. Une clause qui dit simplement « le fournisseur aidera à la sortie » est trop vague. Le plan peut être testé sur un échantillon afin de découvrir les formats propriétaires ou les tâches manuelles difficiles.

~~~mermaid
flowchart LR
  A[Besoin et stratégie] --> B[Exigences vérifiables]
  B --> C[Critères annoncés]
  C --> D[Évaluation et rapport]
  D --> E[Promesses de l'offre retenue]
  E --> F[Clauses et indicateurs]
  F --> G[Recette et suivi]
  G --> H[Sortie et réversibilité]
  H --> I[Retour d'expérience]
  I --> A
~~~

Cette traçabilité est un contrôle central. Une exigence importante qui disparaît au moment du contrat crée un écart entre la décision d’achat et la valeur réellement obtenue.

### 10.5 Gestion des incidents contractuels, des remèdes et du risque de résiliation

Le contrat doit expliquer comment les parties réagissent lorsqu'un engagement n'est pas tenu : notification, qualification, délai de remédiation, plan correctif, escalade, mesure des impacts, recours contractuels et conditions de résiliation éventuelle. Les remèdes précis doivent être adaptés au droit et aux négociations autorisées. Les pénalités ou crédits de service doivent être mesurables et compatibles avec le contrat ; ils ne doivent pas remplacer la correction du défaut quand la continuité dépend d'une action technique.

Une défaillance isolée et un défaut récurrent ne se gèrent pas toujours de la même manière. Une non-conformité ponctuelle peut faire l'objet d'une correction et d'une vérification. Des incidents similaires qui se répètent peuvent révéler une cause racine, une capacité insuffisante, une compétence absente ou une obligation mal rédigée. Le plan correctif indique la cause étayée, les actions, les délais, les mesures temporaires, la preuve de résolution et le test d'efficacité.

La résiliation est un scénario de risque à préparer, pas une menace à improviser au premier désaccord. Le plan doit identifier l'autorité, les motifs contractuels, les obligations de transition, le paiement des travaux acceptés, la protection des données, les accès, les actifs à récupérer et la continuité pendant la substitution. Les conséquences peuvent inclure une période de service transitoire et le soutien au successeur ; les règles exactes doivent être validées juridiquement.

## 11. Réception, transition et entrée en exploitation

### 11.1 Définir la recette avant la mise en œuvre

Les critères d’acceptation sont définis avant le lancement des travaux. Ils indiquent les scénarios, les données, l’environnement, les résultats attendus, les preuves, les responsables, les seuils de réussite et le traitement des défauts. Les tests couvrent le fonctionnel, l’intégration, la performance, la sécurité, la reprise, l’exploitation et le transfert de connaissances, selon le besoin.

Distinguer la réception provisoire, la réception finale, la mise en service et la clôture du contrat si le dispositif les prévoit. Une mise en production ne prouve pas automatiquement que tous les livrables sont acceptés. Le paiement doit suivre les clauses et les preuves convenues.

### 11.2 Transition vers l’exploitation

Le passage en exploitation doit inclure l’inventaire, les accès, les procédures, la supervision, les contacts, les niveaux de service, les compétences, les plans de continuité, les sauvegardes et la responsabilité des changements. Il faut vérifier la capacité des équipes à assurer les opérations sans dépendre de la présence constante du fournisseur qui a effectué la mise en œuvre.

Une transition est fragile lorsque les connaissances restent dans des réunions ou dans la tête d’une seule personne. Exiger une documentation exploitable, des sessions pratiques, des tests par les opérateurs internes et une validation des scénarios de panne courants. Le transfert est achevé lorsque l’équipe destinataire démontre les tâches prévues, pas uniquement lorsqu’elle signe la feuille de présence.

### 11.3 Piloter la performance au fil du contrat

Un tableau de bord utile associe chaque indicateur à une source, une formule, une périodicité, une cible, un seuil d’escalade et un propriétaire. Suivre au minimum les résultats, les délais, la qualité, les incidents, les changements, les risques, les coûts, les actions ouvertes et la satisfaction métier lorsqu’elle est mesurée selon une méthode fiable.

Une revue fournisseur ne doit pas être une simple présentation marketing. Comparer les données aux engagements, examiner les incidents récurrents, demander les analyses de cause, vérifier l’avancement des actions et arbitrer les risques. Les tendances sont souvent plus utiles que la valeur d’un mois isolé. Une mesure en hausse ou en baisse doit être interprétée selon le volume, le périmètre et les changements du service.

### 11.4 Plan de transition fournisseur par jalons

Une transition de fournisseur est un mini-projet à risques. Le contrat doit attribuer clairement les tâches au fournisseur sortant, au fournisseur entrant et à l'acheteur. Prévoir les accès temporaires, les inventaires, la configuration, la documentation, les données, les licences, les contacts, la formation, les tests et la gestion des incidents pendant le chevauchement.

~~~mermaid
flowchart TD
  A[Planifier la transition] --> B[Inventaire et responsabilités]
  B --> C[Accès et documentation sécurisés]
  C --> D[Transfert de connaissances]
  D --> E[Migration / configuration]
  E --> F[Test de bout en bout]
  F --> G{Critères de reprise atteints ?}
  G -->|Non| H[Corriger ou prolonger le chevauchement approuvé]
  H --> F
  G -->|Oui| I[Acceptation par l'acheteur]
  I --> J[Révoquer les accès de sortie et vérifier les données]
~~~

La transition doit être planifiée assez tôt pour que les lacunes puissent être traitées avant l'échéance du contrat. Une dépendance découverte au moment de la sortie donne peu de marge pour négocier, migrer ou constituer une autre source. Le chevauchement peut avoir un coût, mais ce coût doit être comparé au risque d'une interruption ou d'un transfert incomplet.

Un plan de transition doit préciser les critères de démarrage, les livrables par jalon, les ressources des deux fournisseurs, les droits d'accès, les environnements de test, les incidents possibles, les critères d'acceptation et les conditions de clôture. Une réunion de transfert ne suffit pas : les équipes destinataires doivent démontrer qu'elles savent exécuter les tâches prévues et retrouver les informations essentielles.

## 12. Risques d’achat et stratégies de réponse

| Risque | Symptôme ou signal | Réponse de conception ou de pilotage |
|---|---|---|
| Besoin incomplet | Nombreux changements, réponses très différentes | Analyse de besoin, questions de marché et validation croisée |
| Faible concurrence | Peu d’offres comparables | Analyse du marché, allotissement ou stratégie alternative autorisée |
| Dépendance propriétaire | Formats fermés, coûts de sortie élevés | Portabilité, droits, documentation et test de réversibilité |
| Prix initial artificiellement bas | Options essentielles facturées séparément | Bordereau complet, hypothèses de TCO et analyse selon les règles |
| Promesse non prouvée | Présentation convaincante sans mesure | Exigences de preuve, démonstration cadrée et recette |
| Dépendance fournisseur critique | Aucun substitut ou délai de pièce long | Plan de continuité, stock pertinent, fournisseur de rechange et escalade |
| Risque cyber | Accès privilégiés excessifs, notification floue | Contrôles de sécurité, journalisation, coopération et reprise |
| Risque juridique | Clauses contradictoires ou procédure mal qualifiée | Revue juridique et contrôle du régime applicable |
| Biais d’évaluation | Critère non annoncé, notes non motivées | Ancres, calibration, déclarations d’intérêts et audit |
| Dépendances internes | Retards dus aux validations ou accès acheteur | Matrice de responsabilités, prérequis et dates réalistes |
| Changement incontrôlé | Avenants répétés ou périmètre dérivant | Processus de changement, seuils d’autorisation et suivi cumulatif |
| Sortie impraticable | Export propriétaire ou compétences absentes | Plan de sortie chiffré, test d’export et transfert de connaissances |

Le registre des risques précise le propriétaire, la probabilité, l’impact, les signaux d’alerte, les mesures préventives, les mesures de contingence et le risque résiduel. Une matrice rouge-orange-verte peut faciliter la communication, mais ne remplace pas le raisonnement ni l’escalade des risques critiques.

### 12.1 Évaluer et quantifier le risque avant la consultation

Le registre de risques ne doit pas seulement contenir des couleurs. Pour chaque risque, décrire l'événement, ses causes possibles, les conséquences, les contrôles existants, la probabilité ou la fréquence estimée, la gravité, les signaux d'alerte, les mesures de réduction, le propriétaire et le risque résiduel. La méthode de cotation doit être définie par l'organisation et rester suffisamment précise pour comparer les risques.

Exemple : la perte de documentation de configuration peut rendre la transition longue, mais la gravité dépend des services concernés, de la possibilité de reconstruire et des personnes encore disponibles. Un contrôle préventif pourrait imposer la tenue d'un dépôt documentaire appartenant à l'acheteur ; un contrôle de détection pourrait vérifier régulièrement l'exhaustivité ; une mesure de contingence pourrait financer un transfert accéléré. La combinaison de ces mesures est plus robuste qu'une clause générale qui impose seulement au fournisseur de « collaborer ».

Ne pas multiplier les risques à faible valeur informative. Regrouper les risques qui ont une cause commune tout en conservant les conséquences spécifiques. Un seul risque fournisseur peut affecter la maintenance, la cybersécurité et la continuité ; il doit être traité en gouvernance de manière cohérente plutôt que compté plusieurs fois sans analyse.

~~~mermaid
flowchart TD
  A[Identifier l'événement de risque] --> B[Causes et conséquences]
  B --> C[Contrôles déjà en place]
  C --> D[Estimer probabilité et impact]
  D --> E[Choisir prévention, détection et contingence]
  E --> F[Nommer propriétaire et échéance]
  F --> G[Évaluer risque résiduel]
  G --> H{Dans la tolérance autorisée ?}
  H -->|Non| I[Réduire ou faire arbitrer]
  H -->|Oui| J[Surveiller les signaux d'alerte]
~~~

## 13. Atelier pratique — lancer un appel d’offres de maintenance et de continuité

### Situation

Une organisation exploite une application de commandes, une base de données, un service d’identité et des intégrations vers un entrepôt. Le contrat de maintenance arrive à échéance dans six mois. Les incidents majeurs sont traités de façon variable, la documentation de sortie est incomplète et le dernier test de restauration a pris plus longtemps que l’objectif métier. Le fournisseur actuel est compétent sur la plateforme, mais certaines connaissances et certaines configurations sont difficiles à transférer.

Le comité veut lancer une consultation. Il attend un support de qualité, une restauration mesurable, une réduction des incidents récurrents, une meilleure documentation et la possibilité de changer de prestataire sans perdre le contrôle. Le budget est plafonné, mais les coûts de migration et de transition n’ont pas encore été chiffrés.

### Phase A — Cadrer et analyser le marché

1. Décrire les résultats métier attendus, plutôt que d’écrire uniquement « renouveler la maintenance ».
2. Définir ce qui est inclus : support, maintenance corrective, mises à jour, supervision, tests de reprise, documentation, transfert de compétence et assistance de sortie.
3. Identifier les éléments exclus et les responsabilités restant chez l’acheteur.
4. Examiner l’option de prolongation, de remise en concurrence, d’internalisation partielle et d’approche hybride selon ce qui est permis.
5. Analyser les fournisseurs capables, les dépendances aux éditeurs et les délais de transition.
6. Réunir les achats, le métier, la technique, la sécurité, les finances et le juridique pour valider la stratégie.

**Livrable :** une note de stratégie d’achat avec besoin, options, marché, calendrier, risques, budget, procédure envisagée et validations.

### Phase B — Rédiger les exigences

Définir les catégories de criticité des incidents, la prise en charge, le délai de contournement, le rétablissement, les périodes de service, le reporting, l’escalade, les tests de restauration et les obligations de sortie. Décrire la méthode de mesure et les exclusions. Préciser les données de volume et la responsabilité de l’acheteur pour les accès, environnements et validations.

Pour la continuité, demander une procédure de récupération, les dépendances, les résultats d’exercices pertinents, les hypothèses, la disponibilité des personnes clés et les moyens d’accès d’urgence. L’exigence doit être proportionnée au risque et vérifiable durant la sélection ou le contrat.

**Livrable :** une matrice d’exigences avec identifiant, criticité, preuve, méthode de recette et obligation contractuelle.

### Phase C — Élaborer la grille

Avant réception, décider les conditions éliminatoires selon le cadre, les critères notés, les poids, les ancres de notation, les règles de clarification et les méthodes de contrôle financier. Les critères doivent distinguer l’essentiel de la valeur supplémentaire.

Les évaluateurs font une calibration sur un exemple neutre. Ils préparent les questions de démonstration et la fiche de preuve attendue. Le calcul du score est vérifié par une seconde personne.

**Livrable :** une grille publiée ou approuvée selon la procédure, ainsi qu’un guide interne de notation.

### Phase D — Comparer les coûts et risques

Calculer le TCO sur une période de comparaison approuvée. Inclure la transition, la maintenance, les options, les déplacements, les mises à jour, les tests, la formation, la migration et la sortie. Décrire la méthode de traitement des hypothèses tarifaires et des coûts non inclus. Comparer aussi le risque de dépendance, la capacité de support et les scénarios de reprise.

**Livrable :** une comparaison des offres et une analyse de sensibilité, sans ajout de critères non annoncés.

### Phase E — Transformer le choix en contrat

Pour chaque promesse qui influence le classement, définir une obligation ou un livrable contractuel. Rédiger les niveaux de service, le plan de transition, les critères de recette, les rapports, la gestion des changements et les clauses de réversibilité. Déterminer les autorisations, les modalités de paiement et le traitement des défauts.

**Livrable :** un projet de contrat cohérent avec le dossier et un plan de pilotage après attribution.

### Critères de réussite de l’atelier

Le dossier est satisfaisant si un fournisseur peut le chiffrer sans devoir deviner les hypothèses majeures, si les offres seront comparées selon une méthode explicite, si les critères sont liés au besoin, si les décisions peuvent être auditées, si les exigences de continuité sont vérifiables et si la sortie du contrat est réaliste. Il doit éviter à la fois l’excès de prescription technique et les formulations qui laissent tout à l’interprétation.

## 14. Études de cas et corrigés

### Cas 1 — Une exigence favorise un fournisseur connu

L’équipe rédige une exigence demandant un produit précis parce que l’environnement actuel l’utilise. Elle ne documente ni une contrainte de compatibilité ni une analyse des alternatives.

**Analyse :** l’exigence peut restreindre inutilement la concurrence et ne décrit pas le résultat nécessaire. L’équipe doit examiner les interfaces, les coûts de transition, les exigences de sécurité et la compatibilité réelle. Si une contrainte précise est indispensable, elle doit être documentée et formulée conformément au régime d’achat ; sinon, définir le résultat et les équivalences acceptables.

**Correction :** tenir une revue technique indépendante, inscrire les hypothèses, évaluer le coût de changement et faire valider la formulation par les achats et le juridique. La correction n’est pas de supprimer toute exigence de compatibilité ; elle est de justifier ce qui est réellement nécessaire.

### Cas 2 — Offre à prix très bas

Un candidat propose le prix initial le plus faible, mais facture séparément les interventions hors horaires, les déplacements, certains correctifs et l’export de fin de contrat.

**Analyse :** le prix facial n’est pas comparable si les hypothèses et périmètres diffèrent. Il faut appliquer le modèle de prix et les règles de clarification publiés, vérifier les lignes et les hypothèses, puis comparer le coût total selon la méthode approuvée. Ne pas inventer un supplément ou une sanction après réception pour modifier le classement.

**Correction :** inclure au dossier les unités, volumes, options obligatoires, frais récurrents et conditions de sortie. Si le cadre autorise une clarification, documenter le résultat et son effet. Toute procédure de traitement d’une offre anormalement basse doit suivre les règles applicables.

### Cas 3 — La sortie n’a pas été chiffrée

Le contrat proposé autorise le fournisseur à facturer « les coûts de transfert au tarif en vigueur » sans durée, format d’export ou nombre d’heures estimé.

**Analyse :** le coût et le délai de sortie sont imprévisibles, ce qui favorise l’enfermement fournisseur. L’organisation peut découvrir que les données sont exportables mais pas les configurations, la documentation ou les historiques nécessaires pour poursuivre l’exploitation.

**Correction :** définir les formats, livrables, délais, obligations de coopération, prix ou formule de prix, règles d’accès, validation d’intégrité et suppression contrôlée. Tester la réversibilité sur un échantillon avant que la sortie devienne urgente.

### Cas 4 — Les évaluateurs changent les notes après une présentation commerciale

La grille attribue un poids à la continuité. Un candidat fait une présentation persuasive, puis les évaluateurs augmentent sa note sans relier l’amélioration à une preuve prévue.

**Analyse :** la perception de qualité remplace le critère publié. Si la démonstration ou la soutenance ne faisait pas partie d’une méthode autorisée et annoncée, elle ne doit pas servir à modifier le classement de façon non transparente.

**Correction :** appliquer la méthode annoncée, documenter toute clarification permise et justifier les notes avec les preuves prévues. Si les règles ne permettent pas d’utiliser l’information reçue, consulter le responsable de la procédure avant toute décision.

### Cas 5 — Critère de durabilité impossible à vérifier

Le cahier des charges attribue des points à la « solution la plus verte », sans formule ni preuve attendue.

**Analyse :** le critère est flou et les évaluateurs peuvent l’interpréter différemment. Les candidats ne savent pas comment se différencier et le résultat devient difficile à auditer.

**Correction :** définir l’attribut concerné, la méthode, le périmètre et les preuves recevables, puis vérifier la pertinence et la conformité du critère au régime d’achat. Si un critère ne peut pas être mesuré ou évalué de façon cohérente, le reformuler ou le retirer avant la consultation.

## 15. Exercices d’application avec corrigés détaillés

### Exercice 1 — Exigence testable

**Question :** « Le fournisseur doit assurer un service de haute qualité ». Pourquoi cette formulation est-elle insuffisante et comment l’améliorer ?

**Correction :** la formulation ne définit ni résultat ni seuil ni méthode de mesure. Elle peut être interprétée différemment par chaque candidat et chaque évaluateur. Identifier les dimensions de qualité pertinentes : par exemple, la prise en charge selon la criticité, la disponibilité, la résolution, le taux de réouverture et la satisfaction mesurée selon une méthode convenue. Définir pour chacune une formule, un périmètre, une période, les exclusions et la preuve exigée. Les seuils doivent être construits avec les responsables métier et techniques, puis intégrés au dossier et au contrat.

### Exercice 2 — Notation pondérée

**Question :** deux offres sont conformes. L’offre A obtient 80/100 et l’offre B 78/100. Peut-on attribuer automatiquement le marché à A ?

**Correction :** le score n’est exploitable que si la méthode, les poids, les règles de conformité et la procédure ont été respectés. Il faut contrôler les calculs, s’assurer que les notes s’appuient sur les preuves, examiner les risques ou exigences critiques et appliquer les règles annoncées. Si A ne satisfait pas une exigence obligatoire, un score global supérieur ne l’efface pas. Si les scores sont proches, on ne peut pas inventer un critère de départage après réception ; il faut utiliser le mécanisme prévu.

### Exercice 3 — Coût de cycle de vie

**Question :** un fournisseur propose une licence initiale moins chère mais facture l’intégration, la formation, le support et la sortie séparément. Comment comparer ?

**Correction :** définir un horizon, un profil de consommation, les quantités et les hypothèses de coûts. Ajouter les coûts obligatoires et les postes qui ont été inclus dans la méthode d’évaluation. Distinguer les prix fermes des estimations et des options. Analyser les scénarios sensibles et ne pas ajouter un facteur de coût non annoncé après réception. Si le modèle de prix du dossier n’est pas suffisant pour comparer les offres, demander conseil à l’autorité de procédure avant de poursuivre.

### Exercice 4 — Dépendance fournisseur

**Question :** les données peuvent être exportées, mais les règles métier, les tableaux de bord et les procédures d’exploitation sont propriétaires. Est-ce une réversibilité suffisante ?

**Correction :** pas nécessairement. Un export de données ne garantit pas le transfert d’une capacité exploitable. Il faut inventorier les configurations, les schémas, les métadonnées, les licences, les interfaces, les journaux et les connaissances indispensables. Définir ce qui doit être remis, dans quels formats, à quel moment, avec quelle assistance, et comment l’acheteur validera la réutilisabilité. Tester l’export et la reprise dans un environnement indépendant, si le risque le justifie.

### Exercice 5 — Questions identiques ou équitables

**Question :** un candidat découvre un défaut du cahier des charges et le signale avant la date limite. L’acheteur répond seulement à ce candidat. Quelle est la bonne démarche ?

**Correction :** conserver la question, analyser son effet et appliquer les règles de confidentialité et de communication de la procédure. Si la réponse apporte une information pertinente pour tous les candidats ou modifie l’interprétation du dossier, elle doit être communiquée de manière équitable selon les règles applicables. Un addendum peut être nécessaire et un délai supplémentaire peut s’imposer si le changement affecte la préparation des offres. Ne pas transformer la réponse en avantage individuel.

### Exercice 6 — Offre non conforme mais techniquement excellente

**Question :** une offre obtient d’excellentes notes mais omet une pièce explicitement éliminatoire. Les évaluateurs veulent l’accepter en raison de sa qualité. Que faut-il faire ?

**Correction :** appliquer le traitement prévu par la procédure et consulter le responsable compétent si la nature de l’omission ou les règles de clarification sont ambiguës. Ne pas inventer une exception pour un fournisseur préféré. Selon le régime, certaines omissions peuvent faire l’objet d’une clarification, d’autres non. La décision, la base procédurale et les preuves doivent être documentées et le même traitement appliqué aux offres comparables.

### Exercice 7 — Critère de continuité

**Question :** le fournisseur promet un « PRA robuste », sans décrire la restauration, les dépendances ni les résultats des exercices. Comment rendre le critère utile ?

**Correction :** demander la description du scénario, les composants couverts, le RTO/RPO visé, les préconditions, la source de sauvegarde, les dépendances, les responsabilités, la preuve d’exercice, les résultats, les écarts et le plan d’amélioration. Le critère de notation doit évaluer la pertinence et la preuve de ces éléments, tandis que les engagements nécessaires doivent être transformés en clauses et critères de réception. Ne pas attribuer une excellente note sur la seule base d’une promesse commerciale.

### Exercice 8 — Conflit d’intérêts potentiel

**Question :** un membre de l’équipe d’évaluation a travaillé récemment chez l’un des candidats. Quelle mesure prendre ?

**Correction :** déclarer le lien et suivre la procédure de gestion des conflits d’intérêts. L’autorité compétente évalue la pertinence du lien, l’accès aux informations, l’influence sur les décisions et les mesures nécessaires, qui peuvent inclure la récusation. Il faut consigner la décision et protéger la confidentialité. Ne pas conclure automatiquement à une faute, mais ne pas ignorer le risque parce que le membre se déclare impartial.

### Exercice 9 — Indicateur de SLA ambigu

**Question :** un contrat promet 99,9 % de disponibilité sans préciser le périmètre, la période ni les maintenances exclues. Quels problèmes cela crée-t-il ?

**Correction :** le résultat ne peut être calculé de façon cohérente. Les parties pourraient compter des incidents différents ou exclure des périodes de manière incompatible. Définir le service et le point de mesure, la fenêtre, la formule, les exclusions permises, les données de preuve, la méthode de contestation, les seuils et les remèdes. Un objectif de disponibilité doit aussi être cohérent avec les dépendances et l’architecture réelle.

### Exercice 10 — Changements répétés

**Question :** après attribution, de nombreuses demandes de changement augmentent le prix et le délai. Quelles sont les hypothèses à tester avant d’accuser le fournisseur ?

**Correction :** vérifier si le besoin initial était incomplet, si l’acheteur a changé ses priorités, si les dépendances étaient connues, si l’offre a mal interprété le périmètre, si les rôles de validation sont flous et si le fournisseur découvre des contraintes qu’il aurait dû identifier. Analyser les changements un par un, leur cause, leur coût et leur cumul. Appliquer le mécanisme contractuel et corriger les processus ; l’attribution de responsabilité doit reposer sur des faits.

## 16. Défi final — Construire un dossier d’appel d’offres défendable

### Scénario

Une organisation veut renouveler un contrat critique de maintenance applicative dans six mois. Le service doit rester disponible pendant les périodes de forte activité. Les incidents sont parfois résolus sans analyse de cause, les tests de restauration sont irréguliers, les coûts de sortie sont inconnus et plusieurs procédures sont détenues exclusivement par le fournisseur actuel. Le budget doit inclure la transition, mais le montant n’est pas encore validé. Les équipes veulent un support plus mesurable sans verrouiller le dossier sur une technologie propriétaire.

### Travail demandé

Préparer un dossier de stratégie et de consultation comprenant :
1. une note de besoin, les résultats attendus, le périmètre et les exclusions ;
2. une comparaison des options de faire, acheter, réutiliser et hybrider, avec hypothèses ;
3. une analyse de marché et de concurrence, y compris les dépendances communes ;
4. une décision motivée sur l’allotissement ou le regroupement ;
5. une liste d’exigences fonctionnelles, de performance, de sécurité, de service, de continuité et de sortie, reliées à des preuves ;
6. un calendrier réaliste avec les étapes d’approbation et la gestion des questions ;
7. une distinction entre admissibilité, conformité obligatoire et critères de notation ;
8. une grille pondérée et des ancres de notation préalablement définies ;
9. un modèle de coût total sur la durée du contrat, intégrant migration, support, exploitation et sortie ;
10. une méthode de réception, de pilotage du contrat, de changement et de suivi du SLA ;
11. un traitement des conflits d’intérêts, de la confidentialité et de la piste d’audit ;
12. un plan de transition et de réversibilité avec des tests ;
13. un registre de risques, les responsables, les mesures et les critères d’escalade ;
14. une note d’attribution qui explique pourquoi le choix retenu offre la meilleure valeur dans le cadre annoncé.

### Correction de référence

**Besoin.** Définir les résultats métier, les profils utilisateurs, les périodes critiques et l’état actuel. Identifier les incidents récurrents, les limites de documentation et le manque de test comme des problèmes mesurables plutôt que prescrire d’emblée une solution. Les hypothèses de volumes et de criticité sont validées par les propriétaires du service.

**Stratégie.** Comparer le renouvellement, une remise en concurrence, la réinternalisation de certains savoirs, une approche hybride et les contraintes d’interopérabilité. Décrire la concurrence disponible et les risques de dépendance. Valider le type de procédure selon le droit, le statut de l’acheteur, le financement et les politiques applicables.

**Exigences.** Définir les catégories d’incidents, les délais, le périmètre de support, les preuves de performance, la procédure de restauration, les critères de validation des données, le transfert des compétences et l’export. Chaque exigence critique doit disposer d’un test ou d’une preuve et d’une obligation contractuelle correspondante.

**Évaluation.** Annoncer les conditions obligatoires et les critères notés avant réception. Les poids sont justifiés par les risques et les besoins. Les évaluateurs déclarent leurs intérêts, suivent une calibration, documentent les notes et conservent les calculs. La qualité de l’offre ne remplace pas la conformité exigée par la procédure.

**Coût et risque.** Le TCO inclut les postes de transition, de support, de maintenance, de formation et de sortie. Les scénarios de volume, de hausse des coûts et de changement fournisseur sont examinés selon une méthode publiée. Les risques critiques sont traités à part du score lorsque le dossier prévoit des conditions éliminatoires ou des exigences minimales.

**Contrat.** Les promesses qui déterminent le classement sont traduites en livrables, SLA, critères de recette et responsabilités. Les changements, paiements, rapports, défauts récurrents, plans de continuité et conditions de sortie sont encadrés. Le contrat doit être compatible avec le cadre applicable et ne pas introduire d’obligations contradictoires avec le dossier.

**Transition et sortie.** La transition prévoit un inventaire des actifs et connaissances, les autorisations, la formation, les procédures, le test de continuité, les formats de données et la validation de fin. La réversibilité est chiffrée et testée, au moins sur un échantillon lorsque cela est proportionné.

**Décision.** Le rapport d’attribution présente la conformité, les scores, les calculs, les preuves et les risques résiduels selon la méthode prévue. Il explique en quoi la solution retenue répond au besoin et aux critères publiés, sans introduire de raison nouvelle ou non annoncée. Les autorisations et formalités de la procédure doivent être achevées avant la signature.

### Barème indicatif sur 100

| Dimension | Points |
|---|---:|
| Cadrage, stratégie et analyse du marché | 15 |
| Qualité et vérifiabilité des exigences | 15 |
| Cohérence des critères, de la notation et des preuves | 20 |
| TCO, risques et soutenabilité financière | 15 |
| Intégrité, traçabilité et maîtrise procédurale | 10 |
| Contrat, SLA, recette et pilotage | 15 |
| Transition et réversibilité | 10 |

Ce barème sert à évaluer l’exercice pédagogique. Il ne doit pas être transposé dans une consultation réelle comme méthode de sélection sans analyse, approbation et publication conformément au régime applicable.

## 17. Références et approfondissement

Les références suivantes ont des portées différentes. Elles doivent être utilisées pour approfondir la méthode et non comme substitut au cadre contractuel ou juridique applicable.

- [CNUDCI — Loi type sur la passation des marchés publics (2011)](https://uncitral.un.org/fr/texts/procurement/modellaw/public_procurement) : principes d’objectivité, d’équité, de concurrence, d’intégrité et de transparence. Une loi type internationale n’est pas automatiquement la loi applicable au marché étudié.
- [CNUDCI — Guide pour l’incorporation de la Loi type](https://uncitral.un.org/en/texts/procurement/modellaw/public_procurement/guide) : contexte des dispositions et éléments de mise en œuvre.
- [Banque mondiale — Cadre de passation des marchés](https://www.worldbank.org/ext/en/what-we-do/project-procurement/framework) : ressources, documents standards, orientations et exigences propres aux projets financés par le financement de projets d’investissement de la Banque mondiale.
- [Banque mondiale — Règlement de passation des marchés, septième édition, septembre 2025](https://thedocs.worldbank.org/en/doc/c84273d1b230aeb2b0b8134de5dc8cd7-0290012025/original/Procurement-Regulations-7th-Edition-Sep-2025.pdf) : règles à consulter lorsque le financement et la procédure relèvent effectivement de ce cadre.
- [OCDE — Recommandation sur les marchés publics](https://legalinstruments.oecd.org/en/instruments/OECD-LEGAL-0411) : principes de transparence, intégrité, accès, efficacité, gestion des risques, responsabilité et intégration du cycle d’achat.
- [OCDE — Boîte à outils pour l’investissement public efficace](https://www.oecd.org/en/about/projects/effective-public-investment-toolkit.html) : ressources sur la transparence, la professionnalisation et l’utilisation stratégique des achats publics.
- [ISO 20400:2017 — Achats responsables](https://www.iso.org/fr/standard/63026.html) : guide pour intégrer la responsabilité sociétale et les considérations de durabilité dans les achats. La fiche ISO indique que l’édition a été confirmée en 2023 ; vérifier son statut au moment de l’utilisation.

Pour chaque achat réel, identifier l’édition applicable, la juridiction, le financement, les documents standards obligatoires et la personne responsable de la conformité. Conserver un registre des exigences et de leur traduction dans le dossier, puis vérifier que chaque point pertinent correspond à une procédure, une clause ou une preuve. Une liste de références ne constitue jamais à elle seule une certification de conformité.

## Synthèse finale

Un appel d’offres expert est une chaîne de traçabilité, depuis le résultat métier jusqu’à la preuve de réception et à la sortie du fournisseur. La stratégie d’achat doit être justifiée par le marché, le risque et les alternatives. Les exigences doivent être mesurables. Les critères doivent être reliés au besoin et appliqués comme annoncé. Les prix doivent être comparés sur un périmètre et un horizon cohérents. Les échanges doivent rester équitables et documentés. Les obligations déterminantes doivent être inscrites dans le contrat et vérifiées pendant l’exécution.

La rédaction n’est donc pas terminée à la publication de l’avis. Elle doit préparer l’évaluation, la décision, la transition, l’exploitation, la gestion des incidents et la réversibilité. Le professionnel expert sait expliquer pourquoi une exigence existe, quelle preuve permettra de la vérifier, quel risque demeure et qui a autorité pour l’accepter. Cette discipline protège l’organisation, les candidats et les utilisateurs finaux, tout en augmentant la probabilité que le marché produise réellement la valeur attendue.
