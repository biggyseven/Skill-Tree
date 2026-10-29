# Layer 2 (Rollups, sidechains)

## Encadré de mise en contexte

Une blockchain publique doit concilier plusieurs objectifs difficiles : laisser de nombreux participants vérifier le système, garder un historique cohérent, résister à la censure, traiter des transactions et faire payer des ressources limitées. Lorsque la demande augmente, le coût et le délai de confirmation peuvent augmenter eux aussi. Les solutions de couche 2, souvent appelées L2, cherchent à déplacer une partie du travail hors de la couche de base tout en conservant des garanties de sécurité définies.

Le mot Layer 2 ne désigne pas une technologie unique. Un rollup optimiste, un rollup à preuves de validité, une sidechain, un validium et un canal de paiement peuvent tous améliorer certains aspects de l'expérience, mais ne s'appuient pas sur les mêmes mécanismes de sécurité. Le nom commercial, le débit annoncé ou le coût d'une transaction ne suffisent pas à déterminer le niveau de confiance nécessaire. La question centrale de ce cours est : qu'est-ce qui protège réellement les fonds et l'état lorsque l'opérateur de la couche secondaire est défaillant, malveillant ou indisponible ?

Cette leçon prend Ethereum comme fil conducteur, car ses mécanismes de rollup sont largement documentés. Les concepts peuvent aider à analyser d'autres écosystèmes, mais les règles exactes, les fenêtres de sortie, les frais et les garanties doivent toujours être vérifiés pour le réseau étudié.

## Objectifs d'apprentissage

À la fin du cours, tu dois pouvoir expliquer la différence entre une couche de base, un rollup et une sidechain ; décrire les rôles du séquenceur, des contrats de règlement, des preuves et des données ; comparer les rollups optimistes et les rollups à preuves de validité ; comprendre pourquoi la disponibilité des données est aussi importante que la correction du calcul ; analyser les étapes d'un dépôt et d'un retrait ; décomposer les frais d'une opération ; vérifier le réseau et les contrats concernés ; et rédiger une évaluation de risque qui ne se contente pas de recopier une promesse marketing.

## Prérequis et parcours pratique

Il est utile de maîtriser les blocs, les transactions, le consensus, les smart contracts, l'EVM, les portefeuilles et les standards de jetons. Si ces notions sont nouvelles, commence par le cours sur les blocs, celui sur le consensus, puis celui sur l'EVM. Ne dépose pas de fonds réels pendant les exercices : utilise une chaîne locale ou un réseau de test que tu comprends.

Le parcours pratique consiste à sélectionner deux environnements L2, documenter l'identifiant de chaîne, le RPC, l'explorateur et le mécanisme officiel de pont, puis suivre une opération de test de bout en bout. L'objectif n'est pas de choisir arbitrairement le meilleur L2, mais d'apprendre à comparer les hypothèses de confiance et à détecter ce que les indicateurs de performance ne disent pas.

## 1. Le problème de mise à l'échelle

Une blockchain réplique le travail de validation entre plusieurs participants. Cette réplication est l'une des sources de la confiance partagée, mais elle crée aussi des limites de capacité. La couche de base doit faire respecter les règles de consensus, exécuter ou vérifier les transitions d'état, organiser les transactions et rendre disponibles les données nécessaires aux vérificateurs. Augmenter la capacité sans préserver ces fonctions peut simplement déplacer la confiance vers une entité privée.

Trois termes doivent être distingués. Le débit indique le volume de travail traité sur une période. La latence mesure le temps écoulé entre une action et un événement observable, comme l'inclusion. La finalité décrit le niveau auquel une opération est considérée comme ne pouvant plus être annulée selon le protocole et sa politique de sécurité. Une interface rapide n'implique pas que l'opération soit finalisée. Un réseau peut proposer des blocs fréquents mais des sorties vers L1 qui attendent davantage.

Le coût est une autre dimension. Une transaction L2 peut coûter moins cher parce que plusieurs opérations partagent une partie des coûts de publication, parce que les données sont compressées, ou parce que le réseau fonctionne avec des garanties différentes de celles de L1. Il ne faut pas comparer deux prix sans noter le type d'opération, la congestion, la taille des données, la période et la devise utilisée pour le paiement.

La mise à l'échelle doit donc être évaluée comme un compromis entre capacité, disponibilité, coût, délai, sécurité, gouvernance et facilité de sortie. Aucun chiffre unique ne résume l'ensemble.

## 2. Comprendre les couches

La couche de base, ou L1 dans le contexte Ethereum, assure les fonctions de consensus, d'inclusion et d'état propres à son protocole. Un système de couche supérieure cherche à éviter que chaque opération soit exécutée individuellement par tous les validateurs de la couche de base, tout en conservant une méthode permettant de vérifier ou de régler les résultats.

~~~mermaid
flowchart TD
    U[Utilisateurs et applications] --> L2[Exécution sur la couche secondaire]
    L2 --> B[Lots de transactions et état proposé]
    B --> DA[Données publiées ou rendues disponibles]
    B --> P[Preuve ou mécanisme de contestation]
    DA --> L1[Couche de base : consensus et règlement]
    P --> L1
    L1 --> C[État accepté selon les règles du protocole]
~~~

Ce dessin reste conceptuel. Les rollups réels diffèrent par l'organisation des contrats, la disponibilité des données, les méthodes d'exécution, la gouvernance, la manière de traiter les dépôts et la possibilité de forcer une opération sur L1. Il faut donc remplacer ce schéma de principe par la documentation d'architecture du système évalué avant une décision de sécurité.

L'expression hériter de la sécurité de L1 doit être employée avec précision. Un rollup peut utiliser L1 pour le règlement et la disponibilité des données, mais dépendre également d'un séquenceur, de clés d'administration, d'un système de preuve, d'un pont ou d'une procédure de mise à niveau. Une panne ou une compromission de ces composants peut affecter la disponibilité, la résistance à la censure ou la possibilité de sortir, même si le consensus de L1 reste sain.

## 3. Rollup, sidechain, validium et canal : ne pas tout confondre

Un rollup exécute les transactions hors de L1 puis publie des données et des engagements d'état selon un modèle qui permet à L1 d'appliquer certaines garanties sur les transitions. Les rollups optimistes reposent sur une procédure de contestation des transitions invalides. Les rollups à preuves de validité demandent une preuve cryptographique acceptée par un vérificateur avant l'acceptation de la transition correspondante.

Une sidechain est une chaîne distincte avec son propre mécanisme de consensus et ses propres hypothèses de sécurité. Elle peut être reliée à Ethereum par un pont, mais le simple fait qu'elle ait un pont n'en fait pas un rollup. Les validateurs de la sidechain peuvent être indépendants de ceux d'Ethereum ; la sécurité du pont ne garantit pas que chaque règle de la chaîne secondaire soit équivalente à celle d'Ethereum.

Un validium vérifie les transitions au moyen de preuves de validité, mais conserve les données de transaction hors de L1 dans son modèle typique. Cette séparation peut réduire le coût de publication, mais introduit une hypothèse de disponibilité des données : il faut pouvoir accéder aux informations qui permettent de reconstruire l'état et d'utiliser les comptes. La preuve que le calcul est correct n'est pas la preuve que toutes les données nécessaires sont accessibles.

Un canal permet à un groupe de participants d'effectuer plusieurs mises à jour hors chaîne, sous réserve de règles qui rendent possible la résolution sur la couche de base. Il peut réduire fortement le volume d'opérations on-chain pour certains usages, mais ne correspond pas à un environnement général d'exécution de contrats identique à un rollup.

| Type de solution | Où se fait le calcul ? | Où se trouvent les garanties clés ? | Question à vérifier |
|---|---|---|---|
| Rollup optimiste | Principalement sur L2 | Règlement et données liés à L1, contestation des transitions | Qui peut contester et sous quelles conditions ? |
| Rollup à preuve de validité | Principalement sur L2 | Contrat vérificateur et données publiées selon le système | Quelle preuve est vérifiée et quelles données sont disponibles ? |
| Sidechain | Sur sa chaîne | Consensus et validateurs propres à la sidechain | Qui contrôle le consensus secondaire ? |
| Validium | Hors de L1 | Preuve de validité, mais disponibilité de données séparée | Que se passe-t-il si les données ne sont plus servies ? |
| Canal | Hors chaîne entre participants | Règles de clôture et recours à L1 | Qui peut déclencher la fermeture et dans quel délai ? |

Il existe des variantes et des architectures hybrides. La classification doit se baser sur le mécanisme réellement déployé, pas seulement sur le nom du produit.

## 4. Anatomie d'un rollup

Un rollup comporte généralement un environnement d'exécution L2, un ou plusieurs producteurs de lots, un mécanisme de publication vers L1, des contrats qui suivent l'état ou les dépôts, et une stratégie permettant d'assurer que les transitions sont acceptées conformément aux règles. Le séquenceur ordonne souvent les transactions et donne une réponse rapide à l'utilisateur. Il peut être centralisé ou distribué selon le projet et son stade de développement.

Le séquenceur est important, car l'ordre d'exécution peut influencer l'état et la valeur économique. S'il est hors ligne, l'application peut être incapable d'inclure rapidement des transactions. S'il refuse une transaction, la question devient : existe-t-il une procédure permettant de la soumettre directement au contrat L1 ou à un autre mécanisme, et quel niveau de complexité cette procédure impose-t-elle à l'utilisateur ? La possibilité de forcer une opération ne signifie pas toujours qu'elle est rapide ou conviviale.

Le proposeur de lots soumet à L1 une représentation de l'activité L2, comme des données de transactions ou un engagement d'état. Le contrat L1 vérifie ensuite les conditions prévues. Il faut distinguer la confirmation d'une transaction L2 par le séquenceur, l'inclusion du lot sur L1, l'acceptation de l'état par le mécanisme de preuve ou de contestation, et la finalité de la transaction L1. L'application devrait éviter de présenter ces étapes comme un seul événement.

~~~mermaid
sequenceDiagram
    participant W as Portefeuille
    participant S as Séquenceur L2
    participant E as Exécution L2
    participant L as Contrat de règlement L1
    W->>S: Soumettre une transaction signée
    S->>E: Ordonner et exécuter
    E-->>W: Résultat rapide provisoire
    S->>L: Publier lot et données ou engagement
    L-->>S: Lot enregistré selon les règles L1
    Note over L,L: Preuve ou fenêtre de contestation
    L-->>W: État confirmé selon la politique du rollup
~~~

Le diagramme est volontairement simplifié. Selon le rollup, certains calculs et validations interviennent dans des composants supplémentaires. Quand tu lis une documentation technique, identifie précisément quelle étape est représentée par le mot confirmation et laquelle correspond à la sécurité finale de la transition.

## 5. Disponibilité des données : pourquoi elle est essentielle

La disponibilité des données signifie que les informations nécessaires à la vérification ou à la reconstruction de l'état peuvent être obtenues par les acteurs qui en ont besoin. Un engagement cryptographique vers un état ne permet pas, à lui seul, de reconstruire toutes les données cachées derrière cet état. Si un opérateur publie seulement une racine d'état et retient les informations nécessaires pour prouver ou reconstruire les comptes, les utilisateurs peuvent perdre la capacité de suivre leur solde ou de sortir selon le modèle prévu.

Les rollups Ethereum publient généralement les données nécessaires à la reconstruction par des mécanismes d'espace de données on-chain, qui peuvent inclure calldata ou blobs selon l'architecture. Les blobs introduits par EIP-4844 ont un cycle de disponibilité spécifique et ne doivent pas être décrits comme un stockage permanent de fichiers. Le système de disponibilité de données d'un rollup doit être analysé dans sa documentation propre : il ne suffit pas de constater que certaines données sont référencées par un hash.

Il faut distinguer trois propriétés : intégrité, disponibilité et persistance à long terme. L'intégrité vérifie que le contenu correspond à un engagement. La disponibilité détermine si le contenu peut être obtenu à temps pour vérifier ou contester. La persistance détermine si l'information sera conservée à long terme. Ces propriétés se recouvrent parfois, mais ne sont pas équivalentes.

Exemple : un système peut publier une preuve valide d'une mise à jour d'état sans publier toutes les données d'état requises pour rendre les fonds accessibles à leurs propriétaires. Le calcul peut avoir été correct, mais les utilisateurs peuvent quand même rencontrer un problème de disponibilité ou de récupération. C'est pourquoi l'évaluation doit inclure une question pratique : dans quelles conditions un utilisateur peut-il vérifier son solde et exercer son droit de sortie sans permission de l'opérateur ?

## 6. Rollups optimistes et preuves de fraude

Un rollup optimiste propose des transitions d'état en supposant qu'elles sont valides, puis fournit une période ou un mécanisme pendant lequel une partie peut contester un résultat incorrect. La sécurité dépend de plusieurs conditions : les données nécessaires sont disponibles, au moins un acteur capable de détecter et contester une fraude peut agir, la preuve de contestation est correctement implémentée, et la procédure est opérationnelle dans les délais. Ces conditions ne doivent pas être résumées par la simple formule il y a une période de contestation.

La période de contestation influe sur l'expérience de retrait : une opération peut être incluse sur L2 et visible dans l'interface alors que le retrait vers L1 attend le résultat de la procédure. Certains ponts tiers peuvent fournir une liquidité plus rapide, mais ce service rapide ajoute ses propres risques, tarifs et contreparties. Un utilisateur doit savoir s'il utilise le retrait canonique du rollup ou une route tierce qui avance les fonds.

Une preuve de fraude est un mécanisme technique qui cherche à démontrer que la transition annoncée ne respecte pas les règles. Sa sécurité dépend du système de vérification, du délai de contestation, de la possibilité pratique d'exécuter un challenger et des règles de résolution en cas de litige. Une contestation n'est pas un vote d'opinion : elle doit respecter la procédure formelle du protocole.

La revue d'un rollup optimiste doit examiner le chemin de sortie en cas de séquenceur indisponible, la possibilité de publier une transaction forcée, les délais, les frais L1 nécessaires, l'accès aux données et le comportement en cas de panne prolongée. Un scénario de sécurité réaliste inclut un opérateur qui ne répond plus au moment où l'utilisateur veut sortir, pas seulement un scénario où tout le système fonctionne normalement.

## 7. Rollups à preuves de validité et ZK

Les rollups à preuves de validité font vérifier cryptographiquement par un contrat ou un mécanisme de confiance défini qu'une transition d'état respecte les règles représentées. Le producteur peut calculer une grande quantité de transactions hors L1 puis fournir une preuve plus compacte que le rejeu complet de l'ensemble. Ce mécanisme peut améliorer l'efficacité de la vérification on-chain, mais le coût de génération des preuves, le matériel, l'architecture de preuve et les règles du contrat restent des éléments déterminants.

L'expression zero knowledge est souvent utilisée dans ZK-rollup, mais il faut distinguer une preuve de validité et une garantie de confidentialité. La preuve peut démontrer la correction d'une transition sans rendre les données de la transaction privées si ces données sont publiées. Un rollup peut employer une technologie de preuve apparentée aux ZK proofs pour garantir la validité, tout en laissant les transactions et l'état visibles. La confidentialité dépend de ce qui est prouvé et divulgué, pas seulement du nom.

La compatibilité EVM varie également. Certains systèmes cherchent à exécuter des bytecodes ou des opcodes proches de l'EVM ; d'autres imposent des différences dans les outils, le langage ou la manière dont les preuves sont générées. Avant de déployer un contrat, vérifie le compilateur supporté, les précompilations, les coûts de gas, le traitement des événements, les limites de taille et les particularités des bibliothèques. Un contrat qui compile sur Ethereum n'est pas automatiquement compatible avec n'importe quel L2.

Les systèmes de preuves ont leurs propres risques : erreurs de circuits, configuration, confiance dans un paramétrage spécifique lorsque le système le requiert, bug du vérificateur ou différences entre le modèle prouvé et le comportement réel de l'exécution. Une preuve mathématiquement valide garantit seulement la propriété encodée dans le système. La question d'audit est donc : quelle propriété exacte la preuve garantit-elle, et quelles parties de l'architecture restent en dehors de cette garantie ?

## 8. Frais : ce que paie vraiment l'utilisateur

La facture d'une opération sur L2 peut combiner un coût d'exécution local, le coût de publication des données vers L1, des frais de séquenceur ou de service, et éventuellement des frais propres à la preuve ou au mécanisme de règlement. La façon exacte de calculer le prix dépend de l'architecture et peut évoluer avec la congestion ou les mises à jour du protocole.

Une transaction simple et une transaction avec beaucoup de données d'appel ne consomment pas les mêmes ressources. Le coût de publication varie aussi selon la compression du lot et la quantité d'informations qui doit être publiée. Une estimation affichée par un portefeuille ne garantit pas que le montant final sera identique : la charge, la taille des données et l'état d'exécution peuvent changer entre simulation et inclusion.

Pour comparer deux réseaux, utilise la même opération métier, la même taille approximative de paramètres, une période documentée et la devise d'origine. Distingue aussi le coût d'entrée sur le réseau, les frais de transaction, les frais de sortie et le coût du pont. Une route qui semble peu chère pour une transaction locale peut être plus coûteuse lorsqu'on ajoute le dépôt et le retrait canoniques.

| Élément de coût | Question à poser |
|---|---|
| Exécution L2 | Quel travail exécute le contrat et quelle unité tarifaire est appliquée ? |
| Publication de données | Quelle partie de la transaction doit être publiée ou rendue disponible ? |
| Frais de séquenceur | Un supplément est-il appliqué à l'opération ? |
| Entrée depuis L1 | Quels frais et délais sont requis pour déposer ? |
| Sortie vers L1 | Quelle procédure, quels coûts et quelles attentes s'appliquent ? |
| Pont tiers | Quel risque de liquidité, de contrepartie ou de contrat est ajouté ? |

## 9. Dépôts et retraits : suivre la chaîne complète

Le dépôt canonique commence en général par une transaction sur L1 vers un contrat reconnu par le rollup. L'opération est alors détectée par l'infrastructure de L2, puis mise en file ou incluse selon les règles du système. Le délai dépend de l'inclusion et de l'indexation, et une interface doit éviter de montrer le dépôt comme disponible avant que la logique l'autorise.

Le retrait suit souvent plusieurs étapes : l'utilisateur envoie la valeur vers un mécanisme d'exit sur L2, l'opération est incluse dans un lot, le lot atteint l'état requis sur L1, puis l'utilisateur finalise la sortie en appelant un contrat L1. Dans certains modèles optimistes, une fenêtre de contestation intervient entre les étapes. Les détails diffèrent d'une chaîne à l'autre ; il faut consulter la documentation du pont canonique pour le trajet et les exceptions.

~~~mermaid
flowchart TD
    A[Actif sur L1] --> B[Transaction de dépôt]
    B --> C[Contrat d'entrée du rollup]
    C --> D[Opération traitée sur L2]
    D --> E[Utilisateur utilise le solde sur L2]
    E --> F[Demande de sortie sur L2]
    F --> G[Lot et preuve ou contestation]
    G --> H[Finalisation sur L1]
    H --> I[Actif reçu sur L1]
~~~

Les ponts tiers ajoutent une route différente. Certains utilisent une réserve de liquidité pour avancer les fonds ; d'autres dépendent de validateurs externes ou de contrats différents. La vitesse supplémentaire n'est pas gratuite en termes de confiance. L'utilisateur doit vérifier les actifs reçus, le réseau cible, les frais, la liquidité disponible et les hypothèses de sécurité du service.

## 10. Sécurité : séquenceur, clés et pouvoirs d'administration

Même si la couche de base est robuste, un rollup peut dépendre de pouvoirs administratifs capables de changer des contrats, de mettre à niveau un vérificateur, de régler les paramètres de sortie ou d'activer une fonction d'urgence. Il faut examiner les rôles, les multisignatures, les délais, la distribution des clés et la procédure en cas de clé perdue ou compromise.

Un séquenceur centralisé peut fournir une expérience rapide, mais il constitue aussi un point de contrôle sur l'ordre et l'inclusion. La disponibilité d'un chemin de transaction forcée peut réduire le risque de censure durable, mais seulement si le chemin est documenté, réalisable et compatible avec les ressources dont dispose l'utilisateur. Les exigences de frais et de connaissance technique peuvent rendre une protection théorique difficile à exercer en pratique.

Le suivi de la décentralisation ne doit pas se limiter à un indicateur marketing. Examine si l'utilisateur peut exécuter son propre nœud, produire des preuves, vérifier les données, soumettre une transaction en cas d'indisponibilité du séquenceur et sortir sans l'autorisation d'un opérateur. Identifie aussi le composant qui peut mettre à niveau le code et les garde-fous qui limitent les changements.

Un audit indépendant est un élément utile, mais pas une garantie absolue. La portée de l'audit, le commit examiné, les composants exclus, les correctifs réalisés et les changements ultérieurs comptent autant que le logo de l'auditeur. Un rapport doit être lu comme une preuve délimitée et datée, pas comme un certificat éternel de sécurité.

## 11. Préparer une matrice de risque pour un choix de L2

Une matrice de décision évite de choisir uniquement sur le prix ou le débit annoncé. Les critères doivent être pondérés selon l'application. Pour une application de jeu, le délai perçu et le coût peuvent être déterminants ; pour une application de conservation d'actifs, la possibilité de vérification, les chemins de sortie et les pouvoirs administratifs prennent plus de poids.

| Critère | Question d'audit | Exemple de preuve |
|---|---|---|
| Sécurité de l'état | Quel mécanisme accepte les transitions ? | Spécification, contrats et tests |
| Disponibilité des données | Les utilisateurs peuvent-ils reconstruire l'état ? | Documentation et procédure de récupération |
| Résistance à la censure | Existe-t-il une route forcée ? | Procédure et frais de soumission forcée |
| Gouvernance | Qui peut modifier les contrats ? | Rôles, multisig, délai et historique des mises à niveau |
| Retrait | Quel événement permet une sortie sur L1 ? | Documentation du pont canonique |
| Compatibilité | Les outils et contrats sont-ils compatibles ? | Tests sur réseau de test et règles du compilateur |
| Coût | Quel est le coût total du cycle métier ? | Mesures datées d'un dépôt, d'une action et d'une sortie |
| Continuité | Comment l'équipe réagit-elle à une panne ? | Runbook testé et sources de surveillance |

Attribue à chaque critère une note accompagnée d'une justification et d'un niveau de confiance. Une donnée inconnue ne doit pas recevoir une note favorable par défaut. Écris également les conditions éliminatoires : par exemple, une impossibilité de sortir dans le modèle de menace accepté ou une dépendance administrative que l'organisation ne peut tolérer.

## 12. TP guidé A : explorer un rollup sans engager de fonds

L'objectif est de vérifier une route de bout en bout avec des informations publiques et une petite transaction de test. Choisis un environnement qui fournit une documentation officielle, un explorateur et un mécanisme de dépôt et de retrait clairement identifié. Ne copie pas une adresse d'un message non vérifié.

### Étapes

1. Identifie le réseau et vérifie son identifiant de chaîne dans la documentation et dans le portefeuille.
2. Compare l'adresse du contrat de pont affichée par la documentation avec celle de l'explorateur.
3. Lis les conditions de dépôt et de retrait, notamment les délais et frais.
4. Effectue une opération sans valeur financière réelle en utilisant un réseau de test approprié.
5. Enregistre le hash L1, le hash ou reçu L2 si disponible, les horodatages et les états visibles.
6. Vérifie que les changements de solde correspondent au montant attendu et aux frais.
7. Décris les étapes qu'il faudrait suivre si le séquenceur n'était pas disponible.

### Résultat attendu

Le rapport distingue l'envoi par le portefeuille, la diffusion, l'inclusion, l'état observé sur L2 et la finalité selon la procédure du pont. Il cite les sources officielles consultées, note les inconnues et n'affirme pas avoir éprouvé une sortie forcée si le test ne l'a pas réellement exécutée.

## 13. TP guidé B : comparer deux solutions de mise à l'échelle

Sélectionne deux projets avec des modèles différents, par exemple un rollup optimiste et un rollup utilisant des preuves de validité. Utilise les mêmes catégories pour comparer l'exécution, le mécanisme d'état, la disponibilité des données, la sortie, l'administration et la compatibilité des outils. Ne traite pas toutes les chaînes d'une même catégorie comme identiques.

Crée ensuite un tableau contenant les liens documentaires et la date de consultation. Si une information n'est pas disponible, marque-la comme inconnue. Une comparaison honnête peut conclure qu'un point n'a pas pu être vérifié ; elle ne doit pas inventer une valeur pour remplir une cellule.

### Correction proposée

Une bonne comparaison ne donne pas un vainqueur universel. Elle explique quels critères sont les plus importants pour une application donnée, quelles garanties sont héritées de L1, quelles dépendances supplémentaires existent et quelles incertitudes restent à lever. Elle différencie une garantie cryptographique, une procédure opérateur, une promesse de gouvernance et un indicateur de performance.

## 14. Étude de cas : un séquenceur indisponible

Une application de commerce observe que les utilisateurs ne peuvent plus inclure de transactions sur L2. Les pages de statut publiques sont contradictoires ; les lecteurs RPC renvoient des hauteurs différentes et un utilisateur souhaite retirer un actif vers L1. L'équipe doit éviter d'annoncer une perte de fonds avant d'avoir vérifié l'état du système.

### Travail demandé

Écris les hypothèses possibles, les données à collecter, les opérations qui doivent rester bloquées, les sources à comparer et les conditions qui autorisent la reprise. Précise comment aider l'utilisateur à suivre la procédure officielle sans lui demander de partager une clé privée ou un secret du portefeuille.

### Correction proposée

Commence par vérifier les réseaux et les hauteurs auprès de plusieurs sources indépendantes. Consulte la documentation officielle pour identifier les chemins d'urgence et les délais. Ne modifie pas les contrats ni les paramètres de sécurité à la volée pour rétablir l'affichage. Si une sortie forcée existe, communique les prérequis, les frais, les délais et la source qui explique la procédure. Réactive ensuite les opérations progressivement, après vérification des hashes, de l'état final et de l'absence d'une régression persistante.

## 15. Étude de cas : le prix annoncé ne reflète pas le coût final

Une équipe compare deux L2 et choisit celui qui présente la transaction simple la moins chère. Après déploiement, les opérations sont plus onéreuses que prévu, car les appels métier transportent davantage de données, les utilisateurs paient des frais d'entrée et certains doivent emprunter un pont tiers pour sortir. Le benchmark initial ne couvrait qu'une partie du cycle.

La correction consiste à définir un scénario métier représentatif : dépôt, appel de contrat avec paramètres réels, lecture de l'état, éventuelle approbation de jeton et retrait. Mesure chaque étape sur plusieurs périodes et distingue les coûts ponctuels des coûts récurrents. Documente l'incertitude et évite de projeter une observation de faible congestion sur toutes les conditions futures.

## 16. Choisir des preuves de sécurité plutôt que des slogans

Une évaluation technique doit relier chaque affirmation à une preuve. Une page marketing peut annoncer un séquenceur décentralisé, une sécurité héritée d'Ethereum ou un système de retrait sans permission ; la question est de savoir quel mécanisme rend ces affirmations vraies. Pour chaque promesse, cherche une description du protocole, les contrats concernés, les permissions, les délais et une procédure observable qui permet de tester la propriété.

Pour la sécurité de l'état, identifie la pièce qui vérifie la transition proposée et la manière dont elle est configurée. Pour l'accès aux données, demande quelles données sont publiées, pendant combien de temps elles sont disponibles selon le protocole et quels acteurs peuvent les récupérer. Pour la résistance à la censure, vérifie qui peut soumettre une transaction et si un mécanisme de sortie indépendant du séquenceur existe réellement. Pour la gouvernance, cherche les adresses de multisignature, les délais de changement, les rôles d'urgence et l'historique des mises à niveau.

Une preuve de sécurité peut être un contrat vérifié, une spécification, un rapport de test, une transaction publique ou une procédure reproduisible. Elle doit correspondre à la version examinée. Un audit d'une ancienne implémentation ne prouve pas que le code actif est identique. Un dépôt open source ne prouve pas à lui seul que le bytecode déployé correspond au code du dépôt. Une procédure de sortie documentée n'est pas testée tant qu'on n'a pas identifié ses prérequis, les frais requis et les dépendances opérationnelles.

Crée une matrice qui relie chaque affirmation à son élément de preuve, à son propriétaire et à la date de la dernière validation. Si une preuve est manquante, marque le point comme inconnu, demande des informations ou traite l'inconnu comme une hypothèse de risque. Une évaluation robuste ne remplit pas les cases inconnues avec des suppositions favorables.

| Affirmation | Preuve à chercher | Si elle manque |
|---|---|---|
| Les transitions sont vérifiées | Contrat de preuve ou de contestation et règles associées | Ne pas assimiler l'état proposé à l'état final |
| Les données sont disponibles | Modèle de publication, disponibilité et récupération | Évaluer le risque de blocage des utilisateurs |
| Le séquenceur ne peut pas censurer durablement | Chemin forcé, délais et procédure utilisable | Documenter une dépendance de disponibilité |
| La sortie est garantie selon le modèle | Contrats, conditions, coûts et tests | Ne pas considérer le solde affiché comme un droit de sortie immédiat |
| Les mises à niveau sont contrôlées | Rôles, délais, multisignature et historique | Traiter l'administration comme un risque critique |

## 17. Les étapes de confirmation doivent être nommées dans l'interface

Une expérience utilisateur claire décrit des états qui correspondent à des faits. Une transaction « signée » signifie que le portefeuille a autorisé les données ; elle n'est pas nécessairement diffusée. « Envoyée » signifie que l'application a reçu un identifiant de soumission ; le RPC peut répondre après avoir relayé la transaction, sans garantir son inclusion. « Incluse sur L2 » signifie qu'un bloc de L2 contient la transaction selon la source consultée. « Publiée sur L1 » peut décrire le lot qui contient cette activité. Ces étapes ne doivent pas être fusionnées.

Le mot « confirmée » doit être défini. Un explorateur peut appeler confirmation le fait d'être dans un bloc, alors qu'une application financière peut exiger une finalité spécifique ou un nombre de confirmations. Si l'interface se contente d'une coche verte à la première réponse du séquenceur, l'utilisateur peut croire que l'opération est irréversible alors qu'elle est encore provisoire.

Définis le statut métier séparément du statut technique. Une transaction incluse avec succès ne signifie pas nécessairement que le contrat a créé le droit attendu ; elle peut avoir appelé une adresse incorrecte, avoir exécuté une autre fonction ou avoir produit un montant différent après frais. L'application doit lire le reçu et l'état attendu, puis confirmer que l'identifiant d'opération correspond à la demande originale.

Pour une sortie, expose le temps estimé uniquement si tu disposes d'une base fiable et présente-le comme une estimation. Distingue le temps déjà écoulé, l'étape actuelle et les conditions restantes. Si le système ne peut pas déterminer l'état parce que les RPC divergent, affiche « état en cours de vérification » plutôt que de déclarer la transaction réussie ou échouée sans preuve.

~~~mermaid
stateDiagram-v2
    [*] --> Preparee
    Preparee --> Signee
    Signee --> Envoyee
    Envoyee --> IncluseL2
    IncluseL2 --> LotL1
    LotL1 --> EtatAccepte
    Envoyee --> Inconnue: delai RPC
    Inconnue --> IncluseL2: reçu retrouvé
    IncluseL2 --> Reorganisee: bloc retiré
    Reorganisee --> Envoyee: rechercher à nouveau
    EtatAccepte --> [*]
~~~

Ce schéma n'est pas une machine universelle. Adapte-le aux états du protocole choisi et au niveau de confiance nécessaire à l'action métier. Le but est de montrer à l'utilisateur ce qui est connu, ce qui reste à faire et ce qui peut encore changer.

## 18. Modèle de coût et benchmark reproductible

Un benchmark utile mesure une opération représentative, et non la transaction la plus simple que l'explorateur permet d'envoyer. Pour une application DeFi, la séquence peut inclure une approbation de jeton, un dépôt, un échange, une attente de confirmation et un retrait. Pour un jeu, la transaction peut transporter un identifiant, un résultat signé et plusieurs paramètres. Les différences de taille des données et d'exécution influencent les coûts.

Établis un protocole de mesure avant de comparer les solutions. Fixe la version du contrat, les paramètres, le réseau, le portefeuille, la devise de calcul et la fenêtre temporelle. Répète les opérations à différentes périodes pour observer les variations. Archive les hashes et les reçus. Si tu utilises une transaction de test, indique clairement qu'elle ne représente pas nécessairement le coût d'une application de production.

Pour chaque opération, distingue les coûts sur L2, les frais de publication vers L1 lorsqu'ils sont exposés séparément, les frais de dépôt et de retrait, les frais du bridge et les coûts de conversion de l'actif. Ajoute la latence et les taux d'échec : un réseau dont le prix nominal est bas mais qui nécessite plusieurs reprises peut avoir un coût opérationnel élevé.

Le rapport doit aussi identifier les hypothèses non mesurées. Une période de faible congestion ne représente pas un pic de demande. Une simulation locale peut omettre des frais propres au réseau. Une estimation calculée avant inclusion peut différer du reçu. N'invente pas de chiffre de débit maximal à partir de quelques transactions observées ; rapporte la méthode et la portée de l'expérience.

### Fiche de mesure recommandée

| Champ | À enregistrer |
|---|---|
| Réseau et identifiant de chaîne | Nom vérifié et chain ID |
| Contrat et version | Adresse, code et configuration |
| Scénario métier | Suite exacte d'opérations mesurées |
| Horodatage | Début et fin de l'expérience |
| Gas et frais | Estimation, limite et reçu final |
| Publication L1 | Frais connus ou méthode d'estimation |
| Latence | Diffusion, inclusion et état requis |
| Échecs | Reverts, délais RPC, reprises et remplacements |
| Coûts de pont | Dépôt, route choisie, retrait et liquidité |
| Limites | Congestion non représentée ou étape non testée |

## 19. Gouvernance, maturité et hypothèses résiduelles

La maturité d'un rollup dépend de plusieurs dimensions : le contrôle des contrats, le degré d'automatisation du mécanisme de preuve, la disponibilité d'un chemin de sortie, la possibilité de mettre à niveau les composants, la diversité des opérateurs et la transparence des procédures de crise. Il n'existe pas une seule étiquette qui résume ces aspects.

Lorsque des contrats sont contrôlés par une multisignature, demande combien de signatures sont nécessaires, comment les signataires sont répartis, quels changements ils peuvent exécuter et si les utilisateurs disposent d'un délai pour réagir. Lorsque des mises à niveau sont possibles, vérifie si le changement est immédiat ou soumis à un délai, qui publie les informations de changement et si les utilisateurs peuvent sortir avant que le nouveau code devienne actif.

Les stades de décentralisation et les annonces de feuille de route sont des informations de contexte, pas des garanties opérationnelles. Pour un choix de production, vérifie les contrôles actifs aujourd'hui. Une capacité prévue dans une feuille de route ne doit pas être comptée comme une défense tant qu'elle n'existe pas sur le réseau.

Évalue également le coût de la migration. Si une application dépend d'un L2 spécifique, sa migration peut impliquer le déplacement des actifs, la réémission de jetons, la reconfiguration des oracles, la reconstruction d'indexeurs, les changements de chaîne dans les portefeuilles et le support aux utilisateurs. Documente un plan de sortie de fournisseur et la manière dont les données applicatives seront réconciliées après la migration.

## 20. Tester les pannes dans un environnement de laboratoire

Les tests de résilience doivent être contrôlés. Ne coupe pas un réseau public et ne manipule pas un contrat réel pour simuler une panne. Utilise une configuration de test qui permet de limiter l'impact et de revenir à l'état initial. Avant le test, relève la hauteur, les contrats actifs, la progression des lots, le statut du séquenceur et les ressources système.

Simule une perturbation à la fois : RPC indisponible, séquenceur de test arrêté, lot retardé, source de données indisponible ou interface qui ne reçoit plus les événements. Observe ce que l'application affiche, si les transactions peuvent être retrouvées et si elle évite les opérations dupliquées. Le test doit inclure le retour au fonctionnement normal, car certains défauts ne se manifestent qu'au moment de la réconciliation.

Définis un critère de réussite avant d'exécuter le test. Par exemple : l'interface ne présente pas une transaction incertaine comme finalisée, l'application ne répète pas le dépôt, une alerte est générée après un délai prévu, et le système retrouve l'état après restauration du service. Conserve les journaux et horodatages afin qu'un autre opérateur puisse reconstruire le déroulement.

Après chaque exercice, mets à jour le runbook : le signal initial, les commandes autorisées, la source de vérité, le propriétaire de l'incident, les conditions de reprise et les actions interdites. Un test de panne est utile s'il améliore à la fois l'architecture et la capacité d'exploitation.

## 21. Plan de reprise quand une route de sortie est dégradée

Le plan de reprise doit indiquer comment l'utilisateur identifie le mécanisme de sortie officiel, comment il vérifie son solde et quelles ressources on-chain sont requises pour exercer son droit de sortie. Une route de sortie peut demander des frais sur L1, une transaction depuis le compte propriétaire, une preuve d'inclusion ou une attente de protocole. Une procédure vague qui affirme que l'utilisateur peut « toujours sortir » n'est pas opérationnelle.

Documente les prérequis : accès au portefeuille, présence d'actif natif pour payer les frais, réseau correct, RPC fiable, contrat de sortie vérifié et données nécessaires à la construction de la transaction. Prévois une méthode permettant de vérifier l'état indépendamment de l'interface officielle, lorsque le protocole le rend possible. Ne demande jamais à l'utilisateur de communiquer une phrase de récupération au support.

Si la route de sortie est indisponible, définis quels services doivent être suspendus et quelles communications doivent être faites. Il est souvent plus sûr de bloquer une opération irréversible dont la sécurité est incertaine que de continuer à accepter des dépôts tout en ignorant une panne de sortie. La politique doit être proportionnée à la valeur exposée et au temps de rétablissement attendu.

Le plan de reprise se conclut par une réconciliation des comptes, des dépôts, des retraits et des messages en attente. Les métriques doivent revenir aux seuils définis, les transactions provisoires doivent atteindre l'état attendu et les écarts de solde doivent être expliqués. Si un risque résiduel demeure, le document doit le préciser au lieu de présenter une reprise partielle comme un retour complet à la normale.

## 22. Revue finale d'une architecture L2

Avant de choisir un réseau, l'équipe produit doit pouvoir répondre clairement à ces questions : quel mécanisme protège l'état, quelles données sont disponibles et pendant combien de temps, qui peut ordonner ou censurer les transactions, qui peut mettre à niveau les contrats, comment fonctionne la sortie canonique, quels frais sont ajoutés, et comment l'application gère les pannes et les réorganisations ?

La revue doit contenir les sources consultées, leurs dates, les versions de contrats et les inconnues. Un document qui ne distingue pas les faits des hypothèses peut donner une confiance excessive. Une note de décision devrait expliquer les critères éliminatoires, les compromis acceptés et le plan de migration si les conditions changent.

Il faut aussi vérifier les dépendances hors chaîne : indexeurs, services de prix, relayers, fournisseurs RPC, passerelles, gestion de clés et services d'observation. La sécurité de l'état n'assure pas automatiquement la disponibilité de toutes les fonctions de l'application. Le système peut continuer à respecter ses règles alors que l'interface est aveugle ou que le support ne peut pas aider l'utilisateur.

La décision finale doit appartenir au processus de gouvernance approprié et être revue lorsque le protocole change. Les faits mesurés, les liens, les tests et les seuils sont plus utiles qu'une note unique de « sécurité ». La qualité de la décision se juge à la clarté des hypothèses et à la possibilité de vérifier les garanties.

## 23. Vérifier le réseau et la configuration d'une DApp L2

Une erreur de configuration peut donner l'impression qu'un rollup est en panne alors que l'utilisateur consulte une autre chaîne, un RPC retardé ou un contrat différent. Avant une opération sensible, vérifie le chain ID attendu, le nom du réseau et les adresses des contrats. Le nom affiché par un portefeuille est une étiquette pratique, pas une preuve cryptographique d'identité. Le chain ID doit correspondre au réseau défini dans la configuration approuvée.

Conserve les adresses de pont, de token bridge, de contrat de règlement et de vérificateur depuis une source officielle. Lorsque la documentation fait référence à un dépôt de code, vérifie que le commit ou la version correspond à l'implémentation active. Un explorateur qui indique qu'un contrat est vérifié apporte une preuve utile sur le code source publié, mais il faut aussi examiner ses permissions et les capacités de mise à niveau. La vérification du source n'implique pas que le contrat soit sans risque.

Un service RPC peut renvoyer un résultat obsolète ou être configuré pour un autre réseau. Pour des opérations importantes, compare le hash du dernier bloc et l'identifiant de chaîne avec une deuxième source. Cette redondance doit être indépendante autant que possible. Deux URL peuvent aboutir au même fournisseur en amont et partager la même panne.

Une application devrait refuser de construire une transaction si la configuration n'a pas passé ses contrôles minimaux. Elle devrait aussi afficher clairement la chaîne utilisée avant la signature, car une transaction valide sur une mauvaise chaîne reste une erreur de l'utilisateur ou de la configuration. Les environnements de test et de production doivent être isolés afin qu'une adresse de test ne soit pas utilisée par défaut dans l'application publiée.

## 24. Définir les responsabilités de l'opérateur et du produit

La sécurité technique ne suffit pas si personne n'est responsable de la surveillance. Pour chaque composant — RPC, indexeur, séquenceur, bridge, service de prix, contrat de règlement — désigne un propriétaire, un niveau de service, une méthode d'alerte et une procédure de remplacement. Le propriétaire peut être une équipe interne ou un fournisseur externe, mais le produit doit savoir quelle action entreprendre quand ce composant ne respecte plus les objectifs.

Écris les conditions qui limitent les dépôts pendant une panne. Si le chemin de retrait est compromis ou indéterminé, continuer à accepter de nouveaux fonds peut augmenter l'exposition. À l'inverse, bloquer toutes les lectures parce qu'un fournisseur est lent peut dégrader inutilement le service. Une politique de dégradation doit distinguer lecture, dépôt, action réversible, retrait et opération irréversible.

La responsabilité comprend aussi la communication utilisateur. Si une transaction est en attente, l'interface doit expliquer si elle a été signée, diffusée ou incluse, et proposer une prochaine étape sûre. Le support ne doit jamais demander les secrets du portefeuille. Les messages publics doivent distinguer un problème confirmé d'une hypothèse en cours d'investigation.

Après un incident, réunis les preuves et mets à jour les procédures. Le rapport doit expliquer ce qui a échoué, quelles opérations ont été affectées, quels contrôles ont détecté le problème, combien de temps la reprise a duré et quelles modifications éviteront une répétition. Il est possible qu'un composant ait été conforme à ses garanties techniques mais insuffisant pour les exigences produit ; cette nuance doit être conservée dans l'analyse de cause.

## 25. Scénario de décision : rollup, sidechain ou architecture hybride

Un produit de paiement a besoin de faibles coûts, d'un règlement prévisible et de retraits compréhensibles. Une équipe propose un rollup, une sidechain et une solution hybride qui utilise un système de disponibilité de données externe. Pour comparer ces options, commence par décrire la conséquence d'une sortie bloquée, d'une transaction censurée, d'une perte de données ou d'un changement administratif inattendu.

Pour le rollup, vérifie les contrats L1, les mécanismes de preuve ou de contestation, la disponibilité des données, les permissions et la procédure de sortie forcée. Pour la sidechain, examine le consensus propre, la concentration des validateurs, les règles de finalité et la relation avec le bridge. Pour la solution hybride, identifie quels éléments sont vérifiés par L1 et quels éléments dépendent d'un fournisseur ou d'un comité hors chaîne.

Ensuite, mesure le coût du scénario métier complet sur les routes candidates, en incluant les approbations, les dépôts, les actions et les retraits. Note les coûts et délais à la date du test, sans extrapoler à toutes les conditions. Si une information de sécurité n'est pas publique, marque-la comme une inconnue et demande une preuve au fournisseur avant toute adoption à risque élevé.

La décision finale explique pourquoi certains compromis sont acceptés et quelles conditions déclencheraient une nouvelle évaluation. Elle peut par exemple exiger qu'une route de sortie soit prouvée sur un réseau de test, que l'adresse d'administration soit surveillée ou qu'un fournisseur soit remplacé si ses métriques dépassent un seuil. Le résultat attendu est une décision révisable et vérifiable.

## 26. Fiche d'évaluation de maturité

Utilise une grille pour éviter qu'un indicateur simple se substitue à l'analyse. Pour chaque domaine, attribue un statut : vérifié, partiellement vérifié, inconnu ou non applicable. Ajoute un lien de preuve et la date. Ne transforme pas une inconnue en note moyenne par défaut.

| Domaine | Vérification concrète | Statut à noter |
|---|---|---|
| Validité de l'état | Contrats et logique de validation identifiés | Vérifié / partiel / inconnu |
| Données | Méthode de publication et fenêtre de récupération documentées | Vérifié / partiel / inconnu |
| Censure | Chemin alternatif d'inclusion ou de sortie expliqué | Vérifié / partiel / inconnu |
| Gouvernance | Rôles, multisig, délais et mise à niveau inventoriés | Vérifié / partiel / inconnu |
| Sortie | Dépôt, retrait et recours d'urgence compris | Vérifié / partiel / inconnu |
| Exploitation | Alertes, propriétaires et runbooks testés | Vérifié / partiel / inconnu |
| Compatibilité | Compilateur, outils et dépendances testés | Vérifié / partiel / inconnu |
| Coût total | Opérations représentatives mesurées de manière répétable | Vérifié / partiel / inconnu |

La grille ne doit pas produire un score global sans pondération. Un risque de sortie peut être éliminatoire pour un service de conservation même si tous les autres domaines sont solides. Un coût élevé peut être acceptable pour une application à forte valeur si la sécurité répond au besoin. Documente ces priorités avec le propriétaire métier et le responsable technique.

## 27. Analyser une route de bridge avec une frontière de confiance explicite

Une route de dépôt et de retrait est une frontière de sécurité entre deux états. Avant toute opération, identifie qui reçoit le dépôt, quelle condition autorise l'émission ou le crédit sur la destination, quelle preuve est requise et qui peut interrompre le processus. Il faut également séparer le bridge canonique qui fait partie de l'architecture du rollup des services tiers qui avancent la liquidité en échange de frais.

Pour chaque étape, pose quatre questions : quelle donnée est fiable, comment est-elle vérifiée, quelle action peut-elle déclencher et qui peut la modifier ? Par exemple, un événement de dépôt peut être authentique mais encore trop récent pour la politique de finalité. Une preuve peut être valide mais liée à un contrat ou à une chaîne différente. Une adresse peut être correctement affichée dans l'interface mais ne pas correspondre au contrat documenté. Ces différences déterminent si l'opération doit continuer, attendre ou être rejetée.

Une intégration de bridge devrait vérifier le réseau avant de demander la signature, afficher l'actif attendu et calculer les montants dans les unités exactes. Lorsque la route crée une représentation enveloppée, l'interface doit distinguer la représentation de l'actif original. L'utilisateur doit connaître les frais, les délais et les risques supplémentaires. Une transaction réussie sur la chaîne source ne garantit pas que le crédit destination est déjà finalisé.

Les tests de bridge doivent contenir des scénarios d'échec. Simule une transaction source qui n'atteint pas l'état requis, une preuve qui vise la mauvaise chaîne, un paquet soumis deux fois, un délai dépassé et une panne du fournisseur. Chaque scénario doit préciser l'état des fonds, les messages de l'interface et la procédure de reprise. L'objectif est de rendre toute transition explicable même lorsque le chemin nominal n'aboutit pas.

## 28. Politique de confirmation en fonction du risque métier

La politique de confirmation devrait être choisie à partir de l'impact d'une erreur et du type de finalité offert par le protocole. Une lecture publique peut accepter un retard d'affichage et afficher un état provisoire. Une opération de dépôt peut rester en attente jusqu'à ce que le contrat L2 reconnaisse la transaction. Une action financière irréversible peut exiger un niveau de confirmation plus strict et une vérification indépendante.

La politique devrait préciser les états, les conditions de passage entre états, les sources de vérité, le comportement en cas de divergence et la manière de revenir d'un état provisoire. Elle ne doit pas se contenter d'un nombre fixe de confirmations sans expliquer pourquoi ce nombre est pertinent pour le réseau utilisé. La finale d'un protocole, les confirmations probabilistes et l'inclusion par un séquenceur représentent des garanties différentes.

Lorsque plusieurs fournisseurs RPC sont utilisés, compare les hashes à la hauteur pertinente plutôt que seulement leur nom de réseau. Si les réponses sont incohérentes, l'application devrait éviter les actions sensibles jusqu'à ce que la divergence soit comprise. Une réponse de RPC avec un code de succès est une réponse au niveau du transport ; ce n'est pas une preuve que les données conviennent à la décision métier.

Documente comment la politique évolue. Une modification du mécanisme de preuve, de la gouvernance, de la chaîne de base ou du bridge peut changer les délais et les hypothèses. Une application critique doit réexaminer la politique après une mise à niveau majeure ou un incident qui révèle qu'un seuil existant était trop permissif.

### Exemple de matrice métier

| Action | Coût d'une erreur | Politique possible |
|---|---|---|
| Afficher un solde provisoire | Faible si l'état est clairement étiqueté | Afficher avec la hauteur et le statut |
| Créditer une récompense réversible | Modéré | Attendre les confirmations définies et permettre la réconciliation |
| Accepter un dépôt de garantie important | Élevé | Vérifier l'état et la politique de finalité avant crédit définitif |
| Exécuter un retrait irréversible | Très élevé | Exiger les conditions de sécurité définies et une surveillance renforcée |

Ces exemples ne définissent pas une règle universelle. L'application doit adapter chaque action à sa valeur, à sa réversibilité et aux garanties réelles de la chaîne.

## 29. SLO, alertes et mesure de la résilience L2

Un objectif de niveau de service devrait décrire ce que l'utilisateur observe, par exemple la proportion de transactions qui atteignent l'état requis dans un délai défini. Mesure séparément la disponibilité du RPC, la latence du séquenceur, la progression des lots, les délais de publication sur L1, le taux de reverts et le temps de rétablissement. Agréger ces signaux sous une seule métrique de disponibilité masquerait la couche qui défaillit.

Les alertes doivent être basées sur une référence normale. Un séquenceur qui n'a pas inclus de transaction pendant une courte période peut être dans un intervalle attendu de faible activité ; un retard qui augmente continuellement est plus préoccupant. L'alerte doit indiquer le service propriétaire, le périmètre, les données de diagnostic et la procédure de premier niveau. Évite les seuils que personne ne peut expliquer ou qui déclenchent trop de faux positifs pour rester utiles.

La surveillance doit aussi inclure les dépendances du produit. Un L2 peut continuer à traiter les transactions alors qu'un indexeur ou un fournisseur de données externe est en retard. Une application peut alors afficher un état obsolète bien que la chaîne soit fonctionnelle. Compare les données indexées aux appels directs pour les opérations critiques, et conserve la hauteur de bloc de chaque réponse.

Lors d'un exercice de résilience, mesure le temps nécessaire pour identifier une panne, prendre une décision de sécurité, appliquer une solution et confirmer la reprise. Les mesures avant, pendant et après l'incident permettent de savoir si la procédure fonctionne ou si l'équipe a simplement observé un redémarrage spontané. Chaque exercice devrait produire une amélioration vérifiable : une nouvelle métrique, un message d'interface, une meilleure répartition des responsabilités ou une procédure de sortie plus claire.

## 30. Runbook de décision en cas de divergence entre observateurs

Lorsqu'un service RPC montre une hauteur différente d'un autre, ne choisis pas automatiquement la réponse la plus récente ni celle qui correspond à l'attente de l'interface. Commence par vérifier la chaîne, la méthode RPC appelée, la hauteur de référence et l'état de finalité. Certains endpoints peuvent être en retard ou utiliser un cache ; d'autres peuvent montrer une tête provisoire différente avant qu'une réorganisation soit résolue.

Collecte des éléments reproductibles : URL logique du fournisseur sans secret, horodatage UTC, chain ID, hauteur, hash de bloc, état du reçu, adresse appelée et code de retour. Compare les sources avec les mêmes paramètres. Lorsque la divergence touche une opération financière, suspends le traitement irréversible jusqu'à ce que les états attendus soient établis. Une alerte qui se déclenche pendant une variation normale ne doit pas autoriser à elle seule une modification de configuration.

Si la divergence persiste, identifie la couche affectée : RPC, indexeur, séquenceur, publication des lots ou règlement L1. Vérifie les changements récents et les journaux de déploiement. Évite de redémarrer en même temps tous les services, car cela peut effacer des indices et aggraver la capacité à diagnostiquer la cause. La procédure devrait avoir des commandes de lecture en premier, puis des actions de changement uniquement lorsqu'elles ont été approuvées.

La clôture exige davantage que deux hauteurs qui se ressemblent. Vérifie le hash de référence, le statut de la transaction, la progression des lots et la cohérence de l'état utilisé par le produit. Archive les observations avant et après l'incident et note si la cause est confirmée ou seulement probable. Si les sources se sont révélées dépendantes les unes des autres, corrige également l'architecture de surveillance.

## 31. Capacité de sortie et continuité pour les utilisateurs

Une conception responsable considère la sortie comme une fonction essentielle et non comme une page secondaire dans la documentation. Les utilisateurs doivent comprendre comment récupérer leurs fonds, quel réseau et quel portefeuille utiliser, quels frais sont nécessaires et quelles étapes peuvent prendre du temps. La procédure doit être accessible indépendamment du séquenceur lorsque le protocole promet un mécanisme de sortie indépendant.

Le scénario de continuité doit traiter l'absence d'un fournisseur RPC, la panne du séquenceur, la perte d'accès à une interface officielle, les frais L1 élevés et un état qui nécessite une preuve ou une donnée de récupération. Les consignes destinées aux utilisateurs ne doivent jamais demander une clé privée. Lorsque les opérations exigent des étapes avancées, la documentation doit les présenter à partir d'une source officielle vérifiée et préciser ce qui n'a pas été testé par l'équipe produit.

Pour un produit de conservation, considère le temps nécessaire pour qu'un grand nombre d'utilisateurs sorte en période de stress. Une option de sortie théoriquement disponible peut être difficile à exercer si le coût est trop élevé, si les contrats sont complexes ou si les données nécessaires ne sont pas accessibles. Évalue la capacité réelle du mécanisme dans les conditions de charge et documente les limites.

Le test final simule le scénario de perte de l'interface et exige que l'équipe trouve la documentation, identifie le mécanisme canonique, vérifie les contrats et explique les prérequis. Le résultat attendu n'est pas que tous les utilisateurs deviennent des ingénieurs de protocole ; c'est que la conception et le support ne cachent pas les dépendances importantes.

## 32. Questions d'entraînement avec corrigé

### Question 1 : Un rollup est-il simplement une chaîne plus rapide ?

**Correction :** Non. C'est une architecture qui exécute une partie du travail hors de la couche de base et qui s'appuie sur des mécanismes particuliers de publication, de règlement, de preuve ou de contestation. Une sidechain peut aussi être rapide sans partager les mêmes garanties.

### Question 2 : Une transaction montrée dans l'interface est-elle finalisée ?

**Correction :** Pas nécessairement. Il faut déterminer si elle est seulement acceptée par le séquenceur, incluse dans un bloc L2, publiée sur L1, acceptée par le mécanisme de preuve ou de contestation, ou finalisée selon la politique pertinente.

### Question 3 : Pourquoi les données doivent-elles être disponibles ?

**Correction :** Parce que les vérificateurs et utilisateurs peuvent avoir besoin de reconstruire l'état, contrôler une transition ou utiliser leur droit de sortie. Un engagement d'état ne fournit pas automatiquement les données manquantes.

### Question 4 : Un ZK-rollup rend-il toutes les transactions privées ?

**Correction :** Non. Une preuve de validité et la confidentialité sont deux propriétés différentes. Si les données et les adresses sont publiées, elles peuvent rester observables même si une preuve cryptographique est utilisée.

### Question 5 : Pourquoi un retrait canonique peut-il être plus lent qu'un transfert L2 ?

**Correction :** Parce que la sortie peut dépendre de la publication sur L1, de la finalité et, selon le système, d'une période de contestation. Les ponts de liquidité tiers peuvent accélérer l'expérience mais ajoutent des hypothèses de confiance.

### Question 6 : Une sidechain hérite-t-elle automatiquement du consensus Ethereum ?

**Correction :** Non. Elle dispose généralement de son propre consensus et de validateurs propres. Un pont entre les chaînes ne change pas cette propriété à lui seul.

### Question 7 : Quel est le rôle d'un séquenceur ?

**Correction :** Il reçoit, ordonne et traite souvent les transactions L2 avant publication. Son contrôle affecte la latence et potentiellement l'inclusion ; la sécurité doit inclure les mécanismes de repli et de sortie.

### Question 8 : Peut-on comparer les frais de deux réseaux à partir d'une seule transaction ?

**Correction :** Cette observation est insuffisante. Le coût varie selon les données, l'état, la congestion, la publication L1 et le trajet complet. Il faut un scénario métier comparable et des mesures répétées.

### Question 9 : Un audit prouve-t-il que le pont est sûr ?

**Correction :** Non. Il couvre un périmètre, une version et une période. Il faut vérifier les correctifs, les changements, les rôles d'administration, les dépendances et les tests postérieurs.

### Question 10 : Quelle preuve est la plus utile pour confirmer qu'un utilisateur peut sortir ?

**Correction :** La documentation du mécanisme canonique, ses contrats et ses conditions, complétés par une procédure vérifiée sur un environnement de test ou par des preuves d'exécution réelles. Un slogan de résilience ne suffit pas.

## 33. Challenge final : choisir une couche de mise à l'échelle

Une entreprise veut déployer un marché de jetons. Elle souhaite des coûts faibles, un accès rapide, des dépôts et retraits compréhensibles et un chemin de secours en cas de panne de l'opérateur. Trois offres commerciales promettent des coûts et débits attractifs, mais fournissent des informations inégales sur les preuves, les données, le pont et les pouvoirs d'administration.

### Travail demandé

Prépare un rapport de décision contenant le modèle de menace, les critères de sélection, la preuve demandée pour chaque critère, les coûts du cycle complet, la politique de confirmation, le plan de test et la procédure de reprise. Distingue impérativement les rollups des sidechains et des systèmes dont la disponibilité de données est externe à L1.

### Correction proposée

La décision doit commencer par les exigences de sécurité du marché et non par les chiffres publicitaires. Élimine toute option dont les hypothèses de sortie, de disponibilité des données ou de gouvernance ne répondent pas au modèle de risque. Pour les options restantes, teste le cycle dépôt-action-retrait sur un environnement approprié, mesure le coût total, vérifie les contrats officiels et documente les délais exacts.

La recommandation finale doit préciser les compromis acceptés, les risques inconnus, les métriques à surveiller et le responsable de la décision. Si une solution est retenue pour sa rapidité mais dépend d'un opérateur centralisé, cela doit être écrit en tant que risque accepté, avec des garde-fous et une stratégie de sortie. Le but est de choisir une architecture dont les garanties sont comprises, pas de promettre une solution sans risque.

## Glossaire

**Couche de base (L1)** : réseau qui assure les règles de consensus et le règlement sous-jacent.

**Layer 2 (L2)** : système qui traite des opérations sur une couche supérieure en utilisant des mécanismes spécifiques pour réduire certains coûts ou augmenter le débit.

**Rollup** : architecture qui exécute des transactions hors de L1 puis publie des données et des engagements selon un protocole de règlement.

**Séquenceur** : composant qui reçoit et ordonne généralement les transactions L2.

**Preuve de fraude** : preuve utilisée dans certains systèmes optimistes pour contester une transition invalide.

**Preuve de validité** : preuve cryptographique que la transition respecte les règles représentées par le vérificateur.

**Disponibilité des données** : capacité à obtenir les informations nécessaires pour vérifier ou reconstruire l'état.

**Sidechain** : chaîne indépendante avec son propre mécanisme de consensus.

**Validium** : système utilisant des preuves de validité tout en reposant sur un modèle distinct de disponibilité des données.

**Pont canonique** : mécanisme de transfert ou de sortie fourni par l'architecture du réseau et défini par sa documentation.

**Séquenceur centralisé** : séquenceur placé sous le contrôle d'une seule autorité ou d'un ensemble très restreint.

**Finalité** : niveau auquel une opération est considérée comme irréversible selon les règles et hypothèses du système.

## Pour aller plus loin

- Ethereum.org, mise à l'échelle : https://ethereum.org/en/developers/docs/scaling/
- Ethereum.org, rollups optimistes : https://ethereum.org/en/developers/docs/scaling/optimistic-rollups/
- Ethereum.org, rollups à preuves de validité : https://ethereum.org/en/developers/docs/scaling/zk-rollups/
- Ethereum.org, disponibilité des données : https://ethereum.org/en/developers/docs/data-availability/
- Ethereum.org, ponts : https://ethereum.org/en/developers/docs/bridges/

La documentation évolue avec les mises à niveau des protocoles. Pour une décision de production, vérifie la version actuelle des contrats, la documentation du réseau, les rapports de sécurité et les paramètres de sortie plutôt que de réutiliser une valeur de délai ou de frais issue d'un exemple pédagogique.
