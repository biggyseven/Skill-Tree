# Dépannage MTU et PMTUD — Niveau intermédiaire

> **But du cours :** passer du simple test de taille de paquet à un diagnostic réseau reproductible. Vous apprendrez à relier le calcul des en-têtes, le comportement d’IPv4 et d’IPv6, les messages ICMP, TCP/MSS, les tunnels et les captures de paquets afin d’expliquer pourquoi un flux échoue sur certains chemins seulement.

**Niveau :** Intermédiaire  
**Public :** techniciens support, administrateurs systèmes et réseaux en progression  
**Prérequis :** notions d’adresse IP, sous-réseau, routage, ping et modèle TCP/IP ; le cours débutant MTU/PMTUD est considéré comme acquis.  
**Durée conseillée :** 2 h 30 à 4 h, selon les manipulations pratiques.  
**Environnement recommandé :** deux machines de test, un routeur ou pare-feu administrable, une interface VPN de laboratoire et Wireshark ou tcpdump. Les commandes qui changent la configuration doivent être testées dans un environnement autorisé.


## Rapport de comptage des mots

Le contenu pédagogique dépasse le seuil demandé de 5 000 mots. Le comptage officiel de livraison est effectué sur le texte du cours en excluant le code source des cinq SVG animés intégrés, les blocs de commandes fenced, les balises HTML de présentation et le texte de code en ligne. Les titres, les paragraphes, les tableaux, les listes, les légendes rédigées, les questions, les corrigés et les références textuelles sont inclus. Le rapport final situé à la fin du document donne le nombre mesuré et la méthode de calcul. Les outils de comptage peuvent varier légèrement selon leur traitement des mots composés, des apostrophes et des URL.

## Comment utiliser le cours

Lisez d’abord les sections de calcul et de découverte classique. Ensuite, étudiez les cinq schémas SVG animés dans l’ordre : ils représentent la boucle PMTUD, le budget d’en-têtes, la panne de type *black hole*, les effets d’un tunnel et une méthode de diagnostic. Les animations sont intégrées directement dans ce fichier Markdown. Aucun fichier image externe n’est nécessaire pour disposer du code des schémas. Certains éditeurs Markdown assainissent le HTML ou neutralisent l’animation SVG ; dans ce cas, copiez le bloc `<svg>` complet dans un fichier `.svg` et ouvrez-le dans un navigateur récent.

Les valeurs de MTU, d’en-têtes et de surcharge utilisées dans les exemples sont pédagogiques. Elles ne constituent pas une garantie qu’un opérateur, un tunnel ou un logiciel donné emploie exactement ces valeurs. En production, mesurez les interfaces réelles, vérifiez les options actives et consultez les documents du fournisseur.

## 1. Ce qui change entre débutant et intermédiaire

Au niveau débutant, la question centrale est : « pourquoi un paquet trop grand n’arrive-t-il pas à destination ? » Au niveau intermédiaire, il faut répondre à des questions plus précises : à quel endroit la taille devient-elle invalide, quel champ ou quel mécanisme aurait dû signaler le problème, quelle taille est réellement calculée par la pile réseau, et comment prouver l’hypothèse avec des observations indépendantes ?

Il ne suffit pas d’obtenir un ping qui répond. Un ping est un test ICMP isolé ; une application réelle peut utiliser TCP, UDP, QUIC, IPv4 ou IPv6, suivre un itinéraire différent ou ajouter des en-têtes supplémentaires. Un test réussi vers une adresse IP n’établit donc pas automatiquement que tous les flux applicatifs fonctionneront. De la même façon, un test échoué ne prouve pas à lui seul une panne de MTU : le pare-feu peut filtrer ICMP, l’hôte distant peut refuser l’écho, ou la perte peut venir d’une route, d’une congestion ou d’une limitation de débit.

Le technicien intermédiaire travaille avec une hypothèse testable, une mesure, un point de capture et une procédure de retour arrière. Il évite de modifier plusieurs paramètres en même temps. La méthode suivie dans ce cours est : observer les symptômes, définir le flux concerné, mesurer les tailles, identifier les messages de contrôle, localiser la rupture, appliquer le changement le plus ciblé puis vérifier que la correction tient dans la durée.

## 2. Vocabulaire technique à distinguer

### 2.1 MTU de lien

La *Maximum Transmission Unit* (MTU) d’un lien est la taille maximale du paquet de couche réseau que ce lien peut transporter dans les conditions pertinentes de sa technologie et de sa configuration. Dans les exemples IP Ethernet usuels, une MTU de 1500 octets désigne le datagramme IP, pas une trame Ethernet complète comprenant tous les champs de couche 2. Il faut donc éviter d’additionner l’en-tête Ethernet à 1500 lorsqu’on calcule la taille IP classique autorisée.

La MTU est une propriété du lien ou de l’interface, mais le chiffre affiché dans une configuration ne suffit pas toujours à connaître la capacité réelle de bout en bout. Un tunnel peut ajouter de l’encapsulation ; un accès PPPoE peut réduire le budget disponible ; un équipement intermédiaire peut appliquer une limite différente ; une interface virtuelle peut exposer une MTU qui ne reflète pas seule le chemin extérieur.

### 2.2 PMTU et cache PMTU

La *Path MTU* (PMTU) d’un chemin est la plus petite MTU parmi les liens réellement traversés par les paquets d’un flux donné, compte tenu du chemin retenu. Si les MTU successives sont 1500, 1500, 1400 et 9000, la PMTU de ce chemin est 1400 octets. Si le routage change et emprunte un lien de 1300 octets, l’estimation précédente devient trop grande. La PMTU n’est donc pas une propriété universelle de la destination : elle dépend du chemin, du sens, de la famille IP, parfois du flux et du moment.

Les piles réseau peuvent conserver une estimation en cache afin d’éviter de redécouvrir la limite à chaque paquet. Cette optimisation accélère les connexions, mais elle introduit une subtilité de dépannage : deux machines peuvent posséder des estimations différentes, et une route modifiée peut rendre temporairement obsolète une valeur conservée. Lorsqu’un défaut apparaît seulement après une reconnexion, un basculement WAN ou un changement de VPN, le cache et la route doivent faire partie des hypothèses.

### 2.3 PMTUD classique, PLPMTUD et DPLPMTUD

Le PMTUD classique apprend la limite du chemin en s’appuyant sur les messages d’erreur IP appropriés. En IPv4, un routeur qui ne peut pas transmettre un datagramme parce que la fragmentation est interdite peut renvoyer un message ICMP Destination Unreachable, code « fragmentation nécessaire ». En IPv6, un routeur qui ne peut pas transmettre le paquet en raison de la MTU du prochain lien renvoie un message ICMPv6 Packet Too Big. L’émetteur diminue alors la taille utilisée pour ce chemin.

Le PLPMTUD, défini par le RFC 4821, opère à la couche de paquetisation, c’est-à-dire la couche qui choisit la quantité de données placée dans un paquet. Il vérifie la taille par des sondes et des retours de réussite, sans dépendre exclusivement de la réception d’un message ICMP PTB. Le DPLPMTUD, précisé pour les transports datagrammes par le RFC 8899, adapte cette approche à des protocoles tels que UDP et QUIC. Ces approches ne rendent pas ICMP inutile : elles ajoutent une stratégie de découverte plus robuste lorsqu’un retour ICMP est absent ou peu fiable.

### 2.4 MSS, MPS et charge utile

La *Maximum Segment Size* (MSS) TCP est une limite de données TCP qu’un hôte annonce à son pair pendant l’établissement de la connexion. Elle ne correspond ni à la MTU du lien ni à la taille totale du paquet IP. Pour un paquet IPv4 avec en-tête IP standard de 20 octets et en-tête TCP de 20 octets, une MTU de 1500 octets conduit souvent à une MSS de 1460 octets. Pour IPv6 avec l’en-tête de base de 40 octets et un en-tête TCP de 20 octets, le calcul classique donne 1440 octets. Des options IP, des options TCP ou des en-têtes d’extension peuvent réduire la place réellement disponible dans un paquet donné.

Le *Maximum Packet Size* (MPS), terme employé dans les textes sur la découverte de MTU à la couche de paquetisation, est une limite de données de cette couche. Il faut soustraire les en-têtes propres au protocole, à la sécurité ou à l’encapsulation. Par exemple, un transport datagramme sur UDP peut ajouter un en-tête UDP, un en-tête de protocole applicatif et une authentification cryptographique. Il ne faut pas appliquer automatiquement le calcul TCP/MSS à un flux UDP ou QUIC.

## 3. Calculer la taille d’un paquet sans confondre les couches

Un calcul MTU fiable commence par la couche réseau. Pour IPv4 sans options, l’en-tête fait normalement 20 octets. Pour ICMPv4 Echo, le message ICMP ajoute 8 octets ; une commande de ping qui accepte une taille de charge utile de 1472 octets crée donc normalement un datagramme IPv4 de 1500 octets : 20 + 8 + 1472. C’est la raison du chiffre souvent utilisé pour tester une MTU Ethernet de 1500 sous IPv4. Ce chiffre n’est pas universel : il change si les options ou les encapsulations sont différentes.

Pour IPv6, l’en-tête de base fait 40 octets et le message ICMPv6 Echo ajoute généralement 8 octets. Une charge utile de 1452 octets donne ainsi 1500 octets au niveau IP, en l’absence d’en-têtes d’extension supplémentaires. Le fait qu’une commande puisse envoyer cette charge utile ne garantit pas que le chemin l’accepte ; le test doit réellement traverser le chemin dont la PMTU est étudiée.

Le calcul le plus important en production est souvent celui de la place laissée aux données applicatives. Si un chemin a une PMTU de 1400 octets en IPv4 standard, la charge TCP maximale théorique avec un en-tête IP de 20 octets et un en-tête TCP minimal de 20 octets est 1360 octets. Avec des options TCP, la quantité de données d’un segment particulier peut être plus basse. Avec un tunnel, il faut encore prendre en compte les en-têtes ajoutés par l’encapsulation extérieure ; selon le type de tunnel et la configuration, la MTU extérieure disponible peut être consommée avant même que le paquet interne ne soit transmis.

### Exemple de budget d’en-têtes

Imaginons un tunnel pédagogique dont le lien extérieur accepte des paquets IP de 1500 octets. L’encapsulation ajoute 50 octets au paquet interne dans le scénario retenu. Pour que le paquet extérieur n’excède pas 1500, le paquet IP intérieur doit rester à 1450 octets au maximum. Si ce paquet interne est IPv4/TCP avec en-têtes standards, la capacité de données TCP indicative est 1450 − 20 − 20 = 1410 octets. Le calcul ne doit être utilisé que si les 50 octets représentent bien toutes les surcharges actives : les variantes d’IPsec, les options, les balises, le chiffrement et les combinaisons de protocoles peuvent changer le résultat.

### Tableau de repères courants

| Situation pédagogique | En-tête IP | En-tête de transport/contrôle | Charge utile pour atteindre une taille IP de 1500 |
|---|---:|---:|---:|
| IPv4 + ICMP Echo standard | 20 | ICMP : 8 | 1472 |
| IPv6 + ICMPv6 Echo, sans extension | 40 | ICMPv6 : 8 | 1452 |
| IPv4 + TCP minimal | 20 | TCP : 20 | 1460 |
| IPv6 + TCP minimal | 40 | TCP : 20 | 1440 |

Ces valeurs servent de repères, pas de substitut à une capture. Les tailles de données rapportées par les outils ne sont pas toutes définies au même niveau. Une commande de ping peut indiquer la taille de la charge utile ICMP, alors qu’une capture peut montrer la longueur totale du paquet IP. Avant de comparer deux chiffres, notez ce que mesure chaque outil.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="470" viewBox="0 0 1120 470" role="img" aria-labelledby="budgetTitle budgetDesc" style="max-width:100%;height:auto">
<title id="budgetTitle">Animation du budget de taille MTU</title><desc id="budgetDesc">Une barre de 1500 octets est divisée entre en-tête IP, en-tête TCP et données. L'animation met en évidence que chaque en-tête consomme une partie du budget disponible.</desc>
<defs><linearGradient id="budgetBg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#172033"/></linearGradient><style>.bt{font-family:Inter,Arial,sans-serif;fill:#e5e7eb}.btitle{font-size:25px;font-weight:800}.blabel{font-size:16px;font-weight:700}.bsmall{font-size:13px;fill:#bac7d8}.barIP{fill:#60a5fa}.barTCP{fill:#fbbf24}.barData{fill:#34d399}.glow{animation:glow 2s ease-in-out infinite}@keyframes glow{0%,100%{opacity:.7}50%{opacity:1;filter:drop-shadow(0 0 8px #34d399)}}@media(prefers-reduced-motion:reduce){.glow{animation:none}}</style></defs>
<rect width="1120" height="470" rx="22" fill="url(#budgetBg)"/><text x="40" y="48" class="bt btitle">Budget IP : chaque en-tête prend sa part</text><text x="42" y="75" class="bt bsmall">Exemple TCP avec MTU de 1500 octets et en-têtes minimaux</text>
<g transform="translate(50 125)"><text x="0" y="0" class="bt blabel">IPv4</text><rect x="0" y="24" width="1020" height="74" rx="10" fill="#263449"/><rect x="0" y="24" width="13.6" height="74" class="barIP"/><rect x="13.6" y="24" width="13.6" height="74" class="barTCP"/><rect x="27.2" y="24" width="992.8" height="74" rx="3" class="barData glow"/><text x="10" y="120" class="bt bsmall">IP : 20 o</text><text x="150" y="120" class="bt bsmall">TCP : 20 o</text><text x="510" y="67" class="bt blabel" text-anchor="middle">Données TCP : jusqu’à 1460 o</text><text x="1018" y="120" class="bt bsmall" text-anchor="end">Total : 1500 o</text></g>
<g transform="translate(50 285)"><text x="0" y="0" class="bt blabel">IPv6</text><rect x="0" y="24" width="1020" height="74" rx="10" fill="#263449"/><rect x="0" y="24" width="27.2" height="74" class="barIP"/><rect x="27.2" y="24" width="13.6" height="74" class="barTCP"/><rect x="40.8" y="24" width="979.2" height="74" rx="3" class="barData glow"/><text x="10" y="120" class="bt bsmall">IP : 40 o</text><text x="150" y="120" class="bt bsmall">TCP : 20 o</text><text x="520" y="67" class="bt blabel" text-anchor="middle">Données TCP : jusqu’à 1440 o</text><text x="1018" y="120" class="bt bsmall" text-anchor="end">Total : 1500 o</text></g>
<text x="50" y="448" class="bt bsmall">Attention : options TCP, extensions IPv6, encapsulation et sécurité consomment un budget supplémentaire.</text></svg>
</div>

## 4. Le déroulement du PMTUD classique

Le scénario classique débute quand l’hôte source prépare un paquet dont la taille est adaptée à l’interface locale, mais qui dépasse une MTU plus faible rencontrée plus loin. Le premier routeur peut accepter le paquet sur son interface d’entrée et constater ensuite que l’interface de sortie ne peut pas le transporter en un seul morceau. Cette distinction entre interface d’entrée et interface de sortie est importante : la MTU locale de l’émetteur peut être parfaitement correcte, tandis que le problème apparaît à un point situé plusieurs routeurs plus loin.

En IPv4, si la fragmentation est interdite, généralement au moyen du bit DF (*Don't Fragment*), le routeur ne fragmente pas le datagramme pour le faire entrer dans la liaison plus petite. Il abandonne le paquet trop grand et peut envoyer à la source un ICMP Destination Unreachable, type 3, code 4, communément nommé *Fragmentation Needed*. Lorsque le champ MTU suivant est renseigné, l’émetteur dispose d’une indication de la taille que l’interface de sortie peut accepter. L’hôte diminue alors sa taille estimée pour le chemin et retransmet des paquets plus petits.

En IPv6, les routeurs intermédiaires ne fragmentent pas les paquets. Si le paquet dépasse la MTU du lien suivant, le routeur le détruit et envoie un ICMPv6 Packet Too Big, type 2. La source adapte alors ses paquets. Le mécanisme dépend de la bonne circulation de ce message de contrôle ; le bloquer sans discernement est une cause classique d’échec.

Le premier message reçu ne prouve pas toujours que la valeur trouvée sera la valeur finale. Si un autre lien, plus loin sur le chemin, possède une MTU encore plus petite, la nouvelle taille peut échouer à nouveau et déclencher un second retour ICMP. La découverte s’achève lorsque les paquets envoyés respectent tous les liens du chemin courant ou lorsque la pile a choisi une stratégie de repli compatible avec sa mise en œuvre.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="560" viewBox="0 0 1120 560" role="img" aria-labelledby="pmtuLoopTitle pmtuLoopDesc" style="max-width:100%;height:auto">
<title id="pmtuLoopTitle">PMTUD classique : paquet trop grand, message ICMP/PTB et adaptation</title>
<desc id="pmtuLoopDesc">Animation du mécanisme classique de découverte de la MTU du chemin. La source émet un paquet IP de 1500 octets. Un routeur dont le lien de sortie a une MTU de 1400 octets abandonne le paquet non fragmentable et renvoie un message ICMP approprié. La source réduit ensuite la taille et le paquet adapté peut atteindre la destination.</desc>
<defs>
  <linearGradient id="loopBg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0a1020"/><stop offset="1" stop-color="#182235"/></linearGradient>
  <marker id="loopArrowR" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#fb7185"/></marker>
  <marker id="loopArrowG" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#34d399"/></marker>
  <marker id="loopArrowY" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#fbbf24"/></marker>
  <style>
    .lt{font-family:Inter,Arial,sans-serif;fill:#e5e7eb}
    .lhead{font-size:24px;font-weight:800}
    .lbody{font-size:15px;font-weight:700}
    .lsmall{font-size:12px;fill:#bac7d8}
    .lroute{fill:none;stroke-width:4;stroke-linecap:round}
    .lmove{animation:packetForward 6.8s linear infinite;transform-box:fill-box;transform-origin:0 0}
    .lreturn{animation:packetReturn 6.8s linear infinite;transform-box:fill-box;transform-origin:0 0}
    .lnew{animation:packetAdapted 6.8s linear infinite;transform-box:fill-box;transform-origin:0 0}
    @keyframes packetForward{
      0%,2%{transform:translate(0,0);opacity:0}
      7%{opacity:1}
      28%{transform:translate(155px,0);opacity:1}
      33%,100%{transform:translate(155px,0);opacity:0}
    }
    @keyframes packetReturn{
      0%,35%{transform:translate(0,0);opacity:0}
      41%{opacity:1}
      62%{transform:translate(-275px,0);opacity:1}
      68%,100%{transform:translate(-275px,0);opacity:0}
    }
    @keyframes packetAdapted{
      0%,69%{transform:translate(0,0);opacity:0}
      74%{opacity:1}
      97%{transform:translate(690px,0);opacity:1}
      100%{transform:translate(690px,0);opacity:0}
    }
    @media(prefers-reduced-motion:reduce){
      .lmove,.lreturn,.lnew{animation:none;opacity:1}
    }
  </style>
</defs>
<rect width="1120" height="560" rx="22" fill="url(#loopBg)"/>
<text x="42" y="48" class="lt lhead">PMTUD classique : erreur, retour, adaptation</text>
<text x="43" y="76" class="lt lsmall">Exemple pédagogique : PMTU initiale estimée à 1500 octets ; lien de sortie limité à 1400.</text>
<text x="43" y="98" class="lt lsmall">IPv4 : ICMP Destination Unreachable, type 3/code 4 · IPv6 : ICMPv6 Packet Too Big, type 2.</text>
<text x="43" y="120" class="lt lsmall">En IPv4, cet exemple suppose DF=1 ; en IPv6, les routeurs ne fragmentent pas les paquets en transit.</text>

<!-- Les nœuds et leur ligne de chemin restent fixes : seuls les paquets animés se déplacent. -->
<path d="M160 235H962" stroke="#53647d" stroke-width="4" stroke-dasharray="8 8"/>
<g>
  <rect x="42" y="182" width="155" height="108" rx="16" fill="#17263a" stroke="#60a5fa" stroke-width="2"/>
  <text x="119" y="218" class="lt lbody" text-anchor="middle">Source</text>
  <text x="119" y="244" class="lt lsmall" text-anchor="middle">MTU locale 1500</text>
  <text x="119" y="264" class="lt lsmall" text-anchor="middle">PMTU estimée 1500</text>
</g>
<g>
  <rect x="445" y="182" width="230" height="108" rx="16" fill="#332032" stroke="#fb7185" stroke-width="2"/>
  <text x="560" y="214" class="lt lbody" text-anchor="middle">Routeur intermédiaire</text>
  <text x="560" y="240" class="lt lsmall" text-anchor="middle">Lien de sortie MTU 1400</text>
  <text x="560" y="262" class="lt lsmall" text-anchor="middle">Rejette le paquet trop grand</text>
</g>
<g>
  <rect x="923" y="182" width="155" height="108" rx="16" fill="#17263a" stroke="#34d399" stroke-width="2"/>
  <text x="1000" y="218" class="lt lbody" text-anchor="middle">Destination</text>
  <text x="1000" y="244" class="lt lsmall" text-anchor="middle">Réception finale</text>
  <text x="1000" y="264" class="lt lsmall" text-anchor="middle">Paquet adapté</text>
</g>

<!-- Premier temps : paquet IP de 1500 octets vers le routeur. -->
<path d="M198 225H436" class="lroute" stroke="#fb7185" stroke-dasharray="7 6" marker-end="url(#loopArrowR)"/>
<g transform="translate(198 208)">
  <g class="lmove">
    <rect x="0" y="0" width="140" height="34" rx="8" fill="#be123c" stroke="#fecdd3" stroke-width="1"/>
    <text x="70" y="22" class="lt lsmall" text-anchor="middle" fill="#fff">IP : 1500 octets</text>
  </g>
</g>
<g>
  <circle cx="422" cy="225" r="13" fill="#7f1d1d" stroke="#fda4af" stroke-width="2"/>
  <path d="M416 219L428 231M428 219L416 231" stroke="#fff" stroke-width="2.5"/>
  <text x="422" y="252" class="lt lsmall" text-anchor="middle">rejet</text>
</g>

<!-- Deuxième temps : le message d'erreur revient du routeur à la source. -->
<path d="M558 300V350H185V300" class="lroute" stroke="#fbbf24" stroke-dasharray="7 6" marker-end="url(#loopArrowY)"/>
<g transform="translate(472 329)">
  <g class="lreturn">
    <rect x="0" y="0" width="220" height="42" rx="8" fill="#92400e" stroke="#fcd34d" stroke-width="1"/>
    <text x="110" y="16" class="lt" font-size="11.5" text-anchor="middle">ICMP / Packet Too Big</text>
    <text x="110" y="31" class="lt" font-size="10.5" text-anchor="middle">MTU signalée : 1400 octets</text>
  </g>
</g>

<!-- Troisième temps : un paquet adapté parcourt le chemin jusqu'à la destination. -->
<path d="M198 410H1012" class="lroute" stroke="#34d399" stroke-dasharray="9 5" marker-end="url(#loopArrowG)"/>
<g transform="translate(198 393)">
  <g class="lnew">
    <rect x="0" y="0" width="170" height="34" rx="8" fill="#047857" stroke="#6ee7b7" stroke-width="1"/>
    <text x="85" y="22" class="lt lsmall" text-anchor="middle" fill="#fff">IP : ≤ 1400 octets</text>
  </g>
</g>

<rect x="42" y="450" width="1036" height="69" rx="13" fill="#102d28" stroke="#166534"/>
<text x="61" y="477" class="lt lbody">À retenir</text>
<text x="61" y="500" class="lt lsmall">Le retour ICMP/PTB indique une limite à respecter ; l’émetteur adapte ensuite ses paquets. Un lien encore plus petit peut</text>
<text x="61" y="514" class="lt lsmall">déclencher une nouvelle notification. Les routeurs IPv6 ne fragmentent pas les paquets en transit.</text>
</svg>
</div>

## 5. ICMP utile au diagnostic : types, codes et interprétation

ICMP est un protocole de contrôle lié à IP. Il fournit des indications sur la livraison et l’état du réseau, mais ne transforme pas IP en service fiable : un datagramme et son message ICMP associé peuvent tous deux être perdus. Le filtre de sécurité ne doit donc pas considérer tous les messages ICMP comme dangereux par défaut, pas plus qu’il ne doit leur faire confiance sans validation.

Pour le dépannage PMTUD IPv4, le message central est Destination Unreachable, type 3, code 4, « fragmentation nécessaire et DF activé ». Il faut distinguer ce code d’autres erreurs ICMP qui ont une cause différente, comme réseau inaccessible, hôte inaccessible ou port inaccessible. En IPv6, le message pertinent est ICMPv6 Packet Too Big, type 2. Le message indique à la source que le paquet en cause ne peut pas être transmis sans réduire sa taille. Il faut éviter de résumer cela à « ICMP est bloqué » sans avoir observé les paquets réellement présents ou absents.

Une capture peut montrer un message ICMP qui arrive à une interface mais qui ne déclenche pas d’adaptation. Plusieurs causes sont possibles : le message est jugé non pertinent ou invalide, le flux cité ne correspond pas à une connexion active, la pile réseau ne traite pas le message, une règle locale le bloque avant traitement, ou un problème de capture fait croire qu’il n’a pas été pris en compte. Il faut donc vérifier la source, le type/code, la destination du message, le paquet original cité, le sens de circulation et le moment où le message apparaît.

Les messages ICMP peuvent être limités en débit par les routeurs. Si un test envoie de nombreuses sondes rapidement, le comportement observé peut inclure du rate limiting qui n’existe pas de la même façon pour un transfert applicatif. Préférez une cadence de test modérée, répétez l’essai et observez si le résultat dépend du débit ou uniquement de la taille.

## 6. IPv4 et IPv6 : différences importantes pour l’investigation

### 6.1 Fragmentation IPv4

IPv4 possède un mécanisme de fragmentation où un datagramme peut être divisé en fragments. Si DF n’est pas activé, certains routeurs peuvent fragmenter un paquet en fonction de la MTU de sortie ; le destinataire réassemble les fragments. Bien que cela puisse permettre à certains paquets de passer, la fragmentation IPv4 augmente les coûts de traitement et rend la perte d’un seul fragment suffisante pour perdre le datagramme complet. Les équipements de sécurité peuvent aussi traiter les fragments de façon différente, et certains systèmes intermédiaires gèrent mal les fragments atypiques.

Le PMTUD IPv4 classique utilise habituellement des paquets non fragmentables dans le but de découvrir une taille efficace, puis adapte la taille envoyée. Si le bit DF est absent et qu’une fragmentation silencieuse se produit, une sonde peut réussir sans fournir une mesure nette de la PMTU. Il faut savoir ce que l’outil de test demande à la pile et vérifier dans la capture que les paquets sont effectivement non fragmentables quand c’est le but du test.

### 6.2 Fragmentation IPv6

Les routeurs IPv6 ne fragmentent pas les paquets en transit. Si le paquet dépasse la MTU du lien suivant, l’émetteur est informé au moyen d’ICMPv6 Packet Too Big et doit réduire la taille ou effectuer, lorsque c’est approprié, une fragmentation au niveau de la source au moyen de l’en-tête de fragmentation IPv6. Cette distinction donne davantage d’importance à la bonne transmission du message Packet Too Big.

IPv6 fixe à 1280 octets la MTU minimale de lien que les liens doivent prendre en charge selon les spécifications de base. Cela ne signifie pas qu’un administrateur doive régler toutes les interfaces à 1280 octets. Le réseau peut utiliser une MTU plus grande, et la PMTU réelle du chemin peut être plus basse ou plus élevée selon les segments, dans les limites applicables. Il faut aussi tenir compte des en-têtes d’extension éventuels, qui réduisent la place laissée aux données de couche supérieure pour une même taille totale.

### 6.3 Comparer sans supposer que les tests sont identiques

Un test IPv4 réussi et un test IPv6 échoué peuvent provenir d’une différence dans les routes, les pare-feu, les MTU de tunnel ou le traitement ICMP, même si le nom DNS est identique. Les deux familles n’utilisent pas les mêmes adresses et ne parcourent pas forcément les mêmes équipements. Effectuez des tests explicitement en IPv4 puis en IPv6, notez la destination résolue et vérifiez le chemin ou le point de sortie correspondant.

De même, un message d’erreur IPv4 ne doit pas être interprété avec le filtre ICMPv6, et inversement. Le technicien doit maîtriser la famille IP, les types/codes pertinents et la syntaxe propre à l’outil utilisé. Quand un programme tente automatiquement IPv6 puis revient à IPv4, l’application peut paraître intermittente ; comparez les journaux et les captures en forçant chaque famille pour distinguer une préférence de résolution d’un problème de taille.

## 7. TCP, MSS et symptômes d’application

TCP découpe généralement un flux d’octets en segments adaptés à la MSS et aux informations de PMTU disponibles. La MSS est annoncée par chaque extrémité dans les options SYN, et elle décrit la quantité de données TCP que cette extrémité est prête à recevoir dans un segment. Les deux directions peuvent avoir des MSS différentes : l’annonce du client concerne les données envoyées vers le client, tandis que l’annonce du serveur concerne les données envoyées vers le serveur.

Une erreur fréquente consiste à croire qu’une MSS annoncée de 1460 garantit que tous les paquets sur la route feront 1500 octets et seront acceptés. Ce n’est pas le cas. Le chemin peut avoir une PMTU plus petite, des options TCP peuvent allonger l’en-tête, le tunnel peut ajouter une encapsulation extérieure, et le système peut réduire sa taille de segmentation. La MSS annoncée est l’un des éléments du calcul, non une preuve de la PMTU de bout en bout.

Les symptômes d’un PMTUD cassé sont souvent décrits comme « le ping marche, mais le site bloque », « la session démarre, puis le téléchargement reste à zéro », ou « les petits échanges passent, mais une réponse volumineuse échoue ». Ce tableau s’explique lorsqu’un échange initial avec de petits paquets traverse le réseau, puis que la transmission de données déclenche des segments trop grands pour un lien plus restrictif. Si la notification ICMP n’arrive pas, l’émetteur peut retransmettre indéfiniment les mêmes données ou attendre des délais d’expiration.

Ces symptômes ne sont pas spécifiques au MTU. Un problème de fenêtre TCP, de perte, de congestion, d’inspection TLS, de proxy, de DNS, de route asymétrique ou de serveur peut donner une impression similaire. Une capture est donc essentielle : recherchez les retransmissions TCP répétées, les numéros de séquence identiques, les ACK qui cessent de progresser, les paquets ICMP d’erreur éventuels et les différences entre la sortie de l’émetteur et l’entrée du destinataire.

### 7.1 MSS clamping : ce que cela corrige et ce que cela ne prouve pas

Le *MSS clamping* modifie l’option MSS dans les paquets TCP SYN qui traversent un routeur ou un pare-feu. L’équipement annonce alors aux extrémités une MSS plus faible, dans le but de limiter la taille des segments TCP. Cette technique peut être utile lorsqu’un tunnel réduit la PMTU et que des équipements ne transmettent pas les messages PTB nécessaires. Elle peut aussi fournir une mesure de mitigation rapide dans un réseau maîtrisé.

Le clamping ne corrige pas universellement tous les problèmes de MTU. Il n’agit que sur le trafic TCP concerné, pas directement sur les datagrammes UDP, ni forcément sur QUIC, qui fonctionne au-dessus d’UDP. Une valeur arbitrairement faible diminue le rendement, augmente le nombre de paquets et peut ajouter de la charge CPU, sans remédier à la vraie cause du défaut. Il faut choisir la valeur à partir de l’overhead mesuré, limiter la règle aux flux nécessaires et vérifier les deux sens.

Le MSS clamping ne remplace pas une configuration de tunnel cohérente ni un filtrage ICMP correct. Lorsque le réseau prend en charge PMTUD normalement, il est préférable d’éviter une réduction permanente inutile. Si une règle est activée à titre temporaire, documentez son périmètre, sa justification, la mesure de référence et les critères de retrait.

## 8. La panne « PMTUD black hole »

On parle de *PMTUD black hole* lorsque des paquets trop grands sont abandonnés silencieusement, sans que la source reçoive ou traite l’information nécessaire pour ajuster leur taille. La cause typique est un filtrage excessif des messages ICMP liés à la fragmentation nécessaire ou aux paquets trop grands. Le trafic de petite taille peut continuer à fonctionner ; le trafic de grande taille est perdu. Du point de vue utilisateur, la connexion semble établie mais reste bloquée au moment d’échanger davantage de données.

Le diagnostic demande de vérifier deux choses séparément : le paquet trop grand est-il abandonné et le message de contrôle est-il généré ? Si le message est visible sur la sortie du routeur qui détecte la MTU insuffisante mais absent à la source, recherchez la perte sur le retour : ACL, pare-feu, inspection, filtrage du fournisseur ou route retour. Si le routeur ne génère pas le message, vérifiez sa configuration, son implémentation et la nature du trafic. Si le message parvient à la source mais que la taille ne change pas, examinez la pile réseau et la corrélation du message avec le trafic original.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="530" viewBox="0 0 1120 530" role="img" aria-labelledby="holeTitle holeDesc" style="max-width:100%;height:auto">
<title id="holeTitle">PMTUD black hole animé</title><desc id="holeDesc">Les paquets volumineux sont rejetés au niveau d'un lien plus petit. Le message ICMP destiné à prévenir l'émetteur est bloqué par un pare-feu, ce qui provoque des retransmissions répétées.</desc>
<defs><linearGradient id="holeBg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#101122"/><stop offset="1" stop-color="#251a2a"/></linearGradient><marker id="holeArrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#fb7185"/></marker><style>.ht{font-family:Inter,Arial,sans-serif;fill:#f3f4f6}.hh{font-size:24px;font-weight:800}.hb{font-size:15px;font-weight:700}.hs{font-size:12px;fill:#cbd5e1}.drop{animation:drop 2.2s ease-in-out infinite}.retry{animation:retry 2.2s ease-in-out infinite}@keyframes drop{0%,100%{opacity:.15;transform:translateY(-7px)}50%{opacity:1;transform:translateY(7px)}}@keyframes retry{0%,100%{opacity:.25}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.drop,.retry{animation:none}}</style></defs>
<rect width="1120" height="530" rx="22" fill="url(#holeBg)"/><text x="40" y="47" class="ht hh">PMTUD black hole : la notification n’arrive pas</text><text x="42" y="74" class="ht hs">Le paquet trop grand est perdu ; l’émetteur ne reçoit aucun signal exploitable.</text>
<path d="M170 190H945" stroke="#6b7280" stroke-width="4" stroke-dasharray="8 8"/>
<g><rect x="40" y="145" width="160" height="92" rx="15" fill="#18253b" stroke="#60a5fa" stroke-width="2"/><text x="120" y="180" text-anchor="middle" class="ht hb">Émetteur</text><text x="120" y="205" text-anchor="middle" class="ht hs">Attend la suite</text></g>
<g><rect x="415" y="145" width="220" height="92" rx="15" fill="#3a2028" stroke="#fb7185" stroke-width="2"/><text x="525" y="180" text-anchor="middle" class="ht hb">Lien MTU réduite</text><text x="525" y="205" text-anchor="middle" class="ht hs">Détruit les gros paquets</text></g>
<g><rect x="800" y="145" width="260" height="92" rx="15" fill="#342d17" stroke="#fbbf24" stroke-width="2"/><text x="930" y="180" text-anchor="middle" class="ht hb">Pare-feu / ACL</text><text x="930" y="205" text-anchor="middle" class="ht hs">Filtre le message de contrôle</text></g>
<path d="M202 172H407" stroke="#fb7185" stroke-width="4" stroke-dasharray="7 6" marker-end="url(#holeArrow)"/><g class="drop"><circle cx="319" cy="172" r="18" fill="#be123c"/><path d="M308 161L330 183M330 161L308 183" stroke="#fff" stroke-width="4"/></g>
<path d="M635 214H790" stroke="#fbbf24" stroke-width="4" stroke-dasharray="5 6"/><text x="710" y="199" text-anchor="middle" class="ht hs">ICMP PTB</text><path d="M778 205l22 18m0 -18l-22 18" stroke="#fb7185" stroke-width="4"/><text x="711" y="248" text-anchor="middle" class="ht hs">message bloqué</text>
<g transform="translate(45 300)"><rect width="1015" height="145" rx="16" fill="#171b2c" stroke="#45445b"/><text x="24" y="34" class="ht hb">Ce que voit la source</text><g class="retry"><rect x="25" y="52" width="170" height="50" rx="9" fill="#7f1d1d"/><text x="110" y="82" text-anchor="middle" class="ht hs">Retransmission 1</text><rect x="220" y="52" width="170" height="50" rx="9" fill="#7f1d1d"/><text x="305" y="82" text-anchor="middle" class="ht hs">Retransmission 2</text><rect x="415" y="52" width="170" height="50" rx="9" fill="#7f1d1d"/><text x="500" y="82" text-anchor="middle" class="ht hs">Retransmission 3</text></g><text x="610" y="71" class="ht hb">Pas d’ACK utile</text><text x="610" y="94" class="ht hs">Le flux semble figé, puis expire.</text></g>
<text x="45" y="490" class="ht hs">À vérifier : route du retour, ACL, pare-feu local, messages ICMPv4 type 3/code 4 et ICMPv6 type 2.</text></svg>
</div>

Un test avec de petits paquets peut réussir précisément parce qu’il ne déclenche pas le mécanisme de découverte. Le dépannage ne doit donc pas s’arrêter à une réponse à `ping` de taille standard. À l’inverse, ne concluez pas à un black hole après un unique paquet perdu : répétez le test, vérifiez la destination et observez la capture. Un filtre de sécurité peut légitimement limiter certains types ICMP ; la solution n’est pas de tout autoriser globalement, mais de permettre les messages nécessaires avec des contrôles appropriés.

## 9. Les tunnels, VPN et réseaux superposés

Les tunnels encapsulent un paquet interne dans un paquet extérieur. Le paquet IP interne peut être parfaitement conforme à la MTU affichée par son interface virtuelle et devenir trop grand une fois ajouté l’en-tête extérieur. C’est l’une des principales raisons pour lesquelles une connexion fonctionne sur le LAN mais échoue après l’activation d’un VPN. Le chiffre exact à soustraire dépend de la technologie, du mode, de la famille IP extérieure, des options, du chiffrement et de l’implémentation.

Un tunnel peut utiliser GRE, IPsec, WireGuard, VXLAN, Geneve, PPPoE ou une combinaison de plusieurs encapsulations. Il serait incorrect d’attribuer un unique overhead universel à tous les VPN. Les en-têtes de chiffrement et les champs de sécurité peuvent avoir des tailles différentes ; certaines options sont négociées ; un transport UDP peut avoir une surcharge additionnelle ; et les paquets peuvent être encapsulés dans un deuxième tunnel. Calculez l’enveloppe réellement utilisée et vérifiez avec une capture sur l’interface interne et sur l’interface extérieure.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="550" viewBox="0 0 1120 550" role="img" aria-labelledby="vpnTitle vpnDesc" style="max-width:100%;height:auto">
<title id="vpnTitle">Animation du budget MTU dans un tunnel VPN</title><desc id="vpnDesc">Le paquet interne est enveloppé d'en-têtes extérieurs. L'ensemble dépasse la MTU extérieure si la MTU interne n'est pas ajustée.</desc>
<defs><linearGradient id="vpnBg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#0b1720"/><stop offset="1" stop-color="#18253b"/></linearGradient><style>.vt{font-family:Inter,Arial,sans-serif;fill:#e5e7eb}.vh{font-size:24px;font-weight:800}.vb{font-size:15px;font-weight:700}.vs{font-size:12px;fill:#cbd5e1}.vpacket{animation:vshift 4s ease-in-out infinite}@keyframes vshift{0%,100%{transform:translateX(0)}50%{transform:translateX(16px)}}@media(prefers-reduced-motion:reduce){.vpacket{animation:none}}</style></defs>
<rect width="1120" height="550" rx="22" fill="url(#vpnBg)"/><text x="40" y="47" class="vt vh">Tunnel VPN : la surcharge réduit la place disponible</text><text x="42" y="74" class="vt vs">Exemple illustratif : paquet intérieur + enveloppe extérieure ≤ MTU physique</text>
<g transform="translate(45 125)"><text x="0" y="0" class="vt vb">1. Avant encapsulation</text><rect x="0" y="22" width="460" height="76" rx="12" fill="#203b58" stroke="#60a5fa" stroke-width="2"/><rect x="13" y="35" width="80" height="50" rx="6" fill="#2563eb"/><text x="53" y="64" text-anchor="middle" class="vt vs">IP int.</text><rect x="101" y="35" width="80" height="50" rx="6" fill="#0f766e"/><text x="141" y="64" text-anchor="middle" class="vt vs">TCP/UDP</text><rect x="189" y="35" width="257" height="50" rx="6" fill="#15803d"/><text x="317" y="64" text-anchor="middle" class="vt vb">Données</text><text x="0" y="122" class="vt vs">Le paquet intérieur est dimensionné pour son interface.</text></g>
<g transform="translate(45 300)"><text x="0" y="0" class="vt vb">2. Après encapsulation</text><rect x="0" y="22" width="1005" height="94" rx="13" fill="#3b2434" stroke="#fb7185" stroke-width="2"/><rect x="12" y="34" width="140" height="70" rx="7" fill="#9f1239"/><text x="82" y="63" text-anchor="middle" class="vt vs">IP extérieur</text><text x="82" y="82" text-anchor="middle" class="vt vs">+ UDP/GRE</text><rect x="160" y="34" width="160" height="70" rx="7" fill="#92400e"/><text x="240" y="63" text-anchor="middle" class="vt vs">Sécurité</text><text x="240" y="82" text-anchor="middle" class="vt vs">si applicable</text><g class="vpacket"><rect x="328" y="34" width="665" height="70" rx="7" fill="#1d4ed8"/><text x="660" y="75" text-anchor="middle" class="vt vb">Paquet IP intérieur complet</text></g><path d="M1005 21V120" stroke="#fb7185" stroke-width="3" stroke-dasharray="5 5"/><text x="0" y="146" class="vt vs">Si la somme dépasse la MTU extérieure, le paquet peut être perdu ou déclencher PTB.</text></g>
<rect x="45" y="475" width="1005" height="44" rx="10" fill="#113b30" stroke="#166534"/><text x="62" y="503" class="vt vb">Action : mesurer l’overhead réel, adapter la MTU/MSS au bon endroit et vérifier le trafic intérieur comme extérieur.</text></svg>
</div>

### 9.1 Procédure pour isoler un VPN

Commencez par réaliser un test hors tunnel, si la politique de sécurité et l’architecture le permettent. Puis activez le tunnel et répétez exactement le même test vers la même destination, avec la même famille IP et la même charge utile. Si le problème n’existe qu’avec le VPN, le tunnel ou le chemin qui lui est associé devient une hypothèse prioritaire ; cela ne constitue cependant pas une preuve définitive, car l’activation du VPN peut aussi modifier la route, le DNS ou les règles de pare-feu.

Mesurez la taille maximale dans le tunnel avec un test qui ne fragmente pas silencieusement le paquet lorsque cette option est disponible. Comparez la taille acceptée en dessous et au-dessus de la limite. Capturez ensuite le paquet avant encapsulation et le paquet extérieur. Notez le nombre d’octets de chaque en-tête réellement visible, puis comparez la somme avec la MTU du lien physique ou de transport.

Vérifiez enfin le chemin retour. Un VPN peut avoir des routes asymétriques : la requête passe dans le tunnel, mais la réponse revient par une autre passerelle ou un chemin dont la MTU est différente. Il est alors possible que la direction client-vers-serveur fonctionne et que serveur-vers-client échoue, ou inversement. Les deux sens doivent être testés indépendamment.

### 9.2 Ajustement mesuré plutôt qu’une valeur copiée

Ne copiez pas une valeur de MTU lue dans une discussion en ligne sans connaître le tunnel concerné. La valeur juste pour un réseau peut être trop haute pour une chaîne d’encapsulation différente, ou inutilement basse sur un autre réseau. Le meilleur réglage est celui qui respecte la capacité réelle de la route et qui permet de conserver une bonne efficacité sans dépendre d’un mécanisme de retour cassé.

Si une correction est appliquée sur une interface virtuelle, consignez la valeur d’origine. Si un MSS clamping est mis en place sur un pare-feu, consignez les règles, l’ordre de filtrage et les services affectés. Si vous ajoutez une règle ICMP, spécifiez le type, le code, la zone et le sens requis, selon le modèle de sécurité. Testez l’aller et le retour et conservez une méthode de rollback.

## 10. Les chemins asymétriques, ECMP et changements de route

Les paquets d’une même conversation ne traversent pas toujours exactement les mêmes liens dans les deux sens. Le routage peut être asymétrique : le client envoie à travers un fournisseur, tandis que le serveur répond via un autre. La PMTU utile au client-émetteur et celle utile au serveur-émetteur peuvent alors différer. Une valeur unique configurée à un seul endroit ne résout pas nécessairement les deux directions.

Le routage à coût égal (ECMP) peut aussi distribuer différents flux ou chemins de flux sur plusieurs next-hops. Selon l’algorithme de hachage et les équipements utilisés, deux connexions vers la même destination peuvent ne pas emprunter le même trajet. Si un seul des chemins possède une MTU inférieure, le résultat peut sembler aléatoire : un essai fonctionne, un autre échoue. Il ne faut pas qualifier tout de suite ce comportement de « MTU instable » ; il peut s’agir de plusieurs PMTU associées à des chemins différents.

Lorsque le défaut apparaît après une bascule WAN, un changement d’adresse source ou une modification du routage, notez les heures et comparez les chemins avant et après. Vérifiez si une session existante conserve son état, si les nouveaux flux prennent une autre route et si les caches PMTU ont été invalidés ou mis à jour. Les tests doivent conserver autant que possible la même source, la même destination, le même protocole et la même route pour que les comparaisons soient valables.

Une capture à un seul endroit peut être trompeuse si une route alternative ne passe pas par cet endroit. Si le matériel de laboratoire le permet, capturez aux extrémités et sur le routeur supposé être le point de rupture. Comparez les horodatages, les adresses, les ports, les identifiants de flux et les tailles IP. Pour des environnements réels, la collecte de capture doit respecter les politiques de confidentialité et les règles d’exploitation.

## 11. Méthode de test de MTU : construire une preuve

La méthode la plus utile est une recherche progressive de la taille maximale qui traverse le chemin sans fragmentation, dans le contexte exact du test. Il faut d’abord choisir un test qui rapporte une taille connue. Ensuite, on teste une valeur manifestement inférieure à la limite attendue, on vérifie qu’elle passe, puis on augmente la charge utile. Quand une valeur échoue, on réduit l’intervalle pour trouver la frontière. Ce procédé, proche d’une recherche binaire, réduit le nombre de tests nécessaires par rapport à une progression d’un octet à chaque essai.

Pour un ping IPv4 standard sous Windows, `ping -f -l N destination` demande une charge utile ICMP de N octets et positionne l’option ne pas fragmenter pour le test IPv4. En l’absence d’options IP, le paquet IP vaut normalement N + 28 octets. Avec une MTU de 1500, la valeur de départ classique est 1472. Si 1472 passe et 1473 échoue, l’indice est compatible avec un plafond de 1500 octets sur ce chemin de test. Cela ne démontre toujours pas que le trafic TCP ou UDP de l’application suit la même route ni qu’aucune règle particulière ne s’applique à ICMP.

Sous Linux, `ping -M do -s N destination` est une forme courante pour effectuer un test IPv4 sans fragmentation, mais la syntaxe et le support peuvent varier selon la distribution et l’outil `ping` installé. Pour IPv6, utilisez l’outil et les options correspondant à la version installée ; ne transposez pas aveuglément le calcul IPv4. Dans chaque cas, consultez la page de manuel locale (`man ping`) et identifiez si la valeur correspond à la charge utile ou au paquet IP entier.

### 11.1 Pourquoi les pings peuvent induire en erreur

Le trafic ICMP Echo peut être filtré ou traité différemment du trafic applicatif. Certaines politiques limitent les réponses ICMP, certains routeurs appliquent un rate limiting et des systèmes intermédiaires peuvent donner une priorité différente aux messages de contrôle. Un gros ping peut échouer alors qu’un gros flux TCP fonctionne parce que le chemin et le traitement diffèrent ; inversement, le ping peut passer alors que les paquets TCP volumineux échouent. Il faut donc combiner les tests de ping avec des captures, des essais applicatifs contrôlés et l’observation des messages ICMP PTB.

Un second piège est l’ambiguïté des nombres : dans certaines interfaces, la taille affichée inclut l’en-tête IP, dans d’autres elle ne représente que les données ICMP. Un test de « 1400 octets » peut donc signifier un paquet IP de 1400 octets ou une charge utile de 1400 octets, ce qui crée une différence de 28 octets en IPv4 ICMP standard et de 48 octets en IPv6 ICMPv6 standard. Notez explicitement la signification de chaque valeur dans le compte rendu.

Un troisième piège est le chemin local. Si la commande interroge la passerelle locale plutôt que la destination finale, elle ne mesure que le chemin jusqu’à cette passerelle. Si la destination est un serveur dans le cloud, l’adresse finale, le DNS, le VPN et le routage peuvent changer l’itinéraire réel. Testez depuis l’hôte concerné vers la destination exacte, puis comparez si possible à un second point de référence.

## 12. Commandes utiles sur Windows et Linux

Les commandes ci-dessous sont des outils d’observation. Elles ne doivent pas être lancées en aveugle avec des changements de configuration. Les noms d’interface, l’index, l’adresse IP et les options varient selon les systèmes. Effectuez les tests dans un cadre autorisé et notez leur sortie complète.

### 12.1 Windows : examiner l’interface et les routes

```powershell
# Affiche les interfaces IPv4 et leur MTU
netsh interface ipv4 show subinterfaces

# Affiche les interfaces IP connues de Windows
Get-NetIPInterface | Format-Table ifIndex,InterfaceAlias,AddressFamily,NlMtu,ConnectionState

# Affiche les routes IPv4, puis IPv6
Get-NetRoute -AddressFamily IPv4
Get-NetRoute -AddressFamily IPv6

# Test IPv4 sans fragmentation : 1472 octets de données ICMP
ping -4 -f -l 1472 203.0.113.10
```

L’adresse 203.0.113.10 est une adresse de documentation, à remplacer par une destination de test réellement autorisée. La commande `netsh` affiche une vue utile de l’interface, mais elle n’annonce pas la PMTU de toutes les destinations distantes. `Get-NetIPInterface` est également une vue de configuration locale. La PMTU peut être calculée dynamiquement pour un chemin qui n’est pas résumé par le MTU d’interface.

Vous pouvez utiliser `tracert -d destination` pour examiner le chemin apparent, mais `tracert` n’est pas à lui seul un outil de mesure de MTU. Les routeurs qui ne répondent pas aux sondes TTL ou qui filtrent les messages peuvent apparaître sous forme d’astérisques. L’absence d’une réponse à un saut ne signifie pas nécessairement une rupture de transit. Utilisez le chemin tracé comme indice pour choisir les points de capture et les équipements à inspecter.

### 12.2 Linux : interfaces, routes et tests

```bash
# MTU configurées sur les interfaces
ip -br link
ip link show dev eth0

# Route choisie vers une destination, avec l'interface et le next-hop
ip route get 203.0.113.10

# Test IPv4 sans fragmentation (syntaxe fréquente, vérifier man ping)
ping -4 -M do -s 1472 203.0.113.10

# Outil capable d'aider à observer la PMTU selon la distribution
tracepath 203.0.113.10
```

Remplacez `eth0` et l’adresse de documentation par les paramètres de votre laboratoire. `ip link show` rapporte la MTU configurée sur une interface ; il ne prouve pas qu’un chemin distant possède la même MTU. `ip route get` révèle la route actuellement sélectionnée pour cette destination, mais une route multipath ou une modification d’état peut changer le choix. `tracepath` est conçu pour explorer le chemin et peut fournir une indication PMTU, mais ses résultats dépendent des réponses disponibles et de l’implémentation distante.

### 12.3 Captures de paquets

Wireshark permet d’examiner les tailles et les messages. Pour rechercher les erreurs IPv4 de fragmentation nécessaire, un filtre d’affichage courant est `icmp.type == 3 && icmp.code == 4`. Pour ICMPv6 Packet Too Big, utilisez `icmpv6.type == 2`. Le nom exact des champs de filtre peut évoluer entre versions ; utilisez l’autocomplétion de Wireshark ou la documentation associée si la syntaxe est refusée.

Pour TCP, commencez par isoler le flux à l’aide des adresses et ports, puis examinez les segments réémis, les ACK, les fenêtres et les tailles. Des retransmissions ne suffisent pas à conclure à une panne MTU : recherchez un seuil de taille reproductible et la relation temporelle entre la perte et les messages PTB. Si l’interface de capture ne voit que les paquets émis, une absence de retour peut être due à un autre point de rupture. Quand c’est possible, comparez des captures prises des deux côtés de l’équipement suspect.

Les cartes réseau modernes peuvent utiliser des fonctions d’offload comme TSO, GSO, GRO ou LRO. Elles peuvent faire apparaître dans une capture locale des unités plus grandes que les paquets finalement transmis sur le fil, ou regrouper plusieurs paquets reçus. Lors d’un diagnostic avancé, notez où la capture est prise et si les offloads sont actifs. Ne désactivez pas une fonction en production sans raison et sans autorisation ; si l’hypothèse le justifie, testez en laboratoire ou temporairement selon la procédure opérationnelle.

## 13. Lecture d’une capture : signes et limites de la preuve

Un cas classique montre un flux TCP qui établit la connexion au moyen de SYN, SYN-ACK et ACK, puis envoie un gros segment. La destination ne confirme pas la progression attendue ; l’émetteur réémet un segment ayant les mêmes numéros de séquence. Si ce comportement se répète et coïncide avec un point de route dont la MTU est inférieure à la taille du paquet, suspectez une limite de paquet. Cherchez ensuite l’ICMP PTB et vérifiez s’il est émis, transmis et accepté par la source.

Une capture peut donner une preuve directe lorsque le routeur qui rejette les paquets émet une notification indiquant la MTU du prochain lien. Elle fournit alors une borne mesurée de la MTU. Mais elle peut aussi être incomplète : les messages peuvent être filtrés avant le point de capture, capturés dans une interface différente ou perdus avant la source. Dans ce cas, la conclusion correcte est « le message n’est pas visible à ce point de capture », pas « le routeur ne l’a jamais généré ».

Il faut également lire les métadonnées du paquet. Une capture sur une interface VPN peut montrer le paquet intérieur, tandis qu’une capture sur l’interface physique montre le paquet extérieur. Les tailles y sont différentes par construction. Comparer directement les champs de longueur sans identifier la couche est une erreur fréquente. Créez des notes explicites : interface de capture, sens, MTU configurée, famille IP, adresses source/destination, heure et commande utilisée.

L’analyse ne doit pas se limiter au cas de réussite. Capturez une tentative qui échoue et une autre qui fonctionne avec une taille plus petite. Si la seule différence observée est la taille et si les mêmes points sont traversés, l’hypothèse MTU devient plus solide. Si d’autres variables changent, comme l’adresse source ou le chemin, il faut corriger le protocole de test avant de conclure.

## 14. Arbre de décision pour un dépannage reproductible

Le schéma animé suivant résume l’ordre de décision recommandé. L’idée est de séparer trois questions : le défaut dépend-il de la taille, le mécanisme de signalisation fonctionne-t-il, et le problème est-il localisé au chemin tunnelisé ou au chemin direct ? Le but n’est pas de supprimer toute analyse, mais d’empêcher une modification prématurée de l’ensemble du réseau.

<div align="center">
<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="700" viewBox="0 0 1120 700" role="img" aria-labelledby="treeTitle treeDesc" style="max-width:100%;height:auto">
<title id="treeTitle">Arbre de décision animé pour un incident MTU</title><desc id="treeDesc">Le technicien compare petits et gros paquets, vérifie ICMP, compare les chemins et choisit une correction ciblée après capture.</desc>
<defs><linearGradient id="treeBg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#182238"/></linearGradient><marker id="treeA" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0 0L0 6L9 3z" fill="#64748b"/></marker><style>.tt{font-family:Inter,Arial,sans-serif;fill:#e5e7eb}.th{font-size:23px;font-weight:800}.tn{font-size:14px;font-weight:750}.ts{font-size:11px;fill:#cbd5e1}.tbx{fill:#172439;stroke:#475569;stroke-width:1.6}.tgood{fill:#123729;stroke:#16a34a;stroke-width:1.6}.tbad{fill:#3a2028;stroke:#fb7185;stroke-width:1.6}.tpath{stroke:#64748b;stroke-width:3;fill:none;stroke-dasharray:7 6;marker-end:url(#treeA);animation:dash 2s linear infinite}@keyframes dash{to{stroke-dashoffset:-26}}@media(prefers-reduced-motion:reduce){.tpath{animation:none}}</style></defs>
<rect width="1120" height="700" rx="22" fill="url(#treeBg)"/><text x="40" y="45" class="tt th">Arbre de décision : tester, observer, isoler</text>
<rect x="380" y="75" width="360" height="72" rx="14" class="tbx"/><text x="560" y="104" text-anchor="middle" class="tt tn">1. Reproduire la panne</text><text x="560" y="126" text-anchor="middle" class="tt ts">Même source, destination, famille et protocole</text>
<path d="M560 147V185H280V215M560 185H840V215" class="tpath"/><text x="415" y="177" class="tt ts">Comparer tailles</text>
<rect x="70" y="215" width="420" height="82" rx="13" class="tgood"/><text x="280" y="245" text-anchor="middle" class="tt tn">Petits ET gros paquets passent</text><text x="280" y="268" text-anchor="middle" class="tt ts">Chercher une autre cause ; ne pas conclure MTU</text>
<rect x="630" y="215" width="420" height="82" rx="13" class="tbad"/><text x="840" y="245" text-anchor="middle" class="tt tn">Petits passent, gros échouent</text><text x="840" y="268" text-anchor="middle" class="tt ts">Indice fort, à confirmer avec capture</text>
<path d="M840 297V338H560V365" class="tpath"/><rect x="345" y="365" width="430" height="82" rx="13" class="tbx"/><text x="560" y="395" text-anchor="middle" class="tt tn">2. Capturer ICMP et le flux</text><text x="560" y="418" text-anchor="middle" class="tt ts">Type/code PTB, tailles, retransmissions et sens</text>
<path d="M560 447V485H280V515M560 485H840V515" class="tpath"/><rect x="65" y="515" width="430" height="84" rx="13" class="tgood"/><text x="280" y="546" text-anchor="middle" class="tt tn">PTB visible et traité</text><text x="280" y="569" text-anchor="middle" class="tt ts">Vérifier MTU réelle, routage et cache PMTU</text><rect x="625" y="515" width="430" height="84" rx="13" class="tbad"/><text x="840" y="546" text-anchor="middle" class="tt tn">PTB absent ou bloqué</text><text x="840" y="569" text-anchor="middle" class="tt ts">Localiser émission, transit, pare-feu et réception</text>
<path d="M280 599V625H560M840 599V625H560V642" class="tpath"/><rect x="315" y="642" width="490" height="42" rx="10" fill="#123729" stroke="#16a34a"/><text x="560" y="668" text-anchor="middle" class="tt tn">3. Appliquer une correction minimale et revalider</text></svg>
</div>

### Étape A : formaliser l’incident

Notez le nom de l’application, la destination exacte, le protocole connu, la famille IP, l’heure de l’essai et le symptôme précis. « Internet lent » est trop vague ; « l’upload HTTPS s’établit puis reste bloqué après l’envoi d’environ 64 Ko, seulement lorsque le VPN est actif » fournit des pistes testables. Le but est de faire varier un seul facteur à la fois et de pouvoir comparer la panne après chaque action.

### Étape B : contrôler les petits et les grands paquets

Effectuez un ping de taille modeste, puis un test plus grand avec les options permettant d’éviter la fragmentation, si votre système les expose. Cherchez une frontière reproductible. Un plafond constant proche d’une certaine taille est un indice de MTU ; des pertes indépendantes de la taille peuvent correspondre à une autre cause. Répétez les mesures pour réduire le risque de confondre une perte ponctuelle avec une limite de paquet.

### Étape C : identifier la famille et le chemin

Forcez IPv4 puis IPv6 séparément. Vérifiez la route et les interfaces concernées. Si le VPN est actif, comparez le chemin intérieur et le chemin extérieur. Une différence de résultat entre familles ou états du tunnel réduit le périmètre de recherche, mais ne localise pas encore le routeur fautif.

### Étape D : capturer le message de contrôle

Capturez près de la source, puis sur le routeur ou pare-feu suspect si vous disposez de l’accès et de l’autorisation. Filtrez les messages ICMPv4 type 3 code 4 et ICMPv6 type 2. Vérifiez qu’ils font référence au trafic testé. S’ils sont présents à la sortie du routeur et absents à la source, examinez les règles et le chemin retour. S’ils n’apparaissent nulle part, vérifiez si le routeur émetteur les génère et si le paquet excède réellement la MTU de sortie.

### Étape E : choisir une correction contrôlée

La correction dépend de la cause établie. Elle peut consister à autoriser les messages ICMP/PTB nécessaires, réduire la MTU de l’interface tunnel, corriger une encapsulation, ajuster la MSS sur les flux TCP concernés ou corriger une route anormale. N’appliquez pas toutes ces solutions simultanément : vous perdriez la capacité de savoir laquelle a réellement résolu le défaut et vous pourriez masquer un problème ailleurs.

### Étape F : vérifier la non-régression

Répétez le test initial, puis un transfert applicatif réel, un test inverse si pertinent et un test IPv6 si ce trafic est attendu. Vérifiez la taille des segments, l’absence de retransmissions associées à la taille et la réception des messages de contrôle lorsque des paquets de sonde dépassent la limite. Testez également les fonctions non directement visées afin de détecter une réduction excessive de taille ou une règle trop large.

## 15. PLPMTUD et DPLPMTUD : découvrir sans dépendre uniquement d’ICMP

Le PMTUD classique peut échouer lorsque les messages PTB sont perdus, filtrés ou mal traités. Le Packetization Layer Path MTU Discovery (PLPMTUD) ajoute une logique de sondage au niveau de la couche qui découpe les données en paquets. Au lieu de se fier exclusivement à un message de routeur, l’émetteur envoie un paquet de sonde d’une taille déterminée et cherche une confirmation de livraison fournie par le protocole ou l’application. Si une sonde ne réussit pas de manière répétée alors que des sondes plus petites fonctionnent, l’algorithme peut diminuer l’estimation et chercher une taille compatible.

DPLPMTUD est l’adaptation de cette stratégie aux transports datagrammes. Il doit distinguer l’absence d’accusé de réception causée par une taille trop grande d’une perte ordinaire due à la congestion, à un serveur arrêté ou à un chemin défaillant. Le choix de la fréquence, du nombre de sondes et du comportement de repli est donc important. Le mécanisme s’appuie sur des retours disponibles au niveau du transport ou de l’application ; un UDP brut n’offre pas, en soi, un accusé de réception fiable. Une application utilisant UDP doit définir ou employer un protocole capable de fournir le retour requis, ou suivre une stratégie adaptée au protocole utilisé.

La différence conceptuelle à retenir est la suivante : PMTUD classique utilise principalement les indications explicites de la couche IP ; PLPMTUD utilise des sondes de couche de paquetisation ; DPLPMTUD précise cette approche pour des transports datagrammes. Ces mécanismes ne doivent pas être activés sans coordination à plusieurs couches en même temps, car des états redondants peuvent provoquer des sondages inutiles, des limites incohérentes ou une confusion sur la taille réellement utilisable par l’application.

QUIC, qui utilise UDP mais fournit des mécanismes de retour au niveau du transport, peut utiliser des sondes adaptées à la découverte de paquetisation. Cela ne veut pas dire qu’un administrateur peut ignorer les MTU du réseau : il reste nécessaire de permettre le passage des paquets utiles, de gérer les messages PTB et de diagnostiquer les pertes. Une implémentation robuste peut détecter une taille qui ne fonctionne pas, mais une configuration réseau correcte demeure préférable à une perte permanente de paquets de grande taille.

Dans un environnement d’entreprise, le technicien n’a pas toujours accès aux paramètres de PLPMTUD du système d’exploitation ou de l’application. Il peut cependant observer les tailles utilisées, les messages de contrôle, les délais et la différence entre un trafic de petite taille et un trafic de grande taille. Lorsqu’un protocole utilise une découverte intégrée, consultez les journaux et les traces propres à ce protocole au lieu d’extrapoler uniquement à partir d’un ping.

## 16. Sécurité : ICMP doit être filtré intelligemment

Une politique de sécurité sérieuse doit réduire les surfaces d’attaque tout en conservant le fonctionnement requis du réseau. Bloquer en bloc tout ICMP peut interrompre le PMTUD et provoquer des pannes difficiles à diagnostiquer. À l’inverse, autoriser tout ICMP sans limites ni validation n’est pas non plus une politique correcte. Les règles doivent tenir compte des types et codes utilisés, des zones, des interfaces, des directions, des exigences de l’architecture et des capacités de validation des équipements.

Les messages d’erreur IP peuvent être falsifiés. Les hôtes doivent les corréler à du trafic récemment émis et vérifier qu’ils sont plausibles avant de modifier l’estimation d’un chemin. Les équipements et les systèmes d’exploitation mettent en œuvre des formes de validation ; leur comportement spécifique doit être consulté dans la documentation du produit. Le rôle de l’administrateur est de permettre la signalisation nécessaire tout en conservant les contrôles de cohérence.

Une MTU artificiellement réduite peut aussi être utilisée pour provoquer une dégradation de performance si l’hôte accepte aveuglément des messages malveillants. La bonne réponse ne consiste donc pas à désactiver la découverte, mais à vérifier le flux cité, l’origine et le contenu du message. En IPv6, un Packet Too Big indiquant une valeur inférieure à la MTU minimale de lien définie par les spécifications de base ne doit pas conduire l’hôte à utiliser une valeur incompatible ; les règles précises sont définies par le RFC IPv6 PMTUD.

Pour les investigations, limitez les captures aux interfaces, adresses et durées nécessaires. Les traces TCP peuvent exposer des métadonnées, des noms d’hôtes, des ports ou, dans certains protocoles, des données applicatives non chiffrées. Les fichiers de capture doivent être stockés et partagés conformément aux politiques de l’organisation. N’exportez pas de données sensibles vers un service tiers sans autorisation explicite.

## 17. Cas pratique 1 — Le site HTTPS s’ouvre mais le transfert reste bloqué

**Contexte.** Un poste de bureau atteint un site distant. La résolution DNS fonctionne, l’établissement TCP/HTTPS est visible, la page semble commencer à charger, puis certains contenus restent incomplets. Un ping standard vers le serveur répond. Le défaut touche seulement certains postes connectés via un pare-feu ou un tunnel différent.

**Hypothèses initiales.** Le problème peut être lié à la MTU, mais aussi au proxy, à l’inspection TLS, à une perte de segments, à une règle applicative ou à la capacité du serveur. La réussite d’un ping de petite taille élimine seulement certaines causes évidentes ; elle ne garantit pas les paquets de données plus grands. Il faut d’abord déterminer si les postes affectés partagent un même chemin réseau ou une même configuration VPN.

**Procédure.** Notez une URL de test, une heure précise, l’adresse IP obtenue et le poste concerné. Capturez le flux TCP pendant que le navigateur est bloqué. Examinez les segments réémis, les tailles IP et la progression des ACK. Faites ensuite un ping avec une charge utile croissante, en évitant la fragmentation lorsque possible. Comparez les résultats avec un poste qui fonctionne, idéalement sur le même réseau et vers la même adresse.

Si les gros paquets échouent seulement depuis le chemin suspect, mesurez la limite approximative et cherchez les messages PTB. Si la notification est générée mais filtrée, corrigez la règle précise au lieu d’autoriser indistinctement tous les protocoles de contrôle. Si le site ne répond pas à ICMP, utilisez un service de test connu ou la capture d’un flux applicatif autorisé pour vérifier la taille. Ne prenez pas l’absence de réponse à un ping comme une preuve de panne MTU.

**Validation.** Relancez la même session HTTPS, transférez un contenu de taille suffisante et vérifiez qu’aucune série de retransmissions n’est liée à des segments trop grands. Répétez sur un second poste affecté et un poste non affecté. Documentez si la correction est une règle ICMP, un ajustement tunnel ou une modification MSS, et notez le comportement avant/après.

## 18. Cas pratique 2 — Le problème n’existe que lorsque le VPN est activé

**Contexte.** Un utilisateur peut télécharger un fichier sans VPN, mais le téléchargement se fige quand le VPN d’entreprise est actif. Les applications d’authentification et les échanges de texte semblent fonctionner. Le phénomène touche surtout les flux volumineux ou les réponses du serveur.

**Hypothèse.** Le tunnel peut réduire la capacité utile à cause de l’encapsulation. Toutefois, l’activation du VPN modifie parfois aussi la route par défaut, les DNS, l’inspection ou les règles d’accès. On ne doit pas confondre corrélation et cause.

**Procédure.** Choisissez une destination de test autorisée et conservez les mêmes conditions de transfert. Comparez le résultat VPN désactivé et activé. Notez l’interface de sortie et la route choisie. Testez progressivement la taille maximale avec les options de non-fragmentation prises en charge. Capturez le paquet intérieur sur l’interface VPN et le paquet extérieur sur l’interface physique, si vous en avez l’autorisation.

Calculez la surcharge de l’encapsulation réelle, sans appliquer un nombre générique de tête. Vérifiez les événements ICMP PTB et le chemin du retour. Si le tunnel est configuré avec une MTU trop élevée, ajustez-la selon la capacité déterminée. Si le tunnel ne peut pas recevoir les messages nécessaires, examinez les règles de filtrage et le mécanisme de repli disponible. Si TCP est le seul protocole concerné et que le mécanisme de PMTUD est temporairement bloqué par une contrainte connue, un MSS clamping ciblé peut être une mitigation documentée ; il ne corrigera pas nécessairement UDP/QUIC.

**Validation.** Recommencez le test de transfert, vérifiez l’upload comme le download et contrôlez que les autres usages du VPN fonctionnent toujours. Vérifiez la performance : une valeur trop basse peut rendre le service fonctionnel tout en augmentant sensiblement le nombre de paquets. Inscrivez la configuration précédente et un plan de retour arrière.

## 19. Cas pratique 3 — IPv4 fonctionne, IPv6 échoue

**Contexte.** Un service possède un enregistrement A et un enregistrement AAAA. Le navigateur ou l’application tente IPv6, mais certains contenus prennent un temps anormal ou échouent ; IPv4 semble normal. Un test rapide peut masquer le problème si l’application bascule automatiquement entre familles.

**Procédure.** Reproduisez le défaut en forçant une famille à la fois. Vérifiez que la destination est bien celle attendue. Comparez le chemin IPv6, la MTU des interfaces et les tunnels éventuels. Capturez ICMPv6 et recherchez Packet Too Big, type 2. Ne cherchez pas seulement l’équivalent IPv4 type 3 code 4 : le filtre et le traitement sont différents.

Si le paquet IPv6 trop grand est abandonné sans PTB visible, capturez près du routeur supposé être le point de rupture et suivez le message jusqu’à la source. Vérifiez que les règles de sécurité autorisent les types ICMPv6 nécessaires et qu’une politique conçue pour IPv4 n’a pas été transposée de façon incorrecte. Assurez-vous que les outils de test produisent réellement des paquets IPv6 et que le chiffre de taille se rapporte à la même couche que votre calcul.

**Résultat attendu.** Le but n’est pas d’abaisser systématiquement toutes les interfaces IPv6 à une valeur minimale. Il faut découvrir le lien limitant, restaurer le retour PTB et assurer la prise en compte correcte de la PMTU. Validez un transfert IPv6 réel et vérifiez qu’aucun contournement par IPv4 ne masque encore le défaut.

## 20. Cas pratique 4 — Seule une direction est affectée

**Contexte.** Les petits paquets du poste vers le serveur passent, et les gros paquets dans cette direction semblent fonctionner. En revanche, le serveur envoie des réponses volumineuses que le poste ne reçoit pas complètement. L’inverse est également possible.

**Analyse.** Le diagnostic doit séparer le sens client-vers-serveur du sens serveur-vers-client. Le routage peut être asymétrique ; l’un des deux chemins peut traverser un tunnel ou une liaison de MTU plus petite. Une règle de pare-feu ou un filtrage ICMP peut être appliqué différemment dans les deux sens. La MTU et la PMTU ne doivent donc pas être traitées comme un chiffre global unique pour la conversation.

**Procédure.** Réalisez un transfert dans les deux sens si le protocole le permet. Capturez simultanément ou de manière coordonnée aux deux extrémités. Mesurez quelle direction présente les retransmissions, quelles tailles sont émises, quelles tailles sont reçues et si des PTB remontent à l’émetteur de cette direction. Comparez les interfaces de sortie et les routes. Si possible, forcez le trafic vers le même chemin ou utilisez un point de capture intermédiaire.

**Correction.** Ajustez la règle ou le paramètre à l’endroit qui correspond à la cause. Une modification sur le poste client ne réglera pas forcément un problème où les paquets trop grands sont émis par le serveur. Évitez de déployer un MSS clamping unidirectionnel sans vérifier qui initie la connexion et quels segments l’équipement réécrit.

## 21. Cas pratique 5 — Panne intermittente après une bascule WAN

**Contexte.** Après le basculement d’un accès Internet vers un second fournisseur, une application fonctionne avec certains utilisateurs mais pas d’autres. Le changement de route modifie parfois le transit des paquets sans modifier l’adresse de destination. L’ancien chemin pouvait supporter une MTU plus élevée que le nouveau.

**Procédure.** Rassemblez l’heure de bascule, les routes actives, l’adresse source utilisée, l’interface de sortie et les résultats de tests par destination. N’utilisez pas uniquement une capture prise avant le changement. Répétez les mesures après la bascule et contrôlez si les tests choisissent un chemin stable ou multipath. Comparez la PMTU et les réponses ICMP sur les deux chemins.

Une estimation PMTU en cache peut rester valide pendant un certain temps, alors que la route est différente. Selon la pile, la route et les sessions, l’estimation peut être recalculée ou conservée différemment. Évitez de supprimer systématiquement tous les caches sans avoir de preuve ; cela peut masquer le caractère intermittent et affecter des connexions en cours. Si vous devez réinitialiser un cache en environnement contrôlé, consignez la procédure et comparez le comportement avant/après.

La correction durable se situe souvent dans la configuration de la liaison de secours, l’autorisation du PTB ou la cohérence des MTU des routes et tunnels. La validation doit inclure au moins une bascule contrôlée et le retour au chemin nominal, afin de vérifier que le défaut ne réapparaît pas au prochain incident WAN.

## 22. Erreurs fréquentes de diagnostic

**Erreur 1 : réduire toutes les MTU sans localiser le problème.** Cette action peut masquer la cause, réduire le rendement de plusieurs réseaux et créer des configurations incompatibles. Préférez une mesure qui détermine la limite réelle et cible l’interface ou le flux approprié.

**Erreur 2 : bloquer tout ICMP pour « sécuriser » le réseau.** Certains messages sont indispensables à la bonne découverte de la taille maximale. Construisez des règles contrôlées par type/code et contexte, et vérifiez le passage de bout en bout des retours requis.

**Erreur 3 : considérer le ping standard comme une preuve suffisante.** Les petits paquets peuvent passer alors que les gros sont perdus. Testez les tailles, mais confirmez avec une application et une capture lorsque c’est possible.

**Erreur 4 : confondre MSS et MTU.** La MSS concerne les données TCP annoncées par une extrémité ; la MTU concerne la taille du paquet IP sur un lien ; la PMTU concerne le minimum des MTU du chemin. Les valeurs interagissent mais ne sont pas interchangeables.

**Erreur 5 : copier un overhead VPN pris sur Internet.** Les tailles changent selon les modes et options. Mesurez les en-têtes réels ou utilisez la documentation de la configuration exacte.

**Erreur 6 : croire que l’absence de message dans une capture signifie qu’il n’a pas été envoyé.** La capture peut être prise au mauvais endroit ou le message peut être filtré en amont. Comparez les points de capture lorsque la portée du défaut est importante.

**Erreur 7 : négliger IPv6.** Une règle conçue pour ICMPv4 ne couvre pas automatiquement ICMPv6. Vérifiez explicitement les deux familles si le réseau les utilise.

**Erreur 8 : appliquer MSS clamping à UDP.** Le mécanisme modifie une option TCP ; il ne règle pas directement la taille des datagrammes UDP et n’est pas une solution universelle à QUIC.

**Erreur 9 : changer plusieurs variables à la fois.** Si vous changez MTU, MSS, ACL et route en même temps, vous ne saurez pas quelle action a résolu la panne ni laquelle introduit une régression. Faites une modification à la fois et gardez un plan de rollback.

**Erreur 10 : oublier les offloads de capture.** Les paquets observés sur l’hôte peuvent ne pas refléter exactement le découpage physique des paquets sur le fil. Vérifiez le point de capture, les fonctions d’offload et les limites de l’outil.

## 23. Atelier guidé : découvrir une MTU de chemin dans un laboratoire

L’exercice suppose deux machines séparées par un routeur ou une interface configurée avec une MTU plus petite. N’effectuez aucune modification sur un réseau de production sans autorisation. L’objectif n’est pas de provoquer une panne chez des utilisateurs, mais de comprendre la séquence de mesure et la preuve attendue.

### Préparation

Dessinez la topologie : poste A, routeur R1, lien limité, routeur R2 éventuel et poste B. Notez les adresses, les interfaces et les MTU configurées. Assurez-vous que vous pouvez capturer au poste A et, si possible, sur l’interface de sortie du routeur qui possède la MTU limitée. Synchronisez les horloges pour que les horodatages soient comparables.

### Série de tests

Commencez par un ping de petite taille vers B et notez le résultat. Augmentez ensuite la charge utile progressivement, avec l’option de non-fragmentation IPv4 lorsque disponible. Si une taille passe et la taille suivante échoue, répétez plusieurs fois. Si le résultat change d’une exécution à l’autre, vérifiez les pertes générales, le rate limiting ICMP et la stabilité du chemin avant d’établir la frontière.

Capturez la sonde qui échoue. Déterminez si le paquet quitte réellement A, s’il atteint R1 et si un message ICMP est émis. Si le message indique une MTU de 1400, vérifiez que la taille IP du test excède cette valeur et que l’émetteur peut traiter la réponse. Envoyez ensuite une taille compatible et vérifiez qu’elle atteint B. Répétez avec une route ou une MTU différente si votre laboratoire permet de le faire sans risque.

### Questions à rédiger

1. Quelle taille est rapportée par la commande : données ICMP ou paquet IP entier ?
2. Quelle est la MTU de chaque interface, et laquelle est la plus petite sur le chemin ?
3. Le routeur émet-il bien le message ICMP approprié ?
4. La source reçoit-elle et traite-t-elle ce message ?
5. La nouvelle taille passe-t-elle dans les deux sens ?
6. La conclusion est-elle appuyée par une capture et une mesure répétée ?

Le rapport de laboratoire doit distinguer les observations des interprétations. Écrivez, par exemple, « la capture prise sur l’interface externe montre un ICMPv4 type 3 code 4 après l’envoi de la sonde de 1473 octets de données » plutôt que « le routeur est mal configuré », sauf si la configuration observée confirme effectivement cette conclusion.

## 24. Atelier d’analyse Wireshark

Ouvrez une capture d’essai et commencez par un filtre ICMPv4 `icmp.type == 3 && icmp.code == 4`, puis un filtre ICMPv6 `icmpv6.type == 2`. Pour chaque message repéré, consignez l’adresse source du message, la destination du paquet original lorsqu’elle est disponible, le type/code, la valeur de MTU rapportée et l’horodatage. Comparez ces informations à la sonde qui l’a déclenché. Si Wireshark ne décode pas le champ de MTU, examinez la version de l’outil et la structure du message à l’aide de la documentation du protocole, sans deviner la valeur.

Passez ensuite au flux TCP affecté. Utilisez « Follow TCP Stream » si cela facilite l’identification de la session, mais ne vous limitez pas à la vue reconstituée du contenu. Examinez les numéros de séquence, les ACK, les longueurs de segments et les retransmissions. Repérez le dernier octet confirmé par le destinataire. Si les mêmes octets sont réémis à plusieurs reprises et qu’aucun ACK de progression n’arrive, comparez la taille de ces segments avec la PMTU déterminée par les tests.

Pour comparer les points de capture, exportez uniquement le flux nécessaire ou utilisez des filtres correspondant au quintuplet IP/protocole/ports. Les adresses, ports, VLAN, encapsulations et horodatages aident à corréler les paquets entre interfaces. N’oubliez pas que le NAT peut modifier les adresses ou ports et que des captures prises avant/après NAT ne montreront pas nécessairement le même quintuplet.

Un rapport d’analyse solide inclut au minimum une capture réussie et une capture échouée, ou une explication explicite de leur indisponibilité ; les tailles des paquets ; la MTU des interfaces pertinentes ; la présence ou l’absence du retour ICMP au point observé ; et la conclusion limitée à ce que la preuve permet d’affirmer. Il doit aussi consigner les hypothèses alternatives qui ne sont pas encore éliminées.

## 25. Fiche de référence rapide

- **MTU de lien :** taille maximale IP supportée par un lien dans la configuration considérée.
- **PMTU :** minimum des MTU des liens réellement traversés par le chemin concerné.
- **IPv4 PMTUD classique :** le message de signalisation usuel est ICMP Destination Unreachable, type 3, code 4, fragmentation nécessaire.
- **IPv6 PMTUD classique :** le message de signalisation est ICMPv6 Packet Too Big, type 2 ; les routeurs ne fragmentent pas les paquets IPv6 en transit.
- **MSS TCP :** limite de données TCP annoncée par le pair, distincte de la MTU.
- **PMTUD black hole :** les paquets trop grands sont abandonnés et la source ne reçoit pas de signalisation utile.
- **MSS clamping :** mitigation pour TCP uniquement ; elle ne réduit pas directement les datagrammes UDP.
- **VPN :** calculez la surcharge réelle, ne copiez pas une valeur universelle.
- **Capture :** relevez le point de capture, la famille IP, les tailles, le message ICMP et le sens.
- **Correction :** changez une chose à la fois, mesurez avant/après et prévoyez le retour arrière.

## 26. Mini-évaluation intermédiaire

Répondez sans consulter les sections précédentes, puis comparez avec le corrigé.

**Question 1.** Une MTU de 1500 est configurée sur le PC. Un lien distant du chemin n’accepte que 1380 octets. Quelle est la PMTU du chemin si tous les autres liens acceptent au moins 1500 octets ?

**Question 2.** Pour un ping IPv4 standard sans options, quelle est la taille IP totale approximative lorsqu’on utilise une charge utile ICMP de 1472 octets ?

**Question 3.** Quel message ICMPv4 est associé au cas où un routeur ne peut pas transférer un datagramme IPv4 avec DF activé parce que le paquet est trop grand ?

**Question 4.** Quel type de message ICMPv6 indique que le paquet dépasse la MTU du lien suivant ?

**Question 5.** Pourquoi un ping de taille standard peut-il réussir alors qu’un téléchargement reste bloqué ?

**Question 6.** La MSS est-elle la même chose que la PMTU ? Justifiez votre réponse en une phrase.

**Question 7.** Pourquoi un MSS clamping ne suffit-il pas à corriger un flux UDP affecté ?

**Question 8.** Quelles sont les deux grandes hypothèses à distinguer lorsqu’aucun message PTB n’apparaît dans la capture de la source ?

**Question 9.** Pourquoi une MTU de tunnel ne doit-elle pas être choisie seulement à partir d’un chiffre trouvé en ligne ?

**Question 10.** Qu’est-ce qu’un PMTUD black hole ?

**Question 11.** Quelle différence centrale sépare PLPMTUD du PMTUD classique ?

**Question 12.** Pourquoi comparer IPv4 et IPv6 séparément ?

**Question 13.** Que devez-vous vérifier si la panne n’apparaît qu’après une bascule WAN ?

**Question 14.** Une capture sur l’interface locale montre un paquet de taille supérieure à la MTU. Pourquoi cette observation ne prouve-t-elle pas toujours qu’un tel paquet a été transmis tel quel sur le réseau physique ?

**Question 15.** Citez quatre éléments qui doivent apparaître dans un rapport de dépannage MTU exploitable.

### Corrigé

1. La PMTU est 1380 octets, car elle correspond au plus petit MTU de la route réellement utilisée.
2. Environ 1500 octets au niveau IP : 20 octets d’en-tête IPv4 + 8 octets d’ICMP + 1472 octets de données.
3. ICMPv4 Destination Unreachable, type 3, code 4, « fragmentation nécessaire ».
4. ICMPv6 Packet Too Big, type 2.
5. Le petit ping n’atteint pas nécessairement la limite du chemin ; les paquets volumineux peuvent être perdus et le message PTB peut être filtré ou mal traité.
6. Non. La MSS décrit la quantité maximale de données TCP annoncée par un pair, tandis que la PMTU décrit la plus petite MTU des liens du chemin.
7. Le MSS clamping modifie des options TCP dans les SYN ; il ne dimensionne pas directement les datagrammes UDP.
8. Le message n’a pas été généré, ou il a été généré mais perdu/filtré avant la source ; une capture incomplète est également possible et doit être éliminée.
9. L’overhead dépend du tunnel, des options, de la famille IP et des mécanismes de sécurité utilisés.
10. Une situation où les paquets dépassant la MTU sont abandonnés sans signalisation utile permettant à l’émetteur de réduire leur taille.
11. Le PMTUD classique dépend surtout des messages d’erreur IP ; PLPMTUD ajoute des sondes et des retours de la couche de paquetisation.
12. Les routes, filtres, interfaces et messages de contrôle peuvent différer ; les deux familles ne partagent pas automatiquement un même chemin ou une même PMTU.
13. La route choisie, l’adresse source, l’interface de sortie, le cache PMTU, le comportement du second fournisseur et le passage des messages PTB.
14. Les offloads réseau et le point de capture peuvent faire apparaître une représentation qui ne correspond pas exactement au découpage sur le fil.
15. Au minimum : contexte, topologie/MTU mesurées, tailles testées, captures/messages observés, hypothèse confirmée, correction appliquée, vérification et plan de retour arrière. Quatre de ces éléments constituent le minimum de départ, mais un rapport professionnel doit être plus complet.

## 27. Modèle de rapport d’incident à compléter

**Titre de l’incident :** blocage associé à une taille de paquet suspecte.  
**Date et créneau :** noter les heures et le fuseau.  
**Impact utilisateur :** services, utilisateurs, sites et directions de trafic affectés.  
**Topologie :** source, destination, route, interfaces intermédiaires connues et présence éventuelle d’un tunnel.  
**Configuration mesurée :** MTU de chaque interface pertinente, famille IP, état des routes et règles concernées.  
**Symptôme :** décrire ce qui fonctionne, ce qui échoue et à partir de quelle étape.  
**Tests :** commandes exactes, tailles des charges utiles, nombre de répétitions et résultats.  
**Captures :** points de capture, filtres, horodatages, messages ICMP et retransmissions observées.  
**Hypothèse :** expliquer le mécanisme en reliant la taille, le lien limité et la signalisation absente ou traitée.  
**Correction :** changement précis, périmètre, responsable, valeur avant/après et rollback.  
**Validation :** tests réalisés, résultat, contrôles de non-régression et suivi après changement.  
**Incertitudes restantes :** hypothèses qui n’ont pas pu être confirmées, contraintes d’accès et mesures recommandées.

Le rapport doit préserver la traçabilité : une autre personne doit pouvoir répéter le test sans devoir deviner la destination ou l’interprétation de la taille. Les captures peuvent être référencées par nom de fichier et filtre, en évitant d’y insérer des données sensibles inutiles. Précisez si les tests ont été réalisés dans un laboratoire, sur un environnement de préproduction ou en production.

## 28. Checklist opérationnelle de dépannage

- [ ] Le symptôme est décrit avec une destination et un protocole précis.
- [ ] Les tests utilisent la même source, la même destination et la même famille IP.
- [ ] La taille affichée est identifiée comme charge utile ou taille IP.
- [ ] Une taille modeste et plusieurs tailles plus grandes ont été comparées.
- [ ] Les essais sont répétés afin de distinguer une limite d’une perte ponctuelle.
- [ ] Les MTU de l’hôte, du tunnel et des liens pertinents ont été relevées.
- [ ] Les routes et les changements récents sont consignés.
- [ ] Les messages ICMPv4 type 3/code 4 et ICMPv6 type 2 ont été recherchés si pertinents.
- [ ] Le point de génération et le point de réception du PTB sont distingués.
- [ ] Le trafic TCP a été examiné pour les retransmissions et la progression des ACK.
- [ ] Le trafic UDP ou QUIC n’a pas été supposé corrigé par le MSS clamping.
- [ ] La correction choisie correspond à la cause confirmée.
- [ ] Une seule variable principale a été modifiée à la fois.
- [ ] Les tests aller et retour ont été réalisés quand ils sont pertinents.
- [ ] Les services non ciblés ont été vérifiés pour les régressions.
- [ ] Une valeur antérieure et un plan de retour arrière sont disponibles.
- [ ] Les preuves sont jointes au rapport sans données sensibles non nécessaires.

## 29. Résumé final : raisonner par couche et par preuve

Les incidents MTU ne se résolvent pas durablement par une valeur magique. La MTU d’interface, la PMTU du chemin, la MSS TCP et la taille utile au niveau applicatif sont des valeurs liées, mais différentes. La bonne taille dépend du trajet réel, des options et des en-têtes ajoutés en route. Le même serveur peut présenter une limite différente selon la famille IP, le fournisseur, le tunnel ou le sens du flux.

Le PMTUD classique dépend du retour ICMP approprié : en IPv4, il s’agit typiquement de Destination Unreachable type 3/code 4 lorsqu’un datagramme non fragmentable ne peut pas être envoyé ; en IPv6, il s’agit de Packet Too Big type 2. Si le message nécessaire est absent, le paquet trop grand peut être abandonné sans que la source puisse s’adapter : c’est le scénario caractéristique du PMTUD black hole. PLPMTUD et DPLPMTUD ajoutent des méthodes de découverte par sondes, mais la visibilité et la correction du réseau restent importantes.

La démarche efficace combine des tests reproductibles, des calculs explicites d’en-têtes, l’observation des routes, des captures de part et d’autre du point suspect et une modification minimale. Les solutions possibles — autoriser un message de contrôle, corriger un tunnel, ajuster une MTU, appliquer un MSS clamping ciblé ou corriger un chemin — doivent découler de la preuve recueillie. Après la correction, reproduisez le test initial, vérifiez le transfert réel, testez les deux sens lorsque nécessaire et conservez les données avant/après.

L’objectif professionnel est double : rétablir le service et pouvoir expliquer la cause d’une manière vérifiable. Un bon compte rendu indique ce qui a été observé, ce que cela démontre, ce qui reste incertain et comment la correction a été validée. Cette discipline évite les changements globaux inutiles et rend les incidents récurrents plus faciles à traiter.

## 30. Références techniques

Les RFC suivantes constituent les références principales pour les mécanismes décrits. Pour les détails exacts d’une implémentation, complétez-les par la documentation du système d’exploitation, du routeur, du pare-feu, du VPN et de l’outil de capture utilisés.

- **RFC 1191 — Path MTU Discovery** (PMTUD IPv4 classique) : <https://www.rfc-editor.org/rfc/rfc1191.html>
- **RFC 8201 — Path MTU Discovery for IP version 6** (PMTUD IPv6) : <https://www.rfc-editor.org/rfc/rfc8201.html>
- **RFC 4821 — Packetization Layer Path MTU Discovery** (PLPMTUD) : <https://www.rfc-editor.org/rfc/rfc4821.html>
- **RFC 8899 — Datagram Packetization Layer Path MTU Discovery for Datagram Transports** (DPLPMTUD) : <https://www.rfc-editor.org/rfc/rfc8899.html>
- **RFC 2923 — TCP Problems with Path MTU Discovery** (pannes de type black hole) : <https://www.rfc-editor.org/rfc/rfc2923.html>
- **RFC 792 — Internet Control Message Protocol** (ICMPv4) : <https://www.rfc-editor.org/rfc/rfc792.html>

**Note de version :** les outils et interfaces de configuration changent selon les systèmes. Vérifiez la documentation de la version réellement installée avant d’exécuter une commande en production. Ce cours fournit une méthode de diagnostic pédagogique et ne remplace pas la documentation spécifique de l’équipement ni les procédures de changement de votre organisation.


## Rapport final de comptage des mots

**Nombre de mots du cours : 11 055.** Le seuil demandé de 5 000 mots est dépassé de 6 055 mots.

**Méthode de calcul :** comptage automatique des sections pédagogiques 1 à 30, en excluant le présent rapport et l’introduction de comptage, les cinq blocs de code SVG animés, les deux blocs de commandes clôturés par des triples accents graves, les balises HTML de présentation et les expressions de code en ligne. Les titres, paragraphes, tableaux, listes, légendes rédigées, questions, corrigés et références textuelles du cours sont inclus. Les mots avec apostrophes ou traits d’union sont comptés comme une unité. Un autre logiciel peut donner un total légèrement différent selon sa gestion des mots composés et des URL.

**Contrôle des schémas :** cinq éléments SVG animés sont intégrés directement dans ce fichier Markdown ; leurs cinq blocs XML ont été analysés avec succès. Le code des schémas et les commandes ne sont pas inclus dans le total pédagogique.
