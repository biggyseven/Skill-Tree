# Réseau P2P et nœuds

## Encadré de mise en contexte

Une blockchain ne fonctionne pas comme un site web classique où tous les utilisateurs consultent nécessairement le même serveur central. Dans un réseau pair-à-pair (P2P), des ordinateurs appelés nœuds échangent des informations directement avec leurs pairs. Les nœuds reçoivent des transactions et des blocs, vérifient les données selon le protocole, puis les relaient s'ils remplissent les conditions requises. Chaque nœud conserve une vue locale du réseau et peut observer les messages à des moments différents.

Le P2P est essentiel à la résistance aux pannes et à l'ouverture d'une blockchain publique, mais il ne garantit pas automatiquement la décentralisation. Si les participants dépendent de quelques fournisseurs d'accès, de quelques services RPC ou de quelques centres de données, l'architecture peut être plus centralisée en pratique qu'elle ne le semble sur un schéma. De même, un nœud ne participe pas nécessairement à tous les rôles du réseau : certains vérifient complètement les données, d'autres allègent leur stockage, d'autres proposent des blocs ou servent des requêtes aux applications.

Cette leçon explique le réseau P2P, les rôles des nœuds, la découverte des pairs, la propagation des transactions et des blocs, les problèmes de connectivité, les risques de sécurité et les outils de diagnostic. Elle prépare également à comprendre les contrats intelligents : une application blockchain dépend souvent de plusieurs couches, du portefeuille au fournisseur RPC, en passant par les nœuds et le réseau de consensus.

## Objectifs d'apprentissage

À la fin de la leçon, tu sauras :

- expliquer la différence entre un réseau client-serveur et un réseau pair-à-pair ;
- décrire le rôle d'un nœud et distinguer nœud complet, nœud d'archive, validateur, mineur et fournisseur RPC ;
- expliquer comment les pairs sont découverts et les connexions établies ;
- suivre le trajet d'une transaction et d'un bloc à travers le réseau ;
- comprendre les mempools, les relais et les différences de politique entre les nœuds ;
- identifier les effets de la latence, de la perte de paquets, de la partition réseau et de la censure ;
- expliquer pourquoi plus de nœuds ne garantit pas toujours plus de décentralisation ;
- appliquer une méthode de diagnostic sur une panne de synchronisation ;
- analyser les dépendances réseau d'une application blockchain.

## 1. Client-serveur et pair-à-pair

Dans un modèle client-serveur traditionnel, un client envoie une requête à un serveur central ou à un ensemble coordonné de serveurs. Le serveur traite la requête et renvoie une réponse. Cette architecture convient à de nombreux services : boutique en ligne, application bancaire, site de documentation ou plateforme pédagogique. Elle est souvent plus simple à administrer et peut offrir de bonnes performances.

Dans un modèle pair-à-pair, les participants échangent des données entre eux et peuvent remplir des fonctions similaires. Il n'existe pas nécessairement un unique serveur dont dépend tout le réseau. Les participants peuvent relayer des messages, partager les blocs et aider les nouveaux nœuds à rejoindre le système. Certaines applications P2P restent hybrides et utilisent des services centralisés pour la découverte, la coordination ou l'interface utilisateur.

~~~mermaid
flowchart TD
    subgraph CS["Modèle client-serveur"]
        C1["Client A"] --> S["Serveur central"]
        C2["Client B"] --> S
        C3["Client C"] --> S
    end
    subgraph PP["Modèle pair-à-pair"]
        P1["Pair A"] <--> P2["Pair B"]
        P2 <--> P3["Pair C"]
        P1 <--> P4["Pair D"]
        P3 <--> P4
    end
~~~

Une blockchain publique peut combiner plusieurs modèles. Les nœuds P2P se relaient des données, mais les portefeuilles mobiles peuvent interroger un fournisseur RPC centralisé. Un explorateur de blocs peut indexer les données sur ses propres serveurs. Un site DApp peut être livré par une infrastructure web classique même si ses contrats sont déployés sur une chaîne publique.

La bonne question n'est donc pas seulement « la blockchain est-elle décentralisée ? », mais « quelles parties de l'usage dépendent de quelles entités et quelles alternatives sont disponibles ? ».

## 2. Qu'est-ce qu'un nœud ?

Un nœud est un logiciel qui participe au réseau et applique un ensemble de fonctions définies par son implémentation et sa configuration. Selon le protocole, il peut recevoir des données, vérifier des blocs, conserver l'historique, fournir des réponses à des applications ou participer directement au consensus. Tous les nœuds ne remplissent pas nécessairement les mêmes rôles.

### 2.1 Nœud complet

Un nœud complet vérifie les règles du protocole en utilisant les données nécessaires à la validation. Il ne se contente pas de faire confiance à la réponse d'un autre serveur pour chaque affirmation importante sur la chaîne. Dans Bitcoin, un nœud complet peut valider les blocs et maintenir l'ensemble des UTXO actuellement dépensables. Dans Ethereum, un nœud usuel combine un client d'exécution et un client de consensus pour suivre la chaîne avec les fonctions correspondant au rôle choisi.

La validation indépendante aide l'utilisateur à réduire sa dépendance à un fournisseur unique. Elle demande cependant des ressources : processeur, mémoire, stockage, bande passante, temps d'initialisation et maintenance. Les exigences varient avec le protocole et sa configuration.

### 2.2 Nœud d'archive

Un nœud d'archive conserve des données historiques supplémentaires qui ne sont pas nécessaires au fonctionnement courant d'un nœud complet dans sa configuration standard. Dans Ethereum, cela peut inclure des états historiques permettant de répondre à des requêtes sur des états anciens. Le coût de stockage et les besoins opérationnels peuvent être sensiblement plus élevés.

Le terme « archive » ne signifie pas automatiquement que le nœud détient toutes les données imaginables ou qu'il est le seul à pouvoir prouver la validité. Il décrit un profil de données et de requêtes. La manière de conserver l'historique dépend des clients et des évolutions du protocole.

### 2.3 Nœud léger

Un client léger cherche à vérifier certaines informations en téléchargeant moins de données que le nœud complet. Il peut s'appuyer sur des en-têtes, des preuves cryptographiques ou des mécanismes de confiance limités pour vérifier des affirmations. Il est pratique pour les appareils disposant de ressources modestes, mais les garanties dépendent du protocole, du client et de la preuve réellement vérifiée.

« Léger » ne signifie pas « incapable de vérifier quoi que ce soit », mais il ne signifie pas non plus « identique à un nœud complet ». Il faut savoir quelles données sont vérifiées localement et quelles réponses dépendent d'autres participants.

### 2.4 Mineur et validateur

Un mineur participe à la production de blocs dans un réseau de preuve de travail. Un validateur participe aux fonctions de consensus dans un réseau de preuve d'enjeu. Ces rôles peuvent nécessiter des nœuds particuliers, des clés dédiées et des exigences de disponibilité. Un ordinateur qui exécute simplement un nœud complet n'est pas automatiquement un mineur ou un validateur.

Le protocole sépare la validation des règles de la production de blocs. Un nœud peut rejeter un bloc invalide même s'il a été produit par un mineur très puissant ou un validateur ayant une mise importante.

### 2.5 Fournisseur RPC

Les applications utilisent souvent une interface de type RPC pour interroger le réseau ou soumettre une transaction. RPC signifie appel de procédure à distance : le logiciel envoie une requête structurée à un service qui répond par des données ou un résultat. Un fournisseur RPC peut servir un grand nombre d'applications, héberger des nœuds et gérer une couche d'API.

RPC n'est pas synonyme de blockchain ni de consensus. Si une DApp ne peut plus joindre son fournisseur RPC, cela ne prouve pas que la blockchain est en panne. L'application peut essayer un autre fournisseur ou un nœud exploité par l'utilisateur. En revanche, si toutes les interfaces utilisées dépendent du même fournisseur, une panne de celui-ci devient un point de défaillance majeur de l'expérience.

## 3. La topologie du réseau et les pairs

Un pair est un participant auquel un nœud est connecté et avec lequel il peut échanger des messages. Un nœud ne se connecte pas nécessairement à tous les nœuds du réseau : cela serait coûteux et peu efficace quand le réseau grandit. Il maintient plutôt un nombre limité de connexions et utilise celles-ci pour découvrir d'autres pairs ou relayer des données.

Une topologie P2P peut changer au cours du temps. Des nœuds apparaissent et disparaissent, changent d'adresse, redémarrent ou sont séparés du réseau. Le logiciel doit trouver des pairs utilisables et éviter de dépendre d'une seule connexion. Plusieurs connexions indépendantes peuvent réduire certains risques, sans les supprimer.

~~~mermaid
flowchart LR
    A["Nœud local"] --- B["Pair 1"]
    A --- C["Pair 2"]
    A --- D["Pair 3"]
    B --- E["Autre pair"]
    C --- F["Autre pair"]
    D --- E
    E --- F
~~~

### 3.1 Découverte des pairs

Les mécanismes de découverte dépendent du réseau et du client. Ils peuvent inclure des adresses de pairs connues, des nœuds d'amorçage, des bases locales apprises lors de sessions précédentes, des protocoles de découverte ou des adresses fournies par des opérateurs. Certains clients doivent traverser des routeurs ou des pare-feu qui compliquent les connexions entrantes.

Les nœuds d'amorçage facilitent la découverte initiale, mais ne sont pas nécessairement des serveurs centraux qui contrôlent toutes les transactions. Un système bien conçu dispose d'autres moyens d'apprendre des pairs et de se reconnecter. Toutefois, une dépendance trop forte à quelques points de découverte peut rendre l'entrée dans le réseau plus fragile ou faciliter certaines tentatives d'isolement.

### 3.2 Connexions entrantes et sortantes

Une connexion sortante est initiée par le nœud local vers un pair distant. Une connexion entrante est initiée par un autre participant vers le nœud local, lorsque la configuration et le réseau le permettent. Les routeurs NAT et les pare-feu peuvent empêcher les connexions entrantes sans configuration spécifique.

Un nœud qui n'accepte pas de connexion entrante peut tout de même participer au réseau par ses connexions sortantes. Mais, dans certains modèles, accepter des connexions entrantes améliore la capacité d'autres pairs à découvrir et à utiliser ce nœud. La disponibilité doit être évaluée en tenant compte du rôle de la machine, du réseau et de la politique de sécurité.

### 3.3 Résilience et diversité des pairs

Le nombre de connexions n'est pas la seule mesure utile. Si dix connexions mènent toutes au même fournisseur, au même hébergeur ou au même réseau autonome, leur diversité est limitée. Une panne ou une politique de censure commune peut affecter toutes ces connexions.

La diversité se mesure en pratique selon plusieurs dimensions : fournisseurs d'accès, zones géographiques, hébergeurs, implémentations clientes, versions, opérateurs et chemins réseau. Il faut cependant éviter de créer des connexions excessives ou d'ouvrir des ports sans raison ; la sécurité et les limites de ressources restent importantes.

## 4. Comment une transaction circule

Lorsqu'un utilisateur crée une transaction, son portefeuille construit une représentation conforme au protocole et la signe avec le moyen d'autorisation approprié. Il transmet ensuite la transaction à un nœud, souvent par RPC ou par une connexion P2P. Le nœud vérifie plusieurs conditions avant de la relayer ou de la conserver comme transaction en attente.

~~~mermaid
sequenceDiagram
    participant W as Portefeuille
    participant A as Nœud A
    participant B as Nœud B
    participant C as Nœud C
    participant P as Producteur de bloc
    W->>A: Transaction signée
    A->>A: Vérification initiale
    A->>B: Relais à un pair
    B->>C: Relais à un autre pair
    C->>P: Transaction disponible
    P->>P: Sélection selon ses règles
    P-->>A: Bloc avec transaction
~~~

### 4.1 Mempool ou ensemble des transactions en attente

Dans Bitcoin, le terme mempool désigne l'ensemble local des transactions valides selon les contrôles et politiques d'un nœud qui n'ont pas encore été confirmées dans la chaîne suivie. Il n'existe pas un mempool universel identique chez tous les participants. Deux nœuds peuvent avoir reçu des transactions différentes, appliquer des politiques de relais différentes ou avoir des ressources disponibles différentes.

Dans Ethereum, les clients conservent également des transactions en attente, mais les détails et les politiques varient selon les clients et leur mode d'exploitation. Des transactions qui utilisent le même nonce peuvent être en concurrence ou se remplacer selon les règles et politiques. Le vocabulaire et les détails internes doivent être adaptés au protocole au lieu de supposer que toutes les chaînes ont la même structure.

### 4.2 Relais et politiques locales

Un nœud peut refuser de relayer une transaction qui pourrait être valide dans certaines conditions de consensus, parce qu'elle ne respecte pas ses politiques locales de relais, de frais ou de ressources. Cette distinction est importante : les règles de consensus déterminent ce qui est acceptable dans un bloc final, alors que les politiques de relais déterminent ce que le nœud accepte de propager avant l'inclusion.

Les politiques locales servent notamment à limiter le spam, la consommation de ressources et les transactions que le nœud ne veut pas conserver. Elles peuvent différer entre versions et opérateurs. Le fait qu'une transaction ne soit pas visible dans l'interface d'un nœud ne permet donc pas de conclure qu'elle est invalide pour tous les nœuds.

### 4.3 Censure et transaction qui n'arrive pas

Une transaction peut ne pas parvenir à un producteur de bloc parce que le nœud auquel elle a été envoyée ne l'a pas relayée, qu'une connexion est cassée, qu'un fournisseur RPC l'a rejetée, que les frais sont insuffisants selon les politiques courantes ou que les producteurs l'ont omise. Le diagnostic doit suivre la transaction étape par étape : est-elle bien signée ? a-t-elle été acceptée par le premier nœud ? est-elle visible auprès de plusieurs nœuds indépendants ? est-elle admissible et compétitive pour l'inclusion ?

La censure peut être un comportement intentionnel, mais tous les retards ou rejets ne sont pas de la censure. Les frais, le format, les dépendances, les ressources et les pannes ordinaires peuvent expliquer une absence d'inclusion. Une conclusion de censure exige un ensemble de preuves et une définition claire de l'acteur censurant.

## 5. Comment un bloc circule

Un producteur propose un bloc et le diffuse à ses pairs. Les nœuds qui le reçoivent le vérifient selon leurs règles et, s'il est valide et pertinent pour leur chaîne suivie, peuvent le relayer. Les mécanismes de propagation cherchent à limiter la quantité de données retransmises inutilement et à réduire le délai pendant lequel le réseau dispose de vues différentes.

~~~mermaid
flowchart TD
    P["Producteur propose un bloc"] --> A["Premier groupe de pairs"]
    A --> B["Nœuds vérifient le bloc"]
    B --> C["Relais vers d'autres pairs"]
    C --> D["Le réseau apprend le bloc"]
    D --> E["Les nœuds appliquent les règles de sélection"]
    E --> F["La vue locale de la chaîne converge"]
~~~

Si un bloc arrive avant son parent, le nœud peut le conserver comme bloc dont la dépendance manque, ou demander les données manquantes. Si le bloc est incomplet, mal formé ou invalide, le comportement exact dépend du client et du contexte, mais il ne doit pas être accepté comme bloc valide. Si deux blocs valides sont concurrents, la règle de consensus détermine la branche suivie.

### 5.1 Pourquoi la propagation rapide compte

Si la plupart des nœuds apprennent rapidement le nouveau bloc, ils ont moins de temps pour construire des branches concurrentes à partir de l'ancien parent. Dans les réseaux PoW, une propagation lente peut accroître le nombre de blocs concurrents et affecter l'efficacité des mineurs. Dans les réseaux PoS, la disponibilité et la latence des messages peuvent affecter la participation des validateurs, les attestations et parfois la progression vers la finalité.

La rapidité ne doit pas être obtenue au prix d'une validation aveugle. Les nœuds peuvent utiliser des optimisations de propagation, mais la validité des données reste essentielle. Les mécanismes de compression ou de transmission partielle doivent être utilisés selon les règles du protocole et les implémentations conformes.

## 6. Synchronisation d'un nouveau nœud

Un nouveau nœud doit apprendre suffisamment de données pour suivre l'historique et appliquer les règles de la chaîne. Le processus peut être long et gourmand en stockage. Les méthodes d'initialisation varient : certains nœuds vérifient l'historique depuis le point de départ, d'autres utilisent des méthodes de synchronisation accélérée ou des instantanés qui sont ensuite vérifiés selon les garanties disponibles.

Un instantané est un point de départ pratique, mais il ne faut pas confondre sa réception avec une validation indépendante complète. L'opérateur doit comprendre ce qui a été vérifié localement et ce qui dépend de la source de l'instantané. Pour un environnement qui exige un niveau élevé de confiance, la procédure d'initialisation et la vérification des données doivent être documentées.

~~~mermaid
flowchart TD
    A["Installer le client"] --> B["Charger la configuration réseau"]
    B --> C["Découvrir les pairs"]
    C --> D["Échanger des informations sur les blocs"]
    D --> E["Télécharger les données nécessaires"]
    E --> F["Vérifier les blocs et transitions"]
    F --> G["Atteindre la tête de chaîne suivie"]
    G --> H["Surveiller la synchronisation en continu"]
~~~

### 6.1 Stockage, élagage et archive

Un nœud élagué peut supprimer certaines données historiques complètes qu'il n'a plus besoin de conserver pour son fonctionnement courant, tout en maintenant suffisamment d'état et de données pour continuer à valider et servir certaines requêtes. Un nœud d'archive vise au contraire à conserver des données historiques plus riches. Les termes exacts et les fonctions dépendent du protocole.

L'élagage peut réduire les besoins de disque, mais il peut limiter les requêtes historiques qu'un opérateur peut servir. Une entreprise qui souhaite analyser des transactions anciennes ou reconstruire des états doit choisir le profil adapté. Le plus petit stockage n'est pas toujours le meilleur choix ; il doit correspondre à l'objectif de l'application.

## 7. Protocoles réseau, versions et compatibilité

Les clients doivent convenir de formats de messages, de règles de découverte, de procédures de négociation et de versions de protocole. Une incompatibilité peut empêcher un nœud de se connecter ou de comprendre certaines données. Une version ancienne peut être incapable de suivre un réseau après une mise à niveau majeure ; une version défectueuse peut au contraire accepter ou rejeter incorrectement des objets.

Les opérateurs devraient suivre les annonces officielles des clients et les fenêtres de mise à niveau, tester les changements et maintenir une procédure de retour à un état opérationnel sûr. Dans les réseaux à consensus, la mise à jour du logiciel est un sujet de sécurité : exécuter des versions incompatibles peut contribuer à une divergence ou à une perte de service.

Les ports, les API et les interfaces d'administration doivent être exposés selon le principe du moindre privilège. Un port P2P accessible au public ne devrait pas donner accès à une API administrative non protégée. Il faut séparer, lorsque c'est possible, les interfaces publiques de communication avec les pairs et les interfaces de contrôle utilisées par les opérateurs ou applications.

## 8. Menaces réseau

### 8.1 Nœuds Sybil

Une attaque Sybil consiste à créer ou contrôler de nombreuses identités apparentes afin d'influencer la perception d'un participant. Dans un réseau ouvert, une identité de pair ne correspond pas nécessairement à une personne ou à un opérateur indépendant. Afficher « mille pairs connectés » n'est donc pas automatiquement la preuve de mille acteurs indépendants.

Les protocoles utilisent diverses méthodes pour limiter l'impact de telles attaques ou maintenir leurs garanties malgré un ensemble de pairs non fiables. L'opérateur doit comprendre comment son client choisit ses pairs, s'il peut utiliser des connexions diversifiées et quelles informations il vérifie par cryptographie plutôt que d'accepter le nombre de pairs comme mesure de confiance.

### 8.2 Attaque d'éclipse

Une attaque d'éclipse cherche à isoler un nœud de ses pairs honnêtes en contrôlant ou influençant les connexions qu'il utilise. Le nœud peut alors observer un sous-ensemble manipulé du réseau et recevoir des informations incomplètes ou retardées. Selon le protocole et le contexte, cela peut affecter la disponibilité, la perception de la chaîne ou certaines décisions applicatives.

La défense dépend du client et du modèle de menace : diversité des pairs, bonnes pratiques de réseau, gestion des adresses, connexions sortantes multiples, surveillance des changements anormaux et comparaison avec des sources indépendantes. Aucun conseil générique ne remplace l'analyse des protections réellement mises en œuvre par le client.

### 8.3 Déni de service et spam

Un attaquant peut envoyer de nombreuses requêtes ou messages afin de consommer le processeur, la mémoire, le disque ou la bande passante d'un nœud. Les limites de ressources, les mécanismes de priorité, les politiques de relais et la surveillance servent à réduire ces risques. Mais une limitation trop stricte peut aussi empêcher le service légitime d'une application.

Il faut distinguer un problème de charge, une panne matérielle, une attaque volontaire et un comportement normal lors d'une forte activité. Les métriques — latence, débit réseau, taille des files d'attente, consommation mémoire, erreurs de protocole et temps de synchronisation — aident à prendre une décision fondée sur des faits.

### 8.4 Censure par l'infrastructure

Même si les règles de consensus sont ouvertes, les fournisseurs d'accès, les hébergeurs, les points RPC, les indexeurs, les portefeuilles et les interfaces web peuvent filtrer ou bloquer des demandes. Une DApp peut être inaccessible parce que son nom de domaine a expiré, son fournisseur RPC est indisponible ou son interface est hébergée sur un service centralisé.

Il faut donc cartographier les dépendances. L'accès au consensus, la diffusion des transactions, l'interface de l'utilisateur et l'indexation sont des couches différentes. Une stratégie de résilience peut prévoir plusieurs fournisseurs, un nœud personnel, des interfaces alternatives ou une procédure de consultation directe, mais chaque alternative doit être configurée et testée.

## 9. Sécurité opérationnelle d'un nœud

Un nœud est un service réseau exposé à des données non fiables. Il doit être maintenu comme tout autre système important : mises à jour, surveillance, contrôle des accès, sauvegarde des configurations, sécurité du système d'exploitation, gestion des disques et procédures d'incident.

Les clés de consensus ou de production de blocs doivent être séparées des données et services ordinaires lorsque l'architecture le permet. Un nœud complet utilisé pour vérifier les données n'a pas besoin de détenir automatiquement des clés de validateur. La séparation réduit les conséquences d'une compromission d'un composant web ou d'un poste utilisateur.

Les journaux doivent être suffisants pour le diagnostic, mais leur conservation doit respecter les exigences de confidentialité et de sécurité. Une API d'administration accessible publiquement peut être plus dangereuse qu'un port P2P. Il faut contrôler qui peut envoyer des transactions, accéder aux métriques sensibles, déclencher des opérations ou modifier la configuration.

### 9.1 Surveillance minimale

Une supervision opérationnelle peut suivre :

- le nombre de pairs connectés et leur stabilité ;
- l'état de synchronisation et l'écart avec la tête de chaîne connue ;
- la hauteur ou le slot observé ;
- les erreurs de validation et les déconnexions ;
- le temps CPU, la mémoire, le stockage et la bande passante ;
- les files d'attente de transactions et les retards de propagation ;
- la version du client et l'état des mises à niveau.

Ces métriques doivent être interprétées ensemble. Un nœud peut être connecté à de nombreux pairs mais rester bloqué sur un état ancien. Un processus peut être vivant tout en étant incapable de synchroniser correctement. Un seul indicateur vert ne constitue pas une preuve de santé.

## 10. Étude de cas : une DApp inaccessible

Un utilisateur ouvre une DApp et voit le message « réseau indisponible ». Le site web se charge normalement, mais les soldes n'apparaissent pas et les transactions ne sont pas soumises. Il est tentant de conclure immédiatement que la blockchain s'est arrêtée.

Un diagnostic utile suit les couches :

1. Le site web et ses scripts sont-ils accessibles ?
2. Le portefeuille est-il connecté au bon réseau ?
3. Le fournisseur RPC répond-il aux requêtes simples ?
4. Le point RPC est-il synchronisé ou renvoie-t-il des données périmées ?
5. La transaction est-elle construite avec le bon identifiant de réseau et les bons paramètres ?
6. Le nœud accepte-t-il la transaction, et donne-t-il un identifiant de transaction ?
7. L'identifiant est-il visible via une seconde source indépendante ?
8. La chaîne produit-elle de nouveaux blocs et le consensus progresse-t-il ?

Si le fournisseur RPC principal ne répond plus mais qu'un autre service fonctionne, le problème est probablement au niveau du fournisseur ou du chemin réseau, pas nécessairement au niveau du consensus. Si les nœuds indépendants cessent de progresser ou rapportent des erreurs de consensus, l'enquête doit être élargie. Le vocabulaire précis évite les fausses alertes et accélère la résolution.

## 11. TP guidé A : mesurer la connectivité sans altérer le réseau

### Objectif

Apprendre à distinguer un problème de connectivité d'un problème de consensus. Le TP utilise des commandes de diagnostic ordinaires et ne requiert pas l'installation d'un nœud.

### Étape 1 — Vérifier la connectivité de base

Sous Windows PowerShell, teste la résolution DNS du fournisseur ou du serveur de laboratoire choisi :

~~~powershell
Resolve-DnsName example.com
~~~

Remplace le nom par celui de l'hôte que tu es autorisé à diagnostiquer. Le résultat vérifie la résolution DNS, pas l'état de la blockchain.

### Étape 2 — Tester une connexion TCP

Utilise Test-NetConnection vers un hôte et un port que tu es autorisé à tester :

~~~powershell
Test-NetConnection example.com -Port 443
~~~

Un échec peut indiquer un problème de DNS, de routage, de pare-feu, de port ou de service. Il ne prouve pas à lui seul qu'un réseau blockchain a cessé de fonctionner.

### Étape 3 — Comparer deux fournisseurs indépendants

Si tu disposes de deux endpoints de lecture autorisés pour un réseau de test, interroge-les pour obtenir une information simple comme la hauteur de bloc. Compare les résultats et l'heure de la requête. Ne place jamais un secret d'API dans un dépôt public et n'exécute pas de transaction sur le réseau principal dans le cadre de ce TP.

### Étape 4 — Rédiger le diagnostic

Note l'adresse de l'hôte, le type de requête, le résultat, l'heure, l'état DNS/TCP et les écarts observés entre fournisseurs. Conclus en séparant les faits confirmés et les hypothèses. Le rapport ne doit pas déclarer une panne du consensus sur la seule base d'un endpoint qui ne répond pas.

## 12. TP guidé B : cartographier les dépendances d'une DApp

Dessine les composants suivants : navigateur, portefeuille, interface web, fournisseur RPC, nœud complet, réseau P2P, consensus, contrat intelligent et indexeur. Connecte-les selon le parcours d'une lecture et d'une transaction.

~~~mermaid
flowchart TD
    U["Navigateur et utilisateur"] --> UI["Interface de la DApp"]
    U --> W["Portefeuille"]
    UI --> RPC["Fournisseur RPC"]
    W --> RPC
    RPC --> N["Nœud blockchain"]
    N --> P2P["Réseau P2P"]
    P2P --> CONS["Consensus et blocs"]
    CONS --> SC["Contrat intelligent exécuté"]
    N --> IDX["Indexeur / API analytique"]
    IDX --> UI
~~~

### Travail demandé

Pour chaque connexion, précise si elle dépend d'un fournisseur centralisé, d'une connexion P2P, d'un secret ou d'une preuve cryptographique. Ensuite, simule trois pannes : interface web indisponible, fournisseur RPC indisponible et retard de consensus. Pour chacune, identifie ce qui continue à fonctionner et les solutions de reprise possibles.

**Corrigé indicatif :** l'interface peut être hébergée de façon centralisée alors que le contrat est sur une chaîne publique. Le portefeuille signe localement, mais peut dépendre d'un RPC pour diffuser la transaction. Un nœud personnel ou un fournisseur alternatif peut réduire la dépendance RPC. La panne de l'interface peut être contournée uniquement si une interface fiable alternative est disponible ; la transaction ne doit pas être signée à l'aveugle. Un retard de consensus affecte la confirmation et la finalité même si le site et le RPC restent accessibles.

## 13. Dix questions d'entraînement avec corrigé

### Question 1
Quelle est la différence entre client-serveur et P2P ?

**Corrigé :** Le modèle client-serveur repose sur un serveur ou ensemble coordonné de serveurs qui répond aux clients. Le P2P fait échanger des données entre pairs et ne requiert pas un unique serveur central pour tout le réseau.

### Question 2
Un nœud complet est-il automatiquement un validateur ?

**Corrigé :** Non. Il peut vérifier les données et suivre la chaîne sans participer à la production de blocs ni au consensus en tant que validateur ou mineur.

### Question 3
Tous les nœuds ont-ils le même mempool ?

**Corrigé :** Non. Les transactions reçues, les politiques de relais, les ressources et les délais peuvent différer.

### Question 4
Pourquoi la découverte de pairs est-elle importante ?

**Corrigé :** Elle permet au nœud de trouver des participants pour échanger les données. Des mécanismes de découverte trop centralisés peuvent créer des points de fragilité ou faciliter l'isolement.

### Question 5
Une transaction absente du mempool d'un nœud est-elle invalide ?

**Corrigé :** Pas nécessairement. Elle peut ne pas lui être parvenue, être exclue par une politique locale ou être remplacée, sans que cela détermine à lui seul sa validité au consensus.

### Question 6
Qu'est-ce qu'une attaque d'éclipse ?

**Corrigé :** Une tentative d'isoler un nœud en influençant ses connexions et les informations qu'il reçoit, afin de lui donner une vue manipulée ou incomplète du réseau.

### Question 7
Pourquoi plus de connexions ne garantit-il pas toujours une meilleure décentralisation ?

**Corrigé :** Les connexions peuvent dépendre du même hébergeur, fournisseur ou opérateur. Il faut regarder leur diversité et les dépendances communes.

### Question 8
Un fournisseur RPC en panne signifie-t-il que le consensus est arrêté ?

**Corrigé :** Non. Le fournisseur peut être indisponible alors que les nœuds et le consensus continuent. Il faut tester des sources indépendantes.

### Question 9
Pourquoi le logiciel d'un nœud doit-il être mis à jour ?

**Corrigé :** Pour corriger des bugs, suivre les mises à jour de protocole et maintenir la compatibilité. Les mises à jour doivent être planifiées et testées, car une incompatibilité peut aussi causer une panne.

### Question 10
Quelle est la première étape d'un diagnostic réseau sérieux ?

**Corrigé :** Identifier précisément la couche et le symptôme, collecter des données reproductibles et comparer des sources indépendantes avant de conclure à une panne de consensus ou à une attaque.

## 14. Challenge final : un nœud ne se synchronise plus

### Scénario

Ton équipe exploite un nœud de lecture utilisé par une application interne. Le processus est actif, mais la hauteur de bloc affichée n'augmente plus. Le nombre de pairs a baissé et les requêtes RPC renvoient parfois des réponses anciennes. Un collègue propose de supprimer immédiatement les données et de tout resynchroniser.

### Travail demandé

Rédige un plan de réponse de 500 à 700 mots qui :

- commence par des contrôles non destructifs ;
- sépare les hypothèses réseau, stockage, client, RPC et consensus ;
- décrit les journaux et métriques à conserver ;
- propose des tests de comparaison avec une autre source ;
- précise dans quelles conditions une resynchronisation peut être envisagée ;
- inclut des mesures de prévention pour éviter de reproduire la panne.

### Correction proposée

La première étape n'est pas de supprimer les données. Il faut conserver l'état observé, l'heure, la version exacte du client, les paramètres de lancement, le niveau de synchronisation, le dernier bloc connu et les erreurs des journaux. Il faut vérifier l'espace disque, l'état du système de fichiers, l'utilisation CPU et mémoire, la résolution DNS, les connexions TCP, les pare-feu et les journaux du client. Un processus actif ne prouve pas que le nœud progresse.

Ensuite, il faut séparer plusieurs hypothèses. Si le nœud n'a plus de pairs, examiner la découverte, la configuration réseau et les connexions entrantes/sortantes. Si les pairs restent connectés mais que la hauteur reste stable, vérifier les erreurs de validation, le téléchargement des données, l'espace disque et la version du logiciel. Si seul le RPC renvoie des données anciennes alors que le nœud progresse, le problème peut être dans le service API ou un cache. Enfin, consulter des sources indépendantes pour déterminer si la chaîne elle-même connaît un arrêt de production ou de finalité.

Avant une opération de réparation, effectuer des sauvegardes des fichiers de configuration et des données nécessaires à l'investigation. Ne jamais supprimer une base ou réinitialiser un service sans avoir vérifié les procédures du client et les exigences de reprise. Une resynchronisation peut être envisagée si l'état local est corrompu ou si la procédure officielle le recommande, mais elle doit être planifiée en fonction du temps, de la bande passante et de la capacité de stockage. Un instantané de source fiable doit être évalué selon les garanties de vérification disponibles.

Pour la prévention, définir des alertes sur la stagnation de la hauteur, la réduction des pairs, la saturation disque, les erreurs de validation et les temps de réponse RPC. Documenter une procédure de diagnostic, tester les mises à jour en amont, diversifier les fournisseurs d'observation et maintenir un nœud de secours si le service est critique. La décision de supprimer ou reconstruire la base doit être justifiée par des faits, pas par la seule impression que le processus est bloqué.

## Glossaire

**Attaque d'éclipse :** tentative d'isoler un nœud des pairs honnêtes en influençant ses connexions.

**Client léger :** logiciel qui vérifie une partie des informations en téléchargeant moins de données qu'un nœud complet, selon les garanties du protocole.

**Fournisseur RPC :** service qui expose des méthodes permettant aux applications d'interroger un réseau ou de soumettre des transactions.

**Mempool :** ensemble local des transactions en attente connues d'un nœud ; il n'est pas identique partout.

**Mineur :** participant à la production de blocs par preuve de travail.

**Nœud :** logiciel qui participe au réseau en recevant, vérifiant, conservant ou relayant des données.

**Nœud d'archive :** nœud qui conserve des données historiques supplémentaires pour les requêtes associées.

**Nœud complet :** nœud qui valide les règles du protocole en utilisant les données nécessaires à ses fonctions.

**Pair :** participant distant avec lequel un nœud échange des messages.

**P2P :** architecture pair-à-pair où les participants échangent directement des données.

**RPC :** mécanisme d'appel à distance permettant à un programme de demander des opérations ou des données à un service.

**Sybil :** attaque qui utilise de nombreuses identités apparentes contrôlées de façon coordonnée.

**Validateur :** participant qui remplit un rôle dans le consensus d'une chaîne à preuve d'enjeu.

## Pour aller plus loin

- Guide Bitcoin pour développeurs, section réseau : https://developer.bitcoin.org/devguide/p2p_network.html
- Documentation Bitcoin Core : https://bitcoincore.org/en/doc/
- Documentation Ethereum sur les nœuds et clients : https://ethereum.org/developers/docs/nodes-and-clients/
- Documentation Ethereum sur les réseaux : https://ethereum.org/developers/docs/networks/
- Documentation Ethereum sur JSON-RPC : https://ethereum.org/developers/docs/apis/json-rpc/

Les détails de découverte, de relais et de synchronisation dépendent de la version du client. Pour un déploiement réel, consulter la documentation de la version exacte et tester la procédure de reprise dans un environnement sans risque avant de l'utiliser en production.
