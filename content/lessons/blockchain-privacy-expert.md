# ZK-proofs et confidentialité

## Encadré de mise en contexte

Une preuve à divulgation nulle de connaissance, souvent appelée preuve ZK (zero-knowledge proof), permet à un prouveur de démontrer qu'une déclaration respecte des conditions sans révéler nécessairement tous les secrets qui servent à établir cette déclaration. Les preuves de ce type sont utilisées dans différents domaines : systèmes d'identité, vérification de calcul, transactions confidentielles, attestations et rollups.

Le mot ZK ne signifie pas automatiquement qu'une application est anonyme ou que toutes ses données sont secrètes. Une preuve peut démontrer qu'un calcul est correct tout en laissant publiques les données d'entrée. Un rollup peut utiliser une preuve de validité sans masquer les adresses ni les montants. La confidentialité dépend de ce que le système choisit de divulguer, des métadonnées disponibles et de la manière dont les identités peuvent être reliées entre plusieurs usages.

Cette leçon présente les propriétés cryptographiques, les rôles du témoin, des entrées publiques et du vérificateur, l'arithmétisation, les familles de SNARK et de STARK, les engagements, les nullifiers, les circuits, les risques de setup, ainsi que les limites opérationnelles et de confidentialité. Les exemples servent à comprendre et à évaluer des systèmes ; toute implémentation réelle doit utiliser des primitives et des bibliothèques cryptographiques examinées, avec des paramètres documentés.

## Objectifs d'apprentissage

À la fin du cours, tu dois pouvoir expliquer les propriétés de complétude, solidité et confidentialité d'une preuve, distinguer preuve de validité et preuve de confidentialité, définir témoin et entrées publiques, expliquer le rôle des circuits et contraintes, comparer à haut niveau SNARK et STARK, comprendre les engagements et nullifiers, analyser les risques de données et de métadonnées, et écrire un modèle de menace pour une application qui utilise des preuves ZK.

## Prérequis et parcours pratique

Il est utile de connaître les fonctions de hachage, les signatures, l'algèbre de base, les arbres de Merkle et les smart contracts. Les travaux pratiques doivent être effectués avec des exemples fictifs et des bibliothèques de test documentées. N'invente pas ton propre système de preuve pour protéger des données ou des fonds réels : la sécurité repose sur des détails mathématiques et d'implémentation qui dépassent la seule idée générale.

Le parcours pratique consiste à décrire une déclaration, choisir ce que le vérificateur peut connaître, identifier le témoin secret et les contraintes, puis tester si le design révèle encore des informations indirectes. Tu vas également analyser la différence entre une preuve de calcul valide et une garantie de confidentialité complète.

## 1. Qu'est-ce qu'une preuve à divulgation nulle de connaissance ?

Un protocole ZK permet à un prouveur de convaincre un vérificateur qu'une déclaration est vraie sans révéler le témoin qui la justifie, au-delà de l'information que le protocole est conçu pour divulguer. Le prouveur possède des données privées, le témoin, qui satisfont une relation. Le vérificateur reçoit une preuve et des entrées publiques, puis accepte ou rejette selon le protocole.

Trois propriétés conceptuelles sont centrales. La **complétude** signifie qu'un prouveur honnête ayant un témoin valide peut faire accepter la preuve. La **solidité** signifie qu'un prouveur ne devrait pas pouvoir convaincre le vérificateur d'une déclaration fausse, sauf avec une probabilité négligeable ou sous une hypothèse clairement spécifiée. La **confidentialité ZK** signifie que la preuve ne révèle pas plus que ce que la déclaration et les sorties autorisées impliquent, selon la définition formelle du système.

Ces propriétés ne suffisent pas à elles seules à définir un produit sûr. L'implémentation peut exposer le témoin dans les logs, les erreurs, le navigateur ou les systèmes de télémétrie. Les entrées publiques peuvent permettre de relier plusieurs preuves. Une preuve peut être mathématiquement correcte mais porter sur une déclaration métier trop faible. Le design doit donc définir ce qui est prouvé, ce qui est publié et ce qui est caché.

~~~mermaid
flowchart LR
    W[Témoin privé] --> P[Prouveur]
    X[Entrées publiques] --> P
    P --> Z[Preuve]
    X --> V[Vérificateur]
    Z --> V
    V --> R[Acceptée ou rejetée]
~~~

Le diagramme montre le flux conceptuel. Les détails varient selon les systèmes interactifs et non interactifs, mais la séparation entre témoin, déclaration publique et preuve reste essentielle pour analyser les fuites.

## 2. Preuve de validité et confidentialité : deux objectifs distincts

Une preuve de validité démontre que certains calculs ou transitions respectent les règles représentées. Une preuve ZK peut atteindre cet objectif tout en cachant le témoin. Mais une preuve de validité peut aussi être conçue de façon à rendre visibles des données nécessaires au calcul. De même, un système peut préserver une certaine confidentialité sans utiliser une preuve ZK, par exemple en limitant qui a accès aux données, même si cela introduit d'autres hypothèses de confiance.

Il faut donc poser deux questions différentes : « le résultat est-il correct selon les règles ? » et « qu'apprend le vérificateur sur les données privées ? ». La réponse à la première ne résout pas automatiquement la seconde. Une preuve peut établir qu'un compte dispose d'un solde suffisant sans révéler le solde exact, mais si l'application publie aussi des opérations corrélées, un observateur peut déduire des informations supplémentaires.

La confidentialité dépend également des métadonnées : horaires, frais, taille des messages, fréquence des opérations, identités de relayers, adresses de dépôt, comportement du portefeuille et accès aux interfaces. Même si le témoin reste secret, les métadonnées peuvent permettre de relier des transactions. Le modèle de confidentialité doit inclure le protocole complet, pas seulement le circuit.

## 3. Définir la déclaration avant le circuit

Un système de preuve encode une relation mathématique. La première étape consiste à écrire la déclaration en langage métier, puis à la traduire en conditions vérifiables. Exemple : « l'utilisateur connaît un secret qui correspond à un engagement publié et ce secret appartient à une liste autorisée ». Cette phrase peut devenir une relation formelle avec un engagement public, un témoin privé et des contraintes de validité.

La déclaration ne doit pas être plus faible que l'exigence produit. Si le système prouve seulement qu'un utilisateur connaît un secret mais ne vérifie pas qu'il correspond à une autorisation valable, la preuve peut être correctement calculée tout en étant insuffisante. À l'inverse, une déclaration trop large peut exiger un circuit complexe et divulguer davantage de données publiques que nécessaire.

La spécification doit lister les entrées publiques, le témoin, les contraintes et la sortie attendue. Elle doit aussi préciser les hypothèses de confiance, les domaines d'identité, la version de la déclaration et les conditions d'échec. Le vérificateur doit savoir quelle relation il accepte ; une preuve valide pour une version ou une application ne doit pas être interprétée automatiquement comme valide dans un autre contexte.

## 4. Témoin, variables publiques et contraintes

Le témoin contient les informations privées qui permettent de satisfaire la relation. Les entrées publiques sont accessibles au vérificateur et peuvent être inscrites sur une blockchain. Les contraintes décrivent les relations mathématiques qui doivent être vraies pour que la preuve soit acceptée. Un circuit est une manière de représenter un calcul comme un ensemble de contraintes compatibles avec le système de preuve utilisé.

La distinction entre public et privé doit être conçue avec soin. Une valeur privée peut fuiter si elle est utilisée comme sortie, si elle est sérialisée dans un message ou si un composant réutilise une même valeur dans plusieurs contextes. Une valeur publique peut également révéler indirectement un secret si elle réduit fortement les possibilités compatibles avec la preuve.

Les circuits ne sont pas des programmes classiques sans limites. Ils représentent les calculs dans un modèle mathématique particulier, souvent sur un corps fini. Les comparaisons, l'arithmétique signée, le traitement de chaînes, les champs booléens et les limites de taille peuvent demander des contraintes supplémentaires. Un code source qui paraît évident en langage général peut représenter une relation différente lorsqu'il est traduit en contraintes.

## 5. Complétude, solidité et modèle de menace

La complétude traite le cas honnête : si les entrées et le témoin respectent la déclaration, la preuve devrait être acceptée. Un échec de complétude se manifeste lorsqu'un utilisateur légitime ne peut pas générer une preuve valide à cause d'un bug, d'un format, d'une limite ou d'une incohérence entre le prouveur et le vérificateur.

La solidité traite le cas malveillant : une personne ne devrait pas pouvoir faire accepter une déclaration fausse sans contourner les hypothèses cryptographiques ou exploiter une erreur du système. Une erreur dans les contraintes peut permettre au prouveur de démontrer une propriété qui n'est pas celle attendue. Le système de preuve ne corrige pas le sens incorrect de la déclaration encodée.

La propriété de confidentialité traite l'information que la preuve révèle. Une preuve peut protéger le témoin tout en laissant les entrées publiques identifier l'utilisateur. Un système peut aussi révéler le secret via les journaux du prouveur, la télémétrie ou une interface mal conçue. Les trois propriétés doivent donc être testées et examinées séparément.

Le modèle de menace doit inclure le prouveur, le vérificateur, les développeurs de circuit, le service de génération de preuves, les systèmes de publication des paramètres et les opérateurs qui maintiennent l'application. Dans les systèmes qui exigent une configuration de paramètres, la cérémonie de génération et les personnes qui y participent deviennent une frontière de confiance supplémentaire.

## 6. SNARK et STARK : comparer les familles avec prudence

SNARK et STARK désignent des familles de constructions, pas une unique implémentation. Certains SNARK produisent des preuves compactes et rapides à vérifier, mais peuvent demander des paramètres issus d'une configuration particulière. D'autres constructions cherchent à éviter un setup de confiance spécifique. Les STARK utilisent typiquement des techniques de preuve transparentes fondées sur des engagements et des tests de cohérence, avec des compromis différents de taille de preuve, de vérification et de coût de génération.

Le bon choix dépend de la taille du calcul, des exigences de vérification, du coût on-chain, de la maturité des outils, de la surface de sécurité et du modèle cryptographique acceptable. Il ne faut pas déclarer qu'une famille est toujours plus rapide ou plus sûre que l'autre. Le coût de génération peut devenir l'obstacle principal pour l'utilisateur, même lorsque le vérificateur est peu coûteux.

La comparaison exige des benchmarks représentatifs, la version des bibliothèques, le matériel, la taille du témoin, la compilation et la taille des preuves. Les données théoriques ou un benchmark isolé ne suffisent pas à estimer les coûts d'un produit. Évalue aussi la possibilité de maintenir le système et de mettre à jour le circuit sans casser les preuves historiques ou la sécurité de la vérification.

## 7. Configuration de confiance et gestion des paramètres

Certaines constructions utilisent des paramètres publics dont la génération demande une cérémonie ou une configuration de confiance. Dans ce modèle, les participants doivent suivre une procédure définie et les hypothèses liées à la destruction ou à la non-conservation de matériel secret doivent être documentées. Le risque dépend de la construction exacte ; n'applique pas la même explication à toutes les familles de SNARK.

Une cérémonie multi-parties peut réduire le besoin de faire confiance à un participant unique si le protocole garantit que la contribution d'au moins un participant honnête suffit et si celui-ci détruit effectivement la valeur secrète pertinente. Cela ne signifie pas que la cérémonie devient sans hypothèse : il faut vérifier le processus, l'implémentation, les contributions et l'archivage des paramètres publics.

Les systèmes de preuve transparents évitent certaines hypothèses de setup, mais ils ont eux aussi des hypothèses cryptographiques, des paramètres et une complexité d'implémentation. La transparence ne signifie pas qu'un logiciel est automatiquement correct. Dans tous les cas, les artefacts, les versions, les hash de paramètres et les commandes de génération doivent pouvoir être vérifiés.

## 8. Engagements cryptographiques et arbres de Merkle

Un engagement cryptographique permet de fixer une valeur sans la révéler immédiatement, tout en fournissant un mécanisme pour montrer plus tard que la valeur ouverte correspond à l'engagement initial. La propriété dépend du schéma d'engagement et de ses hypothèses. Il faut distinguer l'engagement d'un hash simple, d'un schéma d'engagement dédié et d'une signature.

Les arbres de Merkle permettent d'engager un ensemble de valeurs avec une racine. Une preuve d'inclusion permet de démontrer qu'un élément correspond à cette racine sans publier nécessairement tous les éléments de l'arbre. Dans une application ZK, le témoin peut inclure une valeur et son chemin de Merkle, tandis que la racine et l'affirmation sont publiques. Le circuit vérifie que le chemin est cohérent avec la racine et les règles du protocole.

La racine publique peut servir à identifier une version d'un ensemble, mais la preuve doit établir ce qu'il est autorisé à faire avec l'élément inclus. Une preuve d'appartenance ne démontre pas à elle seule que l'élément est encore valide, non révoqué ou autorisé pour toutes les fonctions. Les règles de révocation et de mise à jour doivent être intégrées à la déclaration.

## 9. Nullifiers et prévention de la double utilisation

Dans plusieurs systèmes confidentiels, un nullifier permet de révéler qu'une capacité ou un élément a été utilisé sans révéler directement l'identité ou le secret sous-jacent. Il est calculé à partir de valeurs liées au témoin et au contexte, selon une construction précise. Le contrat ou le vérificateur peut refuser un nullifier déjà vu, ce qui prévient la réutilisation de la même capacité.

Le nullifier crée un compromis. S'il est déterministe dans un contexte, il peut permettre de repérer une répétition ou de lier des actions. Si les paramètres du contexte sont mal choisis, il peut relier des opérations qui devaient rester indépendantes, ou au contraire permettre un rejeu dans un autre domaine. Il faut définir la portée : contrat, chaîne, époque, application ou opération.

La déclaration doit lier le nullifier au contexte approprié et le contrat doit stocker les valeurs consommées selon une règle claire. Teste la répétition, le changement de domaine, les mises à niveau et les valeurs frontières. Ne suppose pas que le calcul du nullifier garantit seul la confidentialité ; une mauvaise conception peut aussi révéler des relations entre utilisateurs ou transactions.

## 10. Confidentialité : identité, liaison et métadonnées

La confidentialité se mesure par les inférences qu'un adversaire peut tirer. Une application peut cacher un identifiant mais révéler des montants, des heures ou des relations de transaction qui permettent de relier une activité. Une preuve peut rester cryptographiquement sûre tout en étant insuffisante contre une analyse de graphe ou une corrélation avec des données publiques.

Écris un modèle d'adversaire : observe-t-il la blockchain, l'API, les logs d'application, le réseau IP, les adresses de portefeuille ou les données d'identité ? Peut-il combiner plusieurs sources ? Quel lien cherche-t-il à établir ? Les protections doivent correspondre à ces hypothèses. Une propriété ZK ne protège pas nécessairement les métadonnées réseau, le temps d'exécution du prouveur ou les informations demandées par une interface.

La minimisation est souvent aussi importante que la cryptographie. Ne publie que les entrées nécessaires à la vérification. Évite les identifiants réutilisés lorsqu'ils permettent de relier des actions, mais ne suppose pas que changer d'adresse suffit à rendre un utilisateur anonyme. Les modèles de menaces réalistes considèrent aussi les tailles de transaction, les fréquences et les montants.

## 11. Confidentialité et conformité ne s'annulent pas

Les preuves ZK peuvent démontrer certaines propriétés sans révéler tout le dossier sous-jacent. Par exemple, une application peut chercher à prouver qu'une personne répond à un critère d'éligibilité sans publier son document complet. La déclaration doit cependant être précise : prouver qu'une attestation a été signée par une autorité n'est pas la même chose que prouver que l'autorité a effectué une vérification correcte.

La conformité juridique dépend du contexte, des données, des utilisateurs, des juridictions et du rôle de l'application. Une preuve cryptographique ne garantit pas à elle seule que le traitement de données est conforme à toutes les obligations. Les équipes doivent considérer la minimisation, la rétention, les droits d'accès et les recours sans supposer que la confidentialité cryptographique répond à toutes les questions.

Le design doit également examiner les informations nécessaires aux audits légitimes, à la résolution des erreurs et aux procédures de contestation. L'équilibre entre confidentialité, responsabilité et exigences opérationnelles dépend de l'application et doit être documenté par des responsables compétents.

## 12. Coût et expérience de génération de preuve

La génération d'une preuve peut exiger du CPU, de la mémoire, du temps et parfois du matériel spécialisé. Si l'utilisateur doit attendre longtemps ou exécuter un calcul lourd sur mobile, l'expérience peut devenir difficile. Un service distant de génération peut améliorer l'ergonomie, mais il reçoit alors des données ou un témoin et ajoute une nouvelle frontière de confiance.

Le design peut séparer la préparation locale du témoin, la génération de preuve et la vérification. Si un service externe reçoit le témoin, il faut déterminer quelles données il peut apprendre et comment le secret est transmis. Si la génération est locale, mesure la mémoire, le temps, les erreurs et la compatibilité des appareils. Si la preuve est générée côté serveur, analyse le contrôle d'accès et les journaux.

La vérification on-chain consomme généralement des ressources tarifées par le réseau, tandis que la vérification hors chaîne dépend des ressources de l'application. Le choix du système de preuve influe sur la taille et le coût de vérification. Il faut benchmarker le scénario réel, y compris la préparation des données et la gestion des échecs.

## 13. Erreurs de conception et d'implémentation

Les erreurs peuvent se situer dans le circuit, le vérificateur, les bibliothèques, le format des entrées, la sérialisation des valeurs, les paramètres publics ou la logique de contrat qui consomme la preuve. Un champ qui est supposé limité mais qui n'est pas contraint peut permettre des valeurs inattendues. Une conversion d'entier peut être interprétée différemment entre l'application et le circuit.

Les tests doivent couvrir les preuves valides, les témoins incorrects, les entrées publiques modifiées, les preuves altérées, les preuves répétées et les valeurs proches des limites. Vérifie également que le vérificateur rejette un résultat construit pour une autre déclaration ou un autre contexte. Les tests d'intégration doivent confirmer que le contrat interprète correctement l'acceptation de la preuve et ne saute pas des contrôles métier nécessaires.

Ne construis pas de primitives cryptographiques personnalisées pour la production. Utilise des outils connus, vérifie leur documentation et leur version, fais examiner les circuits et les contrats, et conserve des tests reproductibles. Les bibliothèques réduisent certains risques mais ne remplacent pas la spécification de la relation que le système doit prouver.

## 14. TP guidé A : spécifier une preuve de connaissance d'un secret

Imagine un système où l'utilisateur doit démontrer qu'il connaît un secret associé à un engagement public. Décris ce qui est public, ce qui est privé, la relation à vérifier, le résultat public et la manière dont l'application empêcherait le même droit d'être utilisé deux fois. Ne code pas de système cryptographique personnalisé.

### Correction proposée

La déclaration doit inclure l'engagement connu, le secret privé, le calcul permettant de lier les deux et le contexte exact. Si une propriété d'appartenance est requise, la preuve doit aussi vérifier le chemin de Merkle et la racine acceptée. Si une utilisation unique est nécessaire, le système doit définir un nullifier contextualisé et vérifier qu'il n'a pas déjà été consommé. La correction doit explicitement signaler que l'exemple décrit une spécification conceptuelle, pas un système de production.

## 15. TP guidé B : analyser les fuites de métadonnées

Construis un tableau de toutes les données publiques d'une application : adresses, montant, heure, racine d'engagement, nullifier, taille de preuve, événement et appel RPC. Pour chaque élément, demande si un observateur peut le corréler avec une autre source, et si cette information est nécessaire à la vérification.

### Correction proposée

Une analyse de confidentialité utile décrit l'adversaire et les liaisons possibles. Elle ne se contente pas de dire que le témoin est privé. Elle propose de minimiser les entrées publiques, d'éviter les identifiants réutilisés lorsqu'ils n'ont pas de raison d'être stables, de protéger les logs et d'examiner le comportement réseau du prouveur.

## 16. Étude de cas : preuve correcte, confidentialité insuffisante

Une application génère une preuve qui établit correctement qu'un utilisateur satisfait un critère d'éligibilité. L'équipe constate toutefois que les transactions des utilisateurs sont faciles à relier, car la même adresse et le même identifiant apparaissent dans les événements publics. Le produit affirme que les données sont privées parce que les preuves sont de type ZK.

### Travail demandé

Distingue la validité cryptographique de la confidentialité du produit, dresse les données publiques, formule un modèle d'adversaire et propose des mesures qui minimisent la liaison entre actions sans casser les règles métier.

### Correction proposée

La preuve peut être correcte selon la relation encodée tout en révélant des identifiants de corrélation. Il faut examiner les événements, les adresses, les valeurs réutilisées et les données hors chaîne. Les corrections peuvent inclure la minimisation des données publiques, un identifiant contextualisé, une meilleure gestion des événements et la protection des logs. Toute évolution doit vérifier que les règles d'anti-rejeu et les obligations métier restent satisfaites.

## 17. Arithmétisation : transformer un programme en contraintes

Un système de preuve ne vérifie pas une intuition exprimée en prose ; il vérifie une relation formelle. L'arithmétisation consiste à représenter le calcul sous une forme adaptée au système de preuve choisi. Certaines constructions utilisent des contraintes d'égalité sur un corps fini ; d'autres s'appuient sur des polynômes, des engagements et des vérifications de cohérence. Le détail mathématique varie, mais l'idée opérationnelle est la même : le circuit doit représenter exactement le calcul que l'application prétend prouver.

Une traduction incorrecte peut être plus dangereuse qu'un bug de code conventionnel. Par exemple, un programme classique peut vérifier qu'une valeur est comprise entre deux bornes, mais le circuit doit véritablement contraindre la représentation de la valeur, son interprétation et les opérations qui la produisent. Si une comparaison est modélisée uniquement comme une relation modulo un corps fini, les propriétés d'ordre des entiers ne sont pas automatiquement obtenues. Il faut que le circuit encode les bornes et la représentation attendues.

Les développeurs doivent comprendre le modèle des variables, les conversions, la largeur des entiers et les opérations autorisées par le langage de circuit. Les valeurs public/private doivent être identifiées dans la spécification, et les contraintes doivent empêcher les valeurs invalides. Les outils de compilation du circuit peuvent aider à révéler des contraintes absentes ou des chemins de données inattendus, mais une revue humaine reste nécessaire.

Une bonne pratique consiste à écrire d'abord les propriétés du calcul sous forme mathématique et d'ajouter des tests de contre-exemple. Les tests incluent des valeurs à la frontière, des valeurs maximales, des champs absents et des représentations non canoniques. Ensuite, vérifie que l'implémentation de référence, le générateur de preuve et le vérificateur utilisent tous le même sens des entrées.

## 18. Contraintes absentes et preuve d'une mauvaise déclaration

Une preuve peut satisfaire toutes les contraintes du circuit alors que la déclaration métier visée n'est pas correctement encodée. C'est la raison pour laquelle les circuits doivent être audités comme du code de sécurité critique. Une contrainte absente peut rendre possible une valeur qui ne devrait pas être acceptable, et une contrainte mal liée peut permettre à un champ public de ne pas correspondre au témoin.

La revue devrait associer chaque exigence fonctionnelle à une ou plusieurs contraintes. Pour chaque relation, demande quel champ la satisfait, si elle est toujours active et si elle peut être contournée par une représentation alternative. Les propriétés de nullifier, de validité d'une signature, de chemin de Merkle et de domaine de réseau devraient être explicitement liées aux entrées publiques.

Les tests négatifs devraient construire des témoins qui violent une règle à la fois. Par exemple, une signature incorrecte, une racine inconnue, un témoin qui ne correspond pas à l'engagement, un nullifier déjà consommé ou un contexte d'application différent. Le résultat attendu est un échec de génération ou un rejet du vérificateur. Si une preuve est acceptée, l'équipe doit déterminer si le test était invalide ou si le circuit n'a pas encodé la règle.

Les tests aléatoires et l'analyse automatisée peuvent aider à découvrir des contre-exemples, mais ils n'examinent pas nécessairement toutes les propriétés sémantiques. Il est préférable de combiner un modèle de menace, une spécification écrite, des tests ciblés, la revue du code de circuit et une revue indépendante pour les applications à haut risque.

## 19. Engager des données et cacher un membre d'un ensemble

Un engagement peut permettre à une application de publier une racine ou une empreinte d'une valeur sans divulguer immédiatement cette valeur. Dans un système de confidentialité, le prouveur peut démontrer qu'il connaît un élément qui correspond à l'engagement ou appartient à un ensemble approuvé. Le vérificateur reçoit une racine publique et une preuve qui montre que le témoin respecte la relation.

Les arbres de Merkle sont souvent utilisés pour représenter des ensembles de valeurs. Un chemin d'inclusion contient les informations nécessaires pour relier une feuille à une racine, sans publier toutes les autres feuilles. Dans le circuit, il faut vérifier chaque étape du chemin selon la fonction de hachage et l'ordre des éléments. Un chemin erroné doit échouer, et une mise à jour de racine doit être liée à la version ou à l'ensemble auquel le système fait confiance.

L'appartenance à un ensemble n'implique pas nécessairement que l'élément est encore autorisé. Une attestation peut être révoquée, une liste peut être actualisée et une identité peut expirer. Le système doit inclure la version de liste, une preuve de non-révocation ou une autre règle appropriée. Si une ancienne racine reste acceptée sans limite, une autorisation obsolète pourrait encore fonctionner.

Les engagements doivent aussi gérer l'unicité. Certaines constructions ajoutent un secret aléatoire afin qu'un observateur ne puisse pas tester un petit ensemble de valeurs en calculant leurs empreintes. Une valeur déterministe trop prévisible peut permettre une attaque par dictionnaire. Le design doit analyser la résistance à ce type d'inférence ainsi que la disponibilité du secret nécessaire pour ouvrir l'engagement.

## 20. SNARK et STARK : critères d'évaluation concrets

Pour comparer des systèmes de preuve, commence par le calcul à prouver, la fréquence des preuves, la taille du témoin et les contraintes du vérificateur. Ensuite, mesure le temps de génération, la mémoire maximale, la taille de preuve, le coût de vérification et le coût de mise à jour de la déclaration. Le système le plus rapide sur un micro-benchmark peut être mauvais pour une application qui doit fonctionner sur téléphone ou vérifier un grand nombre de preuves sur chaîne.

Les exigences de setup doivent être décrites précisément. Certaines constructions SNARK nécessitent une configuration de paramètres commune dont la sécurité dépend de la procédure et d'hypothèses sur le matériel secret. D'autres constructions reposent sur des paramètres transparents ou des hypothèses différentes. Les STARK sont connus pour leur transparence et leurs propriétés d'échelle dans certaines familles, mais les preuves peuvent être plus volumineuses et le coût de vérification différent. Aucun acronyme ne remplace un benchmark et une analyse cryptographique.

La maturité de l'écosystème est un facteur opérationnel : disponibilité d'outils, qualité des diagnostics, facilité de revue, stabilité du format des preuves, documentation, audits et maintenance. Un système avec de très bonnes propriétés théoriques mais un outil mal compris peut être mal utilisé. Il faut également déterminer le risque de dépendance à un fournisseur de preuve ou à une bibliothèque peu maintenue.

Le rapport de comparaison doit séparer les mesures observées, les hypothèses de modèle et la conclusion. Il ne doit pas déclarer qu'un système est plus sûr simplement parce qu'il est plus récent ou parce que la preuve est plus petite. La sécurité dépend aussi des paramètres, du circuit, du vérificateur et de la façon dont l'application utilise la preuve.

## 21. Concevoir une confidentialité avec un adversaire explicite

La confidentialité n'est pas un seul niveau universel. Un protocole peut protéger le contenu du témoin contre un vérificateur, mais révéler l'identité réseau à un fournisseur de calcul. Un système peut cacher le montant exact mais publier une borne, une catégorie ou un événement qui réduit les valeurs possibles. Une application peut protéger les données on-chain sans protéger la base de données du service qui génère les preuves.

Écris les adversaires et leurs capacités. Un observateur public peut lire les transactions, les événements et les horaires. Un fournisseur RPC peut connaître les adresses interrogées et le contexte réseau. Un service de preuve distant peut recevoir le témoin. Un opérateur d'interface peut disposer de logs et d'identifiants de session. Un membre malveillant peut soumettre des entrées conçues pour révéler un comportement. Les mesures doivent couvrir ces canaux de fuite.

Les menaces incluent la corrélation entre opérations, l'analyse de montant, les attaques par dictionnaire sur des engagements prévisibles, les erreurs de journalisation, les messages d'erreur distinctifs et les temps de calcul. Certaines fuites peuvent être réduites par la minimisation, la séparation des domaines, la standardisation des réponses et le contrôle des logs. D'autres exigent une architecture différente ou des compromis d'ergonomie.

Une note de confidentialité doit annoncer ce qui est protégé, ce qui est public, qui peut l'observer, combien de temps les données sont conservées et quelles inférences demeurent possibles. Évite les affirmations absolues du type « impossible à tracer » si le système ne protège pas tous les canaux. Une description précise permet à l'utilisateur de prendre une décision informée.

## 22. Révocation, mises à jour et preuves historiques

Une application qui utilise des attestations ou des listes d'éligibilité doit définir ce qui se produit lorsqu'un élément est révoqué. Si la preuve fait référence à une racine historique, l'utilisateur peut encore démontrer l'appartenance à l'ancien ensemble. Il faut choisir si la décision doit se baser sur une racine immuable, sur une version active ou sur une preuve de non-révocation.

Les mises à jour créent une tension entre stabilité et fraîcheur. Une preuve qui est liée à un snapshot historique est plus facile à reproduire, mais elle ne connaît pas les événements postérieurs. Une preuve qui exige l'état le plus récent peut nécessiter une requête ou une mise à jour supplémentaire. La spécification doit préciser la période de validité, la version de clé, le contexte et le comportement en cas d'indisponibilité du service de mise à jour.

Les mécanismes de révocation ne doivent pas révéler inutilement les raisons ou données personnelles de la révocation. Une preuve de statut peut être conçue pour cacher la valeur ou l'identité sous-jacente, mais la construction doit être analysée pour les fuites de métadonnées. Il faut aussi définir l'autorité qui publie la révocation, le moyen de contester une erreur et le comportement lorsqu'une autorité est compromise.

Les tests couvrent une preuve fondée sur une racine actuelle, une racine ancienne, une attestation expirée, une révocation et un changement de clé. Ils vérifient que l'application applique la politique écrite et qu'elle n'accepte pas silencieusement une donnée obsolète.

## 23. Opération en production : déploiement, monitoring et incident

Le déploiement d'un système ZK doit archiver les versions du circuit, des bibliothèques, des paramètres, du prouveur, du vérificateur et des scripts de génération. La déclaration publique doit rester alignée entre le calcul client, le générateur de preuve et le contrat. Si une version change la relation mathématique, une preuve ancienne peut ne plus représenter la même propriété et les intégrations doivent être migrées explicitement.

Surveille les taux de preuve réussie, le temps de génération, la mémoire, les erreurs de vérification, les versions de paramètres et les échecs par type d'entrée. Ne collecte pas les témoins dans les logs pour faciliter le diagnostic, sauf si une méthode de protection, de consentement et de minimisation a été explicitement conçue. Les preuves échouées peuvent être diagnostiquées avec des identifiants de requête et des métadonnées minimisées.

Une panne de prouveur ne doit pas inciter à accepter une vérification plus faible. Si la preuve ne peut pas être générée, le produit peut retenter selon une politique sûre ou présenter une indisponibilité temporaire. Un mode de secours doit préserver les garanties de la déclaration ; désactiver le contrôle parce que l'outil est en panne transforme un incident d'expérience en faille de sécurité.

Un incident cryptographique exige de préserver les versions et les preuves de test, de déterminer si le défaut concerne le circuit, le vérificateur, les paramètres ou l'application et de coordonner la correction. Toute nouvelle version devrait être retestée avec des preuves légitimes et adverses. La reprise s'appuie sur des critères vérifiables, pas seulement sur le retour du service en ligne.

## 24. Gestion des clés, des preuves et des paramètres en production

Un système ZK dépend de plusieurs artefacts : source du circuit, version du compilateur, paramètres, clés de vérification, format de preuve, contrats et scripts qui préparent les entrées. Les artefacts doivent être versionnés et reliés entre eux par des identifiants ou hashes vérifiables. Une preuve peut être valide pour une relation et des paramètres donnés, mais ne doit pas être acceptée si elle est interprétée avec une déclaration différente.

La chaîne d'approvisionnement du logiciel doit distinguer la source du circuit, le circuit compilé et le vérificateur déployé. Un changement minime du circuit peut modifier la relation prouvée. Le pipeline doit donc produire un artefact reproductible et exécuter des tests de référence et des tests négatifs avant de publier une nouvelle version. Les clés ou paramètres secrets éventuels doivent être séparés des artefacts publics, et l'accès doit être contrôlé.

Le monitoring doit enregistrer la version du circuit, le temps de génération, le résultat du vérificateur, les types d'échecs, le coût de vérification et la fréquence d'erreurs. Ne journalise pas le témoin par défaut pour faciliter le support. Si une enquête exige de reproduire une preuve, utilise des données synthétiques ou un processus qui respecte le modèle de confidentialité et l'autorisation des utilisateurs.

La rotation des clés et la mise à niveau du vérificateur doivent être traitées comme des changements de sécurité. Vérifie l'ancien et le nouveau contexte, les preuves en attente, les formats et les règles d'expiration. La procédure de reprise doit établir la compatibilité, éviter les rejeux et permettre de diagnostiquer les erreurs sans assouplir la validation.

## 25. Risque de side-channel et comportement temporel

Une preuve peut cacher le témoin dans son contenu cryptographique sans empêcher tous les canaux auxiliaires. Le temps de génération, la quantité de mémoire, les messages d'erreur, l'utilisation du réseau et la taille des données peuvent révéler des informations sur les entrées. Le risque varie selon le matériel, l'implémentation et l'adversaire considéré. Il ne faut pas déclarer ces canaux présents ou absents sans analyse.

Si une preuve est calculée sur l'appareil de l'utilisateur, examine si le temps ou l'utilisation des ressources dépend des secrets. Si le calcul est confié à un serveur, la confidentialité dépend également des données envoyées au serveur, de ses journaux et de son modèle d'accès. Une implémentation peut réduire certaines fuites avec des comportements plus uniformes, une minimisation des données, un contrôle des erreurs ou une architecture de calcul différente.

Les erreurs doivent être formulées avec prudence. Une réponse qui indique explicitement si un secret existe peut permettre des tests répétés. Une API qui distingue plusieurs catégories de refus peut révéler des propriétés des données privées. Le protocole doit déterminer quelles différences sont nécessaires au fonctionnement et lesquelles peuvent être réduites.

Les tests de side-channel sont spécialisés. Un test fonctionnel qui confirme l'acceptation ou le rejet d'une preuve ne permet pas de conclure que les temps d'exécution ne révèlent rien. Pour un système à haute sensibilité, inclue une revue des canaux auxiliaires dans le périmètre de sécurité et décris clairement ses limites.

## 26. Données publiques minimales et conception de schéma

Les entrées publiques doivent contenir uniquement les données nécessaires à la vérification et à l'intégration. Chaque valeur publique peut devenir une clé de corrélation. Un identifiant logique, une racine de Merkle, un montant, une période ou une étiquette de catégorie peut réduire l'ensemble des possibilités pour un observateur. Avant d'ajouter un champ au contrat, demande s'il est nécessaire, quelle information il permet d'inférer et s'il peut être fourni par un mécanisme moins exposant.

La minimisation n'est pas une simple suppression de champs. Elle doit préserver la logique métier. Si le vérificateur doit prouver qu'une transaction correspond à un réseau donné, l'identifiant du domaine peut être essentiel pour empêcher le rejeu. La solution correcte n'est pas de le retirer, mais de vérifier que sa sémantique et son exposition sont comprises. Une preuve ZK ne doit pas masquer un champ indispensable à la sécurité.

Une analyse de schéma peut classer les entrées comme nécessaires, optionnelles ou dérivées. Pour chaque donnée dérivée, demande si elle peut être calculée localement ou incluse dans une relation sans publier sa source. Pour les données optionnelles, mesure le coût de leur suppression. Pour les données nécessaires, documente le risque de corrélation et les usages prévus.

Les versions du schéma et du circuit doivent évoluer ensemble. Une mise à jour qui change la signification d'une entrée publique peut entraîner une interprétation différente par les anciennes applications. Le pipeline doit vérifier que les versions incompatibles sont refusées et que l'interface affiche clairement la déclaration utilisée.

## 27. Expiration, rejeu et gestion d'un droit à usage unique

Une preuve peut continuer à être valide mathématiquement même lorsque le droit qu'elle décrit a expiré. Le protocole doit donc lier la déclaration à une période, une version ou un état de révocation lorsqu'une fraîcheur est requise. Le vérificateur peut recevoir une époque publique ou un identifiant de contexte et contrôler qu'il correspond aux paramètres attendus.

Pour empêcher les usages multiples, le système peut publier un nullifier ou consommer un identifiant d'action. La valeur doit être liée au domaine correct afin qu'une utilisation sur une application ou une chaîne ne permette pas nécessairement de relier ou de réutiliser le droit ailleurs. Le design doit aussi considérer les mises à niveau : une nouvelle version du contrat ne doit pas effacer l'historique des nullifiers consommés si cela permet le rejeu.

Écris des tests de frontière temporelle : juste avant l'expiration, exactement à la limite, juste après et avec une référence de temps obsolète. Ajoute des tests où une preuve est soumise deux fois, sur un autre contrat, sur une autre chaîne ou sous une autre version de déclaration. Le résultat attendu doit être clairement défini pour chaque contexte.

Le comportement de panne compte. Si le service qui fournit la version actuelle est indisponible, le système ne doit pas utiliser silencieusement une époque ancienne si cela augmente le risque. Il peut refuser temporairement l'opération ou utiliser un état de secours documenté, selon le modèle du protocole.

## 28. Tester la solidité de la déclaration métier

Un circuit peut être mathématiquement cohérent sans démontrer la propriété que le produit pense utiliser. Pour éviter ce décalage, écris un document qui relie la déclaration naturelle aux variables publiques, au témoin, aux contraintes et au résultat attendu. Chaque règle métier critique doit être représentée dans les contraintes ou dans un contrôle de vérification explicitement séparé.

Construis ensuite des contre-exemples. Si la déclaration exige un âge minimum, teste la valeur juste sous le seuil, au seuil et juste au-dessus. Si elle exige une signature d'une autorité, teste une signature d'une autre autorité, une mauvaise clé, un message qui change de domaine et des données qui ont été modifiées après signature. Si elle exige un chemin de Merkle, teste une racine différente, une feuille différente et un chemin de longueur incorrecte.

L'exécution de tests doit comparer la sortie du système de référence, celle du prouveur et le résultat du vérificateur. Les différences doivent être expliquées. Si le vérificateur accepte une preuve mais que l'application interprète les entrées différemment, le défaut peut exister hors du circuit. Les tests d'intégration doivent donc couvrir les conversions, les formats, les limites de taille et la sérialisation.

La revue du code de circuit doit être indépendante des tests lorsque l'impact est important. Une analyse automatisée peut être utile, mais seule une compréhension de la déclaration permet d'évaluer si le bon calcul est prouvé. La conclusion doit préciser les hypothèses cryptographiques et les comportements qui n'ont pas été couverts.

## 29. Confidentialité et expérience de récupération

Un produit confidentiel doit rester utilisable lorsque la génération de preuve échoue. L'interface doit expliquer que la preuve n'a pas pu être produite ou vérifiée, sans dévoiler d'informations privées ni demander à l'utilisateur de soumettre le témoin en clair au support. Les erreurs doivent être suffisamment informatives pour permettre le diagnostic, mais pas révéler inutilement quelle condition secrète a échoué.

Le système doit définir comment l'utilisateur conserve les éléments nécessaires à la récupération : clés, engagements, secrets de nullifier, attestations et données qui permettent de reconstruire une preuve. Si ces éléments sont perdus, l'utilisateur peut perdre la capacité de démontrer un droit même si le contrat et l'état public existent encore. La sauvegarde doit être sécurisée et le processus de récupération testé.

La récupération doit aussi éviter la corrélation excessive. Un identifiant de ticket unique peut relier plusieurs sessions si la même valeur est réutilisée. Le support devrait utiliser des identifiants de corrélation techniques qui n'exposent pas le secret et qui ne sont pas publiés sur la chaîne. Les logs doivent être minimisés et la politique de rétention connue.

Pour un incident, collecte la version des outils, le type d'erreur, l'identifiant de requête, les entrées publiques et les paramètres nécessaires. Ne demande pas le témoin secret sauf si un protocole sûr, autorisé et explicitement conçu l'exige. Le mode de secours doit maintenir les mêmes propriétés de sécurité essentielles ; désactiver la vérification ne constitue pas une solution de disponibilité acceptable.

## 30. Concevoir des critères de validation et une matrice de preuves

Un projet ZK devrait relier les exigences produit à des propriétés vérifiables. Pour chaque règle, indique la déclaration, les entrées publiques, les éléments du témoin, les contraintes qui l'encodent, le vérificateur qui l'applique et les tests qui démontrent le comportement attendu. Une phrase d'exigence sans lien vers le circuit ou les contrôles applicatifs risque de rester une intention non vérifiée.

La matrice devrait inclure les propriétés de sécurité — solidité de la déclaration, séparation de domaine, non-réutilisation d'un droit — et les propriétés de confidentialité — absence de divulgation directe du témoin, minimisation des entrées et limitation des corrélations inutiles. Elle doit aussi inclure les aspects d'exploitation : contrôle des paramètres, versions, sauvegarde des données nécessaires et procédure de reprise si le prouveur est indisponible.

Pour chaque test, conserve la version de circuit, la version du compilateur, les paramètres de génération, les entrées publiques et un résultat de test reproductible. Les témoins privés ne doivent pas être placés dans un rapport partagé sans justification et protections explicites. Des données synthétiques peuvent souvent reproduire un bug sans exposer des données sensibles réelles.

La revue doit être capable de répondre à une question précise : si une preuve est acceptée, quelle propriété peut-on conclure exactement ? Si la réponse dépend d'une hypothèse, note cette hypothèse. Si elle dépend d'une autorité d'attestation, examine cette autorité. Si elle dépend d'un état actuel, vérifie la fraîcheur et la version de cet état. La preuve doit être interprétée comme la garantie encodée, pas comme une certification générale du produit.

## 31. Tester une mise à niveau du circuit sans casser les anciennes preuves

Une nouvelle version de circuit peut ajouter une contrainte, changer une entrée publique ou modifier la relation métier. Ces évolutions peuvent rendre les anciennes preuves incompatibles ou, plus dangereusement, conduire des systèmes différents à interpréter les mêmes données différemment. La migration doit définir si les anciennes preuves restent acceptées, pendant combien de temps et dans quel domaine.

Prépare des vecteurs de test communs pour l'ancienne version et la nouvelle : preuves valides, preuves invalides, valeurs limites, entrées publiques différentes et scénarios de rejeu. Compare les résultats et documente toute divergence. Les preuves historiques peuvent avoir une valeur d'audit ; la conservation de leur version, de leurs paramètres et de la déclaration d'origine permet d'expliquer pourquoi elles ont été acceptées à l'époque.

Le vérificateur doit lier la preuve au contexte de version attendu. Une preuve d'une ancienne déclaration ne doit pas être interprétée comme si elle démontrait les règles nouvelles, sauf si une équivalence a été explicitement démontrée. Les applications clientes doivent aussi empêcher les erreurs de compatibilité et afficher clairement quelle version utilise chaque opération.

Le plan de publication comprend la compilation, la vérification des paramètres, la revue du contrat, la simulation de migration et le suivi post-déploiement. Les critères de clôture sont les résultats de tests, la cohérence des versions et la confirmation que les preuves en attente sont traitées selon la règle choisie. Une mise à niveau de circuit est un changement de sécurité, pas un simple changement de performance.

## 32. Étude de cas : fuite par corrélation malgré un témoin secret

Un système prouve que chaque utilisateur possède une attestation valide sans publier son contenu. L'application utilise toutefois le même identifiant stable dans plusieurs transactions, et les heures de soumission sont suffisamment spécifiques pour relier plusieurs actions. L'équipe constate qu'un observateur peut inférer qu'un même compte a participé à des événements différents.

### Travail demandé

Énumère les données qui restent publiques, distingue les fuites on-chain et hors chaîne, propose une matrice d'adversaires et identifie les changements qui réduiraient la corrélation tout en préservant les propriétés anti-rejeu.

### Correction proposée

La preuve peut satisfaire sa propriété ZK tout en permettant une corrélation à travers les entrées publiques. Il faut examiner les identifiants, les événements, les heures, les métadonnées de réseau et les logs du service de preuve. Un changement de schéma peut réduire les identifiants stables ou contextualiser certains nullifiers, mais il doit conserver la prévention du rejeu et la vérifiabilité de la déclaration.

La réponse doit faire la différence entre corrélation certaine et inférence probabiliste, puis mesurer l'effet de la correction. Les interfaces et les logs doivent être revus, car une protection qui ne couvre que les entrées on-chain ne répond pas au scénario si un fournisseur hors chaîne détient encore le lien entre sessions.

## 33. Mettre en place une revue cryptographique indépendante

Une revue indépendante doit préciser la portée : déclaration métier, circuit, compilateur, système de preuve, paramètres, vérificateur, contrat consommateur, sérialisation des données et chemins de récupération. Le rapport doit nommer les versions et les hypothèses. Un examen limité au contrat ne peut pas conclure que le circuit prouve la propriété attendue, et un examen limité au circuit ne peut pas valider toutes les permissions du protocole.

Les questions principales incluent : le circuit encode-t-il toutes les contraintes attendues ? Les valeurs sont-elles bornées et interprétées correctement ? Les paramètres sont-ils authentiques ? Le vérificateur accepte-t-il uniquement la déclaration et le domaine attendus ? Les preuves peuvent-elles être rejouées ? Quelles informations sont divulguées par les entrées publiques et les métadonnées ? Les changements de version sont-ils traçables ?

Les constats doivent inclure un contre-exemple ou une preuve claire lorsque possible, une mesure d'impact et la limite d'applicabilité. Les corrections doivent être testées à nouveau sur le cas d'origine et sur les chemins voisins. Pour un système à forte valeur, une revue devrait aussi examiner le modèle économique et les services hors chaîne, pas uniquement les propriétés mathématiques.

La décision de mise en production doit documenter les risques résiduels et les conditions de réévaluation. Une preuve peut être solide sous une hypothèse mais la plateforme peut rester vulnérable à une erreur de gestion de clés, une fuite de témoin ou une mauvaise configuration. La conclusion doit rester proportionnée à la portée réelle de l'examen.

## 34. Établir un modèle de confidentialité pour chaque donnée

Une revue de confidentialité devrait commencer par un inventaire : témoin, entrées publiques, métadonnées de transaction, identifiants de corrélation, données du portefeuille, journaux du prouveur, données d'indexeur et copies d'attestation. Pour chaque catégorie, indique qui peut la voir, dans quel contexte, pendant combien de temps et quelles conclusions un observateur pourrait en tirer.

Il faut distinguer trois propriétés. La confidentialité cryptographique concerne ce que la preuve révèle sur le témoin. La confidentialité opérationnelle concerne les données reçues et conservées par les services qui génèrent, vérifient ou indexent les preuves. La confidentialité comportementale concerne les liens que l'on peut déduire des horaires, fréquences et motifs d'utilisation. Un projet peut respecter la première propriété tout en échouant sur les deux autres.

Construis un tableau des menaces et des contrôles. Une fuite directe de témoin appelle une protection des flux, des logs et des API. Une corrélation entre transactions peut exiger une minimisation des identifiants ou une modification des événements. Une attaque par dictionnaire peut nécessiter un engagement avec une valeur aléatoire adaptée. Un risque d'expiration demande une règle de fraîcheur. Chaque contrôle doit conserver les propriétés de vérification et d'anti-rejeu attendues.

Le rapport doit aussi dire ce que la conception ne protège pas. Si le service RPC peut associer une adresse IP à une adresse de portefeuille, le circuit ZK ne supprime pas cette observation. Si un utilisateur publie volontairement son identité ailleurs, la blockchain peut permettre de relier certaines activités. Une description honnête de la confidentialité évite de transformer une garantie ciblée en promesse d'anonymat total.

## 35. Test de non-régression des propriétés cryptographiques

Après chaque changement du circuit, du compilateur ou des paramètres, réexécute une suite de tests qui comprend des preuves valides, des témoins invalides, des entrées publiques altérées, des valeurs frontières, des signatures incorrectes et des tentatives de rejeu. Compare les résultats avec la version précédente et explique toute différence. Les nouvelles versions ne doivent pas simplement « passer » ; elles doivent préserver les propriétés intentionnelles et documenter les changements voulus.

Conserve des vecteurs de test reproductibles et non sensibles. Pour les propriétés qui touchent au témoin, utilise des données synthétiques. Archive le hash des artefacts, la configuration du prouveur, la version de la bibliothèque et le statut du vérificateur. Si une preuve historique doit rester vérifiable, conserve sa relation avec la déclaration et les paramètres d'origine.

Le pipeline devrait échouer si les artefacts ne correspondent pas aux versions approuvées, si le vérificateur n'est pas généré à partir du code attendu ou si un test critique est absent. Une compilation réussie ne garantit pas l'équivalence sémantique. Une revue indépendante est utile après une modification qui touche aux contraintes, aux entrées publiques ou aux paramètres de confiance.

Un test de sécurité doit examiner le contrat consommateur. Même si le vérificateur accepte uniquement des preuves valides, l'application peut mal traiter le résultat ou ignorer une condition métier. Vérifie les permissions, le contexte, le domaine, le nullifier et les effets d'état après l'acceptation. Le résultat attendu est une chaîne de preuves reproductible qui relie le circuit au comportement réel du produit.

~~~mermaid
flowchart LR
    A[Exigence métier] --> B[Relation formelle]
    B --> C[Circuit et compilation]
    C --> D[Vecteurs valides et invalides]
    D --> E[Vérificateur et contrat consommateur]
    E --> F[Revue des fuites et du rejeu]
    F --> G[Artefacts versionnés et approuvés]
~~~

## 36. Concevoir les journaux sans révéler le témoin

Les journaux opérationnels sont nécessaires pour diagnostiquer les erreurs de génération et de vérification, mais ils peuvent devenir une voie de fuite. Il faut décider quelles données sont utiles pour le support : identifiant de requête, version du circuit, type d'erreur, temps de génération, taille de preuve et statut de vérification. Le témoin, les secrets d'identité et les données sensibles doivent être exclus par défaut.

Un identifiant de corrélation peut lui-même révéler une relation si la même valeur est réutilisée entre services ou publiée sur chaîne. La politique de logs doit donc considérer les identifiants persistants, les adresses, les timestamps et les détails de la requête. Les données indispensables à un diagnostic doivent être minimisées, protégées, retenues pour une durée définie et accessibles uniquement aux rôles autorisés.

Les erreurs détaillées peuvent également permettre de déduire une propriété secrète. Si l'API répond différemment selon que la preuve échoue à une condition particulière, un adversaire peut envoyer des requêtes répétées pour apprendre des informations. Examine ce que le modèle de menace permet à l'utilisateur ou au service de mesurer, et détermine quelles différences de réponse sont nécessaires à l'exploitation.

La procédure de support devrait utiliser des cas synthétiques chaque fois que possible. Si une enquête doit utiliser des données réelles, elle exige une autorisation, un accès limité, une méthode de partage sécurisée et une suppression contrôlée des copies de travail. Le but est de rendre les incidents reproductibles sans transformer la télémétrie en second canal de divulgation.

## 37. Vérifier l'interface entre le prouveur et le contrat

L'interface entre le prouveur, le sérialiseur et le contrat vérificateur est une frontière critique. Les champs doivent avoir la même signification, le même ordre, les mêmes unités et les mêmes conventions de représentation dans toutes les couches. Une erreur de format peut conduire à un rejet légitime ou, dans un cas plus grave, à vérifier une déclaration différente de celle que l'application croit soumettre.

Les tests d'intégration doivent partir d'une entrée métier, produire les données de témoin et les entrées publiques, générer une preuve puis soumettre l'appel à un vérificateur local ou de test. Vérifie ensuite l'état du contrat, les événements et la gestion d'un rejeu. Les tests doivent inclure les champs hors limite, les valeurs manquantes, les conversions et les identifiants de version.

Lors d'une mise à jour, compare explicitement l'ABI, le format de preuve, les paramètres, les constantes de domaine et les règles de nullifier. Le client doit détecter une incompatibilité plutôt que choisir silencieusement un chemin de vérification différent. Archive les artefacts générés et les données de test non sensibles afin qu'une autre équipe puisse reproduire l'intégration.

Une revue utile associe chaque étape à une propriété. Le prouveur doit générer la preuve pour la relation attendue ; le sérialiseur doit transmettre les mêmes entrées ; le vérificateur doit authentifier la déclaration et le contexte ; le contrat consommateur doit appliquer l'effet métier et empêcher les répétitions. Une preuve mathématiquement valide n'est que l'un des éléments de la chaîne de sécurité.

## 38. Checklist de publication d'une fonctionnalité ZK

Avant la mise en production, confirme que la relation métier est écrite, que les entrées publiques et le témoin sont documentés, que les contraintes du circuit ont été revues, que les paramètres et versions sont épinglés et que les tests négatifs couvrent les frontières, le contexte et le rejeu. La génération et la vérification doivent être compatibles et reproductibles dans l'environnement décrit.

Vérifie les données hors chaîne : le prouveur, le RPC, l'interface, les journaux, les sauvegardes et les services d'attestation. Identifie ce que chacun peut observer, la durée de rétention et les personnes autorisées. Une preuve sûre ne compense pas un système de support qui collecte les témoins ou un backend qui associe chaque preuve à une identité civile sans justification.

Le test de bout en bout doit vérifier l'effet métier après acceptation de la preuve, et pas seulement le résultat booléen du vérificateur. Il doit également vérifier les rejets, les doublons, les versions périmées et les échecs de service. Si une preuve n'est pas disponible, l'application doit conserver les contrôles de sécurité et expliquer l'indisponibilité sans basculer vers une validation moins sûre.

Archive les artefacts, les vecteurs de test, les résultats, les limites de l'examen et les risques résiduels. La publication devrait être bloquée si la déclaration n'est pas alignée entre le circuit et le contrat, si les paramètres ne sont pas vérifiés ou si le modèle de confidentialité ne correspond pas aux attentes annoncées aux utilisateurs.

## 39. Questions d'entraînement avec corrigé

### Question 1 : Quelles sont les trois propriétés classiques d'une preuve ZK ?

**Correction :** Complétude, solidité et confidentialité à divulgation nulle, selon les définitions et hypothèses du protocole choisi.

### Question 2 : Une preuve ZK rend-elle automatiquement la blockchain privée ?

**Correction :** Non. Les entrées publiques, événements, montants, adresses et métadonnées peuvent rester visibles.

### Question 3 : Quelle est la différence entre témoin et entrées publiques ?

**Correction :** Le témoin contient les valeurs utilisées secrètement pour satisfaire la relation ; les entrées publiques sont connues du vérificateur et peuvent être inscrites sur chaîne.

### Question 4 : À quoi sert un circuit ?

**Correction :** Il représente le calcul sous forme de contraintes compatibles avec le système de preuve. La correction dépend de la relation effectivement encodée.

### Question 5 : SNARK et STARK sont-ils des outils uniques ?

**Correction :** Non. Ce sont des familles de constructions, avec des différences de paramètres, de taille de preuve, de coût et d'hypothèses.

### Question 6 : Pourquoi documenter une cérémonie de setup ?

**Correction :** Certaines constructions dépendent de paramètres produits par une procédure sensible. Il faut examiner les hypothèses, les contributions et le matériel secret potentiel.

### Question 7 : À quoi sert un nullifier ?

**Correction :** Il peut signaler qu'une capacité a été consommée et empêcher une réutilisation sans révéler directement le secret d'origine. Sa portée doit être conçue pour éviter les rejeux et les liaisons non souhaitées.

### Question 8 : Une preuve d'inclusion dans un arbre Merkle prouve-t-elle toutes les permissions métier ?

**Correction :** Non. Elle montre que l'élément correspond à une racine sous les règles définies. La révocation, l'éligibilité et les droits doivent être encodés séparément.

### Question 9 : Quels éléments peuvent encore révéler l'identité ?

**Correction :** Les adresses, heures, montants, répétitions, tailles de messages, logs, données de réseau et relations entre opérations peuvent permettre des corrélations.

### Question 10 : Pourquoi ne faut-il pas inventer sa propre primitive ZK pour la production ?

**Correction :** La sécurité dépend de mathématiques, d'implémentation et de paramètres subtils. Un outil éprouvé, une spécification précise, des tests et une revue indépendante sont nécessaires.

## 40. Challenge final : concevoir une preuve pour une application de confidentialité

Une application souhaite permettre à un utilisateur de démontrer qu'il respecte une règle d'éligibilité sans publier son identité civile. Elle doit aussi éviter les utilisations multiples du même droit et permettre à un vérificateur d'authentifier l'autorité qui a émis l'attestation.

### Travail demandé

Définis le témoin, les entrées publiques, les engagements, la relation à prouver, le mécanisme d'identification de l'autorité, la règle de nullifier, les données visibles sur chaîne, les principaux adversaires et les tests négatifs. Explique les fuites qui restent possibles et précise ce qui exige une expertise cryptographique indépendante.

### Correction proposée

Le rapport sépare l'authenticité de l'attestation, l'éligibilité, la confidentialité, l'anti-rejeu et la gouvernance des paramètres. Il précise quelles propriétés sont prouvées et lesquelles dépendent de la gestion de l'identité ou de l'infrastructure. Les données publiques sont minimisées et les identifiants sont contextualisés. Les tests vérifient la preuve valide, le témoin incorrect, une autorité inconnue, un nullifier déjà consommé, une entrée publique modifiée et une preuve liée à un autre contexte.

Le système n'est pas déclaré sûr uniquement parce que la preuve est acceptée. Il faut une revue de la relation, des paramètres, des bibliothèques, du contrat vérificateur et du comportement réel de l'application. La décision finale expose les risques résiduels et n'affirme pas que toute forme de traçage est impossible.

## Glossaire

**Preuve ZK** : preuve qui démontre une déclaration sans révéler le témoin au-delà des informations autorisées.

**Prouveur** : acteur ou programme qui génère la preuve.

**Vérificateur** : programme qui accepte ou rejette la preuve selon la relation et les paramètres.

**Témoin** : données privées qui satisfont la relation à prouver.

**Entrées publiques** : valeurs visibles par le vérificateur et éventuellement inscrites sur la blockchain.

**Circuit** : représentation du calcul sous forme de contraintes.

**SNARK** : famille de preuves succinctes et non interactives, avec des propriétés et hypothèses propres à chaque construction.

**STARK** : famille de preuves transparentes et conçues pour s'adapter à de grands calculs, avec des compromis distincts.

**Engagement** : mécanisme cryptographique qui fixe une valeur tout en permettant de ne pas la révéler immédiatement.

**Arbre de Merkle** : structure qui permet d'engager un ensemble et de prouver l'appartenance d'un élément à partir d'une racine.

**Nullifier** : valeur utilisée dans certains protocoles pour empêcher la réutilisation d'une capacité.

**Disponibilité des données** : possibilité de récupérer les données nécessaires à une vérification ou à la reconstruction de l'état.

## Pour aller plus loin

- Ethereum.org, preuves à divulgation nulle de connaissance : https://ethereum.org/zero-knowledge-proofs
- Ethereum.org, confidentialité : https://ethereum.org/en/privacy/
- Documentation des circuits et bibliothèques choisies par le projet : privilégier les docs officielles et les versions épinglées.
- Rapports indépendants sur les preuves, paramètres et vérificateurs de l'implémentation étudiée.

Le domaine évolue rapidement. Vérifie les propriétés et les hypothèses de la construction effectivement utilisée ; les termes SNARK, STARK et ZK ne constituent pas une certification de sécurité.
