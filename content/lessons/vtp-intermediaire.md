# VTP et gestion des VLANs - Intermédiaire

**Niveau :** Intermédiaire

La segmentation par VLAN constitue l’un des fondements des réseaux Ethernet d’entreprise. Elle permet de séparer logiquement des domaines de broadcast sans exiger un commutateur physique distinct pour chaque groupe d’utilisateurs. Cette séparation facilite l’organisation des postes, des serveurs, de la téléphonie IP, des imprimantes, des équipements d’administration et des systèmes invités. Elle contribue aussi à la maîtrise des flux, mais ne remplace pas à elle seule un pare-feu, des ACL ou une politique de contrôle d’accès. Une fois les VLAN définis, les commutateurs doivent transporter les trames des VLAN concernés à travers les liens inter-switch et maintenir une base de données cohérente.

Le VLAN Trunking Protocol (VTP) est un protocole propriétaire Cisco conçu pour diffuser et synchroniser des informations de configuration VLAN entre des commutateurs appartenant à un même domaine VTP. Au lieu de créer séparément chaque VLAN sur plusieurs équipements, un administrateur peut, dans une architecture compatible, modifier la base VLAN sur un serveur VTP et laisser le protocole propager les changements aux autres commutateurs du domaine. Cette centralisation réduit certaines tâches répétitives, mais introduit également une dépendance opérationnelle : une mauvaise base de VLAN peut se propager au-delà du commutateur où elle a été créée.

VTP ne transporte pas les trames des utilisateurs et ne remplace pas le trunking IEEE 802.1Q. Il transporte des informations de gestion de la base VLAN à l’intérieur d’un domaine compatible. Les trunks, quant à eux, transportent les trames de plusieurs VLAN entre commutateurs. Les deux fonctions sont complémentaires, mais distinctes : la présence d’un trunk ne garantit pas la propagation VTP, et la réception d’une annonce VTP ne garantit pas qu’un VLAN soit autorisé sur chaque trunk ni qu’il existe un port d’accès actif dans ce VLAN.

Dans un réseau intermédiaire, l’enjeu n’est donc pas seulement de connaître les commandes `vtp mode`, `vtp domain` ou `vtp version`. Il faut comprendre la base VLAN, les rôles serveur/client/transparent, le numéro de révision, les mécanismes d’authentification, les limites propres à chaque version, le VTP pruning et ses différences avec la liste de VLAN autorisés sur un trunk. Une conception robuste commence par le choix explicite d’un mode de gestion, se poursuit par une validation du plan de VLAN et s’achève par des contrôles opérationnels et une procédure de changement maîtrisée.

> **Analogie** : Imagine une entreprise possédant plusieurs bâtiments. Chaque équipe — comptabilité, support, développement et visiteurs — dispose de zones de circulation distinctes. Les VLAN sont les règles qui définissent ces zones. Les trunks sont les couloirs capables de transporter des personnes de plusieurs zones entre bâtiments. VTP joue le rôle d’un registre centralisé de la signalisation : il indique aux bâtiments quels groupes existent et quels identifiants leur sont attribués.
>
> Dans une organisation utilisant VTP en mode serveur/client, le commutateur serveur publie les modifications de la base et les commutateurs clients mettent leur base à jour à partir des informations reçues. Cela évite à l’administrateur de recopier chaque création de VLAN sur tous les commutateurs. Mais cette centralisation se comporte aussi comme un registre partagé : si une entrée est supprimée ou si une base incorrecte devient la référence acceptée, plusieurs bâtiments peuvent adopter la même mauvaise information.
>
> Le numéro de révision VTP ressemble à un compteur de version attaché au registre. Dans les versions 1 et 2, un commutateur du même domaine et possédant une révision plus élevée peut, dans certaines conditions, provoquer le remplacement de la base VLAN des autres membres. C’est pourquoi un ancien commutateur ou un équipement de laboratoire ne doit pas être raccordé à la production sans avoir contrôlé son domaine, sa version, son mode et sa révision. VTP version 3 ajoute un contrôle plus strict de la base VLAN au moyen d’un serveur primaire pour les modifications, mais il ne dispense pas de procédures de changement et de validation.
>
> Enfin, le registre VLAN et les couloirs ne sont pas la même chose. Un VLAN peut être correctement défini dans la base VTP mais absent de la liste des VLAN autorisés sur un trunk, ou encore ne pas avoir de port utilisateur actif derrière un commutateur distant. Dans ces cas, la synchronisation de la base ne suffit pas à assurer la connectivité. L’administrateur doit contrôler séparément le domaine VTP, l’existence du VLAN, l’état du trunk, la liste des VLAN autorisés et l’affectation des ports.

---

## 1. La théorie et les algorithmes

### 1.1. VLAN, domaine de broadcast et base VLAN

Un VLAN (*Virtual Local Area Network*) est une segmentation logique de niveau 2. Les équipements affectés à un même VLAN appartiennent au même domaine de broadcast de couche 2, même s’ils sont reliés à des commutateurs différents. Deux VLAN différents sont séparés au niveau Ethernet : pour communiquer entre eux, ils ont normalement besoin d’un équipement de couche 3, tel qu’un routeur ou un commutateur multicouche.

La configuration VLAN comprend au minimum un identifiant numérique, généralement appelé VLAN ID, et peut également contenir un nom. Sur de nombreux commutateurs Cisco, les VLAN usuels sont dans la plage normale 1–1005. Les VLAN 1002 à 1005 sont réservés à des usages historiques sur les plateformes qui les prennent en charge. Les VLAN 1006 à 4094 constituent la plage étendue. Les fonctionnalités exactes et les limites de configuration varient selon le modèle et la version logicielle.

| Élément | Fonction | Exemple | Vérification habituelle |
|---|---|---|---|
| VLAN ID | Identifie le VLAN | `20` | `show vlan brief` |
| Nom du VLAN | Facilite l’administration | `COMPTA` | `show vlan brief` |
| Port d’accès | Affecte un port utilisateur à un VLAN | `Gi1/0/10` dans le VLAN 20 | `show vlan brief`, `show interfaces switchport` |
| Trunk 802.1Q | Transporte plusieurs VLAN sur un lien | `Gi1/0/48` | `show interfaces trunk` |
| Base VLAN | Répertorie les VLAN connus du commutateur | VLAN 10, 20 et 30 | `show vlan`, `show vtp status` |
| Domaine VTP | Groupe logique d’échange VTP | `CAMPUS-ENTREPRISE` | `show vtp status` |

La création du VLAN n’affecte pas automatiquement tous les ports. Un port d’accès doit être configuré dans le VLAN attendu. Pour une liaison inter-switch, le trunk doit transporter le VLAN et le commutateur distant doit disposer d’une configuration cohérente. Il faut donc considérer l’existence du VLAN, son transport et l’affectation des terminaux comme trois tâches différentes.

### 1.2. Rôle de VTP

VTP diffuse des informations de gestion VLAN dans un domaine VTP. Selon la version et le mode, un commutateur peut annoncer les informations de sa base, recevoir les mises à jour des autres équipements et/ou modifier localement la base. VTP ne remplace pas les protocoles de découverte de voisinage, le protocole de trunking ni le mécanisme de transfert Ethernet.

Un domaine VTP est notamment caractérisé par son nom, sa version, son mode et, lorsque cette fonction est activée, son mot de passe. Pour que les commutateurs puissent échanger et accepter les mises à jour, les paramètres doivent être compatibles et les messages doivent pouvoir traverser les liens appropriés. La version, le mot de passe et le mode doivent donc être vérifiés sur l’ensemble du chemin entre les équipements concernés.

VTP est surtout utile dans les environnements Cisco où un grand nombre de commutateurs doivent partager une base VLAN commune. Dans un réseau réduit, dans une architecture multi-constructeurs ou dans un environnement qui exige un contrôle local explicite, les modes transparent ou off peuvent être préférables. Le choix dépend des exigences de gouvernance, du risque accepté, de la compatibilité des équipements et des procédures de changement.

### 1.3. VTP et trunk 802.1Q : deux mécanismes distincts

Un trunk est un lien de couche 2 capable de transporter plusieurs VLAN. L’encapsulation 802.1Q insère une étiquette dans les trames concernées, afin de conserver l’identification du VLAN au-delà du lien physique. Le VLAN natif est traité sans étiquette sur les trunks 802.1Q selon le comportement courant Cisco ; son identifiant doit être cohérent aux deux extrémités afin d’éviter les erreurs et les risques de sécurité associés.

VTP utilise les liens inter-switch compatibles pour transmettre ses annonces, mais la gestion VTP et la liste de VLAN transportés ne sont pas identiques. Un VLAN peut exister dans la base locale tout en étant retiré de la liste autorisée d’un trunk. À l’inverse, un VLAN mentionné dans la liste autorisée peut ne pas être disponible pour le transfert si la base locale ne le contient pas ou si sa présence n’est pas prise en charge par la plateforme.

Le contrôle du transport d’un VLAN s’effectue généralement avec :

```cisco
show interfaces trunk
show interfaces GigabitEthernet1/0/48 switchport
show vlan brief
```

Ces commandes répondent à des questions différentes : quels liens fonctionnent en trunk, quels VLAN sont autorisés/actifs sur les liens et quels VLAN existent dans la base du commutateur. Une bonne procédure de dépannage croise ces résultats au lieu de supposer qu’un statut VTP correct garantit le passage des trames.

### 1.4. Fonctionnement général des annonces VTP

VTP utilise des annonces de contrôle pour informer les commutateurs du domaine des états et des modifications de la base VLAN. Les annonces sont échangées sur les liens compatibles et transportent des informations permettant au récepteur de décider s’il doit accepter les données. Le comportement détaillé dépend de la version VTP et de la plateforme.

Dans un scénario classique en VTP v1 ou v2, lorsqu’un administrateur modifie la base VLAN sur un serveur, le numéro de révision de configuration augmente et les annonces correspondantes sont propagées. Les autres commutateurs du même domaine comparent les informations reçues aux leurs. Une annonce plus récente peut être acceptée et entraîner une mise à jour de la base locale. Il s’agit d’une logique de synchronisation distribuée : les commutateurs n’ont pas besoin d’être configurés un par un, mais la cohérence dépend de paramètres communs et de la bonne provenance des annonces.

Le numéro de révision n’est pas un compteur de sécurité. Il ne prouve pas qu’une base est correcte, approuvée ou issue du serveur prévu. En particulier en VTP v1/v2, la valeur élevée indique une version de base considérée comme plus récente dans les conditions de comparaison du protocole ; elle ne signifie pas que son contenu est meilleur. Cette distinction explique le risque connu lors du raccordement d’un commutateur portant une révision élevée.

La propagation peut aussi être interrompue par des trunks absents, une incompatibilité de domaine, une version non compatible, un mot de passe erroné ou un fonctionnement en mode transparent/off. Les annonces VTP et la circulation des trames utilisateurs sont deux plans de fonctionnement distincts qui doivent être contrôlés séparément.

### 1.5. Les modes VTP

Les modes classiques sont serveur, client et transparent. Certaines plateformes fournissent également le mode off. Les détails exacts varient selon la version VTP, mais les fonctions générales sont les suivantes.

| Mode | Gestion locale de la base VLAN | Réception/propagation VTP | Utilisation typique |
|---|---|---|---|
| Server | Peut modifier la base dans les limites de la version | Annonce les modifications et participe à la synchronisation | Point de gestion VLAN d’un domaine VTP |
| Client | Ne permet normalement pas de créer/supprimer les VLAN dans le modèle classique | Reçoit et utilise les mises à jour du domaine | Commutateur d’accès administré depuis le domaine |
| Transparent | Gestion VLAN locale | Ne synchronise pas sa base locale avec le domaine ; peut relayer des annonces selon version et plateforme | Contrôle local ou frontière administrative |
| Off | Gestion locale | Ne participe pas à la propagation VTP ; comportement de relais selon implémentation | Réduire l’exposition VTP lorsque la plateforme le permet |

Le mode serveur ne doit pas être confondu avec le rôle de serveur primaire VTP v3. En VTP v1/v2, le serveur peut modifier les VLAN et diffuser la base. En VTP v3, les équipements configurés en mode server peuvent avoir un état secondaire ; une opération de promotion en primaire est nécessaire pour effectuer certaines mises à jour de la base concernée. Ce contrôle aide à éviter que plusieurs commutateurs ne publient des modifications concurrentes.

Le mode transparent est utile lorsqu’on souhaite conserver une gestion VLAN localement indépendante. Les modifications réalisées sur un commutateur transparent ne sont pas propagées comme modifications de sa propre base dans le domaine. Toutefois, les détails de transfert des annonces VTP en transit dépendent de la version et de la plate-forme : il ne faut pas extrapoler un comportement observé sur un modèle à tous les modèles Cisco.

Le mode off est également à considérer avec prudence : son existence et ses effets exacts dépendent du système d’exploitation réseau. Dans un guide d’exploitation, il faut confirmer les possibilités avec la commande de consultation de la plateforme plutôt que de supposer que tous les commutateurs offrent exactement les mêmes options.

### 1.6. VTP version 1, version 2 et version 3

La version VTP doit être choisie selon les équipements et les fonctionnalités nécessaires. Les versions ne doivent pas être mélangées sans vérifier la compatibilité et le comportement de chaque modèle.

| Fonction | VTP v1 | VTP v2 | VTP v3 |
|---|---|---|---|
| Propagation des VLAN de plage normale | Oui | Oui | Oui |
| Propagation des VLAN étendus 1006–4094 | Non dans le mécanisme v1 | Non dans le mécanisme v2 | Prise en charge sur plateformes compatibles |
| Gestion du serveur primaire | Non | Non | Oui, pour les bases VTP concernées |
| Authentification améliorée | Non au même niveau que v3 | Non au même niveau que v3 | Options supplémentaires selon plateforme |
| Prise en charge de bases MST | Non | Non | Possible sur plateformes compatibles |
| Risque lié à une révision élevée | Présent | Présent | Mécanismes renforcés, contrôle primaire |

VTP v1 et v2 ne sont pas considérées comme interopérables pour la synchronisation d’une même base dans un domaine où les équipements ne sont pas configurés de manière compatible. Cisco recommande de valider la version de tous les commutateurs du domaine avant de modifier le paramètre.

VTP v3 prend en charge les VLAN étendus sur les plateformes adaptées. Il introduit également une gestion du serveur primaire pour empêcher qu’une modification de base soit publiée sans prise de contrôle explicite. Cette fonction réduit le risque de modification accidentelle, mais le serveur primaire n’est pas une sauvegarde de la configuration et ne garantit pas que chaque modification soit correcte.

Dans VTP v3, le rôle primaire est opérationnel et peut être perdu après un redémarrage ou un changement de paramètres de domaine, selon la plateforme et la version. La procédure d’exploitation doit donc inclure la vérification du rôle avant toute modification. Il faut toujours valider la disponibilité des commandes et la syntaxe sur l’équipement ciblé.

Référence technique Cisco : [VLAN Configuration Guide – Configure VTP](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vtp.html).

### 1.7. Le numéro de révision et le risque de remplacement de la base

Le numéro de révision de configuration VTP est l’un des éléments les plus importants pour l’exploitation des versions 1 et 2. Lorsqu’un changement affecte la base VLAN, la révision augmente. Les commutateurs du domaine utilisent cette valeur dans leur logique de synchronisation.

Considérons un domaine de production dont la base possède la révision 28 et comprend les VLAN 10, 20, 30 et 40. Un ancien commutateur de laboratoire est raccordé au réseau. Il possède le même nom de domaine et une révision 73, mais sa base ne contient que les VLAN 1 et 99. Selon la version, le mode, le mot de passe et les conditions de propagation, ses annonces peuvent conduire les autres équipements VTP v1/v2 à accepter sa base plus récente et à perdre les informations VLAN attendues.

```text
Domaine de production VTP v1/v2

  Base de référence                 Commutateur de laboratoire
  Révision : 28                     Révision : 73
  VLAN : 10,20,30,40                VLAN : 1,99
          |                                  |
          +--------------- trunk ------------+
                           |
                           v
            Annonce à révision supérieure reçue
                           |
                           v
            Risque de remplacement de la base
            sur des équipements du domaine
```

Ce scénario peut entraîner la disparition de VLAN, l’isolement de groupes d’utilisateurs ou une interruption de services dépendant de ces VLAN. Les effets exacts peuvent dépendre du modèle et de l’état des commutateurs. Il s’agit néanmoins d’un risque d’exploitation important qui justifie une procédure systématique avant le raccordement d’un nouvel équipement.

Avant de connecter un commutateur à un domaine VTP v1/v2 existant, il faut vérifier son `vtp domain`, son mode, sa version, son mot de passe et sa révision. La procédure de remise à zéro de révision doit être adaptée à la plateforme : on ne doit pas appliquer aveuglément une ancienne méthode `delete vlan.dat` ou un redémarrage sans sauvegarde ni validation. Certaines plateformes utilisent une base VLAN persistante, et les procédures disponibles peuvent être différentes.

En VTP v3, la fonction serveur primaire apporte une protection supplémentaire contre la publication concurrente d’une base. Elle ne dispense pas de vérifier le commutateur, la version, le domaine, le rôle primaire et le contenu exact de la base avant une opération.

### 1.8. Domaine VTP et mot de passe

Le nom du domaine VTP regroupe logiquement les équipements censés partager une base VLAN. Il doit être cohérent entre les commutateurs qui doivent échanger les informations correspondantes. Une différence de nom peut empêcher la synchronisation attendue, même si le lien physique fonctionne et qu’un trunk est établi.

Le mot de passe VTP, lorsqu’il est activé, permet de vérifier l’authenticité des annonces selon les mécanismes de la version et de l’implémentation. Le mot de passe doit être configuré de manière cohérente sur les équipements concernés. Une valeur différente peut empêcher l’acceptation des mises à jour.

VTP v3 propose des options d’authentification améliorées, dont des formes `hidden` ou `secret` sur certaines plateformes. Les détails de stockage et d’affichage diffèrent de la configuration classique. Il faut suivre la documentation correspondant exactement au système IOS/IOS XE exploité.

Le mot de passe ne doit pas être réutilisé comme secret universel d’administration. Il doit être géré dans un coffre ou un système approuvé par l’organisation, documenté et modifié selon les procédures prévues. Un mot de passe VTP n’empêche pas toutes les erreurs de configuration et ne remplace pas la protection physique des ports, les mécanismes d’administration sécurisée ni le filtrage des annonces.

### 1.9. VTP pruning : réduction du trafic de diffusion inutile

Le VTP pruning permet de limiter la propagation de certains trafics inondés sur des trunks lorsqu’un VLAN n’a pas besoin d’être transporté plus loin dans la topologie. Il vise principalement des types de trafic de diffusion, multicast et unicast inconnu selon les règles de forwarding applicables. Il ne supprime pas la base VLAN et ne remplace pas la liste des VLAN autorisés sur le trunk.

Sans pruning, un commutateur peut répliquer du trafic inondé pour un VLAN sur plusieurs trunks, même si aucun équipement en aval n’utilise ce VLAN. Avec le pruning, les liens inutiles pour ce VLAN peuvent être exclus de la propagation de ce trafic, lorsque les conditions de la fonctionnalité sont réunies.

```text
Sans pruning :

      SW1 -------- SW2 -------- SW3 -------- SW4
       |             |           |            |
     VLAN 20       VLAN 20     aucun port   VLAN 20
     actif                       VLAN 20     actif

Une diffusion du VLAN 20 peut parcourir des trunks inutiles.

Avec pruning (si pris en charge et correctement configuré) :

      SW1 -------- SW2     X     SW3 -------- SW4
       |             |                   |       |
     VLAN 20       VLAN 20             aucun   VLAN 20
     actif                               port    actif
                                      VLAN 20

Le lien inutile pour le trafic inondé VLAN 20 peut être
élagué, tandis que les VLAN nécessaires continuent de passer.
```

Le pruning est désactivé par défaut dans de nombreux environnements Cisco. Il ne s’applique qu’aux VLAN éligibles. Dans les guides Cisco courants, les VLAN 2 à 1001 sont généralement éligibles par défaut, tandis que VLAN 1, VLAN 1002 à 1005 et les VLAN étendus ne sont pas éligibles selon les limites documentées. Il faut valider le comportement sur la plate-forme déployée.

Avec VTP v1/v2, l’activation du pruning sur un serveur peut l’activer pour le domaine entier. En VTP v3, le pruning doit être activé individuellement sur chaque commutateur concerné dans les implémentations qui suivent ce modèle. Les procédures diffèrent donc selon la version.

Le pruning optimise la propagation du trafic inondé, pas la transmission de chaque paquet unicast connu. Il ne constitue pas non plus un mécanisme de sécurité : il n’isole pas un VLAN et ne remplace pas une liste de VLAN autorisés, une ACL ou un pare-feu.

### 1.10. VLAN autorisés sur un trunk et pruning : ne pas confondre

La liste des VLAN autorisés détermine quels VLAN peuvent être transportés sur un trunk. Le pruning agit sur certains trafics inondés dans les VLAN éligibles, en fonction des besoins en aval. Les deux mécanismes sont indépendants, même s’ils influencent ensemble le chemin réel des trames.

| Contrôle | Question à laquelle il répond | Exemple de vérification |
|---|---|---|
| Existence du VLAN | Le VLAN est-il présent dans la base locale ? | `show vlan brief` |
| Trunk opérationnel | Le lien transporte-t-il plusieurs VLAN ? | `show interfaces trunk` |
| Liste autorisée | Ce VLAN est-il autorisé sur le trunk ? | `show interfaces trunk` |
| VTP | La base VLAN est-elle synchronisée ? | `show vtp status` |
| Pruning | Le trafic inondé inutile est-il limité sur le trunk ? | Statut VTP et vérifications spécifiques à la plateforme |
| Port d’accès | Le terminal est-il placé dans le bon VLAN ? | `show interfaces switchport` |

Un VLAN absent de la liste autorisée sera bloqué sur le trunk même si VTP l’a correctement propagé. Un VLAN autorisé mais inexistant dans la base locale ne se comporte pas nécessairement comme un VLAN exploitable. Un VLAN correctement transporté n’implique pas qu’une interface utilisateur soit affectée à ce VLAN.

Dans une exploitation sérieuse, les listes autorisées doivent être explicites et limitées aux VLAN nécessaires au lien, plutôt que d’autoriser aveuglément tous les VLAN. Cela réduit la surface d’exposition et clarifie les chemins de transport.

### 1.11. Base VLAN, persistance et sauvegarde

Sur de nombreuses plateformes Catalyst classiques, la base VLAN est stockée dans un fichier persistant tel que `vlan.dat`. Les détails de stockage évoluent selon les modèles et les systèmes d’exploitation réseau ; certains environnements intègrent différemment cette base à la configuration ou à des mécanismes internes.

La commande `copy running-config startup-config` sauvegarde la configuration active dans la configuration de démarrage, mais ne doit pas être considérée comme une garantie universelle que toutes les données VLAN, tous les paramètres VTP et toutes les bases annexes sont sauvegardés de la même manière sur chaque plateforme.

La sauvegarde doit donc être conçue pour le modèle utilisé. Elle peut comprendre l’export de la configuration, une copie sécurisée des éléments persistants pris en charge, un relevé de `show vlan brief`, `show vtp status`, des listes de VLAN autorisés et une documentation du plan d’adressage et des ports. Dans un réseau critique, il est utile de conserver une référence de l’état VLAN attendu avant tout changement important.

La procédure de restauration doit être testée. Une sauvegarde inutilisable ou un fichier de base dont la provenance est inconnue ne constitue pas une protection suffisante contre une erreur de propagation VTP.

### 1.12. Interaction avec STP et le routage inter-VLAN

VTP ne calcule pas les chemins STP et ne route pas les paquets entre VLAN. Il peut cependant influencer l’existence des VLAN que STP doit prendre en compte. Lorsqu’un VLAN disparaît de la base ou qu’un trunk cesse de le transporter, sa connectivité de couche 2 change et le comportement observé par les protocoles associés peut être modifié.

STP construit une topologie sans boucle pour les VLAN ou instances concernés. Le trunk transporte les trames qui appartiennent aux VLAN autorisés, tandis que le routeur ou le commutateur multicouche fournit l’acheminement de couche 3 entre les réseaux IP des différents VLAN.

Pour qu’un poste du VLAN 20 puisse communiquer avec un serveur dans le VLAN 30, il faut notamment que :

1. le VLAN 20 existe sur les commutateurs concernés ;
2. le port du poste soit affecté au VLAN 20 ;
3. les trunks intermédiaires transportent le VLAN 20 ;
4. le VLAN 30 soit également présent et transporté vers le serveur ;
5. les passerelles de couche 3 et leurs interfaces SVI ou sous-interfaces soient configurées ;
6. des routes et des politiques de filtrage autorisent la communication voulue.

La synchronisation VTP ne réalise aucune de ces étapes à la place de l’administrateur, hormis la propagation de la base VLAN lorsque la configuration et la version le permettent.

### 1.13. Risques, avantages et choix d’architecture

L’intérêt de VTP est la réduction du travail répétitif dans un domaine où les commutateurs Cisco doivent partager une base VLAN. L’avantage augmente lorsque le nombre d’équipements est important et que les processus d’administration sont bien établis.

Le risque principal tient à la propagation d’une modification incorrecte. Une erreur sur un serveur VTP, un raccordement imprudent d’un équipement avec une révision élevée en v1/v2 ou une incohérence de domaine peut affecter plusieurs commutateurs. La centralisation est donc à la fois un avantage opérationnel et une dépendance qui doit être protégée.

Dans les réseaux où la stabilité prime sur la centralisation, certains administrateurs choisissent le mode transparent ou off, puis gèrent localement les VLAN et les trunks à l’aide d’outils d’automatisation ou de modèles de configuration. Cette stratégie augmente les exigences de cohérence des changements, mais réduit la possibilité qu’une annonce VTP modifie automatiquement la base de plusieurs équipements.

VTP v3, lorsqu’il est disponible sur tout le matériel concerné, peut être préférable pour un nouveau déploiement qui nécessite VTP. La décision doit toutefois être prise après validation des capacités matérielles, des versions logicielles, des besoins de propagation des VLAN étendus et de la compatibilité avec les équipements existants. Une migration ne doit pas être réalisée au milieu d’une fenêtre de changement sans plan de retour arrière.

> **Piège :** Une révision VTP élevée n’est pas synonyme de configuration correcte. En VTP v1/v2, elle peut au contraire être la cause d’un remplacement indésirable de la base VLAN lorsque les paramètres de domaine et les autres conditions de synchronisation sont réunis. Avant de raccorder un commutateur inconnu à la production, contrôle son domaine, sa version, son mode, son mot de passe et sa révision. Ne supprime jamais aveuglément un fichier de base VLAN sur un équipement en service : sauvegarde d’abord l’état, vérifie la procédure adaptée au modèle et valide l’effet attendu.

```text
             PLAN DE CONTRÔLE VTP

   +------------------------+
   | Serveur / primaire VTP  |
   | Base VLAN de référence |
   +-----------+------------+
               |
               | Annonces VTP via liens compatibles
               v
   +------------------------+       +------------------------+
   | Commutateur client A   |-------| Commutateur client B   |
   | Base synchronisée      | trunk | Base synchronisée      |
   +-----------+------------+       +-----------+------------+
               |                                |
               v                                v
   +------------------------+       +------------------------+
   | Ports d'accès VLAN 10  |       | Ports d'accès VLAN 20  |
   | VLAN 10 présent        |       | VLAN 20 présent        |
   +------------------------+       +------------------------+

   VTP synchronise la base VLAN ; le trunk transporte les VLAN.
   Il faut valider ces deux mécanismes séparément.
```

---

## 2. Configuration et Pratique

### 2.1. Objectif du laboratoire

Le laboratoire suivant met en place un domaine VTP simple avec trois commutateurs Cisco Catalyst compatibles IOS. SW1 sert de point d’administration de la base VLAN. SW2 et SW3 reçoivent les mises à jour selon leur mode VTP. Les liaisons inter-switch sont des trunks 802.1Q.

La configuration est présentée en mode VTP v2 pour illustrer le modèle serveur/client connu et les risques du numéro de révision. En production, le choix de la version doit être fait en fonction des capacités de tous les équipements ; sur une nouvelle architecture prise en charge, il faut évaluer VTP v3 et documenter son serveur primaire.

Plan logique :

- VLAN 10 : ADMINISTRATION ;
- VLAN 20 : COMPTABILITE ;
- VLAN 30 : SUPPORT ;
- SW1 : serveur VTP ;
- SW2 et SW3 : clients VTP ;
- liens SW1–SW2 et SW1–SW3 : trunks ;
- ports utilisateurs : ports d’accès affectés explicitement à leur VLAN.

```text
                       Domaine VTP CAMPUS-LAB
                             Version 2

                      +------------------+
                      | SW1              |
                      | VTP server       |
                      | VLAN 10/20/30    |
                      +----+--------+----+
                           |        |
                    trunk  |        |  trunk
                           |        |
                  +--------+--+  +--+--------+
                  | SW2       |  | SW3       |
                  | VTP client|  | VTP client|
                  +-----+-----+  +-----+-----+
                        |              |
                   ports d'accès  ports d'accès
                   VLAN 10/20     VLAN 20/30
```

Les noms d’interfaces utilisés ci-dessous sont des exemples. Sur un équipement réel, remplace-les par les interfaces effectivement présentes. Les commandes de trunk, la prise en charge de DTP et certaines options peuvent dépendre du modèle et du logiciel.

### 2.2. Configuration de SW1 : serveur VTP classique

Avant d’appliquer une configuration à un commutateur de production, exécute les commandes d’état, enregistre les sorties et confirme que le domaine n’est pas déjà utilisé pour une autre architecture. Dans un laboratoire isolé, la configuration peut être définie comme suit :

```cisco
hostname SW1

vtp domain CAMPUS-LAB
vtp version 2
vtp mode server
vtp password RemplacerParUnSecretFort

! Les lignes suivantes supposent que les interfaces existent.
interface GigabitEthernet1/0/47
 description TRUNK_VERS_SW2
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown

interface GigabitEthernet1/0/48
 description TRUNK_VERS_SW3
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown

! Création de la base VLAN sur le serveur VTP.
vlan 10
 name ADMINISTRATION
vlan 20
 name COMPTABILITE
vlan 30
 name SUPPORT

end
```

Cette configuration active un domaine nommé `CAMPUS-LAB`, sélectionne VTP version 2 et place SW1 en mode serveur. Le mot de passe indiqué n’est qu’un exemple : il doit être remplacé par un secret propre à l’environnement. Les plateformes peuvent stocker ou afficher les mots de passe différemment ; vérifie leur comportement avant déploiement.

Les trunks autorisent explicitement les VLAN 10, 20 et 30. Cette liste est volontairement réduite au besoin du laboratoire. Elle ne doit pas être confondue avec la liste complète des VLAN qui existent dans la base VTP. La création de VLAN dans le domaine ne signifie pas qu’ils sont transportés sur tous les trunks.

Après configuration, exécute :

```cisco
show vtp status
show vlan brief
show interfaces trunk
show running-config | section vtp
```

Si la version de l’IOS ne prend pas en charge exactement cette forme de filtrage de la configuration ou certaines commandes, utilise la syntaxe correspondante à la plateforme. Pour une configuration de production, vérifie le manuel de commandes Cisco de la version installée.

### 2.3. Configuration de SW2 et SW3 : clients VTP

Les clients doivent utiliser le même domaine, la même version compatible et le même mot de passe si un mot de passe a été configuré. Ils doivent également avoir des trunks actifs pour recevoir les annonces lorsque la topologie l’exige.

Configuration d’exemple pour SW2 :

```cisco
hostname SW2

vtp domain CAMPUS-LAB
vtp version 2
vtp mode client
vtp password RemplacerParUnSecretFort

interface GigabitEthernet1/0/47
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown

interface GigabitEthernet1/0/10
 description POSTE_ADMINISTRATION
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 no shutdown

end
```

Configuration d’exemple pour SW3 :

```cisco
hostname SW3

vtp domain CAMPUS-LAB
vtp version 2
vtp mode client
vtp password RemplacerParUnSecretFort

interface GigabitEthernet1/0/47
 description TRUNK_VERS_SW1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30
 no shutdown

interface GigabitEthernet1/0/20
 description POSTE_COMPTABILITE
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
 no shutdown

interface GigabitEthernet1/0/21
 description POSTE_SUPPORT
 switchport mode access
 switchport access vlan 30
 spanning-tree portfast
 no shutdown

end
```

`spanning-tree portfast` est prévu pour un port d’accès raccordé à un terminal et non à un autre commutateur. Ne l’applique pas sans analyse aux liens inter-switch. Les commandes VLAN d’accès peuvent être acceptées ou nécessiter des conditions particulières selon la plateforme et le mode VTP. Après synchronisation, vérifie que les VLAN existent et que les interfaces sont bien affectées.

Les équipements clients ne servent pas à modifier la base VLAN dans le modèle classique décrit ici. Les créations et suppressions doivent être réalisées sur un serveur VTP approprié, puis confirmées sur les clients.

### 2.4. Vérifier la propagation

Sur chacun des commutateurs, exécute :

```cisco
show vtp status
show vlan brief
show interfaces trunk
show interfaces switchport
```

`show vtp status` permet notamment de contrôler le domaine, la version, le mode et la révision. `show vlan brief` confirme que la base locale contient les VLAN attendus. `show interfaces trunk` permet de vérifier les trunks actifs et les VLAN autorisés. `show interfaces switchport` fournit les détails de mode et d’affectation d’une interface.

Une propagation correcte ne se juge pas uniquement à l’absence de message d’erreur. Les valeurs visibles sur les clients doivent correspondre au plan de VLAN établi. Il faut également vérifier les ports d’accès, les trunks et, lorsque cela est nécessaire, la connectivité de niveau 2 et de niveau 3.

Ajoute ensuite un VLAN de test sur SW1 :

```cisco
configure terminal
vlan 40
 name LAB-TEST
end
```

Sur les clients, vérifie si le VLAN 40 apparaît dans `show vlan brief` après le délai nécessaire à l’échange. Contrôle également que le VLAN est autorisé sur les trunks qui doivent le transporter. Dans notre configuration initiale, les listes de VLAN autorisés ne contiennent que 10,20,30 : le VLAN 40 peut donc exister dans la base locale sans être transporté sur ces trunks. C’est un exemple volontaire qui montre pourquoi propagation VTP et transport du trafic doivent être examinés séparément.

### 2.5. Configuration locale en mode transparent

Le mode transparent est approprié lorsque la base VLAN doit être administrée localement et non synchronisée à partir du serveur VTP du domaine. La syntaxe générale sur les plateformes classiques est :

```cisco
vtp domain CAMPUS-LAB
vtp mode transparent
```

Sur un commutateur transparent, les VLAN sont configurés localement selon les fonctionnalités disponibles. Les changements de sa propre base ne deviennent pas automatiquement la base de référence des autres membres du domaine.

Le traitement des annonces reçues ou transférées dépend de la version VTP et de la plateforme. Avant d’utiliser un équipement transparent comme point de passage pour les annonces, vérifie les détails du modèle. Si la politique exige qu’un commutateur ne participe pas du tout à VTP, le mode off peut être préférable lorsque celui-ci est disponible, mais son comportement doit aussi être vérifié.

Le mode transparent ne signifie pas qu’un commutateur peut transporter un VLAN absent de sa propre base comme si sa configuration était complète. Il faut contrôler l’existence du VLAN, la liste autorisée du trunk et les contraintes propres au logiciel réseau.

### 2.6. Utiliser VTP version 3 et la notion de serveur primaire

Sur les équipements prenant en charge VTP v3, la configuration peut commencer par :

```cisco
configure terminal
vtp domain CAMPUS-LAB
vtp version 3
vtp mode server
vtp password MonSecretVTPFort hidden
end
```

Cette syntaxe est indicative : les mots-clés de mot de passe, leur longueur, leur stockage et leur disponibilité varient selon les versions IOS/IOS XE. Consulte la documentation de l’équipement et n’utilise pas un secret d’exemple en production.

Dans VTP v3, le statut serveur et le statut serveur primaire ne sont pas équivalents. Pour la base VLAN, un serveur doit être promu comme primaire avant de réaliser certaines modifications. La commande privilégiée documentée par Cisco dans les versions compatibles est de la forme :

```cisco
vtp primary vlan
```

Une option `force` est disponible sur certaines plateformes pour outrepasser des conflits, mais elle est susceptible d’écraser une base concurrente. Elle ne doit jamais être appliquée à l’aveugle. Confirme l’identité du serveur voulu, la base attendue, les conflits indiqués et l’existence d’un plan de retour arrière avant toute opération de prise de contrôle.

Pour vérifier l’état VTP v3, les commandes disponibles peuvent inclure :

```cisco
show vtp status
show vtp devices
show vtp devices conflict
show vtp counters
```

La disponibilité et les champs affichés varient selon le modèle et la version logicielle. VTP v3 peut aussi gérer des informations relatives à MST dans des environnements compatibles ; cela doit être considéré comme une fonction distincte de la propagation de la base VLAN et planifié avec précaution.

### 2.7. Activer le pruning

Dans un domaine v1/v2 compatible, le pruning peut être activé depuis un serveur VTP sur les plateformes qui prennent en charge cette commande :

```cisco
configure terminal
vtp pruning
end

show vtp status
```

Le statut doit ensuite être confirmé dans la sortie de `show vtp status`. Le délai de mise en application et le niveau de propagation dépendent de la version et de la plateforme. En VTP v1/v2, l’activation est généralement diffusée dans le domaine. En VTP v3, la procédure Cisco courante nécessite d’activer le pruning sur chaque commutateur concerné.

N’active pas le pruning sans comprendre les VLAN éligibles et le besoin réel en aval. Certaines catégories de VLAN ne peuvent pas être élaguées selon les limites documentées. Si un VLAN doit être disponible à travers un lien, la liste autorisée sur le trunk reste un paramètre indépendant qui doit être configuré et vérifié.

Après activation, utilise les commandes de supervision spécifiques disponibles sur le modèle, puis teste le trafic et vérifie la topologie. Le pruning ne doit pas être interprété comme un contrôle d’accès et ne remplace pas la segmentation de sécurité.

### 2.8. Procédure sécurisée d’ajout d’un commutateur

Un nouvel équipement ne doit pas être branché immédiatement à un domaine VTP v1/v2 en production. La procédure suivante réduit le risque de propagation accidentelle d’une base incorrecte.

1. **Isoler l’équipement** : prépare sa configuration sans le raccorder aux trunks de production.
2. **Sauvegarder son état** : conserve les sorties de `show running-config`, `show vlan brief` et `show vtp status`.
3. **Contrôler le domaine et la version** : compare le nom VTP et la version aux paramètres documentés du réseau cible.
4. **Contrôler la révision** : sur v1/v2, assure-toi que la révision ne peut pas perturber la base existante. Utilise uniquement une procédure de remise à zéro documentée pour la plate-forme.
5. **Choisir le mode** : définis explicitement server, client, transparent ou off selon le rôle prévu.
6. **Configurer les secrets** : applique le mécanisme d’authentification attendu et confirme la cohérence du mot de passe.
7. **Valider les trunks** : limite les VLAN autorisés aux besoins réels et vérifie l’encapsulation et le VLAN natif selon la configuration du réseau.
8. **Raccorder avec contrôle** : surveille le statut VTP, les révisions, la base VLAN et les journaux immédiatement après le raccordement.
9. **Tester le service** : vérifie les VLAN attendus, les ports d’accès, STP et la connectivité.
10. **Documenter** : mets à jour l’inventaire, le schéma des trunks et la procédure de retour arrière.

La prudence doit être renforcée pour les équipements provenant d’un laboratoire, d’un stock de rechange ou d’un ancien site. Leur configuration persistante peut contenir des paramètres qui ne sont plus compatibles avec le réseau actuel.

### 2.9. Sauvegarde, contrôle de changement et retour arrière

Avant une modification importante de la base VLAN, il est nécessaire de documenter l’état attendu. Une sauvegarde minimale peut comprendre la configuration active, la base VLAN disponible selon la plateforme, la sortie de `show vlan brief`, la sortie de `show vtp status` et la liste des VLAN autorisés sur les trunks importants.

La configuration active peut être sauvegardée avec :

```cisco
copy running-config startup-config
```

Cette commande n’est pas à elle seule un plan complet de sauvegarde de la base VLAN pour toutes les plateformes. Utilise le mécanisme de sauvegarde recommandé pour le modèle installé et conserve une copie hors de l’équipement, dans un emplacement contrôlé.

Le retour arrière doit préciser comment rétablir la base attendue et empêcher qu’une annonce indésirable ne réintroduise une base obsolète. En VTP v3, une opération de prise de contrôle peut avoir des effets importants ; en v1/v2, la révision doit être analysée. Une procédure de restauration qui ne traite pas le comportement VTP peut échouer en raison de la resynchronisation automatique.

### 2.10. Contrôles avant mise en production

Avant de considérer un domaine VTP prêt pour la production, vérifie au minimum les points suivants :

- Les commutateurs utilisent la version prévue et prise en charge.
- Le nom de domaine est cohérent sur les équipements qui doivent échanger les bases.
- Le mode VTP est explicitement défini et justifié pour chaque commutateur.
- Le mécanisme d’authentification, s’il est utilisé, est cohérent.
- En v1/v2, les révisions ont été contrôlées avant l’ajout de tout équipement.
- En v3, le rôle primaire est documenté et contrôlé avant une modification de base.
- Les VLAN locaux correspondent au plan d’adressage et à l’inventaire.
- Les listes de VLAN autorisés des trunks sont explicites et limitées aux besoins.
- Les VLAN natifs et les paramètres de trunk sont cohérents aux deux extrémités.
- Les ports utilisateurs sont affectés aux VLAN corrects.
- STP et le routage inter-VLAN fonctionnent comme prévu.
- Les sauvegardes et la procédure de retour arrière ont été validées.

---

## 3. Dépannage et Sécurité

### 3.1. Méthode de diagnostic par couches

Le dépannage doit distinguer quatre niveaux : la connectivité du lien, la négociation ou l’état du trunk, la synchronisation VTP et le transfert dans les VLAN. Un seul de ces niveaux peut être défaillant, ou plusieurs problèmes peuvent être présents en même temps.

Commence par vérifier l’état physique/logique des interfaces et les trunks. Si le lien ne fonctionne pas ou ne transporte pas de trames comme prévu, la synchronisation VTP peut échouer. Ensuite, compare `show vtp status` entre les équipements : domaine, version, mode, révision, pruning et paramètres de sécurité affichés. Vérifie enfin `show vlan brief`, la liste des VLAN autorisés et l’affectation des ports.

Commandes de base :

```cisco
show interfaces status
show interfaces trunk
show vlan brief
show vtp status
show vtp counters
show running-config
show logging
```

Toutes les commandes ne sont pas disponibles avec exactement les mêmes options sur toutes les plateformes. Utilise les commandes équivalentes documentées pour le système d’exploitation réseau installé. Évite d’exécuter des commandes de debug à haut volume sur un équipement de production sans procédure contrôlée.

### 3.2. Problème : les VLAN ne se propagent pas

Si un VLAN créé sur le serveur n’apparaît pas sur un client, vérifie les points suivants :

1. **Domaine VTP** : le nom est-il identique sur les équipements qui doivent échanger la base ?
2. **Version** : la version est-elle compatible et conforme au plan ?
3. **Mode** : le commutateur distant est-il en mode client ou serveur approprié, plutôt qu’en mode transparent/off ?
4. **Mot de passe** : l’authentification est-elle identique, si elle est activée ?
5. **Trunk** : un chemin de trunks opérationnel relie-t-il les commutateurs ?
6. **Révision et état de base** : les annonces sont-elles acceptées par les équipements ?
7. **Plateforme** : le VLAN appartient-il à une plage qui peut être propagée avec la version et le modèle utilisés ?

La commande `show vtp status` donne les premières indications, mais `show interfaces trunk` est nécessaire pour confirmer les liens de transport. Un client VTP peut être correctement configuré et ne recevoir aucune annonce si le chemin de couche 2 n’est pas opérationnel.

Si le VLAN existe dans la base mais que les terminaux ne communiquent pas, élargis le diagnostic : ports d’accès, VLAN autorisés, STP, plan d’adressage IP, passerelles et ACL. Le problème de connectivité ne relève pas nécessairement de VTP lui-même.

### 3.3. Problème : domaine VTP ou mot de passe incompatible

Un nom de domaine différent empêche normalement une synchronisation attendue au sein du même domaine. Un mot de passe incorrect peut aussi empêcher l’acceptation des annonces protégées. Compare les paramètres sur les deux équipements et utilise les commandes de consultation disponibles, sans exposer les secrets dans des captures ou des journaux non protégés.

Ne change pas tous les mots de passe ou toutes les versions simultanément. Identifie d’abord le paramètre qui diffère de la configuration approuvée, puis effectue une modification ciblée. Un changement de domaine peut provoquer d’autres effets, particulièrement sur la manière dont le commutateur participe au système VTP.

En VTP v3, vérifie également la configuration d’authentification et, si disponible, les informations relatives aux équipements et aux conflits de serveurs primaires. Les méthodes de stockage `hidden`/`secret` et les procédures de promotion peuvent modifier l’expérience opérationnelle par rapport aux versions précédentes.

### 3.4. Problème : la base VLAN a été remplacée ou des VLAN ont disparu

Si plusieurs VLAN disparaissent après le raccordement d’un commutateur ou une modification VTP, considère l’incident comme potentiellement lié à la synchronisation de base. Évite de créer immédiatement tous les VLAN manuellement sur plusieurs commutateurs : cela peut masquer l’origine du problème et compliquer la restauration de la cohérence.

Procédure de diagnostic :

- relève immédiatement `show vtp status` sur les commutateurs importants ;
- note le domaine, la version, le mode et le numéro de révision observé ;
- relève `show vlan brief` et compare la base aux sauvegardes ou à l’inventaire ;
- identifie les équipements ajoutés ou modifiés juste avant l’incident ;
- vérifie les journaux et l’état des trunks ;
- isole, si la procédure d’exploitation l’autorise, la source potentielle d’annonces indésirables ;
- restaure la base approuvée selon la procédure correspondant à la version et au modèle.

N’utilise pas une réinitialisation générique de la base ou un redémarrage comme réflexe. Il est nécessaire de comprendre quel équipement fait autorité sur le domaine et comment empêcher la resynchronisation d’une base incorrecte. En v1/v2, la révision et le domaine sont des indices essentiels. En v3, examine le rôle primaire, les conflits et l’état de la base concernée.

### 3.5. Problème : le VLAN existe mais le trafic ne passe pas

La présence du VLAN dans `show vlan brief` confirme son existence dans la base locale ; elle ne confirme pas son transport de bout en bout.

Vérifie successivement :

- le port utilisateur est en mode access et associé au VLAN attendu ;
- le lien inter-switch est en mode trunk ;
- le VLAN est autorisé sur chaque trunk du chemin ;
- le VLAN est actif et transporté sur la liaison ;
- STP ne bloque pas le seul chemin dont le service dépend ;
- le VLAN natif est cohérent aux extrémités lorsque le lien utilise 802.1Q ;
- le terminal possède l’adressage IP et la passerelle appropriés ;
- le routage inter-VLAN et les politiques de sécurité permettent le flux souhaité.

La commande `show interfaces trunk` est essentielle, mais il peut être nécessaire d’examiner les états STP et les interfaces des deux extrémités. Un port d’accès affecté au mauvais VLAN peut donner l’impression que VTP fonctionne mal alors que la base est parfaitement synchronisée.

### 3.6. Problème : VLAN étendu absent des clients

Les VLAN étendus, généralement identifiés par des ID 1006 à 4094, ne sont pas propagés par VTP v1/v2 comme les VLAN de plage normale. VTP v3 prend en charge leur propagation sur des plateformes compatibles. Si un VLAN étendu n’apparaît pas sur un client, vérifie d’abord la version du protocole et les capacités de la plate-forme avant de rechercher une panne de trunk.

Même en VTP v3, la prise en charge exacte dépend de la version logicielle et des fonctionnalités activées. Certains scénarios de configuration de plage étendue peuvent se comporter différemment selon les systèmes. Il faut confirmer la compatibilité avant de migrer une base en production.

Le pruning VTP ne doit pas non plus être supposé applicable à ces VLAN étendus. Dans la documentation Cisco courante, le pruning VTP est limité à la plage normale éligible et les VLAN étendus ne sont pas éligibles. Utilise des listes de VLAN autorisés et une conception de trunk adaptées pour maîtriser leur transport.

### 3.7. Problème : pruning semble bloquer le trafic

Le VTP pruning ne supprime pas un VLAN de la base et ne désactive pas automatiquement toutes ses communications. Il vise à limiter certains trafics inondés sur les trunks qui n’ont pas besoin de les transporter. Si le trafic unicast connu ne passe pas, la cause peut être une liste de VLAN autorisés, STP, la table MAC, le câblage ou une autre fonction de sécurité plutôt que le pruning.

Pour diagnostiquer :

- confirme si le pruning est activé dans le domaine ;
- vérifie la version VTP et la procédure d’activation applicable ;
- contrôle si le VLAN est éligible au pruning ;
- inspecte les listes autorisées des trunks ;
- vérifie la présence de ports actifs dans le VLAN en aval ;
- examine les tables MAC et les états STP ;
- compare le comportement du trafic concerné avec le type de trame et le trajet attendu.

Ne désactive pas globalement le pruning comme première action sans avoir établi qu’il est réellement en cause. Une désactivation peut accroître le volume du trafic inondé et ne pas résoudre un VLAN absent de la liste autorisée.

### 3.8. VTP et sécurité des ports/trunks

VTP doit faire partie de la politique de sécurité des commutateurs, au même titre que la maîtrise des trunks, la segmentation des VLAN, la sécurisation des ports d’accès et la gestion administrative. L’existence d’un domaine VTP n’est pas une frontière de sécurité suffisante.

Mesures recommandées :

- configurer explicitement les ports utilisateur en mode access ;
- désactiver ou encadrer la négociation de trunk sur les ports où elle n’est pas nécessaire, selon le modèle ;
- limiter la liste des VLAN autorisés sur chaque trunk ;
- configurer un VLAN natif cohérent et non utilisé pour les terminaux, selon la politique de conception ;
- limiter les interfaces actives vers des équipements capables d’émettre des annonces de contrôle ;
- utiliser les modes VTP qui correspondent à la politique d’administration ;
- protéger les accès de gestion et les secrets ;
- suivre les changements de révision et les événements VTP ;
- documenter les serveurs VTP et la procédure de modification de la base.

La désactivation de la négociation DTP, lorsqu’elle est possible et requise par la politique de sécurité, est un contrôle différent de VTP. DTP négocie le comportement trunk sur les plateformes qui le prennent en charge ; VTP diffuse la base VLAN. Il ne faut pas croire que désactiver DTP désactive automatiquement VTP, ni qu’activer VTP crée obligatoirement un trunk.

### 3.9. VTP comme vecteur d’erreur de configuration

Le principal danger opérationnel de VTP v1/v2 vient de la possibilité qu’une base inattendue soit acceptée à la suite d’une synchronisation. Une mauvaise configuration peut se propager rapidement à de nombreux commutateurs, avec des effets plus étendus qu’une modification effectuée sur un seul équipement en mode transparent.

Le risque peut être réduit en appliquant une procédure d’accueil des équipements, en limitant les appareils autorisés à rejoindre les trunks de production, en documentant l’autorité de la base, en surveillant les révisions et en préférant une architecture qui rend explicite la responsabilité de modification.

VTP v3 ajoute un contrôle de serveur primaire pour les changements de base, mais ne garantit pas que le contenu publié soit exact. Une personne disposant des droits nécessaires peut toujours effectuer une modification erronée, et une opération forcée peut avoir des conséquences importantes. La sécurité dépend donc à la fois de la fonction protocolaire, des contrôles d’accès et des pratiques d’exploitation.

> **Astuce :** Pour une première analyse, compare `show vtp status`, `show vlan brief` et `show interfaces trunk` sur le commutateur où le VLAN a été créé et sur un client qui devrait le recevoir. Cette comparaison répond séparément à trois questions : le domaine et la révision sont-ils cohérents, le VLAN existe-t-il localement, et les trunks permettent-ils de transporter ce VLAN ? Ajoute ensuite `show interfaces switchport` sur le port utilisateur et les vérifications STP si le VLAN est présent mais le trafic ne passe pas.

### 3.10. Surveillance et exploitation au quotidien

La supervision d’un domaine VTP doit être centrée sur les changements, et pas seulement sur l’état courant. Un contrôle périodique peut enregistrer la version VTP, le mode, le domaine, la révision, le rôle primaire s’il s’agit de VTP v3, les VLAN présents et les trunks autorisés. Toute divergence inattendue doit être traitée comme un événement de configuration à qualifier.

Dans une infrastructure importante, il est utile d’automatiser la comparaison des sorties de référence ou de gérer les VLAN via un système de configuration contrôlée. L’objectif est de détecter une base non conforme avant que cette différence ne provoque une interruption. L’automatisation doit toutefois tenir compte du fait que le comportement de VTP diffère des plateformes où la base VLAN est gérée intégralement de manière locale.

La journalisation doit contenir suffisamment d’informations pour retrouver les changements récents, sans exposer les secrets. Les accès d’administration doivent être individualisés et tracés. Une procédure de changement doit indiquer l’auteur, le but, les VLAN concernés, les trunks affectés, le résultat attendu et le plan de retour arrière.

### 3.11. Danger opérationnel et règle de prudence

> **Danger :** Sur un domaine VTP v1/v2, raccorder sans contrôle un commutateur qui possède le même domaine et une révision de configuration supérieure peut entraîner le remplacement de la base VLAN sur des équipements du domaine. Des VLAN nécessaires peuvent disparaître et provoquer une interruption à grande échelle. En VTP v3, le mécanisme de serveur primaire apporte une protection renforcée, mais une prise de contrôle incorrecte ou une modification mal validée peut toujours perturber le service.
>
> Avant tout raccordement ou changement de base, sauvegarde l’état, contrôle le domaine/la version/le mode/la révision, vérifie le rôle primaire s’il s’applique, puis valide la liste de VLAN et les trunks. Ne lance jamais une commande de prise de contrôle forcée et ne supprime jamais une base persistante sans comprendre les conséquences sur la topologie complète et sans disposer d’un retour arrière documenté.

## Points à retenir

- **VTP synchronise des informations de base VLAN ; il ne transporte pas lui-même les trames utilisateur et ne remplace pas le trunk 802.1Q.** Après toute mise à jour, contrôle l’existence locale du VLAN, la liste autorisée des trunks, l’affectation des ports et STP séparément.
- **En VTP v1/v2, le numéro de révision est un paramètre opérationnel critique.** Une révision plus élevée n’atteste pas d’une meilleure configuration et peut remplacer une base attendue. Avant de raccorder un switch inconnu, vérifie le domaine, le mode, la version, le mot de passe et la révision.
- **VTP v3 ajoute la prise en charge des VLAN étendus et un mécanisme de serveur primaire sur les plateformes compatibles.** Cette protection améliore la gouvernance des modifications, mais elle ne remplace ni les sauvegardes, ni l’authentification, ni la validation des changements.
- **Le VTP pruning et la liste de VLAN autorisés remplissent des fonctions différentes.** Le pruning limite certains trafics inondés sur les trunks éligibles ; la liste autorisée contrôle les VLAN qui peuvent être transportés sur le lien. Ils doivent être configurés et vérifiés indépendamment.
- **Le mode VTP doit être choisi intentionnellement.** Server/client facilite la gestion centralisée ; transparent ou off favorise l’administration indépendante selon les capacités de la plateforme. Le choix doit tenir compte de la taille du réseau, du risque de propagation, de la compatibilité et des procédures d’exploitation.

## Références techniques

- Cisco, [Configure VTP – VLAN Configuration Guide, IOS XE 17](https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/lyr2-fwd/vlan/vlan-configuration-guide/configure-vtp.html).
- Cisco, [Configure VTP on Catalyst Switches](https://www.cisco.com/c/en/us/support/docs/lan-switching/vtp/98154-conf-vlan.html).
- Cisco, [Understanding and Configuring VTP – Catalyst 4500](https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst4500/12-2/31sg/configuration/guide/vtp.html).
