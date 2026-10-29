# Oracles (Chainlink)

## Encadré de mise en contexte

Un smart contract fonctionne dans un environnement où les nœuds doivent pouvoir reproduire la même exécution. Il ne peut donc pas interroger librement un site web, une API météo ou une base bancaire pendant son exécution et supposer que tous les nœuds obtiendront la même réponse. Les données extérieures doivent être apportées dans un format que les nœuds peuvent traiter de manière déterministe. Un **oracle blockchain** est un mécanisme qui relie des informations hors chaîne à des contrats on-chain.

Les oracles peuvent apporter des prix d'actifs, des taux de change, des données météorologiques, des résultats sportifs, des informations logistiques ou des résultats de calcul. Ils rendent les contrats plus utiles, mais ajoutent aussi des hypothèses de confiance et de disponibilité. Un contrat financier qui utilise un prix périmé peut liquider injustement une position ; un contrat qui fait confiance à une seule source peut être manipulé si cette source est erronée ou compromise.

Chainlink propose différents services et réseaux d'oracles, dont les Data Feeds pour certains types de données agrégées. La disponibilité, la méthode de calcul, la fréquence de mise à jour et les garanties varient selon le flux et le réseau. Il ne faut pas prendre un exemple de prix crypto/USD comme une règle universelle applicable à tous les flux.

Ce cours explique le problème de l'oracle, les flux de prix, la lecture de données par contrat, la fraîcheur, les décimales, les hypothèses de sécurité, les solutions de calcul automatisé et les stratégies de repli. Les exemples sont pédagogiques et doivent être adaptés aux adresses, versions et paramètres du réseau ciblé avant tout usage réel.

## Objectifs d'apprentissage

À la fin de ce cours, tu sauras :

- expliquer pourquoi un contrat ne peut pas lire directement n'importe quelle API pendant son exécution ;
- distinguer données on-chain, données hors chaîne et preuves présentées par un oracle ;
- décrire le rôle général de Chainlink Data Feeds et les limites d'une source de prix ;
- utiliser conceptuellement l'interface latestRoundData et decimals ;
- vérifier que les données sont positives, récentes et adaptées au réseau ;
- éviter les erreurs de précision et de conversion des unités ;
- analyser les risques de panne, de retard, de manipulation et de dépendance ;
- distinguer prix spot, prix agrégé, valeur économique et source de vérité ;
- comprendre les fonctions des oracles d'automatisation et de génération aléatoire vérifiable ;
- concevoir des contrôles, tests et mécanismes de repli adaptés au risque de l'application.

## 1. Le problème de l'oracle

Un contrat intelligent est exécuté par plusieurs nœuds qui doivent appliquer les mêmes règles et calculer le même état. Si une transaction demande au contrat de lire un site web, le résultat pourrait varier selon le nœud, l'instant, la région, le cache ou la disponibilité de l'API. Cette divergence rendrait le consensus difficile, voire impossible, si l'information extérieure était directement utilisée dans la transition d'état.

Un oracle résout cette difficulté en apportant la donnée dans une transaction, un flux ou une structure vérifiable par le contrat. Mais un oracle n'abolit pas la confiance dans le monde extérieur : il définit comment une valeur est collectée, vérifiée, agrégée, publiée et consommée.

~~~mermaid
flowchart TD
    W["Monde extérieur : marchés, capteurs, API"] --> O["Réseau ou service oracle"]
    O --> V["Collecte, validation ou agrégation"]
    V --> D["Donnée publiée sur chaîne"]
    D --> C["Smart contract lit la donnée"]
    C --> R["Décision on-chain"]
~~~

### 1.1 Le contrat ne peut pas croire une URL

Imaginons un contrat d'assurance qui indemnise automatiquement si les précipitations dépassent un seuil. Le contrat ne peut pas simplement appeler une API météo publique au moment où la transaction est exécutée. Les nœuds devraient obtenir la même réponse, alors que l'API peut être modifiée, indisponible, localisée ou différente selon la requête.

Le contrat doit recevoir une observation fournie selon des règles déterminées. Cette observation peut être signée, agrégée ou mise à disposition par un réseau d'oracle. L'application doit ensuite définir qui est autorisé à fournir la donnée, quelle plage de temps elle décrit, comment les conflits sont résolus et ce qui se passe en cas de panne.

### 1.2 L'oracle devient une dépendance de sécurité

Une application qui utilise un oracle dépend de la qualité du flux. Il faut examiner sa source, son modèle d'agrégation, son actualisation, sa disponibilité, les limites de son marché et les risques du réseau où il est publié. Plusieurs fournisseurs d'oracles ne garantissent pas nécessairement une diversité réelle si leurs données proviennent des mêmes sources ou si leurs infrastructures partagent les mêmes dépendances.

Le bon modèle de menace demande : quelle action le contrat prendra-t-il si la donnée est fausse, périmée ou indisponible ? Quel montant peut être perdu ? Existe-t-il une solution de pause ou une voie de récupération ? Qui contrôle ces mécanismes ? La réponse doit être écrite dans la conception plutôt que laissée à l'improvisation après incident.

## 2. Catégories de données oracle

Les oracles ne transportent pas tous le même type d'information. La catégorie du service détermine les hypothèses et contrôles nécessaires.

### 2.1 Flux de prix

Un flux de prix fournit une valeur de marché ou une valeur agrégée associée à une paire d'actifs ou à un indicateur. Les contrats de prêt, les systèmes de garantie, certains dérivés et d'autres applications financières l'utilisent pour calculer une valeur, une liquidation ou un ratio de couverture.

Un prix de flux n'est pas automatiquement le prix auquel un utilisateur peut acheter ou vendre la quantité exacte voulue. La valeur peut être agrégée à partir de sources et de règles particulières. Les écarts de marché, la liquidité, les périodes de volatilité et les différences entre plateformes peuvent affecter la pertinence d'un prix pour une application donnée.

### 2.2 Données événementielles

Une application peut dépendre d'un événement extérieur : résultat d'un match, livraison d'un colis, mesure environnementale ou franchissement d'un seuil. Il faut définir qui observe l'événement, comment il est prouvé, à quel moment il devient final et comment les litiges sont gérés.

Une donnée événementielle peut être ambiguë. Par exemple, que signifie « livraison effectuée » si un transporteur indique livré alors que le destinataire conteste ? Le contrat ne résout pas cette question à lui seul. Le système d'oracle et le cadre du produit doivent définir les sources et la procédure de contestation.

### 2.3 Automation

Les services d'automatisation peuvent surveiller une condition et déclencher une transaction lorsque la condition est remplie, selon les règles du service. Cela permet d'éviter que l'application exige une action manuelle permanente. Cependant, un mécanisme d'automatisation n'est pas un serveur omniscient : la condition et les fonctions appelables doivent être définies, les contraintes de gas anticipées, et les incitations et dépendances du service analysées.

### 2.4 Génération aléatoire vérifiable

Les contrats ont besoin de hasard pour certains jeux, tirages ou sélections. Une valeur telle que block.timestamp, un hash de bloc ou un nombre choisi par le premier utilisateur peut être manipulable ou prévisible dans certains contextes. Un service de hasard vérifiable fournit une valeur accompagnée d'une preuve que le contrat peut vérifier selon le protocole choisi.

La génération aléatoire sûre exige que le développeur gère la requête, la réponse, l'unicité de la demande et les cas d'échec. Un contrat ne doit pas permettre à un utilisateur de relancer indéfiniment un tirage jusqu'à obtenir un résultat favorable, ni traiter une valeur comme disponible avant que la preuve soit validée.

## 3. Chainlink Data Feeds : modèle général

Chainlink Data Feeds est une famille de flux de données utilisés par des contrats pour lire certaines valeurs publiées sur une blockchain. Les données sont généralement issues de plusieurs sources et d'un ensemble de nœuds opérateurs dans les systèmes concernés, mais le modèle exact dépend du flux, de la catégorie de données et du réseau. Certains flux ou valeurs particuliers peuvent avoir des méthodes de calcul ou des dépendances différentes ; il faut consulter la documentation du flux choisi.

Le développeur doit rechercher au minimum :

- le réseau ciblé et l'adresse du contrat de flux ;
- l'actif, la paire ou la grandeur représentée ;
- la devise de cotation et l'unité retournée ;
- la fonction de précision, par exemple decimals ;
- la méthode de lecture, comme latestRoundData lorsque l'interface du flux la propose ;
- les recommandations relatives à la fraîcheur et aux limites d'utilisation ;
- les conditions de service, la disponibilité et les risques connus pour ce flux.

L'adresse d'un flux ne doit pas être inventée ou copiée depuis un exemple destiné à un autre réseau. Même si deux flux portent un nom similaire, ils peuvent être déployés à des adresses différentes ou avoir une configuration différente. Utilise la liste officielle d'adresses du réseau et vérifie que l'actif et la paire correspondent exactement au besoin.

### 3.1 Proxy et implémentation sous-jacente

Certains flux sont servis via une adresse proxy dont l'implémentation peut être mise à jour selon l'architecture du service. Le contrat intégrateur utilise l'interface documentée du proxy et ne devrait généralement pas coder en dur l'adresse d'une implémentation interne. Les opérateurs peuvent gérer les détails du flux dans les limites du modèle de gouvernance du service.

Cette architecture rend les interfaces plus stables pour les consommateurs, mais elle ne signifie pas que le service est exempt de dépendance. Le consommateur doit vérifier l'adresse du proxy officielle, suivre la documentation et comprendre quelles garanties existent pour le flux et son réseau.

## 4. Lire une donnée de prix

Sur les flux EVM compatibles qui exposent l'interface AggregatorV3, la fonction latestRoundData renvoie plusieurs champs associés à la dernière observation disponible. L'un des champs centraux est answer, qui contient la valeur numérique du prix. Les champs temporels servent notamment à comprendre quand l'observation a été mise à jour. La fonction decimals donne la précision de la valeur.

Un contrat d'intégration doit vérifier plus que la simple réussite de l'appel. Selon le cas, il doit contrôler que la valeur est positive, que la donnée est suffisamment récente, que la précision est comprise et que le flux est adapté à l'usage. Les contrôles exacts dépendent de la documentation du service et du modèle de risque.

~~~mermaid
sequenceDiagram
    participant A as Application
    participant C as Contrat consommateur
    participant F as Contrat du flux
    A->>C: Demande une opération dépendant du prix
    C->>F: Lire la dernière observation
    F-->>C: Valeur, horodatages et métadonnées
    C->>C: Vérifier valeur, fraîcheur et unités
    C-->>A: Résultat ou erreur contrôlée
~~~

### 4.1 Exemple d'interface

Voici une interface Solidity illustrative compatible avec les méthodes couramment utilisées par les flux de prix de type AggregatorV3. Elle décrit uniquement les fonctions nécessaires à l'exemple. Dans un projet réel, préfère importer l'interface officielle appropriée et verrouiller la version de la dépendance.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPriceFeed {
    function decimals() external view returns (uint8);

    function latestRoundData()
        external
        view
        returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        );
}
~~~

Cette interface explique la forme du résultat, mais ne prouve pas que n'importe quelle adresse est un flux fiable. Si l'adresse configurée pointe vers un contrat différent, l'appel peut échouer ou retourner des données inattendues. Les adresses doivent être issues de la documentation officielle et contrôlées au déploiement.

### 4.2 Vérifier la valeur

Un prix négatif ou nul n'est généralement pas approprié pour une logique qui suppose une valeur de marché positive. Le contrat peut rejeter ce cas. La règle doit être adaptée à l'indicateur : certaines données non financières peuvent légitimement être nulles ou négatives. Il ne faut pas appliquer aveuglément le contrôle answer > 0 à tous les types de flux.

### 4.3 Vérifier la fraîcheur

updatedAt fournit une information temporelle associée à l'observation. Le contrat peut comparer ce champ avec block.timestamp afin de rejeter une valeur trop ancienne. Il faut toutefois choisir un seuil adapté au flux et à l'application. Une paire stable et liquide peut tolérer une fenêtre différente d'un actif très volatil ou d'un flux mis à jour selon d'autres conditions.

Le seuil ne doit pas être arbitraire. Trop strict, il peut bloquer le service en période de faible activité ou d'incident du flux. Trop large, il peut laisser utiliser un prix qui ne reflète plus le marché. La documentation du flux et une analyse des risques doivent guider ce choix. Le contrat doit aussi rejeter ou traiter séparément un updatedAt nul lorsqu'une donnée de mise à jour est attendue.

### 4.4 Contrat lecteur pédagogique

L'exemple suivant montre comment vérifier une valeur positive et une fraîcheur maximale. Il ne contient pas de fonction financière qui transfère des actifs et ne constitue pas un oracle complet de production. Le seuil est fourni au constructeur afin de rappeler qu'il doit être choisi selon le flux et le risque.

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

interface IPriceFeed {
    function decimals() external view returns (uint8);

    function latestRoundData()
        external
        view
        returns (
            uint80 roundId,
            int256 answer,
            uint256 startedAt,
            uint256 updatedAt,
            uint80 answeredInRound
        );
}

contract LecteurDePrix {
    IPriceFeed public immutable flux;
    uint256 public immutable ageMaximum;

    error PrixInvalide();
    error DonneePerimee();
    error HorodatageInvalide();

    constructor(address adresseFlux, uint256 ageMax) {
        require(adresseFlux != address(0), "Flux nul");
        require(ageMax > 0, "Age nul");
        flux = IPriceFeed(adresseFlux);
        ageMaximum = ageMax;
    }

    function lirePrix() external view returns (int256 prix, uint256 dateMiseAJour) {
        (, prix, , dateMiseAJour, ) = flux.latestRoundData();

        if (prix <= 0) revert PrixInvalide();
        if (dateMiseAJour == 0 || dateMiseAJour > block.timestamp) {
            revert HorodatageInvalide();
        }
        if (block.timestamp - dateMiseAJour > ageMaximum) {
            revert DonneePerimee();
        }
    }
}
~~~

Avant d'utiliser un contrat de ce type, il faut encore vérifier l'adresse et le réseau, lire decimals, interpréter correctement answer et définir un seuil réaliste. La fonction ci-dessus retourne la valeur brute : elle ne la convertit pas automatiquement dans une unité financière particulière. C'est volontaire, car la conversion dépend du flux et de l'application.

## 5. Décimales, précision et unités

Les réponses des flux de prix sont habituellement renvoyées sous forme d'entiers. Le nombre de décimales indique comment interpréter la valeur. Pour certaines classes de flux EVM, 8 décimales sont courantes pour les prix crypto/USD, mais il ne faut jamais coder cette convention comme une garantie universelle. Les flux et réseaux peuvent différer ; il faut lire decimals depuis le contrat de flux choisi ou vérifier la documentation officielle.

Supposons qu'un flux ait 8 décimales et renvoie la valeur entière 3 000 000 000 000. Le prix humain correspondant est 30 000. Si un autre flux utilise 18 décimales, la même valeur humaine aurait une représentation entière différente. Comparer deux réponses brutes sans normaliser les unités peut produire une erreur d'un facteur énorme.

### 5.1 Arithmétique entière

Solidity effectue de nombreuses opérations financières avec des entiers, pas avec des nombres décimaux à virgule flottante. Lorsqu'on calcule la valeur d'une quantité à partir d'un prix, il faut définir la précision intermédiaire, les arrondis et l'ordre des opérations. Une multiplication peut dépasser la plage d'un type ; une division perd généralement la partie fractionnaire. Les formules doivent être vérifiées mathématiquement et testées avec les valeurs extrêmes.

### 5.2 Précision du jeton et précision du flux

Une application peut combiner un jeton ERC-20 dont les montants utilisent 6 ou 18 décimales et un flux de prix dont l'answer possède une autre précision. Le calcul doit prendre en compte les deux. Il ne suffit pas de multiplier balanceOf par answer et d'afficher le résultat.

Il faut aussi définir la devise finale et son unité. Un calcul qui convertit un montant d'un jeton vers USD, puis vers une autre devise, doit explicitement normaliser chacune des valeurs et utiliser une logique d'arrondi adaptée à l'objectif. Une erreur de précision peut entraîner des liquidations trop précoces ou trop tardives, des limites incorrectes ou des erreurs d'affichage.

### 5.3 Éviter les flottants du frontend

Les applications web utilisent parfois des nombres JavaScript standards, qui sont représentés en virgule flottante binaire et ne peuvent pas représenter précisément tous les entiers suffisamment grands ou tous les décimaux. Pour des quantités financières, utilise les types entiers et fonctions de conversion de la bibliothèque web3, puis formate la valeur seulement pour l'affichage. L'affichage doit rester distinct de la valeur qui est envoyée au contrat.

## 6. Choisir le bon flux

Le développeur doit identifier précisément la paire et la chaîne. Un flux ETH/USD ne répond pas au même besoin qu'un flux ETH/EUR, et le prix d'un actif sur un réseau n'est pas automatiquement le prix d'un autre actif portant un nom similaire ailleurs. Les actifs enveloppés, les tokens avec rebasing et les actifs à liquidité faible peuvent avoir des risques particuliers de différence entre leur valeur attendue et le prix observable.

La disponibilité varie selon les réseaux et les catégories de flux. Avant le déploiement, vérifie si la paire précise existe sur le réseau visé, quelles sont les sources utilisées, les conditions de mise à jour, les unités, l'adresse officielle et les recommandations d'intégration. Il faut aussi examiner la qualité du marché concerné : un prix agrégé ne garantit pas que le volume du marché soit suffisant pour exécuter une transaction importante.

### 6.1 Prix de marché et liquidité

Un prix est une information, pas une garantie d'exécution. Si un protocole doit liquider une position importante, il doit tenir compte de la liquidité, du slippage, des limites des échanges et des conditions de marché. Une valeur d'oracle peut être correcte selon son objectif alors qu'une transaction de grande taille ne peut pas être exécutée exactement à ce prix.

Il faut séparer le calcul de valeur, la décision de liquidation et l'exécution réelle. Le contrat peut utiliser une valeur oracle pour vérifier un seuil, mais l'effet économique dépend aussi du mécanisme de marché et de la possibilité de réaliser l'opération.

### 6.2 Stablecoins et actifs enveloppés

Un stablecoin vise généralement une stabilité par rapport à un actif de référence, mais la parité peut être affectée par des risques de réserve, d'émetteur, de liquidité et de marché. Un actif enveloppé peut dépendre d'un dépositaire ou d'un pont. Le développeur ne doit pas supposer qu'un token se négocie toujours à sa valeur de référence.

Une application de prêt doit prévoir des variations, des écarts de prix et la possibilité que le marché fonctionne mal. Elle doit également définir quelles sources de prix sont utilisées pour un actif donné et comment elle traite l'absence de flux ou un écart anormal.

## 7. Risques des oracles

### 7.1 Données périmées

Un flux peut ne pas être actualisé selon l'intervalle attendu. Cela peut arriver en période de faible variation, d'incident, de congestion ou pour d'autres raisons propres au système. La fraîcheur doit être définie selon la logique de mise à jour réelle du flux. Le contrat peut refuser des données anciennes, mais il doit alors prévoir ce que l'application fait lorsque le flux est temporairement indisponible.

### 7.2 Source unique

Une API unique peut devenir indisponible, renvoyer une valeur erronée ou être manipulée. L'agrégation de plusieurs sources peut réduire certains risques, mais n'est utile que si les sources sont suffisamment indépendantes et que les règles d'agrégation sont comprises. Plusieurs endpoints qui recopient le même fournisseur ne sont pas une véritable diversité.

### 7.3 Manipulation de marché

Un marché peu liquide peut présenter un prix facilement manipulable. Si l'oracle reflète principalement ce marché ou si le protocole réagit immédiatement à un mouvement temporaire, un attaquant peut chercher à modifier le prix de référence. Les défenses incluent une sélection prudente des flux, des seuils, des limites de taille, des délais, une analyse des liquidités et des règles de pause ou de récupération.

### 7.4 Retard et censure

Un service oracle ou un opérateur peut ne pas publier une donnée en temps utile. Un contrat qui exige une mise à jour peut se bloquer si la donnée n'arrive plus. À l'inverse, accepter sans limite la dernière valeur peut maintenir le fonctionnement mais provoquer une mauvaise décision si le prix a fortement changé.

Le choix est un compromis entre disponibilité et sûreté métier. Une application devrait décider à l'avance si elle préfère suspendre les nouvelles opérations en cas de donnée périmée, limiter l'exposition, activer un mode prudent ou lancer une procédure d'urgence. Le comportement en panne doit être testé autant que le chemin normal.

### 7.5 Mauvaise configuration

Le développeur peut choisir le mauvais flux, le mauvais réseau, la mauvaise devise ou la mauvaise précision. Ce type d'erreur n'est pas une attaque cryptographique mais peut produire les mêmes conséquences financières qu'une donnée fausse. La configuration doit être vérifiée avant déploiement, revue par une seconde personne et testée avec des exemples de valeur connus.

### 7.6 Risque de contrat consommateur

Même lorsque le flux fonctionne comme prévu, le contrat consommateur peut être vulnérable : mauvais contrôle d'horodatage, conversion erronée, hypothèse sur decimals, logique de liquidation incorrecte ou gestion absente d'une réponse invalide. La sécurité dépend donc du service d'oracle et de l'intégration.

## 8. Concevoir un mécanisme de repli

Un mécanisme de repli définit ce que fait l'application lorsque le flux est indisponible, périmé ou incohérent. Il ne devrait pas être improvisé pendant l'incident.

Options possibles selon la criticité :
- refuser temporairement une nouvelle opération qui dépend du prix ;
- permettre certaines lectures mais suspendre les opérations qui transfèrent des fonds ;
- utiliser une source secondaire seulement si elle a été validée et si les règles de transition sont définies ;
- limiter la taille des opérations tant que la donnée est incertaine ;
- déclencher une procédure de gouvernance ou de pause avec des permissions protégées ;
- informer l'utilisateur que la donnée n'est pas disponible au lieu d'afficher un prix périmé comme s'il était actuel.

Utiliser une valeur de secours fixe peut être dangereux si le marché a fortement changé. Une moyenne de plusieurs flux n'est utile que si l'on sait comment gérer les valeurs aberrantes, les écarts et l'absence de l'un des flux. Une procédure d'urgence doit définir qui peut agir, dans quelles conditions, avec quelle traçabilité et comment revenir au fonctionnement normal.

## 9. Automation et hasard vérifiable

Les services d'oracle incluent des usages qui ne sont pas des flux de prix.

### 9.1 Automatisation d'une condition

Un service d'automatisation peut observer l'état d'un contrat et soumettre une transaction lorsque certaines conditions sont satisfaites. Le contrat doit rester responsable de la vérification finale : il ne doit pas supposer qu'une transaction externe est autorisée simplement parce qu'un service d'automatisation l'a appelée.

Les fonctions à automatiser doivent être idempotentes ou protégées contre les déclenchements répétés. Un service peut essayer plusieurs fois, la transaction peut être retardée, et la condition peut avoir changé entre la vérification hors chaîne et l'exécution on-chain. Le contrat doit revalider les conditions à l'instant d'exécution.

### 9.2 Génération aléatoire vérifiable

Pour un jeu ou un tirage, un service de hasard vérifiable peut fournir une valeur et une preuve. Le contrat doit demander un résultat, enregistrer un identifiant unique, attendre une réponse valide et empêcher qu'une même réponse soit consommée plusieurs fois. Si une demande reste en attente, la logique métier doit préciser si le participant peut annuler, relancer ou être remboursé.

Le hasard doit être conçu avec attention : l'ordre des transactions et les informations divulguées peuvent permettre des stratégies de manipulation. Le contrat doit éviter que l'organisateur ou un joueur puisse choisir d'accepter ou d'ignorer le résultat uniquement lorsque cela l'arrange.

## 10. Tester l'intégration oracle

Les tests doivent couvrir plus que la réponse normale d'un prix. Utilise une interface simulée en environnement local pour tester :

- prix positif et horodatage récent ;
- réponse nulle ou négative lorsque cela est invalide pour l'usage ;
- horodatage égal à zéro ;
- observation trop ancienne ;
- horodatage futur ou incohérent ;
- erreur de lecture ou adresse mal configurée ;
- décimales différentes de l'hypothèse initiale ;
- prix très élevé ou faible qui expose un débordement ;
- changement important de prix entre estimation et exécution ;
- comportement de repli lorsque le flux est indisponible.

Les tests simulés permettent de contrôler les cas extrêmes, mais ne prouvent pas que le vrai flux fonctionne sur le réseau cible. Il faut aussi valider l'adresse officielle, tester sur le réseau de test si l'intégration est disponible et vérifier les mises à jour de documentation avant déploiement.

### 10.1 Tests de propriétés

Pour un protocole financier, les propriétés à tester peuvent inclure : aucun calcul n'accepte un prix périmé ; une valeur invalide ne mène pas à un transfert ; la même requête d'automatisation ne peut pas exécuter deux fois l'action ; les conversions d'unité gardent des bornes connues ; une panne du flux ne fait pas passer le contrat dans un état où des actifs peuvent être retirés sans contrôle.

Le test doit considérer les interactions entre fonctions. Une vérification isolée de fraîcheur peut être correcte alors que la fonction de liquidation l'appelle avec une autre valeur ou n'applique pas la même vérification. Les contrôles critiques doivent être centralisés de manière lisible et leurs propriétés documentées.

## 11. TP guidé A : lire un flux de prix en sécurité

### Objectif

Apprendre à vérifier une intégration de prix sans envoyer de fonds. Le TP est réalisé en lecture seule avec une adresse de flux officielle pour le réseau choisi.

### Étape 1 — Identifier le flux

Consulte la documentation officielle Chainlink et sélectionne un flux qui existe sur le réseau de test ou le réseau approprié. Note la paire, l'adresse du proxy, le réseau, les décimales attendues et les recommandations de fraîcheur. Ne copie pas une adresse provenant d'un tutoriel qui cible un autre réseau.

### Étape 2 — Lire la valeur

Utilise un explorateur ou un environnement de lecture pour appeler decimals et latestRoundData, si le flux expose cette interface. Note answer, updatedAt et les autres métadonnées. Convertis la réponse avec la précision retournée au lieu de supposer qu'elle a toujours huit décimales.

### Étape 3 — Contrôler la fraîcheur

Compare updatedAt au temps courant du bloc et calcule l'âge de l'observation. Compare ce résultat aux recommandations du flux et au besoin de l'application. Ne choisis pas arbitrairement un seuil universel.

### Étape 4 — Écrire une fiche

La fiche doit contenir le réseau, l'adresse, la paire, les unités, la date de mise à jour, le contrôle de fraîcheur et les limites. N'utilise pas la valeur pour ouvrir une position financière ou déployer une logique de liquidation dans ce TP.

## 12. TP guidé B : définir la politique de panne d'un protocole

Imagine un protocole de prêt qui utilise un prix oracle pour calculer la valeur des garanties. Le flux n'est plus assez récent et les utilisateurs continuent d'envoyer des transactions. Rédige une politique qui explique quelles fonctions restent accessibles, quelles actions sont bloquées, comment les utilisateurs sont informés et qui peut déclencher la procédure de reprise.

### Étapes

1. Dresse la liste des fonctions qui dépendent du prix.
2. Classe-les par risque : lecture seule, dépôt, emprunt, liquidation ou retrait.
3. Définis un contrôle de fraîcheur et un traitement de valeur invalide.
4. Détermine si la panne doit bloquer toute opération ou seulement certaines opérations qui dépendent de la valorisation.
5. Définis comment valider le retour du flux.
6. Ajoute un journal ou événement qui aide à auditer l'incident sans exposer des secrets.
7. Teste une récupération et un nouvel incident.

### Corrigé indicatif

Une politique prudente peut laisser accessibles les lectures et les fonctions qui ne dépendent pas d'un prix fiable, tout en suspendant les nouvelles opérations qui exigent la valorisation tant que le flux n'est pas acceptable. Les retraits ne doivent pas être bloqués sans réflexion : leur traitement dépend du modèle de solvabilité et des risques de l'application. La reprise doit vérifier le flux et appliquer les mêmes conditions à toutes les transactions. Le seuil, les pouvoirs de pause et la procédure de communication doivent être documentés.

## 13. Dix questions d'entraînement avec corrigé

### Question 1
Pourquoi un contrat ne lit-il pas directement n'importe quelle API web ?

**Corrigé :** Les réponses pourraient varier entre les nœuds et rendre l'exécution non déterministe. Un oracle apporte une donnée selon un mécanisme compatible avec la validation du réseau.

### Question 2
Un oracle est-il automatiquement fiable parce qu'il publie sur chaîne ?

**Corrigé :** Non. Il faut évaluer les sources, l'agrégation, la disponibilité, les mises à jour, les hypothèses de confiance et le contrat consommateur.

### Question 3
À quoi sert decimals sur un flux de prix ?

**Corrigé :** À indiquer la précision de la réponse entière. Il faut lire la valeur réelle du flux plutôt que de supposer une constante universelle.

### Question 4
Pourquoi vérifier updatedAt ?

**Corrigé :** Pour déterminer si la donnée est assez récente pour l'usage. Une valeur très ancienne peut ne plus refléter les conditions pertinentes.

### Question 5
Une valeur positive prouve-t-elle que le prix est correct ?

**Corrigé :** Non. C'est un contrôle de validité élémentaire. La qualité dépend encore du flux, de la source, de la fraîcheur, de la paire et de la logique d'intégration.

### Question 6
Pourquoi un prix de flux n'est-il pas forcément le prix d'exécution ?

**Corrigé :** Le flux peut agréger des données de marché, alors qu'une transaction réelle dépend du volume, de la liquidité, du slippage et des conditions de marché.

### Question 7
Quelle est la différence entre un flux de prix et un service d'automatisation ?

**Corrigé :** Un flux apporte une donnée à lire ; un service d'automatisation peut surveiller une condition et soumettre une transaction. Le contrat doit toujours vérifier les règles à l'exécution.

### Question 8
Pourquoi un contrat devrait-il définir le comportement en cas de panne oracle ?

**Corrigé :** Pour éviter d'utiliser une donnée périmée ou de bloquer des opérations de manière imprévue. Le compromis entre disponibilité et sûreté métier doit être anticipé.

### Question 9
À quoi sert un service de hasard vérifiable ?

**Corrigé :** À apporter un résultat aléatoire avec une preuve vérifiable par le contrat, lorsque le hasard local ou certaines valeurs de bloc sont insuffisants.

### Question 10
La bonne intégration d'un oracle garantit-elle la sécurité de tout le protocole ?

**Corrigé :** Non. La logique financière, les conversions, les permissions, les contrats dépendants et les mécanismes de récupération doivent aussi être sûrs.

## 14. Challenge final : revue d'un oracle de prêt

### Scénario

Un protocole de prêt calcule le ratio de garantie d'un utilisateur à partir d'un flux ETH/USD. Le code lit answer mais ne vérifie ni decimals ni updatedAt. Le contrat permet d'emprunter tant que le ratio calculé paraît suffisant.

### Travail demandé

Rédige une revue de 500 à 700 mots qui énumère les problèmes, propose les contrôles nécessaires, explique les risques de fraîcheur et de précision et décrit les tests indispensables avant la mise en production. N'invente pas d'adresse de flux et précise que les paramètres doivent correspondre au réseau choisi.

### Correction proposée

La première faiblesse est l'hypothèse sur l'unité. La réponse du flux est un entier dont la précision doit être lue ou confirmée dans la documentation du flux précis. Si le contrat suppose une précision différente, le prix peut être mal interprété de plusieurs ordres de grandeur. Il faut définir une conversion cohérente entre les unités du solde du jeton, la précision de la réponse de prix et l'unité finale du ratio.

La deuxième faiblesse est l'absence de contrôle de fraîcheur. Une observation trop ancienne peut rester positive mais ne plus représenter la situation pertinente. Le contrat doit récupérer les métadonnées temporelles du flux, rejeter une valeur dont l'horodatage est invalide et appliquer une fenêtre maximale définie selon les recommandations et les besoins du marché. La fenêtre ne doit pas être copiée mécaniquement d'un autre flux.

Le contrat doit également vérifier que le prix est valide selon le sens de la donnée et que les calculs ne dépassent pas les plages numériques. Il faut tester les prix très bas et élevés, les montants importants, les arrondis et les situations proches du seuil de liquidation. Les contrôles de prix doivent être appliqués à chaque fonction sensible, pas seulement à une fonction de consultation.

L'équipe doit identifier le contrat de flux officiel pour le réseau réellement utilisé et vérifier son adresse ainsi que la paire exacte. Le test doit inclure les cas où le flux ne répond pas, renvoie des données anciennes ou présente une précision différente. Enfin, la procédure de panne doit préciser si les nouvelles demandes d'emprunt sont suspendues, comment les positions existantes sont traitées et qui peut activer la reprise. L'architecture doit éviter qu'une valeur de secours arbitraire permette d'emprunter ou de liquider selon un prix non fiable.

La vérification d'une interface de flux ne suffit pas. Les tests, l'analyse des contrats dépendants, la surveillance et une revue de sécurité indépendante sont nécessaires avant de risquer les fonds des utilisateurs. Les paramètres de production doivent être documentés, vérifiés par une seconde personne et contrôlés après le déploiement.

## Glossaire

**Answer :** valeur entière renvoyée par certaines interfaces de flux de prix.

**Chainlink Data Feeds :** famille de flux de données publiés sur chaîne selon des modèles propres au service et au réseau.

**Décimales :** précision qui permet d'interpréter une réponse entière en valeur lisible.

**Donnée périmée :** information dont l'horodatage est trop ancien par rapport au seuil accepté par l'application.

**Oracle :** mécanisme qui apporte des données extérieures à une blockchain selon une procédure de publication ou de vérification.

**Prix spot :** prix courant observé sur un marché précis, qui peut différer d'une valeur agrégée.

**Source de vérité :** source choisie par l'application comme référence, avec les hypothèses de confiance associées.

**Staleness / fraîcheur :** caractère suffisamment récent d'une donnée pour l'usage demandé.

**updatedAt :** champ temporel associé à une observation dans certaines interfaces de flux.

**Flux de prix :** interface qui fournit un prix ou une valeur de marché selon son modèle de données.

## Pour aller plus loin

- Documentation officielle Chainlink Price Feeds : https://docs.chain.link/data-feeds
- Sélection et qualité des flux : https://docs.chain.link/data-feeds/selecting-data-feeds
- Guide officiel d'intégration des Data Feeds : https://docs.chain.link/data-feeds/using-data-feeds
- Documentation officielle Chainlink Automation : https://docs.chain.link/chainlink-automation
- Documentation officielle Chainlink VRF : https://docs.chain.link/vrf
- Spécification Ethereum sur les smart contracts : https://ethereum.org/developers/docs/smart-contracts/

Les flux et interfaces disponibles dépendent du réseau et du service. Avant d'intégrer une donnée à un protocole financier, consulte la documentation du flux ciblé, valide l'adresse officielle, lis sa précision, définis la politique de fraîcheur et teste les conditions de panne. Un oracle peut améliorer l'utilité d'un contrat, mais il reste une dépendance critique qui doit faire partie du modèle de menace.
