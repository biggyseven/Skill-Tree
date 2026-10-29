# Standards ERC-20, ERC-721

## Encadré de mise en contexte

Sur Ethereum, un smart contract peut représenter des unités numériques et des objets identifiables. Sans interface commune, chaque application devrait apprendre une API différente pour afficher un solde, transférer un actif ou vérifier les permissions. Les standards de jetons définissent un ensemble de fonctions et d'événements communs afin que les portefeuilles, marchés et autres contrats puissent interagir avec de nombreuses implémentations.

Deux standards fondamentaux sont ERC-20 et ERC-721. ERC-20 sert aux jetons fongibles : chaque unité est interchangeable avec une autre unité du même jeton, conformément aux règles du contrat. ERC-721 sert aux jetons non fongibles (NFT) : chaque jeton possède un identifiant distinct au sein du contrat et sa propriété doit être suivie individuellement. Un token n'est pas automatiquement une monnaie, un investissement, un titre juridique ou une preuve universelle de propriété d'un objet physique. Le standard définit surtout une interface technique ; la signification économique ou juridique dépend du projet et du contexte.

Ce cours présente les fonctions, les événements, les autorisations, les unités, les différences entre fongibilité et unicité, les métadonnées, les transferts sûrs, les approbations et les risques. Il montre aussi comment les applications doivent vérifier les contrats et les réseaux. Les exemples de code sont pédagogiques ; pour un projet réel, une implémentation éprouvée et maintenue est préférable à une réécriture maison.

## Objectifs d'apprentissage

À la fin de la leçon, tu sauras :

- expliquer le rôle des standards de jetons dans l'écosystème EVM ;
- distinguer ERC-20, ERC-721 et les actifs natifs d'une blockchain ;
- comprendre les fonctions et événements essentiels d'ERC-20 ;
- expliquer balanceOf, transfer, approve, allowance et transferFrom ;
- gérer correctement les unités et la précision des jetons ;
- décrire l'unicité d'un NFT et le rôle du couple adresse du contrat et tokenId ;
- comprendre les transferts sûrs, les approbations d'un NFT et les opérateurs ;
- distinguer l'état du jeton, les métadonnées et le contenu hébergé hors chaîne ;
- détecter les erreurs d'interface et les risques d'approbation excessive ;
- tester les propriétés attendues d'un jeton avant de l'intégrer dans une DApp.

## 1. Qu'est-ce qu'un standard de jeton ?

Un standard est une spécification d'interface et de comportement. Il définit des fonctions que les contrats compatibles doivent exposer et la signification attendue de certains événements et valeurs. Le standard améliore l'interopérabilité : un portefeuille peut traiter différents jetons avec une interface similaire au lieu d'implémenter une intégration unique pour chaque projet.

Un standard n'est pas une certification de sécurité. Un contrat peut déclarer ou ressembler à une interface connue sans fournir la signification que l'utilisateur attend. Il faut vérifier le code, l'adresse, le réseau, les permissions, les événements et les comportements particuliers. Un jeton peut implémenter ERC-20 tout en présentant des risques économiques, administratifs ou techniques importants.

### 1.1 Actif natif et jeton de contrat

L'ETH est l'actif natif d'Ethereum ; il n'est pas un jeton ERC-20 simplement parce qu'il sert à payer les frais. Les jetons ERC-20 sont généralement des contrats qui maintiennent leurs propres soldes et appliquent des règles de transfert. Les frais du réseau et le solde du jeton sont donc deux choses distinctes.

Une adresse peut détenir de l'ETH sans détenir un jeton particulier. Elle peut détenir plusieurs jetons ERC-20 et plusieurs NFT ERC-721. Un affichage qui montre « solde » doit préciser le type d'actif, le contrat et les unités pour éviter une confusion entre les actifs natifs et les jetons.

### 1.2 Rôle des événements

Les événements permettent aux portefeuilles, explorateurs et indexeurs de suivre les transferts et les approbations. Ils sont une partie importante de l'interface standardisée. Les événements facilitent l'observation, mais les applications doivent vérifier l'adresse du contrat émetteur et gérer la finalité. Un événement émis par un contrat arbitraire ne doit pas être interprété comme une preuve que le jeton attendu a réellement changé de propriétaire.

## 2. ERC-20 : jetons fongibles

ERC-20 définit une interface standard pour des jetons interchangeables. Les unités sont suivies sous forme de nombres dans le contrat. La notion de fongibilité suppose que les unités du même jeton sont équivalentes pour l'application ; elle n'affirme pas que tous les contrats ERC-20 de tous les projets sont équivalents entre eux.

Les fonctions principales comprennent généralement :

- totalSupply : quantité totale en circulation selon la logique du contrat ;
- balanceOf : solde du compte indiqué ;
- transfer : transfert direct vers une adresse ;
- approve : définition ou modification d'une autorisation de dépense ;
- allowance : consultation de l'autorisation donnée à un tiers ;
- transferFrom : transfert exécuté par un tiers autorisé.

Les événements importants incluent Transfer et Approval. Des métadonnées comme name, symbol et decimals sont courantes, mais certaines sont optionnelles dans la spécification ERC-20. Les applications ne doivent donc pas supposer que toutes les implémentations exposent exactement les mêmes métadonnées optionnelles.

~~~mermaid
flowchart TD
    U["DApp ou portefeuille"] --> Q["Lire balanceOf"]
    U --> T["transfer direct"]
    U --> A["approve une dépense"]
    A --> L["Allowance enregistrée"]
    S["Spender autorisé"] --> F["transferFrom"]
    L --> F
    T --> E["Événement Transfer"]
    F --> E
~~~

### 2.1 totalSupply

totalSupply retourne la quantité totale définie par l'implémentation. La manière dont cette valeur évolue dépend des règles du contrat : certains jetons ont une offre fixe, d'autres permettent l'émission de nouvelles unités, et d'autres permettent une destruction. L'interface ERC-20 ne garantit pas à elle seule que l'offre soit plafonnée.

Pour vérifier la politique monétaire d'un jeton, il faut identifier les fonctions d'émission et de destruction, les rôles autorisés, les limites éventuelles et les événements associés. Une description commerciale disant « offre limitée » ne suffit pas si le contrat conserve une fonction de mint illimitée contrôlée par une clé.

### 2.2 balanceOf

balanceOf reçoit une adresse et retourne le solde comptable du jeton pour cette adresse. La fonction ne révèle pas automatiquement l'identité du détenteur ni les conditions d'accès à un service. Le solde est exprimé en unités minimales du jeton, souvent appelées unités de base.

Une interface doit convertir la valeur brute à l'aide des règles de précision appropriées. Si decimals retourne 6, un solde brut de 1 250 000 correspond à 1,25 unité affichée. Mais les applications doivent lire la précision réellement exposée par le contrat au lieu de supposer toujours 18 décimales.

### 2.3 transfer

transfer déplace une quantité du compte qui appelle la fonction vers le destinataire. Dans le modèle usuel, le transfert est autorisé par le compte appelant et l'événement Transfer est émis pour enregistrer le mouvement. Les règles précises du contrat peuvent imposer des conditions supplémentaires, par exemple une pause, une liste de blocage ou des frais.

La fonction retourne un booléen dans l'interface ERC-20. La spécification demande aux intégrateurs de gérer la valeur false plutôt que de supposer que tout appel réussi au niveau du transport signifie que le transfert a réussi. Dans l'écosystème, certaines implémentations anciennes ne respectent pas parfaitement les conventions de retour, d'où l'usage fréquent de bibliothèques comme SafeERC20 pour normaliser plusieurs comportements connus.

### 2.4 approve et allowance

approve permet au détenteur d'autoriser un autre compte ou contrat à dépenser jusqu'à une certaine quantité de jetons. allowance retourne la quantité encore autorisée selon les règles du contrat. Ce mécanisme permet à un échange décentralisé, un protocole de prêt ou un autre contrat d'utiliser des jetons pour le compte de l'utilisateur, sans que celui-ci signe chaque transfert individuel.

Cette commodité crée un risque important. Si le contrat autorisé est malveillant ou compromis, il peut dépenser jusqu'à la limite d'autorisation. Les utilisateurs doivent comprendre quelle adresse est autorisée, quelle quantité elle peut déplacer et pendant combien de temps l'autorisation peut rester active. Une autorisation maximale évite parfois de refaire une transaction, mais augmente le risque en cas de compromission.

### 2.5 Le risque de changement d'allowance

La modification d'une allowance non nulle vers une autre valeur peut créer un problème de course dans certaines interactions, car le dépensier peut agir avant que la nouvelle valeur soit appliquée ou observée. Les interfaces et contrats peuvent utiliser des stratégies recommandées pour réduire le risque, comme mettre d'abord l'autorisation à zéro lorsque c'est nécessaire ou utiliser des fonctions sûres propres à certaines bibliothèques. Il faut toutefois suivre le comportement du jeton et ne pas supposer une stratégie universelle identique pour toutes les implémentations.

### 2.6 transferFrom

transferFrom permet à un tiers de transférer les jetons d'un propriétaire lorsque l'autorisation suffisante existe. Un protocole d'échange utilise souvent ce mécanisme pour déplacer des jetons après qu'un utilisateur a autorisé le contrat. Le contrat devrait vérifier l'autorisation, le solde et les autres conditions prévues par l'implémentation.

Un utilisateur ne doit pas confondre approve et transfer. approve n'effectue pas le transfert voulu par l'utilisateur ; il crée une permission qui permet à un tiers de faire des transferts futurs selon la portée prévue. Une DApp doit afficher distinctement ces deux opérations et expliquer les autorisations demandées.

## 3. Les décimales et les unités ERC-20

La valeur stockée par un contrat ERC-20 est un entier. decimals indique le nombre de décimales que les applications peuvent utiliser pour présenter les unités dans une forme humaine. Il ne change pas la nature arithmétique du stockage : le contrat additionne et soustrait des entiers.

Il faut distinguer trois notions :
- l'unité brute enregistrée dans le contrat ;
- le nombre de décimales utilisé pour la présentation ;
- la quantité économique que l'utilisateur croit transférer.

Si l'application prend « 1,5 » et oublie de la convertir en unités de base, elle pourrait envoyer une quantité mille ou un million de fois plus petite que prévu, selon la précision. À l'inverse, une conversion incorrecte pourrait transférer beaucoup plus que ce que l'utilisateur pense. Les nombres à virgule flottante du navigateur ne sont pas adaptés aux montants monétaires exacts ; utilise des bibliothèques d'entiers ou de décimales précises.

### 3.1 Exemple de conversion

Supposons un jeton qui expose 6 décimales. Une unité humaine vaut alors 1 000 000 d'unités brutes. Pour transférer 2,75 unités, il faut encoder 2 750 000 unités brutes, si le jeton applique bien cette précision. Le contrat ne reçoit pas un nombre décimal : il reçoit un entier.

### 3.2 Pourquoi decimals est optionnel

Le champ decimals a été rendu optionnel dans ERC-20 afin de permettre diverses conventions. Les intégrateurs devraient vérifier l'existence de la fonction et gérer les cas où elle est absente. Les valeurs usuelles ne sont pas une garantie pour chaque contrat. Une interface robuste doit gérer les métadonnées manquantes sans attribuer silencieusement une précision arbitraire.

## 4. Exemple pédagogique ERC-20

Un contrat de jeton réel doit respecter l'interface, traiter les événements et définir ses règles d'émission et d'autorisation. Le code suivant illustre l'idée du registre des soldes, mais ne doit pas être utilisé comme implémentation de production. Il omet volontairement plusieurs détails et contrôles qu'une bibliothèque reconnue traite déjà.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract JetonDidactique {
    string public name = "Jeton Didactique";
    string public symbol = "JDT";
    uint8 public decimals = 18;
    uint256 public totalSupply;

    mapping(address => uint256) private balances;
    mapping(address => mapping(address => uint256)) private allowances;

    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);

    constructor(uint256 supplyInitial) {
        totalSupply = supplyInitial;
        balances[msg.sender] = supplyInitial;
        emit Transfer(address(0), msg.sender, supplyInitial);
    }

    function balanceOf(address account) external view returns (uint256) {
        return balances[account];
    }

    function transfer(address to, uint256 value) external returns (bool) {
        require(to != address(0), "Destinataire nul");
        require(balances[msg.sender] >= value, "Solde insuffisant");
        balances[msg.sender] -= value;
        balances[to] += value;
        emit Transfer(msg.sender, to, value);
        return true;
    }

    function approve(address spender, uint256 value) external returns (bool) {
        allowances[msg.sender][spender] = value;
        emit Approval(msg.sender, spender, value);
        return true;
    }

    function allowance(address owner, address spender) external view returns (uint256) {
        return allowances[owner][spender];
    }

    function transferFrom(address owner, address to, uint256 value) external returns (bool) {
        require(to != address(0), "Destinataire nul");
        require(balances[owner] >= value, "Solde insuffisant");
        require(allowances[owner][msg.sender] >= value, "Allowance insuffisante");
        allowances[owner][msg.sender] -= value;
        balances[owner] -= value;
        balances[to] += value;
        emit Transfer(owner, to, value);
        return true;
    }
}
~~~

Cet exemple est volontairement minimal. Un projet doit tester les cas limites, l'émission, les conventions de transfert, les changements d'autorisation, les erreurs, les événements et l'intégration avec les contrats qui consomment le jeton. En pratique, préférer l'implémentation ERC-20 maintenue d'OpenZeppelin à une implémentation écrite de zéro, puis étendre le comportement de manière explicite.

## 5. ERC-721 : jetons non fongibles

ERC-721 définit une interface pour des actifs identifiables individuellement. Chaque NFT dispose d'un tokenId au sein du contrat. L'identifiant seul n'est pas globalement unique sur toutes les chaînes : l'identité complète d'un NFT est le couple formé de l'adresse du contrat et du tokenId, dans un réseau précis.

La propriété est suivie pour chaque identifiant. Un même contrat peut émettre de nombreux NFT, mais chaque tokenId vivant représente une unité distincte. La standardisation permet aux portefeuilles et places de marché de demander le propriétaire, d'autoriser des transferts et, si les extensions sont présentes, de lire le nom, le symbole et les métadonnées.

~~~mermaid
flowchart TD
    C["Adresse du contrat ERC-721"] --> ID["tokenId unique dans ce contrat"]
    ID --> O["ownerOf(tokenId)"]
    O --> A["Adresse propriétaire"]
    M["tokenURI(tokenId), si pris en charge"] --> META["Métadonnées"]
    META --> F["Nom, description, image et attributs"]
~~~

### 5.1 balanceOf et ownerOf

balanceOf dans ERC-721 retourne le nombre de NFT détenus par une adresse selon les règles du contrat. ownerOf retourne l'adresse propriétaire d'un tokenId existant. Contrairement à ERC-20, ownerOf n'est pas une quantité ; elle identifie le propriétaire de l'objet distinct.

Les applications ne doivent pas supposer que les tokenId sont consécutifs ou commencent à zéro. La spécification considère l'identifiant comme une valeur que le client doit traiter de manière opaque. Certains contrats mintent à partir de zéro, d'autres utilisent des séquences différentes, et certains tokens peuvent être brûlés selon les fonctionnalités du contrat.

### 5.2 Transferts et autorisations

ERC-721 prévoit des transferts initiés par le propriétaire, une adresse approuvée pour un token particulier ou un opérateur approuvé pour plusieurs tokens du propriétaire. approve définit l'autorisation pour un token spécifique ; setApprovalForAll permet à un opérateur d'agir sur l'ensemble des NFT de l'appelant selon les règles du contrat.

L'autorisation globale est pratique pour les places de marché, mais elle est puissante. Si l'opérateur est malveillant ou compromis, il peut transférer plusieurs NFT de l'utilisateur. La DApp doit afficher l'adresse exacte de l'opérateur et expliquer si l'autorisation est limitée à un token ou couvre toute la collection.

### 5.3 transferFrom et safeTransferFrom

transferFrom permet le transfert selon les permissions. safeTransferFrom ajoute des vérifications destinées à éviter la perte accidentelle d'un NFT lorsqu'il est envoyé à un contrat récepteur qui ne sait pas le gérer. Pour un transfert sûr vers un contrat, celui-ci doit généralement implémenter la fonction de réception attendue et retourner la valeur magique définie par le standard.

Le transfert non sûr peut envoyer un NFT à un contrat qui ne sait pas comment le récupérer, ce qui peut le rendre inaccessible de manière permanente. Les applications devraient utiliser la méthode de transfert adaptée au contexte et tester le comportement des contrats récepteurs. « Safe » ne signifie pas qu'un transfert ne peut jamais être frauduleux ; il protège surtout contre une classe de destinataires contractuels non compatibles.

### 5.4 ERC-165 et détection d'interface

ERC-721 s'appuie sur ERC-165 pour permettre à un contrat d'indiquer les interfaces qu'il prend en charge. Un client peut interroger la capacité déclarée d'un contrat plutôt que de supposer qu'il implémente toutes les fonctions d'une famille de standards. Toutefois, la déclaration d'interface doit être interprétée dans le contexte de l'implémentation réelle et ne constitue pas un audit de comportement.

## 6. Métadonnées et stockage NFT

L'extension de métadonnées ERC-721 fournit une fonction tokenURI qui permet de récupérer un identifiant de métadonnées associé au token. Cette URI peut pointer vers du JSON qui contient notamment un nom, une description, une image ou des attributs. Le standard ne garantit pas que ces données seront stockées sur chaîne ni qu'elles resteront accessibles pour toujours.

Si tokenURI renvoie une URL sur un serveur centralisé, l'opérateur du serveur peut changer ou supprimer le contenu. Si l'URI utilise un identifiant de contenu IPFS, l'intégrité du contenu peut être vérifiable, mais sa disponibilité dépend toujours de personnes ou services qui le conservent. L'adresse on-chain et le contenu hors chaîne sont donc deux couches différentes.

### 6.1 Possession du NFT et droits sur le fichier

Posséder un NFT ne signifie pas automatiquement posséder le droit d'auteur sur l'image, le droit d'exploiter une marque ou le droit de posséder l'objet physique décrit. Ces droits dépendent des conditions du projet, du contrat juridique et du droit applicable. Le token peut servir de reçu, de licence, de ticket, de preuve d'appartenance à une communauté ou à d'autres fonctions, mais l'association doit être définie clairement.

Les projets devraient préciser ce que l'acheteur acquiert, les droits d'utilisation du média, les conditions de stockage, la procédure de mise à jour des métadonnées et les risques de disponibilité. Une interface qui affiche seulement « propriétaire du NFT » peut être insuffisante pour expliquer les droits réellement transférés.

### 6.2 Métadonnées immuables ou modifiables

Certains projets fixent les métadonnées après mint ; d'autres permettent à un administrateur de mettre à jour le contenu ou de révéler des attributs ultérieurement. Les deux approches peuvent être légitimes pour des usages différents, mais elles présentent des garanties distinctes. Il faut identifier la fonction qui contrôle l'URI et qui peut la modifier.

Une fonction administrative qui change les métadonnées peut servir à corriger une erreur ou révéler le contenu à une date prévue, mais peut aussi permettre une substitution trompeuse. Les acheteurs doivent savoir si le contenu est immuable, soumis à une révélation différée ou contrôlé par un opérateur.

## 7. Comparer ERC-20 et ERC-721

| Dimension | ERC-20 | ERC-721 |
|---|---|---|
| Nature | Jetons fongibles | Jetons non fongibles |
| Comptabilité | Solde numérique par adresse | Propriétaire par tokenId |
| Transfert | Quantité | Identifiant individuel |
| Approbation | Quantité autorisée pour un spender | Autorisation sur un token ou un opérateur global |
| Métadonnées | Nom, symbole et décimales généralement utilisées, certaines optionnelles | Nom, symbole et URI de chaque token via extension de métadonnées |
| Usage typique | Jeton d'utilité, actif comptable, stablecoin ou gouvernance | Collectible, ticket, objet de jeu ou certificat tokenisé |
| Risque particulier | Autorisation excessive, émission et précision | Approbation globale, métadonnées et perte vers récepteur incompatible |

Il existe d'autres standards, extensions et variantes : par exemple ERC-1155 pour gérer plusieurs types d'actifs dans un même contrat ou des extensions qui définissent des propriétés supplémentaires. La présence d'un standard ne garantit pas que tous les contrats aient les mêmes règles de transfert ou le même modèle économique.

## 8. Mint, burn et autorisations administratives

Mint est le processus par lequel un contrat crée des unités ou NFT selon ses règles. Burn est le processus par lequel des unités sont retirées de la circulation ou un NFT est détruit selon l'implémentation. Le standard ne permet pas à l'utilisateur de supposer que tous les jetons ont une offre fixe ou que le contrat permet nécessairement le burn.

Pour un ERC-20, la fonction de mint peut être réservée à un rôle, ou l'offre initiale peut être émise une seule fois dans le constructeur. Pour un ERC-721, une fonction de mint peut vérifier l'autorisation de l'émetteur, l'unicité du tokenId, la limite d'offre et les règles de métadonnées. Ces décisions font partie de la logique du projet et doivent être documentées.

Les permissions d'administration sont un risque économique. Un administrateur peut pouvoir émettre de nouveaux jetons, geler des comptes, mettre le contrat en pause, changer des métadonnées ou modifier le code via un proxy. L'utilisateur doit comprendre ces pouvoirs avant d'utiliser le token. La transparence de l'adresse du contrat permet l'analyse, mais ne garantit pas que l'utilisateur soit en mesure de la faire seul.

## 9. Risques d'intégration pour les DApps

Les portefeuilles et contrats doivent éviter de traiter un jeton comme fiable simplement parce qu'il expose des fonctions standard. Plusieurs risques existent :

- fonction transfer qui retourne false plutôt que de revert ;
- contrat de jeton qui ne renvoie pas de valeur de retour comme attendu par certains anciens intégrateurs ;
- frais de transfert qui réduisent la quantité reçue ;
- jeton rebasing dont le solde peut évoluer sans transfert classique ;
- jeton avec liste de blocage ou pause ;
- approbation globale trop importante ;
- NFT dont les métadonnées changent ou deviennent indisponibles ;
- jeton copiant le nom et le symbole d'un actif connu ;
- adresse correcte mais sur le mauvais réseau ;
- événement émis par un contrat qui imite la signature d'un autre événement.

Les contrats qui intègrent ERC-20 devraient considérer le comportement réel du jeton. SafeERC20 peut gérer certains cas de retour courants, mais n'élimine pas le risque des jetons à comportement exotique. Les applications financières doivent définir les actifs supportés et tester explicitement les hypothèses sur les transferts et les soldes.

## 10. Lire et vérifier un jeton

Avant d'ajouter un jeton à une application, confirme le réseau, l'adresse exacte et la source d'information. Le nom et le symbole ne sont pas des identifiants uniques : un attaquant peut créer un contrat qui reprend le nom d'un jeton connu. L'adresse du contrat est une information déterminante.

Pour ERC-20, vérifie la quantité totale, la politique d'émission, les fonctions administratives, decimals si disponible, les transferts et les permissions. Pour ERC-721, vérifie ownerOf, les approbations, le comportement de transfert sûr, tokenURI et les pouvoirs qui affectent les métadonnées. Examine également les dépendances, les proxys et les événements.

Les explorateurs de blocs peuvent aider à retrouver les transactions, événements et sources publiées. Une source vérifiée permet de lire le code associé au bytecode dans des conditions compatibles, mais ce n'est pas une garantie de sécurité. Pour un usage important, une revue indépendante et des tests d'intégration restent nécessaires.

## 11. TP guidé A : analyser un ERC-20 sans dépenser de fonds

### Objectif

Apprendre à lire l'interface d'un jeton et à repérer ses hypothèses de sécurité. Le TP se fait en lecture seule à partir d'un contrat de test ou d'un jeton connu ; ne signe aucune transaction et ne révèle jamais de clé privée.

### Étape 1 — Identifier le réseau et le contrat

Note le nom du réseau, son chain ID et l'adresse complète du contrat. Vérifie que les informations concordent avec une source fiable. Ne te fie pas uniquement à une icône ou un ticker.

### Étape 2 — Lire les méthodes

Repère totalSupply, balanceOf, decimals, name et symbol lorsque ces fonctions sont disponibles. Note quelles fonctions sont optionnelles et si la précision du jeton est explicitement exposée.

### Étape 3 — Examiner les autorisations

Cherche les fonctions liées à mint, burn, pause, blacklist, upgrade ou gestion des rôles. Explique les conséquences si elles existent. Le nom d'une fonction ne suffit pas : vérifie qui peut l'appeler et quelles conditions sont appliquées.

### Étape 4 — Examiner les événements

Repère Transfer et Approval dans l'historique. Vérifie l'adresse émettrice des journaux et ne traite pas un événement similaire provenant d'un autre contrat comme une preuve du mouvement.

### Livrable

Fournis une fiche qui comprend le contrat, le réseau, les métadonnées, la politique d'offre, les pouvoirs d'administration et cinq risques éventuels. Si une information ne peut pas être confirmée, marque-la explicitement comme inconnue.

## 12. TP guidé B : analyser un NFT ERC-721

### Objectif

Comprendre comment l'identité d'un NFT est liée à son contrat, à son tokenId, à son propriétaire et à ses métadonnées.

### Étape 1 — Choisir un NFT

Depuis un explorateur ou une collection de test, note l'adresse du contrat et un tokenId. Vérifie ownerOf et balanceOf. Ne suppose pas que tokenId est globalement unique sur tous les contrats.

### Étape 2 — Lire tokenURI

Si le contrat prend en charge l'extension de métadonnées, récupère tokenURI et examine le JSON associé. Note si l'URI utilise une adresse web traditionnelle, un schéma IPFS ou un autre format. N'ouvre pas de lien inconnu qui demande de connecter un portefeuille ou de signer une opération.

### Étape 3 — Examiner les approbations

Vérifie l'approbation d'un token spécifique et l'autorisation globale des opérateurs si les méthodes correspondantes sont disponibles. Explique pourquoi un opérateur global peut représenter un risque supérieur à une approbation unique.

### Étape 4 — Évaluer la promesse

Rédige un court paragraphe qui distingue ce qui est garanti par le contrat (identifiant et propriétaire selon le protocole) de ce qui dépend des métadonnées, de l'hébergeur et des droits juridiques. Un NFT n'est pas automatiquement une propriété immobilière ou un droit d'auteur.

## 13. Dix questions d'entraînement avec corrigé

### Question 1
Pourquoi existe-t-il des standards de jetons ?

**Corrigé :** Ils définissent des interfaces communes afin que les portefeuilles, contrats et places de marché puissent interagir avec plusieurs implémentations de manière plus prévisible.

### Question 2
Quelle est la différence entre ERC-20 et ERC-721 ?

**Corrigé :** ERC-20 suit des quantités fongibles par adresse ; ERC-721 suit des identifiants individuels et leur propriétaire.

### Question 3
Le nom et le symbole identifient-ils un jeton de façon unique ?

**Corrigé :** Non. Plusieurs contrats peuvent utiliser les mêmes métadonnées. L'adresse du contrat et le réseau doivent être vérifiés.

### Question 4
Que fait approve dans ERC-20 ?

**Corrigé :** Il autorise un tiers à dépenser une quantité selon l'allowance. Il n'effectue pas nécessairement le transfert lui-même.

### Question 5
Pourquoi une allowance maximale est-elle risquée ?

**Corrigé :** Le spender peut disposer d'une autorisation très large. S'il est compromis ou malveillant, il peut dépenser jusqu'à cette limite selon les règles du contrat.

### Question 6
Pourquoi decimals ne doit-il pas être supposé toujours égal à 18 ?

**Corrigé :** La précision varie selon les jetons et la fonction est optionnelle dans la spécification. L'application doit lire et gérer la valeur réelle.

### Question 7
Comment identifie-t-on un NFT de manière complète ?

**Corrigé :** Par le réseau, l'adresse du contrat et le tokenId. Le tokenId seul n'est pas unique à l'échelle de toutes les chaînes.

### Question 8
À quoi sert safeTransferFrom ?

**Corrigé :** Il inclut des vérifications destinées à empêcher la perte accidentelle de NFT lors d'un transfert vers un contrat incapable de recevoir correctement le token.

### Question 9
Un NFT garantit-il le droit d'auteur sur son image ?

**Corrigé :** Non. Les droits dépendent des conditions et du cadre juridique. Le standard suit un token et sa propriété on-chain, pas automatiquement tous les droits relatifs à l'œuvre.

### Question 10
Un standard ERC garantit-il qu'un token est sûr ?

**Corrigé :** Non. Il normalise l'interface et certains comportements attendus, mais il ne garantit pas l'économie, les permissions, la qualité des métadonnées ou l'absence de bugs.

## 14. Challenge final : choisir un standard pour une application

### Scénario

Une équipe construit une application pour une communauté. Elle veut proposer un actif de points échangeables, des cartes de membre individuelles et des certificats de formation vérifiables. Elle envisage d'utiliser un seul contrat de jeton pour les trois besoins.

### Travail demandé

Rédige une recommandation de 500 à 700 mots qui compare ERC-20 et ERC-721, décrit les besoins de chaque objet, précise les permissions administratives et explique les risques liés aux métadonnées, aux approbations et aux transferts. Propose un plan de test avant le déploiement.

### Correction proposée

Les points échangeables ressemblent à un actif fongible : ERC-20 peut être adapté si toutes les unités d'un même jeton sont équivalentes. L'équipe doit préciser si l'offre est fixe ou si elle peut être émise par un rôle autorisé, comment les points sont gagnés ou brûlés et quels transferts sont permis. Si les points ne doivent jamais être transférables entre utilisateurs, un standard public classique peut ne pas exprimer toutes les règles métier souhaitées sans contrôles supplémentaires.

Les cartes de membre individuelles et les certificats distincts correspondent davantage à ERC-721 si chaque élément doit avoir un identifiant et un propriétaire séparés. Les certificats exigent un soin particulier : le contrat peut enregistrer une empreinte ou un statut, mais l'émission doit être authentifiée, les révocations doivent être prévues et les informations personnelles ne devraient pas être publiées inutilement. L'identifiant unique ne garantit pas la vérité du contenu ; il établit seulement une relation technique au contrat et aux données enregistrées.

L'équipe doit documenter les rôles d'émission, les pouvoirs de pause et les mécanismes de mise à niveau. Les utilisateurs doivent savoir si les métadonnées peuvent changer et comment vérifier l'origine d'un certificat. Pour les NFT, la stratégie de stockage doit prévoir l'hébergement, la redondance et les droits de réutilisation des images. Les approbations d'opérateurs doivent être limitées et expliquées ; une marketplace ne devrait pas demander un accès global sans justification claire.

Le plan de test inclut les transferts valides et invalides, les soldes, les décimales, les allowances, les erreurs d'autorisation, les identifiants NFT inexistants, les destinataires contractuels incompatibles, la lecture des métadonnées, les fonctions de révocation, les erreurs de réseau et les permissions administratives. Il faut tester les comportements avec des portefeuilles et bibliothèques d'intégration courants, puis faire une revue indépendante si les certificats ou points ont une valeur importante.

La décision dépend des propriétés métier. ERC-20 suit des quantités interchangeables ; ERC-721 suit des objets identifiables. Aucun standard ne remplace la spécification des droits, des règles d'émission, des contrôles d'accès, des données hors chaîne ou des obligations juridiques.

## Glossaire

**Allowance :** quantité de jetons ERC-20 qu'un propriétaire a autorisé un spender à transférer selon les règles du contrat.

**Approval :** autorisation de dépense, en quantité pour ERC-20 ou pour un NFT ou opérateur dans ERC-721.

**ERC-20 :** standard d'interface pour des jetons fongibles.

**ERC-721 :** standard d'interface pour des jetons non fongibles identifiés individuellement.

**Fongibilité :** propriété selon laquelle des unités d'un même actif sont interchangeables dans le cadre défini.

**Mint :** création d'unités ou de tokens selon les règles du contrat.

**NFT :** jeton non fongible doté d'un identifiant individuel dans son contrat.

**TokenId :** identifiant d'un NFT dans le contrat ERC-721.

**TokenURI :** URI associée à un NFT pour obtenir ses métadonnées, selon l'extension utilisée.

**Transfer :** événement généralement émis pour signaler le mouvement d'un jeton.

**TransferFrom :** fonction permettant un transfert exécuté par un tiers autorisé.

**Métadonnées :** informations descriptives associées à un jeton ou NFT.

## Pour aller plus loin

- Spécification officielle ERC-20 : https://eips.ethereum.org/EIPS/eip-20
- Spécification officielle ERC-721 : https://eips.ethereum.org/EIPS/eip-721
- OpenZeppelin ERC-20 : https://docs.openzeppelin.com/contracts/5.x/erc20
- OpenZeppelin ERC-721 : https://docs.openzeppelin.com/contracts/5.x/erc721
- Documentation Ethereum sur les jetons : https://ethereum.org/developers/docs/standards/tokens/

Utilise les standards comme base d'interopérabilité et non comme certificat de sécurité. Pour intégrer un jeton, vérifie l'adresse et le réseau, lis les permissions et le comportement réel, teste les cas limites, et préfère des bibliothèques auditées à une implémentation improvisée.
