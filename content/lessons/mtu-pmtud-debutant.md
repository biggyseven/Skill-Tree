# Dépannage MTU et PMTUD — Niveau débutant

> **Objectif du cours :** comprendre pourquoi des paquets IP trop grands peuvent être bloqués sur le réseau, apprendre à tester la taille maximale d’un paquet sans fragmentation, puis suivre une méthode de dépannage prudente.

**Niveau :** Débutant  
**Prérequis :** savoir ce qu’est une adresse IP, un routeur et un ping.  
**Durée indicative :** 30 à 45 minutes, exercices compris.

## Schéma SVG animé intégré au cours

Le schéma ci-dessous est **intégré directement dans ce fichier Markdown** : il ne dépend pas d’un lien vers un fichier image externe. Il illustre le paquet trop grand, le message ICMP de retour et le nouvel envoi adapté. L’animation SVG est prise en charge par les navigateurs et les visualiseurs qui autorisent l’élément SVG et ses animations.

<div align="center" class="schema-mtu-pmtud">
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1200" height="700" viewBox="0 0 1200 700" style="max-width:100%;height:auto" role="img" aria-labelledby="title desc">
  <title id="title">Schéma animé du dépannage MTU et PMTUD</title>
  <desc id="desc">Un gros paquet envoyé par le client est rejeté au niveau d'un lien dont la MTU vaut 1400 octets. Un message ICMP revient vers la source. La source réduit alors la taille du paquet et le nouvel envoi atteint le serveur.</desc>
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0b1220"/><stop offset="1" stop-color="#111827"/></linearGradient>
    <linearGradient id="green" x1="0" x2="1"><stop offset="0" stop-color="#34d399"/><stop offset="1" stop-color="#84cc16"/></linearGradient>
    <linearGradient id="red" x1="0" x2="1"><stop offset="0" stop-color="#fb7185"/><stop offset="1" stop-color="#ef4444"/></linearGradient>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="7" stdDeviation="8" flood-color="#000" flood-opacity=".25"/></filter>
    <marker id="arrowGreen" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#34d399"/></marker>
    <marker id="arrowRed" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#fb7185"/></marker>
    <marker id="arrowAmber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#fbbf24"/></marker>
    <style>
      text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e5e7eb}
      .title{font-size:27px;font-weight:800;letter-spacing:.2px}
      .sub{font-size:14px;fill:#a7b4c8}
      .nodeTitle{font-size:16px;font-weight:750}
      .nodeSub{font-size:12px;fill:#9ca3af}
      .stepTitle{font-size:16px;font-weight:800}
      .small{font-size:12px;fill:#cbd5e1}
      .tiny{font-size:11px;fill:#9ca3af}
      .node{fill:#172033;stroke:#35445e;stroke-width:1.4}
      .link{stroke:#64748b;stroke-width:3;stroke-linecap:round}
      .pulse{animation:pulse 1.6s ease-in-out infinite}
      .blink{animation:blink 1.05s steps(2,end) infinite}
      @keyframes pulse{0%,100%{opacity:.45}50%{opacity:1}}
      @keyframes blink{0%,100%{opacity:1}50%{opacity:.18}}
      @media (prefers-reduced-motion: reduce){.pulse,.blink{animation:none}}
    </style>
  </defs>
  <rect width="1200" height="700" rx="22" fill="url(#bg)"/>
  <circle cx="1080" cy="85" r="190" fill="#14532d" opacity=".12"/>
  <circle cx="110" cy="660" r="190" fill="#164e63" opacity=".13"/>
  <text x="48" y="52" class="title">MTU &amp; PMTUD — comprendre la panne</text>
  <text x="49" y="78" class="sub">Animation du trajet : paquet trop grand → retour ICMP → nouvel envoi adapté</text>

  <!-- Step indicators -->
  <g transform="translate(48 105)">
    <rect width="335" height="58" rx="12" fill="#3b1723" stroke="#7f1d1d"/>
    <circle cx="28" cy="29" r="15" fill="#ef4444"/><text x="28" y="34" text-anchor="middle" font-size="14" font-weight="800" fill="#fff">1</text>
    <text x="53" y="25" class="stepTitle">Paquet trop grand</text><text x="53" y="43" class="small">Le routeur ne peut pas le transmettre</text>
  </g>
  <g transform="translate(432 105)">
    <rect width="335" height="58" rx="12" fill="#382b12" stroke="#92400e"/>
    <circle cx="28" cy="29" r="15" fill="#f59e0b"/><text x="28" y="34" text-anchor="middle" font-size="14" font-weight="800" fill="#111827">2</text>
    <text x="53" y="25" class="stepTitle">Message ICMP de retour</text><text x="53" y="43" class="small">Il indique que le paquet est trop gros</text>
  </g>
  <g transform="translate(816 105)">
    <rect width="335" height="58" rx="12" fill="#123328" stroke="#166534"/>
    <circle cx="28" cy="29" r="15" fill="#22c55e"/><text x="28" y="34" text-anchor="middle" font-size="14" font-weight="800" fill="#052e16">3</text>
    <text x="53" y="25" class="stepTitle">Nouvel envoi plus petit</text><text x="53" y="43" class="small">La taille respecte la PMTU du trajet</text>
  </g>

  <!-- Topology links -->
  <path d="M166 265 H1038" class="link" opacity=".45"/>
  <path d="M170 265 H365" stroke="#fb7185" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrowRed)"/>
  <path d="M425 265 H658" stroke="#fb7185" stroke-width="3" stroke-dasharray="8 7" marker-end="url(#arrowRed)"/>
  <path d="M718 265 H1035" stroke="#64748b" stroke-width="2" stroke-dasharray="4 8" opacity=".35"/>

  <!-- Client -->
  <g filter="url(#shadow)">
    <rect x="48" y="212" width="128" height="106" rx="15" class="node"/>
    <rect x="82" y="232" width="59" height="37" rx="4" fill="#0f172a" stroke="#7dd3fc" stroke-width="2"/>
    <path d="M91 278 H132 M111 269 V278 M99 285 H123" stroke="#7dd3fc" stroke-width="2.5" stroke-linecap="round"/>
    <text x="112" y="301" class="nodeTitle" text-anchor="middle">Client</text>
  </g>
  <!-- Router 1 -->
  <g filter="url(#shadow)">
    <rect x="324" y="212" width="128" height="106" rx="15" class="node"/>
    <path d="M362 247 H414 M405 238 L414 247 L405 256 M414 267 H362 M371 258 L362 267 L371 276" fill="none" stroke="#93c5fd" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="388" y="301" class="nodeTitle" text-anchor="middle">Routeur A</text>
  </g>
  <!-- Bottleneck router -->
  <g filter="url(#shadow)">
    <rect x="616" y="200" width="136" height="130" rx="15" fill="#351b24" stroke="#fb7185" stroke-width="2.2"/>
    <path d="M654 244 H713 M704 235 L713 244 L704 253 M713 266 H654 M663 257 L654 266 L663 275" fill="none" stroke="#fda4af" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
    <text x="684" y="294" class="nodeTitle" text-anchor="middle">Routeur B</text>
    <rect x="630" y="302" width="108" height="20" rx="10" fill="#7f1d1d"/><text x="684" y="316" text-anchor="middle" font-size="11" font-weight="800" fill="#ffe4e6">MTU 1400</text>
  </g>
  <!-- Server -->
  <g filter="url(#shadow)">
    <rect x="1024" y="212" width="128" height="106" rx="15" class="node"/>
    <rect x="1059" y="229" width="59" height="17" rx="3" fill="#0f172a" stroke="#86efac" stroke-width="1.8"/>
    <rect x="1059" y="250" width="59" height="17" rx="3" fill="#0f172a" stroke="#86efac" stroke-width="1.8"/>
    <circle cx="1067" cy="237" r="2" fill="#4ade80"/><circle cx="1067" cy="258" r="2" fill="#4ade80"/>
    <text x="1088" y="301" class="nodeTitle" text-anchor="middle">Serveur</text>
  </g>

  <!-- Oversized packet movement -->
  <g>
    <rect x="145" y="191" width="116" height="28" rx="7" fill="url(#red)" stroke="#fecdd3" stroke-width="1"/>
    <text x="203" y="209" font-size="11" font-weight="800" text-anchor="middle" fill="#450a0a">1500 octets</text>
    <animateMotion dur="3.2s" begin="0s" fill="freeze" path="M 0,0 L 480,0"/>
  </g>
  <g class="blink">
    <path d="M672 183 L696 207 M696 183 L672 207" stroke="#fb7185" stroke-width="5" stroke-linecap="round"/>
    <text x="684" y="177" text-anchor="middle" font-size="12" font-weight="800" fill="#fda4af">REJETÉ</text>
  </g>
  <text x="480" y="193" class="tiny" text-anchor="middle">Paquet IPv4 avec DF = 1</text>

  <!-- ICMP return lane -->
  <path d="M682 365 H122" stroke="#fbbf24" stroke-width="2.6" stroke-dasharray="7 7" marker-end="url(#arrowAmber)"/>
  <text x="400" y="352" class="small" text-anchor="middle" fill="#fcd34d">ICMP « fragmentation nécessaire » (IPv4)</text>
  <text x="400" y="380" class="tiny" text-anchor="middle">Le routeur signale la contrainte à l’émetteur</text>
  <circle r="8" fill="#fbbf24" stroke="#fff7ed" stroke-width="2">
    <animateMotion dur="3.8s" begin="0s" repeatCount="indefinite" path="M 682,365 L 122,365"/>
  </circle>

  <!-- Successful smaller packet lane -->
  <rect x="48" y="430" width="1104" height="83" rx="14" fill="#0f2d27" stroke="#166534" stroke-width="1.3" opacity=".72"/>
  <path d="M168 470 H1038" stroke="#34d399" stroke-width="3" marker-end="url(#arrowGreen)" opacity=".7"/>
  <text x="70" y="453" font-size="13" font-weight="800" fill="#86efac">APRÈS AJUSTEMENT</text>
  <text x="70" y="491" font-size="12" fill="#bbf7d0">Paquet ≤ 1400 octets</text>
  <circle r="8" fill="#4ade80" stroke="#dcfce7" stroke-width="2">
    <animateMotion dur="4.6s" begin="0.4s" repeatCount="indefinite" path="M 170,470 L 1035,470"/>
  </circle>
  <circle cx="684" cy="470" r="15" fill="none" stroke="#4ade80" stroke-width="2" class="pulse"/>
  <text x="684" y="500" class="tiny" text-anchor="middle" fill="#bbf7d0">Le paquet traverse le lien limitant</text>
  <text x="1081" y="491" font-size="12" font-weight="800" text-anchor="middle" fill="#bbf7d0">LIVRÉ ✓</text>

  <!-- Rule cards -->
  <g transform="translate(48 540)">
    <rect width="350" height="104" rx="13" fill="#172033" stroke="#35445e"/>
    <text x="18" y="27" font-size="14" font-weight="800" fill="#93c5fd">MTU</text>
    <text x="18" y="49" class="small">Taille maximale d’un paquet IP</text><text x="18" y="67" class="small">sur un lien donné.</text>
    <text x="18" y="88" font-size="12" font-weight="700" fill="#c4b5fd">Exemple courant Ethernet : 1500 octets</text>
  </g>
  <g transform="translate(425 540)">
    <rect width="350" height="104" rx="13" fill="#172033" stroke="#35445e"/>
    <text x="18" y="27" font-size="14" font-weight="800" fill="#fcd34d">PMTU</text>
    <text x="18" y="49" class="small">Plus petite MTU rencontrée</text><text x="18" y="67" class="small">sur le trajet complet.</text>
    <text x="18" y="88" font-size="12" font-weight="700" fill="#fcd34d">Ici : 1400 octets</text>
  </g>
  <g transform="translate(802 540)">
    <rect width="350" height="104" rx="13" fill="#172033" stroke="#35445e"/>
    <text x="18" y="27" font-size="14" font-weight="800" fill="#86efac">PMTUD</text>
    <text x="18" y="49" class="small">Méthode qui découvre/estime la PMTU</text><text x="18" y="67" class="small">et adapte la taille des paquets.</text>
    <text x="18" y="88" font-size="12" font-weight="700" fill="#86efac">ICMP doit pouvoir signaler le blocage</text>
  </g>
  <text x="600" y="675" text-anchor="middle" class="tiny">Illustration pédagogique — les valeurs 1500 et 1400 sont des exemples, pas une mesure réelle de votre réseau.</text>
</svg>
</div>

> **Note de compatibilité :** certains visualiseurs Markdown, notamment ceux qui nettoient le HTML pour des raisons de sécurité, peuvent bloquer les SVG intégrés ou leurs animations. Si le schéma ne s’anime pas dans l’aperçu, ouvre le fichier Markdown dans un éditeur qui prend en charge le SVG intégré, ou ouvre la copie autonome `schema-mtu-pmtud-anime.svg` dans Chrome ou Edge.


## 1. Les objectifs d’apprentissage

À la fin de cette leçon, tu dois pouvoir :

- définir **MTU**, **PMTU** et **PMTUD** avec tes propres mots ;
- expliquer pourquoi un paquet IP peut être accepté au départ puis bloqué plus loin ;
- distinguer le comportement d’IPv4 de celui d’IPv6 en matière de fragmentation ;
- effectuer un test de taille sous Windows ou Linux ;
- interpréter les résultats sans confondre un problème MTU avec un simple ping bloqué ;
- appliquer une procédure de dépannage sans modifier aveuglément la configuration du réseau.

## 2. Comprendre les trois notions essentielles

### 2.1 MTU — Maximum Transmission Unit

La **MTU** (unité maximale de transmission) désigne la taille maximale d’un paquet de couche réseau qui peut être transporté en une seule fois sur un lien donné. Elle s’exprime généralement en **octets**.

Sur un réseau Ethernet classique, une MTU IPv4/IPv6 de **1500 octets** est courante. Ce n’est toutefois pas une valeur universelle : un tunnel VPN, PPPoE, un réseau mobile ou un autre encapsulage peut réduire la taille utilisable.

**Analogie :** imagine que chaque route impose une largeur maximale aux camions. Un camion qui passe sur la première route peut être trop gros pour un pont rencontré plus loin.

### 2.2 PMTU — Path MTU

La **PMTU** est la plus petite MTU parmi les liens du trajet entre la source et la destination. Elle dépend donc du chemin réellement suivi, et peut différer selon la destination ou le trajet réseau.

**Exemple :**

| Segment du trajet | MTU de l’exemple |
|---|---:|
| Ordinateur → routeur local | 1500 octets |
| Routeur → tunnel VPN | 1450 octets |
| Tunnel → réseau distant | 1400 octets |
| Réseau distant → serveur | 1500 octets |
| **PMTU du trajet** | **1400 octets** |

La PMTU n’est pas forcément égale à la MTU affichée sur ta carte réseau. Ta carte peut autoriser 1500 octets alors que le trajet complet n’en accepte que 1400.

### 2.3 PMTUD — Path MTU Discovery

Le **PMTUD** est un mécanisme par lequel l’émetteur découvre ou estime la PMTU afin d’envoyer des paquets suffisamment petits pour traverser le trajet.

Dans le mécanisme classique :

1. la machine émettrice envoie un paquet ;
2. un routeur situé plus loin constate que le paquet dépasse la MTU du prochain lien ;
3. le routeur ne peut pas le transmettre tel quel et renvoie un message ICMP indiquant le problème ;
4. l’émetteur ajuste son estimation et envoie des paquets plus petits.

Pour IPv4, le cas classique utilise le bit **DF** (*Don't Fragment*, « ne pas fragmenter »). Pour IPv6, les routeurs intermédiaires ne fragmentent pas les paquets : l’émetteur doit adapter la taille ou, si nécessaire, gérer la fragmentation à la source. Les mécanismes sont décrits dans les RFC 1191 pour IPv4 et RFC 8201 pour IPv6.

## 3. Lire le schéma animé

Le SVG montre un exemple pédagogique avec une MTU locale de 1500 octets et un lien limitant à 1400 octets.

**Étape 1 — Paquet trop grand.** Le client envoie un paquet IPv4 de 1500 octets avec DF activé. Le routeur B ne peut pas le faire passer sur son lien de MTU 1400 ; le paquet est abandonné.

**Étape 2 — Retour du message ICMP.** Le routeur doit signaler à l’émetteur que la fragmentation est nécessaire ou que le paquet doit être réduit. En IPv4, le message classique est ICMP Destination Unreachable, type 3, code 4 (« fragmentation needed »). En IPv6, il s’agit d’ICMPv6 *Packet Too Big*, type 2.

**Étape 3 — Envoi adapté.** L’émetteur ajuste la taille et réessaie avec un paquet qui respecte la PMTU. Dans cet exemple, le paquet IP doit être inférieur ou égal à 1400 octets.

**Le point important :** le routeur limitant n’envoie pas automatiquement un nouveau paquet plus petit à la place de la source. Le mécanisme de découverte sert à informer l’émetteur, qui adapte ensuite ses envois.

## 4. Pourquoi un problème MTU peut être difficile à repérer

Un problème MTU/PMTUD ne provoque pas nécessairement une coupure totale.

Signes possibles :

- certains sites ou applications se chargent, tandis que d’autres restent bloqués ;
- la connexion s’établit, mais le transfert de données se fige ensuite ;
- les petites requêtes passent, mais certains transferts volumineux échouent ;
- une connexion fonctionne sans VPN, mais devient instable avec le VPN ;
- les problèmes sont intermittents parce que le chemin réseau change.

Ces signes sont **des indices, pas une preuve**. Un serveur peut filtrer ICMP, une règle de pare-feu peut bloquer le trafic, un DNS peut échouer ou un service distant peut être indisponible. Il faut comparer plusieurs tests.

### Le « PMTUD black hole »

On parle de trou noir PMTUD (*PMTUD black hole*) lorsqu’un paquet trop grand est abandonné et que le message ICMP qui devrait prévenir l’émetteur n’arrive pas jusqu’à lui. L’émetteur continue alors à tenter d’envoyer des paquets trop grands. Une connexion TCP peut commencer correctement puis se bloquer lors du transfert de données. Le RFC 8201 décrit notamment ce risque lorsque les messages ICMPv6 *Packet Too Big* sont bloqués.

**Erreur à éviter :** ne bloque pas indistinctement tous les messages ICMP/ICMPv6 sur un pare-feu. Certains messages sont nécessaires au bon fonctionnement du réseau et à la découverte de PMTU.

## 5. IPv4 et IPv6 : ce qui change

| Point | IPv4 | IPv6 |
|---|---|---|
| Fragmentation par un routeur intermédiaire | Possible dans certains cas si DF n’est pas activé | Les routeurs intermédiaires ne fragmentent pas les paquets |
| Découverte classique de PMTU | DF activé ; ICMP « fragmentation needed » si le paquet doit être réduit | ICMPv6 *Packet Too Big* |
| Si le message ICMP utile est bloqué | La découverte peut échouer | La découverte peut échouer et bloquer certains transferts |
| En-tête IP de base | 20 octets, sans options | 40 octets |

La taille exacte d’un paquet peut aussi comprendre des en-têtes supplémentaires (options IPv4, extensions IPv6, encapsulation VPN, etc.). Les calculs simplifiés ci-dessous supposent des en-têtes IPv4 et ICMP classiques.

## 6. Travaux pratiques — tester la taille d’un paquet

### Avant de commencer

- Choisis une destination que tu as le droit de tester.
- Utilise une destination qui répond normalement aux pings ; certains serveurs ne répondent pas à ICMP.
- Note si tu es connecté directement, via PPPoE ou via un VPN.
- Ne modifie pas encore la MTU de l’interface.

### 6.1 Test sous Windows (IPv4)

Ouvre **Invite de commandes** (`cmd`) et exécute :

```bat
ping /4 /f /l 1472 1.1.1.1
```

Remplace `1.1.1.1` par une destination de test appropriée si nécessaire.

- `/4` force IPv4.
- `/f` demande le bit « Ne pas fragmenter » (DF).
- `/l 1472` fixe la taille du champ de données ICMP à 1472 octets.

Pourquoi 1472 ? Pour un paquet IPv4 classique sans options, on ajoute 20 octets d’en-tête IPv4 et 8 octets d’en-tête ICMP :

```text
1472 octets de données ICMP
+  8 octets d’en-tête ICMP
+ 20 octets d’en-tête IPv4
= 1500 octets pour le paquet IP
```

**Interprétation prudente :**

- Si la réponse indique que le paquet doit être fragmenté, la taille testée est trop grande pour ce trajet (ou pour une contrainte liée au chemin).
- Si le ping réussit, ce paquet de test a traversé le trajet ; cela ne prouve pas que toutes les applications ou tous les chemins ont la même PMTU.
- Si le ping expire, le résultat est **inconclusif** : la destination ou un équipement intermédiaire peut filtrer les pings.

Si 1472 est trop grand, essaie une valeur plus basse, par exemple :

```bat
ping /4 /f /l 1400 1.1.1.1
ping /4 /f /l 1372 1.1.1.1
```

Réduis ou augmente la valeur par étapes pour rechercher la taille maximale qui passe. Fais des essais dans un nombre raisonnable de valeurs et note chaque résultat.

### 6.2 Relier la taille des données à la MTU

Avec IPv4 sans options et ICMP standard :

**Taille du paquet IP = données ICMP + 28 octets.**

| Taille du paquet IP visée | Données à tester avec `ping /l` |
|---:|---:|
| 1500 octets | 1472 octets |
| 1450 octets | 1422 octets |
| 1400 octets | 1372 octets |
| 1300 octets | 1272 octets |

Ce calcul ne s’applique pas tel quel à IPv6, ni à une application utilisant d’autres en-têtes ou une encapsulation. Le test concerne une destination et un chemin précis.

### 6.3 Vérifier la MTU locale sous Windows

Dans PowerShell, exécute :

```powershell
Get-NetIPInterface | Format-Table InterfaceAlias,AddressFamily,NlMtu
```

Ou dans `cmd` :

```bat
netsh interface ipv4 show subinterfaces
```

Ces commandes affichent la MTU configurée sur les interfaces. **Elles n’affichent pas forcément la PMTU de chaque destination** : la PMTU concerne un trajet, pas seulement l’interface locale.

### 6.4 Tests sous Linux

Pour afficher les interfaces et leur MTU :

```bash
ip link show
```

Pour tenter un ping IPv4 de 1500 octets au total, avec les outils `iputils` :

```bash
ping -4 -M do -s 1472 -c 4 1.1.1.1
```

- `-4` force IPv4.
- `-M do` demande de ne pas fragmenter et de signaler une taille qui ne convient pas (syntaxe de `iputils`).
- `-s 1472` fixe la taille des données ICMP.
- `-c 4` envoie quatre requêtes.

Si la commande `tracepath` est installée, elle peut aider à explorer la PMTU :

```bash
tracepath -n 1.1.1.1
```

Les options disponibles varient selon le système et la version des outils. Sur macOS ou d’autres systèmes, vérifie `man ping` ou `ping --help` plutôt que de supposer que les mêmes options fonctionnent.

## 7. Procédure de dépannage : de la vérification à la correction

### Étape A — Définir précisément le problème

1. Note la destination, l’application et l’heure du problème.
2. Compare le fonctionnement sur le réseau habituel et, si pertinent, avec/sans VPN.
3. Vérifie si le problème touche toutes les destinations ou une seule.
4. Confirme que l’adresse IP et la résolution DNS sont correctes.

### Étape B — Tester sans tirer de conclusion trop vite

1. Lance un ping ordinaire vers la destination, si celle-ci répond à ICMP.
2. Effectue un test avec DF et une grande taille IPv4, comme décrit plus haut.
3. Réduis progressivement la taille si le paquet est trop grand.
4. Recommence avec une seconde destination fiable quand c’est possible.
5. Compare les résultats avec et sans tunnel VPN, si tu en utilises un.

**Important :** un simple ping réussi ne garantit pas que les paquets de toutes les tailles passent. Un ping échoué ne suffit pas non plus à conclure à un problème MTU.

### Étape C — Localiser la contrainte

Examine en priorité les endroits où la taille des paquets peut diminuer :

- tunnel VPN (WireGuard, IPsec ou autre) ;
- accès PPPoE ;
- encapsulation réseau ou overlay ;
- lien WAN, routeur ou pare-feu intermédiaire ;
- changement de chemin ou de fournisseur d’accès.

Lorsque les équipements sont administrables, recherche les compteurs, journaux ou captures qui montrent les paquets rejetés et les messages ICMP correspondants. Une capture côté client et une autre côté routeur peuvent aider à localiser où le message se perd.

### Étape D — Corriger à la bonne place

Selon ce que les tests démontrent, les corrections possibles sont :

1. **Autoriser les messages ICMP requis** dans les pare-feu et équipements de sécurité, avec des règles adaptées au contexte. Pour PMTUD classique : ICMPv4 « fragmentation needed » et ICMPv6 *Packet Too Big*.
2. **Vérifier la MTU du tunnel ou de l’interface WAN** dans la documentation de l’équipement et la comparer à la réalité du chemin.
3. **Ajuster la MTU** de l’interface concernée seulement si les mesures justifient cette modification. Note la valeur d’origine et prévois un retour arrière.
4. **Envisager le MSS clamping** pour certains flux TCP si le routeur/VPN le justifie. Cette technique ajuste la taille maximale des segments TCP ; ce n’est pas une correction universelle pour UDP, QUIC ou tous les trafics IP.
5. Retester les applications réellement affectées, pas seulement le ping.

Évite de modifier au hasard la MTU de toutes les interfaces, de désactiver les protections du pare-feu ou de bloquer ICMP en bloc. Sur un réseau professionnel, valide les changements avec l’administrateur réseau et applique-les d’abord dans un périmètre contrôlé.

## 8. Exemple guidé : un VPN dont le trajet limite les paquets à 1400 octets

**Situation :** la carte Ethernet affiche MTU 1500. Sans VPN, un transfert fonctionne. Avec VPN, la session s’ouvre, mais le chargement d’un gros fichier se bloque.

**Hypothèse à tester :** l’encapsulation du VPN réduit la taille disponible sur le chemin et les messages nécessaires à PMTUD ne sont peut-être pas correctement transmis.

**Démarche :**

1. Comparer les tests avec et sans VPN vers des destinations qui répondent aux pings.
2. Sous IPv4, tester une taille de données ICMP de 1472 octets, puis de 1372 octets avec DF activé.
3. Si 1472 échoue à cause d’une fragmentation nécessaire, tandis que 1372 passe de façon reproductible, une taille de paquet IP proche de 1400 octets devient une piste plausible pour ce trajet.
4. Vérifier la MTU réelle du tunnel, les messages ICMP et la configuration du pare-feu/VPN.
5. Corriger le réglage à l’origine du problème, puis vérifier le transfert du fichier et les autres applications.

**Conclusion :** ces résultats suggèrent une contrainte de taille mais ne suffisent pas, à eux seuls, à localiser le lien fautif ou à prouver que la PMTU est exactement 1400 octets. Il faut corroborer avec les équipements et des tests reproductibles.

## 9. Erreurs fréquentes à éviter

- **« La MTU de mon PC est 1500, donc la PMTU est 1500. »** Faux : un lien plus loin peut avoir une MTU inférieure.
- **« Le ping expire, donc la MTU est trop grande. »** Faux : ICMP peut être filtré ou la destination peut ne pas répondre.
- **« Je vais bloquer ICMP pour être plus sécurisé. »** Dangereux pour certains mécanismes réseau : autorise les messages requis de façon contrôlée.
- **« IPv6 se fragmente comme IPv4 par les routeurs. »** Faux : les routeurs IPv6 intermédiaires ne fragmentent pas les paquets.
- **« Il faut toujours fixer la MTU à 1400. »** Faux : 1400 n’est qu’un exemple ; il faut mesurer et vérifier le contexte.
- **« Le MSS clamping résout tous les protocoles. »** Faux : il concerne TCP, pas tous les paquets IP ni les flux UDP/QUIC.

## 10. Mini-quiz de validation

**Question 1.** Que représente la PMTU ?  
A. La MTU maximale de l’ordinateur  
B. La plus petite MTU d’un lien sur le trajet jusqu’à la destination  
C. La vitesse du réseau

**Question 2.** Pourquoi le message ICMP est-il important pour le PMTUD classique ?  
A. Il informe l’émetteur qu’un paquet est trop grand ou doit être réduit  
B. Il donne une nouvelle adresse IP au client  
C. Il remplace le routeur

**Question 3.** Sous Windows, que fait `/f` dans une commande `ping` IPv4 ?  
A. Force le DNS  
B. Demande que le paquet ne soit pas fragmenté  
C. Change la MTU de l’interface

**Question 4.** Un ping ne reçoit aucune réponse. Que peut-on conclure ?  
A. La PMTU est forcément incorrecte  
B. Le réseau est forcément hors service  
C. Rien de définitif : le ping peut être filtré ou la destination peut ne pas répondre

**Question 5.** Les routeurs intermédiaires fragmentent-ils les paquets IPv6 ?  
A. Oui, toujours  
B. Non, ils ne fragmentent pas les paquets IPv6 en transit  
C. Uniquement si le MTU vaut 1500

### Corrigé

1. **B** — la PMTU correspond à la plus petite MTU du trajet.  
2. **A** — l’émetteur a besoin de connaître la contrainte pour réduire ses paquets.  
3. **B** — `/f` demande le réglage DF pour un test IPv4.  
4. **C** — un ping absent n’identifie pas à lui seul la cause.  
5. **B** — la fragmentation IPv6, si nécessaire, est gérée par la source et non par les routeurs intermédiaires.

## 11. Fiche mémo

- **MTU** : taille maximale d’un paquet IP sur un lien.
- **PMTU** : plus petite MTU du trajet complet.
- **PMTUD** : découverte/estimation de la PMTU par l’émetteur.
- **IPv4** : le test classique emploie DF ; un routeur qui ne peut pas transmettre le paquet doit signaler la nécessité de fragmentation/réduction.
- **IPv6** : les routeurs intermédiaires ne fragmentent pas ; ICMPv6 *Packet Too Big* est essentiel au PMTUD classique.
- **Test Windows IPv4** : `ping /4 /f /l 1472 <destination>` pour viser un paquet IP d’environ 1500 octets, avec les en-têtes classiques.
- **Ne pas confondre** : MTU locale et PMTU de bout en bout.
- **Bon réflexe** : tester, comparer, observer les messages ICMP, corriger la cause et vérifier les applications concernées.

## 12. Références techniques

- IETF / RFC Editor, **RFC 1191 — Path MTU Discovery** (IPv4) : <https://www.rfc-editor.org/rfc/rfc1191.html>
- IETF / RFC Editor, **RFC 8201 — Path MTU Discovery for IP version 6** (IPv6) : <https://www.rfc-editor.org/rfc/rfc8201.html>
- Microsoft Learn, **Commande ping** (options Windows `/f` et `/l`) : <https://learn.microsoft.com/fr-fr/windows-server/administration/windows-commands/ping>
- IETF / RFC Editor, **RFC 8900 — IP Fragmentation Considered Fragile** : <https://www.rfc-editor.org/rfc/rfc8900.html>


**Fin du cours — Dépannage MTU et PMTUD, niveau débutant.**
