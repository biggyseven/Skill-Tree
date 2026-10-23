# VTP et gestion des VLANs - Expert

**Niveau :** Expert

Le VLAN Trunking Protocol (VTP) est un protocole de gestion de couche 2 historiquement associé aux commutateurs Cisco Catalyst. Sa fonction principale est de distribuer et de maintenir une base de données VLAN cohérente à travers un domaine de commutation. Lorsqu'il est correctement conçu, VTP réduit le nombre d'opérations répétitives et limite les divergences entre commutateurs. Lorsqu'il est mal conçu, il peut au contraire propager une modification erronée sur une partie importante du réseau, supprimer des VLANs attendus ou rendre des segments entiers inaccessibles. À un niveau expert, VTP doit donc être traité comme un mécanisme de contrôle du plan de couche 2, et non comme une simple commande destinée à créer des VLANs en une seule fois.

Historiquement, VTP a été conçu pour les architectures de commutation administrées de manière centralisée. Les premières versions, VTP version 1 et version 2, reposent sur un domaine de gestion, un numéro de révision de configuration et la propagation d'annonces à travers les trunks. Cette conception facilite la synchronisation, mais elle introduit une dépendance importante à l'intégrité de la base de données et à la provenance des mises à jour. Une configuration de laboratoire ou un commutateur réutilisé peut conserver un numéro de révision élevé et influencer un domaine si les conditions de compatibilité et les règles de version le permettent. Cette caractéristique explique pourquoi une opération apparemment anodine, comme connecter un équipement récupéré en stock, peut devenir une panne majeure lorsque le domaine utilise VTP v1/v2.

VTP version 3 a été conçu pour corriger plusieurs limites des premières versions, notamment le contrôle des modifications par l'intermédiaire d'un serveur primaire et la prise en charge de fonctionnalités supplémentaires. Il permet de gérer les VLANs de plage étendue sur les plateformes qui l'implémentent et, selon les versions Cisco, de distribuer également des informations liées à la base MST. VTPv3 ne rend toutefois pas le réseau automatiquement sûr : le serveur primaire, les identifiants, les trunks, les mots de passe, les mécanismes d'administration et les procédures de changement restent des éléments critiques. La compatibilité exacte doit toujours être vérifiée par famille de commutateurs et version logicielle, car les commandes et certaines limites varient selon IOS, IOS XE et les gammes matérielles.

L'approche experte consiste à raisonner en termes de cycle de vie de la base VLAN, de version du protocole, d'autorité de modification, de révision, de propagation et de domaine de panne. Il faut distinguer la base VLAN locale, les annonces VTP, le transport des annonces par le réseau de trunks, la liste des VLANs autorisés sur chaque trunk et le fonctionnement de STP. VTP ne configure pas à lui seul les ports d'accès, ne crée pas automatiquement les sous-interfaces des routeurs, ne garantit pas que chaque VLAN est transporté sur tous les trunks et ne remplace pas les politiques de segmentation. Une conception solide choisit délibérément entre l'exploitation de VTP, son usage limité à un périmètre précis ou une gestion locale/automatisée des VLANs sans domaine VTP partagé.

> **Analogie** : Imagine une grande entreprise disposant de dizaines de bâtiments. Chaque bâtiment possède une liste officielle de départements : Finance, Ressources humaines, Production, Invités, Téléphonie et Administration. Les VLANs représentent les départements logiques ; les commutateurs représentent les répartiteurs réseau ; les trunks représentent les liaisons qui transportent plusieurs départements entre bâtiments. Le protocole VTP fonctionne comme un registre partagé qui annonce les changements de la liste officielle aux répartiteurs participants.
>
> Le registre ne fait cependant pas tout le travail. Il ne décide pas quel employé doit se trouver dans quel département, ne vérifie pas à lui seul que les couloirs entre bâtiments sont ouverts et ne garantit pas que chaque bâtiment a besoin de tous les départements. C'est l'administrateur qui définit les ports d'accès, les trunks, les politiques de sécurité et les règles de routage inter-VLAN. VTP fournit surtout une méthode de distribution des informations concernant l'existence et certaines propriétés des VLANs.
>
> Dans un ancien système de registre, une copie portant le numéro d'édition 42 peut être considérée comme plus récente qu'une copie portant le numéro 17, même si son contenu est erroné. Si un répartiteur inconnu arrive avec une copie ancienne mais un numéro d'édition plus élevé, les autres répartiteurs peuvent croire que cette copie constitue la référence la plus récente. C'est l'analogie du risque de numéro de révision en VTP v1/v2. La date d'arrivée de l'équipement n'est pas nécessairement la même chose que l'autorité réelle du contenu. VTPv3 ajoute un contrôle d'autorité : une mise à jour de la base VLAN doit être validée par un serveur primaire désigné pour cette instance. Ce contrôle diminue le risque de remplacement incontrôlé, sans dispenser l'administrateur de vérifier l'identité du commutateur, la base attendue et le scénario de reprise.
>
> Enfin, le registre peut annoncer que le département « Finance » existe, mais il ne construit pas les portes d'accès, ne configure pas les contrôles de passage et ne s'assure pas que chaque bâtiment possède un chemin utile vers ce département. De la même manière, la présence d'un VLAN dans la base locale ne signifie pas que le VLAN traverse tous les trunks, qu'un port d'accès y est affecté, que STP y a ouvert un chemin ou que la passerelle de couche 3 est joignable. Le dépannage expert sépare donc toujours la cohérence de la base VTP de la connectivité réelle de bout en bout.

---

## 1. La théorie et les algorithmes

### 1.1. Périmètre fonctionnel de VTP

VTP distribue des informations de base VLAN dans un domaine de gestion. Selon la version et la plateforme, ces informations incluent notamment l'identifiant VLAN, le nom, l'état et des attributs de type de VLAN. VTP ne transporte pas les trames utilisateur à la place de 802.1Q : il transporte des annonces de contrôle. Le trafic utilisateur continue à être commuté selon les tables MAC, l'appartenance des ports aux VLANs, les trunks, les politiques de sécurité et l'état du spanning tree.

Il faut distinguer les opérations suivantes :

1. **Créer ou supprimer une définition VLAN** dans la base de données d'un commutateur.
2. **Diffuser la définition** aux équipements membres du domaine VTP.
3. **Autoriser le VLAN sur un trunk** donné.
4. **Affecter un port d'accès** au VLAN.
5. **Permettre un acheminement de couche 3**, si le VLAN doit communiquer avec d'autres sous-réseaux.
6. **Garantir un chemin de couche 2 sans boucle**, généralement au moyen de STP ou d'une technologie appropriée.

VTP intervient surtout sur les deux premières opérations. Les autres doivent être validées indépendamment. Une base VLAN synchronisée ne garantit pas une topologie fonctionnelle.

VTP est traditionnellement un protocole propriétaire Cisco, même si son format et son comportement sont documentés dans la documentation technique du constructeur. Sa présence et ses limites dépendent de la plate-forme. Sur un réseau multi-constructeurs, il faut vérifier si l'interopérabilité recherchée existe réellement ; il ne faut pas supposer qu'un équipement tiers participe à la synchronisation uniquement parce qu'il prend en charge IEEE 802.1Q.

### 1.2. Domaine VTP et identités des équipements

Un domaine VTP est l'ensemble logique des commutateurs qui partagent les paramètres de gestion correspondants et acceptent de participer à la même distribution. Pour les modes serveur et client classiques, le nom de domaine est une condition importante de l'échange. Le mot de passe, lorsqu'il est configuré, doit également être cohérent entre les équipements concernés. La version VTP prise en charge et activée constitue une autre condition de compatibilité.

Un domaine VTP n'est pas synonyme de domaine de broadcast. Un même domaine de gestion peut contenir plusieurs VLANs distincts, et un même VLAN peut traverser plusieurs commutateurs lorsque le réseau de trunks le transporte. Inversement, des commutateurs reliés physiquement peuvent ne pas participer au même domaine VTP si leur mode, leur version ou leur configuration l'empêche.

Le nom de domaine doit être explicitement planifié. Des noms de domaine qui diffèrent d'un seul caractère peuvent empêcher la synchronisation attendue. À l'inverse, un nom identique ne suffit pas à prouver que deux équipements doivent être fusionnés : la compatibilité de version, l'autorité des mises à jour, les mots de passe et le plan de VLAN doivent également être examinés. Il est prudent de ne pas brancher directement un commutateur d'un environnement de test dans le réseau de production sans une procédure d'intégration contrôlée.

Les équipements en mode transparent ou off ont un comportement différent des équipements serveur/client. Un commutateur transparent gère localement sa propre base VLAN et ne remplace pas sa base par les annonces reçues. Selon la version et la plateforme, il peut néanmoins relayer certaines annonces VTP reçues sur ses trunks. Le mode off se comporte en général comme transparent sur la base locale, mais ne relaie pas les annonces. Les détails exacts doivent être confirmés dans le guide de configuration de la version utilisée.

### 1.3. Les modes opérationnels

| Mode | Peut modifier localement la base VLAN ? | Applique les mises à jour VTP reçues ? | Peut annoncer des mises à jour ? | Usage typique |
|---|---|---|---|---|
| Server VTP v1/v2 | Oui | Oui | Oui | Commutateur de gestion de base dans les domaines classiques |
| Client VTP v1/v2 | Non, pas de modification locale ordinaire de la base partagée | Oui | Relaye les informations selon le fonctionnement du protocole | Accès à gestion centralisée, environnements historiques |
| Server secondaire VTPv3 | Oui selon les règles de version, mais les mises à jour VLAN nécessitent l'autorité primaire | Oui | Sauvegarde/réception et participation au domaine | Redondance et préparation d'un rôle primaire |
| Primary server VTPv3 | Oui, autorité de modification pour l'instance concernée | Oui | Oui, diffuse les mises à jour autorisées | Source autorisée de changements de base |
| Transparent | Oui, base locale indépendante | Non pour sa propre base | Pas en tant que source d'une base partagée ; peut relayer selon version | Autonomie locale, segmentation administrative ou laboratoire |
| Off | Oui localement lorsque la plateforme le permet | Non pour sa propre base | N'émet pas ou ne relaie pas les annonces VTP selon la définition de la plateforme | Désactivation de VTP dans le périmètre considéré |

Les termes serveur et client n'ont pas exactement le même sens en VTPv3. Il ne faut pas appliquer mécaniquement à VTPv3 la règle historique selon laquelle tout commutateur en mode server peut propager une modification VLAN. En VTPv3, le rôle de **primary server** est un état opérationnel d'autorité associé à une instance, et non simplement un synonyme permanent de `vtp mode server`.

Un domaine peut fonctionner avec une base VTPv3 sans que chaque serveur secondaire soit primaire à tout instant. Le rôle primaire est obtenu par une opération explicite et doit être revalidé selon les procédures de reprise. Le fait qu'un équipement soit configuré en mode server ne prouve donc pas qu'il est le serveur primaire actuel.

### 1.4. Trunks : le canal de transport des annonces

Pour échanger les annonces entre commutateurs, VTP dépend d'un réseau de trunks fonctionnels. Sur les trunks Ethernet classiques, les trames VTP sont associées à l'encapsulation de couche 2 prise en charge par la plateforme. Historiquement, la documentation Cisco décrit des annonces encapsulées dans des trames ISL ou 802.1Q selon la génération et la configuration des équipements. ISL est aujourd'hui une technologie historique ; 802.1Q est le mécanisme de marquage standard utilisé dans les réseaux Ethernet modernes.

La destination MAC bien connue documentée par Cisco pour VTP est `01-00-0C-CC-CC-CC`. VTP utilise une encapsulation de contrôle spécifique ; ce n'est pas une annonce IP routée et elle n'est pas transférée à travers un routeur IP ordinaire comme un paquet applicatif. Elle suit le périmètre de couche 2 où les équipements peuvent échanger les annonces.

La présence physique d'un câble entre deux commutateurs ne suffit pas. Il faut que la liaison soit en trunk, que les paramètres de trunk soient compatibles, que le port ne soit pas dans un état qui bloque le transport des annonces pertinentes et que les versions soient compatibles. Une incohérence de native VLAN peut être un défaut de conception ou de sécurité, même si elle n'empêche pas systématiquement tout échange VTP.

Les annonces VTP et les trames utilisateur ne répondent pas exactement aux mêmes règles. La liste des VLANs autorisés sur un trunk limite le transport des trames de ces VLANs, mais il ne faut pas déduire sans vérification que chaque restriction de VLAN autorisé entraîne la même restriction pour tous les messages de contrôle VTP. Le comportement dépend de la plateforme et du traitement des trames de contrôle. L'observation de l'état VTP et du trunk doit précéder toute conclusion.

### 1.5. Types d'annonces VTP

Les versions classiques de VTP s'appuient sur différents types d'annonces qui coordonnent la vérification de la base et le transfert d'informations VLAN.

| Type d'annonce | Rôle conceptuel | Utilité opérationnelle |
|---|---|---|
| Summary Advertisement | Présente l'identité du domaine et l'état de révision | Permet à un voisin de déterminer s'il doit demander une base plus récente |
| Subset Advertisement | Transporte des enregistrements de VLAN | Communique le contenu de la base, parfois réparti en plusieurs annonces |
| Advertisement Request | Demande les informations nécessaires pour synchroniser la base | Utilisée lorsqu'un commutateur détecte qu'il lui manque une version plus récente |
| Join message | Aide au fonctionnement de certaines fonctions historiques, notamment liées au pruning | Participe aux mécanismes de gestion du trafic selon la version et le contexte |

Dans les versions classiques, une annonce récapitulative contient notamment le nom de domaine, la version VTP, le numéro de révision et d'autres informations d'identification. Une annonce de sous-ensemble fournit les informations VLAN détaillées. Lorsque plusieurs VLANs sont présents, plusieurs annonces peuvent être nécessaires.

Ces messages sont des mécanismes de contrôle, pas des commandes de configuration textuelles. Le commutateur reçoit, valide et interprète les données selon l'état local, le mode VTP, le mot de passe, la version et les règles d'autorité applicables. L'administrateur ne doit donc pas se limiter à constater qu'un paquet VTP circule : le contenu doit être accepté et la base locale doit présenter le résultat attendu.

### 1.6. Numéro de révision : mécanisme et risques

Le numéro de révision est un compteur de 32 bits utilisé dans VTP pour distinguer les versions successives de la base de configuration. Dans les scénarios VTP v1/v2 classiques, une modification VLAN sur un serveur augmente le compteur et provoque des annonces. Un commutateur recevant une annonce du même domaine compare le numéro distant au numéro local. Si la base annoncée est considérée comme plus récente, le commutateur peut demander les informations et remplacer sa base correspondante selon les règles du protocole.

Le numéro de révision ne constitue pas un contrôle de qualité. Il ne prouve pas que la base distante est correcte, qu'elle correspond au plan d'adressage actuel ou qu'elle a été approuvée par l'équipe réseau. Il représente une notion de fraîcheur relative au protocole. La conséquence est importante : dans les domaines v1/v2, le raccordement d'un équipement possédant un numéro élevé et une base incohérente peut provoquer la diffusion de cette base dans le domaine lorsque les conditions d'acceptation sont réunies.

Exemple conceptuel : un réseau de production possède 42 VLANs et une révision VTP de 18. Un commutateur de laboratoire contient seulement 5 VLANs, mais sa révision vaut 93. Si ce commutateur est connecté sans préparation dans un domaine VTP v1/v2 compatible, ses annonces peuvent être interprétées comme une version plus récente. Dans le pire des cas, des VLANs attendus sont supprimés de la base des commutateurs du domaine, même si les configurations des ports et certaines interfaces de couche 3 n'ont pas été modifiées. Le trafic associé devient alors indisponible jusqu'à la restauration de la base et la correction des dépendances.

Le numéro de révision doit être vérifié avant l'intégration d'un équipement. Dans certains environnements historiques, une procédure courante consistait à isoler le commutateur, changer temporairement son nom de domaine, puis le restaurer, afin de remettre le compteur à zéro. Cette procédure est dépendante de la version et ne doit pas être appliquée aveuglément en production. Avec VTPv3, il faut plutôt examiner l'état primaire, la version, la base VLAN et la procédure de prise de contrôle prévue.

Un numéro plus grand n'est pas toujours « meilleur » au sens opérationnel. Il indique une révision associée à la base, mais il ne garantit ni l'intégrité du plan de VLAN ni la légitimité de la source. Les sauvegardes de la base VLAN, les exports de configuration, les contrôles avant raccordement et les procédures de retour arrière sont plus importants qu'une confiance aveugle dans le compteur.

### 1.7. Fonctionnement du processus de synchronisation

Un cycle de synchronisation classique peut être représenté ainsi :

```text
   Commutateur A                         Commutateur B
   Base VLAN rev. 18                     Base VLAN rev. 12
          |                                      |
          |---- Summary Advertisement ---------->| 
          |     domaine CAMPUS, rev. 18          |
          |                                      |
          |                         Compare domaine/version/revision
          |                                      |
          |<--- Advertisement Request ------------|
          |                                      |
          |---- Subset Advertisement(s) --------->|
          |     liste des VLANs                   |
          |                                      |
          |                         Valide et met à jour la base
          |                                      |
          |                         Base VLAN rev. 18
```

Le schéma est conceptuel et représente le chemin classique d'une demande suivie d'annonces. Les échanges exacts, leur fréquence, les champs présents et les décisions dépendent de la version VTP et du contexte. Il ne faut pas supposer que chaque mise à jour s'effectue toujours avec exactement un paquet de chaque type.

La séquence doit être évaluée à partir de plusieurs conditions : le domaine doit correspondre, les versions doivent être compatibles, le mot de passe doit être correct si configuré, la connexion trunk doit transporter les annonces et le mode local doit autoriser la participation à la synchronisation. Sous VTPv3, le contrôle supplémentaire du serveur primaire entre également en jeu pour les modifications de base.

L'opération n'affecte pas automatiquement les ports d'accès. Si VLAN 120 est ajouté à la base, les commutateurs apprennent sa définition, mais aucun port ne rejoint spontanément ce VLAN. Le trunk doit aussi autoriser VLAN 120. Le spanning tree doit permettre le chemin, et une passerelle L3 doit être configurée si les hôtes doivent joindre d'autres sous-réseaux.

### 1.8. Différences entre VTP v1, v2 et v3

| Fonction | VTP v1 | VTP v2 | VTP v3 |
|---|---|---|---|
| Domaine de gestion | Oui | Oui | Oui, avec mécanismes adaptés à la version |
| Numéro de révision | Oui | Oui | Oui, avec contrôle d'autorité supplémentaire |
| Prise en charge des VLANs étendus | Limitée / non prise en charge dans les scénarios classiques | Limitée / non prise en charge dans les scénarios classiques | Prise en charge sur les plateformes compatibles |
| Prise en charge des Private VLANs par la base VTP | Non dans les versions historiques | Non dans les versions historiques | Oui sur les plateformes compatibles, avec précautions de mode |
| Serveur primaire explicite | Non | Non | Oui |
| Distribution de la base MST | Non comme fonction VTPv3 | Non comme fonction VTPv3 | Possible selon la plateforme et l'instance |
| TLV inconnus | Comportement plus restrictif | Support amélioré | Contrôle et extensions liés à la version |
| Compatibilité avec la version antérieure | Dépend de la version et du domaine | V1 et V2 ne doivent pas être considérées comme interchangeables dans le même domaine | VTPv3 n'accepte pas les informations de configuration provenant d'un équipement v1/v2 comme source de mise à jour valide |

VTP v2 ajoute notamment la prise en charge de certains types de VLAN historiques, la propagation de TLV inconnus par les équipements compatibles et une différence de traitement du mode transparent. Ces fonctionnalités sont importantes dans les environnements anciens, mais elles ne doivent pas être confondues avec le contrôle du serveur primaire introduit par VTPv3.

VTPv3 doit être activé explicitement sur chaque équipement concerné ; il ne faut pas supposer que le mécanisme d'activation automatique historique de VTPv2 s'applique à VTPv3. La documentation Cisco précise également que VTPv1 et VTPv2 ne sont pas interopérables au sein d'un même domaine de façon générale, et que les équipements uniquement compatibles v1 ne peuvent pas participer à un domaine VTPv3. Dans une migration, il faut donc inventarier les modèles et les versions logicielles avant de choisir la stratégie.

Les changements de version ne sont pas des opérations cosmétiques. Ils peuvent modifier le comportement d'acceptation des annonces, la disponibilité des types de VLAN et la façon de valider les mises à jour. Il est indispensable de réaliser une matrice de compatibilité à partir de la documentation constructeur de chaque gamme de commutateurs.

### 1.9. VTPv3 : primaire, secondaires et autorité de modification

VTPv3 distingue le mode de fonctionnement du commutateur et le rôle primaire pour une instance de base. Tous les serveurs VTPv3 ne sont pas primaires en permanence. L'opération de prise de rôle primaire autorise un serveur donné à diffuser les mises à jour de la base concernée. Une instance peut concerner la base VLAN ou, sur les plateformes compatibles, la base MST.

La commande Cisco typique pour activer la version 3 est `vtp version 3`. Le rôle primaire pour la base VLAN est ensuite obtenu en mode privilégié par une commande telle que `vtp primary vlan`, sous réserve de la syntaxe de la version. Une variante `force` permet de prendre le contrôle en outrepassant certains conflits, et doit être réservée à une procédure explicitement validée. Ce n'est pas une commande de réparation à essayer sans sauvegarde.

Le rôle primaire est opérationnel et peut être perdu après un redémarrage, un changement de paramètres du domaine ou une transition de rôle selon la plateforme. La procédure d'exploitation doit donc prévoir comment reconnaître le primaire actif, comment en réélire un de façon contrôlée et comment vérifier la cohérence après bascule. Une simple configuration `vtp mode server` ne prouve pas qu'un équipement détient encore l'autorité primaire.

Un serveur secondaire est utile pour maintenir un équipement préparé à prendre la responsabilité de la base, mais cela ne signifie pas que plusieurs serveurs peuvent modifier librement la base VLAN en même temps. VTP a été conçu pour favoriser un processus de changements contrôlé, pas pour résoudre de manière générale les conflits multi-maîtres comme un système de base de données distribué conçu à cet effet.

La désignation du serveur primaire doit être traitée comme une opération de changement. Avant la prise de rôle, l'administrateur compare les VLANs existants, exporte les configurations, vérifie le domaine, le mot de passe, la version et l'état des trunks. Après la prise de rôle, il vérifie la révision, la base, la diffusion et le résultat sur les commutateurs du domaine. Le recours à `force` peut écraser des informations concurrentes ; l'option ne doit donc pas être intégrée à un script de routine sans garde-fous.

### 1.10. Plages de VLAN et implications de version

Les VLANs sont identifiés par un ID. Dans l'environnement Cisco classique, on distingue généralement une plage normale de 1 à 1005 et une plage étendue au-delà de 1005, jusqu'à 4094 pour le format VLAN ID 12 bits, avec des réserves et limites liées à la plateforme. Le traitement des VLANs 1002 à 1005 est historique : ils sont réservés à des usages particuliers et ne doivent pas être traités comme des VLANs utilisateurs ordinaires. Les limites exactes d'utilisation et de propagation dépendent de la version de VTP et de l'équipement.

VTPv1/v2 et VTPv3 n'ont pas les mêmes capacités pour les VLANs étendus. Dans un environnement qui exige des VLANs au-dessus de 1005, il faut vérifier que chaque équipement et chaque version de logiciel prend en charge la base et le mode attendus. VTPv3 est la version à examiner pour les environnements compatibles qui nécessitent la distribution de VLANs étendus.

Un piège consiste à confondre la capacité de créer un VLAN localement et la capacité de le distribuer par VTP. Un commutateur en mode transparent peut accepter localement une définition qui ne se propage pas comme une mise à jour VTP partagée. De même, un VLAN présent dans la base ne signifie pas que le VLAN est autorisé dans les listes de trunk. Ces mécanismes sont indépendants et doivent être testés séparément.

### 1.11. VTP pruning : principe et limites

Le VTP pruning cherche à limiter la diffusion de certains trafics de couche 2 sur des trunks où les VLANs concernés ne sont pas nécessaires en aval. Il vise principalement à réduire le transport inutile de broadcasts, d'unicasts inconnus et de certains flux qui seraient autrement propagés au sein d'un VLAN.

Exemple : SW1 est relié à SW2 et SW3. Le VLAN 30 est utilisé uniquement derrière SW2 ; aucun port ni équipement participant à VLAN 30 ne se trouve derrière SW3. Sans mécanisme de pruning, les trames de diffusion de VLAN 30 peuvent être envoyées sur le trunk vers SW3 si VLAN 30 est transporté. Le pruning peut permettre à SW1 de ne pas envoyer certains trafics de ce VLAN sur un trunk lorsque le voisinage aval n'en a pas besoin.

```text
                    +-------------+
                    |     SW1     |
                    +-------------+
                      /         \
             trunk A /           \ trunk B
                    /             \
              +---------+      +---------+
              |   SW2   |      |   SW3   |
              +---------+      +---------+
              VLAN 30           Aucun port
              utilisé           VLAN 30

   Sans pruning : certains broadcasts VLAN 30 peuvent
   être transportés vers SW3 si le trunk le permet.

   Avec pruning : le transport peut être réduit sur le
   trunk B si les conditions d'élagage sont réunies.
```

Le pruning ne remplace pas la commande `switchport trunk allowed vlan`. La liste des VLANs autorisés définit quels VLANs peuvent être transportés sur le trunk. Le pruning détermine si certains trafics de VLANs pourtant transportables sont nécessaires en aval, selon le mécanisme de signalisation pris en charge. Pour réduire la surface d'exposition, on doit définir explicitement des listes de VLANs autorisés plutôt que de compter uniquement sur le pruning.

La documentation Cisco précise que VTP pruning ne s'applique pas à tous les VLANs : VLAN 1, VLANs 1002 à 1005 et VLANs étendus au-delà de 1005 sont non éligibles dans les contextes documentés. Le pruning prend effet après un délai de convergence et ne doit pas être supposé immédiat. Son comportement exact doit être confirmé sur la version et la gamme utilisées.

Le pruning est annoncé et coordonné dans le domaine et dépend de la connaissance des VLANs qui sont nécessaires derrière certains ports. Il ne faut pas l'activer à l'aveugle sur un réseau qui présente des contraintes spécifiques de téléphonie, de services L2, de PVLAN ou des dispositifs qui ne déclarent pas la présence de manière attendue. La validation consiste à tester les flux de broadcast, à examiner les trunks, à confirmer les VLANs autorisés et à vérifier les états de pruning exposés par la plateforme.

### 1.12. Trunk allowed VLAN, native VLAN et VTP : ne pas confondre

Le trunk 802.1Q est un mécanisme de transport multi-VLAN. Sa configuration possède ses propres paramètres, notamment le mode de trunk, l'encapsulation lorsqu'elle est configurable, la VLAN native et la liste des VLANs autorisés. VTP ne remplace aucun de ces paramètres.

| Mécanisme | Question à laquelle il répond | Exemple de commande de vérification |
|---|---|---|
| Base VLAN locale | Le commutateur connaît-il la définition de VLAN 120 ? | `show vlan brief` |
| VTP | La définition est-elle partagée et synchronisée dans le domaine ? | `show vtp status` |
| Trunk | La liaison transporte-t-elle VLAN 120 ? | `show interfaces trunk` |
| Port d'accès | Le poste est-il affecté à VLAN 120 ? | `show running-config interface ...` |
| STP | Le chemin est-il dans un état permettant le transfert dans VLAN 120 ? | `show spanning-tree vlan 120` |
| Couche 3 | Existe-t-il une passerelle et une route pour le trafic inter-VLAN ? | `show ip interface brief`, `show ip route` |

Une configuration VTP réussie peut donc coexister avec une panne de service. Le VLAN peut être appris partout, mais absent de la liste autorisée d'un trunk. Il peut être autorisé, mais le chemin STP peut être bloqué sur le lien attendu. Il peut circuler en couche 2, mais la passerelle peut être absente ou mal configurée. Le dépannage doit suivre la chaîne complète au lieu d'attribuer tout problème VLAN à VTP.

La VLAN native mérite une attention particulière. Elle concerne le traitement du trafic non étiqueté sur le trunk, et son incohérence peut entraîner des erreurs, des problèmes de sécurité ou des écarts de classification. Il est recommandé d'utiliser une VLAN native dédiée et inutilisée pour les hôtes lorsque la conception le permet, et de faire correspondre les paramètres aux deux extrémités. Les bonnes pratiques exactes dépendent de la plateforme et de l'architecture ; elles ne sont pas assurées par VTP.

### 1.13. Modes transparent et off dans une architecture moderne

Le mode transparent est pertinent lorsque chaque commutateur doit maintenir une base VLAN locale ou lorsque le domaine de synchronisation partagé n'est pas souhaité. Il peut également convenir pour séparer un périmètre d'exploitation tout en relayant certaines annonces dans des scénarios de transit. Le comportement du relais dépend de la version. Le mode off vise une désactivation plus explicite de VTP, y compris la non-transmission des annonces selon la définition Cisco.

Il faut toujours confirmer le résultat opérationnel après changement de mode. Sur certaines familles, la commande de mode et le domaine peuvent être enregistrés dans la configuration, alors que la base VLAN utilise un fichier de base distinct (`vlan.dat`) ou un mécanisme de stockage particulier. En conséquence, la persistance après redémarrage dépend du modèle et de la méthode de configuration. La configuration de sauvegarde ne doit pas être supposée contenir à elle seule toutes les informations de la base VLAN.

Le passage en transparent n'est pas un moyen universel d'effacer une base VTP ou de remettre la révision à zéro. Il modifie le comportement de participation et peut avoir des conséquences sur la persistance de la base. Avant tout changement, exporter la configuration, documenter le domaine, sauvegarder la base lorsque la plateforme le permet et confirmer les conditions de redémarrage.

Dans les réseaux qui choisissent de ne pas utiliser VTP, une approche robuste consiste à configurer les VLANs localement ou au moyen d'un système d'automatisation contrôlé. Cette méthode demande davantage de rigueur pour garantir la cohérence entre commutateurs, mais elle permet d'éviter qu'une seule base VTP mal préparée soit propagée à toute l'infrastructure. Il n'existe pas de stratégie universellement meilleure : la décision dépend du risque accepté, de la taille du domaine, des compétences d'exploitation, des outils d'automatisation et des capacités des équipements.

### 1.14. Sécurité et modèle de menace

Le principal risque VTP n'est pas une simple erreur de nom de VLAN : c'est la possibilité qu'une modification de base non souhaitée soit acceptée puis propagée dans un périmètre plus large. Dans les réseaux v1/v2, le numéro de révision peut amplifier l'impact si un commutateur est raccordé avec une base inattendue. VTPv3 améliore le contrôle de l'autorité de modification, mais le réseau reste vulnérable à une mauvaise opération d'administration, à des secrets exposés ou à des trunks non maîtrisés.

Les mesures de défense doivent être superposées :

- désactiver la négociation de trunk automatique lorsque cela est approprié et configurer explicitement les trunks ;
- limiter les VLANs autorisés sur chaque trunk au strict nécessaire ;
- désactiver les ports inutilisés et les placer dans un VLAN de quarantaine ou une configuration de sécurité conforme à la politique ;
- limiter les interfaces qui peuvent former des liens de couche 2 vers des commutateurs inconnus ;
- protéger les accès d'administration par SSH, AAA, mots de passe robustes et séparation du réseau de gestion ;
- documenter et surveiller les changements de VTP, de VLAN, de trunk et de STP ;
- sauvegarder la base VLAN et la configuration avant les opérations de maintenance ;
- n'intégrer un commutateur neuf, reconditionné ou de laboratoire qu'après vérification de sa version, de son domaine, de son mode et de sa révision ;
- privilégier VTPv3 quand la plateforme et les besoins le justifient, tout en contrôlant explicitement le serveur primaire.

Le mot de passe VTP n'est pas une solution magique. Il permet de faire rejeter les annonces non conformes à la valeur configurée, mais il doit être configuré de manière cohérente et conservé en sécurité. Il ne protège pas contre une erreur effectuée par un administrateur légitime, ne remplace pas la restriction des trunks et ne constitue pas à lui seul une architecture de contrôle d'accès complète.

### 1.15. Politique de gestion : changement, sauvegarde et retour arrière

À un niveau expert, toute modification de base VLAN doit être considérée comme un changement de service. Elle peut modifier l'appartenance de ports, l'état de trunks, les instances STP, les passerelles L3, les politiques de sécurité et la connectivité de plusieurs applications. Une opération VTP devrait donc être précédée d'une validation du périmètre d'impact.

Un dossier de changement doit contenir au minimum : l'objectif, les VLANs concernés, le commutateur autorisé à modifier la base, la version VTP, le domaine, l'état primaire si VTPv3 est utilisé, les trunks concernés, la liste des VLANs autorisés, les dépendances STP, les interfaces L3 et les tests de validation.

La sauvegarde doit inclure des sorties structurées telles que `show vtp status`, `show vlan brief`, `show interfaces trunk`, `show spanning-tree summary`, `show running-config` et les informations de sauvegarde supportées par le modèle. Comme la base VLAN peut être stockée indépendamment de la configuration texte, la procédure doit prévoir sa sauvegarde spécifique si le système le permet. Une simple copie de `running-config` n'est pas nécessairement suffisante.

Le retour arrière doit indiquer comment restaurer la base VLAN attendue, comment vérifier la cohérence sur les membres du domaine et comment contrôler que les trunks et ports d'accès restent conformes. Une suppression massive de VLANs puis leur recréation peut être dangereuse si les VLANs sont associés à des politiques, à des interfaces virtuelles ou à des fonctionnalités spécifiques. Les opérations de restauration doivent être testées avant d'être nécessaires.

> **Piège :** Le numéro de révision n'est ni une signature de qualité ni une preuve d'autorité. En VTP v1/v2, un équipement ayant une révision élevée peut présenter une base inattendue et déclencher une synchronisation dommageable si les conditions de domaine et de compatibilité sont réunies. Ne raccorde jamais directement un commutateur récupéré ou issu d'un laboratoire à un domaine de production sans contrôle préalable. En VTPv3, vérifie en plus le primaire actif et n'utilise pas `vtp primary ... force` comme une commande de dépannage improvisée. Enfin, ne confonds pas « VLAN appris par VTP » avec « VLAN transporté sur le trunk » : la base partagée, la liste allowed VLAN, le port d'accès, STP et le routage constituent des couches de contrôle distinctes.

```text
              DOMAINE DE GESTION VTP
   +--------------------------------------------------+
   |                                                  |
   |    +-------------+      +-------------+          |
   |    | SW-CORE-1   |======| SW-CORE-2   |          |
   |    | VTPv3       |      | VTPv3       |          |
   |    | Primary     |      | Secondary   |          |
   |    +-------------+      +-------------+          |
   |            ||                   ||              |
   |       trunks 802.1Q        trunks 802.1Q         |
   |            ||                   ||              |
   |      +-------------+      +-------------+       |
   |      | SW-ACC-1    |      | SW-ACC-2    |       |
   |      | client ou   |      | transparent |       |
   |      | mode adapté |      | base locale |       |
   |      +-------------+      +-------------+       |
   |                                                  |
   +--------------------------------------------------+

   VTP : distribution de la base de VLANs.
   Trunk : transport de trames multi-VLAN.
   STP : contrôle des chemins L2 sans boucle.
   VLAN membership : affectation des ports.
   Routage L3 : communication entre sous-réseaux.
```

## 2. Configuration et Pratique

Les exemples qui suivent utilisent une syntaxe de type Cisco IOS / IOS XE courante. La prise en charge et les mots-clés précis peuvent varier selon le modèle, la version logicielle et l'instance VTP. Avant d'appliquer une configuration, confronte les commandes à la documentation de la plate-forme et teste-les dans un laboratoire. Les blocs sont des modèles pédagogiques, pas une instruction de coller toutes les commandes sur un réseau en production sans adaptation.

### 2.1. Topologie de laboratoire

Le laboratoire comprend trois commutateurs : SW1 est le commutateur de distribution choisi pour être serveur primaire VTPv3 ; SW2 est un serveur secondaire de secours ; SW3 est un commutateur d'accès configuré pour participer à la base selon la politique de l'exercice. Les trunks sont explicitement configurés en 802.1Q sur les plateformes qui proposent cette syntaxe.

```text
                    Domaine VTP : CAMPUS
                    Version de référence : 3

                      +----------------+
                      |      SW1       |
                      | VTP Server     |
                      | Primary VLAN   |
                      +----------------+
                         ||          \\
                         || trunk     \\ trunk
                         ||             \\
                 +----------------+   +----------------+
                 |      SW2       |===|      SW3       |
                 | Server /       |   | Client ou      |
                 | Secondary      |   | mode validé    |
                 +----------------+   +----------------+

   VLANs du laboratoire :
   10 USERS
   20 VOICE
   30 SERVERS
   40 GUEST
   999 NATIVE-UNUSED (exemple de VLAN native dédiée)
```

La topologie de laboratoire doit être isolée de la production. Avant l'activation de VTP, il faut vérifier qu'aucune liaison de commutation ne connecte le laboratoire à un domaine qui partage involontairement le même nom et la même version. La base VLAN initiale doit être sauvegardée sur les trois commutateurs.

### 2.2. Inventaire avant configuration

Sur chaque commutateur, collecter les informations suivantes :

```cisco
show version
show vtp status
show vtp password
show vlan brief
show interfaces trunk
show spanning-tree summary
show running-config
```

Toutes les commandes ne sont pas disponibles sous la même forme sur chaque modèle. `show vtp password` n'affiche pas nécessairement le secret en clair ; il sert à vérifier la présence du paramètre selon l'implémentation. L'objectif est d'établir la version logicielle, le mode, la version VTP, le domaine, le numéro de révision, l'état de pruning, les VLANs existants et les trunks opérationnels.

Les informations doivent être sauvegardées dans un dossier de changement horodaté. Une sortie de commande est souvent plus utile qu'une capture d'écran seule, car elle peut être recherchée et comparée. Dans les environnements automatisés, un outil de collecte peut produire une base de référence avant et après chaque changement.

### 2.3. Configuration de base du serveur VTPv3

Exemple de configuration sur SW1. Il faut s'assurer que les commandes sont prises en charge par la version IOS/IOS XE utilisée.

```cisco
hostname SW1
!
! Préparer explicitement le domaine VTP et la version.
vtp domain CAMPUS
vtp version 3
vtp mode server
!
! Exemple pédagogique : remplacer par un secret fort
! géré selon la politique de l'organisation.
vtp password Remplacer-Par-Un-Secret-Fort hidden
!
! Exemple d'un trunk vers SW2. Adapter le nom d'interface.
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,999
 no shutdown
!
! Exemple d'un trunk vers SW3.
interface GigabitEthernet1/0/2
 description TRUNK_VERS_SW3
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,999
 no shutdown
!
end
copy running-config startup-config
```

Cette configuration prépare SW1 à participer au domaine. Le mot de passe doit être configuré de façon cohérente sur les équipements concernés. Les mots `hidden` et `secret` dépendent des versions récentes de la plateforme ; si la syntaxe n'est pas disponible, utiliser la syntaxe documentée pour le logiciel concerné, sans exposer le secret dans des systèmes de suivi non protégés.

Avant de créer les VLANs, examiner les paramètres VTP. Le passage au rôle primaire intervient en mode privilégié, une fois le domaine et la version préparés et après confirmation que la base locale est celle que l'équipe veut diffuser.

```cisco
SW1# show vtp status
SW1# show vlan brief
SW1# vtp primary vlan
```

Sur certaines versions, l'opération peut demander une confirmation. La variante `vtp primary vlan force` ne doit être utilisée que lorsque le changement d'autorité a été évalué, que les conséquences de remplacement sont comprises et que la procédure l'autorise. Il faut confirmer dans `show vtp status` l'état primaire et l'identité correspondante avant de procéder à la modification de la base.

### 2.4. Créer les VLANs sur le primaire

Après validation du rôle primaire sur SW1, créer les VLANs nécessaires :

```cisco
configure terminal
!
vlan 10
 name USERS
!
vlan 20
 name VOICE
!
vlan 30
 name SERVERS
!
vlan 40
 name GUEST
!
vlan 999
 name NATIVE-UNUSED
!
end
copy running-config startup-config
```

Les VLANs et les noms sont des exemples. Il faut appliquer la convention d'identification de l'entreprise, limiter les VLANs aux usages réels et vérifier la compatibilité avec les autres fonctions de commutation. Le VLAN 999 est illustratif : il ne suffit pas de nommer un VLAN « native unused » pour rendre sa configuration sûre. Aucun port utilisateur ne doit être affecté à ce VLAN et les paramètres de native VLAN doivent correspondre aux deux extrémités du trunk.

Une fois la base modifiée, vérifier à nouveau le statut et la liste VLAN :

```cisco
show vtp status
show vlan brief
show interfaces trunk
```

Ensuite, vérifier sur SW2 et SW3 que les VLANs se sont propagés comme prévu. Si la base n'est pas reçue, ne pas enchaîner immédiatement d'autres changements. Contrôler le domaine, la version, le mot de passe, le mode, le trunk et les journaux.

### 2.5. Préparer un serveur secondaire et un membre client

SW2 peut être configuré en serveur VTPv3 secondaire afin de maintenir une capacité opérationnelle de reprise. SW3 peut être configuré suivant la politique retenue ; le mode client convient dans une architecture qui souhaite distribuer la base tout en empêchant les changements locaux de base partagée. Sur les plateformes compatibles, les clients VTPv3 peuvent recevoir les informations de base correspondantes, mais ils ne se comportent pas comme des serveurs primaires.

Exemple pour SW2 :

```cisco
hostname SW2
vtp domain CAMPUS
vtp version 3
vtp mode server
vtp password Remplacer-Par-Un-Secret-Fort hidden
!
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,999
 no shutdown
!
interface GigabitEthernet1/0/2
 description TRUNK_VERS_SW3
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,999
 no shutdown
end
copy running-config startup-config
```

Exemple pour SW3 en mode client :

```cisco
hostname SW3
vtp domain CAMPUS
vtp version 3
vtp mode client
vtp password Remplacer-Par-Un-Secret-Fort hidden
!
interface GigabitEthernet1/0/1
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk native vlan 999
 switchport trunk allowed vlan 10,20,30,40,999
 no shutdown
end
copy running-config startup-config
```

Dans un réseau réel, la redondance de la topologie physique et l'état de STP doivent être traités séparément. VTP ne crée pas un chemin redondant fonctionnel à lui seul. Sur SW2, ne lancer une promotion primaire qu'en cas de changement approuvé et après validation de la base locale.

### 2.6. Exemple de mode transparent ou off

Lorsque la conception exige une base VLAN locale indépendante, utiliser le mode transparent ou off selon le besoin de relais des annonces et le comportement pris en charge par la plateforme. Les commandes exactes doivent être vérifiées avant usage.

```cisco
hostname SW-EDGE
vtp domain EDGE-LOCAL
vtp version 3
vtp mode transparent
!
! Les VLANs sont gérés localement sur cet équipement.
vlan 110
 name EDGE-USERS
vlan 120
 name EDGE-VOICE
!
end
copy running-config startup-config
```

Le domaine dans cet exemple est local et n'est pas destiné à rejoindre le domaine de gestion CAMPUS. Il faut vérifier les effets du mode transparent sur la transmission de messages sur cette version. Si la politique impose que VTP ne soit ni traité ni relayé, le mode off peut mieux correspondre à l'objectif, sous réserve des commandes prises en charge.

Le mode transparent doit aussi être évalué avec les Private VLANs et d'autres fonctions spéciales. La documentation Cisco indique, pour les versions et plateformes décrites, des restrictions de mode lorsque des Private VLANs sont configurés. La recommandation est de ne pas changer le mode sans vérifier les dépendances locales.

### 2.7. Pruning : activation et vérification

Le pruning peut être envisagé lorsque la base VTP est cohérente et que le besoin de réduire le trafic diffusé sur certains trunks a été établi. Sur les plateformes qui prennent en charge la commande classique :

```cisco
configure terminal
vtp pruning
end
```

Cette configuration est typique des environnements IOS traditionnels. Le support, la portée de l'activation et les options peuvent différer sur des versions plus récentes. Vérifier la valeur et l'état opérationnel avec les commandes d'état VTP et de trunk disponibles :

```cisco
show vtp status
show interfaces trunk
show vlan brief
```

VTP pruning n'élimine pas un VLAN de la base, et n'a pas pour fonction de retirer automatiquement le VLAN de toutes les listes autorisées sur tous les trunks. Il limite certains trafics sur les trunks lorsque les conditions du mécanisme sont réunies. La liste de VLANs autorisés continue de constituer un contrôle distinct et déterministe du transport.

Les VLANs non éligibles au pruning dans la documentation Cisco courante comprennent VLAN 1, VLANs 1002 à 1005 et les VLANs de plage étendue au-delà de 1005. Il faut confirmer ce comportement sur la plateforme. Le pruning ne doit pas servir de justification pour laisser tous les VLANs autorisés sur tous les trunks.

### 2.8. Vérifier systématiquement les résultats

Après chaque modification de VTP, utiliser une matrice de validation :

| Contrôle | Commande ou méthode | Résultat attendu |
|---|---|---|
| Version et état VTP | `show vtp status` | Domaine, version, mode et révision conformes |
| Autorité primaire v3 | `show vtp status`, commande documentée pour le rôle | Le primaire attendu est identifié pour la base visée |
| Base VLAN | `show vlan brief` | VLANs et noms attendus présents |
| Trunks opérationnels | `show interfaces trunk` | Les interfaces attendues sont des trunks actifs |
| VLANs autorisés | `show interfaces trunk` | Liste allowed conforme au modèle de sécurité |
| STP | `show spanning-tree vlan <id>` | Chemin et rôles STP conformes à la topologie |
| Port d'accès | Configuration de l'interface | Poste affecté au bon VLAN et fonctions d'accès appliquées |
| Couche 3 | Vérification des SVI, routes, ACLs et tests | Connectivité attendue, sans ouverture involontaire |
| Persistance | Sauvegarde puis contrôle après maintenance prévue | Base et mode toujours cohérents après redémarrage contrôlé |

Les sorties doivent être comparées avant/après et non simplement lues de manière isolée. En environnement de production, conserver les résultats dans le ticket de changement. Une alarme de surveillance peut détecter des changements de VLAN, de trunk ou de STP, mais la surveillance n'exclut pas la validation humaine d'une opération à fort impact.

### 2.9. Sauvegarde et documentation

VTP ne dispense pas de maintenir une source de vérité pour le plan VLAN. Pour chaque VLAN, documenter l'identifiant, le nom, la fonction, les plages IP, la passerelle, les zones de sécurité, les trunks qui doivent le transporter, les ports d'accès attendus et les dépendances applicatives.

La sauvegarde doit inclure la configuration du commutateur et, lorsque la plateforme stocke la base dans un fichier séparé, la méthode de sauvegarde de ce fichier. Les systèmes d'exploitation réseau n'ont pas tous la même gestion du fichier de base VLAN ; utiliser uniquement une commande générique sans vérifier le stockage peut laisser la base non sauvegardée.

Exemples de commandes à collecter selon le modèle :

```cisco
show running-config
show startup-config
show vtp status
show vlan brief
show interfaces trunk
show spanning-tree summary
```

La sauvegarde de la base VLAN peut nécessiter une commande de fichier, une copie de la configuration ou une procédure propre à la plateforme. Le nom exact du fichier et son emplacement varient. Il faut suivre la documentation de la gamme et tester la restauration dans un environnement non productif.

### 2.10. Migrer vers VTPv3

Une migration doit commencer par un inventaire de tous les membres possibles du domaine : modèles, versions logicielles, modes actuels, domaine, mot de passe, VLANs normaux et étendus, Private VLANs, trunks et éventuelles bases MST partagées. Ensuite, valider que toutes les plateformes visées prennent en charge la version cible et que la fenêtre de changement permet une interruption si une restauration s'avère nécessaire.

Une approche rigoureuse suit ces étapes :

1. Exporter la configuration actuelle et les données d'état.
2. Comparer la base VLAN actuelle sur tous les commutateurs concernés.
3. Définir la source de vérité et le commutateur qui deviendra primaire.
4. Vérifier et mettre à jour les versions logicielles si nécessaire.
5. Configurer un mot de passe commun conformément à la politique.
6. Appliquer VTPv3 selon une séquence compatible avec la documentation constructeur.
7. Désigner explicitement le primaire de l'instance VLAN et vérifier son état.
8. Contrôler la propagation et les révisions sur les membres.
9. Valider les trunks, STP, les ports d'accès, les passerelles et les applications.
10. Documenter la procédure de retour arrière et les restrictions de compatibilité.

Il ne faut pas mélanger dans le même domaine des équipements dont la version et la capacité de traitement ne sont pas compatibles sans avoir validé le comportement prévu. Cisco indique que VTPv3 n'accepte pas la configuration provenant d'équipements VTPv1/v2 comme source d'informations de configuration valide. La transition n'est donc pas équivalente à une simple mise à jour de l'ensemble des commutateurs : elle demande un plan de coexistence ou une migration coordonnée.

> **Astuce :** Avant tout raccordement d'un commutateur de remplacement, collecte au minimum `show vtp status`, `show vlan brief` et `show interfaces trunk`, puis compare le domaine, la version, la révision, la base VLAN et les ports de trunk à l'état de référence. Pour VTPv3, ajoute l'identification du primaire et une preuve que la base locale est celle qui doit faire autorité. La préparation hors ligne d'un équipement neuf ou réutilisé est souvent plus rapide et beaucoup moins risquée qu'une correction en urgence après propagation d'une mauvaise base.

---

## 3. Dépannage et Sécurité

### 3.1. Méthode de diagnostic par couches

Lorsqu'un VLAN ne fonctionne pas, évite de conclure immédiatement à une panne VTP. Le diagnostic doit isoler successivement la définition VLAN, la diffusion VTP, le trunk, la liste des VLANs autorisés, l'affectation du port, STP et la couche 3.

**Étape 1 : vérifier la base locale.** `show vlan brief` permet de déterminer si le VLAN existe localement. Si le VLAN est absent, vérifier le mode VTP et les annonces ; si la définition existe, passer à la vérification de trunk et de port.

**Étape 2 : vérifier l'état VTP.** `show vtp status` doit afficher le domaine, la version, le mode, la révision et les informations prises en charge par la plateforme. Pour VTPv3, vérifier qui est primaire pour l'instance concernée. Une valeur de révision différente peut être attendue lors d'une transition ou selon le mode ; elle doit être interprétée avec la topologie et les règles de la version, pas utilisée comme unique verdict.

**Étape 3 : vérifier le transport.** `show interfaces trunk` permet de déterminer si la liaison est réellement en trunk et quels VLANs sont autorisés, actifs et en forwarding selon la présentation du logiciel. Les commandes exactes de sous-catégories varient entre IOS classique, IOS XE et autres systèmes Cisco.

**Étape 4 : vérifier STP et les ports.** Examiner le rôle et l'état STP du VLAN, puis l'affectation du port utilisateur. Le port doit être opérationnel et associé au VLAN attendu. Les fonctions de sécurité de port, les ACLs et les paramètres de voix doivent être inclus dans l'analyse.

**Étape 5 : contrôler la couche 3.** Si la communication inter-VLAN est attendue, vérifier l'interface VLAN/SVI, son état, l'adressage IP, le routage, les ACLs et les routes de retour.

Cette séquence évite de confondre synchronisation de configuration et transfert effectif de trafic.

### 3.2. Aucun changement VLAN ne se propage

Si le VLAN est créé sur le serveur mais n'apparaît pas sur les membres, vérifier dans cet ordre :

1. le domaine VTP est-il exactement identique ?
2. la version est-elle compatible et correctement activée ?
3. le mode local permet-il de participer à la réception de la base ?
4. le mot de passe est-il présent et identique si utilisé ?
5. les trunks sont-ils opérationnels entre les équipements ?
6. l'annonce est-elle reçue et acceptée ?
7. VTPv3 utilise-t-il le primaire prévu pour la base VLAN ?
8. la plate-forme prend-elle en charge la plage et le type de VLAN concernés ?

Une cause fréquente est l'hypothèse erronée selon laquelle un serveur en mode server peut toujours pousser des modifications. Sous VTPv3, il faut contrôler l'état primaire. Une autre cause est la présence d'un trunk incorrect ou d'un mot de passe oublié sur un commutateur nouvellement ajouté.

Évite de modifier plusieurs paramètres simultanément. Un changement coordonné d'une seule variable à la fois permet d'observer l'effet et de conserver un diagnostic fiable. Toute modification doit être accompagnée d'une vérification de la base, du trunk et des journaux.

### 3.3. Base incohérente ou révision inattendue

Une différence de révision ne signifie pas toujours que la configuration est erronée. Elle peut refléter un état transitoire, une séparation de domaines, un mode transparent ou des mécanismes propres à la version. Cependant, une révision inattendue associée à une base VLAN incomplète est un signal d'alerte.

En VTP v1/v2, il faut notamment rechercher un commutateur récemment raccordé, un changement de domaine, une réinitialisation, une restauration de base ou une modification effectuée sur un équipement inattendu. Avant toute correction, sauvegarder les états restants et reconstituer quel équipement a émis la dernière mise à jour acceptée.

Ne pas résoudre automatiquement un écart en changeant le nom de domaine ou en recréant les VLANs. Ces opérations peuvent modifier l'état de synchronisation et produire davantage de changements. D'abord, identifier la base autorisée à faire référence, comparer les VLANs attendus et actuels, puis suivre la procédure de récupération adaptée à la version VTP.

Avec VTPv3, vérifier le serveur primaire et l'état de la base de l'instance. Une promotion de primaire doit être planifiée, et `force` doit être réservé à un cas dans lequel l'écrasement des informations concurrentes a été explicitement accepté. Si l'origine d'une base incorrecte est inconnue, isoler le commutateur suspect avant de poursuivre les annonces.

### 3.4. VLAN présent, mais absent du trunk

Le fait qu'un VLAN existe dans la base VTP ne garantit pas qu'il est autorisé sur tous les trunks. Utiliser :

```cisco
show interfaces trunk
show running-config interface GigabitEthernet1/0/1
show vlan brief
```

Contrôler séparément : le mode opérationnel du trunk, la liste des VLANs autorisés, les VLANs actifs, les VLANs que STP permet de transférer et le VLAN natif. Une liste allowed VLAN définie manuellement peut ne pas inclure un nouveau VLAN distribué par VTP. C'est souvent une mesure de sécurité intentionnelle : la base peut être commune alors que chaque trunk ne transporte qu'un sous-ensemble des VLANs nécessaires.

Ne pas remplacer systématiquement une liste stricte par `all` pour réparer rapidement une panne. Une telle modification peut exposer des VLANs à des commutateurs ou segments qui ne doivent pas les transporter. Mettre à jour la liste conformément à la matrice d'autorisation et vérifier les deux extrémités du trunk.

### 3.5. Problèmes liés au mode transparent

Un commutateur transparent maintient sa propre base VLAN. Il ne doit donc pas être dépanné comme un client dont la base devrait automatiquement refléter toute mise à jour reçue. Le relais des annonces dépend de la version et de la plateforme : dans certains contextes, les annonces peuvent être transférées sans que la base locale soit modifiée ; en mode off, le relais n'est pas effectué.

Vérifier le mode réel avec `show vtp status`, les VLANs avec `show vlan brief`, puis le trunk. Si le commutateur devait être autonome, l'absence de synchronisation peut être normale. Si le rôle prévu était client, il faut examiner la configuration du mode, la version, le domaine et les restrictions.

Une base locale peut être perdue ou restaurée différemment après un redémarrage selon la manière dont le mode, le domaine et les VLANs sont stockés. Cette particularité rend les tests de persistance indispensables. Il faut suivre la documentation propre à la plate-forme pour confirmer que les VLANs créés localement et le mode transparent sont effectivement sauvegardés et restaurés comme prévu.

### 3.6. Pruning inattendu ou trafic de broadcast excessif

Si certains trafics d'un VLAN n'apparaissent pas sur un trunk, vérifier si le pruning est activé et si le VLAN est éligible. Examiner ensuite la liste allowed VLAN, l'état du trunk, le voisinage aval et les informations STP. Un flux absent peut résulter d'une restriction de trunk plutôt que du pruning.

Si les broadcasts sont plus importants que prévu, vérifier d'abord la topologie, les boucles, les mécanismes de spanning tree, les ports d'accès et la portée réelle du VLAN. Le pruning ne corrige pas une boucle de couche 2 et ne remplace pas STP. Il réduit certains transports inutiles ; il ne doit pas être utilisé comme mécanisme principal pour limiter les domaines de broadcast.

L'activation du pruning exige une observation post-changement. Attendre le délai de convergence documenté pour la plateforme, puis vérifier l'impact sur les flux requis. Les VLANs non éligibles au pruning et les limites du mécanisme doivent être pris en compte dans l'analyse.

### 3.7. Sécuriser les nouveaux commutateurs

Tout équipement neuf, de remplacement ou de laboratoire doit passer par une procédure d'intégration hors réseau avant de rejoindre les trunks de production. Cette procédure devrait comprendre :

- l'identification du modèle et de la version logicielle ;
- la remise à niveau logicielle selon les standards ;
- la collecte du statut VTP et de la base VLAN ;
- la vérification de la version, du domaine, du mode et de la révision ;
- la suppression des paramètres hérités inutiles selon la procédure approuvée ;
- la configuration explicite des trunks et la limitation des VLANs autorisés ;
- la mise en place des identifiants d'administration et de la journalisation ;
- la validation de la sauvegarde de configuration et de base VLAN ;
- un test en laboratoire avant connexion en production.

Il ne faut pas dépendre d'un avertissement visuel ou du fait que le commutateur est réputé « neuf ». Les équipements reconditionnés ou réutilisés peuvent conserver un état logiciel ou une base de VLAN antérieure. Une procédure d'intégration est plus fiable qu'une supposition sur l'état initial.

### 3.8. Contrôle des trunks et réduction du domaine de diffusion

Les trunks doivent être configurés explicitement là où un trunk est nécessaire. Les ports inutilisés devraient être désactivés ou placés dans une configuration de quarantaine conforme à la politique de l'entreprise. La négociation automatique de trunk doit être évaluée et désactivée lorsqu'elle n'est pas nécessaire, en tenant compte de la plateforme et des voisins.

La liste des VLANs autorisés doit être définie selon le besoin réel du lien. Un trunk entre distribution et accès peut transporter un ensemble différent de VLANs qu'un trunk vers un serveur, un hyperviseur ou un commutateur d'un autre domaine. Un modèle strict facilite l'audit et réduit le risque d'extension involontaire d'un VLAN sensible.

Une bonne pratique consiste à documenter la matrice des trunks : interface locale, voisin, type de lien, native VLAN, liste des VLANs autorisés, fonction, dépendances STP et justification. L'automatisation peut comparer la configuration courante à ce modèle et générer des alertes si un trunk transporte un VLAN non prévu.

### 3.9. Sauvegarde et récupération après une propagation incorrecte

Si une base VLAN incorrecte a été propagée, arrêter les changements supplémentaires et éviter de connecter d'autres commutateurs susceptibles de la redistribuer. L'équipe doit établir quelle base représente la référence validée et isoler les équipements à l'origine du changement suspect.

La récupération doit commencer par les sauvegardes de la base et la configuration. Restaurer l'ensemble des VLANs ne suffit pas si les ports, trunks, interfaces SVI ou règles de sécurité ont eux aussi été modifiés. Il faut comparer les états actuels et attendus, restaurer dans un ordre défini, puis valider l'ensemble des chemins et services affectés.

Pour VTPv1/v2, le traitement du numéro de révision et la séquence de resynchronisation doivent suivre les recommandations de la plateforme. Une action destinée à remettre le compteur à zéro peut modifier le domaine et affecter la propagation. Pour VTPv3, la base et l'état primaire doivent être vérifiés avant toute prise de contrôle. Ne pas lancer une promotion forcée en pleine incertitude sans identifier quel jeu de données doit être conservé.

Après la restauration, confirmer la base sur tous les commutateurs participants, les listes de trunks, les états STP, les ports d'accès et la connectivité des applications. Fermer l'incident seulement lorsque les contrôles techniques et les tests métiers confirment le retour au service.

### 3.10. Journalisation, surveillance et audit

Les changements de VLAN et de trunk doivent être surveillés. En fonction des outils et de la plate-forme, utiliser les journaux système, les mécanismes d'archivage de configuration, les notifications SNMP ou la télémétrie disponible pour repérer les événements pertinents. La surveillance doit inclure l'état du domaine, les révisions, les changements de rôle primaire, les nouveaux VLANs, les suppressions et les modifications de trunk.

Les sauvegardes de configuration peuvent être comparées automatiquement pour déterminer si la liste des VLANs autorisés a été élargie, si une interface a changé de mode ou si le domaine VTP a été modifié. Les alertes doivent être liées à une procédure de réponse afin d'éviter qu'elles ne deviennent un bruit ignoré par les opérateurs.

Un audit périodique doit contrôler :

- que chaque domaine VTP dispose d'une source d'autorité connue ;
- que la version et les modes sont conformes au standard ;
- que les équipements anciens et non compatibles ont une stratégie explicite ;
- que chaque trunk transporte uniquement les VLANs requis ;
- que la VLAN native est cohérente et documentée ;
- que les VLANs de gestion, utilisateurs, serveurs, invités et voix sont séparés conformément au design ;
- que les sauvegardes sont récentes et restaurables ;
- que les changements sont attribuables à un administrateur et associés à un ticket.

### 3.11. Arbre de décision rapide

```text
                 VLAN en panne ou absent
                            |
                            v
                Le VLAN existe localement ?
                     /             \
                   NON             OUI
                   |                |
                   v                v
           Vérifier VTP,       Le trunk le transporte ?
           mode, domaine,           /       \
           version, mot de passe   NON       OUI
           et primaire             |         |
                                  v          v
                         Corriger la liste   Vérifier STP,
                         allowed VLAN        port, sécurité,
                                             SVI et routage

   Ne pas utiliser VTP comme explication unique avant
   d'avoir vérifié toute la chaîne de commutation.
```

### 3.12. Scénario expert : intégration d'un commutateur de secours

Une entreprise dispose d'un domaine VTPv3 CAMPUS avec un primaire actif et un serveur secondaire de secours. Un commutateur en réserve a été utilisé dans un laboratoire ; il est ensuite présenté comme remplacement d'un commutateur d'accès en panne. Le risque n'est pas limité aux ports du commutateur : ses paramètres VTP, son domaine, sa version et son historique peuvent avoir des effets sur le plan de contrôle s'il est raccordé sans préparation.

La procédure doit commencer par une inspection en isolation. L'administrateur vérifie la version logicielle, le mode VTP, la base VLAN, les éventuelles fonctions Private VLAN, la révision, l'état d'instance et les paramètres de mot de passe. Il compare les résultats au standard cible. Il prépare ensuite les trunks avec une liste de VLANs minimale et détermine si le commutateur doit participer à VTP ou fonctionner en mode transparent/off.

Le choix du rôle est une décision d'architecture. S'il s'agit d'un membre VTPv3, il doit être configuré avec la version, le domaine et le secret adaptés, puis synchronisé selon le mécanisme pris en charge. Il ne doit pas devenir primaire par accident. Si l'architecture locale ne nécessite pas la participation au domaine, un mode transparent ou off peut être préférable, mais la base VLAN locale doit être préparée et sauvegardée.

Après l'intégration physique, l'équipe vérifie les trunks, les VLANs autorisés, l'état STP, les ports d'accès et les passerelles. Des tests sont exécutés depuis des postes représentatifs, y compris les VLANs de gestion et de services critiques. L'opération est terminée seulement quand le trafic fonctionne et que la base de référence n'a pas été modifiée au-delà de ce qui était prévu.

### 3.13. Scénario expert : changement de primaire VTPv3

Le changement de primaire peut être nécessaire pour maintenance, mise à niveau, remplacement matériel ou reprise après panne. Il ne doit pas être confondu avec l'élection STP ou le changement de routeur actif : le rôle primaire VTP concerne l'autorité sur la base de données de l'instance.

Avant le changement, relever la base courante, le statut primaire, l'état de la synchronisation, les versions de tous les membres et les dépendances liées aux VLANs. Vérifier également qu'aucune opération de création, suppression ou renommage n'est en cours. Les changements simultanés dans un domaine conçu autour d'une source autorisée peuvent créer des divergences difficiles à expliquer.

La procédure d'exploitation doit documenter la commande de transfert ou de prise de rôle adaptée au logiciel. Après la transition, vérifier l'identité du primaire, la réception des annonces, la base des membres et la capacité de modification attendue. Si l'ancien primaire revient, vérifier comment la plateforme traite la situation avant de lui permettre d'effectuer de nouvelles modifications.

En présence d'une option `force`, analyser le risque de remplacement de bases concurrentes. La commande ne devrait être exécutée qu'avec une validation explicite, une sauvegarde exploitable et un périmètre d'impact connu. Une reprise sûre est une procédure reproductible, pas une commande mémorisée sans contexte.

### 3.14. Synthèse opérationnelle et critères d'acceptation

VTP est correctement exploité lorsque la base VLAN fait autorité clairement, que les versions des équipements sont compatibles, que les trunks transportent les annonces attendues, que les mises à jour sont acceptées par les bons équipements et que les changements sont vérifiables et réversibles.

Un changement VTP ne peut être validé seulement parce que `show vtp status` affiche le domaine attendu. Il faut également comparer la base VLAN, les trunks, STP, l'affectation des ports, les SVI, les routes, les ACLs et les applications. Cette vérification multi-couche évite d'attribuer au protocole une panne liée à une liste de VLANs autorisés ou à une interface de couche 3.

La politique de sécurité doit réduire le domaine de confiance : chaque commutateur ne doit participer qu'aux domaines qu'il doit connaître ; les trunks doivent être explicites ; les secrets doivent être protégés ; les VLANs transportés doivent être limités ; les changements doivent être journalisés ; la base doit être sauvegardée et la reprise doit être testée.

> **Danger :** Une annonce VTP non attendue peut avoir un effet de portée supérieure à l'interface qui la reçoit. En particulier dans les environnements v1/v2, une base provenant d'un commutateur mal préparé peut être considérée comme plus récente en fonction du numéro de révision et être propagée dans le domaine. Dans VTPv3, une mauvaise utilisation du rôle primaire ou de l'option `force` peut également écraser des informations concurrentes. Un VLAN supprimé de la base ou absent d'un trunk peut provoquer une interruption de service pour plusieurs applications. Isole les équipements inconnus, contrôle la base et l'autorité avant raccordement, sauvegarde les données, limite les trunks et applique une procédure de changement approuvée.

## Points à retenir

- **VTP distribue des informations de base VLAN ; il ne remplace ni les trunks 802.1Q, ni STP, ni l'affectation des ports, ni le routage inter-VLAN.** La présence d'un VLAN dans la base n'assure pas son transport sur chaque lien ou sa connectivité de bout en bout.
- **Le numéro de révision indique une version de la base, pas sa qualité ni son autorité.** En VTPv1/v2, un commutateur mal préparé peut provoquer une synchronisation destructive. VTPv3 introduit le rôle primaire et un contrôle renforcé des modifications, mais demande une procédure d'exploitation explicite.
- **La sécurité VTP repose sur plusieurs contrôles.** Valide version, mode, domaine, mot de passe et rôle primaire ; limite chaque trunk aux VLANs nécessaires ; conserve des sauvegardes de configuration et de base VLAN ; vérifie STP et les services après chaque modification.

## Références techniques

- Cisco, *VLAN Configuration Guide — Configure VTP*, guide IOS XE mis à jour le 17 juillet 2026 : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vtp.html
- Cisco, *Understand VLAN Trunk Protocol (VTP)*, document de support mis à jour le 2 avril 2025 : https://www.cisco.com/c/en/us/support/docs/lan-switching/vtp/10558-21.html
- Cisco, *Configuring VTP*, guide pour IOS 15.2(7)E : https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst_digital_building_series_switches/software/15-2_7_e/configuration_guide/b_1527e_consolidated_cdb_cg/m_1525ex_vlan_vtp_cg.html

Les commandes, capacités et valeurs par défaut cités dans ce cours sont des exemples issus de la documentation Cisco. Vérifier leur disponibilité sur le modèle et la version logicielle réellement déployés avant toute utilisation en production.