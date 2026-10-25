# Téléphonie IP avec Cisco Unified Communications Manager (CUCM)

## Mise en contexte : comment une entreprise gère-t-elle ses appels téléphoniques ?

Dans une entreprise, les téléphones des collaborateurs ne sont pas nécessairement reliés à une ligne téléphonique individuelle. Ils peuvent utiliser le réseau IP de l'organisation pour établir des appels, transférer des communications, mettre un correspondant en attente, accéder à une messagerie vocale ou joindre le réseau téléphonique public.

Cisco Unified Communications Manager, généralement abrégé **CUCM** ou appelé historiquement **CallManager**, est une plateforme de contrôle des appels. Elle enregistre les téléphones compatibles, associe des numéros aux lignes, applique les règles de numérotation et établit les communications entre les terminaux, les passerelles et les autres systèmes de communication.

La téléphonie IP n'est toutefois pas simplement « de la voix qui passe sur Ethernet ». Une solution opérationnelle repose sur plusieurs éléments complémentaires : alimentation et VLAN voix, adressage IP, DHCP, TFTP ou mécanisme de provisionnement, signalisation, flux audio RTP, plan de numérotation, routage des appels, sécurité et qualité de service.

> **L'idée essentielle :** CUCM décide comment les appels sont établis et contrôlés. Le média audio circule ensuite entre les terminaux ou par des ressources intermédiaires selon le scénario. La signalisation et le média sont deux fonctions distinctes, même s'ils participent à une même communication.

## Objectifs pédagogiques

À la fin de ce cours, tu sauras :

- expliquer le rôle de CUCM et les composants d'une solution de téléphonie IP ;
- différencier signalisation et média ;
- décrire les rôles de SIP, SCCP, RTP, RTCP, DHCP et TFTP ;
- comprendre le VLAN voix et le processus d'enregistrement d'un téléphone IP ;
- reconnaître les objets CUCM : utilisateur, téléphone, ligne, numéro d'annuaire, Device Pool et profil de sécurité ;
- comprendre les partitions, les Calling Search Spaces (CSS) et les Route Patterns ;
- suivre le parcours d'un appel interne et les grandes étapes d'un appel externe ;
- identifier les principes d'un trunk SIP, d'une passerelle et d'une ressource média ;
- appliquer les bases de QoS et de sécurité ;
- dépanner une panne simple de téléphone ou d'appel à partir d'une méthode structurée.

## Prérequis

Il est utile de connaître les bases d'IPv4, des VLAN, de DHCP, du routage, de TCP/UDP et de la commutation Ethernet. Les notions de PBX, d'extension et de réseau téléphonique public sont un plus, mais elles sont réexpliquées dans ce cours.

Les noms de menus, les ports, les fonctions disponibles et les étapes exactes peuvent différer selon la version de CUCM, le modèle du téléphone, le protocole choisi et la politique de sécurité. Les exemples sont pédagogiques : ils ne remplacent pas le guide de configuration de la version déployée ni une validation en laboratoire.

## 1. Les bases de la téléphonie IP

### 1.1 Qu'est-ce que la téléphonie IP ?

La téléphonie IP transporte la voix sous forme de données numériques sur un réseau IP. Le microphone produit un signal audio, un codec le numérise et le compresse, puis les échantillons sont placés dans des paquets qui traversent le réseau jusqu'au correspondant. Le terminal de réception reconstitue l'audio.

Un appel comprend généralement deux grandes catégories de trafic :

- **La signalisation** : établissement, modification et terminaison de l'appel. Elle permet par exemple à un téléphone d'indiquer qu'il appelle le numéro 1002, de faire sonner le poste distant, puis de signaler que l'utilisateur a décroché.
- **Le média** : les paquets qui transportent la voix, et éventuellement la vidéo. RTP est fréquemment utilisé pour ce transport.

Schéma simplifié :

```text
             Signalisation (ex. SIP)
Téléphone A <------------------------> CUCM <------------------------> Téléphone B
     |                                                                  ^
     |                                                                  |
     +---------------- Flux média RTP/RTCP, selon le scénario ---------+
```

Le schéma est conceptuel. Le média peut passer directement entre téléphones, traverser une passerelle média, un transcodeur, un pont de conférence, un SBC ou une autre fonction intermédiaire. Il ne faut donc pas supposer que tout le flux audio traverse systématiquement CUCM.

### 1.2 Les éléments d'une solution de téléphonie

| Élément | Fonction principale |
|---|---|
| Téléphone IP ou softphone | Interface de l'utilisateur : numérotation, sonnerie, audio et fonctions d'appel |
| CUCM | Contrôle des appels, enregistrement des terminaux et application du plan de numérotation |
| Switch Ethernet | Connectivité de couche 2, PoE éventuel et transport du VLAN voix |
| DHCP | Fournit l'adresse IP et les paramètres réseau nécessaires au terminal |
| TFTP / mécanisme de provisionnement | Fournit des fichiers ou paramètres de configuration aux téléphones, selon le modèle et le mode de provisionnement |
| DNS et NTP | Résolution des noms et synchronisation de l'heure, selon l'architecture |
| Passerelle vocale ou SBC | Interconnexion avec le réseau téléphonique public ou un opérateur, selon le design |
| Trunk SIP | Liaison de signalisation entre CUCM et une autre plateforme de communication |
| Messagerie vocale, par exemple Unity Connection | Stockage et accès aux messages vocaux, si le produit est déployé |
| Ressources média | Conférence, transcodage, musique d'attente ou autres fonctions selon les ressources disponibles |

Ces composants peuvent être physiques, virtualisés ou fournis sous une autre forme d'architecture prise en charge. Tous ne sont pas obligatoires dans une petite maquette.

### 1.3 Téléphonie traditionnelle et téléphonie IP

Dans une architecture téléphonique traditionnelle, un autocommutateur privé (PABX/PBX) relie des postes à des interfaces téléphoniques. En téléphonie IP, les terminaux utilisent le réseau de données et une plateforme de contrôle d'appels.

| Téléphonie traditionnelle | Téléphonie IP avec CUCM |
|---|---|
| Câblage et interfaces souvent dédiés à la téléphonie | Réseau Ethernet partagé, avec segmentation et QoS adaptées |
| Extensions configurées sur le PBX | Numéros associés à des lignes et terminaux dans CUCM |
| Signalisation propre aux interfaces téléphoniques | Protocoles IP de signalisation, par exemple SIP ou SCCP |
| Évolutions souvent liées aux cartes et au matériel du PBX | Évolutions possibles par configuration, licences et capacité de la plateforme |

La convergence voix/données facilite l'administration, mais elle rend la qualité du réseau IP essentielle. Une saturation, une mauvaise politique QoS ou une configuration de VLAN incorrecte peut dégrader les appels.

## 2. Comprendre l'architecture CUCM

### 2.1 Le rôle de CUCM

CUCM maintient les informations nécessaires au contrôle des appels : identités et paramètres des terminaux, lignes, numéros, profils, règles de routage et liens vers les autres équipements de communication.

Lorsqu'un utilisateur compose un numéro, CUCM analyse la destination et les règles qui s'appliquent à l'appelant. Il détermine si la destination est autorisée, quel terminal ou quelle route utiliser et quelles fonctions doivent intervenir. La logique de contrôle peut être distribuée sur plusieurs nœuds d'un cluster.

CUCM n'est pas, à lui seul, un opérateur téléphonique. Pour joindre le réseau téléphonique public, l'entreprise doit disposer d'un service d'interconnexion, par exemple une passerelle vocale ou un trunk SIP vers un fournisseur, et configurer le routage correspondant.

### 2.2 Les composants logiques importants

**Cluster** : ensemble de nœuds CUCM travaillant ensemble. Dans une architecture courante, un nœud Publisher assure des fonctions de base de données et d'administration, tandis que des nœuds Subscriber peuvent assurer le traitement des appels. Les rôles exacts et la répartition dépendent de la version et du design.

**Service de traitement des appels** : fonction logicielle responsable du traitement de la signalisation et de la logique d'appel.

**Téléphone / endpoint** : terminal enregistré, physique ou logiciel, utilisant un protocole pris en charge.

**Ligne / Directory Number (DN)** : numéro attribué à une ligne logique, par exemple 1001. Une ligne peut être associée à un téléphone et, selon la conception, partagée entre plusieurs terminaux.

**Device Pool** : groupe de paramètres couramment appliqués aux terminaux, tels que la région, le fuseau horaire, les ressources média et d'autres comportements communs.

**Phone Button Template** : modèle qui détermine la disposition des touches et lignes sur les modèles compatibles.

**SIP Profile / Device Security Profile** : paramètres de signalisation et de sécurité associés aux appareils ou aux trunks concernés.

**Gateway / SIP Trunk** : point d'interconnexion avec d'autres réseaux ou systèmes.

### 2.3 Vue globale

```text
                         Administration CUCM
                                 |
                          Cluster CUCM
                  +--------------+--------------+
                  |                             |
             Nœud de contrôle              Nœud(s) de contrôle
                  |                             |
       +----------+-----------+-----------------+---------+
       |                      |                           |
   Téléphone A           Téléphone B                 SIP Trunk
   extension 1001        extension 1002                    |
                                                        SBC / Gateway
                                                            |
                                                       Réseau opérateur
                                                            |
                                                           PSTN
```

Les téléphones ont besoin d'une connectivité IP vers les services correspondants. L'accès à CUCM ne signifie pas que les paquets média sont nécessairement envoyés vers les mêmes nœuds. Le chemin média réel dépend des terminaux, des ressources média et de la topologie.

### 2.4 Protocoles à reconnaître

- **SIP (Session Initiation Protocol)** : protocole de signalisation largement utilisé pour créer, modifier et terminer des sessions multimédias.
- **SCCP (Skinny Client Control Protocol)** : protocole de contrôle utilisé par certains terminaux Cisco dans les déploiements compatibles. Tous les modèles ou déploiements n'utilisent pas SCCP.
- **SDP (Session Description Protocol)** : transporte dans les messages de signalisation une description des paramètres média, par exemple les codecs proposés et les adresses/ports associés.
- **RTP (Real-time Transport Protocol)** : transporte les données média en temps réel, notamment la voix.
- **RTCP (RTP Control Protocol)** : fournit des informations de suivi sur la qualité et la réception des flux RTP.
- **DHCP** : fournit l'adressage IP et peut communiquer les paramètres de serveur nécessaires au téléphone.
- **TFTP** : peut fournir les fichiers de configuration et de firmware requis par les téléphones compatibles avec ce mécanisme.
- **DNS / NTP** : permettent respectivement de résoudre les noms et de synchroniser les horloges.

Il ne faut pas confondre **SIP** et **RTP** : SIP aide à établir l'appel ; RTP transporte généralement la voix une fois le média établi.

## 3. Le réseau qui transporte la voix

### 3.1 VLAN voix

Un VLAN voix sépare logiquement le trafic téléphonique du trafic utilisateur. Il est souvent configuré sur les ports du commutateur auxquels les téléphones IP sont connectés. Le PC de l'utilisateur peut être raccordé au port de commutation du téléphone et utiliser le VLAN de données, tandis que le téléphone utilise le VLAN voix si le modèle et la configuration le permettent.

Exemple de plan d'adressage fictif :

| Réseau | Adresse | Utilisation |
|---|---|---|
| VLAN 10 | 192.168.10.0/24 | Ordinateurs utilisateurs |
| VLAN 20 | 192.168.20.0/24 | Téléphones IP |
| VLAN 30 | 192.168.30.0/24 | Serveurs de communication |

Les passerelles, les règles ACL et les chemins entre VLAN doivent être conçus pour autoriser uniquement les communications nécessaires. Le VLAN voix ne remplace pas le contrôle d'accès.

### 3.2 Alimentation PoE

Le PoE (*Power over Ethernet*) permet à un commutateur compatible de fournir l'alimentation électrique à un téléphone par le câble Ethernet. Il simplifie le déploiement, mais il faut vérifier la compatibilité PoE, le budget de puissance du commutateur et la classe de consommation des terminaux.

Si le téléphone n'a aucune alimentation, les premières vérifications concernent l'alimentation secteur ou PoE et le port de commutation avant d'examiner CUCM.

### 3.3 DHCP et option 150

Lors de son démarrage, un téléphone obtient généralement son adresse IP, son masque, sa passerelle et d'autres paramètres réseau via DHCP. Dans de nombreux environnements Cisco, l'option DHCP 150 sert à indiquer les serveurs TFTP. Les détails exacts de provisionnement dépendent du modèle et de la configuration.

Un téléphone qui reçoit une adresse IP n'est pas forcément enregistré. Il peut encore échouer à joindre le serveur TFTP, télécharger sa configuration, résoudre le nom de CUCM ou établir la signalisation.

### 3.4 Processus d'initialisation et d'enregistrement d'un téléphone

```text
1. Mise sous tension du téléphone
           |
           v
2. Le téléphone rejoint le VLAN voix
           |
           v
3. DHCP fournit l'adresse IP et les paramètres nécessaires
           |
           v
4. Le téléphone découvre/contacte le serveur de provisionnement
           |
           v
5. Il récupère les fichiers et paramètres requis
           |
           v
6. Il contacte le service CUCM prévu par sa configuration
           |
           v
7. CUCM identifie l'appareil et valide son enregistrement
           |
           v
8. Le téléphone est prêt à passer ou recevoir des appels
```

L'enchaînement exact varie selon le protocole utilisé, le mécanisme de provisionnement, la sécurité et la version logicielle. L'enregistrement suppose que le terminal est reconnu, que sa configuration est cohérente et que la communication réseau fonctionne.

### 3.5 À quoi servent TFTP et les fichiers du téléphone ?

Selon le mécanisme de provisionnement et le modèle, le téléphone peut télécharger un fichier de configuration qui décrit son identité, ses lignes, ses serveurs de contrôle et certains paramètres. Il peut également télécharger ou utiliser un firmware pris en charge.

Un fichier absent, une référence à un firmware inexistant ou une configuration incohérente peut empêcher le démarrage ou l'enregistrement. Il faut éviter de pousser un firmware à l'aveugle : une mise à niveau doit être compatible avec le modèle, la version CUCM et la procédure de changement validée.

## 4. Objets fondamentaux dans CUCM

### 4.1 Utilisateur, téléphone et ligne

Ces objets sont liés, mais ils ne sont pas identiques.

- Un **utilisateur** représente une personne ou une identité, souvent utilisée pour les fonctions utilisateur et l'association des appareils.
- Un **téléphone** représente le terminal dans la base CUCM.
- Une **ligne** représente un numéro ou DN configuré pour le traitement des appels.

Exemple :

```text
Utilisateur : Amina Ndi
Téléphone  : SEP001122334455
Ligne      : 1001
Libellé    : Amina Ndi
```

L'identifiant de l'appareil (par exemple une adresse MAC dans les déploiements concernés) n'est pas le numéro d'extension. Le DN 1001 peut, selon le design, être déplacé ou partagé sans modifier l'identité physique du terminal.

### 4.2 Device Pool

Le Device Pool fournit un ensemble de paramètres cohérents pour des appareils. Il peut notamment faire référence à une région, un groupe de ressources média, une liste de groupes CUCM et d'autres paramètres de site.

Une entreprise peut utiliser des Device Pools distincts par site, par exemple :

- `DP-DOUALA` pour les téléphones du site de Douala ;
- `DP-YAOUNDE` pour ceux du site de Yaoundé ;
- `DP-LAB` pour les terminaux d'une maquette.

Les noms sont des exemples. Le principe est de réduire les erreurs de configuration en regroupant les paramètres adaptés à chaque environnement.

### 4.3 Profils et modèles

Les modèles de touches, les profils de téléphone, les profils SIP et les profils de sécurité influencent le comportement du terminal. La sélection dépend du modèle de téléphone, du protocole, des fonctions nécessaires et de la politique de sécurité.

Ne modifie pas simultanément plusieurs profils globaux pour résoudre une panne locale : cela peut affecter de nombreux téléphones. Identifie d'abord le paramètre fautif, vérifie sa portée, puis applique un changement contrôlé.

## 5. Numérotation et contrôle des appels

Le plan de numérotation définit les destinations que les utilisateurs peuvent joindre et la façon dont les numéros sont traités.

### 5.1 Extensions internes

Pour une petite entreprise, un plan simple peut être :

| Service | Extensions fictives |
|---|---|
| Accueil | 1000–1009 |
| Administration | 1100–1199 |
| Technique | 1200–1299 |
| Direction | 1300–1399 |

Ce plan permet d'organiser les extensions et de faciliter la documentation. Dans un vrai déploiement, il doit prendre en compte les sites, les plages existantes, la numérotation publique, les services d'urgence applicables et les besoins d'évolution.

### 5.2 Partitions

Une **partition** est un regroupement logique de destinations du plan de numérotation, comme des DN, des Route Patterns ou des Translation Patterns. Elle classe les destinations selon leur accessibilité.

Exemples de noms fictifs :

- `PT-INTERNAL` : extensions internes ;
- `PT-LOCAL` : destinations téléphoniques locales ;
- `PT-NATIONAL` : destinations nationales ;
- `PT-INTERNATIONAL` : destinations internationales.

La partition n'est pas, à elle seule, une autorisation donnée à un utilisateur. Elle organise les destinations pouvant être recherchées.

### 5.3 Calling Search Space (CSS)

Un **Calling Search Space** est une liste ordonnée de partitions qu'un appelant est autorisé à rechercher pour trouver une destination. Un CSS peut être associé à un téléphone, à une ligne et à d'autres objets, selon la fonction concernée. Lorsque des CSS sont affectés à plusieurs niveaux, leur interaction doit être comprise et testée.

Analogie : les partitions sont les rayons d'une bibliothèque ; le CSS est la liste des rayons que l'appelant a le droit de consulter pour trouver la destination.

Exemple pédagogique :

```text
PT-INTERNAL       -> extensions internes
PT-LOCAL          -> destinations locales
PT-NATIONAL       -> destinations nationales
PT-INTERNATIONAL  -> destinations internationales

CSS-EMPLOYEE      -> PT-INTERNAL, PT-LOCAL, PT-NATIONAL
CSS-MANAGEMENT    -> PT-INTERNAL, PT-LOCAL, PT-NATIONAL, PT-INTERNATIONAL
CSS-LOBBY         -> PT-INTERNAL seulement
```

Ces noms et autorisations sont fictifs. Les numéros d'urgence doivent être conçus et testés séparément selon le pays, la réglementation, le site et la solution de routage.

### 5.4 Route Pattern

Un **Route Pattern** reconnaît un ensemble de numéros composés et indique comment les router. Les caractères génériques utilisés dépendent des conventions CUCM.

Exemples pédagogiques :

- `100X` : correspond à une série d'extensions à quatre chiffres commençant par `100`, le caractère `X` représentant un chiffre selon la syntaxe de CUCM.
- `9.!` : exemple classique de préfixe de sortie suivi d'une suite de chiffres, où la signification et le comportement doivent être vérifiés dans le contexte du plan de numérotation.

Les patterns ne doivent pas être copiés tels quels dans une infrastructure active sans analyser les collisions de motifs, l'accès par CSS, la manipulation des chiffres et le routage final. Un pattern trop large peut envoyer des appels vers la mauvaise destination ou ouvrir des possibilités de fraude téléphonique.

### 5.5 Route List et Route Group

Le routage de sortie peut utiliser :

- **Route Group** : groupe de passerelles ou de trunks envisagés pour acheminer un appel ;
- **Route List** : liste logique qui utilise un ou plusieurs Route Groups ;
- **Route Pattern** : règle de numérotation qui renvoie vers une Route List ou une autre destination compatible.

Cette séparation permet de distinguer le plan de numérotation de la sélection des liaisons physiques ou logiques.

### 5.6 Translation Pattern et manipulation des chiffres

Un Translation Pattern permet de reconnaître un numéro, de modifier les chiffres ou le contexte d'appel, puis de réévaluer la destination en fonction des règles applicables. Il peut être utile pour normaliser les numéros, simplifier les habitudes de numérotation ou adapter les formats internes aux formats attendus par un opérateur.

Toujours tracer le numéro composé, les chiffres après traduction, le CSS effectif et la destination finale. Une transformation incorrecte peut créer une boucle ou un appel rejeté.

## 6. Comment se déroule un appel ?

### 6.1 Appel interne entre deux téléphones

Supposons que le téléphone A utilise le DN 1001 et le téléphone B le DN 1002.

```text
Téléphone A             CUCM              Téléphone B
     |                     |                    |
     |---- demande d'appel -------------------->|
     |                     |---- alerte ------->|
     |<------ tonalité / progression ---------- |
     |                     |<--- décroché ------|
     |<--------- confirmation de connexion -----|
     |==========================================|
                  Flux audio RTP
```

Le dessin simplifie l'échange de messages. Avec SIP, les messages précis et les réponses dépendent de l'état de la session, des capacités des terminaux et du scénario. CUCM contrôle l'appel ; le média peut circuler directement entre terminaux si la topologie, les codecs et les politiques le permettent.

### 6.2 Signalisation SIP, SDP et RTP

SIP établit et contrôle la session. SDP décrit notamment les caractéristiques média proposées ou acceptées, comme les codecs, les ports et les adresses IP pour les flux. RTP transporte ensuite les paquets audio.

Une situation classique est celle d'un appel qui sonne, puis se connecte mais ne transporte aucun son. Cela peut signifier que la signalisation fonctionne tandis que le chemin média est bloqué, qu'une adresse média annoncée est incorrecte, qu'une ACL/NAT perturbe la communication ou qu'une ressource intermédiaire est mal configurée.

**Règle de dépannage :** « l'appel s'établit » et « l'audio circule dans les deux sens » sont deux contrôles distincts.

### 6.3 Appel vers le réseau téléphonique public

```text
Téléphone IP
     |
     | Signalisation vers CUCM
     v
    CUCM
     |
     | Route Pattern / CSS / Route List
     v
SIP Trunk ou passerelle vocale
     |
     v
Opérateur téléphonique
     |
     v
Réseau téléphonique public
     |
     v
Correspondant externe
```

L'appel externe nécessite un service opérateur ou une interconnexion configurée. CUCM ne fournit pas automatiquement une connectivité PSTN simplement parce qu'un Route Pattern existe.

### 6.4 Codec et qualité audio

Un codec convertit la voix entre le format audio et une représentation numérique adaptée au transport. Les codecs diffèrent par la qualité, le débit, la complexité et les exigences d'interopérabilité. Les codecs disponibles et les négociations possibles dépendent des terminaux, des profils et des ressources du système.

Le choix d'un codec ne doit pas être réduit à « le débit le plus faible est toujours le meilleur ». Il faut considérer la qualité souhaitée, la bande passante, les transcodages éventuels et les capacités des deux extrémités.

### 6.5 DTMF, mise en attente et transfert

Les tonalités DTMF servent par exemple à saisir des options dans un serveur vocal. Dans les environnements IP, elles peuvent être transportées de différentes manières selon les équipements et les paramètres négociés, par exemple par des événements RTP ou par un mécanisme pris en charge par l'interconnexion.

La mise en attente, le transfert, la conférence et le renvoi sont des fonctions contrôlées par la plateforme et les terminaux. Une fonction peut échouer même si un appel simple fonctionne, en raison d'une différence de capacités, d'une configuration de trunk ou d'une règle de sécurité.

## 7. SIP Trunk et passerelle vocale

### 7.1 SIP Trunk

Un SIP Trunk relie CUCM à un autre système de communication par SIP : autre cluster, plateforme de voix, SBC ou service opérateur pris en charge. Il faut distinguer la configuration de signalisation du chemin média.

Les éléments à examiner comprennent :

- adresse ou nom du pair distant et résolution DNS éventuelle ;
- port et transport SIP utilisés, par exemple UDP/TCP ou TLS selon le design ;
- profil SIP et profil de sécurité ;
- destinations et CSS associés au trunk ;
- formats de numéros, transformations et codecs ;
- routage des médias, NAT et éventuelle traversée par SBC ;
- certificats, chiffrement et validation de l'identité lorsque TLS est utilisé.

Les ports exacts et les fonctions disponibles sont liés à la version et au scénario d'interconnexion. Il faut s'appuyer sur le guide officiel correspondant et sur les paramètres du fournisseur ou du SBC.

### 7.2 Passerelle vocale

Une passerelle convertit ou interconnecte des appels entre environnements IP et interfaces téléphoniques traditionnelles, ou fournit une autre forme d'accès au réseau opérateur. Le rôle exact dépend du type de passerelle et des interfaces déployées.

CUCM peut diriger les appels vers une passerelle via un Route Pattern et la logique de routage correspondante. Une configuration de passerelle doit inclure une analyse du plan de numérotation, des protocoles, de la signalisation, des paramètres média et des règles de sécurité.

### 7.3 Vérifications de base d'un trunk

En cas d'échec d'appel via trunk, vérifie dans cet ordre :

1. Le nom/IP du pair et la connectivité réseau sont-ils corrects ?
2. Le trunk est-il configuré avec les bons profils et paramètres de sécurité ?
3. Les numéros envoyés et reçus ont-ils le format attendu ?
4. Le CSS permet-il de rechercher le Route Pattern ou la destination nécessaire ?
5. Le pair distant accepte-t-il la requête et le type de numéro ?
6. Le média peut-il traverser le chemin prévu dans les deux sens ?
7. Les journaux et traces montrent-ils un rejet de signalisation, une absence de réponse ou un problème après connexion ?

Ne désactive pas globalement la sécurité ni ne rends le trunk accessible depuis tout le réseau pour « tester plus vite ». Réduis les tests à un environnement contrôlé et à des adresses explicitement autorisées.

## 8. Qualité de service (QoS)

La voix interactive est sensible au délai, à la variation du délai (gigue) et à la perte de paquets. Un débit moyen suffisant ne garantit pas un bon appel si les files d'attente réseau sont mal gérées.

### 8.1 Les indicateurs à comprendre

- **Latence** : temps que met un paquet à traverser le réseau.
- **Gigue** : variation du délai d'arrivée des paquets.
- **Perte** : paquets absents ou abandonnés avant d'atteindre le récepteur.
- **MOS** : estimation de la qualité vocale perçue, calculée selon une méthode donnée ; il faut interpréter sa valeur avec le contexte et les outils utilisés.

### 8.2 Marquage DSCP

Dans les conceptions réseau Cisco courantes, les flux audio RTP sont souvent marqués **EF (DSCP 46)** pour recevoir un traitement prioritaire adapté. La signalisation et la vidéo utilisent d'autres marquages selon la politique de conception. Le marquage seul ne suffit pas : les commutateurs, routeurs, liens WAN et équipements intermédiaires doivent appliquer une stratégie QoS cohérente et éviter la saturation de la file prioritaire.

### 8.3 Chemin QoS simplifié

```text
Téléphone IP
   | audio RTP marqué selon la politique
   v
Switch d'accès
   | classification / files d'attente
   v
Réseau de distribution et cœur
   | transport avec politique QoS cohérente
   v
Routeur WAN / lien intersite
   | contrôle de congestion
   v
Téléphone distant ou passerelle
```

Il faut contrôler les marquages et le traitement réel à chaque saut. Si un commutateur efface DSCP ou si un lien WAN est congestionné, la qualité peut se dégrader même si les téléphones sont bien configurés.

## 9. Sécurité de la téléphonie IP

### 9.1 Menaces courantes

Une infrastructure voix peut être exposée à des risques comparables aux systèmes informatiques : accès non autorisé, usurpation d'identité, écoutes de trafic non chiffré, exploitation d'un terminal vulnérable, appels frauduleux, abus de fonctions administratives ou indisponibilité du service.

### 9.2 Principes de défense

- Segmente les téléphones, les utilisateurs et les serveurs selon une architecture documentée.
- Limite les communications réseau aux flux nécessaires.
- Utilise des comptes administratifs nominatifs, des privilèges minimaux et une authentification robuste.
- Maintiens les versions, firmwares et certificats selon la politique de maintenance validée.
- Contrôle les permissions d'appel à l'aide de partitions, CSS et règles de routage.
- Sécurise les trunks et les interconnexions, notamment en vérifiant l'identité des pairs.
- Sauvegarde la configuration et teste les procédures de restauration.
- Surveille les appels anormaux et les journaux d'événements.

### 9.3 SRTP, TLS et profils sécurisés

Selon le modèle, la version et l'interconnexion, la signalisation SIP peut être protégée par TLS et le média par SRTP. Ces mécanismes ne s'activent pas automatiquement dans tous les environnements : il faut vérifier les certificats, les profils de sécurité, la compatibilité des terminaux et le support du pair distant.

Le chiffrement ne remplace pas la protection du réseau. Il doit être déployé avec une gestion rigoureuse des certificats, des identités et des dépendances opérationnelles.

### 9.4 Limiter les appels sortants

Les CSS et partitions peuvent séparer les destinations autorisées. Par exemple, un téléphone d'accueil peut uniquement joindre les extensions internes et certaines destinations externes, tandis qu'un groupe autorisé peut disposer d'un accès plus étendu.

Il faut aussi sécuriser les règles de sortie et les comptes ayant la capacité de modifier le plan de numérotation. Une mauvaise configuration peut rendre accessible un type d'appel coûteux même si le terminal lui-même est sécurisé.

## 10. Haute disponibilité et continuité de service

La téléphonie est souvent une fonction critique. Une architecture de continuité peut inclure plusieurs nœuds CUCM, une redondance réseau, des passerelles multiples, des liens opérateur diversifiés, des sauvegardes et des mécanismes de repli adaptés.

### 10.1 Redondance CUCM

Les terminaux et les Device Pools peuvent être configurés avec des listes de groupes CUCM selon les mécanismes pris en charge. Si un nœud devient indisponible, le téléphone peut chercher un autre nœud prévu par sa configuration. Le comportement exact dépend de l'architecture, du type de panne et des fonctions déployées.

### 10.2 SRST

Sur certains déploiements, Survivable Remote Site Telephony (SRST) permet à un site distant de conserver un ensemble limité de fonctions téléphoniques lorsque la connexion au système central est perdue, si les équipements et la configuration sont conçus pour cela.

SRST n'est pas automatiquement actif sur tous les téléphones et ne reproduit pas nécessairement toutes les fonctions CUCM. Les scénarios de repli doivent être testés, notamment les appels internes locaux, les appels d'urgence, les appels externes et le retour au fonctionnement normal.

### 10.3 Plan de continuité

Une stratégie opérationnelle devrait documenter :

- les services prioritaires et leur tolérance à l'interruption ;
- les dépendances réseau, DNS, NTP, DHCP, alimentation, CUCM et opérateur ;
- les points de bascule et les conditions de retour au service normal ;
- les sauvegardes, les durées de conservation et les tests de restauration ;
- les contacts et procédures de communication en cas d'incident ;
- les contrôles réguliers de capacité, de licences et de versions supportées.

Une redondance non testée n'est pas une garantie de résilience.

## 11. Méthode de dépannage structurée

Le dépannage doit partir des symptômes observables, puis réduire progressivement le périmètre. Ne commence pas par redémarrer tous les téléphones ou services : cette action peut interrompre les utilisateurs et effacer des indices précieux.

### 11.1 Le téléphone ne s'allume pas

1. Vérifie l'alimentation secteur ou PoE.
2. Vérifie le câble et le port du commutateur.
3. Contrôle le budget PoE et les erreurs du port.
4. Confirme que le matériel démarre normalement.
5. Après ces vérifications, passe au réseau et au provisionnement.

### 11.2 Le téléphone a une adresse IP mais ne s'enregistre pas

1. Confirme le VLAN et le sous-réseau du terminal.
2. Vérifie la passerelle et la route vers les serveurs.
3. Vérifie les paramètres DHCP et le serveur de provisionnement attendu.
4. Vérifie la disponibilité du service CUCM et l'identité/configuration de l'appareil.
5. Vérifie l'heure, DNS et les certificats lorsqu'ils sont nécessaires.
6. Consulte l'état du téléphone dans CUCM, les événements pertinents et les traces appropriées.
7. Vérifie qu'une ACL ou un pare-feu ne bloque pas les communications attendues.

### 11.3 Le téléphone est enregistré mais les appels internes échouent

1. Confirme le DN associé à chaque terminal.
2. Vérifie l'accessibilité de la partition de la destination dans le CSS effectif de l'appelant.
3. Vérifie les Route Patterns ou Translation Patterns qui peuvent prendre priorité.
4. Recherche des doublons ou collisions dans le plan de numérotation.
5. Vérifie les états de ligne, les journaux et la progression de l'appel.

### 11.4 L'appel sonne mais il n'y a pas d'audio

1. Détermine si l'absence de son est unidirectionnelle ou bidirectionnelle.
2. Examine les paramètres de média négociés et les adresses/ports annoncés.
3. Vérifie les ACL, le routage, le NAT et les règles de pare-feu entre les extrémités.
4. Contrôle la présence de ressources média ou d'un SBC lorsque le scénario en exige.
5. Vérifie la compatibilité des codecs.
6. Compare les observations côté émission et côté réception.

### 11.5 Les appels externes échouent

1. Détermine si le problème concerne tous les appels externes ou une destination spécifique.
2. Contrôle le CSS, le Route Pattern, la Route List et le Route Group.
3. Vérifie les transformations de chiffres et le format envoyé à l'opérateur.
4. Vérifie l'état du trunk ou de la passerelle.
5. Consulte les codes de réponse et les traces SIP si disponibles.
6. Distingue le rejet de signalisation d'un problème de média après établissement.
7. Confirme auprès de l'opérateur les prérequis et éventuelles restrictions de destination.

### 11.6 Outils d'observation

Selon la version et les droits d'accès, les outils utiles comprennent :

- les pages d'administration de CUCM et l'état des appareils ;
- Cisco Unified Serviceability ;
- Real-Time Monitoring Tool (RTMT) ;
- les journaux et traces de signalisation ;
- les statistiques média et rapports disponibles ;
- les journaux du commutateur, du routeur, du pare-feu, de la passerelle ou du SBC ;
- un analyseur de paquets utilisé dans un laboratoire ou selon les règles de confidentialité du site.

Les menus, les fichiers de trace et les outils disponibles évoluent. Utilise la documentation liée à la version installée et collecte les données nécessaires avant de changer la configuration.

## 12. Travaux pratiques guidés

Les travaux pratiques sont conçus pour un environnement de formation isolé. Utilise une instance CUCM autorisée, les appareils et images licenciés appropriés, ainsi qu'une connectivité maîtrisée. Ne connecte pas une maquette non sécurisée au réseau téléphonique public.

### TP 1 — Préparer un mini-réseau voix

**Objectif :** comprendre le VLAN voix, DHCP et la connectivité des téléphones.

**Topologie de laboratoire :**

```text
Téléphone A ─┐
             ├── Switch d'accès ── Routeur/L3 ── Réseau des serveurs
Téléphone B ─┘                       |
                                  VLAN voix
                                      |
                            DHCP / TFTP / CUCM
```

**Plan fictif :**

| Élément | Valeur d'exemple |
|---|---|
| VLAN voix | 20 |
| Sous-réseau voix | 192.168.20.0/24 |
| Passerelle voix | 192.168.20.1 |
| CUCM Publisher de laboratoire | 192.168.30.10 |
| CUCM Subscriber de laboratoire | 192.168.30.11 |
| TFTP de laboratoire, si séparé | 192.168.30.10 |

**Étapes :**

1. Documente les VLAN, adresses, passerelles, serveurs DNS/NTP et services de provisionnement attendus.
2. Configure le VLAN voix et la connectivité des ports en suivant le guide du commutateur.
3. Configure une étendue DHCP avec masque, passerelle et paramètres de provisionnement adaptés au mécanisme choisi.
4. Vérifie qu'un terminal obtient une adresse IP dans le bon sous-réseau.
5. Vérifie sa connectivité aux services nécessaires, sans ouvrir l'accès à tout le réseau.
6. Observe le journal DHCP et la séquence d'initialisation du téléphone.

**Contrôles attendus :** adresse IP cohérente, passerelle atteignable, bon serveur de provisionnement, configuration adaptée et absence d'erreurs de VLAN.

**Correction :** si le téléphone obtient une adresse dans le VLAN de données, le problème est probablement en amont de CUCM : configuration de port, découverte du VLAN voix ou DHCP. Si l'adresse est correcte mais le téléphone ne contacte pas le serveur, contrôle le routage, les ACL et l'adresse de provisionnement. Si le provisionnement fonctionne mais l'enregistrement échoue, continue avec la configuration de l'appareil et le service CUCM.

### TP 2 — Créer deux lignes et vérifier un appel interne

**Objectif :** comprendre la relation entre téléphone, ligne, DN et CSS.

**Données fictives :**

| Terminal | Identifiant d'appareil | DN |
|---|---|---|
| Téléphone A | identité matérielle du terminal A | 1001 |
| Téléphone B | identité matérielle du terminal B | 1002 |

**Étapes dans l'interface d'administration :**

1. Vérifie que le modèle et le protocole du téléphone sont pris en charge.
2. Configure ou sélectionne le Device Pool de laboratoire.
3. Ajoute le téléphone dans la base CUCM avec ses paramètres obligatoires et un profil de sécurité approprié.
4. Crée ou associe la ligne 1001 au téléphone A et la ligne 1002 au téléphone B.
5. Affecte les partitions prévues aux DN et un CSS autorisant l'accès aux deux extensions.
6. Applique la configuration selon les besoins de la version et redémarre le téléphone uniquement si nécessaire.
7. Vérifie que les deux terminaux sont enregistrés.
8. Passe un appel de 1001 vers 1002, puis de 1002 vers 1001.
9. Vérifie la sonnerie, la réponse, l'audio bidirectionnel, la terminaison et les informations d'appel.

**Correction :** si un téléphone est non enregistré, traite d'abord la connectivité et le provisionnement. Si les deux sont enregistrés mais l'appel est refusé, vérifie le DN, les partitions et le CSS effectif. Si l'appel s'établit sans audio, traite séparément le chemin média.

### TP 3 — Simuler une restriction de numérotation

**Objectif :** comprendre le contrôle d'accès par CSS et partitions sans appeler le réseau public.

Crée, dans l'environnement de laboratoire, deux catégories fictives de destinations :

- `PT-INTERNAL` contient les extensions internes ;
- `PT-EXTERNAL-LAB` contient une destination de test non reliée au PSTN.

Crée deux CSS :

- `CSS-INTERNAL` contient seulement `PT-INTERNAL` ;
- `CSS-LAB-EXTERNAL` contient `PT-INTERNAL` et `PT-EXTERNAL-LAB`.

**Étapes :**

1. Place les DN internes dans `PT-INTERNAL`.
2. Configure une route de laboratoire non connectée au PSTN dans `PT-EXTERNAL-LAB`, si l'environnement prend en charge ce test.
3. Affecte `CSS-INTERNAL` au téléphone de l'accueil.
4. Affecte `CSS-LAB-EXTERNAL` à un terminal de test autorisé.
5. Teste les appels internes depuis les deux terminaux.
6. Teste uniquement le motif de laboratoire, jamais un numéro public réel.
7. Confirme que les destinations interdites ne sont pas joignables et documente les traces observées.

**Correction :** si l'accueil atteint une destination qui devrait être interdite, vérifie les CSS assignés au téléphone et à la ligne, leur combinaison et les autres chemins de routage. Contrôle également les translations et les Route Patterns qui peuvent rendre une destination accessible indirectement.

### TP 4 — Dépanner un appel sans audio

**Objectif :** séparer les problèmes de signalisation des problèmes média.

**Scénario :** deux téléphones se trouvent sur des sous-réseaux différents. L'appel s'établit, mais le correspondant A n'entend pas B.

**Procédure :**

1. Note les adresses IP des deux terminaux et le sens de l'absence audio.
2. Vérifie les informations de média négociées lorsque les outils du laboratoire le permettent.
3. Examine les règles ACL et le routage entre les sous-réseaux.
4. Vérifie les règles qui concernent les flux UDP média et les éventuels dispositifs NAT/firewall.
5. Vérifie si un SBC ou une ressource média intervient dans le scénario.
6. Compare la signalisation et les observations média des deux côtés.
7. Corrige uniquement la règle ou le paramètre identifié, puis répète le test.

**Correction :** un appel établi prouve que la signalisation a progressé suffisamment pour connecter la session, mais pas que les paquets audio sont transportés dans les deux sens. Un filtrage unidirectionnel, une adresse média inaccessible ou un chemin asymétrique peut provoquer ce symptôme. Les ports média exacts doivent être déterminés à partir de la configuration réelle et du guide de la version, et non devinés.

## 13. Exercices corrigés

### Exercice 1 — Signalisation ou média ?

Un téléphone sonne, l'utilisateur décroche, mais aucun son ne circule. Quelle est la première distinction à faire ?

**Correction :** vérifier séparément l'état de la signalisation et le chemin média. L'établissement d'appel indique que la signalisation a fonctionné jusqu'à un certain point, mais le flux RTP peut être bloqué ou mal négocié.

### Exercice 2 — DHCP et enregistrement

Un téléphone reçoit correctement une adresse IPv4, mais reste non enregistré. Cela prouve-t-il que le réseau est entièrement opérationnel ?

**Correction :** non. L'adresse IP ne prouve ni l'accès au TFTP/provisionnement, ni la connectivité vers CUCM, ni la cohérence de la configuration ou des certificats. Il faut poursuivre les contrôles par étape.

### Exercice 3 — Partition et CSS

La ligne 1002 existe dans CUCM, mais le téléphone 1001 ne peut pas l'appeler. Quel mécanisme doit être vérifié en premier ?

**Correction :** la partition contenant le DN 1002 et le CSS effectif du téléphone et/ou de la ligne appelante. Il faut aussi vérifier que la numérotation composée correspond au DN attendu et qu'aucune règle ne détourne l'appel.

### Exercice 4 — Pourquoi séparer le VLAN voix ?

Cite deux avantages et une limite du VLAN voix.

**Correction :** il permet de séparer logiquement les flux voix des données et de construire des politiques QoS et ACL adaptées. Toutefois, il ne chiffre pas le trafic à lui seul et ne remplace ni l'authentification, ni le filtrage, ni la supervision.

### Exercice 5 — Quel est le rôle de la Route List ?

**Correction :** la Route List constitue une couche logique de routage qui peut utiliser un ou plusieurs Route Groups. Le Route Pattern reconnaît les chiffres composés et renvoie vers la logique de routage appropriée.

### Exercice 6 — Voix prioritaire

Pourquoi marquer le trafic audio en EF ne suffit-il pas à garantir une bonne qualité ?

**Correction :** les équipements intermédiaires doivent conserver ou traiter correctement le marquage, mettre en œuvre des files d'attente adaptées et disposer d'une capacité suffisante. Une politique incohérente ou un lien saturé peut dégrader les appels.

### Exercice 7 — Appels sortants non autorisés

Une personne peut appeler des destinations internationales alors que sa politique devrait l'interdire. Donne trois contrôles.

**Correction :** vérifier les CSS effectifs, les partitions des Route Patterns, et les éventuelles Translation Patterns ou routes alternatives. Examiner également les modifications récentes et les permissions administratives.

### Exercice 8 — Un trunk SIP est-il l'audio ?

**Correction :** non. Le trunk représente l'interconnexion de signalisation entre systèmes et participe à l'acheminement des appels. Le média suit le chemin négocié, lequel peut être différent et impliquer un SBC ou des ressources média.

## 14. Défi final corrigé : déployer une petite téléphonie d'entreprise

### Situation

Une entreprise dispose d'un site unique avec quatre employés, un téléphone d'accueil et un accès externe géré par une plateforme de laboratoire. Le réseau réel de l'opérateur téléphonique n'est pas accessible pendant l'exercice.

### Besoins

- Créer quatre extensions internes : 1001, 1002, 1101 et 1102.
- Autoriser les appels internes entre les quatre extensions.
- Réserver un profil d'accès restreint au téléphone d'accueil.
- Vérifier l'enregistrement de tous les téléphones.
- Vérifier la qualité audio en appel interne.
- Préparer une destination de sortie fictive en environnement de laboratoire sans composer de numéro public.
- Rédiger une procédure de dépannage d'une page.

### Proposition de plan logique

| Objet | Valeur proposée |
|---|---|
| VLAN voix | VLAN 20 |
| Réseau voix | 192.168.20.0/24 |
| Réseau serveurs | 192.168.30.0/24 |
| Partition interne | `PT-INTERNAL` |
| Partition de test externe | `PT-EXTERNAL-LAB` |
| CSS standard | `CSS-INTERNAL` |
| CSS autorisé au laboratoire | `CSS-LAB-EXTERNAL` |
| Site | `SITE-LAB` |

Ces valeurs sont des exemples. Il faut éviter les chevauchements avec les réseaux existants et ne pas raccorder la destination externe fictive à un opérateur pendant l'exercice.

### Étapes de réalisation

1. Documenter l'adressage, le VLAN voix, le DHCP, le provisionnement, les serveurs CUCM et la connectivité requise.
2. Vérifier PoE, VLAN et obtention d'adresse IP.
3. Vérifier le provisionnement et enregistrer les appareils dans CUCM.
4. Créer les lignes et associer les DN aux téléphones attendus.
5. Créer les partitions et CSS avec le principe du moindre privilège.
6. Vérifier les appels entre les quatre extensions et le fonctionnement des fonctions de base.
7. Confirmer que le téléphone d'accueil ne voit que les destinations prévues dans son CSS effectif.
8. Contrôler la qualité audio, les statistiques disponibles et le comportement lors de la terminaison de l'appel.
9. Configurer et tester uniquement une destination d'exercice isolée pour la logique de sortie.
10. Consigner les résultats, les erreurs rencontrées, les changements appliqués et la procédure de retour arrière.

### Résultat attendu

Le projet est validé si les quatre téléphones sont enregistrés, si les appels internes aboutissent et transportent l'audio dans les deux sens, si les permissions de numérotation correspondent aux objectifs et si le diagnostic distingue clairement l'accès réseau, le provisionnement, la signalisation, le plan de numérotation et le média.

### Barème d'autoévaluation

| Compétence | Points |
|---|---:|
| VLAN, DHCP et provisionnement | 20 |
| Enregistrement des terminaux | 15 |
| Lignes, DN et Device Pool | 15 |
| Partitions, CSS et contrôle des appels | 20 |
| Vérification audio et QoS | 15 |
| Sécurité, documentation et diagnostic | 15 |
| **Total** | **100** |

Un résultat d'au moins 80/100, sans défaut critique d'accès ou de sécurité, indique que les concepts fondamentaux sont maîtrisés. Ce barème est pédagogique et ne constitue pas une certification professionnelle.

## 15. Glossaire

- **CUCM** : Cisco Unified Communications Manager, plateforme de contrôle des appels.
- **DN (Directory Number)** : numéro logique associé à une ligne.
- **Endpoint** : téléphone IP, softphone ou autre terminal de communication pris en charge.
- **Device Pool** : regroupement de paramètres communs pour les appareils.
- **CSS (Calling Search Space)** : liste ordonnée de partitions que l'appelant peut rechercher.
- **Partition** : regroupement logique de destinations du plan de numérotation.
- **Route Pattern** : règle qui reconnaît un ensemble de numéros composés.
- **Route Group** : groupe de liaisons ou de passerelles utilisées pour acheminer des appels.
- **Route List** : liste logique qui référence des Route Groups.
- **SIP** : protocole de signalisation pour les sessions multimédias.
- **SDP** : description des paramètres de média négociés.
- **RTP** : transport de données média en temps réel.
- **RTCP** : protocole associé au suivi et aux rapports des flux RTP.
- **TFTP** : protocole de transfert de fichiers utilisé par certains mécanismes de provisionnement.
- **DHCP** : protocole d'attribution dynamique des paramètres IP.
- **PoE** : alimentation électrique fournie par Ethernet.
- **PSTN / RTC** : réseau téléphonique public commuté. Ne pas confondre RTCP, qui accompagne RTP, avec RTC.
- **QoS** : mécanismes de qualité de service sur le réseau.
- **DSCP / EF** : champ de marquage du trafic IP / classe Expedited Forwarding souvent utilisée pour la voix RTP.
- **SBC** : contrôleur de session en bordure, fréquemment utilisé pour sécuriser et interconnecter des communications SIP.
- **SRTP** : protection cryptographique de flux RTP.
- **SRST** : Survivable Remote Site Telephony, mécanisme Cisco pouvant fournir certaines fonctions téléphoniques en mode dégradé selon le design.
- **RTMT** : Real-Time Monitoring Tool, outil de supervision et de collecte d'informations CUCM.

## 16. Références techniques officielles

La documentation ci-dessous permet d'approfondir les tâches selon la version CUCM utilisée. Les procédures de menus et paramètres doivent être recoupées avec la version effectivement installée.

1. **Cisco — System Configuration Guide for Unified Communications Manager, Release 15** : architecture, composants, provisioning des terminaux, trunks, passerelles, ressources média et dial plan.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15.html

2. **Cisco — Configure Endpoints, Release 15** : modèles de terminaux, enregistrement, profils et paramètres de téléphone.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_011101.html

3. **Cisco — Configure Partitions, Release 15** : partitions, Calling Search Spaces et contrôle d'accès au plan de numérotation.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/cucm/admin/15/systemConfig/cucm_b_system-configuration-guide-15/cucm_b_system-configuration-guide-14_chapter_010000.html

4. **Cisco — Troubleshoot IP Phone Unregistration Issues in CUCM** : décrit le processus d'enregistrement SIP/SCCP et les premières étapes de diagnostic des téléphones non enregistrés.
   https://www.cisco.com/c/en/us/support/docs/unified-communications/unified-communications-manager-version-115/220670-troubleshoot-ip-phone-unregistration-iss.html

5. **Cisco — Quality of Service and Call Admission Control** : principes de marquage et de qualité de service pour les communications en temps réel.
   https://www.cisco.com/c/en/us/td/docs/voice_ip_comm/uc_system/design/guides/videodg/vidguide/qos.pdf

## 17. Checklist de révision

Avant de considérer le cours terminé, assure-toi de pouvoir expliquer sans aide :

- [ ] pourquoi CUCM est un système de contrôle d'appels et non un opérateur téléphonique ;
- [ ] la différence entre signalisation SIP et média RTP ;
- [ ] le rôle du VLAN voix, de DHCP et du provisionnement ;
- [ ] les relations entre utilisateur, téléphone, DN et Device Pool ;
- [ ] le rôle des partitions, CSS, Route Patterns, Route Lists et Route Groups ;
- [ ] le trajet d'un appel interne et d'un appel externe ;
- [ ] pourquoi la QoS et le chemin média doivent être vérifiés séparément ;
- [ ] comment sécuriser la numérotation et les trunks ;
- [ ] comment isoler méthodiquement une panne de téléphone ou d'appel.

La compétence à retenir est méthodologique : pour une panne CUCM, identifie d'abord où la chaîne s'interrompt — alimentation, réseau, provisionnement, enregistrement, contrôle de l'appel, acheminement ou média — puis vérifie cette couche avant de modifier les suivantes.
