# Sécurité de niveau 2 (L2) — Intermédiaire

> **Objectif du cours :** passer d'une sécurisation de base des ports à une architecture de sécurité L2 cohérente, mesurable et exploitable : contrôle d'accès, protection DHCP/ARP/IP, durcissement des trunks et de STP, protection IPv6, supervision et diagnostic structuré.
>
> **Public visé :** personne ayant terminé le cours `secu-l2-debutant.md`, ou maîtrisant déjà les VLAN, les ports access/trunk, Port Security, DHCP Snooping, Dynamic ARP Inspection (DAI) et les protections STP de base.
>
> **Fil pédagogique :** comprendre le risque → représenter le flux → choisir la protection → configurer prudemment → vérifier les effets → diagnostiquer les écarts. Les configurations sont principalement illustrées avec Cisco IOS/IOS XE ; les concepts restent généraux, mais les commandes et possibilités varient selon le constructeur, le modèle et la version.
>
> **Choix des schémas :** schémas textuels pour les topologies et les procédures reproductibles ; SVG statiques en couleurs pour les flux d'authentification et les dépendances entre protections. Les SVG n'utilisent ni animation ni élément mobile et disposent d'une alternative textuelle afin de rester compréhensibles si une plateforme Markdown filtre les images SVG intégrées.


## Sommaire

1. [Parcours pratique et objectifs](#1-parcours-pratique-et-objectifs)
2. [Modèle de menace et frontières de confiance](#2-modèle-de-menace-et-frontières-de-confiance)
3. [Architecture de laboratoire et règles de changement](#3-architecture-de-laboratoire-et-règles-de-changement)
4. [Durcir les VLAN et les trunks](#4-durcir-les-vlan-et-les-trunks)
5. [Contrôle d'accès réseau avec IEEE 802.1X](#5-contrôle-daccès-réseau-avec-ieee-8021x)
6. [MAB, VLAN de quarantaine et décisions AAA](#6-mab-vlan-de-quarantaine-et-décisions-aaa)
7. [Chaîne de protection DHCP Snooping, DAI et IP Source Guard](#7-chaîne-de-protection-dhcp-snooping-dai-et-ip-source-guard)
8. [Sécuriser STP et la topologie de niveau 2](#8-sécuriser-stp-et-la-topologie-de-niveau-2)
9. [Contrôler les tempêtes et les flux indésirables](#9-contrôler-les-tempêtes-et-les-flux-indésirables)
10. [Sécurité de la couche 2 pour IPv6](#10-sécurité-de-la-couche-2-pour-ipv6)
11. [Sécurité du plan d'administration](#11-sécurité-du-plan-dadministration)
12. [MACsec et protection des liens Ethernet](#12-macsec-et-protection-des-liens-ethernet)
13. [Supervision, journaux et preuves](#13-supervision-journaux-et-preuves)
14. [Méthode de diagnostic avancée](#14-méthode-de-diagnostic-avancée)
15. [Laboratoires guidés](#15-laboratoires-guidés)
16. [Projet de synthèse : sécuriser un petit campus](#16-projet-de-synthèse--sécuriser-un-petit-campus)
17. [Évaluation et corrigés](#17-évaluation-et-corrigés)
18. [Checklist d'exploitation](#18-checklist-dexploitation)
19. [Glossaire](#19-glossaire)
20. [Références techniques](#20-références-techniques)


## 1. Parcours pratique et objectifs

Le cours débutant a présenté les protections une par une. Le niveau intermédiaire enseigne à les **combiner sans créer de panne**, à comprendre leurs dépendances et à les exploiter dans un réseau comportant plusieurs VLAN, des postes gérés, des appareils non compatibles 802.1X et des liaisons redondantes.

### 1.1 Le parcours pratique réutilisé depuis le niveau débutant

Reprends ce mini-parcours avant d'entamer les nouveaux mécanismes. Il sert de point de contrôle, pas de répétition intégrale du cours précédent.

| Étape de remise à niveau | Manipulation | Preuve à conserver |
|---|---|---|
| Inventorier | Relever ports, VLAN, trunks, adresses MAC et équipements connectés | Tableau des ports et schéma de topologie daté |
| Sécuriser l'accès | Vérifier ports utilisateurs, ports inutilisés et VLAN d'accès | Sorties de commandes avant/après |
| Vérifier les protections | Inspecter Port Security, DHCP Snooping, DAI et protections STP déjà actives | État opérationnel et compteurs, pas seulement la configuration |
| Définir un état de référence | Tester DHCP, passerelle, DNS et communication entre VLAN autorisés | Résultats reproductibles depuis un poste témoin |
| Préparer le retour arrière | Sauvegarder la configuration et noter comment restaurer le service | Procédure de rollback simple et testée en laboratoire |

### 1.2 Progression du niveau intermédiaire

| Module | Compétence observable | Critère de réussite |
|---|---|---|
| 1 | Définir une frontière de confiance | Chaque port est classé et justifié : terminal, infrastructure ou administration |
| 2 | Durcir un trunk | VLAN autorisés limités, mode fixe, native VLAN documenté et cohérent |
| 3 | Concevoir un contrôle d'accès 802.1X | Les rôles supplicant, authenticator et serveur AAA sont compris et testés |
| 4 | Combiner DHCP Snooping, DAI et IP Source Guard | Les bindings sont cohérents et le trafic légitime continue de passer |
| 5 | Protéger la topologie STP | Les ports edge et les ports de distribution ont des protections adaptées à leur rôle |
| 6 | Réduire le bruit et les tempêtes | Les seuils sont basés sur une mesure, puis validés par un test contrôlé |
| 7 | Traiter IPv6 | Les mécanismes de découverte de voisin et d'annonce de routeur ne sont pas laissés sans contrôle |
| 8 | Administrer le switch en sécurité | SSH, AAA, SNMPv3, NTP, journalisation et accès d'administration sont cadrés |
| 9 | Diagnostiquer une panne combinée | L'analyse identifie le premier point de rejet plutôt que de désactiver toutes les protections |

### 1.3 Ce qu'il faut savoir faire à la fin

Tu dois pouvoir élaborer un standard de configuration par type de port, choisir les protections compatibles entre elles, documenter les exceptions, prouver leur fonctionnement par des tests légitimes et expliquer les conséquences possibles d'un mauvais réglage. Tu n'as pas besoin de prétendre qu'une protection rend un réseau invulnérable : le travail professionnel consiste à réduire les risques et à savoir détecter ce qui échappe aux contrôles.

### 1.4 Règles de laboratoire

- Travaille sur des équipements de test, Packet Tracer, CML, EVE-NG, GNS3 ou une maquette dont tu as l'autorisation.
- Ne lance pas de saturation, d'usurpation ARP ou de tests d'accès non autorisés sur un réseau de production.
- Modifie une famille de contrôles à la fois, puis compare les résultats aux tests de référence.
- Évite de copier une configuration d'un modèle vers un autre sans vérifier la syntaxe, les dépendances et la compatibilité des fonctionnalités.
- En production, prévois une fenêtre de changement, une sauvegarde, un plan de retour arrière et une console ou un accès hors bande si possible.


## 2. Modèle de menace et frontières de confiance

### 2.1 Penser en scénarios, pas en listes de commandes

Un réseau de campus n'est pas seulement composé de ports et de VLAN. Il contient des rôles de confiance différents : postes gérés, invités, téléphones IP, imprimantes, bornes Wi-Fi, hyperviseurs, serveurs, commutateurs d'accès et équipements de distribution. Le risque dépend de l'endroit où se connecte l'appareil, des protocoles qu'il peut émettre et des autres appareils qui partagent le même domaine L2.

Exemples de scénarios à analyser :

| Scénario | Objectif possible de l'attaquant | Contrôles pertinents | Limite à connaître |
|---|---|---|---|
| Un inconnu branche un ordinateur sur une prise libre | Obtenir une connectivité réseau | 802.1X, MAB contrôlé, ports inutilisés désactivés | Un port laissé dans un VLAN interne permet toujours une exposition |
| Un appareil se présente comme un serveur DHCP | Fournir une fausse passerelle ou de faux DNS | DHCP Snooping, contrôle physique | Il faut identifier correctement les interfaces vers les serveurs légitimes |
| Un hôte émet de faux ARP | Détourner du trafic local | DAI, segmentation, surveillance ARP | Les ports de confiance et les domaines non protégés restent des limites |
| Un switch non autorisé est branché | Étendre le domaine L2 et modifier la topologie | 802.1X, BPDU Guard aux ports edge, contrôle des trunks | BPDU Guard ne remplace pas une politique de contrôle d'accès |
| Un poste usurpe l'IP d'un voisin | Contourner certaines politiques ou perturber le service | IP Source Guard, ACL, NAC | Les hôtes statiques nécessitent une gestion adaptée des bindings |
| Une boucle apparaît après un mauvais brassage | Saturer les liens et tables | STP, Loop Guard, Storm Control | Storm Control limite les effets, mais ne corrige pas nécessairement la boucle |
| Un équipement IPv6 annonce une fausse route | Attirer ou perturber le trafic IPv6 | RA Guard, DHCPv6 Guard, segmentation IPv6 | Une politique limitée à IPv4 n'empêche pas tous les chemins IPv6 |

### 2.2 Frontières de confiance

Attribuer une confiance ne signifie pas qu'un équipement est « sûr ». Cela signifie qu'un rôle précis est autorisé à émettre certains messages sur un lien déterminé. Un port qui rejoint un serveur DHCP légitime peut devoir être de confiance pour DHCP Snooping ; cela ne signifie pas que le même port doit être exempt de tous les autres contrôles.

```text
ZONE TERMINAUX NON FIABLES
PC / imprimante / téléphone / invité
        |
        | ports d'accès : authentification et validation des trames
        v
+------------------------+
| Switch d'accès         |
| 802.1X / MAB            |
| DHCP Snooping / DAI     |
| IP Source Guard         |
| protections STP edge    |
+-----------+------------+
            |
            | trunk contrôlé : VLAN nécessaires seulement
            v
+------------------------+
| Distribution / cœur    |
| routage inter-VLAN      |
| ACL / politiques réseau |
| gestion et supervision  |
+------------------------+
```

Le schéma est volontairement textuel : il représente une frontière et le chemin des contrôles, sans dépendre du rendu graphique.

### 2.3 Défense en profondeur : quels contrôles se complètent ?

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 300" width="100%" height="300" role="img" aria-labelledby="defense-title defense-desc">
  <title id="defense-title">Défense en profondeur pour un port d'accès Ethernet</title>
  <desc id="defense-desc">Cinq couches colorées de contrôles, du contrôle d'identité à la détection opérationnelle, entourent le trafic terminal.</desc>
  <rect x="12" y="12" width="876" height="276" rx="18" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <text x="450" y="39" text-anchor="middle" font-family="Arial, sans-serif" font-size="18" font-weight="700" fill="#0f172a">Défense en profondeur — aucune couche ne suffit seule</text>
  <rect x="38" y="62" width="824" height="36" rx="8" fill="#dbeafe" stroke="#2563eb"/>
  <text x="56" y="85" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#1e3a8a">1. Identité</text>
  <text x="230" y="85" font-family="Arial, sans-serif" font-size="14" fill="#1e3a8a">802.1X / EAP-TLS / politique AAA</text>
  <rect x="38" y="105" width="824" height="36" rx="8" fill="#dcfce7" stroke="#16a34a"/>
  <text x="56" y="128" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#14532d">2. Segment</text>
  <text x="230" y="128" font-family="Arial, sans-serif" font-size="14" fill="#14532d">VLAN assigné, ACL et chemins autorisés</text>
  <rect x="38" y="148" width="824" height="36" rx="8" fill="#fef3c7" stroke="#d97706"/>
  <text x="56" y="171" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#78350f">3. Binding</text>
  <text x="230" y="171" font-family="Arial, sans-serif" font-size="14" fill="#78350f">DHCP Snooping, DAI et IP Source Guard</text>
  <rect x="38" y="191" width="824" height="36" rx="8" fill="#f3e8ff" stroke="#9333ea"/>
  <text x="56" y="214" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#581c87">4. Topologie</text>
  <text x="230" y="214" font-family="Arial, sans-serif" font-size="14" fill="#581c87">STP, BPDU Guard, Root Guard, Storm Control</text>
  <rect x="38" y="234" width="824" height="36" rx="8" fill="#fee2e2" stroke="#dc2626"/>
  <text x="56" y="257" font-family="Arial, sans-serif" font-size="15" font-weight="700" fill="#7f1d1d">5. Exploitation</text>
  <text x="230" y="257" font-family="Arial, sans-serif" font-size="14" fill="#7f1d1d">Syslog, alertes, sauvegarde, contrôle de changement</text>
</svg>

**Lecture du schéma :** une authentification réussie ne prouve pas que le trafic IP respecte les bindings ; un binding valide ne sécurise pas la topologie STP ; un blocage de trame ne sera utile durablement que si l'événement est observable et pris en charge.

### 2.4 Risque résiduel et exception documentée

Une exception doit avoir un propriétaire, une justification, un périmètre, un moyen de surveillance et une date de révision. Par exemple, une imprimante ancienne peut ne pas supporter 802.1X ; cela justifie éventuellement une politique MAB restrictive et un VLAN dédié, pas le placement de l'imprimante dans un VLAN utilisateur sans filtrage.


## 3. Architecture de laboratoire et règles de changement

### 3.1 Topologie conseillée

```text
                        +----------------------+
                        | Routeur / pare-feu   |
                        | passerelles VLAN     |
                        +----------+-----------+
                                   | trunk limité
                         +---------+----------+
                         | SW-DIST (L3/L2)    |
                         | root STP attendu   |
                         +----+----------+----+
                              |          |
                         trunk|          |trunk
                    +---------+--+    +--+---------+
                    | SW-ACC-A   |    | SW-ACC-B   |
                    | accès      |    | accès      |
                    +--+---+---+-+    +-+---+---+--+
                       |   |   |        |   |   |
                      PC  IP  AP       PC  IoT Impr.
```

### 3.2 Plan d'adressage d'exemple

Utilise des plages privées réservées à la documentation et à des laboratoires isolés. Le tableau ci-dessous est un exemple ; adapte-le aux besoins de la maquette.

| VLAN | Rôle | Sous-réseau de labo | Politique de départ |
|---:|---|---|---|
| 10 | Utilisateurs gérés | `192.0.2.0/25` | Accès aux services métier nécessaires |
| 20 | Administration réseau | `198.51.100.0/24` | Accessible uniquement depuis les postes d'administration prévus |
| 30 | Invités | `203.0.113.0/24` | Accès Internet uniquement, aucun accès aux réseaux internes |
| 40 | IoT / imprimantes | `198.18.0.0/24` | Flux explicitement autorisés vers services ciblés |
| 99 | Gestion des switches | `192.0.2.128/25` | Administration restreinte, jamais un VLAN utilisateur par défaut |
| 999 | Parking / VLAN inutilisé | Aucun adressage utilisateur | Aucun service utilisateur, ports non utilisés désactivés |

Les plages `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont destinées aux exemples documentaires. `198.18.0.0/15` est réservée aux tests de benchmarking. Ne copie pas ce plan dans un réseau réel sans choisir un plan privé adapté et vérifier l'absence de conflit.

### 3.3 Inventaire des ports

| Port logique | Équipement connecté | Mode | VLAN | Niveau de confiance | Contrôles prioritaires |
|---|---|---|---:|---|---|
| `Gi1/0/1` | Poste géré | Access | 10 | Faible avant authentification | 802.1X, bindings IP, edge STP |
| `Gi1/0/2` | Téléphone + PC | Access + voice VLAN si pris en charge | 10 + voix | Faible, plusieurs identités | 802.1X multi-domaines, limites adaptées |
| `Gi1/0/10` | Point d'accès contrôlé | Trunk selon le design | VLAN documentés | Infrastructure | Liste VLAN, authentification adaptée, STP selon rôle |
| `Gi1/0/23` | Uplink vers distribution | Trunk statique | 10,20,30,40,99 | Infrastructure | VLAN autorisés, STP, agrégation si nécessaire |
| `Gi1/0/24` | Libre | Aucun service | 999 | Non utilisé | Shutdown, documentation et inspection périodique |

La colonne « confiance » décrit la décision de sécurité, pas l'état physique du lien. Un équipement d'infrastructure doit être contrôlé, inventorié et surveillé même si son port est traité comme de confiance par une fonctionnalité précise.

### 3.4 Préparer et appliquer une modification

1. **Préparer :** écrire le résultat attendu, les ports affectés, les dépendances, les commandes de contrôle et la commande de retour arrière.
2. **Mesurer :** relever l'état actuel et valider les tests de base (DHCP, DNS, passerelle, application métier).
3. **Changer :** appliquer un petit lot de commandes ; éviter une modification globale non testée.
4. **Vérifier :** contrôler l'état opérationnel, les compteurs de rejet, les journaux et l'expérience d'un client.
5. **Documenter :** conserver la configuration finale, les résultats et les exceptions.
6. **Revenir en arrière si nécessaire :** restaurer le dernier état connu et analyser la cause hors de la pression de l'incident.

Ne considère pas la présence d'une commande dans `running-config` comme preuve que le mécanisme fonctionne. La plateforme peut ne pas prendre en charge la fonctionnalité, une interface peut être dans le mauvais rôle, une base d'association peut être vide ou un autre contrôle peut rejeter le trafic avant celui que tu examines.


## 4. Durcir les VLAN et les trunks

### 4.1 Pourquoi le trunk mérite une politique explicite

Un trunk transporte plusieurs domaines VLAN. Une erreur de configuration peut exposer un VLAN sensible à un lien qui n'en a pas besoin, permettre des chemins inattendus ou compliquer l'analyse d'un incident. La règle est simple : **mode fixe, VLAN autorisés minimaux, VLAN natif cohérent et voisins documentés**.

### 4.2 Politique de configuration type — exemple Cisco IOS/IOS XE

```text
configure terminal
!
interface GigabitEthernet1/0/23
 description UPLINK_VERS_SW-DIST
 switchport
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,99
 switchport trunk native vlan 999
 ! Ne pas activer de négociation dynamique non nécessaire.
 ! La syntaxe de désactivation de DTP dépend de la plateforme.
 spanning-tree guard loop
 no shutdown
!
end
```

**À adapter avant exécution :** la commande `switchport trunk encapsulation dot1q` n'est pas présente sur toutes les familles, car certains modèles n'acceptent que 802.1Q. Les commandes de désactivation de DTP varient ; sur certaines plateformes Cisco, `switchport nonegotiate` est disponible lorsque le port est fixé en access ou trunk. Vérifie la référence du modèle et le guide de la version.

**Attention à `spanning-tree guard loop` :** il n'est pas à appliquer aveuglément à chaque trunk. Loop Guard protège certains ports non-edge qui devraient recevoir des BPDUs ; Root Guard s'utilise sur des ports où l'on ne veut pas qu'un voisin devienne racine. Le choix dépend du rôle de chaque lien et de la conception STP.

### 4.3 VLAN natif : cohérence plutôt qu'une valeur magique

Le VLAN natif transporte généralement les trames non taguées sur un trunk 802.1Q. Une différence de VLAN natif entre les deux extrémités peut entraîner des classifications de trames incohérentes et des alertes STP. Placer le VLAN natif sur un VLAN réservé sans utilisateurs réduit certaines erreurs, mais ne remplace pas la cohérence des deux côtés ni le contrôle des VLAN autorisés.

```text
SW-A                                  SW-B
Trunk natif = 999  ------------------  Trunk natif = 999
VLAN autorisés = 10,20,99              VLAN autorisés = 10,20,99

Mauvais exemple :
SW-A natif = 999  ------------------  SW-B natif = 1
                  ^ incohérence à corriger
```

### 4.4 Prévenir les trunks non désirés

Sur les ports de terminaux, configure un mode d'accès explicite et désactive les mécanismes de négociation de trunk quand la plateforme le permet. Ne laisse pas un port utilisateur en mode dynamique par commodité.

```text
interface GigabitEthernet1/0/1
 description POSTE_UTILISATEUR
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
 spanning-tree bpduguard enable
```

La commande PortFast concerne les ports terminaux, pas les liens inter-switchs classiques. BPDU Guard protège un port edge contre la réception inattendue de BPDUs ; selon la configuration, il peut placer le port en état err-disabled. Une alerte doit être traitée comme un événement à diagnostiquer, pas contournée par désactivation immédiate de la protection.

### 4.5 Liste de contrôle trunk

- [ ] Le voisin est inventorié et correspond à la topologie prévue.
- [ ] Le trunk est configuré en mode statique.
- [ ] Seuls les VLAN utiles sont autorisés.
- [ ] Le VLAN natif est réservé et identique aux deux extrémités.
- [ ] Le trunk ne rejoint pas un port utilisateur ou un équipement inconnu.
- [ ] Les protections STP sont choisies selon la position du lien.
- [ ] L'agrégation de liens, si présente, a une configuration cohérente des deux côtés.
- [ ] Les états opérationnels et compteurs sont vérifiés après changement.

### 4.6 Vérification Cisco IOS/IOS XE

```text
show interfaces trunk
show interfaces GigabitEthernet1/0/23 switchport
show vlan brief
show spanning-tree interface GigabitEthernet1/0/23 detail
show logging
```

Le nom et la disponibilité des commandes peuvent varier. Cherche en priorité les VLAN actifs et autorisés, le VLAN natif opérationnel, le rôle STP et les incohérences de voisinage.


## 5. Contrôle d'accès réseau avec IEEE 802.1X

### 5.1 Pourquoi ajouter une décision d'identité ?

Port Security limite ou identifie les adresses MAC apprises sur un port. Ce contrôle n'authentifie pas à lui seul une personne ou un équipement : une MAC peut être usurpée. 802.1X ajoute une procédure d'authentification au point d'accès réseau et peut transmettre une identité à un serveur AAA afin qu'une politique d'accès soit appliquée.

### 5.2 Les trois rôles

- **Supplicant :** client qui demande l'accès, généralement un système d'exploitation ou un équipement compatible 802.1X.
- **Authenticator :** le plus souvent le switch d'accès ou le point d'accès Wi-Fi ; il contrôle l'accès au réseau avant l'autorisation.
- **Serveur d'authentification :** souvent un serveur RADIUS qui valide la méthode, applique une politique et retourne une décision.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 350" width="100%" height="350" role="img" aria-labelledby="dot1x-title dot1x-desc">
  <title id="dot1x-title">Échange d'authentification IEEE 802.1X</title>
  <desc id="dot1x-desc">Le supplicant échange EAPOL avec le switch, le switch relaie EAP via RADIUS au serveur AAA et reçoit une décision avant d'autoriser ou de refuser l'accès.</desc>
  <rect x="18" y="20" width="864" height="310" rx="16" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <rect x="48" y="60" width="220" height="90" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="158" y="88" font-family="Arial,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#1e3a8a">Supplicant</text>
  <text x="158" y="112" font-family="Arial,sans-serif" font-size="14" text-anchor="middle" fill="#1e40af">PC / terminal</text>
  <text x="158" y="132" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#1e40af">Identité + méthode EAP</text>
  <rect x="340" y="60" width="220" height="90" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="450" y="88" font-family="Arial,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#14532d">Authenticator</text>
  <text x="450" y="112" font-family="Arial,sans-serif" font-size="14" text-anchor="middle" fill="#166534">Switch d'accès</text>
  <text x="450" y="132" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#166534">Contrôle le port</text>
  <rect x="632" y="60" width="220" height="90" rx="12" fill="#f3e8ff" stroke="#9333ea" stroke-width="2"/>
  <text x="742" y="88" font-family="Arial,sans-serif" font-size="18" font-weight="700" text-anchor="middle" fill="#581c87">Serveur AAA</text>
  <text x="742" y="112" font-family="Arial,sans-serif" font-size="14" text-anchor="middle" fill="#6b21a8">RADIUS</text>
  <text x="742" y="132" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#6b21a8">Authentifie / autorise</text>
  <line x1="268" y1="96" x2="340" y2="96" stroke="#2563eb" stroke-width="3"/>
  <polygon points="340,96 329,90 329,102" fill="#2563eb"/>
  <text x="304" y="82" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#1e3a8a">EAPOL</text>
  <line x1="560" y1="96" x2="632" y2="96" stroke="#9333ea" stroke-width="3"/>
  <polygon points="632,96 621,90 621,102" fill="#9333ea"/>
  <text x="596" y="82" font-family="Arial,sans-serif" font-size="11" text-anchor="middle" fill="#6b21a8">RADIUS</text>
  <path d="M 742 151 L 742 188 L 450 188 L 450 151" fill="none" stroke="#64748b" stroke-width="2" stroke-dasharray="6 5"/>
  <text x="596" y="208" font-family="Arial,sans-serif" font-size="13" text-anchor="middle" fill="#334155">Access-Accept / Access-Reject</text>
  <rect x="70" y="238" width="330" height="56" rx="10" fill="#dcfce7" stroke="#16a34a"/>
  <text x="235" y="261" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#14532d">Accept</text>
  <text x="235" y="280" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#166534">Port/VLAN/politique autorisés selon la réponse</text>
  <rect x="500" y="238" width="330" height="56" rx="10" fill="#fee2e2" stroke="#dc2626"/>
  <text x="665" y="261" font-family="Arial,sans-serif" font-size="15" font-weight="700" text-anchor="middle" fill="#7f1d1d">Reject ou échec</text>
  <text x="665" y="280" font-family="Arial,sans-serif" font-size="12" text-anchor="middle" fill="#991b1b">Accès refusé ou VLAN de repli selon la politique</text>
</svg>

**Alternative textuelle :** `PC --EAPOL--> switch --RADIUS/EAP--> serveur AAA --décision--> switch --autorise ou refuse--> PC`.

### 5.3 Déroulement opérationnel

1. Le lien physique monte.
2. Le client et l'authenticator entament l'échange EAPOL.
3. Le switch relaie les informations d'authentification au serveur AAA par RADIUS.
4. Le serveur valide ou rejette l'identité selon la méthode EAP et sa politique.
5. Le switch applique le résultat : autorisation, VLAN attribué, ACL téléchargeable ou autres paramètres pris en charge.
6. Les événements et sessions sont surveillés ; une réauthentification peut être prévue selon la politique.

Les trames EAPOL sont échangées localement entre le supplicant et l'authenticator. Le serveur RADIUS n'est pas l'extrémité d'un tunnel EAPOL de couche 2 : le switch relaie le contenu EAP dans des messages RADIUS.

### 5.4 Choisir une méthode d'authentification

| Méthode | Principe | Points forts | Risques / contraintes |
|---|---|---|---|
| EAP-TLS | Certificat client et validation du certificat serveur | Authentification mutuelle solide ; adaptée aux postes gérés | Cycle de vie PKI, enrôlement et révocation des certificats |
| PEAP ou méthode tunnelisée équivalente | Tunnel TLS avec authentification interne | Peut s'intégrer à certains environnements existants | Dépend de la méthode interne et de la validation correcte du certificat serveur |
| MAB (MAC Authentication Bypass) | Utilise l'adresse MAC comme identifiant lorsque 802.1X échoue ou n'est pas supporté | Compatibilité avec certains appareils simples | Faible assurance : la MAC peut être usurpée ; politique restrictive indispensable |
| Port ouvert sans authentification | Accès direct | Simple mais peu contrôlé | À éviter pour les ports internes ordinaires ; acceptable seulement dans des cas explicitement conçus et documentés |

Pour les postes administrés, EAP-TLS est souvent une cible robuste lorsqu'une PKI, l'enrôlement et le support client sont correctement opérés. La méthode exacte doit correspondre aux capacités et politiques de l'organisation. Le serveur doit présenter un certificat validé par le client ; ne demande pas aux utilisateurs de cliquer sur « accepter tous les certificats » pour contourner une erreur.

### 5.5 État autorisé et état non autorisé

Un port 802.1X non autorisé ne devrait pas laisser passer librement le trafic utilisateur ordinaire. Certaines trames nécessaires à l'authentification et au contrôle peuvent être permises selon l'implémentation. Après autorisation, le réseau doit appliquer les autres politiques de sécurité prévues ; l'authentification ne remplace ni la segmentation ni les contrôles DHCP/ARP/IP.

### 5.6 Préparer le service AAA

Avant d'activer 802.1X à grande échelle, prépare :

- au moins un serveur AAA de test et, en production, une stratégie de redondance appropriée ;
- la configuration des clients RADIUS (adresse IP du switch, secret robuste ou méthode plus moderne supportée) ;
- la connectivité de gestion, les ACL nécessaires, la synchronisation de l'heure et la journalisation ;
- un groupe test de postes et une méthode claire de retour arrière ;
- une procédure de secours qui ne transforme pas tous les ports en ports ouverts.

### 5.7 Exemple de squelette Cisco IOS/IOS XE — à adapter

Cet exemple illustre la structure générale, pas une configuration prête à déployer. Les syntaxes AAA et 802.1X diffèrent entre versions et plates-formes ; certaines fonctionnalités nécessitent des prérequis supplémentaires.

```text
! Exemple conceptuel : ne pas coller tel quel en production.
aaa new-model
radius server AAA-LAB
 address ipv4 192.0.2.10 auth-port 1812 acct-port 1813
 key <SECRET_RADIUS_LONG_ET_UNIQUE>
!
aaa authentication dot1x default group radius
aaa authorization network default group radius
!
dot1x system-auth-control
!
interface GigabitEthernet1/0/1
 description POSTE_TEST_8021X
 switchport mode access
 switchport access vlan 10
 authentication port-control auto
 dot1x pae authenticator
 spanning-tree portfast
 spanning-tree bpduguard enable
!
```

**Précautions :** certains systèmes utilisent une syntaxe différente, des commandes de méthode d'authentification, de réauthentification, de gestion des échecs ou de suivi d'équipement. Il faut aussi vérifier la configuration du supplicant, du certificat serveur, de RADIUS et de la politique de retour. Un port 802.1X peut se comporter différemment selon le mode multi-host, multi-auth ou multi-domain. Le choix a un impact important sur les téléphones IP et les appareils en aval.

### 5.8 Vérifications 802.1X

Exemples courants, selon IOS/IOS XE :

```text
show authentication sessions
show authentication sessions interface GigabitEthernet1/0/1 details
show dot1x all
show radius statistics
show logging
```

À confirmer dans la référence du modèle. Vérifie l'état de la session, la méthode utilisée, le résultat AAA, le VLAN et la politique effectivement attribués, ainsi que les compteurs d'échec. Une configuration correcte côté switch ne compense pas un certificat expiré ou un supplicant client mal configuré.


## 6. MAB, VLAN de quarantaine et décisions AAA

### 6.1 MAB : compatibilité, pas identité forte

Certaines imprimantes, caméras, appareils IoT ou équipements anciens ne prennent pas en charge 802.1X. MAB permet de soumettre l'adresse MAC du terminal à un serveur AAA comme élément d'identification. Cette approche apporte une décision centralisée, mais elle n'offre pas la même assurance qu'une authentification cryptographique : une adresse MAC peut être copiée.

Une politique MAB raisonnable doit au minimum :

- autoriser seulement les catégories d'appareils prévues, selon un inventaire tenu à jour ;
- placer les équipements dans un VLAN ou une politique avec des flux strictement limités ;
- limiter la présence d'un terminal à la zone et au port où il est attendu, lorsque les outils le permettent ;
- journaliser les échecs et les changements d'emplacement ;
- prévoir une date de réévaluation des exceptions ;
- éviter de traiter la seule MAC comme un secret.

### 6.2 Modes de port pour plusieurs appareils

Un port peut transporter un téléphone IP et un ordinateur, ou un mini-switch de poste autorisé. Le mode d'authentification doit refléter ce cas. Les modes comme single-host, multi-host, multi-auth ou multi-domain n'ont pas exactement le même comportement et leurs noms ne sont pas parfaitement interchangeables entre constructeurs.

| Situation | Question à résoudre | Mauvais raccourci |
|---|---|---|
| PC derrière un téléphone IP | Les deux identités ont-elles leur propre décision ? | Permettre le premier appareil et faire confiance à tous les suivants sans analyse |
| Imprimante sans 802.1X | Peut-elle utiliser MAB avec une liste ou politique contrôlée ? | Laisser le port sans authentification dans le VLAN des employés |
| Téléphone IP partagé | Le VLAN voix est-il séparé et les services accessibles sont-ils limités ? | Supposer que la voix est fiable par nature |
| Hyperviseur ou serveur avec plusieurs MAC | Le nombre d'identités est-il prévisible ? Les politiques sont-elles compatibles ? | Appliquer une limite MAC de 1 sans inventaire |

### 6.3 VLAN invité, VLAN critique et VLAN de quarantaine

Les noms et comportements dépendent des fonctions supportées, mais les usages typiques sont :

- **VLAN invité :** accès très limité, souvent Internet uniquement.
- **VLAN de quarantaine / remédiation :** accès uniquement aux services nécessaires pour corriger l'équipement ou installer un certificat.
- **VLAN critique AAA :** réponse de secours lorsque le serveur AAA est indisponible, si la plateforme et la politique l'autorisent.
- **VLAN des appareils non gérés :** service restreint pour les équipements sans supplicant.

Le mode « fail open » et le mode « fail closed » sont des décisions de risque. Fail open peut préserver la disponibilité mais accroître l'exposition ; fail closed réduit l'accès en cas de panne AAA mais peut interrompre une activité essentielle. Une solution intermédiaire doit être définie explicitement : par exemple, une politique de secours dédiée, surveillée et restreinte, plutôt que l'ouverture générale des ports.

### 6.4 Matrice d'autorisation type

| Identité / catégorie | VLAN ou politique | Accès autorisé | Interdictions importantes |
|---|---|---|---|
| PC géré authentifié | Utilisateurs | DNS, DHCP, applications métier selon rôle | Administration des switches si non nécessaire |
| Poste d'administration géré | Administration | SSH/HTTPS/SNMP ciblés vers équipements approuvés | Accès d'administration depuis VLAN invités |
| Imprimante MAB autorisée | IoT / impression | Serveur d'impression et DNS/NTP nécessaires | Connexions initiées vers postes utilisateurs non requises |
| Terminal inconnu | Quarantaine ou refus | Portail ou services de remédiation, selon conception | Réseaux métiers et gestion |
| Invité | Invités | DNS et accès externe autorisé | Réseaux internes et interfaces de gestion |

Un VLAN n'est pas un pare-feu complet : les ACL ou politiques du pare-feu doivent appliquer les flux entre segments et vers les ressources sensibles.

### 6.5 Exercices de conception AAA

Pour chaque scénario, écris la décision de politique, la conséquence si le serveur AAA est indisponible et l'élément de preuve à surveiller :

1. Un ordinateur géré possède un certificat valide et appartient au groupe « Finance ».
2. Une imprimante ne supporte pas EAP-TLS mais son identifiant est connu.
3. Un ordinateur échoue parce que son certificat a expiré.
4. Le serveur RADIUS principal ne répond plus, mais le second reste opérationnel.
5. Un terminal inconnu se présente avec la MAC d'une imprimante autorisée.

Le but n'est pas d'écrire un unique « VLAN magique », mais de démontrer que la décision, le périmètre et le contrôle opérationnel sont cohérents.


## 7. Chaîne de protection DHCP Snooping, DAI et IP Source Guard

### 7.1 Pourquoi ces mécanismes vont ensemble

Ces contrôles se renforcent mutuellement, mais ils ne font pas le même travail :

- **DHCP Snooping** filtre les messages DHCP selon le rôle de confiance de l'interface et peut construire une base d'associations attribuant une IP, une MAC, un VLAN et un port.
- **Dynamic ARP Inspection (DAI)** valide les messages ARP reçus sur les interfaces non fiables en se référant à cette base, ou à des listes ARP adaptées aux environnements statiques.
- **IP Source Guard (IPSG)** limite sur un port d'accès le trafic IP dont l'adresse source ne correspond pas à une association autorisée ; la forme précise du contrôle dépend de la plateforme.

<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 920 360" width="100%" height="360" role="img" aria-labelledby="binding-title binding-desc">
  <title id="binding-title">Chaîne DHCP Snooping, DAI et IP Source Guard</title>
  <desc id="binding-desc">DHCP Snooping construit la base de bindings. DAI consulte les associations lors de la validation ARP. IP Source Guard vérifie l'adresse source des paquets IP sur le port.</desc>
  <rect x="14" y="14" width="892" height="332" rx="18" fill="#f8fafc" stroke="#cbd5e1" stroke-width="2"/>
  <rect x="42" y="48" width="236" height="82" rx="12" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="160" y="78" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#1e3a8a">DHCP Snooping</text>
  <text x="160" y="101" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#1e40af">Filtre DHCP + apprend les baux</text>
  <rect x="342" y="48" width="236" height="82" rx="12" fill="#dcfce7" stroke="#16a34a" stroke-width="2"/>
  <text x="460" y="78" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#14532d">Base de bindings</text>
  <text x="460" y="101" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#166534">IP / MAC / VLAN / port</text>
  <rect x="642" y="48" width="236" height="82" rx="12" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="760" y="78" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#78350f">DAI</text>
  <text x="760" y="101" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#92400e">Valide ARP sur ports non fiables</text>
  <line x1="278" y1="89" x2="342" y2="89" stroke="#2563eb" stroke-width="3"/>
  <polygon points="342,89 331,83 331,95" fill="#2563eb"/>
  <line x1="578" y1="89" x2="642" y2="89" stroke="#16a34a" stroke-width="3"/>
  <polygon points="642,89 631,83 631,95" fill="#16a34a"/>
  <text x="460" y="155" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#475569">Une association cohérente sert de référence — si elle est disponible et adaptée</text>
  <rect x="42" y="192" width="386" height="104" rx="12" fill="#f3e8ff" stroke="#9333ea" stroke-width="2"/>
  <text x="235" y="222" text-anchor="middle" font-family="Arial,sans-serif" font-size="18" font-weight="700" fill="#581c87">IP Source Guard</text>
  <text x="235" y="247" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="#6b21a8">Filtre les paquets IP selon le binding</text>
  <text x="235" y="269" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#6b21a8">Activer après validation du service DHCP</text>
  <path d="M 460 130 L 460 173 L 235 173 L 235 192" fill="none" stroke="#9333ea" stroke-width="2.5"/>
  <polygon points="235,192 229,181 241,181" fill="#9333ea"/>
  <rect x="482" y="192" width="396" height="104" rx="12" fill="#e2e8f0" stroke="#64748b" stroke-width="2"/>
  <text x="680" y="222" text-anchor="middle" font-family="Arial,sans-serif" font-size="17" font-weight="700" fill="#0f172a">À ne pas confondre</text>
  <text x="680" y="246" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#334155">Trust = exemption d'un contrôle ciblé</text>
  <text x="680" y="267" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#334155">pas une confiance générale dans l'équipement</text>
  <text x="460" y="322" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" fill="#475569">Si les adresses sont statiques, prévoir des bindings ou ACL adaptés à la plateforme.</text>
</svg>

**Version textuelle :** DHCP Snooping observe les échanges sur les ports configurés et construit une base d'associations ; DAI compare les messages ARP à cette base ; IP Source Guard utilise les associations pour limiter les adresses IP sources sur les ports concernés.

### 7.2 Principe de confiance DHCP

Un port vers un serveur DHCP légitime ou un relais peut nécessiter l'état trusted. Les ports terminaux sont généralement untrusted. Si le port est trusted par erreur, des messages DHCP malveillants peuvent passer à travers le contrôle prévu. Si l'uplink légitime n'est pas trusted alors qu'il doit l'être, les réponses DHCP peuvent être bloquées et les clients ne reçoivent plus de bail.

```text
Client A (untrusted)        SW-ACCÈS               Serveur DHCP
       | DHCP Discover ------>|                         |
       |                      |--- Discover ----------->|
       |                      |<-- Offer ---------------|
       |<-- Offer autorisé ---|                         |

Faux serveur connecté à un port utilisateur :
       | DHCP Offer non autorisé -> rejet / journalisation
```

La topologie réelle peut comporter un relais DHCP et plusieurs switches. Il faut alors définir où les messages sont vus et quel équipement est source de la base de bindings.

### 7.3 Exemple Cisco IOS/IOS XE — DHCP Snooping

```text
configure terminal
ip dhcp snooping
ip dhcp snooping vlan 10,20,30,40
!
interface GigabitEthernet1/0/23
 description UPLINK_VERS_DHCP_AUTORISE
 ip dhcp snooping trust
!
interface GigabitEthernet1/0/1
 description CLIENT_VLAN10
 switchport mode access
 switchport access vlan 10
 ip dhcp snooping limit rate 20
!
end
```

Le seuil `20` est purement indicatif pour un laboratoire et doit être mesuré selon le client, le téléphone, les usages et la plateforme. N'applique pas un seuil arbitrairement bas aux ports qui hébergent plusieurs appareils ou des équipements qui peuvent générer de nombreux échanges DHCP. La commande de persistance de la base de bindings, quand elle existe, doit utiliser un emplacement et des permissions appropriés.

### 7.4 Vérifier DHCP Snooping

```text
show ip dhcp snooping
show ip dhcp snooping binding
show ip dhcp snooping statistics
show logging
```

Cherche la présence du VLAN, le rôle de confiance des interfaces, les limites configurées et les associations apprises. Sur certains switches, les commandes de statistiques ou de base diffèrent.

### 7.5 Activer DAI après avoir vérifié les bindings

```text
configure terminal
ip arp inspection vlan 10,20,30,40
!
interface GigabitEthernet1/0/23
 ip arp inspection trust
!
end
```

L'exemple suppose que l'uplink doit être trusted pour DAI selon la topologie. Il ne faut pas lui appliquer automatiquement le même statut pour toutes les fonctionnalités : **la confiance DHCP, la confiance DAI et le rôle STP doivent chacun être justifiés séparément**.

Pour vérifier :

```text
show ip arp inspection
show ip arp inspection vlan 10
show ip arp inspection statistics
show logging
```

Selon la plateforme, un mécanisme de validation additionnel peut vérifier la correspondance entre l'adresse MAC Ethernet et l'adresse MAC annoncée dans ARP, ainsi que certaines contraintes d'adresse IPv4. Comprends les cas qui seront rejetés avant de l'activer à grande échelle.

### 7.6 Hôtes à adresse IP statique

DAI utilise souvent les associations apprises par DHCP Snooping. Un poste configuré en IP statique peut ne pas avoir d'entrée correspondante et voir ses requêtes ARP rejetées. Pour un réseau comportant des hôtes statiques :

1. dresse la liste des appareils et adresses autorisées ;
2. choisis une méthode supportée par le modèle (par exemple ARP ACL, association statique ou approche équivalente) ;
3. limite cette règle à la bonne interface et au bon VLAN ;
4. teste requêtes et réponses ARP légitimes ;
5. documente la maintenance quand une adresse change.

Ne désactive pas DAI pour tout un VLAN simplement parce qu'une imprimante statique a été oubliée. Corrige plutôt l'exception au bon périmètre, après avoir confirmé l'adresse et la MAC attendues.

### 7.7 IP Source Guard

```text
interface GigabitEthernet1/0/1
 ip verify source
```

C'est une syntaxe illustrée pour certaines plateformes Cisco ; les variantes et le niveau de filtrage disponibles dépendent du modèle et de la version. IPSG n'est pas une ACL universelle pour tout le réseau. Il agit sur l'interface supportée et s'appuie généralement sur les informations d'association disponibles. Les adresses IP statiques nécessitent une prise en charge explicite des bindings ou un mécanisme compatible.

**Ordre recommandé en laboratoire :**

1. valider le DHCP normal ;
2. activer DHCP Snooping et vérifier la base ;
3. activer DAI sur un seul VLAN de test et valider ARP ;
4. répertorier les hôtes statiques et les exceptions nécessaires ;
5. activer IP Source Guard sur un port de test ;
6. valider DHCP, DNS, passerelle, communication locale et trafic autorisé ;
7. étendre seulement après preuve.

### 7.8 Cas IPv6 à part

DAI est lié à ARP pour IPv4. Il ne protège pas automatiquement Neighbor Discovery IPv6, Router Advertisements ou DHCPv6. Le traitement IPv6 est présenté dans la section 10 et doit faire partie du plan dès que IPv6 est activé sur le réseau.


## 8. Sécuriser STP et la topologie de niveau 2

### 8.1 Pourquoi STP reste critique

STP/RSTP réduit les risques de boucles Ethernet en plaçant certains liens dans un état qui empêche la circulation de trames de données. La sélection de la racine influence les chemins actifs. Si un switch non prévu participe à l'élection et devient racine, le trafic peut prendre un chemin inattendu, avec un impact sur la performance, la résilience ou les contrôles réseau.

### 8.2 Carte des protections STP

| Fonction | Usage typique | Ce qu'elle ne fait pas |
|---|---|---|
| PortFast / edge port | Accélérer la transition d'un port terminal vers le forwarding | Ne rend pas le port sûr à lui seul ; éviter sur un lien vers un switch ordinaire |
| BPDU Guard | Mettre en protection un port edge qui reçoit un BPDU inattendu | Ne remplace pas l'authentification d'accès ni les contrôles physiques |
| Root Guard | Empêcher un port désigné de devenir un chemin vers une racine STP non désirée | N'est pas une protection générique à poser sur tout port |
| Loop Guard | Réagir lorsqu'un port non-edge cesse de recevoir les BPDUs attendus dans certains états | Ne remplace pas un design STP correct ou le contrôle du brassage |
| BPDU Filter | Supprimer ou inhiber des BPDUs selon son mode | Peut masquer un problème STP ; à éviter comme solution de facilité |
| Storm Control | Limiter l'effet de certains volumes de broadcast/multicast/unknown unicast | N'empêche pas toujours une boucle et ne restaure pas à lui seul une topologie valide |

### 8.3 Où appliquer quelle protection ?

```text
             SW-DIST (racine STP attendue)
                    /          \
                   /            \
            trunk /              \ trunk
                 /                \
             SW-ACC-A           SW-ACC-B
              |    |             |    |
            PC-A  AP             PC-B  Imprimante
             ^                     ^
        Edge: PortFast + BPDU Guard selon le design

Root Guard : sur un port désigné où une racine en aval est interdite.
Loop Guard : sur les ports non-edge appropriés qui devraient recevoir des BPDUs.
```

### 8.4 BPDU Guard sur les ports edge

```text
interface range GigabitEthernet1/0/1-20
 description PORTS_TERMINAUX_A_VALIDER
 spanning-tree portfast
 spanning-tree bpduguard enable
```

Cet exemple de plage ne doit être utilisé que si tous les ports visés sont réellement des ports terminaux. N'applique pas cette plage à des uplinks ou à un port connecté à un switch en aval sans avoir validé la topologie. Si un appareil en aval émet des BPDUs, le port peut être bloqué et interrompre le service ; le comportement exact dépend de la plateforme.

### 8.5 Root Guard : rôle de la topologie

Root Guard est approprié sur certains ports désignés où l'administrateur veut garantir qu'une racine STP plus prioritaire ne soit pas acceptée depuis l'aval. Il ne faut pas le placer sur un lien qui doit légitimement participer au chemin vers le root bridge attendu.

### 8.6 Loop Guard : port qui cesse de recevoir des BPDUs

Sur certains liens redondants, l'absence inattendue de BPDUs peut amener un port à passer dans un état qui crée une boucle si aucune protection n'existe. Loop Guard aide à protéger les ports compatibles dans cette situation. Ce mécanisme doit être évalué avec la topologie STP, les EtherChannels et les fonctions propriétaires éventuellement utilisées.

### 8.7 Diagnostiquer un port err-disabled

```text
show interfaces status err-disabled
show errdisable recovery
show spanning-tree inconsistentports
show spanning-tree detail
show logging
```

La liste exacte dépend de la plateforme. Avant toute remise en service :

1. identifie la cause et l'heure de l'événement ;
2. inspecte l'appareil raccordé, le câblage et les journaux ;
3. vérifie si le port devrait être edge ou infrastructure ;
4. corrige la cause ;
5. réactive le port selon la procédure du site ;
6. valide la connectivité et confirme qu'aucun nouvel événement n'apparaît.

L'auto-récupération err-disable peut être utile pour certaines causes et certains sites, mais ne doit pas être configurée pour faire disparaître des alertes sans traitement. Le délai et les causes récupérables doivent être choisis explicitement.


## 9. Contrôler les tempêtes et les flux indésirables

### 9.1 Storm Control : limiter l'effet, pas traiter la cause

Une tempête peut être causée par une boucle L2, un équipement défectueux, une mauvaise configuration ou un trafic anormal. Storm Control limite, selon la plateforme, le volume de broadcast, multicast ou unknown unicast reçu par une interface. Il peut préserver une partie du service, mais le seuil dépend de la vitesse du lien, de la taille des trames, des applications et du comportement du matériel.

Exemple conceptuel Cisco IOS/IOS XE :

```text
interface GigabitEthernet1/0/7
 description PORT_TERMINAL_A_MESURER
 storm-control broadcast level 1.00 0.50
 storm-control multicast level 2.00 1.00
```

Les valeurs ne sont **pas** des recommandations universelles. Elles illustrent deux seuils haut/bas lorsque la plateforme supporte cette syntaxe. Vérifie les unités, le mode de calcul, l'action déclenchée et le support du modèle. Commence par mesurer le trafic normal ; un seuil trop faible peut gêner la découverte de services, le démarrage des postes ou certains flux multicast légitimes.

### 9.2 Distinguer trois catégories

- **Broadcast :** trames destinées à tous les hôtes du domaine de broadcast concerné.
- **Multicast :** trames destinées à un groupe, avec un comportement qui dépend des protocoles et de la configuration de l'équipement.
- **Unknown unicast :** trames unicast dont le switch ne connaît pas encore le port de destination dans sa table de commutation ; elles peuvent être diffusées dans le VLAN selon le fonctionnement du switch.

Ne traite pas ces catégories comme équivalentes. Par exemple, restreindre agressivement le multicast peut perturber une application ou un protocole de découverte légitime. Le snooping IGMP/MLD, lorsqu'il est pris en charge, gère un problème différent de celui de Storm Control.

### 9.3 Protected ports et isolation des clients

Certains switches proposent une fonction d'isolation locale, appelée par exemple protected port ou port isolation. Elle peut empêcher certains ports protégés de communiquer directement entre eux sur le même switch tout en leur laissant l'accès à un port non protégé, selon l'implémentation.

```text
PC invité A ----[port isolé]---+
                              |
PC invité B ----[port isolé]---+---- Switch ---- passerelle/pare-feu
                              |
                              +---- pas de communication directe A <-> B
```

Ne présume pas que cette fonction isole le trafic entre switches ou à travers toute la topologie. Le comportement inter-switch est spécifique au constructeur. Pour une segmentation cohérente, privilégie des VLAN, des ACL ou une architecture de politique réseau correctement conçue, et vérifie les limites de la fonction locale.

### 9.4 Multicast : IGMP/MLD snooping

IGMP snooping pour IPv4 et MLD snooping pour IPv6 permettent à un switch compatible d'apprendre quels ports ont besoin de certains groupes multicast. Une mauvaise configuration ou un querier absent peut affecter la distribution multicast. Avant de filtrer le multicast, vérifie les groupes attendus, les équipements qui envoient des rapports et la présence d'un querier là où il est nécessaire.

### 9.5 Vérifications

```text
show storm-control
show interfaces counters errors
show interfaces counters
show logging
```

Ces commandes sont des exemples ; elles varient selon les systèmes. Corrèle les compteurs de trafic avec l'heure de l'incident, les événements STP, les changements d'état des ports et les erreurs physiques. Le fait que Storm Control se déclenche peut être un indice de boucle ou de panne, pas seulement une preuve d'attaque.


## 10. Sécurité de la couche 2 pour IPv6

### 10.1 Pourquoi il faut traiter IPv6 explicitement

Un réseau qui semble IPv4-only peut néanmoins transporter IPv6, volontairement ou non, selon les systèmes et les équipements. Les contrôles ARP ne couvrent pas IPv6 : la découverte de voisinage utilise ICMPv6 Neighbor Discovery, et la configuration automatique peut dépendre des Router Advertisements (RA). Une politique conçue seulement autour de DHCPv4, ARP et ACL IPv4 peut donc laisser un chemin non prévu.

### 10.2 Mécanismes à connaître

| Mécanisme | Objectif | Précaution |
|---|---|---|
| RA Guard | Bloquer des Router Advertisements non autorisés sur des ports de terminaux | Vérifier l'implémentation, les extensions d'en-tête IPv6 et les limites documentées |
| DHCPv6 Guard | Contrôler quels ports peuvent émettre les messages de serveur DHCPv6 | Distinguer ports clients, serveurs et relais légitimes |
| IPv6 Neighbor Discovery Inspection / contrôle ND | Valider des messages de voisinage selon les fonctionnalités disponibles | La couverture varie nettement selon les plateformes |
| IPv6 Source Guard / SAVI ou mécanisme analogue | Limiter certaines usurpations d'adresses sources selon le binding disponible | Dépend de la méthode d'attribution et de l'implémentation |
| ACL IPv6 | Limiter les communications IPv6 entre zones et vers le plan de gestion | Une ACL IPv4 ne filtre pas le trafic IPv6 |

### 10.3 RA Guard : le scénario

Un poste malveillant peut tenter d'annoncer une fausse route par défaut. Les postes qui acceptent cette annonce peuvent envoyer leur trafic à un voisin non autorisé. RA Guard doit être placé et vérifié là où les annonces de routeur ne sont pas attendues, tout en conservant l'accès aux RA légitimes provenant du routeur ou de l'équipement designé.

```text
Routeur IPv6 autorisé -------- port de confiance / rôle routeur
         |                                      |
         | Router Advertisement légitime        v
         +------------------------------------ Switch
                                                |
                                  ports utilisateurs protégés
                                                X
                            RA émis par un poste non autorisé
```

Le comportement exact de RA Guard, notamment face à des extensions IPv6 ou à des paquets inhabituels, dépend de la conformité et de la version de l'implémentation. Une activation sans test peut aussi bloquer des annonces légitimes si les rôles d'interface sont mal identifiés.

### 10.4 Checklist IPv6 L2

- [ ] IPv6 est documenté : activé, désactivé explicitement ou requis par certains services.
- [ ] Les équipements qui peuvent émettre des RA sont identifiés.
- [ ] Les ports terminaux ne sont pas autorisés à fournir des annonces de routeur non prévues.
- [ ] DHCPv6 et les mécanismes de découverte sont couverts par la politique adaptée.
- [ ] Les ACL IPv6 correspondent à la politique IPv4 lorsque celle-ci est censée s'appliquer, sans supposer qu'elles sont identiques.
- [ ] Les journaux, compteurs et outils de supervision permettent de voir le trafic IPv6.
- [ ] Les tests couvrent DNS, passerelle, voisinage, applications et redondance lorsqu'IPv6 est utilisé.

**Prudence :** ne désactive pas IPv6 par réflexe comme unique mesure de sécurité si des systèmes en dépendent. Le but est une politique cohérente, connue et testée.


## 11. Sécurité du plan d'administration

La sécurité L2 ne se limite pas à l'attaque entre deux postes. Un switch compromis ou administrable depuis un VLAN utilisateur peut permettre un accès étendu au réseau. Le plan d'administration doit avoir son propre périmètre, des identités fortes et une traçabilité suffisante.

### 11.1 Réduire les services et les chemins d'administration

- Utilise une adresse de gestion dédiée et un VLAN de gestion restreint, ou une interface de gestion séparée lorsque la conception le prévoit.
- Autorise SSH plutôt que Telnet pour l'administration CLI ; désactive les services non requis.
- Utilise HTTPS pour l'interface Web si elle est nécessaire, avec des certificats et paramètres modernes compatibles avec l'équipement.
- Privilégie SNMPv3 avec authentification et confidentialité plutôt que les communautés SNMPv1/v2c ; limite les sources autorisées.
- Utilise AAA centralisé si possible, avec des comptes locaux de secours protégés et testés.
- Synchronise les horloges avec NTP sécurisé selon les capacités de la plateforme et conserve des journaux horodatés.
- Limite les sources d'administration par ACL ou pare-feu et sépare les comptes d'exploitation des comptes ordinaires.

### 11.2 Exemple conceptuel de restriction des accès

```text
Poste d'administration dédié
          |
          v
+--------------------------+
| VLAN / réseau de gestion |
+------------+-------------+
             |
      ACL / pare-feu
  sources d'administration
  explicitement autorisées
             |
             v
+--------------------------+
| Interfaces de gestion    |
| SSH / HTTPS / SNMPv3     |
| AAA + Syslog + NTP       |
+--------------------------+

VLAN utilisateurs et invités : aucune administration directe
```

Un VLAN de gestion sans filtrage n'est pas suffisant. À l'inverse, une ACL trop stricte peut bloquer le serveur AAA, la supervision ou l'accès de secours. Documente les flux administratifs réellement requis.

### 11.3 Exemple Cisco simplifié — SSH et accès VTY

```text
! Illustration seulement : adapter à la politique et à la version.
ip domain-name lab.example
crypto key generate rsa modulus 3072
ip ssh version 2
!
ip access-list standard MGMT-SOURCES
 permit 192.0.2.130
 deny any log
!
line vty 0 4
 transport input ssh
 access-class MGMT-SOURCES in
 login local
```

Le nom de domaine, la taille de clé acceptée, la syntaxe de génération de clé, la méthode d'authentification et les numéros de lignes VTY varient. Pour un déploiement réel, préfère AAA avec des identités individuelles et une stratégie de secours contrôlée lorsque c'est possible. Vérifie aussi les restrictions des interfaces de gestion hors bande si elles existent.

### 11.4 Gestion des secrets et de la configuration

- Ne place aucun secret réel dans un cours, un dépôt de code, un ticket public ou une capture d'écran.
- Remplace les valeurs `<SECRET>`, les adresses et les noms de domaine avant partage.
- Utilise des secrets uniques, une rotation prévue et un accès selon le moindre privilège.
- Sauvegarde les configurations dans un stockage protégé, contrôle qui peut les modifier et conserve un historique.
- Supprime les anciens comptes, clés et mécanismes d'administration lors des changements de personnel ou de rôle.
- Évite d'exposer les versions logicielles, l'inventaire et les protocoles de découverte inutilement aux ports non fiables.

### 11.5 CDP / LLDP

CDP et LLDP facilitent l'inventaire et le diagnostic des voisins, mais peuvent exposer des informations techniques. Active-les là où elles servent l'exploitation ; limite leur diffusion sur les ports qui n'en ont pas besoin et considère les informations de voisinage comme des données d'infrastructure. Le choix d'activer ou non ces protocoles doit rester cohérent avec les outils de support et les appareils connectés.


## 12. MACsec et protection des liens Ethernet

### 12.1 Quel problème MACsec résout-il ?

MACsec (IEEE 802.1AE) protège les trames Ethernet sur un lien compatible en apportant des fonctions de confidentialité, d'intégrité et de protection contre certaines formes de rejeu selon la suite cryptographique et la configuration employées. Il est utile lorsque la confidentialité et l'intégrité du trafic sur un segment Ethernet sont requises, par exemple sur certains liens d'accès ou d'infrastructure.

```text
Switch A [MACsec] ===== lien Ethernet protégé ===== [MACsec] Switch B
                       trames protégées

Un équipement intermédiaire non autorisé ne doit pas pouvoir lire ou modifier
le contenu protégé comme s'il s'agissait d'un lien Ethernet ordinaire.
```

### 12.2 Ce que MACsec ne fait pas

MACsec n'authentifie pas automatiquement tous les utilisateurs au niveau applicatif et ne remplace pas 802.1X, les ACL, la segmentation ou la sécurisation des équipements. Il protège le lien et dépend de clés, d'une politique de chiffrement et de capacités supportées. Si le trafic est déchiffré à un point du trajet, les contrôles des segments suivants restent nécessaires.

### 12.3 Conditions d'un déploiement réussi

- vérifier que les deux extrémités et les versions logicielles supportent la même méthode ;
- choisir un mode de gestion des clés compatible avec le design et les besoins d'authentification ;
- confirmer les suites cryptographiques, la politique de chiffrement et l'interopérabilité ;
- planifier la migration, le retour arrière et la supervision des sessions ;
- tester le comportement en cas de rotation des clés, de perte de session et de redémarrage ;
- mesurer les conséquences matérielles et opérationnelles sur les ports concernés.

### 12.4 Exemples d'usage

| Situation | Question à trancher |
|---|---|
| Lien entre deux switches d'un même local sécurisé | La confidentialité des trames sur ce lien est-elle exigée par la politique ? |
| Liaison Ethernet traversant une zone partagée | Le risque d'accès physique impose-t-il une protection cryptographique au niveau du lien ? |
| Port vers un appareil final | Le matériel supporte-t-il MACsec et quel modèle d'identité/clé convient à cet appareil ? |
| Lien d'opérateur ou interconnexion distante | MACsec est-il disponible de bout en bout, ou faut-il un autre mécanisme de protection du transport ? |

La disponibilité de MACsec dépend fortement du modèle, de la licence, de la version et du mode de configuration. N'inclus pas ce contrôle dans un standard de port sans vérifier le matériel réel.


## 13. Supervision, journaux et preuves

### 13.1 Une protection sans visibilité est difficile à exploiter

Le contrôle technique doit produire des éléments observables : état, compteurs, événements et contexte. Sans cela, une équipe ne peut pas distinguer un rejet attendu d'une mauvaise configuration, ni vérifier que les politiques sont toujours appliquées après une mise à jour ou un remplacement matériel.

### 13.2 Sources de télémétrie utiles

| Domaine | Éléments à collecter | Signaux intéressants |
|---|---|---|
| 802.1X / AAA | Résultat d'authentification, méthode EAP, VLAN, serveur sollicité | Échecs répétés, bascule serveur, certificat invalide, appareil inédit |
| DHCP Snooping | Ports trusted, bindings, compteurs de rejet, limites de débit | Absence de binding, offres rejetées, changement inhabituel de bail |
| DAI / IPSG | Compteurs et journaux de paquets rejetés | Adresse IP/MAC incohérente, hôte statique manquant, faux positif |
| STP | Root bridge, rôles de ports, changements de topologie | Changement de racine, ports inconsistent, BPDU inattendu |
| Interfaces | Débit, erreurs, drops, changements d'état | Tempête, câblage défectueux, dépassement de seuil |
| Plan de gestion | Connexions SSH, AAA, SNMP, changements de configuration | Tentatives depuis des sources inattendues, changement hors fenêtre |
| IPv6 | RA, DHCPv6, ND, compteurs des protections | Annonces provenant d'un port terminal, divergence IPv4/IPv6 |

### 13.3 Construire une alerte utile

Une alerte doit fournir : équipement, interface, VLAN, heure, type de contrôle, compteurs pertinents, événement précédent et lien vers une procédure de diagnostic. « Port bloqué » est insuffisant si l'équipe ne sait pas pourquoi ni comment identifier le terminal concerné.

### 13.4 Baseline et tendance

Mesure les volumes normaux de broadcast, multicast, authentifications, baux DHCP et changements STP. Les seuils doivent être basés sur le comportement réel et les limites des équipements, avec une marge documentée. Les alertes de sécurité doivent être distinguées des messages purement informatifs, sinon les incidents importants se perdent dans le bruit.

### 13.5 Conservation et protection des journaux

Les journaux peuvent révéler les noms d'hôtes, adresses réseau et habitudes d'accès. Restreins leur accès et leur conservation au besoin opérationnel et aux règles applicables. Synchronise les horloges ; sans horaire cohérent, la corrélation d'une panne ou d'un incident est incertaine. Les journaux centralisés doivent être protégés contre la modification non autorisée.


## 14. Méthode de diagnostic avancée

### 14.1 Toujours déterminer le premier point de rejet

Quand un poste n'obtient plus d'adresse, que la passerelle devient inaccessible ou qu'une authentification échoue, évite de désactiver toutes les protections. Procède par couches : physique → VLAN / trunk → authentification → DHCP → ARP/ND → filtrage IP → passerelle / routage → DNS → application.

```text
Lien physique up ?
   |
   +-- non --> câble, module, négociation, err-disable, port administrativement down
   |
   +-- oui --> VLAN/mode du port correct ?
                 |
                 +-- non --> access/trunk, VLAN autorisé, native VLAN, STP
                 |
                 +-- oui --> authentification autorisée ?
                               |
                               +-- non --> supplicant, EAP, RADIUS, certificat, VLAN de repli
                               |
                               +-- oui --> DHCP/ARP/ND/IP : quel contrôle rejette ?
                                               |
                                               +-- binding, ACL, IPSG, DAI, RA Guard, routage
```

### 14.2 Matrice rapide de dépannage

| Symptôme | Hypothèses fréquentes | Première vérification | À ne pas faire en premier |
|---|---|---|---|
| Pas d'adresse DHCP | VLAN erroné, trunk, serveur/relais, Snooping untrusted/trusted, limite de débit | Vérifier VLAN opérationnel, logs DHCP et binding | Trust tous les ports « pour tester » |
| DHCP fonctionne, mais pas de communication locale IPv4 | DAI rejette ARP, mauvais masque, table ARP incohérente | Compteurs DAI, entrée ARP, MAC table | Désactiver DAI sur tous les VLAN |
| DHCP fonctionne, trafic IP rejeté | IPSG ou ACL, binding absent, IP statique non déclarée | Binding IP/MAC/port et compteur de rejet | Retirer IPSG du switch entier sans identifier le port |
| Le port bloque après branchement d'un appareil | BPDU Guard, limite MAC, 802.1X, storm control, erreur physique | Cause err-disable, authentification et journaux | Réactiver en boucle sans corriger la cause |
| Accès accordé au mauvais VLAN | Politique AAA ou attributs de réponse, cache/session | Détails de session et trace RADIUS | Changer le VLAN global à l'aveugle |
| Lenteur générale après un brassage | Boucle, tempête broadcast, STP, liens agrégés incohérents | Root bridge, changements STP, compteurs interfaces | Désactiver STP pour voir si « ça repart » |
| IPv4 fonctionne mais une politique est contournée | IPv6 non documenté ou ACL incomplète | Routes, voisins, RA et règles IPv6 | Supposer que les ACL IPv4 couvrent IPv6 |
| Administration inaccessible | ACL, VLAN de gestion, AAA, route, SSH, NTP/certificat | Console/hors bande, route et logs AAA | Supprimer toutes les restrictions d'accès |

### 14.3 Séquence de dépannage DHCP Snooping / DAI

1. Confirmer que le client est dans le VLAN attendu et que le trunk transporte ce VLAN.
2. Vérifier que le port terminal est non trusted pour DHCP Snooping.
3. Vérifier que le chemin vers le serveur ou relais DHCP légitime est correctement conçu et que les interfaces nécessaires ont le bon rôle trust.
4. Examiner les journaux et les statistiques pour identifier un rejet précis.
5. Confirmer que la base de bindings contient le couple IP/MAC/VLAN/port attendu.
6. Si DHCP est correct mais ARP échoue, vérifier DAI et les éventuelles adresses statiques.
7. Si ARP fonctionne mais le trafic IP échoue, examiner IPSG puis les ACL et le routage.
8. Faire le test depuis un poste témoin autorisé et noter les résultats.

### 14.4 Exemples de commandes de contrôle

Les commandes suivantes sont des exemples de familles Cisco IOS/IOS XE ; vérifie la disponibilité exacte sur le système concerné.

```text
show interfaces status
show interfaces trunk
show vlan brief
show mac address-table dynamic
show spanning-tree summary
show spanning-tree detail
show ip dhcp snooping
show ip dhcp snooping binding
show ip arp inspection statistics
show authentication sessions
show logging
```

Un diagnostic utile associe les sorties à un moment précis et à l'interface concernée. Une capture d'écran isolée sans heure, topologie ni test de référence est souvent insuffisante pour expliquer un incident.


## 15. Laboratoires guidés

> **Note de compatibilité :** Packet Tracer, les appliances virtuelles et les switches physiques n'implémentent pas toujours les mêmes fonctions ni les mêmes syntaxes. Si une commande n'existe pas, vérifie la matrice de fonctionnalités de la maquette ; ne remplace pas silencieusement le mécanisme par une commande sans rapport.

### Laboratoire 1 — Baseline et durcissement d'un trunk

**Objectif :** limiter explicitement les VLAN d'un trunk et éliminer un port terminal dynamique.

**Topologie :** deux switches, un poste sur chaque switch, VLAN 10 et 20 ; VLAN 99 pour la gestion de laboratoire et VLAN 999 réservé.

**Étapes :**

1. Crée les VLAN requis sur les deux switches.
2. Configure un trunk statique entre switches, autorisant uniquement les VLAN nécessaires.
3. Choisis un VLAN natif réservé et applique la même valeur aux deux côtés.
4. Configure les ports des postes en access dans le VLAN attendu.
5. Vérifie l'état du trunk et teste uniquement les communications permises.
6. Simule en laboratoire une incohérence de VLAN natif ou une liste VLAN incomplète ; observe les symptômes et remets ensuite la configuration cohérente.

**Preuves :** `show interfaces trunk`, configuration des deux côtés, tests de connectivité et schéma final.

**Question :** pourquoi une valeur de VLAN natif identique ne suffit-elle pas si le trunk autorise des VLAN qui ne devraient pas traverser ce lien ?

### Laboratoire 2 — DHCP Snooping sans casser les clients

**Objectif :** bloquer les réponses DHCP venant d'un port terminal.

**Étapes :**

1. Note les paramètres IP normaux du client et identifie le port du serveur/relais DHCP légitime.
2. Active DHCP Snooping uniquement sur le VLAN de test.
3. Configure trusted uniquement sur le chemin légitime identifié.
4. Configure éventuellement une limite de débit prudente sur le port client.
5. Renouvelle le bail depuis le poste et vérifie sa présence dans la base.
6. Examine les journaux et les compteurs ; confirme que le trafic normal fonctionne.

**Preuves :** configuration, binding IP/MAC/VLAN/port et bail client obtenu.

**Critère de réussite :** client reçoit une adresse valide ; aucun port utilisateur n'a reçu trusted par facilité ; la règle de confiance est documentée.

### Laboratoire 3 — DAI et hôte statique

**Objectif :** comprendre pourquoi DAI peut rejeter l'ARP d'un poste sans binding DHCP.

**Étapes :**

1. Avec DHCP Snooping validé, active DAI sur le seul VLAN de test.
2. Vérifie la communication ARP entre deux clients DHCP.
3. Configure dans un laboratoire contrôlé un hôte à adresse statique et observe les différences.
4. Utilise la méthode supportée par la plateforme pour décrire le binding statique ou l'ARP ACL autorisée.
5. Recommence les tests et documente le résultat.

**Sécurité :** ne fais pas d'empoisonnement ARP sur un réseau de production. L'objectif est de comprendre la logique de validation et les journaux, pas de détourner le trafic d'un tiers.

### Laboratoire 4 — Port edge et BPDU Guard

**Objectif :** distinguer un port utilisateur d'un lien inter-switch.

**Étapes :**

1. Identifie les ports terminal et les uplinks dans la topologie.
2. Active PortFast/edge et BPDU Guard uniquement sur les ports terminaux compatibles.
3. Dans une maquette isolée, relie un switch de test sur un port protégé et observe l'événement résultant.
4. Identifie la cause, corrige le raccordement et restaure le port conformément à la procédure.
5. Vérifie que les trunks et le root bridge sont inchangés.

**Preuves :** liste des ports edge, état STP, journaux et procédure de récupération.

### Laboratoire 5 — Conception 802.1X (avec AAA de test)

**Objectif :** comprendre le chemin d'authentification avant un déploiement.

**Étapes :**

1. Prépare un switch compatible, un client configuré comme supplicant et un serveur RADIUS de laboratoire.
2. Déclare les clients RADIUS, la méthode et la politique côté serveur.
3. Configure un seul port test en mode contrôlé par authentification.
4. Teste un client autorisé, un certificat invalide ou un compte non autorisé.
5. Vérifie le résultat, le VLAN/politique et les journaux côté switch et AAA.
6. Teste le comportement lorsque le serveur principal n'est pas joignable, seulement selon la procédure de laboratoire.

**Preuves :** trace d'une session acceptée et refusée, méthode EAP, logs RADIUS et plan de retour arrière.

**Limite :** les commandes exactes dépendent du constructeur. Il est préférable de laisser ce laboratoire au niveau conception dans un simulateur qui ne supporte pas 802.1X.

### Laboratoire 6 — Storm Control et mesure

**Objectif :** construire un seuil à partir d'une mesure plutôt que d'une valeur arbitraire.

**Étapes :**

1. Mesure les compteurs broadcast/multicast/unicast anormal sur un port de test pendant un fonctionnement normal.
2. Identifie les usages attendus de ce port (poste, téléphone, point d'accès, caméra, etc.).
3. Choisis un seuil conservateur à partir de la documentation du constructeur et de la baseline.
4. Applique la politique en labo, puis mesure de nouveau.
5. Vérifie les compteurs, l'effet sur le client et les événements ; retire le réglage si le service légitime est perturbé.

**Preuves :** baseline, seuil choisi avec justification et test post-changement.

### Laboratoire 7 — Inspection de la posture IPv6

**Objectif :** vérifier qu'une politique L2 ne se limite pas à IPv4.

**Étapes :**

1. Identifie si IPv6 est présent et quels routeurs annoncent des préfixes.
2. Cartographie les RA, DHCPv6 et échanges de voisinage légitimes dans le labo.
3. Consulte les fonctionnalités IPv6 First-Hop Security prises en charge par la plateforme.
4. Configure RA Guard ou un mécanisme équivalent sur un port de test approprié.
5. Vérifie les annonces légitimes, les voisins et les journaux.
6. Documente ce qui est ou n'est pas protégé.

**Critère de réussite :** les annonces légitimes restent fonctionnelles et l'équipe peut expliquer la limite de la protection.

### Laboratoire 8 — Exploitation et diagnostic

**Objectif :** produire un dossier de dépannage réutilisable.

Le formateur ou la maquette fournit un incident : pas de DHCP, session 802.1X refusée, incohérence trunk ou port err-disabled. Le stagiaire doit relever l'heure, formuler une hypothèse, identifier les compteurs utiles, tester une cause à la fois et produire un compte rendu comportant cause racine, correction et prévention.

**Barème :** méthode et preuves (40 %), exactitude technique (30 %), retour arrière et gestion du risque (20 %), clarté de la documentation (10 %).


## 16. Projet de synthèse : sécuriser un petit campus

### 16.1 Contexte

Une organisation dispose de deux switches d'accès, d'un switch de distribution, d'ordinateurs gérés, de téléphones IP, d'imprimantes, d'un point d'accès et d'un réseau d'administration. Elle doit réduire le risque qu'un appareil inconnu accède au réseau interne, empêcher les faux serveurs DHCP, limiter l'usurpation ARP/IP, préserver une topologie STP stable et rendre les incidents visibles.

### 16.2 Livrables demandés

1. **Schéma logique :** VLAN, passerelles, trunks, chemins d'administration et frontières de confiance.
2. **Matrice de ports :** terminal, voix, IoT, AP, uplink, administration et ports inutilisés.
3. **Standard trunk :** VLAN autorisés, VLAN natif et contrôles STP avec justification.
4. **Politique d'identité :** 802.1X pour les appareils compatibles, décision MAB restrictive pour les appareils non compatibles, mode de fonctionnement si AAA tombe.
5. **Politique L2/IP :** DHCP Snooping, DAI, IPSG, exceptions statiques et politique IPv6.
6. **Supervision :** événements, compteurs, seuils et destinataires d'alertes.
7. **Plan de déploiement :** ordre, lots, mesures de validation et retour arrière.
8. **Jeu de tests :** trafic autorisé, trafic refusé, panne contrôlée d'un composant, validation après changement.

### 16.3 Architecture de référence simplifiée

```text
                          +------------------+
                          | Pare-feu / L3    |
                          | ACL inter-VLAN   |
                          +--------+---------+
                                   |
                         trunk VLAN nécessaire
                                   |
                         +---------+---------+
                         | Distribution       |
                         | racine STP prévue  |
                         +----+-----------+---+
                              |           |
                            trunk       trunk
                              |           |
                          +---+---+   +---+---+
                          | Accès A|   | Accès B|
                          +---+----+   +----+---+
                              |             |
                    PC / voix / IoT      PC / AP / IoT
                    802.1X ou MAB       policy par rôle

Contrôles sur le chemin : identité -> VLAN/politique -> DHCP/ARP/IP -> routage
Supervision transverse : AAA, STP, bindings, drops, syslog, configuration
```

### 16.4 Ordre de déploiement recommandé

1. Inventaire et mise à jour du schéma ; suppression des trunks et VLAN inutiles après validation.
2. Durcissement des ports inutilisés et des trunks, avec fenêtre de changement.
3. Activation graduelle de DHCP Snooping et validation des baux.
4. Activation de DAI, d'abord sur un VLAN pilote ; préparation des hôtes statiques.
5. Activation d'IP Source Guard par petits lots.
6. Définition des rôles STP et activation des protections adaptées.
7. Mise en place d'AAA et 802.1X sur un groupe pilote avant extension.
8. Contrôle IPv6 explicite et validation des services existants.
9. Centralisation des journaux, tests d'alertes et revue de la sauvegarde.
10. Revue post-déploiement et mise à jour du standard de configuration.

### 16.5 Critères d'acceptation

- aucun port utilisateur inutilement configuré comme trunk ;
- aucun VLAN superflu autorisé sur les uplinks ;
- les ports inutilisés sont désactivés ou traités selon une politique explicitement justifiée ;
- les terminaux reçoivent une politique correspondant à leur identité ou à leur catégorie ;
- les bindings DHCP et les contrôles ARP/IP correspondent aux appareils réellement présents ;
- STP possède une racine et des rôles de ports documentés ;
- IPv6 est traité selon une politique explicite ;
- les changements sont journalisés, vérifiables et réversibles ;
- le dossier contient les limites connues, les exceptions, les responsables et la date de prochaine revue.


## 17. Évaluation et corrigés

### 17.1 Questions

**Q1.** Pourquoi Port Security ne remplace-t-il pas 802.1X ?  
**Q2.** Quel est le risque principal si un port utilisateur est trusted pour DHCP Snooping ?  
**Q3.** Pourquoi DAI peut-il bloquer l'ARP d'un hôte statique ?  
**Q4.** Que doit-on vérifier avant d'activer IP Source Guard ?  
**Q5.** Pourquoi BPDU Guard convient-il aux ports edge mais pas aux trunks inter-switch ordinaires ?  
**Q6.** Storm Control corrige-t-il une boucle L2 ?  
**Q7.** Une ACL IPv4 suffit-elle à imposer une politique équivalente à IPv6 ?  
**Q8.** Quelle est la différence entre authentification 802.1X et décision d'autorisation réseau ?  
**Q9.** Pourquoi MAB doit-il généralement être associé à une politique restrictive ?  
**Q10.** Une interface configurée en trusted pour une fonctionnalité devient-elle automatiquement de confiance pour toutes les autres ?

### 17.2 Corrigé synthétique

1. Port Security limite les adresses MAC d'un port ; 802.1X permet une authentification et une décision de politique fondées sur une méthode et une identité. Ils ne répondent pas au même besoin.
2. Des messages DHCP provenant d'un appareil non autorisé peuvent traverser le contrôle et fournir une configuration trompeuse aux clients.
3. La base des bindings issue de DHCP Snooping peut ne pas contenir la correspondance IP/MAC/VLAN attendue pour le poste statique ; une méthode statique adaptée est requise.
4. Valider le service DHCP, le contenu de la base des bindings, les hôtes statiques, les VLAN concernés et la compatibilité de la plateforme.
5. Un port edge devrait joindre un terminal. Un BPDU inattendu peut révéler qu'un switch a été raccordé et qu'il faut protéger la topologie ; sur un trunk inter-switch, les BPDUs sont attendus.
6. Non. Storm Control peut limiter certains effets, mais il ne remplace pas la résolution de la cause de la boucle ni une configuration STP correcte.
7. Non. IPv6 possède ses propres adresses, messages de découverte et règles de filtrage. Il faut appliquer une politique IPv6 cohérente.
8. L'authentification vérifie une identité ou une preuve ; l'autorisation détermine le réseau et les privilèges qui lui sont accordés.
9. MAB identifie essentiellement l'appareil par son adresse MAC, qui peut être usurpée. La politique doit donc limiter l'appareil à un périmètre réduit.
10. Non. Les états trust sont propres à chaque mécanisme. Chaque interface doit être évaluée séparément pour DHCP Snooping, DAI, STP et toute autre protection.

### 17.3 Scénario d'analyse

Un poste reçoit un bail DHCP valide après l'activation de DHCP Snooping. Il ne peut ensuite joindre aucun voisin IPv4, mais les autres postes du VLAN fonctionnent.

**Démarche attendue :** vérifier VLAN, port et adresse reçue ; inspecter la table ARP et les compteurs DAI ; confirmer que le binding correspond à la MAC et au port du poste ; rechercher une entrée statique ou une politique DAI incompatible ; identifier le premier rejet ; corriger l'association appropriée puis refaire les tests locaux, passerelle, DNS et application. La solution n'est pas de désactiver simultanément DHCP Snooping, DAI et IP Source Guard.

### 17.4 Barème conseillé

| Compétence | Pondération |
|---|---:|
| Compréhension des mécanismes et de leurs limites | 20 % |
| Topologie et segmentation cohérentes | 15 % |
| Configuration sûre et adaptée au matériel | 20 % |
| Vérification opérationnelle et interprétation des compteurs | 20 % |
| Diagnostic avec preuves et cause racine | 15 % |
| Documentation, fenêtre de changement et rollback | 10 % |


## 18. Checklist d'exploitation

### Avant mise en production

- [ ] Le modèle, la version logicielle et la compatibilité des fonctions sont vérifiés.
- [ ] Les ports et leurs rôles sont inventoriés ; les exceptions ont un propriétaire.
- [ ] La liste de VLAN autorisés sur chaque trunk correspond au besoin réel.
- [ ] Le VLAN natif est cohérent sur les deux extrémités et n'héberge pas de terminaux ordinaires.
- [ ] La politique 802.1X et les cas MAB sont testés avec un serveur AAA disponible et indisponible selon le scénario prévu.
- [ ] DHCP Snooping fonctionne et la base des bindings est cohérente.
- [ ] DAI est testé avec les hôtes DHCP et statiques concernés.
- [ ] IP Source Guard est activé de façon progressive et validée.
- [ ] Les protections STP correspondent aux rôles de ports et au root bridge attendu.
- [ ] Les seuils Storm Control sont justifiés par une mesure et non copiés sans contexte.
- [ ] IPv6, y compris RA et DHCPv6, est couvert par une politique explicite.
- [ ] Le plan d'administration est séparé, filtré et journalisé.
- [ ] Les horloges, serveurs de journaux et alertes sont opérationnels.
- [ ] Une sauvegarde restaurable et un rollback testé sont disponibles.

### À chaque changement important

- [ ] Numéro de changement, heure, opérateur et interfaces concernées documentés.
- [ ] État initial et tests de référence conservés.
- [ ] Changement réalisé en lot limité.
- [ ] Tests fonctionnels et compteurs post-changement vérifiés.
- [ ] Aucun nouveau rejet ou changement STP non prévu.
- [ ] Configuration sauvegardée après validation.

### Revue périodique

- [ ] VLAN, trunks, interfaces et équipements inconnus réévalués.
- [ ] Exceptions IP statiques, MAB et ACL obsolètes supprimées ou reconfirmées.
- [ ] Comptes AAA, clés SSH, certificats et secrets renouvelés selon la politique.
- [ ] Journaux et alarmes examinés ; faux positifs et seuils réajustés avec preuve.
- [ ] Versions logicielles et avis de sécurité examinés dans le cadre du processus de gestion des correctifs.
- [ ] Le dossier d'exploitation correspond encore à la topologie réelle.


## 19. Glossaire

| Terme | Définition utile |
|---|---|
| 802.1X | Contrôle d'accès réseau fondé sur l'authentification d'un port ou d'un accès réseau |
| AAA | Authentication, Authorization, Accounting : authentification, autorisation et traçabilité |
| ARP | Protocole de résolution d'adresses IPv4 vers les MAC sur le réseau local |
| BPDU | Trame de contrôle utilisée par STP/RSTP |
| BPDU Guard | Protection d'un port edge contre la réception inattendue de BPDUs |
| DAI | Dynamic ARP Inspection, validation des messages ARP entrants |
| DHCP Snooping | Contrôle des messages DHCP et, sur certaines plateformes, apprentissage de bindings |
| EAP / EAPOL | Framework d'authentification et son transport sur le lien local |
| EAP-TLS | Méthode EAP s'appuyant sur TLS et des certificats |
| IPSG | IP Source Guard, contrôle des adresses IP sources sur une interface supportée |
| MACsec | Protection cryptographique des trames Ethernet sur un lien compatible |
| MAB | MAC Authentication Bypass, solution d'accès fondée sur une adresse MAC quand 802.1X n'est pas disponible |
| NAC | Network Access Control, architecture de contrôle d'accès réseau |
| Native VLAN | VLAN généralement associé au trafic non tagué d'un trunk 802.1Q |
| RA Guard | Contrôle visant à limiter les Router Advertisements IPv6 non autorisés |
| RADIUS | Protocole utilisé par de nombreuses architectures AAA réseau |
| Root Guard | Protection STP visant à empêcher une racine non souhaitée depuis un port donné |
| Storm Control | Limitation du volume de certaines catégories de trafic sur une interface |
| Supplicant | Client logiciel ou appareil demandant l'accès via 802.1X |
| Trunk | Lien qui transporte plusieurs VLAN, généralement avec marquage 802.1Q |
| Untrusted / Trusted | État de confiance d'une interface propre à une fonction de sécurité précise |
| VLAN de quarantaine | Segment restreint destiné à la remédiation ou au traitement d'appareils non conformes |


## 20. Références techniques

Les guides suivants sont des points de départ, pas une invitation à copier une configuration sans vérification. Consulte toujours le guide de la famille matérielle et de la version logicielle réellement utilisée.

1. **Cisco — Security Configuration Guide, Catalyst 9300, IOS XE 26.x** : guide de référence actuel pour plusieurs contrôles L2, dont Port Security, 802.1X, DAI, IP Source Guard et contrôle de trafic.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/26-x/configuration_guide/sec/b_26x_sec_9300_cg.html
2. **Cisco — Configuring Dynamic ARP Inspection, Catalyst 9300 / IOS XE 26.x** : dépendance à DHCP Snooping, ports trusted/untrusted, validation ARP et cas non-DHCP.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/26-x/configuration_guide/sec/b_26x_sec_9300_cg/configuring_dynamic_arp_inspection.html
3. **Cisco — Configuring IP Source Guard, Catalyst 9300 / IOS XE 26.x** : fonctionnement sur port L2 et usage des bindings IP/MAC/VLAN.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/26-x/configuration_guide/sec/b_26x_sec_9300_cg/configuring_ip_source_guard.html
4. **Cisco — Port Security, Catalyst 9300 / IOS XE 26.x** : types d'adresses sécurisées, violations, limites et compatibilités.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/26-x/configuration_guide/sec/b_26x_sec_9300_cg/port_security.html
5. **Cisco — Port-Based Traffic Control** : Storm Control et contrôles par port.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/26-x/configuration_guide/sec/b_26x_sec_9300_cg/configuring_port_based_traffic_control.html
6. **Cisco — IEEE 802.1X Port-Based Authentication, Catalyst 9300 / IOS XE 26.x** : authentification de port et restrictions de plateforme.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/26-x/configuration_guide/sec/b_26x_sec_9300_cg/configuring_ieee_802_1x_port_based_authentication.html
7. **Cisco — Troubleshoot DAI and IP Source Guard in Catalyst switches** : conseils pratiques pour diagnostiquer les rejets et les bindings.  
   https://www.cisco.com/c/en/us/support/docs/switches/lan-switch-software/222274-troubleshoot-dynamic-arp-inspection-dai.html
8. **IETF RFC 3580 — IEEE 802.1X Remote Authentication Dial In User Service (RADIUS) Usage Guidelines** : document informatif sur l'utilisation de RADIUS avec 802.1X.  
   https://datatracker.ietf.org/doc/html/rfc3580
9. **Cisco — Configuring IPv6 First Hop Security, Catalyst 9300 / IOS XE 17.18** : RA Guard, DHCPv6 Guard, Neighbor Discovery Inspection et protection des adresses sources IPv6.  
   https://www.cisco.com/c/en/us/td/docs/switches/lan/catalyst9300/software/release/17-18/configuration_guide/sec/b_1718_sec_9300_cg/configuring_ipv6_first_hop_security.html
10. **IETF RFC 7113 — Implementation Advice for IPv6 Router Advertisement Guard (RA-Guard)** : points de vigilance d'implémentation, notamment les techniques de contournement par en-têtes d'extension IPv6.  
    https://datatracker.ietf.org/doc/html/rfc7113
11. **IETF RFC 4861 — Neighbor Discovery for IP version 6 (IPv6)** : référence du protocole IPv6 Neighbor Discovery.  
    https://datatracker.ietf.org/doc/html/rfc4861


## Conclusion

La sécurité L2 intermédiaire n'est pas une collection de commandes à activer partout. Elle repose sur un design explicite : chaque port possède un rôle, chaque VLAN répond à un besoin, chaque mécanisme est activé dans les limites de la plateforme, et chaque exception est justifiée. Les tests doivent démontrer à la fois que les accès interdits sont bloqués et que les services autorisés continuent de fonctionner.

La meilleure preuve de maîtrise n'est pas la longueur de la configuration : c'est la capacité à expliquer **ce qui est contrôlé, où le contrôle s'applique, quelle donnée le mécanisme utilise, ce qui peut être bloqué à tort et comment revenir à un état sûr**.
