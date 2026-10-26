# Sécurité des commutateurs (Couche 2)

> **Mise en contexte**
>
> Un réseau local peut sembler protégé parce qu'il se trouve derrière un pare-feu, mais une grande partie des communications d'un LAN se déroule à l'intérieur du domaine de commutation. Un poste malveillant, un petit commutateur branché au mauvais endroit, un serveur DHCP clandestin, une table ARP manipulée ou une boucle accidentelle peuvent perturber ou intercepter le trafic sans traverser le pare-feu périmétrique. La sécurité de couche 2 consiste donc à réduire ce qu'un port peut faire, à contrôler les protocoles du LAN et à éviter qu'un équipement d'accès non approuvé devienne un point d'appui.
>
> Ce cours aborde la segmentation VLAN, les ports d'accès et les trunks, les attaques sur les VLAN et les tables MAC, la sécurité de Spanning Tree, la protection DHCP/ARP/IP, le contrôle d'accès 802.1X, le durcissement de la gestion, la supervision et les procédures de diagnostic. Les commandes de configuration sont principalement illustrées avec une syntaxe de type Cisco IOS/IOS XE : la disponibilité des fonctions dépend du modèle, de la version et de la topologie. Les exemples sont pédagogiques et doivent être validés dans un laboratoire avant toute mise en production.

## 1. Objectifs, périmètre et prérequis

La couche 2 du modèle OSI transporte des trames dans un réseau local et utilise notamment les adresses MAC, les VLAN et les mécanismes de commutation. Les dispositifs de sécurité L2 cherchent à garantir qu'un port ne reçoit que les types de trafic attendus, que les domaines de diffusion sont bien délimités et que les protocoles de contrôle ne peuvent pas être détournés par un terminal ordinaire.

À la fin du cours, tu devras savoir expliquer la table MAC et les VLAN, différencier un port d'accès d'un trunk, identifier les risques de VLAN hopping, comprendre le rôle de Spanning Tree et des protections BPDU, configurer le principe de port security, expliquer DHCP Snooping, Dynamic ARP Inspection et IP Source Guard, reconnaître l'intérêt de 802.1X, distinguer les protections IPv4 et IPv6, sécuriser l'accès administratif au commutateur et dépanner les blocages légitimes causés par une politique trop stricte.

Les prérequis sont les adresses MAC, les adresses IP, ARP, DHCP, les VLAN, les trunks 802.1Q, les notions de routage inter-VLAN, les ACL et les bases de configuration en CLI. Le cours privilégie le raisonnement de défense : comprendre la menace, appliquer la protection adaptée, vérifier ce qui est effectivement activé et maintenir une procédure de retour arrière.

## 2. Pourquoi la couche 2 mérite une protection spécifique

Un commutateur apprend les adresses MAC source reçues sur ses ports et associe ces adresses à un VLAN et à une interface. Quand il connaît la destination d'une trame unicast, il peut la transmettre vers le port approprié. Si la destination est inconnue ou si la trame est de diffusion, le commutateur peut la répliquer vers plusieurs ports du même VLAN selon les règles normales de commutation.

Cette logique est efficace, mais elle suppose que les informations apprises et les messages de contrôle correspondent à l'architecture prévue. Un terminal peut usurper une adresse source, générer des trames à grande vitesse, envoyer des réponses DHCP inattendues ou tenter de faire élire un équipement non autorisé comme racine Spanning Tree. L'attaquant n'a pas besoin de compromettre le routeur de sortie pour perturber un VLAN.

La couche 2 n'est pas un périmètre de confiance absolu. La segmentation réduit la portée d'un incident, mais elle n'empêche pas toutes les attaques à l'intérieur d'un VLAN. Une machine malveillante peut tenter de tromper ses voisins, et un trunk mal configuré peut étendre un VLAN au-delà de son périmètre voulu. Il faut donc combiner les protections L2 avec les contrôles d'identité, les pare-feu, la surveillance des hôtes et une conception de réseau documentée.

## 3. La table MAC et les limites de l'apprentissage

La table MAC, parfois appelée CAM table, contient les adresses source observées, leur VLAN et le port sur lequel elles sont apprises. Lorsque le trafic provient d'une nouvelle adresse source, l'entrée peut être ajoutée ou déplacée. Les entrées dynamiques vieillissent généralement après une période d'inactivité ; le comportement exact est propre à la plateforme.

Une attaque de saturation de table MAC tente de produire un grand nombre d'adresses source distinctes afin de consommer les ressources d'apprentissage ou de modifier le comportement de commutation. Selon le matériel et la situation, certains trafics peuvent alors être diffusés dans un périmètre plus large que prévu. Il ne faut pas affirmer que toute saturation entraîne forcément une diffusion de toutes les trames : l'effet dépend de l'architecture et des mécanismes du commutateur.

La protection de port peut limiter le nombre d'adresses MAC apprises sur un port d'accès et définir le traitement d'une violation. Ce contrôle n'arrête pas tous les scénarios d'usurpation : un attaquant peut parfois utiliser une adresse autorisée ou contrôler un appareil déjà légitime. Il constitue un contrôle parmi d'autres, pas une authentification cryptographique de l'utilisateur.

Les symptômes à surveiller comprennent les changements inhabituels d'adresses entre ports, le nombre d'entrées qui augmente rapidement, les alertes de violation, les pertes de trafic, les tempêtes de broadcast et les journaux des interfaces d'accès. Une variation peut cependant être légitime : téléphone IP avec PC en cascade, virtualisation, borne Wi-Fi, hyperviseur ou équipement qui héberge plusieurs adresses. Les limites doivent être calculées à partir de l'inventaire réel.

## 4. VLAN et segmentation

**Schéma pédagogique — Les VLAN séparent les domaines de diffusion ; les règles L3 contrôlent les flux qui franchissent les frontières.**

~~~text
                [Commutateur / routage L3]
                /          |          \
               v           v           v
          VLAN 10       VLAN 30      VLAN 40
          Employes      Equipements  Invites
               |           |           |
               +------ [ACL / pare-feu] ------+

Un VLAN ne remplace pas le filtrage des flux inter-VLAN.
~~~


Un VLAN délimite un domaine de diffusion logique sur l'infrastructure commutée. Il permet de séparer les catégories de terminaux, par exemple postes de travail, téléphones IP, invités, imprimantes, serveurs, équipements IoT et gestion. Les VLAN doivent être associés à des règles cohérentes de routage et de filtrage : séparer deux VLAN ne suffit pas si le routage inter-VLAN autorise ensuite tous les flux.

Une conception raisonnable utilise des VLAN qui correspondent à des usages et des profils de sécurité identifiables. Évite un VLAN unique pour tous les appareils quand leurs exigences de confiance sont distinctes. Évite aussi des centaines de VLAN sans propriétaires, règles ou besoins clairs : une segmentation qui n'est pas documentée devient difficile à maintenir.

Les identifiants VLAN connus dans l'environnement doivent être documentés, notamment le VLAN natif lorsqu'il est utilisé sur un trunk, les VLAN de gestion et les VLAN réservés ou inactifs. Le fait de changer simplement un VLAN d'un nombre bas à un nombre haut n'est pas une mesure de sécurité suffisante. Les protections viennent de la désactivation des négociations non nécessaires, d'une liste explicite de VLAN autorisés, du contrôle d'accès et de la réduction des ports disponibles.

Pour chaque VLAN, documente les sous-réseaux, la passerelle, les serveurs DHCP, les DNS, les règles inter-VLAN, les ports d'accès attendus et les trunks qui doivent transporter ce VLAN. En cas d'incident, cette cartographie permet de déterminer si le VLAN observé est cohérent ou s'il apparaît sur un lien inattendu.

## 5. Port d'accès et trunk 802.1Q

**Schéma pédagogique — Un port d'accès sert généralement un VLAN terminal ; un trunk transporte une liste contrôlée de VLAN.**

~~~text
PC ---- access VLAN 10 ---- [Switch]
                              |
                              | trunk 802.1Q
                              | VLAN 10,20,30 seulement
                              v
                         [Distribution]

Verifier les deux extremites, la liste autorisee et le VLAN natif prevu.
~~~


Un port d'accès transporte généralement le trafic d'un VLAN non tagué pour un terminal final. Un trunk transporte plusieurs VLAN avec des étiquettes 802.1Q, habituellement entre commutateurs ou vers des équipements qui ont réellement besoin de plusieurs VLAN. Les détails exacts dépendent de l'équipement et de la plateforme.

Un terminal ordinaire n'a normalement pas besoin de négocier lui-même la fonction trunk. Lorsque la plateforme prend en charge la négociation dynamique de trunk, désactive-la sur les ports d'accès et fixe explicitement leur rôle. Configure les trunks explicitement aux deux extrémités et autorise seulement les VLAN nécessaires, au lieu de transporter par défaut tous les VLAN.

L'étiquetage 802.1Q ajoute un identifiant VLAN aux trames transportées sur un trunk. Le traitement du VLAN natif peut différer selon le matériel : il est souvent transporté sans étiquette sur les trunks Cisco classiques, mais les options varient. Une différence de VLAN natif entre les deux extrémités peut provoquer des erreurs de classification, des fuites de trafic ou des problèmes de connectivité. La cohérence doit être vérifiée explicitement.

Modèle d'inventaire recommandé :

~~~text
Gi1/0/1-20  postes utilisateurs : access VLAN 10
Gi1/0/21-22 téléphones IP et postes : voice VLAN 20 + data VLAN 10 selon besoin
Gi1/0/23    imprimante autorisée : access VLAN 30
Gi1/0/24    liaison montante : trunk, VLAN 10,20,30 et gestion selon design
Autres ports inoccupés : désactivés et placés dans un VLAN de quarantaine non routé
~~~

Ce schéma illustre une intention de conception, pas un modèle universel. Les ports de téléphones, points d'accès, hyperviseurs, bornes sans fil et appliances peuvent nécessiter plusieurs VLAN. Ils doivent être identifiés par leur fonction plutôt que traités comme des ports utilisateurs simples.

## 6. VLAN hopping : menaces et mesures de réduction

Le VLAN hopping désigne des techniques qui cherchent à faire traverser le trafic d'un VLAN à un autre sans l'autorisation prévue. Les anciens scénarios d'attaque peuvent exploiter la négociation dynamique de trunk ou des comportements particuliers de double étiquetage. La faisabilité dépend de la topologie, de la configuration et de la plateforme ; il ne faut pas supposer qu'une attaque historique fonctionne dans toutes les infrastructures modernes.

Les mesures essentielles sont simples : fixer les ports terminaux en mode access, désactiver la négociation de trunk sur les ports où elle n'est pas nécessaire, limiter les VLAN autorisés sur les trunks, choisir et documenter le VLAN natif, éviter d'utiliser le VLAN natif pour des terminaux sensibles et retirer les VLAN inutilisés des trunks.

La protection n'est pas un changement de numéro. Un VLAN natif au numéro inhabituel mais transporté sur tous les liens, ou un trunk qui autorise tous les VLAN, reste un périmètre fragile. La configuration et le chemin réel comptent davantage que le numéro affiché.

Après un changement, vérifie l'état opérationnel du port, les VLAN autorisés et actifs, le VLAN natif sur chaque extrémité et le chemin d'un hôte de test. Une configuration correcte d'un seul côté ne garantit pas le comportement attendu de bout en bout.

## 7. Ports inutilisés et accès physique

Un port libre mais activé représente une possibilité de connexion non nécessaire. Dans la mesure du possible, désactive les ports inutilisés et place-les dans un VLAN de quarantaine sans passerelle ni accès aux ressources de production. Maintiens un inventaire des ports qui doivent rester libres pour des raisons opérationnelles, et réévalue cet état lors des changements.

Le contrôle physique est complémentaire : armoire verrouillée, contrôle de salle, étiquetage, protection des prises dans les zones publiques, surveillance et inventaire des équipements. La désactivation logicielle ne remplace pas le contrôle physique, et une prise en salle accessible au public doit être considérée comme un point d'entrée potentiel.

Ne coupe pas un port simplement parce qu'il n'est pas visible dans la table MAC à un instant donné. Certaines interfaces sont utilisées de façon intermittente, pour une maintenance planifiée ou par des équipements dormants. Confirme l'usage, le propriétaire et l'impact avant l'action, puis documente la décision.

## 8. Port security

La protection de port limite les adresses MAC autorisées ou apprises sur une interface. Sur certaines plateformes, les adresses peuvent être configurées statiquement, apprises dynamiquement ou apprises puis conservées dans la configuration (sticky). Les modes de violation peuvent provoquer l'abandon du trafic, un état d'interface bloqué ou une alerte selon le matériel et le réglage.

Exemple pédagogique de syntaxe Cisco IOS/IOS XE, à vérifier sur la version cible :

~~~text
interface GigabitEthernet1/0/10
 switchport mode access
 switchport access vlan 10
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
~~~

Cet exemple fixe le port en accès, active la fonction et limite à deux adresses. Une limite de deux peut convenir à un poste avec un téléphone IP en chaîne selon la façon dont les adresses sont apprises ; elle serait trop basse pour certains scénarios et trop haute pour d'autres. Choisis la limite à partir du profil réel et vérifie le comportement du téléphone et du poste après application.

Le mode restrict, lorsqu'il existe sous cette forme, abandonne les trames qui dépassent la politique et peut générer des compteurs ou journaux sans couper entièrement le port. D'autres modes peuvent mettre le port en état err-disabled ou se comporter autrement. Ne copie pas un mode de violation sans connaître son impact et la procédure de récupération.

Le sticky learning aide à retenir les adresses observées, mais peut enregistrer une adresse incorrecte si la connexion est faite au mauvais moment. Il exige une procédure de remplacement d'équipement : nettoyer ou mettre à jour l'entrée selon les règles de gestion et vérifier que l'ancienne adresse n'est plus autorisée. Pour les environnements dynamiques, 802.1X apporte un contrôle d'identité plus fort que la seule adresse MAC.

## 9. DHCP Snooping

**Schéma pédagogique — Le commutateur distingue les ports fiables pour les réponses DHCP des ports terminaux non fiables.**

~~~text
[Client DHCP] --> [Port untrusted]
                       |
                       v
                  [Switch] <---- reponse autorisee ---- [DHCP / relais]
                       ^                                  |
                       +--------- uplink trusted --------+

Binding appris: VLAN + IP + MAC + port
Un port terminal ne doit pas etre trusted sans justification.
~~~


DHCP Snooping observe les échanges DHCP et distingue les interfaces autorisées à recevoir des réponses serveur des ports terminaux non fiables. Il permet au commutateur de bloquer certaines réponses DHCP provenant d'un port non fiable et construit généralement une base de correspondance entre adresse IP attribuée, adresse MAC, VLAN et port. Cette base peut alimenter des contrôles supplémentaires comme Dynamic ARP Inspection et IP Source Guard.

Le modèle de confiance dépend du chemin réel. Les ports vers un serveur DHCP légitime ou vers un relais/trunk qui transporte les réponses autorisées peuvent avoir besoin d'un statut de confiance ; les ports de terminaux restent non fiables. Le statut trusted n'est pas un label décoratif : un port de bordure configuré par erreur comme fiable peut permettre à un serveur DHCP clandestin de contourner le contrôle.

Exemple Cisco IOS/IOS XE indicatif :

~~~text
ip dhcp snooping
ip dhcp snooping vlan 10,20,30
!
interface GigabitEthernet1/0/24
 description Uplink vers infrastructure DHCP autorisee
 switchport mode trunk
 ip dhcp snooping trust
!
interface GigabitEthernet1/0/10
 description Poste utilisateur
 switchport mode access
 switchport access vlan 10
 ip dhcp snooping limit rate 10
~~~

L'exemple montre un uplink de confiance et une limite indicative sur un port terminal ; il ne définit pas toutes les conditions requises dans chaque réseau. Vérifie le chemin du serveur, les VLAN activés et le comportement du relais DHCP. Le seuil de limitation doit correspondre aux besoins de terminaux légitimes et aux capacités de la version utilisée.

DHCP Snooping doit être déployé prudemment dans un réseau existant. Si la base de liaison n'est pas alimentée, les fonctionnalités qui en dépendent peuvent bloquer des hôtes disposant d'adresses dynamiques. Les équipements utilisant des adresses statiques peuvent nécessiter une association statique ou une ACL ARP adaptée. Avant une activation générale, vérifie la population de la base et prépare un test pilote.

## 10. Dynamic ARP Inspection (DAI)

**Schéma pédagogique — DAI compare les messages ARP reçus aux bindings ou exceptions explicitement configurées.**

~~~text
[Trame ARP entrante]
        |
        v
 [DAI sur le VLAN]
        |
        +---- correspondance IP/MAC/port valide --> [Transmettre]
        |
        +---- non-correspondance / politique -----> [Rejeter + compteur]

Les hôtes statiques peuvent nécessiter des bindings ou ACL compatibles.
~~~


ARP associe une adresse IPv4 locale à une adresse MAC. Les hôtes utilisent normalement ARP pour découvrir l'adresse MAC qui correspond à la passerelle ou à un voisin du même sous-réseau. Sans validation, une machine sur le même domaine de diffusion peut tenter d'envoyer de fausses annonces ARP afin d'associer l'adresse IP d'une victime ou de la passerelle à sa propre adresse MAC.

Dynamic ARP Inspection valide les paquets ARP entrants sur les interfaces où la fonction est activée. Sur de nombreuses plateformes, la vérification s'appuie sur la base DHCP Snooping qui contient des correspondances IP-MAC-VLAN-port. Dans les réseaux à adresse statique ou lorsque la base DHCP ne représente pas tous les hôtes, il faut prévoir des bindings statiques ou des ACL ARP supportées par la plateforme.

La fonction ne protège pas magiquement les hôtes qui se trouvent sur des commutateurs ou segments où elle n'est pas activée, et la portée d'une attaque dépend du domaine de diffusion. Une protection homogène du VLAN et une segmentation adaptée sont donc importantes. Un trunk ou un port de confiance doit être configuré uniquement si le modèle opérationnel le justifie.

Exemple de principe :

~~~text
ip dhcp snooping
ip dhcp snooping vlan 10,20
ip arp inspection vlan 10,20
!
interface GigabitEthernet1/0/24
 ip dhcp snooping trust
 ip arp inspection trust
~~~

Cette illustration n'est pas une configuration prête à appliquer : l'activation de DAI peut bloquer des appareils si la base de bindings n'est pas complète ou si les paquets ARP légitimes ne correspondent pas à la politique. Vérifie d'abord la prise en charge, les ports fiables, les VLAN concernés et le besoin d'ACL statiques.

## 11. IP Source Guard

IP Source Guard (IPSG) applique une vérification de source IP sur certains ports de couche 2. Il peut s'appuyer sur la base DHCP Snooping ou sur des bindings IP statiques pour autoriser les adresses source prévues sur une interface. L'objectif est de réduire l'usurpation d'adresse IP par un terminal qui essaie d'utiliser l'adresse d'un voisin.

Sur un port utilisateur, l'activation avant que les bindings soient disponibles peut interrompre la connectivité. L'équipement doit connaître l'association légitime entre l'adresse source, le port et le VLAN. Les hôtes à adresse statique et les environnements particuliers doivent être traités explicitement.

IPSG ne remplace ni une authentification utilisateur ni le contrôle d'accès inter-VLAN. Il ne prouve pas que la personne qui utilise l'adresse est la bonne ; il limite les sources que le port peut émettre selon les bindings. Combine-le avec 802.1X, segmentation et surveillance lorsque le risque le justifie.

## 12. Comment DHCP Snooping, DAI et IPSG se complètent

Ces trois mécanismes traitent des aspects complémentaires :

- DHCP Snooping filtre certains messages DHCP et apprend les attributions d'adresses provenant des échanges autorisés.
- DAI vérifie les associations IPv4-MAC observées dans des messages ARP par rapport aux bindings et aux exceptions prévues.
- IP Source Guard limite les adresses IP source qu'un port peut utiliser selon ses bindings.

Leur chaîne de dépendances demande une préparation. Si le mécanisme d'apprentissage ne connaît pas un terminal légitime, la vérification ARP ou IP peut rejeter son trafic. Si un uplink est marqué trusted à tort, le contrôle DHCP peut être contourné au point où ce statut est appliqué. Une politique qui ne couvre que certains ports ou certains VLAN laisse les zones non protégées.

Un déploiement sûr commence par le VLAN pilote, une cartographie des ports de confiance, l'inventaire des équipements à IP statique, la collecte de la base de bindings et l'observation des compteurs. Ensuite, active une fonction à la fois, valide DHCP, ARP, trafic IP et journaux, puis élargis progressivement. Prévois la réactivation du trafic légitime sans supprimer durablement les contrôles.

## 13. Spanning Tree : prévenir les boucles et les manipulations

**Schéma pédagogique — STP conserve une topologie sans boucle ; les protections doivent correspondre au rôle de chaque port.**

~~~text
             [Switch racine]
              /           \
             v             v
       [Switch A] ------- [Switch B]
             \             /
              \\ chemins redondants
                \\ un port peut etre bloque par STP

Port terminal : PortFast selon plateforme + BPDU Guard si aucune BPDU attendue.
Lien inter-switch : ne pas appliquer aveuglement les protections terminal.
~~~


Spanning Tree Protocol (STP) évite les boucles de couche 2 en calculant une topologie active qui bloque certains chemins redondants. Les variantes et optimisations modernes, comme Rapid Spanning Tree, réduisent les temps de convergence mais conservent le besoin de contrôler les équipements qui envoient des BPDU et les ports qui doivent participer à la topologie.

Un équipement non autorisé qui envoie des BPDU peut influencer le choix de racine ou modifier la topologie. Sur les ports terminaux où aucun commutateur n'est attendu, PortFast accélère le passage à l'état forwarding dans les déploiements Cisco concernés, mais il ne remplace pas BPDU Guard. BPDU Guard peut mettre le port en état de protection lorsqu'une BPDU inattendue arrive.

Exemple Cisco indicatif :

~~~text
interface GigabitEthernet1/0/10
 switchport mode access
 spanning-tree portfast
 spanning-tree bpduguard enable
~~~

Utilise cette approche uniquement pour les ports d'extrémité qui ne doivent pas connecter un pont ou un commutateur. Sur un trunk intercommutateur, un port de virtualisation ou un équipement qui transmet légitimement des BPDU, il faut une conception adaptée. BPDU Guard sur une liaison qui doit recevoir des BPDU peut déclencher une coupure.

Root Guard peut empêcher qu'un port désigné devienne un chemin par lequel un équipement externe impose une meilleure racine ; son utilisation dépend du rôle attendu de l'interface. Loop Guard aide à prévenir certains cas où un port qui devrait recevoir des BPDU n'en reçoit plus et pourrait devenir un chemin de transfert inapproprié. Ces protections ont des rôles différents et ne se substituent pas les unes aux autres.

La racine STP doit être choisie par l'architecture, surveillée et protégée. Ne suppose pas que la racine actuelle est correcte simplement parce que le réseau fonctionne. Une modification de priorité malveillante ou accidentelle peut produire une topologie inattendue et faire passer le trafic par un chemin qui n'était pas prévu.

## 14. Storm control et limites de trafic

Une tempête de broadcast, multicast ou unicast inconnu peut consommer la bande passante d'un segment et les ressources des hôtes. Storm control peut limiter certains types de trafic au-delà d'un seuil de débit ou de pourcentage, selon l'appareil. Les options de réaction varient : supprimer les trames au-dessus du seuil, produire une notification ou agir sur le port.

Un seuil trop strict peut bloquer des comportements légitimes, notamment au démarrage d'un grand nombre d'hôtes, pendant certaines fonctions de découverte ou dans un environnement vidéo/multicast. Un seuil trop large peut n'apporter qu'une protection limitée. Mesure le trafic de base et teste pendant une période représentative.

Storm control protège la disponibilité, mais ne prouve pas l'identité de la source. Combine-le avec la segmentation, le filtrage, des protections DHCP/ARP, la limitation de débit adaptée et des alertes. Une tempête peut être due à une attaque, à une boucle physique, à un mauvais paramétrage ou à une panne matérielle ; le diagnostic doit considérer ces causes.

## 15. 802.1X et contrôle d'accès au réseau

**Schéma pédagogique — 802.1X autorise un port selon une décision d'authentification plutôt que de faire confiance à toute prise physique.**

~~~text
[Supplicant / terminal] -- EAPOL --> [Switch authenticator]
                                          |
                                          | RADIUS
                                          v
                                  [Serveur authentification]
                                          |
                               resultat / role / VLAN
                                          v
                                  [Port autorise ou refuse]

MAB peut dépanner les appareils incompatibles, mais n'offre pas la même garantie qu'un certificat.
~~~


IEEE 802.1X fournit un cadre de contrôle d'accès au port basé sur l'authentification. Le commutateur ou l'équipement d'accès joue le rôle d'authenticator et échange avec le terminal, le supplicant, via le protocole EAPOL. Un serveur d'authentification, souvent RADIUS, valide l'identité ou le certificat selon la méthode configurée. Après la décision, la politique peut attribuer un VLAN, un rôle ou des autorisations, selon les capacités de l'infrastructure.

Le modèle permet de ne pas faire confiance à un appareil simplement parce qu'il est connecté à une prise. Les règles peuvent être liées à un compte utilisateur, à un certificat d'appareil ou à un profil machine. EAP-TLS avec certificats peut fournir une forte authentification mutuelle, mais nécessite une gestion de cycle de vie des certificats. Le choix de méthode doit être évalué selon les clients et les capacités de l'organisation.

MAB (*MAC Authentication Bypass*) est parfois utilisé pour des appareils qui ne supportent pas 802.1X, comme certains périphériques simples. Il s'appuie généralement sur une adresse MAC et ne fournit pas la même garantie qu'un certificat : une adresse MAC peut être usurpée. Il faut limiter les droits des appareils MAB, les classifier, surveiller leur présence et envisager une exception documentée plutôt qu'une ouverture générale.

Prévois le fonctionnement des appareils non gérés, des téléphones IP, des imprimantes, des équipements industriels, des postes de secours et des systèmes critiques. Une politique de refus totale sans chemin de secours planifié peut provoquer une panne. À l'inverse, un mode fail-open durable transforme le contrôle en simple avertissement. La stratégie doit inclure un accès de remédiation ou une procédure de secours sûre.

## 16. Affectation dynamique des VLAN et politiques par rôle

L'affectation dynamique peut placer un appareil dans le VLAN ou rôle qui correspond à son identité, selon l'authentification, le système de contrôle d'accès et les capacités du commutateur. Cela rend possible une séparation entre employés, invités, appareils gérés et équipements sans supplicant.

Une politique par rôle doit limiter ce que le terminal peut atteindre : serveurs nécessaires, DNS, mises à jour, contrôleurs, outils de gestion ou portail de remédiation. Évite que tous les appareils authentifiés reçoivent automatiquement l'accès complet au VLAN utilisateur. Le VLAN est un élément d'une architecture de contrôle ; les ACL, pare-feu et politiques d'application restent nécessaires.

Les transitions doivent être testées. Un poste qui change de port, de rôle ou d'état de conformité peut recevoir une nouvelle politique et perdre des connexions existantes. Documente le comportement attendu, les journaux utiles et les dépendances d'authentification. La surveillance doit détecter les tentatives répétées et les retours inattendus dans un VLAN plus permissif.

## 17. Sécurité du plan de gestion

La gestion du commutateur est un chemin privilégié vers l'infrastructure. Isole l'adresse de gestion dans un réseau ou VRF dédié lorsque l'architecture le permet. Autorise les connexions administratives depuis des sources de confiance uniquement. Préfère SSH à Telnet et SNMPv3 à SNMPv1/v2c lorsque le matériel et les outils le permettent.

Utilise des comptes individuels et une authentification centralisée avec AAA/RADIUS/TACACS+ selon les produits. Conserve un compte de secours selon une procédure protégée. Les privilèges doivent correspondre au besoin : les utilisateurs de lecture ne devraient pas pouvoir changer la configuration. Évite les comptes partagés et les mots de passe par défaut.

Exemple indicatif de principe Cisco :

~~~text
ip domain-name example.invalid
crypto key generate rsa modulus 2048
ip ssh version 2
line vty 0 4
 transport input ssh
 login local
~~~

Les commandes exactes et la syntaxe des clés dépendent de la plateforme et de sa version. Dans un réseau réel, une configuration de gestion doit aussi préciser les comptes, AAA, restrictions de source, politiques de chiffrement, journaux et sauvegardes. Le domaine example.invalid est réservé à l'illustration ; ne réutilise pas un nom d'exemple comme identité réelle.

Désactive les services de gestion qui ne sont pas nécessaires, notamment les protocoles en clair, les services hérités, les interfaces Web non utilisées et les découvertes inutiles sur les ports exposés. Avant de supprimer un service, confirme qu'aucun outil d'exploitation ne dépend de lui. Un durcissement qui supprime le seul accès d'administration peut rendre le réseau difficile à récupérer.

## 18. SNMP, journaux, NTP et sauvegardes

SNMP v1/v2c utilise des chaînes de communauté qui ne fournissent pas les mêmes garanties de sécurité que SNMPv3 avec authentification et confidentialité correctement configurées. Évite les chaînes par défaut et les communautés en lecture-écriture inutilement larges. Limite les sources autorisées et les vues de données à ce qui est nécessaire.

Les journaux centralisés aident à établir une chronologie pour les changements de VLAN, les violations de port, les événements STP, les connexions administratives et les erreurs d'authentification. Synchronise les horloges via une source NTP fiable et protège la collecte. Sans horloge cohérente, la corrélation des événements est plus difficile et les certificats peuvent être interprétés incorrectement.

Sauvegarde les configurations et maintiens un historique contrôlé. Compare les changements avec les tickets ou processus de changement. Un fichier de configuration peut contenir des données sensibles : contrôle les accès, protège le transport et évite de coller des secrets en clair dans un système de documentation non autorisé.

La supervision doit inclure l'état des interfaces, les erreurs, la consommation, les changements de topologie, les compteurs de sécurité, les ports qui passent en état bloqué et les écarts par rapport à la configuration attendue. Les alertes doivent être triées et actionnables. Une avalanche d'alertes sans contexte finit par masquer les incidents importants.

## 19. IPv6 : ne pas oublier les contrôles de couche 2

Les protections IPv4 telles que DHCP Snooping et DAI ne couvrent pas automatiquement tous les mécanismes IPv6. IPv6 utilise notamment Neighbor Discovery (ND) au lieu d'ARP et peut utiliser Router Advertisements (RA), DHCPv6 ou des mécanismes d'autoconfiguration. Une stratégie qui protège seulement IPv4 peut laisser des chemins alternatifs si IPv6 est actif.

RA Guard peut aider à restreindre les annonces de routeur IPv6 sur les ports où un routeur n'est pas attendu, sous réserve des fonctions et limites de la plateforme. Les protections de DHCPv6, ND inspection, source guard IPv6 et les contrôles du plan de gestion IPv6 varient selon le système. Il faut vérifier les recommandations de la version utilisée et ne pas supposer que désactiver IPv4 rend le réseau sûr.

Le protocole IPv6 peut fonctionner sur un LAN même si l'organisation n'en a pas l'intention, selon les paramètres et les équipements. Inventorie le trafic IPv6, les adresses et les routes, puis décide s'il doit être pris en charge et protégé ou désactivé selon une politique explicite. Une désactivation partielle et non documentée peut casser des fonctions et créer une fausse impression de contrôle.

## 20. LACP, ports agrégés et équipements intermédiaires

LACP négocie l'appartenance de liens à un groupe d'agrégation sur les équipements qui le prennent en charge. Une mauvaise configuration du groupe, des VLAN incohérents ou des liens connectés à des équipements différents sans prise en charge de la redondance prévue peuvent provoquer des problèmes de transfert ou une topologie inattendue.

Ne considère pas un lien agrégé comme sûr uniquement parce qu'il transporte plusieurs liens physiques. La politique de sécurité doit être cohérente sur le groupe et les ports membres ; les commandes et restrictions peuvent varier selon la plateforme. Les paramètres d'accès ou de trunk, les VLAN autorisés, MTU, modes LACP et protections STP doivent être cohérents.

Un petit commutateur non autorisé connecté à un port utilisateur est un risque courant. Il peut étendre le domaine de diffusion, ajouter des appareils non inventoriés et parfois déclencher une boucle. Les protections de port, 802.1X, l'inspection des équipements et le contrôle physique contribuent à limiter ce risque. Une politique qui autorise explicitement un mini-switch pour un laboratoire doit être limitée au VLAN et à la durée nécessaires.

## 21. MACsec et protection des liaisons

MACsec, spécifié par IEEE 802.1AE, peut fournir confidentialité et intégrité sur une liaison Ethernet entre équipements compatibles lorsqu'il est correctement déployé et qu'une politique de clés est en place. Il peut réduire le risque d'écoute ou de modification de trames sur certaines liaisons, mais ce n'est pas une solution universelle contre les attaques au sein du VLAN après terminaison de la protection.

La prise en charge de MACsec, les méthodes d'authentification, la gestion de clés et les limites dépendent des matériels et licences. Avant le déploiement, vérifie les compatibilités, le débit, les exigences de redondance et le comportement des outils de diagnostic. La protection d'une liaison ne supprime pas le besoin de VLAN, de contrôle d'accès ou de sécurité des terminaux.

Ne confonds pas MACsec avec le chiffrement applicatif ou un VPN IPsec : ils peuvent protéger des segments différents et avoir des objectifs différents. La défense en profondeur choisit chaque mécanisme en fonction de la menace et de la frontière qu'il protège.

## 22. Principes de configuration : exemple de port d'accès durci

Exemple indicatif Cisco IOS/IOS XE pour un port utilisateur simple, à adapter à la plateforme :

~~~text
interface GigabitEthernet1/0/10
 description Poste utilisateur bureau 2
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 switchport port-security
 switchport port-security maximum 1
 switchport port-security violation restrict
 storm-control broadcast level 1.00
 shutdown
 no shutdown
~~~

Cet exemple ne doit pas être copié tel quel en production sans validation. Le seuil storm control varie selon la syntaxe, les unités et le modèle. La commande shutdown/no shutdown illustre un cycle d'interface mais peut interrompre immédiatement le poste ; ne l'utilise pas comme étape automatique d'une configuration. Pour un port réellement utilisé, les changements doivent être planifiés et appliqués dans l'ordre prévu par le système.

Si le poste est relié via un téléphone IP, l'adresse MAC du téléphone et celle du poste peuvent toutes deux apparaître sur le port. Une limite de 1 peut alors bloquer l'un des appareils. Une borne Wi-Fi, un hyperviseur ou un équipement d'accès multiple demande une politique différente. La valeur idéale n'est pas universelle.

Une procédure de durcissement doit comprendre : identification du port et de son propriétaire ; vérification de la topologie ; sauvegarde de la configuration ; préparation de la commande de retour arrière ; activation d'une protection ; tests DHCP, DNS, passerelle et applications ; revue des compteurs et journaux ; puis mise à jour de l'inventaire.

## 23. Vérification de l'état réel

Il faut vérifier l'état opérationnel, pas seulement la configuration désirée. Une commande de configuration peut être acceptée mais rester inactive faute de prise en charge, être supplantée par une autre politique ou n'affecter que certains VLAN. Les noms exacts varient, mais les familles de vérification incluent :

~~~text
show interfaces status
show vlan brief
show interfaces trunk
show mac address-table dynamic
show spanning-tree
show port-security
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection
show logging
show running-config
~~~

Ces exemples sont des commandes Cisco IOS/IOS XE courantes dans plusieurs familles, mais ne sont pas universelles. Vérifie le guide de commande du modèle et de la version. Pour les fonctions IPv6, NAC, MACsec, storm control et les détails matériels, la commande de diagnostic peut être spécifique.

Prends une capture de l'état avant et après une modification. Compare les interfaces attendues et celles qui sont actives, les trunks et leurs VLAN, la racine STP, les bindings DHCP, les compteurs de violation, les changements de table MAC et les journaux. Si la fonction est censée bloquer un trafic, réalise un test autorisé dans un environnement maîtrisé et confirme le résultat par les compteurs.

## 24. Déploiement progressif et retour arrière

Les contrôles L2 peuvent bloquer un réseau entier si la relation de confiance, les bindings ou les ports de transit sont mal identifiés. Évite donc l'activation globale sans pilote et plan de retour arrière. Commence par inventorier les équipements, les ports de confiance, les VLAN, les hôtes à adresse statique et les fonctions de téléphonie, de Wi-Fi ou de virtualisation.

Déploie d'abord une mesure sur un petit nombre de ports représentatifs. Vérifie un client DHCP, un appareil statique, un téléphone IP, un trunk et les ressources essentielles. Élargis ensuite progressivement et mesure les violations légitimes. Utilise les modes d'observation ou de restriction les moins disruptifs quand ils existent et conviennent au risque, sans oublier qu'ils ne remplacent pas une politique finale.

Le retour arrière doit être concret : savoir quelles lignes ont été ajoutées, qui peut accéder à la console, comment restaurer la configuration précédente et comment s'assurer que l'état n'a pas été altéré ailleurs. Sauvegarde avant les changements et garde un accès hors bande fiable pour les équipements critiques. Un rollback ne doit pas dépendre du service réseau que la nouvelle politique risque de bloquer.

## 25. Tableau de correspondance menace / contrôle

| Menace ou défaut | Contrôle principal | Dépendance ou limite à retenir |
|---|---|---|
| Trunk non autorisé | Ports access fixes, désactivation de négociation inutile, VLAN autorisés explicites | Les commandes dépendent du fabricant ; vérifier les deux extrémités |
| Serveur DHCP clandestin | DHCP Snooping, ports fiables limités, rate limit | Le chemin DHCP et la base de bindings doivent être correctement définis |
| ARP falsifié IPv4 | DAI, bindings ou ACL ARP pour les cas statiques | N'agit que là où la fonction est activée et correctement alimentée |
| Usurpation d'adresse IP source | IP Source Guard, 802.1X et segmentation | Les bindings doivent refléter les usages légitimes |
| Table MAC perturbée | Port security, limites et surveillance | Ne constitue pas une authentification cryptographique |
| BPDU non autorisée sur un port terminal | BPDU Guard, port roles documentés | Ne pas l'appliquer aveuglément sur un lien qui doit transporter des BPDU |
| Boucle ou tempête | STP, protections adaptées, storm control | Un seuil trop faible peut affecter du trafic légitime |
| Accès physique non autorisé | Désactivation des ports libres, contrôle physique, 802.1X | L'inventaire et la gouvernance restent nécessaires |
| Fuite de gestion | VLAN/VRF de gestion, SSH, AAA, filtrage de source | Le réseau de gestion doit être limité et surveillé |
| Attaque IPv6 non traitée | RA Guard et contrôles IPv6 compatibles | Les protections IPv4 ne couvrent pas automatiquement IPv6 |

## 26. TP 1 — Durcir un port utilisateur

### Situation

Le commutateur de laboratoire possède un poste de test sur Gi1/0/10, dans le VLAN 10. Aucun commutateur supplémentaire ne doit être connecté à ce port. Le VLAN 10 utilise DHCP et la passerelle répond correctement. Le port est actuellement configuré de façon trop permissive.

### Travail demandé

1. Sauvegarde l'état de la configuration et inventorie l'adresse MAC du poste.
2. Configure le port en mode access avec le VLAN 10.
3. Active les protections STP adaptées à un port terminal sur la plateforme de laboratoire.
4. Active port security avec une limite d'adresses adaptée au profil réel.
5. Choisis un mode de violation et explique ce qu'il fait.
6. Valide DHCP, DNS, passerelle et application de test.
7. Consulte les compteurs et journaux ; vérifie qu'aucune adresse MAC inattendue n'est observée.

### Correction proposée

Sur une plateforme Cisco qui supporte les commandes indiquées, le port est fixé en access, le VLAN est explicitement déclaré, PortFast et BPDU Guard sont appliqués parce que l'interface est un port terminal, puis port security est configuré avec une limite correspondant au nombre d'appareils légitimes. Si le poste est connecté directement sans téléphone ni pont intermédiaire, une limite d'une adresse peut convenir ; ce choix doit être réévalué pour un autre profil.

Valide la configuration active avant d'étendre à d'autres ports. N'injecte pas volontairement de BPDU sur un port de production. Dans le laboratoire, tu peux simuler une violation autorisée uniquement si le matériel et les règles du TP le permettent, puis vérifier le compteur et restaurer l'état attendu.

## 27. TP 2 — Activer DHCP Snooping sans couper les utilisateurs

### Situation

Le VLAN 10 possède plusieurs clients DHCP, le serveur DHCP est accessible via le trunk Gi1/0/24, et certains équipements du VLAN 30 utilisent des adresses statiques. La mission est de bloquer les réponses DHCP provenant des ports terminaux et de préparer les conditions nécessaires pour activer DAI.

### Travail demandé

1. Identifie les VLAN concernés, le chemin du serveur DHCP et les ports qui transportent les réponses légitimes.
2. Vérifie qu'aucun port terminal n'a besoin d'être trusted.
3. Active DHCP Snooping sur un VLAN pilote et définis le statut trusted du lien qui mène vers l'infrastructure DHCP réelle.
4. Fais renouveler le bail d'un client de test et vérifie la base de bindings.
5. Documente les équipements à adresse statique et la façon dont ils seront pris en charge avant toute activation DAI/IPSG.
6. Vérifie les compteurs, journaux et accès aux services avant d'étendre la politique.

### Correction proposée

La fonction est activée globalement et sur le VLAN pilote selon la syntaxe du système. Le port vers le chemin DHCP autorisé est marqué trusted uniquement après vérification de la topologie. Les ports clients restent untrusted et peuvent recevoir une limite de débit raisonnable. Le bail d'un client de test est renouvelé pour alimenter la base.

Les équipements du VLAN 30 à IP statique doivent être inventoriés et traités explicitement avant d'activer des fonctionnalités qui s'appuient sur la base DHCP. Une bonne procédure utilise un pilote, vérifie les bindings et prépare des associations statiques ou ACL supportées selon le besoin. N'active pas DAI à l'échelle du réseau simplement parce que DHCP Snooping apparaît « enabled ».

## 28. TP 3 — Préparer une matrice de sécurité L2

### Situation

Un petit site comprend les VLAN suivants : 10 pour les postes, 20 pour la voix, 30 pour les imprimantes, 40 pour les invités Wi-Fi, 50 pour les objets connectés, 99 pour la gestion. Un commutateur d'accès relie les postes, les imprimantes et un point d'accès, puis monte vers un commutateur de distribution.

### Travail demandé

Construis une matrice qui indique pour chaque type de port son VLAN, mode access/trunk, VLAN autorisés, exigence 802.1X ou MAB, protection STP, politique port security, nécessité DHCP Snooping/DAI/IPSG ou leurs équivalents, gestion et logs. Identifie les exceptions légitimes telles que téléphone IP, point d'accès multi-VLAN, hyperviseur et périphérique statique.

### Correction proposée

Les ports utilisateurs ordinaires deviennent des ports d'accès et utilisent 802.1X lorsque l'environnement le permet. Les périphériques qui ne peuvent pas s'authentifier reçoivent une politique MAB restrictive et documentée, pas une confiance implicite. Les trunks sont explicitement configurés vers les équipements connus et ne transportent que les VLAN nécessaires. Les ports libres sont désactivés et isolés.

Le VLAN de gestion n'est disponible que depuis les sources d'administration approuvées. Les protections de DHCP, ARP et IP sont adaptées aux usages et au plan d'adressage. Les appareils IPv6 sont également pris en compte. Les alertes sont envoyées vers une collecte centralisée et les modifications sont associées à un ticket et à une sauvegarde.

## 29. Exercices corrigés

### Exercice 1 — Port utilisateur en trunk

Un port relié à un PC négocie dynamiquement le trunk. Quel est le principe de correction ?

**Correction :** fixe le port en mode access, affecte explicitement le VLAN attendu et désactive la négociation de trunk lorsque la plateforme le permet et que cette fonction n'est pas nécessaire. Vérifie ensuite l'état opérationnel et les VLAN présents. Changer uniquement le numéro du VLAN ne corrige pas le risque de trunk.

### Exercice 2 — Serveur DHCP clandestin

Un employé branche un routeur domestique qui répond aux Discover des clients. Quel contrôle réduit ce risque ?

**Correction :** DHCP Snooping, avec ports terminaux non fiables et ports de chemin DHCP approuvé configurés avec confiance minimale. Il faut aussi vérifier le chemin réel des réponses et les journaux. Marquer tous les trunks trusted sans analyse affaiblit la protection.

### Exercice 3 — DAI bloque une imprimante statique

Pourquoi est-ce possible et que faut-il vérifier ?

**Correction :** DAI peut s'appuyer sur les bindings appris par DHCP Snooping. Une imprimante statique peut ne pas figurer dans cette base. Il faut vérifier son adresse, son VLAN et son port, puis prévoir le mécanisme statique ou l'ACL ARP prise en charge par le système. Il ne faut pas désactiver durablement DAI pour tout le VLAN sans comprendre l'exception.

### Exercice 4 — Une BPDU arrive sur un port avec BPDU Guard

Quelle est l'interprétation ?

**Correction :** le port a reçu un message qui ne devrait pas arriver sur ce port terminal. BPDU Guard peut le désactiver ou déclencher un état de protection selon la plateforme. Vérifie si un commutateur, pont ou appareil légitime a été branché et suis la procédure de rétablissement. Ne supprime pas la protection par réflexe.

### Exercice 5 — Port security limite à une adresse

Le poste perd la connectivité lorsqu'un téléphone IP est placé en cascade. Explique pourquoi.

**Correction :** le commutateur peut apprendre l'adresse MAC du téléphone et celle du PC sur le même port. Une limite d'une adresse peut bloquer l'un des deux. Il faut choisir la limite et la configuration voix/données selon le profil légitime, ou concevoir un accès par identité avec une politique adaptée.

### Exercice 6 — Table MAC qui change rapidement

Est-ce nécessairement une attaque ?

**Correction :** non. Un équipement déplacé, un port agrégé mal configuré, une boucle ou un changement normal peut aussi produire des mouvements. Examine la vitesse des changements, les MAC affectées, les ports, les logs STP et la topologie ; corrèle avec les tickets et l'inventaire avant d'accuser un terminal.

### Exercice 7 — VLAN séparés mais tout communique

Pourquoi la segmentation n'apporte-t-elle pas la restriction attendue ?

**Correction :** les VLAN séparent les domaines de diffusion, mais le routeur ou commutateur L3 peut autoriser le routage entre eux. Il faut contrôler les ACL ou pare-feu inter-VLAN et tester les flux qui doivent être refusés aussi bien que ceux qui doivent être autorisés.

### Exercice 8 — IPv4 protégé, IPv6 ignoré

Quel est le risque ?

**Correction :** des mécanismes IPv6 comme Router Advertisements, Neighbor Discovery ou DHCPv6 peuvent rester actifs et suivre des règles différentes. Il faut inventorier IPv6 et déployer les protections compatibles, comme RA Guard lorsque le modèle le permet, ou désactiver explicitement la fonction selon une politique validée.

### Exercice 9 — SNMP avec communauté partagée

Quelles améliorations proposer ?

**Correction :** privilégie SNMPv3 avec authentification et confidentialité supportées, limite les sources autorisées, retire les communautés par défaut et limite les vues et droits. Protége les secrets et les collecteurs, et vérifie la compatibilité de l'outil de supervision.

### Exercice 10 — DHCP Snooping activé, plus aucun bail

Que vérifier dans quel ordre ?

**Correction :** vérifie les VLAN couverts, le port réellement relié au serveur ou au relais, le statut trusted, les compteurs et journaux, puis la base de bindings. Confirme qu'un renouvellement client traverse le chemin prévu. Ne marque pas tous les ports trusted pour faire disparaître l'incident : cela peut éliminer le contrôle que tu cherches à maintenir.

### Exercice 11 — Un lien trunk transporte des VLAN inutiles

Comment le réduire proprement ?

**Correction :** identifie les VLAN nécessaires à chaque extrémité puis limite explicitement la liste autorisée sur le trunk. Vérifie les services et chemins dépendants avant changement, applique la politique de façon cohérente et contrôle l'état opérationnel. Retirer un VLAN sans inventaire peut interrompre les téléphones, points d'accès ou systèmes de gestion.

### Exercice 12 — Le commutateur utilise Telnet pour l'administration

Pourquoi faut-il corriger cela ?

**Correction :** Telnet n'offre pas la protection attendue pour les identifiants et la session. Utilise SSH correctement configuré, limite les sources de gestion, applique AAA et des comptes individuels, puis confirme qu'un accès de secours existe avant de désactiver l'ancien chemin. La procédure doit éviter de perdre tout accès à l'équipement.

## 30. Cas de diagnostic et de mise en production

Les cas suivants sont conçus pour entraîner la méthode de diagnostic. Pour chaque incident, sépare les symptômes, la cause possible, les preuves à recueillir, la correction et le test de non-régression. N'applique pas une solution globale sans confirmer la zone touchée.


### Cas de dépannage 1 — Un PC reçoit une adresse IP appartenant au mauvais sous-réseau

**Analyse.** Un serveur DHCP non autorisé peut répondre plus vite que le serveur attendu, ou le port peut être affecté au mauvais VLAN. Vérifie le VLAN opérationnel, le chemin DHCP, les journaux et le serveur qui a attribué le bail. Déploie DHCP Snooping après avoir identifié les ports de confiance réels et fais renouveler le bail du poste pilote. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne marque pas toutes les interfaces trusted. Cela ferait perdre le contrôle des réponses DHCP. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 2 — Les clients d'un VLAN perdent leur DHCP après activation de Snooping

**Analyse.** Le port vers le serveur ou le relais peut être resté non fiable, le VLAN peut être absent de la liste ou la base n'est pas alimentée. Vérifie les VLAN protégés, le port par lequel arrivent les réponses, la confiance et les compteurs, puis renouvelle le bail d'un client pilote. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne désactive pas la protection dans tout le réseau avant d'avoir confirmé la cause. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 3 — Une imprimante statique est bloquée après DAI

**Analyse.** Son adresse IP-MAC peut ne pas être présente dans la base DHCP Snooping et aucun traitement statique n'est configuré. Confirme l'adresse, le VLAN et le port de l'imprimante puis mets en place un binding ou une ACL ARP statique supportée et limitée à cet appareil. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne crée pas une exception large pour toutes les trames ARP du VLAN. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 4 — Un téléphone IP redémarre ou perd le réseau après port security

**Analyse.** La politique MAC peut autoriser moins d'adresses que nécessaire, ou le VLAN voix n'est pas correctement configuré. Observe les adresses apprises, les VLAN data/voix et les compteurs de violation. Définis une limite conforme au profil du téléphone et du poste en cascade. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne supprime pas port security sans documenter le risque et la mesure de remplacement. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 5 — Un port passe en état err-disabled après réception de BPDU

**Analyse.** BPDU Guard peut avoir détecté un équipement pontant ou une boucle sur un port censé être terminal. Vérifie la topologie physique et les journaux STP. Détermine si le dispositif connecté est autorisé et si le port doit vraiment être un port terminal avant de rétablir le service. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne réactive pas le port automatiquement sans éliminer la cause de la BPDU inattendue. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 6 — Des communications ralentissent pendant une tempête broadcast

**Analyse.** Une boucle, une mauvaise connexion ou un volume excessif de broadcasts peut saturer le segment. Contrôle les compteurs, les changements STP, les ports et la topologie physique. Isole le lien fautif suivant le processus, puis ajuste le storm control après mesure du trafic légitime. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne mets pas un seuil de storm control extrêmement bas sans tester les protocoles nécessaires. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 7 — Une table MAC montre la même adresse qui passe entre deux ports

**Analyse.** Le terminal peut avoir été déplacé, une boucle ou un problème d'agrégation peut exister, ou une usurpation peut être tentée. Corrèle le VLAN, les horodatages, les ports, les changements de câblage et les logs. Vérifie STP et LACP avant de conclure à une attaque. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne bannis pas l'adresse sans déterminer le rôle des ports et le contexte du changement. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 8 — Un trunk transporte des VLAN qui ne devraient pas y figurer

**Analyse.** La liste de VLAN autorisés est trop large ou héritée d'une configuration par défaut. Compare les besoins des deux extrémités et limite la liste aux VLAN nécessaires. Valide les chemins des AP, téléphones, gestion et services avant le changement. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne supprime pas tous les VLAN non utilisés localement sans vérifier les dépendances distantes. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 9 — Un poste peut atteindre le VLAN de gestion

**Analyse.** Les règles de routage inter-VLAN ou l'accès au plan de gestion sont trop permissifs, ou le poste a été affecté au mauvais rôle. Vérifie VLAN, routage, ACL et sources de gestion. Restreins l'administration aux identités et sources approuvées et teste une connexion autorisée puis une connexion refusée. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne compte pas sur le seul VLAN pour imposer tous les contrôles d'accès. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 10 — Une borne Wi-Fi est bloquée par IP Source Guard

**Analyse.** Le port de la borne peut transporter plusieurs clients ou les bindings attendus ne sont pas présents sur ce lien. Confirme le mode de fonctionnement de la borne, les VLAN, les options de sécurité prises en charge et l'architecture de bindings ; adapte la politique au rôle de la borne. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne traite pas un point d'accès multi-VLAN comme un PC ordinaire. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 11 — Un serveur virtualisé perd le réseau après port security

**Analyse.** L'hyperviseur peut émettre plusieurs adresses MAC derrière un seul port physique. Inventorie les interfaces virtuelles et le nombre d'adresses légitimes, puis définis un profil de port adapté au rôle de l'hyperviseur et aux exigences du constructeur. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne fixe pas automatiquement une limite d'une MAC sur les uplinks d'hyperviseurs. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 12 — Le VLAN invité peut communiquer avec des imprimantes internes

**Analyse.** Les ACL de routage ou de pare-feu ne limitent pas le trafic inter-VLAN comme attendu. Teste les flux en IPv4 et IPv6, vérifie les règles inter-VLAN et les routes, puis restreins les destinations invitées à Internet et aux services nécessaires. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne suppose pas que les VLAN isolent à eux seuls les flux routés. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 13 — Un port désactivé est nécessaire à un équipement de secours

**Analyse.** L'inventaire peut être dépassé ou le port peut être réservé à un usage légitime intermittent. Confirme le propriétaire et l'usage prévu, puis applique une activation contrôlée, le VLAN attendu, les protections adaptées et l'enregistrement dans l'inventaire. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne réactive pas des ports en masse simplement parce qu'un utilisateur en a besoin temporairement. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 14 — Le réseau IPv6 fonctionne alors que seules les protections IPv4 sont actives

**Analyse.** Les annonces de routeur et le Neighbor Discovery IPv6 peuvent suivre une voie qui ne passe pas par les protections IPv4. Inventorie les flux IPv6, les VLAN et les équipements qui émettent des RA. Déploie des contrôles IPv6 compatibles ou une politique validée de désactivation. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne présente pas DHCP Snooping ou DAI IPv4 comme une protection complète de l'IPv6. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 15 — Les événements de sécurité ne sont pas corrélables entre équipements

**Analyse.** Les horloges ou journaux ne sont pas synchronisés, ou les messages ne contiennent pas le port/VLAN utile. Configure une synchronisation de temps fiable, une collecte centralisée et une politique de conservation contrôlée. Teste la corrélation avec un événement de port de laboratoire. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne stocke pas de mots de passe ou de clés en clair dans les journaux pour obtenir plus de contexte. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 16 — Une mise à jour de politique 802.1X bloque les imprimantes

**Analyse.** Le périphérique ne supporte pas la méthode attendue ou son profil MAB/VLAN de repli n'est pas configuré. Vérifie l'identité, l'état RADIUS, la méthode EAP, la classification de l'appareil et la politique de rôle. Place les exceptions dans un groupe restreint et surveillé. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne passe pas le réseau entier en fail-open permanent pour éviter un incident de compatibilité. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 17 — La racine STP a changé sans maintenance planifiée

**Analyse.** Un équipement a pu envoyer des BPDU avec une priorité plus favorable, ou un changement physique a modifié la topologie. Inspecte les journaux, la racine actuelle, les priorités et les interfaces concernées. Confirme les changements physiques et protège les ports qui ne doivent pas influencer la racine. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne modifie pas les priorités de tous les commutateurs sans connaître la topologie attendue. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 18 — LACP ne forme pas le groupe attendu

**Analyse.** Les modes, paramètres, VLAN, vitesse ou connexions physiques peuvent être incohérents, ou les ports aboutissent à des équipements incompatibles. Vérifie les membres, les journaux LACP, les configurations de trunk/access, les paramètres communs et la conception de redondance. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne laisse pas des liens de secours transmettant indépendamment et créant une boucle. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 19 — Une chaîne SNMP partagée est visible dans une ancienne configuration

**Analyse.** Le secret peut être encore valide, et certains collecteurs peuvent dépendre d'un protocole ancien. Inventorie les collecteurs, migre vers SNMPv3 supporté, restreins les sources et retire les anciennes communautés une fois la compatibilité vérifiée. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne supprime pas l'ancienne communauté avant d'avoir confirmé l'accès de supervision de remplacement. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 20 — Un port utilisateur est resté en trunk après le remplacement d'un commutateur

**Analyse.** La configuration persistante peut avoir été copiée ou le nouveau matériel peut avoir des valeurs par défaut différentes. Examine l'état opérationnel, la négociation, les VLAN natifs et autorisés ; applique le rôle attendu et valide les deux extrémités. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne suppose pas qu'un remplacement matériel conserve toutes les hypothèses de configuration. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 21 — Une caméra IoT à IP statique échoue après activation des protections

**Analyse.** L'appareil peut ne pas figurer dans la base DHCP et ne pas supporter certains mécanismes d'authentification. Confirme l'adressage, les paquets ARP, le rôle du port et la compatibilité. Prévois un binding statique ou un profil de quarantaine pris en charge et limite l'accès de la caméra. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne désactive pas toutes les protections pour un seul appareil ; applique une exception minimale. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 22 — BPDU Guard déclenche sur un appareil qui transmet légitimement des BPDU

**Analyse.** Le port peut être relié à un pont, un hyperviseur ou un équipement qui participe à la topologie. Identifie la fonction de l'appareil et la conception du chemin. Si la participation STP est légitime, détermine la protection adaptée au rôle et à la plateforme. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne supprime pas BPDU Guard sur un port terminal sans remplacer la protection par un contrôle approprié. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 23 — Un poste continue d'usurper une adresse autorisée malgré port security

**Analyse.** La protection de port peut limiter le nombre de MAC sans lier suffisamment l'identité à un utilisateur ou à un appareil. Examine 802.1X, certificats, contrôle d'accès par rôle, bindings IP-MAC et les journaux. Renforce l'authentification plutôt que de compter uniquement sur une adresse MAC. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne présente pas une adresse MAC comme une preuve fiable de l'identité de l'utilisateur. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 24 — Une modification de VLAN coupe la gestion à distance du commutateur

**Analyse.** Le VLAN de gestion, la route ou les ACL ont changé et le chemin administratif passe par l'interface affectée. Prépare une console ou un accès hors bande, vérifie les routes et la passerelle de gestion et applique le changement avec un rollback exploitable. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne déplace pas le VLAN de gestion sans chemin d'administration de secours. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 25 — Un client obtient un bail mais DAI rejette ses ARP

**Analyse.** Le binding peut être obsolète, incohérent avec le port ou absent du VLAN attendu ; une configuration statique peut également intervenir. Examine la base DHCP Snooping, le bail actif, le VLAN, l'adresse MAC et les compteurs DAI. Renouvelle le bail ou corrige le binding après avoir confirmé la réalité du terminal. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne marque pas tous les ports comme DAI trusted pour masquer l'incohérence. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 26 — Des pertes de paquets apparaissent après activation de storm control

**Analyse.** Le seuil, les unités ou la portée de la fonction peuvent ne pas correspondre au trafic normal. Compare les compteurs et les mesures avant/après, identifie le type de trafic concerné et ajuste le seuil par profil après test représentatif. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne désactive pas à l'aveugle les protections de broadcast si une boucle est toujours possible. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 27 — Une interface de gestion Web reste exposée au VLAN utilisateur

**Analyse.** Le service d'administration est activé sur une interface ou une source trop large. Désactive les services inutiles, limite les sources de gestion, conserve SSH/HTTPS selon la politique et valide l'accès administratif autorisé avant retrait du service ancien. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne coupe pas l'unique accès de gestion sans accès de secours testé. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 28 — Une restauration de configuration a réactivé des ports inutilisés

**Analyse.** La sauvegarde reflète un ancien état et l'inventaire actuel a évolué. Compare la configuration restaurée avec le référentiel actuel, repère les ports actifs sans propriétaire et désactive ceux qui sont confirmés inutiles par une procédure. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne considère pas toute sauvegarde comme une référence de sécurité actuelle sans validation. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 29 — Un petit commutateur est ajouté derrière une prise utilisateur

**Analyse.** Il étend potentiellement le domaine de diffusion et peut connecter des équipements qui n'ont pas été inventoriés. Vérifie port security, 802.1X, l'inventaire, les mouvements MAC et la politique physique. Si le commutateur est autorisé, place-le dans un rôle contrôlé avec segmentation adaptée. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne présume pas que le lien est sûr parce qu'il utilise une prise interne. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 30 — Un incident semble résolu mais les violations continuent

**Analyse.** Un contrôle peut encore rejeter du trafic légitime ou l'appareil mal configuré est toujours connecté. Vérifie les compteurs, les journaux, les bindings, les états de ports et le résultat d'un test depuis un client connu. Documente la cause racine et un seuil de surveillance après correction. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne ferme pas l'incident sur la seule base d'un ping ponctuel. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.

### Cas de dépannage 31 — Les protections sont configurées mais n'apparaissent pas actives sur le matériel

**Analyse.** La plateforme ou la version peut ne pas supporter le mode attendu, ou la fonction n'a pas été activée sur le bon VLAN/interface. Consulte le guide exact de la version, vérifie l'état opérationnel et les compteurs programmés, puis teste en laboratoire avec un paquet représentatif. Consigne la date, le port, le VLAN, les adresses concernées, le dernier changement et les preuves observées. Compare la configuration à l'état opérationnel et traite une hypothèse à la fois.

**Erreur à éviter.** Ne présume pas qu'une ligne dans la configuration prouve que le contrôle est appliqué en matériel. Après correction, valide à la fois le scénario autorisé et un scénario qui doit rester refusé, puis mets à jour l'inventaire et la procédure de retour arrière.


## 31. Défi final — sécuriser le commutateur d'accès d'une agence

### Contexte

Une agence possède un commutateur d'accès raccordé à la distribution par Gi1/0/24. Les ports Gi1/0/1 à Gi1/0/12 servent aux postes, Gi1/0/13 à Gi1/0/16 aux téléphones et postes en cascade, Gi1/0/17 à Gi1/0/20 aux imprimantes et caméras, Gi1/0/21 au point d'accès Wi-Fi, et les autres ports sont inutilisés. Les VLAN sont : 10 postes, 20 voix, 30 équipements, 40 invités et 99 gestion. Le DHCP est fourni par un serveur central à travers le lien montant. Quelques imprimantes et caméras utilisent des IP statiques. La gestion doit être accessible seulement depuis un poste d'administration dédié.

### Étape 1 — Inventorier et sauvegarder

Liste les ports, propriétaires, VLAN, adresses MAC attendues, méthode d'adressage et services. Identifie le chemin DHCP, les trunks, la racine STP et les équipements qui transmettent légitimement plusieurs MAC. Sauvegarde la configuration et assure-toi que la console ou un accès hors bande est disponible avant les changements.

### Étape 2 — Durcir les ports simples

Fixe les ports des postes et les appareils autonomes en mode access avec leur VLAN prévu. Désactive les ports réellement inutilisés et place-les dans un VLAN de quarantaine sans accès à la production. Applique les protections STP sur les ports terminaux et une politique de port security dont la limite correspond au nombre réel d'adresses.

### Étape 3 — Préserver les exceptions légitimes

Les ports téléphone + PC peuvent apprendre plusieurs adresses. Le point d'accès peut transporter plusieurs VLAN et nécessiter un trunk ou un mécanisme spécifique. Les imprimantes et caméras à IP statique doivent être prises en compte dans la base de correspondance et les politiques ARP/IP. N'applique pas à ces ports un profil utilisateur standard sans validation.

### Étape 4 — Protéger DHCP et ARP

Active DHCP Snooping d'abord sur un VLAN pilote et marque trusted uniquement le chemin par lequel les réponses DHCP légitimes doivent arriver. Confirme la création des bindings. Planifie ensuite DAI et IP Source Guard, en traitant les équipements statiques et les exceptions supportées. Vérifie chaque étape avant d'étendre aux autres VLAN.

### Étape 5 — Contrôler les trunks et STP

Configure le lien montant comme trunk explicite, limite les VLAN autorisés aux VLAN nécessaires et vérifie le VLAN natif selon le design. Vérifie la racine STP et les protections appropriées au rôle des ports. N'active pas BPDU Guard sur une liaison qui doit légitimement participer à STP sans avoir étudié le comportement attendu.

### Étape 6 — Sécuriser l'administration

Place l'interface de gestion dans le VLAN 99 ou une VRF adaptée. Autorise l'administration uniquement depuis les sources prévues, utilise SSH et une authentification contrôlée, préfère une gestion SNMP sécurisée si elle est nécessaire, et envoie les événements aux journaux centralisés. Désactive les services inutiles sans supprimer l'unique accès de secours.

### Étape 7 — Tester la politique

Un poste autorisé doit obtenir un bail valide, accéder au DNS et à la passerelle et joindre ses applications autorisées. Un port libre ne doit pas transporter du trafic de production. Une réponse DHCP provenant d'un port non autorisé doit être bloquée par la politique de Snooping une fois celle-ci validée. Les flux invités ne doivent pas atteindre les imprimantes et la gestion si les règles le prévoient. Le plan de gestion doit refuser les connexions depuis un poste ordinaire.

### Étape 8 — Surveiller et revenir en arrière si besoin

Observe les compteurs de port security, les bindings DHCP, les rejets DAI/IPSG, les changements STP et les journaux. Si un équipement légitime est bloqué, isole le port et la cause ; ne retire pas globalement le contrôle. Restaure l'état précédent par la procédure approuvée si le risque opérationnel l'exige, puis reprends le déploiement après correction.

### Correction attendue

Le défi est réussi lorsque chaque port a un rôle et un propriétaire connus, les trunks ne transportent que les VLAN nécessaires, les ports inutilisés sont réellement isolés, les protections L2 sont adaptées aux usages, les équipements à IP statique sont pris en charge explicitement, l'administration est réservée aux sources autorisées et les journaux permettent d'expliquer les blocages. Les tests doivent démontrer que le trafic métier fonctionne et que les flux interdits restent bloqués.

## 32. Checklist de validation

Avant de terminer le durcissement, vérifie les points suivants :

- Chaque port actif a un propriétaire, un rôle et un VLAN documentés.
- Les ports terminaux sont en mode access sauf exception justifiée.
- Les trunks sont explicites et n'autorisent que les VLAN nécessaires.
- La négociation dynamique de trunk est désactivée là où elle n'est pas nécessaire.
- Le VLAN natif est documenté et cohérent aux deux extrémités.
- Les ports inutilisés sont désactivés ou isolés selon le processus.
- Les profils port security reflètent le nombre d'appareils légitimes.
- Les protections STP correspondent au rôle réel de chaque port.
- Les VLAN, les ports trusted et la base de DHCP Snooping sont vérifiés.
- Les IP statiques sont traitées avant d'activer DAI/IPSG.
- Les contrôles IPv6 correspondent à la politique réelle IPv6.
- 802.1X, MAB et accès de remédiation sont testés selon le profil des appareils.
- Le plan de gestion est isolé et réservé aux sources administratives.
- SSH, AAA, SNMP sécurisé, journaux et synchronisation horaire sont vérifiés.
- Une sauvegarde et un rollback sont disponibles.
- Le trafic autorisé et le trafic refusé ont été testés.
- L'inventaire, les changements et les exceptions sont documentés.

## 33. Glossaire

**Adresse MAC :** identifiant de couche liaison utilisé pour acheminer les trames dans un LAN.

**Table MAC/CAM :** table qui associe une adresse MAC à un VLAN et à un port appris.

**VLAN :** domaine de diffusion logique au sein de l'infrastructure commutée.

**Port access :** port qui dessert généralement un seul VLAN non tagué pour un terminal.

**Trunk :** lien qui transporte plusieurs VLAN à l'aide d'un mécanisme de tagging comme 802.1Q.

**VLAN hopping :** techniques visant à faire traverser du trafic entre des VLAN en contournant la séparation attendue.

**STP :** protocole qui prévient les boucles de couche 2 en calculant une topologie active.

**BPDU Guard :** protection qui réagit à des BPDU inattendues sur un port où elles ne sont pas prévues.

**Port security :** contrôle qui limite ou surveille les adresses MAC apprises sur une interface.

**DHCP Snooping :** contrôle des messages DHCP et mécanisme d'apprentissage des associations IP-MAC-VLAN-port.

**DAI :** Dynamic ARP Inspection, validation des messages ARP selon une politique.

**IP Source Guard :** contrôle des adresses IP source sur un port L2.

**802.1X :** cadre de contrôle d'accès au port fondé sur l'authentification.

**RADIUS :** protocole souvent utilisé pour transporter les échanges d'authentification et d'autorisation.

**MAB :** méthode de contournement contrôlé pour des appareils sans supplicant 802.1X, généralement basée sur MAC et moins forte cryptographiquement.

**Storm control :** limitation de certaines catégories de trafic de couche 2.

**RA Guard :** mécanisme de filtrage des Router Advertisements IPv6 sur les ports où ils ne sont pas attendus.

**MACsec :** protection de confidentialité et d'intégrité Ethernet sur les liaisons compatibles.

**Plan de gestion :** interface et services qui permettent de configurer, administrer et surveiller les équipements réseau.

## 34. Références officielles

- Cisco, dépannage de Dynamic ARP Inspection et IP Source Guard sur Catalyst : https://www.cisco.com/c/en/us/support/docs/switches/lan-switch-software/222274-troubleshoot-dynamic-arp-inspection-dai.html
- Cisco, exploitation et dépannage de DHCP Snooping sur Catalyst 9000 : https://www.cisco.com/c/en/us/support/docs/ip/dynamic-host-configuration-protocol-dhcp-dhcpv6/217055-operate-and-troubleshoot-dhcp-snooping.html
- Cisco, guide de configuration Dynamic ARP Inspection pour IOS XE 17 : https://www.cisco.com/c/en/us/td/docs/switches/lan/c9000/sec-crypto/fhs-sisf/fhs-and-sisf-configuration-guide/dynamic-arp-inspection.html
- IEEE 802.1X, contrôle d'accès réseau basé sur les ports : https://1.ieee802.org/security/802-1x/
- IEEE 802.1AE, MAC Security : https://1.ieee802.org/security/802-1ae/

Consulte la documentation exacte du commutateur, du système et de la version avant d'appliquer des commandes. Les protections L2 ne sont efficaces que lorsque les ports de confiance, les VLAN, les bindings et les exceptions correspondent à la topologie réelle. Un changement de sécurité doit toujours être accompagné d'une validation et d'un plan de retour arrière.

Fin du cours.