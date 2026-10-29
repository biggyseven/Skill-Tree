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
    enum Etat { Ouvert, EnCours, Resol u, Ferme }

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

Dans cet extrait, le mot de l'énumération qui représente l'état résolu doit être écrit sans espace comme une seule valeur, par exemple Resolu. Cet exemple illustre l'idée des structures, mais il doit être corrigé avant compilation et complété par des fonctions de lecture et de transition. Toujours compiler le code copié au lieu de supposer que chaque extrait explicatif est déjà un projet complet.

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

## 12. TP guidé A : construire un registre de tâches

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

## 13. TP guidé B : examiner un contrat à partir de son ABI

Choisis un contrat de démonstration sur un réseau de test. Recueille l'adresse, le nom du réseau, l'ABI et la source vérifiée si elle est disponible. Classe les fonctions en lectures et écritures, puis identifie celles qui nécessitent des permissions. Repère les événements et explique comment un indexeur pourrait les utiliser.

Pour chaque fonction, relève les paramètres, les sorties, les effets sur l'état, les erreurs potentielles et la quantité de gaz approximative si tu disposes d'une mesure. N'envoie pas de transaction à un contrat dont tu ne comprends pas l'adresse et le comportement. Le but est la lecture technique, pas la gestion de fonds.

### Corrigé indicatif

L'ABI révèle l'interface mais ne garantit pas le comportement. Les fonctions view sont normalement des lectures qui n'écrivent pas l'état persistant, tandis qu'une fonction d'écriture est appelée par une transaction. Les permissions doivent être vérifiées dans le code. Les événements servent à l'observation, mais l'application doit vérifier l'adresse du contrat et gérer les réorganisations. Une source vérifiée augmente la transparence sans remplacer les tests ou l'audit.

## 14. Dix questions d'entraînement avec corrigé

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

## 15. Challenge final : spécifier et tester un coffre fictif

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
