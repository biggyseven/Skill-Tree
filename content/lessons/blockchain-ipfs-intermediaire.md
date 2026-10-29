# Stockage décentralisé

## Encadré de mise en contexte

Une blockchain est adaptée à un historique partagé de transactions, de soldes, de permissions ou d'engagements cryptographiques. Elle n'est généralement pas l'endroit idéal pour conserver de gros fichiers, des vidéos, des documents ou des métadonnées volumineuses. Le coût de chaque octet stocké et la nécessité de répliquer les données rendent souvent le stockage on-chain coûteux et peu flexible. Les applications Web3 associent donc fréquemment un registre on-chain à un système de stockage distribué ou adressé par contenu.

IPFS, l'InterPlanetary File System, est un ensemble de protocoles qui permet d'identifier et de récupérer du contenu à partir de son identité cryptographique et de sa structure, plutôt que d'une seule localisation serveur. Cette propriété permet de vérifier que le contenu récupéré correspond à l'identifiant demandé. Elle ne garantit pas, à elle seule, que le contenu sera toujours hébergé, qu'il sera confidentiel ou qu'il pourra être supprimé de toutes les copies.

Ce cours explique les identifiants de contenu (CID), les blocs et graphes de données, la persistance, l'épinglage, les passerelles, IPNS, la confidentialité, l'intégration avec un smart contract et les risques d'exploitation. Il est conçu pour un développeur qui souhaite construire une application fiable, pas seulement envoyer un fichier vers un service et copier une adresse.

## Objectifs d'apprentissage

À la fin du cours, tu dois pouvoir expliquer l'adressage par contenu, distinguer un CID d'un simple hash de fichier, diagnostiquer une récupération lente ou indisponible, concevoir une stratégie de pinning redondante, distinguer disponibilité et intégrité, sélectionner une stratégie d'URL ou de nom mutable, éviter d'exposer des informations privées, publier un CID dans une application on-chain et construire une procédure de récupération vérifiable.

## Prérequis et parcours pratique

Il est utile de connaître les fonctions de hachage, les clés, les blocs et l'architecture de base d'une DApp. Le parcours pratique utilise des fichiers de test sans données personnelles. Tu peux suivre les exercices avec un nœud local IPFS ou avec un service de pinning dont tu comprends les conditions. Les commandes montrées ci-dessous sont des exemples d'usage du CLI Kubo et peuvent différer selon la version installée ; vérifie toujours l'aide de ta version avant de les employer sur un environnement important.

Le projet pédagogique consiste à publier un petit document non sensible, obtenir son CID, vérifier l'intégrité du contenu, l'épingler dans plus d'un emplacement indépendant, puis utiliser le CID depuis une page de test. Tu vas ensuite simuler une source indisponible et produire un rapport de reprise.

## 1. Pourquoi séparer stockage et blockchain

Une blockchain favorise la vérifiabilité partagée et un historique gouverné par le consensus. Un fichier, en revanche, peut contenir des millions d'octets, des médias ou des données qui changent. Publier chaque octet dans un contrat peut augmenter les frais, la complexité et la taille de l'état. Une stratégie plus courante consiste à conserver le minimum nécessaire sur la chaîne — par exemple un CID, un hash de référence ou une preuve de propriété — et à servir le contenu à partir d'une couche de stockage.

Cette architecture sépare les responsabilités. Le contrat peut déterminer quel CID est associé à un objet ou qui peut mettre à jour sa référence. IPFS fournit une méthode d'identification et de récupération du contenu. Un système d'hébergement ou de pinning aide à conserver les données accessibles. L'application combine ces éléments et doit gérer les pannes de chacun.

Il faut éviter deux erreurs. Premièrement, stocker une URL et l'appeler décentralisée sans vérifier qui contrôle le serveur. Deuxièmement, appeler un CID permanent simplement parce qu'il est dérivé du contenu. Le CID peut continuer à identifier les mêmes octets alors qu'aucun nœud ne les conserve. L'intégrité de l'identifiant ne remplace pas une stratégie de disponibilité.

## 2. Adressage par contenu : le principe du CID

Dans un système adressé par emplacement, une URL indique généralement où demander une ressource. Dans un système adressé par contenu, le CID décrit cryptographiquement la ressource ou la structure à récupérer. Le CID contient des informations de format, un identifiant de version, un encodage et un multihash. Il n'est donc pas nécessairement identique au résultat brut d'un hash SHA-256 appliqué au fichier original.

Si un seul octet du contenu change, l'identifiant calculé pour cette structure change normalement aussi. Cette propriété facilite la vérification de l'intégrité : le client peut vérifier que les données obtenues correspondent au contenu identifié. Elle permet également que deux nœuds indépendants qui disposent du même contenu, préparé avec les mêmes paramètres de structure, obtiennent le même CID.

Mais le CID dépend de la manière dont le fichier est structuré. IPFS peut découper un gros fichier en blocs, relier les blocs dans un graphe acyclique orienté (DAG) et construire un bloc racine. Le codec, le découpage, l'organisation du DAG, l'algorithme de hash et la version du CID peuvent influencer l'identifiant obtenu. Pour rendre deux procédures reproductibles, documente les paramètres utilisés.

~~~mermaid
flowchart TD
    F[Fichier local] --> C[Découpage en blocs]
    C --> D[Organisation du graphe de contenu]
    D --> R[Bloc racine]
    R --> H[Multihash et métadonnées de format]
    H --> I[CID]
    I --> N[Nœud qui conserve les blocs]
    I --> G[Passerelle ou autre point de récupération]
~~~

Un CID indique quel contenu rechercher, pas nécessairement quel nœud le possède. Le système doit trouver des fournisseurs qui disposent des blocs et qui peuvent les transmettre. Si aucun nœud ne les conserve, le CID reste connu mais le contenu n'est pas récupérable à ce moment-là.

## 3. Hash de fichier, CID et checksum

Un checksum est généralement le résultat d'un algorithme de hachage appliqué directement aux octets d'un fichier. Il sert à vérifier que le fichier obtenu correspond à une empreinte attendue. Le CID est plus expressif : il décrit aussi comment interpréter les données et peut identifier la racine d'une structure en plusieurs blocs. Le hash du fichier original et le CID ne sont donc pas toujours identiques, même si le CID se fonde sur des hashes cryptographiques.

Pour vérifier un fichier téléchargé depuis une source, utilise le checksum fourni par une source de confiance lorsque cela est approprié. Pour retrouver un objet dans IPFS, utilise son CID. N'essaie pas de comparer simplement la chaîne du CID avec le hash brut d'une archive sans connaître le codec, la version et les paramètres de construction.

La distinction devient importante lors d'une migration de stockage ou d'une réimportation. Deux outils peuvent produire des CIDs différents pour les mêmes octets s'ils utilisent des paramètres différents. Cela ne signifie pas automatiquement que l'un des fichiers est corrompu. Il faut comparer les données sous-jacentes et les profils de construction avant de conclure.

### Exemple pratique

Supposons que tu publies un petit fichier JSON comme métadonnée. Tu obtiens un CID, puis tu reformates le JSON et tu republies le fichier. Même si les valeurs métier paraissent identiques, les octets peuvent changer à cause des espaces, de l'ordre des clés ou de l'encodage. Le CID peut donc différer. Si ton système traite l'identifiant comme une version immuable, cette différence est attendue. Si tu souhaites une référence stable vers le dernier document, tu as besoin d'une couche de nommage mutable comme IPNS ou d'une référence on-chain mise à jour selon des règles explicites.

## 4. Les blocs et le graphe de données

IPFS représente souvent de gros fichiers comme plusieurs blocs reliés par une structure de données. Cette organisation permet de demander seulement des parties nécessaires, de réutiliser des blocs déjà présents et d'identifier précisément le contenu. Elle rend cependant simpliste l'idée qu'un fichier est toujours représenté par un seul hash. Le CID racine peut référencer d'autres blocs nécessaires à la reconstruction complète.

Lorsqu'un nœud récupère un objet, il peut devoir obtenir plusieurs blocs depuis différents pairs ou passerelles. La latence dépend alors de la disponibilité de ces blocs, de la connectivité, de la taille des morceaux et du cache local. Un bloc manquant dans le graphe peut empêcher l'ouverture complète d'un document, même si la racine est connue.

Les répertoires et fichiers peuvent être encodés avec UnixFS, tandis que d'autres applications peuvent employer d'autres codecs. Les fichiers volumineux peuvent être divisés en blocs et structurés différemment selon les paramètres. Si une application dépend de la reproductibilité du CID, les paramètres de construction doivent être enregistrés et testés dans un environnement contrôlé.

## 5. CIDv0 et CIDv1

Les identifiants existent sous différentes versions et encodages. Un CIDv0 est souvent reconnaissable à sa représentation textuelle qui commence par Qm et comporte 46 caractères ; un CIDv1 peut être représenté en base32 avec un préfixe tel que bafy. Il ne faut pas décider de la validité d'un identifiant uniquement par son préfixe, mais ces motifs peuvent aider lors d'un diagnostic initial.

CIDv1 contient des informations explicites permettant d'interpréter la version, le codec et le multihash. Il offre une flexibilité d'encodage qui peut être pratique dans les contextes Web et sous-domaines de passerelle. Pour de nouveaux projets, CIDv1 est souvent un choix raisonnable si la pile d'outils utilisée le supporte.

La conversion d'un CID entre formats textuels ne réencode pas nécessairement le contenu. Parfois elle change seulement la manière de représenter l'identifiant. D'autres opérations, comme modifier le codec ou les paramètres de découpage, peuvent conduire à un nouvel identifiant de contenu. Le rapport doit spécifier si le CID a seulement changé de base ou si le contenu a été reconstruit.

## 6. Trouver du contenu : réseau P2P et passerelles

IPFS s'appuie sur un réseau de pairs capables de fournir des blocs. Un nœud peut annoncer qu'il fournit un contenu, rechercher des fournisseurs et récupérer des blocs à partir du réseau. Les mécanismes précis dépendent de la version et de la configuration, mais la logique centrale reste que l'identifiant du contenu et sa disponibilité sont deux faits distincts.

Une passerelle HTTP donne accès à du contenu IPFS depuis un navigateur ou un client qui ne parle pas directement les protocoles IPFS. Elle améliore l'interopérabilité, mais introduit un point de dépendance pour la requête : le navigateur peut dépendre de la passerelle pour trouver et servir les données. Le contenu adressé par CID permet de vérifier l'intégrité selon le modèle du client, mais ne garantit pas la disponibilité de la passerelle, la confidentialité du lecteur ou la neutralité des politiques d'accès.

La configuration du gateway et la manière dont le navigateur vérifie le contenu varient. Une application critique doit documenter si elle utilise une passerelle publique, un gateway privé, un nœud local ou une combinaison. Le fait qu'une URL contient le CID ne garantit pas que le navigateur valide lui-même tous les blocs de la même façon qu'un nœud IPFS complet.

## 7. Persistance, pinning et collecte des déchets

Un nœud IPFS dispose d'une capacité de stockage finie. Il peut supprimer des données mises en cache pour récupérer de l'espace au moyen d'un mécanisme de garbage collection. Le pinning marque des données à conserver localement selon la politique du nœud afin qu'elles ne soient pas supprimées par cette collecte. Le pinning ne constitue pas une promesse qu'un ensemble de serveurs indépendants conservera le contenu à jamais ; il contrôle la rétention dans un environnement donné.

Pour une application destinée à la production, définis une stratégie de persistance : quelles données sont épinglées, où, par qui, avec quelle fréquence de vérification et quelle politique de remplacement. Une seule machine peut tomber en panne, perdre son disque ou être supprimée. Plusieurs copies sont utiles si elles sont réellement indépendantes et si la procédure de reconstruction a été testée.

Le pinning doit aussi couvrir les dépendances du contenu : épingler la racine d'un graphe doit permettre au système de conserver ses blocs nécessaires selon le mécanisme de pinning utilisé, mais il faut vérifier l'état réel dans l'outil. Les tableaux de bord d'un service de pinning ne remplacent pas un test de récupération indépendant. Mesure la disponibilité depuis un environnement distinct, et non depuis le nœud qui possède déjà les données.

### Politique de rétention recommandée

- Identifie le propriétaire métier des données et la raison de leur conservation.
- Définis une durée cible, les copies attendues et la procédure d'archivage.
- Configure des alertes si le pin échoue, disparaît ou n'est plus vérifiable.
- Vérifie périodiquement la récupération depuis au moins une source indépendante.
- Teste la restauration après la perte d'un fournisseur.
- Documente ce qu'il est impossible de supprimer si le contenu a été répliqué par des tiers.

## 8. IPNS et noms mutables

Un CID identifie un contenu précis. Si le contenu change, le CID change normalement aussi. IPNS offre une couche de nommage mutable qui peut pointer vers un CID actualisé, et DNSLink peut servir à associer un nom DNS à une référence de contenu selon la configuration. Ces mécanismes sont utiles pour une application dont la page d'accueil ou le catalogue évolue sans que le consommateur doive apprendre un nouveau CID à chaque mise à jour.

La mutabilité introduit des questions supplémentaires : qui peut mettre à jour le nom, comment la mise à jour est signée, combien de temps les caches peuvent rester anciens, et comment une application décide quelle version afficher. Un nom mutable ne doit pas être confondu avec une identité immuable. Pour une preuve d'intégrité à une date donnée, conserve le CID précis qui a été consulté ou publié.

Dans un contexte blockchain, un contrat peut conserver un CID précis ou une référence mutable définie par un protocole. Si l'administrateur est capable de changer la référence, cette capacité doit être affichée et gouvernée. Un utilisateur qui croit que des métadonnées sont figées doit comprendre si la propriété est garantie par un stockage immuable, par un contrôle de rôle, par une convention sociale ou seulement par la promesse d'un opérateur.

## 9. Confidentiel ne signifie pas décentralisé

Le stockage adressé par contenu facilite la vérification de l'intégrité, mais n'assure pas la confidentialité. Les contenus publics peuvent être lus par toute personne qui parvient à les récupérer. Les identifiants, les métadonnées, les heures de publication et les habitudes de récupération peuvent révéler des informations. Un CID imprévisible ne doit pas être traité comme un mot de passe ou un système de contrôle d'accès.

Si un fichier contient des données privées, ne l'ajoute pas simplement à IPFS en espérant que personne ne connaîtra son CID. Si le chiffrement est adapté au besoin, chiffre le contenu avant publication, définis la gestion et la révocation des clés, puis analyse ce que les métadonnées visibles révèlent encore. La perte d'une clé peut rendre le contenu inutilisable ; le partage de la clé peut permettre à d'autres personnes de conserver des copies déchiffrées.

La suppression est également différente. Effacer la copie locale n'efface pas les copies d'autres nœuds ou de passerelles qui ont déjà récupéré le contenu. Une stratégie de protection des données doit donc éviter de publier des informations dont la diffusion durable serait inacceptable. Le choix du stockage doit être intégré à une analyse de risque, et non ajouté à la fin du développement.

## 10. Intégrer IPFS à une application Web3

Une architecture courante garde une petite référence on-chain et stocke le document ou les métadonnées hors chaîne. Le contrat peut associer un CID à un identifiant d'objet, alors que l'interface récupère le contenu correspondant. L'avantage est de réduire le volume de données écrites sur la blockchain et de bénéficier de l'adressage par contenu. Le risque est que la disponibilité, les mises à jour et la confidentialité dépendent d'une stratégie hors chaîne.

~~~mermaid
flowchart LR
    A[Application] --> C[Smart contract]
    C -->|CID ou référence| A
    A --> G[Passerelle ou nœud IPFS]
    G --> D[Contenu adressé par CID]
    D --> V[Vérification de l'intégrité]
    V --> R[Affichage ou traitement]
~~~

Pour chaque objet, documente l'identifiant on-chain, le CID, le type de contenu, le modèle de mise à jour, l'emplacement du pin, le responsable de la disponibilité et la procédure de récupération. Si l'application prend en charge plusieurs versions, indique si elle affiche la référence actuelle ou la version au moment d'une transaction. Cette distinction peut être importante pour un NFT, un reçu, un document de gouvernance ou une version de logiciel.

Le contrat ne peut pas vérifier qu'un contenu est servi rapidement par chaque passerelle du réseau simplement parce qu'un CID est stocké. Il peut vérifier une référence ou des données fournies à l'exécution, mais la disponibilité hors chaîne reste une propriété de l'architecture. Une application qui en dépend doit prévoir les pannes et la possibilité de remplacer une source sans altérer l'identité du contenu.

## 11. Métadonnées de NFT et contenu immuable

Un NFT peut stocker ou référencer une URI de métadonnées décrivant un nom, une image, une animation ou des attributs. Si l'URI pointe vers un contenu IPFS immuable par CID, il est plus facile de constater qu'une version particulière correspond à son identifiant. Mais l'interface doit encore pouvoir récupérer les blocs, et une copie épinglée doit rester disponible. Un NFT ne devient pas entièrement pérenne uniquement parce que son URI commence par ipfs.

Les métadonnées peuvent aussi être modifiables par le contrat, par un administrateur ou au travers d'une URI de base. Il faut vérifier les fonctions qui changent la référence, les permissions, les conditions de gel et le comportement des marchés qui lisent les métadonnées. Une propriété de gel n'a de sens qu'en rapport avec ce qui est réellement bloqué : le tokenURI, la base URI, le contenu sous-jacent ou plusieurs de ces éléments.

Pour un projet NFT, crée une procédure qui sauvegarde le contenu original, épingle les fichiers et les dépendances, enregistre les CIDs, vérifie les rendus depuis plusieurs points, et documente les limites. Si une image référence d'autres ressources, vérifie aussi leur persistance. Une image disponible ne prouve pas que les fichiers audio, les fichiers de texture ou les métadonnées liées sont eux-mêmes disponibles.

## 12. IPFS et l'indexation d'applications

Les applications peuvent indexer les événements on-chain qui contiennent des CIDs ou des références. L'indexeur relie alors les changements d'état aux objets à récupérer. Cette indexation doit gérer les réorganisations de chaîne, les événements dupliqués, les références remplacées et les contenus indisponibles. Si l'indexeur traite un événement deux fois, il doit éviter de produire plusieurs enregistrements métier identiques.

Lorsqu'un CID n'est plus récupérable, ne remplace pas silencieusement le contenu par un objet homonyme. Conserve l'identifiant attendu, le contexte de publication et le statut d'indisponibilité. Les journaux doivent permettre de distinguer une erreur de réseau, un contenu non épinglé, un CID incorrect, un format non supporté ou un refus d'accès du service d'hébergement.

Pour l'interface, prévois un temps limite, un état de chargement, une erreur explicite et une possibilité de relancer sans créer d'effet on-chain. Une ressource manquante ne doit pas empêcher automatiquement toute la page d'être utilisable si les informations essentielles sont déjà disponibles. Mais si le contenu est requis pour une décision de sécurité, l'application doit refuser de prendre cette décision tant qu'elle n'a pas pu vérifier les données.

## 13. Installer et utiliser un nœud Kubo en laboratoire

Kubo est une implémentation IPFS courante qui fournit un daemon et un outil en ligne de commande. Son installation dépend du système et de la version. Utilise la documentation officielle pour télécharger une version appropriée, vérifier les instructions de mise à jour et comprendre où la configuration et les données sont stockées. N'exécute pas une commande copiée d'une page inconnue sur un serveur de production.

Dans un environnement de test, initialise le dépôt de configuration selon les instructions de ta version, démarre le daemon et vérifie qu'il répond. Les commandes de diagnostic peuvent inclure l'état du nœud, les informations de version, les pairs connectés et l'accès à l'API locale. L'API d'administration ne doit pas être exposée publiquement sans authentification et restrictions appropriées.

Exemples de commandes de base, à valider dans l'aide de la version installée :

~~~bash
ipfs version
ipfs id
ipfs swarm peers
ipfs add --cid-version=1 document-test.txt
ipfs cat <CID>
ipfs pin add <CID>
ipfs pin ls
ipfs get <CID>
~~~

La commande add prépare le contenu et retourne un identifiant. La commande cat tente de récupérer et d'afficher le contenu dans le contexte de l'outil ; elle est adaptée aux petits fichiers de texte, pas à un gros média arbitraire. La commande pin ajoute une protection locale contre la collecte de données selon le modèle du nœud. La présence d'un pin local ne prouve pas qu'une autre machine indépendante peut récupérer l'objet.

Ne divulgue pas la sortie complète de configuration ou les chemins privés d'un serveur si elle révèle des données sensibles. Pour un TP, un fichier texte non sensible suffit à tester le chemin. Le but n'est pas de laisser un daemon de test exposé sur Internet mais de comprendre les étapes de publication, récupération et diagnostic.

## 14. Stratégie de pinning redondant

La redondance doit couvrir plusieurs modes de panne. Deux pins sur deux comptes du même fournisseur peuvent partager le même domaine de panne ; deux copies sur des machines différentes dans le même centre de données peuvent être affectées par une panne régionale ou une suspension de compte. Pour les données critiques, pense en termes de diversité réelle : fournisseurs, régions, accès, authentification, procédures de restauration et capacité à vérifier les données.

Un plan de persistance peut inclure un nœud géré par l'organisation, un fournisseur de pinning indépendant et une copie d'archive contrôlée. La stratégie doit préciser comment les nouveaux CIDs sont envoyés vers chaque destination, comment les erreurs sont détectées, comment les contenus obsolètes sont conservés ou supprimés et qui vérifie le succès. Les fournisseurs changent leurs conditions de service : il faut prévoir un processus de migration.

Le contrôle de santé doit aller au-delà de l'API qui a répondu. Une requête d'intégrité peut vérifier que la ressource identifiée par le CID est réellement récupérable et que le contenu correspond à l'objet attendu. Effectue des contrôles depuis une machine qui ne contient pas déjà les blocs en cache. Sinon, le test confirme seulement que le nœud local a encore sa copie.

## 15. Menaces et erreurs courantes

**CID divulgué** : un objet public adressé par contenu n'est pas confidentiel. Ne publie pas de secrets ou de documents sensibles en supposant que l'identifiant restera inconnu.

**Contenu non épinglé** : le CID reste correct mais les blocs peuvent être collectés ou devenir indisponibles. Vérifie la persistance et la redondance.

**Faux service de pinning** : un fournisseur peut afficher un statut positif sans garantir la récupération réelle dans le temps. Teste l'accès depuis un autre environnement et vérifie les conditions contractuelles.

**Passerelle unique** : l'application peut être indisponible alors que d'autres nœuds possèdent le contenu. Prévois plusieurs chemins de récupération et documente leur indépendance.

**Métadonnées mutable** : une URI peut être remplacée ou son contenu peut changer si elle renvoie vers un serveur centralisé. Définis la politique de version et le pouvoir de modification.

**Référence mal construite** : un CID copié avec une erreur, un codec inattendu ou un réseau non approprié peut bloquer l'affichage. Conserve la source du CID et valide sa forme, sans considérer un motif textuel comme une preuve complète.

**Dépendances manquantes** : un objet racine peut référencer plusieurs blocs ou fichiers auxiliaires. Vérifie la récupération de l'ensemble utilisé par l'application.

**Données à supprimer** : le retrait d'une seule copie ne garantit pas la suppression des répliques. N'envoie pas à un réseau de stockage public des informations dont la persistance serait inadmissible.

## 16. TP guidé A : publier et vérifier un document

Crée un fichier texte non sensible contenant une phrase connue. Ajoute-le au nœud IPFS de laboratoire et note le CID obtenu, la version du logiciel et les paramètres utilisés. Récupère ensuite le contenu par CID, compare les octets avec le fichier source et écris le résultat. Recommence dans un autre répertoire ou sur une autre machine configurée de manière contrôlée afin de comprendre si le CID est reproductible avec les mêmes paramètres.

Épingle le contenu, vérifie la liste des pins et demande ensuite à une instance distincte de récupérer le même CID. Si l'instance ne trouve pas le contenu, analyse la connectivité, la découverte de fournisseurs, le pin et les éventuels problèmes de passerelle. Ne conclus pas immédiatement à une corruption si la récupération échoue : la cause peut être la disponibilité.

### Correction proposée

Le rapport doit distinguer la génération du CID, le stockage local, l'annonce du fournisseur et la récupération depuis un autre nœud. Il doit expliquer que le même contenu peut produire un autre CID si les paramètres de construction diffèrent, et que le succès d'un pin local ne garantit pas la persistance globale. Le test est réussi lorsque les octets récupérés correspondent au fichier attendu et qu'une source indépendante peut retrouver le contenu.

## 17. TP guidé B : concevoir les métadonnées d'un objet Web3

Crée un fichier JSON de métadonnées fictives qui ne contient aucune donnée personnelle. Publie le fichier avec les paramètres documentés et conserve le CID. Dans une application locale, utilise ce CID pour récupérer et afficher le document. Ajoute une erreur simulée où le gateway ne répond pas et vérifie que l'interface affiche un état de panne plutôt qu'une métadonnée provenant d'une référence différente.

Ensuite, publie une version modifiée du JSON et compare les CIDs. Documente la méthode utilisée pour indiquer qu'une version remplace une autre : une référence on-chain mise à jour, une entrée IPNS, un nouveau tokenURI ou une autre règle explicite. Explique qui a le droit de modifier la référence et ce que l'utilisateur peut vérifier.

### Correction proposée

Un résultat solide conserve la version exacte consultée, ne mélange pas l'URI mutable et le CID immuable, et indique la stratégie de pinning pour chaque version. Si le contrat peut changer la référence, cette capacité est mentionnée comme pouvoir d'administration. Le rapport explique les limites de suppression et de confidentialité et ne décrit pas le CID comme une garantie de permanence.

## 18. Atelier : incident de contenu indisponible

Le tableau de bord de ton application affiche une image NFT manquante. La transaction d'émission est confirmée et le tokenURI renvoie une référence IPFS plausible. Un fournisseur de pinning indique que le contenu est présent, mais un autre accès ne parvient pas à le récupérer.

### Travail demandé

- Confirme le réseau, l'adresse du NFT, l'identifiant du token et le tokenURI effectif.
- Vérifie le CID et la structure des métadonnées sans remplacer la référence.
- Interroge les sources de récupération configurées et compare les erreurs.
- Vérifie le pin et les éventuelles dépendances du fichier.
- Détermine si le problème est limité à une passerelle ou concerne la disponibilité des blocs.
- Rédige les conditions de clôture et un plan d'amélioration de la redondance.

### Correction proposée

Commence par récupérer la référence exacte depuis le contrat et non depuis le cache de l'interface. Vérifie ensuite si le document de métadonnées lui-même est disponible, puis si les ressources qu'il référence le sont aussi. Compare au moins une récupération depuis un environnement indépendant. Si une seule passerelle est en échec, l'incident peut être de disponibilité d'accès ; si aucune source ne conserve les blocs, il faut restaurer depuis une copie de confiance et rétablir les pins.

Le remplacement du CID n'est pas une correction automatique : il change l'identité du contenu et doit suivre la politique de mise à jour de l'application. Le rapport doit préciser ce qui était indisponible, les utilisateurs touchés, la procédure de restauration, les sources de référence et les mesures qui empêchent une répétition.

## 19. Modéliser les versions de contenu et conserver un manifeste

Une application qui publie de nombreuses ressources doit garder une trace des versions exactes qu'elle a rendues disponibles. Un CID permet d'identifier une version d'un contenu, mais il ne décrit pas à lui seul son rôle métier, sa date de publication, sa provenance ou la raison du remplacement. Un manifeste peut relier un identifiant logique, une version, un CID, un type MIME, une taille attendue, une date de création et un responsable de publication.

Le manifeste n'a pas besoin d'être un fichier unique ni de vivre entièrement sur la blockchain. Il peut être stocké dans un dépôt versionné, une base ou un document adressé par contenu selon les exigences du produit. Ce qui compte est de rendre la relation vérifiable et de protéger la chaîne de décision : qui a approuvé la publication, quelle version du fichier a été vérifiée et quel identifiant est maintenant associé à l'objet on-chain ?

Les manifestes doivent éviter d'embarquer des secrets et des données privées. Une empreinte de contenu n'est pas un contrôle d'accès. Pour un document qui contient des informations sensibles, décide d'abord si la publication dans un réseau adressé par contenu est acceptable. Si un chiffrement est utilisé, la gestion des clés et l'accès à la clé doivent être documentés séparément.

### Exemple de schéma de manifeste

~~~json
{
  "logical_id": "catalogue-demo-001",
  "version": 3,
  "cid": "bafy...remplacer-par-le-cid-reel",
  "media_type": "application/json",
  "purpose": "metadonnees-publiques-de-test",
  "approved_by": "equipe-publication",
  "created_at": "2026-01-15T12:00:00Z"
}
~~~

Les valeurs sont illustratives : le CID doit être remplacé par un identifiant obtenu lors d'un test réel. Le manifeste doit être validé par un schéma, et les dates doivent être traitées comme des métadonnées déclaratives, pas comme une preuve indépendante de l'heure. Si le manifeste lui-même est adressé par contenu, son CID peut être enregistré comme version du catalogue ou référencé dans un autre document.

## 20. UnixFS, répertoires et dépendances du contenu

Un fichier vu dans une interface est souvent une structure dont le CID racine mène à plusieurs blocs. UnixFS permet de représenter les fichiers et répertoires dans le modèle IPFS. Lorsqu'un catalogue contient des sous-répertoires, des images, des polices, des scripts ou des métadonnées, la disponibilité doit être évaluée pour toute la structure nécessaire au rendu.

Un test simple qui ouvre une page d'accueil ne prouve pas que toutes les ressources du site sont accessibles. Le navigateur peut avoir conservé une image dans son cache, tandis qu'une autre ressource a disparu. Le rapport de publication doit donc inclure un test des dépendances importantes et s'assurer que les ressources critiques sont récupérables depuis une source indépendante.

Les paramètres d'ajout ont une influence sur le découpage et le résultat final. Pour un gros répertoire, le nombre de fichiers, les noms de chemin, le codec et les options de chunking peuvent modifier le graphe. Si plusieurs équipes doivent reconstruire le même catalogue, elles doivent utiliser une procédure versionnée plutôt que des commandes improvisées. Archive l'outil, la version et les options pertinentes avec le résultat de publication.

Une migration de paramètres peut produire de nouveaux CIDs sans modifier le sens métier des fichiers. Le produit doit décider si cela crée une nouvelle version logique ou seulement une nouvelle représentation technique. Les consommateurs qui conservent des références exactes ont besoin d'un mécanisme explicite pour apprendre la nouvelle racine.

## 21. Politique de confidentialité et données personnelles

Le caractère public et répliqué du réseau est une contrainte d'architecture. Si un fichier contient une donnée personnelle, un document confidentiel, une clé, un token d'accès ou un élément qui pourrait mettre une personne en danger, la question ne se résout pas en ne montrant pas le CID à l'écran. Des copies peuvent être récupérées et conservées par des tiers, et les métadonnées de publication peuvent révéler une relation entre plusieurs objets.

La première règle consiste à minimiser les données publiées. Si une information n'est pas nécessaire à l'application publique, ne la place pas dans le document IPFS. Si une donnée sensible doit être distribuée à des destinataires identifiés, évalue un système de stockage avec contrôle d'accès plutôt qu'un réseau public adressé par contenu. Le chiffrement de bout en bout peut protéger le contenu contre les lecteurs qui ne disposent pas de la clé, mais il ne supprime pas toutes les fuites de métadonnées et ne résout pas le partage et la révocation des clés.

Le chiffrement exige un modèle de clés : qui chiffre, qui peut déchiffrer, comment les clés sont distribuées, comment une clé compromise est remplacée et ce qu'il advient des anciennes copies. Une révocation empêche parfois de futurs accès si les clés sont gérées correctement, mais elle ne rappelle pas les copies déjà déchiffrées. Ne promets pas l'effacement total d'un contenu public si tu ne maîtrises pas toutes ses répliques.

Avant de publier, exécute une vérification de contenu et de métadonnées. Recherche des secrets, des identifiants internes, des chemins locaux, des noms de comptes et des documents qui n'ont pas été approuvés pour publication. L'étape d'approbation doit être automatisée quand c'est possible, mais une liste de motifs ne remplace pas l'examen humain pour les catégories à risque.

## 22. Architecture de récupération et objectifs de service

Définis des objectifs de niveau de service pour les ressources critiques : pourcentage de récupération réussie sur une période, délai maximal de récupération depuis une source indépendante, durée avant alerte après un pin manquant et délai de restauration après la perte d'un fournisseur. Les objectifs doivent être mesurables par des tests réels, et non basés uniquement sur le statut API d'un fournisseur.

Les contrôles périodiques doivent interroger les CIDs depuis des environnements qui ne disposent pas déjà du cache, valider les octets ou les métadonnées attendus et enregistrer la durée. Pour les contenus volumineux, vérifie les blocs et chemins réellement nécessaires à l'application. Les échecs doivent être classés : indisponibilité du gateway, fournisseur introuvable, échec réseau, CID mal formé, dépendance manquante ou format incompatible.

Le plan de récupération doit expliquer comment réépingler la bonne version. Il est préférable de partir du manifeste approuvé ou d'une archive contrôlée que de récupérer un contenu homonyme sur un serveur inattendu. Après restauration, compare le CID et le contenu, rétablis les pins sur les domaines de panne attendus, puis répète la vérification depuis une autre machine.

La résilience peut se mesurer comme un système complet : identité de contenu, copies conservées, chemins de recherche, monitoring, accès opérateur et expérience de l'utilisateur en cas d'échec. Une redondance qui n'a jamais été testée peut être nominale mais inutile lorsqu'une panne survient réellement.

## 23. Déployer et migrer un service de pinning

Avant de choisir un fournisseur, évalue la méthode d'authentification, les limites de taille, les conditions de rétention, les quotas, les exports possibles, les journaux, les garanties d'accès et le processus de fermeture du compte. Vérifie si l'organisation peut récupérer ses données ou rediriger le travail vers un autre fournisseur sans dépendre d'une interface propriétaire.

La migration doit commencer par l'inventaire des CIDs et des versions logiques attendues. Envoie les contenus vers la nouvelle destination, vérifie la disponibilité depuis une machine extérieure et n'abandonne l'ancienne copie qu'après un contrôle réussi. La suppression de pins anciens peut être utile pour réduire les coûts, mais elle doit respecter le modèle de rétention et les obligations qui s'appliquent au contenu.

Un plan de migration doit inclure les erreurs possibles : authentification expirée, contenu partiellement transféré, limites de débit, mauvais CID, quota insuffisant et désaccord entre le manifeste et la destination. Les scripts de migration doivent être idempotents afin de pouvoir recommencer sans créer une base d'inventaire incohérente. Conserve les logs de traitement, mais retire les secrets d'authentification des traces.

Pour des données critiques, ne supprime pas immédiatement l'ancienne copie lorsque le nouveau fournisseur annonce un succès. Prévois une période de coexistence, des contrôles indépendants et un critère de clôture explicite. La migration est terminée lorsque les contenus peuvent être récupérés selon les objectifs définis, que les métadonnées de référence ont été mises à jour et que la procédure de retour arrière a été décidée.

## 24. Runbook de diagnostic IPFS

Lorsqu'une ressource est indisponible, commence par collecter la référence exacte et le contexte : CID, heure, environnement utilisateur, URL de récupération, type de fichier, état du nœud local, fournisseur interrogé et erreur observée. Ne remplace pas immédiatement le CID ni ne supprime la référence du catalogue ; cela ferait disparaître une preuve utile et pourrait faire pointer les utilisateurs vers un autre contenu.

Vérifie ensuite la syntaxe du CID, puis l'accès à la passerelle et à d'autres chemins disponibles. Si l'accès fonctionne sur le nœud qui a ajouté le contenu mais pas sur un autre environnement, le cache local peut masquer un problème de publication ou de pinning. Vérifie les pins, les quotas, l'état des services de stockage et la disponibilité des blocs liés dans le graphe.

Distingue une panne d'accès d'une panne de contenu. Une passerelle peut retourner une erreur alors qu'un autre fournisseur conserve le contenu. À l'inverse, une page de statut verte peut être trompeuse si le service répond mais ne parvient pas à récupérer les blocs requis. Le test utile est une récupération du contenu attendu depuis un environnement distinct, suivie d'une vérification d'intégrité.

Si le contenu est réellement indisponible, restaure-le depuis une archive ou une source approuvée, vérifie que le résultat correspond au CID annoncé et rétablis la redondance. Si le contenu source est perdu, n'invente pas un remplacement silencieux. Documente l'incident, identifie la version concernée, évalue l'impact et applique la procédure de publication de nouvelle version si nécessaire.

## 25. Cahier de laboratoire : mesure de disponibilité sur plusieurs sources

Prépare une liste de cinq CIDs de test, dont un fichier petit, un fichier moyen, un répertoire et un document avec une ressource liée. Épingle-les sur deux infrastructures indépendantes et vérifie l'accès depuis une troisième machine. Enregistre le taux de succès, la latence, les erreurs et la version des outils utilisés. Répète le test après une période de rétention puis après avoir arrêté temporairement l'une des sources de test.

Le rapport doit déterminer si le résultat dépend d'un cache, si les répertoires et dépendances sont bien récupérés, si les alertes se déclenchent et si les procédures de reprise permettent de rétablir le contenu. Ne considère pas un échantillon de laboratoire comme une garantie universelle ; il sert à valider la procédure et à révéler des points faibles.

### Barème de réussite

- Tous les CIDs attendus sont inventoriés et associés à leur version logique.
- La vérification est menée depuis une machine distincte qui ne possède pas déjà le contenu.
- Une indisponibilité est détectée et classée correctement.
- La restauration rétablit les données attendues sans changement non documenté de CID.
- Les limites de rétention, de confidentialité et de suppression sont rédigées.
- Un autre opérateur peut reproduire le test à partir du compte rendu.

## 26. Workflow de publication reproductible avec Kubo

Une procédure d'ajout doit pouvoir être rejouée par une autre personne et produire un résultat compréhensible. Enregistre la version de Kubo, les options d'ajout, les fichiers sources, leur encodage, les valeurs de manifeste et le CID retourné. Les commandes de base peuvent évoluer ; utilise la documentation et l'aide de la version installée comme référence, particulièrement si les scripts sont exécutés automatiquement.

Dans un laboratoire, commence par créer un fichier texte dont le contenu est public et sans secret. Ajoute-le avec la version de CID choisie, conserve la sortie, puis récupère le contenu à partir du CID. Compare les octets récupérés avec la source au lieu de seulement confirmer que la commande a affiché un message de réussite. Pour un dossier, vérifie aussi les fichiers et chemins attendus plutôt que de conclure à partir de la seule présence d'un dossier racine.

Lorsqu'un ajout produit un résultat inattendu, ne supprime pas tout de suite l'objet. Contrôle l'encodage des fins de ligne, les caractères, les options, le codec, la version et le découpage. Deux outils peuvent structurer les mêmes octets différemment. Le but d'un workflow reproductible est d'identifier les paramètres pertinents, pas de supposer qu'une chaîne de CID est comparable à un hash brut.

Les scripts de publication doivent arrêter le traitement si l'ajout échoue, si le manifeste ne peut pas être validé ou si le contenu attendu ne peut pas être récupéré. Ils devraient produire un journal d'artefacts qui associe chaque CID à la version source, au statut du pin et à l'approbation. Évite que le script annonce une publication réussie avant que la vérification de récupération indépendante ait fini.

~~~mermaid
flowchart TD
    A[Sources versionnées] --> B[Validation du contenu]
    B --> C[Ajout IPFS reproductible]
    C --> D[CID et manifeste archivés]
    D --> E[Pin sur plusieurs domaines]
    E --> F[Récupération indépendante]
    F --> G{Contenu vérifié ?}
    G -->|Non| H[Arrêter et diagnostiquer]
    G -->|Oui| I[Autoriser publication de la référence]
~~~

## 27. Cache, passerelles et expérience navigateur

Un navigateur peut conserver une ressource en cache même si les blocs ne sont plus accessibles depuis le réseau. Il peut aussi recevoir une page HTTP mise en cache par une passerelle. Ce comportement améliore la rapidité mais peut masquer une panne. Lorsque tu testes la persistance, utilise un environnement distinct, un cache contrôlé et une méthode qui permette de confirmer d'où vient la donnée.

Les erreurs de gateway doivent être distinguées des erreurs du contenu. Un code HTTP 502 ou 504 peut signaler une panne intermédiaire ; une réponse 404 peut signifier que le service n'a pas trouvé le contenu selon son index et ses capacités ; un JSON mal formé peut indiquer que le CID correspond à une autre ressource que celle attendue. Aucun code HTTP isolé ne remplace l'analyse du chemin de récupération.

Les sous-domaines de passerelle peuvent aider à préserver l'isolation d'origine dans le navigateur, alors que d'autres modes de passerelle peuvent partager un même contexte web. Pour une application qui affiche du contenu non fiable, le modèle d'origine, les scripts, les CSP, les types MIME et les options de rendu doivent être examinés. Un fichier HTML public peut contenir du JavaScript qui s'exécute dans le contexte de l'utilisateur si l'application le sert ou l'intègre sans précaution.

Les passerelles peuvent aussi connaître les adresses IP, les heures et les CIDs demandés. Lorsque la confidentialité est importante, évalue les données de télémétrie, les journaux et les politiques du service. Un CID public ne doit pas servir de jeton d'autorisation, et une passerelle ne devrait pas être traitée comme un fournisseur d'identité simplement parce qu'elle sert le fichier.

## 28. Sauvegarde, RPO et RTO des données adressées par contenu

Une stratégie de sauvegarde répond à deux questions : quelle quantité de contenu l'organisation peut-elle se permettre de perdre, et dans quel délai doit-elle rétablir le service ? Le RPO représente le point de données le plus ancien que l'organisation accepte de perdre ; le RTO est le délai cible de retour au service. Pour un catalogue NFT, le RPO peut être proche de zéro pour les métadonnées publiées, car la référence on-chain reste visible même si la copie locale disparaît. Le RTO dépend du temps nécessaire pour restaurer les pins et vérifier les contenus.

Archive les sources originales, les manifestes, les CIDs, les options de construction et la configuration de publication dans un stockage contrôlé. Le pinning réseau ne remplace pas une sauvegarde indépendante : si une erreur de publication ou une action administrative supprime une référence dans plusieurs systèmes, l'archive permet de reconstruire la ressource. Une sauvegarde doit être vérifiable et la procédure de restauration doit être testée.

La copie d'archive doit respecter les contraintes de confidentialité. Ne duplique pas involontairement des secrets dans des logs, paquets ou environnements de test. Contrôle les accès, chiffre les sauvegardes si nécessaire et documente la restauration des clés qui peuvent être requises pour déchiffrer les données.

Organise un exercice de reprise : simule la perte d'un fournisseur, restaure le contenu depuis l'archive ou une source indépendante, compare le contenu avec le CID attendu et vérifie l'accès depuis un environnement externe. Mesure le temps réellement nécessaire et compare-le au RTO annoncé. Si l'objectif n'est pas atteint, adapte l'architecture au lieu d'assouplir silencieusement le critère.

## 29. Contrôle qualité et gouvernance des contenus publiés

Les fichiers publiés sur IPFS doivent suivre une procédure de publication comparable à celle d'un artefact logiciel. Le contenu est construit, validé, approuvé, identifié et conservé. Une mise à jour doit être traçable : quelle version a changé, qui l'a approuvée, pourquoi le CID a changé, quelles références on-chain seront mises à jour et comment l'ancienne version sera conservée ou retirée selon la politique.

Le contrôle qualité peut valider un schéma JSON, des types MIME, la taille, les références de ressources et l'absence de champs sensibles. Les outils automatiques aident à détecter les erreurs de forme, mais ils ne comprennent pas toutes les données privées ou le contexte de publication. Les dossiers à risque devraient exiger une revue humaine et une approbation distincte du développeur qui a préparé le contenu.

Lorsqu'une référence est utilisée par un contrat, vérifie l'ordre des étapes. Il peut être préférable d'épingler et de valider le contenu avant d'écrire le CID dans la chaîne. Si l'écriture on-chain est exécutée en premier et que la publication échoue ensuite, le contrat peut pointer vers une ressource indisponible. Le processus doit définir le statut d'une version entre la préparation, la pinning, la validation et la publication de la référence.

Une fois la référence on-chain mise à jour, archive le hash de transaction, le CID final, le bloc, le manifeste et la confirmation du pin. Si le contrat peut changer la référence, documente ce pouvoir. Si l'URI est censée être immuable, teste que l'implémentation et ses permissions correspondent à cette promesse.

## 30. Comprendre les performances de récupération et la diversité des fournisseurs

La récupération d'un contenu peut varier en fonction de sa taille, du nombre de blocs, du nombre de fournisseurs disponibles, du cache et de la connectivité du nœud. Une ressource de quelques kilo-octets peut être servie rapidement par une seule passerelle, alors qu'un répertoire contenant de nombreuses dépendances peut demander plusieurs requêtes. Il est donc utile de mesurer des classes de contenus différentes et non seulement un petit fichier de test.

Lors d'une enquête sur la lenteur, enregistre le temps jusqu'au premier octet, le temps de récupération complet, le volume transféré, les erreurs et la source utilisée. Une réponse partielle peut être suffisante pour certaines interfaces, mais ne garantit pas que tout le contenu requis soit disponible. Pour un catalogue de fichiers, teste aussi les images, les fichiers audio, les feuilles de style et les références imbriquées qui affectent le rendu.

La diversité des fournisseurs doit être réelle. Plusieurs URL peuvent pointer vers un même service ; plusieurs services peuvent s'appuyer sur le même hébergeur ou le même cache. Si la continuité est importante, documente les fournisseurs, les régions et les chemins de récupération, puis réalise un exercice où une source est volontairement indisponible dans le laboratoire.

Ne cherche pas à optimiser le délai au détriment de la vérification. Une mise en cache peut accélérer l'expérience mais doit être compatible avec le modèle d'intégrité et de version. Si une application affiche un contenu ancien provenant d'un cache tout en prétendant montrer la version actuelle, elle risque d'induire l'utilisateur en erreur. Les métadonnées de version et les identifiants exacts doivent rester disponibles pour le diagnostic.

## 31. Abus de passerelle, contenu non fiable et sécurité du navigateur

Une passerelle ne doit pas devenir un mécanisme d'exécution aveugle de contenu fourni par un utilisateur. Si un catalogue peut référencer du HTML, des scripts, des SVG actifs ou d'autres types de documents complexes, l'application doit définir comment les afficher. Un contenu adressé par CID peut être intègre tout en étant malveillant. L'intégrité garantit que le contenu correspond à son identifiant, pas qu'il est sûr à ouvrir.

Pour les ressources rendues dans un navigateur, évalue l'isolation d'origine, les politiques CSP, les types MIME, l'exécution de scripts, les téléchargements et la façon dont les liens externes sont ouverts. Un iframe correctement sandboxé peut réduire certaines interactions, mais les attributs de sécurité doivent être choisis selon le contenu et testés. Ne suppose pas que l'utilisation d'une passerelle publique isole automatiquement le code provenant de l'utilisateur.

Les services de pinning et les passerelles peuvent être ciblés par des demandes abusives, des contenus volumineux ou des volumes de requêtes anormaux. La protection peut inclure des limites de débit, une file d'attente, une validation des types et tailles, des quotas et un suivi des coûts. Les contrôles doivent éviter qu'un utilisateur consomme toute la capacité disponible en faisant publier des fichiers inutiles ou très volumineux.

Un mécanisme de modération peut empêcher l'application de promouvoir certains contenus, mais il ne peut pas garantir leur disparition de toutes les copies réseau. Distingue la suppression d'une entrée dans ton catalogue, l'arrêt du pinning contrôlé par l'organisation, la désactivation d'un lien de l'interface et l'effacement réel des répliques, qui n'est pas garanti dans un réseau public. Les informations publiées doivent être choisies en tenant compte de cette limite dès la conception.

## 32. Qualité de publication : contrôles avant d'écrire une référence on-chain

Le pipeline de publication devrait valider le contenu avant de créer ou de mettre à jour une référence sur chaîne. Vérifie le format, les champs attendus, les types MIME, les liens internes, la taille, l'absence de secrets et le manifeste d'approbation. Ensuite, ajoute le contenu, enregistre le CID, épingle les blocs, récupère depuis une source indépendante et compare le résultat à l'artefact publié.

Seulement après cette étape, le processus devrait autoriser la transaction qui inscrit le CID ou la référence dans un smart contract. Cette séquence réduit le risque d'avoir un contrat qui pointe vers un contenu qui n'a jamais été conservé correctement. Elle ne supprime pas la possibilité d'une panne future ; c'est pourquoi la surveillance et la redondance restent nécessaires.

Si la transaction on-chain échoue, ne supprime pas automatiquement le contenu déjà épinglé. Il peut être réutilisé au prochain essai si la version n'a pas changé. Si une nouvelle publication modifie le fichier, génère et valide un nouveau CID, conserve la relation entre les versions et indique quelle référence est actuellement approuvée.

Les critères de production doivent inclure la récupération indépendante, l'approbation du contenu, la vérification de la configuration du réseau et du contrat, les journaux d'artefacts et la capacité à revenir à la version précédente lorsque le modèle le permet. Une version précédente peut devoir rester accessible pour préserver l'historique, même si elle n'est plus affichée comme version courante. Le processus doit donc différencier archivage, retrait du catalogue et suppression des pins contrôlés.

## 33. Cycle de vie d'un contenu : publication, évolution et archivage

Le cycle de vie d'un contenu doit être défini avant d'en publier une grande quantité. Une ressource peut être préparée, validée, approuvée, ajoutée, épinglée, annoncée dans le catalogue, remplacée, archivée ou retirée de l'interface. Ces états correspondent à des actions différentes. Supprimer une référence visible ne supprime pas automatiquement les copies réseau ; arrêter le pinning d'une organisation ne signifie pas que le contenu est absent des caches et des nœuds tiers.

Définis les responsabilités pour chaque étape. L'équipe de contenu peut préparer un fichier, l'équipe de sécurité valider qu'il ne contient pas de secret, le pipeline générer un CID, et un opérateur approuver la mise à jour on-chain. L'approbation devrait porter sur le contenu exact, identifié par un CID, et non seulement sur un nom de fichier qui pourrait être modifié après la revue.

Lorsqu'une version change, conserve la relation entre l'ancienne et la nouvelle version, la raison du changement, le manifeste d'approbation et les contrats ou interfaces affectés. Une ressource ancienne peut être nécessaire à l'historique d'une transaction ou à la preuve de ce qu'un utilisateur a vu à une date donnée. L'archivage peut donc être plus approprié qu'une suppression locale.

Pour les données sensibles, le meilleur contrôle est souvent de ne pas les publier du tout. Si un contenu public doit être retiré, l'organisation peut supprimer ses copies contrôlées, retirer les références applicatives et demander aux fournisseurs d'arrêter le pinning lorsque leurs conditions le permettent. Le rapport doit néanmoins être honnête sur l'impossibilité de garantir l'effacement des copies détenues par des tiers.

## 34. Projet pratique avancé : créer un mini-catalogue versionné

Crée un mini-catalogue composé de trois fiches JSON et de trois médias de test. Chaque fiche doit être non sensible et inclure un identifiant logique, une version, le CID du média et un type de contenu. Publie les fichiers avec des paramètres documentés, puis crée un manifeste qui relie les versions aux CIDs. Le catalogue doit permettre de distinguer l'identité logique d'un élément de l'identité cryptographique de chaque fichier.

Ajoute chaque version sur deux destinations de pinning qui ne dépendent pas du même compte ou de la même configuration, si tes ressources de laboratoire le permettent. Récupère ensuite le manifeste depuis un environnement distinct et vérifie les ressources liées. Simule une panne de l'une des destinations et mesure si l'application reste disponible, si l'alerte est déclenchée et si le contenu attendu peut être restauré.

Modifie une fiche et republie-la. Explique si la modification représente une nouvelle version de l'objet ou une nouvelle version technique des octets. Si le CID racine du catalogue change, mets à jour le manifeste sans effacer l'historique. Documente qui peut approuver la nouvelle référence et comment l'interface signale la version courante.

Le rapport final doit inclure les CIDs réellement obtenus, les options utilisées, les résultats des récupérations, la preuve de la redondance, les erreurs observées et les limites. Il doit aussi mentionner les coûts et les contraintes de rétention du système choisi. Un mini-catalogue est réussi lorsque les versions sont traçables, les contenus vérifiables et le chemin de récupération reproductible par un autre opérateur.

## 35. Coûts, limites de service et stratégie de capacité

Le stockage décentralisé ne signifie pas que l'opération ne coûte rien. La publication peut consommer de la bande passante, de l'espace disque, du temps CPU et un budget de service de pinning. Les passerelles peuvent appliquer des limites de requêtes, les fournisseurs des quotas et le nœud local des limites de stockage. Une application qui augmente rapidement le nombre de fichiers doit prévoir la capacité nécessaire pour les publications initiales, les versions historiques et les récupérations.

Établis un modèle de coût par classe de contenu : taille moyenne, nombre de fichiers, nombre de copies, fréquence de mise à jour, volume de lectures et durée de conservation. Sépare les coûts fixes — infrastructure et supervision — des coûts variables, comme les transferts, les requêtes et les opérations d'ajout. N'utilise pas une seule estimation pour tous les objets, car un catalogue de petites fiches et une bibliothèque de vidéos ont des profils très différents.

Les limites de service doivent être définies avec le produit. Si une requête de contenu échoue, l'interface doit éviter les boucles de répétition qui aggravent une surcharge. Les tentatives devraient avoir un délai, un nombre maximal, une stratégie de temporisation et une journalisation contrôlée. Les tâches de pinning massives doivent être mises en file, avec un statut de progression et une reprise après interruption.

La capacité de stockage doit aussi être surveillée. Une saturation du volume peut empêcher un nœud de conserver des données ou de fonctionner normalement. Avant une mise à niveau ou une migration, estime la taille des fichiers, les copies, l'espace temporaire et la marge nécessaire. Un plan qui utilise 100 % du volume nominal n'a pas de capacité de reprise.

Les indicateurs opérationnels peuvent inclure le taux de récupération, la latence, les erreurs par fournisseur, la taille totale épinglée, le nombre de CIDs vérifiés et l'âge du dernier test de restauration. Les objectifs de capacité doivent être réévalués lorsque le catalogue, la politique de rétention ou la charge évolue.

## 36. Questions d'entraînement avec corrigé

### Question 1 : Qu'est-ce qu'un CID ?

**Correction :** Un identifiant de contenu qui encode notamment une version, un codec et une représentation de hash. Il aide à identifier et vérifier le contenu, mais ne précise pas à lui seul où il est stocké ni si quelqu'un le conserve.

### Question 2 : Un CID est-il nécessairement égal au SHA-256 du fichier ?

**Correction :** Non. Un CID peut référencer une racine de graphe et inclure des informations de format et de version. Il peut égaler le hash brut dans certains cas précis, mais il ne faut pas supposer cette équivalence.

### Question 3 : Le pinning garantit-il une permanence absolue ?

**Correction :** Non. Il protège les données contre la collecte locale dans le modèle du nœud ou du service choisi. La persistance dépend de la conservation réelle, des contrats de service et de la redondance.

### Question 4 : IPFS chiffre-t-il les contenus par défaut ?

**Correction :** Non. L'adressage par contenu n'est pas un mécanisme de confidentialité. Les données publiques peuvent être récupérées par ceux qui disposent de l'identifiant ou qui les découvrent autrement.

### Question 5 : Une passerelle publique est-elle la même chose qu'un nœud IPFS local ?

**Correction :** Non. Une passerelle fournit un accès HTTP et peut cacher les détails du réseau de pairs. Un nœud local peut parler directement aux protocoles du réseau, conserver les blocs et vérifier le contenu selon son implémentation.

### Question 6 : Pourquoi deux ajouts peuvent-ils produire des CIDs différents pour le même fichier ?

**Correction :** Les paramètres de construction, le codec, le découpage ou la version du CID peuvent différer. Il faut comparer les profils utilisés avant de conclure que les données sont corrompues.

### Question 7 : Pourquoi ne faut-il pas utiliser un CID comme un secret ?

**Correction :** Parce qu'il identifie le contenu, et non un droit d'accès. Si le contenu est public et le CID connu, d'autres personnes peuvent tenter de le récupérer.

### Question 8 : Quel est l'intérêt d'IPNS ?

**Correction :** Il ajoute un mécanisme de nommage mutable qui peut pointer vers un CID actualisé. Il implique des règles de mise à jour et de cache qui doivent être documentées.

### Question 9 : Que faut-il contrôler lorsqu'une ressource IPFS ne se charge pas ?

**Correction :** Le CID exact, la disponibilité des blocs, les pins, les fournisseurs, le réseau, la passerelle, la structure du DAG et les éventuelles dépendances de métadonnées. Une URL en échec ne prouve pas à elle seule la disparition du contenu.

### Question 10 : Que devrait contenir une stratégie de persistance ?

**Correction :** Les copies attendues, leurs propriétaires, leur indépendance, la fréquence des vérifications, les alertes, la restauration, la rétention et les limites de suppression.

## 37. Challenge final : concevoir le stockage d'un catalogue NFT

Une équipe veut publier un catalogue NFT avec plusieurs milliers de métadonnées et fichiers média. Le contrat conserve les références, une interface affiche les objets et un fournisseur de pinning est choisi pour simplifier l'exploitation. L'équipe demande une conception qui ne se limite pas à envoyer les fichiers sur IPFS.

### Travail demandé

Écris une architecture avec la manière de produire les CIDs, la structure de stockage, la stratégie de pinning redondant, le mécanisme de mise à jour, le contrôle d'intégrité, la protection des données sensibles, la procédure de récupération et le suivi de disponibilité. Ajoute des tests pour les références erronées, le gateway indisponible, un pin manquant et une mise à jour de métadonnées.

### Correction proposée

La solution conserve les métadonnées et médias dans une structure documentée et utilise des CIDs pour les versions immuables. Elle conserve les références de manière vérifiable et n'utilise une couche mutable que si le modèle métier le justifie. Les pins sont répartis sur des domaines de panne réellement distincts, et des récupérations périodiques sont faites depuis des environnements qui ne détiennent pas déjà les blocs en cache.

Les données privées sont exclues de la publication publique, et la politique mentionne explicitement qu'une suppression locale ne garantit pas l'effacement des copies. Les mises à jour sont autorisées par un rôle clairement défini, enregistrées et testées. Les alertes distinguent une passerelle en panne, un contenu manquant, un CID incorrect et une erreur d'affichage. La revue de mise en production exige un test de récupération indépendant et un exercice de restauration.

## Glossaire

**IPFS** : ensemble de protocoles pour identifier et transférer du contenu dans un réseau pair-à-pair.

**CID** : Content Identifier, identifiant comprenant une version, un codec et un multihash.

**Multihash** : représentation qui décrit l'algorithme de hash et sa valeur.

**Codec** : identifiant du format de données à interpréter.

**DAG** : graphe acyclique orienté utilisé pour organiser des blocs liés.

**UnixFS** : format de représentation des fichiers et répertoires couramment utilisé avec IPFS.

**Pinning** : mécanisme qui demande à un nœud de conserver un contenu plutôt que de le laisser à la collecte de données.

**Passerelle** : service HTTP qui facilite l'accès à du contenu IPFS.

**IPNS** : système de nommage mutable pouvant pointer vers un CID.

**DNSLink** : mécanisme qui associe un nom DNS à une référence IPFS selon la configuration choisie.

**Persistance** : conservation effective et continue des données.

**Disponibilité** : possibilité de récupérer les données nécessaires au moment voulu.

**Intégrité** : propriété selon laquelle le contenu correspond à l'identifiant ou à l'engagement attendu.

## Pour aller plus loin

- Documentation IPFS, adressage par contenu : https://docs.ipfs.tech/concepts/content-addressing/
- Documentation IPFS, persistance : https://docs.ipfs.tech/concepts/persistence/
- Documentation IPFS, démarrage : https://docs.ipfs.tech/install/
- Documentation IPFS, passerelles : https://docs.ipfs.tech/concepts/ipfs-gateway/
- Documentation IPFS, IPNS : https://docs.ipfs.tech/concepts/ipns/

Vérifie les options de commande et les valeurs par défaut dans la documentation correspondant à ta version de Kubo. L'architecture de production doit préciser la politique de disponibilité et de confidentialité, car aucun identifiant cryptographique ne remplace un plan de conservation et de récupération.
