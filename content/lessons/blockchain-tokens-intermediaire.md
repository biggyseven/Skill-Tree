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

## 11. Tester la conformité plutôt que le nom du jeton

Un jeton ne devient pas sûr parce que son nom contient « ERC-20 » ou parce qu'il expose une méthode \`transfer\`. La conformité se vérifie avec une suite de comportements attendus et avec le code effectif. L'adresse et le réseau doivent être connus avant de lire les soldes ou les événements. Les métadonnées comme name et symbol sont utiles à l'affichage, mais elles ne sont pas des identifiants uniques.

Pour ERC-20, les tests devraient vérifier notamment :
- \`totalSupply\` et la politique d'émission ;
- \`balanceOf\` avant et après un transfert ;
- le transfert d'une quantité nulle, qui reste un cas à traiter conformément au standard ;
- le refus d'un montant supérieur au solde ;
- \`approve\`, \`allowance\` et \`transferFrom\` ;
- les événements Transfer et Approval ;
- le comportement des autorisations lors d'un transfert par un tiers ;
- les comportements atypiques si le contrat applique frais, pause ou restrictions.

~~~mermaid
flowchart TD
    A["Choisir réseau et adresse"] --> B["Lire interface et code"]
    B --> C["Tester transferts et soldes"]
    C --> D["Tester autorisations"]
    D --> E["Tester erreurs et événements"]
    E --> F["Analyser fonctions administratives"]
    F --> G["Documenter ce qui reste incertain"]
~~~

### Compatibilité et retours de transfert

La spécification ERC-20 prévoit un booléen de retour pour certaines fonctions de transfert et d'approbation, mais des contrats historiques n'ont pas tous le même comportement de retour. Les intégrateurs doivent utiliser des bibliothèques reconnues conçues pour gérer les modèles courants et ne pas supposer que l'absence de revert signifie toujours que les jetons ont été déplacés comme attendu.

Une bibliothèque telle que SafeERC20 peut normaliser plusieurs comportements observés, mais elle ne rend pas sûrs les jetons arbitraires. Un jeton peut appliquer des frais, geler des comptes, rebaser les soldes ou posséder des permissions administratives. Une application financière doit définir les jetons qu'elle supporte et les tests d'intégration qu'elle exige.

### Propriétés de transfert

Pour un jeton simple sans frais ni mécanisme particulier, une propriété attendue est que la somme des soldes ne change pas pendant un transfert ordinaire ; seul le propriétaire de la quantité change. Cette propriété peut être différente si le contrat brûle une commission, émet de nouvelles unités ou applique des règles spécifiques. Il faut toujours formuler les invariants selon le comportement déclaré et codé, pas selon une supposition générale.

## 12. Autorisations de dépense : comprendre approve et permit

Dans ERC-20, \`approve(spender, amount)\` permet à un tiers de transférer une quantité définie de jetons du compte propriétaire. \`transferFrom\` utilise cette permission. Une autorisation n'est pas une transaction de transfert en elle-même : elle ouvre une capacité de dépense future, dont la portée doit être comprise.

~~~mermaid
sequenceDiagram
    participant U as Propriétaire
    participant T as Contrat du jeton
    participant S as Spender
    U->>T: approve(S, quantité)
    T-->>U: Événement Approval
    S->>T: transferFrom(U, destinataire, quantité)
    T->>T: Vérifier solde et allowance
    T-->>S: Transfert accepté ou rejeté
~~~

Une application peut demander une autorisation à chaque utilisation ou demander une autorisation plus grande pour réduire les transactions répétées. L'option d'autorisation large améliore parfois l'expérience mais élargit l'exposition en cas de compromission du spender. L'interface devrait demander le minimum nécessaire et offrir un moyen de consulter les autorisations actives.

### Signatures de type permit

Certains jetons implémentent une extension de type EIP-2612 qui permet de créer ou modifier une allowance à l'aide d'une signature off-chain plutôt que d'une transaction d'approbation séparée. Cette mécanique peut réduire le nombre d'étapes, mais elle introduit des questions de nonce, de domaine, d'expiration et de rejeu. Elle n'est pas disponible sur tous les jetons et doit être vérifiée sur le contrat précis.

Une signature permit reste une autorisation de dépense. Elle ne doit pas être présentée comme une simple connexion ou un message de preuve d'identité. L'application doit afficher le contrat et la portée autorisés, vérifier le domaine et le nonce selon la norme, et traiter les signatures expirées ou déjà utilisées.

### Nettoyage des permissions

Quand une application n'a plus besoin d'une allowance, elle peut aider l'utilisateur à la réduire ou à la révoquer, selon ce que le jeton et le réseau permettent. La révocation est elle-même une transaction ; elle peut échouer ou rester en attente. Une interface doit distinguer la demande d'annulation de l'autorisation et la confirmation effective de la nouvelle valeur.

## 13. NFT : récepteurs, métadonnées et état réel

ERC-721 distingue le propriétaire on-chain, l'identifiant du token et les métadonnées référencées. Une collection peut annoncer une image et des attributs, mais le contrat ne garantit pas que le fichier soit encore disponible ni que les droits d'utilisation du média soient transférés. Il faut considérer le contrat, la URI et le service de stockage comme des composants distincts.

~~~mermaid
flowchart TD
    A["Réseau + adresse du contrat + tokenId"] --> B["ownerOf : propriétaire on-chain"]
    A --> C["tokenURI : emplacement des métadonnées"]
    C --> D["JSON de métadonnées"]
    D --> E["Image / animation / attributs"]
    E --> F["Stockage et disponibilité hors chaîne"]
~~~

### Les transferts sûrs peuvent appeler du code externe

\`safeTransferFrom\` cherche à éviter qu'un NFT soit envoyé à un contrat qui ne peut pas le recevoir en exigeant, pour un destinataire contractuel, le mécanisme de réception attendu par le standard. Cette vérification implique un appel externe au contrat destinataire. Le code du destinataire peut donc s'exécuter pendant le transfert, ce qui oblige les implémentations à raisonner sur les callbacks et les risques de réentrance.

« Sûr » ne signifie pas que le transfert est honnête, réversible ou exempt de phishing. Un utilisateur peut toujours autoriser un contrat malveillant à déplacer un NFT. Les permissions et l'adresse du destinataire doivent être vérifiées avant la signature. Les contrats récepteurs devraient être testés avec les chemins de succès et de refus.

### Métadonnées mutables

La fonction \`tokenURI\` peut renvoyer des données dont le contenu change au fil du temps selon la conception du contrat et l'hébergement. Un administrateur peut avoir un rôle de mise à jour ; un serveur peut changer le fichier ; un stockage adressé par contenu peut garder l'intégrité mais dépend de la disponibilité du contenu.

Pour une collection qui promet une métadonnée immuable, documente précisément ce qui est immuable : l'URI peut-elle changer ? le JSON est-il stocké sur chaîne ? l'image peut-elle disparaître ? la licence peut-elle changer ? La promesse commerciale ne doit pas être confondue avec ce que le code garantit.

### Burn et événements

Un NFT peut être détruit si son contrat implémente un mécanisme de burn. Après la destruction, l'identifiant peut ne plus avoir de propriétaire selon l'implémentation. Les indexeurs doivent traiter les événements appropriés et ne pas supposer que tous les tokenId qui ont existé sont encore valides. Les applications qui affichent une collection doivent gérer les NFT brûlés, les transferts récents et les réorganisations de chaîne.

## 14. Autres standards et matrice de choix

ERC-20 et ERC-721 ne couvrent pas tous les besoins de tokenisation. ERC-1155 permet à un même contrat de gérer plusieurs types de jetons, incluant des types fongibles et non fongibles selon la manière dont ils sont utilisés. Il peut être utile pour les jeux ou les applications qui gèrent de nombreux actifs. En contrepartie, les intégrateurs doivent comprendre son interface de transfert par lots et ses événements particuliers.

~~~mermaid
flowchart TD
    Q["Besoin métier"] --> F{"Unités interchangeables ?"}
    F -->|Oui| ERC20["Évaluer ERC-20"]
    F -->|Non, chaque objet distinct| ERC721["Évaluer ERC-721"]
    F -->|Plusieurs types et lots| ERC1155["Évaluer ERC-1155"]
    ERC20 --> R["Vérifier fonctions, permissions et compatibilité"]
    ERC721 --> R
    ERC1155 --> R
~~~

### Choisir selon la logique, pas selon la mode

| Besoin | Piste de départ | Questions complémentaires |
|---|---|---|
| Points ou unité fongible | ERC-20 | Offre fixe ou mint ? Transferts libres ? Précision ? |
| Pièce de collection individuelle | ERC-721 | Métadonnées, opérateurs, transfert sûr, burn ? |
| Plusieurs catégories d'objets et transferts par lots | ERC-1155 | Gestion des lots, récepteurs, événements et indexeurs ? |
| Certificat vérifiable | ERC-721 ou registre dédié | Révocation, confidentialité et droits juridiques ? |
| Permission à durée limitée | Extension ou contrat d'autorisation | Nonce, échéance, domaine de signature et rejeu ? |

Le standard doit exprimer les propriétés techniques nécessaires sans donner une fausse impression de garantie juridique. Un certificat ou une carte de membre peut nécessiter une fonction de révocation, un statut d'expiration ou un modèle de confidentialité. Ces besoins doivent être vérifiés avant le choix du standard.

### Plan de test d'intégration

Une DApp qui consomme un jeton doit tester l'intégration avec le contrat exact, et non uniquement avec un jeton de test idéal. Les scénarios comprennent les métadonnées absentes, les transferts qui retournent false ou revert, les approbations larges, les frais de transfert, les pauses, les adresses erronées, les mauvais réseaux et les événements dupliqués lors d'une réorganisation. Les tests de propriété doivent utiliser le vrai modèle de comptabilité du jeton.

Pour les NFT, teste l'adresse de collection, les tokenId invalides, les autorisations par token et globales, les récepteurs contractuels qui acceptent ou rejettent, la disponibilité des métadonnées et les pouvoirs qui modifient les URI. Une interface fiable affiche les incertitudes connues et ne transforme pas un événement isolé en preuve universelle de droits.

## 15. TP guidé A : analyser un ERC-20 sans dépenser de fonds

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

## 16. TP guidé B : analyser un NFT ERC-721

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

## 17. ERC-20 : vérifier les propriétés métier et la politique d'offre

L'interface ERC-20 ne définit pas à elle seule l'économie du jeton. Avant de l'intégrer, il faut connaître la règle d'émission, la politique de destruction, les fonctions administratives, la possibilité de pause, l'existence de restrictions de transfert et la manière dont le contrat peut changer. Deux contrats conformes à la même interface peuvent présenter des risques très différents.

### Questions à poser au propriétaire du token

- L'offre est-elle fixe ou peut-elle augmenter ?
- Qui peut appeler mint, burn, pause ou les fonctions de liste de blocage ?
- Une mise à niveau peut-elle modifier les règles de transfert ?
- Existe-t-il une commission prélevée à chaque transfert ?
- Les soldes peuvent-ils évoluer sans événement Transfer classique, par exemple dans un modèle de rebase ?
- La précision est-elle disponible et est-elle utilisée de manière cohérente par les applications ?
- Qui surveille les fonctions administratives et quelle est la procédure d'urgence ?

~~~mermaid
flowchart TD
    A["Contrat ERC-20 identifié"] --> B["Lire offre et règles d'émission"]
    B --> C["Identifier rôles et fonctions sensibles"]
    C --> D["Tester transfert, allowance et retours"]
    D --> E["Tester comportements spécifiques"]
    E --> F["Décider si l'intégration supporte ce token"]
~~~

### Comptabilité et jetons atypiques

Le modèle le plus simple suppose que le montant reçu par un destinataire correspond exactement au montant demandé. Cette hypothèse n'est pas vraie pour tous les jetons : certains prélèvent une commission, modifient les soldes selon une règle de rebase ou appliquent des restrictions. Un protocole qui calcule son solde comptable à partir du montant demandé peut alors diverger de la quantité réellement reçue.

Si un protocole prend en charge ces jetons, il doit prévoir une stratégie adaptée, par exemple vérifier le changement de solde réel avant et après le transfert selon les limites de sécurité. Cette mesure n'est pas universellement adaptée à tous les tokens et peut présenter ses propres cas limites. La meilleure approche est de définir explicitement la liste des jetons supportés et de tester leur comportement réel.

### Approvals et événements

Les événements Approval et Transfer sont des signaux utiles, mais ne remplacent pas l'examen de la fonction et de son statut. Un contrat d'indexation doit vérifier l'adresse émettrice et gérer les réorganisations. L'interface doit également rendre visible le spender autorisé, l'allowance, la quantité et l'action que l'utilisateur s'apprête à signer.

## 18. ERC-721 : identité, propriété et réception par un contrat

L'identité d'un NFT est définie par le réseau, l'adresse du contrat et le tokenId. Ce triplet doit être utilisé dans les bases de données et les API afin d'éviter que deux collections différentes soient confondues parce qu'elles partagent un même tokenId. L'URI et les métadonnées sont des propriétés supplémentaires, pas un substitut à l'identifiant on-chain.

### Détection d'un contrat récepteur

Lors d'un safeTransferFrom vers une adresse de contrat, l'implémentation ERC-721 appelle la fonction de réception attendue et vérifie sa valeur de retour. Ce mécanisme réduit le risque d'envoyer accidentellement un NFT à un contrat incapable de le traiter. Il ne garantit pas que le contrat récepteur conservera le NFT de manière sûre ou qu'il ne fera pas autre chose ensuite.

~~~mermaid
sequenceDiagram
    participant O as Propriétaire
    participant E as Contrat ERC-721
    participant R as Contrat récepteur
    O->>E: safeTransferFrom(destinataire, tokenId)
    E->>E: Vérifier propriétaire et autorisation
    E->>R: onERC721Received(...)
    R-->>E: Valeur de réception attendue
    E->>E: Finaliser le transfert
    E-->>O: Événement Transfer
~~~

Le callback du récepteur est un appel externe. Les implémentations doivent tenir compte de la réentrance et garantir que l'état de propriété est cohérent selon l'ordre d'exécution. Les tests doivent inclure un destinataire conforme, un destinataire qui refuse et un destinataire qui exécute du code inattendu pendant la réception.

### Métadonnées, URI et droits

Le standard ne garantit pas que tokenURI reste disponible ni que le contenu soit immuable. Une URI HTTP dépend d'un serveur ; une URI IPFS dépend de la disponibilité des nœuds qui conservent le contenu. Un identifiant de contenu peut vérifier l'intégrité mais ne chiffre pas le document et ne garantit pas sa pérennité.

Les conditions commerciales doivent préciser les droits associés au NFT. Posséder le token ne signifie pas nécessairement détenir le droit d'auteur, un titre de propriété physique ou la capacité juridique de revendre l'objet associé. Si le NFT est un certificat, l'émetteur, la révocation, la confidentialité et les erreurs doivent être spécifiés.

## 19. Intégration d'un jeton : test de bout en bout

Un contrat qui utilise un jeton doit être testé avec le jeton choisi et avec des réponses réalistes. Un test qui passe avec un ERC-20 simpliste ne prouve pas que le protocole gère correctement les tokens à comportement atypique. La bibliothèque d'intégration, la gestion des retours, la précision des montants et la politique d'allowance doivent être évaluées ensemble.

### Matrice de test recommandée

| Scénario | Vérification attendue |
|---|---|
| Transfert ERC-20 normal | Soldes et événements cohérents |
| Solde insuffisant | Rejet sans mutation incorrecte |
| Approve puis transferFrom | Quantité et allowance réduites selon le contrat |
| Approve maximal | Risque et portée montrés à l'utilisateur |
| Fonction transfer qui revert | Erreur propagée et interface claire |
| Jeton à commission | Quantité reçue traitée selon la politique du protocole |
| NFT inexistant | ownerOf/requête renvoie l'erreur attendue |
| NFT envoyé à un contrat non récepteur | safeTransferFrom refuse le transfert |
| URI inaccessible | Interface gère la métadonnée indisponible |
| Mauvais réseau | Aucune transaction n'est préparée avec la mauvaise configuration |

### Critères d'acceptation

La DApp doit afficher le bon réseau, vérifier l'adresse du contrat, convertir la quantité avec la précision correcte, demander une approbation dont la portée est comprise et attendre un reçu pour conclure. Pour les NFT, elle doit distinguer propriétaire on-chain et métadonnées. L'indexeur doit être capable de reconstruire l'historique à partir d'un bloc de référence et de traiter une réorganisation.

Le protocole peut choisir de ne supporter qu'une liste de jetons explicitement autorisés. Cette politique réduit les surprises, mais nécessite une gouvernance transparente : qui ajoute un jeton, quelles vérifications sont faites, comment un actif est retiré de la liste et quelles conséquences cela a pour les utilisateurs déjà exposés ?

## 20. Cas pratique : suivre une approbation du début à la révocation

Une DApp d'échange peut demander à l'utilisateur d'approuver un contrat de marché avant de transférer ses jetons. La première transaction change allowance ; la transaction suivante utilise transferFrom pour déplacer les jetons. L'utilisateur peut croire qu'il a seulement « connecté » son portefeuille, alors qu'il a en réalité accordé une permission de dépense.

~~~mermaid
sequenceDiagram
    participant U as Utilisateur
    participant D as DApp
    participant T as Contrat ERC-20
    participant M as Contrat de marché
    U->>D: Choisir un montant à échanger
    D->>T: Demander une approbation limitée
    U->>T: Signer approve
    T-->>U: Événement Approval
    U->>M: Confirmer l'échange
    M->>T: transferFrom
    T-->>M: Transfert selon règles du jeton
~~~

### Avant la signature

L'interface devrait montrer l'adresse du spender, le montant autorisé, le jeton concerné et le réseau. Si l'opération requiert une allowance supérieure au montant de l'échange, il faut expliquer pourquoi. Un mécanisme permit n'enlève pas le risque de permission : il déplace le mode d'autorisation vers une signature, avec ses règles de domaine et de nonce.

### Après la signature

L'application doit attendre le reçu de l'approbation et relire allowance si l'opération suivante en dépend. Elle ne doit pas supposer que la permission est active immédiatement après que la fenêtre de portefeuille s'est fermée. Si la transaction est remplacée ou échoue, le montant autorisé peut rester inchangé.

Une révocation est une nouvelle transaction qui met l'autorisation à zéro ou à une valeur plus faible lorsque le contrat le permet. Elle aussi doit être confirmée avant d'annoncer qu'elle est effective. Le portefeuille peut proposer de réduire régulièrement les permissions, mais l'utilisateur doit connaître le coût de la transaction et le fait qu'une révocation n'annule pas un transfert déjà exécuté.

### Pourquoi la liste des jetons supportés est importante

Un protocole peut choisir de n'accepter que des jetons connus et vérifiés. Cette liste peut réduire les risques de frais de transfert, de rebasing ou de comportement inattendu. Il faut toutefois que la gouvernance de cette liste soit claire, et que les utilisateurs sachent qu'un jeton non supporté peut produire un comportement incorrect même s'il expose une interface ERC-20.

## 21. Émission, destruction et gouvernance de l'offre

Les standards ERC décrivent des interfaces, pas une politique monétaire complète. Un token peut suivre ERC-20 et avoir une offre fixe, un mécanisme d'émission contrôlé, des frais, une pause ou des pouvoirs de liste de blocage. L'intégrateur doit lire les fonctions et les rôles pour comprendre qui peut modifier l'offre et dans quelles conditions.

~~~mermaid
flowchart TD
    A["Lire les fonctions d'offre"] --> B{"Mint ou burn autorisé ?"}
    B -->|Oui| C["Identifier rôle, limite et événements"]
    B -->|Non| D["Vérifier l'offre initiale et les règles restantes"]
    C --> E["Évaluer le risque de gouvernance"]
    D --> E
    E --> F["Documenter la politique et tester"]
~~~

Pour un projet de points, le pouvoir de mint peut être voulu, mais il faut préciser qui l'exerce, avec quelles limites et quelle transparence. Pour un stablecoin ou un actif financier, le pouvoir de gel ou la possibilité de mise à niveau peuvent avoir un impact majeur sur les utilisateurs. Le standard ERC-20 ne répond pas à ces questions : elles viennent de l'implémentation et du modèle opérationnel.

### Contrats évolutifs

Lorsqu'un jeton utilise un proxy, le code de transfert peut changer sans que l'adresse de l'actif ne change. Cela apporte une capacité de correction, mais ajoute une hypothèse de confiance concernant l'administration. Le dossier d'intégration devrait préciser l'implémentation actuelle, qui peut la changer et comment la nouvelle version est annoncée.

Une DApp qui accepte un token doit décider ce qu'elle fera en cas de changement de code ou de politique. Certaines applications suivent des listes d'actifs approuvés et réévaluent les jetons en cas de mise à niveau ; d'autres peuvent interrompre les nouvelles positions tant qu'une revue n'est pas terminée.

## 22. Tests de conformité ERC-20/ERC-721 par propriétés

Au lieu de vérifier une seule transaction, formule les propriétés qui doivent rester vraies. Pour ERC-20, un jeton simple sans frais doit déplacer une quantité d'un solde à l'autre sans modifier arbitrairement le total supply. Pour ERC-721, un transfert doit faire correspondre ownerOf au nouveau propriétaire et appliquer les règles d'approbation appropriées.

| Propriété | Test positif | Test négatif |
|---|---|---|
| ERC-20 transfert | Solde émetteur baisse, destinataire augmente | Solde insuffisant |
| ERC-20 approval | Allowance correspond à la valeur signée | Dépense supérieure à allowance |
| ERC-721 propriété | ownerOf reflète le nouveau propriétaire | Transfert par un tiers non autorisé |
| ERC-721 réception sûre | Contrat compatible accepte le NFT | Contrat qui refuse la réception |
| Métadonnées | URI conforme au comportement attendu | URI inaccessible ou modifiable de façon inattendue |

Les propriétés doivent être adaptées au jeton : une commission de transfert ou un mécanisme de rebase change les attentes du modèle simple. Il ne faut pas déclarer un test comme échoué uniquement parce que le token a un comportement spécifique prévu, mais l'application doit avoir décidé si elle supporte ce comportement.

### Contrôle des événements

Les journaux sont utiles pour l'indexation, mais la DApp doit confirmer l'adresse du contrat et gérer les réorganisations. Les NFT brûlés, les approbations révoquées et les transferts d'un même jeton exigent une mise à jour correcte de l'état hors chaîne. Les tests d'intégration doivent inclure une reconnexion et une relecture des événements pour s'assurer que l'indexeur ne crée pas de doublons.

## 23. Dix questions d'entraînement avec corrigé

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

## 24. Challenge final : choisir un standard pour une application

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
