# Cryptographie (hash, clés)

## Encadré de mise en contexte

La cryptographie permet à des participants de vérifier des informations et d'autoriser des actions même lorsqu'ils ne se font pas entièrement confiance. Dans une blockchain, elle contribue à détecter les modifications, à vérifier les signatures et à construire des structures de données reliées entre elles. Pourtant, la cryptographie n'est ni une magie ni une garantie universelle de sécurité. Les mécanismes cryptographiques répondent à des problèmes précis et reposent sur des hypothèses, des paramètres et des implémentations corrects.

Cette leçon construit les fondations nécessaires avant d'étudier les blocs, les transactions et les portefeuilles. Il faut surtout distinguer quatre mécanismes qui sont souvent confondus : le hachage, qui produit une empreinte ; le chiffrement, qui protège la confidentialité ; la signature numérique, qui permet de vérifier qu'un message a été autorisé par une clé privée ; et la dérivation de clés, qui transforme un secret de départ en matériel cryptographique utilisable. Ces opérations peuvent être utilisées ensemble, mais elles ne sont pas interchangeables.

## Objectifs d'apprentissage

À la fin de ce cours, tu sauras :

- expliquer le rôle d'une fonction de hachage cryptographique ;
- distinguer préimage, seconde préimage et collision ;
- comprendre pourquoi une empreinte courte permet de détecter une modification sans prouver toute la vérité d'un document ;
- expliquer le couple clé privée / clé publique et le principe d'une signature numérique ;
- distinguer signature, chiffrement, authentification et autorisation ;
- décrire la différence entre une clé, une adresse et une phrase de récupération ;
- comprendre le rôle de l'entropie et les dangers des secrets prévisibles ;
- expliquer de manière générale le hachage de mots de passe et la dérivation de clés ;
- comprendre les arbres de Merkle et leur utilité dans les blockchains ;
- réaliser des exercices sûrs avec des empreintes et des signatures sans confondre une démonstration pédagogique avec une implémentation de portefeuille réelle.

## 1. Les objectifs de la cryptographie

La cryptographie moderne ne sert pas à un seul objectif. Selon le contexte, elle peut fournir :

**Confidentialité.** Seules les personnes autorisées doivent pouvoir lire le contenu. Le chiffrement est le mécanisme habituel pour cet objectif.

**Intégrité.** Le destinataire doit pouvoir détecter une modification non autorisée des données. Un hachage cryptographique ou un code d'authentification de message peuvent participer à cette vérification.

**Authentification.** Le destinataire doit pouvoir vérifier qu'un message provient d'une entité qui détient un secret ou un moyen d'authentification donné. Une signature numérique peut montrer qu'un message est associé à une clé privée ; elle ne prouve pas à elle seule le nom civil du signataire.

**Non-répudiation au sens technique.** Une signature vérifiable peut rendre difficile pour le détenteur d'une clé de nier qu'une signature a été produite avec cette clé. La portée juridique de cette propriété dépend néanmoins du droit applicable, de la gestion de la clé, du contexte et des preuves supplémentaires. Une signature seule ne prouve pas toujours qui contrôlait réellement la clé au moment de l'opération.

**Autorisation.** Le système vérifie si l'opération demandée est permise selon ses règles. Dans une blockchain, une signature peut prouver qu'une transaction a été autorisée par une clé, mais les nœuds doivent encore vérifier que les fonds peuvent être dépensés, que la transaction respecte le protocole et qu'elle ne viole aucune autre règle.

Ces objectifs sont liés, mais un mécanisme peut remplir l'un sans remplir les autres. Une empreinte SHA-256 ne chiffre pas les données ; tout le monde peut recalculer la même empreinte. Une signature ne cache pas le message ; elle permet de vérifier qu'une signature correspond au message. Une adresse publique peut être visible sans être secrète. Il faut d'abord identifier la propriété recherchée, ensuite choisir le mécanisme adapté.

## 2. Fonctions de hachage cryptographiques

### 2.1 Définition

Une fonction de hachage transforme une entrée de taille arbitraire en une empreinte de taille déterminée. Pour SHA-256, l'empreinte comporte 256 bits, souvent affichés sous la forme de 64 caractères hexadécimaux. Une entrée d'un caractère, un fichier volumineux ou un texte très long produisent tous une sortie de 256 bits.

~~~mermaid
flowchart LR
    A["Texte, fichier ou transaction"] --> H["Fonction de hachage cryptographique"]
    H --> D["Empreinte de taille fixe"]
    D --> C["Comparaison, engagement ou lien de données"]
~~~

Une fonction de hachage ordinaire peut être utilisée pour indexer des données. Une fonction de hachage cryptographique est conçue pour rendre certaines attaques pratiquement irréalisables avec les moyens et connaissances disponibles, tant que l'algorithme reste sûr et qu'il est correctement utilisé. Le terme « cryptographique » exprime un ensemble de propriétés attendues, pas une promesse métaphysique.

### 2.2 Déterminisme

Une fonction de hachage est déterministe : pour une entrée identique, le résultat est identique. Si tu calcules plusieurs fois SHA-256 sur la même suite d'octets, tu obtiens la même empreinte. Cette propriété permet à plusieurs nœuds indépendants de vérifier une donnée sans partager un résultat secret.

Attention : une suite d'octets identique n'est pas toujours la même chose qu'un texte visuellement identique. Deux fichiers texte peuvent utiliser des fins de ligne différentes, ou un caractère accentué peut être encodé de façons différentes. Les espaces, les sauts de ligne et l'encodage font partie des octets hachés. C'est pourquoi les systèmes qui signent ou hachent des données structurées doivent définir une représentation exacte et stable des données.

### 2.3 Effet avalanche

Un bon hachage cryptographique doit produire une sortie qui paraît très différente lorsque l'entrée change légèrement. On appelle souvent cela l'effet avalanche. Si tu changes une lettre, l'empreinte devrait changer sur un grand nombre de bits sans révéler un motif simple qui permettrait de retrouver l'entrée ou de prédire la sortie.

Cet effet est utile pour repérer les modifications, mais il ne signifie pas qu'une empreinte explique ce qui a été modifié. Une différence d'empreinte te dit que les entrées ne correspondent probablement pas, pas où elles diffèrent ni pourquoi le fichier a changé.

### 2.4 Préimage, seconde préimage et collision

Trois notions sont particulièrement utiles :

- **Résistance à la préimage :** étant donnée une empreinte, il doit être impraticable de trouver une entrée qui produit cette empreinte.
- **Résistance à la seconde préimage :** étant donné un message déterminé, il doit être impraticable de trouver un autre message distinct ayant la même empreinte.
- **Résistance aux collisions :** il doit être impraticable de trouver n'importe quelle paire de messages différents qui produisent la même empreinte.

Une collision existe nécessairement en théorie lorsqu'un ensemble infini d'entrées est transformé en un ensemble fini de sorties : plusieurs entrées auront la même sortie. La question pratique est de savoir s'il est possible d'en trouver une de manière exploitable. Pour un hachage sûr de 256 bits, l'espace de recherche est très grand. Dans le modèle idéal, une attaque générique de collision a un ordre de grandeur voisin de 2 puissance 128 essais à cause du paradoxe des anniversaires, tandis qu'une recherche de préimage générique est de l'ordre de 2 puissance 256. Ce sont des ordres de grandeur théoriques, pas des commandes à exécuter sur un ordinateur ordinaire.

Le paradoxe des anniversaires signifie qu'il faut moins d'essais pour trouver deux entrées qui se rencontrent que pour atteindre une empreinte particulière. Il ne signifie pas que les collisions SHA-256 sont faciles à trouver : 2 puissance 128 reste astronomique. Les calculs supposent un comportement idéal et ne doivent pas être interprétés comme des garanties absolues pour tout algorithme.

### 2.5 Hacher n'est pas chiffrer

Le hachage ne fournit pas de mécanisme de déchiffrement. Une empreinte ne contient pas une version chiffrée que l'on pourrait simplement décoder. Mais une donnée ayant peu de possibilités peut parfois être retrouvée par essais. Si un système publie l'empreinte du mot de passe « soleil123 », un attaquant peut tester une liste de mots de passe courants et comparer les empreintes. Pour cette raison, hacher un secret faible ne le rend pas automatiquement secret.

Le chiffrement est différent : il prend un message et une clé, puis produit des données chiffrées destinées à être déchiffrées avec une clé appropriée. Un hachage cryptographique générique n'utilise pas une clé secrète et n'est pas destiné à restituer l'entrée.

### 2.6 Démonstration reproductible avec SHA-256

Sur une machine disposant de Python, on peut utiliser la bibliothèque standard pour hacher deux messages. Cette expérience sert à observer le déterminisme et l'effet avalanche, et non à créer un protocole de monnaie numérique.

~~~python
import hashlib

message_a = "Blockchain"
message_b = "blockchain"

empreinte_a = hashlib.sha256(message_a.encode("utf-8")).hexdigest()
empreinte_b = hashlib.sha256(message_b.encode("utf-8")).hexdigest()

print("A :", empreinte_a)
print("B :", empreinte_b)
print("Identiques :", empreinte_a == empreinte_b)
~~~

Les deux empreintes sont différentes, car la majuscule est différente de la minuscule. Si tu exécutes le programme une seconde fois avec les mêmes chaînes et le même encodage UTF-8, les résultats restent identiques. Il faut toujours comparer les octets exacts, et non seulement l'apparence visuelle du texte.

## 3. Hachage et chaîne de blocs

Dans une blockchain, les fonctions de hachage interviennent à plusieurs niveaux. Les données sont hachées pour identifier un bloc, et un bloc contient généralement une référence cryptographique au bloc précédent. Si le contenu d'un ancien bloc est modifié, son empreinte change. La référence stockée dans le bloc suivant ne correspond alors plus à la nouvelle empreinte.

~~~mermaid
flowchart LR
    G["Bloc 0<br/>données + hachage"] --> B["Bloc 1<br/>référence au bloc 0"]
    B --> C["Bloc 2<br/>référence au bloc 1"]
    C --> D["Bloc 3<br/>référence au bloc 2"]
    X["Modification d'une ancienne donnée"] -. "change son empreinte" .-> G
    G -. "référence devenue incohérente" .-> B
~~~

Le hachage n'empêche pas techniquement quelqu'un de modifier un fichier local. Un attaquant peut changer le bloc puis recalculer ses empreintes successives. La résistance pratique à la réécriture dépend aussi du mécanisme de consensus, de la puissance ou de la mise nécessaire pour proposer une histoire alternative, de la réplication et de la façon dont les nœuds choisissent l'historique à suivre. Le hachage rend les dépendances détectables ; il ne remplace pas le consensus.

### 3.1 Pourquoi lier les blocs ?

Le lien entre les blocs rend le passé pertinent pour la validation du présent. Un nœud qui reçoit un bloc peut vérifier que sa référence au parent correspond au bloc qu'il connaît et que les autres règles sont respectées. Les données et les liens sont ensuite répliqués chez les participants. Cette structure est une partie importante de la traçabilité et de la détection de réécriture.

Cependant, chaque bloc ne contient pas le hash complet de toutes les données précédentes. Dans un format classique, un bloc contient notamment une référence cryptographique à son parent ; il ne recopie pas forcément toutes les données de tous les blocs antérieurs. La relation est récursive : chaque bloc pointe vers le précédent, et la suite de liens permet de remonter l'historique.

## 4. Cryptographie à clé publique

### 4.1 Deux clés liées mathématiquement

La cryptographie à clé publique utilise des clés liées entre elles. Dans le schéma de signature utilisé par de nombreuses blockchains, la clé privée est un secret que l'utilisateur doit protéger. La clé publique correspondante peut être communiquée aux autres participants afin qu'ils vérifient des signatures. Il est conçu pour être praticable de calculer la clé publique depuis la clé privée, mais irréalisable de retrouver la clé privée à partir de la clé publique avec les ressources disponibles et les hypothèses cryptographiques du système.

~~~mermaid
flowchart TD
    S["Secret aléatoire de haute qualité"] --> K["Clé privée"]
    K --> P["Calcul de la clé publique"]
    P --> A["Adresse ou identifiant dérivé"]
    K --> SG["Signature d'un message"]
    P --> V["Vérification de la signature"]
    SG --> V
    M["Message exact"] --> SG
    M --> V
~~~

Une clé publique n'est donc pas un mot de passe. Elle est destinée à être partagée dans les contextes qui le demandent. Une clé privée n'est pas un identifiant public : elle donne le contrôle cryptographique associé à la clé. Toute personne qui copie la clé privée peut, dans le modèle du protocole, agir comme son détenteur.

### 4.2 Pourquoi une clé privée doit être imprévisible

Une clé privée doit être générée à partir d'une source de hasard suffisamment robuste, conforme aux exigences du système. Une valeur obtenue à partir d'un prénom, d'une date de naissance, d'un numéro de téléphone ou d'un compteur est prédictible. Même si elle est affichée avec beaucoup de chiffres, sa longueur visuelle ne crée pas de hasard.

L'entropie sert à exprimer l'incertitude d'une distribution. Si un secret peut prendre 256 valeurs équiprobables, il contient au maximum 8 bits d'entropie. Si un secret est choisi parmi un million de possibilités, l'incertitude est d'environ 20 bits parce que 2 puissance 20 est proche d'un million. Une clé de blockchain doit avoir une entropie très supérieure à ce que peut explorer un attaquant. Les logiciels de portefeuille fiables utilisent des générateurs cryptographiquement sûrs et des procédures conçues pour éviter les secrets prévisibles.

Le risque peut provenir d'un générateur défectueux, d'une mauvaise implémentation, d'un système compromis ou d'un utilisateur qui réutilise une valeur prévisible. Les garanties mathématiques ne corrigent pas un générateur aléatoire catastrophique. La génération de clés doit donc être confiée à des outils éprouvés plutôt qu'improvisée à la main.

## 5. Signatures numériques

### 5.1 Principe

Une signature numérique permet à un détenteur de clé privée de produire une preuve liée à un message. Une personne qui possède la clé publique correspondante peut vérifier que la signature est valide pour ce message, selon l'algorithme et les paramètres utilisés.

Le flux conceptuel est le suivant :

1. L'expéditeur construit un message exact.
2. Le logiciel prépare les données selon le format attendu par le protocole.
3. La clé privée est utilisée pour générer une signature.
4. Le message et la signature sont transmis.
5. Le vérificateur utilise la clé publique et le message reçu pour contrôler la signature.
6. Le protocole applique d'autres règles avant d'accepter l'opération.

~~~mermaid
sequenceDiagram
    participant A as Signataire
    participant R as Réseau
    participant N as Vérificateur
    A->>A: Préparer le message exact
    A->>A: Signer avec la clé privée
    A->>R: Envoyer message + signature
    R->>N: Transmettre l'opération
    N->>N: Vérifier avec clé publique
    N->>N: Vérifier les règles du protocole
    N-->>R: Accepter ou rejeter
~~~

Le message et la signature doivent être associés exactement comme le protocole le prévoit. Si l'utilisateur signe une transaction qui paie dix unités à Bob, la signature ne devrait pas être réutilisable pour payer dix unités à Mallory. Les protocoles définissent donc une représentation précise de la transaction et la partie qui doit être signée.

### 5.2 Ce que prouve une signature — et ce qu'elle ne prouve pas

Une signature valide indique que la signature correspond au message et à la clé publique selon l'algorithme. Dans le modèle de sécurité habituel, cela permet de conclure que la signature a été créée par quelqu'un qui possédait la clé privée, ou qu'une clé a été compromise. Mais la signature ne prouve pas spontanément :

- le nom civil du détenteur ;
- le fait que la clé soit contrôlée par une seule personne ;
- l'absence de contrainte, de tromperie ou de malware au moment de signer ;
- que le message soit vrai ;
- que l'opération soit permise par les règles de l'application ;
- que le logiciel ait affiché à l'utilisateur le même sens que les octets signés.

L'identité et le contexte sont traités par d'autres systèmes : certificats, procédures d'inscription, contrôles organisationnels, journaux, preuves externes ou droit applicable. Sur une blockchain ouverte, une clé peut simplement être un pseudonyme. Les autres participants peuvent vérifier la signature sans connaître l'état civil du signataire.

### 5.3 La signature ne chiffre pas le message

Le message signé peut être public. Dans une transaction blockchain, les montants, les destinations et plusieurs éléments de l'opération sont souvent visibles. La signature n'a pas pour but de les cacher. Pour la confidentialité, il faut d'autres mécanismes : chiffrement, protocoles de confidentialité ou conception qui évite de publier certaines informations. Même dans ce cas, la blockchain peut révéler des métadonnées telles que les heures, les montants, les relations entre adresses et les motifs de transaction.

### 5.4 ECDSA et Schnorr

Bitcoin a utilisé ECDSA sur la courbe elliptique secp256k1 pour une grande partie de ses signatures historiques. Taproot a introduit l'utilisation de signatures Schnorr pour les chemins de dépenses Taproot. Ces systèmes s'appuient sur la cryptographie à courbe elliptique, mais leurs formats, propriétés et règles d'utilisation diffèrent. Il ne faut pas prendre une fonction illustrative dans un langage de programmation pour un remplacement direct d'un algorithme de production.

Ethereum utilise également des signatures cryptographiques pour autoriser les transactions, avec des formats et des conventions propres à son protocole. Les détails d'une signature dépendent du réseau, de la version du protocole et du type de compte ou de message. Pour un développeur, la règle est simple : utiliser les bibliothèques appropriées à la chaîne concernée, respecter les formats spécifiés et ne jamais réinventer soi-même une primitive cryptographique.

## 6. Clé privée, clé publique, adresse et portefeuille

Ces quatre termes sont fréquemment confondus :

**Clé privée.** Secret cryptographique utilisé pour signer certaines opérations. Elle doit rester protégée.

**Clé publique.** Valeur dérivée de la clé privée et partagée dans les contextes où les autres doivent vérifier une signature.

**Adresse.** Identifiant utilisé comme destination ou référence selon la blockchain. Une adresse peut être dérivée de la clé publique ou d'autres données, selon le protocole. Elle n'est pas toujours une simple empreinte directe de la clé publique.

**Portefeuille.** Logiciel ou dispositif qui gère les clés, construit des transactions, affiche des informations, signe des messages et communique avec un réseau ou un service. Un portefeuille n'est pas nécessairement l'endroit où les unités numériques sont stockées physiquement.

~~~mermaid
flowchart TD
    E["Entropie ou secret de départ"] --> PK["Clé privée"]
    PK --> PU["Clé publique"]
    PU --> AD["Adresse, selon les règles du réseau"]
    PK --> SIGN["Signature d'une opération"]
    AD --> LEDGER["Le registre suit l'état associé"]
    SIGN --> CHECK["Les nœuds vérifient l'autorisation"]
~~~

L'expression « mes pièces sont dans mon téléphone » est une simplification. Le téléphone peut gérer les clés qui permettent de signer, mais le solde affiché vient généralement de l'état du réseau, parfois relayé par un fournisseur. Perdre son appareil n'est pas nécessairement fatal si les clés peuvent être restaurées. En revanche, perdre la clé ou la phrase de récupération sans copie peut rendre les fonds inaccessibles. À l'inverse, obtenir la phrase de récupération d'une autre personne peut donner à un attaquant le contrôle de ses comptes.

### 6.1 Une adresse n'est pas toujours secrète

Les adresses sont conçues pour être communiquées afin de recevoir des fonds ou d'identifier un compte. Il n'est donc pas nécessaire de les traiter comme des mots de passe. Mais leur exposition peut avoir des conséquences sur la confidentialité : un observateur peut analyser les transferts associés à une adresse et établir des liens avec d'autres adresses lorsque des informations publiques ou des motifs de transaction le permettent.

La transparence ne signifie pas que l'identité réelle est toujours évidente. Elle signifie que certaines données sont accessibles et qu'elles peuvent parfois être corrélées. Les utilisateurs et entreprises doivent évaluer la confidentialité de leurs opérations et respecter les obligations applicables.

### 6.2 Phrases de récupération et portefeuilles déterministes

Certains portefeuilles utilisent une phrase mnémonique créée à partir d'une source d'entropie et d'un standard de génération de clés. Cette phrase permet de restaurer un ensemble de clés dans des outils compatibles si elle est bien sauvegardée et si les paramètres nécessaires sont connus. La phrase de récupération est extrêmement sensible : elle peut donner accès à de nombreuses clés, et pas seulement à une adresse.

Une phrase ne doit pas être envoyée par courriel, saisie dans un formulaire inconnu, photographiée dans un service cloud non maîtrisé ou communiquée à une personne qui promet une assistance. Une interface malveillante peut demander de la saisir en prétendant vérifier le portefeuille. Il faut se méfier de toute demande de phrase de récupération pour « déverrouiller », « synchroniser » ou « vérifier » un compte.

Un portefeuille déterministe hiérarchique peut dériver de nombreuses clés à partir d'un secret de départ et d'un chemin de dérivation. Cela facilite la sauvegarde et l'organisation, mais augmente aussi l'impact potentiel de la fuite du secret racine. Des portefeuilles peuvent utiliser différentes normes de phrase, de dérivation et de chemins ; une phrase seule peut ne pas suffire à retrouver exactement les mêmes adresses si le logiciel, la passphrase ou le chemin diffèrent.

## 7. Chiffrement symétrique et asymétrique

Le chiffrement symétrique utilise une clé secrète partagée pour chiffrer et déchiffrer. Il peut être très efficace pour protéger de grands volumes de données. Le problème est de transmettre et de conserver la clé de manière sûre.

Le chiffrement asymétrique utilise une paire de clés selon un schéma prévu pour la confidentialité ou l'établissement de secrets. Il peut faciliter certains échanges, mais les systèmes modernes associent généralement plusieurs mécanismes : échange de clés, chiffrement symétrique authentifié, certificats ou protocoles d'authentification.

Il faut éviter une confusion fréquente : une paire de clés utilisée pour les signatures n'est pas automatiquement une paire appropriée pour chiffrer des messages. Les algorithmes et les clés sont employés selon des règles particulières. Une adresse blockchain publique n'est donc pas une destination à laquelle on peut simplement envoyer un texte chiffré que seule la clé privée de l'adresse pourrait ouvrir.

### 7.1 Pourquoi la blockchain ne chiffre-t-elle pas tout ?

Les blockchains publiques ont généralement besoin que les nœuds puissent vérifier les transactions et reconstruire l'état partagé. Si tous les détails nécessaires au consensus étaient chiffrés de façon opaque pour les validateurs, ceux-ci ne pourraient pas forcément vérifier les règles sans mécanismes supplémentaires complexes. De nombreux réseaux publient donc des données essentielles à la validation.

La transparence facilite l'auditabilité, mais peut nuire à la confidentialité. Des approches spécifiques peuvent réduire cette tension, mais elles ont leurs propres hypothèses, coûts, limites de performance et conséquences de conception. Le simple fait d'utiliser une blockchain ne rend pas une application confidentielle.

## 8. Sel, hachage de mots de passe et dérivation de clés

Les mots de passe humains sont habituellement beaucoup moins aléatoires que des clés cryptographiques. Un attaquant qui obtient une base de données d'empreintes peut essayer des mots de passe probables et comparer les résultats. On ne devrait donc pas utiliser un hachage rapide générique comme SHA-256 seul pour stocker des mots de passe.

Les systèmes sérieux utilisent des fonctions de dérivation dédiées, par exemple Argon2id, scrypt, bcrypt ou PBKDF2 selon les contraintes et les exigences de l'environnement. Ces mécanismes sont conçus pour rendre la vérification de chaque candidat plus coûteuse et, pour certaines familles, plus exigeante en mémoire. Le choix dépend notamment des normes de sécurité, de la compatibilité et des capacités d'exploitation.

Un **sel** est une valeur non secrète unique associée à chaque mot de passe avant le calcul de l'empreinte. Il empêche que deux utilisateurs ayant le même mot de passe aient automatiquement la même empreinte et rend inutilisables les tables précalculées génériques correspondantes. Le sel ne remplace pas un mot de passe fort ni une fonction lente. Un **secret serveur supplémentaire** ou *pepper* peut parfois être ajouté en dehors de la base de données, mais il impose une gestion distincte et ne doit pas être confondu avec le sel.

Ces mécanismes sont utiles pour l'authentification d'une application, mais ils ne sont pas la façon générale de produire les clés privées d'une blockchain. Les clés blockchain demandent une entropie de haute qualité et des procédures cryptographiques conçues pour ce but. Hacher un mot de passe faible pour en faire une clé ne transforme pas sa faible entropie en un secret robuste.

## 9. Arbres de Merkle

### 9.1 Pourquoi des arbres ?

Un bloc peut contenir des milliers de transactions. Pour organiser les empreintes de ces transactions, certains systèmes utilisent un arbre de Merkle. Les transactions sont hachées, puis les empreintes sont regroupées par paires et hachées à nouveau. Le processus se poursuit jusqu'à obtenir une empreinte racine, appelée racine de Merkle.

~~~mermaid
flowchart TD
    A["Transaction A"] --> HA["Hash A"]
    B["Transaction B"] --> HB["Hash B"]
    C["Transaction C"] --> HC["Hash C"]
    D["Transaction D"] --> HD["Hash D"]
    HA --> P1["Hash(A || B)"]
    HB --> P1
    HC --> P2["Hash(C || D)"]
    HD --> P2
    P1 --> R["Racine de Merkle"]
    P2 --> R
~~~

La racine résume de manière compacte l'ensemble ordonné des données couvertes par l'arbre. Si une transaction change, son empreinte change, puis les empreintes des nœuds parents concernés changent jusqu'à la racine. Un bloc peut intégrer la racine dans son en-tête. Il devient alors possible de fournir une preuve qui montre qu'une transaction appartient à l'arbre sans transmettre toutes les autres transactions.

### 9.2 Preuve d'inclusion

Pour vérifier une transaction, un vérificateur peut recevoir la transaction, son empreinte, puis les empreintes des branches nécessaires pour reconstruire la racine. Il combine chaque élément dans le bon ordre, recalcule les empreintes intermédiaires et compare le résultat à la racine connue. Si la racine correspond et si les hypothèses cryptographiques tiennent, la preuve soutient l'inclusion de la transaction dans l'ensemble engagé par cette racine.

La preuve ne dit pas que la transaction est honnête, légale ou économiquement appropriée. Elle n'établit pas non plus à elle seule que le bloc est accepté par le consensus ou qu'il est suffisamment confirmé. Elle vérifie une propriété particulière : l'inclusion dans un ensemble de données défini.

~~~mermaid
sequenceDiagram
    participant P as Fournisseur de preuve
    participant V as Vérificateur
    P->>V: Transaction + frères de Merkle + racine attendue
    V->>V: Hacher la transaction
    V->>V: Combiner les empreintes selon l'ordre
    V->>V: Recalculer jusqu'à la racine
    V-->>V: Comparer à la racine connue
    Note over V: Inclusion vérifiée si les règles correspondent
~~~

### 9.3 Limites et détails de construction

L'arbre de Merkle n'est pas simplement une liste de hashes disposés en forme de pyramide. La façon de construire l'arbre, d'ordonner les éléments, de traiter un nombre impair de feuilles et de distinguer les types de données est déterminante. Une implémentation qui calcule la bonne fonction de hachage mais qui utilise le mauvais encodage ou l'ordre incorrect peut produire un résultat incompatible avec le protocole.

Différentes blockchains utilisent différentes structures d'engagement cryptographique. Les arbres de Merkle classiques, les variantes Patricia et d'autres structures n'ont pas exactement les mêmes objectifs. Il faut utiliser le terme précis correspondant à la structure étudiée plutôt que d'appeler « arbre de Merkle » n'importe quel index de données.

## 10. Les engagements cryptographiques et les liens entre données

Une empreinte peut servir d'engagement envers une donnée : l'auteur publie l'empreinte maintenant, puis révèle éventuellement le contenu plus tard. Le vérificateur hache le contenu révélé et compare l'empreinte. Cela peut démontrer que le contenu présenté correspond à l'engagement initial, en supposant le bon encodage et un hachage sûr.

Si la donnée est prévisible, un engagement simplement haché peut divulguer de l'information par essais. Par exemple, l'empreinte d'un choix parmi quatre réponses possibles peut être devinée en calculant les quatre empreintes. Des constructions d'engagement peuvent ajouter un sel secret ou aléatoire à la donnée afin d'atténuer ce risque. Il faut suivre le protocole prévu : ajouter un champ improvisé peut lui-même rendre la preuve non compatible.

Un autre usage consiste à lier des événements entre eux. Un journal peut contenir le hachage de l'entrée précédente : modifier un événement entraîne une rupture de la chaîne. Cependant, si l'attaquant contrôle aussi toutes les copies et peut recalculer le journal sans témoin externe, le hachage seul ne prouve pas qu'une ancienne version existait réellement. Un journal chaîné gagne en force quand ses racines sont périodiquement partagées, signées, publiées ou répliquées par un système indépendant.

## 11. Domaines de menace : ce que la cryptographie ne répare pas

Une conception sûre doit examiner la génération, le stockage, l'utilisation et la restauration des clés. Les principaux risques ne proviennent pas tous de la rupture d'un algorithme :

- **Hameçonnage :** l'utilisateur signe une opération qu'il comprend mal ou donne sa phrase de récupération.
- **Malware :** le logiciel malveillant remplace une adresse ou détourne une signature.
- **Génération faible :** une clé est créée avec une source de hasard insuffisante.
- **Sauvegarde exposée :** une phrase de récupération est stockée dans un fichier accessible à un tiers.
- **Erreur d'interface :** les informations montrées à l'utilisateur ne reflètent pas les octets qui seront signés.
- **Réutilisation des secrets :** une même clé est utilisée dans des contextes différents, ce qui accroît l'impact d'une compromission ou d'une erreur de conception.
- **Algorithme obsolète :** une primitive ne répond plus aux exigences de sécurité actuelles.
- **Mauvaise validation :** le vérificateur n'applique pas correctement le protocole ou accepte des représentations ambiguës.

La cryptographie fournit des briques solides quand elles sont bien utilisées. Elle ne peut pas décider si le destinataire d'un paiement est un escroc, si un utilisateur a été trompé par une interface ou si un contrat respecte une réglementation. La sécurité exige une analyse du système complet, des procédures, de l'exploitation et du comportement humain.

## 12. TP guidé A : observer un hachage sans outil spécialisé

### Objectif

Comparer des fichiers et observer l'effet d'une modification, en utilisant des outils locaux non destructifs.

### Étape 1 — Créer deux fichiers

Crée un dossier de travail et deux fichiers texte UTF-8. Le premier contient la ligne formation blockchain, le second contient exactement la même ligne. Vérifie qu'il n'existe pas d'espace différent à la fin des lignes.

### Étape 2 — Calculer les empreintes

Sur un système disposant d'OpenSSL, la commande suivante calcule l'empreinte SHA-256 d'un fichier :

~~~bash
openssl dgst -sha256 fichier.txt
~~~

Sous PowerShell, tu peux utiliser la commande intégrée suivante :

~~~powershell
Get-FileHash .\fichier.txt -Algorithm SHA256
~~~

Les deux outils doivent produire la même empreinte si le contenu exact des fichiers est identique. Les commandes calculent une empreinte ; elles ne modifient pas le fichier.

### Étape 3 — Modifier un caractère

Change seulement une lettre ou ajoute un espace, puis relance le calcul. Observe que l'empreinte devient très différente. Reviens ensuite au contenu exact initial et vérifie que l'empreinte précédente réapparaît.

### Étape 4 — Consigner les résultats

Note l'algorithme, les noms de fichiers, la taille en octets, les empreintes et les modifications réalisées. Évite de partager publiquement des fichiers contenant des mots de passe ou des informations personnelles : le TP ne nécessite aucun secret réel.

### Questions de réflexion

- Une empreinte prouve-t-elle que le fichier est vrai ?
- Une empreinte permet-elle de retrouver un fichier quelconque de même taille ?
- Pourquoi faut-il noter l'algorithme et les paramètres employés ?
- Que se passe-t-il si un éditeur modifie la fin de ligne ou l'encodage du fichier ?

**Corrigé :** L'empreinte permet de comparer des contenus selon une fonction précise, mais n'atteste pas la vérité ou l'origine du fichier sans mécanisme complémentaire. Elle ne permet pas généralement de retrouver la donnée arbitraire. L'algorithme et les conventions d'encodage assurent que la comparaison porte sur la même représentation. Les fins de ligne et l'encodage changent les octets et donc le résultat.

## 13. TP guidé B : comprendre le flux d'une signature

Le but de ce TP est de dessiner et de commenter le flux de signature, sans générer une clé de portefeuille de production et sans envoyer de transaction réelle.

### Étape 1 — Définir le message

Écris un message pédagogique comme « autoriser le test numéro 17 pour le réseau de laboratoire ». Dans un système réel, il faudrait un format non ambigu, une destination, un montant, un identifiant de chaîne, un nonce et d'autres champs propres au protocole. Le texte humain n'est qu'une représentation illustrative.

### Étape 2 — Distinguer les rôles

Dessine trois acteurs : le signataire, le transporteur du message et le vérificateur. Le signataire contrôle une clé privée et signe les données exactes. Le transporteur peut être considéré comme non fiable. Le vérificateur dispose du message et de la clé publique attendue.

### Étape 3 — Prévoir les mutations

Dans le diagramme, montre ce qui se passe si l'attaquant change le destinataire, le montant ou un seul octet des données signées. La vérification doit échouer pour le message modifié, à condition que la signature et la validation soient utilisées conformément au schéma et que la partie modifiée soit effectivement couverte par la signature.

### Étape 4 — Identifier les hypothèses

Énumère au moins quatre hypothèses nécessaires : clé privée protégée, générateur de clés robuste, données signées non ambiguës, implémentation sûre, vérification de la clé publique attendue et règles de protocole appliquées. Ce dernier point est essentiel : une signature valide ne rend pas automatiquement toute transaction valide.

## 14. Dix questions d'entraînement avec corrigé

### Question 1
À quoi sert une fonction de hachage cryptographique dans une blockchain ?

**Corrigé :** Elle produit une empreinte déterministe des données, utile pour détecter des modifications, identifier des contenus et lier des structures. La sécurité du registre dépend également du consensus et de la réplication.

### Question 2
Quelle est la différence entre une collision et une préimage ?

**Corrigé :** Une collision est une paire de messages différents ayant la même empreinte. Une préimage est une entrée qui produit une empreinte donnée ; la résistance à la préimage désigne la difficulté de retrouver une telle entrée lorsqu'on connaît seulement la sortie.

### Question 3
Pourquoi un SHA-256 ne chiffre-t-il pas un document ?

**Corrigé :** Le hachage ne fournit pas de procédure de déchiffrement. L'empreinte est destinée à résumer le contenu, pas à permettre au destinataire de le récupérer.

### Question 4
Une signature numérique cache-t-elle le message ?

**Corrigé :** Non. Elle permet de vérifier qu'une signature correspond à un message et à une clé publique. La confidentialité exige un mécanisme de chiffrement distinct.

### Question 5
Une clé publique permet-elle d'affirmer le nom civil de son détenteur ?

**Corrigé :** Non. Elle permet de vérifier des signatures correspondant à la clé privée liée. L'identité doit être établie par des mécanismes externes ou un contexte de confiance.

### Question 6
Pourquoi une clé privée ne doit-elle pas être choisie comme une date de naissance ?

**Corrigé :** Parce que ce choix a une entropie faible et peut être exploré par un attaquant. Une clé doit être générée avec un hasard cryptographiquement sûr.

### Question 7
Quelle est la différence entre une clé privée et une adresse ?

**Corrigé :** La clé privée est un secret qui autorise certaines signatures ; l'adresse est un identifiant utilisé par le protocole. Publier une adresse peut être normal ; exposer la clé privée compromet le contrôle cryptographique.

### Question 8
Que vérifie une preuve d'inclusion de Merkle ?

**Corrigé :** Elle permet de vérifier qu'une donnée correspond à un élément de l'arbre engagé par une racine connue, selon la structure exacte. Elle ne prouve pas la vérité ou la légalité de l'élément.

### Question 9
Pourquoi ne pas stocker directement les mots de passe avec SHA-256 seul ?

**Corrigé :** SHA-256 est rapide et facilite les essais massifs de candidats. Les mots de passe nécessitent une fonction de dérivation dédiée et coûteuse, avec un sel unique et une configuration adaptée.

### Question 10
Que garantit une signature valide sur une transaction blockchain ?

**Corrigé :** Elle confirme que la signature correspond aux données couvertes et à la clé attendue, selon l'algorithme. Les nœuds doivent encore vérifier les règles du protocole, l'état et les conditions de dépense.

## 15. Challenge final : analyser une demande de signature suspecte

### Scénario

Un utilisateur reçoit un message disant : « Votre portefeuille a un problème. Pour prouver que vous êtes propriétaire de vos fonds, envoyez votre phrase de récupération et signez ce message. » L'utilisateur demande conseil à ton équipe.

### Travail demandé

Rédige une note de sécurité de 500 à 700 mots qui :

- identifie les secrets qui ne doivent jamais être communiqués ;
- distingue l'action de signer une donnée de celle de révéler une clé privée ;
- explique pourquoi la signature d'un message arbitraire peut présenter un risque si le contenu est trompeur ;
- propose une procédure de vérification indépendante du message reçu ;
- décrit comment réagir si une phrase de récupération a déjà été divulguée.

### Correction proposée

La phrase de récupération est un secret de contrôle. Toute personne qui l'obtient peut généralement restaurer le portefeuille dans un logiciel compatible et contrôler les clés dérivées. Elle ne doit pas être transmise à un support technique, un formulaire, un site web ou une personne qui prétend réparer une erreur. Le service légitime n'a normalement aucune raison de demander cette phrase pour vérifier une transaction publique.

La signature est différente : elle est produite par la clé privée à partir de données définies. Elle ne révèle pas automatiquement la clé privée, mais elle autorise ou prouve quelque chose selon le type de message et le système qui l'interprète. Une demande de signature aveugle reste dangereuse. Le message peut être conçu pour autoriser un contrat, une connexion, une délégation ou une opération qui n'est pas évidente à l'écran. Il faut lire le contenu et comprendre le résultat attendu avant de signer. Si le logiciel n'affiche pas une interprétation claire, l'utilisateur doit refuser.

La procédure doit partir d'un canal indépendant : ouvrir manuellement le site officiel connu ou l'application installée depuis une source fiable, vérifier les annonces du fournisseur, consulter un explorateur de blocs réputé pour confirmer l'état public et utiliser les contacts officiels déjà connus, jamais les liens du message suspect. Il ne faut pas cliquer sur une adresse proposée dans un message alarmant, et l'utilisateur ne doit pas donner à un tiers le contrôle de son écran ou de son portefeuille sans procédure de confiance.

Si la phrase de récupération a été divulguée, il faut considérer les clés dérivées comme compromises. Depuis un environnement propre et un portefeuille de confiance, l'utilisateur doit créer un nouvel ensemble de clés avec une phrase neuve et transférer les actifs vers les nouvelles adresses, en vérifiant soigneusement les destinations et les frais. Il ne faut pas restaurer le secret compromis dans un appareil infecté ou révéler la nouvelle phrase en essayant de « sécuriser » l'ancien portefeuille. Si l'incident implique une entreprise, il faut préserver les preuves, suivre la procédure de réponse aux incidents et évaluer toutes les clés dérivées, les autorisations de contrats et les comptes liés.

La règle de sécurité fondamentale est de ne jamais confondre transparence et innocuité. Une adresse publique peut être partagée, mais une phrase de récupération est un secret. Une signature peut être vérifiable publiquement, mais elle doit être précédée d'une compréhension de ce qui est autorisé. La cryptographie protège des propriétés définies ; les utilisateurs doivent aussi protéger les clés, les interfaces et les décisions humaines.

## Glossaire

**Adresse :** identifiant utilisé par une blockchain pour recevoir des actifs ou désigner un compte ou une condition de dépense.

**Arbre de Merkle :** structure d'empreintes qui permet d'engager un ensemble de données et de fournir des preuves d'inclusion compactes.

**Authentification :** vérification d'une revendication d'identité ou de possession d'un moyen d'authentification, dans un contexte défini.

**Clé privée :** secret cryptographique utilisé pour produire des signatures ou effectuer une opération liée à un schéma de clés.

**Clé publique :** valeur associée à la clé privée, utilisée selon le schéma pour vérifier les signatures ou établir certains mécanismes cryptographiques.

**Collision :** deux entrées différentes qui produisent la même empreinte.

**Confidentialité :** propriété qui limite l'accès au contenu aux parties autorisées.

**Dérivation de clés :** procédé qui produit des clés à partir de secrets ou de matériaux d'entrée selon des règles déterminées.

**Entropie :** mesure de l'incertitude d'une source de données ; elle contribue à la qualité d'un secret.

**Fonction de hachage :** fonction qui associe une entrée à une sortie de taille déterminée.

**Intégrité :** capacité à détecter une modification non autorisée des données.

**Phrase de récupération :** représentation mnémonique permettant généralement de restaurer un portefeuille ou de dériver ses clés.

**Préimage :** entrée produisant une empreinte donnée.

**Signature numérique :** preuve cryptographique vérifiable qui associe un message à une clé privée correspondante.

**Sel :** valeur non secrète ajoutée au traitement d'un mot de passe afin d'éviter plusieurs faiblesses des stockages par empreinte.

**SHA-256 :** fonction de hachage cryptographique qui produit une empreinte de 256 bits.

**UTXO :** sortie de transaction non dépensée, modèle utilisé notamment par Bitcoin.

## Pour aller plus loin

- Documentation Python sur hashlib : https://docs.python.org/3/library/hashlib.html
- Documentation officielle OpenSSL : https://docs.openssl.org/
- Guide Bitcoin pour développeurs : https://developer.bitcoin.org/devguide/
- Documentation de sécurité OWASP sur le stockage des mots de passe : https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html
- Livre blanc de Bitcoin : https://bitcoin.org/bitcoin.pdf

Pour toute application réelle, ne conçois pas un algorithme cryptographique maison. Utilise les spécifications officielles, des bibliothèques largement auditées et une procédure de gestion des clés adaptée au modèle de menace. Les opérations présentées ici servent à comprendre les concepts ; elles ne constituent pas un portefeuille de production.
