# VXLAN — Niveau expert

## EVPN, BGP, routage inter-VNI, Anycast Gateway, multihoming et convergence


# PRÉSENTATION DU COURS

Ce cours constitue le troisième niveau du parcours VXLAN. Il prolonge directement `vxlan-debutant.md` et `vxlan-intermediaire.md`.

Le niveau débutant a présenté les principes de VXLAN, l'encapsulation Ethernet dans UDP/IP, le VNI, les VTEP et la séparation entre underlay et overlay.

Le niveau intermédiaire a permis de mettre ces notions en pratique. Il a notamment étudié la connectivité IP entre les VTEP, les interfaces VXLAN, les associations locales entre VLAN et VNI, l'apprentissage MAC, le trafic BUM, la MTU et le dépannage d'un overlay statique.

Ces deux premiers niveaux constituent une base indispensable, mais ils ne suffisent pas à concevoir une architecture VXLAN évolutive.

Dans un centre de données de grande taille, plusieurs centaines de commutateurs peuvent participer à différents segments réseau. Des machines virtuelles peuvent changer d'emplacement, certains équipements peuvent être reliés à plusieurs commutateurs et des réseaux appartenant à différents tenants doivent communiquer sans perdre leur isolation.

La configuration manuelle des destinations distantes devient alors difficile à maintenir. Il devient nécessaire de distribuer les informations de connectivité, de gérer les chemins redondants, de contrôler la mobilité des adresses MAC et de fournir un mécanisme cohérent pour le routage entre les sous-réseaux.

C'est dans ce contexte que VXLAN est fréquemment associé à **EVPN (Ethernet VPN)**, qui fournit un plan de contrôle permettant de distribuer des informations de reachability. Dans les architectures courantes de centres de données, BGP est utilisé pour transporter les routes EVPN. Les deux technologies remplissent des rôles distincts : VXLAN transporte les trames, tandis qu'EVPN fournit des informations de contrôle. [RFC 8365](https://www.rfc-editor.org/rfc/rfc8365.html)

Le niveau expert étudie cette architecture dans son ensemble. Il ne se limite pas à mémoriser les types de routes BGP ou les commandes d'un constructeur. Il explique comment les informations circulent, comment les décisions de forwarding sont prises, quelles conditions permettent une convergence correcte et comment diagnostiquer les situations dans lesquelles le plan de contrôle et le plan de données ne correspondent plus.

## Positionnement dans le parcours

```text
NIVEAU DÉBUTANT — vxlan-debutant.md
        |
        v
Concepts VXLAN, VNI et VTEP
Underlay et overlay
Encapsulation Ethernet / UDP / IP
        |
        v
NIVEAU INTERMÉDIAIRE — vxlan-intermediaire.md
        |
        v
Configuration VXLAN
Apprentissage MAC et forwarding
Trafic BUM et réplication
MTU et dépannage du tunnel
        |
        v
NIVEAU EXPERT — CE COURS
        |
        v
Plan de contrôle BGP EVPN
Types de routes EVPN
RD et Route Targets
VNI de couche 2 et de couche 3
Routage inter-VNI
Anycast Gateway
Mobilité MAC/IP
Multihoming et convergence
Sécurité et architecture de production
```

**Continuité pédagogique :** ce cours réutilise les concepts et le laboratoire des deux niveaux précédents. Le VTEP, le VNI, l'underlay, l'encapsulation et le forwarding MAC ne sont pas redéfinis comme s'il s'agissait de nouvelles notions : ils servent de point de départ pour étudier le plan de contrôle et le comportement global de l'architecture.


# OBJECTIFS PÉDAGOGIQUES

À la fin de ce cours, l'apprenant doit pouvoir :

1. Expliquer pourquoi EVPN complète VXLAN dans une architecture distribuée.
2. Distinguer le plan de contrôle BGP EVPN du plan de données VXLAN.
3. Comprendre l'utilisation des sessions BGP pour distribuer les routes EVPN.
4. Interpréter les rôles des routes EVPN de types 1 à 5.
5. Distinguer Route Distinguisher et Route Target.
6. Expliquer les notions de MAC-VRF et d'IP-VRF.
7. Comprendre les VNI de couche 2 et les VNI de couche 3.
8. Comparer le routage IRB symétrique et asymétrique.
9. Expliquer le rôle de l'Anycast Gateway.
10. Comprendre la mobilité MAC/IP et la prévention de certaines boucles.
11. Expliquer le multihoming EVPN et l'élection du Designated Forwarder.
12. Comprendre les principes de convergence et de retrait massif des routes.
13. Construire une méthode de dépannage séparant underlay, contrôle et données.
14. Définir une architecture VXLAN EVPN cohérente et vérifiable.
15. Identifier les limites d'une solution propre à un constructeur et les différences possibles entre implémentations.

## Prérequis

L'apprenant doit maîtriser les notions des deux cours précédents :

- Encapsulation VXLAN.
- Fonctionnement du VTEP.
- VNI et associations VLAN-VNI.
- Underlay IP et routage.
- Apprentissage MAC et flooding.
- MTU et transport UDP.
- Lecture des tables de forwarding.
- Principes du dépannage VXLAN.

Il doit également posséder des connaissances en routage BGP, en adressage IP, en VLAN et en segmentation réseau.

Une maîtrise complète de BGP n'est pas indispensable pour commencer, mais les notions de voisins, de routes, de next-hop et de politiques d'importation sont nécessaires pour comprendre le cœur du cours.


# PARTIE 1 — PASSER D'UN OVERLAY STATIQUE À UNE ARCHITECTURE EVPN

## 1. Les limites d'un VXLAN statique

Au niveau intermédiaire, le laboratoire utilisait deux VTEP. Chaque extrémité connaissait explicitement l'adresse IP de l'autre.

Cette méthode fonctionne pour apprendre les mécanismes d'encapsulation et tester un tunnel simple. Elle devient cependant difficile à administrer lorsque le nombre de VTEP augmente.

Dans une architecture comportant quelques dizaines de points de terminaison, les destinations, les segments logiques et les associations locales doivent rester cohérents. Si ces informations sont gérées manuellement partout, une modification de topologie peut nécessiter de nombreux changements coordonnés.

Le problème ne se limite pas au nombre de commandes. Une architecture statique possède aussi des difficultés de découverte, de mobilité et de convergence : comment apprendre qu'une machine virtuelle a été déplacée ? Comment retirer rapidement une ancienne association ? Comment connaître les VTEP participants à un segment ? Comment éviter qu'une information obsolète continue à orienter le trafic vers un ancien emplacement ?

EVPN répond à une partie de ces besoins en fournissant un plan de contrôle capable de distribuer des informations de reachability. Il utilise un modèle de routes BGP enrichi pour représenter des informations Ethernet, MAC/IP et, dans les scénarios appropriés, des préfixes IP. [RFC 7432](https://www.rfc-editor.org/rfc/rfc7432.html) · [RFC 8365](https://www.rfc-editor.org/rfc/rfc8365.html)

### Comparaison des approches

| Fonction | VXLAN statique simple | VXLAN avec EVPN |
|---|---|---|
| Encapsulation des trames | VXLAN | VXLAN |
| Transport entre VTEP | Underlay IP | Underlay IP |
| Identification du segment | VNI | VNI, associé aux informations EVPN |
| Découverte des destinations | Configuration ou apprentissage prévu par l'implémentation | Informations de reachability distribuées par le plan de contrôle, complétées par les mécanismes locaux |
| Mobilité MAC/IP | Dépend des mécanismes et de l'administration | Procédures de mobilité définies dans EVPN |
| Distribution des informations | Peut nécessiter de nombreuses opérations manuelles | BGP EVPN distribue les routes correspondantes |
| Multihoming | Dépend des fonctions disponibles | Procédures EVPN de multihoming prises en charge par l'implémentation |
| Évolutivité opérationnelle | Limitée lorsque les relations se multiplient | Meilleure structuration du contrôle, sous réserve d'une conception cohérente |

EVPN n'élimine pas la nécessité de configurer les équipements. Il rend la distribution des informations de contrôle plus structurée et permet aux équipements de prendre des décisions de forwarding à partir de routes reçues et sélectionnées.

## 2. Les deux plans fondamentaux

Une architecture VXLAN EVPN doit être étudiée à travers deux plans complémentaires.

Le **plan de données** transporte les trames et les paquets. VXLAN est utilisé pour transporter les trames Ethernet sur l'infrastructure IP. Le réseau underlay achemine le paquet extérieur entre les points de terminaison.

Le **plan de contrôle** distribue les informations qui permettent aux VTEP de déterminer quelles destinations existent, à quels segments elles appartiennent et quels chemins utiliser. BGP EVPN transporte ces informations sous la forme de routes et d'attributs.

Il faut éviter de confondre les deux fonctions.

Un préfixe reçu par BGP ne signifie pas automatiquement que tous les paquets vers ce préfixe peuvent être transmis. Le next-hop doit être résolu, le chemin de transport doit être disponible et les états de forwarding nécessaires doivent être installés.

À l'inverse, un paquet UDP/4789 observé sur un lien ne prouve pas que le plan de contrôle possède les bonnes informations sur les destinations MAC/IP.

### Architecture générale

```text
                 PLAN DE CONTRÔLE
                  BGP EVPN
                /          \
               v            v
             VTEP-A        VTEP-B
               |              |
               +--------------+
                  VXLAN / UDP
                       |
                       v
                  UNDERLAY IP
```

Les sessions BGP peuvent être établies entre les équipements VTEP ou au moyen de route reflectors, selon la conception.

Les flux VXLAN suivent le plan de données et utilisent des adresses IP de transport. Les routes EVPN suivent le plan de contrôle BGP. Les deux chemins sont logiquement distincts, même s'ils partagent souvent la même infrastructure IP.

## 3. Le rôle du VTEP dans une architecture EVPN

Le VTEP conserve son rôle d'encapsulation et de décapsulation. L'introduction d'EVPN ne remplace pas le traitement VXLAN.

La différence est que le VTEP peut désormais recevoir des informations de contrôle lui indiquant qu'une adresse MAC ou un préfixe est joignable via un autre VTEP.

Ces informations sont intégrées dans les tables et structures de forwarding de la plateforme.

Le traitement repose alors sur plusieurs décisions :

- Identifier le segment d'origine.
- Rechercher la destination MAC ou IP selon le type de trafic.
- Déterminer le VNI de destination.
- Résoudre le next-hop associé à la route.
- Encapsuler le trafic vers la destination distante.
- Vérifier la cohérence du chemin de transport.

Une route EVPN constitue une information de contrôle. La manière exacte dont elle se traduit dans les tables de forwarding dépend du système réseau et de ses fonctions prises en charge.


# PARTIE 2 — COMPRENDRE BGP EVPN

## 4. Pourquoi BGP ?

BGP permet d'échanger des routes entre pairs et prend en charge plusieurs familles d'adresses. EVPN utilise une famille d'adresses spécifique pour transporter des informations Ethernet.

Dans une architecture VXLAN EVPN, les équipements peuvent donc utiliser BGP pour distribuer des informations sur les destinations MAC, les associations IP/MAC, les segments Ethernet et certains préfixes IP.

BGP n'encapsule pas les trames Ethernet destinées aux workloads. Il transporte les informations de contrôle nécessaires pour construire l'état de forwarding.

Cette séparation présente un avantage important : les équipements peuvent apprendre des informations de reachability sans devoir attendre que chaque destination génère du trafic de données vers eux.

## 5. Underlay et sessions BGP

L'underlay doit fournir la connectivité IP nécessaire pour établir et maintenir les sessions BGP prévues par l'architecture.

Dans une conception courante, les équipements disposent d'adresses de loopback utilisées comme identifiants stables ou points de terminaison des sessions. La possibilité d'utiliser une loopback dépend du routage de l'underlay et des paramètres de session configurés.

La séquence générale est la suivante :

1. L'underlay apprend les routes nécessaires pour joindre les adresses des pairs BGP.
2. Les sessions BGP sont établies.
3. Les équipements activent la famille d'adresses EVPN.
4. Les routes sont annoncées, reçues et évaluées selon les politiques et attributs disponibles.
5. Les routes sélectionnées peuvent alimenter les tables de contrôle et de forwarding appropriées.

Une session BGP établie ne signifie pas que toutes les routes EVPN nécessaires ont été reçues ou installées.

Il faut vérifier séparément l'état de la session, les routes apprises, les politiques appliquées et les résultats de forwarding.

## 6. eBGP, iBGP et route reflectors

Les architectures VXLAN EVPN peuvent utiliser iBGP ou eBGP. Le choix dépend de l'organisation du réseau, des domaines d'administration et des objectifs de conception.

Avec iBGP, la distribution des routes entre de nombreux VTEP peut nécessiter une architecture de route reflection. Le route reflector facilite la distribution des routes BGP sans imposer que chaque VTEP maintienne une session iBGP directe avec tous les autres.

Dans une topologie comportant beaucoup de leaf switches, les route reflectors peuvent simplifier la structure des sessions de contrôle.

Ils ne remplacent cependant pas l'underlay. Les next-hops annoncés doivent rester résolubles, et les politiques de routage doivent permettre aux routes pertinentes d'être distribuées.

### Différence essentielle

Un route reflector distribue des routes BGP selon les règles du protocole. Il ne transporte pas directement les trames VXLAN entre les hôtes.

Le trafic des workloads continue d'être transmis sur le plan de données, à travers l'infrastructure IP et les VTEP.

## 7. Que transporte la famille d'adresses EVPN ?

Les routes EVPN permettent de représenter plusieurs informations utiles à l'overlay.

Les exemples principaux comprennent :

- Les informations d'association entre adresses MAC et, éventuellement, IP.
- Les informations de présence et d'adhésion à un segment Ethernet.
- Les informations relatives aux segments Ethernet multihébergés.
- Les informations permettant de retirer rapidement des routes associées à une panne.
- Les préfixes IP annoncés dans les scénarios qui utilisent les routes EVPN de type 5.

Les types de routes ne remplissent pas tous la même fonction. Il est donc essentiel de comprendre pourquoi une route est annoncée, quels attributs elle transporte et quelles tables peuvent être alimentées par sa réception.


# PARTIE 3 — ROUTE DISTINGUISHER ET ROUTE TARGET

## 8. Pourquoi faut-il distinguer les routes ?

Dans une infrastructure multi-tenant, plusieurs réseaux indépendants peuvent posséder des adresses IP ou des informations Ethernet similaires.

Il faut pouvoir représenter ces informations sans perdre la distinction entre les domaines logiques auxquels elles appartiennent.

EVPN utilise notamment le Route Distinguisher et les Route Targets pour remplir des rôles complémentaires.

Ces deux mécanismes sont parfois confondus, car ils sont tous deux associés aux routes BGP VPN. Ils ne répondent pourtant pas à la même question.

## 9. Le Route Distinguisher

Le **Route Distinguisher (RD)** rend une route VPN identifiable dans le contexte BGP où des informations similaires pourraient apparaître dans plusieurs domaines.

Il est associé à la représentation des routes VPN et participe à l'unicité du NLRI correspondant.

Le RD n'est pas, à lui seul, la politique qui décide quels équipements doivent importer une route.

Il ne constitue pas non plus une clé de chiffrement ni un mécanisme d'isolation du trafic de données.

Une architecture doit attribuer les RD de manière cohérente avec les règles du protocole et le fonctionnement de la plateforme. Dans une même table logique, leur conception doit éviter les collisions non souhaitées.

## 10. Le Route Target

Le **Route Target (RT)** est une communauté étendue BGP utilisée pour déterminer les politiques d'exportation et d'importation des routes VPN.

Une route peut être annoncée avec un ou plusieurs RT. Les équipements qui possèdent une politique d'importation correspondant à ces RT peuvent sélectionner la route pour leur instance logique.

C'est un mécanisme important pour contrôler la distribution des informations entre tenants et entre instances réseau.

Le RT ne remplace pas les politiques de sécurité appliquées aux paquets. Il décide quelles routes sont candidates à l'importation dans les instances concernées ; il ne constitue pas à lui seul une politique de filtrage des communications applicatives.

## 11. Comparaison

| Élément | Route Distinguisher | Route Target |
|---|---|---|
| Question principale | Comment distinguer les routes VPN ? | Quelles instances peuvent importer la route ? |
| Rôle | Unicité du contexte de route | Politique de distribution |
| Application | Encodage de la route VPN | Importation et exportation des routes |
| Effet direct sur la sécurité des paquets | Aucun mécanisme de chiffrement | Ne remplace pas un filtrage de trafic |
| Erreur typique | Collision ou mauvaise conception de l'identité des routes | Route non importée ou importée par une instance indésirable |

## 12. Exemple multi-tenant

Supposons qu'une infrastructure héberge deux tenants, A et B.

Les deux tenants ont un réseau IP privé qui utilise la même plage d'adresses. Cette situation doit rester possible sans que les routes d'un tenant soient automatiquement installées dans l'autre.

L'architecture crée des instances réseau distinctes, puis applique des RD et des RT adaptés.

Le tenant A importe uniquement les routes correspondant à ses politiques. Le tenant B possède une politique distincte.

Il est possible de créer des exceptions d'importation pour certains services partagés, mais ces exceptions doivent être décidées explicitement et documentées.

**Point de sécurité :** une erreur de Route Target peut entraîner une fuite de routes entre domaines logiques. Cette fuite ne signifie pas nécessairement que tous les paquets traverseront immédiatement le réseau, mais elle peut modifier les décisions de routage et exposer des communications non prévues.


# PARTIE 4 — LES TYPES DE ROUTES EVPN

## 13. Pourquoi plusieurs types de routes ?

EVPN doit représenter différentes catégories d'informations de contrôle.

Une seule forme de route ne suffirait pas pour décrire simultanément l'annonce d'une adresse MAC, la présence d'un VTEP dans un segment, l'identité d'un segment Ethernet multihébergé et la distribution d'un préfixe IP.

Les types de routes EVPN répondent à ces besoins distincts.

Les types présentés ci-dessous proviennent du cadre EVPN défini notamment dans la [RFC 7432](https://www.rfc-editor.org/rfc/rfc7432.html), complété pour les overlays IP dans la [RFC 8365](https://www.rfc-editor.org/rfc/rfc8365.html) et pour le routage inter-sous-réseaux dans les [RFC 9135](https://www.rfc-editor.org/rfc/rfc9135.html) et [RFC 9136](https://www.rfc-editor.org/rfc/rfc9136.html).

## 14. Vue synthétique

| Type | Nom courant | Fonction principale |
|---|---|---|
| Type 1 | Ethernet Auto-Discovery | Identification des informations liées à un segment Ethernet et procédures d'annonce ou de retrait |
| Type 2 | MAC/IP Advertisement | Annonce d'une adresse MAC et éventuellement d'une adresse IP associée |
| Type 3 | Inclusive Multicast Ethernet Tag | Signalisation de participation à un segment et informations utilisées pour les procédures BUM |
| Type 4 | Ethernet Segment | Identification et découverte des participants à un segment Ethernet multihébergé |
| Type 5 | IP Prefix | Annonce de préfixes IP pour les scénarios de routage EVPN concernés |

Ces descriptions sont volontairement synthétiques. Chaque type possède des champs et des règles de traitement précis.

## 15. Type 2 — MAC/IP Advertisement Route

La route de type 2 annonce principalement une adresse MAC et peut aussi transporter une adresse IP associée.

Elle est essentielle dans les architectures VXLAN EVPN où les VTEP ont besoin de connaître les adresses MAC distantes.

Si un hôte possède l'adresse MAC `AA:AA:AA:AA:AA:AA`, son VTEP local peut annoncer cette MAC au moyen d'une route de type 2. Lorsque les conditions d'importation et de sélection sont satisfaites, les autres équipements concernés peuvent installer les informations nécessaires au forwarding.

L'annonce peut également comprendre une adresse IP. Cette association MAC/IP contribue à plusieurs mécanismes, notamment la suppression de certaines diffusions ARP et les fonctions de routage selon la conception.

La réception d'une route de type 2 ne signifie pas automatiquement que toutes les étapes du forwarding sont opérationnelles. Le next-hop doit être résolu, la route doit être acceptée et les informations doivent être installées dans les structures appropriées.

## 16. Type 3 — Inclusive Multicast Ethernet Tag Route

La route de type 3 fournit des informations utilisées pour identifier les VTEP participants à une instance Ethernet et pour établir les mécanismes nécessaires à la distribution du trafic BUM.

Dans une architecture utilisant VXLAN, les VTEP doivent savoir comment joindre les autres participants auxquels le trafic de diffusion, le multicast ou les unicasts inconnus doivent être envoyé.

La route de type 3 participe à cette fonction selon les procédures de l'architecture EVPN et les mécanismes de transport choisis.

Il ne faut pas la confondre avec une entrée MAC individuelle. Une route de type 3 renseigne sur la participation et le transport du trafic dans le contexte concerné.

Elle est particulièrement importante lorsque l'overlay utilise des mécanismes d'inclusion et de réplication pour le trafic BUM.

## 17. Type 1 — Ethernet Auto-Discovery Route

Les routes de type 1 jouent un rôle important dans les procédures de découverte et de convergence, notamment lorsque des équipements multihébergent un segment Ethernet.

Elles peuvent être associées à un Ethernet Segment ou à une instance Ethernet, selon la forme de la route et son usage.

Dans les procédures EVPN, ces informations participent notamment au retrait rapide des routes associées à un segment ou à une instance lorsqu'un chemin devient indisponible.

Il faut distinguer les procédures par segment Ethernet des procédures par instance Ethernet. La signification de la route dépend des champs, du contexte et de la procédure appliquée.

Une compréhension approfondie de ces routes devient importante pour analyser les mécanismes de convergence et de mass withdrawal.

## 18. Type 4 — Ethernet Segment Route

La route de type 4 permet aux équipements EVPN de découvrir des participants associés à un même Ethernet Segment.

Elle joue un rôle particulièrement important dans les architectures multihébergées, où plusieurs VTEP ou équipements réseau sont reliés au même équipement ou segment Ethernet.

Les participants peuvent alors détecter l'existence du segment et mettre en œuvre les procédures nécessaires, notamment celles liées à l'élection du Designated Forwarder et aux mécanismes de prévention des boucles.

La route de type 4 n'est pas une annonce de MAC individuelle. Elle fournit les informations liées au segment Ethernet lui-même.

## 19. Type 5 — IP Prefix Route

La route de type 5 est destinée à l'annonce de préfixes IP dans les scénarios EVPN qui nécessitent de distribuer des informations de routage au-delà des simples associations MAC/IP d'hôtes.

Elle est particulièrement utile dans les architectures de centres de données comportant plusieurs sous-réseaux, des VNI de couche 3 ou des passerelles qui doivent annoncer des préfixes.

La [RFC 9136](https://www.rfc-editor.org/rfc/rfc9136.html) décrit l'annonce de préfixes IP en EVPN et son rôle dans les scénarios de connectivité entre sous-réseaux.

Une route de type 5 peut participer à la construction des informations de routage dans une IP-VRF. Le forwarding dépend ensuite de la résolution appropriée de la destination, des attributs de route et des mécanismes de transport de l'overlay.

## 20. Pourquoi il faut connaître les types de routes

Les types de routes facilitent le diagnostic du plan de contrôle.

Par exemple :

- Si une MAC distante est absente, il peut être utile de rechercher si l'annonce de type 2 a été produite, reçue et importée.
- Si la participation à un segment et le mécanisme BUM ne fonctionnent pas comme prévu, la route de type 3 peut être pertinente.
- Si un préfixe de réseau distant manque dans une table de routage, le type 5 peut être impliqué dans le scénario concerné.
- Si un équipement multihébergé ne converge pas correctement, les informations de types 1 et 4 peuvent être essentielles.

Ces pistes ne remplacent pas les contrôles de politique BGP, de next-hop, d'installation et de forwarding.


# PARTIE 5 — MOBILITÉ MAC/IP

## 21. Pourquoi la mobilité est-elle importante ?

Dans un environnement virtualisé, une machine virtuelle peut être déplacée d'un hyperviseur vers un autre.

Son adresse IP peut rester identique, et il est possible que son adresse MAC soit également conservée.

Le réseau doit alors mettre à jour ses informations de reachability afin que le trafic soit envoyé vers le nouvel emplacement et non vers l'ancien.

Sans mécanisme de mobilité cohérent, plusieurs VTEP pourraient continuer à associer la même MAC à des destinations différentes.

Cela peut produire des chemins incohérents, des pertes de paquets ou un état de forwarding instable.

## 22. Exemple de déplacement

Au départ, une machine virtuelle se trouve derrière VTEP-A. Après déplacement, elle se trouve derrière VTEP-C.

Le plan de contrôle doit alors mettre à jour les informations de reachability et faire en sorte que les chemins obsolètes ne restent pas indéfiniment utilisés.

Les mécanismes EVPN prévoient des informations de mobilité associées aux routes MAC/IP afin de déterminer quelle annonce doit être préférée dans les cas de mobilité concernés. La valeur et la logique précises sont définies par les procédures EVPN.

Il ne faut pas interpréter un simple changement de next-hop comme une preuve suffisante que toutes les tables de forwarding ont été mises à jour.

## 23. Compétition entre annonces

Lorsque la même MAC est annoncée depuis plusieurs emplacements dans un scénario de mobilité, les règles de sélection doivent permettre aux équipements de converger vers l'emplacement approprié.

EVPN prévoit notamment un mécanisme de séquence de mobilité MAC. La sélection doit aussi respecter les autres attributs et procédures applicables.

La mobilité n'autorise pas à ignorer l'origine de l'annonce. Une annonce inattendue peut aussi correspondre à une erreur, à une mauvaise configuration ou à une situation d'usurpation.

L'exploitation doit donc distinguer une mobilité légitime d'une instabilité de reachability.

## 24. Diagnostiquer une mobilité incorrecte

Lorsqu'une machine virtuelle est déplacée, plusieurs contrôles peuvent être nécessaires :

1. Identifier le VTEP qui annonce actuellement la MAC.
2. Vérifier les routes MAC/IP reçues.
3. Examiner les informations de mobilité lorsqu'elles sont présentes.
4. Vérifier les décisions de sélection BGP.
5. Contrôler les entrées de forwarding installées.
6. Examiner les annonces obsolètes ou les événements répétés.
7. Confirmer que les nouveaux chemins transportent les paquets.

Une machine virtuelle qui semble connectée localement n'est pas nécessairement joignable depuis tous les VTEP si les informations de contrôle ne convergent pas correctement.


# PARTIE 6 — ARP SUPPRESSION ET DISTRIBUTION MAC/IP

## 25. Rappel sur ARP

Dans un réseau IPv4, ARP permet de découvrir l'adresse MAC associée à une adresse IP locale.

Lorsqu'un hôte cherche à joindre un voisin dont l'adresse MAC n'est pas connue, il peut émettre une requête ARP.

Dans un réseau Ethernet traditionnel, la requête de diffusion est généralement distribuée aux membres du segment concerné.

Dans un grand overlay, la répétition de ces requêtes peut augmenter le trafic de diffusion, particulièrement si de nombreux hôtes doivent résoudre leurs voisins simultanément.

## 26. Principe de l'ARP suppression

Lorsque les informations IP/MAC sont connues de manière fiable par les mécanismes EVPN, certaines implémentations peuvent répondre localement à des requêtes ARP au lieu de diffuser chaque requête à tous les VTEP du segment.

Cette fonction est couramment appelée ARP suppression.

Son principe repose sur l'existence d'une association IP/MAC suffisamment fiable pour fournir la réponse attendue.

La présence d'une route EVPN ne garantit pas, à elle seule, que toutes les conditions de l'ARP suppression sont satisfaites. Les capacités de la plateforme, l'état de la table et la cohérence des informations doivent être vérifiés.

## 27. Pourquoi ARP suppression améliore-t-elle l'exploitation ?

L'ARP suppression peut réduire la quantité de trafic de diffusion nécessaire pour résoudre les voisins dans certains scénarios.

Elle permet également de s'appuyer davantage sur les informations de contrôle pour répondre aux requêtes.

Toutefois, une information IP/MAC incorrecte peut produire une réponse locale incorrecte et détourner le trafic.

Une architecture bien conçue doit donc contrôler la provenance des associations, la mobilité et les mécanismes de résolution.

## 28. Et IPv6 ?

IPv6 utilise Neighbor Discovery, qui s'appuie sur ICMPv6, plutôt que le protocole ARP d'IPv4.

Les mécanismes de suppression et de proxy Neighbor Discovery dépendent des fonctions prises en charge et des procédures de la plateforme.

Il ne faut pas supposer que la configuration d'ARP suppression fournit automatiquement toutes les fonctions équivalentes pour IPv6.


# PARTIE 7 — VNI DE COUCHE 2 ET VNI DE COUCHE 3

## 29. Pourquoi séparer les VNI de couche 2 et de couche 3 ?

Dans une architecture simple, un VNI peut représenter un segment Ethernet auquel appartiennent des hôtes.

Lorsque plusieurs sous-réseaux doivent communiquer, il faut également une fonction de routage.

Les architectures VXLAN EVPN utilisent souvent :

- Un **L2VNI**, associé à un segment Ethernet de couche 2.
- Un **L3VNI**, associé à une instance de routage, généralement une VRF.

Le L2VNI représente un domaine Ethernet virtuel. Le L3VNI identifie le contexte de routage utilisé par l'overlay pour transporter le trafic routé entre les VTEP, dans les architectures qui mettent en œuvre ce modèle.

La relation exacte entre les VNI et les instances dépend de l'architecture et de l'implémentation.

## 30. Exemple de segmentation par tenant

Imaginons un tenant qui possède deux sous-réseaux : un réseau utilisateurs et un réseau serveurs.

Le réseau utilisateurs est associé à un L2VNI, et le réseau serveurs à un autre L2VNI.

Une VRF fournit le contexte de routage entre ces réseaux. Le tenant possède ainsi des domaines de couche 2 séparés et une instance de routage qui définit les communications autorisées entre les sous-réseaux.

Dans une architecture à L3VNI, le VNI de couche 3 est associé à ce contexte de routage.

Les L2VNI ne deviennent pas des réseaux identiques parce qu'ils partagent la même VRF. Ils conservent leurs fonctions de segmentation de couche 2 et le routage entre eux s'effectue au moyen de la fonction L3.

## 31. Pourquoi utiliser des VRF ?

Une VRF fournit une table de routage logique séparée.

Dans une architecture multi-tenant, les clients peuvent posséder des préfixes IP qui se recouvrent. Une table de routage indépendante permet de maintenir la séparation de leurs décisions de routage.

Cette isolation du plan de routage est essentielle lorsque plusieurs tenants partagent une même infrastructure.

Elle doit toutefois être associée à des politiques d'importation et de filtrage cohérentes. Une VRF ne remplace pas à elle seule toute la politique de sécurité du système.

## 32. Lien entre L2VNI, L3VNI et VRF

Une architecture de type courant peut être représentée ainsi :

```text
TENANT A
  |
  +---- L2VNI USERS
  |
  +---- L2VNI SERVERS
  |
  +---- L3VNI associé à la VRF du tenant
                 |
                 v
          Routage inter-sous-réseaux
```

Le schéma décrit une organisation logique, et non une obligation de configuration identique sur toutes les plateformes.

La conception doit préciser les VNI, les VLAN locaux, les sous-réseaux, les interfaces de routage, la passerelle et les politiques d'importation/exportation.


# PARTIE 8 — IRB : ROUTAGE ET COMMUTATION INTÉGRÉS

## 33. Pourquoi IRB est-il nécessaire ?

IRB signifie Integrated Routing and Bridging.

Cette approche permet de combiner les fonctions de commutation Ethernet et de routage IP au sein d'une architecture EVPN.

Dans un centre de données, les workloads d'un même sous-réseau peuvent communiquer au niveau Ethernet, tandis que les workloads de sous-réseaux différents doivent utiliser une fonction de routage.

IRB définit les mécanismes permettant à l'infrastructure overlay de traiter ces deux types de communication.

La [RFC 9135](https://www.rfc-editor.org/rfc/rfc9135.html) décrit les procédures IRB en EVPN et distingue notamment les modèles de routage symétrique et asymétrique.

## 34. Routage symétrique et asymétrique

Les deux modèles permettent de faire communiquer des sous-réseaux différents.

La différence concerne principalement la façon dont le trafic traverse les VTEP et le contexte dans lequel le routage est effectué.

**IRB asymétrique :** le VTEP d'entrée réalise le routage vers le sous-réseau de destination, puis transporte le trafic dans le VNI de couche 2 de destination. Cela implique que les VTEP concernés disposent des informations de couche 2 nécessaires pour le segment de destination.

**IRB symétrique :** le VTEP d'entrée effectue le routage dans le contexte L3 du tenant et transporte le trafic à travers le L3VNI vers le VTEP distant. Le VTEP de sortie effectue ensuite la résolution et le forwarding vers le segment de couche 2 final.

Le second modèle facilite souvent la séparation des segments L2 et du transport de couche 3 dans les grandes architectures distribuées. Le choix doit néanmoins tenir compte des capacités de la plateforme, des exigences opérationnelles et du modèle de service.

## 35. Exemple de routage inter-sous-réseaux

Considérons deux hôtes appartenant au même tenant :

- Hôte A : `192.168.10.11/24`.
- Hôte B : `192.168.20.12/24`.

Les deux hôtes appartiennent à des sous-réseaux différents. Pour communiquer, ils doivent utiliser une passerelle de couche 3.

Le trafic ne doit donc pas être traité uniquement comme une trame Ethernet qui traverse un même L2VNI.

Le chemin comprend la remise du paquet à la passerelle, le routage IP dans le contexte correct, l'encapsulation appropriée vers le VTEP distant et la remise au segment de destination.

### Principe du routage symétrique

```text
HÔTE A
   |
   v
L2VNI SOURCE
   |
   v
Passerelle / VRF
   |
   v
L3VNI DU TENANT
   |
   v
UNDERLAY IP
   |
   v
VTEP DISTANT
   |
   v
Routage et forwarding de sortie
   |
   v
L2VNI DESTINATION
   |
   v
HÔTE B
```

Ce schéma montre les principales étapes logiques. Le traitement précis des tables et des en-têtes dépend du modèle IRB et de l'implémentation.

## 36. Choisir un modèle IRB

Le choix entre IRB symétrique et asymétrique ne doit pas reposer uniquement sur la simplicité apparente du schéma.

Il faut notamment considérer :

- Le nombre de L2VNI par tenant.
- Le nombre de VTEP.
- Les informations que chaque VTEP doit posséder.
- Les exigences de mobilité.
- Le routage entre sous-réseaux.
- Les possibilités d'optimisation de la plateforme.
- La méthode de distribution des routes.
- Les fonctions de sécurité et de filtrage.
- Les besoins de dépannage et de visibilité.

Les capacités exactes varient entre les systèmes réseau. Une conception doit être validée sur les versions logicielles et les modèles matériels retenus.


# PARTIE 9 — ANYCAST GATEWAY

## 37. Pourquoi l'Anycast Gateway est-elle utilisée ?

Dans une architecture VXLAN distribuée, les hôtes peuvent être répartis entre plusieurs leaf switches.

Si la passerelle IP n'existait que sur un emplacement distant unique, certains flux pourraient devoir traverser inutilement le réseau avant d'être routés.

Une passerelle distribuée permet aux équipements d'offrir le service de passerelle sur les différents leaf switches concernés.

Dans les architectures qui emploient une Anycast Gateway, plusieurs équipements utilisent la même adresse IP de passerelle et, selon la solution, la même adresse MAC de passerelle dans le segment concerné.

Cela permet aux hôtes d'utiliser une passerelle cohérente tout en bénéficiant d'un service de routage local sur les leaf switches.

## 38. Principe de fonctionnement

Un hôte connecté à Leaf-A peut envoyer le trafic destiné à un autre sous-réseau vers l'adresse IP de la passerelle configurée localement.

Un autre hôte, raccordé à Leaf-B, peut utiliser la même adresse de passerelle IP.

Les leaf switches assurent le routage dans la VRF correspondante, selon les routes disponibles et les politiques de l'architecture.

Le fait d'utiliser la même adresse de passerelle ne signifie pas que les deux équipements sont un seul appareil physique. C'est un service distribué qui doit être configuré selon des procédures cohérentes.

## 39. Conditions importantes

Une Anycast Gateway exige une cohérence stricte entre les équipements participants.

Il faut notamment vérifier :

- L'adresse IP de passerelle.
- L'adresse MAC de passerelle lorsque la solution en utilise une commune.
- Le sous-réseau associé.
- Le L2VNI et la VRF.
- Les fonctions ARP/ND.
- Les annonces EVPN.
- Les politiques de routage.
- Les comportements lors d'une panne ou d'un déplacement de workload.

Une incohérence entre deux leaf switches peut provoquer des comportements de forwarding imprévisibles, des problèmes de résolution de voisins ou une connectivité partielle.

## 40. Ce que l'Anycast Gateway ne garantit pas

La présence d'une passerelle distribuée ne garantit pas que tous les flux fonctionnent correctement.

Les routes doivent être disponibles, les VNI doivent être cohérents et les politiques de filtrage doivent autoriser la communication.

Il faut également distinguer le fait que la passerelle réponde à une requête ARP/ND du fait qu'elle puisse transmettre le paquet vers sa destination.

La disponibilité du service doit être vérifiée au moyen de tests de connectivité et de contrôles du plan de données.


# PARTIE 10 — COMPRENDRE LA ROUTE EVPN DE TYPE 5

## 41. Pourquoi annoncer des préfixes IP ?

Les routes MAC/IP de type 2 permettent notamment d'annoncer les informations relatives à des hôtes et à leurs associations MAC/IP.

Dans certaines architectures, il est utile d'annoncer des préfixes IP plutôt que de distribuer uniquement des routes individuelles d'hôtes.

La route de type 5 est conçue pour l'annonce de préfixes IP dans EVPN. Elle peut participer au routage entre sous-réseaux et à la distribution de routes de réseaux situés derrière des équipements de type VTEP ou passerelle.

La [RFC 9136](https://www.rfc-editor.org/rfc/rfc9136.html) décrit les routes EVPN de type 5 et les procédures associées à la distribution de préfixes IP.

## 42. Différence entre route d'hôte et route de préfixe

Une route de type 2 peut annoncer une adresse MAC et éventuellement l'adresse IP associée à un hôte. Dans certains scénarios, ces informations peuvent aussi contribuer à la création de routes d'hôtes dans une IP-VRF.

Une route de type 5 annonce un préfixe IP.

Par exemple, une route peut représenter le réseau `192.168.20.0/24` plutôt qu'une seule adresse de machine.

Cette distinction est importante dans les architectures comprenant des sous-réseaux, des passerelles distribuées ou des réseaux IP accessibles derrière une frontière de routage.

## 43. Comment la route de type 5 est-elle utilisée ?

Lorsqu'un équipement reçoit une route de type 5 et l'importe dans le contexte approprié, il peut installer le préfixe dans la table de routage logique correspondante si la route est sélectionnée et si les conditions de forwarding sont satisfaites.

Le paquet sera ensuite traité selon les règles de routage de l'instance et les mécanismes de transport associés.

La route de type 5 ne crée pas une communication sans contrôle : il faut encore une politique d'importation adaptée, une résolution de next-hop correcte et une infrastructure capable d'acheminer le trafic.

## 44. Dépanner une absence de préfixe

Si un préfixe attendu est absent d'une VRF, plusieurs vérifications sont nécessaires :

1. La route est-elle produite par l'équipement source ?
2. La famille d'adresses EVPN est-elle active sur la session BGP ?
3. La route est-elle annoncée au voisin ou au route reflector ?
4. Les politiques BGP permettent-elles de la distribuer ?
5. Le Route Target attendu est-il présent et importé ?
6. Le next-hop est-il résoluble ?
7. La route est-elle acceptée par les règles locales ?
8. Une autre route est-elle préférée ?
9. La route est-elle installée dans la table de routage de la VRF ?

Il faut distinguer une route absente du plan de contrôle d'une route présente mais non installée. Les actions de dépannage diffèrent selon le cas.


# PARTIE 11 — MULTIHOMING EVPN

## 45. Pourquoi connecter un équipement à plusieurs leaf switches ?

Dans un centre de données, un serveur, un commutateur d'accès ou un autre équipement peut être raccordé à plusieurs équipements réseau pour améliorer la disponibilité.

Cette conception est appelée multihoming.

Elle permet de maintenir plusieurs chemins vers le même segment Ethernet, mais introduit des risques si les deux chemins transmettent les mêmes trames sans coordination.

Il faut donc prévoir un mécanisme de contrôle des chemins, de découverte des participants et de prévention des boucles.

EVPN possède des procédures pour gérer des segments Ethernet multihébergés. Les fonctions exactes disponibles dépendent du type de multihoming et de l'implémentation.

## 46. Le rôle de l'Ethernet Segment Identifier

L'Ethernet Segment Identifier, ou ESI, identifie un segment Ethernet multihébergé dans l'architecture EVPN.

Il permet aux équipements de reconnaître qu'ils participent au même segment logique connecté à un équipement ou à un réseau aval.

L'ESI contribue aux procédures de découverte, de convergence et de prévention des boucles.

Il ne doit pas être confondu avec une adresse MAC d'hôte, un VNI ou un Route Target.

Chaque objet a un rôle différent :

- Le VNI identifie le segment VXLAN.
- L'ESI identifie un segment Ethernet multihébergé dans EVPN.
- Le Route Target influence l'importation des routes.
- Le Route Distinguisher participe à l'unicité des routes VPN dans le contexte BGP.

## 47. Les modes de multihoming

Selon la plateforme et l'architecture, le multihoming peut fonctionner selon différentes formes.

**All-active :** plusieurs chemins peuvent être utilisés simultanément pour le forwarding lorsque les procédures EVPN, les politiques et les capacités de la plateforme le permettent.

**Single-active :** un seul chemin est actif pour le forwarding considéré, tandis qu'un ou plusieurs chemins peuvent servir de secours selon la procédure mise en œuvre.

Le choix dépend des besoins de disponibilité, du type d'équipement aval, des possibilités de forwarding et des fonctions d'implémentation.

Il ne faut pas supposer que toute architecture dual-homed est automatiquement all-active.

## 48. Le Designated Forwarder

Dans EVPN, le Designated Forwarder, ou DF, est l'équipement chargé de transmettre certains trafics BUM vers un segment Ethernet multihébergé selon les procédures applicables.

Ce mécanisme contribue à éviter que plusieurs participants transmettent simultanément les mêmes trames vers l'équipement aval lorsque le modèle l'interdit.

Le DF est lié à l'ES, à l'instance Ethernet et aux procédures d'élection. Il ne faut pas le confondre avec le simple équipement qui possède actuellement la meilleure route pour une adresse IP.

La [RFC 8584](https://www.rfc-editor.org/rfc/rfc8584.html) décrit le cadre d'élection du Designated Forwarder. Les extensions de multihoming et les procédures de split horizon ont également évolué, notamment avec la [RFC 9746](https://www.rfc-editor.org/rfc/rfc9746.html).

## 49. Prévention des boucles et split horizon

Dans une architecture multihébergée, une trame peut potentiellement revenir sur le segment par un chemin redondant.

Les procédures de split horizon servent à empêcher certaines retransmissions qui pourraient créer des boucles.

Le traitement précis dépend du type de tunnel et du mode de multihoming.

Il faut donc examiner la procédure associée à l'encapsulation VXLAN plutôt que transposer directement les comportements d'un réseau MPLS.

L'objectif est d'assurer que les trames sont transmises sur les chemins autorisés sans reboucler vers le même segment.

## 50. Mass withdrawal et convergence

Lorsqu'un chemin ou un participant associé à un segment Ethernet disparaît, les autres équipements doivent pouvoir mettre à jour leur état de forwarding.

Les procédures de retrait massif, ou *mass withdrawal*, permettent de retirer efficacement un ensemble de routes associé à un segment ou à une instance selon les mécanismes définis.

L'objectif est d'éviter d'attendre le vieillissement indépendant de nombreuses entrées alors qu'une défaillance commune rend les routes obsolètes.

La convergence dépend néanmoins de plusieurs facteurs :

- La détection de la panne.
- L'annonce ou le retrait des informations de contrôle.
- La propagation BGP.
- La sélection des chemins restants.
- La mise à jour des tables de forwarding.
- Les capacités et limites de la plateforme.

Une session BGP qui reste établie ne prouve pas que toutes les informations de forwarding sont correctes.


# PARTIE 12 — MOBILITÉ MAC ET CONVERGENCE

## 51. Mobilité d'un hôte virtuel

Une machine virtuelle peut changer de serveur physique tout en conservant ses paramètres réseau.

Le VTEP d'origine peut alors posséder une ancienne association entre la MAC et sa destination. Le nouveau VTEP doit annoncer l'emplacement actuel selon les procédures EVPN appropriées.

Le réseau doit traiter les informations de mobilité afin de converger vers le bon emplacement.

Une conception correcte doit aussi prendre en charge le retrait d'informations obsolètes et éviter que des annonces répétées produisent un état instable.

## 52. Comprendre une instabilité MAC

Une MAC qui apparaît alternativement derrière plusieurs emplacements peut indiquer :

- Une mobilité légitime.
- Une mauvaise configuration.
- Une boucle de couche 2.
- Une association incorrecte entre segments.
- Un problème de multihoming.
- Une source de trafic ou un comportement d'équipement inattendu.

Le simple fait de voir une MAC changer de VTEP ne suffit donc pas à conclure qu'il existe une attaque ou une erreur.

Il faut étudier la chronologie, les informations de mobilité, les routes reçues et le contexte du segment.

## 53. Prévenir les conclusions hâtives

Lors d'une panne, il faut distinguer les informations de contrôle annoncées de celles effectivement sélectionnées et installées.

Une route peut être reçue par BGP sans être retenue comme chemin actif.

Elle peut également être active dans le plan de contrôle mais ne pas produire le résultat attendu dans le plan de données.

Le diagnostic doit donc associer plusieurs éléments :

- Les routes reçues.
- Les attributs de sélection.
- Le next-hop.
- Le VNI et le segment associés.
- L'état des interfaces.
- Les entrées MAC/IP.
- Les compteurs de forwarding.
- Les observations du trafic réel.

Cette démarche permet d'identifier la couche où apparaît l'incohérence.


# PARTIE 13 — MÉTHODE DE DÉPANNAGE AVANCÉE

## 54. Séparer le diagnostic en quatre domaines

Une architecture VXLAN EVPN peut présenter des pannes liées à quatre domaines principaux.

### Domaine 1 — Underlay

Le transport IP ne fournit pas la connectivité nécessaire.

### Domaine 2 — Sessions et politiques BGP EVPN

Les sessions ne sont pas établies, les familles d'adresses ne sont pas activées ou les politiques empêchent la distribution des routes nécessaires.

### Domaine 3 — Sélection et installation des routes EVPN

Les routes peuvent être absentes, rejetées, non sélectionnées ou non installées dans le contexte logique attendu.

### Domaine 4 — Plan de données

L'encapsulation, le forwarding, le VNI, la MTU ou la remise locale sont incorrects.

Une panne peut toucher plusieurs domaines simultanément. La méthode consiste à identifier les premières conditions qui ne sont plus satisfaites.

## 55. Cas A — Route de type 2 absente

Une machine virtuelle ne peut pas être atteinte depuis un autre leaf switch et son adresse MAC n'apparaît pas dans les informations distantes attendues.

Il faut d'abord vérifier que le VTEP local a effectivement appris la MAC et qu'il dispose d'une association locale correcte.

Si l'association existe, il faut examiner si l'annonce EVPN est produite, si la session BGP distribue la route et si les politiques permettent son importation.

Lorsque la route est reçue, il faut vérifier si elle est sélectionnée et installée dans le contexte de forwarding approprié.

Modifier les VNI n'est pas une réponse automatique à l'absence d'une route MAC/IP.

## 56. Cas B — Route reçue, mais trafic perdu

Une route MAC/IP apparaît dans la table BGP EVPN, mais les paquets n'arrivent pas à destination.

Il faut vérifier :

- Le next-hop de la route.
- La résolution du next-hop dans l'underlay.
- Le VNI et les informations d'encapsulation.
- Les entrées de forwarding installées.
- Les interfaces et les compteurs.
- La réception du paquet au VTEP distant.
- Le traitement après décapsulation.

Il faut également vérifier si le paquet est envoyé dans le contexte VRF ou L2VNI attendu.

## 57. Cas C — Routes Type 5 absentes

Un sous-réseau distant ne figure pas dans la table de routage de la VRF prévue.

Le diagnostic doit déterminer si le préfixe est annoncé, s'il est distribué dans BGP EVPN, si le Route Target permet son importation et si le next-hop est résoluble.

La route peut aussi être rejetée ou non sélectionnée en raison d'une politique locale ou d'une autre route préférée.

La présence d'une route EVPN dans une table ne garantit pas qu'elle sera installée dans la table de routage de la VRF.

## 58. Cas D — Problème d'Anycast Gateway

Un hôte peut joindre son réseau local, mais les communications vers les sous-réseaux distants échouent.

Le diagnostic doit examiner l'adresse de passerelle, la cohérence des paramètres de l'Anycast Gateway, l'association à la VRF, les routes pertinentes et la résolution des voisins.

Il faut distinguer les problèmes de la passerelle locale des problèmes de routage entre VTEP et des politiques de filtrage.

## 59. Cas E — Multihoming instable

Un équipement connecté à deux leaf switches présente des pertes intermittentes ou des flux qui fonctionnent dans un seul sens.

Il faut examiner les informations relatives à l'ESI, les routes de découverte du segment, l'élection du DF lorsque pertinente, les états des liens et les procédures de split horizon.

Les annonces de retrait et l'état du chemin de secours doivent également être vérifiés.

Le multihoming doit être dépanné comme un mécanisme de redondance coordonné, et non comme deux connexions indépendantes au même segment.

## 60. Ordre recommandé de vérification

Un ordre de vérification raisonnable est le suivant :

1. Vérifier le transport IP entre les adresses de VTEP.
2. Vérifier les sessions BGP et la famille d'adresses EVPN.
3. Examiner les routes EVPN pertinentes.
4. Vérifier les RD, les RT et les politiques d'importation.
5. Contrôler les next-hops et leur résolution.
6. Examiner l'installation des routes et les tables MAC/IP/VRF.
7. Vérifier les VNI et l'encapsulation.
8. Observer le trafic sur le plan de données.
9. Vérifier la décapsulation et la remise locale.
10. Confirmer le résultat avec un test de bout en bout.

Cette méthode n'est pas un ordre immuable. Une panne déjà localisée par une preuve directe peut permettre d'aller directement au composant concerné.


# PARTIE 14 — SÉCURITÉ D'UNE ARCHITECTURE VXLAN EVPN

## 61. L'encapsulation n'est pas une garantie de sécurité

VXLAN transporte les données mais ne chiffre pas automatiquement leur contenu.

EVPN distribue des informations de contrôle, mais ne remplace pas toutes les politiques d'accès au réseau.

La sécurité d'une architecture doit couvrir à la fois le transport, le plan de contrôle, le segment virtuel et les procédures d'administration.

Les préoccupations comprennent :

- Les sources autorisées à échanger du trafic VXLAN.
- La protection des sessions BGP.
- Les politiques d'importation et d'exportation de routes.
- La validation des informations de reachability.
- La séparation des tenants.
- Les politiques de flux entre sous-réseaux.
- La protection des interfaces d'administration.
- La journalisation des changements.
- La détection d'une anomalie ou d'un mouvement inattendu de MAC.

## 62. Séparation des tenants

Une architecture multi-tenant doit séparer les instances de couche 2 et de couche 3 selon les règles prévues.

Les L2VNI identifient des segments Ethernet. Les VRF et les L3VNI, lorsqu'ils sont employés, fournissent des contextes de routage distincts.

Les Route Targets déterminent quelles routes peuvent être importées dans les instances correspondantes.

Une erreur de conception ou de politique peut entraîner une fuite de routes entre tenants.

Il faut donc examiner les routes importées et les chemins de forwarding qui en résultent, au lieu de se fier uniquement aux valeurs inscrites dans la configuration.

## 63. Protection du plan de contrôle

BGP EVPN doit être protégé conformément aux règles de sécurité de l'environnement.

Les mesures appropriées peuvent inclure :

- La restriction des pairs BGP autorisés.
- Le filtrage des sessions et des adresses de transport.
- La protection des plans de contrôle selon les fonctions de la plateforme.
- La validation des politiques d'importation et d'exportation.
- Le contrôle des versions de configuration.
- La surveillance des changements d'état.
- La documentation des procédures de reprise.

La portée exacte de chaque mécanisme dépend de la plateforme et de la conception BGP.

## 64. Détecter les changements inattendus

Les informations de mobilité MAC/IP peuvent changer dans le cadre du fonctionnement normal.

Toutefois, une fréquence anormalement élevée de changements ou des annonces contradictoires peuvent révéler un problème.

Une stratégie d'exploitation doit distinguer les événements légitimes des anomalies. Les alertes doivent être corrélées avec la topologie, l'activité des machines virtuelles et l'état des équipements.

L'objectif n'est pas de bloquer automatiquement toute mobilité, mais de vérifier que le comportement correspond aux attentes.


# PARTIE 15 — CONSTRUIRE UN LABORATOIRE EVPN CONCEPTUEL

## 65. Objectif

Le laboratoire expert reprend l'architecture du niveau intermédiaire, mais introduit le plan de contrôle.

Il ne s'agit plus seulement de configurer des destinations statiques. Les équipements doivent établir les sessions BGP EVPN prévues, échanger des routes et interpréter leurs attributs.

La configuration exacte dépend de la plateforme retenue. Les concepts qui suivent sont indépendants de la syntaxe propre à un constructeur.

## 66. Topologie de travail

```text
                 CONTRÔLE BGP EVPN
             +-------------------------+
             |                         |
             v                         v
          LEAF-A                    LEAF-B
          VTEP-A                    VTEP-B
             |                         |
             +------- UNDERLAY IP ------+
             |                         |
          HÔTE A                    HÔTE B

        L2VNI / L3VNI selon le service
```

Cette architecture représente une topologie conceptuelle à deux leaf switches.

Dans une architecture plus importante, des route reflectors peuvent distribuer les routes EVPN, tandis que l'underlay relie les adresses de transport.

## 67. Étape 1 — Valider l'underlay

Avant d'activer les services EVPN, il faut vérifier la connectivité IP entre les adresses utilisées par les VTEP et les pairs BGP.

Les tables de routage doivent contenir les chemins nécessaires. Les tests doivent confirmer que le transport fonctionne de manière cohérente.

Cette étape doit être documentée pour permettre de distinguer une panne de transport d'une panne du plan de contrôle.

## 68. Étape 2 — Établir BGP EVPN

La session BGP doit être configurée selon l'architecture retenue.

Il faut vérifier :

- Le voisinage BGP.
- La famille d'adresses EVPN.
- Les politiques de distribution.
- Les next-hops annoncés.
- Les Route Targets importés.
- La résolubilité des destinations.

Le statut de la session est un indicateur de transport et de contrôle, mais il ne suffit pas à confirmer que les routes utiles sont présentes.

## 69. Étape 3 — Définir les instances logiques

Les VNI doivent être associés aux segments et aux VRF prévus.

L'architecture doit définir :

- Les L2VNI.
- Les L3VNI, si le modèle utilisé en nécessite.
- Les associations entre VLAN et L2VNI.
- Les sous-réseaux des hôtes.
- Les passerelles.
- Les politiques de routage.
- Les Route Targets.
- Les paramètres de l'Anycast Gateway si elle est utilisée.

La conception doit être centralisée et documentée afin d'éviter les incohérences entre leaf switches.

## 70. Étape 4 — Vérifier les annonces

Les routes EVPN attendues doivent être observées dans les tables BGP.

Il faut distinguer la génération d'une route, sa réception, son acceptation par la politique, sa sélection et son installation dans le contexte logique approprié.

Une route qui n'apparaît pas à une étape donnée doit être recherchée à cette étape plutôt que corrigée au hasard ailleurs.

## 71. Étape 5 — Vérifier le plan de données

Lorsque les routes nécessaires sont présentes, vérifiez le forwarding.

Il faut confirmer que :

- Le VNI utilisé correspond au segment prévu.
- Le next-hop est correct.
- Les adresses MAC/IP sont associées au bon emplacement.
- Les paquets peuvent être encapsulés et reçus.
- Le VTEP distant décapsule le paquet.
- La trame est remise au bon segment.
- Le trafic retour fonctionne également.

Un test de communication doit être complété par des vérifications du chemin pour établir une conclusion fiable.

## 72. Étape 6 — Tester les scénarios de panne

Un laboratoire expert doit également tester des situations anormales, avec des mécanismes de reprise clairement prévus.

Les scénarios peuvent inclure :

- Retrait d'un chemin de transport.
- Arrêt d'une session BGP.
- Retrait d'une annonce MAC/IP.
- Déplacement contrôlé d'une machine virtuelle.
- Perte d'un lien d'un segment multihébergé.
- Incohérence volontaire d'un paramètre de laboratoire.

Les tests doivent être effectués dans un environnement isolé et rétabli après chaque exercice.

La réussite d'un seul test ne prouve pas que toutes les fonctions de convergence sont correctes. Il faut mesurer les résultats et vérifier que les décisions du plan de contrôle correspondent à la topologie restante.


# PARTIE 16 — ÉVOLUTIVITÉ ET CONCEPTION

## 73. Pourquoi l'évolutivité dépend-elle du plan de contrôle ?

Une architecture peut transporter correctement le trafic avec peu de VTEP, puis rencontrer des difficultés lorsque le nombre d'équipements et de routes augmente.

Le nombre de routes, les politiques d'importation, la charge des sessions BGP, le nombre de destinations et la fréquence des changements doivent être pris en compte dans la conception.

EVPN améliore la structuration du contrôle, mais la taille des tables et les capacités des équipements restent des contraintes.

Il faut notamment examiner :

- Le nombre de VTEP.
- Le nombre de segments logiques.
- Le nombre de routes MAC/IP.
- Le nombre de préfixes annoncés.
- Le nombre de VRF.
- Les besoins en BUM et en réplication.
- Les événements de mobilité.
- Le nombre de chemins redondants.
- Les limites matérielles des tables de forwarding.

## 74. ECMP et répartition de charge

Dans l'underlay, ECMP permet d'utiliser plusieurs chemins de coût égal vers une destination lorsque le routage et la plateforme le permettent.

VXLAN ajoute des en-têtes extérieurs qui peuvent servir à identifier les flux pour le hachage. Les champs utilisés et la qualité de la répartition dépendent des équipements.

La présence de plusieurs chemins ECMP ne signifie pas automatiquement que tous les flux seront répartis uniformément.

Le dimensionnement doit également tenir compte des défaillances de liens et des modifications du chemin retenu.

## 75. Charge de l'apprentissage et du contrôle

Dans de grands environnements, la quantité de routes MAC/IP peut devenir importante.

Les annonces, retraits et événements de mobilité affectent le traitement BGP et la mise à jour des tables de forwarding.

Une architecture doit être conçue pour éviter les instabilités inutiles et disposer d'une visibilité suffisante sur la convergence.

La stabilité dépend aussi du comportement des workloads, de la fréquence des déplacements et des capacités de l'underlay.

## 76. Plan de contrôle et plan de données doivent rester cohérents

Le plan de contrôle peut annoncer un état différent de celui réellement disponible dans le réseau si une panne, une erreur ou un retard empêche certaines mises à jour.

Une architecture robuste doit donc être observée sur les deux plans.

Le plan de contrôle indique quelles routes sont connues et sélectionnées. Le plan de données montre si le trafic utilise réellement les chemins prévus.

Pour comprendre une panne, il faut relier les routes, les next-hops, les entrées de forwarding et les paquets effectivement transmis.


# PARTIE 17 — EXERCICES CORRIGÉS

## 77. Exercice 1 — Rôle d'EVPN

**Question :** pourquoi utiliser EVPN au lieu de configurer manuellement toutes les destinations VXLAN dans un grand réseau ?

### Correction

EVPN fournit un mécanisme structuré de distribution des informations de reachability.

Il aide à gérer les annonces MAC/IP, la participation des VTEP aux instances Ethernet, la mobilité et certains scénarios de routage et de multihoming.

La configuration statique peut suffire pour un petit laboratoire, mais elle devient plus difficile à maintenir lorsque le nombre de participants et de changements augmente.

## 78. Exercice 2 — Route de type 2

**Question :** un hôte est joignable localement, mais sa route MAC/IP n'apparaît pas sur le VTEP distant. Quelles vérifications effectuer ?

### Correction

Il faut vérifier que le VTEP source a bien appris l'adresse MAC, que l'annonce de type 2 est produite, qu'elle est distribuée par BGP EVPN et que les politiques permettent son importation.

Il faut ensuite vérifier la sélection de route, le next-hop et l'installation dans les structures de forwarding.

## 79. Exercice 3 — Route Target

**Question :** quelle différence existe entre le Route Distinguisher et le Route Target ?

### Correction

Le RD contribue à distinguer les routes VPN dans le contexte BGP.

Le RT sert aux politiques d'importation et d'exportation des routes dans les instances concernées.

Une erreur de RD peut affecter l'identité des routes. Une erreur de RT peut provoquer une route absente ou une distribution non souhaitée entre instances.

## 80. Exercice 4 — Route de type 3

**Question :** à quoi sert principalement la route EVPN de type 3 ?

### Correction

Elle fournit des informations liées à la participation à une instance Ethernet et aux procédures de diffusion ou de réplication du trafic BUM dans l'architecture EVPN.

Elle ne remplace pas une annonce MAC individuelle de type 2.

## 81. Exercice 5 — Type 5

**Question :** pourquoi une route de type 5 peut-elle être utile en complément des routes MAC/IP de type 2 ?

### Correction

La route de type 5 permet d'annoncer des préfixes IP.

Elle est utile dans les architectures qui doivent distribuer des routes de sous-réseaux, notamment pour des services de routage EVPN et certains scénarios inter-sous-réseaux.

## 82. Exercice 6 — IRB

**Question :** quelle différence fondamentale existe entre IRB symétrique et asymétrique ?

### Correction

Dans le modèle asymétrique, le VTEP d'entrée effectue le routage et transporte ensuite le paquet dans le L2VNI de destination.

Dans le modèle symétrique, le trafic routé traverse le L3VNI associé au contexte de routage du tenant et le VTEP distant effectue la résolution vers le L2VNI final.

Le choix dépend de l'architecture et de la prise en charge de la plateforme.

## 83. Exercice 7 — Anycast Gateway

**Question :** pourquoi plusieurs leaf switches peuvent-ils présenter la même adresse de passerelle ?

### Correction

L'Anycast Gateway permet à plusieurs leaf switches de fournir le même service logique de passerelle aux workloads du réseau concerné.

Cela facilite le routage local et réduit certaines dépendances à une passerelle distante unique.

La configuration doit rester cohérente entre les équipements participants.

## 84. Exercice 8 — Mobilité MAC

**Question :** pourquoi une annonce MAC provenant d'un nouvel emplacement ne doit-elle pas être traitée comme un simple ajout sans tenir compte de l'ancien emplacement ?

### Correction

La même MAC peut alors être associée simultanément à plusieurs emplacements.

EVPN possède des mécanismes de mobilité permettant aux équipements d'identifier et de gérer les changements de reachability.

Il faut vérifier les annonces, les informations de mobilité et la sélection de route pour éviter de conserver des chemins obsolètes.

## 85. Exercice 9 — Multihoming

**Question :** pourquoi le multihoming nécessite-t-il des mécanismes de prévention des boucles ?

### Correction

Plusieurs chemins peuvent relier le même segment Ethernet à l'overlay.

Sans coordination, une trame peut revenir vers le même segment ou être répliquée de manière incorrecte.

Les procédures EVPN associées à l'ESI, au DF et au split horizon contribuent à gérer ces situations selon le modèle de multihoming utilisé.

## 86. Exercice 10 — Dépannage

**Question :** une route EVPN est présente dans BGP mais le trafic ne passe pas. Peut-on conclure que le plan de contrôle est entièrement correct ?

### Correction

Non.

La présence d'une route ne prouve pas que le next-hop est résolu, que la route est installée dans le bon contexte ou que le plan de données transmet les paquets correctement.

Il faut examiner l'ensemble de la chaîne, depuis la sélection des routes jusqu'à l'encapsulation, au transport et à la remise locale.


# PARTIE 18 — ERREURS FRÉQUENTES AU NIVEAU EXPERT

## 87. Confondre VXLAN et EVPN

VXLAN est une encapsulation de données. EVPN est une solution de contrôle et de distribution des informations de reachability.

Les deux technologies peuvent fonctionner ensemble, mais elles ne remplissent pas le même rôle.

## 88. Considérer toute route BGP reçue comme installée

Une route reçue peut être rejetée, non sélectionnée ou ne pas être installée dans la table correspondant au service attendu.

Il faut examiner les politiques, la sélection de route et le forwarding.

## 89. Confondre RD et RT

Le RD et le RT ont des rôles différents.

Une politique d'importation incorrecte peut faire apparaître ou disparaître des routes dans des instances où elles devraient être isolées.

## 90. Supposer que la présence d'un VNI garantit le forwarding

Le VNI est un élément de segmentation. Il ne suffit pas à démontrer que les destinations MAC/IP sont connues, que les next-hops sont résolus et que les paquets peuvent traverser l'underlay.

## 91. Considérer une passerelle Anycast comme un mécanisme autonome

Une Anycast Gateway doit être accompagnée de routes cohérentes, de VRF adaptées, d'associations de segments et d'une configuration compatible sur les leaf switches concernés.

## 92. Ignorer les particularités de multihoming

Le comportement en all-active ou single-active, les procédures de DF et les mécanismes de split horizon dépendent de l'architecture et de l'implémentation.

Les commandes et les hypothèses d'un constructeur ne doivent pas être appliquées automatiquement à un autre.

## 93. Ne regarder que le plan de contrôle

Les routes EVPN peuvent être correctes alors que le transport ou le forwarding présente un défaut.

Le dépannage doit inclure des observations du plan de données.

## 94. Ne regarder que les paquets

Une capture VXLAN peut montrer des paquets qui circulent sans que la distribution des routes EVPN soit correcte de façon durable.

Le plan de données et le plan de contrôle doivent être examinés ensemble.


# PARTIE 19 — GLOSSAIRE EXPERT

**BGP EVPN :** utilisation de la famille d'adresses EVPN de BGP pour distribuer des informations de connectivité Ethernet et IP dans les architectures correspondantes.

**Route Distinguisher (RD) :** valeur utilisée pour distinguer les routes VPN dans leur représentation BGP.

**Route Target (RT) :** communauté étendue utilisée pour les politiques d'importation et d'exportation des routes VPN.

**MAC-VRF :** instance logique de gestion des informations Ethernet et MAC pour un domaine de service.

**IP-VRF :** instance logique de routage IP distincte, utilisée notamment pour séparer les domaines de routage des tenants.

**L2VNI :** VNI associé à un segment logique de couche 2.

**L3VNI :** VNI associé à un service ou contexte de couche 3 dans les architectures qui utilisent ce modèle.

**IRB :** Integrated Routing and Bridging, modèle combinant le forwarding Ethernet et le routage IP.

**Symmetric IRB :** modèle dans lequel le trafic routé traverse le contexte L3 de l'overlay, avec traitement de sortie adapté à la destination.

**Asymmetric IRB :** modèle dans lequel le VTEP d'entrée route le paquet et le transporte ensuite dans le segment L2 de destination.

**Anycast Gateway :** service de passerelle distribuée dans lequel plusieurs équipements fournissent une adresse logique commune selon les règles de l'architecture.

**Route Type 1 :** route Ethernet Auto-Discovery utilisée notamment dans les procédures EVPN liées aux segments Ethernet et aux retraits de routes.

**Route Type 2 :** route MAC/IP Advertisement qui annonce une adresse MAC et éventuellement une adresse IP associée.

**Route Type 3 :** route Inclusive Multicast Ethernet Tag associée à la participation au segment et aux procédures BUM.

**Route Type 4 :** route Ethernet Segment utilisée notamment pour découvrir les participants d'un segment Ethernet multihébergé.

**Route Type 5 :** route IP Prefix utilisée pour annoncer des préfixes IP dans les scénarios EVPN correspondants.

**Ethernet Segment Identifier (ESI) :** identifiant d'un segment Ethernet multihébergé.

**Designated Forwarder (DF) :** participant EVPN chargé de certaines opérations de forwarding BUM vers un segment multihébergé selon les procédures applicables.

**Mass withdrawal :** procédure de retrait efficace d'un ensemble de routes associées à un chemin ou à un segment devenu indisponible.

**Mobilité MAC :** mécanismes de mise à jour de la reachability d'une adresse MAC lorsque son emplacement change.

**ARP suppression :** fonction qui permet, dans les conditions prises en charge, de répondre localement à certaines requêtes ARP à partir d'informations IP/MAC connues.

**Convergence :** processus par lequel le contrôle et le forwarding se mettent à jour après un changement ou une panne.

**BUM :** Broadcast, Unknown unicast et Multicast.


# PARTIE 20 — ÉVALUATION FINALE

## 95. Questions théoriques

L'apprenant doit répondre aux questions suivantes sans consulter le cours.

1. Pourquoi EVPN est-il utile dans une architecture VXLAN de grande taille ?
2. Quelle est la différence entre le plan de contrôle et le plan de données ?
3. Quel est le rôle d'une session BGP EVPN ?
4. Pourquoi un route reflector ne remplace-t-il pas l'underlay ?
5. Quelle est la différence entre RD et RT ?
6. À quoi sert une route EVPN de type 2 ?
7. À quoi sert une route de type 3 ?
8. Quel est le rôle des routes de types 1 et 4 dans les scénarios de multihoming ?
9. Dans quels scénarios une route de type 5 est-elle utile ?
10. Comment la mobilité MAC peut-elle affecter le forwarding ?
11. Quel est le rôle de l'ARP suppression ?
12. Quelle différence existe entre L2VNI et L3VNI ?
13. Quelle est la différence entre IRB symétrique et asymétrique ?
14. Quel est le rôle d'une Anycast Gateway ?
15. Pourquoi faut-il contrôler la cohérence des paramètres de passerelle ?
16. Quel est le rôle de l'ESI ?
17. Pourquoi le DF est-il important dans les procédures de multihoming ?
18. Que cherche à accomplir le mécanisme de split horizon ?
19. Pourquoi faut-il distinguer une route reçue d'une route installée ?
20. Comment séparer une panne de plan de contrôle d'une panne de plan de données ?

## 96. Travaux pratiques de conception

### Travail 1 — Architecture multi-tenant

Dessinez une architecture comprenant deux tenants avec des préfixes IP qui se recouvrent.

Définissez les instances logiques, les VNI, les VRF et les politiques de Route Target nécessaires.

Expliquez comment éviter que les routes du premier tenant soient importées involontairement dans le second.

### Travail 2 — Distribution MAC/IP

Décrivez les étapes nécessaires pour qu'une adresse MAC locale soit annoncée, reçue par un autre VTEP et installée dans le contexte de forwarding approprié.

Précisez quels contrôles effectuer si la route n'arrive pas à destination.

### Travail 3 — Routage inter-VNI

Construisez un exemple comprenant deux sous-réseaux d'un même tenant.

Décrivez les rôles du L2VNI source, de la VRF, du L3VNI et du L2VNI de destination dans un modèle de routage symétrique.

### Travail 4 — Mobilité

Décrivez les changements attendus lorsque la même machine virtuelle est déplacée d'un VTEP à un autre.

Expliquez comment la mobilité MAC influence les annonces EVPN et pourquoi les entrées obsolètes doivent être retirées.

### Travail 5 — Multihoming

Concevez un scénario où un segment Ethernet est raccordé à deux leaf switches.

Expliquez la fonction de l'ESI, les conditions d'utilisation du DF et les contrôles nécessaires pour éviter les boucles.

### Travail 6 — Dépannage complet

Un réseau possède une session BGP EVPN active, mais les communications entre deux hôtes ne fonctionnent pas.

Établissez un plan de dépannage qui vérifie successivement les routes pertinentes, les politiques, les next-hops, les tables de forwarding, les VNI et le transport réel.


# PARTIE 21 — TRANSITION VERS LA PRATIQUE AVANCÉE

## 97. Ce qui est maintenant acquis

Le cours expert a approfondi les fonctions qui complètent VXLAN dans une architecture distribuée.

L'apprenant sait maintenant :

- Pourquoi EVPN est utilisé comme plan de contrôle.
- Comment BGP distribue les informations de reachability.
- Quelle différence existe entre RD et RT.
- Quel rôle remplissent les différents types de routes EVPN.
- Comment les informations MAC/IP peuvent être annoncées.
- Comment les L2VNI et L3VNI participent au routage.
- Pourquoi l'IRB est nécessaire pour communiquer entre sous-réseaux.
- Comment l'Anycast Gateway fournit un service de passerelle distribué.
- Quel rôle jouent ESI, DF et split horizon dans le multihoming.
- Pourquoi la mobilité MAC et les mécanismes de convergence doivent être contrôlés.
- Comment séparer les pannes d'underlay, de plan de contrôle et de plan de données.

Ces éléments constituent les fondations de la conception VXLAN EVPN.

## 98. Schéma final du parcours

```text
NIVEAU DÉBUTANT
Comprendre le transport VXLAN
        |
        v
NIVEAU INTERMÉDIAIRE
Configurer et diagnostiquer les VTEP
        |
        v
NIVEAU EXPERT
Distribuer les informations par EVPN
Réaliser le routage inter-VNI
Gérer la mobilité et le multihoming
        |
        v
PRATIQUE AVANCÉE
Conception multi-racks
Convergence et haute disponibilité
Automatisation des validations
Sécurité et exploitation
```

Le parcours ne se termine pas avec la connaissance des types de routes BGP. Une architecture opérationnelle doit encore être adaptée au matériel, à la topologie, aux volumes de routes, aux exigences de disponibilité et aux politiques de sécurité.

La dernière étape consiste à traduire les principes de conception en une configuration qui peut être testée, vérifiée et exploitée.


# CONCLUSION GÉNÉRALE

VXLAN fournit un mécanisme d'encapsulation permettant de transporter des trames Ethernet sur une infrastructure IP. EVPN complète ce mécanisme en distribuant les informations nécessaires à la connaissance des destinations et à la construction du forwarding dans des architectures distribuées.

Le fonctionnement correct de cette architecture repose sur plusieurs éléments complémentaires : un underlay opérationnel, des sessions de contrôle fonctionnelles, des routes cohérentes, des politiques d'importation et d'exportation adaptées, des VNI corrects et des tables de forwarding correctement installées.

Les routes EVPN ont des rôles distincts. Les routes de type 2 servent notamment aux annonces MAC/IP, celles de type 3 contribuent aux procédures liées à la participation et au trafic BUM, les routes de types 1 et 4 participent aux mécanismes associés aux segments et au multihoming, tandis que les routes de type 5 permettent l'annonce de préfixes IP.

Les VNI de couche 2 et de couche 3, associés à des VRF et à des mécanismes IRB adaptés, permettent de construire des services de connectivité entre les sous-réseaux. Une Anycast Gateway peut fournir un service de passerelle distribué lorsque la conception le prévoit.

Le multihoming, la mobilité MAC/IP et la convergence ajoutent des exigences de contrôle. Il ne suffit plus de vérifier qu'un tunnel existe : il faut vérifier que les bonnes informations sont distribuées, sélectionnées et utilisées par le plan de données.

**Principe final : concevoir l'underlay pour transporter les paquets, utiliser EVPN pour distribuer les informations de contrôle, associer correctement les VNI aux services réseau, vérifier la sélection des routes et valider le forwarding réel.**

Une architecture VXLAN EVPN devient fiable lorsque ses choix de conception, ses mécanismes de convergence et ses procédures de dépannage sont compris et vérifiables.


# RÉFÉRENCES TECHNIQUES

## Spécifications de base

- **RFC 7348 — Virtual eXtensible LAN (VXLAN)**  
  https://www.rfc-editor.org/rfc/rfc7348.html

  Spécification de l'encapsulation VXLAN, de l'en-tête et du VNI.

- **RFC 7432 — BGP MPLS-Based Ethernet VPN**  
  https://www.rfc-editor.org/rfc/rfc7432.html

  Spécification de base des routes EVPN et de nombreuses procédures de contrôle. Certaines procédures ont depuis été mises à jour ou complétées par d'autres RFC.

- **RFC 8365 — A Network Virtualization Overlay Solution Using Ethernet VPN (EVPN)**  
  https://www.rfc-editor.org/rfc/rfc8365.html

  Décrit l'utilisation d'EVPN comme solution d'overlay de virtualisation réseau, notamment avec VXLAN.

## Routage et annonces de préfixes

- **RFC 9135 — Integrated Routing and Bridging in Ethernet VPN (EVPN)**  
  https://www.rfc-editor.org/rfc/rfc9135.html

  Décrit l'IRB et les procédures de connectivité entre sous-réseaux.

- **RFC 9136 — IP Prefix Advertisement in Ethernet VPN (EVPN)**  
  https://www.rfc-editor.org/rfc/rfc9136.html

  Décrit les annonces de préfixes IP au moyen des routes EVPN de type 5.

## Multihoming et convergence

- **RFC 8584 — Framework for Ethernet VPN Designated Forwarder Election Extensibility**  
  https://www.rfc-editor.org/rfc/rfc8584.html

  Décrit le cadre de l'élection du Designated Forwarder.

- **RFC 9746 — BGP EVPN Multihoming Extensions for Split-Horizon Filtering**  
  https://www.rfc-editor.org/rfc/rfc9746.html

  Complète les procédures de multihoming et de split horizon EVPN, y compris les considérations propres aux différents types de tunnels.

Les commandes de configuration, les capacités de multihoming, les modèles IRB et les options de routage varient selon les constructeurs et les versions logicielles. Toute architecture de production doit être validée dans la documentation de la plateforme réellement utilisée.