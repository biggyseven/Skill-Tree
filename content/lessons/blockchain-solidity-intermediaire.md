# Solidity (langage)

## Encadré de mise en contexte

Solidity est un langage de programmation conçu principalement pour écrire des smart contracts destinés à l'Ethereum Virtual Machine (EVM) et aux réseaux compatibles. Il reprend des éléments familiers aux développeurs — types, variables, fonctions, conditions, structures et événements — tout en intégrant des contraintes particulières aux programmes exécutés dans une blockchain : état persistant, appels entre contrats, permissions, données publiques, coûts de gaz et difficultés de mise à jour.

Un contrat Solidity n'est pas un serveur classique. Il est compilé en bytecode, déployé sur une chaîne et exécuté selon les règles du réseau lorsque des appels ou transactions le sollicitent. Une erreur peut donc avoir des conséquences difficiles à réparer, surtout si le contrat contrôle des actifs et ne dispose pas d'une procédure de mise à niveau. Apprendre la syntaxe ne suffit pas : il faut simultanément apprendre à raisonner sur les permissions, les invariants, le coût d'exécution et les attaques possibles.

Ce cours constitue une première entrée pratique dans Solidity. Il couvre la structure d'un contrat, les types, l'état, les fonctions, les modificateurs, les événements, les mappings, les tableaux, les erreurs, les transferts de valeur, les tests et les bonnes pratiques de sécurité. Il prépare au cours suivant sur l'EVM et le gaz. Les exemples sont pédagogiques : ils doivent être testés dans un environnement local avant toute utilisation et ne constituent pas des contrats financiers prêts pour la production.

## Objectifs d'apprentissage

À la fin de la leçon, tu sauras :

- lire la structure d'un fichier Solidity ;
- comprendre le rôle du pragma, des contrats, des variables et des fonctions ;
- choisir des types adaptés aux données ;
- distinguer état persistant, mémoire temporaire et données d'appel ;
- utiliser visibilité, modificateurs, événements et erreurs ;
- expliquer les mappings, tableaux, structures et énumérations ;
- comprendre les appels, les retours et les erreurs d'exécution ;
- écrire des tests de comportement simples et identifier des invariants ;
- éviter plusieurs erreurs de sécurité courantes ;
- développer un contrat simple de suivi de dépôts fictifs sans prétendre qu'il est adapté à de vrais fonds.

## 1. Outils et versions

Pour compiler Solidity, il faut un compilateur compatible avec la version ciblée. Il existe des environnements intégrés comme Remix et des outils de développement qui permettent de compiler, tester, déployer sur un réseau local et analyser les résultats. Le choix de l'outil importe moins que la capacité à contrôler la version exacte, inspecter les avertissements et reproduire le build.

Une directive pragma indique les versions de compilateur avec lesquelles le code est destiné à être compatible. Elle ne télécharge pas elle-même le compilateur, ne garantit pas qu'une version soit installée et n'assure pas que le code soit sécurisé. Une plage de versions doit être choisie selon les pratiques du projet et les exigences de reproductibilité.

Pour les exemples de ce cours, la directive indique Solidity 0.8.20 ou une version compatible de la série 0.8. Les versions modernes de Solidity vérifient automatiquement certains débordements arithmétiques dans les expressions ordinaires, contrairement à certaines versions anciennes. Cela ne supprime pas les erreurs de calcul, les conversions risquées ni tous les problèmes de logique. En pratique, utilise une version stable et prise en charge, lis les notes de version et teste les mêmes paramètres de compilation que ceux prévus pour le déploiement.

## 2. Anatomy d'un fichier Solidity

Un fichier Solidity contient souvent des informations de licence, la directive pragma, des imports éventuels, puis un ou plusieurs contrats, bibliothèques ou interfaces. À l'intérieur d'un contrat, on trouve des types, variables d'état, événements, erreurs, modificateurs, constructeurs et fonctions.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Bonjour {
    string private message;

    event MessageChange(address indexed auteur, string nouveauMessage);

    constructor(string memory messageInitial) {
        message = messageInitial;
    }

    function lireMessage() external view returns (string memory) {
        return message;
    }

    function changerMessage(string calldata nouveauMessage) external {
        message = nouveauMessage;
        emit MessageChange(msg.sender, nouveauMessage);
    }
}
~~~

L'exemple contient plusieurs éléments :

- la licence indique les conditions de réutilisation annoncées pour ce fichier ;
- pragma signale la plage de versions de compilateur visée ;
- contract déclare un nouveau contrat ;
- la variable message est un état persistant ;
- le constructeur s'exécute lors de la création et initialise l'état ;
- lireMessage retourne la valeur sans modifier l'état ;
- changerMessage reçoit une donnée et modifie l'état ;
- l'événement MessageChange écrit une trace exploitable par les applications.

Ce contrat est volontairement simple et n'a pas de contrôle d'accès : n'importe quel appelant peut changer le message. C'est acceptable pour une démonstration, mais souvent incorrect pour un système où le message représente une configuration sensible. L'exemple est utile pour lire la syntaxe, pas pour être déployé comme système de production.

### 2.1 Contrat, bibliothèque et interface

Un contrat peut être déployé et posséder un état ou des actifs. Une bibliothèque regroupe une logique réutilisable selon des règles spécifiques et peut être compilée ou appelée de façons qui dépendent du contexte. Une interface décrit des signatures de fonctions et événements que d'autres contrats peuvent implémenter ou appeler.

Une interface ne garantit pas que l'adresse à laquelle l'application se connecte implémente correctement les fonctions décrites. Il faut vérifier l'adresse, le réseau, les règles d'autorisation et la logique réelle. Deux contrats peuvent exposer des signatures ressemblantes tout en ayant des comportements très différents.

## 3. Types de données

Le choix du type détermine les valeurs représentables et influence le stockage et le coût de calcul.

### 3.1 Types élémentaires

Solidity possède notamment des entiers non signés comme uint256, des entiers signés comme int256, des booléens, des adresses et des types de données binaires. Les entiers non signés ne représentent pas de valeurs négatives. Une adresse représente une valeur de 20 octets utilisée dans l'écosystème EVM, mais toutes les adresses ne sont pas nécessairement des comptes contrôlés directement par une personne : certaines sont associées à des contrats.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract TypesDeBase {
    uint256 public compteur;
    int256 public correction;
    bool public actif = true;
    address public administrateur;
    bytes32 public identifiant;

    constructor() {
        administrateur = msg.sender;
        identifiant = keccak256(abi.encode("Skill Tree", block.chainid));
    }

    function ajouter(uint256 quantite) external {
        compteur += quantite;
    }
}
~~~

La variable compteur est publique : le compilateur expose un accesseur automatique qui permet de lire sa valeur, mais cela ne rend pas toutes les écritures publiques. La variable administrateur est initialisée à l'adresse de l'appelant du constructeur. Il faut cependant mettre en œuvre des contrôles d'accès pour empêcher qu'une fonction sensible soit appelée par n'importe qui.

### 3.2 Entiers et conversions

Les calculs doivent tenir compte des limites du type. Une addition ou multiplication qui dépasse la plage d'un uint256 provoque normalement un revert dans le code moderne vérifié par défaut. Une conversion explicite vers un type plus petit peut tronquer ou modifier la représentation si le programme ne contrôle pas la plage. Les conversions doivent être choisies et testées explicitement.

Les calculs financiers doivent également traiter l'arrondi et l'échelle. Beaucoup de montants sont représentés sous forme d'entiers, par exemple en unités minimales d'un jeton. Si le contrat doit calculer un pourcentage, il faut définir une précision, un ordre d'opérations et une politique d'arrondi. Une formule correcte dans un tableur décimal peut être incorrecte lorsqu'elle est réécrite en arithmétique entière.

### 3.3 Adresses et types payable

Le type address désigne une adresse EVM. address payable permet certaines opérations de transfert de valeur native conformément aux règles du langage. Il ne faut pas convertir arbitrairement une adresse en payable simplement pour éviter de comprendre la logique de réception ou les risques d'appel externe. Le choix doit correspondre au rôle de la variable.

Une adresse ne prouve pas l'identité civile de son contrôleur. Elle peut appartenir à un contrat, être gouvernée par plusieurs clés ou être contrôlée par un système automatisé. Les noms humains et les étiquettes affichées par une interface sont des métadonnées en dehors de la valeur brute de l'adresse.

### 3.4 Chaînes et octets

string sert aux chaînes UTF-8, bytes à des séquences d'octets dynamiques et bytes32 à une valeur de taille fixe de 32 octets. Pour certains identifiants ou empreintes, bytes32 convient ; pour du texte arbitraire, string peut être plus approprié. Il faut toutefois considérer la taille de l'information et le coût de stockage permanent.

Stocker un grand document dans l'état de la blockchain peut être très coûteux. Une application peut choisir de stocker un hash ou un identifiant sur chaîne et de conserver le document ailleurs. Ce choix ne garantit pas que le document hors chaîne restera disponible : il faut prévoir l'hébergement, la redondance, les droits d'accès et le format.

### 3.5 Enum et struct

Un enum définit un ensemble fini de valeurs nommées. Une struct regroupe plusieurs champs en un type de donnée.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract SuiviTicket {
    enum Etat { Ouvert, EnCours, Resolu, Ferme }

    struct Ticket {
        address createur;
        uint64 creeLe;
        Etat etat;
        string description;
    }

    mapping(uint256 => Ticket) private tickets;
    uint256 private prochainId;

    event TicketCree(uint256 indexed id, address indexed createur);

    function creer(string calldata description) external returns (uint256 id) {
        id = prochainId;
        prochainId += 1;
        tickets[id] = Ticket(msg.sender, uint64(block.timestamp), Etat.Ouvert, description);
        emit TicketCree(id, msg.sender);
    }
}
~~~

Dans cet extrait, la valeur `Resolu` est maintenant écrite comme un identifiant Solidity valide. L'exemple illustre les structures et les mappings ; pour une application complète, il faut encore définir les transitions autorisées, la lecture des tâches et les tests de permission. Compile toujours le code dans la version ciblée avant de l'intégrer à un projet.

## 4. Variables d'état, memory et calldata

Les variables d'état sont stockées dans l'état persistant du contrat. Les variables locales vivent seulement pendant l'exécution, sauf si elles sont utilisées pour mettre à jour l'état. Pour les types dynamiques comme string, bytes ou les tableaux, le lieu des données compte.

- storage désigne les données persistantes stockées dans l'état du contrat.
- memory désigne des données temporaires créées pour la durée d'une exécution.
- calldata désigne les données d'entrée de la fonction externe, en lecture seule dans les contextes habituels.

Le compilateur impose les emplacements appropriés selon le type et le contexte. Une fonction qui reçoit une chaîne et ne doit pas la modifier peut souvent utiliser calldata ; un constructeur ou une fonction qui doit construire une valeur temporaire peut employer memory. Les détails influencent les copies, le coût et la disponibilité des données, mais les développeurs doivent d'abord choisir le bon comportement sémantique.

~~~mermaid
flowchart TD
    A["Données de la transaction"] --> C["calldata : entrée de fonction"]
    C --> M["memory : traitement temporaire possible"]
    M --> S["storage : état persistant si une écriture est effectuée"]
    S --> R["Nouvel état après transaction réussie"]
~~~

L'état de stockage ne devrait pas être modifié par des opérations de lecture seulement. Un contrat peut retourner une vue de ses données, mais il ne faut pas supposer que le résultat d'une lecture est un engagement immuable si la chaîne continue à évoluer. Le bloc choisi pour la lecture et l'état au moment de la requête doivent être pris en compte par l'application.

## 5. Fonctions, visibilité et mutabilité

Les fonctions définissent les actions offertes par un contrat. La visibilité distingue notamment les fonctions accessibles depuis l'extérieur et celles accessibles seulement depuis le contrat ou ses dérivés. external est généralement utilisé pour une fonction appelée depuis l'extérieur du contrat ; public permet aussi les appels internes selon les règles du langage. private limite l'accès au contrat lui-même, tandis que internal permet également l'accès depuis les contrats dérivés.

Les marqueurs de mutabilité indiquent comment la fonction peut interagir avec l'état :
- view indique que la fonction ne modifie pas l'état persistant ;
- pure indique qu'elle ne lit ni ne modifie l'état persistant selon les règles du langage ;
- une fonction sans ces marqueurs peut modifier l'état ;
- payable permet à une fonction de recevoir la valeur native avec l'appel.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Calculatrice {
    function additionner(uint256 a, uint256 b) external pure returns (uint256) {
        return a + b;
    }

    uint256 private total;

    function lireTotal() external view returns (uint256) {
        return total;
    }

    function definirTotal(uint256 nouveauTotal) external {
        total = nouveauTotal;
    }
}
~~~

### 5.1 Constructeur

Le constructeur s'exécute lors du déploiement du contrat et initialise souvent les paramètres ou le rôle initial. Il n'est pas appelé comme une fonction publique ordinaire après le déploiement. Les arguments de constructeur sont encodés dans les données de création lors du déploiement, ce qui doit être pris en compte lors de la vérification de source.

Le constructeur ne doit pas configurer par défaut un pouvoir d'administration sans réfléchir au transfert, à la rotation ou à la perte de la clé. Si un administrateur unique est compromis, un ensemble de fonctions protégées peut être compromis avec lui. Il peut être préférable d'utiliser une multisignature ou des rôles qui séparent les responsabilités, selon les besoins.

### 5.2 Modificateurs

Un modificateur permet de réutiliser une condition ou une logique qui entoure une fonction. Il est souvent utilisé pour vérifier les permissions ou l'état du contrat. Les modificateurs réduisent certaines répétitions, mais leur logique doit rester lisible, car ils peuvent masquer des contrôles importants aux lecteurs moins expérimentés.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RegistreAdmin {
    address public proprietaire;

    constructor() {
        proprietaire = msg.sender;
    }

    modifier seulementProprietaire() {
        require(msg.sender == proprietaire, "Acces refuse");
        _;
    }

    function transfererPropriete(address nouveauProprietaire)
        external
        seulementProprietaire
    {
        require(nouveauProprietaire != address(0), "Adresse nulle");
        proprietaire = nouveauProprietaire;
    }
}
~~~

La ligne avec le symbole de continuation indique l'endroit où le corps de la fonction est exécuté après que la condition du modificateur a réussi. Le code reste pédagogique : dans un vrai système, il faut réfléchir à la procédure de récupération du propriétaire, à un éventuel contrôle multisignature et aux tests des comptes non autorisés.

## 6. Conditions, boucles et erreurs

Les instructions conditionnelles permettent de choisir le comportement en fonction des données et de l'état. Les boucles parcourent des collections ou répètent des opérations, mais leur coût peut croître avec leur nombre d'itérations. Une boucle sur une liste contrôlée par les utilisateurs peut rendre une fonction trop chère à exécuter quand la liste grandit.

Les fonctions de validation utilisent souvent require pour vérifier une précondition, revert pour interrompre explicitement une opération ou des erreurs personnalisées pour décrire les échecs. Une transaction qui revert n'applique pas les changements d'état de cette exécution ; néanmoins, le travail déjà effectué peut être facturé en gaz selon les règles de la machine virtuelle.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Limites {
    error QuantiteNulle();
    error QuantiteTropGrande(uint256 maximale);

    uint256 public constant LIMITE = 1000;

    function valider(uint256 quantite) external pure returns (bool) {
        if (quantite == 0) {
            revert QuantiteNulle();
        }
        if (quantite > LIMITE) {
            revert QuantiteTropGrande(LIMITE);
        }
        return true;
    }
}
~~~

Les erreurs personnalisées peuvent réduire le coût et fournir une information plus structurée que de longs messages de texte. Elles ne doivent pas révéler des informations sensibles et l'application cliente doit savoir les décoder si elle veut afficher un message compréhensible.

## 7. Mappings, tableaux et structures

Un mapping associe une clé à une valeur. Il est utile pour retrouver le solde d'un utilisateur, une configuration par identifiant ou une permission. Un mapping n'offre pas automatiquement une liste de toutes ses clés : il est possible de lire une valeur pour une clé connue, mais il faut maintenir un index séparé si le contrat doit parcourir les utilisateurs enregistrés.

Un tableau peut être de taille fixe ou dynamique. Les tableaux dynamiques dans le stockage persistent entre les transactions et peuvent devenir coûteux à parcourir. Les développeurs doivent réfléchir à la taille maximale, à la pagination et à la possibilité pour un utilisateur de bloquer une fonction collective en augmentant une liste.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Carnet {
    struct Profil {
        bool inscrit;
        uint64 dateInscription;
    }

    mapping(address => Profil) private profils;
    address[] private membres;

    event Inscription(address indexed compte);

    function inscrire() external {
        require(!profils[msg.sender].inscrit, "Deja inscrit");
        profils[msg.sender] = Profil(true, uint64(block.timestamp));
        membres.push(msg.sender);
        emit Inscription(msg.sender);
    }

    function lireProfil(address compte) external view returns (Profil memory) {
        return profils[compte];
    }

    function nombreMembres() external view returns (uint256) {
        return membres.length;
    }
}
~~~

Le contrat enregistre chaque compte une seule fois et conserve une liste des membres. Ce mécanisme est utile pour un exercice, mais parcourir toute la liste dans une fonction d'écriture deviendrait risqué à mesure qu'elle grandit. Pour une application d'analyse, il peut être plus efficace d'indexer les événements hors chaîne plutôt que d'essayer d'effectuer toutes les recherches dans le contrat.

## 8. Événements et observabilité

Les événements rendent les actions observables pour les applications externes. Le mot-clé indexed permet de rendre certains arguments plus faciles à filtrer dans les journaux. Les événements sont utiles pour construire des historiques, mais ils ne doivent pas être confondus avec un état accessible directement par le code du contrat.

Une application écoute souvent les événements ou les interroge à travers un indexeur. Elle doit traiter les réorganisations et la finalité : un événement observé dans un bloc récent peut disparaître de l'historique suivi si la chaîne se réorganise. L'interface doit éviter d'annoncer un résultat définitif trop tôt pour une opération critique.

Un événement est une trace, pas une preuve générale que l'application entière s'est comportée correctement. Il faut vérifier la transaction, son reçu, son état final et le contrat émetteur. Des contrats malveillants peuvent émettre des événements trompeurs si l'application ne vérifie pas l'adresse et la logique source.

## 9. Recevoir et transférer la valeur native

Un contrat peut être conçu pour recevoir de l'ETH selon les règles de Solidity et de l'EVM. Une fonction payable peut recevoir une valeur attachée à l'appel. Les contrats doivent définir ce qu'ils font de cette valeur, comment ils la comptabilisent et dans quelles conditions ils autorisent un retrait.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CoffrePedagogique {
    mapping(address => uint256) public depots;

    event Depot(address indexed utilisateur, uint256 montant);

    function deposer() external payable {
        require(msg.value > 0, "Depot nul");
        depots[msg.sender] += msg.value;
        emit Depot(msg.sender, msg.value);
    }
}
~~~

Cet extrait illustre seulement la comptabilisation des dépôts. Il ne comporte pas de fonction de retrait et ne doit pas être utilisé pour recevoir de vrais fonds. Un contrat qui détient de la valeur doit prévoir un chemin de retrait testé, un comportement clair en cas d'erreur, une comptabilité cohérente et une revue de sécurité.

Les transferts de valeur impliquent des interactions externes et des risques de réentrance. Avant d'effectuer un appel vers une autre adresse, le contrat doit considérer ce qui se produit si le destinataire est un contrat hostile, s'il échoue ou s'il rappelle le contrat. Le modèle Checks-Effects-Interactions recommande de vérifier les conditions, mettre à jour l'état, puis effectuer l'interaction externe, tout en testant les cas particuliers.

## 10. Sécurité : éviter les erreurs courantes

### 10.1 Contrôle d'accès absent

Une fonction qui modifie le propriétaire, le taux d'intérêt ou une adresse oracle doit avoir une règle de permission explicite. Le fait que l'interface ne montre pas le bouton aux utilisateurs ordinaires n'empêche pas l'appel direct de la fonction. Les permissions doivent être contrôlées dans le contrat.

### 10.2 Réentrance

Lorsqu'un contrat appelle un tiers, le contrôle peut être transféré à un autre contrat qui appelle ensuite le premier. Si l'état interne n'a pas été mis à jour dans le bon ordre, un retrait ou une opération peut être répété. Les développeurs doivent dessiner les flux d'appels, utiliser un ordre sûr des opérations et comprendre les retours et callbacks.

### 10.3 Hypothèses sur le monde extérieur

Ne pas utiliser block.timestamp comme source d'une horloge ultra précise ou d'un tirage au sort sécurisé. L'horodatage est défini et contraint par le protocole, mais il n'est pas une source parfaite pour tous les usages. Les applications qui dépendent de prix, de données météorologiques ou d'événements physiques ont besoin d'un mécanisme d'oracle et d'une politique pour les données périmées.

### 10.4 Erreurs de calcul

Les arrondis, les conversions, les divisions et l'ordre des opérations doivent être analysés. Un calcul qui arrondit systématiquement vers le bas peut déplacer de petites quantités de valeur. Les quantités doivent être représentées dans des unités bien définies et les limites testées.

### 10.5 Dépendances et mises à niveau

Une bibliothèque doit être prise depuis une source fiable, dans une version connue, puis testée avec les paramètres utilisés. Une dépendance externe peut changer, être mal configurée ou exposer un mécanisme d'administration. Une mise à jour peut corriger une vulnérabilité, mais peut aussi introduire un changement incompatible. Les dépendances et pouvoirs d'administration doivent être documentés.

### 10.6 Confidentialité inexistante par défaut

Les données inscrites sur une blockchain publique peuvent être examinées par des observateurs. Ne publie pas de mots de passe, de secrets d'entreprise ou d'informations personnelles dans le stockage ou les événements. Un hash n'offre pas nécessairement de confidentialité lorsque la valeur initiale a peu de possibilités.

## 11. Tests et méthode de développement

Un contrat doit être testé sur des scénarios normaux et adverses. Les tests unitaires isolent les fonctions ; les tests d'intégration vérifient les interactions entre contrats ; le fuzzing explore des entrées variées ; les tests de propriétés vérifient des invariants. Les outils d'analyse statique peuvent signaler des motifs suspects, mais ils peuvent produire des faux positifs et manquer des bugs logiques.

Pour un coffre, les tests devraient couvrir le dépôt nul, le dépôt positif, le retrait partiel, le retrait complet, le retrait supérieur au solde, l'appel par un compte sans permission, le transfert qui échoue, la réentrance et les limites de gaz. Un test qui vérifie uniquement le chemin réussi ne suffit pas.

~~~mermaid
flowchart TD
    S["Spécification et invariants"] --> U["Tests unitaires"]
    U --> I["Tests d'intégration"]
    I --> F["Fuzzing et tests de propriétés"]
    F --> A["Analyse statique et revue de code"]
    A --> D["Déploiement sur réseau de test"]
    D --> M["Surveillance et procédure d'urgence"]
~~~

### 11.1 Avertissements du compilateur

Les avertissements du compilateur doivent être lus et résolus ou justifiés explicitement. La compilation réussie ne signifie pas que le programme est sûr. Un avertissement peut signaler un code inaccessible, une conversion dangereuse ou une intention ambiguë. Il faut également verrouiller la version du compilateur et les dépendances afin que les résultats soient reproductibles.

### 11.2 Test des permissions

Les tests doivent changer l'identité de l'appelant. Si tu testes une fonction administrative uniquement avec le compte propriétaire, tu n'as pas testé que l'accès est refusé aux autres. Les cas non autorisés sont aussi importants que les cas réussis. Les rôles doivent être testés aux frontières : transfert de propriété, rôle nul, compte perdu, appel répété et interaction avec un contrat externe.

### 11.3 Déploiement et vérification

Une fois le contrat compilé et testé, il peut être déployé sur un réseau local ou de test. Conserve le code source, la version du compilateur, les paramètres d'optimisation, les bibliothèques, l'ABI et le bytecode de création. Après le déploiement, vérifie l'adresse et le bytecode attendu. Les outils de vérification de source facilitent la comparaison publique entre le code annoncé et le code exécuté.

## 12. Concevoir les données avant les fonctions

Un contrat lisible commence par un modèle de données qui représente précisément le besoin. Pour un registre de tâches, il faut décider si chaque tâche possède un créateur, un état, une date, une description et une date de clôture. Pour un coffre, les données peuvent être le solde par utilisateur, les paramètres de pause et les rôles. Ces choix conditionnent les invariants et les tests.

Un mapping convient aux recherches par clé, par exemple \`mapping(address => uint256)\` pour un solde. Il ne fournit pas nativement une liste itérable de toutes les clés. Si le contrat doit afficher le nombre de tâches, le simple fait de posséder \`mapping(uint256 => Task)\` ne suffit pas : il faut aussi conserver un compteur ou un index séparé. Ce compteur doit être mis à jour exactement une fois lors d'une création réussie.

Un tableau dynamique conserve un ordre et permet l'accès par index, mais il peut devenir coûteux à parcourir. Une fonction d'écriture qui boucle sur toutes les tâches pourrait finir par dépasser la limite de gas. Il faut se demander si la recherche doit être réalisée on-chain ou par un indexeur hors chaîne qui écoute les événements.

~~~mermaid
flowchart TD
    R["Besoin métier"] --> Q{"Recherche par clé ou parcours complet ?"}
    Q -->|Par clé| M["Mapping"]
    Q -->|Par index ou ordre| A["Tableau"]
    M --> I["Ajouter un index séparé si nécessaire"]
    A --> L["Éviter les boucles d'écriture non bornées"]
    I --> T["Définir invariants et tests"]
    L --> T
~~~

Un bon modèle de données inclut aussi les états impossibles. Par exemple, une tâche ne doit pas être « terminée » avant d'exister ; un retrait ne doit pas faire passer un solde sous zéro ; une demande qui a déjà été consommée ne doit pas être traitée une seconde fois. Ces propriétés doivent être visibles dans la spécification avant d'écrire les fonctions.

### Exemple de décision de conception

| Besoin | Structure potentielle | Point à vérifier |
|---|---|---|
| Lire le solde d'une adresse connue | Mapping | Le mapping ne liste pas tous les utilisateurs |
| Lire une tâche par identifiant | Mapping de struct | Prévoir les identifiants inexistants |
| Afficher les dernières tâches | Tableau ou indexeur | Définir pagination et ordre |
| Suivre les changements dans l'interface | Événements | Gérer les réorganisations et doublons |
| Empêcher la duplication d'une action | Mapping de drapeaux ou état dédié | Mettre le drapeau à jour dans le bon ordre |

Les structures doivent être adaptées au modèle d'accès réel. Ne choisis pas un tableau uniquement parce qu'il est facile à expliquer, ni un mapping uniquement parce qu'il semble rapide. Le contrat paie le coût des données persistantes et doit pouvoir être utilisé à mesure que le volume augmente.

## 13. Exemple corrigé et compilable : registre de tâches

Le contrat ci-dessous est un exemple pédagogique complet pour illustrer une struct, un enum, un mapping, un compteur, des événements et un contrôle d'accès au niveau d'une tâche. Il n'utilise aucun jeton et n'envoie aucune valeur native. Il constitue un bon exercice pour tester la logique avant de l'élargir.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract RegistreTaches {
    enum Etat { Ouverte, EnCours, Terminee, Annulee }

    struct Tache {
        address createur;
        string titre;
        uint64 creeeLe;
        Etat etat;
    }

    mapping(uint256 => Tache) private taches;
    uint256 public prochainId;

    event TacheCreee(uint256 indexed id, address indexed createur, string titre);
    event EtatModifie(uint256 indexed id, Etat ancienEtat, Etat nouvelEtat);

    error TacheInexistante(uint256 id);
    error AppelantNonAutorise();
    error TransitionInterdite();

    function creer(string calldata titre) external returns (uint256 id) {
        require(bytes(titre).length > 0, "Titre vide");
        id = prochainId;
        prochainId += 1;
        taches[id] = Tache({
            createur: msg.sender,
            titre: titre,
            creeeLe: uint64(block.timestamp),
            etat: Etat.Ouverte
        });
        emit TacheCreee(id, msg.sender, titre);
    }

    function lire(uint256 id) external view returns (Tache memory) {
        if (id >= prochainId) revert TacheInexistante(id);
        return taches[id];
    }

    function definirEtat(uint256 id, Etat nouvelEtat) external {
        if (id >= prochainId) revert TacheInexistante(id);
        Tache storage tache = taches[id];
        if (tache.createur != msg.sender) revert AppelantNonAutorise();
        if (tache.etat == Etat.Terminee || tache.etat == Etat.Annulee) {
            revert TransitionInterdite();
        }
        Etat ancien = tache.etat;
        tache.etat = nouvelEtat;
        emit EtatModifie(id, ancien, nouvelEtat);
    }
}
~~~

Le contrat permet au créateur de modifier l'état tant que la tâche n'est pas terminée ou annulée. Pour un exercice de conception, cela soulève une question utile : l'expression \`nouvelEtat\` permet-elle de passer directement d'Ouverte à Annulée ou d'Ouverte à Terminée ? Le code le permet. Si la politique exige des transitions séquentielles, elle doit les vérifier explicitement. Une enum limite les valeurs possibles, mais ne définit pas à elle seule les transitions métiers autorisées.

Le contrôle par \`id >= prochainId\` repose sur le fait que les identifiants sont créés séquentiellement et qu'aucune suppression ne les réutilise. Si une future version ajoute une destruction ou un import de données, cette hypothèse devra être revue. Les erreurs personnalisées donnent des erreurs structurées, tandis que l'événement permet à l'interface de suivre les changements sans parcourir l'ensemble du stockage.

### Tests minimaux à écrire

1. Le compte A crée une tâche et devient son créateur.
2. Le titre vide est refusé.
3. Le compte B ne peut pas modifier l'état de la tâche de A.
4. Un identifiant supérieur ou égal à \`prochainId\` est rejeté.
5. Le créateur peut modifier l'état d'une tâche ouverte.
6. Une tâche terminée ne peut plus être modifiée.
7. L'événement émis contient l'identifiant et les états attendus.
8. Le comportement correspond à la spécification si l'utilisateur tente de passer directement à l'état Annulée.

Ce petit exemple est volontairement plus utile qu'un extrait qui ne compile pas : la structure, les noms et les types sont cohérents, et les limites métiers sont explicites. Il reste nécessaire de compiler et tester avec la version exacte de Solidity visée.

## 14. Organiser les permissions et les transitions d'état

La sécurité d'un contrat dépend moins du nombre de modificateurs que de la justesse du modèle d'autorisation. Pour chaque fonction d'écriture, formule une phrase : « Qui peut appeler cette fonction, sur quel objet, à quel moment, avec quelles conséquences ? » Si la réponse est vague, le contrôle d'accès n'est pas prêt.

Les permissions peuvent dépendre de l'appelant, du propriétaire d'un objet, d'un rôle, d'un délai ou d'une condition de gouvernance. Le contrôle basé sur \`msg.sender\` ne prouve que l'adresse de l'appelant immédiat dans le contexte EVM ; il n'établit pas l'identité civile de la personne. Lorsqu'un contrat intermédiaire appelle la fonction, \`msg.sender\` peut être ce contrat intermédiaire plutôt que l'utilisateur final.

~~~mermaid
flowchart TD
    A["Appel externe"] --> B["Vérifier l'existence de l'objet"]
    B --> C["Vérifier le rôle ou le propriétaire"]
    C --> D["Vérifier l'état courant et la transition"]
    D --> E["Mettre à jour les données"]
    E --> F["Émettre l'événement correspondant"]
    B -->|Échec| X["Revert"]
    C -->|Échec| X
    D -->|Échec| X
~~~

Il est utile de représenter un objet métier avec une machine à états. Pour une tâche, les états peuvent être Ouverte, EnCours, Terminée et Annulée. La matrice doit préciser quelles transitions sont autorisées :

| État actuel | Nouvel état autorisé | Exemple de règle |
|---|---|---|
| Ouverte | EnCours | Le créateur ou un membre autorisé démarre le travail |
| Ouverte | Annulée | Le créateur peut annuler avant le démarrage |
| EnCours | Terminée | Le créateur ou le rôle responsable valide le résultat |
| Terminée | Tout autre état | Refusé si l'état final est irréversible |
| Annulée | Tout autre état | Refusé, sauf procédure de réouverture documentée |

Cette matrice doit être reflétée dans les tests. Tester uniquement les transitions autorisées ne suffit pas : les transitions interdites constituent souvent le cœur de la sécurité métier. Les cas limites incluent l'appel répété, le mauvais rôle, un identifiant absent, un état final et une transition effectuée par un contrat intermédiaire.

### Séparer les responsabilités administratives

Un propriétaire unique est simple, mais il concentre le pouvoir. Une multisignature répartit une décision entre plusieurs clés, tandis qu'un mécanisme de délai donne aux utilisateurs le temps d'observer une mise à niveau ou une modification de paramètres. Ces approches répondent à des risques différents et apportent une complexité supplémentaire.

Le bon choix dépend du dommage possible. Pour un exercice sans fonds, un propriétaire simple permet d'apprendre la syntaxe. Pour un contrat qui garde des actifs ou contrôle des certificats à valeur importante, il faut documenter la rotation de clés, l'urgence, les conflits, les délais, les journaux et les recours possibles. Une fonction d'administration doit être traitée comme une capacité puissante, pas comme un détail pratique.

## 15. Revue de code, tests de propriétés et critères d'acceptation

Une revue de smart contract doit se concentrer sur les invariants et les chemins d'exécution, pas seulement sur le style du code. Avant de chercher des optimisations, identifie les actifs contrôlés, les rôles, les dépendances et les scénarios de défaillance. Pour chaque fonction d'écriture, examine la précondition, le changement d'état, les appels externes et le résultat observable.

~~~mermaid
flowchart LR
    S["Spécification"] --> I["Définir invariants"]
    I --> U["Tests unitaires"]
    U --> P["Tests négatifs et de propriétés"]
    P --> R["Revue indépendante"]
    R --> D["Déployer sur réseau de test"]
    D --> V["Vérifier bytecode et comportement"]
~~~

### Checklist de revue

- Toutes les fonctions d'écriture ont une règle de permission claire.
- Les identifiants non existants sont rejetés sans modifier l'état.
- Les valeurs nulles, limites et extrêmes sont testées.
- Les transitions d'état autorisées et interdites sont spécifiées.
- Les appels externes peuvent échouer et leur échec est traité.
- Les événements sont émis après une modification réussie et reflètent les valeurs correctes.
- Les données provenant d'oracles ou d'autres contrats sont validées.
- Les boucles ont des limites ou une stratégie de pagination appropriée.
- Les variables publiques et les méthodes accessibles correspondent à l'API voulue.
- La version du compilateur et les dépendances sont fixées pour le build reproductible.
- Les avertissements du compilateur ont été résolus ou documentés.
- Les tests incluent un acteur non autorisé, un état inattendu et une erreur.

### Propriétés et tests automatisés

Un test unitaire vérifie un scénario précis. Un test de propriété vérifie une règle qui devrait rester vraie après plusieurs séquences d'appels. Par exemple, dans un registre de tâches, le nombre \`prochainId\` ne doit jamais diminuer et une tâche doit toujours conserver le créateur initial. Dans un coffre, le total des retraits d'un utilisateur ne doit pas dépasser ses dépôts selon la comptabilité prévue.

Les outils de fuzzing peuvent générer des entrées variées pour découvrir des cas qu'un humain n'a pas écrits à la main. Toutefois, les outils ne connaissent pas automatiquement l'intention métier. Il faut écrire des propriétés suffisamment précises, analyser les contre-exemples et reproduire les défauts identifiés par des tests de régression.

### Échecs à ne pas ignorer

Une compilation réussie ne prouve pas l'absence de bug. Un test passant ne prouve pas que le code est sûr dans tous les états. Un audit est une évaluation limitée dans le temps, sur une version donnée et selon un périmètre annoncé. Après une modification de code, de configuration ou de dépendance, il faut déterminer si les preuves précédentes sont toujours pertinentes.

Pour un vrai projet, conserve le hash du commit, la version du compilateur, les options d'optimisation, les tests exécutés, les adresses de déploiement, l'ABI et les résultats de vérification. Cette traçabilité aide à relier le code source au comportement publié et facilite le diagnostic en cas d'incident.

## 16. TP guidé A : construire un registre de tâches

### Objectif

Écrire un contrat qui permet à chaque utilisateur de créer une tâche et de marquer ses propres tâches comme terminées. Aucun actif financier n'est nécessaire.

### Spécification

Chaque tâche contient un identifiant, le créateur, une description courte et un statut. Un utilisateur peut créer une tâche ; l'identifiant est unique ; seul le créateur peut changer le statut de cette tâche. Chaque création et modification émet un événement. Le contrat doit fournir une fonction de lecture d'une tâche et une fonction qui retourne le nombre total de tâches.

### Étapes

1. Définis une structure Task et un enum TaskStatus.
2. Utilise un tableau ou un mapping, puis justifie ton choix.
3. Écris une fonction createTask qui enregistre le créateur et l'état initial.
4. Écris une fonction markDone qui vérifie le créateur.
5. Émets des événements permettant à une interface de suivre les changements.
6. Compile le contrat et résous les avertissements.
7. Teste avec deux comptes : le créateur doit pouvoir changer le statut, l'autre compte doit être rejeté.
8. Teste un identifiant qui n'existe pas et un appel répété.

### Critères de réussite

Le contrat compile sans erreur ; un utilisateur ne peut pas modifier la tâche d'un autre ; les identifiants ne sont pas réutilisés ; les événements correspondent aux changements effectifs ; les erreurs attendues sont claires. Évite de parcourir tout le tableau dans une transaction d'écriture si son nombre d'éléments peut croître sans limite.

## 17. TP guidé B : examiner un contrat à partir de son ABI

Choisis un contrat de démonstration sur un réseau de test. Recueille l'adresse, le nom du réseau, l'ABI et la source vérifiée si elle est disponible. Classe les fonctions en lectures et écritures, puis identifie celles qui nécessitent des permissions. Repère les événements et explique comment un indexeur pourrait les utiliser.

Pour chaque fonction, relève les paramètres, les sorties, les effets sur l'état, les erreurs potentielles et la quantité de gaz approximative si tu disposes d'une mesure. N'envoie pas de transaction à un contrat dont tu ne comprends pas l'adresse et le comportement. Le but est la lecture technique, pas la gestion de fonds.

### Corrigé indicatif

L'ABI révèle l'interface mais ne garantit pas le comportement. Les fonctions view sont normalement des lectures qui n'écrivent pas l'état persistant, tandis qu'une fonction d'écriture est appelée par une transaction. Les permissions doivent être vérifiées dans le code. Les événements servent à l'observation, mais l'application doit vérifier l'adresse du contrat et gérer les réorganisations. Une source vérifiée augmente la transparence sans remplacer les tests ou l'audit.

## 18. Interactions externes et modèle Checks-Effects-Interactions

Un smart contract doit considérer qu'un appel externe peut transférer le contrôle à du code qui n'est pas sous le contrôle du contrat appelant. Le destinataire peut revenir vers le contrat, déclencher d'autres contrats, refuser l'appel ou retourner des données inattendues. La sécurité ne se limite donc pas aux paramètres visibles de la fonction : l'ordre des écritures et des interactions fait partie du modèle de menace.

Le modèle Checks-Effects-Interactions recommande de vérifier d'abord les préconditions, d'appliquer ensuite les changements d'état nécessaires, puis d'effectuer l'interaction externe. Ce modèle limite de nombreuses formes de réentrance, mais il faut l'appliquer à la logique réelle : certains scénarios ont besoin de callbacks, et certaines opérations doivent être atomiques.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract CoffreDeTest {
    mapping(address => uint256) public soldes;

    error SoldeInsuffisant();
    error TransfertEchoue();

    function crediterPourTest(address utilisateur) external payable {
        require(msg.value > 0, "Montant nul");
        soldes[utilisateur] += msg.value;
    }

    function retirer(uint256 montant) external {
        uint256 solde = soldes[msg.sender];
        if (montant > solde) revert SoldeInsuffisant();

        // Effet appliqué avant l'interaction externe.
        soldes[msg.sender] = solde - montant;

        (bool succes, ) = payable(msg.sender).call{value: montant}("");
        if (!succes) revert TransfertEchoue();
    }
}
~~~

Cet exemple reste pédagogique et ne doit pas être déployé avec des fonds réels sans revue. La fonction \`crediterPourTest\` est accessible à tout le monde et créditerait le compte indiqué avec la valeur attachée à l'appel ; ce choix est acceptable pour illustrer le flux, mais ne représente pas une comptabilité complète. Le retrait réduit d'abord le solde, puis tente le transfert. Si le transfert échoue et que l'erreur est propagée, la transaction revert et l'écriture du solde est annulée selon les règles de l'EVM.

### Scénarios à tester

- Le retrait est inférieur au solde.
- Le retrait est égal au solde.
- Le retrait dépasse le solde.
- Le destinataire est un contrat qui refuse le transfert.
- Le destinataire tente de rappeler \`retirer\` pendant le transfert.
- Le compte effectue deux retraits de suite.
- Le code est exécuté dans un environnement où les frais et l'état initial sont connus.

La règle ne consiste pas à remplacer toutes les anciennes fonctions de transfert par un seul appel précis. Elle consiste à comprendre le contexte d'appel, la sémantique de retour, la possibilité de callbacks et la gestion des erreurs. Pour les composants courants, utilise des bibliothèques auditées et respecte la version de Solidity choisie.

## 19. Construire une suite de tests qui décrit l'intention

Une bonne suite de tests n'est pas un inventaire de boutons que l'on a cliqués. Elle décrit les propriétés qui doivent rester vraies. Pour le registre de tâches, la propriété peut être « seul le créateur modifie sa tâche ». Pour un jeton, elle peut être « le total des soldes suit la règle d'offre attendue ». Pour un coffre, elle peut être « les retraits autorisés ne dépassent pas la comptabilité définie ».

~~~mermaid
flowchart TD
    S["Définir un invariant métier"] --> N["Construire le cas normal"]
    N --> E["Ajouter cas limites"]
    E --> A["Ajouter compte non autorisé"]
    A --> X["Simuler appel externe ou échec"]
    X --> R["Exécuter tests et analyser les contre-exemples"]
    R --> T["Ajouter un test de régression"]
~~~

### Cas de test et résultats attendus

| Catégorie | Exemple | Résultat attendu |
|---|---|---|
| Cas normal | Créer une tâche avec un titre valide | Nouvelle tâche et événement correct |
| Entrée limite | Titre vide | Revert ou erreur prévue |
| Autorisation | Un tiers modifie la tâche d'un autre | Refus sans mutation |
| État invalide | Identifiant inexistant | Refus clairement testable |
| Appel répété | Terminer deux fois une tâche finale | Seconde transition refusée |
| Dépendance | Appel externe qui échoue | État cohérent ou rollback documenté |
| Régression | Rejouer une ancienne faille | Le comportement vulnérable ne revient pas |

Les tests unitaires sont adaptés aux fonctions isolées. Les tests d'intégration valident les interactions entre contrats et bibliothèques. Le fuzzing explore un grand espace d'entrées. Les tests de propriétés vérifient des invariants sur des séquences variées. L'analyse statique repère certains motifs de risque, mais ne connaît pas automatiquement l'intention métier.

### Conditions de sortie vers un réseau public

Avant de déployer, vérifie la version exacte du compilateur, les dépendances, les options d'optimisation, les avertissements, la couverture des chemins critiques et la reproductibilité du build. Conserve le commit source, l'ABI, le bytecode de création et l'adresse déployée. Vérifie ensuite que le code publié correspond à l'artefact construit.

Aucun seuil numérique de couverture ne garantit qu'un contrat soit sûr. Une couverture élevée peut coexister avec des assertions faibles ; une couverture plus ciblée peut manquer un chemin d'appel. Les critères doivent privilégier les invariants, les autorisations, les interactions externes, les cas de panne et la clarté des résultats.

## 20. Étude de cas : réviser un contrat avant de le partager

Supposons qu'un apprenant ait écrit un registre de tâches qui fonctionne sur un réseau local. La première démonstration réussit : créer une tâche augmente le compteur, et le lecteur récupère la bonne description. Avant de déclarer le contrat prêt, il faut vérifier ce qui se passe avec des séquences moins évidentes : changement d'état répété, identifiant inexistant, action depuis une autre adresse, titre inhabituellement long et remise en service après une interruption.

~~~mermaid
flowchart TD
    A["Version qui fonctionne sur le cas nominal"] --> B["Tester limites et erreurs"]
    B --> C["Tester permissions depuis un autre compte"]
    C --> D["Vérifier événements et état final"]
    D --> E["Corriger puis ajouter un test de régression"]
    E --> F["Revue finale avant partage"]
~~~

### De la spécification aux assertions

Une assertion de test doit exprimer une propriété observable. Après la création d'une tâche, le compteur doit avoir augmenté d'une unité et l'événement doit inclure le bon identifiant et le bon créateur. Après une tentative d'accès non autorisé, l'état doit rester identique. Après une erreur, l'application doit pouvoir reconnaître l'échec et ne pas afficher une réussite.

La distinction entre erreur attendue et bug est importante. Si un identifiant n'existe pas, le refus fait partie du contrat. Si un accès non autorisé modifie la tâche, c'est un défaut de sécurité. Si un événement est émis avant qu'une condition échoue puis l'exécution revert, il faut comprendre les règles de rollback des logs et les effets observés par les outils.

### Qualité des exemples pédagogiques

Un exemple dans une leçon doit être clairement classé : extrait illustratif, contrat complet de laboratoire ou implémentation de production. Un extrait de syntaxe peut omettre des contrôles pour rendre un concept visible, mais il ne doit pas contenir une erreur de compilation non signalée. Un contrat de laboratoire doit avoir un périmètre de sécurité explicitement décrit. Un exemple de production exige des tests, une revue, des dépendances vérifiées et une stratégie de déploiement.

Cette classification aide les apprenants à copier le code en connaissance de cause. Dans le dépôt de cours, relis chaque extrait comme si un étudiant allait le coller dans son IDE : noms de variables, types, accolades, version de compilateur, noms d'événements et explication après l'extrait doivent être cohérents.

## 21. Lire du Solidity comme un auditeur

Un audit de lecture commence par les fonctions accessibles depuis l'extérieur. Pour chacune, repère les données contrôlées par l'appelant, la condition d'accès, les lectures d'état, les écritures et les appels externes. Cette méthode évite de rester bloqué sur la syntaxe et aide à comprendre ce qu'un utilisateur peut réellement demander au contrat.

~~~mermaid
flowchart TD
    A["Fonction externe"] --> B["Quelles entrées l'appelant contrôle-t-il ?"]
    B --> C["Quelles permissions sont vérifiées ?"]
    C --> D["Quel état peut être modifié ?"]
    D --> E["Des appels externes sont-ils effectués ?"]
    E --> F["Quels tests démontrent les propriétés ?"]
~~~

### Exercice de lecture guidée

Pour une fonction de transfert, cherche d'abord le propriétaire des fonds et la manière dont le destinataire est choisi. Vérifie ensuite le solde ou l'autorisation, puis l'ordre des écritures. Examine si l'appel peut déclencher un callback. Enfin, relève les événements et vérifie qu'ils ne peuvent pas être interprétés comme une réussite lorsque l'exécution a échoué.

Pour une fonction administrative, identifie qui peut la déclencher et quel dommage elle peut provoquer. Une fonction qui change une adresse oracle est presque aussi critique que la fonction qui lit ce prix : un attaquant capable de remplacer la source peut contourner la sécurité de la fonction consommatrice sans modifier son code.

### Transformer l'analyse en test

Chaque risque doit donner lieu à un scénario précis. Si l'utilisateur A ne doit pas pouvoir modifier les données de B, crée les deux comptes dans le test et tente l'appel depuis B. Si une valeur trop grande doit être refusée, teste la limite elle-même, la valeur juste en dessous et la valeur juste au-dessus. Si un appel externe peut échouer, crée un destinataire de test qui renvoie une erreur et observe l'état final.

Le but est de pouvoir relier chaque règle importante à une condition de code et à un test. Une revue qui ne fait que lire le code sans essayer les chemins négatifs manque souvent les problèmes de logique.

## 22. Conventions et reproductibilité des projets Solidity

Le code doit pouvoir être recompilé et vérifié à partir d'une configuration connue. Verrouille la version du compilateur, la version des bibliothèques et les paramètres d'optimisation. Conserve le code source et le résultat de compilation associés au déploiement. Si une interface dépend d'une ABI, elle doit être régénérée à partir de l'artefact validé, pas modifiée à la main sans contrôle.

### Discipline de projet

- Chaque contrat doit avoir un nom et un périmètre clair.
- Les fonctions publiques et externes doivent être documentées.
- Les permissions doivent être commentées au niveau de l'intention, sans remplacer le test.
- Les erreurs personnalisées doivent être cohérentes avec les conditions qui les déclenchent.
- Les événements doivent représenter les changements significatifs de l'état.
- Les extraits pédagogiques doivent être compilés avant publication.
- Les tests doivent être exécutés après toute correction ou mise à niveau de dépendance.

Un avertissement de compilateur peut révéler une intention ambiguë, une conversion dangereuse ou du code inutilisé. Il ne faut pas le masquer simplement pour avoir un journal propre. En cas de désactivation volontaire, documente la raison et vérifie que le comportement reste correct.

### Critère pédagogique

Un cours technique de qualité doit séparer le code d'exemple qui illustre un concept, le mini-projet qui doit compiler et la recommandation adaptée à la production. Une explication honnête mentionne les omissions et les risques restants. Cette séparation évite qu'un débutant confonde un exemple court avec un contrat prêt à gérer de la valeur réelle.

## 23. Dix questions d'entraînement avec corrigé

### Question 1
À quoi sert la directive pragma ?

**Corrigé :** Elle indique les versions de compilateur compatibles visées par le code ; elle ne garantit ni que cette version soit installée ni que le contrat soit sûr.

### Question 2
Quelle est la différence entre une variable d'état et une variable locale ?

**Corrigé :** Une variable d'état est persistante dans l'état du contrat. Une variable locale est utilisée pendant une exécution, sauf si ses résultats sont ensuite inscrits dans l'état.

### Question 3
Que signifie view ?

**Corrigé :** La fonction ne modifie pas l'état persistant selon les règles du langage ; elle peut lire l'état.

### Question 4
Pourquoi external ne signifie-t-il pas « sécurisé » ?

**Corrigé :** La visibilité décrit comment appeler la fonction. Les règles d'accès doivent être codées et testées séparément.

### Question 5
À quoi sert un mapping ?

**Corrigé :** Il associe une clé à une valeur, par exemple une adresse à un solde. Il n'offre pas à lui seul une liste parcourable de toutes les clés.

### Question 6
Pourquoi les boucles non bornées sont-elles dangereuses ?

**Corrigé :** Leur coût de gaz peut croître jusqu'à rendre la fonction trop coûteuse ou impossible à exécuter dans une transaction.

### Question 7
Quelle est la différence entre storage, memory et calldata ?

**Corrigé :** Storage représente l'état persistant ; memory contient des données temporaires ; calldata représente les données d'entrée de fonction dans un espace de lecture seule approprié.

### Question 8
À quoi servent les événements ?

**Corrigé :** Ils rendent les actions observables dans les journaux afin que les applications puissent les indexer. Ils ne remplacent pas l'état ni la vérification du reçu.

### Question 9
Comment éviter une erreur de contrôle d'accès ?

**Corrigé :** Définir les rôles et les fonctions sensibles, appliquer les contrôles dans le contrat et tester les appels depuis des comptes autorisés et non autorisés.

### Question 10
La compilation réussie prouve-t-elle qu'un contrat est sûr ?

**Corrigé :** Non. Il faut aussi des tests, analyses, revues, contrôles des dépendances, vérification de déploiement et surveillance.

## 24. Challenge final : spécifier et tester un coffre fictif

### Scénario

Tu dois concevoir un contrat de laboratoire dans lequel chaque adresse peut enregistrer un dépôt fictif et consulter son total. Il ne doit pas transférer de valeur native. Un administrateur peut suspendre les nouvelles écritures, mais les lectures restent disponibles. Le projet ne sera pas utilisé pour des actifs réels.

### Travail demandé

Rédige une spécification de 500 à 700 mots, puis propose les fonctions, les événements, les erreurs et les invariants. Décris au moins huit tests, dont des tests de permissions et des tests de comportement en mode suspendu. Explique pourquoi une fonction d'administration est un risque et comment la réduire.

### Correction proposée

Le contrat peut conserver un mapping d'adresse vers un total fictif, une variable d'état pour le propriétaire et un booléen indiquant si les écritures sont suspendues. La fonction de dépôt fictif vérifie que les écritures sont actives, que le montant est supérieur à zéro et qu'il ne dépasse pas les limites prévues pour le test. Elle met à jour le total et émet un événement. La lecture renvoie le total associé à l'adresse demandée sans changer l'état. Les fonctions administratives vérifient que l'appelant est autorisé.

Les invariants incluent : une lecture ne modifie pas l'état ; un compte ne peut pas modifier le solde d'un autre ; un montant nul ou excessif est rejeté ; lorsque la suspension est active, aucune nouvelle écriture n'est acceptée ; seules les actions autorisées peuvent modifier la suspension ; les événements ne sont émis qu'après un changement réussi. Les tests couvrent le dépôt positif, la valeur nulle, la limite maximale, le compte non autorisé, le propriétaire autorisé, la suspension activée, la lecture en mode suspendu et le transfert éventuel du rôle propriétaire.

Le contrôle administratif reste un pouvoir significatif : une clé compromise pourrait suspendre les écritures ou changer le comportement. Une multisignature, une procédure de transfert et une documentation des pouvoirs peuvent réduire certaines dépendances. Une procédure d'urgence doit être testée plutôt qu'improvisée. Même si cet exercice ne déplace aucun actif, il apprend à traiter les permissions, l'état et les tests comme une partie essentielle de la conception.

## Glossaire

**ABI :** interface décrivant les fonctions, paramètres, résultats et événements d'un contrat.

**Adresse :** identifiant utilisé dans l'écosystème EVM pour représenter un compte ou un contrat.

**Calldata :** espace de données d'entrée d'une fonction externe, utilisé en lecture seule dans les contextes habituels.

**Constructeur :** fonction spéciale exécutée lors du déploiement pour initialiser le contrat.

**Événement :** trace enregistrée dans les journaux à destination des applications et indexeurs.

**Mapping :** structure associant des clés à des valeurs.

**Memory :** espace de données temporaire pour une exécution.

**Modificateur :** mécanisme réutilisable qui ajoute des conditions ou une logique autour d'une fonction.

**Pragma :** directive indiquant les versions du compilateur ciblées ou les paramètres de compilation associés.

**Revert :** arrêt d'une exécution qui annule ses changements d'état, avec consommation possible de gaz.

**Solidity :** langage de programmation pour les contrats EVM.

**Storage :** état persistant du contrat.

**Struct :** type qui regroupe plusieurs champs sous une même structure.

**View :** marqueur d'une fonction qui ne modifie pas l'état persistant.

## Pour aller plus loin

- Documentation Solidity : https://docs.soliditylang.org/en/latest/
- Solidity par l'exemple : https://solidity-by-example.org/
- Documentation Ethereum sur les smart contracts : https://ethereum.org/developers/docs/smart-contracts/
- Considérations de sécurité Solidity : https://docs.soliditylang.org/en/latest/security-considerations.html
- OpenZeppelin Contracts : https://docs.openzeppelin.com/contracts/

Compile les exemples avant de les utiliser. Un extrait de cours peut contenir une simplification pédagogique et ne doit pas être copié directement dans un système qui gère des fonds. Pour un contrat réel, fixe les versions de compilateur et de dépendances, écris des tests, fais une revue indépendante et évalue les menaces de l'application complète.
