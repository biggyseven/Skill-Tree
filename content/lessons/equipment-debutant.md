# Équipements réseau de couche 1 et de couche 2 — Niveau débutant

> **Fichier :** `equipment-debutant.md`  
> **Niveau :** Débutant  
> **Prérequis :** notions de base sur un réseau local et les ordinateurs.  
> **Objectif :** identifier les équipements L1 et L2, comprendre leur rôle, distinguer un signal, une trame et un paquet, puis effectuer des contrôles simples sans confondre commutation et routage.

## 1. Pourquoi parler des couches L1 et L2 ?

Le modèle OSI est un modèle de référence qui aide à classer les fonctions réseau. Dans ce cours, L1 désigne la **couche physique** ; L2 désigne la **couche liaison de données**.

- **L1 — Physique :** transporte des symboles ou bits sur un support. On s’intéresse au câble, à la fibre, aux connecteurs, au module optique, au signal radio, au débit et à l’état du lien.
- **L2 — Liaison de données :** forme et traite des trames sur un lien ou dans un réseau ponté. Ethernet emploie des adresses MAC, et un switch L2 apprend où se trouvent les adresses MAC.
- **L3 — Réseau :** achemine des paquets IP entre réseaux. Cette fonction est principalement celle du routeur ou d’un commutateur de couche 3.

Un équipement réel peut remplir des fonctions de plusieurs couches. Un point d’accès Wi-Fi utilise un PHY radio (L1) et le mécanisme MAC 802.11 (L2), puis relie souvent les clients sans fil au LAN Ethernet.

## 2. Schéma 1 — Deux postes reliés par un switch

<svg xmlns="http://www.w3.org/2000/svg" width="980" height="365" viewBox="0 0 980 365" role="img" aria-labelledby="beg1-title beg1-desc" style="width:100%;max-width:980px;height:auto;display:block">
<title id="beg1-title">Communication d’un poste à un autre via un commutateur</title><desc id="beg1-desc">Deux postes se relient à un commutateur Ethernet. La couche 1 transporte les signaux, la couche 2 commute les trames en fonction des adresses MAC.</desc>
<defs><marker id="beg1-arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 Z" fill="#4de0c1"/></marker><style>.b1bg{fill:#0a1220}.b1card{fill:#151f32;stroke:#344660;stroke-width:1.5}.b1h{font:700 18px sans-serif;fill:#f1f5f9}.b1t{font:14px sans-serif;fill:#cbd5e1}.b1s{font:12px sans-serif;fill:#9fb0c8}.b1l{fill:none;stroke:#4de0c1;stroke-width:3;stroke-dasharray:9 7;marker-end:url(#beg1-arr);animation:beg1-flow 1.6s linear infinite}@keyframes beg1-flow{to{stroke-dashoffset:-32}}@media(prefers-reduced-motion:reduce){.b1l{animation:none}}</style></defs>
<rect class="b1bg" width="980" height="365" rx="18"/><text class="b1h" x="28" y="34">De l’interface au commutateur : les deux couches travaillent ensemble</text>
<rect class="b1card" x="28" y="82" width="220" height="116" rx="12"/><rect x="50" y="101" width="45" height="33" rx="3" fill="none" stroke="#60a5fa" stroke-width="2"/><path d="M72 134v8m-12 0h24" stroke="#60a5fa" stroke-width="2"/><text class="b1h" x="111" y="117">PC-A</text><text class="b1t" x="50" y="163">Carte réseau / NIC</text><text class="b1s" x="50" y="183">Adresse MAC source</text>
<rect class="b1card" x="380" y="99" width="220" height="88" rx="12"/><text class="b1h" x="490" y="133" text-anchor="middle">Switch Ethernet</text><text class="b1t" x="490" y="157" text-anchor="middle">Table MAC par VLAN</text><text class="b1s" x="490" y="175" text-anchor="middle">Décision de transfert L2</text>
<rect class="b1card" x="732" y="82" width="220" height="116" rx="12"/><rect x="754" y="101" width="45" height="33" rx="3" fill="none" stroke="#60a5fa" stroke-width="2"/><path d="M776 134v8m-12 0h24" stroke="#60a5fa" stroke-width="2"/><text class="b1h" x="815" y="117">PC-B</text><text class="b1t" x="754" y="163">Carte réseau / NIC</text><text class="b1s" x="754" y="183">Adresse MAC destination</text>
<path class="b1l" d="M248 140 H380"/><path class="b1l" d="M600 140 H732"/>
<rect x="28" y="225" width="445" height="103" rx="12" fill="#102b36" stroke="#267e86"/><text x="48" y="252" style="font:700 16px sans-serif;fill:#99f6e4">Couche 1 — Physique</text><text class="b1t" x="48" y="276">Connecteurs, câble, fibre, niveaux électriques</text><text class="b1t" x="48" y="299">ou signaux optiques/radio, débit négocié.</text>
<rect x="492" y="225" width="460" height="103" rx="12" fill="#1e2140" stroke="#6366f1"/><text x="512" y="252" style="font:700 16px sans-serif;fill:#c7d2fe">Couche 2 — Liaison de données</text><text class="b1t" x="512" y="276">Trames Ethernet, adresses MAC, apprentissage</text><text class="b1t" x="512" y="299">et décision du port de sortie dans le VLAN.</text>
<text class="b1s" x="28" y="350">Le switch n’a pas besoin de lire l’adresse IP pour commuter une trame Ethernet ordinaire.</text></svg>

### Lecture du schéma

1. Le signal passe physiquement par les interfaces et le câblage : c’est la partie L1.
2. Une carte réseau encapsule les données en trame Ethernet et ajoute des adresses MAC : c’est la partie L2.
3. Le switch examine la trame, utilise la table MAC dans le contexte du VLAN et sélectionne le ou les ports de sortie.
4. L’adresse IP n’est pas le critère ordinaire de commutation L2, même si un switch moderne peut également proposer des fonctions L3.

**À retenir :** un voyant de lien indique principalement qu’un lien physique a été établi ; il ne prouve pas qu’une configuration VLAN, une adresse IP ou un service applicatif fonctionne correctement.

## 3. Les équipements de couche 1

### 3.1. Carte réseau (NIC)

La carte réseau, intégrée à un ordinateur ou ajoutée sous forme de carte, fournit une interface physique et des fonctions de liaison de données. Une interface Ethernet possède généralement une adresse MAC et un transceiver/PHY adapté à son port. Elle peut fonctionner en cuivre, en fibre ou, selon le matériel, en radio.

Pannes fréquentes : adaptateur désactivé, pilote, câble défectueux, connecteur endommagé, mauvais transceiver, autonegotiation incohérente ou débit incompatible.

### 3.2. Répéteur et hub

Un **répéteur** régénère ou répète un signal. Un **hub Ethernet** historique est essentiellement un répéteur multiports : ce qu’il reçoit est répété vers les autres ports, sans table MAC ni décision de commutation.

Un hub crée un domaine partagé et, dans son modèle Ethernet classique, un domaine de collision partagé. Les switches modernes l’ont presque partout remplacé. En maintenance, on peut encore rencontrer de vieux hubs, mais il faut éviter de les choisir pour une nouvelle installation.

### 3.3. Câble cuivre à paires torsadées

Un lien cuivre Ethernet utilise des paires torsadées avec connecteurs adaptés. Les performances dépendent notamment de la catégorie et de la qualité du câble, de l’installation, des connecteurs, de la longueur, des perturbations et du type de PHY Ethernet.

- Un câble endommagé ou mal terminé peut entraîner des erreurs, une négociation à vitesse inférieure ou l’absence de lien.
- Dépasser la longueur prévue par la norme peut rendre la liaison non conforme et instable.
- La couleur d’un câble ne définit pas sa catégorie ni sa qualité ; se référer au marquage et à la documentation.
- Ne jamais confondre un câble réseau cuivre avec une simple rallonge téléphonique, un câble d’alarme ou un câble non certifié pour l’usage prévu.

### 3.4. Fibre optique et transceivers

La fibre transporte des impulsions optiques. Elle permet notamment des liaisons longues distances, des débits élevés et une isolation électrique entre extrémités. Il faut faire correspondre le type de fibre, le connecteur, la longueur d’onde, le transceiver et la distance.

- **Multimode (MMF) :** courante pour des liaisons de portée courte à moyenne adaptées au module, souvent dans les bâtiments ou centres de données.
- **Monomode (SMF) :** courante pour des portées plus longues et de nombreux liens de campus ou opérateur.
- **SFP/SFP+/QSFP et dérivés :** familles de formats de modules ; le format mécanique seul ne garantit pas la compatibilité optique ou électrique.

Ne jamais regarder directement dans une fibre ou un port optique. Inspecter et nettoyer les connecteurs avec les outils et procédures appropriés.

### 3.5. Panneau de brassage

Le panneau de brassage termine et organise les câbles horizontaux. C’est un élément passif : il ne commute pas les trames et n’amplifie pas le signal. Des cordons de brassage relient le panneau aux ports des switches.

Un mauvais repérage des prises et panneaux rallonge fortement le dépannage. Le nom de la prise, la position dans le rack, le port de switch, le VLAN attendu et le numéro du lien doivent être documentés.

### 3.6. Convertisseur de média

Un convertisseur cuivre-fibre adapte une interface physique à un autre média. Il peut résoudre une contrainte de distance ou d’immunité électrique, mais il ne corrige pas automatiquement une erreur de VLAN, de duplex, d’IP ou de routage. Les vitesses, la négociation, les longueurs d’onde et les deux côtés doivent être compatibles.

## 4. Les équipements de couche 2

### 4.1. Bridge et switch

Un **bridge** (pont) relie des segments de réseau au niveau L2. Un **switch Ethernet** moderne est généralement un pont multiports. Il apprend les adresses MAC source et associe ces adresses à un port, souvent dans un contexte de VLAN.

Lorsqu’une trame arrive :

1. Le switch apprend ou rafraîchit la MAC source sur le port d’entrée.
2. Il recherche la MAC de destination dans la table pour le VLAN concerné.
3. Si la destination est connue, il transmet vers le port associé, sauf si la destination correspond au port d’entrée.
4. Si la destination unicast est inconnue, il inonde généralement les ports éligibles du même VLAN, en excluant le port d’entrée.
5. Les trames multicast et broadcast suivent des règles spécifiques de transfert et, selon les fonctions disponibles, de filtrage.

La table MAC peut être appelée *CAM table*, *forwarding database* ou table de commutation selon le constructeur.

### 4.2. Adresse MAC

Une adresse MAC Ethernet courante est un identifiant de 48 bits, écrit par exemple `00:1A:2B:3C:4D:5E`. Les premières parties de certaines adresses peuvent être associées à un constructeur, mais les MAC peuvent aussi être administrées localement ou randomisées.

La MAC n’est pas une preuve d’identité. Elle peut être modifiée ou usurpée et ne remplace pas un mécanisme d’authentification.

### 4.3. Point d’accès Wi-Fi

Un point d’accès fournit un accès radio et relie généralement les stations Wi-Fi au réseau local. Il combine une partie physique radio et des fonctions de liaison de données. Le mode exact dépend de la configuration : pont transparent, mesh, contrôleur, mode client ou autres modes spécifiques.

Le Wi-Fi partage le spectre radio entre de nombreuses stations ; la capacité utile dépend entre autres des interférences, de la largeur de canal, du nombre de clients, de la génération Wi-Fi et de la qualité radio. L’indication « débit PHY » n’est pas le débit applicatif garanti.

### 4.4. Switch PoE

Un switch **PoE** peut fournir alimentation et données via un câble Ethernet compatible. Le switch est le PSE (*Power Sourcing Equipment*) ; un appareil alimenté, tel qu’un téléphone IP, une caméra ou un point d’accès, est le PD (*Powered Device*).

Tous les ports d’un switch ne sont pas nécessairement PoE. Vérifier les ports concernés, les classes d’alimentation, le budget total du châssis, les pertes de câble, la priorité PoE et les exigences du PD. Ne pas forcer une injection d’alimentation artisanale sur un port dont le comportement et le câblage ne sont pas connus.

## 5. Schéma 2 — Quel équipement opère à quelle couche ?

<svg xmlns="http://www.w3.org/2000/svg" width="980" height="390" viewBox="0 0 980 390" role="img" aria-labelledby="beg2-title beg2-desc" style="width:100%;max-width:980px;height:auto;display:block">
<title id="beg2-title">Équipements courants des couches 1 et 2</title><desc id="beg2-desc">Comparaison du répéteur, du concentrateur historique, du panneau de brassage, du point d’accès Wi-Fi et du switch. Le routeur intervient principalement à la couche 3.</desc>
<defs><style>.b2bg{fill:#0a1220}.b2c{fill:#151f32;stroke:#344660;stroke-width:1.3}.b2h{font:700 16px sans-serif;fill:#f1f5f9}.b2t{font:13px sans-serif;fill:#cbd5e1}.b2s{font:12px sans-serif;fill:#9fb0c8}.b2a{stroke:#4de0c1;stroke-width:2;stroke-dasharray:8 7;fill:none;animation:b2move 1.8s linear infinite}@keyframes b2move{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.b2a{animation:none}}</style></defs>
<rect class="b2bg" width="980" height="390" rx="18"/><text class="b2h" x="26" y="34">Les équipements ne remplissent pas tous la même fonction</text>
<rect class="b2c" x="24" y="62" width="294" height="112" rx="10"/><text class="b2h" x="42" y="88">Répéteur / concentrateur</text><text class="b2t" x="42" y="112">L1 : régénère ou répète le signal.</text><text class="b2t" x="42" y="134">Un hub partage le même domaine de</text><text class="b2t" x="42" y="153">collision ; technologie aujourd’hui obsolète.</text>
<rect class="b2c" x="343" y="62" width="294" height="112" rx="10"/><text class="b2h" x="361" y="88">Panneau de brassage</text><text class="b2t" x="361" y="112">Passif : organise et termine les câbles.</text><text class="b2t" x="361" y="134">Ne commute pas et n’amplifie pas</text><text class="b2t" x="361" y="153">les données.</text>
<rect class="b2c" x="662" y="62" width="294" height="112" rx="10"/><text class="b2h" x="680" y="88">Switch / commutateur</text><text class="b2t" x="680" y="112">L2 : apprend les MAC et choisit</text><text class="b2t" x="680" y="134">un port de sortie selon la table MAC</text><text class="b2t" x="680" y="153">et le VLAN.</text>
<rect class="b2c" x="24" y="198" width="452" height="112" rx="10"/><text class="b2h" x="42" y="224">Point d’accès Wi-Fi (AP)</text><text class="b2t" x="42" y="248">PHY radio (L1) + MAC 802.11 (L2) ;</text><text class="b2t" x="42" y="270">il relie généralement des clients sans fil</text><text class="b2t" x="42" y="289">au LAN, en pontant ou en relayant selon le mode.</text>
<rect class="b2c" x="503" y="198" width="453" height="112" rx="10"/><text class="b2h" x="521" y="224">Routeur (principalement L3)</text><text class="b2t" x="521" y="248">Transfère des paquets IP entre réseaux.</text><text class="b2t" x="521" y="270">Le distinguer du switch L2 : ce n’est pas</text><text class="b2t" x="521" y="289">la même table ni la même décision de transfert.</text>
<path class="b2a" d="M40 344 H940"/><text class="b2s" x="28" y="370">Repère : L1 transporte les signaux ; L2 traite les trames sur un lien ou un domaine ponté ; L3 route les paquets IP.</text></svg>

| Équipement | Fonction principale | Couche(s) concernée(s) | Limite à ne pas oublier |
|---|---|---|---|
| Câble, connecteur, transceiver | Transport du signal | L1 / interface physique | Ne choisit pas une destination MAC |
| Répéteur ou hub ancien | Régénère/répète | L1 | Ne commute pas par MAC |
| Panneau de brassage | Terminaison et organisation | Passif, raccordement physique | Ne traite pas le trafic |
| Switch L2 | Commutation de trames | L2, plus fonctions annexes selon modèle | N’est pas automatiquement une passerelle IP |
| Point d’accès | Accès WLAN et liaison au LAN | L1 radio + L2 | Ne remplace pas forcément le routeur |
| Routeur | Transfert de paquets entre réseaux | L3 | Utilise la table de routage, pas seulement la table MAC |

## 6. Duplex, vitesse et négociation

Une interface Ethernet moderne prend normalement en charge une ou plusieurs vitesses et des modes de duplex. Le duplex intégral permet l’émission et la réception simultanées sur le lien. La vitesse et le duplex doivent être compatibles aux deux extrémités.

**Pratique recommandée :** laisser l’autonégociation activée des deux côtés, sauf procédure documentée imposant une autre configuration. Fixer arbitrairement vitesse ou duplex sur une seule extrémité peut provoquer des erreurs ou une dégradation.

Les compteurs d’erreurs (CRC/FCS, symboles, pertes de lien, erreurs d’alignement selon l’interface) orientent le diagnostic, mais leur interprétation dépend de la plateforme et du PHY.

## 7. Travaux pratiques guidés

### TP 1 — Relier deux postes au switch

1. Connecter chaque poste à un port d’accès du switch.
2. Vérifier le voyant de lien et l’état de l’interface des deux postes.
3. Configurer deux adresses du même sous-réseau pour un test IP, par exemple `192.168.50.10/24` et `192.168.50.20/24`, dans un laboratoire isolé.
4. Tester avec `ping`.
5. Si le ping échoue, vérifier le câble, le VLAN, les adresses, les pare-feu et la prise en charge d’ICMP avant de conclure à une panne du switch.

### TP 2 — Commandes de diagnostic

**Windows**

```powershell
ipconfig /all
getmac /v
arp -a
ping 192.168.50.20
```

**Linux**

```bash
ip -br link
ip -br address
ip neigh
ping -c 4 192.168.50.20
```

Sur un système Linux qui possède `ethtool` et où les droits le permettent :

```bash
sudo ethtool eth0
```

Remplacer `eth0` par le nom réel de l’interface. Les commandes d’hôte ne montrent pas nécessairement la totalité de la table MAC du switch administrable ; cette dernière se consulte sur le switch ou dans son outil de gestion.

## 8. Méthode débutante de dépannage

| Observation | Causes possibles | Prochaine vérification |
|---|---|---|
| Aucun voyant de lien | Câble, port désactivé, alimentation, mauvais module | Tester un câble connu, observer l’état du port |
| Lien actif mais pas d’accès au LAN | VLAN incorrect, erreur IP, port isolé, sécurité | Vérifier l’adresse, le masque et le VLAN du port |
| Débit inférieur aux attentes | Câble limité ou endommagé, négociation, congestion | Contrôler vitesse, erreurs et statistiques |
| Certains appareils seulement échouent | Port/VLAN, authentification, compatibilité PoE, pilote | Comparer un poste sain et un poste en panne |
| Wi-Fi faible | Couverture, canal, interférences, emplacement de l’AP | Comparer signal, canal, débit PHY et charge |

Une seule observation n’identifie pas toujours la panne. Procéder du physique vers la liaison de données, puis vers l’IP et le service.

## 9. Quiz et corrigé

**Q1.** Quel équipement apprend les MAC et enregistre un port de sortie ?  
**Q2.** Le panneau de brassage est-il un switch ?  
**Q3.** Un voyant de lien allumé prouve-t-il que le VLAN est correct ?  
**Q4.** Le routeur est-il essentiellement un équipement L2 ?  
**Q5.** Que signifie PD dans le vocabulaire PoE ?

**Réponses :**

1. Le switch L2.
2. Non. C’est un élément passif de terminaison et d’organisation.
3. Non. Il indique principalement qu’une liaison physique a été établie.
4. Non. Sa fonction principale est le routage L3, même si des routeurs utilisent aussi des fonctions L2.
5. *Powered Device*, l’appareil alimenté.

## 10. À retenir

- L1 concerne les signaux, les supports et l’établissement physique du lien.
- L2 concerne les trames et les adresses MAC ; le switch apprend la source puis transfère vers le port approprié.
- Un hub répète, un switch commute, un routeur route.
- Le point d’accès combine souvent le physique radio et la liaison de données WLAN.
- La puissance PoE dépend du standard, du PSE, du PD, du câblage et du budget d’alimentation.
- Le diagnostic doit commencer par les observations physiques puis examiner la commutation et enfin les paramètres IP.

## Références techniques

- [IEEE 802.3 — Ethernet Working Group](https://www.ieee802.org/3/) : famille de normes Ethernet, couches physiques et MAC.
- [IEEE 802.1Q-2022 — Bridges and Bridged Networks](https://standards.ieee.org/ieee/802.1q/10323/) : pontage et VLAN ; consulter les amendements applicables.
- [IEEE 802.1AX-2020 — Link Aggregation](https://standards.ieee.org/ieee/149/6768/) : agrégation de liens.
- [IEEE 802.1AB-2026 — Connectivity Discovery](https://standards.ieee.org/ieee/802.1AB/11787/) : découverte de voisins LLDP.
- [IEEE 802.11-2024 — Wireless LAN MAC and PHY](https://standards.ieee.org/ieee/802.11/10548/) : réseau local sans fil.
- [IEEE 802.1X-2020 — Port-Based Network Access Control](https://standards.ieee.org/ieee/C2/10774/802.1X/7345/) : contrôle d’accès par port.
- [IEEE/ISO/IEC 8802-3:2026 — Ethernet](https://www.iso.org/standard/89414.html) : édition ISO/IEC/IEEE publiée en août 2026.
- [IEEE 802.3bt — alimentation PoE sur quatre paires](https://standards.ieee.org/ieee/8802-3_2021_Amd2/10811/).

> Les pages de standards servent à vérifier l’édition et le statut. Pour une installation contractuelle, utiliser le texte normatif applicable, les prescriptions du pays, les règles du bâtiment, ainsi que les documents du constructeur ; ne pas déduire une conformité complète à partir de ce cours seul.
