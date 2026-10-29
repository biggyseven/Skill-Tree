# EVM et gas

## Encadré de mise en contexte

La machine virtuelle Ethereum, ou EVM, est l'environnement d'exécution qui permet aux nœuds compatibles de traiter les smart contracts selon des règles communes. Le code source Solidity est compilé en bytecode ; ce bytecode est exécuté dans un contexte précis par les clients qui valident les transactions. Pour qu'un réseau distribué obtienne le même résultat, les opérations doivent être définies de manière déterministe : les nœuds conformes qui partent du même état et appliquent les mêmes transactions valides doivent calculer le même nouvel état.

Le **gas** est l'unité utilisée pour mesurer le coût en ressources des opérations exécutées dans l'EVM. Il contribue à limiter les calculs, à empêcher qu'une transaction boucle indéfiniment et à faire payer les ressources mobilisées. Il ne correspond ni directement au temps CPU ni au nombre de watts consommés. Une transaction peut échouer tout en consommant du gas, parce que le réseau a tout de même effectué le travail nécessaire avant de revenir à l'état antérieur.

Cette leçon relie les concepts de Solidity à l'exécution réelle. Elle explique la pile, la mémoire, le stockage, le bytecode, les appels entre contrats, les limites de gas, le marché des frais, les estimations, les erreurs fréquentes et les stratégies d'optimisation. Elle prépare au développement de DApps qui doivent afficher les coûts de manière compréhensible et éviter les opérations qui deviennent trop chères.

## Objectifs d'apprentissage

À la fin de ce cours, tu sauras :

- décrire le rôle de l'EVM dans l'exécution des contrats ;
- expliquer la différence entre code source, bytecode, état et transaction ;
- identifier la pile, la mémoire, le stockage et les données de calldata ;
- distinguer gas, limite de gas, prix du gas et frais totaux ;
- calculer un coût simplifié et interpréter les paramètres d'une transaction ;
- comprendre la base fee, le priority fee et max fee après le mécanisme EIP-1559 ;
- différencier un échec avant inclusion d'un revert pendant l'exécution ;
- analyser l'effet des lectures et écritures de stockage sur le coût ;
- comprendre le rôle des appels externes, du contexte d'exécution et de la consommation imbriquée ;
- améliorer du code sans compromettre la sécurité ni rendre les tests insuffisants.

## 1. Le rôle de l'EVM

L'EVM est une machine virtuelle spécifiée par le protocole Ethereum. Elle décrit comment exécuter le bytecode des contrats et comment cette exécution interagit avec l'état. Elle n'est pas une machine physique qui tourne sur un serveur unique ; chaque client compatible implémente les règles nécessaires pour exécuter les transactions et calculer le résultat.

On peut comparer une machine virtuelle à un ordinateur abstrait qui possède un ensemble d'instructions, une pile de valeurs, des règles de mémoire, un état persistant et une comptabilité des ressources. Le détail est important : si les clients interprétaient le même bytecode de manières incompatibles, ils pourraient obtenir des états différents et le consensus serait menacé.

~~~mermaid
flowchart TD
    S["Code source Solidity"] --> C["Compilateur"]
    C --> B["Bytecode EVM"]
    B --> D["Contrat déployé"]
    T["Transaction"] --> X["Contexte d'exécution EVM"]
    D --> X
    X --> G["Comptabilité du gas"]
    X --> R["Résultat et nouvel état"]
    R --> N["Validation par les nœuds"]
~~~

### 1.1 Déterminisme

Une même exécution doit produire le même résultat lorsqu'on utilise le même état initial, les mêmes données d'entrée, le même contexte et les mêmes règles de protocole. Le contrat ne doit pas appeler librement un site web ou lire l'horloge physique locale de chaque nœud, car les réponses pourraient diverger.

L'environnement fournit toutefois certaines informations de bloc et de transaction, comme le numéro de bloc, l'horodatage ou l'appelant. Ces valeurs sont soumises aux règles du protocole. Elles ne doivent pas être utilisées comme s'il s'agissait de mesures physiques parfaites ou d'une source de hasard inviolable.

### 1.2 Ce que l'EVM ne fait pas

L'EVM n'est pas une interface graphique, un portefeuille, un explorateur ou une base de données hors chaîne. Elle n'héberge pas les pages web d'une application. Une DApp comprend souvent plusieurs couches : interface, portefeuille, fournisseur RPC, réseau P2P, consensus, exécution EVM, contrats et parfois indexeurs ou oracles.

Une transaction acceptée par l'EVM n'assure pas que l'interface web est correcte ni que l'utilisateur a compris ce qu'il a signé. Inversement, une panne de fournisseur RPC ou d'interface peut empêcher un utilisateur d'interagir alors que les contrats continuent d'exister sur la blockchain.

## 2. Du code source au bytecode

Solidity est un langage source lisible par les développeurs. Le compilateur le transforme en bytecode que l'EVM peut exécuter. Le compilateur peut également produire une ABI, des métadonnées et des informations utiles au débogage. Les paramètres de compilation, les versions de dépendances et les options d'optimisation influencent le résultat.

La chaîne de transformation comporte généralement :

1. le code source et ses imports ;
2. la compilation avec une version déterminée ;
3. le bytecode de création utilisé lors du déploiement ;
4. l'exécution du code de création, qui initialise éventuellement le contrat ;
5. le bytecode d'exécution enregistré à l'adresse du contrat ;
6. les transactions qui appellent ce bytecode et modifient l'état selon ses règles.

Il faut distinguer le bytecode de création du bytecode d'exécution. Le code de création s'exécute lors du déploiement et retourne généralement le code qui sera conservé. L'initialisation peut utiliser des arguments de constructeur. Lorsqu'un développeur compare une source à un contrat déployé, il doit tenir compte des paramètres et de la méthode de compilation.

### 2.1 ABI et sélecteurs de fonction

L'ABI décrit comment encoder les appels de fonction et comment décoder les résultats ou les événements. Un appel comprend souvent un sélecteur de quatre octets, dérivé du hachage de la signature canonique de la fonction, suivi des arguments encodés. La représentation exacte dépend du type et de l'ordre des paramètres.

L'ABI ne constitue pas une preuve de confiance. Un site peut présenter une ABI et une adresse qui ne correspondent pas au contrat attendu. Vérifie le réseau, l'adresse et si possible la source vérifiée et le bytecode. Un nom de fonction familier peut être réutilisé par un contrat malveillant.

### 2.2 Déploiement et coût

Le déploiement consomme du gas : le réseau exécute le code de création, vérifie les contraintes et enregistre le code et l'état initial nécessaires. Les contrats volumineux peuvent coûter davantage à déployer et sont soumis à des limites de taille. Les constructions complexes ou les chaînes d'initialisation longues peuvent aussi accroître le coût.

La compilation réussie ne garantit ni la sécurité ni le coût acceptable. Avant un déploiement public, il faut compiler avec les paramètres de production, tester sur un réseau local ou de test, vérifier les hypothèses d'exécution et préparer une procédure d'exploitation.

## 3. Les zones de données de l'EVM

Les coûts et les durées d'accès diffèrent selon la zone de données. Il ne faut pas les confondre, même si certains langages utilisent des syntaxes proches.

### 3.1 Pile

La pile est une structure de données de travail utilisée par les instructions EVM. Les instructions prennent des valeurs au sommet de la pile et y placent généralement leurs résultats. Les opérations de calcul élémentaires utilisent souvent la pile.

La pile est de taille limitée par la spécification. Le compilateur Solidity organise le code pour utiliser cette machine abstraite. Si un développeur manipule directement du bytecode ou de l'assembleur, il doit comprendre précisément l'ordre des opérandes et les règles de l'instruction. La pile n'est pas l'endroit où un contrat stocke durablement ses variables.

### 3.2 Mémoire

La mémoire EVM est une zone temporaire pour une exécution. Elle peut contenir des arguments encodés, des données copiées, des buffers de calcul et des valeurs temporaires. Elle n'est pas conservée comme état persistant après la transaction.

L'utilisation de mémoire peut augmenter le coût, notamment lorsque la zone active s'étend. Le coût est lié à la taille de mémoire utilisée et à sa croissance, pas seulement au nombre d'affectations dans le code source. Les développeurs doivent donc éviter de copier inutilement de grandes données, tout en gardant la lisibilité.

### 3.3 Calldata

Calldata est la zone des données d'appel, en lecture seule pour les usages habituels. Les paramètres d'une fonction externe y sont encodés. En Solidity, utiliser calldata pour des données dynamiques que l'on ne souhaite pas modifier peut éviter certaines copies par rapport à memory, selon la structure du code et les optimisations du compilateur.

Calldata n'est pas un stockage durable. Si le contrat doit conserver une chaîne ou un tableau après la fin de l'exécution, il doit la copier dans l'état ou la traiter autrement. Cette copie peut avoir un coût de gas, qui doit être considéré dans la conception.

### 3.4 Stockage

Le stockage est l'état persistant du contrat. Les variables d'état, mappings et tableaux persistants sont représentés dans l'état de la blockchain. Lire ou modifier le stockage peut être significativement plus coûteux que calculer avec une valeur locale, car ces opérations affectent l'état commun que les nœuds doivent suivre.

Le coût exact dépend des règles de gas et du contexte : une lecture peut être plus ou moins coûteuse selon qu'une donnée a déjà été consultée pendant l'exécution, et une écriture peut coûter différemment selon l'état précédent et la nature du changement. Les chiffres précis évoluent avec les mises à jour du protocole ; il faut donc consulter une référence actuelle plutôt que mémoriser un tableau éternel de coûts.

~~~mermaid
flowchart TD
    C["Calldata : arguments de l'appel"] --> M["Mémoire : données temporaires"]
    M --> S["Stockage : état persistant"]
    P["Pile : calculs et opérations"] <--> M
    P <--> S
    P <--> C
~~~

### 3.5 Variables locales et structures complexes

Une variable locale simple peut rester dans la pile ou être organisée autrement par le compilateur. Les structures dynamiques peuvent nécessiter de la mémoire ou du stockage. Le choix de l'emplacement ne doit pas être dicté seulement par la recherche du gas le plus faible : il doit d'abord respecter la logique et le modèle de vie des données.

Un tableau persistant que l'utilisateur peut agrandir sans limite peut devenir difficile à parcourir dans une seule transaction. Si une fonction doit analyser des milliers d'entrées, il peut être préférable d'utiliser une pagination, une structure indexée ou un traitement hors chaîne appuyé sur des preuves appropriées, plutôt que de tout parcourir à chaque appel.

## 4. Qu'est-ce que le gas ?

Le gas mesure la quantité de ressources facturée pour l'exécution des opérations. Chaque transaction consomme un certain nombre d'unités selon les instructions exécutées et les autres règles du protocole. Le gas sert à limiter les calculs et à répartir le coût des ressources entre les utilisateurs.

Le gas consommé et le prix du gas sont deux choses distinctes. La consommation dépend du chemin d'exécution et des règles du protocole. Le prix par unité dépend du mécanisme de frais et des conditions du réseau. Une fonction qui consomme 100 000 unités de gas peut coûter très peu lorsque le prix par unité est faible ou davantage lorsque la demande et les frais augmentent.

### 4.1 Gas limit et gas used

Le gas limit associé à la transaction détermine le maximum que l'expéditeur autorise pour l'exécution, sous réserve des règles de transaction et du bloc. Le gas used est le montant effectivement consommé. Une limite trop basse peut empêcher l'exécution ou provoquer un épuisement de gas selon le point où l'échec survient.

Prenons un exemple simplifié. Supposons qu'une transaction consomme 72 000 unités et que la limite fournie soit de 100 000. Le coût final se calcule sur les unités facturées, et non automatiquement sur la totalité de la limite. Le traitement des frais et de la limite dépend toutefois du type de transaction, du prix effectif et des règles exactes de la version du protocole.

### 4.2 Pourquoi faire payer les calculs ?

Sans coût de calcul, un participant pourrait demander à un nœud d'exécuter une tâche très lourde ou une boucle infinie et l'empêcher de traiter d'autres transactions. Le gas associe une limite et un coût économique à l'exécution. Si une transaction s'épuise en gas, les changements d'état de cette exécution sont annulés, mais les ressources consommées doivent tout de même être payées selon les règles.

Les frais découragent aussi certaines formes de spam. Ils ne suppriment pas toutes les attaques, car un acteur peut avoir des ressources importantes ou exploiter des coûts insuffisamment calibrés. Le protocole et les clients doivent combiner comptabilité de gas, limites de bloc, politiques de relais et protections opérationnelles.

### 4.3 Gas n'est pas du temps CPU

Un développeur ne doit pas supposer qu'une opération qui utilise deux fois plus de gas prend exactement deux fois plus de temps sur une machine. Le gas est une comptabilité normative du protocole, tandis que les temps d'exécution physiques dépendent du matériel, du client et de l'environnement. Les clients doivent calculer le même état, mais leurs performances locales peuvent différer.

Le gas ne se convertit pas non plus directement en watts-heures. Le coût énergétique dépend des ressources physiques mobilisées par les opérateurs et du mécanisme de consensus global. Le gas sert surtout à mesurer l'exécution et à établir les frais sur les réseaux EVM.

## 5. Calcul du coût d'une transaction

Le modèle général est :

**Frais effectifs = gas utilisé × prix effectif par unité de gas.**

Le prix effectif est déterminé par les règles de transaction. Depuis EIP-1559, les transactions de type courant peuvent spécifier une base de frais maximale par unité et un pourboire maximal. La base fee du bloc est déterminée par le mécanisme du protocole et est brûlée ; le pourboire vise à rémunérer le producteur de bloc et peut influencer la priorité relative.

Les paramètres courants sont :

- **base fee** : composant par unité de gas défini par le protocole pour le bloc ;
- **maxPriorityFeePerGas** : maximum que l'expéditeur souhaite offrir comme priorité ;
- **maxFeePerGas** : plafond total par unité que l'expéditeur accepte de payer ;
- **gas limit** : maximum d'unités de gas alloué à la transaction ;
- **gas used** : unités effectivement facturées pour l'opération.

En simplifiant, le prix effectif est limité par le plafond de l'expéditeur et dépend de la base fee et du pourboire applicable. Il faut consulter les spécifications actuelles pour traiter exactement les transactions de type différent et les cas particuliers.

### 5.1 Exemple numérique

Imaginons, uniquement pour l'exercice, une transaction qui utilise 80 000 unités de gas. Supposons que le prix effectif final soit 30 gwei par unité. Le coût en ETH est 80 000 multiplié par 30 gwei, soit 2 400 000 gwei, ce qui équivaut à 0,0024 ETH puisque un ETH vaut un milliard de gwei.

Si le prix effectif était de 10 gwei avec la même consommation, le coût serait de 0,0008 ETH. La consommation n'a pas changé, mais le prix du marché a changé. Si une transaction exécute davantage d'opérations et consomme 160 000 unités au même prix de 30 gwei, son coût serait de 0,0048 ETH.

Ces valeurs sont illustratives, et non une estimation actuelle des frais. Le prix réel varie selon le réseau, le moment, la demande et le type de transaction.

### 5.2 Conversion des unités

L'ether se divise en wei, et un gwei correspond à un milliard de wei. Les interfaces doivent éviter les arrondis décimaux ambigus. Les bibliothèques d'application utilisent souvent des représentations entières ou des types décimaux sûrs pour effectuer ces conversions, plutôt que les flottants binaires classiques qui peuvent introduire des erreurs d'arrondi.

Quand tu présentes un coût à l'utilisateur, indique les unités et la base du calcul. Le gas limit n'est pas le coût final. Le coût final dépend du gas utilisé et du prix effectif par unité ; si la transaction n'est pas exécutée, les règles applicables déterminent si et quels frais sont consommés.

## 6. Base fee, priorité et EIP-1559

EIP-1559 a introduit un mécanisme de marché des frais avec une base fee ajustée selon l'utilisation récente des blocs et un composant de priorité. Le mécanisme cherche à rendre les estimations de frais plus prévisibles et à ajuster le prix de base selon la demande. Il ne garantit pas des frais bas lorsque le réseau est très demandé.

La base fee augmente lorsque le bloc précédent dépasse sa cible d'utilisation et diminue lorsque l'utilisation est sous la cible, selon la formule du protocole. Les producteurs ou validateurs peuvent recevoir le composant de priorité, alors que la base fee est brûlée. L'expéditeur fixe des limites pour ne pas accepter un prix illimité.

### 6.1 Max fee et estimation du portefeuille

Un portefeuille peut estimer la base fee probable des blocs à venir, choisir un pourboire selon la priorité souhaitée et fixer un plafond de prix. La différence entre le plafond et le prix effectif n'est pas nécessairement facturée. Le portefeuille doit toutefois tenir compte d'un changement de demande entre l'estimation et l'inclusion.

Une estimation est un conseil, pas une garantie de délai. Des transactions mieux rémunérées peuvent être sélectionnées avant d'autres, mais la politique du producteur, le type d'opération, la congestion et le comportement du réseau influencent également l'inclusion. Une interface responsable explique le prix estimé, le plafond de l'utilisateur et la possibilité qu'une transaction reste en attente.

### 6.2 Frais et congestion

Lorsque beaucoup d'utilisateurs veulent inscrire des opérations dans la chaîne, les producteurs doivent choisir parmi une demande qui dépasse les ressources disponibles. Les utilisateurs peuvent augmenter leur pourboire pour attirer l'attention, ou patienter. Des transactions complexes consomment plus de gas et peuvent occuper davantage de capacité.

Les frais ne dépendent pas directement du montant envoyé. Une transaction qui envoie 0,01 ETH peut utiliser une quantité de gas similaire à une transaction qui envoie 100 ETH si toutes deux sont des transferts simples avec les mêmes conditions. En revanche, un appel de contrat complexe peut consommer beaucoup plus de gas, même si la valeur transférée est faible.

### 6.3 Réseaux de couche 2

Les réseaux de couche 2 peuvent exécuter les opérations selon leurs propres mécanismes et publier périodiquement des données ou preuves sur Ethereum. Les frais facturés à l'utilisateur peuvent inclure le coût de l'exécution de couche 2 et une part des coûts de données ou de règlement sur la couche de base. Il faut consulter la documentation du réseau concerné : le gas EVM principal n'explique pas à lui seul tous les frais d'un rollup.

## 7. Transactions échouées et consommation

Il faut distinguer au moins trois situations :

1. la transaction est rejetée avant d'être incluse, par exemple en raison d'un format invalide ou d'un problème de validation ;
2. la transaction est incluse, mais l'exécution du contrat renvoie une erreur ou un revert ;
3. l'exécution épuise le gas alloué et s'arrête.

Dans le premier cas, elle peut être rejetée avant inclusion et ne consomme alors pas de gas d'exécution au sens d'une transaction confirmée, même si le portefeuille ou le service a utilisé des ressources pour la simuler. Dans les cas d'échec après inclusion, du gas a été utilisé et les frais correspondants sont généralement facturés. Il faut respecter les différences exactes du protocole et du type de transaction.

Lorsqu'une transaction revert, les changements d'état de cette exécution sont annulés, mais les frais correspondant au travail fourni sont payés selon les règles. Le reçu est utile pour déterminer le résultat. Une interface ne doit pas interpréter le fait qu'une transaction a été incluse comme preuve que l'action métier a réussi.

### 7.1 Pourquoi une transaction peut échouer

Les causes possibles incluent un contrôle require non satisfait, un solde insuffisant, une permission manquante, une condition d'état devenue fausse entre estimation et inclusion, un appel externe qui échoue, une limite de gas trop basse ou une erreur dans le contrat. Certaines erreurs proviennent de l'utilisateur, d'autres du code ou du contexte du réseau.

Pour diagnostiquer, recueille le hash de transaction, le réseau, le reçu, le statut d'exécution, le gas utilisé, les données de l'appel et, si disponibles, la trace d'exécution et les données d'erreur. N'essaie pas de déduire la cause uniquement à partir d'un message générique tel que « transaction failed ».

## 8. Coût de l'état et optimisation du gas

Les opérations sur l'état persistant sont souvent une source importante de coût. Une fonction qui écrit plusieurs champs dans le stockage peut être plus chère qu'un calcul local. Les changements de valeur, les accès répétés, les structures de données et les conditions de cache sont soumis aux règles de gas actuelles et ont évolué au fil des mises à jour.

L'optimisation commence par une mesure reproductible. Compile avec les mêmes options que le projet, exécute des tests représentatifs et mesure le gas pour les différents chemins. Un unique test avec une petite donnée peut masquer une croissance non linéaire. Les tableaux, boucles, concaténations de chaînes et appels externes doivent être testés avec des entrées réalistes et extrêmes.

### 8.1 Réduire les écritures inutiles

Si la logique exige seulement de calculer une valeur temporaire, la stocker durablement peut être inutile. Les contrats peuvent souvent calculer à partir de l'état actuel, effectuer une vérification, puis écrire le minimum de données nécessaires. Mais le code doit conserver les invariants : réduire les écritures ne doit jamais autoriser un utilisateur à contourner les règles ou entraîner une perte d'information essentielle.

### 8.2 Regrouper des opérations

Une application peut parfois regrouper plusieurs actions en une transaction au lieu d'envoyer plusieurs transactions distinctes. Cela peut réduire les coûts fixes ou améliorer l'expérience, mais peut accroître la complexité et le coût maximal d'une seule transaction. Si le regroupement échoue à mi-chemin, il faut comprendre les règles d'atomicité et le comportement des appels.

### 8.3 Événements et indexeurs

Émettre un événement est souvent utile pour permettre aux applications d'indexer des changements sans stocker un historique redondant dans le contrat. Les événements ne sont toutefois pas lisibles arbitrairement par le code EVM comme s'il s'agissait de stockage. Si le contrat doit utiliser une valeur dans une décision future, elle doit être conservée ou reconstruite avec un mécanisme adapté.

L'architecture peut déplacer certaines tâches vers un indexeur hors chaîne. Cela réduit parfois le coût on-chain, mais ajoute une dépendance et demande de gérer la cohérence, les réorganisations et la disponibilité. Une optimisation doit donc être évaluée à l'échelle de l'application, pas seulement du bytecode.

### 8.4 Ne pas sacrifier la sécurité

Les raccourcis dangereux comprennent la suppression d'un contrôle d'accès pour économiser du gas, la réutilisation de variables avec un état difficile à comprendre, l'utilisation d'assembleur sans tests et la réduction excessive des vérifications. Le gas est important, mais une économie minime n'est pas pertinente si elle augmente le risque de perte d'actifs.

Privilégie une architecture lisible, des bibliothèques reconnues et des mesures qui identifient les vrais postes de coût. Les optimisations doivent être couvertes par des tests de régression qui vérifient que le comportement reste conforme.

## 9. Appels entre contrats et contexte d'exécution

Lorsqu'un contrat appelle un autre contrat, l'EVM crée un nouveau contexte d'exécution lié à l'appel. Le contrat appelé consomme des ressources, peut lire ou modifier l'état auquel il a accès et peut rappeler d'autres contrats. Le coût total dépend du chemin complet, pas seulement de la première fonction appelée.

Il faut distinguer les appels qui transmettent un appel classique et ceux qui exécutent du code dans le contexte de stockage d'un autre contrat, comme certaines utilisations de DELEGATECALL. Ce dernier mécanisme est puissant et peut être dangereux : le code appelé agit sur le stockage du contrat appelant. Les architectures de proxy l'utilisent pour les mises à niveau, mais une mauvaise configuration peut compromettre tout l'état.

### 9.1 Atomicité et appels échoués

Une transaction EVM est généralement atomique au niveau de l'état : si une exécution revert, les modifications d'état associées à cette exécution sont annulées selon les règles de l'EVM. Mais les événements et transferts suivent aussi des règles de retour arrière qui doivent être comprises. L'utilisateur peut tout de même payer du gas pour le travail effectué.

Un contrat peut capturer l'échec d'un appel externe et continuer, ou propager l'erreur et annuler l'opération. Le choix affecte l'intégrité métier. Il faut tester les deux comportements et ne pas supposer que tout appel externe réussit.

### 9.2 Appels et réentrance

Un appel externe donne le contrôle au code appelé. Si ce code peut rappeler le contrat initial avant que son état soit correctement mis à jour, une réentrance est possible. Les développeurs doivent examiner les chemins imbriqués et l'ordre des opérations. La logique « vérifier, mettre à jour l'état, interagir ensuite » est une règle de conception utile, mais doit être combinée avec des tests et une compréhension des callbacks.

## 10. Environnement et outils de diagnostic

Pour étudier le gas, utilise un environnement de développement qui fournit les mesures des transactions de test et les traces d'exécution. Les outils courants affichent le gas estimé, le gas utilisé, les frais et les appels internes. Ces éléments servent à diagnostiquer une fonction coûteuse et à comprendre où le travail se produit.

Une trace donne le déroulement de l'exécution selon l'outil, mais n'est pas automatiquement une preuve cryptographique publique. Elle dépend du nœud, des données et de la disponibilité des traces. Pour une investigation fiable, conserve le réseau, la version du client, le hash de transaction, le bloc, le reçu et l'outil utilisé.

Les mesures doivent être reproductibles. Note la version du compilateur, les options d'optimisation, la taille des entrées, l'état initial et le chemin d'exécution. Sans cette information, comparer deux chiffres de gas peut être trompeur.

## 11. Cycle d'exécution d'une transaction EVM

Une transaction ne se résume pas à l'appel d'une fonction Solidity. Le nœud vérifie d'abord la structure et les conditions liées au compte et aux frais, puis la transaction est incluse dans un bloc. Les clients appliquent les opérations dans l'ordre prévu par le protocole, exécutent le bytecode, calculent la consommation de gas et déterminent le nouvel état et le reçu.

~~~mermaid
sequenceDiagram
    participant U as Portefeuille
    participant N as Nœud
    participant B as Bloc
    participant E as EVM
    participant S as État
    U->>N: Transaction signée
    N->>N: Validation préliminaire
    N->>B: Inclusion si sélectionnée
    B->>E: Exécuter le bytecode
    E->>E: Compter le gas
    E->>S: Appliquer les changements si succès
    E-->>N: Reçu et statut
~~~

Cette séquence contient des étapes avec des garanties différentes. Une simulation locale peut aider à détecter un revert, mais l'état peut changer avant l'inclusion. Un hash de transaction identifie l'opération diffusée, mais n'atteste pas son succès. Le reçu indique le résultat de l'exécution incluse, et une application critique doit encore décider quel statut de confirmation ou de finalité elle exige.

### Contexte d'exécution et données visibles

L'EVM reçoit des données de contexte comme l'adresse du contrat, l'appelant immédiat, la valeur transférée, le gas disponible, les données de calldata et les informations de bloc autorisées par le protocole. Les valeurs de bloc ne doivent pas être traitées comme des vérités physiques parfaites. Leur usage doit être évalué selon le modèle de menace.

Lors d'un appel imbriqué, la sémantique dépend de l'instruction employée. Un appel classique exécute du code dans le contexte du contrat appelé. Certaines formes d'appel, notamment DELEGATECALL, exécutent le code d'un autre emplacement en conservant le contexte de stockage et l'identité d'appel pertinents du contrat appelant. C'est une base technique de certaines architectures de proxy, mais une mauvaise configuration peut donner au code appelé le pouvoir de modifier le stockage du contrat principal.

## 12. Pourquoi les opérations de stockage coûtent cher

L'état persistant fait partie du registre partagé que les nœuds doivent maintenir. Une écriture dans le stockage a donc un coût défini par les règles de gas. Le coût dépend du type de changement, de la valeur précédente, des accès effectués dans le contexte de la transaction et des mises à jour du protocole. Il est incorrect d'apprendre une seule valeur de gas et de l'appliquer à tous les contrats sans connaître les conditions.

Les variables temporaires permettent souvent d'effectuer des calculs sans écrire chaque résultat. Mais une variable de stockage est nécessaire si le résultat doit survivre à la fin de la transaction et être consultable lors d'un appel ultérieur. Le concepteur doit distinguer les données persistantes qui font partie de la logique métier des données qui peuvent être recomputées ou indexées hors chaîne.

~~~mermaid
flowchart TD
    A["Entrées d'appel"] --> M["Calcul temporaire en mémoire/pile"]
    M --> Q{"La donnée doit-elle survivre ?"}
    Q -->|Non| R["Retourner résultat ou émettre trace"]
    Q -->|Oui| S["Écrire dans le stockage"]
    S --> C["État partagé mis à jour"]
~~~

### Croissance et complexité

Une fonction qui traite un seul élément peut coûter peu et devenir inutilisable lorsqu'elle parcourt un tableau de milliers d'éléments. Il faut mesurer le coût pour différentes tailles et déterminer si la complexité est linéaire, quadratique ou liée à d'autres données. Les boucles sur une collection contrôlée par des utilisateurs méritent une attention particulière.

Les alternatives comprennent la pagination pour les lectures, les opérations par lots à taille limitée, un indexeur hors chaîne pour les recherches, ou des structures cryptographiques d'engagement lorsque l'application peut vérifier une preuve au lieu de parcourir toutes les données on-chain. Ces solutions échangent la simplicité contre des hypothèses et des composants additionnels ; elles ne doivent pas être choisies uniquement pour réduire le gas apparent.

### Stockage chaud et froid

Les règles de gas tiennent compte du contexte d'accès aux emplacements de stockage. Des accès répétés à un même emplacement au cours d'une transaction peuvent ne pas coûter comme le premier accès. Les mises à jour du protocole ont modifié les coûts et les hypothèses au fil du temps. Le code qui dépend de détails très précis doit donc être mesuré avec une version de client et un réseau de test représentatifs, puis réévalué lorsqu'un fork change les règles.

Il ne faut pas coder des hypothèses de rentabilité fondées sur une situation de cache accidentelle. Si une optimisation dépend du fait qu'une clé de stockage a déjà été lue, cette hypothèse doit être comprise, mesurée et comparée au comportement dans les chemins alternatifs.

## 13. Frais : du gas brut au montant facturé

Pour une transaction courante après EIP-1559, le montant effectif dépend du gas consommé, de la base fee du bloc et du pourboire réellement applicable, sous les plafonds spécifiés par l'expéditeur. La règle de base est d'expliquer le calcul en unités cohérentes : gas used multiplié par le prix effectif par unité donne le coût en wei. La conversion vers ETH utilise le rapport défini entre wei et ETH.

~~~mermaid
flowchart LR
    G["Gas utilisé"] --> M["Multiplier par le prix effectif"]
    B["Base fee du bloc"] --> P["Calcul du prix effectif"]
    T["Priority fee proposé"] --> P
    F["Max fee : plafond utilisateur"] --> P
    P --> M
    M --> W["Coût en wei"]
    W --> E["Conversion en ETH pour affichage"]
~~~

La base fee est déterminée par le mécanisme du protocole et est brûlée. Le composant de priorité est destiné à l'inclusion et est versé selon les règles actuelles du réseau. Le prix effectif ne dépasse pas le plafond du prix que l'expéditeur a accepté. Les formulaires de portefeuille affichent souvent un maximum estimé, qui peut différer des frais effectivement facturés.

### Exemple réutilisable

Si le reçu indique 120 000 gas utilisés et un prix effectif de 25 gwei par unité, le coût est 3 000 000 gwei, soit 0,003 ETH. Cette opération de conversion suppose que le reçu et le prix sont déjà exprimés dans les unités attendues. Pour toute valeur importante, utilise une bibliothèque d'entiers plutôt qu'un type flottant qui peut perdre de la précision.

Il faut distinguer frais, valeur native transférée, jetons transférés et montant économique de l'appel. Une transaction peut envoyer 2 ETH et consommer 0,003 ETH de frais, donc le coût pour l'expéditeur ne se limite pas à l'un des deux nombres. Un appel de contrat peut déplacer des jetons sans envoyer de valeur native, mais il doit toujours être payé en frais sur le réseau qui exécute la transaction.

### Réseaux de couche 2

Un réseau de couche 2 peut facturer l'exécution locale ainsi qu'un coût associé à la publication de données ou au règlement sur une chaîne de base. Son mécanisme de frais dépend de son architecture et des mises à jour déployées. Le coût affiché par un portefeuille ne doit pas être interprété en recopiant simplement la formule d'Ethereum mainnet sans consulter la documentation du L2.

## 14. Diagnostiquer avec un reçu et une trace

Un diagnostic utile commence par le hash de transaction et le réseau. Il faut récupérer le reçu, le statut d'exécution, le gas utilisé, le bloc d'inclusion et, lorsqu'ils sont disponibles, les données de revert ou une trace détaillée. Ensuite, on décompose le chemin : validation de transaction, appel initial, appels externes, instructions coûteuses et point d'échec.

~~~mermaid
flowchart TD
    A["Hash de transaction"] --> B["Récupérer reçu et bloc"]
    B --> C{"Statut succès ?"}
    C -->|Oui| D["Vérifier événements et nouvel état"]
    C -->|Non| E["Inspecter revert et trace"]
    E --> F["Repérer le premier appel fautif"]
    F --> G["Reproduire dans un environnement local"]
    D --> H["Documenter le diagnostic"]
    G --> H
~~~

Une transaction peut échouer parce qu'une précondition métier n'est plus vraie, par exemple qu'un solde est insuffisant au moment de l'exécution. Elle peut échouer sur un appel externe, atteindre la limite de gas ou rencontrer une donnée oracle invalide. Ces causes exigent des corrections différentes. Augmenter arbitrairement la limite de gas ne corrige pas un contrôle d'accès ou une condition métier erronée.

### Procédure de triage

1. Confirmer le réseau, le hash, le bloc et la version du contrat.
2. Lire le reçu et distinguer rejet avant inclusion, revert et succès.
3. Comparer la consommation réelle à l'estimation initiale.
4. Examiner la donnée d'entrée encodée et l'état qui existait au bloc.
5. Si disponible, lancer une trace avec un nœud capable de fournir cette information.
6. Reproduire le scénario dans un environnement local avec le même état de départ.
7. Ajouter un test de régression avant de publier une correction.

Une trace n'est pas la même chose qu'un reçu normatif et toutes les API RPC ne fournissent pas les mêmes détails. Conserve la provenance de chaque donnée utilisée. Lorsque l'analyse repose sur un fournisseur tiers, compare au besoin le résultat avec une source indépendante.

### Optimisation guidée par mesure

Mesure d'abord les chemins dominants et les tailles d'entrée réalistes. Évite de réduire la sécurité pour économiser quelques unités. Une optimisation acceptable conserve les mêmes invariants, améliore ou maintient les tests, et documente le changement. Le gas est une contrainte de conception, mais la lisibilité et la sécurité restent des critères essentiels.

## 15. TP guidé A : comparer les coûts de lecture et d'écriture

### Objectif

Observer comment un contrat consomme du gas pour différentes opérations dans un réseau local ou un environnement de test.

### Étape 1 — Créer un contrat de laboratoire

Utilise un contrat simple qui possède un compteur, une fonction view pour le lire et une fonction qui l'incrémente. N'y associe aucun actif réel. Compile avec une version connue du compilateur.

### Étape 2 — Exécuter les opérations

Déploie le contrat sur un environnement local. Appelle la lecture plusieurs fois, puis appelle la fonction d'écriture. Relève le gas estimé et utilisé lorsque l'outil expose ces mesures. Une lecture simulée ne produit pas nécessairement une transaction persistante, il ne faut donc pas comparer deux catégories sans expliquer leurs différences.

### Étape 3 — Ajouter un tableau

Ajoute une fonction qui écrit dans un tableau de stockage et mesure le coût pour une, dix puis cent valeurs dans le cadre d'une boucle de test contrôlée. Ne déploie pas le code sur le réseau principal. Vérifie aussi le comportement lorsque la limite de gas est insuffisante.

### Étape 4 — Rapporter les résultats

Documente la version du compilateur, l'état initial, les entrées, le nombre d'opérations, le gas observé et les limites de l'expérience. Explique pourquoi les chiffres ne sont pas universels et peuvent changer selon l'état et les règles de gas.

**Corrigé indicatif :** les lectures et calculs sans écriture persistante présentent un profil différent des transactions qui modifient le stockage. Les tableaux augmentent le coût selon la quantité de données et l'algorithme. Les valeurs absolues dépendent du code compilé, de l'environnement et de l'état précédent. Une mesure ne doit pas être généralisée à tous les contrats.

## 16. TP guidé B : calculer des frais effectifs

### Objectif

Savoir expliquer une estimation de frais sans confondre la limite et la consommation réelle.

### Données fictives

Une transaction utilise 95 000 unités de gas. Le prix effectif est de 24 gwei par unité. Pour simplifier, suppose que ces valeurs sont confirmées dans le reçu. Calcule le coût en gwei puis convertis-le en ETH.

### Étapes

1. Multiplie 95 000 par 24.
2. Convertis le total de gwei en ETH avec un milliard de gwei par ETH.
3. Compare au scénario où la transaction utilise 95 000 gas à 40 gwei.
4. Compare au scénario où elle utilise 150 000 gas à 24 gwei.
5. Explique comment maxFeePerGas diffère du prix effectif payé.

**Corrigé :** 95 000 × 24 = 2 280 000 gwei, soit 0,00228 ETH. À 40 gwei, le même gas used donne 0,0038 ETH. Avec 150 000 gas à 24 gwei, le coût est 3 600 000 gwei, soit 0,0036 ETH. Le plafond maxFeePerGas fixe le montant maximum par unité accepté, mais le montant effectivement payé peut être inférieur selon les règles de base fee et de priorité.

## 17. Call frames et appels imbriqués

Lorsqu'une fonction appelle un autre contrat, l'EVM crée un contexte d'appel imbriqué. Le contrat appelé peut exécuter ses instructions, consommer du gas et appeler à son tour d'autres contrats. Le coût total d'une transaction dépend donc du chemin complet, pas uniquement de la fonction publique appelée par le portefeuille.

Il faut distinguer \`CALL\`, \`STATICCALL\` et \`DELEGATECALL\` au niveau conceptuel. CALL lance un appel où le contrat cible s'exécute dans son propre contexte ; STATICCALL interdit les modifications de l'état pendant le sous-appel ; DELEGATECALL exécute le code d'une autre adresse tout en conservant le contexte d'état du contrat appelant pour les opérations concernées. L'usage exact de ces instructions est complexe et doit se baser sur la spécification EVM et l'implémentation utilisée.

~~~mermaid
flowchart TD
    A["Transaction externe"] --> B["Frame du contrat A"]
    B --> C["CALL vers contrat B"]
    C --> D["Frame du contrat B"]
    D --> E["Appel éventuel vers contrat C"]
    E --> F["Retour des appels et résultats"]
    F --> G["État final ou revert propagé"]
~~~

### Propagation des erreurs

Si un appel interne échoue, le contrat appelant peut propager l'erreur et faire échouer l'ensemble de l'exécution, ou traiter l'échec selon sa logique. Le choix doit refléter les règles métier. Par exemple, un protocole qui effectue trois sous-opérations doit préciser si l'échec de la troisième annule les deux premières ou si des sous-opérations indépendantes peuvent être conservées.

La règle d'atomicité de l'EVM protège l'état de l'exécution qui revert, mais elle ne permet pas de conclure que toute opération externe dans un système complet est automatiquement inversée : les appels sont exécutés dans le cadre de la transaction, et les changements d'état traités selon les règles de rollback. Les services off-chain, emails envoyés et actions externes ne sont pas annulés par magie. Il faut donc éviter de déclencher des effets hors chaîne avant d'avoir un état suffisamment fiable, ou prévoir une logique de confirmation et de compensation.

### Traces et débogage

Une trace d'exécution peut révéler la succession d'appels, les arguments, les retours et le point où l'exécution s'arrête. Elle aide à repérer un appel récursif, une fonction coûteuse ou une erreur qui n'est pas visible dans l'interface. Toutes les API ne fournissent pas les mêmes traces ; une application doit documenter l'outil et la source dont elle dépend.

## 18. Optimiser une fonction : démarche et anti-patterns

L'optimisation du gas commence par une mesure de référence, sur le bytecode qui sera réellement déployé. Il faut fixer la version du compilateur, les options, les entrées, le réseau de test, l'état précédent et la méthode de mesure. Sans ces conditions, deux nombres peuvent être incomparables.

### Démarche d'optimisation

1. Écrire des tests qui décrivent le comportement correct.
2. Mesurer le gas pour plusieurs tailles d'entrée et états.
3. Inspecter la trace pour comprendre les opérations dominantes.
4. Formuler une hypothèse précise sur le coût.
5. Modifier une chose à la fois.
6. Relancer les tests fonctionnels et les tests de sécurité.
7. Comparer les mesures, documenter le gain et vérifier qu'il persiste dans les chemins représentatifs.

### Anti-patterns

Une optimisation dangereuse retire une validation d'entrée ou un contrôle d'accès pour économiser des ressources. Une optimisation prématurée utilise de l'assembleur difficile à relire sans preuve que le gas économisé est important. Une optimisation locale déplace parfois le coût vers le stockage ou vers un autre appel et n'améliore pas la transaction totale.

~~~mermaid
flowchart LR
    M["Mesurer le coût actuel"] --> H["Hypothèse mesurable"]
    H --> C["Changer une seule chose"]
    C --> T["Tests et analyse de sécurité"]
    T --> D{"Comportement identique et gain réel ?"}
    D -->|Oui| A["Documenter et conserver"]
    D -->|Non| R["Revenir au code sûr"]
~~~

### Coût des boucles et des lots

Une fonction qui parcourt un tableau dont la taille est contrôlée par des utilisateurs peut devenir inexécutable à mesure que le tableau augmente. Les solutions possibles sont les opérations par lots à taille bornée, la pagination pour les lectures, un indexeur hors chaîne ou une conception où chaque utilisateur traite ses propres éléments. Le bon choix dépend de ce que le contrat doit vérifier on-chain.

Si le contrat doit prouver une propriété sur l'ensemble de la liste, déplacer le calcul vers un serveur qui renvoie simplement un résultat ne suffit pas : il faut un mécanisme de preuve ou une hypothèse de confiance explicitement acceptée. Le gain de gas doit être évalué avec les coûts et risques déplacés hors chaîne.

## 19. Pourquoi les estimations de gas varient

Un simulateur prédit le gas d'un appel sur un état et un contexte donnés. Avant l'inclusion, le solde, les allowances, la position dans un protocole, la valeur d'un oracle ou la configuration d'un contrat peuvent changer. Le chemin d'exécution réel ne correspond alors plus nécessairement à la simulation.

Le prix du gas est aussi différent de la consommation de gas. Le gas used décrit le travail facturé ; le prix effectif par unité décrit le coût économique. Le portefeuille peut montrer un plafond maximal qui n'est pas le montant effectivement payé. L'utilisateur doit pouvoir distinguer estimation, plafond, consommation et frais définitifs dans le reçu.

### Petite expérience

Exécute une même fonction d'écriture dans un environnement local :
- première fois, lorsque l'emplacement de stockage contient zéro ;
- deuxième fois, lorsque la valeur est déjà présente ;
- troisième fois, lorsque la fonction effectue une écriture avec un autre chemin de code ;
- quatrième fois, avec un appel externe qui revert.

Note la valeur de gas used et explique les différences observées. Ne généralise pas un résultat à tous les contrats : les coûts dépendent des instructions, de l'état préalable et des règles du protocole.

### Revue du résultat

Après l'expérience, formule ce qui est stable (le comportement de la fonction selon la spécification), ce qui dépend de l'état (chemin d'exécution et coût), et ce qui dépend du marché des frais (prix par unité). Ce vocabulaire permet de diagnostiquer une transaction chère sans conclure automatiquement que le réseau est mal configuré.

## 20. Exercice avancé : distinguer estimation, exécution et frais

Trois valeurs sont souvent confondues dans les interfaces : l'estimation avant la soumission, le gas used du reçu et les frais définitifs. L'estimation est calculée sur un état simulé. Le reçu reflète l'exécution incluse. Les frais dépendent du gas effectivement facturé et du prix effectif par unité. Ces trois étapes peuvent différer.

~~~mermaid
flowchart TD
    A["Simulation avant envoi"] --> B["Gas estimé"]
    B --> C["Transaction signée et incluse"]
    C --> D["Exécution réelle"]
    D --> E["Gas used dans le reçu"]
    E --> F["Prix effectif par unité"]
    F --> G["Frais effectivement facturés"]
~~~

### Scénario

Une interface estime 90 000 unités de gas. L'utilisateur envoie la transaction avec une limite de 120 000. L'état change avant l'inclusion et la transaction prend un chemin différent, qui utilise 105 000 unités. L'application ne doit pas dire que le gas utilisé a été 90 000 : ce chiffre était une estimation, pas une mesure finale.

Si la transaction échoue après avoir consommé 105 000 unités, les changements d'état peuvent être annulés alors que les frais du travail effectué restent dus selon les règles du protocole. C'est pourquoi l'expérience utilisateur doit afficher à la fois le résultat métier et le coût. Un revert n'est pas forcément un échec de réseau ; il peut être le comportement correct d'une précondition non satisfaite.

### Diagnostic par comparaison

Pour analyser un coût, conserve l'état d'entrée, les paramètres de transaction, la version de compilation, l'estimation, le reçu, le prix effectif et toute trace disponible. Compare ensuite la simulation et l'exécution. Si le résultat diverge, cherche d'abord quel état a changé entre les deux opérations, puis quel chemin d'exécution a été pris.

N'optimise pas sur un seul exemple. Une fonction peut coûter davantage lorsque la valeur de stockage initiale change ou lorsqu'un tableau a grandi. Les mesures répétées doivent couvrir les chemins normaux, limites et adverses.

## 21. Lecture d'une trace : trouver la source d'un gas élevé

Lorsqu'une transaction consomme plus de gas que prévu, commence par comparer l'estimation, le reçu et la trace si celle-ci est disponible. Le premier appel qui consomme beaucoup n'est pas toujours la cause métier du problème ; il faut comprendre pourquoi ce chemin d'exécution a été pris et si la quantité de données était attendue.

~~~mermaid
flowchart TD
    A["Reçu : gas used"] --> B["Comparer à la simulation"]
    B --> C["Inspecter la trace d'appels"]
    C --> D["Repérer boucles, écritures et appels externes"]
    D --> E["Reproduire avec le même état d'entrée"]
    E --> F["Tester une optimisation sûre"]
~~~

### Exemple

Une fonction met à jour un profil et parcourt ensuite une liste d'adresses pour synchroniser les droits. Le coût augmente lorsque la liste grandit. Le problème peut être la complexité de la fonction, mais aussi le fait que l'opération a été conçue comme une écriture collective non bornée. Une optimisation peut consister à traiter les éléments par lots ou à déplacer une partie de la recherche vers un indexeur, mais seulement si la vérification on-chain reste correcte.

Le diagnostic doit enregistrer la taille de la liste, l'état initial, les versions et les appels effectués. Si la liste est très petite dans le test, le défaut de croissance peut passer inaperçu. Les mesures devraient inclure plusieurs tailles d'entrée et les chemins où l'appel externe réussit ou échoue.

## 22. Mesurer l'effet d'une modification de code

Une modification qui semble plus courte n'est pas nécessairement moins coûteuse. Le compilateur peut optimiser deux formes équivalentes différemment, et le coût réel dépend également de l'état et des accès effectués. Compare le gas du bytecode construit avec les mêmes versions et options.

Pour chaque optimisation, prépare :
1. le test de référence qui définit le comportement ;
2. une série d'entrées représentatives ;
3. la mesure avant changement ;
4. la mesure après changement ;
5. les tests de sécurité relancés ;
6. l'explication du gain ou de la perte observés.

Si le gain est faible et que la lisibilité chute fortement, il peut être préférable de conserver la version plus claire. Si une modification réduit fortement les écritures, vérifie qu'elle n'a pas déplacé une dépendance vers un backend moins fiable ou supprimé une vérification de sécurité. Une optimisation est une décision d'architecture, pas seulement une chasse au nombre de gas.

## 23. Suivre une transaction de bout en bout et expliquer sa consommation de gas

Comprendre le gas exige de séparer plusieurs étapes : préparation de la transaction, diffusion, inclusion dans un bloc, exécution par la machine virtuelle, création du reçu et interprétation par l'application. Une transaction peut être correctement signée mais jamais incluse ; elle peut être incluse puis revert ; elle peut réussir tout en produisant un effet métier différent de celui attendu. Le diagnostic doit donc partir de l'identité de la transaction, du réseau et du bloc, puis suivre les preuves disponibles.

### 23.1 Les éléments d'une transaction et le reçu

Pour une transaction de type courant sur Ethereum, vérifie au minimum le compte expéditeur, le nonce, le destinataire ou l'indicateur de création de contrat, les données d'appel, la limite de gas et les paramètres de frais. La limite est le plafond d'unités d'exécution que l'expéditeur autorise ; elle n'est pas la quantité qui sera nécessairement consommée. Le reçu donne notamment le statut, le gas utilisé, le bloc d'inclusion et les logs générés. Ces informations répondent à des questions différentes et ne doivent pas être remplacées par un simple message « terminé ».

Le nonce permet d'ordonner les transactions d'un même compte. Si une transaction antérieure reste en attente, une transaction ultérieure peut rester bloquée même si ses données sont correctes. Une transaction peut aussi être remplacée par une autre utilisant le même nonce et des paramètres de frais adaptés à la politique du réseau. L'application doit suivre le hash effectivement retenu et éviter de présenter une ancienne tentative comme si elle était toujours la transaction active.

### 23.2 Comprendre le modèle de frais

Le gas utilisé mesure le coût en unités d'exécution selon les règles du réseau ; le prix effectif payé par unité détermine ensuite le coût monétaire. Dans le modèle EIP-1559, le montant effectif par unité dépend du prix de base du bloc et du pourboire proposé, dans les limites des paramètres de la transaction. Le prix de base est brûlé sur Ethereum, tandis que le pourboire revient au producteur de bloc selon le mécanisme prévu. Il faut vérifier les règles du réseau ciblé, car les réseaux compatibles EVM peuvent appliquer des politiques différentes.

Un calcul de frais doit tenir compte de l'unité native, de la précision d'affichage et de la différence entre estimation préalable et coût constaté. Une estimation de gas ne prédit pas toutes les conditions d'exécution ; la consommation peut changer selon l'état du contrat, les données d'entrée, la branche exécutée et les écritures de stockage. L'interface devrait afficher séparément le coût estimé, la limite autorisée et le coût réel une fois le reçu disponible.

### 23.3 Diagnostiquer un revert avec une trace

Un reçu ayant un statut d'échec indique que l'exécution n'a pas abouti, mais pas nécessairement où la décision a échoué. Une trace d'exécution peut montrer les appels imbriqués, les données transmises, le type d'appel et l'endroit où le revert est remonté. Selon le client et les méthodes RPC disponibles, la profondeur et le format de la trace varient. Il faut conserver le hash, la chaîne, le bloc et le fournisseur interrogé pour que l'analyse puisse être reproduite.

Cherche d'abord l'appel le plus profond qui a échoué, puis remonte vers l'appelant. Vérifie les conditions d'accès, les paramètres, les soldes, les allowances, les limites de gas et l'état des contrats externes à ce bloc. Le dernier message visible n'est pas toujours la cause initiale : un contrat peut intercepter ou transformer une erreur, et une simulation effectuée après coup peut voir un état différent de celui de l'exécution originale.

| Symptôme | Ce qu'il faut examiner | Conclusion à éviter |
|---|---|---|
| Coût supérieur à l'estimation | État modifié, chemin exécuté, prix effectif | « Le réseau a forcément augmenté le gas » |
| Revert avec message peu clair | Trace, données d'entrée, appel externe | Se fier uniquement au texte de l'interface |
| Transaction non incluse | Nonce, frais, propagation, état du mempool | La considérer comme échouée définitivement |
| Reçu réussi mais résultat inattendu | Événements, état après exécution, bonne adresse | Conclure que le métier est réussi |
| Gas utilisé proche de la limite | Boucles, appels externes, données variables | Augmenter la limite sans identifier la cause |

### 23.4 Optimiser avec des mesures et des invariants

Avant une optimisation, établis une référence reproductible : version du compilateur, paramètres de compilation, état initial, données d'entrée, gas utilisé et effets métier. Modifie un élément à la fois et compare les résultats sur plusieurs tailles d'entrées pertinentes. Une modification qui améliore un cas nominal peut aggraver le pire cas ou rendre le code moins sûr à auditer.

Les économies doivent être évaluées face à la lisibilité, aux risques et au coût de maintenance. Réduire une écriture de stockage peut être intéressant, mais contourner des contrôles de sécurité pour gagner quelques unités de gas est un mauvais compromis. Les boucles dont la taille dépend d'une entrée externe doivent faire l'objet d'une limite explicite ou d'une stratégie de traitement par lots. Une fonction qui devient inexécutable à cause d'une liste trop grande peut causer une panne métier même si elle est logiquement correcte.

~~~mermaid
flowchart TD
    A[Hash de transaction] --> B[Vérifier chaîne et reçu]
    B --> C{Transaction incluse ?}
    C -->|Non| D[Étudier nonce, frais et propagation]
    C -->|Oui| E{Statut réussi ?}
    E -->|Non| F[Analyser revert et trace]
    E -->|Oui| G[Comparer événements et état]
    F --> H[Reproduire sur environnement contrôlé]
    G --> I{Effet métier attendu ?}
    I -->|Non| J[Examiner logique et configuration]
    I -->|Oui| K[Documenter le résultat]
    D --> K
    H --> K
    J --> K
~~~

### 23.5 Mini-laboratoire de diagnostic

Choisis une transaction de test qui appelle une fonction avec au moins deux branches, par exemple un retrait autorisé et un retrait rejeté. Note l'état initial, les paramètres, le gas estimé, la limite, le hash et le reçu. Compare ensuite le chemin réussi avec le chemin qui échoue. Le rapport doit expliquer la condition qui a déclenché l'échec, les effets qui ont été annulés, les événements présents ou absents et ce que l'interface aurait dû afficher.

Ne teste pas de transactions à risque sur un contrat contenant de vrais actifs. Utilise une chaîne locale ou un réseau de test que tu maîtrises. Le résultat attendu est un diagnostic reproductible par un autre développeur, pas seulement une capture d'écran affichant un nombre de gas.

## 24. Dix questions d'entraînement avec corrigé

### Question 1
Quel est le rôle de l'EVM ?

**Corrigé :** Définir et exécuter de manière déterministe le bytecode des contrats dans le contexte du protocole Ethereum, en appliquant les règles d'état et de gas.

### Question 2
Quelle est la différence entre code source et bytecode ?

**Corrigé :** Le code source est la représentation lisible destinée aux développeurs ; le bytecode est la représentation exécutée par l'EVM après compilation.

### Question 3
Pourquoi le stockage persistant est-il important pour le gas ?

**Corrigé :** Les écritures modifient l'état partagé que les nœuds doivent suivre et ont donc un coût selon les règles du protocole. Leur coût dépend du type de changement et du contexte.

### Question 4
Le gas est-il identique au prix du gas ?

**Corrigé :** Non. Le gas mesure la quantité de ressources facturées ; le prix par unité détermine combien coûte chaque unité. Les frais dépendent des deux.

### Question 5
Que se passe-t-il si une transaction revert après son inclusion ?

**Corrigé :** Les changements d'état de l'exécution sont annulés, mais les frais correspondant au gas consommé sont généralement facturés selon les règles du protocole.

### Question 6
Que fait EIP-1559 au mécanisme de frais ?

**Corrigé :** Il introduit notamment une base fee ajustée par le protocole et un composant de priorité, avec des plafonds de frais définis par l'expéditeur.

### Question 7
Pourquoi une estimation de gas n'est-elle pas une garantie ?

**Corrigé :** L'état et le chemin d'exécution peuvent changer avant l'inclusion, les dépendances peuvent évoluer et l'estimation peut être incomplète.

### Question 8
Pourquoi ne pas optimiser en supprimant un contrôle d'accès ?

**Corrigé :** Parce que cela compromet une propriété de sécurité essentielle pour une économie de coût potentiellement minime. Les optimisations ne doivent pas violer les invariants.

### Question 9
À quoi sert une trace d'exécution ?

**Corrigé :** Elle aide à comprendre le chemin et les appels effectués pendant une transaction, ainsi que les opérations qui consomment des ressources. Sa disponibilité dépend de l'outil et du nœud.

### Question 10
Pourquoi le gas d'une couche 2 peut-il différer du coût total payé par l'utilisateur ?

**Corrigé :** Le coût peut inclure l'exécution sur la couche 2 et une part des coûts de publication de données ou de règlement sur la couche de base, selon le réseau.

## 25. Challenge final : diagnostiquer une transaction trop chère

### Scénario

Une application permet à un utilisateur de mettre à jour son profil et d'enregistrer une liste d'éléments. Le coût de transaction augmente fortement à mesure que la liste grandit. Un développeur propose de supprimer une série de vérifications pour réduire le gas.

### Travail demandé

Rédige un rapport de 500 à 700 mots. Tu dois proposer une méthode pour mesurer le coût, identifier les opérations dominantes, distinguer lecture et écriture, évaluer des alternatives de données et démontrer pourquoi les contrôles de sécurité ne doivent pas être supprimés sans analyse.

### Correction proposée

La première étape est de reproduire le coût avec une version, des paramètres de compilation et des entrées fixes. Il faut mesurer plusieurs tailles de liste et profiler la fonction ou examiner une trace pour trouver les postes de coût : écritures de stockage, boucles, copies de données, événements et appels externes. Une seule estimation fournie par un portefeuille ne suffit pas pour savoir où l'exécution dépense le gas.

Ensuite, les développeurs doivent formaliser les invariants. Les vérifications qui garantissent que l'appelant est autorisé, que l'entrée respecte une limite ou que l'état reste cohérent ne doivent pas être supprimées simplement pour réduire le coût. Il faut déterminer quelles vérifications sont redondantes, lesquelles peuvent être faites de façon sûre hors chaîne tout en étant vérifiées on-chain, et lesquelles sont indispensables au contrat.

Si la liste est destinée à un historique consultable, une partie des données peut éventuellement être indexée hors chaîne, avec un engagement ou une preuve selon le modèle d'application. Si le contrat doit utiliser l'intégralité de la liste pour prendre une décision, il faudra concevoir une structure qui garde le coût borné ou traiter les éléments par lots. La pagination aide les lectures et certaines opérations, mais ne résout pas automatiquement un calcul collectif qui doit parcourir toute la liste pour être correct.

Enfin, tout changement doit être testé avec des valeurs petites, grandes, vides, malformées et adverses. Compare le comportement avant et après optimisation, mesure le gas et fais relire le code. Une optimisation réussie réduit les coûts tout en préservant les invariants, les permissions et la clarté. La meilleure solution n'est pas nécessairement le code le plus court, mais une architecture sûre et mesurable.

## Glossaire

**ABI :** description du format d'appel des fonctions et de décodage des résultats d'un contrat.

**Base fee :** frais de base par unité de gas déterminés par le mécanisme du protocole pour un bloc.

**Bytecode :** code exécutable par l'EVM après compilation.

**Calldata :** données d'entrée d'un appel de fonction, habituellement en lecture seule.

**EIP-1559 :** mise à jour qui a introduit le modèle moderne de frais avec base fee et priorité.

**EVM :** machine virtuelle Ethereum qui exécute les contrats selon les règles du réseau.

**Gas :** unité de comptabilité des ressources consommées par une exécution.

**Gas limit :** plafond de gas associé à une transaction ou défini pour un bloc, selon le contexte.

**Gas used :** quantité de gas effectivement consommée par la transaction.

**Max fee :** prix maximal par unité accepté par l'expéditeur dans une transaction compatible.

**Mémoire :** zone de données temporaire pendant l'exécution.

**Prix de priorité :** composant de frais proposé pour encourager l'inclusion de la transaction.

**Revert :** arrêt d'une exécution et annulation de ses changements d'état, avec frais possibles pour le travail effectué.

**Storage :** état persistant d'un contrat sur la blockchain.

## Pour aller plus loin

- Documentation officielle EVM : https://ethereum.org/developers/docs/evm/
- Documentation Ethereum sur le gas et les frais : https://ethereum.org/developers/docs/gas/
- Spécification EIP-1559 : https://eips.ethereum.org/EIPS/eip-1559
- Documentation de Solidity : https://docs.soliditylang.org/en/latest/
- Documentation de débogage d'un environnement Solidity : https://hardhat.org/docs

Les coûts et règles peuvent évoluer avec les mises à jour du protocole. Pour toute estimation de production, vérifie les spécifications actuelles du réseau, mesure le contrat avec la version exacte du compilateur et affiche le coût à l'utilisateur en séparant estimation, plafond et frais effectivement payés.
