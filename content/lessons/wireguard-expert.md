# VPN WireGuard — Expert

**Niveau :** EXPERT

Ce cours poursuit les niveaux Débutant et Intermédiaire. Il suppose que tu sais créer une paire de clés, configurer des peers, lire `wg show`, utiliser `wg-quick`, router un LAN dans le tunnel et diagnostiquer les pannes de base. Ici, le travail consiste à concevoir une architecture gouvernable, à traiter les ambiguïtés de routage, à sécuriser les chemins de données, à maintenir le service en cas de panne et à produire des preuves opérationnelles.

Les exemples sont centrés sur Linux avec `wireguard-tools`, `iproute2`, `nftables` et systemd. Ils ne sont pas universels : adapte les noms d’interfaces, les chemins, les gestionnaires réseau, les capacités du noyau et les politiques de sécurité avant exécution. Les adresses des blocs `198.51.100.0/24`, `203.0.113.0/24` et `2001:db8::/32` sont réservées à la documentation ; elles ne doivent pas être utilisées comme endpoints publics réels.

> **Analogie** : au niveau Expert, WireGuard n’est plus seulement un tunnel entre deux machines. C’est un système d’identité cryptographique intégré à un plan de routage, à des zones de sécurité et à des procédures de changement. Le chiffrement protège un paquet sur le transport ; il ne décide pas, à lui seul, si le paquet doit être routé vers un service, s’il respecte les règles inter-zones ou si le service distant fonctionne.

> **Piège :** un handshake récent ne signifie pas « VPN opérationnel ». Il indique qu’un échange cryptographique est récent entre deux clés configurées. La route du LAN, `AllowedIPs`, le forwarding Linux, le pare-feu, la MTU, le DNS et l’application restent des dépendances séparées.

---

## 1. Théorie et architecture experte

### 1.1 Modèle de sécurité : ce que WireGuard fait et ne fait pas

WireGuard transporte des paquets IP encapsulés dans UDP. Il associe les peers à des clés publiques préconfigurées et utilise une construction de handshake basée sur Noise. Les primitives annoncées par la spécification WireGuard comprennent notamment Curve25519 pour l’échange de secret, ChaCha20-Poly1305 pour le chiffrement authentifié, BLAKE2s pour le hachage et HKDF pour la dérivation. Il utilise un protocole concis et des suites cryptographiques fixées plutôt qu’une longue négociation de suites. Consulte la page protocolaire officielle pour les détails exacts de la version que tu exploites.

WireGuard n’est pas un système complet de gestion d’identité d’entreprise. Il ne fournit pas nativement une autorité de certification, un annuaire d’utilisateurs, une distribution automatique des routes, un portail d’approbation des appareils ni un contrôle d’accès applicatif. La distribution de clés, le cycle de vie des peers, l’inventaire, la collecte de télémétrie et l’automatisation de la configuration doivent être fournis par des couches opérationnelles distinctes.

| Couche | Question de conception | Responsable typique |
|---|---|---|
| Identité cryptographique | Quelle clé publique représente quel appareil ? | Gestion des clés, inventaire et procédures d’enrôlement |
| Handshake et transport | Les deux clés configurées peuvent-elles établir un canal ? | WireGuard et le chemin UDP extérieur |
| Sélection du peer | Quel peer correspond à la destination intérieure ? | `AllowedIPs` et routage système |
| Acheminement IP | Le noyau possède-t-il une route aller et retour ? | `iproute2`, policy routing, protocoles de routage |
| Autorisation réseau | Le flux est-il autorisé entre zones ? | `nftables`, filtrage de l’hôte et ACL réseau |
| Service | Le port et l’application répondent-ils ? | Service cible, DNS, identité applicative |
| Gouvernance | Qui peut créer, modifier ou révoquer un peer ? | Processus de changement, IAM, dépôt contrôlé |

> **Astuce :** écris le modèle de menace avant les règles de pare-feu. Sépare au minimum la perte de confidentialité sur le réseau extérieur, le vol d’une clé privée d’un endpoint, un peer autorisé mais compromis, une erreur de route, une mauvaise attribution d’`AllowedIPs`, une panne d’opérateur et un abus du plan d’administration.

### 1.2 Architecture multi-sites, frontières de confiance et contrôle des préfixes

Dans un hub-and-spoke, le concentrateur contient un peer distinct par site. Chaque entrée doit posséder une clé publique distincte et un ensemble de préfixes correspondant à ce peer. Un hub ne fournit pas automatiquement un routage inter-sites : le système Linux doit acheminer les paquets d’un peer vers un autre, le forwarding doit être activé, les règles du pare-feu doivent l’autoriser et les LAN doivent connaître la route de retour. Un maillage complet implique une configuration et une exploitation différentes ; ne le construis pas implicitement en élargissant toutes les listes `AllowedIPs`.

Les sous-réseaux chevauchants sont un défaut de conception, pas une anomalie cryptographique. Deux sites annonçant `10.20.0.0/24` ne peuvent pas être distingués par leur seul préfixe de destination à travers la même table de routage. Les options sont la renumérotation, une traduction NAT documentée, une segmentation en VRF / namespaces avec politiques explicites ou une passerelle applicative. La traduction peut rendre le dépannage plus difficile et doit préserver la traçabilité de l’adresse originale lorsque c’est nécessaire.

### Schéma animé 1 — Architecture multi-sites

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 410" role="img" aria-label="Architecture WireGuard multi-sites avec hub, deux sites, flux cryptographiques et couche de routage." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="410" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Architecture multi-sites — identité et routage distincts</text>
<rect x="370" y="74" width="260" height="100" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="500" y="102" text-anchor="middle" class="title">Hub WireGuard</text><text x="500" y="128" text-anchor="middle">Peers / clés distinctes</text><text x="500" y="150" text-anchor="middle" class="small">Routage + forwarding + nftables</text>
<rect x="32" y="228" width="245" height="108" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="154" y="258" text-anchor="middle" class="title">Site A</text><text x="154" y="284" text-anchor="middle">LAN 10.10.0.0/24</text><text x="154" y="308" text-anchor="middle" class="small">Peer A · préfixes attribués</text>
<rect x="723" y="228" width="245" height="108" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="845" y="258" text-anchor="middle" class="title">Site B</text><text x="845" y="284" text-anchor="middle">LAN 10.20.0.0/24</text><text x="845" y="308" text-anchor="middle" class="small">Peer B · préfixes attribués</text>
<path d="M277 250 L410 174" class="flow flow-blue"/><path d="M723 250 L590 174" class="flow flow-green"/><circle cx="331" cy="219" r="5" class="packet" fill="#60a5fa"/><circle cx="669" cy="219" r="5" class="packet d2" fill="#4ade80"/>
<rect x="330" y="228" width="340" height="70" rx="10" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="253" text-anchor="middle" class="title">Plans séparés</text><text x="500" y="277" text-anchor="middle" class="small">Data · contrôle de config · observabilité</text>
<text x="500" y="376" text-anchor="middle" class="small">WireGuard transporte les paquets ; Linux décide comment les acheminer.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Un hub n’implémente pas automatiquement le routage inter-sites. Chaque spoke a une clé distincte, des préfixes non ambigus et des règles de forwarding explicites.</p></div>

### 1.4 `AllowedIPs` : sélection du peer et validation des sources

`AllowedIPs` possède deux rôles liés. À l’émission, le préfixe de destination est utilisé pour choisir le peer destinataire. À la réception après authentification et déchiffrement, la source intérieure doit correspondre aux préfixes associés au peer qui a envoyé le paquet. Il s’agit d’un contrôle de cohérence cryptographique du routage, pas d’un remplacement du pare-feu général.

Cette dualité crée des erreurs fréquentes : une route système peut envoyer la destination vers `wg0`, mais aucun peer ne l’autorise ; ou un peer est choisi correctement à l’émission, mais le récepteur rejette le paquet parce que sa source intérieure n’appartient pas aux `AllowedIPs` du peer. L’ordre des préfixes système et le routage le plus spécifique doivent être compris séparément de la logique cryptokey.

**Exemple de principe :** au hub, les `AllowedIPs` d’un peer de site incluent l’adresse tunnel `/32` du peer et les sous-réseaux de LAN derrière lui. Sur le site distant, les `AllowedIPs` incluent les réseaux réellement joignables par ce hub. N’utilise pas `0.0.0.0/0` ou `::/0` par commodité sur toutes les entrées : cela peut attribuer des destinations non intentionnelles à un peer.

### Schéma animé 2 — Cryptokey routing et AllowedIPs

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 410" role="img" aria-label="Schéma du choix du peer avec AllowedIPs à l’émission et validation de la source à la réception." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="410" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Cryptokey routing — une valeur, deux fonctions</text>
<rect x="35" y="77" width="260" height="90" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="165" y="107" text-anchor="middle" class="title">Paquet sortant</text><text x="165" y="133" text-anchor="middle">destination intérieure</text><text x="165" y="151" text-anchor="middle" class="small">ex. 10.20.5.9</text>
<rect x="370" y="77" width="260" height="90" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="500" y="107" text-anchor="middle" class="title">Trie AllowedIPs</text><text x="500" y="133" text-anchor="middle">préfixe le plus spécifique</text><text x="500" y="151" text-anchor="middle" class="small">mapping destination → peer</text>
<rect x="705" y="77" width="260" height="90" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="835" y="107" text-anchor="middle" class="title">Peer sélectionné</text><text x="835" y="133" text-anchor="middle">chiffrement vers sa clé</text><text x="835" y="151" text-anchor="middle" class="small">transport UDP</text>
<path d="M295 122 H370" class="flow flow-blue"/><path d="M630 122 H705" class="flow flow-green"/><circle cx="332" cy="122" r="5" class="packet" fill="#60a5fa"/><circle cx="667" cy="122" r="5" class="packet d2" fill="#4ade80"/>
<path d="M835 167 V221 H500 V251" class="flow flow-muted"/><rect x="320" y="251" width="360" height="82" rx="12" class="red" fill="#30151b" stroke="#fb7185"/><text x="500" y="280" text-anchor="middle" class="title">À la réception après déchiffrement</text><text x="500" y="305" text-anchor="middle">source intérieure vérifiée contre AllowedIPs</text><text x="500" y="322" text-anchor="middle" class="small">clé valide ≠ paquet intérieur automatiquement accepté</text>
<text x="500" y="377" text-anchor="middle" class="small">AllowedIPs sert au choix du peer sortant et à la validation des sources entrantes.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Le routage du noyau et AllowedIPs travaillent ensemble. Une route Linux vers wg0 ne suffit pas si aucun peer ne couvre la destination ; un paquet déchiffré est également contrôlé par rapport aux préfixes autorisés du peer.</p></div>

> **Piège :** l’adresse de tunnel du peer (`10.200.0.2/32` par exemple) et les préfixes de LAN servis par ce peer représentent deux choses distinctes. L’absence d’un préfixe LAN dans la configuration du côté approprié peut donner un handshake parfaitement normal tout en rendant le site inaccessible.

### 1.5 Full tunnel, policy routing et protection contre les fuites

Un full tunnel a pour intention de diriger tout ou presque tout le trafic IP du poste à travers le VPN. Sur Linux, `wg-quick` peut construire des règles de routage adaptées lorsqu’un peer possède une route par défaut dans `AllowedIPs`, mais les détails dépendent des tables, des règles, de l’interface extérieure et de l’environnement du poste. Une configuration plus complexe peut être gérée directement avec `ip rule`, des tables dédiées ou un gestionnaire réseau spécifique.

Le paquet extérieur qui transporte WireGuard doit continuer à sortir vers l’endpoint public par l’interface physique ou par le chemin sous-jacent voulu. Si le paquet UDP extérieur est lui-même routé dans le tunnel, le tunnel peut créer une boucle, perdre son endpoint ou cesser d’établir le handshake. Un kill switch doit bloquer le trafic applicatif qui fuit hors tunnel sans bloquer le transport WireGuard, les services explicitement autorisés (par exemple DHCP local) et les mécanismes nécessaires pour réparer la connectivité.

Un kill switch efficace prend en compte IPv4 et IPv6. Bloquer seulement `0.0.0.0/0` tout en laissant une route IPv6 globale sur l’interface physique laisse une voie de fuite. Le DNS est un autre canal : même si les connexions TCP sont forcées dans le tunnel, un résolveur configuré hors tunnel peut révéler des noms recherchés ou produire des résultats incohérents. Un test de fuite doit couvrir les routes, les connexions réelles, le DNS, IPv6 et le comportement pendant la déconnexion du peer.

### Schéma animé 3 — Full tunnel, routage et kill switch

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 385" role="img" aria-label="Schéma de policy routing pour un full tunnel, l’interface WireGuard, son endpoint extérieur et un kill switch." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="385" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Full tunnel — route de secours et exception endpoint</text>
<rect x="32" y="76" width="230" height="93" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="147" y="107" text-anchor="middle" class="title">Application</text><text x="147" y="133" text-anchor="middle">paquet IP original</text><text x="147" y="151" text-anchor="middle" class="small">marque / UID / dest.</text>
<rect x="350" y="76" width="285" height="93" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="492" y="107" text-anchor="middle" class="title">Règles de routage</text><text x="492" y="133" text-anchor="middle">table principale / dédiée</text><text x="492" y="151" text-anchor="middle" class="small">priorités et exception endpoint</text>
<rect x="725" y="45" width="240" height="78" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="845" y="76" text-anchor="middle" class="title">wg0</text><text x="845" y="101" text-anchor="middle">trafic intérieur chiffré</text>
<rect x="725" y="190" width="240" height="78" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="845" y="221" text-anchor="middle" class="title">Endpoint public</text><text x="845" y="246" text-anchor="middle">UDP via route sous-jacente</text>
<rect x="350" y="222" width="285" height="78" rx="12" class="red" fill="#30151b" stroke="#fb7185"/><text x="492" y="252" text-anchor="middle" class="title">Kill switch</text><text x="492" y="277" text-anchor="middle">refuser la sortie hors tunnel</text>
<path d="M262 122 H350" class="flow flow-blue"/><path d="M635 105 L725 84" class="flow flow-green"/><path d="M635 139 H684 V229 H725" class="flow flow-amber"/><path d="M492 169 V222" class="flow flow-red"/><circle cx="306" cy="122" r="5" class="packet" fill="#60a5fa"/><circle cx="681" cy="95" r="5" class="packet d1" fill="#4ade80"/><circle cx="684" cy="229" r="5" class="packet d2" fill="#fbbf24"/>
<text x="500" y="353" text-anchor="middle" class="small">Le paquet extérieur UDP doit continuer à atteindre l’endpoint ; sinon le tunnel s’auto-coupe.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Un full tunnel doit traiter le trafic intérieur et le paquet UDP extérieur différemment. Une règle kill-switch trop générale peut bloquer les paquets WireGuard eux-mêmes ou la résolution DNS du serveur VPN.</p></div>

### 1.6 Roaming, NAT, endpoints dynamiques et keepalive

Un peer peut changer d’adresse IP ou de port extérieur. Après réception d’un paquet authentifié provenant d’un peer, l’implémentation peut mettre à jour l’endpoint vers lequel le trafic sera renvoyé. Ce comportement permet aux clients mobiles de passer du Wi-Fi à un réseau cellulaire sans reconfigurer à chaque fois l’adresse extérieure. L’endpoint configuré sert notamment à initier le premier échange lorsque le pair distant n’a pas encore été appris.

`PersistentKeepalive` envoie périodiquement un paquet lorsque ce réglage est activé. Il est utile lorsqu’un peer derrière NAT ou un pare-feu avec état doit recevoir du trafic après une période d’inactivité. La valeur souvent citée de 25 secondes est un exemple opérationnel, pas une valeur universelle. Ajuste-la en fonction du délai d’expiration du NAT et des exigences de mobilité ; ne l’active pas systématiquement sur tous les peers.

Un keepalive n’est pas une sonde applicative. Il ne prouve ni la disponibilité du LAN distant, ni l’autorisation d’un port TCP, ni la résolution DNS, ni le fonctionnement du service. La surveillance doit distinguer le dernier handshake, les octets envoyés/reçus, l’état de l’endpoint, les routes et la réponse de bout en bout.

### Schéma animé 4 — Roaming, NAT et endpoint dynamique

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 390" role="img" aria-label="Flux WireGuard d’un peer nomade au travers d’un NAT vers un peer résident, avec keepalive." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="390" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Roaming et NAT — le peer apprend un endpoint authentifié</text>
<rect x="30" y="78" width="240" height="100" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="150" y="109" text-anchor="middle" class="title">Peer nomade</text><text x="150" y="135" text-anchor="middle">Wi-Fi → mobile</text><text x="150" y="156" text-anchor="middle" class="small">endpoint source change</text>
<rect x="380" y="78" width="240" height="100" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="500" y="109" text-anchor="middle" class="title">NAT / pare-feu</text><text x="500" y="135" text-anchor="middle">mapping UDP expirable</text><text x="500" y="156" text-anchor="middle" class="small">paquets sortants autorisés</text>
<rect x="730" y="78" width="240" height="100" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="850" y="109" text-anchor="middle" class="title">Peer résident</text><text x="850" y="135" text-anchor="middle">dernier endpoint appris</text><text x="850" y="156" text-anchor="middle" class="small">source authentifiée</text>
<path d="M270 111 H380" class="flow flow-blue"/><path d="M620 145 H730" class="flow flow-green"/><circle cx="325" cy="111" r="5" class="packet" fill="#60a5fa"/><circle cx="675" cy="145" r="5" class="packet d2" fill="#4ade80"/>
<rect x="155" y="235" width="690" height="80" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="265" text-anchor="middle" class="title">PersistentKeepalive — seulement si nécessaire</text><text x="500" y="290" text-anchor="middle">maintient un mapping ; ne remplace pas les sondes de service</text>
<path d="M150 178 V207 H250 V235" class="flow flow-muted"/><path d="M850 178 V207 H750 V235" class="flow flow-muted"/><text x="500" y="355" text-anchor="middle" class="small">Les paquets authentifiés reçus peuvent mettre à jour dynamiquement l’endpoint du peer.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Le roaming évite de fixer durablement l’adresse IP extérieure du peer. PersistentKeepalive est utile surtout pour un pair derrière NAT qui doit pouvoir recevoir du trafic après une période d’inactivité.</p></div>

### 1.7 Haute disponibilité : séparer protocole, routage et orchestration

WireGuard n’est pas un protocole d’élection de cluster actif/passif et ne synchronise pas automatiquement les états d’un service de haute disponibilité. Une conception avec deux hubs doit décider comment les pairs atteignent chaque hub, quelles routes sont préférées, comment une bascule est décidée, comment prévenir un split-brain et comment vérifier que le nouvel itinéraire livre réellement le service.

Plusieurs modèles existent : endpoint DNS mis à jour, IP virtuelle gérée par un mécanisme HA, deux tunnels distincts avec routage primaire/secondaire, ou un contrôleur qui pousse une nouvelle configuration aux peers. Chacun a des temps de convergence et des risques différents. Un endpoint identique basculant entre deux hôtes n’est sûr que si l’identité cryptographique, la possession des clés, les autorisations et la disponibilité UDP sont conçues explicitement ; ne suppose pas que deux nœuds qui partagent une adresse IP partagent aussi un état de tunnel fonctionnel.

Une bascule doit être validée par une sonde applicative et par l’état des routes. Le fait que le nouveau hub réponde au port UDP ne suffit pas. Les scénarios à tester incluent la panne du processus WireGuard, la panne de la carte réseau, la perte du chemin Internet, la défaillance du service derrière le tunnel, l’indisponibilité du contrôleur et la restauration de l’ancien nœud.

### Schéma animé 5 — Haute disponibilité multi-hub

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 380" role="img" aria-label="Architecture WireGuard avec hub primaire et secondaire supervisés par une sonde HA indépendante." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="380" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Haute disponibilité — le tunnel n’est pas le contrôleur</text>
<rect x="28" y="78" width="220" height="94" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="138" y="109" text-anchor="middle" class="title">Site client</text><text x="138" y="134" text-anchor="middle">wg0 + routes LAN</text><text x="138" y="153" text-anchor="middle" class="small">surveillance hors tunnel</text>
<rect x="390" y="45" width="240" height="83" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="510" y="76" text-anchor="middle" class="title">Hub primaire</text><text x="510" y="102" text-anchor="middle">clé / endpoint A</text>
<rect x="390" y="210" width="240" height="83" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="510" y="241" text-anchor="middle" class="title">Hub secondaire</text><text x="510" y="267" text-anchor="middle">clé / endpoint B</text>
<rect x="735" y="118" width="235" height="105" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="852" y="150" text-anchor="middle" class="title">Contrôleur HA</text><text x="852" y="175" text-anchor="middle">sondes indépendantes</text><text x="852" y="197" text-anchor="middle" class="small">bascule contrôlée</text>
<path d="M248 100 L390 86" class="flow flow-green"/><path d="M248 151 L390 250" class="flow flow-amber"/><circle cx="318" cy="93" r="5" class="packet" fill="#4ade80"/><circle cx="318" cy="201" r="5" class="packet d2" fill="#fbbf24"/><path d="M630 86 L735 142" class="flow flow-muted"/><path d="M630 250 L735 202" class="flow flow-muted"/>
<text x="500" y="340" text-anchor="middle" class="small">WireGuard ne fournit pas à lui seul l’élection active/passive ni la synchronisation de routes.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">La haute disponibilité nécessite un mécanisme externe de santé, une stratégie de bascule, des routes cohérentes et une validation applicative. Les deux hubs ne doivent pas annoncer des routes contradictoires sans contrôle.</p></div>

### 1.8 MTU, PMTUD et fragmentation

Le paquet intérieur est encapsulé dans UDP/IP. L’en-tête extérieur et l’enveloppe WireGuard consomment une partie de la MTU disponible, et la taille supplémentaire varie selon IPv4 ou IPv6 extérieur ainsi que les chemins intermédiaires. Il n’existe pas une valeur de MTU unique adaptée à toutes les topologies. Une MTU conservatrice peut être utile, mais elle doit être mesurée et validée pour le chemin réel.

Un symptôme révélateur est « les pings simples fonctionnent, mais les transferts volumineux ou TLS se bloquent ». Les causes possibles incluent une PMTU mal estimée, des messages ICMP nécessaires au PMTUD bloqués, une mauvaise MSS TCP, une limitation de taille côté tunnel ou un problème applicatif distinct. Réduire la MTU arbitrairement peut masquer le problème tout en réduisant le débit utile ; procède par mesure avec des tailles contrôlées et des captures aux deux extrémités.

### Schéma animé 6 — MTU et PMTUD

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 365" role="img" aria-label="Encapsulation WireGuard et impact de la MTU sur le chemin extérieur et les transferts TCP." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="365" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">MTU / PMTUD — différencier taille intérieure et extérieure</text>
<rect x="30" y="86" width="230" height="102" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="145" y="116" text-anchor="middle" class="title">Paquet intérieur</text><text x="145" y="142" text-anchor="middle">IP + transport + données</text><text x="145" y="164" text-anchor="middle" class="small">MTU du LAN / interface</text>
<rect x="370" y="65" width="265" height="143" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="502" y="96" text-anchor="middle" class="title">Encapsulation WG</text><rect x="397" y="112" width="211" height="24" rx="4" fill="#183650" stroke="#60a5fa"/><text x="502" y="129" text-anchor="middle" class="small">IP extérieur + UDP</text><rect x="397" y="145" width="211" height="37" rx="4" fill="#103627" stroke="#4ade80"/><text x="502" y="168" text-anchor="middle" class="small">WireGuard + paquet chiffré</text>
<rect x="745" y="86" width="225" height="102" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="857" y="116" text-anchor="middle" class="title">Chemin Internet</text><text x="857" y="142" text-anchor="middle">PMTU limitée</text><text x="857" y="164" text-anchor="middle" class="small">fragmentation / drop possible</text>
<path d="M260 137 H370" class="flow flow-blue"/><path d="M635 137 H745" class="flow flow-green"/><circle cx="315" cy="137" r="5" class="packet" fill="#60a5fa"/><circle cx="690" cy="137" r="5" class="packet d2" fill="#4ade80"/>
<rect x="200" y="255" width="600" height="65" rx="12" class="red" fill="#30151b" stroke="#fb7185"/><text x="500" y="282" text-anchor="middle" class="title">Symptôme typique : petit ping OK, gros TCP bloqué</text><text x="500" y="303" text-anchor="middle" class="small">vérifier MTU, PMTUD, ICMP et MSS ; ne pas supposer un défaut crypto</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Le paquet intérieur reçoit une enveloppe UDP/IP et une surcharge cryptographique. La MTU utile dépend de la famille IP extérieure, de l’overlay et de la plus petite MTU du chemin ; un ping de petite taille ne valide pas les gros transferts.</p></div>

### 1.9 Pare-feu, zones et forwarding Linux

Le noyau WireGuard peut recevoir un paquet correctement authentifié et le remettre au chemin IP de l’hôte. Si l’hôte doit relayer le paquet entre deux interfaces, le forwarding IP et les règles de chaîne `FORWARD` sont concernés ; si un service local écoute sur l’hôte, ce sont les règles `INPUT` ; les paquets générés localement touchent `OUTPUT`. Les règles de transfert du LAN vers le LAN distant ne doivent donc pas être confondues avec celles qui autorisent l’UDP extérieur vers l’interface WireGuard.

Définis les zones réseau avant d’écrire les règles. Exemple : zone administration, zone utilisateurs distants, zone services de production et zone de transit. Autorise les flux requis par source, destination, protocole et port ; refuse par défaut les autres flux ; journalise avec parcimonie et évite de produire un volume de logs qui saturerait le système pendant un incident. Les règles stateful facilitent les flux retour, mais elles ne dispensent pas de définir les origines autorisées.

### Schéma animé 7 — Filtrage inter-zones

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 390" role="img" aria-label="Flux LAN-à-LAN au travers de WireGuard, contrôlé par routes et pare-feu nftables." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="390" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Filtrage inter-zones — les clés ne remplacent pas le pare-feu</text>
<rect x="35" y="76" width="220" height="102" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="145" y="107" text-anchor="middle" class="title">LAN source</text><text x="145" y="132" text-anchor="middle">10.10.0.0/24</text><text x="145" y="154" text-anchor="middle" class="small">route vers wg0</text>
<rect x="390" y="76" width="220" height="102" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="500" y="107" text-anchor="middle" class="title">Interface wg0</text><text x="500" y="132" text-anchor="middle">peer / AllowedIPs</text><text x="500" y="154" text-anchor="middle" class="small">cryptokey routing</text>
<rect x="745" y="76" width="220" height="102" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="855" y="107" text-anchor="middle" class="title">LAN distant</text><text x="855" y="132" text-anchor="middle">10.20.0.0/24</text><text x="855" y="154" text-anchor="middle" class="small">route de retour obligatoire</text>
<path d="M255 126 H390" class="flow flow-blue"/><path d="M610 126 H745" class="flow flow-green"/><circle cx="323" cy="126" r="5" class="packet" fill="#60a5fa"/><circle cx="678" cy="126" r="5" class="packet d2" fill="#4ade80"/>
<rect x="250" y="238" width="500" height="84" rx="12" class="red" fill="#30151b" stroke="#fb7185"/><text x="500" y="268" text-anchor="middle" class="title">Contrôles indépendants</text><text x="500" y="293" text-anchor="middle">FORWARD · nftables · rp_filter · routes</text><text x="500" y="311" text-anchor="middle" class="small">la crypto ne remplace pas une politique firewall</text>
<path d="M500 178 V238" class="flow flow-red"/><text x="500" y="363" text-anchor="middle" class="small">Le chemin aller et le chemin retour doivent chacun être autorisés et routés.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Après déchiffrement, le paquet entre dans le chemin réseau de l’hôte. Les règles INPUT, OUTPUT et FORWARD sont différentes ; le forwarding inter-LAN exige une politique explicite et une route retour correcte.</p></div>

### 1.10 Cryptographie, pré-shared key et gestion d’identité

WireGuard a recours à une conception cryptographique moderne et à des suites précises. Une PSK optionnelle peut être combinée au mécanisme public-key pour ajouter un secret symétrique indépendant, mais cela augmente les exigences de distribution et de stockage ; une PSK partagée par tout un parc réduit la granularité de révocation. Si une PSK est utilisée, elle doit être aléatoire, protégée, individualisée selon le modèle de menace et incluse dans la procédure de rotation.

Les clés privées statiques doivent être créées sur l’endpoint qui les détient ou dans un système de gestion approuvé. Les secrets ne doivent pas apparaître dans Git, les images de conteneurs, les sauvegardes accessibles à tous, les tickets, les variables CI affichées ou les logs de configuration. La clé publique peut être partagée pour configurer un peer, mais l’attribution à un propriétaire et à un rôle reste un processus administratif distinct.

Une clé distincte par appareil est généralement préférable à la réutilisation de la même identité par tout un département. Cela permet de retirer un seul appareil perdu ou compromis, de tracer les tentatives et de réduire les conséquences d’une fuite. Conserve des métadonnées non secrètes : propriétaire, rôle, dates de création/expiration de politique, approbateur, sites autorisés, empreinte de clé publique et état de révocation.

### Schéma animé 8 — Rotation des clés statiques

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 385" role="img" aria-label="Étapes de rotation de clés statiques WireGuard avec inventaire, préparation, déploiement, validation puis révocation." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="385" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Rotation d’identité — migration vérifiable, pas coupure aveugle</text>
<rect x="28" y="80" width="220" height="100" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="138" y="111" text-anchor="middle" class="title">Inventaire</text><text x="138" y="137" text-anchor="middle">peer / propriétaire</text><text x="138" y="159" text-anchor="middle" class="small">clé actuelle identifiée</text>
<rect x="280" y="80" width="220" height="100" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="390" y="111" text-anchor="middle" class="title">Préparer</text><text x="390" y="137" text-anchor="middle">nouvelle paire de clés</text><text x="390" y="159" text-anchor="middle" class="small">privée protégée</text>
<rect x="532" y="80" width="220" height="100" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="642" y="111" text-anchor="middle" class="title">Déployer</text><text x="642" y="137" text-anchor="middle">autoriser la clé publique</text><text x="642" y="159" text-anchor="middle" class="small">fenêtre coordonnée</text>
<rect x="784" y="80" width="184" height="100" rx="12" class="red" fill="#30151b" stroke="#fb7185"/><text x="876" y="111" text-anchor="middle" class="title">Révoquer</text><text x="876" y="137" text-anchor="middle">retirer l’ancienne</text><text x="876" y="159" text-anchor="middle" class="small">après validation</text>
<path d="M248 130 H280" class="flow flow-blue"/><path d="M500 130 H532" class="flow flow-green"/><path d="M752 130 H784" class="flow flow-red"/><circle cx="264" cy="130" r="4.5" class="packet" fill="#60a5fa"/><circle cx="516" cy="130" r="4.5" class="packet d1" fill="#4ade80"/><circle cx="768" cy="130" r="4.5" class="packet d2" fill="#fb7185"/>
<rect x="142" y="236" width="716" height="76" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="266" text-anchor="middle" class="title">Contrôles avant fermeture de la fenêtre</text><text x="500" y="290" text-anchor="middle">handshake · routes · application · journaux · retour arrière</text><text x="500" y="355" text-anchor="middle" class="small">Ne jamais placer une clé privée dans Git, les tickets ou les journaux.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">WireGuard renouvelle automatiquement ses clés de session ; la rotation décrite ici concerne les clés statiques d’identité des peers. Conserve une voie de secours et retire l’ancienne autorisation seulement après validation de la nouvelle.</p></div>

### 1.11 Surface d’attaque et limitations connues

WireGuard ne se présente pas comme un système d’obfuscation du trafic ; son transport reste UDP et il ne propose pas un mode natif tunneling-over-TCP. Si un réseau bloque UDP ou utilise une inspection profonde spécifique, ne suppose pas que WireGuard « se fera passer pour HTTPS ». Toute couche supplémentaire de camouflage doit être évaluée comme un composant distinct avec sa propre sécurité, ses performances et ses implications juridiques ou opérationnelles.

La page officielle des limitations connues décrit notamment des considérations de déni de service, de confiance envers l’horloge système et de détection de boucles de routage. Il faut maintenir l’heure système fiable, limiter l’exposition du port UDP aux seules conditions nécessaires, surveiller la charge CPU lors de handshakes anormaux et tester les routes afin d’éviter les boucles. Ne présente pas ces observations comme une preuve qu’un déploiement est vulnérable sans analyser le noyau, la configuration et le contexte réels.

### 1.12 Comparer la santé cryptographique et la santé du service

Une approche d’exploitation experte utilise plusieurs niveaux d’observation. Au niveau WireGuard : clé publique du peer, endpoint connu, dernier handshake et compteurs de transferts. Au niveau réseau : route choisie (`ip route get`), règles de routage (`ip rule`), adresses et MTU des interfaces, compteurs nftables, pertes et captures. Au niveau application : requête TCP/UDP réelle, résolution DNS, code retour et latence. Les horodatages doivent être cohérents pour corréler les changements de route, la rotation de clé et l’incident utilisateur.

### Schéma animé 9 — Observabilité et corrélation

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 395" role="img" aria-label="Pipeline d’observabilité WireGuard avec métriques de peer, routage, compteurs firewall et sonde applicative." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="395" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Observabilité — corréler le protocole et le service</text>
<rect x="30" y="82" width="205" height="100" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="132" y="113" text-anchor="middle" class="title">wg show</text><text x="132" y="139" text-anchor="middle">handshake / octets</text><text x="132" y="161" text-anchor="middle" class="small">compteurs par peer</text>
<rect x="278" y="82" width="205" height="100" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="380" y="113" text-anchor="middle" class="title">Netlink / routes</text><text x="380" y="139" text-anchor="middle">ip route / addr</text><text x="380" y="161" text-anchor="middle" class="small">santé L3 réelle</text>
<rect x="526" y="82" width="205" height="100" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="628" y="113" text-anchor="middle" class="title">Compteurs firewall</text><text x="628" y="139" text-anchor="middle">drop / accept</text><text x="628" y="161" text-anchor="middle" class="small">nftables / conntrack</text>
<rect x="774" y="82" width="195" height="100" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="871" y="113" text-anchor="middle" class="title">Sonde applicative</text><text x="871" y="139" text-anchor="middle">TCP / DNS / HTTP</text><text x="871" y="161" text-anchor="middle" class="small">succès de bout en bout</text>
<path d="M235 132 H278" class="flow flow-blue"/><path d="M483 132 H526" class="flow flow-green"/><path d="M731 132 H774" class="flow flow-amber"/><circle cx="256" cy="132" r="4.5" class="packet" fill="#60a5fa"/><circle cx="504" cy="132" r="4.5" class="packet d1" fill="#4ade80"/><circle cx="752" cy="132" r="4.5" class="packet d2" fill="#fbbf24"/>
<rect x="238" y="244" width="524" height="77" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="500" y="274" text-anchor="middle" class="title">Corrélation temporelle</text><text x="500" y="298" text-anchor="middle">peer + destination + interface + horodatage + résultat</text><text x="500" y="365" text-anchor="middle" class="small">Un handshake récent ne garantit pas la disponibilité d’une application.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Une supervision fiable combine compteurs WireGuard, routes, règles de filtrage, pertes et sonde applicative. N’envoie jamais les clés privées ou les configurations contenant des secrets dans un SIEM.</p></div>

---

## 2. Configuration et pratique

### 2.1 Architecture du laboratoire expert

Le laboratoire ci-dessous est une topologie de démonstration. Le hub est connecté à deux sites et à un poste d’administration. Les plages d’adresses sont réservées à la documentation ; remplace-les par des adresses qui n’entrent pas en conflit avec les réseaux existants.

| Élément | Interface / adresse illustrative | Rôle |
|---|---|---|
| Hub `wg0` | `10.200.0.1/24` | Concentrateur de tunnels |
| Site A `wg0` | `10.200.0.2/32` | LAN `10.10.0.0/24` |
| Site B `wg0` | `10.200.0.3/32` | LAN `10.20.0.0/24` |
| Admin `wg0` | `10.200.0.10/32` | Accès limité à la zone de gestion |
| Endpoint UDP de démonstration | `198.51.100.10:51820` | Adresse réservée aux exemples |

Avant tout changement, prends une sauvegarde de configuration, confirme un accès console ou hors bande, vérifie les routes existantes et planifie une fenêtre de retour arrière. Les exemples ci-dessous n’activent pas automatiquement des règles firewall universelles : elles dépendent du gestionnaire réseau et de la politique existante.

### 2.2 Préparer et protéger les clés

Sur chaque endpoint, génère une paire de clés selon la procédure de la distribution. Le fichier privé doit être accessible uniquement au compte privilégié qui administre WireGuard.

```bash
sudo install -d -m 700 /etc/wireguard
umask 077
wg genkey | tee /etc/wireguard/site-a.key | wg pubkey > /etc/wireguard/site-a.pub
sudo chmod 600 /etc/wireguard/site-a.key
sudo chmod 644 /etc/wireguard/site-a.pub
```

La commande ci-dessus illustre les permissions ; le nom du fichier doit être propre à la machine concernée. Ne copie jamais `site-a.key` dans un autre site. Lis et partage la clé publique avec le pair selon un canal approuvé. Les fichiers `.conf` peuvent contenir la clé privée et doivent être traités comme des secrets même si les adresses et clés publiques qu’ils contiennent ne sont pas secrètes.

> **Danger :** ne colle jamais une vraie clé privée dans un ticket, un message ou une conversation. Si elle a été exposée, considère-la compromise, prépare une nouvelle clé et retire l’ancienne autorisation sur les peers distants.

### 2.3 Exemple de configuration du hub

Le fragment suivant est un modèle de compréhension ; il n’est pas exécutable tel quel parce que les clés publiques et l’endpoint sont des espaces réservés.

```ini
# /etc/wireguard/wg0.conf — HUB (exemple à adapter)
[Interface]
Address = 10.200.0.1/24
ListenPort = 51820
PrivateKey = <CLE_PRIVEE_DU_HUB>

# Peer Site A
[Peer]
PublicKey = <CLE_PUBLIQUE_SITE_A>
AllowedIPs = 10.200.0.2/32, 10.10.0.0/24

# Peer Site B
[Peer]
PublicKey = <CLE_PUBLIQUE_SITE_B>
AllowedIPs = 10.200.0.3/32, 10.20.0.0/24

# Peer administration — exemple à restreindre
[Peer]
PublicKey = <CLE_PUBLIQUE_ADMIN>
AllowedIPs = 10.200.0.10/32
```

Le hub peut recevoir des paquets de ces peers, mais la transmission entre les sites dépend aussi du forwarding IP et des règles `FORWARD`. Les préfixes doivent être attribués à un seul peer de façon non ambiguë dans la table pertinente. N’inclus pas les LAN d’un site sous le peer d’un autre site sauf si un modèle de transit spécifique le justifie.

### 2.4 Exemple de configuration d’un spoke

```ini
# /etc/wireguard/wg0.conf — SITE A (exemple)
[Interface]
Address = 10.200.0.2/32
PrivateKey = <CLE_PRIVEE_SITE_A>

[Peer]
PublicKey = <CLE_PUBLIQUE_HUB>
Endpoint = 198.51.100.10:51820
AllowedIPs = 10.200.0.0/24, 10.20.0.0/24, 10.10.0.0/24
PersistentKeepalive = 25
```

Ce fragment montre une sélection de routes typique pour un spoke, mais il doit être ajusté à la topologie. `10.10.0.0/24` peut déjà être local au site et n’a généralement pas besoin d’être envoyé dans le tunnel depuis ce même site. Utilise un plan d’adressage documenté et vérifie les routes réellement ajoutées par `wg-quick`. La présence de `PersistentKeepalive` est un choix lié au comportement NAT et à la nécessité de recevoir du trafic ; ce n’est pas une obligation universelle.

### 2.5 Séparer configuration WireGuard et routage du système

`wg` configure les paramètres propres à WireGuard, comme les clés, peers, endpoints, ports, `AllowedIPs` et keepalive. `ip` configure les adresses, liens, routes, règles et autres éléments réseau. `wg-quick` réunit plusieurs opérations pratiques : création d’interface, adresse, MTU, routes déduites de `AllowedIPs` et exécution des hooks éventuels. Pour une conception avancée, assure-toi de savoir quelle couche possède chaque route et comment les changements sont réconciliés au redémarrage.

```bash
sudo wg show wg0
sudo wg showconf wg0
ip -details link show wg0
ip addr show dev wg0
ip route show table all
ip rule show
ip route get 10.20.0.10
```

`wg showconf` et les sorties de configuration peuvent contenir des secrets : traite-les avec prudence. `ip route get` indique la route que le noyau choisit pour une destination et constitue une preuve utile pour distinguer un problème de routage du problème de handshake. Si `wg-quick` est remplacé par NetworkManager ou systemd-networkd, évite que deux gestionnaires tentent de posséder la même interface ou les mêmes routes.

### 2.6 Forwarding et nftables : politique explicite

Pour relier des LAN, le noyau doit forwarder IPv4 et, si la topologie en dépend, IPv6. Avant d’activer le forwarding, vérifie la politique de sécurité de l’hôte. Exemple d’inspection :

```bash
sysctl net.ipv4.ip_forward
sysctl net.ipv6.conf.all.forwarding
sudo nft list ruleset
ip route show
```

La mise en place d’une règle nftables doit se faire en cohérence avec le ruleset existant. Évite de remplacer l’ensemble des règles d’un serveur par un exemple pédagogique minimal. Le pattern de politique est : autoriser explicitement les flux `wg0` vers le LAN distant requis, permettre les flux retour correspondants si le filtrage est stateful, et refuser les autres transferts. Les chaînes `input`, `output` et `forward` ont des responsabilités différentes.

```nft
# EXEMPLE DE STRUCTURE, à fusionner avec le ruleset existant.
# Ne pas coller tel quel sur un hôte administré sans revue.
chain forward {
    type filter hook forward priority filter; policy drop;
    ct state established,related accept
    iifname "wg0" oifname "lan0" ip daddr 10.20.0.0/24 accept
    iifname "lan0" oifname "wg0" ip saddr 10.10.0.0/24 ip daddr 10.20.0.0/24 accept
}
```

L’exemple nécessite d’être ajusté à la topologie, aux connexions locales, à IPv6 et à la politique réelle. Un filtre `forward` fondé sur une seule direction peut ne pas traiter convenablement le trafic si les interfaces ou le chemin de retour diffèrent. Valide les règles avec des compteurs et capture aux deux côtés avant de déclarer le service opérationnel.

### 2.7 Full tunnel avec policy routing : checklist avant déploiement

Un full tunnel peut utiliser les mécanismes de `wg-quick`, des tables de routage dédiées ou un gestionnaire réseau. Avant le déploiement, définis explicitement :

1. routes intérieures qui passent par `wg0` ;
2. route extérieure qui atteint l’adresse du serveur WireGuard ;
3. DNS à utiliser et comportement si le résolveur VPN est indisponible ;
4. politique IPv4 **et** IPv6 ;
5. trafic local nécessaire au démarrage (DHCP, contrôle d’accès, gestion) ;
6. comportement du kill switch si l’interface disparaît ;
7. plan de récupération hors tunnel.

```bash
# Inspection avant/après une modification
ip route show table all
ip rule show
ip route get 198.51.100.10
ip route get 1.1.1.1
ip -6 route show table all
```

Les résultats doivent montrer que l’endpoint extérieur reste joignable par la route sous-jacente voulue, tandis que le trafic applicatif choisi par la politique passe dans l’interface VPN. L’adresse `198.51.100.10` est un exemple réservé à la documentation ; remplace-la par l’endpoint de ton environnement pour le test réel.

### 2.8 Contrôler les métriques et le comportement attendu

```bash
watch -n 2 'wg show wg0'
ip -s link show wg0
nstat -az
ss -s
sudo nft list ruleset
```

La commande `wg show` montre notamment l’endpoint courant, le dernier handshake et les octets transférés par peer. Ce sont des indices, non une mesure complète de disponibilité. Les compteurs d’interface révèlent des drops ou erreurs à un niveau différent ; les compteurs firewall aident à repérer des règles qui bloquent un flux ; `ss` et les tests applicatifs permettent de confirmer l’état au niveau transport/application.

### 2.9 Test de MTU contrôlé

Ne commence pas par désactiver le pare-feu ou réduire radicalement la MTU. Mesure d’abord la taille supportée et vérifie si les messages ICMP nécessaires au PMTUD reviennent correctement. Sous Linux, un ping DF peut être utile pour IPv4, mais son option exacte varie avec l’outil et l’OS. Compare un petit paquet, plusieurs tailles plus grandes, puis un transfert TCP reproductible ; observe les captures aux deux extrémités.

```bash
# Exemples d'observation : adapte l'interface et les tailles.
ping -M do -s 1200 10.20.0.10
tracepath 10.20.0.10
ip link show wg0
```

Une seule mesure ne détermine pas la PMTU de tous les chemins. Fais plusieurs essais, distingue la taille ICMP du paquet IP total et vérifie le comportement dans les deux sens. Le chemin peut être asymétrique, et le MSS TCP ne résout pas les problèmes de taille de datagrammes UDP.

### 2.10 Rotation contrôlée des clés statiques

La rotation se prépare comme un changement de configuration, pas comme une action improvisée sur la machine distante. Identifie le pair, l’accès de secours, les consommateurs dépendants, l’heure de changement, les propriétaires et la procédure de retour arrière. Génère la nouvelle clé privée sur l’endpoint qui la détient, distribue sa clé publique, installe les configurations coordonnément, vérifie le handshake puis teste les routes et les services. Après validation, retire l’ancienne clé publique de l’autorisation distante et mets à jour l’inventaire.


### 2.11 Supervision et tableau de bord

Pour une installation de production, collecte au minimum l’âge du dernier handshake par peer attendu, les octets reçus/envoyés, l’existence de l’interface, les routes critiques, les changements d’endpoint, les pertes d’interface, la santé du service distant et les changements de configuration. L’âge du handshake ne doit pas être alerté de la même manière pour un peer qui n’envoie rien pendant des jours et un site qui doit échanger continuellement. La sonde doit dépendre du rôle du peer et du niveau de service attendu.


---

## 3. Dépannage, sécurité et exploitation

### 3.1 Méthode experte : rechercher le premier plan qui échoue

Commence avec une hypothèse qui prédit une observation. Exemple : « le handshake est à jour mais le LAN distant ne répond pas ; je soupçonne le routage ou le forwarding, pas nécessairement la cryptographie ». Observe les routes choisies, le peer pour la destination, les compteurs d’interface et les règles firewall. Capture de part et d’autre du point où le paquet devrait circuler. Ne change qu’une variable par essai.

### Schéma animé 10 — Arbre de dépannage expert

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 455" role="img" aria-label="Arbre de dépannage WireGuard depuis la joignabilité de l’endpoint à la santé du service." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="455" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Dépannage expert — localiser le premier plan en échec</text>
<rect x="350" y="58" width="300" height="58" rx="11" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="500" y="82" text-anchor="middle" class="title">1. Endpoint UDP joignable ?</text><text x="500" y="102" text-anchor="middle" class="small">pare-feu / port / route extérieure</text>
<path d="M500 116 V148" class="flow flow-green"/><polygon points="494,144 500,154 506,144" fill="#4ade80"/><text x="519" y="139" class="small" fill="#86efac">Oui</text>
<rect x="350" y="154" width="300" height="58" rx="11" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="178" text-anchor="middle" class="title">2. Handshake récent ?</text><text x="500" y="198" text-anchor="middle" class="small">clés / endpoint / heure système</text>
<path d="M500 212 V244" class="flow flow-green"/><polygon points="494,240 500,250 506,240" fill="#4ade80"/>
<rect x="350" y="250" width="300" height="58" rx="11" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="500" y="274" text-anchor="middle" class="title">3. AllowedIPs et routes OK ?</text><text x="500" y="294" text-anchor="middle" class="small">route aller + route retour</text>
<path d="M500 308 V340" class="flow flow-green"/><polygon points="494,336 500,346 506,336" fill="#4ade80"/>
<rect x="350" y="346" width="300" height="50" rx="11" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="500" y="367" text-anchor="middle" class="title">4. Firewall / MTU / service</text><text x="500" y="385" text-anchor="middle" class="small">tester par couche et garder une preuve</text>
<rect x="28" y="149" width="250" height="75" rx="11" class="red" fill="#30151b" stroke="#fb7185"/><text x="153" y="178" text-anchor="middle" class="title">Non : couche externe</text><text x="153" y="201" text-anchor="middle" class="small">UDP / NAT / endpoint</text><path d="M350 183 H278" class="flow flow-red"/><polygon points="284,177 274,183 284,189" fill="#fb7185"/>
<rect x="718" y="149" width="250" height="75" rx="11" class="red" fill="#30151b" stroke="#fb7185"/><text x="843" y="178" text-anchor="middle" class="title">Non : identité / handshake</text><text x="843" y="201" text-anchor="middle" class="small">clé publique / config du peer</text><path d="M650 183 H718" class="flow flow-red"/>
<text x="500" y="431" text-anchor="middle" class="small">Commencer par la première preuve qui échoue ; ne pas modifier simultanément routes, clés et pare-feu.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Cet arbre n’affirme pas que toutes les pannes sont linéaires : il impose simplement l’ordre de vérification. Une panne de transport extérieure se traite différemment d’un handshake valide suivi d’un échec de routage ou d’application.</p></div>

### 3.2 Matrice des symptômes

| Symptôme | Hypothèses prioritaires | Preuves discriminantes |
|---|---|---|
| Aucun handshake | endpoint, UDP, clé publique, horloge, règle firewall | endpoint `wg show`, capture UDP, état réseau de base |
| Handshake présent, zéro transfert | route destination, `AllowedIPs`, mauvaise source de test | `ip route get`, `wg show allowed-ips`, compteurs |
| Octets envoyés mais rien reçu | endpoint de retour, route asymétrique, pare-feu distant, peer mal configuré | capture aux deux extrémités, compteur RX, endpoint appris |
| LAN A atteint, LAN B non | forwarding, règle `FORWARD`, route retour, overlap | routes des routeurs LAN, sysctl forwarding, nftables counters |
| Petit ping OK, transfert volumineux bloqué | MTU, PMTUD, MSS, ICMP filtré | tests de taille, `tracepath`, captures ICMP/TCP |
| Tunnel tombe lors d’un changement Wi-Fi | roaming, mapping NAT, endpoint et keepalive | nouvelle adresse/port extérieur, handshake après déplacement |
| Fuites lorsque VPN arrêté | kill switch incomplet, IPv6 ou DNS hors tunnel | routes IPv4/IPv6, test DNS, capture sur interface physique |
| Bascule HA sans récupération | route non convergée, état du hub, clé/endpoint, service indisponible | sonde extérieure, route post-bascule, test app |

### 3.3 Captures et préservation des preuves

Les captures réseau peuvent révéler des adresses internes, des noms DNS, des métadonnées utilisateurs et des données applicatives si elles sont prises après déchiffrement. Sur l’interface extérieure, WireGuard masque le paquet intérieur, mais les adresses extérieures, le rythme, les tailles et les informations de transport restent observables. Sur `wg0`, le trafic a déjà été déchiffré ; traite la capture avec la même rigueur qu’une capture LAN sensible.

```bash
sudo tcpdump -ni eth0 udp port 51820
sudo tcpdump -ni wg0 host 10.20.0.10
sudo journalctl -u wg-quick@wg0 --since '15 minutes ago'
```

Utilise des filtres restreints, un répertoire protégé, une durée courte et une durée de conservation explicite. Note l’horodatage, les interfaces, le filtre exact et l’outil/version. Masque ou exclue les clés et fichiers privés. Une capture prise sur un seul côté n’établit pas à elle seule la direction de la perte : synchronise les heures et capture sur les interfaces pertinentes.

### 3.4 Durcissement du plan de contrôle

- Limite l’accès administrateur aux machines qui gèrent le service WireGuard ; sépare cette zone du trafic utilisateur.
- Stocke les clés privées avec permissions strictes et, si l’architecture l’exige, une solution de gestion des secrets adaptée.
- Attribue une clé distincte à chaque appareil ou site et inventorie son propriétaire, ses préfixes et sa date de rotation.
- Restreins les préfixes `AllowedIPs`; n’utilise pas de route par défaut sur un peer si la topologie n’en a pas besoin.
- N’expose pas des règles de firewall temporaires ou des scripts de démarrage non revus à travers des hooks `PreUp`/`PostUp`.
- Surveille les handshakes et changements d’endpoint sans journaliser les clés privées.
- Mets le noyau, `wireguard-tools`, `iproute2` et le pare-feu à jour selon la politique de maintenance.
- Ne suppose pas qu’un port qui n’envoie aucune réponse à une sonde UDP est la preuve que le service est « invisible » ou impossible à atteindre.

> **Danger :** `wg-quick` permet d’utiliser certains hooks de commande dans la configuration. Comme les fichiers WireGuard peuvent être exécutés avec des privilèges élevés, un fichier de configuration non fiable peut conduire à exécuter des commandes privilégiées. N’importe quel utilisateur ne doit pas pouvoir modifier ces fichiers.

### 3.5 Protection contre la fuite de données et erreurs d’inventaire

Une entrée de peer orpheline n’est pas toujours immédiatement dangereuse, mais elle augmente la surface de gestion et rend les autorisations difficiles à auditer. À chaque départ de collaborateur, retrait d’équipement ou incident de clé, vérifie la présence du peer dans toutes les passerelles, contrôleurs, sauvegardes restaurables et documents. La révocation doit être propagée et confirmée, pas seulement marquée dans un tableau.

Si une clé privée a été compromise, retirer la clé publique de l’autre côté coupe l’accès de cette identité, mais la réponse d’incident doit aussi vérifier les données accessibles, les routes et le périmètre d’exposition. WireGuard ne peut pas annuler les données déjà exfiltrées ni remplacer les contrôles d’autorisation au niveau applicatif.

### 3.6 Résilience et test de retour arrière

Un changement de route, de clé, de MTU ou de pare-feu peut couper la seule connexion d’administration. Pour éviter ce verrouillage : accès hors bande ou console ; sauvegarde protégée ; plan de retour arrière testé ; un seul changement à la fois ; validation via une sonde depuis un point indépendant. Ne valide pas un changement uniquement depuis la session qui l’a rendu possible : le chemin d’administration peut être précisément ce qui va se perdre.


### 3.7 Ingénierie de performance

La performance ne se réduit pas au débit maximal annoncé. Les paquets petits et nombreux peuvent saturer un cœur CPU ou des files réseau avant le débit en bits/s. Les paquets plus gros peuvent révéler un plafond de MTU ou une limite de la liaison. La charge de chiffrement dépend aussi de la plateforme CPU, de la version du noyau, des tailles et directions de paquets, des files NIC, du traitement softirq, du nombre de pairs et du profil de trafic.

Mesure la ligne de base sans tunnel, puis le même trafic via WireGuard, puis le trafic à travers les routes et règles de production. Sépare goodput applicatif, débit de tunnel, pps, CPU par cœur, pertes, retransmissions et latence p50/p95/p99. Répète les mesures sur un profil réaliste et documente les options de NIC, d’affinité et de qdisc. N’applique pas d’optimisation noyau non documentée juste pour faire monter un chiffre synthétique.

### Schéma animé 11 — Ingénierie de performance

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 390" role="img" aria-label="Pipeline d’analyse des performances WireGuard de la charge offerte jusqu’au résultat applicatif." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="390" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Ingénierie de performance — trouver le vrai goulot</text>
<rect x="32" y="82" width="220" height="96" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="142" y="112" text-anchor="middle" class="title">Charge offerte</text><text x="142" y="137" text-anchor="middle">pps + débit + flux</text><text x="142" y="158" text-anchor="middle" class="small">direction / taille de paquet</text>
<rect x="280" y="82" width="220" height="96" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="390" y="112" text-anchor="middle" class="title">CPU / Crypto</text><text x="390" y="137" text-anchor="middle">softirq / queues</text><text x="390" y="158" text-anchor="middle" class="small">affinité / contention</text>
<rect x="528" y="82" width="220" height="96" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="638" y="112" text-anchor="middle" class="title">Chemin réseau</text><text x="638" y="137" text-anchor="middle">MTU / qdisc / NIC</text><text x="638" y="158" text-anchor="middle" class="small">drops / retransmissions</text>
<rect x="776" y="82" width="192" height="96" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="872" y="112" text-anchor="middle" class="title">Application</text><text x="872" y="137" text-anchor="middle">latence / goodput</text><text x="872" y="158" text-anchor="middle" class="small">résultat utilisateur</text>
<path d="M252 130 H280" class="flow flow-blue"/><path d="M500 130 H528" class="flow flow-green"/><path d="M748 130 H776" class="flow flow-amber"/><circle cx="266" cy="130" r="4.5" class="packet" fill="#60a5fa"/><circle cx="514" cy="130" r="4.5" class="packet d1" fill="#4ade80"/><circle cx="762" cy="130" r="4.5" class="packet d2" fill="#fbbf24"/>
<rect x="180" y="244" width="640" height="72" rx="12" class="node" fill="#111827" stroke="#64748b"/><text x="500" y="273" text-anchor="middle" class="title">Mesurer une variable à la fois</text><text x="500" y="297" text-anchor="middle">baseline · p50/p95 · pertes · CPU par cœur · tailles MTU</text><text x="500" y="360" text-anchor="middle" class="small">Éviter d’inférer un plafond à partir d’un seul test TCP.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">La performance WireGuard dépend du débit, des paquets par seconde, des tailles de paquets, des chemins NIC/CPU et de l’application. Mesure séparément charge offerte, débit utile et pertes ; compare des profils reproductibles.</p></div>

### 3.8 Automatisation : état désiré, idempotence et validation

Une automatisation de peers doit définir un état désiré : clés publiques, préfixes, endpoint, port, keepalive, zones autorisées et propriétaire. Elle doit générer et comparer les différences, appliquer un changement minimal, vérifier le résultat effectif avec `wg show`, routes et règles firewall, puis enregistrer l’état final sans stocker de secrets en clair dans les logs. Une exécution répétée ne doit pas dupliquer des routes ou des règles. Prévoyez des tests pour une clé retirée, un préfixe chevauchant, un endpoint absent, un service en échec et un changement interrompu.

La validation ne doit pas se limiter à la syntaxe du fichier : la configuration peut être syntaxiquement valide tout en choisissant le mauvais peer ou en créant une fuite de routage. L’étape de test doit montrer les routes prévues, vérifier l’accès autorisé, confirmer le refus d’un flux non autorisé et valider l’absence de sortie hors tunnel dans le scénario full-tunnel.

### 3.9 Réponse à incident

Lors d’une panne, préserver les preuves avant de modifier l’état si cela ne retarde pas le rétablissement d’un service critique. Collecter un état des peers, routes, règles, compteurs et journaux ; noter les changements récents ; isoler si nécessaire le peer soupçonné ; éviter de supprimer toutes les clés ou toutes les routes simultanément. Toute mesure de confinement doit inclure l’effet sur la continuité, l’accès d’administration et le chemin de retour arrière.

### Schéma animé 12 — Réponse à incident

<div class="wg-visual" style="background:#090d14;color:#e4e7eb;border:1px solid #303846;border-radius:16px;padding:12px;max-width:100%;overflow:hidden;color-scheme:dark" bgcolor="#090d14"><style>.wg-visual{width:100%;max-width:100%;margin:1.2rem 0 1.5rem;color:#e4e7eb;background:#090d14;border:1px solid #303846;border-radius:16px;padding:12px;box-sizing:border-box;overflow:hidden;color-scheme:dark}.wg-visual *{box-sizing:border-box}.wg-visual svg{display:block;width:100%;height:auto;max-width:100%;background:#090d14;border-radius:10px}.wg-visual svg text{font-family:Inter,Segoe UI,Arial,sans-serif;fill:#e4e7eb;font-size:15px}.wg-visual svg .small{font-size:12px;fill:#a1aab8}.wg-visual svg .title{font-size:17px;font-weight:700;fill:#f8fafc}.wg-visual svg .node{fill:#111827;stroke:#64748b;stroke-width:1.5}.wg-visual svg .blue{fill:#10243b;stroke:#60a5fa;stroke-width:1.6}.wg-visual svg .green{fill:#0d2a20;stroke:#4ade80;stroke-width:1.6}.wg-visual svg .amber{fill:#2b2110;stroke:#fbbf24;stroke-width:1.6}.wg-visual svg .red{fill:#30151b;stroke:#fb7185;stroke-width:1.6}.wg-visual svg .flow{fill:none;stroke-width:3;stroke-dasharray:7 9;stroke-linecap:round;animation:wgExpertFlow 1.15s linear infinite}.wg-visual svg .flow-blue{stroke:#60a5fa}.wg-visual svg .flow-green{stroke:#4ade80}.wg-visual svg .flow-amber{stroke:#fbbf24}.wg-visual svg .flow-red{stroke:#fb7185}.wg-visual svg .flow-muted{stroke:#94a3b8;stroke-dasharray:4 8}.wg-visual svg .packet{animation:wgExpertPulse 1.65s ease-in-out infinite;transform-box:fill-box;transform-origin:center}.wg-visual svg .d1{animation-delay:.35s}.wg-visual svg .d2{animation-delay:.7s}.wg-visual svg .d3{animation-delay:1.05s}.wg-visual__caption{margin:.65rem .35rem .25rem;color:#cbd5e1;font-size:.92rem;line-height:1.7}.wg-visual__note{color:#94a3b8;font-size:.82rem;line-height:1.65;margin:.5rem .35rem .2rem}.wg-visual__legend{display:flex;flex-wrap:wrap;gap:.45rem 1rem;color:#cbd5e1;font-size:.82rem;padding:.45rem .3rem}.wg-visual__dot{display:inline-block;width:.65rem;height:.65rem;border-radius:50%;margin-right:.35rem}@keyframes wgExpertFlow{to{stroke-dashoffset:-32}}@keyframes wgExpertPulse{0%,100%{opacity:.3}50%{opacity:1}}@media(prefers-reduced-motion:reduce){.wg-visual svg .flow,.wg-visual svg .packet{animation:none!important}.wg-visual{scroll-behavior:auto!important}}</style><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 410" role="img" aria-label="Cycle de réponse aux incidents WireGuard avec détection, collecte, confinement et validation." style="width:100%;max-width:100%;height:auto;display:block;background:#090d14;border-radius:10px"><rect x="1" y="1" width="1000" height="410" rx="13" fill="#090d14" stroke="#303846"/><text x="26" y="32" class="title">Réponse à incident — contenir sans détruire les preuves</text>
<rect x="32" y="90" width="215" height="92" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="139" y="120" text-anchor="middle" class="title">Détecter</text><text x="139" y="145" text-anchor="middle">sonde / alerte</text><text x="139" y="163" text-anchor="middle" class="small">horodatage précis</text>
<rect x="272" y="90" width="215" height="92" rx="12" class="amber" fill="#2b2110" stroke="#fbbf24"/><text x="379" y="120" text-anchor="middle" class="title">Conserver preuve</text><text x="379" y="145" text-anchor="middle">état / routes / logs</text><text x="379" y="163" text-anchor="middle" class="small">sans exporter secrets</text>
<rect x="512" y="90" width="215" height="92" rx="12" class="green" fill="#0d2a20" stroke="#4ade80"/><text x="619" y="120" text-anchor="middle" class="title">Contenir</text><text x="619" y="145" text-anchor="middle">peer / route / règle</text><text x="619" y="163" text-anchor="middle" class="small">changement minimal</text>
<rect x="752" y="90" width="215" height="92" rx="12" class="blue" fill="#10243b" stroke="#60a5fa"/><text x="859" y="120" text-anchor="middle" class="title">Valider</text><text x="859" y="145" text-anchor="middle">flux applicatif</text><text x="859" y="163" text-anchor="middle" class="small">retour / rollback</text>
<path d="M247 136 H272" class="flow flow-blue"/><path d="M487 136 H512" class="flow flow-amber"/><path d="M727 136 H752" class="flow flow-green"/><circle cx="259" cy="136" r="4.5" class="packet" fill="#60a5fa"/><circle cx="499" cy="136" r="4.5" class="packet d1" fill="#fbbf24"/><circle cx="739" cy="136" r="4.5" class="packet d2" fill="#4ade80"/>
<path d="M859 182 V238 H139 V182" class="flow flow-muted"/><text x="500" y="225" text-anchor="middle" class="small">Post-mortem : cause racine, détection, mesure et prévention</text><rect x="240" y="278" width="520" height="58" rx="11" class="red" fill="#30151b" stroke="#fb7185"/><text x="500" y="302" text-anchor="middle" class="title">Ne pas publier les clés privées</text><text x="500" y="323" text-anchor="middle" class="small">limiter les secrets, préserver horodatages et intégrité</text><text x="500" y="377" text-anchor="middle" class="small">La restauration d’un accès nécessite toujours une validation de bout en bout.</text></svg><p class="wg-visual__caption" style="color:#cbd5e1">Les actions d’urgence doivent être limitées, attribuées et réversibles. Collecte les clés publiques et les compteurs nécessaires au diagnostic, mais ne partage pas les clés privées, les fichiers de configuration secrets ni les dumps mémoire sans contrôle.</p></div>

### 3.10 Cas pratique 1 — handshake frais, application inaccessible

**Contexte :** le hub affiche un handshake récent pour Site A. `wg show` indique quelques octets envoyés, mais le client ne peut pas joindre `10.20.0.10:443` derrière Site B.

**Hypothèses à tester :** la destination est mal routée sur le client ; le peer Site A n’inclut pas le réseau B dans ses `AllowedIPs` ; le hub n’a pas de route système vers B ; le forwarding ou `FORWARD` bloque ; Site B n’a pas de route de retour vers A ; le service n’écoute pas sur l’adresse attendue.

**Procédure :**

1. Sur le client, exécute `ip route get 10.20.0.10` et contrôle si la destination doit être envoyée à `wg0`.
2. Sur le peer, relève `wg show wg0 allowed-ips` et vérifie quel peer couvre la destination.
3. Sur le hub, contrôle `sysctl net.ipv4.ip_forward`, les routes LAN et le compteur de la règle de forwarding.
4. Capture le même test sur `wg0` au hub et sur l’interface LAN de sortie. Si le paquet apparaît sur `wg0` mais pas sur LAN, la cause se situe probablement dans le routage ou le pare-feu du hub.
5. Vérifie le chemin de retour et le service TCP avec `ss -lntp` ou un test équivalent sur l’hôte cible.

**Conclusion attendue :** une connexion cryptographique valide ne prouve pas l’existence d’une route bout-en-bout. Identifie le premier point où le paquet manque puis change uniquement cette couche.

### 3.11 Cas pratique 2 — certains sites fonctionnent, un sous-réseau se chevauche

**Contexte :** un nouveau site est ajouté. Le hub a deux peers dont les `AllowedIPs` incluent tous deux `10.30.0.0/24`. La connectivité devient intermittente ou va vers le mauvais site selon la configuration effective.

**Diagnostic :** compare les préfixes attribués à chaque peer et les routes du système. Détermine si le chevauchement est intentionnel (par exemple, une translation documentée) ou une erreur d’adressage. Ne tente pas de résoudre le problème par une règle firewall qui choisit au hasard un site. Renumérote si possible ; sinon utilise une traduction d’adresse contrôlée ou des domaines de routage séparés. Vérifie ensuite les routes de retour et la traçabilité des adresses.

### 3.12 Cas pratique 3 — le VPN se reconnecte mais les transferts lourds échouent

**Contexte :** handshake récent, petites requêtes réussies, transfert volumineux interrompu.

**Hypothèses :** MTU/PMTUD, messages ICMP filtrés, MSS TCP, chemin retour asymétrique, traitement applicatif ou loss réseau. Teste des tailles incrémentales, capture les ICMP et les retransmissions TCP, et compare le trafic sur `wg0` et l’interface extérieure. Vérifie IPv4 et IPv6. Ne fixe pas immédiatement `MTU = 1280` sans mesure ni explication : cela peut masquer un blocage d’ICMP et réduire l’efficacité du chemin.

### 3.13 Cas pratique 4 — full tunnel et perte d’accès à l’endpoint

**Contexte :** après activation du full tunnel, le client perd le handshake et le trafic Internet.

**Hypothèse clé :** le paquet UDP extérieur destiné à l’endpoint est lui-même forcé dans `wg0`, créant une boucle ou une perte de route sous-jacente. Vérifie `ip route get <endpoint_public>` et l’ordre des règles `ip rule`. Inspecte les routes ajoutées par `wg-quick`, puis remets en place une exception dédiée ou ajuste le modèle de policy routing. Teste ensuite le kill switch avec l’interface active et inactive, en vérifiant également IPv6 et DNS.

### 3.14 Cas pratique 5 — site de secours actif mais service indisponible

**Contexte :** la route primaire est retirée, le secondaire répond et le handshake est récent, pourtant l’application n’est pas accessible.

**Pistes :** le secondaire n’a pas la même politique de préfixes ; les règles firewall ne sont pas synchronisées ; le LAN distant a une route de retour vers l’ancien hub ; un service dépend d’une IP source autorisée ; le contrôle HA vérifie seulement le port UDP. Valide le chemin aller/retour, la politique d’accès et une sonde de l’application. La décision de bascule doit être basée sur des critères de santé définis, pas un seul indicateur WireGuard.

---

## 4. Procédures opérationnelles

### 4.1 Checklist de mise en production

- [ ] Inventaire des peers, propriétaires, empreintes publiques et préfixes associés à chaque clé.
- [ ] Plan d’adressage sans recouvrement ou traduction explicitement documentée.
- [ ] Routes aller et retour vérifiées pour chaque service autorisé.
- [ ] Routage extérieur de l’endpoint distinct du routage intérieur du tunnel.
- [ ] Pare-feu revu sur `INPUT`, `OUTPUT` et `FORWARD` selon les rôles.
- [ ] Tests IPv4 et IPv6 effectués, y compris scénario d’interface déconnectée.
- [ ] MTU / PMTUD testés avec des tailles variées et un transfert réel.
- [ ] Keepalive activé uniquement pour les scénarios NAT qui le justifient.
- [ ] Rotation, révocation et récupération hors bande testées.
- [ ] Supervision du handshake, des compteurs, des routes et de l’application active.
- [ ] Fichiers de configuration et clés privées stockés avec permissions adéquates.
- [ ] Restauration de sauvegarde et rollback testés dans un environnement contrôlé.

### 4.2 Checklist de changement

**Avant :** sauvegarder la configuration, noter l’état des routes et des peers, confirmer l’accès console, définir l’impact, les critères de réussite et les critères de retour arrière. **Pendant :** modifier une couche à la fois ; conserver un canal de diagnostic indépendant ; capturer les compteurs de réussite/échec. **Après :** vérifier handshake, transfert, routes, application, DNS, IPv6, absence de fuite et journaux ; consigner les différences par rapport à l’état désiré.

### 4.3 Checklist de retrait d’un peer

Identifier tous les hubs et configurations où la clé publique est autorisée ; désactiver l’accès selon la procédure de changement ; retirer les préfixes attribués ; vérifier que les routes correspondantes ont disparu ; mettre à jour l’inventaire ; vérifier les journaux pour les tentatives résiduelles ; conserver la preuve de révocation selon les règles de conservation. Si la clé privée est suspectée compromise, déterminer si une nouvelle identité et des changements de secret applicatif sont également nécessaires.

### 4.4 Glossaire ciblé

| Terme | Définition utile en exploitation |
|---|---|
| Peer | Identité WireGuard connue par sa clé publique distante. |
| Endpoint | Adresse/port UDP extérieur utilisé pour envoyer le trafic chiffré. |
| AllowedIPs | Préfixes utilisés pour la sélection du peer et la validation des sources intérieures. |
| Handshake | Échange cryptographique établissant les clés symétriques de session. |
| PersistentKeepalive | Paquet périodique destiné notamment à maintenir un état NAT. |
| Full tunnel | Politique qui envoie le trafic choisi par la route par défaut à travers le VPN. |
| Split tunnel | Seuls certains préfixes sont dirigés dans le tunnel. |
| MTU / PMTU | Taille maximale d’un paquet sur une interface / sur l’ensemble du chemin. |
| Kill switch | Politique qui empêche la sortie hors tunnel du trafic qu’on veut protéger. |
| Plan de contrôle | Gestion de l’état, des clés, des routes et des changements ; à distinguer des paquets applicatifs transportés. |

---

## Points à retenir

1. WireGuard est un transport IP chiffré léger, pas un système complet de gestion d’identité ou de routage dynamique.
2. `AllowedIPs` sert à choisir le peer de destination et à contrôler les sources des paquets intérieurs reçus.
3. La disponibilité doit être évaluée à plusieurs niveaux : handshake, transferts, routes, firewall, DNS et application.
4. Les architectures multi-sites exigent des clés distinctes, des préfixes non ambigus, du forwarding explicite et des routes retour.
5. Un full tunnel doit protéger le trafic applicatif tout en gardant l’endpoint UDP joignable par le chemin sous-jacent ; le kill switch doit couvrir IPv4, IPv6 et DNS.
6. PersistentKeepalive aide dans certains scénarios NAT, mais ne constitue pas une sonde de santé universelle.
7. Les pannes MTU/PMTUD peuvent laisser les petits paquets passer tout en cassant les transferts importants ; mesure le chemin avant de modifier les paramètres.
8. La haute disponibilité et l’orchestration doivent être construites au-dessus de WireGuard avec une sonde indépendante et un plan de retour arrière.
9. Les clés privées sont des secrets opérationnels ; l’inventaire, la rotation, la révocation et les sauvegardes doivent être testés.
10. Les schémas de ce cours sont des modèles conceptuels, non une configuration générée automatiquement. Vérifie toujours les règles et routes dans l’environnement réel.

## Exercices corrigés

### Exercice 1 — mauvais peer sélectionné

**Énoncé :** `ip route get 10.20.0.8` affiche `dev wg0`, mais le paquet ne sort dans aucun compteur du peer attendu.

**Correction :** la route Linux vers `wg0` ne garantit pas qu’un peer WireGuard couvre le préfixe. Examine `wg show wg0 allowed-ips`. Ajoute ou corrige le préfixe sur le peer approprié et assure-toi qu’il ne chevauche pas un autre peer d’une façon non voulue. Vérifie à nouveau les compteurs et un test applicatif.

### Exercice 2 — handshake frais et zéro trafic reçu

**Énoncé :** la passerelle envoie des octets, mais les compteurs reçus ne progressent plus.

**Correction :** vérifier endpoint extérieur, NAT, route de retour, configuration distante, pare-feu et éventuelle asymétrie. Capture d’abord sur l’interface physique, puis sur `wg0` distant. Un compteur TX croissant ne prouve pas que le paquet est accepté côté distant.

### Exercice 3 — trafic LAN-à-LAN à sens unique

**Énoncé :** le site A atteint le service B, mais B ne peut pas répondre à A.

**Correction :** comparer les routes de retour côté B et LAN B, vérifier `AllowedIPs` dans les deux directions, le forwarding et les règles firewall pour les deux chemins. Si une traduction NAT existe, vérifier les règles et les adresses vues par le service.

### Exercice 4 — full tunnel avec fuite IPv6

**Énoncé :** IPv4 sort par le VPN, mais un test IPv6 montre une route extérieure directe.

**Correction :** définir le comportement attendu d’IPv6. Soit transporter les préfixes IPv6 requis par le tunnel et définir les routes/filtrage IPv6, soit bloquer la sortie IPv6 extérieure conformément à la politique. Tester également les requêtes DNS et le scénario où `wg0` est arrêté.

### Exercice 5 — keepalive activé partout

**Énoncé :** la configuration active `PersistentKeepalive = 25` sur tous les peers.

**Correction :** revenir au besoin réel. Conserver le keepalive pour les pairs derrière des NAT ou des pare-feu stateful qui doivent recevoir des données après inactivité ; le supprimer ailleurs pour limiter les paquets périodiques inutiles. La décision doit être documentée dans le profil d’accès du peer.

### Exercice 6 — bascule sans service

**Énoncé :** le contrôleur déclare le hub secondaire disponible car le port UDP répond, mais l’utilisateur ne peut pas joindre l’application.

**Correction :** élargir les critères de santé : vérifier handshake, routes, prefix mappings, firewall, service et route retour. Utiliser une sonde applicative indépendante et documenter le temps de convergence. Un contrôle du transport n’est pas une preuve de service disponible.

---

## Références et lectures complémentaires

Les pages suivantes sont les références de départ pour la mise en œuvre et l’investigation. Les détails peuvent varier selon le système d’exploitation et la version installée ; consulter aussi les pages de manuels livrées avec la distribution.

- WireGuard — site et vue conceptuelle : https://www.wireguard.com/
- WireGuard — protocole et cryptographie : https://www.wireguard.com/protocol/
- WireGuard — limitations connues : https://www.wireguard.com/known-limitations/
- WireGuard — livre blanc : https://www.wireguard.com/papers/wireguard.pdf
- Manuel `wg(8)` : https://man7.org/linux/man-pages/man8/wg.8.html
- Manuel `wg-quick(8)` : https://man7.org/linux/man-pages/man8/wg-quick.8.html
- Documentation Ubuntu Server — introduction WireGuard : https://ubuntu.com/server/docs/wireguard-vpn-introduction/
- Documentation Ubuntu Server — tâches courantes : https://ubuntu.com/server/docs/how-to/wireguard-vpn/common-tasks/
- Noise Protocol Framework : https://noiseprotocol.org/noise.html
- RFC 7748 — Elliptic Curves for Security (X25519) : https://www.rfc-editor.org/rfc/rfc7748
- RFC 8439 — ChaCha20 and Poly1305 for IETF Protocols : https://www.rfc-editor.org/rfc/rfc8439
- RFC 5869 — HMAC-based Extract-and-Expand Key Derivation Function : https://www.rfc-editor.org/rfc/rfc5869
- RFC 7693 — The BLAKE2 Cryptographic Hash and MAC : https://www.rfc-editor.org/rfc/rfc7693
- Linux `ip-route(8)` : https://man7.org/linux/man-pages/man8/ip-route.8.html
- Linux `nft(8)` : https://man7.org/linux/man-pages/man8/nft.8.html

> **Astuce :** conserve avec le cours un profil de laboratoire versionné sans clés réelles, une capture de commandes avant/après et une matrice des flux autorisés. Une preuve reproductible vaut mieux qu’un « tunnel vert » sans explication.
