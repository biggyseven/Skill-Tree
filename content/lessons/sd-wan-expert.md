# SD-WAN — Niveau Expert

> **Parcours :** Débutant → Intermédiaire → Expert  
> **Fichier :** `sd-wan-expert.md`  
> **Environnement de référence :** Cisco Catalyst SD-WAN, avec un raisonnement applicable aux architectures SD-WAN d'entreprise en général.  
> **Fil rouge :** l'entreprise fictive NovaTech, composée d'un siège, de plusieurs agences, d'un centre de données et de services cloud.


## 1. Positionnement du niveau expert

Le niveau débutant a permis de comprendre pourquoi le SD-WAN sépare le transport physique de la logique réseau. Le niveau intermédiaire a réutilisé ces notions pour concevoir et administrer une première architecture NovaTech : plusieurs liens WAN, des tunnels chiffrés, des VPN de service, des règles de routage applicatif et des mécanismes de supervision.

Le niveau expert ne consiste pas à accumuler des commandes. Il consiste à savoir **concevoir, justifier, mesurer, sécuriser, dépanner et faire évoluer** une architecture sous contraintes réelles. Un ingénieur expert doit être capable de prévoir ce qui se passe lorsqu'un lien devient instable, qu'un contrôleur tombe, qu'une politique est mal ordonnée, qu'un site perd son accès au cloud ou qu'une mise à jour introduit une régression.

Ce cours adopte principalement la terminologie actuelle de Cisco Catalyst SD-WAN :

- **SD-WAN Manager** : plan de gestion et d'exploitation, anciennement vManage.
- **SD-WAN Controller** : composant du plan de contrôle qui distribue routes et politiques, anciennement vSmart.
- **SD-WAN Validator** : composant d'orchestration et d'authentification initiale, anciennement vBond.
- **WAN Edge** : routeur ou appliance qui établit les tunnels de données et applique les décisions de routage et de politique.

Les anciens noms restent présents dans certains journaux, commandes et documents. Il est donc utile de connaître les deux appellations.

### Objectifs de compétence

À la fin de ce cours, tu dois pouvoir :

1. concevoir une topologie résiliente et expliquer précisément ses domaines de panne ;
2. analyser les relations entre underlay, overlay, OMP, TLOC, BFD et routage applicatif ;
3. élaborer une stratégie de segmentation et de partage de routes sans créer de chemins de contournement ;
4. construire des politiques lisibles, déterministes et testables ;
5. définir des objectifs de service mesurables et vérifier qu'ils sont réellement atteints ;
6. diagnostiquer méthodiquement les incidents du plan de contrôle et du plan de données ;
7. préparer une migration, un changement ou une mise à niveau avec un plan de retour arrière ;
8. documenter l'architecture pour que l'équipe d'exploitation puisse agir sans dépendre d'une seule personne.

> **Important :** les noms de menus, la syntaxe de certaines commandes et les fonctions disponibles varient selon la version, le modèle matériel et le système d'exploitation de l'équipement. Vérifie toujours la compatibilité et la documentation correspondant exactement à la version déployée avant toute modification en production.


## 2. Architecture NovaTech : point de départ

NovaTech exploite un siège, un centre de données, plusieurs agences, des utilisateurs mobiles et des services SaaS. Chaque agence possède deux transports lorsque le budget et la couverture le permettent : une connexion Internet professionnelle et une seconde liaison indépendante, par exemple une autre fibre, un accès fixe ou mobile, ou MPLS lorsqu'il reste pertinent.

Les principaux flux sont classés en fonction de leur impact métier, pas seulement de leur numéro de port :

| Classe de trafic | Exemple NovaTech | Besoin principal | Comportement attendu |
|---|---|---|---|
| Temps réel | Voix et visioconférence | Faible latence, gigue contrôlée, pertes faibles | Choisir un chemin satisfaisant le SLA ; appliquer une stratégie de secours définie |
| Métier critique | ERP, commandes, authentification | Continuité, stabilité et traçabilité | Privilégier la disponibilité et la prévisibilité |
| SaaS | Messagerie, collaboration, CRM hébergé | Accès direct efficace et sécurisé | Sortie Internet locale lorsque le modèle de sécurité l'autorise |
| Transfert volumineux | Sauvegardes, réplication, mises à jour | Capacité et maîtrise des coûts | Éviter de saturer les flux interactifs ; planifier si nécessaire |
| Administration | SSH, HTTPS d'administration, supervision | Contrôle d'accès strict | Segment séparé, accès restreint et journalisé |
| Invités ou objets connectés | Wi-Fi visiteurs, imprimantes, IoT | Isolement | Aucune communication implicite vers le réseau métier |

Ce tableau constitue un point de départ. En production, chaque classe doit être associée à des propriétaires applicatifs, des horaires de pointe, un volume estimé, des dépendances DNS/identité, des exigences de chiffrement et un objectif de disponibilité.

### Hypothèses d'adressage et de segmentation

Le cours conserve la logique du niveau intermédiaire :

- **VPN 10** : utilisateurs et postes de travail ;
- **VPN 20** : applications et services métier ;
- **VPN 30** : invités et objets connectés à risque ;
- **VPN 512** : gestion des équipements sur les déploiements Cisco qui réservent ce VPN à cet usage ;
- **VPN 0** : interfaces de transport et connectivité underlay pour les fonctions de contrôle et les tunnels.

Les identifiants de VPN 0 et 512 ont un rôle particulier dans Cisco Catalyst SD-WAN. Ne réutilise pas ces numéros comme des VPN de service ordinaires dans ce modèle. La plage autorisée et les restrictions exactes doivent être vérifiées dans le guide de la version cible.

Les plages IP ci-dessous ne sont que des exemples pédagogiques. En entreprise, un plan IP doit empêcher le chevauchement entre agences, réseaux cloud, VPN d'administration, interconnexions partenaires et sites acquis. Un chevauchement non détecté complique le routage, le NAT, la migration et les opérations de dépannage.


## 3. Concevoir à partir des exigences, pas à partir des fonctions

Une erreur classique consiste à commencer par activer toutes les fonctions du produit, puis à chercher un usage. Une architecture experte part des exigences et traduit chaque exigence en décision de conception, méthode de vérification et procédure de secours.

Pour chaque application importante, documente au minimum :

- propriétaire métier et criticité ;
- source et destination, y compris les dépendances indirectes ;
- protocoles, ports et mode de découverte ;
- sens du trafic et asymétrie acceptable ;
- sensibilité à la latence, à la gigue et aux pertes ;
- débit moyen, débit de pointe et taille des transferts ;
- besoin de chiffrement, d'inspection et de journalisation ;
- chemin de secours attendu et impact d'une interruption ;
- méthode de test qui prouve le bon fonctionnement.

### Construire un objectif de service utile

Dire « la visioconférence doit être rapide » n'est pas exploitable. Il faut une mesure, une fenêtre d'observation et une règle de réaction. Exemple de cible de laboratoire, à ajuster avec les équipes applicatives : perte inférieure ou égale à 1 %, latence aller simple visée sous 150 ms et gigue inférieure ou égale à 30 ms. Ces nombres sont des exemples de conception et **ne sont pas des garanties universelles** : le service, le codec, la géographie et le contrat fournisseur peuvent imposer d'autres objectifs.

Un SLA réseau n'est pas à lui seul un SLA applicatif. Une route peut respecter ses seuils tout en offrant une mauvaise expérience à cause d'un DNS lent, d'un serveur surchargé, d'une congestion LAN ou d'une erreur d'authentification. Il faut corréler les métriques SD-WAN avec les tests applicatifs et l'état des dépendances.

### Matrice de décision de chemin

Pour chaque classe, explicite ce qui se passe lorsque le chemin préféré ne respecte plus le SLA : bascule vers un autre transport, maintien temporaire du chemin, accès via un hub, abandon du flux ou alerte sans bascule automatique. Une règle sans comportement de repli clairement défini est une dette opérationnelle.


## 4. Underlay, overlay et frontière de panne

L'**underlay** désigne la connectivité IP de transport : Internet, MPLS, accès mobile ou circuits privés. L'**overlay** désigne les tunnels et la logique SD-WAN construits au-dessus. Cette distinction n'élimine pas la nécessité de concevoir correctement le réseau physique.

Avant de diagnostiquer l'overlay, vérifie que l'underlay permet effectivement de joindre les destinations nécessaires : adresse de transport, passerelle, résolution DNS éventuelle, chemin retour, filtrage réseau et MTU. Un tunnel chiffré ne corrige pas une route physique absente, un lien instable ou une traduction NAT mal maîtrisée.

### Principes avancés de conception de l'underlay

**Diversité réelle.** Deux circuits ne sont pas indépendants uniquement parce qu'ils sont vendus par deux opérateurs. Ils peuvent partager une gaine, un point de présence, une alimentation, un équipement d'accès ou un trajet métropolitain. Le fournisseur doit pouvoir expliquer la diversité physique lorsque celle-ci est nécessaire à la continuité métier.

**MTU et fragmentation.** L'encapsulation, le chiffrement et les en-têtes des transports réduisent la taille utile d'un paquet. Une application peut fonctionner avec de petits paquets et échouer lors de transferts plus importants. Vérifie le MTU sur le trajet, la découverte du MTU de chemin, les messages ICMP nécessaires et les éventuelles restrictions de fragmentation. Ne diminue pas la MTU au hasard sans mesurer les effets sur tous les types de flux.

**NAT et accessibilité.** Les agences derrière NAT doivent disposer d'un chemin d'établissement de tunnels compatible avec la topologie et les mécanismes pris en charge. La présence d'une adresse publique n'est pas la seule variable : filtrage UDP, durée des états NAT, changements d'adresse et règles de sécurité peuvent affecter les sessions.

**Asymétrie.** Un flux aller peut utiliser Internet et le retour un hub ou un autre opérateur si les règles de routage, de NAT ou d'inspection le permettent. Cette asymétrie peut casser une session avec état, dégrader la performance et compliquer l'analyse. Documente les points où l'asymétrie est acceptable et où elle est interdite.

**Capacité utile.** Un lien annoncé à 1 Gbit/s ne fournit pas nécessairement 1 Gbit/s de capacité utile pour tous les flux chiffrés. Mesure les débits réellement observés, la surcharge due aux encapsulations, la capacité de traitement du routeur et l'effet du profil de sécurité activé.

### Méthode de validation du transport

Pour chaque transport et chaque site, réalise une recette qui comprend : état physique, négociation et erreurs d'interface, adressage, passerelle, DNS si nécessaire, MTU, perte et latence vers des points de test contrôlés, comportement après renouvellement d'adresse, puis continuité après coupure volontaire. Conserve une mesure de référence avant toute modification de politique.


## 5. Maîtriser les plans de contrôle, de gestion et de données

Le découpage en plans est essentiel au dépannage, mais il ne faut pas le confondre avec une garantie absolue de séparation des pannes.

- Le **plan de gestion** sert à administrer, déployer les configurations, consulter l'état du réseau et organiser les opérations. SD-WAN Manager est central dans ce rôle.
- Le **plan de contrôle** distribue les informations de routage et les politiques de contrôle. Les SD-WAN Controllers et le mécanisme OMP y jouent un rôle central.
- Le **plan de données** transporte les paquets utilisateur entre WAN Edges, en appliquant les décisions de routage, les politiques et les tunnels.
- Le **Validator** aide notamment à l'orchestration et à la mise en relation initiale des équipements avec les composants du plan de contrôle.

Une perte d'accès à Manager ne signifie pas nécessairement que tous les flux utilisateur s'arrêtent instantanément. Inversement, un tableau de bord accessible ne prouve pas que les tunnels de données fonctionnent. Le comportement exact dépend de l'état déjà établi, des fonctions utilisées, de la version et du type de panne.

### Concevoir les domaines de panne

La haute disponibilité ne consiste pas uniquement à ajouter un deuxième contrôleur. Elle demande d'analyser séparément :

1. panne d'une interface WAN ;
2. panne d'un opérateur ou d'un chemin physique ;
3. panne d'un WAN Edge ;
4. panne d'un SD-WAN Controller ;
5. indisponibilité du Validator ;
6. panne d'une instance ou du cluster Manager ;
7. perte d'un site central ou d'un hub ;
8. panne d'une alimentation, d'un rack, d'un bâtiment ou d'une région cloud ;
9. incident d'identité, de certificat ou de DNS qui affecte plusieurs composants à la fois.

Pour chaque cas, écris ce qui doit continuer à fonctionner, ce qui peut être temporairement indisponible, comment l'alerte est déclenchée, et comment le service revient à l'état normal.

### Redondance des composants de contrôle

Plusieurs instances du plan de contrôle et une implantation répartie entre domaines de panne peuvent réduire le risque d'un point unique de défaillance. La conception doit toutefois prendre en compte la compatibilité des versions, la capacité, l'accessibilité réseau, les certificats, les règles de pare-feu et les mécanismes d'affinité ou de répartition supportés.

Pour SD-WAN Manager, vérifie le modèle de cluster recommandé pour la version et la plateforme. La redondance des serveurs de gestion ne remplace ni la sauvegarde, ni le test de restauration, ni la supervision des bases, ni la procédure de reprise après sinistre.

### Affinité et capacité des contrôleurs

L'affinité peut aider à organiser les associations entre WAN Edges et contrôleurs, notamment pour des architectures géographiquement réparties. Elle doit être dimensionnée : une stratégie qui concentre trop de sites sur un seul groupe peut augmenter l'impact d'une panne ou créer un goulot d'étranglement.

Ne déduis pas la capacité requise à partir du seul nombre de sites. Prends en compte le nombre de sessions de contrôle, les TLOC, les routes annoncées, les politiques, la fréquence des changements, les exigences de redondance et les pics de reconnexion au redémarrage d'un composant.


## 6. Comprendre OMP, les TLOC et la sélection de routes

OMP (Overlay Management Protocol) distribue les informations de routage et les informations nécessaires au fonctionnement de l'overlay entre les composants concernés. Il ne faut pas le confondre avec le protocole de routage utilisé dans le LAN ou dans un réseau opérateur classique.

Un **TLOC** identifie un point de terminaison de transport d'un WAN Edge. Il associe notamment l'identité du site et les propriétés du transport. Plusieurs TLOC peuvent permettre à une agence d'être joignable par Internet et par un transport privé. La disponibilité d'un TLOC ne suffit pas à garantir qu'une application obtiendra le chemin désiré : la route, la politique, le SLA, le VPN, la topologie et les règles de préférence doivent être cohérents.

Pour analyser une route, réponds à ces questions dans l'ordre :

1. La route existe-t-elle dans la table locale du VPN de service ?
2. Le protocole local l'a-t-il apprise, et avec quelle préférence ?
3. Est-elle annoncée dans l'overlay lorsque cela est attendu ?
4. Le contrôleur la reçoit-il et la distribue-t-il aux sites concernés ?
5. Le site distant accepte-t-il cette route au regard des politiques et de la segmentation ?
6. La route sélectionnée pointe-t-elle vers un TLOC utilisable ?
7. Le tunnel de données correspondant est-il établi et stable ?
8. Les politiques AAR, de données ou de sécurité redirigent-elles le flux ?
9. Le chemin retour est-il valide ?

Cette démarche sépare une panne de distribution de routes d'une panne de transport, d'une politique ou d'un service applicatif.

### Préférences de routes et ambiguïtés

L'existence de plusieurs chemins est utile, mais peut rendre la décision moins évidente. Avant de changer une préférence, inspecte l'origine de la route, les attributs annoncés, les politiques de contrôle, les éventuelles redistributions et les routes concurrentes. Évite de corriger un problème en ajoutant une route statique sans comprendre pourquoi la route dynamique n'est pas utilisée : tu risques de masquer la vraie cause et de créer une panne au prochain changement de topologie.

### ECMP et stabilité

L'équilibrage entre plusieurs chemins peut augmenter l'utilisation des ressources, mais il ne garantit pas que chaque flux dispose du même niveau de qualité. Les flux à état, les pare-feu, les NAT et certaines applications peuvent réagir à des changements de chemin ou à une distribution des paquets inadaptée. Vérifie le comportement réel des sessions longues et le maintien de l'état de sécurité lors des bascules.

### Commandes de première analyse

Sur des équipements Cisco IOS XE Catalyst SD-WAN, les commandes suivantes peuvent être utiles, selon la version :

```text
show sdwan control connections
show sdwan control local-properties
show sdwan omp peers
show sdwan omp routes
show sdwan bfd sessions
show sdwan bfd summary
```

Ces commandes fournissent des indices, pas un diagnostic automatique. Sauvegarde la sortie avant et après une modification ; une seule capture au moment où tout fonctionne ne permet pas toujours de reconstituer une panne intermittente.


## 7. BFD, état des tunnels et qualité réelle du chemin

BFD (Bidirectional Forwarding Detection) contribue à surveiller la connectivité du plan de données entre les WAN Edges. Dans Catalyst SD-WAN, l'état des tunnels de données et les mesures associées participent à la décision de chemin et aux fonctions de routage applicatif.

Il faut distinguer trois notions :

- **Tunnel établi** : un tunnel existe et peut transporter du trafic.
- **Tunnel opérationnel** : les mécanismes de supervision considèrent le chemin comme utilisable.
- **Chemin adapté à l'application** : les performances mesurées respectent les exigences de la classe concernée.

Un tunnel peut être opérationnel mais présenter une latence ou une perte qui le rend mauvais pour la voix. À l'inverse, un chemin momentanément au-dessus d'un seuil peut revenir à la normale quelques secondes plus tard. Le réglage des seuils et de la durée de réaction doit éviter les oscillations sans laisser persister une dégradation inacceptable.

### Lire les métriques avec discernement

- **Latence** : délai mesuré entre les points de mesure ; le résultat ne doit pas être confondu avec la latence aller-retour d'un test applicatif.
- **Perte** : proportion de paquets non reçus pendant la fenêtre de mesure. Une faible perte moyenne peut masquer des rafales de pertes qui affectent la voix ou les flux temps réel.
- **Gigue** : variation du délai entre paquets. Elle peut être plus révélatrice que la latence moyenne pour des applications interactives.
- **Disponibilité** : fraction du temps pendant laquelle le service respecte une définition de fonctionnement. La disponibilité du lien, celle du tunnel et celle de l'application sont différentes.

La mesure reste limitée par son point d'observation. Une mesure du chemin WAN ne voit pas nécessairement la surcharge du Wi-Fi, le CPU d'un serveur ou la latence d'un service cloud.

### Éviter le ping-pong de chemins

Une stratégie AAR trop agressive peut provoquer des changements répétés entre chemins. Cela peut dégrader les sessions, ajouter de la complexité et rendre les incidents difficiles à reproduire. Choisis des seuils basés sur les besoins métiers, vérifie la fréquence d'échantillonnage et les mécanismes de récupération disponibles, puis teste un lien dégradé progressivement plutôt qu'en ne simulant qu'une coupure franche.

Pour les décisions de production, documente le comportement de secours : si aucun chemin ne respecte le SLA, la politique doit préciser si le trafic est envoyé sur le meilleur chemin disponible, conservé sur un chemin existant, redirigé vers un hub ou soumis à une autre action. Le choix dépend de la criticité et du risque métier.


## 8. Concevoir les politiques sans créer de surprises

Les politiques sont l'endroit où la flexibilité du SD-WAN peut devenir une source d'incidents. Une politique efficace est lisible, ordonnée, documentée, limitée au bon ensemble de sites et accompagnée de tests.

### Différencier les familles de politiques

- **Politique de contrôle centralisée** : influence notamment la distribution et la sélection des routes ou les relations entre sites.
- **Politique de données centralisée** : décide du traitement des paquets selon des critères, par exemple le VPN, la destination ou l'application.
- **Application-Aware Routing (AAR)** : sélectionne des chemins en fonction de caractéristiques mesurées du plan de données et d'un SLA associé.
- **Politique localisée** : agit au niveau de l'équipement pour des décisions locales prises en charge par la plateforme, comme certains contrôles de routage ou paramètres d'interface.
- **QoS** : classe, marque et met en file d'attente les paquets ; elle ne remplace pas le choix du chemin WAN.

Une politique AAR n'est pas une politique de sécurité complète. Le fait qu'un flux soit envoyé sur le meilleur chemin ne signifie pas qu'il est autorisé, inspecté ou segmenté correctement.

### Ordre et logique des règles

Les séquences sont évaluées suivant l'ordre défini par la politique. Une règle générale placée trop tôt peut capturer un trafic que tu voulais traiter différemment. Avant publication, examine chaque règle avec au moins quatre attributs : conditions de correspondance, action, périmètre d'application et effet sur les règles suivantes.

Utilise des noms qui expriment l'intention, par exemple `AAR-VOICE-STRICT`, `DATA-GUEST-ISOLATION` ou `CTRL-BRANCH-REACHABILITY`, plutôt que `POLICY-NEW-3`. Documente également les dépendances et la date de dernière validation.

### Procédure sûre de changement de politique

1. Définir le résultat métier attendu et le risque associé.
2. Identifier précisément les sites, VPN, applications, destinations et flux aller/retour concernés.
3. Capturer l'état de référence : routes, tunnels, mesures, règles actives et tests d'application.
4. Vérifier l'ordre des règles et les comportements par défaut.
5. Tester en laboratoire ou sur un groupe pilote représentatif.
6. Activer dans une fenêtre contrôlée avec une personne responsable du retour arrière.
7. Vérifier les routes et tunnels, puis des transactions applicatives réelles.
8. Surveiller les métriques après déploiement et comparer avec la référence.
9. Documenter le résultat et la procédure de retour arrière.

Ne considère pas une tâche de déploiement marquée « réussie » comme une preuve suffisante. Elle montre que l'opération de configuration a progressé selon les critères de l'outil, pas nécessairement que tous les flux métier ont été validés.


## 9. AAR et QoS : deux leviers complémentaires

AAR (Application-Aware Routing) choisit un chemin qui répond aux critères définis pour une classe de trafic. QoS (Quality of Service) traite la concurrence pour les ressources, notamment lorsqu'un lien est congestionné. Une architecture avancée a souvent besoin des deux.

Exemple : une visioconférence peut être dirigée vers un lien ayant une latence et une perte acceptables. Si ce lien est ensuite saturé par une sauvegarde, une politique QoS bien conçue peut limiter l'impact sur la voix. Toutefois, la QoS ne crée pas de capacité supplémentaire ; si le trafic entrant dépasse durablement le débit du lien, il faut réduire la demande, augmenter la capacité ou répartir les flux.

### Conception des classes

Pour chaque classe, définis :

- les applications et les mécanismes d'identification ;
- les objectifs de qualité et la priorité métier ;
- le traitement lorsque le lien est congestionné ;
- les limites de bande passante ou garanties éventuelles ;
- les règles de marquage et la confiance accordée aux marquages reçus ;
- le comportement en cas de sortie Internet locale ;
- l'effet sur les flux non classés.

Évite de traiter tout le trafic « critique » en priorité maximale. Si trop de paquets sont placés dans la classe prioritaire, celle-ci perd sa valeur et peut affamer les autres classes. Toute classification doit être vérifiable par des compteurs et des tests de charge.

### Exemple de politique logique (pseudo-configuration)

Le bloc suivant décrit une intention, **pas une syntaxe CLI directement exécutable** :

```text
SI l'application est Voix/Visioconférence
    choisir les chemins respectant le SLA temps réel
    appliquer une classe QoS adaptée
    si aucun chemin ne respecte le SLA, suivre le repli documenté
SINON SI l'application est ERP
    préférer les chemins disponibles prévisibles
    préserver la connectivité vers les services d'identité et DNS
SINON SI le flux est une sauvegarde planifiée
    limiter son impact sur les flux interactifs
    utiliser les chemins et horaires autorisés
SINON
    appliquer la politique par défaut la plus restrictive compatible
```

L'expert doit traduire cette logique dans les mécanismes exacts de la plateforme, puis vérifier la politique générée et son effet effectif sur le routeur.


## 10. Segmentation avancée et partage contrôlé des routes

La segmentation ne se limite pas à attribuer un VPN différent à chaque type d'utilisateur. Elle doit empêcher les communications indésirables à travers l'overlay, les hubs, les sorties Internet, les interconnexions cloud et les routes apprises localement.

Dans le modèle NovaTech, le VPN 30 pour les invités et les objets connectés ne doit pas atteindre librement les applications du VPN 20. Une exception telle que l'accès à un serveur d'impression ou à un portail invité doit être explicite, limitée aux destinations nécessaires et vérifiée dans les deux sens.

### Le partage de routes n'est pas une autorisation de sécurité

Le **route leaking** permet de rendre certains préfixes visibles entre segments pour partager des services ou accompagner une migration. Il crée une connectivité de routage ; il ne remplace pas une politique de sécurité, une ACL ni l'inspection du trafic.

Avant de partager une route, précise :

1. le VPN source et le VPN destination ;
2. les préfixes exacts à partager ;
3. le sens autorisé et le chemin retour ;
4. le protocole ou la source de route autorisée ;
5. la politique de filtrage attachée ;
6. le comportement en cas de route concurrente ou de retrait ;
7. la preuve que les autres préfixes restent isolés.

Une fuite de route trop large peut créer un accès involontaire à l'ensemble d'un réseau. Une route divulguée dans le mauvais sens peut également provoquer une boucle, une préférence inattendue ou un chemin asymétrique.

### Services partagés

Si plusieurs VPN ont besoin d'un DNS, d'un service d'identité ou d'un dépôt de mises à jour, publie uniquement les préfixes nécessaires et limite les protocoles. Évite les règles du type « autoriser tout le VPN 10 vers tout le VPN 20 » uniquement parce que les deux segments appartiennent à la même entreprise.

### Vérifications de segmentation

La recette doit comprendre des tests positifs et négatifs : tester ce qui doit fonctionner, puis démontrer que les flux interdits échouent. Vérifie les routes locales et distantes, le chemin utilisé, les journaux du pare-feu et la réponse réelle du service. Un simple test de ping ne prouve pas qu'une application est autorisée ni qu'un segment est correctement isolé.

Les numéros de VPN et les exemples de fonctions ci-dessus suivent le modèle Cisco présenté dans ce cours. Les restrictions de route leaking et les méthodes de configuration dépendent de la plateforme et de la version ; consulte le guide de routage correspondant avant de déployer.


## 11. Service insertion / service chaining

Le **service insertion** (ou service chaining) permet de diriger certains flux à travers un service réseau ou de sécurité, par exemple un pare-feu, selon des règles définies. C'est utile lorsque des flux précis doivent obligatoirement être inspectés avant d'atteindre une destination, notamment pour les communications inter-VPN ou certaines sorties vers Internet.

Il faut distinguer trois choix d'architecture :

- **Inspection distribuée** : chaque agence dispose de contrôles locaux ; la décision est prise près de la source.
- **Inspection centralisée** : le trafic passe par un hub ou un centre de sécurité central, ce qui facilite certaines politiques, mais peut ajouter de la latence et concentrer la capacité.
- **Inspection en chaîne** : seules les classes de trafic sélectionnées sont envoyées vers le service prévu, conformément à une politique.

Aucun modèle n'est idéal partout. L'inspection centralisée simplifie certains contrôles, mais elle augmente la dépendance au hub et peut faire transiter un volume important de trafic par un site central. L'inspection locale réduit la latence de certains flux mais impose une gouvernance cohérente sur tous les sites.

### Les pièges à anticiper

- Le service de sécurité n'est pas disponible, mais la politique continue d'envoyer le trafic vers lui.
- Le trafic retour ne traverse pas le même point d'inspection et l'état du pare-feu n'est plus cohérent.
- Le service est surchargé ou dégradé alors que les tunnels SD-WAN restent actifs.
- La publicité ou le retrait des routes de service est incorrect.
- Une modification du VPN ou du NAT change le chemin de retour.
- La haute disponibilité du service de sécurité existe sur le papier, mais son basculement n'a jamais été testé.

La supervision doit donc observer à la fois l'état du WAN, le chemin sélectionné et la santé du service inséré. Une route valide jusqu'au pare-feu ne prouve pas que le pare-feu traite correctement le flux.


## 12. Sortie Internet locale, hub central et accès cloud

La sortie Internet locale (DIA, *Direct Internet Access*) évite de faire transiter systématiquement le trafic SaaS par un centre de données. Elle peut réduire la latence et économiser la capacité des liaisons centrales. Elle déplace toutefois le point de sortie, de contrôle et de journalisation.

Avant d'activer la sortie locale dans une agence, valide :

- le service DNS et la cohérence des résolutions ;
- le NAT et les adresses publiques attendues par les services distants ;
- le filtrage web, la protection contre les menaces et la politique de journalisation ;
- les exigences d'inspection TLS et les exclusions qui sont justifiées ;
- l'authentification et les contrôles d'accès ;
- la protection contre les fuites de trafic en cas d'erreur de route ;
- le comportement lorsque la liaison Internet locale tombe ;
- la conformité et la conservation des journaux selon les règles applicables.

L'expression « Internet local » ne signifie pas « Internet sans sécurité ». La question à résoudre est : quels contrôles étaient appliqués au hub, lesquels doivent exister localement, et comment prouver qu'ils sont actifs ?

### Comparer le coût total, pas seulement le prix des circuits

Le coût d'une architecture inclut la bande passante, les équipements, les licences, les services de sécurité, le transit cloud, l'exploitation, les incidents et le temps nécessaire à la résolution des problèmes. Une liaison moins chère peut coûter plus cher si elle augmente les interruptions ou si elle ne répond pas aux exigences de l'application.

### Cloud et SaaS

Pour un service cloud, documente les préfixes et noms de domaine utilisés, le type de connexion (Internet, VPN IPsec, interconnexion privée ou combinaison), le mode d'annonce des routes, les éventuelles contraintes de NAT et le plan de secours. Les adresses et points de terminaison cloud peuvent évoluer ; ne fonde pas une politique permanente sur une liste IP saisie manuellement sans processus de mise à jour.


## 13. Multi-région et topologies à grande échelle

Le choix entre une topologie full-mesh, hub-and-spoke ou multi-région dépend du nombre de sites, des échanges inter-agences, de la géographie, des exigences de sécurité et de la capacité des hubs. Le full-mesh facilite certains échanges directs, mais la quantité de relations potentielles et les besoins de contrôle peuvent croître rapidement. Le hub-and-spoke centralise des fonctions et des politiques, mais peut créer un détour de trafic et un point de concentration. Une architecture multi-région peut aider à structurer des déploiements plus vastes si les fonctions et limites de la version choisie sont adaptées.

Pour NovaTech, le choix doit reposer sur les flux réels : les agences d'une même région ont-elles besoin de communiquer directement ? Les applications sont-elles réparties entre plusieurs régions cloud ? Certaines communications doivent-elles passer par un pare-feu régional ? Les liaisons inter-régions ont-elles des objectifs de délai spécifiques ?

### Principes de conception à grande échelle

- Regrouper les sites par besoin, région, capacité et niveau de sécurité plutôt que par simple commodité administrative.
- Éviter d'appliquer une politique mondiale à tous les sites si certains ont des exigences distinctes.
- Préserver un modèle de nommage et de tags stable pour les sites, les transports, les VPN et les politiques.
- Définir des limites de propagation des routes et empêcher qu'une erreur locale se transforme en incident global.
- Dimensionner les hubs et les services d'inspection pour les scénarios de bascule, pas uniquement pour la charge nominale.
- Tester les chemins régionaux et inter-régionaux après modification des politiques de contrôle.
- Documenter les contraintes propres à chaque région : réglementations, fournisseurs, latence, hébergement, capacité et support.

Le modèle multi-région n'est pas une solution magique à un problème de conception. Il ajoute des concepts de topologie et des dépendances qu'il faut maîtriser, notamment la portée des routes et la manière dont les politiques sont appliquées.


## 14. Sécurité opérationnelle : identité, certificats et accès administrateur

Le chiffrement des tunnels ne couvre pas tous les risques. Une architecture SD-WAN dépend aussi de la confiance entre équipements, de la gestion des identités, des droits d'administration, de l'intégrité des configurations et de la capacité à révoquer un équipement compromis.

### Gouvernance des comptes

Applique le principe du moindre privilège. Sépare les comptes d'exploitation courante des comptes de modification de politique globale. Les comptes d'urgence doivent être protégés, surveillés, testés et utilisés uniquement selon une procédure documentée. Les comptes partagés compliquent l'attribution des actions et doivent être évités lorsque des comptes nominatifs sont disponibles.

### Cycle de vie des certificats

Documente l'autorité de confiance, la chaîne de certificats, l'expiration, la procédure de renouvellement, les responsabilités de l'équipe et le plan de retour arrière. Une panne de certificat peut empêcher l'établissement de relations de contrôle même si l'underlay fonctionne parfaitement.

Ne laisse pas le renouvellement au dernier jour. Supervise les dates d'expiration et teste le renouvellement dans un environnement représentatif. Lors d'un incident de contrôle, examine les horloges, les certificats, la chaîne de confiance et les éléments de configuration pertinents avant de réinstaller ou de réinitialiser un équipement.

### Durcissement

- Restreindre l'accès d'administration aux réseaux et identités autorisés.
- Utiliser des protocoles de gestion sécurisés et désactiver les services inutiles conformément aux recommandations du fournisseur.
- Protéger les sauvegardes, les exports de configuration, les clés et les secrets.
- Activer la journalisation et centraliser les traces utiles.
- Séparer les comptes de consultation et de modification.
- Encadrer les changements d'adresse, de DNS et de certificats.
- Prévoir le traitement d'un équipement volé, perdu ou potentiellement compromis.
- Examiner les fonctions de sécurité activées, leur consommation de ressources et leurs dépendances de licence.

### Gestion des changements

Toute modification globale doit être traçable : demande, propriétaire, périmètre, risques, validation, fenêtre, résultats de tests et retour arrière. Une politique poussée à des centaines de sites mérite un contrôle différent d'un changement limité à un site pilote.


## 15. Disponibilité et reprise après sinistre

Il faut distinguer haute disponibilité (HA) et reprise après sinistre (DR). La HA réduit l'impact de certaines pannes au sein d'une architecture prévue pour la redondance. La DR prépare le rétablissement après une panne majeure qui touche un domaine plus large, par exemple un site informatique ou une région entière.

### Définir des objectifs réalistes

- **RTO (Recovery Time Objective)** : durée maximale visée pour rétablir le service.
- **RPO (Recovery Point Objective)** : quantité maximale de données ou de changements que l'organisation accepte de perdre, exprimée en temps.

Ces objectifs doivent être attribués à des services concrets. Le RTO d'une console d'administration, celui d'une agence et celui d'une application métier peuvent différer. Un objectif de reprise n'est utile que s'il a été testé.

### Sauvegardes

Une sauvegarde n'est pas validée tant que sa restauration n'a pas été testée. Conserve les éléments nécessaires au rétablissement dans un emplacement indépendant du domaine de panne, avec un contrôle d'accès approprié. Documente ce qui est inclus : configuration, données d'administration, certificats ou références nécessaires, inventaire, versions logicielles et dépendances externes.

Ne stocke pas les sauvegardes uniquement sur le système que tu cherches à restaurer. Vérifie leur intégrité, leur date, les droits de lecture et la procédure exacte permettant de les utiliser. Une restauration doit être répétée suffisamment souvent pour que l'équipe connaisse la séquence et les pièges.

### Exercices de panne

Effectue des exercices contrôlés : arrêt d'un transport, indisponibilité d'un contrôleur, perte d'un WAN Edge de test, indisponibilité du service de sécurité ou accès Internet local défaillant. Chaque exercice doit avoir un scénario, un périmètre, une personne habilitée à interrompre le test, des critères de réussite et une analyse après test.

Ne teste pas une panne de grande ampleur en production sans validation de risques et plan de retour arrière. L'objectif est de démontrer les hypothèses de conception, pas de provoquer un incident réel.


## 16. Observabilité, indicateurs et capacité

La supervision experte répond à des questions opérationnelles, pas uniquement à « l'équipement est-il vert ? ». Elle doit relier les indicateurs de contrôle, de tunnel, de performance, de routage, d'interface, de sécurité et d'expérience applicative.

### Indicateurs à suivre

| Domaine | Indicateurs possibles | Question opérationnelle |
|---|---|---|
| Underlay | Disponibilité des interfaces, erreurs, perte, latence, capacité consommée | Le transport est-il fiable et suffisamment dimensionné ? |
| Contrôle | État et durée des connexions, stabilité des sessions, changements de pairs | Les équipements gardent-ils une relation de contrôle stable ? |
| Routage | Nombre de routes, préfixes retirés/ajoutés, changements fréquents | Les annonces et les décisions restent-elles cohérentes ? |
| Tunnel | Tunnels disponibles, changements d'état, perte, latence, gigue | Le chemin répond-il aux besoins applicatifs ? |
| Politique | Résultats de déploiement, modifications, règles actives, erreurs | La politique prévue est-elle réellement appliquée ? |
| Sécurité | Événements de pare-feu, anomalies d'authentification, certificats | Les contrôles de sécurité fonctionnent-ils comme prévu ? |
| Application | Temps de réponse, taux d'erreur, réussite de transaction | L'utilisateur obtient-il le service attendu ? |
| Capacité | Utilisation des liens, CPU, mémoire, files d'attente et croissance des routes | Quelle marge reste-t-il en situation de panne ? |

### Construire des alertes utiles

Une alerte doit indiquer la portée, la gravité, le début, la mesure affectée, la condition de déclenchement et les premières vérifications. Des alarmes trop sensibles produisent de la fatigue et finissent ignorées. Une bonne stratégie combine seuils, durée, corrélation et contexte métier.

Évite d'alerter seulement sur la moyenne. Un lien peut afficher une faible latence moyenne alors que des rafales périodiques rendent les appels inutilisables. Utilise des percentiles, des fenêtres pertinentes et des mesures de transaction lorsque la plateforme d'observabilité le permet.

### Capacité et scénario de panne

Le réseau doit disposer d'une marge en exploitation normale et lors de la perte d'un transport. Si deux liens partagent le trafic, calcule ce qui se produit quand l'un disparaît : le lien restant doit-il porter la totalité du trafic ? Les sauvegardes continuent-elles ? La QoS protège-t-elle les flux importants ? Le routeur peut-il traiter le chiffrement, les ACL et les fonctions de sécurité avec la charge de pointe ?

Il faut également considérer le scénario de reconnexion massive après une panne régionale. Des équipements peuvent tenter de rétablir simultanément tunnels et sessions de contrôle. La capacité de reprise doit être testée, et pas uniquement la capacité en régime stable.


## 17. Méthode de dépannage experte

Le dépannage doit suivre une démarche reproductible. Évite de modifier plusieurs variables à la fois : si le service revient, tu ne sauras pas quelle modification a corrigé le problème ; s'il empire, tu auras créé de nouvelles inconnues.

### Les six étapes

**Étape 1 — Définir le symptôme.** Qui est touché ? Une agence, un VPN, une application, un transport ou tous les sites ? Depuis quelle heure ? Le problème est-il permanent, intermittent ou limité à certaines destinations ?

**Étape 2 — Évaluer la portée.** Compare un site touché avec un site sain, un transport avec l'autre, un VPN avec un autre et une application avec une autre. Un contrôle comparatif réduit rapidement l'espace de recherche.

**Étape 3 — Vérifier les couches dans l'ordre.** Commence par l'interface et l'underlay, puis les connexions de contrôle, la distribution des routes, les tunnels et les métriques, la politique appliquée, et enfin le chemin applicatif. Tu peux revenir en arrière dans cet ordre si une observation indique une cause plus basse dans la pile.

**Étape 4 — Capturer avant de changer.** Recueille les commandes d'état, les compteurs, les journaux, les versions, la configuration récente et l'heure exacte. Harmonise les horloges autant que possible pour corréler les événements.

**Étape 5 — Tester une hypothèse unique.** Chaque test doit distinguer au moins deux causes possibles. Exemples : la route manque-t-elle ou est-elle présente mais inutilisable ? Le tunnel est-il en panne ou le flux est-il bloqué par une politique ? Le problème est-il lié à une taille de paquet, à un DNS ou à un service distant ?

**Étape 6 — Corriger, vérifier et documenter.** Après la correction, vérifie l'application réelle, les mesures réseau et le risque de régression. Enregistre la cause racine, le correctif, les signaux qui auraient permis une détection plus précoce et l'action préventive.

### Commandes à connaître

Sur Cisco IOS XE Catalyst SD-WAN, les commandes ci-dessous constituent des points de départ courants. Adapte-les à la version, au mode de fonctionnement et à l'équipement ; la sortie exacte peut différer.

```text
show sdwan control connections
show sdwan control local-properties
show sdwan omp peers
show sdwan omp routes
show sdwan bfd sessions
show sdwan bfd summary
show sdwan tunnel statistics
show ip interface brief
show interfaces counters errors
show logging
```

Pour vérifier la table de routage d'un VPN de service, utilise la commande de routage correspondant au VPN/VRF et au système d'exploitation, par exemple une commande de consultation de route dans la VRF concernée. Pour les tests, sélectionne explicitement l'interface ou le contexte VPN approprié ; un ping lancé depuis le mauvais VPN peut conduire à une conclusion erronée.

Des commandes liées à l'application, à la politique effective ou au chemin de service existent également selon la version. Avant un exercice de production, confirme leur disponibilité via l'aide CLI ou le guide officiel. Évite de copier une commande trouvée pour une ancienne version sans la vérifier.

### Cas A — L'agence ne peut joindre aucun site distant

1. Vérifier l'état des interfaces WAN et les passerelles de transport.
2. Vérifier l'heure, le DNS si les contrôleurs sont référencés par nom, le NAT et les filtrages.
3. Consulter les connexions de contrôle et les propriétés locales de transport.
4. Vérifier les pairs OMP puis les routes apprises.
5. Vérifier les tunnels de données et leurs mesures.
6. Comparer avec un site de même modèle qui fonctionne.
7. Examiner les changements récents, certificats et règles de pare-feu.

Ne réinitialise pas l'équipement avant d'avoir collecté les éléments qui permettront d'expliquer la panne.

### Cas B — Le contrôle est établi mais l'application échoue

Le fait que les contrôleurs soient joignables ne prouve pas que le flux utilisateur passe. Vérifie le VPN, la route locale, la route de destination, le tunnel, le chemin retour, les politiques de données, l'AAR, le NAT et les contrôles de sécurité. Teste ensuite une transaction applicative et ses dépendances, par exemple DNS ou identité.

### Cas C — Une application est lente mais le tunnel est « up »

Compare la perte, la latence et la gigue sur les transports ; contrôle la capacité et les files d'attente ; recherche un lien saturé ou un changement de chemin fréquent. Vérifie aussi le LAN, le Wi-Fi, le service cloud et le serveur. Une corrélation temporelle entre la dégradation et un changement de route ou une opération de sauvegarde peut être plus utile qu'un ping isolé.

### Cas D — Un site ne reçoit plus une route précise

Détermine d'abord si la route existe à la source. Vérifie ensuite l'annonce, les politiques de contrôle, la réception OMP, le VPN de destination, les filtres et les éventuelles règles de partage de routes. Confirme qu'une route concurrente ne la remplace pas. Compare les attributs et la situation avec un site sain avant d'ajouter une route statique.

### Cas E — Les tunnels oscillent

Regarde les événements physiques, les erreurs d'interface, la perte, les renouvellements NAT, les changements de routes et les journaux BFD. Vérifie si les deux extrémités voient le même événement au même instant. Cherche une cause commune avant d'augmenter les minuteries, car un réglage trop permissif peut masquer une dégradation réelle.


## 18. Cycle de vie logiciel et mise à niveau

Une mise à niveau SD-WAN est une opération sur une architecture distribuée. Elle affecte potentiellement le plan de gestion, le plan de contrôle, les WAN Edges, les compatibilités matérielles, les fonctions de sécurité et les mécanismes d'onboarding.

### Avant de choisir une version

Consulte les notes de version, la matrice de compatibilité et les versions recommandées par le fournisseur pour les composants que tu utilises. Ne choisis pas la version la plus récente uniquement parce qu'elle existe, ni une version ancienne uniquement parce qu'elle est connue. Le choix doit tenir compte du matériel, des fonctionnalités requises, des défauts connus, du cycle de support et des contraintes d'interopérabilité.

### Préparation obligatoire

- Vérifier la compatibilité entre Manager, Validator, Controllers et WAN Edges.
- Lire les prérequis et les chemins de mise à niveau pris en charge ; certaines migrations demandent une version intermédiaire.
- Examiner les défauts ouverts et résolus qui concernent la topologie et les fonctions réellement utilisées.
- Vérifier l'espace disque, la santé du cluster, la synchronisation des bases et les ressources.
- Sauvegarder la configuration et les données pertinentes, puis confirmer que la sauvegarde est exploitable.
- Préparer les images depuis une source officielle et vérifier leur intégrité selon les instructions du fournisseur.
- Définir l'ordre d'upgrade exact indiqué par la documentation de la version cible.
- Tester d'abord dans un environnement de préproduction ou sur un petit groupe pilote lorsque c'est possible.
- Préparer une fenêtre, des responsables, des tests post-changement et un plan de retour arrière réaliste.

### Déploiement progressif

Ne mets pas à niveau tous les sites critiques simultanément, sauf si la procédure officielle l'impose et que le risque a été accepté. Commence par un groupe pilote représentatif, valide le plan de contrôle, la connectivité, les politiques et les applications, puis élargis par vagues.

Après chaque étape, contrôle la stabilité des sessions, les routes, les tunnels, les SLA, la charge des équipements et les journaux. Une mise à niveau qui semble réussie immédiatement peut présenter une dégradation lorsque les liens sont chargés ou lors d'un événement de bascule.

### Retour arrière

Le rollback n'est pas toujours l'inverse mécanique de l'upgrade. Il peut exister des contraintes de compatibilité, de format de base de données ou de configuration. La procédure de retour doit être lue et testée avant le changement, et non découverte après l'échec.

Références à consulter selon le besoin : guide de maintenance réseau, guide de mise à niveau Manager, matrice de compatibilité et notes de version Cisco Catalyst SD-WAN.


## 19. Automatisation, API et prévention de la dérive

L'automatisation devient utile lorsqu'elle réduit les erreurs répétitives, garantit la cohérence et fournit des preuves. Elle devient dangereuse lorsque les scripts appliquent une politique sans validation, sans contrôle de périmètre ou sans mécanisme de retour arrière.

### Principes d'automatisation

1. **Déclarer l'intention.** Décrire le résultat attendu indépendamment des clics dans l'interface.
2. **Valider les entrées.** Vérifier les noms de sites, VPN, adresses, groupes, plages et options avant toute modification.
3. **Utiliser un mode de prévisualisation.** Montrer ce qui serait modifié, puis demander une approbation adaptée au risque.
4. **Limiter le périmètre.** Utiliser un site pilote ou un groupe de test plutôt que l'ensemble de la production.
5. **Contrôler le résultat.** Vérifier la configuration effective et le comportement réseau après le déploiement.
6. **Journaliser sans exposer les secrets.** Conserver les opérations, les identifiants de tâche, les résultats et les erreurs utiles ; ne pas écrire de mots de passe ou de jetons dans les journaux.
7. **Rendre les opérations idempotentes lorsque possible.** Une seconde exécution ne doit pas créer des objets dupliqués ou des différences imprévues.
8. **Gérer les erreurs explicitement.** En cas d'échec partiel, interrompre l'expansion, signaler les sites concernés et déclencher un plan de reprise clair.

### Gestion de la dérive

Une dérive apparaît lorsque l'état réellement déployé ne correspond plus à l'état attendu : modification manuelle, tâche interrompue, changement local non documenté ou modèle obsolète. Il faut distinguer une différence volontaire d'une différence non maîtrisée. La correction automatique d'une dérive peut elle-même être risquée si la référence est erronée.

Garde les modèles, les paramètres et les politiques dans un système de gestion des changements versionné. Ajoute une revue des différences avant déploiement, en particulier pour les politiques globales, l'accès d'administration, les certificats, le route leaking et les sorties Internet locales.

### Pseudo-code d'un contrôle post-déploiement

```python
# Exemple pédagogique : logique de contrôle, pas un client API Cisco prêt à l'emploi.

sites = obtenir_sites_du_groupe_pilote()
resultats = []

for site in sites:
    etat = lire_etat_sdwan(site)
    controles = {
        "control_ok": verifier_controle(etat),
        "routes_ok": verifier_routes_attendues(etat),
        "tunnels_ok": verifier_tunnels_requis(etat),
        "policy_ok": verifier_politique_attendue(etat),
    }
    resultats.append({"site": site, "controles": controles})

if any(not all(r["controles"].values()) for r in resultats):
    arreter_deploiement_et_generer_rapport(resultats)
else:
    autoriser_la_vague_suivante(resultats)
```

Les fonctions sont fictives : elles représentent des contrôles à implémenter avec l'API et les données réellement disponibles dans l'environnement. Ne copie pas ce pseudo-code en production comme s'il s'agissait d'un programme complet.


## 20. Migration d'un WAN traditionnel vers SD-WAN

Une migration réussie déplace les services sans faire perdre la maîtrise du réseau. Le risque principal est souvent le cumul de plusieurs changements : adressage, routage, sécurité, NAT, DNS, QoS et topologie, tous modifiés dans la même fenêtre.

### Inventaire et préparation

Recense les circuits, interfaces, routes, VLAN, VRF, ACL, NAT, règles de pare-feu, dépendances applicatives, tunnels IPsec existants, mécanismes de haute disponibilité et processus de supervision. Identifie également les flux rarement utilisés mais importants : administration, sauvegarde, supervision, authentification et reprise après panne.

Établis une référence de performance et un plan de tests avant de toucher à la topologie. Sans cette référence, il est difficile de démontrer qu'une migration a amélioré ou détérioré le service.

### Stratégie par étapes

1. Préparer les transports et l'adressage en parallèle du réseau existant.
2. Enrôler le WAN Edge et valider la confiance, les sessions de contrôle et la gestion.
3. Établir l'overlay sans basculer immédiatement tous les flux métier.
4. Tester les routes, la segmentation, la sécurité, la sortie Internet et les mécanismes de secours.
5. Migrer une application ou une classe de trafic à la fois lorsque la topologie le permet.
6. Confirmer les transactions métier et les métriques pendant une période d'observation définie.
7. Étendre la migration par groupes représentatifs.
8. Retirer les chemins anciens seulement après validation et accord des propriétaires applicatifs.

### Retour arrière de migration

Un retour arrière doit préciser la condition de déclenchement, les routes et politiques à restaurer, l'ordre des opérations, le responsable de la décision et la preuve que le chemin précédent reste exploitable. Si les deux architectures coexistent temporairement, évite les annonces concurrentes non maîtrisées et surveille les boucles, les routes préférées et les chemins retour.


## 21. Analyse de risque et décisions d'architecture

L'ingénieur expert expose les compromis. Une bonne décision n'est pas forcément la fonction la plus sophistiquée : c'est celle qui répond au besoin avec un niveau de complexité et de risque acceptable.

| Décision | Avantage potentiel | Risque ou coût à maîtriser |
|---|---|---|
| Sortie Internet locale | Latence réduite, moins de trafic via les hubs | Sécurité, journalisation, NAT et politique à appliquer localement |
| Inspection centralisée | Contrôle homogène et visibilité centralisée | Dépendance au hub, détour de trafic, capacité requise en mode dégradé |
| Full-mesh | Chemins directs entre de nombreux sites | Complexité, nombre de chemins et gouvernance des flux |
| Segmentation stricte | Limite les mouvements latéraux | Exige un inventaire précis des dépendances et un processus d'exception |
| AAR avec seuils stricts | Réaction rapide aux dégradations | Changements de chemin trop fréquents si les mesures fluctuent |
| Liens multiples | Tolérance aux pannes et capacité accrue | Coût récurrent, dépendances physiques cachées, exploitation plus complexe |
| Déploiement automatisé | Cohérence et rapidité | Impact étendu en cas d'erreur ou de validation insuffisante |

Pour chaque décision, note le besoin métier, les options considérées, l'option retenue, les raisons, les risques acceptés, les mesures de réussite et la date de réexamen. Ce journal évite de répéter les mêmes débats et facilite les audits.


## 22. Travaux pratiques experts

Les scénarios qui suivent sont conçus pour être réalisés dans un laboratoire ou une maquette représentative. Ils ne supposent pas qu'une commande ou un résultat soit identique sur toutes les versions.

### TP 1 — Dégradation progressive d'un transport

**Situation :** l'agence NovaTech possède deux transports. Le transport Internet reste techniquement actif, mais la perte de paquets monte et la visioconférence devient instable.

**Travail demandé :**

1. relever l'état de l'underlay, des tunnels et des mesures ;
2. identifier la classe AAR appliquée au trafic ;
3. observer le changement éventuel de chemin ;
4. vérifier le comportement lorsque le SLA est dépassé puis redevient conforme ;
5. examiner l'impact sur la voix, le CRM et les sauvegardes ;
6. proposer un réglage de seuil et un plan de test justifiés.

**Critère de réussite :** le trafic temps réel suit le comportement documenté, les flux moins sensibles ne provoquent pas de bascule inutile et les preuves sont consignées.

### TP 2 — Route absente entre deux VPN

**Situation :** un serveur DNS partagé doit être accessible depuis les VPN 10 et 20, mais le VPN 10 ne le joint plus après une modification de segmentation.

**Travail demandé :** déterminer si la panne vient de la route source, de sa distribution, du partage de routes, d'une politique de contrôle, d'une règle de données, du pare-feu ou du chemin retour. Rétablir uniquement la connectivité requise et prouver que le VPN 30 reste isolé.

**Critère de réussite :** les flux autorisés fonctionnent, les flux non autorisés échouent et aucune route plus large que nécessaire n'est annoncée.

### TP 3 — Perte d'un contrôleur

**Situation :** un SD-WAN Controller devient indisponible durant une heure.

**Travail demandé :** vérifier le comportement prévu du plan de contrôle, les associations restantes, l'état des routes, les éventuelles alarmes et la capacité de la redondance. Comparer le comportement observé avec le plan de résilience documenté.

**Critère de réussite :** l'équipe démontre les services affectés et non affectés, identifie les limites de la protection et produit un rapport sans confondre disponibilité du contrôle et disponibilité applicative.

### TP 4 — Sortie Internet locale sécurisée

**Situation :** NovaTech souhaite que les agences accèdent directement à un SaaS plutôt que de traverser le centre de données.

**Travail demandé :** définir la politique de sortie, les règles NAT, la sécurité locale, la journalisation, le comportement en cas de panne, les tests DNS et les contrôles de prévention des fuites. Comparer les résultats de latence et de capacité avant et après.

**Critère de réussite :** la latence s'améliore ou l'amélioration attendue est quantifiée ; les contrôles de sécurité demeurent vérifiables ; le plan de secours est testé.

### TP 5 — Préparation d'une mise à niveau

**Situation :** une mise à niveau est requise pour supporter une fonction ou corriger un défaut.

**Travail demandé :** construire le dossier de changement : versions source et cible, compatibilité, séquence officielle, prérequis, sauvegardes, pilote, critères de réussite, risques, fenêtres, responsables et retour arrière.

**Critère de réussite :** aucune étape ne dépend d'une hypothèse non vérifiée et le retour arrière est décrit avant le début de l'opération.

### TP 6 — Incident intermittent multi-sites

**Situation :** plusieurs agences signalent des lenteurs pendant les sauvegardes nocturnes. Les tableaux de bord ne montrent pas de panne franche.

**Travail demandé :** corréler les horaires, les classes QoS, l'utilisation de chaque transport, les changements AAR, la capacité du hub, les erreurs d'interface et les métriques applicatives. Formuler puis tester une hypothèse à la fois.

**Critère de réussite :** la cause racine est prouvée par des observations reproductibles, et la correction ne dégrade pas les flux prioritaires.


## 23. Étude de cas finale : concevoir le SD-WAN cible de NovaTech

Tu es responsable de l'architecture cible. NovaTech prévoit de passer de plusieurs liaisons opérateur isolées à un SD-WAN exploitable de façon centralisée. Le siège héberge encore quelques applications internes ; le reste migre progressivement vers le cloud. Les agences ont des contraintes de capacité différentes. Certaines accueillent des visiteurs et des équipements IoT. L'équipe réseau est réduite et exige des procédures de dépannage simples.

### Livrables obligatoires

**A. Architecture logique.** Présenter les rôles de Manager, Validator, Controllers et WAN Edges ; les domaines de panne ; les régions ; les hubs ; les transports ; et les fonctions de sécurité.

**B. Plan de segmentation.** Définir les VPN de service, les flux inter-segments autorisés, les préfixes partagés, les chemins d'inspection et les tests négatifs.

**C. Stratégie de routage.** Décrire la distribution des routes, les préférences, les annonces locales, les chemins de secours, le traitement des routes concurrentes et la connectivité cloud.

**D. Matrice AAR/QoS.** Associer chaque classe d'application à ses objectifs, aux chemins souhaités, aux règles de secours, aux classes de congestion et aux indicateurs.

**E. Plan de sécurité.** Décrire les rôles d'administration, la protection des secrets, le renouvellement des certificats, les journaux, la sortie Internet locale et le traitement d'un équipement compromis.

**F. Plan d'exploitation.** Fournir les commandes de diagnostic réellement disponibles, les métriques, les seuils d'alerte, les procédures d'incident et les responsables de l'escalade.

**G. Plan de changement.** Définir la migration progressive, la stratégie pilote, les tests de chaque vague, les critères d'acceptation et le retour arrière.

**H. Validation de résilience.** Expliquer comment tester la perte d'un transport, d'un Edge, d'un contrôleur, d'un hub et d'un service de sécurité sans mettre inutilement la production en danger.

### Barème d'auto-évaluation

| Domaine | Points |
|---|---:|
| Architecture, domaines de panne et capacité | 15 |
| Routage, OMP, TLOC et analyse des chemins | 15 |
| Segmentation et sécurité | 15 |
| AAR, SLA et QoS | 15 |
| Observabilité et dépannage | 15 |
| Cycle de vie, migration et retour arrière | 15 |
| Clarté documentaire et justification des compromis | 10 |
| **Total** | **100** |

Interprétation indicative :

- **90–100 :** conception cohérente, contrôlable et testable ;
- **75–89 :** bonne maîtrise, quelques zones à renforcer ;
- **60–74 :** architecture plausible mais procédures ou preuves insuffisantes ;
- **moins de 60 :** reprendre les fondamentaux du plan de contrôle, des politiques, de la segmentation et de la résilience.

Une bonne note ne remplace pas une revue technique, un test de charge ou un exercice de reprise.


## 24. Erreurs d'expert à éviter

1. **Confondre tunnel actif et application disponible.** Le tunnel n'est qu'une partie du chemin applicatif.
2. **Déployer une politique globale sans pilote.** Une règle incorrecte peut toucher tous les sites en même temps.
3. **Utiliser le route leaking comme contrôle d'accès.** Il rend les routes accessibles ; il ne remplace pas une politique de sécurité.
4. **Choisir les seuils AAR par intuition.** Il faut un objectif applicatif, des mesures de référence et des essais en situation dégradée.
5. **Faire confiance à deux liens sans vérifier leur indépendance.** Une panne physique commune peut couper les deux.
6. **Ignorer les chemins retour.** NAT, pare-feu et routage asymétrique sont des causes fréquentes d'incidents.
7. **Considérer la sauvegarde comme une reprise.** Seul un test de restauration apporte cette preuve.
8. **Mettre à niveau sans vérifier les compatibilités.** La version, le matériel et les chemins d'upgrade conditionnent la faisabilité.
9. **Automatiser sans contrôle de périmètre.** Une exécution rapide peut diffuser une erreur plus vite.
10. **Clore un incident sans cause racine.** Le service peut revenir sans que le risque de récidive soit traité.
11. **Surveiller uniquement l'état des équipements.** Les objectifs doivent être exprimés à l'échelle des flux et des applications.
12. **Documenter seulement le fonctionnement normal.** Les procédures les plus précieuses sont souvent celles qui décrivent les pannes et le retour à l'état stable.


## 25. Glossaire expert

- **AAR — Application-Aware Routing :** sélection de chemin en fonction de mesures et de critères associés à une classe de trafic.
- **BFD — Bidirectional Forwarding Detection :** mécanisme de détection rapide de la perte de connectivité entre points compatibles.
- **DIA — Direct Internet Access :** accès Internet depuis le site plutôt que via un point central.
- **DR — Disaster Recovery :** stratégie de reprise après sinistre.
- **ECMP — Equal-Cost Multi-Path :** utilisation de plusieurs chemins considérés comme équivalents selon les règles de routage applicables.
- **HA — High Availability :** mécanismes destinés à réduire l'interruption lors de certaines pannes.
- **MTU — Maximum Transmission Unit :** taille maximale de paquet ou de trame prise en charge sur une interface ou un chemin selon le contexte.
- **OMP — Overlay Management Protocol :** mécanisme de distribution des routes et informations d'overlay dans Cisco Catalyst SD-WAN.
- **RPO — Recovery Point Objective :** perte de données maximale acceptable exprimée en durée.
- **RTO — Recovery Time Objective :** durée cible maximale de rétablissement d'un service.
- **SLA — Service Level Agreement :** engagement de service ou ensemble de seuils associés à une qualité attendue.
- **TLOC — Transport Location :** identification d'un point de terminaison de transport dans l'architecture Cisco SD-WAN.
- **Underlay :** réseau IP physique ou opérateur utilisé comme transport.
- **Overlay :** tunnels et logique réseau construits au-dessus de l'underlay.
- **WAN Edge :** équipement en bordure du WAN qui participe à l'overlay et transporte les données utilisateur.
- **Route leaking :** partage contrôlé de routes entre segments de routage distincts.
- **Service chaining :** acheminement d'un flux à travers une chaîne de services réseau ou de sécurité.


## 26. Références officielles et approfondissement

Les documents ci-dessous sont des références de départ. Privilégie toujours la documentation liée à la version installée et vérifie les restrictions propres aux plateformes utilisées.

1. [Cisco Catalyst SD-WAN Policies Configuration Guide — versions 26.x et ultérieures](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide.html) — cadre général des politiques centralisées et localisées.
2. [Application-Aware Routing — guide des politiques Cisco Catalyst SD-WAN](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/AAR/app-aware-routing.html) — mesure des chemins, SLA et sélection des tunnels.
3. [Cisco Catalyst SD-WAN High Availability Configuration Guide](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/high-availability/high-availability-guide/high-availability.html) — redondance et stratégies de disponibilité.
4. [Redondance des composants de contrôle](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/high-availability/high-availability-guide/high-availability/control-components-redundancy.html) — composants de contrôle et redondance du Manager.
5. [Cisco Catalyst SD-WAN Routing Configuration Guide — route leaking](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/routing/routing-configuration-guide/route-leaking-between-vpns-ref/route-leaking.html) — partage de routes entre segments.
6. [Configurer le route leaking](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/routing/routing-configuration-guide/route-leaking-between-vpns-ref/configure-route-leaking.html) — procédure et prérequis.
7. [Service insertion / service chaining](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/policies/policies-configuration-guide/sd-wan-service-insertion/information-about-service-insertion.html) — insertion de services dans le chemin du trafic.
8. [Cisco Catalyst SD-WAN Network Maintenance Guide](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/network-maintenance/network-maintenance.html) — mise à niveau, maintenance et opérations sur les équipements.
9. [Cisco Catalyst SD-WAN Device Compatibility](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/release/compatibility/sdwan-device-compatibility.html) — compatibilité matériel et logiciel.
10. [Versions logicielles Cisco Catalyst SD-WAN recommandées](https://www.cisco.com/c/en/us/support/docs/routers/sd-wan/215676-cisco-tac-and-bu-recommended-sd-wan-soft.html) — recommandations évolutives et défauts connus.
11. [Dépannage des erreurs BFD courantes](https://www.cisco.com/c/en/us/td/docs/routers/sdwan/26x-later/routing/routing-configuration-guide/bfd/troubleshoot-common-bfd-errors.html) — démarche de diagnostic BFD.


## Conclusion

Le niveau expert est atteint lorsqu'on sait expliquer le comportement du réseau dans les situations difficiles, pas seulement configurer le scénario nominal. L'ingénieur doit relier les besoins applicatifs à la conception des transports, aux décisions de routage, aux politiques, à la sécurité et à l'exploitation. Il doit également prouver ses hypothèses par des mesures, tester les pannes de façon contrôlée, documenter les compromis et préparer un retour arrière avant les changements risqués.

Pour NovaTech, la cible n'est pas simplement un réseau qui établit des tunnels. C'est un service WAN mesurable, segmenté, résilient et exploitable, dont les réactions en cas de panne sont prévues et vérifiées.
