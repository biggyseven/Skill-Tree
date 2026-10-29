# Audit et sécurité smart contracts

## Encadré de mise en contexte

Un smart contract peut déplacer des actifs, attribuer des droits, enregistrer des votes, déterminer des liquidations ou contrôler l'accès à une application. Une erreur de logique ou de configuration peut ainsi avoir des conséquences bien plus importantes qu'un bug d'interface classique : les transactions sont publiques, les actions peuvent être irréversibles et les utilisateurs ne disposent pas toujours d'un service client capable d'annuler une opération.

La sécurité ne se résume pas à rechercher la réentrance ni à lancer un outil d'analyse statique. Un audit sérieux examine la logique métier, les permissions, les dépendances, les invariants, les mises à niveau, les hypothèses économiques et la manière dont le système sera exploité après son déploiement. Il vérifie également ce qui se passe lorsqu'un acteur est malveillant, lorsqu'un service externe est indisponible ou lorsque plusieurs faiblesse se combinent.

Ce cours présente une méthode de sécurité défensive qui va de la définition du modèle de menace jusqu'à la réponse à incident. Les exemples sont destinés à des environnements de laboratoire autorisés. Le but est d'apprendre à prévenir, détecter et contenir des défaillances, pas à attaquer des contrats réels.

## Objectifs d'apprentissage

Tu dois être capable de construire un modèle de menace, d'identifier les actifs et les pouvoirs, d'écrire des invariants testables, de planifier une revue de code, de combiner tests, fuzzing et analyse statique, d'évaluer les risques des oracles et des appels externes, d'examiner un proxy et ses rôles, de sécuriser le processus de déploiement, et d'écrire un plan d'intervention qui peut être exécuté sous pression.

## Prérequis et environnement

La leçon suppose que tu connais les bases de Solidity, l'EVM, les événements, le gas et les transactions. Le laboratoire doit utiliser une chaîne locale ou un réseau de test avec des comptes sans valeur réelle. Ne teste pas de stratégie de sécurité sur un contrat tiers sans autorisation explicite, et ne publie jamais une clé privée, une phrase de récupération ou un secret de déploiement dans un rapport.

Le parcours proposé est progressif : spécifier la règle métier, dresser l'inventaire des actifs, identifier les frontières de confiance, écrire les tests de base, ajouter les tests adverses, faire la revue de configuration, simuler l'incident, puis vérifier la récupération. Les outils d'audit aident à trouver des défauts, mais ne remplacent jamais la compréhension de ce que le contrat est censé garantir.

## 1. Sécurité comme propriété du système entier

La sécurité d'un contrat ne dépend pas seulement de son fichier Solidity. Le système inclut le bytecode déployé, les bibliothèques, les contrats appelés, les prix externes, les rôles administratifs, les scripts de déploiement, les frontends, les indexeurs et les procédures humaines. Un contrat correctement écrit peut devenir dangereux s'il est déployé à la mauvaise adresse, si son administrateur est contrôlé par une seule clé non protégée ou s'il lit une source de prix inadaptée.

Distingue les catégories de risque. Une vulnérabilité de code permet de violer une propriété technique ou métier. Une erreur de configuration peut pointer vers un mauvais oracle ou laisser une permission excessive. Un défaut opérationnel peut empêcher la pause d'urgence d'être déclenchée à temps. Un risque économique peut permettre de manipuler une hypothèse de marché valide du point de vue du code. Un risque de gouvernance peut permettre à un acteur autorisé de faire modifier les règles sans contrôle suffisant.

Un audit doit examiner toutes ces catégories et préciser les frontières de son travail. « Le contrat est audité » n'indique pas ce qui a été examiné, avec quelle version, par quel outil, ni si les changements ultérieurs sont couverts. Une décision d'acceptation exige une portée explicite et une date.

## 2. Inventorier les actifs et les privilèges

Commence par recenser ce que le système protège ou contrôle : soldes de jetons, monnaie native, droits de retrait, privilèges de mint, votes, garanties, paramètres de liquidation, références d'oracle, clés de mise à niveau et données qui déterminent une décision. Évalue l'impact si chacun de ces éléments est perdu, modifié ou rendu indisponible.

Identifie ensuite les acteurs : utilisateurs ordinaires, administrateurs, opérateurs, relayers, validateurs, fournisseurs d'oracle, multisignatures, bots de liquidation, intégrateurs et contrats externes. Pour chaque acteur, note les actions possibles, les limites de pouvoir et les mécanismes d'approbation. Ne confonds pas la personne qui soumet une transaction avec celle qui peut changer la règle que la transaction exécute.

Un inventaire de privilèges doit également répertorier les pouvoirs indirects. Une fonction qui peut changer l'adresse d'un oracle est presque aussi critique que l'oracle lui-même. Un rôle qui peut mettre à niveau l'implémentation peut modifier n'importe quelle hypothèse de sécurité future. Un rôle qui peut mettre une pause peut protéger les fonds en cas d'urgence, mais peut aussi bloquer une opération nécessaire si sa portée est trop large.

| Actif ou pouvoir | Conséquence d'une compromission | Contrôle attendu |
|---|---|---|
| Fonds ou garanties | Perte, transfert non autorisé ou insolvabilité | Invariants financiers et tests adverses |
| Rôle administrateur | Changement de paramètres ou des droits | Multisignature, délai, séparation des tâches |
| Adresse d'oracle | Décisions basées sur des données incorrectes | Liste d'adresses approuvées et validation |
| Implémentation proxy | Remplacement des règles de contrat | Procédure de mise à niveau et validation du stockage |
| Clé de publication | Déploiement d'un artefact non approuvé | Environnement contrôlé et approbation indépendante |
| Infrastructure d'indexation | Affichage ou traitement de données incorrectes | Réconciliation avec les événements et l'état on-chain |

## 3. Construire un modèle de menace

Un modèle de menace répond à quatre questions : qu'est-ce qui doit être protégé, qui peut tenter de le compromettre, quelles conditions l'attaquant peut influencer et quelles propriétés doivent demeurer vraies. Il doit considérer les utilisateurs honnêtes qui commettent des erreurs, les contrats externes qui se comportent de façon inattendue, les acteurs privilégiés qui abusent de leurs droits et les adversaires capables de combiner plusieurs interactions.

Les frontières de confiance sont les endroits où une hypothèse change : un appel externe, une donnée d'oracle, un message signé, un changement de réseau, une transaction relayée, une mise à niveau ou une interaction avec un service hors chaîne. À chaque frontière, note le format attendu, le contrôle qui le valide, l'échec possible et l'action sûre en cas d'incertitude.

Un modèle utile ne prétend pas prédire toutes les attaques. Il rend les hypothèses lisibles et aide à prioriser les tests. Si le protocole suppose qu'un administrateur reste honnête, il faut le dire. Si la sécurité dépend d'un oracle qui publie une valeur suffisamment fraîche, la limite de fraîcheur doit être définie. Si une fonction devient inutilisable lorsque la liste d'éléments dépasse une taille donnée, cette limite doit faire partie de la spécification.

~~~mermaid
flowchart TD
    A[Définir les actifs] --> B[Identifier les acteurs]
    B --> C[Tracer les frontières de confiance]
    C --> D[Écrire les invariants]
    D --> E[Construire les scénarios adverses]
    E --> F[Tests, outils et revue manuelle]
    F --> G[Classer les constats]
    G --> H[Corriger et retester]
    H --> I[Surveiller le système déployé]
~~~

## 4. Écrire des invariants métier testables

Un invariant est une propriété qui doit rester vraie après toute séquence d'opérations autorisée. Exemples : un utilisateur ne retire pas plus que son crédit ; une même demande de retrait ne peut pas être exécutée deux fois ; l'offre de jetons respecte les règles d'émission ; un prix utilisé pour une liquidation est valide selon une politique écrite ; une fonction administrative rejette tout compte qui ne détient pas le rôle requis.

Évite les exigences vagues. « Les fonds sont sécurisés » n'est pas testable. « Pour tout utilisateur, le cumul des retraits réussis ne dépasse pas les dépôts comptabilisés, ajustés des frais explicitement définis » décrit une propriété qui peut être mise à l'épreuve. Un invariant doit aussi préciser ses exceptions légitimes : frais, transferts externes, pertes de valeur ou opérations de gouvernance.

Une interface ne constitue pas une règle du contrat. Désactiver un bouton n'empêche pas un utilisateur d'appeler directement une fonction publique. Les vérifications importantes doivent vivre dans le code on-chain et être testées en appel direct. Les contrôles de l'interface améliorent l'expérience ; ils ne remplacent pas les contrôles d'autorisation.

~~~mermaid
flowchart LR
    A[Actifs et objectifs] --> B[Acteurs et pouvoirs]
    B --> C[Frontières de confiance]
    C --> D[Invariants]
    D --> E[Scénarios adverses]
    E --> F[Tests et preuves]
~~~

## 5. Accès et rôles : éviter le privilège implicite

Toute fonction qui peut déplacer un actif, modifier une configuration critique, émettre des jetons ou changer une référence de confiance doit avoir une politique d'autorisation claire. Les rôles peuvent séparer les responsabilités, par exemple une personne qui propose un changement, une multisignature qui l'approuve et une fonction d'urgence qui peut interrompre certaines opérations.

Une revue des permissions vérifie les fonctions déclarées, les modificateurs, les chemins internes, les constructeurs, les fonctions d'initialisation des proxies et les opérations de transfert de rôles. Le risque ne se limite pas à une fonction explicitement appelée admin : un mauvais initialiseur ou une fonction non protégée peut conférer des privilèges inattendus. Il faut aussi vérifier le transfert et la révocation des rôles après le déploiement.

L'architecture d'urgence doit être conçue avant l'incident. Une pause peut arrêter les dépôts mais laisser les retraits accessibles, ou inversement, selon le besoin. Ne suppose pas qu'une pause globale est toujours sûre : elle peut empêcher une sortie légitime ou un correctif. Définis les opérations bloquées, les opérations qui restent possibles, qui peut déclencher la pause, et quelles conditions autorisent la reprise.

## 6. Logique métier et erreurs de conception

Un contrat peut n'avoir aucun bug de mémoire ou d'arithmétique et rester vulnérable parce que la logique métier est incorrecte. Exemple : une fonction permet à un utilisateur de retirer une récompense calculée à partir d'une période qui n'a pas encore commencé ; une règle de vote applique un poids deux fois ; un contrat de prêt calcule la garantie sur un prix qui ne correspond pas à l'actif ; un mécanisme de récompense suppose que les utilisateurs ne peuvent pas créer plusieurs comptes.

Les tests doivent modéliser des séquences, pas seulement des appels individuels. Une opération légitime peut créer un état qui rend une opération ultérieure dangereuse. Les tests de propriétés permettent d'explorer plusieurs comptes, montants, intervalles et ordres d'appel. Le fuzzing peut faire apparaître des cas extrêmes que l'auteur n'a pas imaginés.

Les dépendances de marché nécessitent une analyse spécifique. Les prêts flash ne sont pas à eux seuls une vulnérabilité ; ils rendent simplement accessibles, dans une même transaction, des quantités importantes de capital temporaire. Une application qui suppose qu'un prix, un vote ou une liquidité de pool est impossible à manipuler pendant une transaction peut se tromper. Il faut examiner les hypothèses économiques, la structure de marché et les possibilités d'arbitrage.

## 7. Réentrance et appels externes

La réentrance apparaît lorsqu'un contrat appelle un autre contrat qui peut rappeler le contrat initial avant que la séquence d'origine soit terminée. Le risque dépend de l'ordre des mises à jour, des fonctions réentrantes disponibles, du partage de l'état et des invariants. Il ne suffit pas de rechercher une méthode de transfert ou d'ajouter mécaniquement un modificateur de garde sans comprendre le flux.

Le principe checks-effects-interactions recommande de vérifier les préconditions, de mettre à jour l'état local puis d'effectuer l'interaction externe lorsque ce modèle convient. Une protection dédiée contre la réentrance peut être utile, mais elle n'élimine pas toutes les erreurs de logique. Plusieurs fonctions peuvent partager un même état et se rendre vulnérables à un rappel indirect.

Tous les appels externes méritent une vérification de la valeur de retour et du comportement en cas d'échec. Les contrats appelés peuvent revert, renvoyer des données inattendues ou effectuer des opérations qui n'étaient pas prévues dans le modèle de confiance. Lorsque des jetons non standard sont pris en charge, le contrat doit être conçu pour leur comportement documenté plutôt que supposer que tous les jetons ont les mêmes détails d'implémentation.

## 8. Oracles et données externes

Un contrat n'observe pas directement le monde extérieur. Lorsqu'il se fonde sur un prix, une météo, un résultat de jeu ou une identité externe, il dépend d'un oracle et de son modèle de mise à jour. Vérifie l'adresse de la source, le réseau, les unités, les décimales, l'horodatage, les valeurs anormales et le comportement si l'appel échoue.

La fraîcheur doit être une règle métier. Un prix valide à un instant peut devenir inadapté pendant une volatilité importante. À l'inverse, rejeter chaque variation forte peut empêcher le système de réagir à un mouvement réel du marché. La stratégie doit préciser si une donnée trop ancienne bloque l'opération, déclenche une pause, demande une seconde source ou suit une politique de secours.

Ne traite pas plusieurs oracles comme indépendants simplement parce qu'ils ont des adresses différentes. Ils peuvent dépendre des mêmes marchés, fournisseurs, données ou opérateurs. L'audit doit documenter la source de valeur, ses hypothèses de disponibilité et l'impact d'une valeur erronée sur le protocole.

## 9. Validation des entrées et arithmétique

Tout paramètre externe doit être évalué à travers les hypothèses qu'il porte. Une adresse peut être le zéro address, un contrat imprévu ou un contrat légitime mais non compatible. Un montant peut être nul, trop grand, sous le minimum économique ou incompatible avec les unités. Un tableau peut être vide, trop long ou contenir des doublons. Les limites doivent être définies selon le métier et testées sur les valeurs frontières.

Solidity dispose de contrôles arithmétiques dans les versions modernes pour les opérations ordinaires, mais les conversions explicites, les opérations dans unchecked, les divisions entières et les changements d'échelle demandent une analyse attentive. Une formule en virgule fixe doit décrire son échelle, son arrondi et la manière dont elle gère les petites valeurs. Les tests doivent inclure les limites exactes, pas seulement des valeurs moyennes.

Les calculs de prix et de garantie peuvent être corrects d'un point de vue syntaxique mais mauvais économiquement. Vérifie la cohérence des unités et l'ordre des opérations : une division anticipée peut perdre de la précision, tandis qu'une multiplication trop tôt peut dépasser les bornes prévues. La spécification doit permettre à une personne extérieure de reproduire le calcul.

## 10. Déni de service et dépendances de disponibilité

Un contrat peut devenir inutilisable si une boucle grandit sans limite, si une dépendance externe revert systématiquement ou si une action exige qu'un utilisateur particulier réponde. Les fonctions critiques ne devraient pas dépendre d'une liste dont la taille peut croître sans borne lorsque le gas maximal rendra la fonction inexécutable. Les traitements peuvent parfois être scindés en lots ou conçus pour que chaque utilisateur puisse progresser indépendamment.

Examine les appels qui doivent tous réussir pour qu'une transaction avance. Une boucle qui appelle de nombreux destinataires et revert si l'un d'eux échoue peut bloquer l'ensemble du traitement. Une architecture qui autorise l'échec isolé d'une tâche peut être plus robuste, mais elle doit aussi définir comment les résultats partiels sont enregistrés et repris.

Le déni de service inclut les opérations économiques : un attaquant peut remplir une file de requêtes, créer beaucoup de petits objets ou augmenter le coût de calcul d'une fonction, même si aucune erreur de mémoire n'existe. Les limites de débit, les frais, les plafonds et les mécanismes d'anti-abus sont des décisions de conception, pas des ajouts improvisés après une attaque.

## 11. Mises à niveau et proxies

Un proxy garde une adresse d'entrée stable tout en déléguant généralement l'exécution à une implémentation. L'architecture facilite les corrections et l'évolution, mais la capacité de changer l'implémentation devient un pouvoir extrêmement sensible. Le risque comprend les mauvaises mises à niveau, les erreurs de stockage, un administrateur compromis, un délai insuffisant et un changement de gouvernance non compris.

La revue doit examiner l'initialisation, la protection contre une initialisation non autorisée, le stockage et ses compatibilités, les rôles d'upgrade, les événements de changement d'implémentation et les contrôles de validation des artefacts. Les variables de stockage ne peuvent pas être réordonnées sans risque dans de nombreux modèles de proxy ; une nouvelle version peut interpréter les anciennes données de travers même si elle compile.

Une procédure de mise à niveau sûre inclut une compilation reproductible, des tests sur copie de l'état, une validation des différences de stockage, une vérification des rôles, une revue indépendante et un rapport post-déploiement. Si le système ne peut pas revenir proprement à l'ancienne implémentation, le plan doit le dire explicitement et préciser les options de récupération.

~~~mermaid
flowchart TD
    A[Spécification et invariants] --> B[Tests unitaires]
    B --> C[Tests d'intégration]
    C --> D[Fuzzing et tests de propriétés]
    D --> E[Revue manuelle et outils]
    E --> F[Correction]
    F --> G[Tests de régression]
    G --> H[Validation de la version publiée]
~~~

## 12. Tests unitaires, tests d'intégration et fuzzing

Les tests unitaires couvrent des fonctions et des scénarios définis. Les tests d'intégration examinent les interactions entre les contrats et les services. Les tests fondés sur des propriétés vérifient des règles générales après une succession d'actions. Le fuzzing explore de nombreuses entrées ; il est utile pour découvrir des combinaisons inattendues mais ne prouve pas l'absence d'une vulnérabilité.

Une suite de tests de sécurité doit comprendre des appels depuis plusieurs comptes, des montants extrêmes, des appels répétés, des expirations, des transactions remplacées et des dépendances externes simulées. Il faut tester à la fois la réussite et les échecs. Si une transaction revert, vérifie les invariants après le revert et la cause réelle de l'échec. La simple présence d'une exception ne démontre pas que le contrat est resté sûr.

Pour les systèmes financiers, teste aussi l'évolution des grandeurs globales : total des dépôts, total des retraits, offre de jetons, garanties, dettes, frais et récompenses. Le modèle doit préciser si ces grandeurs devraient être égales, bornées ou reliées par une formule. Les tests de propriétés prennent plus de valeur lorsque les invariants ont été écrits avant l'implémentation.

## 13. Analyse statique, symbolique et vérification formelle

L'analyse statique inspecte le code sans exécuter tous les chemins possibles. Elle peut détecter des motifs dangereux, des permissions manquantes, des retours de valeur ignorés et certaines erreurs de logique. Ses résultats doivent être triés : un outil peut produire des faux positifs, manquer une vulnérabilité liée au modèle métier ou ne pas comprendre une dépendance dynamique.

L'exécution symbolique cherche à explorer des chemins avec des contraintes symboliques, afin d'identifier certains états impossibles ou contre-exemples. La vérification formelle peut établir des propriétés précises sous des hypothèses définies. Ces techniques sont puissantes, mais la qualité de la spécification et les frontières du modèle restent essentielles. Prouver une fonction ne démontre pas automatiquement que le protocole économique autour d'elle est sûr.

Un audit devrait documenter les outils et versions, les commandes utilisées, les limites et les constats validés manuellement. L'absence de résultat signifie seulement qu'aucun outil ou examen n'a identifié un problème dans le périmètre et sous les hypothèses considérés. N'utilise pas une capture d'écran avec des coches vertes comme substitut à un rapport de sécurité.

## 14. Supply chain et reproductibilité

La source lue par l'auditeur doit correspondre au code déployé. Verrouille la version du compilateur, les paramètres d'optimisation, les versions des dépendances et la configuration de déploiement. Évite les dépendances à une branche mobile ou les imports qui peuvent changer sans revue. Une mise à jour de bibliothèque peut modifier la logique, les rôles ou les conventions de stockage.

Les secrets de déploiement doivent être gérés en dehors du dépôt. Les pipelines doivent utiliser des identités et des permissions limitées, empêcher les publications non approuvées et conserver un journal des artefacts construits. La séparation entre préparation et approbation évite qu'un seul compte compromis puisse modifier le code, déclencher le déploiement et approuver le changement sans contrôle.

La vérification après déploiement compare l'adresse, le réseau, le bytecode lorsque c'est possible, le code source vérifié, le hash du bloc, les rôles et la configuration initiale. Elle doit aussi confirmer les valeurs des oracles, les adresses des jetons et les paramètres d'urgence. Un artefact parfaitement compilé peut rester dangereux si l'adresse de destination est incorrecte.

## 15. Évaluer un constat de sécurité

Un constat doit contenir le contexte, la précondition, le chemin qui produit le problème, l'impact potentiel, les preuves, la sévérité, la recommandation et le plan de validation. Il doit être assez précis pour que le développeur puisse reproduire le problème, mais il ne doit pas prétendre qu'un impact a été observé si seule une hypothèse théorique a été identifiée.

La sévérité dépend de la portée de l'actif, de la facilité d'exploitation, du privilège nécessaire, de la possibilité de récupération et des conséquences sur la disponibilité. Le même défaut peut avoir un impact limité dans un prototype sans actifs et critique dans un protocole qui garde des fonds. La notation doit être justifiée, pas attribuée uniquement par le nom de la catégorie.

Une correction doit être testée contre le scénario qui a révélé le défaut et contre les chemins voisins. Après le correctif, vérifie que l'invariant initial tient toujours et que les fonctionnalités légitimes n'ont pas été cassées. Les changements de permission, de pause ou de limites doivent également être examinés pour éviter de transférer le risque d'un endroit à un autre.

## 16. Plan d'urgence et réponse à incident

Un incident confirmé exige d'abord de qualifier la portée, de préserver les preuves et de protéger les utilisateurs. Si une pause ou un mécanisme d'urgence existe, la décision d'activation doit respecter le modèle d'autorisation et les règles publiées. Ne tente pas une transaction improvisée sur un contrat réel en espérant récupérer les fonds ; une opération on-chain est publique et peut être irréversible.

Le dossier doit inclure le réseau, les adresses exactes, les hashes de transactions, le bloc de référence, la version du code et les pouvoirs encore actifs. Identifie ce qui est connu et ce qui reste une hypothèse. Sépare les mesures d'endiguement immédiates de la correction définitive. Communique clairement si les retraits sont suspendus, si les soldes affichés sont provisoires ou si une procédure est encore en cours de validation.

Après l'endiguement, analyse la cause racine, reproduis le scénario dans un environnement contrôlé, ajoute un test de régression, examine les permissions et le processus de publication, puis organise une revue indépendante de la correction si l'impact est élevé. Une reprise exige un critère vérifiable : états cohérents, vecteur bloqué, configuration contrôlée, surveillance active et procédure de sortie opérationnelle.

~~~mermaid
sequenceDiagram
    participant M as Monitoring
    participant R as Responsable d'incident
    participant C as Contrat / gouvernance
    participant U as Utilisateurs
    M->>R: Alerte et preuves disponibles
    R->>R: Qualifier portée et hypothèses
    R->>C: Décision d'urgence autorisée
    C-->>R: Résultat de l'action
    R->>U: Communiquer le statut vérifié
    R->>R: Vérifier les critères de reprise
~~~

## 17. TP guidé A : écrire un modèle de menace

Choisis un contrat pédagogique de dépôt ou de vote. Énumère les actifs et les pouvoirs, puis dessine les frontières de confiance. Écris cinq invariants et trois scénarios adverses. Pour chaque scénario, précise l'entrée, le prérequis, le résultat attendu et le contrôle qui doit l'empêcher.

### Correction proposée

Une bonne fiche nomme les éléments précis plutôt que d'écrire simplement « le contrat est sécurisé ». Exemple : le pouvoir de changer l'adresse d'oracle appartient à un rôle distinct ; une donnée trop ancienne doit bloquer une liquidation ; une même demande ne peut pas produire deux paiements ; et le chemin de reprise exige un contrôle de configuration. Les scénarios sont testables et incluent ce que le système doit faire lorsque la dépendance est indisponible.

## 18. TP guidé B : construire une matrice de tests adverses

Crée une matrice pour les permissions, les montants, les appels externes, les oracles, les réorganisations et les mises à niveau. Inclue les cas nominaux, les valeurs frontières, les utilisateurs non autorisés, les erreurs des dépendances et les répétitions. Pour chaque test, note l'invariant observé, la configuration et la preuve collectée.

### Correction proposée

La matrice est utile si chaque ligne correspond à une propriété que l'équipe souhaite vérifier. Les tests doivent vérifier les événements et l'état après l'opération. Les erreurs attendues doivent être distinguées des échecs de l'environnement de test. Les paramètres aléatoires doivent pouvoir être reproduits si le fuzzing trouve un contre-exemple.

## 19. Étude de cas : l'audit est terminé, mais le déploiement reste risqué

Un rapport indépendant examine une version de contrat et ne signale aucun défaut critique. Entre l'audit et le déploiement, l'équipe met à jour une bibliothèque, change le rôle d'administration et remplace l'adresse d'oracle. Le déploiement fonctionne, mais personne n'a comparé les paramètres avec le rapport initial.

### Travail demandé

Identifie les preuves à récupérer, les éléments à revalider et les contrôles de publication qui auraient empêché cette dérive. Écris une procédure de mise en production.

### Correction proposée

L'équipe doit comparer le code et les dépendances au périmètre audité, exécuter à nouveau les tests et les outils pertinents, valider le rôle d'administration et vérifier l'adresse exacte de l'oracle sur le bon réseau. Le processus doit archiver l'artefact et sa configuration, exiger une approbation indépendante des changements sensibles et confirmer après déploiement que les contrats et permissions correspondent à l'état approuvé.

## 20. Utiliser une taxonomie de risques sans réduire l'audit à une checklist

Une taxonomie de vulnérabilités aide à organiser une revue et à comparer des constats. Elle ne constitue pas une garantie de couverture. OWASP Smart Contract Security publie un Top 10 qui reflète des catégories de risques importantes, dont les défauts de contrôle d'accès, les erreurs de logique métier, la manipulation d'oracles, les attaques facilitées par les prêts flash, la validation insuffisante des entrées, les appels externes non vérifiés, les erreurs arithmétiques, la réentrance et les risques de mise à niveau. L'ordre et les intitulés peuvent évoluer d'une édition à l'autre ; consulte la version actuelle pour une revue de production.

La taxonomie sert à poser des questions, pas à conclure automatiquement qu'une classe est absente. Un contrôle d'accès peut être correct localement mais contourné par une fonction d'initialisation ou un proxy mal configuré. Une source de prix peut être correctement interrogée mais utilisée avec la mauvaise échelle. Un appel externe peut vérifier son résultat mais participer à une attaque économique qui rend l'opération rentable pour l'adversaire. Il faut donc suivre la chaîne causale complète.

Construis une matrice de couverture en associant chaque catégorie à un ou plusieurs invariants, aux fonctions concernées, aux tests exécutés et à une preuve de revue. Marque séparément les catégories non applicables et celles qui sont encore inconnues. Une absence de code correspondant à un motif attendu n'est pas suffisante si la logique équivalente est implémentée ailleurs.

Les catégories de risque ne doivent pas être traitées comme des cases indépendantes. Les scénarios graves combinent souvent plusieurs faiblesses : privilège excessif, prix manipulable, absence de plafond et délais de pause trop courts. Une revue solide explore ces chaînes d'exploitation et évalue le résultat métier, pas uniquement la gravité isolée de chaque ligne de code.

## 21. Construire des arbres d'attaque et une carte des dépendances

Un arbre d'attaque décrit un objectif non autorisé — par exemple augmenter une offre, retirer des garanties ou faire accepter un prix erroné — puis les chemins qui pourraient mener à cet objectif. Les branches peuvent représenter des voies alternatives ou des conditions qui doivent être réunies. Cet outil oblige l'auditeur à rechercher plusieurs chemins plutôt que de se concentrer uniquement sur la fonction la plus visible.

Commence par dessiner les composants : contrats, oracles, bibliothèques, rôles, interfaces, relayers, indexeurs et scripts de déploiement. Relie-les selon les appels, les permissions et les dépendances de données. Pour chaque connexion, note qui contrôle le composant, comment son résultat est vérifié et quel comportement apparaît en cas de panne. Une dépendance externe n'est pas un risque secondaire si le contrat lui confie une décision de valeur.

Ensuite, écris des scénarios adverses. « Un rôle d'administration est compromis » doit être détaillé : quels pouvoirs possède-t-il, quels plafonds limitent son action, quelles alertes se déclenchent, quels délais existent et l'utilisateur peut-il sortir avant qu'un changement devienne actif ? « L'oracle publie une valeur incorrecte » doit conduire à examiner la fraîcheur, les unités, la variation, la durée pendant laquelle la valeur peut être utilisée et l'existence d'un mode sûr.

Évalue les chemins composés. Une dépendance peut être faible isolément mais critique lorsque deux autres protections manquent. Si l'administrateur peut changer l'oracle immédiatement et que l'application n'a pas de mécanisme de pause, l'effet combiné est plus important que la somme de deux constats indépendants. Le rapport final doit mettre en évidence les chemins qui mènent à une perte réelle ou à un blocage majeur.

## 22. Approfondir les tests fondés sur des propriétés

Les tests fondés sur des propriétés vérifient une règle de façon répétée à travers différentes entrées et séquences d'appels. Ils sont particulièrement utiles lorsque l'espace des états est trop grand pour écrire un test unitaire pour chaque scénario. Pour un coffre, une propriété peut exprimer que le crédit d'un utilisateur reste inférieur ou égal aux dépôts nets reconnus, selon la comptabilité définie. Pour une gouvernance, un vote ne doit pas être utilisé plus d'une fois et les droits de proposition doivent suivre les règles spécifiées.

Un harness de test doit représenter plusieurs rôles et des contrats auxiliaires qui simulent le comportement externe. Ne teste pas seulement des utilisateurs coopératifs ; ajoute un destinataire qui revert, un contrat qui tente un rappel, un oracle qui renvoie une donnée trop ancienne et un acteur qui tente d'appeler directement une fonction interne au flux d'une action publique.

Le générateur de séquences doit pouvoir répéter les dépôts, les retraits, les pauses, les modifications de configuration, les expirations et les transferts. Après chaque étape, vérifie les invariants pertinents. Lorsqu'un échec est trouvé, conserve la séquence minimale qui le reproduit, la graine du fuzzing, la version du compilateur et la configuration de test. Une correction doit ajouter un test de régression déterministe, même si le fuzzing est également conservé.

Les propriétés nécessitent des préconditions explicites. Si un contrat peut accepter des donations externes ou des frais, la relation entre soldes et crédits doit en tenir compte. Un invariant trop simplifié peut signaler des faux positifs ou pousser à modifier une règle métier qui est en réalité voulue. La spécification doit être discutée avec le propriétaire du protocole et testée sur des scénarios normaux avant de lancer un fuzzing intensif.

## 23. Durcir les pouvoirs d'administration et de gouvernance

Un rôle puissant ne doit pas dépendre d'une seule clé personnelle conservée sur un poste de développement. Pour les actifs ou paramètres critiques, évalue une multisignature, une séparation des responsabilités, des délais de timelock et une procédure de rotation. Le bon mécanisme dépend du besoin : un pouvoir d'urgence peut devoir agir rapidement, tandis qu'une mise à niveau non urgente peut tolérer un délai donnant aux utilisateurs le temps d'examiner ou de quitter le système.

Inventorie chaque fonction privilégiée et les effets qu'elle peut provoquer. Change-t-elle la logique exécutée, l'adresse d'un oracle, un plafond, les frais, les actifs supportés ou la capacité de pause ? Certains paramètres semblent petits mais modifient l'économie du protocole. Le rapport doit expliciter quels pouvoirs permettent de contourner les garanties annoncées aux utilisateurs.

Les transferts de rôle doivent être testés avant le déploiement. Vérifie que le nouveau rôle a bien été attribué, que l'ancien a perdu le pouvoir attendu, que les fonctions d'urgence restent accessibles par l'acteur prévu et que le contrat ne dépend pas d'un administrateur nul ou inaccessible. Les rôles conservés par un compte de déploiement doivent faire l'objet d'une étape explicite de renonciation ou de transfert lorsque la conception l'exige.

Un plan d'urgence doit documenter comment protéger les clés, comment déclencher la pause, qui peut approuver la reprise et comment prévenir les utilisateurs. La multisignature réduit certains risques liés à une clé individuelle, mais elle peut aussi ralentir une réaction ou concentrer plusieurs clés chez une même organisation. Évalue l'indépendance réelle des signataires, pas seulement leur nombre.

## 24. Risque économique, MEV et composabilité

Un contrat exécute les règles qu'on lui a données, mais ces règles fonctionnent dans un marché où les acteurs peuvent observer, ordonner ou combiner des transactions. Le maximal extractable value (MEV) regroupe la valeur qui peut être capturée par le choix de l'ordre, de l'inclusion ou de l'exclusion des transactions. Toutes les formes de MEV ne sont pas des vulnérabilités ; certaines stratégies peuvent néanmoins exploiter une mauvaise hypothèse économique ou produire un coût que l'application n'a pas anticipé.

Analyse l'ordre des transactions et la sensibilité des prix. Une fonction qui calcule un prix à partir d'un seul pool peut être vulnérable à une variation temporaire si elle suppose que le prix observé est représentatif du marché. Une action qui révèle une intention avant son exécution peut permettre à d'autres acteurs de réagir. Les protections peuvent inclure des bornes de slippage, des fenêtres temporelles, des références de prix adaptées et une conception qui limite les effets d'un ordre défavorable, selon le cas d'usage.

La composabilité crée une autre difficulté. Un protocole peut être sûr lorsqu'il est utilisé seul mais devenir dangereux lorsqu'un autre protocole peut l'appeler dans la même transaction ou utiliser ses actifs comme garantie. Les flash loans facilitent des opérations atomiques importantes ; la défense ne consiste pas à bannir mécaniquement les prêts flash, mais à éviter que les propriétés de sécurité dépendent d'un état temporaire facilement manipulable.

Les tests doivent examiner les séquences qui combinent dépôts, emprunts, swaps, liquidations, récompenses et changements de prix. Les hypothèses de liquidité, de disponibilité d'arbitragistes et de comportement des autres protocoles doivent être écrites. Le test en environnement local peut révéler des défauts logiques, mais une analyse économique peut aussi nécessiter des scénarios et hypothèses de marché qui ne sont pas couverts par le fuzzing.

## 25. Workflow d'audit : du gel de périmètre à la retest

Avant la revue, gèle le commit ou le tag du code, liste les contrats, les bibliothèques, les paramètres de compilation et les adresses de dépendances. Précise ce qui est inclus, ce qui est exclu et les hypothèses que l'équipe demande à l'auditeur d'accepter. Sans périmètre exact, la conclusion peut être interprétée à tort comme couvrant les composants qui n'ont jamais été examinés.

La phase de compréhension décrit le système et ses invariants. La phase automatique lance les outils disponibles et qualifie leurs résultats. La phase manuelle suit les flux, permissions, appels externes et règles économiques. La phase de test reproduit les scénarios qui paraissent plausibles. Le rapport classe les constats, explique l'impact et propose des corrections proportionnées. L'équipe corrige ensuite le code ; la retest vérifie non seulement le constat initial mais aussi les chemins voisins.

Le dernier diff doit être comparé au périmètre audité. Un petit changement peut être critique s'il modifie un rôle, une adresse ou un contrôle de validation. Les mises à niveau de bibliothèques et les corrections de configuration doivent également être considérées. Une validation finale doit inclure le code exact qui sera déployé, pas un état intermédiaire.

Le livrable devrait contenir la portée, les versions, les méthodes, les constats, les limites, les corrections, les risques résiduels et les recommandations d'exploitation. N'assimile jamais la conclusion d'un audit à une garantie éternelle ; le système change, les hypothèses évoluent et de nouvelles interactions peuvent révéler des défauts.

## 26. Contrôle préproduction fondé sur les preuves

Avant la publication, vérifie que chaque élément critique possède une preuve et un propriétaire. Le code compilé doit correspondre à la source revue ; les dépendances doivent être verrouillées ; les tests et propriétés doivent être passés dans l'environnement décrit ; les rôles doivent être confirmés ; et les adresses de réseau et d'oracle doivent être contrôlées.

Crée une checklist de preuves plutôt qu'une simple liste de cases. Pour chaque assertion, archive le lien vers le commit, l'artefact, le rapport, la sortie de test ou la transaction publique qui la démontre. Une case cochée sans pièce jointe ne permet pas à une personne indépendante de vérifier ce qui a été fait.

Le contrôle doit inclure les secrets et permissions du pipeline, la configuration des environnements, les procédures d'urgence et les alertes. Le propriétaire de publication doit savoir comment interrompre le processus si une étape de validation échoue. Aucune publication ne devrait continuer silencieusement après un contrôle critique en erreur.

Après le déploiement, vérifie l'adresse, les rôles, les paramètres, les sources externes et les événements qui confirment l'initialisation. Compare l'état réel à la configuration approuvée et archive les résultats. Les premiers blocs après publication doivent être surveillés pour détecter une configuration inattendue ou une activité qui diffère du scénario attendu.

## 27. Exercice de réponse à incident en équipe

Organise un exercice où le scénario est connu des personnes qui animent le test mais pas de l'équipe opératrice. Par exemple, une source de prix renvoie une donnée trop ancienne tandis qu'un service d'indexation est en retard. L'exercice ne doit pas employer de vrais fonds ni exposer des utilisateurs. Il vise à mesurer la coordination, la qualité du diagnostic et la clarté des responsabilités.

Les opérateurs doivent identifier le signal, qualifier les opérations affectées, collecter des preuves, décider si une pause est nécessaire et communiquer un message adapté. Le scénario peut évoluer : un rôle d'administration n'est pas joignable, le RPC principal est en panne ou le correctif n'est pas encore validé. L'équipe doit reconnaître ce qui est inconnu et éviter les modifications improvisées.

À la fin, mesure le temps entre la première alerte, la qualification, la décision, l'endiguement et la reprise. Note les informations manquantes, les accès nécessaires, les erreurs de communication et les actions qui ont créé un risque supplémentaire. Le rapport ne doit pas chercher un coupable individuel ; il doit améliorer le système de réponse.

La suite de l'exercice produit des tâches concrètes avec responsables et dates : ajouter une métrique, améliorer une alerte, automatiser une vérification, séparer des privilèges, mettre à jour le runbook ou former les intervenants. Un plan d'urgence qui n'a jamais été répété reste une hypothèse. L'exercice est terminé lorsque les actions correctives ont été suivies et qu'une nouvelle simulation confirme leur efficacité.

## 28. Tester les rôles, les permissions et le chemin d'urgence

Un exercice de contrôle d'accès doit couvrir chaque rôle et chaque fonction privilégiée. Pour chaque combinaison, précise si l'opération devrait réussir, échouer ou être soumise à un délai. Les tests doivent utiliser des comptes distincts, y compris des comptes qui ont perdu un rôle, des comptes qui possèdent un rôle voisin et des contrats qui essaient d'appeler une fonction privilégiée indirectement.

Une matrice minimale peut contenir le propriétaire initial, le rôle opérationnel, le rôle de pause, l'autorité de mise à niveau, un utilisateur normal et une adresse sans rôle. Vérifie les fonctions de configuration, la mise à jour d'oracle, l'émission de jetons, la pause, la reprise, le transfert de rôle et l'initialisation. Le test doit confirmer non seulement le résultat de l'appel mais l'état complet après son exécution.

La révocation est aussi importante que l'attribution. Après un transfert de rôle, l'ancien compte ne doit plus garder les capacités que la politique lui retire. La procédure doit vérifier que le nouveau compte peut accomplir les fonctions nécessaires et que les contrôles multi-signatures ou délais sont actifs. Un contrat peut être vulnérable si un rôle a été transféré à une adresse qui ne peut pas être contrôlée ou qui ne comprend pas la procédure.

Le chemin d'urgence doit être testé comme une capacité opérationnelle. Qui peut déclencher la pause ? Quelles opérations sont arrêtées ? Peut-on effectuer les retraits ou les actions de récupération indispensables ? Qui approuve la reprise, et quelles preuves doit-il examiner ? Le résultat du test doit être consigné comme un scénario de continuité avec les limites observées. Une pause non testée peut échouer au moment où elle serait le plus nécessaire.

## 29. Sécuriser le déploiement et la surveillance continue

Un contrat est exposé à des risques tout au long de son cycle de vie. La sécurité de publication couvre le dépôt de code, les dépendances, la compilation, les secrets, l'approbation, l'exécution des scripts et la vérification post-déploiement. Un pipeline qui permet à un seul compte de modifier les sources, d'utiliser la clé de production et d'approuver la publication crée une concentration de pouvoir.

Sépare les rôles de développement, revue et publication lorsque le niveau de risque le justifie. Verrouille les versions du compilateur et des bibliothèques, vérifie les changements de dépendance et garde un artefact reproductible. Les secrets ne doivent pas être présents dans les fichiers de configuration versionnés, les logs ou les sorties de test. Les identités de CI doivent disposer uniquement des permissions nécessaires à leur tâche.

Après le déploiement, surveille les événements de rôle, les changements de paramètres, les mises à niveau, les pauses, les opérations anormales et les écarts entre l'état attendu et l'état réel. L'alerte doit être liée à une procédure et à un propriétaire. Une alerte indiquant qu'un administrateur a changé l'adresse d'un oracle est utile uniquement si l'organisation peut vérifier si le changement était approuvé et agir en cas d'écart.

Prévois des contrôles de drift : compare périodiquement les adresses, rôles et paramètres on-chain à une configuration approuvée. La documentation ne doit pas rester la seule source de vérité après les déploiements. Si le système n'est pas immuable, il faut pouvoir détecter les modifications de configuration et mettre à jour les rapports d'audit.

## 30. Étude de cas : coffre avec contrôle d'accès et retrait

Un coffre accepte des dépôts, garde un crédit par utilisateur et permet à un rôle d'urgence de bloquer les nouvelles opérations. L'équipe teste les dépôts et retraits nominaux, mais elle n'a pas vérifié les interactions entre pause, transfert de rôle et échec d'un appel externe.

Construis les scénarios suivants : un utilisateur tente de retirer plus que son crédit ; un compte sans rôle essaie de déclencher la pause ; l'administrateur transfère le rôle puis l'ancien compte tente une modification ; le destinataire du retrait refuse le transfert ; une tentative de retrait survient pendant la pause ; un service d'indexation reçoit deux fois l'événement. Pour chacun, définis l'état attendu, l'événement et le résultat de l'appel.

La correction attendue est une politique explicite. Les appels non autorisés échouent sans changement d'état. L'ancien administrateur perd les capacités prévues. L'échec du transfert suit une règle documentée et ne fait pas perdre le crédit à l'utilisateur. La pause applique précisément le périmètre conçu et ne bloque pas accidentellement une fonction d'urgence qui devait rester disponible. Le traitement dupliqué de l'événement hors chaîne ne produit pas un second crédit métier.

Le rapport doit aussi dire ce que le test ne couvre pas. Il ne démontre pas l'absence de toutes les formes de réentrance ni l'équilibre économique du contrat complet. Les résultats doivent être ajoutés à une matrice de tests plus large, puis revus avec les invariants et le modèle de menace du système.

## 31. Qualifier la sévérité et accepter les risques résiduels

La sévérité d'un constat dépend de l'impact sur les actifs et les utilisateurs, de la facilité d'exploitation, des privilèges requis, de l'exposition de la fonction et de la possibilité de récupération. Il faut distinguer une conséquence confirmée d'un scénario possible. Un défaut de configuration théorique n'a pas le même statut qu'une transaction de test qui reproduit une perte de fonds, mais les deux peuvent mériter une correction selon l'impact.

Chaque constat doit contenir une description, un contexte précis, des préconditions, les étapes reproductibles, la preuve, l'impact, une sévérité justifiée et une recommandation. La formulation ne doit pas exagérer. Si le dommage dépend d'une hypothèse de marché ou de la compromission préalable d'un rôle, cette dépendance doit être indiquée. Un rapport honnête rend l'incertitude explicite.

L'acceptation d'un risque résiduel doit être une décision formelle. Qui accepte le risque ? Pendant combien de temps ? Quel événement déclenchera une nouvelle revue ? Existe-t-il un contrôle compensatoire ? Pour un risque temporaire, définis une date d'expiration ou une condition de retrait de la dérogation. Sinon, une exception urgente devient souvent une configuration permanente oubliée.

Après une correction, exécute les tests du défaut original et les tests des chemins voisins, compare le nouveau code au périmètre revu et documente les risques restants. Une correction peut modifier les permissions ou les hypothèses économiques ; la retest doit donc confirmer qu'elle n'a pas créé une autre voie de contournement.

## 32. Reconstituer une chaîne d'impact au lieu d'isoler un bug

Un constat devient plus facile à prioriser lorsque la revue décrit comment un défaut peut se transformer en impact. Commence par une précondition, puis trace l'appel qui exploite cette condition, la modification d'état, la conséquence sur les actifs et les mécanismes qui pourraient détecter ou limiter le résultat. Une vulnérabilité potentielle n'implique pas toujours une perte ; la chaîne d'impact doit être expliquée et vérifiée.

Exemple de raisonnement : une fonction administrative peut changer une référence de prix ; le contrat de prêt accepte ensuite cette donnée sans vérifier sa fraîcheur ; un appel de liquidation utilise ce prix ; le résultat peut déplacer une garantie ou rendre une dette incorrectement comptabilisée. Le risque ne réside pas dans une seule instruction, mais dans la combinaison d'un pouvoir, d'une donnée et d'une fonction métier. Le rapport doit vérifier si les contrôles de rôle, les limites de variation, les pauses et les tests couvrent cette combinaison.

Utilise une table de scénario qui contient la précondition, l'action, l'état avant, l'état après, la preuve et le contrôle attendu. Cela aide à distinguer une hypothèse théorique d'une faiblesse reproductible. Pour les scénarios financiers, note aussi les unités, les décimales, les frais et la valeur économique ; une balance techniquement cohérente peut être économiquement incorrecte si les prix ou la comptabilité sont mal définis.

Les tests de régression doivent suivre l'effet métier jusqu'à la fin. Bloquer l'appel dangereux n'est pas suffisant si une autre fonction permet d'obtenir le même effet. Une correction de permissions doit être testée à travers tous les points d'entrée ; une correction d'oracle doit être testée avec les autres fonctions qui consomment le prix. Le rapport doit indiquer les chemins adjacents qui ont été revus et ceux qui restent hors périmètre.

## 33. Organiser la divulgation responsable et la gestion des correctifs

Une équipe doit disposer d'un processus permettant de recevoir et de qualifier un signal de vulnérabilité. Le canal de contact doit être clair, les délais d'accusé de réception définis et les informations sensibles traitées avec précaution. Si une faille concerne un contrat public, la publication détaillée de la preuve avant l'endiguement peut permettre à un adversaire d'en profiter. La coordination doit donc prendre en compte le risque immédiat, les obligations de transparence et la nécessité d'informer les utilisateurs.

La procédure devrait définir les rôles : responsable de triage, développeur de correction, autorité de pause ou de mise à niveau, responsable de communication et personne qui valide la reprise. Les décisions importantes doivent être consignées avec leur heure, les preuves disponibles et les limites. Une seule personne ne devrait pas devoir improviser l'ensemble des actions en situation de pression.

La correction exige une analyse du code actif, pas uniquement du dépôt source. Vérifie les adresses, les implémentations, les versions et les permissions. Si une mise à niveau est possible, prépare un patch reproductible, teste le scénario à l'origine de la faille et exécute les tests de régression. Si le contrat est immuable, examine les options de limitation, de migration ou de communication qui sont réellement disponibles ; ne promets pas un correctif on-chain impossible.

Après l'incident, rédige un rapport de cause racine. Il doit expliquer le mécanisme, l'impact, la fenêtre temporelle, les contrôles qui ont échoué, les décisions opérationnelles et les améliorations nécessaires. La publication du rapport doit respecter les contraintes de sécurité et de confidentialité, mais elle ne doit pas transformer un incident en secret organisationnel qui empêche les utilisateurs de comprendre les conséquences.

## 34. Revue finale des risques et décision de publication

La décision de publication devrait examiner la correction du code, la qualité des preuves, la gouvernance des privilèges, la capacité de surveillance, la préparation à l'incident et les risques résiduels. Une checklist n'a de valeur que si les exigences sont liées à des preuves et à des responsabilités. Par exemple, « les permissions ont été revues » devrait renvoyer à une matrice qui décrit les rôles, les fonctions, les tests et les contrôles de déploiement.

Définis des portes de validation. La compilation reproductible ne remplace pas les tests ; les tests ne remplacent pas la revue ; la revue ne remplace pas la vérification des paramètres et du bytecode après déploiement. Chaque étape doit pouvoir interrompre la publication si elle échoue. Les exceptions doivent être documentées, approuvées et limitées dans le temps.

Une évaluation finale doit aussi examiner l'exploitabilité des procédures. Si le système promet une pause d'urgence, l'équipe doit avoir accès aux clés et savoir quel appel déclencher. Si un oracle doit être remplacé, la procédure et les rôles sont prêts. Si la mise à niveau exige un délai, le calendrier et la communication sont préparés. Une défense inutilisable au moment critique n'apporte qu'une protection nominale.

Archive la version examinée, la configuration, les tests, les rapports d'outils, la validation des rôles et le compte rendu du déploiement. Une future revue doit pouvoir reconstruire le contexte au lieu de dépendre du souvenir d'une personne. Après la publication, ouvre une surveillance renforcée pour les changements de rôle, les appels privilégiés inattendus et les comportements qui sortent des profils attendus. L'acceptation d'un risque doit être révisée lorsque les hypothèses changent.

## 35. Conduire une revue guidée de bout en bout

Une revue guidée commence par une question métier précise. Par exemple : un utilisateur ne doit pas pouvoir retirer plus que son crédit reconnu, même si le destinataire est un contrat externe, si le prix change ou si une transaction est répétée. L'auditeur transforme cette règle en invariant, identifie les fonctions qui y contribuent, trace les appels et repère les états qui peuvent changer entre la vérification et l'effet.

La lecture du code suit une séquence répétable. D'abord, liste les points d'entrée externes et leur visibilité. Ensuite, note les préconditions, les rôles et les variables lues ou modifiées. Puis identifie les appels à d'autres contrats et les événements émis. Enfin, cherche les chemins de retour, les reverts et les cas où le traitement s'arrête avant la fin. Pour chaque branche, demande ce qui est vrai après l'appel et ce qui reste garanti si une dépendance échoue.

Établis ensuite un tableau de revue : fonction, hypothèses, actifs affectés, contrôles, tests associés et preuve. Cela évite les remarques trop vagues telles que « revoir les permissions » sans désigner les fonctions ni préciser le résultat attendu. Le tableau aide aussi à repérer une fonction très privilégiée qui n'a pas de test direct, ou un invariant qui n'est couvert que par les tests du chemin nominal.

La revue doit être contradictoire. Demande à une autre personne de tenter de casser l'hypothèse centrale à partir du code et des tests. Elle peut rechercher un autre ordre d'appel, un compte sans rôle, un paramètre extrême ou un état inattendu. La personne qui a écrit le code connaît souvent le chemin normal et peut inconsciemment négliger les comportements que l'interface n'expose pas.

Le résultat est exploitable lorsqu'il indique les hypothèses, les chemins testés, les constats, les limites de la revue et les tests qui deviendront des contrôles de régression. L'objectif n'est pas de produire un document volumineux mais de construire une chaîne de preuves qu'un autre auditeur pourra examiner et reproduire.

## 36. Checklist finale avant mainnet

Avant de déployer un contrat qui contrôle des actifs, vérifie que la version du code et les dépendances sont verrouillées, que la compilation est reproductible et que les tests sont associés aux invariants métier. Les tests doivent inclure les utilisateurs sans rôle, les paramètres extrêmes, les appels externes qui échouent, les répétitions, les opérations de pause et les chemins de reprise.

Vérifie les pouvoirs d'administration et la gouvernance. Chaque rôle doit avoir un propriétaire identifié, une méthode de protection des clés, une procédure de transfert et un mode de révocation. Les fonctions de mise à niveau doivent être traitées comme des fonctions de sécurité critiques. Si le système dépend d'un oracle, vérifie l'adresse, les unités, les décimales, la fraîcheur et la réponse si la valeur est indisponible.

Le déploiement doit passer par une procédure qui contrôle la chaîne, l'adresse cible, les paramètres initiaux, les secrets et les approbations. Après le déploiement, vérifie le code publié, les rôles, les paramètres et les événements d'initialisation. Conserve les artefacts, les hashes, les logs utiles et le plan de retour ou de migration possible.

Enfin, vérifie la capacité opérationnelle : les alertes ont un propriétaire, les runbooks sont accessibles, les clés d'urgence sont disponibles selon la politique et les équipes savent comment communiquer avec les utilisateurs. Les risques résiduels doivent être nommés et acceptés par une autorité adaptée. Si une propriété de sécurité essentielle reste inconnue, le déploiement doit être reporté ou l'exposition limitée plutôt que de traiter l'absence de preuve comme une preuve d'absence de risque.

## 37. Maintenir l'assurance sécurité dans le temps

La sécurité ne se termine pas au jour du déploiement. Les dépendances évoluent, les autorités changent, les intégrations ajoutent de nouvelles fonctions et des usages imprévus apparaissent. Prévois un calendrier de revue ainsi que des événements qui déclenchent une vérification hors cycle : changement de compilateur, mise à jour de bibliothèque, ajout d'un actif, changement de source de prix, nouvelle fonction administrative ou incident dans un protocole intégré.

Maintiens une carte vivante des contrats et des permissions. Elle doit indiquer les adresses, les versions, les rôles, les sources de données, les mises à niveau possibles et les responsables. Compare périodiquement cet inventaire à l'état réellement observable sur chaîne. Lorsque la configuration dérive, détermine si le changement est approuvé et si les tests et procédures restent valides. Une documentation ancienne qui ne correspond plus au déploiement peut être un risque de sécurité à part entière.

Les constats et les tests de régression doivent rester associés à leurs correctifs. Lorsqu'un nouveau test révèle un comportement inattendu, évalue s'il remet en cause une hypothèse plus générale. Ne ferme pas un incident simplement parce qu'un test unitaire a été ajouté ; vérifie que le scénario complet est maîtrisé, que la surveillance détecte une répétition et que les responsables savent réagir.

L'assurance continue peut inclure un processus de divulgation responsable, un budget de revue indépendante et des tests de sécurité périodiques. Les outils automatiques sont utiles, mais les nouvelles fonctions économiques doivent aussi faire l'objet d'une revue métier. Les équipes doivent avoir une voie claire pour signaler une anomalie sans la minimiser par peur d'un retard de publication.

Définis des seuils de réévaluation : changement majeur du protocole, nouvelle dépendance critique, hausse importante de la valeur totale verrouillée ou modification des pouvoirs d'administration. Ces seuils permettent de proportionner les contrôles au risque réel. Une assurance continue efficace est un processus répétable qui transforme les nouveaux événements et constats en tests, procédures et décisions documentées.

## 38. Atelier de pratique : produire une preuve d'audit réutilisable

Choisis une fonction publique et écris une fiche qui relie son objectif métier à ses hypothèses, ses permissions, les variables qu'elle modifie, les appels externes et les invariants à préserver. Prépare au moins trois scénarios : une demande valide, une demande qui viole une précondition et une demande qui traverse une frontière de confiance. Pour chaque scénario, précise l'état de départ, les paramètres, le résultat attendu et les observations à conserver.

Lance ensuite les tests disponibles dans l'environnement de laboratoire et compare les résultats avec la spécification. Si un scénario échoue, réduis-le jusqu'à obtenir un cas reproductible. Si tous les tests passent, vérifie si les scénarios couvrent également les comportements du destinataire externe, les rôles non privilégiés et les appels répétés. Note les limites de l'exercice : un test sur une fonction isolée ne démontre pas la sécurité du protocole complet.

Le rapport final contient la version exacte du code, l'environnement, les commandes, les résultats et la relation entre les tests et les invariants. Il distingue les faits observés des risques non testés. Un autre développeur doit pouvoir reproduire l'exercice sans deviner le compte, la configuration ou la condition initiale.

La valeur de cet atelier est la traçabilité. Une remarque telle que « vérifier la réentrance » devient une preuve de revue lorsqu'elle identifie le chemin d'appel, la propriété qui doit rester vraie, le test du destinataire externe et le résultat obtenu. Si la propriété ne peut pas être testée, documente pourquoi et quelle autre méthode de vérification sera employée.

## 39. Dix questions d'entraînement avec corrigé

### Question 1 : Un audit prouve-t-il l'absence de bugs ?

**Correction :** Non. Il fournit une assurance limitée par son périmètre, sa version, ses hypothèses et le temps consacré. Les nouvelles versions doivent être réévaluées.

### Question 2 : Pourquoi commencer par des invariants ?

**Correction :** Ils définissent ce que le contrat doit garantir. Sans eux, un test ou un outil peut vérifier le code sans savoir si la logique métier est correcte.

### Question 3 : L'analyse statique suffit-elle ?

**Correction :** Non. Elle ne couvre pas toutes les séquences ni toutes les hypothèses économiques. Elle complète les tests et la revue humaine.

### Question 4 : Pourquoi les flash loans apparaissent-ils dans des incidents DeFi ?

**Correction :** Ils permettent de mobiliser temporairement du capital important. Le problème provient d'une logique de protocole qui peut être manipulée par un état de marché ou une séquence d'appels, pas du prêt flash en soi.

### Question 5 : Une fonction de pause est-elle toujours souhaitable ?

**Correction :** Elle peut protéger le système, mais elle crée aussi un pouvoir de blocage. Sa portée et sa gouvernance doivent être adaptées au scénario de risque.

### Question 6 : Quel est le risque majeur d'un proxy ?

**Correction :** La capacité de modifier le code exécuté, combinée aux erreurs possibles de stockage, d'initialisation, de permissions ou de procédure de mise à niveau.

### Question 7 : Pourquoi tester les appels externes ?

**Correction :** Parce que les contrats appelés peuvent échouer, revert, rappeler le contrat ou adopter un comportement inattendu. La réussite locale ne garantit pas la sécurité de l'interaction.

### Question 8 : Pourquoi un prix frais est-il une propriété de sécurité ?

**Correction :** Une donnée ancienne peut conduire à des liquidations ou à des transferts fondés sur une valeur qui ne répond plus aux exigences métier.

### Question 9 : Que faut-il vérifier après le déploiement ?

**Correction :** L'adresse, le réseau, l'artefact, les rôles, les paramètres initiaux, les références d'oracle, les logs et la cohérence avec la version approuvée.

### Question 10 : Quand un système peut-il sortir d'un incident ?

**Correction :** Lorsque le vecteur est endigué, l'état vérifié, les permissions contrôlées, le correctif testé, la surveillance active et les critères de reprise satisfaits.

## 40. Challenge final : préparer la revue de sécurité d'un protocole

Une application conserve des dépôts, utilise un oracle, permet une mise à niveau par gouvernance et s'appuie sur plusieurs contrats externes. L'équipe a écrit des tests unitaires et obtenu un rapport d'analyse statique, mais elle ne dispose pas d'une liste claire d'invariants ni d'un plan d'urgence.

### Travail demandé

Prépare un dossier qui contient l'inventaire des actifs et privilèges, le modèle de menace, dix invariants testables, la matrice de tests, les résultats d'outils, la revue des dépendances, la procédure de déploiement, la surveillance et le plan d'incident. Établis une priorité des travaux et justifie chaque choix.

### Correction proposée

Le dossier commence par la logique métier et les actifs, puis formule les propriétés à préserver. Il vérifie les chemins privilégiés, les appels externes, les oracles, les limites de calcul, les interactions et les mises à niveau. Les résultats des outils sont validés manuellement et reliés à des scénarios reproductibles. La publication n'est autorisée qu'après une comparaison du code, des dépendances et de la configuration avec le périmètre approuvé.

Le plan d'incident précise les autorités d'urgence, les données à collecter, les limites des mesures possibles, la communication et les conditions de reprise. Les risques résiduels sont documentés et acceptés par un processus explicite. La correction finale est validée par des tests de régression et une revue proportionnée à l'impact.

## Glossaire

**Audit de smart contract** : examen structuré du code, de la logique, des privilèges et de ses hypothèses.

**Invariant** : propriété qui doit rester vraie après toute séquence autorisée d'opérations.

**Frontière de confiance** : endroit où une donnée, une identité ou une exécution passe d'un contexte à un autre.

**Réentrance** : situation où un appel externe peut rappeler un contrat avant la fin d'une opération initiale.

**Fuzzing** : exploration automatisée d'un grand ensemble d'entrées et de séquences.

**Analyse statique** : analyse du code sans exécuter tous les chemins possibles.

**Vérification formelle** : démonstration de propriétés sous un modèle et des hypothèses explicites.

**Oracle** : mécanisme qui apporte au contrat des données externes au consensus qu'il exécute.

**Proxy** : architecture qui conserve une adresse d'entrée et délègue l'exécution à une implémentation.

**Multisignature** : mécanisme qui exige plusieurs approbations cryptographiques pour une opération.

**Fuzzing différentiel** : comparaison des résultats de plusieurs implémentations ou configurations sur les mêmes entrées.

**Cause racine** : mécanisme ou condition qui explique la survenue d'un incident.

## Pour aller plus loin

- OWASP Smart Contract Security, Top 10 2026 : https://scs.owasp.org/sctop10/
- Documentation Solidity : https://docs.soliditylang.org/
- Documentation OpenZeppelin Contracts : https://docs.openzeppelin.com/contracts/
- Ethereum.org, sécurité des smart contracts : https://ethereum.org/en/developers/docs/smart-contracts/
- SWC Registry, catalogue historique de faiblesses : https://swcregistry.io/

Les priorités de sécurité évoluent avec les incidents observés. Les catégories OWASP sont des repères de sensibilisation, pas une liste exhaustive ni une certification. Pour chaque projet, adapte les tests à son modèle de menace réel et vérifie la version actuelle des outils utilisés.
