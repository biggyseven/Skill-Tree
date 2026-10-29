# Consensus (PoW vs PoS)

## Encadré de mise en contexte

Une blockchain publique ne dispose généralement pas d'un administrateur central qui décide à lui seul quel historique chaque participant doit accepter. Des nœuds peuvent recevoir des transactions différentes, des blocs concurrents ou des messages avec du retard. Certains participants peuvent être hors ligne, défectueux ou malveillants. Le **consensus** désigne l'ensemble des mécanismes et règles qui permettent au réseau de converger vers un historique accepté malgré ces difficultés.

Deux grandes familles sont souvent comparées : la preuve de travail (*Proof of Work*, PoW), utilisée par Bitcoin, et la preuve d'enjeu (*Proof of Stake*, PoS), utilisée aujourd'hui par Ethereum. La comparaison ne doit pas se réduire à « l'une consomme de l'énergie, l'autre non ». Les deux cherchent à rendre les attaques coûteuses, mais elles utilisent des ressources, des mécanismes de sélection, des incitations et des procédures de récupération différents. Elles exposent aussi des risques différents : concentration du minage, concentration du staking, censure, bugs logiciels, défaillances de réseau et erreurs de gouvernance.

Ce cours part des notions de blocs et de hachage étudiées auparavant. Il explique le problème du consensus avant de détailler PoW et PoS, puis propose des exercices qui t'apprennent à distinguer validité, sélection de chaîne, sécurité économique et finalité.

## Objectifs d'apprentissage

À la fin de ce cours, tu sauras :

- expliquer pourquoi un réseau pair-à-pair a besoin d'un mécanisme de consensus ;
- distinguer validité d'un bloc et choix de la branche à suivre ;
- comprendre les principes de la preuve de travail et de la difficulté ;
- expliquer le rôle des mineurs, des validateurs et des incitations économiques ;
- décrire le consensus par preuve d'enjeu et la finalité d'Ethereum ;
- comparer sécurité, consommation de ressources, centralisation et hypothèses de confiance ;
- expliquer les réorganisations et les doubles dépenses sans les confondre avec la falsification de signatures ;
- identifier les attaques majoritaires et les limites de l'expression « 51 % » ;
- analyser un scénario de panne de consensus avec une démarche structurée.

## 1. Pourquoi faut-il un consensus ?

Imaginons que trois nœuds reçoivent deux transactions incompatibles qui essaient de dépenser la même sortie Bitcoin. Le nœud A reçoit d'abord la transaction qui paie Bob ; le nœud B reçoit d'abord celle qui paie Chloé. Sans règle commune pour choisir un historique, les deux nœuds pourraient conserver indéfiniment des états incompatibles. Les échanges économiques ne pourraient pas s'appuyer sur un registre partagé.

Le réseau doit donc combiner au moins deux niveaux de règles :

1. **Les règles de validité** définissent ce qu'un bloc ou une transaction a le droit de faire. Par exemple, une transaction Bitcoin ne peut pas dépenser un UTXO déjà dépensé dans l'état applicable, et une transaction Ethereum doit respecter son format et les conditions de compte.
2. **Les règles de consensus** permettent aux nœuds de choisir, parmi les propositions qu'ils reçoivent, l'historique qu'ils doivent suivre et les conditions dans lesquelles ils considèrent un bloc comme confirmé ou finalisé.

Un bloc dont les transactions violent les règles n'est pas rendu valide par une grande puissance de calcul ou par de nombreux validateurs. Le consensus n'est pas un vote qui permettrait à une majorité de transformer une donnée invalide en donnée valide selon le protocole. Les nœuds conformes doivent vérifier les règles, puis déterminer quelle branche valide ils retiennent.

~~~mermaid
flowchart TD
    A["Transactions et blocs reçus"] --> B["Vérification de validité"]
    B -->|Invalide| X["Rejeter le bloc"]
    B -->|Valide| C["Évaluer la branche selon le consensus"]
    C --> D["Suivre une branche admissible"]
    D --> E["Actualiser l'état local"]
~~~

### 1.1 Les difficultés d'un réseau distribué

Un réseau pair-à-pair doit fonctionner même quand la communication n'est pas instantanée. Un message envoyé à un nœud peut arriver tard chez un autre. Des paquets peuvent être perdus, un fournisseur d'accès peut tomber en panne, un participant peut se déconnecter et revenir plus tard. Il n'existe pas nécessairement une horloge parfaite commune à tous les participants.

Il faut également considérer les acteurs malveillants. Un participant peut diffuser des transactions contradictoires, omettre certains messages ou tenter de proposer une histoire alternative. Selon les ressources et les hypothèses du protocole, il peut essayer de censurer une transaction, de faire apparaître une double dépense ou de perturber le fonctionnement du réseau.

Le consensus ne rend pas impossible tout incident. Il fournit un ensemble de règles pour que les participants conformes puissent retrouver une vue cohérente de l'historique, sous certaines hypothèses de sécurité et de disponibilité.

### 1.2 Validité, finalité et confiance

Ces mots décrivent des choses distinctes :

- **Validité** : les données respectent les règles de la chaîne et la transition d'état est correcte.
- **Inclusion** : une transaction fait partie d'un bloc.
- **Confirmation** : d'autres blocs ou votes renforcent la confiance dans la place du bloc dans l'historique.
- **Finalité** : le protocole a atteint une condition précise qui donne à un bloc des garanties de finalisation particulières.
- **Confiance opérationnelle** : un service, un portefeuille ou une entreprise se comporte comme prévu. Cette notion dépasse le consensus de base.

Une application peut être hors service alors que la blockchain fonctionne. Un explorateur peut afficher un bloc avec du retard. Une plateforme d'échange peut suspendre les retraits alors que la chaîne continue à produire des blocs. Il faut diagnostiquer la bonne couche avant de parler d'une panne de consensus.

## 2. Familles de mécanismes de consensus

Il existe de nombreux mécanismes et variantes. PoW et PoS sont les exemples dominants dans les réseaux publics les plus connus, mais ils ne sont pas les seules approches. Des réseaux privés ou fédérés utilisent des ensembles de validateurs connus, des protocoles BFT, des autorités préconfigurées ou des modèles hybrides.

Un mécanisme de consensus répond notamment à ces questions :

- Qui peut proposer le prochain bloc ?
- Qui vérifie les propositions ?
- Comment les nœuds choisissent-ils entre des blocs concurrents ?
- Quel type de ressource ou de responsabilité limite les attaques ?
- Quelles pénalités ou récompenses encouragent un comportement conforme ?
- Que se passe-t-il lorsque des participants sont hors ligne ou que le réseau est partitionné ?
- Comment un bloc devient-il suffisamment confirmé ou finalisé pour un usage donné ?

Les réponses sont différentes selon le modèle. Il est donc insuffisant de dire qu'une blockchain est sûre uniquement parce qu'elle utilise « un consensus ». Il faut comprendre le mécanisme réel, ses paramètres, les hypothèses de réseau et la distribution de ses ressources.

## 3. La preuve de travail (Proof of Work)

### 3.1 Principe général

Dans une blockchain à preuve de travail, des mineurs essaient de produire un en-tête de bloc dont le hash répond à une cible déterminée par le protocole. La recherche demande de nombreux calculs, tandis que la vérification d'une preuve trouvée est relativement peu coûteuse. Le protocole ajuste la difficulté selon ses règles afin de maintenir un rythme de production des blocs malgré les variations de puissance de calcul.

Le mineur ne peut pas simplement écrire une valeur de hash qui lui plaît. Le hash doit découler des données exactes de l'en-tête. Le nonce est un champ modifiable, mais d'autres données peuvent aussi être modifiées légalement pour explorer d'autres possibilités. En changeant l'en-tête, le mineur obtient normalement un hash différent. Il cherche un résultat qui satisfait la cible.

~~~mermaid
flowchart TD
    T["Sélectionner les transactions"] --> H["Construire l'en-tête du bloc"]
    H --> C["Calculer le hash"]
    C --> Q{"Hash inférieur à la cible ?"}
    Q -->|Non| N["Modifier nonce ou données admissibles"]
    N --> C
    Q -->|Oui| P["Diffuser le bloc candidat"]
    P --> V["Les nœuds vérifient indépendamment"]
    V --> A["Bloc candidat valide"]
~~~

### 3.2 Cible et difficulté

Le hash produit par une fonction cryptographique est conçu pour se comporter comme une valeur imprévisible. En moyenne, si la cible est très stricte, il faut davantage d'essais pour trouver un hash qui la respecte. La difficulté exprime donc la sévérité de cette condition.

Dans Bitcoin, les blocs contiennent un champ compact qui représente la cible. Le réseau ajuste cette cible à intervalles définis selon les règles du protocole, afin que le temps de bloc moyen reste proche de l'objectif historique d'environ dix minutes. Ce délai est une moyenne, pas un horaire fixe : deux blocs peuvent être trouvés à quelques secondes d'intervalle, puis plusieurs minutes peuvent passer sans nouveau bloc.

Le temps de bloc ne signifie pas que chaque transaction attend systématiquement dix minutes, ni qu'une transaction devient finale après un seul bloc. Une transaction peut être relayée presque immédiatement, mais son inclusion dépend d'un producteur, de la sélection des transactions, de l'état du réseau et du niveau de frais. Le nombre de confirmations est ensuite utilisé pour apprécier le risque de réorganisation.

### 3.3 Que paie réellement le mineur ?

Le mineur consomme des ressources matérielles et énergétiques pour réaliser les calculs. La rentabilité dépend des coûts d'électricité, du matériel, de la difficulté, de la valeur des récompenses, des frais de transaction, de la disponibilité et d'autres facteurs économiques. Dans les réseaux de preuve de travail, la compétition peut encourager l'utilisation de matériel spécialisé.

Un mineur peut avoir beaucoup de puissance de calcul sans avoir le droit de faire accepter un bloc invalide par des nœuds conformes. Si son bloc contient une transaction impossible ou réclame une subvention excessive, les nœuds devraient le rejeter. La puissance de calcul sert à influencer la production et la sélection de chaînes valides, pas à abolir toutes les règles du protocole.

### 3.4 Pourquoi la chaîne avec le plus de travail ?

Bitcoin utilise une règle de sélection fondée sur le travail cumulé des chaînes valides, souvent résumée dans le langage courant comme « la chaîne la plus longue ». Cette dernière expression est imprécise : deux branches peuvent avoir des nombres de blocs différents et la branche de travail cumulé le plus important peut être retenue même si elle n'est pas celle qui a le plus de blocs.

La quantité de travail cumulée permet aux nœuds de comparer les branches selon les règles du protocole. Elle ne signifie pas que tous les nœuds connaissent à chaque instant exactement les mêmes blocs. Pendant la propagation, plusieurs nœuds peuvent suivre provisoirement des branches différentes. Quand de nouveaux blocs arrivent, leur vue peut se réorganiser.

### 3.5 Récompenses et incitations

La récompense de bloc et les frais sont destinés à rendre économiquement utile la production de blocs valides. Si un mineur publie un bloc invalide, il risque de perdre le revenu attendu parce que les nœuds ne l'acceptent pas. Si un mineur construit sur une branche minoritaire qui n'est finalement pas retenue, ses efforts peuvent ne pas rapporter comme il l'espérait.

Les incitations ne remplacent pas les vérifications. Elles cherchent à rendre le comportement conforme préférable à l'attaque dans certaines conditions. L'équilibre dépend de la valeur des actifs, des coûts opérationnels, des possibilités de location ou d'achat de puissance de calcul, des revenus potentiels de l'attaque et des effets sur la confiance envers le réseau.

## 4. La preuve d'enjeu (Proof of Stake)

### 4.1 Principe général

Dans un système de preuve d'enjeu, les participants qui remplissent les conditions du protocole immobilisent ou mettent en jeu un actif afin de participer aux responsabilités de validation. On les appelle souvent validateurs. Le protocole sélectionne ou autorise des validateurs à proposer des blocs, et d'autres validateurs peuvent attester ou voter pour les propositions selon les règles définies.

Au lieu de dépenser une compétition continue de calcul comme principal mécanisme de sélection, le système utilise une mise économique et des règles de pénalité. Certains comportements contraires au protocole peuvent entraîner un *slashing*, c'est-à-dire la destruction ou la pénalisation d'une partie de la mise. Les absences ou les retards peuvent aussi entraîner des pénalités plus modestes, selon le système.

~~~mermaid
flowchart TD
    S["Déposer la mise requise"] --> R["Entrer dans l'ensemble des validateurs"]
    R --> P["Proposer un bloc ou une attestation"]
    P --> V["Les autres validateurs vérifient"]
    V -->|Comportement conforme| G["Récompenses possibles"]
    V -->|Violation sanctionnable| L["Pénalités ou slashing"]
    V -->|Données invalides| X["Bloc rejeté par les nœuds conformes"]
~~~

### 4.2 Staking et responsabilités

Un validateur ne devrait pas être considéré comme un administrateur qui peut créer une vérité selon son souhait. Il doit suivre les règles de validité. Une mise engagée sert à aligner les incitations, mais elle n'autorise pas un validateur à faire accepter n'importe quel bloc. Les nœuds exécutent les règles de validation indépendamment.

La participation peut être directe ou passer par un fournisseur de staking, un pool ou un service de garde. Ces options changent le profil de risque. Détenir soi-même les clés de validateur et utiliser son propre matériel ne présente pas les mêmes risques qu'envoyer ses actifs à un opérateur tiers ou déléguer le contrôle à un service. Un pool peut réduire les exigences techniques pour l'utilisateur, mais créer une concentration opérationnelle ou de gouvernance.

### 4.3 Propositions, attestations et finalité dans Ethereum

Ethereum utilise aujourd'hui la preuve d'enjeu. Son mécanisme de consensus sépare conceptuellement le niveau d'exécution — qui traite les transactions et les contrats — de la logique de consensus qui organise les propositions, attestations et finalisation. Les validateurs proposent des blocs à certains moments et attestent des informations selon les règles du protocole. La finalité dépend de votes et de seuils prévus par le mécanisme, sous des hypothèses relatives aux validateurs et au réseau.

Il faut éviter de réduire Ethereum à « le validateur qui possède le plus d'ETH écrit le prochain bloc ». Le protocole n'est pas un simple classement de soldes. La sélection de propositions, les attestations, les récompenses, les pénalités et la finalité sont définies par un ensemble de règles précises. Les services de staking influencent l'organisation économique, mais ils ne sont pas identiques au protocole lui-même.

### 4.4 Slashing et pénalités

Le slashing vise certains comportements qui menacent le consensus, par exemple des attestations incompatibles ou des propositions contradictoires dans des conditions spécifiées. Les détails sont déterminés par le protocole. Il ne faut pas supposer qu'une erreur de réseau ordinaire et une violation sanctionnable soient toujours traitées de la même façon.

Le validateur doit protéger ses clés, utiliser des clients fiables, maintenir une bonne disponibilité et configurer correctement ses systèmes. Une mauvaise configuration qui permet à plusieurs instances de signer de façon incompatible peut créer des risques. Les sauvegardes, les migrations et les procédures de reprise doivent donc être conçues pour empêcher que deux machines agissent comme le même validateur de façon dangereuse.

### 4.5 Un actif immobilisé n'est pas une protection absolue

La preuve d'enjeu crée une incitation, mais la sécurité dépend aussi de la distribution des mises, des règles de retrait, des pénalités, du coût d'acquérir ou contrôler une mise, des marchés et de la réaction de la communauté à une crise. Une attaque peut chercher à perturber le réseau sans chercher uniquement un profit direct. Une collusion, une censure prolongée ou une défaillance logicielle peuvent avoir des effets différents d'une double dépense classique.

La preuve d'enjeu n'annule pas non plus la nécessité des clients logiciels. Si les validateurs et les utilisateurs exécutent une version boguée, une mise importante ne corrige pas automatiquement l'erreur. Des clients indépendants, des tests, une gouvernance d'urgence et une distribution saine sont importants.

## 5. Comparaison PoW et PoS

| Critère | Preuve de travail (PoW) | Preuve d'enjeu (PoS) |
|---|---|---|
| Ressource principale | Puissance de calcul et énergie | Mise économique immobilisée et participation des validateurs |
| Producteur | Mineur | Validateur sélectionné selon les règles du protocole |
| Coût d'attaque typique | Accès à une part suffisante de la puissance de calcul et coûts opérationnels | Contrôle ou influence d'une part suffisante des mises, plus contraintes de consensus |
| Pénalité directe | Le matériel et l'énergie peuvent être gaspillés ; les blocs invalides sont rejetés | Pénalités protocolaires et slashing dans certains cas |
| Consommation énergétique | Peut être élevée en raison de la compétition de calcul | Nettement plus faible pour la production de consensus que la PoW |
| Risques de concentration | Pools, fabricants de matériel, énergie, hébergement | Pools de staking, fournisseurs de garde, opérateurs, concentration de mise |
| Finalité | Souvent probabiliste avec confirmations supplémentaires | Peut fournir une finalité explicite selon le mécanisme |
| Reprise et incidents | Dépendent de la propagation, du travail cumulé et de la coordination | Dépendent des votes, de la disponibilité, des seuils, des pénalités et du mécanisme de finalité |
| Hypothèses critiques | Coût de la puissance de calcul, honnêteté majoritaire selon modèle, règles de validation | Distribution et comportement des validateurs, sécurité des clés, règles de slashing et disponibilité |
| Exemple | Bitcoin | Ethereum |

La comparaison doit être adaptée à une question opérationnelle. Pour évaluer la consommation d'énergie, il faut considérer le mécanisme et l'exploitation. Pour évaluer la censure, il faut observer la distribution effective des producteurs ou validateurs, les politiques de relais et les dépendances. Pour la finalité, il faut comprendre la définition du protocole et le type de risque que l'entreprise veut réduire.

## 6. L'attaque dite des 51 %

L'expression « attaque des 51 % » est un raccourci pour désigner certains scénarios où un acteur contrôle ou influence une majorité de la ressource pertinente au consensus. Sa signification exacte dépend du protocole. Dans une preuve de travail, on parle généralement de la puissance de hachage. Dans une preuve d'enjeu, les conséquences se décrivent à partir des mises, des votes et des seuils de consensus.

### 6.1 Ce qu'une majorité de hash power pourrait permettre

Dans un modèle PoW tel que Bitcoin, un attaquant contrôlant durablement une majorité de la puissance de calcul pourrait augmenter ses chances de construire une branche alternative avec davantage de travail cumulé et de remplacer certains blocs récents. Cela pourrait permettre une double dépense de transactions pour lesquelles il contrôle les conditions de dépense, ou perturber l'inclusion des transactions.

Cette capacité ne permet pas automatiquement de signer au nom d'un autre utilisateur, de dépenser les UTXO d'autrui sans la clé ou la condition de dépense requise, ni de créer des bitcoins au-delà des règles monétaires que les nœuds valident. Un bloc qui viole ces règles serait rejeté par des nœuds conformes. L'attaque porte surtout sur l'ordre et la sélection de l'historique valide, pas sur l'abolition de toutes les règles cryptographiques.

### 6.2 Censure et double dépense

Un acteur disposant d'une forte influence sur la production peut tenter de ne pas inclure certaines transactions, ou de construire des branches alternatives. La capacité réelle dépend de la durée de contrôle, de la propagation, de la réaction des autres producteurs, des nœuds, des plateformes et du marché. Le coût et les conséquences économiques peuvent être élevés ; l'attaquant n'est pas assuré de gagner financièrement.

Une double dépense ne signifie pas que la même pièce apparaît légitimement deux fois dans l'état final de la chaîne. C'est une tentative de faire accepter des histories différentes à des moments différents. Si une réorganisation retire un bloc qui contenait un paiement, l'état peut revenir à une situation où les fonds semblent disponibles dans la branche retenue. Le bénéficiaire qui a livré un bien sur la base d'une confirmation trop faible supporte alors un risque.

### 6.3 Pourquoi le seuil de 51 % ne résume pas tous les scénarios

Certains effets peuvent apparaître avec une influence inférieure à la majorité, selon la topologie, la disponibilité du réseau, la censure, les règles du protocole ou les ressources de l'attaquant. Dans d'autres cas, une majorité brute ne suffit pas à obtenir l'objectif visé. Les pourcentages ne décrivent pas tout sans préciser la ressource, la durée, les hypothèses, le comportement des autres participants et les conditions de finalité.

Dans les systèmes PoS, une attaque de consensus peut être détectable et entraîner du slashing, mais toutes les attaques ne sont pas automatiquement sanctionnées ou aisément réparables. Les effets dépendent du type de violation, des règles, du comportement des validateurs honnêtes et des procédures de récupération. Un incident grave peut nécessiter une coordination sociale et logicielle, qui est distincte de l'exécution ordinaire du consensus.

## 7. Disponibilité, sûreté et vivacité

La théorie des systèmes distribués distingue plusieurs objectifs. Le vocabulaire exact varie selon les modèles, mais trois idées sont utiles :

- **Sûreté (safety)** : éviter que deux résultats incompatibles soient simultanément considérés comme définitifs selon les garanties du protocole.
- **Vivacité (liveness)** : permettre au système de continuer à progresser, par exemple en finalisant de nouveaux blocs, lorsque les hypothèses prévues sont remplies.
- **Disponibilité opérationnelle** : la capacité d'un service donné à répondre aux utilisateurs. Ce n'est pas identique à la disponibilité du consensus.

Un réseau peut préserver la sûreté en interrompant temporairement sa progression, plutôt que de finaliser deux historiques contradictoires. À l'inverse, une conception qui tente de continuer à tout prix peut accepter un risque de divergence selon ses hypothèses. Le choix entre sûreté et vivacité apparaît particulièrement lors des partitions réseau et des pannes.

Dans Ethereum, par exemple, une participation insuffisante ou une partition peut affecter la finalité tout en laissant certains blocs proposés ou certaines transactions observables. Dans Bitcoin, la production de blocs peut continuer plus lentement, et les branches concurrentes peuvent devenir plus probables dans des conditions de propagation perturbées. Ces situations exigent un diagnostic précis au lieu d'une simple étiquette « le réseau est en panne ».

## 8. Temps, partitions et blocs concurrents

Les réseaux distribués ne reçoivent pas tous les messages au même instant. Supposons que deux producteurs proposent des blocs valides qui partent du même parent. Un groupe de nœuds reçoit d'abord le bloc A, tandis qu'un autre reçoit d'abord le bloc B. Pendant un temps, le réseau peut avoir deux vues locales. Quand une branche prend l'avantage selon les règles, les nœuds s'y alignent progressivement.

~~~mermaid
flowchart TD
    P["Parent commun"] --> A["Bloc A proposé"]
    P --> B["Bloc B proposé presque simultanément"]
    A --> N1["Nœuds qui voient A en premier"]
    B --> N2["Nœuds qui voient B en premier"]
    A --> A2["Suite éventuelle de A"]
    B --> B2["Suite éventuelle de B"]
    A2 --> C["Sélection selon le consensus"]
    B2 --> C
    C --> F["Vue convergente du réseau"]
~~~

Un tel événement n'est pas forcément une attaque. Il peut être normal, surtout quand le délai de propagation est significatif par rapport à l'intervalle de production. Les protocoles ont des règles pour traiter ces situations. Cependant, des partitions longues ou une divergence persistante peuvent signaler un incident plus sérieux.

Les horodatages aident parfois le protocole à appliquer des contraintes, mais ils ne créent pas une horloge mondiale parfaite. Le consensus dépend de règles et de messages, pas d'une confiance absolue dans un seul serveur de temps. Les opérateurs doivent surveiller la synchronisation, les connexions, les erreurs des clients et les métriques de consensus.

## 9. Gouvernance et mise à niveau du consensus

Les règles de consensus sont exécutées par du logiciel. Les changements doivent être développés, documentés, testés et adoptés par les acteurs concernés. Selon le protocole, une modification peut être rétrocompatible, nécessiter une activation coordonnée ou conduire à une divergence si certains participants gardent des règles incompatibles.

Une mise à niveau peut améliorer la sécurité, les performances ou l'expérience de développement, mais elle peut aussi introduire un bug. Les réseaux importants utilisent des spécifications, des tests automatisés, des réseaux de test, des clients indépendants, des annonces de versions et des procédures de coordination. La possibilité d'une erreur ne disparaît pas ; elle doit être réduite par le processus d'ingénierie et de gouvernance.

La gouvernance ne se limite pas au vote on-chain. Les développeurs écrivent du code, les opérateurs choisissent les versions exécutées, les utilisateurs choisissent les services, les validateurs ou mineurs font des choix opérationnels et les marchés peuvent réagir. Les différentes communautés disposent de mécanismes de décision variés. Il est plus précis d'identifier les acteurs et les règles de chaque réseau que de dire qu'une blockchain est « gouvernée par personne ».

## 10. Staking et minage : risques opérationnels

### 10.1 Exploiter un mineur PoW

Un opérateur PoW doit gérer le matériel, la chaleur, l'électricité, les connexions, les logiciels de minage, la sécurité du pool éventuel et la comptabilité de ses revenus. Le choix d'un pool peut réduire la variance des gains, mais concentre une partie de la coordination de production et introduit des dépendances. Un pool n'est pas lui-même le protocole Bitcoin, même s'il peut influencer les modèles de blocs produits.

Un minage rentable n'est pas garanti. Les coûts fixes, la difficulté, la valeur de l'actif, les frais et l'évolution du matériel peuvent rendre l'activité déficitaire. Le rendement financier ne doit jamais être déduit uniquement de la récompense nominale d'un bloc.

### 10.2 Exploiter un validateur PoS

Un validateur doit protéger ses clés, maintenir un client consensus et souvent un client d'exécution, garantir la disponibilité, appliquer les mises à jour et surveiller les pénalités. Les clés qui signent les messages de consensus sont particulièrement sensibles. Une erreur de déploiement peut entraîner des signatures contradictoires ou une indisponibilité.

Le staking via un service ajoute des risques de garde, de contrat, de gouvernance et de contrepartie. Le fait que les règles du protocole soient vérifiables ne signifie pas que l'opérateur de staking est fiable ou que l'utilisateur peut récupérer ses fonds à tout instant. Il faut examiner les conditions, la liquidité, les frais, les délais de retrait et les procédures de secours.

### 10.3 Risques communs

Les deux approches dépendent de logiciels, du réseau, des opérateurs et d'incitations économiques. Les attaques informatiques, les pannes cloud, les erreurs de configuration, la concentration des fournisseurs, la censure légale ou technique et les vulnérabilités du logiciel peuvent affecter le fonctionnement. La comparaison de consensus doit donc être complétée par une analyse de l'écosystème réellement exploité.

## 11. Étude de cas : deux paiements contradictoires

Alice contrôle une sortie Bitcoin et signe deux transactions valides prises isolément : la première paie Bob, la seconde paie Chloé. Elles dépensent toutes deux la même sortie. Aucune ne peut être acceptée dans le même état final comme si l'autre n'existait pas. Les nœuds qui les reçoivent peuvent traiter différemment les transactions en attente, mais un bloc doit respecter la règle de non-double-dépense.

Le producteur qui inclut l'une des transactions rend l'autre incompatible avec l'état après application du bloc. Si un autre producteur a construit une branche concurrente avec l'autre transaction, les nœuds peuvent temporairement observer deux histories candidates. Le consensus et la sélection de chaîne déterminent ensuite laquelle reste dans l'historique suivi.

Un portefeuille qui affiche « envoyé » indique souvent que la transaction a été signée ou relayée, mais ce n'est pas une garantie d'inclusion. Un explorateur qui affiche une première confirmation donne une information utile, mais il faut encore considérer le risque de réorganisation. Les plateformes adoptent des seuils différents selon la valeur, le coût de fraude et les garanties du réseau.

La même intuition s'applique à d'autres modèles, mais les structures comptables diffèrent. Ethereum utilise notamment le nonce d'un compte et des règles d'exécution ; des transactions concurrentes peuvent avoir le même nonce et être incompatibles. Il faut appliquer le modèle du réseau concerné et ne pas recopier les détails UTXO de Bitcoin dans un système à comptes.

## 12. TP guidé A : simuler un consensus simplifié sur papier

### Objectif

Comprendre que plusieurs propositions peuvent être valides localement sans toutes appartenir à l'historique final. Cette simulation est pédagogique : elle ne reproduit pas toutes les règles de Bitcoin ou d'Ethereum.

### Matériel

Utilise des cartes ou une feuille. Dessine un bloc de départ nommé G. Prépare ensuite les blocs A et B qui référencent tous deux G. Prépare enfin A2 qui référence A, et B2 qui référence B. Tous les blocs sont considérés comme valides dans cet exercice.

### Étape 1 — Simuler une propagation

Un groupe de participants reçoit A avant B ; un autre reçoit B avant A. Note la branche que chaque groupe suit provisoirement et explique pourquoi la divergence peut arriver sans bloc malveillant.

### Étape 2 — Ajouter une règle de sélection fictive

Pour les besoins du TP, suppose que la branche ayant le plus de poids cumulé valide est celle à suivre. Attribue des poids simples : A = 2, A2 = 3, B = 2, B2 = 1. Calcule le poids de chaque branche et détermine laquelle serait suivie avec cette règle pédagogique.

### Étape 3 — Introduire un bloc invalide

Place un bloc A3 sur la branche A qui dépense une valeur inexistante. Bien qu'il augmente le poids fictif, il doit être écarté avant la sélection, parce qu'il viole la validité. Réexplique la différence entre « bloc ayant du poids » et « bloc valide ».

### Étape 4 — Répondre aux questions

**Pourquoi deux nœuds peuvent-ils afficher temporairement des vues différentes ?** Parce que les messages ne leur arrivent pas forcément dans le même ordre et au même moment.

**Pourquoi la majorité de poids ne peut-elle pas rendre le bloc A3 valide ?** Parce que les règles de validité sont vérifiées indépendamment du mécanisme de sélection.

**Dans un système réel, le poids est-il toujours simplement le nombre inscrit sur la carte ?** Non. La preuve de travail, la preuve d'enjeu et d'autres protocoles définissent leurs propres règles et mesures.

## 13. TP guidé B : comparer un paiement PoW et un paiement PoS

Crée un tableau de comparaison à deux colonnes. Pour Bitcoin, décris l'émission d'une transaction, sa diffusion, son inclusion dans un bloc miné, puis l'augmentation des confirmations. Pour Ethereum, décris la diffusion d'une transaction, son exécution dans un bloc, la validation par le réseau PoS et les étapes de justification ou finalité pertinentes.

Le tableau doit comprendre les mêmes étapes pour les deux chaînes : transaction créée, transaction relayée, bloc proposé, validation indépendante, inclusion, confirmations ou finalité, statut en cas de réorganisation. Pour chaque étape, précise quelle information le portefeuille peut afficher et ce qu'il ne peut pas garantir.

### Corrigé indicatif

Bitcoin s'appuie sur la preuve de travail et une règle de chaîne à travail cumulé ; les confirmations supplémentaires rendent une réorganisation de plus en plus coûteuse dans les hypothèses habituelles, sans créer une garantie mathématique absolue après un nombre fixe de blocs. Ethereum utilise la preuve d'enjeu, avec propositions et attestations qui conduisent à une finalité protocolisée lorsque les conditions sont réunies. Dans les deux cas, une interface peut être en retard, une transaction peut échouer au niveau applicatif et les services centralisés peuvent ajouter des risques qui ne proviennent pas du consensus de base.

## 14. Dix questions d'entraînement avec corrigé

### Question 1
Pourquoi un réseau blockchain a-t-il besoin d'un mécanisme de consensus ?

**Corrigé :** Les nœuds peuvent recevoir des transactions et blocs dans des ordres différents et certains acteurs peuvent être malveillants. Le consensus aide les nœuds à choisir une histoire commune parmi les propositions valides.

### Question 2
Un bloc avec une preuve de travail valide est-il nécessairement valide ?

**Corrigé :** Non. Il doit respecter les règles du format, les limites, les transactions et les transitions d'état. Une preuve de travail ne transforme pas un bloc invalide en bloc valide.

### Question 3
Que cherche un mineur Bitcoin ?

**Corrigé :** Un en-tête dont le hash respecte la cible de preuve de travail. Il modifie le nonce ou d'autres données admissibles pour explorer de nouvelles valeurs.

### Question 4
La chaîne la plus longue est-elle toujours celle que retient Bitcoin ?

**Corrigé :** La description correcte porte sur le travail cumulé des chaînes valides. Le nombre de blocs seul ne suffit pas à décrire la règle de sélection.

### Question 5
Quelle ressource centrale utilise PoS ?

**Corrigé :** Une mise économique engagée par les validateurs, accompagnée de règles de participation, de récompense et de pénalité.

### Question 6
Le validateur ayant la plus grande mise peut-il imposer n'importe quel bloc ?

**Corrigé :** Non. Les blocs sont soumis aux règles de validité et au mécanisme de consensus. La mise ne donne pas le droit de modifier les règles à volonté.

### Question 7
À quoi sert le slashing ?

**Corrigé :** À sanctionner certaines violations définies par le protocole, notamment certains comportements de signature ou de vote incompatibles avec la sécurité du consensus.

### Question 8
Une attaque de majorité permet-elle de dépenser directement les fonds de n'importe quelle adresse ?

**Corrigé :** Non. Elle peut affecter la sélection de l'historique ou l'inclusion selon le modèle, mais ne remplace pas les clés et conditions de dépense nécessaires pour autoriser une transaction valide.

### Question 9
Qu'est-ce que la finalité ?

**Corrigé :** Une condition définie par le protocole qui donne à un bloc des garanties de finalisation particulières. Elle ne se confond ni avec l'inclusion initiale ni avec la disponibilité d'une application.

### Question 10
Un fork temporaire signifie-t-il que le réseau a été attaqué ?

**Corrigé :** Pas nécessairement. Il peut résulter de blocs concurrents et de délais de propagation. La durée, la profondeur et les données de l'incident sont nécessaires pour établir un diagnostic.

## 15. Challenge final : analyser une suspicion de double dépense

### Scénario

Une boutique accepte un paiement en crypto-actif. Le portefeuille du client affiche que la transaction a été envoyée, et un explorateur montre une confirmation. Quelques instants plus tard, le paiement n'apparaît plus dans l'historique de la branche retenue par un autre explorateur. Le responsable de la boutique conclut immédiatement que tout le réseau a été piraté.

### Travail demandé

Rédige un rapport d'incident de 500 à 700 mots qui :

- distingue transaction diffusée, transaction incluse et paiement final selon le réseau ;
- explique comment une réorganisation peut faire changer le statut d'une transaction ;
- identifie les données à collecter avant de conclure à une attaque ;
- compare les notions de confirmations Bitcoin et de finalité Ethereum ;
- propose une politique d'acceptation des paiements adaptée au risque.

### Correction proposée

Le message « transaction envoyée » décrit généralement une opération signée ou relayée, pas une garantie de finalité. Le statut affiché par un explorateur dépend du réseau consulté, du retard d'indexation et de la branche qu'il suit. Il faut d'abord confirmer le réseau et l'identifiant exact de la transaction, puis relever le hash du bloc, son parent, l'heure, le nombre de confirmations ou l'état de finalité, ainsi que le comportement des clients ou explorateurs indépendants.

Une réorganisation peut faire sortir un bloc récent de l'historique suivi. La transaction qu'il contenait peut alors ne plus être considérée comme confirmée et peut être incluse de nouveau plus tard. Cet événement peut être ordinaire si deux blocs concurrents ont été produits et que le consensus a choisi une branche. Une réorganisation profonde, répétée ou accompagnée d'autres anomalies nécessite une enquête, mais la seule disparition temporaire d'un affichage ne prouve pas un piratage global.

Sur Bitcoin, les confirmations sont un indicateur de profondeur ; plus de blocs construits au-dessus augmentent généralement le coût d'une réorganisation selon les hypothèses de sécurité, sans rendre le risque absolument nul après un seuil universel. Sur Ethereum, les étapes d'inclusion, de justification et de finalité ont des significations protocolaires distinctes. Une politique de paiement doit donc être propre à la chaîne, au montant, au profil de fraude et au coût d'une contestation.

La boutique devrait éviter de livrer un produit de grande valeur dès qu'un portefeuille indique seulement « envoyé ». Elle doit définir le nombre de confirmations ou le statut de finalité attendu, utiliser un nœud ou un fournisseur fiable avec des contrôles indépendants pour les transactions importantes, conserver les identifiants et horodatages, et disposer d'une procédure pour les cas atypiques. La politique doit préciser les seuils, les exceptions, les délais et les responsabilités plutôt que se contenter d'un seul explorateur.

Enfin, le diagnostic doit séparer les problèmes : l'application peut mal afficher l'état, le fournisseur RPC peut être en retard, un nœud peut suivre une branche différente, ou une véritable anomalie de consensus peut exister. Les preuves doivent être collectées avant toute conclusion. Une bonne réponse d'incident commence par la validation des faits, pas par une affirmation spectaculaire.

## Glossaire

**Attestation :** vote ou message d'un validateur qui exprime une position prévue par le protocole de consensus.

**Bloc candidat :** proposition de bloc qui doit encore être validée et suivie selon les règles du réseau.

**Consensus :** règles et mécanismes qui permettent aux nœuds de converger sur un historique commun dans les hypothèses du protocole.

**Difficulté :** niveau d'exigence de la cible de preuve de travail selon les conventions du réseau.

**Double dépense :** tentative de faire accepter des historiques ou transactions incompatibles qui utilisent la même valeur.

**Finalité :** condition protocolisée qui renforce les garanties qu'un bloc restera dans l'historique accepté.

**Fork :** branche concurrente ou divergence de règles dans une blockchain.

**Mineur :** participant qui cherche à produire un bloc selon un mécanisme de preuve de travail.

**PoS :** preuve d'enjeu, mécanisme reposant notamment sur les mises et les responsabilités de validateurs.

**PoW :** preuve de travail, mécanisme qui fait reposer la production de blocs sur une recherche de preuve de calcul.

**Réorganisation :** changement de la branche suivie qui peut retirer certains blocs précédemment observés de l'historique actif.

**Safety / sûreté :** propriété visant à éviter des décisions finales incompatibles selon le modèle de consensus.

**Slashing :** pénalité protocolaire visant certains comportements de validateurs définis comme sanctionnables.

**Vivacité :** capacité d'un protocole à continuer à progresser lorsque ses hypothèses de fonctionnement sont satisfaites.

## Pour aller plus loin

- Documentation Bitcoin sur la chaîne de blocs : https://developer.bitcoin.org/devguide/block_chain.html
- Documentation Ethereum sur le consensus : https://ethereum.org/developers/docs/consensus-mechanisms/
- Documentation Ethereum sur la preuve d'enjeu : https://ethereum.org/developers/docs/consensus-mechanisms/pos/
- Livre blanc de Bitcoin : https://bitcoin.org/bitcoin.pdf
- Documentation Ethereum sur The Merge : https://ethereum.org/roadmap/merge/

Ces ressources sont des points de départ. Pour une analyse de production, il faut également lire les spécifications du protocole correspondant au réseau et au fork étudiés, vérifier les versions de clients et identifier les garanties exactes pertinentes pour le montant ou l'application concernés.
