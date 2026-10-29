# Interopérabilité (bridges, Cosmos)

## Encadré de mise en contexte

Les blockchains possèdent généralement leur propre état, leur propre consensus et leurs propres règles de finalité. Un contrat qui s'exécute sur un réseau ne peut pas simplement lire l'état d'un autre réseau comme s'il s'agissait d'une variable locale. L'interopérabilité vise à faire circuler des actifs, des preuves ou des messages entre des domaines qui ne partagent pas nécessairement la même sécurité.

Un bridge peut permettre à un actif de circuler entre deux réseaux, mais il ne transporte pas littéralement le même état cryptographique d'une chaîne à l'autre. Il peut verrouiller un actif sur la chaîne source et créer une représentation sur la destination, s'appuyer sur un ensemble de validateurs externes ou vérifier des preuves du réseau d'origine. Chaque modèle ajoute des hypothèses différentes. Une opération cross-chain doit donc être pensée comme une succession d'événements asynchrones, avec des étapes de validation, de finalité, de livraison et parfois de compensation.

Ce cours aborde les bridges d'actifs, le passage de messages arbitraires, les light clients, les preuves, les relayers, les timeouts, les risques de replay, la comptabilité des actifs enveloppés et les principes d'IBC dans l'écosystème Cosmos. L'objectif est de savoir évaluer un système inter-chaînes, comprendre où se trouvent les frontières de confiance et construire une procédure de sécurité et de récupération.

## Objectifs d'apprentissage

À la fin du cours, tu dois pouvoir expliquer les principaux modèles de bridge, distinguer transfert d'actif et passage de message, suivre le cycle d'un paquet, analyser les hypothèses d'un light client ou d'un comité externe, concevoir des protections contre le replay, comprendre acknowledgements et timeouts, vérifier les invariants de mint/burn/lock/release, diagnostiquer un transfert bloqué et rédiger un modèle de menace inter-chaînes.

## Prérequis et parcours pratique

Il est utile de connaître les blocs, la finalité, les smart contracts, les événements, les signatures et la gouvernance. Tous les exercices sont conçus pour un environnement de laboratoire et des actifs fictifs. N'utilise pas un bridge avec des fonds réels pour apprendre à partir d'une transaction ratée. La procédure de récupération dépend de la route et de son contrat ; un second transfert peut aggraver le problème en créant des opérations concurrentes.

Le parcours pratique consiste à choisir une route inter-chaînes documentée, à identifier les deux chaînes, les contrats, les preuves de source, les relayers et le mécanisme de secours, puis à simuler des messages retardés, dupliqués et expirés. Le rapport doit distinguer les faits observés, les hypothèses et les informations qui n'ont pas pu être vérifiées.

## 1. Pourquoi l'interopérabilité est difficile

Chaque chaîne possède son propre état et ses propres règles pour déterminer quels blocs sont valides et quand un événement peut être considéré comme final. Une chaîne A peut constater qu'un actif a été verrouillé ; la chaîne B doit ensuite recevoir une preuve ou un message crédible de cet événement avant de créer, créditer ou autoriser quelque chose. La difficulté centrale est de permettre à B de raisonner correctement sur A sans simplement faire confiance à un message non vérifié.

Un message peut arriver en retard, être livré plusieurs fois, être livré dans le désordre, être observé avant la finalité de sa chaîne source ou ne jamais arriver. Le relayer peut tomber en panne. Les réseaux peuvent connaître une réorganisation, une mise à niveau ou une période d'indisponibilité. Un modèle de bridge sûr doit traiter ces états au lieu de supposer que chaque message traverse immédiatement et exactement une fois.

L'interopérabilité est donc un problème de vérification et de coordination entre domaines de confiance. La sécurité dépend de la manière dont la chaîne destination vérifie la preuve de l'événement source, de la sécurité des contrats, des hypothèses de finalité, de la gestion des identifiants et du traitement des pannes.

## 2. Transfert d'actifs et messages arbitraires

Un bridge d'actifs permet un mouvement économique : l'utilisateur dépose ou verrouille un actif dans un domaine et reçoit une valeur correspondante dans un autre. Un bridge de messages peut transmettre un appel ou des données entre contrats, par exemple informer un protocole de gouvernance qu'une décision a été prise sur une autre chaîne. Certains systèmes prennent en charge les deux types d'opération, mais leur logique de sécurité peut différer.

Dans un modèle lock-and-mint, l'actif original est verrouillé sur la source et une représentation est émise sur la destination. Le retrait brûle généralement la représentation, puis la chaîne source libère l'actif original après vérification. Dans un modèle burn-and-mint, l'émission et la destruction sont gérées selon des règles coordonnées sur plusieurs chaînes. D'autres routes utilisent de la liquidité prépositionnée et ne suivent pas exactement ce cycle.

Une représentation enveloppée n'est pas automatiquement équivalente à l'actif original. Sa valeur dépend de la possibilité de la racheter, du contrat du bridge, des réserves, des droits d'administration et de la sécurité de la source. Un bridge qui perd sa capacité de libération peut laisser une représentation encore transférable mais devenue difficile à échanger contre l'actif original.

~~~mermaid
flowchart LR
    A[Actif original sur A] --> B[Verrouillage ou destruction sur A]
    B --> C[Preuve ou message d'origine]
    C --> D[Vérification sur B]
    D --> E[Création ou crédit de représentation sur B]
    E --> F[Utilisateur sur B]
    F --> G[Demande de retour]
    G --> H[Burn ou retrait sur B]
    H --> I[Preuve du retour]
    I --> J[Libération ou émission sur A]
~~~

Le schéma montre un modèle simplifié. Pour analyser un système réel, identifie la règle précise qui relie chaque étape et le mécanisme qui empêche une même preuve d'être consommée deux fois.

## 3. Modèles de confiance d'un bridge

Les bridges basés sur des validateurs externes ou une multisignature demandent à un ensemble d'acteurs de vérifier les événements source et de signer les messages destination. Le niveau de confiance dépend du nombre de signatures nécessaires, de leur indépendance, de leur contrôle opérationnel, des protections de clés et de la manière dont le système réagit à une collusion ou une compromission.

Les bridges basés sur un light client tentent de vérifier sur une chaîne des preuves relatives à l'état de l'autre chaîne. Cette approche peut réduire la nécessité de faire confiance à un comité indépendant, mais elle exige que le client léger représente correctement les règles de consensus et la finalité du réseau source. Un bug dans le vérificateur, une hypothèse cryptographique incorrecte ou une procédure de mise à jour non sûre peut toujours compromettre la route.

Les bridges optimistes peuvent accepter un message sous réserve d'une fenêtre de contestation. Ils dépendent de la capacité d'un participant honnête à détecter un message invalide et à agir dans le délai prévu. Les bridges à preuves cryptographiques cherchent à vérifier directement des assertions sur la chaîne source. Les réseaux de liquidité peuvent avancer les actifs depuis une réserve et se rééquilibrer ultérieurement, ce qui ajoute des risques de liquidité et de contrepartie différents.

| Modèle | Avantage typique | Risque ou hypothèse à examiner |
|---|---|---|
| Multisignature ou comité | Déploiement et connectivité flexibles | Collusion, compromission ou censure des signataires |
| Light client | Vérification liée au consensus source | Correctitude et mise à jour du client de vérification |
| Optimiste avec contestation | Vérification conditionnelle et défi explicite | Disponibilité des données et délais de challenge |
| Réseau de liquidité | Expérience rapide pour l'utilisateur | Liquidité, solvabilité et opérations de rééquilibrage |
| Relayer de messages | Transport des données entre chaînes | Le relayer doit être distingué du mécanisme qui authentifie la preuve |

Une bonne analyse ne qualifie pas un bridge de trustless uniquement parce qu'il utilise une preuve. Les preuves vérifient des propriétés spécifiques. Il reste nécessaire d'identifier qui peut modifier le vérificateur, qui contrôle les contrats, comment les clés sont conservées et si les données nécessaires aux sorties sont disponibles.

## 4. Le cycle de vie d'un message inter-chaînes

Un message typique part d'un contrat source, crée un identifiant ou un engagement, attend le niveau de finalité nécessaire, est récupéré par un relayer, puis est soumis au système de vérification destination. La chaîne destination valide la preuve, vérifie que le message n'a pas déjà été exécuté et appelle la fonction métier. L'accusé de réception ou la preuve de traitement peut ensuite être retourné au domaine source.

Un relayer est souvent un transporteur, pas une autorité de vérité. Il peut proposer le message à la destination, mais la destination doit vérifier les preuves selon le modèle de sécurité du protocole. Si le système dépend d'un relayer particulier pour la disponibilité, il faut prévoir un remplaçant ou un mécanisme qui permet à un autre acteur de livrer le message.

La notion d'exécution exactement une fois est difficile lorsque les composants sont distribués. Les systèmes utilisent généralement des identifiants, des nonces, des états de paquet et des preuves de consommation pour empêcher le traitement répété. Un message peut être reçu deux fois en raison de réessais ; le contrat doit rendre le traitement idempotent ou rejeter le second passage sans appliquer de nouvel effet.

~~~mermaid
sequenceDiagram
    participant A as Chaîne source
    participant R as Relayer
    participant B as Chaîne destination
    A->>A: Créer message et engagement
    R->>A: Lire données et preuve
    R->>B: Soumettre paquet et preuve
    B->>B: Vérifier client, preuve et identifiant
    B->>B: Exécuter une seule fois
    B-->>R: Résultat ou acknowledgement
    R-->>A: Rapporter le résultat si le protocole le prévoit
~~~

Ce déroulement peut varier fortement. Certains systèmes n'ont pas d'accusé de réception explicite, d'autres produisent plusieurs étapes de preuve et certains mécanismes d'actifs reposent sur une procédure différente du passage de messages arbitraires. Vérifie les états exacts dans la spécification du protocole choisi.

## 5. Finalité et réorganisations de la source

Un message fondé sur un événement trop récent peut devenir invalide si la chaîne source réorganise son historique. Si la chaîne destination a déjà exécuté l'effet économique, elle peut ne pas pouvoir annuler facilement cette décision. Le bridge doit donc appliquer une politique de finalité qui correspond au modèle de menace et au protocole source.

Les chaînes n'ont pas toutes la même définition de finalité. Certaines proposent une finalité déterministe selon leur protocole, d'autres exposent un niveau de confirmation probabiliste ou un état de justification spécifique. Une application cross-chain doit utiliser la notion appropriée à la source et ne pas remplacer cette analyse par un nombre fixe de blocs copié d'un autre réseau.

Les délais influencent l'expérience utilisateur. Attendre davantage peut réduire certains risques de réorganisation mais accroît la latence. Les mécanismes de liquidité peuvent avancer une valeur plus tôt, mais l'acteur qui avance les fonds assume un risque et peut facturer ce service. Il faut séparer le statut de l'opération source, l'état du message et le statut du crédit destination.

## 6. Replay, domaines et identifiants de message

Un rejeu survient lorsqu'un message ou une signature valide dans un contexte est présenté une seconde fois dans le même contexte ou dans un autre. Pour le prévenir, l'identité du message doit être liée à la source, à la destination, au protocole, à un identifiant de paquet ou de nonce, ainsi qu'au contenu de l'action lorsqu'il est nécessaire de lever l'ambiguïté.

La signature d'une autorisation ou un message signé doit inclure un domaine de confiance explicite. Une signature prévue pour une chaîne ne doit pas devenir valide sur une autre chaîne seulement parce que l'adresse du contrat est identique. La notion de domain separation limite les ambiguïtés entre chaînes, contrats, versions et fonctions.

Les contrats destination doivent vérifier que le message a été authentifié et qu'il n'a pas déjà été consommé. La protection contre le replay doit également survivre aux mises à niveau et aux changements de configuration. Si le système réinitialise un compteur ou change la manière de calculer l'identifiant, une ancienne preuve pourrait devenir réutilisable si les règles ne sont pas conçues avec soin.

## 7. Comptabilité des actifs enveloppés

La comptabilité est une propriété centrale du bridge. Pour un modèle lock-and-mint, le total des représentations créées doit rester lié aux actifs immobilisés selon les règles du système, en tenant compte des frais et des mécanismes de réserve définis. Un message dupliqué, une preuve acceptée sans dépôt correspondant ou une erreur de burn peut créer plus de représentations que les réserves ne peuvent soutenir.

Formule l'invariant de façon précise. Par exemple, la quantité de représentations en circulation doit être inférieure ou égale à l'actif éligible immobilisé, après ajustements explicitement prévus. Si le modèle permet des frais, des actifs surcollatéralisés ou des émissions contrôlées par plusieurs chaînes, écris la relation comptable exacte. Ne suppose pas que la somme de toutes les balances est toujours égale au dépôt initial sans examiner les frais et les états en attente.

La réconciliation doit tenir compte des messages en transit. Un dépôt peut être final sur la source mais ne pas encore avoir été crédité sur la destination. Un burn peut être observé sur B alors que la libération sur A est en attente. Les rapports de solvabilité doivent donc distinguer les actifs verrouillés, les représentations circulantes, les messages en attente, les retraits en cours et les opérations rejetées.

## 8. Gestion de l'échec, des délais et des accusés de réception

Les systèmes de messagerie inter-chaînes sont asynchrones. Un message peut être créé sans être livré, livré sans que l'application confirme le résultat, ou arriver après que le contexte métier ait changé. Les acknowledgements permettent, dans certains protocoles, de rendre observable le résultat du traitement. Les timeouts permettent de traiter une absence de réponse selon une règle définie, mais ils ne doivent pas provoquer une double émission ou un double remboursement.

Lorsqu'un paquet expire, la récupération doit respecter l'état de la source et de la destination. La source peut avoir besoin de prouver l'expiration selon la règle du protocole avant de libérer un actif ou de remettre une capacité à l'utilisateur. Il ne suffit pas de constater qu'un relayer n'a pas répondu dans l'interface. Une absence de réponse peut être un problème de transport, une congestion ou une preuve qui n'a pas encore atteint la destination.

La reprise doit être conçue à l'avance. Définis le rôle de l'accusé de réception, les conditions d'expiration, la possibilité de soumettre à nouveau un message et l'identifiant utilisé pour dédoublonner le traitement. Il faut aussi documenter les messages qui restent en état indéterminé et les actions opérateur permises, en limitant les pouvoirs qui peuvent déclencher un remboursement.

## 9. Cosmos IBC : clients, connexions, canaux et paquets

IBC, Inter-Blockchain Communication, est un protocole qui permet à des chaînes de l'écosystème Cosmos de communiquer par des clients et des preuves. À un niveau conceptuel, un client suit un état de la chaîne distante ; une connexion établit les paramètres nécessaires à l'échange ; un canal fournit le contexte pour les paquets ; les relayers transportent les messages et preuves ; les paquets et leurs acknowledgements ou timeouts permettent de suivre les résultats.

Le relayer ne doit pas être confondu avec le mécanisme d'authentification. Plusieurs relayers peuvent être capables de transmettre les mêmes paquets, tandis que les preuves sont vérifiées selon la logique du client et du protocole. La sécurité dépend de la validité du client, des paramètres de confiance, de la gestion des mises à jour et de la manière dont le réseau distant est surveillé.

Le cycle de vie comporte plusieurs états et messages, et les détails diffèrent selon la version du protocole et les applications. Pour une intégration réelle, consulte la spécification et la documentation de la version effectivement déployée. Le cours fournit le modèle mental, mais ne remplace pas la documentation d'implémentation.

~~~mermaid
flowchart TD
    A[Client suit la chaîne distante] --> B[Connexion configurée]
    B --> C[Canal ouvert]
    C --> D[Paquet émis sur la source]
    D --> E[Relayer collecte le paquet]
    E --> F[Preuve vérifiée sur destination]
    F --> G[Paquet exécuté par l'application]
    G --> H[Acknowledgement ou état de paquet]
    H --> I[Clôture ou poursuite du canal]
~~~

Un port et un canal sont des paramètres de contexte, pas une preuve de confiance à eux seuls. Vérifie l'identité de la contrepartie, le client associé, le statut du canal, les séquences et les conditions de timeout. Une opération peut échouer parce que le canal n'est pas dans l'état requis ou parce que les données et les preuves ne correspondent pas, même si les chaînes sous-jacentes sont disponibles.

## 10. Clients légers et mises à jour de consensus

Un client léger ne télécharge pas nécessairement toutes les données de la chaîne distante. Il conserve ou vérifie des informations minimales permettant d'authentifier un état ou une preuve selon les règles du consensus. Cette approche réduit le besoin de faire confiance à un opérateur externe, mais sa sécurité dépend de la qualité du client, de ses paramètres de confiance, de sa mise à jour et de sa réaction lorsque la chaîne distante progresse ou change de version.

La rotation de confiance, les périodes de mise à jour et les conditions d'expiration du client sont des mécanismes importants. Un client trop ancien peut être incapable de vérifier de nouveaux états ; une mise à jour incorrecte peut accepter un état frauduleux ou bloquer les paquets légitimes. Le plan opérationnel doit indiquer qui surveille l'expiration, qui déclenche une mise à jour et quelle preuve confirme le succès.

Un système doit éviter de traiter une donnée de consensus distante comme valide seulement parce qu'elle provient d'un relayer familier. L'authentification doit venir du mécanisme défini par le protocole. Si l'application ajoute des services tiers pour accélérer la découverte ou l'indexation, la sécurité de ces services ne doit pas être confondue avec celle du client léger.

## 11. Risques typiques de bridge

Les incidents de bridge proviennent souvent de combinaisons de problèmes : bug du contrat, preuve mal vérifiée, clé compromise, mauvaise configuration, erreur de comptabilité, mise à niveau non sûre, hypothèse erronée sur la finalité ou défaillance opérationnelle. Le risque peut se multiplier parce que le bridge concentre des actifs importants ou sert de dépendance à plusieurs protocoles.

Un contrat peut vérifier qu'un message a été signé par un comité sans s'assurer que le message représente une opération source valide. Un autre système peut vérifier un engagement mais ne pas protéger le consommateur contre la réutilisation de la même preuve. Une route peut aussi reposer sur un actif enveloppé largement utilisé en DeFi ; sa perte de parité peut se propager à des prêts, des pools et des marchés.

La revue doit comprendre une analyse des scénarios de perte totale et partielle, des limites de retrait, des plafonds de mint, des délais de sécurité, des rôles d'urgence et des procédures de mise à niveau. Les mécanismes de pause et de plafonnement peuvent réduire l'impact, mais doivent être testés et gouvernés. Ils ne remplacent pas la validation correcte des messages.

## 12. Ponts et contrats : validation d'un message

Une chaîne destination doit vérifier que le message vient du protocole attendu, qu'il correspond au bon réseau source, qu'il vise le bon contrat, que ses données sont valides et qu'il n'a pas déjà été exécuté. Une preuve valide de source ne signifie pas automatiquement que toutes les actions demandées par le message sont autorisées. La logique métier de destination doit continuer à appliquer ses propres permissions et invariants.

Si un message déclenche une mise à niveau, une émission de jetons ou un transfert de valeur important, applique une politique d'autorisation adaptée au risque. Une authentification cryptographique correcte ne doit pas devenir une porte d'entrée qui contourne l'ensemble des contrôles du contrat. Les paramètres des messages doivent être liés au domaine, aux contrats et à la version attendus.

Les essais doivent inclure des messages mal formés, des identifiants de source incorrects, des nonces répétés, des preuves expirées, des appels destinés à un contrat inattendu et des erreurs de réception. Les tests devraient démontrer que l'état et les réserves restent cohérents quand le message échoue, et pas seulement que l'appel retourne une erreur.

## 13. Gouvernance, clés et procédures d'urgence

Un bridge qui dépend d'un comité, d'une multisignature ou d'un rôle d'administration doit publier clairement les seuils d'approbation, la méthode de rotation des clés, les délais, les identités de secours et les procédures d'urgence. La concentration des pouvoirs, leur disponibilité et la capacité d'un acteur à bloquer une sortie doivent être intégrées au modèle de menace.

Les clés de signature devraient être protégées par des mécanismes adaptés à l'impact, séparées des clés de déploiement et surveillées. La rotation de clés exige de vérifier les contrats ou composants qui acceptent les nouvelles signatures et de s'assurer que les anciennes clés perdent les pouvoirs prévus. Une procédure d'urgence ne devrait pas dépendre exclusivement d'une personne qui n'est pas disponible en dehors des heures de bureau.

La pause d'un bridge peut protéger les utilisateurs en cas d'anomalie confirmée, mais une pause mal conçue peut empêcher les sorties légitimes. Écris les conditions de déclenchement et de reprise, la façon d'informer les utilisateurs et les opérations qui restent permises. Chaque action d'urgence doit laisser une trace consultable et être suivie d'une revue après incident.

## 14. Surveillance et réconciliation cross-chain

La surveillance doit corréler les événements des deux chaînes. Pour chaque opération, conserve un identifiant de corrélation, le réseau source, le réseau destination, l'adresse de contrat, l'identifiant de message, les hashes des transactions, les hauteurs des blocs, les montants et l'état courant. Les journaux techniques doivent permettre de retrouver l'étape où la progression s'est arrêtée.

La réconciliation compare les événements sources, les preuves observées, les paquets en attente, les acknowledgements, les burns, les mints et les réserves. Les résultats doivent différencier un délai normal du protocole, un relayer inactif, un client expiré, une transaction rejetée et un défaut de comptabilité. Un tableau de bord qui n'affiche que le nombre de transferts réussis peut cacher des messages en attente depuis trop longtemps.

Les alertes doivent inclure l'âge maximal d'un paquet, la divergence des soldes, le nombre de tentatives, les changements de configuration, les échecs de vérification et l'état des clients. Les seuils dépendent du protocole et de sa cadence ; définis-les à partir d'une référence et documente les actions opérateur associées. Une alerte sans propriétaire et sans runbook n'offre qu'une visibilité partielle.

## 15. TP guidé A : cartographier un bridge

Choisis un bridge de test documenté. Identifie le modèle de confiance, les contrats source et destination, les actifs, les mécanismes de preuve, le relayer, les délais, les rôles d'administration et les procédures de sortie. Utilise des transactions de test uniquement. Dessine le cycle du transfert et marque les moments où un message pourrait être retardé, dupliqué ou rejeté.

### Correction proposée

La cartographie distingue transport et authentification. Elle ne suppose pas que le relayer garantit la vérité du message. Elle identifie le mécanisme qui vérifie la source, la condition qui protège contre le replay, la procédure d'expiration et l'invariant comptable. Les inconnues sont notées comme des risques à lever avant une mise en production.

## 16. TP guidé B : tester un message dupliqué

Dans une implémentation de laboratoire, crée un message avec un identifiant unique, exécute-le sur la destination, puis soumets de nouveau la même preuve. Vérifie que le second traitement ne crée pas de nouveau transfert ni ne modifie l'état une seconde fois. Répète l'essai avec un identifiant changé mais un contenu identique afin de vérifier que la règle de dédoublonnage est fondée sur le modèle voulu.

### Correction proposée

Le système doit appliquer une règle explicite : soit un identifiant a déjà été consommé et l'appel est rejeté, soit le traitement est idempotent et retourne un résultat sans effet supplémentaire. Le rapport doit vérifier la balance, le nonce ou l'état du message après les deux soumissions. Un simple événement « traitement terminé » ne suffit pas à prouver que l'actif n'a été émis qu'une fois.

## 17. Étude de cas : paquet bloqué après une mise à jour

Une chaîne source a émis un paquet, mais la destination ne l'a pas traité après la mise à jour de son client léger. Le relayer continue de fonctionner et l'interface affiche « en attente ». Plusieurs équipes proposent de réessayer le transfert ou de modifier manuellement l'état du paquet.

### Travail demandé

Définis les premières vérifications, les preuves à collecter, les opérations à ne pas exécuter avant d'avoir clarifié l'état, puis les critères de reprise. Distingue un problème de transport, un problème de client, une preuve invalide et une expiration de paquet.

### Correction proposée

Récupère le paquet original, l'identifiant de source et de destination, la hauteur, la preuve, l'état du client et les journaux du relayer. Vérifie dans la spécification si la mise à jour du client est valide et si la preuve peut encore être soumise. N'émet pas un nouveau transfert simplement parce que l'interface n'a pas reçu de réponse. Si le paquet a expiré, suis la procédure officielle de timeout et vérifie les conditions de remboursement ou de retour. Après correction, réconcilie l'état des deux chaînes et confirme qu'aucun double crédit n'a eu lieu.

## 18. Comprendre les canaux, les séquences et les preuves de paquet dans IBC

Dans IBC, un transfert est traité comme un échange de paquets ayant un contexte précis. Les clients suivent des états distants, les connexions établissent les paramètres d'échange et les canaux définissent un contexte d'application. Les relayers transportent les messages nécessaires à l'évolution du protocole, mais l'authenticité dépend des preuves et des règles vérifiées par le destinataire.

Les séquences permettent d'identifier des paquets distincts et de protéger l'ordre lorsque le mode de canal le requiert. Les canaux ordonnés et non ordonnés n'ont pas les mêmes règles de progression ni les mêmes implications pour les timeouts. Avant d'écrire une procédure de récupération, identifie le mode du canal et les états attendus ; une règle adaptée à un canal peut être incorrecte pour un autre.

Les commitments et preuves permettent de vérifier qu'un paquet a été émis ou qu'un état de paquet existe à une hauteur pertinente. Les données de preuve doivent être associées au client, à la chaîne, au port, au canal, à la séquence et au type d'opération attendus. Une preuve ne doit pas être acceptée simplement parce qu'elle est valide dans un autre contexte.

Dans une intégration réelle, consigne la version IBC, les modules d'application, les paramètres du client et les chaînes participantes. Les chemins d'ouverture de canal, la gestion des clients et les règles de timeout dépendent de la version et de l'implémentation. Le modèle mental de ce cours est un point de départ ; les détails opérationnels doivent être vérifiés dans les spécifications exactes du réseau.

## 19. Identité des actifs et traçabilité des dénominations

Les actifs qui circulent par un protocole inter-chaînes peuvent recevoir une représentation ou une dénomination qui encode leur origine et le chemin emprunté. Il ne faut pas se fier uniquement au nom court ou au symbole affiché dans un portefeuille. Deux actifs peuvent porter le même symbole tout en ayant des émetteurs, des mécanismes de rachat et des garanties différents.

Dans un transfert de jeton IBC, la dénomination et les traces de transfert servent à distinguer les représentations et à savoir quel chemin est utilisé. Une application doit préserver cette identité lorsqu'elle enregistre des soldes, construit des listes d'actifs ou calcule des prix. Si elle réduit chaque dénomination à un symbole d'affichage, elle peut fusionner des actifs qui ne sont pas équivalents et créer une erreur comptable.

La gestion des actifs doit aussi préciser les frais, les montants minimaux, les décimales et le comportement des opérations en attente. Les unités affichées par l'interface ne doivent pas être utilisées directement comme des nombres flottants pour les calculs financiers. La valeur nominale d'un actif distant ne garantit pas sa liquidité ou son prix de marché sur la chaîne de destination.

Avant d'ajouter une route à un portefeuille ou à une application, vérifie l'origine de la dénomination, le chemin prévu, les contrats concernés, la politique de rachat et les mécanismes d'urgence. Si une représentation peut être émise par un bridge, documente la relation entre cette représentation et les actifs ou les garanties sous-jacents. Le symbole n'est qu'une étiquette d'interface ; la référence technique doit être plus précise.

## 20. Mettre à jour un client léger sans perdre les garanties

Un client léger ne reste pas valide automatiquement pour toujours. Il peut avoir une période de confiance, une condition d'expiration ou une exigence de mise à jour. Si le client ne suit plus l'état distant, des paquets peuvent échouer ou être bloqués. Une mise à jour trop tardive peut rendre le canal inutilisable, tandis qu'une mise à jour incorrecte peut accepter un état qui ne devrait pas être considéré comme fiable.

Le runbook doit surveiller l'âge du dernier état accepté, le prochain seuil de mise à jour et les messages d'erreur du client. Il doit nommer la personne ou le service responsable et documenter la procédure officielle de mise à jour. La séquence exacte dépend du client et de la version du protocole ; ne copie pas les paramètres d'une autre chaîne sans validation.

Avant une mise à jour, conserve l'état observé, la version du client, les preuves et les paramètres de confiance. Après le changement, vérifie que l'état courant est accepté, que les preuves attendues peuvent être vérifiées et que le canal reprend sa progression. Un relayer qui tourne ne prouve pas que le client de destination accepte les messages.

Le test de laboratoire devrait inclure un client en retard, une mise à jour valide, une mise à jour invalide et un paquet qui devient éligible pendant la période de reprise. Les critères de succès sont vérifiables : pas d'état distant accepté sans vérification, pas de paquet traité deux fois et progression normale rétablie dans les limites documentées.

## 21. Analyse de menace pour une route inter-chaînes

Le modèle de menace doit examiner les deux chaînes, les contrats, le client ou le comité de vérification, les relayers, les clés, la gouvernance et les systèmes de surveillance. Une hypothèse sûre sur la chaîne source n'implique pas automatiquement une hypothèse sûre sur la destination. Il est possible que la source ait exécuté un dépôt correct alors que la destination possède une configuration erronée ou une adresse de bridge compromise.

Pour chaque acteur, décris ses capacités et ce qui l'empêche d'agir seul. Un relayer peut retarder un paquet ; un comité peut signer un message faux si suffisamment de clés sont compromises ; un administrateur peut changer l'adresse de vérification ; une faille du client peut accepter un état invalide ; un bug de comptabilité peut émettre plus de représentation que les garanties disponibles. Les protections doivent être reliées à des propriétés précises et testées.

Les risques de disponibilité et les risques d'intégrité doivent être séparés. Un relayer hors ligne peut empêcher un transfert de progresser sans falsifier aucun état. Un message faux accepté peut produire un effet économique alors que les services fonctionnent normalement. Les réponses diffèrent : ajouter un relayer peut aider la disponibilité, mais ne corrige pas un vérificateur compromis.

Les limites financières, les plafonds de mint et les délais de sécurité peuvent réduire certains impacts. Ils doivent être conçus pour correspondre au modèle économique et ne pas dépendre de la même clé ou du même composant que celui qu'ils sont censés contenir. Une limite qui peut être relevée immédiatement par le rôle compromis ne constitue pas une défense indépendante.

## 22. Test de domain separation et de rejeu

Un message ou une signature doit être lié au contexte dans lequel il est autorisé. Les éléments potentiels comprennent l'identité de la chaîne source, l'identité destination, le contrat ciblé, le type d'action, un nonce ou identifiant unique, la version de protocole et les données utiles. Les champs exacts dépendent du protocole ; l'objectif est d'éviter qu'une preuve valable pour une opération soit interprétée comme une autorisation d'une autre.

Dans un laboratoire, crée un message de test sur une chaîne source et vérifie qu'il est accepté uniquement dans le contexte attendu. Soumets la même preuve une seconde fois, puis modifie la destination ou l'identifiant de contexte tout en conservant les autres données. Le contrat ou le protocole doit refuser ces réutilisations ou les traiter sans effet supplémentaire, selon le modèle défini.

La suite de tests doit également considérer les remplacements de contrats et la rotation des identités de vérification. Une mise à niveau peut modifier la manière dont un identifiant est calculé. Les messages historiques ne doivent pas devenir réexécutables par inadvertance après une migration de stockage ou une réinitialisation de compteur.

Archive les données d'entrée et le résultat d'exécution. Le test est incomplet si l'interface affiche une erreur mais qu'une écriture d'état ou un transfert a déjà eu lieu. Vérifie les balances, les identifiants consommés, les événements et l'état de la route après chaque tentative.

## 23. Construire la réconciliation comptable du bridge

Une réconciliation fiable compare les dépôts source, les preuves ou messages en transit, les émissions de destination, les burns, les demandes de retrait, les libérations et les réserves. Elle doit connaître les opérations en attente, car une transaction source peut être finale sans que son crédit destination ait encore été appliqué. Un simple écart entre les totaux peut représenter un retard normal, une erreur d'indexation ou un problème de sécurité.

Utilise des identifiants déterministes pour relier les étapes et conserve la hauteur, le hash du bloc et les références des preuves. Lorsqu'un bloc source est réorganisé avant le seuil de sécurité, l'indexeur doit retirer l'événement qui n'est plus canonique ou le marquer comme invalidé. La destination ne doit pas avoir accepté un effet irréversible avant que la preuve respecte sa politique de finalité.

Définis des seuils d'alerte : somme des mints supérieure à la couverture, burn sans preuve de sortie, paquet trop ancien, différence entre état direct et indexeur, ou augmentation anormale des messages rejetés. Ces seuils doivent tenir compte de la cadence normale et du modèle de frais. Les alertes ne doivent pas déclencher automatiquement une action destructive sans vérifier le contexte.

Lorsqu'un écart est détecté, ne réécris pas manuellement les soldes pour faire disparaître l'alerte. Préserve les preuves, identifie le point où les événements divergent, détermine si le problème concerne le transport, la finalité, la logique de bridge ou l'indexation, puis applique la procédure autorisée. Toute correction d'état exige une base de décision documentée et une validation indépendante lorsque les montants sont significatifs.

## 24. Runbook de panne inter-chaînes

Un transfert qui semble bloqué doit d'abord être relié à ses identifiants source et destination. Collecte le hash source, la hauteur, le montant, l'actif, l'identifiant de paquet ou message et le statut observé sur les deux chaînes. Confirme l'identité des réseaux avant de lancer une récupération. Ne demande pas de clé privée ou de phrase de récupération pour le support.

Vérifie les étapes dans l'ordre : source soumise, source incluse, finalité requise atteinte, message ou preuve disponible, relayer actif, vérification destination réussie, exécution métier terminée, acknowledgement ou confirmation retourné si le protocole le prévoit. Chaque étape correspond à une classe de problème. Si la preuve est disponible mais rejetée, le problème peut être le client, la version, le contexte ou la configuration. Si le message n'a pas été transmis, le problème peut être la disponibilité du relayer.

Avant de retenter l'opération, détermine si le protocole permet une nouvelle soumission sûre. Les relayers peuvent retransmettre un même paquet ; la destination doit alors appliquer la règle d'idempotence prévue. Un transfert que l'interface n'a pas reconnu peut déjà avoir été traité. Une nouvelle opération indépendante pourrait créditer l'utilisateur deux fois ou créer une confusion sur l'actif.

Le ticket se clôt lorsque les deux chaînes sont réconciliées, que le destinataire reçoit l'actif attendu, que le message ne peut plus produire de deuxième effet et que les alertes sont revenues à la normale. Si la cause exacte demeure inconnue, le rapport doit le dire et laisser un suivi assigné plutôt que déclarer une réparation complète sur la base d'un affichage rafraîchi.

## 25. Test d'intégration cross-chain par défauts injectés

Dans un environnement de test, définis des scénarios où le relayer s'arrête, le message arrive en retard, le paquet est soumis deux fois, le client est en retard, le message expire et la chaîne source observe une réorganisation. Chaque scénario doit préciser le statut attendu des actifs sur les deux côtés, les messages visibles dans l'interface et la règle de reprise.

Pour une route d'actif, vérifie qu'un dépôt ne produit pas plusieurs mints et qu'un burn ne libère pas plusieurs fois l'actif source. Pour une route de message, vérifie que la fonction destination est exécutée selon la règle exacte, que la consommation du message est enregistrée et que les erreurs ne laissent pas un état partiellement appliqué. Si des actions hors chaîne réagissent aux événements, elles doivent être idempotentes aussi.

L'exercice doit inclure les cas de frontières : arrivée juste avant le timeout, tentative juste après le timeout, changement de hauteur de finalité et mise à jour de client entre la production de la preuve et sa soumission. Ces cas permettent d'identifier les erreurs d'ordre et de condition temporelle souvent absentes des tests nominaux.

La correction attendue n'est pas forcément que tous les messages réussissent immédiatement. Une réponse sûre peut être d'attendre, de rejeter ou de passer à une procédure de récupération. Le succès est que le système respecte ses invariants, conserve des états explicables et ne crée ni émission non couverte, ni perte silencieuse, ni effet dupliqué.

## 26. Choisir une architecture de bridge selon les besoins

Le choix d'un bridge dépend de la nature de la donnée transportée, du niveau de sécurité requis, de la capacité à attendre, des frais, de la connectivité, des utilisateurs ciblés et du type de gouvernance acceptable. Une application qui transfère de petites quantités d'actifs pour un jeu peut accepter certains compromis différents d'un protocole qui déplace des garanties importantes.

Pour chaque route, définis les exigences non négociables avant de comparer le coût. Un mécanisme de vérification externe peut être adapté à un produit qui accepte explicitement la dépendance à des signataires, mais il ne devrait pas être décrit comme équivalent à un client léger. Un réseau de liquidité peut réduire l'attente du transfert, mais l'utilisateur dépend alors des réserves et des opérateurs qui avancent les fonds. Un mécanisme de preuve peut réduire les hypothèses envers un comité, mais la validité de la preuve n'élimine pas les risques de gouvernance et de disponibilité.

Établis une matrice qui relie chaque route aux garanties, aux inconnues et aux preuves. Les critères éliminatoires peuvent inclure une possibilité de mint sans preuve, une absence de protection contre le replay, une autorité de mise à niveau non encadrée ou une procédure de sortie non documentée. Les autres critères peuvent être pondérés selon la valeur transférée, le délai et la complexité opérationnelle.

La décision doit conserver la possibilité d'être révisée. Un changement dans la gouvernance, le client de vérification ou la structure de liquidité peut modifier le niveau de risque. Fixe une date de réévaluation et des signaux déclencheurs, par exemple une nouvelle autorité administrative, une mise à jour majeure ou un incident sur une dépendance.

## 27. Liquidité, solvabilité et contagion entre protocoles

Les actifs enveloppés et les routes de liquidité peuvent être intégrés dans d'autres protocoles, comme des marchés de prêt ou des pools d'échange. Si le bridge perd sa capacité de libérer l'actif sous-jacent ou si le marché cesse de croire à la représentation, le prix peut s'écarter et provoquer des liquidations en chaîne. La sécurité du bridge devient donc un risque systémique pour les intégrateurs qui acceptent sa représentation comme collatéral.

Une analyse économique doit inventorier l'exposition totale : actif verrouillé, représentations en circulation, réserves de liquidité, prêts qui utilisent la représentation, concentration par utilisateur ou intégrateur et limites de retrait. La valeur affichée sur un marché n'est pas une preuve de solvabilité. L'invariant comptable doit relier les actifs d'origine aux représentations et prendre en compte les opérations en transit.

Les limites de mint et les plafonds par période peuvent réduire la taille d'un incident, à condition qu'ils soient indépendants de l'autorité susceptible d'être compromise. Une limite facilement augmentée par la même clé qui contrôle le bridge apporte peu de défense. Les plafonds doivent être calibrés pour ne pas bloquer arbitrairement les opérations légitimes et être liés à une politique claire de surveillance.

Prépare un scénario de stress : un relayer est indisponible, la sortie prend plus de temps que prévu et la liquidité secondaire diminue. Détermine ce que l'utilisateur observe, quel actif peut être échangé, quelles réserves restent disponibles et quelles actions la gouvernance peut entreprendre. Le plan doit éviter de confondre une perte temporaire de liquidité avec une preuve de fraude, tout en déclenchant un contrôle si les invariants de couverture sont violés.

## 28. Exploiter IBC : état des canaux et visibilité opérationnelle

Une intégration IBC doit surveiller l'état des clients, des connexions, des canaux et des paquets. Un canal peut être ouvert mais inutilisable si le client n'est plus à jour ou si les paquets ne peuvent pas être relayés. Un relayer peut fonctionner au niveau du processus mais être incapable de soumettre des transactions en raison de frais, d'une configuration invalide ou d'un problème de compte.

Les métriques devraient inclure l'âge du dernier paquet traité, le nombre de paquets en attente, les timeouts, les acknowledgements, les erreurs de vérification et les mises à jour de client attendues. La cadence de surveillance doit correspondre au débit et au temps de reprise acceptés. Les seuils peuvent différer entre des chaînes très actives et des réseaux qui ne traitent que peu de paquets.

Un runbook devrait expliquer comment vérifier le paquet à la source, retrouver sa séquence, confirmer les preuves et l'état de destination, puis déterminer s'il peut encore être relayé ou s'il doit suivre la procédure de timeout. Ne relance pas aveuglément une opération métier tant que son état n'est pas établi. Le protocole peut permettre une retransmission sûre du paquet, mais cela ne doit pas être supposé pour un effet hors chaîne qui n'est pas idempotent.

La mise à jour de client doit être intégrée au calendrier opérationnel. Surveille la période de confiance ou l'expiration selon l'implémentation, prépare un changement vérifiable et confirme après l'opération que les preuves sont à nouveau acceptées. La reprise doit inclure la réconciliation des paquets anciens qui ont été mis en attente pendant la panne.

## 29. Plan de test d'acceptation d'une intégration inter-chaînes

Avant la production, exécute des tests de bout en bout qui suivent le message de la source à la destination. Inclue un transfert nominal, un relayer en retard, une preuve incorrecte, une répétition, un changement de réseau, un paquet expiré, une mise à jour de client et une panne d'indexation. Chaque test doit préciser l'état attendu des actifs, l'état du message, les événements et le comportement de l'interface.

Les tests doivent inclure les frontières temporelles. Un paquet soumis juste avant un timeout peut produire un résultat différent d'un paquet soumis après. Un bloc source qui est inclus puis retiré avant le seuil de finalité peut modifier l'état attendu. Un message dont l'effet a été appliqué mais dont l'accusé de réception n'a pas été observé ne doit pas être rejoué comme une nouvelle opération sans vérifier l'état réel.

Vérifie les invariants après chaque scénario. Aucun message ne doit produire deux émissions ; aucune sortie ne doit être libérée deux fois ; les montants des actifs enveloppés doivent rester dans la relation comptable définie ; les preuves d'un domaine ne doivent pas être acceptées dans un autre ; et les erreurs ne doivent pas laisser un état impossible à réconcilier.

Enfin, vérifie l'exploitabilité du runbook par une personne qui n'a pas développé le bridge. Le dossier doit fournir les sources de vérité, les identifiants à collecter, les actions sûres, les actions interdites et les critères de clôture. Les tests d'acceptation valident les procédures humaines aussi bien que le code.

## 30. Réagir à une compromission de clé ou d'autorité de vérification

La compromission d'une clé de signataire, d'un rôle d'administration ou d'une autorité de mise à niveau peut menacer simultanément plusieurs opérations inter-chaînes. Le plan d'incident doit indiquer à l'avance comment identifier les messages émis pendant la fenêtre de risque, quelles routes peuvent être mises en pause et qui a le pouvoir de révoquer ou remplacer une autorité. Les changements de clés ne doivent pas être improvisés dans un système qui ne vérifie pas correctement les transitions de configuration.

Conserve les preuves : transactions, hashes de messages, événements de changement de rôle, approbations, versions de contrats et heure de détection. Identifie les réseaux et les actifs affectés. Compare les messages signés avec les événements source et le modèle d'autorisation. Une signature cryptographiquement valide ne prouve pas qu'un message est légitime si la clé a été compromise ; le mécanisme de bridge doit comprendre l'identité et les pouvoirs du signataire dans le modèle de confiance.

La réponse immédiate peut inclure l'arrêt de nouvelles émissions, la suspension d'une route ou la limitation de l'exposition selon les procédures préapprouvées. Avant d'exécuter une action, vérifie qu'elle ne bloque pas une opération d'urgence nécessaire aux utilisateurs. Les soldes et représentations déjà émises doivent être réconciliés pour établir si un écart de couverture existe. La pause doit être suivie d'une procédure de rétablissement et non considérée comme la correction définitive.

La rotation des clés nécessite une validation indépendante : nouvelles autorités, seuils de signature, séparation des rôles, mise à jour du client ou du contrat, état des messages en attente et retrait des anciennes permissions. Teste les messages légitimes et les messages signés par l'ancienne autorité après la rotation. La procédure doit confirmer que les anciens droits ne sont plus actifs selon le modèle prévu.

La communication doit être factuelle. Indique quels réseaux et actifs sont concernés, quelles opérations sont suspendues, ce qui est vérifié, où trouver les mises à jour et quelles actions les utilisateurs doivent éviter. Ne promets pas que les fonds sont sûrs avant d'avoir validé les invariants et l'état des contrats. Après l'incident, réalise une revue indépendante et mets à jour le modèle de menace, la procédure de stockage de clés et les alertes.

## 31. Comprendre les conséquences d'une mise à jour de protocole

Les chaînes évoluent. Une mise à niveau peut modifier les règles de consensus, les formats de preuve, les paramètres de finalité, les interfaces de client ou les modules d'application. Un bridge qui suit la chaîne distante doit savoir comment identifier cette transition et quand les anciennes preuves cessent d'être valides. Une mise à jour mal gérée peut interrompre la disponibilité, bloquer les paquets ou, dans le pire cas, affaiblir la vérification.

Avant une mise à jour, inventorie les clients légers, les contrats, les relayers, les versions de bibliothèques et les chaînes dépendantes. Identifie les versions compatibles, les dates de dépréciation, les migrations de paramètres et les conditions de retour arrière. Le plan doit vérifier qui exécute la modification, qui approuve le changement et comment l'état est confirmé après le déploiement.

Un test sur environnement de développement peut révéler les problèmes de compatibilité, mais il ne reproduit pas toujours la congestion, les retards de mise à jour et les états de paquets de production. Prépare donc des scénarios de migration avec des paquets en attente, des messages près de leur timeout et des événements reçus juste avant ou après le changement de client.

Après mise à jour, compare les identifiants de version, l'état du client, la progression des paquets, les acknowledgements, les timeouts et la capacité à vérifier de nouvelles preuves. Si un problème apparaît, n'accepte pas arbitrairement les preuves en contournant le contrôle défaillant. Le chemin de reprise doit restaurer la vérification, pas supprimer la garantie pour que le tableau de bord redevienne vert.

## 32. Établir des critères d'acceptation et de sortie

Un protocole inter-chaînes doit avoir des critères d'acceptation avant l'ouverture à des actifs significatifs. Ils comprennent l'invariant de couverture, la protection contre le replay, la vérification de la source, la gestion des paquets en attente, les contrôles de rôles, la capacité de récupération et la surveillance. Les tests doivent être liés à ces propriétés afin qu'un échec soit interprétable.

Définis les limites de valeur et les conditions qui imposent un arrêt. Un bridge qui fonctionne correctement pour de petits montants peut avoir un risque d'exposition trop élevé si les limites de mint n'existent pas. Une alerte de divergence doit déclencher un responsable et un runbook. Les opérations exceptionnelles doivent être journalisées et approuvées selon une politique adaptée à leur impact.

La sortie d'incident doit vérifier la cohérence comptable sur les deux chaînes, l'état des messages et les droits de gouvernance. Ne reprends pas les transferts uniquement parce que le relayer ou l'API est de nouveau disponible. Une route peut être joignable alors que des messages invalides sont encore en attente ou que les réserves ne correspondent plus à l'offre de représentation.

Les critères de reprise peuvent exiger une série de tests nominals, un test de rejeu, une réconciliation des messages en transit, la validation de la nouvelle configuration et une observation prolongée. En cas d'écart inexpliqué, maintiens les opérations sensibles en attente. La décision doit être documentée, révisable et assignée à une autorité connue.

## 33. Étude de cas : transfert multi-hop et dépendances cumulées

Un utilisateur veut déplacer un actif depuis la chaîne A vers la chaîne C. Le parcours utilise une route A vers B, puis une route B vers C. Chaque étape peut avoir sa propre finalité, ses contrats, ses relayers, ses frais et ses hypothèses de sécurité. Le fait que la première étape ait réussi ne garantit pas que la seconde soit exécutée, et le produit doit rendre visible l'état intermédiaire.

Avant d'autoriser le transfert, cartographie chaque étape et les conditions de passage. Identifie l'actif original, les représentations possibles, les frais, les confirmations requises, les preuves attendues et les procédures d'échec. Si l'étape A vers B crée une représentation enveloppée qui est ensuite utilisée comme actif source sur B, assure-toi que l'application connaît son identité exacte et son mécanisme de rachat.

Le modèle de risque doit considérer les pannes cumulées. Si le premier bridge fonctionne mais que le second est indisponible, l'utilisateur peut détenir un actif sur B au lieu de C. Si le relayer de la seconde route est bloqué, le message peut rester en attente sans que la première transaction soit annulée. Si une des routes dépend d'un comité et l'autre d'un client léger, leurs risques ne peuvent pas être résumés par un seul statut « transfert sécurisé ».

L'interface doit afficher un statut par étape, l'actif courant, le hash de chaque transaction, la route choisie et les actions possibles. Les messages doivent prévenir l'utilisateur avant qu'il répète la demande. Une opération de secours doit déterminer si l'actif existe déjà sur B et si une nouvelle demande créerait un doublon. La récupération doit suivre les règles des contrats et ne pas simplement renvoyer le même montant sur C.

Le test d'acceptation simule le succès de la première étape suivi d'une panne de la seconde, puis une reprise. Il vérifie que l'actif n'est ni perdu ni émis deux fois, que l'état de chaque étape reste consultable et que la procédure de récupération est compréhensible pour le support. Ce scénario révèle pourquoi le multi-hop exige une comptabilité et une observabilité par étape.

## 34. Checklist avant la mise en production d'une route inter-chaînes

La revue de préproduction doit confirmer l'identité des deux réseaux, les contrats source et destination, les autorités de vérification, la politique de finalité, les protections contre le replay et l'invariant comptable. Les relayers doivent avoir une configuration connue, des accès limités et un mécanisme de reprise qui ne modifie pas arbitrairement la sécurité du protocole.

Teste les cas nominaux et les échecs : message valide, message mal formé, preuve d'un autre domaine, soumission répétée, timeout, retard de finalité, mise à jour de client et erreur de réception. Vérifie l'état des actifs et les événements après chaque cas. La suite de tests doit être reproductible et conserver les versions des contrats, clients et outils.

La surveillance doit relier les deux chaînes et les identifiants de message. Elle doit pouvoir distinguer la source non finale, le message non relayé, la preuve refusée, l'exécution destination échouée et l'indexeur en retard. Un seul indicateur « bridge en ligne » ne suffit pas. Les alertes concernant la couverture d'actifs, les mints anormaux ou les changements de clés doivent déclencher une réponse adaptée.

Enfin, teste le runbook avec une personne qui n'a pas développé le protocole. Cette personne doit pouvoir retrouver les contrats officiels, collecter les identifiants, éviter une soumission en double et décider quand escalader l'incident. Les limites de la procédure doivent être indiquées. Toute information qui n'a pas été testée doit être déclarée comme telle.

La publication devrait être bloquée si une propriété essentielle reste inconnue, si l'ancienne autorité de vérification peut encore agir sans contrôle prévu, si un message peut être consommé deux fois ou si l'équipe ne sait pas comment réconcilier les actifs après une panne. Une route est prête lorsque son comportement nominal et ses modes d'échec sont compris, testés et surveillés.

## 35. Rapport d'observabilité et revue périodique d'une route

Pour chaque route inter-chaînes, conserve un rapport qui associe les identifiants source et destination aux événements de progression. Le rapport doit indiquer l'âge des paquets en attente, le nombre d'acknowledgements et de timeouts, les changements de client, les changements de rôle et les écarts de comptabilité. Il doit aussi distinguer les données mesurées des hypothèses d'opérateur.

Une revue périodique vérifie que les contrats et versions correspondent à la documentation, que les rôles demeurent contrôlés et que la procédure de reprise est encore valide. Les intégrations peuvent évoluer et une nouvelle route peut créer un chemin indirect qui modifie le modèle de risque. Réévalue l'exposition totale, pas seulement chaque transfert isolément.

La revue est terminée lorsque les écarts sont expliqués, les alertes ont un propriétaire, les tests d'échec ont été rejoués selon un calendrier et le runbook est accessible à une équipe qui n'a pas développé le système. Si une preuve manque ou si un pouvoir d'administration a changé sans revue, marque le risque comme ouvert et définis le responsable de l'action suivante.

## 36. Dix questions d'entraînement avec corrigé

### Question 1 : Un bridge transporte-t-il littéralement le même état entre deux chaînes ?

**Correction :** Non. Il utilise un mécanisme qui permet à une chaîne destination d'accepter une preuve, un message ou une instruction liée à l'événement de la source. Les règles et la sécurité de chaque chaîne restent distinctes.

### Question 2 : Quelle différence entre un bridge d'actifs et un bridge de messages ?

**Correction :** Le premier facilite un transfert économique ou la création d'une représentation d'actif. Le second transmet des données ou des appels pouvant déclencher une action sur la destination. Certains systèmes combinent les deux.

### Question 3 : Le relayer est-il nécessairement une autorité de confiance ?

**Correction :** Non. Dans de nombreux protocoles il transporte les données et les preuves, tandis que la destination authentifie le message. Il peut cependant rester un point de disponibilité si aucun relayer alternatif n'existe.

### Question 4 : Pourquoi attendre la finalité de la source ?

**Correction :** Pour réduire le risque qu'un événement source soit retiré par une réorganisation après que la destination a déjà exécuté un effet irréversible.

### Question 5 : Qu'est-ce qu'un replay ?

**Correction :** La réutilisation d'un message ou d'une signature dans un contexte où son effet ne devrait se produire qu'une fois. Les identifiants, nonces et preuves de consommation servent à l'empêcher.

### Question 6 : Pourquoi un actif enveloppé peut-il perdre sa valeur ?

**Correction :** Sa valeur dépend de la confiance dans la possibilité de le racheter contre l'actif sous-jacent. Une faille, un déficit de réserve, un bridge bloqué ou des pouvoirs compromis peuvent rompre cette confiance.

### Question 7 : Que font acknowledgements et timeouts dans un protocole de paquets ?

**Correction :** Ils rendent observable le résultat du traitement ou permettent de résoudre un paquet qui n'a pas été traité dans le délai prévu. Leur usage exact dépend du protocole.

### Question 8 : Quel est l'intérêt d'un client léger ?

**Correction :** Il permet de vérifier certaines assertions sur la chaîne distante sans faire confiance à un simple message fourni par un intermédiaire. Sa sécurité dépend de la correctitude de son implémentation, de ses paramètres et de ses mises à jour.

### Question 9 : Pourquoi la comptabilité est-elle essentielle ?

**Correction :** Parce que les actifs verrouillés, brûlés, émis et libérés doivent respecter un invariant. Une duplication de message ou une preuve acceptée à tort peut créer des représentations sans couverture correspondante.

### Question 10 : Que faire si un transfert reste en attente ?

**Correction :** Identifier l'étape exacte, comparer les preuves et les états des deux chaînes, consulter la procédure du protocole et éviter une répétition aveugle. Il faut confirmer l'état de l'opération avant toute action de récupération.

## 37. Challenge final : évaluer une architecture multi-chaînes

Une application de finance décentralisée veut permettre à ses utilisateurs de déplacer un actif entre trois réseaux. Une route utilise une multisignature, une autre un client léger et une troisième une réserve de liquidité. Le produit souhaite afficher une interface uniforme alors que les délais, les frais et les hypothèses de confiance diffèrent.

### Travail demandé

Rédige un rapport d'architecture qui compare les trois routes, définit les critères de choix, décrit les protections contre le replay, documente la comptabilité des actifs, établit la surveillance et prépare un plan d'incident. Indique ce que l'interface doit afficher pour que l'utilisateur ne confonde pas une transaction source terminée avec un transfert destination finalisé.

### Correction proposée

Le rapport compare explicitement la vérification, les acteurs de confiance, la disponibilité, les délais, les clés, les pouvoirs d'administration, la sortie et le mécanisme de reprise. Chaque message possède un identifiant lié au domaine, à la source et à la destination. La destination vérifie les preuves, vérifie que l'opération n'a pas déjà été consommée et respecte les règles métier.

La comptabilité distingue les actifs originaux, les représentations, les messages en transit, les retraits et les frais. Les alertes surveillent les paquets trop anciens, les écarts de réserves et les changements de configuration. L'interface affiche des états distincts pour la source, le message et la destination, avec les délais et risques propres à la route choisie.

Le plan d'incident empêche les répétitions aveugles, précise qui peut suspendre la route, protège les preuves, impose une réconciliation et définit des critères de reprise testables. Le résultat ne prétend pas que toutes les routes sont équivalentes : il rend les hypothèses compréhensibles et permet à l'application de choisir en fonction du risque métier.

## Glossaire

**Interopérabilité** : capacité de systèmes distincts à échanger des informations ou des actifs selon des règles vérifiables.

**Bridge** : protocole ou système qui facilite la communication ou le transfert de valeur entre chaînes.

**Actif enveloppé** : représentation d'un actif dans un autre domaine, dont la valeur dépend des mécanismes de rachat et de sécurité.

**Relayer** : composant qui transporte paquets, messages ou preuves entre chaînes.

**Client léger** : composant qui vérifie certains éléments de l'état ou du consensus distant sans télécharger et traiter toutes les données de la chaîne.

**Replay** : réutilisation non autorisée d'une preuve, d'un message ou d'une signature.

**Nonce** : valeur utilisée pour distinguer ou ordonner des opérations et empêcher certaines répétitions.

**Acknowledgement** : réponse qui indique le résultat du traitement d'un paquet dans les protocoles qui l'utilisent.

**Timeout** : limite au-delà de laquelle un paquet peut suivre une procédure de récupération définie.

**IBC** : protocole Inter-Blockchain Communication conçu pour l'échange de paquets entre chaînes compatibles.

**Light client** : mécanisme de vérification d'un état distant à l'aide d'informations réduites et de preuves.

**Séparation de domaine** : méthode qui lie une signature ou un message à un réseau, un contrat, une fonction ou un contexte précis.

**Réconciliation** : comparaison des états et événements des deux chaînes pour détecter les divergences et confirmer la comptabilité.

## Pour aller plus loin

- Ethereum.org, bridges : https://ethereum.org/en/developers/docs/bridges/
- Documentation Cosmos, IBC : https://docs.cosmos.network/ibc/latest/
- Spécification IBC : https://github.com/cosmos/ibc
- Documentation Solidity : https://docs.soliditylang.org/
- OWASP Smart Contract Security : https://scs.owasp.org/

Les implémentations de bridge et les versions d'IBC évoluent. Pour une intégration de production, lis la spécification et les contrats effectivement déployés, vérifie les paramètres du client et les rôles d'administration, puis teste le chemin d'échec et de reprise avant de déplacer des actifs réels.
