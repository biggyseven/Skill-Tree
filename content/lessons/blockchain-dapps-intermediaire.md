# Architecture DApp

## Encadré de mise en contexte

Une application décentralisée, ou DApp, combine une interface utilisateur et des composants qui s'appuient sur une blockchain. Le mot « décentralisée » ne signifie pas que chaque élément du produit est réparti entre des milliers de machines. L'interface peut être hébergée sur un serveur classique, l'authentification peut dépendre d'un fournisseur externe, les données de recherche peuvent être gérées par un indexeur et les lectures blockchain peuvent passer par un fournisseur RPC. La décentralisation doit être analysée composant par composant.

L'architecture d'une DApp comporte généralement un frontend, un portefeuille, une bibliothèque cliente, un fournisseur RPC, un ou plusieurs contrats intelligents, le réseau P2P et le consensus. Certaines applications utilisent aussi un indexeur, un backend d'API, un service de notification, un stockage décentralisé ou un oracle. Ces composants ont des responsabilités et des modèles de confiance différents. Une interface élégante peut cacher un contrat vulnérable ; un contrat correct peut être utilisé depuis une interface malveillante ; une application peut afficher un état périmé si son indexeur est en retard.

Ce cours t'apprend à concevoir une architecture compréhensible et résiliente. Il couvre le parcours des lectures et transactions, les portefeuilles et la connexion, RPC, les événements et indexeurs, le stockage, la gestion des erreurs, la sécurité du frontend, les tests et le déploiement. Le but n'est pas seulement de « connecter un site à MetaMask », mais de comprendre le trajet des données et les responsabilités de chaque couche.

## Objectifs d'apprentissage

À la fin du cours, tu sauras :

- décrire l'architecture classique d'une DApp EVM ;
- distinguer frontend, portefeuille, fournisseur RPC, nœud, contrat et indexeur ;
- expliquer le parcours d'une lecture et d'une transaction d'écriture ;
- gérer correctement les changements de compte, de réseau et de statut de transaction ;
- comprendre l'ABI, le chain ID et les adresses de contrat ;
- déterminer quelles données appartiennent à la blockchain et lesquelles restent hors chaîne ;
- traiter les événements, les réorganisations et les données indexées ;
- concevoir les états de chargement, erreurs et confirmations de l'interface ;
- réduire les risques de phishing, d'approbation excessive et de dépendance à un seul fournisseur ;
- définir une stratégie de tests, d'observabilité et de reprise.

## 1. Qu'est-ce qu'une DApp ?

Une DApp est une application qui utilise des contrats intelligents ou d'autres composants d'un réseau décentralisé pour exécuter une partie importante de sa logique. Le frontend peut être développé avec les technologies web habituelles. Il présente les informations, permet à l'utilisateur de choisir une action et construit les appels nécessaires au backend blockchain.

La propriété déterminante est que certaines règles et données sont appliquées par le protocole blockchain plutôt que par un serveur applicatif unique. Cependant, une application peut être hybride : elle peut utiliser des contrats pour les transferts et un backend classique pour les recommandations, les notifications ou la recherche. L'architecture doit donc expliciter les fonctions qui dépendent du consensus et celles qui restent contrôlées par le fournisseur.

~~~mermaid
flowchart TD
    U["Utilisateur dans le navigateur"] --> F["Frontend de la DApp"]
    F --> W["Portefeuille et signature"]
    F --> R["Fournisseur RPC"]
    W --> R
    R --> N["Nœud blockchain"]
    N --> P["Réseau P2P et consensus"]
    P --> C["Contrats intelligents"]
    N --> I["Indexeur et API de lecture"]
    I --> F
~~~

Le diagramme n'indique pas que le contrat est hébergé comme un serveur web. Le bytecode et l'état vivent dans le réseau blockchain, et les nœuds exécutent les appels selon les règles. Le frontend utilise des interfaces réseau pour demander des données ou soumettre une transaction.

## 2. Les composants principaux

### 2.1 Frontend

Le frontend est l'interface avec laquelle l'utilisateur interagit. Il présente les soldes, les formulaires, les statuts de transaction et les messages d'erreur. Il peut être écrit en HTML/CSS/JavaScript, avec React, Vue, Svelte ou une autre technologie. Le choix du framework ne détermine pas à lui seul la décentralisation de l'application.

Le frontend n'est pas une autorité de sécurité. Il peut afficher un montant ou un destinataire, mais il doit construire une transaction cohérente avec l'opération annoncée et afficher les détails importants avant que l'utilisateur signe. Un frontend compromis peut tenter de faire signer une opération différente de celle attendue. Les utilisateurs doivent donc voir les données pertinentes dans leur portefeuille lorsque cela est possible, et l'équipe doit réduire les possibilités de substitution malveillante.

### 2.2 Portefeuille

Le portefeuille gère les clés et permet à l'utilisateur d'autoriser les transactions ou certaines signatures. Il peut être une extension du navigateur, une application mobile, un portefeuille matériel ou une solution intégrée. La DApp ne doit jamais demander la clé privée ou la phrase de récupération. Elle demande au portefeuille de fournir l'adresse et de signer les données selon le protocole.

La connexion à un portefeuille ne signifie pas que le site connaît l'identité civile de l'utilisateur. Elle fournit généralement une adresse ou un compte actif. Une DApp doit demander explicitement l'autorisation de connexion, expliquer pourquoi l'adresse est nécessaire et éviter de solliciter des signatures non compréhensibles.

### 2.3 Bibliothèque cliente

Une bibliothèque web3 permet de formater les requêtes, encoder les appels selon l'ABI, décoder les résultats et interagir avec le fournisseur. Elle peut aider à gérer les unités, les événements et le statut des transactions. La version de la bibliothèque doit être tenue à jour et fixée dans les dépendances du projet pour que les builds restent reproductibles.

Une bibliothèque ne garantit pas que l'adresse du contrat soit correcte. Le développeur doit gérer les adresses par réseau, valider le chain ID et vérifier que l'interface attendue correspond à l'implémentation déployée.

### 2.4 Fournisseur RPC et nœud

Le fournisseur RPC expose des méthodes de lecture et d'envoi de transactions. Il peut être un nœud que l'équipe exploite ou un service tiers. Il permet au frontend d'obtenir des informations sur les blocs, les comptes, les transactions et les contrats.

Le fournisseur RPC peut être indisponible, en retard, limité ou configuré avec des politiques différentes. Un fournisseur peut aussi observer des métadonnées relatives aux requêtes de l'utilisateur. Pour les opérations importantes, il est utile de prévoir un plan de reprise ou une manière de comparer des résultats via une source indépendante. Plusieurs URL qui reposent sur le même fournisseur ne fournissent pas forcément une indépendance réelle.

### 2.5 Contrat intelligent

Le contrat définit la logique on-chain et l'état partagé : soldes, droits, propositions, votes ou règles métier. Les règles importantes qui doivent être imposées à tous les utilisateurs doivent être vérifiées par le contrat, pas seulement par le frontend. Masquer un bouton d'administration ne protège pas une fonction publique si le contrat ne vérifie pas les permissions.

Le contrat doit être audité selon son niveau de risque. Il faut comprendre sa source, ses dépendances, son modèle de mise à niveau et les rôles qui peuvent changer ses paramètres. La DApp doit vérifier le réseau et l'adresse du contrat avant de soumettre des opérations.

### 2.6 Indexeur et backend

Un indexeur lit la blockchain, traite les événements et construit une base de données de lecture plus pratique. Il peut accélérer la recherche d'historique, les classements ou les filtres complexes. Mais cette base est une projection des données de la chaîne : elle doit se synchroniser, gérer les réorganisations et pouvoir être reconstruite.

Un backend classique peut gérer des notifications, de l'analytique, des contenus ou des sessions. Il doit être considéré comme une source contrôlée par son opérateur. Si le backend décide à lui seul qui peut retirer des fonds alors que cette règle est présentée comme on-chain, l'architecture doit être réévaluée.

## 3. Lire l'état de la blockchain

Une lecture peut demander le solde d'un compte, appeler une fonction view, consulter un événement ou interroger un indexeur. Ces opérations n'ont pas toutes les mêmes garanties.

Une lecture directe du contrat à un bloc donné interroge l'état fourni par le nœud. Il faut comprendre si la requête vise le dernier bloc observé, un bloc finalisé ou une hauteur précise. « Dernier état » peut changer entre deux requêtes et deux fournisseurs peuvent être à des hauteurs différentes.

Un indexeur peut fournir des recherches beaucoup plus pratiques, mais il peut avoir un retard. Pour une vue de portefeuille, le compromis peut être acceptable ; pour une opération critique, l'application peut vouloir vérifier directement le contrat ou attendre une finalité définie par le réseau.

### 3.1 Lecture simple et état périmé

Supposons qu'une DApp affiche une quantité disponible. Si elle la charge à l'ouverture de la page et ne l'actualise jamais, un changement on-chain réalisé par un autre utilisateur peut rendre l'affichage périmé. L'application doit définir quand réinterroger les données : changement de compte, changement de réseau, retour d'un onglet en arrière-plan, réception d'un événement ou après confirmation d'une transaction.

L'actualisation doit être contrôlée pour éviter les requêtes excessives. Il peut être utile de combiner un cache à durée courte et une invalidation déclenchée par les événements. Mais le cache doit toujours être présenté comme un mécanisme de performance, pas comme une source normative de vérité.

### 3.2 Pagination et historique

Une demande qui récupère tout l'historique depuis le premier bloc est coûteuse et peut dépasser les limites du fournisseur. Les indexeurs et API peuvent offrir la pagination, des filtres par adresse et des données préagrégées. La DApp doit gérer les pages, les doublons, les retards et les événements réorganisés.

Un indexeur fiable doit garder une référence à la hauteur ou au bloc traité, détecter les réorganisations et corriger les enregistrements qui appartiennent à une branche qui n'est plus suivie. Sans cette gestion, un historique peut contenir deux événements incompatibles ou continuer d'afficher un transfert retiré de l'historique actif.

## 4. Écrire sur la blockchain

Une écriture suit une séquence plus longue qu'une lecture. La DApp prépare les paramètres, le portefeuille affiche ou valide l'opération, l'utilisateur signe, le fournisseur diffuse la transaction, les nœuds la vérifient, un producteur la sélectionne, puis la transaction est exécutée dans un bloc. Le reçu permet ensuite de connaître le statut d'exécution.

~~~mermaid
sequenceDiagram
    participant U as Utilisateur
    participant F as Frontend
    participant W as Portefeuille
    participant R as RPC
    participant C as Contrat
    U->>F: Choisit une action
    F->>F: Valide le formulaire
    F->>W: Demande une transaction
    W-->>U: Affiche les détails à signer
    U->>W: Autorise ou refuse
    W->>R: Diffuse la transaction signée
    R-->>F: Hash de transaction
    F->>R: Suit le reçu
    R-->>F: Reçu et statut d'exécution
    F-->>U: Affiche le résultat réel
~~~

L'interface doit distinguer les états : formulaire valide, portefeuille ouvert, signature refusée, transaction envoyée, transaction en attente, incluse, exécution réussie, exécution échouée, confirmation ou finalité atteinte. Un simple indicateur « succès » immédiatement après la signature est trompeur.

### 4.1 Signature refusée

L'utilisateur peut annuler la fenêtre de signature. Ce n'est pas nécessairement une erreur technique. L'interface devrait arrêter le flux et afficher un message neutre, sans relancer automatiquement des demandes répétées qui inciteraient l'utilisateur à signer sans comprendre.

### 4.2 Transaction envoyée mais non incluse

Recevoir un hash signifie généralement que la transaction a été soumise au fournisseur ou au réseau, mais ne prouve pas qu'elle est incluse. Elle peut rester en attente, être remplacée, être rejetée par les nœuds, subir une congestion ou être oubliée par certains fournisseurs. L'interface doit continuer à suivre le statut et fournir des moyens de consulter l'opération.

### 4.3 Reçu et succès de l'exécution

La transaction peut être incluse mais son exécution peut échouer. L'interface doit examiner le statut du reçu et, si besoin, montrer un message utile. Un échec d'exécution peut consommer du gas. Le retour visuel doit dire explicitement ce qui a échoué et ne pas affirmer que le résultat métier a été obtenu.

### 4.4 Réorganisations et finalité

Un bloc récent peut être retiré de la branche suivie selon le mécanisme de consensus. Pour une opération de faible risque, l'application peut accepter une confirmation initiale ; pour une opération critique, elle doit définir un seuil plus robuste ou attendre le statut de finalité pertinent. Le nombre de confirmations et la signification de la finalité dépendent du réseau.

La DApp ne doit pas inventer une garantie universelle. Elle doit connaître la chaîne cible, ses règles et le risque commercial du scénario. Une transaction d'achat d'un billet de faible valeur et un transfert d'actifs importants ne requièrent pas nécessairement la même politique.

## 5. Gestion du compte et du réseau

Un utilisateur peut changer de compte dans son portefeuille ou basculer vers un autre réseau pendant que la DApp est ouverte. L'application doit détecter ces changements, invalider les données mises en cache et réinterroger l'état. Une adresse présente sur plusieurs réseaux peut correspondre à des états différents et interagir avec des contrats différents.

### 5.1 Chain ID

Le chain ID identifie le réseau dans le contexte des transactions et évite une partie des risques de rejeu entre chaînes. La DApp doit comparer le réseau actif à la configuration attendue avant de proposer une transaction. Une adresse de contrat seule ne suffit pas pour déterminer le réseau.

Les identifiants peuvent être configurés dans les outils et les portefeuilles. Il ne faut pas accepter sans vérification une valeur de chain ID fournie par une page externe ou par un paramètre URL. Le frontend doit disposer d'une liste connue des réseaux pris en charge et afficher clairement le réseau actif.

### 5.2 Changement de compte

Quand le compte change, les données qui dépendent de l'adresse doivent être invalidées : solde, autorisations, positions, tâches en attente et statut de connexion. L'interface doit vérifier que la transaction à soumettre utilise bien le compte attendu. Un formulaire créé pour un compte ne doit pas être signé silencieusement depuis un autre compte.

### 5.3 Connexion et confidentialité

La DApp devrait demander la connexion au portefeuille au moment utile et expliquer ce que la connexion permet. Une adresse peut devenir une donnée personnelle selon le contexte et les informations associées. Les journaux d'analytique, les cookies et les systèmes de support doivent limiter la collecte au nécessaire et éviter d'associer sans raison les adresses à des identités civiles.

Un mécanisme de signature de message peut être utilisé pour prouver le contrôle d'une adresse dans un service web, mais il faut utiliser un format de signature prévu pour l'authentification, avec domaine, nonce, expiration et protection contre le rejeu. Demander de signer une chaîne arbitraire est dangereux et peut entraîner des confusions avec les signatures qui autorisent des transactions ou des ordres.

## 6. ABI, adresses et configuration

La DApp doit connaître l'ABI et l'adresse du contrat correspondant au réseau actif. La configuration devrait être versionnée et vérifiée dans le processus de déploiement. Pour chaque réseau, le projet conserve les adresses des contrats, le chain ID, les dépendances et le commit correspondant au code source.

Une adresse erronée peut conduire à appeler un contrat qui ne correspond pas à l'interface attendue. Le contrat peut retourner des données mal interprétées, ne pas répondre comme prévu ou demander à l'utilisateur de signer une opération dangereuse. Avant le déploiement de l'interface, il faut vérifier les adresses, les transactions de déploiement et le code effectivement publié.

### 6.1 Séparer configuration et secrets

Les adresses publiques de contrats et les identifiants de réseaux ne sont pas des secrets. Les clés privées, les phrases de récupération et certaines clés API privées le sont. Une variable d'environnement utilisée lors du build frontend peut être intégrée au bundle et visible par les utilisateurs : il ne faut pas y placer un secret en pensant qu'il restera privé.

Les services publics peuvent utiliser des clés API qui sont de toute façon exposées côté client, mais elles doivent être limitées et protégées contre l'abus par des quotas, des domaines autorisés ou une architecture appropriée. Les secrets de serveur doivent rester dans le backend.

## 7. Événements, indexation et synchronisation

Les contrats émettent des événements qui facilitent les notifications et les historiques. Le frontend peut écouter les événements en temps réel ou passer par un indexeur pour obtenir des historiques plus complexes. Le choix dépend de la volumétrie, de l'expérience attendue et des garanties de cohérence.

Un écouteur direct doit gérer les déconnexions et les événements répétés. Lorsqu'il se reconnecte, il peut devoir récupérer une plage de blocs antérieurs pour combler les événements manquants. Cette récupération doit éviter les doublons et traiter les réorganisations. Un indexeur doit conserver un curseur de progression et pouvoir reprendre à partir d'une hauteur connue.

### 7.1 État canonique et vue de lecture

L'état canonique est celui obtenu par les règles du réseau dans la branche acceptée. Une base d'indexation ou un cache est une projection qui peut être en retard ou comporter un bug. Pour les opérations critiques, l'application doit savoir quelles données proviennent directement du contrat et lesquelles proviennent d'un service auxiliaire.

Par exemple, un site peut afficher la liste des NFT grâce à un indexeur, mais utiliser directement le contrat pour vérifier la propriété avant de proposer un transfert. Cette approche équilibre performance et cohérence, mais la source choisie doit être documentée et testée.

## 8. Stockage on-chain et off-chain

Toutes les données n'ont pas besoin d'être inscrites dans une blockchain. Les écritures on-chain sont généralement publiques, répliquées et coûteuses. Le contenu volumineux ou fréquemment modifié peut être conservé hors chaîne, avec un identifiant ou un engagement cryptographique sur chaîne lorsque cela convient.

Le stockage off-chain crée d'autres risques : disponibilité, censure, modification, disparition du fournisseur, droits d'accès et formats obsolètes. Le fait de stocker un hash sur chaîne permet de vérifier qu'un fichier correspond à un engagement, mais ne garantit pas que le fichier sera accessible. Une architecture doit prévoir qui conserve les données, combien de copies existent, comment les restaurer et comment les utilisateurs vérifient leur intégrité.

### 8.1 IPFS et identifiants de contenu

IPFS utilise des identifiants basés sur le contenu pour adresser des données. Cela peut aider à détecter qu'un contenu récupéré correspond à l'identifiant attendu, mais l'identifiant n'assure pas à lui seul que le fichier restera hébergé. Des nœuds ou services doivent continuer à conserver et servir les données.

Une DApp qui utilise IPFS devrait documenter les stratégies de pinning, de réplication et de récupération. Elle doit aussi éviter de stocker publiquement des données confidentielles ou personnelles sous prétexte que le contenu est adressé par son hash. Le hachage n'est pas un chiffrement.

### 8.2 Backend classique

Un backend peut fournir des fonctions utiles : recherche complexe, e-mail, contenu éditorial, analytique ou synchronisation. Il doit être considéré comme une dépendance et une source potentielle de panne. La DApp devrait indiquer quelles fonctionnalités continuent à fonctionner lorsque le backend est indisponible et éviter de faire dépendre une propriété on-chain critique d'une réponse non vérifiée du backend.

## 9. Sécurité du frontend

Le frontend est une cible de phishing et de substitution. Un attaquant qui contrôle le code de l'interface peut modifier un destinataire, changer l'adresse d'un contrat, afficher un coût trompeur ou demander des signatures inutiles. Il est donc nécessaire de sécuriser le pipeline de livraison, les dépendances, les domaines, les clés de publication et les mises à jour.

Les mesures utiles incluent l'utilisation de dépendances maintenues, le verrouillage des versions, l'analyse des paquets, une politique de déploiement contrôlée, des en-têtes de sécurité adaptés, la protection contre les scripts injectés et une surveillance des changements de domaine. Les avertissements de signature doivent être clairs ; l'application doit montrer la fonction, le montant, le destinataire, le réseau et les permissions pertinentes lorsque cela est possible.

### 9.1 Approvals et autorisations de jetons

Dans les applications de jetons, un utilisateur peut autoriser un contrat à dépenser des jetons à sa place. Une approbation très élevée peut permettre au contrat d'utiliser davantage de jetons que nécessaire. La DApp doit demander les permissions minimales nécessaires, expliquer leur portée et proposer une manière de vérifier les approbations actives.

Une signature d'approbation n'est pas la même chose qu'un simple login. Elle peut créer une autorisation durable. Les interfaces doivent distinguer une signature de connexion, une approbation de jeton, une transaction de transfert et un appel de contrat. Les utilisateurs ne devraient pas être amenés à signer une demande sans comprendre ce qu'elle autorise.

### 9.2 Validation des entrées

Le frontend doit valider les valeurs pour améliorer l'expérience, mais le contrat doit revalider les invariants critiques. Un utilisateur peut appeler le contrat sans passer par l'interface. Ne te fie pas uniquement à la validation de formulaire pour les limites de montant ou les permissions.

Les chaînes, adresses et quantités doivent être normalisées et affichées de manière claire. Les conversions d'unités sont une source d'erreurs : le token peut utiliser un nombre de décimales différent de celui supposé par le frontend. Il faut lire la précision réelle et ne pas confondre valeur brute et valeur humaine.

## 10. États de l'interface et expérience utilisateur

Une bonne DApp représente l'état réel du processus au lieu d'afficher un simple bouton « Envoyer ». Pour une transaction, les étapes peuvent inclure : données saisies, validation locale, portefeuille demandé, attente de signature, signature refusée, transaction diffusée, confirmation en attente, incluse, succès d'exécution, échec, statut finalisé ou état à vérifier après une réorganisation.

L'utilisateur doit comprendre les actions qu'il peut entreprendre à chaque étape. Pendant l'attente, afficher le hash et un lien vers un explorateur fiable peut aider. En cas d'échec, expliquer si l'opération a été refusée avant soumission ou si elle a échoué après inclusion. Ne jamais prétendre qu'une transaction a réussi sans vérifier le reçu ou l'état pertinent.

Les boutons doivent éviter les doubles soumissions accidentelles, mais un verrou de bouton ne remplace pas les règles de contrat. L'application doit également gérer le rafraîchissement de la page, le changement de compte et la reconnexion du portefeuille sans perdre le contexte de la transaction.

## 11. Tests d'une DApp

La qualité d'une DApp dépend des contrats et de l'interface. Il faut tester la logique on-chain, l'encodage des appels, la gestion des comptes, les erreurs RPC et l'expérience utilisateur. Les tests peuvent utiliser un réseau local, des contrats factices et un fournisseur simulé pour contrôler les réponses.

Les scénarios à couvrir incluent :
- portefeuille absent ou refus de connexion ;
- réseau incorrect ou changement de chain ID ;
- changement de compte durant la saisie ;
- contrat non disponible à l'adresse configurée ;
- lecture échouée ou périmée ;
- transaction rejetée par le portefeuille ;
- transaction relayée mais jamais incluse ;
- transaction incluse avec revert ;
- succès suivi d'une réorganisation ou d'un retard de l'indexeur ;
- approbation refusée ou autorisation insuffisante ;
- réponse RPC mal formée ou fournisseur indisponible.

Les tests doivent vérifier les messages montrés à l'utilisateur, pas uniquement les appels techniques. Une erreur correctement détectée mais affichée comme un succès est un défaut fonctionnel et de sécurité.

## 12. Déploiement et exploitation

Une DApp est déployée dans plusieurs composants. Les contrats sont déployés sur une blockchain ; l'interface web est hébergée dans une infrastructure web ou de stockage ; les indexeurs et backends sont des services à exploiter ; la configuration réseau doit relier les bonnes adresses aux bons environnements.

Le processus de livraison doit différencier développement, réseau de test et production. Les adresses et clés des environnements ne doivent pas être mélangées. Avant une mise en production, vérifier la compilation, les tests, les permissions, le code source des contrats, les endpoints RPC, les politiques CORS, la configuration et les plans de retour arrière.

Une application peut être mise à jour même si un contrat immuable ne l'est pas. À l'inverse, mettre à jour le frontend peut changer le comportement attendu alors que le contrat reste identique. Il faut donc versionner la combinaison d'interface, d'ABI, de contrat et de configuration qui a été validée.

### 12.1 Observabilité

Les métriques opérationnelles utiles incluent latence des requêtes, taux d'erreur RPC, nombre de transactions en attente, temps entre soumission et inclusion, retard de l'indexeur, erreurs de décodage, répartition des réseaux et changements de configuration. Les journaux doivent éviter de collecter des secrets ou de publier des données personnelles inutiles.

Les alertes doivent distinguer un fournisseur qui tombe en panne d'un réseau qui cesse d'avancer. Une stratégie de reprise peut prévoir un fournisseur de secours, mais il faut tester que celui-ci suit le bon réseau, applique les mêmes règles et n'introduit pas de résultats périmés.

## 13. Choisir une architecture selon le modèle de confiance

Toutes les DApps ne doivent pas employer la même architecture. Une application de lecture publique peut appeler directement un contrat et utiliser un indexeur pour l'historique. Une application qui possède des processus métiers complexes peut utiliser un backend pour la recherche, les notifications et la préparation de données, tout en gardant les règles de transfert critiques dans les contrats. Une DApp qui exige un contrôle strict de l'infrastructure peut exploiter son propre nœud ou son propre fournisseur RPC.

Le diagramme ci-dessous montre une architecture hybride typique. Les composants hors chaîne peuvent être remplacés ou répliqués, mais ils introduisent des dépendances à documenter.

~~~mermaid
flowchart TD
    U["Utilisateur"] --> UI["Frontend public"]
    UI --> W["Portefeuille"]
    UI --> API["API métier facultative"]
    API --> IDX["Indexeur / base de lecture"]
    UI --> RPC1["RPC principal"]
    W --> RPC1
    RPC1 --> N["Nœud / réseau blockchain"]
    RPC2["RPC secondaire"] -. "reprise contrôlée" .-> UI
    N --> IDX
~~~

### Décisions à documenter

Pour chaque composant, réponds aux questions suivantes : qui le déploie, qui peut le modifier, que sait-il sur l'utilisateur, que se passe-t-il s'il tombe en panne et comment détecter une réponse périmée ? L'API métier peut fournir des recommandations ou calculs hors chaîne, mais le contrat doit revalider toutes les règles critiques avant de modifier des actifs.

Le choix d'un fournisseur RPC externe réduit la charge opérationnelle, mais crée une dépendance. Exploiter son propre nœud donne plus de contrôle sur la collecte et la disponibilité des données, mais exige de gérer le stockage, les mises à jour, les connexions et la supervision. Un modèle mixte peut utiliser un fournisseur externe pour les lectures ordinaires et une source indépendante pour les décisions critiques, à condition de ne pas introduire deux états contradictoires sans règle de résolution.

### Données publiques et données privées

Les adresses, transactions et événements publics ne doivent pas être considérés comme des secrets. Les données de profil, e-mails ou contenus sensibles devraient généralement être stockés hors chaîne si leur publication n'est pas nécessaire. Un hash sur chaîne permet de vérifier l'intégrité d'un contenu mais n'empêche pas de deviner une valeur prévisible. La conception doit traiter confidentialité, intégrité et disponibilité séparément.

## 14. Machine à états d'une transaction dans le frontend

Une transaction doit traverser plusieurs états explicites. Cette machine à états évite que l'interface affiche « succès » dès que le portefeuille retourne un hash. Les termes exacts peuvent varier selon les bibliothèques, mais les transitions et la signification utilisateur doivent être contrôlées.

~~~mermaid
stateDiagram-v2
    [*] --> Formulaire
    Formulaire --> DemandeSignature: validation locale
    DemandeSignature --> Refusee: utilisateur annule
    DemandeSignature --> Envoyee: transaction signée et soumise
    Envoyee --> EnAttente: hash reçu
    EnAttente --> Incluse: bloc observé
    Incluse --> Reussie: reçu succès
    Incluse --> Echouee: reçu revert
    Reussie --> Confirmee: confirmations ou finalité requise
    Incluse --> EnAttente: réorganisation / bloc perdu
    Refusee --> Formulaire
    Echouee --> [*]
    Confirmee --> [*]
~~~

Chaque état doit avoir une action et un message précis. Quand la signature est refusée, ne pas réessayer automatiquement. Quand la transaction est envoyée, conserver le hash et permettre de retrouver son statut après un rafraîchissement de page. Quand le reçu est un échec, afficher un échec d'exécution, pas un succès suivi d'un avertissement.

### Pseudo-code de gestion d'une transaction

~~~typescript
type TxStatus =
  | "idle"
  | "awaiting-signature"
  | "submitted"
  | "pending"
  | "included"
  | "succeeded"
  | "failed"
  | "finalized";

async function submitAction() {
  setStatus("awaiting-signature");

  try {
    const tx = await contract.writeMethod(argument);
    setTxHash(tx.hash);
    setStatus("submitted");

    const receipt = await tx.wait();
    setStatus("included");

    if (receipt.status !== "success") {
      setStatus("failed");
      return;
    }

    await refreshContractState();
    setStatus("succeeded");
  } catch (error) {
    // Distinguer refus de signature, erreur RPC et échec d'exécution.
    setStatus("failed");
    setErrorMessage(normalizeWalletError(error));
  }
}
~~~

Ce pseudo-code illustre la séquence mais ne doit pas être copié tel quel sans tenir compte de la bibliothèque choisie : le type du statut dans les reçus et la méthode \`wait\` peuvent varier. Une implémentation de production doit gérer le remplacement de transaction, le timeout, la reconnexion, les chaînes réorganisées et le statut de finalité. Elle doit aussi éviter qu'un clic répété envoie plusieurs opérations inattendues.

### Éviter les états impossibles

N'autorise pas le passage direct de « formulaire » à « finalisé ». Le frontend doit conserver le hash d'une transaction envoyée, vérifier le réseau et le compte utilisés, et traiter les cas où la page recharge alors que la transaction est toujours en attente. Un état d'interface n'est pas une source de vérité : il doit pouvoir être reconstruit depuis le portefeuille, le reçu ou le contrat.

## 15. Modèle de menace et frontières de confiance

Une revue DApp doit identifier les acteurs : utilisateur, frontend, portefeuille, RPC, indexeur, backend, contrat et opérateurs de la chaîne. Pour chacun, analyse les capacités d'un attaquant, les données contrôlées par l'acteur et les conséquences possibles.

| Composant | Risque typique | Contrôle utile |
|---|---|---|
| Frontend | Substitution de destinataire ou de fonction | Build contrôlé, adresse vérifiée, détails affichés clairement |
| Portefeuille | Mauvaise compréhension de la signature | Transactions lisibles, moindre permission, pas de phrase de récupération |
| RPC | Données retardées ou disponibilité réduite | Surveillance, comparaisons, solution de repli |
| Indexeur | Historique incohérent après réorganisation | Curseur de bloc, reprise et reconstruction |
| Contrat | Permission incorrecte ou bug logique | Tests, revue, audit proportionné |
| Stockage | Fichier supprimé ou modifié | Réplication, hash d'intégrité, stratégie de récupération |
| Backend | Réponse erronée ou censure | Source de vérité explicite, journaux et alternatives |

Une dépendance doit être testée dans son mode de panne, pas uniquement dans son fonctionnement normal. Le fallback RPC doit être vérifié pour le bon réseau et les mêmes adresses de contrat. L'indexeur doit être capable de rattraper un retard sans dupliquer les événements. Le contrat doit être testé quand un appel externe échoue ou qu'un utilisateur n'a pas la permission.

### Protection contre le phishing et les signatures de message

La DApp ne doit jamais demander à l'utilisateur sa clé privée ou sa phrase de récupération. Les signatures de message devraient utiliser un format adapté à l'authentification avec un domaine, un nonce et une expiration lorsque le protocole le prévoit. Une chaîne de texte arbitraire peut être réutilisée ou mal interprétée.

Les demandes d'approbation de jetons doivent être distinctes des signatures de connexion et des transactions de transfert. L'interface devrait annoncer ce que le contrat pourra dépenser, pendant combien de temps ou jusqu'à quelle quantité selon l'approbation. La clarté de l'écran réduit les erreurs, mais ne remplace pas la validation on-chain.

## 16. Cohérence entre indexeur et chaîne canonique

Un indexeur transforme des blocs et événements en une base adaptée aux recherches. Il doit suivre la hauteur ou le slot qu'il a traité, conserver un identifiant de bloc, et pouvoir détecter qu'un événement appartient à une branche qui n'est plus retenue. Une logique qui se contente d'ajouter tous les événements qu'elle reçoit peut produire des doublons après une reconnexion ou une réorganisation.

~~~mermaid
flowchart TD
    C["Blocs reçus"] --> V["Vérifier la continuité du parent"]
    V --> P["Traiter transactions et événements"]
    P --> DB["Écrire dans l'indexeur avec hauteur et hash"]
    DB --> H{"La tête de chaîne a-t-elle changé ?"}
    H -->|Non| N["Continuer le traitement"]
    H -->|Oui| R["Revenir au dernier ancêtre commun"]
    R --> X["Annuler/recalculer les données affectées"]
    X --> P
~~~

### Stratégie de rattrapage

L'indexeur doit enregistrer un point de contrôle fiable, puis reprendre à partir de celui-ci si le processus redémarre. Les événements devraient être dédupliqués à partir de clés déterministes comme réseau, hash de transaction et index de journal, en tenant compte du fait que la même transaction peut être réincluse dans un autre bloc. En cas de réorganisation, il faut corriger la projection et notifier les composants qui ont déjà consommé l'événement.

Pour une interface qui affiche un certificat ou un NFT, l'indexeur peut être suffisant pour parcourir des milliers d'entrées. Avant d'autoriser une opération critique, il est néanmoins prudent de vérifier l'état actuel du contrat ou de demander une preuve adaptée. L'indexeur est une amélioration de performance, pas une autorité qui peut remplacer les règles on-chain.

### Contrôler les caches

Les caches réduisent la latence et le nombre de requêtes, mais ils peuvent rendre une information périmée. Définis la durée de vie selon le type de donnée : une description statique peut être mise en cache longtemps, tandis qu'une allowance, un solde ou un statut de finalité doit être actualisé selon l'action réalisée. Les changements de compte et de réseau doivent invalider les données associées.

La cohérence d'une DApp est une propriété de bout en bout : l'interface peut être en avance ou en retard par rapport à l'indexeur, le fournisseur RPC peut suivre une tête différente et le contrat peut avoir changé d'état depuis l'ancienne lecture. Les composants doivent afficher la provenance et le statut pertinent des informations sensibles.

## 17. TP guidé A : dessiner une DApp de vote

### Objectif

Concevoir une DApp où les électeurs autorisés peuvent voter pour une proposition. Le TP est conceptuel et ne doit pas être utilisé pour une élection réelle.

### Étape 1 — Définir la logique on-chain

Le contrat doit enregistrer les propositions, vérifier l'autorisation de vote, empêcher un même compte de voter plus d'une fois et conserver le décompte. Identifie les permissions administratives et les limites de la proposition. Les règles de vérification doivent se trouver dans le contrat, pas seulement dans le frontend.

### Étape 2 — Définir le frontend

L'interface doit afficher les propositions et leurs états, demander la connexion, vérifier le bon réseau, vérifier si l'adresse est autorisée, expliquer le vote et suivre le statut de transaction. Après un vote, elle doit vérifier le reçu et actualiser l'état depuis la chaîne.

### Étape 3 — Définir les dépendances

Choisis si les propositions sont stockées intégralement sur chaîne ou si de longs descriptifs sont hébergés hors chaîne. Si un indexeur affiche les votes, explique comment il gère les réorganisations. Identifie le fournisseur RPC principal et la procédure de secours.

### Étape 4 — Tester les erreurs

Teste le portefeuille absent, le réseau incorrect, l'électeur non autorisé, un vote répété, le refus de signature, un revert et une indisponibilité du fournisseur. Le rapport doit expliquer ce que l'utilisateur voit dans chaque cas.

### Corrigé indicatif

Les règles de vote et l'unicité d'un vote doivent être appliquées on-chain. Le frontend vérifie les préconditions pour guider l'utilisateur, mais le contrat reste la source de validation. Un indexeur améliore les recherches mais peut être en retard. Les identités d'électeurs et la confidentialité du vote exigeraient un modèle de menace beaucoup plus élaboré : une adresse publique ne garantit ni anonymat ni unicité d'une personne.

## 18. TP guidé B : cartographier le parcours d'une transaction

Choisis une fonction d'écriture dans un contrat de test. Décris chaque étape de la saisie jusqu'à l'état final, avec la donnée transmise, le composant responsable, l'erreur possible et la mesure de reprise.

Le tableau doit comporter au moins huit étapes : validation de formulaire, lecture des données courantes, vérification du réseau, encodage de l'appel, demande de signature, diffusion RPC, inclusion, reçu, invalidation du cache, affichage final. Ajoute un test où l'utilisateur change de compte pendant l'opération.

**Corrigé indicatif :** l'interface valide l'expérience, mais le contrat valide les règles métier. Le portefeuille autorise la transaction avec la clé de l'utilisateur. Le RPC transmet la demande sans garantir l'inclusion. Les nœuds valident et le consensus choisit la chaîne. Le reçu donne le statut d'exécution ; une lecture actualisée confirme l'état pertinent. Chaque étape doit présenter une erreur distincte.

## 19. Changement de compte, changement de réseau et rejeu d'état

Le compte actif et le réseau sélectionné sont des données de contexte. Une DApp doit écouter les changements proposés par le portefeuille, invalider les lectures associées à l'ancien compte et charger les données du nouveau réseau. Un solde lu sur une chaîne ne doit pas être présenté comme s'il appartenait à une autre. Le même identifiant d'adresse peut avoir des contrats et des états différents selon le réseau.

~~~mermaid
flowchart TD
    A["Compte ou réseau change"] --> B["Arrêter les actions en cours si nécessaire"]
    B --> C["Invalider le cache lié à l'ancien contexte"]
    C --> D["Vérifier chain ID et compte actif"]
    D --> E["Recharger contrats, soldes et allowances"]
    E --> F["Autoriser une nouvelle transaction"]
~~~

### Contrôles avant toute écriture

Avant une transaction, vérifie le chain ID attendu, l'adresse de contrat configurée, les paramètres encodés, le compte actif et les permissions nécessaires. Si le formulaire a été rempli avant un changement de compte, demande une confirmation ou recharge les données pour éviter que l'utilisateur signe avec un contexte différent de celui qu'il croyait utiliser.

Les signatures de connexion doivent être séparées des signatures de transaction. Un mécanisme de connexion de type message signé devrait inclure un domaine, un nonce et une expiration selon le standard retenu. Sans protection contre le rejeu, une signature valide peut être réutilisée dans un autre contexte ou après la période où elle était censée servir.

### Confidentialité et journalisation

Une adresse publique n'est pas nécessairement l'identité civile d'une personne, mais elle peut être reliée à des informations identifiantes par d'autres données. Les logs de frontend, les outils d'analytique et les services de support devraient collecter le minimum nécessaire. Ne journalise jamais la phrase de récupération, une clé privée ou un secret d'API privé. Les erreurs peuvent être enregistrées sans stocker l'intégralité de données sensibles.

## 20. Indexeur : cohérence, relecture et doublons

L'indexeur facilite les recherches sur un historique volumineux, mais il maintient une projection hors chaîne. Il doit conserver un curseur de progression et des informations sur les blocs traités. En cas de réorganisation, les événements d'un bloc retiré de la chaîne canonique doivent être annulés ou recalculés. Sans cette logique, un utilisateur peut voir un transfert qui n'appartient plus à l'état actuellement suivi.

### Procédure de traitement d'événement

1. Identifier le réseau et le contrat émetteur.
2. Confirmer le hash du bloc, le parent et la position de l'événement.
3. Dédupliquer l'événement avec une clé adaptée à l'inclusion courante.
4. Mettre à jour la base et enregistrer la hauteur de traitement.
5. Après redémarrage, reprendre depuis le dernier point de contrôle.
6. Si la tête change, revenir au dernier ancêtre commun connu et rejouer la plage affectée.

~~~mermaid
sequenceDiagram
    participant N as Nœud
    participant I as Indexeur
    participant DB as Base de lecture
    N->>I: Nouveau bloc et événements
    I->>I: Vérifier parent et continuité
    I->>DB: Enregistrer événements et curseur
    N-->>I: Réorganisation possible
    I->>DB: Annuler/recalculer les données affectées
    I->>DB: Reprendre le traitement canonique
~~~

### État canonique et données de recherche

Une base d'indexation peut offrir des requêtes rapides, des filtres et des agrégations, mais elle ne devient pas la source normative du contrat. Pour une décision critique, l'application peut recouper le résultat avec un appel direct au contrat ou une preuve adaptée. Le choix de la source devrait dépendre de la criticité : une liste d'articles peut tolérer quelques secondes de retard ; une autorisation de transfert exige des données récentes et vérifiées.

### Mode dégradé

Si l'indexeur est en retard, l'interface peut afficher un avertissement et continuer à fournir les fonctions directes qui restent sûres. Si le RPC est en panne, la DApp peut basculer vers un fournisseur vérifié, mais doit confirmer que ce dernier suit le réseau attendu. L'application doit éviter d'afficher un succès sur la base d'un cache qui n'a pas été invalidé après une transaction.

## 21. Préparer un lancement sans confondre test et production

Une DApp associe des contrats, une ABI, des adresses, des dépendances frontend, des endpoints RPC et parfois une base d'indexation. Le lancement ne doit pas seulement vérifier que le site s'ouvre. Il doit vérifier que tous les composants correspondent au même environnement et que les opérations critiques donnent le résultat attendu.

### Checklist de mise en production

- Les contrats et le commit source ont été revus.
- Le code et les paramètres de compilation sont reproductibles.
- Les adresses et le chain ID ont été vérifiés par une seconde personne.
- Les tests couvrent les transactions réussies, refusées, en attente et échouées.
- Les changements de compte ou de réseau invalident bien les données périmées.
- Les états de transaction survivent à un rafraîchissement de page.
- Le frontend ne contient pas de secrets privés.
- Les autorisations de jeton sont minimales et explicites.
- Les indexeurs gèrent les doublons et les réorganisations.
- Les alertes de panne RPC et de retard d'indexation sont testées.
- Le plan de reprise a été essayé sans fonds réels.

### Retour arrière et incidents

Un rollback du frontend ne restaure pas nécessairement un contrat qui a déjà modifié l'état. Les procédures doivent distinguer le retour d'une version web, la pause ou mise à niveau d'un contrat et la reconstruction d'un indexeur. Les actions d'urgence doivent être documentées avant le lancement, surtout si des clés administratives existent.

Après une mise à jour frontend, vérifie que la nouvelle interface utilise encore l'ABI et l'adresse attendues. Après une mise à niveau de contrat, revalide l'ABI, les permissions, le stockage et les événements. La version publiée de chaque composant doit être reliée à une trace de déploiement afin de faciliter le diagnostic.

## 22. Scénarios d'interface : messages précis selon la panne

Une DApp fiable ne traite pas tous les problèmes comme « erreur de transaction ». Le portefeuille peut refuser la signature, le réseau actif peut être incorrect, le RPC peut être indisponible, le contrat peut revert ou l'indexeur peut simplement être en retard. Chaque cas demande un message, un état et une possibilité de reprise différents.

| Symptôme | Message utile | Action suivante |
|---|---|---|
| Utilisateur annule la signature | « Signature annulée, aucune transaction soumise par cette action » | Revenir au formulaire |
| Mauvais réseau | « Réseau non pris en charge pour cette action » | Demander un changement vers un réseau connu |
| RPC indisponible avant envoi | « Impossible de contacter le réseau » | Réessayer ou changer de fournisseur approuvé |
| Hash reçu, aucun reçu | « Transaction envoyée, confirmation en attente » | Continuer à suivre le hash |
| Reçu avec échec | « Transaction incluse mais exécution échouée » | Afficher le détail disponible |
| Indexeur en retard | « Historique en cours de synchronisation » | Vérifier l'état direct si nécessaire |

~~~mermaid
flowchart LR
    A["Erreur détectée"] --> B{"À quelle couche ?"}
    B --> C["Portefeuille"]
    B --> D["RPC / réseau"]
    B --> E["Contrat / exécution"]
    B --> F["Indexeur / cache"]
    C --> G["Message et reprise adaptée"]
    D --> G
    E --> G
    F --> G
~~~

### États et accessibilité

Les messages doivent être visibles sans dépendre uniquement d'une couleur ou d'une animation. Un statut de transaction doit pouvoir être lu par les technologies d'assistance, conserver le hash et expliquer la prochaine action. Les boutons devraient être désactivés lorsque le formulaire est invalide ou qu'une transaction identique est en cours, mais la logique de contrat doit toujours être considérée comme la validation finale.

Un bon test UX couvre les scénarios de réseau lent, de refus de portefeuille, de changement d'onglet et de rechargement de page. L'état du frontend devrait être reconstructible à partir du hash et du contexte réseau plutôt que perdu au premier refresh.

## 23. Étude de cas : transaction qui semble réussie mais n'a pas modifié l'état attendu

Un frontend peut afficher la confirmation d'une signature alors que le contrat a rejeté la transaction, que le reçu est en échec ou que l'indexeur n'a pas encore traité l'événement. La bonne expérience doit s'appuyer sur une suite de vérifications et présenter l'état avec précision.

~~~mermaid
flowchart TD
    A["Utilisateur signe"] --> B["Le portefeuille renvoie un hash"]
    B --> C["Attendre le reçu"]
    C --> D{"Statut d'exécution"}
    D -->|Échec| E["Afficher revert et frais possibles"]
    D -->|Succès| F["Relire l'état du contrat"]
    F --> G["Actualiser l'indexeur et l'interface"]
    G --> H["Afficher le résultat confirmé selon la politique"]
~~~

Le hash identifie une transaction, mais ne prouve pas à lui seul que le contrat a produit le résultat souhaité. Après le reçu, relis la valeur de l'état pertinente si cette information est accessible. Si le contrat émet un événement, vérifie l'adresse émettrice et les paramètres attendus. Pour les opérations critiques, tiens compte de la confirmation ou de la finalité appropriée au réseau.

### Reprise en cas d'interruption

Le frontend devrait conserver le hash et le réseau actif afin de retrouver le statut après un rechargement. Si la transaction est encore en attente, l'interface ne doit pas inviter automatiquement l'utilisateur à envoyer une seconde transaction. Si le bloc a été réorganisé, elle doit corriger le statut plutôt que conserver une réussite historique qui n'est plus dans la branche suivie.

## 24. Contrôle final d'une DApp avant la production

Le contrôle final doit inclure une répétition complète du parcours utilisateur depuis un compte neuf, sur le bon réseau, avec les contrats et les indexeurs prévus. Vérifie l'absence de secrets privés dans le bundle frontend, la qualité des messages d'erreur, le statut de la transaction, le changement de compte et les adresses de contrat.

~~~mermaid
flowchart LR
    A["Vérifier configuration"] --> B["Tester compte et réseau"]
    B --> C["Tester signature, attente et reçu"]
    C --> D["Tester erreurs et reprise"]
    D --> E["Contrôler les données on-chain et indexées"]
    E --> F["Tracer la version de production"]
~~~

Un test de fumée après déploiement peut vérifier une lecture non destructive, l'adresse du contrat, le statut de synchronisation du fournisseur et une opération de laboratoire si le réseau et les fonds de test le permettent. Ce test ne remplace pas une suite complète, mais il détecte quelques erreurs de configuration courantes.

Le déploiement doit produire un dossier vérifiable : commit source, ABI, adresse et réseau, version des dépendances, tests exécutés et date de mise en ligne. Toute mise à jour de contrat, de frontend ou de fournisseur devrait vérifier que la configuration reste cohérente.

## 25. Gérer les états asynchrones, les réorganisations et la reprise d'une DApp

Une DApp dépend de plusieurs composants qui ne progressent pas au même rythme : portefeuille, fournisseur RPC, réseau P2P, contrat, indexeur et interface. Une transaction peut être signée dans le portefeuille avant d'être diffusée, diffusée avant d'être incluse, puis incluse sans être immédiatement considérée comme finale. Une interface fiable représente explicitement ces états au lieu d'utiliser un seul indicateur de chargement.

### 25.1 Définir une machine à états de transaction

Les états doivent exprimer des faits distincts. « Préparation » signifie que l'application construit ou simule l'appel ; « attente de signature » signifie que l'utilisateur doit confirmer dans son portefeuille ; « envoyée » signifie que la soumission a retourné un hash ; « incluse » signifie qu'un reçu indique un bloc ; « confirmée » correspond à la politique métier choisie ; « finalisée » ne doit être affichée que lorsque le protocole et la logique de l'application justifient ce terme. Les états rejetés, remplacés, expirés, revertés et indéterminés doivent également être distingués.

L'absence de réponse d'un fournisseur ne prouve pas que la transaction n'a pas été diffusée. Après un timeout, une nouvelle soumission aveugle peut conduire à plusieurs transactions similaires ou à une expérience confuse. Il faut tenter de retrouver l'opération par le hash déjà connu, vérifier l'état et n'offrir une nouvelle tentative que lorsque son effet est compris. Le nonce et le mécanisme de remplacement du portefeuille sont aussi pertinents.

### 25.2 Compte, réseau et session du portefeuille

Les changements de compte et de chaîne sont des événements de sécurité et de cohérence. Lorsqu'un utilisateur change de réseau, les contrats, soldes, nonce, frais et transactions visibles peuvent changer. La DApp doit interrompre les actions qui supposent encore l'ancien contexte, recharger les données et vérifier que l'adresse du contrat est configurée pour la chaîne active. Ne te fie pas uniquement au nom de réseau choisi dans une liste déroulante.

Une session de portefeuille n'est pas toujours une identité applicative complète. Connecter un compte prouve seulement une capacité d'interaction dans le contexte de la signature acceptée ; les permissions métier peuvent nécessiter une signature spécifique, une session expirante ou une authentification supplémentaire. Les signatures de connexion doivent inclure un domaine, un objectif, un nonce et une échéance selon le protocole utilisé pour empêcher qu'une ancienne signature soit rejouée dans un autre contexte.

### 25.3 Indexation et réorganisations

L'interface lit souvent les données d'un indexeur parce que les contrats ne sont pas conçus pour répondre efficacement à toutes les requêtes historiques. L'indexeur ingère des événements et maintient des vues destinées à l'application. Ces vues peuvent être temporairement en retard ou contenir des données issues d'un bloc qui sera ensuite retiré de la chaîne canonique. Il faut documenter le délai attendu, la politique de réorganisation et la méthode de reconstruction.

Ne mélange pas silencieusement une vue d'indexeur avec une lecture directe du contrat si leurs hauteurs diffèrent. Affiche ou journalise le contexte des données critiques, utilise des identifiants idempotents et réconcilie les états lorsqu'un événement est retiré ou réémis. Après une panne d'indexeur, la procédure doit préciser le point de reprise, la façon de détecter les événements manquants et le contrôle qui confirme que la vue a rattrapé la chaîne.

### 25.4 Résilience des fournisseurs RPC

Plusieurs URL ne garantissent pas nécessairement plusieurs sources indépendantes : elles peuvent partager le même fournisseur, le même nœud en amont ou la même infrastructure cloud. Pour une application critique, mesure la latence, le taux d'erreur, le retard de tête et la cohérence des réponses. Un basculement vers un autre fournisseur doit vérifier la chaîne et comparer les hashes à la hauteur pertinente avant d'accepter des données sensibles.

Les appels de lecture peuvent souvent être répétés, mais les soumissions et opérations sensibles doivent suivre une stratégie particulière. Avant de réessayer, vérifie si le premier appel a créé un effet durable. Les services hors chaîne peuvent recevoir plusieurs fois un même événement, perdre une réponse après avoir effectué une écriture ou redémarrer au milieu d'un traitement : les gestionnaires doivent être idempotents et conserver un état de progression vérifiable.

### 25.5 Expérience d'erreur et observabilité

Les messages doivent décrire ce qui est connu, ce qui est incertain et ce que l'utilisateur peut faire. « Transaction impossible » est peu utile si le véritable problème est un mauvais réseau, une signature rejetée ou une transaction incluse puis revertée. Inversement, afficher une cause trop précise sans preuve peut tromper l'utilisateur. Les journaux techniques peuvent être plus détaillés que les messages d'interface, mais ils ne doivent pas contenir de clés privées, de secrets de session ni de données sensibles inutiles.

Surveille au minimum les taux d'échec de signature, les transactions envoyées sans reçu, les délais entre diffusion et inclusion, les reverts, les retards des indexeurs et les divergences entre fournisseurs. Associe les événements à un identifiant de corrélation et au hash de transaction lorsqu'il existe. Ces métriques permettent de voir si un incident concerne un utilisateur, une chaîne, un contrat ou toute l'infrastructure.

~~~mermaid
stateDiagram-v2
    [*] --> Preparation
    Preparation --> AttenteSignature
    AttenteSignature --> Rejetee: utilisateur refuse
    AttenteSignature --> Envoyee: signature et soumission
    Envoyee --> Inconnue: timeout RPC
    Inconnue --> Envoyee: hash retrouvé
    Inconnue --> Incluse: reçu retrouvé
    Envoyee --> Incluse: reçu observé
    Incluse --> Revert: statut échec
    Incluse --> Confirmation: politique satisfaite
    Confirmation --> Finalisee: finalité vérifiée
    Incluse --> Reorganisation: bloc retiré
    Reorganisation --> Envoyee: rechercher transaction
    Revert --> [*]
    Rejetee --> [*]
    Finalisee --> [*]
~~~

### 25.6 Exercice de reprise contrôlée

Simule un retard RPC dans un environnement de test, puis déconnecte temporairement l'indexeur. Vérifie que la DApp n'annonce pas à tort un échec définitif quand une soumission a peut-être réussi, qu'elle continue de distinguer les états provisoires et qu'elle ne crédite pas deux fois le même événement lors de la reprise. Restaure les services, compare leurs hauteurs, réconcilie l'état et documente les limites de la simulation.

Le compte rendu indique le symptôme, l'impact visible, les horodatages, la chaîne active, le hash de transaction, les réponses des fournisseurs, les actions automatiques et le critère de retour à la normale. L'objectif est d'obtenir une application explicable pendant une panne, pas une interface qui masque l'incertitude derrière une animation de chargement.

## 26. Dix questions d'entraînement avec corrigé

### Question 1
Une DApp est-elle entièrement décentralisée parce qu'elle utilise un contrat ?

**Corrigé :** Non. L'interface, le RPC, l'indexeur, le stockage et l'authentification peuvent rester centralisés. Il faut analyser chaque composant et ses dépendances.

### Question 2
À quoi sert le portefeuille ?

**Corrigé :** Il gère les clés et autorise les transactions ou signatures. La DApp ne doit jamais demander la clé privée ou la phrase de récupération.

### Question 3
Que garantit un hash de transaction retourné par RPC ?

**Corrigé :** Il permet d'identifier la transaction soumise dans le contexte prévu, mais ne garantit pas à lui seul l'inclusion, le succès d'exécution ou la finalité.

### Question 4
Pourquoi vérifier le chain ID ?

**Corrigé :** Pour s'assurer que l'application interagit avec le réseau attendu et éviter d'envoyer des transactions à un environnement incorrect.

### Question 5
Pourquoi ne pas faire confiance uniquement à un indexeur ?

**Corrigé :** Il peut être en retard, mal configuré ou mal traiter des réorganisations. Il représente une projection de la chaîne et doit être vérifié pour les opérations critiques.

### Question 6
Quelle est la différence entre une lecture et une écriture ?

**Corrigé :** La lecture interroge un état sans transaction persistante dans le cas habituel. L'écriture nécessite une transaction signée et incluse pour modifier durablement l'état.

### Question 7
Pourquoi une approbation de jeton présente-t-elle un risque ?

**Corrigé :** Elle peut autoriser un contrat à dépenser les jetons d'un utilisateur selon la portée de l'approbation. Il faut limiter et comprendre les permissions accordées.

### Question 8
Que doit faire l'interface après un revert ?

**Corrigé :** Afficher un échec d'exécution, expliquer les informations disponibles et ne pas annoncer que l'action métier a réussi. Le reçu et les données d'erreur doivent être examinés.

### Question 9
IPFS garantit-il que le fichier reste disponible ?

**Corrigé :** Non. L'adressage par contenu aide à vérifier l'intégrité, mais il faut des nœuds ou services qui conservent et servent les données.

### Question 10
Pourquoi gérer les changements de compte et de réseau ?

**Corrigé :** Ils modifient l'identité active, l'état, les contrats disponibles et la signification des transactions. L'application doit invalider les données et revalider le contexte.

## 27. Challenge final : plan de résilience d'une DApp

### Scénario

Tu dois préparer la mise en production d'une DApp de gestion de certificats. Le contrat enregistre un identifiant et une empreinte, l'interface permet de rechercher un certificat, et un indexeur fournit l'historique. Le frontend est hébergé sur une plateforme web et utilise un fournisseur RPC externe.

### Travail demandé

Rédige un plan de 500 à 700 mots qui identifie les composants, leurs responsabilités, leurs hypothèses de confiance, les pannes possibles et les mesures de reprise. Précise quelles données sont on-chain et lesquelles sont hors chaîne. Définis les vérifications effectuées avant la publication d'un certificat et les messages affichés lors d'une transaction en attente ou en échec.

### Correction proposée

Le contrat constitue la source de validation on-chain pour l'enregistrement de l'identifiant et de l'empreinte. Il doit vérifier les permissions, la validité de l'identifiant, les doublons et les règles de mise à jour. Le frontend aide l'utilisateur, mais ne doit pas être la seule couche qui vérifie une permission. Le fournisseur RPC sert les requêtes et transmet les transactions, mais peut être indisponible ou renvoyer un état retardé. L'indexeur facilite la recherche et les historiques, mais doit suivre la chaîne, corriger les réorganisations et pouvoir être reconstruit.

Le fichier ou document du certificat peut rester hors chaîne, tandis que son empreinte est conservée on-chain. Cette architecture vérifie que le document présenté correspond à l'engagement, mais ne garantit ni sa disponibilité ni la vérité du contenu. Le service de stockage doit prévoir des sauvegardes, une politique de conservation, des contrôles d'accès et une procédure de récupération. Les données personnelles ne doivent pas être publiées sur chaîne sans analyse de leur nécessité et des obligations applicables.

Avant production, l'équipe vérifie le bytecode et les adresses des contrats, les permissions, la version et la configuration du frontend, l'ABI, le chain ID, les tests d'intégration et les limites d'accès aux services. Les scénarios de test comprennent refus de signature, réseau incorrect, contrat inexistant à l'adresse configurée, échec d'exécution, retard de l'indexeur et panne RPC. Pour les transactions importantes, une seconde source d'observation peut être utilisée, à condition qu'elle soit réellement indépendante.

L'interface annonce séparément la transaction préparée, signée, envoyée, incluse, réussie ou échouée, puis confirmée selon les garanties du réseau. En cas de panne RPC, elle explique que l'opération n'a pas pu être suivie et évite de faire croire que le certificat est enregistré. La reprise peut basculer vers un fournisseur autorisé et fiable, tandis que les données d'indexation sont rattrapées depuis le dernier point vérifié. Les journaux doivent conserver les hashes, blocs, heures et codes d'erreur sans stocker de secrets.

Ce plan traite la DApp comme un système à plusieurs composants. Le contrat est essentiel, mais la sécurité et la disponibilité de l'expérience dépendent aussi de l'interface, des fournisseurs, de l'indexeur, du stockage et des procédures d'exploitation.

## Glossaire

**ABI :** description permettant d'encoder les appels et décoder les résultats des contrats.

**Chain ID :** identifiant utilisé pour distinguer un réseau dans les contextes de transaction et de configuration.

**DApp :** application dont une partie importante de la logique ou de l'état s'appuie sur un réseau décentralisé, souvent via des smart contracts.

**Frontend :** interface utilisateur de l'application.

**Indexeur :** service qui transforme les données de la blockchain en vues de lecture et recherches plus pratiques.

**Portefeuille :** logiciel ou dispositif qui gère les clés et autorise les transactions et signatures.

**RPC :** interface d'appels à distance pour interroger un nœud ou soumettre des transactions.

**Reçu :** résultat d'une transaction incluse qui indique notamment son statut d'exécution.

**Réorganisation :** changement de branche suivie qui peut modifier le statut de blocs récents.

**Source canonique :** état accepté selon les règles du réseau, par opposition à une projection ou cache hors chaîne.

## Pour aller plus loin

- Introduction technique officielle aux DApps : https://ethereum.org/developers/docs/dapps/
- Documentation Ethereum sur les nœuds et clients : https://ethereum.org/developers/docs/nodes-and-clients/
- Documentation Ethereum sur les API JSON-RPC : https://ethereum.org/developers/docs/apis/json-rpc/
- Documentation Ethereum sur les transactions : https://ethereum.org/developers/docs/transactions/
- Documentation de sécurité OWASP : https://cheatsheetseries.owasp.org/

Une DApp doit être conçue et testée comme un système complet, pas comme une page web reliée à une adresse de contrat. Toute opération qui touche à des actifs ou à des données importantes exige une vérification du contexte réseau, des permissions et du statut final des transactions.
