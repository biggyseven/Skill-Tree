# VPN WireGuard — Débutant

**Niveau :** DÉBUTANT

Un VPN (réseau privé virtuel) crée un chemin logique protégé à travers un réseau qui n’est pas entièrement fiable, comme Internet. WireGuard est une technologie de tunnel VPN moderne conçue pour être relativement simple à configurer, avec un petit ensemble de primitives cryptographiques et une association claire entre les clés publiques des pairs et les adresses IP autorisées.

Ce cours apprend à comprendre les éléments d’un tunnel WireGuard, à distinguer les clés publiques et privées, à lire un fichier de configuration, à établir un tunnel entre deux machines Linux et à diagnostiquer les problèmes courants. Les commandes sont des exemples de laboratoire : adapte les interfaces, les adresses, le pare-feu et la méthode de gestion du réseau à ton système.

> **Analogie** : imagine deux bâtiments qui possèdent chacun une porte sécurisée. Chaque porte a une identité publique que l’autre bâtiment connaît, mais seul le bâtiment garde la clé privée de sa propre porte. Lorsqu’un message doit passer, WireGuard vérifie l’identité du pair, chiffre le paquet puis l’envoie à travers le réseau public. Le réseau intermédiaire transporte le paquet, mais ne doit pas pouvoir lire le trafic intérieur.

> **Piège :** un tunnel peut être configuré sans être réellement opérationnel. La présence d’une interface `wg0` ne prouve ni que le pair est joignable, ni qu’un échange cryptographique récent a eu lieu, ni que le routage permet à l’application d’atteindre sa destination.

---

## 1. La théorie et les mécanismes

### 1.1 À quoi sert WireGuard ?

WireGuard est un protocole de VPN opérant au niveau IP (couche 3). Il transporte des paquets IP à l’intérieur de paquets protégés et encapsulés dans UDP. Il peut relier deux appareils, un poste distant à un réseau d’entreprise ou plusieurs sites, sous réserve de configurer également le routage, le pare-feu et le transfert IP nécessaires.

Usages fréquents :

- **Accès distant** : un ordinateur ou un téléphone rejoint un réseau privé depuis l’extérieur.
- **Site-à-site** : deux routeurs assurent l’échange entre les sous-réseaux de deux sites.
- **Protection d’un flux applicatif** : un hôte utilise une adresse privée atteignable uniquement à travers le tunnel.
- **Connexion entre environnements** : des machines ou serveurs communiquent via des adresses et des clés définies explicitement.

WireGuard ne remplace pas toutes les fonctions de sécurité d’un réseau. Il ne configure pas automatiquement les politiques de pare-feu, les identités des utilisateurs, les règles d’accès applicatives, la haute disponibilité ou les règles de journalisation. Il protège un chemin de communication ; il faut encore décider qui peut joindre quoi.

### 1.2 Les rôles dans un tunnel

WireGuard utilise le terme **peer** (pair) pour désigner un participant associé à une clé publique. L’appellation « serveur » décrit souvent un hôte qui écoute sur un port UDP public ; « client » décrit souvent un hôte qui initie la communication. Ce ne sont pas deux protocoles différents : les deux côtés disposent d’une interface WireGuard et d’une configuration de pairs.

| Élément | Fonction | Exemple |
|---|---|---|
| Interface WireGuard | Interface réseau virtuelle | `wg0` |
| Clé privée | Identité cryptographique secrète de l’interface locale | Fichier lisible seulement par l’administrateur |
| Clé publique | Identifiant que les autres pairs configurent | Une chaîne base64 dérivée de la clé privée |
| Peer | Participant identifié par sa clé publique | Passerelle d’un autre site |
| Endpoint | Adresse IP ou nom et port UDP vers lesquels envoyer | `198.51.100.10:51820` |
| Adresse du tunnel | Adresse IP attribuée à l’interface WireGuard | `10.80.0.2/24` |
| `AllowedIPs` | Préfixes associés à un pair, pour le routage sortant et la validation des adresses source entrantes | `10.80.0.1/32` |
| Port d’écoute | Port UDP local où le pair peut recevoir les paquets WireGuard | `51820` dans les exemples |
| Keepalive persistant | Paquets périodiques facultatifs pour conserver un état NAT ou pare-feu | `25` secondes dans certains scénarios |

Les adresses `198.51.100.0/24` et `203.0.113.0/24` utilisées dans ce cours sont des plages réservées à la documentation. Remplace-les par l’adresse publique ou le nom DNS réel de ton serveur de laboratoire.

### 1.3 Architecture générale du tunnel

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-a-flow{fill:none;stroke-dasharray:7 8;stroke-dashoffset:0;animation:wg-a-dash 1.4s linear infinite}.wg-a-dot{animation:wg-a-pulse 1.3s ease-in-out infinite}.wg-a-dot2{animation-delay:.6s}@keyframes wg-a-dash{to{stroke-dashoffset:-30}}@keyframes wg-a-pulse{0%,100%{opacity:.35}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-a-flow,.wg-a-dot{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 300" width="100%" height="auto" role="img" aria-label="Architecture WireGuard : deux réseaux privés sont reliés par deux interfaces WireGuard à travers Internet. Les lignes animées représentent les paquets chiffrés transportés en UDP."><rect x="1" y="1" width="758" height="298" rx="13" fill="#090d14" stroke="#334155"/><text x="24" y="27" fill="#f8fafc" font-size="16" font-weight="700">Tunnel WireGuard — vue d’ensemble</text><rect x="22" y="52" width="205" height="207" rx="12" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="124" y="76" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">Site A</text><rect x="43" y="97" width="163" height="49" rx="8" fill="#172b42" stroke="#60a5fa"/><text x="124" y="117" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">LAN 10.10.0.0/24</text><text x="124" y="134" text-anchor="middle" fill="#cbd5e1" font-size="11">Postes et serveurs</text><rect x="43" y="178" width="163" height="55" rx="8" fill="#123329" stroke="#4ade80"/><text x="124" y="199" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">Interface wg0</text><text x="124" y="217" text-anchor="middle" fill="#bbf7d0" font-size="11">Clé privée A</text><rect x="272" y="83" width="216" height="145" rx="12" fill="#131c2b" stroke="#64748b"/><text x="380" y="109" text-anchor="middle" fill="#f8fafc" font-size="15" font-weight="700">Internet</text><text x="380" y="132" text-anchor="middle" fill="#94a3b8" font-size="12">Réseau de transport</text><path d="M292 151 H468" stroke="#334155" stroke-width="1"/><text x="380" y="176" text-anchor="middle" fill="#cbd5e1" font-size="12">UDP + paquets chiffrés</text><text x="380" y="197" text-anchor="middle" fill="#94a3b8" font-size="11">Le contenu intérieur est protégé</text><rect x="533" y="52" width="205" height="207" rx="12" fill="#111827" stroke="#60a5fa" stroke-width="1.5"/><text x="635" y="76" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">Site B</text><rect x="554" y="97" width="163" height="49" rx="8" fill="#172b42" stroke="#60a5fa"/><text x="635" y="117" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">LAN 10.20.0.0/24</text><text x="635" y="134" text-anchor="middle" fill="#cbd5e1" font-size="11">Postes et serveurs</text><rect x="554" y="178" width="163" height="55" rx="8" fill="#123329" stroke="#4ade80"/><text x="635" y="199" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">Interface wg0</text><text x="635" y="217" text-anchor="middle" fill="#bbf7d0" font-size="11">Clé privée B</text><path class="wg-a-flow" d="M206 204 H272 M488 204 H554" stroke="#4ade80" stroke-width="3"/><circle class="wg-a-dot" cx="244" cy="204" r="5" fill="#4ade80"/><circle class="wg-a-dot wg-a-dot2" cx="516" cy="204" r="5" fill="#4ade80"/><text x="380" y="278" text-anchor="middle" fill="#94a3b8" font-size="11">Le chiffrement ne remplace pas les routes et les règles de pare-feu.</text></svg></div>

Le schéma sépare le réseau intérieur, les interfaces VPN et le réseau public. Les points verts illustrent le transport protégé : ils ne mesurent pas le débit réel et ne prouvent pas à eux seuls que la connectivité fonctionne.

### 1.4 Clés publiques et privées

Chaque interface WireGuard utilise une paire de clés :

- la **clé privée** reste sur l’appareil qui l’a générée ; elle ne doit pas être envoyée à un autre pair ni copiée dans un message de support ;
- la **clé publique** peut être communiquée aux pairs autorisés pour qu’ils sachent quelle identité accepter ;
- la configuration locale enregistre la clé privée de l’interface et les clés publiques des pairs distants.

WireGuard ne fonctionne pas comme un portail de connexion classique avec un nom d’utilisateur et un mot de passe. L’identité réseau repose sur les clés publiques configurées. Pour retirer l’accès à un appareil, on retire sa clé publique des pairs autorisés et on applique le changement de configuration. Il faut aussi tenir à jour l’inventaire des appareils auxquels chaque clé a été remise.

**Générer une paire de clés sur Linux :**

```bash
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

`umask 077` restreint par défaut l’accès aux fichiers créés dans le répertoire courant. Vérifie quand même les permissions, le répertoire choisi et les sauvegardes. La clé privée ne doit pas apparaître dans une capture d’écran ou dans un dépôt Git. La clé publique se calcule à partir de la clé privée : il n’est pas nécessaire de la choisir manuellement.

> **Danger :** une clé privée publiée doit être considérée comme compromise. Génère une nouvelle paire, déploie la nouvelle clé publique sur les pairs concernés, retire l’ancienne identité puis vérifie la connexion. Supprimer seulement le fichier local ne révoque pas une clé déjà copiée ailleurs.

### 1.5 Handshake : comment les pairs se reconnaissent

Avant d’accepter les données, les pairs effectuent une négociation cryptographique (handshake) qui permet de vérifier l’identité attendue et de dériver des clés de session. WireGuard utilise un protocole cryptographique à suite définie, fondé sur le cadre Noise et l’échange de clés Curve25519. Les paquets de données sont protégés par le chiffrement authentifié ChaCha20-Poly1305. D’autres primitives, comme BLAKE2s et HKDF, interviennent dans les mécanismes de hachage et de dérivation de clés.

L’apprenant n’a normalement pas à régler manuellement une liste de suites cryptographiques comme dans certains autres VPN : WireGuard choisit un ensemble réduit et fixe. Cela réduit les erreurs de négociation, mais ne dispense pas de protéger les clés privées, de maintenir le système à jour et de contrôler les pairs autorisés.

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-b-flow{fill:none;stroke-dasharray:8 7;animation:wg-b-dash 1.2s linear infinite}.wg-b-pulse{animation:wg-b-pulse 1.6s ease-in-out infinite}@keyframes wg-b-dash{to{stroke-dashoffset:-30}}@keyframes wg-b-pulse{0%,100%{opacity:.35}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-b-flow,.wg-b-pulse{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 310" width="100%" height="auto" role="img" aria-label="Séquence simplifiée de handshake WireGuard : l’initiateur envoie une initiation, le pair répond, puis des paquets de données chiffrés peuvent circuler dans les deux sens."><rect x="1" y="1" width="738" height="308" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">Handshake et transport des données</text><rect x="22" y="53" width="190" height="54" rx="9" fill="#112b43" stroke="#60a5fa"/><text x="117" y="75" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">Pair A</text><text x="117" y="93" text-anchor="middle" fill="#cbd5e1" font-size="11">Clé privée A</text><rect x="528" y="53" width="190" height="54" rx="9" fill="#123329" stroke="#4ade80"/><text x="623" y="75" text-anchor="middle" fill="#dcfce7" font-size="14" font-weight="700">Pair B</text><text x="623" y="93" text-anchor="middle" fill="#bbf7d0" font-size="11">Clé privée B</text><path class="wg-b-flow" d="M212 130 H528" stroke="#60a5fa" stroke-width="3"/><polygon points="519,123 531,130 519,137" fill="#60a5fa"/><text x="370" y="123" text-anchor="middle" fill="#93c5fd" font-size="12" font-weight="700">1. Initiation</text><path class="wg-b-flow" d="M528 172 H212" stroke="#4ade80" stroke-width="3"/><polygon points="221,165 209,172 221,179" fill="#4ade80"/><text x="370" y="164" text-anchor="middle" fill="#86efac" font-size="12" font-weight="700">2. Réponse</text><rect x="120" y="198" width="500" height="35" rx="8" fill="#17212e" stroke="#64748b"/><text x="370" y="220" text-anchor="middle" fill="#e4e4e7" font-size="12">Vérification cryptographique et dérivation des clés de session</text><path class="wg-b-flow" d="M212 258 H528" stroke="#a78bfa" stroke-width="3"/><polygon points="519,251 531,258 519,265" fill="#a78bfa"/><text x="370" y="249" text-anchor="middle" fill="#c4b5fd" font-size="12" font-weight="700">3. Données protégées</text><circle class="wg-b-pulse" cx="370" cy="258" r="5" fill="#c4b5fd"/><text x="370" y="291" text-anchor="middle" fill="#94a3b8" font-size="11">Représentation pédagogique, pas capture exacte des messages protocolaires.</text></svg></div>

Ce schéma résume l’ordre des événements. Il ne représente pas chaque champ du protocole, et la création d’une interface ne signifie pas qu’un handshake a déjà eu lieu. Il peut se produire quand le trafic vers le pair est émis ou selon le comportement de l’implémentation.

### 1.6 Encapsulation : les paquets intérieurs et extérieurs

WireGuard protège un paquet IP intérieur en le transportant dans un paquet UDP/IP extérieur. L’adresse extérieure permet au paquet d’atteindre l’endpoint sur Internet ; l’adresse intérieure désigne la destination dans le réseau VPN. Le réseau public voit généralement les adresses extérieures, le port UDP et le volume ou le rythme des paquets, mais pas le contenu IP intérieur en clair.

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-c-dash{stroke-dasharray:8 7;animation:wg-c-dash 1.3s linear infinite}@keyframes wg-c-dash{to{stroke-dashoffset:-30}}@media(prefers-reduced-motion:reduce){.wg-c-dash{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 260" width="100%" height="auto" role="img" aria-label="Structure conceptuelle d’un paquet WireGuard : en-tête IP externe, en-tête UDP, message WireGuard et paquet IP intérieur chiffré et authentifié."><rect x="1" y="1" width="738" height="258" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">Encapsulation d’un paquet</text><text x="22" y="56" fill="#94a3b8" font-size="12">Ce que transporte le réseau public</text><rect x="22" y="70" width="140" height="54" rx="7" fill="#15334c" stroke="#60a5fa"/><text x="92" y="92" text-anchor="middle" fill="#dbeafe" font-size="12" font-weight="700">IP externe</text><text x="92" y="109" text-anchor="middle" fill="#cbd5e1" font-size="10">IP source / destination</text><rect x="170" y="70" width="105" height="54" rx="7" fill="#19352d" stroke="#4ade80"/><text x="222" y="92" text-anchor="middle" fill="#dcfce7" font-size="12" font-weight="700">UDP</text><text x="222" y="109" text-anchor="middle" fill="#bbf7d0" font-size="10">Port</text><rect x="283" y="70" width="435" height="54" rx="7" fill="#17212e" stroke="#64748b"/><text x="500" y="92" text-anchor="middle" fill="#e4e4e7" font-size="12" font-weight="700">Message WireGuard</text><text x="500" y="109" text-anchor="middle" fill="#cbd5e1" font-size="10">Transport protégé et informations de protocole</text><path class="wg-c-dash" d="M34 140 H706" stroke="#a78bfa" stroke-width="2"/><text x="22" y="166" fill="#c4b5fd" font-size="12" font-weight="700">À l’intérieur du message de données</text><rect x="22" y="180" width="696" height="48" rx="8" fill="#201a38" stroke="#a78bfa" stroke-width="1.5"/><text x="370" y="200" text-anchor="middle" fill="#ede9fe" font-size="13" font-weight="700">Paquet IP intérieur chiffré et authentifié</text><text x="370" y="216" text-anchor="middle" fill="#c4b5fd" font-size="11">Adresses et charge utile privées protégées dans le transport</text><text x="370" y="246" text-anchor="middle" fill="#94a3b8" font-size="10">Schéma simplifié : les détails varient selon le type de message WireGuard.</text></svg></div>

Le chiffrement ne rend pas invisible l’existence du tunnel. Un pare-feu peut autoriser ou refuser le port UDP extérieur sans connaître les adresses du paquet intérieur. Pour qu’un hôte du LAN distant atteigne un autre LAN, les routeurs doivent encore avoir des routes correctes et autoriser le transfert des paquets après déchiffrement.

### 1.7 `AllowedIPs` : routage et contrôle d’adresse source

`AllowedIPs` est l’un des paramètres les plus importants, et aussi l’un des plus mal compris. Il associe des préfixes IP à un pair :

1. **Pour l’émission**, WireGuard l’utilise pour sélectionner le pair auquel un paquet destiné à un préfixe sera chiffré, en coordination avec les routes du système.
2. **Pour la réception**, il vérifie que l’adresse IP source du paquet intérieur déchiffré est autorisée pour ce pair.

Autrement dit, `AllowedIPs` participe au routage et au contrôle des sources. Il ne remplace pas toutes les règles de pare-feu et ne constitue pas à lui seul une politique complète d’autorisation applicative.

| Exemple de `AllowedIPs` | Sens pratique courant |
|---|---|
| `10.80.0.2/32` | Une seule adresse de tunnel est associée au peer |
| `10.80.0.0/24` | Toutes les destinations de ce sous-réseau peuvent être envoyées à ce peer, selon les routes installées |
| `192.168.50.0/24` | Le réseau distant `192.168.50.0/24` se trouve derrière le peer |
| `0.0.0.0/0` | Toutes les destinations IPv4 sont candidates à ce peer ; souvent utilisé pour un tunnel IPv4 complet |
| `::/0` | Toutes les destinations IPv6 sont candidates à ce peer |

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-d-flow{stroke-dasharray:8 8;animation:wg-d-dash 1.2s linear infinite}.wg-d-pulse{animation:wg-d-pulse 1.5s ease-in-out infinite}@keyframes wg-d-dash{to{stroke-dashoffset:-32}}@keyframes wg-d-pulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-d-flow,.wg-d-pulse{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 300" width="100%" height="auto" role="img" aria-label="AllowedIPs associe des préfixes à un pair pour l’émission, et vérifie l’adresse source intérieure à la réception."><rect x="1" y="1" width="738" height="298" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">AllowedIPs — deux contrôles complémentaires</text><rect x="22" y="52" width="300" height="95" rx="10" fill="#112b43" stroke="#60a5fa"/><text x="172" y="76" text-anchor="middle" fill="#dbeafe" font-size="14" font-weight="700">Émission</text><text x="172" y="99" text-anchor="middle" fill="#e4e4e7" font-size="12">Destination : 10.80.0.2</text><text x="172" y="119" text-anchor="middle" fill="#93c5fd" font-size="12">Sélection du peer associé</text><rect x="418" y="52" width="300" height="95" rx="10" fill="#123329" stroke="#4ade80"/><text x="568" y="76" text-anchor="middle" fill="#dcfce7" font-size="14" font-weight="700">Réception</text><text x="568" y="99" text-anchor="middle" fill="#e4e4e7" font-size="12">Source intérieure : 10.80.0.2</text><text x="568" y="119" text-anchor="middle" fill="#86efac" font-size="12">Vérification du préfixe autorisé</text><path class="wg-d-flow" d="M172 147 V178 H568 V147" fill="none" stroke="#a78bfa" stroke-width="3"/><circle class="wg-d-pulse" cx="370" cy="178" r="6" fill="#c4b5fd"/><rect x="135" y="207" width="470" height="57" rx="9" fill="#171d29" stroke="#64748b"/><text x="370" y="229" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">Route système + AllowedIPs + pare-feu</text><text x="370" y="247" text-anchor="middle" fill="#cbd5e1" font-size="11">Les trois doivent correspondre à la topologie attendue.</text><text x="370" y="285" text-anchor="middle" fill="#94a3b8" font-size="11">Une route correcte seule ne prouve pas que le peer est joignable.</text></svg></div>

> **Piège :** mettre `AllowedIPs = 0.0.0.0/0` sur un seul côté ne configure pas magiquement tout le réseau distant. Il faut des routes cohérentes, un endpoint accessible, des règles de pare-feu adaptées et, si l’on transporte des réseaux derrière le pair, le routage et le transfert IP correspondant.

### 1.8 Tunnel fractionné et tunnel complet

Avec un **tunnel fractionné** (*split tunnel*), seules les destinations choisies passent par WireGuard. Par exemple, `10.80.0.0/24` peut rejoindre le réseau VPN tandis que la navigation Internet ordinaire continue via le fournisseur local.

Avec un **tunnel complet** (*full tunnel*), on route normalement tout le trafic IP à travers le VPN : `0.0.0.0/0` pour IPv4 et, si l’on veut aussi faire passer IPv6, `::/0`. Un tunnel complet nécessite de comprendre le routage par défaut, le DNS, le pare-feu, la traduction d’adresses si le serveur fait sortir les clients sur Internet, ainsi que la prévention des fuites de trafic en cas de panne.

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-e-flow{fill:none;stroke-dasharray:7 8;animation:wg-e-dash 1.1s linear infinite}.wg-e-dot{animation:wg-e-glow 1.5s ease-in-out infinite}@keyframes wg-e-dash{to{stroke-dashoffset:-30}}@keyframes wg-e-glow{0%,100%{opacity:.25}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-e-flow,.wg-e-dot{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 320" width="100%" height="auto" role="img" aria-label="Comparaison de split tunnel et full tunnel : une destination privée utilise WireGuard dans les deux cas, tandis que l’accès Internet général passe par le réseau local en split tunnel et par le VPN en full tunnel."><rect x="1" y="1" width="738" height="318" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">Deux politiques de routage côté client</text><rect x="22" y="48" width="337" height="246" rx="11" fill="#111827" stroke="#60a5fa"/><text x="190" y="73" text-anchor="middle" fill="#bfdbfe" font-size="14" font-weight="700">Tunnel fractionné</text><rect x="48" y="93" width="112" height="42" rx="7" fill="#172b42" stroke="#60a5fa"/><text x="104" y="110" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="700">Client</text><text x="104" y="125" text-anchor="middle" fill="#cbd5e1" font-size="10">Poste local</text><rect x="213" y="92" width="119" height="44" rx="7" fill="#123329" stroke="#4ade80"/><text x="272" y="109" text-anchor="middle" fill="#dcfce7" font-size="11" font-weight="700">Réseau privé</text><text x="272" y="124" text-anchor="middle" fill="#bbf7d0" font-size="10">via VPN</text><path class="wg-e-flow" d="M160 110 H213" stroke="#4ade80" stroke-width="3"/><circle class="wg-e-dot" cx="186" cy="110" r="5" fill="#4ade80"/><rect x="213" y="181" width="119" height="44" rx="7" fill="#17212e" stroke="#64748b"/><text x="272" y="198" text-anchor="middle" fill="#e4e4e7" font-size="11" font-weight="700">Internet</text><text x="272" y="213" text-anchor="middle" fill="#cbd5e1" font-size="10">via accès local</text><path class="wg-e-flow" d="M104 135 V203 H213" stroke="#94a3b8" stroke-width="2.5"/><text x="190" y="257" text-anchor="middle" fill="#94a3b8" font-size="11">Seuls certains préfixes passent dans wg0.</text><rect x="381" y="48" width="337" height="246" rx="11" fill="#111827" stroke="#a78bfa"/><text x="549" y="73" text-anchor="middle" fill="#ddd6fe" font-size="14" font-weight="700">Tunnel complet</text><rect x="406" y="93" width="112" height="42" rx="7" fill="#172b42" stroke="#60a5fa"/><text x="462" y="110" text-anchor="middle" fill="#f8fafc" font-size="11" font-weight="700">Client</text><text x="462" y="125" text-anchor="middle" fill="#cbd5e1" font-size="10">Poste local</text><rect x="570" y="88" width="121" height="58" rx="7" fill="#201a38" stroke="#a78bfa"/><text x="630" y="107" text-anchor="middle" fill="#ede9fe" font-size="11" font-weight="700">VPN / sortie</text><text x="630" y="123" text-anchor="middle" fill="#ddd6fe" font-size="10">Réseau privé</text><text x="630" y="136" text-anchor="middle" fill="#ddd6fe" font-size="10">et Internet</text><path class="wg-e-flow" d="M518 110 H570" stroke="#a78bfa" stroke-width="3"/><circle class="wg-e-dot" cx="544" cy="110" r="5" fill="#c4b5fd"/><path class="wg-e-flow" d="M462 135 V202 H630 V146" stroke="#a78bfa" stroke-width="2.5"/><text x="549" y="231" text-anchor="middle" fill="#c4b5fd" font-size="11">Routes et DNS à planifier ensemble</text><text x="370" y="309" text-anchor="middle" fill="#94a3b8" font-size="11">Le chemin réel dépend de la table de routage et de la politique du système.</text></svg></div>

> **Astuce :** commence avec un tunnel fractionné minimal entre deux adresses de laboratoire. Une fois que le handshake, le ping et le routage fonctionnent, étudie le tunnel complet séparément. Cette progression permet de distinguer un défaut WireGuard d’un défaut de routage par défaut ou de DNS.

### 1.9 NAT et `PersistentKeepalive`

Un appareil derrière un routeur NAT peut ne pas avoir d’adresse publiquement joignable. S’il émet des paquets vers un endpoint WireGuard public, le NAT crée généralement une association temporaire. Si cette association expire et que le pair distant n’émet rien, la réception peut échouer jusqu’à ce qu’un nouveau paquet sorte du réseau privé.

`PersistentKeepalive` envoie périodiquement un petit paquet authentifié quand cela est nécessaire. Une valeur de 25 secondes est souvent utilisée pour maintenir une association NAT, mais ce n’est pas une obligation pour tous les pairs. Il faut considérer les règles du réseau, la consommation de batterie et la politique du service. Le keepalive n’est ni un chiffrement supplémentaire ni un mécanisme de supervision complet.

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-f-path{fill:none;stroke-dasharray:7 8;animation:wg-f-dash 1.2s linear infinite}.wg-f-packet{animation:wg-f-pulse 1.4s ease-in-out infinite}@keyframes wg-f-dash{to{stroke-dashoffset:-30}}@keyframes wg-f-pulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-f-path,.wg-f-packet{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 285" width="100%" height="auto" role="img" aria-label="Un client WireGuard derrière un NAT envoie un paquet UDP au serveur public. Un keepalive facultatif entretient l’association NAT si aucun trafic utile ne circule."><rect x="1" y="1" width="738" height="283" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">Peer derrière NAT</text><rect x="22" y="62" width="150" height="72" rx="9" fill="#112b43" stroke="#60a5fa"/><text x="97" y="84" text-anchor="middle" fill="#dbeafe" font-size="13" font-weight="700">Client</text><text x="97" y="103" text-anchor="middle" fill="#cbd5e1" font-size="11">Adresse privée</text><text x="97" y="119" text-anchor="middle" fill="#93c5fd" font-size="10">wg0</text><rect x="218" y="62" width="150" height="72" rx="9" fill="#17212e" stroke="#64748b"/><text x="293" y="84" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">Routeur NAT</text><text x="293" y="103" text-anchor="middle" fill="#cbd5e1" font-size="11">Association UDP</text><text x="293" y="119" text-anchor="middle" fill="#94a3b8" font-size="10">Peut expirer</text><rect x="415" y="62" width="300" height="72" rx="9" fill="#123329" stroke="#4ade80"/><text x="565" y="84" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">Endpoint WireGuard public</text><text x="565" y="103" text-anchor="middle" fill="#bbf7d0" font-size="11">Adresse publique : port UDP</text><text x="565" y="119" text-anchor="middle" fill="#86efac" font-size="10">Exemple : 198.51.100.10:51820</text><path class="wg-f-path" d="M172 95 H218 M368 95 H415" stroke="#4ade80" stroke-width="3"/><circle class="wg-f-packet" cx="194" cy="95" r="5" fill="#4ade80"/><circle class="wg-f-packet" cx="390" cy="95" r="5" fill="#4ade80"/><rect x="91" y="172" width="558" height="62" rx="9" fill="#171d29" stroke="#a78bfa"/><text x="370" y="194" text-anchor="middle" fill="#ede9fe" font-size="13" font-weight="700">PersistentKeepalive = 25 (si nécessaire)</text><text x="370" y="214" text-anchor="middle" fill="#c4b5fd" font-size="11">Évite parfois l’expiration de l’association NAT en période d’inactivité.</text><path class="wg-f-path" d="M565 134 V152 H649 V204 H649" stroke="#a78bfa" stroke-width="2"/><text x="370" y="261" text-anchor="middle" fill="#94a3b8" font-size="11">Le keepalive ne remplace pas la vérification du handshake et du trafic utile.</text></svg></div>

### 1.10 Les limites à connaître

WireGuard fournit un tunnel IP protégé, mais certaines fonctions doivent venir d’autres composants :

- **Gestion des utilisateurs** : les clés publiques identifient les pairs ; l’authentification d’un utilisateur et l’attribution de comptes ne sont pas un portail intégrés au protocole.
- **Distribution et révocation des clés** : il faut un processus sûr pour générer, livrer, faire tourner et révoquer les clés.
- **Routage et pare-feu** : un tunnel ne rend pas automatiquement les sous-réseaux mutuellement joignables.
- **Masquage du protocole** : WireGuard n’est pas conçu comme un protocole d’obfuscation ; son transport normal utilise UDP. Il ne fournit pas nativement un mode TCP.
- **Post-quantique** : WireGuard n’est pas post-quantique par défaut. Ne le présente pas comme protégé contre tous les scénarios cryptographiques futurs.
- **Disponibilité** : l’existence d’un tunnel ne protège pas contre une panne Internet, une surcharge de serveur ou une erreur de routage.

> **Danger :** ne transforme pas les exemples de laboratoire en règles universelles. Les plages `AllowedIPs`, le transfert IP, les règles NAT, les routes par défaut et les règles de pare-feu peuvent exposer un réseau entier s’ils sont copiés sans analyse.

---

## 2. Configuration et pratique

### 2.1 Préparer le laboratoire

Le laboratoire minimal utilise deux hôtes Linux : un serveur WireGuard disposant d’un endpoint joignable et un client qui initie la connexion. Les adresses publiques ci-dessous sont réservées à la documentation et doivent être remplacées.

| Paramètre | Serveur | Client |
|---|---|---|
| Adresse du tunnel | `10.80.0.1/24` | `10.80.0.2/24` |
| Port UDP | `51820` | Port éphémère côté NAT ou pare-feu |
| Endpoint public | `198.51.100.10:51820` | Se connecte à l’endpoint serveur |
| Clé privée | Générée localement sur le serveur | Générée localement sur le client |
| Clé publique du peer | Clé publique du client | Clé publique du serveur |
| `AllowedIPs` minimal côté peer | `10.80.0.2/32` | `10.80.0.1/32` |

Prérequis : accès administrateur, packages WireGuard installés, synchronisation de l’heure correcte, routes IP de base fonctionnelles et capacité à autoriser le port UDP côté serveur. Les commandes d’installation diffèrent selon la distribution. Sur Debian/Ubuntu, le paquet est généralement nommé `wireguard`.

```bash
sudo apt update
sudo apt install wireguard
```

Cette commande est adaptée aux distributions Debian et Ubuntu. Sur d’autres systèmes, utilise le gestionnaire de paquets documenté par la distribution ou l’outil d’installation officiel.

### 2.2 Générer les clés en toute sécurité

Sur chacun des deux hôtes, crée un répertoire de configuration protégé puis génère une paire de clés :

```bash
sudo install -d -m 700 /etc/wireguard
cd /etc/wireguard
umask 077
wg genkey | tee privatekey | wg pubkey > publickey
```

Si les permissions et l’appartenance des fichiers ne sont pas celles attendues après l’exécution, corrige-les avant d’utiliser la clé. Vérifie les permissions avec `ls -l` et conserve la clé privée dans un emplacement protégé. Copie uniquement la clé publique de chaque côté. Dans une procédure réelle, préfère un mécanisme de distribution authentifié à un canal de messagerie non protégé.

Pour afficher une clé publique :

```bash
cat /etc/wireguard/publickey
```

N’exécute pas `cat` sur la clé privée dans un terminal partagé ou enregistré. Ne mets pas les clés privées dans un dépôt Git ou une archive qui sera envoyée à des tiers.

### 2.3 Configuration du serveur

Crée `/etc/wireguard/wg0.conf` sur le serveur. Remplace `<CLE_PRIVEE_SERVEUR>` par le contenu de la clé privée locale, sans chevrons littéraux, et `<CLE_PUBLIQUE_CLIENT>` par la vraie clé publique du client.

```ini
[Interface]
Address = 10.80.0.1/24
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_SERVEUR>

[Peer]
PublicKey = <CLE_PUBLIQUE_CLIENT>
AllowedIPs = 10.80.0.2/32
```

Le serveur n’a pas besoin d’un `Endpoint` fixe pour un client mobile ou derrière NAT : il peut apprendre l’adresse source du pair à partir de paquets correctement authentifiés. Cela ne dispense pas le client de pouvoir joindre le port d’écoute du serveur. Pour plusieurs clients, chaque client possède une clé publique distincte et un ensemble `AllowedIPs` non ambigu pour la topologie choisie.

Protège le fichier, car il contient la clé privée :

```bash
sudo chown root:root /etc/wireguard/wg0.conf
sudo chmod 600 /etc/wireguard/wg0.conf
```

### 2.4 Configuration du client

Sur le client, crée son propre `/etc/wireguard/wg0.conf`. Remplace les placeholders par les clés réelles et remplace l’adresse publique de documentation par l’endpoint effectif.

```ini
[Interface]
Address = 10.80.0.2/24
PrivateKey = <CLE_PRIVEE_CLIENT>

[Peer]
PublicKey = <CLE_PUBLIQUE_SERVEUR>
Endpoint = 198.51.100.10:51820
AllowedIPs = 10.80.0.1/32
PersistentKeepalive = 25
```

`PersistentKeepalive = 25` est utile dans certains scénarios où le client est derrière NAT ou un pare-feu qui expire rapidement les associations UDP. Si le client dispose d’une connectivité directe et stable, cette option peut être omise. Elle doit être définie selon le besoin réel, et pas ajoutée automatiquement à chaque configuration.

Le fichier de configuration du client doit aussi être protégé :

```bash
sudo chown root:root /etc/wireguard/wg0.conf
sudo chmod 600 /etc/wireguard/wg0.conf
```

### 2.5 Ouvrir le port côté serveur

Le pare-feu du serveur doit autoriser le trafic UDP entrant sur le port d’écoute choisi, ici `51820/udp`. Si le serveur se trouve derrière un routeur NAT, configure également la redirection UDP vers le bon hôte et vérifie que l’adresse d’endpoint est bien celle visible depuis le client.

Exemple de vérification avec UFW, si UFW est le pare-feu utilisé :

```bash
sudo ufw allow 51820/udp
sudo ufw status verbose
```

N’exécute pas ces commandes sans comprendre les règles existantes et le périmètre d’exposition. Le pare-feu peut être géré par nftables, firewalld, un routeur cloud ou un équipement dédié. Autorise seulement le port et les destinations requis.

### 2.6 Démarrer et observer le tunnel

Sur le serveur puis sur le client :

```bash
sudo wg-quick up wg0
```

Pour afficher l’état :

```bash
sudo wg show
ip address show dev wg0
ip route
```

`wg-quick` configure l’interface, son adresse et les routes déduites de la configuration. Il ne remplace pas un plan de routage plus complet dans les topologies complexes. Si le tunnel est déjà démarré, évite de réexécuter `wg-quick up wg0` sans raison ; utilise plutôt les commandes d’inspection prévues.

Depuis le client, teste l’adresse de tunnel du serveur :

```bash
ping -c 4 10.80.0.1
```

Le ping peut être bloqué par le pare-feu même lorsque le tunnel fonctionne. Dans ce cas, vérifie aussi les compteurs WireGuard, les règles de filtrage et un test applicatif autorisé. La réussite du ping confirme une connectivité ICMP dans ce scénario, pas toutes les applications ni tous les sous-réseaux.

Pour observer l’état WireGuard :

```bash
sudo wg show wg0
```

Cherche notamment : le port d’écoute, la clé publique attendue du peer, `endpoint` si un endpoint est connu, `latest handshake` et les volumes `transfer`. Un handshake récent et des compteurs croissants sont des indices utiles, mais doivent être rapprochés du test applicatif attendu.

### 2.7 Démarrer automatiquement au redémarrage

Sur un système utilisant systemd et `wg-quick`, on peut activer le service :

```bash
sudo systemctl enable --now wg-quick@wg0
sudo systemctl status wg-quick@wg0
```

Choisis une seule méthode cohérente pour gérer l’interface : ne mélange pas sans plan `wg-quick`, une configuration NetworkManager et des scripts personnalisés qui modifient simultanément les mêmes routes. Si le service échoue, lis ses journaux avant d’effectuer des changements :

```bash
sudo journalctl -u wg-quick@wg0 --no-pager -n 80
```

### 2.8 Faire passer un sous-réseau distant

Pour un scénario site-à-site, supposons que le serveur soit la passerelle du réseau `192.168.10.0/24` et que le client soit la passerelle du réseau `192.168.20.0/24`. Il faut alors plus que les deux adresses de tunnel : les routes et `AllowedIPs` doivent associer les LAN distants au bon pair.

Par exemple, côté serveur, l’entrée peer du client peut inclure :

```ini
[Peer]
PublicKey = <CLE_PUBLIQUE_CLIENT>
AllowedIPs = 10.80.0.2/32, 192.168.20.0/24
```

Côté client, l’entrée peer du serveur peut inclure :

```ini
[Peer]
PublicKey = <CLE_PUBLIQUE_SERVEUR>
Endpoint = 198.51.100.10:51820
AllowedIPs = 10.80.0.1/32, 192.168.10.0/24
PersistentKeepalive = 25
```

La passerelle serveur doit connaître le chemin vers `192.168.20.0/24` via WireGuard, et la passerelle client doit connaître le chemin vers `192.168.10.0/24`. Il faut activer le transfert IP sur les passerelles, autoriser le trafic dans les chaînes `FORWARD` ou les règles équivalentes, et vérifier les routes de retour. Le masquerading NAT n’est pas automatiquement nécessaire : il dépend de la topologie et de la façon dont les réseaux distants connaissent les routes de retour.

> **Piège :** ajouter un LAN dans `AllowedIPs` ne crée pas automatiquement une route de retour sur les machines du LAN. Vérifie aussi la passerelle par défaut de chaque hôte et les routes sur les routeurs intermédiaires.

### 2.9 Tunnel complet vers Internet

Pour un client qui doit diriger tout le trafic IPv4 par un serveur VPN, la section peer du client peut utiliser `AllowedIPs = 0.0.0.0/0`. Pour faire aussi passer IPv6, il faut traiter `::/0` et le routage IPv6 de manière cohérente. La configuration exacte dépend de la distribution, du client et de la manière dont `wg-quick` gère le routage.

Le serveur doit alors pouvoir transférer le trafic, appliquer des règles de pare-feu appropriées et fournir une sortie vers Internet. Selon la topologie, une traduction source NAT peut être nécessaire à la sortie du serveur. Le DNS doit être configuré et testé séparément. Une politique de type *kill switch* doit être conçue avec soin si l’objectif est d’empêcher tout trafic de sortir hors VPN pendant une panne.

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-g-flow{fill:none;stroke-dasharray:7 8;animation:wg-g-dash 1.2s linear infinite}.wg-g-dot{animation:wg-g-pulse 1.4s ease-in-out infinite}@keyframes wg-g-dash{to{stroke-dashoffset:-30}}@keyframes wg-g-pulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-g-flow,.wg-g-dot{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 300" width="100%" height="auto" role="img" aria-label="Étapes de configuration WireGuard : générer les clés, distribuer uniquement les clés publiques, configurer les AllowedIPs, autoriser l’endpoint UDP et démarrer puis vérifier le tunnel."><rect x="1" y="1" width="738" height="298" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">Ordre de configuration conseillé</text><rect x="22" y="55" width="210" height="61" rx="9" fill="#112b43" stroke="#60a5fa"/><text x="127" y="79" text-anchor="middle" fill="#dbeafe" font-size="13" font-weight="700">1. Générer les clés</text><text x="127" y="98" text-anchor="middle" fill="#cbd5e1" font-size="11">Une paire sur chaque hôte</text><rect x="265" y="55" width="210" height="61" rx="9" fill="#123329" stroke="#4ade80"/><text x="370" y="79" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">2. Échanger les clés publiques</text><text x="370" y="98" text-anchor="middle" fill="#bbf7d0" font-size="11">Jamais la clé privée</text><rect x="508" y="55" width="210" height="61" rx="9" fill="#201a38" stroke="#a78bfa"/><text x="613" y="79" text-anchor="middle" fill="#ede9fe" font-size="13" font-weight="700">3. Définir les peers</text><text x="613" y="98" text-anchor="middle" fill="#ddd6fe" font-size="11">Endpoint et AllowedIPs</text><path class="wg-g-flow" d="M232 85 H265 M475 85 H508" stroke="#94a3b8" stroke-width="2.5"/><rect x="105" y="164" width="230" height="61" rx="9" fill="#17212e" stroke="#64748b"/><text x="220" y="188" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">4. Autoriser UDP</text><text x="220" y="207" text-anchor="middle" fill="#cbd5e1" font-size="11">Pare-feu / NAT / routes</text><rect x="405" y="164" width="230" height="61" rx="9" fill="#123329" stroke="#4ade80"/><text x="520" y="188" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">5. Démarrer et vérifier</text><text x="520" y="207" text-anchor="middle" fill="#bbf7d0" font-size="11">Handshake, transfert, ping</text><path class="wg-g-flow" d="M613 116 V139 H220 V164 M335 194 H405" stroke="#4ade80" stroke-width="2.5"/><circle class="wg-g-dot" cx="370" cy="139" r="5" fill="#4ade80"/><text x="370" y="263" text-anchor="middle" fill="#94a3b8" font-size="11">Valider une étape avant de dépanner la suivante.</text><text x="370" y="282" text-anchor="middle" fill="#94a3b8" font-size="11">Conserver une copie des configurations sans les secrets.</text></svg></div>

### 2.10 MTU, IPv6 et DNS

Le tunnel ajoute de l’encapsulation au paquet intérieur, ce qui réduit la place disponible pour sa charge utile par rapport à un paquet envoyé directement sur le lien externe. Une MTU inadaptée peut produire un symptôme trompeur : le ping de petite taille fonctionne, mais les transferts plus volumineux ralentissent ou échouent. Il faut mesurer avant de choisir une MTU ou de modifier le MSS TCP.

IPv6 doit être traité explicitement. Si le tunnel n’autorise que des préfixes IPv4, le trafic IPv6 peut continuer par une route locale hors tunnel. C’est parfois voulu, parfois une fuite contraire à la politique. La présence d’une adresse IPv6 sur l’interface ne signifie pas que les routes IPv6 ou le pare-feu sont correctement configurés.

Le DNS doit aussi être inclus dans le plan : quel résolveur l’hôte utilise-t-il, est-il joignable par le tunnel, et les noms privés sont-ils réservés aux clients autorisés ? Un handshake réussi ne prouve pas que le DNS fonctionne.

---

## 3. Dépannage et sécurité

### 3.1 Méthode de diagnostic en couches

Diagnostique dans cet ordre afin de ne pas modifier plusieurs variables en même temps :

1. **État local** : l’interface existe-t-elle et a-t-elle la bonne adresse ?
2. **Configuration** : les clés publiques sont-elles exactes ? Le peer et ses préfixes `AllowedIPs` correspondent-ils à la topologie ?
3. **Transport externe** : l’endpoint est-il correct ? L’UDP d’écoute arrive-t-il au serveur ? Le NAT ou le pare-feu bloque-t-il le trafic ?
4. **Handshake** : `wg show` affiche-t-il un handshake récent ?
5. **Compteurs** : les octets envoyés et reçus augmentent-ils quand le test est lancé ?
6. **Routage** : la destination utilise-t-elle l’interface prévue ? Y a-t-il une route retour ?
7. **Pare-feu et application** : les paquets sont-ils autorisés après déchiffrement et le service répond-il ?

<div style="background:#090d14;color:#e4e4e7;border:1px solid #334155;border-radius:16px;padding:12px;max-width:100%;overflow:hidden" bgcolor="#090d14"><style>.wg-h-flow{fill:none;stroke-dasharray:7 8;animation:wg-h-dash 1.2s linear infinite}.wg-h-pulse{animation:wg-h-pulse 1.5s ease-in-out infinite}@keyframes wg-h-dash{to{stroke-dashoffset:-28}}@keyframes wg-h-pulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-h-flow,.wg-h-pulse{animation:none!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 740 420" width="100%" height="auto" role="img" aria-label="Arbre de dépannage WireGuard : vérifier d’abord l’interface, ensuite l’endpoint et le handshake, puis les AllowedIPs, les routes, le pare-feu et l’application."><rect x="1" y="1" width="738" height="418" rx="13" fill="#090d14" stroke="#334155"/><text x="22" y="28" fill="#f8fafc" font-size="16" font-weight="700">Trouver la première couche en échec</text><rect x="205" y="48" width="330" height="44" rx="8" fill="#112b43" stroke="#60a5fa"/><text x="370" y="75" text-anchor="middle" fill="#dbeafe" font-size="13" font-weight="700">1. Interface et configuration locales correctes ?</text><path class="wg-h-flow" d="M370 92 V113" stroke="#60a5fa" stroke-width="2.5"/><polygon points="364,107 370,116 376,107" fill="#60a5fa"/><rect x="205" y="117" width="330" height="44" rx="8" fill="#17212e" stroke="#64748b"/><text x="370" y="144" text-anchor="middle" fill="#f8fafc" font-size="13" font-weight="700">2. Endpoint UDP joignable ?</text><path class="wg-h-flow" d="M370 161 V182" stroke="#60a5fa" stroke-width="2.5"/><polygon points="364,176 370,185 376,176" fill="#60a5fa"/><rect x="205" y="186" width="330" height="44" rx="8" fill="#123329" stroke="#4ade80"/><text x="370" y="213" text-anchor="middle" fill="#dcfce7" font-size="13" font-weight="700">3. Handshake récent ?</text><path class="wg-h-flow" d="M370 230 V251" stroke="#4ade80" stroke-width="2.5"/><polygon points="364,245 370,254 376,245" fill="#4ade80"/><rect x="205" y="255" width="330" height="44" rx="8" fill="#201a38" stroke="#a78bfa"/><text x="370" y="282" text-anchor="middle" fill="#ede9fe" font-size="13" font-weight="700">4. Compteurs et AllowedIPs cohérents ?</text><path class="wg-h-flow" d="M370 299 V320" stroke="#a78bfa" stroke-width="2.5"/><polygon points="364,314 370,323 376,314" fill="#a78bfa"/><rect x="205" y="324" width="330" height="44" rx="8" fill="#3a2b12" stroke="#fbbf24"/><text x="370" y="351" text-anchor="middle" fill="#fef3c7" font-size="13" font-weight="700">5. Route retour, pare-feu, MTU, DNS</text><path class="wg-h-flow" d="M535 139 H584 V207 H605" stroke="#f87171" stroke-width="2.5"/><rect x="581" y="182" width="137" height="53" rx="8" fill="#351b22" stroke="#fb7185"/><text x="649" y="203" text-anchor="middle" fill="#fecdd3" font-size="11" font-weight="700">Sans handshake</text><text x="649" y="219" text-anchor="middle" fill="#fda4af" font-size="10">Transport / clés</text><circle class="wg-h-pulse" cx="370" cy="390" r="5" fill="#4ade80"/><text x="386" y="394" fill="#94a3b8" font-size="11">Toujours confirmer par un test applicatif attendu.</text></svg></div>

### 3.2 Interface absente ou service en erreur

Commandes utiles :

```bash
ip link show wg0
ip address show dev wg0
sudo wg show
sudo systemctl status wg-quick@wg0
sudo journalctl -u wg-quick@wg0 --no-pager -n 80
```

Causes possibles : paquet absent, faute de frappe dans la configuration, permission trop large ou trop restrictive, clé privée mal copiée, adresse déjà utilisée, interface déjà créée par un autre gestionnaire réseau, ou règle `PostUp` qui échoue. Corrige la première erreur signalée et redémarre proprement l’interface seulement lorsque c’est nécessaire.

### 3.3 Aucun handshake récent

Si `wg show` indique `latest handshake: (none)` ou une date trop ancienne pendant que tu génères du trafic, vérifie :

- l’adresse et le port de l’endpoint distant ;
- la présence du port UDP autorisé sur le pare-feu et, s’il existe, du transfert de port NAT ;
- le fait que la clé publique du peer configurée d’un côté corresponde à la clé privée locale de l’autre côté ;
- l’heure système et l’état des services ;
- la route externe vers l’endpoint, particulièrement si une route par défaut est elle-même dirigée dans le tunnel ;
- la bonne interface et le bon fichier `wg0.conf` sont-ils actifs ?

Capturer le trafic extérieur peut aider. Exemple de lecture uniquement :

```bash
sudo tcpdump -ni any udp port 51820
```

Sur le serveur, observe si les datagrammes arrivent quand le client essaie de communiquer. Une capture de paquets peut contenir des métadonnées sensibles ; limite son périmètre, protège le fichier éventuel et ne la publie pas sans nettoyage. Ne partage jamais la clé privée dans un rapport d’incident.

### 3.4 Handshake récent, mais aucun trafic utile

Si un handshake est récent, passe à l’analyse du trafic intérieur :

```bash
sudo wg show
ip route get 10.80.0.1
ip route get 192.168.10.10
ip -s link show wg0
```

Les destinations ci-dessus sont des exemples à remplacer par celles du laboratoire. Vérifie que `AllowedIPs` inclut le préfixe attendu, que la table de routage envoie le paquet dans l’interface VPN et que l’adresse source utilisée correspond à un préfixe autorisé chez le peer distant.

Pour un LAN, vérifie également le transfert IP sur chaque passerelle, les routes de retour et les règles du pare-feu. Une réponse peut être bloquée par l’hôte distant même si les paquets traversent correctement le tunnel. Fais un test depuis chaque extrémité et distingue le ping de tunnel du test entre les hôtes LAN.

### 3.5 Le tunnel marche, mais les gros transferts échouent

Un tunnel peut transporter de petits paquets tout en échouant sur des paquets volumineux. Les causes possibles incluent une MTU trop élevée, le blocage de messages ICMP nécessaires à la découverte de MTU, un problème PMTUD ou une valeur MSS incohérente. Ne baisse pas aveuglément la MTU de tout le réseau : mesure le comportement le long du chemin et teste les tailles avec prudence.

Pour les connexions TCP, le MSS peut être ajusté au niveau approprié du pare-feu ou du routage. Les options exactes dépendent de la distribution et de la politique réseau. Documente la valeur retenue et teste à nouveau des transferts de tailles différentes.

### 3.6 Le DNS ne fonctionne pas

Si un ping par adresse IP fonctionne mais qu’un nom ne se résout pas, la cause peut être DNS, pas WireGuard. Vérifie le résolveur configuré sur le client, la route vers le serveur DNS, le pare-feu UDP/TCP 53, le domaine de recherche et les règles de split DNS. Certains clients et gestionnaires système appliquent les paramètres DNS différemment ; la directive `DNS` est gérée par `wg-quick` dans les environnements qui la prennent en charge, pas par le protocole WireGuard abstrait lui-même.

### 3.7 Les causes fréquentes classées par symptôme

| Symptôme | Première vérification | Couche à examiner ensuite |
|---|---|---|
| Aucun handshake | Endpoint UDP, clés publiques, pare-feu | NAT, route externe, service serveur |
| Handshake récent, zéro octet reçu | `AllowedIPs`, source/destination | Routes retour, règles de transfert |
| Ping tunnel OK, LAN distant inaccessible | Routes vers le LAN | IP forwarding, pare-feu `FORWARD`, passerelle du LAN |
| Petit ping OK, gros transfert bloqué | MTU / PMTUD | MSS, filtrage ICMP, chemin WAN |
| IP accessible, nom inaccessible | Serveur DNS configuré | Routage DNS, ACL, split DNS |
| Connexion perdue après inactivité | Endpoint et association NAT | `PersistentKeepalive`, expiration de state |
| Un client voit trop de sous-réseaux | `AllowedIPs` et routes | Pare-feu, segmentation, autorisation applicative |

### 3.8 Sécurité et hygiène opérationnelle

1. **Protéger les clés privées** avec les permissions minimales, un stockage secret et une procédure de rotation.
2. **Restreindre `AllowedIPs`** aux préfixes nécessaires. Ne pas utiliser `0.0.0.0/0` sans besoin explicite.
3. **Limiter le port d’écoute** aux réseaux et aux interfaces prévus selon les possibilités de pare-feu.
4. **Mettre à jour l’OS et WireGuard** via les mécanismes supportés de la distribution.
5. **Documenter chaque peer** : propriétaire, rôle, date de création de clé, préfixes autorisés et procédure de révocation.
6. **Surveiller le trafic et l’état**, pas seulement la présence de l’interface. Utilise un test applicatif adapté et protège les journaux.
7. **Tester le retour arrière** avant de modifier routes, pare-feu, DNS ou politiques de tunnel complet.
8. **Vérifier IPv4 et IPv6 séparément**, afin de ne pas laisser un chemin non protégé par inadvertance.

> **Astuce :** fais d’abord fonctionner un seul peer avec une adresse de tunnel /32 dans `AllowedIPs`, puis étends graduellement la politique aux sous-réseaux. Une topologie minimale rend les erreurs de clés, d’endpoint et de routage bien plus faciles à différencier.

### 3.9 Checklist avant mise en service

- [ ] Chaque hôte possède une paire de clés unique.
- [ ] Aucune clé privée n’a été copiée dans le fichier de l’autre pair.
- [ ] Les clés publiques échangées sont celles des bons hôtes.
- [ ] Les adresses de tunnel et les préfixes `AllowedIPs` ne se chevauchent pas involontairement.
- [ ] L’endpoint est correct et le port UDP est autorisé.
- [ ] `wg show` montre un handshake lorsque du trafic est généré.
- [ ] Les compteurs envoyés/reçus augmentent pendant les tests.
- [ ] La route aller et la route retour sont correctes.
- [ ] Le pare-feu n’autorise que les flux nécessaires.
- [ ] Le DNS et IPv6 ont été testés selon la politique attendue.
- [ ] La MTU est validée avec des paquets et des transferts de tailles différentes.
- [ ] La révocation d’un peer et le retour arrière ont été documentés.

---

## Points à retenir

- WireGuard est un VPN IP de couche 3 qui transporte le trafic à l’intérieur de paquets UDP protégés.
- Chaque interface utilise une clé privée secrète et chaque pair distant est identifié par sa clé publique.
- `AllowedIPs` sert au choix du pair à l’émission et à la vérification des adresses source intérieures à la réception.
- `Endpoint` désigne où joindre le pair ; il ne remplace pas les routes ni les règles du pare-feu.
- `PersistentKeepalive` est facultatif et utile dans certains environnements NAT ou pare-feu stateful.
- Un handshake récent prouve que des échanges cryptographiques ont eu lieu, mais il ne garantit pas le routage jusqu’à l’application.
- Pour dépanner, sépare le transport UDP, le handshake, les `AllowedIPs`, le routage, le pare-feu, le DNS et la MTU.
- Le tunnel complet, les LAN distants, le NAT sortant et IPv6 demandent une conception explicite.
- Le protocole ne gère pas à lui seul les comptes utilisateur, la distribution des clés, la segmentation applicative ou l’observabilité complète.

## Exercices corrigés

### Exercice 1 — Lire les clés

**Question :** quelle clé doit rester secrète et quelle clé peut être installée chez le pair distant ?

**Correction :** la clé privée reste sur l’interface qui l’a générée. La clé publique est communiquée aux pairs qui doivent reconnaître cette identité. Ne publie jamais la clé privée.

### Exercice 2 — Comprendre `AllowedIPs`

**Question :** côté client, que signifie `AllowedIPs = 10.80.0.1/32` dans le laboratoire minimal ?

**Correction :** la destination `10.80.0.1` est associée au peer serveur pour l’émission ; à la réception, les sources intérieures venant de ce peer sont limitées aux préfixes autorisés. Les routes système et le pare-feu doivent toujours être cohérents.

### Exercice 3 — Pas de handshake

**Question :** l’interface `wg0` existe, mais `latest handshake` reste absent. Quel ordre de contrôles adopter ?

**Correction :** vérifier le bon fichier chargé et les clés publiques, l’endpoint et le port UDP, le pare-feu/NAT, la route externe vers l’endpoint puis les journaux du service. N’altère pas en même temps les clés, les routes et le pare-feu.

### Exercice 4 — Handshake mais LAN inaccessible

**Question :** les deux pairs ont un handshake récent, mais le client ne peut pas atteindre un serveur du LAN distant.

**Correction :** vérifier que le LAN distant apparaît dans `AllowedIPs` du peer concerné, que la route sélectionne `wg0`, que le transfert IP est activé sur la passerelle, que le pare-feu autorise le transfert et que le LAN dispose d’une route de retour. Vérifier aussi que le pare-feu de l’hôte autorise l’application ciblée.

### Exercice 5 — Faut-il utiliser `PersistentKeepalive = 25` partout ?

**Correction :** non. C’est surtout utile lorsque l’un des pairs se trouve derrière un NAT ou un pare-feu qui expire les états inactifs et que l’on souhaite que le pair reste joignable sans trafic applicatif. Sinon, cette option peut être inutile.

### Exercice 6 — Le DNS ne répond pas

**Question :** une adresse IP privée répond au ping via le tunnel, mais le nom du serveur échoue.

**Correction :** vérifier le résolveur, la route vers ce résolveur, le filtrage DNS, la configuration de domaine de recherche et le split DNS. Éviter de recréer les clés si le handshake et les tests IP prouvent que le tunnel transporte déjà du trafic.

## Glossaire

| Terme | Définition |
|---|---|
| Endpoint | Adresse IP ou nom et port UDP du pair distant |
| Handshake | Échange cryptographique initial ou renouvelé entre les pairs |
| Interface `wg0` | Interface virtuelle WireGuard sur le système |
| `AllowedIPs` | Préfixes associés à un peer pour le routage et la validation d’adresse source |
| Peer | Participant WireGuard identifié par une clé publique |
| Split tunnel | Seuls certains préfixes passent par le VPN |
| Full tunnel | Le trafic IP choisi, souvent toute destination IPv4 et IPv6, passe par le VPN |
| NAT | Traduction d’adresses entre réseaux, susceptible de maintenir un état temporaire |
| MTU | Taille maximale du paquet transféré sans fragmentation au niveau considéré |
| MSS | Taille maximale du segment TCP transporté dans un paquet |
| `wg-quick` | Outil pratique qui configure l’interface, les adresses et les routes associées |

## Références et lectures complémentaires

1. WireGuard — site officiel et présentation : https://www.wireguard.com/
2. WireGuard — documentation de démarrage rapide : https://www.wireguard.com/quickstart/
3. WireGuard — protocole et cryptographie : https://www.wireguard.com/protocol/
4. WireGuard — limites connues : https://www.wireguard.com/known-limitations/
5. `wg-quick(8)` — guide de l’outil : https://man7.org/linux/man-pages/man8/wg-quick.8.html
6. Debian Wiki — WireGuard et exemples de configuration : https://wiki.debian.org/WireGuard
7. Noise Protocol Framework : https://noiseprotocol.org/
8. Donenfeld, J. A. — *WireGuard: Next Generation Kernel Network Tunnel*, NDSS 2017 : https://www.ndss-symposium.org/ndss2017/ndss-2017-programme/wireguard-next-generation-kernel-network-tunnel/

> **Danger :** les adresses, clés factices, règles de pare-feu et extraits de configuration de ce cours constituent un laboratoire. Avant de les utiliser en production, révise la topologie, les règles d’accès, le routage IPv4/IPv6, la protection des secrets, le plan de révocation et la procédure de retour arrière.
