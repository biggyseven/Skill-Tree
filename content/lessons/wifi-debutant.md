<style>
.wifi-flow{stroke-dasharray:9 7;animation:wifiFlow 1.7s linear infinite}
@keyframes wifiFlow{to{stroke-dashoffset:-32}}
@media(prefers-reduced-motion:reduce){.wifi-flow{animation:none;stroke-dasharray:none}}
</style>

# Wi-Fi 802.11 — Niveau Débutant

**Niveau :** Débutant — **Parcours :** Réseaux informatiques — **Prérequis :** notions élémentaires d’adresse IP et de réseau local.

## Objectifs pédagogiques

À la fin de ce cours, tu pourras expliquer la différence entre Wi-Fi et Internet, reconnaître les principaux éléments d’un réseau sans fil, comprendre les bandes de fréquences et les canaux, suivre les grandes étapes de connexion d’un appareil, choisir des réglages de sécurité raisonnables et mener un premier diagnostic méthodique.

Tu n’as pas besoin de connaître les équations radio pour commencer. L’objectif est de comprendre ce qui se passe, de savoir quels indices regarder et d’éviter les conclusions trop rapides du type « le Wi-Fi est mauvais ».

## 1. Le Wi-Fi, c’est quoi exactement ?

Le **Wi-Fi** est une famille de technologies de réseau local sans fil fondées sur les normes IEEE 802.11. Elle permet à un ordinateur, un téléphone, une imprimante ou un autre appareil de communiquer par radio avec un point d’accès et, au-delà, avec le réseau local ou Internet.

Il faut distinguer trois notions :

- **Wi-Fi :** la liaison réseau radio entre l’appareil et le point d’accès (ou un autre mode 802.11).
- **Réseau local (LAN/WLAN) :** l’ensemble des équipements et des règles qui permettent aux appareils de communiquer dans une organisation ou un logement. Un LAN sans fil est souvent appelé WLAN.
- **Internet :** le réseau mondial auquel le réseau local peut donner accès à travers un routeur et un fournisseur d’accès.

Un appareil peut donc être connecté au Wi-Fi sans avoir accès à Internet. Par exemple, il peut être correctement associé au point d’accès mais ne pas recevoir d’adresse IP, ou le routeur peut avoir perdu la connexion du fournisseur d’accès.

### Une analogie simple

Imagine une gare : le **point d’accès** est comme une porte d’entrée vers le réseau local, le **Wi-Fi** est le moyen radio d’atteindre cette porte, le **routeur** dirige les échanges vers d’autres réseaux, et **Internet** est le réseau extérieur. Être arrivé dans la gare ne signifie pas automatiquement que le train prévu circule.

### Wi-Fi et données mobiles : ne pas confondre

Le Wi-Fi utilise une infrastructure locale radio, généralement reliée par Ethernet au réseau de l’entreprise ou du foyer. La 4G/5G utilise le réseau d’un opérateur mobile. Un téléphone peut basculer entre les deux, mais les mécanismes d’accès et les équipements d’infrastructure sont différents.

## 2. Les composants d’un réseau Wi-Fi

### 2.1 Le client ou la station

Une **station** (*STA*) est tout appareil qui participe à un réseau 802.11 : ordinateur portable, smartphone, tablette, terminal de caisse, caméra, imprimante ou objet connecté. La station possède une interface radio avec des capacités précises : bandes prises en charge, normes 802.11, largeur de canal, nombre de flux spatiaux et méthodes de sécurité.

Deux appareils placés dans la même pièce peuvent donc obtenir des résultats différents. Leurs antennes, leur puissance d’émission, leurs pilotes, leur position et leurs capacités ne sont pas nécessairement identiques.

### 2.2 Le point d’accès (AP)

Le **point d’accès** (*Access Point*, AP) fournit une cellule radio Wi-Fi et fait le lien entre les stations et le réseau local. Il diffuse les informations qui permettent aux clients de découvrir le réseau, négocie les paramètres radio et transporte les trames 802.11 entre les clients et l’infrastructure.

Un AP professionnel est souvent relié par un câble Ethernet à un commutateur. Il peut être alimenté par **PoE** (*Power over Ethernet*), qui fait passer l’alimentation et les données sur le même câble compatible. Certains points d’accès sont gérés par un contrôleur, d’autres par le cloud ou de manière autonome.

### 2.3 Routeur, modem et pare-feu

Ces rôles peuvent se trouver dans un seul boîtier domestique, mais ils restent différents :

- Le **commutateur Ethernet** relie les appareils d’un même réseau local filaire.
- Le **routeur** transmet les paquets entre réseaux IP différents.
- Le **pare-feu** applique des règles pour autoriser ou bloquer des flux.
- Le **modem ou terminal d’accès** fournit l’interface vers le réseau du fournisseur, selon la technologie.

Un boîtier vendu comme « routeur Wi-Fi » peut intégrer un point d’accès, un commutateur, un routeur, un serveur DHCP et parfois un modem. C’est pourquoi il faut regarder les fonctions, pas uniquement le nom commercial.

### 2.4 Schéma d’un réseau courant

<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="390" viewBox="0 0 900 390" role="img" aria-label="Chemin entre Internet, routeur, commutateur, point d'accès et clients Wi-Fi" style="width:100%;height:auto;background:#090d14;border-radius:14px" font-family="Arial,Helvetica,sans-serif">
<defs><marker id="wf1arr" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#55d6ff"/></marker><marker id="wf1arrg" markerWidth="9" markerHeight="9" refX="7" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 Z" fill="#5be49b"/></marker></defs>
<rect x="22" y="132" width="132" height="84" rx="12" fill="#13243a" stroke="#55d6ff" stroke-width="2"/><text x="88" y="166" fill="#f1f6ff" font-size="18" text-anchor="middle" font-weight="700">Internet</text><text x="88" y="190" fill="#a9c2db" font-size="12" text-anchor="middle">réseau externe</text>
<rect x="208" y="132" width="142" height="84" rx="12" fill="#172b43" stroke="#55d6ff" stroke-width="2"/><text x="279" y="164" fill="#f1f6ff" font-size="17" text-anchor="middle" font-weight="700">Routeur</text><text x="279" y="188" fill="#a9c2db" font-size="12" text-anchor="middle">passage IP</text>
<rect x="406" y="132" width="142" height="84" rx="12" fill="#172b43" stroke="#55d6ff" stroke-width="2"/><text x="477" y="164" fill="#f1f6ff" font-size="17" text-anchor="middle" font-weight="700">Switch</text><text x="477" y="188" fill="#a9c2db" font-size="12" text-anchor="middle">réseau Ethernet</text>
<rect x="604" y="132" width="132" height="84" rx="12" fill="#123329" stroke="#5be49b" stroke-width="2"/><text x="670" y="164" fill="#effff7" font-size="17" text-anchor="middle" font-weight="700">Point d’accès</text><text x="670" y="188" fill="#b8e8d1" font-size="12" text-anchor="middle">Wi-Fi / 802.11</text>
<rect x="762" y="36" width="116" height="76" rx="12" fill="#20283a" stroke="#a5b4fc" stroke-width="2"/><text x="820" y="65" fill="#f1f5ff" font-size="16" text-anchor="middle" font-weight="700">Laptop</text><text x="820" y="87" fill="#c5d1f6" font-size="12" text-anchor="middle">client radio</text>
<rect x="762" y="247" width="116" height="76" rx="12" fill="#20283a" stroke="#a5b4fc" stroke-width="2"/><text x="820" y="276" fill="#f1f5ff" font-size="16" text-anchor="middle" font-weight="700">Téléphone</text><text x="820" y="298" fill="#c5d1f6" font-size="12" text-anchor="middle">client radio</text>
<path d="M154 174 H202" stroke="#55d6ff" stroke-width="3" fill="none" marker-end="url(#wf1arr)"/><path d="M350 174 H400" stroke="#55d6ff" stroke-width="3" fill="none" marker-end="url(#wf1arr)"/><path d="M548 174 H598" stroke="#55d6ff" stroke-width="3" fill="none" marker-end="url(#wf1arr)"/>
<path d="M736 151 C780 147 784 113 803 112" stroke="#5be49b" stroke-width="3" fill="none" marker-end="url(#wf1arrg)"/><path d="M736 198 C780 207 784 247 803 247" stroke="#5be49b" stroke-width="3" fill="none" marker-end="url(#wf1arrg)"/><path d="M803 101 C785 122 782 145 736 164" stroke="#5be49b" stroke-width="2" opacity=".65" fill="none" marker-end="url(#wf1arrg)"/><path d="M803 258 C784 245 783 216 736 189" stroke="#5be49b" stroke-width="2" opacity=".65" fill="none" marker-end="url(#wf1arrg)"/>
<path d="M160 174 H201 M357 174 H399 M555 174 H597" stroke="#55d6ff" stroke-width="3" fill="none" class="wifi-flow"/>
<path d="M746 144 C777 137 787 112 802 107" stroke="#5be49b" stroke-width="3" fill="none" class="wifi-flow"/><path d="M746 204 C779 216 788 250 802 260" stroke="#5be49b" stroke-width="3" fill="none" class="wifi-flow"/>
<text x="280" y="113" fill="#9fb3ca" font-size="12" text-anchor="middle">liaison filaire / IP</text><text x="477" y="113" fill="#9fb3ca" font-size="12" text-anchor="middle">liaison Ethernet</text><text x="679" y="239" fill="#8ee8b9" font-size="12" text-anchor="middle">ondes radio</text>
<text x="450" y="365" fill="#8d9bb0" font-size="12" text-anchor="middle">Schéma pédagogique : un boîtier domestique peut regrouper plusieurs fonctions.</text>
</svg>
</div>

Les données d’un client Wi-Fi passent par radio jusqu’à l’AP. Si la destination est un service sur Internet, elles continuent généralement sur le réseau filaire vers le routeur. Pour une ressource située sur le même réseau local, le routeur n’est pas forcément traversé : cela dépend de la destination et de la conception du réseau.

## 3. Les notions essentielles : SSID, BSSID, cellule et roaming

### SSID : le nom du réseau

Le **SSID** (*Service Set Identifier*) est le nom que l’utilisateur voit dans la liste des réseaux : par exemple `Bureau-Invites` ou `Maison-WiFi`. Il peut être commun à plusieurs points d’accès pour faciliter la mobilité. Masquer le SSID n’est pas une mesure de sécurité fiable : le nom peut encore être découvert dans certains échanges radio.

### BSSID : l’identifiant d’une cellule radio

Le **BSSID** identifie une Basic Service Set, généralement représentée par l’adresse MAC radio d’un BSS. Deux AP peuvent annoncer le même SSID mais avoir des BSSID différents. Un AP à plusieurs radios ou plusieurs WLAN peut utiliser plusieurs BSSID. Pour dépanner un appareil qui se connecte au mauvais AP, le BSSID est souvent plus utile que le seul nom du réseau.

### Cellule radio et itinérance

Une cellule est la zone dans laquelle une radio permet une communication exploitable avec un AP. Les cellules se chevauchent souvent volontairement dans les réseaux multi-AP. Le **roaming** est le passage d’un client d’un AP à un autre au sein du réseau. Ce passage est piloté en grande partie par le client, avec des mécanismes 802.11 et des optimisations éventuelles (par exemple 802.11k/v/r selon la compatibilité et la configuration).

Avoir deux AP portant le même SSID ne garantit pas un roaming parfait. La configuration de sécurité doit être cohérente, le réseau doit permettre la continuité des sessions et la couverture doit être étudiée. Un client peut rester « collé » trop longtemps à un AP faible ; ce comportement dépend aussi du système et du pilote du client.

### Schéma simplifié du roaming

<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" width="880" height="330" viewBox="0 0 880 330" role="img" aria-label="Itinérance d’un client d’un point d’accès Wi-Fi vers un autre" style="width:100%;height:auto;background:#090d14;border-radius:14px" font-family="Arial,Helvetica,sans-serif">
<defs><marker id="wf7blue" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#55d6ff"/></marker><marker id="wf7green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#5be49b"/></marker></defs>
<text x="28" y="34" fill="#edf5ff" font-size="19" font-weight="700">Roaming : le client change de point d’accès</text>
<rect x="52" y="82" width="220" height="92" rx="12" fill="#123329" stroke="#5be49b" stroke-width="2"/><text x="162" y="112" fill="#effff7" font-size="18" font-weight="700" text-anchor="middle">AP-A</text><text x="162" y="136" fill="#b8e8d1" font-size="13" text-anchor="middle">BSSID A</text><text x="162" y="155" fill="#b8e8d1" font-size="12" text-anchor="middle">Cellule 1</text>
<rect x="608" y="82" width="220" height="92" rx="12" fill="#123329" stroke="#5be49b" stroke-width="2"/><text x="718" y="112" fill="#effff7" font-size="18" font-weight="700" text-anchor="middle">AP-B</text><text x="718" y="136" fill="#b8e8d1" font-size="13" text-anchor="middle">BSSID B</text><text x="718" y="155" fill="#b8e8d1" font-size="12" text-anchor="middle">Cellule 2</text>
<rect x="343" y="196" width="194" height="72" rx="12" fill="#20283a" stroke="#a5b4fc" stroke-width="2"/><text x="440" y="225" fill="#f1f5ff" font-size="16" font-weight="700" text-anchor="middle">Client mobile</text><text x="440" y="246" fill="#cad4f4" font-size="12" text-anchor="middle">même SSID possible</text>
<path d="M356 222 C288 210 252 183 220 174" stroke="#55d6ff" stroke-width="3" fill="none" marker-end="url(#wf7blue)"/><path d="M524 222 C591 208 628 183 660 174" stroke="#5be49b" stroke-width="3" fill="none" marker-end="url(#wf7green)"/><path d="M356 222 C288 210 252 183 220 174" stroke="#55d6ff" stroke-width="3" fill="none" class="wifi-flow"/><path d="M524 222 C591 208 628 183 660 174" stroke="#5be49b" stroke-width="3" fill="none" class="wifi-flow"/>
<path d="M272 128 H603" stroke="#8b9ab0" stroke-width="2" stroke-dasharray="5 6" fill="none"/><text x="440" y="116" fill="#aab9cc" font-size="12" text-anchor="middle">zone de recouvrement possible</text>
<text x="440" y="296" fill="#f2f5ff" font-size="14" font-weight="700" text-anchor="middle">Le client décide du moment du changement selon ses algorithmes et les informations disponibles.</text><text x="440" y="316" fill="#91a3b9" font-size="12" text-anchor="middle">Même SSID ne signifie pas même BSSID ; le roaming dépend aussi de la sécurité et du réseau amont.</text>
</svg>
</div>

## 4. Les bandes de fréquences et les canaux

Le Wi-Fi transporte les informations sur des ondes électromagnétiques. Les bandes les plus connues sont **2,4 GHz**, **5 GHz** et, lorsque la réglementation locale ainsi que les équipements le permettent, **6 GHz**.

### 4.1 Bande 2,4 GHz

Points forts : portée souvent meilleure à puissance et conditions comparables, et compatibilité avec de nombreux appareils anciens ou IoT.

Limites : bande très sollicitée par le Wi-Fi, le Bluetooth et d’autres équipements radio ; peu de place pour des canaux larges ; un réseau voisin ou une source d’interférences peut perturber les transmissions. Les canaux disponibles et les largeurs autorisées dépendent du domaine réglementaire.

### 4.2 Bande 5 GHz

Elle propose généralement davantage de canaux et permet des largeurs de canal plus importantes. Elle est souvent un bon compromis entre débit et couverture. À puissance et conditions comparables, les ondes à fréquence plus élevée sont en général davantage atténuées par les obstacles, mais la portée réelle dépend du bâtiment, de la puissance autorisée, de l’antenne, de l’appareil et des interférences.

Certains canaux 5 GHz sont des canaux **DFS** (*Dynamic Frequency Selection*). Selon la réglementation, l’équipement doit détecter certains radars et peut être contraint de changer de canal. Un changement de canal n’indique donc pas toujours une panne.

### 4.3 Bande 6 GHz et Wi-Fi 6E / 7

Le Wi-Fi 6E étend les capacités du Wi-Fi 6 (802.11ax) à la bande 6 GHz là où son utilisation est autorisée. Wi-Fi 7 correspond à 802.11be et apporte notamment le *Multi-Link Operation* (MLO) ainsi que la possibilité de canaux allant jusqu’à 320 MHz dans les conditions prévues par la norme. Ces possibilités demandent un client et un point d’accès compatibles et dépendent des règles locales. Ne suppose pas qu’un canal 6 GHz est utilisable dans chaque pays ni par tout appareil.

### 4.4 Bande, canal et largeur : trois termes différents

- **Bande** : plage globale de fréquences (par exemple 5 GHz).
- **Canal** : position d’exploitation choisie dans cette bande.
- **Largeur de canal** : quantité de spectre occupée, souvent 20, 40, 80 ou 160 MHz selon la bande, la norme et les capacités des équipements ; 320 MHz existe avec certaines configurations Wi-Fi 7 en 6 GHz.

Une largeur plus grande peut augmenter le débit potentiel, mais elle occupe davantage de spectre, réduit le nombre de canaux réutilisables et peut être plus exposée à la congestion. « Le canal le plus large est toujours le meilleur » est donc une mauvaise règle universelle.

### 4.5 Comment choisir un canal sans règle magique

Dans une maison, commence par les réglages recommandés par le fabricant ou un canal automatique qui fonctionne correctement. Si les performances sont mauvaises, relève les canaux voisins avec un outil de diagnostic, puis fais un changement à la fois et mesure le résultat. En 2,4 GHz, 20 MHz est souvent le choix prudent dans un environnement dense. Les combinaisons fréquemment citées comme 1/6/11 sont valables dans certains domaines réglementaires et plans à 20 MHz ; elles ne doivent pas être appliquées aveuglément à chaque pays ou largeur.

Ne confonds pas **canal occupé** et **signal puissant**. Un signal d’un autre réseau peut être fort mais peu actif, alors qu’un signal moyen très actif peut occuper beaucoup de temps d’antenne. Les mesures de congestion, de bruit et les tests réels aident à décider.

### Illustration conceptuelle des trois bandes

<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" width="880" height="300" viewBox="0 0 880 300" role="img" aria-label="Comparaison conceptuelle des bandes Wi-Fi 2,4, 5 et 6 GHz" style="width:100%;height:auto;background:#090d14;border-radius:14px" font-family="Arial,Helvetica,sans-serif">
<text x="30" y="35" fill="#edf5ff" font-size="19" font-weight="700">Bandes Wi-Fi : compromis, pas classement absolu</text>
<text x="30" y="64" fill="#9cafc5" font-size="12">Vue pédagogique — disponibilité, puissance et canaux varient selon le pays.</text>
<text x="40" y="112" fill="#f4f7ff" font-size="16" font-weight="700">2,4 GHz</text><rect x="180" y="88" width="265" height="38" rx="8" fill="#233b5b" stroke="#55d6ff" stroke-width="2"/><rect x="180" y="88" width="265" height="38" rx="8" fill="#55d6ff" opacity=".08"/><text x="195" y="111" fill="#d9f6ff" font-size="13">Portée utile / forte cohabitation</text>
<text x="40" y="174" fill="#f4f7ff" font-size="16" font-weight="700">5 GHz</text><rect x="180" y="150" width="365" height="38" rx="8" fill="#244a3c" stroke="#5be49b" stroke-width="2"/><text x="195" y="173" fill="#ddfff0" font-size="13">Compromis entre capacité et portée</text>
<text x="40" y="236" fill="#f4f7ff" font-size="16" font-weight="700">6 GHz</text><rect x="180" y="212" width="460" height="38" rx="8" fill="#493a28" stroke="#ffc66d" stroke-width="2"/><text x="195" y="235" fill="#fff2d6" font-size="13">Plus de spectre là où autorisé / portée plus sensible</text>
<text x="675" y="106" fill="#9cafc5" font-size="12">Bande étroite</text><text x="675" y="168" fill="#9cafc5" font-size="12">Plus de canaux</text><text x="675" y="230" fill="#9cafc5" font-size="12">Matériel compatible</text>
<path d="M35 267 H845" stroke="#243247" stroke-width="1"/><text x="440" y="286" fill="#8698ae" font-size="11" text-anchor="middle">La performance dépend aussi du signal, du bruit, du client et de la charge réseau.</text>
</svg>
</div>

## 5. Les générations Wi-Fi : du nom à la norme

Les appellations générationnelles rendent les générations plus faciles à mémoriser. Elles sont associées à des amendements IEEE, mais la certification Wi-Fi correspond à un ensemble de fonctionnalités validées par la Wi-Fi Alliance ; une certification donnée ne signifie pas que chaque option imaginable de la norme est activée.

| Nom courant | Amendement IEEE | Repère simplifié |
|---|---|---|
| Wi-Fi 4 | 802.11n | MIMO, fonctionnement en 2,4 et 5 GHz selon l’équipement |
| Wi-Fi 5 | 802.11ac | Principalement 5 GHz, gains de débit et MU-MIMO descendant selon les versions |
| Wi-Fi 6 | 802.11ax | Efficacité dans les environnements chargés, OFDMA et améliorations multi-utilisateurs |
| Wi-Fi 6E | 802.11ax + bande 6 GHz | Extension du Wi-Fi 6 au 6 GHz dans les régions autorisées |
| Wi-Fi 7 | 802.11be | Améliorations de débit, latence et MLO selon la compatibilité |

Des standards anciens comme 802.11b/g/a existent encore dans des contextes historiques. Leur présence peut ralentir ou compliquer un réseau, mais il ne faut pas désactiver une compatibilité sans vérifier les appareils qui en dépendent.

### Ce que ces noms ne garantissent pas

Le chiffre inscrit sur la boîte n’est pas une promesse de vitesse applicative. Le débit théorique radio est partagé et dépend des capacités du client et de l’AP, de la distance, de la largeur de canal, du nombre de flux spatiaux, du brouillage et du protocole. Le débit utile d’un téléchargement est inférieur au débit physique indiqué, car il faut transmettre des en-têtes, des acquittements, des retransmissions éventuelles et d’autres trafics.

## 6. Comment un appareil rejoint un réseau Wi-Fi

Une connexion se fait par étapes. L’ordre précis dépend du type de réseau, des paramètres de sécurité et des capacités de l’appareil, mais les grandes idées sont les suivantes : découvrir le réseau, choisir un AP, s’authentifier, s’associer, établir les paramètres de sécurité si nécessaire, puis configurer la couche IP.

### 6.1 Découverte

Le point d’accès diffuse périodiquement des **trames Beacon** qui annoncent notamment les caractéristiques de la cellule. Le client peut aussi envoyer des **Probe Requests** et recevoir des Probe Responses pour chercher un réseau. Un SSID masqué n’élimine pas tous ces échanges et n’est pas une véritable barrière de sécurité.

### 6.2 Authentification et association 802.11

Le client et l’AP échangent des trames de gestion pour effectuer l’authentification 802.11 et demander/accorder l’association. Le mot « authentification » peut prêter à confusion : la phase d’authentification 802.11 elle-même ne vérifie pas toujours le mot de passe Wi-Fi de la manière imaginée par les débutants. Avec WPA2-Personal, WPA3-Personal ou un réseau d’entreprise, d’autres échanges de sécurité ont lieu ensuite ou s’articulent avec ce processus.

### 6.3 Sécurité et clés

Une fois l’association faite, les stations doivent établir les mécanismes de protection attendus par le réseau. En WPA2, le **four-way handshake** permet notamment de confirmer la possession du secret nécessaire et d’installer des clés de session. WPA3-Personal utilise SAE pour une authentification par mot de passe plus résistante aux attaques hors ligne, avec un déroulement différent de celui de WPA2. Les détails varient selon la méthode et la configuration.

### 6.4 Configuration IP

Après l’établissement de la liaison et l’accès au réseau, le client obtient généralement ses paramètres IP par DHCP : adresse IP, masque ou préfixe, passerelle et DNS. Il peut alors tenter de communiquer avec la passerelle, résoudre des noms via DNS et accéder à Internet si la route et le service extérieur fonctionnent.

### Schéma des étapes de connexion

<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500" role="img" aria-label="Échanges simplifiés lors de la connexion d’un client Wi-Fi à un point d’accès" style="width:100%;height:auto;background:#090d14;border-radius:14px" font-family="Arial,Helvetica,sans-serif">
<defs><marker id="wf3b" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#55d6ff"/></marker><marker id="wf3g" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#5be49b"/></marker><marker id="wf3a" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ffc66d"/></marker></defs>
<text x="30" y="34" fill="#edf5ff" font-size="19" font-weight="700">Connexion Wi-Fi : vue simplifiée</text><rect x="68" y="58" width="250" height="54" rx="10" fill="#172b43" stroke="#a5b4fc" stroke-width="2"/><text x="193" y="90" fill="#f2f5ff" font-size="17" font-weight="700" text-anchor="middle">Client Wi-Fi</text><rect x="580" y="58" width="250" height="54" rx="10" fill="#123329" stroke="#5be49b" stroke-width="2"/><text x="705" y="90" fill="#effff7" font-size="17" font-weight="700" text-anchor="middle">Point d’accès</text>
<path d="M318 145 H580" stroke="#55d6ff" stroke-width="3" fill="none" marker-end="url(#wf3b)"/><text x="449" y="136" fill="#bdefff" font-size="13" text-anchor="middle">1. Probe Request (si utilisé)</text><path d="M580 179 H318" stroke="#55d6ff" stroke-width="3" fill="none" marker-end="url(#wf3b)"/><text x="449" y="170" fill="#bdefff" font-size="13" text-anchor="middle">2. Beacon / Probe Response</text><path d="M318 231 H580" stroke="#5be49b" stroke-width="3" fill="none" marker-end="url(#wf3g)"/><text x="449" y="222" fill="#bcf8d9" font-size="13" text-anchor="middle">3. Authentification 802.11</text><path d="M318 265 H580" stroke="#5be49b" stroke-width="2" fill="none" marker-end="url(#wf3g)"/><text x="449" y="256" fill="#bcf8d9" font-size="13" text-anchor="middle">4. Association Request</text><path d="M580 299 H318" stroke="#5be49b" stroke-width="2" fill="none" marker-end="url(#wf3g)"/><text x="449" y="290" fill="#bcf8d9" font-size="13" text-anchor="middle">5. Association Response</text><path d="M318 343 H580" stroke="#ffc66d" stroke-width="3" fill="none" marker-end="url(#wf3a)"/><text x="449" y="334" fill="#ffe0a8" font-size="13" text-anchor="middle">6. Échanges de sécurité (selon WPA)</text><path d="M318 397 H580" stroke="#ffc66d" stroke-width="3" fill="none" marker-end="url(#wf3a)"/><text x="449" y="388" fill="#ffe0a8" font-size="13" text-anchor="middle">7. Client ↔ DHCP (souvent via AP/LAN)</text>
<path d="M328 145 H570 M328 231 H570 M328 343 H570" stroke="#55d6ff" stroke-width="2" opacity=".6" fill="none" class="wifi-flow"/><path d="M328 179 H570 M328 265 H570 M328 397 H570" stroke="#5be49b" stroke-width="2" opacity=".6" fill="none" class="wifi-flow"/>
<text x="450" y="444" fill="#f1f5ff" font-size="15" font-weight="700" text-anchor="middle">Le lien Wi-Fi ne suffit pas : l’adresse IP et la route doivent aussi fonctionner.</text><text x="450" y="468" fill="#91a3b9" font-size="12" text-anchor="middle">Séquence pédagogique, non exhaustive ; les détails dépendent du mode de sécurité et des capacités.</text>
</svg>
</div>

## 7. Les trois grandes catégories de trames 802.11

Le protocole 802.11 définit de nombreux types et sous-types de trames. Pour débuter, retiens trois familles :

### Trames de gestion (*Management*)

Elles aident les stations à découvrir les réseaux et à établir ou maintenir leur relation avec un AP. Exemples : Beacon, Probe Request/Response, Authentication, Association Request/Response, Reassociation et Deauthentication/Disassociation.

### Trames de contrôle (*Control*)

Elles coordonnent l’accès au médium ou aident à transporter les données de manière fiable. Selon le mécanisme et la génération, on rencontre par exemple des trames ACK, RTS et CTS. Elles ne sont pas des messages destinés à l’utilisateur ; elles participent au fonctionnement radio.

### Trames de données (*Data*)

Elles transportent les données utilisateur ou certaines informations de couche supérieure. Le contenu peut être protégé par chiffrement si le réseau utilise une sécurité adéquate. Une capture qui affiche les en-têtes radio ne signifie pas que le contenu applicatif est lisible.

Le Wi-Fi est un médium partagé : les stations doivent respecter les règles d’accès à la radio et les transmissions peuvent être retardées par une occupation élevée, des collisions/interférences ou des retransmissions.

### Résumé visuel des familles

<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" width="880" height="300" viewBox="0 0 880 300" role="img" aria-label="Trois familles de trames Wi-Fi : gestion, contrôle et données" style="width:100%;height:auto;background:#090d14;border-radius:14px" font-family="Arial,Helvetica,sans-serif">
<text x="28" y="34" fill="#edf5ff" font-size="19" font-weight="700">Trois grandes familles de trames 802.11</text>
<rect x="28" y="62" width="258" height="180" rx="13" fill="#172b43" stroke="#55d6ff" stroke-width="2"/><text x="157" y="92" fill="#dff7ff" font-size="18" font-weight="700" text-anchor="middle">Gestion</text><text x="48" y="123" fill="#f1f6ff" font-size="14">• Beacon</text><text x="48" y="147" fill="#f1f6ff" font-size="14">• Probe Request/Response</text><text x="48" y="171" fill="#f1f6ff" font-size="14">• Authentication</text><text x="48" y="195" fill="#f1f6ff" font-size="14">• Association / dissociation</text><text x="48" y="221" fill="#a9c2db" font-size="12">Découvrir et gérer la relation</text>
<rect x="311" y="62" width="258" height="180" rx="13" fill="#322d20" stroke="#ffc66d" stroke-width="2"/><text x="440" y="92" fill="#fff0d0" font-size="18" font-weight="700" text-anchor="middle">Contrôle</text><text x="331" y="123" fill="#fff7e8" font-size="14">• ACK</text><text x="331" y="147" fill="#fff7e8" font-size="14">• RTS / CTS</text><text x="331" y="171" fill="#fff7e8" font-size="14">• Autres échanges de contrôle</text><text x="331" y="221" fill="#f5dca8" font-size="12">Coordonner l’accès à la radio</text>
<rect x="594" y="62" width="258" height="180" rx="13" fill="#123329" stroke="#5be49b" stroke-width="2"/><text x="723" y="92" fill="#e5fff2" font-size="18" font-weight="700" text-anchor="middle">Données</text><text x="614" y="123" fill="#effff7" font-size="14">• Trafic utilisateur</text><text x="614" y="147" fill="#effff7" font-size="14">• IP, DNS, applications</text><text x="614" y="171" fill="#effff7" font-size="14">• Contenu protégé si chiffré</text><text x="614" y="221" fill="#b8e8d1" font-size="12">Transporter les données utiles</text>
<text x="440" y="273" fill="#91a3b9" font-size="12" text-anchor="middle">Les sous-types et les détails varient selon le mécanisme et la génération 802.11.</text>
</svg>
</div>

## 8. Comprendre la qualité du signal

### RSSI : la puissance reçue

Le **RSSI** est un indicateur de la puissance reçue, souvent affiché en dBm. Les valeurs en dBm sont négatives dans la plupart des situations Wi-Fi. Une valeur plus proche de zéro correspond généralement à un signal plus fort : par exemple, −45 dBm est plus fort que −75 dBm. Mais les échelles affichées par certains pilotes sont propres au fabricant : vérifie la définition de la mesure avant de comparer des appareils différents.

### Bruit et rapport signal/bruit (SNR)

Le **SNR** compare le signal utile au bruit radio. Un signal puissant ne garantit pas une bonne qualité si le bruit ou les interférences sont également élevés. Inversement, un signal plus faible peut être exploitable si le bruit est faible et que le client reste dans une plage adaptée à son débit.

### Obstacles et emplacement

Les murs, le béton armé, les étages, les surfaces métalliques, les meubles et même l’emplacement de l’AP influencent la propagation. Placer le point d’accès dans un placard métallique ou derrière un grand écran peut dégrader la couverture. Pour une maison, un AP central, dégagé et à hauteur raisonnable est souvent un meilleur départ qu’un appareil posé au sol dans un coin.

### Interférences et airtime

Le Wi-Fi ne se limite pas à « combien de barres » apparaissent à l’écran. Plusieurs réseaux peuvent se partager le même canal et attendre leur tour pour émettre. Plus le canal est occupé, plus le temps d’attente peut augmenter. Une source de bruit non-Wi-Fi peut également nuire à la réception sans apparaître comme un réseau normal dans la liste des SSID.

### Débit de liaison et débit utile

Le système d’exploitation peut afficher une vitesse de connexion ou un **PHY rate**. Ce chiffre décrit un mode de transmission radio, pas le débit garanti de téléchargement. Le débit utile est inférieur en raison des en-têtes, des acquittements, du partage de l’air, de la contention, des retransmissions et des autres équipements traversés. Une connexion indiquée à 866 Mbit/s ne garantit pas un téléchargement à 866 Mbit/s.

## 9. Sécuriser un réseau Wi-Fi

Le chiffrement et l’authentification protègent le réseau, mais ils n’annulent pas tous les risques. La sécurité dépend aussi de la configuration du routeur, de la séparation des invités, des mises à jour, de la qualité des mots de passe et de la protection des équipements finaux.

### 9.1 WPA2 et WPA3

- **WPA2-Personal** : utilise un secret partagé (mot de passe de réseau) ; privilégier AES/CCMP plutôt que les anciens mécanismes.
- **WPA3-Personal** : utilise SAE, conçu pour mieux résister à certaines tentatives d’attaque hors ligne sur mot de passe.
- **WPA2/WPA3-Enterprise** : s’appuie généralement sur 802.1X/EAP et une infrastructure d’authentification, adaptée aux organisations.
- **Réseau ouvert** : ne fournit pas à lui seul la protection cryptographique d’un réseau protégé. Certaines offres utilisent Enhanced Open/OWE, mais il faut vérifier ce qui est réellement activé.

**WEP** et **TKIP** sont anciens et ne doivent pas être considérés comme des choix de sécurité modernes. Évite les modes de compatibilité hérités s’ils ne sont pas indispensables.

### 9.2 Mot de passe et administration

Utilise une phrase de passe longue, unique et difficile à deviner. Modifie aussi les identifiants d’administration par défaut du routeur. Le mot de passe du Wi-Fi et celui de l’interface d’administration remplissent des rôles différents : ne les confonds pas.

Mets à jour le firmware du routeur ou de l’AP depuis la source légitime du fabricant. Désactive les fonctions de gestion à distance si elles ne sont pas nécessaires, et utilise-les uniquement avec une configuration de sécurité maîtrisée.

### 9.3 Réseau invité : isoler, pas seulement renommer

Un SSID invité n’est pas automatiquement isolé du réseau principal. Vérifie que la fonction invité bloque l’accès aux équipements internes et, si nécessaire, la communication directe entre clients. Dans une entreprise, la séparation peut s’appuyer sur des VLAN, des politiques d’accès, un pare-feu ou des fonctions de contrôleur. Une simple couleur ou un nom différent dans la liste des réseaux ne prouve aucune isolation.

### 9.4 WPS et mises à jour

Si le WPS n’est pas nécessaire, désactive-le conformément aux recommandations du fabricant et à la politique de sécurité. Garde les points d’accès, routeurs et clients à jour. Pour un réseau professionnel, documente la version du firmware, les dates de mise à jour et le processus de retour arrière.

### 9.5 Sécurité et vie privée

Une capture radio peut révéler des adresses MAC, des noms de réseaux, des heures de connexion, des destinations et des métadonnées. Le chiffrement Wi-Fi protège le contenu de nombreuses communications sur le lien radio, mais il ne rend pas tous les métadonnées invisibles. Ne capture que les réseaux que tu es autorisé à analyser et protège les fichiers de capture comme des données potentiellement sensibles.

## 10. Wi-Fi en mode infrastructure et autres modes

### Mode infrastructure

C’est le mode le plus courant : chaque station se connecte à un AP. Celui-ci transmet le trafic sur le réseau local. Un réseau de plusieurs AP coordonnés reste généralement dans ce modèle.

### Point d’accès personnel / hotspot

Un smartphone peut partager son accès mobile en créant un petit réseau Wi-Fi. Il joue alors le rôle d’AP pour les clients et réalise souvent du routage et de la traduction d’adresses entre le réseau local et la connexion mobile. Les limites de débit, de batterie et de nombre de clients dépendent de l’appareil et de l’opérateur.

### Wi-Fi Direct et réseaux maillés

Wi-Fi Direct permet à certains appareils de communiquer selon un modèle pair-à-pair géré par la technologie, sans reprendre simplement le schéma classique d’un LAN avec AP dédié. Un système Wi-Fi maillé utilise plusieurs nœuds pour étendre la couverture et relier les points d’accès entre eux ; selon le produit, le lien entre nœuds peut utiliser la radio ou un câble Ethernet. Un maillage améliore la couverture uniquement si les nœuds disposent d’une liaison de retour (*backhaul*) suffisamment bonne.

### Réseau maillé : attention au retour

Un nœud satellite avec un excellent signal vers le téléphone mais une mauvaise liaison vers le nœud principal peut offrir une expérience médiocre. Lorsque c’est possible, un backhaul Ethernet est souvent plus prévisible. En radio, le placement doit tenir compte à la fois du signal client↔nœud et de la liaison nœud↔nœud.

## 11. Diagnostic de base : commencer par localiser la panne

Ne réinitialise pas le routeur dès le premier symptôme. Pose d’abord une question précise : le problème concerne-t-il un seul appareil, une zone, tous les clients ou uniquement Internet ? Note l’heure, l’endroit, le SSID, la bande, l’appareil et les tests déjà réalisés.

### Étape 1 — Vérifier le périmètre

- Un seul appareil est touché : vérifier son Wi-Fi, son pilote, son adresse IP et ses paramètres.
- Plusieurs appareils sur le même AP sont touchés : examiner l’AP, le canal, le backhaul filaire, le DHCP et les changements récents.
- Tous les appareils ont le Wi-Fi mais pas Internet : examiner le routeur, la passerelle, le DNS et la liaison opérateur.
- La panne n’existe que dans une pièce : vérifier la couverture, les obstacles, l’emplacement du client et les interférences.

### Étape 2 — Lire l’état de la connexion

Sous Windows, ouvrir un terminal ou une invite de commandes :

```powershell
netsh wlan show interfaces
netsh wlan show drivers
ipconfig /all
```

`netsh wlan show interfaces` permet notamment de consulter l’état, le SSID, le type radio et des informations de signal que le pilote expose. `netsh wlan show drivers` affiche les capacités rapportées par le pilote. `ipconfig /all` permet d’examiner l’adresse IP, la passerelle, le DHCP et les DNS.

Sous Linux, les commandes disponibles dépendent de la distribution :

```bash
nmcli dev wifi list
ip addr
ip route
resolvectl status
```

`nmcli dev wifi list` liste les réseaux visibles si NetworkManager gère la connexion. `ip addr` et `ip route` affichent les adresses et les routes ; `resolvectl status` affiche l’état DNS lorsqu’il est utilisé sur le système. N’exécute pas une commande comme si tous les systèmes avaient exactement les mêmes outils.

### Étape 3 — Tester par couches

1. **Association Wi-Fi :** le client est-il réellement connecté au bon SSID et au bon AP ?
2. **IP :** a-t-il une adresse compatible avec le sous-réseau attendu ? Une adresse automatique inattendue peut indiquer que DHCP n’a pas répondu, sans suffire à expliquer toutes les causes.
3. **Passerelle :** peut-il joindre la passerelle locale si ICMP est autorisé ?
4. **DNS :** un nom se résout-il ? Essayer `nslookup example.com` ou l’outil DNS équivalent.
5. **Internet et application :** un test vers une adresse externe et un nom permet de distinguer certaines pannes de routage et de résolution. Un serveur externe peut bloquer ICMP ; l’échec d’un `ping` isolé ne prouve donc pas que tout Internet est inaccessible.

### Arbre de dépannage simplifié

<div class="svg-diagram">
<svg xmlns="http://www.w3.org/2000/svg" width="880" height="530" viewBox="0 0 880 530" role="img" aria-label="Arbre de dépannage Wi-Fi depuis la connexion sans fil jusqu'à Internet" style="width:100%;height:auto;background:#090d14;border-radius:14px" font-family="Arial,Helvetica,sans-serif">
<defs><marker id="wf6arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#55d6ff"/></marker><marker id="wf6green" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#5be49b"/></marker><marker id="wf6amber" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#ffc66d"/></marker></defs>
<rect x="300" y="22" width="280" height="54" rx="11" fill="#172b43" stroke="#55d6ff" stroke-width="2"/><text x="440" y="54" fill="#eff7ff" font-size="17" font-weight="700" text-anchor="middle">Wi-Fi connecté ?</text>
<path d="M440 76 V109 H208 V136" fill="none" stroke="#55d6ff" stroke-width="3" marker-end="url(#wf6arr)"/><text x="306" y="101" fill="#9fe7ff" font-size="12">Non</text><path d="M440 76 V109 H670 V136" fill="none" stroke="#5be49b" stroke-width="3" marker-end="url(#wf6green)"/><text x="566" y="101" fill="#9bf0c2" font-size="12">Oui</text>
<rect x="48" y="136" width="320" height="70" rx="11" fill="#38272a" stroke="#fb7185" stroke-width="2"/><text x="208" y="164" fill="#ffe8ec" font-size="15" font-weight="700" text-anchor="middle">Vérifier SSID, mot de passe,</text><text x="208" y="185" fill="#ffe8ec" font-size="15" text-anchor="middle">signal, sécurité et AP</text>
<rect x="510" y="136" width="320" height="70" rx="11" fill="#123329" stroke="#5be49b" stroke-width="2"/><text x="670" y="164" fill="#effff7" font-size="15" font-weight="700" text-anchor="middle">Adresse IP et passerelle</text><text x="670" y="185" fill="#b8e8d1" font-size="13" text-anchor="middle">Vérifier DHCP / sous-réseau</text>
<path d="M670 206 V246" fill="none" stroke="#55d6ff" stroke-width="3" marker-end="url(#wf6arr)"/><path d="M208 206 V247" fill="none" stroke="#ffc66d" stroke-width="3" marker-end="url(#wf6amber)" class="wifi-flow"/>
<rect x="48" y="247" width="320" height="70" rx="11" fill="#322d20" stroke="#ffc66d" stroke-width="2"/><text x="208" y="275" fill="#fff3d9" font-size="15" font-weight="700" text-anchor="middle">Toujours pas de connexion ?</text><text x="208" y="296" fill="#f7dca6" font-size="13" text-anchor="middle">Comparer un autre appareil / une autre zone</text>
<rect x="510" y="247" width="320" height="70" rx="11" fill="#172b43" stroke="#55d6ff" stroke-width="2"/><text x="670" y="275" fill="#eff7ff" font-size="15" font-weight="700" text-anchor="middle">Tester la passerelle</text><text x="670" y="296" fill="#bdefff" font-size="13" text-anchor="middle">Ensuite tester DNS et accès externe</text>
<path d="M670 317 V355" fill="none" stroke="#55d6ff" stroke-width="3" marker-end="url(#wf6arr)"/><path d="M208 317 V355" fill="none" stroke="#ffc66d" stroke-width="3" marker-end="url(#wf6amber)"/>
<rect x="48" y="355" width="320" height="82" rx="11" fill="#20283a" stroke="#a5b4fc" stroke-width="2"/><text x="208" y="382" fill="#f1f5ff" font-size="15" font-weight="700" text-anchor="middle">Panne localisée</text><text x="208" y="403" fill="#cad4f4" font-size="13" text-anchor="middle">AP, radio, interférences ou</text><text x="208" y="420" fill="#cad4f4" font-size="13" text-anchor="middle">association/authentification</text>
<rect x="510" y="355" width="320" height="82" rx="11" fill="#20283a" stroke="#a5b4fc" stroke-width="2"/><text x="670" y="382" fill="#f1f5ff" font-size="15" font-weight="700" text-anchor="middle">Panne IP / service</text><text x="670" y="403" fill="#cad4f4" font-size="13" text-anchor="middle">DHCP, passerelle, DNS, routeur</text><text x="670" y="420" fill="#cad4f4" font-size="13" text-anchor="middle">ou opérateur à examiner</text>
<path d="M208 437 V464 H440 V485 M670 437 V464 H440" fill="none" stroke="#55d6ff" stroke-width="2.5" marker-end="url(#wf6arr)"/><rect x="270" y="485" width="340" height="32" rx="8" fill="#122a23" stroke="#5be49b" stroke-width="1.5"/><text x="440" y="506" fill="#d8ffee" font-size="14" font-weight="700" text-anchor="middle">Noter résultats, heure et changement testé</text>
</svg>
</div>

### Étape 4 — Changer une seule chose à la fois

Un test est plus utile s’il permet d’isoler une cause. Si tu modifies simultanément le canal, le mot de passe, la bande et les paramètres DHCP, tu ne sauras pas ce qui a résolu le problème. Note l’état initial, applique un changement, teste depuis le même endroit et documente le résultat.

Évite les réinitialisations usine sans sauvegarde et sans connaître la configuration de l’opérateur. Elles peuvent supprimer les paramètres Internet, les règles de sécurité ou le nom du réseau et transformer une petite panne en incident plus important.

## 12. Les erreurs fréquentes des débutants

1. **Confondre Wi-Fi et Internet.** La radio peut fonctionner même si le DNS, le routeur ou la liaison opérateur est en panne.
2. **Comparer seulement les barres de signal.** Elles sont un indicateur simplifié, pas une mesure complète du bruit, de la congestion ou du débit utile.
3. **Penser qu’un routeur plus puissant résout tout.** Il peut améliorer certains liens, mais ne règle pas automatiquement les interférences, le mauvais placement ou une liaison montante saturée.
4. **Choisir systématiquement 160 ou 320 MHz.** Une largeur élevée n’est pas forcément adaptée à un environnement encombré ni supportée par les clients.
5. **Masquer le SSID comme mesure de sécurité.** Cela ne remplace pas un protocole de sécurité robuste.
6. **Croire que le réseau invité est isolé par son nom.** Il faut vérifier les politiques effectives et les tests d’accès.
7. **Réinitialiser avant de mesurer.** Cette action efface des indices et peut faire perdre une configuration utile.
8. **Confondre vitesse de liaison et débit Internet.** Le débit radio affiché est seulement une indication de la liaison physique.
9. **Supposer que tous les appareils supportent 5 ou 6 GHz.** Les capacités varient selon les générations et les modèles ; vérifier les spécifications du client.
10. **Déclarer une panne sur la base d’un seul ping.** ICMP peut être filtré ; comparer plusieurs tests et chemins.

## 13. Atelier pratique : installer et vérifier un petit réseau Wi-Fi

### Scénario

Tu dois connecter un ordinateur et un téléphone à un routeur Wi-Fi de test. L’objectif n’est pas de maximiser la vitesse, mais de démontrer que chaque couche fonctionne et de documenter les paramètres.

### Étape A — Préparer

1. Place le routeur ou l’AP dans un endroit dégagé, hors d’un placard métallique.
2. Vérifie la documentation du fabricant et la dernière version stable du firmware.
3. Connecte l’AP au réseau ou au routeur selon la topologie disponible.
4. Choisis un SSID distinctif, une phrase de passe forte et WPA2-AES ou WPA3 si les clients sont compatibles. Ne laisse pas l’administration avec des identifiants par défaut.
5. Si tu configures un réseau invité, vérifie sa politique d’isolation au lieu de supposer qu’elle est activée.

### Étape B — Connecter un client

1. Sur le client, ouvre la liste des réseaux Wi-Fi.
2. Repère le SSID souhaité et vérifie qu’il correspond à ton AP.
3. Connecte-toi avec les paramètres convenus.
4. Vérifie l’état de connexion et, si disponible, le BSSID, la bande, le canal et le signal.
5. Vérifie que le client obtient une adresse IP, une passerelle et un DNS cohérents avec le réseau.

### Étape C — Tester par couches

- Ouvre la page d’administration locale de l’AP si ton compte y est autorisé.
- Essaie de joindre la passerelle locale.
- Résous un nom de domaine avec un outil DNS.
- Teste l’accès à un site autorisé.
- Si le site ne s’ouvre pas, compare avec un autre appareil et consigne les différences.

### Étape D — Simuler un incident sans prendre de risque

Sur un réseau de laboratoire dont tu as l’autorisation, modifie un seul paramètre non critique, comme le nom du réseau ou la disponibilité d’une bande, puis observe le symptôme côté client. Restaure ensuite la configuration précédente. N’effectue pas cet exercice sur un réseau partagé ou utilisé pour la production.

### Fiche de résultat

| Élément | Résultat à noter |
|---|---|
| Date et heure | Quand le test a été effectué |
| Matériel / modèle | Routeur/AP et client |
| SSID / BSSID | Nom du réseau et identifiant radio observé |
| Bande / canal | Valeurs affichées par le client ou l’AP |
| Sécurité | WPA2/WPA3, mode et paramètres connus |
| Adresse IP / passerelle / DNS | Paramètres attribués au client |
| Tests réalisés | Passerelle, DNS, accès applicatif |
| Conclusion | Fonctionne, échec précis, hypothèses suivantes |

## 14. Mini-cas de diagnostic

### Cas 1 — « Connecté, pas d’Internet »

**Observation :** le téléphone annonce qu’il est connecté au SSID, mais les sites ne chargent pas.

**Démarche :** vérifie l’adresse IP et la passerelle. Si l’adresse est incohérente, examine DHCP et le VLAN associé. Si la passerelle est joignable mais que les noms échouent, teste DNS. Si la passerelle et DNS fonctionnent mais aucun site n’est accessible, examine le routage, le pare-feu, le portail captif ou la liaison opérateur. Le message du système est un indice, pas un diagnostic final.

### Cas 2 — Le Wi-Fi est rapide à côté de l’AP mais lent dans la chambre

**Hypothèses :** atténuation par les murs, interférences, client qui conserve une liaison faible, différence de bande ou backhaul du maillage insuffisant.

**Démarche :** mesure depuis deux endroits et sur un même serveur de test, vérifie la bande/canal et compare le signal. Si possible, effectue une mesure locale sur le LAN pour séparer les performances radio de la connexion Internet. Déplace temporairement l’AP de manière contrôlée avant d’acheter du matériel.

### Cas 3 — Un seul ordinateur ne se connecte pas

**Hypothèses :** mot de passe enregistré incorrect, profil réseau périmé, pilote, mode de sécurité incompatible, carte désactivée ou problème spécifique à ce client.

**Démarche :** vérifie s’il détecte le SSID, compare sa compatibilité dans `netsh wlan show drivers`, oublie puis recrée le profil si cela est approprié, mets le pilote à jour depuis une source légitime et teste un autre réseau autorisé. Si d’autres appareils fonctionnent, évite de modifier d’abord la configuration globale de l’AP.

### Cas 4 — Coupures périodiques

**Hypothèses :** changement DFS sur un canal 5 GHz concerné, interférences, problème d’alimentation ou de firmware, itinérance entre AP, congestion ou perte de la liaison filaire.

**Démarche :** note précisément l’heure des coupures, les journaux AP, le BSSID avant/après et si les appareils filaires sont touchés au même moment. Cette comparaison permet de distinguer une panne radio d’une panne du réseau amont.

## 15. Bonnes pratiques d’exploitation

- Documente SSID, mode de sécurité, sous-réseau, passerelle, serveur DHCP et personne responsable.
- Utilise des noms qui distinguent les réseaux interne et invité sans publier d’informations confidentielles.
- Garde les mots de passe et les identifiants d’administration dans un coffre adapté.
- Maintiens le firmware à jour selon une procédure, après vérification des notes de version et de la compatibilité.
- Évite les canaux et largeurs choisis au hasard ; mesure l’environnement, surtout dans un bureau dense.
- Prévois une couverture homogène et teste avec les types de clients réellement utilisés.
- Sépare les appareils invités et objets connectés lorsque le risque le justifie.
- Lors d’une panne, capture les faits avant de modifier la configuration.
- Pour une analyse radio avancée, utilise uniquement des équipements, lieux et données pour lesquels tu as reçu l’autorisation.

## 16. Quiz de validation

Réponds d’abord sans regarder le corrigé.

1. Quelle différence y a-t-il entre Wi-Fi et Internet ?
2. Quel est le rôle principal d’un point d’accès ?
3. Que représente le SSID ? En quoi diffère-t-il du BSSID ?
4. Quelle différence y a-t-il entre une bande, un canal et une largeur de canal ?
5. Pourquoi le canal le plus large n’est-il pas toujours le meilleur ?
6. Que font les trames Beacon ?
7. Quelle est la différence entre une trame de gestion et une trame de données ?
8. Pourquoi « connecté au Wi-Fi » ne prouve-t-il pas que DHCP et DNS fonctionnent ?
9. Pourquoi WPA2-AES ou WPA3 est-il préférable à WEP ?
10. Que faut-il vérifier pour confirmer qu’un réseau invité est isolé ?
11. Quelle est la différence entre RSSI et SNR, en termes simples ?
12. Pourquoi le débit de liaison affiché peut-il être supérieur au débit réel d’un téléchargement ?
13. Si un seul appareil a un problème, quelle approche est la plus raisonnable avant de changer la configuration de l’AP ?
14. Cite deux causes possibles de coupures périodiques sur 5 GHz.
15. Pourquoi faut-il protéger les fichiers de capture radio ?

### Corrigé

1. Le Wi-Fi est la liaison radio locale ; Internet est un réseau externe auquel le LAN peut donner accès.
2. Il fournit la cellule radio et relie les stations au réseau local.
3. Le SSID est le nom du réseau ; le BSSID identifie une cellule/BSS, souvent à partir d’une adresse MAC radio.
4. La bande est la plage de fréquence, le canal est une position dedans, et la largeur mesure le spectre utilisé.
5. Elle occupe davantage de spectre et peut aggraver la congestion ou réduire les possibilités de réutilisation.
6. Elles annoncent périodiquement la présence et les paramètres d’une cellule Wi-Fi.
7. Une trame de gestion sert à la découverte ou au maintien du lien ; une trame de données transporte du trafic utile ou des informations de couche supérieure.
8. L’association radio n’attribue pas à elle seule une adresse IP et ne garantit pas la résolution de noms.
9. WEP est obsolète et vulnérable ; les mécanismes modernes offrent une protection nettement meilleure.
10. Il faut tester ou vérifier la politique de séparation vers le LAN interne et entre clients, et non se fier au nom du SSID.
11. RSSI indique la puissance reçue ; SNR indique la différence relative entre signal utile et bruit.
12. Les en-têtes, acquittements, temps d’attente, retransmissions, partage du médium et limitations du réseau réduisent le débit utile.
13. Vérifier l’état du client, le pilote, le profil, l’adresse IP et comparer avec un autre appareil avant de changer la configuration globale.
14. Par exemple : DFS/changement de canal, interférences, perte de backhaul, congestion ou défaut de firmware/alimentation.
15. Elles peuvent contenir des identifiants, des métadonnées de trafic et des informations sur les appareils ou les réseaux observés.

## 17. Glossaire

- **802.11 :** famille de normes IEEE pour les réseaux locaux sans fil.
- **AP (Access Point) :** point d’accès Wi-Fi.
- **Airtime :** part du temps radio utilisée pour transmettre ou attendre la transmission.
- **BSSID :** identifiant d’un BSS, couramment lié à la MAC radio de la cellule.
- **Beacon :** trame de gestion périodique qui annonce une cellule Wi-Fi.
- **Bande :** plage de fréquences, par exemple 2,4 ou 5 GHz.
- **Canal :** portion de spectre utilisée par la transmission.
- **Client / STA :** appareil doté d’une interface Wi-Fi.
- **DHCP :** protocole qui fournit généralement automatiquement les paramètres IP.
- **DFS :** sélection dynamique de fréquence sur certains canaux, avec contraintes réglementaires de détection de radar.
- **LAN / WLAN :** réseau local / réseau local sans fil.
- **MIMO :** technique utilisant plusieurs antennes ou flux spatiaux pour améliorer certaines transmissions.
- **PoE :** alimentation électrique fournie par Ethernet lorsque les équipements le prennent en charge.
- **RSSI :** indicateur de puissance du signal reçu.
- **Roaming :** passage d’un client d’un AP à un autre.
- **SAE :** mécanisme d’authentification utilisé par WPA3-Personal.
- **SNR :** rapport signal/bruit.
- **SSID :** nom du réseau Wi-Fi annoncé aux utilisateurs.
- **WPA2/WPA3 :** familles de mécanismes de sécurité Wi-Fi modernes.
- **WPA3-Personal :** mode de sécurité personnel qui utilise SAE.
- **WPA3-Enterprise :** famille de modes de sécurité adaptée aux réseaux d’entreprise, généralement avec 802.1X/EAP.

## 18. Pour aller plus loin : sources techniques

Les liens ci-dessous permettent de compléter ce cours et de confirmer les détails qui dépendent du système, du matériel ou de la réglementation locale :

- [Cisco — analyse et dépannage des captures 802.11](https://www.cisco.com/c/en/us/support/docs/wireless-mobility/80211/200527-Fundamentals-of-802-11-Wireless-Sniffing.html) : catégories de trames et processus de connexion.
- [Cisco — guide de référence radio WLAN](https://www.cisco.com/c/en/us/td/docs/wireless/controller/9800/technical-reference/wireless-rf-reference-guide.html) : bandes, générations et principes RF.
- [Wireshark — FAQ sur les captures Wi-Fi](https://www.wireshark.org/download/docs/faq.html) : limites du mode monitor et de la prise de capture selon le système et le pilote.
- [Microsoft — Wi-Fi plus rapide et plus sécurisé sous Windows](https://support.microsoft.com/fr-fr/windows/experience/connectivity-networking/faster-and-more-secure-wi-fi-in-windows) : vérification des capacités client et éléments sur Wi-Fi 6/6E/7 et WPA3.
- [HPE Aruba — générations Wi-Fi](https://arubanetworking.hpe.com/techdocs/aos/wifi-design-deploy/generations/) : correspondance entre noms de générations et amendements IEEE.

**Règle de prudence :** les bandes de fréquences, canaux permis, puissances et certaines fonctionnalités varient selon le domaine réglementaire et le matériel. Vérifie les règles applicables dans ton pays ainsi que les notes du fabricant avant de configurer un réseau réel.


## À retenir

Le Wi-Fi est une liaison radio dont la qualité dépend du client, du point d’accès, du spectre, des obstacles, de la charge et de la configuration. La sécurité doit être traitée comme une fonction essentielle, et le diagnostic doit suivre les couches : association, adressage IP, passerelle, DNS puis application. Un bon technicien n’applique pas un réglage universel : il mesure, formule une hypothèse, teste un changement maîtrisé et conserve les résultats.
