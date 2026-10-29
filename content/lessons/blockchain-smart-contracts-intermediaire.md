# Smart contracts

## Encadré de mise en contexte

Un smart contract est un programme déployé sur une blockchain programmable et exécuté selon les règles du réseau. Il peut conserver un état, exposer des fonctions, vérifier des conditions et modifier des données partagées. Au lieu de confier chaque décision à un serveur appartenant à une entreprise, une application peut faire exécuter certaines règles par les nœuds d'un réseau. Cela rend le comportement inspectable et potentiellement vérifiable par plusieurs participants, mais n'élimine ni les bugs, ni la dépendance aux interfaces, ni les erreurs de conception.

Le terme « contrat intelligent » est parfois trompeur. Un smart contract n'est pas automatiquement un contrat juridique, il n'est pas capable de comprendre le monde réel et il ne corrige pas les ambiguïtés d'un cahier des charges. Il exécute du code. Si le code comporte une erreur, si une donnée externe est fausse ou si la gouvernance est mal conçue, l'exécution peut être techniquement conforme au programme tout en ayant des conséquences indésirables.

Cette leçon présente les concepts essentiels avant d'apprendre Solidity : compte de contrat, état, fonctions, appels, transactions, événements, gaz, ABI, déploiement, tests, composabilité, oracles et sécurité. L'objectif est de construire le modèle mental nécessaire pour lire un contrat, comprendre ce qu'il promet réellement et éviter les erreurs les plus fréquentes.

## Objectifs d'apprentissage

À la fin de la leçon, tu sauras :
- définir un smart contract et expliquer où se trouvent son code et son état ;
- distinguer une lecture, un appel de simulation et une transaction qui modifie l'état ;
- comprendre les fonctions, les événements, les erreurs et les permissions ;
- décrire le parcours entre le portefeuille, le fournisseur RPC, le contrat et les validateurs ;
- expliquer le rôle de l'ABI et du bytecode ;
- comprendre les coûts de gaz, les limites d'exécution et les transactions qui échouent ;
- expliquer la composabilité, les dépendances et les oracles ;
- identifier les risques de réentrance, d'accès non autorisé, de données périmées et de gouvernance ;
- suivre un cycle de développement sûr : conception, test, audit, déploiement, vérification et surveillance ;
- réaliser un mini-projet simple sans gérer de fonds réels.

## 1. Définition : un programme dans l'état partagé

Dans Ethereum, un smart contract est du code qui réside à une adresse de la blockchain et qui peut être exécuté lorsque des transactions ou d'autres contrats l'appellent. Il possède un état persistant défini par le protocole. Cet état peut contenir des valeurs comme un compteur, un solde comptable, des paramètres, une liste d'administrateurs ou les enregistrements d'un vote.

Un contrat n'est pas un processus qui tourne continuellement comme un serveur web. Il s'exécute en réaction à une transaction ou à un appel. Le réseau n'héberge pas un démon individuel par contrat qui serait constamment en train d'écouter Internet ; les clients exécutent les opérations demandées selon les règles de la machine virtuelle et mettent à jour l'état lorsqu'une transaction valide est incluse.

Une image utile est celle d'un distributeur automatique. Le distributeur accepte certaines entrées, vérifie certaines conditions et applique les règles programmées. Mais un smart contract diffère d'une machine physique : son état et son exécution sont reproduits selon les règles du réseau, les transactions sont ordonnées dans un historique partagé et les ressources de calcul sont facturées par le protocole.

~~~mermaid
flowchart TD
    U["Utilisateur"] --> W["Portefeuille : construit et signe"]
    W --> RPC["Nœud ou fournisseur RPC"]
    RPC --> NET["Réseau et consensus"]
    NET --> EVM["Exécution du bytecode"]
    EVM --> S["Mise à jour de l'état"]
    S --> R["Reçu et événements observables"]
    R --> UI["Interface affiche le résultat"]
~~~

### 1.1 Ce que le contrat peut faire

Selon le langage, la machine virtuelle et les permissions, un contrat peut lire des paramètres ou un état persistant, vérifier qui appelle une fonction, accepter ou refuser une opération, calculer un résultat déterministe, enregistrer une nouvelle valeur, émettre des événements, appeler un autre contrat, transférer des actifs selon les règles prévues ou appliquer des règles de vote.

Les fonctions exactes dépendent du code. Le protocole garantit surtout que les clients conformes appliquent les règles de la même façon aux mêmes données et au même état de départ. Il ne garantit pas que le programme réalise l'intention de son auteur.

### 1.2 Ce qu'un contrat ne fait pas automatiquement

Un contrat ne peut pas spontanément consulter un site web, lire un fichier sur l'ordinateur d'un utilisateur, connaître l'heure exacte du monde réel ou vérifier qu'un colis a été livré. Pour intégrer des données extérieures, il faut qu'une transaction apporte l'information ou qu'un mécanisme d'oracle fournisse une valeur. L'oracle introduit des hypothèses spécifiques : source, disponibilité, intégrité, fraîcheur et modèle de confiance.

Un contrat n'est pas non plus automatiquement confidentiel. Sur une blockchain publique, son bytecode et son état accessible peuvent être inspectés, et les transactions peuvent révéler des informations. Même lorsqu'un contrat n'expose pas directement une variable, les données peuvent être retrouvées depuis le stockage ou les traces si le protocole les rend consultables.

Enfin, un contrat ne sait pas si une opération est équitable ou légale par simple lecture du code. Une équipe peut ajouter des conditions et des mécanismes de gouvernance, mais il demeure nécessaire de traiter les questions juridiques, humaines et opérationnelles séparément.

## 2. Cycle de vie d'un smart contract

Un contrat suit généralement plusieurs étapes : conception, programmation, compilation, tests, déploiement, vérification, interaction et maintenance autour de ses dépendances. Chacune peut introduire des risques.

~~~mermaid
flowchart TD
    A["Définir le besoin et les menaces"] --> B["Concevoir règles et permissions"]
    B --> C["Écrire le code source"]
    C --> D["Compiler en bytecode"]
    D --> E["Tester et analyser"]
    E --> F{"Critères de sécurité satisfaits ?"}
    F -->|Non| C
    F -->|Oui| G["Déployer sur réseau de test"]
    G --> H["Vérifier comportement et coûts"]
    H --> I["Revue et audit"]
    I --> J["Déployer sur réseau cible"]
    J --> K["Surveiller événements et dépendances"]
~~~

### 2.1 Conception avant codage

Avant d'écrire un contrat, il faut décrire les acteurs, les actifs, les invariants et les scénarios interdits. Un invariant est une propriété qui doit rester vraie après chaque opération autorisée. Exemples : un utilisateur ne peut pas retirer plus que son solde ; une proposition ne peut pas être exécutée deux fois ; seuls les rôles prévus peuvent modifier les paramètres ; une somme distribuée ne peut pas dépasser la réserve disponible.

Une spécification de qualité comprend les cas normaux, les erreurs attendues, les attaques envisageables et les hypothèses externes. Si les règles sont ambiguës, le code ne choisira pas nécessairement l'interprétation souhaitée. Le programme applique l'interprétation que le développeur a réellement encodée.

### 2.2 Compilation et bytecode

Le code source Solidity est généralement compilé en bytecode que la machine virtuelle peut exécuter. Le bytecode déployé est la représentation effectivement exécutée sur le réseau. Une ABI décrit les fonctions, paramètres, valeurs de retour et événements que l'application peut utiliser pour encoder et décoder les interactions.

Le source lisible et le bytecode doivent correspondre. Les outils de vérification de source permettent aux utilisateurs de comparer les paramètres de compilation et le code publié avec le bytecode déployé. Un contrat non vérifié peut être authentique, mais le public dispose de moins d'éléments simples pour analyser son fonctionnement. Une vérification de source n'est pas à elle seule un audit de sécurité.

### 2.3 Déploiement

Déployer un contrat est une transaction qui contient le code de création ou le bytecode de déploiement. Le réseau exécute les opérations de création et, si elles réussissent, associe le code à une nouvelle adresse. Le déploiement consomme du gaz et dépend du réseau, du portefeuille, du fournisseur RPC, des paramètres de transaction et de la disponibilité des fonds nécessaires.

Les tests doivent être effectués sur des réseaux locaux ou de test avant tout déploiement avec des actifs réels. Un contrat déployé sur un réseau public peut être difficile ou impossible à modifier selon sa conception. Les stratégies de mise à niveau sont des choix architecturaux à comprendre, pas une propriété automatique de tous les contrats.

## 3. Fonctions, données et état

Un contrat comprend habituellement des variables d'état, des fonctions et éventuellement des événements, modificateurs, structures et erreurs personnalisées. Les variables d'état représentent les informations conservées par le contrat. Les variables locales servent au calcul d'une invocation et ne persistent pas nécessairement dans l'état partagé.

Une fonction peut lire l'état, modifier l'état, recevoir de la valeur native, appeler d'autres contrats ou retourner un résultat à l'appelant. Les règles de visibilité et de mutabilité influencent la manière de l'appeler. Les fonctions publiques ou externes ne doivent pas être considérées comme privées simplement parce que l'interface utilisateur ne les affiche pas.

Exemple pédagogique de compteur :

~~~solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract Compteur {
    uint256 private valeur;

    event ValeurModifiee(address indexed auteur, uint256 nouvelleValeur);

    function lire() external view returns (uint256) {
        return valeur;
    }

    function incrementer() external {
        valeur += 1;
        emit ValeurModifiee(msg.sender, valeur);
    }

    function definir(uint256 nouvelleValeur) external {
        require(nouvelleValeur <= 1000, "Valeur hors limite");
        valeur = nouvelleValeur;
        emit ValeurModifiee(msg.sender, valeur);
    }
}
~~~

Ce code illustre des notions de base, mais il ne constitue pas un système complet de production. Toute personne peut appeler incrementer et definir. La limite de valeur n'est qu'une règle d'exemple. Si une fonction était censée être réservée à un administrateur, il faudrait mettre en œuvre des contrôles de permission et tester les chemins d'accès.

### 3.1 Visibilité et autorisation

En Solidity, la visibilité indique comment une fonction ou une variable peut être accédée par le code et l'extérieur. Elle ne remplace pas nécessairement le contrôle d'autorisation. Une fonction publique ne signifie pas qu'elle est réservée au public d'une manière sécurisée ; cela signifie qu'elle peut être appelée selon les règles de visibilité. Les conditions d'accès doivent être encodées séparément.

La valeur msg.sender désigne l'appelant immédiat de l'appel courant. Si un contrat A appelle un contrat B, B voit généralement A comme appelant immédiat, et non l'utilisateur original. Cette distinction est importante pour les permissions, les frais et la logique d'authentification. Les développeurs doivent comprendre le chemin des appels au lieu de supposer qu'une adresse de portefeuille reste toujours l'appelant visible.

Les fonctions administratives nécessitent une politique claire : qui peut les appeler, comment le rôle est transféré, comment une clé est récupérée ou remplacée, et quelles actions sont protégées par plusieurs personnes ou une multisignature. Une seule clé administrateur peut devenir un point de défaillance si elle est perdue ou compromise.

### 3.2 Événements

Un contrat peut émettre des événements pour signaler qu'une action s'est produite. Les événements sont enregistrés dans les journaux de transaction et peuvent être indexés par des applications, des explorateurs et des systèmes de surveillance. Ils sont utiles pour suivre les changements sans interroger constamment toutes les valeurs.

Un événement n'est pas une variable d'état que le contrat peut lire arbitrairement dans le futur. Il s'agit d'une trace d'exécution visible hors chaîne selon les règles du réseau. Une application qui s'appuie sur des événements doit tenir compte des réorganisations, de la finalité et du fait qu'un indexeur peut être en retard. Pour l'état courant, il peut être nécessaire de lire directement le contrat ou de vérifier le statut de la chaîne.

### 3.3 Erreurs et retours

Les contrats utilisent des vérifications et des mécanismes d'erreur pour arrêter une exécution qui ne respecte pas les conditions prévues. Un appel qui échoue peut renvoyer des données d'erreur à l'interface, mais cette donnée peut être absente, transformée ou masquée par une couche intermédiaire. Il faut tester les chemins de succès et d'échec et afficher un message utile sans interpréter arbitrairement tout échec comme un bug du réseau.

Une transaction qui échoue lors de l'exécution peut quand même consommer du gaz. Les ressources déjà dépensées pour exécuter les instructions doivent être payées selon les règles du protocole. L'utilisateur doit donc distinguer une estimation du gaz, une transaction soumise, un reçu inclus et un statut d'exécution.

## 4. Lire et écrire : deux types d'interaction

Une lecture qui n'altère pas l'état peut souvent être simulée par un appel de lecture, couramment exposé via les interfaces RPC comme une opération eth_call. Elle n'est pas nécessairement inscrite dans un bloc et ne nécessite pas de frais de transaction payés par l'appelant, même si la requête peut utiliser les ressources d'un fournisseur. L'état lu correspond au bloc ou au contexte demandé, qui peut être légèrement différent de l'état le plus récent.

Une écriture qui modifie l'état exige normalement une transaction signée par un compte ou un mécanisme d'autorisation. Elle doit être diffusée et incluse dans un bloc pour que la mise à jour soit persistante dans l'état partagé. Elle consomme du gaz et peut être retardée, remplacée selon les règles ou échouer à l'exécution.

~~~mermaid
flowchart LR
    U["Utilisateur"] --> A["Interface DApp"]
    A --> R{"Lecture ou écriture ?"}
    R -->|Lecture| CALL["Appel de lecture à un nœud"]
    CALL --> DATA["Résultat selon l'état demandé"]
    R -->|Écriture| W["Portefeuille prépare et signe"]
    W --> TX["Transaction diffusée"]
    TX --> BL["Inclusion dans un bloc"]
    BL --> EX["Exécution et reçu"]
    EX --> NEW["Nouvel état si succès"]
~~~

Une interface doit expliquer les différences. Afficher « enregistré » dès que le portefeuille a accepté une demande est trompeur si la transaction n'a pas été incluse. Il est préférable de distinguer préparation, signature, diffusion, inclusion, succès d'exécution et confirmation ou finalité.

## 5. Gaz et limites d'exécution

Le gaz est une unité de ressource facturée par le protocole Ethereum. Les instructions de la machine virtuelle consomment des quantités de gaz selon les règles déterminées par le réseau. Le gaz limite le coût d'exécution et aide à empêcher qu'un programme consomme des ressources infinies pendant le traitement d'une transaction.

La consommation ne correspond pas simplement au temps CPU mesuré sur une machine. Elle est une mesure définie par les règles de la machine virtuelle. Deux exécutions qui utilisent les mêmes opérations protocolaires consomment les quantités de gaz définies par le protocole, même si les machines physiques ne sont pas identiques.

Le coût payé dépend du gaz consommé et des paramètres de frais de la transaction. Une fonction qui parcourt un tableau de taille variable peut devenir plus coûteuse lorsque le tableau grandit. Un contrat qui effectue des boucles sans limites peut finir par être impossible à utiliser dans une transaction ordinaire. Les développeurs doivent concevoir la complexité, les structures de données et les chemins d'exécution en tenant compte de ces limites.

### 5.1 Estimation et échec

Un logiciel peut estimer la quantité de gaz nécessaire en simulant une transaction, mais une estimation n'est pas une garantie. L'état peut changer avant l'inclusion, le chemin d'exécution réel peut différer, une dépendance peut changer ses paramètres ou le prix des frais peut évoluer. Une limite trop basse peut faire échouer une transaction ; une limite trop élevée peut réserver inutilement des ressources dans certains contextes, même si le coût facturé dépend des règles effectives.

Les tests doivent couvrir les entrées extrêmes et les états rares, pas seulement le cas heureux. Par exemple, une opération peut réussir avec dix éléments dans une liste et échouer lorsque la liste en contient plusieurs milliers. Une revue de sécurité doit inclure les coûts et la capacité des utilisateurs à effectuer les opérations de sortie.

### 5.2 Coûts persistants

Les écritures dans l'état durable peuvent être plus coûteuses que de simples calculs temporaires. Une architecture efficace évite de stocker des données inutiles sur chaîne et réfléchit aux informations qui doivent être publiques, persistantes et accessibles à long terme. Il faut toutefois éviter une optimisation excessive qui rendrait le code illisible ou introduirait des calculs fragiles.

L'optimisation doit suivre les mesures et tests. Le plus petit bytecode n'est pas automatiquement le meilleur contrat si les compromis rendent les risques plus difficiles à analyser. Les contrats gérant des fonds doivent privilégier l'exactitude et la simplicité, puis optimiser seulement les points qui ont été identifiés et testés.

## 6. ABI et interface d'application

L'ABI (Application Binary Interface) décrit comment encoder les appels de fonctions, décoder les résultats et interpréter les événements d'un contrat. Elle constitue un accord entre l'interface d'une application et le bytecode déployé. Une application peut utiliser l'ABI avec une bibliothèque web3 pour préparer une requête et convertir les données binaires en valeurs lisibles.

L'ABI n'est pas un système d'authentification, ni une preuve que le contrat déployé correspond à un projet annoncé. Elle décrit les fonctions attendues. Il faut vérifier l'adresse du contrat, le réseau, le bytecode et la source si l'on doit lui faire confiance. Un nom de fonction identique à celui d'un contrat réputé ne prouve pas qu'il s'agit du même code.

### 6.1 Adresses et chaînes

Une adresse de contrat ne doit pas être interprétée indépendamment du réseau. La même chaîne de caractères peut exister sur des réseaux différents et désigner des contrats différents. L'interface doit vérifier le chain ID, la bonne adresse et les paramètres du déploiement. Un utilisateur qui interagit avec une adresse correcte sur un réseau incorrect peut obtenir un résultat inattendu ou perdre des fonds si des actifs réels sont impliqués.

### 6.2 Lecture à partir des événements

Pour construire un tableau de bord, une application peut écouter les événements et les stocker dans un indexeur. Cette architecture améliore les performances et permet des recherches historiques, mais ajoute un service hors chaîne qui doit se synchroniser, gérer les réorganisations et détecter les incohérences. L'indexeur n'est pas l'état normatif du contrat : il est une vue construite à partir des données du réseau.

## 7. Composabilité et appels entre contrats

L'un des avantages majeurs des smart contracts est la composabilité : un contrat peut appeler un autre contrat et réutiliser ses fonctions. Un protocole de prêt peut interagir avec un jeton, un oracle et un échange décentralisé. Une application peut assembler des primitives déjà disponibles au lieu de tout recréer.

~~~mermaid
flowchart TD
    D["DApp de prêt"] --> L["Contrat de prêt"]
    L --> T["Contrat de jeton"]
    L --> O["Contrat oracle"]
    L --> E["Contrat d'échange"]
    T --> S["État partagé du jeton"]
    O --> P["Prix fourni par le mécanisme oracle"]
    E --> M["Liquidité et prix de marché"]
~~~

La composabilité crée une puissance et un risque. Un contrat dépend de la logique, de l'état et des permissions des contrats qu'il appelle. Une modification d'un paramètre oracle peut avoir un effet sur les liquidations. Un contrat appelé peut contenir un bug ou être mis à niveau. Une application qui dépend de plusieurs composants doit comprendre les hypothèses de chaque composant.

Un audit limité au contrat principal peut manquer une vulnérabilité située dans une dépendance. Il faut considérer le système complet : bibliothèques, contrats externes, oracles, ponts, rôles d'administration, indexeurs et interfaces.

### 7.1 Appels externes

Un appel externe transfère le contrôle à un autre contrat. Celui-ci peut exécuter du code arbitraire dans les limites du protocole, appeler d'autres contrats et potentiellement rappeler le contrat initial. Cette propriété rend nécessaire une analyse du flux de contrôle. Le code ne doit pas présumer qu'un appel externe est toujours simple ou inoffensif.

Il faut également examiner les valeurs de retour et les erreurs. Certaines interactions peuvent échouer, certains contrats peuvent être malveillants, et des interfaces incompatibles peuvent provoquer une mauvaise interprétation des données. Les contrats doivent définir comment ils réagissent à l'échec d'une dépendance.

## 8. Oracles et monde réel

Les contrats sont exécutés de manière déterministe par les nœuds, ce qui rend difficile l'accès direct à une donnée web arbitraire : si chaque nœud récupérait des réponses Internet différentes à des moments différents, les résultats d'exécution pourraient diverger. Un oracle est un mécanisme qui rend une information extérieure disponible sous une forme que le contrat peut vérifier et traiter.

Les oracles peuvent fournir des prix, des données météorologiques, des résultats de livraison, des taux de change ou d'autres informations. Mais le contrat dépend alors de la qualité de la source et du protocole de transmission. Un oracle peut être en retard, manipulé, indisponible ou mal configuré. Une application financière doit définir comment elle réagit à des données périmées, à des valeurs extrêmes ou à une absence de mise à jour.

Un oracle décentralisé peut agréger plusieurs sources, imposer des garanties économiques et fournir des mécanismes de mise à jour. Il réduit certaines dépendances, mais ne supprime pas toutes les hypothèses. Le modèle de menace doit expliciter le nombre d'opérateurs, la diversité des sources, les seuils, la fraîcheur et les procédures en cas d'incident.

## 9. Sécurité des smart contracts

Le code exécuté sur une blockchain peut contrôler des actifs de valeur. Une vulnérabilité ne se corrige pas toujours par un redémarrage du serveur ou une restauration de sauvegarde. Selon la conception, les utilisateurs peuvent perdre des fonds, un état peut devenir irrécupérable ou l'équipe peut devoir recourir à une procédure de mise à niveau ou à une intervention de gouvernance.

### 9.1 Contrôles d'accès

Chaque fonction sensible doit avoir une politique de permission explicite. Qui peut modifier un paramètre ? Qui peut suspendre une fonctionnalité ? Qui peut ajouter un administrateur ? Le contrat doit limiter les changements de rôle et empêcher les appels non autorisés. Les rôles doivent être testés avec des comptes qui ne disposent pas des permissions, pas seulement avec le compte du développeur.

Un contrôle d'accès doit également prévoir le transfert et la récupération des responsabilités. Une clé perdue peut bloquer un protocole ; une clé compromise peut permettre à un attaquant de modifier des paramètres. Une architecture multisignature ou une gouvernance à délai peut réduire certains risques, mais ajoute de la complexité et doit être testée.

### 9.2 Réentrance

La réentrance peut se produire lorsqu'un contrat effectue un appel externe avant d'avoir mis à jour son état interne, et que le contrat appelé revient appeler le premier avant la fin de l'opération initiale. Si la logique n'a pas été conçue pour ce scénario, l'attaquant peut répéter une action dans un état qui n'a pas encore été actualisé.

Un modèle de défense couramment enseigné est Checks-Effects-Interactions : vérifier les conditions, mettre à jour l'état, puis interagir avec les contrats externes. Ce modèle n'est pas une garantie absolue ; il doit être appliqué avec une compréhension du flux de contrôle, des callbacks et des dépendances. Des verrous de réentrance peuvent aider dans certains cas, mais ils ne corrigent pas une conception globale erronée.

### 9.3 Calculs, autorisations et état

Les contrats doivent gérer les limites numériques, les valeurs nulles, les tableaux, les conversions, l'arrondi et les cas extrêmes. Les versions modernes de Solidity vérifient de nombreux dépassements arithmétiques dans le code ordinaire, mais cela ne rend pas toutes les opérations sûres. Les conversions explicites, les divisions, les arrondis financiers et les formules mal conçues peuvent toujours créer des erreurs.

Les contrats doivent également éviter d'utiliser des valeurs qui peuvent être manipulées ou qui ne disposent pas de la fraîcheur attendue. Un prix venu d'un oracle peut nécessiter un contrôle d'âge. Un mécanisme de vote peut devoir tenir compte des prêts temporaires ou des changements de solde. Une distribution peut devoir éviter de traiter deux fois le même message.

### 9.4 Dépendances et privilèges administratifs

Le mot « décentralisé » ne suffit pas pour décrire une application. Un propriétaire peut disposer d'une fonction de pause, d'une fonction de mise à jour ou d'un contrôle sur une liste blanche. Ces pouvoirs peuvent être utiles en cas d'urgence, mais ils doivent être documentés et protégés. Les utilisateurs doivent savoir qui possède ces pouvoirs et ce qui se passe si cette personne est compromise ou se comporte mal.

Une mise à niveau à travers un proxy peut modifier le code logique sans changer l'adresse utilisée par les utilisateurs. Cela peut être un mécanisme pratique, mais introduit le risque que le code soit changé par une autorité. Il faut examiner qui peut mettre à niveau, les délais, les votes et les possibilités de sortie.

### 9.5 Éviter de réinventer les primitives

Des bibliothèques largement examinées, comme OpenZeppelin Contracts, offrent des composants réutilisables pour les rôles, les jetons et d'autres modèles. Leur usage réduit certains risques par rapport à une implémentation improvisée, mais n'élimine pas la nécessité de vérifier les versions, la configuration, l'intégration et les hypothèses de l'application.

Les contrats doivent être testés, analysés par des outils adaptés, revus par des pairs compétents et, pour les actifs importants, audités selon un processus proportionné au risque. Un audit n'est pas une garantie éternelle : le code peut changer, des dépendances peuvent être mises à niveau et de nouvelles techniques d'attaque peuvent apparaître.

## 10. Immutabilité et évolutivité

Un contrat déployé n'est pas automatiquement modifiable. Dans de nombreux cas, son code est fixé à son adresse. Les données d'état peuvent changer par les fonctions prévues, mais la logique du code reste la même. Certaines architectures utilisent des proxies et des contrats d'implémentation pour permettre des mises à niveau. D'autres choisissent volontairement l'immutabilité pour réduire les pouvoirs administratifs.

Il existe donc un compromis : un contrat immuable peut offrir des garanties sur l'absence de modification unilatérale, mais il peut aussi rendre un bug difficile à corriger. Un contrat évolutif permet une réponse aux vulnérabilités, mais impose de faire confiance à la procédure de mise à niveau et à ses acteurs. Aucune option n'est universellement optimale.

La documentation devrait préciser le modèle retenu. Les utilisateurs doivent savoir si l'adresse du contrat restera liée au même code, si les paramètres peuvent être changés, si un administrateur peut suspendre les opérations et quelles conditions gouvernent une mise à niveau. Ces pouvoirs font partie de la sécurité du système, pas d'un simple détail de gestion.

## 11. Tests : preuve de comportement et limites

Un test automatisé appelle les fonctions du contrat dans un état contrôlé et compare le résultat attendu au résultat observé. Les tests unitaires couvrent des fonctions précises. Les tests d'intégration couvrent les interactions entre contrats. Les tests de propriétés explorent de nombreuses entrées et vérifient que certaines invariants restent vraies. Les tests de fuzzing cherchent des cas qui n'ont pas été écrits manuellement.

Exemples d'invariants pour un coffre simple :
- le total des retraits d'un utilisateur ne dépasse pas ses dépôts enregistrés ;
- seul le détenteur d'un rôle peut modifier un paramètre protégé ;
- chaque demande de retrait ne peut être exécutée qu'une fois ;
- les données persistées restent cohérentes après les erreurs ;
- une transaction échouée ne laisse pas un état partiellement modifié qui viole les règles du contrat.

Les tests ne prouvent pas l'absence de bug. Ils vérifient le comportement sur les scénarios testés. Pour les systèmes à forte valeur, il faut combiner tests, analyse statique, revue de code, tests de propriétés, audit, limites d'exposition et surveillance après le déploiement.

## 12. TP guidé A : utiliser un environnement de test

### Objectif

Compiler et tester un contrat minimal sans utiliser de fonds réels. Le TP peut être réalisé dans un environnement pédagogique comme Remix, en choisissant un environnement local ou un réseau de test pris en charge.

### Étape 1 — Créer le contrat

Recopie le contrat Compteur présenté plus haut. Lis les variables, les fonctions et l'événement. Avant de compiler, écris les permissions que tu observes et celles qui manquent. Tu devrais noter que tout utilisateur peut appeler les deux fonctions d'écriture.

### Étape 2 — Compiler

Choisis un compilateur Solidity compatible avec la directive de version du code et examine les avertissements. N'ignore pas un avertissement simplement parce que la compilation réussit. La compilation signifie que le compilateur a produit un résultat selon ses règles, pas que le programme est sûr.

### Étape 3 — Déployer localement

Utilise l'environnement local de l'outil, sans fonds réels. Déploie le contrat puis appelle lire. Appelle incrementer et vérifie que la valeur change. Appelle definir avec une valeur valide, puis une valeur supérieure à la limite ; observe la différence entre succès et revert.

### Étape 4 — Tester la limite d'accès

Ajoute un contrôle d'accès dans une copie séparée du contrat, par exemple une adresse propriétaire définie dans le constructeur. Teste la fonction avec le propriétaire puis avec une adresse différente. Ne considère pas un test effectué uniquement depuis le compte du développeur comme suffisant.

## 13. TP guidé B : examiner un contrat existant

Choisis un contrat publié sur un réseau de test ou un contrat connu qui dispose d'une source vérifiée. Ne lui envoie pas d'actifs. Vérifie l'adresse et le réseau, lis l'ABI et identifie les fonctions de lecture et d'écriture, les événements, les rôles administratifs et les dépendances.

Crée un tableau à quatre colonnes : élément, fonction observée, risque ou hypothèse, vérification à effectuer. Note au moins huit éléments. Il peut s'agir de l'adresse du propriétaire, des paramètres modifiables, d'une fonction de pause, d'une logique de retrait, d'un oracle, d'une dépendance externe, d'un mécanisme de mise à niveau et de la manière dont les événements sont indexés.

### Corrigé indicatif

Une inspection ne devrait pas conclure « sûr » ou « dangereux » à partir du nom des fonctions. Il faut comprendre la logique complète et le contexte. Une fonction de pause peut protéger les utilisateurs lors d'un incident, mais aussi permettre de bloquer les retraits. Un proxy peut permettre des correctifs, mais il faut identifier qui contrôle la mise à niveau. Une source vérifiée améliore la transparence, sans remplacer un audit ou les tests.

## 14. Dix questions d'entraînement avec corrigé

### Question 1
Qu'est-ce qu'un smart contract ?

**Corrigé :** Un programme déployé à une adresse sur une blockchain programmable, dont le code et l'état sont exécutés selon les règles du réseau.

### Question 2
Un contrat intelligent est-il automatiquement un contrat juridique ?

**Corrigé :** Non. Le terme désigne une catégorie de programme. Sa qualification juridique dépend du contexte, du droit applicable et des engagements en cause.

### Question 3
Quelle est la différence entre lecture et écriture ?

**Corrigé :** Une lecture interroge l'état sans le modifier de manière persistante. Une écriture qui change l'état nécessite normalement une transaction incluse et consomme du gaz.

### Question 4
À quoi sert l'ABI ?

**Corrigé :** Elle décrit comment encoder les appels et décoder les résultats et événements d'un contrat afin que les applications puissent interagir avec lui.

### Question 5
Pourquoi un appel à un contrat peut-il échouer tout en consommant du gaz ?

**Corrigé :** Les instructions ont déjà utilisé des ressources avant que l'exécution échoue. Les règles de frais facturent le gaz consommé selon le protocole.

### Question 6
Pourquoi un contrat ne peut-il pas lire directement une page web de façon déterministe ?

**Corrigé :** Les réponses externes peuvent varier entre nœuds et instants. Un oracle ou un mécanisme de données doit apporter l'information sous une forme compatible avec le consensus.

### Question 7
Qu'est-ce que la composabilité ?

**Corrigé :** La capacité d'un contrat à appeler d'autres contrats et à combiner des fonctionnalités. Elle enrichit les applications mais ajoute des dépendances et des risques.

### Question 8
Comment se produit une réentrance ?

**Corrigé :** Un appel externe transfère le contrôle à un autre contrat qui rappelle le contrat initial avant que l'état interne soit correctement mis à jour, ce qui peut permettre de répéter une opération.

### Question 9
Pourquoi une mise à niveau par proxy introduit-elle une hypothèse de confiance ?

**Corrigé :** Parce qu'une autorité ou une gouvernance peut remplacer l'implémentation logique. Il faut comprendre qui contrôle cette capacité et quelles garanties entourent son usage.

### Question 10
Un audit garantit-il qu'un contrat ne sera jamais exploité ?

**Corrigé :** Non. Il peut réduire le risque, mais ne prouve pas l'absence de toutes les vulnérabilités. Le code, les dépendances, les paramètres et les menaces évoluent.

## 15. Challenge final : concevoir un coffre de laboratoire

### Scénario

Tu dois proposer un contrat de coffre pédagogique qui permet aux utilisateurs de déposer et retirer des unités de valeur de test. Chaque utilisateur ne peut retirer que son propre solde. Le projet doit rester simple et ne doit pas être déployé avec des actifs réels.

### Travail demandé

Rédige une spécification de 500 à 700 mots qui définit les fonctions, les permissions, les événements, les invariants, les erreurs et les tests. Ajoute un diagramme Mermaid du flux de dépôt et de retrait. Identifie au moins cinq risques et explique comment les réduire. Tu n'as pas besoin d'écrire un contrat complet de production.

### Correction proposée

Le coffre doit définir un solde comptable par utilisateur et appliquer une règle qui interdit de retirer plus que ce solde. L'opération de dépôt doit vérifier la quantité fournie et mettre à jour l'état uniquement si la réception d'actifs a effectivement réussi selon le mécanisme choisi. L'opération de retrait doit vérifier le solde, mettre à jour l'état dans un ordre sûr et interagir avec le mécanisme de transfert. Les événements de dépôt et de retrait doivent contenir l'utilisateur, la quantité et, au besoin, les informations de suivi.

~~~mermaid
flowchart TD
    D["Demande de dépôt"] --> V1["Valider quantité et transfert"]
    V1 --> U1["Mettre à jour le solde"]
    U1 --> E1["Émettre événement de dépôt"]
    W["Demande de retrait"] --> V2["Vérifier le solde"]
    V2 --> U2["Débiter le solde"]
    U2 --> T["Effectuer le transfert"]
    T --> E2["Émettre événement de retrait"]
~~~

Les invariants comprennent : un utilisateur ne retire pas plus que son solde ; une opération échouée ne doit pas laisser un solde incohérent ; les rôles administratifs ne peuvent pas détourner les dépôts ; les transferts et événements doivent correspondre à l'état réel ; une même demande ne peut pas être traitée deux fois si un mécanisme externe de demandes est introduit. Les risques incluent la réentrance, les erreurs de permission, le mauvais traitement des retours, les interactions avec des jetons non standard, les coûts de gaz, les arrondis, les clés administratives compromises et l'absence de tests sur les cas limites.

Le plan de test couvre dépôts normaux, dépôts nuls, retraits partiels, retraits exacts, retraits supérieurs au solde, appels non autorisés, transferts qui échouent et interactions adverses simulées. L'équipe devrait utiliser un environnement local, un compilateur compatible, des tests automatisés et une revue de sécurité. Avant tout déploiement public, elle doit expliciter les actifs pris en charge, auditer les dépendances, définir une stratégie d'urgence et s'assurer que les utilisateurs comprennent les permissions et les risques. Cette spécification ne constitue pas un produit prêt à gérer de l'argent réel : elle décrit un exercice contrôlé d'apprentissage.

## Glossaire

**ABI :** description du format des fonctions, paramètres, résultats et événements exposés par un contrat.

**Appel :** interaction avec un contrat ; selon le contexte, elle peut être une lecture simulée ou une transaction réelle.

**Bytecode :** représentation exécutable du programme déployé sur la machine virtuelle.

**Composabilité :** capacité de combiner des contrats et services on-chain dans une application.

**Contrat intelligent :** programme et état déployés sur une blockchain programmable.

**Événement :** journal émis par un contrat afin de rendre une action observable par les applications.

**Gaz :** unité de ressource facturée pour l'exécution selon les règles du réseau.

**Oracle :** mécanisme qui apporte une donnée extérieure à la blockchain.

**Réentrance :** situation où un appel externe permet de réentrer dans une fonction avant la fin de l'opération initiale.

**Revert :** arrêt d'une exécution qui annule les changements d'état de cette exécution selon les règles du protocole, tout en pouvant laisser des frais consommés.

**Solidity :** langage courant pour écrire des contrats sur Ethereum et les réseaux compatibles avec l'EVM.

**État :** données persistantes du réseau, des comptes et des contrats selon le modèle du protocole.

**Transaction :** opération signée et soumise au réseau afin d'être traitée selon les règles du protocole.

## Pour aller plus loin

- Introduction officielle aux smart contracts : https://ethereum.org/developers/docs/smart-contracts/
- Interagir avec les smart contracts : https://ethereum.org/developers/docs/smart-contracts/interacting/
- Déployer des smart contracts : https://ethereum.org/developers/docs/smart-contracts/deploying/
- Documentation Solidity : https://docs.soliditylang.org/en/latest/
- OpenZeppelin Contracts : https://docs.openzeppelin.com/contracts/

Utilise un environnement de test pour les expériences, vérifie la version du compilateur et préfère les bibliothèques reconnues. Toute gestion d'actifs réels exige une analyse approfondie, des tests et des revues indépendantes proportionnées au risque.
