# Sécurité des protocoles de routage

> **Mise en contexte**

Les protocoles de routage constituent le système de décision d’un réseau. Ils indiquent aux routeurs quelles destinations sont joignables, par quels voisins, avec quels coûts et selon quelles politiques. Une route erronée, acceptée trop largement ou annoncée au mauvais voisin peut détourner du trafic, rendre un service inaccessible, exposer des données ou épuiser les ressources d’un équipement. Une panne de routage ne se limite donc pas à un problème de connectivité : elle peut devenir un incident de sécurité, de disponibilité et de confiance.

Ce cours prolonge la gouvernance et la conformité par des mesures techniques vérifiables. Il traite en priorité de BGP entre systèmes autonomes, puis des protocoles de routage internes comme OSPF et IS-IS. Les exemples utilisent des adresses et des AS fictifs, dans un laboratoire isolé. Ils sont destinés à durcir les équipements que l’on administre, pas à annoncer des préfixes réels ni à intervenir sur le routage d’autrui.

## Objectifs et méthode

À la fin de ce cours, vous devez savoir expliquer les menaces contre le plan de contrôle, distinguer détournement de préfixe et fuite de routes, écrire une politique d’import et d’export par voisin, interpréter les états RPKI, limiter les annonces anormales, protéger une session de routage, sécuriser OSPF ou IS-IS, surveiller les changements et organiser un retour arrière. Vous devez aussi savoir reconnaître les limites de chaque contrôle : aucune mesure isolée ne rend un réseau invulnérable.

Le parcours recommandé est cumulatif : comprendre les annonces, inventorier les préfixes et les relations, concevoir une politique restrictive, tester cette politique en laboratoire, déployer par étapes, puis observer et documenter les résultats. En production, toute modification de routage doit suivre la procédure de changement de l’organisation.

## 1. Ce que le routage décide réellement

Le plan de contrôle échange et calcule des informations de routage. Le plan de transfert applique la table résultante pour faire passer les paquets. Le premier construit la décision ; le second l’exécute. Une attaque ou une erreur du plan de contrôle peut donc modifier le trajet emprunté par des paquets tout à fait légitimes.

~~~text
                 PLANS D'UN ROUTEUR
+------------------------------------------------+
| Plan de contrôle                               |
| BGP / OSPF / IS-IS | politiques | RIB          |
|              décision de route                 |
+------------------------+-----------------------+
                         |
                         v
+------------------------------------------------+
| Plan de transfert                              |
| FIB | recherche de destination | interface      |
|               transfert des paquets            |
+------------------------------------------------+
                         |
                         v
                réseau de destination
~~~

La RIB (Routing Information Base) conserve les routes candidates et leurs attributs. La FIB (Forwarding Information Base) contient les décisions effectivement utilisées pour transmettre les paquets. Les termes exacts et leur organisation dépendent de l’implémentation. Il faut contrôler les deux niveaux lors du dépannage : une route visible dans les informations BGP n’est pas nécessairement sélectionnée dans la table de routage active.

La disponibilité de la session ne prouve pas que son contenu est légitime. Une session BGP peut être établie tout en acceptant une annonce trop spécifique. De même, un voisin OSPF peut participer à une adjacence tout en annonçant une information de routage inappropriée si l’architecture et les contrôles ne limitent pas son influence.

~~~text
Annonce reçue
    |
    v
Validation syntaxique et identité du voisin
    |
    v
Politique d'import : préfixe, AS_PATH, origine, attributs
    |
    v
Sélection du meilleur chemin selon la politique
    |
    v
Installation dans la RIB puis la FIB
    |
    v
Annonce aux autres voisins selon la politique d'export
~~~

La sécurité doit s’appliquer à chaque transition. Filtrer seulement à l’export laisse potentiellement des routes inutiles occuper la mémoire ou influencer la sélection locale. Filtrer seulement à l’import ne suffit pas si un routeur réannonce ensuite un préfixe qui ne devrait jamais sortir. Le modèle défensif utilise donc des contrôles d’entrée et de sortie indépendants.

## 2. Menaces principales

### 2.1 Détournement de préfixe

Un détournement de préfixe se produit lorsqu’un système autonome annonce un préfixe qu’il n’est pas autorisé à originer, ou lorsqu’une route concurrente attire le trafic destiné à ce préfixe. L’annonce peut être malveillante, accidentelle ou due à une erreur de configuration. Le BGP classique transporte des informations de chemin et de politique, mais ne fournit pas à lui seul une preuve cryptographique complète que l’annonceur est autorisé par le détenteur de l’espace d’adresses.

Les conséquences varient : perte de trafic, itinéraire plus long, observation possible d’une partie du trafic, interception s’il existe une capacité supplémentaire, ou instabilité. Il faut éviter de conclure qu’un détournement aboutit toujours à une interception : le chemin retour, les filtres, le routage interne et le comportement applicatif jouent également un rôle.

### 2.2 Fuite de routes

Une fuite de routes est la propagation d’informations de routage au-delà de la relation ou de la politique prévue. Un client peut, par erreur, réannoncer à un fournisseur une route apprise d’un autre fournisseur. Un pair latéral peut relayer une route reçue d’un autre pair. L’annonce peut être techniquement valide mais contraire aux accords commerciaux ou à la politique de transit.

~~~text
              Fournisseur A
                   |
                   v
             +-----------+
             | AS Client |
             +-----------+
                   |
            fuite non voulue
                   |
                   v
               Fournisseur B

Attendu : la route de A n'est pas réannoncée à B
Risque    : trafic détourné, transit non autorisé, congestion
~~~

Le détournement de préfixe porte sur l’origine annoncée ou le chemin choisi pour un espace donné. La fuite porte sur la propagation d’une route qui n’aurait pas dû être transmise à ce voisin. Ces événements peuvent se chevaucher, mais leurs contrôles ne sont pas identiques : RPKI Origin Validation aide à vérifier l’origine d’un préfixe, tandis que les politiques de relation entre voisins et les rôles BGP visent notamment les fuites.

### 2.3 Épuisement des ressources et instabilité

Un voisin peut annoncer un volume excessif de routes, des préfixes extrêmement spécifiques ou des changements très fréquents. Même si ces annonces ne deviennent pas les meilleures routes, leur traitement consomme de la mémoire et du temps processeur. La mise à jour en rafale peut compliquer les diagnostics et déstabiliser la convergence. Le seuil de préfixes maximum doit protéger la plateforme sans provoquer l’arrêt inattendu d’une session légitime en cas de croissance normale de la table.

### 2.4 Usurpation et compromission de voisin

Une session de routage peut être menacée par des paquets forgés, une usurpation d’adresse, un accès de gestion compromis, une mauvaise protection de la liaison ou une erreur d’identité du voisin. L’authentification de la session aide à réduire certaines possibilités d’injection, mais elle ne valide pas à elle seule les préfixes. Un administrateur disposant de droits excessifs peut également publier une politique dangereuse sans avoir à attaquer le protocole.

### 2.5 Mauvaise configuration et dépendance fournisseur

Des filtres copiés sans revue, une liste de préfixes obsolète, un changement d’ASN mal coordonné ou un défaut de documentation peut créer une faille aussi grave qu’une attaque active. La défense doit inclure une source de vérité des annonces autorisées, des revues de configuration, des tests automatiques et une procédure de retour arrière.

~~~text
MENACES                 CONTROLES PRINCIPAUX
Préfixe non autorisé -> ROA / RPKI / filtres stricts
Fuite de route       -> politiques par relation / BGP Roles / OTC
Annonce massive      -> maximum-prefix / supervision mémoire
Session forgée       -> ACL de contrôle / TCP-AO ou mécanisme disponible
OSPF voisin indu     -> authentification / filtrage / segmentation
Erreur opérateur     -> revue pair-à-pair / test / journal / rollback
~~~

## 3. BGP : modèle de sécurité opérationnel

BGP échange des routes entre systèmes autonomes. En eBGP, les voisins appartiennent généralement à des AS différents ; en iBGP, ils appartiennent au même AS. Une politique sûre commence par décrire chaque relation : client, fournisseur, pair, route server ou liaison interne. Le rôle est plus utile qu’une simple liste d’adresses, car les routes que l’on accepte et celles que l’on transmet dépendent du contrat et de l’intention réseau.

### 3.1 Inventaire avant configuration

Pour chaque voisin, l’inventaire doit contenir au minimum : adresse IP, ASN distant, type de relation, préfixes pouvant être reçus, préfixes pouvant être annoncés, nombre attendu de routes, mode d’authentification, source de vérité, contact d’escalade, fenêtre de maintenance et seuil d’alerte. Toute valeur inconnue doit devenir une action, et non une hypothèse implicite.

~~~text
Voisin     ASN   Relation     Import autorisé      Export autorisé
R-CLIENT   64521 Client       Préfixes du client   Nos routes convenues
R-TRANSIT  64510 Fournisseur  Routes Internet      Nos préfixes autorisés
R-PEER     64530 Pair         Routes du pair       Routes selon accord
R-IBGP     64500 Interne      Politique interne    Politique interne
~~~

Les ASN de cet exemple sont illustratifs. Dans un vrai inventaire, on confirme les ASN, les préfixes et l’accord de peering avec les sources administratives faisant autorité. Ne jamais considérer qu’une route est légitime seulement parce qu’elle provient d’un voisin connu.

### 3.2 Refus par défaut

La politique recommandée est de refuser les annonces par défaut puis d’autoriser explicitement les routes nécessaires. Cette approche évite que l’ajout d’un voisin ou d’une nouvelle annonce bénéficie automatiquement de toute la confiance du routeur. Le principe de refus par défaut s’applique en entrée comme en sortie.

RFC 8212 formalise un comportement de rejet par défaut pour les annonces eBGP lorsque les politiques d’import ou d’export ne sont pas explicitement configurées. Le soutien et le comportement dépendent de la plateforme et de sa version : l’opérateur doit vérifier l’implémentation, les valeurs par défaut et les sorties de commande, plutôt que supposer que la protection est active.

~~~text
              Politique d'import
Annonce voisine ---> [Refus par défaut]
                          |
                +---------+---------+
                |                   |
        correspond aux       aucune règle
        règles approuvées    explicite
                |                   |
                v                   v
             Accepter             Rejeter

Le même raisonnement est appliqué séparément à l'export.
~~~

La liste autorisée doit être conçue pour le voisin précis. Il faut éviter les filtres génériques du type « accepter toutes les routes privées » ou « accepter n’importe quelle route si l’ASN est connu ». Pour un client qui ne possède qu’un seul préfixe, la liste peut être très courte. Pour un fournisseur de transit, une table complète peut être nécessaire, mais cela ne dispense pas de contrôler les préfixes spéciaux, les longueurs de préfixe aberrantes et le volume reçu.

### 3.3 Filtrage des préfixes

Un filtre de préfixe compare l’adresse et la longueur du préfixe annoncés à des critères. Un filtre trop large accepte plus que ce qui est attendu ; un filtre trop strict peut couper un service légitime. Pour un client, on doit expliciter les préfixes alloués et les longueurs annoncées. Une liste doit être générée depuis une source maîtrisée, versionnée, revue et déployée de façon reproductible.

~~~text
Préfixe prévu : 198.51.100.0/24
Annonce prévue : 198.51.100.0/24

Décision :
198.51.100.0/24 -> conforme à la liste
198.51.100.0/25 -> à rejeter sauf autorisation explicite
203.0.113.0/24  -> hors liste, à rejeter

Les plages sont réservées aux exemples documentaires.
~~~

Ne transposez pas mécaniquement cet exemple à une politique de fournisseur qui doit recevoir une table Internet complète. Les critères diffèrent selon la relation. À l’entrée d’un client, seules les routes que le client est autorisé à annoncer devraient être acceptées. À la sortie, seules les routes qu’il est autorisé à recevoir devraient être exportées. La politique de sortie est tout aussi importante : un routeur ne doit pas devenir un transit involontaire.

### 3.4 Filtrage AS_PATH

L’attribut AS_PATH représente les systèmes autonomes traversés par la route dans le modèle BGP classique. Il est utile pour détecter des chemins inattendus, éviter une réannonce de routes contenant son propre ASN et appliquer les règles de relation. Il ne faut pas en faire une preuve absolue de légitimité : les attributs BGP peuvent être mal configurés, et la validation du chemin a des limites.

Les règles doivent être précises. Refuser son propre ASN dans AS_PATH est un garde-fou classique contre des boucles. Les AS privés doivent être traités conformément au contrat et à la politique, et retirés lorsque cela est nécessaire avant de publier les routes vers des pairs qui n’ont pas à les voir. On ne retire pas des attributs au hasard : leur modification peut affecter la politique, le débogage et la traçabilité.

### 3.5 Limite du nombre de préfixes

Une limite de préfixes protège contre l’annonce accidentelle d’une table complète par un client ou contre une croissance qui dépasse la capacité prévue. On définit un seuil fondé sur le contrat, le nombre actuel de routes, une marge de croissance et les capacités matérielles. Le seuil doit être revu périodiquement. Il faut aussi déterminer ce qui se produit à son dépassement : alerte, rejet supplémentaire ou arrêt de session selon les capacités de la plateforme et le risque métier.

Un seuil trop bas transforme une anomalie bénigne en panne ; un seuil trop élevé protège mal. Ne copiez pas un nombre universel. Mesurez le volume réel, documentez le calcul, testez le comportement, configurez une alerte avant le seuil critique et surveillez l’évolution. Une session qui tombe au moment d’une mise à jour légitime doit déclencher un diagnostic, et non un relèvement automatique du seuil sans analyse.

### 3.6 Communautés, agrégation et propagation

Les communautés BGP servent à exprimer des politiques et des instructions dans la chaîne de routage. Elles peuvent signaler une route à ne pas exporter au-delà d’un périmètre, demander une préférence ou identifier l’origine d’une annonce. Leur signification dépend de la politique locale ou de l’accord du fournisseur. Une communauté n’a aucun effet magique si les routeurs ne lui associent pas une action.

Conservez les communautés qui portent une intention de sécurité, notamment les valeurs de portée d’export prévues par les standards, sauf raison documentée de les modifier. Si des communautés sont ajoutées automatiquement, nettoyez ou normalisez celles qui ne doivent pas sortir du réseau. Vérifiez l’effet sur chaque frontière d’AS. Les communautés sont des attributs de politique : une mauvaise traduction ou un nettoyage trop large peut réintroduire une route dans une portée où elle ne devrait jamais se trouver.

### 3.7 BGP Roles et Only-To-Customer

RFC 9234 décrit la négociation de rôles BGP et l’attribut Only-To-Customer (OTC) pour aider à prévenir ou détecter les fuites. Les rôles explicitent la relation de voisinage — fournisseur, client, pair, route server ou client de route server — et les règles associées limitent les routes qu’un AS peut réannoncer. OTC permet de marquer certaines annonces afin de rendre certaines fuites détectables ou inéligibles.

Le bénéfice vient de la cohérence entre la relation configurée de chaque côté et la politique d’annonce. Une valeur de rôle incorrecte peut interrompre la session ou restreindre les routes ; une prise en charge incomplète peut limiter les protections. On doit donc confirmer la compatibilité, commencer en environnement de test, aligner les valeurs avec les deux partenaires et examiner les logs de négociation avant un déploiement généralisé. Ce mécanisme complète les filtres classiques ; il ne remplace pas l’inventaire et l’application stricte des politiques.

~~~text
           Modèle de relation BGP
                 Fournisseur
                     |
               routes vers client
                     v
                  Client
                  /    \
          pas de transit non autorisé
                /        \
           Pair A        Pair B

Rôle négocié + filtre d'export + OTC
= défense en profondeur contre les fuites
~~~

## 4. RPKI et validation de l’origine des routes

### 4.1 Concepts fondamentaux

La Resource Public Key Infrastructure (RPKI) lie des ressources Internet à des certificats et permet notamment de publier des Route Origin Authorizations (ROA). Une ROA indique qu’un ASN est autorisé à originer un préfixe avec une longueur maximale déclarée. La validation de l’origine compare l’annonce BGP à ces informations. Les routeurs reçoivent généralement un état validé via des serveurs cache et le protocole RPKI-to-Router, plutôt que de réaliser la validation cryptographique complète pour chaque annonce.

Trois états usuels sont distingués :

- **Valid** : une ROA correspond à l’origine ASN annoncée et à la longueur du préfixe.
- **Invalid** : une ROA couvrant le préfixe contredit l’ASN d’origine ou la longueur annoncée dépasse le maximum autorisé.
- **NotFound** (parfois appelé NotFound/Unknown selon l’implémentation) : aucune ROA pertinente ne permet de valider ou d’invalider cette annonce.

NotFound ne signifie pas que la route est malveillante. Cela signifie qu’aucune autorisation RPKI correspondante n’est disponible dans l’ensemble de données utilisé. On peut encore appliquer d’autres contrôles : filtres du voisin, registre d’adresses, politique d’AS_PATH, réputation du canal d’information et vérification auprès du titulaire.

~~~text
Route BGP reçue
   | préfixe + ASN d'origine
   v
Validation contre les ROA
   |
   +-- Valid ------> politique normale, autres contrôles maintenus
   |
   +-- Invalid ----> généralement rejeter ou traiter selon politique stricte
   |
   +-- NotFound ---> politique documentée, filtres classiques obligatoires
~~~

### 4.2 Limites de la validation d’origine

RPKI Origin Validation vérifie une relation entre un préfixe, un ASN autorisé et une longueur maximale. Elle ne prouve pas que tous les AS intermédiaires sont honnêtes, ne garantit pas que le chemin de données est optimal, ne règle pas toutes les fuites de routes et ne protège pas les systèmes finaux. Il ne faut donc pas présenter RPKI comme une authentification complète de tout l’AS_PATH.

L’état Invalid doit être investigué. Il peut refléter une annonce hostile, un ROA mal configuré ou une transition légitime pas encore mise à jour. Les opérateurs doivent coordonner la création et la modification des ROA avec l’équipe qui contrôle l’espace d’adresses. Le paramètre maxLength mérite une attention spéciale : plus il autorise de longueurs spécifiques que nécessaire, plus il élargit l’ensemble des annonces possibles.

### 4.3 Déploiement progressif de RPKI

Avant de rejeter les routes Invalid, démarrer en mode observation permet de mesurer la réalité de la table et d’identifier les problèmes connus. Pour chaque invalidité observée, déterminer le préfixe, l’origine annoncée, la ROA correspondante, le partenaire, l’heure, la durée et les décisions proposées. Corriger les ROA du réseau administré avec l’autorité compétente ; pour un tiers, contacter l’opérateur au lieu de modifier des données qui ne lui appartiennent pas.

~~~text
Phase A : connecter un cache RPKI et vérifier son état
Phase B : collecter les états Valid / Invalid / NotFound
Phase C : analyser chaque Invalid significatif
Phase D : corriger les ROA que l'on contrôle
Phase E : tester le rejet sur un périmètre limité
Phase F : élargir avec métriques, alertes et rollback
~~~

Il est nécessaire de surveiller la disponibilité du cache, l’âge des données, l’état des sessions RTR et les volumes par état. Une panne du cache ne doit pas être confondue avec une absence de ROA. La réaction à un cache indisponible doit être définie à l’avance : les politiques exactes dépendent des outils et du niveau de risque, et doivent être testées pour éviter que la perte du service de validation ne provoque une panne généralisée.

### 4.4 ROA et plan de maintenance

Une ROA trop restrictive peut invalider des annonces légitimes ; une ROA trop large autorise des annonces qui ne sont pas nécessaires. Documentez le titulaire du préfixe, les ASN autorisés, les longueurs prévues et les dates de changement. Avant une migration d’ASN, définissez la séquence de transition et assurez-vous que les autorisations nécessaires existent avant de déplacer l’annonce. Maintenez un registre des préfixes et des propriétaires.

Les outils de vérification ne remplacent pas une validation humaine pour les opérations importantes. Une vérification doit confirmer le préfixe exact, sa longueur, l’ASN d’origine et le résultat de validation depuis plusieurs points pertinents si l’opération dépend de plusieurs caches ou réseaux. Les données de routage peuvent changer dans le temps ; il faut conserver l’heure des observations.

## 5. Protéger les sessions et le plan de contrôle

### 5.1 Filtrer l’accès au routeur

Le routeur doit recevoir uniquement les protocoles de contrôle attendus sur les interfaces et adresses appropriées. Les règles d’accès doivent tenir compte du type de voisin, des adresses source et destination, du protocole, du port si pertinent, et des exigences du plan d’administration. Ne pas exposer sans justification les services de gestion à Internet. Séparer l’administration des échanges de routage réduit l’impact de la compromission d’un poste bureautique.

Le filtrage du plan de contrôle doit autoriser les paquets nécessaires aux adjacences prévues et rejeter ou limiter les autres. Une ACL trop permissive à destination du routeur facilite les tentatives d’épuisement de ressources ; une ACL trop stricte casse les adjacences légitimes. L’inventaire des protocoles autorisés doit être maintenu comme un contrôle de sécurité, non comme un réglage oublié.

~~~text
Trafic entrant
    |
    v
[Filtre au plus près du routeur]
    |
    +-- voisin attendu / protocole attendu --> contrôle de session
    |
    +-- trafic non autorisé ----------------> rejet ou limitation
    |
    v
CPU du routeur
    |
    +--> BGP / OSPF / IS-IS
    +--> supervision et administration autorisées
~~~

### 5.2 Authentification des sessions BGP

Les mécanismes de protection de session peuvent réduire les risques liés à l’injection de paquets et à l’interruption d’une session. TCP-AO a été conçu comme successeur de TCP MD5 ; l’implémentation et la compatibilité doivent être vérifiées sur les deux extrémités. Certains environnements utilisent encore des mécanismes plus anciens pour des raisons de compatibilité. Les clés ne doivent pas être partagées via des canaux non sûrs, inscrites en clair dans les tickets ou réutilisées sans politique.

Une authentification de session ne remplace jamais le filtrage des routes. Un voisin authentifié peut être mal configuré ou compromis. La sécurité de BGP repose sur plusieurs couches : identification du voisin, protection des paquets, contrôle des annonces, surveillance des changements et procédure de réponse.

### 5.3 GTSM / TTL Security

Le Generalized TTL Security Mechanism (GTSM) utilise les valeurs TTL pour compliquer certaines attaques distantes contre le plan de contrôle, notamment quand les voisins doivent être directement adjacents. Il est particulièrement pertinent pour des sessions dont la topologie et le nombre de sauts attendus sont bien définis. Il n’est pas universel : les sessions multihop et certains designs nécessitent une configuration adaptée ou un mécanisme différent.

GTSM n’est pas une authentification cryptographique. Un paquet provenant d’un voisin proche peut toujours nécessiter des vérifications supplémentaires. Il faut traiter GTSM, les ACL de contrôle et l’authentification comme des contrôles complémentaires. Avant activation, examiner la topologie réelle et prévoir un test qui n’interrompt pas le peering de production.

### 5.4 Protection du processeur

Les mécanismes de control-plane policing ou de protection équivalents limitent le trafic qui atteint le processeur. Ils doivent préserver les paquets légitimes de routage, de supervision et d’administration tout en limitant les flux inattendus. Les seuils doivent être basés sur les profils de trafic normaux et l’expérience de la plateforme. Une règle générique trop agressive peut faire tomber les protocoles qu’elle devait protéger.

La mesure comprend le taux de paquets, les rejets par classe, les changements de CPU et les états d’adjacence. En cas d’incident, vérifier si la perte de voisin vient d’un problème réseau, d’une protection mal dimensionnée, d’une surcharge du processeur ou d’une authentification incohérente. L’horodatage précis des événements permet de relier les symptômes.

### 5.5 Gestion sécurisée des équipements

L’administration doit reposer sur des identités individuelles ou un système de gestion centralisé, un accès chiffré, l’authentification multifacteur quand elle est disponible et des permissions minimales. Les sauvegardes des configurations doivent être protégées et testées. Les journaux de connexion, les changements de configuration et les commandes sensibles doivent être centralisés lorsque c’est possible.

Les secrets de voisinage ont besoin d’un propriétaire, d’une procédure de rotation et d’un stockage approprié. Une clé copiée sur plusieurs systèmes sans inventaire finit par être difficile à renouveler. Privilégiez des mécanismes et systèmes de gestion qui permettent de déployer les secrets sans les exposer dans les journaux. Les accès d’urgence doivent être documentés, contrôlés et vérifiés après usage.

## 6. Sécurité d'OSPF et d'IS-IS

### 6.1 Menaces du routage interne

OSPF et IS-IS diffusent des informations utilisées à l’intérieur d’un domaine de routage. Un voisin non autorisé ou un équipement compromis peut injecter des informations, provoquer des calculs de topologie, modifier les coûts, créer des instabilités ou consommer des ressources. La menace existe même si le protocole n’est pas directement accessible depuis Internet : un poste connecté à un segment mal protégé peut constituer un point d’entrée.

L’objectif n’est pas d’activer une option isolée, mais de limiter qui peut participer, où les adjacences peuvent exister, quelles informations sont distribuées et comment le domaine est surveillé. Les interfaces qui ne doivent pas devenir voisines sont rendues passives quand la plateforme le permet, les réseaux utilisateurs sont séparés des liens de routage, et les politiques de redistribution sont revues avec prudence.

### 6.2 OSPF : authentification et conception

Les variantes et versions d’OSPF ne possèdent pas toutes exactement les mêmes options. OSPFv2 dispose de mécanismes d’authentification cryptographique spécifiés dans des RFC dédiées, avec des mises à jour et des considérations de compatibilité. OSPFv3 dispose de mécanismes propres et peut également s’appuyer sur des protections externes selon le design. Le choix doit suivre les capacités documentées du matériel et du logiciel, ainsi que les exigences de l’organisation.

Le secret ou les clés d’authentification doivent être cohérents entre voisins, gérés comme des secrets et renouvelés selon une fenêtre organisée. Une divergence de clé ou d’algorithme empêche l’échange correct. On prévoit donc une procédure d’activation, un contrôle de l’état des adjacences et un retour arrière avec accès console ou chemin de gestion indépendant. Ne changez pas la clé sur tous les routeurs sans séquencer et vérifier.

~~~text
                 Backbone OSPF
             +-------------------+
             |       Area 0      |
             | R1 ----- R2 ------ R3
             +-------------------+
                 |           |
             Area 10       Area 20
              R4             R5
               |              |
           réseau users    serveurs

Principes :
- adjacences uniquement sur les liens prévus
- interfaces utilisateurs passives
- authentification cohérente
- redistribution restreinte et documentée
~~~

### 6.3 Aires, frontières et redistribution

La séparation en aires améliore l’évolutivité, mais n’est pas automatiquement une frontière de sécurité. Un routeur de frontière d’aire peut influencer la propagation des routes ; un routeur de redistribution peut convertir des routes entre OSPF, BGP, routes statiques et autres protocoles. Chaque redistribution doit préciser les préfixes permis, les métriques, les tags et le sens. Une redistribution large sans filtrage peut créer des boucles ou diffuser des routes qu’on voulait garder locales.

Les routes par défaut demandent une attention particulière. Elles étendent souvent fortement l’impact d’une erreur, car de nombreuses destinations peuvent être envoyées vers le même prochain saut. Toute annonce de défaut doit être liée à une condition explicite, une politique et une preuve de disponibilité. Les routes statiques temporaires doivent être inventoriées, car elles peuvent masquer une panne ou créer un chemin inattendu.

### 6.4 IS-IS

IS-IS est fréquemment utilisé dans les réseaux de fournisseurs et grandes infrastructures. Il diffuse des informations d’état de liens et construit la topologie via la base de données d’état de liens. Sa conception et les mécanismes de protection doivent être adaptés à la plateforme, aux niveaux du domaine et aux adjacences réelles. Les clés et algorithmes supportés doivent être vérifiés, et le comportement de l’équipement observé après changement.

Les bonnes pratiques communes à IS-IS et OSPF sont l’isolation des segments de routage, l’authentification quand elle est disponible et exigée, le filtrage des interfaces inutiles, la protection CPU, la journalisation, la revue des modifications et la limitation de la redistribution. Une topologie isolée réduit l’exposition, mais ne supprime pas le risque d’un équipement interne compromis.

### 6.5 Réseaux multi-constructeurs

Dans un réseau constitué de plusieurs constructeurs, les noms de commandes et les détails de compatibilité varient. Les standards donnent le cadre, mais la configuration doit être testée avec les versions exactes. Vérifiez notamment les algorithmes d’authentification disponibles, la rotation de clés, la prise en charge des options, la commande de vérification et les messages de journalisation.

Un changement doit être testé avec au moins deux voisins réels ou représentatifs, la perte d’un voisin, le retour du voisin et une clé incorrecte en laboratoire. L’objectif est de constater que le contrôle fonctionne et de connaître le message qui permet de diagnostiquer un défaut. Sans cette connaissance, l’activation peut se transformer en panne difficile à isoler.

## 7. Validation, surveillance et preuve

### 7.1 Construire une ligne de base

Avant de modifier le réseau, collecter les routes reçues et annoncées, les états des sessions, le nombre de préfixes, les distributions RPKI, les journaux et les métriques CPU/mémoire. Établir la période normale d’observation, les fenêtres de maintenance et les événements métier qui peuvent influencer le routage. Sans référence, une alerte est difficile à interpréter.

Les métriques doivent répondre à une question concrète : qu’est-ce qui a changé, quand, pour quel voisin, quel préfixe et avec quelle conséquence ? Une capture complète de sortie de commande peut être utile, mais un indicateur stable simplifie l’exploitation quotidienne. Conservez la source, l’horodatage, la version du logiciel et la méthode de collecte pour que les résultats soient reproductibles.

~~~text
Voisin   Etat   Prefixes reçus   Invalid RPKI   Dernier changement
AS64510  Up     valeur de base   valeur suivie  heure UTC
AS64521  Up     plage attendue   0 attendu*     heure UTC
AS64530  Up     plage attendue   valeur suivie  heure UTC

* Une valeur attendue est un objectif défini par la politique,
  pas une garantie mathématique ni une preuve universelle.
~~~

### 7.2 Alertes utiles

Les alertes prioritaires concernent les changements de préfixe non planifiés, le passage d’une session à l’état Down, une hausse rapide du nombre de routes, des annonces Invalid, un cache RPKI inaccessible, des changements de rôle ou de politique et une saturation CPU. Il faut éviter de déclencher un flot d’alertes pour un phénomène stable. Les seuils et fenêtres doivent être documentés ; une alerte critique doit joindre suffisamment de contexte pour accélérer le diagnostic.

Ne déclenchez pas automatiquement un blocage à partir d’un signal unique non confirmé lorsque le risque de faux positif est important. Des actions automatiques peuvent être utiles, mais elles exigent une analyse de risque, des garde-fous, des limites, un journal d’action et une possibilité de désactivation. Les mécanismes qui modifient le routage ont un impact potentiel important : ils doivent être traités comme du code de production.

### 7.3 Journalisation et corrélation temporelle

Centralisez les journaux de session, de politique, de validation RPKI, de configuration et de système. Synchronisez les horloges. Lorsqu’une route disparaît, l’équipe doit pouvoir relier le changement de route aux événements sur le voisin, la politique, le cache ou l’équipement. Les logs locaux seuls peuvent disparaître si l’équipement redémarre ou si une personne les efface.

Une preuve exploitable contient les données originales pertinentes, l’heure de collecte, la commande ou la source, l’identité de la personne ou de l’automatisation, le changement proposé et le résultat. Les secrets doivent être masqués. La conservation suit les règles de sécurité, de confidentialité et de conformité de l’organisation. La documentation de la preuve ne doit pas exposer publiquement les topologies détaillées ou les clés d’administration.

### 7.4 Tests automatisés de politique

La politique de routage peut être traitée comme une configuration versionnée : sources de préfixes, ASN, rôles, communautés et exceptions explicitement approuvées. Une validation automatique peut détecter une règle d’export plus large que prévu, une liste vide, un préfixe non documenté, une valeur incohérente ou une variation de seuil. Les tests doivent valider l’intention et la configuration générée, puis l’observation réelle après déploiement.

~~~text
Changement proposé
       |
       v
Validation du format et des sources
       |
       v
Tests de politique : import / export / exception
       |
       v
Revue à deux personnes
       |
       v
Déploiement limité
       |
       v
Comparaison état attendu / état réel
       |
       +--> conforme : généraliser
       |
       +--> anomalie : rollback et enquête
~~~

## 8. Exemple de politique défensive en laboratoire

Les syntaxes varient suivant le système réseau. Les extraits ci-dessous expriment l’intention et ne sont pas des commandes universelles. Il faut consulter la documentation du constructeur et les versions installées avant utilisation. Le laboratoire doit être isolé et utiliser des adresses réservées à la documentation ou des plages privées.

~~~text
Politique CLIENT-AS64521
  IMPORT:
    accepter 198.51.100.0/24 si l'ASN distant est 64521
    rejeter les autres préfixes
    alerter si le nombre dépasse le seuil défini
  EXPORT:
    annoncer uniquement les préfixes du réseau local
    rejeter les routes apprises d'un autre client
    appliquer les communautés prévues par l'accord
  SESSION:
    voisin attendu = adresse inventoriée
    authentification et ACL selon capacités
    journaliser changement d'état
~~~

L’exemple comporte volontairement une liste courte. Pour un fournisseur de transit, l’importation d’une table complète ne peut pas utiliser uniquement cette liste. Elle doit s’appuyer sur une politique spécifique de fournisseur, des filtres spéciaux et de longueur de préfixe, les règles de l’AS_PATH, RPKI et la capacité de la plateforme. Évitez de copier le bloc client sur tous les voisins.

### 8.1 Vérifications à effectuer

Avant d’activer une politique, répondre aux questions suivantes : quelles routes doivent être acceptées ? quelles routes doivent être annoncées ? quelle est la source de ces autorisations ? que se passe-t-il lorsque les données de validation sont indisponibles ? quels indicateurs permettent de voir une erreur ? qui peut approuver une exception ? comment revenir à l’état précédent ?

Après activation, comparer les tables avant et après, contrôler les routes annoncées au voisin, observer les alertes, vérifier la connectivité des préfixes attendus et confirmer que les routes interdites sont absentes. Une session établie ne constitue pas un test suffisant. On vérifie les effets dans les deux sens et pour chaque relation critique.

## 9. Procédure de réponse à une anomalie de routage

Une anomalie peut commencer par une alerte, une perte de service, une hausse de latence ou la découverte d’une nouvelle route. Ne pas appliquer immédiatement une modification large. D’abord établir l’étendue de l’incident, conserver les preuves et identifier la route, le voisin et l’instant de changement. Les commandes de lecture seule et l’export d’état doivent précéder les modifications si la situation le permet.

~~~text
1. Détecter : alerte, client, supervision ou opérateur
2. Qualifier : préfixes, ASN, voisins, impact, heure UTC
3. Préserver : état BGP/RIB/FIB, logs, changements récents
4. Contenir : filtre ciblé ou arrêt coordonné si nécessaire
5. Valider : RPKI, AS_PATH, sources d'autorité, partenaires
6. Rétablir : correction minimale, observation et tests
7. Apprendre : cause, preuve, contrôle manquant, propriétaire
~~~

Le confinement doit être proportionné. Rejeter une seule route invalidée peut être approprié si l’analyse est claire ; arrêter une session entière peut retirer de nombreux préfixes légitimes et aggraver l’incident. Toute action à large impact doit suivre les règles d’escalade convenues. Si le voisin est un fournisseur ou un pair externe, communiquer les informations utiles sans partager de secrets internes.

Après le rétablissement, documenter la cause racine, les routes touchées, la durée, les actions, les approbations, les contrôles qui ont détecté l’incident et ceux qui ont échoué. Créer ensuite une action corrective assignée à un propriétaire, avec une date cible et une preuve attendue. Une simple mention « mauvaise configuration » ne permet pas de prévenir la répétition : il faut expliquer pourquoi la configuration n’a pas été testée ou pourquoi le contrôle n’a pas détecté l’écart.

## 10. Travaux pratiques guidés

Les TPs sont conçus pour un environnement local ou simulé. Utilisez des routeurs virtuels, des namespaces ou un simulateur autorisé. Ne créez pas d’annonces BGP sur un réseau public, ne testez pas de fuite sur des systèmes tiers et n’expérimentez pas sur une session de production. Avant chaque TP, sauvegarder l’état initial et définir comment revenir à cet état.

### TP 1 — Établir une politique client stricte

**Contexte :** un routeur R1 dans un laboratoire échange des routes avec un routeur client R2. Le client n’est autorisé à annoncer que 198.51.100.0/24. Votre objectif est de garantir que seul ce préfixe est accepté et que R1 n’exporte que les routes contractuellement prévues au client.

**Étapes :**
1. Inventorier l’adresse de voisin, l’ASN fictif, les routes attendues et les routes de test.
2. Créer une politique d’import en refusant tout par défaut.
3. Ajouter une règle précise pour le préfixe autorisé.
4. Créer une politique d’export distincte et limiter les annonces au client.
5. Tester une annonce correcte, une annonce plus spécifique et un préfixe extérieur.
6. Vérifier la route acceptée dans la RIB puis dans la FIB.
7. Vérifier ce que R1 annonce réellement à R2.
8. Sauvegarder les sorties et expliquer les décisions.

**Résultat attendu :** la route autorisée est acceptée si les autres conditions sont remplies ; le préfixe non prévu et la route plus spécifique sont rejetés sauf autorisation explicite. Les routes apprises d’autres clients ne deviennent pas des routes de transit par erreur.

**Correction commentée :** la politique ne doit pas reposer uniquement sur l’ASN du voisin. L’ASN identifie la relation BGP, mais ne prouve pas que chaque préfixe annoncé appartient à ce client. La liste d’import limite les destinations originaire du client, et la politique d’export limite la propagation. Il faut vérifier les deux côtés. Pour réussir, le rapport contient la configuration, la source d’autorité de la liste, les résultats des trois tests et une explication des routes présentes ou absentes.

### TP 2 — Lire et traiter les états RPKI

**Contexte :** un laboratoire reçoit trois annonces fictives : l’une correspond à la ROA, l’une indique un ASN d’origine non autorisé, et l’une n’a pas de ROA correspondante. Les résultats sont fournis par un cache simulé ou par un environnement de test.

**Étapes :**
1. Consigner le préfixe, la longueur, l’ASN d’origine et le résultat RPKI.
2. Identifier quelle propriété provoque l’état Invalid dans le deuxième cas.
3. Ne pas classer automatiquement NotFound comme Invalid.
4. Comparer la décision selon la politique actuelle et une politique plus stricte.
5. Simuler une indisponibilité du cache et observer les alertes.
6. Proposer un plan de migration vers le rejet des Invalid avec une phase d’observation.
7. Décrire la procédure de correction d’une ROA dont votre organisation est propriétaire.

**Correction commentée :** Valid signifie qu’une autorisation correspondante couvre le préfixe et l’ASN originaire. Invalid signifie qu’une autorisation existante contredit l’annonce, y compris lorsque la longueur annoncée dépasse le maxLength permis. NotFound signifie qu’aucune autorisation correspondante n’est disponible. La réponse appropriée à NotFound dépend de la politique, mais l’absence de ROA ne constitue pas une preuve d’attaque. Il faut préserver les filtres du voisin, mesurer les états et distinguer une invalidité des données d’un cache indisponible.

**Livrable :** un tableau des trois annonces avec état, explication, décision prévue, risque de faux positif et action d’enquête.

### TP 3 — Détecter une fuite de routes

**Contexte :** AS64521 reçoit une route d’un fournisseur AS64510. Une erreur de politique la réannonce au pair AS64530. Le réseau est simulé, et les routes représentent des données de test uniquement.

**Étapes :**
1. Dessiner les relations fournisseur-client-pair.
2. Déterminer quels préfixes sont originés localement et lesquels ont été appris.
3. Écrire les règles d’export attendues pour chaque voisin.
4. Examiner la prise en charge de BGP Roles et OTC par les implémentations du lab.
5. Dans le cas compatible, configurer les rôles conformément à la relation de chaque session.
6. Introduire volontairement une erreur uniquement dans le lab et constater le signal de validation.
7. Corriger la politique et vérifier que la route ne sort plus vers le mauvais voisin.
8. Documenter les limites et les cas où les mécanismes ne peuvent être appliqués.

**Correction commentée :** le problème n’est pas nécessairement que le préfixe soit illégitime ; il est que la route apprise du fournisseur soit exportée vers un pair alors que la politique interdit ce transit. La solution principale est une politique d’export conforme à la relation et testée. BGP Roles/OTC peuvent aider à prévenir ou détecter certains écarts lorsque les deux extrémités et leur implémentation sont compatibles. Ils ne dispensent pas de filtres explicites.

**Livrable :** diagramme du chemin attendu et du chemin erroné, matrice d’export, sorties avant/après et plan de déploiement progressif.

### TP 4 — Renforcer un domaine OSPF

**Contexte :** une topologie OSPFv2 fictive contient un backbone, deux aires et un réseau utilisateur. Un routeur ne doit pas établir d’adjacence sur le segment utilisateur. Le laboratoire supporte l’authentification prévue par la version de logiciel retenue.

**Étapes :**
1. Recenser les interfaces et adjacences prévues.
2. Marquer passives les interfaces qui ne doivent pas former de voisinage, si l’implémentation le permet.
3. Définir la méthode d’authentification et la procédure de distribution des clés.
4. Activer la protection de façon séquencée entre deux voisins de test.
5. Vérifier les adjacences, les journaux et la table de routage.
6. Tester une divergence de clé dans le lab, constater l’effet puis restaurer la clé attendue.
7. Contrôler les politiques de redistribution et l’annonce de route par défaut.
8. Documenter les risques de déploiement et le retour arrière.

**Correction commentée :** l’interface utilisateur ne doit pas participer au voisinage si ce n’est pas requis. L’authentification doit être cohérente aux deux extrémités et conforme à la capacité réelle du produit. Une clé incorrecte doit provoquer un échec identifiable. Une procédure sûre conserve un chemin de gestion alternatif, sauvegarde les configurations et vérifie chaque adjacence après le changement. L’authentification ne remplace ni la segmentation ni la protection du processeur.

**Livrable :** matrice interface/voisinage, preuve d’état avant/après, méthode de rotation des clés et procédure de rollback.

## 11. Exercices corrigés

### Exercice 1 — Filtrage client

Un client est autorisé à annoncer 203.0.113.0/24. Il annonce aussi 203.0.113.0/25. Que doit faire le filtre ?

**Correction :** rejeter le /25 en l’absence d’autorisation explicite. Une route plus spécifique peut attirer du trafic différent, et le fait qu’elle soit contenue dans un bloc autorisé ne signifie pas qu’elle est prévue.

### Exercice 2 — Route d’un voisin connu

Une annonce vient du bon ASN, mais son préfixe ne figure pas dans l’accord. Est-elle sûre ?

**Correction :** non. L’identité du voisin et l’autorisation de route sont deux contrôles différents. La politique d’import doit refuser le préfixe non approuvé et ouvrir une investigation.

### Exercice 3 — RPKI NotFound

Le validateur renvoie NotFound. Faut-il le rejeter de façon automatique dans tous les cas ?

**Correction :** non, pas comme règle universelle. NotFound indique l’absence de ROA correspondante dans les données consultées. Une politique peut choisir une réaction stricte, mais elle doit mesurer l’impact et maintenir des filtres classiques.

### Exercice 4 — RPKI Invalid

Une route est Invalid parce que l’ASN d’origine ne correspond pas à la ROA. Quelles sont les premières vérifications ?

**Correction :** confirmer le préfixe, la longueur, l’ASN d’origine, la ROA, l’heure, la source des données et l’accord de routage. Vérifier si l’annonce est malveillante, une erreur de ROA ou une migration coordonnée.

### Exercice 5 — Max-prefix

Le client annonce soudainement beaucoup plus de routes que son volume habituel. Pourquoi ne pas augmenter immédiatement le seuil ?

**Correction :** l’augmentation peut laisser une anomalie consommer de la mémoire ou propager des routes non prévues. Il faut confirmer les annonces attendues avec le client, observer le seuil et appliquer la procédure d’escalade.

### Exercice 6 — Fuite ou détournement

Un AS réannonce à son pair une route apprise d’un fournisseur. Quel est le concept principal ?

**Correction :** une fuite de routes, car le problème est la propagation contraire à la relation de peering. Cela peut également produire un effet de détournement ou affecter la sélection du chemin.

### Exercice 7 — Rôle BGP mal configuré

Un côté indique Provider et l’autre Peer. Que faire ?

**Correction :** suspendre le déploiement et réconcilier les rôles avec l’accord réel. Les rôles doivent correspondre entre les deux extrémités. Ne pas forcer une session en production sans comprendre les conséquences de politique.

### Exercice 8 — Session authentifiée

Un voisin BGP est authentifié mais annonce un préfixe inconnu. Est-ce acceptable ?

**Correction :** pas sans vérification et politique d’import adaptée. L’authentification réduit certains risques sur la session, mais ne prouve pas l’autorisation de chaque annonce.

### Exercice 9 — GTSM

Peut-on considérer GTSM comme une authentification cryptographique ?

**Correction :** non. GTSM utilise le TTL pour limiter certaines attaques distantes contre un voisinage attendu. Il complète l’ACL et les mécanismes d’authentification sans les remplacer.

### Exercice 10 — Plan de contrôle

Pourquoi limiter les paquets envoyés au processeur du routeur ?

**Correction :** le CPU est une ressource plus limitée que le plan de transfert matériel. Un trafic inattendu peut l’épuiser, ralentir les protocoles de routage et provoquer une indisponibilité.

### Exercice 11 — Interface OSPF passive

Pourquoi rendre passive une interface connectée à des postes utilisateurs ?

**Correction :** parce qu’aucun voisinage ne doit y être établi si le besoin n’existe pas. Cela réduit l’exposition accidentelle, mais il faut conserver l’annonce des réseaux nécessaires selon le comportement de la plateforme.

### Exercice 12 — Redistribution

Une redistribution sans filtre exporte des routes statiques et BGP dans OSPF. Quel est le risque ?

**Correction :** propagation excessive, boucle de routage, route par défaut inattendue ou perte de contrôle sur la provenance. Définir une liste autorisée, des tags et des conditions d’annonce.

### Exercice 13 — Clé OSPF

Après rotation, un voisin reste Down. Quel contrôle vient en premier ?

**Correction :** comparer la clé, l’algorithme, l’identifiant de clé, les fenêtres de validité éventuelles et la configuration des deux extrémités. Lire les journaux et vérifier la connectivité sans désactiver aveuglément les contrôles.

### Exercice 14 — Cache RPKI indisponible

Les états RPKI ne se mettent plus à jour. Quelle réaction est attendue ?

**Correction :** alerter, diagnostiquer la connectivité RTR et appliquer la politique de continuité décidée à l’avance. Il ne faut ni considérer tous les préfixes comme valides, ni purger toute la table sans stratégie.

### Exercice 15 — Filtre d’export

Pourquoi faut-il vérifier les routes annoncées après une politique d’import stricte ?

**Correction :** parce qu’une route importée peut être ensuite propagée à un voisin inattendu selon les règles d’export. L’import ne contrôle que les routes reçues ; l’export contrôle la diffusion.

### Exercice 16 — Journaux

Quelle donnée rend une enquête sur un changement de route plus fiable ?

**Correction :** un horodatage synchronisé, le voisin, le préfixe, les attributs utiles, le changement de configuration, la source de l’événement et la décision prise. Les secrets ne doivent pas figurer dans le rapport.

### Exercice 17 — Notion de route valide

Une route apparaît dans BGP, mais pas dans la FIB. Pourquoi ?

**Correction :** elle peut ne pas être sélectionnée, être rejetée par une règle de meilleure route, être supplantée par une route de préférence supérieure ou ne pas être installée pour une autre raison. Il faut vérifier BGP, la RIB et la FIB.

### Exercice 18 — Exceptions

Un service métier exige une route normalement bloquée. Comment la traiter ?

**Correction :** créer une exception explicite, limitée, avec propriétaire, justification, durée, revue et test. Une exception ne doit pas devenir une règle générique non documentée.

### Exercice 19 — Action automatique

Une alerte RPKI doit automatiquement supprimer une route. Quels garde-fous faut-il définir ?

**Correction :** fiabilité des données, seuils, périmètre, journalisation, mode observation, critères d’activation, contrôle humain pour les cas à fort impact, retour arrière et procédure de secours. Évaluer le coût du faux positif.

### Exercice 20 — Incident de routage

Quel est le premier objectif lors d’une anomalie grave ?

**Correction :** qualifier l’étendue et préserver l’information avant toute modification large, lorsque les contraintes opérationnelles le permettent. Le confinement vient ensuite avec une action ciblée et une communication coordonnée.

## 12. Défi final — Sécuriser un mini-réseau opérateur

**Scénario :** votre équipe administre AS64500. Il possède un préfixe public documenté dans l’exercice, un voisin client AS64521, un fournisseur AS64510 et un pair AS64530. Il exploite également un domaine OSPF interne. Le client annonce un préfixe non prévu, des annonces RPKI Invalid sont observées chez un fournisseur, et une route fournisseur est réannoncée vers le pair à la suite d’une modification récente. Enfin, une interface utilisateur envoie des paquets de contrôle OSPF qui ne devraient pas participer à une adjacence.

Les AS et les préfixes sont fictifs. Tout le défi se déroule dans un laboratoire fermé.

### Livrables obligatoires

1. **Cartographie :** dessiner les relations, les préfixes attendus, les interfaces OSPF et les frontières de confiance.
2. **Matrice de politique :** définir l’import et l’export de chaque voisin, les filtres et les exceptions.
3. **RPKI :** classifier les états, expliquer chaque invalidité et décrire la coordination avec le détenteur des ROA.
4. **Anti-fuite :** corriger l’export vers le pair, vérifier le support des rôles BGP et d’OTC, et documenter les limites.
5. **Protection du contrôle :** proposer les protections de session compatibles, les filtres d’accès, GTSM si pertinent et la protection CPU.
6. **OSPF :** empêcher l’adjacence non prévue, protéger les voisins de routage et revoir la redistribution.
7. **Observabilité :** définir les alertes, les preuves, l’horodatage, les métriques et l’escalade.
8. **Déploiement :** proposer un changement en étapes, un plan de validation et un rollback.
9. **Incident :** produire un résumé de l’impact, de la cause, du confinement, du rétablissement et des actions préventives.

### Correction de référence

La réponse doit démarrer par une liste de préfixes et de rôles approuvés, pas par une série de commandes copiées. Sur le client, refuser toutes les routes sauf les préfixes autorisés. Sur le fournisseur, appliquer la politique correspondant à la réception d’une table de transit, avec les protections de préfixe et d’AS_PATH pertinentes. Sur le pair, n’exporter que les routes prévues et empêcher la réannonce de routes fournisseur si le contrat et la politique l’interdisent. Les politiques d’import et d’export sont vérifiées indépendamment.

Pour RPKI, distinguer Valid, Invalid et NotFound. Ne pas confondre une ROA erronée avec une attaque confirmée. Vérifier les données, ouvrir une coordination avec le propriétaire autorisé, corriger uniquement les ressources que l’organisation contrôle et mesurer l’effet avant d’imposer un rejet à grande échelle. Contrôler la santé du cache et la fraîcheur des états.

Pour la fuite, expliquer que l’AS_PATH peut être plausible alors que la politique de propagation est interdite. Corriger la politique d’export, tester la table annoncée et considérer BGP Roles/OTC si les deux extrémités le prennent en charge. Une simple session authentifiée ne suffit pas. Pour le plan de contrôle, limiter les protocoles aux voisins attendus, appliquer l’authentification compatible et les protections de proximité pertinentes, puis protéger le CPU sans supprimer les paquets de routage légitimes.

Pour OSPF, rendre passive ou filtrer l’interface utilisateur selon la plateforme, vérifier les adjacences prévues, les clés et les routes redistribuées. Les changements sont faits séquentiellement avec sauvegarde, fenêtre de changement, tests avant/après et chemin de gestion de secours. La correction finale doit être prouvée par l’état des voisins, les tables, les annonces reçues par chaque voisin simulé et les journaux.

### Barème sur 100 points

- Cartographie et inventaire des préfixes : 10 points.
- Politiques import/export exactes et justifiées : 20 points.
- RPKI et plan de traitement des invalidités : 15 points.
- Prévention des fuites et rôle BGP/OTC : 15 points.
- Protection des sessions et du plan de contrôle : 10 points.
- Sécurisation OSPF et redistribution : 10 points.
- Supervision, journalisation et conservation des preuves : 10 points.
- Plan de changement, tests et retour arrière : 10 points.

Une solution qui se contente d’activer RPKI sans filtres, d’ajouter une clé sans contrôler les annonces ou de supprimer une session sans évaluer l’impact ne peut pas obtenir la totalité des points. L’objectif est une défense en profondeur qui reste exploitable et réversible.

## 13. Checklist de mise en production

Avant un changement de routage, confirmer chacun des points suivants :

- Les voisins, ASN, relations et préfixes autorisés disposent d’un propriétaire et d’une source de vérité.
- Les politiques d’import et d’export sont explicites, testées et distinctes.
- Les préfixes spéciaux, les longueurs attendues, les chemins AS et les communautés sont traités selon une politique documentée.
- Les limites de préfixes sont adaptées au volume réellement attendu et une alerte se déclenche avant le seuil critique.
- Le fonctionnement et la fraîcheur de RPKI sont supervisés ; les Invalid ont une procédure d’enquête.
- Les mécanismes de protection de session sont compatibles et leurs secrets ont un cycle de vie.
- Les interfaces de routage sont limitées aux liens nécessaires ; les interfaces non routantes ne créent pas de voisinage involontaire.
- Le processeur est protégé contre les paquets inattendus sans bloquer les protocoles légitimes.
- Les journaux sont synchronisés et centralisés lorsque c’est possible.
- Les tests contrôlent les routes reçues, annoncées, installées et le trafic utile.
- Le déploiement se fait par étapes, avec approbation, surveillance et retour arrière.
- Les exceptions ont un propriétaire, une échéance et une revue.
- Le rapport post-changement inclut les preuves et les résultats, y compris les échecs.

## 14. Glossaire

**AS (Autonomous System)** : ensemble de réseaux exploité sous une politique de routage commune et identifié par un ASN.

**ASN** : numéro d’un système autonome utilisé notamment par BGP.

**AS_PATH** : attribut BGP qui décrit la séquence de systèmes autonomes associée à une route dans les annonces BGP classiques.

**BGP** : protocole de routage inter-domaine fondé sur des politiques, utilisé pour l’échange de routes entre AS.

**eBGP / iBGP** : session BGP entre AS distincts / session BGP à l’intérieur du même AS.

**FIB** : table utilisée par le plan de transfert pour décider comment transmettre un paquet.

**GTSM** : mécanisme utilisant le TTL attendu pour réduire certaines attaques distantes contre le plan de contrôle.

**Import / export** : règles qui contrôlent respectivement les routes reçues d’un voisin et celles annoncées à ce voisin.

**Invalid RPKI** : état d’une annonce contredisant une ROA applicable, notamment sur l’ASN d’origine ou la longueur du préfixe.

**NotFound** : état sans ROA correspondante dans les informations validées consultées.

**OTC** : attribut BGP Only-To-Customer, conçu pour contribuer à la prévention et à la détection de fuites.

**OSPF** : protocole de routage interne à état de liens.

**Plan de contrôle** : composants qui échangent et calculent les décisions de routage.

**Plan de transfert** : composants qui utilisent la FIB pour faire circuler les paquets.

**Préfixe** : ensemble d’adresses IP exprimé par une adresse réseau et une longueur, par exemple /24.

**RIB** : base des informations de routage et des routes candidates.

**ROA** : autorisation signée liant un préfixe, un ASN d’origine et une longueur maximale.

**RPKI** : infrastructure de clés et de ressources utilisée, entre autres, pour vérifier les autorisations d’origine des routes.

**Route leak / fuite de routes** : propagation d’une route au-delà de la relation ou de la politique prévue.

**Route hijack / détournement de préfixe** : annonce ou chemin qui attire le trafic d’un préfixe sans autorisation ou contrairement à l’intention du détenteur.

**TCP-AO** : option d’authentification TCP définie comme successeur du mécanisme TCP MD5.

**Validation d’origine** : contrôle qui compare l’ASN d’origine d’une annonce BGP avec les autorisations RPKI.

## 15. Références officielles pour approfondir

- RFC 7454 — BGP Operations and Security, bonnes pratiques opérationnelles BGP : https://www.rfc-editor.org/rfc/rfc7454.html
- RFC 8212 — Default External BGP (EBGP) Route Propagation Behavior without Policies : https://www.rfc-editor.org/rfc/rfc8212.html
- RFC 6811 — BGP Prefix Origin Validation : https://www.rfc-editor.org/rfc/rfc6811.html
- RFC 9234 — Route Leak Prevention and Detection Using Roles in UPDATE and OPEN Messages : https://www.rfc-editor.org/rfc/rfc9234.html
- RFC 7908 — Problem Definition and Classification of BGP Route Leaks : https://www.rfc-editor.org/rfc/rfc7908.html
- RFC 5925 — The TCP Authentication Option : https://www.rfc-editor.org/rfc/rfc5925.html
- RFC 5082 — The Generalized TTL Security Mechanism : https://www.rfc-editor.org/rfc/rfc5082.html
- RFC 6192 — Protecting the Router Control Plane : https://www.rfc-editor.org/rfc/rfc6192.html
- RFC 5709 — OSPFv2 HMAC-SHA Cryptographic Authentication : https://www.rfc-editor.org/rfc/rfc5709.html
- Documentation FRRouting BGP et RPKI, pour comparer les concepts aux options d’un logiciel précis : https://docs.frrouting.org/en/latest/bgp.html

Les RFC décrivent des protocoles ou des bonnes pratiques ; elles ne garantissent pas que toutes les fonctions soient présentes ou activées sur un équipement donné. Vérifiez toujours la documentation du fabricant, la version installée et les contraintes de votre topologie. Les exigences juridiques et contractuelles doivent être confirmées avec les équipes compétentes.

## Schéma complémentaire A — Cycle de vie d'une annonce

~~~text
Préfixe détenu
    |
    v
ROA / registre / politique interne
    |
    v
Annonce BGP émise par l'AS autorisé
    |
    v
Contrôles du voisin récepteur
    |
    +--> filtre préfixe et relation
    +--> AS_PATH et communautés
    +--> validation d'origine RPKI
    |
    v
Décision locale documentée
    |
    v
Surveillance des routes reçues et exportées
~~~

Ce cycle rappelle qu'une autorisation doit être cohérente à la source, dans l'annonce et dans les politiques du récepteur. Si l'un de ces éléments change, les autres doivent être revérifiés. Une route acceptée aujourd'hui peut devenir anormale après un changement de ROA, d'ASN, de contrat ou de politique de transit.

## Schéma complémentaire B — Mesurer la qualité du contrôle

~~~text
Contrôle configuré
      |
      v
Test de conformité automatisé
      |
      v
Déploiement limité
      |
      v
Observation du trafic et des routes
      |
      +--> résultat attendu : enregistrer la preuve
      |
      +--> résultat inattendu : contenir et restaurer
      |
      v
Revue périodique de la politique
~~~

Une mesure de sécurité n'est démontrée que si le test et l'observation réelle confirment son comportement. La configuration seule décrit l'intention, tandis que les résultats donnent la preuve de l'application effective.

## Conclusion

La sécurité du routage repose sur la maîtrise des annonces, la réduction de la confiance implicite et la capacité de prouver ce que le réseau fait réellement. Les filtres de préfixes et de chemins, les politiques d’import/export, RPKI, les rôles BGP, les protections de session, l’authentification interne, la sécurité du plan de contrôle et la supervision répondent à des risques différents. Les additionner sans cohérence ne suffit pas : ils doivent être documentés, testés ensemble, révisés et intégrés aux procédures de changement.

La bonne pratique n’est pas de viser une configuration « sécurisée une fois pour toutes ». C’est d’établir une politique explicite, surveiller les écarts, limiter leur portée, préserver des preuves et pouvoir revenir à un état connu. C’est ainsi que le routage devient un service résilient plutôt qu’une source de confiance implicite.

Fin du cours.