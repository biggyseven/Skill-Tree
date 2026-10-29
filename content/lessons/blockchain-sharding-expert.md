# Sharding et scalabilité

## Encadré de mise en contexte

Une blockchain doit permettre à de nombreux participants de vérifier un état commun sans faire confiance à un opérateur unique. Cette propriété a un coût : chaque nœud complet doit traiter les données prévues par son rôle, valider les règles du protocole et rester synchronisé avec le réseau. Lorsque le nombre d'utilisateurs augmente, l'exécution, la publication des données, le stockage de l'état et la propagation deviennent des ressources limitées.

Le **sharding** consiste, au sens général, à répartir un ensemble de données ou de travaux en partitions, appelées shards, afin d'éviter qu'un seul composant réalise tout le travail. Dans une blockchain, cette idée est plus difficile que dans une base de données centralisée : il faut préserver le consensus, l'authentification de l'état, la disponibilité des données et les garanties de sécurité entre partitions. Une simple séparation des transactions ne suffit donc pas à produire une blockchain à la fois scalable et sûre.

Les architectures ont évolué. Sur Ethereum, le plan initial consistant à répartir l'exécution sur plusieurs shards a laissé davantage de place à une approche centrée sur les rollups et la capacité de données. Le terme « sharding » est encore utilisé pour désigner différentes techniques et différentes étapes de feuille de route ; il faut préciser le mécanisme dont on parle. Le Danksharding et l'échantillonnage de disponibilité des données (DAS) sont des concepts importants de cette évolution, mais leurs composants et leurs étapes de déploiement doivent être vérifiés dans la documentation officielle actuelle. Le cours distingue les concepts généraux des choix propres à une chaîne.

## Objectifs d'apprentissage

À la fin de cette leçon, tu dois pouvoir expliquer pourquoi la scalabilité ne se résume pas au nombre de transactions par seconde, distinguer sharding d'exécution et sharding de données, comprendre la relation entre disponibilité des données et rollups, identifier les coûts de communication entre shards, comparer plusieurs approches d'architecture, établir des métriques utiles et rédiger un plan de test de capacité avec des critères de sécurité.

## Prérequis et parcours pratique

Il est recommandé de connaître les blocs, le consensus, les nœuds P2P, l'EVM, les rollups et la notion de finalité. Les exercices se font sur des données synthétiques, un réseau local ou un environnement de test. Les chiffres de capacité utilisés dans les exercices servent à apprendre la méthode ; ils ne doivent pas être présentés comme des mesures de débit de production.

Le parcours pratique consiste à cartographier les ressources d'une application, à déterminer son goulot d'étranglement, à comparer deux mécanismes de scalabilité et à produire une note de décision qui décrit les compromis et les risques résiduels. Une bonne réponse distingue les mesures obtenues, les hypothèses et les objectifs encore non validés.

## 1. Pourquoi la scalabilité est un problème d'architecture

Le débit est la quantité de travail exécutée ou validée par unité de temps. La latence mesure le temps entre une demande et un résultat observable. La finalité indique à quel niveau le protocole considère une opération comme suffisamment établie pour qu'elle ne soit normalement plus révoquée selon son modèle de sécurité. Ces trois notions sont liées mais ne sont pas interchangeables. Une interface qui affiche une confirmation rapide ne prouve pas qu'une opération est déjà finalisée.

La scalabilité comprend plusieurs ressources : calcul, bande passante, stockage, propagation, traitement des signatures, disponibilité des données et capacité de vérification. Une conception qui améliore une ressource peut en surcharger une autre. Par exemple, augmenter la taille des blocs peut accroître le volume que les validateurs doivent recevoir et vérifier. Augmenter la fréquence des blocs peut réduire le temps entre les inclusions mais créer davantage de pression sur le réseau et le stockage.

La capacité utile n'est pas uniquement la capacité théorique d'un producteur. Une blockchain doit rester vérifiable par les participants que son modèle cherche à soutenir. Si la capacité exige du matériel hors de portée de la plupart des opérateurs indépendants, le nombre de validateurs potentiels peut diminuer et les dépendances peuvent se concentrer. L'objectif de conception est donc un compromis entre performance, décentralisation, coût, sécurité et expérience utilisateur.

## 2. Les limites des mesures de transactions par seconde

Le nombre de transactions par seconde est un indicateur simple, mais il peut être trompeur sans connaître le type de transaction. Un transfert simple et un appel complexe de contrat n'utilisent pas les mêmes ressources. Un réseau peut compter des opérations agrégées, des signatures hors chaîne ou des opérations exécutées sur des composants distincts. Compare uniquement des mesures dont la définition est claire.

Pour analyser un chiffre, demande : quelle opération a été comptée, dans quelles conditions, à quel niveau de finalité, sur quelle période, avec quel taux d'échec, et selon quelle méthode de test ? Il faut aussi considérer les coûts de sortie, les frais de publication de données et le délai nécessaire pour récupérer les actifs dans le modèle canonique. Une application très rapide à l'intérieur d'un domaine peut avoir une sortie lente ou un risque de dépendance différent.

Évite de mélanger le débit observé en test avec une capacité théorique calculée à partir de la taille maximale des blocs. Les benchmarks doivent inclure le profil de charge, la distribution des tailles d'entrée, la latence des nœuds, l'état du réseau et les hypothèses matérielles. Pour un système financier, la capacité n'est acceptable que si la correction et les invariants sont conservés sous charge.

## 3. Qu'est-ce qu'un shard ?

Dans son sens général, un shard est une partition logique d'un ensemble de données ou d'un travail. Une base de données peut répartir les lignes entre plusieurs serveurs. Dans une blockchain, un shard peut correspondre à une partition de données, un domaine d'exécution ou un ensemble de responsabilités attribuées à des validateurs. Ces modèles ne sont pas équivalents et le terme doit être défini dans la spécification d'un protocole.

Le sharding vise à permettre à un nœud de ne pas avoir à exécuter ou stocker intégralement chaque partie du système. Cependant, l'architecture doit continuer à permettre de vérifier les transitions, de communiquer entre les partitions et de détecter les données manquantes. Si une partition peut produire un état que les autres ne peuvent pas vérifier, ou si une donnée nécessaire est indisponible, le système peut se retrouver avec un résultat dont la validité ne peut pas être confirmée.

Un protocole doit donc définir l'affectation des responsabilités, les engagements d'état, les règles de consensus local et global, la disponibilité des données et le chemin de communication inter-shards. Il doit également préciser ce qu'un utilisateur peut vérifier avec un nœud partiel et quelles preuves sont requises pour accepter une opération provenant d'une autre partition.

~~~mermaid
flowchart TD
    A[État logique global] --> B[Partition A]
    A --> C[Partition B]
    A --> D[Partition C]
    B --> E[Consensus et données de A]
    C --> F[Consensus et données de B]
    D --> G[Consensus et données de C]
    E --> H[Preuves et coordination]
    F --> H
    G --> H
    H --> I[État global cohérent selon le protocole]
~~~

Ce diagramme est un modèle conceptuel. Les shards d'une conception réelle peuvent ne pas exécuter séparément des contrats, et les règles de coordination peuvent être communes plutôt que locales. Il sert à poser les bonnes questions, pas à décrire toutes les blockchains shardées.

## 4. Sharding d'exécution et sharding de données

Le **sharding d'exécution** répartit le traitement des transactions ou des transitions d'état. Certaines opérations peuvent être exécutées dans une partition donnée, avec des mécanismes pour authentifier leurs résultats et gérer les interactions vers d'autres partitions. Cette approche peut permettre à plusieurs domaines de traiter du travail en parallèle, mais elle introduit la complexité du partage d'état, de l'ordonnancement et de la communication inter-shards.

Le **sharding de données** répartit principalement l'espace disponible pour publier ou rendre accessibles des données, sans nécessairement répartir de la même manière l'exécution générale de la couche de base. Cette distinction est importante dans les architectures rollup-centric : les rollups peuvent exécuter les transactions hors chaîne et utiliser la couche de base pour publier des données permettant à des participants de vérifier ou reconstruire l'état. Une capacité de données plus élevée peut réduire certains coûts de publication.

Ces deux techniques répondent à des goulots d'étranglement différents. Le sharding d'exécution cherche à répartir du calcul ou de l'état. Le sharding de données cherche à augmenter la capacité de publication et la disponibilité de données. Un système peut combiner plusieurs approches, mais il doit expliquer les garanties de sécurité de chaque composant et les responsabilités de vérification.

## 5. Les problèmes de communication entre shards

Lorsque des opérations touchent plusieurs partitions, le système doit définir comment elles sont ordonnées et confirmées. Une transaction locale peut être simple si toutes ses données appartiennent au même shard. Une opération qui transfère un actif d'un shard à un autre exige souvent une coordination afin d'éviter de débiter une source sans créditer la destination, ou de créditer la destination sans débit valide.

La coordination peut augmenter la latence, créer des états provisoires et rendre les échecs plus difficiles à traiter. Si un message arrive en retard ou est traité deux fois, le système doit pouvoir identifier l'opération et empêcher un effet dupliqué. Les règles d'atomicité inter-shards peuvent être complexes : certaines architectures privilégient une exécution séquentielle, d'autres utilisent des messages asynchrones et une logique de compensation.

Les dépendances de communication constituent également un risque de disponibilité. Si une partition a besoin d'une autre pour finaliser une opération, la panne de la seconde peut ralentir ou bloquer la première. Il est important de cartographier les dépendances et de déterminer si un problème reste local ou affecte l'ensemble du système.

## 6. Affectation des validateurs et sécurité

Une architecture qui répartit la validation entre partitions doit déterminer comment les validateurs sont attribués et comment les changements d'affectation sont sécurisés. Si un attaquant peut concentrer une part suffisante de sa puissance dans une partition particulière, une sécurité globale moyenne peut masquer une vulnérabilité locale. La sélection des validateurs, l'aléa, la rotation et les preuves d'appartenance doivent être étudiés dans le protocole réel.

Il existe un compromis entre le coût de communication, la fréquence de rotation et la capacité à détecter une concentration. Une rotation fréquente peut compliquer l'exploitation et la synchronisation ; une rotation rare peut laisser une partition exposée plus longtemps à un groupe d'acteurs malveillants. La sécurité dépend des hypothèses précises sur les acteurs honnêtes, les clés, le réseau et le mécanisme de sanction lorsqu'il existe.

Ne suppose pas que diviser les participants en groupes maintient automatiquement les garanties du consensus global. Le protocole doit démontrer comment l'acceptation des transitions d'une partition est liée à des preuves et à une règle d'ensemble, et comment les changements de groupe sont authentifiés.

## 7. Disponibilité des données et reconstruction de l'état

La disponibilité des données permet aux validateurs ou observateurs concernés de vérifier que les données associées à un bloc ont été rendues accessibles selon le protocole. La récupération historique est une autre propriété : pouvoir télécharger plus tard des données anciennes depuis une archive. Ces capacités sont proches, mais ne sont pas identiques. Une chaîne peut garantir que les données ont été disponibles pendant la fenêtre requise sans garantir que chaque fournisseur les servira éternellement.

Dans une architecture de rollup, les données publiées permettent aux participants de reconstruire l'état ou d'établir qu'une transition respecte les règles. Un engagement cryptographique vers une racine d'état ne fournit pas à lui seul toutes les données nécessaires pour retrouver les comptes ou contester une transition. C'est pourquoi l'espace de données et ses garanties ont un effet direct sur la sécurité du système supérieur.

Les mécanismes d'échantillonnage de disponibilité visent à permettre à des participants de vérifier la disponibilité sans télécharger intégralement tout le contenu. Ils reposent sur des constructions cryptographiques et des hypothèses de réseau précises. Pour les évaluations de production, consulte la documentation officielle de la version considérée : un mécanisme proposé, un déploiement partiel et une fonctionnalité active ne doivent pas être confondus.

## 8. Ethereum et l'évolution vers une approche centrée sur les rollups

Le plan d'échelle d'Ethereum a évolué. Le sharding traditionnel d'exécution, où des sous-ensembles de validateurs auraient suivi des shards distincts, a été moins prioritaire que l'amélioration de la capacité de données pour les rollups. Les rollups exécutent une grande partie des transactions sur une couche secondaire et publient des données ou des engagements sur la couche de base selon leur modèle de sécurité. Cette approche cherche à conserver la vérification et le règlement de la couche de base tout en augmentant la capacité disponible pour les systèmes qui s'y appuient.

Le Danksharding est associé à une augmentation de la disponibilité de données dédiée aux rollups et à des mécanismes de vérification plus efficaces. L'échantillonnage de disponibilité des données (DAS) vise à permettre à des nœuds de vérifier, à travers des échantillons, qu'une quantité importante de données est disponible sans demander à chacun de télécharger chaque octet. L'architecture complète implique des prérequis et étapes de développement ; il faut donc vérifier le statut de déploiement actuel dans la feuille de route officielle plutôt que de le présenter comme terminé.

La conséquence pédagogique est importante : aujourd'hui, le mot sharding ne doit pas être utilisé comme synonyme automatique de « plusieurs chaînes d'exécution indépendantes ». Il peut désigner une répartition des données ou un ensemble de techniques planifiées pour améliorer la capacité. Une analyse sérieuse précise le mécanisme, ses garanties et son statut réel.

## 9. Les alternatives au sharding

Les rollups déplacent l'exécution sur une couche secondaire et s'appuient sur des mécanismes de règlement et de vérification. Ils peuvent offrir des modèles de preuve différents et des délais de retrait distincts. Leur performance dépend du séquenceur, de la compression, de la publication des données, du mécanisme de preuve ou de contestation et des coûts de la couche de base.

Les canaux d'état et canaux de paiement permettent à des participants d'effectuer de nombreuses mises à jour hors chaîne, puis de résoudre le résultat sur la couche de base selon des règles précises. Ils sont efficaces pour des interactions répétées entre participants, mais ne constituent pas une solution universelle pour toutes les applications. Les sidechains possèdent généralement leurs propres hypothèses de consensus et ne doivent pas être traitées comme équivalentes à un rollup qui hérite de certaines garanties de la couche de base.

La compression, les améliorations de l'exécution, la réduction des données, les caches et les changements de format peuvent aussi améliorer certaines performances. Ces optimisations ne répondent pas toutes au même problème de sécurité. Il faut identifier le goulot d'étranglement avant de choisir un mécanisme, sinon on peut optimiser un composant qui n'est pas limitant.

## 10. Évaluer une architecture de scalabilité

Une évaluation commence par le profil de travail : transactions simples ou complexes, fréquence de lecture, taille des données, interactions synchrones, besoin de finalité, valeur économique et attentes de récupération. Il faut ensuite relier chaque exigence à un mécanisme d'architecture et à une preuve de fonctionnement. Les chiffres de débit ne suffisent pas si la solution ne peut pas garantir l'accès aux données ou la correction du résultat.

Pour chaque solution candidate, demande quel état est partagé, où les transactions sont exécutées, qui ordonne les opérations, qui vérifie les transitions, où les données sont conservées et comment un utilisateur peut quitter le système. Note les hypothèses d'administration et la procédure de reprise lorsqu'un composant est indisponible. Les risques inconnus doivent rester explicitement inconnus.

| Critère | Question de revue |
|---|---|
| Exécution | Où s'exécute le travail et qui le vérifie ? |
| Données | Qui peut récupérer les données nécessaires et quand ? |
| Finalité | Quand l'opération est-elle considérée comme stable ? |
| Communication | Comment les opérations inter-partitions sont-elles coordonnées ? |
| Décentralisation | Quel matériel et quelles responsabilités faut-il assumer ? |
| Gouvernance | Qui peut modifier les paramètres ou le code ? |
| Récupération | Comment l'utilisateur retrouve-t-il son état après une panne ? |
| Coût total | Les mesures incluent-elles entrée, action, sortie et exploitation ? |

## 11. Prérequis d'un benchmark crédible

Définis le scénario de charge, la taille des entrées, le nombre d'utilisateurs simulés, la durée, le matériel, la version du logiciel et le critère de succès. Mesure la latence médiane et les percentiles élevés, le taux d'erreur, le débit soutenu, la progression de la finalité, la consommation des ressources et la capacité à récupérer après une surcharge. Un pic ponctuel ne prouve pas que la charge peut être maintenue.

Répète le benchmark en augmentant la charge par paliers. Observe si le temps de confirmation augmente progressivement, si les erreurs montent brusquement ou si un composant devient saturé. Si l'application dépend d'un indexeur, d'un RPC ou d'un service de données, mesure ces composants aussi. La limite de l'architecture peut se situer hors du protocole lui-même.

Ne présente pas les résultats comme universels. Les tests de laboratoire ne reproduisent pas toutes les conditions d'un réseau public. Documente les hypothèses, les dépendances et les limites de généralisation. Un rapport technique qui dit « 3 000 TPS » sans expliquer le workload apporte peu d'information à un architecte.

## 12. TP guidé A : identifier un goulot d'étranglement

Construis un mini-système de test qui simule des transactions de tailles différentes et collecte les temps de réception, d'exécution et de validation. Augmente la charge progressivement et note à quel moment la latence augmente fortement. Répète l'expérience en faisant varier une seule dimension, par exemple la taille de la transaction, le nombre de clients ou la fréquence d'écriture.

### Correction proposée

Le compte rendu doit identifier le composant limitant à partir des métriques. Si le CPU reste peu utilisé mais que les files réseau montent, il faut examiner la propagation plutôt que d'ajouter simplement des cœurs CPU. Si les écritures de stockage ralentissent, la capacité d'exécution théorique ne suffit pas à expliquer la performance de bout en bout. Le résultat doit comporter des données, pas seulement une impression subjective.

## 13. TP guidé B : comparer deux designs

Compare un design qui répartit l'exécution avec un design centré sur des rollups qui publient les données sur une couche de base. Décris l'emplacement du calcul, les rôles des validateurs, la disponibilité des données, le mécanisme de vérification et les modes d'échec. Utilise une matrice commune et marque les informations qui n'ont pas pu être vérifiées.

### Correction proposée

Il n'existe pas de vainqueur universel. Le bon choix dépend du goulot d'étranglement, des garanties requises et des ressources de l'application. La conclusion doit préciser les hypothèses acceptées et les preuves supplémentaires nécessaires avant production.

## 14. Étude de cas : un shard est lent mais le réseau paraît sain

Une application observe que certaines opérations deviennent lentes alors que les métriques globales du réseau restent normales. Les opérations concernent souvent le même sous-ensemble de comptes. L'équipe envisage d'augmenter les limites globales, mais ne sait pas si le problème vient d'une partition, d'une dépendance de communication ou d'un indexeur.

### Travail demandé

Écris un plan de diagnostic qui identifie les opérations concernées, compare les partitions, examine les messages inter-shards et sépare le retard de l'état réel. Définis les preuves à conserver et les conditions qui autorisent le changement de configuration.

### Correction proposée

Commence par relier chaque transaction à son chemin d'exécution et aux composants qu'elle touche. Compare la latence locale, les files de communication, les preuves et les données d'indexation. Ne change pas plusieurs variables simultanément. Le retour à la normale doit être mesuré pour le même profil d'opération et le résultat doit montrer que les invariants et l'ordre des transitions restent respectés.

## 15. Atomicité, messages inter-shards et cohérence des états

Lorsque plusieurs partitions exécutent des opérations en parallèle, une transaction métier peut toucher plus d'un domaine. Un transfert inter-shard doit, par exemple, diminuer un solde sur la source et augmenter celui de la destination. Si chaque partition progresse indépendamment, le système doit traiter le temps écoulé entre les deux événements, l'échec d'un message et la possibilité d'une répétition.

Une architecture synchrone peut tenter de rendre l'opération atomique à travers plusieurs partitions, mais cette coordination peut accroître la latence et créer des dépendances de disponibilité. Une architecture asynchrone utilise souvent des messages et des états intermédiaires. Elle doit identifier le transfert avec un identifiant unique, empêcher les doubles crédits et décrire le comportement en cas d'expiration, de message manquant ou de réorganisation.

L'atomicité ne doit pas être supposée à partir du nom d'une fonction. Il faut consulter la spécification et vérifier si l'opération est réellement atomique à travers les domaines, si elle est compensable, et si un résultat partiel peut être observé. Une application doit conserver des états explicites comme initié, source confirmée, message en attente, destination créditée et finalisé. Un statut « terminé » ne doit être affiché que lorsque les conditions métier sont satisfaites.

Les tests doivent inclure la soumission répétée d'un même message, le délai de livraison, l'arrêt temporaire d'une partition et la reprise. Ils doivent vérifier les soldes des deux côtés, les preuves de consommation et l'absence d'un état impossible. Une transaction peut être techniquement valide dans chaque shard tout en enfreignant un invariant global si la coordination est mal conçue.

## 16. Échantillonnage de disponibilité des données : ce que cela prouve

Les approches de disponibilité des données cherchent à établir que les informations nécessaires ont été suffisamment diffusées selon les règles du protocole. L'échantillonnage de disponibilité permet à un participant de demander et vérifier un sous-ensemble de données plutôt que de télécharger l'intégralité du contenu. Pour obtenir une garantie utile, la construction s'appuie sur des engagements cryptographiques, une structure qui permet de vérifier les échantillons et des hypothèses probabilistes explicites.

L'échantillonnage ne signifie pas qu'un nœud peut toujours reconstruire instantanément toute donnée historique. Il vise à détecter qu'une quantité de données nécessaire à la validation n'a pas été rendue disponible comme prévu. Il faut distinguer la disponibilité au moment du consensus, la capacité d'un full node à vérifier les données reçues et la retrievabilité historique permettant plus tard de télécharger les données anciennes.

Cette distinction devient essentielle pour les rollups. Une racine d'état peut être cryptographiquement valide sans que l'utilisateur dispose de toutes les données nécessaires pour reconstruire sa position. Une architecture doit préciser où les données sont publiées, pendant combien de temps elles sont nécessaires, quels acteurs peuvent les obtenir et quelles possibilités de sortie sont disponibles si un fournisseur de données disparaît.

Les systèmes d'échantillonnage font des hypothèses sur le comportement du réseau et les propriétés de l'encodage. Ils doivent être évalués à partir de la spécification et de la version implémentée. La présence d'un champ de données ou d'un hash dans un bloc ne doit pas être interprétée comme une garantie de conservation permanente du contenu.

## 17. Modéliser la capacité et le coût d'une partition

La capacité d'une architecture shardée dépend du coût que chaque partition peut traiter et des frais de coordination entre partitions. Un modèle de capacité peut commencer par mesurer le travail moyen par transaction, la distribution des tailles, le nombre de partitions actives, le trafic inter-partitions et les marges nécessaires pour absorber les pointes. Il faut éviter de multiplier simplement le débit mesuré d'une partition par le nombre total de partitions : cette estimation ignore les goulots d'étranglement partagés et le coût de coordination.

Définis des scénarios : charge uniformément répartie, une partition très sollicitée, beaucoup d'opérations inter-shards, perte d'un participant, et montée soudaine de charge. Mesure non seulement le débit moyen, mais aussi les percentiles de latence, le taux d'échec, la croissance des files d'attente et le temps de récupération. Un système peut afficher un bon débit moyen tout en offrant une expérience médiocre à un sous-ensemble d'utilisateurs.

Les travaux doivent aussi inclure les coûts opérationnels : matériel, bande passante, stockage, redondance, archivage, surveillance, rotation des validateurs et disponibilité des données. Un système qui demande à chaque opérateur de conserver des volumes excessifs peut réduire le nombre de participants capables de vérifier le réseau. Une optimisation ne doit donc pas se limiter au serveur qui traite le plus vite.

| Mesure | Pourquoi l'enregistrer | Signal de risque |
|---|---|---|
| Débit par partition | Repérer les différences locales | Concentration de charge |
| Latence p95/p99 | Mesurer l'expérience sous pointe | Longue queue de requêtes |
| Messages inter-shards en attente | Quantifier la coordination | Files qui croissent continuellement |
| Échec de transaction | Détecter les limites ou conflits | Hausse lors de pics |
| Retard de finalité | Distinguer exécution et sécurité | Résultat rapide mais provisoire |
| Temps de reprise | Évaluer la résilience | Retour à la normale trop lent |

## 18. Choisir une affectation des données et limiter les points chauds

Une stratégie de partitionnement doit choisir comment une clé est affectée à un domaine : par plage, hash, région, type d'actif, compte ou règle métier. Une affectation par plage peut améliorer certaines requêtes mais concentrer l'activité sur une plage très populaire. Une affectation par hash peut répartir la charge, mais rendre plus coûteuses les requêtes qui traversent plusieurs partitions. Le bon choix dépend des accès dominants et du besoin de transaction atomique.

Les données connexes peuvent être gardées ensemble pour réduire le trafic inter-shards. Cependant, l'affectation doit prévoir ce qui arrive si le volume ou l'activité évolue. Une partition très active peut devenir un hot shard ; migrer ses données sans protocole peut générer des incohérences, des duplications ou des états indéterminés. Le mécanisme de migration doit définir la période de transition, la source de vérité et l'authentification du nouvel emplacement.

Dans une blockchain, la stratégie est encore contrainte par le protocole de consensus et les règles d'authentification. Le développeur d'application ne peut pas décider librement de changer la partition d'une adresse si cela modifie la sémantique de la chaîne. Il faut distinguer le sharding fourni par le protocole du partitionnement de données dans un indexeur ou une base applicative. Le terme peut sembler identique, mais les garanties et le contrôle sont différents.

## 19. Réorganisations, finalité et états provisoires

Les partitions ou couches d'exécution peuvent exposer des états provisoires avant que le niveau de finalité attendu soit atteint. Une application doit donc définir quels états peuvent être montrés à l'utilisateur, quelles opérations peuvent être déclenchées sur un état provisoire et quelles opérations doivent attendre. Si une application crédite un compte interne dès qu'elle voit une transaction puis traite celle-ci comme définitive sans vérifier le niveau de finalité requis, une réorganisation peut créer un écart comptable.

La politique de confirmation dépend du protocole, du type d'action et de l'impact financier. Il ne suffit pas de copier un nombre fixe de blocs depuis un autre réseau. Définis les états, les sources de vérité, les seuils d'escalade et le comportement si deux fournisseurs se contredisent. Une divergence doit conduire à un examen ou à une dégradation contrôlée, pas à sélectionner silencieusement la réponse la plus favorable.

Les indexeurs doivent aussi prendre en charge la réorganisation. Ils devraient suivre les hauteurs et hashes, pouvoir retirer un événement qui ne fait plus partie de l'historique canonique selon la source et reconstruire l'état dérivé. Les services externes qui réagissent aux événements doivent être idempotents : le même événement peut être reçu plusieurs fois, retiré puis réémis, ou traité avant que l'état soit final.

## 20. Plan de migration et évolution d'un système shardé

Ajouter une partition, changer le schéma de données ou modifier la règle d'affectation est une opération de migration, pas simplement une modification de configuration. Il faut définir un point de départ, un état à déplacer, une règle d'authentification et une stratégie de coexistence entre ancienne et nouvelle configuration. Un conflit entre deux écrivains qui croient chacun être la source de vérité peut créer des pertes ou des doublons.

La procédure devrait inclure une simulation sur des données représentatives, une vérification des preuves d'état, un plan de retour et des critères de clôture. Selon le protocole, un retour arrière peut être limité ou impossible une fois une transition finalisée. Dans ce cas, le plan doit privilégier la correction contrôlée ou la reconstruction à partir d'une source de vérité plutôt que promettre un rollback qui ne peut pas être réalisé.

Les évolutions de consensus, de disponibilité de données et de formats de preuve peuvent aussi modifier les coûts et les garanties. Versionne les paramètres, conserve les résultats des benchmarks et exige une revue des dépendances critiques après une mise à niveau. Ne déduis pas la sécurité d'un protocole actuel à partir de l'état d'une proposition de recherche ancienne.

## 21. Atelier de laboratoire : simuler une partition sous pression

Dans un réseau local autorisé, construis plusieurs générateurs de charge qui envoient des opérations à des domaines logiques différents. Commence par une charge uniforme puis concentre temporairement le trafic sur une seule partition. Observe la latence, les files, les erreurs et le taux de transactions inter-domaines. Ne perturbe pas un réseau public ni un service de production pour réaliser cet exercice.

Ensuite, simule une panne limitée : arrête une instance de test ou retarde les messages entre deux composants. Vérifie que l'application distingue le retard de l'échec final, qu'elle n'exécute pas une opération deux fois et qu'elle reprend lorsque la communication revient. Mesure l'impact sur les autres partitions et confirme que les indicateurs globaux ne masquent pas la panne locale.

### Correction proposée

Un compte rendu doit contenir la configuration, la charge, les durées, les métriques avant/pendant/après et les limites de la simulation. Il explique si le goulot était l'exécution locale, la communication, le stockage ou un composant commun. Il vérifie que les états transitoires sont explicitement gérés et que la récupération ne viole pas les invariants. Il ne peut pas extrapoler directement le résultat d'un réseau local à une blockchain publique.

## 22. Concevoir une revue de scalabilité à partir des risques

Une revue doit demander quelles propriétés sont les plus importantes pour l'application. Si les actifs ont une grande valeur, la possibilité de reconstruire l'état et de sortir peut compter davantage que le temps moyen d'inclusion. Si le produit exige des opérations rapides mais réversibles, il peut tolérer davantage d'états provisoires à condition que l'interface le dise et que le système sache les réconcilier.

Énumère les scénarios de panne : saturation d'une partition, disponibilité de données insuffisante, perte d'un validateur, message inter-shard perdu, évolution de protocole, divergence RPC et surcharge de l'indexeur. Pour chacun, définis une propriété qui doit rester vraie, une métrique observable, une action opérateur et un critère de reprise. Ce tableau évite de tester seulement les cas nominaux.

La revue finale doit être datée et reliée à la version de protocole évaluée. Les architectures changent, les paramètres de capacité évoluent et les mécanismes proposés peuvent devenir implémentés ou être abandonnés. La documentation officielle, les tests de référence et les données de production sont complémentaires ; aucun de ces éléments ne remplace les deux autres.

## 23. Modes de panne et dégradation contrôlée

Une architecture répartie doit définir ce qui se passe lorsqu'une partition ne progresse plus, lorsqu'un validateur est indisponible ou lorsqu'un message de coordination se perd. La réaction sûre n'est pas toujours de poursuivre à tout prix. Certaines opérations peuvent continuer en lecture, alors que les opérations qui exigent un état global cohérent doivent attendre. Le protocole et l'application doivent rendre cette distinction explicite.

Un mode dégradé devrait préserver les invariants plutôt que masquer l'incertitude. Si un transfert inter-shard attend une preuve de l'autre domaine, l'application doit afficher qu'il est en attente, pas qu'il est échoué définitivement. Si une partition expose une tête provisoire, une action irréversible devrait attendre la politique de finalité. Si un fournisseur de données est indisponible, la logique ne doit pas utiliser une valeur ancienne sans une limite de fraîcheur définie.

La reprise demande de réconcilier les messages et les états. Lorsqu'un composant revient, il peut retrouver une file d'opérations en attente ou des événements qui ont été traités par un service hors chaîne. Les consommateurs doivent être idempotents et conserver un identifiant stable pour éviter qu'une reprise génère des effets doubles. Une mesure de reprise réussie doit vérifier les états métier, pas seulement la disponibilité des processus.

Pour chaque panne, écris un tableau des capacités préservées, des actions bloquées, des alertes, du responsable et du critère de retour. Cette matrice simplifie le support et empêche une équipe de prendre une décision arbitraire en situation d'urgence. Les pannes combinées doivent également être envisagées : une partition retardée peut entraîner une saturation des files, ce qui peut ensuite affecter les autres domaines.

## 24. Gouvernance des paramètres et évolution des règles

Les paramètres de scalabilité peuvent influer sur la sécurité : tailles de bloc, fréquence d'ordonnancement, nombre de partitions, stratégie d'affectation, fenêtres de finalité et seuils de communication. Les modifier peut faire évoluer les coûts matériels, les délais, la disponibilité et les conditions que les nœuds doivent respecter. La gouvernance des paramètres doit être traitée comme un changement de protocole ou de configuration critique.

Une procédure de changement devrait inclure une proposition documentée, une analyse de compatibilité, une simulation, un plan de déploiement et un critère d'annulation ou de correction. Les paramètres actuellement actifs doivent être conservés dans un inventaire versionné, puis comparés à ceux observés après le changement. Une modification qui semble améliorer le débit peut créer un effet indésirable sur la participation ou les messages inter-shards.

Les dépendances communes doivent être identifiées. Si toutes les partitions reposent sur le même service d'ordonnancement, le même indexeur ou le même fournisseur RPC, une panne de ce composant peut sembler être une panne globale de consensus. Le nombre de partitions n'est pas un indicateur suffisant de résilience lorsqu'une ressource centrale reste partagée.

La revue post-déploiement doit mesurer les effets réels. Compare le profil de charge, la latence, la progression de la finalité, les erreurs et la consommation de ressources avec la référence. Si la performance s'améliore mais que les échecs augmentent, le changement doit être analysé comme un compromis et non célébré par un seul chiffre.

## 25. Atelier avancé : détection d'un hot shard

Une application fictive répartit les comptes entre plusieurs partitions. La majorité du trafic utilise des comptes ordinaires, mais une campagne promotionnelle crée soudainement beaucoup d'opérations sur une même collection. Le débit global reste correct pendant quelques minutes, tandis que la latence de cette partition augmente et que les utilisateurs affectés signalent des retards.

### Travail demandé

Définis les métriques qui permettent d'identifier le hot shard, distingue une saturation locale d'une panne globale, écris une procédure de limitation de charge et précise les contrôles nécessaires avant de réaffecter les données.

### Correction proposée

Le diagnostic commence par la latence et le débit par partition, les files d'attente, les conflits, les opérations inter-partitions et la charge des ressources. Compare le comportement d'opérations semblables dans les autres partitions. Si la charge est le facteur principal, une limite temporaire ou un traitement par lots peut réduire l'impact, mais toute action doit respecter la logique du métier et ne pas perdre les demandes acceptées.

La réaffectation des données exige une procédure de migration : identifier un point de coupure, authentifier l'état déplacé, empêcher deux écrivains de considérer simultanément la même donnée comme autoritative et vérifier les références après migration. Le succès se mesure par le retour de la latence à la cible, l'absence de duplication et la cohérence des soldes ou objets.

## 26. Atelier avancé : disponibilité des données et récupération

Prépare un test dans lequel une ressource de données requise par un nœud de vérification est retardée ou indisponible. Observe les messages d'erreur, la progression du système et les conséquences sur les actions de l'application. Ne simule pas l'absence de données sur un réseau public : utilise un environnement local isolé afin de ne pas affecter d'autres participants.

Le rapport doit séparer l'indisponibilité temporaire, l'impossibilité de reconstruire un état et le simple retard d'un indexeur. Il doit montrer quelle source fait autorité, comment les autres composants détectent le problème et quelles actions sont bloquées. La reprise devrait confirmer que les données sont cohérentes et accessibles selon les exigences du protocole.

### Critères de réussite

- Les événements sont associés à une hauteur et à un identifiant de version.
- L'application ne traite pas un résultat provisoire comme final.
- La panne déclenche une alerte exploitable.
- La reprise ne produit pas de double effet.
- Les limites de la simulation sont documentées.

## 27. Revue de scalabilité et décentralisation

Un choix de scalabilité doit aussi considérer le coût d'exploitation par validateur, le stockage requis, la complexité de mise à niveau et la facilité d'exécuter un nœud indépendant. Une architecture qui augmente la capacité en rendant la validation accessible uniquement à quelques opérateurs peut modifier le modèle de confiance. Le compromis doit être explicite et évalué à partir de données, pas uniquement d'intentions de conception.

Mesure les ressources requises pour un nœud représentatif, la bande passante, le volume de données, le retard toléré, la durée de synchronisation et les exigences de stockage historique. Les nœuds d'archive, les nœuds de vérification et les nœuds qui produisent des blocs peuvent avoir des besoins différents ; ne suppose pas qu'ils doivent tous conserver exactement les mêmes données.

Évalue aussi les dépendances institutionnelles : qui développe le client, qui publie les binaires, qui peut proposer un changement de protocole et comment les opérateurs vérifient la mise à niveau. Une architecture répartie qui dépend d'un seul outil ou d'un seul opérateur peut perdre une partie des bénéfices attendus de la décentralisation.

## 28. Note de décision finale

Une note de décision compare les solutions selon les exigences du produit : capacité, latence, finalité, coût, disponibilité des données, récupération, gouvernance et ressources. Elle doit présenter les preuves consultées, les résultats des benchmarks et les inconnues. Une donnée non vérifiée doit rester inconnue et peut devenir un critère de non-adoption si elle concerne une propriété critique.

Écris également les critères de réexamen : nouvelle version majeure, incident de disponibilité, changement des hypothèses de sécurité, augmentation de la charge ou évolution de la feuille de route. Les performances mesurées à une date donnée ne garantissent pas une capacité constante. Les coûts et les mécanismes de scalabilité peuvent évoluer, et la note doit être revue lorsque ses hypothèses changent.

## 29. Vérifier les hypothèses avant de choisir un mécanisme

Un choix d'architecture de scalabilité doit commencer par une liste d'hypothèses vérifiables. Si le système annonce que les transactions sont indépendantes, vérifie quelles opérations traversent réellement les partitions. S'il annonce que les données sont disponibles, identifie qui doit les obtenir, par quel chemin et pendant quelle période. S'il annonce qu'un utilisateur peut sortir en cas de panne, vérifie le contrat, les prérequis, les frais et la capacité de construire la transaction sans l'interface habituelle.

Pour chaque affirmation, relie une preuve et une limite. Une spécification explique le comportement prévu, un test montre le comportement dans les conditions testées et une mesure de production indique la réalité observée durant une période. Aucun des trois ne remplace les deux autres. Un test local peut établir que le code suit une règle, mais il ne prouve pas le comportement du réseau sous une partition ou sous une charge non représentée.

Établis une matrice qui classe les inconnues. Une inconnue liée à la facilité de sortie peut être éliminatoire pour une application de conservation ; une inconnue sur la latence moyenne peut être tolérable si le produit est réversible. La gravité dépend de l'usage, de la valeur exposée et de la possibilité de récupération. Ne donne pas automatiquement une note favorable à une propriété qui n'a pas pu être vérifiée.

Les décisions doivent être datées et liées à la version de l'architecture. La feuille de route, les paramètres actifs, les contrats et les exigences opérationnelles changent. Une analyse qui était vraie avant une mise à niveau peut devenir obsolète. Prévois un déclencheur de nouvelle revue en cas de changement du consensus, du modèle de données, de la politique de sortie ou de la gouvernance.

## 30. Décomposer les coûts d'une architecture shardée

Le coût total d'une solution comprend plus que le coût de calcul des transactions. Il peut inclure la publication de données, la coordination entre partitions, la conservation historique, la gestion des validateurs, les indexeurs, les appels RPC, les preuves, les sauvegardes et l'assistance aux utilisateurs. Une architecture qui réduit le gas d'une transaction peut accroître les coûts de synchronisation ou d'exploitation.

Définis un scénario représentatif et mesure toutes les étapes. Pour une action de portefeuille, cela peut inclure la préparation, l'exécution, l'attente de confirmation, l'éventuelle interaction inter-shard, l'indexation et la sortie. Conserve les heures, les tailles de données, les versions et les coûts. Répète les tests à plusieurs niveaux de charge afin de ne pas extrapoler une fenêtre calme à une période de pointe.

Évalue aussi le coût imposé aux opérateurs qui vérifient le système. La capacité d'exécution n'est pas une réussite si les nœuds indépendants ont besoin de ressources disproportionnées pour rester synchronisés. La bande passante, la capacité de stockage, le temps de synchronisation et les exigences d'archivage affectent la diversité des participants capables de contribuer à la vérification.

Une comparaison honnête rapporte les mesures obtenues et leurs limites. Les chiffres théoriques peuvent aider à estimer un plafond, mais ils ne décrivent pas nécessairement le débit sûr et soutenable. Si une solution propose un meilleur coût moyen au prix d'une sortie moins robuste ou d'une gouvernance plus centralisée, ce compromis doit figurer dans la décision.

## 31. Étude de cas : capacité améliorée, récupération dégradée

Une plateforme réduit le coût de publication des données et annonce une meilleure capacité. Après une mise à niveau, les transactions quotidiennes sont plus rapides, mais un opérateur d'archive ne parvient plus à récupérer certaines données anciennes à partir de son mécanisme habituel. L'équipe doit déterminer si cela affecte le consensus, les indexeurs ou la récupération historique.

### Travail demandé

Définis la différence entre disponibilité au moment du consensus et retrievabilité historique, les métriques à collecter, les services qui sont affectés et le critère qui autorise la clôture. Explique pourquoi l'absence de données depuis un seul fournisseur ne prouve pas nécessairement que les données n'ont jamais été disponibles.

### Correction proposée

Commence par comparer les hauteurs, les hashes, les engagements de données, les sources de récupération et la période de rétention attendue. Distingue les nœuds qui vérifient les nouveaux blocs des services d'archive qui répondent aux requêtes historiques. Vérifie si la politique de conservation a changé ou si un fournisseur rencontre une panne isolée. Ne conclus pas à une faille de consensus sur la seule base d'une erreur HTTP.

Le rapport doit expliquer quelles fonctions de l'application sont affectées et si les utilisateurs peuvent toujours vérifier l'état requis pour les opérations actives. Si la récupération historique est un objectif de service, la panne reste un incident opérationnel même lorsque le consensus demeure correct. La clôture exige une récupération depuis une source conforme à la politique, une cause documentée et une amélioration de la redondance si nécessaire.

## 32. Revue post-déploiement d'une modification de capacité

Après un changement de capacité, compare le système à une référence et vérifie que les gains ne s'accompagnent pas d'un risque inattendu. Les indicateurs doivent couvrir la latence, le débit, les erreurs, la finalité, les files d'attente, la disponibilité des données, les performances des nœuds et la qualité de la synchronisation. Mesure les opérations qui traversent plusieurs domaines, car elles peuvent être affectées différemment des opérations locales.

La revue inclut également les utilisateurs et l'application. Des frais plus faibles peuvent entraîner une augmentation de la charge ; un traitement plus rapide peut modifier le rythme des événements reçus par les indexeurs. Les services hors chaîne doivent être capables d'absorber ce débit sans perdre ni dupliquer les opérations. Les alertes et les limites doivent être réévaluées lorsque le profil de charge change.

Archive la version de protocole, les paramètres, le code de test, les observations et la fenêtre temporelle. Si les résultats diffèrent de l'hypothèse, détermine si le problème est local, global ou dépendant du type de transaction. La décision de poursuivre doit être liée à des critères écrits, non à une impression générale que la mise à niveau « semble plus rapide ».

## 33. Grille d'acceptation d'une architecture de scalabilité

Avant adoption, confirme que l'équipe peut expliquer l'emplacement de l'exécution, le mécanisme de vérification, la disponibilité des données, la politique de finalité, les communications inter-domaines, la gouvernance et les chemins de sortie. Les exigences doivent être traduites en tests ou en preuves. Toute propriété centrale encore inconnue est un risque ouvert, pas une case implicite validée.

Pour chaque scénario de panne, indique le symptôme, la source de vérité, l'action permise, l'action interdite et le critère de reprise. Pour chaque benchmark, archive les paramètres et les limites. Pour chaque dépendance critique, nomme un responsable et une méthode de surveillance. Cette discipline rend l'architecture exploitable par une autre équipe après un changement de personnel.

La revue finale doit demander si la solution reste vérifiable lorsque la charge augmente, qu'un opérateur disparaît ou que l'accès à une donnée est retardé. Si la réponse dépend d'une procédure non testée, planifie un exercice avant production. La scalabilité se juge sur un système complet qui reste correct sous charge, pas sur le seul résultat d'un benchmark nominal.

## 34. Critères de décision pour un système à plusieurs domaines

Une architecture répartie doit être choisie à partir de la charge et des garanties attendues, et non parce que le sharding semble être une solution générale à tout problème de performance. Si la charge est essentiellement liée à des lectures, un indexeur ou un cache peut suffire. Si les limites viennent de l'exécution de contrats, un rollup ou une optimisation de calcul peut être plus pertinent. Si le coût principal provient de la publication de données, une approche centrée sur la disponibilité des données peut répondre plus directement au problème.

Commence par classer le goulot d'étranglement : CPU, stockage, bande passante, contention sur l'état, disponibilité de données, coordination ou service auxiliaire. Mesure la contribution de chaque composant et définis le résultat recherché. Une architecture qui répartit les écritures peut réduire la contention locale mais accroître le nombre de messages et la complexité de la réconciliation. Le résultat doit être évalué sur un scénario représentatif.

Pour chaque option, documente l'état de référence, la façon dont une transition est acceptée, les preuves disponibles, le modèle de panne et la méthode de récupération. Demande également quelle partie de la vérification peut être exécutée indépendamment et quel matériel est nécessaire. Les garanties qui dépendent d'un opérateur ou d'un comité doivent être indiquées explicitement.

Une décision bien écrite contient des critères éliminatoires, des compromis acceptés, des tests avant production et des signaux déclencheurs de réexamen. Elle doit pouvoir être relue par une équipe différente sans reconstituer les hypothèses à partir de conversations ou de tableaux de bord. L'objectif est une architecture mesurable et révisable, pas une promesse de débit sans modèle de sécurité.

## 35. Réponse à incident : divergence d'état entre partitions

Lorsqu'une application constate des états contradictoires entre deux partitions, la première étape consiste à préserver les preuves et à déterminer si le problème vient d'une réorganisation, d'un retard de message, d'un indexeur décalé ou d'un défaut d'atomicité. Les hauteurs, hashes, identifiants de transaction et statuts de finalité doivent être collectés depuis plusieurs sources adaptées.

Évite de corriger manuellement un solde pour faire disparaître la divergence. Un ajustement de données sans comprendre la cause peut créer un second écart ou empêcher une réconciliation fiable. Vérifie la séquence complète de l'opération, le message source, la preuve, l'état destination et les contrôles contre le rejeu. Les actions irréversibles doivent rester bloquées tant que l'état n'est pas déterminé selon la politique du protocole.

Si la divergence provient d'un retard, surveille la progression et réconcilie les messages en attente. Si elle provient d'une incohérence de protocole ou d'une preuve acceptée à tort, suis la procédure d'urgence et évite toute action improvisée. Le rapport doit indiquer ce qui est confirmé, les hypothèses ouvertes, l'impact métier, les limites des données et le responsable de la décision de reprise.

La clôture exige que les états soient réconciliés, que les invariants globaux soient vérifiés, que les messages n'aient pas produit de double effet et que la cause ait entraîné un test de régression ou une amélioration de l'observabilité. Un tableau de bord redevenu vert n'est pas une preuve suffisante de cohérence.

~~~mermaid
flowchart TD
    A[Divergence détectée] --> B[Préserver hashes et identifiants]
    B --> C[Comparer état source et destination]
    C --> D{Retard ou incohérence ?}
    D -->|Retard| E[Suivre messages en attente]
    D -->|Incohérence| F[Limiter opérations irréversibles]
    E --> G[Réconcilier les états]
    F --> H[Procédure d'urgence et revue]
    G --> I[Vérifier invariants et doublons]
    H --> I
    I --> J[Clôture et test de régression]
~~~

## 36. Construire un plan de test reproductible pour la scalabilité

Une campagne de test doit préciser le workload, la version, les paramètres, le matériel, le nombre de clients, la durée et les critères d'arrêt avant d'être exécutée. Sans ces informations, deux mesures ne sont pas comparables. Le test doit aussi définir ce qui compte comme une opération terminée : réponse du séquenceur, inclusion, validation ou finalité selon le système.

Commence par une charge de référence puis augmente graduellement le nombre de clients. Mesure le débit soutenu, les percentiles de latence, le taux d'échec, la consommation CPU/mémoire, la bande passante, le stockage et l'évolution des files d'attente. Effectue ensuite des tests de charge déséquilibrée et de reprise après panne. Les mesures doivent inclure les transactions inter-shards, parce que les interactions entre partitions peuvent se comporter très différemment des opérations locales.

Le test est une expérience. Si tu modifies le nombre de partitions, la taille de bloc et le nombre de clients en même temps, tu ne peux pas attribuer le résultat à une cause unique. Change une variable à la fois quand cela est possible, répète les mesures et conserve les écarts. Dans des environnements complexes, les interactions peuvent nécessiter une matrice de tests, mais les variables et les raisons de leur changement doivent rester tracées.

La qualité du test se juge également à la sûreté. Vérifie les invariants après chaque scénario, y compris après une saturation, une interruption et une reprise. Une solution qui garde un débit élevé en sacrifiant la cohérence ou en faisant perdre des messages n'a pas atteint l'objectif. Le rapport doit expliciter les limites du laboratoire et éviter de présenter les résultats comme une garantie pour toutes les conditions de production.

## 37. Signaux à surveiller après mise en production

La surveillance doit suivre séparément les performances, la correction et la disponibilité. Les performances comprennent débit, latence, taux de reverts, files d'attente et saturation des ressources. La correction comprend les conflits, les écarts de données, les messages répétés et les incohérences entre le statut affiché et l'état vérifié. La disponibilité couvre les composants de validation, les données et les chemins de récupération.

Les alertes doivent avoir un propriétaire et une action associée. Une hausse de la latence peut appeler une investigation, mais pas forcément un redémarrage. Une divergence entre les états peut exiger de suspendre les opérations irréversibles. Un retard de messages doit être classé selon la cadence normale du protocole. Les seuils doivent être fondés sur une référence, puis révisés lorsque la charge ou l'architecture change.

Surveille aussi les dépendances partagées. Plusieurs partitions peuvent sembler indépendantes tout en utilisant le même fournisseur RPC, la même source de données ou le même service d'indexation. Si ce service est en panne, les tableaux de bord peuvent signaler plusieurs problèmes locaux qui ont en réalité une cause commune. La cartographie des dépendances facilite le diagnostic et aide à choisir la redondance réellement utile.

Après chaque incident ou changement de capacité, compare le résultat avec les objectifs de niveau de service et les hypothèses du modèle de menace. Une amélioration des métriques n'est durable que si elle n'affaiblit pas la vérification, l'accès aux données ou la possibilité de récupérer l'état. Enregistre les résultats et ajoute les scénarios découverts aux tests de régression.

## 38. Contrôler les dépendances communes entre partitions

Une architecture peut répartir le calcul sans répartir tous les risques. Des partitions peuvent partager la même couche de consensus, le même service de disponibilité de données, la même infrastructure de publication, les mêmes fournisseurs RPC ou le même indexeur. Cette dépendance commune peut transformer une panne locale en incident global, même si les domaines d'exécution paraissent isolés dans le diagramme d'architecture.

Pour chaque composant partagé, indique quelles partitions en dépendent, quel type de panne peut se produire, quelles métriques l'observent et quelle alternative existe. Vérifie si la redondance est réellement indépendante : deux adresses RPC peuvent pointer vers le même fournisseur, et deux services d'indexation peuvent utiliser le même nœud en amont. Une architecture de haute disponibilité doit réduire les domaines de panne, pas seulement multiplier les instances.

Teste les composants communs dans un environnement contrôlé. Simule une indisponibilité du fournisseur de données ou de l'indexeur et observe si l'état canonique reste vérifiable, si les actions sensibles sont suspendues et si la récupération est reproductible. Le test doit distinguer une défaillance de l'observabilité d'une défaillance du protocole lui-même.

La revue finale associe la cartographie des dépendances à une décision de risque. Si l'application dépend d'un fournisseur central pour déterminer l'état, cette dépendance doit être acceptée explicitement ou remplacée par une méthode de vérification plus indépendante. La pluralité des partitions ne suffit pas à démontrer la résilience du système complet.

## 39. Fiche de clôture d'une étude de scalabilité

Toute étude doit finir par une synthèse qui peut être relue par un architecte, un opérateur et un responsable produit. Décris le problème initial, le goulot mesuré, les options examinées, les résultats du benchmark, les hypothèses non vérifiées et la décision. Ajoute les critères qui déclencheraient un retour sur le choix : changement de charge, incident de disponibilité, nouvelle version du protocole ou modification des garanties.

Sépare les faits, les estimations et les opinions. Un fait renvoie à une mesure ou à une source ; une estimation explicite sa méthode ; une opinion décrit une préférence ou un compromis. Cette distinction évite qu'un débit théorique soit cité plus tard comme une mesure de production. Conserve les limites du test, notamment l'absence de congestion réelle ou de pannes simultanées.

La synthèse doit également décrire ce que l'équipe surveillera après publication : latence, erreurs, finalité, disponibilité des données, files de messages et capacité de récupération. Chaque alerte critique doit avoir un propriétaire et un runbook. La décision de scalabilité n'est pas terminée tant que l'équipe ne sait pas détecter un résultat anormal et réagir sans sacrifier les invariants du système.

## 40. Checklist pour la revue d'architecture

Avant d'accepter une architecture shardée, vérifie que les exigences de charge sont mesurées, que le mécanisme de vérification est identifié, que les opérations inter-partitions ont des états explicites et que la disponibilité des données est décrite selon le protocole. Les indicateurs doivent distinguer performance, correction et capacité de reprise.

Pour chaque dépendance, précise le responsable, les métriques, la procédure de panne et le critère de retour à la normale. Les rapports doivent être liés à une version précise de l'architecture et à des résultats reproductibles. Une propriété non vérifiée reste une inconnue, et une inconnue qui touche aux actifs ou à la reconstruction d'état peut être un critère bloquant.

Le test final doit démontrer que le système conserve les invariants sous charge, lors d'un retard inter-partitions et après une reprise. Les résultats de laboratoire ne garantissent pas toutes les conditions d'un réseau public, mais ils rendent les hypothèses et les limites explicites.

## 41. Questions d'entraînement avec corrigé

### Question 1 : Le sharding signifie-t-il simplement ajouter des serveurs ?

**Correction :** Non. Il faut répartir les responsabilités tout en maintenant des règles de vérification, de consensus, de disponibilité et de coordination entre partitions.

### Question 2 : Pourquoi le débit seul est-il insuffisant ?

**Correction :** Il ne décrit ni la latence, ni la finalité, ni le coût d'entrée et de sortie, ni les hypothèses de sécurité, ni le taux d'échec.

### Question 3 : Quelle est la différence entre sharding d'exécution et de données ?

**Correction :** Le premier répartit l'exécution ou l'état ; le second répartit principalement la capacité de publication ou de disponibilité des données. Ils répondent à des contraintes différentes.

### Question 4 : Pourquoi les opérations inter-shards sont-elles complexes ?

**Correction :** Elles nécessitent une coordination pour empêcher les états incohérents, les pertes de message, les doubles effets ou les transitions qui ne sont pas confirmées dans les deux domaines.

### Question 5 : Un rollup est-il une sidechain ?

**Correction :** Non. Le modèle de sécurité d'un rollup dépend de mécanismes de règlement et de données sur sa couche de base ; une sidechain possède généralement des hypothèses de consensus propres.

### Question 6 : Pourquoi parler de disponibilité des données ?

**Correction :** Les vérificateurs ont besoin des données requises pour reconstruire ou contrôler l'état. Un engagement vers une racine ne fournit pas à lui seul toutes les données manquantes.

### Question 7 : Le Danksharding est-il simplement le sharding d'exécution traditionnel ?

**Correction :** Non. Il est associé à l'évolution de la capacité de données d'Ethereum pour les rollups et à des mécanismes de disponibilité plus efficaces. Le statut précis doit être vérifié dans la feuille de route officielle.

### Question 8 : Comment mesurer un benchmark crédible ?

**Correction :** Avec un workload décrit, des versions et paramètres documentés, plusieurs niveaux de charge, des mesures de latence, d'erreurs, de finalité et de ressources, ainsi qu'une explication des limites.

### Question 9 : Une partition lente implique-t-elle une panne du consensus global ?

**Correction :** Pas nécessairement. Le problème peut concerner la communication inter-partitions, une dépendance spécifique, l'exécution locale ou l'indexation de l'application.

### Question 10 : Quel est le résultat attendu d'un test de scalabilité ?

**Correction :** Identifier les limites et le comportement sous charge, tout en démontrant que les invariants, la vérification et la capacité de récupération restent corrects.

## 42. Challenge final : défendre une architecture de scalabilité

Un service Web3 prévoit une hausse importante de charge. Trois propositions sont étudiées : accroître les limites de la couche de base, répartir le travail sur des partitions d'exécution ou exécuter les transactions dans des rollups avec publication de données. Les propositions annoncent des chiffres de débit différents, mais utilisent des hypothèses et des tests non comparables.

### Travail demandé

Rédige une décision d'architecture avec le workload cible, les exigences de finalité, les limites de matériel, les garanties de données, les coûts totaux, les modes d'échec et les critères de migration. Définis un benchmark commun et indique quelles informations restent inconnues.

### Correction proposée

La décision commence par les besoins de l'application, pas par le chiffre le plus élevé. Elle distingue débit, latence et finalité, et identifie le composant qui constitue le goulot d'étranglement. Chaque architecture est évaluée avec les mêmes scénarios, tandis que les différences de modèle de sécurité sont conservées plutôt que masquées dans une note unique.

La recommandation doit expliquer les compromis, les limites de récupération, les dépendances administratives et les tests nécessaires avant production. Les hypothèses non vérifiées sont enregistrées comme des travaux à terminer. Une architecture n'est pas prête simplement parce qu'elle atteint le débit théorique annoncé ; elle doit rester vérifiable et exploitable sous les conditions attendues.

## Glossaire

**Sharding** : partitionnement des données ou du travail entre plusieurs domaines.

**Shard** : partition ou domaine de responsabilité dans une architecture shardée.

**Sharding d'exécution** : répartition du traitement ou de l'état.

**Sharding de données** : répartition de la capacité de publication ou de disponibilité des données.

**Disponibilité des données** : possibilité pour les acteurs requis d'obtenir les données nécessaires à la vérification selon le protocole.

**DAS** : échantillonnage de disponibilité des données, méthode qui cherche à vérifier cette disponibilité par des échantillons et des mécanismes cryptographiques.

**Rollup** : système qui exécute des opérations hors de la couche de base et utilise un mécanisme de règlement et de données défini.

**Finalité** : niveau auquel l'état est considéré comme suffisamment établi selon les règles du protocole.

**Débit** : quantité de travail traitée par unité de temps.

**Latence** : durée entre une action et un résultat observable.

**Goulot d'étranglement** : ressource ou composant qui limite la performance du système.

## Pour aller plus loin

- Ethereum.org, scalabilité : https://ethereum.org/en/developers/docs/scaling/
- Ethereum.org, feuille de route de scalabilité : https://ethereum.org/roadmap/scaling
- Ethereum.org, disponibilité des données : https://ethereum.org/en/developers/docs/data-availability/
- Ethereum.org, rollups : https://ethereum.org/en/developers/docs/scaling/optimistic-rollups/
- Documentation Ethereum, Danksharding et DAS : suivre les liens de la feuille de route officielle.

La feuille de route évolue. Vérifie la documentation active au moment de l'implémentation, notamment pour différencier une proposition, un prérequis en cours de développement et une fonctionnalité effectivement déployée.
