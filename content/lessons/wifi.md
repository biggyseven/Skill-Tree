# Wi-Fi 802.11 : conception, sécurité et exploitation

Le Wi-Fi relie des appareils sans câble. C'est pratique, mais le support radio
est partagé, sensible aux obstacles et plus difficile à diagnostiquer qu'un
câble Ethernet. Une bonne installation Wi-Fi ne consiste pas à mettre des bornes
partout : il faut comprendre les bandes, les canaux, la puissance, les débits,
la sécurité et le roaming.

> Analogie : le Wi-Fi est une conversation dans une salle. Plus les personnes
> parlent fort, plus elles se gênent. On peut ajouter des salles, changer de
> fréquence ou demander à chacun de parler à tour de rôle, mais on ne peut pas
> rendre le bruit inexistant.

## 1. Les bases radio

Une borne Wi-Fi émet des ondes radio. Le client reçoit un signal plus ou moins
fort selon la distance, les murs, le métal, l'eau et les autres émetteurs.

Deux notions sont importantes :

- **RSSI** : force du signal reçu, souvent exprimée en dBm. Plus la valeur est
  proche de zéro, plus le signal est fort.
- **SNR** : rapport entre le signal utile et le bruit. Un bon RSSI ne suffit pas
  si le bruit est élevé.

| RSSI approximatif | Interprétation |
|---:|---|
| -30 à -50 dBm | Très bon, proche de la borne |
| -50 à -65 dBm | Bon, usage courant |
| -65 à -75 dBm | Moyen, peut être instable |
| -75 à -85 dBm | Faible, roaming souvent nécessaire |
| Moins de -85 dBm | Très faible, connexion peu fiable |

Ces valeurs sont indicatives : le débit dépend aussi du nombre d'antennes, du
client, du bruit et de la largeur de canal.

Le Wi-Fi utilise des modulations qui s'adaptent au signal. Quand le lien se
dégrade, le débit baisse pour rester fiable. Une barre Wi-Fi « pleine » ne
garantit donc pas un débit élevé.

## 2. Les générations 802.11

| Norme | Nom commercial | Bandes | Apports principaux |
|---|---|---|---|
| 802.11b | Wi-Fi 1 | 2,4 GHz | 11 Mb/s, historique |
| 802.11a | Wi-Fi 2 | 5 GHz | 54 Mb/s, moins d'interférences |
| 802.11g | Wi-Fi 3 | 2,4 GHz | 54 Mb/s |
| 802.11n | Wi-Fi 4 | 2,4 et 5 GHz | MIMO, 40 MHz, jusqu'à 600 Mb/s théoriques |
| 802.11ac | Wi-Fi 5 | 5 GHz | MU-MIMO descendant, 80/160 MHz |
| 802.11ax | Wi-Fi 6 / 6E | 2,4, 5 et 6 GHz | OFDMA, MU-MIMO, BSS coloring, TWT |
| 802.11be | Wi-Fi 7 | 2,4, 5 et 6 GHz | Canaux très larges, MLO, meilleure efficacité |

Les débits annoncés sont des maxima théoriques. Le débit réel dépend du nombre
de clients, de la largeur de canal, du signal, des interférences et du trafic.

### MIMO et MU-MIMO

Le **MIMO** utilise plusieurs antennes pour envoyer plusieurs flux en parallèle.
Le **MU-MIMO** permet à une borne de servir plusieurs clients simultanément
dans certaines conditions. Ces technologies améliorent la capacité, mais elles
ne compensent pas un mauvais emplacement.

### OFDMA

L'OFDMA, introduite avec Wi-Fi 6, découpe le canal en petites unités de
ressources. Plusieurs clients peuvent transmettre dans le même intervalle, ce
qui est efficace pour les petits paquets et les nombreux objets connectés.

## 3. Les bandes de fréquence

### 2,4 GHz

La bande 2,4 GHz porte loin et traverse mieux les murs, mais elle est très
encombrée : micro-ondes, Bluetooth, caméras, téléphones sans fil et réseaux
voisins.

Caractéristiques :

- canaux plus étroits et peu nombreux ;
- portée supérieure ;
- débit souvent plus faible ;
- forte probabilité d'interférences ;
- utile pour les objets connectés et les zones éloignées.

### 5 GHz

La bande 5 GHz offre plus de canaux et moins d'interférences. Elle porte moins
loin et traverse moins bien les obstacles.

Caractéristiques :

- plus de canaux disponibles ;
- largeurs de canal plus grandes ;
- débit plus élevé ;
- portée plus courte ;
- certains canaux sont DFS, partagés avec des radars.

### 6 GHz

La bande 6 GHz est utilisée par Wi-Fi 6E et Wi-Fi 7. Elle offre beaucoup de
canaux propres, ce qui réduit la contention. Elle est réservée aux équipements
récents et porte moins loin que 2,4 GHz.

| Bande | Portée | Débit | Interférences | Usage typique |
|---|---|---|---|---|
| 2,4 GHz | Longue | Plus faible | Élevées | IoT, couverture, secours |
| 5 GHz | Moyenne | Élevé | Moyennes | Postes, mobiles, bureaux |
| 6 GHz | Courte | Très élevé | Faibles | Wi-Fi 6E/7, zones denses |

## 4. Les canaux

Un canal est une portion de la bande utilisée pour transmettre. Deux bornes qui
utilisent le même canal se partagent le temps de parole. Deux bornes sur des
canaux qui se chevauchent créent des interférences.

### Canaux 2,4 GHz

En 2,4 GHz, les canaux se chevauchent largement. La pratique courante consiste
à utiliser les canaux **1, 6 et 11** pour un plan à trois canaux non
chevauchants en 20 MHz.

```text
Canaux 2,4 GHz : 1 2 3 4 5 6 7 8 9 10 11 12 13
Plan courant :   1 . . . . 6 . . . . 11
```

Selon le pays, les canaux 12 et 13 peuvent être autorisés. Le canal 14 est
spécifique à certains pays. Il faut respecter la réglementation locale.

### Canaux 5 GHz

La bande 5 GHz possède davantage de canaux. On distingue les canaux UNII et les
canaux DFS. Les canaux DFS peuvent être utilisés par des radars météo ou
aéronautiques : la borne doit les libérer si elle détecte un radar.

Largeurs courantes :

- 20 MHz : plus de canaux, moins de débit par client ;
- 40 MHz : compromis ;
- 80 MHz : débit élevé, moins de canaux ;
- 160 MHz : très large, peu de canaux, surtout en zone peu dense.

En entreprise, on privilégie souvent 20 ou 40 MHz en 5 GHz pour limiter la
contention. En maison, 80 MHz peut être intéressant si peu de voisins.

### Canaux 6 GHz

La bande 6 GHz offre de nombreux canaux et peu d'interférences. Les largeurs de
80 et 160 MHz y sont plus faciles à utiliser. Les équipements anciens ne la
voient pas.

## 5. SSID, BSSID et association

Un **SSID** est le nom du réseau Wi-Fi. Un **BSSID** est l'adresse MAC de la
radio d'une borne pour un SSID donné. Un même SSID peut être diffusé par
plusieurs bornes pour former un **ESSID** (Extended Service Set).

Quand un client veut se connecter :

1. Il écoute les balises (*beacons*) envoyées par les bornes.
2. Il peut envoyer une probe request pour découvrir les réseaux.
3. Il choisit un SSID et s'authentifie.
4. Il s'associe à la borne.
5. Il obtient une adresse IP, souvent par DHCP.
6. Il peut envoyer des données.

Une borne diffuse régulièrement des balises contenant le SSID, les capacités
et les paramètres de sécurité. Le client ne « voit » pas tous les réseaux de la
même façon selon sa carte, sa position et les canaux qu'il scanne.

## 6. Sécurité Wi-Fi

La sécurité Wi-Fi protège l'accès au réseau et chiffre les échanges radio. Elle
ne remplace pas une sécurité applicative : HTTPS, authentification et mises à
jour restent indispensables.

### WEP et WPA

**WEP** est obsolète et ne doit plus être utilisé. **WPA** avec TKIP est
également considéré comme obsolète. Ces protocoles ne résistent pas aux
attaques modernes.

### WPA2

WPA2 utilise AES-CCMP et existe en deux modes :

- **WPA2-Personal** : une phrase secrète partagée, souvent appelée PSK.
- **WPA2-Enterprise** : authentification individuelle via 802.1X, EAP et un
  serveur RADIUS.

Le mode Personal est simple pour une maison. Le mode Enterprise est adapté aux
entreprises, car chaque utilisateur possède ses propres identifiants.

### WPA3

WPA3 renforce la sécurité :

- **SAE** (Simultaneous Authentication of Equals) remplace la PSK classique et
  limite les attaques par dictionnaire hors ligne ;
- **WPA3-Enterprise** renforce l'authentification ;
- **PMF** (Protected Management Frames) protège certaines trames de gestion ;
- le chiffrement peut utiliser GCMP.

Le mode WPA3-Personal n'est pas compatible avec tous les anciens clients. On
peut utiliser un mode transition WPA2/WPA3, mais il faut accepter une sécurité
moins stricte pendant la coexistence.

### 802.1X et RADIUS

En WPA2/WPA3-Enterprise, le client s'authentifie auprès d'un serveur RADIUS,
souvent via EAP. L'utilisateur peut utiliser un identifiant/mot de passe ou un
certificat. Le contrôleur ou la borne transmet les échanges d'authentification.

> Analogie : WPA2-Personal est une clé unique pour tout l'immeuble. WPA2-
> Enterprise est un badge individuel vérifié à l'entrée.

### Bonnes pratiques

- Désactiver WEP et WPA/TKIP.
- Utiliser WPA2-AES au minimum, WPA3 si les clients le supportent.
- Changer les mots de passe par défaut de la box.
- Séparer le Wi-Fi invité du réseau interne.
- Désactiver WPS s'il n'est pas nécessaire.
- Mettre à jour les bornes et les contrôleurs.
- Utiliser un portail captif ou un VLAN invité pour les visiteurs.
- Surveiller les points d'accès non autorisés.

## 7. Le roaming

Le roaming permet à un client de passer d'une borne à une autre sans perdre sa
connexion. Le client reste associé au même SSID, mais change de BSSID.

Le client décide souvent lui-même de quitter une borne, en fonction du signal,
du débit et de ses propres algorithmes. C'est pourquoi deux téléphones peuvent
se comporter différemment au même endroit.

### Roaming « sticky »

Un client collé à une borne lointaine reste connecté avec un mauvais signal au
lieu de passer à une borne plus proche. On parle de **sticky client**. Les
solutions incluent :

- réduire la puissance des bornes ;
- ajuster le seuil de RSSI minimal ;
- utiliser le band steering ;
- activer les mécanismes 802.11k/v/r.

### 802.11k, 802.11v et 802.11r

| Mécanisme | Rôle simplifié |
|---|---|
| 802.11k | Fournit au client une liste de voisins et de canaux |
| 802.11v | Permet à l'infrastructure de suggérer une transition |
| 802.11r | Accélère le roaming avec une transition rapide |

Le roaming rapide est particulièrement utile pour la voix sur Wi-Fi, les
badges et les terminaux mobiles qui changent souvent de borne.

### Band steering

La borne ou le contrôleur peut encourager un client compatible 5/6 GHz à
utiliser cette bande plutôt que 2,4 GHz. Cela améliore souvent le débit, mais
un mauvais réglage peut déconnecter des objets anciens.

## 8. Les contrôleurs WLC

Un **WLC** (Wireless LAN Controller) centralise la gestion de nombreuses
bornes. Il peut gérer la configuration, les SSID, la sécurité, le roaming, les
canaux, la puissance et la supervision.

### Autonomous AP et architecture centralisée

- **AP autonome** : chaque borne est configurée séparément. Simple pour un
  petit site, plus difficile à maintenir à grande échelle.
- **AP léger + WLC** : les bornes sont gérées par un contrôleur. La
  configuration est centralisée.
- **Contrôleur cloud** : la gestion est externalisée, mais le trafic peut
  rester local selon l'architecture.

### CAPWAP

CAPWAP est un protocole courant entre un AP léger et un WLC. Il transporte le
contrôle et parfois les données. Les ports classiques sont UDP 5246 pour le
contrôle et UDP 5247 pour les données.

Le **split-MAC** sépare les fonctions :

- l'AP gère le temps réel radio, les balises, l'association et le chiffrement ;
- le WLC gère la configuration, la politique, l'itinérance et la supervision.

### Modes de déploiement

- **Local** : le trafic client revient au WLC, qui le place sur le VLAN prévu.
- **FlexConnect** : l'AP peut commuter localement le trafic et survivre à une
  coupure du WLC.
- **Mesh** : les bornes se relient sans câble, avec une racine reliée au réseau.

### Mobilité

Dans un grand campus, plusieurs WLC peuvent former un groupe de mobilité pour
permettre au client de passer d'un contrôleur à l'autre sans changer d'adresse
IP. La conception du VLAN et du DHCP doit être cohérente.

## 9. Concevoir un réseau Wi-Fi

### Étude de site

Une étude de site permet de déterminer le nombre de bornes, leur emplacement,
la puissance et les canaux. On peut utiliser une étude predictive sur plan,
puis une validation sur site avec un outil de mesure.

### Capacité et couverture

Il faut distinguer :

- **couverture** : le signal est-il suffisant ?
- **capacité** : le réseau peut-il servir tous les clients simultanément ?

Une salle avec beaucoup d'utilisateurs peut nécessiter plusieurs bornes même si
une seule borne couvre toute la surface. Le Wi-Fi est un média partagé : plus de
clients actifs signifie moins de temps radio pour chacun.

### Bonnes pratiques de conception

- placer les bornes près des zones de usage, pas seulement au plafond au hasard ;
- éviter les obstacles métalliques et les coins ;
- utiliser 20/40 MHz en 5 GHz pour limiter la contention ;
- planifier les canaux pour éviter les chevauchements ;
- baisser la puissance si les bornes s'entendent trop ;
- prévoir le PoE et le budget électrique ;
- séparer les SSID invités et internes ;
- documenter les canaux, puissances et adresses.

## 10. Diagnostic Wi-Fi sous Linux

La commande `nmcli` de NetworkManager permet de lister les réseaux visibles :

```bash
nmcli dev wifi
```

On peut aussi demander une liste plus détaillée :

```bash
nmcli device wifi list
```

Avec `iw` :

```bash
iw dev
iw dev wlan0 link
iw dev wlan0 scan | less
```

Avec `iwlist` sur d'anciens systèmes :

```bash
iwlist wlan0 scan
```

Sous Windows :

```powershell
netsh wlan show networks
netsh wlan show interfaces
```

Ces commandes montrent le SSID, le BSSID, le canal, la fréquence, le signal et
parfois la sécurité. Elles permettent de vérifier si le client voit la borne
attendue et sur quel canal elle émet.

### Interpréter les résultats

- Un signal faible associé à un débit élevé est souvent instable.
- Deux bornes sur le même canal se partagent le temps radio.
- Un canal large peut sembler rapide mais créer plus de contention.
- Un client qui reste sur une borne lointaine peut nécessiter du band steering
  ou un seuil RSSI.

## 11. Sécurité et attaques courantes

### Rogue AP

Un point d'accès non autorisé peut être branché par un utilisateur ou installé
par un attaquant. Il peut contourner les politiques du réseau. On le détecte
par la surveillance radio et les inventaires.

### Evil twin

Un attaquant diffuse un SSID qui ressemble au réseau légitime pour récupérer des
identifiants. WPA3 et la vigilance des utilisateurs réduisent le risque, mais
la sensibilisation reste essentielle.

### Déauthentification

Des trames de gestion mal protégées peuvent servir à déconnecter des clients.
PMF et WPA3 renforcent la protection des trames de gestion.

### Bonnes pratiques

- Utiliser WPA3 ou WPA2-AES.
- Activer PMF quand c'est possible.
- Désactiver les SSID inutilisés.
- Isoler le réseau invité.
- Mettre à jour les firmwares.
- Surveiller les BSSID inconnus.
- Ne pas partager la clé PSK de l'entreprise.

## 12. Cas concrets

### Cas 1 : Wi-Fi lent dans un open space

Le signal est fort, mais le débit est faible. On découvre que toutes les bornes
sont sur le même canal 5 GHz et que les canaux font 80 MHz. On réduit à 40 MHz,
on répartit les canaux et on baisse la puissance des bornes trop proches. La
contention diminue.

### Cas 2 : téléphone qui ne passe pas d'une borne à l'autre

Le téléphone reste accroché à une borne éloignée. On vérifie la couverture, on
active 802.11k/v et on ajuste le seuil de roaming. On évite aussi de baisser
trop la puissance au point de créer des trous.

### Cas 3 : invités sur le réseau interne

Le SSID invité utilise le même VLAN que les employés. On crée un VLAN invité,
une politique de filtrage et un portail. Les invités n'accèdent plus aux
serveurs internes.

### Cas 4 : WPA2-Personal dans une entreprise

Tous les employés connaissent la même phrase secrète. Un départ ou une fuite
oblige à changer la clé pour tout le monde. On migre vers WPA2/WPA3-Enterprise
avec RADIUS et des identifiants individuels.

### Cas 5 : borne qui redémarre

La borne est alimentée en PoE. Le budget électrique du switch est dépassé quand
plusieurs caméras démarrent. On vérifie le budget PoE, le câble et la classe de
l'alimentation. On répartit les équipements sur plusieurs switches.

## 13. À retenir

- 2,4 GHz porte loin mais est encombré ; 5 GHz offre plus de canaux ; 6 GHz est
  encore plus propre mais réservé aux clients récents.
- Les canaux 1, 6 et 11 sont le plan classique en 2,4 GHz.
- Les canaux 5 GHz peuvent être DFS et doivent libérer la fréquence si un radar
  est détecté.
- WPA2-AES est le minimum ; WPA3-SAE est préférable quand les clients le
  supportent.
- WPA2/WPA3-Enterprise utilise 802.1X et RADIUS.
- Le roaming dépend du client, de la couverture et des mécanismes 802.11k/v/r.
- Le WLC centralise la gestion ; CAPWAP relie les AP légers au contrôleur.
- Un bon Wi-Fi se conçoit avec une étude de couverture et de capacité.
- `nmcli dev wifi` est une commande Linux simple pour voir les réseaux proches.
- La sécurité Wi-Fi ne remplace pas la sécurité des applications et des
  serveurs.

Le Wi-Fi est un réseau radio : on ne le règle pas seulement avec des valeurs de
puissance, on l'observe, on mesure et on vérifie le résultat sur les clients.
