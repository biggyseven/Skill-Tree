# Histoire (Bitcoin, Ethereum)

## Encadré de mise en contexte

Une technologie ne se comprend pas uniquement par son fonctionnement technique. Pour comprendre la blockchain, il faut aussi comprendre les problèmes auxquels ses concepteurs voulaient répondre, les compromis qu'ils ont acceptés et les événements qui ont fait évoluer les usages. Bitcoin et Ethereum sont deux projets souvent regroupés sous le mot « crypto », mais ils n'ont pas exactement la même ambition. Bitcoin cherche principalement à permettre un système monétaire numérique pair-à-pair sans autorité centrale. Ethereum reprend l'idée d'un registre partagé et lui ajoute une machine d'exécution programmable, afin que des règles et des applications puissent fonctionner sur un réseau public.

Cette leçon raconte leur histoire sans supposer que les prix des actifs ou les promesses commerciales prouvent leur valeur technologique. Les événements sont présentés comme une progression d'idées, de choix techniques, d'incidents et de réponses collectives. Les dates sont des repères utiles, mais l'histoire des protocoles est faite de propositions, de débats, de déploiements progressifs et de désaccords. Une blockchain peut continuer à fonctionner alors que des entreprises qui l'utilisent disparaissent, et une communauté peut se diviser sur la façon de faire évoluer son protocole.

## Objectifs d'apprentissage

À la fin de cette leçon, tu sauras :

- expliquer les idées qui ont préparé l'arrivée de Bitcoin ;
- situer le livre blanc de Bitcoin, son bloc de genèse et ses premiers usages ;
- raconter les principales étapes de l'évolution de Bitcoin et expliquer pourquoi certains changements sont controversés ;
- expliquer l'origine d'Ethereum et la différence entre une blockchain de monnaie et une plateforme de contrats intelligents ;
- décrire l'épisode de The DAO et le débat ayant conduit à une divergence de chaîne ;
- expliquer le passage d'Ethereum de la preuve de travail à la preuve d'enjeu ;
- comparer les objectifs, les architectures et les compromis de Bitcoin et Ethereum ;
- lire une chronologie sans confondre dates historiques, annonces commerciales et réalité technique.

## 1. Avant Bitcoin : les problèmes à résoudre

L'idée d'un argent numérique est beaucoup plus ancienne que Bitcoin. Depuis plusieurs décennies, des chercheurs tentent de créer des paiements sur Internet qui ne reposent pas entièrement sur une banque ou un opérateur central. Internet a rendu l'échange de fichiers facile, mais cette facilité pose un problème particulier pour la monnaie : un fichier peut être copié sans que l'original disparaisse. Si un utilisateur envoie un fichier représentant dix unités monétaires à deux destinataires, comment empêcher qu'il dépense deux fois la même somme ?

Dans le monde physique, remettre un billet à un commerçant transfère le billet : le vendeur ne peut normalement pas conserver le même billet tout en le donnant à une seconde personne. Dans un système numérique, il faut établir un état partagé et un ordre des transactions. Une base de données centrale peut résoudre ce problème en demandant à un serveur de décider quelle dépense est valide. Mais le serveur devient un point de confiance et un point de défaillance : qui le contrôle, qui peut bloquer un compte, que se passe-t-il si l'opérateur est compromis ou indisponible ?

Les systèmes de paiement en ligne traditionnels répondent efficacement à de nombreux besoins. La blockchain n'est pas automatiquement meilleure qu'une banque ou qu'une base de données. Son ambition est différente : permettre à des participants qui ne se connaissent pas nécessairement de maintenir un registre commun, en suivant des règles publiques et sans demander à un administrateur unique de valider chaque opération.

### 1.1 Des travaux précurseurs

Plusieurs idées ont préparé le terrain :

- La cryptographie à clé publique permet de prouver qu'une opération a été autorisée par le détenteur d'une clé privée, sans révéler cette clé.
- Les fonctions de hachage permettent de produire une empreinte compacte d'un message et de détecter de nombreuses modifications.
- Les signatures numériques permettent de vérifier l'origine d'un message signé et son intégrité.
- Les systèmes distribués étudient comment plusieurs ordinateurs peuvent s'accorder alors que les messages peuvent être retardés ou que certains participants ne se comportent pas correctement.
- Les mécanismes de preuve de travail, développés dans différents contextes avant Bitcoin, associent un coût de calcul à la production d'une preuve vérifiable.
- Les propositions de monnaie numérique comme eCash et les travaux de Wei Dai autour de b-money ont exploré différentes façons de créer des paiements numériques ou des registres sans institution centrale unique.

Ces travaux n'ont pas constitué un unique prototype qui serait devenu Bitcoin. Ils forment plutôt une bibliothèque d'idées. L'apport de Bitcoin est d'avoir assemblé plusieurs de ces idées dans un protocole cohérent, opérationnel et ouvert à la participation du public.

### 1.2 Le problème de la double dépense

Imaginons Alice qui possède une unité numérique. Elle crée deux messages : « payer Bob » et « payer Chloé ». Si Bob et Chloé reçoivent chacun le message sans pouvoir consulter un état commun, ils peuvent croire tous les deux avoir été payés.

Un système doit donc répondre à trois questions :

1. Qui a l'autorité pour proposer une opération ?
2. Comment les participants vérifient-ils qu'elle respecte les règles ?
3. Comment se mettent-ils d'accord sur l'ordre des opérations concurrentes ?

Bitcoin combine des signatures, un réseau pair-à-pair, un journal de transactions, une preuve de travail et une règle de choix de chaîne. La signature n'empêche pas à elle seule une double dépense : elle prouve qu'une autorisation correspond à une clé, mais il faut également que le réseau détermine quelle dépense est compatible avec l'historique accepté.

## 2. La naissance de Bitcoin

### 2.1 Le livre blanc de 2008

À la fin d'octobre 2008, un auteur ou groupe d'auteurs utilisant le pseudonyme Satoshi Nakamoto diffuse le document intitulé *Bitcoin: A Peer-to-Peer Electronic Cash System*. Le document propose un système de paiement électronique pair-à-pair. Il décrit comment des participants peuvent diffuser des transactions, les grouper en blocs, relier ces blocs par leurs empreintes cryptographiques et consacrer du travail de calcul à la production de blocs.

Le contexte économique de 2008 rend le sujet de la confiance financière particulièrement visible, mais il serait simpliste de présenter Bitcoin comme une réaction unique à une crise. Les idées de monnaie numérique, de cryptographie et de réseaux distribués sont antérieures. Le livre blanc décrit avant tout un mécanisme technique : remplacer la nécessité de faire approuver chaque transfert par un intermédiaire central par une validation collective selon des règles déterministes.

Satoshi Nakamoto n'a pas publiquement révélé une identité civile vérifiée. Il est donc plus exact de parler de pseudonyme que d'attribuer avec certitude le projet à une personne précise. Des théories circulent depuis longtemps, mais elles ne constituent pas une preuve.

### 2.2 Le bloc de genèse

Le 3 janvier 2009, le premier bloc de Bitcoin, appelé bloc de genèse, est créé. Il établit le point de départ de la chaîne. Le texte contenu dans ce bloc fait référence à un titre de presse britannique au sujet d'un sauvetage bancaire. Cette référence est souvent interprétée comme un commentaire sur le contexte monétaire de l'époque, mais il convient de distinguer le fait observable — le texte inscrit dans le bloc — des interprétations que l'on peut en tirer.

Le bloc de genèse est particulier : il est configuré dans le logiciel et n'est pas dépensable de la même manière que les sorties ordinaires de la chaîne. Au fil des jours suivants, le réseau commence à produire des blocs et à échanger des transactions. Le protocole est alors un logiciel expérimental utilisé par un nombre limité de participants.

~~~mermaid
timeline
    title Les premières étapes de Bitcoin
    2008 : Publication du livre blanc
         : Proposition d'argent électronique pair-à-pair
    3 janvier 2009 : Création du bloc de genèse
    2009 : Démarrage du réseau public
    2010 : Développement des premiers échanges et paiements médiatisés
    2012 : Premier halving
    2017 : SegWit activé
    2021 : Taproot activé
~~~

### 2.3 Les premiers paiements et l'expérimentation

Les premières années sont dominées par l'expérimentation. Les développeurs examinent le logiciel, les utilisateurs apprennent à gérer les clés et des plateformes d'échange apparaissent. En mai 2010, un paiement devenu célèbre porte sur deux pizzas achetées en échange de bitcoins. Cet épisode est souvent raconté parce qu'il illustre le passage d'une unité principalement échangée entre passionnés à un instrument utilisé pour acheter un bien réel. Il ne signifie pas que le paiement était la première transaction de toute nature, ni qu'il aurait été possible de prévoir la valorisation future de l'actif.

Cette anecdote enseigne surtout une leçon : la valeur d'un moyen d'échange dépend d'un ensemble d'éléments sociaux et techniques. Un protocole peut rendre des transferts possibles, mais l'acceptation par des commerçants, la liquidité, les outils de portefeuille, l'accès à Internet et la confiance des participants se construisent séparément.

Dans cette période apparaissent aussi les premiers services centralisés permettant d'acheter ou vendre des bitcoins. Ils rendent l'accès plus simple, mais réintroduisent des risques spécifiques : garde des fonds, gestion des comptes, solvabilité, sécurité opérationnelle et conformité réglementaire. Il ne faut pas confondre la décentralisation du protocole Bitcoin avec la décentralisation de chaque entreprise qui propose des services autour de lui.

## 3. Les grandes étapes de l'évolution de Bitcoin

### 3.1 Une émission prévisible et les halvings

Le protocole Bitcoin prévoit une récompense pour le producteur d'un bloc valide. Cette récompense comprend une subvention de bloc et, selon les transactions incluses, des frais payés par les utilisateurs. La subvention diminue par paliers programmés, approximativement tous les 210 000 blocs. Cette réduction est appelée *halving*.

Le calendrier d'émission est une règle du logiciel, pas une garantie de prix. Une baisse de la subvention peut modifier les revenus des mineurs et les discussions sur la sécurité économique du réseau, mais elle ne prouve pas que le cours va monter ou descendre. La demande, la liquidité, la réglementation, la concurrence et les conditions macroéconomiques influencent aussi les marchés.

Le mécanisme illustre une caractéristique essentielle : les règles monétaires sont publiques et prévisibles au niveau du protocole, mais leur valeur économique reste incertaine. Les utilisateurs doivent distinguer une propriété technique mesurable d'une hypothèse financière.

### 3.2 Les plateformes et les risques de garde

Des plateformes centralisées ont accéléré l'achat et la vente de bitcoins. Elles ont également démontré qu'un système décentralisé pouvait être entouré d'intermédiaires vulnérables. Des incidents majeurs, dont l'effondrement de Mt. Gox en 2014, ont marqué l'histoire du secteur. Le détail des responsabilités et des événements est complexe, mais la leçon pédagogique est simple : le protocole, le portefeuille logiciel, la plateforme d'échange et l'organisation qui conserve les fonds sont des couches différentes.

Une transaction Bitcoin peut être valide au niveau du protocole alors qu'un service de garde fait faillite. À l'inverse, une plateforme peut fonctionner normalement alors qu'une transaction est invalide pour le réseau. Un diagnostic rigoureux demande toujours d'identifier la couche concernée.

### 3.3 Taille des blocs et désaccords de gouvernance

Au fil de la croissance du réseau, une question devient importante : comment augmenter la capacité de traitement ? Une solution simple en apparence serait d'augmenter la quantité maximale de données par bloc. Mais une taille de bloc supérieure peut augmenter les coûts de stockage, de bande passante et de vérification pour les opérateurs de nœuds. Si moins de personnes peuvent faire fonctionner un nœud complet, le réseau risque de devenir plus dépendant d'opérateurs bien équipés.

Le débat ne porte donc pas uniquement sur le nombre de transactions par seconde. Il implique des arbitrages entre capacité, frais, propagation des blocs, exigences matérielles et facilité de vérification indépendante. La communauté n'a pas toujours été d'accord sur le meilleur compromis. La divergence ayant conduit à Bitcoin Cash en 2017 est un exemple de désaccord qui s'est traduit par des règles de consensus différentes. Il faut parler de chaînes distinctes issues d'une séparation de règles, pas d'une mise à jour qui aurait silencieusement transformé tous les logiciels en un seul réseau.

### 3.4 SegWit

Segregated Witness, généralement appelé SegWit, a été activé sur Bitcoin en 2017. L'objectif technique le plus visible était de séparer certaines données de signature du format historique des transactions, avec des effets sur la mesure de la taille des blocs, la malléabilité des transactions et la possibilité de construire des solutions de paiement de seconde couche.

La malléabilité est un phénomène dans lequel une représentation de transaction peut être modifiée de certaines façons sans changer le transfert économique visé, ce qui compliquait certains protocoles construits au-dessus de Bitcoin. SegWit a réduit une partie de ce problème pour les types de transactions concernés. Il a également facilité le développement du Lightning Network, réseau de paiement qui permet des échanges hors chaîne principale, avec des mécanismes de règlement en chaîne.

Il faut éviter deux erreurs : SegWit n'a pas rendu la capacité de Bitcoin illimitée, et l'activation d'une mise à jour du protocole ne signifie pas que tous les logiciels et services adoptent immédiatement tous ses avantages.

### 3.5 Lightning Network et paiements de seconde couche

Le Lightning Network est un système de paiement construit au-dessus de Bitcoin. Il utilise notamment des canaux de paiement et des contrats cryptographiques afin que plusieurs échanges puissent avoir lieu sans inscrire chaque transfert sur la chaîne principale. Les résultats peuvent ensuite être réglés ou contestés en s'appuyant sur Bitcoin.

L'architecture cherche à réduire le nombre de transactions directement inscrites sur la couche de base et à rendre certains paiements plus rapides ou moins coûteux. Elle apporte en contrepartie des questions de liquidité des canaux, de routage, de disponibilité, de gestion des nœuds et d'expérience utilisateur. Une couche de paiement n'abolit donc pas les contraintes de la base : elle déplace une partie de la complexité dans une autre architecture.

### 3.6 Taproot

La mise à jour Taproot a été activée en novembre 2021. Elle a introduit des améliorations relatives aux signatures et à la construction des scripts, notamment avec Schnorr et les arbres de scripts de type Merkle, selon les usages. Elle peut améliorer l'efficacité de certaines constructions et rendre différentes dépenses plus proches en apparence dans certains cas, sans garantir un anonymat complet.

Taproot est un exemple utile de l'évolution progressive d'un protocole : il faut définir des règles, écrire des implémentations, les tester, coordonner leur activation et attendre l'adoption par les portefeuilles et les services. La gouvernance de Bitcoin est souvent qualifiée de prudente parce qu'une modification de règles peut affecter des milliers d'opérateurs indépendants. Cette prudence protège certaines propriétés, mais elle rend également les évolutions plus lentes et contestées.

## 4. L'idée d'Ethereum : une blockchain programmable

### 4.1 Pourquoi Bitcoin ne répondait-il pas à tous les besoins ?

Bitcoin permet déjà de vérifier des signatures, de suivre des unités et d'appliquer des conditions de dépense. Mais les développeurs ont souhaité disposer d'une plateforme plus générale pour exécuter du code d'application partagé. L'idée n'est pas que Bitcoin serait inutile ou incapable de toute logique. C'est plutôt qu'une architecture conçue pour des paiements avec des règles de dépense spécifiques n'offre pas la même expérience qu'une machine d'exécution programmée pour une grande variété d'applications.

En 2013, Vitalik Buterin propose dans le livre blanc d'Ethereum une blockchain généraliste dotée de contrats intelligents. Au lieu de limiter l'état partagé à un modèle centré sur les sorties de transaction, Ethereum maintient un état global mis à jour par l'exécution des transactions et du code. Les développeurs peuvent écrire des contrats, les déployer et interagir avec eux en payant des frais de calcul.

### 4.2 La préparation et le lancement

Le projet se structure en 2014, avec plusieurs cofondateurs et une campagne publique de financement en ether. Le réseau principal Ethereum est lancé le 30 juillet 2015 avec la version initiale appelée Frontier. Il s'agit d'une étape importante, mais non de la fin des travaux : une plateforme exécutant du code arbitraire doit faire évoluer ses clients, ses outils, ses mécanismes de sécurité et ses règles de consensus.

Ethereum s'est ensuite enrichi d'outils pour les développeurs, de langages de contrats tels que Solidity, de portefeuilles, d'explorateurs et d'applications variées. Cette ouverture a encouragé l'expérimentation, mais elle a également étendu la surface d'attaque. Un bug dans un contrat peut avoir des conséquences financières même si le protocole de base fonctionne comme prévu.

### 4.3 Qu'est-ce qu'un contrat intelligent ?

Un contrat intelligent est du code déployé dans la blockchain qui est exécuté selon les règles du réseau. Il peut conserver un état, accepter des appels, vérifier des conditions et produire des effets sur cet état. Le terme « contrat » peut induire en erreur : le code n'est pas automatiquement un contrat juridique, et il ne sait pas spontanément si une information du monde réel est vraie.

Prenons un contrat de coffre numérique : il peut imposer que deux signatures sur trois autorisent une sortie. La règle peut être exécutée de manière déterministe, à condition que les clients et le protocole suivent les mêmes règles. En revanche, le contrat ne peut pas vérifier seul qu'un colis a réellement été livré ou qu'une entreprise est financièrement solvable, à moins que l'information soit fournie par une source extérieure, par exemple un oracle. L'oracle réintroduit alors une hypothèse de confiance ou un mécanisme collectif de vérification.

~~~mermaid
flowchart TD
    U["Utilisateur"] --> W["Portefeuille"]
    W --> T["Transaction signée"]
    T --> N["Nœuds Ethereum"]
    N --> V["Vérification des règles"]
    V --> E["Exécution du contrat"]
    E --> S["Nouvel état partagé"]
    S --> X["Reçu consultable par les applications"]
~~~

## 5. The DAO : un incident technique et un désaccord collectif

En 2016, The DAO est un projet expérimental de financement collectif construit avec des contrats intelligents sur Ethereum. Une vulnérabilité dans le code permet à un attaquant de déplacer une grande quantité d'ether sous le contrôle du système. Le problème ne correspond pas simplement à une panne de serveur : le programme a exécuté des opérations conformément à ce que permettait son code, même si ce comportement était contraire à l'intention de ses concepteurs.

L'incident provoque un débat majeur. Une partie de la communauté soutient un changement de l'histoire reconnue par les clients pour restaurer une situation considérée comme injuste. D'autres considèrent qu'une modification de l'historique pour réparer un contrat crée un précédent dangereux et défendent le principe selon lequel les règles et les transactions doivent rester inchangées, même lorsque leur résultat est indésirable.

La chaîne qui a continué avec les règles modifiées a conservé le nom Ethereum (ETH). Une autre chaîne a continué sans ce changement de l'historique et est devenue Ethereum Classic (ETC). Le point pédagogique n'est pas de décréter qu'une seule position est moralement évidente. C'est de reconnaître que la gouvernance décentralisée ne supprime pas les conflits : elle oblige les communautés à les résoudre par les logiciels, les opérateurs, les utilisateurs, les applications et les règles qu'ils choisissent de suivre.

Cet événement enseigne aussi que la sécurité du code et la sécurité du protocole sont différentes. Un contrat peut avoir un bug sans que le moteur de consensus soit cassé. La correction du code ne suffit pas toujours à réparer les conséquences économiques. Les audits, les tests, les limites de retrait, les délais de gouvernance, les mécanismes d'arrêt et les programmes de divulgation de vulnérabilités réduisent certains risques, mais aucun n'offre une garantie absolue.

## 6. D'Ethereum à la preuve d'enjeu

### 6.1 Pourquoi changer le consensus ?

Ethereum a initialement utilisé la preuve de travail, comme Bitcoin. La preuve de travail repose sur une compétition de calcul : les mineurs cherchent une preuve répondant aux critères du protocole. Ce mécanisme rend coûteuse la production de blocs invalides, mais consomme de l'énergie et exige du matériel spécialisé dans de nombreuses conditions.

La preuve d'enjeu, ou Proof of Stake, prend une approche différente. Les validateurs immobilisent de l'ETH selon les règles du protocole et participent à la proposition et à l'attestation des blocs. Un comportement malveillant ou une violation des règles peut entraîner des pénalités, et dans certains cas la destruction d'une partie de la mise. Le mécanisme dépend donc des règles économiques, de la disponibilité des validateurs et de la capacité du réseau à organiser le consensus.

Aucun mécanisme de consensus n'est magique. La preuve d'enjeu réduit fortement le besoin de calcul concurrentiel de la preuve de travail, mais crée d'autres questions : distribution de la mise, concentration des services de staking, risques de logiciel, disponibilité et incitations économiques.

### 6.2 La Beacon Chain

Le 1er décembre 2020, la Beacon Chain démarre comme chaîne de consensus en preuve d'enjeu distincte du réseau principal historique. Elle permet de préparer et d'observer le fonctionnement du nouveau mécanisme sans immédiatement remplacer le système qui exécutait les transactions Ethereum. Cette phase illustre la difficulté de modifier une infrastructure publique utilisée par des applications et des détenteurs d'actifs : le changement doit être planifié, testé, communiqué et coordonné.

### 6.3 The Merge en septembre 2022

Le 15 septembre 2022, la mise à jour appelée The Merge fait passer le réseau principal d'Ethereum de la preuve de travail à la preuve d'enjeu, en intégrant l'ancien niveau d'exécution à l'infrastructure de consensus issue de la Beacon Chain. L'historique de transactions n'est pas effacé. Les utilisateurs n'ont pas eu besoin de convertir un « ancien ETH » en un nouvel actif : il s'agissait d'une transition du mécanisme de consensus du réseau.

La transition a fortement réduit la consommation énergétique liée à la production de blocs, souvent estimée autour de 99,95 % pour Ethereum. Cette donnée décrit la conséquence du changement de consensus, pas la consommation totale d'électricité de toutes les applications, des ordinateurs des utilisateurs ou des infrastructures qui interagissent avec Ethereum.

The Merge n'a pas, à lui seul, multiplié instantanément la capacité de traitement des transactions ni résolu tous les frais élevés. La scalabilité est un ensemble de problèmes distincts. Ethereum a poursuivi les évolutions de sa feuille de route, dont des travaux autour des données de seconde couche et des blobs introduits avec la mise à jour Dencun en 2024.

~~~mermaid
flowchart LR
    A["Ethereum historique<br/>exécution + preuve de travail"] --> M["The Merge<br/>15 septembre 2022"]
    B["Beacon Chain<br/>consensus Proof of Stake"] --> M
    M --> C["Ethereum après The Merge<br/>exécution + consensus Proof of Stake"]
~~~

## 7. Usages qui se sont développés autour d'Ethereum

### 7.1 Finance décentralisée

La finance décentralisée, souvent appelée DeFi, regroupe des applications permettant des échanges, des prêts, des emprunts ou des stratégies financières au moyen de contrats intelligents. Des utilisateurs peuvent interagir directement avec un contrat sans que chaque opération soit autorisée individuellement par une banque. Les contrats et leurs états peuvent être observés publiquement, ce qui facilite certaines analyses.

Mais l'accès direct ne supprime pas les risques : bugs de contrats, manipulations de prix, défauts des oracles, erreurs de gouvernance, ponts inter-chaînes vulnérables, liquidations automatiques et pertes liées à la volatilité. Une application dite décentralisée peut aussi dépendre d'un site web, d'un service RPC ou d'une équipe qui contrôle certains paramètres. Il faut analyser les dépendances au lieu de se fier uniquement à une étiquette marketing.

### 7.2 Jetons et NFT

Ethereum a facilité la création de jetons fongibles et de jetons non fongibles. Un jeton fongible est conçu pour que les unités soient interchangeables selon les règles du contrat. Un NFT identifie une unité distincte. Mais un jeton n'est pas à lui seul une preuve de propriété juridique universelle ou une garantie que le fichier associé sera hébergé à jamais. Il faut lire les règles du contrat, examiner les métadonnées, comprendre le stockage et tenir compte des droits applicables.

Les jetons ont démontré que les contrats intelligents peuvent représenter des droits ou des unités économiques dans des formats programmables. Ils ont aussi donné lieu à des usages spéculatifs, des escroqueries et des projets de qualité très variable. Pour un ingénieur, le défi consiste à distinguer les propriétés techniques du jeton de ce que les promoteurs affirment qu'il représente.

### 7.3 Organisations autonomes décentralisées

Une DAO est une organisation qui utilise des règles de gouvernance, souvent en partie encodées dans des contrats. Les participants peuvent voter avec des jetons ou selon d'autres règles. Toutefois, l'exécution d'un vote n'efface pas les conflits de gouvernance, la concentration du pouvoir, les questions juridiques ni la dépendance à des interfaces et des contributeurs humains. Le mot « autonome » ne signifie pas qu'une organisation peut fonctionner sans personnes ni décisions collectives.

## 8. Comparer Bitcoin et Ethereum

| Dimension | Bitcoin | Ethereum |
|---|---|---|
| Intention historique dominante | Argent numérique pair-à-pair et registre monétaire | Plateforme programmable pour contrats et applications |
| Modèle de données | Modèle transactionnel fondé sur les sorties non dépensées (UTXO) | Modèle d'état avec comptes, stockage et exécution des contrats |
| Consensus actuel | Preuve de travail | Preuve d'enjeu depuis The Merge |
| Actif natif | BTC | ETH |
| Logique applicative | Scripts de dépense avec capacités volontairement limitées | Contrats intelligents à état, exécutés dans l'environnement Ethereum |
| Évolutions typiques | Compatibilité, sécurité, confidentialité relative et couches de paiement | Contrats, expérience développeur, consensus et scalabilité via couches complémentaires |
| Risques à examiner | Conservation des clés, minage, frais, congestion et dépendance aux services | Tous les risques de base, plus bugs de contrats et dépendances d'applications |

Cette comparaison simplifie volontairement des systèmes complexes. Les deux possèdent des développeurs, des nœuds, des portefeuilles, des marchés et des communautés. Les deux peuvent servir de base à des usages qui n'étaient pas prévus par chaque utilisateur. Leur différence ne se résume pas à « Bitcoin est ancien, Ethereum est moderne » ni à « l'un est meilleur ». Ils optimisent des priorités différentes.

## 9. Comment lire une chronologie blockchain

Quand tu étudies un événement, distingue cinq choses :

1. **La proposition** : un livre blanc, une spécification ou une idée publiée.
2. **L'implémentation** : du code capable de mettre en œuvre la proposition.
3. **Le déploiement** : la mise en service sur un réseau de test ou sur le réseau principal.
4. **L'adoption** : la part des nœuds, portefeuilles et services qui utilisent effectivement la fonctionnalité.
5. **Les effets** : conséquences sur l'usage, la sécurité, les coûts et l'écosystème.

Ces étapes ont souvent des dates différentes. Dire qu'une proposition a été publiée n'implique pas qu'elle est en production. Dire qu'une mise à jour est activée ne signifie pas que tous les portefeuilles exploitent déjà toutes ses améliorations. Dire qu'un projet a levé des fonds ne prouve pas la qualité de son code.

Le vocabulaire est lui aussi important : le réseau, le protocole, le client, le portefeuille, l'explorateur, l'échange et l'application sont des choses distinctes. Un portefeuille ne « contient » généralement pas physiquement les pièces : il protège les clés qui permettent d'autoriser des opérations, tandis que le registre public indique l'état du réseau. Perdre le téléphone et perdre la clé de récupération ne sont donc pas exactement la même situation.

## 10. Sécurité, gouvernance et enseignements tirés de l'histoire

L'histoire des deux projets montre que la décentralisation est un ensemble de compromis, pas une propriété binaire. Un réseau peut avoir beaucoup de nœuds mais une forte concentration de fournisseurs d'accès RPC. Un protocole peut être ouvert, alors qu'une application dépend d'un administrateur unique. Un contrat peut être public et auditable, alors que peu de personnes sont capables d'analyser correctement son code.

Les incidents historiques invitent à poser des questions concrètes :

- Qui peut modifier les règles du système ?
- Que se passe-t-il si un bug est découvert ?
- Les utilisateurs peuvent-ils vérifier les règles par eux-mêmes ?
- Les transactions sont-elles réversibles par une autorité, par une majorité de validateurs ou par personne au niveau du protocole ?
- Les actifs sont-ils conservés par l'utilisateur ou par une plateforme ?
- Les interfaces et les données viennent-elles d'une source indépendante ?
- Quel est le coût d'une attaque et quelles incitations économiques le réduisent ou l'augmentent ?

Bitcoin met l'accent sur une base monétaire aux règles relativement limitées et sur la vérification indépendante. Ethereum montre le potentiel et les dangers d'un système programmable : un contrat permet une nouvelle catégorie d'applications, mais il devient aussi un code critique qui doit être conçu et testé avec soin. L'histoire n'apporte donc pas une preuve qu'une blockchain serait invulnérable. Elle fournit des études de cas sur la manière dont des protocoles, des développeurs et des communautés gèrent les erreurs et les désaccords.

## 11. TP guidé : construire une chronologie raisonnée

### Objectif

Construire une chronologie qui relie un événement historique à un problème technique et à une conséquence. Le but n'est pas de mémoriser des dates isolées, mais de comprendre pourquoi elles importent.

### Étape 1 — Préparer les entrées

Crée un tableau dans un document ou une feuille de calcul avec les colonnes suivantes :

- Date ou période
- Projet concerné
- Événement
- Problème visé
- Changement technique ou organisationnel
- Limites restantes
- Source consultée

Ajoute au minimum les événements suivants : livre blanc de Bitcoin, bloc de genèse, paiement des pizzas, débat sur la taille des blocs, activation de SegWit, activation de Taproot, proposition d'Ethereum, lancement de Frontier, incident de The DAO, lancement de la Beacon Chain et The Merge.

### Étape 2 — Formuler une hypothèse technique

Pour chaque événement, rédige deux phrases. La première précise quel problème était traité. La seconde explique ce que l'événement n'a pas résolu. Par exemple : « SegWit a modifié la représentation d'une partie des données de transaction et amélioré certains fondements des protocoles de seconde couche. Il n'a pas rendu la capacité de la chaîne illimitée et n'a pas supprimé tous les frais ou toutes les contraintes de propagation. »

### Étape 3 — Vérifier les sources

Privilégie les livres blancs, les annonces officielles de mises à jour, les spécifications et les analyses techniques réputées. Une page promotionnelle peut expliquer un objectif, mais ne doit pas être la seule preuve d'une propriété de sécurité. Note si une source distingue les faits observables et l'interprétation.

### Étape 4 — Présenter et comparer

Sélectionne trois événements qui ont changé un protocole ou son consensus. Pour chacun, écris un paragraphe de 100 à 150 mots qui décrit le changement, le bénéfice visé et un compromis ou une limite. Termine par une comparaison des approches de gouvernance de Bitcoin et Ethereum, sans conclure que l'une est parfaite.

### Résultat attendu

Un document de chronologie d'au moins une page, avec des sources cliquables, des dates contrôlées et des formulations techniques qui ne promettent pas plus que ce que les faits démontrent.

## 12. Mini-projet : une fiche de veille historique

Imagine qu'une équipe technique doit évaluer une blockchain avant de déployer une application. Prépare une fiche d'une page qui répond aux questions suivantes :

1. Quand le réseau a-t-il été lancé et quelles sont ses règles de consensus actuelles ?
2. Quels événements ont conduit à des changements de règles ou à des divergences ?
3. Quelle est la procédure de mise à jour du logiciel ?
4. Quelles dépendances externes sont nécessaires à ton application ?
5. Que se passerait-il si la chaîne connaissait un incident de consensus ou une mise à jour controversée ?
6. Comment vérifier les informations sur le réseau indépendamment du site marketing d'un fournisseur ?

Le livrable doit séparer les faits confirmés, les hypothèses et les points à investiguer. Cette discipline est transférable à l'étude de n'importe quel protocole.

## 13. Dix questions d'entraînement avec corrigé

### Question 1
Pourquoi la double dépense est-elle plus difficile à traiter pour un fichier numérique que pour un billet physique ?

**Corrigé :** Un fichier peut être copié et envoyé à plusieurs destinataires sans que les copies disparaissent. Il faut donc un état commun et un ordre des transactions permettant de déterminer quelle dépense est valide.

### Question 2
Que publie le livre blanc de Bitcoin en 2008 ?

**Corrigé :** Une proposition de système de paiement électronique pair-à-pair qui combine des transactions signées, des blocs liés cryptographiquement, une preuve de travail et une règle de validation collective.

### Question 3
Qui est Satoshi Nakamoto ?

**Corrigé :** Le pseudonyme associé à la proposition et au logiciel initial de Bitcoin. Son identité civile n'a pas été publiquement établie de façon vérifiable ; il ne faut pas présenter les spéculations comme des faits.

### Question 4
Le bloc de genèse suffit-il à expliquer la valeur de Bitcoin ?

**Corrigé :** Non. Il marque le démarrage de l'historique de Bitcoin. La valeur économique dépend aussi de l'adoption, de la liquidité, de la demande, des attentes et du contexte externe.

### Question 5
Pourquoi les débats sur la taille des blocs touchent-ils à la décentralisation ?

**Corrigé :** Des blocs plus volumineux peuvent augmenter les exigences de stockage, de bande passante et de vérification. Ces coûts peuvent rendre plus difficile l'exécution indépendante d'un nœud par des particuliers.

### Question 6
Quel bénéfice SegWit a-t-il apporté ?

**Corrigé :** Il a modifié la manière dont certaines données de signature sont représentées et mesurées, contribué à réduire des problèmes de malléabilité pour les transactions concernées et facilité certaines solutions de seconde couche. Il n'a pas rendu Bitcoin illimité.

### Question 7
Quelle est l'idée centrale d'Ethereum ?

**Corrigé :** Proposer un réseau public dont l'état peut être modifié non seulement par des transferts, mais aussi par l'exécution de contrats intelligents, afin de construire des applications programmables partagées.

### Question 8
L'incident de The DAO signifie-t-il que le consensus Ethereum était cassé ?

**Corrigé :** Pas à lui seul. Une vulnérabilité dans le contrat a permis un comportement que ses concepteurs ne souhaitaient pas. Le programme et le réseau peuvent exécuter les règles tout en produisant un résultat économiquement indésirable.

### Question 9
Que représente The Merge ?

**Corrigé :** La transition d'Ethereum de la preuve de travail à la preuve d'enjeu, réalisée le 15 septembre 2022, en reliant le niveau d'exécution historique au mécanisme de consensus issu de la Beacon Chain.

### Question 10
Bitcoin est-il objectivement meilleur qu'Ethereum ?

**Corrigé :** La question est trop générale. Bitcoin et Ethereum ont des priorités et architectures différentes. Il faut définir le besoin, puis comparer les propriétés, les coûts, les risques, les contraintes et l'écosystème pertinents.

## 14. Challenge final : expliquer un changement de protocole à un collègue

Tu fais partie d'une équipe qui doit préparer un atelier d'introduction à la blockchain. Un collègue affirme : « Une blockchain est immuable, donc toute transaction est toujours irréversible et aucun changement de règles ne peut arriver. » Tu dois corriger cette affirmation en utilisant l'histoire de Bitcoin et Ethereum.

### Consignes

Rédige une réponse structurée de 400 à 600 mots qui :

- explique la différence entre immutabilité pratique et impossibilité absolue de changement ;
- distingue le consensus du protocole, le code d'un contrat intelligent et la garde par une plateforme ;
- utilise au moins un exemple Bitcoin et un exemple Ethereum ;
- décrit pourquoi une divergence de chaîne peut apparaître ;
- termine par trois questions de vérification avant qu'une entreprise adopte une blockchain.

### Correction proposée

Une blockchain est conçue pour rendre la modification discrète de l'historique difficile ou détectable, mais cela ne signifie pas que tout changement soit physiquement impossible. L'histoire de Bitcoin montre que les règles d'un protocole peuvent évoluer grâce à des mises à jour adoptées par les opérateurs. Les débats sur la capacité des blocs et l'activation de SegWit ont illustré qu'une évolution technique dépend d'un accord suffisamment large et que des participants peuvent ne pas adopter les mêmes règles. Une divergence de chaîne peut se produire si des logiciels appliquent des règles incompatibles.

Ethereum illustre une autre dimension. L'incident de The DAO concernait une vulnérabilité dans un contrat intelligent. La communauté a ensuite été divisée sur la réponse à apporter, et une divergence a donné naissance à deux chaînes poursuivant des règles différentes. Cet épisode ne prouve pas qu'un administrateur puisse effacer n'importe quelle transaction à volonté ; il montre que les communautés peuvent parfois choisir des règles distinctes et que la gouvernance du protocole demeure un sujet concret.

Il faut également distinguer trois couches. Le consensus définit comment les participants s'accordent sur un historique et un état valide. Un contrat intelligent est un programme soumis aux règles de la plateforme ; son résultat peut être indésirable même si son exécution respecte le code. Une plateforme centralisée qui conserve les fonds ajoute un autre risque : elle peut être piratée ou faire faillite sans que le consensus du réseau soit en panne.

Avant d'adopter une blockchain, une entreprise devrait donc demander : qui conserve les clés et qui peut autoriser les opérations ? Comment les mises à jour du protocole et des contrats sont-elles validées et annoncées ? Quelles dépendances, quelles procédures de secours et quels risques de gouvernance existent ? Le choix ne doit pas se baser sur une promesse d'immuabilité absolue, mais sur une évaluation documentée des menaces, des compromis et du niveau de contrôle acceptable.

## Glossaire

**Bloc de genèse :** premier bloc d'une chaîne, point de départ de l'historique.

**Blockchain :** registre répliqué dont les blocs sont liés par des références cryptographiques et dont l'état valide dépend de règles de protocole et d'un mécanisme de consensus.

**Consensus :** mécanisme permettant aux participants de converger vers un historique ou un état accepté.

**Contrat intelligent :** programme exécuté selon les règles d'une blockchain et capable de maintenir un état.

**DAO :** organisation utilisant des mécanismes de gouvernance numériques, souvent appuyés par des contrats intelligents.

**DeFi :** applications financières décentralisées construites sur des protocoles et contrats.

**Double dépense :** tentative d'utiliser la même valeur numérique dans plusieurs opérations incompatibles.

**Fork :** divergence de règles, de logiciel ou d'historique menant parfois à des chaînes distinctes.

**Halving :** réduction programmée de la subvention de bloc sur Bitcoin.

**Immutabilité pratique :** difficulté de réécrire l'historique accepté, qui dépend du consensus, des incitations et de la profondeur des confirmations.

**Oracle :** mécanisme apportant à un contrat une donnée provenant de l'extérieur de la blockchain.

**Preuve d'enjeu :** mécanisme de consensus où des validateurs engagent une mise et participent aux responsabilités du protocole.

**Preuve de travail :** mécanisme de consensus qui s'appuie sur une preuve de calcul coûteuse à produire et relativement facile à vérifier.

**SegWit :** mise à jour Bitcoin qui a séparé certaines données de signature dans le format des transactions et apporté plusieurs effets techniques.

**UTXO :** sortie de transaction non dépensée, élément du modèle comptable de Bitcoin.

## Pour aller plus loin

- Livre blanc de Bitcoin, « Bitcoin: A Peer-to-Peer Electronic Cash System » : https://bitcoin.org/bitcoin.pdf
- Présentation officielle d'Ethereum : https://ethereum.org/what-is-ethereum/
- Historique d'Ethereum : https://ethereum.org/ethereum-history-founder-and-ownership/
- Annonce de lancement d'Ethereum en 2015 : https://blog.ethereum.org/2015/07/30/ethereum-launches
- Explication officielle de The Merge : https://ethereum.org/roadmap/merge/

Quand tu lis ces ressources, relève la différence entre une spécification technique, une chronologie éditoriale et un texte de communication. Ces sources sont utiles pour commencer, mais une investigation approfondie peut demander de confronter les documents officiels aux analyses indépendantes et au code des implémentations.
