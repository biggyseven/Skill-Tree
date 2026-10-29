# Structure d'un bloc

## Encadré de mise en contexte

Un bloc est souvent représenté comme un rectangle contenant une liste de transactions. Cette image aide à démarrer, mais elle ne suffit pas à comprendre ce qu'un nœud vérifie ni pourquoi l'historique peut être considéré comme coûteux à réécrire. Un bloc possède des métadonnées, des engagements cryptographiques sur les données qu'il contient ou sur l'état produit, ainsi que des relations avec d'autres blocs. Le format précis dépend du protocole : Bitcoin et Ethereum n'organisent pas leurs données de la même façon et n'utilisent pas le même mécanisme de consensus.

Cette leçon décrit les éléments habituels d'un bloc, leur utilité, les validations effectuées par les nœuds et les situations qui peuvent provoquer le rejet d'un bloc. Elle insiste sur une distinction fondamentale : **un bloc bien formé n'est pas automatiquement un bloc accepté**. Il peut respecter la syntaxe tout en contenant une transaction invalide, référencer un parent inconnu, dépasser une limite du protocole ou appartenir à une branche que le consensus ne retient finalement pas.

## Objectifs d'apprentissage

À la fin de cette leçon, tu sauras :

- décrire la relation entre blocs, transactions et état ;
- expliquer le rôle du bloc de genèse, du bloc parent et du hachage d'en-tête ;
- comprendre les champs principaux d'un en-tête Bitcoin ;
- distinguer la racine de Merkle du hash du bloc ;
- expliquer la différence entre taille en octets, poids de bloc et capacité ;
- identifier les éléments structurants d'un bloc Ethereum ;
- comprendre les racines d'état, de transactions et de reçus ;
- décrire le flux d'un bloc à travers les nœuds ;
- distinguer validation syntaxique, validation des transactions, consensus et finalité ;
- expliquer confirmations, réorganisations et risques liés à un bloc non finalisé ;
- réaliser une inspection guidée et corriger une hypothèse de bloc invalide.

## 1. Qu'est-ce qu'un bloc ?

Un bloc est une unité de données structurée qu'un protocole utilise pour grouper des opérations et les relier à un historique. Dans une blockchain, un bloc contient généralement ou référence une collection de transactions et des métadonnées nécessaires à l'identification, à la validation ou à la mise à jour de l'état. D'autres données sont spécifiques à chaque protocole.

On peut distinguer trois niveaux :

1. **Les données applicatives** : les transactions, les appels de contrats ou d'autres opérations soumises au protocole.
2. **Les métadonnées du bloc** : référence au parent, horodatage ou slot, informations de consensus et engagements cryptographiques.
3. **L'état obtenu après exécution** : soldes, UTXO, stockage des contrats et autres données qui décrivent le résultat de l'application des transactions.

Les niveaux sont liés, mais ils ne sont pas identiques. Une transaction décrit une opération proposée. Le bloc est le conteneur ordonné dans lequel elle est incluse. L'état est le résultat de l'application des règles sur l'historique précédent. Selon la blockchain, l'état peut être explicitement résumé par une racine dans l'en-tête.

~~~mermaid
flowchart TD
    T["Transactions ordonnées"] --> B["Corps du bloc"]
    P["Bloc parent connu"] --> H["En-tête du nouveau bloc"]
    B --> R["Engagements cryptographiques"]
    R --> H
    H --> C["Validation et consensus"]
    C --> S["Nouvel état accepté"]
    S --> N["Bloc suivant construit sur cet état"]
~~~

Un bloc n'est donc pas une preuve que toutes les opérations qui y figurent sont moralement acceptables ou économiquement sûres. C'est un objet que le réseau doit vérifier selon ses règles. Les applications peuvent encore présenter des risques, et une transaction peut être valide au niveau du protocole tout en déclenchant un contrat mal conçu.

## 2. Bloc de genèse et chaînage

### 2.1 Le bloc de genèse

Le bloc de genèse est le premier bloc de la chaîne. Il ne possède pas de parent ordinaire antérieur dans la même chaîne ; son traitement est prévu par le logiciel ou par les paramètres de lancement du réseau. Les autres blocs peuvent ainsi construire une histoire à partir d'un point de départ convenu.

Chaque nœud doit utiliser les paramètres correspondant au bon réseau. Un bloc de genèse différent implique généralement un historique différent. Un nœud Bitcoin du réseau principal, un nœud de test et un nœud d'un réseau privé peuvent utiliser des paramètres distincts : il ne suffit pas d'avoir un programme du même nom pour être connecté au même registre.

### 2.2 Le hash du parent

Dans une blockchain à chaînage par hash, l'en-tête du nouveau bloc contient une référence cryptographique au bloc parent. Cette référence lie le bloc courant à un historique précis. Si le contenu du parent change, son hash change ; l'en-tête du bloc enfant ne pointe alors plus vers le hash correspondant. Les blocs suivants dépendent à leur tour du hash de leur parent.

~~~mermaid
flowchart LR
    A["Bloc A<br/>hash A"] --> B["Bloc B<br/>parent = hash A"]
    B --> C["Bloc C<br/>parent = hash B"]
    C --> D["Bloc D<br/>parent = hash C"]
    X["Modification de A"] -. "hash A modifié" .-> A
    A -. "référence de B incohérente" .-> B
~~~

Cette construction rend une modification détectable. Elle n'interdit pas à quelqu'un de modifier une copie locale et de recalculer les blocs suivants. La difficulté de remplacer une histoire acceptée vient aussi du consensus, des incitations, des ressources nécessaires et des règles appliquées par les nœuds. Il faut éviter de décrire le chaînage par hash comme une protection autonome contre toute réécriture.

### 2.3 Les forks de blocs

Deux blocs différents peuvent référencer le même parent. Cela peut survenir si plusieurs producteurs proposent un bloc à des instants rapprochés, si les messages mettent du temps à circuler ou si un protocole permet plusieurs propositions concurrentes. Il peut alors exister temporairement plusieurs branches.

Le mécanisme de consensus détermine ensuite comment les nœuds choisissent la branche à suivre ou comment ils finalisent une chaîne. Les détails varient : Bitcoin utilise la preuve de travail et une règle de sélection basée sur le travail cumulé valide ; Ethereum utilise la preuve d'enjeu et un mécanisme de consensus fondé sur les validateurs, les attestations et la finalité. Les mécanismes ne doivent pas être mélangés en une seule règle simplifiée.

## 3. En-tête Bitcoin

Bitcoin sépare son en-tête de bloc du contenu complet de la liste des transactions. L'en-tête historique comporte 80 octets et contient plusieurs champs. Le format d'un bloc complet inclut aussi une représentation de la liste de transactions et leurs sérialisations.

Les champs principaux de l'en-tête Bitcoin sont :

| Champ | Taille historique | Rôle |
|---|---:|---|
| Version | 4 octets | Indication de version et de signalisation de règles |
| Hash du bloc parent | 32 octets | Référence cryptographique au bloc précédent |
| Racine de Merkle | 32 octets | Engagement envers les transactions du bloc |
| Horodatage | 4 octets | Temps déclaré par le producteur du bloc, sous contraintes du protocole |
| Cible encodée (nBits) | 4 octets | Représentation compacte de la cible de preuve de travail |
| Nonce | 4 octets | Champ modifié pendant la recherche de preuve de travail |

Les nombres ci-dessus décrivent la sérialisation traditionnelle de l'en-tête Bitcoin. Un développeur doit également tenir compte de l'ordre des octets, de la représentation exacte des champs et des règles de validation. L'affichage d'un explorateur n'est pas forcément identique à l'ordre binaire transmis sur le réseau.

### 3.1 Version

Le champ de version est un champ numérique de l'en-tête. Historiquement, il indiquait une version et a ensuite été utilisé, selon les périodes et les règles, pour signaler des capacités ou des mécanismes de mise à niveau. Il ne faut pas l'interpréter comme un simple numéro de version du logiciel installé sur le mineur. Le logiciel, la version d'en-tête et les règles activées sont des concepts distincts.

### 3.2 Hash du parent

Le hash du parent lie le bloc courant au bloc précédent. Le nœud vérifie que le parent est connu et que le bloc s'inscrit correctement dans une chaîne valide. Un bloc dont le parent est inconnu peut être mis en attente jusqu'à ce que les données manquantes arrivent, ou être traité différemment selon l'implémentation ; cela ne signifie pas qu'il doit être accepté immédiatement.

### 3.3 Racine de Merkle

La racine de Merkle résume les transactions ordonnées du bloc selon la construction de Merkle définie par Bitcoin. Les nœuds calculent l'engagement attendu et le comparent à la racine de l'en-tête. Une racine incohérente signale que la liste de transactions ou son organisation ne correspond pas à l'en-tête présenté.

Cette racine n'est pas le hash du bloc lui-même. La racine de Merkle est un champ de l'en-tête ; le hash de bloc est calculé à partir de l'en-tête sérialisé selon la fonction prévue par le protocole. Une modification de la liste des transactions change en principe la racine de Merkle, donc l'en-tête, donc le hash du bloc.

### 3.4 Horodatage

L'horodatage est une valeur déclarée par le producteur du bloc. Le protocole impose des contraintes, notamment relatives au temps des blocs précédents et au temps rapporté par les nœuds. Il ne constitue pas une horloge mondiale parfaitement fiable. Des divergences existent entre l'heure réelle, les horloges des machines et les temps acceptables par le protocole.

Il est donc imprudent de déduire d'un horodatage seul l'heure exacte à laquelle une transaction s'est produite ou a été vue par tous les nœuds. L'horodatage doit être interprété dans le contexte du protocole et des limites de précision prévues.

### 3.5 Cible et preuve de travail

Bitcoin utilise la preuve de travail. Le champ nBits encode une cible. Pour qu'un en-tête satisfasse la preuve de travail, son hash interprété selon la convention de Bitcoin doit se situer dans la plage permise par la cible. Le mineur fait varier certaines données, y compris le nonce et des éléments liés aux transactions, afin de chercher un hash acceptable.

La cible et la difficulté sont liées, mais ce sont deux façons différentes d'exprimer l'exigence de calcul. Une cible plus basse impose une condition plus stricte : moins de hashes la satisfont. Le protocole ajuste périodiquement la cible selon ses règles, afin de maintenir une production des blocs autour d'un intervalle visé malgré les variations de puissance de calcul.

Un champ nonce de 32 bits offre un nombre limité de valeurs. Lorsque toutes les valeurs possibles ont été essayées, les mineurs peuvent modifier d'autres éléments admissibles, par exemple la transaction coinbase et l'extra-nonce qu'elle contient, ce qui change la racine de Merkle et fournit un nouvel espace de recherche. La preuve de travail ne consiste donc pas simplement à incrémenter le nonce à l'infini.

## 4. Le corps d'un bloc Bitcoin

Après l'en-tête se trouve une représentation de la collection de transactions. Le corps comprend notamment un compteur de transactions et les transactions sérialisées. L'ordre compte : la racine de Merkle et les règles de validation s'appliquent à une collection déterminée, avec une construction définie.

### 4.1 La transaction coinbase

Le premier élément d'un bloc Bitcoin valide est une transaction spéciale appelée transaction coinbase. Elle crée la subvention de bloc autorisée par le protocole et permet de réclamer les frais des transactions incluses. Ce n'est pas la même chose qu'une plateforme d'échange appelée « Coinbase » ; le terme technique est historique et désigne un type de transaction.

La coinbase ne dépense pas des sorties ordinaires de la même façon qu'une transaction utilisateur. Elle dispose de contraintes particulières et peut inclure des données supplémentaires définies par le protocole. Le producteur du bloc ne peut pas réclamer une subvention supérieure à la règle monétaire applicable. Si la coinbase crée trop de valeur, le bloc est invalide même si la preuve de travail est correcte.

### 4.2 Entrées et sorties UTXO

Bitcoin s'appuie sur le modèle UTXO. Une transaction consomme des sorties non dépensées de transactions antérieures et crée de nouvelles sorties. Chaque sortie spécifie une valeur et une condition de dépense. Une transaction est généralement valide si ses entrées peuvent être dépensées selon leurs conditions, qu'elles n'ont pas déjà été consommées, que les sommes respectent les règles et que toutes les contraintes de script sont satisfaites.

La valeur entrée moins la valeur sortie correspond aux frais de la transaction, selon les règles et conventions applicables. Les frais peuvent être réclamés par le producteur du bloc via la coinbase. Les entrées ne sont pas simplement des « adresses qui envoient de l'argent » : elles référencent des sorties antérieures spécifiques et fournissent des données de dépense permettant de satisfaire leurs conditions.

~~~mermaid
flowchart LR
    U1["Sortie non dépensée A"] --> T["Transaction"]
    U2["Sortie non dépensée B"] --> T
    T --> O1["Nouvelle sortie pour Bob"]
    T --> O2["Nouvelle sortie de monnaie"]
    T --> F["Frais implicites = entrées - sorties"]
~~~

### 4.3 Ordre des transactions

Les transactions d'un bloc sont ordonnées. Une transaction peut dépendre d'une sortie créée par une transaction précédente, ce qui impose une relation de dépendance. Un bloc ne peut pas arbitrairement placer une transaction dépensant une sortie avant que cette sortie existe dans l'état à appliquer, sauf cas et règles spécifiques prévus par le protocole. La validation s'effectue de manière à produire un état cohérent.

La présence d'une transaction dans le corps ne prouve pas qu'elle a été diffusée avant toutes les autres transactions connues. Le producteur assemble un bloc à partir de données qu'il reçoit et d'une politique de sélection qui respecte le protocole. Il peut choisir parmi des transactions concurrentes, notamment en fonction des frais et des dépendances, sans pouvoir rendre valides les transactions qui enfreignent les règles de consensus.

## 5. Taille, poids, frais et capacité dans Bitcoin

La taille brute d'un bloc en octets n'est pas toujours la mesure pertinente de la capacité. Depuis SegWit, Bitcoin utilise une notion de poids de bloc qui prend en compte les données témoins et les données non témoins selon des facteurs distincts. Les limites du protocole s'appliquent au poids et à d'autres contraintes, pas uniquement à un chiffre de taille observé dans un explorateur.

Les frais Bitcoin sont souvent exprimés en satoshis par unité de poids, par exemple sat/vB. Une transaction plus complexe ou qui transporte davantage de données peut consommer plus d'espace dans un bloc. Les frais ne sont pas simplement un pourcentage du montant envoyé : envoyer une petite somme peut coûter plus cher qu'envoyer une grande somme si la transaction a la même taille et si le marché des frais est similaire.

La capacité réelle est influencée par la demande, le comportement des producteurs de blocs, le poids des transactions, la politique du mempool, les règles du réseau et les couches complémentaires telles que Lightning. Les chiffres de transactions par seconde sont donc des estimations dépendant du type de transactions et des hypothèses retenues.

Une distinction opérationnelle est importante : un nœud peut avoir des politiques de relais plus restrictives que les règles de consensus. Une transaction qui n'est pas relayée par un nœud selon sa politique n'est pas nécessairement invalide au sens du consensus. À l'inverse, une transaction acceptée dans un mempool peut encore ne jamais être incluse, ou être rejetée par un bloc si elle ne respecte pas les règles.

## 6. Corps et en-têtes dans Ethereum

Ethereum possède un modèle différent de Bitcoin. Ses blocs comprennent un en-tête et des données liées aux transactions, aux reçus et à l'exécution. La structure exacte a évolué avec les mises à jour du protocole. Les champs suivants sont des catégories importantes, mais la liste complète dépend de la version du protocole, du type de bloc et des mises à jour activées.

### 6.1 Champs courants de l'en-tête Ethereum

| Champ | Rôle conceptuel |
|---|---|
| Parent hash | Identifie le bloc parent |
| State root | Engagement cryptographique envers l'état résultant du bloc |
| Transactions root | Engagement envers les transactions incluses |
| Receipts root | Engagement envers les reçus d'exécution |
| Number | Hauteur du bloc dans la chaîne d'exécution |
| Timestamp | Temps associé au bloc selon les règles du réseau |
| Gas limit | Limite de gaz associée au bloc selon les règles applicables |
| Gas used | Gaz consommé par les transactions exécutées dans le bloc |
| Beneficiary / fee recipient | Adresse associée à la réception de certaines rémunérations, selon les règles |
| Base fee per gas | Prix de base du gaz dans les formats qui incluent ce champ |
| MixHash / prevRandao | Champ dont le rôle a évolué avec la transition du consensus |
| Extra data | Champ de données auxiliaire soumis à des limites |
| Withdrawals root | Engagement relatif aux retraits dans les formats où il existe |
| Champs liés aux blobs | Engagements et données ajoutés par les mises à jour qui prennent en charge les blobs |

La présence, le nom exact et la sérialisation de certains champs varient au fil des mises à jour. Il faut consulter la spécification correspondant au fork de réseau étudié plutôt que de prendre un exemple ancien comme description valable pour toujours.

### 6.2 La racine d'état

La state root est un engagement cryptographique sur l'état résultant de l'exécution des transactions du bloc. L'état Ethereum comprend notamment les comptes, leurs soldes, certains compteurs et le stockage des contrats. Plutôt que de recopier l'ensemble de cet état dans l'en-tête, le bloc contient une racine qui résume la structure de données d'état selon les règles du protocole.

La racine d'état est différente de la racine de transactions. Deux listes de transactions peuvent être différentes mais produire des états similaires dans certains scénarios, et une même liste de transactions appliquée à des états précédents différents peut donner des résultats différents. La state root engage le résultat de la transition depuis l'état parent, tandis que la transactions root engage la liste des transactions sérialisées.

### 6.3 Transactions root et receipts root

La transactions root engage les transactions du bloc. La receipts root engage les reçus obtenus après l'exécution. Un reçu contient des informations sur le résultat de l'exécution, comme le statut, la quantité cumulée de gaz et des journaux produits, selon le format et la version. Un reçu n'est pas la transaction elle-même : il décrit des informations liées à son traitement.

La distinction est utile pour le diagnostic. Si une transaction est présente et valide au niveau du protocole, elle peut échouer lors de l'exécution d'un contrat et produire un reçu indiquant un échec. La transaction a néanmoins consommé des ressources et peut entraîner des frais selon les règles. Le terme « transaction invalide » ne doit donc pas être utilisé pour toute exécution qui échoue : l'invalidité de transaction, le rejet par le consensus et l'échec d'exécution sont des catégories différentes.

### 6.4 Gaz, limite de gaz et frais

Dans Ethereum, le gaz mesure les ressources de calcul et d'exécution facturées par le protocole. Chaque opération d'exécution consomme une quantité définie de gaz. Une transaction fournit une limite de gaz, et le bloc impose une limite globale selon les règles applicables. Une exécution qui atteint sa limite peut échouer, tout en consommant le gaz déjà utilisé selon les règles du protocole.

Depuis la mise à jour London, le mécanisme de frais comprend une base fee par unité de gaz et, dans les transactions concernées, une priorité offerte au producteur. La base fee est déterminée par le mécanisme du protocole et est brûlée, tandis que la priorité peut être versée selon les règles du réseau. Les frais exacts dépendent de l'utilisation, de la limite de gaz, de la base fee et des champs de frais de la transaction.

Le gaz n'est pas un synonyme exact du temps CPU, du coût électrique ou du prix de marché. C'est une unité comptable interne destinée à mesurer les ressources facturées. Deux opérations qui prennent un temps réel différent peuvent avoir une consommation de gaz imposée par la machine virtuelle et ses règles. Le montant économique payé dépend ensuite du prix du gaz.

## 7. Comparer le bloc Bitcoin et le bloc Ethereum

| Sujet | Bitcoin | Ethereum |
|---|---|---|
| Modèle central | Transactions qui consomment et créent des UTXO | Transactions qui changent un état de comptes et de contrats |
| Preuve de consensus | Preuve de travail sur l'en-tête | Preuve d'enjeu pour le consensus actuel |
| Engagement des transactions | Racine de Merkle dans l'en-tête | Transactions root, selon la structure propre au protocole |
| Engagement d'état | L'état UTXO est reconstruit à partir des transactions validées ; ce n'est pas une state root dans l'en-tête de base Bitcoin | State root engage l'état résultant |
| Ressource de capacité | Poids de bloc et règles associées | Limite et consommation de gaz, plus contraintes liées aux données et au format |
| Résultat d'exécution | Validation des conditions UTXO et scripts | Exécution de la machine virtuelle et reçus |
| Rétribution | Subvention de bloc et frais revendiqués par la coinbase | Récompenses et mécanismes de frais définis par le protocole actuel |

Cette comparaison ne signifie pas que Bitcoin n'a pas d'état ou qu'Ethereum ne valide pas de transactions. Les deux réseaux maintiennent un état dérivé de l'historique et vérifient leurs règles. Leur structure de données et leur consensus diffèrent.

## 8. Comment un nœud valide un bloc

La validation ne se réduit pas à vérifier que le hash est au bon format. Un nœud suit une procédure déterminée par sa chaîne et son implémentation. Les grandes familles de contrôles comprennent :

1. **Décodage et format.** Les données peuvent-elles être décodées selon les règles de sérialisation attendues ? Les champs obligatoires sont-ils présents et de taille acceptable ?
2. **Référence au parent.** Le parent est-il connu et valide ? La hauteur, le slot ou les données de branche sont-ils cohérents ?
3. **Limites structurelles.** Le bloc respecte-t-il les limites de poids, de gaz, de données, de nombre de transactions et les contraintes spécifiques ?
4. **Engagements cryptographiques.** Les racines correspondent-elles aux données présentées ?
5. **Transactions.** Les signatures, nonces, entrées, sorties, frais et autres règles de validation sont-ils corrects ?
6. **Transition d'état.** En appliquant les transactions dans l'ordre aux données du parent, le nœud obtient-il l'état attendu ?
7. **Consensus.** Le bloc satisfait-il le mécanisme de production et les règles de sélection ou de finalité du réseau ?
8. **Contexte et politique.** Le nœud décide comment stocker, propager et sélectionner le bloc selon le protocole et ses politiques locales.

Toutes les chaînes ne procèdent pas dans exactement cet ordre ni avec les mêmes contrôles. Certains vérifications peuvent être effectuées à des étapes distinctes ou partagées entre clients. La liste sert de modèle mental, pas de spécification complète d'un client précis.

~~~mermaid
flowchart TD
    A["Réception d'un bloc"] --> B["Décodage et contrôles de format"]
    B -->|Échec| X["Rejet ou mise en attente"]
    B --> C["Vérifier le parent et les limites"]
    C -->|Échec| X
    C --> D["Vérifier les engagements"]
    D -->|Échec| X
    D --> E["Valider et exécuter les transactions"]
    E -->|Échec| X
    E --> F["Vérifier les règles de consensus"]
    F -->|Échec| X
    F --> G["Accepter dans la chaîne suivie"]
    G --> H["Partager et mettre à jour l'état local"]
~~~

La validation est déterministe dans le sens où des nœuds conformes qui reçoivent le même état de départ et les mêmes données valides devraient appliquer les mêmes règles et calculer le même résultat. Si des implémentations se comportent différemment sur un cas limite, elles peuvent diverger ; c'est pourquoi les spécifications, les tests croisés et les clients indépendants sont importants.

## 9. Production, diffusion et inclusion

Le processus typique se déroule ainsi :

- Un utilisateur crée une transaction, qui est signée par le moyen d'autorisation approprié.
- La transaction est diffusée vers un ou plusieurs nœuds, qui la vérifient et peuvent la garder dans leur mempool ou ensemble de transactions en attente.
- Un producteur de bloc sélectionne certaines transactions qui respectent les règles et construit un bloc candidat.
- Il construit les engagements nécessaires et effectue les opérations de consensus prévues.
- Le bloc est transmis aux pairs.
- Les nœuds reçoivent le bloc, le vérifient indépendamment et mettent à jour leur vue du réseau s'il est valide et si les règles de consensus le conduisent à être suivi.

Une transaction dans le mempool n'est pas encore dans un bloc. Une transaction dans un bloc récemment produit n'est pas nécessairement finale. Une transaction peut être remplacée, abandonnée ou non incluse selon les règles et les événements du réseau. L'interface d'un portefeuille peut afficher un statut optimiste qui doit être interprété avec le niveau de confirmation.

~~~mermaid
sequenceDiagram
    participant U as Utilisateur
    participant N1 as Nœud receveur
    participant P as Producteur de bloc
    participant N2 as Autre nœud
    U->>N1: Transaction signée
    N1->>N1: Vérification initiale
    N1-->>P: Relais possible
    P->>P: Sélection et assemblage
    P->>N2: Bloc candidat
    N2->>N2: Validation indépendante
    N2-->>N2: Mettre à jour la chaîne si les règles le permettent
~~~

## 10. Confirmations, réorganisations et finalité

### 10.1 Confirmations dans Bitcoin

Dans Bitcoin, une transaction peut être considérée comme ayant une confirmation quand elle est incluse dans un bloc valide de la chaîne suivie. Chaque bloc supplémentaire qui s'appuie sur celui-ci augmente le nombre de confirmations. Le risque d'une réorganisation dépend du contexte, de la sécurité de la chaîne, du comportement des mineurs et de la profondeur observée. Dire qu'une transaction est « irréversible après exactement six blocs » est une simplification : six confirmations sont une convention utilisée dans certains contextes, pas une loi universelle qui garantit un risque nul.

Une transaction non confirmée peut être remplacée ou rester en attente. Une transaction confirmée peut être affectée par une réorganisation. Les entreprises choisissent des seuils de confirmations adaptés à la valeur et au risque, au lieu d'utiliser une règle identique pour tout paiement.

### 10.2 Finalité dans Ethereum

Ethereum emploie un mécanisme de consensus à preuve d'enjeu et une notion de finalité qui se distingue des confirmations probabilistes souvent discutées pour Bitcoin. Les validateurs votent sur les blocs ou les checkpoints selon les règles du protocole. La finalité est atteinte selon les conditions de consensus correspondantes, mais elle repose sur des hypothèses, notamment relatives aux validateurs, à la connectivité et aux règles de slashing. Un bloc finalisé est beaucoup plus difficile à révoquer que la simple présence d'un bloc récent, sans que cela signifie que toute couche applicative ou tout fournisseur soit exempt de risque.

Il faut donc distinguer le statut « proposé », le statut « inclus », les confirmations observées et la finalité selon le protocole. Une interface peut les simplifier en une seule étiquette, ce qui est pratique mais insuffisant pour une décision opérationnelle critique.

### 10.3 Réorganisation de chaîne

Une réorganisation survient quand la branche retenue par un nœud change et que certains blocs précédemment suivis cessent d'appartenir à l'historique sélectionné. Les transactions de ces blocs peuvent réapparaître dans l'ensemble des transactions en attente, être incluses plus tard ou devenir incompatibles avec le nouvel état. Une opération qui semblait confirmée peut donc changer de statut si le bloc qui la contenait est retiré de la branche suivie.

Une réorganisation n'est pas automatiquement une attaque. Elle peut résulter de la propagation et de la concurrence ordinaires des blocs. Une réorganisation profonde ou inhabituelle doit cependant être traitée comme un signal d'investigation. Il faut observer les données du réseau, les clients utilisés et l'état de consensus avant d'en tirer une conclusion.

## 11. Erreurs fréquentes d'interprétation

### « Le hash du bloc est la racine de Merkle »

Faux. Dans Bitcoin, la racine de Merkle est un champ de l'en-tête. Le hash de bloc est calculé à partir de l'en-tête complet selon les règles du protocole. Dans Ethereum, les champs d'engagement sont différents et il ne faut pas copier le modèle Bitcoin tel quel.

### « Un bloc contient le solde de chaque utilisateur »

C'est trompeur. Dans Bitcoin, le nœud reconstruit l'ensemble des sorties non dépensées en validant les transactions. Dans Ethereum, l'état des comptes et des contrats est résumé par une structure d'état dont la racine est engagée dans le bloc. L'état n'est pas simplement une liste de soldes mise directement dans chaque bloc.

### « Une transaction présente dans un bloc a réussi »

Cela dépend du sens de « réussir ». La transaction peut être valide et incluse au niveau du protocole, alors que l'exécution d'un contrat dans Ethereum se termine par un statut d'échec. Il faut consulter le reçu, les événements et l'état obtenu, pas uniquement la présence dans la liste des transactions.

### « Une preuve de travail prouve que toutes les transactions sont correctes »

La preuve de travail répond à un problème de consensus et de sélection de l'historique. Un nœud valide les transactions et les règles indépendamment ; un hash répondant à la cible ne rend pas acceptables des transactions invalides. Un bloc avec une preuve de travail correcte mais une transaction invalide doit être rejeté.

### « Un horodatage est une preuve exacte de l'heure »

Non. C'est un champ contraint par le protocole, mais l'heure déclarée ne constitue pas une horloge mondiale parfaitement synchronisée. Il faut examiner le fonctionnement du réseau et les limites d'horodatage.

## 12. TP guidé A : inspection conceptuelle d'un bloc Bitcoin

### Objectif

Savoir identifier les éléments clés d'un bloc à partir d'une fiche descriptive ou d'un explorateur public. Le TP ne demande pas de dépenser de fonds, de lancer un mineur ou de modifier une blockchain.

### Étape 1 — Choisir un bloc

Ouvre un explorateur réputé en lecture seule et sélectionne un bloc ancien ou récent. Vérifie que tu consultes le réseau Bitcoin et non un réseau de test ou une chaîne alternative. Note la hauteur, le hash du bloc et le hash du parent.

### Étape 2 — Repérer l'en-tête

Relève la version, l'horodatage, la cible encodée et le nonce lorsque l'explorateur les affiche. Vérifie si l'outil montre des valeurs formatées ou une sérialisation brute. Ne compare pas directement des chaînes hexadécimales sans comprendre la convention d'affichage.

### Étape 3 — Examiner les transactions

Compte les transactions et repère la transaction coinbase. Observe les frais et le poids de quelques transactions. Tu n'as pas besoin de décoder toutes les sorties : identifie simplement comment le bloc engage la liste des transactions et comment le producteur récupère les frais selon les règles.

### Étape 4 — Écrire un compte rendu

Crée un tableau avec les colonnes : champ, valeur affichée, rôle et contrôle qu'un nœud pourrait effectuer. Le compte rendu doit inclure au moins six lignes, notamment le parent, la racine de Merkle, l'horodatage, la cible, le nonce et le nombre de transactions.

**Corrigé attendu :** Le hash du parent rattache le bloc à l'historique ; la racine de Merkle engage les transactions ; l'horodatage indique le temps déclaré soumis aux règles ; la cible fixe les exigences de preuve de travail ; le nonce est une donnée parmi celles utilisées pour chercher une preuve valide ; le compteur et la liste de transactions permettent de reconstruire le corps du bloc. Les valeurs concrètes dépendent du bloc choisi, l'important est de les interpréter correctement.

## 13. TP guidé B : lire un bloc Ethereum sans confondre les racines

### Objectif

Reconnaître les informations qui décrivent l'en-tête, les transactions, les reçus et l'état d'Ethereum.

### Étape 1 — Choisir un bloc

Utilise un explorateur Ethereum en mode lecture seule. Note le numéro de bloc, le parent hash et l'horodatage. Il est préférable de prendre un bloc finalisé et d'utiliser un explorateur qui indique la signification des champs.

### Étape 2 — Étudier trois transactions

Pour trois transactions, note l'expéditeur, le destinataire ou l'adresse de contrat, le gaz utilisé, les frais et le statut du reçu. Vérifie qu'un statut d'échec de contrat ne signifie pas automatiquement que la transaction entière était mal formée.

### Étape 3 — Comparer les racines

Repère, dans les données techniques lorsqu'elles sont exposées, la state root, la transactions root et la receipts root. Écris une phrase pour chacune : l'une engage l'état résultant, l'autre la liste des transactions, la troisième les reçus d'exécution. Ne tente pas de recalculer les racines à partir d'un JSON simplifié sans respecter l'encodage du protocole.

### Étape 4 — Préparer le diagnostic

Réponds à cette question : « Si une transaction échoue, quel champ ou quelle donnée faut-il regarder pour comprendre ce qui s'est passé ? » Une réponse utile mentionne le reçu, le gaz consommé, les données d'appel et éventuellement les traces d'exécution, tout en distinguant les outils de diagnostic des données normatives du protocole.

## 14. Dix questions d'entraînement avec corrigé

### Question 1
Pourquoi le bloc de genèse est-il particulier ?

**Corrigé :** Il constitue le point de départ de l'historique et ne référence pas un bloc parent ordinaire. Les paramètres de lancement et les logiciels du réseau définissent comment il est reconnu.

### Question 2
Quel est le rôle du hash du parent ?

**Corrigé :** Il lie le bloc actuel à un bloc précédent particulier. Une modification du parent change son hash et rompt la correspondance de la référence dans le bloc enfant.

### Question 3
La racine de Merkle est-elle le hash complet du bloc Bitcoin ?

**Corrigé :** Non. C'est un champ de l'en-tête qui engage les transactions. Le hash du bloc est calculé à partir de l'en-tête complet selon les règles du protocole.

### Question 4
À quoi sert le champ nBits dans Bitcoin ?

**Corrigé :** Il encode de façon compacte la cible de preuve de travail que doit respecter le hash de l'en-tête.

### Question 5
Quel est le rôle de la transaction coinbase Bitcoin ?

**Corrigé :** Elle permet au producteur du bloc de réclamer la subvention de bloc et les frais admissibles. Elle est spéciale et soumise aux règles monétaires du protocole.

### Question 6
Pourquoi la taille en octets ne suffit-elle pas pour décrire la capacité de Bitcoin ?

**Corrigé :** Le protocole utilise le poids de bloc qui traite les données témoins et non témoins selon des facteurs distincts. Les politiques de relais et la demande influencent aussi l'expérience de capacité.

### Question 7
Quelle est la différence entre transactions root et state root dans Ethereum ?

**Corrigé :** La transactions root engage la liste des transactions ; la state root engage l'état obtenu après l'application des règles et des transactions au bloc parent.

### Question 8
Une transaction incluse dans Ethereum a-t-elle nécessairement réussi son exécution ?

**Corrigé :** Non. Une transaction peut être incluse et valide au niveau du protocole tout en terminant par un statut d'échec d'exécution de contrat. Il faut consulter le reçu.

### Question 9
Pourquoi un bloc avec une preuve de travail valide peut-il être rejeté ?

**Corrigé :** La preuve de travail n'est qu'un élément. Le bloc doit également respecter le format, les engagements, les transactions, les limites et les autres règles de consensus.

### Question 10
Qu'est-ce qu'une réorganisation ?

**Corrigé :** C'est un changement de branche suivie par un nœud, qui peut retirer de l'historique actif certains blocs précédemment observés et modifier le statut de transactions non finalisées.

## 15. Challenge final : diagnostiquer un bloc candidat

### Scénario

Une équipe exploite un explorateur interne. Un nouveau bloc candidat est reçu. Le hash de son en-tête respecte la cible annoncée, mais la racine de Merkle ne correspond pas aux transactions transmises. Un collègue affirme que le bloc devrait tout de même être accepté puisqu'il possède une preuve de travail valide.

### Travail demandé

Rédige un compte rendu de 400 à 600 mots qui :

- explique pourquoi la preuve de travail ne remplace pas les autres validations ;
- décrit les contrôles à effectuer avant d'accepter le bloc ;
- identifie les causes possibles d'une racine de Merkle incohérente ;
- différencie une erreur d'encodage ou de données d'une attaque confirmée ;
- propose une procédure de diagnostic qui préserve les journaux et évite une modification manuelle du bloc.

### Correction proposée

Le bloc ne doit pas être accepté seulement parce que son en-tête satisfait la cible. Dans Bitcoin, le hash de l'en-tête et la racine de Merkle remplissent des rôles différents. La preuve de travail vérifie que le producteur a trouvé un en-tête répondant à une condition de calcul ; elle ne prouve pas que le corps du bloc correspond à cet en-tête ni que toutes les transactions sont valides. Si la racine calculée depuis la liste de transactions ne correspond pas à la racine de l'en-tête, le nœud ne peut pas vérifier l'engagement annoncé.

La première étape est de conserver le bloc brut, l'identifiant du pair qui l'a transmis, l'heure de réception et les journaux de validation. Il faut ensuite vérifier que les données ont été décodées selon le bon format, que l'ordre des transactions n'a pas été changé et que le calcul applique exactement les règles de Merkle du protocole. Une erreur de sérialisation, un troncage du corps, une conversion incorrecte des octets ou un logiciel défectueux peuvent produire une incohérence sans démontrer à eux seuls une attaque.

Si le décodage est correct, le client doit recalculer l'engagement depuis les transactions et comparer le résultat à l'en-tête. Le bloc doit être rejeté ou traité selon les règles du client si l'incohérence persiste. L'équipe ne doit pas modifier manuellement la racine ou le corps dans l'objectif de faire passer le bloc : cela construirait un objet différent du bloc reçu et masquerait potentiellement la cause.

Le diagnostic doit enfin comparer les données reçues auprès de plusieurs pairs indépendants, examiner la version de l'implémentation, reproduire le problème avec un outil de validation conforme et vérifier si d'autres clients observent la même anomalie. L'équipe peut ensuite déterminer s'il s'agit d'un problème réseau, d'un bug d'implémentation, d'une erreur de stockage ou d'un comportement malveillant. La réponse correcte est donc de séparer la preuve de travail, l'intégrité de l'engagement, la validité des transactions et le consensus : ces contrôles se complètent et aucun ne remplace les autres.

## Glossaire

**Bloc :** unité structurée de données qui regroupe des opérations et des métadonnées selon un protocole.

**Bloc de genèse :** premier bloc de l'historique d'un réseau.

**Bloc parent :** bloc auquel le nouveau bloc se rattache par une référence définie par le protocole.

**Coinbase :** transaction spéciale de Bitcoin qui réclame la subvention de bloc et les frais admissibles.

**Confirmation :** inclusion d'une transaction dans un bloc, puis approfondissement de son historique par les blocs suivants ; le sens opérationnel du terme dépend du réseau.

**En-tête :** partie du bloc qui contient des métadonnées et engagements cryptographiques.

**Finalité :** état dans lequel le consensus offre les garanties de finalisation définies par le protocole.

**Fork / réorganisation :** branche concurrente ou changement de la branche retenue par un nœud selon les règles de consensus.

**Gas :** unité de ressource facturée dans Ethereum pour l'exécution et certaines opérations.

**Hash du bloc :** identifiant cryptographique calculé à partir des données prévues par le protocole, souvent à partir de l'en-tête.

**Mempool :** ensemble local de transactions en attente qu'un nœud connaît et peut relayer ; ce n'est pas une liste globale identique sur tous les nœuds.

**Nonce :** champ ou valeur utilisée dans des mécanismes du protocole ; dans l'en-tête Bitcoin, c'est une donnée modifiée pour chercher une preuve de travail. Le terme possède d'autres significations dans Ethereum et les transactions.

**Racine de Merkle :** empreinte racine qui engage un ensemble ordonné de données selon une structure de Merkle.

**Receipts root :** engagement cryptographique envers les reçus d'exécution d'un bloc Ethereum.

**State root :** engagement envers l'état résultant d'un bloc Ethereum.

**Transactions root :** engagement envers les transactions incluses dans un bloc Ethereum.

**UTXO :** sortie de transaction non dépensée que les transactions Bitcoin peuvent consommer.

**Poids de bloc :** mesure utilisée par Bitcoin pour appliquer des limites qui tiennent compte de catégories de données différentes.

## Pour aller plus loin

- Guide de développement Bitcoin : https://developer.bitcoin.org/devguide/block_chain.html
- Référence pour développeurs Bitcoin : https://developer.bitcoin.org/reference/
- Documentation de développement Ethereum : https://ethereum.org/developers/docs/blocks/
- Documentation Ethereum sur les transactions : https://ethereum.org/developers/docs/transactions/
- Documentation Ethereum sur le gaz : https://ethereum.org/developers/docs/gas/

Pour investiguer un bloc réel, conserve toujours le réseau, la hauteur, l'identifiant du bloc, le parent et les champs exacts consultés. Un explorateur est pratique, mais la validation de production repose sur un client conforme et sur les données qu'il vérifie, pas seulement sur l'apparence d'une page web.
