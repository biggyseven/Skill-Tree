# Sécurité de niveau 2 (L2) — Expert

> **Objectif du cours :** concevoir, déployer, auditer et dépanner une architecture de sécurité L2 à l'échelle d'un campus ou d'un réseau de datacenter. Le fil rouge est l'exploitation fiable : identité, segmentation, intégrité du plan de contrôle, protection des hôtes, chiffrement des liens, automatisation des contrôles et réponse aux incidents.
>
> **Prérequis :** avoir terminé `secu-l2-debutant.md` et `secu-l2-intermediaire.md`, ou maîtriser les VLAN, trunks 802.1Q, STP/RSTP/MST, Port Security, DHCP Snooping, DAI, IP Source Guard, 802.1X, AAA/RADIUS, protection IPv6 et journalisation.
>
> **Plateformes illustrées :** concepts indépendants du constructeur, avec exemples de CLI principalement Cisco IOS/IOS XE. Les commandes sont des modèles à adapter : les noms, valeurs par défaut, restrictions, échelles matérielles et fonctions disponibles dépendent du châssis, du ASIC et de la version logicielle. Une commande acceptée par le CLI n'est pas, à elle seule, une preuve que la fonction est active dans le plan de données.
>
> **Approche pédagogique :** reprendre rapidement les acquis du débutant, vérifier le socle intermédiaire, puis aller vers le design, les interactions entre contrôles, les tests négatifs en laboratoire, l'observabilité et la gestion des changements.
>
> **Choix des schémas :** tous les visuels sont des schémas textuels en blocs monospace. Les topologies montrent les liaisons et les rôles ; les diagrammes de flux présentent les étapes, les décisions et les rejets. Les légendes précisent les hypothèses à vérifier en laboratoire. Ils restent lisibles dans un terminal ou un éditeur Markdown.


## Sommaire

1. [Parcours pratique et critères d'expertise](#1-parcours-pratique-et-critères-dexpertise)
2. [Modèle de menace et architecture de référence](#2-modèle-de-menace-et-architecture-de-référence)
3. [Méthode de changement, rollback et laboratoire](#3-méthode-de-changement-rollback-et-laboratoire)
4. [Construire un standard de port et de VLAN](#4-construire-un-standard-de-port-et-de-vlan)
5. [NAC avancé : 802.1X, EAP-TLS, MAB et RADIUS CoA](#5-nac-avancé--8021x-eap-tls-mab-et-radius-coa)
6. [Segmentation, politiques d'accès et microsegmentation](#6-segmentation-politiques-daccès-et-microsegmentation)
7. [Chaîne de validation IPv4 : DHCP Snooping, DAI et IPSG](#7-chaîne-de-validation-ipv4--dhcp-snooping-dai-et-ipsg)
8. [Sécurité IPv6 et gestion des bindings](#8-sécurité-ipv6-et-gestion-des-bindings)
9. [STP à l'échelle : root design, guards et liens unidirectionnels](#9-stp-à-léchelle--root-design-guards-et-liens-unidirectionnels)
10. [EtherChannel, découverte de voisinage et contrôle du plan L2](#10-etherchannel-découverte-de-voisinage-et-contrôle-du-plan-l2)
11. [MACsec : protéger les liens Ethernet](#11-macsec--protéger-les-liens-ethernet)
12. [Plan d'administration et durcissement des équipements](#12-plan-dadministration-et-durcissement-des-équipements)
13. [Télémétrie, journaux, preuves et détection de dérive](#13-télémétrie-journaux-preuves-et-détection-de-dérive)
14. [Automatisation défensive et contrôle de conformité](#14-automatisation-défensive-et-contrôle-de-conformité)
15. [Segmentation virtualisée et limites du domaine L2](#15-segmentation-virtualisée-et-limites-du-domaine-l2)
16. [Runbooks de réponse aux incidents](#16-runbooks-de-réponse-aux-incidents)
17. [Laboratoires experts guidés](#17-laboratoires-experts-guidés)
18. [Projet de synthèse : campus d'entreprise durci](#18-projet-de-synthèse--campus-dentreprise-durci)
19. [Évaluation finale et corrigé](#19-évaluation-finale-et-corrigé)
20. [Checklist de production et critères d'acceptation](#20-checklist-de-production-et-critères-dacceptation)
21. [Glossaire](#21-glossaire)
22. [Références techniques](#22-références-techniques)


## 1. Parcours pratique et critères d'expertise

### 1.1 Le parcours pratique hérité du niveau débutant

Ne saute pas cette étape au prétexte que le cours est expert. Les incidents avancés se résolvent souvent en découvrant qu'un port a été classé comme trunk alors qu'il dessert un poste, qu'une interface de serveur est « trusted » par erreur, ou qu'un contrôle a été activé sans binding exploitable.

| Étape de contrôle | Manipulation | Preuve attendue |
|---|---|---|
| Inventorier | Relever modèle, version, interfaces, VLAN, trunks, voisins et MAC apprises | Inventaire daté et topologie physique/logique |
| Tester le chemin nominal | DHCP ou IP statique, passerelle, DNS, services autorisés | Matrice de tests issue d'un poste témoin |
| Contrôler les accès | Vérifier port access, VLAN natif, VLAN autorisés, ports inutilisés | Tableau des rôles de ports et écarts |
| Contrôler les protections | Vérifier Port Security, DHCP Snooping, DAI, IPSG, STP, IPv6 FHS | Configurations et états opérationnels |
| Préparer le retour arrière | Sauvegarder la configuration et tester la procédure en maquette | Sauvegarde exploitable et rollback écrit |

### 1.2 Le contrôle intermédiaire avant d'attaquer l'expert

| Compétence | Question de validation |
|---|---|
| Trunks | La liste des VLAN autorisés est-elle minimale et identique aux besoins des deux extrémités ? |
| 802.1X | Que se passe-t-il pour un poste sans supplicant, un téléphone, une imprimante MAB et une panne AAA ? |
| DHCP Snooping/DAI/IPSG | D'où vient chaque binding ? Que se passe-t-il pour un hôte statique ou après un redémarrage ? |
| STP | Quel switch doit être root pour chaque instance et quelles interfaces sont edge, réseau ou bloquées ? |
| IPv6 | Qui peut émettre des RA et des réponses DHCPv6 ? Comment les bindings IPv6 sont-ils obtenus ? |
| Supervision | Une violation produit-elle une preuve exploitable, avec heure, interface, VLAN et adresse MAC ? |

Si une réponse est incertaine, le laboratoire correspondant plus loin est un prérequis, pas une punition : l'expertise consiste à rendre le comportement vérifiable.

### 1.3 Ce qui distingue le niveau expert

À la fin, tu dois pouvoir :

- concevoir des rôles de ports et des politiques d'accès cohérents avec un modèle de menace ;
- expliquer quelles données une protection consulte, à quel endroit elle s'applique, et quels trafics légitimes peuvent être bloqués ;
- définir des politiques par type d'équipement plutôt que copier une configuration identique sur tous les ports ;
- diagnostiquer une panne combinant AAA, VLAN, bindings et protection de topologie sans désactiver toutes les protections ;
- démontrer la sécurité par des tests positifs et négatifs, des compteurs, des journaux et une revue de configuration ;
- prévoir les effets des changements, la restauration et la gestion des exceptions.

### 1.4 Règles de sécurité des travaux pratiques

Tous les scénarios d'usurpation, de boucles et de génération de trafic doivent rester dans une maquette isolée et autorisée. N'émets pas de faux DHCP, de fausses annonces ARP/IPv6, de boucles ou de tempêtes sur un réseau de production. Pour simuler une violation, utilise un VLAN de laboratoire, un équipement contrôlé, un générateur limité et des seuils bas définis pour cet exercice. Conserve les résultats et nettoie la maquette après le test.


## 2. Modèle de menace et architecture de référence

### 2.1 Modéliser les actifs, chemins et frontières

La segmentation ne doit pas seulement refléter l'organigramme. Elle doit représenter les relations nécessaires entre appareils et services. Une imprimante, un poste de travail et un contrôleur de domaine n'ont ni le même profil de communication ni le même niveau de privilège.

| Actif ou fonction | Risque prioritaire | Contrôles typiques | Preuve opérationnelle |
|---|---|---|---|
| Poste géré | Appareil non conforme ou usurpation d'identité | 802.1X/EAP-TLS, VLAN/ACL dynamique, EDR hors du périmètre L2 | Session NAC, certificat, rôle, compteurs d'accès |
| Téléphone IP | Usurpation ou pont non prévu | 802.1X/MAB selon capacités, voix séparée, limitation des flux | État de session voix/données et tests QoS |
| Imprimante/IoT | Firmware ancien, absence de supplicant | MAB surveillé, VLAN dédié, ACL très étroite | Inventaire propriétaire + flux autorisés |
| Switch d'accès | Modification de topologie, configuration dérivée | STP guards, trunks contrôlés, gestion dédiée, contrôle d'intégrité | Root attendu, état des trunks, conformité |
| Serveur/Hyperviseur | Multiplicité MAC, VLAN tags ou ponts virtuels | Port-channel/trunk explicitement validé, ACL, contrôle de l'hyperviseur | Inventaire vSwitch, MAC, VLAN et flux |
| Plan d'administration | Vol de compte ou mouvement latéral | SSH, AAA, MFA côté service, ACL de gestion, SNMPv3 | Journaux d'authentification et chemins d'accès |
| Liens entre switches | Écoute locale, usurpation ou panne unidirectionnelle | MACsec si adapté, STP, UDLD, LACP, supervision optique | État MACsec/LACP, erreurs optiques, événements STP |

### 2.2 Topologie de référence du cours

```text
                       +-------------------------+
                       | Services de sécurité    |
                       | RADIUS / PKI / Syslog   |
                       | NTP / supervision       |
                       +-----------+-------------+
                                   |
                           réseau de gestion
                                   |
       +---------------------------+---------------------------+
       |                       DIST-1 / DIST-2                  |
       |  root STP planifié / SVI / ACL / politiques inter-VLAN |
       +-----------+-----------------------------+-------------+
                   ||                            ||
             trunks/Po                       trunks/Po
                   ||                            ||
          +--------+---------+          +---------+--------+
          | ACC-1            |          | ACC-2             |
          | NAC / bindings   |          | NAC / bindings    |
          +--+-----+-----+---+          +---+----+----+-----+
             |     |     |                  |    |    |
            PC   IPphone IoT                PC  AP  printer
```

`Po` signifie Port-channel/EtherChannel. La redondance physique doit être conçue en même temps que STP/LACP, pas ajoutée après coup. Un trunk doit transporter uniquement les VLAN nécessaires ; la présence d'un deuxième câble ne justifie pas une extension arbitraire du domaine L2.

### 2.3 Modèle de traitement d'une trame

```text
  TRAME ENTRANTE
       |
       v
  +---------------------+
  | 1. IDENTITE         |  802.1X / MAB / rôle
  +----------+----------+
             | OK
             v
  +---------------------+
  | 2. PORT ET VLAN     |  access / trunk / VLAN attendu
  +----------+----------+
             | OK
             v
  +---------------------+
  | 3. VALIDATION L2    |  DHCP / ARP / IP / MAC / bindings
  +----------+----------+
             | OK
             v
  +---------------------+
  | 4. POLITIQUE METIER |  ACL / groupe / flux autorisé
  +----------+----------+
             | OK
             v
  +---------------------+
  | 5. OBSERVABILITE    |  compteurs / journaux / télémétrie
  +----------+----------+
             |
             v
       TRAFIC ACCEPTE

  A CHACUNE des 5 étapes : résultat non conforme
                         |
                         v
              +--------------------------+
              | REFUS / QUARANTAINE      |
              | identifier le premier    |
              | contrôle en échec et     |
              | conserver les preuves    |
              +--------------------------+

  Un contrôle réussi ne garantit pas que les suivants réussiront.
  Ne désactive pas toutes les protections pour contourner un rejet.
```

**Lecture :** le contrôle d'identité ne valide pas les adresses sources ; un binding correct n'autorise pas forcément le flux métier ; une politique bien définie ne prouve pas que le matériel la programme comme attendu. Il faut collecter des preuves à chaque frontière.

### 2.4 La matrice de menace

Avant de configurer, remplis une matrice de ce type :

| Menace | Prévention | Détection | Limitation de l'impact | Risque résiduel |
|---|---|---|---|---|
| Appareil inconnu | 802.1X, MAB contrôlé | échecs AAA, nouvelles MAC | rôle/ACL restreint | usurpation d'identité faible selon méthode |
| DHCP frauduleux | DHCP Snooping / DHCPv6 Guard | compteurs de drop et logs | VLAN client isolé | ports trusted mal classés |
| ARP/IP spoofing | DAI, IPSG, segmentation | violations et changements de binding | microsegmentation | flux statiques/exceptionnels |
| Root STP inattendu | root design, Root Guard, BPDU Guard | changement du root, TCN | redondance et convergence contrôlées | erreurs de design ou de domaine STP |
| Écoute sur lien | MACsec | état MKA/SecY, événements de clé | chiffrement applicatif en complément | extrémités compromises et trafic hors périmètre |
| Compte admin compromis | AAA, ACL, MFA côté service | logs d'accès, source inhabituelle | accès hors bande et rôle minimal | session d'administration déjà ouverte |

Un contrôle ne doit jamais être déclaré « suffisant » sans préciser son point d'application et son champ de visibilité.


## 3. Méthode de changement, rollback et laboratoire

### 3.1 La fiche de changement obligatoire

Un changement de sécurité L2 peut couper un étage entier. Avant d'appliquer une politique de binding ou de modifier STP, prépare une fiche comprenant :

1. **Périmètre** : équipements, interfaces, VLAN, utilisateurs, services et fenêtre.
2. **État initial** : configuration, topologie, root STP, sessions 802.1X, bindings, compteurs d'erreur et résultats fonctionnels.
3. **Hypothèse** : le risque à réduire et le mécanisme choisi.
4. **Plan de test** : flux autorisés qui doivent continuer, flux interdits qui doivent être rejetés.
5. **Plan de rollback** : commandes ou sauvegarde, accès console/hors bande, condition explicite de retour arrière.
6. **Validation après changement** : fonction, compteurs, journaux, latence et état des adjacences.
7. **Approbation** : propriétaire du service, opérateur, heure de début/fin et résultat.

### 3.2 Déploiement par anneaux

```text
Anneau 0 : maquette fidèle (mêmes versions et mêmes fonctions)
        |
        v
Anneau 1 : switch pilote + appareil représentatif
        |
        v
Anneau 2 : petit groupe de ports/étage avec observation renforcée
        |
        v
Anneau 3 : déploiement progressif par rôle de port
        |
        v
Anneau 4 : audit, retrait des exceptions temporaires et documentation
```

Ne généralise pas une configuration testée seulement avec un PC Windows si le parc contient des téléphones IP, des imprimantes, des hyperviseurs, des stations Linux, des bornes ou des équipements médicaux/industriels.

### 3.3 Conditions d'arrêt

Arrête le changement et reviens à l'état contrôlé si un seul des critères de sécurité ou de service suivants est rencontré :

- le root bridge change sans raison prévue ;
- le nombre de sessions non autorisées ou de rejets augmente au-delà du seuil de test ;
- DHCP, DNS, voix ou applications essentielles échouent sur plusieurs ports représentatifs ;
- un trunk transporte un VLAN non prévu ;
- les bindings deviennent incohérents ou disparaissent après une action attendue ;
- la supervision n'enregistre plus les événements nécessaires au diagnostic ;
- l'accès de gestion est perdu ou le rollback ne peut plus être exécuté.

### 3.4 Sauvegarde et comparaison

Conserver un snapshot avant/après et comparer la configuration effective, pas uniquement le fichier généré par l'automatisation. Certaines fonctions sont héritées d'un template, d'une politique centrale ou d'un état opérationnel qui n'apparaît pas directement dans le même bloc de configuration. La sauvegarde n'est valable que si le fichier peut être restauré et si le matériel de laboratoire montre que la restauration fonctionne.


## 4. Construire un standard de port et de VLAN

### 4.1 Les rôles de port à définir

Un standard raisonnable comprend au minimum les rôles suivants :

| Rôle | Comportement attendu | Contrôles à étudier | Exceptions typiques |
|---|---|---|---|
| `USER-8021X` | Terminal géré, identité individuelle | EAP-TLS, VLAN/ACL par rôle, DHCP Snooping, DAI, IPSG selon compatibilité, BPDU Guard | dépannage documenté et borné dans le temps |
| `VOICE-DATA` | Téléphone + éventuellement PC | 802.1X multidomain ou politique adaptée, VLAN voix, QoS et limites par appareil | compatibilité téléphone/supplicant à tester |
| `IOT-MAB` | Appareil sans supplicant | MAB, VLAN dédié, ACL très restrictive, limite MAC et inventaire | adresse MAC usurpable, donc ne pas traiter MAB comme preuve forte |
| `AP-EDGE` | Point d'accès avec plusieurs clients | trunk/access selon le modèle, VLANs exacts, contrôles adaptés à l'AP | 802.1X supplicant ou politique de port dédiée |
| `SERVER-ACCESS` | Serveur physique à une ou plusieurs MAC | VLAN dédié, ACL, bindings statiques/dynamiques selon l'hôte | hyperviseur et machines virtuelles imposent une revue spécifique |
| `SWITCH-UPLINK` | Liaison entre commutateurs | trunk borné, LACP si agrégé, STP guards adaptés, UDLD si supporté | ne jamais activer BPDU Guard comme sur un port terminal |
| `ADMIN-OOB` | Gestion réseau | VLAN/réseau de gestion, ACL, SSH, AAA, SNMPv3 | accès d'urgence strictement documenté |
| `PARKING` | Port sans usage prévu | administrativement désactivé, VLAN de parking, description et inventaire | activation uniquement via processus de changement |

### 4.2 Pourquoi un unique modèle de port est dangereux

Appliquer la même configuration à un poste, un hyperviseur et un trunk entraîne des conflits : l'hyperviseur peut légitimement présenter plusieurs MAC ; le trunk doit émettre des BPDUs ; un téléphone peut nécessiter une politique de domaine voix ; une borne peut transporter plusieurs VLAN. Le bon objectif est un nombre limité de profils explicites, pas un modèle universel.

### 4.3 Exemple de durcissement d'un port utilisateur Cisco IOS/IOS XE

> **Exemple de référence, pas une configuration universelle.** Vérifie d'abord que l'interface dessert bien un terminal unique, que le VLAN 10 existe et que les prérequis AAA et 802.1X sont configurés. Le bloc ci-dessous illustre le principe d'un rôle de port ; il ne remplace pas la configuration globale de RADIUS ni la politique du serveur.

```text
interface GigabitEthernet1/0/12
 description USER-8021X - prise bureau B-214
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
 ! La limite MAC ne doit être réglée qu'après inventaire du poste et des éventuels téléphones/docks.
 ! Port Security, 802.1X et IPSG peuvent avoir des interactions dépendantes de la plateforme.
 authentication port-control auto
 dot1x pae authenticator
```

Ce bloc est volontairement conservateur : il n'ajoute pas un nombre arbitraire de MAC sécurisées, ne force pas un fallback MAB et ne configure pas de VLAN critique sans analyser le risque. Les noms de commandes et les prérequis exacts doivent être validés pour la plateforme.

### 4.4 Ports inutilisés

Un port inutilisé doit être identifié dans l'inventaire, désactivé administrativement, doté d'une description explicite et affecté à un VLAN de parking non utilisé pour les postes. La protection ne s'arrête pas à `shutdown` : la surveillance doit détecter une réactivation manuelle ou l'apparition d'un équipement là où aucun raccordement n'est prévu.

Exemple à adapter :

```text
interface range GigabitEthernet1/0/20-24
 description UNUSED - PARKING - activation sur changement approuve
 switchport mode access
 switchport access vlan 999
 shutdown
```

N'applique pas une plage d'interfaces avant d'avoir exclu les uplinks, les ports d'empilage, les AP, les téléphones et les ports reliés à un système de supervision.

### 4.5 VLAN natif, VLAN de gestion et trunks

- Désactive la négociation dynamique de trunk lorsque la plateforme la propose et qu'elle n'est pas requise.
- Précise le mode access ou trunk plutôt que laisser la négociation décider.
- Autorise uniquement les VLAN requis sur chaque trunk.
- Documente le VLAN natif et vérifie que les deux extrémités ont un comportement cohérent.
- Évite de placer des terminaux ordinaires dans le VLAN natif ou dans le VLAN de gestion.
- N'assimile pas le fait de choisir un VLAN natif peu utilisé à un contrôle cryptographique ou à une authentification.

Commande de principe (la syntaxe varie) :

```text
interface TenGigabitEthernet1/1/1
 description UPLINK vers DIST-1
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,99
 ! VLAN natif documenté et identique aux deux extrémités
 ! Aucun VLAN supplémentaire sans justification d'architecture
```

### 4.6 Port Security : quand et quand ne pas l'utiliser

Port Security peut limiter les MAC sur un port, mais ce mécanisme ne prouve pas l'identité de l'utilisateur. Il peut être utile sur certains ports d'accès simples, mais entre en tension avec des téléphones + PC, des hyperviseurs, des points d'accès, des appareils à MAC multiples ou des scénarios de remplacement rapide. Une violation ne doit pas conduire à couper aveuglément un port de production sans savoir si la politique de violation choisie est `shutdown`, `restrict` ou une autre action.

Avant activation :

1. relever le nombre normal de MAC par port sur une période représentative ;
2. identifier docks, téléphones, machines virtuelles et mécanismes de failover ;
3. tester les événements de mobilité et de remplacement matériel ;
4. choisir une action adaptée à la criticité et à la capacité d'intervention ;
5. superviser les changements de MAC et revoir les exceptions.


## 5. NAC avancé : 802.1X, EAP-TLS, MAB et RADIUS CoA

### 5.1 Séparer authentification, autorisation et posture

- **Authentification :** quel compte ou quel appareil prouve son identité ?
- **Autorisation :** quelle connectivité cette identité reçoit-elle ?
- **Posture :** des signaux complémentaires indiquent-ils que le terminal satisfait la politique ? La posture peut dépendre d'une plateforme NAC/endpoint et n'est pas une propriété automatique d'Ethernet.
- **Accounting :** quelles sessions ont existé, sur quel port, pendant quelle durée et avec quelle décision ?

Une session « authentifiée » n'est pas nécessairement « autorisée à tout faire ». Le résultat pratique d'une authentification devrait être un rôle compréhensible : VLAN, ACL, groupe de sécurité ou ensemble de services permis.

### 5.2 Échange 802.1X de bout en bout

```text
        SUPPLICANT                    AUTHENTICATOR                    SERVEUR AAA
      (poste / terminal)              (switch d'accès)                   (RADIUS)
              |                              |                                |
  1. Lien actif                            |                                |
              |<----- EAP-Request/Identity --|                                |
  2. EAP-Response/Identity ---------------->|                                |
              |                              |--- RADIUS Access-Request ----->|
              |                              |    (EAP encapsulé)              |
              |<----- EAP-Request (TLS) -----|<-- Access-Challenge ------------|
  3. EAP-TLS : certificats et preuve ------>|--- Access-Request ------------->|
              |                              |<-- Challenge / suite EAP --------|
              |<----------- échanges EAPOL -->|--- échanges RADIUS ------------>|
              |                              |                                |
              |                              |<-- Access-Accept ou Reject ------|
              |                              |                                |
  4. Succès : port/session autorisé         |                                |
              |<-- rôle / VLAN / ACL --------|                                |
              |                              |                                |

  TERMINAL  <------ EAPOL sur le lien local ------>  SWITCH
  SWITCH    <------------ RADIUS/IP ------------->  SERVEUR AAA

  Access-Accept = authentification acceptée, avec autorisation à appliquer.
  Access-Reject = refus ; aucune session normale ne doit être ouverte.
  Panne AAA     = appliquer la politique de secours explicitement définie,
                  jamais supposer qu'elle est identique sur tous les switches.
```

Le trafic EAPOL est échangé entre terminal et authenticator ; le switch relaie les messages EAP au serveur AAA via RADIUS. Ne confonds pas le transport EAPOL local et le transport RADIUS dans le réseau d'infrastructure.

### 5.3 Pourquoi EAP-TLS est souvent privilégié pour les terminaux gérés

EAP-TLS s'appuie sur une authentification basée sur certificats. Cela évite de traiter une adresse MAC comme une identité forte et permet une gestion de cycle de vie : émission, renouvellement, révocation et validation de la chaîne. La sécurité réelle dépend de la validation des certificats, de la protection des clés privées et de la politique du supplicant. Un certificat expiré ou une autorité de certification incorrectement distribuée peut provoquer une panne d'accès à grande échelle.

Points d'audit :

- certificats terminaux et certificats serveurs avec EKU et noms attendus ;
- chaîne de confiance et dates valides ;
- comportement en cas de certificat révoqué ou absent ;
- renouvellement silencieux avant expiration ;
- horloges cohérentes via NTP ;
- stratégie de récupération si le certificat, le supplicant ou le serveur AAA échoue ;
- absence de méthode de repli plus faible sans besoin et périmètre explicites.

### 5.4 MAB : mécanisme de compatibilité, pas preuve d'identité forte

Le MAC Authentication Bypass peut convenir à un appareil qui ne prend pas en charge 802.1X, mais une adresse MAC est observable et usurpable. MAB doit être associé à une autorisation limitée : VLAN IoT, ACL définie par les services nécessaires, inventaire du propriétaire, profilage prudent et surveillance des changements. Évite de transformer l'absence de supplicant en accès normal au réseau utilisateur.

Pour chaque type de MAB, documente : nom de l'équipement, adresse(s) MAC connue(s), emplacement, propriétaire, flux attendus, durée de l'exception, alternative au remplacement et responsable de la validation périodique.

### 5.5 Modes d'hôte et prises partagées

Les termes exacts varient selon le constructeur, mais les concepts courants sont :

| Mode conceptuel | Effet | Risque ou limite |
|---|---|---|
| Un seul hôte | Une session authentifiée sur le port | Peut bloquer les scénarios téléphonique + PC |
| Multi-hôte | Une authentification peut autoriser plusieurs appareils derrière le même port | Un terminal autorisé peut ouvrir l'accès à d'autres appareils en aval |
| Multi-auth | Chaque terminal est authentifié individuellement | Plus de sessions et d'états à diagnostiquer |
| Multi-domaine | Gère des domaines de rôle distincts, souvent voix et données | Ne couvre pas automatiquement toutes les topologies avec plusieurs appareils |

Le mode doit correspondre au branchement réel. Une prise qui dessert un téléphone et un PC ne doit pas recevoir le même profil qu'un port d'imprimante. Un mini-switch non autorisé peut modifier le modèle de confiance même si le premier appareil est authentifié.

### 5.6 VLAN invité, VLAN restreint et serveur AAA indisponible

Le choix « fail-open » ou « fail-closed » est une décision de continuité et de risque. Il n'existe pas de règle universelle qui autorise toujours ou refuse toujours le trafic pendant une panne RADIUS.

| Scénario | Choix à étudier | Garde-fous |
|---|---|---|
| Poste utilisateur géré, AAA indisponible | Accès restreint ou maintien d'une session déjà autorisée selon politique | VLAN/ACL limité, alerte immédiate, délai et sortie du mode critique |
| Invité | Accès limité ou refus selon le service | Aucun chemin vers les réseaux internes, durée courte |
| Téléphone IP | Continuité de la voix si le risque métier le justifie | VLAN voix restreint, pas d'autorisation générale de la donnée |
| Imprimante ou IoT MAB | Règle par appareil et service | Ne pas convertir une panne AAA en accès illimité |

Toute politique de secours doit être testée lorsque le serveur est indisponible puis revient, afin de vérifier la réauthentification, le changement de rôle et les sessions obsolètes.

### 5.7 RADIUS CoA et changement de rôle en cours de session

Change of Authorization (CoA) permet, lorsque la plateforme le supporte et qu'il est configuré correctement, de modifier une session à la suite d'un changement de politique ou d'un événement de conformité. CoA est puissant : une erreur peut réauthentifier ou déconnecter un grand nombre de terminaux.

Avant activation :

1. définir les sources RADIUS légitimes et contrôler le secret/les mécanismes de protection supportés ;
2. filtrer la gestion du plan de contrôle afin qu'un hôte ordinaire ne puisse pas envoyer des messages CoA ;
3. démarrer sur une session de laboratoire et vérifier l'identifiant de session ;
4. valider l'effet précis (changer le rôle, réauthentifier ou déconnecter) ;
5. simuler le serveur inaccessible et la reprise ;
6. surveiller les événements et prévoir une procédure de secours.

### 5.8 Méthode de diagnostic NAC

Traite un seul échec du terminal au serveur. Une capture côté terminal ou port d'accès, les journaux du switch, l'état RADIUS, les journaux du serveur AAA et le résultat de la politique forment ensemble un jeu de preuves beaucoup plus utile qu'un simple « 802.1X ne marche pas ».

Ordre recommandé :

1. le lien physique est-il stable et le port dans le bon mode ?
2. le terminal émet-il EAPOL et le switch répond-il ?
3. le switch atteint-il le serveur AAA avec l'adresse source attendue ?
4. l'échange RADIUS contient-il une réponse et une raison exploitable ?
5. le certificat, l'identité et la politique sont-ils acceptés ?
6. la session a-t-elle reçu le rôle/les attributs prévus ?
7. le VLAN existe-t-il et est-il transporté jusqu'à la passerelle ?
8. DHCP, DNS et le service final passent-ils après autorisation ?

Commandes de vérification (selon version) :

```text
show access-session interface <interface> details
show authentication sessions interface <interface> details
show aaa servers
show radius statistics
show logging | include DOT1X|RADIUS|AUTHMGR
```

Certaines versions privilégient `show access-session`, d'autres exposent une syntaxe historique. Consulter la référence de commandes de la plateforme ; limiter les `debug` en production et préférer une capture ciblée si possible.


## 6. Segmentation, politiques d'accès et microsegmentation

### 6.1 Le VLAN isole le domaine de diffusion, pas toute la communication

Deux hôtes du même VLAN peuvent communiquer directement au niveau L2 sans passer par l'ACL inter-VLAN du routeur. Par conséquent, un pare-feu ou une ACL placé uniquement sur une SVI ne filtre pas nécessairement les échanges entre deux hôtes du même VLAN. Il faut choisir le point de contrôle selon le chemin réel : ACL de port (PACL), VLAN ACL (VACL), ACL de SVI, politique de pare-feu distribué, contrôle par groupe ou microsegmentation sur l'hyperviseur.

### 6.2 Choisir le contrôle en fonction du chemin

| Contrôle | Point d'application typique | Cas d'usage | Limite à vérifier |
|---|---|---|---|
| ACL sur SVI / L3 | Trafic routé entre VLAN | Contrôler les flux inter-VLAN | Ne filtre pas forcément le trafic local au même VLAN |
| PACL | Port d'entrée physique | Filtrer certains flux entrants sur un port | Ordre/priorité et fonctions supportées variables |
| VACL | Trafic associé à un VLAN, y compris selon la plateforme certains flux bridgés | Contrôle dans un domaine L2 | Syntaxe, ordre et capacités matérielles à vérifier |
| Private VLAN / port isolation | Communication entre ports d'un même segment selon rôles | Isolation de clients/serveurs | Ne remplace pas le contrôle des flux routés |
| SGACL / SGT (solution constructeur) | Politique basée sur groupes de sécurité | Appliquer une politique liée au rôle plutôt qu'à l'adresse seule | Dépend du support, de la propagation du tag et du point d'application |
| Microsegmentation hyperviseur | vNIC / workload | Limiter les flux east-west virtuels | Ne protège pas automatiquement les flux hors de l'hyperviseur |
| Pare-feu distribué / hôte | Pile réseau du workload ou point distribué | Politique très granulaire | Gestion, visibilité et couverture des systèmes non gérés |

### 6.3 Construire une matrice de flux explicite

Exemple conceptuel à adapter :

| Source | Destination | Autorisé | Contrôle à valider |
|---|---|---|---|
| Utilisateur géré | DNS/DHCP/identité | Oui, ports requis seulement | ACL / pare-feu + service de base |
| Utilisateur géré | Serveur métier | Selon rôle | ACL inter-VLAN ou politique par groupe |
| Invité | Réseaux internes privés | Non | Pare-feu/ACL et vérification IPv4 **et** IPv6 |
| Imprimante | Serveur d'impression, DNS, NTP | Seulement ce qui est nécessaire | VLAN IoT + liste blanche de flux |
| Imprimante | Postes clients | Non par défaut | Filtrage au point où le trafic passe réellement |
| Administration réseau | SSH/SNMP/HTTPS d'équipements | Oui depuis bastion/postes dédiés | ACL de gestion et AAA |
| Poste utilisateur | SSH des switches | Non | Filtrage du plan de gestion |

« Refus par défaut » signifie que les flux non décrits sont refusés au point d'application correct. Cela ne signifie pas qu'on doit supprimer sans analyse les protocoles nécessaires au fonctionnement : ARP, ND, DHCP, DNS, NTP, authentification, supervision et dépannage doivent être identifiés explicitement.

### 6.4 Private VLAN et isolation de ports

Les Private VLAN (PVLAN) peuvent distinguer un port promiscuous (par exemple une passerelle ou un service central) et des ports isolés ou communautaires. C'est utile lorsque plusieurs hôtes doivent partager un sous-réseau IP tout en limitant leurs échanges L2. Cependant, la compatibilité dépend du modèle et des fonctions activées ; certaines protections de source ou politiques ne peuvent pas être combinées avec PVLAN sur des plateformes précises. Vérifie la matrice de compatibilité avant le design.

Schéma textuel :

```text
                +--------------------------+
                | Passerelle / service     |
                | port promiscuous         |
                +------------+-------------+
                             |
              +--------------+--------------+
              |                             |
       +------+-------+              +------+-------+
       | Client A     |  pas de L2   | Client B     |
       | port isolé   |<------------>| port isolé   |
       +--------------+  direct      +--------------+
```

Ce modèle ne garantit pas l'isolation de tous les chemins possibles. Il faut vérifier le routage, les interfaces secondaires, les trunks, les autres VLAN et les points de sortie.

### 6.5 Exemple de politique par rôle (illustration logique)

```text
ROLE: USER-MANAGED
  permit DHCP vers relais/serveurs autorisés
  permit DNS vers résolveurs internes
  permit services métier explicitement approuvés
  deny accès administration des switches
  deny réseaux invités / IoT sauf besoin documenté
  deny reste, avec journalisation à seuil raisonnable

ROLE: PRINTER
  permit impression depuis les serveurs d'impression autorisés
  permit DNS/NTP nécessaires
  deny initiation vers postes utilisateurs
  deny accès administration réseau
  deny reste
```

C'est une spécification de politique, pas une syntaxe d'équipement. Avant de la traduire en ACL, précise les protocoles et ports, les sens de connexion, les réponses aux connexions établies, les adresses de service et le comportement IPv6. Évite les ACL fondées sur l'idée qu'un nom de service est toujours un seul port.

### 6.6 Exemple de segmentation par Security Group Tag

```text
  ATTRIBUTION DU ROLE                 POLITIQUE DE FLUX                   APPLICATION

  +----------------------+            Source -> destination               +------------------+
  | Poste géré           |            STAFF -> apps métier : AUTORISER -->|                  |
  | rôle : STAFF         |-----------> STAFF -> administration : REFUSER  | Point d'enforce- |
  +----------------------+                                                | ment compatible  |
                                                                          | (switch / routeur|
  +----------------------+            IOT-PRINT -> print server : LIMITER | / fabric)        |
  | Imprimante           |-----------> IOT-PRINT -> postes : REFUSER ---->|                  |
  | rôle : IOT-PRINT     |                                                +--------+---------+
  +----------------------+                                                         |
                                                                                   v
                                                                         Compteurs / journaux

  Exemple de matrice minimale :
  +-------------+--------------------+-------------------------------+
  | SOURCE      | DESTINATION        | DECISION                      |
  +-------------+--------------------+-------------------------------+
  | STAFF       | Apps métier        | Autoriser les ports requis    |
  | STAFF       | Admin équipements  | Refuser sauf rôle admin       |
  | IOT-PRINT   | Serveur d'impression| Autoriser flux strictement utiles|
  | IOT-PRINT   | Postes utilisateurs| Refuser                        |
  | INVITE      | Réseau interne     | Refuser ; Internet limité     |
  +-------------+--------------------+-------------------------------+

  Les tags de groupe (ex. SGT) sont propres à une solution compatible ;
  vérifier leur attribution, leur propagation et chaque point d'enforcement.
```

Cette approche est utile lorsqu'un système comme Cisco TrustSec ou une solution équivalente prend en charge les tags et leur enforcement. Ne présente pas un SGT comme une propriété universelle d'Ethernet : c'est une fonction de solution qui nécessite support de bout en bout et vérification des points où la politique est effectivement appliquée.


## 7. Chaîne de validation IPv4 : DHCP Snooping, DAI et IPSG

### 7.1 Les trois fonctions ne font pas la même chose

- **DHCP Snooping** inspecte les échanges DHCP et peut construire une table de bindings ; il distingue les interfaces trusted et untrusted pour les messages concernés.
- **Dynamic ARP Inspection (DAI)** inspecte les messages ARP et peut les comparer aux bindings disponibles ou à une politique d'exceptions.
- **IP Source Guard (IPSG)** filtre le trafic IP entrant sur un port selon les associations source IP/MAC/VLAN/port disponibles. Lorsqu'il est activé sans binding utilisable, du trafic légitime peut être bloqué.

### 7.2 Le flux logique des dépendances

```text
                  CHEMIN DHCP LEGITIME
  Client             Switch d'accès                         Serveur / relais DHCP
    |                       |                                        |
    |--- DHCP Discover ---->|                                        |
    |                       |--- DHCP Discover (uplink trusted) ---->|
    |                       |<-- DHCP Offer (uplink trusted) ---------|
    |<-- DHCP Offer --------|                                        |
    |--- Request ---------->|                                        |
    |                       |--- DHCP Request ----------------------->|
    |                       |<-- DHCP ACK -----------------------------|
    |<-- DHCP ACK ----------|                                        |
    |                       |                                        |
    |                  DHCP Snooping apprend un binding               |
    |             (IP, MAC, VLAN, port, durée/état selon plateforme)   |
    |                       |                                        |
    +-----------------------+----------------------------------------+
                            |
             +--------------+------------------+
             |                                 |
             v                                 v
  +------------------------+       +-------------------------+
  | DAI                    |       | IP Source Guard          |
  | vérifie les messages   |       | contrôle l'IP source     |
  | ARP selon bindings et  |       | sur le port d'entrée     |
  | éventuelles exceptions |       | selon bindings/politique |
  +-----------+------------+       +------------+------------+
              |                                 |
       ARP conforme ?                    Source IP conforme ?
         oui / non                          oui / non

  DHCP SNOOPING / DAI : ports clients généralement untrusted.
  TRUSTED             : uniquement là où la fonction et le chemin le justifient.
  IPSG                : applique sa propre politique d'entrée selon les bindings.

  Attention : un hôte à IP statique, un relais DHCP, un redémarrage ou
  une table de bindings absente peut nécessiter une procédure spécifique.
  Trusted pour DHCP Snooping ne signifie pas « fiable pour tout le réseau ».
```

### 7.3 L'erreur critique : marquer trop de ports « trusted »

Un port trusted signifie une exception à une fonction de contrôle précise, pas une confiance générale dans l'équipement. Dans DHCP Snooping, un uplink vers le serveur ou le relais DHCP légitime peut être trusted ; un port utilisateur ne devrait pas l'être. Si un port d'accès est marqué trusted par erreur, un serveur DHCP malveillant branché directement peut contourner le contrôle attendu sur cette fonction.

Pour chaque VLAN et chaque interface :

1. identifier les chemins DHCP légitimes ;
2. distinguer les ports de serveurs/relais, les trunks et les ports d'hôtes ;
3. confirmer la politique sur les deux côtés de chaque chemin ;
4. simuler en laboratoire un échange DHCP normal et un message provenant d'une interface non autorisée ;
5. examiner les compteurs, les bindings et les journaux ;
6. vérifier l'effet après rechargement ou bascule de l'équipement.

### 7.4 DHCP Snooping et persistance des bindings

Une table de bindings doit survivre aux événements que ton architecture considère normaux : renouvellement DHCP, redémarrage du switch, bascule de stack, restauration de configuration ou remplacement du serveur. Les fonctionnalités de persistance et leurs chemins de stockage varient selon plateforme. Si la table est perdue alors qu'IPSG/DAI s'appuient sur elle, des hôtes correctement configurés peuvent se retrouver bloqués.

Plan de validation :

- observer un bail DHCP obtenu correctement ;
- enregistrer l'entrée IP/MAC/VLAN/port et son âge ;
- redémarrer en laboratoire selon le scénario prévu ;
- vérifier que la table est reconstruite ou restaurée comme attendu ;
- tester les hôtes statiques via une méthode documentée ;
- comparer les compteurs avant et après ;
- tester les relais DHCP et les VLAN sur les trunks.

### 7.5 DAI et les hôtes statiques

DAI qui s'appuie uniquement sur une table DHCP n'a pas nécessairement la preuve suffisante pour un équipement configuré statiquement. Les exceptions statiques et les listes d'accès ARP doivent être restreintes à une source de confiance, documentées et revues après remplacement du matériel. Une exception trop large peut annuler le contrôle qu'elle devait compléter.

Ne confonds pas :

- **un ARP légitime mais non appris** : risque de faux positif à diagnostiquer ;
- **un ARP incohérent avec le binding** : possible erreur de configuration ou usurpation ;
- **un ARP autorisé par une exception large** : la règle peut être trop permissive.

### 7.6 Activation progressive de IP Source Guard

Sur une interface où IPSG est activé, le comportement peut être un refus du trafic IP source qui n'a pas de binding exploitable, avec des exceptions DHCP spécifiques. Sur certains équipements, l'option de vérification MAC/IP change le type de filtre programmé. La documentation du modèle doit donc être lue avant de combiner IPSG avec un port-channel, PVLAN, une IP statique ou d'autres politiques.

Procédure saine :

1. collecter les hôtes et leurs modes d'adressage ;
2. activer DHCP Snooping en premier et valider les bindings ;
3. activer DAI sur un VLAN pilote, avec plan pour hôtes statiques ;
4. valider le trafic ARP et les compteurs ;
5. activer IPSG sur un petit lot de ports simples ;
6. tester DHCP, DNS, passerelle, applications et renouvellement de bail ;
7. élargir uniquement si les preuves sont satisfaisantes.

### 7.7 Diagnostic d'un blocage L2/L3

Ne suppose pas qu'un problème de connectivité est forcément une ACL. Examine, dans l'ordre du chemin réel : état de port et session NAC, VLAN, DHCP et binding, ARP, table MAC, STP, ACL/SGACL, routage puis service final. Cette séquence varie si le poste utilise une IP statique ou si le flux reste dans le même VLAN : adapte-la au symptôme.

Commandes de diagnostic à adapter :

```text
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection
show ip arp inspection statistics
show ip verify source
show mac address-table dynamic interface <interface>
show interfaces <interface> counters errors
show logging | include DHCP|SNOOP|ARP|IPSG
```

Les commandes exactes et les compteurs disponibles varient. Capture si nécessaire les trames DHCP/ARP sur un port miroir isolé et vérifie les horodatages avant de conclure.


## 8. Sécurité IPv6 et gestion des bindings

### 8.1 L2 doit inclure IPv6 même si l'entreprise « n'utilise pas IPv6 »

Un poste peut posséder une adresse IPv6 link-local même si aucun plan d'adressage global n'a été conçu. Les mécanismes de découverte de voisin, les Router Advertisements (RA) et DHCPv6 peuvent donc influencer des terminaux. Une ACL IPv4 ou un contrôle DHCPv4 ne protège pas automatiquement IPv6.

### 8.2 First Hop Security : fonctions à relier au design

| Fonction | Objectif | Dépendance / point de vigilance |
|---|---|---|
| RA Guard | Bloquer les annonces de routeur non autorisées sur les ports d'hôtes | Doit bien analyser les en-têtes IPv6 ; les implémentations vulnérables aux extensions peuvent être contournées |
| DHCPv6 Guard | Limiter les messages serveur/réponse DHCPv6 aux chemins légitimes | Identifier les serveurs et relais, vérifier les messages et l'attachement de politique |
| IPv6 Source Guard / Prefix Guard | Empêcher des sources ou préfixes incohérents avec les bindings | Nécessite une table fiable et une stratégie pour les adresses statiques/prefix delegation |
| ND inspection / SISF / device tracking | Construire et valider des informations sur les voisins IPv6 | Les anciens mécanismes peuvent être dépréciés sur certaines plateformes ; vérifier la fonction recommandée pour la version utilisée |
| ACL IPv6 | Restreindre les communications IP routées | Autoriser explicitement les protocoles ICMPv6 requis ; ne pas transposer une politique IPv4 incomplète |

### 8.3 Le risque des en-têtes d'extension IPv6

Une implémentation RA Guard qui ne reconnaît pas correctement la chaîne d'en-têtes IPv6 peut manquer des Router Advertisements malformés ou spécialement construits. La RFC 7113 décrit les risques de contournement par en-têtes d'extension et donne des recommandations d'implémentation. En expert, la question n'est pas seulement « RA Guard est-il activé ? », mais : « l'implémentation de cette version traite-t-elle correctement les cas limites pertinents et les fragments ? »

### 8.4 Méthode de validation IPv6

- recenser les RA légitimes et les ports d'où ils proviennent ;
- confirmer que les hôtes obtiennent le préfixe, la passerelle et le DNS attendus ;
- vérifier DHCPv6 si le réseau l'utilise ;
- examiner la table device-tracking/bindings IPv6 ;
- tester un message interdit exclusivement dans un laboratoire ;
- vérifier compteurs, journaux, compatibilité RA Guard et comportements de fragmentation ;
- prouver qu'IPv4 et IPv6 appliquent une politique cohérente d'accès invité et de gestion.

### 8.5 Exemple de logique de ports de confiance

```text
Port relié à un routeur IPv6 légitime : autoriser les RA attendus selon la politique
Port relié à un poste : bloquer les RA non autorisés
Port d'accès IoT : limiter DHCPv6 / ND selon les capacités de l'équipement
Trunk inter-switch : appliquer la politique réseau adaptée, sans le traiter comme un port terminal
```

Cette logique décrit le rôle, pas la syntaxe. Ne mets pas tous les trunks en mode trusted sans analyser où les RA sont censés être émis et comment la protection est appliquée à travers la topologie.


## 9. STP à l'échelle : root design, guards et liens unidirectionnels

### 9.1 La racine STP est un choix d'architecture

Le root bridge doit se situer à un endroit prévu du réseau, généralement sur la couche de distribution ou dans le domaine défini par l'architecture. Le choix dépend du design L2 et des chemins de redondance. Fixe explicitement la priorité du root attendu, documente le root secondaire et vérifie le résultat opérationnel pour chaque VLAN ou instance MST pertinente.

Le principe d'exemple suivant montre un root planifié, pas une promesse sur une topologie universelle :

```text
                 DIST-1 (root prévu pour instances A/C)
                   /                         \
                  /                           \
             ACC-1 ------------------------- ACC-2
                |                              |
             terminaux                      terminaux

DIST-2 : root secondaire prévu, chemin redondant documenté.
```

### 9.2 Choisir les protections selon le rôle du port

| Mécanisme | Usage typique | Erreur fréquente |
|---|---|---|
| PortFast / edge | Port relié à un terminal final | L'activer sans vérifier si un switch/bridge peut être connecté |
| BPDU Guard | Fermer/mettre en erreur un edge qui reçoit une BPDU inattendue | L'appliquer à un uplink inter-switch légitime |
| Root Guard | Empêcher qu'un port désigné accepte une nouvelle racine supérieure non attendue | L'utiliser là où le port doit parfois devenir root port |
| Loop Guard | Prévenir un port root/alternate qui deviendrait designated à cause d'une perte unidirectionnelle de BPDUs | Le combiner avec Root Guard sur la même interface si la plateforme ne permet pas les deux |
| Bridge Assurance | Sur les liens réseau compatibles, détecter l'absence de BPDUs attendues selon la fonction | Supposer que toutes les plateformes et tous les liens la prennent en charge |
| UDLD | Détecter certains liens optiques unidirectionnels | Croire qu'UDLD remplace STP ou qu'il est disponible sur tout type de lien |
| Storm Control | Limiter les effets d'un volume excessif de certaines trames | Choisir un seuil arbitraire ou traiter la limite comme une correction de topologie |

### 9.3 Comparer Root Guard et Loop Guard

Les deux fonctions ne sont pas interchangeables. Root Guard concerne un port où tu ne veux pas qu'une meilleure BPDU transforme la topologie en choisissant une nouvelle racine via ce chemin. Loop Guard protège certains ports root/alternate contre une absence de BPDUs qui pourrait les conduire à devenir designated alors qu'une boucle demeure possible. Les restrictions de compatibilité et le comportement exact doivent être vérifiés pour le mode STP et la version.

### 9.4 Le danger du « root bridge surprise »

Une BPDU supérieure reçue à un mauvais endroit peut modifier le root, les chemins actifs, les rôles et les ports bloqués. Le résultat peut être un chemin sous-optimal, une boucle ou une interruption. La réponse ne doit pas commencer par désactiver STP ou retirer tous les guards.

Runbook initial :

1. relever le root ID, le root port, les changements STP récents et les interfaces ayant reçu des BPDUs ;
2. comparer l'état actuel aux racines prévues ;
3. corréler les horaires aux branchements, aux modifications et à la perte de liens ;
4. identifier l'interface où la BPDU inattendue est entrée ;
5. appliquer la mesure la plus ciblée selon la topologie ;
6. vérifier la convergence, les tables MAC, les pertes de paquets et les journaux ;
7. enregistrer la cause racine et le test qui empêche la récidive.

### 9.5 Diagramme : edge, root guard et loop guard

```text
                       DIST-1 (ROOT BRIDGE prévu)
                       priorité STP planifiée
                         /                 \
                lien réseau             lien réseau
                (Root Port côté         (Root Port côté
                 switch d'accès)         switch d'accès)
                     /                     \
              +-------------+           +-------------+
              |    ACC-1    |-----------|    ACC-2    |
              | switch accès| lien inter-switch / chemin redondant
              +------+------+           +------+------+
                     |                         |
            ports terminaux              ports terminaux
             PC / téléphone                PC / AP / IoT
                     |                         |
             EDGE + BPDU Guard         EDGE + BPDU Guard

  PROTECTIONS PAR ROLE DE PORT
  +----------------------+--------------------------------------------+
  | Port terminal / edge | PortFast/edge + BPDU Guard selon plateforme |
  | Vers switch attendu  | Root Guard / Loop Guard selon design       |
  | Lien fibre critique | UDLD si supporté et adapté                  |
  | Port-channel         | LACP, membres cohérents, vérification STP   |
  +----------------------+--------------------------------------------+

  Le dessin illustre l'intention, pas les rôles garantis de chaque lien.
  Le rôle réel dépend de l'instance/VLAN, des coûts, priorités et états.
  Vérifier root, root ports, designated ports, alternate/blocked ports
  et ports inconsistent après chaque modification.
```

### 9.6 Triage d'un changement STP

Commandes typiques selon plateforme :

```text
show spanning-tree summary
show spanning-tree root
show spanning-tree detail
show spanning-tree inconsistentports
show logging | include SPANTREE|LOOPGUARD|UDLD|LINK
show interfaces status
```

Compare les informations à l'état attendu. Sur un réseau à nombreuses instances, échantillonne les instances et interfaces pertinentes ; ne confonds pas une sortie tronquée avec une absence d'événement.

### 9.7 Storm Control et réponse à une tempête

Storm Control peut limiter certaines catégories de trafic au-dessus d'un seuil. Les seuils doivent partir d'une mesure du trafic normal, d'une période représentative et du rôle du port. Un seuil trop bas peut bloquer de l'ARP, du multicast ou d'autres protocoles nécessaires ; un seuil trop élevé peut laisser l'impact se produire. En cas de tempête, identifier la boucle ou la source reste prioritaire.


## 10. EtherChannel, découverte de voisinage et contrôle du plan L2

### 10.1 LACP et cohérence de Port-channel

Un port-channel ne rend pas automatiquement les liens sûrs. Les membres doivent avoir une configuration compatible, la méthode de négociation doit être choisie explicitement, et la topologie STP doit être comprise comme un port logique. Un membre mal configuré peut être suspendu, mis en état individuel ou conduire à des résultats surprenants selon la plateforme.

Audit :

- protocole LACP/PAgP/statique documenté et support partagé ;
- VLAN autorisés et VLAN natif cohérents sur les deux extrémités ;
- vitesse, duplex et MTU compatibles ;
- fonctions de sécurité appliquées au Port-channel ou au membre selon les recommandations de la plateforme ;
- état de chaque membre, nombre de liens actifs et journaux de changement ;
- câbles répartis selon l'architecture et les domaines de panne réellement prévus.

Commandes indicatives :

```text
show etherchannel summary
show lacp neighbor
show interfaces port-channel <id>
show interfaces <member> counters errors
show spanning-tree interface port-channel <id> detail
```

### 10.2 CDP, LLDP et exposition d'informations

Les protocoles de découverte de voisins simplifient l'exploitation, mais peuvent révéler modèle, version, nom, VLAN voix, capacités et topologie. Ce n'est pas un contrôle d'accès et un message de découverte ne doit pas être considéré comme une preuve d'identité. Active-les uniquement où ils ont une utilité opérationnelle ; protège les ports terminaux où cette information n'est pas nécessaire, et maintiens le protocole de découverte sur les liens qui doivent être supervisés.

### 10.3 UDLD et erreurs physiques

Les erreurs physiques, les optiques incompatibles et les pannes unidirectionnelles peuvent provoquer des effets L2 complexes. UDLD peut détecter certains cas sur les supports et plateformes compatibles, mais ne remplace ni la supervision optique ni STP. Compare les compteurs CRC, les transitions de lien, les erreurs FEC/optique si disponibles et les événements UDLD avant de conclure que le problème est purement logique.

### 10.4 Protection des protocoles de contrôle

Les protections de plan de contrôle doivent limiter l'accès aux interfaces, aux protocoles de gestion et aux services qui peuvent influencer l'état du réseau. Ne filtre pas arbitrairement toutes les trames de contrôle : STP, LACP, LLDP/CDP, EAPOL et les protocoles de routage ou de supervision peuvent être requis selon le rôle du port. L'objectif est une politique par rôle et une documentation des protocoles attendus.


## 11. MACsec : protéger les liens Ethernet

### 11.1 Ce que MACsec protège

MACsec (IEEE 802.1AE) fournit des services de sécurité au niveau Ethernet sur un lien où les deux extrémités et le matériel prennent en charge le mécanisme. Selon la configuration, il peut fournir intégrité, authenticité d'origine et confidentialité des trames protégées. MKA (MACsec Key Agreement) est couramment utilisé pour gérer les associations et les clés dans des déploiements compatibles.

MACsec protège le segment où il est actif ; il ne chiffre pas automatiquement le trafic de bout en bout au-delà de ce lien. Pour un chemin avec plusieurs segments, chaque lien et chaque point de terminaison doivent être analysés. Les données peuvent ressortir déchiffrées du lien si le prochain segment n'est pas lui aussi protégé.

### 11.2 Plan de contrôle et plan de données

```text
                 PLAN DE CONTROLE : MKA / gestion des clés

       +----------------------+                       +----------------------+
       | SWITCH A             |<---- échanges MKA ---->| SWITCH B             |
       | port MACsec          |                       | port MACsec          |
       +----------+-----------+                       +-----------+----------+
                  |                                               |
                  +------------- CA / clés / SAK -----------------+
                                négociation
                                    |
                                    v
                       Association de sécurité active
                                    |
                                    v
                 PLAN DE DONNEES : trames Ethernet protégées

       +----------------------+  ===== lien MACsec =====  +----------------------+
       | SWITCH A             |  chiffrement / intégrité  | SWITCH B             |
       | émission protégée    |  contrôle anti-rejeu      | vérification / remise|
       +----------------------+                           +----------------------+

       Trafic avant le lien       SUR LE LIEN             Trafic après le lien
       en clair selon source  =>  protégé MACsec      =>  déchiffré à l'extrémité

  MACsec protège uniquement les segments où il est établi et opérationnel.
  Vérifier l'état de la session, la suite cryptographique, les compteurs,
  les erreurs MKA, le renouvellement des clés et les segments non protégés.
```

### 11.3 Concepts importants

- **CAK/CKN** : paramètres de clé et d'identification utilisés selon le mode de gestion ; leur protection, leur distribution et leur renouvellement sont essentiels.
- **MKA** : protocole de gestion des associations de clés, notamment dans les déploiements fondés sur des mécanismes d'authentification compatibles.
- **SAK** : clé d'association de sécurité qui protège le trafic de données dans le cadre MACsec.
- **Cipher suite et packet numbering** : doivent être choisis selon les capacités des deux extrémités, le débit et les recommandations applicables.
- **Confidentiality offset** : paramètre qui peut laisser une portion du payload non chiffrée selon le profil ; justifier sa valeur et ne pas supposer que toutes les octets sont cryptés si le profil ne le garantit pas.

Ne confonds pas un lien qui a une politique MACsec configurée avec une session qui a effectivement établi et utilise une association de sécurité. Vérifie l'état opérationnel, la suite choisie, les compteurs de paquets protégés et les erreurs MKA.

### 11.4 Où l'activer ?

Cas possibles : liens switch-à-switch dans des locaux partagés, segments de distribution exposés, interconnexion de bâtiments ou environnements soumis à des exigences de confidentialité. La décision dépend de la compatibilité matérielle, du débit, des exigences de disponibilité, des modes de gestion de clés et des contraintes d'interopérabilité.

Il n'est pas toujours pertinent de chiffrer tous les ports d'accès sans analyse : l'extrémité doit être capable de participer, la gestion de clés doit être maîtrisée et le comportement en cas d'échec doit être défini.

### 11.5 Checklist de validation MACsec

- les deux extrémités supportent le mode et les suites compatibles ;
- la configuration de gestion de clés est cohérente et protégée ;
- le canal d'authentification et les échanges MKA sont observables ;
- la session est réellement établie sur le lien prévu ;
- les compteurs chiffrés et les compteurs d'erreur évoluent de manière cohérente ;
- le comportement lors de rekey, redémarrage, perte de voisin ou modification de politique a été testé ;
- la sécurité de la gestion hors du lien MACsec est traitée séparément ;
- la documentation indique quels segments sont chiffrés et quels segments ne le sont pas.

### 11.6 Exemple illustratif de configuration

Le détail de la configuration MACsec est particulièrement dépendant du modèle et du mode de clés. Le bloc suivant montre uniquement la forme d'une politique dans un guide IOS XE compatible ; ce n'est pas une recette complète à copier :

```text
! EXEMPLE INDICATIF UNIQUEMENT — vérifier la commande et les prérequis du modèle
mka policy <nom-politique>
 ! définir les paramètres et suite compatibles selon le guide de version
!
interface <interface-compatible>
 macsec network-link
```

Avant d'utiliser une suite, une méthode de clé ou une commande, lis le guide MACsec correspondant à la version logicielle et aux deux matériels. Effectue d'abord la mise en service dans un laboratoire : une incompatibilité peut interrompre le lien ou laisser croire qu'un trafic est protégé alors qu'il ne l'est pas.


## 12. Plan d'administration et durcissement des équipements

### 12.1 Séparer les plans utilisateur et gestion

Le réseau de gestion ne doit pas devenir accessible simplement parce qu'un terminal est dans un VLAN d'entreprise. Le plan d'administration peut être un VRF, un réseau hors bande ou un segment dédié selon l'architecture. Restreins les sources d'administration, impose l'authentification centralisée lorsqu'elle est disponible, limite les privilèges, surveille les accès et prévois un accès d'urgence contrôlé.

### 12.2 SSH, AAA et principe du moindre privilège

- privilégier SSH à l'administration distante non chiffrée ;
- limiter les sources avec ACL et/ou VRF de gestion ;
- supprimer les comptes par défaut et les comptes inutilisés ;
- employer des comptes nominatifs ou des rôles, pas un secret partagé par toute l'équipe ;
- utiliser une authentification multifacteur sur la plateforme d'accès/bastion lorsqu'elle est disponible ;
- définir les droits par rôle et auditer les changements de privilège ;
- protéger les secrets de RADIUS, SNMP, API et automation ;
- ne pas mettre de mots de passe ou de clés en clair dans un dépôt Git ou un fichier de laboratoire partagé.

### 12.3 SNMP, NTP, Syslog et API

| Service | Bonnes pratiques | Risques à gérer |
|---|---|---|
| SNMP | SNMPv3 avec authentification/confidentialité compatibles ; vues limitées | communautés v1/v2c, accès trop large, exposition des informations |
| NTP | Sources de temps approuvées et surveillées | horloges incohérentes compliquant certificats et corrélation d'incidents |
| Syslog | Serveur central, transport protégé si supporté, rétention adaptée | log local écrasé, absence d'heure ou de contexte d'interface |
| API / NETCONF / RESTCONF | HTTPS/SSH, ACL, rôles, secrets de courte durée lorsqu'ils sont supportés | token dans le code, API exposée au VLAN utilisateur, privilèges excessifs |
| Console / accès hors bande | Accès physique contrôlé et journalisé | chemin de contournement de toutes les restrictions réseau |

### 12.4 Réduire la surface d'attaque

- désactiver les services et protocoles non nécessaires après vérification de leurs dépendances ;
- vérifier les versions de logiciel, avis de sécurité et recommandations de durcissement du fournisseur ;
- séparer les comptes opérateur, automation et lecture seule ;
- limiter les tentatives de gestion et alerter sur les échecs répétés ;
- conserver une configuration de secours accessible sans exposer le service de gestion au réseau utilisateur ;
- protéger l'image logicielle, les sauvegardes et les identifiants de déploiement.

### 12.5 Plan de gestion versus plan de contrôle

Le **plan de gestion** sert à administrer l'équipement : SSH, API, SNMP, console. Le **plan de contrôle** exécute STP, LACP, protocoles de voisinage, authentification et autres fonctions qui gouvernent le réseau. Les deux doivent être protégés, mais les mesures ne sont pas identiques : une ACL de gestion ne corrige pas une mauvaise topologie STP, et une protection STP n'empêche pas la compromission d'un compte SSH.


## 13. Télémétrie, journaux, preuves et détection de dérive

### 13.1 Transformer les protections en signaux opérables

Un mécanisme qui rejette une trame sans fournir de preuve peut être difficile à dépanner. Un mécanisme qui enregistre chaque paquet peut au contraire produire trop de bruit. Il faut donc choisir les événements utiles, les seuils, les destinations et la durée de conservation.

| Signal | Données minimales | Usage |
|---|---|---|
| Échec 802.1X/MAB | équipement, port, MAC, méthode, motif, heure, serveur AAA | distinguer échec de supplicant, certificat, politique et reachability |
| Changement de VLAN/role | session, valeur précédente, nouvelle valeur, source de décision | détecter une politique inattendue ou un CoA mal ciblé |
| Violation DHCP/DAI/IPSG | interface, VLAN, MAC/IP, compteur, type de rejet | isoler une source illégitime ou une table de bindings incomplète |
| Changement STP | root ID, rôle de port, instance, TCN, interface | retrouver une BPDU, une boucle ou un changement de câblage |
| Flap de MAC | MAC, anciens/nouveaux ports, VLAN, intervalle | distinguer déplacement légitime, boucle et conflit |
| Événement MACsec | session, pair, suite, clé/association (sans secrets), compteurs | établir si le lien est réellement protégé |
| Modification de configuration | utilisateur, méthode, diff, ticket, horodatage | audit et détection de dérive |

Ne journalise pas les secrets, les clés privées, les secrets RADIUS ou les données personnelles inutiles. Les journaux doivent aider à reconstruire un événement sans exposer des identifiants sensibles.

### 13.2 Sources de preuve à corréler

```text
Terminal / EDR ou client 802.1X
          |
          +---- capture côté terminal ou port miroir
          |
Switch d'accès : session, interface, VLAN, compteurs et logs
          |
Serveur AAA / PKI : décision, certificat, règle et motif
          |
Distribution / pare-feu : route, ACL, compteurs et logs
          |
Syslog / NTP / supervision centrale : corrélation et timeline
```

Les horodatages doivent être synchronisés et leur fuseau documenté. Sans heure cohérente, des événements parfaitement exacts peuvent être ordonnés à tort.

### 13.3 Seuils et faux positifs

Définis un comportement de référence pour les VLANs et les rôles de ports. Un nombre brut de violations n'est pas suffisant : 100 événements sur un seul port peuvent signaler un hôte défectueux, tandis qu'un unique changement du root STP peut affecter tout le domaine. Le seuil doit tenir compte du rayon d'impact et du caractère attendu de l'événement.

Pour chaque alerte, définis :

- gravité et responsable ;
- contexte à joindre automatiquement ;
- action initiale sans risque (par exemple collecter l'état, pas éteindre tous les ports) ;
- délai de prise en charge ;
- condition de clôture ;
- mécanisme de retour d'expérience.

### 13.4 Baseline et drift

Une base de référence inclut plus que `show running-config` : topologie, VLAN existants, trunks, root STP, sessions d'authentification, bindings, modules, version, politiques AAA, horloge et compteurs significatifs. La comparaison doit distinguer le changement autorisé, la dérive de configuration, les variations normales d'état et un éventuel défaut de supervision.


## 14. Automatisation défensive et contrôle de conformité

### 14.1 Automatiser d'abord la lecture et la preuve

Le premier usage de l'automatisation devrait être la collecte et la comparaison, pas l'application en masse d'une configuration. Une automatisation qui active une fonction incompatible sur cent ports peut amplifier une erreur de design très rapidement.

Progression conseillée :

1. **Read-only** : collecter versions, interfaces, VLAN, trunks, STP, sessions et bindings.
2. **Audit** : comparer avec un référentiel de profils et lister les écarts.
3. **Simulation** : afficher le diff attendu sans changer les équipements.
4. **Pilote** : appliquer un changement à une interface de maquette ou un équipement de test.
5. **Canary** : appliquer à un groupe limité, observer, puis élargir selon les critères.
6. **Rollback** : restaurer l'état connu si les tests de santé échouent.

### 14.2 Exemple de règles de conformité

Ce tableau peut être converti en script, playbook Ansible, pipeline CI ou outil de configuration. Les règles doivent être paramétrées par rôle ; un contrôle global ne doit pas imposer une configuration access aux uplinks.

| Règle | Condition attendue | Exception acceptable |
|---|---|---|
| Uplink documenté | Port-channel/trunk présent dans l'inventaire et VLAN autorisés explicitement listés | aucun trunk dynamique inconnu sans ticket |
| Port utilisateur | Mode access, VLAN et profil NAC attendus | exception temporaire avec propriétaire |
| Port inutilisé | Désactivé et étiqueté `UNUSED` | port réservé, avec date de revue |
| STP edge | Edge + BPDU Guard sur les ports de terminal compatibles | appareil nécessitant un bridge selon design, validé séparément |
| Root STP | Identifiant et priorité conforme aux instances attendues | changement planifié en cours de maintenance |
| DHCP Snooping | VLANs couverts et interfaces trusted identifiées | serveur/relais documenté et testé |
| IPv6 | RA/DHCPv6 couverts si IPv6 existe sur le segment | désactivation IPv6 décidée et vérifiée de bout en bout, pas supposée |
| Gestion | SSH/AAA/SNMPv3 selon le standard ; accès limité | compte de secours scellé et audité |
| Version | version autorisée par la politique de parc | exception de compatibilité suivie avec échéance |

### 14.3 Pseudo-code d'audit non destructif

Le script suivant illustre un contrôle local sur des données normalisées ; il ne se connecte pas aux switches, n'applique aucune commande et doit être adapté à la structure réelle de l'inventaire.

```python
from dataclasses import dataclass
from typing import Iterable

@dataclass
class Port:
    name: str
    role: str
    admin_up: bool
    mode: str
    allowed_vlans: set[int]
    bpdu_guard: bool
    description: str


def audit_ports(ports: Iterable[Port]) -> list[str]:
    """Produit des écarts à examiner ; ne modifie aucun équipement."""
    findings: list[str] = []

    for port in ports:
        if port.role == "UNUSED":
            if port.admin_up:
                findings.append(f"{port.name}: port UNUSED encore actif")
            if "UNUSED" not in port.description.upper():
                findings.append(f"{port.name}: description d'interface à corriger")

        elif port.role in {"USER-8021X", "IOT-MAB"}:
            if port.mode.lower() != "access":
                findings.append(f"{port.name}: rôle terminal mais mode={port.mode}")
            if not port.bpdu_guard:
                findings.append(f"{port.name}: BPDU Guard à vérifier")

        elif port.role == "SWITCH-UPLINK":
            if port.mode.lower() != "trunk":
                findings.append(f"{port.name}: uplink sans mode trunk explicite")
            if not port.allowed_vlans:
                findings.append(f"{port.name}: liste VLAN vide/indéterminée à examiner")

    return findings
```

Les contrôles d'un vrai système doivent inclure les résultats opérationnels, les politiques héritées, les versions logicielles et les exceptions. Une valeur absente de la collecte est **inconnue**, pas automatiquement « conforme » ou « non conforme ».

### 14.4 Secrets et accès des pipelines

- ne stocke pas les identifiants dans le code ; utilise un gestionnaire de secrets ;
- sépare les credentials lecture seule des credentials de changement ;
- applique une restriction réseau au compte d'automatisation ;
- journalise l'utilisateur, le pipeline, le diff et le résultat ;
- exige une approbation pour les changements qui influencent STP, trunks, AAA ou MACsec ;
- teste la restauration sur une maquette compatible ;
- protège les dépôts et artefacts de configuration, qui peuvent révéler les noms, adresses et choix de sécurité du réseau.

### 14.5 CI pour configurations réseau

Avant qu'un changement soit appliqué :

1. vérifier syntaxe et modèles de configuration ;
2. exécuter les règles de conformité ;
3. produire un diff de configuration lisible ;
4. confirmer l'existence des VLAN, ports et adresses référencés ;
5. simuler les effets connus ou tester en lab ;
6. approuver le changement et archiver le résultat.

Le « pipeline vert » ne prouve pas à lui seul que le trafic fonctionne : il garantit seulement que les contrôles automatisés définis ont réussi. Les tests opérationnels restent obligatoires.


## 15. Segmentation virtualisée et limites du domaine L2

### 15.1 Pourquoi les environnements virtualisés changent les hypothèses

Un hyperviseur peut faire apparaître plusieurs MAC derrière une seule carte physique, porter plusieurs VLAN, réaliser du bridging local entre vNIC ou déplacer un workload sans changer le port physique. Les limites MAC d'un port, les politiques basées uniquement sur le port physique et l'observation des flux peuvent alors être insuffisantes ou produire des faux positifs.

Lors de l'intégration d'un hyperviseur :

- documenter les VLAN réellement présentés aux vSwitch/vDS ;
- limiter les VLAN autorisés sur le trunk physique au nécessaire ;
- comprendre les modes promiscuous, MAC changes et forged transmits propres à l'hyperviseur ;
- placer les politiques east-west au point où les flux se croisent réellement ;
- coordonner le réseau physique, le réseau virtuel et l'équipe plateforme ;
- surveiller les événements de mobilité et les changements de port-channel.

### 15.2 EVPN/VXLAN et segmentation du plan de données

Dans un réseau de datacenter à overlay, les segments virtuels peuvent être transportés au-dessus d'un underlay L3. La sécurité ne se résume alors pas à la liste des VLAN locaux : il faut examiner l'association tenant/segment, les points d'encapsulation et de décapsulation, les politiques appliquées aux workloads, ainsi que le comportement des fonctions de contrôle et de routage.

Ce cours ne prétend pas fournir une configuration universelle EVPN/VXLAN. Le design dépend du fournisseur, du control plane, de l'architecture multitenant et du placement des politiques. Utilise les principes suivants :

- maintenir un underlay prévisible et protégé ;
- limiter les VLAN/VNI et les routes importées/exportées au besoin ;
- définir les points de segmentation et d'application des politiques ;
- vérifier l'anti-spoofing et les mécanismes de mobilité des adresses ;
- surveiller les changements de MAC/IP et les associations route/VNI ;
- tester l'isolation inter-tenant et la couverture IPv6 ;
- ne pas compter sur un filtre d'accès L2 local pour protéger tous les chemins d'un overlay.

### 15.3 Contrôler les fuites de VLAN

Les causes possibles incluent un trunk trop permissif, une configuration native incohérente, un vSwitch qui transporte des VLAN non prévus, un bridge logiciel ou une mauvaise association tenant/VNI. Le diagnostic suit le chemin entier : port terminal → switch d'accès → trunk → distribution/underlay → overlay → port de sortie. Les captures sur un seul port ne suffisent pas si la fuite se produit au point d'encapsulation ou dans le plan virtuel.


## 16. Runbooks de réponse aux incidents

Chaque runbook suit quatre règles : stabiliser sans élargir l'impact, collecter les preuves avant de nettoyer, limiter le changement au point fautif et prouver le rétablissement. Les commandes ci-dessous sont indicatives et doivent être vérifiées sur l'équipement.

### 16.1 Incident A — DHCP frauduleux suspecté

**Symptômes possibles :** plusieurs clients reçoivent une passerelle ou un DNS inhabituel, les baux changent sans explication, les compteurs DHCP Snooping augmentent.

1. Identifier VLAN, clients affectés, bail, gateway/DNS, MAC source et horaire.
2. Vérifier la table DHCP Snooping et les interfaces trusted.
3. Examiner le port d'où proviennent les messages serveur non attendus ; ne pas conclure à partir de la seule MAC sans vérifier le voisinage.
4. Isoler le port suspect selon la procédure d'incident et le périmètre approuvé.
5. Renouveler les baux de laboratoire puis, si le changement est validé, des clients ciblés ; vérifier les nouveaux paramètres.
6. Corriger la classification de confiance et documenter la cause.

```text
show ip dhcp snooping
show ip dhcp snooping binding
show logging | include DHCP|SNOOP
show mac address-table address <mac>
```

### 16.2 Incident B — DAI bloque un appareil légitime

1. Identifier exactement la MAC, l'IP, le VLAN et l'interface affectée.
2. Vérifier si l'hôte utilise DHCP ou une IP statique.
3. Examiner les bindings, l'état DHCP relay et les compteurs DAI.
4. Vérifier que le port trusted n'est pas la solution rapide proposée par erreur.
5. Si l'hôte est statique, créer une exception minimale et documentée ou choisir une méthode de binding supportée.
6. Retester ARP, passerelle et service ; supprimer toute exception temporaire inutile.

### 16.3 Incident C — le root STP a changé

1. Capturer le root ID et les ports root/designated/alternate, par instance.
2. Comparer l'heure à un changement de câblage, switch, trunk ou configuration.
3. Identifier le port ayant reçu la BPDU supérieure si les outils le permettent.
4. Examiner les guards configurés selon le rôle de l'interface.
5. Stabiliser le domaine par la correction la plus ciblée, sans désactiver STP globalement.
6. Vérifier la convergence, les pertes, les tables MAC et les changements STP répétés.
7. Ajouter un test ou une règle de conformité pour prévenir la récurrence.

### 16.4 Incident D — flapping de MAC et tempête

1. Évaluer l'impact : saturation, perte de paquets, ports en erreur et MAC qui changent rapidement de port.
2. Trouver le VLAN, la MAC et les interfaces impliquées.
3. Vérifier les liens redondants, le Port-channel et l'état STP.
4. Inspecter les changements de câblage, bridges non autorisés ou mini-switches.
5. Isoler uniquement le segment à risque si cela peut être fait sans couper un chemin critique.
6. Après correction de la boucle, confirmer que le volume de trafic et les tables MAC reviennent à une valeur normale.

### 16.5 Incident E — échec 802.1X après renouvellement de certificats

1. Déterminer si le problème affecte un terminal, un modèle, un site ou tous les terminaux.
2. Vérifier date/heure, certificat client, chaîne, EKU, certificat serveur, noms et révocation.
3. Corréler un seul échange EAPOL/RADIUS sur le switch et le serveur AAA.
4. Vérifier que le switch atteint le serveur par la bonne interface source et que la politique attendue s'applique.
5. Définir une exception de secours seulement si nécessaire et avec accès restreint ; ne pas généraliser MAB à tous les ports.
6. Tester renouvellement automatique et retirer l'exception une fois la PKI corrigée.

### 16.6 Incident F — MACsec configuré mais session inactive

1. Confirmer le support des fonctions et le mode choisi aux deux extrémités.
2. Vérifier l'état de MKA, l'identité du pair, la configuration de clé et les événements de négociation.
3. Comparer la suite cryptographique, le mode d'authentification et les politiques appliquées.
4. Contrôler vitesse, interface, erreurs physiques et éventuelles limitations de plateforme.
5. N'effectuer un flap de lien qu'après validation du risque et selon le guide du constructeur ; certaines modifications peuvent nécessiter une réinitialisation de session.
6. Vérifier l'état réellement sécurisé et les compteurs de trames protégées.

### 16.7 Incident G — poste authentifié mais sans accès métier

Vérifie le plan de bout en bout :

- session d'accès et identité/attributs AAA ;
- VLAN ou rôle assigné et présence sur les trunks ;
- obtention d'une adresse, passerelle et DNS ;
- binding et protections d'adresses ;
- chemin vers la destination (L2 local ou routage L3) ;
- ACL/PACL/VACL/SGACL ou pare-feu réellement traversé ;
- service final, ports, TLS et journal du serveur.

La phrase « 802.1X est vert » prouve seulement une partie du parcours. Note la première étape qui échoue et vérifie son point de contrôle.

### 16.8 Après incident : préserver et apprendre

Enregistre les configurations avant/après, extraits de journaux, chronologie, commandes utilisées, interfaces et VLAN concernés, décisions de confinement, cause racine, preuves de rétablissement et action préventive. Évite d'archiver des secrets, certificats privés ou données utilisateurs inutiles. Une correction non traduite en standard, surveillance ou test risque de ne pas prévenir le même incident.


## 17. Laboratoires experts guidés

### Préparation commune

Matériel possible : trois switches virtuels ou physiques, un routeur/pare-feu, un serveur RADIUS, deux clients gérés, un appareil MAB simulé, un serveur DHCP de laboratoire, un outil de capture et un collecteur de journaux. Utilise une maquette isolée, les mêmes versions autant que possible et des identifiants sans valeur en production.

Pour chaque lab : écris le résultat attendu **avant** la modification, conserve les sorties de commandes et réalise au moins un test positif et un test négatif contrôlé.

### Lab 1 — Audit de ports et réduction des trunks

**Objectif :** produire un inventaire fiable et un standard de port.

**Étapes :**
1. relever interface, description, mode, VLAN, trunk, MAC apprises et voisin ;
2. classer les ports selon les rôles de la section 4 ;
3. trouver un trunk qui transporte plus de VLAN que nécessaire dans la maquette ;
4. limiter la liste de VLAN dans une fenêtre de test ;
5. vérifier les services autorisés, l'état STP et la cohérence des deux extrémités ;
6. comparer la configuration et l'état opérationnel au référentiel.

**Réussite :** chaque port a un rôle, les VLAN inutiles ne sont plus transportés, les services attendus continuent de fonctionner et la preuve est archivée.

**Rollback :** restaurer la liste originale et vérifier à nouveau les deux extrémités si un service de référence échoue.

### Lab 2 — 802.1X EAP-TLS et panne AAA

**Objectif :** distinguer l'authentification de l'autorisation et tester le comportement de continuité.

**Étapes :**
1. configurer un client de test avec un certificat valide ;
2. valider l'échange EAPOL/RADIUS et le rôle autorisé ;
3. provoquer un rejet de politique contrôlé ;
4. tester un certificat expiré ou non approuvé dans la maquette ;
5. rendre le serveur AAA indisponible selon la procédure de lab ;
6. vérifier le VLAN/role de secours et confirmer qu'il n'accorde pas d'accès général ;
7. restaurer le serveur et contrôler la réauthentification.

**Résultat attendu :** tu peux expliquer chaque refus à partir des preuves terminal/switch/AAA, et la panne du serveur ne transforme pas un accès restreint en accès privilégié.

### Lab 3 — MAB pour IoT sans supplicant

**Objectif :** mettre un appareil non compatible dans un segment limité.

**Étapes :**
1. identifier l'adresse MAC et l'enregistrer dans l'inventaire de test ;
2. créer une décision MAB vers un VLAN isolé ;
3. autoriser seulement DNS/NTP et le service nécessaire ;
4. tester les services autorisés et un service interdit ;
5. simuler un appareil à MAC différente puis une entrée MAB inconnue ;
6. confirmer les alertes, les raisons de refus et le processus de révision.

**Réussite :** MAB ne donne pas un accès identique à celui d'un poste EAP-TLS et chaque exception est explicable.

### Lab 4 — DHCP Snooping + DAI + IPSG avec retour arrière

**Objectif :** tester les dépendances de bindings sans couper tous les hôtes.

**Étapes :**
1. vérifier DHCP normal et enregistrer le binding d'un client ;
2. activer DHCP Snooping uniquement dans le VLAN pilote ;
3. confirmer l'apprentissage et la bonne classification des interfaces trusted ;
4. activer DAI et tester ARP normal ;
5. activer IPSG sur un seul port utilisateur connu ;
6. tester renouvellement de bail, changement de port et hôte statique prévu ;
7. redémarrer la maquette si le scénario de persistance fait partie de l'objectif ;
8. enregistrer les compteurs, puis revenir en arrière et vérifier la connectivité.

**Réussite :** les trames mal classées sont contrôlées, les hôtes autorisés continuent de fonctionner et les exceptions statiques ne sont pas globales.

### Lab 5 — STP : root inattendu et perte de BPDUs

**Objectif :** savoir interpréter les protections STP.

**Étapes :**
1. relever les root ID et rôles de ports attendus ;
2. vérifier BPDU Guard sur les ports terminaux ;
3. dans un environnement isolé, connecter un switch de lab comme « racine inattendue » ;
4. observer les compteurs/états et l'effet du guard approprié ;
5. simuler une anomalie de lien unidirectionnel uniquement si la maquette le permet en sécurité ;
6. vérifier Loop Guard/UDLD selon la plateforme ;
7. restaurer le câblage et prouver la convergence.

**Réussite :** tu sais expliquer pourquoi Root Guard et Loop Guard ne remplacent pas l'un l'autre, et tu ne désactives pas STP pour résoudre l'incident.

### Lab 6 — Politique de segmentation

**Objectif :** écrire une matrice avant de configurer les règles.

**Étapes :**
1. créer des rôles `USER`, `PRINTER` et `ADMIN` ;
2. documenter les flux indispensables avec protocole et port ;
3. identifier lesquels sont routés et lesquels restent dans le même VLAN ;
4. appliquer les règles au point de passage réel ;
5. tester un flux autorisé, un flux interdit inter-VLAN et un flux interdit intra-VLAN ;
6. répéter les contrôles IPv4/IPv6 si les deux sont actifs.

**Réussite :** la segmentation est démontrée pour les chemins pertinents et les résultats négatifs sont consignés.

### Lab 7 — MACsec et contrôle de l'état réel

**Objectif :** faire la différence entre configuration et session protégée.

**Étapes :**
1. confirmer le support et la méthode des deux extrémités ;
2. établir MACsec dans la maquette via le mode documenté ;
3. relever l'état MKA, la suite et les compteurs ;
4. générer un flux de test et vérifier que les compteurs de protection évoluent ;
5. modifier un paramètre uniquement dans la maquette afin d'observer un échec de négociation ;
6. rétablir la politique et vérifier l'état sécurisé ;
7. documenter quels autres segments restent hors du lien MACsec.

**Réussite :** la preuve mentionne l'état opérationnel et non uniquement la présence de lignes de configuration.

### Lab 8 — Contrôle de conformité read-only

**Objectif :** produire un rapport d'écarts sans changer le réseau.

**Étapes :**
1. créer un inventaire simple de ports et de rôles ;
2. collecter des sorties normalisées depuis la maquette ;
3. exécuter le pseudo-code ou son adaptation réelle ;
4. injecter volontairement un écart dans un port de lab ;
5. confirmer que le rapport détecte le bon port et explique la règle ;
6. corriger, relancer et archiver les résultats avant/après.

**Réussite :** l'audit signale les écarts et les inconnues, sans modifier automatiquement les équipements.

### Lab 9 — Exercice de réponse à incident intégré

**Scénario :** après remplacement d'un switch d'accès, certains postes n'obtiennent plus d'adresse, les imprimantes sont partiellement accessibles et un événement STP apparaît dans le même intervalle.

**Consignes :**
1. construire une chronologie ;
2. séparer les symptômes communs et les symptômes par type d'équipement ;
3. vérifier la compatibilité de version, les VLAN et trunks ;
4. examiner la persistance des bindings, l'état AAA et les changements STP ;
5. formuler au moins deux hypothèses et indiquer quelle preuve les départage ;
6. appliquer une correction limitée ;
7. exécuter les tests fonctionnels et négatifs ;
8. rédiger le rapport d'incident et une mesure préventive automatisable.

**Barème :** 25 % qualité de la chronologie, 25 % vérification des hypothèses, 20 % minimisation du rayon d'impact, 20 % preuves de rétablissement, 10 % documentation.


## 18. Projet de synthèse : campus d'entreprise durci

### 18.1 Contexte

Tu dois préparer le design de sécurité d'un petit campus comprenant une distribution redondante, trois switches d'accès, des postes gérés, téléphones IP, imprimantes, IoT, un Wi-Fi entreprise, un réseau invité, des serveurs internes et un réseau d'administration.

Le projet n'est pas une suite de commandes à coller ; il doit produire des décisions techniques justifiées, testables et réversibles.

### 18.2 Livrables obligatoires

1. **Topologie** physique et logique avec rôles d'équipement, trunks et Port-channels.
2. **Plan de VLAN/adressage** IPv4/IPv6, passerelles, DNS/DHCP et périmètre de chaque segment.
3. **Standard de ports** incluant utilisateur EAP-TLS, téléphone + PC, IoT MAB, AP, serveur/hyperviseur, uplink et parking.
4. **Politique d'identité** : méthode primaire, MAB, attributs d'autorisation, modes d'hôte et comportement AAA indisponible.
5. **Politique de bindings** : VLAN surveillés par DHCP Snooping/DAI/IPSG, traitement des hôtes statiques et persistance.
6. **Design STP** : mode, root primaire/secondaire, edge, BPDU Guard et guards réseau justifiés.
7. **Segmentation** : matrice de flux avec contrôle placé sur le bon chemin (intra-VLAN et routé).
8. **Gestion et télémétrie** : SSH/AAA, SNMPv3, NTP, Syslog, accès hors bande, alertes et rétention.
9. **MACsec** : décision de déploiement ou de non-déploiement justifiée, segments concernés et preuve opérationnelle requise.
10. **Tests d'acceptation** positifs et négatifs, plan pilote et rollback.
11. **Automatisation** d'au moins cinq règles de conformité en lecture seule.
12. **Runbook** d'un incident au choix avec collecte de preuves, actions de confinement et conditions de clôture.

### 18.3 Critères d'acceptation minimum

| Domaine | Test de réussite |
|---|---|
| Identité | Un terminal géré est autorisé selon son certificat ; un certificat invalide ne reçoit pas le rôle normal |
| MAB | Un appareil IoT connu reçoit seulement ses flux nécessaires ; un appareil inconnu est refusé/restreint |
| DHCP/ARP/IP | Le client légitime passe les tests ; une source interdite est bloquée dans le laboratoire |
| STP | Le root attendu est stable ; un BPDU inattendu sur un port edge déclenche la politique prévue |
| Segmentation | Les flux autorisés fonctionnent ; les flux non autorisés intra-VLAN et inter-VLAN sont testés au point approprié |
| IPv6 | RA/ DHCPv6 et flux invités suivent la politique si IPv6 est actif |
| Gestion | Le switch n'est administrable que depuis les sources prévues ; journaux et temps sont cohérents |
| Observabilité | Chaque test négatif produit une preuve exploitable sans divulguer de secret |
| Résilience | Le rollback est testé et la restauration des bindings/AAA est comprise |
| Documentation | Un autre technicien peut reproduire le déploiement, valider les résultats et revenir en arrière |

### 18.4 Évaluation du projet

- 20 % architecture et modèle de menace ;
- 20 % segmentation et politique de flux ;
- 20 % combinaison des protections L2/IPv6/802.1X ;
- 15 % déploiement progressif et rollback ;
- 15 % qualité des tests, journaux et preuves ;
- 10 % standardisation et automatisation.

Un projet avec beaucoup de commandes mais sans tests, preuves, traitement des exceptions ou procédure de retour arrière ne peut pas obtenir la meilleure note.


## 19. Évaluation finale et corrigé

### 19.1 Questions

**Q1.** Un poste s'authentifie en 802.1X mais ne peut pas joindre son serveur métier. Cite cinq points à vérifier dans l'ordre du chemin.

**Q2.** Pourquoi une adresse MAC approuvée par MAB n'est-elle pas une identité forte ? Donne deux mesures compensatoires.

**Q3.** Un port utilisateur est marqué trusted pour DHCP Snooping « afin d'éviter les pannes ». Quel est le risque et quelle démarche faut-il appliquer ?

**Q4.** Un hôte à IP statique est bloqué par DAI/IPSG après activation. Quelle est la bonne méthode et quel raccourci faut-il éviter ?

**Q5.** Quel est le rôle de Root Guard et en quoi diffère-t-il de Loop Guard ?

**Q6.** Pourquoi un filtrage d'ACL sur SVI ne garantit-il pas toujours l'isolation entre deux hôtes du même VLAN ?

**Q7.** Que signifie « MACsec configuré » et quelles preuves confirment que le lien est réellement protégé ?

**Q8.** Pourquoi le contrôle IPv4 seul ne suffit-il pas dans un réseau où IPv6 reste actif ?

**Q9.** Quel ordre de maturité faut-il privilégier pour automatiser la sécurité L2 ?

**Q10.** Donne quatre raisons pour lesquelles un changement L2 doit comporter un rollback et des critères d'arrêt.

**Q11.** Un switch d'accès est remplacé ; DHCP échoue, mais seuls certains appareils sont affectés. Cite quatre hypothèses distinctes et une preuve à collecter pour chacune.

**Q12.** Quelle différence fais-tu entre un contrôle préventif, un signal de détection et une mesure de réduction d'impact ? Utilise l'exemple d'un root STP inattendu.

### 19.2 Corrigé

**R1.** Vérifier état et identité de la session, attributs d'autorisation/VLAN, VLAN sur les trunks, DHCP/DNS et bindings, puis ACL/SGACL/pare-feu traversé et service final. Adapter l'ordre selon que le trafic est local au VLAN ou routé.

**R2.** Une MAC est exposée dans les trames et peut être usurpée. Mesures : VLAN d'IoT distinct avec ACL restrictive, inventaire/propriétaire, contrôle de port compatible, surveillance des changements de MAC ou remplacement par un mécanisme d'identité forte lorsque possible.

**R3.** Un service DHCP frauduleux peut contourner le filtre attendu sur cette interface. Identifier les chemins de serveurs/relais, ne faire confiance qu'aux interfaces légitimes, tester DHCP normal et interdit, relever compteurs, puis corriger de façon ciblée.

**R4.** Inventorier l'adresse, fournir un binding ou une exception minimale selon la plateforme, tester ARP et trafic IP, documenter le propriétaire et réviser périodiquement. Éviter de rendre le port entier trusted ou de désactiver DAI/IPSG partout.

**R5.** Root Guard empêche une racine non souhaitée d'être acceptée par un port prévu pour rester désigné. Loop Guard empêche certains ports root/alternate de devenir designated en l'absence inattendue de BPDUs. Les fonctions et compatibilités exactes dépendent de la plateforme ; on ne les applique pas indistinctement.

**R6.** Le trafic entre deux hôtes du même VLAN peut rester commuté localement sans traverser la SVI. Il faut placer le contrôle au point réel : VACL, PACL, PVLAN/isolation, politique distribuée ou hôte selon le design et le support.

**R7.** Il faut une session opérationnelle, un pair et un mode/suite cohérents, un état MKA valide si utilisé, des compteurs de trames protégées et aucune erreur de négociation. La ligne de configuration seule ne prouve pas que les paquets sont chiffrés.

**R8.** Les terminaux peuvent utiliser IPv6 link-local, RA, ND et DHCPv6 même sans adresse IPv4 globale. Les ACL IPv4 ne contrôlent pas ces chemins ; il faut une politique IPv6 et des protections FHS adaptées au support.

**R9.** Collecte read-only, audit de conformité, diff simulé, laboratoire, pilote/canary, déploiement progressif, puis vérification et rollback automatisable. Ne commence pas par appliquer une modification à tout le parc.

**R10.** Une fonction peut avoir des dépendances non vues ; un trunk ou root STP peut modifier le chemin ; une politique NAC peut bloquer les hôtes ; l'accès de gestion peut être perdu ; des bindings peuvent manquer ; les symptômes peuvent être difficiles à attribuer sans état initial. Le rollback réduit le rayon d'impact.

**R11.** Exemples : VLAN de trunk absent (preuve : liste VLAN/état trunk), base de bindings non restaurée (table avant/après reboot), sessions AAA différentes (journal de session), incompatibilité de version/fonction (versions et feature matrix), panne DHCP relay (capture/compteurs de relay), problème STP/Port-channel (root et états des membres). Il faut une preuve par hypothèse plutôt qu'un changement simultané de tous les paramètres.

**R12.** Préventif : Root Guard placé là où une nouvelle racine est interdite. Détection : log/alerte sur changement du root ID ou BPDU inattendue. Réduction d'impact : topologie redondante, confinement ciblé et procédure d'intervention. Ces fonctions se complètent, elles ne sont pas substituables.


## 20. Checklist de production et critères d'acceptation

### 20.1 Avant une mise en production

- [ ] Modèle, ASIC, version et restrictions des fonctions vérifiés dans la documentation officielle.
- [ ] Topologie, root STP, VLAN, trunks, Port-channels et voisins inventoriés.
- [ ] Les rôles des ports sont classés ; ports inutilisés désactivés avec processus de réservation.
- [ ] Les méthodes d'identité, certificats, MAB et modes d'hôte ont été testés.
- [ ] Les conséquences d'une indisponibilité AAA et le retour à l'état normal sont connus.
- [ ] DHCP Snooping, DAI et IPSG ont été déployés et vérifiés progressivement ; les hôtes statiques sont pris en charge.
- [ ] IPv6 est couvert par une politique explicite ou sa désactivation a été vérifiée de bout en bout et approuvée.
- [ ] Les guards STP correspondent au rôle des ports et sont testés dans la topologie réelle.
- [ ] Les VLAN et chemins de segmentation ont été testés intra-VLAN et inter-VLAN.
- [ ] MACsec est prouvé opérationnel s'il est prévu ; les segments non protégés sont documentés.
- [ ] SSH/AAA/SNMPv3/NTP/Syslog et les accès de secours sont protégés et testés.
- [ ] Les sauvegardes sont restaurables ; le rollback a été testé ; les critères d'arrêt sont écrits.
- [ ] Les alertes importantes, les propriétaires et les délais de réponse sont définis.

### 20.2 Après changement

- [ ] Tests fonctionnels exécutés depuis des appareils représentatifs.
- [ ] Tests négatifs autorisés en laboratoire ou sur le périmètre de validation exécutés.
- [ ] Configuration effective et état opérationnel comparés à l'état attendu.
- [ ] Compteurs de drop, sessions, bindings, STP et MACsec vérifiés.
- [ ] Pas de changement de VLAN, root STP, port-channel ou rôle NAC inattendu.
- [ ] Journaux et horodatages cohérents, preuve archivée.
- [ ] Les exceptions temporaires ont une date d'expiration et un propriétaire.
- [ ] Sauvegarde après validation et documentation mise à jour.

### 20.3 Revue périodique

- [ ] VLAN et trunks inutiles supprimés après validation d'impact.
- [ ] Exceptions MAB, IP statiques, ACL et ports trusted revus par propriétaire.
- [ ] Certificats, clés, comptes AAA et clés/API d'automatisation renouvelés suivant la politique.
- [ ] Version logicielle et avis de sécurité évalués, mises à jour planifiées.
- [ ] Écarts de configuration, sessions inconnues, MAC flapping et événements STP analysés.
- [ ] Les tests de restauration et de reprise AAA/MACsec sont périodiquement rejoués.
- [ ] Les runbooks correspondent toujours à la topologie et au matériel réels.


## 21. Glossaire

| Terme | Définition pratique |
|---|---|
| 802.1X | Contrôle d'accès réseau au niveau d'un port ; s'appuie souvent sur EAP et un serveur AAA |
| AAA | Authentication, Authorization, Accounting : authentification, autorisation et traçabilité |
| BPDU | Trame de contrôle utilisée par STP |
| BPDU Guard | Protection d'un port edge qui reçoit une BPDU inattendue |
| CAK / CKN | Paramètres de clé/identification utilisés dans un profil MACsec selon le mode de gestion |
| CoA | Change of Authorization, modification d'une session d'accès en cours si supportée/configurée |
| DAI | Dynamic ARP Inspection, validation des messages ARP entrants |
| DHCP Snooping | Contrôle des messages DHCP et apprentissage des bindings sur plateforme supportée |
| EAP-TLS | Méthode d'authentification EAP fondée sur TLS et certificats |
| Edge / PortFast | État/fonction STP destiné à un port relié à un terminal final |
| IPSG | IP Source Guard, contrôle de l'IP source au port d'entrée selon des bindings/politiques |
| LACP | Protocole de négociation et de contrôle des liens agrégés |
| MACsec | Protection cryptographique Ethernet sur un lien compatible |
| MAB | MAC Authentication Bypass ; solution de compatibilité basée sur l'adresse MAC, non équivalente à une identité forte |
| MKA | MACsec Key Agreement, gestion des associations et clés MACsec |
| NAC | Network Access Control, architecture de contrôle d'accès réseau |
| PACL | Port ACL, ACL appliquée à un port selon les capacités de la plateforme |
| PVLAN | Private VLAN, isolation de certains ports au sein d'un domaine VLAN selon des rôles |
| RADIUS | Protocole AAA fréquemment utilisé pour 802.1X |
| Root Guard | Protection STP contre une racine non souhaitée sur un port prévu pour rester désigné |
| Loop Guard | Protection STP contre certains changements de rôle liés à l'absence de BPDUs |
| SGT / SGACL | Tag et ACL de groupe dans certaines solutions de segmentation constructeur |
| SVI | Interface VLAN de couche 3 sur un switch multilayer |
| VACL | ACL appliquée à un VLAN, lorsque supportée |
| VNI / VXLAN | Identifiant de segment et mécanisme d'overlay L2/L3 sur IP dans certains datacenters |


## 22. Références techniques

Les docs constructeur sont des guides de plateforme, pas des recettes universelles. Vérifie le matériel, l'ASIC, les restrictions et la version logicielle en place avant d'appliquer une commande.

1. **Cisco — Security Configuration Guide, Catalyst 9300, IOS XE 17.18.x** : guide regroupant plusieurs protections de sécurité, dont 802.1X, DHCP Snooping, DAI, IPSG et First Hop Security IPv6.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg.html
2. **Cisco — Troubleshoot Dot1x on Catalyst 9000 Series Switches**, mis à jour le 6 octobre 2026 : méthode d'analyse des échanges entre client, switch et serveur AAA.  
   https://www.cisco.com/c/en/us/support/docs/lan-switching/8021x/220919-troubleshoot-dot1x-on-catalyst-9000-seri.html
3. **Cisco — Configuring IEEE 802.1X Port-Based Authentication, Catalyst 9300 / IOS XE 17.18** : rôles, hôtes, limites et paramètres 802.1X propres à la plateforme.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg/configuring_ieee_802_1x_port_based_authentication.html
4. **Cisco — Configuring IP Source Guard, Catalyst 9300 / IOS XE 17.18** : bindings, hôtes statiques et restrictions de configuration.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg/configuring_ip_source_guard.html
5. **Cisco — Configuring IPv6 First Hop Security, Catalyst 9300 / IOS XE 17.18** : RA Guard, DHCPv6 Guard, Source Guard et restrictions de la plateforme.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg/configuring_ipv6_first_hop_security.html
6. **Cisco — Configuring Optional Spanning-Tree Features, Catalyst 9300 / IOS XE 17.18** : BPDU Guard, Root Guard, Loop Guard et autres mécanismes STP.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/lyr2/b_1718_lyr2_9300_cg/configuring_optional_spanning_tree_features.html
7. **Cisco — Configuring MACsec Encryption, Catalyst 9300 / IOS XE 17.17** : MKA, profils et considérations de chiffrement au niveau Ethernet.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-17/configuration_guide/sec/b_1717_sec_9300_cg/macsec_encryption.html
8. **Cisco — Cisco TrustSec Overview, Catalyst 9300 / IOS XE 17.18** : SGT, SGACL et application de politiques basées sur les groupes.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/cts/b_1718_cts_9300_cg/cisco_trustsec_overview.html
9. **IETF RFC 7113 — Implementation Advice for IPv6 Router Advertisement Guard (RA-Guard)** : limitations connues des implémentations qui ne traitent pas correctement les extensions IPv6.  
   https://www.rfc-editor.org/rfc/rfc7113.html
10. **IETF RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)** : référence du protocole ND.  
    https://www.rfc-editor.org/rfc/rfc4861.html
11. **IETF RFC 3748 — Extensible Authentication Protocol (EAP)** : description du cadre EAP. Vérifie aussi les mises à jour et extensions pertinentes pour le déploiement utilisé.  
    https://www.rfc-editor.org/rfc/rfc3748.html
12. **IETF RFC 3580 — IEEE 802.1X RADIUS Usage Guidelines** : considérations d'utilisation de RADIUS pour l'authentification 802.1X ; à lire avec les extensions et recommandations actuelles du déploiement.  
    https://www.rfc-editor.org/rfc/rfc3580.html
13. **IETF RFC 7268 — RADIUS Attributes for IEEE 802 Networks** : attributs RADIUS associés aux réseaux IEEE 802.  
    https://www.rfc-editor.org/rfc/rfc7268.html
14. **IEEE 802.1AE — MAC Security (MACsec)** : norme de référence pour les services de sécurité au niveau Ethernet. Le texte intégral des normes IEEE peut nécessiter un accès via l'IEEE.  
    https://standards.ieee.org/standard/802_1AE-2018.html


## Conclusion

Une architecture L2 experte n'est pas celle qui active le plus de mécanismes. C'est celle où les rôles de ports, les identités, les segments, les bindings, les chemins STP, les politiques et les preuves d'exploitation restent cohérents lorsque le réseau change ou tombe en panne.

Pour chaque protection, pose systématiquement cinq questions :

1. **Où s'applique-t-elle ?** port, VLAN, ASIC, SVI, hyperviseur, lien MACsec ou point d'application distribué.
2. **Quelle donnée lui permet de décider ?** identité, certificat, binding, BPDU, tag, ACL ou état de session.
3. **Que peut-elle bloquer à tort ?** hôte statique, téléphone, IPv6, VM, trafic de contrôle ou service de démarrage.
4. **Comment prouver qu'elle fonctionne ?** état opérationnel, capture, compteur, journal, test positif et test négatif.
5. **Comment revenir à un état sûr ?** rollback testé, accès hors bande, owner et condition d'arrêt claire.

Le résultat attendu est un réseau où la sécurité est intentionnelle, observable, versionnée et réversible — et non une configuration longue dont personne ne peut expliquer les conséquences.
