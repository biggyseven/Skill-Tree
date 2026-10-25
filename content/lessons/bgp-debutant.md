# BGP — Niveau Débutant

**Durée indicative :** 5 à 7 heures, avec les laboratoires  
**Prérequis :** adressage IPv4, sous-réseaux, table de routage, route statique, notions de routeur et d’AS. La connaissance d’OSPF ou d’un IGP est utile, mais le cours explique les liens nécessaires.  
**Environnement recommandé :** Packet Tracer si les fonctions BGP de l’image sont suffisantes, ou une maquette Cisco IOS/IOS XE, FRRouting ou autre environnement documenté ; Wireshark est facultatif.

Ce document est le premier niveau de la série BGP. Il construit les fondations nécessaires aux futurs cours `bgp-intermediaire.md` et `bgp-expert.md`. L’objectif est de comprendre ce que BGP échange, comment les sessions se forment, comment le chemin AS_PATH est interprété, pourquoi les politiques sont indispensables, et comment vérifier une route de bout en bout. Le niveau Intermédiaire pourra ensuite approfondir les politiques complexes, iBGP à grande échelle, route reflectors, communautés, agrégation et ingénierie de trafic ; le niveau Expert traitera les architectures multi-fournisseurs, la résilience, l’automatisation, la sécurité du routage et les incidents complexes.

> **Conventions des exemples :** les AS `65010`, `65020` et `65030` appartiennent à la plage ASN privée 16 bits ; les préfixes `192.0.2.0/24`, `198.51.100.0/24` et `203.0.113.0/24` sont réservés à la documentation. Remplace-les uniquement dans un laboratoire par les paramètres de ton environnement. Une configuration BGP ne doit jamais être appliquée à un réseau public ou de production sans politiques validées, filtre de préfixes, plan de retour arrière et revue par l’équipe réseau.

## Objectifs pédagogiques

À la fin du cours, tu dois pouvoir :

- expliquer ce qu’est un système autonome (AS) et distinguer eBGP d’iBGP ;
- décrire BGP comme un protocole de routage à vecteur de chemins (*path vector*) ;
- comprendre la session TCP, les états BGP et les messages principaux ;
- lire le rôle d’AS_PATH, NEXT_HOP, LOCAL_PREF, MED et des communautés à un niveau introductif ;
- expliquer pourquoi BGP applique une politique avant d’accepter ou d’annoncer des routes ;
- configurer une session eBGP simple dans une maquette à deux routeurs ;
- annoncer un préfixe en vérifiant qu’il existe bien dans la table de routage locale ;
- examiner les routes reçues, la route retenue et les annonces envoyées ;
- diagnostiquer les pannes de base sans confondre session établie et connectivité de bout en bout.

## Comment utiliser ce cours

Lis les schémas dans l’ordre. Chaque SVG est directement intégré dans ce fichier Markdown ; aucun dossier d’images externe n’est nécessaire. Les marqueurs animés représentent des exemples de chemin ou d’échange, pas le minutage réel des messages BGP. Certains lecteurs Markdown peuvent désactiver les animations SVG ; dans ce cas, les labels et les diagrammes restent lisibles sans animation.

Pour chaque laboratoire, relève d’abord l’état initial, configure un seul élément à la fois, vérifie le résultat dans la session BGP et la table de routage, puis teste la connectivité jusqu’à la destination. En BGP, `Established` est nécessaire pour échanger des routes, mais ne garantit ni que le préfixe existe, ni qu’il soit accepté, sélectionné, installé ou utilisable par le plan de transfert.


## 1. À quoi sert BGP ?

### 1.1. Routage interne et routage entre systèmes autonomes

Un réseau d’entreprise ou de fournisseur peut employer un protocole de passerelle intérieure (*IGP*, par exemple OSPF ou IS-IS) pour connaître les chemins au sein d’un domaine administratif. BGP est le protocole de passerelle extérieure (*EGP*) utilisé pour échanger de l’information de joignabilité entre systèmes autonomes. Dans de nombreux réseaux, BGP est aussi utilisé à l’intérieur d’un AS pour distribuer des routes externes selon la politique de l’organisation.

Un **système autonome** (*Autonomous System*, AS) est un ensemble de réseaux et de routeurs exploité selon une politique de routage commune. Sur Internet, chaque AS public pertinent possède un numéro d’AS (ASN). Les ASN privés sont utiles dans les laboratoires et certains réseaux privés, mais doivent être gérés conformément au contexte d’interconnexion.

La différence fondamentale n’est pas simplement que BGP est « plus grand » qu’OSPF. OSPF décrit la topologie d’une aire et calcule les chemins selon les coûts des liens ; BGP échange des préfixes et des attributs qui permettent à l’administrateur de mettre en œuvre une politique entre domaines. BGP peut donc préférer une route qui n’est pas géographiquement la plus courte, parce que les politiques commerciales, la préférence locale ou les règles d’ingénierie de trafic dominent.

| Question | IGP (ex. OSPF) | BGP |
|---|---|---|
| Usage fréquent | Chemins au sein d’un domaine | Échange de préfixes entre AS, distribution de routes externes en interne |
| Information principale | Topologie de liens et métriques | Préfixes et attributs de chemin/politique |
| Décision typique | Coût du chemin selon l’algorithme du protocole | Politique et attributs BGP, puis résolution du prochain saut |
| Session | Dépend du protocole IGP | Session TCP, généralement port 179 |
| Portée des annonces | Aire/domaine IGP selon le protocole | Selon voisins et politiques d’import/export |

### 1.2. BGP est un protocole à vecteur de chemins

BGP annonce des préfixes IP avec des attributs. L’un des plus connus est **AS_PATH**, une séquence d’AS qui permet au routeur de voir par quels domaines une route a été annoncée. La présence de son propre ASN dans l’AS_PATH conduit normalement un routeur eBGP à rejeter la route afin de prévenir certaines boucles inter-AS.

BGP n’envoie pas la carte complète de tous les liens physiques d’Internet. Il annonce des informations de joignabilité : par exemple « je peux atteindre `198.51.100.0/24` ». Le routeur applique ensuite sa politique, compare les chemins candidats, sélectionne des routes et tente de les installer dans la table de routage. Cette distinction entre **route annoncée**, **route acceptée**, **meilleur chemin**, **route installée** et **paquet effectivement transféré** est fondamentale.

### Schéma 1 — Échange de préfixes entre deux AS

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="BGP : échanger des préfixes entre systèmes autonomes" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">BGP : échanger des préfixes entre systèmes autonomes</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">eBGP relie des AS distincts ; les flèches de contrôle montrent les annonces, pas les paquets utilisateurs.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="55" y="170" width="235" height="115" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="172.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Routeur A</text>
<text x="172.5" y="220" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">AS 65010 · eBGP voisin</text>
<rect x="670" y="170" width="235" height="115" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="787.5" y="197" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Routeur B</text>
<text x="787.5" y="220" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">AS 65020 · eBGP voisin</text>
<path d="M 290 220 L 670 220" fill="none" stroke="#45c7f5" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<text x="480" y="198" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Session TCP port 179</text>
<text x="480" y="245" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">203.0.113.1/30  ↔  203.0.113.2/30</text>
<rect x="70" y="330" width="250" height="72" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="195.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">LAN A</text>
<text x="195.0" y="380" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">192.0.2.0/24</text>
<rect x="640" y="330" width="250" height="72" rx="12" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="765.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">LAN B</text>
<text x="765.0" y="380" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">198.51.100.0/24</text>
<path d="M 172 330 L 172 302 L 170 285" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 765 330 L 765 302 L 785 285" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="6" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 290 220 L 670 220" dur="3.2s" begin="0s" repeatCount="indefinite"/></circle>
<text x="480" y="437" text-anchor="middle" fill="#adbdcf" font-size="13" font-weight="400">A annonce son préfixe BGP ; B le sélectionne si la politique et les attributs le permettent.</text>
</svg>
</div>

Dans le schéma, les routeurs disposent d’une session eBGP via un réseau de transit. Les LAN sont les préfixes d’exemple que chaque côté souhaite annoncer. L’animation souligne le lien de contrôle BGP ; elle ne signifie pas que les paquets de données empruntent forcément un unique trajet sans autre vérification.

### 1.3. Qu’est-ce que BGP n’est pas ?

BGP n’est pas un mécanisme de chiffrement du trafic utilisateur. BGP ne valide pas automatiquement la propriété d’un préfixe simplement parce qu’un voisin l’annonce. Il ne remplace pas les routes connectées ni l’IGP nécessaire pour atteindre certains prochains sauts. Il ne choisit pas non plus systématiquement la route « la plus rapide » : il suit un processus de sélection et une politique locale.

Une route BGP peut être présente dans la base BGP mais absente de la table de routage générale si son prochain saut est impossible à résoudre, si une autre source de routage a été préférée ou si la route est inéligible. À l’inverse, une route présente dans la table ne garantit pas qu’un pare-feu ou un service distant accepte le trafic.


## 2. AS, ASN, eBGP et iBGP

### 2.1. ASN : identifier le domaine de routage

Le numéro d’AS apparaît dans les sessions eBGP et dans l’AS_PATH. Les exemples utilisent des ASN privés `65010`, `65020` et `65030`. La plage privée classique à 16 bits est `64512–65534`; les plages privées 32 bits sont aussi définies par les standards. L’utilisation réelle doit être vérifiée selon la forme de l’ASN, les systèmes et la politique d’interconnexion.

Le numéro configuré dans la commande `router bgp` identifie généralement l’AS local du processus BGP. Le numéro déclaré dans `neighbor ... remote-as` décrit l’AS attendu du voisin eBGP ou iBGP. Une incohérence est une cause fréquente d’échec de session.

### 2.2. eBGP : entre AS différents

Une session **eBGP** connecte deux routeurs appartenant à des AS distincts. Elle est utilisée, par exemple, entre un client et son fournisseur, entre deux fournisseurs, ou entre un réseau d’entreprise et un routeur de peering. Les politiques d’importation et d’exportation déterminent quelles routes sont reçues, retenues et annoncées.

Dans une configuration eBGP directement connectée, les adresses des voisins doivent généralement être joignables sur le lien ou via la configuration de voisinage prévue. Les scénarios avec loopbacks et `ebgp-multihop` demandent des précautions supplémentaires et seront étudiés plus tard. Au niveau débutant, commence par un lien directement connecté afin d’isoler les variables.

### 2.3. iBGP : au sein du même AS

Une session **iBGP** relie des routeurs qui appartiennent au même AS. Elle peut distribuer les routes externes à travers le réseau interne. Les règles iBGP ne sont pas identiques à celles d’eBGP : en particulier, une route apprise d’un voisin iBGP n’est pas normalement réannoncée à un autre voisin iBGP ordinaire. Les grands réseaux utilisent des architectures comme les route reflectors ou les confédérations pour gérer cette contrainte. Ces mécanismes appartiennent aux niveaux suivants.

### Schéma 2 — Distinguer eBGP et iBGP

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 470" role="img" aria-label="eBGP et iBGP : la frontière des AS change le type de session" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="470" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">eBGP et iBGP : la frontière des AS change le type de session</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Les sessions eBGP traversent une frontière AS ; les sessions iBGP relient des routeurs au sein du même AS.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="112" width="420" height="255" rx="16" fill="#101f30" stroke="#45c7f5" stroke-width="2"/>
<text x="255" y="139" text-anchor="middle" fill="#45c7f5" font-size="16" font-weight="700">AS 65010</text>
<rect x="505" y="112" width="410" height="255" rx="16" fill="#201b35" stroke="#c4b5fd" stroke-width="2"/>
<text x="710" y="139" text-anchor="middle" fill="#c4b5fd" font-size="16" font-weight="700">AS 65020</text>
<rect x="85" y="190" width="145" height="75" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="157.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R1</text>
<text x="157.5" y="240" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Edge</text>
<rect x="300" y="190" width="125" height="75" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="362.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R2</text>
<text x="362.5" y="240" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Interne</text>
<rect x="565" y="190" width="145" height="75" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="637.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R3</text>
<text x="637.5" y="240" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Edge</text>
<rect x="770" y="190" width="125" height="75" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="832.5" y="217" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">R4</text>
<text x="832.5" y="240" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Interne</text>
<path d="M 230 227 L 300 227" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="265" y="211" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">iBGP</text>
<path d="M 425 227 L 565 227" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="495" y="211" text-anchor="middle" fill="#fbbf24" font-size="12" font-weight="700">eBGP</text>
<path d="M 710 227 L 770 227" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="740" y="211" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">iBGP</text>
<circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 425 227 L 565 227" dur="2.7s" begin="0s" repeatCount="indefinite"/></circle>
<text x="480" y="415" text-anchor="middle" fill="#adbdcf" font-size="13" font-weight="400">Les politiques d’export/import décident quels préfixes sont acceptés et annoncés.</text>
</svg>
</div>

Le schéma distingue les frontières d’AS. Les liens marqués iBGP restent à l’intérieur d’un même domaine ; le lien eBGP traverse la frontière entre AS. Une ligne représente une relation de session dans l’exemple, pas nécessairement un câble direct dans toutes les architectures réelles.

### 2.4. Le rôle d’un IGP à côté de BGP

Dans un réseau à plusieurs routeurs, l’IGP peut transporter les routes d’infrastructure : loopbacks, liens internes et prochains sauts nécessaires. BGP décide quelles destinations et quelles politiques annoncer, mais le **NEXT_HOP** d’une route doit pouvoir être atteint par le plan de routage. Si ce prochain saut est inaccessible, la route BGP peut ne pas être utilisable.

Ne confonds pas la route vers un préfixe utilisateur et la route permettant d’atteindre le prochain saut BGP. Le diagnostic vérifie ces deux éléments séparément. Dans un simple eBGP directement connecté, le prochain saut est souvent directement raccordé. Dans iBGP et les architectures de cœur, la résolution récursive est plus visible.


## 3. Session BGP : TCP, états et messages

### 3.1. TCP port 179

BGP forme une session fiable au-dessus de TCP, typiquement sur le port 179. Avant même de comparer les routes, les deux extrémités doivent pouvoir établir la connexion TCP et accepter leurs paramètres de session. Un ping peut réussir pendant que la session BGP échoue : une ACL peut bloquer TCP/179, l’ASN distant peut être incorrect, ou les paramètres BGP peuvent être incompatibles.

Les contrôles de base comprennent l’adresse du voisin, l’adresse source attendue, l’accessibilité IP, le port TCP, l’ASN local/distant, le Router ID, l’authentification configurée et les capacités négociées. Le comportement exact dépend de l’implémentation et des options utilisées.

### 3.2. États BGP

La machine d’état inclut des états comme **Idle**, **Connect**, **Active**, **OpenSent**, **OpenConfirm** et **Established**. Le chemin nominal progresse vers Established lorsque TCP et l’échange d’ouverture réussissent. **Active n’est pas un synonyme de session établie** : le routeur est typiquement en train de tenter ou de reprendre la connexion TCP.

### Schéma 3 — Chemin nominal et état Active

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Cycle de vie simplifié d’une session BGP" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Cycle de vie simplifié d’une session BGP</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Chemin nominal de l’établissement TCP à Established ; Active signifie une tentative/reprise, pas un état « connecté ».</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="150" width="145" height="58" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="117.5" y="185" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Idle</text>
<rect x="225" y="150" width="145" height="58" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="297.5" y="185" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Connect</text>
<rect x="405" y="150" width="145" height="58" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="477.5" y="185" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">OpenSent</text>
<rect x="585" y="150" width="145" height="58" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="657.5" y="185" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">OpenConfirm</text>
<rect x="765" y="150" width="145" height="58" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="837.5" y="185" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Established</text>
<path d="M 190 179 L 225 179" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 216 172 L 225 179 L 216 186" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 370 179 L 405 179" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 396 172 L 405 179 L 396 186" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 550 179 L 585 179" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 576 172 L 585 179 L 576 186" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 730 179 L 765 179" fill="none" stroke="#45c7f5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 756 172 L 765 179 L 756 186" fill="none" stroke="#45c7f5" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="260" y="280" width="250" height="62" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/>
<text x="385" y="306" text-anchor="middle" fill="#fbbf24" font-size="14" font-weight="700">Active / nouvelle tentative</text>
<text x="385" y="328" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">TCP ou ouverture échouée</text>
<path d="M 297 208 L 297 250 L 385 250 L 385 280" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 260 311 L 205 311 L 205 179 L 225 179" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="6 6"/>
<text x="195" y="292" text-anchor="middle" fill="#fbbf24" font-size="11" font-weight="700">reprise</text>
<text x="480" y="405" text-anchor="middle" fill="#adbdcf" font-size="13" font-weight="400">Les timers, le TCP/179, le Router ID, les capacités et la politique doivent être compatibles.</text>
<text x="480" y="436" text-anchor="middle" fill="#adbdcf" font-size="13" font-weight="400">Après Established, UPDATE transporte les routes ; keepalive aide à maintenir la session.</text>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 190 179 L 225 179" dur="1.3s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 370 179 L 405 179" dur="1.3s" begin="0.4s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 550 179 L 585 179" dur="1.3s" begin="0.8s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 730 179 L 765 179" dur="1.3s" begin="1.2s" repeatCount="indefinite"/></circle>
</svg>
</div>

Le schéma ne montre qu’une trajectoire simplifiée de réussite. En exploitation, une tentative peut revenir à Connect ou Active après un échec, être temporisée, ou être réinitialisée par la détection d’une condition anormale.

### 3.3. Messages BGP principaux

| Message | Rôle simplifié |
|---|---|
| OPEN | Négocier les paramètres et identifier le pair, notamment l’ASN et les capacités |
| UPDATE | Annoncer ou retirer des routes et transporter des attributs |
| KEEPALIVE | Confirmer la continuité de la session lorsque nécessaire selon le protocole |
| NOTIFICATION | Signaler une erreur et généralement fermer la session |
| ROUTE-REFRESH | Demander une réannonce de routes selon les capacités négociées |

Les messages UPDATE transportent l’information de routage. Ils peuvent annoncer un préfixe, ses attributs et des retraits. BGP ne doit pas être modélisé comme une simple diffusion périodique de toute la table à chaque intervalle fixe : les changements et les mécanismes de rafraîchissement suivent les règles du protocole.

### 3.4. Comment interpréter `Established`

`Established` indique que la session est opérationnelle au niveau BGP et peut échanger des messages de routage. Cela ne signifie pas automatiquement qu’un préfixe voulu est reçu ou accepté. Il faut vérifier la politique, les attributs, le best path, la table de routage et le transfert réel.

Une session établie peut échanger zéro préfixe si les filtres interdisent toutes les annonces, si le voisin n’annonce rien, ou si les familles d’adresses/paramètres pertinents ne sont pas activés. La bonne question est donc : **quelles routes sont reçues, lesquelles sont éligibles, et lesquelles sont envoyées au voisin ?**


## 4. Préfixes et attributs : ce que BGP échange

### 4.1. NLRI et préfixe

BGP transporte des informations de joignabilité réseau, souvent appelées NLRI (*Network Layer Reachability Information*). Dans les exemples IPv4, le préfixe comprend une adresse réseau et une longueur, comme `192.0.2.0/24`. Une annonce BGP est interprétée avec ses attributs et les règles de politique.

Il faut annoncer des préfixes dont on a autorité et dont la portée est voulue. Une faute de masque, un préfixe trop large ou l’annonce par erreur d’une route par défaut peut détourner du trafic. Les filtres doivent décrire exactement la liste attendue avant qu’une session soit activée.

### 4.2. AS_PATH

AS_PATH indique la séquence d’AS parcourus par une route dans une annonce eBGP. Il joue un rôle de prévention des boucles inter-AS et d’aide à la sélection. Plus l’AS_PATH est court, plus un chemin peut être préféré à attributs comparables et selon l’algorithme de la plateforme, mais **le chemin AS le plus court n’est pas toujours choisi** si un attribut plus prioritaire ou une politique locale favorise un autre chemin.

### Schéma 4 — Comprendre la propagation d’AS_PATH

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="AS_PATH : la route garde la trace des AS traversés" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">AS_PATH : la route garde la trace des AS traversés</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Le chemin affiché est celui vu par le routeur récepteur ; l’AS voisin apparaît généralement à gauche dans l’AS_SEQUENCE.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="45" y="170" width="250" height="105" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="170.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Réseau origine</text>
<text x="170.0" y="220" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">AS 65010 · 192.0.2.0/24</text>
<rect x="355" y="170" width="250" height="105" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="480.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Transit</text>
<text x="480.0" y="220" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">AS 65020 · reçoit puis réannonce</text>
<rect x="665" y="170" width="250" height="105" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="790.0" y="197" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Destination</text>
<text x="790.0" y="220" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">AS 65030 · sélectionne le chemin</text>
<path d="M 295 223 L 355 223" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 605 223 L 665 223" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="325" y="204" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">eBGP</text>
<text x="635" y="204" text-anchor="middle" fill="#4ade80" font-size="12" font-weight="700">eBGP</text>
<rect x="65" y="330" width="225" height="58" rx="10" fill="#142a24" stroke="#4ade80" stroke-width="2"/>
<text x="177" y="354" text-anchor="middle" fill="#4ade80" font-size="14" font-weight="700">Annonce locale</text>
<text x="177" y="374" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">192.0.2.0/24</text>
<rect x="365" y="330" width="230" height="58" rx="10" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/>
<text x="480" y="354" text-anchor="middle" fill="#fbbf24" font-size="14" font-weight="700">Vu par AS 65020</text>
<text x="480" y="374" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">AS_PATH: 65010</text>
<rect x="665" y="330" width="250" height="58" rx="10" fill="#201b35" stroke="#c4b5fd" stroke-width="2"/>
<text x="790" y="354" text-anchor="middle" fill="#c4b5fd" font-size="14" font-weight="700">Vu par AS 65030</text>
<text x="790" y="374" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">AS_PATH: 65020 65010</text>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 295 223 L 355 223" dur="1.2s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 605 223 L 665 223" dur="1.2s" begin="0.6s" repeatCount="indefinite"/></circle>
<text x="480" y="434" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Un AS qui retrouve son propre ASN dans l’AS_PATH rejette généralement la route pour prévenir une boucle eBGP.</text>
</svg>
</div>

Les valeurs sont illustratives : lorsqu’un préfixe est annoncé depuis AS 65010 vers AS 65020, puis vers AS 65030, ce dernier voit normalement AS 65020 avant AS 65010 dans la séquence de chemin. L’ordre exact des attributs et la représentation détaillée dépendent du type d’annonce ; le principe visible ici est la liste d’AS traversés.

### 4.3. Attributs importants pour commencer

| Attribut | Utilité | À retenir |
|---|---|---|
| NEXT_HOP | Indique le prochain saut pour joindre le préfixe | Doit être résoluble dans le contexte de routage |
| AS_PATH | Trace des AS traversés | Contribue à éviter des boucles et à choisir un chemin |
| LOCAL_PREF | Préférence interne au même AS | Une valeur plus élevée est généralement préférée dans la décision locale |
| MED | Indication de préférence d’entrée dans un AS voisin | Une valeur plus faible peut être préférée, sous les règles de comparaison applicables |
| ORIGIN | Indique le type d’origine de la route | Les valeurs historiques IGP, EGP et incomplete sont comparées selon l’algorithme |
| COMMUNITY | Étiquette/pointeur de politique transporté avec la route | Son sens dépend de la convention d’exploitation et des règles configurées |
| WEIGHT | Préférence locale dans certaines implémentations Cisco | Propre au routeur, non propagée comme attribut BGP aux voisins |

### Schéma 5 — Lire les attributs sans les confondre

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 490" role="img" aria-label="Attributs BGP : ils décrivent et influencent la sélection des routes" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="490" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Attributs BGP : ils décrivent et influencent la sélection des routes</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">La séquence exacte de décision dépend de l’implémentation ; Weight est spécifique à Cisco et n’est pas transmis aux voisins.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="55" y="112" width="185" height="55" rx="9" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="147" y="145" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">LOCAL_PREF</text>
<rect x="255" y="112" width="365" height="55" rx="9" fill="#151f2d" stroke="#344357" stroke-width="1"/>
<text x="437" y="136" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="600">Préférence dans un AS</text>
<text x="437" y="154" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">Plus élevé préféré</text>
<rect x="55" y="180" width="185" height="55" rx="9" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="147" y="213" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">AS_PATH</text>
<rect x="255" y="180" width="365" height="55" rx="9" fill="#151f2d" stroke="#344357" stroke-width="1"/>
<text x="437" y="204" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="600">AS traversés</text>
<text x="437" y="222" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">Plus court souvent préféré</text>
<rect x="55" y="248" width="185" height="55" rx="9" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="147" y="281" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">ORIGIN</text>
<rect x="255" y="248" width="365" height="55" rx="9" fill="#151f2d" stroke="#344357" stroke-width="1"/>
<text x="437" y="272" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="600">Origine de la route</text>
<text x="437" y="290" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">IGP &lt; EGP &lt; incomplete</text>
<rect x="55" y="316" width="185" height="55" rx="9" fill="#172333" stroke="#fbbf24" stroke-width="2"/>
<text x="147" y="349" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">MED</text>
<rect x="255" y="316" width="365" height="55" rx="9" fill="#151f2d" stroke="#344357" stroke-width="1"/>
<text x="437" y="340" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="600">Coût annoncé à un voisin</text>
<text x="437" y="358" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">Plus faible souvent préféré*</text>
<rect x="55" y="384" width="185" height="55" rx="9" fill="#172333" stroke="#fb7185" stroke-width="2"/>
<text x="147" y="417" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">NEXT_HOP</text>
<rect x="255" y="384" width="365" height="55" rx="9" fill="#151f2d" stroke="#344357" stroke-width="1"/>
<text x="437" y="408" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="600">Prochain saut à atteindre</text>
<text x="437" y="426" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">Doit être résoluble</text>
<rect x="655" y="130" width="250" height="105" rx="12" fill="#201b35" stroke="#c4b5fd" stroke-width="2"/>
<text x="780" y="158" text-anchor="middle" fill="#c4b5fd" font-size="15" font-weight="700">Weight (Cisco)</text>
<text x="780" y="181" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">local au routeur</text>
<text x="780" y="201" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">jamais annoncé au peer</text>
<rect x="655" y="265" width="250" height="105" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/>
<text x="780" y="293" text-anchor="middle" fill="#fbbf24" font-size="15" font-weight="700">* MED</text>
<text x="780" y="316" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">comparaison conditionnelle</text>
<text x="780" y="336" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">selon la politique/plateforme</text>
<text x="480" y="460" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Ne mémorise pas une liste isolée : observe les attributs réellement reçus et la raison du best path.</text>
</svg>
</div>

Cette vue compare les rôles les plus courants sans prétendre représenter une séquence de sélection universelle. L’ordre complet du best-path peut varier selon l’implémentation, les options et les attributs présents. Dans le niveau débutant, il faut d’abord apprendre à afficher les attributs et à expliquer pourquoi une route précise a été retenue.

### 4.4. Sélection du meilleur chemin

BGP peut connaître plusieurs chemins vers le même préfixe. Il les compare au moyen du processus de décision du routeur. Certains paramètres sont des préférences internes, d’autres viennent du voisin, et certains chemins peuvent être inéligibles avant même la comparaison finale.

Une façon raisonnable d’aborder le best path consiste à :

1. vérifier si chaque chemin est valide et son prochain saut résoluble ;
2. regarder les politiques et préférences locales ;
3. comparer les attributs de chemin réellement reçus ;
4. consulter la raison de sélection affichée par la plateforme ;
5. vérifier la route installée dans la table générale et le chemin de transfert.

Ne modifie pas d’emblée MED, LOCAL_PREF ou AS_PATH pour « forcer » un résultat. Commence par déterminer où le chemin perd l’élection et quel attribut est réellement comparé sur l’équipement.


## 5. Politiques d’importation et d’exportation

### 5.1. Pourquoi une session ne suffit pas

Les politiques définissent quelles annonces peuvent entrer dans la décision locale, lesquelles sont rejetées, et quelles routes seront exportées vers un voisin. Sans politique explicite et ciblée, une erreur peut propager un préfixe que le réseau ne devrait pas annoncer. Les pratiques modernes recommandent de contrôler les annonces à chaque frontière eBGP, avec une liste attendue de préfixes et des limites explicites.

RFC 8212 spécifie que les routes ne doivent pas être éligibles à la décision eBGP sans politique d’importation explicite, et qu’elles ne doivent pas être annoncées sans politique d’exportation explicite, sous réserve du comportement de l’implémentation et de sa configuration. Tous les équipements déployés ne présentent pas nécessairement ce comportement par défaut ; il faut donc configurer, vérifier et tester la politique plutôt que supposer qu’elle existe.

### Schéma 6 — Filtrer les annonces entrantes et sortantes

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="Politique BGP : contrôler ce qui entre et ce qui sort" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Politique BGP : contrôler ce qui entre et ce qui sort</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Exemple de principe : n’accepter que le préfixe attendu du voisin et n’annoncer que les préfixes autorisés.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="50" y="160" width="190" height="82" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="145.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">AS voisin</text>
<text x="145.0" y="210" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">annonce reçue</text>
<rect x="300" y="145" width="280" height="112" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/>
<text x="440" y="173" text-anchor="middle" fill="#fbbf24" font-size="16" font-weight="700">Filtre IN</text>
<text x="440" y="196" text-anchor="middle" fill="#eef4fb" font-size="13" font-weight="400">prefix-list / route-map</text>
<text x="440" y="221" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">allow attendu · deny reste</text>
<rect x="675" y="160" width="230" height="82" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="790.0" y="187" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">RIB BGP locale</text>
<text x="790.0" y="210" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">routes candidates</text>
<path d="M 240 201 L 300 201" fill="none" stroke="#45c7f5" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 580 201 L 675 201" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="300" y="300" width="280" height="96" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="2"/>
<text x="440" y="328" text-anchor="middle" fill="#fb7185" font-size="16" font-weight="700">Filtre OUT</text>
<text x="440" y="351" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="400">liste des préfixes annoncés</text>
<text x="440" y="374" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">pas de fuite de routes</text>
<path d="M 790 242 L 790 270 L 580 270 L 580 300" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="675" y="330" width="230" height="70" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="790.0" y="357" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">AS voisin</text>
<text x="790.0" y="380" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">reçoit export filtré</text>
<path d="M 580 348 L 675 365" fill="none" stroke="#c4b5fd" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 240 201 L 300 201" dur="1.1s" begin="0s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#4ade80" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 580 201 L 675 201" dur="1.2s" begin="0.5s" repeatCount="indefinite"/></circle>
<circle r="5" fill="#fb7185" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 790 242 L 790 270 L 580 270 L 580 300" dur="2.4s" begin="0.2s" repeatCount="indefinite"/></circle>
<text x="480" y="443" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Règle opérationnelle : politique explicite dans les deux directions ; vérifier les routes annoncées après activation.</text>
</svg>
</div>

La politique d’importation (IN) agit sur les routes reçues d’un voisin ; la politique d’exportation (OUT) agit sur les routes envoyées à ce voisin. Un préfixe qui n’est pas accepté ne devient pas une route utilisable ; un préfixe non autorisé à l’export ne doit pas être annoncé à ce voisin. Les commandes et valeurs de défaut varient selon le système : vérifie la configuration effective.

### 5.2. Prefix-list et route-map

Une **prefix-list** définit les préfixes qu’une politique reconnaît. Une **route-map** peut associer une condition de correspondance à une action, par exemple accepter un préfixe et définir un attribut. La logique d’évaluation, l’ordre des séquences et l’action implicite en fin de liste sont importants : un filtre qui semble correct visuellement peut bloquer toutes les routes ou, à l’inverse, accepter trop de routes.

Avant d’activer une politique :

- inventorie les préfixes légitimes reçus du voisin ;
- inventorie les préfixes que tu dois lui annoncer ;
- décide ce qui doit être rejeté ;
- inspecte les compteurs ou les annonces post-politique ;
- vérifie qu’aucune route par défaut ou plage plus large ne passe par accident ;
- prépare une procédure de retour arrière.

### 5.3. Filtres et risque de route leak

Une fuite de routes (*route leak*) se produit lorsqu’une information de routage est propagée en dehors de la portée ou de la politique prévue. Le problème peut venir d’un mauvais filtre, d’une redistribution trop large ou d’une configuration de peering. La conséquence va de l’acheminement asymétrique à la perte de connectivité ou au détournement du trafic.

Une politique correcte décrit à la fois ce que l’on accepte et ce que l’on annonce. Le fait qu’un préfixe soit légitime dans son réseau d’origine ne signifie pas qu’il doit être exporté vers tous les voisins. Le sens commercial de la relation — client, fournisseur, pair, réseau interne — influence souvent les règles d’exportation.


## 6. Configuration d’un laboratoire eBGP à deux routeurs

Cette section configure deux routeurs connectés directement dans une maquette. Les adresses de documentation ne sont pas destinées à une annonce sur Internet. La commande `network` sous BGP n’attribue pas l’adresse et ne crée pas l’interface : elle demande à BGP d’annoncer le préfixe si une route correspondante est présente dans la table de routage, selon la syntaxe et les règles du système.

### 6.1. Topologie et plan d’adressage

| Équipement | AS | Interface de transit | LAN local à annoncer |
|---|---:|---|---|
| R1 | 65010 | `203.0.113.1/30` | `192.0.2.0/24` |
| R2 | 65020 | `203.0.113.2/30` | `198.51.100.0/24` |

Adapte les noms d’interfaces à ton routeur. Dans l’exemple, `GigabitEthernet0/0` est le lien de transit et `GigabitEthernet0/1` est l’interface LAN. Les LAN doivent être présents dans la table de routage, par exemple en tant que réseaux connectés.

### 6.2. R1 — AS 65010

```cisco
configure terminal
!
interface GigabitEthernet0/0
 description EBGP_VERS_R2
 ip address 203.0.113.1 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description LAN_R1
 ip address 192.0.2.1 255.255.255.0
 no shutdown
!
ip prefix-list R2-IN seq 5 permit 198.51.100.0/24
ip prefix-list R1-OUT seq 5 permit 192.0.2.0/24
!
route-map R2-IN permit 10
 match ip address prefix-list R2-IN
!
route-map R1-OUT permit 10
 match ip address prefix-list R1-OUT
!
router bgp 65010
 bgp router-id 1.1.1.1
 neighbor 203.0.113.2 remote-as 65020
 neighbor 203.0.113.2 description R2_AS65020
 neighbor 203.0.113.2 route-map R2-IN in
 neighbor 203.0.113.2 route-map R1-OUT out
 network 192.0.2.0 mask 255.255.255.0
end
```

### 6.3. R2 — AS 65020

```cisco
configure terminal
!
interface GigabitEthernet0/0
 description EBGP_VERS_R1
 ip address 203.0.113.2 255.255.255.252
 no shutdown
!
interface GigabitEthernet0/1
 description LAN_R2
 ip address 198.51.100.1 255.255.255.0
 no shutdown
!
ip prefix-list R1-IN seq 5 permit 192.0.2.0/24
ip prefix-list R2-OUT seq 5 permit 198.51.100.0/24
!
route-map R1-IN permit 10
 match ip address prefix-list R1-IN
!
route-map R2-OUT permit 10
 match ip address prefix-list R2-OUT
!
router bgp 65020
 bgp router-id 2.2.2.2
 neighbor 203.0.113.1 remote-as 65010
 neighbor 203.0.113.1 description R1_AS65010
 neighbor 203.0.113.1 route-map R1-IN in
 neighbor 203.0.113.1 route-map R2-OUT out
 network 198.51.100.0 mask 255.255.255.0
end
```

### 6.4. Pourquoi les annonces peuvent-elles manquer ?

La route `192.0.2.0/24` doit être présente dans la table de routage de R1, par exemple parce que l’interface LAN est configurée avec une adresse appartenant à ce sous-réseau. Si le LAN est absent de la RIB, la commande `network` peut ne pas provoquer l’annonce attendue. Vérifie également la résolution du voisin, l’état de l’interface et les politiques.

Les prefix-lists de cet exemple utilisent un seul préfixe exact. Les règles non explicitement acceptées ne passent pas la route-map illustrée. Avant d’utiliser une syntaxe équivalente sur une autre plateforme, confirme le comportement de la séquence terminale et des politiques sans correspondance.

### 6.5. Vérifier l’état

Commandes Cisco IOS courantes (la disponibilité varie selon la version) :

```cisco
show ip interface brief
show ip bgp summary
show ip bgp
show ip bgp neighbors 203.0.113.2
show ip route bgp
show ip prefix-list
show route-map
```

Sur R1, vérifie que le voisin `203.0.113.2` est établi et que le préfixe `198.51.100.0/24` est reçu/sélectionné. Sur R2, vérifie `192.0.2.0/24`. Puis effectue des tests ciblés entre les adresses LAN, en tenant compte des règles ICMP, des routes retour et de l’environnement simulé.

### 6.6. Sauvegarde et retour arrière

N’enregistre pas un changement avant d’avoir validé le résultat prévu et vérifié que les filtres n’annoncent pas d’autres routes. Dans une maquette, garde une copie de la configuration initiale. En production, la procédure peut inclure une fenêtre de changement, des captures avant/après et une validation par un second administrateur.


## 7. BGP et IGP : plan de contrôle et résolution du prochain saut

### Schéma 7 — BGP et IGP remplissent des rôles complémentaires

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 480" role="img" aria-label="BGP et IGP : deux rôles différents, souvent complémentaires" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="480" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">BGP et IGP : deux rôles différents, souvent complémentaires</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">BGP transporte la politique de joignabilité entre AS ; un IGP fournit souvent la connectivité interne et la résolution de NEXT_HOP.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="50" y="115" width="385" height="245" rx="14" fill="#101f30" stroke="#45c7f5" stroke-width="2"/>
<text x="242" y="143" text-anchor="middle" fill="#45c7f5" font-size="16" font-weight="700">AS 65010</text>
<rect x="90" y="180" width="125" height="70" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="152.5" y="207" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Edge</text>
<text x="152.5" y="230" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">BGP</text>
<rect x="280" y="180" width="115" height="70" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="337.5" y="207" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Core</text>
<text x="337.5" y="230" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">IGP</text>
<path d="M 215 215 L 280 215" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="242" y="198" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">IGP</text>
<rect x="525" y="115" width="385" height="245" rx="14" fill="#201b35" stroke="#c4b5fd" stroke-width="2"/>
<text x="717" y="143" text-anchor="middle" fill="#c4b5fd" font-size="16" font-weight="700">AS 65020</text>
<rect x="565" y="180" width="125" height="70" rx="12" fill="#172333" stroke="#c4b5fd" stroke-width="2"/>
<text x="627.5" y="207" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Edge</text>
<text x="627.5" y="230" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">BGP</text>
<rect x="755" y="180" width="115" height="70" rx="12" fill="#172333" stroke="#4ade80" stroke-width="2"/>
<text x="812.5" y="207" text-anchor="middle" fill="#eef4fb" font-size="17" font-weight="700">Core</text>
<text x="812.5" y="230" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">IGP</text>
<path d="M 690 215 L 755 215" fill="none" stroke="#4ade80" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="722" y="198" text-anchor="middle" fill="#4ade80" font-size="11" font-weight="700">IGP</text>
<path d="M 395 215 L 565 215" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<text x="480" y="197" text-anchor="middle" fill="#fbbf24" font-size="13" font-weight="700">eBGP</text>
<circle r="6" fill="#fbbf24" stroke="#eef4fb" stroke-width="1.8"><animateMotion path="M 395 215 L 565 215" dur="2.8s" begin="0s" repeatCount="indefinite"/></circle>
<text x="480" y="405" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Un préfixe BGP peut être connu sans NEXT_HOP résoluble : il ne sera pas forcément installé/utilisable.</text>
</svg>
</div>

La session eBGP échange des préfixes entre AS. À l’intérieur de chaque AS, un IGP ou des routes connectées peuvent transporter les préfixes d’infrastructure permettant d’atteindre les routeurs et les NEXT_HOP. L’IGP ne remplace pas la politique BGP ; BGP ne remplace pas la connectivité interne nécessaire à son fonctionnement.

### 7.1. Une route BGP reçue mais non installée

Quand le voisin est `Established` mais que le préfixe n’apparaît pas dans la RIB, vérifie successivement :

1. le voisin envoie-t-il réellement le préfixe ?
2. la politique d’importation l’accepte-t-elle ?
3. la route est-elle valide selon les attributs et la famille d’adresses ?
4. le NEXT_HOP est-il résolu ?
5. une autre source de routage est-elle préférée dans la RIB ?
6. le routeur installe-t-il un chemin de forwarding utilisable ?

La réponse n’est pas toujours « ajouter un network statement ». Une annonce peut être reçue puis rejetée par politique, ou acceptée par BGP sans être installée parce que son prochain saut est inaccessible. Affiche les attributs et la raison du meilleur chemin si la plateforme la fournit.

### 7.2. Le plan de données

Après installation, le plan de transfert doit pouvoir acheminer les paquets. Vérifie le préfixe, la route de retour et le prochain saut. Un test ping ne prouve pas à lui seul que toutes les applications fonctionnent, car les pare-feu, les ACL, les chemins asymétriques et les MTU peuvent affecter le trafic. Utilise un test correspondant au service réellement visé.


## 8. Sécurité BGP : les premières règles

BGP est un protocole de contrôle du routage. Une annonce erronée peut affecter plus d’un routeur et, dans un environnement public, avoir un impact très large. La sécurité commence par un périmètre précis : qui est le voisin, quelles routes peut-il annoncer et lesquelles sommes-nous autorisés à lui annoncer ?

### 8.1. Mesures élémentaires

- définir des politiques d’importation et d’exportation pour chaque session eBGP ;
- n’accepter que les préfixes attendus et interdire les plages non légitimes ;
- annoncer uniquement les préfixes approuvés ;
- filtrer l’accès au plan de contrôle, notamment aux sessions TCP BGP autorisées ;
- contrôler le nombre de préfixes acceptés avec des limites adaptées si la plateforme le permet ;
- protéger la gestion des routeurs et limiter les modifications de configuration ;
- superviser les changements de session et de routes ;
- maintenir une procédure de retour arrière testée.

### 8.2. Pourquoi un filtre de préfixes est indispensable

Une route plus spécifique peut attirer un trafic qui aurait sinon suivi une route moins spécifique. Une annonce par erreur ou malveillante peut créer un détour ou une perte de connectivité. Les filtres doivent tenir compte du rôle du voisin, des préfixes qu’il est autorisé à fournir et du plan d’adressage. Les filtres copiés sans adaptation peuvent être aussi dangereux que l’absence de filtre.

### 8.3. Limites des exemples débutants

Les commandes de filtrage, l’authentification de session, les limites de préfixes, les communautés et les contrôles anti-usurpation varient selon les OS réseau. Les exemples ne sont pas une politique Internet universelle. Le déploiement réel doit suivre la documentation de la plate-forme et les accords avec les fournisseurs/peers.


## 9. Tableau de dépannage BGP

### Schéma 8 — Distinguer session, préfixe et transfert

<div class="lesson-figure" style="max-width:100%;overflow-x:auto;margin:1.2rem 0;border-radius:14px">
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 500" role="img" aria-label="Dépannage BGP : distinguer session, route, sélection et transfert" style="display:block;width:100%;max-width:960px;height:auto;font-family:Inter,Arial,sans-serif">
<rect width="960" height="500" rx="16" fill="#0d1420"/>
<text x="28" y="34" fill="#eef4fb" font-size="22" font-weight="700">Dépannage BGP : distinguer session, route, sélection et transfert</text>
<text x="28" y="58" fill="#adbdcf" font-size="13">Ne change pas les timers au hasard : chaque étape doit produire une observation qui confirme ou exclut une hypothèse.</text>
<line x1="28" y1="76" x2="932" y2="76" stroke="#34475d" stroke-width="1.5"/>
<rect x="330" y="100" width="300" height="60" rx="12" fill="#172333" stroke="#45c7f5" stroke-width="2"/>
<text x="480" y="125" text-anchor="middle" fill="#eef4fb" font-size="15" font-weight="700">Problème de reachabilité ?</text>
<text x="480" y="145" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">préciser source / destination / préfixe</text>
<rect x="55" y="220" width="245" height="75" rx="12" fill="#301b25" stroke="#fb7185" stroke-width="2"/>
<text x="177" y="248" text-anchor="middle" fill="#fb7185" font-size="14" font-weight="700">Session non établie</text>
<text x="177" y="272" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="400">TCP 179 · voisin · paramètres</text>
<rect x="358" y="220" width="245" height="75" rx="12" fill="#2a2619" stroke="#fbbf24" stroke-width="2"/>
<text x="480" y="248" text-anchor="middle" fill="#fbbf24" font-size="14" font-weight="700">Session Established</text>
<text x="480" y="272" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="400">mais préfixe absent ?</text>
<rect x="660" y="220" width="245" height="75" rx="12" fill="#142a24" stroke="#4ade80" stroke-width="2"/>
<text x="782" y="248" text-anchor="middle" fill="#4ade80" font-size="14" font-weight="700">Route présente</text>
<text x="782" y="272" text-anchor="middle" fill="#eef4fb" font-size="11" font-weight="400">mais trafic échoue ?</text>
<path d="M 480 160 L 177 220" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 480 160 L 480 220" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 480 160 L 782 220" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<rect x="55" y="340" width="245" height="65" rx="10" fill="#fb7185" stroke="#182333" stroke-width="1"/>
<text x="177" y="365" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="700">IP / TCP / AS / ID</text>
<text x="177" y="386" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">ACL control-plane, timers</text>
<rect x="358" y="340" width="245" height="65" rx="10" fill="#fbbf24" stroke="#182333" stroke-width="1"/>
<text x="480" y="365" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="700">Origine / policy / best path</text>
<text x="480" y="386" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">NEXT_HOP · filtre · RIB</text>
<rect x="660" y="340" width="245" height="65" rx="10" fill="#4ade80" stroke="#182333" stroke-width="1"/>
<text x="782" y="365" text-anchor="middle" fill="#eef4fb" font-size="12" font-weight="700">FIB / route retour / ACL</text>
<text x="782" y="386" text-anchor="middle" fill="#adbdcf" font-size="11" font-weight="400">MTU · hôte · service</text>
<path d="M 177 295 L 177 340" fill="none" stroke="#fb7185" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 480 295 L 480 340" fill="none" stroke="#fbbf24" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M 782 295 L 782 340" fill="none" stroke="#4ade80" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<text x="480" y="455" text-anchor="middle" fill="#adbdcf" font-size="12" font-weight="400">Preuves : show bgp summary · routes · policy · logs · ping/traceroute ciblés · captures si nécessaire</text>
</svg>
</div>

### 9.1. Session bloquée en Idle, Connect ou Active

Vérifie l’état et la joignabilité IP du voisin, TCP/179, la configuration de l’ASN local et distant, l’adresse du voisin, les restrictions de contrôle-plane et les paramètres d’authentification s’ils sont configurés. En cas de voisinage loopback ou multi-saut, vérifie les routes de transport et les paramètres de source. N’augmente pas arbitrairement les timers pour résoudre un problème TCP.

### 9.2. Session Established mais aucun préfixe reçu

Vérifie si le voisin annonce les préfixes, si les règles d’importation les acceptent, si la famille d’adresses est activée et si le préfixe est correctement originaire chez le voisin. Vérifie les journaux et la sortie de politique. Une session établie sans routes peut être le résultat voulu d’une politique stricte.

### 9.3. Préfixe reçu mais absent de la table de routage

Inspecte le best path et ses attributs, vérifie le NEXT_HOP, compare les sources de routes concurrentes et regarde si la plateforme a une raison explicite pour ne pas installer le chemin. Distingue l’Adj-RIB-In, le chemin BGP sélectionné et la RIB générale : ce sont des vues différentes.

### 9.4. Préfixe installé mais trafic en échec

Vérifie la FIB/route de forwarding si accessible, les routes retour, les ACL/pare-feu, le MTU, le DNS si le test utilise un nom, et l’hôte destination. Une panne de service n’indique pas toujours une panne BGP.

### 9.5. Route annoncée par erreur

Compare l’export réel avec la liste approuvée, vérifie la route-map et la prefix-list réellement attachées au voisin, puis applique le plan de retrait contrôlé. Ne supprime pas le processus BGP entier pour retirer une annonce si un correctif ciblé de politique est possible et approuvé.


## 10. Laboratoires pratiques

### Laboratoire 1 — Former une session eBGP

**But :** obtenir `Established` entre R1 et R2 de l’exemple de la section 6.

1. Vérifie les interfaces, les adresses et les pings sur le réseau de transit.
2. Configure les ASN et le voisin de chaque côté.
3. Vérifie l’état avec `show ip bgp summary`.
4. Si l’état n’est pas établi, note l’état exact et collecte les paramètres avant de modifier quoi que ce soit.
5. Corrige une seule cause supposée puis confirme que l’état a changé pour la raison attendue.

**Livrable :** sorties avant/après et diagnostic de la cause initiale.

### Laboratoire 2 — Annoncer un préfixe local

1. Vérifie que le réseau LAN apparaît dans la RIB.
2. Configure le `network` statement exact.
3. Vérifie la table BGP locale et l’annonce envoyée au voisin.
4. Retire temporairement l’entrée de la RIB en laboratoire, si c’est sans risque pour la maquette, puis observe la différence.
5. Restaure la route et prouve que l’annonce revient.

**À démontrer :** BGP ne crée pas l’interface et le `network` statement ne remplace pas le plan d’adressage.

### Laboratoire 3 — Filtrer les annonces

1. Configure une prefix-list qui autorise seulement le préfixe LAN attendu.
2. Attache la politique d’importation au voisin.
3. Vérifie que la route attendue est acceptée.
4. Dans un lab isolé, ajoute un préfixe non prévu depuis un voisin de test.
5. Vérifie qu’il ne devient pas une route candidate utilisable.
6. Configure l’export et vérifie les annonces sortantes.

**Livrable :** tableau des préfixes reçus, acceptés, sélectionnés, exportés et rejetés.

### Laboratoire 4 — Lire AS_PATH

Utilise deux ou trois AS simulés. Observe la route à l’origine, sur le premier voisin et sur le dernier AS. Note l’ASN qui apparaît dans l’AS_PATH après chaque passage eBGP. Explique le rôle de cette information pour l’évitement de boucle et pourquoi la longueur n’est qu’un facteur du choix de route.

### Laboratoire 5 — Préférer un chemin dans un AS privé de test

Configure deux chemins à un même préfixe uniquement dans un laboratoire conçu pour cela. Compare les attributs BGP et la décision de best path. Ne change qu’un attribut à la fois et relève le résultat réel. Le but est d’observer la politique, pas de mémoriser un ordre de commandes dépendant d’un constructeur.

### Laboratoire 6 — Session établie, service indisponible

Laisse le voisinage BGP établi mais introduis dans le lab une erreur de route retour ou de filtre sur le service. Vérifie le voisinage, la table de route, puis la connectivité depuis l’hôte. Produis une explication qui distingue la santé de la session et celle de l’application.


## 11. Évaluation avec corrigés

### Questions

1. Que signifie AS et à quoi sert un ASN ?
2. Quelle est la différence entre eBGP et iBGP ?
3. Pourquoi BGP utilise-t-il TCP ?
4. Que signifie l’état `Established` ?
5. Quelle information donne AS_PATH ?
6. Pourquoi un routeur peut-il recevoir une route sans l’installer dans la RIB ?
7. Quelle différence existe entre politique d’importation et d’exportation ?
8. Pourquoi faut-il vérifier que le préfixe d’un `network` statement existe dans la RIB ?
9. LOCAL_PREF et MED sont-ils interchangeables ?
10. Le chemin AS le plus court est-il toujours préféré ?
11. Pourquoi BGP a-t-il besoin que NEXT_HOP soit résoluble ?
12. Quelle est la différence entre route acceptée et route annoncée ?
13. Pourquoi une session établie peut-elle n’échanger aucune route ?
14. Que faire si une route est installée mais que l’application échoue ?
15. Pourquoi utiliser des prefix-lists sur une session eBGP ?
16. Que veut dire une route leak ?
17. Quelle différence existe entre une LSA OSPF et une annonce BGP ?
18. Quels contrôles effectuer si la session reste en Active ?
19. Pourquoi la politique d’exportation doit-elle dépendre de la relation avec le voisin ?
20. Quelles preuves conserver lors d’un changement BGP ?

### Corrigés

**1.** Un AS est un domaine de routage exploité selon une politique commune ; l’ASN identifie ce domaine dans les échanges BGP.

**2.** eBGP relie des AS différents ; iBGP relie des routeurs du même AS.

**3.** TCP fournit un transport fiable et ordonné des messages de session BGP, généralement sur le port 179.

**4.** La session est établie et peut échanger des routes. Cela ne garantit pas qu’un préfixe particulier est accepté, installé ou joignable.

**5.** AS_PATH montre les AS traversés par la route, contribue à la prévention de boucles et intervient dans le choix de chemin.

**6.** La politique peut rejeter la route, le NEXT_HOP peut être inaccessible, une autre route peut être préférée ou le chemin peut être inéligible.

**7.** L’importation contrôle les routes reçues et considérées localement ; l’exportation contrôle les routes annoncées au voisin.

**8.** Le `network` statement annonce en général un préfixe déjà présent dans la table de routage selon les règles de la plateforme ; il ne crée pas ce réseau.

**9.** Non. LOCAL_PREF sert principalement à la préférence interne d’un AS ; MED influence souvent l’entrée préférée depuis un AS voisin et sa comparaison est conditionnelle.

**10.** Non. Un attribut plus prioritaire, une préférence locale ou l’éligibilité du chemin peut mener à un autre choix.

**11.** Le NEXT_HOP est le prochain routeur vers lequel le trafic doit être envoyé. S’il n’est pas résolu, le chemin peut ne pas être utilisable.

**12.** Une route acceptée est admissible à la décision locale ; une route annoncée est sélectionnée pour être exportée à un voisin selon la politique sortante.

**13.** Le voisin peut ne rien annoncer, la politique peut tout rejeter ou la famille d’adresses pertinente peut ne pas être activée.

**14.** Vérifier forwarding, routes retour, ACL/pare-feu, MTU, DNS et service. Ne pas accuser BGP avant d’avoir localisé la panne.

**15.** Elles limitent le périmètre aux préfixes attendus, préviennent les annonces accidentelles et donnent une intention vérifiable.

**16.** Une route leak est la propagation de routes en dehors de la politique ou de la portée prévue.

**17.** OSPF échange des informations d’état de liens dans une aire et calcule SPF ; BGP échange des préfixes et attributs selon des politiques entre voisins.

**18.** Vérifier IP source/destination, TCP/179, remote-as, adresse de voisin, ACL du plan de contrôle, timers/authentification si activés et journaux de session.

**19.** Un client, un fournisseur, un pair et un voisin interne n’ont pas nécessairement le droit d’apprendre ou de recevoir les mêmes préfixes.

**20.** Configuration avant/après, état de session, routes reçues/sélectionnées/exportées, policy attachée, captures/logs horodatés, tests applicatifs et plan de retour arrière.


## 12. Checklist avant/après modification BGP

### Avant
- [ ] Identifier le voisin, son ASN et la relation (client, fournisseur, pair, interne).
- [ ] Sauvegarder la configuration actuelle et collecter la sortie de `show ip bgp summary`.
- [ ] Établir la liste précise des préfixes attendus en entrée et en sortie.
- [ ] Vérifier le plan d’adressage et les routes locales nécessaires aux annonces.
- [ ] Préparer les tests de connectivité et une procédure de retour arrière.

### Pendant
- [ ] Modifier un élément à la fois.
- [ ] Examiner les routes reçues, acceptées et sélectionnées.
- [ ] Vérifier l’export réel de la route-map et de la prefix-list.
- [ ] Éviter l’activation d’une session sans politique validée.

### Après
- [ ] Vérifier Established et les préfixes attendus.
- [ ] Comparer best path, RIB et route de forwarding.
- [ ] Tester le trafic dans les deux sens et le service concerné.
- [ ] Archiver les résultats et mettre à jour le diagramme de réseau.


## 13. Glossaire essentiel

| Terme | Sens pratique |
|---|---|
| AS / ASN | Système autonome / numéro d’identification |
| eBGP | Session BGP entre AS distincts |
| iBGP | Session BGP au sein du même AS |
| NLRI | Information de joignabilité d’un préfixe réseau |
| AS_PATH | Suite des AS traversés par une route annoncée |
| NEXT_HOP | Prochain saut utilisé pour atteindre un préfixe |
| LOCAL_PREF | Préférence de route au sein d’un AS, généralement plus élevée = préférable |
| MED | Attribut qui peut aider à choisir un point d’entrée vers un AS voisin |
| Community | Étiquette transportée dans BGP pour exprimer ou appliquer une politique |
| Prefix-list | Filtre qui reconnaît des préfixes et longueurs de préfixe |
| Route-map | Règle conditionnelle pour filtrer ou modifier des attributs, selon la plateforme |
| RIB | Table de routage générale du système |
| Route leak | Propagation involontaire ou non autorisée de routes |
| Best path | Chemin choisi par le processus de décision local BGP |


## 14. Références techniques

Les normes décrivent le protocole ; elles ne garantissent pas la même commande ni le même ordre d’affichage sur chaque routeur. Vérifie toujours la documentation de la version et la politique de ton réseau.

- **RFC 4271 — A Border Gateway Protocol 4 (BGP-4)**, spécification de base : <https://www.rfc-editor.org/rfc/rfc4271.html>
- **RFC 8212 — Default eBGP Route Propagation Behavior without Policies**, exigences de politique explicite import/export : <https://www.rfc-editor.org/rfc/rfc8212.html>
- **RFC 7454 — BGP Operations and Security**, recommandations opérationnelles de sécurité : <https://www.rfc-editor.org/rfc/rfc7454.html>
- **RFC 6793 — BGP Support for Four-Octet AS Number Space**, prise en charge des ASN 32 bits : <https://www.rfc-editor.org/rfc/rfc6793.html>
- **Cisco — BGP Configuration Guide**, sélectionner la version correspondant au système utilisé : <https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-software/products-installation-and-configuration-guides-list.html>

## Préparation au niveau Intermédiaire

Le niveau Intermédiaire réutilisera les notions de session BGP, ASN, préfixes, AS_PATH, attributs, politiques et NEXT_HOP. Il approfondira les politiques de préférence, iBGP, route reflectors, communautés, agrégation, filtrage avancé, contrôle d’annonces et analyse des décisions best path. Le niveau Expert traitera les architectures multi-fournisseurs, l’ingénierie de trafic, la résilience, l’automatisation et les incidents à large impact.
